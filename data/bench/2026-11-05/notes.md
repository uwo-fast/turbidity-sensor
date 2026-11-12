# 2026-11-05: column setup for the integrated run

Setup record ahead of the first run with the actuator and tube head together. No captures yet.

- **Vessel:** the lab's clear acrylic column, 100 mm bore (7.85 mL per mm of height), sparged from
  the bottom section through two side ports. A `7L` mark is written on the wall.
- **Lid and sampler:** the printed pocket lid from `open-source-bioreactor`
  (`scad/_spikes/column_lid/`), with the sampler (`scad/custom/sampler.scad`) and a syringe actuator
  standing on it. A stand rod steadies the actuator.
- **Fill:** to be topped up with BG-11 growth medium to the line marked by the thumb in
  `photos/fill_line_thumb.jpg`, so the riser is submerged.
- **Light:** a lamp on a clamp behind the column, with a window beside it.

## Photos

| File | Shows |
| --- | --- |
| `photos/column_front.jpg` | The column before the lid went on: plain acrylic top, the culture at its current level with foam on the surface, the lamp, gas lines and rotameter |
| `photos/column_rear_lamp.jpg` | The sampler and actuator on the lid, and green growth on the wall above the culture |
| `photos/sampler_on_lid.jpg` | The actuator, the sampler and the pocket lid; motor and sensor leads not yet connected |
| `photos/fill_line_thumb.jpg` | The fill line, the riser hanging from the pocket's floor, and the growth on the wall |

## First motor runs

A2 in its tube case on `a2` (2.8 kΩ load, as on 10-28), the riser in DI water, motor on M4 of the
Adafruit 2348 HAT, Nano on the Pi's USB at 50 Hz (`vcc_mv` about 4680). 8 s each unless noted, with the
line wet from the 1.0 run on. Band limits are counts: water above 800, air 420–470, dips below 420.
A plateau is at least 100 ms moving under 3 counts row to row.

| File | Throttle | Moved | Water | Air | Dips | On a plateau | Reading after stopping |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| `61_di_m4_t050` | 0.5 (7 s) | No | 0 | 100 % | 0 | 100 % | 442, dry tube |
| `63_di_m4_t060` | 0.6 | Yes | 71 % | 20 % | 6 % | 88 % | 438, air |
| `64_di_m4_t070` | 0.7 | Yes | 61 % | 24 % | 11 % | 71 % | About 246, std 18.7: neither level |
| `65_di_m4_t080` | 0.8 | Yes | 66 % | 18 % | 14 % | 75 % | 851, water, std 0.19 |
| `66_di_m4_t090` | 0.9 | Yes | 19 % | 26 % | 51 % | 28 % | 851, water, std 0.13 |
| `62_di_m4_t100` | 1.0 (6 s, dry line at the start) | Yes | 15 % | 37 % | 42 % | 31 % | 453, air, after a settling transient |

`60_di_t050` is the same 0.5 run on M1, with no motor connected there.

- **Levels:** water 851–852. Dry tube 441–442. Wet air varied by stop and run, 425–453, so the air
  level is not one number. The run before the 0.8 capture left a stop reading about 397 and drifting.
- **Turn time:** about 5 s at 0.6 and about 3 s at 0.8 and 0.9, from a few turns per run, so rough.
- **Column:** water moved as a solid column at 0.6–0.8, by eye.

### Low speed and restarts

| File | Throttle | Result |
| --- | ---: | --- |
| `67_di_m4_t050_wet`, `68_di_m4_t055` | 0.5, 0.55 (10 s) | Flat at 851. Not watched |
| `69_di_m4_t050_watched`, `70_di_m4_t055_watched` | 0.5, 0.55 (10 s) | Flat at 851. Crank seen still at both |
| `71_di_m4_t065_30s` | 0.65 (30 s) | Water 77 %, air 13 %, dips 7 %, 83 % on plateaus. About 4.4 s a turn over four turns. First air crossing at 8.4 s; the crank was seen to hesitate at the start |
| `72_di_m4_t065_start1` to `5` | 0.65 (6 s each) | All five show an air crossing, so all five started. Seen to struggle a little |

| `73_di_m4_t070_30s` | 0.7 (30 s) | Water 69 %, air 14 %, dips 15 %, 72 % on plateaus. About 4.1 s a turn over seven turns, first air crossing at 1.7 s. One messy turn at about 17.5–20 s |
| `74_di_m4_t070_start1` to `5` | 0.7 (5 s each) | All five show an air crossing. Stops: 3 in water, 1 in air (440), and start3 at about 370–470 for 1 s, then 850 from 1.2 s on |

So the motor starts between 0.55 and 0.6, and 0.65 is near that edge. Supply voltage not recorded.

**Where the stops landed**, over the 11 runs at 0.6 and above: 6 in water at 850–851, 2 in air (438, 453),
and 3 on neither level, reading about 246, 304 and 862. These do not hold steady: the 246 stop had reached
about 397 by the next run, the 304 stop about 297, and the 862 stop about 891, which reads above clear water.

## Column, DI water, air on at 1 vvm

Logger on the column from 17:12, data in `~/rig-data/water-clay/` on the Pi, 5 minutes a cycle. No air-off
baseline in the column was taken.

- **Stalls at 0.7:** 3 of the first 8 bursts stayed flat (17:12, 17:39, 17:44). The motor was seen humming
  with the crank still on a later burst, and moved at 0.7 in other tests from other rest positions.
- **Kick, from 18:03:** each start runs 1 s at 1.0, then 0.7. The first 6 bursts all moved, at about
  4.1–4.3 s a turn, and all 6 read `ok`, after 5 nudges in total.
- **Water level:** 851.0–851.8 in those 6, against 850.2–851.3 with no air in a beaker.
- **Spikes in still readings:** single rows far below water, down to 147 counts, 4 in those 6 cycles. Possibly
  bubbles rising past the beam; not identified. They raise `still_std` to 5–18, but the median does not move.

## Algae run 1: media and inoculation

Logger data in `~/rig-data/algae-run-1/` on the Pi, 2-minute cycles while inoculating, from 19:01.

- **Media:** 3 L of BG-11, swapped in for the DI water. Clear reference from 5 cycles, 19:01–19:10: 851.4–852.7.
- **Inoculum:** 100 mL into the 3 L, so about 1:31, taken from a denser culture on hand, not the 10-29 master. Its OD
  was not measured. Time not recorded: the reading places it between about 19:10 and 19:11.
- **First response:** the still reading stepped from 851.4 (cycle ending 19:10:18) to 844.3 and 844.9 (cycles
  ending 19:12:18 and 19:14:18), about −0.9 %, with no nudges.
- **Second inoculum:** another 100 mL of the same culture, so 200 mL in about 3.2 L, about 1:16. Time not recorded yet.
  The still reading stepped to 836.4 and 837.9 (cycles ending 19:20 and 19:21).
- **Throttle to 0.8, from the next restart after 20:04:** every burst up to then ran at 0.7. The 19:17 burst moved
  in only 11 of 37 half-second windows, against 25–32 before it. Suspected cause, not measured: a warm motor and
  a wet seal leave less margin than the first dry test.
- **Rig moved to another bench for the week, about 19:25–19:58:** cycles ending 19:27–19:58 read about 205–214 with std about 40, verdict
  `no_rows` or `aborted`: not culture readings, exclude them. `vcc_mv` rose to about 4830–4920 from about 4690.
  USB unplugged about 19:58; the logger relinked by itself at 19:58:30.
- **After the move:** still 843.8 and 842.3, air 466, against about 837 and 441 before. No head, wiring or culture
  change was reported, so the step is not growth. Treat the 852 clear reference as not comparable across the
  move; the run's baseline starts here.
- **OD750 of the culture:** 0.3583, Cary 50, screen stamp 21:52:42, about 20:52 by the Pi's clock: the Cary reads one
  hour ahead (`photos/cary50_od750_culture.jpg`). Blanked with DI water, reading −0.0002. Where the sample was drawn is not
  recorded yet. The sensor read 838.0–840.1 around then.
- **Against 10-29:** with the 10-29 ODs as corrected on 11-07, A2's 10-29 readings give about −2.5 % at OD 0.358. Before the
  move it read −1.7 % on this culture (837 against 852); the OD was read about 90 min later, after the move. The doses imply
  an inoculum of about OD 5.7, which is not a measurement.
- **A1 as a control:** head in clear DI in its tube case on `a1` from about 21:13, not touching the column. Settled to
  879.1–879.3 from 21:15 to 22:52, std about 0.25.
- **Sampler failure, about 22:02–22:10:** A2 read 835–840 in `ok` cycles until 22:01. The 22:02 and 22:04 bursts stayed
  flat in sample. The 22:06 burst moved between 849 and 904 with no air. From 22:10 it reads air only, at first 469, then
  decaying from about 495 to 482, with no liquid at the beam. **Exclude A2 data from 22:02 until fixed.**
- **Cause found by eye, late evening:** the crank is camming out on the motor shaft. Logger stopped for the night, to fix
  the crank in the morning. Whether this also explains the earlier stalls and the 22:10 loss of draw is not yet checked.

### Restart, 2026-11-06 evening

- **Gap:** no usable A2 data from 22:02 on 11-05. The logger stopped at 23:53. Cycles from about 23:35 read exactly 0.0.
- **Actuator:** revised to a shorter 5 mL syringe (`5ml-gnr2`, syringe-actuator `baf411d`) with a new crank and rod,
  about 5.2 mL a stroke at the nominal bore, against 5.8. Head, tube, riser, case and wiring reported untouched.
- **Causes of the friction, as found at the bench:** (1) overtightening the crank's set screw tips the crank out of
  flat, which adds friction through the mechanism; (2) isopropanol put through the syringe days earlier likely degraded
  the barrel and/or the stopper, adding more. Together these led to the crank camming out. Replacement syringes
  came in a different size, hence the new preset and reprint. The extra friction may also explain the stalls at 0.7,
  and the 0.55–0.8 throttle findings, so those limits may not carry over to the revised unit.
- **Culture:** reported healthy, air on throughout the gap.
- **Data:** continues in `~/rig-data/algae-run-1b/`, starting at 2-minute cycles. A1 read 880.6 in DI at 22:20, and A2
  425 with the tube empty.
- **OD750, 11-06:** 0.4624 against DI (blank read 0.0007), screen stamp 23:32:10, about 22:32 by the Pi's clock if the Cary
  is still an hour ahead (`photos/cary50_od750_culture_1106.jpg`). Two separate samples, 0.4624 and 0.4553 (read 3 in `photos/cary50_od750_culture_1107.jpg`), then combined into A1. From 0.3583 about 25.7 h earlier.
- **Hand-filled A1 on that sample:** about 829.9 at 22:46, against 880.6 in DI at 22:20: −5.8 %. `vcc_mv` also fell,
  from 4855 to about 4650, so this needs a fresh A1 clear reading. A1's 10-29 readings, with the corrected ODs, give about −2.9 % at this OD.
- **A2 through the rig, first cycle:** sample 833.2, air 457, still 833.8, `ok`. Against 852 before the move, about −2.1 %.
- **A1 settled:** fills 1–3 read about 829–830 at `vcc_mv` about 4673. DI clear refill, 868.1 at about 4635, std small, from
  22:56. So about −4.4 % as read, about −4.7 % allowing for the supply. Between 880.6 at 4855 and 868.1 at 4635, A1's clear
  moved about 0.3 % per 1 % of supply.
- **Comparison, same culture, OD 0.4624:** A1 hand-filled about −4.5 %; A2 through the rig about −1.8 % (852 scaled to the
  present supply); A1's 10-29 response, corrected, about −2.9 %. A2's cycles at 0.7 from 22:56: stops needed nudges, 833–836 when `ok`.
- **Sample site:** the 0.4624 sample was taken by pipette a couple of centimetres below the sampling tube, so column
  stratification does not explain A2 reading less than A1. Why A2 responds about half as much as hand-filled A1 is still
  open. To check without using culture: A2's clear reference through its line at the end of the run, then A1 and A2
  side by side on the same standards.
- **A2 clear through its own line, 11-06:** riser in a beaker of DI, about 23:19–23:25, A1 unplugged. 864.4 and 863.9
  (std about 0.2) in `ok` cycles, at `vcc_mv` 4712. This replaces the 852 from before the move. Against the culture at about
  834.5: about −3.1 to −3.4 %, not −1.8 %. Compared with hand-filled A1 at about −4.5 to −4.7 %, the gap is about 1.3 points;
  A1 and A2 differed by up to 1.5 points on the 10-29 series. The −1.8 % figure above came from the stale reference.
- **A2 opened and checked, 11-06, about 23:29–23:38:** taken apart, optical tube wiped with a Kimwipe, reassembled, A1 plugged
  back in. Cycles ending 23:30–23:38 read 0.0: exclude. First DI cycle after: sample 855.7, still 852.9, air 432, at `vcc_mv`
  4635. A1 in DI at the same supply: 870. **A2's clear reference for culture read after this point is this new one,** not 864;
  culture readings from before use 864.
- **Final clear reference after reopening, DI, 23:41–00:34:** A2 854.1 ± 0.7 over the last 8 accepted cycles from 00:16 (853.5 ±
  0.9 over all 13), A1 872.6, `vcc_mv` about 4635–4654, A1 connected. Accepted means steady and within 5 of that burst's
  sample level. A2/A1 stayed at 0.979–0.980 (std 0.0007) while both rose about 0.3 %, so the rise is shared. Rejected stops read
  steadily as low as 814–838 in plain DI, so a steady still reading alone does not mean water.
- **Line behaviour changed after reopening:** bursts show few air stretches and more dips, against 7 or so air stretches per burst
  before, probably less air in the line. To restore before culture: drain the line, set the plunger fully in, then re-immerse.
- **Back in culture, 11-07 from 00:38, after draining the line as for DI:** liquid at the beam 13–17 % of each burst, against 34–50 %
  for the same culture, air and syringe at 22:46–23:05, and 46–82 % in DI. Brief culture plateaus read about 827–831, about
  −3 % against the 854.1 clear. Not explained. Between the two culture periods: A2 reopened, tube wiped, riser out and in.
- **Logger bug, fixed in `rig.py`:** the cycle ending 00:53 read `ok` at 444.8, which is air, because a dip was taken for air and
  air for the sample. **Exclude it.** It is the only `ok` row under 700 counts across the water, first and second algae runs.
- **Stop-and-read removed, 11-07 01:41:** the logger now only runs the motor on a timer, logs, and picks the culture from each
  burst's steady stretches. New data in `~/rig-data/algae-run-1c/`, throttle 0.5, 15-minute cycles. On the 11-05 run, 66 bursts
  good by both methods differ by a median of −0.09 counts (std 0.74). The picks for the old runs are in `~/rig-data/picked/`.
- **OD750, 11-07 morning:** 0.3997 and 0.3810 from two samples, blank −0.0020 after, in the same report as 11-06's reads
  (`photos/cary50_od750_culture_1107.jpg`). Mean 0.390, against 0.459 the night before: about 15 % lower. A2's picked readings rose over
  the night, from about 832 to about 840–855, which also means a thinner sample.
- **Picking fixed, 11-07 12:57:** wet air reached 494–520, above the old ±25 band, and outweighed the culture in one burst (504.8).
  Now `near_air = 60` and plateaus more than 15 from the culture's common level are dropped. Re-picking changed nothing in
  `algae-run-1`; in `algae-run-1c`, 504.8 became 835.7 `thin` and 4 more `ok` became `thin`. Re-picked runs in `~/rig-data/picked/`.
- **Cary against the sensor's picks** (A2, `ok` medians in a window around each read; % against 864 for Thu and Fri, 854.1 for Sat,
  not corrected for supply):

  | Cary read | OD750 | Bursts `ok` | A2 median | Change | `vcc_mv` |
  | --- | ---: | ---: | ---: | ---: | ---: |
  | Thu 11-05 20:52 | 0.358 | 35 | 839.4 | −2.9 % | 4855 |
  | Fri 11-06 22:32 | 0.459 | 8 | 833.1 | −3.6 % | 4654 |
  | Sat 11-07 12:45 | 0.390 | 1 | 837.4 | −2.0 % | 4772 |

  Thu and Fri share A2's 864 clear reference, measured Fri 23:19–23:25; Sat follows the reopening. Not yet a calibration.
- **10-29 OD labels corrected, 11-07:** the 10-29 bottles, re-read on the Cary after a week in the fridge, gave `c0063` 0.3064,
  `c0125` 0.5223 and `c0250` 0.9504 (undiluted, near the Cary's top), about twice what 10-29 recorded under those labels. The
  10-29 Cary reads were each one bottle down: the cuvette series' stock was `c0500`, not `c1000`, and the two direct reads were
  `c0063` and `c0250`. Corrected in `../2026-10-29/cary50_od750.md` and `cell_count.md`; the sensor readings are unchanged. With
  the corrected ODs, 10-29 gives about −3.5 % (A2) and −2.9 % (A1) at OD 0.459, against −3.1 to −3.4 % (A2, through the rig)
  and −4.5 to −4.7 % (A1, hand-filled) on 11-06.
- **Diluted re-reads, 11-07:** `c0250` 1:1 in supernatant 0.5310 (so 1.06) and `c0500` 0.4923 (recorded as 1:4, multiplied by 4 to 1.97, so the dilution is not certain). Re-read 1:7 on 11-09: 0.2855 and 0.3643 (2.28, 2.91), 24 % apart, probably clumps after the fridge, so not settled and not repeated; the corrected value stays 2.22 from the 10-29 fit, against 1.11 and
  2.22 from the corrected 10-29 fit and 0.556 and 1.11 under the old labels. Each level about doubles the one below (1.70, 2.03,
  1.85). `c0500` reads lowest, likely from clumping in the fridge that vortexing did not fully break up; read several times.
- **OD750, 11-07 evening, about 19:00–19:25 by the Pi's clock:** 0.4867 and 0.4773 from two 1.4 mL samples at about the
  sampling tube's depth; mean 0.482, up about 24 % from 0.390 that morning. Predicted from the sensor before the read: 0.48–0.64,
  most likely about 0.53, from A2 at about 826–831 (17:00–18:45) against about 837 in the morning. Level marked and photos taken.
- **Overnight 11-07 to 11-08:** A2 fell from about 828–832 (19:00–20:00) to about 814–822 (midnight to 06:00). Delivery recovered
  by itself: from about 04:00 nearly every burst is `ok`, with 40–97 rows. From about 05:00 to 09:13 A2 rose again, from about 815
  to 826–828, with no addition.
- **OD750, 11-08 about 10:15:** 0.5653 and 0.5553, mean 0.560.
- **BG-11 top-up, 11-08 10:20:** 1 L added; level re-marked. A2: 827.9 at 09:13, then 832.3 (10:28, 215 rows) and 830.8 (10:43,
  226 rows). Cary at 10:55: 0.4376 and 0.4344, mean 0.436, a drop to 0.78 of 0.560, which a column of about 3.5 L
  before the addition would give.
- **Cary against A2 so far:** 0.390 about 837, 0.436 about 831, 0.482 about 828.5 fall in order; 0.560 sits against about 828 in
  the bursts just before it, but about 815–821 in the early morning. The 05:00–09:13 rise is not explained: the lamp coming
  on, or the change in delivery, are the candidates.
- **Growth test starts 11-08 10:20,** after the BG-11 top-up: fresh volume, well mixed, good delivery, and a Cary anchor of 0.436
  at 10:55. Everything before is setup. From here the level is held at the 10:20 mark with DI water, replacing what evaporates,
  so no more nutrients are added: a batch culture. Photo: `photos/column_1108_after_bg11.jpg`, with the level marks for
  11-07 19:35, 22:00 and 11-08 10:20.
- **First 10.5 h of the test:** every burst `ok`, with 62–226 rows of culture. A2 fell steadily from about 832 (10:28) to about
  800 (20:58).
- **OD750, 11-08 about 23:25, undiluted:** 0.7242 and 0.7018, mean 0.713. A2 at about 793 (23:13). Predicted from the sensor
  before the read: about 0.75–0.85; from a 0.8-day doubling: about 0.68.
- **Same samples diluted 1:1, about 23:30:** 0.3962 and 0.3911, so 0.792 and 0.782, mean 0.787, about 10 % above the undiluted
  read. The 10-29 `c0250` re-read did the same (0.950 undiluted, 1.06 diluted 1:1), so the Cary reads low from about 0.7, well
  below the 0.97 where it clearly saturates. Use the diluted value: 0.787, ×1.8 from 0.436 in about 12.5 h, a doubling time of
  about 15 h. Dilute samples to read about 0.5 or below from here; Saturday's undiluted 0.560 may be slightly low.
- **Lamp switch times, 11-08/09:** off at 00:00, on at 09:30 (meant 08:00). Neither head steps at the switch second in the 1 Hz
  rows between bursts (A1 about 880.5–881.6 across both), so no direct leak of lamp light is seen. But A2's picked culture
  level moved at the first burst after each switch: about 793 before 00:00 to about 785 at 00:13, rising slowly to about 795 by
  09:28; about 795 before 09:30 to about 807 at 09:43, then 806 and 804. Cause not known.
- **OD750, 11-09 10:20:** diluted 1:1, 0.4043 and 0.4004 (×2: 0.809, 0.801); diluted 1:2, 0.2819 and 0.2725 (×3: 0.846, 0.818).
  The 1:2 reads come out about 3 % above the 1:1, so the Cary already reads slightly low near 0.40: dilute to about 0.2–0.3.
  About 0.80–0.83, up 2–6 % from 0.787 at 23:30, while A2 read about 804 at 10:13 against about 793 then: on this night the
  two disagree in direction.
- **Power blip, 11-09 about 12:00:** the Pi rebooted and the logger and page restarted by themselves (enabled at boot), with
  about 2 min of data missing, from after the 11:58 burst to 12:00:48. Bursts resumed at 12:04, every one `ok`. 17 rows written
  before the clock synced carry `clock_synced` 0. One 2 s loss of the Nano at 12:05, relinked by itself (and one on 11-08 at
  15:01). The lamp, on its own supply and a manual timer, went off with the blip and stayed off until switched back on at 14:10.
- **Air lost with the blip, 11-09:** the building air supply also stopped at about 12:00 and did not come back. Electric air pumps
  were set up to give about 1 vvm again; the time air resumed is not recorded, and the data suggests about 16:45. With no
  air, 12:04–16:34, A2's picks stayed smooth (std 2–4). From 16:49 to about 18:19 they turned spiky (772–787, std 4–8) and most
  bursts showed no steady air level; from 18:34 they settled again (std about 2.4, about 774). Treat 12:00–18:30 on 11-09 as
  disturbed: no mixing for about 4.5 h, then a new air supply settling in.
- **OD750, 11-09 19:24:** diluted 1:2, 0.3227 and 0.3267 (×3: 0.968, 0.980), mean 0.974, up about 17 % from 10:20 across the
  outage. A2 read 769.4 at 19:19 and 764.1 at 19:34, falling steadily with the lamp on.
- **DI top-up, 11-09 19:38:** 150 mL of DI water, back to the 11-08 10:20 mark. The column holds just under 4 L, the volume now
  held. Expected dilution about 3.7 %, OD about 0.974 to 0.938.
- **OD750, 11-09 23:03:** diluted 1:3, 0.2492 and 0.2309 (×4: 0.997, 0.924), mean 0.960; the two differ by about 8 %, more than
  usual. A2 read 762.0 at 22:49 and 762.4 at 23:04.
- **Lamp off, 11-09 23:46.** All 95 bursts on 11-09 up to then read `ok`, with at least 70 rows of culture.
- **Lamp on, 11-10 08:26.** The 23:46 lamp-off gave 760.4 to 749.6 at the 23:49 burst, then A2 rose slowly to about 764 by 06:49.
- **OD750, 11-10:** diluted 1:4. At 10:05, 0.2101 and 0.2128 (×5: 1.051, 1.064), mean 1.057, with A2 about 761.7. At 11:36, 0.2218 and
  0.2212 (×5: 1.109, 1.106), mean 1.108, with A2 about 752.
- **Unexplained step, 11-10 07:04:** A2 764.8 to 752.3, with the lamp off. The 08:26 lamp-on then gave 758.8 to 769.3 at the 08:34 burst.
- **OD750, column U3, 11-10 21:40:** diluted 1:4, 0.2811 and 0.2882 (×5: 1.406, 1.441), mean 1.423. A2 713.4 at 21:34, 713.8 at 21:49.
- **OD750, column U3, 11-11 09:10:** diluted 1:4, 0.1789 and 0.1811 (×5: 0.895, 0.906), mean 0.900, lower than the night before.
  A2 727.6 at 09:04, 724.1 at 09:19.
- **Lamp switches 11-10/11, on the 16/8 timer started 11-10 08:26, read from the data:** off between 00:19 and 00:34 (A2 −12.6 at
  the 00:34 burst; timer due 00:26), on between 08:19 and 08:34 (+13.9 at 08:34; timer due 08:26). A one-burst spike at 04:34
  (+18.8, back −13.2 at 04:49) is not a switch: probably a bubble or clump.
- **OD750, 11-11 21:38:** diluted 1:4, 0.3026 and 0.3021 (×5: 1.513, 1.511); the same samples diluted 1:5, 0.2508 and 0.2528 (×6: 1.505,
  1.517). Mean 1.512; the two dilutions agree within 0.1 %, so the Cary is linear at 0.25–0.30. A2 676.3 at 21:34, 673.6 at 21:49.
- **DI top-up, 11-11 21:54:** 200 mL of DI water, back to the 11-08 10:20 mark, the same mark as the 150 mL top-up on 11-09.
- **After the 21:54 top-up:** A2 673.6 (21:49), 680.5 (22:04), 682.3 (22:19): about +7 to +9, thinner, as a dilution of about 5 % should.
- **OD750, 11-11 22:36:** diluted 1:4, 0.3071 and 0.3061 (×5: 1.536, 1.531); 1:5, 0.2598 and 0.2586 (×6: 1.559, 1.552). Mean 1.544,
  about 2 % above 21:38, where the top-up predicts about 1.43–1.45. The Cary's blank had shifted by about 0.01 when re-zeroed
  before this set, enough at these readings to account for most of the gap; not used as a dilution check. Samples kept in the
  fridge, dated, to re-read on another instrument.
- **The lamp steps, four times now:** A2's culture level falls at the first burst after the lamp goes off and rises at the first
  burst after it comes on: 00:00 off, about 793 to 785; 09:30 on, about 795 to 807; about 12:00 off, 791.8 to 781.4; 14:10 on,
  781.8 to 794.5. With the lamp off it holds nearly flat (779–782 from 12:04 to 14:04).
- **Lamp:** 16 h on, 8 h off, on a manual timer set to roughly match daylight. Switch times to be confirmed.
- **Cary 50 clock:** one hour ahead since the change to standard time on 11-01; right on 10-29. Subtract an hour from Cary
  stamps from 11-01 on.
- **Rig data in this folder:** `rig-data/<run>/` holds each run's raw logs (gzip), `summary.csv` and `events.csv`, a snapshot to
  11-12 00:19 for `algae-run-1c` and to 11-09 23:19 for the others; `rig-data/picked-<run>.csv` is the picking at that date applied to each run. `80`–`82` and `90` are the column
  diagnostics and live reads from the Pi.

## Read from the photos, not measured

Scaled from the column's width in the pictures, so good to a few centimetres at best. Replace these
with tape-measure figures (`docs/bench/sampler-waveform.md`, step 0).

- **Volumes:** the culture stands at about 5 L now and the fill line is at about 8 L, which would
  dilute it to about 0.6 ×.
- **Riser:** its lower end looks close to the fill line.
- **Headspace:** the pocket's floor is about 85 mm above the fill line.
- **Side port:** the hex plug in `column_front.jpg` sits about 170 mm below the top flange, near the
  fill line.
