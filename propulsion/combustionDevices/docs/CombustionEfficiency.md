[Home](../README.md) > Combustion Efficiency

# Combustion Efficiency

## Contents

- [Overview](#overview)
- [What c* efficiency is, and is not](#what-c-efficiency-is-and-is-not)
- [Where the loss comes from](#where-the-loss-comes-from)
- [Measuring it](#measuring-it)
- [What real engines achieve](#what-real-engines-achieve)
- [The film cooling debit](#the-film-cooling-debit)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [What is not validated](#what-is-not-validated)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Combustion efficiency is the fraction of the ideal characteristic velocity an engine actually delivers. It is the injector's number, it is measurable without a thrust stand, and it is the first thing to look at when an engine underperforms.

The [propulsion hub](../../docs/PerformanceFundamentals.md) covers why the `Cf` and `c*` split is a diagnostic. This document is about the `c*` half specifically: what causes the shortfall and what can be done about it.

---

## What c* efficiency is, and is not

```
eta_c* = c*_measured / c*_ideal        c*_measured = Pc At / mdot
```

**It contains everything upstream of the throat and nothing downstream of it.** Injector, mixing, atomisation, vaporisation, residence time, completeness of reaction, and heat lost to the wall.

It is **not** a measure of how good the combustion chemistry is. The chemistry is what CEA computes and it is essentially always complete given enough time and mixing. What `eta_c*` measures is whether the injector delivered the conditions the chemistry needed, in the volume available.

**A subtlety that catches people:** the ideal `c*` you divide by has to be at the same mixture ratio and chamber pressure. Comparing a measured value against a tabulated ideal taken at a different condition produces an efficiency that is partly a condition mismatch. This library carries two ideal values that differ by up to 4.3 per cent for exactly that class of reason, and reports the gap rather than hiding it.

---

## Where the loss comes from

Roughly in order of size on a typical engine.

**Incomplete mixing.** Propellant that reaches the throat at a local mixture ratio far from nominal has not released its full energy. This is the dominant term and it is what element design addresses.

**Incomplete vaporisation.** A drop that has not evaporated has not burnt. Scales with the orifice diameter, which is why there is an upper bound on element size.

**Residence time.** If the chamber is shorter than the reaction needs, some fraction leaves unburnt. This is the term `L*` exists to bound, and on a chamber built at or above its `L*` it is usually small.

**Heat loss to the wall.** Real and usually a fraction of a per cent. On the worked example chamber it is 8.13 MW against roughly 229 MW of thermal power, which is 3.6 per cent of the energy release, though not all of that shows up as a `c*` debit because much of it is returned by the regenerative circuit.

**Film cooling.** Deliberate, and covered below.

---

## Measuring it

```
c* = Pc At / mdot
```

Every term is instrumented on a test stand: a chamber pressure tap, a throat diameter measured before the test, and a flow measurement on each propellant.

**No thrust measurement is required**, which is what makes it the diagnostic. A thrust stand is expensive, it needs calibration, and its reading is confounded by the nozzle. `c*` needs none of that.

Two practical cautions.

**The throat erodes.** On an ablative chamber, and to a lesser extent on any chamber, the throat area at the end of the burn is not the area at the start. An efficiency computed on the pre-test dimension drifts through the burn.

**Chamber pressure is measured somewhere specific.** The static pressure at the injector face is not the stagnation pressure at the throat, and on a low contraction ratio chamber the difference is a real fraction of a per cent. The measurement station has to be stated with the number.

---

## What real engines achieve

| Engine class | Typical `eta_c*` |
|---|---|
| Well developed | 0.96 to 0.98 |
| Best in class | 0.99 and above |
| Early development | 0.90 to 0.94 |

The library defaults to **0.96**, described as what a well developed engine achieves.

**Validation against RS-25 says that default is conservative for a best-in-class engine.** The published vacuum impulse of 452.3 s against the library's ideal 459.8 s implies a combined efficiency of **0.984** across both `c*` and `Cf` together, which is above the library's combined default of 0.941.

The default was **not changed to match**, and the reasoning is worth recording. RS-25 is the highest performing liquid engine ever flown, and a default that assumed its performance would flatter every other engine that used the library. The gap is recorded and tested instead. See [ValidationReferences](ValidationReferences.md).

---

## The film cooling debit

Film cooling diverts fuel to the wall, where it burns at a mixture ratio chosen for wall temperature rather than for impulse, and some of it does not burn at all.

**The debit is not the film fraction.** That is the single most common overstatement in this subject and this library made it before correction. Film propellant partly burns and partly mixes back into the core, so the loss is a fraction of the diverted flow: commonly quoted as **0.3 to 0.5 times the film fraction**.

At the worked example's 8 per cent film fraction, that is a **2.4 to 4.0 per cent** `c*` debit rather than 8 per cent, which is a factor of two to three in a number that decides whether a design is acceptable.

**That multiplier is an estimate and is reported as a range for that reason.** No single source was found for it. A number quoted as a range is honest about what it is.

---

## Design rules of thumb

- **Measure `c*` before touching anything.** It needs no thrust stand and it halves the problem.
- **State the chamber pressure measurement station** with any efficiency figure.
- **Use the pre-test throat area and note the erosion**, or measure after as well.
- **Compare against an ideal at the same mixture ratio and pressure.**
- **Do not use the library defaults for a best-in-class engine.** They are conservative by about four points.
- **Cost film cooling at 0.3 to 0.5 of the diverted flow.**
- **Expect the injector to be developed by test.** Mixing is the dominant loss and it is not predictable to the accuracy that matters.

---

## Failure modes

**Efficiency computed against an ideal at the wrong condition.** Part of the answer is a condition mismatch rather than a loss.

**Throat erosion ignored.** The efficiency drifts through the burn and the drift is read as a combustion change.

**Chamber pressure station unstated.** A fraction of a per cent, which matters when the quantity of interest is a few per cent.

**Film debit taken as the film fraction.** Overstates by two to three times.

**A combined Isp efficiency used to diagnose.** It cannot be inverted into a cause. See [PerformanceFundamentals](../../docs/PerformanceFundamentals.md).

---

## Worked numbers

| Quantity | Value |
|---|---|
| Library default `eta_c*` | 0.96 |
| Library default `eta_Cf` | 0.98 |
| Library combined default | 0.941 |
| RS-25 implied combined, from published data | 0.984 |
| Gap | 4.3 points, conservative |
| Film debit at 8 per cent film fraction | 2.4 to 4.0 % |
| Worked example wall heat load | 8.13 MW |
| As a fraction of thermal power | 3.6 % |

---

## What is not validated

**The film cooling debit multiplier.** Registered with what would close it: hot fire data relating measured `c*` efficiency to film fraction on a single chamber.

**The element mixing quality figures** in `INJECTOR_ELEMENTS`. A ranking rather than a measurement, and they must not be used to predict an efficiency.

Both are in [validation/referenceCases.py](../../../validation/referenceCases.py).

---

## Standards

| Standard | What it gives you |
|---|---|
| **CPIA 246** | **Liquid rocket engine performance prediction and evaluation.** The JANNAF methodology |
| CPIA 178 | Performance test data acquisition and interpretation |
| NASA RP-1311 | CEA, which supplies the ideal to divide by |
| NASA SP-8089 | Injectors |

**The JANNAF methodology is what fixes what is included in a delivered efficiency and what is not**, which is the whole difficulty in quoting one.

---

## Tool interface

The efficiencies are inputs to the [propulsion hub](../../docs/PerformanceFundamentals.md) rather than outputs of this sub-domain, because they are measured rather than predicted.

```python
import sys
sys.path.insert(0, '../propulsionLibrary')    # from the sub-domain directory

from EnginePerformance import EnginePerformance

performance = EnginePerformance()
performance.setInputs({'combination':                 'LOX/RP-1',
                       'chamberPressure':             10.0e6,
                       'areaRatio':                   20.35,
                       'cstarEfficiency':             0.96,
                       'thrustCoefficientEfficiency': 0.98})

cstar = performance.calculateCharacteristicVelocity()
print(cstar['ideal'], cstar['delivered'])
```

---

## References

- CPIA 246, *Liquid rocket engine performance prediction and evaluation*
- NASA SP-8089, *Liquid rocket engine injectors*
- Gordon and McBride, NASA RP-1311, *CEA*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- Yang, Habiballah, Hulka and Popp, *Liquid Rocket Thrust Chambers*
