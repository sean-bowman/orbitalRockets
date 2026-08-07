[Home](../README.md) > Life and Endurance Testing

# Life and Endurance Testing

## Contents

- [Overview](#overview)
- [What life means, by article](#what-life-means-by-article)
- [The test condition](#the-test-condition)
- [Acceleration](#acceleration)
- [What to instrument](#what-to-instrument)
- [Wear-out mechanisms](#wear-out-mechanisms)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Life testing demonstrates that the article survives four times its expected service life. It is the longest activity in a qualification campaign, it is on the critical path from the moment it starts, and it is the test most often run at the wrong condition.

**The point is to find the wear-out mechanism.** A life test that produces no failures at 4x has demonstrated the margin. One that produces a failure at 3.5x has demonstrated considerably more, because the mechanism is now known and can be designed against, inspected for, and life-limited.

---

## What life means, by article

Life is not one number, and testing the wrong one demonstrates nothing.

| Article | Life unit | Wear-out mechanisms |
|---|---|---|
| **Valve** | Actuation cycles | Seat wear, stem seal wear, actuator degradation, galling |
| **Regulator** | Cycles and total throughput | Seat erosion, spring relaxation, diaphragm fatigue, setpoint drift |
| **Check valve** | Cycles | Seat wear from chatter, spring fatigue, reverse leakage growth |
| **Catalyst bed** | Pulses and cumulative burn seconds | Attrition, washout, sintering, poisoning; ignition delay growth |
| **Seal** | Compressed hours at temperature | Compression set, stress relaxation, chemical attack, permeation |
| **Bellows** | Flex cycles | Fatigue cracking at the convolution root |
| **Pressure vessel** | Pressure cycles | Fatigue crack growth; stress rupture for a COPV |
| **Filter** | Throughput mass | Dirt capacity exhausted; element collapse |

**A regulator has two life units and both matter.** Cycling it demonstrates the seat; flowing through it demonstrates erosion. A test that does one and not the other has demonstrated half of it.

---

## The test condition

**This is the part that decides whether the test means anything**, and it is where life tests most commonly go wrong.

| Get this right | Or the test demonstrates |
|---|---|
| At the operating differential | The actuator, not the seat |
| At temperature | Ambient behaviour of a component that runs hot or cold |
| With the service fluid or a representative one | Nothing about chemical compatibility or lubricity |
| Leak tested throughout, not only at the end | The end state, with no trend |
| At the flight duty cycle | A different thermal state entirely |

**Cycling a valve open and closed at ambient with no differential is the classic example.** It exercises the actuator through its full stroke and tells you nothing about seat wear, which is the mechanism that actually limits the life.

**Duty cycle matters for anything thermal.** A catalyst bed pulsed at the flight duty cycle reaches a different bed temperature from one pulsed continuously, and bed temperature drives both the ignition delay and the attrition rate.

---

## Acceleration

Acceleration is how a ten-year life fits in a six-month programme. It rests on a model, and the model rests on a parameter that is material and mechanism specific.

**Arrhenius**, for thermally activated degradation (elastomer ageing, lubricant breakdown, diffusion):

```
AF = exp( (Ea / k) * (1/T_use - 1/T_test) )
```

**Coffin-Manson**, for thermal cycling fatigue:

```
AF = (dT_test / dT_use)^n
```

| Model | Typical parameter | Sensitivity |
|---|---|---|
| Arrhenius | Ea = 0.7 eV | **Exponential.** 0.5 vs 0.9 eV changes AF by an order of magnitude |
| Coffin-Manson | n = 2 to 3 | Power law. 2 vs 3 changes AF by the range ratio |

**Using a default is a stated assumption, not a calculation.** The [`LifeTest`](../fluidSystemsTestingLibrary/LifeTest.py) class flags it every time a default is used, because an Arrhenius factor computed from an assumed activation energy is a number with no more authority than the assumption behind it.

**The limit on acceleration is that it must not change the failure mechanism.** Raising the temperature until an elastomer is above its own decomposition point does not accelerate ageing; it substitutes a different failure. **An acceleration factor above about 20 needs the mechanism explicitly argued.**

**Parallelism is the alternative.** Running four articles for a quarter of the duration demonstrates the same total life with no model assumption, at the cost of three more articles. When the acceleration model is weak, this is the honest path.

---

## What to instrument

The whole value of a life test is in the trend, so the instrumentation has to run throughout rather than bracketing the test.

| Measurement | Detects |
|---|---|
| **Leak rate, at intervals** | Seat and seal degradation, long before functional failure |
| **Flow number, at intervals** | Erosion, plugging, edge rounding |
| Actuation force or current | Friction growth, galling onset |
| Response time | Actuator degradation, contamination |
| Setpoint (regulators) | Spring relaxation, seat erosion |
| Ignition delay (catalyst beds) | Poisoning and attrition |
| Cycle count | The independent variable, recorded automatically |
| Temperature | Confirms the condition is being maintained |

**Define the interval before starting.** Measuring at 10 percent increments gives ten points on a trend; measuring at the start and end gives two, and two points cannot show a knee.

---

## Wear-out mechanisms

**Wear-out is what the test is looking for**, and recognizing its onset matters more than reaching the target count.

| Signature | Likely mechanism |
|---|---|
| Leak rate rising smoothly | Seat wear or compression set |
| Leak rate stepping | A particle, or a cracked seal |
| Flow number rising | Erosion or edge rounding |
| Flow number falling | Plugging or contamination |
| Actuation force rising | Friction growth, galling, lubricant loss |
| Response time growing | Actuator degradation or contamination |
| Setpoint drifting | Spring relaxation |
| Ignition delay growing | Catalyst poisoning |

**A trend that flattens is more suspicious than one that rises.** It often means the measurement stopped being sensitive rather than that the degradation stopped.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Life factor | 4x expected, for flight hardware |
| Test at the operating condition | Differential, temperature, fluid, duty cycle |
| Instrument throughout | The trend is the value, not the end state |
| Measurement interval | 10 % increments minimum |
| Acceleration factor ceiling | ~20 without an explicit mechanism argument |
| Arrhenius Ea | Measure it; a default is an assumption |
| Parallelism over acceleration | When the model is weak |
| Start early | It is on the critical path |
| A failure at 3.5x is more informative than a pass at 4x | The mechanism is now known |

---

## Failure modes

**Cycling at the wrong condition.** The most common life test error. The actuator is demonstrated and the seat is not.

**Bracketing instead of trending.** Two data points, no knee, no mechanism.

**An acceleration factor with an assumed activation energy.** The number has no more authority than the assumption.

**Acceleration that changed the mechanism.** The article failed by a route flight would never produce, or survived because the real mechanism was never exercised.

**A regulator cycled but not flowed.** Half the life demonstrated.

**Life testing started late.** It is on the critical path and nothing can compress it.

**No spare article.** The life test article fails at 2x and there is nothing to restart with.

---

## Worked example

The thruster valve from [`codeInterface.py`](../codeInterface.py):

| Quantity | Value |
|---|---|
| Expected service life | 5000 actuation cycles |
| Life factor | 4x |
| **Required demonstration** | **20 000 cycles** |
| Test rate | 2 cycles/s |
| **Duration** | **0.12 days** |
| Fits the schedule | Yes |
| Test condition | At the operating differential, at temperature, with the service fluid or a representative one, leak tested throughout |

An elastomer seal on the same system, for contrast:

| Quantity | Value |
|---|---|
| Expected life | 10 years compressed at temperature |
| Required demonstration | 40 years |
| Arrhenius, 293 K service to 373 K test, Ea = 0.7 eV | **AF = 380** |
| Accelerated duration | **38 days** |

The valve fits easily; the seal only fits because of a factor of 380 that rests entirely on an assumed activation energy. That assumption is the weakest part of the whole campaign and it should be measured rather than defaulted.

---

## Standards

| Standard | Scope |
|---|---|
| MIL-STD-1540 | Test requirements, including life testing |
| NASA-STD-7002 | Payload test requirements |
| MIL-HDBK-217 | Reliability prediction (dated, but the acceleration models persist) |
| JEDEC JESD22-A104 | Temperature cycling (source of Coffin-Manson practice) |
| JEDEC JEP122 | Failure mechanisms and models for semiconductor devices (Arrhenius practice) |
| ASTM D395 | Rubber compression set |
| ASTM D573 | Rubber deterioration in an air oven (accelerated ageing) |

---

## Tool interface

```python
from LifeTest import LifeTest

test = LifeTest()
test.setInputs({'articleType': 'valve', 'expectedLife': 5000,
                'cycleRate': 2.0, 'availableDuration': 30.0 * 86400.0,
                'accelerationModel': 'none'})

test.calculateRequiredLife()   # 4x, plus the condition and wear-out mechanisms
test.calculateAcceleration()   # AF from the selected model
test.calculateDuration()       # raises TestInfeasibleError if it does not fit
print(test.generateReport())
```

Lookup table: `LifeTest.LIFE_DEFINITIONS`, which carries the life unit, the test condition and the wear-out mechanisms for each article type.

---

## References

1. MIL-STD-1540E, *Test Requirements for Launch, Upper-Stage, and Space Vehicles*.
2. Nelson, W., *Accelerated Testing: Statistical Models, Test Plans, and Data Analysis*, Wiley, 2004.
3. Escobar, L. A. and Meeker, W. Q., "A Review of Accelerated Test Models", *Statistical Science*, Vol. 21, 2006.
4. JEDEC JEP122H, *Failure Mechanisms and Models for Semiconductor Devices*.
