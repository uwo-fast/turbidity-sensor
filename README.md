# turbidity

Portable C turbidity modeling and calibration utilities for the Amphenol `TSW-10` and `TST-10` sensors.

This repository is now organized as a small code-first open source project:

- a stateless C library for the sensor model and 3-point calibration solve
- a calibration CLI that emits a machine-readable JSON profile
- a strict CSV stream example for host-side validation and replay
- an Arduino example that applies the same model to a conditioned analog input

## Status

This is an MVP built from vendor-datasheet curves that were digitized and fit offline. It is useful for software integration, bench validation, and unit-specific 3-point profiling, but it is not a substitute for empirical end-to-end optical calibration on finished hardware.

## Repository Map

- `include/`: public C API
- `src/`: core implementation plus the generated vendor-fit header used at runtime
- `tools/`: offline utilities, including the 3-point calibration CLI and calibration generator
- `examples/`: host and Arduino examples
- `data/calibration/`: raw vendor digitizations and generated calibration artifacts
- `tests/`: unit, CLI-contract, and package smoke tests
- `docs/archive/`: preserved research, planning, and datasheet material

## Development

Tasks run through [`just`](https://github.com/casey/just) (`just --list` shows them all):

```sh
just build    # configure and compile (warnings are errors)
just test     # build and run the test suite
just check    # clang-format check + clang-tidy (CI-equivalent)
just fmt      # format C/C++ sources in place
just regen    # regenerate calibration artifacts
just arduino  # compile the Arduino example with PlatformIO
```

`fmt`, `check` and CI use clang-format and clang-tidy 18.1.8.

Without `just`, the equivalent CMake commands are:

```sh
cmake -S . -B build -DBUILD_TESTS=ON -DBUILD_TOOLS=ON -DBUILD_EXAMPLES=ON
cmake --build build
ctest --test-dir build --output-on-failure
```

## Install

```sh
cmake --install build --prefix ./_install
```

The install exports a standard CMake package that downstream projects can consume with:

```cmake
find_package(turbidity REQUIRED CONFIG)
target_link_libraries(my_app PRIVATE turbidity::turbidity)
```

## Quick Start

Solve a unit-specific profile from exactly three known `NTU,mV` reference pairs:

```sh
build/turbidity_calibrate \
  --sensor tsw10 \
  --point 0,4195 \
  --point 500,3452 \
  --point 1500,2497
```

Example JSON output:

```json
{"sensor":"tsw10","trim_t":0.478192628,"gain":1.003159094,"offset_mv":12.943040793,"rmse_mv":0.000000000,"max_abs_error_mv":0.000000000}
```

The solve has three free parameters for three points, so `rmse_mv` and `max_abs_error_mv` are zero whenever `trim_t` lands inside `[0, 1]`. They only become non-zero when `trim_t` is pinned at a bound, so they do not measure calibration quality.

Replay a CSV stream through the model:

```sh
printf 'timestamp_ms,raw_mv\n0,4195\n100,3452\n200,2497\n' | \
  build/turbidity_stream --sensor tsw10 --trim 0.5 --gain 1.0 --offset-mv 0 --filter-window 8
```

Input schema is strict:

- the first line must be exactly `timestamp_ms,raw_mv`
- every sample row must contain exactly two columns
- malformed rows are treated as hard errors

## Calibration Data Pipeline

The vendor-derived model is generated from the digitized point clouds in `data/calibration/vendor-data/`.

To regenerate the derived calibration tables, fit reports, and runtime header:

```sh
python3 tools/generate_vendor_calibration.py
```

If you want CMake to run that regeneration as part of the build, enable:

```sh
cmake -S . -B build -DTURBIDITY_REGENERATE_CALIBRATION=ON
```

## Arduino Example

The Arduino example lives under `examples/arduino/` and uses the same stateless library API. It reads the sensor output as an analog voltage in millivolts.

The `TST-10` and `TSW-10` need two external resistors, per the datasheet test circuit:

| Sensor pin | Function | Connect to |
| --- | --- | --- |
| 1 | VCC (emitter anode, phototransistor collector) | +5 V |
| 2 | Output (phototransistor emitter) | ADC input, and `Ro` 4.7 kΩ to GND |
| 3 | Emitter diode cathode | `Ri` 470 Ω to GND |

Power the sensor from the same 5 V rail the ADC uses as its reference. The emitter current, and so the output, rises with the supply, so a shared reference cancels part of the supply variation. It is not fully ratiometric, because the diode forward voltage does not scale with the supply.

## License

This project is licensed under `GPL-3.0-only`. See [LICENSE](LICENSE).
