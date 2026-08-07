[Home](../README.md) > Nickel and Superalloys

# Nickel and Superalloys

## Contents

- [Overview](#overview)
- [Solid solution versus precipitation hardened](#solid-solution-versus-precipitation-hardened)
- [Inconel 718](#inconel-718)
- [Inconel 625](#inconel-625)
- [Monel](#monel)
- [The high temperature alloys](#the-high-temperature-alloys)
- [Welding](#welding)
- [Cost and lead time](#cost-and-lead-time)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Nickel alloys are what you reach for when temperature or corrosion rules out everything else. They are face-centred cubic, so unlike steel they stay tough at cryogenic temperature as well, which makes Inconel 718 unusual: one of very few alloys that is simultaneously a hot section material and a cryogenic pressure vessel material.

They are also expensive, long lead and hard to machine, so the decision to use one is usually forced rather than chosen.

---

## Solid solution versus precipitation hardened

This is the dividing line that governs everything downstream, especially welding.

| Mechanism | Alloys | Strength | Weldable as-is |
|---|---|---|---|
| **Solid solution** | 625, Hastelloy X, Haynes 230 | Moderate | **Yes** |
| **Precipitation hardened** | 718, Monel K-500 | High | No, needs post-weld solution and age |

**A precipitation hardened alloy welded in the aged condition has a soft spot at the weld** and it does not recover without a full solution treat and age of the assembly. Welding in the aged condition also risks strain age cracking, where the gamma prime precipitates during cooling and cracks the heat affected zone.

The practice that follows is: **weld in the solution annealed condition, then age the whole assembly.** That constrains the build sequence, because the aging cycle has to be compatible with everything else already attached.

---

## Inconel 718

The workhorse. Roughly half of all aerospace superalloy tonnage.

| Property | Value |
|---|---|
| Yield strength (STA) | 1034 MPa |
| Ultimate strength (STA) | 1276 MPa |
| A-basis ultimate, L | 1234 MPa |
| Density | 8190 kg/m3 |
| Useful to | ~925 K |
| Yield at 20 K | 1.18x room temperature |
| Fracture toughness | 96 MPa-sqrt(m) |
| Hydrogen notched ratio | 0.55 |

**The temperature range is the selling point.** It carries 88 percent of its room temperature yield at 800 K and 118 percent at 20 K, so a single alloy covers a turbopump from the cryogenic inlet to the hot gas turbine.

**It is not hydrogen immune.** A notched ratio of 0.55 is far better than a low alloy steel at 0.18, and it is not 1.0. The susceptibility rises with the aging treatment, so the highest strength conditions are the worst, and hydrogen service argues for a lower strength age.

**Additive 718 is mature.** LPBF with HIP, solution treat and age reaches essentially wrought properties, with a Z direction knockdown around 5 percent after HIP rather than the 25 percent it would be as-built. HIP closes the porosity that dominates as-built fatigue.

**The HIP cycle runs above the gamma prime solvus**, so it dissolves the strengthening precipitate. A part HIPed and not re-treated is soft, and none of the allowables apply to it.

---

## Inconel 625

Solid solution strengthened, weldable with no post-weld heat treatment, and outstandingly corrosion resistant.

| Property | Value |
|---|---|
| Yield strength | 414 MPa |
| Ultimate strength | 827 MPa |
| **PREN** | **51.2** |
| Critical pitting temperature | **+57 degC** |
| Useful to | ~1100 K |

**PREN 51 is the number that matters.** It puts the critical pitting temperature above any service temperature, which is why 625 bellows are specified at coastal launch sites where 316L would pit. The seven times cost multiplier over 316L buys a positive pitting threshold.

**Weldability with no post-weld heat treatment** makes it the default for bellows, flex hoses and hot gas ducting, where the assembly cannot be put through a solution cycle.

Its strength is modest, so it is chosen for environment rather than for load.

---

## Monel

Nickel-copper, and the copper is the whole story in both directions.

| Alloy | Fty [MPa] | Ftu [MPa] | Condition |
|---|---|---|---|
| Monel 400 | 240 | 550 | Annealed |
| **Monel K-500** | **690** | **1100** | Age hardened |

**Outstanding in fluorine and high concentration peroxide**, which is a very short list of materials and the reason Monel exists in a propulsion context at all.

**Catastrophic in hydrazine.** Copper catalyses hydrazine decomposition, producing gas, flow instability and an unbounded pressure rise. At 30 percent copper Monel is a copper-base alloy for this purpose, and it is prohibited. This catches people out precisely because Monel is otherwise an excellent propulsion alloy.

**K-500 is Monel with aluminium and titanium added** to make it age hardenable, roughly tripling the yield strength while keeping the fluorine and peroxide compatibility. It is the valve stem and fastener alloy for those services, and it carries the identical copper prohibition.

---

## The high temperature alloys

Where 718 and 625 run out of strength.

| Alloy | Fty [MPa] | Useful to | Strengthening | Where it belongs |
|---|---|---|---|---|
| **Haynes 230** | 390 | ~1250 K | Tungsten solid solution | Gas generator ducting, turbine inlet |
| **Hastelloy X** | 360 | ~1200 K | Molybdenum solid solution | Combustor sheet, formed hot structure |

**Haynes 230 keeps useful strength beyond 1200 K** where 625 has essentially none, and the tungsten content is what does it. It is the alloy for hot gas manifolds and turbine inlet hardware.

**Hastelloy X trades strength for formability and oxidation resistance**, which makes it the classic combustor sheet alloy. Where a hot section part has to be formed and welded rather than machined, it is usually the choice.

Both are expensive, both run to 26 week lead times, and neither should be specified without confirming a supplier.

---

## Welding

| Alloy | Practice |
|---|---|
| 625, Hastelloy X, Haynes 230 | Weld as-is. No post-weld heat treatment required |
| **718** | Weld solution annealed, then age the assembly. As-welded yield is 724 MPa against 1034 |
| Monel 400 | Readily weldable |
| Monel K-500 | Weld annealed, then age |

**Electron beam welding is preferred for 718** where the geometry allows, because the narrow heat affected zone limits the knockdown to about 5 percent rather than the 45 percent of an as-welded fusion joint.

Full weld treatment in [fluidSystems Welds.md](../../fluidSystems/fluidSystemsLibrary/docs/Welds.md).

---

## Cost and lead time

Indexed to 316L bar at 1.0, with the basis date carried alongside because these rot within a quarter.

| Alloy | Relative cost | Bar lead time |
|---|---|---|
| 316L | 1.0 | 3 weeks |
| Monel 400 | 5.5 | 14 weeks |
| **Inconel 718** | **6.5** | **14 weeks** |
| Inconel 625 | 7.0 | 12 weeks |
| Monel K-500 | 8.0 | 20 weeks |
| Hastelloy X | 11.0 | 20 weeks |
| **Haynes 230** | **14.0** | **24 weeks** |

**Lead time is a material property in every practical sense.** A 24 week bar lead time on Haynes 230 sets the programme schedule, and discovering it after the design freezes is a recurring and avoidable programme event.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| 718 for strength across a wide temperature range | 20 K to 925 K in one alloy |
| 625 for environment rather than load | PREN 51, weldable as-is |
| Weld PH alloys annealed, age the assembly | Or accept a 45 % knockdown |
| Haynes 230 above 1100 K | Where 625 has no strength left |
| Never Monel in hydrazine | Copper catalyses decomposition |
| HIP above the gamma prime solvus needs a re-treat | Or the part is soft |
| 718 is hydrogen resistant, not immune | Notched ratio 0.55, worse at higher strength |
| Confirm the supplier before the design freeze | 14 to 26 week lead times |

---

## Failure modes

**718 welded in the aged condition.** Strain age cracking in the heat affected zone.

**A weld left as-welded in a PH alloy.** A soft spot at 55 percent of parent yield.

**Monel in a hydrazine system.** Catalytic decomposition and an unbounded pressure rise.

**718 in high pressure hydrogen at peak strength.** Better than steel, and still embrittled.

**An additive part HIPed and not re-treated.** Soft, and outside every allowable in the database.

**316L specified where 625 was needed.** Pitting at the launch site, discovered in service.

**A programme schedule built without checking superalloy lead times.** The commonest of these failures and entirely preventable.

---

## Standards

| Standard | Scope |
|---|---|
| **MMPDS Chapter 6** | Heat resistant alloy allowables |
| AMS 5662 / 5663 | Inconel 718 bar, solution treated and aged |
| AMS 5596 | Inconel 718 sheet |
| AMS 5599 / 5666 | Inconel 625 sheet and bar |
| ASTM B443 / B446 | Inconel 625 plate, sheet and bar |
| ASTM B127 / B164 | Monel 400 sheet and bar |
| AMS 4676 | Monel K-500 bar |
| AMS 5878 / 5891 | Haynes 230 |
| AMS 5536 / 5754 | Hastelloy X |
| **ASTM F3055** | Additive manufactured Inconel 718 |
| ASTM F3056 | Additive manufactured Inconel 625 |

---

## Tool interface

```python
from MaterialDatabase import MaterialDatabase, queryMaterial
from HeatTreatment import HeatTreatment

# The wide temperature range that justifies 718
database = MaterialDatabase()
database.setInputs({'material': 'Inconel 718', 'condition': 'sta'})
for temperature in (20.0, 293.15, 800.0, 1000.0):
    database.temperature = temperature
    database.properties  = {}
    print(temperature, database.getProperties()['yieldStrength'] / 1.0e6)

# The HIP cycle and what has to follow it
treatment = HeatTreatment()
treatment.setInputs({'material': 'Inconel 718', 'condition': 'lpbf hip + sta'})
print(treatment.calculateHipCycle())
```

---

## References

1. MMPDS-18, Chapter 6, *Heat Resistant Alloys*.
2. Donachie, M. J. and Donachie, S. J., *Superalloys: A Technical Guide*, 2nd ed., ASM, 2002.
3. Reed, R. C., *The Superalloys: Fundamentals and Applications*, Cambridge University Press, 2006.
4. Special Metals Corporation, *Inconel Alloy 718* and *Inconel Alloy 625* datasheets.
5. Haynes International, *Haynes 230 Alloy* datasheet.
