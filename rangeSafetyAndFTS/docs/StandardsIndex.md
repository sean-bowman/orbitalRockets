[Home](../README.md) > Standards Index

# Standards Index

## Contents

- [Overview](#overview)
- [14 CFR Part 450](#14-cfr-part-450)
- [What reading it settled](#what-reading-it-settled)
- [The range documents](#the-range-documents)
- [What was not read](#what-was-not-read)
- [References](#references)

---

## Overview

This is the domain where the governing documents are the substance rather than a reference, so the index matters more here than anywhere else in the repository.

**One regulation was read and it is the one the licence rests on.** The range documents are indexed and not read, and that is the honest position rather than a satisfactory one.

---

## 14 CFR Part 450

*Launch and Reentry License Requirements*, the FAA regulation that licenses any commercial launch or reentry from a US site or by a US entity.

**Read for section 450.101 and section 450.145**, which are the launch safety criteria and the highly reliable flight safety system.

450.101 supplies:

- Collective risk to the public, **1e-4 expected casualties**
- Collective risk to neighbouring operations personnel, **2e-4**
- Individual risk to the public, **1e-6 probability of casualty per launch**
- Individual risk to neighbouring operations personnel, **1e-5**
- Aircraft, **1e-6 probability of impact with debris capable of causing a casualty**

450.145 supplies:

- **A design reliability of 0.999 at 95 per cent confidence**, for the onboard and off-vehicle portions both
- The requirement for commensurate design, analysis and testing
- The obligation to monitor the flight environments the components experience

**Both are duplicated into [validation/referenceCases.py](../../validation/referenceCases.py)** and asserted against the library by a test.

---

## What reading it settled

**Collective and individual risk are separate tests and both apply.** That is not obvious from a summary, and it changes what a risk analysis has to do: a launch can meet the collective criterion by spreading a small risk thinly and still fail the individual one for the person nearest the trajectory. **The individual limit exists to stop exactly that trade.**

**The neighbouring operations personnel limits are looser by exactly a factor of two on the collective side and ten on the individual side**, which is the regulation distinguishing people who chose to be there from people who did not. That factor is a policy statement rather than an engineering one and it is worth seeing.

**Aircraft are excluded from the collective casualty expectation and given a probability of impact criterion instead**, which is a stricter and simpler test: an aircraft struck by debris is assumed lost rather than assessed for casualties.

**And the reliability requirement applies to the off-vehicle portion.** The ground transmitter chain carries the same 0.999 at 95 per cent as the hardware on the rocket, which is easy to miss when thinking about an FTS as vehicle hardware.

---

## The range documents

Indexed and not read, and they are where the implementation detail lives.

**AFSPCMAN 91-710**, *Range Safety User Requirements*, which governs operations at the Eastern and Western Ranges. **Not read**, and it is also the largest gap in [groundSystemsAndOperations](../../groundSystemsAndOperations/docs/StandardsIndex.md), so its absence touches two domains.

**RCC 319**, the Range Commanders Council flight termination system commonality standard, which codifies the FTS component and design requirements the ranges apply. **Not read.** It is the document that would turn most of [FlightTerminationSystems](FlightTerminationSystems.md) from practice into requirement.

**RCC 321**, *Common Risk Criteria Standards for National Test Ranges*, which is the range equivalent of the Part 450 criteria. **Not read.**

**14 CFR Part 417 appendix D**, *Flight Termination Systems, Components, Installation, and Monitoring*, which is the legacy prescriptive FTS appendix that Part 450 replaced for new licences and which is still the most detailed public description of what an FTS has to be. **Not read.**

---

## What was not read

| Document | Would fix |
|---|---|
| AFSPCMAN 91-710 | Range user requirements, shared with ground systems |
| RCC 319 | FTS component and design requirements in detail |
| RCC 321 | The range risk criteria alongside the FAA ones |
| 14 CFR Part 417 appendix D | The prescriptive FTS description |
| 14 CFR 450.135 | Debris risk analysis, read only in summary |
| FAA AC 450.123-1 | Population exposure assessment method |

**RCC 319 is the largest of these for this domain**, because the FTS material here is practice-based and that document is the requirement. **AC 450.123-1 is the most tractable**, because it is the method behind the population data that drives the whole risk analysis, and it is public.

**And one that is not a document**: a debris catalogue and break-up model. That is the largest single piece of unbuilt work implied by this repository, and it is what would turn the impact probabilities from representative into derived. See [DebrisAndBlast](DebrisAndBlast.md).

---

## References

- 14 CFR Part 450, sections 450.101 and 450.145, read
- 14 CFR 450.135 and Part 417 appendix D, not read
- AFSPCMAN 91-710, RCC 319 and RCC 321, not read
- FAA AC 450.123-1, *Population Exposure Assessment*, not read
- [ValidationReferences](ValidationReferences.md)
