[Home](../README.md) > Spin Casting Overview

# Centrifugal Casting Overview

## Contents

- [Overview](#overview)
- [The three variants](#the-three-variants)
- [Why it is clean](#why-it-is-clean)
- [What it makes](#what-it-makes)
- [What it cannot make](#what-it-cannot-make)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [Document index](#document-index)
- [References](#references)

---

## Overview

Molten metal is poured into a spinning mould. The centrifugal field throws the dense metal outward and everything less dense than it inward, so the outer wall comes out exceptionally sound and the bore carries essentially all the contamination.

Machine the bore away and what is left is cleaner than a static casting of the same alloy could be.

---

## The three variants

| Variant | Axis | Bore formed by | Makes |
|---|---|---|---|
| **True centrifugal** | Horizontal or vertical | **The field itself.** No core | Pipe, tube, liners, rings |
| **Semi-centrifugal** | Vertical | A core | Wheels, discs, pulleys |
| **Centrifuge** | Vertical, parts off-axis | Moulds on a rotating arm | Small complex parts, fed by the field |

**True centrifugal is the one this sub-domain covers.** It is the variant where the field does the work of forming the bore, and where the segregation benefit is strongest.

**Horizontal against vertical axis** matters for the shape: a horizontal axis gives a parallel bore, a vertical axis gives a parabolic one because gravity competes with the field along the length. Vertical machines are used for short parts where the parabola is machined away.

---

## Why it is clean

**The centrifugal field is a density separator.**

Everything in the melt that is less dense than the metal migrates inward: oxide inclusions, slag, refractory erosion, dissolved gas. Everything denser stays where it is, and there is usually nothing denser.

**The separation is fast.** Stokes velocity in a centrifugal field scales with the G-factor, so at 80 g a 50 um alumina particle moves at tens of millimetres per second. The solidification front advances at hundredths of a millimetre per second.

**The ratio of those two velocities is the figure of merit**, and it is worth naming: the capture number.

```
captureNumber = v_stokes / v_front
```

Well above one and essentially every inclusion reaches the bore before it is engulfed. Near or below one and the front outruns them and they are frozen in place. See [SolidificationAndSegregation.md](SolidificationAndSegregation.md).

---

## What it makes

| Part | Why centrifugal |
|---|---|
| **Pipe and tube** | The classic application. Long, hollow, sound |
| **Bushings and bearings** | Bronze, and the bore is machined anyway |
| **Cylinder liners** | Sound outer wall, machined bore |
| **Rings and flanges** | Better buy-to-fly than machining from plate |
| Rocket nozzle liners | Where a hollow refractory-lined section is wanted |
| Rolls | Bimetallic, with a hard shell cast onto a tough core |

**The economic case is buy-to-fly.** A ring machined from plate is 8:1; centrifugally cast it is around 2:1, and on an expensive alloy that is the whole cost.

**Bimetallic parts are a genuine speciality.** Pour one alloy, let it partly solidify, pour a second. The field holds them in layers and the result is a hard shell metallurgically bonded to a tough core, which nothing else produces as simply.

---

## What it cannot make

| Limit | Reason |
|---|---|
| **Anything not axisymmetric** | The field is radial |
| **Solid sections** | It produces a hollow by definition |
| **Thin walls below 4 mm** | Freezes before the melt distributes |
| **Length to diameter above 8** | The pour cannot be distributed evenly |
| Titanium | Reactive, and the mould coating cannot hold it |
| Tight tolerances | It is a casting, at IT12 or worse |

**The axisymmetric limit is absolute.** A feature that is not a body of revolution cannot be formed by a radial field, so flanges, bosses and ports are machined afterwards or the part is not a candidate.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| G-factor | 60 to 100 preferred, 40 to 150 usable |
| Minimum wall | 4 mm |
| Length to diameter | Up to 8 |
| Minimum bore | 25 mm |
| Bore machining allowance | 1.5 to 3 mm |
| Buy-to-fly | ~2 : 1 |
| Tolerance grade | IT12 |
| Axisymmetric only | The field is radial |

---

## Failure modes

**G-factor too low.** The melt rains at top of arc; a thick bottom and a thin top.

**G-factor too high.** Banding and longitudinal tearing.

**Insufficient bore allowance.** The segregated layer stays in the part.

**Wall too thin.** It freezes before the melt distributes.

**Length to diameter too high.** The wall tapers along the length.

**Vertical axis on a long part.** A parabolic bore.

---

## Worked numbers

From [`CentrifugalCasting`](../spinCastingLibrary/CentrifugalCasting.py), a 200 mm OD, 20 mm wall, 400 mm long 316L cylinder:

| Quantity | Value |
|---|---|
| Rotational speed for G = 80 | **846 rev/min** |
| G-factor at the bore | 64 |
| Casting modulus | 16.07 mm |
| Solidification time | 542 s |
| Stokes velocity, 50 um alumina | 46.0 mm/s inward |
| Front velocity | 0.037 mm/s |
| **Capture number** | **1248** |
| Escape fraction | 100 % |
| Bore machining allowance | 1.90 mm |
| Buy-to-fly | 1.95 : 1 |

**A capture number of 1248 is the whole argument for the process.** The field outruns the solidification front by three orders of magnitude, so essentially nothing is trapped.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM A geometry-specific centrifugal casting specifications** | By alloy family |
| ASTM A426 | Centrifugally cast ferritic alloy pipe for high temperature service |
| ASTM A451 | Centrifugally cast austenitic steel pipe |
| ASTM B505 | Copper alloy continuous castings |
| ISO 8062 | Casting dimensional tolerances and machining allowances |
| NASA-STD-5001 | Casting factors |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'spinCastingLibrary')

from CentrifugalCasting import CentrifugalCasting

casting = CentrifugalCasting()
casting.setInputs({'alloy': '316L', 'outerDiameter': 0.200,
                   'wallThickness': 0.020, 'length': 0.400})

casting.selectRotationalSpeed(targetGFactor = 80.0)
casting.calculateGFactor()
casting.calculateSolidification()
casting.calculateInclusionMigration()
casting.calculateMachiningAllowance()
print(casting.generateReport())
```

---

## Document index

| Document | Covers |
|---|---|
| [ProcessFundamentals.md](ProcessFundamentals.md) | The three variants, and horizontal against vertical |
| [RotationalSpeed.md](RotationalSpeed.md) | G-factor, the window, and speed selection |
| [MouldDesign.md](MouldDesign.md) | Permanent and expendable, coatings, thermal management |
| [Solidification.md](Solidification.md) | Chvorinov, directional structure, grain refinement |
| [SolidificationAndSegregation.md](SolidificationAndSegregation.md) | Stokes migration against the front |
| [Alloys.md](Alloys.md) | What is cast centrifugally and what is not |
| [AchievableGeometry.md](AchievableGeometry.md) | Wall, length, bore, and the axisymmetric limit |
| [MachiningAllowance.md](MachiningAllowance.md) | Segregation against tolerance, and which binds |
| [Defects.md](Defects.md) | Banding, cold shut, hot tearing, segregation |
| [PostProcessing.md](PostProcessing.md) | Heat treatment, HIP, machining |
| [Inspection.md](Inspection.md) | RT, UT, penetrant, dimensional |
| [ProcessComparison.md](ProcessComparison.md) | Against forging, wrought and additive |
| [Qualification.md](Qualification.md) | Lot acceptance and the casting factor |

---

## References

1. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
2. ASM Handbook Volume 15, *Casting*.
3. Chirita, G. et al., "Sensitivity of Different Al-Si Alloys to Centrifugal Casting Effect", *Materials and Design*, Vol. 31, 2010.
