[Home](../README.md) > Umbilicals and Disconnects

# Umbilicals and Disconnects

## Contents

- [Overview](#overview)
- [What crosses the interface](#what-crosses-the-interface)
- [The three ways to separate](#the-three-ways-to-separate)
- [Separation force](#separation-force)
- [Retract](#retract)
- [Contingency reconnect](#contingency-reconnect)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

The umbilical is the last thing connecting the vehicle to the ground and the first thing that has to stop. **The interface is where the problems are**, and it earns disproportionate attention because a failure here is a launch failure at T-0 rather than a maintenance item.

---

## What crosses the interface

More than people expect, and each has its own failure mode.

**Propellant fill and drain**, at full transfer rate, cryogenic. The largest connection and the one whose disconnect matters most.

**Pressurant and purge**, at high pressure and low flow.

**Vent and relief return**, which is where boil-off goes and which has to stay connected until the last moment.

**Electrical power**, so the vehicle runs on ground power until it does not. See [electricalPower](../../electricalPower/).

**Command and telemetry**, hardline until the vehicle goes to radio.

**Conditioned air or nitrogen** to the payload and the avionics bays, which usually flows until seconds before release.

**Each of those is a leak path, a heat leak and a schedule item**, and the count of them is a good proxy for how long an integration takes.

---

## The three ways to separate

**Fly-away** relies on vehicle motion to pull the connector apart. Simple, no actuator, and the separation happens exactly when the vehicle moves. It puts a load into the vehicle and it demands that the disconnect be reliable in one direction under a load nobody controls precisely.

**Retract before release** pulls the umbilical clear on a command, before or at ignition. It removes the load from the vehicle and it introduces a mechanism that has to work on time, every time, with no retry.

**Drop-away** uses a hinge or a lanyard so the mass falls clear under gravity. Between the two, and common for lightweight electrical connections.

**The choice is a trade between a load and a mechanism**, and the answer usually differs by line: the big cryogenic disconnects retract, the small electrical ones fly away.

---

## Separation force

Two contributions and the second is the one that surprises.

**Mechanical.** Detent, latch, spring, and the friction of the seal faces.

**Pressure area.** A pressurised disconnect is being pushed apart by the pressure across its own seal area, and that force can dominate. **A disconnect at flight pressure separates differently from one at ambient**, which is why depressurising before separation is a sequence decision rather than a convenience.

The pressure area calculation is a [Fitting](../../fluidSystems/) problem and lives in fluid systems. The spring and mass of the retract are a [mechanismsAndSeparation](../../mechanismsAndSeparation/docs/SpringsAndEnergyStorage.md) problem. **Neither is recomputed here**, which is the boundary this domain draws.

---

## Retract

The requirement is a race and it is worth writing as one.

**The umbilical has to be clear before the vehicle reaches it.** Vehicle rise is quadratic in time from a standing start and the retract is roughly linear, so the margin is early and the failure is late.

**The retract has to survive the acoustic and thermal environment** it is retracting through, which is the worst environment on the pad.

**And it has to fail safe.** A retract that does not fire leaves hardware in the vehicle path. The usual answer is a mechanical backup that fly-away separation will clear, which makes the retract an improvement rather than a dependency.

---

## Contingency reconnect

The requirement people design last and need first.

**A scrub after tanking needs a detank**, which needs the fill connection intact or reconnectable. If the umbilical has already retracted, someone has to reconnect it next to a loaded vehicle.

**That is a hazardous operation** with a loaded vehicle in the loop, and it is why the sequence keeps the propellant connections until as late as possible and why the retract is usually the last thing in the count rather than a convenient early one.

**Design for the detank, not just for the launch.** In the worked example a scrub after tanking costs 0.96 flight loads, and all of it has to come back out through this interface. See [PropellantStorageAndTransfer](PropellantStorageAndTransfer.md).

---

## Design rules of thumb

- **Count the crossings.** Each is a leak path, a heat leak and a schedule item.
- **Choose separation by line**, not for the whole umbilical at once.
- **Include pressure area in the separation force.** It often dominates.
- **Retract the big cryogenic lines last.** The detank needs them.
- **Make the retract an improvement over fly-away**, not a dependency.
- **Design the reconnect before you need it**, next to a loaded vehicle.

---

## Failure modes

**Separation force computed from the latch alone.** Pressure area can dominate.

**A retract with no mechanical backup.** Hardware in the vehicle path.

**Propellant connections retracted early.** The detank has nowhere to go.

**A reconnect procedure written after the first scrub.** Written under the worst conditions available.

**A connector count that grows through integration.** Every one is a schedule item and they accumulate quietly.

---

## References

- [FittingsAndConnectors](../../fluidSystems/fluidSystemsLibrary/docs/FittingsAndConnectors.md), for the pressure area force
- [SpringsAndEnergyStorage](../../mechanismsAndSeparation/docs/SpringsAndEnergyStorage.md), for the retract
- [PropellantStorageAndTransfer](PropellantStorageAndTransfer.md), for why the detank governs the sequence
