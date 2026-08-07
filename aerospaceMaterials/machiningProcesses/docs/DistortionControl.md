[Home](../README.md) > Distortion Control

# Distortion Control

## Contents

- [Overview](#overview)
- [Where the stress comes from](#where-the-stress-comes-from)
- [Why asymmetric removal bows the part](#why-asymmetric-removal-bows-the-part)
- [The stress profile matters](#the-stress-profile-matters)
- [Controls](#controls)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A part that was flat in the fixture and is bowed on the surface plate has released residual stress. The stress was already in the stock, it was self-equilibrating, and machining broke the equilibrium.

This is the commonest cause of scrap on large machined aerospace structure and it is entirely predictable.

---

## Where the stress comes from

| Source | Magnitude | Character |
|---|---|---|
| **Quenching** | **100 to 200 MPa** | Compressive surface, tensile core |
| Rolling or forming | Varies | Direction dependent |
| **Machining itself** | 50 to 300 MPa | A thin surface layer only |
| Welding | High, local | Around the joint |

**Quench stress is the dominant source in thick aluminium plate**, and it is unavoidable: a solution treated plate has to be quenched fast enough to keep the solute in solution, and fast quenching means a steep thermal gradient and a large residual stress.

**The profile is compressive at the surfaces and tensile in the core**, because the surface solidifies and contracts first and the core contracts later against a constrained surface.

**It is self-equilibrating.** The net force and net moment are zero across the full thickness, which is why the plate is flat as delivered.

**Stress relieved tempers exist for this reason.** 7050-T7451 is T7451 rather than T7 precisely because the plate has been mechanically stress relieved by controlled stretching, taking the quench stress from perhaps 180 MPa down to 20 or 30. **On a large machined part it is worth paying for the stress relieved temper**, and it is often not specified.

---

## Why asymmetric removal bows the part

**Removing material from one face removes part of the balancing force, and the remaining stress distribution has a net moment.**

| Removal | Result |
|---|---|
| **Symmetric, both faces equally** | The moment stays zero. **No bow** |
| **Asymmetric, one face** | A net moment. **The part bows** |
| Pocketing one side | Asymmetric by definition |

**Almost every aerospace machined part is asymmetric**, because it is a pocketed panel or a stiffened structure with material on one side.

**The bow is a curvature, so it grows with the square of the length:**

```
delta = M L^2 / (8 E I)
```

**A 1 m panel bows sixteen times as much as a 250 mm one** with the same moment per unit width, which is why distortion is a large part problem specifically.

---

## The stress profile matters

**Treating the removed layer as carrying a uniform stress overstates the distortion badly, and it is the intuitive mistake.**

Quench residual stress is not uniform. It varies through the thickness, roughly parabolically, from compression at the surfaces to tension at the core:

```
sigma(z) = sigma_residual * (3 (2z/t)^2 - 1) / 2
```

with `z` measured from the mid-plane. That form has zero net force and zero net moment, as it must.

**Integrating this profile over the removed layer gives the released moment.**

**Assuming the removed layer carries the full surface stress uniformly overstates the result by roughly four times**, because the layer near the mid-plane is in tension, not compression, and it partly cancels.

**In an early version of the class this error gave a 12.47 mm bow on a panel that actually bows 3.12 mm.** Both numbers are large, and the difference between them is the difference between a part that can be straightened and one that is scrap.

---

## Controls

| Control | Effect |
|---|---|
| **Stress relieved stock** | T7451, T851. **Attack the cause** |
| **Symmetric removal** | Alternate faces, keep the moment near zero |
| **Rough, stress relieve, finish** | Let it move, then cut it true |
| **Rough oversize, allow to move, re-datum** | The practical production answer |
| Fixturing that does not constrain | A constrained part relaxes after unclamping |
| Vibratory stress relief | Cheap, and its effectiveness is debated |
| Cryogenic and uphill quenching | Specialised |

**Buying stress relieved stock is by far the most effective control** and it is a purchase order line rather than a process. The mechanical stretch that produces a T7451 temper removes most of the quench stress before any material is machined.

**Rough, stress relieve, finish is the classical route** and it costs a thermal cycle and a re-fixturing. It works.

**Rough oversize, unclamp, let it move, re-datum and finish is what production actually does**, and it works because the finishing cuts are light enough to release very little further stress.

**Fixturing that clamps a bowed part flat does not fix anything.** The part is elastic in the fixture, machined true in that state, and it springs back when unclamped. The distortion appears at final inspection instead of at rough.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Quench stress | 100 to 200 MPa in thick plate |
| Stress relieved temper | 20 to 30 MPa. Specify it |
| Symmetric removal keeps the moment zero | |
| Bow grows as `L^2` | A large part problem |
| The profile is parabolic, not uniform | 4x difference |
| Rough, relieve, finish | The classical route |
| Rough oversize and re-datum | The production route |
| Clamping flat fixes nothing | It springs back |

---

## Failure modes

**Non-stress-relieved plate used for a large pocketed panel.** Predictable scrap.

**Uniform stress assumed in the removed layer.** The distortion is overstated 4x.

**Part clamped flat and machined true.** It springs back after unclamping.

**Finish machining before the part has moved.** The distortion appears at final inspection.

**Datums not re-established after roughing.** Everything is referenced to a surface that moved.

**Distortion treated as a fixturing problem.** It is a residual stress problem.

---

## Worked numbers

From [`MachiningProcess.calculateDistortion`](../machiningProcessesLibrary/MachiningProcess.py), a 500 mm long 25 mm plate with 150 MPa residual stress, 5 mm removed from one face:

| Model | Bow |
|---|---|
| Uniform stress in the removed layer | 12.47 mm |
| **Parabolic self-equilibrating profile** | **3.12 mm** |

**The parabolic result is the correct one** and it is what the class computes. The uniform assumption is recorded here because it is the natural first guess and it is wrong by four times.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM E837** | Residual stress by the hole drilling strain gauge method |
| ASTM E915 | X-ray diffraction residual stress measurement alignment |
| **AMS 2770** | Heat treatment of wrought aluminium alloys, including stress relieved tempers |
| AMS-QQ-A-250 | Aluminium plate, including T7451 |
| SAE ARP4915 | Aerospace machining practices |

---

## Tool interface

```python
from MachiningProcess import MachiningProcess

machining = MachiningProcess()
machining.setInputs({'material': '7075', 'condition': 't73', 'process': 'end mill',
                     'toolDiameter': 0.020, 'axialDepth': 0.005,
                     'radialDepth': 0.003, 'feedPerTooth': 0.0001})
result = machining.calculateDistortion(residualStress = 150.0e6,
                                       plateThickness = 0.025,
                                       machinedFraction = 0.20,
                                       partLength = 0.500)
for key in sorted(result):
    print(f'  {key}: {result[key]}')
```

---

## References

1. Withers, P. J. and Bhadeshia, H. K. D. H., "Residual Stress Part 1: Measurement Techniques", *Materials Science and Technology*, Vol. 17, 2001.
2. Prime, M. B. and Hill, M. R., "Residual Stress, Stress Relief, and Inhomogeneity in Aluminum Plate", *Scripta Materialia*, Vol. 46, 2002.
3. ASM Handbook Volume 16, *Machining*.
