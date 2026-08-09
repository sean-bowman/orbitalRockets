[Home](../README.md) > Configuration Trades

# Configuration Trades

## Contents

- [Overview](#overview)
- [Diameter against length](#diameter-against-length)
- [Tank arrangement](#tank-arrangement)
- [Common bulkhead](#common-bulkhead)
- [Engine layout](#engine-layout)
- [Fairing and the volume constraint](#fairing-and-the-volume-constraint)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Configuration is where a set of masses becomes a shape, and the shape then feeds back into the masses. Most of this document is qualitative because the trades depend on manufacturing and transport constraints this repository does not carry.

---

## Diameter against length

For a fixed propellant volume, diameter and length trade against each other, and three things pull in different directions.

**A fatter tank has less surface area per unit volume**, so less wall mass for the same enclosed volume, which favours fat.

**A fatter tank has a thicker wall at the same pressure**, because hoop stress is `pr/t`, which favours thin. These two do not cancel: wall mass goes as `p r^2 L` roughly, and volume as `r^2 L`, so **wall mass per unit volume depends on pressure and not on radius at all** for the barrel. The dome and the minimum gauge break that, which is why the answer is not indifferent.

**A longer vehicle bends more.** Slenderness drives the bending modes, the gust loads and the control authority needed. See [aerospaceStructures](../../aerospaceStructures/) and [environmentsAndLoads](../../environmentsAndLoads/).

In practice the diameter is set by transport and by the factory long before any of this, and the length is what falls out. **A designer who thinks they are choosing a diameter is usually choosing a road.**

---

## Tank arrangement

**Separate tanks with an intertank** is the conservative arrangement. Each tank is independently pressurised and inspectable, the intertank carries the load path, and the cost is a structural section that holds no propellant.

**Common bulkhead** deletes the intertank. It is covered below.

**Tandem against concentric.** Tandem is universal on launch vehicles. Concentric tanks appear on some spacecraft and they exist to shorten the vehicle at the cost of an awkward load path and a shared wall between propellants.

---

## Common bulkhead

A single dome separating oxidiser from fuel, deleting the intertank and one dome.

**What it buys** is length and mass: an intertank section and one full dome, which on a large stage is substantial.

**What it costs** is a wall with cryogenic propellant on one side and a different cryogenic propellant on the other, with a pressure difference across it that reverses between fill, flight and drain. It has to be insulated, it has to be leak-tight to a much tighter standard than an external wall because a leak mixes propellants, and it cannot be inspected once built.

**It is the highest-consequence structural decision on a launch vehicle** and the failure mode is not a leak overboard, it is an internal mixture. That asymmetry is why it is not universal despite the mass being clearly favourable.

---

## Engine layout

**One engine** is the simplest and it has no engine-out and a narrow throttle range.

**A cluster** buys engine-out capability and throttle granularity, at the cost of a thrust structure that distributes several loads rather than one, and a base region with several plumes interacting. See [ThrustToWeightAndSizing](ThrustToWeightAndSizing.md).

**Gimballed against fixed.** Gimballing all engines is unnecessary; gimballing the outer ring or a subset is common and it puts an asymmetric load into the thrust structure whenever the gimbal is used.

The thrust structure is where the layout becomes a mass, and it belongs to [aerospaceStructures](../../aerospaceStructures/).

---

## Fairing and the volume constraint

The fairing is sized by the payload envelope rather than by the payload mass, and the two are not correlated.

**A volume-limited payload is common and a mass-limited one is not always.** A large, light spacecraft can fill a fairing at half the vehicle's mass capability, and the vehicle is then flying a fairing it did not need to be that big.

The fairing is dry mass jettisoned early, so its [mass chain](MassChain.md) amplification is lower than a tank kilogram but not negligible: it is carried through most of the first stage burn.

**Fairing separation is a mechanism**, and it belongs to [mechanismsAndSeparation](../../mechanismsAndSeparation/).

---

## Worked numbers

The reference vehicle from the worked example.

| Quantity | Value |
|---|---|
| Tank radius | 0.9 m |
| First stage propellant | 30.65 t |
| First stage tank overall length | 12.9 m |
| Second stage tank overall length | 3.4 m |
| First stage wall thickness at 0.35 MPa | 1.00 mm |

That 1.00 mm is below what a real 2219 tank would be built to, because the pressure vessel model carries no minimum manufacturing gauge. It is the clearest place in this domain where a configuration constraint is missing from the model.

---

## Design rules of thumb

- **Find the diameter constraint before trading diameter.** It is usually transport.
- **Barrel wall mass per unit volume is set by pressure, not radius.** The domes and the gauge floor break the indifference.
- **Treat a common bulkhead as a hazard decision**, not a mass decision.
- **Size the fairing on volume**, and check whether the vehicle is then mass-limited at all.
- **Check slenderness against the bending modes** before settling a length.

---

## Failure modes

**A diameter chosen on mass and rejected by transport.** The constraint that should have come first.

**A common bulkhead traded on mass alone.** The failure mode is an internal propellant mixture.

**A minimum gauge omitted.** Produces tanks thinner than anything manufacturable.

**A fairing sized on payload mass.** It is a volume constraint.

---

## References

- [aerospaceStructures](../../aerospaceStructures/docs/), for the shell and the thrust structure
- [environmentsAndLoads](../../environmentsAndLoads/docs/), for the gust and bending cases slenderness drives
- [mechanismsAndSeparation](../../mechanismsAndSeparation/), for fairing and stage separation
