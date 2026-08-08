[Home](../README.md) > Radiation Heat Transfer

# Radiation Heat Transfer

## Contents

- [Overview](#overview)
- [The fourth power, and what it does to design](#the-fourth-power-and-what-it-does-to-design)
- [Absorptivity and emissivity are not one number](#absorptivity-and-emissivity-are-not-one-number)
- [Degradation](#degradation)
- [View factors](#view-factors)
- [Linearising radiation for a network](#linearising-radiation-for-a-network)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Radiation is the only mechanism that works in vacuum, which makes it the only way a spacecraft rejects heat and the dominant mechanism on any surface above roughly 600 K. It is also the only mechanism in this domain that is strongly nonlinear, and nearly every counterintuitive result here traces back to that.

```
q = eps sigma A (T_h^4 - T_c^4)      sigma = 5.670374419e-08 W/m^2 K^4
```

---

## The fourth power, and what it does to design

The exponent is the whole story.

| Surface temperature | Blackbody emissive power, 1 m^2 |
|---|---|
| 300 K | 459 W |
| 1000 K | 56.7 kW |
| 3000 K | 4.59 MW |

**A surface at 1000 K radiates 124 times what the same surface radiates at 300 K.** That is why radiation is ignorable in a room temperature electronics box and is the only thing keeping an ablative heat shield from consuming itself.

Three design consequences follow directly.

**Radiators want to be hot.** Rejecting 35 W to a 250 K sink takes 0.148 m^2 at 305 K and 0.387 m^2 at 275 K. Thirty kelvin costs a factor of 2.6 in area. Every degree of radiating temperature given away to a conduction path or an interface is paid for in radiator size.

**The sink matters less than it looks.** The same 35 W to deep space at 4 K takes 0.081 m^2 against 0.148 m^2 in low Earth orbit at 250 K. The sink is 246 K colder and the area only halves, because the surface term dominates. A radiator sized for LEO is not badly wrong at GEO.

**An ablative surface finds its own temperature.** The balance between arriving flux and radiated flux has a single solution, and it is an output. Telling the code the surface temperature rather than solving for it is the mistake described in [AeroheatingAndTPS](AeroheatingAndTPS.md).

---

## Absorptivity and emissivity are not one number

Absorptivity is measured against the solar spectrum, which peaks near 0.5 micrometres. Emissivity is measured against the surface's own emission, which at 300 K peaks near 10 micrometres. A real surface can behave completely differently in those two bands, and thermal control coatings exist to exploit exactly that.

| Surface | `alpha` | `eps` | `alpha/eps` | Equilibrium facing the sun |
|---|---|---|---|---|
| Optical solar reflector | 0.08 | 0.80 | 0.10 | 221 K |
| White paint | 0.20 | 0.88 | 0.23 | 272 K |
| Aluminised kapton | 0.40 | 0.80 | 0.50 | 331 K |
| Black paint | 0.95 | 0.88 | 1.08 | 401 K |
| Bare aluminium | 0.15 | 0.05 | 3.00 | 518 K |
| Gold | 0.30 | 0.03 | 10.00 | 700 K |

The equilibrium column is a flat plate normal to the sun at 1361 W/m^2 with no other load, `T = (alpha/eps G / sigma)^0.25`.

**Bare aluminium runs 246 K hotter than white paint in the same place**, despite absorbing less sunlight. It absorbs 0.15 and emits 0.05, so it cannot get rid of what little it takes in. This is the most useful single table in spacecraft thermal control and the one most often misread, because low absorptivity sounds like a cold surface and is not.

**Black paint is a good radiator, not a hot surface.** Its `alpha/eps` is near 1, so in sunlight it runs warm, but out of sunlight it is nearly as good as white paint. Black paint on internal surfaces is a way of coupling a box to itself, and it costs nothing thermally because there is no sun inside.

---

## Degradation

Optical properties change on orbit, and they change in one direction.

Ultraviolet, atomic oxygen and contamination all raise absorptivity. Emissivity is largely unaffected because it is an infrared property and the damage is optical. **So `alpha/eps` rises over the mission, and every surface gets hotter.**

White paint at beginning of life has `alpha` = 0.20 and equilibrates at 272 K. At an end of life `alpha` of 0.35, the same surface reaches 313 K. **A 41 K rise, with no change to the hardware.**

That is why the hot case is an end of life case and the cold case is a beginning of life case. Sizing both at the same optical properties gets one of them wrong, and the two errors are in opposite directions so they do not cancel.

The [environmentsAndLoads](../../environmentsAndLoads/docs/ThermalEnvironments.md) domain owns the degradation model and the case definitions. This domain consumes the resulting properties.

---

## View factors

The view factor `F_ij` is the fraction of radiation leaving surface `i` that arrives at surface `j`. Two rules do most of the work.

```
sum over j of F_ij = 1              a surface sees something in every direction
A_i F_ij = A_j F_ji                 reciprocity
```

**The summation rule is the useful one for sanity checking.** If the view factors from a surface do not sum to one, something is missing from the enclosure, and the thing that is missing is usually space.

For a small object in a large enclosure, `F = 1` and the enclosure's emissivity drops out entirely. This is the case for nearly every spacecraft external surface radiating to space, and it is why the simple form is usually good enough.

For two grey surfaces that see only each other, the exchange includes both emissivities:

```
q = sigma A (T_1^4 - T_2^4) / (1/eps_1 + 1/eps_2 - 1)
```

**That denominator is why two low emissivity surfaces facing each other are a very good insulator**, which is the entire principle of multilayer insulation. Twenty layers of aluminised film do not conduct less; they simply cannot exchange radiation with each other.

---

## Linearising radiation for a network

A resistance network needs a linear conductance, so radiation is written as an equivalent coefficient:

```
h_r = eps sigma (T_h + T_c)(T_h^2 + T_c^2)
R   = 1 / (h_r A)
```

This is algebraically exact at the temperatures used to form it and wrong at any other temperature. **A transient that swings 300 K cannot use a frozen linearisation.** The [ThermalNetwork](ThermalModelling.md) class re-forms it every time step for that reason.

The linearised resistance is also a useful intuition tool. Radiation from a 300 K surface at emissivity 0.85 over 1 m^2 is 0.247 K/W to a 250 K sink and 0.758 K/W to deep space. **The colder sink gives the higher resistance**, which reads wrongly until you notice that the resistance is defined against the total `dT`, and the `dT` grew faster than the flux did.

---

## Design rules of thumb

- **Radiate as hot as the hardware allows.** Area goes as `T^-4` and nothing else in the design is that leveraged.
- **Use `alpha/eps` to choose a coating, not `alpha` alone.** Low absorptivity with low emissivity is a hot surface.
- **Size the hot case at end of life optical properties and the cold case at beginning of life.** They are different analyses.
- **Check that view factors sum to one.** The missing surface is usually space.
- **Assume `F` = 1 to space** for any external surface with a clear hemisphere. The refinement rarely changes a decision.
- **Do not freeze a radiation linearisation across a large transient.**

---

## Failure modes

**Treating `alpha` and `eps` as the same number.** They are measured in different spectral bands and a real coating separates them by an order of magnitude.

**Beginning of life properties used for the hot case.** White paint moves 41 K over a mission. That is larger than most thermal margins.

**A frozen linearisation in a transient.** Correct at one temperature, increasingly wrong away from it.

**A radiator pointed somewhere it should not be.** A sun facing surface sees a 390 K environment and is a heat source. The [Radiator](RadiatorsAndRejection.md) class reports that case as unusable rather than returning a negative area.

**Ignoring radiation because the temperatures are low.** True at 300 K in air. Not true at 300 K in vacuum, where it may be the only mechanism present.

---

## Worked numbers

| Case | Value |
|---|---|
| Blackbody emissive power, 300 K | 459 W/m^2 |
| Blackbody emissive power, 1000 K | 56.7 kW/m^2 |
| Blackbody emissive power, 3000 K | 4.59 MW/m^2 |
| Radiative resistance, eps 0.85, 1 m^2, 300 to 250 K | 0.247 K/W |
| Radiative resistance, eps 0.85, 1 m^2, 300 to 4 K | 0.758 K/W |
| White paint equilibrium, beginning of life | 272 K |
| White paint equilibrium, end of life at `alpha` 0.35 | 313 K |
| Bare aluminium equilibrium | 518 K |
| Gold equilibrium | 700 K |

---

## Standards

| Standard | What it gives you |
|---|---|
| ASTM E903 | Solar absorptance by spectrophotometry |
| ASTM E408 | Total normal emittance |
| ASTM E1918 | Solar reflectance in the field |
| ECSS-Q-ST-70-06 | Particle and molecular contamination control, which drives degradation |
| NASA-HDBK-2001 | Optical property tables and degradation data |

---

## Tool interface

```python
from thermalUtils import STEFAN_BOLTZMANN, SURFACE_PROPERTIES, radiationResistance

for name, entry in SURFACE_PROPERTIES.items():
    ratio = entry['absorptivity'] / entry['emissivity']
    print(f'{name:26s} {ratio:5.2f}')

print(radiationResistance(0.85, 1.0, 300.0, 250.0))
```

`SURFACE_PROPERTIES` is asserted by test to agree with the equivalent table in [environmentsAndLoads](../../environmentsAndLoads/docs/ThermalEnvironments.md), read statically so neither domain imports the other.

---

## References

- Siegel and Howell, *Thermal Radiation Heat Transfer*
- Gilmore, *Spacecraft Thermal Control Handbook*, volume I, chapter 4
- Modest, *Radiative Heat Transfer*
- NASA-HDBK-2001, optical properties and degradation
