[Home](../README.md) > Specifications and Procurement

# Specifications and Procurement

## Contents

- [Overview](#overview)
- [What a specification guarantees](#what-a-specification-guarantees)
- [The certification](#the-certification)
- [Lead times](#lead-times)
- [Traceability](#traceability)
- [Counterfeit and diverted material](#counterfeit-and-diverted-material)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

A material specification is a contract. It states what the supplier guarantees, and everything it does not state is not guaranteed. Most material problems in aerospace trace to a specification that did not say something the designer assumed.

---

## What a specification guarantees

| Guaranteed | Not guaranteed unless stated |
|---|---|
| **Chemistry**, within a range | **Grain direction** relative to the part |
| **Minimum mechanical properties** | **Typical** properties |
| **Product form and dimensions** | Residual stress state |
| Heat treatment condition | Ultrasonic quality class |
| Surface condition class | Inclusion content |
| | **Which orientation the tested specimen came from** |

**Specifications guarantee minima, not typical values.** A 316L bar to ASTM A276 is guaranteed 205 MPa yield; it typically delivers 280. Designing to the typical value and receiving the minimum is a real failure mode, and it is why allowables are statistical rather than typical. See [aerospaceMaterials AllowablesAndStatistics.md](../../docs/AllowablesAndStatistics.md).

**Ultrasonic quality class is optional in most specifications** and it has to be invoked. AMS 2154 class A, AA or AAA differ substantially in the discontinuity size they permit, and a specification that does not name a class permits whatever the mill normally ships.

**Specimen orientation is the omission that matters most.** A tensile result on a certification is meaningful only if the orientation is stated, and for a thick plate it usually is not the orientation the part will be loaded in.

---

## The certification

| Type | Meaning |
|---|---|
| **Type 2.1** | The supplier declares conformity. **No test data** |
| **Type 3.1** | **Test results from the actual lot**, certified by the manufacturer |
| Type 3.2 | 3.1 plus an independent third party |

**Type 3.1 is the aerospace minimum** and it carries the actual chemistry and mechanical results for the heat and lot supplied.

**A 2.1 certificate carries no data at all.** It is a statement that the material meets the specification, with nothing to verify it against.

**Read the certificate against the specification.** A certificate can conform to a different specification than the one ordered, and the discrepancy is only visible if somebody compares them.

---

## Lead times

| Form | Lead time |
|---|---|
| Common aluminium sheet, bar | **4 to 8 wk** |
| Aluminium plate | 8 to 16 wk |
| Stainless plate and bar | 8 to 14 wk |
| **Titanium plate and bar** | **16 to 30 wk** |
| **Nickel alloy bar** | **20 to 40 wk** |
| **Extrusion, new die** | 12 to 20 wk plus die |
| **Forging** | **20 to 30 wk plus tooling** |
| Al-Li plate | 20 to 40 wk, limited sources |

**Titanium and nickel lead times drive programme schedules** and they are volatile: they lengthen substantially when the commercial aerospace cycle is strong, because launch vehicle volumes are small next to airframe and engine demand.

**Mill minimums are a real constraint.** A mill run may have a several tonne minimum, so a small quantity comes from a distributor's stock at a premium or not at all.

**Distributor stock changes the calculation entirely** and it is the reason 6061 and 316L are used so much: they are on the shelf.

---

## Traceability

| Level | Detail |
|---|---|
| **Heat number** | The melt. Chemistry traces to it |
| **Lot number** | The heat treat batch. Mechanical properties trace to it |
| **Serial number** | The individual piece, for fracture critical hardware |

**Traceability has to survive the shop.** A bar cut into six pieces produces six pieces that all need the heat and lot marking transferred, and the transfer is a controlled operation.

**Fracture critical hardware is serialised** and its material traceability is retained for the life of the vehicle, per NASA-STD-5019 and equivalent.

---

## Counterfeit and diverted material

**A real and growing problem, and titanium and nickel are the targets because they are expensive.**

| Risk | Detail |
|---|---|
| **Falsified certification** | The paperwork does not match the material |
| **Diverted scrap** | Material rejected by one customer resold |
| **Wrong alloy** | Substituted, sometimes deliberately |
| Re-marked | A lower grade marked as a higher one |

| Control | Detail |
|---|---|
| **Approved supplier list** | Buy from the mill or an approved distributor |
| **Incoming verification** | PMI by XRF or optical emission, on receipt |
| **Independent test** | Tensile from the received lot, for critical material |
| Certificate review | Against the specification, by someone competent |

**Positive material identification by handheld XRF is fast and cheap** and it catches the wrong-alloy cases. It does not catch a correct alloy in the wrong condition, which needs a hardness check or a tensile test.

**AS6174 and AS5553 are the counterfeit avoidance standards** and they define the required process for material and for electronic parts respectively.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| A specification guarantees minima | Not typical |
| Invoke the ultrasonic class explicitly | Or you get what the mill ships |
| Type 3.1 certification minimum | 2.1 carries no data |
| Titanium and nickel lead 20 to 40 wk | And they are volatile |
| Mill minimums are real | Distributor stock or nothing |
| Transfer heat and lot marking on cut-up | A controlled operation |
| PMI on receipt for expensive alloys | Fast and cheap |

---

## Failure modes

**Typical properties used in design.** The specification guarantees minima.

**Ultrasonic class not invoked.** Whatever the mill ships.

**2.1 certificate accepted for flight hardware.** No test data at all.

**Certificate not compared against the ordered specification.** A different spec accepted.

**Heat marking lost on cut-up.** Traceability broken and the material is unusable.

**Titanium bought on the open market.** Counterfeit exposure.

**Forging lead time discovered at detail design.** 30 weeks.

---

## Standards

| Standard | Scope |
|---|---|
| **AS9100** | Quality management for aerospace |
| **AS6174** | Counterfeit materiel avoidance |
| AS5553 | Counterfeit electronic parts avoidance |
| EN 10204 | Types of inspection documents, 2.1 / 3.1 / 3.2 |
| **AMS 2154 / MIL-STD-2154** | Ultrasonic inspection of wrought metals, quality classes |
| NASA-STD-5019 | Fracture control requirements |
| ASTM E1476 | Metal and alloy distribution system |

---

## References

1. AS9100D, *Quality Management Systems: Requirements for Aviation, Space and Defense Organizations*.
2. MMPDS-2023, *Metallic Materials Properties Development and Standardization*.
3. AS6174A, *Counterfeit Materiel: Assuring Acquisition of Authentic and Conforming Materiel*.
