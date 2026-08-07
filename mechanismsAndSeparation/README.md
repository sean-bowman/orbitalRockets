# mechanismsAndSeparation

**Mechanisms, Separation Systems and Deployables**

> **Status: scaffolded.** The topic coverage below is defined and the documents are planned. Nothing in this domain is written yet. See [../fluidSystems/](../fluidSystems/) for a completed domain.

---

## What This Is

Mechanisms are single-shot, non-redundant, and they have to work. This domain covers stage and fairing separation, payload release, deployables, and the actuators and pyrotechnics that drive them.

The engineering problem is unusual: most of these devices operate exactly once, in an environment that cannot be fully reproduced, after months of storage, and a failure is immediate mission loss with no recovery.

Reference documentation with a focused class library for the calculations that genuinely need one.

## Design Ethos

- It operates once. Every margin has to be demonstrated by analysis plus test on other articles.
- Shock is the price of a fast separation, and everything nearby pays it.
- Preload relaxation over months of storage is a real failure mode, not a theoretical one.
- Redundancy in a mechanism usually means two ways to release, not two of the same thing.
- Test the mechanism in the flight configuration and orientation. Gravity is not a small effect at this scale.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/MechanismsOverview.md` | Hub: mechanism classes, the design process, document index | planned |
| `docs/SeparationSystems.md` | Stage separation, clamp bands, linear separation, pushers and springs | planned |
| `docs/Pyrotechnics.md` | Initiators, detonating cord, frangible joints, NSI, safe and arm | planned |
| `docs/NonExplosiveActuators.md` | Shape memory, paraffin, split spool, motorized alternatives to pyro | planned |
| `docs/FairingSeparation.md` | Fairing jettison, hinge and clamshell, contamination and clearance | planned |
| `docs/DeploymentMechanisms.md` | Hinges, dampers, latches, deployment kinematics and rate control | planned |
| `docs/ActuatorsAndDrives.md` | Electromechanical, hydraulic, pneumatic; sizing, backdriving, holding | planned |
| `docs/SpringsAndEnergyStorage.md` | Compression springs, energy budgets, separation velocity and tipoff | planned |
| `docs/TribologyAndLubrication.md` | Vacuum lubrication, cold welding, dry films, life at temperature | planned |
| `docs/MechanismTesting.md` | Functional test, life, shock characterization, deployment in 1-g | planned |
| `docs/StandardsIndex.md` | Annotated index of the governing mechanism standards | planned |

## Planned library

| Class | Computes | Status |
|---|---|---|
| `SeparationSystem` | Separation velocity and tipoff rate from spring energy, mass properties and geometry | planned |
| `ClampBand` | Preload, release load, band tension, shock estimate | planned |
| `MechanismActuator` | Actuator sizing: load, stroke, rate, margin against friction and preload | planned |
| `DeploymentKinematics` | Deployment rate, latch loads, damping requirement | planned |

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `utils.py`.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [environmentsAndLoads](../environmentsAndLoads/) | Separation is a major shock source for everything nearby |
| [aerospaceStructures](../aerospaceStructures/) | Separation planes are structural interfaces carrying flight loads |
| [rangeSafetyAndFTS](../rangeSafetyAndFTS/) | Shares pyrotechnic initiation hardware and safe-and-arm practice |
| [reliabilityAndMissionAssurance](../reliabilityAndMissionAssurance/) | Single-shot non-redundant devices dominate the fault tree |

---

Sean Bowman
