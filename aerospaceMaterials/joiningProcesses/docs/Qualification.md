[Home](../README.md) > Qualification

# Qualification

## Contents

- [Overview](#overview)
- [The three qualifications](#the-three-qualifications)
- [Procedure qualification](#procedure-qualification)
- [Operator qualification](#operator-qualification)
- [Essential variables](#essential-variables)
- [Production control](#production-control)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Welding is a special process: its output cannot be fully verified by inspecting the product, so it is controlled by qualifying the process and the people. That framing explains every requirement that follows.

---

## The three qualifications

| Qualification | What it demonstrates |
|---|---|
| **Procedure (PQR to WPS)** | **The process produces a sound joint** |
| **Operator or welder (WPQ)** | **This person can execute it** |
| **Equipment** | The machine holds the parameters |

**All three are required and they are independent.** A qualified procedure executed by an unqualified welder is not a qualified weld, and neither is a qualified welder working to an unqualified procedure.

**The document chain runs: PQR to WPS to WPQ.**

| Document | Content |
|---|---|
| **PQR** (procedure qualification record) | The parameters actually used and the test results obtained |
| **WPS** (welding procedure specification) | The instructions to the welder, supported by the PQR |
| **WPQ** (welder performance qualification) | Evidence that a named welder can execute a WPS |

---

## Procedure qualification

| Step | Detail |
|---|---|
| **1. Weld a test coupon** | To the proposed parameters, recorded as they happen |
| **2. Nondestructive test it** | RT, PT, UT as applicable |
| **3. Destructively test it** | Tensile, bend, macro, hardness, impact as required |
| **4. Record the PQR** | The parameters used and the results |
| **5. Write the WPS** | With ranges, supported by the PQR |

**The PQR records what was done, not what was intended.** If the coupon was welded at 145 amps, the PQR says 145 amps, and the WPS range is derived from it within the essential variable limits.

**Test requirements depend on the code and the criticality**, and for aerospace under AWS D17.1 they typically include two transverse tensile, four bend, a macro-section and hardness, with impacts where toughness governs.

**One PQR can support several WPSs** within the essential variable ranges, and a single WPS may be supported by more than one PQR where the ranges are wide.

---

## Operator qualification

| Element | Detail |
|---|---|
| **A test weld** | To an applicable WPS, in the required position |
| **Position** | 1G through 6G. **A higher position qualifies lower ones** |
| Material group | P-numbers or equivalent grouping |
| Thickness range | Qualified thickness derives from the coupon |
| **Continuity** | Requalification if the process is not used for a period, typically 6 months |

**The 6G position qualifies all positions**, which is why pipe welders test in 6G: a single test covers everything.

**Continuity requirements are real and they are frequently missed.** A welder who has not used a process for six months is no longer qualified for it, regardless of experience.

**Automatic and machine welding qualifies the operator differently** from manual welding, because the skill involved is setup and monitoring rather than manipulation. An FSW or EBW operator is qualified on the machine setup.

---

## Essential variables

**The parameters that, if changed beyond a defined range, invalidate the qualification.**

| Category | Examples |
|---|---|
| **Essential** | **Process, base material group, filler group, thickness range, preheat, PWHT** |
| **Supplementary essential** | Heat input, position, where impact testing is required |
| Non-essential | Joint detail, technique, travel speed within limits |

**Changing an essential variable requires requalification**, which means a new coupon, new tests and a new PQR. That is the mechanism by which the qualification retains meaning.

**Base material group changes are the commonest trap.** A procedure qualified on 304L does not cover 316L unless the grouping says so, and the grouping is defined by the code rather than by engineering judgement.

**Heat input is supplementary essential where toughness matters**, which covers most cryogenic and fracture critical work. A change in heat input changes the HAZ and the fusion zone structure, so the impact properties demonstrated no longer apply.

---

## Production control

| Element | Detail |
|---|---|
| **Weld map** | Every weld identified, with its WPS and welder |
| **Traceability** | Filler lot, gas, parameters |
| **Recorded parameters** | On automatic processes, per weld |
| **Consumable control** | Low hydrogen electrodes in heated storage, with exposure limits |
| Repair procedure | Qualified separately, with a repair count limit |
| **Inspection records** | Traceable to the weld |

**Repair welds need their own qualification** and a limit on the number of repairs at one location. Repeated repair accumulates heat input, widens the HAZ and raises the residual stress, and after two or three attempts the material is worse than the original defect.

**Consumable exposure control matters for low hydrogen processes.** An electrode out of its heated oven for longer than the permitted period has absorbed moisture and it is a hydrogen source. See [WeldDefects.md](WeldDefects.md).

**Automatic process parameter recording is what makes FSW and EBW attractive** from a quality standpoint: every weld has a recorded parameter trace, which a manual weld does not.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Welding is a special process | Qualify it, do not inspect it in |
| Three qualifications, all required | Procedure, operator, equipment |
| PQR records what was done | The WPS gives ranges |
| 6G qualifies all positions | |
| Continuity, typically 6 months | And it is frequently missed |
| Essential variable change means requalification | |
| Limit repairs at one location | Two or three |
| Automatic processes record parameters | A real quality advantage |

---

## Failure modes

**Qualified welder, unqualified procedure.** Not a qualified weld.

**Material group change assumed covered.** It is defined by the code.

**Heat input changed where toughness governs.** The impacts no longer apply.

**Welder continuity lapsed.** No longer qualified.

**Repeated repair at one location.** Worse than the original defect.

**Electrode exposure exceeded.** A hydrogen source.

**PQR written from the intended parameters.** It must record the actual ones.

---

## Standards

| Standard | Scope |
|---|---|
| **AWS D17.1** | Fusion welding for aerospace applications |
| AWS D17.3 | Friction stir welding for aerospace |
| **ASME BPVC Section IX** | Welding, brazing and fusing qualifications |
| **NASA-STD-5006** | General welding requirements for aerospace |
| ISO 15614 | Welding procedure specification and qualification |
| ISO 9606 | Qualification testing of welders |
| **AS9100** | Quality management, special processes |
| Nadcap AC7110 | Welding accreditation |

---

## References

1. AWS D17.1, *Specification for Fusion Welding for Aerospace Applications*.
2. ASME BPVC Section IX, *Welding, Brazing, and Fusing Qualifications*.
3. NASA-STD-5006A, *General Welding Requirements for Aerospace Materials*.
