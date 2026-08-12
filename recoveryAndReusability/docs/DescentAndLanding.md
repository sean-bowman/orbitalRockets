[Home](../README.md) > Descent and Landing

# Descent and Landing

## Contents

- [Overview](#overview)
- [Propulsive against parachute](#propulsive-against-parachute)
- [Touchdown is an energy problem](#touchdown-is-an-energy-problem)
- [Absorbers](#absorbers)
- [Tipover](#tipover)
- [The droneship case](#the-droneship-case)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The landing is the visible part of recovery and the cheapest part to get right. It is also where the trade between a light single-use absorber and a heavier reusable one is decided, and that is a reuse decision rather than a landing one.

---

## Propulsive against parachute

Two ways down, and the choice is made further upstream than it looks.

**A parachute costs no reserve propellant** and it costs a large mass of canopy, lines and deployment hardware, plus a splashdown or a mid-air retrieval. Its accuracy is poor, its terminal velocity is set by drag area, and **salt water is the refurbishment problem** it substitutes for the propellant one.

**A propulsive landing costs reserve propellant**, which is by far the larger payload penalty, and it buys precision, a dry vehicle and a landing on a prepared surface. It also demands an engine that throttles deep enough to hover a nearly empty stage, which is a propulsion requirement rather than a recovery one and it is often the binding one. See [ThrottlingAndMixtureRatio](../../propulsion/docs/ThrottlingAndMixtureRatio.md).

**The deciding question is what the salt water does to the hardware.** A stage that can be flown again after immersion has a cheap recovery mode available; one that cannot has to land dry, and the reserve propellant follows from that rather than from a preference.

---

## Touchdown is an energy problem

The vehicle arrives with kinetic energy and the legs absorb it over a stroke.

```
n = v**2 / (2 g s eta) + 1
```

with `s` the usable stroke and `eta` the absorber efficiency, the fraction of the force-stroke rectangle it actually fills. The plus one is the vehicle's own weight, which the legs carry once the motion stops.

**The load factor is inversely proportional to the stroke.** Doubling the stroke halves the load, and stroke is cheap in mass relative to the structure that reacts the load. **A leg design that trades the other way has the conversation backwards.**

Two things follow.

**The sink rate matters as its square**, so a control system that arrives a metre per second faster than planned does not cost a small margin.

**And the leg reacts the load, so the load ends up in the thrust structure**, which was already the most heavily loaded part of the stage. Landing loads are a structural design case on hardware that exists for a different reason.

---

## Absorbers

| Absorber | Efficiency | Reusable | Why |
|---|---|---|---|
| Crushable honeycomb | 0.80 | no | nearly constant force through the crush |
| Crushable aluminium | 0.70 | no | cheaper and less uniform |
| Hydraulic damper | 0.55 | yes | force follows velocity and falls as the vehicle stops |
| Pneumatic strut | 0.45 | yes | springs back, which is a rebound problem as well |

**The reusable ones are the inefficient ones and that is not a coincidence.** A crushable core fills its rectangle because it fails at a constant load; a damper cannot, because its force is proportional to a velocity that is going to zero by definition.

**So a reusable absorber is bought back with stroke**, about one and a half times as much for the same load factor. On a vehicle designed for many flights that is the right trade: stroke costs a little mass once and replacing a crushed core costs a refurbishment operation every flight. See [RefurbishmentProcess](RefurbishmentProcess.md).

**A capsule flying once takes the honeycomb**, and it is the correct answer for that vehicle.

---

## Tipover

The other landing failure, and it is geometry rather than energy.

The vehicle tips if its centre of gravity passes outside the leg footprint. The static margin is

```
theta = arctan( footprint radius / centre of gravity height )
```

and three things eat into it, additively.

**Ground slope** subtracts directly.

**Horizontal velocity at touchdown**, through the rotation its kinetic energy produces against the potential energy of lifting the centre of gravity to the tipping edge.

**A leg that does not lock**, which removes a corner of the footprint entirely and is the reason legs have a positive lock and a verification of it.

**A launch vehicle is a bad shape for this.** The static angle falls as the arctangent of footprint over height, so a slender stage runs out of margin quickly: 39 degrees at a nine metre footprint and an eleven metre centre of gravity, nine degrees at three times the height, and nothing at ten times. **The footprint is what buys it back**, which is why landing legs are long and why they fold.

---

## The droneship case

Worth separating because it is harder than a pad landing by more than either term suggests.

A moving deck has a slope that is not zero and is not known in advance, and it demands a horizontal rate match against a ship that is itself moving. **Both terms subtract from the same tipover margin and they add to each other**, so a case that clears comfortably on land can be marginal at sea.

It is also where the landing accuracy requirement is set: the deck is small, and the vehicle has one attempt.

**This domain takes the deck slope and the horizontal rate as inputs.** The sea state that produces them is a naval architecture problem, and the guidance that closes the position is one [avionicsAndGNC](../../avionicsAndGNC/docs/GuidanceAlgorithms.md) declined for stated reasons.

---

## Worked numbers

A 26 t stage at 2 m/s onto 450 mm of hydraulic damper, four legs.

| Quantity | Value |
|---|---|
| Load factor | 1.82 g |
| Force per leg | 116 kN |
| Structural limit | 4.5 g, margin 147 % |
| Stroke needed for the limit | 106 mm |
| Honeycomb at the same stroke | 1.57 g |
| Damper stroke for honeycomb parity | 655 mm, 1.5x |
| Static tipover angle | 39.3 deg |
| Margin on a 2 deg pad | 37.1 deg |
| Margin on a 6 deg deck at 1.5 m/s | 31.9 deg |

**The touchdown is not the demanding case here**, which is the usual finding on a propulsively landed stage: the sink rate is controlled and the margin is large. The demanding case is the one where the control system does not deliver the sink rate it promised.

---

## Design rules of thumb

- **Buy load factor with stroke, not with structure.** It is inversely proportional and stroke is cheap.
- **Pick the absorber by flight count**, not by mass.
- **Design the footprint for tipover**, because the static angle falls fast with height.
- **Treat slope, horizontal rate and a failed leg lock as additive.**
- **Check that the engine throttles deep enough to hover an empty stage** before committing to a propulsive landing.
- **Decide what salt water does to the hardware** before choosing between a parachute and a burn.

---

## Failure modes

**A load factor computed without the absorber efficiency.** A damper fills barely half its rectangle.

**A crushable core on a vehicle designed for many flights.** A refurbishment operation every landing.

**Tipover computed statically.** Slope, horizontal rate and a failed lock all subtract from the same margin.

**A droneship case sized on the pad case.** Two terms subtract instead of none.

**A sink rate treated as nominal.** The load factor goes as its square.

---

## Tool interface

```python
from LandingLoads import LandingLoads

loads = LandingLoads()
loads.setInputs({'landedMass':      26000.0,
                 'sinkRate':        2.0,
                 'horizontalRate':  0.5,
                 'stroke':          0.45,
                 'absorber':        'hydraulicDamper',
                 'legCount':        4,
                 'footprintRadius': 9.0,
                 'centreOfGravity': 11.0,
                 'groundSlope':     2.0,
                 'limitLoadFactor': 4.5})

touchdown = loads.calculateLoadFactor()      # raises above the structural limit
required  = loads.requiredStroke(4.5)
absorbers = loads.compareAbsorbers()
tipover   = loads.calculateTipover()         # raises at or below one degree of margin
```

Both failures raise rather than reporting a negative margin, because a vehicle that exceeds its load factor or tips over is lost rather than degraded.

---

## References

- [SpringsAndEnergyStorage](../../mechanismsAndSeparation/docs/SpringsAndEnergyStorage.md), for the stored energy side
- [ThrottlingAndMixtureRatio](../../propulsion/docs/ThrottlingAndMixtureRatio.md), for the hover requirement
- [StaticAndQuasiStaticLoads](../../environmentsAndLoads/docs/StaticAndQuasiStaticLoads.md)
