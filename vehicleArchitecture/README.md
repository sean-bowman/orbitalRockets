# vehicleArchitecture

**Launch Vehicle Sizing, Staging and Configuration Trades**

> **Status: scaffolded.** The topic coverage below is defined and the documents are planned. Nothing in this domain is written yet. See [../fluidSystems/](../fluidSystems/) for a completed domain.

---

## What This Is

The top-level design that sets the requirements every other domain works to. This domain covers vehicle sizing from a payload requirement: staging, propellant selection, mass fractions, thrust-to-weight, trajectory basics, and the configuration trades that determine whether a vehicle closes at all.

It sits above the other domains and is where the mass chain that runs through all of them either closes or does not.

Reference documentation, a component class library and a tiered test suite, matching the [fluidSystems](../fluidSystems/) template.

## Design Ethos

- The rocket equation is unforgiving and it is not the hard part. The mass fraction is the hard part.
- A vehicle either closes or it does not. Optimizing an open design is wasted effort.
- Every subsystem mass estimate is wrong. Carry the uncertainty explicitly rather than pretending.
- Staging is a discrete choice with continuous consequences. Trade it early because it cannot be changed late.
- The payload is the residual of a large subtraction. Small errors upstream are large errors in payload.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/ArchitectureOverview.md` | Hub: the sizing loop, the mass chain, document index | planned |
| `docs/RocketEquationAndStaging.md` | Tsiolkovsky, staging optimization, serial and parallel, drop tanks | planned |
| `docs/PropellantSelection.md` | Isp versus density, storability, handling, the density-impulse trade | planned |
| `docs/MassFractionsAndEstimating.md` | Mass estimating relationships, structural mass fractions, growth allowance | planned |
| `docs/ThrustToWeightAndSizing.md` | Liftoff T/W, gravity losses, engine count, throttle range | planned |
| `docs/TrajectoryBasics.md` | Ascent profile, gravity turn, losses, max-Q, delta-V budget | planned |
| `docs/ConfigurationTrades.md` | Diameter, length, tank arrangement, engine layout, fairing sizing | planned |
| `docs/MassProperties.md` | CG, inertia, mass tracking, growth management, margin policy | planned |
| `docs/PerformanceAndPayload.md` | Payload to orbit, performance sensitivity, margin allocation | planned |
| `docs/ReusabilityImpacts.md` | Recovery hardware mass, propellant reserve, performance cost of reuse | planned |
| `docs/CostAndProducibility.md` | Design for manufacture at the vehicle level, rate and learning curve | planned |
| `docs/StandardsIndex.md` | Annotated index of relevant standards and reference vehicles | planned |

## Planned library

| Class | Computes | Status |
|---|---|---|
| `StagedVehicle` | Rocket equation across stages, mass fractions, payload, staging optimization | planned |
| `MassBudget` | Subsystem mass rollup with growth allowance, margin tracking, CG and inertia | planned |
| `AscentTrajectory` | Simplified ascent: gravity and drag losses, delta-V budget, max-Q | planned |
| `PropellantTrade` | Isp, density, bulk density, density-impulse comparison across combinations | planned |
| `SizingLoop` | Iterates vehicle geometry, mass and performance to a closed design | planned |

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `utils.py`.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [aerospaceStructures](../aerospaceStructures/) | Supplies the tank and structure sizes; consumes their mass estimates |
| [fluidSystems](../fluidSystems/) | Tank pressure and feed system mass feed directly into the mass chain |
| [recoveryAndReusability](../recoveryAndReusability/) | Recovery hardware is a payload penalty paid at every launch |
| [environmentsAndLoads](../environmentsAndLoads/) | Configuration determines the load environment |

---

Sean Bowman
