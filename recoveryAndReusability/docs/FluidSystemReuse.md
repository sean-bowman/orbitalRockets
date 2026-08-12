[Home](../README.md) > Fluid System Reuse

# Fluid System Reuse

## Contents

- [Overview](#overview)
- [What a flight does to a fluid system](#what-a-flight-does-to-a-fluid-system)
- [Seals](#seals)
- [Valves](#valves)
- [Contamination](#contamination)
- [Can it be re-cleaned in place](#can-it-be-re-cleaned-in-place)
- [Pressure vessels](#pressure-vessels)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

The fluid system is where reuse gets expensive, because it is the system whose condition is hardest to establish without opening it, and opening it is what makes it dirty.

---

## What a flight does to a fluid system

Four things, and they are not equally reversible.

**Thermal cycling.** A cryogenic system goes from ambient to 20 K and back on every flight, and every joint, seal and bellows sees the full excursion. See [CryogenicSystems](../../fluidSystems/fluidSystemsLibrary/docs/CryogenicSystems.md).

**Pressure cycling.** Every vessel and line sees a full pressure cycle, which is a fracture life consumption rather than a fatigue one on a composite overwrapped vessel.

**Vibration and shock**, which loosens what is not positively retained and fretting-wears what is.

**And contamination**, which is the one that accumulates rather than cycling. Combustion products, ablation debris, atmospheric ingestion during entry, and salt if the vehicle landed at sea.

**The first three are cycles and the fourth is a state**, and that difference is why contamination is the harder problem: a cycle count can be tracked and a contamination state has to be measured or assumed.

---

## Seals

The component most affected by reuse and the cheapest to replace, which is a fortunate combination.

**An elastomer seal takes a compression set** and does not fully recover, and cryogenic exposure accelerates it. A seal that sealed on the first flight may not on the fifth, and there is no inspection short of removing it that establishes whether it will.

**So static seals are usually replaced rather than inspected**, which is the [replacement policy](RefurbishmentProcess.md) argument in its cleanest form: inspection costs more than replacement and discriminates worse.

**A dynamic seal is different**, because it wears rather than setting, and wear can sometimes be inferred from leakage. That makes on-condition viable where it is not for a static seal.

**And every seal replaced is a joint reopened**, which needs a leak check afterwards. See [Leaks](../../fluidSystems/fluidSystemsLibrary/docs/Leaks.md). The cost of a seal is the leak check, not the seal.

Material behaviour is in [Seals](../../fluidSystems/fluidSystemsLibrary/docs/Seals.md), which this domain does not duplicate.

---

## Valves

The component where condition is hardest to establish and where a functional test does most of the work.

**A valve that cycles correctly probably is correct**, which is more than can be said for most components, and it is why functional testing is the backbone of a fluid system turnaround.

**What a functional test does not catch** is a seat that is degrading but still seals, a solenoid whose pull-in margin has fallen, and a soft goods item partway through its life. Those need either a measurement, such as pull-in voltage or closing time, or a replacement interval.

**Measure the margins, not just the outcome.** A solenoid that closes is a pass; a solenoid that closes at 80 per cent of its rated pull-in voltage against 60 per cent when new is a trend, and a trend is what predicts the flight where it does not close. See [ValveAndActuatorDrive](../../electricalPower/docs/ValveAndActuatorDrive.md).

---

## Contamination

The accumulating problem.

**Combustion products and ablation debris** come back through the system during shutdown transients and after. **Atmospheric ingestion** happens during entry on any system that is not positively pressurised. **Salt** arrives with a water landing and is the reason a splashdown recovery has a refurbishment problem where a propulsive one has a propellant problem.

**Contamination migrates.** Debris generated in one part of the system ends up in the filters, the orifices and the valve seats of another, which is why the filter is both the mitigation and the instrument: **what the filter caught is the best available measurement of what the system generated.**

**Inspect the filters and keep the record.** A filter that catches more this flight than last is a system telling you something, and it is the cheapest condition monitoring in the vehicle.

Cleanliness levels and their consequences are in [CleanlinessAndContamination](../../fluidSystems/fluidSystemsLibrary/docs/CleanlinessAndContamination.md).

---

## Can it be re-cleaned in place

**The question that decides whether a fluid system is reusable at all**, and it is a design question rather than an operational one.

**In-place cleaning needs flow paths that reach everywhere**, connections to introduce and remove the cleaning fluid, and no dead legs where contamination collects and cleaning fluid does not. **A dead leg is a permanent contamination reservoir** and no amount of flushing fixes it.

**If it cannot be cleaned in place it has to be disassembled**, and a disassembled system is a system whose every joint has to be remade, releaked and reverified. That is the single largest step change in refurbishment cost available.

**So the design rules are layout rules**: no dead legs, cleaning connections at the extremities, and flow paths that a cleaning fluid can traverse in the direction contamination travels.

---

## Pressure vessels

The item with the most rigorous life management and the least visible degradation.

**A composite overwrapped pressure vessel has a fracture-controlled life** measured in pressure cycles, and its condition is established by [proof pressure](InspectionAndAcceptance.md) and by cycle counting rather than by looking at it.

**Proof testing consumes the life it establishes**, which is the uncomfortable part: every proof cycle is a cycle. On a vessel with a sixty cycle life, proof testing every flight spends a real fraction of the budget on establishing the budget.

**And a vessel that has been through an entry and a landing is one whose impact history is not fully known**, because a composite overwrap can be damaged by an impact that leaves no visible mark. That is the argument for impact protection rather than for inspection: the inspection does not reliably find it.

---

## Design rules of thumb

- **Replace static seals, do not inspect them.** Inspection costs more and discriminates worse.
- **Cost a seal as a leak check.** The seal itself is nothing.
- **Measure valve margins, not just function.** The trend predicts the failure.
- **Read the filters and keep the record.** Cheapest condition monitoring available.
- **Design out dead legs.** They are permanent contamination reservoirs.
- **Provide cleaning connections at the extremities** or accept disassembly.
- **Protect composite vessels from impact.** The inspection will not find it.

---

## Failure modes

**Static seals inspected rather than replaced.** More cost, less confidence.

**A functional test taken as a condition assessment.** It does not see margins.

**Filters replaced without being read.** The measurement is thrown away.

**A dead leg anywhere in the system.** It never gets clean.

**Proof testing every flight on a fracture-limited vessel.** Consuming the budget to measure it.

**Impact damage on a composite overwrap assumed to be visible.** It frequently is not.

---

## References

- [Seals](../../fluidSystems/fluidSystemsLibrary/docs/Seals.md) and [Leaks](../../fluidSystems/fluidSystemsLibrary/docs/Leaks.md)
- [CleanlinessAndContamination](../../fluidSystems/fluidSystemsLibrary/docs/CleanlinessAndContamination.md)
- [CryogenicSystems](../../fluidSystems/fluidSystemsLibrary/docs/CryogenicSystems.md)
- [ValveAndActuatorDrive](../../electricalPower/docs/ValveAndActuatorDrive.md), for the pull-in margin trend
