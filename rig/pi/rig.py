#!/usr/bin/env python3
"""Run the syringe actuator on a timer, log everything, and pick the culture out of the log.

The motor runs for burst_s every period_s, with no knowledge of where the crank is. The Nano's
rows are logged at its full rate during a burst. Air and culture pass the beam in turn, so each
burst holds stretches at the culture's level, and those are its reading. Nothing depends on where
the crank stops.

Files in data_dir:
  raw-YYYYMMDD.csv  every row in a burst, 1 Hz between them
  summary.csv       one row per burst: the culture picked from it, and a verdict
  events.csv        anything that went wrong, and starts and stops

pick_samples.py applies the same picking to any saved raw file. Only the motor library is outside
the standard library, and only `--stub-motor` avoids it. See README.md.
"""
import argparse
import csv
import datetime
import fcntl
import glob
import os
import pathlib
import select
import signal
import statistics
import sys
import termios
import time
import tomllib
import tty

HEADER_PREFIX = "timestamp_ms,"
FULL_ON = 0.0  # adafruit_motor: both PWMs full on, which brakes
TIMESYNC_FLAG = "/run/systemd/timesync/synchronized"
MAX_MANUAL_RUN_S = 60.0


class LinkLost(Exception):
    """The Nano stopped answering, or never sent its header."""


# ---- analysis: pure functions over counts ----


def plateaus(values, min_rows, max_step):
    """The steady stretches: at least min_rows in a row, each within max_step of the last.

    Meniscus crossings and droplets swing far from any level, and are not one themselves.
    """
    found = []
    start = 0
    for index in range(1, len(values) + 1):
        if index == len(values) or abs(values[index] - values[index - 1]) >= max_step:
            if index - start >= min_rows:
                found.append(values[start:index])
            start = index
    return found


def pick_sample(values, levels):
    """What one burst shows: (sample level, its rows, its spread, air level, verdict).

    Sample is the plateaus above the air band that sit within sample_band of their common level. So it
    needs culture that reads above air, which stops being true near air's own level: then a burst reads
    no_sample, not a wrong number. Wet air drifts, so the band is wide.
    """
    if not values:
        return None, 0, None, None, "no_sample"
    found = plateaus(values, levels["plateau_rows"], levels["plateau_step"])
    air_top = levels["air_reference"] + levels["near_air"]
    air_bottom = levels["air_reference"] - levels["near_air"]
    above = [run for run in found if statistics.median(run) > air_top]
    if above:
        # The culture is the level most of those rows share; a stray stretch far from it is not culture.
        centre = statistics.median([x for run in above for x in run])
        above = [run for run in above if abs(statistics.median(run) - centre) <= levels["sample_band"]]
    sample_rows = [x for run in above for x in run]
    air_rows = [x for run in found if air_bottom <= statistics.median(run) <= air_top for x in run]
    air = statistics.median(air_rows) if air_rows else None
    sample = statistics.median(sample_rows) if sample_rows else None
    spread = statistics.pstdev(sample_rows) if sample_rows else None
    if max(values) - min(values) < levels["min_swing"]:
        return sample, len(sample_rows), spread, air, "no_motion"  # a stalled crank, read in one place
    if not sample_rows:
        return None, 0, None, air, "no_sample"
    verdict = "ok" if len(sample_rows) >= levels["min_sample_rows"] else "thin"
    return sample, len(sample_rows), spread, air, verdict


# ---- motor ----


class HatMotor:
    """One channel of an Adafruit DC & Stepper Motor HAT."""

    def __init__(self, number, address):
        from adafruit_motorkit import MotorKit

        self._motor = getattr(MotorKit(address=address), f"motor{number}")

    def run(self, throttle):
        self._motor.throttle = throttle

    def stop(self):
        self._motor.throttle = FULL_ON

    def off(self):
        self._motor.throttle = None


class StubMotor:
    """Writes the throttle to a file, for the simulated Nano to read."""

    def __init__(self, path):
        self._path = pathlib.Path(path)
        self.stop()

    def _write(self, text):
        temporary = self._path.with_suffix(".tmp")
        temporary.write_text(text)
        os.replace(temporary, self._path)

    def run(self, throttle):
        self._write(str(throttle))

    def stop(self):
        self._write("0")

    def off(self):
        self._write("off")


def open_motor(config, stub_path):
    if stub_path:
        return StubMotor(stub_path)
    motor = config["motor"]
    return HatMotor(motor["number"], motor["address"])


# ---- serial ----


def _is_row(line, columns):
    fields = line.split(",")
    if len(fields) != len(columns):
        return False
    try:
        [float(field) for field in fields]
    except ValueError:
        return False
    return True


class NanoLink:
    """The Nano's CSV over USB. Connecting waits for the header its setup() prints."""

    def __init__(self, port, header_timeout_s):
        self._port = port
        self._header_timeout_s = header_timeout_s
        self._pending = b""
        self._fd = None
        self.columns = None

    def _resolve_port(self):
        if self._port != "auto":
            return self._port
        found = sorted(glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*"))
        if not found:
            raise LinkLost("no /dev/ttyUSB* or /dev/ttyACM*")
        return found[0]

    def connect(self):
        port = self._resolve_port()
        try:
            self._fd = os.open(port, os.O_RDWR | os.O_NOCTTY)
            tty.setraw(self._fd)
            attributes = termios.tcgetattr(self._fd)
            attributes[4] = attributes[5] = termios.B115200
            termios.tcsetattr(self._fd, termios.TCSANOW, attributes)
        except OSError as error:
            self.close()
            raise LinkLost(f"cannot open {port}: {error}") from error
        self._reset_board()
        termios.tcflush(self._fd, termios.TCIFLUSH)
        self._pending = b""
        deadline = time.monotonic() + self._header_timeout_s
        while time.monotonic() < deadline:
            for line in self.read_lines(0.2):
                if line.startswith(HEADER_PREFIX):
                    self.columns = line.split(",")
                    return
                # A board that did not reset never repeats its header. Rows the same shape
                # as the ones before the reconnect are the same board.
                if self.columns and _is_row(line, self.columns):
                    return
        self.close()
        raise LinkLost(f"no CSV header from {port} within {self._header_timeout_s:g} s")

    def _reset_board(self):
        """Opening a port resets most Nanos, not all; the header is only sent after a reset."""
        try:
            fcntl.ioctl(self._fd, termios.TIOCMBIC, termios.TIOCM_DTR.to_bytes(4, sys.byteorder))
            time.sleep(0.05)
            fcntl.ioctl(self._fd, termios.TIOCMBIS, termios.TIOCM_DTR.to_bytes(4, sys.byteorder))
        except OSError:
            pass  # a pseudo-terminal has no DTR

    def read_lines(self, timeout_s):
        try:
            ready, _, _ = select.select([self._fd], [], [], timeout_s)
            if not ready:
                return []
            chunk = os.read(self._fd, 4096)
        except OSError as error:
            raise LinkLost(f"serial read failed: {error}") from error
        if not chunk:
            raise LinkLost("serial port closed")
        self._pending += chunk
        *lines, self._pending = self._pending.split(b"\n")
        return [line.rstrip(b"\r").decode("ascii", errors="replace") for line in lines]

    def close(self):
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None


# ---- logs ----


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


def stamp():
    return utc_now().isoformat(timespec="milliseconds")


def clock_synced():
    return int(os.path.exists(TIMESYNC_FLAG))


class Appender:
    """A CSV opened for appending, its header written once, with a torn last line ended."""

    def __init__(self, path, header):
        needs_header = not path.exists() or path.stat().st_size == 0
        torn = not needs_header and path.read_bytes()[-1:] != b"\n"
        self._file = open(path, "a", encoding="ascii", errors="replace", newline="")
        self.writer = csv.writer(self._file, lineterminator="\n")
        if torn:
            self._file.write("\n")
        if needs_header:
            self.writer.writerow(header)
        self.sync()

    def row(self, values, sync=True):
        self.writer.writerow(values)
        if sync:
            self.sync()

    def sync(self):
        self._file.flush()
        os.fsync(self._file.fileno())

    def close(self):
        self._file.close()


class RawLog:
    """One file per UTC day. A change of the Nano's columns starts a new file."""

    def __init__(self, data_dir):
        self._data_dir = data_dir
        self._key = None
        self._log = None
        self._last_sync = 0.0

    def write(self, values, columns, now):
        key = (utc_now().strftime("%Y%m%d"), tuple(columns))
        if key != self._key:
            self.close()
            self._log = self._open(key[0], columns)
            self._key = key
        self._log.row(values, sync=False)
        if now - self._last_sync >= 1.0:
            self._log.sync()
            self._last_sync = now

    def _open(self, day, columns):
        header = ["time_utc", "burst", "phase", "throttle", "clock_synced", *columns]
        path = self._data_dir / f"raw-{day}.csv"
        if path.exists() and path.stat().st_size:
            with open(path, encoding="ascii", errors="replace") as existing:
                if existing.readline().rstrip("\n").split(",") != header:
                    path = self._data_dir / f"raw-{day}-{utc_now().strftime('%H%M%S')}.csv"
        return Appender(path, header)

    def close(self):
        if self._log is not None:
            self._log.sync()
            self._log.close()
            self._log = None
            self._key = None


SUMMARY_HEADER = [
    "time_utc", "burst", "clock_synced", "channel", "burst_rows", "sample_level", "sample_rows", "sample_std",
    "air_level", "verdict",
]


# ---- the cycle ----


class Rig:
    def __init__(self, config, motor, link):
        self.config = config
        self.schedule = config["schedule"]
        self.levels = config["levels"]
        self.motor = motor
        self.link = link
        self.linked = False
        data_dir = pathlib.Path(config["data_dir"]).expanduser()
        data_dir.mkdir(parents=True, exist_ok=True)
        self.raw = RawLog(data_dir)
        self.summary = Appender(data_dir / "summary.csv", SUMMARY_HEADER)
        self.events = Appender(data_dir / "events.csv", ["time_utc", "event", "detail"])
        self.column = f"adc_counts_{config['channel']}"
        self.column_index = None
        self.phase = "idle"
        self.phase_end = 0.0
        self.throttle = 0.0
        self.kick_end = None
        self.burst_id = 0
        self.burst_values = []
        self.next_burst = time.monotonic() + self.schedule["start_delay_s"]
        self.last_row = 0.0
        self.last_idle_log = 0.0

    def event(self, name, detail=""):
        self.events.row([stamp(), name, detail])
        print(f"{name}: {detail}", file=sys.stderr, flush=True)

    # Motor state and the phase change together, so a row is never logged against the wrong one.
    def _set_throttle(self, throttle):
        self.motor.run(throttle)
        self.throttle = throttle

    def _start_motor(self, now):
        """Start from rest. A crank that runs at the set throttle may not break free at it."""
        motor = self.config["motor"]
        if "kick_throttle" in motor:
            self._set_throttle(motor["kick_throttle"])
            self.kick_end = now + motor["kick_s"]
        else:
            self._set_throttle(motor["throttle"])

    def _stop_motor(self):
        self.kick_end = None
        self.motor.stop()
        self.throttle = 0.0

    def connect(self):
        self.link.connect()
        if self.column not in self.link.columns:
            raise SystemExit(f"{self.column} is not in the Nano's columns: {','.join(self.link.columns)}")
        self.column_index = self.link.columns.index(self.column)
        self.linked = True
        self.last_row = time.monotonic()
        self.event("linked", ",".join(self.link.columns))

    def lose_link(self, reason):
        self.linked = False
        self.link.close()
        self.abort("link_lost", reason)

    def abort(self, name, detail):
        """Stop the motor and give up on any burst in progress: the sensor can no longer be trusted."""
        self._stop_motor()
        self.event(name, detail)
        if self.phase != "idle":
            self._write_summary(aborted=True)
            self.phase = "idle"

    def start_burst(self, now):
        self.burst_id = int(time.time())
        self.burst_values = []
        while self.next_burst <= now:
            self.next_burst += self.schedule["period_s"]
        self._start_motor(now)
        self.phase = "burst"
        self.phase_end = now + self.schedule["burst_s"]

    def on_row(self, line, now):
        if line.startswith(HEADER_PREFIX):
            # The board reset under us. Its millis restarted, and any burst is suspect.
            self.link.columns = line.split(",")
            self.abort("board_reset", "header mid-stream")
            return
        fields = line.split(",")
        if len(fields) != len(self.link.columns):
            return  # a line cut off by a reset or a reconnect
        try:
            value = float(fields[self.column_index])
        except ValueError:
            return
        self.last_row = now
        if self.phase == "burst":
            self.burst_values.append(value)
        else:
            if now - self.last_idle_log < self.config["serial"]["idle_log_s"]:
                return
            self.last_idle_log = now
        self.raw.write(
            [stamp(), self.burst_id, self.phase, self.throttle, clock_synced(), *fields], self.link.columns, now
        )

    def tick(self, now):
        if now - self.last_row > self.config["serial"]["stale_s"]:
            raise LinkLost(f"no rows for {self.config['serial']['stale_s']:g} s")
        if self.kick_end is not None and now >= self.kick_end:
            self.kick_end = None
            self._set_throttle(self.config["motor"]["throttle"])
        if self.phase == "idle":
            if now >= self.next_burst:
                self.start_burst(now)
        elif now >= self.phase_end:
            self._stop_motor()
            self._write_summary()
            self.phase = "idle"

    def _write_summary(self, aborted=False):
        sample, rows, spread, air, verdict = pick_sample(self.burst_values, self.levels)
        self.summary.row(
            [
                stamp(), self.burst_id, clock_synced(), self.config["channel"], len(self.burst_values),
                sample, rows, spread, air, "aborted" if aborted else verdict,
            ]
        )

    def run(self):
        self._stop_motor()
        self.event("start", f"throttle {self.config['motor']['throttle']}, period {self.schedule['period_s']:g} s")
        serial = self.config["serial"]
        try:
            while True:
                if not self.linked:
                    try:
                        self.connect()
                    except LinkLost as error:
                        self.event("link_retry", str(error))
                        time.sleep(serial["retry_s"])
                        continue
                try:
                    for line in self.link.read_lines(0.02):
                        self.on_row(line, time.monotonic())
                    self.tick(time.monotonic())
                except LinkLost as error:
                    self.lose_link(str(error))
        finally:
            self.motor.off()
            self.raw.close()
            self.event("stop", f"phase {self.phase}")
            self.link.close()


# ---- command line ----


def load_config(path):
    with open(path, "rb") as source:
        config = tomllib.load(source)
    throttle = config["motor"]["throttle"]
    if not 0.0 < abs(throttle) <= 1.0:
        raise SystemExit(f"motor.throttle must be within -1..1 and not 0, got {throttle}")
    if "kick_throttle" in config["motor"]:
        kick_throttle, kick_s = config["motor"]["kick_throttle"], config["motor"]["kick_s"]
        if not abs(throttle) <= abs(kick_throttle) <= 1.0:
            raise SystemExit(f"motor.kick_throttle must be between the throttle and 1, got {kick_throttle}")
        if not 0.0 < kick_s < config["schedule"]["burst_s"]:
            raise SystemExit(f"motor.kick_s must be above 0 and under schedule.burst_s, got {kick_s}")
    for name in ("period_s", "burst_s"):
        if config["schedule"][name] <= 0:
            raise SystemExit(f"schedule.{name} must be above 0")
    if config["schedule"]["burst_s"] >= config["schedule"]["period_s"]:
        raise SystemExit("schedule.period_s must exceed burst_s")
    return config


def interrupt(_signal, _frame):
    raise SystemExit(0)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default=str(pathlib.Path(__file__).with_name("rig.toml")))
    parser.add_argument("--stub-motor", metavar="FILE", help="write the throttle to FILE; no HAT needed")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("run", help="burst, read and log until stopped")
    commands.add_parser("stop", help="turn the motor channel off")
    manual = commands.add_parser("motor", help="run the motor for a set time, for the bench test")
    manual.add_argument("--throttle", type=float, required=True)
    manual.add_argument("--seconds", type=float, required=True)
    args = parser.parse_args(argv)

    signal.signal(signal.SIGTERM, interrupt)
    signal.signal(signal.SIGINT, interrupt)
    config = load_config(args.config)
    motor = open_motor(config, args.stub_motor)

    if args.command == "stop":
        motor.off()
        return 0
    if args.command == "motor":
        if not (0.0 < abs(args.throttle) <= 1.0 and 0.0 < args.seconds <= MAX_MANUAL_RUN_S):
            raise SystemExit(f"--throttle must be within -1..1 and not 0, --seconds up to {MAX_MANUAL_RUN_S:g}")
        try:
            motor.run(args.throttle)
            time.sleep(args.seconds)
        finally:
            motor.off()
        return 0

    link = NanoLink(config.get("port", "auto"), config["serial"]["header_timeout_s"])
    Rig(config, motor, link).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
