# thermalManagement

**Thermal Protection, Thermal Control and Heat Transfer**

> **Status: complete.** Five classes, twelve documents and 54 tests, with a worked example that follows an ascent heat pulse from the aeroheating environment through TPS sizing into the soakback that reaches the avionics 950 seconds after the heating stopped.

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

## Documentation

| Document | Covers | Status |
|---|---|---|
| [ThermalOverview.md](docs/ThermalOverview.md) | Hub: the four thermal problems, the transport mechanisms, document index | **written** |
| [ConductionAndResistance.md](docs/ConductionAndResistance.md) | Resistance networks, contact conductance, transient conduction, Biot and Fourier | **written** |
| [ConvectionAndBoiling.md](docs/ConvectionAndBoiling.md) | Correlations and their validity limits, the boiling curve, chilldown | **written** |
| [RadiationHeatTransfer.md](docs/RadiationHeatTransfer.md) | The fourth power, absorptivity against emissivity, degradation, view factors | **written** |
| [AeroheatingAndTPS.md](docs/AeroheatingAndTPS.md) | Sutton-Graves, the ablation energy balance, recession against insulation limits | **written** |
| [CryogenicInsulation.md](docs/CryogenicInsulation.md) | MLI as a radiation problem, penetrations, the ground to flight transition | **written** |
| [ThermalControlSystems.md](docs/ThermalControlSystems.md) | Heaters, thermostats, the hot and cold case as one problem | **written** |
| [HeatPipesAndTwoPhase.md](docs/HeatPipesAndTwoPhase.md) | The four limits, wick selection, ground testability and dead angles | **written** |
| [RadiatorsAndRejection.md](docs/RadiatorsAndRejection.md) | Sizing, sinks, fin efficiency, the fourth power penalty | **written** |
| [ThermalModelling.md](docs/ThermalModelling.md) | Nodal networks, implicit marching, radiative nonlinearity, run length, soakback | **written** |
| [ThermalTesting.md](docs/ThermalTesting.md) | Thermal balance, vacuum and cycling, instrumentation, ground test artefacts | **written** |
| [StandardsIndex.md](docs/StandardsIndex.md) | Annotated index of the governing thermal standards | **written** |

## Library

| Class | Computes | Status |
|---|---|---|
| `ThermalNetwork` | Multi-node resistance network, steady state and transient, soakback and sensitivity | **written** |
| `AblativeTPS` | The surface energy balance, recession, insulation depth, material comparison | **written** |
| `Radiator` | Area against a sink temperature, fin efficiency, sink comparison | **written** |
| `HeatPipe` | Capillary, sonic, entrainment and boiling limits, transport, ground testability | **written** |
| `ThermalControl` | Heater power, setpoint band, duty cycle, thermostat life, hot case check | **written** |

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `utils.py`.

---

## Worked example

`codeInterface.py` follows one heat pulse across three domains, because no single domain owns the failure it produces.

| Link | Owner | Value |
|---|---|---|
| Aeroheating flux | environmentsAndLoads | 0.163 MW/m^2 over 140 s |
| Protection thickness | thermalManagement | 11.48 mm of cork, insulation limited |
| Avionics peak, run stopped when the heating stops | thermalManagement | 307.4 K |
| Avionics peak, run until every node turns over | thermalManagement | 374.8 K at 950 s |
| Avionics limit | fluidSystems | 323.15 K |

The short run passes and the long run fails, on the same model and the same hardware. The only difference is when the analyst stopped integrating.

```bash
python thermalManagement/codeInterface.py
```

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
