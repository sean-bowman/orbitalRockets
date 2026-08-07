[Home](../README.md) > Verification and Inspection

# Verification and Inspection

## Contents

- [Overview](#overview)
- [The problem](#the-problem)
- [Flow test](#flow-test)
- [Borescope](#borescope)
- [Replication](#replication)
- [Computed tomography](#computed-tomography)
- [Coupons and witness passages](#coupons-and-witness-passages)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Verifying an internal surface is harder than producing it. The surface that has just been improved is the one surface that cannot be measured by a profilometer, seen directly, or reached by a gauge.

Every available method is indirect, and each proves something different from what it is usually assumed to prove.

---

## The problem

**A surface roughness specification on an internal passage is not directly measurable** on the finished part. A stylus profilometer needs access; an optical instrument needs line of sight; neither exists inside a 5 mm bore 180 mm long.

**What is available:**

| Method | What it actually proves |
|---|---|
| Flow test | That the passage flows, at some pressure drop |
| Borescope | What the borescope can reach and resolve |
| Replication | The surface of a replica, at one accessible location |
| CT | Geometry and gross surface, at the scan resolution |
| Coupons | What a separate part did |

**None of them measures the roughness of the surface in question.** They measure a proxy, and knowing which proxy is which is the whole discipline.

---

## Flow test

**The practical production method.** Flow a known fluid at a known pressure drop and compare against a qualified reference.

| Strength | Weakness |
|---|---|
| Directly measures what matters for a flow passage | Cannot distinguish roughness from geometry |
| Fast and cheap | Needs a qualified reference article |
| Catches blockage and gross under-honing | Insensitive to a local defect |

**It cannot separate roughness from bore size.** A passage that is rough and slightly oversize flows the same as one that is smooth and slightly undersize. On a part where the bore is also growing during honing, those two effects move in opposite directions and can cancel.

**Flow testing before and after honing is far more informative than after alone**, because the change is attributable to the process.

---

## Borescope

**Visual, and limited by access and resolution.**

| Use | Limit |
|---|---|
| Confirming the media reached a location | Only where the scope reaches |
| Finding gross defects, blockage, media residue | Not quantitative |
| Confirming the sintered layer is gone | Subjective, and it needs experience |

**A borescope is a qualitative tool** and it is frequently over-credited. "Inspected by borescope" in an inspection record usually means somebody looked at the first 50 mm of a 180 mm passage.

**It is genuinely useful for confirming media residue is gone**, which is a real risk and an easy thing to see.

---

## Replication

**The only method that produces a measurable surface.**

A silicone or polymer replicating compound is pressed against the surface, cured, removed, and the replica is measured on a conventional profilometer.

| Strength | Weakness |
|---|---|
| Produces a real Ra measurement | Only where the compound can be placed and removed |
| Non-destructive | Not usable deep in a small passage |
| Traceable to a standard method | Fidelity falls at fine scales |

**Replication works at an accessible location and not in the middle of a long passage**, which is precisely where the honing is least effective. It is a useful check at the entry and a poor proxy for the middle.

---

## Computed tomography

**Measures geometry well and surface poorly**, and the reason is resolution.

A CT scan resolves roughly 1/1000 of its field of view. A 100 mm part gives 100 um voxels, and a 5 um surface roughness is invisible at that scale.

| CT is good for | CT is not good for |
|---|---|
| Bore size and shape along the passage | Ra |
| Residual powder or media | Fine surface texture |
| Confirming the passage is open | Confirming it is smooth |
| Wall thickness after honing | |

**CT and flow testing are complementary.** CT gives the geometry, flow gives the effective roughness, and together they separate the two effects that a flow test alone confounds.

---

## Coupons and witness passages

**The most defensible approach, and the one that requires planning.**

A witness passage is a sacrificial feature built or made alongside the part, honed in the same fixture in the same cycle, and then sectioned and measured directly.

| Requirement | Reason |
|---|---|
| Same fixture and cycle | Or it is not a witness |
| Representative geometry | A 10 mm straight bore does not witness a 4 mm bend |
| Sectioned and measured | The whole point is direct measurement |
| Retained | Part of the data package |

**A witness passage that is not representative is worse than none**, because it produces a number that will be believed.

**For an additive part the witness can be printed as part of the build**, which makes it genuinely representative of the surface it is witnessing.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| No method measures internal Ra directly | All are proxies |
| Flow test before and after | The change is attributable |
| Flow confounds roughness with bore size | CT separates them |
| Borescope is qualitative | And it is over-credited |
| Replication needs access | Good at the entry, poor in the middle |
| CT resolves ~1/1000 of the field of view | Geometry yes, roughness no |
| Witness passages must be representative | Or they mislead |

---

## Failure modes

**"Inspected by borescope" on a passage the scope cannot traverse.** Verified nothing.

**Flow test alone on a part where the bore grew.** Roughness and size cancelled.

**CT credited with a roughness measurement.** Below its resolution.

**A witness coupon of different geometry.** A believable wrong number.

**Media residue not checked.** It is a contaminant.

**No before measurement.** The change cannot be attributed to the process.

---

## Standards

| Standard | Scope |
|---|---|
| **ISO 4287 / 21920** | Surface texture, profile method |
| ASME B46.1 | Surface texture, including replication practice |
| ISO 25178 | Areal surface texture |
| ASTM E1351 | Production and evaluation of field metallographic replicas |
| **ASTM F3335** | Assessing removal of additive manufacturing residues |
| ASTM E1441 | Computed tomography imaging |

---

## References

1. ASME B46.1, *Surface Texture (Surface Roughness, Waviness, and Lay)*.
2. Townsend, A. et al., "Surface Texture Metrology for Metal Additive Manufacturing: A Review", *Precision Engineering*, Vol. 46, 2016.
3. du Plessis, A. et al., "Standard Method for microCT-based Additive Manufacturing Quality Control", *MethodsX*, Vol. 5, 2018.
