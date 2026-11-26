# Algae run 2: plan

Run 2 repeats the run-1 growth test (`data/bench/2026-11-05/notes.md`) with a second hardware integration.
A BREAD DCMT slice drives and reads the same head and sampler, in place of a Pi motor HAT and a separate Nano.
The Nano on the slice picks each burst at the edge, and the host also logs every reading. Like run 1, the run
is meant to show that an uncontrolled, timer-driven sampler can track a batch culture, measured against Cary
OD750. It also compares the edge picker with the run-1 Python picker on the same raw stream.

## What changes from run 1

| Run 1 | Run 2 |
| --- | --- |
| Pi 4 with an Adafruit 2348 HAT drove the motor; a separate Nano streamed the head over USB | A gen1 DCMT slice with a classic Nano, under Anolis on the same Pi: motor 1 drives the actuator open loop, and port 1 reads the head and the lamp |
| Picking ran in Python on the Pi, over bursts the Pi had started | Picking runs in C on the slice's Nano, in windows gated on motor 1 plus a tail. The host logs every 20 ms reading, so the Python picker can run on the same stream as a reference |
| Idle rows logged at 1 Hz | Every reading logged, idle included: the data for detecting bursts from the signal alone |
| The crank cammed out on 11-15 08:34. The motor screws worked loose | The N20 is mounted with its screws along the stroke and held by a printed cradle (uwo-fast/syringe-actuator PR #24, merged) |
| The stall went unnoticed until morning | A heartbeat on the Anolis run (lab setup, kept outside this repo). A `no_motion` verdict has to reach it (see Open) |
| A2 stepped about 10–17 counts (1.3–2.8 %) at each lamp switch, more as the culture grew denser. The cause is unknown. Nothing was black: the sampler case was grey PETG, and its bayonet base and the column lid were clear PETG | Sampler case printed black, with a filament change to clear PETG for the bayonet section that faces the culture, so that no pigment reaches the culture. Then the light test below |
| Lamp switch times inferred from the data | Lamp state logged on terminal B of port 1 by a light-dependent resistor facing the lamp |
| The air reading is the floor: A2 reads air below about 526 counts (air 466 + `near_air` 60), which is OD 2.53 on the run-1 fit. Run 1 plateaued at 2.2–2.35 | Run to the plateau as in run 1, so the two compare. Mark any sensor point above OD 2.4 as near the air floor |
| Inoculum OD not measured. Run 1 reached 4.0 L only with a 1 L BG-11 top-up on 11-08 | 4.0 L from the start: 200 mL of inoculum, read on the Cary first, into 3.8 L of BG-11 (volumes still to be confirmed) |
| Room temperature known only roughly (22–23 °C) | A BME280 on the same I2C bus as the slice logs temperature, humidity and pressure through Anolis |

## Before the culture goes in

1. **Firmware:** flash the slice with the DCMT turbidity build (`gen1_nano_*` variant with the edge picker; env name from
   the DCMT work). Record the DCMT commit, the env and the sha256 of the firmware, so the firmware that ran
   can be traced to a commit.
2. **Wiring, by position, not by the gen1 silkscreen** (`Slice_DCMT/docs/hardware-revisions.md`): port 1 is the upper
   encoder header, J3, silked `ENC 2`.
   - Head adapter: signal to port 1 terminal A (`p1a`, A2), VCC to 5 V, GND to GND.
   - LDR: a divider with a 10 kΩ resistor to port 1 terminal B (`p1b`, A3), taped facing the lamp. Any LDR whose
     resistance under the lamp is near 10 kΩ will do.
   - Actuator motor: motor 1. Port 2: unused.
3. **Actuator:** the N20 in its cradle, with the set screws tightened until the gearbox cannot move. Run 20 bursts in
   DI. Every burst must read `ok`, with liquid moving in the line. Start at half duty after a 1 s kick at full duty, as in
   run 1 (0.5 on the HAT), and check the stroke against run 1: about 4.3 s per turn at that power. Tighten the set screws
   of the cradle again after the first day.
4. **Clear reference:** run DI through the head line for 30 min or more, after the sampler case is closed. This replaces
   854.1, which was measured with the run-1 sampler case and the run-1 Nano.
5. **Light test, in DI, before the culture.** With the sampler case closed, switch the lamp by hand 3 times, 30 min on
   and 30 min off each time. DI has no cells to respond to light, so:
   - if the step is gone in DI, the run-1 steps were a response of the culture;
   - if the step is still there, it is light or the supply reaching the head.

   The LDR records the switch times alongside the reading. The test also sets the LDR on/off threshold.
6. **Supply:** in run 1, the Nano supply stepped about 130 mV at lamp switches. Check whether the slice backplane
   supply and the lamp share a power strip or circuit, and move one of them if so.
7. **Schedule, in Anolis:** motor 1 for 18.5 s every 900 s, 1 s at full then the running duty, under the watchdog lease.
8. **Heartbeat:** enable the run's heartbeat after the first burst is logged, and disable it before stopping the run.

## During the run

- **Cary OD750:** two samples per draw, twice a day. Record the depth they are drawn from. Dilute 1:N with
  N = round(OD / 0.25) − 1, taking the OD from the sensor fit just before drawing. This puts each reading at about
  0.25. For example:

  | Expected OD | Dilution |
  | ---: | --- |
  | 0.4 | 1:1 |
  | 0.8 | 1:2 |
  | 1.2 | 1:4 |
  | 1.6 | 1:5 |
  | 2.0 | 1:7 |
  | 2.4 | 1:9 |

- **Samples to avoid:** do not draw in the first 90 min after the lamp comes on. In run 1, both samples drawn 45–50 min
  after lamp-on were off the fit (11-09 10:20 and 11-11 09:10). The sample drawn at 70 min (11-13 09:38) was on it.
- **Reading samples:** read them the same day where possible. If they must wait, record when each was drawn and when it
  was read. The 10-29 re-reads after storage scattered by 24 %.
- **DI top-ups:** top up to the start mark and log the time and volume. Do not top up within 15 min before a Cary draw.
- **Hand draws** (only if the sampler fails): hold each one in the tube at least 33 s and read the median from 3 to 33 s.
  Keep the draw speed and volume the same each time. A tube left wet changes the air reading. The hand draws in run 1
  were not repeatable between groups, so treat them as a fallback, not as readings to compare.
- **Dry weight (#30):** filter a measured volume at 3–4 densities spread over the run, at the same time as a Cary draw.

## Open

- Start date, and which days a technician covers.
- The DCMT turbidity build: the env name, and the contracts op it reports through (`GET_INPUT_SUMMARY` draft).
- How a `no_motion` verdict reaches the heartbeat.
- Whether the daily 12:04 USB drop in run 1 (four days, 3 aborted bursts) recurs. It affected the Nano on the Pi USB,
  which the slice replaces, but the cause is still unknown.
