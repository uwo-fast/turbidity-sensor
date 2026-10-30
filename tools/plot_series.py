#!/usr/bin/env python3
"""Plot a concentration series from capture files as SVG, standard library only.

Each capture's level comes from its name (`..._c1000_...` is level 1000, by default
1000 mg/L kaolin). --x maps levels to other x values, such as cells/mL, with --xlabel
naming the axis.
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

# Validated categorical slots (CVD and normal-vision separation, all pairs); the marker
# shape repeats the identity for greyscale print and colour-vision deficiency.
COLOURS = ("#2a78d6", "#eb6834", "#1baf7a", "#6250d6")
SHAPES = ("circle", "square", "triangle", "diamond")
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"
W, H, LEFT, RIGHT, TOP, BOTTOM = 720, 500, 78, 24, 82, 58


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
        sys.exit(f"error: no _c<level> in the name of {path}")
    return int(match.group(1))


def nice_ticks(lo, hi, count=6):
    span = hi - lo or 1
    step = 10 ** math.floor(math.log10(span / count))
    step *= next(m for m in (1, 2, 2.5, 5, 10) if span / (step * m) <= count)
    first = math.ceil(lo / step - 1e-9) * step
    return [round(first + i * step, 10) for i in range(int((hi - first) / step + 1e-9) + 1)]


def marker(shape, x, y, colour):
    ring = f'stroke="{SURFACE}" stroke-width="2"'
    if shape == "square":
        return f'<rect x="{x - 4.5}" y="{y - 4.5}" width="9" height="9" fill="{colour}" {ring}/>'
    if shape == "triangle":
        return f'<polygon points="{x},{y - 5.5} {x + 5.5},{y + 4.5} {x - 5.5},{y + 4.5}" fill="{colour}" {ring}/>'
    if shape == "diamond":
        return f'<polygon points="{x},{y - 6} {x + 6},{y} {x},{y + 6} {x - 6},{y}" fill="{colour}" {ring}/>'
    return f'<circle cx="{x}" cy="{y}" r="5" fill="{colour}" {ring}/>'


def svg(path, title, subtitle, xlabel, ylabel, series, y_range, log_x, legend_at_bottom):
    """series: [(label, [(x, y, sd_or_None)])]; y_range: (low, high) or None to fit."""
    points = [p for _, pts in series for p in pts]
    xs = sorted({x for x, _, _ in points})
    if log_x:
        tx = math.log2
        x_lo, x_hi = tx(xs[0]) - 0.3, tx(xs[-1]) + 0.3
        x_ticks = xs
    else:
        tx = float
        x_lo, x_hi = 0.0, xs[-1] * 1.04
        x_ticks = nice_ticks(0, xs[-1])
    exponent = 0 if xs[-1] < 1e4 else int(math.floor(math.log10(xs[-1])))
    scale = 10 ** exponent
    if exponent:
        xlabel = f"{xlabel} (×10{str(exponent).translate(str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹'))})"

    if y_range:
        y_lo, y_hi = y_range
    else:
        y_lo = min([0] + [y - (sd or 0) for _, y, sd in points])
        y_hi = max([0] + [y + (sd or 0) for _, y, sd in points])
        pad = (y_hi - y_lo) * 0.05 or 1
        y_lo, y_hi = (y_lo - pad if y_lo < 0 else y_lo), (y_hi + pad if y_hi > 0 else y_hi)
    y_ticks = nice_ticks(y_lo, y_hi)

    def px(x):
        return LEFT + (tx(x) - x_lo) / (x_hi - x_lo) * (W - LEFT - RIGHT)

    def py(y):
        return TOP + (y_hi - y) / (y_hi - y_lo) * (H - TOP - BOTTOM)

    def fmt(v):
        return f"{v:g}".replace("-", "−")

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="Helvetica, Arial, sans-serif" font-size="13" fill="{INK}">',
           f'<rect width="{W}" height="{H}" fill="{SURFACE}"/>',
           f'<text x="{LEFT}" y="24" font-size="16" font-weight="600">{title}</text>',
           *(f'<text x="{LEFT}" y="{44 + 16 * i}" fill="{MUTED}" font-size="12">{line}</text>'
             for i, line in enumerate(subtitle))]
    for y in y_ticks:
        out.append(f'<line x1="{LEFT}" y1="{py(y)}" x2="{W - RIGHT}" y2="{py(y)}" stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{LEFT - 8}" y="{py(y) + 4}" text-anchor="end" fill="{MUTED}">{fmt(y)}</text>')
    for x in x_ticks:
        out.append(f'<line x1="{px(x)}" y1="{TOP}" x2="{px(x)}" y2="{H - BOTTOM}" stroke="{GRID}" stroke-width="1"/>')
        out.append(f'<text x="{px(x)}" y="{H - BOTTOM + 18}" text-anchor="middle" fill="{MUTED}">{fmt(round(x / scale, 6))}</text>')
    out.append(f'<line x1="{LEFT}" y1="{py(0)}" x2="{W - RIGHT}" y2="{py(0)}" stroke="{MUTED}" stroke-width="1"/>')
    out.append(f'<text x="{(LEFT + W - RIGHT) / 2}" y="{H - 14}" text-anchor="middle">{xlabel}</text>')
    out.append(f'<text x="20" y="{(TOP + H - BOTTOM) / 2}" text-anchor="middle" '
               f'transform="rotate(-90 20 {(TOP + H - BOTTOM) / 2})">{ylabel}</text>')

    for n, (_, pts) in enumerate(series):
        colour = COLOURS[n % len(COLOURS)]
        pts = sorted(pts)
        out.append(f'<polyline fill="none" stroke="{colour}" stroke-width="2" stroke-linejoin="round" '
                   f'points="{" ".join(f"{px(x):.1f},{py(y):.1f}" for x, y, _ in pts)}"/>')
        for x, y, sd in pts:
            if sd:
                x0, y0, y1 = px(x), py(y - sd), py(y + sd)
                out.append(f'<path d="M{x0},{y0}V{y1}M{x0 - 5},{y0}H{x0 + 5}M{x0 - 5},{y1}H{x0 + 5}" '
                           f'stroke="{colour}" stroke-width="1.5" fill="none"/>')
        for x, y, _ in pts:
            out.append(marker(SHAPES[n % len(SHAPES)], px(x), py(y), colour))

    row = 20
    ly = (H - BOTTOM - 12 - row * (len(series) - 1)) if legend_at_bottom else TOP + 14
    out.append(f'<rect x="{LEFT + 10}" y="{ly - 14}" width="190" height="{row * len(series) + 8}" '
               f'fill="{SURFACE}" fill-opacity="0.9" stroke="{GRID}"/>')
    for n, (label, _) in enumerate(series):
        colour, y = COLOURS[n % len(COLOURS)], ly + row * n
        out.append(f'<line x1="{LEFT + 18}" y1="{y - 4}" x2="{LEFT + 42}" y2="{y - 4}" stroke="{colour}" stroke-width="2"/>')
        out.append(marker(SHAPES[n % len(SHAPES)], LEFT + 30, y - 4, colour))
        out.append(f'<text x="{LEFT + 50}" y="{y}">{label}</text>')
    out.append("</svg>\n")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(out))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+", help="captures named ..._c<level>...; repeats at one level are averaged")
    parser.add_argument("--clear", nargs="+", required=True, help="clear-water captures (their means are averaged)")
    parser.add_argument("--dark", nargs="+", help="dark captures; default: dark is 0")
    parser.add_argument("--columns", nargs="+", help="ADC columns to plot; default: all in the clear captures")
    parser.add_argument("--label", nargs="+", default=[], help="column=label pairs for the legend")
    parser.add_argument("--x", nargs="+", default=[], help="level=value pairs (c0500=7.2e7) giving each _c level its x value")
    parser.add_argument("--xlabel", default="kaolin (mg/L)")
    parser.add_argument("--log-x", action="store_true", help="log2 x axis, for a series that doubles at each level")
    parser.add_argument("--title", default="")
    parser.add_argument("--out-dir", default="build/plots")
    parser.add_argument("--name", default="series")
    args = parser.parse_args(argv)

    clear = column_means(args.clear)
    dark = column_means(args.dark) if args.dark else {}
    labels = dict(pair.split("=", 1) for pair in args.label)
    columns = args.columns or sorted(clear)
    x_of = {int(k.lstrip("c")): float(v) for k, v in (pair.split("=", 1) for pair in args.x)}
    fills = {}
    for path in args.files:
        level = concentration(path)
        if x_of and level not in x_of:
            sys.exit(f"error: no --x value for level {level} ({path})")
        fills.setdefault(x_of.get(level, level), []).append(column_means([path]))

    change, attenuation = [], []
    print("column,x,fills,change_pct,change_sd,attenuation,attenuation_sd")
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
            print(f"{column},{conc:g},{len(rows)},{c_pts[-1][1]:.2f},{sd_pct or 0:.2f},{a_pts[-1][1]:.4f},{sd_att or 0:.4f}")
        label = labels.get(column, column)
        change.append((label, c_pts))
        attenuation.append((label, a_pts))

    os.makedirs(args.out_dir, exist_ok=True)
    stem = os.path.join(args.out_dir, args.name)
    n = sorted({len(rows) for rows in fills.values()})
    fills_text = f"{n[0]}" if len(n) == 1 else f"{n[0]}–{n[-1]}"
    subtitle = (f"Mean of {fills_text} fills per point, each head against its own clear reference.",
                "Error bars ±1 SD; where none shows, the SD is smaller than the marker.")
    svg(stem + "_change.svg", args.title, subtitle, args.xlabel, "change from clear (%)", change,
        (-100, 0), args.log_x, legend_at_bottom=True)
    svg(stem + "_attenuation.svg", args.title, subtitle, args.xlabel, "attenuation, −ln T", attenuation,
        None, args.log_x, legend_at_bottom=False)
    print(f"wrote {stem}_change.svg and {stem}_attenuation.svg", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
