[Home](../README.md) > Friction Stir Welding

# Friction Stir Welding

## Contents

- [Overview](#overview)
- [The process](#the-process)
- [Why it works where fusion does not](#why-it-works-where-fusion-does-not)
- [The zones](#the-zones)
- [What it achieves](#what-it-achieves)
- [Variants](#variants)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

A rotating non-consumable tool is plunged into the joint line and traversed, stirring the material together in the solid state. It welds the aluminium alloys that cannot be fusion welded, and it is the reason modern launch vehicle tanks look the way they do.

---

## The process

| Element | Detail |
|---|---|
| **Tool** | A shouldered pin, non-consumable, in a hard tool material |
| **Rotation** | 200 to 2000 rpm, material dependent |
| **Traverse** | 50 to 500 mm/min |
| **Forge force** | Substantial. The tool is pressed into the joint |
| **Backing** | A rigid anvil. **Required** |

**The heat comes from friction and plastic work**, and it takes the material to 70 to 90 percent of its melting point: hot enough to flow, not hot enough to melt.

**The forge force is large** and it is why FSW needs a stiff machine and a rigid backing anvil. A gantry FSW machine for a tank barrel is a substantial structure.

**The tool wears** and in hard materials it wears quickly, which is why FSW is dominated by aluminium. Steel and titanium FSW needs polycrystalline boron nitride tooling and it is a specialist operation.

---

## Why it works where fusion does not

**No melting means no solidification, and solidification is where fusion welding's problems come from.**

| Fusion problem | FSW |
|---|---|
| **Hot cracking** | **None.** Nothing solidifies |
| Porosity from dissolved gas | None |
| Solidification shrinkage | None |
| **Cast fusion zone structure** | **Replaced by a fine recrystallised structure** |
| Filler and dilution | No filler |
| Distortion from a large heat input | Much less |

**7075 and 2024 can be friction stir welded** and they cannot be fusion welded. That single fact opened high strength aluminium to welded construction.

**The stirred zone is finer grained than the parent**, because the severe deformation at temperature dynamically recrystallises it. That is why the stirred zone is often not the weakest part of the joint.

---

## The zones

| Zone | Structure | Strength |
|---|---|---|
| **Nugget (stir zone)** | **Fine recrystallised** | Often near parent, sometimes higher |
| **Thermomechanically affected** | Deformed, not recrystallised | Reduced |
| **Heat affected** | **Overaged, not deformed** | **Usually the weakest** |
| Parent | Unaffected | 1.00 |

**The HAZ is still the weak point**, and that is the important limitation. FSW removes the fusion zone problems and it does not remove the overageing of a precipitation hardened alloy beside the weld.

**The HAZ is narrower than a fusion weld's** because the heat input is lower, so less material is knocked down.

**Efficiency is 0.80 to 0.95 in 2219** against roughly 0.70 for a fusion weld, and the improvement comes from both the better nugget and the narrower HAZ.

---

## What it achieves

| Property | FSW | Fusion |
|---|---|---|
| **Efficiency, 2219** | **0.80 to 0.95** | 0.70 |
| Weldable alloys | **Including 7075, 2024** | Not those |
| Distortion | **Low** | Higher |
| Porosity | **None** | Possible |
| Repeatability | **Very high.** Machine controlled | Operator dependent |
| Position | **Any, with the right machine** | Any |

**Repeatability is underrated.** FSW parameters are machine settings, so a qualified weld schedule produces the same weld every time. A manual GTAW weld does not, which is why welder qualification is such a large part of fusion welding quality.

**It is the launch vehicle tank process** and it is used on the longitudinal barrel seams, the circumferential joints and the dome gores on essentially every current vehicle.

---

## Variants

| Variant | Detail |
|---|---|
| **Self-reacting (bobbin)** | A tool with shoulders on both faces. **No backing anvil needed** |
| **Retractable pin** | The pin withdraws at the end, filling the exit hole |
| Friction stir spot welding | A spot equivalent, for sheet |
| **Friction stir processing** | Not a joint. Local structure refinement |
| Stationary shoulder | Better surface, less heat |

**The exit hole is the classic FSW problem.** At the end of a weld the pin withdraws and leaves a hole the size of the pin, which has to be outside the part, filled, or eliminated with a retractable pin tool.

**Self-reacting tools eliminate the backing anvil**, which is what makes circumferential welds on a closed tank possible. A conventional tool needs support on the inside face; a bobbin tool provides its own.

**Friction stir processing is not joining at all.** The same tool is traversed over a surface to refine the structure, close casting porosity or homogenise a weld, and it is used to repair and improve castings.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Solid state, 70 to 90 % of melting | No solidification problems |
| Welds 7075 and 2024 | Which fusion does not |
| Efficiency 0.80 to 0.95 in 2219 | Against 0.70 fusion |
| **The HAZ is still the weak point** | Overageing is not avoided |
| Rigid backing anvil required | Unless self-reacting |
| Plan for the exit hole | Or use a retractable pin |
| Repeatability is a machine property | Not an operator one |
| Tool wear limits it in hard materials | Aluminium dominates |

---

## Failure modes

**No backing support.** The material is pushed out of the joint rather than stirred.

**Insufficient forge force.** A root defect, and it is a lack of penetration.

**Traverse too fast for the rotation.** A wormhole void along the weld.

**Exit hole left in the part.** A hole.

**HAZ knockdown assumed eliminated.** It is reduced, not removed.

**Joint gap outside tolerance.** FSW is intolerant of fit-up gaps.

---

## Standards

| Standard | Scope |
|---|---|
| **AWS D17.3** | Friction stir welding for aerospace applications |
| AWS D8.17 | Friction stir welding of aluminium alloys |
| NASA-STD-5006 | General welding requirements |
| ISO 25239 | Friction stir welding, aluminium |
| ASTM E1417 / E2700 | Penetrant and phased array ultrasonic |

---

## References

1. Mishra, R. S. and Ma, Z. Y., "Friction Stir Welding and Processing", *Materials Science and Engineering R*, Vol. 50, 2005.
2. Threadgill, P. L. et al., "Friction Stir Welding of Aluminium Alloys", *International Materials Reviews*, Vol. 54, 2009.
3. AWS D17.3, *Specification for Friction Stir Welding of Aluminum Alloys for Aerospace Applications*.
