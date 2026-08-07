[Home](../../README.md) > Fluid Systems Overview

# Aerospace Fluid Systems Overview

The hub document. It maps the subject, states the conventions the whole library uses, walks a feed system end to end, and indexes everything else.

## Contents

- [What a fluid system is](#what-a-fluid-system-is)
- [Conventions](#conventions)
- [Feed system architecture](#feed-system-architecture)
- [The pressure budget](#the-pressure-budget)
- [The design sequence](#the-design-sequence)
- [Cross-cutting concerns](#cross-cutting-concerns)
- [The ten things that break fluid systems](#the-ten-things-that-break-fluid-systems)
- [Document index](#document-index)
- [Class index](#class-index)

---

## What a fluid system is

A propulsion fluid system moves propellant and pressurant from where they are stored to where they are burned, at a controlled rate, without leaking, igniting, freezing, plugging or bursting.

Its components divide into five functional groups:

| Group | Components | Job |
|---|---|---|
| **Containment** | Tanks, lines, fittings, seals, welds | Hold the fluid in |
| **Flow control** | Valves, orifices, venturis, regulators, check valves | Set the flow rate and direction |
| **Protection** | Relief valves, burst discs, filters | Limit pressure and remove particulate |
| **Conditioning** | Insulation, heaters, heat exchangers | Keep the fluid in its intended state |
| **Instrumentation** | Pressure, temperature, flow, level | Know what is happening |

Every one of those is a leak path, a mass increment and a failure mode. The best fluid system is the one with the fewest components that meets its requirements.

---

## Conventions

**Everything internal to this library is mass-base SI.**

| Quantity | Unit |
|---|---|
| Length, diameter, thickness | m |
| Area | m^2 |
| Volume | m^3 |
| Mass | kg |
| Mass flow | kg/s |
| Pressure | Pa, **absolute** unless stated as gauge |
| Temperature | K |
| Density | kg/m^3 |
| Dynamic viscosity | Pa-s |
| Thermal conductivity | W/m-K |
| Specific heat | J/kg-K |
| Force | N |
| Torque | N-m |
| Leak rate | scc/s (0 degC, 1 atm) internally; every unit available through `leakRateConvert` |

**Imperial appears only at boundaries**, through named conversion constants in [`utils`](../utils.py) (`PA_PER_PSIA`, `M_PER_IN`, `KG_PER_LBM`, `N_PER_LBF`, `NM_PER_INLBF`) or through explicit converter functions.

**Friction factors are Darcy**, four times the Fanning factor. Every call site says so.

**Fluid properties come from `fluidProps`**, which dispatches to a correlation table for hydrazine, then REFPROP if installed, then CoolProp. Same signature in every case:

```python
rho, mu, k, cp = fluidProps('Oxygen', 'TP', 'D VIS TCX Cp', 90.2, 4.0e5)
```

**Two "standard" states are in circulation and they are not the same.** Leak rates and scc/s use the vacuum industry convention (0 degC, 1 atm). SCFM uses 60 degF. Both are carried explicitly so neither is assumed by accident.

---

## Feed system architecture

A generic pressure-fed monopropellant system, in flow order:

```
  [pressurant bottle]
        |
   isolation valve
        |
    REGULATOR  ------- relief valve ------- burst disc
        |
    check valve  (series redundant if hypergolic)
        |
  [propellant tank]  <- PMD, level sensing, relief
        |
      FILTER
        |
       LINE  (bends, fittings, flex where needed)
        |
   isolation valve
        |
   trim ORIFICE  or  CAVITATING VENTURI
        |
   thruster VALVE
        |
     INJECTOR
        |
   CATALYST BED
        |
      NOZZLE
```

A blowdown system deletes the bottle, the regulator, the isolation valve and the check valve, and charges the propellant tank directly. See [PressurizationAndBlowdown.md](PressurizationAndBlowdown.md).

A bipropellant system runs two of the propellant branches from a common pressurant manifold, which is where series-redundant check valves become mandatory. See [FlowControlDevices.md](FlowControlDevices.md).

A cryogenic system adds chilldown provisions, recirculation on any vertical downcomer, insulation, and vent paths at every high point. See [CryogenicSystems.md](CryogenicSystems.md).

---

## The pressure budget

The pressure budget is the spine of the design and it is worked backwards from the chamber:

```
tank pressure  =  chamber pressure
                + injector dP           (15 to 30 % of Pc)
                + catalyst bed dP       (10 to 25 % of Pc, monoprop only)
                + valve dP
                + orifice or venturi dP
                + line friction and minor losses
                + filter dP
                + elevation head
                - (nothing, ever, adds pressure)
```

**Then everything upstream of the tank follows:** the regulator outlet band maximum sets the tank MEOP, the relief valve sits above that, the burst disc above that, and the proof pressure above that. See [QualificationAndTesting.md](QualificationAndTesting.md).

**Why it matters so much:**

```
line diameter -> pressure drop -> tank pressure -> tank wall thickness -> vehicle mass
```

Every kPa saved in the feed system is a kPa off the tank pressure, and tank mass scales with pressure times volume. Undersizing a feed line by one tube size can cost more mass in tank wall than the entire valve complement weighs.

**Carry honest minor losses.** A vehicle run with a dozen fittings, four bends and a quick disconnect can carry more loss than the straight tube it connects. The single most common pressure budget error is neglecting them.

---

## The design sequence

1. **Requirements.** Thrust or flow rate, duty cycle, mission duration, environment, mass budget, envelope, hazard classification.
2. **Architecture.** Regulated or blowdown. Monopropellant or bipropellant. Pressure fed or pump fed. Number of thrusters and their arrangement. This is where the biggest mass decisions are made.
3. **Propellant and material selection.** Compatibility screening comes first because it eliminates options rather than optimizing among them. See [MaterialsCompatibility.md](MaterialsCompatibility.md).
4. **Chamber conditions.** Chamber pressure, expansion ratio, and for a monopropellant the catalyst bed sizing. See [CatalystBeds.md](CatalystBeds.md) and [MonopropellantThrusters.md](MonopropellantThrusters.md).
5. **Pressure budget.** Allocate the drop across injector, bed, valves, orifices, lines and filter, working back to a required tank pressure.
6. **Component sizing.** Lines, orifices, valves, filters, each against its allocation and its velocity limit.
7. **Pressurization.** Pressurant mass, bottle or ullage sizing. See [PressurizationAndBlowdown.md](PressurizationAndBlowdown.md).
8. **Transients.** Water hammer on every valve closure, priming surge on every opening, adiabatic compression on every oxygen valve. See [WaterHammer.md](WaterHammer.md).
9. **Thermal.** Insulation, heaters, boil-off, soakback. See [Insulation.md](Insulation.md).
10. **Structural.** Wall thickness, supports, natural frequency, thermal growth accommodation.
11. **Leak budget.** Derived from hazard or mission criteria, allocated across joints, and used to select joint types. See [Leaks.md](Leaks.md).
12. **Qualification plan.** Written at the start, not at the end.

**Steps 5 through 8 iterate.** Sizing a line changes the pressure budget, which changes the tank pressure, which changes the pressurant mass, which changes the vehicle mass, which sometimes changes the thrust requirement.

---

## Cross-cutting concerns

Five things touch every component and cannot be delegated to a subsystem:

**Compatibility.** Every wetted material against every fluid it can see, including during off-nominal conditions. See [MaterialsCompatibility.md](MaterialsCompatibility.md).

**Cleanliness.** Specified at the system level, achieved at the part level, maintained through assembly. The system is only as clean as the dirtiest thing that entered it. See [CleanlinessAndContamination.md](CleanlinessAndContamination.md).

**Leak rate.** Allocated across every joint. Twenty joints at 1e-6 scc/s is a 2e-5 scc/s system. See [Leaks.md](Leaks.md).

**Trapped volumes.** Every volume that can be isolated must have a relief path. This is the single most common serious design error in fluid systems, and it is the one that bursts hardware.

**Operability.** Can it be purged, drained, safed, leak checked and worked on? See [OperationsAndPurge.md](OperationsAndPurge.md).

---

## The ten things that break fluid systems

In rough order of how often they actually cause problems:

1. **Contamination.** A single particle in an orifice or on a valve seat. See [CleanlinessAndContamination.md](CleanlinessAndContamination.md).
2. **The wrong seal material.** NBR in hydrazine, Viton at cryogenic temperature, an elastomer below its glass transition. See [Seals.md](Seals.md).
3. **Water hammer.** A valve closing faster than the pipe period. See [WaterHammer.md](WaterHammer.md).
4. **A trapped volume with no relief path.** Especially with a cryogen or with hydrazine.
5. **Undersized lines discovered late.** The pressure budget does not close and the fix is expensive. See [PipeRoutingAndSizing.md](PipeRoutingAndSizing.md).
6. **Vibration fatigue at fittings.** The line fails where it is stiffest, at the joint.
7. **Leak requirements that cannot be measured.** A 1e-12 scc/s requirement verified by pressure decay. See [Leaks.md](Leaks.md).
8. **The choking limit ignored.** A valve or orifice sized on the full differential when it is choked. See [Valves.md](Valves.md).
9. **Material incompatibility.** Titanium in oxygen, copper in hydrazine, high strength steel in hydrogen. See [MaterialsCompatibility.md](MaterialsCompatibility.md).
10. **A pressure set point ladder that does not close.** The relief lifts during normal operation, or the burst disc goes first. See [FlowControlDevices.md](FlowControlDevices.md).

Nine of the ten are design decisions rather than manufacturing defects, and all ten are checkable before anything is built.

---

## Document index

### Components

| Document | Covers |
|---|---|
| [Orifices](Orifices.md) | Discharge coefficients, choked and cavitating flow, ISO 5167 metering, drill selection |
| [Pipe Routing and Sizing](PipeRoutingAndSizing.md) | Darcy-Weisbach, minor losses, velocity limits, ASME B31.3 wall thickness, routing, supports |
| [Valves](Valves.md) | Cv sizing, choked flow, cavitation, characteristics and authority, actuation, leakage classes |
| [Fittings and Connectors](FittingsAndConnectors.md) | Fitting families, sealing mechanisms, torque and preload, galling |
| [Seals](Seals.md) | Gland sizing, squeeze and fill, extrusion, materials, glass transition, permeation |
| [Leaks](Leaks.md) | Units, flow regimes, equivalent hole size, gas scaling, detection methods, test design |
| [Welds](Welds.md) | Joint types, efficiency and HAZ derating, ferrite control, purge, inspection |
| [Insulation](Insulation.md) | Resistance networks, MLI, boil-off, condensation and liquid air |
| [Water Hammer and Hazards](WaterHammer.md) | Joukowsky, wave speed, column separation, priming, adiabatic compression |
| [Flow Control Devices](FlowControlDevices.md) | Regulators, relief valves, burst discs, check valves, filters, cavitating venturis |

### Monopropellant systems

| Document | Covers |
|---|---|
| [Hydrazine](Hydrazine.md) | Properties, chemistry, purity, compatibility, hazards, handling, system implications |
| [Catalyst Beds](CatalystBeds.md) | Shell 405, decomposition chemistry, bed loading and length, Ergun, starting, life |
| [Monopropellant Thrusters](MonopropellantThrusters.md) | Performance, nozzle sizing, small thruster efficiency, blowdown, pulse mode, gas generators |
| [Passivation](Passivation.md) | Chemical passivation, propellant passivation, spacecraft passivation |

### Systems and operations

| Document | Covers |
|---|---|
| [Pressurization and Blowdown](PressurizationAndBlowdown.md) | Regulated and blowdown sizing, pressurant selection, real gas, ullage collapse, PMDs |
| [Cryogenic Systems](CryogenicSystems.md) | Chilldown, two-phase flow, geysering, contraction, NPSH, materials, stratification |
| [Materials Compatibility](MaterialsCompatibility.md) | The compatibility matrix, oxygen, hydrogen, hydrazine, N2O4, peroxide, lubricants |
| [Cleanliness and Contamination](CleanlinessAndContamination.md) | Cleanliness levels, cleaning processes, oxygen cleaning, verification, design for cleanability |
| [Instrumentation](Instrumentation.md) | Pressure, temperature, flow, level, installation effects, sample rates |
| [Operations and Purge](OperationsAndPurge.md) | Purge methods and verification, loading, safing, lockout, GSE, sequences |
| [Qualification and Testing](QualificationAndTesting.md) | MEOP, factors of safety, proof and burst, environmental, life, acceptance |
| [Standards Index](StandardsIndex.md) | Annotated index of every standard referenced |

---

## Class index

| Class | File | Primary use |
|---|---|---|
| `Orifice` | [Orifice.py](../Orifice.py) | Size a hole, or find the flow through one |
| `CavitatingVenturi` | [CavitatingVenturi.py](../CavitatingVenturi.py) | Choked liquid flow control |
| `Valve` | [Valve.py](../Valve.py) | Cv sizing, choking, cavitation, characteristics, actuation |
| `Line` | [Line.py](../Line.py) | Pressure drop, diameter sizing, wall thickness, mass |
| `Fitting` | [Fitting.py](../Fitting.py) | Joint selection, loss, torque, compatibility |
| `Seal` | [Seal.py](../Seal.py) | Gland sizing, extrusion, compatibility, permeation |
| `LeakPath` | [LeakPath.py](../LeakPath.py) | Leak units, regimes, detection, test feasibility, allowables |
| `Weld` | [Weld.py](../Weld.py) | Derating, allowable pressure, ferrite, inspection level |
| `Insulation` | [Insulation.py](../Insulation.py) | Heat leak, thickness sizing, boil-off, condensation |
| `WaterHammer` | [WaterHammer.py](../WaterHammer.py) | Surge, closure time, column separation, adiabatic compression |
| `CatalystBed` | [CatalystBed.py](../CatalystBed.py) | Decomposition chemistry, bed sizing, Ergun, cold start |
| `MonopropThruster` | [MonopropThruster.py](../MonopropThruster.py) | Nozzle sizing, Isp, blowdown, pulse mode |
| `Pressurization` | [Pressurization.py](../Pressurization.py) | Pressurant mass, bottle and ullage sizing |
| `Regulator` | [Regulator.py](../Regulator.py) | Regulator band, relief sizing, burst disc, pressure ladder |
| `CheckValve` | [CheckValve.py](../CheckValve.py) | Cracking pressure, chatter, reverse leakage |
| `Filter` | [Filter.py](../Filter.py) | Rating selection, element sizing, life |

**Shared infrastructure** is in [utils.py](../utils.py): `fluidProps` and the property backends, `frictionFactor`, `leakRateConvert`, `materialProperties`, `roughnessTable`, `b31_3WallThickness`, `hoopStressCalculator`, `chokedMassFlux`, `criticalPressureRatio`, `isentropicValues`, `secantSolve`, `applyInputs`, `formatReportTable`, and the `FluidSystemError` exception hierarchy.

**Every class follows the same pattern:**

```python
component = ClassName()
component.setInputs({...})        # flat configuration dictionary
component.calculateSomething()    # or sizeSomething()
print(component.generateReport()) # formatted table plus advisory notes
```

and every class raises a typed error (`InvalidInputError`, `PressureDropError`, `ChokedFlowError`, `CompatibilityError`, `ConvergenceFailureError`, `NumericalInstabilityError`) with enough context in the message to diagnose the problem without reading the source.
