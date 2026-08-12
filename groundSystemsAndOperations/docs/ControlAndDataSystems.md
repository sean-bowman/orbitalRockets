[Home](../README.md) > Control and Data Systems

# Control and Data Systems

## Contents

- [Overview](#overview)
- [What the ground control system is](#what-the-ground-control-system-is)
- [Interlocks](#interlocks)
- [Command paths and authority](#command-paths-and-authority)
- [Recording](#recording)
- [Displays](#displays)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

The ground control system operates every valve, reads every transducer, enforces every interlock and records what happened. It is the least glamorous system on the pad and the one whose failure most reliably ends a countdown.

---

## What the ground control system is

Architecturally it is a real-time control system with a supervisory layer, and the split matters.

**The real-time layer** holds the interlocks and the sequences that have to run on time. It is deterministic, it is simple, and it keeps working when the supervisory layer does not.

**The supervisory layer** holds the displays, the operator commands and the recording. It is where the complexity is and where the changes happen.

**The safety-critical logic belongs in the layer that does not change**, which is the same argument [avionics](../../avionicsAndGNC/docs/FlightComputers.md) makes about flight software, and for the same reason.

---

## Interlocks

An interlock prevents a command from being executed when the state is wrong.

**In hardware where it matters most.** A software interlock is one bug away from not existing, and the highest-consequence ones, ordnance arming and the flight termination safe-and-arm chain, are wired.

**A defeated interlock is a configuration change**, tracked and reviewed, not a switch somebody flips during a test. The commonest way an interlock fails is not that it broke, it is that it was bypassed for a reason that made sense at the time and never restored.

**And an interlock that fires often is a design problem.** Operators learn to expect it, then work around it, and at that point it has stopped being a control.

---

## Command paths and authority

Two things: what can send a command, and who is allowed to.

**Every commandable device should have exactly one authoritative path** during an operation. Two paths to the same valve is two sources of truth about its position.

**Local control exists for maintenance and it has to be locked out during operations**, because the failure mode is a technician at a local panel and an operator at a console commanding the same valve in opposite directions.

**Authority is procedural rather than technical** and it belongs with the console structure in [LaunchOperations](LaunchOperations.md): anybody can call a hold and one person resumes.

---

## Recording

**Telemetry you did not record is data you do not have, and you find out after the failure.** That is true on the ground with more force than in flight, because ground bandwidth is nearly free and there is no excuse.

**Record everything, at rate, always.** The ground system has no downlink constraint, no mass constraint and no power constraint. The only argument against recording a channel is storage, and storage is the cheapest thing on the pad.

**Record the commands as well as the measurements.** Reconstructing a sequence from measurements alone means inferring what was commanded, and the difference between commanded and achieved is exactly what an investigation needs.

**Timestamp everything from one clock.** Two clocks means two versions of what happened first, and causality is what an investigation is trying to establish.

**And keep it.** A recording that is overwritten on the next run is a recording that exists only until it is needed.

---

## Displays

Worth a section because it is where operator error is designed in or out.

**Show state, not just value.** A number without its limits is a number the operator has to remember the limits for.

**Make the abnormal obvious and the normal quiet.** A display where everything is coloured is a display where nothing is.

**Show what was commanded next to what was achieved.** The disagreement is the fault.

**And design the display for the worst minute**, not for the ninety nine quiet ones. The layout that reads well during a nominal count and badly during an anomaly is the wrong layout.

---

## Design rules of thumb

- **Split real-time from supervisory** and put the safety logic in the layer that does not change.
- **Wire the highest-consequence interlocks.**
- **Track every interlock defeat as a configuration change.**
- **One authoritative command path per device during an operation.**
- **Record everything at rate, commands included, on one clock, and keep it.**
- **Design displays for the worst minute.**

---

## Failure modes

**Safety logic in the layer that changes weekly.** It will change.

**An interlock bypassed for a good reason and never restored.** The commonest interlock failure.

**An interlock that fires routinely.** Operators route around it and it stops being a control.

**Two command paths to one valve.** Two sources of truth about its position.

**Measurements recorded without commands.** The investigation has to infer half of it.

**Two clocks.** Two versions of what happened first.

---

## References

- [Instrumentation](../../fluidSystems/fluidSystemsLibrary/docs/Instrumentation.md), for what is being measured
- [FlightComputers](../../avionicsAndGNC/docs/FlightComputers.md), for the same architectural argument in flight
- [LaunchOperations](LaunchOperations.md), for the console structure
