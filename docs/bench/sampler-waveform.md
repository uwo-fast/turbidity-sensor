# Sampler waveform test

This test measures the tube head signal over one crank turn, before any logger is written for the
column (`data/bench/2026-11-05/notes.md`). It takes about an hour, and starts off the column.

It answers five questions:

1. Whether the signal alone can distinguish air from sample when the two read the same, or whether the
   crank needs an index sensor.
2. How far moving readings differ from still ones.
3. How many turns replace the sample.
4. The real stroke volume.
5. The lowest speed the motor runs and restarts at.

## Why

In the tube, air reads below clear water. A1 read 474.5 counts with a dry tube
(`data/bench/2026-10-28/`, `45_a1_tube_load_air`) and 463.0 in the culture as grown
(`data/bench/2026-10-29/`, `c1000`), so a fixed threshold fails near that density.

## Setup

- **Logger at 50 Hz:** the default 10 Hz gives too few rows per turn. No source change is needed:

  ```sh
  PLATFORMIO_BUILD_FLAGS=-DTURBIDITY_SAMPLE_PERIOD_MS=20 just upload nano arduino-multichannel
  ```

  Do not add `-UTURBIDITY_SAMPLE_PERIOD_MS`: PlatformIO places it last, and the build falls back to
  100 ms with no error. The compiler warns that the macro is redefined. This is expected. Check the
  rate from `timestamp_ms` in the first capture. The calculation gives about 13 ms per row; this has
  not yet been measured on a board.
- **Motor:** terminal M4 of the Adafruit 2348 HAT, with 12 V on its power terminal and the Pi on its
  own supply. A bench supply with the leads switched by hand also works for this test.
- **Heads:** one head in the sampler, with the load resistor and references recorded for it. Take
  a clear-water and a dry-tube reading first.
- **Fluid path:** the riser and tube of the sampler, tip down, with a jar at the same lift height as
  the column. Leave the line full of air when starting.

## Steps

Number the captures from `60_` upward in a new dated folder, and note the motor voltage for each.

**0. Measure.** Measure the distance from the hole to the fill line, the distance from the hole to the
beam (top end of the riser to the window), the riser length, the culture volume now and at the fill
line in litres, and the gas flow on the rotameter.

**1. Light.** With clear water standing in the tube, record 60 s each with the lamp off, the lamp on, and
a torch held on the grey walls of the sampler. The sampler is grey, not the opaque black that the case
design calls for. Pass: the three readings agree within about 1 count. Otherwise, sleeve the sampler
before anything else.

**2. Waveform, clear water.** Run 20 turns at 12 V. Expect a two-level trace. Compare the air level
with the dry-tube reading, since a wet tube may differ.

**3. Waveform at the crossover.** Dilute culture or kaolin until the still reading is within about
5 counts of the air level, and run 20 turns. Look for a visible edge at each meniscus crossing.

| Result | Then |
| --- | --- |
| Edges clear at the crossover | No crank sensor needed |
| No edges, but moving readings match still ones (step 4) | No crank sensor if burst data is enough. Still readings near the crossover are flagged |
| No edges, and moving readings differ from still ones | Add the crank sensor |

**4. Moving against still.** On a sample well away from the air level, cut power at five random
points. Read for 60 s with the liquid still after each. Compare with the level of that sample in the
moving trace. This also shows the settling rate.

**5. Exchange.** Start with clear water in the line, then put the riser in culture and log turn by
turn. Count the turns until the reading is within 1 % of the culture level. Repeat with the line
primed full of liquid and no air. I expect that to be slower, because old liquid shuttles back and
forth in the line.

**6. Stroke volume.** Prime the line with water and put its beaker on a 0.01 g balance. Turn the crank
by hand to each end of the stroke and read the mass at each. The difference in grams ≈ mL. Compare
with 5.77 mL, calculated from the nominal bore.

**7. Lowest speed.** Step the voltage or HAT throttle down from 12 V. At each step, note the turn time,
and check five times whether the motor restarts from a stop with the plunger mid-draw. Note splashing or
bubbles at each speed. Keep the slowest setting that always restarts, with some margin.

## Then, on the column

Repeat steps 1 and 2 on the column with the gas on. Bubbles and foam are new here, so run this at the
real gas flow before starting a long run.

## Not covered

This test does not cover fouling, drift or wear over several days. The first multi-day run measures
those. End that run with a clear-water reference in the same tube.
