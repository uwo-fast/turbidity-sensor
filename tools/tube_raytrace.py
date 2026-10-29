#!/usr/bin/env python3
"""Ray-trace the tube case's cross-section: how much light reaches the detector.

A 2D model in the plane across the tube. The emitter and detector windows face each
other at x = -4.15 and +4.15 mm (head_x0 in hardware/probe/probe.scad), each 1.4 mm
wide. The FEP tube (7.9375 mm OD, 6.35 mm ID) sits centred between them, with air
outside it. Rays leave every point of the emitter window, spread evenly over
+-half-angle, refract at each wall with Fresnel losses, and are dropped on total
internal reflection or on missing the next surface. The script reports the fraction
of emitted power that lands on the detector window for each fill, and its ratio to
an air-filled tube.

Not modelled: the windows' own lenses, the axis along the tube (no focusing there),
scattering, absorption. Standard library only.
"""
import argparse
import math
import random

WINDOW_X = 4.15
WINDOW_HALF_WIDTH = 0.7
TUBE_OUTER_R = 7.9375 / 2
TUBE_INNER_R = 6.35 / 2
N_FEP = 1.34
FILLS = {"air": 1.0, "water": 1.333, "isopropanol": 1.377}


def transmit(n1, n2, cos_i):
    """Fresnel power transmission (unpolarized) and cos of the refracted angle, or (0, None) on TIR."""
    sin_t = n1 / n2 * math.sqrt(max(0.0, 1 - cos_i * cos_i))
    if sin_t >= 1:
        return 0.0, None
    cos_t = math.sqrt(1 - sin_t * sin_t)
    rs = ((n1 * cos_i - n2 * cos_t) / (n1 * cos_i + n2 * cos_t)) ** 2
    rp = ((n1 * cos_t - n2 * cos_i) / (n1 * cos_t + n2 * cos_i)) ** 2
    return 1 - (rs + rp) / 2, cos_t


def hit_circle(p, d, r):
    b = p[0] * d[0] + p[1] * d[1]
    disc = b * b - (p[0] ** 2 + p[1] ** 2 - r * r)
    if disc < 0:
        return None
    ts = [t for t in (-b - math.sqrt(disc), -b + math.sqrt(disc)) if t > 1e-9]
    return min(ts) if ts else None


def detected_fraction(n_core, half_angle_deg, rays, seed):
    rng = random.Random(seed)
    surfaces = ((TUBE_OUTER_R, 1.0, N_FEP), (TUBE_INNER_R, N_FEP, n_core),
                (TUBE_INNER_R, n_core, N_FEP), (TUBE_OUTER_R, N_FEP, 1.0))
    total = 0.0
    for _ in range(rays):
        a = math.radians(rng.uniform(-half_angle_deg, half_angle_deg))
        p, d, w = [-WINDOW_X, rng.uniform(-WINDOW_HALF_WIDTH, WINDOW_HALF_WIDTH)], [math.cos(a), math.sin(a)], 1.0
        for r, n1, n2 in surfaces:
            t = hit_circle(p, d, r)
            if t is None:
                break
            p = [p[0] + t * d[0], p[1] + t * d[1]]
            nx, ny = p[0] / r, p[1] / r
            if d[0] * nx + d[1] * ny > 0:
                nx, ny = -nx, -ny
            cos_i = -(d[0] * nx + d[1] * ny)
            tr, cos_t = transmit(n1, n2, cos_i)
            if cos_t is None:
                break
            w *= tr
            k = n1 / n2
            d = [k * d[0] + (k * cos_i - cos_t) * nx, k * d[1] + (k * cos_i - cos_t) * ny]
        else:
            if d[0] > 0 and abs(p[1] + (WINDOW_X - p[0]) / d[0] * d[1]) <= WINDOW_HALF_WIDTH:
                total += w
    return total / rays


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--half-angles", type=float, nargs="+", default=[10, 20, 30, 45],
                        help="emitter half-angles to try, degrees")
    parser.add_argument("--rays", type=int, default=200000)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args(argv)

    print("half_angle_deg," + ",".join(f"{name},{name}_over_air" for name in FILLS))
    for half_angle in args.half_angles:
        fractions = {name: detected_fraction(n, half_angle, args.rays, args.seed) for name, n in FILLS.items()}
        cells = [f"{fractions[name]:.4f},{fractions[name] / fractions['air']:.3f}" for name in FILLS]
        print(f"{half_angle:g}," + ",".join(cells))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
