# propulsion

**Liquid Bipropellant Rocket Propulsion**

> **Status: scaffolded.** The topic coverage below is defined and the documents are planned. Nothing in this domain is written yet. See [../fluidSystems/](../fluidSystems/) for a completed domain.

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

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/PropulsionOverview.md` | Hub: the engine as a system, the parameter relationships, document index | planned |
| `docs/PerformanceFundamentals.md` | Isp, c*, Cf, efficiencies, and how they fail independently | planned |
| `docs/PropellantSelection.md` | Bipropellant combinations, density Isp, storability, handling, the real trades | planned |
| `docs/EngineSizing.md` | From thrust and Isp to a chamber, a throat and a mass estimate | planned |
| `docs/ThrottlingAndMixtureRatio.md` | Deep throttle, injector authority, mixture ratio control, propellant utilisation | planned |
| `docs/EngineIntegration.md` | Gimbal, plumbing, heat soak, the interfaces to structure and fluid systems | planned |
| `docs/StandardsIndex.md` | Annotated index of the governing propulsion standards | planned |

## Planned library

| Class | Computes | Status |
|---|---|---|
| `EnginePerformance` | Isp, c*, Cf, efficiencies, altitude performance, throttle behaviour | planned |
| `EngineSizing` | Throat and chamber geometry from thrust, Pc and mixture ratio, plus mass | planned |
| `PropellantCombination` | Property lookup, density Isp, mixture ratio optimum, hazard classification | planned |

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `propulsionUtils.py`.

---

## Sub-domains

| Sub-domain | Covers | Status |
|---|---|---|
| [combustionDevices](combustionDevices/) | Injectors, chamber sizing, combustion stability, regenerative cooling | scaffolded |
| [turbomachinery](turbomachinery/) | Pumps, turbines, inducers, cavitation, shaft dynamics | scaffolded |
| [engineCycles](engineCycles/) | Gas generator, staged combustion, expander, pressure-fed, power balance | scaffolded |
| [nozzles](nozzles/) | Performance, area ratio, thrust coefficient, altitude compensation | scaffolded |
| [ignitionAndStart](ignitionAndStart/) | Igniters, start and shutdown transients, chill-in, purge | scaffolded |
| [propulsionTesting](propulsionTesting/) | Hot fire campaigns, test stands, instrumentation, data reduction | scaffolded |

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
