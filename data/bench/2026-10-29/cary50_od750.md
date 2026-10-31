## Cary 50 — Algae Dilution Series (2026-10-29)

Instrument: Varian Cary 50 UV-Vis spectrophotometer\
Wavelength: 750 nm (OD₇₅₀)\
Cuvettes: Semi-micro, 10 mm optical path\
Blank: Cell-free culture supernatant\
Master stock: the `c1000` bottle (culture as grown), so 25 % is `c0250` and 12.5 % is `c0125`

### Procedure

1. Prepared a starting suspension of 250 µL algae master stock (25%) and 750 µL native supernatant (75%), totaling 1,000 µL.
2. Zeroed the Cary 50 using supernatant and verified the blank (OD = 0.0020).
3. Measured the starting suspension.
4. Sequentially added 250 µL supernatant to the same suspension, mixing and measuring OD₇₅₀ after each addition.
5. Continued until the final volume reached 2,000 µL.

### Results

| Read      | Total volume | Stock fraction | OD₇₅₀  |
| --------- | ------------ | -------------- | ------ |
| 1 (blank) | 1,000 µL     | 0%             | 0.0020 |
| 2         | 1,000 µL     | 25.00%         | 0.5301 |
| 3         | 1,250 µL     | 20.00%         | 0.4631 |
| 4         | 1,500 µL     | 16.67%         | 0.3872 |
| 5         | 1,750 µL     | 14.29%         | 0.3170 |
| 6         | 2,000 µL     | 12.50%         | 0.2786 |

### Observations

- OD₇₅₀ decreased monotonically from 0.5301 to 0.2786 with progressive dilution.
- All culture measurements fell within a useful preliminary working range (approximately 0.28–0.53 OD).
- Measured values were 4.7–9.6% above a straight scaling of the starting measurement (+9.2, +9.6, +4.7, +5.1% at 20, 16.67, 14.29 and 12.5%).
- A straight-line fit gives 0.0206 OD per % stock, intercept 0.031, R² 0.977.
- Cuvette fill height and beam coverage were independently checked and confirmed adequate.

Conclusion: The dilution series demonstrates the expected decreasing OD₇₅₀ response with decreasing algae concentration. Results are suitable for preliminary analysis, pending replicate measurements to characterize repeatability and linearity.

### Direct reads from the sensor bottles

- `c0125`: 0.2747, matching the 12.5 % read above (0.2786), so the bottle series was made correctly.
- `c0500`: 0.9813, read from the bottle; near the top of the linear range.

### Master stock OD

A proportional fit through the origin of reads 2–6, OD = k × fraction with
k = Σ(OD × fraction) / Σ(fraction²), gives OD₇₅₀ 2.22 for `c1000`. The other levels scale
from it by dilution (`c0063` 0.139, `c2000` 4.45, `c4000` 8.89); above about 1.0 these are
extrapolated, not measurable in a 10 mm cuvette.
