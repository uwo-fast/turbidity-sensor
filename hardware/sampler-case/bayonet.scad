/**
 * @file bayonet.scad
 * @brief The sampler case on a bayonet port: bayonet-port-scad's pin as the base's foot
 * @author Cameron K. Brooks
 * @copyright 2026
 *
 * The case as open-source-bioreactor stands it on its lid: bayonet_std, an 18 mm panel, the
 * riser sealed by a 4x1.5 o-ring. It is also the pattern for any vessel's foot: define what the foot
 * is computed from before the include, set the foot_* figures after it, and pass the foot as the
 * base's child.
 */

use <bayonet-port-scad/custom/bayonet_port.scad>
include <bayonet-port-scad/custom/bayonet_interfaces.scad>

panel = 18; // the lid's thickness at the port

include <sampler_case.scad>

part = "none"; // sampler_case.scad's own drawing, off: this file draws the parts below
piece = "assembly"; // [assembly, case, base, top]
explode = 0; // the step between the base, the top and the actuator, in mm
section = false; // cut away the half towards -y
seals = false; // draw the two o-rings a builder fits: the riser's, in the foot's bore, and the face seal
riser_l = 0; // draw the riser this long, down from its top end in the sleeve; 0 draws none

foot_flange_h = bayonet_flange_height(bayonet_std);
foot_neck_r = bayonet_flange_radius(bayonet_std);
foot_core_r = bayonet_interface_radius(bayonet_std) - bayonet_pin_radius(bayonet_std);
foot_gland_top_z = bayonet_bore_gland_centre(oring_4x1p5_epdm, panel) + bayonet_bore_gland_length(oring_4x1p5_epdm) / 2;

module foot() {
  bayonet_port(type=bayonet_std, part="pin", panel_thickness=panel, center_bore_radius=riser_bore,
               bore_oring=oring_4x1p5_epdm, catch_pockets=false);
}

// The foot's two o-rings, each at its free section. The riser's sits in its gland in the bore, its ID
// on the riser, and overlaps the gland's wall by the squeeze it is fitted with. The face seal sits in
// the groove under the flange, standing proud of it until the foot is locked on the lid.
module foot_seals() { foot_riser_oring(); foot_face_seal(); }
module foot_riser_oring() translate([0, 0, bayonet_bore_gland_centre(oring_4x1p5_epdm, panel)]) oring(oring_4x1p5_epdm);
module foot_face_seal() {
  ring = bayonet_oring(bayonet_std);
  translate([0, 0, bayonet_gland_depth(bayonet_std) - oring_cross_section(ring) / 2]) oring(ring);
}

// The riser, l long, hanging from its top end in the sleeve through the foot's bore and o-ring.
module foot_riser(l) {
  translate([0, 0, riser_top_z - l]) difference() {
    cylinder(d=riser_od, h=l);
    translate([0, 0, -1]) cylinder(d=riser_id, h=l + 2);
  }
}

if (piece == "base") lay(split_z) sampler_base() foot();
else if (piece == "top") lay(face_z) sampler_top();
else if (piece == "assembly" || piece == "case") {
  color("orange") half() sampler_base() foot();
  color("darkorange") half() translate([0, 0, explode]) sampler_top();
  sampler_bought(explode=explode, actuator=piece == "assembly");
  if (seals) color("black") half() foot_seals();
  if (riser_l > 0) color("silver") half() foot_riser(riser_l);
}
