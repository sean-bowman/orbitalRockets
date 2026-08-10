[Home](../README.md) > Tribology and Lubrication

# Tribology and Lubrication

## Contents

- [Overview](#overview)
- [Why vacuum changes everything](#why-vacuum-changes-everything)
- [Cold welding](#cold-welding)
- [Wet against dry](#wet-against-dry)
- [What the standard requires](#what-the-standard-requires)
- [Bearings](#bearings)
- [What this domain does not model](#what-this-domain-does-not-model)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Friction is the largest variable resisting torque in most mechanisms, it carries the highest safety factor in [the margin equation](ActuatorsAndDrives.md), and it is the least predictable quantity in the domain.

This document is qualitative. **Nothing in it is modelled**, and that is a scope decision rather than an omission: lubrication is a materials and process discipline, and NASA-STD-5017B itself points at a separate standard for it.

---

## Why vacuum changes everything

On the ground, most metals carry an oxide layer and an adsorbed film of water and hydrocarbons. That film is a lubricant nobody specified, and it is doing more work than most designers realise.

In vacuum it desorbs. What is left is clean metal against clean metal, and clean metal against clean metal has a friction coefficient several times higher than the same pair measured in air.

**A mechanism qualified in air and flown in vacuum is a different mechanism**, and the standard lists changes in static and kinetic friction due to storage time or vacuum exposure among the conditions a margin calculation has to account for.

---

## Cold welding

The limiting case. Two clean, similar metals in contact under load, with the oxide disrupted by even small relative motion, can form a solid-state bond.

Three things make it worse: **similar metals**, **high contact pressure**, and **fretting**, which is small-amplitude motion that keeps disrupting the oxide without generating enough sliding to carry debris away.

That combination is exactly what a stowed mechanism experiences during launch: high preload, vibration-induced micromotion, and months of vacuum beforehand if the launch is from orbit.

The mitigations are dissimilar materials, a hard coating, or a lubricant that stays in place. **NASA-STD-5017B strongly encourages dissimilar metals for contacting surfaces, and is explicit that doing so is not a substitute for lubrication.**

---

## Wet against dry

**Wet lubricants** are oils and greases. Better friction, better life under load, and they creep, evaporate, polymerise under high contact pressure, and contaminate optics. The standard requires an evaporative loss analysis showing 90 per cent of the initial quantity remains at end of life, not counting degradation.

**Dry films** are solid lubricants, usually molybdenum disulphide or a sputtered coating. No creep, no outgassing, works across a wide temperature range, and it **wears out**: the film has a finite number of cycles and once it is gone the friction is metal on metal.

The choice is roughly: wet where the cycle count is high and contamination is tolerable, dry where the cycle count is low and contamination is not. A single-shot mechanism is the natural dry film case, and molybdenum disulphide performs better in vacuum than in air, which is one of the few things about this subject that works in the designer's favour.

---

## What the standard requires

NASA-STD-5017B treats lubrication as a process subject to a separate standard, NASA-STD-6016, and requires that **all surfaces in contact for which friction under relative motion negatively affects performance shall be lubricated**.

It then lists nineteen considerations for lubricant selection, which is worth reading in full. The ones most often missed: creep properties, polymerisation under high contact pressure, lubricant purity and filtration level, generation and management of dry lubricant wear debris, compatibility with preservative and shipping oils, **exposure to propellant or propellant vapour**, and interaction with pyrotechnic reaction products.

That last one matters here specifically: a mechanism next to a [pyrotechnic device](Pyrotechnics.md) sees its combustion products.

---

## Bearings

The standard is unusually specific about rolling element bearings, and the numbers are carried in this library as data.

**Allowable mean Hertzian contact stress under non-operational yield design loads**, which is the launch vibration case for a non-rotating bearing:

| Material | Quiet running | Non-quiet running |
|---|---|---|
| 440C | 2310 MPa | 2760 MPa |
| 52100 | 2480 MPa | 2960 MPa |
| M50 | 2480 MPa | 2960 MPa |
| M62 | 3790 MPa | 4070 MPa |

The quiet-running limits correspond to a brinell depth of about 0.00003 to 0.00005 times the ball diameter, and the non-quiet limits to 0.0001, which experience shows can be tolerated in most applications without affecting fatigue life.

**These are not operating stress allowables.** The standard says so explicitly: stresses during intentional rotation need a life calculation and will generally be lower.

---

## What this domain does not model

Everything in this document.

Friction coefficients are inputs to [MechanismActuator](ActuatorsAndDrives.md) rather than outputs of anything, and they carry the highest safety factor in the equation precisely because they are the least predictable term.

**The honest position is that a friction coefficient in this library is a number somebody supplied**, and the standard's factor of 3.00 on variable torques at analysis is the standard's own assessment of how much that number should be trusted.

---

## Design rules of thumb

- **Assume vacuum friction is worse than what you measured in air.**
- **Use dissimilar metals**, and lubricate anyway.
- **Dry film for single-shot, wet for high cycle count**, and check contamination either way.
- **Check propellant vapour compatibility.** It is on the standard's list and it is easy to miss.
- **Use the non-operational bearing allowables for launch**, and a life calculation for operation.

---

## Failure modes

**Qualified in air, flown in vacuum.** Friction rises and the margin was sized on the low number.

**Cold welding at a stowed interface.** High preload plus fretting plus similar metals.

**Dry film worn out before end of life.** It has a cycle count and it is finite.

**Wet lubricant creeping onto an optic.** Or polymerising under contact pressure.

**Non-operational bearing allowables used for operating stress.** They are not the same limits.

---

## References

- NASA-STD-5017B, section 4.6 on lubrication and section 4.9 on bearings, and table 3
- NASA-STD-6016, *Standard Materials and Processes Requirements for Spacecraft*, referenced by the above and not read here
- [aerospaceMaterials](../../aerospaceMaterials/), for coatings and surface treatment
- Conley, *Space Vehicle Mechanisms: Elements of Successful Design*, the tribology chapters
