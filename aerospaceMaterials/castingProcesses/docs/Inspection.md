[Home](../README.md) > Inspection

# Inspection

## Contents

- [Overview](#overview)
- [Radiography](#radiography)
- [Penetrant](#penetrant)
- [Ultrasonic and CT](#ultrasonic-and-ct)
- [What each method misses](#what-each-method-misses)
- [Acceptance](#acceptance)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Casting inspection is dominated by radiography, and the reason is that casting defects are mostly volumetric. What radiography misses is planar, and what is planar in a casting is mostly bifilms, which nothing finds.

---

## Radiography

**The primary volumetric method** and the basis of casting acceptance.

| Detects well | Detects poorly |
|---|---|
| Gas porosity | **Bifilms** |
| Shrinkage | Tight cracks normal to the beam |
| Inclusions of differing density | Fine dispersed microporosity |
| Core shift, as a wall thickness change | |

**Sensitivity is roughly 2 percent of section thickness**, so a 20 mm section reveals defects down to about 0.4 mm. That is the number that decides whether radiography is adequate for a given critical flaw size.

**Reference radiographs are the acceptance basis**, per ASTM E446, E186, E280 for steel and E155 for aluminium. A casting is compared against a graded set of standard images and assigned a severity level per defect type, per area.

**Digital radiography has largely replaced film** and it gives better contrast sensitivity, immediate results and a permanent digital record. The acceptance standards are the same.

---

## Penetrant

**Surface breaking defects only, and it needs a suitable surface.**

| Surface | Suitability |
|---|---|
| Investment cast, as cast | Usable |
| **Sand cast, as cast** | **Poor. It indicates everywhere** |
| Machined | Good |
| Shot peened | **Poor. Peening closes surface openings** |

**Peening before penetrant hides defects**, because the plastic flow closes surface-breaking cracks so the penetrant cannot enter. The order is penetrant first, then peen. See [postProcessing](../../postProcessing/).

**Etching before penetrant reopens closed indications** on a machined surface, and it is specified where the machining may have smeared the surface.

---

## Ultrasonic and CT

| Method | Use |
|---|---|
| **Ultrasonic** | Wall thickness, laminar defects, thick sections |
| **Computed tomography** | Full 3D porosity map, complex geometry |

**Ultrasonic is limited by coarse grain structure**, which is common in castings and especially in heavy sections. The beam scatters and the noise floor rises.

**CT is the best method available for a complex casting** and it is expensive and slow. It gives a full volumetric map with no geometry limitation, which is exactly what a complex investment casting needs and exactly what radiography struggles with.

**CT is standard for additive parts and it is becoming standard for critical castings**, and it is worth costing for a low-volume flight-critical part where the geometry defeats radiography.

---

## What each method misses

**Stating this explicitly is more useful than listing what each finds.**

| Method | Misses |
|---|---|
| **Radiography** | Bifilms, tight planar cracks, microporosity below 2 % of section |
| **Penetrant** | Everything subsurface. Anything closed by peening or smearing |
| **Ultrasonic** | Defects hidden by grain noise. Small defects in thick sections |
| **CT** | Very little, and it costs |
| **Visual** | Everything except the surface |

**Bifilms are missed by everything**, which is why the fix is process control rather than inspection, and why unpressurised gating matters more than the inspection specification.

---

## Acceptance

| Element | Detail |
|---|---|
| **Classification** | Per AMS 2175: class 1 through 4, by criticality |
| **Zones** | Different acceptance in different regions of the same casting |
| **Severity level** | Per defect type, against the reference radiographs |
| Coverage | 100 % for factor 1.0, sampled below |

**Zoning is the practical tool.** A casting rarely needs its whole volume to the same standard, and specifying class 1 everywhere is expensive and usually wrong. Define the critical zones from the stress analysis and specify accordingly.

**The acceptance level has to be stated on the drawing**, and a drawing that says only "radiograph" has specified nothing.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Radiographic sensitivity | ~2 % of section thickness |
| Reference radiographs are the acceptance basis | ASTM E446, E155 |
| Penetrant before peening | Peening closes indications |
| Ultrasonic is limited by grain noise | Common in heavy sections |
| CT for complex critical castings | Expensive, and the best available |
| Bifilms are missed by everything | Process control, not inspection |
| Zone the acceptance | Class 1 everywhere is wrong |

---

## Failure modes

**Peened then penetrant inspected.** Surface cracks closed and missed.

**Radiography specified with no acceptance level.** No basis for accept or reject.

**Critical flaw size below the radiographic sensitivity.** The method cannot find what matters.

**Class 1 specified over the whole casting.** Expensive, and unnecessary.

**Clean radiography taken as a sound casting.** Bifilms do not show.

**Penetrant on an as-cast sand surface.** Indications everywhere.

---

## Standards

| Standard | Scope |
|---|---|
| **AMS 2175** | Castings, classification and inspection |
| **ASTM E446 / E186 / E280** | Reference radiographs for steel castings |
| ASTM E155 | Reference radiographs for aluminium and magnesium castings |
| ASTM E505 | Reference radiographs for die castings |
| ASTM E1417 | Liquid penetrant testing |
| ASTM E1742 | Radiographic examination |
| ASTM E2698 | Digital detector array radiography |
| ASTM E1441 | Computed tomography imaging |
| ASTM A802 | Steel castings, surface acceptance standards |

---

## References

1. ASM Handbook Volume 17, *Nondestructive Evaluation and Quality Control*.
2. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
3. AMS 2175, *Castings, Classification and Inspection of*.
