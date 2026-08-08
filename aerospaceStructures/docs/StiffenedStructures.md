[Home](../README.md) > Stiffened Structures

# Stiffened Structures

## Contents

- [Overview](#overview)
- [Why stiffening works](#why-stiffening-works)
- [The three competing modes](#the-three-competing-modes)
- [Crippling](#crippling)
- [Isogrid, orthogrid and skin-stringer](#isogrid-orthogrid-and-skin-stringer)
- [The honest comparison](#the-honest-comparison)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Stiffening is the other answer to the shell buckling problem. Where a sandwich separates two facesheets with a core, a stiffened panel puts discrete ribs on one face and lets the skin span between them.

---

## Why stiffening works

**Not because it is stronger in the same mode. Because it changes which mode governs.**

An unstiffened cylinder buckles in the imperfection-sensitive mode that carries the 0.29 to 0.65 knockdown. A stiffened one buckles either:

| Mode | Character | Knockdown |
|---|---|---|
| **Locally, between stiffeners** | A **plate** problem | Mild, modes well separated |
| **Globally, as a stiffened shell** | Far less imperfection sensitive | Better, because `R/t_effective` is low |

**Converting a shell problem into a plate problem is the whole mechanism.** A flat plate's buckling modes are well separated, so theory is close to test.

**The effective bending thickness is what improves the global knockdown.** Putting material away from the neutral axis raises the second moment, so:

```
t_effective = (12 I / b)^(1/3)
```

For the reference orthogrid this is **13.97 mm against a smeared thickness of 2.90 mm**, a gain of 4.82x, and the knockdown rises from 0.357 to **0.630**.

**That cube root is worth stating explicitly** because a square root there is an easy slip and it silently inverts the result, producing the impossible conclusion that stiffening reduces capability.

---

## The three competing modes

| Mode | What buckles |
|---|---|
| **Local skin buckling** | The skin bay between stiffeners |
| **Crippling** | The stiffener's own flanges, locally |
| **General instability** | The whole stiffened shell between ring frames |

**A design is balanced when the three are close together.** Any mode occurring much later than the others is carrying mass that is not earning anything.

| Balance | Meaning |
|---|---|
| General instability governs by a wide margin | Stiffeners too small |
| Local buckling governs by a wide margin | Stiffeners too far apart |
| **Within ~20 %** | **Reasonably optimised** |

**Local skin buckling is not necessarily failure.** A skin that buckles between stiffeners can continue to carry load in a post-buckled diagonal-tension field, and airframes exploit this routinely. That is a design decision, not an accident, and it requires the stiffeners to be sized for the redistributed load.

---

## Crippling

**A stiffener does not fail by Euler buckling as a column. Its flanges buckle locally first, and after that it has lost the section it needed.**

The Gerard method correlates it against a non-dimensional geometry parameter:

```
sigma_cc / sigma_y = beta (g t^2 / A sqrt(E / sigma_y))^m
```

**`g` is the number of flanges and cuts in the section**, which is why a hat section cripples later than a blade of the same area: more edges means more restraint.

| Stiffener | Flanges | Crippling ratio | Stress |
|---|---|---|---|
| **Blade** | 1 | **0.729** | 286.5 MPa |
| Tee | 2 | 1.000 | 393.0 MPa |
| **Hat** | 4 | **1.000** | **393.0 MPa** |

**A blade is the simplest to machine and the first to cripple.** For the reference geometry it is only 73 percent effective, meaning the stiffener reaches its limit at 73 percent of the material yield.

**Crippling is capped at yield.** A section stocky enough not to cripple simply reaches yield, and the correlation must be cut off there rather than extrapolated.

---

## Isogrid, orthogrid and skin-stringer

| Form | Pattern | Character |
|---|---|---|
| **Isogrid** | Equilateral triangles | **Isotropic smeared properties.** Machined |
| **Orthogrid** | Orthogonal ribs | Different properties each direction. Machined |
| **Skin-stringer** | Discrete stringers on a skin | The classic airframe form. Built up or machined |

**Isogrid's isotropy is its distinguishing property.** The equilateral triangle pattern gives the same smeared stiffness in every in-plane direction, which makes the analysis far simpler and suits a shell loaded in combined compression, bending and shear.

**Orthogrid is more efficient where the loading is directional**, which a launch vehicle barrel usually is: axial compression dominates and hoop is handled by pressure.

**Machined grid structures are made from one piece**, so there is no bond line to qualify and no fastener count. The cost is buy-to-fly: a machined orthogrid barrel starts as a very thick plate or a forged cylinder and most of it becomes chips. See [aerospaceMaterials machiningProcesses](../../aerospaceMaterials/machiningProcesses/).

**Skin-stringer is built up and riveted**, which has a lower material cost and a much higher part and labour count.

---

## The honest comparison

**Against an unstiffened skin of identical areal mass**, which is the comparison most often skipped:

| Article | Allowable |
|---|---|
| Unstiffened skin, equal mass | 49.4 MPa |
| **Stiffened panel** | **108.0 MPa** |
| **Gain** | **2.18x** |

**A stiffened panel that carries less than an unstiffened skin of the same mass is a worse design that took more machining to produce**, and that outcome is entirely possible with badly proportioned stiffeners.

**Making that comparison is one line of code** and it is the check that keeps a stiffening scheme honest.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Stiffening changes the mode, not the strength | Shell problem becomes plate problem |
| `t_effective = (12 I / b)^(1/3)` | A cube root, not a square root |
| Balance the three modes within ~20 % | |
| Blade cripples first | Hat and tee are fully effective |
| Crippling is capped at yield | Never extrapolate past it |
| Isogrid for combined loading | Isotropic smeared properties |
| Orthogrid for directional loading | More efficient |
| Always compare against an equal-mass skin | |

---

## Failure modes

**Effective thickness from a square root.** Stiffening appears to reduce capability 4x.

**One mode checked.** The other two may govern.

**Unbalanced design accepted.** Mass carried that earns nothing.

**Blade stiffener assumed fully effective.** It cripples at 73 percent of yield.

**No comparison against an equal-mass skin.** The stiffening may be buying nothing.

**Post-buckled skin credited without sizing the stiffeners for redistribution.** They take the load the skin shed.

---

## Worked numbers

From [`StiffenedPanel`](../aerospaceStructuresLibrary/StiffenedPanel.py), 2219-T87 skin-stringer, 2 mm skin, 100 mm spacing, 30 x 3 mm blades:

| Quantity | Value |
|---|---|
| Smeared thickness | 2.900 mm |
| Effective bending thickness | **13.97 mm** |
| Thickness gain | **4.82x** |
| Knockdown | 0.630, against 0.357 smeared |
| Areal mass | 8.24 kg/m^2 |
| Bending efficiency | 111.7x an equal-mass skin |

| Mode | Stress |
|---|---|
| **Local skin buckling** | **108.0 MPa, GOVERNS** |
| Crippling | 286.5 MPa |
| General instability | 393.0 MPa |

**The modes are 3.64x apart, so this design is not balanced.** The stiffeners are heavier than they need to be relative to the skin spacing.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA CR-124075** | Isogrid design handbook |
| NASA SP-8007 | Buckling of thin-walled circular cylinders |
| MMPDS Chapter 8 | Crippling and column analysis |
| Bruhn C7 | Crippling of formed and extruded sections |
| ECSS-E-HB-32-24 | Buckling of structures |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'aerospaceStructuresLibrary')

from StiffenedPanel import StiffenedPanel, STIFFENER_TYPES

panel = StiffenedPanel()
panel.setInputs({'material': '2219-T87', 'condition': 't87', 'panelType': 'orthogrid',
                 'skinThickness': 0.002, 'stiffenerSpacing': 0.10,
                 'stiffenerHeight': 0.030, 'stiffenerThickness': 0.003,
                 'radius': 1.0, 'frameSpacing': 0.5, 'axialLoad': 400.0e3})

screen = panel.screenInstabilityModes()
print(screen['governingMode'], screen['modeSpread'], screen['balanced'])
print(panel.compareAgainstUnstiffened()['note'])

for stiffener in STIFFENER_TYPES:
    panel.stiffenerType = stiffener
    print(f'{stiffener:6s} crippling ratio '
          f'{panel.calculateCrippling()["cripplingRatio"]:.3f}')
```

---

## References

1. Meyer, R. R., *Isogrid Design Handbook*, NASA CR-124075, 1973.
2. Gerard, G., *Handbook of Structural Stability Part IV: Failure of Plates and Composite Elements*, NACA TN 3784, 1957.
3. Bruhn, E. F., *Analysis and Design of Flight Vehicle Structures*, Jacobs, 1973, Chapter C7.
