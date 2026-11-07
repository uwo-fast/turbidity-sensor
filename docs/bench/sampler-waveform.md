# Sampler waveform test

What the tube head sees over one crank turn, measured before any logger is written for the column
(`data/bench/2026-11-05/notes.md`). About an hour, off the column at first.

It settles five things:

1. Whether the signal alone can tell air from sample when the two read the same, or the crank needs
   an index sensor.
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
  100 ms with no error. The compiler warns that the macro is redefined; that is expected. Check the
  rate from `timestamp_ms` in the first capture. The arithmetic gives about 13 ms per row, not yet
  measured on a board.
- **Motor:** terminal M4 of the Adafruit 2348 HAT, with 12 V on its power terminal and the Pi on its
  own supply. A bench supply with the leads switched by hand also works for this test.
- **Heads:** one head in the sampler, with its load resistor and references as recorded for it. Take
  a clear-water and a dry-tube reading first.
- **Fluid path:** the sampler's own riser and tube, tip down, with a jar at the same lift the column
  will have. Leave the line full of air when starting.

## Steps

Name captures `60_` upward in a new dated folder, and note the motor voltage in each.

**0. Measure.** Hole to fill line; hole to the beam (riser's top end to window); riser length; culture
level now and at the fill line, in litres; gas flow on the rotameter.

**1. Light.** Clear water still in the tube, 60 s each: lamp off, lamp on, a torch held on the sampler's
grey walls. The sampler is grey, not the opaque black the case calls for. Pass: within about 1 count
of each other. Otherwise sleeve it before anything else.

**2. Waveform, clear water.** Run 20 turns at 12 V. Expect a two-level trace. Note the air level
against the dry-tube reading: a wet tube may differ.

**3. Waveform at the crossover.** Dilute culture or kaolin until the still reading is within about
5 counts of the air level, and run 20 turns. Look for a visible edge at each meniscus crossing.

| Result | Then |
| --- | --- |
| Edges clear at the crossover | No crank sensor needed |
| No edges, but moving readings match still ones (step 4) | No crank sensor if burst data is enough; still readings near the crossover get flagged |
| No edges, and moving readings differ from still ones | Add the crank sensor |

**4. Moving against still.** On a sample well away from the air level, cut power at five random
points. Read 60 s still after each. Compare with that sample's level in the moving trace. This also
shows the settling rate.

**5. Exchange.** Start with clear water in the line, then put the riser in culture and log turn by
turn. Count the turns to within 1 % of that culture's level. Repeat with the line primed full of
liquid and no air: I expect that to be slower, with old liquid shuttling in the line.

**6. Stroke volume.** Line primed with water, its beaker on a 0.01 g balance. Turn the crank by hand
to each end of the stroke and read the mass at each. Difference in grams ≈ mL. Compare with 5.77 mL,
worked out from the nominal bore.

**7. Lowest speed.** Step the voltage or HAT throttle down from 12 V. At each step, note the turn time
and whether the motor restarts from a stop with the plunger mid-draw, five times. Note splashing or
bubbles at each speed. Keep the slowest setting that always restarts, with some margin.

## Then, on the column

Repeat steps 1 and 2 on the column with the gas on. Bubbles and foam are new here, so run this at the
real gas flow before starting a long run.

## Not covered

Fouling, drift and wear over days. The first multi-day run measures those; end it with a clear-water
reference in the same tube.
