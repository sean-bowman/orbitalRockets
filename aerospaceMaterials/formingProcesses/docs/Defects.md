[Home](../README.md) > Defects

# Forming Defects

## Contents

- [Overview](#overview)
- [The catalogue](#the-catalogue)
- [Splitting](#splitting)
- [Wrinkling](#wrinkling)
- [Orange peel](#orange-peel)
- [Luders bands](#luders-bands)
- [Bulk forming defects](#bulk-forming-defects)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Forming defects divide cleanly into two families: tensile instabilities, where the material ran out of ductility, and compressive instabilities, where it buckled. The fixes are opposite, which is why identifying which one is happening comes first.

---

## The catalogue

| Defect | Family | Cause | Fix |
|---|---|---|---|
| **Splitting** | Tensile | Strain beyond the forming limit | More ductile temper, larger radius, better lubrication |
| **Necking** | Tensile | Strain beyond uniform elongation | Same |
| **Wrinkling** | Compressive | Insufficient blank holder force, or a compressive flange | More holder force, draw beads |
| **Buckling** | Compressive | Slender section in compression | Support, or redesign |
| **Orange peel** | Surface | Coarse grain | Finer grain material |
| **Luders bands** | Surface | Discontinuous yielding | Temper roll, or form above the strain |
| Springback out of tolerance | Elastic | Uncompensated | Overbend, coin |
| Earing | Anisotropy | `r`-value varies with direction | Trim, or a lower anisotropy material |
| **Laps and folds** | Bulk | Material folded over itself | Preform design |

---

## Splitting

**The tensile failure, and the FLD is the tool for predicting it.**

| Cause | Fix |
|---|---|
| **Plane strain region over the limit** | Redesign the shape, or change temper |
| Insufficient uniform elongation | Form annealed |
| Small punch or die radius | Increase it |
| Poor lubrication | The material cannot flow in |
| Excessive blank holder force | Reduce it |

**Splits appear at the plane strain regions first**, not at the biaxially stretched ones, which is counter-intuitive and is the main thing the FLD teaches. See [FormingLimitDiagram.md](FormingLimitDiagram.md).

**A split at the punch radius in drawing means too much blank holder force**, because the material is being prevented from flowing in from the flange and is being stretched at the punch instead. That is the same knob that fixes wrinkling, in the other direction.

---

## Wrinkling

**The compressive instability, and it is a buckling problem rather than a strength problem.**

The flange of a drawn part is in circumferential compression as it is pulled into a smaller diameter, and an unsupported thin flange buckles.

| Cause | Fix |
|---|---|
| **Insufficient blank holder force** | More |
| Thin sheet, large flange | Draw beads, or a stepped holder |
| Uneven material flow | Balance the blank shape |
| Unsupported curved region | Support tooling |

**Blank holder force sits between wrinkling and splitting** and the window can be narrow. Too little and the flange wrinkles; too much and the wall splits. Finding the window is a large part of die tryout.

**A wrinkled flange cannot enter the die**, so the defect is self-compounding: once wrinkling starts, the increased thickness jams the clearance and the part is scrap.

**Draw beads are the more sophisticated control.** They restrain the material locally by bending and unbending it as it passes, which lets the flow be tuned around the perimeter rather than set by one global force.

---

## Orange peel

**A rough dimpled surface on a stretched region, and it is a grain size problem.**

Each grain deforms slightly differently according to its orientation, and if the grains are large enough their individual deformation becomes visible on the surface.

| Cause | Fix |
|---|---|
| **Coarse grain in the incoming material** | Specify a grain size |
| Overheating during an intermediate anneal | Control the anneal |

**It is cosmetic on most parts and functional on some.** On a sealing surface or a fatigue critical surface the roughness matters, and on an external surface it is a finish rejection.

**Specifying a maximum grain size on the incoming sheet is the fix**, and ASTM E112 grain size 6 or finer is a typical requirement for a stretched aerospace skin.

---

## Luders bands

**Visible flame-shaped bands on the surface of low carbon steel and some aluminium alloys**, from discontinuous yielding.

The material has an upper and lower yield point, and deformation propagates as a front rather than uniformly. The front leaves a visible surface step.

| Cause | Fix |
|---|---|
| **Discontinuous yielding** | **Temper roll** the sheet before forming |
| Aluminium-magnesium alloys | Form soon after annealing, or accept it |

**Temper rolling gives the sheet a small pre-strain** that takes it past the yield point discontinuity, so the subsequent forming is uniform. It is standard for automotive body panel steel and it has a shelf life: the discontinuity returns with strain ageing over weeks to months.

**In 5000 series aluminium it is a Portevin-Le Chatelier effect** from dynamic strain ageing, and it cannot be temper rolled away. It is a known limitation of forming 5083 and similar alloys to a cosmetic surface.

---

## Bulk forming defects

| Defect | Cause | Fix |
|---|---|---|
| **Laps and folds** | Material folded over itself and not bonded | Preform design |
| **Underfill** | Insufficient material or force | More stock, more force |
| **Die wear** | Progressive dimensional drift | Die maintenance schedule |
| **Flow through** | Grain flow cut by the flash line | Die and preform design |
| Central burst | Tensile hydrostatic stress in the core | Reduce per-pass reduction |

**Laps are the serious one.** Folded material with an oxide between the faces does not bond, so a lap is a crack with a crack's stress intensity. They are found by macro-etch and by penetrant after machining, and they scrap the forging.

**Flow through is a grain flow defect rather than a discontinuity.** The material flows past the die cavity into the flash, carrying the grain flow with it and leaving the part's flow pattern cut off. It passes every NDE method and it costs the forging its main advantage.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Tensile and compressive families | Opposite fixes |
| Splits appear at plane strain first | Not at biaxial |
| Split at the punch radius | Too much holder force |
| Wrinkled flange | Too little |
| Draw beads tune the flow locally | Better than one global force |
| Specify grain size for stretched surfaces | E112 grade 6 or finer |
| Temper roll for Luders | And it has a shelf life |
| Laps are cracks | Macro-etch and penetrant |

---

## Failure modes

**Holder force raised to fix a split.** It causes them.

**Holder force lowered to fix wrinkling without checking the wall.** It splits instead.

**Coarse grain sheet stretched to a visible surface.** Orange peel.

**Temper rolled sheet stored for months.** Strain ageing restored the discontinuity.

**Lap missed because radiography was clean.** It is planar and tight.

**Flow through undetected.** Every NDE method passes it.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM E112** | Determining average grain size |
| ASTM E2218 | Determining forming limit curves |
| ASTM E517 | Plastic strain ratio r |
| ASTM E381 | Macroetch testing of steel, for laps and flow |
| ASTM E1417 | Liquid penetrant testing |
| AMS 2154 | Ultrasonic inspection of wrought products |

---

## References

1. Marciniak, Z., Duncan, J. L. and Hu, S. J., *Mechanics of Sheet Metal Forming*, 2nd ed., Butterworth-Heinemann, 2002.
2. Hosford, W. F. and Caddell, R. M., *Metal Forming: Mechanics and Metallurgy*, 4th ed., Cambridge, 2011.
3. ASM Handbook Volume 14A and 14B, *Metalworking*.
