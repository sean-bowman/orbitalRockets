# propulsion

**Liquid Bipropellant Rocket Propulsion**

> **Status: complete.** The hub and all six sub-domains: 20 classes, 50 documents and 404 tests, with a worked example at every level. The hub example is built around the one decision that has three defensible answers which disagree.

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

**Method-of-characteristics nozzle contour generation lives in the NOVA suite**, which produces the isentropic wall contour, the cooling channel geometry that follows it, and CAD-ready output. Reimplementing that here would create a second implementation with nothing enforcing agreement between them.

**The boundary is fidelity, not subject.** The [nozzles](nozzles/) sub-domain computes a Rao parabolic contour at conceptual fidelity, because the loss budget, the cooling area and the mass estimate all need a wall angle and a wetted area before anyone runs a characteristics solution. An earlier version of this section drew the line at geometry altogether, and that was too broad: it left the divergence loss depending on a lookup table of exit angles that was wrong by three and a half degrees and inverted a published finding.

The general rule that came out of it: an argument against duplicating an external tool is not an argument against every calculation in that tool's subject.

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
| [combustionDevices](combustionDevices/) | Injectors, chamber sizing, combustion stability, regenerative cooling | **complete** |
| [turbomachinery](turbomachinery/) | Pumps, turbines, inducers, cavitation, shaft dynamics | **complete** |
| [engineCycles](engineCycles/) | Gas generator, staged combustion, expander, pressure-fed, power balance | **complete** |
| [nozzles](nozzles/) | Performance, area ratio, thrust coefficient, contour, altitude compensation | **complete** |
| [ignitionAndStart](ignitionAndStart/) | Igniters, start and shutdown transients, chill-in, purge | **complete** |
| [propulsionTesting](propulsionTesting/) | Hot fire campaigns, test stands, instrumentation, data reduction | **complete** |

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
