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

foot_flange_h = bayonet_flange_height(bayonet_std);
foot_neck_r = bayonet_flange_radius(bayonet_std);
foot_core_r = bayonet_interface_radius(bayonet_std) - bayonet_pin_radius(bayonet_std);
foot_gland_top_z = bayonet_bore_gland_centre(oring_4x1p5_epdm, panel) + bayonet_bore_gland_length(oring_4x1p5_epdm) / 2;

module foot() {
  bayonet_port(type=bayonet_std, part="pin", panel_thickness=panel, center_bore_radius=riser_bore,
               bore_oring=oring_4x1p5_epdm, catch_pockets=false);
}

if (piece == "base") lay(split_z) sampler_base() foot();
else if (piece == "top") lay(face_z) sampler_top();
else if (piece == "assembly" || piece == "case") difference() {
  union() {
    color("orange") sampler_base() foot();
    color("darkorange") translate([0, 0, explode]) sampler_top();
    sampler_bought(explode=explode, actuator=piece == "assembly");
  }
  if (section) translate([-500, -1000, -500]) cube(1000);
}
