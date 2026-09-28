#!/usr/bin/env python3
"""Summarize captured CSV logs: one row per file and signal column.

Reads each file by header name and reports count, mean, sample standard
deviation, min and max for every signal column present, including the
per-channel adc_counts_* columns of the multichannel logger. Output is CSV on
stdout, so bench steps can be compared side by side or loaded elsewhere.

With --dark and --clear, each ADC column is also normalized against the same
column's mean in those two reference captures:

    transmittance = (mean - dark) / (clear - dark)
    attenuation   = -ln(transmittance)

Each head is normalized against its own references, which cancels differences
in gain between heads.
"""
import argparse
import csv
import math
import statistics
import sys

SIGNAL_COLUMNS = ("adc_counts", "dark_adc_counts", "vcc_mv", "raw_mv")
# 95% of the 10-bit ADC's 1024 counts: a clear reference above this may clip.
FULL_SCALE_WARN_COUNTS = 972


def is_signal(name):
    return name in SIGNAL_COLUMNS or name.startswith("adc_counts_")


def is_adc(name):
    return name == "adc_counts" or name.startswith("adc_counts_")


def read_capture(path):
    """Returns (duration_s, {column: [values]}) for the signal columns in header order."""
    with open(path, newline="", encoding="ascii") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or "timestamp_ms" not in reader.fieldnames:
            raise ValueError(f"{path}: missing CSV header with timestamp_ms")
        columns = [name for name in reader.fieldnames if is_signal(name)]
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
    return (timestamps[-1] - timestamps[0]) / 1000.0, values


def reference_means(path):
    _, values = read_capture(path)
    return {name: statistics.fmean(series) for name, series in values.items() if is_adc(name)}


def normalize(name, mean, dark, clear):
    for label, reference in (("dark", dark), ("clear", clear)):
        if name not in reference["means"]:
            raise ValueError(f"{reference['path']} has no {name} column; {label} references need every channel")
    span = clear["means"][name] - dark["means"][name]
    if span <= 0:
        raise ValueError(f"{name}: clear reference is not above dark")
    transmittance = (mean - dark["means"][name]) / span
    attenuation = f"{-math.log(transmittance):.4f}" if transmittance > 0 else ""
    return f"{transmittance:.4f}", attenuation


def summarize(path, dark=None, clear=None):
    duration_s, values = read_capture(path)
    for name, series in values.items():
        mean = statistics.fmean(series)
        summary = {
            "file": path,
            "column": name,
            "n": len(series),
            "duration_s": f"{duration_s:.1f}",
            "mean": f"{mean:.3f}",
            "std": f"{statistics.stdev(series):.3f}" if len(series) > 1 else "",
            "min": f"{min(series):.3f}",
            "max": f"{max(series):.3f}",
        }
        if dark is not None:
            summary["transmittance"], summary["attenuation"] = (
                normalize(name, mean, dark, clear) if is_adc(name) else ("", "")
            )
        yield summary


def load_reference(path):
    return {"path": path, "means": reference_means(path)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+", help="capture CSV files")
    parser.add_argument("--dark", help="capture with the beam blocked, for normalization")
    parser.add_argument("--clear", help="capture in clear water, for normalization")
    args = parser.parse_args(argv)
    if (args.dark is None) != (args.clear is None):
        parser.error("--dark and --clear go together")

    fieldnames = ["file", "column", "n", "duration_s", "mean", "std", "min", "max"]
    if args.dark is not None:
        fieldnames += ["transmittance", "attenuation"]
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    try:
        dark = clear = None
        if args.dark is not None:
            dark, clear = load_reference(args.dark), load_reference(args.clear)
            for name, mean in clear["means"].items():
                if mean >= FULL_SCALE_WARN_COUNTS:
                    print(
                        f"warning: {name}: clear reference {mean:.1f} counts is near full scale "
                        f"(>= {FULL_SCALE_WARN_COUNTS}); the head may clip",
                        file=sys.stderr,
                    )
        for path in args.files:
            for summary in summarize(path, dark, clear):
                writer.writerow(summary)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
