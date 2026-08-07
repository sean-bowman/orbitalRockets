[Home](../README.md) > Vibratory Finishing

# Vibratory Finishing

## Contents

- [Overview](#overview)
- [The process](#the-process)
- [Media](#media)
- [What it achieves](#what-it-achieves)
- [What it rounds that you wanted sharp](#what-it-rounds-that-you-wanted-sharp)
- [Additive applications](#additive-applications)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Parts and abrasive media are tumbled together in a vibrating bowl. The media rubs against the part, breaking edges and reducing surface roughness. It is cheap, it is batch, and it is remarkably effective on external surfaces.

It reaches nothing internal, and it rounds every edge it touches.

---

## The process

| Element | Role |
|---|---|
| **Bowl** | Vibrates, circulating the mass |
| **Media** | Ceramic, plastic or steel shapes that do the work |
| **Compound** | Water plus a chemical that cleans, lubricates and carries away swarf |
| **Time** | Hours. The control parameter |

**Material removal is very low** and the effect is progressive. A cycle is measured in hours rather than minutes, and the outcome is set by time more than by anything else.

**It is a batch process.** Parts are loaded together, and part-on-part impingement is a real damage mechanism on anything delicate. Compartmented bowls or part fixtures prevent it at the cost of throughput.

---

## Media

| Media | Cut rate | Finish | Use |
|---|---|---|---|
| **Ceramic** | High | Moderate | Deburring and general |
| **Plastic** | Low | Fine | Soft alloys, and finishing after ceramic |
| **Steel** | Very low | Bright | Burnishing rather than cutting |
| Organic (walnut, corn cob) | Very low | Polish | Final polishing, and drying |

**Shape matters as much as material.** Angled cut triangles and cones reach into corners; spheres do not. Media that lodges in a hole or a slot has to be removed by hand, and media selection is partly a matter of picking a shape that cannot get stuck in the part.

**Media wears and it has to be topped up and periodically screened**, because worn media is smaller and it starts lodging in places fresh media does not.

---

## What it achieves

| Outcome | Detail |
|---|---|
| **Edge break** | The primary purpose. Consistent radii on every edge |
| **Ra improvement** | From perhaps 3 um to under 1 um with a fine media |
| **Burr removal** | Effective on accessible burrs |
| Compressive stress | With steel media, a light peening effect |
| Cleaning | The compound does real work |

**Consistent edge break is the real value.** Hand deburring produces a variable radius that depends on the operator; vibratory finishing produces the same radius everywhere, which matters when the edge break is a fatigue requirement.

---

## What it rounds that you wanted sharp

**The process cannot distinguish a burr from a feature.**

| Feature | Risk |
|---|---|
| **Sharp orifice entry** | Rounded, and the discharge coefficient changes |
| **Sealing edges** | Rounded, and a knife edge seal stops sealing |
| Datum edges | Rounded, and the datum moves |
| Thread crests | Rounded |
| Fine detail | Softened |

**A sharp-edged orifice was sized sharp**, and rounding its entry changes its discharge coefficient measurably. See [fluidSystems Orifices.md](../../../fluidSystems/fluidSystemsLibrary/docs/Orifices.md), where entry geometry is a primary Cd driver.

**Masking is possible and it is awkward** in a tumbling process. The practical answer is usually to vibratory finish before the critical feature is machined, which puts it in the process sequence rather than treating it as a finishing operation.

---

## Additive applications

Vibratory finishing is a natural fit for additive parts, on external surfaces only.

| Application | Notes |
|---|---|
| **Removing partially sintered particles** | Effective, and it is the main use |
| Support witness marks | Reduces them; it does not remove a support stub |
| General Ra reduction | 20 um to perhaps 5 um on an external surface |
| Edge break on printed edges | Consistent, where hand work is not |

**It reaches nothing internal.** An additive part with internal passages needs abrasive flow machining for those, and vibratory finishing handles the outside. The two are complementary and neither substitutes for the other. See [extrusionHoning](../../extrusionHoning/).

**Media lodging in an additive part is a real risk**, because additive parts have pockets and lattices that media enters and cannot leave. That has to be considered at design time.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| External surfaces only | Nothing internal |
| Cycle time | Hours |
| Ra achievable | Under 1 um with fine media |
| Edge break | Consistent, which is the real value |
| It cannot distinguish a burr from a feature | Mask, or sequence around it |
| Media shape | Chosen so it cannot lodge in the part |
| Part-on-part impingement | Real. Compartment delicate parts |
| Complementary to abrasive flow | Outside and inside |

---

## Failure modes

**A sharp orifice entry rounded.** The discharge coefficient changed.

**Media lodged in a lattice or pocket.** Removed by hand, or not at all.

**Part-on-part impingement.** Dents on a delicate part.

**Expected to reach an internal passage.** It does not.

**Worn media not screened.** It lodges where fresh media does not.

**Datum edge rounded.** The datum moved.

---

## Standards

| Standard | Scope |
|---|---|
| ISO 13715 | Edges of undefined shape, indication and dimensioning |
| ASME B46.1 | Surface texture |
| ISO 4287 / 21920 | Surface texture |
| ASTM F3301 | Post-processing methods for metal additive parts |

---

## References

1. Davidson, D. A., "Mass Finishing Processes", *Metal Finishing*, Vol. 105, 2007.
2. Gillespie, L. K., *Deburring and Edge Finishing Handbook*, SME, 1999.
3. ASTM F3301-18, *Standard for Additive Manufacturing -- Post Processing Methods*.
