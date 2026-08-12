[Home](../README.md) > Life Tracking and Limits

# Life Tracking and Limits

## Contents

- [Overview](#overview)
- [The arithmetic](#the-arithmetic)
- [The limiting item](#the-limiting-item)
- [Why it only works with a measured environment](#why-it-only-works-with-a-measured-environment)
- [Demonstrated against certified](#demonstrated-against-certified)
- [The fleet leader](#the-fleet-leader)
- [Retirement](#retirement)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

How many more times an article can fly. The arithmetic is easy and the inputs are the problem.

---

## The arithmetic

Miner's rule applied to an airframe. Every flight consumes a fraction of each item's allowable life, the fractions accumulate linearly, and the article is retired when one reaches unity.

```
consumed_i = sum over flights of ( damage per flight )_i
```

**Linear accumulation is a convention rather than a measurement.** Real failures scatter around it by a factor of several either way, which is why a life limit carries a [scatter factor](#demonstrated-against-certified) on top rather than being taken at its face value.

The damage per flight itself comes from a stress spectrum through a fatigue curve, which is [aerospaceMaterials](../../aerospaceMaterials/docs/FractureAndDamageTolerance.md) and [aerospaceStructures](../../aerospaceStructures/docs/FatigueAndFracture.md). **This domain counts; it does not derive.**

---

## The limiting item

**One item limits the article and it is rarely the one that looks worst after a flight.**

| Item | Driver | Allowable flights |
|---|---|---|
| Engine turbopump | low cycle fatigue on start and shutdown | 15 |
| Thermal protection | recession and cracking per entry | 25 |
| Landing leg | crush core or damper, one shot per landing | 40 |
| Pressure vessel | pressure cycles against a fracture life | 60 |
| Primary structure | load cycles | 200 |

**Thermal protection comes back visibly damaged with more life left than a turbopump that comes back looking untouched.** Appearance and damage rate are unrelated, and an inspection programme weighted by how alarming things look is weighted wrongly.

**The primary structure is almost never the limit**, which surprises people whose intuition comes from aircraft. A launch vehicle sees few load cycles and severe thermal and pressure ones.

**And extending the limiting item moves the limit rather than removing it.** Doubling the turbopump life on the table above buys ten flights, not a hundred and eighty five, because thermal protection is waiting at twenty five. **Life limits behave exactly like [turnaround drivers](../../groundSystemsAndOperations/docs/LaunchOperations.md)**: one governs, and fixing it buys the gap to the next.

---

## Why it only works with a measured environment

The uncomfortable part.

**Damage per flight depends on the environment the article actually saw**, not on the number of flights. A flight flown hot, or long, or through a heavier gust consumes more life than a nominal one.

**A tracker fed nominal flights returns a nominal answer regardless of what happened.** It is then a counter with a life limit written on it, which is not the same thing and is worse because it looks like the same thing.

**So life tracking is a telemetry requirement before it is a structures one.** The instrumentation that records the environment has to exist, has to survive, and has to be recorded and kept. See [InspectionAndAcceptance](InspectionAndAcceptance.md), where the same argument produces the access ports.

The leverage is worth knowing. On an article with ten flights on it and fifteen allowable, **a severity factor of 1.5 exhausts it entirely**: the damage already consumed does not shrink when conditions improve, so a harsher environment costs more than proportionally, and the more flights are already on the article the worse the leverage gets.

---

## Demonstrated against certified

Two different numbers that get quoted interchangeably.

**A demonstrated life is one article surviving a count**, in test or in service.

**A certified life has to cover the fleet**, so it carries a scatter factor between it and the demonstration. A factor of four is a common convention.

**The certified number is therefore always smaller than the demonstrated one**, and a programme that quotes its demonstrated life as its certified life has skipped the step that covers the scatter.

**The worked case states a certified life above what its scatter factor supports**, which is a real and common position rather than an error: the gap is held by inspection rather than by analysis. That is a legitimate strategy and it has a cost, which is the inspection programme that holds it, and it is why the [inspection ladder](InspectionAndAcceptance.md) and the life limit are the same conversation.

---

## The fleet leader

**Flying one article ahead of the rest is the instrument**, and the lead in flights is the warning.

A fleet flown evenly has no leader, so every article reaches its life limit at the same time and **the first indication is a failure rather than a finding**. A fleet with a leader fourteen flights ahead has fourteen flights of warning, and it has an article that can be torn down to learn what the rest are doing.

**That is what a fleet leader is for**, and it is the reason to tear down the leader rather than the fleet: teardown costs ninety times a walkaround and ends the article, so doing it once buys information about all of them.

---

## Retirement

The decision the arithmetic exists to support, and it is a disposition rather than a number.

**The class raises rather than reporting a negative remaining life.** An article past a life limit is a decision for a named person on the evidence, and a tool that returns a negative number invites somebody to treat it as a small negative margin.

**Three things can extend a life** and they are not equivalent. **Replace the limiting item**, which buys the gap to the next. **Re-analyse it against a measured environment**, which is free if the instrumentation exists. **Or accept it on inspection**, which costs an inspection programme forever.

**And retirement is not the end of the article's usefulness.** A retired flight leader is the best teardown specimen a programme will ever have.

---

## Worked numbers

An article with ten flights on it.

| Quantity | Value |
|---|---|
| Limiting item | engine turbopump |
| Remaining flights | 5 |
| Gain from extending it | 10 flights, and no more |
| Severity that exhausts it now | 1.5 |
| Fleet leader against next article | 36 against 22 |
| Warning bought | 14 flights |
| Demonstrated life | 15 |
| Certified supported at scatter 4 | 3.8 |
| Certified stated | 20, an implied scatter of 0.75 |
| Inspection cost spread | 90x |

---

## Design rules of thumb

- **Instrument the flight environment.** Without it the tracker is a counter.
- **Find the limiting item before optimising anything.**
- **Expect the gain from extending it to be the gap to the next.**
- **Fly a fleet leader.** The lead is the warning.
- **Tear down the leader, not the fleet.**
- **Do not quote a demonstrated life as a certified one.**

---

## Failure modes

**Life tracked by flight count.** A counter wearing a life limit.

**The alarming item assumed to be the limiting one.** Appearance and damage rate are unrelated.

**A life limit extended in isolation.** The next item is waiting.

**A fleet flown evenly.** No leader, no warning, and every article limits at once.

**A demonstrated life certified.** The scatter factor is what stands between them.

**A negative remaining life reported as a number.** It is a disposition.

---

## Tool interface

```python
from LifeTracking import LifeTracking

life = LifeTracking()
life.setInputs({'flightsFlown':   10.0,
                'certifiedLife':  20.0,
                'severityFactor': 1.0})

accumulation  = life.calculateAccumulation()      # raises past a life limit
severity      = life.severitySensitivity()
fleet         = life.fleetLeaderLead([36.0, 22.0, 18.0])
certification = life.certifiedAgainstDemonstrated()
ladder        = life.inspectionLadder()
```

---

## References

- [FatigueAndFracture](../../aerospaceStructures/docs/FatigueAndFracture.md), for where damage per flight comes from
- [FractureAndDamageTolerance](../../aerospaceMaterials/docs/FractureAndDamageTolerance.md)
- [InspectionAndAcceptance](InspectionAndAcceptance.md), for what holds a life the analysis does not
- [LaunchOperations](../../groundSystemsAndOperations/docs/LaunchOperations.md), for the same one-driver arithmetic
