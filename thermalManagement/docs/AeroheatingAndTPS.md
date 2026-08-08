[Home](../README.md) > Aeroheating and TPS

# Aeroheating and TPS

## Contents

- [Overview](#overview)
- [Sutton-Graves, and what it says about shape](#sutton-graves-and-what-it-says-about-shape)
- [Peak heating is not peak dynamic pressure](#peak-heating-is-not-peak-dynamic-pressure)
- [How an ablator works](#how-an-ablator-works)
- [The surface temperature is an output](#the-surface-temperature-is-an-output)
- [Recession limited or insulation limited](#recession-limited-or-insulation-limited)
- [Material selection](#material-selection)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Aerodynamic heating is a kinetic energy problem. A vehicle moving at 2400 m/s carries 2.9 MJ per kilogram of air it pushes aside, and a stagnation point converts essentially all of the local flow's kinetic energy into enthalpy. The heat flux that results has to go somewhere, and the choices are: radiate it, absorb it, or carry it away in material that leaves the vehicle.

Thermal protection is the third option, plus as much of the first two as the material can manage.

This document covers ascent heating on a launch vehicle. Entry heating is the same physics at higher velocity, and the same tools apply, but the design problem is different because the integrated load is far larger.

---

## Sutton-Graves, and what it says about shape

The stagnation point cold wall heat flux for a hemisphere:

```
q = K sqrt(rho / R_n) V^3       K = 1.7415e-4 in SI
```

Three exponents, and each is a design statement.

**`V^3`.** Doubling velocity multiplies the heat flux by eight. This is why heating peaks late in ascent and why entry is a categorically harder problem than ascent, not a quantitatively harder one.

**`rho^0.5`.** Density enters weakly. Halving the density only reduces flux by 29 per cent, so climbing out of the atmosphere helps far less than slowing down would.

**`R_n^-0.5`.** A blunter nose has a lower stagnation heat flux. This is the single most important shape result in the field and it is counterintuitive to anyone who expects sharp to be better. Going from a 350 mm nose radius to 50 mm multiplies the stagnation flux by 2.65.

The physics behind the blunt body result is that a blunt nose pushes the bow shock forward and away from the surface, so more of the shock heated gas leaves the region without touching the vehicle. It is the reason every entry vehicle from Mercury onward is blunt, and it is why a sharp nose cone on an ascent vehicle is a thermal decision as much as an aerodynamic one.

| Case | `V` [m/s] | `rho` [kg/m^3] | `R_n` [m] | `q` [MW/m^2] |
|---|---|---|---|---|
| Ascent, small launch vehicle | 2400 | 1.6e-3 | 0.35 | 0.163 |
| Ascent, faster | 3000 | 1.6e-3 | 0.35 | 0.318 |
| Ascent, sharp 50 mm nose | 2400 | 1.6e-3 | 0.05 | 0.431 |
| Low Earth orbit entry, peak | 7500 | 1.0e-4 | 0.50 | 1.039 |
| Lunar return | 11 000 | 2.0e-4 | 1.00 | 3.278 |

**Sharpening the nose of the ascent vehicle costs more heat flux than flying 600 m/s faster does.**

---

## Peak heating is not peak dynamic pressure

Dynamic pressure goes as `rho V^2`. Heat flux goes as `sqrt(rho) V^3`. Both are products of a falling density and a rising velocity, so both have a maximum, but the maxima are at different points on the trajectory.

**Heating peaks later and higher than max-Q**, because the velocity exponent is larger and the density exponent is smaller. A structure sized at max-Q and a heat shield sized at max-Q are not sized at the same condition, and only one of them is right.

The integrated load matters separately from the peak. A short intense pulse and a long mild one can carry the same joules per square metre and require very different protection, because recession follows the integral and insulation depth follows the duration. Both numbers have to come from the trajectory, which is why the [environmentsAndLoads](../../environmentsAndLoads/docs/ThermalEnvironments.md) domain owns them.

---

## How an ablator works

An ablative material rejects heat by four mechanisms at once, and the accounting matters because they scale differently.

**Blowing blockage.** Pyrolysis gas leaving the surface thickens the boundary layer and reduces the convective flux arriving at it. The reduction is typically 20 to 40 per cent; the [AblativeTPS](#tool-interface) class uses 30 per cent as a default, which is conservative for high blowing rates and about right for ascent.

**Radiation from the hot surface.** The surface is at 1000 to 3600 K depending on the material, and `sigma T^4` at those temperatures is large. **For a high temperature ablator at moderate flux, radiation rejects essentially all of the arriving heat and there is no recession at all.**

**Heat of ablation.** The energy consumed by pyrolysis, decomposition and mass loss, per kilogram removed. This is the term that produces recession, and it only operates on the flux that remains after the first two.

**Insulation by the char and virgin layers.** What is left after all of the above still has to be stopped from reaching the structure, and that is a conduction problem through a low conductivity solid.

| Material | Heat of ablation [MJ/kg] | Density [kg/m^3] | Virgin `k` [W/m K] | Surface `T` [K] |
|---|---|---|---|---|
| Cork | 6.5 | 480 | 0.07 | 1000 |
| Silica phenolic | 11.6 | 1730 | 0.55 | 2800 |
| Carbon phenolic | 21.0 | 1450 | 0.60 | 3600 |
| PICA | 26.0 | 270 | 0.13 | 3000 |

---

## The surface temperature is an output

The tabulated surface temperature is the temperature at which a material ablates hard. It is not a property the material has at all times.

The correct statement is an energy balance. Of the arriving flux, blowing blocks some fraction. What reaches the surface is either radiated away or drives recession. If the flux that reaches the surface can be radiated entirely at a temperature below the ablation temperature, **the surface sits at that radiative equilibrium and does not recede.**

```
T_eq = (q_blocked / (eps sigma))^0.25
ablating if T_eq >= T_ablation
```

This is not a detail. At the 0.163 MW/m^2 ascent case, the blocked flux gives a radiative equilibrium of 1240 K. Cork ablates at 1000 K, so cork recedes. **Silica phenolic, carbon phenolic and PICA all ablate above 2800 K, so at this flux none of them recede at all.** They are pure insulators here, and their heat of ablation is irrelevant.

Treating the tabulated temperature as an input rather than an output does two things wrong at once. It reports recession that does not happen, and it drives the net flux calculation against a surface far hotter than the real one, which oversizes the insulation. This was a real bug in this library and it is guarded by a regression test.

**A second version of the same trap:** the peak flux may ablate while the mean flux does not. A single calculation run at the mean reports zero recession and misses the peak entirely. The class flags that case explicitly rather than letting it pass.

---

## Recession limited or insulation limited

The total thickness is recession plus insulation plus margin, and which term dominates decides what to do about it.

**Insulation limited** means the thickness is set by keeping the backface cool for the duration. The lever is a lower virgin conductivity, and heat of ablation is nearly irrelevant.

**Recession limited** means the material is being consumed faster than it insulates. The lever is a higher heat of ablation or a higher surface temperature, and conductivity is secondary.

The transition happens with flux, not material, and the same material can be on either side of it.

| Flux [MW/m^2] | Cork recession [mm] | Cork total [mm] | Limited by |
|---|---|---|---|
| 0.163 | 2.96 | 11.48 | Insulation |
| 0.500 | 13.54 | 24.71 | Recession |
| 2.000 | 60.66 | 83.60 | Recession |

**Cork at 2 MW/m^2 recedes 61 mm and is a bad answer.** At 0.163 MW/m^2 it recedes 3 mm and is the right one. The material did not change; the flux did.

---

## Material selection

The selection is not on heat of ablation. It is on areal mass, which is thickness times density, and the two terms fight each other.

At the ascent case, 0.163 MW/m^2 over 140 seconds:

| Material | Thickness [mm] | Areal mass [kg/m^2] | Recedes |
|---|---|---|---|
| Cork | 11.48 | 5.51 | Yes |
| Silica phenolic | 15.75 | 27.24 | No |
| PICA | 17.20 | 4.64 | No |
| Carbon phenolic | 17.69 | 25.65 | No |

**PICA is the thickest and the lightest.** It needs 50 per cent more thickness than cork and weighs 16 per cent less, because its density is 270 kg/m^3 against cork's 480. Silica phenolic is thinner than PICA and weighs six times as much.

At 2 MW/m^2 the gap becomes decisive: PICA at 5.77 kg/m^2 against silica phenolic at 33.85. **This is the entire argument for low density ablators**, and it is a density argument rather than a chemistry one.

Cork remains the ascent answer for a small launch vehicle because it is cheap, well understood, sprayable, and at 5.51 against 4.64 kg/m^2 the mass penalty against PICA is 0.87 kg per square metre. Over the 0.55 m^2 nose cap in the worked example that is under half a kilogram, and PICA is not sprayable.

---

## Design rules of thumb

- **Size at peak heating, not max-Q.** They are different trajectory points.
- **Blunt the nose if the thermal problem is hard.** Flux goes as `R_n^-0.5` and it is usually the cheapest lever available.
- **Solve for the surface temperature rather than asserting it.** Below the flux that sustains ablation, the material does not recede.
- **Check the peak and the mean separately.** A mean flux calculation can report no ablation on a surface that ablates at peak.
- **Select on areal mass.** Thickness alone rewards dense materials that are the wrong answer.
- **Know which limit you are on.** Insulation limited wants lower conductivity; recession limited wants higher heat of ablation. Optimising the wrong one does nothing.
- **Add margin on thickness, not on flux.** The margin is for manufacturing and property scatter, and it belongs where those live.

---

## Failure modes

**Surface temperature treated as an input.** Reports recession that does not occur and oversizes insulation against a fictitious hot surface.

**Mean flux only.** Misses a peak that ablates.

**Sized at max-Q.** Undersized, because peak heating is later.

**Selected on heat of ablation.** PICA and carbon phenolic have comparable heats of ablation and differ by a factor of five in areal mass.

**Cold wall flux used as hot wall flux.** Sutton-Graves gives the cold wall value. The hot wall flux is lower, and using cold wall throughout is conservative but can be conservative by a large factor at high surface temperature.

**Backface limit taken as the structure limit.** The backface of the TPS is not the structure temperature. Heat continues to flow inward after the pulse ends, which is the soakback problem in [ThermalModelling](ThermalModelling.md).

---

## Worked numbers

All produced by running the code, at 0.163 MW/m^2 peak, 22.8 MJ/m^2 integrated, 140 s, 420 K backface limit, 1.25 margin.

| Quantity | Value |
|---|---|
| Blowing blockage | 30 % |
| Flux reaching the surface | 0.114 MW/m^2 |
| Radiative equilibrium temperature | 1240 K |
| Cork ablation temperature | 1000 K, so cork ablates |
| Flux driving recession | 0.066 MW/m^2 |
| Recession depth | 2.96 mm |
| Insulating depth | 6.22 mm |
| Total thickness | 11.48 mm |
| Areal mass | 5.51 kg/m^2 |
| Governing limit | Insulation, recession is 26 % of the total |
| Shield mass over 0.55 m^2 | 3.03 kg |

---

## Standards

| Standard | What it gives you |
|---|---|
| NASA SP-8014 | Entry thermal protection, the design monograph |
| NASA SP-8029 | Aerodynamic and rocket exhaust heating during launch and ascent |
| ASTM E285 | Oxyacetylene ablation testing |
| ASTM E457 | Thermal flux measurement by calorimeter |
| ASTM E511 | Heat flux measurement with a circular foil gauge |
| MIL-HDBK-17 | Composite materials handbook, for the phenolics |

---

## Tool interface

```python
from AblativeTPS import AblativeTPS

shield = AblativeTPS()
shield.setInputs({'material':           'cork',
                  'peakHeatFlux':       1.63e5,
                  'heatLoad':           2.28e7,
                  'pulseDuration':      140.0,
                  'backfaceLimit':      420.0,
                  'initialTemperature': 293.15,
                  'thicknessMargin':    1.25})

flux = shield.calculateNetHeatFlux()
print(flux['isAblating'], flux['surfaceTemperature'])

sizing = shield.sizeThickness()
print(sizing['totalThickness'], sizing['limitedBy'])

for name, entry in shield.compareMaterials()['materials'].items():
    print(f'{name:18s} {entry["arealMass"]:6.2f} kg/m^2')
```

The [worked example](../codeInterface.py) runs this and carries the backface temperature into a [ThermalNetwork](ThermalModelling.md) to find what happens behind it.

---

## References

- Sutton and Graves, *A general stagnation point convective heating equation for arbitrary gas mixtures*, NASA TR R-376
- Anderson, *Hypersonic and High Temperature Gas Dynamics*
- NASA SP-8014, *Entry thermal protection*
- Tran et al., *Phenolic Impregnated Carbon Ablators for Discovery class missions*
- Laub and Venkatapathy, *Thermal protection system technology and facility needs*
