[Home](../README.md) > Flight Termination Systems

# Flight Termination Systems

## Contents

- [Overview](#overview)
- [The architecture](#the-architecture)
- [The requirement](#the-requirement)
- [The arithmetic that shapes the subject](#the-arithmetic-that-shapes-the-subject)
- [What is done instead](#what-is-done-instead)
- [Redundancy that is not](#redundancy-that-is-not)
- [Safe and arm](#safe-and-arm)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

**The flight termination system is the highest reliability requirement on the vehicle, and it must work when everything else has failed.** That second clause is what makes it hard: the FTS is called on precisely in the conditions that broke the vehicle.

---

## The architecture

A command-destruct FTS is a short chain and every link is doubled.

**Antennas and command receivers**, tuned to the range transmitter, which have to work through a tumbling vehicle's changing attitude and through plume attenuation.

**A dedicated FTS battery**, independent of the vehicle bus, because the vehicle bus is one of the things that may have failed. See [electricalPower](../../electricalPower/).

**A safe and arm device**, which physically interrupts the initiation path until arming and provides the positive indication that it is interrupted.

**Initiators and the destruct charge**, which is usually a linear shaped charge along the tankage. See [DestructMechanisms](DestructMechanisms.md).

**And the ground segment**: the transmitter, its redundant chain, and the console that sends the command. **14 CFR 450.145 applies the reliability requirement to the off-vehicle portion as well**, which is easy to forget when thinking about the hardware on the rocket.

---

## The requirement

**A design reliability of 0.999 at 95 per cent confidence**, for the onboard and the off-vehicle portions both.

That single pair of numbers shapes the entire subject, and it is worth understanding rather than reciting.

---

## The arithmetic that shapes the subject

With zero failures in n tests, the lower confidence bound on reliability is `(1 - C) ** (1/n)`, so the number of successful tests needed is

```
n = ln(1 - C) / ln(R)
```

| Reliability claimed | Tests needed at 95 % confidence |
|---|---|
| 0.90 | 28 |
| 0.99 | 298 |
| **0.999** | **2,994** |
| 0.9999 | 29,956 |

**Demonstrating 0.999 at 95 per cent confidence by test alone takes about three thousand successful firings of a single-use ordnance system.**

Nobody has done that and nobody will. The articles are consumed by the test, the cost is prohibitive, and a three thousand unit lot would not be the lot that flies.

**Each additional nine costs ten times the tests**, so the arithmetic gets worse rather than better as requirements tighten. A realistic thirty test programme demonstrates 0.905 at the same confidence.

---

## What is done instead

The claim is not demonstrated. **It is argued**, and the argument has four parts.

**Redundancy**, which is the largest term and is arithmetic rather than testing: two parallel paths at 0.995 each give 0.99998.

**Parts with their own qualification histories.** An initiator with a lot acceptance record behind it carries evidence a system-level test cannot produce.

**Environmental testing to margin**, which establishes that the system works outside the flight envelope rather than establishing a rate.

**And an end-to-end test of the actual flight article**, which proves the path rather than the rate: that this receiver, this battery, this safe and arm and this initiation circuit are connected and function. See [FTSTestingAndVerification](FTSTestingAndVerification.md).

**That is not a weakness in the regulation.** It is the only available answer, and the regulation's own language, "commensurate design, analysis and testing", says as much.

---

## Redundancy that is not

Two failure modes hidden by the word.

**A two out of two configuration is worse than a single path.** An initiator pair wired so that BOTH must fire to sever a charge has doubled the number of things that can stop it: at 0.995 per element, a parallel pair reaches 0.99998 and a series pair reaches 0.99003, which is below the single element.

| Configuration | Paths | Path reliability |
|---|---|---|
| Dual parallel | either works | 0.99998 |
| Triple, two of three | two of three | 0.99993 |
| Single | one | 0.99500 |
| Dual series | both must work | **0.99003** |

**And a redundant train behind a single series element is a single string system.** The dual parallel ordnance in the worked case reaches 0.99998, and putting it behind one command receiver at 0.995 takes the system to 0.99468, which fails the requirement. **The system reliability is the receiver's, not the ordnance's.**

**That is why the receivers, the batteries and the ordnance are all doubled** rather than only the visible one, and it is why the series elements are where an FTS design review should start.

---

## Safe and arm

The device that makes the system safe to be near before flight and lethal after it, and its two requirements pull opposite ways.

**It must not permit initiation before arming**, under any credible stimulus including stray radio frequency energy, static discharge and lightning. See [Pyrotechnics](../../mechanismsAndSeparation/docs/Pyrotechnics.md) for the no-fire and all-fire arithmetic, which this domain does not duplicate.

**And it must not prevent initiation after arming**, which is the reliability requirement above.

**A mechanical interrupter satisfies both** by physically breaking the explosive train, and it provides the positive position indication that a ground crew can verify. That is why it is mechanical rather than electronic: **the safety case rests on being able to see the interruption**, not on trusting a state.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Requirement | 0.999 at 95 % confidence |
| Zero-failure tests to demonstrate it | 2,994 |
| What 30 tests demonstrate | 0.905 |
| Cost per additional nine | 10x the tests |
| Dual parallel path, 0.995 elements | 0.99998 |
| Dual series path, same elements | 0.99003, worse than one |
| System with three good series elements | 0.99918, clears |
| System behind one 0.995 receiver | 0.99468, **fails** |

---

## Design rules of thumb

- **Start an FTS review at the series elements.** They are where redundancy is lost.
- **Check the wiring, not the word.** Two of two is worse than one.
- **Apply the requirement to the ground segment too.** The regulation does.
- **Expect the claim to be argued, not demonstrated.** No test programme reaches three nines.
- **Keep the safe and arm mechanical and observable.**
- **Give the FTS its own battery.** The vehicle bus is one of the things that may have failed.

---

## Failure modes

**A reliability quoted as demonstrated.** 2,994 tests, and nobody has run them.

**A two of two initiator pair called redundant.** Worse than a single one.

**A redundant train behind one receiver.** A single string system.

**The ground segment left out of the reliability case.** The regulation includes it.

**An FTS on the vehicle bus.** It fails with the thing it exists to stop.

**A safe and arm state trusted rather than observed.** The safety case needs to see the break.

---

## Tool interface

```python
from TerminationReliability import TerminationReliability

termination = TerminationReliability()
termination.setInputs({'elementReliability': 0.995,
                       'configuration':      'dualParallel',
                       'seriesElements':     {'command receiver': 0.9995,
                                              'FTS battery':      0.9998},
                       'testsAvailable':     30})

demonstration  = termination.demonstrationSize()
ladder         = termination.demonstrationLadder()
configurations = termination.compareConfigurations()
check          = termination.checkRequirement()   # raises below 450.145
```

---

## References

- 14 CFR 450.145, *Highly reliable flight safety system*
- 14 CFR Part 417 appendix D, *Flight Termination Systems, Components, Installation, and Monitoring*, not read
- RCC 319, *Flight Termination Systems Commonality Standard*, not read
- [Pyrotechnics](../../mechanismsAndSeparation/docs/Pyrotechnics.md), for the initiation margins
- [RedundancyAndFaultTolerance](../../reliabilityAndMissionAssurance/docs/RedundancyAndFaultTolerance.md), for the common cause problem this arithmetic ignores
