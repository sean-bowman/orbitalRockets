[Home](../README.md) > Copper Alloys

# Copper Alloys

## Contents

- [Overview](#overview)
- [The figure of merit is not strength](#the-figure-of-merit-is-not-strength)
- [The alloys](#the-alloys)
- [Why liners fail](#why-liners-fail)
- [The hydrazine prohibition](#the-hydrazine-prohibition)
- [Additive copper](#additive-copper)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Copper alloys appear on a launch vehicle in exactly one place: the regeneratively cooled combustion chamber liner. Everywhere else they are too heavy, too weak, or prohibited.

In that one place they are irreplaceable, because nothing else conducts heat well enough to keep a chamber wall below its melting point while the gas side sits above 3000 K.

---

## The figure of merit is not strength

A chamber liner does not fail by yielding under pressure. It fails by **thermal strain ratcheting**: the hot gas side wants to expand, the cold coolant side restrains it, and the resulting compressive plastic strain accumulates every cycle until the wall thins and splits. The characteristic failure is a doghouse-shaped bulge with a longitudinal crack.

The material index that matters is therefore

```
M = sigma * k / (E * alpha)
```

Conductivity and strength both help; modulus and thermal expansion both hurt. **Copper wins on `k` by such a margin that it survives losing on everything else.**

| Alloy | k [W/m-K] | Fty [MPa] | E [GPa] | alpha [1e-6/K] | Index |
|---|---|---|---|---|---|
| **GRCop-42** | 320 | 190 | 125 | 17.5 | **27.8** |
| NARloy-Z | 345 | 165 | 124 | 18.0 | 25.5 |
| C18150 CuCrZr | 320 | 350 | 128 | 17.0 | 51.5 |
| Inconel 718 | 11.4 | 1034 | 200 | 13.0 | 4.5 |
| 316L | 16.3 | 170 | 193 | 16.0 | 0.9 |

**Inconel is six times worse and stainless is thirty times worse**, despite being far stronger. That is the entire argument for a copper liner.

---

## The alloys

| Alloy | Composition | Fty [MPa] | k [W/m-K] | Where it belongs |
|---|---|---|---|---|
| **GRCop-42** | Cu-8Cr-4Nb | 190 | 320 | Additive chamber liners |
| **NARloy-Z** | Cu-3Ag-0.5Zr | 165 | 345 | Wrought liners. The SSME alloy |
| C18150 | Cu-0.8Cr-0.08Zr | 350 | 320 | Heat exchangers, development chambers |

**GRCop-42 was designed for LPBF from the start**, which is why it appears in additive chambers and nowhere else. Cr2Nb precipitates pin the grain boundaries, so it keeps useful strength and creep resistance to 1000 K where a conventional copper alloy has none. The dispersoids are thermally stable, so unlike a precipitation hardened alloy it does not over-age.

**NARloy-Z is the SSME main combustion chamber liner alloy** and the reference every newer copper alloy is measured against. Higher conductivity than GRCop-42 and lower elevated temperature strength, so it is the better wrought choice and the worse additive one for a part running hot.

**C18150 is the commercially available option** at a fraction of the cost and lead time. Lower temperature capability, but for a heat exchanger, an electrode or a development chamber that does not need many cycles, it is the sensible choice and it can be bought this quarter.

---

## Why liners fail

The mechanism is worth understanding because it explains every design feature of a chamber.

**During a burn** the gas side reaches perhaps 800 K while the coolant side stays near 200 K. The hot side wants to expand and cannot, so it goes into compression and yields. **After shutdown** the temperature equalises, and the hot side is now too long for the space available, so it goes into tension and yields the other way.

Each cycle accumulates plastic strain. The wall thins locally, bulges towards the gas, and eventually splits. The failure is low cycle fatigue driven by thermal strain, not by pressure.

**What helps:**

| Measure | Why |
|---|---|
| Higher conductivity | Lower gas side temperature, smaller gradient |
| Thinner wall | Smaller gradient across it |
| Lower modulus | Less stress for the same strain |
| Lower expansion | Less strain for the same gradient |
| Higher yield strength | More elastic range before ratcheting starts |

The thin wall requirement is why chamber liners are 0.7 to 1.5 mm and why additive manufacturing suits them: the coolant channels can be built in rather than machined and closed out.

---

## The hydrazine prohibition

**Every copper-base alloy is prohibited in hydrazine service.** Copper catalyses hydrazine decomposition, producing nitrogen, ammonia and hydrogen, with an unbounded pressure rise in a closed volume.

| Prohibited | Copper content |
|---|---|
| GRCop-42 | 88 % |
| NARloy-Z | 96.5 % |
| C18150 | 99 % |
| Monel 400 | 32 % |
| Brass, bronze | 60 to 90 % |

**The prohibition extends to things that are easy to miss**: brass fittings, bronze bushings, copper-bearing anti-seize, copper gaskets, copper-filler brazing, and the copper sulfate passivation test. The fluidSystems document [MaterialsCompatibility.md](../../fluidSystems/fluidSystemsLibrary/docs/MaterialsCompatibility.md) carries the full list.

**The precipitation hardening stainless grades are a different case.** 17-4PH carries 3.5 percent copper bound as precipitates in a passivated matrix, and it is used in hydrazine service. The prohibition is on copper-base alloys, where copper is the matrix.

---

## Additive copper

Copper is difficult to process by LPBF for a physical reason: **it reflects the infrared laser wavelength**. Pure copper absorbs perhaps 5 percent at 1070 nm, so most of the beam energy is wasted and the melt pool is unstable.

**GRCop-42 works because the chromium and niobium raise the absorptivity** enough for a conventional fibre laser. That is part of why the alloy exists in the form it does.

**Green and blue wavelength lasers** absorb far better in copper and are becoming available, which will change the picture for pure copper and for the conventional copper alloys. As of now, GRCop-42 on a standard machine is the mature route.

**Data maturity is low.** Everything in the database for GRCop-42 is marked `estimate` rather than `statistical`, because the public property database is still developing and lot to lot scatter is significant. A programme using it for flight hardware has to establish its own allowables.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| The index is `sigma k / (E alpha)`, not strength | Copper wins on conductivity alone |
| Liner walls 0.7 to 1.5 mm | Thinner wall, smaller gradient, less ratcheting |
| GRCop-42 for additive, NARloy-Z for wrought | Elevated temperature strength versus conductivity |
| C18150 where the duty cycle is short | A tenth the cost and lead time |
| Never any copper-base alloy in hydrazine | Catalytic decomposition |
| Failure is thermal strain, not pressure | Low cycle fatigue, doghouse bulge |
| Establish your own allowables for GRCop | The public data is not a statistical basis |

---

## Failure modes

**Doghouse bulge and longitudinal split.** The characteristic liner failure. Thermal strain ratcheting.

**A copper fitting in a hydrazine system.** Catalytic decomposition and pressure rise.

**Blocked or partially blocked coolant channel.** Local overheating and rapid burn-through. The reason chamber cleanliness and filtration are not negotiable.

**GRCop allowables taken from a paper.** They are typical values from one build, and lot scatter is significant.

**Pure copper attempted on a standard LPBF machine.** Poor absorption, unstable melt pool, porosity.

**A liner designed on room temperature properties.** GRCop-42 retains 68 percent of its yield at 800 K and 48 percent at 1000 K.

---

## Standards

| Standard | Scope |
|---|---|
| ASTM B441 | C18150 chromium zirconium copper |
| **NASA/TM GRCop-42 and GRCop-84 reports** | The primary GRCop property source |
| ASTM E8 / E21 | Tension testing at room and elevated temperature |
| ASTM E606 | Strain controlled fatigue testing, which is the relevant mode |
| **NASA-STD-6030** | Additive manufacturing requirements for spaceflight |
| MSFC-STD-3716 | Standard for additively manufactured spaceflight hardware |
| CGA G-4.4 | Oxygen pipeline and piping systems, for the oxygen-side compatibility |

---

## Tool interface

```python
from MaterialSelector import MaterialSelector

# The liner index, which is a first class loading mode rather than a special case
selector = MaterialSelector()
selector.setInputs({'requirements': {'serviceTemperature': 800.0,
                                     'maximumTemperature': 1000.0,
                                     'fluids': ['CH4', 'LOX']},
                    'loadingMode': 'regen chamber liner',
                    'strengthProperty': 'yieldStrength'})
for entry in selector.rank():
    print(entry['label'], entry['index'])
```

---

## References

1. Ellis, D. L., *GRCop-84: A High Temperature Copper Alloy for High Heat Flux Applications*, NASA/TM-2005-213566.
2. Gradl, P. R. et al., "GRCop-42 Development and Hot-fire Testing", AIAA Propulsion and Energy, 2019.
3. Huzel, D. K. and Huang, D. H., *Modern Engineering for Design of Liquid-Propellant Rocket Engines*, AIAA, 1992.
4. Quentmeyer, R. J., *Experimental Fatigue Life Investigation of Cylindrical Thrust Chambers*, NASA TM X-73665, 1977.
5. ASM Handbook Volume 2, *Properties and Selection: Nonferrous Alloys*.
