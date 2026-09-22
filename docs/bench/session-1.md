# Bench session 1: proof of life and relative trend

## Goal

Show that a `TSW-10` or `TST-10`, wired to a 5 V AVR board, produces a stable signal that
decreases monotonically and repeatably as kaolin concentration rises.

This session does **not** establish NTU. There is no formazin standard, and the NTU
produced by a kaolin suspension depends on the kaolin batch, so concentrations are
recorded in mg/L of kaolin. The vendor-curve NTU the firmware prints is not evidence of
anything yet. The raw ADC counts are the measurement.

Run the `TSW-10` first: its vendor test range (0–1000 NTU) is the lower of the two, which
suits a series that starts at clear water. Repeat with the `TST-10` if time allows.

## Equipment

- `TSW-10` and/or `TST-10`, an Arduino Uno or Nano, and a USB cable
- 4.7 kΩ resistor (`Ro`) and 470 Ω resistor (`Ri`), breadboard, jumper wires
- Multimeter
- Clamp or stand that holds the sensor at a fixed depth, with the optical gap submerged
  and the connector end dry
- One beaker that fits the sensor (use the same beaker throughout), stirring rod,
  thermometer
- Opaque cover for the beaker and sensor (a box or aluminium foil)
- Kaolin, Tween 20, DI water, a balance, a graduated cylinder or pipettes

Use only a **5 V** board. The sensor output reaches about 4.8 V, which exceeds the ADC
input range of 3.3 V boards such as ESP32 or RP2040. Those need a voltage divider,
which is out of scope for this session.

## Safety

- Kaolin is a fine powder. Weigh and transfer it gently to avoid raising dust, and wear
  a dust mask if one is available. Follow your lab's SDS for kaolin and Tween 20.
- Keep liquids away from the board and the breadboard. Only the sensor's optical end
  goes in the water; its connector is not rated for immersion.
- Power everything from USB only.

## 1. Wire the sensor

Use the datasheet test circuit in the README (Arduino Example section):

| Sensor pin | Connect to |
| --- | --- |
| 1 | 5 V |
| 2 | A0, and 4.7 kΩ to GND |
| 3 | 470 Ω to GND |

**Optional ambient-light check:** wire the 470 Ω resistor to **D7** instead of GND and use
the `uno_switched_emitter` build. The firmware then turns the emitter off briefly for
every sample and logs `dark_adc_counts`, which is the reading from ambient light
alone. This build targets the Uno. For a Nano, copy the env with `board = nanoatmega328new`.

## 2. Electrical checks (before any water)

With the board powered over USB and the sensor dry:

1. Measure the 5 V rail at the board. Record it; it is the ADC reference.
2. Measure the voltage across `Ri` (pin 3 to GND). Emitter current is that voltage
   divided by 470 Ω; it must be under the 30 mA rating. Record both.
3. Measure pin 2 to GND with the gap open, then with an opaque card blocking the gap.
   The voltage must drop clearly when blocked. If it does not, stop and recheck the wiring.

## 3. Flash and capture

```sh
just upload uno        # or: nano, nano_oldbootloader, uno_switched_emitter
just capture /dev/ttyACM0 data/bench/<date>/01_dry_open.csv --duration 60
```

The port is usually `/dev/ttyACM0` for an Uno and `/dev/ttyUSB0` for a Nano clone.
Opening the port resets the board. The capture starts at the CSV header and ends after
`--duration` seconds, or at Ctrl+C.

Store each capture under `data/bench/<date>/` (the capture tool creates the folder)
with a numbered step name, as in the steps below, plus a `notes.md` from the template at
the end.

## 4. Baselines

Capture 60 s for each, with the sensor clamped in its measuring position:

| File | Condition |
| --- | --- |
| `01_dry_open.csv` | Dry, in air, room light |
| `02_dry_blocked.csv` | Dry, opaque card in the gap |
| `03_blank_covered.csv` | In the blank diluent (below), covered |
| `04_blank_uncovered.csv` | In the blank diluent, uncovered, room light |
| `05_blank_stability.csv` | In the blank diluent, covered, **10 minutes**, untouched |

If `03` and `04` differ by more than the noise in `05`, ambient light is reaching the
detector. Keep the sensor covered for every step after this.

## 5. Kaolin series

**Diluent:** DI water plus a small, fixed dose of Tween 20 (for example one drop per
litre). Record exactly what you used. Every solution in the series, including the blank
and the stock, is made with this same diluent, so the Tween 20 concentration stays constant
and only the kaolin changes.

**Stock (1000 mg/L):** 1.000 g kaolin made up to 1 L with diluent. Mix well.

**Dilutions** (200 mL each, made from well-mixed stock):

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

For each step, from low to high concentration:

1. Pour the solution into the beaker, clamp the sensor in its measuring position, and
   cover.
2. Stir gently for 10 s. **Avoid bubbles and foam:** Tween 20 foams, and bubbles in the
   gap scatter light and read as turbidity.
3. Capture 60 s. Record the water temperature.
4. Empty the beaker. Rinse the beaker and sensor with diluent.

Kaolin settles, so the reading drifts upward (clearer) after stirring stops. That drift
is expected. Once, at 200 mg/L, capture 5 minutes after stirring (`20_settling_c0200.csv`)
to measure it.

**Repeat the whole series three times** (`r1`, `r2`, `r3` suffixes). Re-stir the stock
before each dilution.

## 6. Pass criteria

Session 1 passes when all of the following hold:

1. **Electrical:** the emitter current is under 30 mA, and pin 2 responds to blocking the
   gap.
2. **Stability:** the standard deviation of `adc_counts` in `05_blank_stability.csv` is
   recorded. Call it σ; 3σ is the resolution floor for this setup.
3. **Monotonic trend:** in every repeat, mean `adc_counts` falls at each step up the
   series, and each drop is larger than 3σ.
4. **Repeatability:** the spread of the three repeats at each concentration is recorded.
   There is no threshold yet; this number sets the target for session 2.

Also record the following. They are findings, not pass or fail:

- Whether the blank reading falls in the datasheet's 0 NTU envelope: 3.68–4.73 V for the
  `TSW-10`, 3.78–4.55 V for the `TST-10`. At a 5.000 V reference that is about 754–969
  and 775–932 counts. Outside it means something to explain (supply, wiring, or the part),
  not a failed session.
- The ambient-light difference (`03` vs `04`, or `dark_adc_counts`).
- The settling drift at 200 mg/L.

## 7. Analysis

```sh
just summarize data/bench/<date>/[0-9]*.csv > data/bench/<date>/summary.csv
```

The `[0-9]*` pattern matches only the numbered step files, so `summary.csv` is not
summarized itself on a re-run. The output gives the count, mean, standard deviation, min
and max of each signal column per file. Plot mean `adc_counts` against kaolin concentration, one line per repeat.

`raw_mv` assumes a 5000 mV reference. For volts, rescale by the 5 V rail measured in
step 2: `mV = adc_counts × rail_mV / 1024`. `vcc_mv` is estimated from the chip's
internal bandgap, which varies by about 10% between chips. Use it only to watch for
supply drift within a session.

## Notes template

Copy into `data/bench/<date>/notes.md`:

```markdown
# Bench session 1: <date>

- Operator:
- Sensor: TSW-10 / TST-10, marking or ID:
- Board and firmware env:
- Commit (`git rev-parse --short HEAD`):
- 5 V rail (multimeter):
- Voltage across Ri / emitter current:
- Pin 2, gap open / blocked:
- Room temperature:
- Kaolin (product, lot):
- Tween 20 dose in diluent:
- Beaker and sensor depth:

## Step log

| File | Time | Water temp (°C) | Notes |
| --- | --- | --- | --- |

## Observations
```
