[Home](../README.md) > Copper Alloys

# Copper Alloys

## Contents

- [Overview](#overview)
- [The alloys](#the-alloys)
- [Why conductivity is the requirement](#why-conductivity-is-the-requirement)
- [The regenerative liner index](#the-regenerative-liner-index)
- [GRCop-42](#grcop-42)
- [The propellant prohibitions](#the-propellant-prohibitions)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Copper alloys exist in a launch vehicle for one reason: the regeneratively cooled combustion chamber liner. Nothing else combines the thermal conductivity needed to get the heat out with enough strength to survive the pressure and the thermal cycling.

---

## The alloys

| Alloy | Conductivity [W/m/K] | Yield [MPa] | Max temperature | Notes |
|---|---|---|---|---|
| **GRCop-42** | 340 | 190 | **800 degC** | **Cu-Cr-Nb. The NASA additive liner alloy** |
| **NARloy-Z** | 320 | 180 | 750 degC | Cu-Ag-Zr. **The SSME liner alloy** |
| **C18150** | 330 | 310 | 450 degC | Cu-Cr-Zr. Commercially available |
| C10100 OFHC | **391** | 70 | 200 degC | Pure. Highest conductivity, no strength |
| C17200 beryllium copper | 105 | 1000 | 300 degC | Strong, low conductivity, toxic dust |

**Pure copper has the best conductivity and no strength.** Every alloy in the table trades conductivity for strength, and the engineering question is where on that trade the application sits.

---

## Why conductivity is the requirement

**A regenerative chamber liner has to conduct the heat flux out of the hot gas side and into the coolant, across a wall thin enough that the temperature drop is survivable.**

```
dT = q * t / k
```

At a heat flux of 50 MW/m^2, which is normal for a high pressure chamber, across a 1 mm wall:

| Material | k [W/m/K] | Temperature drop |
|---|---|---|
| **GRCop-42** | 340 | **147 K** |
| 316L | 15 | **3300 K** |
| IN718 | 11 | 4500 K |

**The stainless and nickel numbers are impossible**, which is the whole argument. A steel or nickel liner at that heat flux melts, and no thickness reduction saves it because the flux is fixed by the combustion.

**That is why chamber liners are copper and the jacket is not.** The liner conducts, the structural jacket carries the pressure, and the two are joined by brazing, electroforming or additive manufacture.

---

## The regenerative liner index

**The Ashby index for this application is not conductivity alone.**

```
M = sigma * k / (E * alpha)
```

| Term | Why |
|---|---|
| `sigma` | It has to hold the pressure |
| `k` | It has to conduct the heat |
| `E * alpha` | **The thermal stress it generates per degree** |

**The denominator is what makes it interesting.** A liner with a steep through-thickness temperature gradient develops thermal stress proportional to `E * alpha * dT`, and that stress is what causes the low cycle fatigue failure mode that limits chamber life.

**Copper alloys win this index by a wide margin** despite their modest strength, because the high conductivity reduces `dT` and the low modulus reduces the stress that `dT` produces.

**Doghouse failure is the characteristic mode**: the hot gas wall thins and bulges outward into the channel over repeated cycles, from ratcheting plastic strain, until it fails. It is a thermal strain problem, not a pressure problem.

---

## GRCop-42

**A NASA developed Cu-Cr-Nb alloy, strengthened by Cr2Nb dispersoids.**

| Property | Detail |
|---|---|
| **Dispersion strengthened** | Cr2Nb particles, which do not dissolve |
| **Stable to 800 degC** | The dispersoids do not coarsen appreciably |
| **Conductivity 340 W/m/K** | Retained, because the dispersoids are discrete |
| **LPBF processable** | This is why it matters now |

**Dispersion strengthening is what allows both conductivity and temperature capability.** A precipitation hardened copper alloy loses strength as the precipitates coarsen and puts solute in the matrix that scatters electrons; a dispersion of stable intermetallic particles does neither.

**Its additive processability is what changed the field.** A GRCop-42 chamber liner can be printed with integral cooling channels in one piece, replacing a brazed assembly of a machined liner and a formed jacket. That is a substantial reduction in part count, lead time and failure modes.

**GRCop-42 against GRCop-84** differs in the Cr2Nb volume fraction: 84 has more, so it is stronger and less conductive, and 42 has become the more used of the two for additive liners.

---

## The propellant prohibitions

**Copper-base alloys are prohibited in hydrazine service**, and it is a categorical prohibition rather than a compatibility rating.

| Propellant | Copper base alloys |
|---|---|
| **Hydrazine, MMH, UDMH** | **Prohibited.** Catalytic decomposition |
| Ammonia | Prohibited. Attack |
| LOX, GOX | Acceptable with care |
| RP-1 | Acceptable |
| LH2 | Acceptable |

**Copper catalyses hydrazine decomposition**, which is exothermic and self-accelerating. A copper surface in a hydrazine system is an ignition source.

**The prohibition applies to copper matrix alloys**, not to alloys containing copper as a minor constituent. **17-4PH contains 3 to 5 percent copper as a precipitating element and is not prohibited**, because the copper is bound in precipitates within an iron matrix rather than present as a copper surface. That distinction cost a wrong test assertion in this build, with the threshold set at 3 percent instead of the correct copper-base criterion.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Copper liners because nothing else conducts | 340 against 15 W/m/K |
| Liner index | `sigma k / (E alpha)` |
| Doghouse failure is thermal strain | Not pressure |
| GRCop-42 is dispersion strengthened | Conductivity and temperature together |
| GRCop-42 is LPBF processable | Integral channels in one piece |
| **Copper-base alloys prohibited in hydrazine** | Catalytic decomposition |
| 17-4PH is not a copper-base alloy | The copper is in precipitates |

---

## Failure modes

**Steel or nickel liner at a high heat flux.** It melts.

**Liner life predicted on pressure alone.** The failure is thermal strain ratcheting.

**Precipitation hardened copper used above its coarsening temperature.** Strength and conductivity both go.

**Copper-base alloy in a hydrazine system.** Catalytic decomposition.

**17-4PH excluded from hydrazine on its copper content.** It is not copper-base.

**GRCop conductivity assumed equal to pure copper.** It is 13 % lower.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-6016** | Materials and processes requirements |
| **NASA-STD-6001** | Flammability, offgassing and compatibility |
| ASTM B152 | Copper sheet, strip, plate and rolled bar |
| ASTM B187 | Copper bar, bus bar, rod and shapes |
| ASTM E1461 | Thermal diffusivity by the flash method |
| ASTM E228 | Linear thermal expansion |
| AMS 4640 | Copper alloy specifications by grade |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterialsLibrary')

from MaterialSelector import MaterialSelector

selector = MaterialSelector()
selector.setInputs({'requirements': {'serviceTemperature': 800.0},
                    'loadingMode': 'regen chamber liner'})
selector.screen()
for entry in selector.rank()[:5]:
    print(f'{entry["label"]:24s} index {entry["index"]:12.4g}')
```

---

## References

1. Ellis, D. L., *GRCop-84: A High-Temperature Copper Alloy for High-Heat-Flux Applications*, NASA/TM-2005-213566.
2. Gradl, P. R. et al., "GRCop-42 Development and Hot-fire Testing Using Additive Manufacturing", AIAA 2019-4228.
3. Huzel, D. K. and Huang, D. H., *Modern Engineering for Design of Liquid-Propellant Rocket Engines*, AIAA, 1992.
