[Home](../../README.md) > Monopropellant Thrusters and Gas Generators

# Monopropellant Thrusters and Gas Generators

## Contents

- [Overview](#overview)
- [Performance](#performance)
- [Nozzle sizing](#nozzle-sizing)
- [Efficiency and the small thruster problem](#efficiency-and-the-small-thruster-problem)
- [Blowdown operation](#blowdown-operation)
- [Pulse mode](#pulse-mode)
- [Propellant selection](#propellant-selection)
- [Gas generators](#gas-generators)
- [Thermal design](#thermal-design)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Operations](#operations)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A monopropellant thruster is a catalyst bed with a nozzle on it, a valve in front of it and a heater wrapped around it. That is the whole device.

The performance is modest: 220 to 235 s of vacuum specific impulse for hydrazine, against 320 s for a storable bipropellant and 450 s for hydrolox. The reason it is used anyway is everything else:

| Property | Consequence |
|---|---|
| One propellant | One tank, one feed system, no mixture ratio control |
| Spontaneous catalytic start | No igniter, no ignition sequence, no start transient to tune |
| Millisecond pulse capability | Attitude control with fine impulse resolution |
| Very high cycle life | Tens of thousands of pulses over a decade |
| Roughly three moving parts | A valve, and optionally a second valve for redundancy |

The [`CatalystBed`](../CatalystBed.py) class covers the chemistry and the bed. This document and the [`MonopropThruster`](../MonopropThruster.py) class cover the nozzle, the delivered performance, the blowdown behaviour and the pulse mode.

**Gas generators** are the same device used for a different purpose: producing warm gas to drive a turbine, pressurize a tank, or actuate something, rather than to produce thrust. Everything about the bed is the same; the nozzle is replaced by a duct.

---

## Performance

**Characteristic velocity** is set by the bed and is covered in [CatalystBeds.md](CatalystBeds.md). For hydrazine at typical dissociation it is around 1310 m/s ideal.

**Thrust coefficient** is set by the nozzle:

```
Cf_ideal = sqrt( (2*g^2/(g-1)) * (2/(g+1))^((g+1)/(g-1)) * (1 - (Pe/Pc)^((g-1)/g)) )
         + (Pe - Pa)/Pc * epsilon
```

The first term is the momentum contribution and the second is the pressure thrust. **In vacuum the pressure thrust term is entirely positive and grows with expansion ratio**, which is why vacuum thrusters use large area ratios and why a spacecraft thruster looks like a small chamber with an enormous bell on it.

**Specific impulse:**

```
Isp = c* * Cf / g0
```

**Expansion ratio trade** for hydrazine at 1.5 MPa chamber pressure, vacuum:

| Expansion ratio | Exit Mach | Cf (ideal) | Vacuum Isp [s] | Exit diameter / throat diameter |
|---|---|---|---|---|
| 10 | 3.55 | 1.60 | 198 | 3.2 |
| 20 | 4.14 | 1.69 | 209 | 4.5 |
| **50** | **5.16** | **1.80** | **222** | **7.1** |
| 100 | 6.05 | 1.86 | 230 | 10.0 |
| 200 | 7.05 | 1.91 | 236 | 14.1 |
| 400 | 8.18 | 1.95 | 241 | 20.0 |

The returns diminish steeply. Going from 50 to 100 buys 8 s of Isp and adds 40 percent to the nozzle diameter; going from 100 to 200 buys 6 s and adds another 40 percent. Real spacecraft thrusters run between 50 and 300 depending on how much envelope is available.

**Sea level operation** is a different problem entirely. A nozzle with an exit pressure below roughly 35 percent of ambient will flow separate, which produces side loads and unstable thrust. A thruster intended for sea level test has to be sized for it or tested in an altitude chamber.

---

## Nozzle sizing

```
At = mdot * c* / Pc                  throat area from mass flow
At = F / (Pc * Cf)                   throat area from required thrust
Ae = At * epsilon
```

**Throat diameter scale.** For hydrazine at 1.5 MPa chamber pressure:

| Thrust | Mass flow | Throat diameter |
|---|---|---|
| 0.5 N | 0.00023 kg/s | 0.53 mm |
| 5 N | 0.0023 kg/s | 1.6 mm |
| 22 N | 0.010 kg/s | 3.3 mm |
| 100 N | 0.046 kg/s | 7.0 mm |
| 445 N | 0.20 kg/s | 14.8 mm |

**A 0.5 mm throat is the fundamental problem of small thrusters.** It is a hole small enough that the boundary layer is a significant fraction of it, small enough that any particle plugs it, and small enough that manufacturing tolerance is a meaningful fraction of the area.

**Nozzle contour.** Conical at 15 degrees half angle is standard for monopropellant thrusters, and the divergence efficiency is

```
lambda = (1 + cos(alpha)) / 2 = 0.983 at 15 degrees
```

A bell contour recovers most of that 1.7 percent. On a small thruster the boundary layer loss is five to ten times larger than the divergence loss, so the contouring effort is not repaid and a conical nozzle is usually the right engineering answer. On a large thruster (above about 100 N) a bell is worth having.

---

## Efficiency and the small thruster problem

Three efficiency factors are applied to the ideal performance:

| Factor | What it accounts for |
|---|---|
| c* efficiency | Decomposition completeness and heat loss in the bed |
| Divergence | Non-axial exit momentum |
| **Boundary layer** | **Viscous loss in the throat and nozzle** |

The boundary layer term dominates for small thrusters:

| Thrust class | c* efficiency | Boundary layer efficiency | Combined |
|---|---|---|---|
| Above 100 N | 0.96 | 0.98 | 0.94 |
| 10 to 100 N | 0.95 | 0.96 | 0.91 |
| 1 to 10 N | 0.93 | 0.92 | 0.86 |
| **Below 1 N** | **0.90** | **0.85** | **0.77** |

**This is why a 1 N hydrazine thruster delivers around 200 s while a 445 N unit delivers 235 s from identical chemistry.** The boundary layer displacement thickness in a 0.5 mm throat is a meaningful fraction of the throat radius, so a substantial part of the flow area is occupied by low-momentum fluid. No amount of nozzle contouring recovers it, and the loss grows as the thruster gets smaller.

Flight examples, all hydrazine:

| Thruster | Thrust | Vacuum Isp | Expansion ratio |
|---|---|---|---|
| Aerojet MR-103 | 1.0 N | 209 s | ~100 |
| Aerojet MR-111 | 4.5 N | 215 s | ~100 |
| Aerojet MR-106 | 22 N | 228 s | ~80 |
| Aerojet MR-107 | 245 N | 229 s | ~50 |
| Aerojet MR-104 | 445 N | 235 s | ~60 |

The trend with size is unmistakable and it is almost entirely the boundary layer.

---

## Blowdown operation

Most spacecraft monopropellant systems are blowdown: the propellant tank is charged with pressurant once, and the pressure falls as propellant is consumed. No regulator, no pressurant bottle, no isolation valves.

**Thrust falls with tank pressure.** Chamber pressure tracks feed pressure nearly proportionally (the injector and the bed are both roughly square-law resistances in series with a choked throat), and thrust is proportional to chamber pressure:

```
F ~ Pc,     mdot ~ Pc,     Isp roughly constant
```

Specific impulse is nearly constant because c* is almost independent of chamber pressure and, in vacuum, `Pe/Pc` is fixed by the expansion ratio so `Cf` is fixed too.

**Blowdown ratio trade:**

| Blowdown ratio | Final thrust | Initial ullage / propellant volume | Tank oversizing |
|---|---|---|---|
| 2:1 | 50 % | 100 % | 2.00x |
| 3:1 | 33 % | 50 % | 1.50x |
| **4:1** | **25 %** | **33 %** | **1.33x** |
| 5:1 | 20 % | 25 % | 1.25x |
| 10:1 | 10 % | 11 % | 1.11x |

A higher blowdown ratio needs less ullage volume but delivers a wider thrust range. Beyond about 4:1 the low-end thrust becomes impractical, which is why 4:1 is close to universal.

**The design implications are all on the vehicle side:**

- The attitude control system must be stable across a 4:1 thrust range
- **The minimum impulse bit changes by the same factor**, which is what actually limits pointing accuracy at end of life
- Burn durations grow by 4x for the same delta-V, so thermal soakback grows
- The propellant tank has to be sized for the initial pressure AND for the initial ullage

The ullage sizing and pressurant mass are covered in [PressurizationAndBlowdown.md](PressurizationAndBlowdown.md) and in the [`Pressurization`](../Pressurization.py) class.

---

## Pulse mode

A monopropellant thruster used for attitude control spends most of its life firing pulses of a few tens of milliseconds. The impulse delivered by a short pulse is much less than `F * t`, because:

1. The valve takes time to open, during which thrust is building
2. **The bed has to light**, which is the ignition delay and is the dominant term for a cold bed
3. The chamber has to fill to pressure, which takes a few residence times
4. On closing, the valve shuts but the bed continues to decompose the propellant already in it, producing a **tail-off impulse** that is not commanded and is not repeatable

A simple model:

```
t_effective = t_commanded - t_ignitionDelay - 0.5*t_open + 0.5*t_close
I_bit       = F * t_effective
```

Opening subtracts, closing adds, and the ignition delay subtracts outright.

**Worked numbers** for a 100 N thruster with 5 ms symmetric valve transients:

| Bed temperature | Ignition delay | 10 ms pulse | 20 ms pulse | 50 ms pulse | 200 ms pulse |
|---|---|---|---|---|---|
| **293 K (cold)** | 21 ms | **no light** | **no light** | 58 % | 90 % |
| **373 K (heated)** | 1.6 ms | **84 %** | 92 % | 97 % | 99 % |

**A cold bed cannot deliver a 20 ms pulse at all.** The ignition delay exceeds the pulse width, the valve closes before the bed lights, and the propellant that went in either decomposes as an uncommanded tail-off or does not decompose at all. That is the practical argument for catalyst bed heaters, stated in impulse terms rather than in life terms.

**Minimum impulse bit and pointing accuracy.** The minimum repeatable impulse bit, combined with the moment arm and the vehicle inertia, sets the attitude deadband achievable. It is a system-level number and it is why very fine pointing requirements drive toward smaller thrusters, electric propulsion, or reaction wheels rather than toward shorter pulses on a large thruster.

**Pulse-to-pulse repeatability** matters as much as the mean. The scatter is dominated by the ignition delay scatter, which is why a heated bed is not just faster but more repeatable.

---

## Propellant selection

| Propellant | rho [kg/m^3] | Tc [K] | Isp_vac [s] | rho*Isp [kN-s/m^3] | T_freeze [K] | Preheat |
|---|---|---|---|---|---|---|
| **Hydrazine** | 1008 | 1350 | 222 | 223 | 274.7 | no |
| **AF-M315E / ASCENT** | 1465 | 1900 | 253 | **371** | 208 | **yes** |
| **LMP-103S** | 1240 | 1900 | 248 | 307 | 183 | **yes** |
| 90 % hydrogen peroxide | 1390 | 1020 | 166 | 230 | 262 | no |
| 98 % hydrogen peroxide | 1430 | 1230 | 173 | 247 | 272 | no |

*Isp at expansion ratio 50 with realistic efficiency applied.*

**Read the density-impulse column, not the Isp column.** For a volume-limited spacecraft, which is almost all of them, `rho * Isp` is the figure of merit, and the green propellants win decisively: AF-M315E delivers 66 percent more density-impulse than hydrazine despite only a 14 percent Isp advantage.

**Green monopropellants** (AF-M315E/ASCENT, HAN-based; LMP-103S, ADN-based) also remove the toxicity handling burden entirely, which for a small satellite program is often worth more than the performance. The costs are real:

- **1900 K chamber temperature** against 1350 K for hydrazine. That requires iridium-rhenium or similar refractory chamber materials, which are expensive and have their own manufacturing challenges.
- **A catalyst bed preheat to roughly 640 K is mandatory** before every start. That is a substantial power draw and a much more demanding thermal design than a hydrazine bed heater at 350 K.
- Less flight heritage, though both have now flown (LMP-103S on PRISMA, AF-M315E on the NASA GPIM mission).

**Hydrogen peroxide** decomposes over a silver or manganese oxide catalyst to steam and oxygen. Low performance, but the products are non-toxic, the density is high, and the decomposition products are an oxidizer, which makes it usable as the oxidizer half of a bipropellant. It requires scrupulous cleanliness: any catalytic contamination causes runaway decomposition in the tank, and it decomposes slowly in storage regardless, so a vent path is mandatory.

---

## Gas generators

A gas generator is a catalyst bed producing warm gas for a purpose other than thrust:

| Application | Requirement | Design consequence |
|---|---|---|
| **Turbine drive** | Gas temperature below the turbine material limit, typically 900 to 1200 K | Run the bed long (high ammonia dissociation) to reduce temperature, or dilute |
| **Tank pressurization** | Gas compatible with the propellant, temperature low enough for the tank | Hydrazine gas generators pressurizing a hydrazine tank are self-compatible, which is elegant |
| **Actuation** | Fast response, defined total gas volume | Sized on gas volume rather than mass flow |
| **Emergency power (APU)** | Sustained duty, defined power | Bed life and thermal management dominate |

**The design driver is almost always the exit temperature**, not the performance. Where a thruster runs a short bed to keep c* up, a gas generator runs a long bed to push the ammonia dissociation toward 1.0 and get the temperature down to 894 K, which is the practical floor for pure hydrazine. Below that requires dilution with a diluent gas or with water.

**Hydrazine gas generators** have flown as APU drives (the X-15, the Shuttle APUs used hydrazine) and as tank pressurization sources. The Shuttle APU case is instructive: three hydrazine-fuelled APUs each drove a turbine at 72 000 rpm, and the whole system existed because hydrazine is storable, restartable and produces clean gas.

---

## Thermal design

**Soakback is usually more limiting than steady state.** During a firing, propellant flow cools the injector and the valve. At shutdown the flow stops but the bed is still at 1350 K, and heat conducts forward into the valve. The valve seat sees its maximum temperature **minutes after the firing ends**.

Design responses:

- A thermal standoff between the valve and the bed: a thin-wall, low-conductivity section that restricts the conduction path
- A radiator or a conduction path to the spacecraft structure at the standoff
- Seat materials chosen for the soakback temperature, not the operating temperature
- Duty cycle limits: a minimum off time between firings so the soakback can dissipate

**Radiative cooling.** A spacecraft thruster is radiation cooled: the chamber and nozzle run hot and radiate to space. The chamber material has to survive its own equilibrium temperature, which for hydrazine at 1350 K chamber and a niobium or Haynes alloy chamber means a wall around 1200 K.

**Plume impingement.** The nozzle exit plume expands enormously in vacuum and impinges on whatever is nearby: solar arrays, antennas, radiators, thermal blankets. The impingement produces a force (an unintended torque), a heat load, and a contamination deposit. Plume analysis is a system-level task and it constrains thruster placement more often than anything else.

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Vacuum expansion ratio | 50 to 300 | Diminishing returns above 100 |
| Sea level exit pressure | > 35 % of ambient | Flow separation below |
| Nozzle half angle | 15 degrees conical | Bell not worth it below 100 N |
| Injector stiffness | 20 to 30 % of Pc | Isolates the feed from bed oscillations |
| Blowdown ratio | 4:1 | Thrust range vs ullage volume |
| Bed heater setpoint | 350 to 400 K | Eliminates ignition delay and hard starts |
| Minimum useful pulse | > 3x the ignition delay | Below that the bed does not light reliably |
| Small thruster efficiency | 0.77 combined below 1 N | The boundary layer, not the chemistry |
| Design for soakback | Always | The valve peaks after shutdown |
| Gas generator: run long | X toward 1.0 | Temperature is the driver, not c* |
| Plume clearance | System level analysis | Impingement force, heat and contamination |

---

## Failure modes

**Valve leakage.** A monopropellant thruster valve that leaks dribbles propellant onto a hot bed, which decomposes it and produces uncommanded thrust. On a spacecraft that is a slow, unexplained attitude disturbance and it will exhaust the propellant supply.

**Throat plugging.** A particle in a 0.5 mm throat. Immediate loss of the thruster and a chamber overpressure.

**Hard start.** Covered in [CatalystBeds.md](CatalystBeds.md). Damages the bed and fatigues the chamber.

**Catalyst washout into the throat.** The downstream retainer fails and catalyst plugs or erodes the throat.

**Valve soakback overtemperature.** The seat exceeds its limit after shutdown and leaks thereafter.

**Nozzle flow separation** in a sea level test of a vacuum-optimized nozzle. Side loads that can bend or break the nozzle.

**Plume impingement damage.** Thermal or contamination damage to a nearby surface, or an unintended torque that the control system fights continuously.

**Blowdown thrust below the control authority limit.** At end of life the thrust is a quarter of nominal, and if the control system was not designed for it, the vehicle cannot maintain attitude.

**Freezing.** The 274.7 K hydrazine freezing point applies to the thruster valve and the injector as much as to the tank.

---

## Operations

**Acceptance test every thruster.** Steady-state thrust, Isp, ignition delay, minimum impulse bit and pulse-to-pulse repeatability. Record all of them; they are the baseline against which in-flight performance is judged.

**Track ignition delay.** The single best health indicator for the catalyst bed.

**Verify valve leakage before and after every test.** A leaking valve is both a performance problem and a hazard.

**Preheat before firing** wherever the mission allows.

**Respect the minimum off time.** Firing again before the soakback has dissipated stacks the thermal loads.

**Do not fire into a nozzle with anything in front of it.** Obvious, and it happens.

---

## Worked example

A 100 N hydrazine thruster at 1.5 MPa chamber pressure, expansion ratio 50, in vacuum, using the chemistry from the [CatalystBeds.md](CatalystBeds.md) example (`X = 0.40`, c* = 1311 m/s).

| Quantity | Value |
|---|---|
| Chamber temperature | 1350 K |
| Ideal c* | 1310.0 m/s |
| Delivered c* (0.96 efficiency, large class) | 1257.6 m/s |
| Specific heat ratio | 1.310 |
| Expansion ratio | 50 |
| Exit Mach number | 5.16 |
| Exit pressure | 1.50 kPa |
| Divergence efficiency | 0.983 |
| Ideal Cf | 1.7951 |
| Delivered Cf | 1.7293 |
| **Throat diameter** | **7.006 mm** |
| **Exit diameter** | **49.54 mm** |
| Mass flow | 0.04598 kg/s |
| **Thrust** | **100.0 N** |
| **Vacuum specific impulse** | **221.8 s** |
| Required feed pressure (25 % injector dP) | 1.875 MPa |

**Blowdown at 4:1:**

| Point | Chamber pressure | Thrust | Vacuum Isp |
|---|---|---|---|
| Start | 1.500 MPa | 100.0 N | 221.8 s |
| 25 % | 1.125 MPa | 81.3 N | 221.8 s |
| 50 % | 0.750 MPa | 62.5 N | 221.8 s |
| 75 % | 0.375 MPa | 43.8 N | 221.8 s |
| End | 0.375 MPa | 25.0 N | 221.8 s |

Thrust falls exactly with chamber pressure and Isp is constant, which is the expected behaviour in vacuum. The initial ullage required for a 4:1 isothermal blowdown is 33 percent of the propellant volume.

**Pulse mode with a 373 K heated bed** (1.6 ms ignition delay, 5 ms symmetric valve transients):

| Pulse width | Effective time | Impulse bit | Efficiency |
|---|---|---|---|
| 10 ms | 8.4 ms | 0.84 N-s | 84 % |
| 20 ms | 18.4 ms | 1.84 N-s | 92 % |
| 50 ms | 48.4 ms | 4.84 N-s | 97 % |

With a 293 K cold bed (20.9 ms delay), the 10 ms and 20 ms pulses do not light at all.

Reproduce with:

```python
from CatalystBed import CatalystBed
from MonopropThruster import MonopropThruster

bed = CatalystBed()
bed.setInputs({'massFlow': 0.046, 'chamberPressure': 1.5e6,
               'ammoniaDissociation': 0.40, 'bedTemperature': 373.15})
bed.calculateDecomposition()
bed.sizeBed()
bed.checkColdStart()

thruster = MonopropThruster()
thruster.setInputs({'propellant': 'n2h4', 'thrust': 100.0,
                    'chamberPressure': 1.5e6, 'expansionRatio': 50.0,
                    'catalystBed': bed})
thruster.calculatePerformance()
print(thruster.generateReport())
print(thruster.comparePropellants())
print(thruster.calculateBlowdown(4.0, 5))
print(thruster.calculateMinimumImpulseBit(0.010))
```

---

## Standards

| Standard | Scope |
|---|---|
| MIL-PRF-26536 | Propellant, hydrazine |
| NASA SP-8087 | Liquid rocket engine fluid-cooled combustion chambers |
| NASA SP-8089 | Liquid rocket engine injectors |
| NASA SP-8080 | Liquid rocket pressure regulators, relief valves, check valves, burst disks and explosive valves |
| AIAA S-080 | Space systems metallic pressure vessels, pressurized structures and pressure components |
| JANNAF | Liquid rocket engine performance test and evaluation methodology |
| ECSS-E-ST-35C | Space engineering: propulsion general requirements |
| MIL-STD-1522 | Safe design and operation of pressurized missile and space systems |

---

## Tool interface

The [`MonopropThruster`](../MonopropThruster.py) class covers nozzle sizing, performance, blowdown and pulse mode.

```python
from MonopropThruster import MonopropThruster

thruster = MonopropThruster()
thruster.setInputs({'propellant': 'n2h4', 'thrust': 100.0,
                    'chamberPressure': 1.5e6, 'expansionRatio': 50.0,
                    'ambientPressure': 0.0, 'nozzleHalfAngle': 15.0,
                    'injectorPressureDrop': 0.25})

thruster.calculatePerformance()               # throat, exit, Cf, Isp, feed pressure
thruster.calculateBlowdown(4.0, 11)           # thrust and Isp decay
thruster.calculateMinimumImpulseBit(0.020)    # pulse mode
print(thruster.comparePropellants())          # selection table with density-impulse
print(thruster.generateReport())
```

Supply a `CatalystBed` instance through the `catalystBed` input to size the nozzle from the actual bed chemistry rather than from the nominal propellant table. That is the right way to run a real design, because the table entries are nominal and the bed you built has its own dissociation fraction.

Lookup tables: `MonopropThruster.MONOPROPELLANTS`, `MonopropThruster.NOZZLE_EFFICIENCIES`.

---

## References

1. Sutton, G. P. and Biblarz, O., *Rocket Propulsion Elements*, 9th ed., Wiley, 2016.
2. Schmidt, E. W., *Hydrazine and Its Derivatives*, 2nd ed., Wiley, 2001.
3. Price, T. W. and Evans, D. D., *The Status of Monopropellant Hydrazine Technology*, JPL Technical Report 32-1227, 1968.
4. Aerojet Rocketdyne, *In-Space Propulsion Data Sheets* (MR-103, MR-106, MR-107, MR-111, MR-104).
5. Spores, R. A. et al., "GPIM AF-M315E Propulsion System", AIAA 2013-3849.
6. Anflo, K. and Crowe, B., "In-Space Demonstration of an ADN-based Propulsion System", AIAA 2011-5832.
7. Huzel, D. K. and Huang, D. H., *Modern Engineering for Design of Liquid-Propellant Rocket Engines*, AIAA, 1992.
8. NASA SP-8087, *Liquid Rocket Engine Fluid-Cooled Combustion Chambers*, 1972.
