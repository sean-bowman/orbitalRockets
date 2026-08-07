[Home](../../README.md) > Insulation

# Insulation

## Contents

- [Overview](#overview)
- [Governing physics](#governing-physics)
  - [The resistance network](#the-resistance-network)
  - [Surface coefficients](#surface-coefficients)
  - [Critical insulation radius](#critical-insulation-radius)
- [Insulation systems](#insulation-systems)
  - [Foam](#foam)
  - [Multilayer insulation](#multilayer-insulation)
  - [Vacuum jackets and evacuated powder](#vacuum-jackets-and-evacuated-powder)
  - [Aerogel](#aerogel)
- [Boil-off](#boil-off)
- [Condensation, frost and liquid air](#condensation-frost-and-liquid-air)
- [Penetrations and real-world degradation](#penetrations-and-real-world-degradation)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Operations](#operations)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Insulation on a fluid system does one of three jobs, and which one it is determines how it is sized:

| Job | Sizing criterion | Typical application |
|---|---|---|
| Limit heat leak into a cryogen | Heat rate [W] | Propellant tank, transfer line, hold time |
| Keep a surface above a temperature | Surface temperature [K] | Prevent condensation, frost or liquid air on a cold line |
| Keep a surface below a temperature | Surface temperature [K] | Touch limit or structural limit on a hot line |

These are different constraints and they give different thicknesses, so all of them have to be evaluated. On a cryogenic line the heat leak target comes from the boil-off allowance and the surface temperature target comes from the requirement not to condense liquid air, and which one governs is not obvious in advance.

The one thing that must be internalized about cryogenic insulation is that **the best insulations are not conduction-limited at all.** Multilayer insulation works by suppressing radiation between many reflective layers in a vacuum, and its effective conductivity depends on layer density and interstitial gas pressure far more than on any material property. That makes it fragile in a way foam is not: a slowly failing vacuum jacket gives no external sign until the boil-off rate is measured.

---

## Governing physics

### The resistance network

One-dimensional steady conduction through the insulation in series with convection and radiation at the outer surface.

**Cylindrical:**

```
R_conduction = ln(r_outer / r_inner) / (2 * pi * k * L)
R_surface    = 1 / ( (h_convection + h_radiation) * A_outer )
Q            = (T_ambient - T_inner) / (R_conduction + R_surface)
T_surface    = T_ambient - Q * R_surface
```

**Planar:**

```
R_conduction = t / (k * A)
```

The surface resistance is nonlinear, because the radiation coefficient depends on the surface temperature which depends on the heat rate which depends on the resistance. The [`Insulation`](../Insulation.py) class iterates to convergence.

**The surface resistance is not negligible.** On a well-insulated cryogenic line the conduction resistance dominates and the surface term is a few percent. On a thinly insulated or bare line the surface term can be most of the total, and an insulation calculation that omits it will over-predict the heat leak substantially. In the worked example below the surface term is 7 percent of the total, and at half the thickness it would be 14 percent.

### Surface coefficients

**Natural convection** from a horizontal cylinder:

```
Ra = g * beta * |T_s - T_inf| * L^3 / (nu * alpha)
Nu = C * Ra^n
```

with `C = 0.53, n = 0.25` for `1e4 < Ra < 1e9` and `C = 0.13, n = 1/3` above that. `L` is the outer diameter. Air properties are evaluated at the film temperature and `beta = 1/T_film` for an ideal gas.

The number to keep in your head for **still air is 3 to 10 W/m^2-K**.

**Forced convection** (Hilpert, cross flow over a cylinder):

```
Nu = C * Re^m * Pr^(1/3)
```

| Re | C | m |
|---|---|---|
| 0.4 to 4 | 0.989 | 0.330 |
| 4 to 40 | 0.911 | 0.385 |
| 40 to 4 000 | 0.683 | 0.466 |
| 4 000 to 40 000 | 0.193 | 0.618 |
| 40 000 to 400 000 | 0.027 | 0.805 |

**Wind matters more than people expect.** A 5 m/s breeze roughly triples the surface coefficient relative to still air, which on a thinly insulated line can double the heat leak. Outdoor ground systems must be sized for wind, and the wind case is often what sets the thickness rather than the still-air case.

**Radiation**, linearized about the current surface temperature:

```
h_radiation = eps * sigma * (T_sink^2 + T_s^2) * (T_sink + T_s)
```

For a surface near 290 K with `eps = 0.9`, this is about 5 W/m^2-K, comparable to natural convection. Radiation is not a small correction on a still-air surface; it is roughly half the total.

**In space the sink temperature is not ambient.** Use the effective radiative sink (deep space at about 4 K, or a planetary body's effective temperature) and note that convection is zero. On-orbit insulation is an entirely radiative problem.

### Critical insulation radius

```
r_critical = k / h
```

Adding insulation to a cylinder does two opposing things: it increases the conduction resistance (good) and it increases the outer surface area, which decreases the surface resistance (bad). Below the critical radius the second effect wins and **adding insulation increases the heat loss.**

For typical foam on a small tube with natural convection, `k = 0.026 W/m-K` and `h = 9.6 W/m^2-K` gives `r_critical = 2.7 mm`, which is smaller than most pipes. So in practice the critical radius rarely bites on insulation.

Where it does bite is on **small-diameter items with a relatively high-conductivity covering**: an instrumentation line, a small tube, or an electrical cable with a plastic jacket. There the jacket can genuinely increase the heat loss, which is precisely why electrical cable insulation is designed as a heat-shedding feature rather than a heat-retaining one.

---

## Insulation systems

| System | k [W/m-K] | Density [kg/m^3] | Vacuum? | Temp range [K] |
|---|---|---|---|---|
| Polyurethane foam (SOFI) | 0.026 | 35 | No | 20 to 400 |
| Polyisocyanurate board | 0.023 | 40 | No | 20 to 420 |
| Aerogel blanket | 0.014 | 150 | No | 4 to 920 |
| Mineral wool | 0.040 | 100 | No | 200 to 920 |
| Ceramic fiber | 0.10 | 128 | No | 290 to 1600 |
| Evacuated perlite | 0.0009 | 130 | **Yes** | 4 to 1000 |
| Bare vacuum annulus | 1e-4 | 0 | **Yes** | 4 to 800 |
| MLI, 20 layer | 5e-5 | 60 | **Yes** | 4 to 400 |
| MLI, 60 layer | 2e-5 | 60 | **Yes** | 4 to 400 |

The spread from foam to good MLI is a factor of **700**, and the entire difference is that MLI works in a vacuum and foam does not. That is the central trade in cryogenic insulation: a vacuum jacket is heavy, expensive and can fail, and nothing else comes close to it.

### Foam

Sprayed-on foam insulation (SOFI) was the Shuttle external tank standard and remains the default for large flight cryogenic tanks. It is cheap, light, applied in place, and it needs no vacuum jacket.

Its failure mode is moisture. Foam must be **closed cell and sealed**, because:

- Open cells take on atmospheric moisture, and wet foam conducts far better than dry foam
- Worse, on a cryogenic surface the foam **cryopumps**: air diffuses in, liquefies against the cold face, and the resulting liquid air both destroys the insulating value and creates an oxygen-enrichment hazard inside the insulation
- The trapped liquid or ice then boils or sublimes on warmup, which can debond the foam

The Shuttle foam-shedding problem was a debonding-and-cryopumping problem, and it is the reason foam application, void control and inspection are so heavily controlled on flight tanks.

### Multilayer insulation

MLI is many layers of reflective film (typically aluminized Mylar or Kapton) separated by a low conductivity spacer (Dacron netting, silk net, or embossing), in a vacuum.

Radiation between two parallel surfaces scales as `1/(N+1)` for `N` shields, so 20 layers cut the radiative transfer by a factor of 21. In a good vacuum that leaves only:

- Solid conduction through the spacers and through layer-to-layer contact
- Residual gas conduction
- Radiation through the seams and penetrations

**Two design variables dominate:**

1. **Layer density.** Too loose and there are not enough layers per unit thickness; too tight and the layer-to-layer contact conduction takes over. The optimum is around 20 to 30 layers per cm, and **MLI compressed around a tight radius or under a strap performs far worse locally.**
2. **Interstitial pressure.** Below 1e-3 Pa the residual gas contributes nothing. Above 1 Pa the gas conduction dominates and the MLI performs no better than a bare vacuum gap, a degradation of **two orders of magnitude**.

Diminishing returns set in above roughly 40 layers, because solid conduction rather than radiation becomes the limit.

**Pump-down time** is a real design constraint. Each layer traps gas and the conductance out of a multilayer stack is very low, so evacuating a 60-layer blanket can take days. Perforated layers are used to speed it up, at a small radiative penalty.

### Vacuum jackets and evacuated powder

A vacuum jacket is a second pressure boundary around the line or vessel with the annulus evacuated. It provides the vacuum that MLI or evacuated perlite needs and it is itself a significant heat leak path through:

- The **supports** that hold the inner vessel concentric. These are the dominant conduction path and they are designed as long, thin, low-conductivity struts (G-10 fiberglass, or a long thin stainless tube) for exactly that reason.
- The **fill and vent penetrations**, which are direct metal paths from cold to warm. Vapor-cooled shields, which route the boil-off vapor along the penetration to intercept the heat, are the standard mitigation on high-performance dewars.

**Evacuated perlite** fills the annulus with expanded perlite powder and evacuates it. It is the standard for large cryogenic storage tanks: it fills any shape, it is cheap by volume, and it is tolerant of the annulus geometry. Its drawback is that it **settles** over time, opening voids at the top of a vertical annulus where the insulation is then absent.

### Aerogel

Silica aerogel in a flexible fiber batting. The best non-vacuum insulation available, usable from 4 K to 920 K, and it does not require a jacket. Its drawbacks:

- Expensive
- Dusty and unpleasant to install (respiratory protection required)
- **Compresses under load**, and compressed aerogel conducts substantially better. Strapping or clamping aerogel blanket degrades it exactly where the strap is.

It is the right answer for a line that must be insulated without a vacuum jacket and where foam is inadequate.

---

## Boil-off

```
mdot_boiloff = Q / h_fg
```

This assumes the tank is **vented** and sitting at its saturation pressure. A locked-up tank does not boil off; it self-pressurizes, and the heat leak goes into raising the ullage pressure instead. That is a different and considerably more dangerous calculation, and it is why cryogenic tanks have relief devices.

Latent heats and the volumetric comparison, at one atmosphere:

| Fluid | T_sat [K] | h_fg [kJ/kg] | rho_liquid [kg/m^3] | h_fg x rho [MJ/m^3] |
|---|---|---|---|---|
| LH2 | 20.3 | 446 | 71 | **31.6** |
| LCH4 | 111.7 | 511 | 423 | 216 |
| LN2 | 77.4 | 199 | 807 | 161 |
| LOX | 90.2 | 213 | 1141 | **243** |

**Hydrogen has by far the highest latent heat per unit mass**, which sounds favorable until you note the density. The latent heat per unit **volume** is 31.6 MJ/m^3 against 243 MJ/m^3 for LOX. For the same heat leak per unit tank volume, a hydrogen tank boils off roughly **eight times as fast** as an oxygen tank. That, plus the much larger tank volume per unit mass of propellant, is why hydrogen insulation is such a disproportionate part of a hydrolox vehicle.

**Hold time** is the operationally meaningful number:

```
t_hold = (allowable mass loss) / mdot_boiloff
```

and it is what determines whether a vehicle can sit on the pad through a hold, and how much topping capacity the ground system needs.

---

## Condensation, frost and liquid air

Three thresholds on the outer surface temperature, in increasing severity.

**1. Below the dew point: water condenses.** A nuisance on most systems and a serious problem on anything electrical or on any insulation that is not vapor sealed, because wet insulation conducts far better than dry insulation and the problem is self-reinforcing. Dew point from the Magnus formula:

```
gamma = 17.625 * T_C / (243.04 + T_C) + ln(RH)
T_dew = 243.04 * gamma / (17.625 - gamma)      [degC]
```

At 20 degC and 60 percent relative humidity the dew point is 12.0 degC (285.1 K).

**2. Below 273 K: frost forms.** Frost is itself an insulator so it partially self-limits, but it adds mass, it sheds in sheets, and it hides the surface from inspection. On a flight vehicle, shed ice is a debris hazard.

**3. Below 90 K: LIQUID AIR.** This is a hazard, not an inconvenience.

Air condensing on a surface below 90 K is **oxygen enriched**, because oxygen liquefies at 90 K and nitrogen at 77 K, so the first condensate is roughly 50 percent oxygen against the 21 percent in air. As it sits and the nitrogen preferentially evaporates, it enriches further.

That liquid drips onto whatever is below it. If what is below it is asphalt, an organic coating, a polymer, or contaminated insulation, the result is an **impact-sensitive explosive**. This is a documented and repeated accident mechanism.

Consequences for design:

- Bare LH2 and LHe lines are never routed above anything
- A vacuum-jacketed line is used rather than a foam-insulated one wherever the surface would otherwise go below 90 K
- Where liquid air cannot be avoided, a drip pan of a compatible material and a controlled drain path are provided
- Concrete rather than asphalt under any cryogenic hardware
- A dry gas (GN2) purge in the insulation annulus prevents air ingress entirely and is the standard solution on ground systems

---

## Penetrations and real-world degradation

**Insulation performance is degraded by everything a real installation contains,** and the degradation is large.

| Degradation | Typical factor |
|---|---|
| MLI seams, overlaps and closeouts | 1.5 to 3 |
| Structural supports through the insulation | 1.5 to 5, depending on support design |
| Fill, vent and instrumentation penetrations | 1.2 to 2 |
| Compression around bends and under straps | 1.2 to 2 locally |
| Combined, small highly penetrated vessel | **3 to 5** |
| Combined, large simple vessel | **1.5 to 2** |

A laboratory coupon measurement of MLI effective conductivity is a lower bound and nothing more. The [`Insulation`](../Insulation.py) class carries an explicit `penetrationFactor` defaulting to 2.0 for exactly this reason, and it should be raised for a small, complex installation.

**Supports are usually the dominant single penetration.** A stainless support strut is a direct conduction path of 16 W/m-K bridging the insulation entirely. The mitigations are:

- Long, thin struts (maximize `L/A`)
- Low conductivity materials: G-10 fiberglass (0.3 W/m-K), Ti-6Al-4V (6.7 W/m-K)
- **Vapor cooling**: route the boil-off vapor along the strut to intercept the heat before it reaches the cold end. Highly effective and essentially free, because the vapor is being vented anyway

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Still-air surface coefficient | 3 to 10 W/m^2-K including radiation | The anchor number |
| Radiation share on a still-air surface | ~50 % | Not a small correction |
| Wind at 5 m/s | Roughly 3x the still-air coefficient | Size ground systems for wind |
| MLI vacuum requirement | < 1e-3 Pa | Above 1 Pa it is worthless |
| MLI layer density | 20 to 30 layers/cm | Tighter increases contact conduction |
| MLI diminishing returns | Above ~40 layers | Solid conduction takes over |
| Real installation degradation | 2 to 5x the coupon value | Seams, supports, penetrations |
| Critical radius for foam on a small tube | ~3 mm | Rarely governs for insulation |
| Liquid air threshold | 90 K surface temperature | Hard hazard limit |
| Hydrogen boil-off per unit volume | ~8x oxygen | Sets hydrolox insulation mass |
| Support design | Maximize L/A, use G-10, vapor cool | Supports dominate the penetration budget |
| Foam must be closed cell and sealed | Always | Cryopumping and moisture |
| Aerogel under compression | Degraded | Do not strap over it |

---

## Failure modes

**Vacuum loss.** The dominant cryogenic insulation failure. A small leak in the jacket, or outgassing from the annulus over time, raises the interstitial pressure and the heat leak rises by up to two orders of magnitude. **There is no external sign.** The vessel looks identical. It is detected by boil-off rate, by frost appearing on the outer jacket, or by an annulus pressure gauge, which is why vacuum-jacketed hardware is instrumented for annulus pressure.

**Foam cryopumping.** Air diffuses into an unsealed or damaged foam, liquefies against the cold face, destroys the insulating value, and creates an oxygen-enriched liquid inside the insulation.

**Foam debonding and shedding.** Thermal cycling plus trapped gas plus poor surface preparation. A flight debris hazard.

**Perlite settling.** Voids open at the top of a vertical annulus and the heat leak concentrates there.

**MLI compression.** Locally crushed insulation at a strap, a bend or a support performs dramatically worse than the average, and the heat leak concentrates at exactly those points.

**Moisture ingress into non-sealed insulation.** Wet insulation conducts far better, and on a cold line the water freezes and expands, mechanically damaging the insulation.

**Ice formation and shedding.** Adds mass, breaks off in sheets, hides the surface from inspection, and on a launch vehicle is a debris hazard to whatever is downstream.

**Liquid air condensation.** The hazard case, covered above.

**Insulation on a hot line trapping a leak.** Insulation over a hot hydrocarbon line can absorb a small leak and hold it against a hot surface, which is a classic industrial autoignition mechanism. It applies to any absorbent insulation over any flammable-fluid line.

---

## Operations

**Instrument the annulus pressure** on any vacuum-jacketed hardware. It is the only warning you get.

**Measure boil-off** as an acceptance test and periodically thereafter. A rising boil-off rate is the integrated health indicator for the whole insulation system.

**Inspect for frost patterns.** A cold spot on the outer surface of an insulated line is a local insulation failure, and frost makes it visible for free.

**Do not walk on, lean on, or strap over insulation.** Compression is permanent damage to MLI and aerogel.

**Purge the annulus with dry gas** on any ground insulation system that is not evacuated. It prevents air ingress, moisture and cryopumping in one step.

**Keep organics away from anything below 90 K.** No asphalt, no oil, no polymer sheeting under a cryogenic line.

**Re-evacuate on a schedule.** Vacuum annuli degrade through outgassing even without a leak, and periodic pump-down is a maintenance item, not a repair.

---

## Worked example

A 50.8 mm OD LOX transfer line, 10 m long, 25 mm of polyurethane foam, 90.17 K contents, 293.15 K ambient, still air, 60 percent relative humidity.

| Quantity | Value |
|---|---|
| Effective conductivity | 0.026 W/m-K |
| Conduction resistance | 0.4195 K/W |
| Surface resistance | 0.0328 K/W (7 % of total) |
| Convection coefficient | 4.85 W/m^2-K |
| Radiation coefficient | 4.77 W/m^2-K |
| **Heat leak** | **448.8 W** |
| Heat flux | 141.7 W/m^2 |
| **Surface temperature** | **278.4 K** |
| Dew point | 285.1 K |
| **Condensation risk** | **Water condensation** |
| Insulation mass | 2.08 kg |
| Critical radius | 2.70 mm |

**Boil-off** for a 1 m^3 tank at 95 percent fill:

| Quantity | Value |
|---|---|
| LOX latent heat at 90.17 K | 213.1 kJ/kg |
| Boil-off rate | 2.11 g/s |
| Boil-off per day | 182.0 kg/day |
| Liquid mass | 1084 kg |
| Fraction lost per day | 16.8 % |
| Hold time to 10 % loss | 14.3 hours |

**Two things this result tells you.** The surface at 278.4 K is below the 285.1 K dew point, so this line will run wet and the foam must be vapor sealed. And 16.8 percent per day is a very high boil-off rate for a transfer line, which is expected: this is a line, not a well-insulated dewar, and the surface-to-volume ratio is unfavorable. If this heat leak were unacceptable, the choices are more foam (diminishing returns, and the surface temperature only rises slowly) or a vacuum jacket (a factor of several hundred, at a large cost in mass and complexity).

**Sizing for a surface temperature target of 275 K** gives 20.2 mm of foam and a 516 W heat leak.

The direction is worth being explicit about, because it is easy to get backwards. On a **cold** line, more insulation raises the outer surface toward ambient. So a surface temperature target is a **minimum**, and the thickness that exactly meets it is the **minimum acceptable** thickness: 20.2 mm gives 275.0 K, and the 25 mm design gives a warmer 278.4 K with a lower heat leak. On a **hot** line the sense reverses: the surface temperature target is a maximum and thicker insulation drives the surface down toward it. The [`Insulation`](../Insulation.py) class solves for the exact match in both cases; deciding which side of it you need is the engineer's job.

Reproduce with:

```python
from Insulation import Insulation

line = Insulation()
line.setInputs({'material': 'polyurethane foam', 'geometry': 'cylindrical',
                'innerDiameter': 0.0508, 'thickness': 0.025, 'length': 10.0,
                'innerTemperature': 90.17, 'ambientTemperature': 293.15,
                'relativeHumidity': 0.6, 'fluid': 'Oxygen'})

line.calculateHeatLeak()
line.calculateCriticalRadius()
line.calculateBoilOff(tankVolume = 1.0)
print(line.generateReport())
```

---

## Standards

| Standard | Scope |
|---|---|
| ASTM C177 | Steady-state heat flux and thermal transmission by the guarded hot plate |
| ASTM C335 | Steady-state heat transfer properties of pipe insulation |
| ASTM C518 | Steady-state thermal transmission by heat flow meter apparatus |
| ASTM C740 | Evacuated reflective insulation in cryogenic service |
| ASTM C1774 | Thermal performance testing of cryogenic insulation systems |
| ISO 21014 | Cryogenic vessels, cryogenic insulation performance |
| CGA H-3 | Cryogenic hydrogen storage |
| NASA-STD-8719.17 | Ground-based pressure vessels and pressurized systems |
| NASA SP-8080 | Liquid rocket propellant tank pressurization |
| ASTM G93 | Cleaning methods and cleanliness levels for material and equipment used in oxygen-enriched environments |

---

## Tool interface

The [`Insulation`](../Insulation.py) class covers the resistance network, sizing, boil-off, condensation and the critical radius.

```python
from Insulation import Insulation

insulation = Insulation()
insulation.setInputs({'material': 'mli 20 layer', 'geometry': 'cylindrical',
                      'innerDiameter': 0.0508, 'length': 10.0,
                      'innerTemperature': 90.17, 'ambientTemperature': 293.15,
                      'annulusPressure': 1e-4, 'penetrationFactor': 3.0,
                      'fluid': 'Oxygen'})

insulation.sizeThickness(targetHeatLeak = 5.0)          # or targetSurfaceTemperature, or both
insulation.calculateHeatLeak()
insulation.calculateBoilOff(tankVolume = 1.0, fillFraction = 0.95)
insulation.checkCondensation()
insulation.calculateCriticalRadius()
print(insulation.generateReport())
```

Lookup table: `Insulation.INSULATION_MATERIALS`. Vacuum thresholds: `Insulation.MLI_VACUUM_THRESHOLD_GOOD`, `Insulation.MLI_VACUUM_THRESHOLD_LOST`. Liquid air limit: `Insulation.LIQUID_AIR_THRESHOLD`.

---

## References

1. Barron, R. F., *Cryogenic Heat Transfer*, 2nd ed., CRC Press, 2016.
2. Barron, R. F., *Cryogenic Systems*, 2nd ed., Oxford University Press, 1985.
3. Incropera, F. P. and DeWitt, D. P., *Fundamentals of Heat and Mass Transfer*, 6th ed., Wiley, 2007.
4. Fesmire, J. E. and Augustynowicz, S. D., "Thermal Performance Testing of Cryogenic Insulation Systems", NASA Kennedy Space Center, *Thermal Conductivity 29*, 2007.
5. Lockheed Missiles and Space Company, *Basic Investigations of Multi-Layer Insulation Systems*, NASA CR-54191, 1964 (the Lockheed MLI equation).
6. Timmerhaus, K. D. and Flynn, T. M., *Cryogenic Process Engineering*, Plenum Press, 1989.
7. NASA SP-8080, *Liquid Rocket Propellant Tank Pressurization*, 1975.
8. Churchill, S. W. and Chu, H. H. S., "Correlating Equations for Laminar and Turbulent Free Convection from a Horizontal Cylinder", *International Journal of Heat and Mass Transfer*, Vol. 18, 1975.
