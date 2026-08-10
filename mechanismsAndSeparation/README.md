# mechanismsAndSeparation

**Mechanisms, Separation Systems and Deployables**

> **Status: complete.** Five classes, twelve documents and 61 tests, with a worked example that walks one stage separation from the band that holds the joint to the panel that deploys afterwards.

---

## What This Is

Mechanisms are single-shot, non-redundant, and they have to work. This domain covers stage and fairing separation, payload release, deployables, and the actuators and pyrotechnics that drive them.

The engineering problem is unusual: most of these devices operate exactly once, in an environment that cannot be fully reproduced, after months of storage, and a failure is immediate mission loss with no recovery.

**The hardware is simple and the confidence is expensive.** That is the shape of the domain and it is the opposite of most of this repository.

---

## The correction that paid for itself

This domain is built on NASA-STD-5017B, **read directly from the standard rather than from a summary of it**.

A web search summary of that same standard reported the required torque margin as **1.0 or greater**. The standard says a margin **greater than or equal to zero** indicates the requirement is met, because the reserve lives inside the safety factors rather than on top of the result.

Building on the summary would have made every mechanism in this library look twice as marginal as it is, and would have driven hardware changes to correct a problem that does not exist.

The general lesson generalises past this domain: a summary of a standard is a secondary source about a document that **exists and is obtainable**, which is a far weaker position than a summary of an experiment. See [StandardsIndex](docs/StandardsIndex.md).

---

## Design Ethos

- It operates once. Every margin has to be demonstrated by analysis plus test on other articles.
- Shock is the price of a fast separation, and everything nearby pays it.
- Preload relaxation over months of storage is a real failure mode, not a theoretical one.
- Redundancy in a mechanism usually means two ways to release, not two of the same thing.
- Test the mechanism in the flight configuration and orientation. Gravity is not a small effect at this scale.

---

## What the domain found

**The joint that flies is not the joint that was installed.** Preload relaxes 11.3 % over nine months. Embedment, short-term relaxation and storage compound rather than add, and none is visible on the vehicle.

**Neither a stronger spring nor more springs fixes tipoff.** A stronger spring raises the tipoff rate and the separation velocity in the same proportion, so **the rotation accumulated while clearing does not move at all**. And the deterministic worst case is flat in spring count: half the springs high and half low give the same net moment whether there are four or forty. Only the statistical case improves, and lot correlation undermines even that. **Matching in opposing pairs is the only thing that attacks the bound.**

**The latch pays quadratically for the spring**, and the damper that fixes it counts as a resisting torque in the margin equation that justified the spring.

**Test evidence buys margin.** The same actuator goes from +0.205 to +0.620 with no design change.

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [MechanismsOverview.md](docs/MechanismsOverview.md) | Hub: what makes the domain different, what it found, document index | **written** |
| [SeparationSystems.md](docs/SeparationSystems.md) | Clamp bands, preload relaxation, separation velocity, tipoff, recontact | **written** |
| [Pyrotechnics.md](docs/Pyrotechnics.md) | No-fire and all-fire, the firing circuit, safe and arm, the shock | **written** |
| [NonExplosiveActuators.md](docs/NonExplosiveActuators.md) | Shape memory, paraffin, split spool, and why none is sized here | **written** |
| [FairingSeparation.md](docs/FairingSeparation.md) | Jettison, clearance, contamination, the free molecular limit | **written** |
| [DeploymentMechanisms.md](docs/DeploymentMechanisms.md) | Hinges, latches, rate control, the quadratic latch | **written** |
| [ActuatorsAndDrives.md](docs/ActuatorsAndDrives.md) | The margin equation, the three margins, what evidence buys | **written** |
| [SpringsAndEnergyStorage.md](docs/SpringsAndEnergyStorage.md) | Energy budgets, the momentum split, matching against multiplying | **written** |
| [TribologyAndLubrication.md](docs/TribologyAndLubrication.md) | Vacuum friction, cold welding, dry film life, bearing allowables | **written** |
| [MechanismTesting.md](docs/MechanismTesting.md) | Testing a device that operates once, and the one-g offload problem | **written** |
| [StandardsIndex.md](docs/StandardsIndex.md) | NASA-STD-5017B in detail, and the correction reading it produced | **written** |
| [ValidationReferences.md](docs/ValidationReferences.md) | One standard, exact closed forms, three gaps, no hardware case | **written** |

## Library

| Class | Computes | Status |
|---|---|---|
| `SeparationSystem` | Separation velocity, tipoff both ways, recontact | **written** |
| `ClampBand` | Wedge preload, relaxation over storage, joint margin, released energy | **written** |
| `PyrotechnicInitiator` | Firing circuit adequacy and stray energy safety | **written** |
| `MechanismActuator` | Static, dynamic and holding margin to NASA-STD-5017B | **written** |
| `DeploymentKinematics` | Deployment rate, latch impact energy, damper sizing | **written** |

**`PyrotechnicInitiator` was added beyond the plan.** The objectives asked for no-fire and all-fire currents, which is a real circuit calculation, and it is the piece that ties this domain to [electricalPower](../electricalPower/) and to electromagnetic compatibility.

**Six checks refuse rather than report**: a separation that recontacts, a clamp band that gaps, a firing circuit that will not fire, a circuit that could fire from stray energy, a deployable that stalls, and a negative torque margin. Every one is a lost mission rather than a degraded device.

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `mechanismUtils.py`.

---

## Worked example

`codeInterface.py` walks one stage separation end to end.

| Question | Answer |
|---|---|
| Preload lost to nine months of storage | 11.3 % |
| Tipoff, deterministic worst case | 0.396 deg/s |
| Tipoff, statistical at 4 springs | 0.140 deg/s |
| Tipoff, statistical at 12 springs | 0.081 deg/s |
| Latch energy undamped | 3.86 J |
| Latch energy damped | 1.00 J |
| Actuator margin from analysis | +0.205 |
| Actuator margin from flight-article test | +0.620 |

```bash
python mechanismsAndSeparation/codeInterface.py
```

---

## What this domain does not compute

Named rather than approximated, because in a domain this weakly anchored an unmarked estimate is worse than a gap.

**The shock.** Pyroshock prediction is test-derived. [ClampBand](docs/SeparationSystems.md) computes the released strain energy and stops.

**Tribology.** Vacuum lubrication, cold welding and dry film life are material and process questions. Documented, not modelled.

**Non-explosive actuator performance.** Each is a proprietary characteristic curve rather than a calculation.

**Fairing clearance.** A flexible multi-body problem, and applying the rigid-body check to it would be using the tool outside its scope.

**Deployment in one g.** The offload rig is usually the hardest part of testing a deployable.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [environmentsAndLoads](../environmentsAndLoads/) | Separation is a major shock source for everything nearby |
| [aerospaceStructures](../aerospaceStructures/) | Separation planes are structural interfaces carrying flight loads |
| [electricalPower](../electricalPower/) | Firing circuits and the sustained power a non-explosive actuator needs |
| [vehicleArchitecture](../vehicleArchitecture/) | The stage masses this separates, and the fairing mass it drops |
| [rangeSafetyAndFTS](../rangeSafetyAndFTS/) | Shares pyrotechnic initiation hardware and safe-and-arm practice |
| [reliabilityAndMissionAssurance](../reliabilityAndMissionAssurance/) | Single-shot non-redundant devices dominate the fault tree |

---

Sean Bowman
