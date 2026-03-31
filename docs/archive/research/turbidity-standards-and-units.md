# Turbidity Standards and Units

Researched on `2026-03-31`.

## Why This Note Exists

This repo already has standards-related PDFs under `datasheets/`, but the current work
is still in vendor-derived calibration territory. This note is a high-level map of what
those standards imply and why that matters.

## Turbidity Is an Optical Property

USGS describes turbidity as an optical measure of water clarity based on how much light
is scattered by material in the sample. That is a useful anchor because it separates
`turbidity` from simpler ideas like direct solids mass.

Practical consequence:

- turbidity is not just "how many milligrams per liter of stuff are in the water"
- different particles can produce different optical responses even at similar mass
  concentrations

## EPA Method 180.1

The EPA's `Method 180.1` is a nephelometric turbidity method.

Key points from the EPA method text:

- intended scope is roughly `0 to 40 NTU` without dilution
- higher values may be obtained by dilution
- readings are based on scattered light compared with a reference suspension
- the instrument is calibrated with formazin suspension
- the method treats `NTU` as comparable to earlier `FTU` and `JTU` reporting in that
  method context

Project implication:

- EPA 180.1 is useful background for low-turbidity instrument validation
- it is not a direct match to the vendor appliance-sensor datasheet curves in the
  `1000-4000 NTU` regime

## ISO 7027-1:2016

ISO `7027-1:2016` is the quantitative optical turbidity standard in the current ISO
split.

Official ISO summary points:

- it specifies two quantitative optical methods
- nephelometry is for low-turbidity water and reports in `NTU`
- turbidimetry is more suitable for highly turbid water and reports in `FAU`
- the ISO summary says there is numerical equivalence between `NTU` and `FNU`
- the summary gives a typical nephelometric range below about `400 NTU`
- the summary gives a typical turbidimetric attenuation range of about `40 to 4000 FAU`

Project implication:

- the current repo's vendor-derived curves extending to `1000 NTU` and `4000 NTU`
  overlap more with the "high turbidity" conversation than with the classic
  low-turbidity drinking-water nephelometer case
- a future standards-aware build may need to be clear about whether it is trying to
  emulate nephelometric practice, attenuation-style practice, or simply use a custom
  optical transfer function

## ISO 7027-2:2019

ISO `7027-2:2019` covers semi-quantitative transparency methods such as:

- transparency tube
- transparency disc
- diver visibility methods

This matters mainly as context: ISO itself separates those visual transparency methods
from the quantitative optical-instrument methods in ISO 7027-1.

## Caution on NTU, JTU, FNU, FAU, and mg/L

The different unit names often get blurred together online.

Safe summary:

- `NTU` is widely used for nephelometric turbidity reporting
- ISO explicitly links `NTU` and `FNU` numerically in the 7027-1 summary
- `FAU` is used for attenuation-based turbidity measurement in ISO 7027-1
- `JTU` is an older reporting unit that still appears in some legacy discussions
- `mg/L` is a mass concentration and should not be treated as universally equivalent to
  optical turbidity

For this repo, any source that casually equates `NTU`, `JTU`, and `mg/L` should be
handled with caution.

## What This Means for the Repo Today

- The repo is currently using vendor appliance-sensor curves, not standards-traceable
  formazin-based bench calibration.
- That is acceptable for early firmware work, architecture decisions, and rough
  transfer-function experiments.
- It is not enough to claim compliance with EPA or ISO turbidity methods.
- If the project later aims at quantified field or lab use, it will need:
  - calibration media and a repeatable procedure
  - known geometry and optical configuration
  - controlled electronics and ADC behavior
  - comparison against a trusted reference instrument or standard method

## Sources

Primary sources:

- https://nepis.epa.gov/Exe/ZyNET.exe/30000Q10.TXT?Client=EPA&Displa=&Docs=&EndTime=&ExtQFieldOp=0&File=D%3A%5Czyfiles%5CIndex+Data%5C76thru80%5CTxt%5C00000001%5C30000Q10.txt&FuzzyDegree=0&ImageQuality=r75g8%2Fr75g8%2Fx150y150g16%2Fi425&Index=1976+Thru+1980&IntQFieldOp=0&MaximumDocuments=1&Password=anonymous&QField=&QFieldDay=&QFieldMonth=&QFieldYear=&Query=&SearchMethod=1&SortMethod=h%7C-&Time=&Toc=&TocEntry=&TocRestrict=n&User=ANONYMOUS&XmlQuery=&ZyActionD=ZyDocument
- https://www.iso.org/standard/62801.html
- https://www.iso.org/standard/69545.html
- https://www.usgs.gov/water-science-school/science/turbidity-and-water
