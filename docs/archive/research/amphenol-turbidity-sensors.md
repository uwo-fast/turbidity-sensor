# Amphenol Turbidity Sensors

Researched on `2026-03-31`.

## Scope

This note covers the Amphenol Thermometrics turbidity-sensor family entries most relevant to the repo:

- `TST-10`
- `TSW-10`
- nearby family context for `TSD-10`

## Shared Official Positioning

Across the official Amphenol product pages and 2024 datasheets, both `TST-10` and
`TSW-10` are described as turbidity sensors for wash water in washing machines and
dishwashers. The sensing principle is optical transmission: as soil or suspended
material increases, transmitted light decreases and the controller uses that change to
adjust wash behavior.

DigiKey classifies both parts as:

- sensor type: `Turbidity`
- output type: `Phototransistor`

That distributor metadata is consistent with the Amphenol description of a light
emitter plus a photo-transistor style receiver path.

## TST-10

### Official facts

- Official page title and official 2024 datasheet identify the part as `TST-10`.
- Rated voltage: `5V DC` between pin 1 and ground.
- Voltage differential: `2.7V +/- 20%`.
- Vendor test method: compare output in `0 NTU` water and `4000 NTU` water.
- Output measurement is taken between pin 2 and ground.
- Operating temperature on the official product page: `-10C to 90C`.
- Storage temperature on the official product page: `-20C to 90C`.
- Rated current: `30 mA max`.
- Insulation resistance: `100 MOhm min by 500V DC`.

### What matters for this repo

- `TST-10` is the higher-range Amphenol target in the current repo framing.
- The official test method reaching `4000 NTU` matches the repo's generated
  `tst10-calibration.csv` range and the current fit report.
- The official sources support treating `TST-10` as the actual optical sensing head,
  not an amplifier board.

## TSW-10

### Official facts

- Official page title and official 2024 datasheet identify the part as `TSW-10`.
- Rated voltage: `5V DC` between pin 1 and ground.
- Voltage differential: `1.3V +/- 20%`.
- Vendor test method: compare output in `0 NTU` water and `1000 NTU` water.
- Output measurement is taken between pin 2 and ground.
- Operating temperature on the official product page: `-30C to 80C`.
- Storage temperature on the official product page: `-10C to 80C`.
- Rated current: `30 mA max`.
- Insulation resistance: `100 MOhm min by 500V DC`.

### TSW-specific extras visible in the 2024 datasheet OCR

The current TSW datasheet text extraction clearly exposes more of the electrical sketch
than the TST datasheet OCR does. It shows:

- pin 1 as `VCC (+5V)`
- pin 2 as `Output`
- pin 3 as `GND`
- an internal optical path labeled with a diode and photo transistor
- resistor labels around `470 ohm` and `4.7 kohm`

This is strong evidence that the TSW part is an optical sensing element with a simple
internal network rather than a complete MCU-ready conditioning board.

### What matters for this repo

- `TSW-10` is the lower-range Amphenol target in the current repo framing.
- The official test method reaching `1000 NTU` and the plotted curve extending further
  into the `2000 NTU` region are not the same claim. The repo's extrapolated/generated
  artifacts should not be mistaken for official measurement guarantees.

## Family Context: TSD-10

Amphenol also publishes a sibling `TSD-10` part in the same turbidity family.
Public search snippets show:

- `5V` supply
- `3.0V +/- 10%` voltage differential
- `0 NTU` to `4000 NTU` vendor test method

This matters because the official `TST-10` product page currently lists `TSD-10` under
"Part Numbers" even though the page title, URL, and linked datasheet all say `TST-10`.
That should be treated as a website inconsistency, not as proof that `TST-10` and
`TSD-10` are the same part.

## Source Conflicts That Matter

### 1. TST-10 page vs TST-10 part-number field

The official Amphenol `TST-10` page currently shows `TSD-10` under the "Part Numbers"
section. However:

- the page title says `TST-10`
- the URL slug says `tst-10`
- the linked 2024 datasheet says `TST-10`
- DigiKey lists `TST-10` as a distinct active part
- Amphenol also has a separate `TSD-10` page

Working assumption: treat this as an Amphenol webpage inconsistency and use the 2024
`TST-10` datasheet plus distributor listing as the stronger identifiers.

### 2. TSW-10 temperature range: Amphenol vs DigiKey

There is a real conflict between sources for `TSW-10` operating temperature:

- Amphenol official page / 2024 datasheet: `-30C to 80C`
- DigiKey metadata: `-10C to 90C`

Working assumption: use the official Amphenol page and datasheet as the primary source
until a newer official correction says otherwise.

## Practical Interpretation

For this repo, the safest high-level interpretation is:

- `TST-10` and `TSW-10` are the actual Amphenol sensing elements.
- They are not turnkey MCU interface boards.
- Any conditioning, buffering, thresholding, or output shaping needed by the host
  should be treated as a separate design problem.

## Sources

Primary sources:

- https://amphenol-sensors.com/en/thermometrics/turbidity/2959-tst-10
- https://amphenol-sensors.com/en/thermometrics/turbidity/934-tsw-10
- https://www.amphenol-sensors.com/hubfs/AAS-920-617C-Thermometrics%20TST10-022724-web.pdf
- https://www.amphenol-sensors.com/hubfs/AAS-920-479D-Thermometrics-TSW-10-022724-web.pdf
- https://amphenol-sensors.com/en/thermometrics/turbidity/2958-tsd-10

Supporting distributor sources:

- https://www.digikey.ca/en/products/detail/amphenol-advanced-sensors/TST-10/4767842
- https://www.digikey.ca/en/products/detail/amphenol-advanced-sensors/TSW-10/4250485
