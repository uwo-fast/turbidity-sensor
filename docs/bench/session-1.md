# Bench session 1: proof of life and relative trend

## Goal

Show that turbidity heads, read through DFRobot SEN0189 adapters by a 5 V AVR board,
give stable signals that fall monotonically and repeatably as kaolin concentration rises.
Then check whether several heads agree once each is normalized against its own dark and
clear-water readings.

This session does **not** establish NTU. There is no formazin standard, and the NTU of a
kaolin suspension depends on the kaolin batch, so concentrations are recorded in mg/L of
kaolin. The ADC counts, and the transmittance computed from them, are the measurements.

## Choose a setup

Both setups use the same adapters, firmware and analysis. They differ in how the sample
reaches the beam and how the references are taken. Run one setup per session.

| Setup | Head | Sample |
| --- | --- | --- |
| **Tube** | Bare probe board in the printed case ([`hardware/case/`](../../hardware/case/README.md)) | Flows through a clear 5/16 x 1/4 in tube in the optical slot |
| **Stock** | Unmodified `TSW-10` or `TST-10` in its own housing | The head is immersed in a container |

Most users will run the stock housings, so both are supported equally. This lab starts with
the tube setup. The vendor curves and the datasheet envelope apply only to the stock
setup: the tube's optical path is different.

**Heads:** up to four at once, on `A0`–`A3`, with the `arduino-multichannel` logger. One
head with the single-channel `arduino` example also works; its log has one `adc_counts`
column instead of `adc_counts_a0`…`a3`.

## Equipment

- Probes (with their cables) and one SEN0189 adapter per head
- Arduino Nano (or Uno) and a USB cable; a breadboard to share 5 V and GND among adapters
- Multimeter
- An opaque card (stock) or an opaque 5/16 in rod, such as a dowel wrapped in black tape (tube)
- **Tube setup:** printed cases, tube, opaque sleeving or tape for the tube outside the
  cases, a stand that holds the cases with the tube vertical, and a way to move sample
  through the tube: a peristaltic pump recirculating from a stirred beaker (preferred), or
  a large syringe
- **Stock setup:** a clamp per head, and one container that holds every head at the same
  depth with its optical gap submerged and its connector end dry
- Opaque cover (a box or aluminium foil), stirring rod, thermometer
- Kaolin, Tween 20, DI water, a balance, a graduated cylinder or pipettes

Use only a **5 V** board. The output reaches about 4.8 V, beyond the ADC range of 3.3 V
boards such as ESP32 or RP2040.

## Safety

- Kaolin is a fine powder. Weigh and transfer it gently to avoid raising dust, and wear
  a dust mask if one is available. Follow your lab's SDS for kaolin and Tween 20.
- Keep liquids away from the adapters, the breadboard and the Arduino. None is
  waterproof. Stock setup: only the probe's optical end goes in the water; its connector
  is not rated for immersion. Tube setup: check the tube joints for leaks before running
  kaolin.
- Power everything from USB only.

## 1. Connect the hardware

See [`docs/hardware.md`](../hardware.md) for what the adapter does to the signal.

1. Plug each probe cable into its adapter. Do not adjust the `RV` trimmer on any probe
   (see `docs/hardware.md`).
2. Set every adapter's switch to **`A`**. Leave its potentiometer alone; it does nothing
   in `A` mode.
3. Connect every adapter's `VCC` and `GND` to the Nano's `5V` and `GND`, and each
   adapter's signal to its own input, `A0` to `A3`. Record which head is on which input.

Four adapters draw well under 100 mA together (each emitter is capped at 10 mA by the
adapter's 500 Ω resistor), which USB supplies.

## 2. Electrical checks (before any water)

With the Nano powered over USB and every head dry:

1. Measure the 5 V rail at the Nano. Record it; it is the ADC reference.
2. For each adapter, run the adapter check in `docs/hardware.md`: the probe's middle pin
   and the adapter's signal output agree within a few tens of millivolts. Label and set
   aside any adapter that fails.
3. For each head, block the beam (the card in the gap, or the rod in the case bore) and
   confirm its output drops clearly.

## 3. Flash and capture

```sh
just upload nano arduino-multichannel   # or nano_oldbootloader for most clones
just capture /dev/ttyUSB0 data/bench/<date>/01_air.csv --duration 60
```

The port is usually `/dev/ttyUSB0` for a Nano clone and `/dev/ttyACM0` for an Uno. Opening
the port resets the board. The capture starts at the CSV header and ends after
`--duration` seconds, or at Ctrl+C. The tool creates the folder.

Store every capture under `data/bench/<date>/` with a numbered step name, as below, plus a
`notes.md` from the template at the end. Every file holds all heads, one column each.

## 4. References and baselines

The references make heads comparable: each head's readings are later expressed as a
transmittance between its own dark (0) and clear-water (1) readings.

| File | Stock setup | Tube setup |
| --- | --- | --- |
| `01_air.csv` | Heads dry, in air | Cases empty, no tube |
| `02_dark.csv` | Opaque card in each gap | Opaque rod through each bore, before the tube goes in |
| `03_clear.csv` | Heads in the blank diluent (below), covered | Tube in place, sleeved, filled with blank diluent, no bubbles |
| `04_clear_uncovered.csv` | As `03`, uncovered, room light | As `03`, sleeving removed near the cases |
| `05_clear_stability.csv` | As `03`, **10 minutes**, untouched | As `03`, **10 minutes**, no flow |

`01_air` is a health check, not a reference: the optics are designed for water, so air
readings need not resemble clear-water readings.

If `03` and `04` differ by more than the noise in `05`, ambient light is reaching the
detectors: keep everything covered or sleeved from here on.

**Stock setup, crosstalk:** in the blank, block one head's gap with the card and confirm
the other heads' readings do not change. Repeat for each head.

## 5. Kaolin series

**Diluent:** DI water plus a small, fixed dose of Tween 20 (for example one drop per
litre). Record exactly what you used. Every solution, including the blank and the stock,
is made with this same diluent, so the Tween 20 concentration stays constant and only the
kaolin changes.

**Stock (1000 mg/L):** 1.000 g kaolin made up to 1 L with diluent. Mix well.

**Dilutions,** per 200 mL. Scale every volume by the same factor to fill your container:

| Step | Kaolin (mg/L) | Stock (mL) | Diluent (mL) |
| --- | ---: | ---: | ---: |
| `10_c0000` | 0 | 0 | 200 |
| `11_c0025` | 25 | 5 | 195 |
| `12_c0050` | 50 | 10 | 190 |
| `13_c0100` | 100 | 20 | 180 |
| `14_c0200` | 200 | 40 | 160 |
| `15_c0400` | 400 | 80 | 120 |
| `16_c0800` | 800 | 160 | 40 |
| `17_c1000` | 1000 | 200 | 0 |

Run the steps from low to high concentration. Stir gently throughout. **Avoid bubbles
and foam:** Tween 20 foams, and a bubble in the beam reads as turbidity.

**Tube setup,** with the cases in series on one vertical tube line:

1. With a pump: recirculate from the stirred beaker through the tube, bottom to top, so
   bubbles rise out. Let it run until readings settle, then capture 60 s while it flows.
2. With a syringe: push at least three tube volumes of the new solution up through the
   tube, then capture 30 s straight away. Kaolin settles in a still tube, so the reading
   drifts clearer within seconds to minutes.
3. Record the water temperature. Move to the next beaker without rinsing: the next
   solution flushes the tube.

**Stock setup:**

1. Pour the solution into the container, clamp the heads in position, and cover.
2. Stir gently for 10 s, then capture 60 s. Record the water temperature.
3. Empty the container. Rinse the container and heads with diluent.

**Settling:** once, at 200 mg/L, capture 5 minutes with no flow or stirring
(`20_settling_c0200.csv`).

**Repeat the whole series three times** (`r1`, `r2`, `r3` suffixes). Re-stir the stock
before each dilution.

**End of session:** capture the clear reference again (`30_clear_end.csv`) the same way as
`03`, to measure drift.

## 6. Pass criteria

Session 1 passes when all of the following hold for every head that passed its adapter
check:

1. **Electrical:** the output drops when the beam is blocked.
2. **Stability:** the standard deviation of the head's counts in
   `05_clear_stability.csv` is recorded. Call it σ; 3σ is that head's resolution floor.
3. **Monotonic trend:** in every repeat, the head's mean counts fall at each step up the
   series, and each drop is larger than 3σ.
4. **Repeatability:** the spread of the three repeats at each concentration is recorded.

Record these as findings, not pass or fail:

- **Head agreement:** at each concentration, the spread of attenuation between heads.
  If it is small, one curve can serve every head once each has its two references.
  This sets the target for session 2.
- **Drift:** `30_clear_end` against `03_clear`, per head.
- **Ambient light:** `03` against `04`.
- **Settling** at 200 mg/L.
- **Stock setup only:** whether each head's clear reading falls in the datasheet's 0 NTU
  envelope (3.68–4.73 V for the `TSW-10`, 3.78–4.55 V for the `TST-10`; about 754–969 and
  775–932 counts at a 5.000 V reference). DFRobot's own figure is 4.1 ± 0.3 V. The
  adapter's 500 Ω emitter resistor may put readings slightly lower.

## 7. Analysis

```sh
just summarize --dark data/bench/<date>/02_dark.csv --clear data/bench/<date>/03_clear.csv \
  data/bench/<date>/[0-9]*.csv > data/bench/<date>/summary.csv
```

For each file and head this gives the count, mean, standard deviation, min and max of the
counts, plus:

- `transmittance`: `(mean - dark) / (clear - dark)`, from 1 in clear water toward 0 as
  the beam is blocked;
- `attenuation`: `-ln(transmittance)`, which starts at 0 in clear water and rises with
  turbidity.

The reference files appear in the output too; `02` should normalize to about 0 and `03`
to 1. The command warns when a head's clear reading is within 5% of full scale, where it
may clip. Plot attenuation against kaolin concentration, one line per head and repeat.
The `[0-9]*` pattern matches only the numbered step files, so `summary.csv` is not
summarized itself on a re-run.

`vcc_mv` is estimated from the chip's internal bandgap, which varies by about 10% between
chips. Use it only to watch for supply drift within a session.

## Notes template

Copy into `data/bench/<date>/notes.md`:

```markdown
# Bench session 1: <date>

- Operator:
- Setup: tube / stock
- Board and firmware (example and env):
- Commit (`git rev-parse --short HEAD`):
- 5 V rail (multimeter):
- Room temperature:
- Kaolin (product, lot):
- Tween 20 dose in diluent:
- Tube setup: tube material and size, flow method (pump rate or syringe):
- Stock setup: container and head depth:

## Heads

| Input | Sensor (TSW-10 / TST-10) | Source | ID | Adapter (source, marking) | Adapter check (probe / output, V) | Blocked drop OK |
| --- | --- | --- | --- | --- | --- | --- |
| A0 | | | | | | |
| A1 | | | | | | |
| A2 | | | | | | |
| A3 | | | | | | |

## Step log

| File | Time | Water temp (°C) | Notes |
| --- | --- | --- | --- |

## Observations
```
