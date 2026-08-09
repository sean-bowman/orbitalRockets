# environmentsAndLoads

**Launch and Flight Environments, Loads Definition**

> **Status: complete.** Five classes, thirteen documents and 60 tests, with a worked example that derives a component environment from flight data and compares it against the generic specification the same hardware is currently qualified to.

---

## What This Is

Every qualification level, every factor of safety and every design margin in this repository traces back to an environment definition. This domain covers where those environments come from: the physical sources, how they are measured and characterized, how they are turned into specifications, and how much margin gets added at each step.

It is upstream of nearly everything else. Get the environment wrong and every downstream qualification is answering the wrong question.

Reference documentation, a component class library and a tiered test suite, matching the [fluidSystems](../fluidSystems/) template.

## Design Ethos

- An environment specification is a statistical statement, not a measurement. Know the percentile and the confidence.
- Margin accumulates. Flight to acceptance to qualification is two additions, and each one has a reason.
- The governing environment is rarely the loudest one. It is the one the hardware is least tolerant of.
- Test levels are derived, not chosen. Every dB should be traceable to a source.
- Enveloping is convenient and expensive. Know what the envelope cost you.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| [EnvironmentsOverview.md](docs/EnvironmentsOverview.md) | Hub: the environment sources, the derivation chain, document index | **written** |
| [RandomVibration.md](docs/RandomVibration.md) | PSD, Grms, sources, transmissibility, derivation of test levels, Miner scaling | **written** |
| [AcousticEnvironment.md](docs/AcousticEnvironment.md) | Liftoff and aerodynamic acoustics, SPL, vibroacoustic response, reverberant test | **written** |
| [ShockEnvironment.md](docs/ShockEnvironment.md) | Pyroshock, separation, SRS, attenuation with distance, test methods | **written** |
| [SineAndTransientVibration.md](docs/SineAndTransientVibration.md) | Low frequency transients, sine equivalent, coupled loads analysis | **written** |
| [AerodynamicLoads.md](docs/AerodynamicLoads.md) | Max-Q, angle of attack, buffet, aeroelasticity, gust and wind shear | **written** |
| [ThermalEnvironments.md](docs/ThermalEnvironments.md) | Aeroheating, solar and albedo, thermal cycling, on-orbit extremes | **written** |
| [StaticAndQuasiStaticLoads.md](docs/StaticAndQuasiStaticLoads.md) | Liftoff, max acceleration, staging, landing, ground handling | **written** |
| [PressureEnvironments.md](docs/PressureEnvironments.md) | Ambient profile, venting, compartment pressure, differential during ascent | **written** |
| [NaturalEnvironments.md](docs/NaturalEnvironments.md) | Wind, humidity, salt fog, sand and dust, lightning, radiation | **written** |
| [LoadCyclesAndCLA.md](docs/LoadCyclesAndCLA.md) | The loads cycle process, coupled loads analysis, model validation | **written** |
| [EnvironmentDerivation.md](docs/EnvironmentDerivation.md) | Flight data to specification: statistics, enveloping, margin policy | **written** |
| [StandardsIndex.md](docs/StandardsIndex.md) | Annotated index of the governing environments standards | **written** |
| [ValidationReferences.md](docs/ValidationReferences.md) | The external sources the tools are checked against, and what is not checked | **written** |

## Planned library

| Class | Computes | Status |
|---|---|---|
| `RandomVibrationSpec` | PSD breakpoint tables, Grms, level derivation, qual and acceptance, Miner duration scaling | **built** |
| `ShockSpectrum` | SRS construction, pyroshock attenuation with distance and joints, test level derivation | **built** |
| `AcousticSpec` | Octave band SPL, overall SPL, vibroacoustic response estimate | **built** |
| `ThermalEnvironment` | Aeroheating estimate, on-orbit hot and cold cases, cycle definition | **built** |
| `LoadFactorSet` | Quasi-static load factors by flight event, combination, limit and ultimate | **built** |

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `utils.py`.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [aerospaceStructures](../aerospaceStructures/) | Supplies the load cases structure is sized against |
| [fluidSystems](../fluidSystems/) | Vibration is what fails lines at their fittings |
| [fluidSystemsTesting](../fluidSystems/fluidSystemsTesting/) | Every environmental test level derives from here |
| [thermalManagement](../thermalManagement/) | Thermal environments drive TPS and thermal control sizing |

---

Sean Bowman
