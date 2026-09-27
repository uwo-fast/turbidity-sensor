// Printed flow-through case for the bare DFRobot SEN0189 probe board.
//
// The stock probe housing is removed. The bare probe PCB (emitter and detector
// heads on a U-shaped bracket, right-angle 3-pin connector) drops into the base,
// the lid closes over it, and a clear tube runs vertically through the optical
// slot between the heads.
//
// Frame: origin on the PCB centreline, z = 0 at the PCB underside, +y toward the
// head arms, -y toward the connector. The base sits below z = split_z, the lid above.
//
// Every pocket in both parts is cut from one board envelope grown by `clr`, so the
// two parts cannot disagree about where the board is. The board envelope comes
// from a CAD model of the board, not from measurement: check it with calipers
// before relying on a fit.
//
// Export both parts with `just case`.

/* [Output] */

// which part(s) to render
part = "assembly"; // [assembly, base, lid]
// print: each part flat side down at z = 0
orient = "assembly"; // [assembly, print]

/* [Fit] */
// clearance around the board envelope, per side
clr = 0.2; // [0:0.05:0.5]
// 5/16 in clear tube, nominal outside diameter
tube_od = 7.9375; // [5:0.0025:8.2]
// added to tube_od for the bore diameter
tube_fit = 0.2; // [0:0.05:0.8]
// 45 degree chamfer at each outer end of the tube bore
lead_in = 0.6; // [0:0.1:1.5]
// Number of facets for circular features (higher = smoother)
facets = 96; // [24:8:192]

/* [Case] */
// outside width (x)
case_w = 30;
// outside length (y)
case_l = 40;
// floor below the underside relief
floor_t = 1.0;
// roof above the connector pocket
roof_t = 1.0;
// base/lid parting plane; the PCB top is pcb_t, so the PCB sits recessed
split_z = 2.0;
// tube axis, centred between the heads in x
tube_y = 11.4;
// hole under the RV trimmer (docs/hardware.md: do not adjust RV)
access_hole = true;

/* [Alignment keys] */
// key centreline, mirrored in x
key_x = 12.42;
// key start (y)
key_y0 = 2.5;
// key end (y)
key_y1 = 17.5;
// key width
key_w = 2.0;
// ridge height below the lid; the groove is key_h + key_clr deep
key_h = 1.8;
// clearance around the keys, per side
key_clr = 0.2; // [0:0.05:0.5]

/* [Board envelope: measure your board] */
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

// top of the black head bracket (z)
bracket_top = 4.5;
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

// top of the emitter and detector heads (z), over y flare_y1..pcb_y1
head_top = 7.5;

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
// access hole width (x)
trim_w = 4.0;
// access hole length (y)
trim_l = 5.0;

/* [Hidden] */
eps = 0.01;
bot_z = -(under_d + clr + floor_t);
top_z = conn_top + clr + roof_t;
bore_d = tube_od + tube_fit;

module mirror_x() {
  children();
  mirror([1, 0, 0]) children();
}

module box(x0, x1, y0, y1, z0, z1) {
  translate([x0, y0, z0]) cube([x1 - x0, y1 - y0, z1 - z0]);
}

module pcb_outline() {
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

module bracket_outline() {
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
module board(c = 0) {
  // PCB
  translate([0, 0, -c]) linear_extrude(pcb_t + 2 * c) offset(delta=c) pcb_outline();
  // underside relief
  box(-under_hw - c, under_hw + c, under_y0 - c, under_y1 + c, -under_d - c, eps);
  mirror_x() box(under_arm_x0 - c, under_hw + c, under_arm_y0 - c, pcb_y1 + c, -under_d - c, eps);
  // bracket, heads, connector
  // (both overhang the PCB edge, so they get clearance underneath too)
  translate([0, 0, pcb_t - c - eps]) linear_extrude(bracket_top - pcb_t + 2 * c + eps) offset(delta=c) bracket_outline();
  mirror_x() box(head_x0 - c, head_x1 + c, flare_y1 - c, pcb_y1 + c, pcb_t, head_top + c);
  box(-conn_hw - c, conn_hw + c, conn_y0 - c, conn_y1 + c, pcb_t - c - eps, conn_top + c);
}

module tube_bore() {
  translate([0, tube_y, bot_z - 1]) cylinder(d=bore_d, h=top_z - bot_z + 2, $fn=facets);
  translate([0, tube_y, bot_z - eps])
    cylinder(d1=bore_d + 2 * lead_in, d2=bore_d, h=lead_in + eps, $fn=facets);
  translate([0, tube_y, top_z - lead_in])
    cylinder(d1=bore_d, d2=bore_d + 2 * lead_in, h=lead_in + eps, $fn=facets);
}

module keys(grow = 0, extra_h = 0) {
  mirror_x() box(
      key_x - key_w / 2 - grow, key_x + key_w / 2 + grow,
      key_y0 - grow, key_y1 + grow,
      split_z - key_h - extra_h, split_z + eps
    );
}

module base() {
  difference() {
    box(-case_w / 2, case_w / 2, -case_l / 2, case_l / 2, bot_z, split_z);
    board(clr);
    // open the PCB pocket to the parting plane so the board drops in
    linear_extrude(split_z + 1) offset(delta=clr) pcb_outline();
    tube_bore();
    keys(grow=key_clr, extra_h=key_clr);
    if (access_hole)
      box(
        trim_x - trim_w / 2, trim_x + trim_w / 2, trim_y - trim_l / 2, trim_y + trim_l / 2,
        bot_z - 1, 0
      );
  }
}

module lid() {
  difference() {
    union() {
      box(-case_w / 2, case_w / 2, -case_l / 2, case_l / 2, split_z, top_z);
      keys();
    }
    board(clr);
    // connector window: the plug enters through the -y wall
    box(-conn_hw - clr, conn_hw + clr, -case_l / 2 - 1, conn_y1, split_z - 1, conn_top + clr);
    tube_bore();
  }
}

module tube() {
  translate([0, tube_y, bot_z - 5]) cylinder(d=tube_od, h=top_z - bot_z + 10, $fn=facets);
}

if (part == "base") {
  if (orient == "print")
    translate([0, 0, -bot_z]) base();
  else
    base();
} else if (part == "lid") {
  if (orient == "print")
    translate([0, 0, top_z]) rotate([180, 0, 0]) lid();
  else
    lid();
} else {
  color("orange") base();
  color("gray", 0.5) lid();
  %board();
  %tube();
}
