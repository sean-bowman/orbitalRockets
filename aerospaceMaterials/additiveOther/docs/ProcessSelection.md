[Home](../README.md) > Process Selection

# Process Selection

## Contents

- [Overview](#overview)
- [The decision sequence](#the-decision-sequence)
- [The selection table](#the-selection-table)
- [Size](#size)
- [Rate against resolution](#rate-against-resolution)
- [Material](#material)
- [Design rules of thumb](#design-rules-of-thumb)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Six additive processes with different envelopes, and the selection reduces to four questions asked in order. Asking them in the right order eliminates most of the options before any detailed comparison is needed.

---

## The decision sequence

| Order | Question | Effect |
|---|---|---|
| **1** | **Is it a repair?** | Only DED and cold spray qualify |
| **2** | **Does it fit in a build chamber?** | Above ~400 mm, only DED and WAAM |
| **3** | **What resolution does it need?** | Fine internal geometry means powder bed |
| **4** | **What is the material?** | Reactive, crack prone, or non-conductive narrows it |

**Repair is the first question because it eliminates four of the six** immediately, and it is often not asked because additive is assumed to mean new build.

**Size is the second because it is binary.** A part larger than the build chamber is not an LPBF part at any price, and no amount of optimisation changes that.

---

## The selection table

| Need | Process | Second choice |
|---|---|---|
| **Fine internal geometry** | **LPBF** | -- |
| **Low residual stress, crack prone alloy** | **EB-PBF** | LPBF with a heated plate |
| **Large structure, near net** | **WAAM** | DED |
| **Large structure, better resolution** | **DED** | WAAM plus more machining |
| **Repair, substrate can take heat** | **DED** | Conventional weld repair |
| **Repair, substrate cannot** | **Cold spray** | -- |
| **Volume production, moderate properties** | **Binder jetting** | LPBF at higher cost |
| **A casting mould** | **Binder jet sand** | Conventional pattern |
| Functionally graded material | DED | -- |
| TiAl | **EB-PBF** | -- |

---

## Size

| Process | Practical limit |
|---|---|
| LPBF | 400 mm, and up to 800 in large machines |
| EB-PBF | 350 mm |
| Binder jetting | 500 mm, less after 20 % shrinkage |
| **DED** | **Metres.** Robot reach |
| **WAAM** | **Metres.** Robot reach |
| **Cold spray** | **Unlimited.** Handheld or robot |

**The 400 mm cliff is the single most consequential number in additive process selection**, because it divides the field cleanly and it is not negotiable.

**Segmentation and joining is the alternative** for a part slightly over the limit: build in pieces and weld or bolt them. That reintroduces a joint, with its knockdown and its inspection requirement, and it is often still the right answer.

---

## Rate against resolution

| Process | Rate [cm^3/h] | Tolerance | Minimum feature |
|---|---|---|---|
| LPBF | 20 to 80 | **IT8** | **0.4 mm** |
| EB-PBF | 55 to 110 | IT10 | 0.6 mm |
| Binder jet | High | IT11 | 1.0 mm |
| DED | 50 to 500 | IT12 | 1.5 mm |
| **Cold spray** | 500 to 3000 | IT13 | Coarse |
| **WAAM** | **500 to 5000** | **IT14** | **3 mm** |

**The trade is monotonic**, which makes it easy to reason about: every step up in rate costs resolution, and there is no process that gives both.

**Two orders of magnitude in rate and six IT grades in tolerance** span the table, and a part's requirements usually place it clearly.

**Machining allowance is the way to compare them fairly.** A WAAM part needs 3 to 6 mm per surface and an LPBF part needs 0.5 to 1 mm, and once that is in the buy-to-fly the comparison is honest.

---

## Material

| Constraint | Excludes |
|---|---|
| **Non-conductive** | **EB-PBF.** The bed smokes |
| **Crack prone (TiAl, some superalloys)** | **LPBF.** Solidification cracking |
| **Reactive (Ti)** | Nothing, but each process handles it differently |
| **Heat sensitive substrate** | Everything except **cold spray** |
| High reflectivity (Cu, Al) | Conventional LPBF. Green or blue lasers solve it |
| Available as wire only | Powder bed processes |
| Available as powder only | WAAM |

**Feedstock availability is a real constraint** and it is often discovered late. An alloy available as bar and plate is not necessarily available as gas atomised spherical powder in the right size distribution, or as welding wire, and qualifying a new feedstock is a programme in itself.

**Copper's reflectivity defeated conventional infrared LPBF** for years, and green and blue diode lasers have solved it. GRCop-42 chamber liners are the result. See [wroughtMaterials CopperAlloys.md](../../wroughtMaterials/docs/CopperAlloys.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Ask repair first | It eliminates four of six |
| Then size | 400 mm is a cliff |
| Then resolution | Fine internal means powder bed |
| Then material | Reactive, crack prone, non-conductive |
| Rate and resolution trade monotonically | No process gives both |
| Compare with the machining allowance included | Or the comparison is dishonest |
| Check feedstock availability early | It is a programme in itself |

---

## Standards

| Standard | Scope |
|---|---|
| **ISO/ASTM 52900** | Additive manufacturing terminology and process categories |
| **NASA-STD-6030** | Additive manufacturing requirements for spaceflight |
| ISO/ASTM 52911 | Design for powder bed fusion |
| ASTM F3187 | Directed energy deposition |
| ASTM F3339 | Cold spray |
| AWS D20.1 | Fabrication of metal components using additive manufacturing |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterialsLibrary')

from ProcessComparison import ProcessComparison

for size in (0.150, 1.500):
    comparison = ProcessComparison()
    comparison.setInputs({'material': 'TI-6AL-4V', 'condition': 'annealed',
                          'finishedMass': 10.0, 'minimumWallThickness': 0.005,
                          'characteristicSize': size, 'requiredTolerance': 5.0e-4})
    print(f'{size*1000:5.0f} mm -> {comparison.selectRoute()["selected"]}')
```

---

## References

1. Gibson, I., Rosen, D. and Stucker, B., *Additive Manufacturing Technologies*, 3rd ed., Springer, 2021.
2. Gradl, P. R. et al., "Metal Additive Manufacturing in Aerospace: A Review", *Materials and Design*, Vol. 209, 2021.
3. ISO/ASTM 52900, *Additive Manufacturing: General Principles: Fundamentals and Vocabulary*.
