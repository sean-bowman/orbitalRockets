[Home](../README.md) > Sheet Metal Forming

# Sheet Metal Forming

## Contents

- [Overview](#overview)
- [Brake bending](#brake-bending)
- [Roll forming](#roll-forming)
- [Deep drawing](#deep-drawing)
- [Stretch forming](#stretch-forming)
- [Choosing between them](#choosing-between-them)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Four processes cover most sheet work. They differ in how the material is fed into the deformation, and that difference decides both what shapes they make and how they fail.

---

## Brake bending

**The simplest and the most flexible.** A punch presses the sheet into a die to form a straight bend.

| Property | Value |
|---|---|
| Minimum r/t | 1.0 |
| Tolerance | +/- 0.5 mm |
| Tooling | Low. Standard punches and dies |
| Rate | Slow, one bend at a time |

**Variants** differ in how far the punch descends:

| Variant | Detail | Springback |
|---|---|---|
| **Air bending** | The punch does not bottom. The angle is set by the depth | High, and it varies |
| **Bottoming** | The punch bottoms in the die | Lower |
| **Coining** | The material is compressed at the bend | **Lowest**, and the force is very high |

**Air bending is flexible and inconsistent.** One tool set makes any angle, and the angle depends on the punch depth, the material thickness and the material strength, all of which vary lot to lot.

**Coining removes springback by plastically deforming the whole thickness**, and it needs perhaps five to ten times the force. It is used where the angle tolerance is tight.

**Bend sequence matters.** Each bend has to leave room for the tooling to reach the next one, and a sequence that works on paper can be impossible on the machine.

---

## Roll forming

**Sheet is passed through successive roll stands, each adding a little of the final shape.**

| Property | Value |
|---|---|
| Minimum r/t | 2.0 |
| Tolerance | +/- 1.0 mm |
| Tooling | Medium to high, a full roll set |
| Rate | **Fast** |

**It makes long constant cross sections** and nothing else. Channels, hat sections, stringers and skins with a constant curvature.

**Roll bending of plate into a cylinder is the related operation** and it is how tank barrel sections are made: plate through a three-roll or four-roll bender to a constant radius, then longitudinally welded.

**The ends are the problem in roll bending.** The leading and trailing edges of the plate are not fully formed because they have not passed through all three rolls, and they come out flat. Pre-bending the ends, or leaving trim allowance, is the standard answer.

---

## Deep drawing

**A blank is drawn into a die cavity by a punch, with a blank holder controlling the material flow.**

| Property | Value |
|---|---|
| Minimum r/t | 3.0 |
| Tolerance | +/- 0.3 mm |
| Tooling | **High.** Matched punch, die and blank holder |
| Rate | Fast |

**The limiting drawing ratio is about 2.0** for most materials, meaning a blank no more than twice the punch diameter. Deeper cups need redrawing operations, with an anneal between them.

**Blank holder force is the critical parameter and it is a narrow window:**

| Force | Result |
|---|---|
| **Too low** | **Wrinkling** in the flange, which then cannot enter the die |
| **Too high** | **Splitting** at the punch radius, because the material cannot flow in |

**The r-value governs drawability**, more than `n` does. The plastic strain ratio `r` measures the material's preference for thinning against narrowing, and a high `r` means the material draws in from the flange rather than thinning at the wall.

**Earing is the anisotropy signature.** A drawn cup develops a wavy rim because `r` varies with direction in the sheet, and the ears have to be trimmed off.

---

## Stretch forming

**The sheet is gripped at its edges and stretched over a form block.**

| Property | Value |
|---|---|
| Minimum r/t | 4.0 |
| Tolerance | +/- 1.0 mm |
| Tooling | **Medium. A single form block** |
| Rate | Slow |

**It is the aerospace skin process.** Wing skins, fuselage panels and tank domes are stretch formed, because the tooling is a single male block rather than a matched set and because it produces large gently curved shapes.

**Springback is almost eliminated** because the whole section is stretched into the plastic range. That is the process's main advantage over pressing: there is no elastic core to spring back.

**Everything thins.** Unlike drawing, no material flows in from a flange, so the entire strain is thinning strain. A stretch formed skin is thinner than its blank everywhere, and the thinning has to be in the stress analysis.

**The grip material is scrap** and it is a real fraction of the blank, which makes the buy-to-fly worse than the process's reputation suggests.

---

## Choosing between them

| Need | Process |
|---|---|
| A few straight bends | **Brake** |
| Long constant section, at rate | **Roll forming** |
| A cup or closure, at rate | **Deep drawing** |
| A large gently curved skin | **Stretch forming** |
| Tight angle tolerance | Brake, coined |
| Low tooling cost | Brake or stretch |

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Brake minimum r/t | 1.0 |
| Coining removes springback | At 5 to 10x the force |
| Limiting drawing ratio | ~2.0 |
| Blank holder force window | Wrinkle below, split above |
| `r`-value governs drawability | More than `n` |
| Stretch forming eliminates springback | The whole section goes plastic |
| Stretch forming thins everywhere | Put it in the stress analysis |
| Roll bending leaves flat ends | Pre-bend or trim |

---

## Failure modes

**Air bending angle assumed repeatable.** It varies with lot thickness and strength.

**Blank holder force too low.** Wrinkling.

**Blank holder force too high.** Splitting at the punch radius.

**Draw ratio above 2.0 in one operation.** Splitting. It needs a redraw.

**Earing not trimmed.** The cup rim is wavy and out of tolerance.

**Stretch forming thinning ignored.** The skin is thinner than the drawing everywhere.

**Bend sequence not checked against tool access.** Unbuildable.

---

## Standards

| Standard | Scope |
|---|---|
| ASTM E290 | Bend testing for ductility |
| **ASTM E517** | Plastic strain ratio r for sheet metal |
| ASTM E646 | Tensile strain hardening exponents |
| ASTM E2218 | Determining forming limit curves |
| SAE ARP1917 | Sheet metal forming terminology |

---

## References

1. Marciniak, Z., Duncan, J. L. and Hu, S. J., *Mechanics of Sheet Metal Forming*, 2nd ed., Butterworth-Heinemann, 2002.
2. Hosford, W. F. and Caddell, R. M., *Metal Forming: Mechanics and Metallurgy*, 4th ed., Cambridge, 2011.
3. ASM Handbook Volume 14B, *Metalworking: Sheet Forming*.
