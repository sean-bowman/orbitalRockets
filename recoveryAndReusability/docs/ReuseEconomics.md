[Home](../README.md) > Reuse Economics

# Reuse Economics

## Contents

- [Overview](#overview)
- [The cost of a flight](#the-cost-of-a-flight)
- [Most of the benefit is early](#most-of-the-benefit-is-early)
- [Break-even](#break-even)
- [Recovery losses](#recovery-losses)
- [Cost per flight against cost per kilogram](#cost-per-flight-against-cost-per-kilogram)
- [The precedent](#the-precedent)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Whether reuse pays, and what actually decides it. Every cost here is a fraction of one expendable unit cost, so the arithmetic carries no currency and does not go stale.

---

## The cost of a flight

```
cost per flight = unit cost / flights + refurbishment + recovery + expendable elements
```

**The first term collapses fast and the others do not.** That single asymmetry generates every result below.

**The expendable elements are the term most often forgotten.** On a vehicle with a reusable first stage, the upper stage is thrown away on every flight, and it is not a small fraction of a launch. A reuse case that quotes only the amortised booster is quoting a quarter of the problem.

---

## Most of the benefit is early

| Flights | Cost per flight | Amortised share | Marginal saving |
|---|---|---|---|
| 1 | 1.370 | 73 % | |
| 2 | 0.870 | 57 % | 0.500 |
| 3 | 0.703 | 47 % | 0.167 |
| 5 | 0.570 | 35 % | 0.133 |
| 10 | 0.470 | 21 % | 0.100 |
| 20 | 0.420 | 12 % | 0.050 |
| 40 | 0.395 | 6 % | 0.025 |

**Two thirds of the benefit arrives by the third flight.** Going from one flight to two halves the amortised unit cost. Going from twenty to forty saves 0.025 unit costs, which is under two per cent of the flight.

**The cost floor is the sum of the recurring terms** and nothing about flight count touches it. So **once the flight count is high the refurbishment cost is the whole game**, and a programme optimising flight count at that point is optimising the term that has already stopped mattering.

**The argument for a very high flight count is therefore not amortisation.** It is fleet size: a fleet that flies each article forty times needs half the articles of one that flies each twenty, and articles are capital.

---

## Break-even

Setting a reusable flight equal to an expendable one gives

```
n = 1 / (1 - refurbishment - recovery)
```

which has two useful properties.

**It is small when the recurring costs are small.** At eight per cent refurbishment and four per cent recovery it is 1.1 flights: the second flight of an article pays for the recovery hardware and the operation.

**And it does not exist at all when the recurring costs exceed one unit cost.** A stage that costs as much to refurbish as to build is never worth recovering, at any flight count. **The class refuses rather than reporting a large number**, because reporting one suggests that flying more fixes it and it does not.

**That is the failure mode worth naming**, and it is not hypothetical: a vehicle whose design makes inspection expensive can land in it, which is what [RefurbishmentProcess](RefurbishmentProcess.md) is about.

---

## Recovery losses

Recovery does not always succeed, and the arithmetic is worse than the rate suggests.

A stage recovered with probability `p` flies a geometric number of times before it is lost. **Twenty planned flights at 97 per cent recovery become 15.2 expected: a 24 per cent shortfall from a 3 per cent loss rate.**

**The losses compound over the fleet life rather than applying once.** Each recovery is another chance to lose the article, so a design life of forty flights demands a recovery reliability that a design life of five does not.

Two consequences.

**Recovery reliability is worth several times its rate**, which justifies flying the early flights of a programme conservatively even at a performance cost.

**And the effective flight count is an expectation rather than a plan.** A fleet sized on the plan is a fleet that shrinks.

---

## Cost per flight against cost per kilogram

The comparison that includes the [payload penalty](RecoveryHardware.md), and it is the one most often left out.

A reusable flight costs less **and carries less**. On the worked case the cost per flight falls 65 per cent against expending and the cost per kilogram falls 57, because the reusable flight carries 19 per cent less payload.

**Which of those a customer cares about depends entirely on whether their payload fits** inside the reduced capacity. For most payloads it does, and cost per flight is the number that matters. For the ones it does not, the vehicle is expended and the comparison never arises.

**That is why the penalty rarely appears in a public reuse argument** and why it belongs in an engineering one.

---

## The precedent

The most instructive comparison available, and it is published on both sides.

| | Design turnaround | Achieved turnaround | Flight leader |
|---|---|---|---|
| Space Shuttle orbiter | 14 days | 54 days | 39 flights |
| Falcon 9 booster | not stated | 9.2 days | 36 flights |

**The Shuttle achieved 3.9 times its design turnaround at its very best**, and typical turnarounds were months.

**A Falcon 9 booster has turned around in less time than the Shuttle's design goal**, and its flight leader has 36 flights against a stated qualification target of 40.

**The difference is not landing technology.** Both vehicles landed successfully and repeatedly. **It is that the Shuttle's design made establishing its condition expensive**, and that is the argument this whole domain rests on: reuse is an inspection problem before it is a landing problem.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Refurbishment | 0.08 unit costs |
| Recovery operation | 0.04 |
| Expendable elements | 0.25 |
| Break-even | 1.1 flights |
| Benefit realised by flight 3 | 68 % |
| Cost floor | 0.370 unit costs |
| Planned flights | 20 |
| Expected at 97 % recovery | 15.2 |
| Cost per flight saving | 65 % |
| Cost per kilogram saving | 57 % |

---

## Design rules of thumb

- **Include the expendable elements.** The upper stage flies once.
- **Stop optimising flight count once the amortised term is small.**
- **Attack refurbishment cost.** It is the floor and nothing else touches it.
- **Treat recovery reliability as worth several times its rate.**
- **Size the fleet on the expected flight count, not the planned one.**
- **Quote cost per kilogram as well as cost per flight**, and say which one the case rests on.

---

## Failure modes

**A reuse case quoting only the amortised booster.** The upper stage flies once.

**Flight count optimised at a high count.** The term has already collapsed.

**A large break-even reported where none exists.** Flying more does not fix a refurbishment cost above a unit cost.

**A fleet sized on planned flights.** Losses compound.

**Cost per flight quoted without the payload penalty.** The saving per kilogram is smaller.

**A design turnaround quoted as a capability.** The Shuttle's fourteen days is the cautionary example.

---

## Tool interface

```python
from ReuseEconomics import ReuseEconomics

economics = ReuseEconomics()
economics.setInputs({'refurbishmentCost':  0.08,
                     'recoveryCost':       0.04,
                     'expendableElements': 0.25,
                     'recoverySuccess':    0.97,
                     'flightsPerArticle':  20.0,
                     'payloadPenalty':     0.189})

effective     = economics.effectiveFlights()
cost          = economics.costPerFlight()
sweep         = economics.flightCountSweep()
breakEven     = economics.breakEven()            # raises where none exists
perKilogram   = economics.costPerKilogram()
refurbishment = economics.refurbishmentSensitivity()
```

---

## References

- [RefurbishmentProcess](RefurbishmentProcess.md), for what sets the floor
- [RecoveryHardware](RecoveryHardware.md), for the payload penalty
- [RecoveryOperations](RecoveryOperations.md), for the recovery term
- [CostAndProducibility](../../vehicleArchitecture/docs/CostAndProducibility.md)
