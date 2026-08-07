[Home](../README.md) > Thin Wall Machining

# Thin Wall Machining

## Contents

- [Overview](#overview)
- [The deflection](#the-deflection)
- [The cubic dependence](#the-cubic-dependence)
- [Strategies](#strategies)
- [Support](#support)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Most aerospace structural machining is thin wall machining: isogrid, orthogrid, integrally stiffened panels and pocketed frames. The wall deflects away from the cutter, so the finished wall is thicker than the programmed one, and the error grows as the wall gets thinner.

---

## The deflection

**The wall is a cantilever plate loaded by the radial cutting force.**

```
delta = F_r * h^3 / (3 * E * I)
I = b * t^3 / 12
```

| Symbol | Meaning |
|---|---|
| `F_r` | Radial cutting force |
| `h` | Wall height, the cantilever length |
| `t` | Wall thickness |
| `b` | The effective width over which the load spreads |
| `E` | Elastic modulus |

**The effective width is not the axial depth of cut.** A point load on a plate spreads, and taking `b` as the axial engagement treats the wall as a narrow beam and greatly overstates the deflection.

**The correct treatment is plate spreading**, with the effective width taken as roughly twice the wall height or the axial depth, whichever is larger:

```
b_eff = max(2 h, a_p)
```

**Using the axial depth alone gave deflections of tens of millimetres** in an early version of the class, which is obviously wrong and was the signal that the model was incorrect.

---

## The cubic dependence

**Deflection goes as the cube of the height and the inverse cube of the thickness**, and both are severe.

| Change | Deflection |
|---|---|
| Wall height doubled | **8x** |
| Wall thickness halved | **8x** |
| Radial force halved | 0.5x |
| A stiffer material | Inversely with `E` |

**Halving the wall thickness multiplies the deflection by eight**, which is why the last finishing pass on a thin wall is the difficult one: the wall is thinnest exactly when it is being finished.

**A 60 mm tall, 1.5 mm aluminium wall is very compliant**, and it is a completely normal aerospace feature. That geometry is why isogrid machining is a speciality.

**Titanium is stiffer than aluminium by 1.65x in modulus** and its cutting forces are five times higher, so a titanium thin wall deflects roughly three times as much as an aluminium one of the same geometry.

---

## Strategies

| Strategy | Effect |
|---|---|
| **Multiple finishing passes** | Each removes less, so each deflects less |
| **Spring passes** | A final pass at zero nominal depth, cutting what the deflection left |
| **Top-down layering** | Machine the top of the wall to depth before going lower |
| **Reduced radial engagement** | Lower `F_r` |
| **Climb milling** | Lower and more consistent radial force |
| Deflection compensation | Offset the toolpath by the predicted deflection |

**Top-down layering is the important one and it is not obvious.** Machining the full wall height in one pass leaves the whole wall standing and compliant for the entire cut. Machining in layers, taking the top few millimetres of both sides to final thickness before descending, means the compliant portion is only ever a few millimetres tall.

**The cubic dependence is what makes it work.** A 5 mm tall standing wall deflects `(5/60)^3` of a 60 mm one, which is a factor of 1700.

**Spring passes are the crude answer** and they work. A pass at the same nominal position removes the material the previous pass deflected away from, and two or three converge.

**Deflection compensation needs a good force model** and it is used in production isogrid machining, where the geometry is regular and the compensation can be verified once and reused.

---

## Support

| Method | Detail |
|---|---|
| **Wax or low melting alloy fill** | Pockets filled, machined, then melted out |
| **Vacuum fixturing** | Distributed support on the back face |
| Followers | A support that tracks the cutter on the far side |
| Sacrificial ribs | Machined away last |
| **Freeze fixturing** | The part frozen into an ice or water-based medium |

**Wax fill is the traditional answer** for a pocketed panel and it is effective and slow. The pockets are filled after roughing, the walls are finished against a supported back face, and the wax is melted out.

**Sacrificial ribs are the cheapest** and they need the toolpath to reach them last, which constrains the machining sequence.

**Vacuum fixturing supports the back face without adding anything to the part**, and it works only where the back face is flat and accessible.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| `delta = F_r h^3 / (3 E I)` | Cantilever plate |
| Effective width | `max(2h, a_p)`, not `a_p` |
| Deflection goes as `h^3` and `1/t^3` | Both severe |
| Top-down layering | The most effective strategy |
| Spring passes | Two or three converge |
| Climb milling | Lower and steadier radial force |
| Titanium deflects ~3x aluminium | Higher force, and only 1.65x the modulus |
| Wax fill for pocketed panels | Effective and slow |

---

## Failure modes

**Wall machined in one full-height pass.** Maximum compliance for the whole cut.

**Effective width taken as the axial depth.** The deflection is greatly overstated.

**Single finishing pass on a thin wall.** The wall is thick by the deflection.

**Deflection compensation applied without a verified force model.** The error moves rather than going away.

**Wax fill omitted on a deep pocketed panel.** Chatter and wall thickness variation.

**Aluminium strategy applied to titanium.** Three times the deflection.

---

## Worked numbers

From [`MachiningProcess.calculateThinWallDeflection`](../machiningProcessesLibrary/MachiningProcess.py), a 12 mm 4 flute end mill in 6061-T6, 5 mm axial, 3 mm radial:

| Wall | Height | Thickness | Deflection | Passes needed |
|---|---|---|---|---|
| Short and thick | 20 mm | 3.0 mm | small | 1 |
| **Tall and thin** | **60 mm** | **1.5 mm** | **large** | **several** |

**The tolerance threshold in the class is 25 um**, below which a single pass is adequate.

---

## Standards

| Standard | Scope |
|---|---|
| ISO 286 | Limits and fits, IT grades |
| ISO 2768 | General tolerances |
| ASME Y14.5 | Dimensioning and tolerancing |
| SAE ARP4915 | Aerospace machining practices |

---

## Tool interface

```python
from MachiningProcess import MachiningProcess, THIN_WALL_TOLERANCE

machining = MachiningProcess()
machining.setInputs({'material': '6061', 'process': 'end mill',
                     'toolDiameter': 0.012, 'axialDepth': 0.005,
                     'radialDepth': 0.003, 'feedPerTooth': 0.0001})
machining.calculateCuttingForce()

for height, thickness in ((0.020, 0.003), (0.060, 0.0015)):
    result = machining.calculateThinWallDeflection(wallHeight = height,
                                                   wallThickness = thickness)
    print(f'{height*1000:4.0f} x {thickness*1000:4.1f} mm: '
          f'{result["deflection"]*1e6:9.1f} um, '
          f'{result["springPassesRequired"]} spring passes')
```

---

## References

1. Altintas, Y., *Manufacturing Automation*, 2nd ed., Cambridge University Press, 2012.
2. Ratchev, S. et al., "Milling Error Prediction and Compensation in Machining of Low-Rigidity Parts", *International Journal of Machine Tools and Manufacture*, Vol. 44, 2004.
3. ASM Handbook Volume 16, *Machining*.
