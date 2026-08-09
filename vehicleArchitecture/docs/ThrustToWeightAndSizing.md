[Home](../README.md) > Thrust to Weight and Sizing

# Thrust to Weight and Sizing

## Contents

- [Overview](#overview)
- [The loss budget wants more thrust than anyone buys](#the-loss-budget-wants-more-thrust-than-anyone-buys)
- [So what does set it](#so-what-does-set-it)
- [Engine count and engine-out](#engine-count-and-engine-out)
- [Throttle range](#throttle-range)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Liftoff thrust to weight is one of the first numbers chosen and it is usually justified by the ascent loss budget. That justification does not survive being computed.

---

## The loss budget wants more thrust than anyone buys

Gravity loss falls with thrust to weight, because the vehicle spends less time fighting gravity. Drag loss rises, because it is faster deeper in the atmosphere. So the total has a minimum.

The minimum is at

```
x / x0 = (G / 1.2 D)^(1 / 2.2)
```

and for a representative loss split, gravity 1250 m/s against drag 250 m/s at a reference thrust to weight of 1.35, that lands at **a thrust to weight of 2.58**.

**Nothing flies there.** Launch vehicles sit between about 1.2 and 1.5.

Drag loss starts five times smaller than gravity loss and rises more slowly than gravity loss falls, so across the entire practical range more thrust is always better for the loss budget. At 1.35 the losses are 1600 m/s, which is 302 m/s worse than the optimum, and closing that gap would take **1.9 times the liftoff thrust**.

**So the loss budget sets a floor and not a target.**

---

## So what does set it

Three things the loss budget cannot see, and they all push down.

**Engine mass.** Nearly doubling the thrust means nearly doubling the engines, and engine mass is dry mass at the bottom of the stack where the [mass chain](MassChain.md) amplification is worst. Three hundred metres per second of loss is worth a few per cent of payload; doubling the first stage engine mass is worth more.

**Engine cost.** Usually the binding one on a commercial vehicle, and entirely outside this domain.

**Structural loads.** Higher thrust to weight means higher axial acceleration, which sizes the thrust structure and the interstage, and higher dynamic pressure at a lower altitude. See [environmentsAndLoads](../../environmentsAndLoads/).

The floor at about 1.2 is real: below it gravity loss climbs steeply and an engine-out becomes unsurvivable.

---

## Engine count and engine-out

Engine count is a reliability and a granularity decision more than a thrust one.

**More engines means engine-out capability** but only if the remaining engines can still make the mission, which requires the nominal thrust to weight to exceed the floor after losing one. A nine engine first stage losing one drops to 89 per cent thrust; at a nominal 1.35 that is 1.20, exactly at the floor.

**More engines means more failure opportunities**, and whether that trade is favourable depends on whether a single engine failure is survivable. It is a step change rather than a gradient: an engine-out capable vehicle and one that is not are different vehicles, not the same vehicle with different reliability.

**Fewer, larger engines are cheaper per newton and worse at throttling**, because a single engine's throttle range is narrower than the range available from shutting some down.

None of this is computed in this domain. It is named because a thrust to weight chosen without it is chosen on the wrong criterion.

---

## Throttle range

Two constraints, at opposite ends of the flight.

**Maximum dynamic pressure** early, which is usually handled by throttling down through the transonic region rather than by structure.

**Maximum acceleration** late, when the stage is nearly empty and the same thrust produces several times the initial acceleration. A first stage at 1.35 at liftoff can reach four or five g at burnout, and either the payload or the structure sets the limit.

The second is what actually sizes the throttle range on most vehicles, and it is a consequence of the mass ratio rather than a design choice.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Reference thrust to weight | 1.35 |
| Losses at that point | 1600 m/s |
| Loss-minimising thrust to weight | 2.58 |
| Losses at the optimum | 1298 m/s |
| Penalty for flying at 1.35 | 302 m/s |
| Thrust multiple to reach the optimum | 1.9 |
| Practical floor | about 1.2 |

---

## Design rules of thumb

- **Do not justify a thrust to weight with the loss budget.** It wants 2.58.
- **Use the floor.** Below about 1.2 the gravity loss climbs steeply and engine-out stops working.
- **Check the post-failure thrust to weight**, not the nominal one, if engine-out is claimed.
- **Size the throttle range on burnout acceleration**, which is usually the binding end.
- **Price engine mass through the mass chain**, because it sits where the amplification is worst.

---

## Failure modes

**A thrust to weight optimised on losses.** Produces an answer nothing flies.

**Engine-out claimed without checking the remaining thrust to weight.** Nine minus one at 1.35 lands exactly on the floor.

**Throttle range sized on max-Q only.** Burnout acceleration is usually worse.

**Engine count chosen on thrust alone.** It is a reliability and granularity decision.

---

## Tool interface

```python
from AscentTrajectory import AscentTrajectory

ascent = AscentTrajectory()
ascent.setInputs({'thrustToWeight': 1.35, 'latitude': 28.5, 'launchAzimuth': 90.0})

losses = ascent.calculateLosses()
sweep  = ascent.optimiseThrustToWeight()

print(ascent.generateReport())
```

A thrust to weight at or below one raises rather than returning a loss budget, because the vehicle does not leave the pad and the number would look like a result.

---

## References

- [TrajectoryBasics](TrajectoryBasics.md), for the loss model and what it is not
- [MassChain](MassChain.md), for why engine mass at the bottom is expensive
- Sutton and Biblarz, *Rocket Propulsion Elements*
