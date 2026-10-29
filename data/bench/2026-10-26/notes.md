# Bench session 1: 2026-10-26, kaolin series

Hardware, wiring and diluent as in `../2026-10-25/`, which also holds the references
(`02_dark`, `03_clear`).

- **Method:** cumulative additions at constant volume (`docs/bench/session-1.md`,
  section 5). Each repeat starts from 300 mL of fresh diluent. At each step, after
  stirring, v mL is removed and v mL of a 10 g/L stock (1.500 g kaolin made up to 150 mL
  with diluent) is added: 0.75, 0.75, 1.51, 3.03, 6.12, 12.50, 6.52 mL for 25 to
  1000 mg/L.
- **Tube flow:** syringe, outlet back into the beaker

## Captures

Counts are 16-read means, from 0 to 1023. Times are when each capture ended (file times).

| File | Time | Water temp (°C) | A0 | A1 | A2 | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `10_c0000_r1_lit` | 21:36 | | 980.2 | 825.4 | 956.0 | Blank, 30 s, room light reaching the beaker. A1 +25.4 counts (+3.2 %) over `03_clear`, std 0.50. Not used |
| `10_c0000_r1` | 21:39 | | 980.1 | 800.4 | 955.6 | Blank, covered. Within 1.2 counts of `03_clear` on every head. A1 std 0.47 (0.16 in `03`) |
| `11_c0025_r1` | 21:45 | | 980.2 | 800.0 | 956.1 | No change from the blank on any head (A1 −0.4, A2 +0.4 counts) |
| `12_c0050_r1` | 21:50 | | 980.3 | 799.3 | 956.2 | From the blank: A1 −1.1 (−0.14 %), A2 +0.5 |
| `13_c0100_r1` | 21:56 | | 980.1 | 799.4 | 955.2 | From the blank: A1 −1.0 (−0.13 %), A2 −0.4 (−0.05 %) |
| `14_c0200_r1` | 22:02 | | 980.3 | 795.4 | 955.8 | From the blank: A1 −4.9 (−0.62 %), A2 +0.2 |
| `20_settling_c0200` | 22:09 | | 980.2 | 794.7 | 955.8 | 300 s still, straight after `14`. Change, first to last minute: A0 −0.02, A1 −0.33, A2 +0.06. No measurable settling |
| `15_c0400_r1` | 23:54 | | 980.0 | 788.8 | 954.0 | From the blank: A1 −11.6 (−1.45 %), A2 −1.6 (−0.17 %), A0 −0.1. Taken 1 h 45 min after `20` |
| `16_c0800_r1` | 00:04 (10-27) | | 979.9 | 646.7 | 952.3 | From the blank: A1 −153.7 (−19.2 %), std 0.96; A2 −3.4 (−0.35 %); A0 −0.3. Not used: the repeat below disagrees |
| `16_c0800_r1b` | 00:06 (10-27) | | 979.7 | 771.3 | 953.4 | Re-stirred, same solution. From the blank: A1 −29.1 (−3.6 %), A2 −2.3 (−0.24 %), A0 −0.4. The A1 drop in `16_c0800_r1` was not repeatable (a dense plume after stirring, or a bubble) |
| `17_c1000_r1` | 00:23 (10-27) | | 979.5 | 753.4 | 952.2 | From the blank: A1 −47.0 (−5.9 %), A2 −3.5 (−0.36 %), A0 −0.6. First attempt failed (no CSV header within 10 s); retried |
| `18_c2000_r1` | 20:37 (10-27) | | 974.0 | 307.5 | 949.1 | 33.33 mL step, about 20 h after `17`. From the blank: A1 −492.9 (−61.6 %), A2 −6.5 (−0.68 %), A0 −6.1, its first clear drop. A1 rose 1.9 counts during the 30 s. Not used: the repeat below disagrees |
| `18_c2000_r1b` | 20:48 (10-27) | | 979.9 | 699.4 | 934.3 | Same solution. Before it: A0 and A1 lifted out, the beaker mixed, the heads rinsed in DI water and bubbles cleared from their gaps with a bare finger, then put back; the tube re-flushed from the mixed beaker. From the blank: A1 −101.0 (−12.6 %), A2 −21.3 (−2.2 %, std 0.99), A0 −0.3 |
| `19_c4000_r1` | 21:07 (10-27) | | 978.2 | 646.0 | 937.8 | 75.00 mL step. From the blank: A1 −154.4 (−19.3 %), A2 −17.9 (−1.9 %, std 1.13, falling 3 counts during the 30 s), A0 −1.9 |
| `30_clear_end_r1` | 22:30 (10-27) | | 980.1 | 800.3 | 956.9 | Fresh diluent, heads and tube rinsed, 60 s. Matches `10_c0000_r1` and `03_clear` within 1.3 counts on every head, so neither the finger contact nor two days on the bench moved them |
| `40_a0_rv_clear` | 22:38 (10-27) | | 980.0 | 633.7 | 739.4 | A0's RV turned slightly, A0 in clear diluent; A1 and A2 out of the water (air readings). A0 unchanged, still at its ceiling |
| `41_a0_rv_clear` | 22:41 (10-27) | | 815.8 | 636.7 | 740.0 | RV turned further counter-clockwise (viewed from above), A0 in clear diluent; A1 and A2 in air. A0 off its ceiling, but rising 810.8 → 821.1 across the 60 s (std 3.9). `vcc_mv` 4754, up about 25 from every earlier capture |

## Observations

- **Bubbles on the stock heads.** After stirring, fine bubbles clung to both lenses and
  filled the gap between them (`photos/heads_bubbles_side.png`,
  `photos/heads_bubbles_front.png`), and the 2000 mg/L beaker carried a thick foam
  (`photos/beaker_foam.png`). Bubbles in the gap most likely caused the low first
  captures at 800 and 2000 mg/L, where A0 and A1 read low together and the repeat did not.
- **Bare-finger contact before `18_c2000_r1b`.** `30_clear_end_r1` matches the
  blank within 1.3 counts, so it left no measurable film on the lenses.
- **The flange does not block light.** It is printed in a translucent material
  (`photos/flange_on_beaker.png`), and the beaker is clear, so "covered" needs an opaque
  cover over the whole beaker.
