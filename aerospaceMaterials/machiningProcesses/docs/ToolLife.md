[Home](../README.md) > Tool Life

# Tool Life

## Contents

- [Overview](#overview)
- [The Taylor equation](#the-taylor-equation)
- [The speed sensitivity](#the-speed-sensitivity)
- [The values](#the-values)
- [Wear modes](#wear-modes)
- [Choosing the speed](#choosing-the-speed)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Tool life is the strongest function of cutting speed in machining, and the relation is a power law with a small exponent, which is what makes the sensitivity so severe.

---

## The Taylor equation

```
V * T^n = C
```

| Symbol | Meaning |
|---|---|
| `V` | Cutting speed [m/min] |
| `T` | Tool life [min] |
| `n` | **Taylor exponent**, 0.18 to 0.30 |
| `C` | The speed giving one minute of life [m/min] |

**`C` is the cutting speed at one minute of tool life** by definition, which makes it a convenient material and tool constant.

**`n` is the sensitivity** and a small `n` means a steep dependence. It is a property of the tool material more than of the workpiece: carbide has a higher `n` than high speed steel, and ceramic higher still.

---

## The speed sensitivity

**The consequence of a small exponent, and it is the reason cutting speed is controlled so tightly.**

Rearranging for the life ratio at two speeds:

```
T_2 / T_1 = (V_1 / V_2)^(1/n)
```

**`1/n` is between 3.3 and 5.6**, so a modest speed change is a large life change.

| Speed increase | n = 0.30 | n = 0.20 | n = 0.18 |
|---|---|---|---|
| +10 % | 0.70x life | 0.56x | 0.53x |
| **+20 %** | **0.51x** | **0.33x** | **0.30x** |
| +50 % | 0.26x | 0.13x | 0.11x |

**A 20 percent speed increase on Inconel 718 costs 70 percent of the tool life.** That is why the machining of nickel alloys is run at conservative speeds and why the speed is the parameter that gets locked down in a process specification.

**It also means that a 20 percent speed reduction triples the tool life**, which is the trade available when tooling cost dominates or when a tool change mid-part is unacceptable.

**Feed and depth of cut have far weaker effects.** The extended Taylor equation carries exponents of roughly 0.15 for feed and 0.05 for depth, against 1.0 for speed. **Take a deeper cut before taking a faster one** is the direct consequence and it is one of the more useful rules in machining.

---

## The values

| Material | n | C [m/min] | Machinability |
|---|---|---|---|
| 6061-T6 | 0.30 | 800 | 190 |
| 2219-T87 | 0.28 | 600 | 130 |
| 7075-T73 | 0.28 | 550 | 120 |
| 4340 | 0.22 | 200 | 55 |
| 316L | 0.20 | 150 | 45 |
| 17-4PH H1025 | 0.20 | 140 | 40 |
| **TI-6AL-4V** | 0.20 | **75** | 22 |
| **INCONEL 718** | **0.18** | **40** | **12** |

**Inconel 718 has both the lowest `C` and the lowest `n`**, meaning it must be cut slowly and it punishes any deviation hardest. That combination is what makes nickel superalloy machining a speciality.

**Aluminium's n = 0.30 is forgiving** as well as fast, which is part of why aluminium machining tolerates aggressive programming.

---

## Wear modes

**Tool life ends in different ways and the mode says what to change.**

| Mode | Appearance | Cause | Fix |
|---|---|---|---|
| **Flank wear** | Uniform land on the flank | Abrasion. The normal mode | Accept, or a harder grade |
| **Crater wear** | A crater on the rake face | Diffusion at high temperature | Coating, lower speed |
| **Built-up edge** | Material welded to the edge | Low speed, ductile material | **Higher speed** |
| **Notching** | A notch at the depth of cut line | Work hardened layer, oxidation | Vary the depth, ramp entry |
| **Chipping** | Small edge fractures | Interrupted cut, vibration | Tougher grade, stabilise |
| Thermal cracking | Comb cracks across the edge | Thermal cycling, coolant on a hot edge | Continuous coolant or none |

**Flank wear is the intended mode** and the tool life criterion in ISO 3685 is a flank wear land of 0.3 mm.

**Built-up edge is fixed by going faster**, which is the one wear mode where the intuitive response is wrong. At low speed the chip welds to the rake face; above a critical speed the temperature is high enough that it does not.

**Notching is the characteristic nickel alloy failure** and it happens at the depth of cut line where the tool meets the work hardened layer left by the previous pass. Varying the depth of cut between passes spreads the notch and extends the life substantially.

**Thermal cracking argues against intermittent coolant.** A tool that is quenched every revolution in an interrupted cut cracks; either flood it continuously or run it dry.

---

## Choosing the speed

| Objective | Approach |
|---|---|
| **Minimum cost** | Balance tool cost against machine time |
| **Maximum rate** | Higher speed, shorter life |
| **A complete part per tool** | Set the life to the part cycle time |
| Unattended running | Long life, conservative speed |

**Setting the tool life to the part cycle time is the practical aerospace answer** on a long-running part, because a tool change mid-cut leaves a witness mark and a dimensional step.

**Minimum cost speed is lower than maximum rate speed**, always, because tool cost rises faster than machine time falls once the life gets short.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| `V T^n = C` | The Taylor equation |
| `1/n` is 3.3 to 5.6 | The life sensitivity |
| +20 % speed | Roughly a third to a half of the life |
| Deeper before faster | Depth exponent ~0.05, speed 1.0 |
| Flank wear 0.3 mm | The ISO 3685 criterion |
| Built-up edge | Go faster |
| Notching in nickel | Vary the depth of cut |
| Set the life to the part cycle | Avoid mid-cut tool changes |

---

## Failure modes

**Speed raised 20 % to save time.** Two thirds of the tool life gone.

**Built-up edge treated by slowing down.** It gets worse.

**Constant depth of cut in nickel.** Notching at the same line every pass.

**Intermittent coolant on an interrupted cut.** Thermal cracking.

**Tool change mid-cut.** A witness mark and a dimensional step.

**Taylor constants taken from a handbook for a different tool grade.** They are tool properties as much as material ones.

---

## Worked numbers

From [`MachiningProcess.calculateToolLife`](../machiningProcessesLibrary/MachiningProcess.py), a 12 mm end mill at 36 m/min:

| Material | n | Tool life | Slowing 20 % multiplies the life by |
|---|---|---|---|
| **6061** | 0.30 | 19769 min | **1.84** |
| **316L** | 0.20 | 3125 min | **2.49** |
| **INCONEL 718** | **0.18** | **2.0 min** | **3.37** |

**The class returns `1.2^(1/n)`, which is the life gained by slowing 20 percent.** Speeding up by 20 percent leaves its reciprocal: 54 percent of the life at n = 0.30 and **30 percent at n = 0.18**.

**Inconel 718 at 36 m/min gives 2 minutes of tool life**, against 19769 for 6061 at the same speed. That is the machinability spread expressed as directly as it can be: the same cut, four orders of magnitude apart in tool life.

---

## Standards

| Standard | Scope |
|---|---|
| **ISO 3685** | Tool life testing with single point turning tools |
| **ISO 8688-1 / -2** | Tool life testing in milling, face and end milling |
| ISO 513 | Classification of hard cutting materials |
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
    result = machining.calculateToolLife()
    print(f'{material:14s} V {result["cuttingSpeedMetresPerMinute"]:5.0f} m/min  '
          f'T {result["toolLifeMinutes"]:7.1f} min  '
          f'slowing 20 % multiplies the life by {result["lifeRatioForTwentyPercentFaster"]:5.2f}')
```

---

## References

1. Taylor, F. W., *On the Art of Cutting Metals*, ASME, 1907.
2. Shaw, M. C., *Metal Cutting Principles*, 2nd ed., Oxford University Press, 2005.
3. ISO 3685, *Tool-Life Testing with Single-Point Turning Tools*.
