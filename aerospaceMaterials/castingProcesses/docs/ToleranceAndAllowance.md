[Home](../README.md) > Tolerance and Allowance

# Tolerance and Allowance

## Contents

- [Overview](#overview)
- [Three separate allowances](#three-separate-allowances)
- [Dimensional tolerance grades](#dimensional-tolerance-grades)
- [Machining stock](#machining-stock)
- [Pattern shrinkage](#pattern-shrinkage)
- [Draft](#draft)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Three allowances are applied to a casting and they are routinely confused. They compensate for different things, they are applied at different stages, and getting the distinction wrong produces castings that are the wrong size in ways machining cannot fix.

---

## Three separate allowances

| Allowance | Compensates for | Applied to | Removed by |
|---|---|---|---|
| **Machining stock** | Casting tolerance and surface | Casting dimensions | **Machining** |
| **Pattern shrinkage** | Solid state contraction | The pattern | **Nothing. It becomes the casting** |
| **Draft** | Pattern or die extraction | The pattern | Machining, if the surface is machined |

**Pattern shrinkage is not machined off.** The pattern is made oversize so that after the casting contracts to room temperature, it is the right size. If the allowance is wrong, every casting from that tool is the wrong size, and if it is undersize no amount of machining recovers it.

**Machining stock is machined off** and it is set by the casting's dimensional tolerance plus its surface condition.

**They are added at different points** and it is worth stating the sequence: the drawing dimension gets machining stock added to give the casting dimension, and the casting dimension gets pattern shrinkage added to give the pattern dimension.

---

## Dimensional tolerance grades

**ISO 8062 DCTG**, which is the casting analogue of ISO 286's IT grades.

| Process | DCTG | Approximate IT | Tolerance at 100 mm |
|---|---|---|---|
| **Die** | 4 | IT8 | ~0.09 mm |
| **Investment** | 6 | IT11 | ~0.4 mm |
| **Permanent mould** | 8 | IT12 | ~1.0 mm |
| **Sand** | 11 | IT14 | ~5 mm |

**The tolerance grows with the dimension**, which is why the grade rather than an absolute tolerance is the right specification.

**A DCTG 11 sand casting holds about 5 mm on a 100 mm dimension**, which means essentially every functional feature has to be machined.

---

## Machining stock

```
stock = toleranceAtSize + surfaceAllowance
```

| Process | Typical stock |
|---|---|
| Die | 0.5 mm |
| Investment | 1.5 to 2 mm |
| Permanent mould | 2 to 3 mm |
| **Sand** | **5 to 8 mm** |

**Stock is per surface**, so a dimension between two machined surfaces carries it twice.

**The stock has to exceed the tolerance**, or a casting at one end of its tolerance band will clean up and one at the other end will not. That sounds obvious and it is the commonest cause of castings that machine short.

**Downward-facing surfaces get more stock** in sand casting, because they are the cope surface and inclusions float up into them.

---

## Pattern shrinkage

**Solid state contraction from the solidus to room temperature.**

| Alloy | Linear contraction |
|---|---|
| Steel | 1.8 to 2.0 % |
| Stainless | 2.0 to 2.3 % |
| Aluminium | 1.2 to 1.5 % |
| Copper alloys | 1.5 to 2.0 % |
| Nickel alloys | 2.0 to 2.5 % |

**It is not the same as the solidification shrinkage** that the riser feeds. Solidification shrinkage is volumetric, happens during freezing, and is fed with liquid metal. Pattern shrinkage is linear, happens after freezing, and is compensated by tooling geometry.

**The effective contraction is less than the free value** where the mould restrains it, which is why pattern shrinkage is partly empirical and why foundries keep their own allowances by pattern type.

**A first article dimensional survey is how the allowance is confirmed**, and on a complex casting the tooling is usually adjusted after it.

---

## Draft

**Taper on vertical surfaces so the pattern comes out of the mould.**

| Process | Draft |
|---|---|
| **Sand** | 1 to 3 degrees |
| Investment | 0.5 to 1 degree, and sometimes zero |
| **Die** | 1 to 2 degrees, more on deep pockets |
| Permanent mould | 2 to 3 degrees |

**Investment casting can approach zero draft** because the wax pattern is melted out rather than withdrawn. That is another of its geometric advantages and it is easy to overlook.

**Draft adds mass** and on a deep feature it adds a lot. A 3 degree draft on a 100 mm deep pocket adds 5 mm to the wall at the bottom.

**Draft direction has to be consistent with the parting line**, and a feature that needs draft in two directions needs a different parting line or a core.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Three allowances, three purposes | Do not confuse them |
| Pattern shrinkage is not machined off | It becomes the casting |
| Stock must exceed the tolerance | Or some castings machine short |
| Stock is per surface | Twice for a dimension between two |
| DCTG 6 investment, DCTG 11 sand | The practical range |
| Pattern shrinkage | 1.2 % aluminium to 2.5 % nickel |
| Draft 1 to 3 degrees | Near zero for investment |
| First article dimensional survey | Confirms the allowance |

---

## Failure modes

**Pattern shrinkage confused with machining stock.** Every casting the wrong size.

**Stock less than the tolerance.** Castings that machine short.

**Stock counted once for a two-surface dimension.** One surface does not clean up.

**No draft on a sand pattern.** The mould is damaged on withdrawal.

**Draft ignored in the mass estimate.** Heavier than predicted.

**Tooling not adjusted after first article.** A known dimensional offset carried through production.

---

## Worked numbers

From [`CastingProcess.calculateMachiningAllowance`](../castingProcessesLibrary/CastingProcess.py), a 100 cm^3 stainless investment casting:

| Quantity | Value |
|---|---|
| Machining stock | 1.74 mm |
| Pattern oversize | 1.80 mm |
| Casting yield | 78 % |

---

## Standards

| Standard | Scope |
|---|---|
| **ISO 8062-3** | Casting dimensional and geometrical tolerances and machining allowances |
| ISO 286 | ISO system of limits and fits, IT grades |
| AMS 2175 | Castings, classification and inspection |
| ASTM A802 | Steel castings, surface acceptance standards |

---

## Tool interface

```python
from CastingProcess import CastingProcess, CASTING_PROCESSES

for process in ('investment', 'sand', 'die'):
    casting = CastingProcess()
    casting.setInputs({'process': process, 'alloyFamily': 'stainless',
                       'castingVolume': 1.0e-4, 'castingSurfaceArea': 0.05,
                       'characteristicSize': 0.100})
    result = casting.calculateMachiningAllowance()
    print(f'{process:16s} stock {result["machiningStock"]*1000:5.2f} mm, '
          f'pattern +{result["patternOversize"]*1000:5.2f} mm')
```

---

## References

1. ISO 8062-3, *Geometrical Product Specifications: Dimensional and Geometrical Tolerances for Moulded Parts*.
2. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
3. ASM Handbook Volume 15, *Casting*.
