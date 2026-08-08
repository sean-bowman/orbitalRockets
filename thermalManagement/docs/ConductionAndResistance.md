[Home](../README.md) > Conduction and Resistance

# Conduction and Resistance

## Contents

- [Overview](#overview)
- [The resistance formulation](#the-resistance-formulation)
- [Contact conductance, which is where the resistance actually is](#contact-conductance-which-is-where-the-resistance-actually-is)
- [Series and parallel](#series-and-parallel)
- [Transient conduction](#transient-conduction)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Conduction is the mechanism with the cleanest physics and the worst reputation for being modelled badly, because the equation is trivial and the input that dominates the answer is not in the equation at all.

Fourier's law in one dimension gives a resistance:

```
R = L / (k A)      [K/W]
```

That is the whole of steady conduction through a uniform slab. The difficulty is never this expression. It is that a real thermal path is a chain of these, the chain includes interfaces, and the interfaces are usually larger than the metal.

---

## The resistance formulation

Treating each element as a resistance is worth doing even when the intention is a full numerical model, because it makes the dominant term visible before any solving happens.

| Element | Resistance |
|---|---|
| Conduction through a slab | `L / (k A)` |
| Contact across an interface | `1 / (h_c A)` |
| Convection at a surface | `1 / (h A)` |
| Radiation, linearised | `1 / (h_r A)`, `h_r = eps sigma (T_h + T_c)(T_h^2 + T_c^2)` |

**The radiation entry is a linearisation and has to be recomputed as temperatures change.** It is exact at the temperatures used to form it and wrong everywhere else, which is acceptable for network assembly and not acceptable for a transient across a large temperature swing. The [ThermalNetwork](ThermalModelling.md) class re-forms it at each step rather than freezing it.

---

## Contact conductance, which is where the resistance actually is

Two solid surfaces bolted together touch over a small fraction of their apparent area. Heat crosses through the contact spots, through whatever fills the gaps, and by radiation across them. In vacuum the middle term disappears, which is why the same joint is four times worse in orbit than on the bench.

| Joint | `h_c` [W/m^2 K] | Note |
|---|---|---|
| Deliberate isolator | 50 | A designed thermal break |
| **Bolted, bare, vacuum** | **500** | **The common case, and very variable** |
| Bolted, bare, air | 2000 | Trapped air conducts across the gap |
| Bonded, thermally filled | 5000 | Filled adhesive |
| Bolted, with grease | 8000 | Grease fills the asperities |
| Bolted, with indium foil | 20 000 | Soft metal foil, the good option |
| Welded or integral | 1 000 000 | Effectively no interface |

**That table spans a factor of four hundred, and a factor of forty across the options an engineer actually chooses between.** No material property in this domain varies that much. Conductivity across the whole set of structural metals spans about a factor of twenty, from titanium at 7 W/m K to aluminium at 167.

The practical consequence is an ordering rule. Model the interfaces before refining the metal, because the uncertainty in one bolted joint in vacuum exceeds the entire difference between two candidate alloys.

**The values above are representative, not design values.** Real contact conductance depends on bolt preload, surface finish, flatness, and how many times the joint has been taken apart. A factor of two either way on the bare vacuum number is normal. That uncertainty is the reason the [ThermalNetwork](ThermalModelling.md) class reports what fraction of the total resistance sits in contact interfaces: it is telling the reader how much of the answer is built on a soft number.

---

## Series and parallel

Resistances in series add. Resistances in parallel add as reciprocals. Both statements are exact and both are worth checking numerically, because a network assembled by hand often has one of them backwards.

The useful diagnostic is the fraction of the total each element carries.

In the worked example the chain from the TPS backface to the sink comes out as:

| Element | Share of series resistance |
|---|---|
| Bulkhead to sink, radiation | 80.4 % |
| Bulkhead to TPS backface, bolted bare vacuum | 16.2 % |
| Avionics to bulkhead, bolted with grease | 3.4 % |

**Eighty per cent of the answer sits in one radiative link.** Refining the greased interface cannot move the result, no matter how carefully it is characterised. This is the entire content of `resistanceSensitivity()`, and it is worth running before spending effort rather than after.

---

## Transient conduction

Two groups decide the modelling approach before any equations are written.

**Biot number** compares internal to surface resistance:

```
Bi = h L / k
```

Below 0.1 the body is nearly isothermal and a lumped node is defensible. The limit is a convention rather than a physical boundary, but it corresponds to roughly 5 % internal gradient, which is usually smaller than the uncertainty in `h`.

**Fourier number** is dimensionless time:

```
Fo = alpha t / L^2,       alpha = k / (rho c)
```

The practical form is the penetration depth, `sqrt(alpha t)`, which answers how far into a part the heat has got.

**Penetration depth is why short pulses do not care about part thickness and long soaks do.** A 1 second pulse into aluminium reaches 8.3 mm. The same pulse into 316L reaches 2.0 mm. Over 100 seconds those become 83 mm and 20 mm.

---

## Design rules of thumb

- **Compute the resistance chain before building a model.** The dominant term is usually obvious and usually not the one being refined.
- **Assume vacuum for any joint that flies.** Bench data taken in air overstates the conductance by a factor of four on a bare bolted interface.
- **A deliberate isolator is a design element.** At 50 W/m^2 K it is ten times worse than a bare joint, which is the point when the objective is to keep something warm.
- **Check Biot before lumping**, and record the check rather than assuming it.
- **Use penetration depth to choose the time step.** A step that lets heat penetrate further than the node spacing is not resolving anything.

---

## Failure modes

**The interface omitted.** Parts drawn touching in CAD are not thermally connected. This is the most common single error in a hand built network.

**Bench conductance used for flight.** Air in the gap is a real conduction path and it is not there in orbit.

**Lumping something with a high Biot number.** The reported temperature is an average. The failure is at the surface.

**A frozen radiation linearisation.** Acceptable for assembling a network, wrong for a transient that moves 300 K.

**Refining the wrong resistance.** Characterising a joint that carries 3 % of the total is effort that cannot change the answer.

---

## Worked numbers

All produced by running the code.

| Case | Value |
|---|---|
| 10 mm of 6061 aluminium, 0.01 m^2 | 0.0060 K/W |
| Bolted bare vacuum joint, 0.01 m^2 | 0.200 K/W |
| Bolted greased joint, 0.01 m^2 | 0.0125 K/W |
| Convection at 500 W/m^2 K, 0.01 m^2 | 0.200 K/W |
| Radiation, eps 0.85, 1 m^2, 300 K to 250 K | 0.247 K/W |
| Radiation, eps 0.85, 1 m^2, 300 K to 4 K | 0.758 K/W |

**The bare vacuum joint over 0.01 square metres is thirty three times the resistance of the 10 mm of aluminium it joins**, and it is numerically identical to a 500 W/m^2 K convective film over the same area.

| Property | 6061 aluminium | 316L stainless |
|---|---|---|
| Diffusivity `alpha` | 6.90e-05 m^2/s | 4.05e-06 m^2/s |
| Penetration, 1 s | 8.31 mm | 2.01 mm |
| Penetration, 100 s | 83.1 mm | 20.1 mm |
| Biot at `h` = 500, `L` = 5 mm | 0.015 | 0.154 |

**Aluminium at these conditions is a lump and stainless is not**, on identical geometry in an identical environment. The difference is a factor of seventeen in diffusivity.

---

## Standards

| Standard | What it gives you |
|---|---|
| ECSS-E-ST-31C | Thermal control general requirements, including model fidelity expectations |
| NASA-HDBK-2001 | The spacecraft thermal control handbook, contact conductance data |
| ASTM E1225 | Steady state thermal conductivity measurement, guarded comparative method |
| ASTM D5470 | Thermal interface material characterisation |

---

## Tool interface

```python
from thermalUtils import (conductionResistance, contactResistance, radiationResistance,
                          biotNumber, thermalDiffusivity, thermalPenetrationDepth)

metal = conductionResistance(0.010, 167.0, 0.01)
joint = contactResistance(0.01, 'bolted, bare, vacuum')

print(f'{joint / metal:.0f}x')

alpha = thermalDiffusivity(167.0, 2700.0, 896.0)
print(thermalPenetrationDepth(alpha, 100.0))
print(biotNumber(500.0, 0.005, 167.0))
```

Resistances are assembled into a network through [ThermalNetwork](ThermalModelling.md), which takes the same joint type strings.

---

## References

- Incropera and DeWitt, *Fundamentals of Heat and Mass Transfer*, chapters 2 to 5
- Madhusudana, *Thermal Contact Conductance*
- Gilmore, *Spacecraft Thermal Control Handbook*, volume I
- Carslaw and Jaeger, *Conduction of Heat in Solids*
