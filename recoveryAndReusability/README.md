# recoveryAndReusability

**Recovery, Entry, Landing and Refurbishment**

> **Status: scaffolded.** The topic coverage below is defined and the documents are planned. Nothing in this domain is written yet. See [../fluidSystems/](../fluidSystems/) for a completed domain.

---

## What This Is

Reuse changes the economics of launch and it changes the engineering everywhere. This domain covers the flight side (entry, descent, landing) and the ground side (inspection, refurbishment, life tracking) along with the economics that decide whether reuse is worth the performance it costs.

The interesting engineering is not the landing. It is designing hardware whose condition after flight can be established cheaply enough to fly it again.

Reference documentation with a focused class library for the calculations that genuinely need one.

## Design Ethos

- Reuse is an inspection problem before it is a landing problem.
- Every kilogram of recovery hardware is paid on every flight, including the ones that do not recover.
- Design for inspectability or accept teardown. There is no third option.
- Life tracking only works if the flight environment was actually measured.
- The break-even flight count is the real figure of merit, not the fact of reuse.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/RecoveryOverview.md` | Hub: recovery architectures, the reuse economics, document index | planned |
| `docs/EntryAerodynamics.md` | Entry environment, heating, deceleration, control authority | planned |
| `docs/DescentAndLanding.md` | Propulsive landing, parachutes, landing legs, touchdown loads | planned |
| `docs/RecoveryHardware.md` | Grid fins, legs, chutes, flotation, and their mass and performance cost | planned |
| `docs/InspectionAndAcceptance.md` | Post-flight inspection, what to inspect, NDE, disposition criteria | planned |
| `docs/RefurbishmentProcess.md` | Turnaround flow, cleaning, replacement policy, cost per turn | planned |
| `docs/LifeTrackingAndLimits.md` | Cycle counting, life-limited parts, usage monitoring, retirement | planned |
| `docs/FluidSystemReuse.md` | What reuse does to a fluid system: seals, valves, contamination, cleaning | planned |
| `docs/ReuseEconomics.md` | Break-even flight count, refurbishment cost, performance penalty, fleet leader | planned |
| `docs/StandardsIndex.md` | Annotated index of relevant standards and reuse precedent | planned |

## Planned library

| Class | Computes | Status |
|---|---|---|
| `RecoveryBudget` | Recovery hardware mass and propellant reserve, and the payload penalty per flight | planned |
| `LandingLoads` | Touchdown load factors, leg stroke and energy absorption, tipover margin | planned |
| `LifeTracking` | Cycle accumulation against life limits, remaining life, retirement prediction | planned |
| `ReuseEconomics` | Cost per flight versus flight count, break-even, sensitivity to refurbishment cost | planned |

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `utils.py`.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [vehicleArchitecture](../vehicleArchitecture/) | Recovery hardware and reserve propellant are a direct payload penalty |
| [thermalManagement](../thermalManagement/) | Entry heating drives the TPS that has to survive repeatedly |
| [fluidSystems](../fluidSystems/) | Seals, valves and cleanliness after a flight are the refurbishment driver |
| [reliabilityAndMissionAssurance](../reliabilityAndMissionAssurance/) | Life limits and usage monitoring are reliability instruments |

---

Sean Bowman
