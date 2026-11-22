# Sampler housing

A flow cell round the bare probe board, drawn through by the
[syringe actuator](https://github.com/uwo-fast/syringe-actuator) bolted on top, standing on a
vessel's port. A clear FEP tube runs between the board's heads; the vessel's riser is bushed into
its bottom, and the syringe draws culture up through it.

Two prints, both in `sampler.scad`:

- **The base:** the vessel's foot, a skirt out to the housing, and the floor under the board.
- **The top:** the board's pocket, the shroud round the syringe, and the face the actuator bolts to.

## The foot

The foot is the part that mounts the base on the vessel's port, and it belongs to the vessel. This
file draws everything above it and checks its fits against four figures, `foot_flange_h`,
`foot_neck_r`, `foot_core_r` and `foot_gland_top_z`. Their defaults are the bayonet pin on
open-source-bioreactor's standard port.

A project with a foot includes this file, sets `part = "none"`, sets the four figures, and passes
its foot as the child of `sampler_base()`, `sampler_placed()` or `sampler_print("base")`:

```openscad
use <bayonet_port.scad>
include <bayonet_interfaces.scad>
panel = 18;  // set before the include below: see the note
include <turbidity-sensor/hardware/sampler/sampler.scad>
part = "none";
foot_flange_h = bayonet_flange_height(bayonet_std);
// ...the other three

sampler_print("base") bayonet_port(type=bayonet_std, part="pin", panel_thickness=panel,
                                   center_bore_radius=riser_bore, bore_oring=oring_4x1p5_epdm,
                                   catch_pockets=false);
```

OpenSCAD takes a reassigned variable's last value, evaluated where this file first assigns it. So
set the foot figures after the include, and define anything they are computed from before it.

Without a child the base has no foot, so it cannot be printed for use on its own. Issue
[#49](https://github.com/uwo-fast/turbidity-sensor/issues/49) tracks other feet.

## Syringes

`syringe` picks the actuator's layout. Only `5ml-gnr2`, the syringe the sampler runs, has been
fit-tested; the others render but are unverified.

## Checks and libraries

```sh
just scad-setup     # the pinned scadman, then NopSCADlib and syringe-actuator from scadman.lock
just check-sampler  # tests/sampler/fit.scad: renders empty while every fit holds
```

## Status

Run 1 (`data/bench/2026-11-05/`) used an earlier version of this housing, printed from
open-source-bioreactor before syringe-actuator v0.1.0, whose face sat 13.8 mm higher. The move here
changed no geometry: with the bayonet pin passed as the foot, the base and top export
byte-identical to open-source-bioreactor's at f3c35f0, the merge of its #150.
