/**
 * @file sampler_actuator.scad
 * @brief The syringe actuator as mounted on the sampler, drawn from the syringe-actuator library
 * @author Cameron K. Brooks
 * @copyright 2026
 *
 * This is a separate file because sampler_case.scad includes NopSCADlib, whose assembly() shadows
 * the one in the actuator library. In this file, the library version is the only one in scope.
 * Actuator frame: x along the syringe axis, the nozzle towards -x, z up from the plate underside.
 * sampler_case.scad places it.
 */

use <syringe-actuator/cad/main.scad>

// The actuator L in its body at crank angle a (180 is the plunger pushed in), with its syringe and
// motor. The mount screws of the body are left out, because the face screws of the sampler go up
// into it instead.
module sampler_actuator(L, a) {
  assembly(L, a, bought=true, body=false);
  color("lightsteelblue", 0.35) {
    body(get(L, "body"));
    lid(get(L, "body"));
    cap(get(L, "body"));
  }
}
