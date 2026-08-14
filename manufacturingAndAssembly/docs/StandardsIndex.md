[Home](../README.md) > Standards Index

# Standards Index

## Contents

- [Overview](#overview)
- [MIL-HDBK-1823A](#mil-hdbk-1823a)
- [What reading it settled](#what-reading-it-settled)
- [Wright's curve](#wrights-curve)
- [What was not read](#what-was-not-read)
- [Where the process standards live](#where-the-process-standards-live)
- [References](#references)

---

## Overview

One standard read in full for the part of it this domain uses, one origin paper for the learning curve, and a long list indexed but not read.

The reason the list is long is structural: **manufacturing standards are process standards**, and the process standards belong with the processes, which are in the ten [aerospaceMaterials](../../aerospaceMaterials/) sub-domains rather than here.

---

## MIL-HDBK-1823A

*Nondestructive Evaluation System Reliability Assessment*, 7 April 2009.

**Read for section 4.5.2.2 and appendix G**, which are the demonstration sizes and the probability of detection model.

It supplies:

- The four generalised linear model link functions: logit or log-odds, probit, complementary log-log and log-log
- The log-odds model this library uses, `log(POD/(1-POD)) = (log(a) - mu)/sigma`
- The definitions of a50, a90 and a90/95
- A minimum of 60 targeted sites for a binary hit or miss response and 40 for a quantitative one
- At least three times as many unflawed sites as flawed, for the false positive rate
- The statement that 120 binary opportunities give a significantly more precise a50, and therefore a smaller a90/95

**And two observations that are easy to miss and change how the numbers are read**, both in the next section.

---

## What reading it settled

**a90 and a90/95 are different kinds of number.** a90 is a property of the inspection: the size found nine times in ten. a90/95 is the 95 per cent confidence bound on an **estimate** of a90, so it depends on the demonstration as well as on the inspection.

**The handbook states that a90/95 has become a de facto design criterion.** Put those together and **the flaw size a programme designs to is partly a statement about how many specimens somebody paid for**, which is not how a design criterion is usually understood. The two are used interchangeably in casual discussion and they should not be.

**The recommended target sizing changed and the reason is instructive.** Targets were once spaced uniformly on a log scale; the current recommendation is uniform Cartesian spacing, **because a90/95 is the criterion and the ninetieth percentile is therefore the part of the curve worth estimating precisely.** The handbook also warns that demonstrations tend to contain too many large targets, because small ones are hard to make and the ones intended to be small often come out larger.

**Both are recorded in [ValidationReferences](ValidationReferences.md)** and asserted by a test.

---

## Wright's curve

T. P. Wright, *Factors Affecting the Cost of Airplanes*, Journal of the Aeronautical Sciences, 1936.

**Not read**, and it is a derivation rather than a standard: the cost of the nth unit is the first unit cost times n to the power log2 of the learning rate, and that either follows from the definition or it does not.

**What is not a derivation is the learning rate itself**, which is fitted to a cost history and is registered here as unvalidated. [vehicleArchitecture](../../vehicleArchitecture/docs/CostAndProducibility.md) names both the rate and a cost estimating relationship as gaps it does not fill, and this domain fills the first as an input rather than a prediction.

---

## What was not read

| Standard | Covers | Would fix |
|---|---|---|
| ASME Y14.5 | Geometric dimensioning and tolerancing | The formal basis of a tolerance stack |
| AWS D17.1 | Aerospace fusion welding | Weld procedure qualification ranges |
| AS9100 | Aerospace quality management | The production control framework |
| AS5553 | Counterfeit electronic part avoidance | The traceability requirements |
| NAS 410 | NDE personnel qualification | Who is allowed to inspect |
| ASTM E1417, E1444 | Penetrant and magnetic particle practice | The procedures behind the capability figures |
| SAE AMS specifications | Material and process specifications | Almost every process parameter here |

**ASME Y14.5 is the largest of these for this domain**, because a tolerance stack computed without its definitions is a stack of numbers whose meaning is assumed. The arithmetic here is right and the question of what a tolerance zone actually is, on a feature of size with a datum reference frame, is not addressed.

**And one that is not a standard**: a POD demonstration report for an actual procedure. That would replace every representative a50 and sigma in the library with a measured one, and it is the most tractable gap in the domain.

---

## Where the process standards live

Not an omission. The process-specific standards are indexed with the processes.

| Sub-domain | Standards indexed there |
|---|---|
| [additiveLPBF](../../aerospaceMaterials/additiveLPBF/) | NASA-STD-6030, AMS7000 series, powder specifications |
| [castingProcesses](../../aerospaceMaterials/castingProcesses/) | Casting classes and radiographic acceptance |
| [postProcessing](../../aerospaceMaterials/postProcessing/) | Peening, plating and anodising specifications |
| [extrusionHoning](../../aerospaceMaterials/extrusionHoning/) | Abrasive flow process control |
| [aerospaceMaterials](../../aerospaceMaterials/docs/StandardsIndex.md) | MMPDS and the allowables basis |
| [fluidSystems](../../fluidSystems/fluidSystemsLibrary/docs/StandardsIndex.md) | Welding, cleanliness and leak standards |

---

## References

- MIL-HDBK-1823A, *Nondestructive Evaluation System Reliability Assessment*, 7 April 2009
- T. P. Wright, *Factors Affecting the Cost of Airplanes*, 1936, not read
- ASME Y14.5, AWS D17.1, AS9100, AS5553, NAS 410, ASTM E1417 and E1444, all not read
- [ValidationReferences](ValidationReferences.md)
