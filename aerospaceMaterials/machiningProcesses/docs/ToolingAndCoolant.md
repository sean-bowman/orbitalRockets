[Home](../README.md) > Tooling and Coolant

# Tooling and Coolant

## Contents

- [Overview](#overview)
- [Tool materials](#tool-materials)
- [Coatings](#coatings)
- [Geometry](#geometry)
- [Coolant](#coolant)
- [High pressure coolant](#high-pressure-coolant)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

The tool material, its coating, its geometry and the coolant delivery are four independent choices, and getting any of them wrong on a difficult alloy costs more than getting the speeds and feeds slightly wrong.

---

## Tool materials

| Material | Hot hardness | Toughness | Use |
|---|---|---|---|
| **High speed steel** | Low | **High** | Low speed, interrupted cuts, form tools |
| **Carbide** | Good | Good | **The general answer** |
| Cermet | Better | Lower | Finishing steel |
| **Ceramic** | **Very high** | **Low** | **Nickel alloys**, hard turning. Not titanium |
| **CBN** | Very high | Low | Hardened steel, nickel |
| **PCD** | Low (graphitises) | Low | **Aluminium, composites**. Not steel |

**Hot hardness and toughness trade against each other**, and the whole table is that trade. A ceramic runs at four times the carbide speed in Inconel and it shatters in an interrupted cut.

**Carbide grade matters as much as the family.** A fine grain high cobalt grade is tough and wears fast; a coarse grain low cobalt grade is wear resistant and chips. The ISO 513 classification groups them by application, and the letters are worth knowing: P for steel, M for stainless, K for cast iron, N for non-ferrous, S for superalloys and titanium, H for hardened material.

**PCD cannot cut steel.** Diamond dissolves in iron at cutting temperatures, so PCD is for aluminium, composites and non-ferrous work only.

**Ceramic cannot cut titanium**, for the analogous chemical reason.

---

## Coatings

| Coating | Property | Use |
|---|---|---|
| **TiN** | General purpose, gold coloured | Steel, general |
| **TiAlN / AlTiN** | **High temperature. Forms an alumina layer in service** | **Hard, dry and high speed work** |
| TiCN | Harder, tougher than TiN | Abrasive material |
| **AlCrN** | Very high temperature | Nickel alloys |
| **Diamond** | Extremely hard | Aluminium with silicon, composites |
| **Uncoated polished** | Low friction, sharp edge | **Aluminium** |

**TiAlN is the workhorse for difficult material.** At temperature the aluminium in it oxidises to form a thin alumina layer that is both hard and a thermal barrier, so the coating improves as it heats.

**Uncoated polished carbide is correct for aluminium**, which is counter-intuitive. A coating adds edge radius and surface energy, both of which promote built-up edge in aluminium. A sharp, polished, uncoated edge does not.

**Coatings do not fix a wrong substrate.** A coated tough grade in an application that needs wear resistance still wears.

---

## Geometry

| Feature | Effect |
|---|---|
| **Rake angle** | Positive reduces force and weakens the edge |
| **Helix angle** | Higher gives a smoother cut and more axial force |
| **Flute count** | More flutes for higher feed, fewer for chip space |
| **Edge preparation** | A hone strengthens the edge and raises the force |
| **Variable pitch** | **Disrupts the chatter regeneration** |

**Rake angle follows the material.** Aluminium gets 15 to 20 degrees positive; nickel and titanium get slightly positive to neutral, because the edge has to survive.

**Flute count follows the material's chip volume.** Aluminium removes a great deal of material and needs the chip space, so two or three flutes; nickel removes little and benefits from more engagement, so five to seven.

**Variable pitch and variable helix cutters are the cheapest chatter countermeasure available.** Unequal tooth spacing means successive teeth do not regenerate the same wave, which breaks the feedback loop directly. They are worth specifying by default on thin wall work. See [ChatterAndStability.md](ChatterAndStability.md).

---

## Coolant

| Type | Cooling | Lubrication | Notes |
|---|---|---|---|
| **Flood emulsion** | **Good** | Good | The general answer |
| Straight oil | Moderate | **Excellent** | Threading, broaching, gear cutting |
| **Minimum quantity lubrication** | Poor | Good | Environmentally driven, and it works in aluminium |
| **Dry** | None | None | Hardened steel, some cast iron |
| Cryogenic (LN2, CO2) | **Excellent** | None | Titanium, and it is specialised |

**Coolant does three jobs**: it removes heat, it lubricates the chip-tool interface, and it evacuates chips. On a deep pocket the third one is often the binding requirement.

**Dry machining is correct in a few places** and wrong in most. Hardened steel turning with CBN is done dry because the thermal shock of intermittent coolant cracks the tool, and the softening of the workpiece at temperature actually helps.

**Cryogenic machining of titanium is a real technique** with a real benefit, and it is not widely deployed because of the handling infrastructure.

---

## High pressure coolant

**Not a refinement. In titanium and nickel it is the enabling technology.**

| Pressure | Effect |
|---|---|
| 5 to 10 bar | Conventional flood |
| **70 bar** | **Penetrates the chip-tool interface. Breaks chips** |
| 200 to 350 bar | Substantial further tool life gains |

**A conventional flood jet does not reach the cutting zone.** The chip covers it and the coolant runs over the top. A high pressure jet aimed at the rake face penetrates under the chip and reaches the interface where the heat is.

**Tool life gains of 2 to 5x in titanium** are typical going from flood to 70 bar, and that is a larger effect than most tooling changes.

**It also breaks chips.** Titanium and stainless produce long stringy chips that wrap the tool and the part; a high pressure jet curls and breaks them, which is what makes unattended running possible.

**Through-tool delivery is required** for the jet to be aimed correctly, so the tooling, the holders and the spindle all have to support it. That is the real cost of high pressure coolant and it is a machine specification decision rather than a per-job one.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Hot hardness trades against toughness | The whole tool material table |
| ISO 513 letters | P steel, M stainless, K iron, N non-ferrous, S superalloy, H hard |
| No PCD in steel | Diamond dissolves in iron |
| No ceramic in titanium | Chemical attack |
| Uncoated polished carbide for aluminium | A coating promotes built-up edge |
| TiAlN for hot work | It improves as it heats |
| Variable pitch for chatter | The cheapest countermeasure |
| High pressure coolant in titanium | 70 bar, 2 to 5x tool life |

---

## Failure modes

**PCD used on steel.** It graphitises immediately.

**Ceramic used in titanium.** Chemical attack.

**Coated tooling in aluminium.** Built-up edge from the edge radius.

**Flood coolant assumed to reach the cutting zone.** The chip blocks it.

**High pressure coolant specified without through-tool holders.** It cannot be aimed.

**Intermittent coolant on a CBN hard turning tool.** Thermal cracking.

**Two flute cutter in Inconel.** Too little engagement, and the chip space is not needed.

---

## Standards

| Standard | Scope |
|---|---|
| **ISO 513** | Classification and application of hard cutting materials |
| ISO 3685 | Tool life testing with single point turning tools |
| ISO 8688 | Tool life testing in milling |
| ISO 1832 | Indexable inserts, designation |
| **OSHA / ACGIH** | Metalworking fluid exposure limits |
| ASTM E2693 | Evaluating metalworking fluid mist |

---

## References

1. Shaw, M. C., *Metal Cutting Principles*, 2nd ed., Oxford University Press, 2005.
2. Ezugwu, E. O., "High Speed Machining of Aero-Engine Alloys", *Journal of the Brazilian Society of Mechanical Sciences*, Vol. 26, 2004.
3. ASM Handbook Volume 16, *Machining*.
