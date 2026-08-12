[Home](../README.md) > Entry Aerodynamics

# Entry Aerodynamics

## Contents

- [Overview](#overview)
- [The Allen-Eggers solution](#the-allen-eggers-solution)
- [Peak deceleration](#peak-deceleration)
- [Peak heating](#peak-heating)
- [The corridor trade](#the-corridor-trade)
- [Where the peaks happen](#where-the-peaks-happen)
- [Why a booster is not a capsule](#why-a-booster-is-not-a-capsule)
- [What the solution does not cover](#what-the-solution-does-not-cover)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Entry is the first thing to compute about a recovered stage and it has a closed form solution that is nearly seventy years old and still the right place to start.

---

## The Allen-Eggers solution

Assume a constant flight path angle, an exponential atmosphere and no lift. Drag then gives the velocity against density directly:

```
V(rho) = V_e * exp( -rho * H / (2 * beta * sin|gamma|) )
```

with `beta = m / (Cd A)` the ballistic coefficient, `H` the scale height and `gamma` the flight path angle below the horizontal.

**Everything else is differentiation.** Each peak sits where the derivative of the relevant quantity against density vanishes, and because the density appears only inside an exponential, each peak lands at a fixed multiple of the entry velocity.

---

## Peak deceleration

```
a_max = V_e**2 * sin|gamma| / (2 * e * H)      at  V = V_e / sqrt(e) = 0.607 V_e
```

**The ballistic coefficient is not in that equation.** Neither is the mass, the drag coefficient or the area. A dense slender body and a light blunt one, entering at the same speed on the same path angle, pull the same maximum g.

What the ballistic coefficient changes is *where*: the peak sits at `rho = beta sin|gamma| / H`, so a heavier body decelerates lower down and later. It reaches the same peak, having spent longer getting there and more of the atmosphere doing it.

**This is the most counterintuitive result in the domain**, and it survives every representative number in it, because it comes from an exponent rather than a value.

The scaling that does hold: **peak g goes as the square of entry velocity and, for shallow angles, linearly with the flight path angle.**

---

## Peak heating

Sutton and Graves give the stagnation point convective flux:

```
q = k * sqrt(rho / Rn) * V**3        k = 1.7415e-4 for Earth air
```

Differentiating with the velocity profile above puts the peak at `rho = beta sin|gamma| / (3 H)` and `V = V_e exp(-1/6) = 0.846 V_e`, which gives

```
q_max ~ sqrt( beta sin|gamma| / Rn ) * V_e**3
```

**Peak flux rises with the ballistic coefficient, with steepness and with the cube of entry velocity, and falls with nose radius.** That last one is why entry bodies are blunt: a large nose radius is the cheapest way to reduce stagnation heating, and it costs drag that an entry body wants anyway.

Integrating the flux over the whole entry gives the heat load, which has a closed form because the integrand is `rho^(-1/2) exp(-a rho)`:

```
Q = k * V_e**2 * sqrt( pi * beta * H / (Rn * sin|gamma|) )
```

**The units on the Sutton-Graves constant are quoted wrongly in several sources**, by four orders of magnitude. See [ValidationReferences](ValidationReferences.md), where the convention is fixed against published entry cases rather than against the statement.

---

## The corridor trade

Put the two scalings side by side and the entry design trade falls out.

| | Peak rate | Total load |
|---|---|---|
| Ballistic coefficient | rises as sqrt(beta) | rises as sqrt(beta) |
| Steepness | rises as sqrt(sin gamma) | **falls** as 1/sqrt(sin gamma) |
| Entry velocity | rises as V^3 | rises as V^2 |
| Nose radius | falls as 1/sqrt(Rn) | falls as 1/sqrt(Rn) |

**Flight path angle is the only one that moves the two in opposite directions**, and that is the corridor decision.

**A steep entry** is short and violent: a high peak flux and a small total load. It needs a material that survives a high flux, and not much of it.

**A shallow entry** is long and mild: a low peak flux and a large total load. It needs a lot of a cheaper material.

**Peak rate selects the thermal protection material and total load sets its thickness**, so the corridor decides which of those two problems the programme has. There is no angle that improves both, which is why it is a choice rather than an optimum.

---

## Where the peaks happen

**Peak heating happens before peak deceleration**, at 0.846 of the entry velocity against 0.607, and higher in the atmosphere.

The separation is exact and universal:

```
h_q - h_g = H * ln(3) = 7.9 km
```

because the two peak densities differ by exactly a factor of three and altitude is logarithmic in density.

**The separation is the invariant, not the ratio.** Sources quoting the altitude ratio as about 1.1 are quoting it for an orbital entry, where the deceleration peak is high enough that 7.9 km is a tenth of it. On a booster returning from a lofted suborbital trajectory the peaks sit near 16 and 24 km and the ratio is 1.5.

**The practical consequence is that the structure and the thermal protection are not designed by the same instant of the entry**, which is easy to assume and wrong.

---

## Why a booster is not a capsule

The single most useful comparison in the domain.

| | Booster return | From orbit |
|---|---|---|
| Entry velocity | 2,200 m/s | 7,800 m/s |
| Peak deceleration | 5.3 g | 16.6 g |
| Peak heat flux | 18 W/cm2 | 390 W/cm2 |
| Total heat load | 690 J/cm2 | 17,430 J/cm2 |

A first stage separates well short of orbital velocity and follows a lofted suborbital arc, so it re-enters at about a quarter of orbital speed. **Peak flux goes as the cube of velocity**, so that alone is a factor of forty; the booster also enters far more steeply, which raises its own flux and brings the measured ratio back to twenty two.

**Eighteen watts per square centimetre is a paint and a metal skin problem. Four hundred is a heat shield.** That is the whole reason first stage reuse arrived long before upper stage reuse, and it is a consequence of one exponent rather than of anything about materials.

---

## What the solution does not cover

Named because a closed form that gets the shape right invites being trusted for the magnitude.

**Lift.** A lifting entry flies a shallower effective corridor and can hold a constant deceleration, which is a different problem with a different solution.

**A varying flight path angle**, which every real entry has. The solution assumes it constant, and the assumption fails first near the horizontal.

**A real atmosphere.** A single scale height is a coarse fit at the 40 to 70 km altitudes where an orbital entry peaks.

**Radiative heating**, which is negligible at booster speeds and a large fraction of the total at lunar return speeds.

**Anywhere but the stagnation point.** The rest of the body sees a lower flux and the distribution is a computational fluid dynamics problem.

**And what the heat flux does to the structure**, which is [thermalManagement](../../thermalManagement/docs/AeroheatingAndTPS.md) and [environmentsAndLoads](../../environmentsAndLoads/). This domain computes the environment and hands it over.

---

## Worked numbers

A booster return at 2,200 m/s and 25 degrees, ballistic coefficient 2,251 kg/m2.

| Quantity | Value |
|---|---|
| Peak deceleration | 5.3 g, at 16.0 km |
| Peak heat flux | 18 W/cm2, at 23.9 km |
| Total heat load | 690 J/cm2 |
| Altitude separation | 7.9 km, always |
| Peak flux across 16x in beta | 4x |
| Peak g across 16x in beta | **unchanged** |
| Steepening 2 to 40 degrees, flux | 4.3x |
| Steepening 2 to 40 degrees, load | 0.23x |

---

## Design rules of thumb

- **Compute the Allen-Eggers peaks before anything else.** They cost nothing and they set the problem.
- **Do not expect a heavy entry to be a high-g entry.** It is a hot one.
- **Blunt the nose.** It is the cheapest reduction in stagnation heating available.
- **Pick the corridor by which thermal protection problem you would rather have.**
- **Design the structure and the thermal protection to different instants.**
- **Check the entry velocity before assuming a heat shield is needed.**

---

## Failure modes

**Peak g assumed to scale with mass.** It does not scale with the vehicle at all.

**A corridor optimised.** Peak rate and total load move in opposite directions; there is no optimum.

**The Sutton-Graves constant used with the units several sources state.** Wrong by 1e4.

**An altitude ratio of 1.1 applied to a suborbital return.** The separation is fixed and the ratio is not.

**The closed form trusted for a magnitude.** It gets the shape right and it assumes a constant flight path angle, no lift and one scale height.

---

## Tool interface

```python
from EntryTrajectory import EntryTrajectory

trajectory = EntryTrajectory()
trajectory.setInputs({'entryVelocity':   2200.0,
                      'flightPathAngle': 25.0,
                      'mass':            26000.0,
                      'dragCoefficient': 1.1,
                      'referenceArea':   10.5,
                      'noseRadius':      1.8})

deceleration = trajectory.calculatePeakDeceleration()
heating      = trajectory.calculatePeakHeating()
beta         = trajectory.compareBallisticCoefficients()
corridor     = trajectory.compareFlightPathAngles()
```

A flight path angle below one degree is refused: that is a glide, and the constant flight path angle the solution assumes is the first thing to go.

---

## References

- H. J. Allen and A. J. Eggers, *A Study of the Motion and Aerodynamic Heating of Ballistic Missiles Entering the Earth Atmosphere at High Supersonic Speeds*, NACA Report 1381, 1958
- K. Sutton and R. A. Graves, *A General Stagnation Point Convective Heating Equation for Arbitrary Gas Mixtures*, NASA TR R-376, 1971
- NASA TFAWS 2012 aerothermodynamics course notes, for the relations as taught
- [AeroheatingAndTPS](../../thermalManagement/docs/AeroheatingAndTPS.md), which takes it from here
