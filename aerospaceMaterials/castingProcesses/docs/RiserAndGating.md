[Home](../README.md) > Riser and Gating

# Riser and Gating

## Contents

- [Overview](#overview)
- [Two independent riser conditions](#two-independent-riser-conditions)
- [The timing condition](#the-timing-condition)
- [The volume condition](#the-volume-condition)
- [Which binds, and what to do](#which-binds-and-what-to-do)
- [Gating](#gating)
- [Casting yield](#casting-yield)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A riser is a reservoir of liquid metal that feeds the casting as it shrinks. It has to satisfy two conditions simultaneously, and they are independent: it has to still be liquid when the casting has finished freezing, and it has to contain enough metal.

A riser that satisfies one and not the other does not work, and the two failures look different.

---

## Two independent riser conditions

| Condition | Requirement | Failure mode |
|---|---|---|
| **Timing** | `M_riser >= 1.2 M_casting` | Centreline shrinkage in the heavy section |
| **Volume** | `V_riser * efficiency >= shrinkage * V_casting` | Cavity under the riser neck |

**Both have to hold.** Sizing on one alone is the commonest riser design error.

---

## The timing condition

**The riser must freeze after the casting it feeds.**

If it freezes first, it stops feeding while the casting is still shrinking, and the shrinkage cavity forms in the part instead of in the riser. That is exactly the outcome the riser exists to prevent.

```
M_riser >= 1.2 * M_casting
```

**The 1.2 factor is the conventional margin.** It accounts for the riser losing heat to the mould on more sides than the analysis assumes and for the uncertainty in the modulus calculation.

**For a cylindrical riser of height equal to its diameter, `M = D/6`**, so the required diameter follows directly:

```
D_riser = 6 * 1.2 * M_casting
```

**Insulating and exothermic sleeves change the calculation** by effectively raising the riser modulus without raising its volume. That is why they are used: they let a smaller riser satisfy the timing condition, which improves the yield.

---

## The volume condition

**The riser must contain enough liquid to make up the solidification shrinkage.**

```
V_riser * feedingEfficiency >= shrinkage * V_casting
```

**Feeding efficiency is about 14 percent** for a plain cylindrical riser. A riser does not deliver all its volume: its own solidification front closes it off long before it is empty, and the pipe that forms in the top is the visible evidence.

**Insulating sleeves raise the efficiency** as well as the modulus, to perhaps 25 percent, because the riser stays liquid longer and feeds for more of its volume.

**Aluminium is the hard case** at 6.5 percent shrinkage, needing roughly twice the riser volume of steel for the same casting.

---

## Which binds, and what to do

**The binding condition says what to change**, and that is the useful output.

| Binding | Meaning | Fix |
|---|---|---|
| **Timing** | The riser is not staying liquid long enough | Make it **fatter**. Or use an insulating sleeve |
| **Volume** | It is freezing late enough and running out of metal | Make it **taller**, or use more than one |

**Making a volume-bound riser fatter is the wrong fix** and it is the intuitive one. Adding diameter raises the modulus, which was already adequate, while adding relatively little usable volume because the efficiency is low.

**Making a timing-bound riser taller is equally wrong.** Height adds volume without much modulus, because the modulus of a tall cylinder is dominated by its diameter.

---

## Gating

The runner system that gets metal from the pour cup into the cavity.

| Element | Role |
|---|---|
| **Sprue** | The vertical downrunner. Tapered, to stay full |
| **Runner** | Horizontal distribution |
| **Ingate** | Entry into the cavity |
| Well, filters, traps | Reduce turbulence and catch inclusions |

**Gating ratios** describe the relative cross sections, written sprue : runner : ingate.

| Ratio | Type | Behaviour |
|---|---|---|
| **1 : 2 : 4** | Unpressurised | Slow, low turbulence. **The aerospace choice** |
| 1 : 1 : 1 | Pressurised | Fast, turbulent, and the system stays full |
| 4 : 3 : 2 | Strongly pressurised | Very turbulent |

**Turbulence is the enemy.** A turbulent fill entrains air and folds the oxide film on the metal surface into the bulk, creating bifilms that act as cracks. That is Campbell's central argument and it is why unpressurised gating is standard for quality castings.

**A tapered sprue stays full** and therefore does not aspirate air. A parallel sprue runs partly empty and draws air in, which is one of the easiest defects to design out.

---

## Casting yield

```
yield = V_casting / (V_casting + V_risers + V_gating)
```

| Alloy | Typical yield |
|---|---|
| Steel | 60 to 75 % |
| **Aluminium** | **45 to 60 %** |
| Investment cast, small parts | 30 to 50 % |

**Aluminium's low yield follows directly from its shrinkage.** More shrinkage means more riser volume means less of the poured metal in the part.

**Yield is a real cost** and it is a large part of why casting cost is not simply the part mass times the alloy price. On an expensive alloy a 50 percent yield doubles the material cost.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Riser modulus | >= 1.2 x casting modulus |
| Riser feeding efficiency | ~14 %, or ~25 % with a sleeve |
| Timing bound | Make it fatter |
| Volume bound | Make it taller, or add another |
| Gating ratio | 1 : 2 : 4 unpressurised |
| Tapered sprue | Or it aspirates air |
| Casting yield | 45 to 75 % |

---

## Failure modes

**Riser modulus below 1.2x.** It freezes first; shrinkage in the part.

**Volume-bound riser made fatter.** More modulus, still not enough metal.

**Turbulent fill.** Entrained air and folded oxide bifilms.

**Parallel sprue.** Aspirated air throughout the fill.

**Aluminium risered like steel.** Half the volume needed.

**Yield ignored in the cost estimate.** Material cost doubled.

---

## Worked numbers

From [`CastingProcess.sizeRiser`](../castingProcessesLibrary/CastingProcess.py):

| Casting | Modulus | Riser D | Binding | Yield |
|---|---|---|---|---|
| 100 cm^3 stainless, investment | 2.00 mm | 14.4 mm | **volume** | 78 % |
| 1000 cm^3 aluminium, sand | larger | larger | volume | lower |
| 1000 cm^3 steel, sand | larger | larger | timing | higher |

**Aluminium yields worse than steel for the same casting**, directly from the shrinkage difference.

---

## Standards

| Standard | Scope |
|---|---|
| AMS 2175 | Castings, classification and inspection |
| ISO 8062 | Casting tolerances and machining allowances |
| ASTM E446 / E186 / E280 | Reference radiographs |

---

## Tool interface

```python
from CastingProcess import CastingProcess, RISER_MODULUS_RATIO

for family in ('steel', 'aluminium'):
    casting = CastingProcess()
    casting.setInputs({'process': 'sand', 'alloyFamily': family,
                       'castingVolume': 1.0e-3, 'castingSurfaceArea': 0.15})
    casting.calculateSolidification()
    result = casting.sizeRiser()
    print(f'{family:10s} riser {result["riserVolume"]*1e6:7.1f} cm^3, '
          f'binding {result["bindingCondition"]:6s}, yield {result["castingYield"]*100:.0f} %')
```

---

## References

1. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
2. Wlodawer, R., *Directional Solidification of Steel Castings*, Pergamon, 1966.
3. ASM Handbook Volume 15, *Casting*.
