# rangeSafetyAndFTS

**Range Safety, Flight Termination and Public Risk**

> **Status: complete.** Four classes, eleven documents and 80 tests, anchored to 14 CFR Part 450 read from the regulation.

---

## What This Is

Range safety is the constraint that does not negotiate. This domain covers the flight termination system, the trajectory limits it enforces, the public risk analysis that sets them, and the regulatory framework the whole thing sits inside.

**The governing documents are the substance here**, more than in any other domain in this repository. What is computed is the arithmetic underneath them.

---

## The four results

**The instantaneous impact point accelerates and then ceases to exist.** Downrange distance grows faster than linearly with speed, so the impact point crawls early in an ascent and sprints late: in the worked case the drift rate grows from 1.1 to 55 km per second of flight, a factor of 49. Then at orbital insertion the free-flight perigee rises above the surface, the trajectory no longer intersects the Earth, and **there is no impact point at all.** The class raises rather than returning a large number, because that is the moment the flight termination system stops having a job.

**Risk follows population, not impact probability.** The downrange ocean takes 59 per cent of the debris and contributes 2 per cent of the casualty expectation; one coastal town takes 0.03 per cent of the debris and contributes 83 per cent of the risk. **A range safety analysis is a population analysis with a trajectory attached**, and the azimuth that minimises risk minimises overflown people rather than overflown distance.

**The individual criterion binds, not the collective one.** 14 CFR 450.101 sets both, and collective risk can be met by spreading a small number thinly over many people while individual risk cannot. In the worked case the individual margin is 3.3 against a collective 6.8, and it is the household nearest the trajectory that shapes the azimuth.

**And the reliability requirement cannot be demonstrated.** 450.145 asks for 0.999 at 95 per cent confidence, which by zero-failure test alone is **2,994 successful firings of a single-use ordnance system.** Thirty tests demonstrate 0.905, and each additional nine costs ten times the tests. The claim is argued from redundancy, parts history, environmental margin and an end-to-end test, rather than demonstrated. **That is not a weakness in the regulation, it is the only available answer.**

**Two things the word redundant hides.** A two-out-of-two initiator pair reaches 0.99003 against 0.995 for a single one: **doubling it made the system worse.** And a dual parallel ordnance train behind one command receiver at 0.995 fails the requirement, because **the system reliability is the receiver's, not the ordnance's.**

---

## Design Ethos

- The FTS is the highest reliability requirement on the vehicle, and it must work when everything else has failed.
- Public risk is a quantified, regulated number. It is not a judgement call.
- The launch azimuth and the trajectory are shaped by range safety before they are shaped by performance.
- An autonomous FTS moves the decision onboard; it does not remove the requirement to justify it.
- Range safety requirements are known early. Designing around them late is expensive.
- Size the destruct lines on the fastest part of the ascent, not the average.

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [RangeSafetyOverview.md](docs/RangeSafetyOverview.md) | Hub: what the domain found, the three questions, document index | **written** |
| [TrajectoryLimitsAndIIP.md](docs/TrajectoryLimitsAndIIP.md) | The impact point, why it accelerates, destruct lines and gates | **written** |
| [PublicRiskAnalysis.md](docs/PublicRiskAnalysis.md) | Casualty expectation, the two criteria, what drives risk | **written** |
| [FlightTerminationSystems.md](docs/FlightTerminationSystems.md) | Architecture, the demonstration arithmetic, redundancy that is not | **written** |
| [AutonomousFTS.md](docs/AutonomousFTS.md) | Moving the decision onboard, rule sets, and what it does not remove | **written** |
| [DestructMechanisms.md](docs/DestructMechanisms.md) | Shaped charge, thrust termination, what termination achieves | **written** |
| [DebrisAndBlast.md](docs/DebrisAndBlast.md) | Fragment ballistics, the dispersion problem, blast and toxic | **written** |
| [HazardAreasAndClearing.md](docs/HazardAreasAndClearing.md) | Ground and flight hazard areas, ships, aircraft, clearing | **written** |
| [RegulatoryFramework.md](docs/RegulatoryFramework.md) | Part 450, hazard control strategies, what an applicant submits | **written** |
| [FTSTestingAndVerification.md](docs/FTSTestingAndVerification.md) | What a test can establish, qualification, the end-to-end test | **written** |
| [StandardsIndex.md](docs/StandardsIndex.md) | One regulation read, and the range documents indexed | **written** |
| [ValidationReferences.md](docs/ValidationReferences.md) | The criteria, the arithmetic, and two gaps | **written** |

## Library

| Class | Computes | Status |
|---|---|---|
| `ImpactPoint` | Keplerian free-flight impact point, drift through an ascent, destruct line warning | **written** |
| `PublicRisk` | Casualty area, collective and individual risk against 450.101, land use comparison | **written** |
| `TerminationReliability` | Zero-failure demonstration, redundancy configurations, the 450.145 check | **written** |
| `DebrisDispersion` | Fragment catalogue, ballistic descent to the ground, footprint, impact probability per region | **written** |

**Five things were deliberately not built.** Blast overpressure, which [groundSystemsAndOperations](../groundSystemsAndOperations/) computes from DESR 6055.09; toxic dispersion, which neither domain models and both say so; ordnance initiation, which [mechanismsAndSeparation](../mechanismsAndSeparation/) owns; autonomous FTS rule sets, whose verification is a [software assurance](../avionicsAndGNC/) problem; and the licensing process, which is a workflow.

**And three that `DebrisDispersion` stops short of**, named rather than implied. A Monte Carlo over thousands of sampled fragments, where this propagates four classes and disperses each: **the difference is coverage rather than accuracy.** A structural break-up model, which decides what the catalogue is. And a lethality model, which needs an impact angle and an injury criterion on top of the impact velocity this domain computes.

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `rangeSafetyUtils.py`.

---

## Worked example

`codeInterface.py` takes one coastal launch through the impact point, the debris footprint, the risk analysis and the termination system.

| Question | Answer |
|---|---|
| Impact point drift, first to last | 49x |
| When the impact point ceases to exist | t+320 s |
| Ocean share of debris against risk | 59 % against 2 % |
| Debris footprint, length against width | **81 km against 4.5 km** |
| Ballistic coefficient span across the catalogue | 656 to one |
| Offset the coastal town needs to be licensable | **20 km** |
| Collective Ec against its limit | 6.5e-6 against 1e-4 |
| Individual Pc against its limit | 3.0e-7 against 1e-6 |
| Which criterion binds | **individual** |
| Failure probability at which Ec reaches the limit | 0.31 |
| Land use classes that clear the criterion | 4 of 7 |
| Tests to demonstrate 0.999 at 95 % | **2,994** |
| What 30 tests actually demonstrate | 0.905 |
| System reliability, and its weakest link | 0.99918, command receiver |

```bash
python rangeSafetyAndFTS/codeInterface.py
```

---

## The anchor, and what it settled

**14 CFR Part 450 was read** for sections 450.101 and 450.145, which are the launch safety criteria and the highly reliable flight safety system. Both are duplicated into [validation/referenceCases.py](../validation/referenceCases.py) and asserted against the library by a test.

Reading it settled three things a summary would not have.

**Collective and individual risk are separate tests and both apply.** The individual limit exists to stop the trade the collective one permits, and it is usually the tighter.

**The neighbouring operations personnel limits are looser by exactly a factor of two on the collective side and ten on the individual side**, which is a policy statement rather than an engineering one.

**And the reliability requirement covers the off-vehicle portion.** The ground transmitter chain carries the same 0.999 at 95 per cent as the hardware on the rocket.

**The anchor is exact and it establishes nothing about the analysis feeding it.** The criteria are numbers a launch is licensed against rather than a model of anything, so reproducing them is exact by construction. The debris and population inputs are representative and registered as unvalidated, which means **the arithmetic is right and the answer is illustrative.** That is stated in [ValidationReferences](docs/ValidationReferences.md) rather than implied.

**RCC 319 and AFSPCMAN 91-710 were not read**, and a debris catalogue and break-up model is the largest single piece of unbuilt work implied by this repository.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [avionicsAndGNC](../avionicsAndGNC/) | An autonomous FTS is avionics with the most stringent reliability requirement on the vehicle |
| [mechanismsAndSeparation](../mechanismsAndSeparation/) | Owns the initiation margins and the safe and arm practice |
| [groundSystemsAndOperations](../groundSystemsAndOperations/) | Owns the blast siting calculation and the clearing conventions |
| [recoveryAndReusability](../recoveryAndReusability/) | Computes the ballistic descent of a single body, which a debris model would run many times |
| [vehicleArchitecture](../vehicleArchitecture/) | Azimuth and trajectory are constrained by range safety before performance |
| [reliabilityAndMissionAssurance](../reliabilityAndMissionAssurance/) | Owns the common cause arithmetic this domain's redundancy model leaves out |

---

Sean Bowman
