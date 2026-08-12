[Home](../README.md) > GSE Design

# GSE Design

## Contents

- [Overview](#overview)
- [The same equations, different constraints](#the-same-equations-different-constraints)
- [Where ground and flight genuinely diverge](#where-ground-and-flight-genuinely-diverge)
- [Pneumatics](#pneumatics)
- [Mobility and modularity](#mobility-and-modularity)
- [Why no GSE library exists here](#why-no-gse-library-exists-here)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Ground support equipment is a fluid system that happens to sit on the ground. That sentence is the whole design philosophy and the whole reason this domain has no GSE library.

---

## The same equations, different constraints

A ground half system is lines, valves, orifices, regulators, reliefs, filters and joints. Every one of those is computed in [fluidSystems](../../fluidSystems/), and the equations do not change when the hardware stops flying.

What changes is the objective function.

| | Flight | Ground |
|---|---|---|
| Mass | governs everything | almost free |
| Cost | secondary | governs |
| Wall thickness | minimum gauge | schedule pipe, oversized |
| Reconfiguration | never | constantly |
| Inspection | before flight | continuously |
| Life | one flight | decades |

**Ground hardware is heavier, cheaper and reconfigured more often**, and the design consequence is that a ground system should be built from standard components with generous margins, because the thing that will actually happen to it is being taken apart and reassembled differently.

---

## Where ground and flight genuinely diverge

Four places, and they are worth naming because they are where the shared equations stop being enough.

**Line length.** A ground run is tens or hundreds of metres against metres on a vehicle. Pressure drop, chill-down mass, thermal mass and transient response all scale with it, and a ground transient is slower and larger than the flight equivalent.

**Human access.** Ground hardware is operated, inspected and repaired by people standing next to it, sometimes with the system live. That makes isolation, lockout, relief routing and labelling design requirements rather than good practice.

**Reconfiguration.** A flight system is welded where possible. A ground system is flanged and unioned because it will be changed, and every one of those is a leak path. See [Leaks](../../fluidSystems/fluidSystemsLibrary/docs/Leaks.md).

**And duty cycle.** A flight valve cycles a handful of times. A ground valve cycles thousands, which turns seat wear and actuator life from a non-issue into the maintenance schedule.

---

## Pneumatics

The system that touches everything and gets designed last.

**Purge, actuation, pressurisation, and pneumatic control** all come off the same high pressure gas supply, and the peak demand is usually a simultaneous event nobody costed: several valves actuating during a purge while the vehicle tank is being pressurised.

**Size the storage on the peak coincident demand**, not on the sum of steady flows, and check the regulator's droop at that peak. A regulator that sags during the coincident event delivers a lower actuation pressure exactly when the most valves are moving.

**Helium is the expensive one** and it is used because it stays gaseous next to liquid hydrogen. Nitrogen does everything else and costs a fraction as much, so the split between them is a real cost decision.

---

## Mobility and modularity

A pad gets reconfigured, and skid-mounted systems are how that stays affordable.

**A skid is a tested subsystem**, which means the acceptance test happens once in a shop rather than every time on the pad. That is the main argument for modularity and it is a schedule argument rather than a cost one.

**The interfaces between skids are where the leaks are**, which is the price. See [UmbilicalsAndDisconnects](UmbilicalsAndDisconnects.md) for the same trade at the vehicle interface.

---

## Why no GSE library exists here

Stated plainly, because it is the largest scope decision in this domain.

**A GSE fluid analysis would reimplement [fluidSystems](../../fluidSystems/) with different inputs.** Line, Valve, Orifice, Regulator, Relief, Filter, Fitting, Seal, Leak and WaterHammer all apply directly to a ground system. A second implementation sized for heavier walls and lower cost would be the same equations, and having two of them is worse than having one: they drift, and nothing enforces agreement.

**What this domain adds is the integration across an operation**, which is what [PropellantLoading](PropellantStorageAndTransfer.md) does: it takes the boil-off rate from fluid systems and the chill-down mass from propulsion and totals them over a launch attempt. That is a calculation nothing else does, and it is small.

**The general rule this follows** is the one written into [BUILDOUT](../../BUILDOUT.md): an argument against duplicating a neighbouring tool is not an argument against every calculation nearby. Check what the neighbour actually computes before declining to compute anything.

---

## Design rules of thumb

- **Use the flight fluid tools on ground systems.** The equations do not change.
- **Design for reconfiguration**, because it will be reconfigured.
- **Size pneumatics on the peak coincident demand** and check regulator droop there.
- **Split helium and nitrogen deliberately.** The cost difference is large.
- **Skid-mount so acceptance happens in a shop**, then accept the interface leaks.
- **Count the flanges.** They are the leak population.

---

## Failure modes

**A second fluid library for ground hardware.** Two implementations that drift.

**Pneumatics sized on the sum of steady flows.** The coincident peak is what fails.

**A ground system designed as a flight system.** Too light, too welded, too hard to change.

**Duty cycle ignored.** Ground valves cycle thousands of times and wear.

**Flange count treated as a detail.** It is the leak rate.

---

## References

- [fluidSystems](../../fluidSystems/), which computes every component in a ground half system
- [Leaks](../../fluidSystems/fluidSystemsLibrary/docs/Leaks.md), for what a flange population costs
- [TestFacilitiesAndGSE](../../fluidSystems/fluidSystemsTesting/docs/TestFacilitiesAndGSE.md)
