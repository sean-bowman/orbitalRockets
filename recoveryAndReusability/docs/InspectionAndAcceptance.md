[Home](../README.md) > Inspection and Acceptance

# Inspection and Acceptance

## Contents

- [Overview](#overview)
- [The ladder](#the-ladder)
- [What each level actually catches](#what-each-level-actually-catches)
- [Proof pressure as an inspection](#proof-pressure-as-an-inspection)
- [Disposition](#disposition)
- [Designing for inspectability](#designing-for-inspectability)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

**Reuse is an inspection problem before it is a landing problem.** This is the document that sentence points at.

The question after a flight is not whether the hardware looks all right. It is whether its condition can be established cheaply enough, and reliably enough, to fly it again.

---

## The ladder

Each level catches something the one below cannot, and the cost rises faster than the coverage.

| Level | Relative cost | Catches |
|---|---|---|
| Walkaround | 1 | visible damage and missing hardware |
| Borescope | 4 | internal surfaces without disassembly |
| Proof pressure | 12 | a flaw large enough to leak or burst |
| Non-destructive evaluation | 25 | a flaw below the proof size, where access allows |
| Teardown | 90 | everything, and it ends the article as flown |

**A spread of ninety times, and the most thorough level destroys the thing it is establishing.** That is the whole shape of the problem: the only inspection that finds everything is the one you cannot do to a flight article.

**So the question is never "inspect more".** It is "inspect what, and what will be decided on the answer", and an inspection with no disposition attached to its outcome is a cost with no product.

---

## What each level actually catches

Worth stating individually, because the levels are often treated as degrees of thoroughness rather than as different instruments.

**A walkaround finds what changed.** It is the cheapest and it catches the failures that are obvious once you look: a missing panel, a scorched line, a leg that did not lock. It is also the only level that scales to every flight.

**A borescope buys access without disassembly**, which is the expensive part of everything below it. Its value is entirely a function of whether the design provided ports, and that is a decision made years earlier.

**Non-destructive evaluation finds flaws it has access to and a technique for.** That qualifier does the work: ultrasonic inspection needs a surface and a couple of the geometry, dye penetrant needs a surface finish, radiography needs both sides. **A flaw in a location none of them reaches is not found, and the report says nothing about it.**

**Teardown finds everything and produces a set of parts.** It is what a fleet leader is for: tear down one article to learn what all of them are doing, rather than tearing down each.

---

## Proof pressure as an inspection

The one that is genuinely a measurement rather than a look, and it deserves separating.

A proof test to a defined factor above operating pressure **screens out any flaw large enough to fail at that pressure.** It is not a survey: it does not tell you where the flaws are or how large the surviving ones are. What it establishes is an upper bound on the largest surviving flaw, and that bound feeds directly into a [damage tolerance](../../aerospaceMaterials/docs/FractureAndDamageTolerance.md) life calculation.

**Two things about it are uncomfortable.**

**It is itself a load cycle**, so it consumes life to establish life. On a pressure vessel with a fracture-limited life, proof testing every flight is a real fraction of the life budget.

**And it can grow a flaw it does not fail.** A proof test that takes a subcritical flaw and extends it leaves the article in a worse state than it found it, which is the argument for proof factors being as low as they can be rather than as high as possible.

---

## Disposition

The part that is a decision rather than a measurement.

**Somebody has to decide, on the evidence, whether the article flies again.** The evidence is incomplete by construction, the decision is one-way, and the person making it is under schedule pressure. That is a governance problem and it is why disposition authority is named rather than assumed.

**Write the criteria before the inspection.** A finding assessed against criteria written afterwards is assessed against criteria written by somebody who wants to fly.

**And record the disposition, not just the finding.** A programme that keeps its inspection reports and not its dispositions has a record of what it saw and none of what it decided, which is exactly backwards for learning.

---

## Designing for inspectability

**Design for inspectability or accept teardown. There is no third option.** That is the domain's central design rule and it means specific things.

**Access ports where the borescope has to go**, decided when the structure is laid out and impossible afterwards.

**Surfaces that a technique can reach.** A weld that no ultrasonic probe can couple to is a weld that will be accepted on faith.

**Instrumentation that records the environment**, because [life tracking](LifeTrackingAndLimits.md) without a measured environment returns a nominal answer regardless of what happened.

**And life-limited parts that can be replaced without disassembling everything around them.** The refurbishment cost is dominated by access, and access is a layout decision. See [RefurbishmentProcess](RefurbishmentProcess.md).

**The Space Shuttle is the case study**, and the point is not that it was inspected too much. It is that its design made inspection expensive: tiles individually bonded and individually assessed, engines that came out for teardown, and an airframe with limited access. Fifty four days was its best ever turnaround against a two week design goal.

---

## Design rules of thumb

- **Attach a disposition to every inspection** before running it.
- **Put the access ports in when the structure is laid out.**
- **Prefer a technique that reaches over a technique that is sensitive.**
- **Keep the proof factor as low as it can be.** It is a load cycle and it can grow a flaw.
- **Tear down the fleet leader, not the fleet.**
- **Record dispositions, not just findings.**

---

## Failure modes

**Inspecting more instead of inspecting better.** Cost rises faster than coverage.

**A technique with no access.** The report is silent about what it could not reach.

**Criteria written after the finding.** Written by somebody who wants to fly.

**Proof testing every flight on a fracture-limited vessel.** Consuming the life you are establishing.

**A design with no access ports.** Every inspection becomes a disassembly.

**Findings kept and dispositions discarded.** No record of what was decided.

---

## References

- [FractureAndDamageTolerance](../../aerospaceMaterials/docs/FractureAndDamageTolerance.md), for what a proof test bounds
- [QualificationAndTesting](../../fluidSystems/fluidSystemsLibrary/docs/QualificationAndTesting.md)
- [LifeTrackingAndLimits](LifeTrackingAndLimits.md), for what the inspection feeds
- [RefurbishmentProcess](RefurbishmentProcess.md)
