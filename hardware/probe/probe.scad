// The probe board inside an Amphenol TSW-10 or TST-10 turbidity probe (the board is the same in
// both), as a library a housing is built around. It draws nothing itself.
//
// The board: a PCB with an emitter and a detector head on a U-shaped bracket, facing each other
// across a slot, and a right-angle 3-pin connector at the other end. A clear tube runs vertically
// through the slot, between the heads.
//
// Frame: origin on the PCB centreline, z = 0 at the PCB underside, +y toward the head arms, -y
// toward the connector, whose plug enters from -y.
//
// The figures come from a CAD model drawn from caliper measurements, and matched the board used
// for the first printed case. Remeasure and change them here; every housing follows. The bracket's
// and the heads' heights were measured from the PCB's top face, and are kept that way.
//
// Use it with `use <probe.scad>`:
//   probe(c)               the board grown by c on every side, to subtract from a housing
//   probe_outline()        the PCB's outline (2D), to open a pocket to a parting plane
//   probe_bbox(c)          [[x0, y0, z0], [x1, y1, z1]] of probe(c)
//   probe_optical_axis()   [x, y] where a tube passes between the heads
//   probe_gap()            the space between the heads' inner faces: the widest tube that fits
//   probe_heads()          [x0, x1, y0, y1, z1]: one head's inner and outer faces, its y extent
//                          (the other head mirrors it in x) and its top
//   probe_pcb()            [thickness, half-width of the body, the y where it narrows to the arms]
//   probe_connector()      [half-width, plug face y, back face y, top z]
//   probe_trimmer()        [x, y] of the RV trimmer's centre, under the PCB

// PCB thickness
pcb_t = 1.5;
// half-width of the PCB body
pcb_hw = 12.15;
// connector-end edge (y)
pcb_y0 = -14.6;
// where the PCB narrows to the two arms (y)
pcb_neck_y = 0.0;
// arm inner edge (half the slot width)
pcb_arm_x0 = 4.35;
// arm outer edge
pcb_arm_x1 = 9.15;
// bottom of the PCB slot (y)
pcb_slot_y = 4.0;
// arm tips (y)
pcb_y1 = 17.7;

// the black head bracket's height above the PCB's top face
bracket_h = 4.5;
// bracket root edge (y)
bracket_y0 = -4.0;
// bracket half-width at the root
bracket_hw0 = 7.65;
// the root widens to the head width from here (y)
flare_y0 = 2.0;
// to here (y)
flare_y1 = 7.7;
// head inner face (half the optical gap)
head_x0 = 4.15;
// head outer face
head_x1 = 9.65;
// bottom of the bracket slot (y)
bracket_slot_y = 5.0;

// the emitter and detector heads' height above the PCB's top face, over y flare_y1..pcb_y1
head_h = 7.5;

// The emitter and detector's optical axis along the arms (y). Not yet measured: this is where the
// first case put its tube, between the heads. Measure where the lenses sit and replace it.
optical_y = 11.4;

// right-angle connector half-width; the plug enters from -y
conn_hw = 5.0;
// connector plug face (y)
conn_y0 = -16.6;
// connector back face (y)
conn_y1 = -9.4;
// connector top (z)
conn_top = 11.0;

// depth of the solder joints, trimmer and legs below the PCB
under_d = 2.5;
// main underside relief half-width
under_hw = 8.75;
// main relief start (y)
under_y0 = -11.35;
// main relief end (y)
under_y1 = 3.0;
// inner edge of the relief under each arm
under_arm_x0 = 4.75;
// start of the relief under each arm (y)
under_arm_y0 = 8.7;
// RV trimmer centre, underside (x)
trim_x = 0.4;
// RV trimmer centre, underside (y)
trim_y = -2.4;

eps = 0.01;

bracket_top = pcb_t + bracket_h;
head_top = pcb_t + head_h;

function probe_optical_axis() = [0, optical_y];
function probe_gap() = 2 * head_x0;
function probe_heads() = [head_x0, head_x1, flare_y1, pcb_y1, head_top];
function probe_pcb() = [pcb_t, pcb_hw, pcb_neck_y];
function probe_connector() = [conn_hw, conn_y0, conn_y1, conn_top];
function probe_trimmer() = [trim_x, trim_y];
function probe_bbox(c = 0) =
  let (hw = max(pcb_hw, bracket_hw0, head_x1, conn_hw, under_hw) + c)
    [
      [-hw, min(pcb_y0, conn_y0, under_y0) - c, -under_d - c],
      [hw, pcb_y1 + c, max(conn_top, head_top, bracket_top, pcb_t) + c],
    ];

module probe_mirror_x() {
  children();
  mirror([1, 0, 0]) children();
}

// Cuboid between two corners.
module probe_box(p0, p1) {
  translate(p0) cube(p1 - p0);
}

module probe_outline() {
  polygon(
    [
      [-pcb_hw, pcb_y0],
      [pcb_hw, pcb_y0],
      [pcb_hw, pcb_neck_y],
      [pcb_arm_x1, pcb_neck_y],
      [pcb_arm_x1, pcb_y1],
      [pcb_arm_x0, pcb_y1],
      [pcb_arm_x0, pcb_slot_y],
      [-pcb_arm_x0, pcb_slot_y],
      [-pcb_arm_x0, pcb_y1],
      [-pcb_arm_x1, pcb_y1],
      [-pcb_arm_x1, pcb_neck_y],
      [-pcb_hw, pcb_neck_y],
    ]
  );
}

module probe_bracket_outline() {
  polygon(
    [
      [-bracket_hw0, bracket_y0],
      [bracket_hw0, bracket_y0],
      [bracket_hw0, flare_y0],
      [head_x1, flare_y1],
      [head_x1, pcb_y1],
      [head_x0, pcb_y1],
      [head_x0, bracket_slot_y],
      [-head_x0, bracket_slot_y],
      [-head_x0, pcb_y1],
      [-head_x1, pcb_y1],
      [-head_x1, flare_y1],
      [-bracket_hw0, flare_y0],
    ]
  );
}

// The board, grown by c on every side. c = 0 is the board itself.
module probe(c = 0) {
  // PCB
  translate([0, 0, -c]) linear_extrude(pcb_t + 2 * c) offset(delta=c) probe_outline();
  // underside relief
  probe_box([-under_hw - c, under_y0 - c, -under_d - c], [under_hw + c, under_y1 + c, eps]);
  probe_mirror_x()
    probe_box([under_arm_x0 - c, under_arm_y0 - c, -under_d - c], [under_hw + c, pcb_y1 + c, eps]);
  // bracket and heads; the bracket and the connector overhang the PCB edge,
  // so they get clearance underneath too
  translate([0, 0, pcb_t - c - eps])
    linear_extrude(bracket_top - pcb_t + 2 * c + eps) offset(delta=c) probe_bracket_outline();
  probe_mirror_x() probe_box([head_x0 - c, flare_y1 - c, pcb_t], [head_x1 + c, pcb_y1 + c, head_top + c]);
  // connector
  probe_box([-conn_hw - c, conn_y0 - c, pcb_t - c - eps], [conn_hw + c, conn_y1 + c, conn_top + c]);
}
