[Home](../README.md) > Wrought Materials Overview

# Wrought Materials Overview

## Contents

- [Overview](#overview)
- [Why this sub-domain has no library](#why-this-sub-domain-has-no-library)
- [The three axes](#the-three-axes)
- [The families](#the-families)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [Document index](#document-index)
- [References](#references)

---

## Overview

Wrought material is metal that has been mechanically worked from a cast ingot into a product form: plate, sheet, bar, extrusion, forging, tube. It is the baseline against which every other route is knocked down, and the reason is the grain structure that working produces.

A wrought allowable is the number in the handbook with no factor applied. Everything else in this domain is a fraction of it.

---

## Why this sub-domain has no library

**Deliberately, and the reasoning matters more than the verdict.**

Product form, temper and orientation are not calculations. They are **axes of the material database**, already present as the `conditions` and `orientation` dimensions of `MATERIAL_DATABASE`.

**A class whose `calculate` method looks up what T73 means is exactly the class not to build.** It would duplicate the database, it would drift from it, and it would add a layer between the user and the data for no analytical benefit.

**What this sub-domain contributes is knowledge**: what the designations mean, which orientation is dangerous, what a specification actually guarantees, and what the procurement lead times are. That is documentation, not code.

**The calculation entry point is [`queryMaterial`](../../aerospaceMaterialsLibrary/MaterialDatabase.py)**, which takes the alloy, the condition, the temperature, the orientation and the basis and returns the property with its provenance.

---

## The three axes

| Axis | What it is | Where it lives |
|---|---|---|
| **Product form** | Plate, sheet, bar, extrusion, forging, tube | Affects the achievable properties and the section thickness |
| **Temper or condition** | The thermal and mechanical processing state | The `conditions` dimension of the database |
| **Orientation** | L, LT, ST relative to the working direction | The `orientation` dimension |

**All three have to be specified for a property to mean anything.** "7075 yield strength" is not a number; "7075-T73 plate, ST orientation, A-basis, 25 mm thickness" is.

**Orientation is the one most often omitted**, and it is the one that causes structural failures. See [GrainDirection.md](GrainDirection.md).

---

## The families

| Family | Density | Strengthening | Where it is used |
|---|---|---|---|
| **Aluminium** | 2700 | Precipitation, work | **Primary structure, tanks** |
| **Stainless** | 8000 | Work, precipitation | Fluid systems, cryogenic, fittings |
| **Nickel** | 8200 | Precipitation, solid solution | **Hot sections, high pressure** |
| **Titanium** | 4430 | Alpha-beta processing | **High specific strength, COPV bosses** |
| Steel | 7850 | Martensite, tempering | Fasteners, landing gear, high strength |
| Copper | 8900 | Precipitation, dispersion | **Regenerative chamber liners** |

**Aluminium dominates by mass** in a launch vehicle because tanks dominate the structure and aluminium is the right answer for a tank.

**Titanium appears where the specific strength justifies its cost and its LOX incompatibility does not disqualify it**, which is a narrower set than its properties suggest.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Wrought is the baseline | Everything else is a fraction of it |
| Specify form, temper and orientation | All three, or the number means nothing |
| ST is the dangerous orientation | Especially for SCC |
| Thickness reduces properties | Quench rate falls with section |
| The database is the entry point | Not a class in this sub-domain |

---

## Failure modes

**Orientation omitted from a property call.** Silently the best direction.

**Handbook property used without the product form.** Sheet and plate differ.

**Temper assumed from the alloy number.** 7075-T6 and 7075-T73 differ by 15 % in strength and by a factor in SCC resistance.

**Thickness effect ignored.** A 100 mm plate does not have 12 mm plate properties.

---

## Standards

| Standard | Scope |
|---|---|
| **MMPDS** | Metallic materials properties development and standardization |
| **ANSI H35.1** | Alloy and temper designation systems for aluminium |
| ASTM B209 / B211 / B221 | Aluminium sheet, bar and extrusion |
| ASTM A240 / A276 | Stainless plate and bar |
| AMS specifications | Per alloy and form |
| SAE AMS-STD-2154 | Ultrasonic inspection of wrought metals |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterialsLibrary')

from MaterialDatabase import queryMaterial

for orientation in ('L', 'LT', 'ST'):
    value = queryMaterial('7075-T73', 't73', orientation = orientation, basis = 'A')
    print(f'{orientation:3s} A-basis yield {value["yieldStrength"]/1e6:.0f} MPa')
```

---

## Document index

| Document | Covers |
|---|---|
| [ProductForms.md](ProductForms.md) | Plate, sheet, bar, extrusion, forging, tube |
| [TemperDesignations.md](TemperDesignations.md) | The T, H and O systems and what they mean |
| [GrainDirection.md](GrainDirection.md) | L, LT, ST, and why ST is dangerous |
| [ThicknessEffects.md](ThicknessEffects.md) | Quench rate, section size, property fall-off |
| [AluminiumAlloys.md](AluminiumAlloys.md) | The 2000, 6000, 7000 series and Al-Li |
| [StainlessSteels.md](StainlessSteels.md) | Austenitic, PH, and where each belongs |
| [NickelAlloys.md](NickelAlloys.md) | IN718, IN625, Monel, Haynes |
| [TitaniumAlloys.md](TitaniumAlloys.md) | Ti-6Al-4V, ELI, CP grades, Ti-3Al-2.5V |
| [CopperAlloys.md](CopperAlloys.md) | GRCop-42, NARloy-Z, C18150 |
| [SpecificationsAndProcurement.md](SpecificationsAndProcurement.md) | What a spec guarantees, lead times, certification |
| [Inspection.md](Inspection.md) | Ultrasonic, chemistry, mechanical acceptance |
| [MaterialSubstitution.md](MaterialSubstitution.md) | When an equivalent is not equivalent |
| [ProcessComparison.md](ProcessComparison.md) | Wrought against cast and additive |

---

## References

1. MMPDS-2023, *Metallic Materials Properties Development and Standardization*.
2. Campbell, F. C., *Manufacturing Technology for Aerospace Structural Materials*, Elsevier, 2006.
3. ASM Handbook Volume 1 and 2, *Properties and Selection*.
