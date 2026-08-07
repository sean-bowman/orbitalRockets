[Home](../README.md) > Wire Arc Additive

# Wire Arc Additive Manufacturing

## Contents

- [Overview](#overview)
- [The process](#the-process)
- [What it achieves](#what-it-achieves)
- [Why the rate matters](#why-the-rate-matters)
- [Residual stress and distortion](#residual-stress-and-distortion)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

WAAM is arc welding with a robot, depositing bead on bead to build a shape. The equipment is a welding power supply, a wire feeder and a robot, all of which are commodity items, and the deposition rate is two orders of magnitude above powder bed processes.

It makes preforms, not parts.

---

## The process

| Element | Detail |
|---|---|
| **Energy** | GMAW, GTAW, or plasma arc |
| **Feedstock** | **Standard welding wire.** Cheap and available |
| **Motion** | Industrial robot, or a gantry |
| Shielding | Local gas shroud, or a tent for reactive alloys |
| **Rate** | **500 to 5000 cm^3/h** |

**The feedstock cost advantage is substantial.** Welding wire is a commodity at a fraction of the price of gas atomised powder, and there is no unfused powder to recover, sieve and re-certify.

**Cold metal transfer and similar controlled short circuit processes** are preferred because they put less heat in per unit deposited, which reduces the distortion that is WAAM's main problem.

**Titanium WAAM needs a full inert enclosure**, not a local shroud, because the deposited material stays hot enough to oxidise for a long time behind the arc.

---

## What it achieves

| Property | Value |
|---|---|
| **Rate** | **500 to 5000 cm^3/h.** 10 to 100x LPBF |
| **Tolerance** | **IT14. Very coarse** |
| Surface | Very rough, a visible bead profile |
| **Size** | **Metres.** Effectively unlimited |
| Minimum wall | 3 to 8 mm, one or two bead widths |
| Machining allowance | **3 to 6 mm per surface** |
| Properties | Good after heat treatment, and anisotropic |

**The machining allowance is what defines the process.** Every surface needs 3 to 6 mm removed, so WAAM makes a near net preform that is then machined conventionally.

**That framing is important because it sets the comparison.** WAAM does not compete with LPBF; it competes with a forging or a large plate, and against those it wins on lead time, on tooling and on buy-to-fly.

---

## Why the rate matters

**A 40 kg titanium structural part illustrates it.**

| Route | Buy-to-fly | Deposition or removal time | Lead |
|---|---|---|---|
| Machined from plate | 10 : 1 | Very long | 16 wk |
| Forged and machined | 4 : 1 | Long | 30 wk plus tooling |
| **WAAM and machined** | **1.5 : 1** | **~20 hours deposition** | **6 wk** |
| LPBF | -- | Exceeds the build volume | -- |

**LPBF cannot make it at all** at that size, so the comparison is against wrought routes.

**Against a forging, WAAM wins on lead time and tooling** by a very large margin: no die, no 30 week queue, and a design change is a program change.

**Against machining from plate, WAAM wins on material** by a factor of nearly seven in titanium, which at the alloy's cost index of 8.5 is a very large number.

**That is the WAAM case in full**, and it is why the process is being adopted for large titanium and nickel structure despite its coarseness.

---

## Residual stress and distortion

**The main technical problem, and it follows directly from the heat input.**

| Cause | Detail |
|---|---|
| **High heat input per unit volume** | It is arc welding |
| **Many thermal cycles** | Every layer reheats those below |
| **Constrained contraction** | Against the baseplate |

| Control | Detail |
|---|---|
| **Rigid baseplate clamping** | Restrain during the build |
| **Deposition sequence** | Balance the heat, alternate directions |
| **Interpass temperature control** | Wait, or actively cool |
| **Interpass rolling** | Roll each layer. It refines the grain and reduces the stress |
| Symmetric building | Build both sides of a symmetric part together |
| **Post-build stress relief** | Before removing from the baseplate |

**Interpass rolling is the interesting one.** A roller passes over each deposited layer, plastically working it, which both introduces compressive stress that offsets the thermal tensile stress and breaks up the coarse columnar grain structure into something finer and more equiaxed. It improves the properties and the distortion at the same time.

**Remove from the baseplate only after stress relief**, or the accumulated stress releases as distortion in exactly the way a machined plate bows. See [machiningProcesses DistortionControl.md](../../machiningProcesses/docs/DistortionControl.md).

**The grain structure is very coarse columnar** without interpass working, with grains growing through many layers. In titanium these can be tens of millimetres long, and the anisotropy that produces is substantial.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| WAAM makes preforms | 3 to 6 mm allowance per surface |
| Rate 500 to 5000 cm^3/h | 10 to 100x LPBF |
| Minimum wall 3 to 8 mm | One or two beads |
| Compare against forging and plate | Not against LPBF |
| Rigid clamping and a deposition sequence | Distortion |
| Interpass rolling | Stress and grain structure together |
| Stress relieve before removing from the plate | |
| Full inert enclosure for titanium | Not a local shroud |

---

## Failure modes

**Fine features expected.** Minimum wall is a bead width.

**Removed from the baseplate before stress relief.** It distorts.

**Local shroud on titanium.** Oxidation behind the arc.

**Coarse columnar structure not addressed.** Severe anisotropy.

**Machining allowance underestimated.** Surfaces do not clean up.

**Compared against LPBF.** They are different applications.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-6030** | Additive manufacturing requirements for spaceflight |
| **AWS D20.1** | Fabrication of metal components using additive manufacturing |
| ISO/ASTM 52900 | Additive manufacturing terminology |
| AWS D17.1 | Fusion welding for aerospace |
| ASTM F3187 | Directed energy deposition of metals |
| ASTM E2700 | Phased array ultrasonic |

---

## References

1. Williams, S. W. et al., "Wire + Arc Additive Manufacturing", *Materials Science and Technology*, Vol. 32, 2016.
2. Colegrove, P. A. et al., "Microstructure and Residual Stress Improvement in Wire and Arc Additively Manufactured Parts through High-Pressure Rolling", *Journal of Materials Processing Technology*, Vol. 213, 2013.
3. AWS D20.1, *Specification for Fabrication of Metal Components using Additive Manufacturing*.
