[Home](../README.md) > Hole Making

# Hole Making

## Contents

- [Overview](#overview)
- [The processes](#the-processes)
- [Why drilling is the weakest link](#why-drilling-is-the-weakest-link)
- [Deep holes](#deep-holes)
- [Fastener holes](#fastener-holes)
- [Cold expansion](#cold-expansion)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

A launch vehicle structure has tens of thousands of holes and most of them are fastener holes. They are the fatigue critical features of the structure, they are the poorest tolerance features produced by any machining process, and the way they are made decides the fatigue life of the joint.

---

## The processes

| Process | Tolerance | Ra | Notes |
|---|---|---|---|
| **Twist drilling** | IT10 to IT12 | 3.2 um | Fast, poor tolerance, poor location |
| **Reaming** | IT7 | 0.8 um | Finishes a drilled hole. Follows the existing axis |
| **Boring** | IT6 | 0.8 um | **Corrects the axis.** Single point |
| Gun drilling | IT9 | 1.6 um | Deep holes, high L/D |
| **Wire EDM** | IT7 | 1.6 um | Any hardness. Recast layer |
| Reamed and cold expanded | IT7 | 0.8 um | **The fatigue answer** |

**Reaming follows the hole it is given, boring corrects it.** That is the practical distinction and it decides which one a part needs. A reamer floats into the existing hole and improves its size and finish; it does not move the axis. A boring bar cuts on a single point at a commanded radius, so it produces a hole concentric with the spindle regardless of where the pilot was.

---

## Why drilling is the weakest link

| Problem | Cause |
|---|---|
| **Poor location** | The web wanders as the drill enters |
| **Oversize** | The two lips never cut identically |
| **Lobing** | A two-flute drill produces a slightly triangular hole |
| **Exit burr** | The material breaks out rather than being cut |
| **Poor perpendicularity** | The drill deflects |

**A drill is a poorly constrained tool.** It is long, slender, cuts on two edges that are never identical, and it is guided only by the hole it is making.

**Spot drilling or a stub drill pilot fixes the location**, by establishing a conical seat that the drill cannot wander from.

**Exit burrs are a real assembly problem**, not a cosmetic one. A burr under a fastener head or between two faying surfaces prevents proper clamp-up and it is a fatigue initiation site. Backing material, a reduced feed at breakthrough, and deburring are the answers.

**In stacked material the burr is between the layers** where it cannot be removed without disassembly, which is why aerospace assembly drills, disassembles, deburrs and reassembles, or uses one-shot drilling with the right parameters to avoid the interlaminar burr entirely.

---

## Deep holes

| L/D | Approach |
|---|---|
| Below 3 | Conventional twist drill |
| 3 to 5 | Peck drilling, through-tool coolant |
| **5 to 20** | **Gun drilling** |
| Above 20 | BTA or ejector drilling |

**Chip evacuation is the constraint.** A conventional drill relies on its flutes to carry chips out, and beyond a few diameters they pack, the torque rises and the drill breaks.

**Gun drills solve it with a single effective cutting edge, a V-shaped flute and high pressure coolant through the tool.** The coolant carries the chips out and supports the drill against the bore, so straightness is far better than a twist drill achieves.

**Straightness matters on a deep hole** and it is not a tolerance most drawings state. A twist drill can wander a millimetre in 100 mm; a gun drill holds a fraction of that.

---

## Fastener holes

**The fatigue critical feature of a riveted or bolted structure.**

| Requirement | Reason |
|---|---|
| **Size to fit class** | Interference or clearance, per the joint design |
| **Perpendicularity** | An angled hole loads the fastener in bending |
| **Surface finish** | It is a crack initiation site |
| **No burrs** | Clamp-up and initiation |
| **Edge distance** | Typically 2D minimum |
| No smearing or laps | Initiation sites |

**Hole quality dominates joint fatigue life**, and the difference between a well made and a poorly made hole is a factor of several in life. That is a larger effect than the fastener choice.

**Interference fit fasteners improve fatigue life** by putting the hole bore into compression, in the same way cold expansion does, and they require a correspondingly tighter hole tolerance.

**Drilling composite and metal stacks is a speciality** because the two materials want opposite parameters: composite wants high speed and low feed with a sharp diamond-coated tool to avoid delamination, and titanium wants low speed and high feed. One-shot stack drilling parameters are a compromise developed per stack.

---

## Cold expansion

**A mandrel is pulled through the hole, expanding it plastically and leaving a compressive residual hoop stress around the bore.**

| Property | Value |
|---|---|
| Radial expansion | 3 to 6 % |
| **Fatigue life improvement** | **3 to 10x** |
| Residual stress | Compressive, to roughly one radius deep |
| Process | Split sleeve, split mandrel, or direct |

**The fatigue improvement is very large** and it is the standard treatment for fatigue critical fastener holes in aircraft structure. A 3 to 10x life improvement from a process that takes seconds per hole is an unusually good trade.

**The mechanism is the same as shot peening**: a compressive residual stress at the crack initiation site delays initiation and slows early growth. The difference is that the compression here is deep, running to roughly one hole radius into the material.

**The hole is reamed to final size after expansion**, because the expansion leaves it oversize and slightly irregular.

**It cannot be applied everywhere.** It needs access to both faces, it needs sufficient edge distance and ligament, and it is not used in thin material where the expansion would simply bulge the sheet.

**The compression relaxes under high load excursions**, so the benefit is claimed against a spectrum that has been demonstrated rather than assumed indefinite.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Drilling is IT10 to IT12 | Ream or bore for anything better |
| Reaming follows, boring corrects | The axis |
| Spot drill for location | |
| Gun drill above L/D 5 | Chip evacuation and straightness |
| Edge distance | 2D minimum |
| Hole quality dominates joint fatigue | More than the fastener choice |
| Cold expansion | 3 to 10x fatigue life |
| Ream to size after expansion | |

---

## Failure modes

**Drilled hole assumed located to milling tolerance.** It is not.

**Reaming used to correct a misplaced hole.** It follows the existing axis.

**Burr left between stacked layers.** Clamp-up prevented, and an initiation site.

**Deep hole drilled with a twist drill.** Chip packing and breakage.

**Cold expansion applied with insufficient edge distance.** The ligament cracks.

**Composite parameters used on the metal layer of a stack.** Or the reverse.

**Cold expansion benefit assumed permanent.** It relaxes under high load excursions.

---

## Standards

| Standard | Scope |
|---|---|
| **NASM 33540** | Fastener hole preparation |
| **FAA AC 43.13** | Acceptable methods, techniques and practices |
| ASTM E466 | Force controlled constant amplitude axial fatigue tests |
| **MIL-HDBK-5 / MMPDS** | Joint allowables and hole quality effects |
| ISO 286 | Limits and fits |
| ASME Y14.5 | Dimensioning and tolerancing |
| FTI 8101 | Cold expansion process specification |

---

## References

1. ASM Handbook Volume 16, *Machining*.
2. Phillips, J. L., *Sleeve Coldworking Fastener Holes*, AFML-TR-74-10, 1974.
3. MMPDS-2023, *Metallic Materials Properties Development and Standardization*.
