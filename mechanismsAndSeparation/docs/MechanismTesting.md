[Home](../README.md) > Mechanism Testing

# Mechanism Testing

## Contents

- [Overview](#overview)
- [Testing a device that operates once](#testing-a-device-that-operates-once)
- [What the standard requires](#what-the-standard-requires)
- [The one-g offload problem](#the-one-g-offload-problem)
- [Life testing](#life-testing)
- [Shock characterisation](#shock-characterisation)
- [What test evidence is worth](#what-test-evidence-is-worth)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Every other domain in this repository tests hardware to find out how it behaves. This one tests hardware to find out how *other* hardware will behave, because the article that flies has never been operated.

---

## Testing a device that operates once

The article that flies is the article that has never been fired, deployed or released. So the evidence comes from three places and none of them is the flight article in its flight configuration.

**Qualification units**, tested to the environment with margin, usually to destruction. They are the same design and not the same article.

**Lot acceptance**, testing a sample from the same production lot as the flight units. This is what connects the qualification evidence to the specific hardware, and it is why lot traceability matters more here than anywhere else.

**Acceptance testing of the flight article** in whatever way does not consume it: continuity, resistance, preload, torque with the release device removed, functional cycling of a resettable mechanism.

**The gap between the last two is the whole problem.** A pyrotechnic release on the flight article can be verified for continuity and not for function, and no amount of care closes that gap.

---

## What the standard requires

NASA-STD-5017B is prescriptive about verification and the requirements are worth listing.

**All torque margins verified during acceptance test at the highest possible level of assembly** [DDMR 11]. Not at component level, because interfaces add resisting torque and a component-level margin can be comfortably positive while the assembly is negative.

**Torque margin applied under worst-case conditions throughout life, including throughout life testing** [DDMR 9]. Worst case means the combination of minimum driving torque and maximum resisting torque over the qualification environmental limits, and the standard adds a caution: only combinations that can occur simultaneously need be considered.

**The mechanism remains functional after exposure to stall conditions at any point in travel** [DDMR 29], with guidance of one minute of stall for compliance assessment, two minutes in qualification and one in acceptance.

**Positive margin with full design factors under worst-case transient loads from mechanical stop impact** [DDMR 31].

Where direct margin testing is impossible, the standard permits testing the individual torque terms and computing the margin from tested values, which is a materially weaker claim and is worth recording as such.

---

## The one-g offload problem

A deployable designed for zero g has to be tested on Earth, and gravity at this scale is not a small effect.

**Offload rigs** support the deploying mass with a counterweight, an air bearing table, or a gantry that follows the motion. Each adds something the flight article will not have: friction, inertia, a tether force that is not quite vertical, and a constraint that changes the dynamics.

The domain ethos states the rule: **test the mechanism in the flight configuration and orientation.** Where that is impossible, the offload becomes part of the test article and its effects belong in the uncertainty.

**A deployment that works in a rig and fails in flight is usually an offload artefact rather than a mechanism failure**, and the way to catch it is to test in more than one orientation and see whether the answer moves.

---

## Life testing

A single-shot device has a life of one and still needs life testing, for two reasons.

**Cycle life on the qualification unit** establishes that the mechanism is not marginal. A device that works on cycle one and fails on cycle ten was always marginal on cycle one.

**Calendar life** is the one that matters more here and is harder. Preload relaxes, lubricant evaporates, dry film degrades, and none of that is exercised by cycling. The standard requires an evaporative loss analysis showing 90 per cent of the liquid lubricant remains at end of life precisely because **life testing evaluates cycle life and not calendar life**.

So the storage duration is a requirement, it has to be stated, and it has to be covered by analysis rather than by test unless the programme is prepared to wait.

---

## Shock characterisation

Shock is measured rather than predicted, which makes the characterisation test the only source of the number.

The test fires the actual device on a representative structure with accelerometers at the locations that matter, and produces a shock response spectrum. Everything downstream, including whether nearby hardware needs to be qualified to a higher level, comes from that measurement.

**This library computes the released energy and stops.** See [Pyrotechnics](Pyrotechnics.md) and [ValidationReferences](ValidationReferences.md).

---

## What test evidence is worth

Quantitatively, and this is the most useful thing in the document.

| Evidence | FSv | Margin on the reference actuator |
|---|---|---|
| Theory or analysis | 3.00 | +0.205 |
| Development test at extremes | 2.50 | +0.394 |
| Acceptance test of flight hardware at extremes | 2.00 | +0.620 |

**Three times the margin between the first row and the last, with no design change.**

That is the argument for a test programme stated in the currency the design uses. A mechanism that fails its margin on analysis has two options, and testing is usually cheaper than the redesign.

---

## Design rules of thumb

- **Test at the highest level of assembly possible.** Interfaces add resistance.
- **Test in more than one orientation** and see whether the answer moves.
- **State the storage duration as a requirement.** Calendar life is not covered by cycling.
- **Budget the characterisation test.** Shock has no other source.
- **Cost the test against the redesign** the analysis factors would otherwise demand.

---

## Failure modes

**Component-level margin accepted for an assembly.** Interfaces add resisting torque.

**An offload artefact mistaken for a mechanism result.** Test in another orientation.

**Calendar life assumed to be covered by cycle life.** It is not, and the standard says so.

**Shock predicted rather than measured.** There is no adequate analytic model.

**Margin computed from individually tested terms** and reported as if directly verified. Weaker claim.

---

## References

- NASA-STD-5017B, requirements DDMR 9, 11, 29 and 31
- [ActuatorsAndDrives](ActuatorsAndDrives.md), for the margin the evidence buys
- [fluidSystemsTesting](../../fluidSystems/fluidSystemsTesting/), for the campaign philosophy
- [propulsionTesting](../../propulsion/propulsionTesting/), for the discrimination arithmetic
