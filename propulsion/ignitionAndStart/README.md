# ignitionAndStart

**Ignition, Start and Shutdown Transients**

> **Status: scaffolded.** The topic coverage below is defined and the documents are planned. Nothing in this sub-domain is written yet. See [../../fluidSystems/](../../fluidSystems/) for a completed domain.

---

## What This Is

The few hundred milliseconds at each end of a burn, which is where a disproportionate share of engine failures live. An engine that runs happily at steady state can destroy itself during a start that admits propellant in the wrong order.

Shutdown is harder than start and gets less attention. At start the engine is cold and empty; at shutdown it is hot, full, and the propellants continue to arrive after the valves are commanded closed.

Reference documentation, a component class library and a tiered test suite, matching the [fluidSystems](../../fluidSystems/) template.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/IgnitionSystems.md` | Torch, pyrotechnic, hypergolic slug, spark and catalytic. Reliability and reuse | planned |
| `docs/StartTransient.md` | The sequence, priming, the ignition overpressure, and thrust build | planned |
| `docs/ChillInAndConditioning.md` | Cryogenic chill-down, why it matters, and what it costs in propellant | planned |
| `docs/ShutdownTransient.md` | Valve sequencing, dribble volume, and why shutdown is the harder problem | planned |
| `docs/RestartAndReuse.md` | Multiple starts, purge between them, and what reuse demands | planned |

## Planned library

| Class | Computes | Status |
|---|---|---|
| `IgnitionSystem` | Igniter energy, timing margin, and the ignition detection logic | planned |
| `StartTransient` | Priming volumes, sequence timing, and the overpressure estimate | planned |

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../../common/](../../common/) through this sub-domain's `ignitionUtils.py`.

---

## Where this sub-domain connects

| Domain | Interaction |
|---|---|
| [../combustionDevices/](../combustionDevices/) | Ignition happens in the chamber and the injector governs it |
| [../../fluidSystems/](../../fluidSystems/) | Valve sequencing, dribble volumes and water hammer at shutdown |
| [../../reliabilityAndMissionAssurance/](../../reliabilityAndMissionAssurance/) | Ignition reliability is frequently the driving failure mode |

---

Sean Bowman
