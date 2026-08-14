[Home](../README.md) > FTS Testing and Verification

# FTS Testing and Verification

## Contents

- [Overview](#overview)
- [What a test can establish](#what-a-test-can-establish)
- [Qualification](#qualification)
- [Lot acceptance](#lot-acceptance)
- [The end-to-end test](#the-end-to-end-test)
- [What the reliability argument is made of](#what-the-reliability-argument-is-made-of)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

The flight termination system has the most stringent reliability requirement on the vehicle and the least ability to demonstrate it. This document is about what testing can and cannot establish, and what fills the gap.

---

## What a test can establish

The distinction the whole subject rests on.

**A test can establish that a path works.** This receiver, this battery, this safe and arm, this initiator, connected as they will fly, function when commanded. That is a categorical statement about one article and it is worth a great deal.

**A test cannot establish a rate.** Demonstrating 0.999 at 95 per cent confidence needs 2,994 successful firings with no failures, and the articles are consumed by the test. See [FlightTerminationSystems](FlightTerminationSystems.md).

**So the test programme proves the path and the analysis argues the rate**, and confusing the two is the commonest error in an FTS discussion.

---

## Qualification

Establishing that the design survives its environments with margin.

**Environmental testing to levels above flight**: vibration, shock, thermal, altitude, humidity and electromagnetic. The margin is the point: a component that works at the flight level and fails just above it has no demonstrated robustness.

**Functional testing after each environment**, because the failure that matters is the one the environment caused rather than the one present at the start.

**And a life demonstration** where the component sees repeated exposure, which matters for an FTS that sits armed through a scrubbed count and then flies days later.

**Qualification articles are not flight articles.** They have been through more than a flight article ever will and they are not flown, which is what makes the testing meaningful and what makes it expensive.

---

## Lot acceptance

The evidence that this batch is like the qualified one.

**Ordnance is lot acceptance tested destructively**, because there is no non-destructive test that establishes an initiator will fire. A sample from the lot is fired and the rest of the lot inherits the result.

**That is a statistical argument on a small sample**, and it is exactly the argument [manufacturingAndAssembly](../../manufacturingAndAssembly/docs/ProcessQualification.md) makes about coupons: made the same way, from the same lot, in the same run.

**The lot is the unit of evidence**, which is why lot traceability on ordnance is absolute and why a lot change is a requalification question.

---

## The end-to-end test

The single most valuable test in the programme, and it is not a reliability test.

**The actual flight article, with the actual ground segment, commanded through the actual path**, up to but not including initiation: a simulated initiator or a resistive load in place of the ordnance.

**What it establishes** is that the receiver is tuned, the antennas are connected, the battery is in circuit, the safe and arm is wired the right way round, the polarity is correct, and the command from the range console reaches the initiation circuit.

**That list is almost entirely interface errors**, and interface errors are what integration testing catches everywhere in this repository: see [AvionicsTesting](../../avionicsAndGNC/docs/AvionicsTesting.md), where sign and scaling errors at interfaces are named as the most common finding.

**It proves the path, once.** It says nothing about the rate, and it is worth doing anyway because a wiring error is a certainty rather than a probability.

---

## What the reliability argument is made of

Four parts, in rough order of contribution.

**Redundancy**, which is arithmetic: two parallel paths at 0.995 give 0.99998. It is the largest single term and it costs nothing to demonstrate because it is a configuration rather than a measurement. **It is also where the argument is most often wrong**, through a series element or a two-of-two wiring. See [RedundancyAndFaultTolerance](../../reliabilityAndMissionAssurance/docs/RedundancyAndFaultTolerance.md).

**Parts history.** An initiator design with thousands of firings across programmes carries evidence no single programme could generate, and that is the closest thing to a demonstrated rate available.

**Environmental margin**, which converts a categorical statement about robustness into a reduced probability of an environment-induced failure.

**And the end-to-end test**, which removes the interface errors that would otherwise dominate everything else.

**Notice what is absent: a reliability trial.** The regulation's language, commensurate design, analysis and testing, is an acknowledgement that the number is argued.

---

## Design rules of thumb

- **Separate proving the path from arguing the rate.** They are different claims.
- **Test to margin, not to level.**
- **Run the end-to-end test on the flight article.** Wiring errors are certainties.
- **Keep ordnance lot traceability absolute.** The lot is the unit of evidence.
- **Check the redundancy argument for series elements.** It is where it usually fails.
- **Expect qualification articles not to fly.** That is what makes them useful.

---

## Failure modes

**An end-to-end test treated as a reliability demonstration.** It proves a path, once.

**Testing to flight level.** No demonstrated margin.

**A lot change without requalification.** The evidence was about the other lot.

**A redundancy argument with an unexamined series element.** A single string system.

**Qualification articles flown.** They have been through more than a flight article should.

---

## References

- [FlightTerminationSystems](FlightTerminationSystems.md), for the demonstration arithmetic
- [ProcessQualification](../../manufacturingAndAssembly/docs/ProcessQualification.md), for the lot argument
- [AvionicsTesting](../../avionicsAndGNC/docs/AvionicsTesting.md), for what integration testing catches
- 14 CFR 450.145, which asks for commensurate design, analysis and testing
