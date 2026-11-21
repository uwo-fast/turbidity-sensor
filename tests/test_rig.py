#!/usr/bin/env python3
"""Tests for rig/pi/rig.py: the level analysis, and whole runs against a simulated Nano."""
import csv
import pathlib
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
RIG_DIR = ROOT / "rig" / "pi"
CAPTURES = ROOT / "data" / "bench" / "2026-11-05"
sys.path.insert(0, str(RIG_DIR))

import rig  # noqa: E402

CONFIG = """
channel = "a1"
port = "{port}"
data_dir = "{data}"
[motor]
number = 1
address = 0x60
throttle = {throttle}
{kick}
[schedule]
period_s = {period}
start_delay_s = 0.5
burst_s = 3.5
[levels]
air_reference = 474.5
near_air = 60.0
plateau_rows = 5
plateau_step = 3.0
min_sample_rows = 25
min_swing = 100.0
sample_band = 15.0
[serial]
header_timeout_s = {header_timeout}
stale_s = 1.0
retry_s = 0.2
idle_log_s = 0.2
"""


LEVELS = {"air_reference": 440.0, "near_air": 60.0, "plateau_rows": 5, "plateau_step": 3.0, "min_sample_rows": 25, "min_swing": 100.0, "sample_band": 15.0}


class PlateausTest(unittest.TestCase):
    def test_keeps_plateaus_and_drops_swings(self):
        values = [850.0] * 6 + [300.0, 100.0, 600.0] + [440.0] * 5 + [90.0, 95.0, 90.0]
        self.assertEqual(rig.plateaus(values, 5, 3.0), [[850.0] * 6, [440.0] * 5])

    def test_a_signal_that_never_settles_has_no_plateaus(self):
        self.assertEqual(rig.plateaus([100.0, 200.0, 300.0, 400.0] * 5, 5, 3.0), [])


class PickSampleTest(unittest.TestCase):
    def pick(self, values):
        return rig.pick_sample(values, LEVELS)

    def test_picks_the_culture_and_ignores_air_and_dips(self):
        values = ([830.0] * 30 + [100.0]) * 3 + ([440.0] * 20 + [20.0]) * 2 + [50.0] * 8
        sample, rows, _, air, verdict = self.pick(values)
        self.assertEqual((sample, rows, air, verdict), (830.0, 90, 440.0, "ok"))

    def test_too_little_culture_is_thin(self):
        values = [830.0] * 10 + [100.0] + [440.0] * 200
        self.assertEqual(self.pick(values)[4], "thin")

    def test_only_air_has_no_sample_and_no_number(self):
        values = ([440.0] * 20 + [100.0]) * 5
        sample, rows, _, _, verdict = self.pick(values)
        self.assertEqual((sample, rows, verdict), (None, 0, "no_sample"))

    def test_a_flat_burst_did_not_move(self):
        self.assertEqual(self.pick([830.0] * 900)[4], "no_motion")

    def test_wet_air_above_the_old_band_is_not_the_sample(self):
        # 2026-11-07 04:27 UTC burst: air at 501-505 outweighed 13 rows of culture at 835-837, and read 504.8.
        levels = {**LEVELS, "air_reference": 466.0}
        values = ([466.0] * 30 + [10.0]) * 4 + ([501.4] * 12 + [10.0]) + ([504.8] * 35 + [10.0]) + ([834.6] * 7 + [10.0]) + [837.1] * 6
        sample, rows, _, _, verdict = rig.pick_sample(values, levels)
        self.assertEqual((rows, verdict), (13, "thin"))
        self.assertAlmostEqual(sample, 835.5, delta=1.5)

    def test_a_stray_stretch_far_from_the_culture_is_dropped(self):
        # 2026-11-07 07:27 UTC burst: one stretch at 728 among culture at 840-841.
        values = ([840.3] * 7 + [10.0]) + ([841.0] * 10 + [10.0]) + ([841.3] * 6 + [10.0]) + ([728.3] * 8 + [10.0]) + [440.0] * 40
        sample, rows, _, _, verdict = rig.pick_sample(values, LEVELS)
        self.assertEqual((rows, verdict), (23, "thin"))
        self.assertAlmostEqual(sample, 841.0, delta=0.5)

    def test_an_air_stop_cannot_read_as_good(self):
        # 2026-11-07 00:52: the old stop-and-read logic called 444.8 good.
        values = ([444.8] * 60 + [30.0]) * 10 + ([830.0] * 6 + [30.0])
        sample, rows, _, _, verdict = self.pick(values)
        self.assertEqual((sample, rows, verdict), (830.0, 6, "thin"))


class RealCaptureTest(unittest.TestCase):
    """The picking against the first motor runs: DI water, A2, 2026-11-05."""

    def run_rows(self, name):
        with open(CAPTURES / f"{name}.csv", encoding="ascii") as source:
            return [float(row["adc_counts_a2"]) for row in csv.DictReader(source) if row["state"] == "run"]

    def test_finds_the_water_level_wherever_the_crank_stopped(self):
        for name in ("63_di_m4_t060", "64_di_m4_t070", "65_di_m4_t080", "71_di_m4_t065_30s", "73_di_m4_t070_30s"):
            with self.subTest(name):
                sample, rows, _, air, verdict = rig.pick_sample(self.run_rows(name), LEVELS)
                self.assertEqual(verdict, "ok")
                self.assertAlmostEqual(sample, 851.0, delta=2.0)
                self.assertTrue(425.0 <= air <= 465.0, air)

    def test_every_burst_length_window_at_the_chosen_speed_agrees(self):
        run = self.run_rows("73_di_m4_t070_30s")
        window = int(18.5 * 50)
        for start in range(0, len(run) - window, 25):
            with self.subTest(start=start):
                sample, _, _, _, verdict = rig.pick_sample(run[start : start + window], LEVELS)
                self.assertEqual(verdict, "ok")
                self.assertAlmostEqual(sample, 851.0, delta=2.0)

    def test_a_stalled_crank_does_not_move(self):
        self.assertEqual(rig.pick_sample(self.run_rows("69_di_m4_t050_watched"), LEVELS)[4], "no_motion")


class ConfigTest(unittest.TestCase):
    def load(self, **replace):
        text = CONFIG.format(port="x", data="y", period=10.0, header_timeout=1.0, throttle=1.0, kick="")
        for old, new in replace.items():
            text = text.replace(f"{old} = ", f"{old} = {new} #")
        with tempfile.NamedTemporaryFile("w", suffix=".toml") as file:
            file.write(text)
            file.flush()
            return rig.load_config(file.name)

    def test_accepts_a_good_config(self):
        self.assertEqual(self.load()["channel"], "a1")

    def test_refuses_a_stopped_or_excess_throttle(self):
        for throttle in (0.0, 1.5):
            with self.assertRaises(SystemExit):
                self.load(throttle=throttle)

    def test_refuses_a_kick_that_is_weaker_or_longer_than_a_burst(self):
        for kick in ("kick_throttle = 0.5\nkick_s = 0.5", "kick_throttle = 1.5\nkick_s = 0.5", "kick_throttle = 1.0\nkick_s = 3.6", "kick_throttle = 1.0\nkick_s = 0"):
            text = CONFIG.format(port="x", data="y", period=10.0, header_timeout=1.0, throttle=0.7, kick=kick)
            with self.subTest(kick), tempfile.NamedTemporaryFile("w", suffix=".toml") as file:
                file.write(text)
                file.flush()
                with self.assertRaises(SystemExit):
                    rig.load_config(file.name)

    def test_refuses_a_period_shorter_than_its_cycle(self):
        with self.assertRaises(SystemExit):
            self.load(period_s=3.0)


class KickTest(unittest.TestCase):
    def test_a_stop_during_the_kick_stays_stopped(self):
        with tempfile.TemporaryDirectory() as folder:
            work = pathlib.Path(folder)
            path = work / "rig.toml"
            path.write_text(
                CONFIG.format(
                    port="x", data=work / "data", period=30.0, header_timeout=1.0, throttle=0.7,
                    kick="kick_throttle = 1.0\nkick_s = 0.5",
                )
            )
            motor_file = work / "motor"
            machine = rig.Rig(rig.load_config(path), rig.StubMotor(motor_file), None)
            now = time.monotonic()
            machine.next_burst = now + 1000.0
            machine.last_row = now + 10.0
            machine._start_motor(now)
            self.assertEqual(motor_file.read_text(), "1.0")
            machine._stop_motor()
            machine.tick(now + 1.0)  # past the kick's end: nothing may start the motor again
            self.assertEqual(motor_file.read_text(), "0")


class RunTest(unittest.TestCase):
    """rig.py and fake_nano.py as separate processes, as they run on the Pi."""

    def start(self, *fake_args, period=30.0, header_timeout=2.0, throttle=1.0, kick=""):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        work = pathlib.Path(self.dir.name)
        self.data = work / "data"
        self.motor = work / "motor"
        link = work / "tty"
        self.fake = subprocess.Popen(
            [sys.executable, str(RIG_DIR / "fake_nano.py"), "--link", str(link), "--motor-file", str(self.motor), *fake_args]
        )
        self.addCleanup(self.fake.wait)
        self.addCleanup(self.fake.kill)
        deadline = time.monotonic() + 5
        while not link.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        config = work / "rig.toml"
        config.write_text(
            CONFIG.format(port=link, data=self.data, period=period, header_timeout=header_timeout, throttle=throttle, kick=kick)
        )
        self.rig = subprocess.Popen(
            [sys.executable, str(RIG_DIR / "rig.py"), "--config", str(config), "--stub-motor", str(self.motor), "run"],
            stderr=subprocess.DEVNULL,
        )
        self.addCleanup(self.rig.wait)
        self.addCleanup(self.rig.kill)

    def rows(self, name):
        path = self.data / name
        if not path.exists():
            return []
        with open(path, encoding="ascii") as source:
            return list(csv.DictReader(source))

    def wait_for_summary(self, count=1, timeout=25.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            rows = self.rows("summary.csv")
            if len(rows) >= count:
                return rows
            time.sleep(0.05)
        self.fail(f"no summary row {count} within {timeout} s; events: {self.rows('events.csv')}")

    def wait_for_motor(self, wanted, timeout=10.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.motor.exists() and self.motor.read_text() == wanted:
                return
            time.sleep(0.01)
        self.fail(f"motor never read {wanted!r}")

    def stop_rig(self):
        self.rig.send_signal(signal.SIGTERM)
        return self.rig.wait(timeout=5)

    def test_a_burst_picks_the_sample_and_the_air(self):
        self.start()
        row = self.wait_for_summary()[0]
        self.assertEqual(row["verdict"], "ok")
        self.assertAlmostEqual(float(row["sample_level"]), 660.0, delta=2.0)
        self.assertAlmostEqual(float(row["air_level"]), 474.5, delta=2.0)
        self.assertEqual(self.motor.read_text(), "0")
        raw = [name.name for name in self.data.glob("raw-*.csv")]
        self.assertEqual(len(raw), 1)
        phases = {entry["phase"] for entry in self.rows(raw[0])}
        self.assertEqual(phases, {"idle", "burst"})

    def test_the_motor_only_runs_for_the_burst(self):
        self.start()
        self.wait_for_summary()
        started = time.monotonic()
        while time.monotonic() - started < 1.5:
            self.assertEqual(self.motor.read_text(), "0")
            time.sleep(0.05)

    def test_sample_reading_like_air_gives_no_number(self):
        self.start("--sample", "470")
        row = self.wait_for_summary()[0]
        self.assertNotEqual(row["verdict"], "ok")
        self.assertEqual(row["sample_level"], "")

    def test_a_stalled_crank_shows_no_motion(self):
        self.start("--stalled")
        self.assertEqual(self.wait_for_summary()[0]["verdict"], "no_motion")

    def test_a_sticky_crank_stalls_without_a_kick(self):
        self.start("--breakaway", "0.8", throttle=0.7)
        self.assertEqual(self.wait_for_summary()[0]["verdict"], "no_motion")

    def test_a_kick_frees_a_sticky_crank_and_the_burst_runs_at_the_set_throttle(self):
        self.start("--breakaway", "0.8", throttle=0.7, kick="kick_throttle = 1.0\nkick_s = 0.4")
        row = self.wait_for_summary()[0]
        self.assertEqual(row["verdict"], "ok")
        raw = self.rows(next(self.data.glob("raw-*.csv")).name)
        burst = [entry["throttle"] for entry in raw if entry["phase"] == "burst"]
        self.assertEqual(burst[0], "1.0")
        self.assertEqual(burst[-1], "0.7")
        self.assertLess(burst.count("1.0"), 40)  # 0.4 s at 50 Hz, not the whole burst

    def test_a_stop_during_the_kick_is_not_undone_by_it(self):
        self.start(throttle=0.7, kick="kick_throttle = 1.0\nkick_s = 0.5")
        self.wait_for_motor("1.0")
        self.assertEqual(self.stop_rig(), 0)
        self.assertEqual(self.motor.read_text(), "off")

    def test_a_late_header_is_retried(self):
        self.start("--header-after", "1.5", header_timeout=0.4)
        self.assertEqual(self.wait_for_summary()[0]["verdict"], "ok")
        self.assertIn("link_retry", {entry["event"] for entry in self.rows("events.csv")})

    def test_losing_the_nano_mid_burst_stops_the_motor_and_recovers(self):
        self.start("--silence-at", "2.0", "--silence-for", "3.0", period=6.0)
        self.wait_for_motor("1.0")
        self.assertEqual(self.rig.poll(), None)
        self.wait_for_motor("0", timeout=3.0)  # the burst alone would end at about 4.5 s
        rows = self.wait_for_summary(count=2)
        self.assertEqual(rows[0]["verdict"], "aborted")
        self.assertEqual(rows[1]["verdict"], "ok")
        self.assertIn("link_lost", {entry["event"] for entry in self.rows("events.csv")})

    def test_terminating_mid_burst_turns_the_motor_off(self):
        self.start()
        self.wait_for_motor("1.0")
        self.assertEqual(self.stop_rig(), 0)
        self.assertEqual(self.motor.read_text(), "off")
        self.assertEqual(self.rows("events.csv")[-1]["event"], "stop")


if __name__ == "__main__":
    unittest.main()
