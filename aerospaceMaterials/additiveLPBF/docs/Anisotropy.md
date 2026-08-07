[Home](../README.md) > Anisotropy

# Anisotropy

## Contents

- [Overview](#overview)
- [Why the layers are a direction](#why-the-layers-are-a-direction)
- [How much](#how-much)
- [Fatigue is worse than static](#fatigue-is-worse-than-static)
- [What HIP recovers](#what-hip-recovers)
- [Thermal conductivity](#thermal-conductivity)
- [Putting orientation on the drawing](#putting-orientation-on-the-drawing)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

An additive part has a grain, in the same sense that a rolled plate has one. Properties measured along the build direction differ from properties measured across it, and the difference is large enough to matter.

The difference between additive and wrought is that the direction is chosen at build time rather than at the mill, so it can be optimised, and so it can be got wrong.

---

## Why the layers are a direction

Three mechanisms, all pointing the same way.

**Columnar grains.** Grains grow along the thermal gradient, which points down into the previously solidified material. So they grow vertically, crossing several layers, and produce a strong texture.

**Interlayer bonds.** Every layer boundary is a weld. A good one is indistinguishable from the bulk; a marginal one is a plane of weakness, and they are all perpendicular to the Z axis.

**Defect orientation.** Lack of fusion defects lie in the build plane. That makes them perpendicular to a Z tensile stress, which is the worst possible orientation.

**All three make Z the weak direction**, and the third dominates.

---

## How much

| Condition | Z yield ratio | Z ultimate ratio | Z elongation ratio |
|---|---|---|---|
| **AlSi10Mg as-built** | 0.93 | 0.88 | **0.70** |
| AlSi10Mg stress relieved | 0.96 | 0.94 | 0.85 |
| **316L as-built** | 0.90 | 0.93 | 0.80 |
| **Inconel 718 HIP + STA** | **0.95** | 0.94 | 0.85 |
| Ti-6Al-4V HIP + annealed | 0.96 | 0.95 | 0.85 |

**Elongation is hit hardest, always.** Strength falls by 5 to 12 percent and ductility by 15 to 30. That is characteristic of a defect-driven mechanism rather than a texture-driven one: defects reduce the strain to failure far more than they reduce the stress to yield.

**A part designed on XY properties and built in Z is undersized by the ratio**, and a part whose orientation was never specified has to be designed to the worst case.

---

## Fatigue is worse than static

**The static knockdown understates the fatigue knockdown substantially.**

Fatigue is controlled by crack initiation at the largest defect, and the largest defect is usually a lack of fusion flaw lying in the build plane. Loaded in Z, that flaw is a crack normal to the stress.

| Property | Typical Z knockdown |
|---|---|
| Yield strength | 5 to 10 % |
| Ultimate strength | 5 to 12 % |
| **Fatigue strength, as-built** | **30 to 50 %** |
| Fatigue strength, HIP and machined | 10 to 15 % |

**As-built surface roughness compounds it.** A 20 um Ra surface has notches at every particle, so a fatigue critical additive surface has two initiation mechanisms working together.

---

## What HIP recovers

| Defect | HIP effect |
|---|---|
| **Keyhole porosity** | Closes and bonds. Largely recovered |
| **Lack of fusion** | Closes geometrically; the oxidised surfaces frequently do not bond |
| **Entrapped gas** | Compressed, not removed. Re-expands on later heat treatment |
| Texture | Unaffected, unless the cycle recrystallises |

**HIP moves the Z knockdown from about 25 percent to about 5 percent** for a well-processed part, and that is why fatigue critical additive hardware is always HIPed. It does not make the part isotropic.

**The remaining 5 percent is texture and interlayer bonds**, and no post-processing removes it.

---

## Thermal conductivity

**Also anisotropic, and it is forgotten more often than the mechanical properties.**

Layer boundaries and residual porosity impede heat flow across the layers. Z conductivity typically runs 5 to 15 percent below XY as-built.

**For a regenerative chamber liner or a heat exchanger that is a real effect**, and it points the same way as the mechanical anisotropy: the build direction is the weak one.

---

## Putting orientation on the drawing

**If the orientation is not specified, nothing stops a build being oriented badly**, and the worst case has to be assumed.

The [`LpbfQualification`](../additiveLpbfLibrary/LpbfQualification.py) class carries an `unknown` orientation with a knockdown of 0.85, worse than the Z value of 0.90, for exactly that reason. Specifying the orientation on the drawing recovers 5 percent of the allowable for free.

**What a drawing should carry:**

- The build direction relative to a part datum
- Any surface that must be up-skin or down-skin
- Where supports may and may not contact
- Whether the orientation may be changed without a review

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Z is the weak direction, always | Three mechanisms all agree |
| Static knockdown | 5 to 12 % |
| **Fatigue knockdown, as-built** | **30 to 50 %** |
| Fatigue knockdown, HIP and machined | 10 to 15 % |
| Elongation knockdown | 15 to 30 %, always the worst |
| HIP recovery | Z knockdown 25 % to 5 % |
| Unspecified orientation | Assume worse than Z |
| Put the build direction on the drawing | It is free |

---

## Failure modes

**Designed on XY properties, built in Z.** Undersized by the ratio.

**Static knockdown applied to a fatigue problem.** Understates it by a factor of three or more.

**Orientation not on the drawing.** Nothing stops a bad build orientation.

**HIP assumed to make the part isotropic.** It reduces the anisotropy and does not remove it.

**Thermal anisotropy ignored on a heat exchanger.** Z conductivity is lower.

**A vendor's XY datasheet used as the allowable.** It is the best direction, quoted alone.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM F3122** | Evaluating mechanical properties of metal additive parts |
| ISO/ASTM 52921 | Standard terminology for coordinate systems and test methodologies |
| ASTM E8 | Tension testing |
| ASTM E466 | Force controlled constant amplitude axial fatigue |
| NASA-STD-6030 | Additive manufacturing requirements |

---

## Tool interface

```python
from LpbfQualification import LpbfQualification, ORIENTATION_KNOCKDOWN

for orientation in ('XY', '45', 'Z', 'unknown'):
    print(orientation, ORIENTATION_KNOCKDOWN[orientation]['factor'])

qualification = LpbfQualification()
qualification.setInputs({'consequenceClass': 'AXB', 'buildOrientation': 'unknown'})
print(qualification.calculateAllowablesPath()['orientationNote'])
```

---

## References

1. ASTM F3122-14, *Standard Guide for Evaluating Mechanical Properties of Metal Materials Made via Additive Manufacturing Processes*.
2. Kok, Y. et al., "Anisotropy and Heterogeneity of Microstructure and Mechanical Properties in Metal Additive Manufacturing", *Materials and Design*, Vol. 139, 2018.
3. Wycisk, E. et al., "Effects of Defects in Laser Additive Manufactured Ti-6Al-4V on Fatigue Properties", *Physics Procedia*, Vol. 56, 2014.
4. Gradl, P. R. et al., "Metal Additive Manufacturing in Aerospace: A Review", *Materials and Design*, Vol. 209, 2021.
