#!/usr/bin/env python3
"""Capture the Arduino example's CSV log from a serial port to a file.

Standard library only (POSIX termios), so it runs on Linux and macOS without
pyserial. Opening the port resets most Arduino boards, so the capture starts
from the CSV header. Anything received before the header is discarded, and a
final line cut off mid-transfer is dropped, so the file always replays through
turbidity_stream.
"""
import argparse
import os
import select
import sys
import termios
import time
import tty

BAUD_RATES = {
    9600: termios.B9600,
    19200: termios.B19200,
    38400: termios.B38400,
    57600: termios.B57600,
    115200: termios.B115200,
}
HEADER_PREFIX = "timestamp_ms,"


def open_port(path, baud):
    fd = os.open(path, os.O_RDWR | os.O_NOCTTY)
    tty.setraw(fd)
    attributes = termios.tcgetattr(fd)
    attributes[4] = BAUD_RATES[baud]
    attributes[5] = BAUD_RATES[baud]
    termios.tcsetattr(fd, termios.TCSANOW, attributes)
    termios.tcflush(fd, termios.TCIFLUSH)
    return fd


def capture(fd, output, duration_s, header_timeout_s):
    """Writes header and complete rows to `output`. Returns the row count.

    Ctrl+C ends the capture normally and keeps the rows received so far.
    """
    started = time.monotonic()
    pending = b""
    header_seen = False
    rows = 0

    try:
        while True:
            elapsed = time.monotonic() - started
            if not header_seen and elapsed > header_timeout_s:
                raise RuntimeError(f"no CSV header within {header_timeout_s:g} s; check the port, baud rate and sketch")
            if header_seen and duration_s is not None and elapsed >= duration_s:
                return rows

            ready, _, _ = select.select([fd], [], [], 0.2)
            if not ready:
                continue
            chunk = os.read(fd, 4096)
            if not chunk:
                raise RuntimeError("serial port closed")
            pending += chunk

            *lines, pending = pending.split(b"\n")
            for raw in lines:
                line = raw.rstrip(b"\r").decode("ascii", errors="replace")
                if not header_seen:
                    if line.startswith(HEADER_PREFIX):
                        header_seen = True
                        output.write(line + "\n")
                    continue
                if line.startswith(HEADER_PREFIX):
                    raise RuntimeError(f"board reset mid-capture after {rows} rows; the file holds the rows before the reset")
                output.write(line + "\n")
                output.flush()
                rows += 1
    except KeyboardInterrupt:
        return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", required=True, help="serial device, e.g. /dev/ttyACM0 or /dev/ttyUSB0")
    parser.add_argument("--output", required=True, help="CSV file to write (overwritten)")
    parser.add_argument("--baud", type=int, default=115200, choices=sorted(BAUD_RATES))
    parser.add_argument("--duration", type=float, default=None, help="seconds to record after the header; default: until Ctrl+C")
    parser.add_argument("--header-timeout", type=float, default=10.0, help="seconds to wait for the CSV header")
    args = parser.parse_args(argv)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    fd = open_port(args.port, args.baud)
    try:
        with open(args.output, "w", encoding="ascii", errors="replace", newline="") as output:
            print(f"capturing {args.port} -> {args.output} (Ctrl+C to stop)", file=sys.stderr)
            rows = capture(fd, output, args.duration, args.header_timeout)
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    finally:
        os.close(fd)

    print(f"captured {rows} rows to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
