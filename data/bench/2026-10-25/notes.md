# Bench session 1: 2026-10-25

Same hardware and wiring as the end of `../2026-10-24/`.

- **Board:** Arduino Nano, `arduino-multichannel` logger, `/dev/ttyUSB0`
- **Adapters:** DFRobot SEN0189 V1.0, switch at A
- **Supply:** `vcc_mv` 4712–4732 (bandgap estimate, not measured with a multimeter)
- **Heads:** **A0** = TST-10 (stock, in a covered beaker), **A1** = new head (model not recorded), **A2** = case head (tube), **A3** = unconnected, ignore it
- **Diluent:** 0.01 % v/v Tween 20 in DI water, from a 1 % stock (`docs/bench/session-1.md`, section 5)
- **Tween 20 (product, lot):**
- **Kaolin (product, lot):**
- **Tube flow:** syringe

The references end at 01:02 on 10-26. The kaolin series continues in `../2026-10-26/`.

## Captures

Counts are 16-read means, from 0 to 1023. Times are when each capture ended (file times).

| File | Time | Water temp (°C) | A0 | A1 | A2 | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `01_air` | 10:28 | | 977.8 | 635.5 | 748.6 | Heads dry |
| `02_dark` | 11:51 | | 7.0 | 2.7 | 0.0 | Blocked |
| `03a_clear_di` | 19:07 | | 980.6 | 804.8 | 947.2 | Plain DI water, no Tween, uncovered. A2 std 1.83, noisier than A0 (0.13) and A1 (0.43) |
| `04_clear_uncovered` | 00:38 (10-26) | | 980.2 | 806.2 | 956.7 | Diluent, uncovered. Stds 0.11 / 0.42 / 0.12. Taken before `03`, and saved as `03_clear` at first, then renamed |
| `03_clear` | 00:49 (10-26) | | 980.2 | 800.0 | 956.8 | Diluent, covered and sleeved, same fill as `04`. Stds 0.09 / 0.16 / 0.09 |
| `05_clear_stability` | 01:02 (10-26) | | 980.2 | 800.1 | 956.5 | As `03`, 600 s. Stds 0.09 / 0.20 / 0.12. Drift, first to last minute: 0.00 / +0.25 / +0.12 |

## Observations

- **A0 (TST-10) is saturated in clear water.** From air to plain DI water, A1 and A2 rose
  27 %, while A0 rose only 0.3 % (977.8 → 980.6). 980.6 counts at `vcc_mv` 4730 is about
  4.53 V, about 0.2 V below the supply, which looks like the detector's saturation ceiling.
  Low kaolin concentrations will likely read as clear on A0 until the signal comes off that
  ceiling. RV left untouched (`docs/hardware.md`); A0 runs the series as-is.
- **Room light (`03` covered against `04` uncovered, same fill):** A1, in the open beaker,
  reads 6.2 counts (0.8 %) higher uncovered, and its std rises from 0.16 to 0.42. A2, in
  the case, is unchanged (956.8 against 956.7). A0 is saturated, so it cannot show it.
  Room light reaches the stock heads, so the beaker stays covered from here on.
- **Plain DI against diluent (`03a` → `04`, both uncovered):** A1 +1.4 counts (+0.2 %),
  A2 +9.5 (+1.0 %). Both exceed the within-capture noise, but each capture was a separate
  fill, and A2's `03a` fill was noisy (std 1.83 against 0.12 in `04`), so fill-to-fill
  variation cannot be told apart from a Tween 20 effect. Every solution in the series uses
  the diluent and is normalized against `03`, so neither difference enters the results.
