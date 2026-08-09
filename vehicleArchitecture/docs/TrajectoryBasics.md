[Home](../README.md) > Trajectory Basics

# Trajectory Basics

## Contents

- [Overview](#overview)
- [The budget](#the-budget)
- [The only free term](#the-only-free-term)
- [The three losses](#the-three-losses)
- [What is not modelled, and why that matters](#what-is-not-modelled-and-why-that-matters)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The vehicle has to deliver more delta-V than the orbit needs, and the difference is loss. This document is the budget and an honest account of how little of it is computed here.

---

## The budget

```
required = orbital velocity - rotation assist + gravity + drag + steering
```

For a low Earth orbit from Cape Canaveral due east:

| Term | Value |
|---|---|
| Circular orbital velocity | 7660 m/s |
| Rotation assist | -408 m/s |
| Gravity loss | +1250 m/s |
| Drag loss | +250 m/s |
| Steering loss | +100 m/s |
| **Required** | **8852 m/s** |

That is 15.6 per cent more than the orbit itself needs, and vehicles are typically sized to around 9300 m/s to carry reserve on top.

---

## The only free term

The rotation assist is the one term in the budget that costs nothing, and it is the reason launch sites are near the equator and launches go east.

```
assist = 465 cos(latitude) sin(azimuth)
```

At the equator due east it is 465 m/s. At Cape Canaveral, 28.5 degrees, it is 408. Due south from anywhere it is zero, which is why a polar or sun-synchronous mission is more expensive than its orbital energy suggests.

**A high inclination mission pays twice**: it loses the assist and it usually flies a dogleg to clear a range, which is steering loss.

---

## The three losses

**Gravity loss** dominates and it is the integral of `g sin(gamma)` over the burn: the component of gravity fighting the velocity vector. It falls with thrust to weight, because a vehicle that accelerates harder spends less time doing it. It is the reason a launch vehicle pitches over early rather than climbing vertically.

**Drag loss** is small on a large vehicle and not on a small one, because drag scales with frontal area while mass scales with volume. A small vehicle has more area per unit mass and pays more. This is one of the few real penalties of small launch that is physics rather than economics.

**Steering loss** is the cost of thrusting off the velocity vector, whether to control the trajectory shape or to satisfy a range constraint. It is the smallest of the three and it is a trajectory design outcome rather than a vehicle property.

---

## What is not modelled, and why that matters

**No trajectory is integrated here.** There is no steering law, no atmospheric model, no vehicle aerodynamic model, and no optimiser. What this domain carries is a loss correlation anchored at a reference thrust to weight.

That has one consequence worth stating clearly. **The absolute loss total is representative rather than computed**, so every vehicle sized in this domain is sized to a delta-V that a real trajectory optimisation would move.

What survives that limitation is the **shape**: how the losses depend on thrust to weight, which is what [ThrustToWeightAndSizing](ThrustToWeightAndSizing.md) uses, and the conclusion there holds for any exponent pair where gravity loss falls faster than drag loss rises.

The loss model is registered as unvalidated with exactly that scope. See [ValidationReferences](ValidationReferences.md).

**A real ascent analysis belongs in a trajectory tool**, and pointing at one rather than half-building it here is the same decision this repository made about method-of-characteristics nozzle contours.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Orbital velocity, 400 km circular | 7660 m/s |
| Rotation assist, 28.5 degrees due east | 408 m/s |
| Rotation assist, equator due east | 465 m/s |
| Rotation assist, due south | 0 m/s |
| Total losses at a thrust to weight of 1.35 | 1600 m/s |
| Required delta-V | 8852 m/s |
| Typical sizing target with reserve | 9300 m/s |

---

## Design rules of thumb

- **Launch east and near the equator** if the mission lets you. It is the only free delta-V.
- **Budget the losses, then add reserve.** The loss model is representative, not computed.
- **Expect a small vehicle to pay more drag loss.** Area over mass is against it.
- **Do not optimise a trajectory in this domain.** Use a trajectory tool and consume its answer.
- **A high inclination mission pays twice**, in lost assist and in dogleg steering.

---

## Failure modes

**A loss budget quoted as if computed.** It is a correlation anchored at one point.

**The rotation assist taken as 465 regardless of site.** It scales with the cosine of latitude and the sine of azimuth.

**Small vehicle drag underestimated by scaling a large vehicle's budget.** The scaling is against it.

**Sizing to the loss total with no reserve.** Every term in it is soft.

---

## Tool interface

```python
from AscentTrajectory import AscentTrajectory

ascent = AscentTrajectory()
ascent.setInputs({'thrustToWeight':   1.35,
                  'latitude':         28.5,
                  'launchAzimuth':    90.0,
                  'residualVelocity': 0.0})

budget = ascent.calculateBudget()
```

---

## References

- [ThrustToWeightAndSizing](ThrustToWeightAndSizing.md), which uses the shape of this model
- Curtis, *Orbital Mechanics for Engineering Students*
- Sutton and Biblarz, *Rocket Propulsion Elements*, the flight performance chapter
