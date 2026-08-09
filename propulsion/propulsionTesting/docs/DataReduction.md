[Home](../README.md) > Data Reduction

# Data Reduction

## Contents

- [Overview](#overview)
- [The three parameters](#the-three-parameters)
- [The correlation trap](#the-correlation-trap)
- [Which channel dominates](#which-channel-dominates)
- [The throat area, which nobody calls a measurement](#the-throat-area-which-nobody-calls-a-measurement)
- [Efficiency, and whether it was established](#efficiency-and-whether-it-was-established)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A firing produces channels. A result is a number with an uncertainty attached, and getting from one to the other is three lines of algebra and one genuinely easy mistake.

This document is mostly about the mistake, because the algebra is not in dispute and the uncertainty is what decides whether the test answered anything.

---

## The three parameters

```
c*  = Pc * At / mdot
Cf  = F / (Pc * At)
Isp = F / (mdot * g)
```

Each is a product of powers of the measured channels, so the relative uncertainty of each is the root sum of squares of the relative channel uncertainties, weighted by the exponents. All the exponents here are plus or minus one, so the weights are all one and the signs drop out in the squaring.

| Parameter | Depends on |
|---|---|
| c* | Chamber pressure, throat area, mass flow |
| Cf | Thrust, chamber pressure, throat area |
| Isp | **Thrust and mass flow only** |

That last row is the whole of the next section.

---

## The correlation trap

**Chamber pressure and throat area appear in both c\* and Cf, and they appear inverted.** So the two results are not independent, their errors are anti-correlated, and combining them by root sum of squares double-counts the two shared terms.

Worse, the product is algebraically exact:

```
c* * Cf = (Pc At / mdot) * (F / (Pc At)) = F / mdot
```

The shared terms cancel completely. Specific impulse computed that way carries **no chamber pressure or throat area uncertainty at all**.

On the reference booster:

| Route to specific impulse | Value | Uncertainty |
|---|---|---|
| `F / (mdot g)`, direct | 277.02 s | **1.25 %** |
| `c* Cf / g`, uncertainties combined as independent | 277.02 s | **2.02 %** |

Same number to the last digit, **1.61 times the uncertainty**.

This is not a subtle case. It is the default thing to do when a reduction produces c* and Cf and somebody wants an Isp. And a generic uncertainty budget will get it wrong every time, because its interface takes independent contributors and these are not independent.

**This repository owns such a budget class**, `UncertaintyBudget` in [fluidSystemsTesting](../../../fluidSystems/fluidSystemsTesting/docs/UncertaintyAndStatistics.md). It is a good class and it would get this wrong. That is not a defect in it; it is a case its interface cannot express, and it is why [PerformanceReduction](DataReduction.md) is written here rather than assembled from it.

**Never compute Isp as c\* times Cf and propagate the two uncertainties independently. Compute it from thrust and mass flow, which is both simpler and correct.**

---

## Which channel dominates

Representative development stand figures, and the ordering is more stable across installations than the values are.

| Channel | Relative | Share of c* variance |
|---|---|---|
| Chamber pressure | 0.50 % | 11 % |
| Throat area | 1.00 % | 44 % |
| Mass flow | 1.00 % | 44 % |

**No single channel dominates**, which is the case where a budget is worth building rather than guessing. The throat area and the mass flow carry equal weight, so improving either one alone leaves the other in place:

| Instrumentation | u(c*) |
|---|---|
| As tested | 1.50 % |
| Throat area improved to 0.3 % | 1.16 % |
| Mass flow improved to 0.3 % | 1.16 % |
| **Both improved** | **0.66 %** |

Two-thirds of a percentage point of improvement requires improving both. That is a useful thing to know before authorising one of them.

---

## The throat area, which nobody calls a measurement

It is the only entry in that table that does not have an instrument attached to it, and it is tied for the largest.

It comes from a cold diameter, checked once, before the test. It is doubled going into the area because area goes as diameter squared, so a 0.5 per cent diameter measurement is a 1 per cent area. And **it does not include the throat eroding during the firing**, which is not measured at all and is not in the budget.

For an ablative or a graphite throat that omission is not small. For a copper throat it is smaller and it is still an omission rather than a zero.

---

## Efficiency, and whether it was established

A c* efficiency quoted without the uncertainty of the measurement behind it is a number rather than a result.

On the reference booster the measured c* is 1751.4 m/s against an ideal of 1823, giving an efficiency of **0.9607** and a shortfall of 3.93 per cent. The measurement carries 1.50 per cent.

**So the shortfall is real and it is established at a ratio of 2.6.** That is enough to say the injector loses about four per cent and not enough to say whether it loses three or five. See [CampaignStructure](CampaignStructure.md) for what follows from that.

The comparison is only valid against an ideal computed at the same chamber pressure and mixture ratio as the test point. Comparing against a different point is the most common way an efficiency is overstated, and [PerformanceReduction](DataReduction.md) raises rather than warns if the ideal values are not supplied.

---

## Worked numbers

The 100 kN booster, treating the hub's design point as recorded channels.

| Quantity | Value |
|---|---|
| Characteristic velocity | 1751.4 m/s, 1.50 % |
| Thrust coefficient | 1.5511, 1.35 % |
| Specific impulse | 277.02 s, **1.25 %** |
| Specific impulse, naive combination | 277.02 s, 2.02 % |
| Inflation from the naive route | **1.61x** |
| c* efficiency | 0.9607 |
| Shortfall against ideal | 3.93 % |

---

## Design rules of thumb

- **Compute Isp from thrust and mass flow.** Never from c* times Cf with independent uncertainties.
- **Build the budget before the test**, not after. It decides whether the test is worth running.
- **Quote the uncertainty with the efficiency**, every time. Without it the efficiency is not a result.
- **Improve channels in pairs when they carry equal weight.** One at a time buys almost nothing.
- **Put the throat area in the budget.** It is tied for the largest term and it is the one nobody lists.

---

## Failure modes

**Isp from c* times Cf with combined uncertainties.** Inflates by a factor of 1.6 on this engine, and it is the default thing to do.

**An efficiency quoted without an uncertainty.** Not a result.

**Comparing against an ideal at a different chamber pressure or mixture ratio.** The most common way an efficiency is overstated.

**Throat area treated as exact.** It is tied for the largest term in the c* budget.

**Throat erosion omitted.** Not in the budget at all, and not small for an ablative throat.

**Improving one channel and expecting the budget to move.** It will not, if another carries equal weight.

---

## Tool interface

```python
from PerformanceReduction import PerformanceReduction

reduction = PerformanceReduction()
reduction.setInputs({'chamberPressure': 10.0e6,
                     'throatArea':      6.446e-3,
                     'massFlow':        36.81,
                     'thrust':          100.0e3})

reduced     = reduction.reduce()
uncertainty = reduction.calculateUncertainty()
efficiency  = reduction.compareEfficiency(idealCstar = 1823.0,
                                          idealThrustCoefficient = 1.6146)

print(reduction.generateReport())
```

Channel uncertainties default to the representative development stand figures in `INSTRUMENT_UNCERTAINTY` and should be replaced with the calibration certificates for a real budget.

---

## References

- Sutton and Biblarz, *Rocket Propulsion Elements*, the performance parameter definitions
- ISO/IEC Guide 98-3, *Guide to the expression of uncertainty in measurement*, for the propagation rule
- [fluidSystemsTesting UncertaintyAndStatistics](../../../fluidSystems/fluidSystemsTesting/docs/UncertaintyAndStatistics.md), for the general budget method this document departs from and why
