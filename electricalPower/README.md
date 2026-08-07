# electricalPower

**Electrical Power, Distribution and Harnessing**

> **Status: scaffolded.** The topic coverage below is defined and the documents are planned. Nothing in this domain is written yet. See [../fluidSystems/](../fluidSystems/) for a completed domain.

---

## What This Is

The electrical system is the one that touches every other subsystem, and harnessing is reliably underestimated in both mass and schedule. This domain covers power generation and storage, distribution and protection, harness design, and the grounding and bonding scheme that determines whether the vehicle has an EMI problem.

It is included because a fluid system with valves and instrumentation is an electrical system too, and the failure modes are shared.

Reference documentation with a focused class library for the calculations that genuinely need one.

## Design Ethos

- Harness mass is always more than estimated. Estimate it from connector and run counts, not from a fraction.
- Grounding is a topology decision made early and expensive to change late.
- Every connector is a failure point, and connector count is the best available reliability proxy.
- Voltage drop over a long run is a real constraint, not a rounding error.
- Batteries are a thermal problem and a safety problem before they are an energy problem.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/PowerOverview.md` | Hub: the power architecture, the energy budget, document index | planned |
| `docs/BatteriesAndStorage.md` | Chemistries, sizing, discharge curves, thermal behaviour, safety | planned |
| `docs/PowerDistribution.md` | Buses, switching, protection, fusing, load shedding | planned |
| `docs/HarnessDesign.md` | Wire gauge, derating, routing, shielding, mass estimating, connectors | planned |
| `docs/GroundingAndBonding.md` | Single point versus multipoint, bonding straps, structure as return | planned |
| `docs/EMIAndEMC.md` | Emissions and susceptibility, shielding, filtering, MIL-STD-461 | planned |
| `docs/PyroCircuits.md` | Firing circuits, no-fire and all-fire, safe and arm, stray current | planned |
| `docs/ValveAndActuatorDrive.md` | Solenoid and motor drive, inrush, holding current, flyback | planned |
| `docs/PowerQuality.md` | Transients, ripple, undervoltage, brownout behaviour | planned |
| `docs/ElectricalTesting.md` | Continuity, insulation resistance, hipot, EMC test, harness acceptance | planned |
| `docs/StandardsIndex.md` | Annotated index of the governing electrical standards | planned |

## Planned library

| Class | Computes | Status |
|---|---|---|
| `PowerBudget` | Load rollup by mode and phase, energy from a duty cycle, battery sizing with margin | planned |
| `Battery` | Capacity, discharge under load, voltage curve, thermal load, sizing to a mission profile | planned |
| `HarnessSizing` | Wire gauge from current and length, derating, voltage drop, harness mass estimate | planned |
| `PyroCircuit` | Firing current, no-fire margin, bridgewire energy, stray current assessment | planned |

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `utils.py`.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [fluidSystems](../fluidSystems/) | Valve actuation, heaters and instrumentation are all electrical loads |
| [avionicsAndGNC](../avionicsAndGNC/) | Shares the harness, the grounding scheme and the EMI environment |
| [mechanismsAndSeparation](../mechanismsAndSeparation/) | Pyro firing circuits and actuator drive |
| [thermalManagement](../thermalManagement/) | Heater power is usually the largest steady load on a storable-propellant vehicle |

---

Sean Bowman
