[Home](../README.md) > Stability and Collapse

# Stability and Collapse

## Contents

- [Overview](#overview)
- [Columns, where theory works](#columns-where-theory-works)
- [Euler and Johnson](#euler-and-johnson)
- [The transition slenderness](#the-transition-slenderness)
- [Effective length](#effective-length)
- [P-delta amplification](#p-delta-amplification)
- [External pressure collapse](#external-pressure-collapse)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

This document is the deliberate counterweight to [ShellBuckling.md](ShellBuckling.md). A column is the one structural element where the classical solution is trustworthy, and understanding why is the fastest route to understanding why a shell's is not.

---

## Columns, where theory works

**Euler is accurate to within a few percent for a slender pinned column.** No empirical knockdown, no lower-bound curve fitted to sixty years of scatter.

**The reason is mode spacing.** A column has one buckling mode at its critical load. The next mode is at four times the load, so there is nothing nearby for an imperfection to couple it to. A cylinder has dozens of modes within a few percent of each other, and that near-degeneracy is what makes it imperfection sensitive.

| Element | Modes near critical | Knockdown |
|---|---|---|
| **Column** | **One** | **None** |
| Flat plate | Few | Mild |
| **Cylinder, axial** | **Dozens** | **0.29 to 0.65** |

**This is the single most useful comparison in the domain.** Imperfection sensitivity is not about how carefully something is built; it is about how many ways it can fail at the same load.

---

## Euler and Johnson

```
Euler      sigma = pi^2 E / lambda^2
Johnson    sigma = sigma_y - (sigma_y / (2 pi))^2 lambda^2 / E
```

with `lambda = L_effective / rho` the slenderness ratio and `rho = sqrt(I/A)` the radius of gyration.

**Euler is only valid above the transition slenderness.** Below it, Euler predicts a buckling stress above the material yield strength, which is physically impossible: the column crushes before it buckles.

**The Johnson parabola covers the short range.** It is constructed tangent to the Euler curve at the transition and runs to the yield strength at zero slenderness.

**Applying Euler below the transition is the classic column error and it is always unconservative.** For the reference short column the class reports Euler at 3139 MPa against Johnson at 269.9 MPa, which is **11.6x optimistic**.

---

## The transition slenderness

```
lambda_c = sqrt(2 pi^2 E / sigma_y)
```

**It is a material property, not a geometry one**, and it is worth recognising on sight:

| Material | E [GPa] | Fty [MPa] | lambda_c |
|---|---|---|---|
| **6061-T6** | 68.9 | 276 | **70** |
| 2219-T87 | 73.1 | 393 | 61 |
| 7075-T73 | 71.7 | 400 | 59 |
| **316L annealed** | 193 | 205 | **136** |
| Ti-6Al-4V | 113.8 | 880 | 50 |

**At the transition the critical stress is exactly half the yield strength**, for every material. That falls out of the algebra and it is a useful check: if a Johnson-Euler implementation does not give `sigma_y / 2` at `lambda_c`, it is wrong.

**A strong material has a low transition slenderness**, which means more of its geometry range is elastic buckling rather than crushing. Titanium at 50 spends most of its useful range in the Euler regime.

---

## Effective length

**Where real columns are lost.** The end restraint assumption moves the buckling load by a factor of sixteen across the range.

| End condition | Theoretical K | **Design K** | Load relative to pinned |
|---|---|---|---|
| **Fixed-fixed** | 0.5 | **0.65** | 2.4x |
| Fixed-pinned | 0.7 | **0.80** | 1.6x |
| **Pinned-pinned** | 1.0 | **1.0** | 1.0x |
| Fixed, free to sway | 1.0 | **1.20** | 0.7x |
| **Fixed-free** | 2.0 | **2.10** | **0.23x** |

**The design values are deliberately more conservative than the theoretical ones**, because a real joint is never perfectly fixed. Assuming a fixed end that behaves as pinned costs half the capability that was credited.

**A cantilever is sixteen times weaker than a fixed-fixed column of the same length**, on theoretical factors. That is the largest single lever in column design and it is a joint design decision, not a member one.

**Sway matters.** A frame whose ends are rotationally fixed but free to translate is weaker than a pinned-pinned column, which surprises people. The design value of 1.20 reflects it.

---

## P-delta amplification

**An axial load acting through the lateral deflection that bending produces adds moment, so the two do not superpose.**

```
AF = 1 / (1 - P / P_critical)
```

| P / P_critical | Amplification |
|---|---|
| 0.25 | 1.33 |
| **0.50** | **2.00** |
| 0.75 | 4.00 |
| **0.90** | **10.00** |

**A column at half its buckling load doubles its applied moment.** An interaction check that ignores this is optimistic exactly where it matters, and the error grows without bound as the load approaches critical.

**Eccentricity produces moment without any applied bending.** A load offset from the centroid by `e` produces `P e`, amplified by the same factor, which is why column end fittings are designed to load through the centroid.

---

## External pressure collapse

**A different problem from axial buckling, and far less imperfection sensitive.**

| Regime | Relation |
|---|---|
| **Long shell** | `p = E/(4(1-nu^2)) (t/R)^3`, independent of length |
| **Short shell** | Held up by the end rings, far stronger |
| Transition | At `L = 1.14 R sqrt(R/t)` |

**The long-shell result is independent of length**, which is why adding a ring frame is so effective: it converts a long shell into two short ones.

**Collapse goes as the cube of `t/R`**, so it is very sensitive to thickness. Halving the wall drops the collapse pressure by a factor of eight.

**The knockdown is only 0.90**, because the modes are well separated. Theory is close to test here in a way it never is for axial compression.

**The applications are vacuum jackets, drained tanks and submerged structure.** A cryogenic vacuum jacket is the common case, and a tank that is drained while still sealed can collapse under one atmosphere.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Euler needs no knockdown | One buckling mode |
| Johnson below the transition | Euler is unconservative there |
| `lambda_c = sqrt(2 pi^2 E / sigma_y)` | ~70 for 6061-T6 |
| At the transition, `sigma = sigma_y / 2` | Always. Use it as a check |
| Design K, not theoretical K | Real joints are not perfectly fixed |
| Cantilever is 16x weaker than fixed-fixed | The largest lever available |
| P-delta doubles the moment at half critical | |
| External pressure goes as `(t/R)^3` | And its knockdown is only 0.90 |

---

## Failure modes

**Euler applied to a short column.** 11.6x optimistic for the reference case.

**Theoretical K used for a bolted end.** Half the credited capability.

**Sway ignored in a frame.** Weaker than pinned-pinned.

**P-delta omitted from a combined check.** Optimistic where it matters most.

**Load introduced off the centroid.** Moment with no applied bending.

**A sealed tank drained.** One atmosphere external collapses a thin shell.

---

## Worked numbers

From [`BeamColumn`](../aerospaceStructuresLibrary/BeamColumn.py), 6061-T6 50 mm x 2 mm tube:

| Length | Slenderness | Regime | Euler | Johnson | Critical |
|---|---|---|---|---|---|
| **0.25 m** | 14.7 | **Johnson** | 3139 MPa | **269.9 MPa** | 269.9 MPa |
| 1.2 m | 70.6 | Euler | 136.2 MPa | 136.2 MPa | 136.2 MPa |

**At slenderness 70.6, just above the transition of 70.2, Euler and Johnson agree to within rounding.** That tangency is the strongest available check on both formulas.

| End condition | Critical load |
|---|---|
| Fixed-fixed | 65.4 kN |
| Fixed-pinned | 56.3 kN |
| Pinned-pinned | 41.1 kN |
| Fixed-sway | 28.5 kN |
| **Fixed-free** | **9.3 kN** |

**A 7.0x spread on design factors**, and 16x on theoretical ones.

---

## Standards

| Standard | Scope |
|---|---|
| NASA SP-8007 | Buckling of thin-walled circular cylinders |
| **AISC 360** | Steel construction, column curves and effective length |
| MMPDS Chapter 8 | Column and beam-column analysis |
| ASME BPVC Section VIII Division 1 UG-28 | External pressure |
| ECSS-E-HB-32-24 | Buckling of structures |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'aerospaceStructuresLibrary')

from BeamColumn import BeamColumn
from structuresUtils import transitionSlenderness

print(f'6061-T6 transition slenderness: {transitionSlenderness(68.9e9, 276.0e6):.1f}')

for length in (0.25, 1.2, 2.0):
    column = BeamColumn()
    column.setInputs({'material': '6061-T6', 'length': length, 'shape': 'thin tube',
                      'outerDiameter': 0.050, 'wallThickness': 0.002,
                      'axialLoad': 30.0e3})
    result = column.calculateBuckling()
    print(f'L={length:.2f} m  lambda {result["slenderness"]:5.1f}  {result["regime"]:8s}  '
          f'{result["criticalStress"] / 1e6:7.1f} MPa')

print(column.compareEndConditions()['note'])
```

---

## References

1. Timoshenko, S. P. and Gere, J. M., *Theory of Elastic Stability*, 2nd ed., McGraw-Hill, 1961.
2. Bruhn, E. F., *Analysis and Design of Flight Vehicle Structures*, Jacobs, 1973.
3. MMPDS-2023, *Metallic Materials Properties Development and Standardization*, Chapter 8.
