[Home](../README.md) > Forging

# Forging

## Contents

- [Overview](#overview)
- [Open die and closed die](#open-die-and-closed-die)
- [Grain flow](#grain-flow)
- [Short transverse](#short-transverse)
- [Forging temperature](#forging-temperature)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Forging is bulk deformation of a heated billet between dies. It produces the highest and most reliable properties of any metal forming route, and it does so by controlling the grain flow rather than by any change of composition.

---

## Open die and closed die

| Type | Detail | Tolerance | Tooling | Use |
|---|---|---|---|---|
| **Open die** | Flat or simple dies, the material spreads freely | Coarse | **Very low** | Large simple shapes, preforms |
| **Closed die** | The material fills a shaped cavity | IT9 to IT11 | **High** | Net shape parts, at quantity |
| Blocker | An intermediate closed die stage | Coarse | Medium | Preform for the finisher |
| Precision | Closed die with tight control | IT8 | Very high | Near net shape, minimal machining |

**Open die forging is how large billets and preforms are made**, including the cylinders that flow forming starts from. It needs almost no tooling, it is slow, and its dimensional control is poor.

**Closed die forging is a quantity process.** The die set is a major investment with a long lead time, typically 24 weeks, and it pays back only across many parts.

**Precision forging approaches net shape**, which is attractive when the alloy is expensive. The die cost is higher again and the process window is narrower.

---

## Grain flow

**The reason to forge, and it is a geometric property rather than a metallurgical one.**

Deformation elongates the grains and aligns the inclusion stringers along the direction of material flow. In a well designed forging that flow follows the part contour, so the grain runs along the load path.

| Route | Grain flow |
|---|---|
| **Forged** | **Follows the contour** |
| Machined from plate | Straight through, cut at every contour |
| Cast | None, or dendritic |

**Properties are highest along the grain flow.** A forged hook, crankshaft or lug carries its load along the flow direction and gets the best of the material.

**A machined part cuts through the flow**, exposing the ends of the elongated grains and the inclusion stringers at the machined surface. That is why a machined lug and a forged lug of the same alloy have different fatigue lives.

**Die design is grain flow design.** The die cavity and the preform shape together determine where the material flows, and a forging drawing normally specifies the required flow pattern with a macro-etch acceptance requirement.

---

## Short transverse

**The direction with the worst properties, and the one most often overlooked.**

| Orientation | Definition | Relative properties |
|---|---|---|
| **L, longitudinal** | Along the principal working direction | Best |
| **LT, long transverse** | Across, in the working plane | Good |
| **ST, short transverse** | **Through the thickness** | **Worst** |

**The short transverse direction is loaded across the flattened grains and across the inclusion stringers**, which is the direction in which those features act most like defects.

| Property | ST penalty |
|---|---|
| Yield strength | Small, 5 to 10 % |
| **Elongation** | **Large, often half** |
| **Fracture toughness** | **Large** |
| **Stress corrosion threshold** | **Large. This is the critical one** |

**Stress corrosion cracking in aluminium is overwhelmingly a short transverse problem.** 7075-T6 has an ST `K_ISCC` that is a fraction of its L value, and that single fact is the reason T73 and T7451 tempers exist.

**A part machined from a thick forging can end up loaded in ST** without anyone noticing, because the orientation is a property of the stock and the drawing usually does not show it. **Specifying the forging orientation relative to the part axes is the fix**, and it belongs on the drawing.

See [wroughtMaterials](../../wroughtMaterials/) for the full treatment.

---

## Forging temperature

| Family | Forging range |
|---|---|
| Aluminium | 350 to 450 degC |
| Titanium | 900 to 980 degC, below the beta transus |
| Steel | 1050 to 1250 degC |
| Nickel | 1000 to 1150 degC |

**Titanium's beta transus is the constraint that matters.** Forging above it produces a coarse transformed beta structure with poor ductility and fatigue properties; forging just below it, in the alpha-beta field, gives the fine equiaxed structure that Ti-6Al-4V is specified for.

**The transus is composition dependent**, around 995 degC for Ti-6Al-4V, and the forging window is therefore narrow and lot specific.

**Aluminium's window is narrow at the top too**, because incipient melting at the grain boundaries begins not far above the forging range and it is unrecoverable.

**Nickel alloys are forged hot and they work harden fast**, so they need frequent reheats and they are hard on dies.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Forge for grain flow | It is the reason |
| Grain flow follows the contour | And properties follow the flow |
| Short transverse is the worst direction | Especially for SCC |
| Specify the forging orientation | It is not on most drawings and it should be |
| Titanium below the beta transus | ~995 degC for Ti-6Al-4V |
| Closed die lead time | ~24 weeks |
| Open die for preforms | Almost no tooling |
| Macro-etch to verify flow | It is an acceptance requirement |

---

## Failure modes

**Part machined from a forging loaded in ST.** Low toughness and low SCC threshold.

**Titanium forged above the beta transus.** Coarse structure, poor fatigue.

**Aluminium overheated.** Incipient grain boundary melting, and it is unrecoverable.

**Grain flow not specified.** The forger optimises for die fill instead.

**Laps from poor preform design.** A folded surface, and it is a crack.

**Closed die tooling ordered for a low quantity.** It never amortises.

---

## Standards

| Standard | Scope |
|---|---|
| **AMS 2380 / AMS 4127 etc.** | Aluminium alloy forgings, by alloy |
| AMS 4928 | Ti-6Al-4V bars, forgings and rings, annealed |
| **AMS 2154** | Ultrasonic inspection of wrought metal products |
| ASTM A788 | Steel forgings, general requirements |
| ASTM B247 | Aluminium alloy die and hand forgings |
| **MIL-STD-2154** | Ultrasonic inspection |
| ASTM E381 | Macroetch testing of steel, for grain flow |

---

## References

1. ASM Handbook Volume 14A, *Metalworking: Bulk Forming*.
2. Altan, T., Ngaile, G. and Shen, G., *Cold and Hot Forging: Fundamentals and Applications*, ASM International, 2005.
3. Boyer, R., Welsch, G. and Collings, E. W., *Materials Properties Handbook: Titanium Alloys*, ASM International, 1994.
