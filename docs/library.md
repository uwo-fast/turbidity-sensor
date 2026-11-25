# The C library and its tools

A portable, stateless C11 library. It models a TSW-10 or TST-10 head from the manufacturer's curves
and estimates turbidity from a reading, using a per-unit trim, gain and offset. A command-line tool
solves for those three parameters from three reference points. `turbidity_stream` replays a logged
CSV through the model.

The manufacturer's curves describe a head in its stock housing. They do not describe a head in the
printed tube case in `hardware/tube-case/`, where the water-filled tube changes the light path. A head
in the case is calibrated from its own dark, clear and reference readings instead
([`hardware/tube-case/README.md`](../hardware/tube-case/README.md)).

## Install

```sh
cmake --install build --prefix ./_install
```

The install exports a standard CMake package that downstream projects can use with:

```cmake
find_package(turbidity REQUIRED CONFIG)
target_link_libraries(my_app PRIVATE turbidity::turbidity)
```

## Quick start

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

The solve has three free parameters for three points, so `rmse_mv` and `max_abs_error_mv` are zero whenever `trim_t` falls inside `[0, 1]`. They do not measure calibration quality. The tool exits non-zero instead of printing a profile in two cases. The first is when the points do not constrain the fit: voltage must fall as NTU rises, and the points must span at least a tenth of the sensor's range. The library returns `TURBIDITY_STATUS_INVALID_ARGUMENT` for these. The second is when the fit lands on a `trim_t` bound, where the vendor model's family of curves cannot represent the points.

Replay a CSV stream through the model:

```sh
printf 'timestamp_ms,raw_mv\n0,4195\n100,3452\n200,2497\n' | \
  build/turbidity_stream --sensor tsw10 --trim 0.5 --gain 1.0 --offset-mv 0 --filter-window 8
```

The input schema is strict, and any violation is a hard error:

- the first line is a header naming each column; it must include `timestamp_ms` and `raw_mv`, in any order, with no empty or repeated names
- other named columns are allowed and ignored, so the Arduino example's serial log replays as-is
- every row has exactly as many fields as the header, with no empty fields and no surrounding whitespace
- `timestamp_ms` is a non-negative integer up to 2^64 - 1; `raw_mv` is a finite number
- lines end in LF or CRLF, may be at most 510 characters, and the last line may omit its newline

## Calibration data pipeline

The vendor-derived model is generated from the digitized point clouds in `data/calibration/vendor-data/`.

To regenerate the derived calibration tables, fit reports, and runtime header:

```sh
python3 tools/generate_vendor_calibration.py
```

To have CMake run the regeneration as part of the build, enable:

```sh
cmake -S . -B build -DTURBIDITY_REGENERATE_CALIBRATION=ON
```

## Arduino example

The Arduino example is in `examples/arduino/` and uses the same stateless library API. It builds for the Uno and Nano (`uno`, `nano`, `nano_oldbootloader`), and for an Uno with a switched emitter (`uno_switched_emitter`).

Every 100 ms it logs one CSV row over serial at 115200 baud:

- `adc_counts`: the mean of 16 ADC reads, the primary measurement
- `dark_adc_counts`: the same with the emitter off (`uno_switched_emitter` only), which measures ambient light
- `vcc_mv`: supply voltage estimated from the internal bandgap of the ATmega328P. It tracks drift within a session and is not an absolute measurement
- `raw_mv`, `filtered_mv`, `equivalent_mv`, `estimated_ntu`, `range_status`: the vendor-curve model applied to the reading

The log can be replayed directly through `turbidity_stream`. `tools/capture_serial.py` (`just capture`) records it to a file, starting at the header and dropping a truncated last line.

`examples/arduino-multichannel/` is a bench logger for up to four heads at once on `A0`–`A3`. It logs `vcc_mv` and one `adc_counts_<pin>` column per head, without applying the model. `just summarize --dark … --clear …` normalizes each head against its own dark and clear-water captures.

[`docs/bench/session-1.md`](bench/session-1.md) is the first bench procedure, for the stock housings or the printed tube case. It covers wiring checks, references for each head, and a kaolin dilution series.

The probe needs a load resistor and an emitter resistor. In the default setup, these come from a DFRobot SEN0189 adapter with its switch at `A`. The adapter is the datasheet test circuit plus a unity-gain buffer, so its analog output is the probe voltage. Connect its signal output to `A0`. [`docs/hardware.md`](hardware.md) covers the adapter circuit, a check for boards from other sources, and bare wiring without an adapter.
