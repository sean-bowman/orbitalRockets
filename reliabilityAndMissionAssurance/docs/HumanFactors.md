[Home](../README.md) > Human Factors

# Human Factors

## Contents

- [Overview](#overview)
- [The failure mode that is a person](#the-failure-mode-that-is-a-person)
- [Error-proofing](#error-proofing)
- [Procedure design](#procedure-design)
- [Verification](#verification)
- [Why quantifying it is hard](#why-quantifying-it-is-hard)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

**Most failures are not random. They are design escapes, process escapes, or human error.** This is the third one, and it is treated here as a design problem rather than a people problem.

---

## The failure mode that is a person

The framing decides what gets fixed.

**"Operator error" is not a root cause.** It ends an investigation exactly where it should start, and the questions it forecloses are the useful ones: why was the error possible, why was it not caught, and what about the design or the procedure permitted it. See [ProblemReporting](ProblemReporting.md).

**A person who can make a mistake will eventually make it**, given enough repetitions, enough fatigue and enough schedule pressure. That is not a character judgement; it is a rate.

**So the design question is not how to make people not make mistakes.** It is how to make the mistake impossible, or harmless, or immediately visible. **All three are design decisions and none of them is training.**

**Training is the weakest of the available responses** and it is the one most often chosen, for the same reason improved detection is the weakest [FMECA](FMECA.md) action and the one most often chosen: it is the cheapest and it requires nothing of the design.

---

## Error-proofing

Making the wrong action impossible, in descending order of how well it works.

**Make it physically impossible.** Connectors that only mate one way, fasteners that will not fit the wrong hole, a fitting whose thread does not match the wrong fluid. **This is the only response that works when everything else has gone wrong**, and it costs almost nothing at design time and a great deal afterwards.

**Make it obvious.** Colour, labelling, orientation and asymmetry. Weaker, because it depends on somebody looking, and it degrades under time pressure exactly when it is needed.

**Make it detectable.** A check, an interlock, an instrumented verification. It does not prevent the error, it catches it, and it works only if somebody acts on the catch.

**And make it harmless.** A design where the wrong action does not cause a failure is better than one where it is prevented, because prevention can be defeated and harmlessness cannot.

**The recurring theme is that the earlier the response, the cheaper and the more effective**, which is the same shape as [design for inspectability](../../recoveryAndReusability/docs/InspectionAndAcceptance.md) and [design for manufacture](../../manufacturingAndAssembly/docs/ManufacturingOverview.md).

---

## Procedure design

**A procedure that cannot be followed under pressure will not be followed under pressure.** That is [groundSystemsAndOperations](../../groundSystemsAndOperations/docs/HazardousOperations.md)'s rule and it applies to every procedure on the programme.

Six things that make one followable.

**Written in the order things are done**, not in the order they were designed.

**One action per step.** A step containing three actions gets two of them.

**Verification in line**, not in a block at the end. A check performed twenty steps after the action it verifies is a check on somebody's memory.

**Branches for the failures that are expected**, because the ones that are worked out during the event are worked out by tired people.

**A place to record what was actually done**, because the difference between the procedure and the execution is the record an investigation needs.

**And short enough to hold.** A procedure that runs to hundreds of steps will be sampled rather than followed, and knowing which parts get sampled is worth more than pretending it does not happen.

---

## Verification

Two controls that look similar and defend against different things, which [groundSystemsAndOperations](../../groundSystemsAndOperations/docs/HazardousOperations.md) also works through.

**Two-person control** means no single person can complete a hazardous action alone. It defends against a single mistaken or deliberate act.

**Independent verification** means a second person checks a completed configuration against the procedure, without having watched it being set.

**The second catches more and is skipped more often.** The common failure is not one person doing something wrong; it is **two people believing the same wrong thing about a valve position**, and two-person control does nothing about that because both people share the belief.

---

## Why quantifying it is hard

Stated because human reliability analysis exists and this domain does not implement it.

**The methods produce numbers** with error probabilities per action type, adjusted by performance shaping factors for stress, time pressure, training and interface quality.

**The uncertainty on those numbers is very large**, frequently an order of magnitude, and the performance shaping factors are judgements rather than measurements.

**And a number invites a comparison it cannot support**: putting a human error probability alongside a component failure rate in a [fault tree](FaultTreeAnalysis.md) makes them look like the same kind of quantity, and they are not.

**So this domain documents the design responses rather than putting a probability on a person.** The responses are actionable and the probability is not, which is the same reasoning that keeps [component failure rate prediction](ReliabilityAllocation.md) out of the library.

---

## Design rules of thumb

- **Never stop a root cause at a person.**
- **Prefer physically impossible to obvious to detectable to harmless**, in that order of design effort.
- **Treat training as the weakest response**, not the default one.
- **Write procedures in execution order, one action per step.**
- **Put verification in line**, not at the end.
- **Use independent verification, not just two-person control.**
- **Assume a long procedure will be sampled.**

---

## Failure modes

**Operator error recorded as a root cause.** The investigation stopped at the start.

**Training as the corrective action.** Nothing about the design changed.

**A connector that can mate two ways.** It eventually will.

**A verification block at the end of a procedure.** A check on memory.

**Two-person control substituted for independent verification.** The shared belief survives both.

**A three hundred step procedure.** It will be sampled and nobody will say which parts.

---

## References

- [HazardousOperations](../../groundSystemsAndOperations/docs/HazardousOperations.md), for procedure design and the two verification controls
- [ProblemReporting](ProblemReporting.md), for why a person is not a root cause
- [QualityAndProcessControl](QualityAndProcessControl.md), for where human error sits among the escapes
- [FMECA](FMECA.md), for the same ordering of response strength
