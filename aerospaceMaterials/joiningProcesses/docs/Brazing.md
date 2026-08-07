[Home](../README.md) > Brazing

# Brazing

## Contents

- [Overview](#overview)
- [Brazing against welding and soldering](#brazing-against-welding-and-soldering)
- [Joint clearance](#joint-clearance)
- [Filler selection](#filler-selection)
- [The processes](#the-processes)
- [Joint design](#joint-design)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Brazing joins with a filler that melts and the parent that does not. The joint strength comes from the lap area rather than from the filler's strength, and that is the single most important thing about designing one.

---

## Brazing against welding and soldering

| | Soldering | Brazing | Welding |
|---|---|---|---|
| Filler melting point | Below 450 degC | **Above 450 degC** | -- |
| Parent melts | No | **No** | Yes |
| Strength | Low | **Moderate to high** | Parent |
| Dissimilar metals | Excellent | **Excellent** | Limited |
| Distortion | Very low | **Low** | Higher |

**The parent does not melt**, which is what makes brazing the answer for dissimilar metals and for thin sections. There is no fusion zone, no dilution and no intermetallic formation from melting the two parents together.

**Uniform heating means low distortion**, especially in furnace brazing where the whole assembly comes to temperature together.

---

## Joint clearance

**The most important brazing design parameter and the one most often wrong.**

| Clearance | Result |
|---|---|
| **Too tight (below ~0.02 mm)** | The filler cannot flow in |
| **0.025 to 0.125 mm** | **The target. Capillary action fills the joint** |
| Too loose (above ~0.25 mm) | **Capillary action fails.** Voids, and low strength |

**Capillary action is what fills the joint**, and it works only within a narrow clearance band. A joint that is too loose does not fill and a joint that is too tight does not either.

**Clearance is specified at brazing temperature, not at room temperature.** That matters for dissimilar metals: a stainless sleeve on a copper shaft has a different clearance at 1000 degC than at 20 degC, and the difference can be larger than the target clearance itself.

**A joint between materials of different expansion has to be designed for the hot clearance**, which sometimes means an interference fit cold or a large gap cold. Getting this backwards produces a joint that has zero clearance at temperature and does not fill.

---

## Filler selection

| Filler family | Temperature | Use |
|---|---|---|
| **Silver (BAg)** | 620 to 870 degC | General purpose, low temperature. **Contains cadmium in some grades** |
| **Copper (BCu)** | 1080 to 1120 degC | Furnace brazing steel, high strength |
| **Nickel (BNi)** | 900 to 1200 degC | **High temperature, corrosion resistant.** Aerospace |
| Aluminium (BAlSi) | 570 to 620 degC | Aluminium. Very narrow window |
| Gold (BAu) | 900 to 1050 degC | Vacuum electronics, oxidation resistance |

**Nickel fillers are the aerospace choice** for hot structure, heat exchangers and engine hardware, because they retain strength at temperature and resist oxidation.

**Aluminium brazing has a very narrow window** because the filler melting point is close to the parent's. A 20 degC overshoot melts the part.

**Cadmium bearing silver fillers are being phased out** on toxicity grounds and cadmium-free equivalents exist at slightly higher temperature.

**The filler's own strength is rarely the limit** because the joint is in shear over a large lap area. Joint area is the design variable.

---

## The processes

| Process | Atmosphere | Use |
|---|---|---|
| **Furnace, vacuum** | Vacuum | **Aerospace. Clean, no flux, uniform** |
| Furnace, hydrogen | Reducing | Steel, copper |
| Torch | Flux | Repair, small quantity |
| Induction | Flux or controlled | Localised, at rate |
| Dip | Molten salt | Aluminium |

**Vacuum furnace brazing is the aerospace standard** because it needs no flux, so there is no flux residue to trap and corrode, and the heating is uniform so the distortion is minimal.

**Flux residue is a real problem** in any fluxed process. It is corrosive, it is trapped in the joint where it cannot be removed, and it is a known long term failure mode. Vacuum brazing avoids it entirely.

**Fixturing has to accommodate expansion.** An assembly fixtured rigidly at room temperature and heated to 1100 degC will either distort or open the joint clearance, depending on the fixture material.

---

## Joint design

| Rule | Detail |
|---|---|
| **Lap, not butt** | The strength is the lap area |
| **Lap length 3x the thinner member** | The usual starting point |
| **Loaded in shear** | Brazed joints are weak in peel and cleavage |
| Filler placement | Preplaced ring or foil, drawn through by capillarity |
| **Venting** | A closed joint traps gas and does not fill |
| Fit-up | Self-locating features, since the joint moves at temperature |

**Butt joints have almost no area** and they are the commonest brazing design error. A butt brazed tube is as strong as the filler across the tube wall section, which is a small fraction of what a lapped socket joint gives.

**Peel and cleavage loading must be avoided.** The joint is a thin layer and any loading that opens it acts on a very small area. Design so the load is shear across the lap.

**Venting a closed joint** is easy to overlook. A blind socket with no vent traps the air, which cannot escape as the filler flows in, and the joint fills partially.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Clearance 0.025 to 0.125 mm | **At brazing temperature** |
| Lap, not butt | The area is the strength |
| Lap length 3x the thinner member | |
| Shear, not peel or cleavage | |
| Nickel fillers for aerospace hot structure | |
| Vacuum furnace brazing | No flux residue |
| Vent closed joints | |
| Design the clearance for dissimilar expansion | It can invert |

---

## Failure modes

**Clearance specified cold on a dissimilar joint.** Wrong at temperature.

**Butt joint.** Almost no area.

**Joint loaded in peel.** A thin layer opened.

**Closed joint unvented.** Partial fill.

**Flux residue trapped.** Long term corrosion.

**Aluminium brazing overshoot.** The part melts.

**Filler strength used as the joint strength.** The area governs.

---

## Standards

| Standard | Scope |
|---|---|
| **AWS C3.6** | Furnace brazing |
| AWS C3.7 | Aluminium brazing |
| **AMS 2665 / 2675** | Brazing, silver and nickel |
| **ASME BPVC Section IX** | Brazing procedure and performance qualification |
| AWS A5.8 | Filler metals for brazing |
| AWS BRH | Brazing handbook |
| ASTM E1417 / E2375 | Penetrant and ultrasonic |

---

## References

1. Schwartz, M. M., *Brazing*, 2nd ed., ASM International, 2003.
2. AWS, *Brazing Handbook*, 5th ed., American Welding Society, 2007.
3. Messler, R. W., *Joining of Materials and Structures*, Butterworth-Heinemann, 2004.
