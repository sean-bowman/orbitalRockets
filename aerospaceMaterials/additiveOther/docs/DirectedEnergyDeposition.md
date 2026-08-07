[Home](../README.md) > Directed Energy Deposition

# Directed Energy Deposition

## Contents

- [Overview](#overview)
- [The process](#the-process)
- [What it achieves](#what-it-achieves)
- [Repair](#repair)
- [Functionally graded material](#functionally-graded-material)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Powder or wire is fed into a melt pool created by a laser, electron beam or arc, on a moving head. There is no powder bed, so there is no build chamber limit and no support structure, and there is also no fine detail.

---

## The process

| Element | Detail |
|---|---|
| **Energy source** | Laser, electron beam or plasma arc |
| **Feedstock** | Blown powder, or wire |
| **Motion** | 3 to 5 axis gantry, or a robot arm |
| **Atmosphere** | Inert shroud, glovebox, or vacuum for EB |
| Deposition rate | 50 to 500 cm^3/h for powder |

**The head can be mounted on a robot**, which is why the size limit is the robot's reach rather than a chamber. Multi-metre structures are routine.

**Blown powder capture efficiency is 40 to 90 percent**, so a substantial fraction of the powder does not enter the melt pool. That is a real cost on expensive alloys and it is one reason wire fed DED is preferred where the resolution allows.

**Five axis motion removes the need for supports** because the head can approach from any direction, depositing onto an inclined surface rather than building up to it. That is a genuine advantage over powder bed processes.

---

## What it achieves

| Property | Value |
|---|---|
| **Tolerance** | IT12. **Everything functional is machined** |
| Surface | 10 to 25 um Ra |
| **Size** | **Metres** |
| Minimum feature | 1 to 2 mm |
| **Properties** | Good, and **directional** |
| Buy-to-fly | 1.5 to 3 : 1 |

**Properties are good and columnar.** The melt pool solidifies directionally into the previously deposited material, producing columnar grains growing along the build direction, which gives a real anisotropy: typically better in the build direction for strength and worse for ductility and toughness.

**Heat treatment reduces the anisotropy** and does not eliminate it, because the columnar structure survives a stress relief and only a full recrystallisation removes it, which most alloys will not tolerate.

**Interlayer porosity is the characteristic defect**, from insufficient remelting of the previous layer. It is a planar lack of fusion between beads and it is the reason DED parts are HIPed for critical applications.

---

## Repair

**The application that distinguishes DED, because no powder bed process can do it.**

| Application | Detail |
|---|---|
| **Worn surfaces** | Restore dimension on a shaft, a seal land, a blade tip |
| **Damaged features** | Rebuild a broken boss or a gouged surface |
| Erosion and corrosion | Add a resistant clad layer |
| Design changes | Add material to an existing part |

**Turbine blade tip repair is the mature application** and it has been in production for decades.

**The substrate has a HAZ**, which is the limitation. Depositing onto a heat treated part locally re-solutionises or overages the substrate beneath the deposit, and the affected depth has to be within the machining allowance or accounted in the analysis.

**Repair qualification is harder than new-build qualification** because the substrate condition varies from part to part. A new part starts from known stock; a repaired part starts from something that has been in service, with an unknown history of thermal exposure and possibly fatigue damage.

**Cold spray avoids the HAZ entirely** and it is the alternative where the substrate cannot tolerate heat. See [ColdSpray.md](ColdSpray.md).

---

## Functionally graded material

**DED can change the feedstock composition during the build**, which nothing else in this family does easily.

| Application | Detail |
|---|---|
| **Copper to nickel transition** | A chamber liner integral with its structural jacket |
| Stainless to Inconel | A gradual transition avoiding a dissimilar weld |
| Hard facing | A wear resistant surface on a tough core |
| Thermal expansion grading | Reducing the mismatch stress across a joint |

**The GRCop to Inconel transition in a chamber is the flagship application** and it eliminates the brazed or bolted joint between liner and jacket, which is one of the harder joints in an engine.

**Grading avoids the intermetallic problem** of a sharp dissimilar interface by spreading the composition change over many layers, so no single layer has the composition that forms the brittle phase in quantity.

**It is difficult to qualify** because the material properties vary continuously through the transition and there is no handbook allowable for a composition that exists only in one part.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| No chamber limit | Robot reach |
| No supports needed with 5 axis | It deposits onto inclines |
| Tolerance IT12 | Machine every functional surface |
| Powder capture 40 to 90 % | A real cost |
| Columnar and anisotropic | Heat treatment reduces it |
| HIP for critical parts | Interlayer porosity |
| The substrate gets a HAZ in repair | Account for it |
| Grading avoids dissimilar intermetallics | And it is hard to qualify |

---

## Failure modes

**Interlayer lack of fusion.** Planar, and it needs HIP or better parameters.

**Anisotropy ignored.** Build direction properties differ substantially.

**Repair HAZ not accounted.** The substrate is locally in a different condition.

**Powder capture efficiency omitted from the cost.** Up to 60 % lost.

**As-deposited tolerance assumed usable.** IT12.

**Graded material used without allowables.** There are none.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM F3187** | Directed energy deposition of metals |
| **NASA-STD-6030** | Additive manufacturing requirements for spaceflight |
| ISO/ASTM 52900 | Additive manufacturing terminology |
| AWS D20.1 | Fabrication of metal components using additive manufacturing |
| ASTM F3049 | Characterising properties of metal powders |
| ASTM E1441 | Computed tomography imaging |

---

## References

1. Gibson, I., Rosen, D. and Stucker, B., *Additive Manufacturing Technologies*, 3rd ed., Springer, 2021.
2. Gradl, P. R. et al., "Metal Additive Manufacturing in Aerospace: A Review", *Materials and Design*, Vol. 209, 2021.
3. ASTM F3187, *Standard Guide for Directed Energy Deposition of Metals*.
