[Home](../README.md) > Thermal Overview

# Thermal Overview

## Contents

- [Overview](#overview)
- [What this domain is for](#what-this-domain-is-for)
- [The three transport mechanisms, and which one governs](#the-three-transport-mechanisms-and-which-one-governs)
- [Steady state is the easy half](#steady-state-is-the-easy-half)
- [The design rules of thumb](#the-design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Where the domain sits](#where-the-domain-sits)
- [Tool interface](#tool-interface)
- [Documents in this domain](#documents-in-this-domain)
- [References](#references)

---

## Overview

Thermal management on a launch vehicle is not one problem. It is at least four, and they are governed by different physics, sized against different requirements, and usually owned by different people.

There is the ascent problem, where aerodynamic heating deposits a large flux for a short time and something has to stop it reaching the structure. There is the cryogenic problem, where the vehicle is trying to keep propellant cold on the pad against an environment 200 K warmer. There is the on orbit problem, where a spacecraft has to reject its own dissipation to a sink whose temperature depends on where it is looking. And there is the soakback problem, which is the one that catches people, because it is not a problem at all until the event that caused it is over.

This domain covers all four, but it is organised around the last one. The rest of the material is here because you cannot analyse soakback without it.

---

## What this domain is for

The pattern this domain exists to catch is simple to state and hard to notice.

A heat pulse arrives, is stopped by protection that is correctly sized, and the analysis closes with margin. Then the heat that was absorbed rather than rejected spreads inward, and something behind the protection reaches its peak temperature long after the vehicle has left the atmosphere. The protection did its job. The analysis was run correctly. The answer was still wrong, because the model stopped integrating when the heating stopped.

[the worked example](../codeInterface.py) runs exactly this case. A 140 second ascent heat pulse is stopped by 11.48 mm of cork. The avionics behind it reach 307.4 K when the heating ends, comfortably inside a 323.15 K limit, and 374.8 K at 950 seconds, which is not. Same model, same hardware, same heat pulse. The only difference is when the analyst stopped.

The number that decides pass or fail is a modelling choice, not a physical one. That is what makes it dangerous.

---

## The three transport mechanisms, and which one governs

Everything in this domain is conduction, convection or radiation, and the useful skill is knowing which one is carrying the heat before writing any equations.

| Mechanism | Scales as | Governs when |
|---|---|---|
| Conduction | `dT` linearly | Solids, and any joint between them |
| Convection | `dT` linearly, but `h` varies by four orders | There is a fluid moving, including boiling |
| Radiation | `T^4` difference | Vacuum, or anything above roughly 600 K |

**The fourth power is the single most important fact in the domain.** It means radiation is negligible at room temperature and dominant at combustion temperatures, it means a radiator that runs 30 K colder is enormously larger, and it means an ablative surface finds its own temperature rather than being told one.

The [Radiator](RadiatorsAndRejection.md) numbers make the scaling concrete. Rejecting 35 W to a 250 K sink takes 0.148 square metres at 305 K and 0.387 square metres at 275 K. Thirty kelvin of radiating temperature costs a factor of 2.6 in area.

**Contact resistance is the mechanism people forget.** It is conduction, but it does not behave like conduction, because the conductance across a bolted joint spans a factor of forty depending on what is in the gap.

| Joint | Conductance [W/m^2 K] |
|---|---|
| Deliberate isolator | 50 |
| Bolted, bare, in vacuum | 500 |
| Bolted, bare, in air | 2000 |
| Bonded, thermally filled | 5000 |
| Bolted, with grease | 8000 |
| Bolted, with indium foil | 20 000 |
| Welded or integral | effectively infinite |

A bolted aluminium joint in vacuum, 0.01 square metres, is 0.2 K/W. Ten millimetres of 6061 over the same area is 0.006 K/W. **The interface is thirty times the resistance of the metal it joins.** Modelling the metal carefully and the joint carelessly gets the answer wrong in the direction that matters.

---

## Steady state is the easy half

Steady state answers whether a design can work. Transient answers whether it survives getting there, and it is usually the harder question.

Two dimensionless groups decide how much modelling detail a transient needs.

**Biot number**, `Bi = h L / k`, compares the resistance inside a body to the resistance at its surface. Below 0.1 the body is nearly isothermal and a single lumped node is honest. Above it, internal gradients matter and one node is a fiction.

The limit is not academic. At `h = 500 W/m^2 K` on a 5 mm characteristic length, aluminium gives `Bi = 0.015` and stainless gives `Bi = 0.154`. The aluminium part is a lump. The stainless part, same geometry, same environment, is not.

**Fourier number**, `Fo = alpha t / L^2`, is dimensionless time. It says how far heat has got. The companion is the thermal penetration depth, `sqrt(alpha t)`, which is the practical version of the same statement.

In one second heat penetrates 8.3 mm into 6061 aluminium and 2.0 mm into 316L. In one hundred seconds, 83 mm and 20 mm. **A short pulse into a thick part never sees the far side**, which is exactly why ablative protection works and exactly why the transient has to keep running after the pulse ends.

---

## The design rules of thumb

- **Size ascent protection at peak heating, not peak dynamic pressure.** Heating goes as `V^3 sqrt(rho)`, so the two conditions are not the same and peak heating is later.
- **Run the transient until every node has turned over.** If a node's maximum falls at the last time step, that is a truncation artefact and not a peak.
- **Model the joints before refining the metal.** Contact conductance spans a factor of forty and conductivity within a material class does not.
- **Check the Biot number before lumping.** Below 0.1 a single node is defensible; above it, say so rather than hoping.
- **Radiate hot.** Area goes as the inverse fourth power of temperature, so raising the radiating temperature is the cheapest lever available.
- **A heat pipe is a cliff, not a curve.** Past its capillary limit it stops working rather than degrading. Design margin, not proximity.
- **Cost the heater power against the radiator that caused it.** A radiator sized for the hot case is paid for continuously in the cold case, and the two are usually budgeted separately.

---

## Failure modes

**The truncated transient.** The most common, and the reason this domain leads with soakback. A run that stops when the heating stops reports the temperature at that moment as though it were the maximum.

**The isothermal assumption applied to something that is not.** A lumped node on a part with `Bi > 0.1` reports an average and hides the surface, which is where the material actually fails.

**The joint that was not in the model.** Two parts drawn touching are not two parts thermally connected. In vacuum, with no grease, a bolted interface is a real resistance.

**The sink that is a source.** A radiator pointed at the sun sees a 390 K environment. It is not a poor radiator, it is not a radiator. The [Radiator](RadiatorsAndRejection.md) class reports that case as unusable rather than returning a negative area.

**The ablative surface temperature treated as an input.** The tabulated value is what the material holds while ablating hard. Below the flux that sustains it, the surface sits at radiative equilibrium and does not recede. Using the tabulated value regardless oversizes insulation against a surface hotter than the real one, and reports recession that does not happen.

**The heat pipe tested favourably.** A grooved pipe transports 115 W horizontal and nothing at all at 2 degrees adverse tilt in one gravity. A bench test that did not control tilt to better than that did not test the pipe.

---

## Where the domain sits

| Domain | What crosses the boundary |
|---|---|
| [environmentsAndLoads](../../environmentsAndLoads/README.md) | Aeroheating flux, on orbit hot and cold cases, thermal cycle counts |
| [aerospaceMaterials](../../aerospaceMaterials/README.md) | Conductivity, specific heat, temperature dependent allowables |
| [aerospaceStructures](../../aerospaceStructures/README.md) | Thermal stress, and the structure that is also the conduction path |
| [fluidSystems](../../fluidSystems/README.md) | Cryogenic boiloff, line chilldown, the avionics that end up hot |

**The surface optical properties in this domain are asserted by test to match the ones in environmentsAndLoads.** The check reads the other domain with `ast` rather than importing it, so neither domain depends on the other's internals and the values still cannot drift apart.

---

## Tool interface

```python
from ThermalNetwork import ThermalNetwork

network = ThermalNetwork()
network.setInputs({'timeStep': 2.0, 'endTime': 6000.0})

network.addNodeFromMass('bulkhead', mass = 22.0, specificHeat = 900.0, temperature = 293.15)
network.addNodeFromMass('avionics', mass = 6.5, specificHeat = 800.0, temperature = 293.15,
                        heatLoad = 35.0)
network.addNode('sink', temperature = 250.0, boundary = True)

network.addContact('bulkhead', 'avionics', area = 0.012, jointType = 'bolted, with grease')
network.addRadiation('bulkhead', 'sink', emissivity = 0.85, area = 0.9)

result = network.solveTransient()
print(result['truncated'])
```

The five classes and what each is for:

| Class | Answers |
|---|---|
| [ThermalNetwork](ThermalModelling.md) | What temperature does everything reach, and when |
| [AblativeTPS](AeroheatingAndTPS.md) | How thick does the protection have to be |
| [Radiator](RadiatorsAndRejection.md) | How large is the radiator, and against which sink |
| [HeatPipe](HeatPipesAndTwoPhase.md) | How much can this pipe carry, and does it survive the bench |
| [ThermalControl](ThermalControlSystems.md) | How much heater power, and what does it cost over the mission |

---

## Documents in this domain

| Document | Covers |
|---|---|
| [ConductionAndResistance.md](ConductionAndResistance.md) | Conduction, contact conductance, resistance networks |
| [ConvectionAndBoiling.md](ConvectionAndBoiling.md) | Correlations, their validity limits, boiling regimes |
| [RadiationHeatTransfer.md](RadiationHeatTransfer.md) | Stefan-Boltzmann, view factors, optical properties, degradation |
| [AeroheatingAndTPS.md](AeroheatingAndTPS.md) | Sutton-Graves, ablation, TPS sizing and material choice |
| [CryogenicInsulation.md](CryogenicInsulation.md) | MLI, foam, boiloff, the ground hold problem |
| [ThermalControlSystems.md](ThermalControlSystems.md) | Heaters, thermostats, coatings, the hot and cold case pair |
| [HeatPipesAndTwoPhase.md](HeatPipesAndTwoPhase.md) | The four limits, wick selection, ground testability |
| [RadiatorsAndRejection.md](RadiatorsAndRejection.md) | Sizing, sinks, fin efficiency, the fourth power penalty |
| [ThermalModelling.md](ThermalModelling.md) | Nodal networks, time stepping, lumping, model correlation |
| [ThermalTesting.md](ThermalTesting.md) | Thermal vacuum, balance, cycling, what each test proves |
| [StandardsIndex.md](StandardsIndex.md) | The standards, and what each is actually for |

---

## References

- Incropera and DeWitt, *Fundamentals of Heat and Mass Transfer*
- Gilmore, *Spacecraft Thermal Control Handbook*, volumes I and II
- NASA-HDBK-2001, *Spacecraft Thermal Control Handbook*
- ECSS-E-ST-31C, *Thermal control general requirements*
- NASA SP-8014, *Entry thermal protection*
