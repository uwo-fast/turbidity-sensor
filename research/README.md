# Research Notes

Researched on `2026-03-31`.

This directory collects factual research relevant to the repo's turbidity-sensor work.
The goal is to separate:

- primary-source vendor facts
- standards and measurement context
- project-specific interpretation
- secondary/community references that may still be useful, but should not be treated as ground truth

## Doc Map

- `amphenol-turbidity-sensors.md`
  - Official facts for `TST-10`, `TSW-10`, and the nearby `TSD-10` family context.
  - Includes source conflicts that matter for engineering decisions.
- `dfrobot-sen0189.md`
  - Official DFRobot product/wiki facts, what the board does, and what DFRobot itself says about accuracy and NTU conversion.
- `turbidity-standards-and-units.md`
  - High-level measurement context from ISO, EPA, and USGS sources.
  - Clarifies what NTU/FNU/FAU mean and what they do not mean.
- `project-hardware-and-integration.md`
  - Repo-specific synthesis: actual sensing heads vs conditioning/interface board, current artifact state, and immediate engineering implications.
- `secondary-references.md`
  - Useful but non-authoritative external references such as community discussions and open-source projects.

## Highest-Signal Takeaways

- `TST-10` and `TSW-10` are the actual Amphenol optical sensing parts this repo is centered on.
- `SEN0189` is best treated here as a conditioning/interface reference path, even though the official DFRobot product is sold as a probe-plus-adapter kit.
- Current repo calibration artifacts are vendor-derived from datasheet curves, not from bench calibration.
- `ISO 7027` and `EPA 180.1` are useful reference points for later validation, but the repo is not yet implementing a standards-validated turbidity instrument.
- Some online sources disagree on important details. Those conflicts are documented instead of being silently normalized.

## Source Discipline

When reading these notes, prefer the following order:

1. Official vendor product page
2. Official vendor datasheet
3. Official standards body or government source
4. Official support/forum clarifications
5. Distributor metadata
6. Community/open-source material

If two sources disagree, the disagreement should be treated as a real research result, not a nuisance to ignore.
