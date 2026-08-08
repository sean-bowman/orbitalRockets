[Home](../README.md) > Pressure Vessels and Tanks

# Pressure Vessels and Tanks

## Contents

- [Overview](#overview)
- [Membrane theory](#membrane-theory)
- [Three thicknesses, one wall](#three-thicknesses-one-wall)
- [Dome shape](#dome-shape)
- [The Y-ring](#the-y-ring)
- [Common bulkheads](#common-bulkheads)
- [A tank is three things at once](#a-tank-is-three-things-at-once)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A propellant tank is a pressure vessel, a primary structure and a fluid container simultaneously, and the three requirements do not agree. This document sizes the first and says where it fights the other two.

---

## Membrane theory

```
hoop           sigma_h = p R / t
longitudinal   sigma_l = p R / (2 t)
sphere         sigma   = p R / (2 t)
```

**Hoop is exactly twice longitudinal in a cylinder.** That is why cylindrical pressure vessels split along a line parallel to the axis, and it is worth knowing on sight.

**A sphere of the same radius and pressure needs half the wall**, because it carries the load in two directions everywhere. A sphere is the lightest pressure vessel there is.

**It also packs into a vehicle badly**, which is the entire reason launch vehicles use cylinders with domed ends rather than spheres. The tank is competing for length in a vehicle whose length is expensive.

**The von Mises equivalent stress is what the yield check should use**, since the state is biaxial:

```
sigma_vm = sqrt(sigma_h^2 - sigma_h sigma_l + sigma_l^2) = sigma_h sqrt(3)/2
```

which is about 0.866 of the hoop stress.

---

## Three thicknesses, one wall

**Three independent requirements produce three candidate walls and the largest wins.**

| Requirement | Pressure | Against | Typical factor |
|---|---|---|---|
| **Burst** | `FS x MEOP` | Ultimate | 1.50 |
| **Yield** | `FS x MEOP` | Yield | 1.10 |
| **Proof** | `FS x MEOP` | Yield, no permanent set | 1.25 |

**Which one governs is the useful output**, because it says what to change. A burst-governed wall responds to a stronger alloy; a proof-governed one responds to a lower proof factor or a higher yield strength specifically.

**The proof test governs more often than people expect**, and a wall sized on burst alone yields during its own acceptance test. That is a real and recurring failure, and it is the same binding-constraint result the [fluidSystems](../../fluidSystems/) helium bottle produces by a different route.

**Joint efficiency applies to the parent thickness.** A fusion welded 2219 tank at 0.70 efficiency needs its wall divided by 0.70, which is a 43 percent increase. See [WeldedStructures.md](WeldedStructures.md).

---

## Dome shape

**The other trade, and it is between length and buckling.**

| Dome | Aspect ratio | Height | Equatorial hoop |
|---|---|---|---|
| **Hemispherical** | 1.000 | R | **+0.500, tensile** |
| **sqrt(2) ellipsoidal** | 1.414 | 0.707 R | **0.000, exactly zero** |
| 2:1 ellipsoidal | 2.000 | 0.500 R | **-1.000, compressive** |

**The hemisphere is the best pressure shape and the longest.** It carries pure biaxial tension everywhere and needs the least wall, and it costs a full radius of vehicle length at each end.

**An ellipse is shorter and develops compressive hoop stress near its equator.** On a thin dome that compression buckles, which is a different failure mode entirely and is not caught by a membrane stress check.

**The threshold is exactly `sqrt(2)`**, where the equatorial hoop stress passes through zero. That is why `sqrt(2)` ellipsoidal domes are so common: they are the shortest dome with no compressive hoop stress anywhere.

**A 2:1 ellipsoidal dome has substantial equatorial compression** and it is used where the length saving is worth a buckling check.

---

## The Y-ring

**The joint between the dome and the barrel, and it is the hardest detail in a tank.**

The problem is a discontinuity in meridional curvature. The dome carries its load partly in the hoop direction; the barrel carries twice as much hoop as longitudinal. Where they meet, the radial displacements do not match, so a bending moment develops to enforce compatibility.

| Consequence | Detail |
|---|---|
| **Local bending** | Superimposed on the membrane stress |
| **A thickened ring** | The Y-ring, machined from a forging or a ring rolling |
| **Fatigue critical** | A stress concentration at a welded joint |
| Attachment | Frequently where the barrel joins the thrust structure too |

**Membrane theory does not describe it** and a discontinuity analysis or a finite element model is required. The classes here size the membrane regions and stop at the Y-ring deliberately.

---

## Common bulkheads

**One dome shared between two tanks, which removes an entire dome and the intertank between them.**

| Benefit | Cost |
|---|---|
| **Substantial length and mass saving** | **Differential pressure in both directions** |
| Fewer parts | Thermal problem if the propellants differ in temperature |
| | A leak connects the two propellants |

**The differential pressure reverses.** During flight the lower tank may be at higher pressure; during drain or on the pad the reverse. The bulkhead must be checked for buckling in the direction where it is in compression, which is the harder case.

**A LOX/LH2 common bulkhead is a thermal problem as much as a structural one**, with 90 K on one side and 20 K on the other, and it usually needs insulation within the bulkhead itself.

**A leak path between two propellants is a hazard**, which is why common bulkheads carry leak detection in the interstitial space.

---

## A tank is three things at once

| Role | Wants |
|---|---|
| **Pressure vessel** | A thick wall and a hemispherical dome |
| **Primary structure** | A thin wall it can stabilize with pressure |
| **Fluid container** | A shape that drains, and volume packed into a given length |

**They conflict directly.** The pressure vessel wants thickness; the structure wants thinness plus pressure. The resolution is pressure stabilization, and it makes the structure dependent on the pressurization system working. See [ShellBuckling.md](ShellBuckling.md).

**The worked example shows the tank is not the stability problem** at either scale, because a pressure-sized wall is comparatively thick. The stability problem is the dry structure beside it.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Hoop is twice longitudinal | Cylinders split axially |
| A sphere needs half the wall | And packs badly |
| Size against burst, yield and proof | The largest wins |
| Proof governs more often than expected | |
| sqrt(2) dome has zero equatorial hoop | The shortest with no compression |
| Above sqrt(2), check the dome for buckling | Not just burst |
| Joint efficiency divides the wall | 0.70 is a 43 % increase |
| The Y-ring needs a discontinuity analysis | Membrane theory stops there |

---

## Failure modes

**Wall sized on burst alone.** Yields during the proof test.

**2:1 dome checked only for burst.** Equatorial compression buckles it.

**Joint efficiency omitted.** The wall is 30 to 40 percent thin.

**Membrane theory applied at the Y-ring.** It does not describe the discontinuity bending.

**Common bulkhead checked in one pressure direction.** The reverse case governs.

**Hoop stress used for the yield check.** Von Mises is 0.866 of it, and using hoop is conservative but inconsistent.

---

## Worked numbers

From [`PressureVessel`](../aerospaceStructuresLibrary/PressureVessel.py), 2219-T87 at A-basis, 0.70 joint efficiency, 2.4249 MPa:

| Article | Burst | Yield | **Proof** | Governs | R/t |
|---|---|---|---|---|---|
| R = 0.18 m | 2.190 mm | 1.988 mm | **2.259 mm** | **proof** | 79.7 |
| R = 1.80 m | 21.904 mm | 19.881 mm | **22.592 mm** | **proof** | 79.7 |

**The proof test governs at both scales**, by 3.1 percent over burst. **R/t is identical**, because `t = pR/sigma` makes the radius cancel.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-5001** | Structural design and test factors |
| **AIAA S-080** | Metallic pressure vessels, pressurized structures |
| AIAA S-081 | Composite overwrapped pressure vessels |
| ASME BPVC Section VIII | Pressure vessel design, terrestrial |
| NASA-STD-5019 | Fracture control |
| MIL-STD-1522 | Pressurized systems, safety |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'aerospaceStructuresLibrary')

from PressureVessel import PressureVessel, DOME_TYPES

tank = PressureVessel()
tank.setInputs({'material': '2219-T87', 'condition': 't87', 'basis': 'A',
                'radius': 1.80, 'cylindricalLength': 6.0,
                'jointEfficiency': 0.70, 'operatingPressure': 2.4249e6})

sizing = tank.sizeWallThickness()
print(sizing['bindingConstraint'], sizing['requiredThickness'] * 1000.0)

for dome in DOME_TYPES:
    tank.domeType = dome
    result = tank.calculateDomeGeometry()
    print(f'{dome:20s} hoop factor {result["equatorialHoopFactor"]:+.3f}')
```

---

## References

1. AIAA S-080A, *Space Systems: Metallic Pressure Vessels, Pressurized Structures, and Pressure Components*.
2. Huzel, D. K. and Huang, D. H., *Modern Engineering for Design of Liquid-Propellant Rocket Engines*, AIAA, 1992.
3. Flugge, W., *Stresses in Shells*, 2nd ed., Springer, 1973.
