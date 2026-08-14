[Home](../README.md) > Debris and Blast

# Debris and Blast

## Contents

- [Overview](#overview)
- [The catalogue](#the-catalogue)
- [Where a fragment goes](#where-a-fragment-goes)
- [Why the footprint is an ellipse](#why-the-footprint-is-an-ellipse)
- [Blast](#blast)
- [Toxic release](#toxic-release)
- [Why none of it is computed here](#why-none-of-it-is-computed-here)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Everything between a break-up and an impact probability. This is the largest single piece of unbuilt work implied by this repository, and this document says what it would take.

---

## The catalogue

A break-up model turns a vehicle into a list of fragments, each with a mass, an area, a ballistic coefficient and an imparted velocity.

**The catalogue is the input to everything downstream** and it is the least public part of the analysis: it depends on the vehicle's construction, its propellant state at break-up, and whether the break-up was a termination or a structural failure.

**A terminated liquid vehicle produces a short catalogue of large pieces.** A structural failure at maximum dynamic pressure produces a longer one of smaller pieces, which is worse for the risk analysis because small pieces disperse further.

---

## Where a fragment goes

Each fragment is a ballistic entry problem, and this repository already computes one.

**[EntryTrajectory](../../recoveryAndReusability/docs/EntryAerodynamics.md) in recoveryAndReusability solves the descent of a single body** with a given ballistic coefficient, using the Allen-Eggers closed form. That is the physics.

What is missing is everything around it.

**Every fragment**, rather than one.

**With an imparted velocity** from the break-up, which spreads the initial conditions.

**Through a wind field**, which moves a low ballistic coefficient fragment tens of kilometres and a high one barely at all.

**From every failure time along the trajectory**, because a failure at 60 seconds and one at 200 produce entirely different footprints.

**The result is a probability distribution rather than a point**, and producing it is a Monte Carlo rather than a closed form.

---

## Why the footprint is an ellipse

Worth knowing even without the model.

**Downrange spread comes from the ballistic coefficient distribution.** A light fragment slows quickly and lands short; a dense one carries and lands long. That spread is along the velocity vector and it is the long axis.

**Crossrange spread comes from the imparted velocity and the wind**, both of which are smaller effects, so the footprint is long and narrow.

**And the low ballistic coefficient tail is the one that reaches sideways**, because it is the one the wind moves. A light fragment is the least energetic and the most widely dispersed, which is why a footprint is not simply a scaled version of the debris mass distribution.

---

## Blast

For a vehicle that impacts intact or nearly so, the far field overpressure is a hazard in its own right and 14 CFR 450.101 counts it in the collective risk.

**The calculation is the same one [groundSystemsAndOperations](../../groundSystemsAndOperations/docs/HazardZonesAndSiting.md) does** for pad siting: an explosive equivalence from DESR 6055.09 and Hopkinson-Cranz cube root scaling to a distance.

**It is not repeated here.** The propellant combination table, the hydrogen sublinear rule and the K factors all live there, read from the standard, and a second implementation would drift.

**What differs is the geometry**: a pad blast is at a known location and an impact blast is wherever the vehicle came down, so the exposed population is a distribution rather than a site plan.

---

## Toxic release

The third contributor the regulation counts, alongside inert debris and blast.

**It scales with release rate, wind and atmospheric stability rather than with quantity**, which makes it fundamentally different from the other two: a small release on a still day can produce a larger hazard area than a large one in a breeze.

**It is not modelled in this repository**, in this domain or in [groundSystemsAndOperations](../../groundSystemsAndOperations/docs/ValidationReferences.md), and both say so. It needs a dispersion model and a meteorological input that nothing here carries.

**On a hypergolic vehicle it can be the governing contributor**, which is worth stating because the inert debris analysis is the one that gets done.

---

## Why none of it is computed here

The scope decision, stated plainly.

**A break-up model and a debris dispersion is a real piece of work**, not a class. It needs a fragment catalogue this repository has no basis for, a Monte Carlo framework it does not have, and a wind field model it does not carry.

**So this domain takes an impact probability as an input** and registers it as unvalidated, with the note that closing the gap is the largest single piece of unbuilt work implied by the repository.

**What that costs is honesty about the risk numbers**: the casualty expectation is computed exactly from inputs that are representative, so the arithmetic is right and the answer is illustrative. That is stated in [ValidationReferences](ValidationReferences.md) rather than implied.

---

## Design rules of thumb

- **Prefer a short catalogue of large pieces.** They disperse less.
- **Expect the footprint to be long and narrow**, along the velocity vector.
- **Watch the low ballistic coefficient tail.** It is what the wind moves.
- **Reuse the pad blast calculation.** It is the same standard.
- **Check toxic release separately on a hypergolic vehicle.** It can govern.
- **Run the analysis from every failure time**, not just the worst one.

---

## Failure modes

**A footprint scaled from the debris mass.** The light fragments disperse furthest.

**One failure time analysed.** The footprint moves through the ascent.

**Wind left out.** It is the crossrange spread.

**Toxic release assumed to scale with quantity.** It scales with dispersion.

**A blast calculation reimplemented.** The standard already lives in ground systems.

---

## References

- [EntryAerodynamics](../../recoveryAndReusability/docs/EntryAerodynamics.md), which computes one fragment's descent
- [HazardZonesAndSiting](../../groundSystemsAndOperations/docs/HazardZonesAndSiting.md), for the blast calculation
- 14 CFR 450.135, *Debris risk analysis*, not read in full
- [PublicRiskAnalysis](PublicRiskAnalysis.md), which consumes the impact probabilities
