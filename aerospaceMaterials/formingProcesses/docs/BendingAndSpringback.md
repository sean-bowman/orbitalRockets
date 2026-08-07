[Home](../README.md) > Bending and Springback

# Bending and Springback

## Contents

- [Overview](#overview)
- [Minimum bend radius](#minimum-bend-radius)
- [Grain direction](#grain-direction)
- [Springback](#springback)
- [Bend allowance and the k factor](#bend-allowance-and-the-k-factor)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Three questions have to be answered before a bend can be made: how tight it can be without cracking, how much it will spring back, and how long the blank has to be. They are independent and each has a closed form.

---

## Minimum bend radius

**Bending stretches the outer fibre and compresses the inner one**, and the limit is when the outer fibre reaches the material's tensile ductility.

The outer fibre strain in a bend of radius `r` on thickness `t` is approximately

```
eps = 1 / (2r/t + 1)
```

Setting that equal to the true fracture strain, which relates to reduction of area as `ln(1/(1-RA))`, and simplifying against the empirical data gives the standard relation:

```
r_min / t = 50 / RA - 1        RA in percent
```

| Material | RA | r_min / t | On 2 mm sheet |
|---|---|---|---|
| **316L annealed** | 70 % | 0.00 | Flat on itself |
| **6061-T6** | 45 % | 0.11 | 0.22 mm |
| 2219-T87 | 35 % | 0.43 | 0.86 mm |
| **7075-T73** | 30 % | 0.67 | 1.33 mm |
| **Ti-6Al-4V annealed** | 25 % | 1.00 | 2.00 mm |
| Ti-6Al-4V STA | 15 % | 2.33 | 4.67 mm |

**RA above 50 percent means the material can be bent flat on itself**, which the formula gives directly and which matches practice for annealed austenitic stainless.

**Temper dominates.** 6061 in T6 bends at `r/t` = 0.11 and in the O condition it bends flat, and Ti-6Al-4V goes from 1.00 annealed to 2.33 in the STA condition. That is the same alloy in every case.

**Titanium is also bent hot** at 200 to 300 degC, which raises its ductility substantially and is standard practice for tight bends.

---

## Grain direction

**Bending across the rolling direction is easier than bending along it**, and the difference is large enough to matter.

| Bend orientation | Ductility |
|---|---|
| **Bend line perpendicular to rolling** | Lower. The crack runs along the elongated grains |
| **Bend line parallel to rolling** | Higher |

**Rolling elongates the grains and aligns the inclusion stringers.** A bend whose tension direction is along the stringers finds a ready crack path.

**The practical rule is to orient the bend line across the rolling direction**, and where a part needs bends in two directions, the tighter one gets the favourable orientation.

**A part with bends in both directions may need a larger radius on both** than either would need alone, and that is worth catching at layout rather than at first article.

---

## Springback

**Elastic recovery when the punch is withdrawn**, and it is unavoidable because the bend is elastic-plastic rather than fully plastic.

The ratio of final to initial bend radius follows from beam theory:

```
r_i / r_f = 4 (r_i sigma_y / (E t))^3 - 3 (r_i sigma_y / (E t)) + 1
```

**The governing group is `sigma_y / E`**, and that is the whole story:

| Material | sigma_y [MPa] | E [GPa] | sigma_y / E | Springback |
|---|---|---|---|---|
| 316L annealed | 205 | 193 | 0.0011 | Low |
| 6061-T6 | 276 | 68.9 | 0.0040 | Moderate |
| 7075-T73 | 400 | 71.7 | 0.0056 | High |
| **Ti-6Al-4V** | 828 | **113.8** | **0.0073** | **Highest** |

**Titanium is the worst case** because it has a high yield strength and a low modulus, which is the same combination that makes it a good spring material.

**Springback is compensated by overbending.** The punch angle is set larger than the target so the part springs back to the right angle, and the compensated angle is what goes on the tool.

**A larger radius springs back more**, because `r sigma_y / (E t)` grows with `r`. That means a generous bend radius costs more compensation, and a tight bend springs back less.

**Bottoming and coining reduce springback** by plastically deforming through the full thickness at the bend, and they need much higher press force.

---

## Bend allowance and the k factor

**The blank length is not the sum of the flat lengths**, because the material at the bend is stretched on the outside and compressed on the inside, and the neutral axis is not at mid-thickness.

```
bendAllowance = angle * (r + k * t)
```

**The `k` factor locates the neutral axis** as a fraction of the thickness from the inside surface.

| r / t | k |
|---|---|
| < 1 | 0.33 |
| 1 to 3 | 0.40 |
| > 3 | 0.50 |

**The neutral axis shifts inward on a tight bend.** At `r/t` below 1 it sits at a third of the thickness, not half, because the outer fibre stretches more than the inner one compresses.

**Using `k` = 0.5 on a tight bend gives a blank that is too long** and a part that is oversize after bending. On a single bend that is a small error; on a part with six bends it accumulates.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Minimum bend radius | `r/t = 50/RA - 1` |
| RA above 50 % | Bends flat on itself |
| Bend line across the rolling direction | Higher ductility |
| Springback scales with `sigma_y / E` | Titanium is the worst |
| Larger radius springs back more | |
| Compensate by overbending | Put the compensated angle on the tool |
| `k` factor | 0.33 tight, 0.50 generous |
| Bend titanium hot | 200 to 300 degC |

---

## Failure modes

**T6 temper bent at the annealed radius.** Outer fibre cracking.

**Bend line along the rolling direction.** Cracking at a radius that works the other way.

**Springback uncompensated.** Every part the same amount out of tolerance.

**`k` = 0.5 on a tight bend.** Blank too long, part oversize.

**Titanium bent cold at a tight radius.** Cracking. It should be hot formed.

**Springback compensation carried between materials.** It is a material property.

---

## Worked numbers

From [`FormingProcess`](../formingProcessesLibrary/FormingProcess.py), 2 mm sheet, 90 degree bend, 10 mm bend radius:

| Material | r_min | Springback | Compensated angle |
|---|---|---|---|
| **316L annealed** | **0.00 mm** | **1.19 deg** | 91.19 deg |
| 6061-T6 | 0.86 mm | 5.40 deg | 95.40 deg |
| 7075-T73 | 2.00 mm | 8.18 deg | 98.18 deg |
| **Ti-6Al-4V annealed** | **2.00 mm** | **10.42 deg** | **100.42 deg** |

**Titanium springs back nearly nine times as far as 316L** at the same geometry, and the ordering follows `sigma_y / E` exactly.

**The bend allowance is 17.18 mm in every case**, because it is a geometry result at a given radius and it does not depend on the material.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM E290** | Bend testing of material for ductility |
| ASTM E8 / E8M | Tension testing, for RA |
| AMS 2770 | Heat treatment of wrought aluminium alloys |
| SAE ARP1917 | Clarification of terms for sheet metal forming |

---

## Tool interface

```python
from FormingProcess import FormingProcess, FORMING_PROCESSES

for material, condition in (('6061', 't6'), ('TI-6AL-4V', 'annealed'), ('316L', 'annealed')):
    forming = FormingProcess()
    forming.setInputs({'material': material, 'condition': condition, 'process': 'air bend',
                       'thickness': 0.002, 'bendAngle': 90.0, 'bendRadius': 0.010})
    bend = forming.calculateMinimumBendRadius()
    back = forming.calculateSpringback()
    print(f'{material:14s} r_min {bend["minimumBendRadius"]*1000:5.2f} mm, '
          f'compensated angle {back["compensatedAngle"]:6.2f} deg')
```

---

## References

1. Hosford, W. F. and Caddell, R. M., *Metal Forming: Mechanics and Metallurgy*, 4th ed., Cambridge, 2011.
2. Marciniak, Z., Duncan, J. L. and Hu, S. J., *Mechanics of Sheet Metal Forming*, 2nd ed., Butterworth-Heinemann, 2002.
3. ASM Handbook Volume 14B, *Metalworking: Sheet Forming*.
