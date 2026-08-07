[Home](../../README.md) > Catalyst Beds

# Catalyst Beds

## Contents

- [Overview](#overview)
- [The catalyst](#the-catalyst)
- [Decomposition chemistry](#decomposition-chemistry)
- [Bed sizing](#bed-sizing)
  - [Bed loading](#bed-loading)
  - [Bed length and residence time](#bed-length-and-residence-time)
  - [Granule size and grading](#granule-size-and-grading)
- [Pressure drop](#pressure-drop)
- [Starting](#starting)
- [Life and degradation](#life-and-degradation)
- [Bed hardware](#bed-hardware)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Operations](#operations)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A catalyst bed is the combustion chamber of a monopropellant thruster. It has no igniter, no oxidizer and no spray to worry about: liquid hydrazine contacts an iridium-on-alumina catalyst, decomposes spontaneously, and leaves as hot gas at 900 to 1600 K.

That simplicity is why monopropellant systems have flown continuously since the 1960s. It is also deceptive, because almost everything that determines whether a bed works is empirical. There is no first-principles way to predict the ammonia dissociation fraction from the bed geometry, no reliable way to predict the pressure drop of a two-phase reacting packed bed, and no way to predict catalyst life without testing. Catalyst bed design is a matter of applying well-established heuristics and then testing.

The three sizing quantities are:

| Quantity | Symbol | What it controls |
|---|---|---|
| **Bed loading** | G [kg/m^2-s] | Bed diameter. Narrow acceptable band |
| **Bed length** | L | Residence time, ammonia dissociation, chamber temperature |
| **Granule size** | d_p | Pressure drop, surface area, attrition resistance |

---

## The catalyst

**Shell 405** is iridium on a high surface area alumina support, roughly 32 weight percent iridium. Developed by Shell Development Company under Navy and JPL sponsorship in 1962, it remains the reference hydrazine catalyst.

What makes it special is that it is **spontaneous**: hydrazine decomposes on contact at temperatures down to roughly 275 K, with no ignition source. Every earlier hydrazine catalyst required a preheat or a hypergolic start slug. Spontaneity is what makes a monopropellant attitude control system possible, because a thruster that must be preheated before every 20 ms pulse is not usable.

| Catalyst | Bulk density | Void fraction | Minimum start T | Notes |
|---|---|---|---|---|
| **Shell 405** | 1200 kg/m^3 | 0.37 | 275 K | The reference. ~32 wt% Ir |
| LCH-202 | 1150 kg/m^3 | 0.38 | 280 K | European equivalent |
| H-KC12GA | 1250 kg/m^3 | 0.36 | 285 K | Slightly lower activity, better attrition resistance |

**The iridium content dominates the cost** of a small thruster. A 150 g catalyst charge contains roughly 48 g of iridium, which at any plausible price is a significant fraction of the hardware cost. That is a real constraint on bed sizing: there is a direct financial incentive not to oversize.

**The support matters as much as the metal.** The alumina must be high surface area (to disperse the iridium), thermally stable (the bed cycles from ambient to 1400 K in milliseconds, thousands of times), and mechanically strong (it is being hammered by liquid impingement and pressure transients). Support degradation, not iridium loss, is what usually ends a bed's life.

---

## Decomposition chemistry

Two steps:

```
3 N2H4  ->  4 NH3 + N2         dH = -112.3 kJ per mol N2H4    exothermic, fast
4 NH3   ->  2 N2 + 6 H2        dH =  +46.0 kJ per mol NH3     endothermic, slower
```

The first step is fast and goes essentially to completion in the first few millimetres of bed. The second is slower and its extent depends on residence time, which is why it is the bed length that controls it.

Combined, with ammonia dissociation fraction `X`:

```
N2H4  ->  (4/3)(1-X) NH3  +  (1/3 + (2/3)X) N2  +  2X H2
```

Total moles go from 5/3 at `X = 0` to 3 at `X = 1`, so the mean molecular weight falls from 19.2 g/mol to 10.7 g/mol.

**The energy balance.** Heat released per mole of hydrazine:

```
Q(X) = 112.3 - 46.0 * (4/3) * X  =  112.3 - 61.3*X    [kJ/mol N2H4]
```

Applied to the product mixture, this gives an adiabatic temperature that is very nearly linear in `X`:

```
T_adiabatic = 1659 - 765*X       [K, propellant initially at 298 K]
```

| X | T [K] | MW [g/mol] | gamma | c* [m/s] |
|---|---|---|---|---|
| 0.0 | 1659 | 19.23 | 1.27 | 1278 |
| 0.2 | 1500 | 16.58 | 1.29 | 1304 |
| **0.38** | **1362** | **14.75** | **1.31** | **1311** |
| 0.4 | 1347 | 14.57 | 1.31 | 1311 |
| 0.6 | 1194 | 12.99 | 1.33 | 1300 |
| 0.8 | 1041 | 11.72 | 1.35 | 1268 |
| 1.0 | 894 | 10.68 | 1.37 | 1224 |

**Characteristic velocity has a broad interior maximum.** Because `c* ~ sqrt(T/MW)` and both `T` and `MW` fall with `X`, there is an optimum around `X = 0.38`. But the peak is very flat: c* varies by only 3 percent between `X = 0.2` and `X = 0.6`.

**Chamber temperature is not flat.** It falls by more than 300 K over that same range.

**Therefore bed length is chosen for thermal reasons, not performance reasons.** A longer bed dissociates more ammonia, which barely changes c* but substantially reduces the chamber temperature, the throat heat load, the chamber wall temperature and the valve soakback. On a spacecraft thruster that has to survive thousands of cycles, that thermal relief is worth far more than a 1 percent performance difference. Typical designs run `X = 0.3` to `0.5`.

---

## Bed sizing

### Bed loading

Bed loading is the mass flow per unit bed frontal area:

```
G = mdot / A_bed
```

It is the primary sizing parameter and it has a **narrow acceptable band**:

| G [kg/m^2-s] | G [lbm/in^2-s] | Consequence |
|---|---|---|
| below 10 | below 0.014 | **The bed runs cold and wet.** Not enough heat is generated per unit area to hold the bed above the decomposition temperature. Liquid hydrazine works its way through undecomposed |
| 10 to 20 | 0.014 to 0.028 | Low end. Acceptable for long-duration steady firing |
| **20 to 30** | **0.028 to 0.043** | **The design band. Nominal is around 25** |
| 30 to 40 | 0.043 to 0.057 | High end. Used for pulse-mode thrusters where the duty cycle is low |
| above 40 | above 0.057 | Residence time too short, dissociation falls, catalyst physically erodes |

**Undecomposed hydrazine reaching the throat is a hard failure.** It flashes in the nozzle, produces no thrust, and if it accumulates it can detonate. The low-loading limit is therefore not a performance guideline; it is a safety limit.

Bed loading also changes over the life of a thruster: as catalyst attrites and washes out, the effective bed volume falls and the loading on the remaining catalyst rises.

### Bed length and residence time

There is no first-principles way to predict the bed length required for a given ammonia dissociation. The design heuristic is length-to-diameter ratio:

| L/D | Typical use |
|---|---|
| 0.5 to 1.0 | Short bed, low dissociation, high chamber temperature, minimum pressure drop |
| **1.0 to 2.0** | **The usual range** |
| 2.0 to 3.0 | Long bed, high dissociation, low chamber temperature, high pressure drop |

The gas-phase residence time in the void volume is what actually governs the dissociation kinetics:

```
t_residence = (V_bed * epsilon * rho_gas) / mdot
```

and it comes out in the range of 1 to 5 ms for typical designs. That is short, which is why the second reaction step does not go to completion and why `X` sits well below 1.

**Real design practice runs the calculation backwards**: build a bed, fire it, measure the chamber pressure and mass flow, infer c*, back out `X`, and then use that `X` for the rest of the design. The [`CatalystBed`](../CatalystBed.py) class exposes `ammoniaDissociation` as an input for exactly that reason.

### Granule size and grading

| Mesh | Size range | Use |
|---|---|---|
| 14-18 | 1.41 to 1.00 mm | Coarse. Inlet layer |
| **20-25** | **0.841 to 0.707 mm** | **General purpose** |
| 25-30 | 0.707 to 0.595 mm | Fine. Downstream layer |
| 30-35 | 0.595 to 0.500 mm | Very fine, high pressure drop |

The size trade is direct:

- **Smaller granules** give more surface area per unit volume (faster decomposition, shorter bed) but much more pressure drop (Ergun scales as `1/d_p^2` viscous and `1/d_p` inertial) and are more prone to being blown out of the bed.
- **Larger granules** give the reverse.

**Most beds are graded.** A coarse layer at the inlet survives the liquid impingement from the injector, which is mechanically the most severe location in the bed; a finer layer downstream provides the surface area for the ammonia dissociation without seeing the impingement. Two or three layers separated by screens is standard.

---

## Pressure drop

The Ergun equation for a packed bed:

```
dP/L = 150 * mu * (1-eps)^2 * U / (eps^3 * d_p^2)      viscous, Blake-Kozeny
     + 1.75 * (1-eps) * rho * U^2 / (eps^3 * d_p)      inertial, Burke-Plummer
```

with `U` the superficial velocity (volumetric flow over the total bed frontal area, as if the bed were empty).

**This is a substantial approximation and it must be treated as one.** A hydrazine catalyst bed is not a single-phase packed bed:

- The inlet is liquid at roughly 1000 kg/m^3
- The outlet is hot gas at roughly 2 kg/m^3
- The transition happens over the first few particle diameters
- The volumetric flow rate rises by a factor of several hundred across that transition
- Most of the pressure drop occurs exactly in the region where the density is changing fastest

The [`CatalystBed`](../CatalystBed.py) class evaluates Ergun at the hot gas exit condition, which is where the superficial velocity and therefore the inertial term are largest. That is deliberately conservative and it is right within about a factor of two.

**Real bed pressure drops are measured, not calculated.** Typical values are 10 to 25 percent of chamber pressure. If a calculation returns much more than that, the sizing is off (too fine a granule, too long a bed, too high a loading) rather than the correlation being wrong.

**The bed pressure drop is part of the feed system budget.** The tank must supply the chamber pressure plus the bed drop plus the injector drop plus the line losses, so a bed that costs 25 percent of chamber pressure raises the required tank pressure by that much and drives tank mass.

---

## Starting

**Spontaneous start.** Shell 405 decomposes hydrazine on contact at temperatures down to about 275 K. No igniter, no preheat, no start slug. This is the whole reason the catalyst exists.

**Ignition delay** is the time from valve opening to chamber pressure rise. It is strongly temperature dependent, roughly Arrhenius:

| Bed temperature | Estimated ignition delay |
|---|---|
| 273 K | ~35 ms |
| 293 K | ~21 ms |
| 320 K | ~9 ms |
| 350 K | ~3 ms |
| 400 K | ~1 ms |

**Why the delay matters:** during the delay, propellant accumulates in the bed undecomposed. When it does light, all of it decomposes at once, producing a **hard start**: a pressure spike that can be several times the nominal chamber pressure. Repeated hard starts:

- Shatter the catalyst granules
- Produce fines that wash out of the bed
- Erode the bed retention screens
- Fatigue the chamber and the injector

**Catalyst bed heaters exist for exactly this reason.** A spacecraft monopropellant thruster is typically held at 350 to 400 K by a bed heater before any firing. That eliminates the delay, eliminates the hard start, and substantially extends catalyst life. The heater power is a real budget item and its failure is a credible fault, but the alternative is worse.

**Cold start below 275 K** is where the trouble is. Ignition delay grows to hundreds of milliseconds, the accumulated propellant is large, and the start is violent. Below the propellant freezing point at 274.7 K there is no start at all.

---

## Life and degradation

Catalyst beds degrade rather than fail suddenly. The observable is **ignition delay growth**: a bed that started in 3 ms when new takes 10 ms after a few thousand pulses, then 30 ms, then fails to start.

**Degradation mechanisms:**

| Mechanism | Cause | Effect |
|---|---|---|
| **Attrition** | Thermal cycling, pressure transients, liquid impingement | Granules crack and produce fines. Fines wash out, bed volume falls, remaining granules see higher loading |
| **Sintering** | High temperature exposure | Iridium crystallites grow and coalesce, reducing active surface area |
| **Support degradation** | Thermal cycling, hydrothermal attack from water | Alumina loses surface area and mechanical strength |
| **Poisoning** | Contaminants in the propellant | Active sites blocked, permanently in most cases |
| **Washout** | Fines and whole granules carried out of the bed | Bed voids, flow channels through the void, local overheating |

**Catalyst poisons:**

| Poison | Source | Limit | Note |
|---|---|---|---|
| **Water** | Hygroscopic propellant, any air exposure | 1.0 wt% (MIL-PRF-26536) | The most common contaminant |
| **Aniline** | Hydrazine production residual | 0.5 wt% standard, 0.003 wt% ultra pure | Permanently adsorbed |
| **Carbon dioxide** | Air exposure of propellant or bed | -- | Forms carbonate on the alumina |
| **Chlorides** | Cleaning solvents, bare hands, PVC | -- | Attack both the support and the iridium |
| **Sulfur** | Any source | -- | Classic noble metal poison, permanent |
| Metals (Fe, Cu, Mo, Co) | System materials, corrosion | -- | Catalyze decomposition upstream of the bed rather than in it |

**Life expectations.** A well-designed bed on ultra pure propellant with a bed heater achieves tens of thousands of pulses and hundreds of thousands of seconds of cumulative firing. The same bed on standard grade propellant with cold starts may fail in hundreds of cycles. **The propellant grade and the bed heater are life decisions, not performance decisions.**

---

## Bed hardware

**Retention screens.** The catalyst is held between an upstream and a downstream screen or perforated plate. The downstream retainer is the critical one: it has to hold the catalyst against the full flow at 1400 K, cycle after cycle, without blinding or fatiguing. Retainer failure dumps catalyst into the throat.

**Bed springs and preload.** The bed is preloaded so the granules cannot move relative to each other. An unloaded bed lets granules vibrate and abrade one another, which accelerates attrition dramatically. Thermal expansion has to be accommodated in the preload design, since the bed and the chamber wall grow differently.

**Injector.** For a monopropellant thruster, the injector distributes propellant across the bed frontal area. Distribution quality matters more than atomization: a bed with a maldistributed inlet develops hot and cold regions, the cold regions pass undecomposed propellant, and the hot regions sinter. Multi-element or showerhead injectors, and sometimes a distribution plate, are used.

**Thermal standoff.** The bed runs at 900 to 1400 K and the valve immediately upstream must stay below its seal temperature limit. A thermal standoff (a thin-wall low-conductivity section between the valve and the bed) plus a radiator or a conduction path is standard, and **soakback after shutdown is often more limiting than the steady-state temperature**, because at shutdown the coolant flow stops but the bed is still hot.

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Bed loading | 20 to 30 kg/m^2-s nominal | Cold and wet below 10, erosion above 40 |
| Bed L/D | 1.0 to 2.0 | Empirical; sets residence time |
| Gas residence time | 1 to 5 ms | Governs ammonia dissociation |
| Ammonia dissociation | 0.3 to 0.5 | Broad c* peak at 0.38; choose for thermal reasons |
| Granule size | 20-25 mesh general, 14-18 at the inlet | Coarse survives impingement |
| Bed pressure drop | 10 to 25 % of Pc | Higher means the sizing is off |
| Injector stiffness | 20 to 30 % of Pc | Isolates the feed from bed oscillations |
| Bed heater setpoint | 350 to 400 K | Eliminates ignition delay and hard starts |
| Propellant grade | Ultra pure for > 10^4 pulses | Life, not performance |
| Filtration | 10 to 25 micron absolute upstream | Particulate abrades catalyst |
| Bed preload | Always | Unloaded granules abrade one another |
| Design for soakback, not just steady state | Always | The valve sees its worst temperature after shutdown |

---

## Failure modes

**Cold and wet bed.** Bed loading too low, or bed temperature too low. Undecomposed hydrazine reaches the throat. A hard failure and potentially an explosive one.

**Hard start.** Long ignition delay allows propellant to accumulate, then it lights all at once. Shatters catalyst, erodes retainers, fatigues the chamber.

**Catalyst attrition and washout.** Fines are generated by thermal cycling and mechanical loading, then carried out. The bed voids, flow channels through the void, and the remaining catalyst is overloaded.

**Retainer failure.** The downstream screen fails and catalyst is dumped into the throat. Immediate and complete loss of the thruster.

**Poisoning.** Progressive ignition delay growth ending in start failure. Slow, and it looks like normal ageing until it is not.

**Sintering.** High temperature exposure coalesces the iridium crystallites and reduces active surface. Aggravated by low ammonia dissociation, which is a reason not to run a bed too short.

**Maldistributed injection.** Hot and cold regions across the bed face. Cold regions pass propellant, hot regions sinter. Often shows up as an asymmetric temperature signature on the chamber.

**Valve soakback.** After shutdown the bed is hot and there is no flow to carry the heat away. The valve seat sees its maximum temperature minutes after the firing ends, and this is what usually sets the seat material.

**Decomposition upstream.** A catalytic contaminant in the feed line decomposes propellant before it reaches the bed. Gas in the feed line destabilizes the flow.

---

## Operations

**Never expose a bed to air unnecessarily.** CO2 and moisture both poison it. Beds are shipped and stored under dry nitrogen, and the caps come off at installation.

**Bake out before first use** if the bed has been exposed. Vacuum bake at elevated temperature drives off adsorbed water and CO2, and recovers much of the lost activity.

**Track ignition delay across the life of the thruster.** It is the single best health indicator and it costs nothing to record if chamber pressure is already instrumented.

**Verify propellant purity before loading.** The certificate of analysis is the cheapest life insurance available.

**Preheat before firing** wherever the mission allows it. A 350 K bed lights in milliseconds; a 275 K bed lights in tens of milliseconds with a hard start.

**Do not fire a bed below the propellant freezing point.** There is nothing to decompose.

---

## Worked example

A 100 N class hydrazine thruster: 0.045 kg/s at 1.5 MPa chamber pressure, propellant at 293.15 K, nominal bed loading, Shell 405 with 20-25 mesh granules, `X = 0.40`.

**Chemistry:**

| Quantity | Value |
|---|---|
| Chamber temperature | 1347 K |
| Products per mol N2H4 | 0.800 NH3 + 0.600 N2 + 0.800 H2 |
| Product molar mass | 14.566 g/mol |
| Specific gas constant | 570.8 J/kg-K |
| Specific heat ratio | 1.310 |
| **Characteristic velocity** | **1311 m/s** |

**Geometry at 25 kg/m^2-s bed loading and L/D = 1.5:**

| Quantity | Value |
|---|---|
| Bed loading | 25.0 kg/m^2-s (0.0356 lbm/in^2-s) |
| Bed frontal area | 18.00 cm^2 |
| Bed diameter | 47.87 mm |
| Bed length | 71.81 mm |
| Bed volume | 129.3 cm^3 |
| Catalyst mass | 155.1 g |
| Void fraction | 0.37 |
| Gas residence time | 2.07 ms |

**Pressure drop** (Ergun at the hot gas exit): 725 kPa, which is 48 percent of chamber pressure. The class flags this: a typical bed runs 10 to 25 percent, so this design is out of family. The remedies in order of preference are a coarser granule (14-18 mesh roughly doubles `d_p` and cuts the inertial term in half), a shorter bed, or a lower bed loading (which increases the frontal area and cuts the superficial velocity).

**Cold start at 293 K:** estimated ignition delay 21 ms, hard start risk moderate. The class recommends a bed heater at 350 to 400 K, which would bring the delay to about 3 ms.

**Optimal dissociation sweep:** the peak c* of 1311 m/s occurs at `X = 0.38` with a chamber temperature of 1362 K. Running at `X = 0.6` instead costs 0.8 percent of c* and buys 168 K of chamber temperature relief, which on a long-life thruster is a trade worth making.

Reproduce with:

```python
from CatalystBed import CatalystBed

bed = CatalystBed()
bed.setInputs({'massFlow': 0.045, 'chamberPressure': 1.5e6,
               'inletTemperature': 293.15, 'ammoniaDissociation': 0.40,
               'catalyst': 'shell 405', 'meshSize': '20-25',
               'lengthToDiameterRatio': 1.5, 'bedTemperature': 293.15})

bed.calculateDecomposition()
bed.sizeBed()
bed.calculatePressureDrop()
bed.checkColdStart()
print(bed.generateReport())

optimum = bed.optimalDissociation()
print(optimum['optimalDissociation'], optimum['maximumCharacteristicVelocity'])
```

---

## Standards

| Standard | Scope |
|---|---|
| MIL-PRF-26536 | Propellant, hydrazine (purity grades that set catalyst life) |
| MIL-C-83125 | Catalyst, hydrazine decomposition (Shell 405 type) |
| NASA SP-8087 | Liquid rocket engine fluid-cooled combustion chambers |
| NASA SP-8089 | Liquid rocket engine injectors |
| NASA SP-8113 | Liquid rocket engine combustion stabilization devices |
| AIAA S-080 | Space systems metallic pressure vessels and pressure components |
| JANNAF | Liquid propulsion test and performance methodology |

---

## Tool interface

The [`CatalystBed`](../CatalystBed.py) class covers the chemistry, sizing, pressure drop and start behaviour.

```python
from CatalystBed import CatalystBed

bed = CatalystBed()
bed.setInputs({'massFlow': 0.045, 'chamberPressure': 1.5e6,
               'inletTemperature': 293.15, 'ammoniaDissociation': 0.40,
               'catalyst': 'shell 405', 'meshSize': '20-25',
               'bedLoading': 25.0, 'lengthToDiameterRatio': 1.5,
               'bedTemperature': 350.0})

bed.calculateDecomposition()    # T, MW, gamma, c*, product composition
bed.sizeBed()                   # diameter, length, volume, catalyst mass, residence time
bed.calculatePressureDrop()     # Ergun
bed.checkColdStart()            # ignition delay, hard start risk
bed.optimalDissociation()       # the X that maximizes c*, plus the full sweep
print(bed.generateReport())
```

Lookup tables: `CatalystBed.CATALYSTS`, `CatalystBed.MESH_SIZES`, `CatalystBed.CATALYST_POISONS`, and the bed loading limits `BED_LOADING_MINIMUM`, `BED_LOADING_NOMINAL`, `BED_LOADING_MAXIMUM`.

A `CatalystBed` instance can be handed directly to a [`MonopropThruster`](../MonopropThruster.py) so the nozzle is sized from the actual bed chemistry rather than from the nominal propellant table.

---

## References

1. Schmidt, E. W., *Hydrazine and Its Derivatives*, 2nd ed., Wiley, 2001.
2. Sutton, G. P. and Biblarz, O., *Rocket Propulsion Elements*, 9th ed., Wiley, 2016.
3. Grant, A. F., *Basic Factors Involved in the Design and Operation of Catalytic Monopropellant Hydrazine Reaction Chambers*, JPL Report 20-77, 1954.
4. Kesten, A. S., *Analytical Study of Catalytic Reactors for Hydrazine Decomposition*, NASA CR-1656, 1970.
5. Ergun, S., "Fluid Flow through Packed Columns", *Chemical Engineering Progress*, Vol. 48, 1952.
6. Wucherer, E. J., Christofferson, S. and Reed, B., "Assessment of High Performance HAN Monopropellants", AIAA 2000-3872.
7. Price, T. W. and Evans, D. D., *The Status of Monopropellant Hydrazine Technology*, JPL Technical Report 32-1227, 1968.
8. NASA SP-8087, *Liquid Rocket Engine Fluid-Cooled Combustion Chambers*, 1972.
