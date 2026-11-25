# Tube case

A printed rectangular case that replaces the stock housing of the probe. Remove the stock
housing, place the bare DFRobot SEN0189 probe board in the printed base, close the lid, and push a
clear tube down
through the optical slot between the emitter and detector heads. Water flows through
the tube instead of around an immersed probe.

| File | Contents |
| --- | --- |
| `tube_case.scad` | Parametric source for both parts, with the case parameters |
| `../probe/probe.scad` | The board model: its dimensions, envelope and optical axis |
| `base.stl`, `lid.stl` | Print-ready exports, flat side down |

After changing the source, regenerate the STLs with `just tube-case` (requires OpenSCAD).
The triangle order of the export varies from run to run, so the STLs show as changed even
when the geometry has not changed.

## Parts

- **Clear tube:** 5/16 in (7.94 mm) outside diameter. FEP, acrylic, polycarbonate, or
  glass. The refractive index of FEP (about 1.34) is close to that of water, so the beam
  bends very little where it crosses from the inner wall into the water. The outer surface,
  against air, still bends it. The tube used here has a 1/4 in (6.35 mm) inside diameter;
  a 1/4 in drill shank fits it snugly. Calipers read 0.244-0.246 in, which is low, as
  calipers read in a small bore. The case does not depend on the inside diameter, but two
  quantities do: the length of water in the beam (6.35 mm) and the volume of liquid in the
  tube (0.032 mL per millimetre).
  The bore is `tube_od + tube_fit` (0.2 mm over by default). That fit is snug enough
  for the tube alone to hold the base and lid together. Loosen it and you will need tape
  or a zip tie as well. For another tube, set `tube_od` to its measured diameter. The
  gap between the heads is about 8.3 mm, so the tube cannot be much larger.
- **Probe board:** the bare board from inside the stock housing, with its bracket, heads,
  and right-angle connector.

## Printing

- Print in **opaque black**. Light that gets through the walls reaches the detector.
- Print the base as exported. Print the lid top-down, as exported. Neither part needs
  supports.
- Test the tube in both bores before assembling. If it is too tight, raise `tube_fit`
  rather than reaming the bore, and re-export.

## Assembly

1. Open the stock housing. Before you touch anything, photograph both sides of the
   board and mark the position of the `RV` trimmer (see [`docs/hardware.md`](../../docs/hardware.md#probe-trimmer-rv)),
   so the board can go back in its stock housing at its original setting.
2. Drop the board into the base, component side up. The pocket fits it only one way.
3. Put the lid on, keys down, with its window over the connector. The keys locate it
   on the base.
4. Push the tube through the lid, between the heads, and out through the base. The tube
   holds the case closed.
5. Plug the probe cable in through the window.

The base has a hole under the `RV` trimmer, for the setup below. To remove the hole, set
`access_hole = false`.

## Optics and setup

Filled with water, the tube acts as a cylindrical lens and concentrates the emitter's beam
on the detector. With the load fixed, one board read 1.87 times as much with water in the
tube as with it empty. A board in its stock housing read 1.26 times as much in water as in
air. `tools/tube_raytrace.py` models this cross-section and predicts a ratio of 1.52 for
water over air, unchanged for emitter half-angles from 10 to 45°.

As a result, a board that reads well in its stock housing reads near the top of the ADC range
in the case: 940–970 counts of 1023 in clear water, where it barely responds to turbidity. Two
boards stayed there even with `RV` at its dimmest end. Lowering the load resistance on the probe
output fixes this. The same applies to the [sampler case](../sampler-case/README.md), which has
the same pocket and tube. The stock housing needs no resistor. To set the load:

1. Turn `RV` fully counter-clockwise (viewed from above), its dimmest end.
2. With clear water in the tube, add a resistor from the probe's output (the middle pin of
   the probe connector) to GND, in parallel with the 4.7 kΩ load on the adapter. Choose it so
   the clear reading is about 850–880 counts. Boards differ: one needed 15 kΩ, another 6.8 kΩ.
3. Record the resistor value with the board's data.

With this setup, two boards, each in its own case and tube, read −8.6 % and −4.9 % at
250 mg/L kaolin and −85.7 % and −85.3 % at 4000 mg/L. Standard deviations were 0.1–1.0 points
across five fills per point (`data/bench/2026-10-28/notes.md`). Without the resistor, a board in
the case changed by −1.7 % at 4000 mg/L.

Replacing the water with isopropanol (refractive index 1.377) was intended to confirm the lens
effect. The model predicts +4.5 % over water. The heads in tube cases rose 2.4–3.0 %, but a head
in its stock housing, with no tube in its path, rose 14 %. Something else also changes with the
liquid, so the test does not isolate the lens effect.

## Light leaks

A clear tube acts as a light pipe: it carries light along its walls from wherever its
ends are lit. Sleeve the tube with opaque tubing or tape outside the case, and check the dark
reading before trusting low-turbidity numbers. With the SEN0189 adapter the emitter is
always on, so take the dark reading with an opaque rod in place of the tube. The
`uno_switched_emitter` build measures ambient light on every sample, but it needs the
bare wiring in [`docs/hardware.md`](../../docs/hardware.md#alternative-bare-wiring), not the adapter.

The optical path differs from the stock housings (tube walls and a 6.35 mm water column
instead of the window in the stock housing), so the Amphenol vendor curves do not describe
this setup. Calibrate it from its own dark and clear-water readings.

## Using the tube case in another OpenSCAD project

`include` the file and set `part = "none"`. This imports the case modules (`base()`,
`lid()`, `tube_bore()`, …) and dimensions, lets you override the case parameters, and
draws nothing. The board library it uses, `../probe/probe.scad`, is included with it, so
`probe()` and the `probe_*()` functions are available in your file. The board dimensions
cannot be overridden from your file. Change them in `probe.scad`.

```openscad
include <tube_case.scad>
part = "none";   // draw nothing from this file
tube_od = 8.0;   // any of the case's parameters can be overridden

// The case is a box case_w x case_l, from z = bot_z to top_z, in this file's frame
// (origin on the PCB centreline, z = 0 at the PCB underside). The tube axis runs
// along z at (0, tube_y).
difference() {
  translate([-case_w / 2 - 5, -case_l / 2 - 5, bot_z - 5])
    cube([case_w + 10, case_l + 10, 5]);
  translate([0, tube_y, bot_z - 6]) cylinder(d=tube_od + 2, h=7);
}
base();
```

`use <tube_case.scad>` also works, but only at the default parameters: overrides are
ignored and the dimensions are not readable.

## Status

- Printed at the default parameters and fitted to a real board. The board, keys and tube
  all fit, and the tube holds the parts together without tape or a zip tie.
- Print settings for that fit: Prusa MK3, PETG, 3 perimeters, 30% gyroid infill,
  0.07 mm layers with adaptive variable layer height (quality/speed slider at 0.5,
  smoothed with radius 5 and "keep min"). The fit clearances (`clr`, `tube_fit`,
  `key_clr`) are proven only for this setup. On another printer or material, print the
  base first and test the tube and board in it.
- The board dimensions are in `../probe/probe.scad`, from a CAD model drawn from caliper
  measurements. They matched the board used for the test print, and the TSW-10 and TST-10
  boards are the same. If your board differs, update the dimensions there, starting with
  the inner faces of the heads (`head_x0`) and the PCB outline (`pcb_*`).
- The position of the tube axis along the arms (`optical_y`, 10.8) is the centre of the
  lens windows, measured from the root of the arms. The first print placed the tube at
  11.4, before this was measured.
- Tested wet on 2026-10-28 with kaolin standards from 250 to 4000 mg/L, after the setup in
  [Optics and setup](#optics-and-setup).
