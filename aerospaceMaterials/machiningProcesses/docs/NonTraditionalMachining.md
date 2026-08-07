[Home](../README.md) > Non-Traditional Machining

# Non-Traditional Machining

## Contents

- [Overview](#overview)
- [The processes](#the-processes)
- [EDM](#edm)
- [ECM](#ecm)
- [Waterjet](#waterjet)
- [Laser](#laser)
- [Choosing between them](#choosing-between-them)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

These processes remove material by something other than a cutting edge, which frees them from the hardness limit and from the cutting force. They pay for it in rate, in surface condition, or both.

---

## The processes

| Process | Mechanism | Tolerance | Affected layer | Force |
|---|---|---|---|---|
| **Wire EDM** | Spark erosion | IT7 | **Recast, 5 to 30 um** | **None** |
| **Sinker EDM** | Spark erosion | IT7 | Recast | None |
| **ECM** | Anodic dissolution | IT8 | **None** | None |
| **Abrasive waterjet** | Erosion | IT11 | **None** | Low |
| **Laser** | Melting and vaporisation | IT9 | **HAZ and recast** | None |
| Chemical milling | Etching | IT10 | None | None |

**Zero cutting force is the shared advantage** and it is what makes them viable for very thin, very delicate or very hard parts that a cutting tool would deflect or shatter.

---

## EDM

**Material is removed by a controlled spark discharge between a tool electrode and the workpiece, through a dielectric.**

| Variant | Detail |
|---|---|
| **Wire EDM** | A travelling wire cuts a 2D profile through the full thickness |
| **Sinker EDM** | A shaped electrode is sunk into the work, reproducing its form |
| Hole popping | A fast small hole drill, often to start a wire cut |

**It cuts anything conductive at any hardness**, which is the reason to use it. Hardened tool steel, carbide and superalloys are cut as easily as mild steel.

**Sharp internal corners are its geometric advantage.** A wire cut corner has the wire radius, which can be 0.1 mm, where a milled corner has the cutter radius. That is why die and mould work is EDM work.

**The recast layer is the cost.** Melted material resolidifies on the surface, 5 to 30 micrometres thick depending on the settings, and it is brittle, microcracked and in tensile residual stress.

| Setting | Recast |
|---|---|
| Roughing | 20 to 30 um |
| **Skim passes** | **5 um or less** |

**Skim passes reduce it and do not eliminate it.** On a fatigue critical surface the recast layer must be removed, by abrasive flow machining, by etching or by a light conventional cut. See [extrusionHoning](../../extrusionHoning/).

**Wire EDM leaves no force on the part**, so a very thin or very delicate feature can be cut without support. That combination, arbitrary hardness plus zero force plus sharp corners, is what it is for.

---

## ECM

**Anodic dissolution: the workpiece is the anode, a shaped tool is the cathode, and electrolyte flows between them.**

| Property | Detail |
|---|---|
| **No thermal or mechanical damage** | **This is the key property** |
| No tool wear | The tool does not touch the work |
| Any hardness | It is electrochemical |
| Tolerance | IT8 |
| Tooling | A shaped cathode per feature |

**It leaves no affected layer at all**, which distinguishes it from every other process here and from conventional machining too. No recast, no white layer, no residual stress, no work hardening.

**That is why it is used for turbine blade and blisk work**, where the fatigue requirement is severe and any surface damage is unacceptable.

**Precise ECM (PECM) with a pulsed supply and an oscillating tool** achieves much better tolerance and surface finish than conventional ECM, and it has become a real competitor to grinding for hard, complex, fatigue critical shapes.

**The tooling is the drawback.** Each feature needs a shaped cathode, developed iteratively, so it is a quantity process. Electrolyte handling and waste treatment are also real costs.

---

## Waterjet

**Abrasive garnet entrained in a water jet at 4000 bar erodes the material.**

| Property | Detail |
|---|---|
| **Cuts anything** | Metal, composite, glass, stone, stacks of dissimilar material |
| **No heat affected zone** | The cutting is mechanical and cold |
| Tolerance | IT11, and better on a good machine with taper compensation |
| **Taper** | The kerf is wider at the top |
| Thickness | Up to 200 mm |

**No HAZ is the main advantage** over laser and plasma. A waterjet cut edge in titanium or in a composite needs no subsequent removal of a damaged layer.

**Taper is the main limitation** and it comes from the jet losing energy as it descends. Dynamic taper compensation, which tilts the head, largely corrects it on modern machines.

**It is the standard route for cutting blanks from plate**, especially in titanium and in composites where thermal cutting would do damage.

**Delamination at entry is the composite failure mode** and it is controlled by piercing outside the part outline or by a low pressure pierce.

---

## Laser

**Melting and vaporisation by a focused beam, with an assist gas to clear the melt.**

| Property | Detail |
|---|---|
| **Very fast** | On thin material |
| **Narrow kerf** | 0.1 to 0.3 mm |
| **HAZ and recast** | The cost |
| Thickness | Practical to about 20 mm |
| No force | |

**It is the fastest route for thin sheet profiles** and it dominates sheet metal blanking.

**The HAZ is the aerospace concern.** A laser cut edge has a melted and resolidified layer with an altered microstructure beneath it, and on a fatigue critical edge it has to be removed.

**Reflective materials are difficult.** Aluminium and copper reflect at conventional CO2 wavelengths, which is why fibre lasers, at around 1 micrometre, displaced CO2 for those materials.

**Laser drilling of cooling holes** in turbine components is a major application, and percussion and trepanning variants trade rate against hole quality.

---

## Choosing between them

| Need | Process |
|---|---|
| Hard material, sharp internal corners | **Wire EDM** |
| **No affected layer at all** | **ECM** |
| Thick plate blanks, no HAZ | **Waterjet** |
| Thin sheet profiles, fast | **Laser** |
| Composite, no thermal damage | Waterjet |
| A complex 3D cavity in hard material | Sinker EDM |
| Large area thin-down on a formed skin | Chemical milling |

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Zero cutting force is the shared advantage | Thin, delicate, hard |
| EDM recast | 5 to 30 um, and it must be removed if fatigue matters |
| ECM leaves no affected layer | The reason for blisk work |
| Waterjet has no HAZ | And it tapers |
| Laser has a HAZ | And it is the fastest on thin sheet |
| EDM cuts any hardness | Conductive only |
| ECM needs a shaped cathode | A quantity process |

---

## Failure modes

**EDM recast layer left on a fatigue critical surface.** A brittle microcracked layer in tension.

**Waterjet taper ignored on a thick part.** The bottom of the cut is undersize.

**Laser cut edge used as a fatigue critical edge.** The HAZ is an initiation site.

**Composite waterjet pierced inside the part outline.** Delamination.

**ECM tooling developed for a low quantity.** It does not amortise.

**EDM attempted on a non-conductive material.** It does not work.

---

## Standards

| Standard | Scope |
|---|---|
| **AMS 2280** | Integrity of machined surfaces, including EDM |
| ISO 28881 | Electro discharge machines, safety |
| ASTM F3050 | Non-traditional machining processes |
| ASTM E1417 | Liquid penetrant testing |
| ISO 9013 | Thermal cutting, classification of cuts |
| AMS 2649 | Etch inspection for thermal damage |

---

## References

1. ASM Handbook Volume 16, *Machining*.
2. Jameson, E. C., *Electrical Discharge Machining*, Society of Manufacturing Engineers, 2001.
3. McGeough, J. A., *Advanced Methods of Machining*, Chapman and Hall, 1988.
