[Home](../README.md) > Injector Design

# Injector Design

## Contents

- [Overview](#overview)
- [Two jobs that pull against each other](#two-jobs-that-pull-against-each-other)
- [Element types](#element-types)
- [Orifice sizing](#orifice-sizing)
- [Momentum ratio is not a free choice](#momentum-ratio-is-not-a-free-choice)
- [Stiffness](#stiffness)
- [The outer row](#the-outer-row)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [What is not validated](#what-is-not-validated)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The injector decides how well the engine burns, whether the chamber survives, and whether the whole thing couples into an oscillation that destroys it. It is the component with the most ways to be wrong and the least analytical support for getting it right, which is why injector development is dominated by test rather than by calculation.

Nothing in this document predicts c* efficiency. What it does is set out the parameters that decide it, the ones that are forced rather than chosen, and the trade that runs through all of them.

---

## Two jobs that pull against each other

**Mix the propellants well enough to burn completely in the residence time available.** That is what c* efficiency measures, and the [propulsion hub](../../docs/PerformanceFundamentals.md) shows why it is the injector's number: nothing downstream of the throat can change it.

**Do not do that next to the wall.** An element that mixes well produces a hot core, and an element that mixes well against the wall produces a hot wall and then a hole.

**An injector that is uniform from centre to wall is either mixing badly everywhere or destroying its chamber**, and which one depends on how good it is. That is the whole difficulty, and it is why essentially every engine runs a different element pattern in its outer row and accepts the efficiency loss.

The third job is not to couple with anything, which is [CombustionStability](CombustionStability.md).

---

## Element types

| Element | `Cd` | Mixing | Wall tolerant | Character |
|---|---|---|---|---|
| Like-on-like doublet | 0.75 | 0.85 | Yes | Each propellant impinges on itself. Poor mixing, very forgiving |
| Unlike impinging doublet | 0.80 | 1.00 | **No** | The workhorse. Good mixing, and it will find the wall |
| Unlike impinging triplet | 0.78 | 1.10 | **No** | Two oxidiser on one fuel. Better mixing, less tolerant still |
| Coaxial shear | 0.85 | 0.90 | Yes | The cryogenic standard. Needs a large velocity ratio |
| Coaxial swirl | 0.70 | 1.05 | Yes | Swirl atomises at lower velocity ratio, for more pressure drop |
| Pintle | 0.80 | 0.95 | Yes | One element, variable area, inherently deep throttling and stable |

**Mixing quality and wall tolerance are close to opposites across this set.** The best mixing element in the table is not wall tolerant, and every wall tolerant one mixes worse. That is not a coincidence in the data, it is the same physics stated twice.

The mixing quality figures are a **ranking and not a measurement**. They order the element types and they must not be used to predict a c* efficiency. That is registered as unvalidated.

**The pintle is the outlier and deserves its own note.** It is a single element with a variable injection area, so it holds pressure drop roughly constant as the flow falls instead of letting it drop as the square. That makes it inherently deep-throttling, which is why it appears on every engine that has to land. It is also inherently stable, because there is no pattern of discrete elements to support a transverse mode.

---

## Orifice sizing

```
mdot = Cd A sqrt(2 rho dP)
```

Solved for area, then diameter, per element. The element count is an input because it is a packaging decision as much as a flow one: the elements have to fit on the face with enough land between them to drill and enough to stop the pattern merging.

Two practical bounds:

**Below about 0.4 mm** the holes are hard to drill repeatably, hard to keep clean, and a single particle blocks one. A blocked element is a local mixture ratio excursion, which is a local hot spot.

**Above about 2 mm** the jet is coarse and atomisation suffers. The drop size scales with the orifice, and a large drop that has not evaporated by the throat has not burnt.

For the [worked example](../codeInterface.py) at 160 elements and 20 per cent stiffness: oxidiser 1.97 mm, fuel 1.34 mm. Both inside the band, and the oxidiser is close enough to the ceiling that a lower element count would not be usable.

---

## Momentum ratio is not a free choice

The oxidiser to fuel stream momentum ratio decides where the mixed core sits. Near one the streams penetrate each other evenly and the mixing plane is where the geometry put it. Far from one the stronger stream sweeps the weaker aside and the mixing plane moves, which on an outer row element means it moves toward the wall.

The recommended band is roughly 0.7 to 1.5. Now the part that matters:

**At equal pressure drop on both circuits, the momentum ratio is forced.**

```
V ~ sqrt(dP / rho)      so      J = MR sqrt(rho_fuel / rho_ox)
```

For LOX/RP-1 at a mixture ratio of 2.56 that is **2.16**, well outside the band, before any design choice has been made. The same is true of every combination with a dense oxidiser and a light fuel, which is all of them.

**The consequence is that a single injector stiffness describes neither circuit.** Real injectors run different pressure drops on the two sides, and the fuel side is normally the higher. Bringing the worked example to 1.5 needs the fuel side at 67.4 m/s, a 2.88 MPa drop against the oxidiser side's 2.00 MPa.

This is the sort of result that is obvious once seen and invisible until then, and a tool that takes one stiffness number will produce an out-of-band momentum ratio every time without saying why.

---

## Stiffness

Injector pressure drop as a fraction of chamber pressure. It is what decouples the feed system from the chamber: when it is high, a chamber pressure oscillation cannot propagate upstream and modulate the flow feeding it.

| Value | Meaning |
|---|---|
| Below 5 % | Chug territory. The feed system and chamber are one coupled oscillator |
| 15 to 25 % | The recommended design band |
| Above 25 % | Pump work buying stability margin already held |

**On a throttling engine, specify it at the deepest intended setting rather than at full thrust.** Stiffness falls linearly with throttle, so 20 per cent at full thrust is 5 per cent at quarter throttle. See [ThrottlingAndMixtureRatio](../../docs/ThrottlingAndMixtureRatio.md).

The floor is a **necessary condition and not a sufficient one**. Chug involves the feed line inertance and the chamber volume as well, so clearing it does not prove stability and failing it does prove a problem.

---

## The outer row

Diverting fuel to the wall protects it and removes that propellant from the performance mixture ratio. At 8 per cent film fraction the core mixture ratio rises from 2.56 to 2.78.

**The c* cost is 0.3 to 0.5 times the film fraction, not the fraction itself.** Film propellant partly burns. An earlier version of this library asserted the loss equalled the fraction, which overstates it by two to three times, and that error is the sort that wrongly rejects the only workable design. See [AlternativeCooling](AlternativeCooling.md).

The outer row is normally a **different element from the core**, and the usual choice is like-on-like: it mixes badly, which next to a wall is exactly what is wanted.

---

## Design rules of thumb

- **Choose the core element for mixing and the outer row for tolerance.** They are different problems and should be different elements.
- **Run the two circuits at different pressure drops.** Equal drops force the momentum ratio out of band.
- **Keep orifices between 0.4 and 2 mm.**
- **Specify stiffness at the deepest throttle setting.**
- **Use a pintle if the engine has to throttle deeply**, and accept the mixing penalty.
- **Cost the outer row at 0.3 to 0.5 of the diverted flow.**
- **Expect to develop the injector by test.** The analysis sets the starting point and does not finish the job.

---

## Failure modes

**One stiffness applied to both circuits.** Forces the momentum ratio out of band, silently.

**A high mixing element in the outer row.** The mixing plane moves toward the wall and the wall is what finds out.

**Stiffness specified at full thrust on a throttling engine.** A fifth of it at quarter throttle, and chug follows.

**Orifices below 0.4 mm.** One particle is one blocked element, which is one local hot spot.

**Film fraction costed at the full fraction.** Overstates the penalty by two to three times.

**Mixing quality figures used to predict efficiency.** They are a ranking, and they are registered as unvalidated for that reason.

---

## Worked numbers

The [worked example](../codeInterface.py) injector: 160 unlike impinging doublets, 20 per cent stiffness, LOX/RP-1 at 10 MPa.

| Quantity | Value |
|---|---|
| Pressure drop | 2.00 MPa |
| Oxidiser orifice | 1.97 mm |
| Fuel orifice | 1.34 mm |
| Momentum ratio | 2.16 |
| Forced value at equal drop, `MR sqrt(rho_f/rho_ox)` | 2.16 |
| Fuel side drop to reach a ratio of 1.5 | 2.88 MPa |
| Film fraction | 8 % |
| Core mixture ratio | 2.78 against an overall 2.56 |
| c* cost of the outer row | 2.4 to 4.0 % |
| Deepest throttle at this stiffness | 25 % |

---

## What is not validated

**The mixing quality figures.** A ranking, not a measurement, and no source states them as numbers. They order the element types and nothing more.

**The film cooling c* penalty.** The 0.3 to 0.5 multiplier is commonly quoted with no single source found, which is why it is reported as a range.

Both are in [validation/referenceCases.py](../../../validation/referenceCases.py). See [ValidationReferences](ValidationReferences.md).

---

## Standards

| Standard | What it gives you |
|---|---|
| **NASA SP-8089** | **Liquid rocket engine injectors.** The design monograph |
| NASA SP-8120 | Nozzles, for the downstream boundary |
| CPIA 655 | Combustion stability testing and rating |
| NASA SP-194 | Combustion instability, which the injector is the usual cause of |

---

## Tool interface

```python
from Injector import Injector

injector = Injector()
injector.setInputs({'combination':     'LOX/RP-1',
                    'chamberPressure': 10.0e6,
                    'oxidiserFlow':    26.47,
                    'fuelFlow':        10.34,
                    'elementType':     'unlike impinging doublet',
                    'elementCount':    160,
                    'stiffness':       0.20,
                    'filmFraction':    0.08})

orifices = injector.sizeOrifices()
print(orifices['orifices']['oxidiser']['diameter'])

momentum = injector.calculateMomentumRatio()
print(momentum['momentumRatio'], momentum['withinBand'])

print(injector.checkStiffness(throttleSetting = 0.4)['clearsFloor'])
print(injector.checkWallCompatibility()['coreMixtureRatio'])
```

---

## References

- NASA SP-8089, *Liquid rocket engine injectors*
- Harrje and Reardon, NASA SP-194, *Liquid Propellant Rocket Combustion Instability*
- Yang, Habiballah, Hulka and Popp, *Liquid Rocket Thrust Chambers*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- Dressler, *Summary of Deep Throttling Rocket Engines with Emphasis on Apollo LMDE*
