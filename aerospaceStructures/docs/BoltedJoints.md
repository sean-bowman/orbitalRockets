[Home](../README.md) > Bolted Joints

# Bolted Joints

## Contents

- [Overview](#overview)
- [The joint stiffness diagram](#the-joint-stiffness-diagram)
- [Why preload works](#why-preload-works)
- [Separation](#separation)
- [Preload scatter](#preload-scatter)
- [Member failure modes](#member-failure-modes)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A preloaded joint is the one structural element where more applied load does not mean much more bolt load, right up until it does. Understanding both halves of that sentence is the whole subject.

---

## The joint stiffness diagram

**The bolt and the clamped members are two springs in parallel.** Applied tension splits between them by their relative stiffness:

```
load factor    Phi = k_bolt / (k_bolt + k_member)
bolt tension   F_bolt = F_preload + Phi P
```

**Member stiffness comes from the Rotscher pressure cone**, integrated along its length:

```
k = pi E d tan(a) / ln( ((2 l tan(a) + D - d)(D + d)) / ((2 l tan(a) + D + d)(D - d)) )
```

with a 30 degree half angle, `D` the head or washer bearing diameter and `d` the bolt diameter. A symmetric joint is two such frusta in series.

**Two details in that formula are easy to get wrong and both matter:**

**The cone starts at the head bearing face, not the shank.** The clamp load is introduced over the head footprint, roughly 1.5 diameters. Starting it at the bolt diameter understates member stiffness by about 1.7x.

**It must be integrated, not evaluated at mid-grip.** The cone area grows as the square of the grip while stiffness divides by the grip, so a mid-grip area approximation makes member stiffness *rise* with grip length. A longer spring must be softer.

---

## Why preload works

**Because the members are stiffer than the bolt, most applied tension unloads the members rather than stretching the bolt.**

For the reference joint, of 4.00 kN applied, only **1.09 kN reaches the bolt**. The other 2.91 kN goes into relieving the clamp force.

| Configuration | Phi |
|---|---|
| **Steel bolt in steel, long grip** | **0.10 to 0.30** |
| Steel bolt in aluminium, short grip | 0.25 to 0.50 |
| Very short grip, soft members | Higher still |

**The 0.1 to 0.3 rule of thumb assumes steel members at a grip of several diameters**, and it is quoted without those qualifiers constantly. A steel bolt in aluminium at `l/d` of 1.9 legitimately gives 0.27, and the same joint at `l/d` of 6 gives less.

**Two things lower Phi and both are design levers**: stiffer members and a longer grip. A longer grip lowers the bolt stiffness faster than the member stiffness, which is why washers and spacers can improve a fatigue-critical joint.

---

## Separation

**Past separation the load factor jumps to 1.0 and the bolt takes everything.**

```
P_separation = F_preload_minimum / (1 - Phi)
```

**The joint's behaviour changes discontinuously**, which is why separation is checked as its own requirement with its own factor, typically 1.20, rather than being folded into a stress margin.

**Separation is evaluated at minimum preload** because that is the bound that makes it worst. Bolt yield is evaluated at maximum preload. The two requirements pull in opposite directions and both must be satisfied, which is why NASA-STD-5020 requires the analysis at both bounds.

**A joint that separates in service is not necessarily failed** and it is certainly not behaving as analysed. Fatigue life collapses once the bolt sees the full load range, and fretting begins at the faying surface.

---

## Preload scatter

**Preload is the least controlled quantity in the joint.**

| Method | Scatter |
|---|---|
| **Torque** | **+/- 30 %** |
| Torque plus angle | +/- 15 % |
| Load indicating washer | +/- 10 % |
| **Bolt stretch** | **+/- 5 %** |
| **Ultrasonic** | **+/- 5 %** |

**Torque control is imprecise because the nut factor is.** `T = K F d` looks deterministic and `K` depends on thread friction, bearing friction, plating, lubrication and reuse history. Values from 0.12 to 0.20 are all defensible for nominally similar hardware.

**Embedment loses about 5 percent in the first hours** as surface asperities bed in. Longer-term relaxation continues through thermal cycling and creep, and it is worse in aluminium joints than steel ones.

**Critical joints use stretch or ultrasonic measurement** and the reason is the scatter, not the accuracy of the torque wrench.

---

## Member failure modes

**Three, and none of them involve the bolt's strength.**

| Mode | Character | Allowable |
|---|---|---|
| **Bearing** | Hole elongates. Progressive and visible | ~1.5 Ftu, the hole is confined |
| **Shear-out** | Material to the free edge tears out. **Sudden** | 0.577 Ftu |
| **Net section** | Reduced section through the hole fails | Ftu |

**Edge distance decides which one you get.** Below about 2 diameters the joint fails by shear-out, which is sudden and gives no warning. Above it, bearing governs and the hole elongates visibly first.

**That is why 2D edge distance is a hard minimum** rather than a guideline, and why 4D pitch protects the net section.

**Hole quality dominates joint fatigue life**, more than the fastener choice does. See [aerospaceMaterials HoleMaking](../../aerospaceMaterials/machiningProcesses/docs/HoleMaking.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| `Phi = k_bolt / (k_bolt + k_member)` | Typically 0.1 to 0.3 for steel on steel |
| The cone starts at the head bearing face | ~1.5 d |
| Integrate the cone, do not use mid-grip area | Or stiffness rises with grip |
| Separation at minimum preload | Bolt yield at maximum |
| Separation carries its own factor | 1.20 |
| Torque scatter | +/- 30 % |
| Embedment | ~5 % in the first hours |
| Edge distance 2D, pitch 4D | Minimums, not guidelines |

---

## Failure modes

**Preload assumed accurate from torque.** +/- 30 percent.

**Analysis at nominal preload only.** Neither bound is checked.

**Separation folded into a stress margin.** It is a discontinuity, not a stress.

**Edge distance below 2D.** Sudden shear-out instead of progressive bearing.

**Member stiffness from a mid-grip area.** Rises with grip length, which is impossible.

**Cone started at the shank.** Member stiffness understated 1.7x.

**Preload relaxation ignored in an aluminium joint.** It relaxes more than steel.

---

## Worked numbers

From [`BoltedJoint`](../aerospaceStructuresLibrary/BoltedJoint.py), 6.35 mm A286 bolt in 2219-T87, 12 mm grip:

| Quantity | Value |
|---|---|
| Bolt stiffness | 395.9 MN/m |
| Member stiffness | 1061.7 MN/m |
| Stiffness ratio | 2.68 |
| **Load factor Phi** | **0.2716** |
| Of 4.00 kN applied, to the bolt | **1.09 kN** |
| Separation load | 8.32 kN |

**Member stiffness falls with grip length**, as it must:

| Grip | k_member | Phi |
|---|---|---|
| 8 mm | 586.5 MN/m | 0.503 |
| 12 mm | 479.7 MN/m | 0.452 |
| 24 mm | 368.8 MN/m | 0.349 |
| 40 mm | 322.3 MN/m | **0.269** |

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-5020** | Requirements for threaded fastening systems |
| VDI 2230 | Systematic calculation of high duty bolted joints |
| NASM 33540 | Fastener hole preparation |
| **ASTM B850** | Post-coating hydrogen embrittlement relief baking |
| ASTM F519 | Mechanical hydrogen embrittlement testing |
| MMPDS Chapter 8 | Joint allowables |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'aerospaceStructuresLibrary')

from BoltedJoint import BoltedJoint

joint = BoltedJoint()
joint.setInputs({'boltDiameter': 0.00635, 'memberMaterial': '2219-T87',
                 'memberCondition': 't87', 'gripLength': 0.012,
                 'memberThickness': 0.006, 'edgeDistance': 0.0127,
                 'appliedTension': 4.0e3, 'appliedShear': 3.0e3})

diagram = joint.calculateJointDiagram()
for finding in diagram['findings']:
    print(finding)

members = joint.calculateMemberChecks()
print(f'edge distance ratio {members["edgeDistanceRatio"]:.2f}, '
      f'adequate {members["edgeDistanceAdequate"]}')
```

---

## References

1. NASA-STD-5020B, *Requirements for Threaded Fastening Systems in Spaceflight Hardware*.
2. Bickford, J. H., *An Introduction to the Design and Behavior of Bolted Joints*, 4th ed., CRC Press, 2007.
3. VDI 2230 Part 1, *Systematic Calculation of Highly Stressed Bolted Joints*.
