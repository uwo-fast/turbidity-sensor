# Changelog

All notable changes to this project are documented in this file.

The format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `just render` draws each view in `hardware/sampler-case/views.tsv` to
  `build/figures/<name>.png`, or only those matching a filter: the two prints, the case exploded
  and in section, and the assembly whole, exploded and in section. `bayonet.scad` gains
  `explode`, `section` and `piece = "case"` for the case without the actuator, and
  `sampler_bought()` takes `explode` and `actuator`

### Changed

- **Breaking:** `turbidity_solve_profile_3point()` returns `TURBIDITY_STATUS_INVALID_ARGUMENT`
  unless the three points, in any order, fall in voltage as NTU rises and span at least a tenth
  of the sensor's range (400 NTU for a TST-10, 200 for a TSW-10); it used to return a profile
  that the points could not constrain. `turbidity_calibrate` says what the points must do, and
  refuses a fit that lands on a `trim_t` bound
- syringe-actuator is pinned at v0.1.2, and `sampler_stroke_ml()` reads the layout's `throw` from
  its public interface; the sampler case's prints are unchanged and one 5ml-gnr2 stroke is still
  5.17 mL
- The logger's README and results page say what the `no_motion` and `no_sample` verdicts measure:
  `no_motion` is a burst in which nothing passed the beam, from the crank, the syringe's fitting or
  the riser's inlet; `no_sample` a burst whose signal moved but never held steady at culture

### Fixed

- The logger's picker dropped every steady stretch more than `sample_band` (15 counts) from the
  burst's own median; a burst's reading is now the median of every steady stretch above air. A
  `rig.toml` that still sets `sample_band` runs unchanged. Run 1 is re-picked with it and its
  figures redrawn: the fit becomes OD = 4.004 × (−ln(counts / 854.1))^0.629, and the five later
  reads come within +0.1 to +2.6 %
- `just regen` writes the calibration CSVs with LF line endings, so it no longer leaves them
  modified
- Run 1's notes give the column as measured: 670 mm overall and about 4.0 L held, in place of
  the 7 L mark and the 3.5, 5 and 8 L estimates; the run 2 plan starts at 4.0 L
- The run 2 plan gives run 1's lamp steps over all 14 switches of its growth test: 9.9 to 17.4
  counts, 1.3 to 2.8 % of the reading

## [0.4.0] - 2026-11-22

### Added

- What a vessel needs to cut and check the sampler's line, from the sampler case:
  `sampler_sleeve_l()`, `sampler_syringe()`, `sampler_stroke_ml()` (one stroke's volume, 5.17 mL
  for 5ml-gnr2) and `sampler_line_ml(riser_l)`, the line's volume from a riser's open end up past
  the heads; `sampler_clear_tube_cut()` gives the clear tube's cut as before
- Run 1's riser length in its notes: 22.5 cm, 4 mm outside and 3 mm bore

### Fixed

- The sampler case offered every syringe layout; it builds only for the 5 mL layouts, and says so.
  The 1, 3, 10, 20 and 30 mL stop at syringe-actuator's assert that their `nozzle_l` is not
  measured yet
- `capture_serial.py` emptied its output when a capture failed before the CSV header; it now
  writes to `<output>.partial` and keeps an existing file until the header arrives
- `capture_serial.py` resets the board on every capture, so it prints its header even when DTR was
  already up; a port with no modem lines skips the reset

## [0.3.0] - 2026-11-22

### Changed

- The board's three enclosures are named stock housing, tube case and sampler case, defined in
  `docs/hardware.md`. No geometry changed: the sampler case's prints are byte-identical to 0.2.0's
- **Breaking:** `hardware/case/` is now `hardware/tube-case/`, and `turbidity_case.scad` is
  `tube_case.scad`; `hardware/sampler/` is now `hardware/sampler-case/`, and `sampler.scad` is
  `sampler_case.scad`. `just case` is now `just tube-case`, and `just check-sampler` is
  `just check-sampler-case`. Module and function names are unchanged

## [0.2.0] - 2026-11-22

### Added

- `hardware/sampler/bayonet.scad`, the file to print the sampler housing from: it stands the housing
  on the bayonet pin from bayonet-port-scad v0.1.0, and is the pattern for another vessel's foot.
  The fit test runs on this foot, so the housing's fits are checked against the port library's
  figures

### Changed

- syringe-actuator is pinned at v0.1.1; the sampler housing's base and top are unchanged
- The sampler housing, and the geometry generated from it, is licensed GPL-3.0-or-later only: it
  includes GPL-3.0-or-later libraries, so the CERN-OHL-S-2.0 grant over it did not hold. The tube
  case, probe library and flange keep both licences

## [0.1.0] - 2026-11-22

### Added

- A portable, stateless C library (`include/`, `src/`) that models a TSW-10 or TST-10 head from
  the manufacturer's curves and estimates turbidity from a reading, with a per-unit trim, gain and
  offset. It installs as a CMake package (`turbidity::turbidity`) and is a PlatformIO library
- `turbidity_calibrate`, which solves a unit's trim, gain and offset from three `NTU,mV` reference
  points and prints them as JSON
- `turbidity_stream`, which replays a logged CSV through the model. It reads columns by header
  name, so the Arduino example's log replays as-is, and rejects any malformed row
- The vendor calibration: the datasheet curves digitised in `data/calibration/vendor-data/`, and a
  generator (`just regen`) that writes the calibration tables, fit reports, plots and the
  library's model header from them
- An Arduino example for the Uno and Nano that logs the mean of 16 ADC reads, a supply estimate
  from the bandgap, the model's estimate and, on a switched emitter, a dark reading
- A multichannel Arduino logger for up to four heads on `A0`–`A3`, with no model
- `tools/capture_serial.py` (`just capture`), which records a board's serial log to CSV, and
  `tools/summarize_capture.py` (`just summarize`), which reports each column's statistics and,
  with `--dark` and `--clear`, each head's transmittance and attenuation against its own references
- `tools/plot_series.py` (`just plot`), SVG plots of percent change and attenuation against
  concentration or any x value (`--x`, `--xlabel`, `--log-x`), and `tools/tube_raytrace.py`, a 2D
  ray trace of the tube case's cross-section
- The probe board library, `hardware/probe/probe.scad`: the board's measured outline, heights and
  optical axis, through `probe()` and the `probe_*()` functions, from which any housing sizes itself
- The tube case, `hardware/case/`: a printed flow-through case round the bare board and a 5/16 in
  clear tube, with base and lid STLs, Customizer parameters checked by asserts, and `part = "none"`
  for including it in another project. Printed and fitted on a Prusa MK3 in PETG
- The sampler housing, `hardware/sampler/`: the flow cell round the board that the syringe
  actuator bolts onto, standing on a vessel's foot passed in as its child, with a fit test
  (`just check-sampler`); `just scad-setup` installs the OpenSCAD libraries scadman pins:
  syringe-actuator v0.1.0 and NopSCADlib v21.41.1
- A printed flange that holds a TST-10 in its stock housing over a beaker's rim
- The sampler logger, `rig/pi/`: a Raspberry Pi runs the syringe actuator in timed bursts, logs a
  tube head through a Nano, and picks the culture's reading out of each burst with a verdict
  (`ok`, `thin`, `no_sample`, `no_motion`, `aborted`); `pick_samples.py` repeats the picking on a
  saved log, and a read-only summary page is served on 127.0.0.1. Both run as systemd services
- Wiring and setup (`docs/hardware.md`): the DFRobot SEN0189 adapter as the default interface, a
  check for other adapters, bare wiring, the three setups, the head inventory, and how to set a
  head's `RV` trimmer; the tube case's optics, and the load resistor that brings a head off the ADC
  ceiling in it
- The session 1 bench procedure and test solutions (`docs/bench/session-1.md`,
  `docs/test-solutions.md`): per-head dark and clear references, and a kaolin series in one beaker
  with 0.01 % v/v Tween 20 diluent
- Session 1 bench data, 2026-10-24 to 10-29, and its write-up (`docs/bench/session-1-results.md`):
  head screening, `RV`, two beaker repeats, and the tube case's five-fill kaolin standards
- The 2026-10-29 *Chlorella vulgaris* series on three heads, with OD750 reads, a cell count,
  photos and a results spreadsheet
- The record of column run 1 (`data/bench/2026-11-05/`): notes, raw logs, picks, figures with the
  scripts that draw them, and a results spreadsheet; the procedures for the motor runs and the
  column trial, and the plan for run 2
- Licensing: software GPL-3.0-or-later, hardware CERN-OHL-S-2.0 (the CAD under both) and data
  CC-BY-4.0, set out in `LICENSING.md`; a `CITATION.cff`
- `just build`, `test`, `check` (clang-format and clang-tidy 18.1.8), `fmt`, `regen`, `case`
  (the tube case's and flange's STLs), `arduino` and `upload`, and CI that also checks the
  generated calibration files have not drifted
