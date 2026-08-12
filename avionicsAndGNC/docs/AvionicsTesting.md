[Home](../README.md) > Avionics Testing

# Avionics Testing

## Contents

- [Overview](#overview)
- [The ladder](#the-ladder)
- [Hardware in the loop](#hardware-in-the-loop)
- [Day in the life](#day-in-the-life)
- [What integration catches](#what-integration-catches)
- [What nothing catches](#what-nothing-catches)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Avionics is the one subsystem that can be tested almost completely before flight, because its inputs can be simulated. Almost is doing a lot of work in that sentence.

---

## The ladder

Each rung tests something the one below cannot.

**Unit test** exercises a function against its requirement, on a workstation.

**Software in the loop** runs the flight software against a simulated vehicle, on a workstation. Fast, cheap, and it does not test the target processor or its timing.

**Processor in the loop** runs the real compiled software on the real processor against a simulated vehicle. **This is where timing and numerical behaviour first become real**, and where a floating point difference between the workstation and the target shows up.

**Hardware in the loop** adds the real sensors, actuators and buses.

**Integrated vehicle test** adds the rest of the vehicle.

**Day in the life** runs the whole thing through a complete mission timeline.

---

## Hardware in the loop

The rung that earns the most, because it is the first one where the real interfaces exist.

The simulation computes the vehicle state, drives the sensors or their electrical equivalents, reads the actuator commands and closes the loop. **The flight hardware does not know it is not flying**, which is exactly the property that makes the test worth having.

Three things it catches that nothing below it does.

**Timing.** Bus latency, scheduling jitter and the actual loop period, against the budget in [DataBusesAndNetworks](DataBusesAndNetworks.md).

**Interface errors.** Scaling, sign conventions, units and endianness. **A sign error in a control loop is a divergence**, and it is caught here in an afternoon or in flight once.

**Actuator dynamics.** The real actuator has a rate limit and a lag, and the simulation's model of it was an assumption. See [ActuationAndTVC](ActuationAndTVC.md).

---

## Day in the life

Running the full mission timeline, in order, at rate, with the real hardware.

It catches what only sequence catches: mode transitions that work individually and not in order, a state left set by an earlier phase, a resource that was not released, a counter that overflows only after the eighth minute.

**Most of the flight software complexity is in mode management**, as [GuidanceAlgorithms](GuidanceAlgorithms.md) notes, and mode management is exactly what a sequence test exercises and a unit test does not.

---

## What integration catches

The findings that repeat across programmes, which is the useful list.

**Sign and scaling errors** at every interface. The most common finding and the cheapest to fix at this stage.

**Timing that was budgeted and not measured.** See [ControlLawsAndStability](ControlLawsAndStability.md): latency is phase margin.

**Grounding and EMI interactions**, because this is the first time the real harness exists. See [electricalPower](../../electricalPower/docs/EMIAndEMC.md).

**Startup and initialisation order**, which nothing below integration exercises.

**Assumptions two teams made differently**, which is the class of finding that justifies integration testing existing at all.

---

## What nothing catches

Stated because a complete-looking test programme is the dangerous kind.

**A wrong requirement.** Correctly implemented, thoroughly verified, and flown. See [SoftwareAssurance](SoftwareAssurance.md).

**An environment outside the simulation.** The simulation contains what somebody modelled, and the flight contains everything.

**A dispersion combination not run.** The space is too large to cover and the runs are chosen, which means somebody chose not to run the one that mattered.

**Something that only happens once.** A [separation event](../../mechanismsAndSeparation/), a hard start, a structural transient. Those are simulated or they are not tested.

---

## Design rules of thumb

- **Get to processor in the loop early.** Timing and numerics become real there.
- **Run day in the life before flight**, in order and at rate.
- **Check every interface sign and scaling explicitly.** It is the most common finding.
- **Measure the latency, do not assume it.**
- **Record the dispersions you did not run**, so the coverage gap is visible.

---

## Failure modes

**Simulation-only verification.** The target processor is part of the system.

**Mode transitions tested individually.** The order is what fails.

**A sign error found in flight.** An afternoon on a bench, once in flight.

**Latency budgeted and never measured.** Arrives as missing phase margin.

**A complete-looking test programme.** The dangerous kind, because it stops the search.

---

## References

- [DataBusesAndNetworks](DataBusesAndNetworks.md), for the timing this measures
- [SoftwareAssurance](SoftwareAssurance.md), for what verification cannot reach
- [fluidSystemsTesting](../../fluidSystems/fluidSystemsTesting/), for the campaign philosophy
