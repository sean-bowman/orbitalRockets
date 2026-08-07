[Home](../README.md) > Machining Allowance

# Machining Allowance

## Contents

- [Overview](#overview)
- [Two competing requirements](#two-competing-requirements)
- [The segregated layer](#the-segregated-layer)
- [The free surface condition](#the-free-surface-condition)
- [Which binds](#which-binds)
- [The outer surface](#the-outer-surface)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The bore machining allowance decides whether the process delivers its cleanliness benefit. Leave too little and the segregated layer stays in the part, which defeats the entire reason for choosing the process.

---

## Two competing requirements

**The allowance is the larger of two independent requirements**, not their sum.

| Requirement | What it is |
|---|---|
| **Segregation** | The contaminated bore layer, which must be removed entirely |
| **Tolerance** | The dimensional stock any casting needs |

**Taking the maximum rather than the sum is correct**, because removing the segregated layer also removes the dimensional stock. They occupy the same material.

**Which one binds is the useful output**, because it says what to change. A segregation-bound allowance responds to a higher G-factor or a cleaner melt; a tolerance-bound one responds to a better mould.

---

## The segregated layer

All the inclusions that escaped to the bore accumulate there. The layer thickness follows from a mass balance:

```
depth = wallThickness * inclusionVolumeFraction * escapeFraction / packingFraction
```

**For a normal melt cleanliness this layer is thin**, a few tenths of a millimetre, because the inclusion volume fraction in a decent melt is around 0.1 percent.

**A dirty melt makes it thicker in direct proportion.** The process concentrates whatever is there, so a melt with ten times the inclusion content produces ten times the layer.

**That is worth stating plainly: centrifugal casting does not clean a melt, it relocates the contamination.** The total inclusion content is unchanged; it has simply been moved somewhere it can be machined off. A dirty melt gives a dirty casting with a thicker layer to remove.

---

## The free surface condition

**The bore is a free surface and it carries its own problems independently of the inclusions.**

| Feature | Cause |
|---|---|
| **Roughness** | A liquid free surface under a rotating field, freezing |
| **Oxide skin** | The bore is exposed to atmosphere for the whole solidification |
| **Subsurface gas porosity** | Gas rejected on freezing collects at the last liquid, which is the bore |
| Shrinkage | The last material to freeze, so it carries the shrinkage |

**This term is usually the larger of the two** and it is roughly 1.5 mm plus a fraction of the wall thickness.

**It does not depend on the melt cleanliness at all**, which means that a very clean melt does not reduce the allowance below this floor.

---

## Which binds

| Case | Binding | What to change |
|---|---|---|
| Clean melt, thick wall | **Free surface** | Nothing. This is the floor |
| Dirty melt | **Segregation** | Clean the melt |
| Thin wall, low G | Segregation, and the escape fraction is low too | Raise the G-factor |
| Tight bore tolerance | Tolerance | A better mould, or accept more stock |

**On a well run process the free surface condition binds**, and that is the sign that the segregation is being handled properly.

**A segregation-bound allowance is a melt cleanliness signal**, and it is worth acting on upstream rather than machining more off.

---

## The outer surface

**The outer surface needs far less allowance** because it takes the mould surface directly.

| Surface | Allowance |
|---|---|
| **Bore** | 1.5 to 3 mm |
| **Outer** | 1 to 2 mm, dimensional only |

**The outer surface is the sound one.** It solidified first, against the mould, under the full centrifugal pressure, and it is where the properties are best. Machining more off it than the tolerance requires is throwing away the best material in the casting.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Bore allowance | The larger of segregation and tolerance |
| Not the sum | They occupy the same material |
| Typical bore allowance | 1.5 to 3 mm |
| Outer allowance | 1 to 2 mm |
| Free surface floor | ~1.5 mm plus 2 % of the wall |
| Segregation-bound means a dirty melt | Fix it upstream |
| The process relocates contamination | It does not remove it |

---

## Failure modes

**Insufficient bore allowance.** The segregated layer stays in the part.

**Allowance taken as the sum of both terms.** Twice the machining needed.

**Dirty melt accepted because the process is clean.** It relocates rather than removes.

**Excessive outer machining.** The best material in the casting is removed.

**Allowance set from a table.** It depends on the melt, the wall and the speed.

---

## Worked numbers

From [`CentrifugalCasting.calculateMachiningAllowance`](../spinCastingLibrary/CentrifugalCasting.py):

| Casting | Segregation | Free surface | Allowance | Binding |
|---|---|---|---|---|
| 200 mm OD, 20 mm wall | small | 1.90 mm | **1.90 mm** | free surface |
| 100 mm OD, 5 mm wall | small | 1.60 mm | **1.60 mm** | free surface (segregation) |

| Quantity | 200 mm casting |
|---|---|
| As-cast bore | 156.2 mm |
| Finished bore | 160.0 mm |
| Pour mass | 38.6 kg |
| **Buy-to-fly** | **1.95 : 1** |

---

## Standards

| Standard | Scope |
|---|---|
| **ISO 8062** | Casting dimensional tolerances and machining allowances |
| ASTM A451 / A426 | Centrifugally cast pipe |
| ASTM E45 | Inclusion content of steel |

---

## Tool interface

```python
from CentrifugalCasting import CentrifugalCasting

casting = CentrifugalCasting()
casting.setInputs({'alloy': '316L', 'outerDiameter': 0.200,
                   'wallThickness': 0.020, 'length': 0.400})
casting.selectRotationalSpeed()
casting.calculateSolidification()
casting.calculateInclusionMigration(inclusionVolumeFraction = 0.0010)
result = casting.calculateMachiningAllowance()

print(result['bindingConstraint'], result['boreMachiningAllowance'])
print(result['buyToFly'])
```

---

## References

1. ISO 8062-3, *Dimensional and Geometrical Tolerances for Moulded Parts*.
2. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
3. ASTM E45, *Standard Test Methods for Determining the Inclusion Content of Steel*.
