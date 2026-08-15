[Home](../README.md) > Shell Buckling

# Shell Buckling

## Contents

- [Overview](#overview)
- [The classical solution](#the-classical-solution)
- [Why it overpredicts](#why-it-overpredicts)
- [The SP-8007 knockdown](#the-sp-8007-knockdown)
- [Pressure stabilization](#pressure-stabilization)
- [The other load cases](#the-other-load-cases)
- [Combined loading](#combined-loading)
- [The Batdorf parameter](#the-batdorf-parameter)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

This is the central subject of the domain. A launch vehicle is mostly thin cylinders in compression, and the classical solution for how much compression they carry is wrong by a factor of two to four in the unconservative direction.

---

## The classical solution

For an axially loaded thin cylinder, small-deflection theory gives

```
sigma_classical = E t / (R sqrt(3 (1 - nu^2)))
```

**It depends only on the material and on `t/R`.** Not on length, not on the boundary conditions, not on how the load is introduced. For a long cylinder that is genuinely the answer the theory produces.

**It is also close to twice what tests give**, and that discrepancy is not experimental scatter. It is real.

---

## Why it overpredicts

**Imperfection sensitivity, and the mechanism is worth understanding rather than memorising.**

A cylinder in axial compression has **many distinct buckling modes at nearly the same critical load.** Axial half-waves and circumferential waves trade off against each other, and the classical eigenvalue is nearly degenerate: dozens of mode shapes share it.

**A structure with closely spaced modes is unstable in the mathematical sense as well as the physical one.** The smallest geometric deviation couples the modes, and the shell finds a lower-energy path down that the perfect-geometry analysis never sees.

| Structure | Mode spacing | Sensitivity |
|---|---|---|
| **Cylinder, axial** | **Nearly degenerate** | **Severe** |
| Flat plate | Well separated | Mild |
| **Column** | **One mode** | **None** |
| Sphere, external pressure | Nearly degenerate | Severe |

**That table is the whole explanation.** A column has a single mode, so there is nothing for an imperfection to couple it to, and Euler is accurate. A cylinder has dozens, and it is not.

**Test scatter never converged.** Data from the 1930s through the 1960s spread across a band from roughly 0.2 to 0.8 of theory, with no trend that additional care in manufacture removed. The design factors are therefore lower bounds fitted to the scatter, not corrections to a model.

---

## The SP-8007 knockdown

```
gamma = 1 - 0.901 (1 - exp(-phi))
phi   = (1/16) sqrt(R/t)
```

| R/t | gamma | Classical is optimistic by |
|---|---|---|
| 100 | 0.516 | 1.94x |
| 200 | 0.437 | 2.29x |
| **400** | **0.357** | **2.80x** |
| 800 | 0.283 | 3.53x |
| 1600 | 0.219 | 4.56x |

**It falls monotonically with R/t**, because a thinner shell is more imperfection sensitive: the same absolute manufacturing deviation is a larger fraction of the wall.

**It is a lower bound on old data, and it is conservative by design.** A modern shell built to a measured tolerance and analysed with its actual imperfection field supports a far less punitive factor, and that is current practice at the large end. It needs a measured shell, so it is out of scope for preliminary sizing.

**The curve is empirical and has no physical content**, and it comes with two stated bounds.

**It applies below R/t = 1500.** NASA/SP-8007 Rev 2 writes the parameter as `phi = (1/16) sqrt(r/t)` for `r/t < 1500`, which is a bound on the correlation rather than a convention. Above it the expression still returns a number and the number means nothing, so the library refuses.

**It is unverified by experiment above L/r = 5.** That one fails differently: the correlation is untested there rather than meaningless, so the library reports where the shell sits rather than refusing. **A long shell also needs a column check**, because the classical prediction the knockdown multiplies cannot see the interaction between shell buckling and column buckling and becomes unconservative in exactly that regime. [BeamColumn](../aerospaceStructuresLibrary/BeamColumn.py) is what does it.

---

## Pressure stabilization

**Internal pressure recovers a large part of the knockdown**, and it is why a pressurized tank skin is an efficient compression member.

The mechanism is direct: internal pressure pretensions the shell circumferentially and pushes it outward, which suppresses the inward buckling lobes that the imperfections would otherwise trigger.

| Internal pressure | Knockdown | Allowable |
|---|---|---|
| 0 | 0.6148 | 345.0 MPa |
| 0.500 MPa | 0.6315 | 354.4 MPa |
| 1.000 MPa | 0.6482 | 363.7 MPa |
| 2.236 MPa | **0.6896** | **386.9 MPa** |

**The recovery saturates.** Past a non-dimensional pressure of roughly `p (R/t)^2 / E` of 1, the shell has recovered essentially all of the loss and more pressure buys nothing.

**Crediting it carries an obligation.** An analysis that takes the stabilized allowable has to demonstrate that the pressure cannot be lost while the compressive load is applied. A tank that is empty and unpressurized on the pad is the ground handling case and it is checked at zero pressure.

**Pressure-stabilized stages take this to its conclusion** and have no structural capability at all without pressure. The Atlas of the 1950s could not stand up unpressurized. That is a design choice with an operational cost, not a free improvement.

---

## The other load cases

| Load | Knockdown | Why |
|---|---|---|
| **Axial compression** | **0.29 to 0.65** | Nearly degenerate modes |
| **Bending** | **1.3x the axial value** | Peak stress acts over a short arc |
| **Torsion** | **0.67** | Well separated modes. Carried as `gamma^(3/4)` in the stress expression |
| **External pressure, long** | **0.90** | Two-lobe oval mode, theory close to test |
| **External pressure, short** | **0.5625** | More circumferential waves, far wider scatter |

**Bending is less sensitive than uniform compression** because only part of the circumference is highly loaded, and the shell can shed load around a local imperfection into the less loaded region.

**Torsion and external pressure are barely sensitive at all.** Their buckling modes are well separated, so theory is close to test and the factors are mild. A shell that would need a 0.3 knockdown in compression needs 0.67 in torsion.

**External pressure carries two factors and they differ by 1.6.** A long cylinder collapses into a two-lobe oval where theory and test agree closely. A shorter one buckles into more circumferential waves, where the reported scatter is far wider: end restraint was often not accounted for in the test analysis, and some reported buckling loads were isolated buckles rather than a global pattern. **Applying the long cylinder factor to a short shell is unconservative by that 1.6**, and the branch that selects the classical pressure has to select the factor with it.

---

## Combined loading

```
R_axial + R_bending + R_shear^2 <= 1
```

**Axial and bending add linearly** because they produce the same membrane stress. **Shear enters quadratically.**

**A structure checked one load at a time can pass every check and fail the combination**, and the governing condition on a vehicle is never one load alone. The class reports this explicitly when it happens.

---

## The Batdorf parameter

```
Z = L^2 sqrt(1 - nu^2) / (R t)
```

**Separates short shells from long ones.** Below `Z` of about 10 the shell is short: the end restraint carries the load and buckling is plate-like. Above a few hundred it is long, and the classical cylinder solution applies.

**It matters for external pressure more than for axial compression**, because a short shell under external pressure is held up by its end rings and is far stronger than the long-shell result. See [StabilityAndCollapse.md](StabilityAndCollapse.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| `sigma_cl = E t / (R sqrt(3(1-nu^2)))` | The classical solution |
| Knockdown `1 - 0.901(1 - exp(-sqrt(R/t)/16))` | SP-8007 |
| Classical is 2 to 4x optimistic | Always knock it down |
| Bending relief | 1.3x the axial knockdown |
| Torsion 0.67 | Mild, well separated modes |
| External pressure 0.90 long, 0.5625 short | The branch decides the factor |
| Pressure stabilization is large | And it must be shown non-losable |
| Combine loads | Linear in axial and bending, quadratic in shear |
| Do not extrapolate beyond R/t 1500 | A bound the document states, not a convention |

---

## Failure modes

**Classical buckling used as the allowable.** Two to four times optimistic.

**Yield used to size a thin shell.** Passes by 7x at the failure load.

**Pressure stabilization credited without a pressure-retention argument.** The ground case is unpressurized.

**Loads checked individually.** The combination fails where each alone passes.

**The knockdown curve extrapolated past its range.** It has no physical content to extrapolate.

**The long cylinder external pressure factor used on a short shell.** Unconservative by 1.6, and the two cases look identical in a report that prints only one knockdown.

**A long shell checked for shell buckling alone.** The classical prediction becomes unconservative at large L/r because it cannot see column buckling, so the knockdown multiplies a number that is already too high.

**Bending checked at the axial knockdown.** Conservative, and it costs mass unnecessarily.

---

## Worked numbers

From [`CylindricalShell`](../aerospaceStructuresLibrary/CylindricalShell.py):

| Article | R/t | Classical | Knockdown | Allowable | Yield | Governs by |
|---|---|---|---|---|---|---|
| 1 m, 2.5 mm 6061-T6 | 400 | 105.4 MPa | 0.357 | **37.6 MPa** | 276 MPa | **7.3x** |
| Stage tank, 2219-T87 | 79.7 | 561.2 MPa | 0.615 | 345.0 MPa | 345.0 MPa | 1.0x |
| **Dry skirt, 2219-T87** | **600** | 74.5 MPa | **0.294** | **21.9 MPa** | 345 MPa | **15.8x** |

**The stage tank sits exactly on the boundary.** At R/t 79.7 the 2219-T87 buckling allowable and its yield strength agree to three figures, which is the transition between a strength-governed and a stability-governed wall.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA SP-8007** | Buckling of thin-walled circular cylinders |
| NASA SP-8019 | Buckling of thin-walled truncated cones |
| NASA SP-8032 | Buckling of thin-walled doubly curved shells |
| NASA-STD-5001 | Structural design and test factors |
| ECSS-E-HB-32-24 | Buckling of structures, European handbook |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'aerospaceStructuresLibrary')

from CylindricalShell import CylindricalShell
from structuresUtils import sp8007Knockdown

for ratio in (100.0, 400.0, 1600.0):
    print(f'R/t {ratio:6.0f}  knockdown {sp8007Knockdown(ratio):.4f}  '
          f'optimistic by {1.0 / sp8007Knockdown(ratio):.2f}x')

shell = CylindricalShell()
shell.setInputs({'material': '2219-T87', 'condition': 't87', 'radius': 1.8,
                 'thickness': 0.003, 'length': 2.0, 'axialLoad': 247.0e3})
result = shell.calculateAxialBuckling()
for finding in result['findings']:
    print(finding)
```

---

## References

1. NASA SP-8007, *Buckling of Thin-Walled Circular Cylinders*, revised 1968.
2. Koiter, W. T., *On the Stability of Elastic Equilibrium*, doctoral thesis, Delft, 1945.
3. Hilburger, M. W., *Developing the Next Generation Shell Buckling Design Factors and Technologies*, AIAA 2012-1686.
