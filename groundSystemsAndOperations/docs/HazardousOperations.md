[Home](../README.md) > Hazardous Operations

# Hazardous Operations

## Contents

- [Overview](#overview)
- [Clearing the pad](#clearing-the-pad)
- [The hazardous operations themselves](#the-hazardous-operations-themselves)
- [Toxic against explosive](#toxic-against-explosive)
- [Procedures](#procedures)
- [Two-person and independent verification](#two-person-and-independent-verification)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Most of the risk to people on a launch programme is on the ground, and almost all of it is concentrated into a handful of named operations. This document is about which they are and what surrounds them.

---

## Clearing the pad

The primary control, and it is the only one that works by removing the exposure rather than reducing it.

**The clear area comes from the [siting](HazardZonesAndSiting.md) rings**, and the criterion applied depends on who is being protected: intraline distance for operations personnel, inhabited building distance for everybody else.

**Clearing is a schedule item on the critical path**, because it takes real time to move people and account for them, and nothing hazardous starts until the account closes. In the worked example the pad clear is the first task and everything depends on it.

**Re-entry after a scrub is the harder direction.** The vehicle is loaded, the systems are pressurised, and somebody has to go back in. That is a decision with its own criteria and it should have them written before the scrub.

---

## The hazardous operations themselves

The list is short and it does not change much between programmes.

**Ordnance installation and arming.** Initiators, separation charges, flight termination. The rule is that ordnance is installed late, arming is later still, and the circuit is verifiably safe until the last practical moment. See [Pyrotechnics](../../mechanismsAndSeparation/docs/Pyrotechnics.md).

**Propellant loading**, especially the first pressurised transfer of a campaign.

**Pressurisation to flight levels**, which turns every joint into a stored energy source.

**Anything with the flight termination system live.**

**And detanking after a scrub**, which is loading in reverse with the additional problem that everything is already cold, already wet, and already known to have been through one attempt.

---

## Toxic against explosive

Two different hazards with two different exclusion zones, and they do not size the same way.

**Explosive hazard scales as the cube root of the quantity.** Eight times the propellant is twice the distance, which means large loads are surprisingly compact hazards and small ones are surprisingly large. See [HazardZonesAndSiting](HazardZonesAndSiting.md).

**Toxic hazard scales with dispersion**, which depends on the release rate, the wind and the atmospheric stability far more than on the total quantity. A small hypergolic leak on a still day can produce a larger exclusion zone than a large one in a breeze.

**That means the two zones move independently**, and a site laid out for one is not automatically laid out for the other. A hypergolic vehicle needs both computed, and this domain computes only the first.

**The protective equipment differs completely.** Blast protection is distance and structure. Toxic protection is self-contained breathing apparatus, scrubbed vents, decontamination, and a wind-aware exclusion zone that is redrawn on the day.

---

## Procedures

**A procedure that cannot be followed under pressure will not be followed under pressure.** That is the single design rule for procedures and everything else is a consequence of it.

**Written to be read in real time**, in the order things are done, with the verification steps in line rather than at the end.

**Hold points where the sequence commits**, so there is somewhere to stop that is not the middle of a transfer.

**Contingency branches for the failures that are expected**, which are known: the leak, the failed valve, the sensor disagreement, the abort. A contingency worked out during the event is a decision made by tired people.

**And a red-lined procedure is a finding.** If the procedure was changed at the console, either the procedure was wrong or the change was, and both need closing before the next run.

---

## Two-person and independent verification

Two controls that look similar and do different things.

**Two-person control** means no single person can complete a hazardous action alone. It defends against a deliberate or mistaken single act, and it is standard for ordnance and for arming.

**Independent verification** means a second person checks a completed configuration against the procedure, without having watched it being set. It defends against a shared assumption, which is the failure mode that two people working together does not catch.

**The second is the one more often skipped and the one that catches more**, because the common failure is not a person doing something wrong, it is two people believing the same wrong thing about a valve position.

---

## Design rules of thumb

- **Clear by criterion**, and know which criterion applies to whom.
- **Write the re-entry criteria before the scrub**, not after it.
- **Install ordnance late and arm later.**
- **Compute the toxic zone separately.** It does not scale like the explosive one.
- **Write procedures to be read in real time**, with verification in line.
- **Use independent verification, not just two-person control.** They catch different things.
- **Treat every red line as a finding.**

---

## Failure modes

**A toxic zone assumed to be inside the explosive one.** They scale differently and either can be larger.

**Re-entry decided during the scrub.** Under time pressure, with a loaded vehicle.

**A procedure written to be audited rather than followed.** It will not be followed.

**Two-person control substituted for independent verification.** The shared assumption survives both people.

**A red line accepted without closure.** Either the procedure or the change was wrong.

---

## References

- [HazardZonesAndSiting](HazardZonesAndSiting.md), for the explosive zone
- [Pyrotechnics](../../mechanismsAndSeparation/docs/Pyrotechnics.md), for ordnance safing and arming
- [Hydrazine](../../fluidSystems/fluidSystemsLibrary/docs/Hydrazine.md), for the toxic handling case
- NASA-STD-8719.12A, for the explosives safety requirements this reflects
