[Home](../README.md) > Process Comparison

# Process Comparison

## Contents

- [Overview](#overview)
- [The comparison](#the-comparison)
- [Against machining from plate](#against-machining-from-plate)
- [Against forging](#against-forging)
- [Against additive](#against-additive)
- [When centrifugal wins](#when-centrifugal-wins)
- [Design rules of thumb](#design-rules-of-thumb)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Centrifugal casting competes with a small set of processes for a specific class of part: hollow bodies of revolution. Against each competitor it wins on a different axis.

---

## The comparison

For a 200 mm diameter, 400 mm long ring or liner:

| Route | Buy-to-fly | Allowable | Lead time | Relative cost | Tolerance |
|---|---|---|---|---|---|
| **Centrifugal cast** | 2.0 : 1 | **casting factor** | 14 wk | 0.7 | IT12 |
| Ring rolled and machined | 3.0 : 1 | full wrought | 18 wk | 1.4 | IT9 |
| Machined from plate | 8.0 : 1 | full wrought | 12 wk | 1.0 | IT7 |
| Closed die forged | 4.0 : 1 | full wrought | 24 wk | 1.8 | IT7 |
| Flow formed | 2.5 : 1 | full wrought | 14 wk | 1.0 | IT9 |
| **LPBF** | 1.4 : 1 | build direction | 10 wk | 3.2 | IT8 |

**The casting factor is the discriminator** and it dominates the comparison. At an unqualified factor of 2.0 the allowable is halved and the part needs twice the material, which wipes out the buy-to-fly advantage entirely.

**At a qualified factor of 1.0 the comparison inverts** and centrifugal casting is the cheapest route with a full allowable. That is the trade the process turns on, and it is a programme investment rather than a part decision. See [castingProcesses CastingFactorAndQualification.md](../../castingProcesses/docs/CastingFactorAndQualification.md).

---

## Against machining from plate

| Axis | Centrifugal | Machining |
|---|---|---|
| **Buy-to-fly** | **2 : 1** | 8 : 1 |
| Allowable | Casting factor | Full wrought |
| Tolerance | IT12 | IT7 |
| Lead time | 14 wk | 12 wk |
| **Setup cost** | Mould | None |

**Machining wins on a single part and loses badly at quantity**, because the buy-to-fly is four times worse and there is no tooling to amortise against.

**On an expensive alloy the buy-to-fly dominates everything.** Eight to one on Ti-6Al-4V at 8.5 times the 316L cost index is a very large number, and it is why the comparison is different for every alloy.

---

## Against forging

| Axis | Centrifugal | Ring rolled |
|---|---|---|
| Buy-to-fly | 2 : 1 | 3 : 1 |
| **Allowable** | Casting factor | **Full wrought** |
| **Grain flow** | Radial columnar | **Circumferential** |
| Lead time | 14 wk | 18 wk |
| Cost | 0.7 | 1.4 |

**Ring rolling gives circumferential grain flow**, which is the loaded direction for a ring or a flange, and it gives the full wrought allowable. That is a real advantage and it is why ring rolling is the default for a highly loaded ring.

**Centrifugal casting is cheaper and faster** and it carries the casting factor. For a moderately loaded liner or bushing that trade favours casting; for a highly loaded structural ring it does not.

---

## Against additive

| Axis | Centrifugal | LPBF |
|---|---|---|
| **Buy-to-fly** | 2 : 1 | **1.4 : 1** |
| Allowable | Casting factor | Build direction knockdown |
| **Size** | **Metres** | 400 mm |
| **Cost** | **0.7** | 3.2 |
| Lead time | 14 wk | 10 wk |
| Complexity | Axisymmetric only | Almost anything |

**They barely compete.** Additive wins on complexity and on lead time; centrifugal wins on size and on cost by a factor of four.

**The overlap is a small, simple, hollow, expensive-alloy part**, and there additive's shorter lead time often decides it for a development article while centrifugal decides it for production.

---

## When centrifugal wins

| Condition | Why |
|---|---|
| **Hollow body of revolution** | The process's natural shape |
| **Moderate loading** | The casting factor is affordable |
| **Larger than an additive build volume** | Additive is out |
| **Quantity** | The mould amortises |
| **Expensive alloy** | Buy-to-fly dominates |
| Bimetallic | Almost nothing else does it |
| The bore is machined anyway | The segregated layer costs nothing extra |

**The last one is the quiet advantage.** For a bushing, a liner or a bearing, the bore is a finished functional surface and it was always going to be machined. The machining allowance the segregation demands is therefore free.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| The casting factor dominates the comparison | 2.0 unqualified halves the allowable |
| Qualified, centrifugal is the cheapest route | With a full allowable |
| Ring rolling for highly loaded rings | Circumferential grain flow |
| Machining for one-offs | No tooling |
| Additive for complexity | Not for size or cost |
| Buy-to-fly dominates on expensive alloys | |
| Free allowance where the bore is machined anyway | |

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-5001** | Structural design and test factors, including casting factors |
| NASA-STD-6016 | Materials and processes requirements |
| ISO 8062 | Casting tolerances and machining allowances |
| ISO 286 | Tolerance grades |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterialsLibrary')

from ProcessComparison import ProcessComparison

comparison = ProcessComparison()
comparison.setInputs({'material': '316L', 'condition': 'annealed', 'finishedMass': 8.0,
                      'minimumWallThickness': 0.015, 'characteristicSize': 0.200,
                      'requiredTolerance': 1.0e-3})
for entry in comparison.compareRoutes():
    print(f'{entry["route"]:32s} {entry["buyToFly"]:.1f}:1  '
          f'allow {entry["allowableFactor"]:.2f}  cost {entry["relativeCost"]:.1f}')
```

---

## References

1. NASA-STD-5001B, *Structural Design and Test Factors of Safety for Spaceflight Hardware*.
2. Campbell, F. C., *Manufacturing Technology for Aerospace Structural Materials*, Elsevier, 2006.
3. ASM Handbook Volume 15, *Casting*.
