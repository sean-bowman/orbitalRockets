[Home](../README.md) > Nozzle Contour

# Nozzle Contour

## Contents

- [Overview](#overview)
- [Rao's approximation](#raos-approximation)
- [Why a table cannot do this](#why-a-table-cannot-do-this)
- [The short bell surprise](#the-short-bell-surprise)
- [Wetted area, and who gets it wrong](#wetted-area-and-who-gets-it-wrong)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Validation](#validation)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A conceptual design needs three things from a nozzle contour before anyone runs a method of characteristics solution: a wall angle, a length, and a wetted area. The wall angle sets the divergence loss, the length sets the mass and the packaging, and the wetted area sets the cooling load.

Rao's parabolic approximation gives all three in closed form from an area ratio and a length fraction. That is what [NozzleContour](NozzleContour.md) computes and it is the whole of its ambition.

**This is not a method of characteristics solution.** The NOVA suite generates axisymmetric MoC isentropic contours and the cooling channel geometry that follows them, and nothing here approaches that fidelity. The two answer different questions: this one answers "roughly what shape and how much area", NOVA answers "what are the coordinates". See [NozzleContourInterface](NozzleContourInterface.md) for where the boundary sits and why.

---

## Rao's approximation

A Rao bell is a circular arc leaving the throat, followed by a parabola that meets the exit plane at a specified angle. Two angles define it.

| Angle | Symbol | What it is |
|---|---|---|
| Initial wall angle | `theta_n` | The wall angle just downstream of the throat, where the parabola begins |
| Exit wall angle | `theta_e` | The wall angle at the exit plane, which sets the divergence loss |

Rao published both as functions of area ratio and length fraction, as a chart. The library carries a logarithmic fit to the 80 per cent bell curves:

```
theta_n = 24.317 + 2.623 ln(eps)
theta_e = 19.433 - 2.623 ln(eps)
```

with a multiplicative correction for length fraction, `0.80 / L`, because a shorter bell has to turn the flow harder at the throat and has less length to turn it back.

**The two angles move in opposite directions with area ratio.** That is the geometric heart of a bell: a larger expansion turns the flow harder at the throat and has further to turn it back by the exit.

| Area ratio | `theta_n` | `theta_e` | Divergence efficiency |
|---|---|---|---|
| 5 | 28.5 | 15.2 | 0.9825 |
| 10 | 30.4 | 13.4 | 0.9864 |
| 20 | 32.2 | 11.6 | 0.9898 |
| 40 | 34.0 | 9.8 | 0.9928 |
| 60 | 35.1 | 8.7 | 0.9943 |
| 100 | 36.4 | 7.4 | 0.9959 |

A vacuum nozzle at an area ratio of 100 has less than half the divergence loss of a booster nozzle at 20, and that is before anything about the contour has been chosen.

---

## Why a table cannot do this

This sub-domain shipped a lookup table of exit angles first, one number per contour family, and it was wrong.

The table gave an 80 per cent bell an exit angle of 8 degrees regardless of area ratio. Rao gives 11.5 degrees at an area ratio of 20. The divergence efficiency at 8 degrees is 0.9951 and at 11.5 it is 0.9899, so **the table understated the divergence loss by a factor of two** and [NozzlePerformance](NozzlePerformance.md) concluded that the boundary layer was the largest loss when it is not.

The 8 degree figure is not invented. It is roughly right for a large upper stage nozzle, somewhere above an area ratio of 60. Applied to a first stage booster it is out by three and a half degrees, and a fixed number cannot represent a quantity that varies by a factor of two across the range of nozzles a launch vehicle uses.

**The cone is still tabulated and that is correct.** A 15 degree cone has a 15 degree exit angle by definition. Rao has nothing to say about it. The library computes the bells and looks up the cone, which is the right split rather than an inconsistency, and a test asserts no bell ever gets a tabulated angle again.

---

## The short bell surprise

The usual story is that a bell recovers divergence loss from a cone. At long lengths that is true. At short lengths it is not, and the direction is the opposite of the intuition.

| Length fraction | `theta_n` | `theta_e` | Length | Divergence efficiency |
|---|---|---|---|---|
| 0.60 | 43.0 | 15.4 | 356 mm | 0.9821 |
| 0.70 | 36.8 | 13.2 | 416 mm | 0.9868 |
| 0.80 | 32.2 | 11.5 | 475 mm | 0.9899 |
| 0.90 | 28.6 | 10.2 | 534 mm | 0.9920 |
| 1.00 | 25.8 | 9.2 | 594 mm | 0.9935 |

**A 60 per cent bell leaves at 15.4 degrees, which is steeper than the 15 degree cone it competes with.** Its divergence loss is therefore worse than the cone's. It still wins overall, but only because it is 40 per cent shorter and has correspondingly less wall friction.

A short bell is not a cheap way to buy divergence recovery. It is a way to buy wall area back. That distinction is invisible in a table and obvious the moment the angle is computed.

---

## Wetted area, and who gets it wrong

A bell bulges outward from the straight line between throat and exit. Approximating it as a cone frustum therefore understates its area, and the wetted area is what the cooling circuit is sized against.

On the reference booster, at an area ratio of 20.35 and a 45.3 mm throat radius:

| Estimate | Area |
|---|---|
| Cone frustum, throat to exit | 3928 cm^2 |
| Integrated Rao contour | 4308 cm^2 |
| **Ratio** | **1.097** |

The ratio is insensitive to length fraction, holding between 1.096 and 1.098 across the whole admissible range, which is what makes it usable as a correction factor rather than a case-by-case calculation.

**[combustionDevices](../../combustionDevices/docs/RegenerativeCooling.md) uses the frustum.** The nozzle is about two thirds of the wetted area of that engine, so the total is understated by about 6.6 per cent and the integrated heat load rises from 8.13 MW to roughly 8.66 MW.

That correction has been **registered rather than propagated**. The cooling circuit on that engine already fails to close, the correction makes it fail by more, and the direction is therefore safe. Propagating it would couple the two sub-domains for a number that changes no conclusion. The entry is `bellWettedArea` in [the unvalidated register](../../../validation/referenceCases.py), and it says exactly this.

---

## Worked numbers

The reference booster nozzle, at an area ratio of 20.35 on a 45.3 mm throat radius, as an 80 per cent bell.

| Quantity | Value |
|---|---|
| Exit radius | 204.4 mm |
| 15 degree cone length | 593.6 mm |
| Bell length | 474.9 mm |
| Initial wall angle | 32.2 degrees |
| Exit wall angle | 11.5 degrees |
| Turning | 20.7 degrees |
| Divergence efficiency | 0.9899 |
| Wetted area, integrated | 4308 cm^2 |
| Wetted area, frustum | 3928 cm^2 |

---

## Design rules of thumb

- **Compute the exit angle, do not look it up.** It varies by a factor of two across the area ratios a launch vehicle uses, and this sub-domain published a wrong finding by not doing so.
- **Check the exit angle against the contour that actually gets built.** It is the only number the conceptual and the MoC halves share.
- **Do not assume a short bell recovers divergence.** Below about 70 per cent it is steeper than the cone.
- **Add about 10 per cent to a frustum wetted area** before believing a cooling closure that used it.
- **Stay between 0.6 and 1.0 length fraction.** Outside it the correction is an extrapolation, and far outside it the class refuses rather than returning nonsense.

---

## Failure modes

**A tabulated exit angle.** The defect this sub-domain published and withdrew. A fixed number for a quantity that varies by a factor of two.

**A frustum wetted area in a cooling calculation.** Understates the area by about a tenth, in the unsafe direction.

**Extrapolating the length correction.** Rao's fit covers roughly 0.6 to 1.0. At 0.3 and a large area ratio the initial wall angle comes out past 90 degrees, which turns the wall past radial and is not a nozzle. The class raises there.

**Treating this as a manufacturing contour.** The coordinates are for area and length. A wall to cut metal against comes from a method of characteristics solution.

**A guard that cannot fire.** The first version of this class checked that the exit angle stayed below the initial angle. The correction is multiplicative, so it cannot reverse them and the check never fired. It read as a handled failure mode and was not one, and it has been replaced by the initial angle bound above.

---

## Validation

The wall angle fit is checked against Rao's published chart, reproduced as Huzel and Huang figure 4-16. At an area ratio of 20 for an 80 per cent bell the chart gives an initial angle of about 33 degrees and an exit angle of about 11, and the fit gives 32.2 and 11.6.

The registered band is **one degree**, in `CORRELATION_ACCURACY['raoWallAngles']`, and that band is not negligible: a degree of exit angle is worth about 0.1 per cent of divergence efficiency at these angles. It is a quarter of the error the lookup table it replaced was making.

**The wetted area is not validated.** Published engines give channel counts and coolant paths rather than wetted areas. Both the frustum and the integrated contour are calculations, and only their ratio is being claimed. See [ValidationReferences](ValidationReferences.md).

---

## Tool interface

```python
from NozzleContour import NozzleContour

contour = NozzleContour()
contour.setInputs({'throatRadius':   0.0453,
                   'areaRatio':      20.35,
                   'lengthFraction': 0.80})

angles = contour.wallAngles()      # initial, exit, turning
area   = contour.surfaceArea()     # integrated, frustum, ratio
points = contour.coordinates()     # axial and radial arrays

print(contour.generateReport())
```

`lengthFraction` defaults to 0.80 and is the bell length as a fraction of a 15 degree cone of the same area ratio, which is how bells are universally quoted.

---

## References

- Rao, *Exhaust nozzle contour for optimum thrust*, Jet Propulsion 1958
- Huzel and Huang, *Modern Engineering for Design of Liquid-Propellant Rocket Engines*, figure 4-16
- Sutton and Biblarz, *Rocket Propulsion Elements*, the nozzle configuration chapter
- NASA SP-8120, *Liquid rocket engine nozzles*
