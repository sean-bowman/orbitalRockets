[Home](../README.md) > Sensors and Navigation

# Sensors and Navigation

## Contents

- [Overview](#overview)
- [The four error terms](#the-four-error-terms)
- [Why the gyroscope wins](#why-the-gyroscope-wins)
- [The crossover](#the-crossover)
- [Grades](#grades)
- [Aiding bounds, it does not reduce](#aiding-bounds-it-does-not-reduce)
- [Alignment](#alignment)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

An inertial navigation system measures acceleration and angular rate and integrates them. Everything it gets wrong is integrated too, which is why the error growth **law** matters more than the error magnitude.

---

## The four error terms

Each sensor error enters the position solution through a different number of integrations, so each grows at a different rate.

| Source | Enters as | Position error grows as |
|---|---|---|
| Accelerometer random walk | velocity noise | t^1.5 |
| Accelerometer bias | constant acceleration | t^2 |
| Gyro random walk | attitude noise, then tilt | t^2.5 |
| Gyro bias | attitude ramp, then tilt | **t^3** |

**The exponents are exact**, because each is an integration of a constant or of a random walk, and they are asserted as such in the tests rather than fitted.

Because they differ, **the dominant term changes with flight duration**, and any statement about which sensor matters is a statement about a flight length.

---

## Why the gyroscope wins

The mechanism is worth stating because it is not obvious and it is the whole result.

An attitude error tilts the accelerometer triad. A tilted accelerometer resolves a component of gravity into what it reports as horizontal acceleration:

```
a = g sin(theta) ~ g theta
```

**Gravity is 9.8 m/s^2 and it is always there.** A milliradian of tilt produces about 10 mm/s^2 of false horizontal acceleration, which is 1000 micro g, which is larger than the bias of any accelerometer worth flying.

So the gyroscope's error reaches the position solution *through the accelerometer*, amplified by gravity, and integrated one extra time because the attitude error is itself growing.

---

## The crossover

On a tactical grade unit, the accelerometer bias and gyro-through-tilt terms cross at about **63 seconds**.

| Time | Accelerometer bias | Gyro through tilt |
|---|---|---|
| 30 s | 1.3 m | 0.6 m |
| 60 s | 5.3 m | 5.1 m |
| 120 s | 21.2 m | 41.1 m |
| 300 s | 132.4 m | 641.8 m |
| 540 s | 428.9 m | **3743.2 m** |

At sixty seconds they are within a few per cent. At nine minutes they are a factor of nine apart, and the gyro term is 98.6 per cent of the variance.

**Below the crossover an accelerometer specification is what to buy and above it a gyro specification is.** A sensor budget written from a short-flight intuition, or from a ground test that lasted a minute, buys the wrong instrument.

---

## Grades

The same nine minute flight on three sensor classes:

| Grade | Attitude error | Position error |
|---|---|---|
| Navigation | 0.0017 deg | 52 m |
| Tactical | 0.1512 deg | 3770 m |
| Industrial | 7.5025 deg | 187 188 m |

**A spread of 3594 times.** That is unusual: for most components the grade choice is worth tens of per cent and here it is worth three and a half orders of magnitude.

So **the grade is the decision and the specific unit is a detail**, which inverts the usual procurement instinct.

---

## Aiding bounds, it does not reduce

An aiding source does not make the inertial errors smaller. It stops them growing, by correcting the solution periodically, and that is a different and more useful thing.

Two consequences follow and both are operational rather than analytical.

**Availability matters more than accuracy.** A 10 m aiding source available 98 per cent of the time leaves 2 per cent of the flight on pure inertial, and the pure inertial error at the end of a 9 minute flight is kilometres. **The unaided case has to be survivable, not merely unlikely.**

**The outage duration matters more than its frequency.** Error grows as the cube of time since the last correction, so one long outage is far worse than several short ones totalling the same time.

A star tracker is worth noting separately: it bounds **attitude** only, and attitude is exactly the term that dominates the position growth. It is also useless in atmosphere and during high rate manoeuvres, which is most of an ascent.

---

## Alignment

Everything above assumes the navigation started from a known attitude. Getting there is its own problem.

**Gyrocompassing** finds north by sensing the Earth's rotation rate, 15 degrees per hour. That requires a gyro whose bias is small compared with a component of that rate, which is precisely the navigation grade threshold: a 1 degree per hour tactical gyro cannot gyrocompass usefully.

**Transfer alignment** takes the attitude from another system, which moves the problem rather than solving it.

**An alignment error is an initial attitude error**, and it enters the position solution through the same tilt path as a gyro bias, except that it does not grow: it produces a position error growing as t squared rather than t cubed. **That makes a poor alignment equivalent to an accelerometer bias**, which is a useful way to compare them.

---

## Worked numbers

Tactical grade, 540 s, GPS aided.

| Quantity | Value |
|---|---|
| Gyro bias | 1.0 deg/h |
| Accelerometer bias | 300 micro g |
| Attitude error at 540 s | 0.151 deg |
| Position error, unaided | 3770 m |
| Gyro term share of variance | 98.6 % |
| Crossover time | 63 s |
| Position error, GPS bounded | 10 m |
| GPS availability | 98 % |

---

## Design rules of thumb

- **Specify the gyro first** on anything flying longer than about a minute.
- **State the flight duration** with any sensor requirement. Without it the requirement is meaningless.
- **Choose the grade, then the unit.** The grade is worth three orders of magnitude.
- **Size for the unaided case.** Aiding availability is not certainty.
- **Check gyrocompassing feasibility against the bias.** Below navigation grade it is not available.

---

## Failure modes

**A sensor budget written from a short flight.** Buys the accelerometer and the gyro decides.

**A requirement with no duration.** Cannot be met or missed.

**Aiding treated as a reduction.** It is a bound, and it has an availability.

**One long outage budgeted as several short ones.** The growth is cubic in the gap.

**Gyrocompassing assumed on a tactical unit.** The bias swamps the Earth rate component.

---

## Tool interface

```python
from NavigationDrift import NavigationDrift

navigation = NavigationDrift()
navigation.setInputs({'grade':               'tactical',
                      'flightTime':          540.0,
                      'aiding':              'GPS',
                      'positionRequirement': 500.0})

drift      = navigation.calculateDrift()
crossover  = navigation.identifyCrossover()
comparison = navigation.compareGrades()
check      = navigation.checkRequirement()
```

`checkRequirement()` raises rather than reporting a negative margin, because a vehicle that does not know where it is is not a degraded vehicle.

---

## References

- Titterton and Weston, *Strapdown Inertial Navigation Technology*
- IEEE Std 952, *Specification Format Guide and Test Procedure for Single-Axis Interferometric Fiber Optic Gyros*, not read here
- [ValidationReferences](ValidationReferences.md), for the exact integration laws
