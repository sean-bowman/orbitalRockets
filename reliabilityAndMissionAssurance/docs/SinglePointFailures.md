[Home](../README.md) > Single Point Failures

# Single Point Failures

## Contents

- [Overview](#overview)
- [What one is](#what-one-is)
- [Finding them](#finding-them)
- [Why a launch vehicle has so many](#why-a-launch-vehicle-has-so-many)
- [Accepting one](#accepting-one)
- [Tracking](#tracking)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

**Single point failures should be listed, argued and accepted deliberately, never discovered.** This is the document behind that sentence, and the operative word is deliberately.

---

## What one is

**A single failure whose occurrence causes the top event on its own.** In [fault tree](FaultTreeAnalysis.md) terms it is a minimal cut set of order one.

It is categorically different from a two-failure combination rather than quantitatively worse. **A cut set of order one occurs at its own probability**, which is typically three or more orders of magnitude above the product of two. On the worked tree five single point failures carry essentially 100 per cent of the top event and two redundant pairs carry a thousandth.

**So the ranking of a fault tree is nearly always the ranking by cut set order**, and the single point failures are the analysis.

---

## Finding them

**A fault tree finds them and nothing else does reliably.**

A [FMECA](FMECA.md) lists modes and their effects but does not say which ones stand alone, because it works one component at a time and cannot see whether something else would have covered the failure.

**A block diagram hides them**, because a redundant pair drawn as two boxes looks redundant regardless of whether it shares a power feed, a connector, an environment or a lot. See [RedundancyAndFaultTolerance](RedundancyAndFaultTolerance.md).

**And a walk of the hardware finds the ones the drawings do not show.** A cable route that carries both channels through one clamp is a single point failure that no analysis based on the schematic will ever produce.

---

## Why a launch vehicle has so many

Not a failure of diligence. It is structural.

**Single-shot devices are non-redundant by construction.** A separation bolt, an initiator, a fairing joint: they act once, at a moment that cannot be repeated, and duplicating them often makes things worse rather than better. See the two-of-two case in [FlightTerminationSystems](../../rangeSafetyAndFTS/docs/FlightTerminationSystems.md).

**Structure is not redundant.** A tank has one wall.

**Mass punishes redundancy directly.** Every duplicated component is carried the whole way up, and [vehicleArchitecture](../../vehicleArchitecture/) prices that in payload.

**And the mission is short and unrepeatable.** There is no maintenance, no repair and no second attempt, so the usual answer of detecting a failure and fixing it does not exist.

**The result is that a launch vehicle accepts single point failures where an aircraft would not**, and the discipline is in accepting them explicitly rather than in pretending there are none.

---

## Accepting one

A single point failure is a decision. **An undiscovered one has had the decision made by default**, which is why the class raises rather than reporting a count.

An acceptance rationale needs four things.

**Why redundancy is not practical.** Mass, single-shot behaviour, or a duplication that makes it worse.

**What reduces the probability instead**: [derating](DeratingAndMargins.md), qualification to margin, [process control](QualityAndProcessControl.md), lot acceptance testing.

**What would detect a degradation before flight**, if anything.

**And who accepted it.** A named person, on a date, at a review. **An acceptance with no name on it is not an acceptance.**

---

## Tracking

The part that decays quietly.

**The list changes as the design does.** A component deleted removes a single point failure and a component added may create one, and neither is visible unless the list is maintained against the current configuration. See [ConfigurationManagement](ConfigurationManagement.md).

**A stale acceptance is a finding.** An accepted single point failure for a component that no longer exists means the list has not been re-derived, which means the ones that appeared since have not been either.

**The check is symmetric and cheap**: derive the list from the current tree, compare it to the accepted list, and both differences are findings. The class reports stale acceptances alongside unaccepted failures for exactly that reason.

---

## Worked numbers

| Single point failure | Probability | Share of the top event |
|---|---|---|
| engineStartFail | 2.00e-3 | 57.1 % |
| regulatorFail | 5.00e-4 | 14.3 % |
| boltFail | 5.00e-4 | 14.3 % |
| fairingFail | 3.00e-4 | 8.6 % |
| mainValveFail | 2.00e-4 | 5.7 % |

| Quantity | Value |
|---|---|
| Single point failures | 5 |
| Share of the top event they carry | 100 % |
| On the accepted list | 3 |
| **Unaccepted, and refused** | **2** |

---

## Design rules of thumb

- **Derive the list from a fault tree**, not from a FMECA or a block diagram.
- **Walk the hardware.** The routing single points are not on the schematic.
- **Expect a launch vehicle to have them.** The discipline is explicitness, not elimination.
- **Put a name and a date on every acceptance.**
- **Re-derive the list at every configuration change.**
- **Treat a stale acceptance as a finding.** It means the list is not current.

---

## Failure modes

**A list derived from a block diagram.** Shared feeds and shared lots are invisible.

**An acceptance with no name.** Not an acceptance.

**A list that is not re-derived after a design change.** The new ones are invisible.

**A stale acceptance ignored.** It says the list is not current.

**A single-shot device duplicated in series.** Two things that can stop it instead of one.

---

## References

- [FaultTreeAnalysis](FaultTreeAnalysis.md), which produces the list
- [RedundancyAndFaultTolerance](RedundancyAndFaultTolerance.md), for why some redundancy is not
- [ConfigurationManagement](ConfigurationManagement.md), for keeping the list current
- [mechanismsAndSeparation](../../mechanismsAndSeparation/), where the single-shot devices live
