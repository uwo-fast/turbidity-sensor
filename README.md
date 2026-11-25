# turbidity-sensor

[![Software: GPL-3.0-or-later](https://img.shields.io/badge/Software-GPL--3.0--or--later-blue.svg)](LICENSES/GPL-3.0-or-later.txt)
[![Hardware: CERN-OHL-S-2.0](https://img.shields.io/badge/Hardware-CERN--OHL--S--2.0-orange.svg)](LICENSES/CERN-OHL-S-2.0.txt)

A low-cost turbidity sensor and its software, for monitoring culture density in a running
bioreactor. It uses the circuit board from a TST-10-type turbidity probe (as sold on DFRobot's
SEN0189 module), mounted in a 3D-printed case around a clear tube and read by an Arduino Nano. A
timed syringe actuator draws culture from the vessel through the tube for each reading.

<!-- The first print from run 1, grey, on a clear lid. Replace with photos of the black reprint from run 2: #48 -->
![The sampler on the lid of a column photobioreactor, with the syringe actuator body above and the sampler case below](docs/images/sampler.jpg)

## What's here

- **Sensor head:** the bare probe board in one of two printed cases around a clear tube.
  [`hardware/tube-case/`](hardware/tube-case/README.md) is a plain block for bench use or an inline
  liquid line. [`hardware/sampler-case/`](hardware/sampler-case/README.md) mounts on a vessel port
  below the syringe actuator. [`hardware/probe/`](hardware/probe/) holds the measured board outline
  that both cases are sized from. [`docs/hardware.md`](docs/hardware.md#setups) lists the
  enclosures and covers the wiring.
- **Readout:** [`examples/arduino-multichannel/`](examples/arduino-multichannel/) streams raw
  readings from up to four heads. [`tools/`](tools/) captures, summarises and plots them.
- **Sampler logger:** [`rig/pi/`](rig/pi/README.md) runs the syringe actuator
  ([uwo-fast/syringe-actuator](https://github.com/uwo-fast/syringe-actuator)) in timed bursts and
  extracts a culture reading from each burst. It does not need position sensing or valves.
- **C library:** a model of the head based on the manufacturer's curves, and a calibration tool.
  The model applies to a head in its stock housing, not in the tube case. See
  [`docs/library.md`](docs/library.md).
- **Data:** all bench sessions and runs, with their notes, in [`data/bench/`](data/bench/).

## Status

- **Bench:** two heads in tube cases measured kaolin standards from 250 to 4000 mg/L. Readings of
  clear water repeat within 0.05–0.11 % across refills of the tube, about one ADC count
  ([`docs/bench/session-1-results.md`](docs/bench/session-1-results.md)).
- **Run 1:** the sampler monitored a *Chlorella vulgaris* batch culture in a sparged column for
  about 7 days, with a benchtop spectrophotometer (OD750) as the reference.
  - A fit to the first four days predicted five later readings within 2.6 %. This excludes four
    readings that have recorded caveats. With those four included in the fit, the later readings
    are 4.5–10.1 % off.
  - Record: [`data/bench/2026-11-05/notes.md`](data/bench/2026-11-05/notes.md).
- **Not yet done:**
  - turbidity units, from a formazin series ([#23](https://github.com/uwo-fast/turbidity-sensor/issues/23));
  - picking readings on the Nano itself, for a BREAD DCMT slice ([run 2](docs/bench/algae-run-2-plan.md));
  - configuring the logger without editing it by hand ([#46](https://github.com/uwo-fast/turbidity-sensor/issues/46)).

## Repository map

- `include/`, `src/`: the C library; `src/` also holds the generated vendor-fit header
- `tools/`: the calibration CLI and generator, serial capture, summary and plot scripts, and the tube ray trace
- `examples/`: the Arduino examples and a host replay example
- `rig/pi/`: the sampler logger
- `hardware/`: the probe library, the tube case, the sampler case, and a flange that holds a TST-10 over a beaker
- `data/bench/`: bench sessions and runs
- `data/calibration/`: vendor digitisations and generated calibration
- `docs/`: wiring, test solutions, the library, bench procedures
- `docs/archive/`: earlier research and datasheets
- `tests/`: unit, CLI-contract, package smoke and logger tests

## Development

Tasks run through [`just`](https://github.com/casey/just); `just --list` shows them all.

```sh
just build    # configure and compile (warnings are errors)
just test     # build and run the test suite
just check    # clang-format check + clang-tidy (CI-equivalent)
just arduino  # compile the Arduino examples for every board
just capture  # record a board's serial log to CSV
```

`fmt`, `check` and CI use clang-format and clang-tidy 18.1.8.

Without `just`:

```sh
cmake -S . -B build -DBUILD_TESTS=ON -DBUILD_TOOLS=ON -DBUILD_EXAMPLES=ON
cmake --build build
ctest --test-dir build --output-on-failure
```

## License

Copyright © 2025–2026 Cameron Brooks.

This project is free software: you may redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.
Hardware design files and the outputs generated from them are instead licensed
under [CERN-OHL-S-2.0](LICENSES/CERN-OHL-S-2.0.txt). The exception is the sampler
case, which includes GPL libraries and remains GPL-3.0-or-later. The bench and
calibration data are licensed under [CC-BY-4.0](LICENSES/CC-BY-4.0.txt). See
[`LICENSING.md`](LICENSING.md) for what applies where, including the third-party
datasheets and standards that this repository does not license. The organization
[licensing policy](https://github.com/uwo-fast/.github/blob/main/LICENSING.md)
gives the reasons.
