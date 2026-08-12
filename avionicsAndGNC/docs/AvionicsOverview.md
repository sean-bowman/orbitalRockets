[Home](../README.md) > Avionics Overview

# Avionics Overview

## Contents

- [Overview](#overview)
- [What the domain found](#what-the-domain-found)
- [What was built and what was not](#what-was-built-and-what-was-not)
- [The interfaces](#the-interfaces)
- [Document index](#document-index)
- [Design rules of thumb](#design-rules-of-thumb)
- [References](#references)

---

## Overview

The vehicle's nervous system: flight computers and their redundancy, the sensor suite, guidance and navigation, control laws and actuation, and the data systems that carry it all.

This domain was scaffolded **documentation-first**, and the reasoning was that the trajectory and control algorithm work overlaps material that already exists, and a library here would duplicate rather than add. That reasoning held for most of it and not for all of it, and the section below says which.

**The goal is architectural literacy**: enough to understand the interfaces, ask the right questions, and know what an avionics team needs from the fluid and structural side.

---

## What the domain found

Three results, and they share a shape.

**The navigation error is the gyroscope, not the accelerometer.** An attitude error tilts the accelerometer triad, so gravity leaks into the horizontal channel. That path grows as the **cube** of time while accelerometer bias grows as the square, and on a tactical grade unit the two cross at about 63 seconds. Most launch vehicle flights are on the gyro side of that. See [SensorsAndNavigation](SensorsAndNavigation.md).

**The disturbance that sizes the gimbal changes through the flight.** Thrust misalignment is present the whole burn and largest when the thrust is largest; the aerodynamic term exists only in the atmosphere and dominates when it does. A gimbal sized on one condition is sized on the wrong one for most of the flight. See [ActuationAndTVC](ActuationAndTVC.md).

**Twelve channels out of ninety-three are three quarters of the telemetry bandwidth.** The high-rate structural measurements dominate everything else combined, which is where a cut has to come from and is exactly the group an investigation needs. See [TelemetryAndInstrumentation](TelemetryAndInstrumentation.md).

**In every one of the three, the quantity that dominates is not the quantity that gets specified.** The accelerometer is specified and the gyroscope decides. The aerodynamic case is analysed and the thrust misalignment is continuous. The channel count is negotiated and the sample rate spends the bandwidth.

That is a useful shape for a domain built for literacy rather than authority: **it says which question to ask**, which is what somebody outside the discipline actually needs.

---

## What was built and what was not

Three classes, and the test applied to each was whether it computes something no other domain does.

**Built:**

| Class | Why nothing else computes it |
|---|---|
| `NavigationDrift` | No other domain has a sensor |
| `ControlAuthority` | Structures has the loads and propulsion has the thrust; neither closes the attitude loop |
| `TelemetryBudget` | Nothing else allocates bandwidth |

**Not built, each for a stated reason:**

**Guidance algorithms.** Closed-loop targeting and ascent guidance duplicate the conceptual vehicle design work, and [vehicleArchitecture](../../vehicleArchitecture/) already owns the delta-V budget they would be optimising against.

**Control law synthesis.** Gain scheduling and margin computation need a plant model: rigid body, bending modes, slosh modes and actuator, coupled. [aerospaceStructures](../../aerospaceStructures/) owns the modes and [fluidSystems](../../fluidSystems/) owns the slosh, and assembling a coupled model from them is a real piece of work rather than a class.

**Kalman filtering and sensor fusion.** The error models here are what a filter would consume. Implementing the filter would be implementing an estimator whose tuning is the entire engineering content.

**Radiation single event effects.** A parts and environment question.

**Flight software assurance.** A process, documented in [SoftwareAssurance](SoftwareAssurance.md) and not modelled.

---

## The interfaces

The reason to understand this domain from outside is the interfaces, and there are four that matter.

**To [fluidSystems](../../fluidSystems/)**: every valve command and every transducer reading. The avionics decides when a valve moves and the fluid system decides what happens when it does, and the sequencing between them is where [ignitionAndStart](../../propulsion/ignitionAndStart/) lives.

**To [aerospaceStructures](../../aerospaceStructures/)**: the bending modes. A control loop closing near a structural mode couples to the airframe, and the fix is a notch filter that costs phase margin at the control frequency. **That is a structures number the control engineer needs and a control constraint the structures engineer creates.**

**To [electricalPower](../../electricalPower/)**: the harness, the grounding scheme and the EMI environment, all shared.

**To [mechanismsAndSeparation](../../mechanismsAndSeparation/)**: the sequence, the firing commands and the separation events the navigation has to survive.

---

## Document index

| Document | Covers |
|---|---|
| [FlightComputers](FlightComputers.md) | Redundancy, voting, the harder problem of deciding who is right |
| [SensorsAndNavigation](SensorsAndNavigation.md) | IMU error models, the cubic term, aiding, alignment |
| [GuidanceAlgorithms](GuidanceAlgorithms.md) | Ascent guidance, targeting, abort logic, and what is not modelled |
| [ControlLawsAndStability](ControlLawsAndStability.md) | Margins, gain scheduling, flex and slosh coupling |
| [ActuationAndTVC](ActuationAndTVC.md) | Disturbances, gimbal angle, actuator rate, RCS |
| [DataBusesAndNetworks](DataBusesAndNetworks.md) | Bus selection, determinism, fault containment |
| [TelemetryAndInstrumentation](TelemetryAndInstrumentation.md) | Measurement lists, sample rates, recording strategy |
| [SoftwareAssurance](SoftwareAssurance.md) | Process, verification, coding standards, autocoding |
| [AvionicsTesting](AvionicsTesting.md) | HIL, day-in-the-life, and what integration catches |
| [StandardsIndex](StandardsIndex.md) | The standards, and the ones not read |
| [ValidationReferences](ValidationReferences.md) | Exact integration laws and three gaps |

---

## Design rules of thumb

- **Buy the gyroscope, not the accelerometer**, on anything flying longer than about a minute.
- **Check the governing disturbance at more than one flight condition.** It changes.
- **Budget the actuator rate, not just the angle.** Rate limiting is a nonlinearity the margins do not describe.
- **Ask structures for the bending frequency early.** It constrains the control bandwidth.
- **Record more than you downlink.** They fail in opposite ways.

---

## References

- [ValidationReferences](ValidationReferences.md)
- Titterton and Weston, *Strapdown Inertial Navigation Technology*
- Greensite, *Analysis and Design of Space Vehicle Flight Control Systems*
- Wie, *Space Vehicle Dynamics and Control*
