# Test solutions

The bench series uses kaolin suspended in a diluent of DI water with 0.01 % v/v Tween 20.
The recipe is in [`bench/session-1.md`](bench/session-1.md), section 5.

## Tween 20 dose

0.01 % is a chosen value. No published dose for Tween 20 in dilute kaolin suspensions was
found, and kaolin dispersant doses in the literature (about 0.5–1 wt % of the clay) are for
concentrated slurries ([Ceramics 2024](https://doi.org/10.3390/ceramics7030076)), not
tens of mg/L.

The dose is set against Tween 20's critical micelle concentration (CMC): about 0.06 mM, or
0.0074 % w/v at a molecular weight of 1228
([Thermo Fisher 28320](https://www.thermofisher.com/order/catalog/product/28320),
[Sigma-Aldrich 11332465001](https://www.sigmaaldrich.com/deepweb/assets/sigmaaldrich/product/documents/130/724/11332465001.pdf),
[OpenWetWare](https://openwetware.org/wiki/Critical_micelle_concentration_(CMC))).

- Tween 20 wets the kaolin so the stock disperses without clumps. Nonionic surfactants on
  polar solids reach an adsorption plateau around the CMC
  ([Levitz 2002](https://doi.org/10.1016/S1631-0713(02)01806-0)), so more does not coat
  the particles further.
- Above the CMC, extra surfactant forms micelles and foam, and bubbles read as turbidity.
- 0.01 % v/v is about 0.011 % w/v (density about 1.1 g/mL; the SDS gives the exact
  figure), or about 1.5 × the CMC.

Every concentration comes from the one kaolin stock, so the particles' surface state is the same
at every concentration. `03a_clear_di` against `03_clear` checks that the diluent itself
does not change the reading.
