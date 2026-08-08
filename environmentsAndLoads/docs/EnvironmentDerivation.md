[Home](../README.md) > Environment Derivation

# Environment Derivation

## Contents

- [Overview](#overview)
- [The chain](#the-chain)
- [Why the statistics are done in decibels](#why-the-statistics-are-done-in-decibels)
- [Percentile and confidence](#percentile-and-confidence)
- [Zones](#zones)
- [Enveloping](#enveloping)
- [The margin ladder](#the-margin-ladder)
- [When there is no flight data](#when-there-is-no-flight-data)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

This is the document the domain exists for. Everything else describes an environment; this one describes how a number becomes a requirement, and how to tell whether a given number can be defended.

---

## The chain

| Step | Operation | Adds |
|---|---|---|
| **1. Measure** | Accelerometers, microphones, in the right zone | Nothing. Evidence |
| **2. Process** | PSD from the time history, band by band | Nothing |
| **3. Pool** | Across flights and channels in one zone | Nothing |
| **4. Limit** | Mean + k sigma, in decibels | **1 to 3 dB** |
| **5. Envelope** | A straight-line breakpoint table over the data | **1 to 2 dB** |
| **6. Acceptance** | = MPE | 0 dB |
| **7. Qualification** | + 3 dB, x2 duration | **3 dB** |

**Steps 4, 5 and 7 are where every decibel comes from**, and each is a defensible engineering decision with an alternative. Steps 1 to 3 are measurement and cannot be argued with; steps 4 to 7 can.

**The total is typically 5 to 8 dB from the mean measurement to the qualification level**, which is a factor of three to six in power spectral density. That is a large number and it is worth being able to itemise.

---

## Why the statistics are done in decibels

**Because vibration environments are log-normally distributed, not normally.**

A physical argument makes this unsurprising: the response at a point is a product of many factors, source strength times transmissibility times local impedance, and a product of random variables tends to log-normal in the way a sum tends to normal.

**The consequence is direct.** Taking a mean and standard deviation on linear PSD values and adding `k sigma` gives a different answer from doing it in decibels, and the linear answer is wrong. The error grows with the scatter, so it is worst exactly where it matters.

**A negative lower bound is the tell.** If a linear mean-minus-two-sigma comes out negative, the distribution is not normal and the whole calculation was on the wrong scale.

---

## Percentile and confidence

**Both are part of the specification, and they answer different questions.**

| Basis | k | Means |
|---|---|---|
| **P50/50** | 0.000 | The mean. **Not a maximum predicted environment** |
| **P95/50** | 1.645 | 95th percentile, 50 % confidence. The common choice |
| **P95/90** | 2.145 | 95th percentile, **90 % confidence** |
| P99/90 | 3.000 | 99th percentile, 90 % confidence |

**Percentile is about the population.** P95 means 95 percent of flights fall below this level.

**Confidence is about the sample.** P95/90 means you are 90 percent confident that the true 95th percentile is below your estimate, which matters when the standard deviation is itself estimated from few samples.

**With three flights the standard deviation is barely known**, so P95/50 is not defensible and P95/90 is. The higher factor exists precisely to cover that uncertainty, and using the lower one with a small sample is the commonest way a derivation is quietly wrong.

---

## Zones

**A zone is a region of the vehicle within which the environment is treated as uniform, and defining them is the largest single decision in the domain.**

| Zone | Relative severity |
|---|---|
| **Engine compartment** | **4.0** |
| Aft skirt | 2.5 |
| Forward skirt | 1.2 |
| **Tank barrel** | **1.0** (reference) |
| Payload bay | 0.6 |
| **Isolated payload** | **0.2** |

**That is 13 dB from top to bottom**, against 3 to 6 dB for every margin policy argument in the discipline.

**A zone that is not homogeneous should be split.** The tell is a large standard deviation in the pooled data: if the scatter within a zone exceeds about 5 dB, the zone is probably combining places that behave differently, and splitting it lowers the derived level for most of the hardware in it.

**Zone boundaries are drawn early, on a layout drawing, often by someone not thinking about vibration.** Revisiting them with data is one of the highest-leverage things a programme can do and it is rarely done, because by then the specifications are baselined.

---

## Enveloping

**A breakpoint table is a straight-line envelope over a ragged measured spectrum, and the enveloping itself adds margin.**

| Approach | Character |
|---|---|
| **Tight envelope** | Follows the data, many breakpoints, hard to test to |
| **Loose envelope** | Few breakpoints, easy to specify, adds 1 to 3 dB |
| Peak-hold envelope | Over every flight and channel. Very conservative |

**Enveloping across zones is where it gets expensive.** A single specification covering the whole vehicle is the envelope of every zone, which means everything is qualified to the engine compartment. That is 13 dB of unnecessary margin on most of the hardware.

**Notching is the reverse operation** and it is legitimate: reducing the input at a frequency where the test fixture drives the article harder than flight would. It requires a force limit or a response limit justification, and it is the difference between testing the hardware and testing the fixture.

---

## The margin ladder

**Every decibel should be traceable to a reason.**

| Source | Typical | Reason |
|---|---|---|
| **Statistical limit** | +1 to +3 dB | Population and sampling uncertainty |
| **Enveloping** | +1 to +2 dB | Straight lines over ragged data |
| **Qualification margin** | **+3 dB** | Lot and unit variability |
| Duration compression | 0 to +3 dB | Miner equivalence, if the test is shortened |
| **Total** | **+5 to +8 dB** | A factor of 3 to 6 in PSD |

**A test level that looks expensive should be decomposable into that table.** If it cannot be, the level is not derived, and the right response is to say so rather than to argue about it.

---

## When there is no flight data

**Which is most of the time, especially on a new vehicle.**

| Approach | Character |
|---|---|
| **Generic specification** | GEVS, MIL-STD-1540. Chosen from a table |
| **Heritage** | A similar vehicle's measured environment, scaled |
| **Analysis** | Vibroacoustic model, VAPEPS or finite element |
| **Ground test** | Static fire measurements, which cover the engine source only |

**Using a generic specification is legitimate and it must be labelled.** The problem is never that a generic environment was used; it is that it was used and then treated as though it had been derived, so nobody knows how much margin is in it or whether it is even conservative.

**A generic environment can be unconservative.** The worked example finds the derived level 1.12 dB above the generic one, meaning the hardware had been qualified to less than it will see.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Do the statistics in decibels | Environments are log-normal |
| P95/50 with few samples is not defensible | Use P95/90 |
| A zone with scatter above 5 dB should be split | It is not homogeneous |
| Zone definition is worth 13 dB | Margin policy is worth 3 to 6 |
| Enveloping adds 1 to 3 dB | And more across zones |
| Total flight-to-qualification | 5 to 8 dB |
| Label a generic environment as chosen | Not derived |
| Every decibel needs a reason | Or it is not a derivation |

---

## Failure modes

**Linear statistics on a log-normal quantity.** Wrong, and worst where the scatter is largest.

**P95/50 with three flights.** The standard deviation is not known well enough.

**One specification enveloped across the whole vehicle.** 13 dB of unnecessary margin on most hardware.

**A generic environment presented as derived.** Nobody knows how much margin is in it.

**Notching without a force or response limit justification.** Unsupported relief.

**Duration compressed without checking the failure mode.** Miner assumes it does not change.

**Margin added at each step by a different person.** Nobody owns the total.

---

## Worked numbers

From [`codeInterface.py`](../codeInterface.py), six flights in the aft skirt:

| Step | Value | Added |
|---|---|---|
| Sample mean | 0.0515 g^2/Hz | -- |
| Standard deviation | 1.01 dB | -- |
| **P95/50 limit** | **0.0756 g^2/Hz** | **+1.67 dB** |
| Normalised onto the measured shape | 9.25 Grms | +1.00 dB |
| Qualification | 11.64 Grms, 120 s/axis | +3.00 dB |

**Against the generic specification of 8.13 Grms, the derived environment is +1.12 dB.**

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-HDBK-7005** | Dynamic environmental criteria. The derivation reference |
| **NASA-STD-7001** | Payload vibroacoustic test criteria |
| MIL-STD-1540 | Test requirements, including the margin policy |
| GSFC-STD-7000 | GEVS, the generic specification most often used |
| ECSS-E-ST-10-03 | Testing |
| IES-RP-DTE012 | Handbook for dynamic data acquisition and analysis |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'environmentsAndLoadsLibrary')

from environmentsUtils import toleranceLimit, NORMAL_TOLERANCE_FACTORS

measurements = [0.042, 0.061, 0.038, 0.071, 0.049, 0.055]

for basis in ('P50/50', 'P95/50', 'P95/90', 'P99/90'):
    result = toleranceLimit(measurements, basis = basis)
    print(f'{basis}  k = {result["toleranceFactor"]:.3f}  '
          f'{result["limitValue"]:.4f} g^2/Hz  '
          f'{result["marginOverMean"]:+.2f} dB over the mean')
```

---

## References

1. NASA-HDBK-7005, *Dynamic Environmental Criteria*, 2001.
2. Piersol, A. G., "Determination of Maximum Structural Responses", *Shock and Vibration Bulletin*, 1991.
3. MIL-STD-1540E, *Test Requirements for Launch, Upper Stage and Space Vehicles*.
