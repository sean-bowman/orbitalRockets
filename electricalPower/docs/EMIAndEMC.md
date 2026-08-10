[Home](../README.md) > EMI and EMC

# EMI and EMC

## Contents

- [Overview](#overview)
- [Four problems with one name](#four-problems-with-one-name)
- [MIL-STD-461](#mil-std-461)
- [The three mitigations](#the-three-mitigations)
- [Why ordnance sets the requirement](#why-ordnance-sets-the-requirement)
- [What an EMC test actually catches](#what-an-emc-test-actually-catches)
- [Why nothing here is modelled](#why-nothing-here-is-modelled)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Electromagnetic compatibility is the requirement that the vehicle's own systems do not interfere with each other or with anything outside. It is verified by test against a standard, and it is designed for by three mitigations applied early.

---

## Four problems with one name

They have different mechanisms and different fixes, and calling them all EMI is how the wrong one gets applied.

**Conducted emissions**: noise a device puts onto the power bus. Fixed by input filtering at the source.

**Conducted susceptibility**: how a device behaves when the bus is noisy. Fixed by input filtering at the victim, and by designing the load to tolerate the bus it actually has. See [PowerQuality](PowerQuality.md).

**Radiated emissions**: noise a device or its harness broadcasts. Fixed by shielding and by controlling the loop areas that radiate.

**Radiated susceptibility**: how a device behaves in an external field. Fixed by shielding and by circuit design.

The harness is the dominant antenna for both radiated cases, which is why an EMI problem is usually a harness problem rather than a box problem.

---

## MIL-STD-461

The governing standard for emissions and susceptibility requirements and their test methods, organised as requirement groups: CE for conducted emissions, CS for conducted susceptibility, RE for radiated emissions, RS for radiated susceptibility, each with a number for the specific test.

**It is not read here**, and the requirement limits are therefore not carried in this library. What is carried is the qualitative structure above and the boundary in the next section.

---

## The three mitigations

Applied in this order, because each is cheaper than the next.

**Control the loop area.** A circuit radiates in proportion to the area enclosed by its current loop. Twisted pairs work because the twist cancels the loop; a signal returning through a distant ground rather than its own return wire encloses a very large one. **This is free and it is a routing decision made when the harness is drawn.**

**Filter at the interface.** A filter at every box interface stops noise entering or leaving, and it is far cheaper than shielding the whole vehicle.

**Shield.** Effective, heavy, and only as good as its termination: **a shield grounded at one end is not a shield above a certain frequency**, and a shield terminated with a pigtail rather than a full circumferential connection loses most of its effectiveness.

---

## Why ordnance sets the requirement

The tightest electromagnetic requirement on a launch vehicle usually comes from the initiators, not from the avionics.

An NSI must not fire at one amp or one watt, and the vehicle has to guarantee that against radio frequency pickup on a harness that acts as an antenna, lightning-induced transients, static discharge and a test set connected wrongly.

**That drives the bonding, the shielding, the twisted shielded pairs, the shorting plugs and the operational radio silence**, and it is why the initiator choice is an electromagnetic compatibility decision as much as an ordnance one: a more sensitive initiator tightens every one of those requirements.

The arithmetic is in [mechanismsAndSeparation](../../mechanismsAndSeparation/docs/Pyrotechnics.md) and the boundary is in [PyroCircuits](PyroCircuits.md).

---

## What an EMC test actually catches

Worth being specific, because the test is expensive and its coverage is narrower than it looks.

**It catches** a device that emits above the limit, a device that malfunctions at the specified field strength, and a filter that was designed and not fitted.

**It does not catch** an interaction that only occurs in a configuration not tested, which on a vehicle with modes means most configurations. It does not catch an intermittent bond, because the test article is usually assembled carefully. And it does not catch a problem that only appears with the flight harness routing, if the test was done on a bench harness.

**The most common real finding is a shield termination**, and it is found by inspection rather than by the test.

---

## Why nothing here is modelled

Every quantity in this document is either a measured limit from a standard that has not been read, or a field problem needing a solver this repository does not have.

A model that produced an emissions number would be producing an unearned one, and in a domain where the real verification is a test that costs a week of chamber time, an unearned number is worse than none.

**What this library does supply** is the harness resistance and the firing circuit current that a real susceptibility assessment consumes. That is the honest boundary.

---

## Design rules of thumb

- **Control loop area first.** It is free and it is decided when the harness is routed.
- **Filter at every box interface.** Cheaper than shielding.
- **Terminate shields circumferentially.** A pigtail is not a termination.
- **Let ordnance set the requirement**, because it usually does.
- **Route power away from signal**, and cross at right angles where they must meet.

---

## Failure modes

**A signal returning through a distant ground.** A very large loop, radiating.

**A pigtail shield termination.** Most of the shielding lost.

**A filter designed and not fitted.** The commonest EMC test finding.

**An EMC test on a bench harness.** The flight routing is the thing being tested.

**A sensitive initiator chosen for circuit mass.** It tightens every EMC requirement on the vehicle.

---

## References

- MIL-STD-461, *Requirements for the Control of Electromagnetic Interference Characteristics*, not read here
- MIL-STD-464, *Electromagnetic Environmental Effects Requirements for Systems*, not read here
- [GroundingAndBonding](GroundingAndBonding.md)
- [mechanismsAndSeparation Pyrotechnics](../../mechanismsAndSeparation/docs/Pyrotechnics.md)
