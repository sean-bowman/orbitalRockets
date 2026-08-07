[Home](../README.md) > Qualification

# Qualification

## Contents

- [Overview](#overview)
- [The casting factor](#the-casting-factor)
- [What qualification requires](#what-qualification-requires)
- [Lot acceptance](#lot-acceptance)
- [Process control](#process-control)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A centrifugal casting is qualified as a casting, under the same casting factor ladder that governs every other casting route. The process-specific additions are the speed record and the segregated layer verification.

The full treatment of the casting factor is in [castingProcesses](../../castingProcesses/docs/CastingFactorAndQualification.md). This document covers what is specific here.

---

## The casting factor

| Factor | Allowable multiplier | Requirements |
|---|---|---|
| **2.00** | 0.50 | Default. Nothing qualified |
| **1.33** | 0.752 | Documented process, sample volumetric NDE, one qualification lot |
| **1.00** | 1.00 | Qualified process, 100 % volumetric NDE, three sample lots, SPC |

**A factor of 2.0 halves the allowable**, which means twice the material for the same load. **That is almost always more expensive than qualifying the process would have been**, and the comparison is rarely made because the two costs sit in different budgets.

**Centrifugal castings are good candidates for a factor of 1.0** because the geometry is simple, the wall is uniform, radiography works well, and the process has few variables. Qualifying a centrifugal casting process is easier than qualifying an investment casting one.

---

## What qualification requires

| Element | Detail |
|---|---|
| **Frozen process** | Alloy, melt practice, speed, pour temperature, pour rate, mould, coating |
| **100 % volumetric NDE** | Radiography, to a stated reference radiograph level |
| **Three sample lots** | Demonstrating property consistency |
| **Property testing** | Tensile from prolongations or sacrificial castings, at defined locations |
| **Statistical process control** | On the parameters that matter |

**Process-specific additions for centrifugal casting:**

| Element | Why |
|---|---|
| **Rotational speed record** | It is the governing parameter |
| **Pour temperature record** | It sets the superheat and the viscosity |
| **Coating thickness control** | It sets the solidification time |
| **Segregated layer verification** | On a sectioned first article, confirming the machining allowance |

**The segregated layer verification is the one nobody else does**, and it is the direct confirmation that the process delivered its benefit. Section a first article, measure the inclusion distribution across the wall, and confirm the allowance removes it.

---

## Lot acceptance

| Test | Frequency |
|---|---|
| Chemical analysis | Per heat |
| **Tensile** | Per lot, from a prolongation or a sacrificial casting |
| Radiography | Per casting, at factor 1.0 |
| Penetrant | Per casting, after machining |
| Wall thickness map | Per casting |
| Hardness | Per casting, as a fast heat treat check |

**Test location matters and it has to be specified.** Properties vary through the wall, because the outer material solidified fast against the mould and the inner material slowly. A specimen taken from the outer third is not representative of the whole wall.

**Prolongations are the usual answer**: extra length cast on the end, from the same pour, sectioned for test specimens.

---

## Process control

| Parameter | Control |
|---|---|
| **Rotational speed** | Recorded every casting |
| **Pour temperature** | Measured and recorded |
| Pour rate and traverse | Controlled, and recorded on an instrumented machine |
| Mould preheat | Measured |
| **Coating thickness** | Controlled and periodically measured |
| Melt cleanliness | Per heat, by inclusion count or a filtration check |

**Coating thickness is the parameter most often uncontrolled** and it directly sets the solidification time, which sets the structure and the capture number. A mould re-coated more heavily produces a different casting with no parameter having formally changed.

**Melt cleanliness is worth measuring** because the process relocates contamination rather than removing it. A dirty heat gives a casting with a thicker segregated layer, and if the allowance was set on a clean heat the contamination stays in the part.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Factor 2.0 halves the allowable | Qualify the process instead |
| Centrifugal is an easy process to qualify | Simple geometry, few variables |
| Record the speed every casting | It is the governing parameter |
| Control the coating thickness | It sets the solidification time |
| Section a first article | Confirm the segregated layer |
| Specify the test specimen location | Properties vary through the wall |
| Measure melt cleanliness | The process relocates, it does not remove |

---

## Failure modes

**Factor 2.0 accepted without comparing against the qualification cost.** Twice the material.

**Coating thickness uncontrolled.** A different casting with no parameter change.

**Test specimens from the outer third.** Not representative.

**Segregated layer never verified.** The allowance is a model output.

**Dirty heat accepted.** More contamination, same allowance, contamination retained.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-5001** | Structural design and test factors, including casting factors |
| NASA-STD-6016 | Materials and processes requirements |
| **ASTM A451 / A426 / A660** | Centrifugally cast pipe, including test requirements |
| ASTM E446 / E186 / E280 | Reference radiographs |
| AMS 2175 | Castings, classification and inspection |
| ASTM E45 | Inclusion content of steel |
| AS9100 | Quality management |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../castingProcesses/castingProcessesLibrary')

from CastingProcess import CastingProcess, CASTING_FACTORS

for level in (1.00, 1.33, 2.00):
    casting = CastingProcess()
    casting.setInputs({'process': 'centrifugal cast' if False else 'investment',
                       'alloyFamily': 'stainless', 'qualificationLevel': level})
    result = casting.selectCastingFactor()
    print(f'{level:.2f}: allowable x{result["allowableMultiplier"]:.3f}, '
          f'mass penalty {result["massPenalty"]:.2f}x')
```

---

## References

1. NASA-STD-5001B, *Structural Design and Test Factors of Safety for Spaceflight Hardware*.
2. NASA-STD-6016B, *Standard Materials and Processes Requirements for Spacecraft*.
3. ASTM A451, *Standard Specification for Centrifugally Cast Austenitic Steel Pipe*.
