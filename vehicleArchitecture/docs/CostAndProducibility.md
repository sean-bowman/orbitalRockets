[Home](../README.md) > Cost and Producibility

# Cost and Producibility

## Contents

- [Overview](#overview)
- [The axis this domain cannot see](#the-axis-this-domain-cannot-see)
- [Where mass and cost disagree](#where-mass-and-cost-disagree)
- [Rate and the learning curve](#rate-and-the-learning-curve)
- [Design for manufacture at vehicle level](#design-for-manufacture-at-vehicle-level)
- [What would be needed to model this](#what-would-be-needed-to-model-this)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

This document computes nothing. It exists because a domain that optimises on mass should say what it is not optimising on, and because several of this domain's own results point directly at cost without being able to follow.

---

## The axis this domain cannot see

Every result in [ArchitectureOverview](ArchitectureOverview.md) is a mass result. Three of the four say a thing widely treated as a design decision is flat in mass, and in every one of those cases **the decision is actually being made on something else, and that something else is usually cost.**

**The staging split** is flat to a fifth of a per cent, and Falcon 9 sits four per cent off its optimum. What it buys is engine commonality between stages, which is a manufacturing decision.

**The liftoff thrust to weight** is not set by the loss budget. It is set by engine mass and engine cost.

**Reusability** cannot be decided on mass at all, because the mass side always says no.

So the pattern is consistent: **where this domain finds a flat optimum, it has usually found a place where cost is the real objective.** That is a useful thing for a mass-based tool to be able to say about itself.

---

## Where mass and cost disagree

Four common cases, all qualitative.

**Common parts against optimal parts.** Two identical engines are cheaper and heavier than one optimised per stage. Falcon 9's second stage engine is a vacuum-optimised version of the first stage engine rather than a different engine, and the mass penalty is real.

**Fewer, larger parts against more, smaller ones.** A single large engine is cheaper per newton and worse for engine-out and throttling.

**Margin against mass.** Thicker is heavier and it is also more forgiving of manufacturing variation, which reduces scrap. A design at minimum gauge everywhere has no tolerance for a thin batch.

**Material choice.** The lighter alloy is usually harder to weld, harder to form and slower to machine. [aerospaceMaterials](../../aerospaceMaterials/) carries the processing side of that, and none of it is priced.

---

## Rate and the learning curve

Unit cost falls with cumulative production on a roughly log-linear curve, and the exponent is the thing that decides whether a vehicle is viable at rate.

Two consequences that reach the architecture.

**A design decision that reduces part count reduces cost twice**: once per unit and again through faster learning on the parts that remain.

**A vehicle designed for a low flight rate and flown at a high one is the wrong vehicle**, and the reverse is worse. The rate assumption is an architecture input and it is rarely written down as one.

Neither is modelled here. Both are named because they change what "optimal" means.

---

## Design for manufacture at vehicle level

The vehicle-level manufacturing decisions are made early and they are hard to reverse.

**Diameter is set by transport and by the factory**, as [ConfigurationTrades](ConfigurationTrades.md) says, and a diameter chosen on mass and rejected by a road is a common and expensive discovery.

**Joint count and joint type.** Every weld is a process, an inspection and a rework risk. A stage with fewer, longer welds is cheaper and needs bigger tooling.

**Common bulkhead against intertank.** Mass says common bulkhead. Manufacturability and inspectability say intertank, and the hazard argument in [ConfigurationTrades](ConfigurationTrades.md) says the same.

**Additive against wrought.** Priced neither here nor in [aerospaceMaterials](../../aerospaceMaterials/), which carries the process capability and not the cost.

---

## What would be needed to model this

Stated so the gap is a defined piece of work rather than a shrug.

**A cost estimating relationship per subsystem**, of the same shape as a mass estimating relationship and with the same weaknesses, plus a learning curve exponent and a rate assumption.

**A recurring against non-recurring split**, because the architecture decisions that reduce recurring cost frequently raise non-recurring cost and the balance depends entirely on the flight rate.

Both are well-established practice and neither is in this repository. **The honest position is that this domain optimises one axis of several and says so**, which is better than a cost model built on assumed coefficients that would carry more authority than it earns.

---

## Design rules of thumb

- **When you find a flat mass optimum, ask what the real objective is.** It is usually cost.
- **Write down the flight rate assumption.** It is an architecture input.
- **Count joints, not just mass.** Every one is a process and an inspection.
- **Expect the cheaper vehicle to be heavier**, and expect that to be correct.
- **Do not build a cost model on assumed coefficients** and then trade against it.

---

## Failure modes

**A vehicle optimised on mass and selected on cost.** The optimisation answered a question nobody was asking.

**A flat optimum defended.** It is flat because the decision is being made elsewhere.

**A rate assumption left implicit.** It decides whether the architecture is right.

**A cost model with invented coefficients.** It carries authority it has not earned, and mass at least is checkable.

---

## References

- [ArchitectureOverview](ArchitectureOverview.md), for the flat optima this document explains
- [manufacturingAndAssembly](../../manufacturingAndAssembly/), which owns the production side
- [aerospaceMaterials](../../aerospaceMaterials/docs/), for process capability, which is not cost
