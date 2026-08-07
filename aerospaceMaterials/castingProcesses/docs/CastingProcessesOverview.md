[Home](../README.md) > Casting Processes Overview

# Casting Processes Overview

## Contents

- [Overview](#overview)
- [The routes](#the-routes)
- [The casting factor is the whole trade](#the-casting-factor-is-the-whole-trade)
- [Where casting wins](#where-casting-wins)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [Document index](#document-index)
- [References](#references)

---

## Overview

Casting is the cheapest route to a complex shape and it carries a knockdown that no other route does. The reason is that a casting's properties are a property of the process rather than of the alloy: the same alloy, the same chemistry and the same heat treatment produce different mechanical properties depending on how it solidified and what got trapped while it did.

Centrifugal casting has its own sub-domain in [spinCasting](../../spinCasting/). This one covers the static routes.

---

## The routes

| Route | Min wall | Max mass | Tolerance | Ra | Lead | Cost |
|---|---|---|---|---|---|---|
| **Investment** | 1.5 mm | 50 kg | DCTG 6 | 3.2 um | 20 wk | 1.2 |
| **Sand** | 5 mm | 2000 kg | DCTG 11 | 25 um | 12 wk | 0.5 |
| **Die** | 1.0 mm | 25 kg | DCTG 4 | 1.6 um | 26 wk | 0.4 |
| **Permanent mould** | 3.5 mm | 150 kg | DCTG 8 | 12.5 um | 16 wk | 0.7 |

**Investment casting is the dominant aerospace route.** Complex geometry in one piece with an excellent as-cast surface, at a real tooling cost and a 20 week lead time.

**Die casting has the best dimensions and the worst qualification story.** The fast fill entraps gas, which produces porosity that cannot be closed by HIP because the gas re-expands. Aluminium and zinc only in practice, and it is difficult to qualify for structure.

**Sand casting is cheap, large and coarse.** It is rarely a flight structure route without a qualification programme, and it is the right answer for tooling, fixtures and ground equipment.

---

## The casting factor is the whole trade

| Factor | Allowable | Mass penalty | Requirements |
|---|---|---|---|
| **1.00** | 1.000 | 1.00x | Qualified process, 100 % volumetric NDE, three sample lots, SPC |
| **1.33** | 0.752 | 1.33x | Documented process, sample NDE, one qualification lot |
| **2.00** | **0.500** | **2.00x** | **Default. Nothing qualified** |

**A factor of 2.0 halves the allowable, so the part needs twice the material to carry the same load.** No alloy substitution recovers that.

**Qualifying the process is frequently cheaper than the mass the default factor costs**, and that comparison is almost never made because the two numbers sit in different budgets: one in manufacturing engineering and one in mass properties.

**Making that trade visible is the point of running the [`CastingProcess`](../castingProcessesLibrary/CastingProcess.py) class.**

---

## Where casting wins

| Condition | Why |
|---|---|
| **Complex geometry** | One piece rather than a weldment or a machining |
| **Low buy-to-fly** | 1.6 : 1 investment against 8 : 1 machining |
| Internal passages | Cast in with cores, and inspectable if the geometry allows |
| Quantity | The tooling amortises |
| **A qualified process** | Then it is cheapest with a full allowable |

**Casting competes directly with additive** on complex geometry, and the discrimination is quantity and size: additive wins at one-off and small, casting wins at quantity and large. See [ProcessComparison.md](ProcessComparison.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Casting factor 2.0 | Halves the allowable |
| Investment for aerospace complexity | 1.5 mm walls, DCTG 6 |
| Sand for large and cheap | 5 mm walls, DCTG 11 |
| Die casting is hard to qualify | Entrapped gas |
| Riser modulus | >= 1.2 x casting modulus |
| Solidification shrinkage | 3 % steel to 6.5 % aluminium |
| Casting yield | 50 to 80 % |
| HIP does not close surface connected porosity | No pressure differential |

---

## Failure modes

**Unqualified casting used at the qualified allowable.** Half the strength assumed.

**Riser satisfying timing but not volume.** A cavity under the riser neck.

**Riser satisfying volume but not timing.** Centreline shrinkage in the heavy section.

**Pattern shrinkage wrong.** Every casting from that tool is the wrong size.

**Die casting specified for a structural part.** Entrapped gas, and it cannot be HIPed out.

**Wall below the process minimum.** A misrun.

---

## Worked numbers

From [`CastingProcess`](../castingProcessesLibrary/CastingProcess.py), a 100 cm^3 stainless investment casting with a 0.05 m^2 cooling area:

| Quantity | Value |
|---|---|
| Casting modulus | 2.00 mm |
| Solidification time | 6 s |
| Riser diameter | 14.4 mm |
| **Binding riser condition** | **volume** |
| Casting yield | 78 % |
| Machining stock | 1.74 mm |
| Pattern oversize | 1.80 mm |

| Casting factor | Allowable | Mass penalty | Saving available |
|---|---|---|---|
| 1.00 | 1.000 | 1.00x | 0 % |
| 1.33 | 0.752 | 1.33x | 25 % |
| **2.00** | **0.500** | **2.00x** | **50 %** |

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-5001** | Structural design and test factors, including casting factors |
| NASA-STD-6016 | Materials and processes requirements |
| **AMS 2175** | Castings, classification and inspection |
| ISO 8062 | Casting dimensional tolerances and machining allowances |
| ASTM E446 / E186 / E280 | Reference radiographs for steel castings |
| AMS-A-21180 | Aluminium alloy castings, high strength |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'castingProcessesLibrary')

from CastingProcess import CastingProcess

casting = CastingProcess()
casting.setInputs({'process': 'investment', 'material': '316L', 'alloyFamily': 'stainless',
                   'castingVolume': 1.0e-4, 'castingSurfaceArea': 0.05,
                   'qualificationLevel': 2.00})

casting.calculateSolidification()
casting.sizeRiser()
casting.selectCastingFactor()
casting.calculateMachiningAllowance()
print(casting.generateReport())
```

---

## Document index

| Document | Covers |
|---|---|
| [InvestmentCasting.md](InvestmentCasting.md) | Pattern, shell, burnout, pour |
| [SandCasting.md](SandCasting.md) | Green sand, chemically bonded, and where it fits |
| [DieCasting.md](DieCasting.md) | High pressure, and why it is hard to qualify |
| [Solidification.md](Solidification.md) | Chvorinov, modulus, directional solidification |
| [RiserAndGating.md](RiserAndGating.md) | Modulus method, feeding, gating ratios |
| [CastingFactorAndQualification.md](CastingFactorAndQualification.md) | The ladder and what earns each step |
| [Defects.md](Defects.md) | Porosity, shrinkage, cold shut, inclusions |
| [Inspection.md](Inspection.md) | RT, penetrant, and what each finds |
| [ToleranceAndAllowance.md](ToleranceAndAllowance.md) | ISO 8062, machining stock, pattern shrinkage |
| [ProcessComparison.md](ProcessComparison.md) | Against wrought and additive |

---

## References

1. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
2. ASM Handbook Volume 15, *Casting*.
3. NASA-STD-5001B, *Structural Design and Test Factors of Safety for Spaceflight Hardware*.
