[Home](../README.md) > Loads and Load Cases

# Loads and Load Cases

## Contents

- [Overview](#overview)
- [The load sources](#the-load-sources)
- [Why the governing case is not the largest load](#why-the-governing-case-is-not-the-largest-load)
- [The factor ladder](#the-factor-ladder)
- [Factors multiply the load](#factors-multiply-the-load)
- [Enveloping against combining](#enveloping-against-combining)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Everything downstream depends on getting the load cases right, and the commonest structural error is not a bad calculation but a case that was never run.

---

## The load sources

| Phase | Axial | Lateral | Other |
|---|---|---|---|
| **Ground handling** | 1 g | 0.5 g | **Unpressurized.** Crane, transport, erection |
| **Liftoff** | 3 g | 1 g | Acoustic, transient, hold-down release |
| **Max-Q** | 2.5 g | 2 g | **Highest bending.** Aerodynamic, gust, buffet |
| **Max acceleration** | **6 g** | 0.3 g | End of first stage burn, lowest mass |
| **Staging** | 0.5 g | 0.5 g | Shock, separation transient |
| Entry | 4 g | 1.5 g | Reusable stages, plus heating |

**Ground handling is the case most often skipped** and it is the only one with no internal pressure, which makes it the governing stability case for a pressure-stabilized structure.

**Max acceleration has the highest axial load** because the stage is nearly empty at the end of its burn, so the same thrust produces the highest acceleration.

**Max-Q has the highest bending** and only moderate axial load. Neither case bounds the other.

---

## Why the governing case is not the largest load

**Because structures fail under combinations, and the combination is not maximised by any single component.**

From the worked example:

| Case | Axial | Lateral | p_int | Severity |
|---|---|---|---|---|
| ground handling | 1.0 g | 0.5 g | 0 | 0.286 |
| liftoff | 3.0 g | 1.0 g | 2.236 MPa | 1.409 |
| **max-Q** | 2.5 g | **2.2 g** | 2.236 MPa | **2.174** |
| max acceleration | **6.0 g** | 0.3 g | 1.800 MPa | 1.552 |
| staging | 0.5 g | 0.6 g | 1.500 MPa | 0.795 |

**Max acceleration is the largest in axial load. Max-Q is the worst case overall.** The two disagree, and a structure sized on axial load alone is sized for the wrong condition.

**The severity index is a screening tool, not an answer.** It sums each component normalised by its maximum across the set, which finds candidates worth analysing properly. The real answer comes from running each case through the actual failure criteria.

---

## The factor ladder

| Level | Factor | Against |
|---|---|---|
| **Limit** | 1.00 | The maximum expected during the mission |
| **Yield** | **1.10** | Must not yield |
| **Ultimate** | **1.40** | Must not rupture |

**Those are for a structure qualified by test.** Without a qualification test article the factors rise substantially:

| Level | By test | By analysis alone |
|---|---|---|
| Yield | 1.10 | **1.60** |
| Ultimate | 1.40 | **2.00** |

**A model uncertainty factor multiplies on top** where the loads themselves come from a model rather than from flight or test measurement. It is 1.0 for well validated loads and rises where they are not.

**Separation of a preloaded joint carries its own factor**, typically 1.20, because separation is a discontinuity in behaviour rather than a stress limit. See [BoltedJoints.md](BoltedJoints.md).

---

## Factors multiply the load

**Not the allowable, and the distinction is not pedantic.**

For a linear response the two are equivalent. For a nonlinear one they are not, and buckling under combined load is nonlinear:

```
R_axial + R_bending + R_shear^2 <= 1
```

**The shear term is quadratic**, so multiplying the loads by 1.4 and multiplying the allowables by 1/1.4 give different answers. Factoring the allowable is unconservative wherever the interaction is superlinear.

**The g level is an input describing the environment and is not factored.** Only the resulting load is. A report showing a factored g level is self-contradictory, and the class deliberately leaves the g values untouched.

---

## Enveloping against combining

| Approach | What it does |
|---|---|
| **Enveloping** | Take the maximum of each component across all cases and apply them together |
| **Combining** | Analyse each case as it actually occurs |

**Enveloping is conservative and it is not free.** It sizes against a condition that never occurs, and worse, it hides which phase actually drives the structure. An engineer looking at an enveloped case cannot tell what to change to reduce the mass.

**Combining requires more analysis and gives an answer you can act on.** If max-Q governs, reducing the gust response or the trajectory's angle of attack buys mass. An envelope tells you nothing of the sort.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Yield 1.10, ultimate 1.40 | Qualified by test |
| Yield 1.60, ultimate 2.00 | By analysis alone |
| Separation factor | 1.20, its own requirement |
| Factors multiply the load | Not the allowable |
| Do not factor the g level | It is an environment, not a load |
| Combine, do not envelope | An envelope hides the driver |
| Run ground handling unpressurized | It governs stabilized structure |
| The largest load is rarely the governing case | |

---

## Failure modes

**Ground handling skipped.** The only unpressurized case, and it governs stability.

**Cases enveloped.** Sized for a condition that never occurs, and the driver is hidden.

**Factors applied to the allowable.** Unconservative where the interaction is superlinear.

**Already-factored loads combined.** Double counting.

**Model uncertainty omitted for unvalidated loads.** The factor exists for a reason.

**Analysis-only qualification run at test factors.** 1.40 where 2.00 was required.

---

## Worked numbers

From [`LoadCase`](../aerospaceStructuresLibrary/LoadCase.py) on the worked example:

| Quantity | Result |
|---|---|
| Governing by axial load | **max acceleration** |
| Governing by combined severity | **max-Q** |
| They agree | **No** |
| Yield factor | 1.10 |
| Ultimate factor | 1.40 |

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-5001** | Structural design and test factors of safety |
| NASA-STD-5002 | Load analyses of spacecraft and payloads |
| NASA-STD-5020 | Threaded fastening systems, separation factors |
| ECSS-E-ST-32 | Structural general requirements |
| SMC-S-016 | Test requirements for launch, upper stage and space vehicles |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'aerospaceStructuresLibrary')

from LoadCase import LoadCase

cases = LoadCase()
cases.setInputs({'referenceMass': 4200.0, 'referenceLength': 6.0,
                 'qualificationBy': 'test'})
cases.addCase('liftoff',   axialG = 3.0, lateralG = 1.0, internalPressure = 2.236e6)
cases.addCase('max-Q',     axialG = 2.5, lateralG = 2.2, internalPressure = 2.236e6,
              dynamicPressure = 35.0e3)
cases.addCase('max accel', axialG = 6.0, lateralG = 0.3, internalPressure = 1.8e6)

result = cases.identifyGoverning()
for finding in result['findings']:
    print(finding)
```

---

## References

1. NASA-STD-5001B, *Structural Design and Test Factors of Safety for Spaceflight Hardware*.
2. NASA-STD-5002A, *Load Analyses of Spacecraft and Payloads*.
3. Wijker, J. J., *Spacecraft Structures*, Springer, 2008.
