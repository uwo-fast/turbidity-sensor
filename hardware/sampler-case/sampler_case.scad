/**
 * @file sampler_case.scad
 * @brief Sampler case: a printed case around the turbidity probe board that mounts on a vessel
 *        port, with a syringe actuator bolted on top to draw culture through it
 * @author Cameron K. Brooks
 * @copyright 2026
 *
 * Two printed parts. The base is a foot with a skirt out to the case, and the floor under the
 * board. The top holds the board, split at the PCB underside, and extends into a shroud that flares
 * out to the face the actuator bolts to. The board drops into the top upside down and the base
 * closes it. A clear tube runs through both parts between the heads of the board. The dip tube is
 * the vessel riser, bushed into the bottom of the clear tube.
 *
 * The foot mounts the base on the vessel port, and its design belongs to the vessel. This file
 * draws everything above the foot, and checks its fits against the foot dimensions (foot_*,
 * below). A file that provides a foot passes it as the child of sampler_base(), sampler_placed()
 * or sampler_print(), and sets the foot_* dimensions to match. `include` this file and set
 * `part = "none"` to draw nothing from it. Order matters with `include`: OpenSCAD uses the last
 * value assigned to a variable, evaluated where this file first assigns it. So set foot_* (and
 * anything else this file defines) after the include, and define the values they are computed
 * from (panel, bayonet_std) before it. The defaults match the bayonet pin on the standard port of
 * open-source-bioreactor (bayonet_std, 18 mm panel, 4x1.5 riser o-ring).
 *
 * Port frame: origin on the port axis at the outer face of the lid, +z out of the vessel, +x
 * radially outward. The fits are checked by `just check-sampler-case` (tests/sampler-case/fit.scad).
 */

use <../probe/probe.scad>
use <syringe-actuator/cad/main.scad>
use <sampler_actuator.scad>
include <NopSCADlib/core.scad>
include <NopSCADlib/vitamins/screws.scad>
include <NopSCADlib/vitamins/nuts.scad>
include <NopSCADlib/vitamins/inserts.scad>

part = "assembly"; // [assembly, base, top, none]
// print: lay the base upside down on its parting face, the top face-down on its 4-hole face
orient = "print"; // [print, assembly]
$fn = 64;

// ---- the foot ----
// Dimensions of the vessel port that the case is checked against. Defaults: the bayonet pin of
// open-source-bioreactor on bayonet_std, 18 mm panel, 4x1.5 riser o-ring, read from its port
// library at open-source-bioreactor f3c35f0.
foot_flange_h = 5;       // height of the foot flange top above the lid, where the case neck starts
foot_neck_r = 14.1;      // flange radius, which the case neck continues straight up
foot_core_r = 8.8;       // radius inside the foot pin that the tube seat may use
foot_gland_top_z = -14.55; // top of the riser o-ring gland in the foot, which the seat must clear
flange_h = foot_flange_h;

// ---- sources ----
// riser: 4 x 0.5 steel tube; the bore for it is 0.2 over its radius
riser_od = 4;
riser_id = 3;
riser_bore = riser_od / 2 + 0.2;
// from hardware/tube-case/README.md: the clear tube is 5/16 in OD and 1/4 in ID, and a bore
// 0.2 over its OD holds it snugly
tube_od = 7.9375;
tube_id = 6.35;
tube_fit = 0.2;
// syringe-actuator layout for the syringe, in the actuator frame: x along the syringe axis, the
// nozzle towards -x, z up from the plate underside. The holes and outline of its front face are
// [y, z]. Only 5ml-gnr2, the syringe the sampler uses, has been fit-tested. The other 5 mL layouts
// render but are unverified. The 1, 3, 10, 20 and 30 mL layouts do not build: syringe-actuator has
// not measured their nozzle_l, which sets the face position.
syringe = "5ml-gnr2"; // [5ml-gnr1, 5ml-gnr2, 5ml-gnr1-ga25, 5ml-gnr2-ga25]
act = actuator(syringe);
act_body = get(act, "body");
holes = get(act_body, "mount_front");
axis_z = get(act, "axis_z");
syringe_past_face = front_x(act) - tip_x(act);
barrel_od = get(get(act, "syringe"), "barrel_od");
// front wall of the actuator, end_t thick
actuator_wall = get(act_body, "end_t");
// the front face in the port frame, with its motor side (-z) facing out along +x
face_outline = [for (p = front_face(act_body)) to_port(p)];
// luer-to-barb fitting, from the syringe tip to the top end of the clear tube (measured). Its barb
// is heat-set into the top end of the clear tube and stretches the last 18 mm of the tube to 9.75
// diameter (measured)
fitting_l = 5;
barb_l = 18;
barb_od = 9.75;
// Fasteners. Base to top: heat-set inserts, as used in the head's motor mount, from the
// registered rows. Screws and nuts are from NopSCADlib. Actuator to face: screws up from
// counterbores under the face, with nuts inside the front wall of the actuator, so the actuator
// fits on over bare screw ends.
outer_screw = M3_dome_screw;   // ISO 7380, from below at the outer corners
outer_screw_l = 8;
// heat-set inserts, as NopSCADlib insert rows: name, length, outer d, hole d, screw d, ...
outer_insert = ["M3x5.56 18-8", 5.56, 4.6,     3.57,   3,     3.65,     1.6,     4.4,     3.9,     undef, undef,   "97163A150", "18-8 SS", 10];
inner_screw = M2_cs_cap_screw; // ISO 10642, from above at the inner end
inner_screw_l = 6;
inner_insert = ["M2x4.78 18-8", 4.78, 3.6,     2.71,   2,     3.0,      1.0,     3.4,     3.1,     undef, undef,   "97163A124", "18-8 SS", 1];
face_screw = M3_cap_screw;     // ISO 4762, up through the face into the actuator
face_screw_l = 10;
face_nut = M3nS_thin_nut;     // DIN 562 square: it cannot turn as the screw is driven from below

// ---- design parameters ----
clr = 0.2;        // around the board, per side; the proven fit from the tube case
wall = 2;         // case side walls around the board pocket
floor_t = 1.2;    // under the relief
roof_t = 1.2;     // over the connector
min_wall = 0.8;   // minimum thickness for any of them
corner_r = 4;
neck_h = 1;       // the case overhangs the neighbours' flanges, and clears them by the lid's 1 mm
neck_r = foot_neck_r; // the foot flange continues straight up into the skirt
// A skirt from the neck out to the outline, formed as the hull of the two, so the underside slopes
// into the neck instead of stepping. It faces up when the base prints upside down.
skirt_h = 8;
riser_under_window = 2;
// length of clear tube over the top of the riser, with a 1/8 x 1/4 in silicone sleeve between
// them. 6 held too little, and a print drilled about 10 deeper held it.
bushing_l = 16;
// seat for the clear tube in the base, wider than bore_r: the sleeve swells the end of the tube,
// and a test print needed 8.5 to 8.6 diameter there
tube_seat_d = 8.6;
clamp_t = 2.2;      // base thickness under the head of each outer screw
seat_t = 2.5;       // top thickness under the countersink of the inner screw
shroud_id = barrel_od + 1;
shroud_wall = 2.4;
plate_t = 5;
lead_in = 0.6;
// fastener holes, from their rows
outer_cbore_d = 2 * screw_head_radius(outer_screw) + 0.5;
outer_insert_d = 2 * insert_hole_radius(outer_insert);
outer_insert_l = insert_hole_length(outer_insert) + 1;
inner_clear_d = 2 * screw_clearance_radius(inner_screw);
inner_seat_d = 2 * screw_head_radius(inner_screw) + 0.6;
inner_insert_d = 2 * insert_hole_radius(inner_insert);
inner_insert_l = insert_hole_length(inner_insert) + 0.5;
face_clear_d = 2 * screw_clearance_radius(face_screw);
face_cbore_d = 2 * screw_head_radius(face_screw) + 0.5;
face_clamp_t = 2.5;  // face thickness over the head of each face screw
// across-flats size of the hex key that turns the face screws from below. Its corners sweep a
// circle as it turns, and that circle is kept clear straight up from the parting face into each
// head.
face_key_d = 2.5;

// ---- derived ----
pocket = probe_bbox(clr);            // board frame, including clearance
face_key_sweep = face_key_d / cos(30); // diameter swept by the key corners as it turns
axis = probe_optical_axis();         // where the clear tube runs, board frame
split_b = -clr;                      // parting plane, board frame: the floor of the PCB pocket
bot_b = pocket[0][2] - floor_t;      // underside of the base, board frame
top_b = pocket[1][2] + roof_t;       // top of the roof, board frame
base_z0 = flange_h + neck_h + skirt_h;  // underside of the base, port frame
board_z = base_z0 - bot_b;              // board z = 0, port frame
split_z = board_z + split_b;
roof_z = board_z + top_b;
window_z = board_z + probe_pcb()[0];    // bottom edge of the heads
riser_top_z = window_z - riser_under_window;
clear_z0 = riser_top_z - bushing_l;
bore_r = (tube_od + tube_fit) / 2;
tube_seat_r = tube_seat_d / 2;
// The tube is snug only between the heads. Above their tops, its bore opens at 45 degrees to the
// shroud bore, so the tube drops in, and its stretched end sits where the cone is wider than it.
heads_top_z = board_z + probe_heads()[4] + clr;
tube_top_z = heads_top_z + (barb_od + tube_fit) / 2 - bore_r + barb_l;
face_z = tube_top_z + fitting_l + syringe_past_face;
plate_z0 = face_z - plate_t;
shroud_r = shroud_id / 2 + shroud_wall;
function to_port(p) = [axis_z - p[1], p[0]]; // actuator [y, z] to port [x, y], with its motor side out
// The pocket in the port frame: board y runs outward along -x from the axis
pocket_x = [axis[1] - pocket[1][1], axis[1] - pocket[0][1]];  // [inner, outer]
// the inner screw is just outside the shroud tube, and its slot keeps min_wall to the inner end.
// Its head sits flush with the top of the countersink.
inner_screw_x = -(shroud_r + inner_seat_d / 2 + 0.1);
inner_head_z = split_z + seat_t + (inner_seat_d - inner_clear_d) / 2;
// the outline: the pocket and its walls, wide enough for the slot of the inner screw. Its inner
// end is a half-circle as wide as the case.
half_w = max(pocket[1][0] + wall, -inner_screw_x + inner_seat_d / 2 + min_wall);
// each outer screw is at the centre of a rounded corner, with its insert min_wall clear of the
// outer end of the pocket, so its counterbore keeps the same wall thickness all round
outer_screw_x = pocket_x[1] + min_wall + outer_insert_d / 2;
outer_x = outer_screw_x + corner_r;
outer_screws = [for (s = [-1, 1]) [outer_screw_x, s * (half_w - corner_r)]];
outline_reach = norm([outer_x - corner_r, half_w - corner_r]) + corner_r;
top_skirt_h = outline_reach - shroud_r; // 45 degrees where it reaches farthest
flare_h = max([for (p = face_outline) norm(p)]) - shroud_r;

assert(tube_od < probe_gap(), "the clear tube does not pass between the heads");
assert(half_w >= neck_r, "the pin's flange reaches past the case's inner end, which would overhang");
assert(min(wall, floor_t, roof_t) >= min_wall, "a wall is thinner than min_wall");
assert(corner_r - outer_cbore_d / 2 >= min_wall, "an outer screw's counterbore breaks the rounded corner");
assert(inner_screw_x + inner_seat_d / 2 < pocket_x[0] - min_wall, "the inner screw's seat runs into the pocket");
assert(riser_top_z < split_z, "the riser's top reaches up into the top part");
assert(tube_seat_r + min_wall <= foot_core_r, "the clear tube's seat breaks out of the foot's core");
assert(clear_z0 - (tube_seat_r - riser_bore) > foot_gland_top_z + min_wall, "the clear tube's seat reaches the riser's o-ring");
assert(plate_z0 - flare_h > roof_z + top_skirt_h, "the face's flare reaches down into the top skirt");
assert(min([for (h = holes) abs(to_port(h)[1])]) - (face_key_sweep / 2 + clr) - pocket[1][0] >= min_wall,
       "a face screw's key groove leaves less than min_wall to the board's pocket");

echo(str("sampler: case ", outer_x + half_w, " x ", 2 * half_w, ", face ", face_z, " over the lid; clear tube cut ",
         tube_top_z - clear_z0, "; the riser's top ", riser_top_z, " over the lid"));

// The board in the port frame: optical axis on the port axis, connector end outward (+x).
module board_place() {
  translate([0, 0, board_z]) rotate([0, 0, 90]) translate([-axis[0], -axis[1], 0]) children();
}

module outline() {
  offset(r=corner_r) offset(delta=-corner_r) hull() {
    translate([0, -half_w]) square([outer_x, 2 * half_w]);
    circle(r=half_w, $fn=192);
  }
}

// Hulls each child with the next: one solid through the sections in order, with no stepped seam
module loft() for (i = [0 : $children - 2]) hull() { children(i); children(i + 1); }

// A round section for a loft, at height z
module disk(r, z) translate([0, 0, z]) cylinder(r=r, h=0.01, $fn=128);

// A blind hole up from z = 0, open 1 below it, with a 45 degree point at its end so it prints
// either way up
module drill(d, h) {
  translate([0, 0, -1]) cylinder(d=d, h=h + 1);
  translate([0, 0, h - 0.01]) cylinder(r1=d / 2, r2=0, h=d / 2);
}

// The slot between the heads where the clear tube passes, board frame, from z0 to z1. Without it,
// the round tube bore would clip the head pockets and leave knife-edge cusps in the beam path.
module tube_slot(half, z0, z1) {
  translate([-half, axis[1] - bore_r - 0.5, z0]) cube([2 * half, pocket[1][1] - axis[1] + bore_r + 0.5, z1 - z0]);
}

// The base, with the foot (passed as its child) unioned in, so the riser bore and the tube seat
// cut through both and the base stays one print.
module sampler_base() {
  difference() {
    union() {
      children();
      loft() {
        disk(neck_r, flange_h - 1);
        disk(neck_r, flange_h + neck_h);
        translate([0, 0, base_z0]) linear_extrude(split_z - base_z0) outline();
      }
    }
    // the relief under the board, opened past the inner edges of the arm reliefs across the tube
    // path, with its floor level with theirs so it bridges in the same layer when printed
    board_place() {
      probe(clr);
      tube_slot(probe_heads()[0] + 0.5, pocket[0][2], split_b + 0.01);
    }
    // the clear tube seat, with a lead-in from the split, and the riser bore below it. The seat
    // narrows to the riser bore at 45 degrees. This still stops the end of the tube (its outside
    // wall meets the cone immediately) and prints upside down with nothing to bridge.
    translate([0, 0, clear_z0]) cylinder(r=tube_seat_r, h=split_z - clear_z0 + 1);
    translate([0, 0, clear_z0 - (tube_seat_r - riser_bore) + 0.01]) cylinder(r1=riser_bore, r2=tube_seat_r, h=tube_seat_r - riser_bore);
    translate([0, 0, split_z - lead_in]) cylinder(r1=tube_seat_r, r2=tube_seat_r + lead_in, h=lead_in + 0.01);
    translate([0, 0, flange_h - 2]) cylinder(r=riser_bore, h=clear_z0 - flange_h + 3);
    // the outer screws, from below: clearance through to the split, counterbored up from the
    // underside to leave clamp_t under the head
    for (p = outer_screws) translate([each p, 0]) {
      translate([0, 0, split_z - clamp_t - 1]) cylinder(r=screw_clearance_radius(outer_screw), h=clamp_t + 2);
      translate([0, 0, base_z0]) cylinder(d=outer_cbore_d, h=split_z - clamp_t - base_z0);
      // below the top edge of the skirt the underside slopes in, so the counterbore opens straight
      // out to the corner there. This leaves a clean notch, not a wall that thins to nothing around
      // its mouth.
      hull() for (o = [[0, 0], [20, sign(p[1]) * 20]]) translate([each o, -1]) cylinder(d=outer_cbore_d, h=base_z0 + 1.01);
    }
    // insert for the inner screw, from the split down
    translate([inner_screw_x, 0, split_z]) mirror([0, 0, 1]) drill(inner_insert_d, inner_insert_l);
  }
}

module sampler_top() {
  difference() {
    // the case, its skirt up into the shroud tube at 45 degrees where it reaches farthest, and
    // the flare out to the face. Nothing exceeds 45 degrees when the top prints face-down.
    loft() {
      translate([0, 0, split_z]) linear_extrude(roof_z - split_z) outline();
      disk(shroud_r, roof_z + top_skirt_h);
      disk(shroud_r, plate_z0 - flare_h);
      translate([0, 0, plate_z0]) linear_extrude(plate_t) polygon(face_outline);
    }
    // inserts for the outer screws, from the split up
    for (p = outer_screws) translate([each p, split_z]) drill(outer_insert_d, outer_insert_l);
    // the inner screw: clearance through seat_t, a 90 degree countersink, and a slot up through the
    // skirt and out through the inner end for the driver
    translate([inner_screw_x, 0, 0]) {
      translate([0, 0, split_z - 1]) cylinder(d=inner_clear_d, h=seat_t + 1.01);
      translate([0, 0, split_z + seat_t]) cylinder(r1=inner_clear_d / 2, r2=inner_seat_d / 2, h=inner_head_z - split_z - seat_t);
      hull() for (x = [0, -50]) translate([x, 0, inner_head_z - 0.01]) cylinder(d=inner_seat_d, h=roof_z + top_skirt_h - inner_head_z + 2);
    }
    board_place() {
      probe(clr);
      // The board goes in upside down, heads first, so the whole board must pass through the PCB
      // layer: the heads are wider than the arms, and the connector overhangs the end of the PCB
      translate([0, 0, split_b - 1]) linear_extrude(probe_pcb()[0] + clr - split_b + 1) projection() probe(clr);
      // the tube slot, open all the way from the parting face to the tops of the heads
      tube_slot(probe_heads()[0] + 0.1, split_b - 1, probe_heads()[4] + clr);
      // connector window: the plug enters through the outer end
      conn = probe_connector();
      translate([-conn[0] - clr, -50, split_b - 1]) cube([2 * (conn[0] + clr), 50 + conn[2], conn[3] + clr - split_b + 1]);
    }
    // clear tube bore, snug up to the tops of the heads, then a 45 degree cone out to the shroud bore
    _cone = shroud_id / 2 - bore_r;
    translate([0, 0, split_z - 1]) cylinder(r=bore_r, h=heads_top_z - split_z + 1.01);
    translate([0, 0, heads_top_z]) cylinder(r1=bore_r, r2=shroud_id / 2, h=_cone + 0.01);
    translate([0, 0, heads_top_z + _cone]) cylinder(d=shroud_id, h=face_z - heads_top_z - _cone + 1);
    // actuator screws: clearance through face_clamp_t, counterbored down and out through the
    // underside of the flare, where they are inserted. Below each, a groove runs from the head down
    // the side of the case and out through the parting face, so the long arm of a key reaches the
    // head straight up from the top of the base.
    for (h = holes) translate([each to_port(h), 0]) {
      translate([0, 0, face_z - face_clamp_t - 1]) cylinder(d=face_clear_d, h=face_clamp_t + 2);
      translate([0, 0, plate_z0 - flare_h]) cylinder(d=face_cbore_d, h=face_z - face_clamp_t - plate_z0 + flare_h);
      _head = face_z - face_clamp_t - screw_head_height(face_screw);
      translate([0, 0, split_z - 1]) cylinder(d=face_key_sweep + 2 * clr, h=_head - split_z + 1.01);
    }
  }
}

// Every fastener in place: the outer screws from below with their inserts in the top, the inner
// screw from above with its insert in the base, and the actuator screws and nuts. lift raises each
// head that far off its seat, so a check sees a seated head as contact, not overlap.
module sampler_fasteners(inserts=true, lift=0) {
  for (p = outer_screws) {
    translate([each p, split_z - clamp_t - lift]) rotate([180, 0, 0]) screw(outer_screw, outer_screw_l);
    if (inserts) translate([each p, split_z]) rotate([180, 0, 0]) insert(outer_insert);
  }
  translate([inner_screw_x, 0, inner_head_z + lift]) screw(inner_screw, inner_screw_l);
  if (inserts) translate([inner_screw_x, 0, split_z]) insert(inner_insert);
  for (h = holes) translate([each to_port(h), 0]) {
    translate([0, 0, face_z - face_clamp_t - lift]) rotate([180, 0, 0]) screw(face_screw, face_screw_l);
    translate([0, 0, face_z + actuator_wall]) nut_square(face_nut);
  }
}

// The actuator in the port frame: its x (the syringe axis, nozzle towards -x) down the port z,
// the outside of its front face on the sampler face, and its [y, z] turned by to_port.
module actuator_place() {
  multmatrix([[0, 0, -1, axis_z], [0, 1, 0, 0], [1, 0, 0, face_z - front_x(act)], [0, 0, 0, 1]]) children();
}

// With section, the half towards -y is cut away from each part separately, so a colour applied
// outside it covers the cut face. A part that sets its own colours inside keeps them, and the
// outer colour reaches only its cut face. A full render (--render) keeps the colours. A preview
// draws every cut face in one colour.
section = false;
module half() if (section) difference() {
  children();
  translate([-500, -1000, -500]) cube(1000);
} else children();
// The same for a part that sets its own colours: its cut face is drawn in c, and nothing else changes.
module half_in(c) if (section) color(c) half() children(); else children();

// Every bought part in place except the dip tube, which the head cuts and draws with the other
// tubes: the board, the clear tube with its stretched top end, the silicone sleeve over the top of
// the riser, the luer-to-barb fitting (simplified to its barb and hub), the fasteners, and the
// actuator in its body, with the plunger at crank angle a (180 is pushed in). explode lifts the
// parts that go in the top by that distance and the actuator by twice that, and stands each
// fastener head off its seat by the same distance.
module sampler_bought(a = 180, explode = 0, actuator = true) {
  translate([0, 0, explode]) {
    color("darkgreen") half() board_place() probe();
    color("white", 0.5) half() difference() {
      union() {
        translate([0, 0, clear_z0]) cylinder(d=tube_od, h=tube_top_z - barb_l - clear_z0);
        translate([0, 0, tube_top_z - barb_l]) cylinder(d=barb_od, h=barb_l);
      }
      translate([0, 0, clear_z0 - 1]) cylinder(d=tube_id, h=tube_top_z - clear_z0 + 2);
    }
    color("whitesmoke") half() {
      translate([0, 0, tube_top_z - barb_l]) cylinder(d=tube_id, h=barb_l);
      translate([0, 0, tube_top_z]) cylinder(d=barb_od, h=fitting_l);
    }
    half_in("silver") sampler_fasteners(lift=explode);
  }
  color("gainsboro") half() difference() {
    translate([0, 0, clear_z0]) cylinder(d=tube_id, h=bushing_l);
    translate([0, 0, clear_z0 - 1]) cylinder(d=riser_od, h=bushing_l + 2);
  }
  if (actuator) half_in("gainsboro") translate([0, 0, 2 * explode]) actuator_place() sampler_actuator(act, a);
}

// print orientation: turned over about z
module lay(z) if (orient == "print") translate([0, 0, z]) rotate([180, 0, 0]) children(); else children();

// Values a vessel design uses to place the sampler, all in the port frame: the height of the top
// end of the riser, the top of the face, and the length of the clear tube.
function sampler_riser_top_z() = riser_top_z;
function sampler_face_z() = face_z;
function sampler_clear_tube_cut() = tube_top_z - clear_z0;
// Values a vessel design uses to cut and check its sample line. Length of the silicone sleeve over
// the top of the riser.
function sampler_sleeve_l() = bushing_l;
// The syringe row, and the volume one stroke draws: the actuator stroke (2 x the crank throw)
// times the syringe bore area (nominal, from the syringe row).
function sampler_syringe() = get(act, "syringe");
function sampler_stroke_ml() = PI * pow(get(get(act, "syringe"), "bore_d") / 2, 2) * 2 * get(act, "throw") / 1000;
// Volume of the line from the open end of a riser, riser_l below its top, up the clear tube to the
// top of the heads. A stroke must move this volume before the culture at the beam is culture drawn
// from the inlet. The top of the heads is used because the probe library does not record the
// height of the lens windows.
function sampler_line_ml(riser_l) =
  (riser_l * PI * pow(riser_id / 2, 2) + (heads_top_z - riser_top_z) * PI * pow(tube_id / 2, 2)) / 1000;
// The two prints in the port frame, as they stand on the lid, with the foot passed as the child.
// Each sets its own facets, because a file that uses this one does not inherit its $fn.
module sampler_base_placed() {
  $fn = 64;
  sampler_base() children();
}
module sampler_top_placed() {
  $fn = 64;
  sampler_top();
}
module sampler_placed() {
  $fn = 64;
  sampler_base() children();
  sampler_top();
}
// One print as it lies on the bed, with the foot of the base passed as the child.
module sampler_print(part) {
  $fn = 64;
  if (part == "base") translate([0, 0, split_z]) rotate([180, 0, 0]) sampler_base() children();
  else if (part == "top") translate([0, 0, face_z]) rotate([180, 0, 0]) sampler_top();
  else assert(false, str("sampler_print: no part \"", part, "\""));
}

if (part == "base") lay(split_z) sampler_base();
else if (part == "top") lay(face_z) sampler_top();
else if (part == "assembly") {
  color("orange") sampler_base();
  color("darkorange") sampler_top();
  sampler_bought();
}
