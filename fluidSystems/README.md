# fluidSystems

**Aerospace Fluid System Design and Analysis Library**

A reference and a toolset for aerospace fluid system engineering: comprehensive technical documentation on the design, analysis and operation of fluid system hardware, paired with a Python library of one class per major component.

---

## What This Is

Two things that are meant to be used together.

**A technical reference.** Twenty-three documents covering the physics, the design procedures, the rules of thumb, the failure modes and the governing standards for every major fluid system topic: valves, lines, orifices, fittings, seals, leaks, welds, insulation, water hammer, hydrazine, catalyst beds, monopropellant thrusters, passivation, pressurization, cryogenics, materials compatibility, cleanliness, instrumentation, operations and qualification.

**A working toolset.** Sixteen component classes that size hardware and analyze it: a small custom GFSSP for design decisions and light single-component analysis. Every class pulls real fluid properties, applies the correlations documented alongside it, and reports not just numbers but the findings that matter -- a leak requirement that no joint can meet, a check valve that will chatter, a pressure set point ladder that does not close.

Full integrated system network solving is out of scope. The components are analyzed individually and chained by hand, which is what a pressure budget actually is.

## Design Ethos

- All internal quantities are in mass-base SI. Imperial appears only at boundaries, through named conversion constants.
- Fluid properties come from real equations of state: REFPROP where installed, CoolProp otherwise, and a correlation table for hydrazine, which neither backend models.
- One class per component, one file per class, one consistent interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`.
- The documentation and the code are cross-linked in both directions. Every class docstring names its theory document; every document has a tool interface section.
- Errors are typed and carry context. A failed calculation says what went wrong and what the physical limit was, not just that it failed.
- The tools report findings, not only results. A calculation that produces a number and a warning is more useful than one that produces a number.

---

## Contents

- [Installation](#installation)
- [Quickstart](#quickstart)
- [Worked example: 100 N hydrazine monopropellant system](#worked-example-100-n-hydrazine-monopropellant-system)
- [Component library](#component-library)
- [Documentation](#documentation)
- [Testing](#testing)
- [Repository structure](#repository-structure)

---

## Installation

Targets **Python 3.10** on Windows.

```bash
pip install -r dependencies.txt
```

Fluid properties dispatch to REFPROP first and fall back to CoolProp. **CoolProp alone is sufficient** to run everything in this library; REFPROP adds accuracy and mixture support. Hydrazine is served by a built-in correlation table either way, because no general equation of state for it exists in either backend.

## Quickstart

```python
import sys
sys.path.insert(0, 'fluidSystemsLibrary')

from Orifice import Orifice

element = Orifice()
element.setInputs({'fluid': 'N2H4', 'upstreamPressure': 2.20e6,
                   'downstreamPressure': 1.90e6, 'upstreamTemperature': 293.15,
                   'massFlow': 0.045, 'orificeType': 'square'})
element.sizeDiameter()
print(element.generateReport())
```

Every class follows the same pattern:

```python
component = ClassName()
component.setInputs({...})         # flat configuration dictionary
component.calculateSomething()     # or sizeSomething()
print(component.generateReport())  # formatted table plus advisory notes
```

`codeInterface.py` is a ready-made driver that runs a complete feed system end to end:

```bash
python codeInterface.py
```

---

## Worked example: 100 N hydrazine monopropellant system

`codeInterface.py` sizes a GHe-pressurized hydrazine monopropellant feed system from a 100 N thrust requirement, walking the chain in reverse flow order because that is how a pressure budget is built: start at the chamber, add every loss going upstream, and arrive at the required tank pressure.

```
NOZZLE <- CATALYST BED <- INJECTOR <- THRUSTER VALVE <- TRIM ORIFICE <-
FEED LINE <- FILTER <- PROPELLANT TANK <- CHECK VALVE <- REGULATOR <- He BOTTLE
```

### Pressure budget

| Station (upstream order) | P [MPa] | dP [kPa] | Note |
|---|---|---|---|
| Nozzle throat (chamber) | 1.5000 | | 100.0 N, Isp 221.9 s |
| Catalyst bed inlet | 1.7637 | +263.7 | bed dP 17.6 % of Pc |
| Injector inlet | 2.1387 | +375.0 | 8 x 0.575 mm, Cd 0.804 |
| Thruster valve inlet | 2.1687 | +30.0 | Cv 0.348 |
| Trim orifice inlet | 2.2187 | +50.0 | 2.686 mm bore |
| Feed line inlet | 2.2360 | +17.3 | 0.375 in OD x 0.065 in wall |
| Filter inlet (tank outlet) | 2.2360 | +0.01 | 40 micron absolute, beta 1000 |
| Propellant tank | 2.2360 | | required regulated pressure |
| Regulator inlet (bottle) | 30.0000 | | initial bottle pressure |

### System summary

| Quantity | Value |
|---|---|
| Thrust | 100.00 N (22.48 lbf) |
| Vacuum specific impulse | 221.87 s |
| Propellant mass flow | 0.04596 kg/s |
| Chamber temperature | 1347 K |
| Required tank pressure | 2.2360 MPa |
| Total feed system dP | 736 kPa (49.1 % of Pc) |
| Peak pressure (surge) | 2.4249 MPa |
| Feed line | 0.375 in OD x 0.065 in wall, 0.817 kg |
| Catalyst mass | 179.0 g Shell 405 |
| Pressurant (regulated) | 0.1394 kg He in a 3.23 L bottle at 30 MPa |
| Filter element | 40 micron, 45.6 cm^2 envelope |
| Line heater power | 5.00 W |
| System leak allowable | 1.04e-05 scc/s He |

### The findings it surfaces

The numbers are not the interesting part. These are:

- **The two AN flare unions alone contribute 2.0e-4 scc/s of helium, which exceeds the 1.04e-5 scc/s system allowable derived from the hydrazine exposure limit by a factor of 20.** The joints have to be VCR or welded, and the tool says so rather than leaving it to be discovered later.
- **The pressurant check valve will chatter.** At its minimum flow it sits at 40 percent of the flow needed to hold the poppet on its stop.
- **A pressure decay leak test cannot verify this system.** It is temperature-limited at 2.1e-2 scc/s, three orders of magnitude above the requirement.
- **The catalyst bed pressure drop is 17.6 percent of chamber pressure**, which is in family, but the granule size had to be coarsened to 14-18 mesh to get there.
- **The 20 ms valve closure is eight times the pipe period**, so the surge is 0.19 MPa rather than the 3.05 MPa Joukowsky value. Hydrazine has the worst water hammer characteristics of any common propellant at 2.07 MPa per m/s.

---

## Component library

| Class | File | Primary use |
|---|---|---|
| `Orifice` | [Orifice.py](fluidSystemsLibrary/Orifice.py) | Size a hole, or find the flow through one. Incompressible, choked, cavitating, ISO 5167 |
| `CavitatingVenturi` | [CavitatingVenturi.py](fluidSystemsLibrary/CavitatingVenturi.py) | Choked liquid flow control and unchoke margin |
| `Valve` | [Valve.py](fluidSystemsLibrary/Valve.py) | Cv sizing, choking, cavitation, characteristics and authority, actuation |
| `Line` | [Line.py](fluidSystemsLibrary/Line.py) | Pressure drop, diameter sizing, B31.3 wall thickness, mass |
| `Fitting` | [Fitting.py](fluidSystemsLibrary/Fitting.py) | Joint selection, loss, torque, compatibility screening |
| `Seal` | [Seal.py](fluidSystemsLibrary/Seal.py) | Gland sizing, extrusion, glass transition, permeation |
| `LeakPath` | [LeakPath.py](fluidSystemsLibrary/LeakPath.py) | Leak units, flow regimes, detection, test feasibility, hazard allowables |
| `Weld` | [Weld.py](fluidSystemsLibrary/Weld.py) | Joint efficiency and HAZ derating, ferrite prediction, inspection level |
| `Insulation` | [Insulation.py](fluidSystemsLibrary/Insulation.py) | Heat leak, thickness sizing, boil-off, condensation and liquid air |
| `WaterHammer` | [WaterHammer.py](fluidSystemsLibrary/WaterHammer.py) | Surge, closure time, column separation, adiabatic compression |
| `CatalystBed` | [CatalystBed.py](fluidSystemsLibrary/CatalystBed.py) | Decomposition chemistry, bed sizing, Ergun, cold start |
| `MonopropThruster` | [MonopropThruster.py](fluidSystemsLibrary/MonopropThruster.py) | Nozzle sizing, Isp, blowdown, pulse mode |
| `Pressurization` | [Pressurization.py](fluidSystemsLibrary/Pressurization.py) | Pressurant mass, bottle and ullage sizing, real gas |
| `Regulator` | [Regulator.py](fluidSystemsLibrary/Regulator.py) | Regulator band, relief sizing, burst disc, pressure set point ladder |
| `CheckValve` | [CheckValve.py](fluidSystemsLibrary/CheckValve.py) | Cracking pressure, chatter margin, reverse leakage |
| `Filter` | [Filter.py](fluidSystemsLibrary/Filter.py) | Rating selection, element sizing on life, clean dP |

Shared infrastructure is in [utils.py](fluidSystemsLibrary/utils.py): the `fluidProps` property stack, `frictionFactor`, `leakRateConvert`, `materialProperties`, `roughnessTable`, `b31_3WallThickness`, `chokedMassFlux`, `secantSolve`, `formatReportTable`, and the `FluidSystemError` exception hierarchy.

---

## Documentation

Start at [FluidSystemsOverview.md](fluidSystemsLibrary/docs/FluidSystemsOverview.md), which maps the subject, states the conventions and indexes everything.

### Components

| Document | Covers |
|---|---|
| [Orifices](fluidSystemsLibrary/docs/Orifices.md) | Discharge coefficients, choked and cavitating flow, ISO 5167, drill selection |
| [Pipe Routing and Sizing](fluidSystemsLibrary/docs/PipeRoutingAndSizing.md) | Darcy-Weisbach, minor losses, velocity limits, B31.3, routing, supports |
| [Valves](fluidSystemsLibrary/docs/Valves.md) | Cv sizing, choking, cavitation, characteristics, actuation, leakage classes |
| [Fittings and Connectors](fluidSystemsLibrary/docs/FittingsAndConnectors.md) | Fitting families, sealing mechanisms, torque and preload, galling |
| [Seals](fluidSystemsLibrary/docs/Seals.md) | Gland sizing, squeeze and fill, extrusion, materials, permeation |
| [Leaks](fluidSystemsLibrary/docs/Leaks.md) | Units, regimes, equivalent hole size, gas scaling, detection, test design |
| [Welds](fluidSystemsLibrary/docs/Welds.md) | Joint types, derating, ferrite control, purge, inspection |
| [Insulation](fluidSystemsLibrary/docs/Insulation.md) | Resistance networks, MLI, boil-off, condensation and liquid air |
| [Water Hammer and Hazards](fluidSystemsLibrary/docs/WaterHammer.md) | Joukowsky, wave speed, column separation, adiabatic compression |
| [Flow Control Devices](fluidSystemsLibrary/docs/FlowControlDevices.md) | Regulators, relief, burst discs, check valves, filters, venturis |

### Monopropellant systems

| Document | Covers |
|---|---|
| [Hydrazine](fluidSystemsLibrary/docs/Hydrazine.md) | Properties, chemistry, purity, compatibility, hazards, handling |
| [Catalyst Beds](fluidSystemsLibrary/docs/CatalystBeds.md) | Shell 405, chemistry, bed loading and length, Ergun, starting, life |
| [Monopropellant Thrusters](fluidSystemsLibrary/docs/MonopropellantThrusters.md) | Performance, nozzle sizing, blowdown, pulse mode, gas generators |
| [Passivation](fluidSystemsLibrary/docs/Passivation.md) | Chemical, propellant and spacecraft passivation |

### Systems and operations

| Document | Covers |
|---|---|
| [Pressurization and Blowdown](fluidSystemsLibrary/docs/PressurizationAndBlowdown.md) | Regulated and blowdown sizing, pressurants, real gas, ullage collapse |
| [Cryogenic Systems](fluidSystemsLibrary/docs/CryogenicSystems.md) | Chilldown, two-phase flow, geysering, contraction, NPSH, materials |
| [Materials Compatibility](fluidSystemsLibrary/docs/MaterialsCompatibility.md) | The compatibility matrix, oxygen, hydrogen, hydrazine, N2O4, peroxide |
| [Cleanliness and Contamination](fluidSystemsLibrary/docs/CleanlinessAndContamination.md) | Cleanliness levels, cleaning, oxygen cleaning, verification |
| [Instrumentation](fluidSystemsLibrary/docs/Instrumentation.md) | Pressure, temperature, flow, level, installation effects, sample rates |
| [Operations and Purge](fluidSystemsLibrary/docs/OperationsAndPurge.md) | Purge methods and verification, loading, safing, lockout, GSE |
| [Qualification and Testing](fluidSystemsLibrary/docs/QualificationAndTesting.md) | MEOP, factors of safety, proof and burst, environmental, life |
| [Standards Index](fluidSystemsLibrary/docs/StandardsIndex.md) | Annotated index of every standard referenced |

---

## Testing

```bash
python -m pytest tests/ -v
```

The tests are organized in three tiers, following the pattern used in NOVA:

- **Tier 1** covers pure constants and unit conversions with no property backend, so it runs anywhere and catches unit errors immediately.
- **Tier 2** validates against published references: Crane TP-410 for line pressure drop, ISO 5167 for orifice plate discharge coefficients, the definition of Cv for valve sizing, textbook Joukowsky surge values, AS568 gland tables for seal geometry, and Aerojet Rocketdyne catalog data for hydrazine thruster performance.
- **Tier 3** covers self-consistency identities: forward and inverse solves must round-trip, leak rate conversions must round-trip through every unit, and a valve Cv converted to a loss coefficient and back must reproduce the original pressure drop.

Every test carries a docstring explaining what defect it exists to catch, and assertion messages name the likely root cause rather than just reporting the mismatch.

---

## Repository structure

```
fluidSystems/
├── README.md
├── codeInterface.py               top-level driver and worked example
├── dependencies.txt
├── pytest.ini
├── tests/                         tiered test suite
└── fluidSystemsLibrary/
    ├── __init__.py
    ├── utils.py                   property stack, conversions, correlations, errors
    ├── *.py                       one class per component, sixteen of them
    ├── assets/                    JSON configuration for the worked example
    └── docs/                      twenty-three reference documents
```

---

Sean Bowman
