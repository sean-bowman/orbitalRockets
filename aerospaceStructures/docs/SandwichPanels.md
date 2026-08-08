[Home](../README.md) > Sandwich Panels

# Sandwich Panels

## Contents

- [Overview](#overview)
- [Why the separation buys so much](#why-the-separation-buys-so-much)
- [The five failure modes](#the-five-failure-modes)
- [Wrinkling](#wrinkling)
- [Intracell dimpling](#intracell-dimpling)
- [Shear crimping and core shear](#shear-crimping-and-core-shear)
- [Cores](#cores)
- [What sandwiches are bad at](#what-sandwiches-are-bad-at)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A sandwich panel is an I-beam smeared out over an area. The facesheets carry bending as a force couple, the core carries the shear and holds the facesheets apart, and the separation is what buys the stiffness.

---

## Why the separation buys so much

**Flexural rigidity goes as the square of the separation while mass goes almost linearly with core depth.**

```
D = E_f t_f d^2 / 2
```

| Change | Rigidity | Mass |
|---|---|---|
| Double the core depth | **~4x** | **~1.2x** |
| Double the facesheet | 2x | 1.8x |

**Deepening the core is the cheapest stiffness available in structures.** The core contributes almost nothing to the mass because it is mostly air, and it contributes the entire lever arm.

**The comparison against an equal-mass solid plate is the honest one**, and it is enormous: the reference panel is **375x** stiffer in bending than a solid plate of the same areal mass.

**The thin-facesheet approximation** neglects the facesheets bending about their own axes. That term is 0.013 percent of the total for the reference panel, so it is genuinely negligible, and the class reports it so the assumption can be checked rather than assumed.

---

## The five failure modes

| Mode | What happens | Governed by |
|---|---|---|
| **Facesheet yield** | The facesheet reaches its allowable | Face material |
| **Wrinkling** | The facesheet buckles into the core, short wavelength | Face and core moduli |
| **Intracell dimpling** | The facesheet dips into one cell | Cell size |
| **Shear crimping** | A wrinkle through the whole section | Core shear modulus |
| **Core shear** | The core fails in shear | Core shear strength |

**The governing mode moves with the geometry**, so checking the mode you expect to govern is not a design process. That is why the class screens all five.

**A sixth mode exists and is not modelled here: flatwise tension**, the bond between facesheet and core letting go. It is a process and inspection problem more than an analysis one, and it is the reason sandwich structure is qualified by coupon testing.

---

## Wrinkling

```
sigma_wr = K (E_f E_c G_c)^(1/3)
```

**It does not depend on the panel length or the boundary conditions at all.** That is the property that catches people, because anyone whose intuition comes from column buckling expects a longer panel to be weaker.

**Wrinkling is a local instability.** The facesheet buckles into the core at a wavelength of a few core depths, and what resists it is the core's elastic foundation stiffness. The panel could be a metre long or a centimetre; the wrinkling stress is the same.

**The theoretical coefficient is 0.91 and the design value is 0.50.** Wrinkling is imperfection sensitive in the same way shell buckling is, for the same reason: closely spaced modes. The nearly two-to-one gap between theory and practice is the same story told at a smaller scale.

---

## Intracell dimpling

```
sigma_d = K E_f (t_f / s)^2 / (1 - nu^2)
```

with `s` the cell inscribed diameter.

**It scales as the inverse square of the cell size**, which makes it the mode most exposed to a late change. Doubling the cell size quarters the dimpling stress.

**Core cell size is the parameter most likely to be substituted for availability**, and a substitution from 1/8 inch to 3/16 inch cell is a 2.25x reduction in dimpling allowable. That is a design change, not a procurement one.

**Foam cores have no cells and therefore no dimpling mode at all**, which is one of their few advantages over honeycomb.

---

## Shear crimping and core shear

**Crimping is a wrinkle whose wavelength is comparable to the core depth**, and it governs when the core shear modulus is low. Foam-cored panels crimp where honeycomb ones wrinkle.

**Core shear stress is carried over the separation, not the core depth**, because the shear flows between the facesheet centroids:

```
tau = V / d
```

**Honeycomb is strongly orthotropic.** The ribbon (L) direction is roughly twice as stiff and strong in shear as the transverse (W) direction, so the core orientation is a design decision that must appear on the drawing.

---

## Cores

| Core | Density | Shear modulus L | Notes |
|---|---|---|---|
| Aluminium 3.1 pcf | 49.7 | 310 MPa | Lightweight, 3/16 in cell |
| **Aluminium 4.5 pcf** | 72.1 | **448 MPa** | **The general purpose choice** |
| Aluminium 8.1 pcf | 130 | 924 MPa | High load, 1/8 in cell, thin faces |
| **Nomex 3.0 pcf** | 48.1 | 44 MPa | Non-metallic, radar transparent, soft |
| **Rohacell foam 51** | 52.0 | 19 MPa | Closed cell, isotropic, no dimpling |

**Nomex is an order of magnitude softer in shear than aluminium at the same density**, which moves the governing mode toward crimping and core shear.

**Closed-cell foam does not trap water and open honeycomb does.** Water ingress into a honeycomb panel is a real service problem: it adds mass, it freezes and expands, and it corrodes aluminium core. Vented and sealed designs both exist and both have failure histories.

---

## What sandwiches are bad at

| Weakness | Detail |
|---|---|
| **Concentrated loads** | The core crushes. Needs a potted insert or a hard point |
| **Attachments** | Every fastener needs an insert |
| **Water ingress** | Honeycomb traps it |
| **Impact** | Local core crush is invisible from outside |
| **Inspection** | Disbonds are hard to find. Tap test or ultrasonic |
| Edge closure | Every edge needs a detail |

**A sandwich panel has no capability at a point.** Every fastener, every bracket and every edge needs a designed detail, and those details are where the mass that the core saved comes back.

**Barely visible impact damage is the classic composite sandwich problem.** A tool drop crushes the core locally with almost no external mark, and the panel's compression strength there is substantially reduced.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Rigidity goes as `d^2`, mass as `d` | Deepen the core |
| Stiffness advantage over equal-mass solid | 100 to 400x |
| Wrinkling is length independent | The counterintuitive one |
| Wrinkling design coefficient | 0.50, against 0.91 theoretical |
| Dimpling goes as `1/s^2` | Cell size substitutions are design changes |
| Core shear acts over `d`, not `h_c` | |
| Honeycomb L is ~2x W in shear | Put the orientation on the drawing |
| Every attachment needs an insert | That is where the mass returns |

---

## Failure modes

**Only the expected mode checked.** The governing one moves with the geometry.

**A longer panel assumed weaker in wrinkling.** It is not.

**Core substituted to a larger cell.** Dimpling allowable falls as the square.

**Fastener through a sandwich with no insert.** The core crushes.

**Honeycomb panel unsealed in a wet environment.** Water ingress, mass, freeze damage, corrosion.

**Core orientation omitted from the drawing.** Half the shear capability if it is built rotated.

---

## Worked numbers

From [`SandwichPanel`](../aerospaceStructuresLibrary/SandwichPanel.py), 0.5 mm 6061-T6 facesheets on 25 mm aluminium 4.5 pcf core:

| Quantity | Value |
|---|---|
| Separation `d` | 25.50 mm |
| Flexural rigidity | 11201 N*m |
| Areal mass | 4.503 kg/m^2 |
| **Stiffness advantage** | **375x an equal-mass solid plate** |
| Facesheet own-axis term | **0.013 %** of the total |
| Wrinkling stress | 1362 MPa |
| Dimpling stress | 1706 MPa |
| Crimping stress | 11653 MPa |

**Wrinkling is above the facesheet yield here**, because the facesheet is thin and the core is stiff. For this geometry facesheet yield governs, which is exactly why the class screens rather than assuming.

---

## Standards

| Standard | Scope |
|---|---|
| **MIL-HDBK-23** | Structural sandwich composites |
| ASTM C393 | Core shear properties by beam flexure |
| ASTM C365 | Flatwise compressive properties of sandwich cores |
| ASTM C297 | Flatwise tensile strength of sandwich constructions |
| ASTM C273 | Shear properties of sandwich core materials |
| **CMH-17** | Composite materials handbook, sandwich volume |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'aerospaceStructuresLibrary')

from SandwichPanel import SandwichPanel, CORE_TYPES

panel = SandwichPanel()
panel.setInputs({'faceMaterial': '6061-T6', 'faceThickness': 0.0005,
                 'coreType': 'aluminium honeycomb 4.5 pcf', 'coreDepth': 0.025,
                 'panelLength': 0.8, 'panelWidth': 0.5,
                 'appliedMoment': 500.0, 'appliedShear': 2000.0})

screen = panel.screenFailureModes()
for mode, margin in sorted(screen['margins'].items(), key = lambda item: item[1]):
    print(f'{mode:20s} {margin:+8.3f}')
print(screen['governingMode'])
```

---

## References

1. MIL-HDBK-23A, *Structural Sandwich Composites*.
2. Allen, H. G., *Analysis and Design of Structural Sandwich Panels*, Pergamon, 1969.
3. Zenkert, D., *An Introduction to Sandwich Construction*, EMAS, 1997.
