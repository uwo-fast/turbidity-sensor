# Algae run 2: plan

Run 2 repeats the run-1 growth test (`data/bench/2026-11-05/notes.md`) with three changes: the rebuilt actuator,
an all-black printed housing, and the fixes below for what run 1 got wrong. Like run 1, it is meant to show
that an uncontrolled, timer-driven sampler and a simple logger can follow a batch culture against Cary OD750.

## What changes from run 1

| Run 1 | Run 2 |
| --- | --- |
| The crank cammed out on 11-15 08:34; the motor's screws worked loose | Motor turned with its screws along the stroke and gripped by a printed cradle (uwo-fast/syringe-actuator PR #24) |
| The stall went unnoticed until morning | A Healthchecks heartbeat on the Pi fails after 2 `no_motion` or `aborted` bursts in a row. It is lab setup and is kept outside this repo |
| The housing let light through; A2 stepped ±10–13 counts at each lamp switch | All-black housing, then the light test below |
| Lamp switch times inferred from the data | Lamp state logged on `a3` by a light-dependent resistor facing the lamp |
| The air reading is the floor: A2 reads air below about 526 counts (air 466 + `near_air` 60), which the run-1 fit puts at OD 2.53. Run 1 plateaued at 2.2–2.35 | Run to the plateau as in run 1, so the two compare. Mark any sensor point above OD 2.4 as near the air floor |
| Inoculum OD not measured | Same volumes (100 + 100 mL into 3 L BG-11), with the inoculum read on the Cary first |

## Before the culture goes in

1. **Actuator:** mount it and run 20 bursts in DI at `throttle = 0.5`. Every burst must read `ok`, with the line moving.
2. **Firmware:** confirm the Nano still runs `multichannel-20ms.hex`, sha256 `86a29036bcd43686…`.
3. **Clear reference:** DI through A2's line, 30 min or more, after the housing is closed. This replaces 854.1, which
   belonged to the run-1 housing.
4. **Light test, in DI, before the culture.** Housing closed, lamp switched by hand 3 times, 30 min on and 30 min off
   each time, with A1 in DI outside the column as a control. In DI there are no cells to respond to light, so:
   - if the step is gone in DI, the run-1 steps were the culture's response;
   - if the step is still there, it is light or the supply reaching the head.
   
   Lamp state comes from `a3`: a light-dependent resistor in a divider with a 10 kΩ resistor, taped facing the lamp.
   Any LDR whose resistance under the lamp is near 10 kΩ will do. The test also sets the on/off threshold for `a3`.
5. **Supply step:** the Nano's `vcc_mv` stepped about 130 mV at lamp switches. Check whether the Pi's supply and the
   lamp's share a power strip or circuit, and move one if so. The light test shows whether that removes the step.
6. **Daily 12:04 link loss:** in run 1 the Nano's USB dropped for 3 s at 12:04 local on four days running (`link_lost`
   in `events.csv`; 3 of them aborted a burst). Read the Pi's journal around 12:04 for a timer or a USB reset.
7. **Config:** `data_dir = "~/rig-data/algae-run-2"`. Commit any other change to `rig/pi/rig.toml` before the run,
   so "what ran" is a commit.

## During the run

- **Heartbeat:** enable the timer after the first burst is logged, and disable it before stopping the rig.
- **Cary OD750:** two samples per draw, twice a day, from the sampler's depth. Dilute 1:N with N = round(OD / 0.25) − 1,
  taking the OD from the fit on the sensor just before drawing. That puts each read at about 0.25. For example:

  | Expected OD | Dilution |
  | ---: | --- |
  | 0.4 | 1:1 |
  | 0.8 | 1:2 |
  | 1.2 | 1:4 |
  | 1.6 | 1:5 |
  | 2.0 | 1:7 |
  | 2.4 | 1:9 |

- **Samples to avoid:** no draws in the first 90 min after the lamp comes on. In run 1, both samples drawn 45–50 min after
  lamp-on read off the fit (11-09 10:20 and 11-11 09:10). The one at 70 min (11-13 09:38) read on it.
- **Reading samples:** read them the same day where possible. Fridge-stored samples read on the fit in run 1, but the
  10-29 re-reads after storage scattered 24 %.
- **DI top-ups:** to the start mark, logged with time and volume, not within 15 min before a Cary draw.
- **Hand draws** (only if the sampler fails): hold each one in the tube for 30 s and read the median from 3 to 33 s. Keep the
  draw speed and volume the same each time. A tube left wet changes the air reading.
- **Dry weight (#30):** filter a measured volume at 3–4 densities spread over the run, at the same time as a Cary draw.

## Open

- Start date, and which days a technician covers.
