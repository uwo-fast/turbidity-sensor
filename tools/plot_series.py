#!/usr/bin/env python3
"""Plot a concentration series from capture files as SVG, standard library only.

Each capture's concentration comes from its name (`..._c1000_...` is 1000 mg/L).
Every ADC column is normalized against its own clear (and, optionally, dark)
captures, as in summarize_capture.py:

    transmittance = (mean - dark) / (clear - dark)
    attenuation   = -ln(transmittance)

Captures at the same concentration are repeat fills: the plots show their mean
and, with two or more, their sample standard deviation as error bars. Writes
<name>_change.svg (percent change from clear) and <name>_attenuation.svg, and
prints the table behind them.
"""
import argparse
import math
import os
import re
import statistics
import sys

from summarize_capture import is_adc, read_capture

COLOURS = ("#0072B2", "#D55E00", "#009E73", "#CC79A7")
W, H, LEFT, RIGHT, TOP, BOTTOM = 640, 420, 70, 20, 40, 50


def column_means(paths):
    means = {}
    for path in paths:
        _, columns = read_capture(path)
        for name, values in columns.items():
            if is_adc(name):
                means.setdefault(name, []).append(statistics.fmean(values))
    return {name: statistics.fmean(values) for name, values in means.items()}


def concentration(path):
    match = re.search(r"_c(\d+)", os.path.basename(path))
    if not match:
        sys.exit(f"error: no _c<mg/L> in the name of {path}")
    return int(match.group(1))


def svg(path, title, ylabel, series):
    """series: [(label, [(x, y, sd_or_None)])]"""
    points = [p for _, pts in series for p in pts]
    x_max = max(x for x, _, _ in points) or 1
    lows = [y - (sd or 0) for _, y, sd in points] + [0]
    highs = [y + (sd or 0) for _, y, sd in points] + [0]
    y_min, y_max = min(lows), max(highs)
    pad = (y_max - y_min) * 0.05 or 1
    y_min, y_max = y_min - pad, y_max + pad

    def px(x):
        return LEFT + x / x_max * (W - LEFT - RIGHT)

    def py(y):
        return TOP + (y_max - y) / (y_max - y_min) * (H - TOP - BOTTOM)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif" font-size="12">',
           f'<rect width="{W}" height="{H}" fill="white"/>',
           f'<text x="{W / 2}" y="22" text-anchor="middle" font-size="14">{title}</text>',
           f'<line x1="{LEFT}" y1="{py(0)}" x2="{W - RIGHT}" y2="{py(0)}" stroke="#999"/>',
           f'<line x1="{LEFT}" y1="{TOP}" x2="{LEFT}" y2="{H - BOTTOM}" stroke="#333"/>',
           f'<text x="{W / 2}" y="{H - 10}" text-anchor="middle">kaolin (mg/L)</text>',
           f'<text x="16" y="{H / 2}" text-anchor="middle" transform="rotate(-90 16 {H / 2})">{ylabel}</text>']
    for i in range(5):
        x = x_max * i / 4
        out.append(f'<text x="{px(x)}" y="{H - BOTTOM + 16}" text-anchor="middle">{x:g}</text>')
    step = 10 ** math.floor(math.log10((y_max - y_min) / 5))
    step *= next(m for m in (1, 2, 5, 10) if (y_max - y_min) / (step * m) <= 6)
    y = math.ceil(y_min / step) * step
    while y <= y_max:
        out.append(f'<text x="{LEFT - 6}" y="{py(y) + 4}" text-anchor="end">{y:g}</text>')
        out.append(f'<line x1="{LEFT - 3}" y1="{py(y)}" x2="{LEFT}" y2="{py(y)}" stroke="#333"/>')
        y = round(y + step, 10)
    for n, (label, pts) in enumerate(series):
        colour = COLOURS[n % len(COLOURS)]
        pts = sorted(pts)
        out.append(f'<polyline fill="none" stroke="{colour}" points="{" ".join(f"{px(x)},{py(y)}" for x, y, _ in pts)}"/>')
        for x, y, sd in pts:
            if sd:
                out.append(f'<line x1="{px(x)}" y1="{py(y - sd)}" x2="{px(x)}" y2="{py(y + sd)}" stroke="{colour}"/>')
            out.append(f'<circle cx="{px(x)}" cy="{py(y)}" r="3" fill="{colour}"/>')
        out.append(f'<text x="{W - RIGHT - 120}" y="{TOP + 16 * (n + 1)}" fill="{colour}">{label}</text>')
    out.append("</svg>\n")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(out))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+", help="captures named ..._c<mg/L>...; repeats at one concentration are averaged")
    parser.add_argument("--clear", nargs="+", required=True, help="clear-water captures (their means are averaged)")
    parser.add_argument("--dark", nargs="+", help="dark captures; default: dark is 0")
    parser.add_argument("--columns", nargs="+", help="ADC columns to plot; default: all in the clear captures")
    parser.add_argument("--label", nargs="+", default=[], help="column=label pairs for the legend")
    parser.add_argument("--title", default="")
    parser.add_argument("--out-dir", default="build/plots")
    parser.add_argument("--name", default="series")
    args = parser.parse_args(argv)

    clear = column_means(args.clear)
    dark = column_means(args.dark) if args.dark else {}
    labels = dict(pair.split("=", 1) for pair in args.label)
    columns = args.columns or sorted(clear)
    fills = {}
    for path in args.files:
        fills.setdefault(concentration(path), []).append(column_means([path]))

    change, attenuation = [], []
    print("column,mg_per_l,fills,change_pct,change_sd,attenuation,attenuation_sd")
    for column in columns:
        d = dark.get(column, 0.0)
        c_pts, a_pts = [], []
        for conc, rows in sorted(fills.items()):
            t = [(row[column] - d) / (clear[column] - d) for row in rows]
            pct = [100 * (v - 1) for v in t]
            att = [-math.log(v) for v in t]
            sd_pct = statistics.stdev(pct) if len(pct) > 1 else None
            sd_att = statistics.stdev(att) if len(att) > 1 else None
            c_pts.append((conc, statistics.fmean(pct), sd_pct))
            a_pts.append((conc, statistics.fmean(att), sd_att))
            print(f"{column},{conc},{len(rows)},{c_pts[-1][1]:.2f},{sd_pct or 0:.2f},{a_pts[-1][1]:.4f},{sd_att or 0:.4f}")
        label = labels.get(column, column)
        change.append((label, c_pts))
        attenuation.append((label, a_pts))

    os.makedirs(args.out_dir, exist_ok=True)
    stem = os.path.join(args.out_dir, args.name)
    svg(stem + "_change.svg", args.title, "change from clear (%)", change)
    svg(stem + "_attenuation.svg", args.title, "attenuation, -ln T", attenuation)
    print(f"wrote {stem}_change.svg and {stem}_attenuation.svg", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
