# Secondary References

Researched on `2026-03-31`.

This file collects useful secondary sources. They may help with practical bring-up or
broader design ideas, but they should not outrank the primary vendor and standards
sources documented elsewhere in `research/`.

## Arduino Forum: SEN0189 at 3.3V

A relevant Arduino forum thread discusses using `SEN0189` at `3.3V` instead of the
recommended `5V` supply.

Useful takeaways from that discussion:

- users do encounter unrealistic NTU values when trying to use copied formulas without
  recalibration
- one experienced reply explicitly advises calibrating under the actual electrical
  conditions being used
- the thread also warns that using a lower supply voltage changes emitted light level
  and therefore changes apparent turbidity response

This is not an authoritative source, but it is a practical warning that the full
sensor-plus-electronics transfer function depends on the supply and interface path.

## DFRobot Forum FAQ

The DFRobot forum FAQ is semi-official rather than purely community-authored, so it is
stronger than a random hobbyist post but still weaker than a datasheet.

The most important caution there is that DFRobot explicitly describes `SEN0189` as more
qualitative than quantitative and says conversion to standard NTU is not recommended.

That makes it a useful supporting source whenever community formulas are being compared
or questioned.

## DFRobot Selection Guide

DFRobot's liquid-sensor selection guide is useful because it presents how DFRobot
markets `SEN0189` inside a larger product lineup.

Useful takeaways:

- it lists `SEN0189` as a low-cost, plug-and-play turbidity sensor
- it gives a claimed range of `0-3000 NTU`
- it gives a claimed accuracy of about `+/-10% FS`

Limitation:

- these claims are in tension with DFRobot's own FAQ guidance that standard-NTU
  conversion is not recommended
- for this reason, the guide is useful context but should not outrank the FAQ caution

## Open-Source Turbidity Projects

One useful example of a more instrument-style turbidity effort is the
`rivertechlabs/turbiditysensor` GitHub project, which presents itself as an open-source,
low-cost in-situ turbidity sensor system.

Value to this repo:

- helps show what a more complete field-oriented turbidity system looks like
- suggests where this repo could grow later beyond simple sensor bring-up
- can provide ideas for packaging, system architecture, and deployment thinking

Limitation:

- it is not a drop-in reference for the Amphenol appliance sensors
- it should be treated as adjacent inspiration, not as direct evidence about
  `TST-10`, `TSW-10`, or `SEN0189`

## Recommended Use of Secondary Material

Use secondary sources for:

- pitfalls
- experimental ideas
- sanity checks
- example architectures

Do not use them as the primary source for:

- official electrical limits
- sensor identity
- calibration authority
- standards claims

## Sources

- https://forum.arduino.cc/t/formula-for-measuring-sensor-sen0189-at-3-3-v/991779
- https://www.dfrobot.com/forum/topic/315216
- https://www.dfrobot.com/blog-1138.html
- https://github.com/rivertechlabs/turbiditysensor
