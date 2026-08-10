[Home](../README.md) > Standards Index

# Standards Index

## Contents

- [Overview](#overview)
- [NASA-STD-5017B](#nasa-std-5017b)
- [The margin equation and its factors](#the-margin-equation-and-its-factors)
- [Requirements this library implements](#requirements-this-library-implements)
- [Scope limits the standard states](#scope-limits-the-standard-states)
- [The correction reading it produced](#the-correction-reading-it-produced)
- [Related standards](#related-standards)
- [What was not read](#what-was-not-read)
- [References](#references)

---

## Overview

This domain has one governing standard and it is unusually complete. Most of what this library computes comes directly out of it, which makes this document longer than a standards index usually is.

---

## NASA-STD-5017B

*Design and Development Requirements for Mechanisms*, approved 06 December 2022, superseding NASA-STD-5017A.

It covers mechanism design, torque and force margins, clearances, lubrication, bearings, fasteners, status indication and structural requirements, in about 126 pages of requirements each with a stated rationale and guidance.

**It was read directly** from the standard rather than through a summary, and [the correction that produced](#the-correction-reading-it-produced) is the strongest argument in this repository for doing so.

---

## The margin equation and its factors

```
torque margin = T_avail / (sum FSf Tf + sum FSv Tv + sum FSa Ta) - 1        (Equation 4-1)
```

`T_avail` is the minimum available torque from the driving or holding component, understood to include magnetic losses such as hysteresis and eddy current drag, mechanical losses such as bearing, brush and windage drag, and torque ripple from cogging and commutation.

`Tv` are the individual maximum **variable** resisting torques, whose values change with environmental conditions and cycles: friction, viscous drag, wire harness torque from flexing or set.

`Tf` are the individual maximum **fixed** resisting torques, not strongly influenced by environment or cycles: bearing drag, vehicle manoeuvre-induced torques, return springs, unbalanced pressure loads limited by relief mechanisms.

`Ta` is the torque required to achieve a specified acceleration.

**Table 1, minimum safety factors:**

| Source of torque data | FSv | FSf | FSa |
|---|---|---|---|
| Theory or analysis | 3.00 | 1.50 | 1.25 |
| Development test at expected environmental extremes | 2.50 | 1.35 | 1.15 |
| Qualification test | 2.50 | 1.35 | 1.15 |
| Lot acceptance test at expected environmental extremes | 2.50 | 1.35 | 1.15 |
| Acceptance test of flight hardware at ambient conditions | 2.50 | 1.35 | 1.15 |
| Acceptance test of flight hardware at expected environmental extremes | 2.00 | 1.25 | 1.10 |
| Test evaluation of one-spring-out case | 1.00 | 1.00 | 1.00 |

The one-spring-out row applies **only** to mechanisms using multiple springs in parallel for redundancy, evaluated after one has failed. The standard explicitly distinguishes this from a single spring designed to tolerate partial failure, where it does not apply.

The standard also notes the analysis factors are **not** to be treated as no-test design factors: verifying margins by test is required regardless.

---

## Requirements this library implements

| Requirement | Content |
|---|---|
| DDMR 9 | Torque margin applied under worst-case conditions throughout life, including life testing |
| DDMR 10 | Torque multipliers meet margin at **both** input and output |
| DDMR 11 | All torque margins verified during acceptance test at the highest possible level of assembly |
| DDMR 12 | Static torque margin greater than zero within the full range of motion |
| DDMR 13 | Dynamic torque margin greater than zero |
| DDMR 14 | Holding torque margin greater than zero at the specified positions |
| DDMR 26 | Direct indication of the critical states of each mechanism |
| DDMR 29 | Remains functional after exposure to stall at any point in travel |
| DDMR 30 | Non-jamming mechanical stops where over-travel would be detrimental |
| DDMR 31 | Positive margin with full design factors under worst-case stop impact loads |

Table 3 of the standard gives allowable mean Hertzian contact stress for bearing materials under non-operational yield design loads, and those are carried in [TribologyAndLubrication](TribologyAndLubrication.md).

---

## Scope limits the standard states

Two are worth quoting because they change what this library does.

**Torque margin does not apply to mechanisms that must provide a specific value within a narrow tolerance** rather than a minimum. The standard names a spring holding a relief valve closed, and **an ejection mechanism requiring a specific separation velocity**, as examples.

That second example is exactly the [SeparationSystem](SeparationSystems.md) case, which is why that class computes velocities and clearances rather than margins. A margin applied there would be answering a question the standard says not to ask.

**For holding margin, the available torque is the intentional holding torque only.** The standard excludes incidental, unreliable and uncharacterised contributors such as joint friction, harness bending and blanket rubbing. That is the opposite of what a conservative analyst might assume, and it means a mechanism held only by friction has no holding capability at all as far as the standard is concerned.

---

## The correction reading it produced

A web search summary of this standard reported that **an operating torque margin of 1.0 or greater is required**.

The standard says: *the required reserve torque is included in the equation in the form of the safety factors, so a torque margin greater than or equal to zero indicates that requirements are met.*

**The threshold is zero, not one.**

Building this library on the summary would have made every mechanism in it appear twice as marginal as it is, and would have driven hardware changes to correct a problem that does not exist. The correction is carried in [validation/referenceCases.py](../../validation/referenceCases.py) with the standard's own wording, and a test asserts it.

This is the clearest instance in this repository of a primary source paying for itself on first reading, and it is worth generalising: **a summary of a standard is a secondary source about a document that exists and is obtainable**, which is a much weaker position than a summary of an experiment.

---

## Related standards

**NASA-STD-6016**, *Standard Materials and Processes Requirements for Spacecraft*. NASA-STD-5017B treats lubrication as a process subject to this standard. Not read.

**NASA-STD-5001**, *Structural Design and Test Factors of Safety for Spaceflight Hardware*. Referenced by 5017B when distinguishing its analysis factors from structural design factors. Not read.

**ANSI/ABMA** bearing standards, for the ABEC tolerance classes and ball grades 5017B requires. Not read.

**MIL-STD-1576**, *Electroexplosive Subsystem Safety Requirements and Test Methods for Space Systems*. The governing document for the [pyrotechnic](Pyrotechnics.md) practice this library describes qualitatively. **Not read**, and the no-fire and all-fire conventions used here come from general practice rather than from it.

---

## What was not read

Recorded explicitly, on the same principle as the rest of the repository.

**MIL-STD-1576**, which would put the initiator margins on the same footing as the torque margins. This is the largest closable gap in the domain.

**Any manufacturer data sheet** for a non-explosive actuator, which is why [none of them is sized](NonExplosiveActuators.md).

**Any pyroshock test report**, which is why [the shock is not predicted](Pyrotechnics.md).

---

## References

- NASA-STD-5017B, *Design and Development Requirements for Mechanisms*, 06 December 2022
- [ValidationReferences](ValidationReferences.md)
- Conley, *Space Vehicle Mechanisms: Elements of Successful Design*
