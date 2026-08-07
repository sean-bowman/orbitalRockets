[Home](../README.md) > Acceptance and Flight Screening

# Acceptance and Flight Screening

## Contents

- [Overview](#overview)
- [What acceptance is for](#what-acceptance-is-for)
- [The acceptance test procedure](#the-acceptance-test-procedure)
- [What acceptance must not do](#what-acceptance-must-not-do)
- [Workmanship screening](#workmanship-screening)
- [Baseline data](#baseline-data)
- [Disposition](#disposition)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Acceptance testing answers one question: **was this specific article built to the qualified design?** It is not asking whether the design is good. Qualification established that, on other articles, and re-establishing it on every unit would consume the fleet.

Every flight article goes through it, so the constraints are different from qualification in every respect: levels are lower, tests are non-destructive, the procedure is fixed, and the throughput matters.

---

## What acceptance is for

Two purposes, and they are different.

**Conformance.** The article matches the drawing, the process and the qualified configuration. Verified by inspection and by functional test against the qualification baseline.

**Workmanship screening.** Latent manufacturing defects are precipitated into detectable failures before flight. This is why acceptance includes environmental exposure at all: a cold solder joint, a marginal weld, a contaminated seal or a loose fastener that would survive a bench test will surface under vibration and thermal cycling.

**The screen is the reason acceptance is not just inspection.** Inspection finds what it looks for; a workmanship screen finds what nobody thought to look for.

---

## The acceptance test procedure

Every flight article, in this order:

| Step | Purpose |
|---|---|
| Dimensional inspection | The article is what the drawing says |
| Cleanliness verification | To the specified level, before assembly onto anything |
| **Proof pressure** | Strength with no permanent set |
| **Leak test** | Immediately after proof, which can open a marginal joint |
| Functional test, ambient | Stroke, timing, setpoint, response |
| **Flow calibration** | The recorded flow number, the baseline for life trending |
| Random vibration | Workmanship screen at flight levels |
| **Leak test** | After vibration, which loosens joints |
| Thermal cycling | Workmanship screen, flight range |
| Functional test, final | Compared against the pre-environmental baseline |

**The procedure is fixed and identical for every article.** Any variation destroys the comparability that makes the data useful, and comparability across the fleet is a large part of the value.

**The final functional test only means something against the pre-environmental baseline** taken on the same article with the same setup. A final measurement in isolation shows the article works; the comparison shows whether the environments changed it.

---

## What acceptance must not do

**Acceptance must not consume meaningful life.** An acceptance test that uses a significant fraction of the qualified life is a design problem, not a test decision. If proof plus environmental plus functional consumes 10 percent of the qualified cycles, the qualified life needs to be higher or the acceptance sequence needs to be shorter.

**Acceptance must not be destructive.** Obvious, and it still happens: a proof test above yield, a life screen that wears the seat, a thermal cycle beyond the seal's capability.

**Acceptance must not be at qualification levels.** Qualification levels include margin the design was proven against; applying them to every flight article spends that margin on the ground.

**Acceptance must not be tailored per article.** A test tailored for a particular unit because it failed the standard sequence is not acceptance; it is a disposition, and it goes through the MRB.

**Track the life consumed.** Every acceptance cycle counts against the qualified life and the count has to follow the article. That is a configuration management requirement, not a test one.

---

## Workmanship screening

The environmental portion of acceptance exists to precipitate latent defects, and the levels are chosen for that rather than for demonstrating capability.

| Screen | Precipitates |
|---|---|
| **Random vibration** | Loose fasteners, cracked solder, marginal welds, fretting, poor bonding |
| **Thermal cycling** | Differential expansion failures, cold solder, marginal seals, delamination |
| Proof pressure | Marginal welds and joints, undersized wall |
| Burn-in (electronics) | Infant mortality |

**Effectiveness depends on the level and the duration**, and both are lower than qualification by design. A screen too gentle precipitates nothing; a screen too severe consumes life. The MIL-STD-1540 levels are the conventional balance.

**A screen that never finds anything is either a perfect process or an ineffective screen**, and the difference matters. Track the screen's find rate across the fleet; a rate of zero over many articles is worth investigating rather than celebrating.

---

## Baseline data

**The most under-valued output of acceptance testing.** Every article leaves with a recorded set of numbers, and those numbers are the reference for the rest of its life.

| Recorded | Used for |
|---|---|
| **Flow number** | Detecting erosion, plugging and edge rounding later |
| **Leak rate** | Detecting seal degradation |
| Response time | Detecting actuator degradation and contamination |
| Setpoint | Detecting spring relaxation |
| Actuation force or current | Detecting friction growth |
| Cleanliness result | The baseline contamination state |

**Record numbers, not pass/fail.** An article that passed tells you nothing later; an article whose flow number was 0.3481 tells you everything when it measures 0.3610 after a flight.

**Trend across the fleet.** Individual articles drift; the fleet distribution shifting is a process signal, and it is visible only if the numbers are recorded and collected.

---

## Disposition

When an article fails acceptance:

| Path | When |
|---|---|
| **Rework and retest** | The nonconformance can be corrected and the correction verified |
| Repair | A departure from the drawing that restores function but not conformance. Requires MRB |
| **Use as is** | The nonconformance is shown not to affect fitness. Requires engineering justification and MRB |
| Scrap | Nothing else is acceptable |

**"Use as is" needs a written engineering justification, not a signature.** It is a permanent departure from the qualified configuration and it has to be traceable to the article for the rest of its life.

**Retest after rework has to cover what the rework could have affected**, which is often more than the failed test. A joint remade after a leak failure needs proof and leak, not just leak.

**A failure at acceptance is a process signal.** One article failing is a nonconformance; three failing the same way is a process problem, and the corrective action belongs upstream in manufacturing rather than in the test cell.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Acceptance answers conformance, not capability | Qualification did capability |
| Non-destructive, always | And it must not consume meaningful life |
| At flight levels, not qualification levels | The margin is spent on the ground otherwise |
| Identical procedure for every article | Comparability is the value |
| Final functional against the pre-environmental baseline | On the same article, same setup |
| Record numbers, not pass/fail | The baseline for the article's whole life |
| Track life consumed by acceptance | It follows the article |
| Trend the screen find rate | Zero over many articles is worth investigating |
| "Use as is" needs written justification | It is a permanent configuration departure |
| Retest covers what rework could affect | Usually more than the failed test |

---

## Failure modes

**Acceptance at qualification levels.** Flight life consumed on the ground.

**Acceptance that consumes significant life.** A design problem discovered as a test problem.

**Pass/fail recorded instead of numbers.** No baseline, and no way to interpret a later measurement.

**Procedure varied per article.** Comparability destroyed, fleet trending impossible.

**Final functional with no pre-environmental baseline.** The article works and nobody knows whether it changed.

**Life consumed by acceptance not tracked.** The qualified life is overstated for every article.

**"Use as is" without written justification.** A configuration departure with no traceability.

**Repeated identical failures treated as individual nonconformances.** The process problem is never addressed.

**Rework retested only for the failed test.** The rework damaged something else.

---

## Standards

| Standard | Scope |
|---|---|
| **MIL-STD-1540** | Test requirements, including acceptance test levels and content |
| NASA-STD-7002 | Payload test requirements |
| MIL-STD-1520 | Corrective action and disposition system for nonconforming material |
| **AS9100** | Quality management, including nonconforming output control |
| ISO 9001 clause 8.7 | Control of nonconforming outputs |
| ECSS-Q-ST-20 | Space product assurance: quality assurance |
| ASME BPVC Section VIII | Pressure vessel acceptance requirements |

---

## Tool interface

```python
from TestCampaign import TestCampaign

campaign = TestCampaign()
campaign.setInputs({'articleName': 'Thruster isolation valve', 'articleType': 'valve',
                    'hardwareClass': 'component', 'fluidHazard': 'toxic'})
matrix = campaign.buildMatrix()

# The acceptance sequence, which is guaranteed non-destructive by construction
for step in matrix['acceptanceSequence']:
    print(step['name'], '--', step['purpose'])
    assert not step['destructive']
```

The class enforces the non-destructive rule structurally: a destructive test appearing in an acceptance sequence raises a design note flagging it as a planning error, and the [test suite](../tests/testFluidSystemsTesting.py) asserts it across every article type.

---

## References

1. MIL-STD-1540E, *Test Requirements for Launch, Upper-Stage, and Space Vehicles*.
2. NASA-STD-7002B, *Payload Test Requirements*.
3. AS9100D, *Quality Management Systems for Aviation, Space and Defense Organizations*.
4. MIL-STD-1520C, *Corrective Action and Disposition System for Nonconforming Material*.
