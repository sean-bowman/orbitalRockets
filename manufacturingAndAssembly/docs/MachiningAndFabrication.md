[Home](../README.md) > Machining and Fabrication

# Machining and Fabrication

## Contents

- [Overview](#overview)
- [What machining is for](#what-machining-is-for)
- [Where the cost is](#where-the-cost-is)
- [Buy-to-fly](#buy-to-fly)
- [Thin walls](#thin-walls)
- [Mirror milling](#mirror-milling)
- [What machining can hold](#what-machining-can-hold)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Machining is the process that can make anything and should be asked to make as little as possible. The physics is in [machiningProcesses](../../aerospaceMaterials/machiningProcesses/); what stays here is when to use it.

---

## What machining is for

**Features, not shapes.** Machining is unbeatable for a tolerance, a surface finish, a hole pattern or an interface, and it is the wrong way to produce a shape that a forming or casting process could make near net.

**The right question is what fraction of a part is machined**, not whether it is. A spun dome with a machined Y-ring interface is right; a dome milled from plate is a shape produced by removing everything that is not it.

---

## Where the cost is

Not in the cutting.

**Setup and fixturing.** Every setup is a labour operation and a new datum, and every new datum is a [tolerance contributor](AssemblyAndIntegration.md). **Reducing setups improves cost and accuracy together**, which is unusual and worth exploiting.

**Programming and proving.** Once per part number rather than per part, so it amortises on a rate programme and dominates a one-off.

**Cycle time**, which is the only term people picture and rarely the largest.

**And the material removed**, which is bought at plate price and sold at scrap price.

---

## Buy-to-fly

The ratio of bought mass to flying mass, and it is the single number that decides whether machining from solid is defensible.

A ratio of 10 to 1 means nine tenths of an expensive aerospace alloy becomes swarf. On titanium or a nickel alloy that is a real fraction of the part cost; on aluminium it is mostly the machine time it took to remove.

**`ProcessComparison` in [aerospaceMaterials](../../aerospaceMaterials/docs/ProcessRouteSelection.md) computes this** against near-net alternatives, along with the allowable knockdown and lead time each route carries. It is not recomputed here.

**The reason to know the number is that it changes the answer non-obviously**: a near net route with a lower allowable can still win, because it needs less material and less machining, and the part gets thicker to compensate at a lower total cost.

---

## Thin walls

Where machining stops being predictable, and it is exactly where launch vehicle structure lives.

**A thin wall deflects away from the cutter**, so the wall comes out thicker than commanded and the error grows with depth of cut and with how unsupported the wall is. `MachiningProcess` in [machiningProcesses](../../aerospaceMaterials/machiningProcesses/) computes the deflection.

**And a machined part moves after machining**, because removing material unbalances the residual stress that was in the plate. An isogrid panel milled from one side bows, and the bow is a function of the plate's stress state rather than of the machining.

**Two consequences for the design.** Symmetric machining bows less than asymmetric. And a stress-relieved plate is worth its premium on anything thin, which is a material specification decision made for a manufacturing reason.

---

## Mirror milling

The answer to the thin wall problem on a large skin, and it is worth knowing because it changes what is designable.

A support head follows the cutter on the opposite side of the skin, so the wall is held rather than free. That removes the deflection, permits a thinner wall, and needs a machine large enough to reach both sides of a launch vehicle panel.

**It is a capital decision that opens a design space**, which is the general shape of most manufacturing capability: the process does not make the design cheaper, it makes a different design possible.

---

## What machining can hold

| Process | Tolerance, fraction of nominal |
|---|---|
| Sand casting | 3e-3 |
| Sheet forming | 1.5e-3 |
| Welding | 1e-3 |
| Additive | 5e-4 |
| Turning and milling | 1e-4 |
| Grinding | 2e-5 |
| Lapping | 5e-6 |

**Three orders of magnitude across the list**, which is why process selection is a tolerance decision before it is a cost one, and why the machined features on a formed part are usually the only ones with a real tolerance on them.

---

## Design rules of thumb

- **Machine features, form shapes.**
- **Count setups.** Fewer is cheaper and more accurate at once.
- **Know the buy-to-fly before defending machining from solid.**
- **Machine symmetrically on anything thin.**
- **Specify stress-relieved plate for thin machined parts.**
- **Put the tolerance on the machined feature**, not on the formed one.

---

## Failure modes

**A shape milled from plate.** Removing everything that is not the part.

**Cost estimated from cycle time.** Setup and programming are usually larger.

**A thin wall machined without a deflection allowance.** It comes out thick.

**An asymmetric machined panel.** It bows and nobody knows by how much.

**A tolerance placed on a formed feature.** The process cannot hold it.

---

## References

- [machiningProcesses](../../aerospaceMaterials/machiningProcesses/), which carries tool life, chatter and deflection
- [ProcessRouteSelection](../../aerospaceMaterials/docs/ProcessRouteSelection.md), for buy-to-fly
- [AssemblyAndIntegration](AssemblyAndIntegration.md), for what each setup costs downstream
