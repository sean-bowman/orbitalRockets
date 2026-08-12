[Home](../README.md) > Refurbishment Process

# Refurbishment Process

## Contents

- [Overview](#overview)
- [The flow](#the-flow)
- [Where the cost goes](#where-the-cost-goes)
- [Replacement policy](#replacement-policy)
- [Access is the whole game](#access-is-the-whole-game)
- [Turnaround against refurbishment](#turnaround-against-refurbishment)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Refurbishment is the recurring cost that decides whether reuse pays, and it is decided almost entirely by decisions made during design.

---

## The flow

The shape is common even where the details differ.

**Receive and safe.** See [RecoveryOperations](RecoveryOperations.md).

**Clean.** Soot, salt, residual propellant, and whatever the landing put on it.

**Inspect.** The [ladder](InspectionAndAcceptance.md), at whatever level the plan calls for.

**Disposition.** Fly as is, repair, replace, or retire.

**Replace the single-use items.** Ordnance, crushable absorbers, seals, filters, anything the plan lists.

**Re-test.** Functional checks, leak checks, and whatever acceptance the plan requires.

**Release to flight.**

**Every one of those steps is labour**, and labour is what refurbishment cost is made of. That is why access dominates: a step that takes four hours with a port and forty without is a factor of ten in the term that decides the whole reuse case.

---

## Where the cost goes

Not in the parts. In the labour of establishing that the parts are acceptable.

**Access and disassembly.** Getting to the thing that has to be inspected or replaced, and putting it back.

**Inspection labour.** The technique itself is usually quick; the setup, the access and the interpretation are not.

**Re-test.** A system opened has to be closed and proven closed again, which on a fluid system means a [leak check](../../fluidSystems/fluidSystemsLibrary/docs/Leaks.md) at every joint that was broken.

**Paperwork.** Not a joke: a flight article's configuration record has to be current, and every replacement and disposition is a record entry that somebody has to make and somebody else has to check.

**Parts are the smallest of those on a well designed vehicle** and the largest on a badly designed one, because a design that cannot be inspected has to be replaced instead.

---

## Replacement policy

Three categories, and the boundaries between them are the design decision.

**Replace every flight.** Single-use items: ordnance, crushable absorbers, some seals. **Cheap and certain**, and the argument for putting an item in this category is that inspecting it costs more than replacing it.

**Replace on condition.** Inspected each flight and replaced when a criterion fires. **This is the expensive category** because it costs an inspection every flight and a replacement sometimes, and it only pays where the item is dear and the inspection is cheap.

**Replace on life.** Replaced at a flight count regardless of condition. **Cheap to administer and it wastes life**, deliberately, in exchange for not having to establish condition. See [LifeTrackingAndLimits](LifeTrackingAndLimits.md).

**The commonest mistake is putting an item in "on condition" because it feels rigorous.** On-condition is the most expensive of the three and it should be reserved for items where the inspection genuinely discriminates.

---

## Access is the whole game

Said again because it is the single lever.

**A refurbishment plan is a list of things to reach.** How long each takes is set by whether the design put a port, a panel or a removable section where it is needed, and that decision is made when the structure is laid out and is effectively impossible afterwards.

**A stage designed for one flight has no reason to provide access**, and so it does not, and so it is expensive to refurbish. That is not a failure of the refurbishment team.

**The corollary is that a first reusable vehicle derived from an expendable one is expensive to turn around**, and the second one, designed for it, is not. That is a normal programme trajectory rather than a surprise.

---

## Turnaround against refurbishment

Two different quantities that get conflated.

**Turnaround is elapsed time.** It sets how many flights an article can do in a period, and therefore how large a fleet has to be.

**Refurbishment cost is money per flight.** It sets whether reuse pays at all.

They are correlated and they are not the same. **A programme can buy turnaround with parallel facilities and staffing without touching the cost**, and it can reduce the cost by simplifying the work without touching the elapsed time.

**Which to attack depends on what is binding.** If the fleet is large enough, attack cost. If the fleet is capital-constrained, attack turnaround.

---

## Worked numbers

The precedent comparison, which is the most instructive thing in this subject.

| | Design goal | Achieved | Flight leader |
|---|---|---|---|
| Space Shuttle orbiter | 14 days | 54 days | 39 flights |
| Falcon 9 booster | not stated | 9.2 days | 36 flights |

**The Shuttle achieved 3.9 times its design turnaround at its very best**, and typical turnarounds were months rather than the 54 day record.

**A Falcon 9 booster has turned around in less time than the Shuttle design goal.** The difference is not landing technology and it is not effort. **It is that the Shuttle's design made inspection expensive**: individually bonded tiles individually assessed, engines removed for teardown, and limited access to an airframe that had to be human-rated.

---

## Design rules of thumb

- **Put the access in when the structure is laid out.** There is no later.
- **Replace rather than inspect** wherever replacement is cheaper than establishing condition.
- **Reserve on-condition for items where the inspection discriminates.** It is the dear option.
- **Separate turnaround from refurbishment cost** and know which one binds.
- **Expect the first reusable derivative of an expendable vehicle to be expensive.** Design the second one for it.
- **Count the paperwork.** It is real labour on a flight article.

---

## Failure modes

**Access left to the refurbishment team.** They cannot add it.

**Everything on condition.** The most expensive policy applied by default.

**Turnaround and cost treated as one number.** Different levers, different fixes.

**A reuse case built on parts cost.** The cost is labour.

**Design goals quoted as capability.** The Shuttle's two week goal is the cautionary example.

---

## References

- [InspectionAndAcceptance](InspectionAndAcceptance.md), which feeds this
- [Leaks](../../fluidSystems/fluidSystemsLibrary/docs/Leaks.md), for what reopening a joint costs
- [ReuseEconomics](ReuseEconomics.md), for what refurbishment cost decides
- [FluidSystemReuse](FluidSystemReuse.md)
