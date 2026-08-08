[Home](../README.md) > Convection and Boiling

# Convection and Boiling

## Contents

- [Overview](#overview)
- [What sets the coefficient](#what-sets-the-coefficient)
- [The correlations, and where they stop being true](#the-correlations-and-where-they-stop-being-true)
- [Boiling, which is not a correlation problem](#boiling-which-is-not-a-correlation-problem)
- [Chilldown](#chilldown)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Convection is the mechanism where the physics is easy and the number is not. `q = h A dT` is exact by definition, because `h` is defined to make it exact. Everything difficult about convection is hidden inside `h`, and `h` spans four orders of magnitude across the cases a launch vehicle contains.

| Situation | `h` [W/m^2 K] |
|---|---|
| Natural convection, gas | 2 to 25 |
| Forced convection, gas | 25 to 250 |
| Natural convection, liquid | 50 to 1000 |
| Forced convection, liquid | 100 to 20 000 |
| Nucleate boiling | 3000 to 100 000 |
| Film boiling | 100 to 300 |

**Note that film boiling is worse than forced convection in the same liquid.** That inversion is the single most important fact on this page, and it is the reason cryogenic chilldown is slow and the reason a burnout is a cliff rather than a slope.

**The natural convection correlations for insulated cryogenic surfaces already live in [fluidSystems](../../fluidSystems/fluidSystemsLibrary/docs/Insulation.md)**, in `Insulation._convectionCoefficient`, with the ground hold condensation and liquid air cases. This document covers the physics and the validity limits rather than re-implementing them.

---

## What sets the coefficient

Three dimensionless groups, and knowing which regime a case is in is most of the work.

```
Re = rho V L / mu         inertia to viscous, forced flow
Gr = g beta dT L^3 / nu^2 buoyancy to viscous, natural flow
Pr = mu c / k             momentum to thermal diffusivity, a fluid property
Nu = h L / k              the answer, dimensionless
```

**The regime test is `Gr / Re^2`.** Well below 1 the flow is forced and buoyancy can be ignored. Well above 1 it is natural. Near 1 it is mixed, and mixed convection is where correlations are least reliable and where a lot of real ground hold cases sit.

Prandtl number sorts the fluids and explains why the same geometry behaves differently in each.

| Fluid | `Pr` | Consequence |
|---|---|---|
| Liquid metals | 0.004 to 0.03 | Thermal boundary layer far thicker than the velocity one |
| Gases | about 0.7 | The two boundary layers are comparable |
| Water | 2 to 7 | Thermal layer thinner |
| Oils | 100 to 40 000 | Thermal layer very thin, entrance effects persist |

---

## The correlations, and where they stop being true

Every correlation is a curve fit to a data set, and the data set has edges. Using one outside its range is the most common way to get a confidently wrong number.

| Correlation | Form | Valid for |
|---|---|---|
| Dittus-Boelter | `Nu = 0.023 Re^0.8 Pr^n` | `Re > 10 000`, `0.6 < Pr < 160`, `L/D > 10`, small `dT` |
| Sieder-Tate | `Nu = 0.027 Re^0.8 Pr^(1/3) (mu/mu_w)^0.14` | As above, but large property variation |
| Gnielinski | `Nu = (f/8)(Re - 1000)Pr / (1 + 12.7 sqrt(f/8)(Pr^(2/3) - 1))` | `3000 < Re < 5e6`, the better choice |
| Churchill-Chu | Natural convection, vertical plate | All `Ra`, all `Pr` |
| Vertical plate, laminar | `Nu = 0.59 Ra^0.25` | `10^4 < Ra < 10^9` |
| Vertical plate, turbulent | `Nu = 0.10 Ra^(1/3)` | `Ra > 10^9` |

**`n` in Dittus-Boelter is 0.4 for heating and 0.3 for cooling.** Getting it backwards is a 10 to 15 per cent error that never announces itself.

**Dittus-Boelter is valid for small temperature differences and is used almost exclusively for large ones.** For a cryogenic line at 100 K with a 200 K wall, the property variation across the boundary layer is enormous and Sieder-Tate's viscosity ratio correction exists precisely for that case. The correction is typically 10 to 25 per cent.

**The laminar to turbulent transition in natural convection is at `Ra` around 10^9**, and the exponent changes from 1/4 to 1/3 across it. That matters more than it looks: at `Ra = 1/3` the coefficient becomes independent of length scale, so a taller tank wall does not have a lower coefficient.

---

## Boiling, which is not a correlation problem

The boiling curve is the one place in heat transfer where increasing the driving temperature difference decreases the heat flux, and where the system can jump discontinuously between two stable states.

| Regime | Wall superheat | Behaviour |
|---|---|---|
| Natural convection | 0 to 5 K | No bubbles, ordinary single phase |
| Nucleate | 5 to 30 K | Bubbles form and depart. Extremely effective |
| Critical heat flux | about 30 K | The peak. The last stable nucleate point |
| Transition | 30 to 120 K | Unstable. Flux falls as superheat rises |
| Film | above 120 K | Vapour blanket. Flux an order lower, then rises again by radiation |

**Critical heat flux is a design limit and not a design point.** Past it the surface is blanketed by vapour, the coefficient collapses by two orders, and the wall temperature jumps by hundreds of kelvin in a step. On a heat flux controlled surface, such as a regeneratively cooled chamber wall or an electrically heated element, that jump is burnout and it is not recoverable by backing off slightly. The system has moved to the film branch and stays there until the flux is reduced far below CHF.

For water at atmospheric pressure, CHF is around 1.1 MW/m^2. For cryogens it is far lower, which is why cryogenic chilldown spends most of its time in film boiling.

**The Leidenfrost point is the minimum of the curve**, where film boiling is at its least effective. A cryogen poured onto a warm surface sits in film boiling, insulated from the surface by its own vapour, and transfers heat badly. This is not a nuisance; it is the dominant physics of every chilldown.

---

## Chilldown

Cooling a warm line with a cryogen traverses the boiling curve backwards, and does so slowly.

The line starts far above the Leidenfrost point, so the first contact is film boiling. Vapour blankets the wall, the coefficient is 100 to 300 W/m^2 K, and the wall cools slowly. As it falls the film collapses into transition, then nucleate boiling, where the coefficient jumps by two orders and the remaining cooling happens quickly.

**Most of a chilldown is spent in its worst heat transfer regime.** The consequence is a propellant consumption that is dominated by the film boiling phase and a duration that is not proportional to the thermal mass alone.

The vapour generated during film boiling also has to go somewhere. A chilldown into a closed volume raises pressure, and a chilldown through a pump can produce enough vapour to stall it. The [fluidSystems](../../fluidSystems/fluidSystemsLibrary/docs/CryogenicSystems.md) document owns the system consequences.

---

## Design rules of thumb

- **Check the validity range of every correlation before using it**, and record which one was used. A number without its correlation is not traceable.
- **Use Gnielinski rather than Dittus-Boelter** where the fit matters. It is better behaved near transition and covers a wider Prandtl range.
- **Apply a property correction where `dT` is large.** Sieder-Tate exists for exactly this and is a 10 to 25 per cent effect.
- **Never design at critical heat flux.** Design below it with margin, because the failure past it is discontinuous.
- **Assume film boiling for the start of any chilldown**, and size the propellant consumption on that basis rather than on nucleate coefficients.
- **Check `Gr / Re^2` before assuming forced convection.** Low velocity gas flows on the pad are frequently mixed.

---

## Failure modes

**A correlation used outside its range.** It still returns a number, and the number looks reasonable. This is the defining hazard of convective analysis.

**Nucleate boiling coefficients used for a chilldown.** Optimistic by two orders in the phase that dominates the duration.

**Designing at CHF.** There is no margin on the far side. The transition is a jump, not a slope.

**Ignoring the entrance region.** `L/D > 10` is a real condition, and short passages have coefficients well above the fully developed value.

**Forced convection assumed on the pad.** A vehicle sitting in still air with a cold wall is driving its own natural circulation, and the two mechanisms are comparable.

---

## Worked numbers

| Case | Value |
|---|---|
| Convective resistance at `h` = 500 W/m^2 K, 0.01 m^2 | 0.200 K/W |
| The same resistance as a bare bolted joint in vacuum | 0.200 K/W |

**A 500 W/m^2 K film over 0.01 square metres and a bare bolted vacuum joint over the same area are numerically identical resistances.** That equivalence is worth carrying, because it puts a familiar number on an unfamiliar one.

| Regime | `h` [W/m^2 K] | Ratio to film boiling |
|---|---|---|
| Film boiling | 200 | 1 |
| Forced convection, liquid | 5000 | 25 |
| Nucleate boiling | 30 000 | 150 |

---

## Standards

| Standard | What it gives you |
|---|---|
| ASME PTC 19.23 | Guidance on heat transfer test uncertainty |
| ECSS-E-ST-31C | Thermal control general requirements |
| NASA-HDBK-2001 | Spacecraft thermal control handbook |
| ASTM C177 | Guarded hot plate, for the conductivity inputs correlations need |

---

## Tool interface

This domain models convection as a resistance and takes the coefficient as an input, because the coefficient is a judgement and the domain does not pretend otherwise.

```python
from thermalUtils import convectionResistance, biotNumber

resistance = convectionResistance(500.0, 0.01)
print(biotNumber(500.0, 0.005, 167.0))
```

The natural convection correlations for cryogenic ground hold are implemented in [fluidSystems](../../fluidSystems/fluidSystemsLibrary/docs/Insulation.md), and [ThermalNetwork](ThermalModelling.md) accepts a convective link through `addResistance`.

---

## References

- Incropera and DeWitt, *Fundamentals of Heat and Mass Transfer*, chapters 6 to 10
- Rohsenow, Hartnett and Cho, *Handbook of Heat Transfer*
- Collier and Thome, *Convective Boiling and Condensation*
- Barron, *Cryogenic Heat Transfer*
