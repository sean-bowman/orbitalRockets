[Home](../README.md) > Composites and Laminates

# Composites and Laminates

## Contents

- [Overview](#overview)
- [Orthotropy, and why a single strength is meaningless](#orthotropy-and-why-a-single-strength-is-meaningless)
- [The materials](#the-materials)
- [Laminate basics](#laminate-basics)
- [COPV overwrap and stress rupture](#copv-overwrap-and-stress-rupture)
- [Damage tolerance](#damage-tolerance)
- [Environmental effects](#environmental-effects)
- [The galvanic problem](#the-galvanic-problem)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Composites offer specific strengths several times any metal and they come with a completely different failure philosophy. A metal yields, redistributes and warns. A composite does not yield, does not redistribute, and fails in a mode that depends on the layup rather than on the material.

This document covers what a materials engineer needs to select and specify one. The laminate analysis itself, the stiffness matrices and the failure criteria, belong in [aerospaceStructures](../../aerospaceStructures/).

---

## Orthotropy, and why a single strength is meaningless

A unidirectional carbon-epoxy lamina in the fibre direction:

| Direction | Strength [MPa] | Modulus [GPa] |
|---|---|---|
| **Longitudinal tension** | 2720 | 161 |
| Longitudinal compression | 1690 | 161 |
| **Transverse tension** | **64** | 11.4 |
| In-plane shear | 128 | 5.2 |

**The transverse strength is 2.4 percent of the longitudinal.** That single fact is why laminates exist: a real part needs plies at several angles because a unidirectional laminate is useless in every direction but one.

**Compression is 62 percent of tension**, because the failure mode changes from fibre tensile fracture to fibre microbuckling in the resin. Any compression-loaded composite part is sized on that lower number, and it is far more sensitive to voids and to fibre waviness.

Quoting a single strength for a composite is meaningless without the layup, the direction, and the loading sense.

---

## The materials

| Material | Density | Longitudinal strength | Tg | Where it belongs |
|---|---|---|---|---|
| **IM7/8552 carbon-epoxy** | 1570 | 2720 MPa | 473 K | Structural panels, fairings, tubes |
| **T1000G carbon-epoxy** | 1600 | 3040 MPa | 400 K | COPV overwrap |
| S-glass epoxy | 1980 | 1700 MPa | 400 K | Radomes, insulators, low cost structure |

**The fibre carries the load and the matrix holds it in place.** Fibre choice sets strength and stiffness; matrix choice sets the temperature limit, the moisture sensitivity and the processing route.

**The glass transition temperature is the real service limit**, not the strength. Above `Tg` the matrix softens, the compression and shear allowables collapse, and the part loses stiffness even though the fibres are unaffected. A 473 K `Tg` epoxy is not a 473 K material; the usable limit is typically 30 to 50 K below it, and lower still when wet.

---

## Laminate basics

**Layup notation:** `[0/45/-45/90]s` means four plies at those angles, then mirrored, giving eight plies total. The `s` denotes symmetric.

**Three rules that prevent most laminate problems:**

**Symmetric about the mid-plane.** An unsymmetric laminate couples in-plane load to bending, so it warps when it cools from cure and warps again under load.

**Balanced**, meaning every `+theta` ply has a matching `-theta`. An unbalanced laminate couples extension to shear.

**At least 10 percent of plies in each of the four principal directions.** A laminate with no 90 degree plies has essentially no transverse strength, and it will find a transverse load eventually.

**Cure matters as much as layup.** Autoclave cure at pressure produces void contents below 1 percent; out-of-autoclave processes typically reach 1 to 2 percent. **Voids hit compression and interlaminar shear hardest**, which are already the weak directions.

---

## COPV overwrap and stress rupture

A composite overwrapped pressure vessel is sized by a mechanism that has no metallic equivalent.

**A composite under sustained load fails after a time that depends on the stress ratio.** Not fatigue, not creep rupture in the metallic sense: individual fibres break progressively, load redistributes to their neighbours, and the process accelerates. There is no threshold below which it stops, only stress ratios at which the predicted life exceeds the mission by enough margin.

| Stress ratio | Typical predicted life |
|---|---|
| 0.80 | hours |
| 0.70 | ~1000 hours |
| **0.50** | **Design limit per AIAA S-081** |

**The ultimate strength number is impressive and misleading.** A T1000G overwrap tests at 3040 MPa and is designed to roughly 0.5 of that, because the vessel has to hold pressure for years rather than seconds.

**This is why a COPV has a defined service life in years and in pressurised hours**, tracked per article, and why leaving one pressurised on the pad is a real consumption of life rather than a storage condition.

**Liner buckling is the second COPV failure mode.** On depressurisation the metallic liner, which was stretched plastically during autofrettage, goes into compression and can buckle away from the overwrap. It is controlled by limiting the depressurisation and by the liner thickness.

---

## Damage tolerance

**Barely visible impact damage is the governing case for most composite structure.** A tool dropped on a laminate produces delamination and matrix cracking that is almost invisible on the surface and can reduce compression strength by 40 to 60 percent.

| Concept | Meaning |
|---|---|
| **BVID** | Barely visible impact damage. The threshold of visual detectability |
| **CAI** | Compression after impact. The allowable that BVID drives |
| Delamination | Ply separation, the dominant damage mode |
| Disbond | Separation at a bonded joint |

**The design allowable for a compression-loaded composite panel is usually the compression after impact strength**, not the pristine strength, and the gap is large. Designing to pristine allowables and relying on inspection to find damage is not a viable strategy, because BVID is by definition at the edge of what inspection finds.

**Ultrasonic C-scan is the standard NDE**, and thermography is faster for large areas. Neither finds a tight delamination reliably, which is why the allowable is knocked down rather than the damage inspected out.

---

## Environmental effects

| Effect | Consequence |
|---|---|
| **Moisture absorption** | Plasticises the matrix. Lowers `Tg` by 20 to 30 K and cuts hot compression allowables by ~15 % |
| **Hot wet** | The governing condition for most matrix-dominated allowables |
| Thermal cycling | Micro-cracking in the matrix, particularly on cryogenic tankage |
| UV | Degrades exposed epoxy. Requires a paint or a surfacing film |
| Cryogenic | Micro-cracking, which becomes a permeation path on a linerless tank |

**Hot wet is the condition allowables are quoted at** for anything matrix-dominated, because it is realistic rather than pessimistic: a part absorbs moisture over its life and a hot day happens.

**Cryogenic micro-cracking is why linerless composite cryogenic tanks are hard.** Differential contraction between fibre and matrix cracks the matrix at low temperature, and enough cracks link up into a permeation path. It is a solved problem in some programmes and it is not a free choice.

---

## The galvanic problem

**Carbon fibre is strongly cathodic**, sitting near graphite in the galvanic series. A carbon laminate bolted directly to aluminium is a 0.9 V couple with an unfavourable area ratio, and it will destroy the aluminium.

**The standard fix is a glass ply on the interface**, plus a wet-installed sealant, plus fasteners chosen from a compatible group. Titanium and A286 fasteners are used with carbon for exactly this reason; aluminium fasteners are not.

The quantitative treatment is in [CorrosionAndSCC.md](CorrosionAndSCC.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| A single strength number is meaningless | Quote direction, sense and layup |
| Symmetric and balanced | Or the part warps out of the tool |
| At least 10 % of plies in each principal direction | It will find the transverse load |
| Service limit is 30 to 50 K below Tg | And lower wet |
| Compression is ~60 % of tension | And far more void sensitive |
| COPV design stress ratio | 0.50, per AIAA S-081 |
| Compression allowable is CAI, not pristine | BVID is the governing damage |
| Hot wet is the design condition | Not pessimism, realism |
| Never carbon directly against aluminium | Glass ply and sealant |

---

## Failure modes

**Sustained load stress rupture.** A COPV held at high stress ratio for years.

**Barely visible impact damage.** Invisible, and 40 to 60 percent of the compression strength.

**Delamination from an out-of-plane load.** Composites have almost no through-thickness strength.

**Matrix micro-cracking on cryogenic cycling.** Becomes a permeation path.

**Warping out of the cure tool.** Unsymmetric layup.

**Galvanic destruction of an adjacent aluminium part.** Carbon is strongly cathodic.

**A laminate sized on pristine allowables.** The first tool drop invalidates it.

**Voids from an out-of-autoclave cure used with autoclave allowables.** Compression and interlaminar shear are hit hardest.

---

## Standards

| Standard | Scope |
|---|---|
| **CMH-17** | Composite Materials Handbook, the allowables and methodology source |
| **AIAA S-081** | Composite overwrapped pressure vessels |
| ANSI/AIAA S-080 | Metallic pressure vessels, for the liner |
| NASA-STD-5019 | Fracture control, including composites |
| ASTM D3039 | Tensile properties of polymer matrix composites |
| ASTM D6641 | Compressive properties, combined loading |
| **ASTM D7136 / D7137** | Impact damage resistance and compression after impact |
| ASTM D2344 | Short beam strength, for interlaminar shear |
| ASTM D5229 | Moisture absorption and equilibrium conditioning |
| NCAMP NMS specifications | Qualified material specifications for shared databases |

---

## Tool interface

```python
from MaterialDatabase import queryMaterial

overwrap = queryMaterial('T1000G', 'filament wound', 293.15)

# The number that actually sizes a COPV, and it is not the ultimate strength
rupture = overwrap['stressRupture']
designStress = overwrap['ultimateStrength'] * rupture['designStressRatio']
print(designStress / 1.0e6)          # roughly half the tested ultimate

# Orthotropy, made explicit
print(overwrap['ultimateStrength'] / overwrap['transverseStrength'])   # about 60x
```

---

## References

1. CMH-17, *Composite Materials Handbook*, Volumes 1 to 3.
2. AIAA S-081B-2018, *Space Systems -- Composite Overwrapped Pressure Vessels*.
3. Daniel, I. M. and Ishai, O., *Engineering Mechanics of Composite Materials*, 2nd ed., Oxford, 2006.
4. Phoenix, S. L. et al., "Stress Rupture of Composite Overwrapped Pressure Vessels", NASA/TP-2009-215683.
5. Niu, M. C. Y., *Composite Airframe Structures*, Conmilit Press, 1992.
