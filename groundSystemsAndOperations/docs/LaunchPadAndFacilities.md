[Home](../README.md) > Launch Pad and Facilities

# Launch Pad and Facilities

## Contents

- [Overview](#overview)
- [The layout is set by distances](#the-layout-is-set-by-distances)
- [Flame trench and deflector](#flame-trench-and-deflector)
- [Acoustic suppression](#acoustic-suppression)
- [Lightning protection](#lightning-protection)
- [The launch mount and hold-down](#the-launch-mount-and-hold-down)
- [What a pad has to survive](#what-a-pad-has-to-survive)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

A launch pad is a set of concentric distances with hardware placed in the gaps. Almost every layout decision follows from [siting](HazardZonesAndSiting.md) and almost every hardware decision follows from what one launch does to the structure.

---

## The layout is set by distances

The rings come from the explosive equivalent of the propellant load, and everything else fits between them.

**Inside the closest ring is nothing that has to survive**, because the ring where the vehicle stands is the one where lethal overpressure lives. In the worked example that is 27 m at the lung rupture criterion against 609 m at inhabited building distance.

**Between the rings sit the things that can be rebuilt**: the launch mount, the umbilical tower, the water tank, the local pneumatics.

**Outside the outermost ring sits everything with people in it.**

**The binding facility is rarely the closest one.** It is the one whose criterion is strictest relative to where it sits, which is a different question. In the worked example the propellant farm at 700 m against a 274 m intraline requirement binds at 2.55, while the launch control centre at 4,500 m sits at 7.4 times its requirement.

---

## Flame trench and deflector

The exhaust has to go somewhere that is not back at the vehicle.

**A trench with a deflector turns the plume horizontally** and splits it away from the vehicle. The deflector is the most heavily loaded piece of civil structure on the site: it takes the full stagnation heating and pressure of a rocket exhaust for the duration of the liftoff transient, and it does so repeatedly.

**Ablative or water-cooled, and both are consumables.** A deflector is inspected and refurbished on a schedule, which is a turnaround driver on a high-cadence pad.

**The trench geometry is a plume problem** and belongs with [nozzles](../../propulsion/nozzles/) and the plume expansion at sea level, not here.

---

## Acoustic suppression

The loudest environment a vehicle sees is its own liftoff, reflected.

**Water injection is the standard mitigation**, and the mechanism is worth stating because it is not the obvious one: the water absorbs acoustic energy by being atomised and vaporised, and it also reduces the plume's own noise generation by breaking up the shear layer. Flow rates are large, hundreds of cubic metres in tens of seconds.

**The environment itself belongs to [environmentsAndLoads](../../environmentsAndLoads/docs/AcousticEnvironment.md)**, which computes the overall sound pressure level and the spectrum. What the pad decides is how much water and where, and that is a facility design informed by the environment rather than a calculation done here.

**The vehicle is not the only thing being protected.** Reflected acoustics load the payload fairing, and payload acoustic limits are frequently what sets the suppression requirement rather than the vehicle structure.

---

## Lightning protection

A pad is the tallest conductive thing on a flat coastal site, which is a description of a lightning rod.

**A catenary or mast system intercepts the strike** and carries it to ground through a path that does not include the vehicle. Down conductors, ground rings and a low-impedance earth are the whole of it.

**The vehicle is protected by not being the path**, not by being able to take the current.

**Every strike within a defined radius triggers a retest**, because a nearby strike induces currents in the vehicle harness even without a direct hit. That retest is a turnaround driver and it is the reason lightning shows up in a schedule discussion as well as in a safety one. See [electricalPower](../../electricalPower/docs/GroundingAndBonding.md) for the bonding side.

---

## The launch mount and hold-down

**The mount carries the vehicle before flight and the thrust during ignition**, which are two different load cases and the second is the larger.

**Hold-down exists so that the engines can be checked before release.** Start, reach steady state, verify chamber pressures and health, then release. That converts an engine start failure from a loss of vehicle into a pad abort, which is the single highest-value thing hold-down does.

**Release has to be simultaneous and clean.** An asymmetric release is a lateral load and a rotation at the worst possible moment. See [mechanismsAndSeparation](../../mechanismsAndSeparation/).

**And the released energy has to go somewhere.** The vehicle unloads the mount in milliseconds, and the structure rings.

---

## What a pad has to survive

Listed because pad design is mostly a durability problem rather than a strength one.

**Its own launch**, repeatedly. Heat, pressure, acoustics, vibration, and water.

**The salt environment**, on a coastal site, permanently. Corrosion is the pad's dominant maintenance cost and it works on everything not actively protected.

**A propellant spill**, without spreading it. Sloped decks, containment, and separation of incompatible fluids.

**And a launch failure on or near the pad**, which is what the [siting](HazardZonesAndSiting.md) rings are for and which is a design case rather than a contingency.

---

## Design rules of thumb

- **Lay the pad out from the rings outward.** The distances are not negotiable and everything else is.
- **Treat the deflector as a consumable** with an inspection interval, not as a structure.
- **Get the payload acoustic limit before sizing the water.** It usually governs.
- **Protect the vehicle by not being the lightning path.**
- **Use hold-down to convert a start failure into a pad abort.**
- **Budget corrosion maintenance from day one on a coastal site.**

---

## Failure modes

**A layout designed before the siting.** Everything moves.

**A deflector treated as permanent structure.** It is a consumable and it drives turnaround.

**Acoustic suppression sized on the vehicle limit.** The payload usually governs.

**Lightning protection designed for the strike rather than for the retest.** The retest is the schedule cost.

**An asymmetric hold-down release.** A lateral load and a rotation at liftoff.

---

## References

- [HazardZonesAndSiting](HazardZonesAndSiting.md), which sets the layout
- [AcousticEnvironment](../../environmentsAndLoads/docs/AcousticEnvironment.md)
- [GroundingAndBonding](../../electricalPower/docs/GroundingAndBonding.md)
- [TestFacilitiesAndGSE](../../fluidSystems/fluidSystemsTesting/docs/TestFacilitiesAndGSE.md), for the test stand equivalent
