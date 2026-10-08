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
// two parts cannot disagree about where the board is. The board, its envelope and
// its figures live in ../probe/probe.scad; this file adds only the case's own
// choices.
//
// Export both parts with `just case`.

use <../probe/probe.scad>

/* [Output] */

// which part(s) to render
part = "assembly"; // [assembly, base, lid]
// print: lay base or lid flat side down at z = 0 (ignored for the assembly)
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
// base/lid parting plane; the PCB top is probe_pcb()[0], so the PCB sits recessed
split_z = 2.0;
// hole under the RV trimmer (docs/hardware.md: do not adjust RV)
access_hole = true;
// access hole width (x)
access_w = 4.0;
// access hole length (y)
access_l = 5.0;

/* [Alignment keys] */
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

/* [Hidden] */
eps = 0.01;
// thinnest wall the asserts below accept
min_wall = 0.8;

// the board's pocket, its clearance included
pocket = probe_bbox(clr);
bot_z = pocket[0][2] - floor_t;
top_z = pocket[1][2] + roof_t;
bore_d = tube_od + tube_fit;
// the tube on the board's optical axis
tube_y = probe_optical_axis()[1];
// key centreline, halfway between the head pocket and the outer wall
key_x = (case_w / 2 + probe_heads()[1] + clr) / 2;
// widest pocket half-width and pocket y extents
pocket_hw = pocket[1][0];
pocket_y0 = pocket[0][1];
pocket_y1 = pocket[1][1];

assert(tube_od < probe_gap(), "tube_od: the tube must fit between the heads (probe_gap())");
assert(min(floor_t, roof_t) >= min_wall, "floor_t, roof_t: thinner than min_wall");
assert(case_w / 2 - pocket_hw >= min_wall, "case_w: the side walls are thinner than min_wall");
assert(
  pocket_y0 + case_l / 2 >= min_wall && case_l / 2 - pocket_y1 >= min_wall,
  "case_l: the end walls are thinner than min_wall"
);
assert(
  tube_y + bore_d / 2 + lead_in + min_wall <= case_l / 2,
  "tube_y, tube_od: the tube bore breaks through the end wall"
);
assert(lead_in < min(split_z - bot_z, top_z - split_z), "lead_in: deeper than a part is thick");
assert(
  key_x - key_w / 2 - key_clr - (probe_heads()[1] + clr) >= min_wall
  && case_w / 2 - (key_x + key_w / 2 + key_clr) >= min_wall,
  "key_w, key_clr: the key groove walls are thinner than min_wall"
);
assert(
  key_y0 < key_y1 && key_y0 - key_clr - (probe_pcb()[2] + clr) >= min_wall
  && case_l / 2 - (key_y1 + key_clr) >= min_wall,
  "key_y0, key_y1: the keys must run along the arms, clear of the PCB body and the end wall"
);
assert(
  split_z - key_h - key_clr - bot_z >= min_wall,
  "key_h: the key groove breaks through the floor"
);

module mirror_x() {
  children();
  mirror([1, 0, 0]) children();
}

// Cuboid between two corners.
module box(p0, p1) {
  translate(p0) cube(p1 - p0);
}

// The case outline, from z0 to z1.
module slab(z0, z1) {
  box([-case_w / 2, -case_l / 2, z0], [case_w / 2, case_l / 2, z1]);
}

// Lay a part flat for printing when orient = "print": flip it if asked, then lift it by lift.
module pose(lift, flip = false) {
  if (orient == "print")
    translate([0, 0, lift]) rotate([flip ? 180 : 0, 0, 0]) children();
  else
    children();
}

module tube_bore() {
  $fn = facets;
  translate([0, tube_y, bot_z - 1]) cylinder(d=bore_d, h=top_z - bot_z + 2);
  translate([0, tube_y, bot_z - eps])
    cylinder(d1=bore_d + 2 * lead_in, d2=bore_d, h=lead_in + eps);
  translate([0, tube_y, top_z - lead_in])
    cylinder(d1=bore_d, d2=bore_d + 2 * lead_in, h=lead_in + eps);
}

// The lid's alignment keys, grown by c on every side but the top. c = key_clr cuts the grooves.
module keys(c = 0) {
  mirror_x() box(
      [key_x - key_w / 2 - c, key_y0 - c, split_z - key_h - c],
      [key_x + key_w / 2 + c, key_y1 + c, split_z + eps]
    );
}

module base() {
  difference() {
    slab(bot_z, split_z);
    probe(clr);
    // open the PCB pocket to the parting plane so the board drops in
    linear_extrude(split_z + 1) offset(delta=clr) probe_outline();
    tube_bore();
    keys(key_clr);
    if (access_hole)
      box(
        [probe_trimmer()[0] - access_w / 2, probe_trimmer()[1] - access_l / 2, bot_z - 1],
        [probe_trimmer()[0] + access_w / 2, probe_trimmer()[1] + access_l / 2, 0]
      );
  }
}

module lid() {
  difference() {
    union() {
      slab(split_z, top_z);
      keys();
    }
    probe(clr);
    // connector window: the plug enters through the -y wall
    conn = probe_connector();
    box([-conn[0] - clr, -case_l / 2 - 1, split_z - 1], [conn[0] + clr, conn[2], conn[3] + clr]);
    tube_bore();
  }
}

module tube() {
  translate([0, tube_y, bot_z - 5]) cylinder(d=tube_od, h=top_z - bot_z + 10, $fn=facets);
}

if (part == "base") {
  pose(-bot_z) base();
} else if (part == "lid") {
  pose(top_z, flip=true) lid();
} else {
  color("orange") base();
  color("gray", 0.5) lid();
  %probe();
  %tube();
}
