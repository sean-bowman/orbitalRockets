[Home](../README.md) > Spinning and Flow Forming

# Spinning and Flow Forming

## Contents

- [Overview](#overview)
- [Conventional spinning](#conventional-spinning)
- [Shear spinning](#shear-spinning)
- [Flow forming](#flow-forming)
- [Where each belongs](#where-each-belongs)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Three related processes form a rotating blank or preform against a mandrel with a roller. They differ in whether the thickness is meant to change, and that difference makes them three different processes rather than one.

These are the aerospace answers for domes, cones and thin walled cylinders, and flow forming in particular produces motor cases and pressure vessel liners that nothing else makes as well.

---

## Conventional spinning

**A flat blank is progressively formed over a mandrel by a roller, and the thickness stays roughly constant.**

| Property | Value |
|---|---|
| Thickness | Approximately constant |
| **Tooling** | **A single mandrel. Low cost** |
| Tolerance | +/- 0.5 mm |
| Rate | Slow |
| Shapes | Domes, cones, hemispheres, dished ends |

**The material is bent, not stretched**, so the blank diameter has to equal the developed length of the finished profile. Getting that blank size right is the main design calculation.

**Low tooling cost is the reason to use it.** A mandrel is a single turned tool, so a one-off tank dome is far cheaper spun than stretch formed and vastly cheaper than pressed.

**Wrinkling is the characteristic failure.** The blank flange is in circumferential compression as it is drawn down, and it buckles. Multiple passes with a controlled roller path, and sometimes a follower on the back face, are how it is prevented.

**It is slow and operator dependent.** CNC spinning has changed that considerably, and a programmed multi-pass path is repeatable in a way a manual one is not.

---

## Shear spinning

**A flat blank is formed over a mandrel with deliberate, controlled thinning.**

The sine law governs it:

```
t_final = t_blank * sin(alpha)
```

where `alpha` is the half angle of the cone measured from the axis.

| Cone half angle | Thickness ratio |
|---|---|
| 60 deg | 0.87 |
| 45 deg | 0.71 |
| **30 deg** | **0.50** |
| 15 deg | 0.26 |

**The blank diameter equals the finished part diameter**, which is the practical distinction from conventional spinning. There is no draw-in, so there is no flange and no wrinkling.

**A sharp cone thins a great deal**, and at some point the required thinning exceeds the material's capability and the part tears. That sets the minimum achievable cone angle for a given material and blank.

**Steep cones need multiple stages** with intermediate anneals, exactly as any heavily worked forming operation does.

---

## Flow forming

**A thick preform cylinder is extended along a mandrel by rollers, reducing the wall and lengthening the part.**

| Property | Value |
|---|---|
| **Tolerance** | **+/- 0.1 mm, the best in this family** |
| Wall reduction | 50 to 75 % per pass |
| Surface | Excellent, a burnished finish |
| **Properties** | **Improved by the cold work** |

**It is the process for thin walled high strength cylinders**: solid motor cases, COPV metallic liners, pressure vessel shells and gun barrels.

**The properties improve.** The heavy cold work raises the yield strength substantially, and the deformation is uniform around the circumference so the improvement is uniform. A flow formed case is stronger than the preform it came from, and the design allowable can reflect that once it is qualified.

**Concentricity and wall uniformity are excellent** because the part is formed against a mandrel by rollers at fixed radial positions.

**Forward and reverse variants** differ in whether the material flows in the same direction as the roller travel:

| Variant | Material flow | Use |
|---|---|---|
| **Forward** | Same direction as the roller | Closed-end parts |
| **Reverse** | Opposite | Longer parts, both ends open |

**The preform is a significant part of the cost** because it is usually a forged or ring rolled cylinder, machined to a precise starting wall. Flow forming is not a route that starts from stock.

---

## Where each belongs

| Need | Process |
|---|---|
| A dome or dished end, one-off | **Conventional spinning** |
| A cone with a controlled wall | **Shear spinning** |
| A thin walled cylinder to tight tolerance | **Flow forming** |
| Improved properties from cold work | **Flow forming** |
| Lowest tooling cost | Conventional spinning |
| Best surface and concentricity | Flow forming |

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Conventional spinning holds thickness | Blank equals the developed length |
| Shear spinning sine law | `t = t_0 sin(alpha)` |
| Shear spinning blank equals part diameter | No draw-in, no wrinkling |
| Flow forming tolerance | +/- 0.1 mm |
| Flow forming reduction | 50 to 75 % per pass |
| Flow forming raises the yield strength | And it can be qualified |
| Wrinkling is the conventional spinning failure | Multi-pass path, follower |

---

## Failure modes

**Blank size taken as the part diameter in conventional spinning.** Far too small.

**Wrinkling from too aggressive a roller path.** Multiple passes are needed.

**Shear spinning to too steep a cone.** The sine law thinning exceeds the material.

**Flow forming reduction beyond the material's capability in one pass.** Circumferential cracking.

**Flow formed property improvement claimed without qualification.** It is real and it has to be demonstrated.

**Preform wall not precise.** The finished wall inherits the error.

---

## Standards

| Standard | Scope |
|---|---|
| AMS 2750 | Pyrometry, for intermediate anneals |
| AMS 2770 | Heat treatment of wrought aluminium alloys |
| ASTM E8 / E8M | Tension testing, for the worked properties |
| SAE AMS-STD-2154 | Ultrasonic inspection of wrought metals |
| ASTM E2218 | Forming limit curves |

---

## References

1. Wong, C. C., Dean, T. A. and Lin, J., "A Review of Spinning, Shear Forming and Flow Forming Processes", *International Journal of Machine Tools and Manufacture*, Vol. 43, 2003.
2. ASM Handbook Volume 14B, *Metalworking: Sheet Forming*.
3. Hosford, W. F. and Caddell, R. M., *Metal Forming: Mechanics and Metallurgy*, 4th ed., Cambridge, 2011.
