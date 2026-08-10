[Home](../README.md) > Mechanisms Overview

# Mechanisms Overview

## Contents

- [Overview](#overview)
- [What makes this domain different](#what-makes-this-domain-different)
- [What the domain found](#what-the-domain-found)
- [The standard this domain is built on](#the-standard-this-domain-is-built-on)
- [Document index](#document-index)
- [What this domain does not compute](#what-this-domain-does-not-compute)
- [Design rules of thumb](#design-rules-of-thumb)
- [References](#references)

---

## Overview

Mechanisms are single-shot, non-redundant, and they have to work. Stage and fairing separation, payload release, deployables, and the actuators and pyrotechnics that drive them.

---

## What makes this domain different

The engineering problem is unusual and it reorganises everything.

**The device operates exactly once**, in an environment that cannot be fully reproduced, after months of storage, and a failure is immediate mission loss with no recovery. There is no run-in, no trend to watch and no second attempt.

So the confidence cannot come from the article that flies. It comes from analysis plus test on other articles, which is why [NASA-STD-5017B](StandardsIndex.md) ties its safety factors to the level of test evidence rather than to the design.

**The hardware is simple and the confidence is expensive.** That is the shape of the whole domain and it is the opposite of most of this repository, where the hardware is complex and the physics is settled.

---

## What the domain found

Four results, and three of them are corrections to something that seemed obvious.

**The joint that flies is not the joint that was installed.** Preload relaxes by about eleven per cent over nine months. Embedment, short-term relaxation and storage compound rather than add, and none of them is visible on the vehicle. See [SeparationSystems](SeparationSystems.md).

**Neither a stronger spring nor more springs fixes tipoff.** A stronger spring raises the tipoff rate and the separation velocity in the same proportion, so the rotation accumulated while clearing does not move at all. And the deterministic worst case is flat in spring count: half the springs high and half low produce the same net moment whether there are four or forty. Only the statistical case improves. **Matching the springs in opposing pairs is the one thing that attacks the bound.**

**The latch pays quadratically for the spring.** Impact energy goes as the square of the arrival rate, so a deployment spring chosen with generous margin arrives violently. A damper resolves it and then eats the margin that justified the spring, because the standard counts damper drag as a resisting torque. See [DeploymentMechanisms](DeploymentMechanisms.md).

**Test evidence rather than design is what buys margin.** The same actuator goes from a margin of 0.21 to 0.62 with no design change, because the standard retires uncertainty by measurement. See [ActuatorsAndDrives](ActuatorsAndDrives.md).

---

## The standard this domain is built on

NASA-STD-5017B, *Design and Development Requirements for Mechanisms*, read directly from the standard rather than from a summary of it.

**That distinction earned its keep immediately.** A web search summary of this same standard reported the required torque margin as 1.0 or greater. The standard says a margin greater than or equal to **zero** indicates the requirement is met, because the reserve is inside the safety factors rather than applied on top of the result.

Building on the summary would have made every mechanism in this library look twice as marginal as it is, and would have driven hardware decisions to correct a problem that does not exist.

The full equation, the factor table and the requirement numbers are in [StandardsIndex](StandardsIndex.md) and carried as data in `mechanismUtils.py` with the citation attached.

---

## Document index

| Document | Covers |
|---|---|
| [SeparationSystems](SeparationSystems.md) | Clamp bands, preload relaxation, separation velocity, tipoff and recontact |
| [Pyrotechnics](Pyrotechnics.md) | No-fire and all-fire, the firing circuit, safe and arm, and the shock |
| [NonExplosiveActuators](NonExplosiveActuators.md) | Shape memory, paraffin, split spool, and the trade against pyro |
| [FairingSeparation](FairingSeparation.md) | Jettison, clearance, contamination |
| [DeploymentMechanisms](DeploymentMechanisms.md) | Hinges, latches, rate control and the quadratic latch |
| [ActuatorsAndDrives](ActuatorsAndDrives.md) | The margin equation, the three margins, and what evidence buys |
| [SpringsAndEnergyStorage](SpringsAndEnergyStorage.md) | Energy budgets, the momentum split, spring matching |
| [TribologyAndLubrication](TribologyAndLubrication.md) | Vacuum lubrication, cold welding, dry film life |
| [MechanismTesting](MechanismTesting.md) | Testing a device that operates once, and the one-g offload problem |
| [StandardsIndex](StandardsIndex.md) | NASA-STD-5017B in detail, and the correction reading it produced |
| [ValidationReferences](ValidationReferences.md) | One standard at standard level, and three gaps |

---

## What this domain does not compute

Named rather than approximated, because in a domain this weakly anchored an unmarked estimate is worse than a gap.

**The shock.** Pyroshock prediction is a test-derived discipline. [ClampBand](SeparationSystems.md) computes the released strain energy and stops there, because a shock response spectrum from this library would carry more authority than it earns.

**Tribology.** Vacuum lubrication, cold welding and dry film life are material and process questions rather than mechanism arithmetic. Documented in [TribologyAndLubrication](TribologyAndLubrication.md) and not modelled.

**Deployment in one g.** The offload rig is usually the hardest part of testing a deployable and none of it is here.

**Non-explosive actuator performance.** The devices are described in [NonExplosiveActuators](NonExplosiveActuators.md) and none of them is sized, because each is a proprietary characteristic curve rather than a calculation.

---

## Design rules of thumb

- **Carry the margin against the relaxed preload**, not the installed one.
- **Match springs in opposing pairs.** Adding them improves the expectation and not the bound.
- **Size the latch before the spring.** The energy goes as the square of arrival rate.
- **Read the standard.** The summary of this one was wrong in the direction that costs hardware.
- **Test to buy margin.** It is cheaper than the design change the analysis factors would demand.

---

## References

- NASA-STD-5017B, *Design and Development Requirements for Mechanisms*
- [ValidationReferences](ValidationReferences.md)
- NASA-STD-5019, *Fracture Control Requirements for Spaceflight Hardware*
- Conley, *Space Vehicle Mechanisms: Elements of Successful Design*
