[Home](../README.md) > Public Risk Analysis

# Public Risk Analysis

## Contents

- [Overview](#overview)
- [The calculation](#the-calculation)
- [The criteria](#the-criteria)
- [Two tests, and both apply](#two-tests-and-both-apply)
- [Risk follows population](#risk-follows-population)
- [Casualty area is not footprint](#casualty-area-is-not-footprint)
- [The weakest number](#the-weakest-number)
- [Why launch sites are where they are](#why-launch-sites-are-where-they-are)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

**Public risk is a quantified, regulated number. It is not a judgement call.** This document is the calculation and the limits it is checked against.

---

## The calculation

Casualty expectation is a product summed over every place debris could land:

```
Ec = sum over regions of ( population density * casualty area * probability of impact )
```

with the whole thing scaled by the probability the vehicle fails at all.

**Three inputs and one of them is not about the vehicle.** The population density is a census question, the impact probability is a trajectory and debris question, and the casualty area is a lethality question. Only the failure probability belongs to the launch vehicle, and it multiplies all of them.

---

## The criteria

14 CFR 450.101, read from the regulation.

| Criterion | Limit | Applies to |
|---|---|---|
| Collective, public | 1e-4 expected casualties | all members of the public, excluding aircraft and neighbouring operations personnel |
| Collective, neighbouring | 2e-4 expected casualties | neighbouring operations personnel |
| Individual, public | 1e-6 probability of casualty per launch | any individual member of the public |
| Individual, neighbouring | 1e-5 probability of casualty per launch | any individual neighbouring operations person |
| Aircraft | 1e-6 probability of impact | aircraft, through the hazard areas established for them |

**These are limits rather than targets.** A launch above any of them does not get a licence, and there is no engineering argument that trades one against another. The classes raise rather than reporting a margin, for that reason.

**The neighbouring limits are looser by exactly a factor of two on the collective side and ten on the individual side**, which is the regulation distinguishing people who chose to be there from people who did not.

---

## Two tests, and both apply

The distinction that catches people.

**Collective risk is an expected number of casualties across everybody.** It can be met by spreading a small risk thinly over a large population, because the expectation is a sum.

**Individual risk is the probability of casualty for one person**, and it cannot be spread. **It exists precisely to stop the trade the collective criterion permits.**

**On a coastal site the individual criterion is usually the tighter of the two**, by a factor of two in the worked case, and it is what shapes a launch azimuth: the constraint is not the total risk, it is the household nearest the trajectory.

---

## Risk follows population

The headline result, and it falls straight out of the product.

| Region | Density | P(impact) | Ec | Share of risk |
|---|---|---|---|---|
| Coastal town | 1,500 /km2 | 0.0008 | 1.30e-5 | **88 %** |
| Launch area | 1 /km2 | 0.15 | 1.62e-6 | 11 % |
| Downrange ocean | 0.02 /km2 | 0.82 | 1.77e-7 | 1 % |

**The ocean takes 82 per cent of the debris and contributes 1 per cent of the risk.** One town takes 0.08 per cent of the debris and contributes 88 per cent.

**A range safety analysis is a population analysis with a trajectory attached.** The azimuth that minimises risk is the one that minimises overflown people, not overflown distance, and the trajectory that spends longest over water is not necessarily the safest one if it clips a town on the way out.

**The corollary is that the analysis is only as good as its population data**, which is why the regulation has a whole advisory circular on population exposure assessment.

---

## Casualty area is not footprint

**The casualty area is the area within which a person is considered a casualty**, not the area the fragment covers.

It includes the fragment's own footprint, an allowance for a standing person, and an allowance for the fragment skipping or splashing rather than stopping where it lands. A half kilogram fragment carries about half a square metre; an intact stage carries ninety.

**A 253 fragment catalogue in the worked case carries 540 square metres of casualty area**, which is far more than the debris itself covers and is the number that multiplies the population density.

**Fragment count and casualty area are not proportional**, because the classes differ by orders of magnitude in area each. Sixty medium fragments and twelve large ones carry the same total area, which means a break-up that produces fewer, larger pieces is not obviously safer.

---

## The weakest number

**The failure probability multiplies everything and it is the least well established input.**

The relationship is exactly linear, so a launch that clears its criterion at an assumed two per cent failure probability does not clear it at twenty. In the worked case the criterion is met up to a failure probability of about 0.14.

**The risk analysis inherits the reliability estimate whole**, and a reliability estimate on a new vehicle is an argument rather than a measurement. See [reliabilityAndMissionAssurance](../../reliabilityAndMissionAssurance/) for what that argument looks like and how weak it is early in a programme.

**That is why the sensitivity sweep is worth running and reporting**, rather than quoting a single number against a limit.

---

## Why launch sites are where they are

The same debris over every land use class, at a one per cent impact probability.

| Land use | Density | Ec | Clears 1e-4 |
|---|---|---|---|
| Open ocean | 0 | 0 | yes |
| Shipping lane | 0.02 /km2 | 2.2e-9 | yes |
| Remote land | 1 /km2 | 1.1e-7 | yes |
| Rural land | 50 /km2 | 5.4e-6 | yes |
| Suburban | 1,500 /km2 | 1.6e-4 | **no** |
| Urban | 6,000 /km2 | 6.5e-4 | **no** |
| Dense urban | 20,000 /km2 | 2.2e-3 | **no** |

**Six orders of magnitude, for identical hardware and an identical failure.** Only four of the seven classes clear the criterion.

**That is the whole reason launch sites sit on coasts with an ocean downrange**, and it is a siting decision made once and for ever. No amount of vehicle reliability moves a launch site inland.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Fragments | 253, carrying 540 m2 of casualty area |
| Collective Ec | 1.48e-5 against 1e-4, margin 6.8 |
| Individual Pc | 3.0e-7 against 1e-6, margin 3.3 |
| Which criterion binds | individual, by a factor of 2 |
| Ocean share of debris against risk | 82 % against 1 % |
| Failure probability at which Ec reaches the limit | 0.14 |
| Land use classes clearing the criterion | 4 of 7 |

---

## Design rules of thumb

- **Check both criteria.** They catch different failures and the individual one usually binds.
- **Minimise overflown people, not overflown distance.**
- **Get real population data.** The analysis is only as good as it.
- **Use casualty area, not fragment footprint.** It is far larger.
- **Sweep the failure probability and report the sweep.** It multiplies everything.
- **Treat the limits as limits.** No engineering argument trades against them.

---

## Failure modes

**Only the collective criterion checked.** The individual one is usually tighter.

**Risk minimised by keeping the trajectory over water.** The town on the coast is what matters.

**Fragment footprint used as casualty area.** Off by roughly an order of magnitude.

**A single failure probability quoted against a limit.** It multiplies everything and is the weakest input.

**A land use class used where a census exists.** Six orders of magnitude of spread live in that choice.

---

## Tool interface

```python
from PublicRisk import PublicRisk

risk = PublicRisk()
risk.setInputs({'failureProbability': 0.02,
                'fragments': {'small': 180, 'medium': 60, 'large': 12, 'intact': 1},
                'nearestPersonProbability': 3.0e-7,
                'regions': [{'name': 'coastal town', 'landUse': 'suburban',
                             'impactProbability': 0.0008}]})

collective  = risk.calculateCollective()    # raises above 450.101
individual  = risk.calculateIndividual()    # raises above 450.101
sensitivity = risk.failureSensitivity()
landUse     = risk.compareLandUse()
```

---

## References

- 14 CFR 450.101, *Safety criteria*, and 450.135, *Debris risk analysis*
- FAA AC 450.123-1, *Population Exposure Assessment*, not read
- [TrajectoryLimitsAndIIP](TrajectoryLimitsAndIIP.md), which supplies the impact geometry
- [DebrisAndBlast](DebrisAndBlast.md), for where the impact probabilities come from
