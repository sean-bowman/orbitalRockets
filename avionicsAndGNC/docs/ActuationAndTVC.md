[Home](../README.md) > Actuation and TVC

# Actuation and TVC

## Contents

- [Overview](#overview)
- [The vehicle is unstable](#the-vehicle-is-unstable)
- [Three disturbances](#three-disturbances)
- [The trim allowance](#the-trim-allowance)
- [The rate is the other half](#the-rate-is-the-other-half)
- [Arrangements](#arrangements)
- [Reaction control](#reaction-control)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Thrust vector control is the only thing holding a launch vehicle pointed in the right direction. This document is about how much authority it needs and which disturbance decides.

---

## The vehicle is unstable

A launch vehicle has its centre of pressure ahead of its centre of gravity, so an angle of attack produces a moment that **increases** the angle of attack.

That is not a design flaw, it is a consequence of putting the heavy engines at the back and a fairing at the front, and fixing it aerodynamically would mean fins large enough to cost more in mass and drag than the control system does.

**So the control system is not improving a stable vehicle, it is preventing a divergence.** A control failure at dynamic pressure is immediate rather than gradual, which is the practical difference between an unstable airframe and a stable one.

The library refuses a positive static margin on the grounds that it is almost always a sign convention error, and that guard exists because the convention differs between sources.

---

## Three disturbances

They have different origins and different time histories, which is why the governing one changes through the flight.

**Thrust misalignment.** The thrust vector is not exactly along the axis, from engine mounting tolerance and from vector uncertainty within the engine itself. The moment is proportional to thrust, so it is present the whole burn and largest when the thrust is largest.

**Centre of gravity offset.** The centre of gravity is not exactly on the thrust axis, from mass properties tolerance and from propellant distribution. Also proportional to thrust.

**Aerodynamic.** The unstable airframe at an angle of attack. Proportional to dynamic pressure and angle of attack, so it peaks at max-Q and vanishes outside the atmosphere. **Wind is how this becomes a sizing case**, because wind appears as angle of attack and a gust appears as more of it.

On the reference vehicle:

| Condition | Total | Governing |
|---|---|---|
| Liftoff | 3.5 kN m | thrust misalignment |
| Max-Q | 17.0 kN m | aerodynamic |
| Max-Q with gust | 30.4 kN m | aerodynamic |
| Above the atmosphere | 3.5 kN m | thrust misalignment |

**A gimbal sized on one condition is sized on the wrong one for most of the flight**, and the two conditions do not even have the same governing physics.

Note that these are added rather than combined in quadrature, because they can align and there is no statistical argument that they will not.

---

## The trim allowance

The gimbal has to hold the steady disturbances **and** have authority left to respond with.

The library allows a third of the range for trim. That is a convention rather than a standard, and the reasoning behind it is not: **a vehicle trimmed at its stop cannot manoeuvre**, and a vehicle that cannot manoeuvre is not marginal, it is uncontrolled.

On the reference vehicle at max-Q the trim takes 1.62 degrees of 8, leaving 6.38. With an 8 degree gust it exceeds the allowance and the library refuses it, which is the case a vehicle is actually lost in.

---

## The rate is the other half

The angle says whether the vehicle can be held. The rate says whether it can be held *in time*, and it is the requirement that is usually short.

A loop closing at frequency `f` with command amplitude `A` needs a peak gimbal rate of `2 pi f A`. On the reference vehicle, commanding the remaining 6.38 degrees at 1 Hz needs **40 degrees per second**.

**An actuator slower than that rate-limits**, and rate limiting is a nonlinearity. The gain and phase margins are linear measures and they say nothing about it: **a loop with good margins on paper goes unstable in flight through exactly this**, and it does so suddenly rather than gradually.

That makes actuator rate a stability requirement wearing the clothes of a performance one.

---

## Arrangements

| Arrangement | Range | Axes | Roll from |
|---|---|---|---|
| Single gimballed engine | 8 deg | 2 | something else |
| Gimballed cluster | 6 deg | 3 | differential gimbal |
| Fixed engine with RCS | 0 | 3 | reaction control |

**A single gimballed engine cannot produce roll**, which is the thing most often forgotten about it: the gimbal gives pitch and yaw and roll needs a separate effector, usually reaction control or vernier thrusters.

A cluster gets roll from differential gimbal for free, which is a real architectural advantage of multiple engines that has nothing to do with thrust or engine-out.

---

## Reaction control

Named rather than modelled, because the sizing couples directly into [fluidSystems](../../fluidSystems/) rather than into anything here.

**In vacuum it is adequate for everything.** With no aerodynamic disturbance the only moments are thrust misalignment during a burn and disturbance torques during coast, and both are small.

**In atmosphere it is not adequate for anything.** The aerodynamic moment on an unstable airframe at dynamic pressure is orders of magnitude beyond what a practical reaction control system produces.

The sizing question is a **duty cycle** question rather than a thrust question: the propellant is set by how many pulses over how long, which is a mission profile, and the interface to fluid systems is a total impulse and a minimum impulse bit.

---

## Worked numbers

The reference vehicle at max-Q.

| Quantity | Value |
|---|---|
| Thrust | 100 kN |
| Gimbal arm | 6.0 m |
| Static margin | -0.06 |
| Dynamic pressure | 35 kPa |
| Wind angle of attack | 4 deg |
| Disturbance total | 17.0 kN m |
| Trim angle | 1.62 deg |
| Trim allowance | 2.64 deg |
| Remaining for control | 6.38 deg |
| Rate needed at 1 Hz | 40 deg/s |

---

## Design rules of thumb

- **Check more than one flight condition.** The governing disturbance changes.
- **Add the steady disturbances**, do not combine them in quadrature. They can align.
- **Keep the trim inside a third of the range.** The rest is for controlling.
- **Specify the actuator rate.** It is a stability requirement, not a performance one.
- **Remember roll.** A single gimballed engine does not produce it.

---

## Failure modes

**A gimbal sized at max-Q only.** Wrong governing disturbance for most of the flight.

**A vehicle trimmed near its stop.** Cannot respond, and the library refuses it.

**An actuator sized on angle alone.** Rate limits, and the linear margins do not see it.

**A gust case not analysed.** It is the case the vehicle is lost in.

**Roll authority assumed from a single gimbal.** It is not there.

---

## Tool interface

```python
from ControlAuthority import ControlAuthority

control = ControlAuthority()
control.setInputs({'thrust':            100.0e3,
                   'gimbalArm':         6.0,
                   'arrangement':       'single gimballed engine',
                   'dynamicPressure':   35000.0,
                   'referenceArea':     2.545,
                   'staticMargin':      -0.06,
                   'vehicleLength':     18.0,
                   'vehicleDiameter':   1.8,
                   'windAngleOfAttack': 4.0,
                   'bendingFrequency':  6.0})

disturbances = control.calculateDisturbances()
authority    = control.checkAuthority()
rate         = control.requiredActuatorRate(controlFrequency = 1.0)
```

A positive static margin raises, because a launch vehicle is unstable and a positive value is almost always a sign convention error.

---

## References

- Greensite, *Analysis and Design of Space Vehicle Flight Control Systems*
- Wie, *Space Vehicle Dynamics and Control*
- [ControlLawsAndStability](ControlLawsAndStability.md), for what the rate does to the loop
- [fluidSystems](../../fluidSystems/), for the reaction control propellant
