[Home](../README.md) > Casting Factor and Qualification

# Casting Factor and Qualification

## Contents

- [Overview](#overview)
- [The ladder](#the-ladder)
- [Why the factor exists](#why-the-factor-exists)
- [What earns each step](#what-earns-each-step)
- [The trade nobody makes](#the-trade-nobody-makes)
- [HIP](#hip)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The casting factor is the single most consequential number in casting design. It is a divisor applied to the allowable, and at its default value it halves the strength of the material.

It is not a factor of safety. The factor of safety is applied separately and on top.

---

## The ladder

| Factor | Allowable multiplier | Mass penalty | Requirements |
|---|---|---|---|
| **2.00** | 0.500 | 2.00x | **Default. Nothing qualified** |
| **1.33** | 0.752 | 1.33x | Documented process, sample volumetric NDE, one qualification lot |
| **1.00** | 1.000 | 1.00x | Qualified process, 100 % volumetric NDE, three sample lots, SPC |

**The multiplier is `1 / factor`**, so a factor of 2.0 gives half the allowable and a part that needs twice the material.

**The factor multiplies the allowable, then the factor of safety multiplies the load.** An unqualified casting at NASA-STD-5001's ultimate factor of 1.4 therefore carries an effective margin of 2.8 against its material allowable, which is a very conservative structure.

---

## Why the factor exists

**Because a casting's properties are a property of the process, not of the alloy.**

| Source of variability | Effect |
|---|---|
| **Solidification rate varies through the part** | Thick sections have coarser structure and lower properties |
| **Porosity is stochastic** | A pore of unknown size may sit at the critical location |
| **Inclusions are stochastic** | Same |
| **Test coupons are not the part** | A separately cast bar froze differently from the casting |
| Batch to batch variation | Melt practice, mould condition, pour temperature |

**The test coupon problem is the fundamental one.** A wrought material's test coupon is cut from the same plate as the part and it experienced the same processing. A casting's coupon is often cast separately, with a different modulus and a different freezing rate, and it does not represent the part.

**That is why the qualification requirements centre on demonstrating that the process is repeatable** rather than on demonstrating a strength number. The strength number is already in the handbook; what is in doubt is whether this casting has it.

---

## What earns each step

### Factor 1.33

| Requirement | Detail |
|---|---|
| **Documented process** | The parameters written down and controlled |
| **Sample volumetric NDE** | Radiography on a sample of the production |
| **One qualification lot** | Property testing demonstrating the process meets the handbook |

### Factor 1.00

| Requirement | Detail |
|---|---|
| **Qualified process** | Frozen, with change control |
| **100 % volumetric NDE** | Every casting radiographed, to a stated acceptance level |
| **Three sample lots** | Demonstrating consistency, not just capability |
| **Statistical process control** | Ongoing, on the parameters that matter |

**The step from 1.33 to 1.00 is mostly the 100 percent NDE**, and that is a recurring per-part cost rather than a one-off qualification cost. It is the reason many programmes stop at 1.33.

**Three lots rather than one is the other half**, and it is about consistency. A single good lot demonstrates the process can work; three demonstrate that it does.

---

## The trade nobody makes

**Qualifying the process is frequently cheaper than the mass the default factor costs, and the comparison is almost never made.**

The reason is organisational: the qualification cost sits in manufacturing engineering's budget and the mass penalty sits in mass properties' budget, and nobody owns both.

| Quantity | Factor 2.0 | Factor 1.0 |
|---|---|---|
| Allowable | 0.500 x | 1.000 x |
| Part mass | 2.00 x | 1.00 x |
| Qualification cost | 0 | Real, one-off |
| Per-part NDE cost | Low | Real, recurring |

**On a mass-critical vehicle a 50 percent mass saving on a cast component is worth a great deal**, and the qualification is a one-off cost amortised over the programme.

**On a low-rate programme with a small cast component the arithmetic goes the other way**, and factor 2.0 with a heavier part is correct.

**The point is that it is an arithmetic question with an answer**, and [`CastingProcess.selectCastingFactor`](../castingProcessesLibrary/CastingProcess.py) exists to make that answer visible.

---

## HIP

**Hot isostatic pressing is usually a prerequisite for factor 1.0** and it is not sufficient on its own.

| Effect | Detail |
|---|---|
| **Closes internal porosity** | Gas and shrinkage both, by creep under pressure |
| **Does not close surface connected porosity** | No pressure differential across the pore wall |
| **Does not remove inclusions** | They are still there |
| Homogenises | High temperature, long time |
| May coarsen the structure | Check against the alloy's solvus |

**The surface connection limitation is the one that catches people.** A pore that connects to the surface has argon at full pressure on both sides of its wall, so there is no driving force to close it. HIP closes what is interior and leaves what is not.

**HIP does not qualify a process.** It improves a casting, and the qualification requirements are separate and additional.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Default factor | 2.00, halving the allowable |
| Documented process | 1.33 |
| Fully qualified with 100 % NDE | 1.00 |
| The factor is not a factor of safety | Both apply |
| Compare qualification cost against mass cost | Somebody has to own both |
| HIP is necessary and not sufficient | Qualification is separate |
| HIP does not close surface connected porosity | No differential |

---

## Failure modes

**Factor 2.0 accepted by default.** Twice the material, and no comparison made.

**Casting factor confused with factor of safety.** One or the other omitted.

**HIP taken as qualification.** It is not.

**Separately cast test coupons assumed representative.** Different modulus, different properties.

**Process changed after qualification.** The qualification is void.

---

## Worked numbers

From [`CastingProcess.selectCastingFactor`](../castingProcessesLibrary/CastingProcess.py):

| Level | Allowable multiplier | Mass penalty | Mass saving available |
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
| ASTM A1080 | Hot isostatic pressing of steel and stainless |
| ASTM E446 / E186 / E280 | Reference radiographs |
| AS9100 | Quality management |

---

## Tool interface

```python
from CastingProcess import CastingProcess, CASTING_FACTORS

for level in (1.00, 1.33, 2.00):
    casting = CastingProcess()
    casting.setInputs({'process': 'investment', 'alloyFamily': 'stainless',
                       'qualificationLevel': level})
    result = casting.selectCastingFactor()
    print(f'{level:.2f}  allowable x{result["allowableMultiplier"]:.3f}  '
          f'mass {result["massPenalty"]:.2f}x')
    for requirement in result['requirements']:
        print('     ', requirement)
```

---

## References

1. NASA-STD-5001B, *Structural Design and Test Factors of Safety for Spaceflight Hardware*.
2. NASA-STD-6016B, *Standard Materials and Processes Requirements for Spacecraft*.
3. AMS 2175, *Castings, Classification and Inspection of*.
