# avionicsAndGNC

**Avionics, Guidance, Navigation and Control**

> **Status: scaffolded.** The topic coverage below is defined and the documents are planned. Nothing in this domain is written yet. See [../fluidSystems/](../fluidSystems/) for a completed domain.

---

## What This Is

The vehicle's nervous system. This domain covers flight computers and their redundancy, the sensor suite, guidance and navigation, control laws and actuation, and the data systems that carry it all.

Documentation first: the control algorithms overlap with the conceptual vehicle design work already covered elsewhere, and a library here would duplicate rather than add. The value is in understanding the architecture and the interfaces to the domains that are built out.

Reference documentation first. A class library will follow once the documents establish what the tools actually need to compute.

## Design Ethos

- The control loop is only as good as its actuator, and the actuator is usually the limit.
- Sensor errors are systematic before they are random. Know the bias, not just the noise.
- Redundancy management is harder than redundancy. Deciding which computer is right is the problem.
- Latency is a phase margin cost. Budget it explicitly.
- Telemetry you did not record is data you do not have, and you only find out after the failure.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/AvionicsOverview.md` | Hub: the avionics architecture, interfaces, document index | planned |
| `docs/FlightComputers.md` | Processor selection, redundancy, voting, radiation tolerance, watchdogs | planned |
| `docs/SensorsAndNavigation.md` | IMU, GPS, star trackers, sensor errors, alignment, Kalman filtering | planned |
| `docs/GuidanceAlgorithms.md` | Ascent guidance, closed-loop guidance, targeting, abort logic | planned |
| `docs/ControlLawsAndStability.md` | Attitude control, gain scheduling, stability margins, slosh and flex coupling | planned |
| `docs/ActuationAndTVC.md` | Thrust vector control, RCS, actuator dynamics, control authority | planned |
| `docs/DataBusesAndNetworks.md` | Bus selection, timing, determinism, fault containment | planned |
| `docs/TelemetryAndInstrumentation.md` | Measurement lists, sample rates, bandwidth, recording strategy | planned |
| `docs/SoftwareAssurance.md` | Flight software process, verification, coding standards, autocoding | planned |
| `docs/AvionicsTesting.md` | HIL, processor-in-the-loop, integrated testing, day-in-the-life | planned |
| `docs/StandardsIndex.md` | Annotated index of the governing avionics standards | planned |

## Library

None planned yet. Reference documentation first. A class library will follow once the documents establish what the tools actually need to compute.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [electricalPower](../electricalPower/) | Shares the harness, grounding scheme and EMI environment |
| [fluidSystems](../fluidSystems/) | Commands every valve and reads every transducer |
| [vehicleArchitecture](../vehicleArchitecture/) | Control authority and guidance losses feed the performance budget |
| [rangeSafetyAndFTS](../rangeSafetyAndFTS/) | AFTS is avionics with the most stringent reliability requirement on the vehicle |

---

Sean Bowman
