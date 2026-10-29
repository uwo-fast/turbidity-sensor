# Bench session 1: 2026-10-28, new references and repeat 2

Hardware, wiring, diluent and method as in `../2026-10-26/`, with one change: A0's RV
trimmer was turned counter-clockwise (viewed from above) until A0 came off its ceiling in
clear water (`../2026-10-26/notes.md`, captures `40` and `41`). Repeat 1's references in
`../2026-10-25/` no longer apply to A0.

## Captures

Counts are 16-read means, from 0 to 1023. Times are when each capture ended (file times).

| File | Time | Water temp (°C) | A0 | A1 | A2 | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `03_clear` | 00:12 | | 787.0 | 804.7 | 956.1 | All heads in clear covered diluent. Stds 0.30 / 0.30 / 0.10. A0 steady to within 0.4 counts across the 60 s |
| `05_clear_stability` | 00:26 | | 787.0 | 804.7 | 956.0 | As `03`, 600 s. Stds 0.15 / 0.22 / 0.06. Drift, first to last minute: +0.05 / +0.13 / −0.01 |
| `02_dark` | 09:46 | | 0.0 | 0.0 | 0.0 | All heads blocked. 7.0 / 2.7 / 0.0 on 10-25 |
| `10_c0000_r2` | 09:53 | | 786.9 | 804.4 | 958.0 | Repeat 2 blank: 300 mL fresh diluent, fresh 10 g/L stock (3.000 g to 300 mL). Within 1.9 counts of `03_clear` |
| `11_c0025_r2` | 10:20 | | 779.9 | 794.1 | 957.3 | From the blank: A0 −7.0 (−0.89 %), A1 −10.3 (−1.28 %), A2 −0.7. Repeat 1 at 25 mg/L: A1 −0.4 |
| `11_c0025_r2b` | 10:22 | | 778.8 | 793.4 | 958.0 | Heads lifted and tilted to release bubbles, re-stirred. From the blank: A0 −8.1, A1 −11.0 (−1.37 %), A2 0.0. Confirms `11_c0025_r2`, so the drop is not bubbles |
| `11_c0025_r2c` | 10:35 | | 778.7 | 794.6 | 958.3 | Still 25 mg/L: the 50 mg/L addition was missed, and the file was first saved as `12_c0050_r2`. From the blank: A0 −8.3, A1 −9.8 (−1.22 %), A2 +0.3. Three captures at 25 mg/L agree |
| `12_c0050_r2` | 10:42 | | 779.4 | 795.0 | 957.7 | From the blank: A0 −7.5, A1 −9.4 (−1.17 %), A2 −0.3. No further drop from 25 mg/L. First attempt failed (no CSV header within 10 s); retried |
| `13_c0100_r2` | 10:47 | | 779.4 | 793.8 | 958.1 | From the blank: A0 −7.5, A1 −10.6 (−1.32 %), A2 +0.1. Within 1.2 counts of 25 and 50 mg/L |
| `14_c0200_r2` | 10:51 | | 778.8 | 794.0 | 957.9 | From the blank: A0 −8.1, A1 −10.4, A2 −0.1. No change from 100 mg/L. Repeat 1 at 200 mg/L: A1 −4.9 from its blank, about 5 counts below its 100 mg/L reading |
| `15_c0400_r2` | 10:55 | | 772.7 | 789.3 | 957.9 | From 200 mg/L: A0 −6.2, A1 −4.8 (std 1.00, one dip to 782), A2 0.0. First response above the 25–200 mg/L plateau |
| `16_c0800_r2` | 10:59 | | 761.7 | 777.6 | 956.0 | From the blank: A0 −25.3 (−3.2 %), A1 −26.8 (−3.3 %), A2 −2.1. Repeat 1 at 800 mg/L: A1 −29.1 (−3.6 %), A2 −2.3 |
| `17_c1000_r2` | 11:05 | | 752.7 | 773.9 | 955.8 | From the blank: A0 −34.2 (−4.3 %), A1 −30.5 (−3.8 %, std 0.95), A2 −2.2. Repeat 1 at 1000 mg/L: A1 −47.0 (−5.9 %), A2 −3.5 |
| `18_c2000_r2` | 11:12 | | 721.3 | 744.0 | 951.0 | From the blank: A0 −65.6 (−8.3 %), A1 −60.4 (−7.5 %, std 1.02), A2 −7.0 (−0.73 %). Repeat 1 at 2000 mg/L: A1 −101.0 (−12.6 %) |
| `19_c4000_r2` | 11:20 | | 668.0 | 688.6 | 941.8 | From the blank: A0 −118.9 (−15.1 %), A1 −115.8 (−14.4 %), A2 −16.2 (−1.7 %). Repeat 1 at 4000 mg/L: A1 −154.4 (−19.3 %), A2 −17.9 (−1.9 %) |

## Tube head

Room lit, no shade, for every capture in this section. The case shielded its head from room
light on 10-25 (`03_clear` sleeved 956.8, `04_clear_uncovered` 956.7), so the tube readings
should not depend on it; the stock-housing readings here do.

| File | Time | Setup | A2 or A1 in the case | Notes |
| --- | --- | --- | --- | --- |
| `40_a2_rv_clear` | 11:48 | A2's board in the case, clear water | A2 970.8 | A2's RV was already fully counter-clockwise (956 in clear water); this is half a turn clockwise, so clockwise brightens, as on A0 |
| `43_a1_tube_air` | 12:05 | A1's board moved into the case; A2's board out of the case in air | A1 687.3 | A2's board in air, uncased: 896.4 |
| `43_a1_tube_clear` | 12:07 | A1, clear water | A1 953.9 | RV untouched. 1.39 × its air reading |
| `44_a1_tube_rv_clear` | 12:10 | A1, clear water, RV fully counter-clockwise | A1 943.6 | RV cannot bring a board off the ceiling in the tube |
| `45_a1_tube_load_air` | 12:34 | A1, tube empty, RV fully counter-clockwise, **15 kΩ from probe output to GND** on A1's adapter (4.7 kΩ ∥ 15 kΩ ≈ 3.6 kΩ load) | A1 474.5 | |
| `45_a1_tube_load_clear` | 12:36 | As `45_a1_tube_load_air`, clear water | A1 887.0 | Std 0.16. Off the ceiling. Water raised it 1.87 × over air |
| `46_a1_tube_c4000` | 12:39 | As `45_a1_tube_load_clear`, 4000 mg/L kaolin (left over from repeat 2), 60 s | A1 781.2 | −105.8 (−11.9 %) from `45_a1_tube_load_clear`, steady across the 60 s. The case head without the resistor gave −1.7 % at 4000 mg/L; the stock-housing heads −14 to −19 % |

Four captures taken while a load resistor was missing or on the wrong adapter were discarded.

- **Why every board saturates in the tube:** the water-filled tube acts as a cylindrical
  lens and concentrates the beam on the detector. With the load fixed, water raised A1 1.87 ×
  over air in the tube (`45_a1_tube_load_air` → `_clear`), against 1.26 × for A1 in its
  stock housing on 10-25 (A2's 1.28 × that day was in the case, near the ceiling). A 2D ray trace of this geometry (windows ±4.15 mm, 1.4 mm
  wide; FEP tube 7.94 mm OD, 6.35 mm ID; `tools/tube_raytrace.py`) predicts 1.52 ×, the same for emitter half-angles of
  10–45°. The isopropanol test below does not isolate the effect.

### Two tube heads, evening

From here, two cases sit in series on one tube: **A1** (as above) and **A2**, its board back
in a case, set up the same way (RV fully counter-clockwise, 15 kΩ from probe output to GND
on A2's adapter). Every fill reaches both heads at once. A0 stays in its stock housing.

| File | Time | Setup | A0 | A1 | A2 | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `02_dark_tube` | 19:45 | Black-oxide Allen keys as blocks: one through each tube bore, a slightly larger one in A0's gap | 0.0 | 0.0 | 0.0 | 60 s |
| `47_tube_clear_1` | 20:31 | Clear water, fill 1 | 776.1 | 875.5 | 921.7 | Stds 0.26 / 0.28 / 0.11. A3, unconnected, follows A2 (906.0 here, 5.5 in `02_dark_tube`): the ADC's sampling capacitor keeps A2's charge |
| `47_tube_clear_2` | 20:35 | Clear water, fill 2 | 776.6 | 878.6 | 921.3 | Stds 0.24 / 0.21 / 0.10 |
| `47_tube_clear_3` | 20:36 | Clear water, fill 3 | 776.8 | 876.4 | 921.2 | Stds 0.15 / 0.29 / 0.11. Across the three fills: A1 876.9 ± 1.6 (0.18 %), A2 921.4 ± 0.3 (0.03 %) |
| `48_tube_c0250_1` | 23:08 | 250 mg/L standard (300 mL bottle), fill 1; A0 in a 25 mL container of the same standard. File since overwritten (23:50) | 514.7 | 806.2 | 903.6 | From the clear mean: A1 −70.7 (−8.1 %), A2 −17.8 (−1.9 %) |
| `48_tube_c0250_2` | 23:17 | Fill 2. File since overwritten (23:52) | 628.8 | 807.7 | 899.5 | A1 repeats within 1.5 counts; A2 within 4.1. A0 differs by 114 counts between fills, so the 25 mL container is not repeatable |

**A2's load changed to 4.7 kΩ ∥ 6.8 kΩ ≈ 2.8 kΩ** (the 15 kΩ swapped for 6.8 kΩ) after
`48_tube_c0250_2`: A2 sat at 921 in clear water, its fills were unusually steady (0.03 %), and
it gave a quarter of A1's response at 250 mg/L, which points to compression near the ceiling.
On the serial monitor straight after, with the 250 mg/L standard still in the tube: A2 797.0,
A1 809.8. A1's clear reference (`47_tube_clear_1` to `_3`) still applies; A2's is retaken.

| File | Time | Setup | A0 | A1 | A2 | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `47_tube_clear_4` | 23:36 | Clear water, fill 4, A2 on the 2.8 kΩ load; A0 back in clear water (retaken, overwriting a 23:28 capture with A0 still in kaolin) | 635.5 | 878.3 | 861.1 | Stds 0.55 / 0.28 / 0.36. The 23:28 capture read A2 862.2; against A2's 797.0 at 250 mg/L on the monitor, −7.6 %, close to A1's −8 %. A0 read 776.8 in clear water at 20:36, so its small container does not repeat |
| `47_tube_clear_5` | 23:39 | Clear water, fill 5 | 634.9 | 880.1 | 860.9 | Stds 0.22 / 0.13 / 0.09. First attempt failed (no CSV header within 10 s); retried |
| `47_tube_clear_6` | 23:40 | Clear water, fill 6 | 637.4 | 880.8 | 861.1 | Stds 0.56 / 0.14 / 0.09. A1 sits 2.9 above its fills 1–3 mean |
| `47_tube_clear_7` | 23:42 | Clear water, fill 7 | 636.9 | 879.4 | 861.6 | Stds 0.18 / 0.17 / 0.17 |
| `47_tube_clear_8` | 23:43 | Clear water, fill 8. **The file was emptied at 00:43 on 10-29 (0 bytes); the means here, A1 878.946 and A2 861.939, are all that remain** | 637.9 | 878.9 | 861.9 | Stds 0.14 / 0.18 / 0.07. First attempt failed (no CSV header within 10 s); retried. **Clear reference for the standards, fills 4–8:** A1 879.5 ± 1.0 (0.11 %), A2 861.3 ± 0.4 (0.05 %) |

Percentages from here are against the fills 4–8 clear reference.

| File | Time | A1 | A2 | Notes |
| --- | --- | --- | --- | --- |
| `48_tube_c0250_1` | 23:50 | 805.2 (−8.45 %) | 812.2 (−5.70 %) | 250 mg/L, fill 1. Overwrites the earlier `_1` |
| `48_tube_c0250_2` | 23:52 | 805.0 (−8.47 %) | 813.8 (−5.51 %) | Fill 2. A1 std 4.39: something passed through its beam |
| `48_tube_c0250_3` | 23:55 | 801.2 (−8.90 %) | 812.4 (−5.68 %) | Fill 3 |
| `48_tube_c0250_4` | 23:59 | 806.6 (−8.29 %) | 828.2 (−3.84 %) | Fill 4. A2 about 15 counts clearer than fills 1–3 while A1 matches them. First attempt failed (no CSV header within 10 s); retried |
| `48_tube_c0250_5` | 00:01 (10-29) | 799.7 (−9.08 %) | 827.3 (−3.95 %) | Fill 5. A2 stays at fill 4's level: a step between fills 3 and 4, not drift within a capture (no fill drifts more than 1.6 counts on A2). Five fills: A1 −8.64 ± 0.33 %, A2 −4.94 ± 0.95 % |
| `48_tube_c0500_1` | 00:08 | 706.0 (−19.72 %) | 728.7 (−15.39 %), std 26.5 | 500 mg/L, fill 1. A2 wandered 733 → 750, then fell to about 668 in the last 6 s (a bubble or clump reaching its beam); A1 steady |
| `48_tube_c0500_2` | 00:11 | 704.3 (−19.93 %) | 730.6 (−15.18 %) | Fill 2. Both steady |
| `48_tube_c0500_3` | 00:14 | 704.1 (−19.94 %) | 733.1 (−14.89 %) | Fill 3, retaken over a 00:13 capture in which A2 fell from 763 to 414 mid-capture and A1 read −26.2 % (a slug of settled kaolin or air) |
| `48_tube_c0500_4` | 00:16 | 707.4 (−19.57 %) | 733.9 (−14.79 %) | Fill 4 |
| `48_tube_c0500_5` | 00:18 | 708.7 (−19.42 %) | 732.8 (−14.93 %) | Fill 5. Five fills: A1 −19.72 ± 0.23 %, A2 −15.04 ± 0.24 % |
| `48_tube_c1000_1` | 00:25 | 558.8 (−36.47 %) | 589.4 (−31.57 %) | 1000 mg/L, fill 1 |
| `48_tube_c1000_2` | 00:28 | 559.5 (−36.38 %) | 585.3 (−32.05 %) | Fill 2 |
| `48_tube_c1000_3` | 00:30 | 559.0 (−36.44 %) | 583.8 (−32.22 %) | Fill 3 |
| `48_tube_c1000_4` | 00:32 | 558.7 (−36.47 %) | 582.9 (−32.33 %) | Fill 4 |
| `48_tube_c1000_5` | 00:34 | 558.1 (−36.54 %) | 579.2 (−32.75 %) | Fill 5. Five fills: A1 −36.46 ± 0.06 %, A2 −32.18 ± 0.43 %. A2 darkened steadily across the five fills (−31.57 → −32.75 %) |
| `48_tube_c2000_1` | 00:53 | 327.5 (−62.76 %) | 333.5 (−61.28 %) | 2000 mg/L, fill 1 |
| `48_tube_c2000_2` | 00:57 | 324.1 (−63.15 %) | 333.2 (−61.31 %) | Fill 2. First attempt failed (no CSV header within 10 s); retried |
| `48_tube_c2000_3` | 00:58 | 324.2 (−63.14 %) | 332.9 (−61.35 %) | Fill 3 |
| `48_tube_c2000_4` | 01:00 | 322.4 (−63.35 %) | 328.1 (−61.91 %) | Fill 4 |
| `48_tube_c2000_5` | 01:02 | 323.8 (−63.18 %) | 330.0 (−61.69 %) | Fill 5. Five fills: A1 −63.12 ± 0.22 %, A2 −61.51 ± 0.28 % |
| `48_tube_c4000_1` | 01:07 | 126.9 (−85.57 %) | 129.0 (−85.02 %) | 4000 mg/L, fill 1 |
| `48_tube_c4000_2` | 01:10 | 126.4 (−85.63 %) | 128.0 (−85.14 %) | Fill 2 |
| `48_tube_c4000_3` | 01:14 | 126.0 (−85.67 %) | 124.9 (−85.50 %) | Fill 3. A0 132.8 (−79.1 %) |
| `48_tube_c4000_4` | 01:16 | 126.0 (−85.68 %) | 127.0 (−85.26 %) | Fill 4. A0 132.0 (−79.3 %) |
| `48_tube_c4000_5` | 01:17 | 125.3 (−85.76 %) | 125.0 (−85.49 %) | Fill 5 |

### Standards summary

Five fills per point, against each head's clear fills 4–8 (A1 879.5, A2 861.3, A0 636.5; dark
0 for all three). Change in percent, mean ± SD, with attenuation −ln T in brackets. A0 is the
stock-housing head in a 25 mL container of each standard.

| mg/L | A1 (tube) | A2 (tube) | A0 (stock housing) |
| ---: | ---: | ---: | ---: |
| 250 | −8.64 ± 0.34 (0.090) | −4.94 ± 0.95 (0.051) | −23.2 ± 14.1 (not usable) |
| 500 | −19.72 ± 0.22 (0.220) | −15.04 ± 0.25 (0.163) | −20.50 ± 0.13 (0.229) |
| 1000 | −36.46 ± 0.06 (0.454) | −32.18 ± 0.43 (0.388) | −33.20 ± 0.70 (0.403) |
| 2000 | −63.12 ± 0.21 (0.997) | −61.51 ± 0.28 (0.955) | −58.21 ± 0.63 (0.872) |
| 4000 | −85.66 ± 0.07 (1.942) | −85.28 ± 0.21 (1.916) | −79.10 ± 0.12 (1.566) |

A0's 250 mg/L fills range from −11.3 to −45.9 %, while its container handling was still
changing; from 500 mg/L up it is repeatable.

| File | Time | A1 | A2 | Notes |
| --- | --- | --- | --- | --- |
| `49_tube_clear_end` | 01:27 | 881.6 (+0.24 %) | 864.3 (+0.35 %) | Clear water after the standards, DI-flushed. A0 635.4 (−0.18 %). Every head is back within 0.35 % of its clear reference: no drift and no kaolin film over the series |
| `49_tube_ipa` | 01:34 | 907.7 (+2.95 % over `49_tube_clear_end`) | 885.0 (+2.40 %) | 99.9 % isopropanol in place of water. The tube ray trace predicted about +4.6 %. A0, in its 25 mL container of isopropanol, rose +14.4 % with no tube in its path, so something besides the tube's refraction changes too (the emitter is infrared, and water and isopropanol absorb differently there); the test does not isolate the lens effect |
