#!/usr/bin/env python3
"""Stand in for the Nano and the crank on a pseudo-terminal, for testing rig.py with no hardware.

Prints the logger's CSV with the signal a head would see: the crank turns while the
throttle in --motor-file is not zero, and the beam reads air near the plunger's in
position and sample otherwise. The turn's geometry is the 5 mL actuator's.
"""
import argparse
import math
import os
import random
import sys
import time

THROW_MM = 25.25
ROD_MM = 90.0
FULL_THROTTLE_RPM = 35.0


def drawn(angle):
    """How far the plunger has drawn, 0 at its in position (angle 0) to 1 at its out position."""
    x = THROW_MM * math.cos(angle) + math.sqrt(ROD_MM**2 - (THROW_MM * math.sin(angle)) ** 2)
    return (THROW_MM + ROD_MM - x) / (2 * THROW_MM)


def read_throttle(path):
    try:
        with open(path, encoding="ascii") as source:
            text = source.read().strip()
    except OSError:
        return 0.0
    return 0.0 if text in ("", "off") else float(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--link", required=True, help="symlink to create to the pseudo-terminal")
    parser.add_argument("--motor-file", required=True)
    parser.add_argument("--air", type=float, default=474.5)
    parser.add_argument("--sample", type=float, default=660.0)
    parser.add_argument("--noise", type=float, default=0.5)
    parser.add_argument("--rate", type=float, default=50.0)
    parser.add_argument("--air-below", type=float, default=0.173, help="fraction of the stroke drawn at the meniscus")
    parser.add_argument("--header-after", type=float, default=0.5, help="seconds before the header")
    parser.add_argument("--stalled", action="store_true", help="the crank never turns")
    parser.add_argument("--breakaway", type=float, default=0.0, help="throttle a resting crank needs to start; once turning, any will do")
    parser.add_argument("--silence-at", type=float, help="seconds in: stop sending rows")
    parser.add_argument("--silence-for", type=float, default=0.0, help="then send a header, as a reset board does")
    args = parser.parse_args()

    master, slave = os.openpty()
    os.symlink(os.ttyname(slave), args.link)

    angle = 1.5  # starts in sample
    rng = random.Random(1)
    started = time.monotonic()
    sent_header = False
    silenced = False
    turning = False
    period = 1.0 / args.rate
    while True:
        now = time.monotonic() - started
        if not sent_header:
            if now >= args.header_after:
                os.write(master, b"timestamp_ms,vcc_mv,adc_counts_a0,adc_counts_a1,adc_counts_a2,adc_counts_a3\r\n")
                sent_header = True
            time.sleep(0.01)
            continue
        if args.silence_at is not None and not silenced and now >= args.silence_at:
            silenced = True
            time.sleep(args.silence_for)
            os.write(master, b"timestamp_ms,vcc_mv,adc_counts_a0,adc_counts_a1,adc_counts_a2,adc_counts_a3\r\n")

        throttle = read_throttle(args.motor_file)
        running = throttle != 0.0
        if running and abs(throttle) >= args.breakaway:
            turning = True
        if not running:
            turning = False
        if turning and not args.stalled:
            angle += 2 * math.pi * FULL_THROTTLE_RPM / 60.0 * abs(throttle) * period
        level = args.air if drawn(angle) < args.air_below else args.sample
        counts = level + rng.gauss(0.0, args.noise)
        row = f"{int(now * 1000)},4752,0.00,{counts:.2f},0.00,0.00\r\n"
        os.write(master, row.encode("ascii"))
        time.sleep(period)


if __name__ == "__main__":
    sys.exit(main())
