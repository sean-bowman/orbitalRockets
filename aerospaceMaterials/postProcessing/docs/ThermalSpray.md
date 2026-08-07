[Home](../README.md) > Thermal Spray

# Thermal Spray

## Contents

- [Overview](#overview)
- [The processes](#the-processes)
- [Bond strength and porosity](#bond-strength-and-porosity)
- [Residual stress](#residual-stress)
- [Cold spray](#cold-spray)
- [Surface preparation](#surface-preparation)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Thermal spray accelerates molten or softened particles at a surface, where they flatten and build a coating layer by layer. It is a mechanical bond rather than a metallurgical one, and understanding that explains most of its behaviour.

---

## The processes

| Process | Particle state | Velocity | Bond | Porosity |
|---|---|---|---|---|
| **HVOF** | Molten to semi-molten | 600 to 1000 m/s | 70 MPa | 1 % |
| **Plasma** | Fully molten | 200 to 400 m/s | 35 MPa | 5 % |
| **Cold spray** | **Solid** | 500 to 1200 m/s | 50 MPa | 0.5 % |
| Wire arc | Molten | 100 to 200 m/s | 20 MPa | 8 % |
| Flame | Molten | 50 to 100 m/s | 15 MPa | 12 % |

**HVOF is the aerospace default.** High velocity and moderate temperature give a dense, well bonded, low oxide coating. The velocity does the work rather than the heat, which is why it beats plasma for metallic coatings.

**Plasma reaches higher temperatures** and it is what sprays ceramics that HVOF cannot melt: thermal barrier coatings, oxides, zirconia.

---

## Bond strength and porosity

**The bond is mechanical interlocking**, not metallurgical fusion. Particles flatten into the surface roughness and key into it.

**That is why surface preparation dominates the result.** A smooth surface has nothing to key into and the coating falls off.

| Consequence of a mechanical bond | Detail |
|---|---|
| **Bond strength is modest** | 20 to 70 MPa, against parent metal strength |
| **It is a shear-critical joint** | Coatings fail by debonding, not by breaking |
| **Preparation is everything** | Grit blast to a specified roughness immediately before |
| Thickness is limited | Residual stress accumulates with thickness |

**Porosity is inherent to the process** except in cold spray. Splats do not fill perfectly and there are voids between them. For a wear coating that is often acceptable and sometimes useful, because the pores retain lubricant. For a corrosion barrier it is a through-path and a sealer is required.

---

## Residual stress

**The coating is deposited hot and cools bonded to a substrate that contracts differently.**

```
sigma = E * dAlpha * dT / (1 - nu)
```

| Case | Result |
|---|---|
| **Coating contracts more than the substrate** | Coating in **tension**. It cracks |
| **Coating contracts less** | Coating in **compression**. Benign |

**A coating in tension cracks, and the cracks let corrosive media through to the interface where they undercut the bond.** That is the classic thermal spray failure and it is entirely predictable from the CTE mismatch.

**Check the sign of the mismatch before selecting a coating**, and where it is unfavourable use a graded bond coat that steps the expansion between substrate and topcoat.

**Thickness is limited by the accumulated stress.** Beyond a few hundred micrometres for most systems the coating debonds under its own residual stress, which is why thick deposits need cold spray.

---

## Cold spray

**The exception in every respect, and it is worth understanding separately.**

Particles are accelerated in a supersonic gas jet and they arrive **solid**. Bonding is by plastic deformation on impact: above a critical velocity the particle and the substrate deform enough to break their oxide films and cold weld.

| Property | Consequence |
|---|---|
| **No melting** | No oxidation, no phase change, no heat affected zone |
| **No thermal excursion** | **No CTE mismatch stress at all** |
| **Compressive residual stress** | From the particle impact, like peening |
| **Thick deposits** | Millimetres rather than hundreds of micrometres |
| Requires ductile particles | Ceramics do not cold spray |

**The absence of thermal stress is why cold spray does dimensional restoration.** A worn shaft can be built back up by millimetres, which no thermal process manages.

**The critical velocity is material specific** and it is the governing process parameter. Below it, particles bounce off and erode the surface rather than coating it.

---

## Surface preparation

**The single largest determinant of whether a thermal spray coating works.**

| Step | Requirement |
|---|---|
| **Degrease** | Any oil prevents bonding |
| **Grit blast** | To a specified roughness, typically 3 to 6 um Ra |
| **Spray immediately** | Within hours. The freshly blasted surface oxidises |
| Mask | Overspray goes everywhere |

**The time between blasting and spraying is a controlled parameter.** A blasted surface left overnight has re-oxidised and the bond strength falls measurably.

**Grit blasting embeds grit in the surface**, and that grit is under the coating for the life of the part. Alumina grit is standard; using an inappropriate grit on a fatigue critical part introduces inclusions at the surface.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| HVOF for metals | Dense, well bonded, the default |
| Plasma for ceramics | Higher temperature |
| Cold spray for thick deposits | And for no thermal stress |
| Bond strength | 20 to 70 MPa. It is a shear-critical joint |
| Check the CTE mismatch sign | Tension cracks, compression does not |
| Grit blast to 3 to 6 um Ra | And spray within hours |
| Seal a corrosion coating | Porosity is a through-path |
| Thickness limit | Set by accumulated residual stress |

---

## Failure modes

**Coating in tension.** It cracks, and the cracks undercut the bond.

**Poor surface preparation.** It debonds, often in service rather than at inspection.

**Blasted surface left before spraying.** Re-oxidised, and the bond is weak.

**Unsealed porous coating used as a corrosion barrier.** The pores are a through-path.

**Coating too thick.** It debonds under its own residual stress.

**Cold spray below the critical velocity.** It erodes rather than coats.

---

## Standards

| Standard | Scope |
|---|---|
| **AMS 2447** | Thermal spray coatings, general |
| AMS 2435 | Tungsten carbide coating, HVOF |
| **ASTM C633** | Adhesion or cohesive strength of thermal spray coatings |
| ASTM E2109 | Determining area percentage porosity in thermal sprayed coatings |
| ASTM B851 | Automated controlled shot peening prior to coating |
| ISO 14923 | Thermal spraying, characterisation and testing |

---

## Tool interface

```python
from SurfaceTreatment import SurfaceTreatment, THERMAL_SPRAY

treatment = SurfaceTreatment()
treatment.setInputs({'material': '316L', 'condition': 'annealed', 'alloyFamily': 'stainless'})

hot  = treatment.calculateThermalSprayStress('HVOF', coatingExpansion = 18.0e-6)
cold = treatment.calculateThermalSprayStress('cold spray')

print(hot['residualStress'] / 1e6, hot['mechanism'])     # tension, CTE mismatch
print(cold['residualStress'] / 1e6, cold['mechanism'])   # compression, particle impact
```

---

## References

1. Davis, J. R. (ed.), *Handbook of Thermal Spray Technology*, ASM, 2004.
2. Assadi, H. et al., "Cold Spraying: A Materials Perspective", *Acta Materialia*, Vol. 116, 2016.
3. Pawlowski, L., *The Science and Engineering of Thermal Spray Coatings*, 2nd ed., Wiley, 2008.
