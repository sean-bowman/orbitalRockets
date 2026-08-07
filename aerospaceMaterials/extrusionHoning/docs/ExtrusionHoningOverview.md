[Home](../README.md) > Extrusion Honing Overview

# Extrusion Honing Overview

## Contents

- [Overview](#overview)
- [How it works](#how-it-works)
- [What it is for](#what-it-is-for)
- [What it cannot do](#what-it-cannot-do)
- [The self-correcting property, and its opposite](#the-self-correcting-property-and-its-opposite)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [Document index](#document-index)
- [References](#references)

---

## Overview

Abrasive flow machining, also called extrusion honing, forces a viscoelastic abrasive-laden putty back and forth through a workpiece. The media acts as a self-conforming tool: it flows where the passage flows, so it reaches internal geometry no rigid tool can, and it removes material in proportion to the local wall shear stress.

It is the practical answer to the as-built surface of an additively manufactured internal passage, and to deburring a cross-drilled intersection that nothing else can reach.

---

## How it works

Two opposed cylinders clamp the workpiece between them. Media is extruded from one into the other through the passage, then back. One pass in each direction is a cycle.

| Element | Role |
|---|---|
| **Media** | A polymer carrier loaded with abrasive. Shear thinning, so it is stiff in the cylinder and flows in the passage |
| **Fixture** | Holds the part, seals the ends, and directs the media where it is wanted |
| **Restrictors** | Deliberately throttle the easy paths so parallel branches receive matched flow |
| **Pressure** | 3 to 20 MPa typically. Sets the wall shear |
| **Cycles** | 5 to 50. Sets the total removal |

**The removal mechanism is abrasion under shear**, not impact and not cutting. The abrasive particles are pressed against the wall by the flowing carrier and dragged along it.

---

## What it is for

| Application | Why nothing else works |
|---|---|
| **Additive internal passages** | No tool reaches them |
| **Cross-drilled intersections** | The burr is inside, at the intersection |
| **Fuel injector and nozzle passages** | Small, deep, and flow critical |
| **Extrusion and forming dies** | Complex internal profiles, and it polishes them evenly |
| Turbine blade cooling passages | Cast in, and internal |
| Deburring generally | Where the burr is inaccessible |

**The additive application is the growth area** and it is why this sub-domain sits inside aerospaceMaterials rather than beside it. A 20 um as-built passage is not a usable flow passage, and abrasive flow is the only route to improving it.

---

## What it cannot do

| Limit | Reason |
|---|---|
| **Dead-ended passages** | The media has nowhere to go |
| **Below 0.3 mm** | The media cannot be extruded at any practical pressure |
| **Beyond the grit-limited floor** | The abrasive cannot make a finish finer than its own scratch |
| **Correct geometry** | It follows the passage, it does not straighten it |
| **Remove much material** | Tens of micrometres, not millimetres |

**The dead-end limit is a design constraint, not a process one.** A passage that cannot be honed has to be designed differently at concept, and this is the point that most often reaches back into the additive design. See [AdditiveApplications.md](AdditiveApplications.md).

---

## The self-correcting property, and its opposite

**Within a single passage the process is self-correcting.** A restriction sees a higher local velocity, therefore a higher wall shear, therefore more removal. It opens faster than the passage around it and the bore evens out.

**Across parallel branches it is exactly the opposite.** The branch that flows best gets the most media, the most shear and the most removal, so it opens further and takes an even larger share on the next cycle. The differences amplify.

For a power law fluid the conductance goes as `D^(3 + 1/n)`, and with `n` near 0.28 that exponent is above six. **A ten percent diameter difference between two branches produces a seventy percent flow difference**, and it grows every cycle.

**This is why fixturing and restrictors exist**, and it is the whole engineering content of applying the process to a manifold. See [FixturingAndFlowControl.md](FixturingAndFlowControl.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Passage range | 0.3 to 100 mm depending on media grade |
| Pressure | 3 to 20 MPa |
| Cycles | 5 to 50 |
| Typical removal | 10 to 100 um radial |
| Ra improvement | ~4x, to a grit-limited floor |
| Both ends must be accessible | No dead ends |
| Balance parallel branches | Or the differences amplify |
| Passage grows | Put it in the tolerance stack |

---

## Failure modes

**Dead-ended passage.** Cannot be honed at all.

**Unbalanced parallel branches.** One is over-honed and the others are untouched.

**Passage growth not in the tolerance stack.** An orifice sized before honing is not the size it was.

**Running past the finish floor.** Stock removed, no finish improvement.

**Sharp orifice entry rounded.** The discharge coefficient changed.

**Media left in the part.** It is a contaminant and it has to be cleaned out.

---

## Worked numbers

From [`ExtrusionHoning`](../extrusionHoningLibrary/ExtrusionHoning.py), a 4.76 mm by 180 mm additive Inconel 718 passage at 7 MPa for 20 cycles:

| Quantity | Value |
|---|---|
| Media selected | medium, 200 um grit |
| Wall shear stress | 46.3 kPa |
| Apparent shear rate | 44.4 1/s |
| Radial removal | 51.8 um |
| Diametral growth | 104 um, **2.18 %** |
| Ra | **20.0 to 5.06 um**, a 4.0x improvement |
| Grit-limited floor | 5.00 um |
| Cycles to reach the floor | 12 |

**Twenty cycles is past the twelve needed**, so the last eight removed stock without improving the finish.

---

## Standards

| Standard | Scope |
|---|---|
| ISO 4287 / 21920 | Surface texture, profile method |
| ASME B46.1 | Surface texture |
| **ASTM F3335** | Assessing removal of additive manufacturing residues |
| SAE ARP4438 | Abrasive flow machining, where a vendor practice is cited |
| ISO 8785 | Surface imperfections |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'extrusionHoningLibrary')

from ExtrusionHoning import ExtrusionHoning

honing = ExtrusionHoning()
honing.setInputs({'passageDiameter': 0.00476, 'passageLength': 0.180,
                  'material': 'Inconel 718', 'condition': 'lpbf hip + sta',
                  'extrusionPressure': 7.0e6, 'cycleCount': 20})

honing.calculateWallShear()
honing.calculateRemoval()
honing.calculateSurfaceFinish()
print(honing.generateReport())
```

---

## Document index

| Document | Covers |
|---|---|
| [MediaAndRheology.md](MediaAndRheology.md) | Carrier, abrasive, grit, media life |
| [ProcessParameters.md](ProcessParameters.md) | Pressure, flow, cycles, temperature |
| [MaterialRemovalAndFinish.md](MaterialRemovalAndFinish.md) | Removal models, Ra decay, edge radius |
| [FixturingAndFlowControl.md](FixturingAndFlowControl.md) | Tooling, restrictors, branch balancing |
| [AdditiveApplications.md](AdditiveApplications.md) | Finishing LPBF passages, and what it cannot fix |
| [VerificationAndInspection.md](VerificationAndInspection.md) | Flow test, borescope, CT, replication |
| [ProcessQualification.md](ProcessQualification.md) | Coupons, first article, production control |
| [StandardsIndex.md](StandardsIndex.md) | Annotated standards and vendor practice |

---

## References

1. Rhoades, L. J., "Abrasive Flow Machining", *Manufacturing Engineering*, Vol. 101, 1988.
2. Jain, V. K. and Adsul, S. G., "Experimental Investigations into Abrasive Flow Machining", *International Journal of Machine Tools and Manufacture*, Vol. 40, 2000.
3. Gradl, P. R. et al., *Metal Additive Manufacturing for Propulsion Applications*, AIAA, 2022.
