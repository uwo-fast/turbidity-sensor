#!/usr/bin/env python3
"""One burst at 50 Hz: a normal burst (left) and the first after the stall (right), with the air band and the picked culture rows."""
import csv
import datetime
import gzip
import importlib.util
import pathlib
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
RUN = HERE.parent / "rig-data" / "algae-run-1c"
REPO = HERE.parents[3]
spec = importlib.util.spec_from_file_location("rig", REPO / "rig" / "pi" / "rig.py")
rig = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rig)
LEVELS = tomllib.loads((REPO / "rig" / "pi" / "rig.toml").read_text())["levels"]
TZ = datetime.timezone(datetime.timedelta(hours=-5))
BURSTS = [("20261110", "1794319441"), ("20261115", "1794749641")]


def burst_rows(day, burst):
    rows = []
    with gzip.open(RUN / f"raw-{day}.csv.gz", "rt") as fh:
        for r in csv.DictReader(fh):
            if r["phase"] == "burst" and r["burst"] == burst:
                rows.append((datetime.datetime.fromisoformat(r["time_utc"]), float(r["adc_counts_a2"])))
    return rows


def picked_rows(values):
    """Indices of the rows pick_sample counts as culture, from the same plateaus and band."""
    sample, _, _, _, _ = rig.pick_sample(values, LEVELS)
    if sample is None:
        return set(), None
    keep, i = set(), 0
    for run in rig.plateaus(values, LEVELS["plateau_rows"], LEVELS["plateau_step"]):
        # plateaus() returns slices in order; find each one's start in values
        while values[i:i + len(run)] != run:
            i += 1
        med = sorted(run)[len(run) // 2]
        if med > LEVELS["air_reference"] + LEVELS["near_air"] and abs(med - sample) <= LEVELS["sample_band"]:
            keep.update(range(i, i + len(run)))
        i += len(run)
    return keep, sample


W, H = 1600, 720
PANELS = [(150, 760), (840, 1450)]
T, B = 90, 580
SURF, INK, INK2, GRID, ORANGE, BLUE, BAND = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1", "#eb6834", "#2a78d6", "#eceae4"
Y0, Y1 = 0.0, 1000.0


def y(v):
    return B - (v - Y0) / (Y1 - Y0) * (B - T)


svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="{SURF}"/>']
air_lo, air_hi = LEVELS["air_reference"] - LEVELS["near_air"], LEVELS["air_reference"] + LEVELS["near_air"]
for (L, R), (day, burst) in zip(PANELS, BURSTS):
    rows = burst_rows(day, burst)
    values = [v for _, v in rows]
    t0 = rows[0][0]
    secs = [(t - t0).total_seconds() for t, _ in rows]
    span = 19.0

    def x(s, L=L, R=R):
        return L + s / span * (R - L)

    _, n, _, air, verdict = rig.pick_sample(values, LEVELS)
    # a burst that never swung gives no reading, whatever level it sat at
    keep, sample = picked_rows(values) if verdict != "no_motion" else (set(), None)
    svg.append(f'<rect x="{L}" y="{y(air_hi):.1f}" width="{R - L}" height="{y(air_lo) - y(air_hi):.1f}" fill="{BAND}"/>')
    for v in (0, 200, 400, 600, 800, 1000):
        svg.append(f'<line x1="{L}" x2="{R}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="{GRID}"/>')
        svg.append(f'<text x="{L - 12}" y="{y(v) + 6:.1f}" font-size="20" fill="{INK2}" text-anchor="end">{v}</text>')
    for s in range(0, 20, 5):
        svg.append(f'<text x="{x(s):.1f}" y="{B + 30}" font-size="20" fill="{INK2}" text-anchor="middle">{s}</text>')
    pts = " ".join(f"{x(s):.1f},{y(v):.1f}" for s, v in zip(secs, values))
    svg.append(f'<polyline points="{pts}" fill="none" stroke="{BLUE}" stroke-width="1.5"/>')
    for i in sorted(keep):
        svg.append(f'<circle cx="{x(secs[i]):.1f}" cy="{y(values[i]):.1f}" r="2.5" fill="{ORANGE}"/>')
    if sample is not None:
        svg.append(f'<line x1="{L}" x2="{R}" y1="{y(sample):.1f}" y2="{y(sample):.1f}" stroke="{ORANGE}" stroke-width="2" stroke-dasharray="8 6"/>')
    when = t0.astimezone(TZ).strftime("%b %d %H:%M")
    level = f"reading {sample:.1f} from {n} rows" if sample is not None else "no reading"
    svg.append(f'<text x="{L}" y="{T - 40}" font-size="22" font-weight="bold" fill="{INK}">{when}: {verdict}</text>')
    svg.append(f'<text x="{L}" y="{T - 14}" font-size="19" fill="{INK2}">{level}; swing {max(values) - min(values):.0f} counts</text>')
    print(f"{when} burst {burst}: {verdict}, {level}, air {air}, {len(values)} rows")
svg.append(f'<text x="34" y="{(T + B) / 2:.1f}" font-size="21" fill="{INK}" text-anchor="middle" transform="rotate(-90 34 {(T + B) / 2:.1f})">Sensor (A2) reading (ADC counts)</text>')
svg.append(f'<text x="{(PANELS[0][0] + PANELS[1][1]) / 2:.1f}" y="{B + 66}" font-size="21" fill="{INK}" text-anchor="middle">Time from the start of the burst (s)</text>')
ly = H - 28
lx = PANELS[0][0]
svg.append(f'<line x1="{lx}" x2="{lx + 30}" y1="{ly - 6}" y2="{ly - 6}" stroke="{BLUE}" stroke-width="2"/>')
svg.append(f'<text x="{lx + 40}" y="{ly}" font-size="19" fill="{INK}">Sensor (A2), 50 Hz</text>')
lx += 250
svg.append(f'<circle cx="{lx + 8}" cy="{ly - 6}" r="5" fill="{ORANGE}"/>')
svg.append(f'<text x="{lx + 22}" y="{ly}" font-size="19" fill="{INK}">Rows picked as culture</text>')
lx += 270
svg.append(f'<line x1="{lx}" x2="{lx + 30}" y1="{ly - 6}" y2="{ly - 6}" stroke="{ORANGE}" stroke-width="2" stroke-dasharray="8 6"/>')
svg.append(f'<text x="{lx + 40}" y="{ly}" font-size="19" fill="{INK}">Reading (median of picked rows)</text>')
lx += 360
svg.append(f'<rect x="{lx}" y="{ly - 16}" width="22" height="20" fill="{BAND}" stroke="{GRID}"/>')
svg.append(f'<text x="{lx + 30}" y="{ly}" font-size="19" fill="{INK}">Air band: culture must read above it</text>')
svg.append("</svg>")
(HERE / "burst.svg").write_text("\n".join(svg))
