# vehicleArchitecture

**Launch Vehicle Sizing, Staging and Configuration Trades**

> **Status: complete.** Four classes, thirteen documents and 61 tests, with a worked example that traces one bar of feed system pressure drop all the way to the payload and finds it worth 730 kg of liftoff mass.

---

## What This Is

The top-level design that sets the requirements every other domain works to. Vehicle sizing from a payload requirement: staging, mass fractions, thrust-to-weight, the delta-V budget, and the configuration trades that determine whether a vehicle closes at all.

It sits above the other domains and is where the mass chain running through all of them either closes or does not.

Reference documentation, a component class library and a tiered test suite, matching the [fluidSystems](../fluidSystems/) template.

---

## The result

**Every kilogram added to the first stage tank costs about eleven kilograms at liftoff.**

One bar of extra feed system pressure drop thickens the tank wall by 0.29 mm, adds 64 kg to the tank, and costs **730 kg on a 40 tonne vehicle**. That chain runs from a fluid system pressure drop through a structures wall thickness into a rocket equation, and no single subsystem can see it.

```
feed pressure drop -> tank pressure -> wall thickness -> tank mass
                   -> structural coefficient -> rocket equation -> payload
```

[SizingLoop](docs/MassChain.md) imports the pressure vessel model from [aerospaceStructures](../aerospaceStructures/) rather than reimplementing a tank, so a change in the structures allowables reaches the payload without anyone reconciling two tank models. That is the only three-domain coupling in this repository and a test asserts it still resolves.

---

## Design Ethos

- The rocket equation is unforgiving and it is not the hard part. The mass fraction is the hard part.
- A vehicle either closes or it does not. Optimizing an open design is wasted effort.
- Every subsystem mass estimate is wrong. Carry the uncertainty explicitly rather than pretending.
- Staging is a discrete choice with continuous consequences. Trade it early because it cannot be changed late.
- **Payload sensitivity is inversely proportional to payload fraction.** This bullet used to say payload is the residual of a large subtraction so small errors upstream are large errors in payload. That is a claim about marginal vehicles rather than about rockets, and building the domain disproved it in the general form. See [PerformanceAndPayload](docs/PerformanceAndPayload.md).

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [ArchitectureOverview.md](docs/ArchitectureOverview.md) | Hub: the sizing loop, what the domain found, document index | **written** |
| [MassChain.md](docs/MassChain.md) | Feed pressure to payload, the amplification, why it crosses domains | **written** |
| [RocketEquationAndStaging.md](docs/RocketEquationAndStaging.md) | Tsiolkovsky, the bookkeeping, optimal staging and why it is flat | **written** |
| [MassFractionsAndEstimating.md](docs/MassFractionsAndEstimating.md) | Where estimates come from, growth allowance against margin | **written** |
| [ThrustToWeightAndSizing.md](docs/ThrustToWeightAndSizing.md) | The loss optimum nobody flies, engine count, engine-out | **written** |
| [TrajectoryBasics.md](docs/TrajectoryBasics.md) | The delta-V budget, the losses, and what is not modelled | **written** |
| [PerformanceAndPayload.md](docs/PerformanceAndPayload.md) | Payload sensitivity, and the ethos this domain corrected | **written** |
| [ConfigurationTrades.md](docs/ConfigurationTrades.md) | Diameter, tank arrangement, common bulkhead, fairing | **written** |
| [MassProperties.md](docs/MassProperties.md) | CG on predictions, burn travel, inertia, re-baselining | **written** |
| [ReusabilityImpacts.md](docs/ReusabilityImpacts.md) | The recovery penalty, measured rather than modelled | **written** |
| [PropellantSelection.md](docs/PropellantSelection.md) | What this adds to the propulsion trade, which is tank mass | **written** |
| [CostAndProducibility.md](docs/CostAndProducibility.md) | The axis mass-based design cannot see | **written** |
| [StandardsIndex.md](docs/StandardsIndex.md) | The standards, and the ones not read | **written** |
| [ValidationReferences.md](docs/ValidationReferences.md) | One hardware source, exact closed forms, three gaps | **written** |

## Library

| Class | Computes | Status |
|---|---|---|
| `StagedVehicle` | Rocket equation across stages, staging optimisation, payload sensitivity | **written** |
| `MassBudget` | Subsystem rollup with growth allowance and margin kept apart, CG and inertia | **written** |
| `AscentTrajectory` | Delta-V budget, ascent losses, thrust-to-weight dependence | **written** |
| `SizingLoop` | Iterates tank, mass and performance to a closed vehicle, and traces the mass chain | **written** |
| `PropellantTrade` | Isp, density, bulk density, density-impulse comparison | **not built** |

**`PropellantTrade` was deliberately not built.** [propulsion](../propulsion/docs/PropellantSelection.md) already owns `PropellantCombination`, which computes bulk density, density impulse and the volume split across seven combinations. A second table here would be a second thing to keep in agreement. What this domain adds instead is the reason density impulse is a figure of merit at all, which is a tank mass propulsion does not model, and that is in [PropellantSelection](docs/PropellantSelection.md).

Two checks **refuse rather than report**: a sizing loop that diverges, and a stage whose structure outweighs the propellant it would need. Both are open designs, and returning the last iterate of a diverging loop would hand somebody an open design that reads as closed.

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `vehicleUtils.py`.

---

## Worked example

`codeInterface.py` closes a 1.5 t to LEO vehicle from the tank outward.

| Lever | Worth |
|---|---|
| One bar of feed system pressure drop | **730 kg of liftoff mass** |
| One kilogram in the first stage tank | **11.3 kg of liftoff mass** |
| Ten per cent off the optimal staging split | 0.20 % |
| One per cent of dry mass, healthy vehicle | 0.34 % of payload |
| One per cent of dry mass, marginal vehicle | 1.50 % of payload |

**The largest lever is the one furthest from anybody who calls themselves a vehicle designer.** The smallest is the one that gets argued about most.

```bash
python vehicleArchitecture/codeInterface.py
```

---

## Three things this domain found that it did not expect

**The staging optimum is flat and the reference vehicle is not at it.** Falcon 9 sits about four per cent off its own payload optimum, and that four per cent buys engine commonality, booster recovery and a staging altitude the recovery needs. A vehicle at its theoretical staging optimum would be a worse vehicle.

**The loss budget wants a liftoff thrust to weight of 2.58** and everything flies near 1.35. Gravity loss falls faster with thrust to weight than drag loss rises across the whole practical range, so the loss budget sets a floor rather than a target and the real decision is engine mass and engine-out.

**Where this domain finds a flat mass optimum, it has usually found a place where cost is the real objective.** That pattern holds for the staging split, the thrust to weight and reusability, and it is what [CostAndProducibility](docs/CostAndProducibility.md) exists to say.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [aerospaceStructures](../aerospaceStructures/) | Supplies the pressure vessel model the sizing loop imports; a change in its allowables reaches the payload |
| [fluidSystems](../fluidSystems/) | Where the tank pressure is decided, and therefore where the mass chain starts |
| [propulsion](../propulsion/) | Engine performance and the propellant trade, consumed rather than duplicated |
| [recoveryAndReusability](../recoveryAndReusability/) | Recovery hardware is a payload penalty paid at every launch |
| [environmentsAndLoads](../environmentsAndLoads/) | Configuration determines the load environment |

---

Sean Bowman
