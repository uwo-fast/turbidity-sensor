# Bench session 2: 2026-10-29, *Chlorella vulgaris*

Hardware, wiring and heads as in `../2026-10-28/`: A0 in its stock housing in a 100 mL beaker,
A1 and A2 in tube cases with their load resistors (15 kΩ and 6.8 kΩ) and RV as set there. Bin
over the heads, lights off, shades drawn. Both tube units (case, tube and syringe) were cleaned
and reassembled since 10-28.

- **Culture:** *Chlorella vulgaris*, from the prof. Part of it was centrifuged and resuspended
  in supernatant to make the denser levels.
- **Diluent, clear reference and Cary blank:** the culture's own supernatant. It is mostly DI
  water with nutrients (recipe to come from the prof).
- **Levels:** the `_c` number is per-mille of the culture as grown: `c1000` is the culture as
  grown, `c0063` is 0.0625 of it, `c4000` is 4 times as dense.
- **OD750:** `cary50_od750.md`. **Cell count:** `cell_count.md`.
- **Photos** (`photos/`): the series in 50 mL conical tubes, light to dark green from
  `c0063` to `c4000` (`series_tubes_side`, `series_tubes_front`), and the `c0063` tube on a
  vortex mixer (`c0063_tube_vortex`).

## Preview (A1 only)

With the prof, before the series. A1 in its tube; A0 not in the culture; A2 not connected, so
its column (and A3's) is leftover charge, not a reading. Dark 0, from 10-28.

| File | Time | A1 | Change from clear | Notes |
| --- | --- | ---: | ---: | --- |
| `50_preview_clear` | 11:32 | 866.0 | | Clear fill |
| `50_preview_culture_1` | 11:37 | 460.2 | −46.9 % | Culture as grown |
| `50_preview_culture_2` | 11:39 | 465.7 | −46.2 % | Refill |
| `50_preview_culture_3` | 11:41 | 463.6 | −46.5 % | Refill. Three fills: −46.5 %, attenuation 0.626 |
| `50_preview_culture_p50` | 11:47 | 655.2 | −24.3 % | Culture at 50 %; attenuation 0.279 |

## References

60 s captures (`53_supp_clear5` 54 s), all three heads at once.

- **Dark** (`51_dark.txt`): Allen keys in both bores and in A0's gap, read on the serial
  monitor. A0, A1 and A2 at 0.00 throughout, as on 10-28. Dark is 0 for all three.

| File | Time | A0 | A1 | A2 |
| --- | --- | ---: | ---: | ---: |
| `52_di_clear` | 13:12 | 808.0 | 872.6 | 850.0 |
| `53_supp_clear1` | 13:23 | 809.9 | 874.6 | 852.0 |
| `53_supp_clear2` | 13:25 | 810.6 | 875.0 | 850.0 |
| `53_supp_clear3` | 13:27 | 811.3 | 875.5 | 850.0 |
| `53_supp_clear4` | 13:29 | 811.8 | 875.7 | 850.0 |
| `53_supp_clear5` | 13:30 | 810.9 | 875.8 | 848.1 |
| Supernatant, 5 fills | | 810.9 ± 0.7 | 875.3 ± 0.5 | 850.0 ± 1.4 |

- **Supernatant against DI:** +0.4 % (A0), +0.3 % (A1), 0.0 % (A2). It reads as water.
- **Tube heads after reassembly:** DI reads 0.8 % (A1) and 1.3 % (A2) below 10-28 (879.5,
  861.3). The series uses this day's supernatant references.
- **A0:** DI reads 808.0, against 636.5 on 10-28. A0's clear moved by that much during 10-28
  too (776.8 at fill 3, 635.5 at fill 4), so A0 compares only within a session.

## Series

The levels are in separate bottles and one head ran at a time: each head got its own five
fills of a level, one after another, the sample mixed before each fill. Each capture is 60 s.

`per_head/` holds each head's raw captures, with the other heads unplugged (0, or a few
counts of leftover charge). `54_alg_c<level>_<fill>.csv` merges fill n of each head into one
file, each column from that head's own capture; the rows were not taken at the same time, and
the merged files hold no `vcc_mv` or `adc_counts_a3`.

A1's first five `c0063` fills (17:17–17:28, 872.0–872.4, −0.35 %) were drawn without mixing
in the syringe; they are kept in `per_head/unmixed/` and not used.

| Level | Head | Captured | Five fills | Mean | Change from supernatant |
| --- | --- | --- | --- | ---: | ---: |
| `c0063` | A2 | 17:35–17:41 | 837.9, 834.1, 836.3, 836.6, 835.2 | 836.0 | −1.65 % |
| `c0063` | A0 | 17:44–17:50 | 786.9, 783.4, 782.8, 782.8, 783.4 | 783.9 | −3.33 % |
| `c0063` | A1 | 18:00–18:10 | 863.6, 866.1, 864.5, 866.1, 865.4 | 865.1 | −1.16 % |
| `c0125` | A2 | 18:15–18:27 | 813.8, 811.1, 811.5, 811.6, 809.9 | 811.6 | −4.52 % |
| `c0125` | A1 | 18:32–18:39 | 841.2, 840.9, 841.0, 842.7, 841.6 | 841.5 | −3.86 % |
| `c0125` | A0 | 18:41–18:51 | 752.1, 752.3, 743.0, 750.0, 749.7 | 749.4 | −7.58 % |
| `c0250` | A2 | 19:00–19:06 | 751.4, 749.3, 751.0, 749.7, 750.1 | 750.3 | −11.73 % |
| `c0250` | A1 | 19:09–19:20 | 761.3, 760.9, 779.4, 772.2, 764.2 | 767.6 | −12.30 % |
| `c0250` | A0 | 19:28–19:34 | 674.8, 675.9, 674.9, 674.5, 674.4 | 674.9 | −16.77 % |
| `c0500` | A2 | 19:39–19:46 | 628.2, 627.8, 627.5, 626.3, 627.4 | 627.4 | −26.18 % |
| `c0500` | A1 | 19:50–19:56 | 656.6, 660.3, 658.9, 659.9, 661.6 | 659.5 | −24.66 % |
| `c0500` | A0 | 20:00–20:06 | 591.2, 590.5, 590.3, 590.1, 590.8 | 590.6 | −27.17 % |
| `c1000` | A2 | 20:10–20:15 | 439.8, 440.0, 439.1, 440.1, 440.0 | 439.8 | −48.26 % |
| `c1000` | A1 | 20:18–20:24 | 462.6, 464.4, 460.7, 463.4, 463.9 | 463.0 | −47.10 % |
| `c1000` | A0 | 20:27–20:33 | 437.9, 444.1, 439.1, 439.2, 438.8 | 439.8 | −45.76 % |
| `c2000` | A2 | 20:36–20:41 | 240.1, 238.3, 240.1, 238.8, 238.9 | 239.3 | −71.85 % |
| `c2000` | A1 | 20:44–20:50 | 250.2, 250.8, 251.6, 253.1, 252.3 | 251.6 | −71.26 % |
| `c2000` | A0 | 20:58–21:13 | 218.5, 220.6, 220.8, 224.1, 224.6 | 221.7 | −72.66 % |
| `c4000` | A2 | 21:48–21:55 | 102.1, 102.4, 104.0, 102.5, 105.0 | 103.2 | −87.86 % |
| `c4000` | A1 | 22:00–22:08 | 107.0, 107.0, 106.7, 107.0, 106.7 | 106.9 | −87.79 % |
| `c4000` | A0 | 22:11–22:20 | 136.8, 137.7, 140.5, 132.4, 133.0 | 136.1 | −83.22 % |

The culture as grown read −47.1 % on A1, against −46.5 % in the morning preview.

## End references

Tubes flushed with supernatant first; all three heads at once.

| File | Time | A0 | A1 | A2 |
| --- | --- | ---: | ---: | ---: |
| `55_sup_clear_end` | 22:32 | 814.9 (+0.5 %) | 874.8 (−0.1 %) | 848.6 (−0.2 %) |
| `56_di_clear_end` | 22:36 | 810.4 (+0.3 %) | 874.9 (+0.3 %) | 847.3 (−0.3 %) |

Every head is back within 0.5 % of its start references, so no film built up over the series.
A1's noise within each end capture was 6.7–7.2 counts (864–886), against 0.2–0.8 earlier.

## Open

- The medium recipe (from the prof).
- Whether tube fills went back to their bottles or were discarded.
- Centrifuge speed, time and volumes for the concentrate.
- Whether `50_preview_clear` was DI water or medium.
