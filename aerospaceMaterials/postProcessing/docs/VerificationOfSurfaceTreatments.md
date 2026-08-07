[Home](../README.md) > Verification of Surface Treatments

# Verification of Surface Treatments

## Contents

- [Overview](#overview)
- [The general problem](#the-general-problem)
- [Peening](#peening)
- [Removal processes](#removal-processes)
- [Coatings](#coatings)
- [Hydrogen relief](#hydrogen-relief)
- [Residual stress measurement](#residual-stress-measurement)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Almost every process in this sub-domain produces a result that cannot be measured directly on the finished part. Verification is therefore mostly process verification with coupons, and knowing which is which prevents a false sense of assurance.

---

## The general problem

| Process | Directly measurable on the part? |
|---|---|
| Shot peening | **No.** Coverage visually, intensity on a strip |
| Laser shock peening | **No.** Same |
| Chemical milling | Yes, thickness ultrasonically |
| Electropolishing | Partly. Ra where accessible |
| Anodising | Yes, thickness by eddy current |
| Plating | Yes, thickness |
| Hydrogen relief | **No.** Not on the part at all |
| Thermal spray | Thickness yes, bond strength no |

**The processes that change the surface stress state are the ones that cannot be verified directly**, and they are also the ones where the benefit is most often assumed rather than demonstrated.

---

## Peening

| Element | Method |
|---|---|
| **Intensity** | Almen strip, at saturation. Per SAE J443 |
| **Coverage** | Visual at 10x, or a fluorescent tracer |
| Media condition | Screening, and a broken-particle count |
| Compressive layer | X-ray diffraction on a coupon, destructively |

**The Almen strip verifies the machine setup, not the part.** It says the process was delivering a given intensity, which is the strongest available statement short of sectioning the part.

**Coverage is verified on the part** and it is the one element that can be. Visual inspection at magnification, or a tracer coating that the impacts remove.

**Nothing verifies that a specific part has the intended compressive layer**, and that is why the process controls are as tight as they are.

---

## Removal processes

| Element | Method |
|---|---|
| **Thickness after chem mill** | Ultrasonic. The standard |
| Dimensional | CMM or micrometer, where accessible |
| **Ra after electropolish** | Profilometer, where accessible |
| Etch rate | Coupons in the bath, weighed |
| Alpha case removal | Metallographic section or microhardness on a coupon |

**Ultrasonic thickness measurement is the workhorse** for chemical milling and it measures the actual wall rather than inferring it from the etch time.

**Alpha case removal cannot be verified visually** and it needs a section or a hardness traverse on a witness coupon processed alongside. See [AlphaCaseRemoval.md](AlphaCaseRemoval.md).

---

## Coatings

| Element | Method |
|---|---|
| **Thickness** | Eddy current, magnetic, or a section |
| **Adhesion** | Bend test, tape test, or ASTM C633 pull test on a coupon |
| Porosity | Metallographic section, or a ferroxyl test through the coating |
| Coverage | Visual, and a dye check for holidays |
| Hardness | Microindentation on a section |

**Adhesion is tested on coupons**, not on parts, because every adhesion test is destructive. The coupon is prepared and coated alongside the parts in the same run.

**Holiday detection matters for a corrosion coating.** A pinhole in a coating over a less noble substrate concentrates the whole galvanic current on that point. See [aerospaceMaterials CorrosionAndSCC](../../docs/CorrosionAndSCC.md).

---

## Hydrogen relief

**The bake cannot be verified on the part at all.** There is no non-destructive test for hydrogen content.

**What is verified is the process**, per ASTM F519: notched specimens plated alongside production parts, held at 75 percent of notched fracture strength for 200 hours, and they must not fail.

| Element | Detail |
|---|---|
| F519 specimens | Per plating lot or per shift |
| **Furnace records** | Temperature, time, and the start time relative to plating |
| Traceability | Which parts were in which bake |

**The start time record is the one that matters** and it is the one most often absent. Without it, there is no evidence the four hour window was met.

---

## Residual stress measurement

Where a direct measurement is genuinely needed.

| Method | Depth | Destructive |
|---|---|---|
| **X-ray diffraction** | Surface, ~10 um | No, but layer removal is needed for a profile |
| **Hole drilling** | To ~1 mm | Yes, locally |
| Neutron diffraction | Bulk, through thickness | No, and it needs a reactor |
| Curvature | Thin sections only | No |

**X-ray diffraction with successive layer removal is the standard method** for a peening residual stress profile, and it is a coupon method because the layer removal destroys the part.

**Hole drilling is the practical field method** and it leaves a small hole that can sometimes be tolerated on a non-critical area.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Peening intensity | Almen strip at saturation |
| Peening coverage | Visual at 10x, on the part |
| Compressive layer | XRD on a coupon, destructively |
| Chem mill thickness | Ultrasonic, on the part |
| Alpha case removal | Section or hardness, on a coupon |
| Coating adhesion | Coupon, always destructive |
| Hydrogen relief | ASTM F519 coupons plus furnace records |
| Record the bake start time | The window is the requirement |

---

## Failure modes

**Peening assumed effective with no coverage check.** The one thing that could be verified was not.

**Almen strip taken as verifying the part.** It verifies the machine.

**Coating adhesion assumed from appearance.** It debonds in service.

**Alpha case removal verified visually.** It is invisible.

**No bake start time record.** No evidence the window was met.

**Chem mill depth inferred from time.** The bath drifted.

---

## Standards

| Standard | Scope |
|---|---|
| **SAE J443** | Procedures for using standard shot peening test strip |
| SAE J442 | Test strip, holder and gage |
| **ASTM E837** | Residual stress by hole drilling |
| ASTM E2860 | Residual stress in bearing steels by X-ray diffraction |
| **ASTM C633** | Adhesion or cohesive strength of thermal spray coatings |
| ASTM B571 | Adhesion of metallic coatings |
| ASTM E797 | Ultrasonic thickness measurement |
| **ASTM F519** | Mechanical hydrogen embrittlement evaluation |
| ASTM B499 | Coating thickness by magnetic method |

---

## References

1. SAE J443, *Procedures for Using Standard Shot Peening Test Strip*.
2. ASTM E837-20, *Standard Test Method for Determining Residual Stresses by the Hole-Drilling Strain-Gage Method*.
3. Prevey, P. S., "X-Ray Diffraction Residual Stress Techniques", *ASM Handbook Volume 10*, 1986.
