#!/usr/bin/env python3
"""Pick the culture out of saved raw logs: one CSV row per burst, on stdout. It changes no file.

    pick_samples.py ~/rig-data/algae-run-1b/raw-*.csv
"""
import argparse
import collections
import csv
import datetime
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import rig  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("raw", nargs="+")
    parser.add_argument("--config", default=str(pathlib.Path(__file__).with_name("rig.toml")))
    args = parser.parse_args()
    config = rig.load_config(args.config)
    column = f"adc_counts_{config['channel']}"
    bursts = collections.OrderedDict()
    for path in args.raw:
        with open(path, encoding="ascii", errors="replace") as source:
            for row in csv.DictReader(source):
                if row["phase"] == "burst" and row.get(column):
                    bursts.setdefault(int(row["burst"]), []).append(float(row[column]))
    out = csv.writer(sys.stdout, lineterminator="\n")
    out.writerow(["time_utc", "burst", "burst_rows", "sample_level", "sample_rows", "sample_std", "air_level", "verdict"])
    for burst, values in bursts.items():
        when = datetime.datetime.fromtimestamp(burst, datetime.timezone.utc).isoformat(timespec="seconds")
        out.writerow([when, burst, len(values), *rig.pick_sample(values, config["levels"])])
    return 0


if __name__ == "__main__":
    sys.exit(main())
