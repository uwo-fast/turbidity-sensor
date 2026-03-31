# Context

## Project Snapshot

This repo is a working brief for adapting appliance-derived turbidity sensing hardware
into a reusable embedded measurement workflow.

The primary sensing elements are:

- Amphenol Thermometrics `TST-10`
- Amphenol Thermometrics `TSW-10`

The current on-hand interface / conditioning reference module is:

- DFRobot `SEN0189`

The project is currently about firmware and bring-up, not a finished water-quality
instrument. The goal is to understand the optical sensor heads, define the required
signal-conditioning path between those sensors and an MCU or SBC, and create a
calibration workflow that can later be replaced or refined with bench data.

This repo is not yet a standards-validated turbidity instrument project.

## Current State

- Official sensor datasheets and standards-related PDFs are stored under `datasheets/`.
- `calibration/vendor-data/` contains digitized points extracted from the Amphenol
  datasheet curves.
- `calibration/generate_calibration_csvs.py` converts those raw point clouds into the
  canonical generated calibration tables:
  - `calibration/tst10-calibration.csv`
  - `calibration/tsw10-calibration.csv`
- `calibration/plot.py` generates plots and quadratic fit reports:
  - `calibration/tst10-plot.png`
  - `calibration/tsw10-plot.png`
  - `calibration/tst10-fit.txt`
  - `calibration/tsw10-fit.txt`
- The current calibration data is vendor-derived from datasheet curves. It is useful
  for early firmware development, simulation, and comparison work, but it is not a
  substitute for empirical calibration.

## Sensor Comparison

| Sensor | Supply | Output style | Vendor test range or nominal range reference | Notable electrical behavior | Current repo role |
| --- | --- | --- | --- | --- | --- |
| `TST-10` | 5V DC | 3-pin analog optical sensor head, output measured between pin 2 and GND | Vendor test method compares output in `0 NTU` and `4000 NTU` water | Contains the actual emitter / receiver sensing pair; datasheet voltage differential `2.7V +/- 20%` | Primary target, higher-range Amphenol sensing element |
| `TSW-10` | 5V DC | 3-pin analog optical sensor head, output measured between pin 2 and GND | Vendor test method compares output in `0 NTU` and `1000 NTU` water | Contains the actual emitter / receiver sensing pair; datasheet voltage differential `1.3V +/- 20%` | Primary target, lower-range Amphenol sensing element |
| `SEN0189` | 5V DC | Conditioning / interface module with analog `0-4.5V` output plus digital threshold output | Official DFRobot material does not state a formal NTU range on the main wiki page | Minimal interface electronics between the sensing hardware and MCU/SBC; response time `<500 ms` | On-hand bring-up/reference board, not the primary sensor identity |

## Technical Direction

- Firmware should stay MCU-agnostic first, with Arduino and Raspberry Pi treated as
  example hosts rather than the defining platform.
- The architectural split should stay explicit: optical sensing element first,
  conditioning / interface electronics second, host firmware third.
- The software path should separate:
  - raw analog acquisition
  - filtering / averaging
  - calibration mapping
  - reporting or host integration
- `TST-10` and `TSW-10` are the actual sensing parts the repo is ultimately trying to
  support.
- `SEN0189` is useful for faster bring-up because it provides a ready-made conditioning
  / interface board, but its convenience should not redefine the final calibration or
  electrical assumptions for the Amphenol sensing heads.
- Practical bring-up likely needs explicit attention to power, analog reference,
  ADC resolution, filtering, and any required conditioning or buffering around the
  target sensor path.

## Calibration and Validation Stance

- The current repo calibration is based on vendor datasheet curves, not on measured
  calibration liquids or a validated bench setup.
- The generated calibration CSVs and quadratic fit reports are implementation aids for
  early development. They are not authoritative metrology.
- Community `SEN0189` voltage-to-NTU formulas are useful as practical bring-up
  references only. They should not be treated as authoritative calibration for this
  repo.
- `ISO 7027`, `EPA 180.1`, and related standards documents in `datasheets/` are
  present as future reference material for proper calibration and quantification work.
  They are not the basis for any current compliance claim.

## Known Facts

- Official Amphenol material describes both `TST-10` and `TSW-10` as turbidity sensors
  for wash water in washing machines and dishwashers.
- Both primary Amphenol sensors are specified for `5V` operation and analog voltage
  measurement against ground.
- `TST-10` and `TSW-10` are the actual optical sensing elements that contain the light
  emitter / receiver pair used for turbidity measurement.
- The vendor documentation distinguishes `TST-10` and `TSW-10` mainly by their test
  method range and output differential.
- The repo already contains generated calibration tables, plots, and quadratic fit
  reports derived from the vendor curves.
- The DFRobot `SEN0189` module is available as on-hand hardware and is relevant as a
  conditioning / interface reference path between a turbidity sensing element and an
  MCU or SBC.

## Unknowns and Working Assumptions

- The real transfer function of any physical sensor in the intended setup is still
  unknown until bench measurements are collected.
- The best analog front-end and ADC strategy for the final embedded target is still an
  open engineering decision.
- Temperature sensitivity, drift, fouling, repeatability, and installation effects
  still need empirical characterization.
- It is assumed that the current vendor-derived curves are good enough for initial
  firmware scaffolding.
- It is assumed that `TST-10` and `TSW-10` remain the main sensor targets even if the
  earliest experiments use `SEN0189`.
- It is assumed that `SEN0189` can help validate the interface chain from sensor to
  MCU/SBC, plus acquisition, filtering, and firmware structure, but not stand in as a
  one-to-one calibration proxy for the Amphenol sensing heads.

## Near-Term Milestones

- Define the first practical electrical interface path for one target sensor.
- Implement raw sampling, filtering, and logging on a simple embedded target.
- Use the current generated calibration artifacts to support early firmware behavior
  and test harnesses.
- Compare bring-up experience with the on-hand `SEN0189` against expectations from the
  Amphenol sensor documentation.
- Replace or refine vendor-derived calibration with empirical data once real bench
  testing begins.
- Revisit standards-oriented quantification later, after the basic sensing path is
  working reliably.

## Primary References

- [Amphenol TST-10 page](https://amphenol-sensors.com/en/thermometrics/turbidity/2959-tst-10)
- [Amphenol TST-10 datasheet PDF](https://www.amphenol-sensors.com/hubfs/AAS-920-617C-Thermometrics%20TST10-022724-web.pdf)
- [Amphenol TSW-10 page](https://amphenol-sensors.com/en/thermometrics/turbidity/934-tsw-10)
- [Amphenol TSW-10 datasheet PDF](https://www.amphenol-sensors.com/hubfs/AAS-920-479D-Thermometrics-TSW-10-022724-web.pdf)
- [DFRobot SEN0189 product page](https://www.dfrobot.com/product-1394.html)
- [DFRobot SEN0189 wiki](https://wiki.dfrobot.com/sen0189)
- Local calibration artifacts under `calibration/`
- Local standards and background PDFs under `datasheets/`
