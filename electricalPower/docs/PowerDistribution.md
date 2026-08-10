[Home](../README.md) > Power Distribution

# Power Distribution

## Contents

- [Overview](#overview)
- [Bus voltage](#bus-voltage)
- [Centralised against distributed](#centralised-against-distributed)
- [Switching](#switching)
- [Protection](#protection)
- [What happens on a short](#what-happens-on-a-short)
- [Load shedding](#load-shedding)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Distribution is where the power architecture becomes hardware. Most of the decisions are topology rather than sizing, which is why this document is longer than the class behind it.

---

## Bus voltage

The one distribution decision with a computable answer, and it is in [HarnessDesign](HarnessDesign.md): **copper falls roughly with the square of bus voltage**, and on the reference harness a 12 V bus does not close at all.

What pushes back:

**Insulation, creepage and clearance** grow with voltage, and in a partial vacuum they grow faster. The Paschen minimum sits in the range a launch vehicle passes through on ascent, so a bus that is safe at sea level and in vacuum can arc in between. **That is an ascent-specific hazard and it has no analogue in ground equipment.**

**Component availability.** A 28 V ecosystem exists; a 100 V one is narrower and more expensive.

**Single-fault energy.** A higher bus delivers more energy into a fault before protection acts.

28 V is the launch vehicle default for historical reasons and it is a reasonable answer for a short vehicle. A long one should ask the question again.

---

## Centralised against distributed

**Centralised switching** puts all the switches in one box. Fewer boxes, simpler qualification, and every load's current runs the full length of the vehicle, which is harness mass through the [voltage drop](HarnessDesign.md) constraint.

**Distributed switching** puts switches near the loads and runs a single high-current feed. Far less harness, and more boxes to qualify, more connectors, and a distribution network that has to be commanded rather than wired.

The trade is harness mass against box count and connector count, and **connector count is the reliability proxy**, so it is not a pure mass trade.

On a long vehicle the harness saving usually wins. On a short one it usually does not.

---

## Switching

**Relays** are simple, have a genuine open circuit when off, and have a contact life and a coil holding current. A latching relay removes the holding current at the cost of a state that survives a power interruption, which is either a feature or a hazard depending on the load.

**Solid state switches** have no contact wear, switch fast, and never fully open: leakage current matters where the load is an ordnance circuit, which is why [pyro circuits](PyroCircuits.md) use mechanical interruption rather than a transistor.

**Both need a flyback path** on an inductive load. See [ValveAndActuatorDrive](ValveAndActuatorDrive.md).

---

## Protection

Three approaches with different failure behaviour.

**Fuses** are simple, non-resettable, and their clearing time depends on the fault current, which depends on the source impedance. A fuse that does not clear because the fault current is too low is a fuse that is not protecting anything.

**Circuit breakers** are resettable and heavier.

**Current-limited switches** limit rather than interrupt, which keeps the bus up and leaves the fault energised. That is right for a fault that might clear and wrong for one that will not.

**Coordination** is the part that is easy to get wrong: a downstream device has to clear before an upstream one, across the whole range of credible fault currents. That needs a source impedance model.

**This library does not model any of it**, and the reason is that source impedance: the battery's internal resistance, the harness resistance to the fault, and the switch behaviour all matter, and the first is a cell characteristic this domain does not carry. See [ValidationReferences](ValidationReferences.md).

---

## What happens on a short

Worth walking through because it is the case the architecture is judged on.

**The bus voltage collapses** toward the fault, and every load on it sees the sag. Whether they ride through depends on their input capacitance and their undervoltage behaviour. See [PowerQuality](PowerQuality.md).

**The fault current is set by the source impedance**, not by the load. A low-impedance battery delivers a very large current into a bolted fault.

**Protection acts, or does not.** A fault at the far end of a long harness may draw less current than the same fault at the distribution unit, because the harness resistance limits it, and that is the case where a fuse fails to clear.

**The remaining loads recover, or do not.** A load that dropped out during the sag and does not restart itself is a mission failure caused by a fault it was not part of.

That last one is the reason isolation matters more than protection: **the goal is not to survive the fault, it is to keep the fault's consequences inside the faulted branch.**

---

## Load shedding

Shedding is a design decision made in advance and executed under a condition nobody wants to be in.

**What sheds first** should be the load whose loss is recoverable, and that is a mission question rather than an electrical one. Heaters shed before avionics; telemetry sheds before guidance.

**Automatic against commanded.** Automatic shedding is fast and can be wrong. Commanded shedding needs a link and a decision, which a launch vehicle in ascent does not have time for.

**The reason it is here at all** is the energy budget: a battery sized with margin and a mission that runs long is exactly the case where shedding buys the remaining objectives.

---

## Design rules of thumb

- **Ask the bus voltage question if the vehicle is long.** 28 V is a default, not an answer.
- **Check the Paschen range.** A bus safe at sea level and in vacuum can arc on ascent.
- **Trade harness mass against connector count**, not against box mass alone.
- **Coordinate protection across the fault current range**, not at one value.
- **Design isolation before protection.** Keeping the consequence local matters more.
- **Decide the shed order early**, because it is a mission decision.

---

## Failure modes

**A fuse that does not clear.** Fault current limited by the harness rather than the source.

**A solid state switch on an ordnance circuit.** It never fully opens.

**A load that drops out on a sag and does not restart.** A fault it was not part of.

**Protection coordinated at one fault current.** The range is what matters.

**A latching relay in an unexpected state after a power interruption.** Feature or hazard, and the design has to have decided which.

---

## References

- [HarnessDesign](HarnessDesign.md), for the bus voltage against copper result
- [PowerQuality](PowerQuality.md), for what a sag does to the loads
- [PyroCircuits](PyroCircuits.md), for why ordnance uses mechanical interruption
- MIL-STD-704, *Aircraft Electric Power Characteristics*, not read here
