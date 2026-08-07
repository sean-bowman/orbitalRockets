[Home](../README.md) > Diffusion Bonding

# Diffusion Bonding

## Contents

- [Overview](#overview)
- [The mechanism](#the-mechanism)
- [The three requirements](#the-three-requirements)
- [SPF/DB](#spfdb)
- [The inspection problem](#the-inspection-problem)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Two clean surfaces held in contact at temperature and pressure bond by atomic diffusion across the interface. Done properly the joint is indistinguishable from the parent material, with no filler, no fusion zone and no HAZ.

Done improperly it looks the same and it is not, which is the process's central difficulty.

---

## The mechanism

| Stage | Detail |
|---|---|
| **1. Contact** | Asperities on the two surfaces touch and deform plastically |
| **2. Creep and yielding** | The contact area grows under pressure and temperature |
| **3. Void shrinkage** | The remaining voids at the interface close by diffusion |
| **4. Grain boundary migration** | Grains grow across the original interface |

**Stage 4 is what makes the joint indistinguishable.** Once grains have grown across the interface, there is no interface: the microstructure is continuous and the properties are the parent's.

**A joint that stops at stage 3 has closed voids and an intact original interface**, which is a planar array of oxide and it is weak in exactly the way a bifilm is.

---

## The three requirements

| Requirement | Typical value |
|---|---|
| **Temperature** | 0.5 to 0.8 of the melting point in kelvin |
| **Pressure** | Enough to yield the asperities. 1 to 10 MPa typical |
| **Time** | Minutes to hours |
| **Surface cleanliness** | **The one that governs** |

**Surface oxide is what prevents bonding**, and every requirement is really about getting through it.

| Material | Oxide behaviour | Bondability |
|---|---|---|
| **Titanium** | **Dissolves into the bulk at temperature** | **Excellent** |
| Nickel alloys | Stable, needs high pressure | Moderate |
| Stainless | Chromium oxide is stable | Moderate |
| **Aluminium** | **Very stable oxide. Reforms instantly** | **Difficult** |

**Titanium bonds readily because its oxide dissolves.** Oxygen is soluble in alpha titanium to several percent, so the surface oxide simply diffuses into the bulk at bonding temperature and the two clean metal surfaces meet.

**Aluminium is the opposite case.** Its oxide is thermodynamically very stable, it does not dissolve, and it reforms in milliseconds on any exposed surface. Diffusion bonding aluminium requires disrupting the oxide mechanically during the bond, and it is not a routine process.

**That contrast is why diffusion bonding in aerospace means titanium.**

---

## SPF/DB

**Superplastic forming combined with diffusion bonding in one cycle**, which works because titanium's superplastic temperature and its diffusion bonding temperature are the same.

| Structure | Result |
|---|---|
| **Two sheet** | A hollow shell, bonded at the edges |
| **Three sheet** | A sandwich with an integral formed core |
| **Four sheet** | A truss core |

**Stop-off is how the pattern is defined.** A yttria or boron nitride maskant is screen printed where bonding is not wanted; everywhere else bonds. Then gas pressure blows apart the unbonded regions into the die.

**The result is integrally stiffened hollow titanium structure with no fasteners and no welds**, at a part count a fabricated equivalent cannot approach.

**It is slow**, four to eight hours per cycle, because the superplastic strain rate window governs. See [formingProcesses SuperplasticForming.md](../../formingProcesses/docs/SuperplasticForming.md).

---

## The inspection problem

**This is the reason diffusion bonding is not more widely used.**

| Problem | Detail |
|---|---|
| **A weak bond looks like a good bond** | No geometric discontinuity to detect |
| **Radiography sees nothing** | There is no density difference |
| **Ultrasonic is the only option** | And a kissing bond reflects almost nothing |
| Geometry limits access | An internal bond in a sandwich is hard to reach |

**A kissing bond is the failure mode**: surfaces in intimate contact, with an intact oxide between them, transmitting compression perfectly and carrying no tension. Ultrasonically it is nearly invisible because the acoustic impedance mismatch across a closed interface is very small.

**The consequence is that the process is qualified rather than inspected.** Parameters are frozen, coupons are made alongside the parts and destructively tested, and the part is accepted on the process rather than on a measurement of the joint.

**That is an uncomfortable position for a flight critical joint** and it is why diffusion bonded structure is used where the alternative is worse rather than as a general answer.

**Design so the bond is not the sole load path** where it can be arranged, and place bonds where a failure is detectable in service.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Temperature 0.5 to 0.8 T_melt | |
| Pressure 1 to 10 MPa | Enough to yield asperities |
| Surface cleanliness governs | Everything else serves it |
| Titanium bonds readily | Its oxide dissolves |
| Aluminium does not | Its oxide does not |
| Grain growth across the interface is the goal | Not just void closure |
| **A weak bond looks like a good bond** | Qualify the process |
| Avoid a bond as the sole load path | Where possible |

---

## Failure modes

**Kissing bond.** Intimate contact, intact oxide, no tensile strength, and nearly invisible.

**Insufficient surface preparation.** The oxide is not overcome.

**Aluminium diffusion bonded by a titanium recipe.** It does not bond.

**Inspection relied on instead of process qualification.** The methods cannot find the failure mode.

**Stop-off misapplied.** The pattern is wrong and it is unrecoverable.

**Grain coarsening during the long cycle.** Superplasticity and properties both degraded.

---

## Standards

| Standard | Scope |
|---|---|
| AMS 2801 | Heat treatment of titanium alloy parts |
| AMS 4911 | Ti-6Al-4V sheet |
| AMS 2750 | Pyrometry |
| ASTM E2448 | Superplastic properties of metallic sheet |
| ASTM E2700 | Phased array ultrasonic testing |
| NASA-STD-5006 | General welding requirements |

---

## References

1. Ridley, N. (ed.), *Superplasticity: 60 Years After Pearson*, Institute of Materials, 1995.
2. Kazakov, N. F., *Diffusion Bonding of Materials*, Pergamon, 1985.
3. Messler, R. W., *Joining of Materials and Structures*, Butterworth-Heinemann, 2004.
