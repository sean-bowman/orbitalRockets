[Home](../README.md) > Inspection

# Joint Inspection

## Contents

- [Overview](#overview)
- [What each method finds](#what-each-method-finds)
- [Radiography](#radiography)
- [Ultrasonic and phased array](#ultrasonic-and-phased-array)
- [Penetrant](#penetrant)
- [Proof testing](#proof-testing)
- [Inspectability as a design requirement](#inspectability-as-a-design-requirement)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

The methods complement each other and each has a blind spot. A joint inspected by one method has been inspected for one class of defect.

---

## What each method finds

| Method | Finds | Misses |
|---|---|---|
| **Visual** | Geometry, undercut, colour | **Everything internal** |
| **Penetrant** | Surface breaking | **Everything subsurface.** Anything smeared or peened closed |
| **Radiography** | **Volumetric**: porosity, slag, LOP | **Planar: lack of fusion, tight cracks** |
| **Ultrasonic** | **Planar**: LOF, cracks, laminations | Small volumetric. Coarse grain attenuates it |
| **Phased array** | Both, with imaging | Requires access and skill |
| **Proof test** | Gross inadequacy | **Nothing about margin** |
| Leak test | Through-leaks | Structural adequacy |

**A critical weld gets radiography and ultrasonic**, because their blind spots are complementary.

**Phased array ultrasonic has largely replaced both on new work** because it images the weld volume, records the data, and finds both defect classes. It costs skill and access.

---

## Radiography

| Property | Value |
|---|---|
| **Sensitivity** | ~2 % of section thickness |
| **Best at** | Rounded volumetric defects |
| **Worst at** | Planar defects at an angle to the beam |
| Record | Permanent, and reviewable |

**Image quality indicators are what make the result meaningful.** A radiograph without a penetrameter demonstrating the achieved sensitivity is an image, not an inspection.

**Digital radiography has displaced film** and it gives better contrast sensitivity, immediate results and a digital record. The acceptance criteria are unchanged.

**Double wall single image techniques** are used on small pipe where the source cannot be placed inside, and they carry a geometric penalty that has to be accounted in the sensitivity.

---

## Ultrasonic and phased array

| Method | Detail |
|---|---|
| **Conventional UT** | A single transducer, manually scanned. Operator dependent |
| **Phased array (PAUT)** | An array, electronically steered. **Imaged and recorded** |
| **Time of flight diffraction (TOFD)** | Sizes defects accurately by diffraction from the tips |

**Phased array is the current standard for critical weld inspection** because it produces a recorded image of the weld volume that can be reviewed later, which conventional UT does not.

**TOFD sizes defects better than any other method** because it measures the diffracted signal from the crack tips rather than the reflection from its face, which makes the measurement insensitive to the defect orientation.

**Coarse grain attenuation limits all of them** in austenitic weld metal, which is a genuinely difficult ultrasonic material. Austenitic welds scatter and skew the beam, and specialised low frequency dual element probes are used.

---

## Penetrant

| Requirement | Detail |
|---|---|
| **Surface condition** | Clean, no smearing, no peening |
| **Not after peening** | It closes surface breaking defects |
| Etch before | Where machining may have smeared |
| Sensitivity level | 1 through 4. **Specify it** |

**Penetrant on a weld is for surface breaking cracks**, and it is very good at that and blind to everything else.

**The order matters**: penetrant before peening, always. Shot peening plastically closes surface openings and a peened crack does not take penetrant.

**Delayed inspection for cold cracking** applies to penetrant as much as to any other method: on hydrogen susceptible material, wait 24 to 48 hours.

---

## Proof testing

**A proof test demonstrates that the article survives a defined overload, and that is all it demonstrates.**

| What it shows | What it does not |
|---|---|
| The article did not fail at the proof load | **Any margin above it** |
| No gross defect large enough to fail at proof | **That a subcritical flaw is not growing** |
| The assembly is complete | The remaining life |

**Proof testing as NDE is a legitimate technique** and it has a specific fracture mechanics basis: surviving a proof load of `k` times limit demonstrates that no flaw larger than the critical size at the proof stress is present. That bounds the initial flaw size for a damage tolerance analysis.

**It is not a substitute for volumetric inspection** unless the analysis has been done, and the analysis requires knowing the material's fracture toughness and the flaw growth behaviour.

**A proof test can damage the article** by growing a subcritical flaw, which is why proof-as-NDE is applied with a subsequent inspection or with a demonstrated no-growth condition. See [aerospaceMaterials FractureAndDamageTolerance.md](../../docs/FractureAndDamageTolerance.md).

---

## Inspectability as a design requirement

**A joint that cannot be inspected has no verification for the life of the vehicle, and that is a design decision made at layout.**

| Requirement | Detail |
|---|---|
| **Access for the method** | Radiographic source and film, or transducer contact |
| **Geometry the method can handle** | A weld in a corner is not radiographable |
| **A surface the method can use** | Penetrant needs a suitable finish |
| Reference standards | Representative of the actual geometry |
| Coverage | Stated, and achievable |

**Full penetration joints are specified partly for inspectability.** A partial penetration weld has an unfused root by design, and no volumetric method can distinguish that from an unintended lack of penetration.

**Inspectability is decided at layout and it is very expensive to add later.** Moving a weld 20 mm at concept costs nothing; discovering at qualification that it cannot be inspected costs a redesign.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| RT and UT have complementary blind spots | Specify both for critical welds |
| Phased array does both, with a record | The current standard |
| TOFD sizes best | |
| Penetrant before peening | |
| Delay 24 to 48 hours on hydrogen susceptible material | |
| Proof shows survival, not margin | |
| Full penetration for inspectability | Not just strength |
| Decide inspectability at layout | |

---

## Failure modes

**Radiography alone.** Lack of fusion missed.

**Peened then penetrant inspected.** Surface cracks closed.

**Immediate inspection on high strength steel.** Delayed cracking appears later.

**Proof test taken as evidence of margin.** It is not.

**Weld placed where no method has access.** No verification, ever.

**Radiograph without an image quality indicator.** Unknown sensitivity.

**Penetrant sensitivity level unspecified.** Undefined acceptance.

---

## Standards

| Standard | Scope |
|---|---|
| **AWS D17.1** | Fusion welding for aerospace, acceptance criteria |
| ASME BPVC Section V | Nondestructive examination |
| **ASTM E1417** | Liquid penetrant testing |
| ASTM E1742 | Radiographic examination |
| ASTM E2698 | Digital detector array radiography |
| **ASTM E2700** | Phased array ultrasonic testing of welds |
| ASTM E2373 | Time of flight diffraction |
| **NASA-STD-5009** | Nondestructive evaluation requirements for fracture critical items |
| NASA-STD-5019 | Fracture control requirements |

---

## References

1. ASM Handbook Volume 17, *Nondestructive Evaluation and Quality Control*.
2. NASA-STD-5009B, *Nondestructive Evaluation Requirements for Fracture-Critical Metallic Components*.
3. AWS D17.1, *Specification for Fusion Welding for Aerospace Applications*.
