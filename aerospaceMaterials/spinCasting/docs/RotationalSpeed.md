[Home](../README.md) > Rotational Speed

# Rotational Speed

## Contents

- [Overview](#overview)
- [The G-factor](#the-g-factor)
- [Selecting the speed](#selecting-the-speed)
- [The window](#the-window)
- [The bore sees less](#the-bore-sees-less)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Rotational speed is the single governing process parameter, and the window is narrow at both ends for different reasons.

---

## The G-factor

Speed is never specified directly, because a speed that is right for a 100 mm mould is wrong for a 400 mm one. What is specified is the centrifugal acceleration at the outer wall, as a multiple of gravity.

```
G = omega^2 * r / g
```

Inverting for the speed in revolutions per minute:

```
N = (30 / pi) * sqrt(G * g / r)
```

**The speed falls as the square root of radius**, so a large mould spins slower than a small one for the same G-factor. A 100 mm radius at G = 80 needs 846 rev/min; a 400 mm radius needs 423.

---

## Selecting the speed

**Specify the G-factor at the outer radius**, because that is where the metal has to be pinned against the mould.

| Target | Use |
|---|---|
| 60 to 80 | General. The safe middle |
| 80 to 100 | Where cleanliness matters most |
| Above 100 | Thin walls, and it approaches the banding limit |
| Below 60 | Only where the wall is thick and the alloy freezes slowly |

**Higher G is better for segregation** because the Stokes velocity scales with it directly, so more inclusions escape before the front catches them.

**Higher G is worse for feeding.** The melt is pinned so hard against the mould that it cannot move to feed the solidification shrinkage, which produces longitudinal tearing.

**The two considerations pull in opposite directions**, and the 60 to 100 preferred window is where they balance.

---

## The window

| G-factor | Regime | Symptom |
|---|---|---|
| **Below 40** | Too low | The melt rains at top of arc. Thick bottom, thin top, entrapped defects |
| 40 to 60 | Acceptable | |
| **60 to 100** | **Preferred** | |
| 100 to 150 | Acceptable | |
| **Above 150** | Too high | Banding, longitudinal tearing, mould coating thrown |

**The raining failure is the classic under-speed symptom.** At the top of the arc the melt is being held up by the centrifugal field against gravity. If the field is not strong enough, the melt detaches, falls through the bore, and lands on the bottom. The result is a casting that is thick at the bottom, thin at the top, and full of entrapped oxide from the falling metal.

**A G-factor of 1 is exactly the point at which the melt is weightless at top of arc**, and 40 is the practical minimum with margin for the melt's own strength and surface tension.

**The banding failure at high G** is longitudinal segregation bands, caused by the melt being unable to feed and by unsteady front motion. It is discussed in [Defects.md](Defects.md).

---

## The bore sees less

**The field grows with radius**, so the bore always sees a lower G-factor than the outer wall.

```
G_bore / G_outer = r_bore / r_outer
```

**On a thick walled casting the difference is large.** A 200 mm OD with a 40 mm wall has a bore radius of 60 mm against an outer radius of 100 mm, so the bore sees 60 percent of the outer G-factor.

**That matters for the segregation calculation**, because the Stokes velocity is evaluated across the whole wall and it falls as the inclusion approaches the bore. The migration slows down exactly where the inclusions are heading.

**It also matters for the raining criterion**, which applies at the free surface, meaning at the bore. A casting whose outer wall sees G = 45 may have a bore at G = 27 and rain anyway.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Specify G at the outer radius | Not the speed |
| Preferred window | 60 to 100 |
| Absolute minimum | 40 |
| Absolute maximum | 150 |
| Speed falls as sqrt(radius) | Large moulds spin slower |
| Bore G-factor | Outer G times the radius ratio |
| Check the bore against the raining limit | It is the free surface |

---

## Failure modes

**Below 40 G.** The melt rains at top of arc.

**Above 150 G.** Banding and longitudinal tearing.

**G specified at the bore rather than the outer wall.** The outer wall is over-speeded.

**Speed reused from a different mould size.** The G-factor is wrong by the radius ratio.

**Bore G-factor not checked on a thick wall.** It rains despite an acceptable outer figure.

---

## Worked numbers

From [`CentrifugalCasting`](../spinCastingLibrary/CentrifugalCasting.py):

| OD | Wall | Target G | Speed | Bore G | Regime |
|---|---|---|---|---|---|
| 200 mm | 20 mm | 80 | **846 rev/min** | 64 | preferred |
| 200 mm | 40 mm | 80 | 846 rev/min | **48** | preferred, bore marginal |
| 100 mm | 10 mm | 80 | 1196 rev/min | 64 | preferred |
| 200 mm | 20 mm | 20 | 423 rev/min | 16 | **too low** |
| 200 mm | 20 mm | 300 | 1638 rev/min | 240 | **too high** |

---

## Standards

| Standard | Scope |
|---|---|
| ASTM A451 / A426 | Centrifugally cast pipe |
| ASTM B505 | Copper alloy continuous castings |
| ISO 8062 | Casting tolerances |

---

## Tool interface

```python
from CentrifugalCasting import CentrifugalCasting, G_FACTOR_WINDOW

for target in (20.0, 80.0, 300.0):
    casting = CentrifugalCasting()
    casting.setInputs({'alloy': '316L', 'outerDiameter': 0.200, 'wallThickness': 0.020})
    casting.selectRotationalSpeed(targetGFactor = target)
    result = casting.calculateGFactor()
    print(f'G={target:5.0f}: {casting.rotationalSpeed:6.0f} rpm, '
          f'bore G={result["boreGFactor"]:5.0f}, {result["regime"]}')
```

---

## References

1. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
2. Janco, N., *Centrifugal Casting*, American Foundrymen's Society, 1988.
3. ASM Handbook Volume 15, *Casting*.
