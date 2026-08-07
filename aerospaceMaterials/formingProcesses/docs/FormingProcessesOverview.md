[Home](../README.md) > Forming Processes Overview

# Forming Processes Overview

## Contents

- [Overview](#overview)
- [The processes](#the-processes)
- [Why forming wins](#why-forming-wins)
- [The two properties that govern everything](#the-two-properties-that-govern-everything)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [Document index](#document-index)
- [References](#references)

---

## Overview

Forming shapes metal by plastic deformation. It removes no material, it retains and improves the wrought grain structure, and it produces most of the primary structure in a launch vehicle: tank domes, barrel sections, skins, brackets and rings.

The two properties that govern all of it are the material's reduction of area, which sets how far it can be bent, and its work hardening exponent, which sets how far it can be stretched.

---

## The processes

| Process | Min r/t | Tolerance | Tooling | Rate | Use |
|---|---|---|---|---|---|
| **Brake bending** | 1.0 | +/- 0.5 mm | Low | Slow | Brackets, small parts |
| **Roll forming** | 2.0 | +/- 1.0 mm | Medium | Fast | Long constant sections |
| **Deep drawing** | 3.0 | +/- 0.3 mm | High | Fast | Cups, closures |
| **Stretch forming** | 4.0 | +/- 1.0 mm | Medium | Slow | **Skins, tank domes** |
| **Hydroforming** | 2.0 | +/- 0.2 mm | Medium | Medium | Complex shallow shapes |
| **Spinning** | 2.0 | +/- 0.5 mm | Low | Slow | **Domes, cones, one-offs** |
| **Flow forming** | -- | +/- 0.1 mm | Medium | Medium | **Thin walled cylinders** |
| **Superplastic forming** | 0.5 | +/- 0.5 mm | High | **Very slow** | Complex titanium |

---

## Why forming wins

| Axis | Forming | Machining |
|---|---|---|
| **Buy-to-fly** | 1.1 to 1.5 : 1 | 5 to 10 : 1 |
| **Grain structure** | Wrought, and worked further | Wrought, cut through |
| **Rate** | Fast once tooled | Slow |
| Tooling | Required | None |
| Tolerance | Moderate | Excellent |

**The buy-to-fly advantage is decisive on a large thin structure.** A machined tank dome would start as a solid billet the size of the dome, and the notion is absurd; a spun or stretch-formed dome starts as a plate of roughly the finished area.

**Grain flow follows the shape** in a formed part, which is the same advantage a forging has. A machined part cuts through the grain flow of the stock it came from.

---

## The two properties that govern everything

### Reduction of area, for bending

```
r_min / t = 50 / RA - 1
```

**Bending is a surface strain problem.** The outer fibre of a bend is stretched, and how far it can be stretched before it cracks is set by the material's tensile ductility, measured as reduction of area.

| Material | RA | r_min / t |
|---|---|---|
| 6061-T6 | 45 % | **0.11** |
| 7075-T73 | 30 % | 0.67 |
| 316L annealed | 70 % | 0.00 |
| Ti-6Al-4V annealed | 25 % | **1.00** |

**The relation says a material with RA above 50 percent can be bent flat on itself**, and that is broadly true of annealed austenitic stainless.

### Work hardening exponent, for stretching

```
sigma = K * eps^n
```

**The uniform elongation equals n.** That is the direct and useful consequence: a material with n = 0.25 can be stretched 25 percent uniformly before it necks, and no further.

| Material | n | K [MPa] | Uniform elongation |
|---|---|---|---|
| **316L annealed** | **0.45** | 1400 | **45 %** |
| 6061-O | 0.22 | 400 | 22 % |
| 6061-T6 | 0.05 | 450 | **5 %** |
| Ti-6Al-4V | 0.08 | 1100 | 8 % |

**Temper is more important than alloy here.** 6061 in the O condition stretches 22 percent and in T6 it stretches 5 percent, and that is the same alloy. **Form in the annealed condition and heat treat afterwards** is the resulting rule, and it is close to universal.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Minimum bend radius | `r/t = 50/RA - 1` |
| Uniform elongation | Equals `n` |
| Form annealed, heat treat after | Almost always |
| Bend across the rolling direction | Higher RA transverse to the grain |
| Springback grows with `sigma_y / E` | Titanium is the worst |
| Neutral axis shifts inward on a tight bend | `k` factor 0.33 to 0.5 |
| Buy-to-fly | 1.1 to 1.5 : 1 |

---

## Failure modes

**Bending a T6 temper at the annealed radius.** Cracking on the outer fibre.

**Springback not compensated.** Every part out of angular tolerance the same way.

**Strain path ignored in the forming limit check.** Plane strain is the worst case and it is not the obvious one.

**Bend along the rolling direction.** Lower transverse ductility, and it cracks.

**Bend allowance computed with `k` = 0.5 on a tight bend.** The blank is the wrong length.

---

## Worked numbers

From [`FormingProcess`](../formingProcessesLibrary/FormingProcess.py), 2 mm sheet, 90 degree bend, 10 mm bend radius:

| Material | RA | r_min | Springback | Compensated punch angle |
|---|---|---|---|---|
| **316L annealed** | 70 % | **0.00 mm** | 1.19 deg | 91.19 deg |
| 6061-T6 | 45 % | 0.86 mm | 5.40 deg | 95.40 deg |
| **Ti-6Al-4V** | 25 % | **2.00 mm** | **10.42 deg** | **100.42 deg** |

**Titanium's springback is the largest** because springback scales with `sigma_y / E` and titanium has both a high yield strength and a low modulus.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM E290** | Bend testing of material for ductility |
| ASTM E8 / E8M | Tension testing of metallic materials |
| ASTM E646 | Tensile strain hardening exponents of sheet |
| ASTM E2218 | Determining forming limit curves |
| AMS 2770 | Heat treatment of wrought aluminium alloys |
| SAE AMS-STD-2154 | Ultrasonic inspection of wrought metals |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'formingProcessesLibrary')

from FormingProcess import FormingProcess

forming = FormingProcess()
forming.setInputs({'material': '6061', 'condition': 't6', 'process': 'air bend',
                   'thickness': 0.002, 'bendAngle': 90.0, 'bendRadius': 0.010})

forming.calculateMinimumBendRadius()
forming.calculateSpringback()
forming.calculateBendAllowance()
print(forming.generateReport())
```

---

## Document index

| Document | Covers |
|---|---|
| [SheetMetalForming.md](SheetMetalForming.md) | Brake, roll, deep draw, stretch |
| [BendingAndSpringback.md](BendingAndSpringback.md) | Minimum radius, springback, bend allowance |
| [FormingLimitDiagram.md](FormingLimitDiagram.md) | Strain paths, the FLD, and why plane strain is worst |
| [WorkHardening.md](WorkHardening.md) | The power law, uniform elongation, anneal scheduling |
| [Hydroforming.md](Hydroforming.md) | Sheet and tube, pressure sizing |
| [SpinningAndFlowForming.md](SpinningAndFlowForming.md) | Domes, cones and thin walled cylinders |
| [Forging.md](Forging.md) | Open die, closed die, grain flow |
| [RingRolling.md](RingRolling.md) | Seamless rings, circumferential grain flow |
| [SuperplasticForming.md](SuperplasticForming.md) | Titanium, SPF/DB, and why it is slow |
| [Defects.md](Defects.md) | Splitting, wrinkling, orange peel, tearing |
| [ProcessComparison.md](ProcessComparison.md) | Against machining, casting and additive |

---

## References

1. Hosford, W. F. and Caddell, R. M., *Metal Forming: Mechanics and Metallurgy*, 4th ed., Cambridge, 2011.
2. Marciniak, Z., Duncan, J. L. and Hu, S. J., *Mechanics of Sheet Metal Forming*, 2nd ed., Butterworth-Heinemann, 2002.
3. ASM Handbook Volume 14A, *Metalworking: Bulk Forming*, and 14B, *Sheet Forming*.
