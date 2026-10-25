// Flange that holds a TST-10, in its stock housing, over a beaker so the
// probe hangs down into the liquid.

$fn = $preview ? 32 : 96;

thickness = 5;
outer_diameter = 80; // larger than the vessel's opening
inner_diameter = 34; // fits the TST-10 housing
hole_separation = 44; // centre to centre, across the flange
hole_diameter = 4;

difference() {
  cylinder(h=thickness, d=outer_diameter);
  translate([0, 0, -1])
    cylinder(h=thickness + 2, d=inner_diameter);
  for (angle = [0, 90, 180, 270])
    rotate(angle)
      translate([hole_separation / 2, 0, -1])
        cylinder(h=thickness + 2, d=hole_diameter);
}
