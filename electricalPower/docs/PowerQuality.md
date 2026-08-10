[Home](../README.md) > Power Quality

# Power Quality

## Contents

- [Overview](#overview)
- [The four disturbances](#the-four-disturbances)
- [Where they come from](#where-they-come-from)
- [Undervoltage and brownout](#undervoltage-and-brownout)
- [The restart problem](#the-restart-problem)
- [What this domain computes](#what-this-domain-computes)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Power quality is what the bus actually looks like at a load, as opposed to what the specification says. It matters because most electrical failures in integration are quality failures rather than capacity failures.

---

## The four disturbances

**Steady-state tolerance**: the bus is not at its nominal voltage. It sags as the battery discharges and as load current rises through the [harness resistance](HarnessDesign.md).

**Ripple**: periodic variation from switching regulators and from pulse-width modulated loads.

**Transients**: short excursions from switching, inrush and [flyback](ValveAndActuatorDrive.md).

**Interruption**: the bus goes away briefly, from a switchover or a fault.

They need different mitigations and a load specified only against the first will meet its specification and still fail.

---

## Where they come from

Mostly from the vehicle itself, which is why this is a self-compatibility problem.

**Battery internal resistance** turns every current step into a voltage step, and it rises as the battery discharges and as it gets cold. **The worst power quality is at the end of the mission on a cold pack**, which is also when the margins are thinnest.

**Harness resistance** does the same thing distributed along the vehicle, so two loads on the same feed disturb each other through a shared impedance. That is the electrical analogue of the ground loop in [GroundingAndBonding](GroundingAndBonding.md), and the fix is the same: separate the paths.

**Inrush** from a motor start or several valves actuating together. See [ValveAndActuatorDrive](ValveAndActuatorDrive.md).

**Flyback** from an inductive load being switched off, which is a transient in the other direction.

---

## Undervoltage and brownout

The dangerous region is not zero volts, it is the range between working and off.

A digital device below its minimum operating voltage and above its reset threshold can execute incorrectly rather than stopping: a processor that browns out can write to memory, command an output, or hang in a state its watchdog does not catch.

**That is why a brownout detector is not the same as an undervoltage lockout.** The first tells the software something is wrong; the second holds the device in reset until the supply is good, which is the behaviour that is actually safe.

**Specify the behaviour, not just the tolerance.** A load specified as "28 V plus or minus 10 per cent" has said nothing about what it does at 20 V, and 20 V is the condition it will see.

---

## The restart problem

The failure that costs missions is not the sag, it is what happens afterwards.

A load that drops out during a transient and does not restart itself has converted a recoverable disturbance into a permanent failure, and it may have been caused by a fault in a completely different branch.

Three things make it worse: a device that needs a command to restart, a device whose restart draws a large inrush that causes another sag, and a set of devices that all restart simultaneously and do it together.

**Staggered restart is a design feature**, and on a vehicle it usually has to be automatic because there is no time to command it.

---

## What this domain computes

Honestly, very little of the above.

[HarnessSizing](HarnessDesign.md) computes the steady-state drop, which is the first of the four disturbances and the only one with a clean answer here. [SolenoidDrive](ValveAndActuatorDrive.md) computes the inrush time constant and the flyback energy, which are sources rather than bus responses.

**The bus response needs a source impedance model**, including the battery's internal resistance and its variation with state of charge and temperature, and this domain does not carry one. That is the same gap that stops it modelling [fault current and protection coordination](PowerDistribution.md), and it is registered in [ValidationReferences](ValidationReferences.md).

**A cell datasheet would close it**, which makes this one of the more tractable gaps in the repository.

---

## Design rules of thumb

- **Specify behaviour, not just tolerance.** What does the load do at 20 V.
- **Use undervoltage lockout, not just brownout detection.** Held in reset is the safe state.
- **Check power quality at end of mission on a cold pack.** That is the worst case.
- **Separate feeds for loads that disturb each other**, because shared impedance couples them.
- **Make restart automatic and staggered.** Simultaneous restart causes the next sag.

---

## Failure modes

**A load specified only on steady-state tolerance.** Meets its specification and fails on a transient.

**A processor operating through a brownout.** Executes incorrectly rather than stopping.

**A load that drops out and waits for a command.** A recoverable disturbance made permanent.

**Simultaneous restart after a sag.** Causes the next one.

**Two sensitive loads sharing a feed with a switching one.** Coupled through the harness resistance.

---

## References

- MIL-STD-704, *Aircraft Electric Power Characteristics*, not read here
- [PowerDistribution](PowerDistribution.md), for the fault case
- [ValveAndActuatorDrive](ValveAndActuatorDrive.md), for the transient sources
- [BatteriesAndStorage](BatteriesAndStorage.md), for the source impedance that is not modelled
