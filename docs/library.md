# The C library and its tools

A portable, stateless C11 library that models a TSW-10 or TST-10 head from the manufacturer's curves
and estimates turbidity from a reading, with a per-unit trim, gain and offset. A command-line tool
solves those three from three reference points, and `turbidity_stream` replays a logged CSV through
the model.

The manufacturer's curves describe a head in its stock housing. They do not describe the printed
tube case in `hardware/tube-case/`, whose water-filled tube changes the light path; a head in the case is
calibrated from its own dark, clear and reference readings instead
([`hardware/tube-case/README.md`](../hardware/tube-case/README.md)).

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

Input schema is strict, and any violation is a hard error:

- the first line is a header naming each column; it must include `timestamp_ms` and `raw_mv`, in any order, with no empty or repeated names
- other named columns are allowed and ignored, so the Arduino example's serial log replays as-is
- every row has exactly as many fields as the header, with no empty fields and no surrounding whitespace
- `timestamp_ms` is a non-negative integer up to 2^64 - 1; `raw_mv` is a finite number
- lines end in LF or CRLF, may be at most 510 characters, and the last line may omit its newline

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

The Arduino example lives under `examples/arduino/` and uses the same stateless library API. It builds for the Uno and Nano (`uno`, `nano`, `nano_oldbootloader`), and for an Uno with a switched emitter (`uno_switched_emitter`).

Every 100 ms it logs one CSV row over serial at 115200 baud:

- `adc_counts`: the mean of 16 ADC reads, the primary measurement
- `dark_adc_counts`: the same with the emitter off (`uno_switched_emitter` only), which measures ambient light
- `vcc_mv`: supply estimate from the ATmega328P's internal bandgap; it tracks drift within a session and is not an absolute measurement
- `raw_mv`, `filtered_mv`, `equivalent_mv`, `estimated_ntu`, `range_status`: the vendor-curve model applied to the reading

The log replays directly through `turbidity_stream`. `tools/capture_serial.py` (`just capture`) records it to a file, starting at the header and dropping a truncated last line.

`examples/arduino-multichannel/` is a bench logger for up to four heads at once on `A0`–`A3`. It logs `vcc_mv` and one `adc_counts_<pin>` column per head, with no model: `just summarize --dark … --clear …` normalizes each head against its own dark and clear-water captures.

[`docs/bench/session-1.md`](bench/session-1.md) is the first bench procedure, for the stock housings or the printed tube case: wiring checks, per-head references, and a kaolin dilution series.

The probe needs a load resistor and an emitter resistor. The default setup gets them from a DFRobot SEN0189 adapter with its switch at `A`: the adapter is the datasheet test circuit plus a unity-gain buffer, so its analog output is the probe voltage. Connect its signal to `A0`. [`docs/hardware.md`](hardware.md) covers the adapter circuit, a check for boards from other sources, and bare wiring without an adapter.
