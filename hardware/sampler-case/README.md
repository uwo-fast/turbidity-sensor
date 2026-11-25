# Sampler case

A printed case that holds the bare probe board and a clear tube, and mounts on a vessel port.
The [syringe actuator](https://github.com/uwo-fast/syringe-actuator) bolts on top and draws culture
through the tube. The clear FEP tube runs between the heads of the board. The riser from the vessel
is bushed into the bottom of the tube, and the syringe draws culture up through it.

For the board, it is the same as the [tube case](../tube-case/README.md): it has the same pocket,
tube and light path. It needs the same load resistor
([optics and setup](../tube-case/README.md#optics-and-setup)), and a board gives the same readings
in either case. The only difference is how much ambient light reaches the tube.

The case is printed in two parts, both defined in `sampler_case.scad`:

- **Base:** the foot that mounts on the vessel, a skirt out to the case, and the floor under the
  board.
- **Top:** the board pocket, the shroud around the syringe, and the face that the actuator bolts
  to.

## The foot

The foot mounts the base on the vessel port, and its design belongs to the vessel.
`sampler_case.scad` draws everything above the foot and checks its fits against four dimensions:
`foot_flange_h`, `foot_neck_r`, `foot_core_r` and `foot_gland_top_z`. Their defaults match the
bayonet pin on the standard port of open-source-bioreactor.

`bayonet.scad` mounts the case on that pin, using
[bayonet-port-scad](https://github.com/CameronBrooks11/bayonet-port-scad). Print from this file. It
is also the template for another foot:

1. `use`/`include` the foot library, and define the values that the foot dimensions are computed
   from (`panel`), before including `sampler_case.scad`.
2. After the include, set `part = "none"` and the four `foot_*` dimensions.
3. Pass the foot as the child of `sampler_base()`, `sampler_placed()` or `sampler_print("base")`.

OpenSCAD uses the last value assigned to a variable, evaluated where `sampler_case.scad` first
assigns it. A dimension set before the include is therefore silently replaced by the default, and a
name defined after the include is still undefined where the dimensions are computed.

Without a child, the base has no foot. Issue
[#49](https://github.com/uwo-fast/turbidity-sensor/issues/49) tracks other foot designs.

## Syringes

`syringe` selects the actuator layout. Only `5ml-gnr2`, the syringe the sampler uses, has been
fit-tested. The other 5 mL layouts (`5ml-gnr1`, `5ml-gnr1-ga25`, `5ml-gnr2-ga25`) render but are
unverified. The 1, 3, 10, 20 and 30 mL layouts do not build yet. syringe-actuator has not measured
their `nozzle_l`, which sets the position of the face, so the build stops there.

## The line

A vessel design that cuts the riser uses these functions to cut and check the rest of the sample
line:

| Function | Returns |
| --- | --- |
| `sampler_clear_tube_cut()` | cut length of the FEP tube, mm |
| `sampler_sleeve_l()` | length of the silicone sleeve over the top of the riser, mm |
| `sampler_syringe()` | the row for the syringe in syringe-actuator |
| `sampler_stroke_ml()` | volume drawn by one stroke: the actuator stroke times the nominal bore area of the syringe |
| `sampler_line_ml(riser_l)` | volume of the line from the open end of the riser to the top of the heads |

A stroke must move `sampler_line_ml(riser_l)` before the liquid at the beam is culture drawn from
the inlet rather than culture that stood in the line between bursts. The top of the heads is used
in place of the beam because the probe library does not record the height of the lens windows.

## Checks and libraries

```sh
just scad-setup     # install the pinned scadman, then the libraries pinned in scadman.lock
just check-sampler-case  # render tests/sampler-case/fit.scad with the bayonet foot; empty while every fit holds
```

To export a print, with the libraries on `OPENSCADPATH`:

```sh
OPENSCADPATH=$PWD/.scadman/env openscad --export-format binstl -D 'piece="base"' -o base.stl hardware/sampler-case/bayonet.scad
```

`piece` is `base`, `top`, `case` or `assembly`. The two prints are exported in their print
orientation. In `case` and `assembly`, `seals=true` draws the two o-rings of the foot: the riser
o-ring in its bore and the face seal under the flange. `riser_l` draws that many millimetres of the
riser, down from its top end.

## Status

Run 1 (`data/bench/2026-11-05/`) used an earlier version of this case. It was printed from
open-source-bioreactor before syringe-actuator v0.1.0, and its face sat 13.8 mm higher. Moving the
case into this repository changed no geometry. With the bayonet pin passed as the foot, the base
and top export byte-identical to those in open-source-bioreactor at f3c35f0, the merge commit of
its #150.
