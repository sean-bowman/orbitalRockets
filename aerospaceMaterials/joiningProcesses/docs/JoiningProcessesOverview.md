[Home](../README.md) > Joining Processes Overview

# Joining Processes Overview

## Contents

- [Overview](#overview)
- [Why this sub-domain has no library](#why-this-sub-domain-has-no-library)
- [The processes](#the-processes)
- [The joint efficiency ladder](#the-joint-efficiency-ladder)
- [Choosing a process](#choosing-a-process)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [Document index](#document-index)
- [References](#references)

---

## Overview

Joints are where structures fail. Every joining process introduces a discontinuity in the material, the geometry or both, and the design question is which discontinuity is most tolerable for the load, the environment and the inspection access available.

---

## Why this sub-domain has no library

**Because [`Weld`](../../../fluidSystems/fluidSystemsLibrary/Weld.py) already exists** and it does joint efficiency, HAZ knockdown and WRC-1992 ferrite number prediction.

**Duplicating it is the worst available outcome.** Two implementations of the same knockdown table drift, and the drift is invisible until two analyses of the same joint disagree.

**The pieces `Weld` does not cover are structures problems**: braze lap length, adhesive shear-lag and bolted joint bearing all belong in `aerospaceStructures` alongside the rest of the joint analysis, not here.

**A cross-domain drift test asserts that the `as-welded` conditions in `MATERIAL_DATABASE` match `Weld.HAZ_KNOCKDOWN`**, so the two sources of the same number cannot diverge. It reads `Weld.py` by `ast.parse` rather than importing it, because both libraries have a `utils` module and importing shadows it.

---

## The processes

| Process | Efficiency | Dissimilar metals | Inspection | Use |
|---|---|---|---|---|
| **Fusion welding** | 0.5 to 1.0 | Limited | RT, PT, UT | The general answer |
| **Friction stir welding** | **0.8 to 0.95** | Some | PT, UT, phased array | **Tanks. High strength aluminium** |
| **Brazing** | Joint limited | **Excellent** | UT, proof | Heat exchangers, dissimilar |
| **Diffusion bonding** | ~1.0 | Some | **Difficult** | Titanium, SPF/DB |
| **Mechanical fastening** | 0.6 to 0.9 | **Excellent** | Visual, torque | Assembly, removability |
| **Adhesive** | Joint limited | **Excellent** | Tap test, UT | Composite, thin sheet |
| Explosive welding | ~1.0 | **Excellent** | UT | Transition joints |

---

## The joint efficiency ladder

| Joint | Efficiency |
|---|---|
| **Parent material** | **1.00** |
| Full penetration butt weld, austenitic stainless | 0.90 to 1.00 |
| Full penetration butt weld, 2219 | 0.70 |
| **Friction stir weld, 2219** | **0.80 to 0.90** |
| **Fusion weld, 6061-T6** | **0.50** |
| Fillet weld | 0.55 to 0.70 |
| Partial penetration | Proportional, and worse |
| Riveted lap joint | 0.60 to 0.80 |

**Heat treatable aluminium loses half its strength in a fusion weld** because the HAZ is overaged, and no filler choice recovers it. Post-weld solution treatment and ageing would, and it is impractical on most structures.

**Austenitic stainless barely loses anything** because it has no precipitates to overage. Its strength comes from the solid solution and from work hardening, and the weld loses only the work.

**That asymmetry drives a great deal of design.** A stainless weldment can be designed at nearly parent strength; an aluminium one cannot.

---

## Choosing a process

| Requirement | Process |
|---|---|
| **High strength aluminium, high efficiency** | **Friction stir welding** |
| Pressure boundary, inspectable | Fusion welding, full penetration |
| **Dissimilar metals** | Brazing, explosive welding, or mechanical |
| **Removability** | Mechanical fastening |
| Thin sheet, distributed load | Adhesive |
| Hollow titanium structure | **Diffusion bonding, with SPF** |
| **A cryogenic to ambient transition** | Explosive welded transition joint |

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Joints are where structures fail | Design the joint first |
| Fusion weld in 6061-T6 | 0.50 efficiency |
| Austenitic stainless welds near parent | No precipitates to lose |
| FSW for high strength aluminium | 0.80 to 0.95 |
| Full penetration for a pressure boundary | Partial penetration cannot be volumetrically inspected |
| Dissimilar metals want brazing or mechanical | Not fusion |
| Inspection access is a design requirement | Not a shop problem |

---

## Failure modes

**As-welded aluminium designed at parent strength.** Half the actual capability assumed.

**Partial penetration weld in a pressure boundary.** It cannot be inspected volumetrically.

**Dissimilar fusion weld.** Brittle intermetallics.

**Weld placed where it cannot be inspected.** No verification for the life of the vehicle.

**7075 fusion welded.** Hot cracking.

**Galvanic couple ignored at a fastened joint.** Corrosion at the faying surface.

---

## Standards

| Standard | Scope |
|---|---|
| **AWS D17.1** | Fusion welding for aerospace applications |
| AWS D17.3 | Friction stir welding for aerospace |
| **AMS 2680 / 2681** | Electron beam welding |
| AWS C3.6 | Furnace brazing |
| **NASA-STD-5006** | General welding requirements for aerospace |
| ASME BPVC Section IX | Welding and brazing qualification |
| NASM 33540 | Fastener hole preparation |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../../fluidSystems/fluidSystemsLibrary')

from Weld import Weld

weld = Weld()
weld.setInputs({'material': '6061-T6', 'jointType': 'butt full penetration',
                'outerDiameter': 0.050, 'wallThickness': 0.003})
result = weld.calculateDerating()
print(f'joint efficiency {result["jointEfficiency"]:.2f}, '
      f'HAZ yield factor {result["hazYieldFactor"]:.2f}, '
      f'total derating {result["totalDerating"]:.2f}')
```

---

## Document index

| Document | Covers |
|---|---|
| [FusionWelding.md](FusionWelding.md) | GTAW, GMAW, EBW, LBW, and the HAZ |
| [FrictionStirWelding.md](FrictionStirWelding.md) | The tank process, and why it works |
| [Brazing.md](Brazing.md) | Filler selection, clearance, joint design |
| [DiffusionBonding.md](DiffusionBonding.md) | Solid state, SPF/DB, and the inspection problem |
| [MechanicalFastening.md](MechanicalFastening.md) | Rivets, bolts, hole quality, galvanic |
| [AdhesiveBonding.md](AdhesiveBonding.md) | Shear lag, surface preparation, environment |
| [DissimilarMetalJoints.md](DissimilarMetalJoints.md) | Intermetallics, transition joints, galvanic |
| [WeldDefects.md](WeldDefects.md) | Porosity, cracking, lack of fusion, distortion |
| [Inspection.md](Inspection.md) | RT, PT, UT, phased array, proof |
| [Qualification.md](Qualification.md) | Procedure and operator qualification |

---

## References

1. AWS D17.1, *Specification for Fusion Welding for Aerospace Applications*.
2. Kou, S., *Welding Metallurgy*, 2nd ed., Wiley, 2003.
3. Messler, R. W., *Joining of Materials and Structures*, Butterworth-Heinemann, 2004.
