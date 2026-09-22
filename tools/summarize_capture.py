#!/usr/bin/env python3
"""Summarize captured CSV logs: one row per file and signal column.

Reads each file by header name and reports count, mean, sample standard
deviation, min and max for every signal column present. Output is CSV on
stdout, so bench steps can be compared side by side or loaded elsewhere.
"""
import argparse
import csv
import math
import statistics
import sys

SIGNAL_COLUMNS = ("adc_counts", "dark_adc_counts", "vcc_mv", "raw_mv")


def summarize(path):
    with open(path, newline="", encoding="ascii") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or "timestamp_ms" not in reader.fieldnames:
            raise ValueError(f"{path}: missing CSV header with timestamp_ms")
        columns = [name for name in SIGNAL_COLUMNS if name in reader.fieldnames]
        values = {name: [] for name in columns}
        timestamps = []
        for line_number, row in enumerate(reader, start=2):
            try:
                timestamps.append(int(row["timestamp_ms"]))
                for name in columns:
                    value = float(row[name])
                    if not math.isfinite(value):
                        raise ValueError
                    values[name].append(value)
            except (TypeError, ValueError):
                raise ValueError(f"{path}:{line_number}: malformed row") from None

    if not timestamps:
        raise ValueError(f"{path}: no data rows")

    duration_s = (timestamps[-1] - timestamps[0]) / 1000.0
    for name in columns:
        series = values[name]
        yield {
            "file": path,
            "column": name,
            "n": len(series),
            "duration_s": f"{duration_s:.1f}",
            "mean": f"{statistics.fmean(series):.3f}",
            "std": f"{statistics.stdev(series):.3f}" if len(series) > 1 else "",
            "min": f"{min(series):.3f}",
            "max": f"{max(series):.3f}",
        }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+", help="capture CSV files")
    args = parser.parse_args(argv)

    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=["file", "column", "n", "duration_s", "mean", "std", "min", "max"],
        lineterminator="\n",
    )
    writer.writeheader()
    try:
        for path in args.files:
            for summary in summarize(path):
                writer.writerow(summary)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
