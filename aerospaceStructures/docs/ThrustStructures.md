[Home](../README.md) > Thrust Structures

# Thrust Structures

## Contents

- [Overview](#overview)
- [Getting thrust into the tank](#getting-thrust-into-the-tank)
- [Thrust structure forms](#thrust-structure-forms)
- [Gimbal loads](#gimbal-loads)
- [Skirts and interstages](#skirts-and-interstages)
- [Point loads into thin shells](#point-loads-into-thin-shells)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The thrust structure takes a small number of very large point loads from the engines and distributes them into a thin shell that cannot accept point loads at all. That is the whole problem.

---

## Getting thrust into the tank

**An engine applies its thrust at a gimbal bearing a few hundred millimetres across. The tank aft dome is a membrane that carries no bending.** Something has to reconcile those.

| Approach | Detail |
|---|---|
| **Thrust cone** | A conical shell from the engine mounts to the tank skirt joint |
| **Thrust beam or crossbeam** | A beam across the base, engines hung from it |
| **Truss** | Discrete members, common for a single engine or a cluster |
| **Direct to skirt** | Engines mounted to a ring at the skirt, the load never enters the dome |

**The conical shell is the classic large-vehicle answer** because a cone naturally converts a ring of load at one diameter into a ring at another, and it is a shell rather than a discrete structure so the load is distributed by the time it arrives.

**Direct-to-skirt is the modern preference where the layout allows it**, because it keeps the concentrated load out of the pressure vessel entirely. The thrust goes engine to ring to skirt to barrel, and the dome only ever sees pressure.

---

## Thrust structure forms

| Form | Best for | Weakness |
|---|---|---|
| **Cone** | Many engines, axisymmetric | Heavy, and its own buckling problem |
| **Truss** | Few engines, clear load paths | Point loads at every node |
| **Crossbeam** | Two or four engines | Bending dominated, heavy |
| Monocoque skirt with ring | Single engine | Ring is the whole design |

**A thrust cone is itself a buckling problem.** It is a thin conical shell in axial compression, and cones are as imperfection sensitive as cylinders. NASA SP-8019 covers them and the knockdown treatment is analogous.

**A truss puts point loads at every node**, which moves the problem rather than solving it. Each node needs a fitting, and fittings are heavy and fatigue critical.

---

## Gimbal loads

**A gimballed engine does not apply an axial force. It applies a force vector that rotates, plus the torque needed to rotate it.**

| Load | Source |
|---|---|
| **Axial thrust** | The nominal case |
| **Side force** | `T sin(theta)` at the gimbal angle |
| **Moment at the mount** | Side force times the offset to the mount plane |
| **Actuator reaction** | Into the structure, at the actuator attachment |
| **Torsion on the vehicle** | From differential gimbal in a cluster |

**The side force is the design case for the mount**, not the axial thrust. At 8 degrees of gimbal a 1 MN engine applies 139 kN laterally, and it applies it at a moment arm.

**Actuator loads are frequently missed.** The actuator pushes against the structure to move the engine, and that reaction is a real load path that needs a designed fitting.

**Engine-out is a load case.** A cluster with one engine out is asymmetric, and the remaining engines gimbal to compensate, which produces a load distribution nothing in nominal operation resembles.

---

## Skirts and interstages

**These are the structures where buckling genuinely governs**, because they are dry: no internal pressure to size their walls and none to stabilize them.

| Structure | Function |
|---|---|
| **Aft skirt** | Carries thrust from the engine mounts to the tank, ground support at the hold-downs |
| **Interstage** | Carries the upper stage through first stage flight, then separates |
| **Forward skirt** | Carries the payload and its adapter |

**They carry the full vehicle compression with no pressure stabilization**, so `R/t` is a free choice and it is chosen thin. The worked example's dry skirt at `R/t` of 600 buckles at 21.9 MPa against a 345 MPa yield, a factor of **15.8**.

**They are the natural home for stiffening**, because a monocoque wall thick enough to carry the compression unaided is heavier than a stiffened one. See [StiffenedStructures.md](StiffenedStructures.md).

**Hold-down loads are a ground case with flight consequences.** The vehicle sits on the aft skirt, and the hold-down posts introduce point loads into it at exactly the locations that are also carrying thrust in flight.

---

## Point loads into thin shells

**A thin shell has no capability at a point.** Every concentrated load needs a designed introduction, and this is where a large fraction of a vehicle's structural mass lives.

| Method | Detail |
|---|---|
| **Ring frame** | Distributes a radial or moment load around the circumference |
| **Longeron** | Distributes an axial load along the length |
| **Doubler** | Local thickening under a fitting |
| **Integral machined pad** | The same, machined from the parent rather than added |
| Fitting | A discrete part transferring load into a ring or longeron |

**The load has to be diffused over roughly `sqrt(R t)`** before the shell behaves as a membrane again. That length is the shell's characteristic decay length and it sets how big the introduction structure has to be.

**Kick loads at a change in cone angle** are the same problem in a different guise. Where a conical section meets a cylindrical one, the meridional load has a radial component that must be reacted by a ring, and the ring load can be very large.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Keep concentrated loads out of the pressure vessel | Direct to skirt where the layout allows |
| A thrust cone is its own buckling problem | SP-8019 |
| Size the mount for side force, not axial thrust | `T sin(theta)` |
| Include actuator reactions | A real load path, frequently missed |
| Engine-out is a load case | Nothing in nominal resembles it |
| Skirts and interstages are dry | Buckling governs, by 10 to 20x |
| Diffusion length is `sqrt(R t)` | How big the introduction must be |
| A cone-cylinder junction needs a ring | The kick load can be very large |

---

## Failure modes

**Point load into a membrane with no introduction structure.** Local collapse.

**Mount sized for axial thrust only.** Side force at gimbal governs.

**Actuator reaction omitted.** An unanalysed load path.

**Engine-out not run.** An asymmetric case nothing else bounds.

**Cone-cylinder junction with no ring.** The kick load has nowhere to go.

**Skirt sized like a tank wall.** It has no pressure to stabilize it.

**Hold-down loads treated as ground-only.** They share structure with flight loads.

---

## Worked numbers

From [`CylindricalShell`](../aerospaceStructuresLibrary/CylindricalShell.py) on the worked example's dry skirt, 2219-T87, 1.8 m radius, 3 mm wall:

| Quantity | Value |
|---|---|
| R/t | **600** |
| Classical buckling | 74.5 MPa |
| Knockdown | **0.294** |
| Allowable | **21.9 MPa** |
| Material yield | 345.0 MPa |
| **Buckling governs by** | **15.8x** |
| Applied | 7.3 MPa |
| Margin | +1.148 |
| Wall for zero margin | 2.22 mm |

**The classical solution is 3.4x optimistic here**, which is the largest knockdown anywhere in the worked example and it is on the structure that most needs to be light.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA SP-8007** | Buckling of thin-walled circular cylinders |
| **NASA SP-8019** | Buckling of thin-walled truncated cones |
| NASA SP-8032 | Buckling of thin-walled doubly curved shells |
| NASA-STD-5001 | Structural design and test factors |
| MIL-HDBK-1783 | Engine structural integrity program |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'aerospaceStructuresLibrary')

from CylindricalShell import CylindricalShell

skirt = CylindricalShell()
skirt.setInputs({'material': '2219-T87', 'condition': 't87', 'basis': 'A',
                 'radius': 1.80, 'thickness': 0.0030, 'length': 2.00,
                 'axialLoad': 247.0e3})

result = skirt.calculateAxialBuckling()
for finding in result['findings']:
    print(finding)

print(skirt.sizeThicknessForAxialLoad())
```

---

## References

1. NASA SP-8019, *Buckling of Thin-Walled Truncated Cones*, 1968.
2. Huzel, D. K. and Huang, D. H., *Modern Engineering for Design of Liquid-Propellant Rocket Engines*, AIAA, 1992.
3. Bruhn, E. F., *Analysis and Design of Flight Vehicle Structures*, Jacobs, 1973.
