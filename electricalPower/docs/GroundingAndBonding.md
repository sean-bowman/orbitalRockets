[Home](../README.md) > Grounding and Bonding

# Grounding and Bonding

## Contents

- [Overview](#overview)
- [What grounding is for](#what-grounding-is-for)
- [Single point](#single-point)
- [Multipoint](#multipoint)
- [Hybrid, and why almost everything is](#hybrid-and-why-almost-everything-is)
- [Structure as a return path](#structure-as-a-return-path)
- [Bonding](#bonding)
- [Why none of this is modelled](#why-none-of-this-is-modelled)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Grounding is a topology decision made early and expensive to change late, and it has no scalar answer. This document explains the choices and models none of them, which is a scope decision stated rather than an omission.

---

## What grounding is for

Three separate jobs that get the same name, and most grounding arguments are two people optimising different ones.

**A return path** for current to get back to its source.

**A reference** so that two circuits agree what zero volts means.

**A fault and discharge path** so that energy has somewhere to go that is not through something delicate.

A topology that is excellent for one can be poor for another, which is why the answer is usually hybrid.

---

## Single point

Every ground connects to one node, and nothing else.

**What it buys** is that no current flows in the reference: because there is only one path, there are no ground loops and no circulating currents driven by the potential difference between two grounding points.

**What it costs** is length. A single-point ground on a large vehicle needs long conductors, and a long conductor is an inductor at high frequency: **above a few megahertz a single-point ground stops being single point**, because the impedance of the connection dominates.

So single point is right for low-frequency and sensitive analogue, and it stops working exactly where high-frequency interference starts.

---

## Multipoint

Everything grounds to the nearest structure.

**What it buys** is low impedance at high frequency, because every path is short.

**What it costs** is ground loops: two grounding points at different potentials drive a circulating current, and that current appears as noise in whatever shares the path.

Multipoint is right for digital and RF and wrong for a low-level analogue measurement.

---

## Hybrid, and why almost everything is

Real vehicles are hybrid, and the usual arrangement is single point for power and low-frequency signals, multipoint for high-frequency and shielding, with capacitive connections that are open at DC and closed at RF.

**The important part is not which scheme is chosen but that it is written down and enforced.** A grounding scheme that exists as a drawing and not as an inspection becomes multipoint by accident, one bracket at a time.

---

## Structure as a return path

Using the vehicle structure as the current return saves the return conductor, which on a large harness is half the copper.

**It requires the structure to be electrically continuous**, which a bolted composite airframe is not, and a joint with an anodised or painted faying surface is not either.

**It couples every current into the structure**, so a high-current return shares its path with everything else grounded to structure. That is exactly the ground loop problem above, at vehicle scale.

**And it removes the factor of two** from the [voltage drop calculation](HarnessDesign.md), which is a real harness saving and is the reason it keeps being proposed.

On a metallic vehicle with bonded joints it is a reasonable choice for power. On a composite vehicle it is usually not available at all, and a composite airframe therefore carries more harness than a metallic one for a reason that has nothing to do with the electrical design.

---

## Bonding

Bonding is the deliberate electrical connection of structure to structure, and it has its own set of jobs: fault current paths, static discharge, lightning, shield termination and RF reference.

**Bonding straps have inductance**, so a strap that is a good bond at DC can be a poor one at the frequency that matters. Short and wide beats long and thick.

**Faying surface bonds** need the finish removed and then protected, which is a process rather than a design, and it belongs to [aerospaceMaterials](../../aerospaceMaterials/) alongside the galvanic corrosion it can cause.

**Bonding is where grounding meets [mechanisms](../../mechanismsAndSeparation/)**: NASA-STD-5017B requires bonding and ground paths between moving and stationary parts sufficient to meet the electromagnetic requirements, and notes that bearings and gears should not be assumed to be either conductive or insulating.

---

## Why none of this is modelled

There is no scalar answer to model.

A grounding topology is judged by whether the resulting noise is below what the loads tolerate, and that is measured in an [EMC test](EMIAndEMC.md) rather than computed. A model that produced a number would be producing an unearned one.

What this domain does supply is the [harness resistance](HarnessDesign.md), which is the input a real grounding analysis would need, and the [firing circuit resistance](PyroCircuits.md) that the stray energy assessment in [mechanismsAndSeparation](../../mechanismsAndSeparation/docs/Pyrotechnics.md) consumes.

---

## Design rules of thumb

- **Decide the topology before the harness is drawn.** It is expensive to change afterwards.
- **Single point below, multipoint above.** The crossover is where the conductor becomes an inductor.
- **Write the scheme down and inspect against it.** It degrades one bracket at a time.
- **Short and wide bonding straps.** Inductance, not resistance.
- **Do not assume a composite structure is a return path.** It usually is not.

---

## Failure modes

**A single point ground long enough to be an inductor.** Single point at DC and multipoint above it, unintentionally.

**A ground loop through structure.** Two references at different potentials, and the difference appears as noise.

**A grounding scheme that exists only as a drawing.** Becomes hybrid by accident.

**Structure return assumed on a composite vehicle.** The continuity is not there.

**A bond that is good at DC and poor at RF.** Long, thin straps.

---

## References

- MIL-STD-464, *Electromagnetic Environmental Effects Requirements for Systems*, not read here
- NASA-STD-5017B, section 4.5 on bonding across moving interfaces
- [EMIAndEMC](EMIAndEMC.md), where the topology is judged
- [aerospaceMaterials](../../aerospaceMaterials/), for faying surface preparation and galvanic risk
