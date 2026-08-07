[Home](../README.md) > Surface Condition

# Surface Condition

## Contents

- [Overview](#overview)
- [Where the roughness comes from](#where-the-roughness-comes-from)
- [Roughness by orientation](#roughness-by-orientation)
- [Why it matters](#why-it-matters)
- [What improves it](#what-improves-it)
- [Internal surfaces](#internal-surfaces)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

As-built LPBF surfaces are between ten and thirty times rougher than drawn tube. On an external surface that is a machining operation. On an internal passage it is a permanent property unless the passage is accessible to abrasive flow.

---

## Where the roughness comes from

| Mechanism | Contribution |
|---|---|
| **Partially melted particles** | Powder adhering at the melt pool edge. The dominant term |
| **Stair stepping** | Layer discretisation of a sloped surface. Scales with layer thickness |
| **Balling** | Surface tension breaking a track into beads where energy is marginal |
| **Spatter** | Ejected droplets landing and being melted in |
| **Down-skin sinking** | The pool sinks into loose powder before it freezes |

**Adhering particles dominate**, which is why roughness scales with particle size as much as with layer thickness, and why a finer powder gives a better surface at the cost of flowability.

---

## Roughness by orientation

| Surface | Ra | Note |
|---|---|---|
| **Up-skin** | 12 um | Top facing. Best case |
| **Vertical wall** | 20 um | The reference |
| **Down-skin** | 40 um | Sitting on loose powder |
| Drawn tube, for comparison | 1.5 um | |

**Down-skin is twice vertical and the mechanism is different.** The melt pool has nothing solid beneath it, so it sinks into the powder and freezes with a rounded, particle-encrusted underside. Below the 45 degree self-supporting angle it gets rapidly worse.

**The transition is continuous with angle**, not a step, so a surface at 50 degrees is already degrading even though it is technically self-supporting.

---

## Why it matters

| Consequence | Magnitude |
|---|---|
| **Fatigue** | A 30 to 50 % debit as-built, because every adhering particle is a notch |
| **Flow** | An additive manifold sized on drawn-tube roughness badly under-predicts its own pressure drop |
| **Cleanliness** | A rough surface traps contamination and is hard to verify clean |
| **Sealing** | An as-built surface is not a sealing surface at any Ra |
| **Fretting and wear** | Asperities are the initiation sites |

**The flow consequence is the one that reaches other domains.** A 20 um internal surface against 1.5 for drawn tube is a factor of 13 in relative roughness, and in a small-bore passage that is squarely in the roughness-dependent region of the Moody diagram. The claim is made in the docstring of `roughnessTable()` in [common/materials.py](../../../common/materials.py) and it is demonstrated in the [aerospaceMaterials worked example](../../codeInterface.py).

---

## What improves it

| Method | Achievable Ra | Access needed |
|---|---|---|
| **Machining** | 1.6 um | External, with a datum |
| **Abrasive flow machining** | 5 um from 20 | Through-flow path |
| Electropolishing | 0.4 um floor | Wetted, and it removes stock from both sides |
| Vibratory finishing | 3 um | External, and it rounds edges |
| Micro-machining or laser polishing | 2 um | Line of sight |
| Chemical milling | No improvement | It removes uniformly, preserving the profile |

**Chemical milling does not improve roughness**, which surprises people. It removes material uniformly, so the peaks and valleys move inward together and the profile is preserved. Electropolishing removes the peaks preferentially, which is why it does improve Ra.

**Contour parameter optimisation** is the cheapest improvement available and it happens during the build. A separate perimeter parameter set can take a vertical wall from 20 um to perhaps 8, at no post-processing cost.

---

## Internal surfaces

**The constraint that shapes additive design.**

An internal passage cannot be machined, cannot be vibratory finished, and cannot be reached by any line-of-sight process. The only options are:

| Option | Requirement |
|---|---|
| **Abrasive flow machining** | A through-flow path with both ends accessible |
| Electropolishing | The passage must be wetted and an electrode reachable |
| Nothing | The as-built surface is what the part has for its life |

**Design the flow path so it can be honed.** A passage with a dead end cannot be abrasive flow machined, because the media has nowhere to go. That is a design decision made at concept, not a finishing decision made later. See [extrusionHoning](../../extrusionHoning/).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Vertical wall as-built | 20 um Ra |
| Down-skin as-built | 40 um Ra |
| Up-skin as-built | 12 um Ra |
| After abrasive flow | 5 um Ra |
| After machining | 1.6 um Ra |
| Fatigue debit, as-built surface | 30 to 50 % |
| An as-built surface is not a sealing surface | At any Ra |
| Design internal passages so they can be honed | Both ends accessible |
| Optimise contour parameters | The cheapest improvement there is |

---

## Failure modes

**A manifold sized on drawn-tube roughness.** Pressure drop badly under-predicted.

**An as-built surface used as a seal face.** It leaks.

**A dead-ended internal passage.** Cannot be finished at all.

**Fatigue allowable taken from a machined coupon and applied to an as-built surface.** Overstated by a factor of two.

**Chemical milling specified to improve a finish.** It does not.

---

## Worked numbers

From [`LpbfProcess`](../additiveLpbfLibrary/LpbfProcess.py) and [`ExtrusionHoning`](../../extrusionHoning/extrusionHoningLibrary/ExtrusionHoning.py):

| Quantity | Value |
|---|---|
| Vertical wall, as-built | 20.0 um Ra |
| Down-skin at 20 degrees | 35.6 um Ra |
| Ratio to drawn tube | **13x** |
| After 20 cycles of abrasive flow | **5.06 um Ra** |
| Improvement | **4.0x** |
| Grit-limited floor, medium media | 5.00 um Ra |

The 4.0x improvement matches the `roughnessTable` entries in the shared common package exactly, and a test asserts it so the two cannot drift.

---

## Standards

| Standard | Scope |
|---|---|
| **ISO 4287 / 21920** | Surface texture, profile method |
| ASME B46.1 | Surface texture |
| ISO/ASTM 52902 | Test artefacts for geometric capability assessment |
| ASTM F3301 | Post-processing methods |

---

## Tool interface

```python
from LpbfProcess import LpbfProcess

process = LpbfProcess()
process.setInputs({'material': 'Inconel 718'})

for angle in (170.0, 90.0, 45.0, 20.0):
    result = process.predictSurfaceRoughness(angle)
    print(angle, result['orientation'], result['roughnessMicrometres'])
```

---

## References

1. Townsend, A. et al., "Surface Texture Metrology for Metal Additive Manufacturing: A Review", *Precision Engineering*, Vol. 46, 2016.
2. Strano, G. et al., "Surface Roughness Analysis, Modelling and Prediction in Selective Laser Melting", *Journal of Materials Processing Technology*, Vol. 213, 2013.
3. Gradl, P. R. et al., "Metal Additive Manufacturing in Aerospace: A Review", *Materials and Design*, Vol. 209, 2021.
