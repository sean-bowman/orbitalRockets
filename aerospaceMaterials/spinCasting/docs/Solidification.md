[Home](../README.md) > Solidification

# Solidification

## Contents

- [Overview](#overview)
- [Chvorinov](#chvorinov)
- [The modulus of a centrifugal casting](#the-modulus-of-a-centrifugal-casting)
- [Directional structure](#directional-structure)
- [Feeding](#feeding)
- [Grain refinement](#grain-refinement)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Solidification time governs the structure, the feeding and the inclusion separation. It comes from one geometric parameter and one process constant.

---

## Chvorinov

```
t = B * (V / A)^n          n = 2
```

The volume to surface area ratio is the **casting modulus**, and it is the single geometric parameter that governs freezing time. Two castings with the same modulus freeze in the same time whatever their shape.

**The exponent of 2 means the dependence is strong.** Doubling the modulus quadruples the time.

**B is the mould constant** and it carries everything about the mould: material, coating, preheat. A sand-lined mould has roughly twice the constant of a metal one, so it freezes half as fast.

---

## The modulus of a centrifugal casting

**Heat leaves almost entirely through the outer surface into the mould.** The bore is exposed to air inside a spinning cylinder and it radiates comparatively little.

That makes the effective cooling area much smaller than the total surface area:

```
A_effective = A_outer + 0.15 * A_bore
```

**Ignoring that gives a modulus roughly half the true value and a freezing time a quarter of it**, which then propagates into a front velocity four times too high and a capture number four times too low.

**The consequence is real.** A model that treats the bore as a full cooling surface reports a process that barely cleans when in fact it cleans thoroughly.

---

## Directional structure

**The centrifugal casting freezes directionally, from the outside in**, and that is unusual and useful.

| Zone | Structure |
|---|---|
| **Chill zone, at the mould wall** | Fine equiaxed grains from rapid nucleation |
| **Columnar zone** | Grains growing inward along the thermal gradient |
| **Equiaxed zone, near the bore** | Where the gradient collapses, if the wall is thick enough |

**The columnar zone is the bulk of a typical wall** and its grains are aligned radially. That gives good properties circumferentially and hoop-wise, which is the direction a pipe or a liner is loaded.

**Directional solidification also means directional feeding.** The last liquid to freeze is at the bore, and that is where any shrinkage porosity ends up, which is convenient because the bore is machined away.

---

## Feeding

**The centrifugal field is the feeding pressure**, and that is a genuine advantage over static casting.

In a static casting, feeding relies on gravity and a riser. In a centrifugal casting the field pressurises the melt against the solidifying shell continuously, at a pressure of

```
p = rho * omega^2 * (r_outer^2 - r^2) / 2
```

**At G = 80 on a 100 mm radius that is of order a hundred kilopascals**, applied everywhere and continuously.

**No risers are needed.** That is why the casting yield is high, around 90 percent against 50 to 70 for a static casting with risers, and it is a large part of the process's economics.

---

## Grain refinement

| Mechanism | Effect |
|---|---|
| **Rapid chilling at the mould wall** | Fine chill zone |
| **Melt shearing during filling** | Breaks dendrite arms, which then act as nuclei |
| Grain refiner additions | As for any casting |
| Lower superheat | More nuclei survive |

**The shearing effect is specific to this process.** The melt is being sheared vigorously against the mould as it distributes, and that fragments growing dendrites. The fragments are carried into the bulk and become new nucleation sites.

**The result is a finer structure than a static casting of the same section**, which is another of the process's advantages and it is easy to overlook next to the cleanliness benefit.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Chvorinov exponent | 2 |
| Effective cooling area | Outer plus ~15 % of the bore |
| Sand-lined mould constant | ~2x a metal mould |
| Structure | Chill, columnar, then equiaxed if thick enough |
| Feeding | By the field, and no risers are needed |
| Casting yield | ~90 % |
| Melt shearing refines the grain | Specific to this process |

---

## Failure modes

**Bore treated as a full cooling surface.** Freezing time a quarter of the truth.

**Insufficient superheat.** The melt freezes before it distributes.

**Excessive superheat.** Coarse columnar structure and a longer cycle.

**Non-uniform mould cooling.** Directional structure skewed, and an eccentric wall.

---

## Standards

| Standard | Scope |
|---|---|
| ASTM E112 | Determining average grain size |
| ASTM E3 | Preparation of metallographic specimens |
| ASTM A451 / A426 | Centrifugally cast pipe |

---

## Tool interface

```python
from CentrifugalCasting import CentrifugalCasting, CHVORINOV_EXPONENT

for wall in (0.010, 0.020, 0.040):
    casting = CentrifugalCasting()
    casting.setInputs({'alloy': '316L', 'outerDiameter': 0.200, 'wallThickness': wall})
    casting.selectRotationalSpeed()
    result = casting.calculateSolidification()
    print(f'{wall*1000:3.0f} mm wall: modulus {result["modulus"]*1000:5.2f} mm, '
          f't_sol {result["solidificationTime"]:6.0f} s')
```

---

## References

1. Chvorinov, N., "Theory of the Solidification of Castings", *Giesserei*, Vol. 27, 1940.
2. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
3. Stefanescu, D. M., *Science and Engineering of Casting Solidification*, 3rd ed., Springer, 2015.
