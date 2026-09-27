# Printed flow-through case

An alternative to the stock probe housing. Remove the housing, drop the bare DFRobot
SEN0189 probe board into the printed base, close the lid, and push a clear tube down
through the optical slot between the emitter and detector heads. Water flows through
the tube instead of around an immersed probe.

| File | Contents |
| --- | --- |
| `turbidity_case.scad` | Parametric source for both parts |
| `base.stl`, `lid.stl` | Print-ready exports, flat side down |

Regenerate the STLs after changing the source with `just case` (needs OpenSCAD). The
export's triangle order varies from run to run, so the STLs show as changed even when
the geometry is not.

## Parts

- **Clear tube:** 5/16 in (7.94 mm) outside diameter. Acrylic, polycarbonate, or glass.
  The bore is `tube_od + tube_fit` (0.2 mm over by default) for a snug slide fit. For
  another tube, set `tube_od` to its measured diameter. The gap between the heads is
  about 8.3 mm, so the tube cannot be much larger.
- **Probe board:** the bare board from inside the stock housing, with its bracket, heads,
  and right-angle connector.
- **Tape or a zip tie** to hold the lid on. The tube locks the parts in place
  sideways, and the keys on the lid locate it on the base.

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
3. Put the lid on, keys down, with its window over the connector.
4. Push the tube through the lid, between the heads, and out through the base.
5. Tape or zip-tie the case closed, and plug the probe cable in through the window.

The base has a hole under the `RV` trimmer. Leave the trimmer alone until it is
characterized. To remove the hole, set `access_hole = false`.

## Light leaks

A clear tube carries light along its walls, like a light pipe, from wherever its ends
are lit. Sleeve the tube with opaque tubing or tape outside the case, and take dark
readings (see the `uno_switched_emitter` build) before trusting low-turbidity numbers.

## Status

- The board envelope in the source comes from a CAD model of the board, not from
  calipers. Measure a board before relying on a fit. The heads' inner faces
  (`head_x0`) and the PCB outline (`pcb_*`) matter most.
- The fit was checked in CAD against that board model. Both parts clear it by at least
  0.1 mm. The lid keys clear their grooves by at least 0.1 mm. A 5/16 in tube passes both
  bores and clears the board.
- It has not been printed or tested wet.
