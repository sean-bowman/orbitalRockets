[Home](../README.md) > Flow Separation

# Flow Separation

## Contents

- [Overview](#overview)
- [Two criteria that disagree](#two-criteria-that-disagree)
- [What the disagreement is worth](#what-the-disagreement-is-worth)
- [Side loads](#side-loads)
- [The start transient](#the-start-transient)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

When the exit pressure falls far enough below ambient, the boundary layer cannot negotiate the adverse gradient and detaches from the wall.

**It is not a performance penalty.** Past the separation point the flow is unsteady, the separation line moves, and the nozzle sees a lateral load it was not designed for. Separation has destroyed hardware, and it is the reason a vacuum optimised nozzle cannot simply be lit on the pad.

---

## Two criteria that disagree

Both are curve fits to test data and neither is a physical limit.

**Summerfield** puts the threshold at a fixed fraction of ambient:

```
Pe < 0.4 Pa
```

**Schmucker** makes it depend on the pressure ratio, which matters because a launch vehicle nozzle runs at pressure ratios of a hundred and Summerfield was fitted at rather less:

```
Pe / Pa = 0.667 (Pc / Pa)^-0.2
```

At a 10 MPa chamber at sea level, Summerfield gives a threshold of 40.5 kPa and Schmucker gives 27.0. **Schmucker is the less conservative of the two at launch vehicle conditions**, and it permits a larger area ratio:

| Criterion | Threshold | Permitted area ratio |
|---|---|---|
| Summerfield | 40.5 kPa | 21.42 |
| Schmucker | 27.0 kPa | 29.17 |

**A 36 per cent difference in the permitted expansion.** At an area ratio of 25 the two disagree about whether the nozzle separates at all.

The library reports both rather than picking one, because picking one hides a design decision that rests on which curve fit is believed.

---

## What the disagreement is worth

Less than it looks, and this is the useful finding.

Moving the design point from Summerfield's limit to Schmucker's, holding the same five per cent margin, changes the burn-averaged specific impulse of the reference booster by **0.45 seconds**, which is 0.15 per cent.

**A 36 per cent change in a design variable moves the answer by a seventh of a per cent**, because the area ratio optimum is broad. The [propulsion hub](../../docs/PerformanceFundamentals.md) found the same flatness from the other direction: everything from an area ratio of 20 to 28 is within half a second of the burn-average optimum.

It does change one conclusion. The hub found its burn-average optimum at an area ratio of 25.75 and **rejected it, because Summerfield said it separates.** Under Schmucker it does not. So the hub's unreachable optimum is reachable, and reaching it is worth half a second.

That is worth knowing before anyone argues over which correlation to believe.

---

## Side loads

The reason separation is a structural problem rather than a performance one.

A separated nozzle has an attached region and a separated region, and the boundary between them is not axisymmetric and does not hold still. The pressure distribution is therefore asymmetric and unsteady, and it produces a lateral force and a bending moment at the throat.

**That load can exceed the steady gimbal load**, and it is unsteady, so it is a fatigue driver as well as a strength case. It has bent nozzle extensions and damaged gimbal actuators.

The load is largest during **transients**, when the separation line is sweeping along the nozzle rather than sitting still.

---

## The start transient

The worst case for separation on any engine with a large area ratio, and it is unavoidable.

At the instant of start the chamber pressure is ambient and rises to full. The nozzle is therefore **fully separated at the beginning of every start**, and the separation line sweeps from near the throat down to the exit as the chamber comes up.

Three consequences.

**Every start is a side load event**, and it is a structural design case rather than an anomaly.

**A faster start sweeps the line faster**, which reduces the dwell at any one station and is generally better.

**The nozzle has to survive it at sea level**, which is what limits the area ratio of a first stage engine far more directly than the steady state condition does. See [AreaRatioSelection](AreaRatioSelection.md).

An upper stage engine started in vacuum never sees this, which is part of why upper stage area ratios are what they are.

---

## Design rules of thumb

- **Report both criteria.** Choosing one hides a design decision.
- **Hold margin off whichever is used.** They are correlations with real scatter.
- **Treat separation as a structural case, not a performance one.**
- **Design for a fully separated start.** It happens every time.
- **Expect the largest side load during transients**, not in steady separated flow.
- **Do not spend long arguing about the criterion.** It is worth half a second.

---

## Failure modes

**Separation treated as a performance loss.** The attached-flow relations return a thrust coefficient and the real problem is a side load.

**One criterion reported.** The design rests on a choice nobody was told about.

**The start transient not considered.** Every start is fully separated at the beginning.

**Side load omitted from the gimbal load case.** It can exceed the steady load and it is unsteady.

**A vacuum area ratio lit at sea level.** The nozzle separates and the side load is the problem.

---

## Worked numbers

The reference booster, 10 MPa chamber, sea level.

| Quantity | Value |
|---|---|
| Summerfield threshold | 40.5 kPa |
| Schmucker threshold | 27.0 kPa |
| Summerfield permitted area ratio | 21.42 |
| Schmucker permitted area ratio | 29.17 |
| Difference | 36 % |
| Worth in burn-averaged impulse | 0.45 s, 0.15 % |
| Hub's rejected optimum | 25.75, forbidden by Summerfield and permitted by Schmucker |

---

## Standards

| Standard | What it gives you |
|---|---|
| NASA SP-8120 | Liquid rocket engine nozzles, including the side load discussion |
| Summerfield, Foster and Swan | The original separation correlation |
| Schmucker | The pressure ratio dependent refinement |
| NASA-STD-5012 | Strength and life assessment, for the side load as a fatigue case |

---

## Tool interface

```python
from NozzleLosses import NozzleLosses

losses = NozzleLosses()
losses.setInputs({'combination':     'LOX/RP-1',
                  'areaRatio':       25.0,
                  'chamberPressure': 10.0e6,
                  'ambientPressure': 101325.0})

separation = losses.checkSeparation()

print(separation['separatedBySummerfield'], separation['separatedBySchmucker'])
print(separation['criteriaAgree'])
print(separation['summerfieldLimit'], separation['schmuckerLimit'])
```

A zero ambient pressure is refused, because a separation criterion has no meaning in vacuum.

---

## References

- Summerfield, Foster and Swan, *Flow separation in overexpanded supersonic exhaust nozzles*
- Schmucker, *Flow processes in overexpanded chemical rocket nozzles*
- NASA SP-8120, *Liquid rocket engine nozzles*
- Frey and Hagemann, *Status of flow separation prediction in rocket nozzles*
- Ostlund and Muhammad-Klingmann, *Supersonic flow separation with application to rocket engine nozzles*
