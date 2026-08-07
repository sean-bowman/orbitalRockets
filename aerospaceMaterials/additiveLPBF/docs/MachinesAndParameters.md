[Home](../README.md) > Machines and Parameters

# Machines and Parameters

## Contents

- [Overview](#overview)
- [The machine axes that matter](#the-machine-axes-that-matter)
- [Build volume](#build-volume)
- [Laser count and overlap zones](#laser-count-and-overlap-zones)
- [Gas flow](#gas-flow)
- [Machine qualification](#machine-qualification)
- [Parameter transfer](#parameter-transfer)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Machines differ in ways that matter to the part and in ways that do not. Build volume and laser count are the obvious ones. Gas flow and beam calibration are the ones that decide whether a parameter set transfers, and they are rarely in a specification.

---

## The machine axes that matter

| Axis | Typical range | Why it matters |
|---|---|---|
| **Build volume** | 250 to 400 mm cube | The hardest constraint in the process |
| **Laser count** | 1 to 12 | Throughput, and the overlap zone problem |
| **Laser power** | 200 to 1000 W per laser | Copper and aluminium need the top of the range |
| **Spot size** | 60 to 100 um | Enters the normalised enthalpy to the three-halves power |
| **Layer thickness** | 20 to 100 um | Cost against resolution |
| **Gas flow** | Uniform or not | The variable nobody specifies and everybody suffers |
| **Preheat** | Ambient to 500 degC | Required for crack-prone alloys |

---

## Build volume

**The hardest constraint in the process.** A part larger than the build volume is not a slow part, it is a different part: it has to be split and joined, and the joint reintroduces exactly what the process was meant to remove.

Splitting is not free:

- The joint carries its own knockdown. See [aerospaceMaterials Allowables](../../docs/AllowablesAndStatistics.md)
- The joint has to be inspectable, which usually means it has to be accessible
- Two builds cost two setups
- The split surfaces need machining, so datums have to exist

**Design to the build volume of a machine you can actually get time on**, not to the largest machine in a brochure. Machine availability is a real constraint and a part that needs the one 400 mm machine in the region has a supply chain of one.

---

## Laser count and overlap zones

More lasers means proportionally more throughput and one new failure mode.

**Where two lasers meet, the material is melted twice with a different thermal history from anywhere else.** That overlap zone, sometimes called the stitch line, is a real feature of the part and it has been shown to carry reduced fatigue properties in some systems.

| Control | Effect |
|---|---|
| Overlap zone position controlled in the build file | Keep it out of high stress regions |
| Rotated between layers | Stops the stitch stacking vertically |
| Qualified as a feature | The honest approach for a fracture critical part |

**For a fracture critical part, either place the overlap deliberately or use a single laser machine.** Discovering a stitch line running through a highly stressed section after the fact is a requalification.

---

## Gas flow

**The most consequential machine variable that never appears in a specification.**

Inert gas flows across the build to remove the plume of vapour and spatter above the melt pool. If it does not, the plume attenuates and scatters the beam, and the spatter falls back onto the powder bed and gets melted into the next layer.

| Symptom | Cause |
|---|---|
| Porosity that varies with position on the plate | Non-uniform gas flow |
| Parts downstream of others building worse | Spatter carried across the bed |
| Density that varies build to build | Filter loading changing the flow |

**Position on the build plate is a process variable** for exactly this reason, and it is why witness coupon placement is a specification item rather than a convenience. See [Qualification.md](Qualification.md).

**Filters load and the flow changes.** A machine that produced good parts last month and produces porous ones now, at identical parameters, usually has a loaded filter.

---

## Machine qualification

Per MSFC-SPEC-3717 and NASA-STD-6030, a qualified machine has:

- Laser power calibrated and verified, at the build plane rather than the source
- Beam profile and spot size measured
- Scanner positional accuracy verified
- Oxygen level monitored and recorded
- Gas flow velocity mapped across the plate
- Recoater condition controlled
- A maintenance record, and a demonstration that a service did not change the output

**The last one is the one that gets skipped.** A machine serviced between builds is a changed machine until it has been demonstrated otherwise, and a laser replacement in particular is a requalification.

---

## Parameter transfer

**A parameter set does not transfer between machines and treating it as though it does is the commonest cause of an unexplained porous build.**

What differs even between two machines of the same model:

| Variable | Effect |
|---|---|
| Actual laser power at the build plane | Optics degrade; the source setting is not the delivered power |
| Beam profile | A slightly different spot changes the normalised enthalpy by the three-halves power |
| Gas flow field | Different plumbing, different filter state |
| Recoater condition | A worn blade lays a different layer |
| Powder lot | See [PowderAndFeedstock.md](PowderAndFeedstock.md) |

**Transfer is an equivalency exercise, not a file copy.** The receiving machine builds the same coupons, they are tested, and the results are compared against agreed criteria. That is 18 to 30 specimens, and it is what NCAMP and the NASA additive standards exist to structure.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Design to a machine you can get time on | Not the largest in a brochure |
| Splitting a part | Reintroduces the joint the process removed |
| Multi-laser overlap zones | Place deliberately or use a single laser |
| Position on the plate | A process variable, not a convenience |
| A machine service | A change until demonstrated otherwise |
| Parameter transfer | An equivalency exercise, 18 to 30 specimens |

---

## Failure modes

**A part designed for a 400 mm machine and built on a 250.** Split, joined, and requalified.

**A stitch line through a fracture critical section.** Discovered after the fact.

**Porosity that varies across the plate.** Gas flow, and it is not a parameter problem.

**A parameter set copied between machines.** Unexplained porosity.

**A laser replaced and the machine not requalified.** The delivered power changed.

---

## Standards

| Standard | Scope |
|---|---|
| **MSFC-SPEC-3717** | Control and qualification of LPBF processes |
| NASA-STD-6030 | Additive manufacturing requirements |
| ISO/ASTM 52904 | Process characteristics and performance |
| ISO/ASTM 52941 | Acceptance tests for laser metal PBF machines |
| ASTM F3303 | Process characteristics for critical applications |

---

## References

1. MSFC-SPEC-3717, *Specification for Control and Qualification of Laser Powder Bed Fusion Metallurgical Processes*.
2. Ferrar, B. et al., "Gas Flow Effects on Selective Laser Melting Productivity and Consistency", *Journal of Materials Processing Technology*, Vol. 212, 2012.
3. Anwar, A. B. and Pham, Q. C., "Selective Laser Melting of AlSi10Mg: Effects of Scan Direction and Gas Flow", *Journal of Materials Processing Technology*, Vol. 240, 2017.
