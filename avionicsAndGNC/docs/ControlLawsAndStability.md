[Home](../README.md) > Control Laws and Stability

# Control Laws and Stability

## Contents

- [Overview](#overview)
- [The margins](#the-margins)
- [What the margins do not cover](#what-the-margins-do-not-cover)
- [Structural flex](#structural-flex)
- [Slosh](#slosh)
- [Gain scheduling](#gain-scheduling)
- [Why the synthesis is not here](#why-the-synthesis-is-not-here)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

The attitude control loop closes around an unstable airframe with flexible structure and sloshing propellant inside it. Each of those three is a separate stability problem and they interact.

---

## The margins

The classical requirements, and they are conventions rather than a standard this repository has read.

**Gain margin 6 dB**: the loop gain can double before instability.

**Phase margin 30 degrees**: the loop can absorb that much extra phase lag.

Both are single-number summaries of a frequency response, and both assume the system is linear and time-invariant, which a launch vehicle is neither.

---

## What the margins do not cover

This is the useful part, because a design that meets its margins and fails is the case worth understanding.

**Rate limiting.** An actuator commanded faster than it can move is a nonlinearity. The margins are linear measures and say nothing about it, and the failure is sudden. See [ActuationAndTVC](ActuationAndTVC.md), where the required rate is computed.

**Time variation.** Mass, inertia, centre of gravity, thrust and dynamic pressure all change through the flight, and a margin computed at one instant is a margin at one instant. Gain scheduling is the response and it is covered below.

**Latency.** Sensor sampling, filtering, computation and command output are all delay, and delay is phase lag proportional to frequency. **A control loop's latency budget is a phase margin budget**, and it should be written down as one rather than discovered as one.

**Saturation.** Both the actuator angle and the actuator rate saturate, and a saturated loop is open.

---

## Structural flex

The airframe bends. Its modes appear in the sensor signal, and if the control loop responds to them it drives them.

**The separation between the control bandwidth and the first bending mode is the design parameter.** A factor of five or more and the modes can be ignored; less, and they have to be handled.

The handling is a **notch filter** at the mode frequency, and the cost is phase lag at frequencies below it, which is phase margin at the control frequency, which is the thing the separation was protecting.

So a close bending mode costs control bandwidth twice: once because the loop cannot be closed above it, and again because the notch that permits closing below it eats the margin.

**The mode frequency comes from [aerospaceStructures](../../aerospaceStructures/)** and it changes through the flight as propellant drains. A notch designed for the full-tank mode is mistuned at burnout.

---

## Slosh

Liquid propellant in a partially full tank has its own modes, and the first lateral slosh mode is typically well below the structural modes and closer to the control frequency.

Two things make it harder than flex.

**The slosh mode moves a lot.** Its frequency depends on fill level, so it sweeps through a range during the burn, and a fixed notch cannot track it.

**It has mass.** A slosh mode is a significant fraction of the propellant moving, which means it is a real disturbance rather than only a sensor artefact.

The mitigations are **baffles**, which add damping and mass, and **avoiding the coupling** by keeping the control bandwidth away from the slosh range, which is not always possible.

The slosh model belongs to [fluidSystems](../../fluidSystems/) and the structural coupling to [aerospaceStructures](../../aerospaceStructures/). **This document names the interface and computes neither**, which is the honest position for a domain built for literacy.

---

## Gain scheduling

Because the plant changes through the flight, the controller does too.

**Scheduled on what** is the design decision. Time is simplest and it is open loop: a vehicle flying a dispersed trajectory is at a different condition from the one the schedule assumed. Dynamic pressure or Mach number are better and require measuring them. Mass is better still for the inertia terms and it is inferred rather than measured.

**The transitions matter.** A schedule that switches discretely introduces a transient; one that interpolates continuously does not, and interpolating between two stable controllers does not guarantee the interpolated one is stable.

---

## Why the synthesis is not here

Computing a control law needs a plant model, and the plant is the coupled system: rigid body, bending modes, slosh modes and actuator dynamics, all varying with time.

Every piece of that lives in a different domain. [aerospaceStructures](../../aerospaceStructures/) owns the modes, [fluidSystems](../../fluidSystems/) owns the slosh, [propulsion](../../propulsion/) owns the thrust, and [vehicleArchitecture](../../vehicleArchitecture/) owns the mass properties.

**Assembling them into a coupled model is a real piece of work rather than a class**, and a synthesis built on a rigid-body-only plant would be answering an easier question than the one that matters while looking like it had answered the real one.

So this domain computes the [control authority](ActuationAndTVC.md) and the actuator rate, which are requirements on the plant rather than functions of it, and it documents the rest.

---

## Design rules of thumb

- **Write the latency budget as a phase margin budget.** That is what it is.
- **Get the bending frequency from structures early**, and get it at more than one fill level.
- **Keep a factor of five between control bandwidth and the first mode** if the design allows it.
- **Expect the notch to cost what the separation was buying.**
- **Schedule on a measured quantity** where you can, and know the dispersion where you cannot.

---

## Failure modes

**A margin met and a rate limit hit.** The linear measures do not see it.

**A notch tuned at one fill level.** Mistuned for most of the burn.

**A slosh mode swept through the control bandwidth.** Fixed filters cannot track it.

**Latency discovered rather than budgeted.** It arrives as missing phase margin.

**A margin computed at one flight condition.** The plant is time-varying.

---

## References

- Greensite, *Analysis and Design of Space Vehicle Flight Control Systems*
- Wie, *Space Vehicle Dynamics and Control*
- [aerospaceStructures](../../aerospaceStructures/), for the bending modes
- [fluidSystems](../../fluidSystems/), for the slosh modes
