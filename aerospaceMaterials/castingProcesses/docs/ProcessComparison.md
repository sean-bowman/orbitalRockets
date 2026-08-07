[Home](../README.md) > Process Comparison

# Process Comparison

## Contents

- [Overview](#overview)
- [The comparison](#the-comparison)
- [The casting factor decides it](#the-casting-factor-decides-it)
- [Against machining](#against-machining)
- [Against additive](#against-additive)
- [Against forging](#against-forging)
- [When casting wins](#when-casting-wins)
- [Design rules of thumb](#design-rules-of-thumb)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Casting is the cheapest route to a complex shape and it is the only route that carries a knockdown applied to the material allowable itself. Whether that knockdown is 2.0 or 1.0 decides the whole comparison, and it is a programme decision rather than a part decision.

---

## The comparison

For a moderately complex 8 kg part in 316L:

| Route | Buy-to-fly | Allowable | Lead time | Relative cost | Tolerance |
|---|---|---|---|---|---|
| **Investment cast, qualified** | **1.6 : 1** | **1.00** | 20 wk | 1.2 | IT11 |
| Investment cast, default | 1.6 : 1 | **0.50** | 20 wk | 1.2 | IT11 |
| Sand cast | 1.8 : 1 | 0.50 to 1.00 | 12 wk | 0.5 | IT14 |
| Centrifugal cast | 2.0 : 1 | 0.50 to 1.00 | 14 wk | 0.7 | IT12 |
| **Machined from plate** | 8.0 : 1 | **1.00** | **12 wk** | 1.0 | **IT7** |
| Forged and machined | 4.0 : 1 | 1.00 | 24 wk | 1.8 | IT7 |
| **LPBF** | 1.4 : 1 | 0.85 to 1.00 | **10 wk** | 3.2 | IT8 |

---

## The casting factor decides it

**At factor 2.0 the part needs twice the material to carry the same load**, which erases the buy-to-fly advantage that was the reason to cast it.

| Factor | Allowable | Effective part mass | Verdict against machining |
|---|---|---|---|
| **2.00** | 0.50 | **2.00x** | Casting's advantage is gone |
| 1.33 | 0.752 | 1.33x | Marginal |
| **1.00** | 1.00 | **1.00x** | **Casting wins clearly** |

**The comparison is therefore not between casting and machining. It is between a qualified casting process and machining**, and if the process is not going to be qualified the trade should be made at 0.50 allowable honestly. See [CastingFactorAndQualification.md](CastingFactorAndQualification.md).

---

## Against machining

| Axis | Casting | Machining |
|---|---|---|
| **Buy-to-fly** | **1.6 : 1** | 8.0 : 1 |
| Allowable | Casting factor | **1.00** |
| **Tolerance** | IT11 | **IT7** |
| **Lead time** | 20 wk | **12 wk** |
| **Tooling** | **Required** | None |
| Complexity | **Any** | A cutter has to reach it |

**Machining wins on a single part and on tolerance**, and it loses badly on material.

**The alloy decides how badly.** An 8 : 1 buy-to-fly in aluminium is affordable; the same ratio in Inconel 718 costs eight times the material and sixteen times the machining time. That is why near net shape routes are chosen in the difficult alloys and not in aluminium.

---

## Against additive

| Axis | Investment casting | LPBF |
|---|---|---|
| Buy-to-fly | 1.6 : 1 | **1.4 : 1** |
| **Tooling** | **Required. 20 wk** | **None** |
| **Lead time** | 20 wk | **10 wk** |
| **Cost** | **1.2** | 3.2 |
| **Size** | **Large** | 400 mm |
| **Volume economics** | **Best at quantity** | Flat with quantity |
| Internal geometry | Cores, and they must come out | **Excellent** |

**They compete directly on complex geometry** and they split on quantity and size.

**Additive wins the first article** by a wide margin: no tooling, half the lead time, and a design change costs nothing.

**Casting wins production** because the tooling amortises and the per-part cost is a third of additive's.

**The common pattern is additive for development and casting for production**, and the transition is a real programme decision because the two routes have different allowables, different defect populations and separate qualifications.

---

## Against forging

| Axis | Investment casting | Closed die forging |
|---|---|---|
| **Complexity** | **Very high** | Moderate |
| Allowable | Casting factor | **1.00, with grain flow** |
| **Grain flow** | None | **Follows the contour** |
| Buy-to-fly | **1.6 : 1** | 4.0 : 1 |
| Lead time | 20 wk | **24 wk** |
| Cost | **1.2** | 1.8 |

**Forging wins on properties and casting wins on shape**, which is the oldest trade in metal forming.

**Fatigue critical parts go to forging** because the grain flow follows the load path and there is no stochastic defect population. A casting's fatigue life is governed by its worst defect, and that defect's size and location are not known.

---

## When casting wins

| Condition | Why |
|---|---|
| **Complex geometry at quantity** | The tooling amortises |
| **A qualified process** | Then it is cheapest at full allowable |
| **Larger than an additive build volume** | Additive is out |
| Expensive alloy | Buy-to-fly dominates |
| Internal passages | Cores, where they can be removed and inspected |
| **Part count reduction** | One casting replacing a weldment |

**Part count reduction is the underrated benefit.** A casting that replaces a six piece weldment removes five welds, their inspections, their knockdowns and their fit-up tolerances, and that is often worth more than the material saving.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| The casting factor decides the comparison | 2.0 erases the advantage |
| Compare against a qualified process | Or make the trade at 0.50 honestly |
| Machining for one-offs and tolerance | |
| Additive for development, casting for production | And they requalify separately |
| Forging for fatigue critical | Grain flow and no defect population |
| Part count reduction is worth more than it looks | |
| Buy-to-fly is alloy dependent | 8 : 1 in aluminium and in IN718 differ |

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-5001** | Structural design and test factors, including casting factors |
| NASA-STD-6016 | Materials and processes requirements |
| **AMS 2175** | Castings, classification and inspection |
| ISO 8062 | Casting tolerances and machining allowances |
| NASA-STD-6030 | Additive manufacturing requirements |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterialsLibrary')

from ProcessComparison import ProcessComparison

comparison = ProcessComparison()
comparison.setInputs({'material': '316L', 'condition': 'annealed', 'finishedMass': 8.0,
                      'minimumWallThickness': 0.004, 'characteristicSize': 0.200,
                      'requiredTolerance': 5.0e-4})
for entry in comparison.compareRoutes():
    print(f'{entry["route"]:32s} btf {entry["buyToFly"]:4.1f}:1  '
          f'allow {entry["allowableFactor"]:.2f}  lead {entry["leadTimeWeeks"]:3.0f} wk  '
          f'cost {entry["relativeCost"]:.1f}')
```

---

## References

1. NASA-STD-5001B, *Structural Design and Test Factors of Safety for Spaceflight Hardware*.
2. Campbell, F. C., *Manufacturing Technology for Aerospace Structural Materials*, Elsevier, 2006.
3. ASM Handbook Volume 15, *Casting*.
