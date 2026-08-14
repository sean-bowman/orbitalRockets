[Home](../README.md) > Forming and Spinning

# Forming and Spinning

## Contents

- [Overview](#overview)
- [Why a dome is spun](#why-a-dome-is-spun)
- [Springback](#springback)
- [The forming limit](#the-forming-limit)
- [Rolling a barrel](#rolling-a-barrel)
- [Hot against cold](#hot-against-cold)
- [What forming does to the material](#what-forming-does-to-the-material)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Forming makes shapes and machining makes features, and almost every large launch vehicle part is the product of both. The equations are in [formingProcesses](../../aerospaceMaterials/formingProcesses/); what stays here is the selection.

---

## Why a dome is spun

A tank dome is a doubly curved shell several metres across in a few millimetres of material, and there are only a handful of ways to make one.

**Spinning** forms it from a circular blank over a mandrel with a roller. One tool, one blank, no weld, and a wall thickness that varies in a way the process controls rather than eliminates.

**Gore welding** forms flat or singly curved panels and welds them into a dome. Cheaper tooling, more welds, and every weld is a [knockdown](../../fluidSystems/fluidSystemsLibrary/docs/Welds.md) and an inspection.

**Stretch forming** over a die, which is fast and needs a die per shape.

**Explosive and hydro forming** for shapes the others cannot reach.

**The trade is tooling cost against weld count**, and the weld count is what decides it on a pressure vessel: a spun dome has no weld in the membrane and a gored one has many, and each is a fracture critical location that has to be inspected. See [InspectionAndNDE](InspectionAndNDE.md).

---

## Springback

The part is a different shape when the tool comes off, and it is the reason forming is iterative.

Elastic recovery unbends the part by an amount that scales with the ratio of yield strength to elastic modulus, so **a stronger alloy springs back more for the same forming operation.** That is a genuinely awkward property: the material chosen for its strength is the one hardest to form to shape.

**Aluminium and titanium behave very differently here**, because their strength-to-modulus ratios differ by more than either alone suggests. Titanium is usually formed hot for exactly this reason.

**The practical answer is overbend**, and the amount is established on the first article and carried in the tool. That makes the first part of a run the one that pays for the process development, which is a [learning curve](RateAndLearning.md) in its most literal form.

---

## The forming limit

How far a sheet can be strained before it necks, expressed as a diagram of major against minor strain.

Two things about it matter at the design stage.

**It is a property of the material and the strain path**, so a part formed in two operations can reach a strain that one operation cannot.

**And plane strain is the worst path**, which is where a long shallow feature lives. A design that looks gentle can sit exactly on the worst part of the diagram.

`FormingProcess` in [formingProcesses](../../aerospaceMaterials/formingProcesses/) computes the limit and the minimum bend radius. **This domain consumes them and does not reproduce them.**

---

## Rolling a barrel

The tank barrel, which is the other half of the worked example.

Plate is rolled to a cylinder and welded along its length. Two things come out of it and both appear in the [tolerance stack](AssemblyAndIntegration.md).

**Roundness after roll**, which is the dominant contributor in the worked case at half the statistical stack. It is set by the rolling process, the plate thickness and how the cylinder is supported after it comes off.

**And the longitudinal weld shrinkage**, which pulls the cylinder out of round in a way the rolling did not.

**The two together are three quarters of the stack**, which is why the assembly tolerance conversation on a tank is really a conversation about the barrel.

---

## Hot against cold

**Cold forming** keeps the strength the material was delivered with, work hardens as it goes, and springs back more.

**Hot forming** relieves the stress as it forms, springs back far less, and either needs a heat treatment afterwards or accepts a lower allowable. It also costs a furnace, a tool that survives the temperature, and a longer cycle.

**On titanium the choice is usually made for you** by the springback and the limited cold formability. On aluminium it is a real trade and it turns on whether the part can be solution treated and aged afterwards, which is [postProcessing](../../aerospaceMaterials/postProcessing/).

---

## What forming does to the material

Named because it is the interface to [aerospaceMaterials](../../aerospaceMaterials/) and it is easy to forget.

**Thickness varies**, and a spun dome is thinner at the knuckle than at the crown by design. The structural analysis has to use the formed thickness distribution rather than the blank.

**Properties become directional.** Rolled and formed material has a grain direction and different allowables along, across and through it, which is the [short transverse](../../aerospaceMaterials/wroughtMaterials/) problem.

**And residual stress is left behind**, which is what makes a formed part move when it is subsequently machined. See [MachiningAndFabrication](MachiningAndFabrication.md).

---

## Design rules of thumb

- **Count the welds before choosing between a spun and a gored dome.**
- **Expect springback to scale with strength.** The strong alloy is the awkward one.
- **Check the strain path, not just the strain.** Plane strain is the worst case.
- **Design the barrel roundness.** It is half the assembly stack.
- **Use the formed thickness in the analysis**, not the blank thickness.
- **Decide hot or cold on the heat treatment that follows.**

---

## Failure modes

**A gored dome on a fracture critical tank.** Every weld is an inspection and a knockdown.

**Springback treated as a tooling problem.** It is a material property.

**A gentle-looking feature in plane strain.** The worst path on the diagram.

**Blank thickness used in the analysis.** The formed part is thinner where it matters.

**A formed part machined without stress relief.** It moves.

---

## References

- [formingProcesses](../../aerospaceMaterials/formingProcesses/), which carries springback and the forming limit
- [spinCasting](../../aerospaceMaterials/spinCasting/), for the centrifugal casting alternative
- [Welds](../../fluidSystems/fluidSystemsLibrary/docs/Welds.md), for what each weld costs
- [wroughtMaterials](../../aerospaceMaterials/wroughtMaterials/), for the directional allowables
