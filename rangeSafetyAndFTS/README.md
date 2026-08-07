# rangeSafetyAndFTS

**Range Safety, Flight Termination and Public Risk**

> **Status: scaffolded.** The topic coverage below is defined and the documents are planned. Nothing in this domain is written yet. See [../fluidSystems/](../fluidSystems/) for a completed domain.

---

## What This Is

Range safety is the constraint that does not negotiate. This domain covers the flight termination system, the trajectory limits it enforces, the public risk analysis that sets them, and the regulatory framework the whole thing sits inside.

Documentation first because the content is largely regulatory and analytical rather than hardware sizing, and because the governing documents are the substance.

Reference documentation first. A class library will follow once the documents establish what the tools actually need to compute.

## Design Ethos

- The FTS is the highest reliability requirement on the vehicle, and it must work when everything else has failed.
- Public risk is a quantified, regulated number. It is not a judgement call.
- The launch azimuth and the trajectory are shaped by range safety before they are shaped by performance.
- An autonomous FTS moves the decision onboard; it does not remove the requirement to justify it.
- Range safety requirements are known early. Designing around them late is expensive.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/RangeSafetyOverview.md` | Hub: the regulatory framework, the safety process, document index | planned |
| `docs/FlightTerminationSystems.md` | FTS architecture, ordnance, receivers, batteries, reliability requirements | planned |
| `docs/AutonomousFTS.md` | AFTS architecture, rule sets, verification, the shift from ground command | planned |
| `docs/DestructMechanisms.md` | Linear shaped charge, thrust termination, and what termination achieves | planned |
| `docs/TrajectoryLimitsAndIIP.md` | Instantaneous impact point, destruct lines, gates, limit derivation | planned |
| `docs/PublicRiskAnalysis.md` | Ec, casualty expectation, debris models, overflight, risk criteria | planned |
| `docs/DebrisAndBlast.md` | Debris catalogs, fragment ballistics, blast overpressure, toxic dispersion | planned |
| `docs/HazardAreasAndClearing.md` | Ground hazard zones, launch area clearing, ship and aircraft exclusion | planned |
| `docs/RegulatoryFramework.md` | FAA Part 450, AFSPCMAN 91-710, licensing, safety approval | planned |
| `docs/FTSTestingAndVerification.md` | FTS qualification, end-to-end test, reliability demonstration | planned |
| `docs/StandardsIndex.md` | Annotated index of the governing range safety documents | planned |

## Library

None planned yet. Reference documentation first. A class library will follow once the documents establish what the tools actually need to compute.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [avionicsAndGNC](../avionicsAndGNC/) | AFTS is avionics with the most stringent reliability requirement on the vehicle |
| [mechanismsAndSeparation](../mechanismsAndSeparation/) | Shares ordnance, initiation and safe-and-arm practice |
| [vehicleArchitecture](../vehicleArchitecture/) | Trajectory and azimuth are constrained by range safety before performance |
| [reliabilityAndMissionAssurance](../reliabilityAndMissionAssurance/) | FTS reliability demonstration is the hardest reliability case on the vehicle |

---

Sean Bowman
