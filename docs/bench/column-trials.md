# Column trials: water, bubbles, clay, then algae

The rig on the column in stages, each adding one unknown, so a problem points at its cause. Setup and
the motor runs behind these settings are in `data/bench/2026-11-05/notes.md`.

Write down the time of every change (gas on, clay added, top-up) in the day's bench notes, as the
summary only holds what the rig measured. Do not move the head, its load resistor or its trimmer between
stages, or the stages stop being comparable.

The limits below are starting points to judge by, not established figures. `raw-*.csv` keeps every row, so
any result can be looked at again with other limits.

## Before stage 1

1. **Measure** the riser's sample hole to the fill line, and the fill line's volume in litres. The hole
   needs about 40 mm of cover, plus whatever evaporation takes over the run.
2. **Check** the side plug at the fill line for leaks, and that the lid vents: back-pressure pushes liquid up
   the riser and shifts the timing.
3. **Install the services** (`rig/pi/README.md`), started by hand and not enabled at boot, so a run survives
   SSH dropping.
4. **Do a two-cycle run** with the column full of water and no gas, watching each burst. This is the first
   time `rig.py run`, not a capture script, drives the motor.

## Stage 1: water, gas off, then on

| Step | Cycles at 5 minutes | Change |
| --- | ---: | --- |
| 1a | 6 | Gas off: the baseline |
| 1b | 12 | Gas on, at the flow the algae run will use |
| 1c | 6 | Lamp on as well, if it was off. Compare with the lamp off |

**Passes if**, with gas on:

- at least 10 of 12 bursts read `ok`;
- the picked sample level stays within about 3 counts of the baseline, about 851, with no trend.

**Bubbles are the problem if** bursts turn to `thin` or `no_sample`, or the level sits lower with gas on.
A dip inside a burst does not matter by itself: only steady stretches count. Fixes to try: a hood or
downward-facing hole on the riser to shield it from the plume, or moving the hole away from the plume.

## Stage 2: clay, gas on

Same water, same head. Kaolin at known steps, to check that the reading still trends with the gas on and
that the rig copes where sample and air read alike.

Disperse each dose in about 100 mL of column water first, and pour it in. Give it 5 cycles at each step.

| Target (mg/L) | Added this step, in 8 L | A2 on 10-28 | Expected counts here |
| ---: | ---: | ---: | ---: |
| 250 | 2 g | −4.9 % | about 809 |
| 500 | 2 g | −15.0 % | about 723 |
| 1000 | 4 g | −32.2 % | about 577 |
| 1500 | 4 g | Not measured | about 435, by interpolation: **the same as air** |
| 2000 | 4 g | −61.5 % | about 328 |

For another volume, the dose in grams is the step in mg/L × litres ÷ 1000. Expected counts are the 10-28
percentages applied to 851. That was another container, filled by hand, so look for the trend, not a match.

**Passes if:**

- the reading falls at each step, close to the expected curve;
- it stays steady across the cycles at each step, so the gas keeps the clay suspended;
- at 1500 mg/L the rig reads `no_sample` rather than reporting a confident wrong number: the picking needs
  culture that reads above air.

The 1500 mg/L step is the crossover test: the point where the logger cannot separate sample from air, which
a growing culture will pass through. If the meniscus still shows in the raw rows there, the rig may not need
a crank sensor (`docs/bench/sampler-waveform.md`, step 3).

The logger picks the culture from each burst, so these limits can be changed afterwards and the raw
rows re-picked with `rig/pi/pick_samples.py`.

**Afterwards:** drain, rinse the column, riser and tube with DI water, and read clear water again. Pass: within
about 1 % of the start, about 851. A lasting drop means film on the tube.

## Stage 3: algae

Only after stages 1 and 2 pass.

1. Take the clear reference in the BG-11 used for the top-up, in the tube.
2. Top up the column and start a new `data_dir`, so this run has its own files.
3. Set `period_s` back to 900, and `enable` the services if they should survive a reboot.
4. Take samples for OD750 and dry weight now and then, with the time written down, to tie the readings
   to biomass.
5. End with a clear-water reference in the same tube, to measure fouling.
