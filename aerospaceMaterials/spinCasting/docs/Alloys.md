[Home](../README.md) > Alloys

# Alloys for Centrifugal Casting

## Contents

- [Overview](#overview)
- [The alloys](#the-alloys)
- [What makes an alloy suit the process](#what-makes-an-alloy-suit-the-process)
- [Titanium](#titanium)
- [Bimetallic castings](#bimetallic-castings)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Centrifugal casting suits most castable alloys and it suits some far better than others. The discriminators are density, freezing range and reactivity.

---

## The alloys

| Alloy | Density | Use | Notes |
|---|---|---|---|
| **Carbon and alloy steel** | 7000 | Pipe, rolls, liners | The volume application |
| **316L and austenitic stainless** | 7000 | Corrosion service pipe, liners | Wide freezing range; feeding matters |
| **Bronze** | 8000 | Bushings, bearings | The classic. High density helps separation |
| **Inconel 625** | 7600 | Corrosive and hot service | Needs vacuum or inert melting |
| Ductile and grey iron | 7000 | Pipe, cylinder liners | Very well suited |
| Aluminium | 2400 | Occasional | Low density means a higher speed for the same benefit |
| **Titanium** | 4400 | **Not practical** | See below |

---

## What makes an alloy suit the process

**High density.** The Stokes velocity scales with the density difference between melt and inclusion, so a dense melt separates a light oxide faster. Bronze at 8000 kg/m^3 separates an alumina inclusion nearly twice as fast as aluminium at 2400 does, at the same G-factor.

**A narrow freezing range.** A wide range gives a long mushy zone, and inclusions cannot migrate through a mush. The separation effectively stops once the local solid fraction reaches coherency, so a wide-range alloy has a shorter window.

**Low reactivity.** The melt is in contact with a mould coating for the whole solidification, at high G, with vigorous shearing. A reactive alloy attacks the coating and picks up its constituents.

**Moderate melting point.** A permanent mould has a life, and it is short above about 1600 degC.

---

## Titanium

**Not practical centrifugally, and the reasons are worth stating because they are the same reasons titanium is hard to cast at all.**

| Problem | Detail |
|---|---|
| **Reactivity** | Molten titanium reduces every common refractory. It picks up oxygen from the mould |
| **Alpha case** | The result is a cased surface on every face, inside and out |
| **Melting** | It has to be melted in vacuum or inert, so the whole machine has to be enclosed |
| Coating | No coating survives contact for the solidification time |

**Titanium castings are made**, in rammed graphite moulds under vacuum, and they are investment cast rather than centrifugally cast. Even then the alpha case is removed chemically afterwards. See [postProcessing AlphaCaseRemoval.md](../../postProcessing/docs/AlphaCaseRemoval.md).

**The centrifugal variant that does exist is centrifuge casting under vacuum**, used for small titanium parts, and it uses the field for filling rather than for segregation.

---

## Bimetallic castings

**A genuine speciality of the process and worth knowing about.**

Pour one alloy, let it partly solidify, then pour a second. The field holds them in concentric layers and the interface is metallurgically bonded.

| Application | Layers |
|---|---|
| **Rolling mill rolls** | Hard wear-resistant shell on a tough core |
| Cylinder liners | Wear surface on a cheaper backing |
| Bearings | Bearing alloy on a steel shell |

**The interface is the engineering problem.** Pour the second alloy too early and they mix; too late and they do not bond. The window is set by the first alloy's solidification and it is narrow.

**Nothing else produces a metallurgically bonded bimetallic cylinder as simply**, which is why the process survives in that niche regardless of what else is available.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Dense melts separate faster | Bronze better than aluminium |
| Narrow freezing range | Longer separation window |
| Reactive alloys | Not suitable |
| Above ~1600 degC | Expendable lining, not a permanent mould |
| Titanium | Not centrifugally cast |
| Bimetallic | A real speciality, and the pour window is narrow |

---

## Failure modes

**Reactive alloy in a coated permanent mould.** Coating attacked, and the melt contaminated.

**Wide freezing range alloy at a low G-factor.** The mush forms before the inclusions clear.

**Aluminium spun at a steel speed.** The density difference is smaller and the separation is weaker.

**Bimetallic second pour mistimed.** Mixing, or no bond.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM A451** | Centrifugally cast austenitic steel pipe |
| ASTM A426 | Centrifugally cast ferritic alloy pipe |
| ASTM A660 | Centrifugally cast carbon steel pipe |
| ASTM B505 | Copper alloy continuous castings |
| ASTM A532 | Abrasion resistant cast irons, for roll shells |

---

## References

1. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
2. ASM Handbook Volume 15, *Casting*.
3. Chirita, G. et al., "Sensitivity of Different Al-Si Alloys to Centrifugal Casting Effect", *Materials and Design*, Vol. 31, 2010.
