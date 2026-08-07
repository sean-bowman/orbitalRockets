[Home](../README.md) > Process Comparison

# Process Comparison

## Contents

- [Overview](#overview)
- [The comparison](#the-comparison)
- [Where machining wins](#where-machining-wins)
- [Where it loses](#where-it-loses)
- [The alloy dependence](#the-alloy-dependence)
- [Design rules of thumb](#design-rules-of-thumb)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Machining is the route every other route is compared against. It needs no tooling, it holds the best tolerances, it has the shortest lead time, and it throws away most of the material it starts with.

---

## The comparison

For a moderately complex 8 kg part in 316L:

| Route | Buy-to-fly | Allowable | Lead time | Relative cost | Tolerance |
|---|---|---|---|---|---|
| **Machined from plate** | **8.0 : 1** | **Full wrought** | **12 wk** | 1.0 | **IT7** |
| Closed die forged and machined | 4.0 : 1 | Full wrought | 24 wk | 1.8 | IT7 |
| Ring rolled and machined | 3.0 : 1 | Full wrought | 18 wk | 1.4 | IT9 |
| Investment cast and machined | 1.6 : 1 | Casting factor | 20 wk | 1.2 | IT11 |
| Centrifugal cast and machined | 2.0 : 1 | Casting factor | 14 wk | 0.7 | IT12 |
| LPBF and machined | 1.4 : 1 | Build direction | 10 wk | 3.2 | IT8 |

**Machining wins on lead time and allowable together**, and nothing else offers both.

**It loses badly on buy-to-fly**, and that is its only real weakness.

---

## Where machining wins

| Condition | Why |
|---|---|
| **One-off or low quantity** | No tooling to amortise |
| **Short lead time** | Stock to part in days |
| **Full wrought allowable** | No knockdown of any kind |
| **Tight tolerance** | IT7 routinely, IT5 by grinding |
| Design changes expected | A program change, not a tool change |
| Cheap material | The buy-to-fly does not hurt |

**Machining is always available as the fallback**, which has a value that does not appear in a cost table. Every other route needs tooling, a qualification, or a supplier; machining needs stock and a program.

**Development hardware is machined almost by default** for exactly that reason, and the route is often revisited only when the quantity justifies tooling.

---

## Where it loses

| Condition | Why |
|---|---|
| **Expensive alloy** | 8 : 1 on titanium or Inconel is a very large bill |
| **Difficult alloy** | 16x the machining time as well |
| **Complex internal geometry** | A cutter has to reach it |
| **Large thin structure** | Distortion and deflection |
| Quantity | Tooling amortises for the alternatives |

**The two penalties compound on the difficult alloys**, and that is the important point. Inconel 718 has both a high material cost and a machinability index of 12, so an 8 : 1 buy-to-fly means paying for eight times the material and spending sixteen times as long removing seven eighths of it.

**That compounding is why near net shape routes are chosen in titanium and nickel and not in aluminium.** The same buy-to-fly ratio has a completely different consequence.

---

## The alloy dependence

| Alloy | Relative material cost | Machinability | Combined penalty of 8:1 |
|---|---|---|---|
| **6061-T6** | 0.4 | 190 | Low |
| 316L | 1.0 | 45 | Moderate |
| TI-6AL-4V | 8.5 | 22 | **High** |
| **INCONEL 718** | 6.0 | **12** | **Very high** |

**Buy-to-fly is not a single figure of merit**, and treating it as one is the commonest error in process selection. An 8 : 1 aluminium part and an 8 : 1 Inconel part are different decisions entirely.

**The right framing is total cost**, which [`ProcessComparison`](../../aerospaceMaterialsLibrary/ProcessComparison.py) computes across the routes with the material cost index, the machinability and the allowable knockdown all in place.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Machining buy-to-fly | 5 to 10 : 1 |
| No tooling, no knockdown, shortest lead | Its three advantages |
| Buy-to-fly penalty compounds with machinability | On the difficult alloys |
| Near net shape competes hardest in Ti and Ni | And barely at all in aluminium |
| Always available as a fallback | Which has real value |
| IT7 routinely, IT5 by grinding | The best tolerances available |

---

## Standards

| Standard | Scope |
|---|---|
| ISO 286 | Limits and fits, IT grades |
| NASA-STD-5001 | Structural design and test factors, including casting factors |
| NASA-STD-6016 | Materials and processes requirements |
| SAE ARP4915 | Aerospace machining practices |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterialsLibrary')

from ProcessComparison import ProcessComparison

for material, condition in (('6061', 't6'), ('316L', 'annealed'),
                            ('TI-6AL-4V', 'annealed'), ('INCONEL 718', 'sta')):
    comparison = ProcessComparison()
    comparison.setInputs({'material': material, 'condition': condition, 'finishedMass': 8.0,
                          'minimumWallThickness': 0.005, 'characteristicSize': 0.200,
                          'requiredTolerance': 1.0e-4})
    best = comparison.selectRoute()
    print(f'{material:14s} best route: {best["selected"]}')
```

---

## References

1. Campbell, F. C., *Manufacturing Technology for Aerospace Structural Materials*, Elsevier, 2006.
2. ASM Handbook Volume 16, *Machining*.
3. NASA-STD-6016B, *Standard Materials and Processes Requirements for Spacecraft*.
