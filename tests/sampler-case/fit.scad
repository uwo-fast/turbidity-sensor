// Fit checks for the sampler. Each check draws the material that should not exist, so this file
// renders empty while every fit holds. `just check-sampler-case` fails on anything it draws.
// It uses the bayonet foot (the bayonet-port-scad pin), so the fits are checked against the
// dimensions of a real foot rather than the case defaults.
include <../../hardware/sampler-case/bayonet.scad>
piece = "none";

module parts() { sampler_base() foot(); sampler_top(); }

// the board inside either part
intersection() { board_place() probe(); parts(); }
// the board pocket grown by min_wall, outside the case: a wall that is too thin
difference() {
  board_place() probe(clr + min_wall);
  translate([0, 0, board_z + bot_b]) linear_extrude(top_b - bot_b) outline();
}
// the clear tube, from its seat to its top end including the length the barb stretches, inside
// either part
intersection() {
  union() {
    translate([0, 0, clear_z0 + 0.05]) cylinder(d=tube_od, h=tube_top_z - clear_z0 - 0.05, $fn=96);
    translate([0, 0, tube_top_z - barb_l]) cylinder(d=barb_od, h=barb_l, $fn=96);
  }
  parts();
}
// the board swept 20 straight down out of its seat, inside the top: it cannot go in
intersection() {
  minkowski() {
    board_place() probe();
    translate([0, 0, -20]) cylinder(r=0.001, h=20, $fn=4);
  }
  sampler_top();
}
// the shank of a 1.6 mm hex key on the inner screw, tilted 10 degrees outward, inside the top:
// out of reach
intersection() {
  translate([inner_screw_x, 0, inner_head_z + 0.3]) rotate([0, -10, 0]) cylinder(d=1.6, h=150, $fn=16);
  sampler_top();
}
// the hex key for the face screws, turning, with half its clearance around it, straight up into
// each head from below the parting face, inside the top: out of reach, or a skin left over the
// groove mouth
intersection() {
  for (h = holes) translate([each to_port(h), split_z - 1])
    cylinder(d=face_key_sweep + clr, h=face_z - face_clamp_t - screw_head_height(face_screw) - split_z + 1, $fn=48);
  sampler_top();
}
// any screw or nut inside either part, with each head 0.01 off its seat. The inserts are left out,
// because a heat-set insert melts into its hole.
intersection() { sampler_fasteners(inserts=false, lift=0.01); parts(); }
// the ends of the face screws and their nuts inside the actuator frame or behind its front wall:
// no room for them there. Each nut has a flat facing the side wall of the body, 0.4 from it, which
// also stops it turning.
intersection() {
  sampler_fasteners(inserts=false);
  translate([0, 0, face_z - front_x(act)]) rotate([0, -90, 0]) translate([0, 0, -axis_z]) {
    frame(get(act, "frame"));
    difference() {
      body(act_body);
      translate([front_x(act) - 1, -100, -100]) cube([actuator_wall + 1, 200, 200]);
    }
  }
}
// the riser, from its top end in the sleeve down through the foot and past it, inside either part: the
// bore pinches it
intersection() { foot_riser(riser_top_z + panel + 10); parts(); }
// the riser o-ring, inside the gland radius, inside either part: the gland does not hold it, or
// the bore below or above it pinches it. Outside that radius it meets the gland wall by its
// squeeze. The check stops 0.05 inside the radius, so the facets of the two cylinders do not meet.
intersection() {
  foot_riser_oring();
  translate([0, 0, -panel - 1]) cylinder(r=bayonet_bore_gland_radius(oring_4x1p5_epdm) - 0.05, h=panel + 2, $fn=96);
  parts();
}
// the face seal at its free cross-section inside either part: its groove under the flange is too small
intersection() { foot_face_seal(); parts(); }
