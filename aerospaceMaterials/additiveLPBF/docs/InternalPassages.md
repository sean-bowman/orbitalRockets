[Home](../README.md) > Internal Passages

# Internal Passages

## Contents

- [Overview](#overview)
- [Why powder gets stuck](#why-powder-gets-stuck)
- [The aspect ratio limit](#the-aspect-ratio-limit)
- [Removing it](#removing-it)
- [Verifying it is gone](#verifying-it-is-gone)
- [What cannot be verified should not be closed](#what-cannot-be-verified-should-not-be-closed)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Internal passages are the reason to use this process and they are its largest risk. A passage that cannot be cleared of powder, or cleared and then verified, is a part with an uninspectable defect built into it by design.

This is the single topic where an additive programme is most likely to lose hardware.

---

## Why powder gets stuck

Loose powder in a passage is not simply loose. The heat of subsequent layers partially sinters the powder adjacent to the passage wall, so what fills the passage is a gradient from loose powder in the middle to a lightly bonded cake at the wall.

| Region | Condition |
|---|---|
| Passage centre | Loose, pours out |
| Near the wall | Partially sintered, needs mechanical or vibratory energy |
| At the wall | Bonded, and it is effectively part of the wall |

**The bonded layer is why a passage never comes out at its drawing dimension** and why flow testing an additive manifold is not optional.

---

## The aspect ratio limit

```
effectiveAspect = (L / D) * (1 + 0.5 * bends)
```

**Twenty to one is the practical limit**, and every bend counts against it because powder has to be shaken around a corner rather than poured out.

| Geometry | Effective aspect | Feasible |
|---|---|---|
| 4.76 mm x 60 mm, straight | 12.6 | Yes |
| 4.76 mm x 180 mm, straight | 37.8 | **No** |
| 4.76 mm x 180 mm, 2 bends | 75.6 | **No** |
| 2 mm x 200 mm, 3 bends | 250 | **No** |

**A long small passage is the hard case**, and it is exactly the case an integrated manifold produces.

---

## Removing it

| Method | Notes |
|---|---|
| **Gravity and orientation** | Free. Design the passage to drain, and orient the part so it does |
| **Vibration** | Effective on loose powder, poor on the sintered layer |
| **Compressed gas** | Blows the loose fraction out. Needs both ends open |
| **Ultrasonic in solvent** | Reaches the lightly sintered layer |
| **Abrasive flow machining** | Removes the bonded layer and improves the finish at the same time |
| Chemical | Rarely, and it attacks the part too |

**Designing the passage to drain is the highest-value measure and it is free.** A passage that runs downhill in the build orientation empties itself. One with a low point holds powder no matter what is done afterwards.

**Abrasive flow machining is the only method that removes the bonded layer**, and it needs a through-flow path with both ends accessible. That is a design requirement, set at concept. See [extrusionHoning](../../extrusionHoning/).

---

## Verifying it is gone

| Method | What it proves |
|---|---|
| **Computed tomography** | Directly. The only method that sees inside |
| **Flow test** | That the passage flows, and against what pressure drop |
| Borescope | Only what it can reach and see |
| Weighing | A gross check. Sensitive to a few grams at best |
| Radiography | Poorly. It integrates through thickness |

**Flow testing is the practical production check** and CT is the qualification one. A flow test against a qualified reference catches a partially blocked passage and it does not distinguish a blockage from a rough wall.

**Weighing is worth doing because it is nearly free.** A part significantly heavier than its model has powder in it somewhere.

---

## What cannot be verified should not be closed

**The rule this document exists for.**

If a passage cannot be verified clear, then the part has an unknown internal condition for its life. In a propulsion system that powder migrates downstream into an injector, a valve seat or a catalyst bed.

| If verification is impossible | Options |
|---|---|
| Split the part and join it | The joint is inspectable |
| Add an access port and plug it | The port is inspectable |
| Drill the passage conventionally | Not additive, and it works |
| Accept the risk | Only for a non-critical part, and it should be a written decision |

**The [`LpbfProcess`](../additiveLpbfLibrary/LpbfProcess.py) class raises rather than warns** on a passage beyond the aspect ratio limit, because a warning in a report is not the same as a decision.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Aspect ratio limit | 20 : 1 |
| Each bend | Counts as 0.5 extra L/D |
| Minimum channel | 0.5 mm, below which evacuation is impossible |
| Design the passage to drain | Free, and the highest-value measure |
| Both ends accessible | Required for abrasive flow and for gas |
| Verify by CT at qualification | Flow test in production |
| Weigh the part | Nearly free, catches the gross case |
| Unverifiable means redesign | Not accept and hope |

---

## Failure modes

**Powder left in a closed passage.** Migrates downstream in service.

**A dead-ended passage.** Cannot drain, cannot be honed.

**A low point in the build orientation.** Holds powder regardless of what follows.

**Verified by borescope where the borescope cannot reach.** Verified nothing.

**Radiography accepted as the verification.** It integrates through thickness.

**Flow test passed on a rough passage read as clear.** The two are not distinguishable by flow alone.

---

## Worked numbers

From [`LpbfProcess.checkPowderEvacuation`](../additiveLpbfLibrary/LpbfProcess.py):

| Passage | Bends | Effective aspect | Result |
|---|---|---|---|
| 4.76 mm x 60 mm | 0 | 12.6 | **feasible** |
| 4.76 mm x 180 mm | 2 | 75.6 | **raises `ProcessInfeasibleError`** |

The second is the thruster valve manifold from the [aerospaceMaterials worked example](../../codeInterface.py), and the class refusing it is the correct answer: that geometry has to be split or redesigned.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-6030** | Additive manufacturing requirements |
| MSFC-STD-3716 | LPBF spaceflight hardware |
| ASTM E1441 | Computed tomography imaging |
| **NASA-STD-5009** | NDE requirements for fracture critical components |
| ASTM F3335 | Assessing and qualifying non-destructive testing of AM parts with internal channels |

---

## Tool interface

```python
from LpbfProcess import LpbfProcess
from lpbfUtils import ProcessInfeasibleError

process = LpbfProcess()
process.setInputs({'material': 'Inconel 718'})

print(process.checkPowderEvacuation(0.00476, 0.060)['feasible'])      # True

try:
    process.checkPowderEvacuation(0.00476, 0.180, bends = 2)
except ProcessInfeasibleError as error:
    print(error)      # explains why, and what to do instead
```

---

## References

1. ASTM F3335-20, *Standard Guide for Assessing the Removal of Additive Manufacturing Residues*.
2. Gradl, P. R. et al., *Metal Additive Manufacturing for Propulsion Applications*, AIAA, 2022.
3. du Plessis, A. et al., "Standard Method for microCT-based Additive Manufacturing Quality Control", *MethodsX*, Vol. 5, 2018.
