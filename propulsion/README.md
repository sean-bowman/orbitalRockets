# propulsion

**Liquid Bipropellant Rocket Propulsion**

> **Status: hub complete, sub-domains scaffolded.** Three engine-level classes, six documents and 61 tests, with a worked example built around the one decision that has three defensible answers which disagree. The six sub-domains below are not written yet.

---

## What This Is

The engine, and everything between the tank outlet and the nozzle exit. This domain is deliberately liquid bipropellant: pump-fed and pressure-fed, storable and cryogenic, from a small upper stage engine to a booster.

Monopropellant hydrazine, catalyst beds and the feed system upstream of the engine are covered in [fluidSystems](../fluidSystems/) and are not repeated here.

The domain is organised as a hub with six sub-domains, in the same way [aerospaceMaterials](../aerospaceMaterials/) is, because propulsion is too large to sit in one flat document set. The documents at this level cover the engine as a system: what the cycle choice buys, how the performance parameters relate, and what sizes an engine. The sub-domains cover the hardware.

Reference documentation, a component class library and a tiered test suite, matching the [fluidSystems](../fluidSystems/) template.

## Design Ethos

- Performance is `F = Cf c* mdot`, and the two coefficients fail independently. Knowing which one a problem lives in is most of the diagnosis.
- The cycle is chosen before anything else and it constrains everything after it.
- Combustion instability is not a margin, it is a threshold. A stable engine and an unstable one differ by a design detail, not by a factor.
- Cooling is the constraint that sizes chambers. Almost every chamber is as large as it is because of heat flux, not because of residence time.
- Real propellant properties, always. Ideal gas assumptions in a chamber are wrong in the direction that matters.

## Where this stops

**Nozzle contour generation lives in the NOVA suite**, which generates method-of-characteristics contours and cooling channel geometry and exports CAD-ready output. This domain covers nozzle performance, area ratio selection, thrust coefficient and the altitude compensation trades: the decisions, not the geometry generation. The [nozzles](nozzles/) sub-domain says so explicitly and points there.

That division is deliberate. Reimplementing a contour generator here would create a second implementation with nothing enforcing agreement between them.

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [PropulsionOverview.md](docs/PropulsionOverview.md) | Hub: the Cf and c* factorisation, the decision order, what sizes an engine | **written** |
| [PerformanceFundamentals.md](docs/PerformanceFundamentals.md) | Isp, c*, Cf, the two efficiencies, altitude behaviour, flow separation | **written** |
| [PropellantSelection.md](docs/PropellantSelection.md) | Density impulse against specific impulse, the volume split, storability | **written** |
| [EngineSizing.md](docs/EngineSizing.md) | Thrust to throat to chamber to mass, and what governs each step | **written** |
| [ThrottlingAndMixtureRatio.md](docs/ThrottlingAndMixtureRatio.md) | Injector authority, the separation floor, propellant utilisation | **written** |
| [EngineIntegration.md](docs/EngineIntegration.md) | The interfaces either side, the fuel-as-coolant coupling, gimbal, heat soak | **written** |
| [StandardsIndex.md](docs/StandardsIndex.md) | Annotated index of the governing propulsion standards | **written** |
| [ValidationReferences.md](docs/ValidationReferences.md) | The external sources the tools are checked against, and what is not checked | **written** |

## Library

| Class | Computes | Status |
|---|---|---|
| `EnginePerformance` | c*, Cf, Isp, the two efficiencies separately, altitude sweep, expansion trade | **written** |
| `EngineSizing` | Throat and chamber geometry, the cooling cross-check, nozzle length, mass | **written** |
| `PropellantCombination` | Bulk density, density impulse, the volume split, the combination trade | **written** |

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `propulsionUtils.py`.

---

## Sub-domains

| Sub-domain | Covers | Status |
|---|---|---|
| [combustionDevices](combustionDevices/) | Injectors, chamber sizing, combustion stability, regenerative cooling | scaffolded |
| [turbomachinery](turbomachinery/) | Pumps, turbines, inducers, cavitation, shaft dynamics | scaffolded |
| [engineCycles](engineCycles/) | Gas generator, staged combustion, expander, pressure-fed, power balance | scaffolded |
| [nozzles](nozzles/) | Performance, area ratio, thrust coefficient, altitude compensation | scaffolded |
| [ignitionAndStart](ignitionAndStart/) | Igniters, start and shutdown transients, chill-in, purge | **complete** |
| [propulsionTesting](propulsionTesting/) | Hot fire campaigns, test stands, instrumentation, data reduction | scaffolded |

---

## Worked example

`codeInterface.py` sizes a first stage booster, and is built around the area ratio decision because three reasonable questions give three different answers.

| Question asked | Area ratio | Burn-averaged Isp | Flyable |
|---|---|---|---|
| What maximises thrust at liftoff | 10.75 | 296.2 s | Yes |
| What maximises impulse over the burn | 25.75 | 302.3 s | No, separates on the pad |
| What the flow will tolerate | 21.42 | 302.0 s | On the limit |
| **The design point, with margin** | **20.35** | **301.8 s** | **Yes** |

The intuitive answer is not a bad answer. It is the right answer to the wrong question: it genuinely does maximise sea level impulse, and it costs 61 m/s of stage delta-V. The true optimum is unreachable. The constraint that rules it out sits half a second away from it.

```bash
python propulsion/codeInterface.py
```

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [fluidSystems](../fluidSystems/) | Everything upstream of the engine inlet, and the monopropellant case |
| [aerospaceStructures](../aerospaceStructures/) | Thrust structure, gimbal loads, chamber as a pressure vessel |
| [aerospaceMaterials](../aerospaceMaterials/) | GRCop chamber liners, superalloy turbine hardware, additive manufacture |
| [thermalManagement](../thermalManagement/) | Regenerative cooling is a heat exchanger, and the nozzle radiates |
| [environmentsAndLoads](../environmentsAndLoads/) | The engine is the dominant source of vibration and acoustics |
| [vehicleArchitecture](../vehicleArchitecture/) | Engine performance and mass are the inputs to vehicle sizing |

---

Sean Bowman
