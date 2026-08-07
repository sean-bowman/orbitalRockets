[Home](../README.md) > Achievable Geometry

# Achievable Geometry

## Contents

- [Overview](#overview)
- [The limits](#the-limits)
- [Wall thickness](#wall-thickness)
- [Length to diameter](#length-to-diameter)
- [The axisymmetric constraint](#the-axisymmetric-constraint)
- [Tolerances and surface](#tolerances-and-surface)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The process makes hollow bodies of revolution, and the envelope is set by how far the melt can be distributed before it freezes.

---

## The limits

| Limit | Value | What happens past it |
|---|---|---|
| **Minimum wall** | 4 mm | Freezes before the melt distributes |
| **Maximum wall** | ~150 mm | Long freezing time, coarse structure, and it is uneconomic |
| **Minimum bore** | 25 mm | The field cannot form a smaller free surface reliably |
| **Length to diameter** | 8 | The pour cannot be distributed evenly |
| Maximum diameter | ~2 m | Machine dependent |
| Maximum length | Several metres | Machine dependent |

---

## Wall thickness

**Thin walls are the hard case and there are two separate reasons.**

**Freezing before distribution.** A thin section has a small modulus and freezes fast. The melt has to reach the far end of the mould before the near end solidifies, and below about 4 mm it does not.

**A fast front.** Thin walls freeze fast, which raises the front velocity and lowers the capture number. The cleanliness benefit weakens exactly where the wall is thinnest. See [SolidificationAndSegregation.md](SolidificationAndSegregation.md).

**Thick walls are limited economically rather than technically.** A 150 mm wall freezes slowly, gives a coarse columnar structure, and the machining to get to a useful part is substantial.

**Wall thickness is set by the pour mass rather than by tooling**, which is the process's most flexible property:

```
m = rho * pi * D * t * L
```

One mould makes a range of walls simply by pouring more or less, and that is unusual in casting.

---

## Length to diameter

**Above about 8, the pour cannot be distributed evenly.**

The melt has to travel along the mould, and it is freezing as it goes. A traversing pour spout helps and it does not remove the limit.

**The symptom is a tapered wall**: thicker where the melt was poured first and thinner at the far end, or the reverse depending on the pour sequence.

**Long parts need a horizontal machine and a traversing spout**, and even then the taper has to be inside the machining allowance.

---

## The axisymmetric constraint

**Absolute.** The field is radial, so any feature that is not a body of revolution cannot be formed by it.

| Feature | How it is made |
|---|---|
| **Flanges** | Machined from a thicker as-cast section, or welded on |
| **Bosses and ports** | Machined, or welded |
| **Internal features** | Machined |
| Varying wall along the length | Possible with a stepped mould, and unusual |
| **Non-round bore** | Not possible. The free surface is a cylinder |

**The bore is always round** because it is a free surface under a radial field, and no mould feature changes that. A part needing a non-round bore is machined from a round casting.

**This constraint is what usually decides whether a part is a centrifugal casting candidate**, and it is decided at concept rather than at process selection.

---

## Tolerances and surface

| Property | As-cast |
|---|---|
| **Tolerance grade** | IT12, roughly |
| **Outer surface** | Takes the mould surface. Reasonable |
| **Bore surface** | A free surface. Rough, oxidised, and machined away |
| Concentricity | Good, since both surfaces are formed by the same rotation |
| Ovality | Low, for the same reason |

**Concentricity is a real strength.** Both the outer and inner surfaces are formed by the same rotation about the same axis, so they are concentric to a degree that a bored tube is not.

**The bore surface is poor and it does not matter**, because it is machined away along with the segregated layer. See [MachiningAllowance.md](MachiningAllowance.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Minimum wall | 4 mm |
| Minimum bore | 25 mm |
| Length to diameter | 8 |
| Wall set by pour mass | One mould, many walls |
| Axisymmetric only | Absolute |
| The bore is always round | It is a free surface |
| Tolerance | IT12 |
| Concentricity | A strength of the process |

---

## Failure modes

**Wall below 4 mm.** Freezes before it distributes.

**L/D above 8.** A tapered wall.

**A non-axisymmetric feature expected as cast.** It has to be machined or welded.

**A non-round bore expected.** Not possible.

**Tolerance expected better than IT12.** It is a casting.

---

## Standards

| Standard | Scope |
|---|---|
| **ISO 8062** | Casting dimensional tolerances and machining allowances |
| ASTM A451 / A426 / A660 | Centrifugally cast pipe, dimensional requirements |
| ISO 286 | Tolerance grades |

---

## Tool interface

```python
from CentrifugalCasting import CentrifugalCasting, GEOMETRY_LIMITS

casting = CentrifugalCasting()
casting.setInputs({'alloy': '316L', 'outerDiameter': 0.100,
                   'wallThickness': 0.002, 'length': 1.200})
result = casting.checkGeometry()
for issue in result['issues']:
    print(issue)
```

---

## References

1. ISO 8062-3, *Geometrical Product Specifications: Dimensional and Geometrical Tolerances for Moulded Parts*.
2. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
3. ASM Handbook Volume 15, *Casting*.
