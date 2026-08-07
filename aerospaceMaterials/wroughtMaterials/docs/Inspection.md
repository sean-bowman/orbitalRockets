[Home](../README.md) > Inspection

# Inspection

## Contents

- [Overview](#overview)
- [Ultrasonic](#ultrasonic)
- [Chemistry](#chemistry)
- [Mechanical acceptance](#mechanical-acceptance)
- [Metallography](#metallography)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Wrought material inspection is mill inspection, and the acceptance is on the lot rather than on the part. The engineering decision is which classes and tests to invoke, because most of them are optional in the base specification.

---

## Ultrasonic

**The primary volumetric method for wrought product**, and it looks for the inclusions, laminations and porosity that survived working.

| Class | Reference reflector | Use |
|---|---|---|
| **A** | 3/64 in flat bottom hole | General |
| **AA** | 2/64 in | Critical |
| **AAA** | 1/64 in | **Fracture critical** |

**The class has to be invoked.** A base specification like ASTM B209 does not require ultrasonic inspection at all; the class comes from AMS 2154 or MIL-STD-2154, called out separately.

**Class selection follows from the critical flaw size.** A fracture mechanics analysis gives the largest flaw the part can tolerate; the ultrasonic class has to detect something smaller than that with margin. Choosing the class without that analysis is guessing.

**Coarse grain attenuates the beam**, which is a real limitation in thick titanium and nickel sections and in castings. It raises the noise floor and can hide the very discontinuities the inspection is for.

**Ultrasonic is oriented.** A lamination parallel to the plate surface reflects a normal-incidence beam well; a discontinuity normal to the surface does not. Angle beam inspection covers the second case and it has to be specified.

---

## Chemistry

| Method | Use |
|---|---|
| **Optical emission spectroscopy** | The mill method. Full quantitative analysis |
| **XRF** | Handheld PMI. Fast, and it misses light elements |
| Combustion analysis | **Carbon, sulphur.** XRF cannot see them |
| Inert gas fusion | **Oxygen, nitrogen, hydrogen.** Critical for titanium |

**XRF cannot measure carbon**, which means it cannot distinguish 316 from 316L. That is a significant limitation for incoming verification, because the L designation is exactly the thing that governs sensitization.

**Inert gas fusion for interstitials is mandatory for titanium** because the oxygen content is what separates standard grade from ELI, and it is not visible by any other quick method.

**Lithium is also invisible to XRF**, so Al-Li alloys need spectroscopy for verification.

---

## Mechanical acceptance

| Test | Frequency | Notes |
|---|---|---|
| **Tensile** | Per lot | **Orientation must be stated** |
| Hardness | Per piece or per lot | A fast heat treat verification |
| Bend | Per lot, for sheet | Ductility |
| Impact | Per lot, where toughness governs | Charpy, at temperature |
| Fracture toughness | Rarely per lot | Usually from the qualification |

**Test specimen orientation and location have to be specified**, and for thick plate this is not a formality. A specimen from near the surface of a 100 mm plate has better properties than one from the core, and the specification usually calls for the least favourable location.

**Hardness is the cheapest heat treat verification** and it correlates well enough with strength within an alloy and condition to catch a missed or wrong treatment.

**Lot acceptance testing does not verify the part.** It verifies the material the part was made from, before machining, before welding, before anything the shop did. Anything downstream needs its own verification.

---

## Metallography

| Purpose | Standard |
|---|---|
| **Grain size** | ASTM E112 |
| **Inclusion content** | ASTM E45 |
| **Grain flow** | ASTM E381, macroetch |
| **Alpha case depth** | Section and microhardness traverse |
| Sensitization | ASTM A262 |
| Delta phase, in IN718 | Specific etchants |

**Grain size is worth specifying** where formability or fatigue matters. A stretched aerospace skin needs a fine grain to avoid orange peel; a creep application wants a coarse one.

**Macroetch for grain flow is a forging acceptance requirement** and it is the only way to verify that the flow follows the contour as the drawing intended. See [formingProcesses Forging.md](../../formingProcesses/docs/Forging.md).

**Alpha case depth needs a section** and it cannot be measured non-destructively with any reliability, which is why titanium heat treat is controlled by process rather than verified per part.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Ultrasonic class must be invoked | It is not in the base spec |
| Class follows from the critical flaw size | Not from convention |
| Angle beam for normal-oriented discontinuities | Specify it |
| XRF cannot see carbon | It cannot distinguish 316 from 316L |
| Inert gas fusion for titanium interstitials | ELI verification |
| State the tensile specimen orientation and location | |
| Lot acceptance verifies the material, not the part | |
| Macroetch for forging grain flow | The only verification |

---

## Failure modes

**Ultrasonic class not invoked.** Whatever the mill ships.

**Class chosen by convention.** No relation to the critical flaw size.

**XRF used to verify an L grade.** It cannot.

**Titanium ELI verified without interstitial analysis.** Unverified.

**Specimen location unspecified for thick plate.** Optimistic results.

**Lot acceptance assumed to cover the finished part.** It covers the stock.

**Coarse grain attenuation ignored.** Discontinuities hidden by noise.

---

## Standards

| Standard | Scope |
|---|---|
| **AMS 2154 / MIL-STD-2154** | Ultrasonic inspection of wrought metals, classes A, AA, AAA |
| ASTM E2375 | Ultrasonic testing of wrought products |
| **ASTM E8 / E8M** | Tension testing |
| ASTM E18 / E10 | Rockwell and Brinell hardness |
| ASTM E23 | Notched bar impact testing |
| **ASTM E112** | Determining average grain size |
| ASTM E45 | Inclusion content of steel |
| ASTM E381 | Macroetch testing |
| ASTM E1447 | Hydrogen in titanium by inert gas fusion |
| ASTM E1409 | Oxygen and nitrogen in titanium |

---

## References

1. ASM Handbook Volume 17, *Nondestructive Evaluation and Quality Control*.
2. MMPDS-2023, *Metallic Materials Properties Development and Standardization*.
3. MIL-STD-2154, *Inspection, Ultrasonic, Wrought Metals, Process For*.
