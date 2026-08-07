[Home](../README.md) > Cutting Force

# Cutting Force

## Contents

- [Overview](#overview)
- [Specific cutting energy](#specific-cutting-energy)
- [The force components](#the-force-components)
- [Power and spindle sizing](#power-and-spindle-sizing)
- [Chip thinning](#chip-thinning)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Cutting force sizes the spindle, sizes the fixture, and feeds the deflection and chatter analyses. It comes from one material property and the chip cross section.

---

## Specific cutting energy

**The energy needed to remove unit volume of material**, and it is the material property that governs cutting force.

```
F_t = k_s * A_chip
```

| Material | k_s [J/mm^3] |
|---|---|
| **6061-T6** | **0.7** |
| 2219-T87 | 0.8 |
| 7075-T73 | 0.8 |
| 4340 | 2.8 |
| 316L | 3.0 |
| 17-4PH | 3.2 |
| TI-6AL-4V | 3.5 |
| **INCONEL 718** | **4.5** |

**Aluminium is six times easier than Inconel** on force alone, and that is before the tool life difference.

**Specific energy rises as the chip gets thinner**, which is the size effect: a very thin chip costs more energy per unit volume than a thick one because a larger fraction of the work goes into ploughing and rubbing rather than shearing. The tabulated values are for a nominal chip thickness and light finishing cuts exceed them.

**The rake angle also matters** and a positive rake reduces the force. That is one reason aluminium tooling is ground with a high positive rake and nickel tooling is not: the aluminium tool can afford the weaker edge.

---

## The force components

| Component | Direction | Typical magnitude |
|---|---|---|
| **Tangential, `F_t`** | Along the cutting velocity | **1.0** |
| **Radial, `F_r`** | Perpendicular, into the work | **0.3 to 0.5** |
| Axial, `F_a` | Along the tool axis | 0.2 to 0.4 |

**The tangential force sets the power.** It acts along the cutting speed, so power is force times speed.

**The radial force sets the deflection**, both of the tool and of the workpiece. It is the component that pushes a thin wall away from the cutter, so it is the one that appears in the thin wall analysis. See [ThinWallMachining.md](ThinWallMachining.md).

**The ratio is not constant** and it depends on the rake angle, the tool wear and the chip thickness. A worn tool has a much higher radial force ratio, which is why a part machined with a worn tool is dimensionally different from one machined with a sharp one.

---

## Power and spindle sizing

```
P = F_t * V
P_spindle = P / efficiency
```

**Machine efficiency is 70 to 85 percent** for a typical spindle drive.

**Aluminium machining is power limited and nickel machining is not.** That sounds backwards and it follows from the speeds: aluminium is cut at 800 m/min and removes material fast, so a high speed aluminium machining centre needs 30 to 50 kW; Inconel is cut at 40 m/min, so despite six times the specific energy the power is lower.

**The material removal rate is the useful framing:**

```
P = k_s * MRR
```

**A 40 kW spindle at 85 percent efficiency removes about 48,000 mm^3/min of aluminium and about 7,500 of Inconel**, and that ratio is the real cost difference in roughing.

**Torque limits at low speed.** A large diameter cutter at a low spindle speed can exceed the machine's torque limit long before its power limit, and that is the constraint on heavy roughing in nickel alloys.

---

## Chip thinning

**The radial engagement changes the actual chip thickness**, and ignoring it under-feeds the cut.

When the radial depth is less than half the cutter diameter, the maximum chip thickness is less than the feed per tooth:

```
h_max = f_z * sqrt(1 - (1 - 2 a_e / D)^2)      approximately, for a_e < D/2
```

| Radial engagement | Chip thinning factor |
|---|---|
| 50 % of diameter | 1.00 |
| 25 % | 0.87 |
| **10 %** | **0.60** |
| 5 % | 0.44 |

**At 10 percent radial engagement the actual chip is 60 percent of the programmed feed per tooth**, so the feed has to be raised by 1/0.6 to get the intended chip.

**Running a light radial cut at the nominal feed rubs rather than cuts**, which generates heat, work hardens the surface and wears the tool rapidly without removing much material.

**High speed machining strategies depend on this** and they run very light radial engagements at greatly increased feed rates. The chip stays a reasonable thickness, the engagement time per flute is short, and the heat goes into the chip.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| `F_t = k_s A_chip` | The whole calculation |
| Specific energy | 0.7 aluminium to 4.5 IN718 |
| Radial force | 0.3 to 0.5 of tangential |
| `P = k_s MRR` | The useful framing |
| Spindle efficiency | 70 to 85 % |
| Compensate for chip thinning below 50 % radial | Raise the feed |
| Aluminium machining is power limited | Nickel is not |
| A worn tool has a higher radial force | Different dimensions |

---

## Failure modes

**Chip thinning ignored on a light radial cut.** Rubbing, heat and rapid wear.

**Spindle sized on specific energy alone.** Aluminium needs the power, not Inconel.

**Torque limit ignored on a large cutter at low speed.** Stall.

**Radial force omitted from the fixture calculation.** The part moves.

**Force computed with a sharp tool ratio and the tool is worn.** The deflection is larger.

---

## Worked numbers

From [`MachiningProcess.calculateCuttingForce`](../machiningProcessesLibrary/MachiningProcess.py), a 12 mm end mill, 5 mm axial, 3 mm radial, 0.1 mm/tooth at 36 m/min:

| Material | Cutting force | Spindle power |
|---|---|---|
| **6061** | **93.8 N** | 0.06 kW |
| 316L | 287.5 N | 0.17 kW |
| **INCONEL 718** | **500.0 N** | 0.30 kW |

**The force ratio is 5.3x from 6061 to Inconel 718**, tracking the specific cutting energy directly.

**The powers are small because the cut is small.** Roughing at production depths scales both by the material removal rate, and it is there that the aluminium machine's 40 kW spindle earns its keep.

---

## Standards

| Standard | Scope |
|---|---|
| ISO 3685 | Tool life testing with single point turning tools |
| ISO 8688 | Tool life testing in milling |
| ASME B5.54 | Performance evaluation of machining centres |
| SAE ARP4915 | Aerospace machining practices |

---

## Tool interface

```python
from MachiningProcess import MachiningProcess, MACHINABILITY

for material in ('6061', '316L', 'INCONEL 718'):
    machining = MachiningProcess()
    machining.setInputs({'material': material, 'process': 'end mill',
                         'toolDiameter': 0.012, 'axialDepth': 0.005,
                         'radialDepth': 0.003, 'feedPerTooth': 0.0001})
    result = machining.calculateCuttingForce()
    print(f'{material:14s} F {result["cuttingForce"]:7.1f} N  '
          f'P {result["spindlePower"]/1000:5.2f} kW  '
          f'MRR {result["removalRateCubicCentimetrePerMinute"]:6.1f} cm^3/min')
```

---

## References

1. Shaw, M. C., *Metal Cutting Principles*, 2nd ed., Oxford University Press, 2005.
2. Altintas, Y., *Manufacturing Automation*, 2nd ed., Cambridge University Press, 2012.
3. ASM Handbook Volume 16, *Machining*.
