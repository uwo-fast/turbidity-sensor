# Algae run 2: plan

Run 2 repeats the run-1 growth test (`data/bench/2026-11-05/notes.md`) on a second integration. The same
head and sampler are driven and read by a BREAD DCMT slice instead of a Pi motor HAT and a separate Nano.
The slice's own Nano picks each burst at the edge, and the host logs every reading alongside. Like run 1, it
is meant to show that an uncontrolled, timer-driven sampler can follow a batch culture against Cary OD750. It
also checks the edge picker against the run-1 Python picker on the same raw stream.

## What changes from run 1

| Run 1 | Run 2 |
| --- | --- |
| Pi 4 with an Adafruit 2348 HAT drove the motor; a separate Nano streamed the head over USB | A gen1 DCMT slice with a classic Nano, under Anolis on the same Pi: motor 1 drives the actuator open loop, and port 1 reads the head and the lamp |
| Picking ran in Python on the Pi, over bursts the Pi had started | Picking runs in C on the slice's Nano, in windows gated on motor 1 plus a tail. The host logs every 20 ms reading, so the Python picker can run on the same stream as a reference |
| Idle rows logged at 1 Hz | Every reading logged, idle included: the data for detecting bursts from the signal alone |
| The crank cammed out on 11-15 08:34; the motor's screws worked loose | The N20 stands with its screws along the stroke, gripped by a printed cradle (uwo-fast/syringe-actuator PR #24, merged) |
| The stall went unnoticed until morning | The Anolis run's heartbeat, which is lab setup kept outside this repo; a `no_motion` verdict has to reach it (see Open) |
| A2 stepped about 8–14 counts at each lamp switch, cause open | All-black housing, then the light test below |
| Lamp switch times inferred from the data | Lamp state logged on port 1's terminal B by a light-dependent resistor facing the lamp |
| The air reading is the floor: A2 reads air below about 526 counts (air 466 + `near_air` 60), which the run-1 fit puts at OD 2.53. Run 1 plateaued at 2.2–2.35 | Run to the plateau as in run 1, so the two compare. Mark any sensor point above OD 2.4 as near the air floor |
| Inoculum OD not measured | Same volumes (100 + 100 mL into 3 L BG-11), with the inoculum read on the Cary first |

## Before the culture goes in

1. **Firmware:** flash the slice with the DCMT turbidity build (`gen1_nano_*` variant with the edge picker; env name from
   the DCMT work). Record the DCMT commit, the env and the firmware's sha256, so "what ran" is a commit.
2. **Wiring, by position, not by the gen1 silkscreen** (`Slice_DCMT/docs/hardware-revisions.md`): port 1 is the upper
   encoder header, J3, silked `ENC 2`.
   - Head's adapter: signal to port 1 terminal A (`p1a`, A2), VCC to 5 V, GND to GND.
   - LDR: a divider with a 10 kΩ resistor to port 1 terminal B (`p1b`, A3), taped facing the lamp. Any LDR whose
     resistance under the lamp is near 10 kΩ will do.
   - Actuator motor: motor 1. Port 2: unused.
3. **Actuator:** the N20 in its cradle, set screws tightened until the gearbox cannot move. Run 20 bursts in DI: every
   burst must read `ok`, with the line moving. Start at half duty after a 1 s kick at full, as in run 1 (0.5 on the HAT),
   and check the stroke against run 1's, about 4.3 s a turn at that power. Tighten the cradle's set screws again after the
   first day.
4. **Clear reference:** DI through the head's line, 30 min or more, after the housing is closed. This replaces 854.1,
   which belonged to the run-1 housing and the run-1 Nano.
5. **Light test, in DI, before the culture.** Housing closed, lamp switched by hand 3 times, 30 min on and 30 min off
   each time. In DI there are no cells to respond to light, so:
   - if the step is gone in DI, the run-1 steps were the culture's response;
   - if the step is still there, it is light or the supply reaching the head.

   The LDR gives the switch times to the reading; the test also sets its on/off threshold.
6. **Supply:** in run 1 the Nano's supply stepped about 130 mV at lamp switches. Check whether the slice's backplane
   supply and the lamp share a power strip or circuit, and move one if so.
7. **Schedule, in Anolis:** motor 1 for 18.5 s every 900 s, 1 s at full then the running duty, under the watchdog lease.
8. **Heartbeat:** enable the run's heartbeat after the first burst is logged, and disable it before stopping the run.

## During the run

- **Cary OD750:** two samples per draw, twice a day. Record the depth they are drawn from. Dilute 1:N with
  N = round(OD / 0.25) − 1, taking the OD from the fit on the sensor just before drawing. That puts each read at about
  0.25. For example:

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
- **Reading samples:** read them the same day where possible. If they must wait, record when each was drawn and read;
  the 10-29 re-reads after storage scattered 24 %.
- **DI top-ups:** to the start mark, logged with time and volume, not within 15 min before a Cary draw.
- **Hand draws** (only if the sampler fails): hold each one in the tube at least 33 s and read the median from 3 to 33 s.
  Keep the draw speed and volume the same each time. A tube left wet changes the air reading. Run 1's hand draws were not
  repeatable between groups, so treat them as a fallback, not a reading to compare.
- **Dry weight (#30):** filter a measured volume at 3–4 densities spread over the run, at the same time as a Cary draw.

## Open

- Start date, and which days a technician covers.
- The DCMT turbidity build: the env name, and the contracts op it reports through (`GET_INPUT_SUMMARY` draft).
- How a `no_motion` verdict reaches the heartbeat.
- Whether run 1's daily 12:04 USB drop (four days, 3 aborted bursts) recurs. It was the Nano on the Pi's USB, which the
  slice replaces, but the cause is still unknown.
