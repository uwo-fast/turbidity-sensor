# Changelog

All notable changes to this project are documented in this file.

The format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2026-11-25

### Added

- `seals` and `riser_l` in `bayonet.scad`: the foot's two o-rings (the riser's 4 × 1.5 in the bore,
  the 23 × 1.5 face seal under the flange) and a length of the riser, drawn in the case and
  assembly. Both default off, so the drawing is unchanged. The section views draw both, with
  60 mm of riser, and `just check-sampler-case` checks that the riser passes its bore, that its
  o-ring sits in its gland, and that the face seal fits its groove (#75).

### Changed

- `CITATION.cff` names the project `turbidity-sensor`, not the library's `turbidity`, and adds an
  abstract, keywords and the repository, which Zenodo reads for the archived release's record.
- `section` cuts each part on its own, inside its colour, so its cut face is drawn in that colour;
  a part that colours itself (the screws, the actuator) keeps its colours and gets one for its cut.
  The section views render in full with Manifold, which keeps those colours; a preview drew every
  cut face in one.

### Fixed

- `just render` gives a row whose flags ask for `--render` a full render. It passed `--preview`
  ahead of every row's flags, and OpenSCAD then previews whatever follows.
- The sampler case draws the four nuts that hold the actuator to its face as M3 square nuts
  (DIN 562), as they are built, not hex nuts. Only the drawing changes: the printed base and top
  are the same.

## [0.5.0] - 2026-11-24

### Added

- `just render`, which draws each row of `hardware/sampler-case/views.tsv` to
  `build/figures/<name>.png`, cropped to the model; `just render 'case_*'` draws a subset. A row
  is a name, a camera rotation and `-D` flags over `bayonet.scad`. Eight views: the two prints,
  the case exploded and in section, and the assembly whole, exploded and in section.
  `bayonet.scad` gains `explode`, `section` and `piece = "case"` (the case without the
  actuator), and `sampler_bought()` takes `explode` and `actuator`. The prints are unchanged;
  the pictures carry no labels yet, and the o-rings and riser are not in the model.

### Changed

- **Breaking:** `turbidity_solve_profile_3point()` accepted points that cannot constrain the fit.
  It now returns `TURBIDITY_STATUS_INVALID_ARGUMENT` unless the three points, in any order, fall
  in voltage as NTU rises and span at least a tenth of the sensor's range (400 NTU for a TST-10,
  200 for a TSW-10). `turbidity_calibrate` says what the points must do, and refuses a fit that
  lands on a `trim_t` bound, where the vendor model cannot represent the points.
- syringe-actuator is pinned at v0.1.2, which lists `get(L, "throw")` among its public names
  for `sampler_stroke_ml()`. The sampler case's base and top are unchanged, and one `5ml-gnr2`
  stroke is still 5.17 mL.
- The rig's verdicts are described by what they measure: `no_motion` means the burst's signal
  never swung by `min_swing` (100 counts), so nothing passed the beam, from a stalled crank, a
  syringe off its fitting or a riser out of the culture; `no_sample` means the signal moved but
  never held steady at culture. `rig/pi/README.md`, the results page's `no_motion` message and
  the config comments say so. The picking is unchanged.
- Column run 1 is re-picked with the corrected picker: 5, 29 and 195 readings move in
  `picked-algae-run-1.csv`, `-1b` and `-1c`, and 6 run-1c setup-day bursts go from `thin` to
  `ok`; no growth-test burst changes verdict. `growth_test` and `agreement` are redrawn, and the
  fit becomes OD = 4.004 (-ln(c/854.1))^0.629: fitted reads -4.5 to +6.6 %, the five later reads
  +0.1 to +2.6 %.

### Fixed

- The run 1 notes gave the column as 7 L, with 5 L and 8 L photo estimates and a 3.5 L volume
  inferred from a Cary drop. They now give U3 as measured on 2026-11-22 (670 mm overall, a
  17 mm flange at each end, a 115 mm tube, about 4 L at most with the pocket lid in) and the
  held volume as about 4.0 L (511 mm of culture, 4,013 mL). The run-2 plan says "sampler case"
  and starts run 2 at 4.0 L: 200 mL of inoculum into 3.8 L of BG-11, volumes still to be confirmed.
- `tools/generate_vendor_calibration.py` wrote the calibration CSVs with CRLF line endings while
  `.gitattributes` stores them as LF, so every `just regen` left both files modified; it now
  writes LF.
- The rig's picker dropped every steady stretch whose median sat more than 15 counts
  (`sample_band`) from the median of the burst's culture rows, discarding real draws. The
  reading is now the median of every steady stretch above air, and `sample_std` their spread.
  `sample_band` is gone from `rig.toml`; a config that still sets it runs unchanged.
- The run-2 plan said head A2 stepped about 8-14 counts at each lamp switch, the range run 1's
  notes record for the switches up to 11-11; over all 14 switches of run 1's growth test it is
  9.9-17.4 counts, 1.3-2.8 % of the reading, growing as the culture grew denser.
- `CMakeLists.txt`, `library.json` and `CITATION.cff` said 0.2.0 at every tag, so the CMake package
  and the PlatformIO library of v0.1.0 to v0.4.0 all reported 0.2.0. They now say 0.4.0, the
  latest release, and `just check` (`scripts/check-version.sh`) fails unless the three agree with
  each other, with the newest release in this changelog and, on a tag, with the tag.
  `CONTRIBUTING.md` gives the release steps.

## [0.4.0] - 2026-11-22

### Added

- The run 1 notes record the sampler's stainless riser as 22.5 cm long, 4 mm outside and 3 mm
  bore, where they had only a position read from the photos.
- Line figures from the sampler case for a vessel to cut and check its line:
  `sampler_sleeve_l()` (16 mm), `sampler_syringe()`, `sampler_stroke_ml()` (5.17 mL for
  `5ml-gnr2`) and `sampler_line_ml(riser_l)`, the volume from the riser's open end up past the
  heads' top. The sampler case README tables them with `sampler_clear_tube_cut()`.

### Fixed

- A `capture_serial.py` capture that failed before its CSV header emptied an existing output
  file, as happened to `47_tube_clear_8.csv` on 2026-10-29. It now writes to `<output>.partial`
  and renames it onto the output when the header arrives.
- `capture_serial.py` did not reset the board when DTR was already up, so the header could be
  missed. It now pulses DTR when it opens the port, skipping ports with no modem lines. The
  reset is still to be checked on a Nano.
- The sampler case README said syringes other than `5ml-gnr2` render but are unverified. Only
  the other 5 mL layouts (`5ml-gnr1`, `5ml-gnr1-ga25`, `5ml-gnr2-ga25`) do; the 1, 3, 10, 20 and
  30 mL stop at syringe-actuator's assert that their `nozzle_l` is not measured yet.

## [0.3.0] - 2026-11-22

### Changed

- **Breaking:** The three enclosures are named stock housing, tube case and sampler case, defined
  in `docs/hardware.md`. `hardware/case/` is now `hardware/tube-case/` with `tube_case.scad`,
  and `hardware/sampler/` is now `hardware/sampler-case/` with `sampler_case.scad`; `just case`
  is now `just tube-case`, and `just check-sampler` is `just check-sampler-case`. Module and
  function names and the geometry are unchanged; the sampler case's echo reads "sampler: case".

## [0.2.0] - 2026-11-22

### Added

- `hardware/sampler/bayonet.scad`, which stands the housing on the bayonet pin from
  bayonet-port-scad v0.1.0: the file to print from, and the pattern for another vessel's foot.
  The fit test now runs on this foot, so the fits are checked against figures read from the port
  library. `scadman.toml` pins bayonet-port-scad v0.1.0.

### Changed

- syringe-actuator is pinned at v0.1.1, which adds a tab on the actuator lid's front end and an
  optional `front_plate` part. The sampler housing's base and top are unchanged.
- `LICENSING.md` granted the sampler housing both `GPL-3.0-or-later` and `CERN-OHL-S-2.0`, but
  it includes NopSCADlib and bayonet-port-scad and uses syringe-actuator, all GPL-3.0-or-later.
  `hardware/sampler/` and the geometry generated from it are now `GPL-3.0-or-later` alone; the
  case, probe and flange keep both licences.

## [0.1.0] - 2026-11-22

### Added

- The project is licensed under the GNU General Public License v3 (`LICENSE`).
- Voltage-vs-NTU calibration tables for the Amphenol TST-10 and TSW-10 sensors
  (`calibration/Voltage_vs_NTU_TST-10.csv`, `calibration/Voltage_vs_NTU_TSW-10.csv`) and
  `calibration/plot.py`, which plots both curves of each sensor with quadratic fits.
- The Amphenol TST-10 and TSW-10 datasheets, ISO 7027 and the BSI turbidity standard under
  `datasheets/`, and a README listing the two parts with DigiKey links and reference projects
  and papers.
- The EPA Method 180.1 (1993) nephelometry document in `datasheets/`, Amphenol product links
  for both parts, and a README reference list split into academic papers and implementation
  references.
- Points digitized with WebPlotDigitizer from the datasheet calibration curves
  (`tst10-high.csv`, `tst10-low.csv`, `tsw10-high.csv`, `tsw10-low.csv`), with the datasheet
  plot images they came from, and `CONTEXT.md` stating the project's purpose and goals.
- `calibration/generate_calibration_csvs.py`, which turns the raw digitized `voltage, NTU`
  point clouds into `tst10-calibration.csv` and `tsw10-calibration.csv`, with columns `NTU`,
  `Voltage (High)` and `Voltage (Low)`; `plot.py` now plots these files.
- `plot.py` writes a quadratic fit report per sensor (`tst10-fit.txt`, `tsw10-fit.txt`) with
  the equation, a copy/paste form, the coefficients, R^2 and the valid NTU range, and shows R^2
  in the plot legend. The generated reports give R^2 from 0.995 to 0.999 over 0-4000 NTU
  (TST-10) and 0-2000 NTU (TSW-10).
- README links to the DFRobot SEN0189 board and wiki, the conditioning board on hand, which
  carries a TSW-10/TST-10 sensor.
- Research notes under `research/`: Amphenol sensor facts, the DFRobot SEN0189, turbidity
  standards and units (ISO, EPA, USGS), hardware integration, and secondary references.
- A roadmap in `planning/roadmap.md`; `CONTEXT.md` moves to `planning/context.md`.
- A portable C99 turbidity library (`include/turbidity/turbidity.h`, `src/turbidity.c`) for the
  TSW-10 and TST-10: a vendor-curve model with a per-unit profile (`trim_t`, `gain`,
  `offset_mv`), a moving-average filter (window up to 64 samples, default 8), range status
  (in range, clamped low/high, invalid) and a 3-point profile solve. It builds with CMake, with
  unit tests under `ctest`, and as a PlatformIO library through `library.json`.
- Host tools: `turbidity_calibrate` solves a profile from three `--point NTU,MV` pairs, and
  `turbidity_stream` replays a `timestamp_ms,raw_mv` CSV from stdin through the model and
  prints the filtered value, NTU estimate and range status per row.
- An Arduino Uno PlatformIO example that reads the sensor on `A0` every 100 ms and logs CSV at
  115200 baud, configured through build flags (sensor, trim, gain, offset, filter window).
- `tools/generate_vendor_calibration.py`, one pipeline that regenerates the calibration CSVs,
  fit reports, the plot images (when matplotlib is installed) and the runtime model header
  `src/turbidity_model_data.generated.h` from the vendor data. The CMake option
  `TURBIDITY_REGENERATE_CALIBRATION=ON` runs it during the build.
- CMake install of a `turbidity` package that downstream projects use through
  `find_package(turbidity REQUIRED CONFIG)` and `turbidity::turbidity`, with `BUILD_TESTS`,
  `BUILD_TOOLS` and `BUILD_EXAMPLES` options and a package smoke test.
- CI that builds and tests the project, fails when the generated calibration artifacts are out
  of date, and compiles the Arduino example.
- A `justfile` with `setup`, `build`, `test`, `check`, `fmt`, `fmt-check`, `lint`, `regen`,
  `arduino` and `clean` recipes; `check` runs `fmt-check` (clang-format) and `lint` (clang-tidy)
  without changing the tree, and CI uses clang-format and clang-tidy 18.1.8. Also adds
  `CONTRIBUTING.md`.
- The CMake option `TURBIDITY_WARNINGS_AS_ERRORS`, with one warning flag list for all targets
  that adds `-Wshadow` and `-Wconversion`.
- Bench logging in the Arduino example: `adc_counts` (mean of 16 reads) as the primary
  measurement, a bandgap-derived `vcc_mv` supply drift indicator on the ATmega328P, and, with
  `TURBIDITY_EMITTER_PIN` set, `dark_adc_counts` read with the emitter off to measure ambient
  light. New PlatformIO environments `nano`, `nano_oldbootloader` and `uno_switched_emitter`.
- `tools/capture_serial.py`, which records the board's serial log with only the Python standard
  library, starting at the CSV header, dropping a truncated last line and stopping on a board
  reset, and `tools/summarize_capture.py`, which reports count, mean, std, min and max per
  signal column. Both run as `just capture` and `just summarize`; `just upload` flashes a board.
- Bench procedure `docs/bench/session-1.md`: wiring checks, baselines, a kaolin dilution series
  with a constant Tween 20 diluent, pass criteria and a notes template.
- `docs/hardware.md`, covering the DFRobot SEN0189 adapter circuit (the datasheet test circuit
  with a 4.7 kohm load and 500 ohm emitter resistor, followed by a unity-gain LMV358 buffer), a
  check that any adapter behaves as a unity-gain buffer, wiring a bare probe instead, and the
  `RV` trimmer inside every probe housing, which must not be adjusted until characterized.
- A parametric printed flow-through case for the bare SEN0189 probe board
  (`hardware/case/turbidity_case.scad`) with print-ready `base.stl` and `lid.stl`, a README and
  a `just case` recipe that re-exports the STLs. A 5/16 in clear tube passes through the
  optical slot; all dimensions are Customizer parameters, and `assert()` checks stop the
  export when the tube would not fit between the heads or a wall would be thinner than 0.8 mm.
  Not yet printed or tested wet.
- The case README records the clear tube's inside diameter: 1/4 in (6.35 mm), which holds
  0.032 mL per millimetre of tube.
- A probe board library, `hardware/probe/probe.scad`, shared by the TSW-10 and TST-10. It draws
  nothing: `probe(c)` is the board grown by `c` for cutting a pocket, `probe_outline()` its
  PCB, and `probe_bbox()`, `probe_optical_axis()`, `probe_gap()`, `probe_heads()`,
  `probe_pcb()`, `probe_connector()` and `probe_trimmer()` give a housing the figures to size
  itself from. The flow-through case is now built on it, with the same base and lid geometry.
- `part = "none"` in `turbidity_case.scad`, which renders nothing, so another OpenSCAD project
  can `include` the case with overrides and use its modules, dimensions and the `probe_*()`
  functions. The case README documents the pattern with a tested example, lists FEP as a tube
  material, and notes that the adapter cannot switch the emitter (dark readings use an opaque
  rod) and that the vendor curves do not describe the tube's optical path.
- `examples/arduino-multichannel`, a logger that prints raw `adc_counts_*` for `A0`-`A3` plus
  `vcc_mv` each sample, with no model. `summarize_capture.py` reports every per-channel column
  and, with `--dark` and `--clear`, each head's transmittance and attenuation against its own
  references; it rejects a clear reference not above dark and warns when one is near full
  scale. `just upload` takes the example to flash, and CI compiles both examples.
- Session 1 bench data from 2026-10-24 to 2026-10-29 in `data/bench/<date>/`, with each day's
  captures and `notes.md`: head screening, references, two kaolin repeats in a beaker, and
  five-fill kaolin standards in the tube case. `tools/plot_series.py` (`just plot`) writes SVG
  plots of percent change and attenuation against concentration to `build/plots`.
- `docs/test-solutions.md`, giving the reasons and sources for the 0.01 % v/v Tween 20 diluent
  dose, which is a chosen value since no published dose for dilute kaolin suspensions was found.
- A printed flange (`hardware/tst-flange/flange.scad`, `flange.stl`) that sits on a beaker's rim
  and holds a TST-10 in its stock housing down into the liquid: 80 mm across, a 34 mm bore and
  four 4 mm holes on a 44 mm circle. `just case` exports it alongside the case.
- `tools/tube_raytrace.py`, a 2D ray trace of the case cross-section; it predicts 1.52x for
  water over air at emitter half-angles of 10-45 degrees, and +4.5 % for isopropanol over water.
- `docs/bench/session-1-results.md`, the session 1 write-up: head screening and spread, what
  `RV` does, the two beaker repeats, the tube case setup and five-fill standards, the conditions
  that moved the readings, and the limits. The same stock-housing head read -15.1 % at a
  nominal 4000 mg/L in a beaker and -79.1 % in the bottled standard, so the beaker series is
  treated as showing direction and within-run agreement, not response to a known concentration.
  Bench photos from 2026-10-28 go with it.
- The 2026-10-29 *Chlorella vulgaris* series in `data/bench/2026-10-29/`: three heads at 7 levels
  from `c0063` to `c4000`, five fills each, against supernatant references, with OD750 reads
  (`cary50_od750.md`) and a cell count (`cell_count.md`, 7.2 x 10^7 cells/mL at `c0500`). Every
  head responds across the whole range, and the two tube heads agree within 1.5 points at every
  level. Photos of the samples are in `photos/`.
- `plot_series.py` options `--x c0500=7.2e7 ...` to map each level to its own x value (a level
  with no value is an error), `--xlabel` to name the axis, and `--log-x` to space a doubling
  series evenly. Without `--x` the axis is still kaolin (mg/L).
- `CITATION.cff`.
- A Raspberry Pi logger in `rig/pi/` that runs the syringe actuator in bursts and logs a tube
  head through a Nano. `rig.py` runs the motor for `burst_s` every `period_s` through an
  Adafruit 2348 HAT, with a 1 s full-throttle kick at each start and then the running throttle
  (0.5 by default), and logs every Nano row at 50 Hz during a burst and at 1 Hz between bursts.
  It picks the culture reading from each burst's steady stretches above the air band and gives
  each burst a verdict: `ok`, `thin`, `no_sample`, `no_motion` or `aborted`.
  `pick_samples.py` repeats the picking on any saved raw file, and `view_server.py` serves a
  read-only summary page on 127.0.0.1 only; both run as systemd services. `tests/test_rig.py`
  and `tests/test_rig_view.py` run under `ctest`.
- Column run 1 in `data/bench/2026-11-05/`: `notes.md` covers the first motor runs, the setup
  days and the growth test from 11-08 10:20 to the stop on 11-16 19:55, with every Cary OD750
  read, the DI top-ups, lamp switches, the 11-09 power and air outage, the 11-15 sampler stall
  and its cause, and the 11-16 hand draws. `rig-data/` holds the gzipped raw logs, summaries,
  events and picks of every segment, with bench captures and photos. The procedures are in
  `docs/bench/sampler-waveform.md` and `docs/bench/column-trials.md`, and
  `docs/bench/algae-run-2-plan.md` plans run 2 on a BREAD DCMT slice.
- Three figures of column run 1 in `data/bench/2026-11-05/figures/`, with the standard-library
  scripts that draw them: `growth_test.png` (the A2 reading per 15-min burst above the Cary
  OD750 reads), `agreement.png` (each Cary read against the sensor, with the fit
  OD = 3.989 x (-ln(counts / 854.1))^0.628, residuals -4.6 % to +6.4 % on the 7 fitted reads
  and -0.1 % to +2.4 % on the 5 later ones) and `burst.png` (one normal 50 Hz burst beside the
  first burst after the stall).
- A snapshot of the 10-29 *Chlorella* results spreadsheet,
  `data/bench/2026-10-29/algae_2026-10-29_results_2026-11-21.xlsx`, carrying the corrected Cary
  labels. The Markdown files stay the record; the sheet is not kept in sync.
- A snapshot of the column run 1 results workbook,
  `data/bench/2026-11-05/algae_run1_column_results_2026-11-21.xlsx`: every Cary read with its
  dilution, each Cary sample against the sensor and the fit, every burst with its verdict and
  fitted OD, the events and the 11-16 hand draws. The notes and `rig-data/` stay the record.
- The sampler housing, the flow cell round the bare board that the syringe actuator bolts onto,
  moved from open-source-bioreactor as `hardware/sampler/sampler.scad`. The vessel's foot is
  passed in as the child of `sampler_base()`, `sampler_placed()` or `sampler_print("base")`,
  and the housing checks its fits against four `foot_*` figures, which default to the
  bioreactor's bayonet pin. A `syringe` parameter defaults to `5ml-gnr2`, the only size
  fit-tested. `just check-sampler` runs the fit test `tests/sampler/fit.scad`, also in CI, and
  `just scad-setup` installs the libraries `scadman.toml` pins (syringe-actuator v0.1.0 and
  NopSCADlib v21.41.1).

### Changed

- The digitized vendor points and datasheet plot images move to `calibration/vendor-data/`.
  `plot.py` now saves `tst10-plot.png` and `tsw10-plot.png` instead of opening a window, and
  runs from any directory.
- `CONTEXT.md` describes the project in detail: the TST-10 and TSW-10 as the sensing elements,
  the SEN0189 as the on-hand interface board, a sensor comparison table, the current
  calibration artifacts and the technical direction.
- The repository layout changes: calibration data moves to `data/calibration/`, the
  datasheets, planning and research notes to `docs/archive/`, the Arduino and POSIX programs
  to `examples/`, and `turbidity_calibrate` to `tools/`.
- **Breaking:** The library is stateless. Every function returns a `turbidity_status` code,
  `turbidity_estimate_ntu_from_mv` replaces the context and `turbidity_process_sample`, the
  profile no longer carries `filter_window`, `TURBIDITY_RANGE_INVALID` is gone, and
  `turbidity_sensor_max_ntu` returns its value through an output argument. Filtering moves to
  the examples (`examples/common/moving_average.h`).
- `turbidity_calibrate` prints the solved profile as one line of JSON, and the stream and
  Arduino examples add an `equivalent_mv` column to their CSV output.
- The project is named `turbidity`, version 0.2.0 in CMake and `library.json`, under
  `GPL-3.0-only`, and the README documents build, test, install, quick start and the
  calibration pipeline.
- `.gitattributes` sets line endings per file type: LF for source, scripts and docs, CRLF for
  `.bat`, `.cmd` and `.ps1`.
- `turbidity_stream` reads columns by header name: `timestamp_ms` and `raw_mv` are required in
  any order and other named columns are ignored, so the Arduino example's serial log replays
  directly.
- The bench procedure uses the DFRobot SEN0189 adapter as the default sensor interface; its
  analog output is the probe voltage, so the vendor curves still apply.
- The case has been printed and fitted to a real board: the snug tube now holds base and lid
  together, so tape or a zip tie is no longer needed unless `tube_fit` is loosened. The README
  gives the print settings the fit is proven on (Prusa MK3, PETG, 3 perimeters, 30 % gyroid
  infill, 0.07 mm adaptive layers). Not yet tested wet.
- **Breaking:** The probe board's figures leave the case's Customizer; remeasuring a board now
  means editing `hardware/probe/probe.scad`.
- `docs/hardware.md` lists the three setups (stock TSW-10 and TST-10 housings and the printed
  tube case with its 6.35 mm water column), which of them the vendor curves describe, and the
  head inventory. Session 1 covers both setups with up to four heads, per-head dark and
  clear-water references, a crosstalk check, pump or syringe sample handling for the tube, and
  head agreement as a recorded finding.
- The README states the project's goal, characterizing the TSW-10 and TST-10 and building a
  reproducible measurement approach, and lists the current features.
- The session 1 diluent is 0.01 % v/v Tween 20, made as two 1-in-100 dilutions, replacing "one
  drop per litre"; a new `03a_clear_di` capture checks plain DI water; and each kaolin repeat runs
  in one beaker at constant volume from a 10 g/L stock, replacing eight separate dilutions.
- The docs now say what `RV` does instead of "don't touch RV": turning it counter-clockwise
  dims a head, and a head near the ADC ceiling should be set to about 800-880 counts in clear
  water after marking and photographing the trimmer. A new "Optics and setup" section in the
  case README explains that the water-filled tube concentrates the beam (1.87x over air) and
  gives the fix: `RV` fully counter-clockwise plus a resistor from the probe output to GND
  chosen for 850-880 counts in clear water (15 kohm and 6.8 kohm on the two boards tested).
- The session 1 procedure takes in the bench lessons: metal blocks for dark, an opaque cover
  over the whole beaker, stock shaken before every draw and sized at 450 mL, a series up to
  4000 mg/L, stirring and bubble checks for the stock heads, tube heads set up first and run as
  separate standards with five fills each, and retakes under a `b` suffix with no name reused.
- `plot_series.py` plots run the change axis from 0 to -100 %, use 10 px markers with a
  distinct shape per series, capped +/-1 SD error bars, round-valued ticks with the power of
  ten in the axis label, and a legend keyed by line and marker.
- The software moves from `GPL-3.0-only` to `GPL-3.0-or-later`; the OpenSCAD
  sources are also under `CERN-OHL-S-2.0`, the STLs under `CERN-OHL-S-2.0` and `data/` under
  `CC-BY-4.0`. `LICENSING.md` says what applies where and lists the third-party material the
  repository does not own, with the licence texts in `LICENSES/` and badges in the README.
- The README leads with the sensor and its sampler instead of the vendor-curve library, and is
  titled with the repository's name. It states the bench repeatability (0.05-0.11 %), run 1's
  fit result and what is not done yet. The library's install, quick start, CSV schema,
  calibration pipeline and Arduino example sections move unchanged to `docs/library.md`, which
  now opens by saying the vendor curves describe the stock housing, not the tube case.

### Fixed

- The README calibration example now shows the output the tool actually produces, and notes
  that the 3-point RMSE and maximum error are zero unless `trim_t` is pinned at a bound.
- The wiring documentation said the 4.7 kohm output and 470 ohm emitter resistors were inside
  the sensor and pin 3 was ground; they are external, pin 3 is the emitter diode cathode, and
  the README now gives the datasheet test circuit.
- `turbidity_stream` accepted rows its README called invalid: empty fields were collapsed
  (`100,,3350` parsed as two columns), negative timestamps wrapped, timestamps above 2^32 were
  truncated, lines over 255 characters split into a bogus row, and CRLF input (as Arduino
  `Serial.println` sends) was rejected. Every row must now match the header's field count with
  no empty fields or whitespace, timestamps are 64-bit with overflow checks, LF and CRLF are
  accepted, the final newline is optional, and over-long lines are rejected before any output.
- The Arduino example divided AVR ADC readings by 1023; it now uses 1024.
- The Arduino example linked the library with `file://`, which copied the whole repository,
  `.git` included, into the PlatformIO cache; it now uses `symlink://`.
- The probe's bracket (4.5) and heads (7.5) were measured from the PCB's top face but drawn from
  its underside, so both stood 1.5 too low and a housing taking the board heads-first bottomed
  out before the PCB seated. They are now `bracket_h` and `head_h` over the top face; the case
  lid's head and bracket pockets are 1.5 deeper and `lid.stl` is re-exported.
- A board did not seat in a housing printed to the old probe figures. The PCB is now 1.6 thick
  (was 1.5), raising the bracket and head tops to 6.1 and 9.1, and the connector's back face
  `conn_y1` moves from -9.4 to -8.0. `base.stl` and `lid.stl` are re-exported.
- The probe's optical axis was 11.4, where the first case put its tube, not a measurement; it is
  now 10.8, where the lens windows are centred, and the case's tube bore moves 0.6 toward the
  connector in both parts.
- The case README and 2026-10-28 notes gave the stock housing's water-over-air ratio as
  1.26-1.27x, but the 1.28 came from a head in the case; they now compare the tube's 1.87x with
  the one housed board (1.26). The notes' ray-trace figure is corrected from 1.51x to 1.52x.
- The case's `RV` access-hole comment still said not to adjust `RV`; it now says to mark its
  position and take air, clear and dark references first, and `docs/hardware.md` puts the same
  step first.
- Head A1 was logged as a new head of unrecorded model; A0, A1 and A2 are all DFRobot TST-10s.
  `docs/hardware.md` no longer says heads of one model from different vendors are the same part:
  the DFRobot boards carry a 150 ohm series resistor that the others do not, shown in a photo.
- The 2026-10-29 OD750 notes had rounded placeholders; they now give the direct reads (`c0125`
  0.2747, `c0500` 0.9813) and the master stock OD, 2.22, from a fit through the in-cuvette
  series, with the other levels scaled by dilution.
- The 2026-10-29 Cary labels were wrong: the series' stock was `c0500`, not `c1000`, and the two
  direct reads were `c0063` and `c0250`, not `c0125` and `c0500`. The values are unchanged, so
  `c1000` is about OD 4.45, not 2.22, and the levels run from 0.278 (`c0063`) to 17.8
  (`c4000`). Re-reads of the bottles on 2026-11-07 and 2026-11-09 are added.

### Removed

- `calibration/Voltage_vs_NTU_TST-10.csv` and `calibration/Voltage_vs_NTU_TSW-10.csv`, replaced
  by the generated `tst10-calibration.csv` and `tsw10-calibration.csv`.
- `calibration/generate_calibration_csvs.py` and `calibration/plot.py`.
- The ISO 7027-1:2016 and BS EN ISO 7027-1:2016 PDFs, whose terms forbid reposting; a README in
  `docs/archive/datasheets/` cites them by number and title instead.
