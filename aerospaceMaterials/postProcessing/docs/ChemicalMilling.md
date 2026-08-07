[Home](../README.md) > Chemical Milling

# Chemical Milling

## Contents

- [Overview](#overview)
- [The process](#the-process)
- [Both surfaces](#both-surfaces)
- [Masking](#masking)
- [Undercut](#undercut)
- [What it does not do](#what-it-does-not-do)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Chemical milling removes metal by controlled etching. It is the process that makes isogrid panels, that thins tank domes, and that removes alpha case from titanium.

It has one property that makes it uniquely useful and one that catches people out, and they are the same property: it removes material uniformly from every wetted surface.

---

## The process

| Step | Detail |
|---|---|
| **Clean** | Any contamination masks the etch locally |
| **Mask** | A maskant applied to surfaces that must not be etched |
| **Scribe and strip** | The maskant cut and peeled where etching is wanted |
| **Etch** | Immersion in the etchant, timed |
| **Rinse and demask** | |
| **Inspect** | Thickness, usually ultrasonic |

**Time is the control.** The etch rate is a property of the etchant, its concentration and its temperature, and the depth is the rate multiplied by the time. That makes the process controllable and it makes it entirely dependent on bath control.

| Alloy | Etchant | Rate |
|---|---|---|
| Aluminium | Sodium hydroxide | 20 to 40 um/min |
| Titanium | Nitric and hydrofluoric acid | 10 to 25 um/min |
| Steel and stainless | Ferric chloride or nitric | 10 to 30 um/min |
| Nickel alloys | Ferric chloride | 5 to 15 um/min |

---

## Both surfaces

**The error people make.** A part immersed in etchant is attacked on every wetted surface, so a wall loses stock from both sides and the thickness falls by twice the removal depth.

```
remainingWall = initialWall - 2 * removalDepth
```

**A 0.15 mm etch on a 2 mm wall leaves 1.7 mm, not 1.85.**

**Masking one side is possible and it is an extra operation with its own failure modes**: a maskant that lifts, a scribe that cuts too deep, a pinhole that etches a spot. The default assumption should be that both sides are attacked, and single-sided etching should be a deliberate decision with its own controls.

---

## Masking

The maskant is the tooling of the process.

| Type | Use |
|---|---|
| **Peelable elastomer** | The standard. Sprayed or dipped, cured, scribed and peeled |
| Photoresist | Fine detail, where a scribe cannot hold the tolerance |
| Mechanical | Plugs and caps for holes and ports |
| Tape | Small areas and repairs |

**Failure modes of the maskant are the failure modes of the process:**

| Failure | Result |
|---|---|
| Lifting at an edge | Undercut beyond the scribe line |
| Pinhole | A local pit, often not found until inspection |
| Scribed too deep | A witness line in the surface |
| Incomplete cure | General lifting |

**Scribing is a manual operation on most parts** and it is where the dimensional accuracy of the process is set.

---

## Undercut

**The etch attacks sideways as well as downward**, so material is removed under the maskant edge.

```
undercut ~ etchDepth
```

The undercut ratio is roughly 1:1 for most alloys and etchants, so a 2 mm deep etch removes about 2 mm laterally beyond the scribe line.

**The scribe line has to be offset inward by the expected undercut**, and that offset is a process parameter that has to be established rather than assumed. It varies with alloy, etchant, temperature and depth.

**Undercut sets the minimum feature spacing.** Two pockets 3 mm apart etched 2 mm deep will meet.

---

## What it does not do

| Expectation | Reality |
|---|---|
| **Improve surface finish** | **No.** It removes uniformly, preserving the profile |
| Remove a deep scratch | No. It deepens it, because the scratch etches too |
| Correct geometry | No. It follows the existing surface |
| Introduce residual stress | No, and that is a genuine advantage over machining |

**The finish point surprises people.** Chemical milling removes peaks and valleys at the same rate, so the profile moves inward unchanged and the Ra is the same afterwards. Electropolishing removes peaks preferentially, which is why it improves Ra and chem mill does not. See [Electropolishing.md](Electropolishing.md).

**No residual stress is the real advantage.** A chem milled surface carries no machining residual stress and no work hardened layer, which matters on a thin panel that would distort if machined.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Both surfaces are attacked | Wall loses 2x the etch depth |
| Undercut | ~1:1 with depth |
| Minimum feature spacing | ~2x the etch depth |
| Etch rate | 5 to 40 um/min by alloy |
| No finish improvement | The profile is preserved |
| No residual stress | The advantage over machining |
| Time is the control | Bath control is everything |
| Verify thickness ultrasonically | Not by calculation |

---

## Failure modes

**Etch depth sized for one surface.** The wall is half what was intended.

**Maskant lifted.** Undercut well beyond the scribe.

**Pinhole in the maskant.** A local pit.

**Undercut not allowed for.** Features meet or the dimension is wrong.

**Expected to improve the finish.** It does not.

**Bath concentration drifted.** The rate changed and the timing is wrong.

---

## Worked numbers

From [`SurfaceTreatment.calculateStockRemoval`](../postProcessingLibrary/SurfaceTreatment.py), 316L at 25 um/min for 10 minutes on a 3.00 mm wall:

| Quantity | Value |
|---|---|
| Removal per surface | 0.250 mm |
| **Removal from the wall** | **0.500 mm** |
| Remaining wall | **2.500 mm** |
| Ra before | 3.2 um |
| **Ra after** | **3.2 um, unchanged** |

The class raises a `ProcessInfeasibleError` if the etch would remove the whole wall, because that is a specification error rather than a marginal result.

---

## Standards

| Standard | Scope |
|---|---|
| **SAE AMS 2680** | Chemical milling of aluminium alloys |
| SAE AMS 2681 | Chemical milling of titanium alloys |
| AMS 2700 | Passivation, which often follows |
| MIL-C-81769 | Chemical milling of metals, general |
| ASTM E797 | Ultrasonic thickness measurement |

---

## Tool interface

```python
from SurfaceTreatment import SurfaceTreatment

treatment = SurfaceTreatment()
treatment.setInputs({'material': '316L', 'condition': 'annealed',
                     'alloyFamily': 'stainless', 'wallThickness': 0.003,
                     'initialRoughness': 3.2e-6})

result = treatment.calculateStockRemoval('chemical mill', processTime = 600.0,
                                         etchRate = 25.0e-6)
print(result['stockRemovalPerSurface'], result['stockRemovalBothSurfaces'])
print(result['initialRoughness'], result['finalRoughness'])    # unchanged
```

---

## References

1. SAE AMS 2680, *Chemical Milling of Aluminum Alloys*.
2. Harris, W. T., *Chemical Milling: The Technology of Cutting Materials by Etching*, Clarendon Press, 1976.
3. Davis, J. R. (ed.), *Surface Engineering for Corrosion and Wear Resistance*, ASM, 2001.
