[Home](../README.md) > Repair

# Additive Repair

## Contents

- [Overview](#overview)
- [Why repair is different from new build](#why-repair-is-different-from-new-build)
- [The processes](#the-processes)
- [The substrate problem](#the-substrate-problem)
- [The workflow](#the-workflow)
- [Qualification](#qualification)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Additive repair adds material to hardware that already exists, which no powder bed process can do. It is the application where DED and cold spray have no competition, and it is qualified quite differently from new-build additive.

---

## Why repair is different from new build

| | New build | Repair |
|---|---|---|
| **Starting condition** | Known stock, certified | **A part with a service history** |
| **Geometry** | From CAD | **From the actual damaged part** |
| **Substrate** | A build plate, discarded | **Flight hardware, retained** |
| **Prior damage** | None | **Possibly fatigue damage, unknown** |
| **Qualification basis** | The process | **The process plus the substrate assessment** |

**The unknown substrate is the whole difficulty.** A new part starts from certified stock with a known thermal history. A repaired part starts from something that has been in service for an unknown number of cycles at an unknown temperature, possibly with subcritical fatigue damage that is smaller than the inspection threshold.

**Adaptive machining is required** because the damaged geometry is not the CAD geometry. The part is scanned, the actual damage boundary is found, the deposition path is generated against the scan, and the finish machining is generated against the same scan. That toolchain is a substantial part of the process.

---

## The processes

| Process | HAZ | Rate | Use |
|---|---|---|---|
| **DED, laser powder** | **Yes** | Moderate | Blade tips, seal lands, precision restoration |
| **DED, wire** | Yes | High | Larger volume restoration |
| **Cold spray** | **None** | **Very high** | **Heat sensitive substrates, corrosion damage** |
| Weld repair (conventional) | Yes | Moderate | The traditional method |
| Thermal spray | Minimal | High | Coatings, not structural |

**Cold spray and DED split the field by whether the substrate can take heat.**

**A heat treated aluminium or magnesium casting cannot** and cold spray is the answer. **A nickel turbine blade can** and DED gives better properties and a metallurgical bond throughout.

---

## The substrate problem

| Issue | Detail |
|---|---|
| **Unknown thermal history** | It may already be overaged |
| **Possible fatigue damage** | Below the inspection threshold |
| **Contamination** | Oxidation, fuel residue, coating remnants |
| **HAZ from the repair** | Locally changes the substrate condition |
| **Distortion** | The part is not clamped to a build plate |

**Contamination removal is the first step and it is not trivial.** A part from a hot section carries oxide, and a part from a fluid system carries residue. Both prevent bonding, and both are in the damage cavity where they are hardest to remove.

**The repair HAZ affects flight hardware**, not a discarded build plate. In a heat treated substrate this locally alters the condition, and either the affected material is within the machining allowance or the analysis accounts for it.

**Prior fatigue damage is the one that cannot be resolved by inspection** alone, which is why repair schemes are limited by the number of prior service cycles and by a cumulative repair count.

---

## The workflow

| Step | Detail |
|---|---|
| **1. Inspect and assess** | Is it repairable? Prior repairs, service hours, damage extent |
| **2. Remove damage** | Machine to sound material, and verify by NDE |
| **3. Clean** | Contamination removal, and verify |
| **4. Scan** | Capture the actual geometry |
| **5. Generate the path** | Adaptively, against the scan |
| **6. Deposit** | With oversize allowance |
| **7. Heat treat** | Where the substrate allows |
| **8. Adaptive finish machine** | Against the same scan |
| **9. Inspect** | The repair, the interface and the HAZ |

**Step 2 is where repairs are lost.** Machining to sound material sometimes reveals that the damage extends further than the inspection indicated, and the part becomes unrepairable at that point.

**Verifying cleanliness before deposition** is a step that is easy to omit and it is the commonest cause of interface lack of fusion.

**The interface is the critical inspection**, not the deposit. A sound deposit poorly bonded to the substrate is a planar defect at exactly the highest stress location.

---

## Qualification

| Element | Detail |
|---|---|
| **Repair scheme** | Approved for a specific part, damage type and location |
| **Damage limits** | Maximum size, depth and location |
| **Repair count limit** | How many times a part may be repaired |
| **Prior service limit** | Repairable only within a service life fraction |
| **Coupon testing** | Representative substrate condition |
| **NDE of the interface** | Required |

**A repair scheme is part specific**, not process specific. A qualified DED repair for one blade does not qualify the same process on a different blade, because the substrate, the geometry and the stress field all differ.

**Coupons must represent the actual substrate condition**, which means service exposed material where available. A coupon made from new stock does not represent a part with 5000 hours on it.

**Repair count limits exist** because each repair cycle adds heat, adds residual stress and removes sound material, and the accumulated effect is not linear.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Only DED and cold spray can repair | Powder bed cannot |
| Cold spray where the substrate cannot take heat | |
| Adaptive scanning and pathing required | The geometry is not CAD |
| Machine to sound material and verify | Repairs are lost here |
| Verify cleanliness before depositing | The commonest interface failure |
| **The interface is the critical inspection** | Not the deposit |
| Repair schemes are part specific | Not process specific |
| Coupons from service exposed material | Not new stock |

---

## Failure modes

**Contamination not removed.** Interface lack of fusion.

**Damage boundary not verified by NDE.** Repair over a crack.

**CAD geometry used instead of a scan.** The deposit does not fit the damage.

**Repair HAZ not accounted in the substrate.** Locally different condition.

**Coupons from new stock.** Not representative.

**Repair count limit exceeded.** Accumulated degradation.

**Deposit inspected, interface not.** The critical location is unverified.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-6030** | Additive manufacturing requirements for spaceflight |
| ASTM F3187 | Directed energy deposition of metals |
| **ASTM F3339** | Cold spray deposition |
| MIL-STD-3021 | Materials deposition, cold spray |
| AWS D20.1 | Fabrication of metal components using additive manufacturing |
| **ASTM E1417 / E2700** | Penetrant and phased array ultrasonic |
| AS9110 | Quality management for maintenance organisations |

---

## References

1. Gradl, P. R. et al., "Metal Additive Manufacturing in Aerospace: A Review", *Materials and Design*, Vol. 209, 2021.
2. Champagne, V. K. (ed.), *The Cold Spray Materials Deposition Process*, Woodhead, 2007.
3. NASA-STD-6030, *Additive Manufacturing Requirements for Spaceflight Systems*.
