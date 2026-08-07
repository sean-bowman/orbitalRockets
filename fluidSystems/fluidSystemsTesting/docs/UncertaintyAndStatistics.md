[Home](../README.md) > Uncertainty and Statistics

# Uncertainty and Statistics

## Contents

- [Overview](#overview)
- [The GUM method](#the-gum-method)
- [Type A and Type B](#type-a-and-type-b)
- [Distributions and divisors](#distributions-and-divisors)
- [The dominant contributor](#the-dominant-contributor)
- [Reliability demonstration](#reliability-demonstration)
- [Testing longer instead of testing more](#testing-longer-instead-of-testing-more)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Two separate statistical questions, often confused.

**Measurement uncertainty** asks: how well do we know the number this test produced? Answered by a GUM uncertainty budget.

**Reliability demonstration** asks: how confident are we that the population behaves like the units we tested? Answered by sample size analysis.

A result with a tight measurement uncertainty from a sample of one tells you the number precisely and tells you nothing about the population.

---

## The GUM method

1. Write the measurement equation, `y = f(x1, x2, ... xn)`
2. Estimate the standard uncertainty `u(xi)` of each input from its distribution
3. Compute the sensitivity coefficient `ci = dy/dxi`, analytically or numerically
4. Combine: `uc(y) = sqrt( sum( (ci * u(xi))^2 ) )`
5. Expand: `U = k * uc(y)`, with `k = 2` for approximately 95 percent coverage

**Report as** `y = value +/- U (k = 2)`. A result reported without the coverage factor is ambiguous by a factor of two.

**The combination assumes independence.** Correlated contributors need a covariance term, and the practical response is to combine them into a single term rather than estimate a correlation coefficient nobody can defend.

---

## Type A and Type B

**This distinction is about how the uncertainty was evaluated, not about what kind it is.**

| Type | Evaluated by | Example |
|---|---|---|
| **A** | Statistical analysis of repeated observations | Standard deviation of ten runs |
| **B** | Everything else | Calibration certificate, manufacturer specification, engineering judgement |

Both are standard uncertainties. Both combine identically. The distinction exists for traceability and for reporting, not for the arithmetic, and treating Type B as somehow less rigorous is a misreading of the method.

---

## Distributions and divisors

Converting a stated half-width into a standard uncertainty requires knowing the distribution, and **this is where most budgets go wrong, always in the unconservative direction.**

| Distribution | Divisor | When |
|---|---|---|
| Normal, k = 1 | 1 | Already a standard uncertainty |
| **Normal, k = 2** | **2** | A calibration certificate at 95 percent coverage |
| Normal, k = 3 | 3 | A certificate at 99.7 percent |
| **Rectangular** | **sqrt(3) = 1.732** | **A tolerance band with no distribution stated** |
| Triangular | sqrt(6) = 2.449 | A tolerance where the centre is more likely |
| U-shaped | sqrt(2) = 1.414 | A cyclic effect, such as temperature control oscillation |

**A manufacturer tolerance with no distribution stated is rectangular.** Treating its half-width as a standard uncertainty overstates confidence by a factor of 1.73, and it is the single most common error in an uncertainty budget.

**Conversely, do not divide a calibration certificate's stated k = 2 value by sqrt(3).** That is over-conservative and it is the opposite error, which happens less often but does happen.

---

## The dominant contributor

The most actionable output of a budget.

**Because contributors combine in quadrature, a term at half the magnitude of the largest contributes only a quarter of the variance.** If one term is 80 percent of the combined variance, improving anything else is wasted effort.

The [`UncertaintyBudget`](../fluidSystemsTestingLibrary/UncertaintyBudget.py) class sorts by variance share and flags a term above 50 percent, because that is the number that tells you where to spend money.

**Example:** a Cv measurement dominated by the pressure transducer at 39 percent of the variance. Buying a better flow meter changes nothing; buying a better transducer, or using a lower-range one, changes everything.

---

## Reliability demonstration

**The success-run formula.** Testing `n` units with zero failures demonstrates reliability `R` at confidence `C`:

```
n = ln(1 - C) / ln(R)
```

It follows from requiring `R^n <= 1 - C`: the probability of observing `n` consecutive successes from a population with true reliability `R` is at most `1 - C`.

**The consequences are brutal:**

| Requirement | Units, zero failures | Practical |
|---|---|---|
| R = 0.90 at 50 % | 7 | Yes |
| R = 0.90 at 90 % | 22 | Marginal |
| R = 0.95 at 90 % | 45 | No |
| **R = 0.99 at 90 %** | **230** | **No** |
| R = 0.99 at 95 % | 299 | No |
| R = 0.999 at 95 % | 2995 | No |

**Nobody builds 2995 flight valves.** High reliability is never demonstrated by test alone. It is argued from test plus analysis plus heritage plus process control, with the test contributing a bound rather than the number.

**The reverse calculation is the honest one:**

```
R = (1 - C)^(1/n)
```

Three units passing demonstrates `R = 0.464` at 90 percent confidence. That is a real number and it is usually far weaker than the requirement it is being used to close. Knowing the gap during planning is what lets the argument be constructed deliberately instead of assembled in a panic at the readiness review.

**Allowing failures makes it worse.** One permitted failure raises the sample size substantially, which is why qualification programmes specify zero failures and treat any failure as a stop-and-investigate rather than a budgeted allowance.

---

## Testing longer instead of testing more

For a wear-out failure mechanism following a Weibull distribution with shape parameter `beta`:

```
n = ln(1 - C) / ( ratio^beta * ln(R) )
```

where `ratio` is the test duration as a multiple of the required life.

**This only works when beta is greater than 1**, meaning the mechanism is wear-out. For `beta = 1` the failures are random and memoryless, extra duration buys exactly nothing, and the expression collapses to the success-run result.

The trade is genuinely useful for seals, bearings and anything with a wear mechanism. It is precisely wrong for anything whose failures are random, and applying it without establishing `beta` from data is a common and expensive error.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Report with the coverage factor | `y +/- U (k = 2)` |
| Bare tolerance is rectangular | Divide by sqrt(3) |
| Calibration certificate at 95 % | Divide by 2, not sqrt(3) |
| Attack the dominant contributor | Quadrature means the rest barely matters |
| Success run | `n = ln(1-C)/ln(R)` |
| R = 0.99 at 90 % | 230 units. Plan the argument, not the test |
| Reverse calculation is the honest statement | 3 units gives R = 0.46 |
| Zero failures in a qualification plan | Any failure is a stop-and-investigate |
| Weibull duration trade needs beta > 1 | And beta from data, not assumed |

---

## Failure modes

**A rectangular tolerance treated as a standard uncertainty.** Confidence overstated by 1.73x.

**A calibration certificate divided by sqrt(3).** Over-conservative, the opposite error.

**Correlated contributors combined as independent.** Understates the combined uncertainty.

**Effort spent on a minor contributor.** Quadrature means it barely moves the result.

**A reliability requirement with no demonstration plan.** Discovered when someone asks how R = 0.99 will be shown.

**The reverse calculation never done.** Nobody knows what the campaign actually demonstrates.

**Weibull duration trade applied to a random failure mechanism.** Extra duration bought nothing and the sample size was reduced on the strength of it.

**Uncertainty reported without a coverage factor.** Ambiguous by a factor of two.

---

## Worked example

From [`codeInterface.py`](../codeInterface.py), the Cv measurement:

| Contributor | Type | Half width | Distribution | u(xi) | Share |
|---|---|---|---|---|---|
| Pressure transducer | B | 0.0052 | normal k=2 | 0.00260 | **39 %** |
| Flow meter calibration | B | 0.0035 | normal k=2 | 0.00175 | 18 % |
| Temperature effect | B | 0.0028 | rectangular | 0.00162 | 15 % |
| Fluid density | B | 0.0021 | rectangular | 0.00121 | 9 % |
| Repeatability | A | 0.0019 | normal k=1 | 0.00190 | 21 % |

| Result | Value |
|---|---|
| Combined uncertainty | 0.00418 |
| Coverage factor | k = 2 |
| **Expanded uncertainty** | **0.00836** |
| Result | Cv = 0.348 +/- 0.0084 (k = 2) |
| Relative | 2.41 % |
| **Dominant** | **Pressure transducer, 39 %** |

The transducer is on a 5 MPa range measuring a 50 kPa differential, which is why it dominates. A differential transducer on a 100 kPa range would cut the dominant term by a factor of fifty and the total uncertainty by nearly half, and no other change on the stand comes close to that.

And the reliability side:

| Quantity | Value |
|---|---|
| Requirement | R = 0.99 at 90 % confidence |
| Units needed, zero failures | 230 |
| Units available | 3 |
| **Demonstrated** | **R = 0.4642** |

---

## Standards

| Standard | Scope |
|---|---|
| **ISO/IEC Guide 98-3 (GUM)** | Uncertainty of measurement |
| **AIAA S-071** | Assessment of experimental uncertainty |
| ASME PTC 19.1 | Test uncertainty |
| NIST Technical Note 1297 | Guidelines for evaluating and expressing uncertainty |
| ISO 16269-6 | Statistical interpretation of data, statistical tolerance intervals |
| MIL-HDBK-17 / CMH-17 | Composite materials handbook, A-basis and B-basis methodology |
| MMPDS | Metallic materials properties, allowables methodology |
| IEC 61710 | Power law model, goodness-of-fit tests and estimation |

---

## Tool interface

```python
from UncertaintyBudget import UncertaintyBudget
from SampleSize import SampleSize

budget = UncertaintyBudget()
budget.setInputs({'measurand': 'Cv', 'measurandValue': 0.348, 'measurandUnit': '-'})
budget.addContributor('pressure transducer', 0.0052, 'normal k=2', evaluationType = 'B')
budget.addContributor('repeatability',       0.0019, 'normal k=1', evaluationType = 'A')
result = budget.calculate()
print(result['dominantContributor'], result['dominantShare'])

sample = SampleSize()
sample.setInputs({'targetReliability': 0.99, 'confidenceLevel': 0.90, 'availableArticles': 3})
sample.calculateSuccessRun()      # 230 units
sample.calculateDemonstrated()    # R = 0.4642 from 3
print(sample.compareRequirements())   # the cost of each common requirement
```

---

## References

1. ISO/IEC Guide 98-3:2008, *Uncertainty of Measurement -- Part 3: Guide to the Expression of Uncertainty in Measurement (GUM)*.
2. AIAA S-071A-1999, *Assessment of Experimental Uncertainty with Application to Wind Tunnel Testing*.
3. NIST Technical Note 1297, *Guidelines for Evaluating and Expressing the Uncertainty of NIST Measurement Results*.
4. Nelson, W., *Accelerated Testing*, Wiley, 2004.
5. Meeker, W. Q. and Escobar, L. A., *Statistical Methods for Reliability Data*, 2nd ed., Wiley, 2021.
