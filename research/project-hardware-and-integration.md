# Project Hardware and Integration Notes

Researched on `2026-03-31`.

## The Most Important Architecture Clarification

For this repo, keep the hardware stack mentally split into three layers:

1. sensing element
2. conditioning / interface electronics
3. host MCU or SBC

Within that split:

- `TST-10` and `TSW-10` are the actual optical sensing elements
- `SEN0189` is the most relevant on-hand conditioning / interface reference path
- the host side may be Arduino, Raspberry Pi, or another embedded target

This distinction should stay explicit in future docs and firmware design.

## What the Repo Already Has

The repo already contains useful development artifacts:

- vendor datasheet PDFs under `datasheets/`
- digitized vendor-curve data under `calibration/vendor-data/`
- generated calibration tables:
  - `calibration/tst10-calibration.csv`
  - `calibration/tsw10-calibration.csv`
- generated plots and quadratic-fit reports:
  - `calibration/tst10-plot.png`
  - `calibration/tsw10-plot.png`
  - `calibration/tst10-fit.txt`
  - `calibration/tsw10-fit.txt`

These are good scaffolding for firmware and simulation work.

## What the Repo Does Not Yet Have

The repo does not yet establish:

- a validated analog front-end for the Amphenol sensing heads
- a bench-calibrated transfer function for a real assembled system
- a standards-traceable optical geometry or calibration workflow
- a confirmed one-to-one mapping between Amphenol sensor behavior and DFRobot board
  behavior

## Immediate Integration Consequences

### For firmware

A clean firmware architecture should separate:

- ADC reading / raw sample capture
- signal conditioning in software
- calibration mapping
- output / logging / host transport

That makes it easier to swap between:

- direct Amphenol sensor experimentation
- DFRobot-style conditioned analog output
- future bench-derived calibration models

### For electronics

The key unknown is not just the sensor curve. It is the full chain:

- sensor supply voltage stability
- output loading
- analog reference choice
- ADC resolution and noise floor
- any buffering, gain staging, or filtering between sensor and host
- cable length and grounding behavior

### For calibration

The current generated curves are useful starting points, but they represent vendor
curve reconstruction and interpolation, not physical truth for a specific build.

Use them for:

- early code paths
- plotting and sanity checks
- rough expected-voltage envelopes

Do not use them as final evidence of measurement accuracy.

## Practical Next Research / Build Questions

- What exact conditioning path is required for direct `TST-10` / `TSW-10` bring-up?
- Can the `SEN0189` board be cleanly repurposed as an interface path for the Amphenol
  heads, or is it better treated only as a conceptual reference?
- What ADC resolution and reference voltage are required to make the expected voltage
  differences meaningful in practice?
- What calibration fluids or reference instruments are realistically available for
  later bench work?
- Which use case matters most first: proof-of-life sensing, relative turbidity trends,
  or quantitative comparison against a known reference?

## Recommended Working Rules

- Treat vendor datasheet curves as scaffolding.
- Treat DFRobot examples and community formulas as bring-up aids.
- Prefer official vendor or standards material whenever there is conflict.
- Document source conflicts instead of averaging them away.
- Keep the firmware architecture flexible enough to survive future calibration changes.

## Sources

This note is a synthesis built from:

- `research/amphenol-turbidity-sensors.md`
- `research/dfrobot-sen0189.md`
- `research/turbidity-standards-and-units.md`
- local repo artifacts under `calibration/` and `datasheets/`
