[Home](../README.md) > Validation References

# Validation References

The external sources this domain's tools are checked against, and the considerable amount they cannot check.

Kept separate from the reference lists at the foot of each document. Those are further reading; this is the material a test asserts against. The methodology is in [validation/README.md](../../validation/README.md).

| Level | Means |
|---|---|
| **Hardware** | Compared against measured or specified performance of real hardware |
| **Standard** | Reproduces a published standard or definition exactly. Catches an implementation error only |
| **Bounded** | No direct comparison, but the result is bracketed by something |
| **Unvalidated** | No external anchor. Recorded with what depends on it |

**This domain has no hardware anchor and no standard anchor**, which makes it the weakest-anchored domain in the repository. It is also the domain whose conclusions depend least on the numbers, and those two facts are related rather than coincidental.

Stated at the top because a reader is entitled to know it before reading the results.

---

## What holds regardless of the inputs

The domain's three results are structural. Each follows from an exponent, a sign or a sum, and none from a value.

**The gyro term overtakes the accelerometer term early in any flight.** An accelerometer bias integrates twice into position and grows as the square of time. A gyro bias integrates once into attitude, which tilts the accelerometers into gravity, and that integrates twice more into position, giving the cube. **A cubic overtakes a quadratic, and where it does so is the only thing the grades set.** In the worked example that is 63 seconds, and by the 540 second flight time the gyro term is 98.6 per cent of the variance.

**The governing control disturbance changes through the flight.** Aerodynamic moment is present at dynamic pressure and absent above the atmosphere, and thrust misalignment is present throughout. Any values where one term switches off give the same conclusion, which is that a gimbal sized on a single condition is sized on the wrong one for most of the ascent.

**A handful of channels carry most of the telemetry.** Twelve of ninety three carry 75 per cent, because bit rate is the product of sample rate and word length and the sample rate spans four orders of magnitude across the list. **That is a property of the measurement list**, and a framing overhead multiplies every channel equally.

**None of the three is validated and none of the three is at risk.** That is the honest position, and it is different from claiming the numbers are right.

---

## Closed forms

- **Validation level:** Standard, and exact
- **Key findings:**
  - Position error from accelerometer bias is `0.5 b t^2`, checked to scale as the square
  - Position error through tilt is `0.5 g theta_dot t^3` in effect, checked to scale as the cube
  - The variance shares sum to one
  - Trim plus manoeuvre plus reserve equals the required gimbal angle
  - Channel bit rates sum to the total, and the shares sum to one
  - The static margin is negative for every launch vehicle case, and a positive one is refused

**The refusals do more work here than the arithmetic.** [ControlAuthority](../avionicsLibrary/ControlAuthority.py) raises rather than reports a negative margin, because a vehicle that cannot trim its disturbance is lost rather than degraded. In the worked example the 8 degree gust case at max-Q is refused while the design case passes, and the gap between those two is the interesting part of the result.

---

## What is not validated

Three entries in [validation/referenceCases.py](../../validation/referenceCases.py) under `UNVALIDATED`, and each names what survives it.

**IMU grades and aiding bounds** (`imuGrades`). Bias, random walk and scale factor are representative of a sensor class rather than of any part number, and the aiding bounds depend on the receiver and the environment. Every absolute error figure scales with them. **The structural result does not**: the integration orders are fixed by the mathematics, so the crossover time moves and its existence does not. **Closable with a datasheet, and not as easily as that sounds.** The ADIS16507 was attempted through the manufacturer, two distributors and two mirrors and every route was blocked. Summaries quoting the figures exist and are not recorded here, because a summary of a document nobody read is exactly what this directory exists to keep out.

**Control disturbances** (`controlDisturbances`). Thrust misalignment, centre of gravity offset, the trim allowance and the gimbal ranges are representative. The trim angle and therefore the pass or fail verdict scale with them. **The conclusion does not**, because it rests on one term being present in one phase and absent in the other. The trim allowance of a third is explicitly a convention rather than a measurement.

**Telemetry overhead** (`telemetryOverhead`). Framing overhead and link margin are representative pending [IRIG 106 or CCSDS](StandardsIndex.md). Utilisation moves with them, and on a marginal plan the verdict moves with it. The concentration result does not.

---

## What is not modelled at all

Distinct from unvalidated, and listed because a reader should not have to infer it.

**Guidance algorithms.** Deliberately not built. They optimise a delta-V budget that [vehicleArchitecture](../../vehicleArchitecture/) already owns, and a guidance law without a trajectory integration is a formula rather than a result. The reasoning is in [GuidanceAlgorithms](GuidanceAlgorithms.md).

**Control law synthesis.** No plant model exists here. [ControlLawsAndStability](ControlLawsAndStability.md) states the margin requirements and the bending separation and synthesises nothing.

**Kalman filtering.** The estimator that fuses inertial and aiding data. [SensorsAndNavigation](SensorsAndNavigation.md) computes the unaided growth and the aided bound and does not implement the filter between them.

**Radiation environment and part rates.** Environment-specific, and [FlightComputers](FlightComputers.md) argues that the launch vehicle case and the satellite case differ by orders of magnitude in what they justify.

**Bus protocol timing.** The latency budget is a sum of assumed contributions, and the phase cost of that sum is exact. See [DataBusesAndNetworks](DataBusesAndNetworks.md).

---

## The shape of what is here

The domain was scaffolded documentation-first, and building it confirmed the reason rather than overturning it.

**Three classes were built**, and the test applied to each was whether it computes something no other domain does. Navigation drift, control authority against the disturbance set, and the telemetry bandwidth rollup all passed that test. Guidance, control synthesis and estimation all failed it, for the reasons above.

**What the domain concludes** rests on integration orders and sums, and survives every representative input being wrong.

**What it reports** rests on representative values that a real programme would replace from a datasheet, a mass properties statement and a telemetry standard. All three exist and none is a research problem.

**And what it documents** rests on standards that were not read. That is the honest weakness of this domain: [SoftwareAssurance](SoftwareAssurance.md) describes a process whose authority is entirely in the documents it names, and unlike everywhere else in this repository there is no calculation underneath to fall back on.
