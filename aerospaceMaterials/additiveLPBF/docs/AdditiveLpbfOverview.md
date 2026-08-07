[Home](../README.md) > LPBF Overview

# Laser Powder Bed Fusion Overview

## Contents

- [Overview](#overview)
- [What makes LPBF different](#what-makes-lpbf-different)
- [The process in one page](#the-process-in-one-page)
- [Where it wins](#where-it-wins)
- [Where it does not](#where-it-does-not)
- [The four things that decide whether a part works](#the-four-things-that-decide-whether-a-part-works)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [Document index](#document-index)
- [References](#references)

---

## Overview

Laser powder bed fusion spreads a thin layer of metal powder, melts a cross section into it with a laser, lowers the plate, and repeats. Thousands of times. The part emerges buried in loose powder, welded to a build plate, full of residual stress, and covered in a surface nobody would accept from any other process.

It is used anyway, because it makes geometry that cannot be made any other way, and because on an expensive alloy its buy-to-fly ratio of about 1.2 to 1 against 8 to 1 for machining from plate is the whole cost of the part.

---

## What makes LPBF different

**The build is the melt.** For a wrought part the material arrives qualified and the shop qualifies its processes. Here the material and the part are created in the same operation, so every variable that would be a mill's problem becomes the part's problem: chemistry, solidification rate, porosity, grain structure, residual stress.

The consequences run through everything else in this sub-domain.

| Consequence | Where it shows up |
|---|---|
| The material has no independent existence | [Qualification.md](Qualification.md): the part cannot be qualified by inspecting it |
| Solidification is extremely fast | [ProcessFundamentals.md](ProcessFundamentals.md): 1e5 to 1e7 K/s, giving a microstructure no casting produces |
| The layers are a direction | [Anisotropy.md](Anisotropy.md): Z properties differ from XY, and the drawing has to say which |
| Internal geometry is unreachable | [InternalPassages.md](InternalPassages.md): unevacuated powder cannot be seen, reached or removed |
| Every layer is a chance to go wrong | [Defects.md](Defects.md): a 40 mm part is a thousand opportunities |

---

## The process in one page

| Step | What happens | What can go wrong |
|---|---|---|
| **Recoat** | A blade or roller spreads 20 to 60 um of powder | Poor flow gives a thin layer; a coarse particle scores it |
| **Scan** | The laser melts the cross section, hatch by hatch | Too little energy is lack of fusion; too much is keyholing |
| **Lower** | The plate drops one layer thickness | Nothing, and it is the majority of the cycle time |
| **Repeat** | Thousands of times | Each layer inherits the last one's stress |
| **Cool** | The build cools in the chamber | Distortion as the constraint of the plate is fought |
| **Stress relieve** | On the plate, before cutting off | Skip it and the part bananas when cut free |
| **Remove** | Wire EDM or bandsaw off the plate | The part moves; this is the last chance to catch it |
| **Depowder** | Loose powder out, supports off | Powder left in a closed passage cannot be removed later |
| **HIP** | Optional, and required for anything fatigue critical | Above a solvus it dissolves the strengthening phase |
| **Heat treat** | Solution, age, or anneal | A part HIPed and not re-treated is in an unknown condition |
| **Machine** | Datums, sealing faces, threads | The as-built surface is not a sealing surface |
| **Inspect** | CT for internal, penetrant for surface | Radiography misses the defect this process produces |

**The list is long and that is the point.** A quoted LPBF lead time that covers only the build is quoting a fraction of the process.

---

## Where it wins

**Internal geometry.** Conformal cooling channels, integrated manifolds, lattice structures. A part that would be six machined pieces and five joints becomes one piece and no joints, and every joint removed is a leak path removed.

**Expensive alloys.** Buy-to-fly of 1.2 against 8 for machining from plate. On Ti-6Al-4V at 8.5 times the 316L cost index, or GRCop-42 at 22, the stock saving dominates everything else.

**Lead time.** Six weeks against 24 for a closed die forging, because there is no tooling.

**Low volume.** No tooling means no amortisation, so the hundredth part costs the same as the first. That is exactly backwards from every conventional process and it is why additive suits development hardware.

**Consolidation.** Fewer parts, fewer joints, fewer fasteners, less assembly labour, and a shorter bill of materials.

---

## Where it does not

**Anything large.** Build volumes are typically 250 to 400 mm. Beyond that the part has to be split and joined, which reintroduces the joint the process was meant to remove.

**Anything simple.** A plain cylinder is cheaper to turn. Additive earns its cost through complexity, and a part with no complexity is paying for capability it does not use.

**Anything high volume.** The per-part cost does not fall with quantity, so at some volume any conventional process wins.

**Anything that needs a fine finish everywhere.** As-built roughness is 20 um Ra on a vertical wall against 1.5 for drawn tube. External surfaces can be machined; internal ones can only be abrasive flow machined, and only if they are accessible.

**Anything where the internal geometry must be verified and cannot be.** This is the one that stops programmes rather than costing them money. See [InternalPassages.md](InternalPassages.md).

---

## The four things that decide whether a part works

**1. Is the process point inside the window?** Between lack of fusion and keyholing, and not near either edge. [TheProcessMap.md](TheProcessMap.md).

**2. Can the powder get out?** Every internal passage, around every bend. [InternalPassages.md](InternalPassages.md).

**3. Is the geometry buildable?** Minimum wall, overhang angle, self-supporting channels, and somewhere to put the supports. [DesignForLpbf.md](DesignForLpbf.md).

**4. Can the result be inspected to the level the consequence demands?** [Inspection.md](Inspection.md) and [Qualification.md](Qualification.md).

**A part that fails any of the four is not a marginal part.** It is a part that has to be redesigned, and finding out at the build is expensive.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Buy-to-fly | ~1.2 : 1 as-built, ~1.4 : 1 HIPed and machined |
| Build volume | 250 to 400 mm typical |
| Layer thickness | 20 to 60 um, 40 typical |
| Minimum wall | 0.4 mm |
| Self-supporting overhang | 45 degrees from horizontal |
| Self-supporting round channel | 8 mm, or any size as a teardrop |
| Powder evacuation aspect ratio | 20 : 1, and each bend counts against it |
| As-built roughness | 20 um Ra vertical, 40 downskin |
| Volumetric energy density | 40 to 90 J/mm^3 for the common alloys |
| Melt pool penetration | 1.5 to 2.5 layers |

---

## Failure modes

**Lack of fusion porosity.** Flat, layer-aligned, behaves like a crack. The worst defect the process produces and HIP does not fully recover it.

**Unevacuated powder in a closed passage.** Cannot be seen, reached or removed, and it migrates downstream.

**The part bananas when cut off the plate.** Residual stress released. Stress relieve on the plate.

**A recoater crash.** A curled overhang catches the blade and the build stops.

**Properties assumed isotropic.** Z direction is 5 to 25 percent below XY depending on condition.

**A vendor datasheet used as an allowable.** It is a typical value from one machine and one parameter set.

**HIP applied and no re-treatment.** The part is soft and outside every allowable.

**Design freedom used without design discipline.** The commonest failure of all: a part that could only be made additively and cannot be inspected, cleared of powder, or supported.

---

## Worked numbers

From [`LpbfProcess`](../additiveLpbfLibrary/LpbfProcess.py), a production Inconel 718 parameter set at 285 W and 0.96 m/s on a 40 um layer:

| Quantity | Value |
|---|---|
| Volumetric energy density | 67.5 J/mm^3 |
| Normalised enthalpy | 13.5, against a 6 to 30 window |
| Process regime | **stable** |
| Melt pool depth | 91 um, **2.28 layers** |
| Melt pool width | 158 um |
| Hatch overlap | 30 % |
| Vertical wall roughness | 20.0 um Ra, 13x drawn tube |
| Downskin roughness | 35.6 um Ra |

The same class on GRCop-42 at 300 W returns **lack of fusion**, and it still does at 500 W. Copper reflects the fibre laser wavelength, so its absorptivity is 0.15 against 0.42 for nickel, and that single number is why copper is hard. See [Alloys.md](Alloys.md).

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-6030** | Additive manufacturing requirements for spaceflight systems |
| **MSFC-STD-3716** | Standard for additively manufactured spaceflight hardware by LPBF |
| MSFC-SPEC-3717 | Specification for control and qualification of LPBF processes |
| ISO/ASTM 52900 | Additive manufacturing, general principles and terminology |
| ISO/ASTM 52904 | Process characteristics and performance, metal powder bed fusion |
| **ASTM F3055 / F3056** | Additive Inconel 718 and 625 |
| ASTM F3184 | Additive 316L |
| AMS 4999 | Additive Ti-6Al-4V |
| ASTM F3049 | Characterizing metal powders for additive manufacturing |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'additiveLpbfLibrary')

from LpbfProcess import LpbfProcess

process = LpbfProcess()
process.setInputs({'material': 'Inconel 718', 'laserPower': 285.0, 'scanSpeed': 0.960,
                   'hatchSpacing': 110.0e-6, 'layerThickness': 40.0e-6})

process.calculateEnergyDensity()
process.calculateMeltPool()        # and the layer overlap criterion
process.classifyRegime()           # lack of fusion, stable or keyhole
print(process.generateReport())
```

---

## Document index

| Document | Covers |
|---|---|
| [ProcessFundamentals.md](ProcessFundamentals.md) | Melt pool, scan strategy, solidification rate |
| [TheProcessMap.md](TheProcessMap.md) | Energy density, normalised enthalpy, the window |
| [MachinesAndParameters.md](MachinesAndParameters.md) | OEMs, build volume, laser count, parameter development |
| [Alloys.md](Alloys.md) | What each alloy needs, and why copper is hard |
| [PowderAndFeedstock.md](PowderAndFeedstock.md) | PSD, morphology, chemistry, reuse, safety |
| [Defects.md](Defects.md) | Porosity, cracking, and how each is detected |
| [ResidualStressAndSupports.md](ResidualStressAndSupports.md) | Distortion, support strategy, stress relief |
| [Anisotropy.md](Anisotropy.md) | Build direction effects on every property |
| [PostProcessing.md](PostProcessing.md) | Stress relief, HIP, heat treat, machining datums |
| [SurfaceCondition.md](SurfaceCondition.md) | As-built roughness and what improves it |
| [DesignForLpbf.md](DesignForLpbf.md) | Minimum feature, overhangs, self-supporting geometry |
| [InternalPassages.md](InternalPassages.md) | Powder evacuation and the limits of verification |
| [Inspection.md](Inspection.md) | CT, in-situ monitoring, witness coupons |
| [Qualification.md](Qualification.md) | NASA-STD-6030, classification, equivalency |

---

## References

1. NASA-STD-6030, *Additive Manufacturing Requirements for Spaceflight Systems*.
2. MSFC-STD-3716, *Standard for Additively Manufactured Spaceflight Hardware by Laser Powder Bed Fusion*.
3. Gradl, P. R. et al., "Metal Additive Manufacturing in Aerospace: A Review", *Materials and Design*, Vol. 209, 2021.
4. DebRoy, T. et al., "Additive Manufacturing of Metallic Components: Process, Structure and Properties", *Progress in Materials Science*, Vol. 92, 2018.
5. Gibson, I., Rosen, D. and Stucker, B., *Additive Manufacturing Technologies*, 3rd ed., Springer, 2021.
