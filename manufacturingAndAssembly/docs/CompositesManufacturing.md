[Home](../README.md) > Composites Manufacturing

# Composites Manufacturing

## Contents

- [Overview](#overview)
- [The part and the process are one decision](#the-part-and-the-process-are-one-decision)
- [Layup](#layup)
- [Cure](#cure)
- [Tooling](#tooling)
- [Defects](#defects)
- [Why inspection is harder here](#why-inspection-is-harder-here)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

In a metal part the material exists before the part does. **In a composite part the material and the part are made at the same time**, which is the single fact everything else follows from.

---

## The part and the process are one decision

A metal design can be made by several routes and the material properties are the same at the end. A composite cannot: fibre volume fraction, void content, ply orientation and cure state are all outcomes of the process, and all of them are allowables.

**So a composite allowable belongs to a process rather than to a material**, and a process change is a material change. That is why a composite qualification is so much larger than a metal one and why it is so hard to second-source.

**And it is why design for manufacture is not optional here.** A layup that cannot be laid up is a material that does not exist.

---

## Layup

**Hand layup** is flexible, needs no capital, and is slow and operator-dependent. It is the right answer for one article and a rate limit for fifty. See [RateAndLearning](RateAndLearning.md): a skilled person is a rate limit with a holiday allowance.

**Automated fibre placement** lays narrow tows under a head on a robot. It is fast, repeatable and heavily capital-and-programming intensive, and its geometry is constrained: it needs a surface the head can reach at an angle it can steer to, and it cannot make a tight concave corner.

**Automated tape laying** is the same idea in wider tape, faster and less steerable, which suits large gentle surfaces.

**Filament winding** is the cheapest of all and only makes surfaces of revolution, which is why it dominates pressure vessels and does nothing for a wing.

**The process constrains the geometry**, so the choice is made at the concept stage or it is made for you.

---

## Cure

**An autoclave gives pressure and temperature together**, and the pressure is what consolidates the laminate and drives out voids. It is the reference process and it costs a large pressure vessel with a heater in it, whose size is a hard limit on part size.

**Out-of-autoclave prepreg** cures under vacuum bag pressure alone, so about one atmosphere instead of six or seven. That removes the capital limit on part size and puts the void content burden entirely on the resin chemistry and the bagging. **The trade is capital and part size against void content and process latitude**, and out-of-autoclave has far less latitude: a bagging error that an autoclave would push out becomes a void.

**Cure is also a thermal problem.** A thick laminate is an insulator that generates its own heat exotherming, so the middle of a thick part cures at a different temperature and a different rate from the surface. Thickness limits and ramp rates come from that rather than from the resin data sheet.

---

## Tooling

**The tool has to survive the cure and produce the right shape at room temperature**, and those are different requirements because the tool and the part have different thermal expansion.

**An invar tool matches carbon fibre closely and costs a great deal.** An aluminium tool is cheap and moves far more than the part does, so the tool is machined to a shape that is wrong at room temperature and right at cure temperature. **A composite tool matches by construction and has a shorter life.**

**Tool thermal mass sets the cure ramp**, and a heavy tool cannot follow the cycle the resin needs. That is a tooling decision made for a chemistry reason and it is easy to get wrong. See [ToolingAndFixturing](ToolingAndFixturing.md).

---

## Defects

The ones that matter, and their causes are all in the process.

**Porosity and voids**, from insufficient consolidation pressure or entrapped volatiles. The commonest out-of-autoclave defect and the one that most directly attacks the interlaminar strength.

**Delamination**, from a contaminated ply interface, an impact, or a cure that did not consolidate. It is the defect composites are known for and it is the one that grows.

**Wrinkles and fibre waviness**, from a ply forced into a curvature it does not want. **A wrinkle is a strength knockdown that looks like nothing**, and it is easy to bag over.

**Foreign object debris**, principally backing film left between plies, which is a laminate with a crack already in it.

**And an incomplete cure**, which is invisible and is only established by a coupon.

---

## Why inspection is harder here

Composites break the assumptions most [inspection methods](InspectionAndNDE.md) rest on.

**Ultrasonic works and is the workhorse**, because a delamination is a planar reflector normal to the beam, which is the one orientation ultrasonic likes.

**Radiography is nearly useless for delamination**, because a tight planar defect parallel to the beam has almost no absorption contrast. It finds foreign objects and it does not find the defect that matters.

**Eddy current does nothing** on a non-conducting laminate, and magnetic particle less than nothing.

**Thermography and computed tomography both work** and both are expensive.

**So the method list collapses to essentially one plus expensive alternatives**, which is a much weaker position than a metal part, and it is why coupon-based process control carries more of the assurance burden in composites than in metals. See [ProcessQualification](ProcessQualification.md).

---

## Design rules of thumb

- **Choose the layup process at concept.** It constrains the geometry.
- **Treat a process change as a material change.** The allowables belong to the process.
- **Know the autoclave size before designing a part that needs one.**
- **Match the tool expansion or machine the tool to the wrong shape deliberately.**
- **Design out tight concave corners** if the part is to be placed automatically.
- **Assume ultrasonic and coupons.** The rest of the NDE list mostly does not apply.

---

## Failure modes

**A hand layup taken to rate.** The operator is the rate limit.

**An out-of-autoclave part designed to autoclave void content.** One atmosphere is not seven.

**A thick laminate cured on the resin data sheet ramp.** The middle exotherms.

**An aluminium tool machined to the room temperature shape.** The part comes out wrong.

**Radiography specified for delamination.** It will not find it.

**A wrinkle bagged over.** A knockdown that looks like nothing.

---

## References

- [InspectionAndNDE](InspectionAndNDE.md), for why the method list is short here
- [ToolingAndFixturing](ToolingAndFixturing.md), for the expansion match
- [aerospaceMaterials](../../aerospaceMaterials/), for the composite allowables
- [aerospaceStructures](../../aerospaceStructures/), for laminate analysis
