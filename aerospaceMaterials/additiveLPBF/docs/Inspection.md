[Home](../README.md) > Inspection

# Inspection

## Contents

- [Overview](#overview)
- [Why radiography is not enough](#why-radiography-is-not-enough)
- [Computed tomography](#computed-tomography)
- [In-process monitoring](#in-process-monitoring)
- [Witness coupons](#witness-coupons)
- [Surface methods](#surface-methods)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

An additive part cannot be qualified by inspecting it, because the geometry additive exists to produce is the geometry no inspection reaches. Most of the evidence comes from process control and from coupons, and the inspection that does happen has to be chosen for the defect this process actually produces.

---

## Why radiography is not enough

**Radiography integrates through the thickness.** A flaw is detected by the difference in attenuation along the ray path, so a flaw with little extent along that path produces little contrast.

**The defect this process produces is a flat lack of fusion flaw lying in the build plane.** Radiographed from the side, it is presented edge-on and its through-path extent is its thickness, which is micrometres. It is close to invisible.

**It would be detectable radiographed from directly above or below**, and that is the one orientation an integrated part rarely permits.

| Method | Sees a flat build-plane flaw |
|---|---|
| Radiography, from the side | **Effectively no** |
| Radiography, normal to the flaw | Yes, if access permits |
| **Computed tomography** | **Yes, in any orientation** |
| Ultrasonic | Yes, with access and a good surface |

The credited flaw sizes in [NASA-STD-5009](../../docs/FractureAndDamageTolerance.md) reflect this: radiography is credited with 2.54 mm against 0.25 for CT.

---

## Computed tomography

**The only volumetric method that reaches an internal passage**, and the largest single cost driver in additive qualification.

| Parameter | Effect |
|---|---|
| **Resolution** | Roughly 1/1000 of the field of view. A 100 mm part gives ~100 um voxels |
| **Penetration** | Falls with density and thickness. Dense alloys limit the section |
| **Time** | Hours per part for a high resolution scan |
| **Data** | Gigabytes, and analysing it is a skill |

**The resolution and field of view trade is the constraint.** A part small enough for 25 um voxels is a small part, and scanning a large part at a resolution that finds a 100 um flaw is not possible in one scan. Regions of interest are scanned separately, which means knowing in advance where to look.

**CT belongs in the trade at design time**, not at inspection planning. A design decision that adds an uninspectable passage has added a cost that appears much later.

---

## In-process monitoring

Watching the build rather than inspecting the result.

| Method | What it sees |
|---|---|
| **Melt pool monitoring** | Photodiode or camera on the pool. Size, intensity, stability |
| **Layer imaging** | A photograph of each layer, before and after scanning |
| Thermal imaging | The pool and its surroundings |
| Acoustic | Experimental, and promising for keyhole detection |

**Layer imaging is the most useful and the least glamorous.** A photograph of every layer catches recoater streaks, short feed, part lifting and spatter accumulation, and every one of those is a build to stop rather than a part to reject afterwards.

**Melt pool monitoring produces enormous data and limited decision support.** It reliably detects that something anomalous happened; relating that to whether the part is acceptable is an open problem, and treating an anomaly count as an acceptance criterion is not yet defensible.

**What monitoring is genuinely good for is stopping a bad build early.** A recoater crash detected at layer 200 saves the 3000 layers that would have been built on top of it.

---

## Witness coupons

**The primary evidence for an additive part**, because the part itself usually cannot be tested.

Specimens built alongside the part, in the same build, from the same powder, tested to confirm the process was in control that day.

| Requirement | Reason |
|---|---|
| **Same build** | A different build is a different day and a different machine state |
| **Same powder lot** | Chemistry and flow both matter |
| **Distributed placement** | Build position affects properties through gas flow and thermal history |
| Both orientations | XY and Z, because they differ |
| Tested to the same specification | Or they prove something else |

**Placement is a specification item, not a convenience.** Coupons taken from one corner of the plate monitor that corner. See [Qualification.md](Qualification.md).

---

## Surface methods

| Method | Use |
|---|---|
| **Penetrant** | Surface-breaking flaws. Needs a machined surface; an as-built surface bleeds everywhere |
| Eddy current | Surface and near-surface, on a conductive machined surface |
| Visual | Balling, layer defects, discolouration |
| Surface roughness | Ra, as a process indicator as much as a requirement |

**Penetrant does not work on an as-built surface.** The roughness holds penetrant in every crevice and the whole surface indicates. The surface has to be machined or etched first, which limits penetrant to features that are machined anyway.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Radiography | Blind to the flat build-plane flaw |
| CT credited flaw | 0.25 mm, against 2.54 for radiography |
| CT resolution | ~1/1000 of the field of view |
| Layer imaging | The most useful monitoring, and it stops bad builds early |
| Melt pool monitoring | Not yet an acceptance criterion |
| Witness coupons | Same build, same powder, distributed placement |
| Penetrant | Needs a machined surface |
| Plan the inspection at design time | Not at inspection planning |

---

## Failure modes

**Radiography accepted as volumetric NDE.** Blind to the defect that matters.

**A part too large to CT at useful resolution.** Discovered after it is built.

**Penetrant attempted on an as-built surface.** Indicates everywhere.

**Coupons from one plate corner.** They monitor that corner.

**Monitoring data collected and never analysed.** Terabytes, no decisions.

**Inspection planned after the design froze.** The uninspectable feature is already in the part.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-5009** | NDE requirements for fracture critical components. The credited flaw sizes |
| ASTM E1441 | Computed tomography imaging |
| ASTM E1742 | Radiographic examination |
| ASTM E1417 | Liquid penetrant testing |
| **ASTM F3335** | Assessing NDT of AM parts with internal channels |
| ISO/ASTM 52905 | Non-destructive testing of additive parts |
| NASA-STD-6030 | Additive manufacturing requirements |

---

## Tool interface

```python
from LpbfQualification import LpbfQualification

qualification = LpbfQualification()
qualification.setInputs({'consequenceClass': 'AXM', 'processMaturity': 'qualified',
                         'hasInternalPassages': True})

plan = qualification.buildInspectionPlan()
print(plan['computedTomographyRequired'])    # True
for method in plan['methods']:
    print(' ', method)
```

---

## References

1. NASA-STD-5009B, *Nondestructive Evaluation Requirements for Fracture-Critical Metallic Components*.
2. du Plessis, A., Yadroitsev, I. et al., "X-Ray Microcomputed Tomography in Additive Manufacturing: A Review", *3D Printing and Additive Manufacturing*, Vol. 5, 2018.
3. Everton, S. K. et al., "Review of In-Situ Process Monitoring and In-Situ Metrology for Metal Additive Manufacturing", *Materials and Design*, Vol. 95, 2016.
