[Home](../README.md) > Data Buses and Networks

# Data Buses and Networks

## Contents

- [Overview](#overview)
- [What a flight bus has to be](#what-a-flight-bus-has-to-be)
- [The families](#the-families)
- [Determinism](#determinism)
- [Fault containment](#fault-containment)
- [Timing and latency](#timing-and-latency)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

The data bus is the shared resource that everything on the vehicle depends on, which makes it simultaneously the most convenient piece of the architecture and the most dangerous.

---

## What a flight bus has to be

Four properties, and commercial buses generally provide the first two.

**Reliable in the environment**, which is vibration, temperature and EMI. See [electricalPower EMIAndEMC](../../electricalPower/docs/EMIAndEMC.md).

**Fast enough**, which for a launch vehicle is a low bar. The control loop needs kilobits and the [telemetry](TelemetryAndInstrumentation.md) needs megabits, and neither is difficult.

**Deterministic**, which is the hard one and is covered below.

**Fault containing**, which is the one commercial buses are worst at.

---

## The families

**Command-response**, such as MIL-STD-1553. A bus controller polls each terminal in a fixed sequence, so the timing is completely deterministic and the controller is a single point of control. Slow by modern standards, extremely well understood, and the determinism is architectural rather than statistical.

**Broadcast serial**, such as CAN. Cheap, robust, widely available, and its arbitration is priority-based, which means a low-priority message has a latency that depends on what else is talking. Determinism holds for the highest-priority traffic and degrades below it.

**Switched networks**, such as Ethernet variants with time-triggered or scheduled extensions. Fast, flexible, and their determinism comes from the schedule rather than from the medium, so it is only as good as the configuration.

**Point to point** for anything that cannot tolerate sharing, which usually means the actuator command and the safety-critical discretes.

---

## Determinism

The property that separates a flight bus from an office one.

**A deterministic bus delivers a message in a bounded time, every time.** Not on average, not usually: bounded.

That matters because the control loop has a fixed period, and a message that arrives late is a message that missed its cycle. On an unstable airframe a missed cycle is a control outage, and the loop's phase margin is being spent on transport delay. See [ControlLawsAndStability](ControlLawsAndStability.md).

**Average latency is not the specification. Worst case latency is**, and a bus characterised by its average is uncharacterised for this purpose.

---

## Fault containment

The failure mode that makes a shared bus dangerous.

**A babbling node** transmits continuously and denies the bus to everything else. On a bus with no guardian this takes down every subsystem regardless of their own health, which converts one component failure into a vehicle failure.

The responses are a **bus guardian** that enforces each node's transmission slot, physically separate buses for independent functions, and point-to-point links for anything that must not be denied.

**Three flight computers on one bus is one flight computer**, as far as that failure mode is concerned. See [FlightComputers](FlightComputers.md).

---

## Timing and latency

The chain that a control command traverses, and every link is delay.

Sensor sampling, sensor filtering, bus transport to the computer, computation, bus transport to the actuator, actuator response.

**Add them up and write the total down as a phase margin cost**, because that is what it is. A 30 degree phase margin at 1 Hz is about 83 ms of allowable delay, and a chain of six links each taking 10 ms has spent three quarters of it.

**Jitter is worse than latency.** A constant delay is a phase lag the controller can be designed around; a varying one cannot be, and it has to be budgeted at its worst case, which means the design pays for the jitter as though it were always present.

---

## Design rules of thumb

- **Specify worst case latency, not average.**
- **Budget the whole chain**, sensor to actuator, and convert it to phase.
- **Prefer a constant delay to a smaller varying one.**
- **Fit a bus guardian, or separate the buses.** A babbling node takes everything.
- **Keep safety-critical commands off the shared bus.**

---

## Failure modes

**A bus specified on average latency.** Uncharacterised for a control loop.

**A babbling node with no guardian.** One failure denies the whole vehicle.

**Redundant computers on a single bus.** The redundancy count is one.

**Jitter budgeted at its average.** The design pays worst case regardless.

**Latency discovered at integration.** It arrives as missing phase margin.

---

## References

- MIL-STD-1553, *Digital Time Division Command/Response Multiplex Data Bus*, not read here
- [ControlLawsAndStability](ControlLawsAndStability.md), for the phase cost of delay
- [FlightComputers](FlightComputers.md), for the shared resource argument
