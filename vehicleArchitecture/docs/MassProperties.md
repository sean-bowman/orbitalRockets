[Home](../README.md) > Mass Properties

# Mass Properties

## Contents

- [Overview](#overview)
- [Centre of gravity on the prediction, not the estimate](#centre-of-gravity-on-the-prediction-not-the-estimate)
- [The CG moves through the burn](#the-cg-moves-through-the-burn)
- [Inertia](#inertia)
- [Tracking and re-baselining](#tracking-and-re-baselining)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Mass properties are the mass budget with positions attached, and the positions are what the control system consumes.

---

## Centre of gravity on the prediction, not the estimate

**Growth allowance is not distributed evenly across a vehicle**, because maturity is not distributed evenly. The harness at 25 per cent and the actuators at 15 per cent are in different places, so the centre of gravity computed on estimates is not the centre of gravity computed on predictions.

[MassBudget](MassProperties.md) computes it on predicted masses and reports the shift, because a control system sized on an estimate CG is sized on a number that is going to move.

On the worked example's avionics assembly the shift is 13 mm, which is small. It is small **there**; the same calculation on a stage where the engines are mature and the payload adapter is not can move it much further.

---

## The CG moves through the burn

The largest CG excursion on a launch vehicle is not estimating growth, it is the propellant leaving.

A stage at burnout has lost most of its mass from the tanks, so the CG moves toward whatever is left, which is the engines at the bottom and the payload at the top. **The CG travel through a burn is metres on a large stage**, and the control system has to be stable across all of it.

Two consequences.

**The worst case for control is not the worst case for loads.** Loads peak near max-Q with tanks nearly full; control margin is usually worst near burnout.

**Slosh moves the effective CG dynamically**, and it is a stability problem rather than a mass properties one. It belongs to [fluidSystems](../../fluidSystems/) and to the control design, and it is not modelled here.

---

## Inertia

[MassBudget](MassProperties.md) computes the axial second moment about the centre of gravity, which is the spread of mass along the vehicle.

That is the term that dominates pitch and yaw inertia on a slender vehicle, and it is adequate for a first control sizing. **It is not a full inertia tensor**: there are no radial positions in the line items, so roll inertia and products of inertia are not available.

That is a stated limit rather than an oversight. A full mass properties model needs a three-dimensional position per item and a coordinate convention, and this domain carries a station only.

---

## Tracking and re-baselining

A mass budget is a document with a date on it, and the useful thing is the sequence rather than any one issue.

**Track the predicted mass, not the estimate.** A programme whose estimate is flat while its maturity rises is a programme whose predicted mass is falling, which is the healthy shape and is invisible if only the estimate is reported.

**Re-baseline when maturity changes, not when the number changes.** Moving an item from calculated to preliminary drops its allowance from 15 to 10 per cent and the predicted mass falls without any hardware changing. That is legitimate and it has to be recorded as a maturity change rather than as a mass saving, or the same saving gets claimed twice.

---

## Worked numbers

The avionics assembly.

| Quantity | Value |
|---|---|
| Total predicted mass | 203.2 kg |
| Centre of gravity on predicted masses | 1.956 m |
| Centre of gravity on estimates | 1.943 m |
| Shift from growth | 13.1 mm |
| Axial second moment about the CG | 286 kg m^2 |

---

## Design rules of thumb

- **Compute the CG on predicted masses.** Growth is not evenly distributed.
- **Check control stability at burnout**, not only at max-Q.
- **Record a maturity change as a maturity change**, not as a mass saving.
- **Track the predicted mass over time.** A flat estimate with rising maturity is a falling prediction.
- **Get a real inertia tensor before sizing a control system.** A station is not a position.

---

## Failure modes

**CG from estimates.** It moves as the estimates mature and the control system does not.

**Control sized at one flight condition.** The CG travels metres through a burn.

**A maturity change claimed as a mass saving.** The same saving gets counted twice.

**An axial second moment mistaken for an inertia tensor.** No radial positions, no roll inertia.

---

## Tool interface

```python
from MassBudget import MassBudget

budget = MassBudget()
budget.setInputs({'items': [{'name': 'batteries', 'mass': 46.0,
                             'maturity': 'calculated', 'station': 2.8}]})

centre = budget.calculateCentreOfGravity()
```

Every item needs a station or the call raises, because a centre of gravity computed from a subset is worse than none.

---

## References

- [MassFractionsAndEstimating](MassFractionsAndEstimating.md), for the growth allowance this positions
- AIAA S-120 and the ANSI/AIAA mass properties standards
- [environmentsAndLoads](../../environmentsAndLoads/docs/), for the flight conditions the properties are consumed at
