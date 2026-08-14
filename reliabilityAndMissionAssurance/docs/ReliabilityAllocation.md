[Home](../README.md) > Reliability Allocation

# Reliability Allocation

## Contents

- [Overview](#overview)
- [Series multiplication](#series-multiplication)
- [Item count is a reliability parameter](#item-count-is-a-reliability-parameter)
- [Allocating a target](#allocating-a-target)
- [The basis audit](#the-basis-audit)
- [Why prediction is so often wrong](#why-prediction-is-so-often-wrong)
- [What demonstrating a target would take](#what-demonstrating-a-target-would-take)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Where a vehicle's reliability goes, and what the number rests on. The second half is the harder one.

---

## Series multiplication

A launch vehicle is a series system: everything has to work. So the reliabilities multiply, and the multiplication is unforgiving.

```
100 items at 0.999 each   ->  0.905
1000 items at 0.999 each  ->  0.368
```

**The budget is kept in failure probability rather than in reliability**, because failure probabilities are nearly additive for small values and reliabilities are not. On the worked case the sum of failure probabilities is 2.850e-2 against an exact 2.824e-2: **an error of 0.93 per cent, and the shares mean something.**

That is why an allocation divides the allowed **unreliability** rather than the reliability, and why a budget reported as a column of reliabilities hides where the problem is.

---

## Item count is a reliability parameter

The consequence that reaches the design.

At a fixed per-item reliability, the system reliability falls exponentially with the count.

| Items | System reliability at 0.99995 each |
|---|---|
| 10 | 0.9995 |
| 100 | 0.9950 |
| 1,000 | 0.9512 |
| 5,000 | 0.7788 |

**Reliability halves at about 14,000 items** at that per-item figure.

**A design with twice the parts at the same per-part reliability has roughly twice the failure probability**, which makes **part count reduction a reliability decision before it is a mass or cost one.** That is the argument a mass case cannot make on its own, and it is the strongest available reason to delete a component.

It also cuts the other way: **a component added for reliability has to buy more than it costs.** A monitoring channel, a bypass line or an extra sensor is a part with its own failure modes, and if it does not remove more failure probability than it adds it has made the vehicle worse.

---

## Allocating a target

Given a vehicle target, each subsystem gets a share of the allowed unreliability.

**Equal allocation is the honest starting point and it is rarely right.** A propulsion system and a structure do not deserve the same failure budget, because one of them has thousands of parts and moving fluid and the other has bolts.

**Weighted allocation by complexity, by heritage or by criticality is the usual next step**, and every weighting is a judgement that should be written down rather than embedded.

**What the allocation is actually for is a conversation.** It gives each subsystem a number to design to and it gives the system a way to see when one of them has spent more than its share. **It is not a prediction and it should never be reported as one**, which is what the basis audit is for.

---

## The basis audit

The most useful thing in this document.

**A reliability number without a stated basis is a wish.** So every entry in a budget carries where it came from, and the bases are not equivalent.

| Basis | Means |
|---|---|
| Demonstrated | a test programme with a stated confidence |
| Heritage | flight history on this design |
| Predicted | a parts count prediction, which is usually optimistic |
| Allocated | a share of the target, with nothing behind it yet |
| Assumed | a number somebody wrote down |

On the worked case:

| Basis | Share of the failure budget |
|---|---|
| Heritage | 53 % |
| Assumed | 21 % |
| Allocated | 14 % |
| Demonstrated | 11 % |
| Predicted | 2 % |

**63 per cent has evidence behind it and 35 per cent does not.** The budget closes, and a third of it rests on an allocation and a number somebody wrote down.

**That is not a criticism of the programme, it is the normal state of a budget early on.** What matters is that it is visible, because the subsystems with no evidence are exactly the ones where the estimate will move, and they should be where the test programme goes.

**The basis column costs nothing to keep and it is the difference between a budget and a list of numbers.**

---

## Why prediction is so often wrong

Worth stating because parts count prediction is the default answer and this domain declines to implement it.

**The handbooks are old and their data older.** A failure rate database built from a component population decades ago describes that population.

**They predict random failures and most failures are not random.** They are design escapes, process escapes and human error, and none of those appears in a parts count.

**They are optimistic in a specific way**: they capture the wear-out and random behaviour of well made parts operating in their envelope, which is the regime where almost nothing goes wrong.

**And a prediction has an authority its basis does not support**, which is the practical problem: a number from a handbook looks like a measurement and gets treated as one.

**So this domain takes failure rates as inputs, registers them as unvalidated, and says the only honest source is operating experience.** See [ValidationReferences](ValidationReferences.md).

---

## What demonstrating a target would take

The arithmetic that closes the argument.

With zero failures in n trials the lower confidence bound on reliability is `(1 - C) ** (1/n)`, so

```
n = ln(1 - C) / ln(R)
```

**Demonstrating a 0.97 vehicle target at 95 per cent confidence would take 98 flights with no failures.** Each additional nine costs ten times that.

**So a vehicle reliability is argued from its parts rather than demonstrated as a whole**, which is exactly the position [rangeSafetyAndFTS](../../rangeSafetyAndFTS/docs/FlightTerminationSystems.md) reaches about a flight termination system, by the same arithmetic.

**Which is why the basis audit matters more than the number.** The number cannot be demonstrated; what can be shown is what each piece of it rests on.

---

## Worked numbers

| Subsystem | Reliability | Share of failure budget | Basis |
|---|---|---|---|
| Propulsion | 0.98500 | 53 % | heritage |
| Fluid systems | 0.99400 | 21 % | assumed |
| Separation | 0.99600 | 14 % | allocated |
| Avionics | 0.99700 | 11 % | demonstrated |
| Structures | 0.99950 | 2 % | predicted |

| Quantity | Value |
|---|---|
| Rollup | 0.97176 against a 0.970 target, margin 1.06 |
| Additive approximation error | 0.93 % |
| Evidenced share of the failure budget | 63 % |
| Flights to demonstrate the target | 98 |

---

## Design rules of thumb

- **Keep the budget in failure probability.** The shares mean something there.
- **Carry a basis on every entry.** It costs nothing.
- **Put the test programme where the evidence is missing**, not where the number is worst.
- **Count the parts.** Item count is a reliability parameter.
- **Make a component added for reliability pay for itself.**
- **Do not report an allocation as a prediction.**

---

## Failure modes

**A budget in reliabilities.** The shares are meaningless and the dominant subsystem is hidden.

**No basis column.** A list of numbers with a total.

**A parts count prediction quoted as a measurement.** It has authority its basis does not support.

**Part count treated as a mass question only.** It is a reliability parameter.

**A monitoring channel added without accounting for its own failures.** It can make the vehicle worse.

**A vehicle reliability quoted as demonstrated.** 98 flights, and nobody has flown them.

---

## Tool interface

```python
from ReliabilityBudget import ReliabilityBudget

budget = ReliabilityBudget()
budget.setInputs({'target': 0.97, 'itemReliability': 0.99995,
                  'subsystems': [{'name': 'propulsion', 'reliability': 0.985,
                                  'basis': 'heritage'}]})

rollup        = budget.calculateRollup()      # raises where the budget does not close
allocation    = budget.allocate()
audit         = budget.basisAudit()
items         = budget.itemCountEffect()
demonstration = budget.demonstrationCost()
```

---

## References

- [FlightTerminationSystems](../../rangeSafetyAndFTS/docs/FlightTerminationSystems.md), for the same demonstration arithmetic
- [RedundancyAndFaultTolerance](RedundancyAndFaultTolerance.md), for what redundancy actually buys against a budget
- [CostAndProducibility](../../vehicleArchitecture/docs/CostAndProducibility.md), for the other reason to reduce part count
- MIL-HDBK-217, the parts count prediction handbook, not read and deliberately not implemented
