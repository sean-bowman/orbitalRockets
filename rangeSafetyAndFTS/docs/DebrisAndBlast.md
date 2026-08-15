[Home](../README.md) > Debris and Blast

# Debris and Blast

## Contents

- [Overview](#overview)
- [The catalogue](#the-catalogue)
- [Where a fragment goes](#where-a-fragment-goes)
- [Why the footprint is an ellipse](#why-the-footprint-is-an-ellipse)
- [Worked numbers](#worked-numbers)
- [What a launch azimuth buys](#what-a-launch-azimuth-buys)
- [Blast](#blast)
- [Toxic release](#toxic-release)
- [What is computed and what is not](#what-is-computed-and-what-is-not)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Everything between a break-up and an impact probability, which is what [`DebrisDispersion`](../rangeSafetyLibrary/DebrisDispersion.py) computes and this document explains.

---

## The catalogue

A break-up model turns a vehicle into a list of fragments, each with a mass, an area, a ballistic coefficient and an imparted velocity.

**The catalogue is the input to everything downstream** and it is the least public part of the analysis: it depends on the vehicle's construction, its propellant state at break-up, and whether the break-up was a termination or a structural failure.

**A terminated liquid vehicle produces a short catalogue of large pieces.** A structural failure at maximum dynamic pressure produces a longer one of smaller pieces, which is worse for the risk analysis because small pieces disperse further.

---

## Where a fragment goes

Each fragment is a ballistic descent, and [`DebrisDispersion`](../rangeSafetyLibrary/DebrisDispersion.py) integrates one for every class in the catalogue.

A two dimensional point mass with drag in an exponential atmosphere, starting from the vehicle's velocity at break-up. The fragment keeps as much of that velocity as its ballistic coefficient lets it, which is the entire spread of the footprint.

```
beta = m / (Cd A)
dv/dt = - rho(h) |v_rel| v_rel / (2 beta) + g
```

**Drag acts on the velocity relative to the air rather than to the ground**, which is what makes the wind term do anything at all.

**The drag area is `Cd A` and it is not split.** A tumbling plate has no single reference area and its drag coefficient is an average over attitude, so separating the two implies a precision that is not there.

**The step is adaptive**, from the tighter of a velocity criterion and a scale height criterion. An insulation panel spends forty five minutes at terminal velocity where nothing is changing, and a fixed step small enough for its entry into thick air would take a hundred thousand of them to land it.

**Terminal velocity is the check on the whole thing.** From drag equal to weight, `v = sqrt(2 g beta / rho)` exactly, and a fragment dropped from rest has to arrive at it and no other speed.

---

## Why the footprint is an ellipse


**Downrange spread comes from the ballistic coefficient distribution.** A light fragment slows quickly and lands short; a dense one carries and lands long. That spread is along the velocity vector and it is the long axis.

**Crossrange spread comes from the imparted velocity and the wind**, both smaller, so the footprint is long and narrow.

Two things fall out of computing it that are not obvious from stating it.

**The destruct charge widens the footprint through the heavy fragments, not the light ones.** The intuition runs the other way: a charge scatters light debris furthest. It does the opposite, because the fragments a charge can throw hardest are exactly the ones that decelerate fastest. On the worked case the charge moves a turbopump 2.3 km sideways and an insulation panel 9 metres.

**The wind does the reverse**, and by more. Drift is the wind speed times the fall time, and the fall times run from three minutes to forty five, so a 15 m/s wind moves the turbopump 650 m and the insulation panel 26 km.

**Which means the impacts are not in ballistic coefficient order once there is any wind at all.** In still air they are: the lightest fragment lands nearest and the heaviest furthest, and nothing but the fragment decides. With a wind on it the lightest fragment is carried past a heavier one, so **a footprint is not a property of the vehicle alone and the order of the pieces on the ground changes with the weather.**

---

## Worked numbers

A break-up at 28 km, 1000 m/s, 45 degrees, 30 km downrange, in a 15 m/s wind.

| Class | Count | `beta` [kg/m2] | `v_t` [m/s] | Fall [s] | Impact [km] | Drift [km] |
|---|---|---|---|---|---|---|
| insulation | 400 | 1.3 | 4.6 | 2687 | 56.8 | 26.5 |
| skin | 180 | 10.9 | 13.2 | 963 | 41.8 | 9.2 |
| structure | 40 | 133.3 | 46.2 | 342 | 62.1 | 2.5 |
| machinery | 6 | 875.0 | 118.4 | 219 | 122.7 | 0.7 |

**The catalogue spans 656 to one in ballistic coefficient and the impacts span 81 km.** The footprint is 81 km long and 4.5 km wide, an aspect ratio of 18 to one.

**The length is the ballistic coefficient spread and the width is the destruct charge**, and those two are an order of magnitude apart. That is the whole reason a debris footprint is drawn as a long thin ellipse rather than a circle around the break-up point.

**The scatter about each impact point comes from a different cause at each end of the catalogue.** Two causes are carried: the destruct throw, and the mean wind not being known exactly. The throw dominates for the turbopump and the wind for everything else, because a fragment that falls slowly loses its throw in seconds and then spends the rest of the descent in a wind nobody measured.

---

## What a launch azimuth buys

The result that came out of computing the impact probabilities rather than assuming them, and it changed the answer.

**The worked case assumed 0.0008 for the coastal town and computes 0.00034.** Every region's assumed value was the wrong size. That matters more than the direction, because the casualty expectation is linear in it and **a number with no derivation behind it cannot be argued with.**

**With the town directly under the ground track the launch is not licensable**, by a factor of thirty on the collective criterion, and no vehicle reliability recovers that: the relationship is linear, so the failure probability would have to fall below a thousandth.

| Town offset [km] | P(impact) | Ec | Licensable |
|---|---|---|---|
| 0 | 0.18066 | 2.93e-03 | no |
| 5 | 0.07856 | 1.27e-03 | no |
| 10 | 0.01760 | 2.86e-04 | no |
| 15 | 0.00638 | 1.04e-04 | no |
| 20 | 0.00176 | 2.96e-05 | **yes** |
| 25 | 0.00034 | 6.51e-06 | **yes** |
| 30 | 0.00004 | 1.79e-06 | **yes** |

**The town has to sit about 20 km off the ground track, and that is a computed distance rather than a rule of thumb.**

**It is bought against the cross-range dispersion of the light debris rather than against the footprint width.** The footprint is 4.5 km wide, so a naive reading says 5 km of offset is plenty. It is not, because the width is the destruct throw and the thing that actually reaches sideways is the wind uncertainty acting on 400 insulation panels for forty five minutes. **A wind error is a vector**, and its cross-range component is as large as its downrange one.

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

## What is computed and what is not

**Computed:** the ballistic coefficients, the descent of every fragment class through an exponential atmosphere with a wind, the impact point and speed of each, the footprint they add up to, a dispersion about each impact point from the destruct throw and the wind uncertainty, and the impact probability in each region that a risk analysis needs.

**Not computed, and each for a stated reason.**

**A Monte Carlo dispersion.** Four fragment classes are propagated deterministically and dispersed about their impact points. A real analysis samples thousands of fragments over break-up time, attitude, fragment properties and a measured wind profile. **The difference is not accuracy, it is coverage:** a catalogue of four classes has four modes and a real footprint is continuous.

**A structural break-up model.** The catalogue here is representative. What decides a real one is where a specific vehicle comes apart under a specific load, which is a structural analysis of an article rather than a range safety calculation.

**A lethality model.** The casualty areas are per fragment class. A real one takes a fragment mass, impact velocity and angle through an injury criterion; this domain computes the impact velocity and stops there.

**Every failure time along the trajectory.** One break-up state is propagated. A failure at 60 seconds and one at 200 produce entirely different footprints, and running the sweep is a loop rather than a model, so what is missing is the trajectory coupling rather than the physics.

**A wind profile.** A single mean wind and a single uncertainty, deliberately. Carrying a measured profile would imply the rest of the model is good enough to deserve one.

**What all of that costs is stated in [ValidationReferences](ValidationReferences.md)**: the arithmetic is exact and the catalogue is representative, so the footprint shape is a result and the footprint numbers are illustrative.

---

## Design rules of thumb

- **Prefer a short catalogue of large pieces.** They disperse less.
- **Expect the footprint to be long and narrow**, along the velocity vector.
- **Watch the low ballistic coefficient tail.** It is what the wind moves, and it is most of the count.
- **Compute the impact probability rather than assuming it.** It multiplies everything downstream and it is the one input nobody can check by eye.
- **Buy the offset against the light debris dispersion, not the footprint width.** The width is a destruct charge and the reach is a wind error.
- **Reuse the pad blast calculation.** It is the same standard.
- **Check toxic release separately on a hypergolic vehicle.** It can govern.
- **Run the analysis from every failure time**, not just the worst one.

---

## Failure modes

**A footprint scaled from the debris mass.** The light fragments disperse furthest.

**Impacts assumed to fall in ballistic coefficient order.** They do in still air and not otherwise.

**A footprint width taken as the offset a town needs.** The width is the destruct throw and it reaches nothing like as far as the wind uncertainty on the light debris.

**One failure time analysed.** The footprint moves through the ascent.

**Wind left out.** It is the crossrange spread.

**Toxic release assumed to scale with quantity.** It scales with dispersion.

**A blast calculation reimplemented.** The standard already lives in ground systems.

---

## References

- [EntryAerodynamics](../../recoveryAndReusability/docs/EntryAerodynamics.md), which solves the same descent in closed form for a single body, through the same exponential atmosphere
- [HazardZonesAndSiting](../../groundSystemsAndOperations/docs/HazardZonesAndSiting.md), for the blast calculation
- 14 CFR 450.135, *Debris risk analysis*, not read in full
- [PublicRiskAnalysis](PublicRiskAnalysis.md), which consumes the impact probabilities
