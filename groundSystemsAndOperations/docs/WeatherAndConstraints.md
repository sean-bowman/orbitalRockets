[Home](../README.md) > Weather and Constraints

# Weather and Constraints

## Contents

- [Overview](#overview)
- [Criteria multiply](#criteria-multiply)
- [Attempts beat criteria](#attempts-beat-criteria)
- [Independence is the optimistic assumption](#independence-is-the-optimistic-assumption)
- [The weather rules themselves](#the-weather-rules-themselves)
- [Upper level winds](#upper-level-winds)
- [Launch windows](#launch-windows)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The probability of getting off the ground, and what actually moves it. Almost none of this is a weather forecasting problem and almost all of it is arithmetic that gets done wrong.

---

## Criteria multiply

Launch commit criteria are a list of conditions, every one of which has to hold at the same instant. The probability of that is the product.

**Six criteria, none worse than 88 per cent on its own, give 60.5 per cent together.** The combined penalty against the worst single criterion is 27 points, and it is invisible when criteria are reviewed one at a time, which is how they are reviewed.

| Criterion | Violated | Go alone | Costs the launch |
|---|---|---|---|
| Ground winds | 12% | 88% | 8.3% |
| Upper level winds | 10% | 90% | 6.7% |
| Lightning within 10 nm | 8% | 92% | 5.3% |
| Cumulus cloud rule | 7% | 93% | 4.6% |
| Thick cloud layer rule | 6% | 94% | 3.9% |
| Range asset readiness | 5% | 95% | 3.2% |

**The right column is the number to argue about**, because it is what the criterion actually costs the programme, and it depends on the other criteria as well as on itself. A criterion is never free.

---

## Attempts beat criteria

The result that matters operationally.

Two levers raise the campaign probability: improve a criterion, or get another attempt. They are not close.

| Attempts | Baseline | Fix the worst criterion by 5 points | One more attempt | Ratio |
|---|---|---|---|---|
| 1 | 60.5% | +3.4% | +23.9% | 6.9 |
| 2 | 84.4% | +2.6% | +9.4% | 3.6 |
| 3 | 93.8% | +1.5% | +3.7% | 2.5 |
| 4 | 97.6% | +0.7% | +1.5% | 2.0 |
| 8 | 99.9% | +0.0% | +0.0% | 1.2 |

**Attempts win at every count, and by the most where there are fewest.** Five points on a launch commit criterion is a large change to a criterion; one more attempt is a schedule decision.

That makes **turnaround a launch probability requirement** rather than an operational convenience, which is the link back to [LaunchOperations](LaunchOperations.md).

**It also says when to stop arguing about criteria.** Once a campaign has enough attempts, the criteria stop mattering and the binding constraint moves elsewhere, usually to [propellant resupply](PropellantStorageAndTransfer.md).

---

## Independence is the optimistic assumption

The arithmetic above treats attempts as independent. For weather that is optimistic: a front sitting over the range violates the same criteria tomorrow.

The correlated case is modelled as a two-state chain on the go condition:

```
P(go | went yesterday)     = p + (1 - p) * rho
P(go | scrubbed yesterday) = p * (1 - rho)
```

Those two reproduce the unconditional rate exactly and give a lag-one correlation coefficient of exactly `rho`, which is what makes it a model rather than a fudge. A campaign only ever follows the scrub branch, because the first go ends it.

At a correlation of 0.4 the conditional go probability after a scrub falls from 60.5 to 36 per cent, and an eight attempt campaign falls from 99.9 to 98.3. **The gap between the two is offered as the honest uncertainty in the answer rather than as a result.**

---

## The weather rules themselves

Almost all of them exist because of one thing: **a launch vehicle is a conductor being flown through a charge gradient**, and it can trigger a strike that would not otherwise have happened.

**Triggered lightning is the reason for most of the cloud rules.** The vehicle and its exhaust plume form a long conductor. The rules about cumulus clouds, anvil clouds, debris clouds, thick cloud layers and disturbed weather are all about charge in the air rather than about lightning already occurring.

**Natural lightning is the smaller half of the problem** and the more obvious one.

**Ground winds** are a structural constraint on the vehicle standing on the pad and on the release transient at liftoff.

**Temperature and precipitation** matter for icing, for material properties, and for what a wet vehicle does to its own electrical systems.

**None of these is computed here.** This domain takes violation rates as inputs. Forecasting is not an engineering calculation.

---

## Upper level winds

Worth separating, because it is the one weather constraint that is a vehicle analysis rather than a rule.

A balloon or profiler measures the wind against altitude on the day. That profile is flown through the ascent trajectory, and it produces an angle of attack history, a dynamic pressure history and therefore a set of structural loads and a [control authority](../../avionicsAndGNC/docs/ActuationAndTVC.md) demand.

**The verdict is a load indicator rather than a threshold**, and it is computed hours before the launch on that day's data. That makes it the only launch commit criterion with a whole analysis chain behind it, and the only one where a marginal answer can sometimes be bought back by changing the trajectory.

The loads themselves belong to [environmentsAndLoads](../../environmentsAndLoads/docs/AerodynamicLoads.md).

---

## Launch windows

A window is set by the mission rather than by the ground, and its length changes everything about the count.

**An instantaneous window** removes every hold and recycle option, so the count has to be clean or the day is lost. That is a rendezvous or a specific plane.

**A window of an hour or more** buys the recycles worked in [LaunchOperations](LaunchOperations.md), and the number of holds it absorbs is a design input to the countdown rather than an operational discovery.

**Window length and turnaround are the two schedule inputs to launch probability**, and they act differently: window length buys retries within a day, turnaround buys days.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Six criteria, per attempt | 60.5% |
| Worst criterion alone | 88% |
| Combined penalty | 27 points |
| Attempts to reach 90% | 3 |
| Attempts to reach 95% | 4 |
| Attempts to reach 99% | 5 |
| Campaign at 8 attempts, independent | 99.9% |
| Campaign at 8 attempts, correlated at 0.4 | 98.3% |
| Conditional go after a scrub | 36% |
| Expected scrubs across the campaign | 3.2, of which 1.5 weather |

---

## Design rules of thumb

- **Cost a criterion by what it removes from the campaign**, not by how often it fires.
- **Buy attempts before you buy criteria.** The ratio is 6.9 to one on a single attempt campaign.
- **Treat independence as optimistic** and report the correlated case alongside it.
- **Know whether the window is instantaneous** before designing the count.
- **Do not fight the cloud rules.** They are about triggered lightning, not about visibility.

---

## Failure modes

**Criteria reviewed one at a time.** The multiplication is invisible from inside a single review.

**A campaign planned on independent attempts.** Weather persists.

**Effort spent tightening a criterion on a campaign with many attempts.** It buys nothing measurable.

**A count designed without knowing the window length.** The hold budget is the wrong size.

**An unmeasurable criterion.** It resolves to judgement under time pressure.

---

## Tool interface

```python
from LaunchAvailability import LaunchAvailability

availability = LaunchAvailability()
availability.setInputs({'constraints': {'ground winds':      0.12,
                                        'upper level winds': 0.10,
                                        'lightning':         0.08},
                        'attempts':    4,
                        'correlation': 0.4})

perAttempt  = availability.calculatePerAttempt()
campaign    = availability.calculateCampaign()
levers      = availability.compareLevers()
sweep       = availability.attemptSweep()
attribution = availability.scrubAttribution()
```

---

## References

- [LaunchOperations](LaunchOperations.md), for where attempts come from
- [AerodynamicLoads](../../environmentsAndLoads/docs/AerodynamicLoads.md), for what an upper wind profile produces
- [NaturalEnvironments](../../environmentsAndLoads/docs/NaturalEnvironments.md)
- 45th Weather Squadron launch forecast support, for the published scrub record
