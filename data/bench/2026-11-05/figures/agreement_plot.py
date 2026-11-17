#!/usr/bin/env python3
"""Cary OD750 against the Sensor (A2) reading at the same time, one point per Cary sample. Standard library only."""
import csv
import datetime
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
CLEAR = 854.1
FIT_END = datetime.datetime(2026, 11, 12)  # the fit uses reads up to here; later reads test it
TOPUPS = [datetime.datetime(2026, 11, 9, 19, 38), datetime.datetime(2026, 11, 11, 21, 54), datetime.datetime(2026, 11, 14, 0, 26)]
sens = [(datetime.datetime.strptime(r["time_local"], "%Y-%m-%d %H:%M"), float(r["a2_counts"])) for r in csv.DictReader(open(HERE / "growth_test_sensor.csv"))]
pts = []
for r in csv.DictReader(open(HERE / "growth_test_cary.csv")):
    t = datetime.datetime.strptime(r["time_local"], "%Y-%m-%d %H:%M")
    # bursts within 16 min, on the same side of any DI top-up as the sample
    near = [c for s, c in sens if abs((s - t).total_seconds()) <= 16 * 60 and not any(min(s, t) < u < max(s, t) for u in TOPUPS)]
    if not near:
        continue
    reads = [float(v) for v in r["reads_multiplied_back"].split()]
    pts.append((t, sum(near) / len(near), float(r["mean_od750"]), min(reads), max(reads), r["note"]))

solid = [(c, od) for t, c, od, _, _, note in pts if not note and t < FIT_END]
later = [(c, od) for t, c, od, _, _, note in pts if not note and t >= FIT_END]
xs = [math.log(-math.log(c / CLEAR)) for c, _ in solid]
ys = [math.log(od) for _, od in solid]
n = len(xs)
mx, my = sum(xs) / n, sum(ys) / n
p = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
k = math.exp(my - p * mx)
resid = [(k * (-math.log(c / CLEAR)) ** p) / od - 1 for c, od in solid]
pred = [(k * (-math.log(c / CLEAR)) ** p) / od - 1 for c, od in later]

W, H = 1600, 900
OFFSETS = {"Nov 09 10:20": (-14, -10, "end"), "Nov 09 19:24": (-14, -10, "end"), "Nov 09 23:03": (14, 22, "start"), "Nov 11 22:36": (-14, -12, "end"),
           "Nov 12 10:26": (20, 34, "start"), "Nov 12 22:32": (14, -8, "start"), "Nov 13 09:38": (14, 20, "start"),
           "Nov 14 09:31": (-14, -10, "end"), "Nov 14 00:24": (14, 20, "start")}
L, R, T, B = 150, 60, 80, 760
SURF, INK, INK2, GRID, ORANGE, BLUE = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1", "#eb6834", "#2a78d6"
X0, X1, Y0, Y1 = 850.0, 550.0, 0.0, 2.5  # x runs from clear on the left to denser on the right


def x(c):
    return L + (c - X0) / (X1 - X0) * (W - L - R)


def y(od):
    return B - (od - Y0) / (Y1 - Y0) * (B - T)


svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="{SURF}"/>']
for v in (850, 800, 750, 700, 650, 600, 550):
    svg.append(f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="{T}" y2="{B}" stroke="{GRID}"/>')
    svg.append(f'<text x="{x(v):.1f}" y="{B + 32}" font-size="20" fill="{INK2}" text-anchor="middle">{v}</text>')
for v in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5):
    svg.append(f'<line x1="{L}" x2="{W - R}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="{GRID}"/>')
    svg.append(f'<text x="{L - 12}" y="{y(v) + 6:.1f}" font-size="20" fill="{INK2}" text-anchor="end">{v:.1f}</text>')
# fit curve over the range of the solid points
lo, mid, hi = max(c for c, _ in solid) + 8, min(c for c, _ in solid), min(c for c, _ in solid + later) - 8


def curve(a, b):
    return " ".join(f"{x(a + (b - a) * i / 100):.1f},{y(k * (-math.log((a + (b - a) * i / 100) / CLEAR)) ** p):.1f}" for i in range(101))


svg.append(f'<polyline points="{curve(lo, mid)}" fill="none" stroke="{BLUE}" stroke-width="2"/>')
svg.append(f'<polyline points="{curve(mid, hi)}" fill="none" stroke="{BLUE}" stroke-width="2" stroke-dasharray="8 6"/>')
for t, c, od, rmin, rmax, note in pts:
    svg.append(f'<line x1="{x(c):.1f}" x2="{x(c):.1f}" y1="{y(rmin):.1f}" y2="{y(rmax):.1f}" stroke="{ORANGE}" stroke-width="2"/>')
    if t >= FIT_END and not note:
        svg.append(f'<rect x="{x(c) - 7:.1f}" y="{y(od) - 7:.1f}" width="14" height="14" fill="{ORANGE}" stroke="{ORANGE}" stroke-width="2.5"/>')
    else:
        svg.append(f'<circle cx="{x(c):.1f}" cy="{y(od):.1f}" r="8" fill="{SURF if note else ORANGE}" stroke="{ORANGE}" stroke-width="2.5"/>')
    label = t.strftime("%b %d %H:%M")
    dx, dy, anchor = OFFSETS.get(label, (14, 6, "start"))
    svg.append(f'<text x="{x(c) + dx:.1f}" y="{y(od) + dy:.1f}" font-size="16" fill="{INK2}" text-anchor="{anchor}">{label}</text>')
svg.append(f'<text x="{L}" y="{T - 30}" font-size="24" font-weight="bold" fill="{INK}">Cary OD750 against Sensor (A2) at the same time (growth test, Nov 8–14)</text>')
svg.append(f'<text x="34" y="{(T + B) / 2:.1f}" font-size="21" fill="{INK}" text-anchor="middle" transform="rotate(-90 34 {(T + B) / 2:.1f})">Cary OD750 (diluted, multiplied back)</text>')
svg.append(f'<text x="{(L + W - R) / 2:.1f}" y="{B + 66}" font-size="21" fill="{INK}" text-anchor="middle">Sensor (A2) reading at the same time (ADC counts, mean of bursts within 15 min); clearer ← → denser</text>')
ly = H - 30
items = [("dot", ORANGE, "Cary OD750, fitted"), ("square", ORANGE, "Cary OD750, after the fit"), ("dot", SURF, "Cary OD750, with caveat (see notes)")]
lx = L
for kind, fill, label in items:
    if kind == "dot":
        svg.append(f'<circle cx="{lx + 8}" cy="{ly - 6}" r="8" fill="{fill}" stroke="{ORANGE}" stroke-width="2.5"/>')
    else:
        svg.append(f'<rect x="{lx + 1}" y="{ly - 13}" width="14" height="14" fill="{fill}" stroke="{ORANGE}" stroke-width="2.5"/>')
    svg.append(f'<text x="{lx + 26}" y="{ly}" font-size="19" fill="{INK}">{label}</text>')
    lx += 26 + len(label) * 10 + 30
svg.append(f'<line x1="{lx}" x2="{lx + 30}" y1="{ly - 6}" y2="{ly - 6}" stroke="{BLUE}" stroke-width="2"/>')
svg.append(f'<text x="{lx + 40}" y="{ly}" font-size="19" fill="{INK}">Fit (Nov 8–11); later reads {min(pred) * 100:+.1f}% to {max(pred) * 100:+.1f}% from it</text>')
svg.append("</svg>")
(HERE / "agreement.svg").write_text("\n".join(svg))
print(f"fit OD = {k:.3f} * (-ln(counts/{CLEAR}))^{p:.3f} on {n} reads; residuals {min(resid) * 100:+.1f}% to {max(resid) * 100:+.1f}%;"
      f" {len(later)} later reads {min(pred) * 100:+.1f}% to {max(pred) * 100:+.1f}%")
