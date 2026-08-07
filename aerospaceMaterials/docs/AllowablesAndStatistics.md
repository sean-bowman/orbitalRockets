[Home](../README.md) > Allowables and Statistics

# Allowables and Statistics

## Contents

- [Overview](#overview)
- [The three bases](#the-three-bases)
- [The tolerance limit](#the-tolerance-limit)
- [The k-factor](#the-k-factor)
- [What the sample size costs](#what-the-sample-size-costs)
- [Batches, and why pooling overstates the allowable](#batches-and-why-pooling-overstates-the-allowable)
- [The non-parametric alternative](#the-non-parametric-alternative)
- [Knockdowns](#knockdowns)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A material property measured on twenty specimens produces twenty numbers. A design needs one, and the one it needs is not the average.

The design value has to be a statement about the whole population with a stated confidence, because the part that flies was not one of the twenty tested. That statement is a **one-sided lower tolerance limit**, and computing it correctly is the core statistical content of this domain.

---

## The three bases

| Basis | Exceedance | Confidence | Required when |
|---|---|---|---|
| **A** | 99 % of the population | 95 % | Single load path: failure of one element causes loss of structural integrity |
| **B** | 90 % of the population | 95 % | Redundant structure that can redistribute load |
| **S** | Not statistical | -- | A specification guaranteed minimum |

**S-basis is not a weaker version of A-basis; it is a different kind of statement.** A specification minimum is a value every lot is required to meet, enforced by lot acceptance testing. It is often more conservative than a computed A-basis would be, and it comes with no information about the distribution.

**The load path decides, not the designer.** A pressure vessel wall cannot redistribute load around a failure, so it is single load path and takes A-basis. That is why the helium bottle in the worked example pays for A-basis and why the cost of doing so shows up directly in the wall thickness.

---

## The tolerance limit

For a normally distributed property:

```
T = mean - k * s
```

with `s` the sample standard deviation on `n - 1` degrees of freedom, and `k` the one-sided tolerance factor for the required basis and sample size.

The entire content of the method is in `k`. It has to account for two separate uncertainties at once: how far into the tail the required exceedance sits, and how badly the sample mean and standard deviation might misrepresent the population.

**For a lognormal property**, the same calculation is performed on the logarithms and exponentiated back. For metallic strength this is rarely the right model; a lognormal fit that beats a normal fit on metallic data usually means the sample mixes product forms or heats.

---

## The k-factor

Three independent routes, implemented so they can cross-check each other.

**Exact**, from the non-central t distribution. This is the definition rather than an approximation to it:

```
k = t'_(n-1, delta)(gamma) / sqrt(n)          delta = z_p * sqrt(n)
```

**Natrella / Owen closed form**, which needs no special functions:

```
a = 1 - z_gamma^2 / (2 (n - 1))
b = z_p^2 - z_gamma^2 / n
k = [ z_p + sqrt(z_p^2 - a b) ] / a
```

**MMPDS Chapter 9 curve fits**, at 95 percent confidence:

```
k_B = 1.282 + exp(0.958 - 0.520 ln n + 3.19 / n)
k_A = 2.326 + exp(1.340 - 0.522 ln n + 3.87 / n)
```

The three constants that everything rests on:

| Quantity | Value | Meaning |
|---|---|---|
| `z_p` for A-basis | 2.3263479 | One-sided 99 % exceedance |
| `z_p` for B-basis | 1.2815516 | One-sided 90 % exceedance |
| `z_gamma` | 1.6448536 | 95 % confidence |

**The three routes agree to within 2 percent at n = 10 and better than 1 percent above n = 20.** A test asserts this across the range, and it is worth more than any single implementation because it catches a coding error that one implementation alone cannot see.

**The leading constants in the MMPDS fits are the limiting normal quantiles**, which is why the fits converge correctly: with infinite data there is no confidence penalty left and `k` becomes `z_p`.

---

## What the sample size costs

| n | k_B | k_A | B-basis as % of mean at CV 3 % | A-basis as % of mean |
|---|---|---|---|---|
| 5 | 3.407 | 5.741 | 89.8 | 82.8 |
| **10** | **2.355** | **3.981** | **92.9** | **88.1** |
| 20 | 1.926 | 3.295 | 94.2 | 90.1 |
| **30** | **1.777** | **3.064** | **94.7** | **90.8** |
| 50 | 1.646 | 2.862 | 95.1 | 91.4 |
| **100** | **1.527** | **2.684** | **95.4** | **91.9** |
| 300 | 1.417 | 2.522 | 95.7 | 92.4 |
| infinity | 1.282 | 2.326 | 96.2 | 93.0 |

**Below n = 10 the number stops being about the material.** At n = 5 the A-basis factor is 5.741, which for any realistic scatter produces a value driven almost entirely by how little data there is. The [`Allowables`](../aerospaceMaterialsLibrary/Allowables.py) class raises rather than returning it.

**There is a ceiling that no amount of testing reaches.** With infinite data `k` converges on `z_p`, so the basis ratio cannot exceed `1 - z_p * CV`. At a 5 percent coefficient of variation the A-basis can never rise above 88 percent of the mean. Reducing process scatter is the only route past that, and it is a manufacturing conversation rather than a testing one.

---

## Batches, and why pooling overstates the allowable

Test specimens come from lots, and lots differ. Pooling every specimen as though they came from one population treats between-lot variation as though it were measurement noise, and it understates the true population spread.

```
s_total^2 = s_within^2 + s_between^2
```

The ANOVA route separates the two variance components and computes the tolerance limit from the total. It produces the lower and more defensible number, and **the difference between the pooled and ANOVA values is a direct measure of how much lot to lot variation the process carries.**

**MMPDS practice wants at least ten lots** for a directly computed basis value. A thirty-specimen sample from one heat is a statement about that heat, not about the alloy.

When between-lot variation exceeds within-lot variation, that is a **process control finding as much as a statistical one**, and it usually points at the supplier rather than at the material.

---

## The non-parametric alternative

Assuming nothing about the distribution, the r-th smallest observation is a lower tolerance bound with confidence

```
C = 1 - sum_(i=0)^(r-1) C(n, i) p^i (1-p)^(n-i)
```

**The cost of assuming nothing is severe.** A B-basis at 95 percent confidence needs `n = 29` before even the lowest observation qualifies as a bound. An A-basis needs `n = 299`.

That is precisely why metallic allowables are computed parametrically. The normality assumption is doing enormous work, which is also why the goodness of fit is worth checking rather than assuming.

---

## Knockdowns

The basis value is not the design value. Process effects are applied on top, and they compound multiplicatively.

| Knockdown | Factor | Why |
|---|---|---|
| Aluminium, as-welded | 0.55 | HAZ loses temper, no recovery without solution treat and age |
| Aluminium, post-weld heat treated | 0.90 | Solution treated and aged after welding |
| Austenitic stainless weld | 1.00 | Solid solution alloy, no strength to lose |
| **Electron beam weld** | **0.95** | Narrow HAZ, minimal heat input |
| Friction stir weld | 0.80 | Solid state, but the nugget is recrystallised |
| **Casting, qualified process** | **1.00** | 100 % volumetric NDE and three sample lots |
| Casting, partial qualification | 0.75 | The 1.33 casting factor |
| **Casting, no qualification** | **0.50** | The default 2.0 casting factor |
| Additive, Z direction with HIP | 0.90 | Build direction normal to the load |
| Additive, as-built surface | 0.75 | Fatigue on an unmachined LPBF surface |
| Slow quench, thick section | 0.85 | Incomplete solution retention |

**The casting factor is the strongest argument in this table.** The difference between a qualified and an unqualified casting process is the entire allowable, and qualifying the process is frequently cheaper than the mass the factor costs.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| A-basis for single load path | Pressure vessels, single fasteners, monolithic fittings |
| Minimum sample for a computed basis | n = 10 hard floor, n = 100 advisory |
| Minimum lots | 10, per MMPDS practice |
| k_B at n = 30 | 1.777 |
| k_A at n = 30 | 3.064 |
| Basis ratio ceiling | `1 - z_p * CV`, unreachable by more testing |
| Coefficient of variation above 8 % | Usually a mixed sample, not a variable material |
| Knockdowns compound multiplicatively | And the chain has to be recorded |
| Non-parametric B-basis | Needs n = 29 minimum |

---

## Failure modes

**A typical value used as an allowable.** The margin does not exist.

**An A-basis from five specimens.** A number with the authority of a statistic and the content of a guess.

**Pooling across lots.** Understates the spread, overstates the allowable.

**A knockdown forgotten.** An aluminium weldment sized on parent properties.

**Two knockdowns applied where one covers both.** Over-conservative, which costs mass and looks rigorous.

**A rejected distribution fit ignored.** Usually a sample that mixes product forms or test temperatures.

**No audit trail.** The design value cannot be revisited when an assumption changes.

**Asking for a basis ratio above the ceiling.** No sample size reaches it; only reducing scatter does.

---

## Worked example

From [`codeInterface.py`](../codeInterface.py), the Ti-6Al-4V bottle:

| Step | Factor | Value [MPa] | Basis |
|---|---|---|---|
| Sample mean | -- | 957.2 | 30 specimens, CV 2.99 % |
| **A-basis tolerance limit** | 0.9082 | **869.4** | k = 3.064 at n = 30 |
| EB girth weld | 0.9500 | 825.9 | Narrow HAZ, minimal heat input |
| **Design value** | 0.8628 | **825.9** | 13.7 % below typical in total |

| Comparison | Value |
|---|---|
| B-basis at the same sample | 906.3 MPa |
| **Cost of the single load path** | **37 MPa, 4.1 %** |
| n needed for a 0.92 basis ratio | 105, against the 30 tested |

The last line is the useful one: reaching a 92 percent basis ratio would need three and a half times the testing, and the programme now has a number to put against that decision rather than an instinct.

---

## Standards

| Standard | Scope |
|---|---|
| **MMPDS Chapter 9** | Statistical procedures for computing allowables |
| **CMH-17 Volume 1** | Composite allowables methodology |
| ASTM E739 | Statistical analysis of linear or linearized stress-life data |
| ISO 16269-6 | Statistical tolerance intervals |
| NASA-STD-5001 | Structural design and test factors of safety |
| **NASA-STD-6016** | Materials and processes requirements, including allowables |
| ASTM E8 / E21 | Tension testing at room and elevated temperature |

---

## Tool interface

```python
import numpy as np

# a synthetic lot, so this fence runs standalone
rng = np.random.default_rng(20260807)
measuredStrengths = rng.normal(350.0e6, 12.0e6, 60)
lotNumbers = ['lot-{}'.format(1 + index // 6) for index in range(60)]

from Allowables import Allowables, toleranceFactorExact

allowables = Allowables()
allowables.setInputs({'sampleData': measuredStrengths,       # np.ndarray [Pa]
                      'batchIdentifiers': lotNumbers,
                      'loadPath': 'single',                  # requires A-basis
                      'knockdowns': {'girth weld': 'weld, electron beam'}})

allowables.fitDistribution()        # Anderson-Darling
allowables.calculateBasisValue()    # both A and B; raises below n = 10
allowables.selectDesignValue()      # A or B from the load path, and the cost of the choice
allowables.applyKnockdowns()        # the ordered chain
allowables.calculateAnovaBasis()    # multi-lot variance components
allowables.calculateRequiredSampleSize(0.92)
print(allowables.generateReport())
```

Module functions: `toleranceFactorExact`, `toleranceFactorNatrella`, `toleranceFactorMmpds`. Lookup table: `Allowables.STANDARD_KNOCKDOWNS`.

---

## References

1. MMPDS-18, Chapter 9, *Guidelines for the Presentation of Data*.
2. Natrella, M. G., *Experimental Statistics*, NBS Handbook 91, 1963.
3. Owen, D. B., "Factors for One-Sided Tolerance Limits", Sandia SCR-607, 1963.
4. Meeker, W. Q., Hahn, G. J. and Escobar, L. A., *Statistical Intervals*, 2nd ed., Wiley, 2017.
5. CMH-17-1G, *Composite Materials Handbook*, Volume 1, Chapter 8.
