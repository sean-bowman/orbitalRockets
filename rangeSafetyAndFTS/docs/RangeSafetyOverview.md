[Home](../README.md) > Range Safety Overview

# Range Safety Overview

## Contents

- [Overview](#overview)
- [What this domain found](#what-this-domain-found)
- [The three questions](#the-three-questions)
- [What is computed and what is not](#what-is-computed-and-what-is-not)
- [Document index](#document-index)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Range safety is the constraint that does not negotiate. This domain covers the flight termination system, the trajectory limits it enforces, the public risk analysis that sets them, and the regulatory framework the whole thing sits inside.

**The governing documents are the substance here**, more than in any other domain in this repository. What is computed is the arithmetic underneath them.

---

## What this domain found

**The instantaneous impact point accelerates and then ceases to exist.** It crawls downrange early in an ascent and sprints late, growing by roughly fifty times in drift rate across the worked case. And at orbital insertion the free-flight perigee rises above the surface, the trajectory no longer intersects the Earth, and there is no impact point at all. **That is the natural end of the range safety flight phase** and the class raises rather than returning a large number. See [TrajectoryLimitsAndIIP](TrajectoryLimitsAndIIP.md).

**Risk follows population, not impact probability.** In the worked case the ocean takes 82 per cent of the debris and contributes 1 per cent of the casualty expectation, while one coastal town takes 0.08 per cent of the debris and contributes 88 per cent of the risk. **A range safety analysis is a population analysis with a trajectory attached**, and the azimuth that minimises risk minimises overflown people rather than overflown distance. See [PublicRiskAnalysis](PublicRiskAnalysis.md).

**The individual criterion binds a coastal site, not the collective one.** Collective risk can be met by spreading a small number thinly over many people; individual risk cannot, and that is exactly what it exists to prevent. Both tests apply and they catch different failures.

**And the reliability requirement cannot be demonstrated.** 14 CFR 450.145 asks for 0.999 at 95 per cent confidence, which by zero-failure test alone is **2,994 successful firings of a single-use ordnance system.** Thirty tests demonstrate 0.905. The claim is argued from design rather than demonstrated by test, and knowing that arithmetic is the difference between understanding the requirement and reciting it. See [FlightTerminationSystems](FlightTerminationSystems.md).

**A redundant ordnance train behind a single command receiver is a single string system**, and a two-out-of-two initiator pair is worse than one initiator. The word redundant does not distinguish between the wirings and the arithmetic does.

---

## The three questions

Range safety asks the same three questions of every launch, in order.

**Where would the debris go?** A trajectory question, answered by the instantaneous impact point.

**What would that cost?** A population question, answered by casualty expectation against a regulatory limit.

**And can the vehicle be stopped?** A system question, answered by a reliability argument that no test programme can close.

**Only the first is about the vehicle**, which is the thing worth carrying out of this domain.

---

## What is computed and what is not

| Built | Why nothing else does it |
|---|---|
| `ImpactPoint` | A Keplerian free-flight solution; no other domain propagates a trajectory |
| `PublicRisk` | No other domain has a population in it |
| `TerminationReliability` | The zero-failure arithmetic that shapes the FTS requirement |

| Not built | Where it lives, or why not |
|---|---|
| Debris catalogues and fragment ballistics | A break-up model and a Monte Carlo; [EntryTrajectory](../../recoveryAndReusability/docs/EntryAerodynamics.md) does one body |
| Blast overpressure and quantity-distance | [HazardSiting](../../groundSystemsAndOperations/docs/HazardZonesAndSiting.md), read from DESR 6055.09 |
| Toxic dispersion | Needs a dispersion model this repository does not carry |
| Ordnance initiation | [PyrotechnicInitiator](../../mechanismsAndSeparation/docs/Pyrotechnics.md) |
| Autonomous FTS rule sets | Mission specific, and their verification is [software assurance](../../avionicsAndGNC/docs/SoftwareAssurance.md) |
| The licensing process | A regulatory workflow, documented rather than modelled |

---

## Document index

| Document | Covers |
|---|---|
| [TrajectoryLimitsAndIIP](TrajectoryLimitsAndIIP.md) | The impact point, why it accelerates, destruct lines and gates |
| [PublicRiskAnalysis](PublicRiskAnalysis.md) | Casualty expectation, the two criteria, what actually drives risk |
| [FlightTerminationSystems](FlightTerminationSystems.md) | Architecture, the demonstration arithmetic, redundancy that is not |
| [AutonomousFTS](AutonomousFTS.md) | Moving the decision onboard, rule sets, and what it does not remove |
| [DestructMechanisms](DestructMechanisms.md) | Linear shaped charge, thrust termination, what termination achieves |
| [DebrisAndBlast](DebrisAndBlast.md) | Fragment ballistics, the dispersion problem, blast and toxic |
| [HazardAreasAndClearing](HazardAreasAndClearing.md) | Ground hazard zones, ship and aircraft exclusion, clearing |
| [RegulatoryFramework](RegulatoryFramework.md) | Part 450, the licensing flow, and what an applicant actually submits |
| [FTSTestingAndVerification](FTSTestingAndVerification.md) | Qualification, end-to-end test, and what a test can establish |
| [StandardsIndex](StandardsIndex.md) | One regulation read, and the range documents indexed |
| [ValidationReferences](ValidationReferences.md) | The criteria, the arithmetic, and two gaps |

---

## Design rules of thumb

- **The FTS is the highest reliability requirement on the vehicle**, and it must work when everything else has failed.
- **Public risk is a quantified, regulated number.** It is not a judgement call.
- **The launch azimuth and the trajectory are shaped by range safety before they are shaped by performance.**
- **An autonomous FTS moves the decision onboard**; it does not remove the requirement to justify it.
- **Range safety requirements are known early.** Designing around them late is expensive.
- **Size the destruct lines on the fastest part of the ascent**, not the average.

---

## Failure modes

**A destruct line sized on an early drift rate.** The impact point accelerates by tens of times.

**An impact point expected to exist through insertion.** It does not, and that is physical.

**Risk minimised by minimising overflown distance.** Risk follows population.

**Only the collective criterion checked.** The individual one is usually the tighter.

**An FTS reliability quoted as demonstrated.** No test programme reaches three nines.

**A redundant ordnance train behind one receiver.** A single string system with a redundant part.

---

## References

- 14 CFR Part 450, *Launch and Reentry License Requirements*, sections 450.101 and 450.145
- AFSPCMAN 91-710 and RCC 319, indexed and not read
- [ValidationReferences](ValidationReferences.md)
