[Home](../README.md) > Solidification and Segregation

# Solidification and Segregation

## Contents

- [Overview](#overview)
- [The competition](#the-competition)
- [Stokes velocity in a centrifugal field](#stokes-velocity-in-a-centrifugal-field)
- [The solidification front](#the-solidification-front)
- [The capture number](#the-capture-number)
- [Where the model went wrong first](#where-the-model-went-wrong-first)
- [The segregated layer](#the-segregated-layer)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The cleanliness of a centrifugal casting is the whole reason to choose the process, and it comes from one competition: inclusions migrating inward against a solidification front advancing inward behind them.

---

## The competition

**Two velocities, both pointing inward, and the ratio decides everything.**

| Velocity | What it is |
|---|---|
| **Stokes velocity** | How fast an inclusion migrates to the bore |
| **Front velocity** | How fast the solidification front sweeps the wall |

**An inclusion escapes if it reaches the bore before the front reaches it.** That is the whole physics, and it is a race rather than a distance calculation.

---

## Stokes velocity in a centrifugal field

In a gravitational field a particle settles at the Stokes velocity. In a centrifugal field the same balance holds with `g` replaced by `omega^2 r`:

```
v = d^2 * (rho_melt - rho_inclusion) * omega^2 * r / (18 * mu)
```

**The inclusion is less dense than the melt**, so the density difference is positive and the particle migrates **inward**, towards the bore.

**Three strong dependencies:**

| Parameter | Dependence | Consequence |
|---|---|---|
| **Particle diameter** | `d^2` | A 200 um slag particle separates 16 times faster than a 50 um oxide |
| **G-factor** | linear | Doubling the speed quadruples the velocity, since G goes as omega^2 |
| **Viscosity** | inverse | Higher superheat means lower viscosity means faster separation |

**Fine oxides set the requirement.** Coarse slag separates almost instantly and was never the problem; a 20 um alumina particle is what decides whether the process is clean.

---

## The solidification front

The front advances inward from the mould wall, sweeping the wall thickness over the solidification time:

```
v_front = wallThickness / t_solidification
```

with the solidification time from Chvorinov. See [Solidification.md](Solidification.md).

**The front is slow.** For a 20 mm wall freezing in 542 seconds it advances at 0.037 mm/s, which is four orders of magnitude slower than a typical Stokes velocity.

**That asymmetry is the process.**

---

## The capture number

```
captureNumber = v_stokes / v_front
```

| Capture number | Meaning |
|---|---|
| **Well above 100** | Essentially every inclusion escapes. The process is doing its job |
| 3 to 100 | Most escape |
| **Below 3** | The front outruns them. The cleaning benefit is largely lost |

**A low capture number means the process has bought nothing.** The casting is still a casting and its inclusion content is what a static casting's would be.

**What raises it:**

| Change | Effect |
|---|---|
| Higher G-factor | Direct, and it is the primary control |
| Thicker section | Slows the front, since the time goes as the modulus squared |
| More superheat | Lower viscosity, faster migration |
| Cleaner melt | Fewer inclusions to start with, which is the real answer |

**A thin section is the hard case.** It freezes fast, the front is quick, and the capture number falls. That is why a thin centrifugal casting is less clean than a thick one at the same speed.

---

## Where the model went wrong first

**Worth recording, because the wrong version is intuitive and it produces nonsense.**

The obvious approach is to integrate the Stokes velocity over the solidification time and call the result the migration distance:

```
distance = v_stokes * t_solidification     # WRONG
```

For the example above that gives 46 mm/s times 271 s, which is **12 metres**. The wall is 20 mm.

**The distance saturates at the wall thickness for every inclusion type**, so the model reports "machine the whole wall away" regardless of the inputs and the calculation is useless.

**The error is treating it as a distance problem when it is a race.** A free particle does cross the wall in under a second; what matters is whether the front got there first, and that is a ratio of velocities.

**The segregated layer then follows from a mass balance rather than from kinematics.**

---

## The segregated layer

All the escaped inclusions accumulate in a thin layer at the bore. Its thickness follows from the inclusion volume fraction and how densely the escaped material packs:

```
segregatedDepth = wallThickness * inclusionVolumeFraction * escapeFraction / packingFraction
```

**That layer is thin**, typically a few tenths of a millimetre for a normal melt cleanliness.

**It is usually not what governs the machining allowance.** The bore is also a free surface, so it carries roughness, oxide skin and subsurface gas porosity independently of the inclusion content, and that free surface condition is the larger of the two terms.

Both are computed and the larger is taken. See [MachiningAllowance.md](MachiningAllowance.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| It is a race, not a distance | Capture number, not migration length |
| Capture number above 100 | Essentially complete separation |
| Capture number below 3 | The benefit is largely lost |
| Stokes velocity | `d^2`, so fine oxides govern |
| Thin sections are the hard case | The front is fast |
| Higher G is the primary control | Velocity scales with it |
| The segregated layer is thin | The free surface usually governs |

---

## Failure modes

**Thin section spun at a speed suited to a thick one.** The front wins.

**Migration treated as a distance.** The answer is metres and it means nothing.

**Bore allowance set from the inclusion layer alone.** The free surface condition is larger.

**Dirty melt.** The process concentrates the inclusions and there are more of them.

---

## Worked numbers

From [`CentrifugalCasting.calculateInclusionMigration`](../spinCastingLibrary/CentrifugalCasting.py), 316L at 846 rev/min, 20 mm wall:

| Inclusion | d [um] | v_stokes [mm/s] | v_front [mm/s] | Capture | Escape |
|---|---|---|---|---|---|
| **Alumina** | 50 | 46.0 | 0.037 | **1248** | 100 % |
| Silica | 80 | 168.0 | 0.037 | 4557 | 100 % |
| Slag | 200 | 1013.9 | 0.037 | 27496 | 100 % |
| Gas porosity | 300 | 3799.2 | 0.037 | 103038 | 100 % |

**Even the finest inclusion in the table has a capture number above a thousand.** For a 5 mm wall on a 100 mm OD the same alumina gives a capture number of 357, still ample.

---

## Standards

| Standard | Scope |
|---|---|
| ASTM E45 | Determining the inclusion content of steel |
| ASTM E1245 | Determining inclusion content by automatic image analysis |
| ASTM A451 / A426 | Centrifugally cast pipe |

---

## Tool interface

```python
from CentrifugalCasting import CentrifugalCasting, INCLUSION_TYPES

for inclusion in INCLUSION_TYPES:
    casting = CentrifugalCasting()
    casting.setInputs({'alloy': '316L', 'inclusionType': inclusion})
    casting.selectRotationalSpeed()
    casting.calculateSolidification()
    result = casting.calculateInclusionMigration()
    print(f'{inclusion:14s} capture {result["captureNumber"]:8.0f}, '
          f'escape {result["escapeFraction"]*100:5.1f} %')
```

---

## References

1. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
2. Chirita, G. et al., "Sensitivity of Different Al-Si Alloys to Centrifugal Casting Effect", *Materials and Design*, Vol. 31, 2010.
3. Stefanescu, D. M., *Science and Engineering of Casting Solidification*, 3rd ed., Springer, 2015.
