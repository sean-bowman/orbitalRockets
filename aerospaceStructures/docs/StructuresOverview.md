[Home](../README.md) > Structures Overview

# Structures Overview

## Contents

- [Overview](#overview)
- [Why buckling governs](#why-buckling-governs)
- [The analysis sequence](#the-analysis-sequence)
- [The knockdown ladder](#the-knockdown-ladder)
- [Conventions](#conventions)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [Document index](#document-index)
- [References](#references)

---

## Overview

Launch vehicle structure is a buckling problem wearing a stress problem's clothes. Almost nothing on a vehicle fails by exceeding its material strength. It fails by buckling, by fatigue at a joint, or through a load path nobody drew.

That single fact reorganises the whole discipline. A stress check is the thing you do last to confirm nothing silly has happened, not the thing you do first to size the structure.

---

## Why buckling governs

**A representative barrel section makes the case numerically.** A 1 m radius, 2.5 mm 6061-T6 shell:

| Quantity | Value |
|---|---|
| Material yield | 276 MPa |
| Classical buckling stress | 105.4 MPa |
| **Empirical knockdown** | **0.357** |
| **Allowable buckling stress** | **37.6 MPa** |
| **Buckling governs by** | **7.3x** |

**A stress check against the material allowable passes by a factor of seven at the load that destroys the shell.** That is not a conservative analysis, it is an analysis of the wrong failure mode.

**The reason is imperfection sensitivity.** A cylinder in axial compression has many buckling modes at nearly the same load, so the smallest geometric deviation lets the shell find a lower-energy path down. Test scatter from the 1930s onward never approached theory and never converged, which is why the design factors are empirical lower bounds rather than corrections to a model.

**Not everything is imperfection sensitive**, and knowing what is not is as useful:

| Element | Sensitivity | Knockdown |
|---|---|---|
| **Cylinder, axial compression** | **Severe** | **0.29 to 0.65** |
| Cylinder, bending | Moderate | 1.3x the axial value |
| Cylinder, torsion | Mild | 0.80 |
| Cylinder, external pressure | Mild | 0.90 |
| **Flat plate** | **Mild** | Well separated modes |
| **Column** | **None** | **Euler is accurate** |

**A column needs no knockdown at all**, because it has one buckling mode rather than a dense cluster. The contrast between [ShellBuckling.md](ShellBuckling.md) and [StabilityAndCollapse.md](StabilityAndCollapse.md) is the most useful comparison in this domain.

---

## The analysis sequence

| Order | Step | Why here |
|---|---|---|
| **1** | **Load cases and combination** | The governing case is rarely the largest single load |
| **2** | **Stiffness requirement** | Frequency sizes structure and it is expensive to fix late |
| **3** | **Stability** | Buckling governs, so size against it |
| **4** | **Strength** | Confirms nothing silly happened |
| **5** | **Joints** | Where structures actually fail |
| **6** | **Fatigue and fracture** | For anything with a life requirement |
| 7 | Mass properties | The objective function |

**Stiffness comes before strength** and it is routinely done in the other order. A structure sized by strength and then found to be too soft usually has to grow substantially, because frequency goes as the square root of stiffness over mass and doubling it needs four times the stiffness.

**Joints get the same analysis effort as the members they connect**, which is the step most often shortchanged.

---

## The knockdown ladder

Everything in this domain is a fraction of the material allowable, and it is worth seeing the fractions in one place.

| Source | Typical factor |
|---|---|
| **Shell buckling imperfection** | **0.29 to 0.65** |
| Casting factor, unqualified | 0.50 |
| As-welded aluminium HAZ | 0.50 |
| Short transverse orientation, SCC | 0.10 to 0.30 |
| Bolted joint efficiency | 0.60 to 0.80 |
| A-basis against typical | 0.85 to 0.90 |
| Ultimate factor of safety | 1 / 1.40 |

**These multiply.** A welded, cast, unqualified, short-transverse-loaded shell has very little of its handbook strength left, and the arithmetic is worth doing explicitly rather than assuming the factors overlap.

---

## Conventions

| Convention | Detail |
|---|---|
| **Units** | Mass-base SI throughout. Imperial only at boundaries, via named constants |
| **Compression positive** | For axial load on a shell or column |
| **Margin of safety** | `MS = allowable / (applied x FS) - 1` |
| **Factors multiply the load** | Not the allowable. They are different for a nonlinear response |
| **Allowables** | From [aerospaceMaterials](../../aerospaceMaterials/), through `structuralAllowables()` |
| Knockdowns | Applied explicitly and reported, never folded silently into an allowable |

**The factor multiplies the load, not the allowable**, and for a nonlinear response such as buckling under combined load those are not the same operation. See [LoadsAndLoadCases.md](LoadsAndLoadCases.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Buckling governs, not strength | 7.3x for a representative shell |
| The classical shell solution is 2 to 4x optimistic | Always apply a knockdown |
| A column needs no knockdown | Euler is accurate |
| Stiffness before strength | Frequency is expensive to fix late |
| Combine load cases, do not envelope them | |
| Joints get equal analysis effort | They are where structures fail |
| Knockdowns multiply | Do the arithmetic explicitly |

---

## Failure modes

**A stress check used to size a thin shell.** It passes by a factor of seven at the failure load.

**Classical buckling used without a knockdown.** Two to four times optimistic.

**Load cases enveloped component by component.** Sizes against a condition that never occurs and hides which phase drives the structure.

**Frequency checked after the structure is sized.** A late and expensive growth.

**A beam idealisation used on a thin shell.** Misses the shell modes entirely.

**Knockdowns assumed to overlap.** They multiply.

---

## Worked numbers

From [`codeInterface.py`](../codeInterface.py), which inherits its pressure from [fluidSystems](../../fluidSystems/) and its allowables from [aerospaceMaterials](../../aerospaceMaterials/):

| Article | Radius | Wall | R/t | Governed by |
|---|---|---|---|---|
| Small tank | 0.18 m | 2.26 mm | **79.7** | pressure, proof test |
| Stage tank | 1.80 m | 22.59 mm | **79.7** | pressure, proof test |
| **Dry skirt** | 1.80 m | 3.00 mm | **600** | **buckling, by 15.8x** |

**The two tanks differ by a factor of ten in radius and have identical R/t**, because a pressure-sized wall obeys `t = pR/sigma` and the radius cancels. **Scale is not what makes a shell a stability problem.** Having no pressure to size the wall is.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-5001** | Structural design and test factors of safety |
| **NASA SP-8007** | Buckling of thin-walled circular cylinders |
| NASA-STD-5019 | Fracture control requirements |
| **NASA-STD-5020** | Threaded fastening systems |
| NASA-STD-6016 | Materials and processes requirements |
| MMPDS | Metallic material allowables |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'aerospaceStructuresLibrary')

from CylindricalShell import CylindricalShell

shell = CylindricalShell()
shell.setInputs({'material': '6061-T6', 'radius': 1.0, 'thickness': 0.0025,
                 'length': 3.0, 'axialLoad': 200.0e3})
result = shell.calculateAxialBuckling()

print(f'yield      {result["yieldStrength"] / 1e6:7.1f} MPa')
print(f'buckling   {result["allowableStress"] / 1e6:7.1f} MPa')
print(f'governs by {result["governingRatio"]:7.1f}x')
```

---

## Document index

| Document | Covers |
|---|---|
| [LoadsAndLoadCases.md](LoadsAndLoadCases.md) | Sources, combination, factors, the governing case |
| [ShellBuckling.md](ShellBuckling.md) | Cylinders, knockdowns, SP-8007, pressure stabilization |
| [PressureVesselsAndTanks.md](PressureVesselsAndTanks.md) | Membrane theory, domes, proof, tanks as structure |
| [StabilityAndCollapse.md](StabilityAndCollapse.md) | Columns, Euler and Johnson, external pressure |
| [SandwichPanels.md](SandwichPanels.md) | Cores, wrinkling, dimpling, crimping |
| [StiffenedStructures.md](StiffenedStructures.md) | Isogrid, orthogrid, skin-stringer, crippling |
| [BoltedJoints.md](BoltedJoints.md) | Preload, joint diagrams, separation, bearing |
| [WeldedStructures.md](WeldedStructures.md) | Joint efficiency, HAZ, friction stir, weld lands |
| [BondedAndCompositeJoints.md](BondedAndCompositeJoints.md) | Adhesive joints, laminates, damage tolerance |
| [ThrustStructures.md](ThrustStructures.md) | Thrust takeout, gimbal loads, skirts, interstages |
| [DynamicsAndModes.md](DynamicsAndModes.md) | Modal analysis, requirements, POGO, slosh |
| [FatigueAndFracture.md](FatigueAndFracture.md) | S-N, crack growth, fracture control |
| [MassPropertiesAndOptimization.md](MassPropertiesAndOptimization.md) | Mass estimating, sizing loops, efficiency |
| [StandardsIndex.md](StandardsIndex.md) | Annotated index of the governing standards |

---

## References

1. NASA SP-8007, *Buckling of Thin-Walled Circular Cylinders*, revised 1968.
2. Bruhn, E. F., *Analysis and Design of Flight Vehicle Structures*, Jacobs, 1973.
3. NASA-STD-5001B, *Structural Design and Test Factors of Safety for Spaceflight Hardware*.
