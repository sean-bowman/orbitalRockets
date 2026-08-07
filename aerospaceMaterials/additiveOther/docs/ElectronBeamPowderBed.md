[Home](../README.md) > Electron Beam Powder Bed

# Electron Beam Powder Bed Fusion

## Contents

- [Overview](#overview)
- [The differences from LPBF](#the-differences-from-lpbf)
- [Why the residual stress is low](#why-the-residual-stress-is-low)
- [The sintered cake](#the-sintered-cake)
- [What it achieves](#what-it-achieves)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

EB-PBF is a powder bed process like LPBF, using an electron beam in vacuum on a powder bed held at 600 to 750 degC. The hot bed is the whole difference, and it changes the residual stress, the support requirements, the surface finish and the materials that can be processed.

---

## The differences from LPBF

| | LPBF | EB-PBF |
|---|---|---|
| **Energy** | Laser, 200 to 1000 W | **Electron beam, 3 to 6 kW** |
| **Atmosphere** | Argon or nitrogen | **Vacuum** |
| **Bed temperature** | 80 to 200 degC | **600 to 750 degC** |
| **Residual stress** | **High** | **Very low** |
| Beam deflection | Galvanometer mirrors | **Electromagnetic. Very fast, no inertia** |
| Layer thickness | 20 to 60 um | 50 to 200 um |
| **Rate** | 20 to 80 cm^3/h | **55 to 110 cm^3/h** |
| **Tolerance** | **IT8** | IT10 |
| Surface | 8 to 20 um Ra | **20 to 40 um Ra. Rougher** |
| Materials | Wide | **Conductive only.** Ti and Ni dominate |

**Electromagnetic beam deflection has no moving parts**, so the beam can be moved at speeds a galvanometer cannot approach, and it can be split to maintain several melt pools at once.

**Vacuum is required for the beam** and it has a side benefit: no atmospheric contamination at all, which suits titanium.

---

## Why the residual stress is low

**The bed is held near the stress relief temperature throughout the build.**

| Mechanism | Detail |
|---|---|
| **Small thermal gradient** | The melt pool cools into a 700 degC bed, not a 150 degC one |
| **Continuous stress relief** | The material sits at temperature for the whole build |
| Slow cooldown | The whole build cools together at the end |

**The consequence list is long and it is what makes EB-PBF worth the trade:**

| Consequence | Detail |
|---|---|
| **No post-build stress relief needed** | It happened during the build |
| **Fewer supports** | Supports in LPBF mostly resist stress, not gravity |
| **Overhangs down to ~30 degrees** | Against 45 for LPBF |
| **Larger parts without distortion** | |
| **Crack prone alloys become processable** | Solidification cracking needs stress |

**The support reduction is the largest practical benefit.** LPBF supports exist mainly to anchor the part against thermal distortion, and removing them is a significant part of LPBF post-processing cost. EB-PBF needs far fewer.

**Crack prone superalloys are processable** in EB-PBF that are not in LPBF, because solidification and liquation cracking are driven by thermal stress and the hot bed removes most of it.

---

## The sintered cake

**The powder surrounding the part lightly sinters at the bed temperature**, which is EB-PBF's characteristic complication.

| Consequence | Detail |
|---|---|
| **The part is embedded in a solid cake** | Not loose powder |
| **Powder removal is a blasting operation** | Not a pour-out |
| **Internal channels are very hard to clear** | The cake is inside them |
| Powder recovery | It is broken up and re-sieved |
| Support removal | Easier. The supports are weakly sintered too |

**Internal passages are the real limitation.** An LPBF part with a small internal channel is emptied by pouring and vibrating; an EB-PBF part has sintered cake in that channel that has to be blasted out through the same small opening.

**That, plus the rougher surface, is why EB-PBF is not used for the fine internal geometry that LPBF handles.**

**Powder recovery is a blasting process** using the same alloy powder as the blast media, so nothing foreign is introduced.

---

## What it achieves

| Property | Value |
|---|---|
| Tolerance | IT10 |
| Surface | 20 to 40 um Ra |
| Build volume | ~350 mm |
| Minimum wall | 0.6 to 1.0 mm |
| **Materials** | **Ti-6Al-4V, TiAl, IN718, CoCr.** Conductive only |
| Properties | Comparable to LPBF after HIP |

**Ti-6Al-4V is the dominant material** and EB-PBF is the standard route for additive titanium orthopaedic implants and for aerospace titanium where the geometry suits.

**Titanium aluminide is the alloy EB-PBF uniquely enables.** TiAl is extremely crack prone and it is essentially unprocessable by LPBF; the hot bed makes it work, and TiAl turbine blades are in production by EB-PBF.

**Non-conductive materials cannot be processed** because the electron beam charges them, and the accumulated charge repels the powder in a phenomenon called smoke: the bed is blown apart. That excludes ceramics and it limits some alloys.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Hot bed, 600 to 750 degC | The whole difference |
| No post-build stress relief needed | |
| Overhangs to ~30 degrees | Against 45 for LPBF |
| Far fewer supports | They resist stress, not gravity |
| Crack prone alloys become processable | TiAl in particular |
| Sintered cake, not loose powder | Blasting, not pouring |
| **Avoid small internal channels** | The cake cannot be cleared |
| Conductive materials only | Or the bed smokes |

---

## Failure modes

**Small internal channels designed.** The sintered cake cannot be removed.

**LPBF surface finish expected.** EB-PBF is 2 to 3x rougher.

**Non-conductive material attempted.** Smoke, and the build fails.

**LPBF support strategy applied.** Far more support than needed.

**Powder recovery underestimated.** It is a blasting operation.

**LPBF process parameters transferred.** Different layer thickness, different everything.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM F2924** | Additive manufactured Ti-6Al-4V by powder bed fusion |
| ASTM F3001 | Additive manufactured Ti-6Al-4V ELI |
| **NASA-STD-6030** | Additive manufacturing requirements for spaceflight |
| ISO/ASTM 52900 / 52911 | Terminology and powder bed fusion design |
| ASTM F3049 | Characterising metal powders |
| ASTM E1441 | Computed tomography imaging |

---

## References

1. Gibson, I., Rosen, D. and Stucker, B., *Additive Manufacturing Technologies*, 3rd ed., Springer, 2021.
2. Korner, C., "Additive Manufacturing of Metallic Components by Selective Electron Beam Melting", *International Materials Reviews*, Vol. 61, 2016.
3. NASA-STD-6030, *Additive Manufacturing Requirements for Spaceflight Systems*.
