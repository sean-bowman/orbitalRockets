[Home](../README.md) > Configuration Management

# Configuration Management

## Contents

- [Overview](#overview)
- [Three configurations](#three-configurations)
- [Baselines](#baselines)
- [Change control](#change-control)
- [As-designed against as-built](#as-designed-against-as-built)
- [Why it is a reliability function](#why-it-is-a-reliability-function)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Configuration management is the least interesting subject in this repository and it is the one whose absence most reliably invalidates everything else in it.

---

## Three configurations

They diverge, and knowing which one an analysis was run against is the whole discipline.

**As-designed** is what the drawings say.

**As-built** is what was actually made, including every deviation, every replacement and every waiver.

**As-flown** is what was on the vehicle at liftoff, which differs from as-built by whatever happened during integration and the countdown.

**Every analysis in this repository is run against as-designed**, and the vehicle that flies is as-flown. **The gap between them is the configuration management problem**, and it is not small: a stack of accepted deviations, replaced components from different lots, and a shim somebody fitted.

---

## Baselines

A baseline is a configuration frozen at a point, with changes after it controlled.

**The functional baseline** is the requirements. **The allocated baseline** is the requirements pushed down to subsystems. **The product baseline** is the drawings and specifications.

**Each is frozen when it is stable enough that changing it costs more than it saves**, and freezing too early is as expensive as freezing too late: an early freeze produces a stream of changes through the control process, which is the process working correctly and looking like failure.

**What matters is that the baseline exists and is identifiable**, because every analysis, every test and every acceptance refers to one.

---

## Change control

The process, and the two things it is actually for.

**To make sure somebody who understands the consequence sees the change.** A change that looks local is frequently not: a bracket moved changes a load path, a lot changed invalidates a [qualification](../../manufacturingAndAssembly/docs/ProcessQualification.md), a software parameter changed alters an [autonomous FTS rule set](../../rangeSafetyAndFTS/docs/AutonomousFTS.md).

**And to make sure the analyses are re-run.** A change invalidates whatever analysis assumed the old configuration, and **the failure is not the change, it is the analysis that was not re-run.**

**The specific list of analyses that has to be re-checked on a change is worth writing down once**: the [fault tree](FaultTreeAnalysis.md) and its single point failure list, the [FMECA](FMECA.md), the [tolerance stacks](../../manufacturingAndAssembly/docs/AssemblyAndIntegration.md), the mass properties, the loads and the reliability budget. **A change board that approves changes without triggering that list is approving changes blind.**

---

## As-designed against as-built

Where the divergence actually accumulates.

**Accepted deviations.** Each one individually small and defensible, and collectively a vehicle nobody has analysed.

**Replaced components.** A different serial number, frequently a different lot, occasionally a different part number.

**Rework.** A joint remade, a weld repaired, a surface reworked, and each of those is a process the [qualification](../../manufacturingAndAssembly/docs/ProcessQualification.md) may not cover.

**And unrecorded adjustment.** The shim, the tweak, the thing that was obviously fine.

**The mitigation is to record the as-built and to periodically difference it against the as-designed**, which is a boring activity that finds real things. **A vehicle whose as-built has never been differenced is a vehicle whose analyses describe a different vehicle.**

---

## Why it is a reliability function

The connection that gets missed.

**Every reliability claim refers to a configuration.** A [single point failure list](SinglePointFailures.md) derived from one tree is a list for that tree. A [redundancy](RedundancyAndFaultTolerance.md) argument assuming two lots is void if both units came from one. A [qualification](../../manufacturingAndAssembly/docs/ProcessQualification.md) covers the process that was qualified.

**So a configuration that drifts silently invalidates the reliability case silently**, and nothing announces it. There is no failure, no anomaly and no signal: just an analysis that has stopped describing the hardware.

**That is why configuration management belongs in this domain rather than in a programme office document.** It is not administration; it is the thing that keeps every other claim in this repository attached to a vehicle.

---

## Design rules of thumb

- **Know which configuration an analysis was run against.**
- **Freeze a baseline when changing it costs more than it saves**, not earlier.
- **Write the re-check list once**, and trigger it on every change.
- **Record the as-built and difference it against the as-designed.**
- **Treat a lot change as a configuration change.** The qualification was about the other lot.
- **Expect deviations to accumulate.** Individually defensible, collectively a different vehicle.

---

## Failure modes

**An analysis with no configuration reference.** It describes something, and nobody knows what.

**A change approved without triggering the re-check list.** The change is fine and the analysis is stale.

**Deviations accepted individually and never rolled up.** A vehicle nobody has analysed.

**A lot change treated as a supply matter.** It is a qualification matter.

**An as-built never differenced.** The drift is silent and so is the failure.

---

## References

- [ProblemReporting](ProblemReporting.md), which is where deviations are raised
- [ProcessQualification](../../manufacturingAndAssembly/docs/ProcessQualification.md), for what a lot change invalidates
- [SinglePointFailures](SinglePointFailures.md), for the list that has to be re-derived
- [AutonomousFTS](../../rangeSafetyAndFTS/docs/AutonomousFTS.md), for mission data as a configuration item
