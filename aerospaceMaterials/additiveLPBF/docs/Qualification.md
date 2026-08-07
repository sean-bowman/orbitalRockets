[Home](../README.md) > Qualification

# Qualification

## Contents

- [Overview](#overview)
- [Why additive inverts the usual structure](#why-additive-inverts-the-usual-structure)
- [The five pillars](#the-five-pillars)
- [Part classification](#part-classification)
- [Process maturity](#process-maturity)
- [Witness coupons](#witness-coupons)
- [The allowables route](#the-allowables-route)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Qualifying an additive part is not qualifying a part made from a qualified material. The material and the part are created in the same operation, so the whole structure has to be rebuilt.

NASA-STD-6030 and MSFC-STD-3716 are the documents that do it, and they are worth reading rather than summarising.

---

## Why additive inverts the usual structure

| Wrought part | Additive part |
|---|---|
| Material arrives qualified, with a mill certificate | **The build is the melt.** No independent material exists |
| Shop qualifies its processes | Every melt parameter becomes the part's problem |
| Properties from a published allowable | Properties depend on the machine, the powder and the orientation |
| Inspection finds manufacturing defects | The geometry that matters cannot be inspected |

**The consequence is that most of the evidence comes from process control rather than from inspection**, and that is uncomfortable for anyone used to a wrought supply chain.

---

## The five pillars

NASA-STD-6030 structures the argument this way, and it is a useful checklist because a programme with four of them has a gap rather than 80 percent of a qualification.

| Pillar | Content |
|---|---|
| **Qualified material and process** | A frozen specification, with every property-affecting parameter named and controlled |
| **Qualified equipment** | Machine qualification, calibration, maintenance record, and a demonstration that a second machine matches |
| **Qualified personnel** | Operator training and currency, and a defined authority for deviations |
| **Part and process qualification** | First article, witness coupons, and the demonstration that this geometry builds correctly |
| **Production control** | Lot acceptance, in-process monitoring, statistical process control, and the discipline that any change is a change |

**The missing pillar is where the failure comes from**, which is why the [`LpbfQualification`](../additiveLpbfLibrary/LpbfQualification.py) class reports them as a checklist rather than a score.

---

## Part classification

Two axes: what happens if the part fails, and how much is known about how it was made.

| Class | Meaning | Coupons | Volumetric NDE | Basis |
|---|---|---|---|---|
| **AXM** | Fracture critical or high consequence | 12 | Required | A |
| **AXB** | Structurally significant, or fail-safe | 6 | Required | B |
| **BXB** | Redundant load path, low consequence pressure | 3 | Sample | B |
| **CXC** | Non-structural | 1 | No | typical |

**A pressure boundary is normally AXM or AXB** regardless of what the load path looks like, because a leak or a rupture is a safety consequence.

---

## Process maturity

| Maturity | Multiplier | Meaning |
|---|---|---|
| **Qualified** | 1.00 | Frozen parameters, qualified machine, controlled powder, monitoring |
| Controlled | 1.50 | Documented, but the machine or monitoring is not formally qualified |
| Developmental | 2.50 | Parameters under development |
| **Uncontrolled** | infinite | Parameters or powder history unknown |

**An uncontrolled process cannot produce flight hardware above non-structural, at any coupon count.** No quantity of coupons substitutes for a frozen parameter set: coupons monitor a process that is under control and they measure noise on one that is not.

**A service bureau build with no parameter disclosure sits in the uncontrolled row.** That is not a criticism of service bureaus, several of which run better process control than most in-house shops. It is a statement about what the customer can demonstrate.

---

## Witness coupons

| Requirement | Reason |
|---|---|
| Same build, same powder lot | A different build is a different day |
| **Distributed placement** | Build position affects properties through gas flow and thermal history |
| Both orientations | XY and Z differ |
| Tested to the part specification | Or they prove something else |

**Test matrix by class:**

| Class | Tests |
|---|---|
| CXC | Tensile in the build direction |
| BXB | Plus transverse tensile, density |
| AXB | Plus fatigue, metallography |
| **AXM** | Plus fracture toughness, chemistry including oxygen |

---

## The allowables route

| Route | Specimens | When |
|---|---|---|
| **Equivalency** | 18 to 30 | Against a published additive database. The usual route |
| **Full allowables** | ~100 across 10 builds | Where no database exists |
| Published | 0 | Where one applies exactly, which is rare |

**Equivalency is far cheaper and it is not free.** The acceptance criteria have to be agreed before the data exists, and the commonest invalid argument is equivalency across a machine or powder change.

**The orientation knockdown enters here.** An unspecified build orientation carries a worse factor than Z, because if the orientation is not on the drawing then nothing stops a build being oriented badly. Specifying it recovers 5 percent of the allowable for free.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| The build is the melt | Evidence comes from process control |
| Five pillars, all required | Four is a gap |
| Uncontrolled process | No flight hardware above CXC |
| Coupon placement | A specification item |
| Equivalency | 18 to 30 specimens, criteria agreed first |
| Full allowables | ~100 specimens across 10 builds |
| Any parameter change | A process change |
| Specify build orientation | Recovers 5 % for free |

---

## Failure modes

**A qualified material made by an unqualified process.** Not qualified hardware.

**Equivalency claimed across a machine change.** The commonest invalid argument.

**A machine software update treated as maintenance.** It is a process change.

**Coupons from a favourable plate position.** They monitor nothing useful.

**Four pillars complete.** The gap is where the failure comes from.

**A service bureau build with no parameter disclosure used for flight.** Nothing can be demonstrated.

---

## Worked numbers

From [`LpbfQualification`](../additiveLpbfLibrary/LpbfQualification.py):

| Class | Maturity | Coupons | CT | Basis | Equivalency |
|---|---|---|---|---|---|
| AXM | qualified | 12 | Yes | A | 30 |
| AXB | controlled | **9** | Yes | B | 18 |
| BXB | qualified | 3 | No | B | 18 |
| CXC | developmental | 3 | No | typical | 0 |
| **AXM** | **uncontrolled** | -- | -- | -- | **raises** |

The AXB row shows the maturity multiplier: 6 coupons at qualified become 9 at controlled.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-6030** | Additive manufacturing requirements for spaceflight systems |
| **MSFC-STD-3716** | LPBF spaceflight hardware |
| MSFC-SPEC-3717 | Control and qualification of LPBF processes |
| ASTM F3303 | Process characteristics for critical applications |
| NCAMP | Shared qualification databases |
| **MMPDS Chapter 9** | Allowables and equivalency methodology |
| AS9100 | Quality management |

---

## Tool interface

```python
from LpbfQualification import LpbfQualification

qualification = LpbfQualification()
qualification.setInputs({'partName': 'thruster valve manifold',
                         'consequenceClass': 'AXB', 'processMaturity': 'controlled',
                         'buildOrientation': 'Z', 'hasInternalPassages': True,
                         'isPressureBoundary': True})

qualification.classifyPart()
qualification.calculateCouponRequirement()
qualification.buildInspectionPlan()
qualification.calculateAllowablesPath()
qualification.assessPillars({'qualifiedMaterialProcess': True, 'qualifiedEquipment': True})
print(qualification.generateReport())
```

---

## References

1. NASA-STD-6030, *Additive Manufacturing Requirements for Spaceflight Systems*.
2. MSFC-STD-3716, *Standard for Additively Manufactured Spaceflight Hardware by Laser Powder Bed Fusion*.
3. MSFC-SPEC-3717, *Specification for Control and Qualification of LPBF Metallurgical Processes*.
4. Seifi, M. et al., "Progress Towards Metal Additive Manufacturing Standardization to Support Qualification and Certification", *JOM*, Vol. 69, 2017.
