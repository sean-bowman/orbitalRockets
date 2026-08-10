[Home](../README.md) > Deployment Mechanisms

# Deployment Mechanisms

## Contents

- [Overview](#overview)
- [The torsion spring arrives weakest](#the-torsion-spring-arrives-weakest)
- [The latch pays quadratically](#the-latch-pays-quadratically)
- [The damper that eats its own justification](#the-damper-that-eats-its-own-justification)
- [Latches and the indication problem](#latches-and-the-indication-problem)
- [Mechanical stops](#mechanical-stops)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A hinged deployable is a spring, an inertia, a travel and a latch. Every one of those four interacts with the others, and the interactions are where the design lives.

---

## The torsion spring arrives weakest

A torsion spring unwinds as it deploys, so its torque falls with angle:

```
T(theta) = T_stowed - k theta
```

**A spring sized on its stowed torque is sized at the easiest point of its travel.** The design case is the end of travel, where the spring is weakest and where a latch may be adding its own resistance.

[DeploymentKinematics](DeploymentMechanisms.md) **refuses** a case that stalls, because a deployable that stops halfway is a failed mission rather than a slow one, and it names the falling spring torque in the message because that is the usual cause.

---

## The latch pays quadratically

The panel arrives with kinetic energy:

```
E = 0.5 I omega^2
```

and all of it goes into the latch, the hinge and the structure behind them.

**The energy goes as the square of the arrival rate**, so a spring chosen with generous deployment margin arrives with far more energy than one chosen to just deploy. On the reference panel, doubling the spring torque roughly doubles the arrival rate and quadruples the latch energy.

So **the deployment margin requirement and the latch load requirement pull directly against each other**, and neither can be satisfied by moving the spring alone.

---

## The damper that eats its own justification

A viscous damper resolves the conflict. It costs deployment time, it costs a component that has to work after storage at temperature, and it costs something less obvious.

**NASA-STD-5017B lists damper drag among the resisting torques a margin calculation has to include.** So the damper that protects the latch appears in the denominator of the margin equation that justified the spring, and adding it reduces the margin it was bought to enable.

On the reference panel, holding the latch to 1.0 J takes a damper of 2.21 N m s per radian, cutting the impact energy by 74 per cent and extending the deployment from 1.60 s to 2.17 s.

That is the trade in three numbers, and the fourth number, the margin the damper costs, is why deployables are iterated rather than sized.

---

## Latches and the indication problem

A latch has to engage, hold, and be **known** to have engaged.

NASA-STD-5017B requires a direct indication of a mechanism's critical states, and it is explicit about what direct means. Measuring the position of a component in a latch drivetrain is an **indirect** indication that can be wrong if the drivetrain has failed structurally or has enough backlash to let the shaft turn while the latch remains disengaged. **Measuring the latch pawl itself is direct.**

That distinction costs a sensor and a harness and it is the difference between knowing and inferring.

---

## Mechanical stops

The standard requires non-jamming mechanical stops wherever over-travel would be detrimental, and it requires a positive margin with full design factors under the worst-case transient loads from stop impact.

Two things follow. **A software or limit-switch stop is not a mechanical stop**, and the standard says so: soft stops can be unreliable. And the impact against the stop is a dynamic event, so a static analysis of it can be unconservative.

The same energy calculation applies as for the latch, and it applies at the maximum speed the mechanism can reach combined with the stall torque of whatever is driving it.

---

## Worked numbers

The reference panel, 90 degrees of travel, 2.5 kg m^2.

| Quantity | Undamped | Damped |
|---|---|---|
| Spring torque, stowed | 4.00 N m | 4.00 N m |
| Spring rate | 1.20 N m/rad | 1.20 N m/rad |
| Damping | 0 | 2.21 N m s/rad |
| Deployment time | 1.60 s | 2.17 s |
| Arrival rate | 100.7 deg/s | 51.2 deg/s |
| Latch impact energy | 3.86 J | 1.00 J |

---

## Design rules of thumb

- **Size the spring at the end of travel**, where it is weakest.
- **Size the latch before finalising the spring.** The energy is quadratic in arrival rate.
- **Count the damper in the margin.** It resists the deployment it protects.
- **Sense the pawl, not the drivetrain.** Direct indication is a different claim.
- **Fit a mechanical stop.** A limit switch is not one.

---

## Failure modes

**A spring sized on stowed torque.** Stalls near the end of travel, where the spring is weakest.

**A latch sized after the spring.** The energy is quadratic and the surprise is large.

**A damper omitted from the margin calculation.** The standard requires it and it is the term most often forgotten.

**Latch state inferred from the drivetrain.** Backlash or a structural failure makes it wrong.

**A stop impact analysed statically.** The contact is usually fast enough to need a dynamic analysis.

---

## Tool interface

```python
import numpy as np
from DeploymentKinematics import DeploymentKinematics

panel = DeploymentKinematics()
panel.setInputs({'springTorque':    4.0,
                 'springRate':      1.2,
                 'inertia':         2.5,
                 'travel':          np.radians(90.0),
                 'resistingTorque': 0.6})

impact = panel.latchImpact()
sizing = panel.sizeDamper(energyLimit = 1.0)
```

`travel` is in radians, and a value above a full turn raises on the assumption it was passed in degrees.

---

## References

- NASA-STD-5017B, sections 4.7 on indication of status and 4.8 on structural requirements
- [ActuatorsAndDrives](ActuatorsAndDrives.md), for the margin the damper reduces
- Conley, *Space Vehicle Mechanisms: Elements of Successful Design*
