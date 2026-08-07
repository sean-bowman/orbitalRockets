[Home](../README.md) > Process Comparison

# Process Comparison

## Contents

- [Overview](#overview)
- [The comparison](#the-comparison)
- [Why forming wins on material](#why-forming-wins-on-material)
- [Against machining](#against-machining)
- [Against casting](#against-casting)
- [Against additive](#against-additive)
- [When forming loses](#when-forming-loses)
- [Design rules of thumb](#design-rules-of-thumb)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Forming keeps the wrought allowable, improves the grain structure and throws away almost nothing. Its costs are tooling, tolerance and the fact that it makes a limited range of shapes.

---

## The comparison

For a large thin structural shell or dome:

| Route | Buy-to-fly | Allowable | Lead time | Cost | Tolerance |
|---|---|---|---|---|---|
| **Stretch formed** | 1.4 : 1 | **1.00** | 10 wk | 0.9 | IT12 |
| **Spun** | 1.3 : 1 | **1.00** | **8 wk** | **0.6** | IT11 |
| **Flow formed** | 1.5 : 1 | **1.00 or better** | 14 wk | 1.0 | **IT9** |
| Hydroformed | 1.3 : 1 | 1.00 | 12 wk | 0.9 | IT10 |
| Forged and machined | 4.0 : 1 | **1.00** | 24 wk | 1.8 | IT7 |
| **Machined from plate** | **10 : 1** | 1.00 | 12 wk | 1.0 | **IT7** |
| Cast | 1.6 : 1 | **0.50 to 1.00** | 20 wk | 1.2 | IT11 |
| LPBF | 1.4 : 1 | 0.85 to 1.00 | 10 wk | 3.2 | IT8 |

**Forming routes hold the allowable at a buy-to-fly close to unity**, which no other family does.

---

## Why forming wins on material

**Nothing is removed.** A formed part starts as a blank of roughly the finished surface area and it ends as the finished shape, with only trim and grip material lost.

| Route | Where the material goes |
|---|---|
| **Forming** | **Trim and grips only.** 1.1 to 1.5 : 1 |
| Machining | **Chips.** 5 to 10 : 1 |
| Casting | Risers and gates. 1.5 to 2 : 1, before machining |
| Additive | Supports and machining allowance. 1.4 : 1 |

**A machined tank dome is not a real option.** It would start as a billet the size of the dome, and the notion is absurd. That is why domes are spun or stretch formed, and it illustrates the general point: for a large thin shape, forming is the only sensible route.

**The grain flow improves rather than being cut.** A formed part's grain follows the shape, as a forging's does, where a machined part cuts through it.

---

## Against machining

| Axis | Forming | Machining |
|---|---|---|
| **Buy-to-fly** | **1.1 to 1.5 : 1** | 5 to 10 : 1 |
| Allowable | 1.00 | 1.00 |
| **Grain flow** | **Follows the shape** | Cut through |
| **Tolerance** | IT9 to IT12 | **IT7** |
| **Tooling** | **Required** | None |
| Shapes | Limited | **Any** |
| Rate | **Fast once tooled** | Slow |

**They are complementary rather than competing** on most parts. A formed part with machined features is the normal answer: form the shape, then machine the interfaces, the datums and the sealing surfaces.

**Machining wins outright on a small complex part** where the tooling cannot amortise and the shape is not formable.

---

## Against casting

| Axis | Forming | Casting |
|---|---|---|
| **Allowable** | **1.00** | **Casting factor** |
| **Defect population** | None stochastic | Stochastic |
| **Fatigue** | Predictable | Worst-defect governed |
| Complexity | **Limited** | **Very high** |
| Buy-to-fly | 1.1 to 1.5 : 1 | 1.6 : 1 |

**Forming wins on properties, casting wins on shape**, and the allowable is the sharper edge of that.

**A formed part has no stochastic defect population**, which is what makes its fatigue behaviour predictable. A casting's fatigue life is set by its largest defect, whose size and location are not known in advance, and that uncertainty is a large part of the casting factor.

---

## Against additive

| Axis | Forming | LPBF |
|---|---|---|
| **Size** | **Unlimited** | 400 mm |
| **Cost** | **0.6 to 1.0** | 3.2 |
| **Allowable** | **1.00** | 0.85 to 1.00 |
| Complexity | Limited | **Very high** |
| Tooling | Required | **None** |
| Lead time | 8 to 14 wk | **10 wk** |

**They barely overlap.** Forming makes large simple shapes cheaply at full allowable; additive makes small complex shapes expensively at a knockdown.

**Where they do meet is a small formed part with a complex feature**, and the usual resolution is to form the shape and add the feature by machining or by welding rather than to print the whole thing.

---

## When forming loses

| Condition | Better route |
|---|---|
| **Complex non-developable geometry** | Casting or additive |
| **Small quantity, expensive tooling** | Machining |
| **Very tight tolerance** | Machining or grinding |
| **Thick section** | Forging or machining |
| Internal features | Casting, additive, or machining |
| Non-formable temper only available | Machining |

**Tooling amortisation is the usual disqualifier** at low quantity. A stretch form block or a spinning mandrel is cheap as tooling goes, and a deep draw die set or a superplastic forming tool is not.

**Spinning is the low tooling exception** and it is why a one-off dome is spun rather than pressed: the mandrel is a single turned tool.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Forming keeps the allowable at buy-to-fly ~1.2 : 1 | Unique among the families |
| Grain flow improves rather than being cut | |
| Form then machine the interfaces | The normal answer |
| No stochastic defect population | Predictable fatigue |
| Spinning has the lowest tooling cost | One-off domes |
| Tooling amortisation is the usual disqualifier | |
| A large thin shape has no alternative | Forming is the route |

---

## Standards

| Standard | Scope |
|---|---|
| **MMPDS** | Wrought allowables |
| NASA-STD-5001 | Structural design and test factors |
| NASA-STD-6016 | Materials and processes requirements |
| ASTM E2218 | Determining forming limit curves |
| ISO 286 | Limits and fits, IT grades |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterialsLibrary')

from ProcessComparison import ProcessComparison

comparison = ProcessComparison()
comparison.setInputs({'material': '2219', 'condition': 't87', 'finishedMass': 25.0,
                      'minimumWallThickness': 0.003, 'characteristicSize': 1.200,
                      'requiredTolerance': 1.0e-3})
for entry in comparison.compareRoutes():
    print(f'{entry["route"]:32s} btf {entry["buyToFly"]:4.1f}:1  '
          f'allow {entry["allowableFactor"]:.2f}  cost {entry["relativeCost"]:.1f}')
```

---

## References

1. MMPDS-2023, *Metallic Materials Properties Development and Standardization*.
2. Campbell, F. C., *Manufacturing Technology for Aerospace Structural Materials*, Elsevier, 2006.
3. ASM Handbook Volume 14B, *Metalworking: Sheet Forming*.
