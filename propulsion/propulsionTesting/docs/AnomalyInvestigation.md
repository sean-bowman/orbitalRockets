[Home](../README.md) > Anomaly Investigation

# Anomaly Investigation

## Contents

- [Overview](#overview)
- [Reading a failure backwards](#reading-a-failure-backwards)
- [Signatures worth recognising](#signatures-worth-recognising)
- [The ones that look like each other](#the-ones-that-look-like-each-other)
- [Derived channels worth computing every time](#derived-channels-worth-computing-every-time)
- [What the data cannot tell you](#what-the-data-cannot-tell-you)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Something goes wrong on a stand and there is a data set, some hardware, and a room full of people with opinions. This document is about the part of that which transfers: what the channels look like for the common failures, and which pairs of failures look alike.

The part that does not transfer is judgement built from having been in that room, and the honest position is that this document is a starting point for someone who has not been.

---

## Reading a failure backwards

The method is the same every time.

**Find the first channel that departed from nominal**, not the first alarm. Alarms fire on thresholds and thresholds are crossed in an order that has nothing to do with causation.

**Establish the time ordering to the resolution of the data**, and notice when the ordering is inside the sample interval, because then there is no ordering, only a coincidence.

**Ask what could produce that channel and not the others**, which is where the derived channels below earn their place.

**Stop when the explanation accounts for every channel**, not when it accounts for the alarming one. A theory that explains the chamber pressure and not the coolant outlet temperature is not finished.

---

## Signatures worth recognising

| Signature | Looks like | Usually is |
|---|---|---|
| Chamber pressure step down, flows steady | A performance loss | A throat that grew: erosion or a liner failure |
| Chamber pressure step down, both flows down | An engine throttling itself | A feed system restriction upstream of both |
| Fuel flow up, chamber pressure flat | A meter fault | A fuel side leak downstream of the meter |
| Coolant outlet temperature rising steadily | Approaching steady state | A cooling passage blocking, if it does not level off |
| Coolant outlet temperature falling | Nothing to worry about | A passage that has burned through and is dumping into the chamber |
| Low frequency thrust oscillation, chamber pressure flat | A chug | A stand mode, until a modal survey says otherwise |
| Low frequency oscillation in both | A stand mode | A chug, and see [combustionDevices](../../combustionDevices/docs/CombustionStability.md) |
| Chamber pressure spike at ignition | A hard start | A hard start, and see [ignitionAndStart](../../ignitionAndStart/docs/StartTransient.md) |
| Mixture ratio drifting through the burn | A control problem | A tank ullage or a meter drifting with temperature |

None of these is diagnostic on its own. The table is a list of first guesses that have a better record than the intuitive first guess, which is usually that the instrument is wrong.

---

## The ones that look like each other

Three pairs cause most of the misdiagnoses.

**A stand mode against a chug.** Both are low frequency oscillations. The discriminator is that a chug moves with chamber pressure and injector pressure drop and a stand mode does not, and the cheap answer is a modal survey done once. See [TestStands](TestStands.md).

**An aliased acoustic mode against a genuine low frequency instability.** A 1T mode sampled below Nyquist appears in the performance band as an oscillation that is not there. **This one is worse than the others** because the false signature is at the frequency the real problem would be at. The only defence is anti-alias filtering in hardware, decided at build time. See [Instrumentation](Instrumentation.md).

**Throat erosion against a c\* efficiency change.** Both show as chamber pressure falling at constant flow. The discriminator is that erosion is progressive within a firing and does not recover between firings, and an efficiency change is a step that repeats. Post-test throat measurement settles it, and it is the reason to measure the throat after as well as before.

---

## Derived channels worth computing every time

Not because they are needed every time, but because computing them costs nothing and not having them after an anomaly costs a repeat test.

**Mixture ratio**, from the two flows. It moves before most things do.

**c\*, continuously**, not just over the steady window. Its shape through the firing distinguishes progressive from step changes.

**Injector pressure drop**, as manifold minus chamber. It is the chug discriminator and it is also the first thing to move when an element blocks.

**Coolant temperature rise and the implied heat load**, against the [combustionDevices](../../combustionDevices/docs/RegenerativeCooling.md) prediction. It is the only in-flight measurement of the heat load in this repository.

**Every channel's rate of change.** Ordering is easier to see in derivatives than in values, and the first departure is usually visible in a derivative before it is visible in a level.

---

## What the data cannot tell you

Stated plainly because this sub-domain is thinner than it looks.

**Which channel to distrust on the day.** Every stand has a channel with a history and that history is not in the data.

**What it sounded like.** Experienced test engineers hear things before the data shows them, and that is not a figure of speech.

**What the hardware looked like afterwards.** Post-test inspection resolves more anomalies than data reduction does, and it is not modelled here at all.

**Whether the anomaly matters.** That is a requirements question and it belongs to [reliabilityAndMissionAssurance](../../../reliabilityAndMissionAssurance/).

---

## Design rules of thumb

- **Find the first departure, not the first alarm.**
- **Explain every channel**, not the one that alarmed.
- **Compute the derived channels every time.** They cost nothing and they cannot be added later.
- **Measure the throat after as well as before.** It settles the commonest ambiguous signature.
- **Do the modal survey once**, or argue about stand modes forever.
- **Photograph and inspect before disassembly.** The hardware is evidence and it is destroyed by handling.

---

## Failure modes

**Diagnosing from the alarming channel.** The alarm order is a threshold artefact.

**Stopping at the first sufficient explanation.** Sufficient for one channel is not sufficient.

**Blaming the instrument first.** Sometimes right, and it is the guess with the worst record.

**Attributing an aliased acoustic mode to a low frequency instability.** The false signature sits exactly where the real one would.

**No post-test throat measurement.** Leaves erosion and efficiency indistinguishable.

**Disassembling before inspecting.** The hardware is the other half of the data set.

---

## References

- [combustionDevices CombustionStability](../../combustionDevices/docs/CombustionStability.md), for the instability mechanisms behind several signatures
- [ignitionAndStart StartTransient](../../ignitionAndStart/docs/StartTransient.md), for the hard start signature
- [fluidSystemsTesting AnomalyAndFailureInvestigation](../../../fluidSystems/fluidSystemsTesting/docs/AnomalyAndFailureInvestigation.md), for the investigation process this follows
- Sutton and Biblarz, *Rocket Propulsion Elements*, the testing and failure chapters
