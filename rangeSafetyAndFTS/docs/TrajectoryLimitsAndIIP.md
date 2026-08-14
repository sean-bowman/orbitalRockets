[Home](../README.md) > Trajectory Limits and IIP

# Trajectory Limits and IIP

## Contents

- [Overview](#overview)
- [What the impact point is](#what-the-impact-point-is)
- [The solution](#the-solution)
- [It accelerates](#it-accelerates)
- [Then it ceases to exist](#then-it-ceases-to-exist)
- [The Earth turns underneath](#the-earth-turns-underneath)
- [Destruct lines and gates](#destruct-lines-and-gates)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Trajectory-based range safety is one calculation repeated every fraction of a second: where would the debris go if the vehicle failed now.

---

## What the impact point is

**The instantaneous impact point is where the vehicle would land if all thrust stopped at this instant** and the vehicle followed a free-flight trajectory to the ground.

It is not where the vehicle is going and it is not where the debris would land after a break-up, which disperses. It is the reference point that every trajectory limit is drawn against, and its virtue is that it is computable in real time from a state vector alone.

---

## The solution

The state defines a Keplerian orbit. Follow it forward to where it crosses the Earth's surface.

Specific angular momentum and energy come straight from the state:

```
h = r v cos(gamma)
eps = v**2/2 - mu/r
p = h**2/mu
e = sqrt(1 + 2 eps h**2 / mu**2)
```

The true anomaly at the current radius and at the Earth's surface follow from the orbit equation, and the range angle between them is the free-flight range. The time of flight comes from Kepler's equation through the eccentric and mean anomalies.

**It is exact for a vacuum trajectory over a spherical Earth**, which is the right fidelity: drag matters for the debris and not for the reference point, and the point of an impact point is that it is unambiguous rather than accurate.

---

## It accelerates

The property that decides how a launch is protected.

**Downrange distance grows faster than linearly with speed** at a fixed flight path angle, so the impact point moves slowly early in the ascent and extremely quickly late in it. In the worked case the drift rate grows from about 1 km per second of flight at twenty seconds to 55 km per second of flight at four and a half minutes: **a factor of fifty.**

Two consequences.

**A destruct line sized on an early drift rate is sized on the wrong number.** A line that gives ten seconds of warning early in the flight gives a fraction of a second late in it.

**And the reaction budget is set by the fastest part of the ascent**, not the average. The decision, the transmission and the ordinance function all have to fit inside the time the impact point takes to cross the corridor at its fastest.

---

## Then it ceases to exist

At orbital insertion the free-flight perigee rises above the Earth's surface. The trajectory no longer intersects the ground, and **there is no impact point at all.**

That is not a numerical failure and the class raises rather than returning a large number. **It is the moment the flight termination system stops having a job**, and it is the natural end of the range safety flight phase.

**The approach to it is asymptotic**, which matters operationally: in the last seconds before insertion the impact point runs away to the far side of the planet and then disappears. That is why the final range safety limits are expressed as a state condition rather than as a geographic line.

---

## The Earth turns underneath

The free-flight arc is computed in an inertial frame and the impact point is on a rotating surface.

**At the equator the ground moves at about 465 m/s**, so a five minute fall moves the impact point roughly 140 km west of where a non-rotating Earth would put it. That is a correction rather than a detail, and it is applied to where the point lands rather than as a term in the trajectory.

**It grows with time of flight**, so it is largest exactly where the impact point is furthest downrange and moving fastest.

---

## Destruct lines and gates

The geometry the impact point is checked against.

**A destruct line** is a boundary the impact point may not cross. Cross it and the vehicle is terminated. The lines are drawn to protect populated areas with a margin for the debris dispersion around the impact point and for the reaction time.

**A gate** is the inverse: a region the impact point must be inside at a given time. It catches an underperforming vehicle that has not gone anywhere dangerous but is not going where it should either.

**Both are derived from the [risk analysis](PublicRiskAnalysis.md) rather than drawn on a map.** The line sits where the casualty expectation of continuing exceeds the criterion, which means it depends on the population behind it, the debris the vehicle would make, and the reaction time.

**And the margin between the line and the population is the debris dispersion plus the reaction distance**, which is the impact point drift rate multiplied by the reaction time. At 55 km per second of drift and four seconds of reaction, that is 220 km of margin needed for the reaction alone.

---

## Worked numbers

A coastal ascent to low orbit.

| t [s] | Altitude | Speed | IIP downrange | Drift |
|---|---|---|---|---|
| 20 | 3 km | 200 m/s | 2 km | 1.1 km/s |
| 60 | 28 km | 1,000 m/s | 126 km | 5.1 km/s |
| 110 | 78 km | 2,600 m/s | 685 km | 11.5 km/s |
| 200 | 135 km | 5,000 m/s | 1,721 km | 12.7 km/s |
| 290 | 175 km | 7,300 m/s | 4,853 km | 55.0 km/s |
| 320 | 185 km | 7,800 m/s | **none** | |

| Quantity | Value |
|---|---|
| Drift growth across the ascent | 49x |
| Impact point ceases to exist | t+320 s |
| 900 km destruct line crossed | t+150 s at 10.1 km/s |
| Warning over the last 100 km | 9.9 s against a 4 s reaction |

---

## Design rules of thumb

- **Compute the impact point from the state**, not from a predicted trajectory.
- **Size destruct lines on the fastest drift rate**, not the average.
- **Budget the reaction distance as drift rate times reaction time.** It is hundreds of kilometres late in the flight.
- **Expect the impact point to disappear at insertion** and express the final limits as a state condition.
- **Apply the Earth rotation correction.** It is over a hundred kilometres on a long fall.
- **Derive the lines from the risk analysis**, not from a map.

---

## Failure modes

**A destruct line sized early in the ascent.** The drift rate grows by tens of times.

**A reaction budget taken as a constant.** It is a distance and the distance grows.

**An impact point expected through insertion.** It ceases to exist and that is physical.

**The Earth rotation left out.** Over a hundred kilometres on a five minute fall.

**A line drawn on a map rather than derived from risk.** It protects the wrong thing.

---

## Tool interface

```python
from ImpactPoint import ImpactPoint
from rangeSafetyUtils import ImpactPointError

point = ImpactPoint()
point.setInputs({'altitude': 78000.0, 'speed': 2600.0, 'flightPathAngle': 22.0,
                 'states': [{'time':  20.0, 'altitude':   3000.0, 'speed':  200.0,
                             'flightPathAngle': 80.0},
                            {'time': 110.0, 'altitude':  78000.0, 'speed': 2600.0,
                             'flightPathAngle': 22.0},
                            {'time': 200.0, 'altitude': 135000.0, 'speed': 5000.0,
                             'flightPathAngle':  7.0}],
                 'destructRange': 900000.0,
                 'reactionTime':  4.0})

impact = point.calculateImpactPoint()
trace  = point.traceAscent()
check  = point.checkDestructLine()

# At insertion the free-flight perigee clears the surface and there is no impact point.
try:
    point.calculateImpactPoint(altitude = 185000.0, speed = 7800.0, flightPathAngle = 0.3)
except ImpactPointError:
    pass
```

---

## References

- [PublicRiskAnalysis](PublicRiskAnalysis.md), which is where the lines come from
- [EntryAerodynamics](../../recoveryAndReusability/docs/EntryAerodynamics.md), for the ballistic descent of one body
- [TrajectoryBasics](../../vehicleArchitecture/docs/TrajectoryBasics.md)
