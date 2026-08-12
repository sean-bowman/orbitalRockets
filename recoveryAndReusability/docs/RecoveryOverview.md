[Home](../README.md) > Recovery Overview

# Recovery Overview

## Contents

- [Overview](#overview)
- [What this domain found](#what-this-domain-found)
- [The five questions](#the-five-questions)
- [What is computed and what is not](#what-is-computed-and-what-is-not)
- [Document index](#document-index)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Reuse changes the economics of launch and it changes the engineering everywhere. This domain covers the flight side, entry and landing, and the ground side, inspection and life management, along with the economics that decide whether reuse is worth the performance it costs.

**The interesting engineering is not the landing.** It is designing hardware whose condition after flight can be established cheaply enough to fly it again.

---

## What this domain found

**Peak deceleration does not depend on the vehicle.** Allen and Eggers solved ballistic entry in closed form in 1958, and the maximum g is `V_e^2 sin|gamma| / (2 e H)`: entry velocity, flight path angle and atmospheric scale height, and nothing about the body. Across a factor of sixteen in ballistic coefficient the peak g does not move at all. **What moves is the heating**, which goes as the square root of the ballistic coefficient. See [EntryAerodynamics](EntryAerodynamics.md).

**A booster entry is a different problem from an orbital one by a factor of twenty two in heat flux**, because peak flux goes as the cube of entry velocity and a first stage returns from a lofted suborbital trajectory at a quarter of orbital speed. That single exponent is why a booster needs paint and a capsule needs a heat shield, and it is the whole reason first stage reuse arrived long before upper stage reuse.

**Reserve propellant costs nearly five times the payload that recovery hardware does**, even though the hardware is the part that gets designed, weighed and argued about. And the penalty in kilograms is fixed while the payload it eats into is not, so **the penalty as a fraction rises with mission difficulty**: that is why boosters are expended on the hardest missions of an otherwise reusable fleet. See [RecoveryHardware](RecoveryHardware.md).

**Stroke is the cheap variable at touchdown.** Load factor is inversely proportional to it, so a reusable damper, which fills its force-stroke rectangle far worse than a crushable core, is bought back with travel rather than with structure. See [DescentAndLanding](DescentAndLanding.md).

**The limiting life item is not the one that looks worst after a flight.** Thermal protection comes back visibly damaged with more life left than a turbopump that comes back looking untouched, and extending the limiting item moves the limit to the next rather than removing it. See [LifeTrackingAndLimits](LifeTrackingAndLimits.md).

**Two thirds of the benefit of reuse arrives by the third flight.** The amortised unit cost collapses fast and the recurring terms do not, so once the flight count is high **the refurbishment cost is the whole game**. And a three per cent recovery loss rate removes a quarter of the planned flights, because the losses compound over the fleet life. See [ReuseEconomics](ReuseEconomics.md).

---

## The five questions

A reusable stage has to answer these in order, and each one can end the programme.

**Does it survive the entry?** An environment problem, and for a first stage a mild one.

**What does recovery cost in payload?** A performance problem, and the largest single number in the trade.

**Does it survive the landing?** A load and a geometry problem, and the visible one.

**Can its condition be established afterwards?** An inspection problem, and the one that decided the Space Shuttle.

**Does the arithmetic close?** An economics problem, and it is decided by refurbishment cost rather than by flight count.

---

## What is computed and what is not

| Built | Why nothing else does it |
|---|---|
| `EntryTrajectory` | Nothing else computes an entry. Thermal and environments take a flux as an input |
| `RecoveryBudget` | vehicleArchitecture publishes the penalty; nothing builds it from the parts |
| `LandingLoads` | Nothing else has a touchdown in it |
| `LifeTracking` | Nothing else accumulates damage across flights |
| `ReuseEconomics` | Nothing else has a cost in it at all |

| Not built | Where it lives |
|---|---|
| Aeroheating into a structure | [environmentsAndLoads](../../environmentsAndLoads/) and [thermalManagement](../../thermalManagement/) |
| Fatigue and crack growth | [aerospaceMaterials](../../aerospaceMaterials/), which owns Paris law and the material data |
| Payload exchange ratios | [vehicleArchitecture](../../vehicleArchitecture/), whose mass chain defines them |
| Parachute sizing | A drag area and a deployment transient, and the propulsive case is what this domain was built around |
| Guidance to the landing point | [avionicsAndGNC](../../avionicsAndGNC/docs/GuidanceAlgorithms.md), which declined it for stated reasons |
| Sea state and droneship dynamics | Naval architecture. The deck slope is an input here |

---

## Document index

| Document | Covers |
|---|---|
| [EntryAerodynamics](EntryAerodynamics.md) | Allen-Eggers, the peaks, the corridor trade, what heating depends on |
| [DescentAndLanding](DescentAndLanding.md) | Propulsive against parachute, touchdown loads, legs, tipover |
| [RecoveryHardware](RecoveryHardware.md) | What recovery costs in mass and reserve, and what that costs in payload |
| [RecoveryOperations](RecoveryOperations.md) | Ships, safing, transport, and the operation nobody budgets |
| [InspectionAndAcceptance](InspectionAndAcceptance.md) | What to inspect, what NDE catches, and who dispositions |
| [RefurbishmentProcess](RefurbishmentProcess.md) | Turnaround flow, replacement policy, where the cost goes |
| [LifeTrackingAndLimits](LifeTrackingAndLimits.md) | Cycle counting, the limiting item, fleet leader, retirement |
| [FluidSystemReuse](FluidSystemReuse.md) | What reuse does to seals, valves and cleanliness |
| [ReuseEconomics](ReuseEconomics.md) | Break-even, the flight count curve, recovery losses, cost per kilogram |
| [StandardsIndex](StandardsIndex.md) | What governs reuse, which is less than you would expect |
| [ValidationReferences](ValidationReferences.md) | Two closed forms, one units correction, three gaps |

---

## Design rules of thumb

- **Reuse is an inspection problem before it is a landing problem.**
- **Every kilogram of recovery hardware is paid on every flight**, including the ones that do not recover.
- **Design for inspectability or accept teardown.** There is no third option.
- **Life tracking only works if the flight environment was actually measured.**
- **The break-even flight count is the real figure of merit**, not the fact of reuse.
- **Once the flight count is high, argue about refurbishment cost.** Nothing else moves.

---

## Failure modes

**A heavy entry assumed to be a high-g entry.** Peak deceleration does not depend on the vehicle.

**Recovery hardware counted and reserve propellant forgotten.** The reserve is the larger cost by a factor of five.

**A reuse case argued on flight count.** Most of the benefit is in the first three, and the rest is refurbishment cost.

**A recovery loss rate treated as a small correction.** Three per cent removes a quarter of the flights.

**Life tracked from a flight count rather than a measured environment.** It returns a nominal answer regardless of what happened.

**A demonstrated life quoted as a certified one.** The scatter factor is what stands between them.

---

## References

- H. J. Allen and A. J. Eggers, NACA Report 1381, 1958
- K. Sutton and R. A. Graves, NASA TR R-376, 1971
- [vehicleArchitecture/ReusabilityImpacts](../../vehicleArchitecture/docs/ReusabilityImpacts.md), which owns the published payload penalty
- [ValidationReferences](ValidationReferences.md)
