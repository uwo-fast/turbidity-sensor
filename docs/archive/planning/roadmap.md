# Roadmap

## Purpose

This roadmap turns the current repo state into a deliberate sequence of technical work.
It is meant to sit next to `planning/context.md`:

- `planning/context.md` explains what the project is, what is known, and what is still
  uncertain.
- `planning/roadmap.md` explains what to do next and in what order.

## Where the Project Stands Now

The repo already has a useful base:

- primary vendor and standards references in `datasheets/`
- a structured research set in `research/`
- generated vendor-derived calibration tables in `calibration/`
- generated quadratic fit reports in `calibration/`
- a clarified project framing that separates:
  - the actual optical sensing elements: `TST-10` and `TSW-10`
  - the conditioning / interface reference path: `SEN0189`
  - the host firmware side: MCU or SBC

The repo does not yet have a validated electrical interface, a bench-calibrated sensor
model, or a working firmware path on a real target.

## Guiding Principles

- Treat `TST-10` and `TSW-10` as the primary sensor targets.
- Treat `SEN0189` as a useful reference path for interface and bring-up, not as the
  final sensor identity.
- Keep vendor-derived calibration clearly separated from empirical calibration.
- Prefer simple, inspectable firmware and documentation over premature optimization.
- Preserve the architectural split between sensing element, conditioning electronics,
  and host-side software.
- Document conflicts and uncertainties instead of hiding them.

## Main Workstreams

### 1. Electrical Interface Definition

Goal: determine the practical analog interface between the Amphenol sensing heads and a
host ADC.

Tasks:

- extract or reconstruct the likely electrical behavior of `TST-10` and `TSW-10`
  from datasheets and bench observation
- decide whether initial testing will use:
  - direct sensor bring-up
  - an adapted conditioning path inspired by `SEN0189`
  - a temporary custom interface board or breadboard circuit
- define power, grounding, reference-voltage, and output-loading assumptions
- identify the minimum viable analog front-end needed for proof-of-life testing

Exit criteria:

- one explicit interface path is chosen
- wiring, supply, and expected output range are written down
- the team knows what the host ADC is expected to measure

### 2. Host and Firmware Bring-Up

Goal: build a small, portable acquisition path that can read, filter, and report sensor
output without locking the repo to one platform too early.

Tasks:

- choose the first concrete host target for proof-of-life work
- implement raw sampling and logging
- add simple filtering / averaging
- separate calibration mapping from raw acquisition logic
- make it easy to inspect voltage, raw counts, and derived values independently

Exit criteria:

- raw sensor output can be sampled repeatably
- filtered and unfiltered signals can be compared
- the code structure can support later calibration changes without large rewrites

### 3. Calibration Model Development

Goal: move from vendor-derived scaffolding toward a real project-specific calibration
workflow.

Tasks:

- keep the current vendor-derived calibration files as the baseline development model
- compare real bench measurements against the generated CSVs and fit reports
- decide whether the next calibration representation should remain polynomial or move
  to a table / interpolation-first model
- define how calibration data will be versioned and regenerated

Exit criteria:

- the repo has a documented path from vendor-derived model to empirical model
- at least one sensor path has measured data that can be compared to the current curves
- calibration regeneration remains scripted and repeatable

### 4. Validation Strategy

Goal: define what counts as success before trying to claim quantitative performance.

Tasks:

- decide whether the near-term target is:
  - proof-of-life sensing
  - relative turbidity trend tracking
  - quantitative comparison against a reference instrument
- identify realistic reference fluids, standards, or comparison instruments
- document what can and cannot be claimed at each maturity stage
- keep `ISO 7027` and `EPA 180.1` as future validation references rather than current
  compliance claims

Exit criteria:

- success criteria are written down for the next milestone
- the repo distinguishes exploratory measurements from validated measurements

### 5. Documentation and Repo Structure

Goal: keep the project legible as it grows.

Tasks:

- treat `planning/context.md` as the stable orientation brief
- treat `planning/roadmap.md` as the active sequencing document
- keep `research/` focused on factual source-backed notes
- use `calibration/` only for generated artifacts and calibration-related scripts/docs
- later, align `README.md` with the clearer sensor-versus-conditioning framing

Exit criteria:

- new contributors can understand the repo layout in one pass
- planning, research, and generated artifacts do not get mixed together

## Recommended Sequence

### Phase 1: Freeze the Conceptual Model

- keep the sensor / board / host split explicit
- confirm the first target sensor to bring up physically
- confirm the first host platform for proof-of-life

### Phase 2: Build the First Electrical Path

- wire one sensor through the chosen interface path
- measure raw output under controlled simple conditions
- capture enough data to confirm the signal is real and interpretable

### Phase 3: Build the First Firmware Slice

- sample raw data
- log data visibly
- add simple filtering
- keep calibration application separate from acquisition

### Phase 4: Compare Against the Current Calibration Scaffolding

- compare observed voltages to vendor-derived expected curves
- note where the current model is useful and where it diverges
- decide what extra measurement points are needed

### Phase 5: Start Empirical Calibration

- gather controlled reference points
- regenerate the calibration model from measured data
- retain the older vendor-derived artifacts for comparison history

### Phase 6: Decide Whether to Pursue Standards-Aware Validation

- only after the sensing chain is stable
- only after the project knows whether it wants qualitative, relative, or quantitative
  turbidity claims

## Immediate Next Steps

1. Choose the first physical bring-up target: `TST-10` or `TSW-10`.
2. Choose the first host platform for acquisition.
3. Write down the first intended electrical interface path in a dedicated planning note.
4. Define what proof-of-life success looks like for the first bench session.
5. Keep using the current calibration artifacts only as development scaffolding until
   bench data exists.

## Current Risks

- assuming the vendor-derived curves are more authoritative than they are
- allowing `SEN0189` convenience to silently define the final Amphenol interface
- mixing standards language into the project before the bench process exists
- coupling firmware too tightly to one calibration representation too early
- making electrical decisions before the expected signal range is clearly documented
