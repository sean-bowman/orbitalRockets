[Home](../README.md) > Sand Casting

# Sand Casting

## Contents

- [Overview](#overview)
- [The moulding methods](#the-moulding-methods)
- [What it achieves](#what-it-achieves)
- [Where it belongs](#where-it-belongs)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Sand casting is the oldest and the cheapest metal forming process. It makes anything, at any size, coarsely.

For flight structure it is rarely the answer without a qualification programme. For tooling, fixtures, ground support equipment and development hardware it is often exactly right.

---

## The moulding methods

| Method | Binder | Detail | Use |
|---|---|---|---|
| **Green sand** | Clay and water | Coarse | High volume, low cost |
| **Chemically bonded** | Resin | Better | Aerospace and low volume |
| **Shell moulding** | Resin coated sand, heat cured | Good | Better tolerance and surface |
| Lost foam | Polystyrene pattern, unbonded sand | Moderate | Complex shapes, no cores needed |
| **No-bake** | Air setting resin | Good | Large parts, and the aerospace default |

**Chemically bonded sand is what aerospace uses.** Green sand's dimensional repeatability is poor and its surface is coarse; a resin bonded mould holds better tolerance and gives a better surface at a higher cost.

**Lost foam is interesting for complex shapes** because the pattern is vaporised by the incoming metal, so no cores or parting lines are needed. Its dimensional control is moderate and it has a specific defect mode: incomplete pattern vaporisation leaving carbon in the casting.

---

## What it achieves

| Property | Value |
|---|---|
| Minimum wall | 5 mm |
| Maximum mass | Effectively unlimited, tonnes |
| Tolerance | DCTG 11, roughly IT14 |
| Surface | 25 um Ra |
| Buy-to-fly | 1.8 : 1 |
| Lead time | 12 weeks |
| Relative cost | 0.5, the cheapest route here |

**The tolerance is the limitation.** DCTG 11 holds about 5 mm on a 100 mm dimension, which means almost every functional surface has to be machined and the stock allowance is substantial.

---

## Where it belongs

| Application | Why |
|---|---|
| **Tooling and fixtures** | Cheap, large, and the tolerance does not matter |
| **Ground support equipment** | Same |
| **Development hardware** | Fast and cheap for a shape that will change |
| Large low-stress structure | Where the casting factor is affordable |
| Prototype castings | Before committing to investment tooling |

**Prototyping in sand before committing to an investment die is standard practice**, and it is worth doing because the casting design questions (feeding, gating, shrinkage) are the same and the tooling is a fraction of the cost.

**3D printed sand moulds have changed this.** A binder jetted sand mould needs no pattern at all, so a one-off sand casting can be made in weeks with no tooling. That has made sand casting a genuine competitor to additive for large, simple, one-off parts.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Minimum wall | 5 mm |
| Tolerance | DCTG 11 |
| Surface | 25 um Ra |
| Draft | 1 to 3 degrees, required for pattern removal |
| Chemically bonded for aerospace | Green sand is too coarse |
| Prototype in sand before investment tooling | The design questions are the same |
| 3D printed moulds remove the pattern cost | A real change |
| Casting factor 2.0 unless qualified | And it usually is not |

---

## Failure modes

**Sand inclusion.** Mould erosion by the incoming metal, and the sand ends up in the casting.

**Mould wall movement.** The mould deforms under the metal head and the casting is oversize.

**Insufficient draft.** The pattern damages the mould on removal.

**Veining.** The mould surface cracks from thermal expansion and metal enters the cracks.

**Poor surface accepted as inspected.** Penetrant on an as-cast sand surface indicates everywhere.

**Used for flight structure at factor 2.0.** Twice the material, and nobody compared it against qualifying.

---

## Standards

| Standard | Scope |
|---|---|
| **AMS 2175** | Castings, classification and inspection |
| ASTM A27 / A216 | Carbon steel castings |
| ASTM B26 | Aluminium alloy sand castings |
| ISO 8062 | Casting tolerances |
| ASTM E446 | Reference radiographs |

---

## References

1. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
2. ASM Handbook Volume 15, *Casting*.
3. Beeley, P. R., *Foundry Technology*, 2nd ed., Butterworth-Heinemann, 2001.
