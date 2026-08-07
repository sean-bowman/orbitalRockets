[Home](../../README.md) > Hydrazine

# Hydrazine

## Contents

- [Overview](#overview)
- [Physical properties](#physical-properties)
- [Chemistry and decomposition](#chemistry-and-decomposition)
- [The hydrazine family](#the-hydrazine-family)
- [Specification and purity](#specification-and-purity)
- [Materials compatibility](#materials-compatibility)
- [Hazards](#hazards)
- [Handling and operations](#handling-and-operations)
- [System design implications](#system-design-implications)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Hydrazine (N2H4) is the reference storable monopropellant and has been since the early 1960s. It has flown on essentially every geostationary satellite, every deep space probe with chemical propulsion, and a very large fraction of everything else in orbit.

What makes it useful is not its performance, which is modest at 220 to 235 s of vacuum specific impulse. It is the combination of four properties that nothing else has all of:

1. **It decomposes spontaneously on a catalyst** at room temperature, so a thruster needs no igniter and no ignition sequence.
2. **It is storable indefinitely** as a liquid at ordinary spacecraft temperatures.
3. **It is a monopropellant**, so there is one tank, one feed system and no mixture ratio.
4. **It is also an excellent bipropellant fuel**, so the same propellant serves attitude control monopropellant thrusters and a bipropellant apogee engine on the same spacecraft.

What makes it a problem is that it is acutely toxic, a suspected human carcinogen, flammable over an enormous range in air, and hypergolic with several common oxidizers. The propellant is cheap; the handling infrastructure is not, and on many programs the ground handling cost exceeds the flight hardware cost.

The [`CatalystBed`](../CatalystBed.py) and [`MonopropThruster`](../MonopropThruster.py) classes cover the decomposition and performance side. This document covers the propellant itself.

---

## Physical properties

Anhydrous hydrazine, from the [`utils.hydrazineProps`](../utils.py) correlations:

| Property | Value | Note |
|---|---|---|
| Molecular formula | N2H4 | |
| Molar mass | 32.045 g/mol | |
| **Freezing point** | **274.69 K (1.54 degC)** | **The design driver for heater power** |
| Normal boiling point | 386.65 K (113.5 degC) | |
| Critical temperature | 653 K | |
| Critical pressure | 14.7 MPa | |
| Density at 293 K | 1008.5 kg/m^3 | |
| Density at 298 K | 1004.2 kg/m^3 | |
| Dynamic viscosity at 298 K | 0.913 mPa-s | Roughly that of water |
| Vapor pressure at 298 K | 1.92 kPa (14.4 torr) | Low, which is why vapor leaks are subtle |
| Vapor pressure at 323 K | 12.4 kPa | Rises steeply |
| Thermal conductivity at 298 K | 0.371 W/m-K | |
| Specific heat at 298 K | 3084 J/kg-K | |
| Surface tension at 298 K | 66.7 mN/m | High, comparable to water |
| Heat of vaporization at 298 K | 1395 kJ/kg | |
| Heat of formation, liquid | +50.6 kJ/mol | **Positive.** The propellant is metastable |
| Isentropic bulk modulus | 4.45 GPa | Very stiff; water hammer is severe |
| Autoignition temperature in air | 543 K (270 degC) | Lower on many surfaces |
| Flammability limits in air | **4.7 to 100 vol %** | There is no upper limit |

**The freezing point at 1.54 degC is the single most consequential number.** It is above the temperature of almost any unheated surface in orbit, which means every hydrazine spacecraft carries tank heaters, line heaters, valve heaters and thruster heaters, with the associated power budget, thermostats, redundancy and failure modes. Frozen hydrazine also expands on freezing, so a frozen and capped line can burst.

**The flammability limits have no upper bound.** Hydrazine is not merely flammable in air; it burns in the absence of any oxidizer at all, because decomposition itself is exothermic. A hydrazine vapor cloud will propagate a flame at any concentration above 4.7 percent, including pure hydrazine vapor.

**The positive heat of formation** is what makes it a monopropellant. Decomposition to nitrogen and hydrogen releases energy with no oxidizer required, which is the definition of a metastable propellant and the reason it must be treated as an energetic material rather than as a solvent.

---

## Chemistry and decomposition

**Catalytic decomposition** in two steps:

```
3 N2H4  ->  4 NH3 + N2         dH = -112.3 kJ per mol N2H4    exothermic
4 NH3   ->  2 N2 + 6 H2        dH =  +46.0 kJ per mol NH3     endothermic
```

Combined, with ammonia dissociation fraction `X`:

```
N2H4  ->  (4/3)(1-X) NH3  +  (1/3 + (2/3)X) N2  +  2X H2
```

The adiabatic decomposition temperature falls almost linearly with `X`:

| X | Temperature [K] | Mean MW [g/mol] | c* [m/s] |
|---|---|---|---|
| 0.0 | 1659 | 19.23 | 1278 |
| 0.2 | 1500 | 16.58 | 1304 |
| **0.38** | **1362** | **14.75** | **1311 (peak)** |
| 0.4 | 1347 | 14.57 | 1311 |
| 0.6 | 1194 | 12.99 | 1300 |
| 1.0 | 894 | 10.68 | 1224 |

**The characteristic velocity peak is broad and the temperature is not.** c* varies by only 3 percent between `X = 0.2` and `X = 0.6`, while the chamber temperature falls by more than 300 K over the same range. That means bed length is chosen for thermal reasons -- chamber wall temperature, throat temperature, valve soakback -- rather than for performance. This is covered in detail in [CatalystBeds.md](CatalystBeds.md).

**Thermal decomposition** without a catalyst begins around 500 K and becomes rapid above 550 K. This is not a designed process; it is a hazard. Any hot spot in a hydrazine system -- a heater that has failed on, a valve that has soaked back from a firing, a line touching a hot structure -- will decompose propellant, generate gas, and pressurize a trapped volume. Hydrazine trapped between two closed valves and heated is a bomb, and this failure mode has destroyed hardware.

**Catalytic decomposition on contaminants** is the more insidious version. Metals catalyze hydrazine decomposition, some very effectively:

| Catalyst | Effect |
|---|---|
| Iridium (Shell 405) | Designed. Spontaneous at 275 K |
| **Copper and copper alloys** | **Strongly catalytic. Keep every copper-bearing alloy out of a hydrazine system, including Monel and brass** |
| Iron oxide, rust | Catalytic. A rusty line will generate gas |
| Molybdenum, cobalt | Catalytic |
| Silver | Mildly catalytic |
| 300-series stainless, aluminum, titanium | Acceptably inert |

Decomposition upstream of the injector produces gas in the feed line, which causes flow instability, injector maldistribution, and in a blowdown system a slow rise in tank pressure with no explanation.

---

## The hydrazine family

| Propellant | Formula | Use | Freezing point | Notes |
|---|---|---|---|---|
| **Hydrazine** | N2H4 | Monopropellant, bipropellant fuel | 274.7 K | The reference |
| **MMH** (monomethylhydrazine) | CH3N2H3 | Bipropellant fuel with NTO | 220.7 K | Much lower freezing point. Not a practical monopropellant: it does not decompose cleanly on a catalyst |
| **UDMH** (unsymmetrical dimethylhydrazine) | (CH3)2N2H2 | Bipropellant fuel | 216 K | More stable, lower performance than MMH |
| **Aerozine 50** | 50/50 N2H4/UDMH by mass | Bipropellant fuel (Titan, Apollo) | 266 K | Compromise between the freezing point of UDMH and the performance of hydrazine |

The reason spacecraft use hydrazine for monopropellant and MMH for bipropellant is exactly the catalyst behaviour: hydrazine decomposes cleanly on iridium, and the methylated derivatives leave carbon deposits that poison the bed. A dual-mode spacecraft that uses hydrazine for both its monopropellant thrusters and its bipropellant apogee engine gets a single fuel tank, which is a genuine architecture-level simplification.

---

## Specification and purity

**MIL-PRF-26536** is the governing US specification. The grades that matter:

| Grade | N2H4 minimum | Water maximum | Aniline maximum | Particulate | Use |
|---|---|---|---|---|---|
| Standard | 98.0 % | 1.0 % | 0.5 % | 10 mg/L | General |
| **Monopropellant** | **98.5 %** | **1.0 %** | **0.5 %** | **1 mg/L** | **Catalytic thrusters** |
| High purity | 99.0 % | 1.0 % | 0.005 % | 1 mg/L | Long life catalyst beds |
| Ultra pure | 99.5 % | 0.5 % | 0.003 % | 1 mg/L | Extended life, high cycle count |

**Why the impurity limits exist:**

- **Water** occupies active catalyst sites and raises ignition delay. Hydrazine is hygroscopic and miscible with water in all proportions, so any air exposure adds water. This is the most common contaminant.
- **Aniline** is a residual from the production process. It is strongly and effectively permanently adsorbed on the catalyst.
- **Carbon dioxide** forms carbonate on the alumina support. Picked up from any air exposure.
- **Particulate** plugs injector orifices and abrades the catalyst.
- **Iron, chloride, sulfur** are catalyst poisons and corrosion sources.

**The purity grade is a life requirement, not a performance requirement.** Standard grade and ultra pure grade give the same Isp on the first firing. The difference shows up as ignition delay growth and eventual start failure over thousands of pulses, which is why a long-life geostationary satellite buys ultra pure and a single-burn upper stage does not.

---

## Materials compatibility

| Material | Compatibility | Note |
|---|---|---|
| 304L, 316L, 321 stainless | **Excellent** | The standard system material |
| 6061, 2219 aluminum | **Excellent** | Standard tank material |
| Titanium 6Al-4V | **Excellent** | Standard tank material for flight |
| Inconel 625, 718 | Good | |
| **Copper, brass, bronze, Monel** | **PROHIBITED** | Catalyze decomposition |
| Nickel | Marginal | Mildly catalytic; acceptable as a plating in small areas |
| Silver | Marginal | Mildly catalytic. Avoid silver-plated fittings |
| Magnesium, zinc, cadmium | Prohibited | Attacked, and cadmium plating is a common accidental contaminant |
| **EPDM** | **Good** | The standard elastomer |
| **Butyl (IIR)** | **Good** | Lowest gas permeability; good for long-term seals |
| **PTFE, PCTFE** | **Excellent** | Inert |
| FFKM (Kalrez) | Good | Where the temperature range demands it |
| **NBR (Buna-N)** | **PROHIBITED** | Degrades AND catalyzes decomposition |
| **FKM (Viton)** | **PROHIBITED** | Attacked by hydrazine |
| Silicone | Poor | Attacked |
| Polyurethane, polyamide (nylon) | Poor | Attacked |

**The two rules to carry:**

1. **No copper-bearing alloys anywhere.** That includes brass fittings, bronze bushings, Monel, and copper-based anti-seize compounds. This eliminates a lot of standard plumbing hardware.
2. **No Buna-N and no Viton.** These are the two most common elastomers in any shop and both are wrong. Use EPDM, butyl, or PTFE. This is the single most common seal material error in hydrazine work, and it is dangerous rather than merely inconvenient, because a degrading NBR seal accelerates decomposition of the propellant it is containing.

---

## Hazards

**Toxicity.** Hydrazine is acutely toxic by inhalation, ingestion and skin absorption, and it is a suspected human carcinogen (IARC Group 2A, EPA Group B2).

| Exposure limit | Value |
|---|---|
| OSHA PEL, 8-hour TWA | 1 ppm (skin) |
| **ACGIH TLV, 8-hour TWA** | **0.01 ppm (skin)** |
| NIOSH IDLH | 50 ppm |
| Odor threshold | 3 to 5 ppm |

**The odor threshold is 300 to 500 times the TLV.** If you can smell hydrazine, you are already far above the occupational limit. Detection must be instrumental, not sensory.

The skin notation matters: hydrazine is readily absorbed through intact skin, so a respirator alone is not adequate protection and full-body chemical protective clothing (SCAPE suits, or equivalent with supplied air) is standard for propellant transfer operations.

**Flammability.** Flammable limits in air are 4.7 to 100 percent by volume. There is no upper flammability limit, because decomposition is self-sustaining. Autoignition in air is 543 K, and much lower on catalytic surfaces: hydrazine will ignite on contact with rusty iron oxide, on some metal oxides, and on porous materials such as cloth or insulation at ambient temperature.

**A hydrazine spill onto a porous organic material is a fire waiting to start**, and this has caused accidents. The large surface area promotes catalytic decomposition, the decomposition is exothermic, and the material self-heats to ignition.

**Hypergolicity.** Hydrazine is hypergolic with nitrogen tetroxide, nitric acid, hydrogen peroxide and several other oxidizers. Fuel and oxidizer systems must be physically separated with no shared cavity or vent path where a leak from one could reach the other.

**Decomposition pressurization.** Trapped hydrazine that is heated or catalytically contaminated generates gas with no outlet. A hydrazine volume isolated between two closed valves is a pressure vessel with an internal energy source, and this has burst hardware.

---

## Handling and operations

**Personal protective equipment.** For any operation with the potential for exposure: SCAPE suit or equivalent fully encapsulating suit with supplied breathing air. For lower-hazard operations, chemical splash suit, butyl or laminate gloves (not nitrile), face shield and a supplied-air respirator. Never rely on a cartridge respirator for hydrazine.

**Vapor monitoring.** Continuous instrumental monitoring at the TLV level. Colorimetric badges, electrochemical sensors and ion mobility spectrometry are all used. The monitor is not optional; the odor threshold is useless.

**Transfer operations.** Closed transfer only, with vapor return. No open pouring, ever. Inert the receiving vessel with GN2 before transfer and after. Ground all equipment; hydrazine handling is done in an atmosphere that may be flammable.

**Deluge and neutralization.** Large water deluge available at any transfer operation. Hydrazine is miscible with water in all proportions and dilution is the primary spill response. Neutralization with a hypochlorite or peroxide solution is used for residues, with the caution that the reaction is exothermic and can be violent at high hydrazine concentrations.

**Waste.** Hydrazine-contaminated water is hazardous waste. Everything that touches hydrazine becomes hazardous waste, which is a substantial part of the operational cost.

**Purge before opening.** Any line that has contained hydrazine must be drained, flushed and purged with GN2 before any joint is broken. Residual hydrazine in a supposedly empty line is the most common route to a personnel exposure. See [OperationsAndPurge.md](OperationsAndPurge.md).

**Storage.** Cool, dark, under inert gas, in a compatible container (316L stainless or aluminum), away from oxidizers, away from catalytic metals, away from anything porous and organic.

---

## System design implications

**Heaters everywhere.** The 274.7 K freezing point drives heaters on the tank, every line, every valve, the catalyst bed and the thruster. Those heaters have a power budget, need thermostats, need redundancy, and their failure modes (failed off, freezing propellant; failed on, decomposing propellant) are both credible and both bad.

**No copper anywhere.** Rules out a lot of standard hardware, including many commercial valves and regulators that use brass internals or bronze bushings.

**Seal material control at part number level.** EPDM, butyl or PTFE only. Every seal in the system, including the ones inside purchased components, has to be verified.

**Bellows-sealed valves.** The external leakage requirement for a toxic propellant effectively rules out any dynamic sliding stem seal. See [Valves.md](Valves.md).

**Very tight leak requirements.** With a 0.01 ppm TLV, the allowable leak rate derived from a hazard criterion is around 1e-5 scc/s into a typical bay volume over a shift. That is tighter than a flare fitting achieves, which pushes the design toward welded joints and VCR fittings. See [Leaks.md](Leaks.md).

**Severe water hammer.** Hydrazine has both a high density (1008 kg/m^3) and a very high bulk modulus (4.45 GPa), giving a wave speed near 2050 m/s and a Joukowsky surge of about **2.07 MPa per m/s** of velocity change. That is the worst of any common propellant and it is why hydrazine line velocity limits are set at 6 m/s. See [WaterHammer.md](WaterHammer.md).

**Filtration.** An absolute-rated filter upstream of the catalyst bed, and upstream of every injector orifice. Particulate abrades catalyst and plugs orifices, and the propellant specification allows 1 mg/L which is not zero.

**No trapped volumes.** Every isolatable volume needs a relief path, because trapped hydrazine plus heat equals pressure with no upper bound.

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Keep above | 280 K minimum, 285 K preferred | Freezing at 274.7 K, with margin |
| Keep below | 320 K | Thermal decomposition risk rises |
| Line velocity limit | 6 m/s | Water hammer, 2.07 MPa per m/s |
| Injector stiffness | 20 to 30 % of Pc | Isolates the feed from bed oscillations |
| Filtration | 10 to 25 micron absolute | Below d/10 of the smallest orifice |
| No copper alloys | Absolute | Decomposition catalysis |
| Seals | EPDM, butyl, PTFE only | Not NBR, not FKM |
| Leak allowable | ~1e-5 scc/s from a 0.01 ppm TLV | Drives welded and VCR joints |
| Propellant grade | Monopropellant grade minimum | Life, not performance |
| Purity for long life | Ultra pure for > 10^4 pulses | Ignition delay growth |
| Blowdown ratio | 4:1 typical | Thrust range vs ullage volume |
| Vapor detection | Instrumental only | Odor threshold is 300x the TLV |

---

## Failure modes

**Freezing.** Heater failure, thermostat failure, or an unheated section of line. The propellant freezes, the line is blocked, and on thaw the expansion may have burst something.

**Decomposition in the feed line.** From a catalytic contaminant (copper, iron oxide, a degraded seal) or from a local hot spot. Produces gas upstream of the injector, which causes flow instability and, in a blowdown system, a slow unexplained tank pressure rise.

**Trapped volume pressurization.** Hydrazine isolated between two valves, heated by soakback or by a failed-on heater. The pressure has no upper bound short of rupture.

**Catalyst poisoning.** Water, CO2, aniline or particulate accumulating on the bed. Manifests as growing ignition delay, then hard starts, then start failure.

**Seal degradation.** An incompatible elastomer softens, swells and sheds material into the propellant, which then poisons the catalyst. The seal failure and the bed failure arrive together.

**Personnel exposure.** From a joint broken without a proper purge, from a monitoring gap, or from inadequate PPE. The consequence is severe and the propellant gives no sensory warning at hazardous concentrations.

**Spill onto porous organic material.** Self-heating to ignition.

**Hard start.** A cold bed with a long ignition delay accumulates propellant, then lights all at once. The pressure spike damages the bed and the chamber.

---

## Worked example

Hydrazine properties at a typical spacecraft tank condition, 293.15 K and 2.4 MPa:

```python
from utils import fluidProps, hydrazineProps

density   = fluidProps('N2H4', 'TP', 'D',   293.15, 2.4e6)    # 1008.5 kg/m^3
viscosity = fluidProps('N2H4', 'TP', 'VIS', 293.15, 2.4e6)    # 9.74e-4 Pa-s
vapor     = fluidProps('N2H4', 'TP', 'P',   293.15, 2.4e6)    # 1428 Pa
```

Note that `fluidProps` routes hydrazine to a correlation table rather than to an equation of state, because neither REFPROP nor CoolProp models it. The correlations cover 275 to 450 K to about 1 to 2 percent, and only saturated liquid properties are returned; the pressure argument is accepted and ignored, which is a reasonable approximation for a nearly incompressible liquid at feed system pressures.

**The hazard-derived leak allowable**, for a 30 m^3 unventilated bay, an 8-hour exposure and the 0.01 ppm ACGIH TLV:

```python
from LeakPath import LeakPath

leak = LeakPath()
leak.setInputs({'species': 'He', 'upstreamPressure': 2.4e6, 'temperature': 293.15})
allowable = leak.calculateAllowableFromHazard(enclosureVolume = 30.0,
                                              concentrationLimit = 1e-8,
                                              exposureTime = 28800.0)
# allowableUnventilatedSccs = 1.04e-5 scc/s
```

That is tighter than an AN flare fitting achieves (1e-4 scc/s per joint), so a hydrazine system with flare joints in an unventilated bay does not close its own hazard analysis. Welded joints or VCR fittings are required, which is precisely why hydrazine systems are built that way.

**The water hammer surge** for a 6 m/s velocity change:

```
dP = rho * a * dV = 1008 * 2050 * 6 = 12.4 MPa
```

against a typical 2.4 MPa system pressure. That is why the velocity limit is 6 m/s and why closure times are computed rather than assumed.

---

## Standards

| Standard | Scope |
|---|---|
| MIL-PRF-26536 | Propellant, hydrazine (purity grades and test methods) |
| MIL-STD-1522 | Standard general requirements for safe design and operation of pressurized missile and space systems |
| AFSPCMAN 91-710 | Range safety user requirements (propellant handling) |
| NASA-STD-8719.12 | Safety standard for explosives, propellants and pyrotechnics |
| KSC-STD-Z-0005 | Design and operation of hazardous propellant facilities |
| NIOSH Pocket Guide | Hydrazine exposure limits and protective measures |
| ACGIH TLV | 0.01 ppm 8-hour TWA, skin notation |
| CGA P-1 | Safe handling of compressed gases (referenced for pressurant) |
| NASA SP-8087 | Liquid rocket engine fluid-cooled combustion chambers (hydrazine property data) |
| ASTM D1385 | Hydrazine in water |

---

## Tool interface

Hydrazine properties come from [`utils.hydrazineProps`](../utils.py), reached transparently through `fluidProps`:

```python
from utils import fluidProps, hydrazineProps

# Through the unified accessor, same call signature as any other fluid
rho, mu, cp = fluidProps('N2H4', 'TP', 'D VIS Cp', 293.15, 2.4e6)

# Or directly, which also exposes the fixed-point properties
freezingPoint = hydrazineProps('TMIN',  293.15)   # 274.69 K
boilingPoint  = hydrazineProps('TNBP',  293.15)   # 386.65 K
latentHeat    = hydrazineProps('H',     293.15)   # J/kg
```

Supported output codes: `D`, `VIS`, `TCX`, `Cp`, `STN`, `P` (vapor pressure), `H` (heat of vaporization), `M`, `TCRIT`, `PCRIT`, `TMIN` (freezing point), `TNBP`.

The propulsion side is in [`CatalystBed`](../CatalystBed.py) and [`MonopropThruster`](../MonopropThruster.py). Compatibility screening is built into [`Fitting.checkCompatibility`](../Fitting.py) and [`Seal.checkCompatibility`](../Seal.py), both of which raise `CompatibilityError` on a hydrazine-incompatible material rather than warning.

---

## References

1. Schmidt, E. W., *Hydrazine and Its Derivatives: Preparation, Properties, Applications*, 2nd ed., Wiley, 2001. The reference work.
2. MIL-PRF-26536F, *Propellant, Hydrazine*.
3. NASA SP-8087, *Liquid Rocket Engine Fluid-Cooled Combustion Chambers*, 1972.
4. Sutton, G. P. and Biblarz, O., *Rocket Propulsion Elements*, 9th ed., Wiley, 2016.
5. Wucherer, E. J. et al., "Hydrazine Catalyst Production", AIAA 2003-5079.
6. NIOSH, *Pocket Guide to Chemical Hazards*, hydrazine entry.
7. Clark, J. D., *Ignition! An Informal History of Liquid Rocket Propellants*, Rutgers University Press, 1972.
8. AFRPL-TR-69-149, *Hydrazine Handling Manual*.
