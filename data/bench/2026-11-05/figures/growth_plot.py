#!/usr/bin/env python3
"""Growth test figure: Sensor (A2) reading per burst (top) and Cary OD750 (bottom), shared time axis. Standard library only."""
import csv
import datetime
import math
import pathlib
import sys

TZ = datetime.timezone(datetime.timedelta(hours=-5))
OUT = pathlib.Path(__file__).resolve().parent
RUN = OUT.parent  # data/bench/2026-11-05
CLEAR = 854.1  # A2 clear through its own line, DI, 11-06 23:41-00:34, after reopening


def t(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=TZ)


START, END = t("2026-11-08 10:20"), t("2026-11-12 00:30")

# Cary OD750, growth test, from data/bench/2026-11-05/notes.md: (time, reads multiplied back, note)
CARY = [
    ("2026-11-08 10:55", [0.4376, 0.4344], ""),
    ("2026-11-08 23:30", [0.7924, 0.7822], ""),
    ("2026-11-09 10:20", [0.8086, 0.8008, 0.8457, 0.8175], "50 min after lamp on"),
    ("2026-11-09 19:24", [0.9681, 0.9801], ""),
    ("2026-11-09 23:03", [0.9968, 0.9236], "pair 8 % apart"),
    ("2026-11-10 10:05", [1.0505, 1.0640], ""),
    ("2026-11-10 11:36", [1.1090, 1.1060], ""),
    ("2026-11-10 21:40", [1.4055, 1.4410], ""),
    ("2026-11-11 09:10", [0.8945, 0.9055], "45 min after lamp on"),
    ("2026-11-11 21:38", [1.5130, 1.5105, 1.5048, 1.5168], ""),
    ("2026-11-11 22:36", [1.5355, 1.5305, 1.5588, 1.5516], "Cary blank shifted 0.01"),
]
# lamp off (dark) and other disturbances
DARK = [("2026-11-09 00:00", "2026-11-09 09:30"), ("2026-11-09 12:00", "2026-11-09 14:10"),
        ("2026-11-09 23:46", "2026-11-10 08:26"), ("2026-11-10 00:26", "2026-11-10 00:26"),
        ("2026-11-11 00:26", "2026-11-11 08:26")]
DARK = [d for d in DARK if d[0] != d[1]]
OUTAGE = ("2026-11-09 12:00", "2026-11-09 18:30")
EVENTS = [("2026-11-08 10:20", "1 L BG-11, start"), ("2026-11-09 19:38", "+150 mL DI"), ("2026-11-11 21:54", "+200 mL DI")]

picks = []
for r in csv.DictReader(open(RUN / "rig-data" / "picked-algae-run-1c.csv")):
    when = datetime.datetime.fromisoformat(r["time_utc"]).astimezone(TZ)
    if START <= when <= END and r["verdict"] in ("ok", "thin") and r["sample_level"]:
        picks.append((when, float(r["sample_level"]), r["verdict"]))

W, H = 1600, 900
L, R = 150, 40
P1 = (70, 440)   # top panel y range (px)
P2 = (510, 760)  # bottom panel
SURF, INK, INK2, GRID, SHADE, HATCH = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1", "#eceae4", "#d8d5cc"
BLUE, ORANGE = "#2a78d6", "#eb6834"


def x(when):
    return L + (when - START).total_seconds() / (END - START).total_seconds() * (W - L - R)


def yscale(lo, hi, top, bottom):
    return lambda v: bottom - (v - lo) / (hi - lo) * (bottom - top)


ya = yscale(850.0, 650.0, *P1)  # reversed: up = denser, as in the OD panel
yo = yscale(0.0, 1.8, *P2)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="{SURF}"/>',
       '<defs><pattern id="hatch" width="10" height="10" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">'
       f'<line x1="0" y1="0" x2="0" y2="10" stroke="{HATCH}" stroke-width="4"/></pattern></defs>']
for top, bottom in (P1, P2):
    for a, b in DARK:
        svg.append(f'<rect x="{x(t(a)):.1f}" y="{top}" width="{x(t(b)) - x(t(a)):.1f}" height="{bottom - top}" fill="{SHADE}"/>')
    a, b = OUTAGE
    svg.append(f'<rect x="{x(t(a)):.1f}" y="{top}" width="{x(t(b)) - x(t(a)):.1f}" height="{bottom - top}" fill="url(#hatch)"/>')
# gridlines and y labels
for v in (650, 700, 750, 800, 850):
    svg.append(f'<line x1="{L}" x2="{W - R}" y1="{ya(v):.1f}" y2="{ya(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
    svg.append(f'<text x="{L - 12}" y="{ya(v) + 6:.1f}" font-size="20" fill="{INK2}" text-anchor="end">{v}</text>')
for v in (0.0, 0.5, 1.0, 1.5):
    svg.append(f'<line x1="{L}" x2="{W - R}" y1="{yo(v):.1f}" y2="{yo(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
    svg.append(f'<text x="{L - 12}" y="{yo(v) + 6:.1f}" font-size="20" fill="{INK2}" text-anchor="end">{v:.1f}</text>')
# day ticks
day = START.replace(hour=0, minute=0) + datetime.timedelta(days=1)
while day <= END:
    xx = x(day)
    for top, bottom in (P1, P2):
        svg.append(f'<line x1="{xx:.1f}" x2="{xx:.1f}" y1="{top}" y2="{bottom}" stroke="{GRID}" stroke-width="1"/>')
    anchor = "end" if xx > W - R - 60 else "middle"
    svg.append(f'<text x="{xx:.1f}" y="{P2[1] + 30}" font-size="20" fill="{INK2}" text-anchor="{anchor}">{day.strftime("%a %b %d")}</text>')
    day += datetime.timedelta(days=1)
# events
for when, label in EVENTS:
    xx = x(t(when))
    for top, bottom in (P1, P2):
        svg.append(f'<line x1="{xx:.1f}" x2="{xx:.1f}" y1="{top}" y2="{bottom}" stroke="{INK2}" stroke-width="1.5"/>')
    anchor = "start" if xx < W - 260 else "end"
    dx = 6 if anchor == "start" else -6
    ly_ = P1[1] - 12 if when == EVENTS[0][0] else P1[0] + 22
    svg.append(f'<text x="{xx + dx:.1f}" y="{ly_}" font-size="18" fill="{INK}" text-anchor="{anchor}">{label}</text>')
# sensor points
for when, att, verdict in picks:
    fill = BLUE if verdict == "ok" else SURF
    svg.append(f'<circle cx="{x(when):.1f}" cy="{ya(att):.1f}" r="4" fill="{fill}" stroke="{BLUE}" stroke-width="1.5"/>')
# cary points with range bars
for when, reads, note in CARY:
    xx = x(t(when))
    mean = sum(reads) / len(reads)
    svg.append(f'<line x1="{xx:.1f}" x2="{xx:.1f}" y1="{yo(min(reads)):.1f}" y2="{yo(max(reads)):.1f}" stroke="{ORANGE}" stroke-width="2"/>')
    hollow = bool(note)
    svg.append(f'<circle cx="{xx:.1f}" cy="{yo(mean):.1f}" r="7" fill="{SURF if hollow else ORANGE}" stroke="{ORANGE}" stroke-width="2.5"/>')
# axes titles and panel titles
svg.append(f'<text x="{L}" y="{P1[0] - 18}" font-size="24" font-weight="bold" fill="{INK}">Sensor (A2): one reading per 15-min burst (axis reversed: up = denser)</text>')
svg.append(f'<text x="{L}" y="{P2[0] - 18}" font-size="24" font-weight="bold" fill="{INK}">Cary OD750: diluted samples, multiplied back</text>')
for (top, bottom), lines in ((P1, ("Sensor (A2) reading", "(ADC counts, reversed)")), (P2, ("Cary OD750", "(diluted, multiplied back)"))):
    cy = (top + bottom) / 2
    for lx, line in zip((26, 52), lines):
        svg.append(f'<text x="{lx}" y="{cy:.1f}" font-size="21" fill="{INK}" text-anchor="middle" transform="rotate(-90 {lx} {cy:.1f})">{line}</text>')
svg.append(f'<text x="{(L + W - R) / 2:.1f}" y="{P2[1] + 62}" font-size="21" fill="{INK}" text-anchor="middle">Date (2026, local time); tick at midnight</text>')
# legend row
ly = H - 22
items = [("dot", BLUE, BLUE, "Sensor (A2)"), ("dot", ORANGE, ORANGE, "Cary OD750"),
         ("dot", SURF, ORANGE, "Cary OD750, with caveat (see notes)"), ("rect", SHADE, None, "Lamp off"), ("hatch", None, None, "Power and air outage")]
lx = L
for kind, fill, stroke, label in items:
    if kind == "dot":
        svg.append(f'<circle cx="{lx + 8}" cy="{ly - 6}" r="7" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    elif kind == "rect":
        svg.append(f'<rect x="{lx}" y="{ly - 16}" width="22" height="20" fill="{fill}" stroke="{GRID}"/>')
    else:
        svg.append(f'<rect x="{lx}" y="{ly - 16}" width="22" height="20" fill="url(#hatch)" stroke="{GRID}"/>')
    svg.append(f'<text x="{lx + 30}" y="{ly}" font-size="19" fill="{INK}">{label}</text>')
    lx += 30 + len(label) * 10 + 34
svg.append("</svg>")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "growth_test.svg").write_text("\n".join(svg))
with open(OUT / "growth_test_sensor.csv", "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["time_local", "a2_counts", "verdict"])
    for when, level, verdict in picks:
        w.writerow([when.strftime("%Y-%m-%d %H:%M"), round(level, 2), verdict])
with open(OUT / "growth_test_cary.csv", "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["time_local", "reads_multiplied_back", "mean_od750", "note"])
    for when, reads, note in CARY:
        w.writerow([when, " ".join(f"{v:.4f}" for v in reads), round(sum(reads) / len(reads), 4), note])
print(len(picks), "sensor points;", len(CARY), "Cary points; counts range", round(min(p[1] for p in picks), 1), round(max(p[1] for p in picks), 1))
