[Home](../README.md) > Separation Systems

# Separation Systems

## Contents

- [Overview](#overview)
- [The clamp band and its wedge](#the-clamp-band-and-its-wedge)
- [Preload relaxation](#preload-relaxation)
- [Separation velocity](#separation-velocity)
- [Tipoff, and the two things that do not fix it](#tipoff-and-the-two-things-that-do-not-fix-it)
- [Recontact](#recontact)
- [Linear separation and frangible joints](#linear-separation-and-frangible-joints)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A stage separation is two events. The joint lets go, and then the two halves move apart without hitting each other. The first is a preload problem and the second is a kinematics problem, and they fail differently.

---

## The clamp band and its wedge

A clamp band is a tension band around a pair of V-section flanges. A band under tension `T` produces a total inward radial force of `2 pi T` on the ring, independent of radius, and the wedge turns that into axial clamping:

```
P = 2 pi T / tan(alpha)
```

with `alpha` the wedge half angle measured from the interface plane.

**At fifteen degrees the amplification is 23.4.** That is the whole device: a band a person can tension by hand produces a preload of hundreds of kilonewtons.

Friction on the wedge faces gives some of it back. At a friction coefficient of 0.15 the wedge efficiency is about 0.64, so a 12 kN band delivers 180 kN rather than the frictionless 281 kN.

**The friction cuts both ways.** It opposes the band tightening, which is the loss above, and it opposes the band releasing, which is a release reliability question this library does not model.

---

## Preload relaxation

This is the failure mode this domain's ethos names, and the reason is that the losses are individually small and they compound.

| Mechanism | Loss | When |
|---|---|---|
| Embedment | 5 % | Within hours, as surface asperities flatten |
| Short-term relaxation | 3 % | First weeks |
| Storage | up to 5 % | Months, accruing over the first year |

On the reference joint that is **11.3 per cent over nine months**, taking 180 kN of installed preload to 160 kN.

Two things about that are worth stating plainly.

**The losses compound rather than add.** Applying them in series gives less than their sum, which is a small mercy and does not change the conclusion.

**None of them is visible on the vehicle.** There is no gauge on a clamp band. A joint installed to a comfortable margin and flown a year later is a different joint, and the only way to know is to have carried the relaxation in the margin from the start.

[ClampBand](SeparationSystems.md) **refuses** a joint whose retained preload does not hold the flight load with a factor of 1.2, rather than reporting a negative margin, because a clamp band that gaps in flight is a stage coming apart.

---

## Separation velocity

Springs store energy and the two bodies share it in inverse proportion to their masses:

```
v_rel = sqrt(2 E (1/m1 + 1/m2))
```

The lighter body takes most of the velocity and most of the energy, which is why a small upper stage separating from a large booster moves and the booster barely does. On the reference case, 160 J gives 0.481 m/s relative, split 0.370 and 0.111.

---

## Tipoff, and the two things that do not fix it

Tipoff is the angular rate the separating body leaves with, and it comes from spring force mismatch rather than from spring force.

**A stronger spring does not fix it.** Both the velocity and the tipoff rate scale with the square root of stiffness, because both come from the same impulse. So the rotation accumulated while clearing, which is what actually matters, **does not move at all**. A stronger spring buys separation velocity and no recontact margin.

**More springs do not fix the bound either.** The deterministic worst case, half the springs at the top of tolerance and half at the bottom, produces the same net moment whether there are four springs or forty:

| Springs | Worst case | Statistical |
|---|---|---|
| 2 | 0.396 deg/s | 0.198 deg/s |
| 4 | 0.396 deg/s | 0.140 deg/s |
| 8 | 0.396 deg/s | 0.099 deg/s |
| 12 | 0.396 deg/s | 0.081 deg/s |

Only the statistical case improves, as one over the root of the count.

**So adding springs buys a better expected outcome and no better bound.** And the statistical argument is weakest exactly where it is most often invoked: springs from a single production lot are correlated, not independent.

**What attacks the bound is matching.** Measure the springs, pair the high ones against the high ones across the bolt circle, and the imbalance cancels by construction rather than by chance. A separation system with many springs and no matching requirement has bought the statistical case and specified the worst one.

---

## Recontact

The separating body translates and rotates at the same time. What matters is whether it clears before the rotation closes the gap:

```
clearTime = clearanceLength / v_rel
rotation  = tipoffRate * clearTime
excursion = clearanceLength * sin(rotation)
```

On the reference case that is 1.29 mm of excursion against a 20 mm radial gap, a factor of 15.5.

[SeparationSystem](SeparationSystems.md) **refuses** a case that recontacts. A separation that recontacts is a lost mission, not a degraded separation, and reporting a negative clearance invites somebody to treat it as a small number.

---

## Linear separation and frangible joints

The clamp band is one of three arrangements and the library models only it.

**A linear separation system** runs an explosive cord along a structural joint designed to fail in a controlled way. It suits a non-circular interface and it distributes the release rather than concentrating it, at the cost of a longer explosive train.

**A frangible joint** is a structural section with a notch and a contained charge, designed to fracture cleanly. The containment is what makes it usable near sensitive hardware, and the fracture behaviour is a materials problem rather than a mechanism one.

Both are named here rather than modelled, because both are characterised by test rather than calculated.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Band tension | 12.0 kN |
| Wedge amplification at 15 degrees | 23.4 |
| Wedge efficiency at 0.15 friction | 0.64 |
| Delivered preload | 180.4 kN |
| Retained after nine months | 160.0 kN, 11.3 % lost |
| Separation energy | 160 J |
| Relative velocity | 0.481 m/s |
| Tipoff, worst case | 0.396 deg/s |
| Tipoff, statistical at four springs | 0.140 deg/s |
| Lateral excursion while clearing | 1.29 mm |
| Radial gap | 20 mm |

---

## Design rules of thumb

- **Carry the margin against the relaxed preload.** Eleven per cent over nine months on a real joint.
- **Match the springs in opposing pairs.** It is the only thing that improves the bound.
- **Do not fix tipoff with a stronger spring.** The rotation while clearing does not move.
- **Check recontact, not just velocity.** A healthy velocity with a tipoff rate is still a collision.
- **State the storage duration** as a requirement, because it is a term in the preload.

---

## Failure modes

**A joint sized on installed preload.** It relaxes, and nothing on the vehicle shows it.

**Tipoff attacked with spring strength.** Raises the rate and the velocity together and buys nothing.

**Spring count treated as a bound improvement.** It improves the expectation only, and lot correlation undermines even that.

**Recontact not checked.** The separation velocity looks fine right up to the collision.

**A transverse inertia estimated from a bolt circle.** It understates by an order of magnitude and therefore overstates the tipoff rate by the same factor. This library required the inertia as an input after making exactly that mistake.

---

## Tool interface

```python
from ClampBand import ClampBand
from SeparationSystem import SeparationSystem

band = ClampBand()
band.setInputs({'bandTension': 12000.0, 'interfaceRadius': 0.60,
                'bandArea': 1.2e-4, 'flightLoad': 95000.0, 'storageMonths': 9.0})

joint = band.checkJoint()

system = SeparationSystem()
system.setInputs({'springCount': 4, 'springStiffness': 8000.0, 'springStroke': 0.10,
                  'springRadius': 0.55, 'separatingMass': 1800.0, 'remainingMass': 6000.0,
                  'inertia': 2653.0, 'clearanceLength': 0.30, 'radialGap': 0.020})

recontact = system.checkRecontact()
counts    = system.compareSpringCounts()
```

`inertia` is required rather than defaulted, and it is the transverse inertia of the separating body about its own centre of gravity.

---

## References

- NASA-STD-5017B, *Design and Development Requirements for Mechanisms*
- Conley, *Space Vehicle Mechanisms: Elements of Successful Design*, the separation systems chapters
- [Pyrotechnics](Pyrotechnics.md), for the device that cuts the band
- [SpringsAndEnergyStorage](SpringsAndEnergyStorage.md)
