# avionicsAndGNC

**Avionics, Guidance, Navigation and Control**

> **Status: complete.** Three classes, twelve documents and 55 tests, with a worked example whose three subjects share one result: the quantity that dominates is not the quantity that gets specified.

---

## What This Is

The vehicle's nervous system. This domain covers flight computers and their redundancy, the sensor suite, guidance and navigation, control laws and actuation, and the data systems that carry it all.

It was scaffolded documentation-first, on the grounds that the trajectory and control algorithm work overlaps material that already exists and a library here would duplicate rather than add. **Building it confirmed that reasoning rather than overturning it.** Three classes were built anyway, and the test applied to each was whether it computes something no other domain does.

**This domain is built for architectural literacy rather than design authority.** It says which question to ask, which is what somebody outside the discipline actually needs.

---

## The three results

**The navigation error is the gyroscope, not the accelerometer.** An accelerometer bias integrates twice into position and grows as the square of time. A gyro bias integrates once into attitude, that tilts the accelerometer triad into gravity, and the result integrates twice more: a cube. **A cubic overtakes a quadratic**, here at 63 seconds, and by the 540 second flight time the gyro term is 3743 m against 429 m and 98.6 per cent of the variance. Below the crossover an accelerometer specification is what to buy and above it a gyro specification is, and most launch vehicle flights are on the gyro side of it. The spread across three IMU grades is 3594 times, which makes the grade the decision and the unit a detail.

**The disturbance that sizes the gimbal changes through the flight.** Above the atmosphere the thrust misalignment governs, and it is present the whole burn. At max-Q the aerodynamic term takes over, because the vehicle is unstable by design: the centre of pressure sits 6 per cent of the vehicle length ahead of the centre of gravity, so any angle of attack grows itself. **A gimbal sized on one condition is sized on the wrong one for most of the ascent.** The 8 degree gust case at max-Q is refused outright, and the class raises rather than reporting the negative margin, because that vehicle is lost rather than degraded.

**The angle is half the actuator answer and the rate is the other half.** Commanding the remaining 6.38 degrees at 1 Hz needs 40 degrees per second. An actuator slower than that rate-limits, and a rate limit is a nonlinearity that gain and phase margins do not describe at all. A loop with good margins on paper goes unstable in flight through exactly this.

**Twelve channels out of ninety three are three quarters of the telemetry.** Bit rate is sample rate times word length, and sample rate spans four orders of magnitude across a measurement list. The high-rate structural accelerometers dominate everything else combined, which is where a bandwidth cut has to come from and exactly the group an investigation needs. The recorder holds 109 minutes against a 9 minute flight and the downlink is the constrained side, **and they fail in opposite ways**, which is why a vehicle records everything and downlinks a subset.

---

## Design Ethos

- The control loop is only as good as its actuator, and the actuator is usually the limit.
- Sensor errors are systematic before they are random. Know the bias, not just the noise.
- Redundancy management is harder than redundancy. Deciding which computer is right is the problem.
- Latency is a phase margin cost. Budget it explicitly: 83 ms costs 30 degrees at 1 Hz.
- Software fails by design and never at random, so three copies of it vote unanimously for the wrong answer.
- Telemetry you did not record is data you do not have, and you only find out after the failure.

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [AvionicsOverview.md](docs/AvionicsOverview.md) | Hub: what the domain found, the architecture, document index | **written** |
| [SensorsAndNavigation.md](docs/SensorsAndNavigation.md) | The integration orders, the crossover, grades, what aiding does | **written** |
| [ActuationAndTVC.md](docs/ActuationAndTVC.md) | Control authority, the disturbance set, the rate limit | **written** |
| [ControlLawsAndStability.md](docs/ControlLawsAndStability.md) | Margins, gain scheduling, bending and slosh separation | **written** |
| [GuidanceAlgorithms.md](docs/GuidanceAlgorithms.md) | Guidance against control, the ascent phases, why none is computed | **written** |
| [FlightComputers.md](docs/FlightComputers.md) | Redundancy, voting, the common mode problem, radiation | **written** |
| [DataBusesAndNetworks.md](docs/DataBusesAndNetworks.md) | Determinism, the latency budget, fault containment | **written** |
| [TelemetryAndInstrumentation.md](docs/TelemetryAndInstrumentation.md) | Measurement lists, sample rates, record against downlink | **written** |
| [SoftwareAssurance.md](docs/SoftwareAssurance.md) | Why software has no random failures, process, autocoding | **written** |
| [AvionicsTesting.md](docs/AvionicsTesting.md) | The ladder, hardware in the loop, day in the life, what nothing catches | **written** |
| [StandardsIndex.md](docs/StandardsIndex.md) | Every standard here, and every one unread | **written** |
| [ValidationReferences.md](docs/ValidationReferences.md) | No anchor, and why the conclusions survive it | **written** |

## Library

| Class | Computes | Status |
|---|---|---|
| `NavigationDrift` | Error growth by term, the crossover, grade comparison, what aiding bounds | **written** |
| `ControlAuthority` | Disturbance moments by phase, trim, gimbal margin, required rate | **written** |
| `TelemetryBudget` | Channel rollup, framing and margin, link fit, recorder duration | **written** |

**Three things were deliberately not built**, and each has a stated reason.

**Guidance algorithms.** They optimise a delta-V budget that [vehicleArchitecture](../vehicleArchitecture/) already owns, and a guidance law without a trajectory integration is a formula rather than a result. See [GuidanceAlgorithms](docs/GuidanceAlgorithms.md).

**Control law synthesis.** It needs a coupled plant model: rigid body, bending modes, slosh and actuator together. [aerospaceStructures](../aerospaceStructures/) owns the modes and [fluidSystems](../fluidSystems/) owns the slosh, and assembling them is a real piece of work rather than a class.

**Kalman filtering.** The error models here are what a filter would consume. Implementing it would be implementing an estimator whose tuning is the entire engineering content.

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `avionicsUtils.py`.

---

## Worked example

`codeInterface.py` works an ascent avionics suite through navigation, control and telemetry.

| Question | Answer |
|---|---|
| What dominates the navigation error | gyro bias through tilt |
| Its share of the variance at 540 s | 98.6 % |
| When the gyro term overtakes the accelerometer | 63 s |
| Spread across three IMU grades | 3594x |
| What governs the gimbal at max-Q | aerodynamic at angle of attack |
| What governs it above the atmosphere | thrust misalignment |
| The max-Q gust case | **refused** |
| Gimbal rate needed at 1 Hz | 40 deg/s |
| Share of telemetry in 12 of 93 channels | 75 % |
| Recorder duration against a 9 minute flight | 109 min |

```bash
python avionicsAndGNC/codeInterface.py
```

---

## The gaps

**This domain has no hardware anchor and no standard anchor**, which makes it the weakest-anchored in the repository. Every standard in its index was not read.

It is also the domain whose conclusions depend least on its numbers, and the two facts are related. The gyro term overtaking the accelerometer term follows from an integration order. The governing disturbance changing follows from one term being present in one phase and absent in the other. The telemetry concentration follows from the spread of sample rates. **None of the three is validated and none of the three is at risk**, which is a different claim from the numbers being right.

**An IMU datasheet is the most tractable gap by a wide margin**, and every manufacturer publishes one. See [ValidationReferences](docs/ValidationReferences.md), which states this at the top rather than the bottom.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [electricalPower](../electricalPower/) | Shares the harness, grounding scheme and EMI environment, and is where MIL-STD-461 is indexed |
| [fluidSystems](../fluidSystems/) | Commands every valve and reads every transducer; owns the slosh modes |
| [aerospaceStructures](../aerospaceStructures/) | Owns the bending modes the control frequency has to stay clear of |
| [vehicleArchitecture](../vehicleArchitecture/) | Owns the delta-V budget that guidance would optimise against |
| [rangeSafetyAndFTS](../rangeSafetyAndFTS/) | AFTS is avionics with the most stringent reliability requirement on the vehicle |

---

Sean Bowman
