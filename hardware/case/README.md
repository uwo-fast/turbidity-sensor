# Printed flow-through case

An alternative to the stock probe housing. Remove the housing, drop the bare DFRobot
SEN0189 probe board into the printed base, close the lid, and push a clear tube down
through the optical slot between the emitter and detector heads. Water flows through
the tube instead of around an immersed probe.

| File | Contents |
| --- | --- |
| `turbidity_case.scad` | Parametric source for both parts: the case's own choices |
| `../probe/probe.scad` | The board it is built around: its figures, envelope and optical axis |
| `base.stl`, `lid.stl` | Print-ready exports, flat side down |

Regenerate the STLs after changing the source with `just case` (needs OpenSCAD). The
export's triangle order varies from run to run, so the STLs show as changed even when
the geometry is not.

## Parts

- **Clear tube:** 5/16 in (7.94 mm) outside diameter. Acrylic, polycarbonate, or glass.
  The one used is 1/4 in (6.35 mm) inside diameter: a 1/4 in drill shank fits it snugly.
  Calipers read it 0.244-0.246 in, low, as they do in a small bore. The case does not depend
  on the inside diameter, but the volume of liquid in the tube does: 0.032 mL per millimetre.
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
   board and mark the position of the `RV` trimmer (see [`docs/hardware.md`](../../docs/hardware.md#probe-trimmer-rv)).
2. Drop the board into the base, component side up. The pocket fits it only one way.
3. Put the lid on, keys down, with its window over the connector. The keys locate it
   on the base.
4. Push the tube through the lid, between the heads, and out through the base. The tube
   holds the case closed.
5. Plug the probe cable in through the window.

The base has a hole under the `RV` trimmer. Leave the trimmer alone until it is
characterized. To remove the hole, set `access_hole = false`.

## Light leaks

A clear tube carries light along its walls, like a light pipe, from wherever its ends
are lit. Sleeve the tube with opaque tubing or tape outside the case, and take dark
readings (see the `uno_switched_emitter` build) before trusting low-turbidity numbers.

## Status

- Printed at the default parameters and fitted to a real board. The board, keys and tube
  all fit, and the tube holds the parts together without tape or a zip tie.
- Print settings for that fit: Prusa MK3, PETG, 3 perimeters, 30% gyroid infill,
  0.07 mm layers with adaptive variable layer height (quality/speed slider at 0.5,
  smoothed with radius 5 and "keep min"). The fit clearances (`clr`, `tube_fit`,
  `key_clr`) are proven only for this setup. On another printer or material, print the
  base first and test the tube and board in it.
- The board's figures live in `../probe/probe.scad`, from a CAD model drawn from caliper
  measurements. They matched the board used for the test print, and the TSW-10 and TST-10
  boards are the same. If yours differs, remeasure there: the heads' inner faces
  (`head_x0`) and the PCB outline (`pcb_*`) first.
- The tube's axis along the arms (`optical_y`, 11.4) is where this case put the tube,
  between the heads, not a measurement of where the lenses sit.
- Not yet tested wet.
