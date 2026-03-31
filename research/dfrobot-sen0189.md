# DFRobot SEN0189

Researched on `2026-03-31`.

## What the Official DFRobot Product Is

Official DFRobot material presents `SEN0189` as a complete product made of:

- a turbidity sensor adapter board
- a turbidity sensor probe
- a probe cable
- a Gravity analog sensor cable

So the official DFRobot product is not only a board. It is sold as a probe-plus-adapter
kit.

## Official Product Facts

From the DFRobot product page and wiki:

- SKU: `SEN0189`
- Operating voltage: `5V DC`
- Operating current: `40 mA max`
- Response time: `<500 ms`
- Insulation resistance: `100 M min`
- Output modes:
  - analog output up to about `0-4.5V`
  - digital threshold output
- Operating temperature: `5C to 90C`
- Storage temperature: `-10C to 90C`
- Adapter board dimensions: `38 mm x 28 mm x 10 mm`

## Board-Level Features Called Out by DFRobot

The DFRobot wiki's analog example page exposes several concrete board features:

- a `D/A` switch chooses whether the output pin carries analog or digital output
- in analog mode, output voltage decreases as turbidity increases
- a threshold potentiometer is used in digital mode
- the sample code assumes a direct MCU ADC read of the analog output

DFRobot also gives one practical reference point in the analog example:

- in clear water below about `0.5 NTU`, the output should be around `4.1V +/- 0.3V`
  at about `10C to 50C`

That is useful as a sanity check for board behavior, not as a full calibration model.

## Waterproofing / Mechanical Cautions

Official DFRobot material repeats an important mechanical warning:

- the top of the probe is not waterproof
- the adapter board is not waterproof
- official FAQ wording says the probe is only partially waterproof

This matters a lot for real deployments and bench setups.

## What DFRobot Itself Says About Accuracy

A particularly important source is the official DFRobot forum FAQ for `SEN0189`.
DFRobot support says:

- the voltage-vs-turbidity curve shown in their materials is approximate
- actual measured data may differ
- the device behaves more like a qualitative analog sensor than a precise quantitative
  NTU instrument
- conversion to standard NTU data is not recommended

That statement should heavily influence how this repo treats `SEN0189`:

- useful for bring-up and interface work
- risky as a claimed quantitative turbidity instrument without independent calibration

## Source Conflict: Marketed Range vs Support Guidance

There is an important tension inside DFRobot's own ecosystem:

- a DFRobot selection-guide blog post lists `SEN0189` with a measurement range of
  `0-3000 NTU` and an accuracy of about `+/-10% FS`
- the official DFRobot FAQ says the device behaves more like a qualitative analog
  sensor and that conversion to standard NTU is not recommended

Working interpretation for this repo:

- treat the selection-guide numbers as marketing-level or application-level guidance
- treat the FAQ caution as the stronger warning about what can actually be claimed
  without independent calibration

## Important Caveat About the Wiki's Unit Note

The DFRobot analog example page includes a note equating `JTU`, `NTU`, and `mg/L`.
That should not be treated as a general scientific truth.

Reason:

- `NTU` is an optical turbidity unit
- suspended-solids mass concentration is a different kind of quantity
- the relationship between optical turbidity and solids concentration depends strongly
  on particle size, particle shape, color, and sample composition

For this repo, that DFRobot note should be treated as a weak simplification rather than
an authoritative measurement statement.

## How SEN0189 Fits This Repo

For this project, the most useful interpretation is narrower than the official product
bundle description:

- the repo's primary sensing elements are `TST-10` and `TSW-10`
- `SEN0189` is most useful here as a conditioning / interface reference path between a
  turbidity sensing element and an MCU or SBC
- the board's direct analog output, digital threshold mode, switch, and potentiometer
  make it a convenient reference for early bring-up decisions

This does not prove that the `SEN0189` probe and the Amphenol sensor heads are the same
part or have the same transfer function.

## Project Implications

- `SEN0189` is valuable for fast bring-up because it exposes an MCU-friendly output.
- It should not silently define the final calibration model for `TST-10` / `TSW-10`.
- Any firmware that begins with `SEN0189` should preserve a clean abstraction boundary
  between sensing element, conditioning electronics, and host-side calibration logic.

## Sources

Primary sources:

- https://www.dfrobot.com/product-1394.html
- https://wiki.dfrobot.com/sen0189
- https://wiki.dfrobot.com/sen0189/docs/18001

Official support / clarification:

- https://www.dfrobot.com/forum/topic/315216

Additional DFRobot source:

- https://www.dfrobot.com/blog-1138.html
