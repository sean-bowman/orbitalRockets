[Home](../README.md) > Guidance Algorithms

# Guidance Algorithms

## Contents

- [Overview](#overview)
- [Guidance against control](#guidance-against-control)
- [The ascent in phases](#the-ascent-in-phases)
- [Open loop against closed loop](#open-loop-against-closed-loop)
- [Abort logic and mode management](#abort-logic-and-mode-management)
- [Why none of this is computed here](#why-none-of-this-is-computed-here)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Guidance decides where to point. Control makes the vehicle point there. Conflating them is the commonest confusion from outside the discipline and it matters because they fail differently.

---

## Guidance against control

**Guidance is a trajectory problem.** It runs slowly, it looks ahead, and its failure mode is arriving in the wrong orbit.

**Control is a stability problem.** It runs fast, it looks at now, and its failure mode is tumbling.

They are separated by an order of magnitude or more in bandwidth, which is what makes the separation valid: guidance can treat the vehicle as though it points where it is told, and control can treat the commanded direction as constant.

**A guidance failure is recoverable and a control failure is not**, which is why the two get different reliability treatment.

---

## The ascent in phases

**Vertical rise** clears the tower with no manoeuvring, because the margin for error near the ground is zero.

**Pitch over** starts the turn, and it is a small deliberate manoeuvre that sets up everything after it.

**Gravity turn** follows: the vehicle flies at near zero angle of attack and gravity does the turning. **That is the aerodynamically cheap way to do it** and it is why the trajectory looks the way it does. It is not an optimisation, it is a constraint: any significant angle of attack at dynamic pressure is a structural load case and a [control authority](ActuationAndTVC.md) problem.

**Closed loop guidance** takes over once the atmosphere is thin enough that angle of attack is free, and steers to the target orbit directly.

**The handover between the last two is the interesting moment**, because it is where the vehicle stops flying a shape and starts flying to a target, and any dispersion accumulated in the first part has to be absorbed by the second.

---

## Open loop against closed loop

**Open loop** flies a pre-computed attitude profile against time. Simple, predictable, and it cannot correct anything: a dispersion in thrust, mass or atmosphere flies straight through into the injection.

**Closed loop** computes the steering from the current state to the target every cycle. It absorbs dispersions, and it needs a good navigation solution to do it, which is why [SensorsAndNavigation](SensorsAndNavigation.md) is upstream of this.

Almost every vehicle is open loop in the atmosphere, because the gravity turn constraint means there is nothing to optimise, and closed loop above it.

---

## Abort logic and mode management

Mode management is the part that is easy to underestimate: the vehicle has a set of states, transitions between them, and conditions that trigger the transitions, and **most of the flight software's complexity lives there rather than in the algorithms.**

**An abort decision is a one-way door made in milliseconds on incomplete information.** The design questions are what triggers it, whether it is automatic or commanded, and what the vehicle does afterwards, and each is a mission decision rather than an avionics one.

For an uncrewed vehicle the abort usually resolves to flight termination, which belongs to [rangeSafetyAndFTS](../../rangeSafetyAndFTS/) and carries the most stringent reliability requirement on the vehicle.

---

## Why none of this is computed here

Stated plainly because the domain was scaffolded documentation-first and this is the clearest case for it.

**Ascent guidance optimises a delta-V budget that [vehicleArchitecture](../../vehicleArchitecture/) already owns.** That domain computes the losses, the required delta-V and the payload sensitivity, and a guidance implementation here would be optimising against numbers computed there while producing its own version of them.

**The trajectory work overlaps material that already exists**, which is what the domain objectives said at the outset.

**And a guidance law without a trajectory simulation is a formula rather than a result.** Implementing one would produce something that looked like an answer and could not be flown or checked.

So this domain computes the [navigation solution](SensorsAndNavigation.md) that guidance consumes and the [control authority](ActuationAndTVC.md) that limits it, and documents the algorithms.

---

## Design rules of thumb

- **Keep guidance and control separated in bandwidth.** The separation is what makes both tractable.
- **Fly the gravity turn.** Angle of attack at dynamic pressure costs loads and authority.
- **Put the closed loop handover where the atmosphere ends**, not where it is convenient.
- **Expect mode management to be most of the software.** Budget it as such.
- **Decide the abort criteria before flight.** There is no time to decide during.

---

## Failure modes

**Guidance and control conflated.** They have different bandwidths and different consequences.

**Angle of attack flown in the atmosphere.** A load case and an authority problem at once.

**Open loop through a dispersion.** It flies straight into the injection error.

**Closed loop on a poor navigation solution.** It steers confidently to the wrong place.

**Mode logic treated as glue.** It is where the complexity actually is.

---

## References

- [vehicleArchitecture](../../vehicleArchitecture/), which owns the delta-V budget
- Wie, *Space Vehicle Dynamics and Control*
- Battin, *An Introduction to the Mathematics and Methods of Astrodynamics*
- [rangeSafetyAndFTS](../../rangeSafetyAndFTS/), for what an uncrewed abort resolves to
