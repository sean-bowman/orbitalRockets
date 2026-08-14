[Home](../README.md) > Redundancy and Fault Tolerance

# Redundancy and Fault Tolerance

## Contents

- [Overview](#overview)
- [The beta factor](#the-beta-factor)
- [What another unit buys](#what-another-unit-buys)
- [What reducing beta buys](#what-reducing-beta-buys)
- [Coverage](#coverage)
- [Active, standby and voting](#active-standby-and-voting)
- [Fail operational and fail safe](#fail-operational-and-fail-safe)
- [Redundancy that is not](#redundancy-that-is-not)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

**Redundancy that shares a failure cause is not redundancy.** This document is the arithmetic behind that sentence, and the arithmetic is more damning than the sentence is.

---

## The beta factor

A failure rate splits into an independent part and a common cause part.

```
lambda_independent = (1 - beta) * lambda
lambda_common      = beta * lambda
```

The independent part is what redundancy defends against. **The common part defeats every redundant unit at once.** So for n parallel units,

```
Q = ((1 - beta) * q) ** n  +  beta * q
```

**The first term falls as the nth power and the second does not fall at all.**

That is the whole content of the subject. At a ten per cent beta and a one per cent element failure, two units give 1.08e-3 against an ideal 1.00e-4: **the redundancy is worth a factor of nine rather than a factor of a hundred**, and common cause is 93 per cent of what remains.

**Beta is a property of how much the units share.**

| Sharing | Beta | Means |
|---|---|---|
| Identical, same batch | 0.20 | same design, same lot, same installation |
| Identical, different lot | 0.10 | same design, different lot |
| Same design, separated | 0.05 | physically and thermally separated |
| Diverse design | 0.02 | different designs solving the same problem |
| Diverse and separated | 0.01 | the practical floor |

**The ordering is a mechanism rather than a value.** Units that share a design share its design errors, and units that share an environment share what the environment does to them. See [FlightComputers](../../avionicsAndGNC/docs/FlightComputers.md), where the same argument is made about software: three copies of one program vote unanimously for the wrong answer.

---

## What another unit buys

| Units | Q with beta 0.10 | Q ideal | Common cause share | This unit buys |
|---|---|---|---|---|
| 1 | 1.00e-2 | 1.00e-2 | 0 % | |
| 2 | 1.08e-3 | 1.00e-4 | 93 % | 89 % |
| 3 | 1.00e-3 | 1.00e-6 | 100 % | **7 %** |
| 4 | 1.00e-3 | 1.00e-8 | 100 % | 0 % |
| 5 | 1.00e-3 | 1.00e-10 | 100 % | 0 % |

**The first duplication is worth a great deal. The second is worth seven per cent. The third is worth nothing at all.**

By five units the ideal arithmetic and the real one differ by seven orders of magnitude, which is a good measure of how badly a redundancy case built on the ideal form misleads.

---

## What reducing beta buys

The lever that works, at a fixed unit count.

| Sharing | Beta | Q at two units |
|---|---|---|
| Identical, same batch | 0.20 | 2.06e-3 |
| Identical, different lot | 0.10 | 1.08e-3 |
| Same design, separated | 0.05 | 5.90e-4 |
| Diverse design | 0.02 | 2.96e-4 |
| Diverse and separated | 0.01 | 1.98e-4 |

**Ten times across the ladder, with no hardware added.** On the worked case adding a third unit buys seven per cent and moving one rung down the ladder buys forty-five: **a factor of six for a layout decision and a sourcing decision.**

**That is the cheapest reliability available and it is the one most often left on the table**, because separation and diversity are decided early by people thinking about packaging and procurement rather than about reliability.

---

## Coverage

The term that matters for standby redundancy and not for active.

**An active redundant set has all units running**, so a failure is either tolerated immediately or it is not. Coverage does not enter.

**A standby set has to detect the failure and switch.** A standby unit that is not known to have failed is not there when it is called on, so the benefit of every unit after the first is multiplied by the fraction of failures the monitoring actually detects.

**At 95 per cent coverage a standby set gets 95 per cent of the redundancy it paid for**, and the missing five per cent is a unit sitting there failed while everybody believes it is available. See [FlightComputers](../../avionicsAndGNC/docs/FlightComputers.md) for the same problem in a voting context: **deciding which unit is right is harder than having two.**

---

## Active, standby and voting

Three arrangements with different failure behaviour.

**Active parallel.** All units run, any one suffices. Simplest, and it has no detection requirement.

**Standby.** One runs, the others wait. Lower wear and lower power, and it needs detection and switching, both of which are new failure modes.

**Voting.** Three or more run and the majority wins. It tolerates a unit producing a wrong answer rather than no answer, which the other two arrangements do not, and it costs a voter that is itself a single point unless it too is redundant.

**The choice is about what kind of failure is expected.** A unit that stops is handled by any of them; a unit that lies is handled only by voting.

---

## Fail operational and fail safe

Different requirements that get conflated, and the difference is what happens after the failure.

**Fail operational** means the function continues. It needs enough redundancy to keep working with one unit gone, and it is what a control system needs during a burn.

**Fail safe** means the system goes to a state that does no harm. It needs a defined safe state and a way to reach it, and it is usually cheaper.

**Fail passive** means it stops doing anything, which is safe only if stopping is safe.

**A launch vehicle is mostly fail operational during flight and fail safe on the ground**, and the transition between those is a real design boundary. **The failure is assuming one where the other applies**: a valve that fails closed is fail safe on a pad and fail catastrophic during a burn.

**And the fault tolerance requirement, one fault or two, is a level rather than a design.** It says how many failures the system survives, not how the survival is arranged, and the arrangement is what this document is about.

---

## Redundancy that is not

Four patterns worth recognising.

**A shared power supply, harness or connector.** Two units on one feed are one unit. See [electricalPower](../../electricalPower/docs/PowerDistribution.md).

**A shared environment.** Two units in the same bay see the same shock, the same thermal excursion and the same contamination.

**A shared lot.** Two units from one manufacturing lot share whatever went wrong in it, which is why [lot traceability](../../manufacturingAndAssembly/docs/ProcessQualification.md) is a reliability control rather than a paperwork one.

**And a series element.** A redundant train behind a single receiver is a single string system, which [rangeSafetyAndFTS](../../rangeSafetyAndFTS/docs/FlightTerminationSystems.md) works through in the FTS case.

**Each of those is invisible on a block diagram and obvious on a layout drawing**, which is why a redundancy review that only looks at the block diagram finds none of them.

---

## Worked numbers

Two avionics units at 0.99 each, identical from different lots, against a 0.9995 requirement.

| Quantity | Value |
|---|---|
| Ideal reliability | 0.999900, **clears** |
| With beta 0.10 | 0.998919, **fails** |
| Common cause share | 93 % |
| A third unit | +7 % |
| One rung down the sharing ladder | +45 % |
| Separation alone (beta 0.05) | 0.999410, still fails |
| Diverse design (beta 0.02) | 0.999704, **clears** |

**The ideal arithmetic clears the requirement and the real one does not**, which is exactly the error the beta factor exists to catch.

---

## Design rules of thumb

- **Compute redundancy with a beta factor.** The ideal form misleads by orders of magnitude.
- **Stop at two units unless beta is very small.** The third buys single digits.
- **Reduce beta instead**: separate, use different lots, diversify where it is justified.
- **Apply coverage to standby sets** and not to active ones.
- **Choose voting if a unit can lie**, not just stop.
- **Review the layout, not the block diagram.** Shared causes are invisible on one and obvious on the other.

---

## Failure modes

**A redundancy gain from the ideal formula.** Off by the ratio of two terms.

**A third unit on a common cause dominated set.** Mass, power and interfaces for single digits.

**Two units on one power feed.** One unit with two boxes.

**A standby set with no coverage term.** It is not there when called.

**Fail safe assumed where fail operational is needed.** A valve that fails closed during a burn.

**A redundancy review conducted on a block diagram.** Every shared cause is invisible there.

---

## Tool interface

```python
from RedundancyAnalysis import RedundancyAnalysis
from reliabilityUtils import RedundancyError

analysis = RedundancyAnalysis()
analysis.setInputs({'elementReliability':  0.99,
                    'units':               2,
                    'sharing':             'identicalDifferentLot',
                    'requiredReliability': 0.9995})

configuration = analysis.calculateConfiguration()
units         = analysis.unitSweep()
betas         = analysis.betaSweep()
levers        = analysis.compareLevers()

# Identical units from different lots do not clear the requirement on common cause alone.
try:
    analysis.checkRequirement()
except RedundancyError:
    pass

# Diversifying them does, with no hardware added.
analysis.sharing = 'diverseDesign'
analysis.beta = 0.02
check = analysis.checkRequirement()
```

---

## References

- [FlightComputers](../../avionicsAndGNC/docs/FlightComputers.md), for the common mode argument in software
- [FlightTerminationSystems](../../rangeSafetyAndFTS/docs/FlightTerminationSystems.md), for series elements in a redundant train
- [ProcessQualification](../../manufacturingAndAssembly/docs/ProcessQualification.md), for the lot argument
- IEC 61508 and the beta factor estimation methods, not read
