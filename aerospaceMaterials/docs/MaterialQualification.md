[Home](../README.md) > Material Qualification

# Material Qualification

## Contents

- [Overview](#overview)
- [What qualification actually establishes](#what-qualification-actually-establishes)
- [The material specification](#the-material-specification)
- [The process specification](#the-process-specification)
- [Establishing an allowable](#establishing-an-allowable)
- [Equivalency](#equivalency)
- [Lot acceptance](#lot-acceptance)
- [Traceability](#traceability)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Qualifying a material means establishing, with evidence, that material produced to a stated specification by a stated process reliably has the properties a design depends on.

**Three things get qualified and they are different:** the material, the process, and the part. This document covers the first two. The third is [fluidSystemsTesting](../../fluidSystems/fluidSystemsTesting/README.md).

The distinction matters because a qualified material made by an unqualified process is not qualified hardware, and this is where most additive manufacturing programmes discover how much work is left.

---

## What qualification actually establishes

| Question | Answered by |
|---|---|
| What is this material? | The material specification: composition, product form, condition |
| How is it made? | The process specification: parameters, equipment, operators |
| What are its properties? | The allowables development programme |
| Does this lot conform? | Lot acceptance testing |
| Where did it come from? | Traceability records |

**All five are required.** A programme with excellent allowables and no traceability cannot demonstrate that the flight article was made from the material tested.

---

## The material specification

Names what the material is, in enough detail that two suppliers produce the same thing.

| Element | Content |
|---|---|
| **Composition** | Element ranges, and the limits on tramp elements |
| **Product form** | Sheet, plate, bar, forging, powder, and the size range |
| **Condition** | Temper or heat treat condition, with the cycle referenced |
| **Mechanical properties** | Minimum values, by orientation and thickness |
| **Process requirements** | Melting practice, reduction ratio, forming limits |
| **Inspection** | What is examined, by what method, to what acceptance |
| **Certification** | What the mill must report and retain |

**Melting practice matters more than people expect.** Vacuum induction melted plus vacuum arc remelted (VIM-VAR) material has far lower inclusion content than air melted, and for a fatigue or fracture critical part that is the difference between the two allowables. It is a specification line, not a supplier choice.

**Reduction ratio governs grain structure.** A forging with inadequate reduction has cast structure in its core and does not meet wrought allowables regardless of composition.

---

## The process specification

Names how the material is turned into a part. This is the harder of the two and it is where additive manufacturing concentrates its difficulty.

**A frozen process specification pins:**

| Parameter class | Examples |
|---|---|
| **Equipment** | Machine make and model, and often the specific serial number |
| **Parameters** | Laser power, scan speed, hatch, layer thickness, gas flow |
| **Feedstock** | Powder specification, particle size distribution, reuse limits |
| **Environment** | Atmosphere, oxygen level, humidity, temperature |
| **Post-processing** | Stress relief, HIP, heat treat, surface finishing |
| **Personnel** | Operator qualification and currency |
| **Inspection** | In-process monitoring, witness coupons, final NDE |

**Any change to any of these is a process change** requiring re-qualification or an equivalency argument. A machine software update, a powder lot from a different atomiser, a change of shielding gas supplier: all of them.

**Witness coupons are how the process is monitored in production.** Specimens built alongside the part, in the same build, from the same powder, tested to confirm the process was in control that day. Their placement and quantity are specification items because build position affects properties.

---

## Establishing an allowable

The programme that turns test specimens into a design value.

| Step | Typical scale |
|---|---|
| Material and process specifications frozen | -- |
| Sampling plan defined | Lots, product forms, orientations, thicknesses |
| **Specimens tested** | **100 or more, across 10 or more lots** |
| Statistical reduction | Per MMPDS Chapter 9 or CMH-17 |
| Documentation and review | -- |

**The sample size is the cost.** A hundred specimens across ten lots is a real programme, and it is why most projects use published allowables and confine their own testing to demonstrating equivalency.

The statistical method is in [AllowablesAndStatistics.md](AllowablesAndStatistics.md). **The important practical point is the ten lot requirement**: between-lot variation is usually larger than within-lot variation, and a hundred specimens from one heat is a statement about that heat rather than about the material.

**A basis value from fewer than ten specimens should not be produced at all.** The [`Allowables`](../aerospaceMaterialsLibrary/Allowables.py) class raises below that threshold rather than returning a number with the authority of a statistic and the content of a guess.

---

## Equivalency

The route most programmes actually take: demonstrate that your material and process produce properties statistically equivalent to an established database, and use that database.

**What equivalency requires:**

| Requirement | Why |
|---|---|
| Same material specification | A different composition is a different material |
| Same process specification class | Same equipment type, same parameter set |
| **A statistically valid comparison sample** | Typically 18 to 30 specimens |
| A defined acceptance criterion | Usually a mean and a minimum test against the database |
| Documentation | The argument, written down and reviewed |

**Equivalency is far cheaper than a full allowables programme and it is not free.** Thirty specimens is a real test campaign, and the acceptance criteria have to be agreed before the data exists rather than after.

**The commonest invalid equivalency argument is across a process change.** Material from a different machine, a different powder lot, or a different post-processing route is not equivalent by assertion. NCAMP and the NASA additive standards exist largely to structure that argument.

---

## Lot acceptance

Once qualified, each production lot is verified against the specification.

| Test | Confirms |
|---|---|
| Chemical analysis | Composition within specification |
| **Tensile** | Yield, ultimate, elongation meet the minimum |
| Hardness | Heat treat condition, as a fast proxy |
| Grain size | Processing was correct |
| Conductivity (aluminium) | Temper verification, non-destructively |
| NDE | Freedom from the defects the specification prohibits |

**Lot acceptance verifies conformance, not capability.** It confirms the lot meets the specification minimum; it does not re-establish the allowable, which is a population statement made once.

**Electrical conductivity is a useful and underused temper check for aluminium.** It correlates with the aging condition, it is non-destructive, and it distinguishes T6 from T73 on a finished part where hardness may not.

---

## Traceability

The chain from the flight part back to the melt.

```
flight part -> serial number -> lot number -> heat number -> mill certificate
```

**Every link has to survive**, and the weak points are always the same: material issued from stores without recording the lot, an offcut used for a second part, a re-identification after a machining operation removed the marking.

**Why it matters:** when a lot is found nonconforming after the fact, the question is which hardware it went into. Without traceability the answer is everything built in that period, and the disposition is scrap.

**Counterfeit and misrepresented material is a real risk**, particularly for high value alloys bought outside a qualified supply chain. Controls are: buy from approved distributors with mill certificates, verify certificates against the mill directly for critical material, and perform incoming positive material identification.

**Positive material identification by XRF is cheap and fast** and it catches the substitution errors that certificates cannot: material correctly certified and then mixed up in a warehouse.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Material, process and part are three separate qualifications | All three are required |
| Specify melting practice for fatigue critical parts | VIM-VAR is a specification line |
| A process change is any change | Machine, powder lot, gas supplier, software |
| Full allowables need 100 specimens across 10 lots | Which is why equivalency exists |
| Equivalency needs 18 to 30 specimens | And agreed criteria before the data |
| Witness coupons monitor the process | Placement and quantity are specification items |
| Lot acceptance verifies conformance, not capability | The allowable is established once |
| Conductivity checks aluminium temper non-destructively | Underused |
| Traceability breaks at stores, offcuts and re-marking | Those are where to look |
| PMI by XRF on incoming critical material | Cheap, and it catches mix-ups |

---

## Failure modes

**A qualified material made by an unqualified process.** Not qualified hardware.

**An equivalency claim across a machine change.** The commonest invalid argument.

**Allowables from a single lot.** A statement about that heat, not the material.

**A process parameter changed without a change notice.** Discovered when the properties shift.

**Witness coupons from a favourable build position.** They monitor nothing useful.

**Traceability lost at an offcut.** Two parts, one lot record.

**Counterfeit material with a plausible certificate.** Verified with the mill, or not verified.

**Lot acceptance treated as re-qualification.** It confirms the minimum, not the distribution.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-6016** | Standard materials and processes requirements for spacecraft |
| **NASA-STD-6030** | Additive manufacturing requirements for spaceflight systems |
| MSFC-STD-3716 | Standard for additively manufactured spaceflight hardware |
| MSFC-SPEC-3717 | Specification for control and qualification of AM processes |
| **MMPDS Chapter 9** | Allowables development and equivalency methodology |
| CMH-17 Volume 1 | Composite allowables and equivalency |
| **NCAMP** | National Center for Advanced Materials Performance, shared databases |
| AS9100 | Quality management for aviation, space and defence |
| **AS6174 / AS5553** | Counterfeit materiel and electronic parts avoidance |
| ASTM E1417 / E1444 | Penetrant and magnetic particle examination |
| ASTM F3049 | Characterizing properties of metal powders for additive manufacturing |

---

## Tool interface

```python
import numpy as np

# a synthetic lot, so this fence runs standalone
rng = np.random.default_rng(20260807)
measuredStrengths = rng.normal(350.0e6, 12.0e6, 60)
lotNumbers = ['lot-{}'.format(1 + index // 6) for index in range(60)]

from Allowables import Allowables
from MaterialDatabase import getProvenance

# The guard that stops an under-sampled allowable being produced at all
allowables = Allowables()
allowables.setInputs({'sampleData': measuredStrengths, 'batchIdentifiers': lotNumbers,
                      'basis': 'A', 'loadPath': 'single'})
allowables.calculateBasisValue()      # raises below n = 10, warns below n = 100 or 10 lots
allowables.calculateAnovaBasis()      # separates within-lot and between-lot variance

# What basis class a database value actually carries
print(getProvenance('AlSi10Mg', 'lpbf as-built', 'typical')['basisClass'])   # 'estimate'
```

---

## References

1. NASA-STD-6016B, *Standard Materials and Processes Requirements for Spacecraft*.
2. NASA-STD-6030, *Additive Manufacturing Requirements for Spaceflight Systems*.
3. MSFC-STD-3716, *Standard for Additively Manufactured Spaceflight Hardware by Laser Powder Bed Fusion*.
4. MMPDS-18, Chapter 9, *Guidelines for the Presentation of Data*.
5. SAE AS6174A, *Counterfeit Materiel; Assuring Acquisition of Authentic and Conforming Materiel*.
