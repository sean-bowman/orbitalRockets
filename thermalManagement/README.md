# thermalManagement

**Thermal Protection, Thermal Control and Heat Transfer**

> **Status: scaffolded.** The topic coverage below is defined and the documents are planned. Nothing in this domain is written yet. See [../fluidSystems/](../fluidSystems/) for a completed domain.

---

## What This Is

Everything on a launch vehicle either gets too hot or too cold, and thermal management is what keeps each item inside its band. This domain covers thermal protection during ascent and entry, thermal control on orbit, and the heat transfer analysis underneath both.

It shares its physics with the insulation work already in fluid systems, and extends it to ablatives, radiative cooling, heat pipes and radiators.

Reference documentation, a component class library and a tiered test suite, matching the [fluidSystems](../fluidSystems/) template.

## Design Ethos

- Radiation dominates at high temperature and conduction at low. Know which regime you are in before choosing an approach.
- A thermal model is only as good as its boundary conditions, and the boundary conditions are usually the weakest part.
- Transient behaviour matters more than steady state on a launch vehicle. Nothing reaches steady state during ascent.
- Every thermal path is a structural path and vice versa. Isolators are load paths and load paths are heat leaks.
- Soakback is when things fail. The peak temperature is usually after the event, not during it.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/ThermalOverview.md` | Hub: the thermal design process, regimes, document index | planned |
| `docs/ConductionAndResistance.md` | Resistance networks, contact conductance, transient conduction, Biot number | planned |
| `docs/ConvectionAndBoiling.md` | Free and forced convection, boiling regimes, film coefficients | planned |
| `docs/RadiationHeatTransfer.md` | View factors, emissivity, enclosure analysis, radiators | planned |
| `docs/AeroheatingAndTPS.md` | Ascent and entry heating, ablatives, reusable TPS, hot structures | planned |
| `docs/CryogenicInsulation.md` | MLI, foam, vacuum jackets, boil-off, penetrations (extends the fluid systems work) | planned |
| `docs/ThermalControlSystems.md` | Heaters, thermostats, coatings, louvres, active loops | planned |
| `docs/HeatPipesAndTwoPhase.md` | Heat pipes, loop heat pipes, capillary limits, working fluids | planned |
| `docs/RadiatorsAndRejection.md` | Radiator sizing, sink temperatures, deployable radiators | planned |
| `docs/ThermalModelling.md` | Nodal models, correlation to test, model uncertainty, margins | planned |
| `docs/ThermalTesting.md` | Thermal vacuum, thermal cycling, balance tests, instrumentation | planned |
| `docs/StandardsIndex.md` | Annotated index of the governing thermal standards | planned |

## Planned library

| Class | Computes | Status |
|---|---|---|
| `ThermalNetwork` | Multi-node resistance network solve, steady state and transient | planned |
| `AblativeTPS` | Recession rate, char depth, backface temperature, sizing for a heat pulse | planned |
| `Radiator` | Area sizing against a sink temperature, fin efficiency, view factor | planned |
| `HeatPipe` | Capillary, sonic, entrainment and boiling limits, transport capability | planned |
| `ThermalControl` | Heater power sizing, setpoint band, duty cycle, worst hot and cold cases | planned |

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `utils.py`.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [fluidSystems](../fluidSystems/) | Insulation, boil-off and heater sizing are shared physics |
| [aerospaceStructures](../aerospaceStructures/) | Thermal gradients are a load case; isolators are load paths |
| [environmentsAndLoads](../environmentsAndLoads/) | Supplies the thermal environments this domain designs against |
| [aerospaceMaterials](../aerospaceMaterials/) | Temperature-dependent properties and maximum use temperatures |

---

Sean Bowman
