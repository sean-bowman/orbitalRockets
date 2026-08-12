[Home](../README.md) > Standards Index

# Standards Index

## Contents

- [Overview](#overview)
- [The closed forms](#the-closed-forms)
- [What governs a reusable vehicle](#what-governs-a-reusable-vehicle)
- [Standards borrowed from aviation](#standards-borrowed-from-aviation)
- [What was not read](#what-was-not-read)
- [References](#references)

---

## Overview

**Reuse has less governing standard behind it than any other domain in this repository**, and that is a statement about the subject rather than about the research.

Expendable launch is covered by decades of standards. Reusable launch is covered by a much thinner set, because the regulatory and engineering framework was built for vehicles that fly once, and the practice is ahead of the documentation.

What this domain rests on instead is two closed forms and a set of published operational figures.

---

## The closed forms

**Allen and Eggers, NACA Report 1381, 1958.** The ballistic entry solution: the velocity profile, the peak deceleration and its independence from the ballistic coefficient, the peak heating density, and the velocity fractions at each peak. **Not a standard, and stronger than one**: it is a derivation, and it either follows or it does not.

The relations used here were read from the NASA TFAWS 2012 aerothermodynamics course notes, which teach them in the form used, rather than from the original report.

**Sutton and Graves, NASA TR R-376, 1971.** Stagnation point convective heating for arbitrary gas mixtures. The constant for Earth air is 1.7415e-4.

**Its units are quoted inconsistently and the error is four orders of magnitude.** Several sources state that the expression returns W/cm2 with SI inputs. Reproducing published entry cases shows it returns W/m2. See [ValidationReferences](ValidationReferences.md), where the convention is fixed against Stardust and Apollo rather than against the statement.

---

## What governs a reusable vehicle

Thin, and worth being explicit about.

**14 CFR Part 450**, the FAA launch and reentry licence requirements, which govern reentry vehicle operations from a US site including public safety and the reentry itself. **Not read.**

**AFSPCMAN 91-710**, the range user requirements, which apply to the launch half. **Not read**, and it is also the largest gap in [groundSystemsAndOperations](../../groundSystemsAndOperations/docs/StandardsIndex.md).

**NASA-STD-5019**, fracture control requirements, which is what a life-limited pressure vessel or a fracture critical structure is managed against. **Not read**, and it is the one whose absence most affects [LifeTrackingAndLimits](LifeTrackingAndLimits.md).

**There is no standard that says how many times a stage may fly.** That is established per programme, by demonstration and by a certification argument, and the [scatter factor](LifeTrackingAndLimits.md) convention is the closest thing to a rule.

---

## Standards borrowed from aviation

Where a reusable launch programme goes for precedent, and the borrowing has to be done carefully.

**Aviation continued airworthiness** has a mature framework for exactly this problem: life-limited parts, cycle counting, on-condition maintenance, inspection intervals and fleet leader programmes. The vocabulary this domain uses is largely aviation's.

**The mismatch is the cycle count.** An airliner flies tens of thousands of cycles and a booster flies tens, so the statistical basis that underpins aviation practice does not exist. **Aviation gets its life limits from a fleet; a launch programme gets them from one article and a scatter factor.**

**And the environment is not comparable.** A cryogenic thermal cycle, a start transient and an entry are not fatigue cycles in the aviation sense, and applying aviation intervals to them borrows a framework without its evidence.

**Borrow the framework and not the numbers** is the rule, and it is the same rule this repository applies to every borrowed table.

---

## What was not read

| Standard | Would fix |
|---|---|
| 14 CFR Part 450 | Reentry licensing and public safety requirements |
| AFSPCMAN 91-710 | Range user requirements, shared with ground systems |
| NASA-STD-5019 | Fracture control, which life tracking rests on |
| NASA-HDBK-5010 | Fracture control implementation guidance |
| NACA Report 1381 | The Allen-Eggers original, read here through course notes |
| NASA TR R-376 | The Sutton-Graves original, read here through course notes |

**The last two matter less than the others**, because the relations are derivations and they were checked by reproducing published entry cases rather than by trusting a transcription. **The Sutton-Graves units question would have been settled by the original**, and it was settled instead by two entry cases, which is arguably the better check.

**And one that is not a standard**: a published refurbishment cost breakdown from a real reusable programme. Nothing in this domain would change structurally, and every economics number would become anchored rather than representative.

---

## References

- H. J. Allen and A. J. Eggers, NACA Report 1381, 1958
- K. Sutton and R. A. Graves, NASA TR R-376, 1971
- NASA TFAWS 2012 aerothermodynamics course notes
- 14 CFR Part 450, NASA-STD-5019, AFSPCMAN 91-710, all unread
- [ValidationReferences](ValidationReferences.md)
