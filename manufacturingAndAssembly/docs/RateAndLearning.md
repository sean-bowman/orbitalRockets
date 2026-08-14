[Home](../README.md) > Rate and Learning

# Rate and Learning

## Contents

- [Overview](#overview)
- [Wright's curve](#wrights-curve)
- [The unit cost against the average](#the-unit-cost-against-the-average)
- [Which processes learn](#which-processes-learn)
- [Capacity is the slowest station](#capacity-is-the-slowest-station)
- [Shifts before machines](#shifts-before-machines)
- [What rate does to a design](#what-rate-does-to-a-design)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

**Rate changes everything.** A process that works for one article may not work for fifty, and a cost that is true at unit one is not true at unit fifty. Both are arithmetic and both are routinely got wrong in the same direction.

---

## Wright's curve

The cost of the nth unit built is

```
C(n) = C(1) * n ** b        b = log2(learning rate)
```

so **every doubling of cumulative production costs a fixed fraction of the previous doubling.** An 85 per cent rate means the second unit costs 85 per cent of the first, the fourth 85 per cent of the second, and so on. The exponent is negative and small, which is what makes the curve log-linear.

| Unit | Cost | Of the first | Saving from the previous doubling |
|---|---|---|---|
| 1 | 1.000 | 100 % | |
| 2 | 0.850 | 85 % | 0.150 |
| 4 | 0.722 | 72 % | 0.128 |
| 8 | 0.614 | 61 % | 0.108 |
| 16 | 0.522 | 52 % | 0.092 |
| 32 | 0.444 | 44 % | 0.078 |
| 64 | 0.377 | 38 % | 0.067 |

**Every doubling saves the same fraction and a smaller absolute amount**, so 45 per cent of the whole saving arrives in the first four units.

**That has an uncomfortable consequence for a launch programme.** A vehicle built ten or twenty times has barely started down its curve, so its unit cost is much closer to the first article than to the asymptote. **A cost estimate quoting the learned-out figure is quoting a number the programme will not reach**, and the gap is not small.

---

## The unit cost against the average

Two numbers that get used interchangeably and should not be.

**The unit cost** is what the next one costs. It is the right number for a marginal decision: whether to build one more.

**The cumulative average** is the total divided by the count. It is the number a programme is judged on, and **it lags the unit cost badly** because it still carries every expensive early unit.

Over a run of twenty at 85 per cent, the last unit costs 0.50 of the first and the cumulative average is 0.62: a factor of 1.25 between them. **Quoting the wrong one moves an entire programme cost estimate by a quarter.**

---

## Which processes learn

The learning rate is not a property of the programme. It is a property of how much of the cost is labour.

| Process class | Rate | Unit 20 | Why |
|---|---|---|---|
| Manual assembly | 0.80 | 0.38 | the most labour and therefore the steepest curve |
| Composites | 0.82 | 0.42 | layup is labour, cure is not |
| Welding | 0.85 | 0.50 | operator skill and fixturing both improve |
| Machining | 0.90 | 0.63 | programme once, then it is cycle time |
| Additive | 0.92 | 0.70 | build time is build time |
| Raw material | 0.98 | 0.92 | almost nothing to learn; it is a purchase |

**The more labour a process carries, the more there is to learn.** A process that is mostly a material purchase barely learns at all.

**Which means a vehicle built from bought hardware has a flatter curve than one built from labour**, whatever the programme plan assumes, and a make-buy decision is therefore also a decision about the shape of the cost curve. See [SupplyChainAndMakeBuy](SupplyChainAndMakeBuy.md).

---

## Capacity is the slowest station

The second piece of arithmetic, and it is simpler and more often ignored.

**A line produces at the rate of its slowest station and no faster**, because the stations run in parallel on different units. Capacity is a minimum rather than a sum.

| Station | Cycle time | Utilisation |
|---|---|---|
| Circumferential weld and dome mate | 75 h | **90 %** |
| Longitudinal weld | 60 h | 72 % |
| Proof and inspect | 50 h | 60 % |
| Plate roll and tack | 45 h | 54 % |
| Y-ring machining | 38 h | 46 % |

**A line with 268 hours of total cycle time makes 27 units a year because one station takes 75 of them.** Anything spent on the other four buys nothing at all.

**And the bottleneck moves.** Cutting the circumferential weld to 55 hours makes the longitudinal weld the constraint at 60, so the gain from the fix is the gap to the next station rather than the whole difference. That is the same arithmetic as a [turnaround driver](../../groundSystemsAndOperations/docs/LaunchOperations.md) and a [life limit](../../recoveryAndReusability/docs/LifeTrackingAndLimits.md), and it appears in this repository for the third time because it is genuinely general.

**Utilisation above about 85 per cent is a warning rather than an achievement**, because above it queueing time grows faster than utilisation does and the line stops behaving linearly. A line at 90 per cent meets its rate on paper and misses it whenever anything goes wrong.

---

## Shifts before machines

Worth checking before a machine is bought, because it is usually the cheapest capacity available.

**A second shift doubles capacity for the cost of people.** A second machine doubles it for the cost of a machine plus people, plus the floor space, plus a second set of tooling, plus a second qualification.

**The limits on shifts are real and they are not capital**: recruitment, supervision, the quality of work done at three in the morning, and the maintenance window that has to fit somewhere.

**Neither is free and the ordering is nearly always shifts first**, which makes it the first question rather than the last.

---

## What rate does to a design

The reason this belongs in an engineering document rather than a management one.

**A process that works once may not work fifty times.** A hand layup that one skilled person can do is a rate limit with a name and a holiday allowance.

**Tooling that is adequate for one article is a bottleneck for fifty.** See [ToolingAndFixturing](ToolingAndFixturing.md): the tooling decision is made early, by someone who was not thinking about rate.

**Inspection scales badly.** A [teardown or a full volumetric inspection](InspectionAndNDE.md) that is affordable on a first article is not affordable on every unit, so a rate programme has to decide what it inspects on every unit and what it inspects on a sample, and that is a design-for-inspection decision.

**And a design with many unique parts has a flat learning curve by construction**, because nothing is made often enough to learn. Part count reduction is a cost decision before it is a mass one.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Learning rate | 0.85, exponent -0.234 |
| Unit 64 | 38 % of the first |
| Share of the saving in the first four units | 45 % |
| Unit 20 against the cumulative average | 0.50 against 0.62 |
| Sum of station cycle times | 268 h |
| Bottleneck | 75 h, 90 % utilisation |
| Capacity | 27 a year against a demand of 24 |
| Gain from fixing the bottleneck | 15 h, then it moves |
| Capacity after the fix | 33 a year |

---

## Design rules of thumb

- **Quote the unit cost or the average and say which.** They differ by a quarter at unit 20.
- **Do not quote a learned-out cost for a short programme.** It will not be reached.
- **Pick the learning rate from how much of the cost is labour.**
- **Improve the bottleneck or improve nothing.**
- **Expect the bottleneck to move**, and know what it moves to.
- **Treat 85 per cent utilisation as a warning.**
- **Ask about shifts before buying a machine.**

---

## Failure modes

**Capacity estimated as the sum of cycle times.** It is the slowest station.

**Investment off the bottleneck.** No rate gain at all.

**A learned-out unit cost in a twenty unit programme.** Off by a factor.

**The cumulative average and the unit cost confused.** A quarter, in the direction that flatters.

**A learning rate assumed rather than chosen by labour content.** A bought-hardware vehicle barely learns.

**A hand process taken to rate.** A skilled person is a rate limit.

---

## Tool interface

```python
from ProductionRate import ProductionRate

production = ProductionRate()
production.setInputs({'firstUnitCost': 1.0,
                      'processClass':  'welding',
                      'annualDemand':  24.0,
                      'shifts':        1.0,
                      'stations':      {'longWeld': 60.0, 'circWeld': 75.0}})

doublings  = production.doublingSweep()
cumulative = production.cumulativeCost(20)
classes    = production.compareProcessClasses(20)
takt       = production.calculateTakt()          # raises where the line cannot meet its rate
shifts     = production.shiftSensitivity()
```

---

## References

- T. P. Wright, *Factors Affecting the Cost of Airplanes*, 1936, the origin of the learning curve
- [CostAndProducibility](../../vehicleArchitecture/docs/CostAndProducibility.md), which names this as a gap
- [LaunchOperations](../../groundSystemsAndOperations/docs/LaunchOperations.md), for the same bottleneck arithmetic
- [ToolingAndFixturing](ToolingAndFixturing.md)
