[Home](../README.md) > Performance and Payload

# Performance and Payload

## Contents

- [Overview](#overview)
- [Two vehicles, two sensitivities](#two-vehicles-two-sensitivities)
- [The ethos this domain corrected](#the-ethos-this-domain-corrected)
- [The upper stage matters more](#the-upper-stage-matters-more)
- [What the elasticities are on the reference vehicle](#what-the-elasticities-are-on-the-reference-vehicle)
- [The two exchange ratios](#the-two-exchange-ratios)
- [Margin allocation](#margin-allocation)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Payload is what is left after everything else has been subtracted, so it moves more than anything that moves it. That much is folklore. This document puts numbers on it and finds the folklore is a claim about a particular kind of vehicle rather than about rockets.

---

## Two vehicles, two sensitivities

The same one per cent error costs different amounts depending on when it is found.

**A rubber vehicle** is re-sized around the change. The tanks grow, the liftoff mass grows, and the payload fraction absorbs most of it. That is the sensitivity that matters during conceptual design, when the vehicle is still a spreadsheet.

**A fixed vehicle** has been built. The propellant load and the tank volumes are what they are, so an error in dry mass comes off the payload and nothing else. That is the sensitivity that matters after metal is cut.

The second is larger, and the gap between them is the argument for finding errors early.

---

## The ethos this domain corrected

This domain's stated design principle said the payload is the residual of a large subtraction, so small errors upstream are large errors in payload.

That is worth checking rather than repeating.

| Vehicle | Payload fraction | Fixed-vehicle elasticity |
|---|---|---|
| Reference, good structure | 4.17 % | 0.34 |
| Mediocre structure | 3.44 % | 0.53 |
| Pressure fed upper stage | 2.24 % | 0.90 |
| Marginal, near closure | 1.38 % | 1.50 |

**The elasticity is not a property of the rocket equation. It is inversely proportional to the payload fraction the design already has.**

On a healthy vehicle a one per cent dry mass error costs a third of a per cent of payload. On a marginal one it costs one and a half.

So the original claim is true of designs in trouble and not of designs in general, and **it becomes true exactly when the design is least able to respond to it.** That is a more useful statement than the original, because it says when to worry rather than saying worry always.

The domain README has been corrected to match, and a test asserts the monotonic relationship across the sweep so the correction cannot quietly revert.

---

## The upper stage matters more

A kilogram on the upper stage is carried the whole way. A kilogram on the lower stage is dropped early.

Everybody states that qualitatively. The elasticities put a number on it: on the reference vehicle, the second stage specific impulse elasticity is about two and a half times the first stage's, and the same ordering holds for the structural coefficients.

**That ordering is worth having before allocating engineering effort**, because it is not obvious how much more the upper stage matters, only that it does.

---

## What the elasticities are on the reference vehicle

Fractional change in payload per fractional change in the input, on a rubber vehicle sized to a fixed delta-V.

| Input | Elasticity |
|---|---|
| Target delta-V | -3.57 |
| Stage 2 specific impulse | +2.65 |
| Stage 1 specific impulse | +1.03 |
| Stage 2 structural coefficient | -0.30 |
| Stage 1 structural coefficient | -0.09 |

**The delta-V target is the largest single term**, which is worth noticing: the mission requirement moves the payload more than any hardware property does. A hundred metres per second of unbudgeted loss is worth more than a percentage point of specific impulse.

The signs are all as they should be, and that is not a trivial statement: an inverted bisection in the staging optimiser once made every one of them come out backwards, and nothing except a sign check noticed.

---

## The two exchange ratios

An elasticity is dimensionless and a recovery budget needs kilograms, so `exchangeRatios()` reports the other form of the same question: **payload lost per kilogram of first stage dry mass, and per kilogram of first stage propellant the ascent burn does not use.**

These are the two numbers [recoveryAndReusability](../../recoveryAndReusability/) builds a recovery penalty from, and they belong here rather than there because a landing leg and a landing burn cost payload through the same rocket equation as everything else on the stage.

**The two perturbations differ in one respect and that is the whole result.** Added dry mass raises the first stage initial mass and its burnout mass together. Reserved propellant is already aboard, so it raises the burnout mass alone. Differentiating the stage contribution:

```
d(dV)/d(dry)      = c (1/I - 1/F)
d(dV)/d(reserve)  = -c / F

dry / reserve     = 1 - F/I = 1 - 1/R
```

**`1 - 1/R` is below one for any stage that burns any propellant**, so a kilogram of reserve propellant always costs more payload than a kilogram of dry mass, on every vehicle, and relatively more the smaller the mass ratio of the stage carrying it. The offsetting rise in initial mass is what dry mass gets and reserve does not.

| Vehicle | First stage `R` | Dry | Reserve | `1 - 1/R` | Measured |
|---|---|---|---|---|---|
| Falcon 9 class | 3.63 | 0.1115 | 0.1540 | 0.7242 | 0.7242 |
| Small kerolox | 3.65 | 0.1106 | 0.1524 | 0.7261 | 0.7261 |
| Hydrolox | 3.37 | 0.2674 | 0.3803 | 0.7032 | 0.7032 |
| Heavy, poor structure | 4.46 | 0.0727 | 0.0937 | 0.7758 | 0.7758 |

**The closed form is reported alongside the numerical result rather than instead of it.** A closed form that has not been checked against the thing it claims to describe is a claim about algebra, and this one is asserted against the measured ratio on all four vehicles.

**A vehicle whose propellant loads are given is taken as built.** A recovery budget is written against a stage that exists, so only a vehicle without them is re-optimised, and the exchange ratio then belongs to the optimal split rather than to any real article.

## Margin allocation

Payload margin and mass margin are the same margin seen from two ends, and the conversion is the elasticity.

On the reference vehicle, holding 5 per cent payload margin is equivalent to holding about 15 per cent dry mass margin, because the elasticity is about a third. On a marginal vehicle at an elasticity of 1.5, the same 5 per cent payload margin costs only 3 per cent of dry mass.

**A marginal design needs less mass margin to protect the same payload margin**, which is counterintuitive and is a consequence of the payload already being small. It is not an argument for marginal designs.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Reference payload fraction | 4.17 % |
| Fixed-vehicle dry mass elasticity | 0.34 |
| Marginal-vehicle dry mass elasticity | 1.50 |
| Largest rubber elasticity | delta-V target, 3.57 |
| Upper to lower stage elasticity ratio | about 2.6 |

---

## Design rules of thumb

- **Ask the payload fraction before quoting a sensitivity.** They are inversely related.
- **Worry about mass in proportion to how little margin the design has**, not always and not never.
- **Budget the delta-V carefully.** It is the largest single elasticity on a rubber vehicle.
- **Weight upper stage effort by the elasticity ratio**, which is about two and a half here.
- **Convert payload margin to mass margin through the elasticity**, not one for one.

---

## Failure modes

**Quoting a sensitivity without the vehicle it belongs to.** They differ by a factor of five across reasonable designs.

**Assuming the rubber and fixed sensitivities are the same.** They are not, and which one applies depends on whether metal has been cut.

**An unbudgeted delta-V loss.** The largest elasticity on the list.

**Treating a sign check as trivial.** An inverted solver made every elasticity here come out backwards and nothing else caught it.

---

## Tool interface

```python
from StagedVehicle import StagedVehicle

vehicle = StagedVehicle()
vehicle.setInputs({'stages': [{'specificImpulse': 297.0, 'structuralCoefficient': 0.0513},
                              {'specificImpulse': 348.0, 'structuralCoefficient': 0.0359}],
                   'payloadMass':  22800.0,
                   'targetDeltaV': 9252.0})

sensitivity = vehicle.payloadSensitivity()

rubber = sensitivity['elasticities']
fixed  = sensitivity['fixedVehicle']['dryMassElasticity']
```

---

## References

- [RocketEquationAndStaging](RocketEquationAndStaging.md), for the sizing this differentiates
- [MassChain](MassChain.md), for where the dry mass actually comes from
- Humble, Henry and Larson, *Space Propulsion Analysis and Design*
