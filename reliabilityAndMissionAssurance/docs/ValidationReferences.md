[Home](../README.md) > Validation References

# Validation References

The external material this domain's tools are checked against, and what they cannot check.

Kept separate from the reference lists at the foot of each document. Those are further reading; this is the material a test asserts against. The methodology is in [validation/README.md](../../validation/README.md).

| Level | Means |
|---|---|
| **Hardware** | Compared against measured or specified performance of real hardware |
| **Standard** | Reproduces a published standard or definition exactly. Catches an implementation error only |
| **Bounded** | No direct comparison, but the result is bracketed by something |
| **Unvalidated** | No external anchor. Recorded with what depends on it |

**This domain has no external anchor at all**, which is worth stating plainly at the top rather than discovering at the bottom. Nothing was read, and there is no standard whose reproduction would validate any of it.

**What can be asserted is that the arithmetic is exact and that every result the domain reports survives its tables being wrong.** That is a weaker claim than a validation and it is a stronger claim than it sounds, because this is a domain where the form of a number matters more than its value.

---

## Closed forms

- **Validation level:** Standard, and exact
- **Key findings:**
  - Series reliability is the product, checked at 100 and 1,000 items
  - Parallel reliability is one minus the product of the unreliabilities
  - The beta factor form `Q = ((1 - beta) q)^n + beta q`, with the common cause term asserted constant across unit counts
  - A beta of zero reproduces the ideal case exactly, at every unit count
  - A single unit has no common cause term, so it is never reported as better than its own element
  - An OR gate is the complement product and an AND gate is the product
  - Minimal cut sets contain no smaller cut set, asserted pairwise
  - The rare event sum exceeds the exact top event and the error is small when the events are rare
  - Criticality is severity times occurrence, and the risk priority number is that times detection
  - `n = ln(1 - C) / ln(R)` for a zero-failure demonstration

**The common cause assertion earns its place.** That the common cause term does not fall as units are added is the domain's headline result and it is pure algebra, so it is asserted at four unit counts rather than argued.

---

## What survives the tables being wrong

The useful list, because it is what the domain actually claims.

**That series reliability multiplies**, so item count is a reliability parameter. Arithmetic.

**That common cause dominates a redundant set above a couple of units**, and that reducing beta beats adding a unit. Follows from one term falling as the nth power and the other not falling at all.

**That single point failures dominate a fault tree.** Follows from a cut set of order one occurring at its own probability while an order two is a product of two small numbers.

**That the importance ranking differs from the probability ranking.** Follows from the definition of the Birnbaum measure.

**That multiplying ordinal ranks produces a sort rather than a measurement**, and that folding detection into a ranking buries the detectable catastrophes. Follows from what an ordinal scale is.

**And that a reliability number without a stated basis is a wish.** Not arithmetic at all, and the basis audit exists to make it visible rather than to prove it.

**None of those moves when the beta factors, the failure rates or the ordinal scales change.**

---

## What is not validated

Three entries in [validation/referenceCases.py](../../validation/referenceCases.py) under `UNVALIDATED`, and the third is a different kind of entry from the others.

**Beta factors and coverage** (`betaFactors`). A real beta factor is estimated from operating experience on a specific redundant configuration, and published estimates vary by a factor of several across industries and analysts. **The model is standard and its form is not in doubt; the values are.** Every absolute redundancy figure scales with them and none of the structural results does. **IEC 61508 is what would replace them with an estimation procedure**, and it was not read.

**Component failure rates** (`componentFailureRates`). Representative, and the domain declines to substitute a handbook prediction for the reasons in [ReliabilityAllocation](ReliabilityAllocation.md). **The only honest source is operating experience**, and the basis audit exists to make the difference between a number with evidence and a number without it visible rather than to hide it.

**Ordinal scales** (`ordinalScales`). These cannot be validated because there is nothing to validate them against: **an ordinal rank is a definition.** A different severity or detection scale reorders the FMECA table without anything about the design changing. **That is the point the domain makes rather than a weakness it has**, which is why criticality is reported alongside the risk priority number and why the mandatory review filter uses no arithmetic at all. **Nothing closes this entry**, and it is recorded so that the absence is deliberate rather than overlooked.

---

## Cross-domain consistency

One thing is asserted across a domain boundary rather than against a reference.

**The zero-failure demonstration arithmetic** is implemented here and in [rangeSafetyAndFTS](../../rangeSafetyAndFTS/docs/FlightTerminationSystems.md), because both need it: that domain applies it to a flight termination system and this one to a vehicle reliability target. **A test asserts the two agree** rather than letting two implementations of one formula drift.

**And the common cause model runs the other way.** rangeSafetyAndFTS computes its FTS redundancy with independent paths, which is optimistic, and says so; this domain supplies the beta factor arithmetic that would reduce every one of those gains. **Neither domain silently assumes the other's position.**

---

## What is not modelled at all

**Component failure rate prediction.** Declined, with the reasoning written down.

**Quantified human reliability analysis.** Declined, because a human error probability in a fault tree looks like the same kind of quantity as a component failure rate and is not.

**Quality systems, configuration management and problem reporting.** Process, and documented rather than modelled. **They are where most escapes actually come from**, which is the uncomfortable relationship between what this domain computes and what actually causes failures.

**Derating curves.** Component specific, and they live with the components.

**Bayesian updating of a reliability estimate.** Real and useful, and it needs a prior this repository has no basis for.

---

## The shape of what is here

**This is the domain with the weakest anchor in the repository and the results least sensitive to it**, and those two facts are the same fact.

Everything the domain concludes follows from the form of an expression rather than the value in it: a product, a power, an ordinal scale, a cut set order. **A domain whose conclusions are about form does not need a reference to be right, and it cannot use one to become more right.**

**What it cannot do is tell you the number.** Every probability in it is representative, and the honest use of the library is to run it on a programme's own rates rather than to quote its outputs. The basis audit exists so that the difference between those two uses is visible on the face of the report.
