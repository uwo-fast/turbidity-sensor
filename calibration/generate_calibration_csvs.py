#!/usr/bin/env python3
import csv
import os
import sys
from bisect import bisect_left
from collections import defaultdict


class CalibrationDataError(Exception):
    pass


def load_vendor_curve(csv_path):
    if not os.path.isfile(csv_path):
        raise CalibrationDataError(f"Missing vendor CSV: {csv_path}")

    buckets = defaultdict(list)
    with open(csv_path, newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        for line_number, row in enumerate(reader, start=1):
            if not row:
                continue
            if len(row) != 2:
                raise CalibrationDataError(
                    f"Malformed row in {csv_path}:{line_number}: expected 2 columns"
                )

            try:
                voltage = float(row[0].strip())
                ntu = float(row[1].strip())
            except ValueError as exc:
                raise CalibrationDataError(
                    f"Malformed numeric value in {csv_path}:{line_number}"
                ) from exc

            buckets[ntu].append(voltage)

    if len(buckets) < 2:
        raise CalibrationDataError(
            f"Not enough unique points in {csv_path} to interpolate calibration data"
        )

    curve = []
    for ntu in sorted(buckets):
        voltages = buckets[ntu]
        curve.append((ntu, sum(voltages) / len(voltages)))
    return curve


def interpolate_curve(curve, target_ntu):
    ntu_values = [point[0] for point in curve]
    idx = bisect_left(ntu_values, target_ntu)

    if idx < len(curve) and curve[idx][0] == target_ntu:
        return curve[idx][1]

    if idx == 0:
        left, right = curve[0], curve[1]
    elif idx == len(curve):
        left, right = curve[-2], curve[-1]
    else:
        left, right = curve[idx - 1], curve[idx]

    ntu0, voltage0 = left
    ntu1, voltage1 = right
    if ntu1 == ntu0:
        return voltage0

    fraction = (target_ntu - ntu0) / (ntu1 - ntu0)
    return voltage0 + fraction * (voltage1 - voltage0)


def write_calibration_csv(output_path, high_curve, low_curve, max_ntu):
    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["NTU", "Voltage (High)", "Voltage (Low)"])

        for ntu in range(0, max_ntu + 1, 100):
            high_voltage = interpolate_curve(high_curve, ntu)
            low_voltage = interpolate_curve(low_curve, ntu)
            writer.writerow(
                [ntu, f"{high_voltage:.3f}", f"{low_voltage:.3f}"]
            )


def generate_sensor_csvs(calibration_dir):
    sensors = [
        {
            "slug": "tst10",
            "label": "TST-10",
            "max_ntu": 4000,
        },
        {
            "slug": "tsw10",
            "label": "TSW-10",
            "max_ntu": 2000,
        },
    ]

    vendor_dir = os.path.join(calibration_dir, "vendor-data")

    for sensor in sensors:
        high_path = os.path.join(vendor_dir, f"{sensor['slug']}-high.csv")
        low_path = os.path.join(vendor_dir, f"{sensor['slug']}-low.csv")
        output_path = os.path.join(calibration_dir, f"{sensor['slug']}-calibration.csv")

        high_curve = load_vendor_curve(high_path)
        low_curve = load_vendor_curve(low_path)
        write_calibration_csv(output_path, high_curve, low_curve, sensor["max_ntu"])
        print(f"Generated {sensor['label']} calibration CSV: {output_path}")


def main():
    calibration_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        generate_sensor_csvs(calibration_dir)
    except CalibrationDataError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
