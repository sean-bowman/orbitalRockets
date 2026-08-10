[Home](../README.md) > Actuators and Drives

# Actuators and Drives

## Contents

- [Overview](#overview)
- [The margin equation](#the-margin-equation)
- [The threshold, and the correction](#the-threshold-and-the-correction)
- [Fixed against variable](#fixed-against-variable)
- [Three margins](#three-margins)
- [What test evidence buys](#what-test-evidence-buys)
- [Gearboxes](#gearboxes)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

An actuator has to move something against everything resisting it, under worst-case conditions, after storage, once. NASA-STD-5017B turns that into one equation and a table of factors, and the factors are the interesting part.

---

## The margin equation

```
margin = T_avail / (sum FSf Tf + sum FSv Tv + sum FSa Ta) - 1
```

| Symbol | Meaning |
|---|---|
| `T_avail` | Minimum available torque from the driving or holding component |
| `Tf` | Fixed resisting torques, not strongly influenced by environment or cycles |
| `Tv` | Variable resisting torques, which change with environment and cycles |
| `Ta` | Torque required to achieve a specified acceleration |

The standard notes that the minimum available torque from an energised motor is understood to include magnetic losses such as hysteresis and eddy current drag, and mechanical losses such as bearing, brush and windage drag, plus torque ripple from cogging and commutation. **The available torque is not the nameplate torque.**

---

## The threshold, and the correction

**The requirement is a margin at or above zero.** The reserve lives inside the safety factors rather than on top of the result, and the standard says explicitly that setting the factors to unity represents the torque at which no reserve is available.

This is worth stating loudly because a web search summary of this same standard reported the threshold as **1.0 or greater**. It is not. Building on that summary would have made every mechanism in this library look twice as marginal as it is, and would have driven hardware changes to fix a problem that does not exist.

The correction is recorded in [ValidationReferences](ValidationReferences.md) as the clearest case in this repository of reading a primary source paying for itself immediately.

---

## Fixed against variable

The split matters more than anything else in the equation, because **it changes the safety factor by a factor of two**.

**Fixed**: bearing drag, brush and windage drag, return springs, unbalanced pressure loads limited by relief mechanisms, vehicle manoeuvre-induced torques. Factor 1.50 at analysis.

**Variable**: friction torque, viscous drag, wire harness torque due to flexing or set. Factor 3.00 at analysis.

Getting an item into the wrong list is the input most worth checking, and friction is the one that gets misfiled: it belongs in variable, and it is usually the largest term.

The standard lists about twenty conditions a margin calculation has to account for, including changes in static and kinetic friction due to storage time or vacuum exposure, thermally induced distortions, damper drag, variations in lubricity, and torque required when swapping between redundant electronics.

---

## Three margins

They are different calculations rather than three views of one.

**Static margin** asks whether it can start moving. Static friction values, and the acceleration term and its factor are excluded.

**Dynamic margin** asks whether it can achieve a required acceleration. Only applicable where a minimum acceleration, time or velocity is actually required.

**Holding margin** asks whether it stays put against disturbances, and it has two twists. `T_avail` is the **intentional** holding torque only: brakes, springs, detents, a powered motor. The standard explicitly excludes incidental, unreliable and uncharacterised contributors such as joint friction, harness bending and blanket rubbing, **which is the opposite of what a conservative analyst might assume.** And the disturbing torques all go in the variable list regardless of how variable they are, because the holding torque itself carries the variability.

---

## What test evidence buys

The same actuator, no design change, at every level of evidence:

| Data source | FSv | FSf | Margin |
|---|---|---|---|
| Theory or analysis | 3.00 | 1.50 | +0.205 |
| Development test at extremes | 2.50 | 1.35 | +0.394 |
| Qualification test | 2.50 | 1.35 | +0.394 |
| Acceptance test, ambient | 2.50 | 1.35 | +0.394 |
| Acceptance test of flight hardware at extremes | 2.00 | 1.25 | +0.620 |
| One spring out, redundant springs | 1.00 | 1.00 | +1.47 |

**Three times the margin between the top row and the bottom, with no hardware change.** That is not the standard being lenient; it is uncertainty being retired by measurement.

Two cautions the standard attaches. The analysis factors are **not** a no-test option: verifying margin by test is required regardless. And the one-spring-out factors apply only to genuinely redundant springs in parallel with one failed, not to a single spring designed to tolerate partial failure.

---

## Gearboxes

The standard requires margin at **both** the input and the output of a torque multiplier.

The reason is that a gearbox is not a hundred per cent efficient and some resisting torques act before the multiplication rather than after, so basing a margin on the overall output alone can give a false impression of the true margin.

On a 50:1 reduction at 80 per cent efficiency the output margin is the worse of the two, and a design assessed only at the output would have looked comfortable.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Available torque | 4.50 N m |
| Fixed resisting, bearing and return spring | 1.15 N m |
| Variable resisting, seal and harness | 0.67 N m |
| Factored resisting at analysis | 3.735 N m |
| Static margin at analysis | +0.205 |
| Static margin at flight-article test | +0.620 |
| Required | 0 |

---

## Design rules of thumb

- **The threshold is zero.** Check any summary against the standard.
- **Put friction in the variable list.** It doubles its factor and it is usually the largest term.
- **Exclude incidental friction from holding torque.** The standard does.
- **Check both sides of a gearbox.**
- **Budget for the test.** It is cheaper than the design margin the analysis factors demand.

---

## Failure modes

**A margin threshold of 1.0.** Doubles the apparent conservatism and drives unnecessary redesign.

**Friction misfiled as fixed.** Halves its factor.

**Incidental friction counted as holding torque.** It is unreliable and the standard excludes it.

**Nameplate motor torque used as available torque.** It excludes magnetic and mechanical losses.

**A gearbox assessed at the output only.** Can hide a negative input margin.

**One-spring-out factors applied to a single spring.** They are for redundant springs in parallel.

---

## Tool interface

```python
from MechanismActuator import MechanismActuator

actuator = MechanismActuator()
actuator.setInputs({'availableTorque': 4.5,
                    'fixedTorques':    [0.80, 0.35],
                    'variableTorques': [0.42, 0.25],
                    'dataSource':      'theory or analysis',
                    'gearRatio':       50.0,
                    'gearEfficiency':  0.80})

margins    = actuator.checkMargins()
comparison = actuator.compareDataSources()
geared     = actuator.checkGearedMargins()
```

`checkMargins()` raises rather than reporting a negative margin.

---

## References

- NASA-STD-5017B, *Design and Development Requirements for Mechanisms*, section 4.3 and table 1
- [StandardsIndex](StandardsIndex.md), for the requirement numbers
- [ValidationReferences](ValidationReferences.md), for the threshold correction
