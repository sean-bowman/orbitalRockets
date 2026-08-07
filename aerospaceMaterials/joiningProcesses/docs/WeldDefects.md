[Home](../README.md) > Weld Defects

# Weld Defects

## Contents

- [Overview](#overview)
- [The catalogue](#the-catalogue)
- [Cracking](#cracking)
- [Lack of fusion and penetration](#lack-of-fusion-and-penetration)
- [Porosity](#porosity)
- [Geometric defects](#geometric-defects)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Weld defects divide into planar and volumetric, and the distinction decides both how dangerous they are and how they are found. Planar defects are far more dangerous and far harder to detect, which is an unfortunate combination.

---

## The catalogue

| Defect | Type | Cause | Detection |
|---|---|---|---|
| **Hot cracking** | **Planar** | Low melting films at solidification | RT, PT, UT |
| **Cold cracking** | **Planar** | Hydrogen, restraint, hard microstructure | **Delayed.** UT, PT |
| **Lack of fusion** | **Planar** | Insufficient heat or poor access | **UT.** RT often misses it |
| **Lack of penetration** | **Planar** | Root not reached | RT, UT |
| Porosity | Volumetric | Gas, contamination | **RT** |
| Slag inclusion | Volumetric | Incomplete removal between passes | RT |
| Undercut | Geometric | Excessive current, wrong technique | Visual |
| Excess reinforcement | Geometric | Too much filler | Visual |
| Burn through | Geometric | Excessive heat, thin section | Visual |
| Arc strike | Surface | Careless electrode contact | Visual, PT |

**Planar defects are the dangerous ones** because they behave as cracks with a stress intensity, while a rounded pore is a stress concentration of modest severity.

**Radiography sees volumetric defects well and planar ones poorly**, which is the wrong way round. A lack of fusion lying parallel to the plate surface presents almost no thickness change to the beam and it is routinely missed.

**Ultrasonic sees planar defects well**, which is why a critical weld gets both.

---

## Cracking

### Hot cracking

**Solidification cracking, in the fusion zone, while it is still partly liquid.**

| Contributor | Detail |
|---|---|
| **Low melting films** | Sulphur, phosphorus, and eutectics |
| **Wide freezing range** | Longer vulnerable period |
| **Restraint** | Shrinkage strain with nowhere to go |
| **Fully austenitic solidification** | No delta ferrite to dissolve the impurities |
| Zinc in 7000 series aluminium | Why 7075 is not fusion weldable |

**Delta ferrite prevents it in austenitic stainless**, which is why the ferrite number is controlled at 3 to 10 FN. See [FusionWelding.md](FusionWelding.md).

### Cold cracking

**Hydrogen assisted cracking, and it is delayed.**

**Four conditions, all required:**

| Condition | Detail |
|---|---|
| **Hydrogen** | From moisture, contamination, or the consumable |
| **Susceptible microstructure** | Martensite, from a fast cool |
| **Restraint stress** | Tensile |
| **Temperature below ~200 degC** | It happens on cooling and after |

**It appears hours to days after welding**, which is why inspection is delayed by 24 to 48 hours on susceptible materials. Inspecting immediately after welding and passing the weld is a known failure mode.

| Control | Detail |
|---|---|
| **Low hydrogen consumables**, dried | Remove the hydrogen |
| **Preheat** | Slower cooling, softer microstructure, more hydrogen escapes |
| **Post-weld hydrogen bake** | Drive the remaining hydrogen out |
| Reduce restraint | Sequence and fixturing |

**Preheat addresses three of the four conditions at once**, which is why it is the primary control for high strength steel welding.

---

## Lack of fusion and penetration

**The most dangerous common defects, because they are planar and they are the hardest to find.**

| Defect | Detail |
|---|---|
| **Lack of fusion** | The weld metal did not fuse to the sidewall or a previous pass |
| **Lack of penetration** | The root was not reached |

**Radiography misses lack of sidewall fusion routinely** because the defect lies at an angle to the beam and it has negligible thickness. It can be a full length unbonded interface and pass a radiographic inspection.

**Ultrasonic finds it** and that is why a critical weld specifies both methods, or phased array which is better than either alone.

**Full penetration joints are specified for pressure boundaries** partly because a partial penetration joint has a designed lack of penetration at its root, which cannot be distinguished from an unintended one.

---

## Porosity

| Type | Cause |
|---|---|
| **Scattered** | Dissolved gas rejected on solidification |
| **Clustered** | Local contamination |
| **Linear** | A contaminated joint line |
| Wormhole | Gas escaping through the solidifying metal |

**Aluminium porosity is hydrogen** from moisture on the surface or in the shielding gas. Hydrogen is very soluble in liquid aluminium and nearly insoluble in solid, so it comes out on freezing.

**Cleaning and drying are the control**, and aluminium welding requires scraping or chemical cleaning of the joint immediately before welding, because the oxide re-forms and traps moisture.

**Titanium porosity is worse** because it also means atmospheric contamination, and the discolouration of the weld is the field indicator: silver is good, straw is marginal, blue and grey are rejectable.

**Porosity is volumetric and modestly harmful**, and it is over-reported relative to its consequence because radiography finds it so easily.

---

## Geometric defects

| Defect | Consequence |
|---|---|
| **Undercut** | A sharp notch at the toe. **A fatigue initiation site** |
| **Excess reinforcement** | A sharp toe angle. Same |
| **Misalignment** | Eccentric load path, bending |
| Burn through | A hole |
| **Arc strike** | A local quenched spot. Cracking |

**Undercut is a fatigue defect rather than a strength one.** It removes little section and it leaves a sharp notch exactly at the weld toe where the stress concentrates, which is where fatigue cracks start anyway.

**Weld toe geometry dominates weld fatigue life**, and grinding the toe smooth is a recognised fatigue improvement technique worth a factor of two or more.

**Arc strikes are rejectable on high strength steel** because the tiny melted spot cools very fast into untempered martensite and cracks.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Planar defects are dangerous, volumetric less so | |
| RT finds volumetric, UT finds planar | Specify both for critical welds |
| Cold cracking is delayed | Inspect 24 to 48 hours later |
| Preheat addresses three of four cold cracking conditions | |
| Ferrite number 3 to 10 prevents hot cracking | |
| Lack of sidewall fusion passes radiography | Use UT |
| Undercut is a fatigue defect | Grind the toe |
| Titanium weld colour is the field indicator | Silver good, blue rejectable |

---

## Failure modes

**Radiography alone on a critical weld.** Lack of fusion missed.

**Inspection immediately after welding on high strength steel.** Cold cracking appears later.

**Fully austenitic weld metal.** Hot cracking.

**Aluminium joint not cleaned immediately before welding.** Hydrogen porosity.

**Undercut accepted as a minor defect.** It is a fatigue initiation site.

**Arc strike left on high strength steel.** Untempered martensite and cracking.

**Titanium welded with poor shielding.** Contamination, visible as discolouration.

---

## Standards

| Standard | Scope |
|---|---|
| **AWS D17.1** | Fusion welding for aerospace, including acceptance criteria |
| **NASA-STD-5006** | General welding requirements |
| ASME BPVC Section V | Nondestructive examination |
| **ASTM E1417** | Liquid penetrant testing |
| ASTM E1742 | Radiographic examination |
| **ASTM E2700** | Phased array ultrasonic testing of welds |
| ISO 6520 | Classification of imperfections in metallic fusion welds |
| ISO 5817 | Quality levels for imperfections |

---

## References

1. Kou, S., *Welding Metallurgy*, 2nd ed., Wiley, 2003.
2. AWS D17.1, *Specification for Fusion Welding for Aerospace Applications*.
3. ASM Handbook Volume 6, *Welding, Brazing, and Soldering*.
