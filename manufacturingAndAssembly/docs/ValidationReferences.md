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

**This domain's anchor covers the model and not the numbers**, which is an unusual split and worth stating first. The probability of detection model and the demonstration sizes are the standard and are exact. The a50 and sigma values put into the model are representative and are registered as unvalidated.

---

## MIL-HDBK-1823A

- **Source:** MIL-HDBK-1823A, *Nondestructive Evaluation System Reliability Assessment*, 7 April 2009. Section 4.5.2.2 for the demonstration sizes, appendix G for the model
- **Validation level:** Standard
- **Relevance:** Every probability of detection this domain computes
- **Key findings:**
  - The log-odds link, `log(POD/(1-POD)) = (log(a) - mu)/sigma`, one of four the handbook lists alongside probit, complementary log-log and log-log
  - a50, a90 and a90/95 defined separately
  - Because the logit of 0.9 is log 9, `a90/a50 = 9 ** sigma` exactly
  - Minimum 60 targeted sites for a binary response, 40 for a quantitative one
  - At least three unflawed sites per flawed site, for the false positive rate
  - 120 binary opportunities give a significantly more precise a50 and a smaller a90/95

**All of those are duplicated into [validation/referenceCases.py](../../validation/referenceCases.py) and asserted against the library by a test.** They are separate files on purpose: a library edited without the register is a library that has quietly stopped citing anything.

---

## What reading it settled

**a90 and a90/95 are different kinds of number and are used interchangeably.**

a90 is a property of the inspection. a90/95 is the 95 per cent confidence bound on an estimate of a90, which means **it falls as the demonstration grows, for the same technique.** The handbook states that a90/95 has become a de facto design criterion.

Together those say something uncomfortable: **the flaw size a programme designs to is partly a statement about how many specimens somebody paid for.** A programme that ran the 60 target minimum and one that ran 120 will design to different numbers with the same inspection.

**The recommended target sizing also changed, and the reason is the criterion.** Uniform Cartesian spacing replaced uniform log spacing because a90/95 is what gets designed to, so the ninetieth percentile is the part of the curve worth estimating precisely. The handbook separately warns that demonstrations contain too many large targets, because small ones are hard to make.

**Neither of those would have come from a summary**, and both change how a capability figure should be read. This is the third time in this repository that reading a standard rather than a summary changed something, after NASA-STD-5017B in [mechanismsAndSeparation](../../mechanismsAndSeparation/docs/ValidationReferences.md) and DESR 6055.09 in [groundSystemsAndOperations](../../groundSystemsAndOperations/docs/ValidationReferences.md).

---

## Closed forms

- **Validation level:** Standard, and exact
- **Key findings:**
  - `POD(a50) = 0.5` exactly, and `podSize` inverts `logOddsPod` to machine precision
  - `a90/a50 = 9 ** sigma` exactly, asserted against the model rather than tabulated
  - The worst case stack is the arithmetic sum and the statistical stack the quadrature sum
  - Both sets of contributor shares sum to one
  - **The sigma crossover is exactly the square root of the count for equal contributors**, asserted at 2, 4, 6, 9, 16 and 25
  - The three sigma reject fraction is 2,700 parts per million, one assembly in 370
  - Wright's exponent is `log2(rate)`, checked at 0.5 and 1.0
  - Every doubling costs exactly the learning rate times the previous doubling
  - Capacity is linear in shifts

**The crossover assertion earns its place.** It is the domain's headline result, it is pure algebra, and it contradicts the reason the statistical method is normally reached for.

---

## What is not validated

Three entries in [validation/referenceCases.py](../../validation/referenceCases.py) under `UNVALIDATED`, and each names what survives it.

**Inspection capability** (`inspectionCapability`). The a50 and sigma values are representative of a method rather than of a qualified procedure, and the handbook is emphatic that geometry, material, surface finish and access all move them. Every absolute flaw size scales with them, and so does the verdict on a given part. **The structural results do not**: that `a90/a50` is nine to the power sigma follows from the logit of 0.9; that an inspection whose reliably detectable size exceeds the critical flaw establishes nothing follows from the definitions of both; and that the ranking by a90 is not the ranking by usefulness follows from what each method cannot reach. **A POD demonstration report closes this and is the most tractable gap here.**

**Learning rates** (`learningRates`). Representative by process class rather than fitted to a cost history. Every cost figure scales with them. **The structural results do not**: Wright's law, the falling absolute saving per doubling, and the cumulative average lagging the unit cost. **The ordering is also structural**, because the more labour a process carries the more there is to learn.

**Process tolerances and cycle times** (`processTolerances`). Representative. The absolute stack and the absolute capacity scale with them; the crossover algebra and the bottleneck arithmetic do not. **The tolerance ordering is textbook and is not in doubt**; the values are shop data that nobody publishes.

---

## What is not modelled at all

**Process physics.** Taylor tool life, chatter lobes, springback, forming limits, solidification, weld knockdowns and abrasive flow all live in the ten [aerospaceMaterials](../../aerospaceMaterials/) sub-domains. A second implementation here would be the same equations with a different import path.

**Weld distortion.** Named in [WeldingAndJoining](WeldingAndJoining.md) as a real manufacturing problem and not computed. It needs a thermal-mechanical analysis of the weld and its restraint.

**Critical flaw size.** `DamageTolerance` in aerospaceMaterials computes it; this domain consumes it and asks whether the inspection can see it.

**Cost estimating relationships.** [vehicleArchitecture](../../vehicleArchitecture/docs/CostAndProducibility.md) names this as a gap and it remains one. The learning curve here takes a first unit cost as an input rather than predicting one.

**Geometric dimensioning and tolerancing semantics.** The stack arithmetic is right and ASME Y14.5 was not read, so what a tolerance zone means on a feature of size with a datum reference frame is assumed rather than established.

**Supplier qualification and counterfeit control.** Governance, documented rather than modelled.

---

## The shape of what is here

**What the domain concludes rests on algebra.** The crossover is a sum over a quadrature sum. The ratio of a90 to a50 is nine to the power sigma. Capacity is a minimum rather than a sum. Every doubling costs a fixed fraction. None of those moves when the representative tables do.

**What it reports rests on tables a real shop would replace from its own records**, and all three are registered.

**And what it documents rests on process standards that live with the processes**, which is not an omission: this domain is the cross-cutting view and the ten sub-domains carry the depth.
