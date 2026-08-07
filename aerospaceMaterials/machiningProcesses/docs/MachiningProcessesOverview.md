[Home](../README.md) > Machining Processes Overview

# Machining Processes Overview

## Contents

- [Overview](#overview)
- [The processes](#the-processes)
- [Machinability](#machinability)
- [The four questions](#the-four-questions)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [Document index](#document-index)
- [References](#references)

---

## Overview

Machining is the default manufacturing route: no tooling, any geometry, the best tolerances available, and an unbeatable lead time. Its cost is the material it removes and the time it takes, and both scale badly with the alloy.

For aerospace the discipline is not how to cut metal but how to cut it without distorting the part, chattering the surface, or destroying the fatigue life of the material left behind.

---

## The processes

| Process | Tolerance | Ra | Use |
|---|---|---|---|
| **Milling** | IT7 | 1.6 um | The general answer. Pockets, faces, contours |
| **Turning** | IT7 | 1.6 um | Bodies of revolution |
| **Drilling** | IT10 | 3.2 um | Holes, and the poorest tolerance |
| **Grinding** | IT5 | 0.4 um | Hard materials, tight tolerance, fine finish |
| **Boring** | IT6 | 0.8 um | Precise holes, better than drilling |
| **Reaming** | IT7 | 0.8 um | Finishing a drilled hole |
| Broaching | IT7 | 1.6 um | Internal forms, at quantity |
| **Wire EDM** | IT7 | 1.6 um | Hard materials, sharp internal corners |

**Drilling is the weakest link in most parts.** IT10 is two to three grades worse than milling, and a hole that has to be located and sized precisely needs boring or reaming after it.

**Grinding is the only route to IT5**, and it is also the route for hardened material that a cutting tool cannot handle.

**Wire EDM cuts anything conductive regardless of hardness**, at the cost of a recast layer that has to be removed if the surface is fatigue critical.

---

## Machinability

**Indexed to free machining steel at 100.**

| Material | Index | Taylor n | Taylor C [m/min] | Specific energy [J/mm^3] |
|---|---|---|---|---|
| **6061-T6** | **190** | 0.30 | 800 | 0.7 |
| 2219-T87 | 130 | 0.28 | 600 | 0.8 |
| 7075-T73 | 120 | 0.28 | 550 | 0.8 |
| 4340 | 55 | 0.22 | 200 | 2.8 |
| **316L** | **45** | 0.20 | 150 | 3.0 |
| 17-4PH H1025 | 40 | 0.20 | 140 | 3.2 |
| **TI-6AL-4V** | **22** | **0.20** | **75** | **3.5** |
| **INCONEL 718** | **12** | **0.18** | **40** | **4.5** |

**The spread is a factor of sixteen** between 6061 and Inconel 718, and it is the single biggest driver of machining cost after part volume.

**Titanium and nickel are hard to machine for the same reason: low thermal conductivity.** The heat generated at the cutting edge has nowhere to go except into the tool, so tool temperature rises fast and the tool fails. That is why both are cut slowly with high pressure coolant.

**Aluminium is machined at ten times the speed of Inconel** and the difference is why an aluminium structure is cheap and a nickel one is not, independent of the raw material price.

---

## The four questions

Every machining plan answers four questions and they are largely independent.

| Question | Governing analysis | Document |
|---|---|---|
| **What force and power?** | Specific cutting energy | [CuttingForce.md](CuttingForce.md) |
| **How long does the tool last?** | Taylor `V T^n = C` | [ToolLife.md](ToolLife.md) |
| **Will it chatter?** | Stability lobes | [ChatterAndStability.md](ChatterAndStability.md) |
| **Will the part move?** | Deflection and residual stress | [ThinWallMachining.md](ThinWallMachining.md), [DistortionControl.md](DistortionControl.md) |

**On an aerospace part the last two usually govern**, and that is what distinguishes aerospace machining from general machining. A thin walled aluminium structural part is almost never limited by force or by tool life; it is limited by deflection, chatter and the distortion released when the stock comes off.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Machinability spread | 16x, 6061 to IN718 |
| Taylor exponent | 0.18 to 0.30 |
| Specific energy | 0.7 J/mm^3 aluminium, 4.5 IN718 |
| Drilling is IT10 | Bore or ream for anything better |
| Grinding for IT5 | And for hardened material |
| Deflection and distortion govern aerospace parts | Not force or tool life |
| Wire EDM leaves a recast layer | Remove it if fatigue matters |

---

## Failure modes

**Aluminium speeds applied to titanium.** The tool fails in seconds.

**Thin wall machined to nominal.** It deflects away from the cutter and the wall is thick.

**Symmetric stock removal assumed.** Asymmetric removal releases residual stress and the part bows.

**Chatter treated as a feeds and speeds problem.** It is a dynamics problem with a stability map.

**Recast layer left on a fatigue critical EDM surface.** A cracked brittle layer.

**Drilled hole assumed located to milling tolerance.** It is two grades worse.

---

## Worked numbers

From [`MachiningProcess`](../machiningProcessesLibrary/MachiningProcess.py), a 12 mm end mill, 5 mm axial, 3 mm radial, 0.1 mm/tooth at 36 m/min:

| Material | Cutting force | Spindle power | Tool life |
|---|---|---|---|
| **6061** | 93.8 N | 0.06 kW | **19769 min** |
| 316L | 287.5 N | 0.17 kW | 3125 min |
| **INCONEL 718** | **500.0 N** | 0.30 kW | **2.0 min** |

**The same cut gives 19769 minutes of tool life in aluminium and 2 minutes in Inconel 718.** Force differs by 5.3x and tool life by four orders of magnitude, which is why cutting speed rather than force is the parameter that gets controlled.

**Slowing 20 percent multiplies the tool life by `1.2^(1/n)`**: 1.84 in 6061 and **3.37 in Inconel 718**. That sensitivity is the single most useful number in machining a difficult alloy.

---

## Standards

| Standard | Scope |
|---|---|
| **ISO 3685** | Tool life testing with single point turning tools |
| ISO 8688 | Tool life testing in milling |
| **ISO 286** | Limits and fits, IT grades |
| ISO 4287 / 21920 | Surface texture parameters |
| ASTM E837 | Residual stress by hole drilling |
| AMS 2649 | Etch inspection for grinding burn |
| SAE ARP4915 | Aerospace machining practices |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'machiningProcessesLibrary')

from MachiningProcess import MachiningProcess

machining = MachiningProcess()
machining.setInputs({'material': 'INCONEL 718', 'condition': 'sta', 'process': 'end mill',
                     'toolDiameter': 0.012, 'axialDepth': 0.005,
                     'radialDepth': 0.003, 'feedPerTooth': 0.0001})

machining.calculateCuttingForce()
machining.calculateToolLife()
print(machining.generateReport())
```

---

## Document index

| Document | Covers |
|---|---|
| [CuttingForce.md](CuttingForce.md) | Specific energy, force, power, spindle sizing |
| [ToolLife.md](ToolLife.md) | Taylor, the speed sensitivity, wear modes |
| [ChatterAndStability.md](ChatterAndStability.md) | Regenerative chatter, stability lobes, spindle speed selection |
| [ThinWallMachining.md](ThinWallMachining.md) | Deflection, pass strategy, support |
| [DistortionControl.md](DistortionControl.md) | Residual stress release, stress relief, symmetric removal |
| [SurfaceIntegrity.md](SurfaceIntegrity.md) | White layer, grinding burn, residual stress, fatigue |
| [Machinability.md](Machinability.md) | The index, why titanium and nickel are hard |
| [ToolingAndCoolant.md](ToolingAndCoolant.md) | Tool materials, coatings, high pressure coolant |
| [NonTraditionalMachining.md](NonTraditionalMachining.md) | EDM, ECM, waterjet, laser |
| [HoleMaking.md](HoleMaking.md) | Drilling, boring, reaming, and fastener holes |
| [ProcessComparison.md](ProcessComparison.md) | Against forming, casting and additive |

---

## References

1. Shaw, M. C., *Metal Cutting Principles*, 2nd ed., Oxford University Press, 2005.
2. Altintas, Y., *Manufacturing Automation*, 2nd ed., Cambridge University Press, 2012.
3. ASM Handbook Volume 16, *Machining*.
