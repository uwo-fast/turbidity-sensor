# Sampler case

A printed case round the bare probe board and a clear tube, drawn through by the
[syringe actuator](https://github.com/uwo-fast/syringe-actuator) bolted on top, standing on a
vessel's port. A clear FEP tube runs between the board's heads; the vessel's riser is bushed into
its bottom, and the syringe draws culture up through it.

To the board it is the same as the [tube case](../tube-case/README.md): the same pocket, tube
and light path, so it needs the same load resistor
([optics and setup](../tube-case/README.md#optics-and-setup)), and a board reads the same in
either. It differs only in how much ambient light reaches the tube.

Two prints, both in `sampler_case.scad`:

- **The base:** the vessel's foot, a skirt out to the case, and the floor under the board.
- **The top:** the board's pocket, the shroud round the syringe, and the face the actuator bolts to.

## The foot

The foot is the part that mounts the base on the vessel's port, and it belongs to the vessel. This
file draws everything above it and checks its fits against four figures, `foot_flange_h`,
`foot_neck_r`, `foot_core_r` and `foot_gland_top_z`. Their defaults are the bayonet pin on
open-source-bioreactor's standard port.

`bayonet.scad` stands the case on that pin, from
[bayonet-port-scad](https://github.com/CameronBrooks11/bayonet-port-scad), and is the file to
print from. It is also the pattern for another foot:

1. `use`/`include` the foot's library, and define what the foot figures are computed from
   (`panel`), before including `sampler_case.scad`.
2. After the include, set `part = "none"` and the four `foot_*` figures.
3. Pass the foot as the child of `sampler_base()`, `sampler_placed()` or `sampler_print("base")`.

OpenSCAD takes a reassigned variable's last value, evaluated where `sampler_case.scad` first assigns
it, so a figure set before the include is silently replaced by the default, and a name defined
after it is still undefined where the figures are computed.

Without a child the base has no foot. Issue
[#49](https://github.com/uwo-fast/turbidity-sensor/issues/49) tracks other feet.

## Syringes

`syringe` picks the actuator's layout. Only `5ml-gnr2`, the syringe the sampler runs, has been
fit-tested. The other 5 mL layouts (`5ml-gnr1`, `5ml-gnr1-ga25`, `5ml-gnr2-ga25`) render but are
unverified. The 1, 3, 10, 20 and 30 mL do not build yet: syringe-actuator has not measured their
`nozzle_l`, which places the face, and the build stops there.

## The line

A vessel that cuts the riser reads these to cut and check the rest of the line:

| Function | Gives |
| --- | --- |
| `sampler_clear_tube_cut()` | the FEP tube's cut length, mm |
| `sampler_sleeve_l()` | the silicone sleeve's length over the riser's top, mm |
| `sampler_syringe()` | the syringe's row in syringe-actuator |
| `sampler_stroke_ml()` | what one stroke draws: the actuator's stroke across the syringe's nominal bore |
| `sampler_line_ml(riser_l)` | the line's volume from the riser's open end up past the heads' top |

A stroke has to move `sampler_line_ml(riser_l)` before the culture at the beam is culture drawn
from the inlet, rather than what stood in the line between bursts. The heads' top stands in for the
beam because the lens window's height on them is not in the probe library.

## Checks and libraries

```sh
just scad-setup     # the pinned scadman, then the libraries scadman.lock pins
just check-sampler-case  # tests/sampler-case/fit.scad, on the bayonet foot: renders empty while every fit holds
```

To export a print, with the libraries on `OPENSCADPATH`:

```sh
OPENSCADPATH=$PWD/.scadman/env openscad --export-format binstl -D 'piece="base"' -o base.stl hardware/sampler-case/bayonet.scad
```

`piece` is `base`, `top` or `assembly`; both prints come out lying as they print.

## Status

Run 1 (`data/bench/2026-11-05/`) used an earlier version of this case, printed from
open-source-bioreactor before syringe-actuator v0.1.0, whose face sat 13.8 mm higher. The move here
changed no geometry: with the bayonet pin passed as the foot, the base and top export
byte-identical to open-source-bioreactor's at f3c35f0, the merge of its #150.
