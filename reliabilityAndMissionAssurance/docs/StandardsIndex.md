[Home](../README.md) > Standards Index

# Standards Index

## Contents

- [Overview](#overview)
- [Why the list is thin](#why-the-list-is-thin)
- [The method standards](#the-method-standards)
- [The quality standards](#the-quality-standards)
- [What was deliberately not implemented](#what-was-deliberately-not-implemented)
- [What was not read](#what-was-not-read)
- [References](#references)

---

## Overview

**Nothing in this domain was read**, which is the honest position and is unusual in this repository. Everything here is either arithmetic or practice.

---

## Why the list is thin

Two reasons, and the second is the interesting one.

**The methods are older than the standards that describe them.** A fault tree, a series product and a beta factor model are mathematics; the standards describe how to apply them and in what format to report them, and neither changes the arithmetic.

**And the numbers the standards supply are the ones this domain declines to use.** MIL-HDBK-217 is the canonical parts count prediction handbook and implementing it would put a number with a long documented history of being optimistic into a library where it would carry more authority than it earns. See [ReliabilityAllocation](ReliabilityAllocation.md).

**So the domain rests on arithmetic that is exact, tables that are representative and registered as such, and practice that is documented.** There is no standard whose reproduction would validate any of it, and saying so is more useful than indexing documents that would not.

---

## The method standards

**MIL-STD-1629A**, *Procedures for Performing a Failure Mode, Effects and Criticality Analysis*. The origin of the FMECA format and of the criticality ranking, including the severity classification this library uses. **Not read.**

**NUREG-0492**, the *Fault Tree Handbook*, which is the standard reference for cut set enumeration and quantification. **Not read**, and the cut set algorithm here is the textbook one: an OR gate's cut sets are the union of its inputs', an AND gate's are the cross product, and non-minimal sets are removed.

**IEC 61508**, *Functional Safety of Electrical, Electronic and Programmable Electronic Safety-related Systems*, which is where the beta factor estimation methods and the safety integrity levels live. **Not read**, and it is the largest gap for this domain: the beta factors here are representative and it is the document that would replace them with an estimation procedure.

**MIL-HDBK-217**, *Reliability Prediction of Electronic Equipment*. **Not read, and deliberately not implemented.** See below.

---

## The quality standards

**AS9100**, aerospace quality management, which is the framework behind [QualityAndProcessControl](QualityAndProcessControl.md) and [ConfigurationManagement](ConfigurationManagement.md). **Not read**, and it is a framework rather than a method: it says what a system must have and not how to compute anything.

**NASA-STD-8729.1**, the NASA reliability and maintainability handbook, and **NPR 8705.2**, human-rating requirements, both of which carry fault tolerance requirements expressed as one-fault or two-fault tolerance. **Neither read.**

**ANSI/AIAA S-102**, the space systems performance-based reliability standard series. **Not read.**

---

## What was deliberately not implemented

Worth separating from what was not read, because the reasoning is different.

**MIL-HDBK-217 style parts count prediction.** Four reasons, in [ReliabilityAllocation](ReliabilityAllocation.md): the data is old, it predicts random failures where most failures are escapes, it is optimistic in a specific and known way, and **a prediction carries an authority its basis does not support.** Implementing it here would produce numbers that look like measurements.

**Quantified human reliability analysis.** The methods exist and their uncertainty is frequently an order of magnitude, and **putting a human error probability into a fault tree alongside a component failure rate makes them look like the same kind of quantity.** [HumanFactors](HumanFactors.md) documents the design responses instead, because those are actionable and a probability is not.

**Both are declines rather than omissions**, and the reasoning is written down so the decision can be revisited rather than rediscovered.

---

## What was not read

| Standard | Covers | Would fix |
|---|---|---|
| IEC 61508 | Functional safety, beta factor estimation | The beta factors, currently representative |
| MIL-STD-1629A | FMECA procedure and criticality | The severity and criticality conventions |
| NUREG-0492 | Fault tree handbook | The cut set and quantification conventions |
| AS9100 | Aerospace quality management | The quality system framework |
| NASA-STD-8729.1 | Reliability and maintainability | The NASA practice |
| NPR 8705.2 | Human-rating requirements | Fault tolerance levels |
| ANSI/AIAA S-102 | Performance-based reliability | The reporting framework |

**IEC 61508 is the largest gap**, because the beta factor is the domain's central quantity and that document carries the method for estimating it rather than a table of values.

**And one that is not a standard**: operating experience. Every failure rate in this library is representative, and the only honest source for a real one is a population of components that have been used. That is the gap the domain says out loud rather than filling with a handbook.

---

## References

- IEC 61508, MIL-STD-1629A, NUREG-0492, AS9100, NASA-STD-8729.1, NPR 8705.2, ANSI/AIAA S-102, all not read
- MIL-HDBK-217, not read and deliberately not implemented
- [ValidationReferences](ValidationReferences.md)
