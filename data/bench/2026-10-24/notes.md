# Bench sitting 2026-10-24: head screening

22:48 on 2026-10-24 to 00:49 on 2026-10-25. Session 1 proper (references and the kaolin
series) starts fresh in `../2026-10-25/`.

- **Board:** Arduino Nano, `arduino-multichannel` logger, `/dev/ttyUSB0`
- **Adapters:** DFRobot SEN0189 V1.0, switch at A
- **Supply:** `vcc_mv` 4693–4712 (bandgap estimate, not measured with a multimeter)
- **Conditions:** heads dry, in air, on a desk in medium room light. Blocks were an Allen key in the gap for stock heads, and the rod or a hand for the case.
- **Not done:** the multimeter adapter check (probing didn't work well).

## Result

| Head | Status |
| --- | --- |
| TSW-10 (stock) | **Faulty.** Output fixed at ~788 counts whatever the light or the RV pot setting. The fault follows the probe, not the pin or the adapter. Removed. |
| Second TST-10 (stock) | **Faulty.** Fixed at ~709, no response to blocking. Removed. |
| TST-10 (stock) | Good. Air ~978, blocked ~1. |
| New TST-10 (stock) | Good. Air ~630, blocked ~0. |
| Case head | Good. Air ~746, blocked 0. |

Final wiring: **A0** = TST-10 (its probe on the adapter first used for the TSW), **A1** = new TST-10, **A2** = case, **A3** = unconnected. The three working heads are all DFRobot TST-10s; their probe boards have a 150 Ω resistor (marked `151`) in series with the signal, which the TSW-10 and the non-DFRobot heads lack. A3 reads leftover charge from A2 (`00_new_blk_3_baseline`: it fell to ~7 while A2 was blocked), so ignore that column.

## Captures

Counts are 16-read means, from 0 to 1023.

| File | Setup | What it shows |
| --- | --- | --- |
| `00_smoke` | A0 TST, A1 TSW, A2 second TST, A3 case | All four read: 977.0 / 788.2 / 709.9 / 776.7. A2 wandered (std 2.46). |
| `00_block` | same | A0 blocked → 1.0. A3 blocked → 0.0, but came back to ~747, not ~765. A1 and A2 never dropped. |
| `00_unplug` | same | Inconclusive. With its probe unplugged, A1's adapter read ~957, not ~0. |
| `00_swap` | pins swapped A0↔A1, A2↔A3 | Levels followed the heads (A0 785, A1 977, A2 ~740, A3 705), so the pins carry real heads. No blocks. |
| `00_blk_a0` | TSW on A0 | Blocked: flat at 785.1–786.1. |
| `00_blk_probe` | same | TST on A1 blocked → 0.4. TSW on A0 flat at 785.0–785.9. |
| `00_blk_swap2` | probe cables swapped: TSW probe on the A1 adapter | A0 (TST probe, TSW's old adapter) → 1.0. A1 (TSW probe) flat at 787.9–788.9. **The TSW probe is faulty.** |
| `00_blk_a3` | second TST on A3, TSW unplugged | A3 blocked: flat at 708.5–709.1. A1's adapter with no probe read ~958. |
| `00_rv_a1` | TSW on A1 | RV at three positions, light and dark at each: flat at 788.0–789.1. |
| `00_new_a1` | new head on A1, A3 empty | A1 at ~628–631. |
| `00_blk_new_a1` | same | Three blocks of A1 → 0.0–1.5, each recovering to ~629. |
| `00_new_blk_3_baseline` | final wiring | A0 → 1.0, A1 → 0.0, A2 → 0.0. No crosstalk between real heads. |
| `trial_01_air` | final wiring, untouched | 977.8 (std 0.10) / 630.5 (0.35) / 745.8 (0.32) |
| `trial_02_dark` | all three blocked | 6.6 / 1.7 / 0.0 |

An aborted 28-row run (`00_block2`) was deleted.

## Next (2026-10-25)

1. Warm up for 10 minutes, then capture `01_air` and `02_dark`.
2. Capture `03_clear`: the stock heads in blank diluent, covered; the tube syringe-filled. Check A0's level in water: at 972 counts or more it is near full scale.
3. Then `04` and `05`, followed by the kaolin series (`docs/bench/session-1.md`).
