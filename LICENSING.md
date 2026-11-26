# Licensing

This document states which licence covers which parts of this repository, and
explains what that means. [What applies where](#what-applies-where) is the operative
section: it states the terms under which these files are made available. The rest of
this document is commentary for convenience. The binding terms are the full texts in
[`LICENSES/`](LICENSES/).

Where a project holds both software and hardware design files, each component is
licensed separately. This is not dual licensing: you do not choose which licence
covers a given file.

- **Software** — GNU General Public License v3.0 or later (`GPL-3.0-or-later`) —
  [`LICENSES/GPL-3.0-or-later.txt`](LICENSES/GPL-3.0-or-later.txt)
- **Hardware** — CERN Open Hardware Licence Version 2, Strongly Reciprocal
  (`CERN-OHL-S-2.0`) — [`LICENSES/CERN-OHL-S-2.0.txt`](LICENSES/CERN-OHL-S-2.0.txt)
- **Research data** — Creative Commons Attribution 4.0 International (`CC-BY-4.0`) —
  [`LICENSES/CC-BY-4.0.txt`](LICENSES/CC-BY-4.0.txt)

The root [`LICENSE`](LICENSE) is a copy of the GPL text. GitHub reads that file and
reports only one licence per repository, so this document is the complete statement
of licensing.

## What applies where

| Path | Licence |
| --- | --- |
| `include/`, `src/`, `tools/`, `examples/`, `rig/`, `tests/` | `GPL-3.0-or-later` |
| `CMakeLists.txt`, `cmake/`, `library.json`, `justfile`, `.github/`, and other build tooling | `GPL-3.0-or-later` |
| `hardware/`, except `hardware/sampler-case/` — parametric CAD source (`.scad`) | `GPL-3.0-or-later` **and** `CERN-OHL-S-2.0` |
| `hardware/`, except `hardware/sampler-case/` — geometry (STL) generated from that source | `CERN-OHL-S-2.0` |
| `hardware/sampler-case/` — the sampler case's source, and geometry generated from it | `GPL-3.0-or-later` |
| `data/` — bench captures, their notes and photos, and the calibration sets | `CC-BY-4.0`, except as listed under [Third-party components](#third-party-components) |
| `docs/` | see below, except as listed under [Third-party components](#third-party-components) |

Add a row to the table above for each new top-level directory.

Parametric CAD source is granted under both licences so that a licensee who Makes a
Product from the geometry can satisfy CERN-OHL-S-2.0 §4, which requires the Complete
Source — the design in its preferred form for modification, meaning the source, not
the mesh. The tube case, probe and flange CAD can carry both licences because they
include no GPL-licensed library. The sampler case includes NopSCADlib,
bayonet-port-scad and syringe-actuator, which are GPL-3.0-or-later. The sampler case
and the geometry generated from it are therefore `GPL-3.0-or-later` only. See the
organization [licensing policy](https://github.com/uwo-fast/.github/blob/main/LICENSING.md).

**Documentation.** Documentation specific to software is licensed
`GPL-3.0-or-later`, and documentation specific to hardware `CERN-OHL-S-2.0`.
Documentation that covers both (for example, a build guide with a bill of materials
and code listings), and documentation specific to neither, is licensed under both, at
your option.

## Third-party components

Anything vendored or included keeps its own licence, unaffected by this document.
None of the files below is licensed by this repository.

| Path | Owner | Status |
| --- | --- | --- |
| `docs/archive/datasheets/TST-10-*.pdf`, `docs/archive/datasheets/TSW-10-*.pdf` | Amphenol Thermometrics | Vendor datasheets, all rights reserved by their publisher |
| `data/calibration/vendor-data/*-datasheet-plot.png` | Amphenol Thermometrics | Plots cropped from those datasheets |
| `docs/archive/datasheets/EPA180.1_Turbidity_Nephelometry_1993.pdf` | US EPA | US Government work |

The curves in `data/calibration/vendor-data/*.csv` were digitized by this project
from those plots, and are covered by the `data/` row above.

## Contributions

"Contribution" means any work of authorship intentionally submitted for inclusion
in this project — a pull request, patch, commit, issue, or other communication —
excluding anything conspicuously marked "Not a Contribution".

Unless you state otherwise, contributions you submit are licensed under whichever
of the licences above covers the files they touch, with no additional terms. By
submitting a contribution you represent that you have the right to license it on
those terms.

## Patents

Both GPL-3.0 (section 11) and CERN-OHL-S-2.0 (section 7) contain express patent
provisions. Review them before using, modifying, or distributing this project.

## Disclaimer of warranty and liability

This section summarises terms in the licences themselves: GPL-3.0 sections 15–17
and CERN-OHL-S-2.0 section 6.

THIS PROJECT, INCLUDING ALL SOFTWARE AND HARDWARE DESIGNS, IS PROVIDED "AS IS"
WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
NON-INFRINGEMENT.

TO THE EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL THE AUTHORS,
CONTRIBUTORS, OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER
LIABILITY ARISING FROM, OUT OF, OR IN CONNECTION WITH THIS PROJECT.

### Additional disclaimer

The following is not a summary of either licence. It is an additional disclaimer of
the kind GPL-3.0 section 7(a) permits, offered alongside them:

HARDWARE DESIGNS HERE HAVE NOT BEEN INDEPENDENTLY VERIFIED OR CERTIFIED FOR SAFETY
OR REGULATORY COMPLIANCE. ANY PHYSICAL PRODUCT MANUFACTURED FROM THEM IS PRODUCED
ENTIRELY AT YOUR OWN RISK. TO THE EXTENT PERMITTED BY APPLICABLE LAW, THE AUTHORS
AND CONTRIBUTORS ARE NOT RESPONSIBLE FOR ANY PERSONAL INJURY, PROPERTY DAMAGE, OR
OTHER HARM RESULTING FROM THE USE OR MANUFACTURE OF PRODUCTS BASED ON THEM.

## Trademarks

Neither licence grants trademark rights. This project does not grant permission to
use the names, trademarks, or logos of the FAST research group or of the project's
contributors, except as needed to describe the project's origin.

## Precedence

Where the commentary in this document and the full licence texts conflict, the full
texts prevail. The scope table above is not commentary. It states which files are
made available under which terms.
