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
- A metal block for each gap and bore, such as black-oxide Allen keys. A card in a stock
  head's gap let 3–7 counts through; metal reads 0.
- **Tube setup:** printed cases, tube, opaque sleeving or tape for the tube outside the
  cases, a stand that holds the cases with the tube vertical, and a way to move sample
  through the tube: a peristaltic pump recirculating from a stirred beaker (preferred), or
  a large syringe
- **Stock setup:** a clamp per head, and one container that holds every head at the same
  depth with its optical gap submerged and its connector end dry
- Opaque cover (a box or aluminium foil) over the whole beaker: a clear beaker under a
  translucent lid or flange still lets room light reach the stock heads. Stirring rod,
  thermometer.
- Kaolin, Tween 20, DI water, a balance, a graduated cylinder, and a pipette or small syringe for volumes under 1 mL

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

1. Plug each probe cable into its adapter. A head reading above about 950 counts in clear
   water needs its `RV` trimmer turned down first (see `docs/hardware.md`).
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
3. For each head, block the beam (a metal block in the gap, or a metal rod in the case bore) and
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

The first readings are why. On 2026-09-27, stock heads in air read between about 700 and
900, each one steady, but different from head to head. A DigiKey head (with a UL "RU"
mark) matched one DFRobot head, and a second DFRobot head differed from both. Those
readings were noted as "raw mV" without recording which column they came from, but
either way, nominally identical heads disagreed.

| File | Stock setup | Tube setup |
| --- | --- | --- |
| `01_air.csv` | Heads dry, in air | Cases empty, no tube |
| `02_dark.csv` | Metal block in each gap | Metal rod through each bore, before the tube goes in |
| `03a_clear_di.csv` | As `03`, in plain DI water | As `03`, filled with plain DI water |
| `03_clear.csv` | Heads in the blank diluent (below), covered | Tube in place, sleeved, filled with blank diluent, no bubbles |
| `04_clear_uncovered.csv` | As `03`, uncovered, room light | As `03`, sleeving removed near the cases |
| `05_clear_stability.csv` | As `03`, **10 minutes**, untouched | As `03`, **10 minutes**, no flow |

`01_air` is a health check, not a reference: the optics are designed for water, so air
readings need not resemble clear-water readings.

If `03` and `04` differ by more than the noise in `05`, ambient light is reaching the
detectors: keep everything covered or sleeved from here on. If `03a` and `03` differ, the
Tween 20 is changing the reading: record it before the series.

**Stock setup, crosstalk:** in the blank, block one head's gap with a metal block and confirm
the other heads' readings do not change. Repeat for each head.

## 5. Kaolin series

**Diluent:** DI water with 0.01 % v/v Tween 20. Every solution, including the blank and
the stock, is made with this same diluent, so the Tween 20 concentration stays constant and
only the kaolin changes.

1. **1 % stock:** 1 mL Tween 20 in 99 mL DI water. Mix by gentle inversion, not shaking.
   Tween 20 is too viscous to dose accurately by drops.
2. **Diluent:** 10 mL of the 1 % stock made up to 1 L with DI water. Make one batch for
   the day's work.

[`../test-solutions.md`](../test-solutions.md) gives the reasons for the dose.

**Stock (10 g/L):** 4.500 g kaolin made up to 450 mL with diluent, enough for three
repeats at 300 mL (140 mL each). **Shake it hard before every draw:** at 10 g/L the kaolin
settles in the bottle within minutes, and a draw from a settled bottle is mostly diluent.

**Series:** each repeat runs in one beaker of fresh diluent, raising the concentration
step by step at constant volume. At each step, stir, remove the volume below from the
beaker, then add the same volume of stock. Volumes are for 300 mL; for a beaker volume V,
the step from C_old to C_new is V × (C_new − C_old) / (10000 − C_old) mL.

| Step | Kaolin (mg/L) | Remove, then add stock (mL) |
| --- | ---: | ---: |
| `10_c0000` | 0 | 0 |
| `11_c0025` | 25 | 0.75 |
| `12_c0050` | 50 | 0.75 |
| `13_c0100` | 100 | 1.51 |
| `14_c0200` | 200 | 3.03 |
| `15_c0400` | 400 | 6.12 |
| `16_c0800` | 800 | 12.50 |
| `17_c1000` | 1000 | 6.52 |
| `18_c2000` | 2000 | 33.33 |
| `19_c4000` | 4000 | 75.00 |

Record any volume that differs from the table, so the concentration can be recomputed.
**Avoid bubbles and foam:** Tween 20 foams, and a bubble in the beam reads as turbidity.

**Stock setup:** the heads stay clamped in the covered beaker for the whole repeat. After
each addition:

1. Stir slowly to the bottom without breaking the surface. After a pause of more than a
   few minutes, stir longer: a cloud of settled kaolin stirred up around the heads reads as
   far more turbid than the beaker is.
2. Check each head's gap for bubbles. Lower heads in at an angle, and clear clinging
   bubbles with a squirt of diluent, not a finger.
3. Cover, wait 30 s, then capture.

Bubbles in the gaps caused the two bad captures in repeat 1. Both read far lower than the
trend and recovered when repeated (`data/bench/2026-10-26/photos/`).

**Tube setup,** each case on its own vertical tube and syringe, filled from the same standard. Set each tube head up
first ([`hardware/case/README.md`](../../hardware/case/README.md#optics-and-setup)): out of
the box, a board in the case sits near the ADC ceiling and barely responds.

Use separate standards rather than the beaker: each fill is then an independent sample,
and nothing settles onto the heads. Make each standard in its own capped bottle from the
10 g/L stock (shaken), made up with diluent:

| Kaolin (mg/L) | Stock (mL) | Diluent (mL) | Files |
| ---: | ---: | ---: | --- |
| 250 | 7.5 | 292.5 | `48_tube_c0250_1` … `_5` |
| 500 | 15 | 285 | `48_tube_c0500_1` … `_5` |
| 1000 | 30 | 270 | `48_tube_c1000_1` … `_5` |
| 2000 | 60 | 240 | `48_tube_c2000_1` … `_5` |
| 4000 | 120 | 180 | `48_tube_c4000_1` … `_5` |

1. Clear reference: five separate fills of clear water (`47_tube_clear_1` … `_5`),
   draining and refilling between them.
2. For each standard, low to high, five fills: shake the bottle, push at least 15 mL up
   through the tube (the last syringe slow and bubble-free), cover or sleeve, and capture
   30 s straight away. No DI rinse between standards: the next standard flushes the last.
3. Finish with a DI flush and one clear fill (`49_tube_clear_end`), to check for drift and
   for kaolin left on the tube.

With a pump instead of a syringe, recirculate from the stirred bottle, bottom to top, and
capture 60 s while it flows. Record the water temperature at each step.

If a capture disagrees with the trend, take it again under a `b` suffix, keep both, and
note which is used. Never re-run a capture under a name you want to keep: a capture that
fails before the header empties its output file (#21).

**Settling:** once, at 200 mg/L, capture 5 minutes with no flow or stirring
(`20_settling_c0200.csv`).

**Repeat the whole series three times** (`r1`, `r2`, `r3` suffixes), each from fresh
diluent.

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
- Tween 20 (product, lot) and dose in diluent:
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
