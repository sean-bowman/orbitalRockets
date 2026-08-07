[Home](../README.md) > Process Fundamentals

# Process Fundamentals

## Contents

- [Overview](#overview)
- [True centrifugal casting](#true-centrifugal-casting)
- [Horizontal against vertical axis](#horizontal-against-vertical-axis)
- [Semi-centrifugal and centrifuge](#semi-centrifugal-and-centrifuge)
- [The pour](#the-pour)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

The process is simple to describe and the details decide whether it works: how fast to spin, when to pour, how fast to pour, and how the mould manages heat.

---

## True centrifugal casting

**No core.** The bore is formed by the centrifugal field holding the melt against the mould wall.

| Step | Detail |
|---|---|
| **Mould preparation** | Coated, preheated |
| **Spin up** | To speed before the pour, not during it |
| **Pour** | Along the length, at a controlled rate |
| **Hold** | Spinning until fully solid |
| **Slow and extract** | |

**Spinning up before the pour is not optional.** Pouring into a mould that is still accelerating gives a melt that has not been distributed by the field, and the result is a thick bottom.

**Holding until fully solid** is what stops the melt slumping. Stopping the spin while the core is still liquid produces exactly the defect the process exists to avoid.

**The wall thickness is set by the pour mass**, not by tooling. That is the process's most useful property: one mould makes a range of wall thicknesses simply by pouring more or less.

```
m = rho * pi * D * t * L
```

---

## Horizontal against vertical axis

| Axis | Bore shape | Length | Use |
|---|---|---|---|
| **Horizontal** | **Parallel** | Long, up to several metres | Pipe, tube, liners |
| **Vertical** | **Parabolic** | Short | Rings, short bushings |

**The parabola on a vertical machine is gravity competing with the field along the length.** At the top the only radial force is centrifugal; at the bottom gravity adds a downward component, so the melt sits slightly thicker there and the free surface curves.

```
bore profile ~ parabolic, with the difference growing as L^2 / (omega^2 R)
```

**A higher speed flattens the parabola** because it makes the centrifugal field dominant, but the practical answer for anything long is a horizontal machine.

**Vertical machines are simpler and cheaper** and they are the right choice for a short ring where the parabola is inside the machining allowance anyway.

---

## Semi-centrifugal and centrifuge

**Semi-centrifugal** uses a core to form the bore and the field to feed and densify the casting. It makes discs, wheels and pulleys: parts that are axisymmetric but not hollow in the way a pipe is.

**The benefit is feeding rather than bore formation.** The field pressurises the melt against the outer periphery, which feeds the solidification shrinkage far better than gravity alone. The centre, where the field is weakest, is where the porosity ends up, and that is usually machined away for the bore anyway.

**Centrifuge casting** puts several small moulds on a rotating arm, fed through radial runners from a central sprue. The field acts as the feeding pressure.

| Application | Why |
|---|---|
| Small complex parts | Pressure feeding fills thin sections |
| Jewellery and dental | The classic use |
| Reactive alloys in vacuum | Combined with vacuum induction melting |

**It is a filling aid rather than a segregation process**, and the density separation benefit is largely absent because the parts are small and freeze fast.

---

## The pour

| Parameter | Effect |
|---|---|
| **Pour temperature** | Superheat above the liquidus. Too little and it freezes before distributing |
| **Pour rate** | Too fast and the melt piles up; too slow and the first metal freezes |
| **Pour distribution** | Along the length, usually by a traversing spout |
| Pour position | Radially, so the melt enters near the mould wall |

**Superheat is typically 90 to 120 K.** Enough to distribute along the mould before freezing begins, and not so much that the mould coating is damaged or the grain structure coarsens.

**A traversing spout is standard on a long horizontal casting.** Pouring at one end and relying on the melt to run along the mould gives a thick end and a thin one, so the spout moves along the length during the pour.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Spin up before pouring | Not during |
| Hold spinning until fully solid | Or the core slumps |
| Wall thickness set by pour mass | One mould, many walls |
| Superheat | 90 to 120 K |
| Horizontal for long parts | Vertical gives a parabolic bore |
| Traversing spout on long castings | Or the wall tapers |
| Semi-centrifugal for discs | The field feeds rather than forms |

---

## Failure modes

**Poured during spin-up.** A thick bottom.

**Spin stopped before full solidification.** The core slumps.

**Insufficient superheat.** The melt freezes before it distributes.

**Single-point pour on a long casting.** The wall tapers.

**Vertical axis on a long part.** A parabolic bore outside the allowance.

---

## Standards

| Standard | Scope |
|---|---|
| ASTM A451 | Centrifugally cast austenitic steel pipe |
| ASTM A426 | Centrifugally cast ferritic alloy pipe |
| ASTM B505 | Copper alloy continuous castings |
| ISO 8062 | Casting tolerances and machining allowances |

---

## References

1. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
2. ASM Handbook Volume 15, *Casting*.
3. Janco, N., *Centrifugal Casting*, American Foundrymen's Society, 1988.
