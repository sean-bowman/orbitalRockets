[Home](../README.md) > Radiators and Rejection

# Radiators and Rejection

## Contents

- [Overview](#overview)
- [The sizing equation and what dominates it](#the-sizing-equation-and-what-dominates-it)
- [The fourth power penalty](#the-fourth-power-penalty)
- [Sinks](#sinks)
- [Fin efficiency](#fin-efficiency)
- [The radiator and the heater are the same decision](#the-radiator-and-the-heater-are-the-same-decision)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

In vacuum there is nowhere for heat to go except out by radiation. Every watt a spacecraft generates has to leave through a surface, and the surface is sized by a fourth power law, which makes it behave unlike any other sizing problem on the vehicle.

```
A = Q / (eps sigma (T_rad^4 - T_sink^4))
```

Everything interesting follows from the exponent.

---

## The sizing equation and what dominates it

Two temperatures appear and they do not contribute equally.

At 305 K radiating to a 250 K low Earth orbit sink, the surface term `T_rad^4` is 8.65e+09 and the sink term `T_sink^4` is 3.91e+09. **The sink is 45 per cent of the surface term**, which is enough to matter and not enough to dominate.

At higher radiating temperatures it fades. At 350 K the sink is 26 per cent of the surface term; at 400 K it is 15 per cent. **A hot radiator barely cares where it is pointed. A cold one cares a great deal.**

This is the practical reason to run radiators hot beyond the area saving: it also makes the design insensitive to the environment, which is the part of the analysis with the largest uncertainty.

---

## The fourth power penalty

The single most useful number in radiator design is how fast area grows as the radiating temperature falls.

Rejecting 35 W to a 250 K sink:

| Radiating temperature [K] | Net flux [W/m^2] | Area [m^2] |
|---|---|---|
| 350 | 553.9 | 0.063 |
| 305 | 236.9 | 0.148 |
| 275 | 90.5 | 0.387 |
| 260 | 33.1 | 1.057 |

**From 305 K to 275 K, thirty kelvin, the area increases by a factor of 2.6. From 305 K to 260 K it increases by a factor of 7.2.**

The last row is the important one. At 260 K the radiator is only 10 K above its sink, the net flux has collapsed to 33 W/m^2, and the area has become absurd. **As the radiating temperature approaches the sink temperature the required area goes to infinity**, and the approach is steep rather than gradual.

This is why every degree of temperature drop between the heat source and the radiating surface is expensive. A 10 K drop across a bolted interface, a 5 K drop along a conduction path and a 5 K drop across a heat pipe are individually reasonable and collectively cost a factor of two in radiator area.

**Put the radiator as close to the source, thermally, as the design allows**, and spend mass on the conduction path rather than on the radiator.

---

## Sinks

The effective sink temperature is what the radiator sees, and it depends entirely on where it is pointed.

| Sink | Temperature [K] | Area for 35 W at 305 K [m^2] | Note |
|---|---|---|---|
| Deep space | 4 | 0.081 | Anti-sun, no planet in view. The best case |
| Geostationary | 100 | 0.082 | Earth is small in the field of view |
| Low Earth orbit | 250 | 0.148 | Earth fills much of the hemisphere |
| Sun facing | 390 | unusable | Effectively a heat source |

**Deep space and geostationary are within 2 per cent of each other**, because at 305 K radiating temperature, a 4 K sink and a 100 K sink are both negligible. The distinction only appears for cryogenic radiators, where it becomes the whole design.

**Low Earth orbit costs a factor of 1.8 over deep space**, because the Earth fills a large part of the sky and is at roughly 250 K. That is the number that matters for most missions, and it is not a small penalty.

**The sun facing case is not a poor radiator, it is not a radiator.** At 390 K the environment is above the radiating temperature and the surface absorbs. The [Radiator](#tool-interface) class reports that case as unusable rather than returning a negative area, because a negative area propagating into a mass budget is worse than an error.

Radiator placement is therefore a configuration decision made early, and it competes directly with solar array placement, antenna fields of view and instrument boresights. **A radiator that ends up pointing at the sun for part of the orbit has to be sized for that part.**

---

## Fin efficiency

A radiator larger than a compact plate needs the heat spread across it, and the spreading is not free. A fin at distance from the root runs cooler than the root, and cooler means less rejection per unit area.

```
h_r = 4 eps sigma T^3            the linearised radiation coefficient
m   = sqrt(2 h_r / (k t))        the fin parameter
eta = tanh(mL) / (mL)            efficiency
```

| Fin | `mL` | Efficiency |
|---|---|---|
| Aluminium, 1.5 mm, 150 mm | 0.528 | 0.916 |
| Aluminium, 0.5 mm, 150 mm | 0.914 | 0.791 |
| Aluminium, 1.5 mm, 300 mm | 1.055 | 0.743 |
| 316L, 1.5 mm, 150 mm | 1.694 | 0.552 |

**Doubling the fin length costs 17 points of efficiency**, so the effective area gain from doubling the length is not double. **Using stainless instead of aluminium costs 36 points**, which is why radiator fins are aluminium, and why the ones that are not are heat pipe embedded.

The efficiency also falls with temperature, because `h_r` goes as `T^3`. A hot radiator spreads heat less well than a cold one, which partly offsets the fourth power advantage. It does not offset it much: the area saving goes as `T^4` and the efficiency loss as `T^3`.

---

## The radiator and the heater are the same decision

A radiator sized for the hot case is, in the cold case, an unwanted heat leak that has to be made up by a heater.

**The radiator and the heater are one design variable with two costs**, and they are usually in two different budgets owned by two different people. The radiator costs mass and area. The heater costs power, continuously, for the mission.

For the worked example avionics: 0.148 m^2 of radiator, and 78.8 kWh of heater energy over a one year mission. Neither number is unreasonable. What is unreasonable is trading them separately, because reducing the radiator by 20 per cent to save mass would reduce the heater load by roughly the same fraction and nobody in the mass conversation would notice.

Variable conductance heat pipes, louvres and deployable radiators all exist to break this coupling, and all of them cost a mechanism. See [ThermalControlSystems](ThermalControlSystems.md).

---

## Design rules of thumb

- **Radiate as hot as the hardware allows.** Nothing else in the design has a fourth power lever.
- **Spend mass on the conduction path to the radiator rather than on the radiator.** Every kelvin lost on the way is paid for in area.
- **Point away from the sun and away from the planet, in that order.**
- **Use aluminium fins.** The efficiency penalty for stainless is 36 points on a typical geometry.
- **Keep `mL` below about 1.** Beyond that the fin is mostly cold.
- **Size the hot case at end of life optical properties.** Degradation only goes one way.
- **Trade the radiator and the heater together.** They are one variable.

---

## Failure modes

**Radiating temperature given away to interfaces.** A 20 K total drop from source to surface can double the area required.

**A sink temperature assumed rather than derived from the pointing.** A radiator that sees the Earth for part of the orbit has a different sink for that part.

**A sun facing surface treated as a radiator.** It is a heat source, and a negative area in a spreadsheet is a real failure mode.

**Fin efficiency ignored.** A long thin fin has substantially less effective area than its geometric area.

**Beginning of life properties used for sizing.** The hot case is an end of life case.

**Radiator and heater traded separately.** Produces a design that is mass optimal and power hostile.

---

## Worked numbers

Rejecting 35 W to a 250 K sink, white paint at emissivity 0.88.

| Radiating temperature [K] | Net flux [W/m^2] | Area [m^2] |
|---|---|---|
| 350 | 553.9 | 0.063 |
| 305 | 236.9 | 0.148 |
| 275 | 90.5 | 0.387 |
| 260 | 33.1 | 1.057 |

Sink comparison at 305 K:

| Sink | Area [m^2] |
|---|---|
| Deep space, 4 K | 0.081 |
| Geostationary, 100 K | 0.082 |
| Low Earth orbit, 250 K | 0.148 |
| Sun facing, 390 K | Unusable |

A larger case, 500 W at 313 K to deep space:

| Quantity | Value |
|---|---|
| Net flux | 478.9 W/m^2 |
| Area | 1.044 m^2 |
| Radiation coefficient `h_r` | 1.550 W/m^2 K |
| Fin efficiency, aluminium 1.5 mm x 150 mm | 0.916 |

---

## Standards

| Standard | What it gives you |
|---|---|
| ECSS-E-ST-31C | Thermal control general requirements |
| NASA-HDBK-2001 | Spacecraft thermal control handbook, radiator chapter |
| ASTM E903 | Solar absorptance |
| ASTM E408 | Total normal emittance |
| ECSS-Q-ST-70-06 | Contamination control, which drives optical degradation |

---

## Tool interface

```python
from Radiator import Radiator

radiator = Radiator()
radiator.setInputs({'heatLoad':             35.0,
                    'radiatingTemperature': 305.0,
                    'sinkTemperature':      250.0,
                    'surfaceFinish':        'white paint'})

sizing = radiator.sizeArea()
print(sizing['area'], sizing['netFlux'])

for name, entry in radiator.compareSinks()['sinks'].items():
    print(name, entry['area'] if entry['usable'] else 'unusable')
```

Fin efficiency needs the fin geometry as well:

```python
from Radiator import Radiator

radiator = Radiator()
radiator.setInputs({'heatLoad':             500.0,
                    'radiatingTemperature': 313.0,
                    'sinkTemperature':      4.0,
                    'surfaceFinish':        'white paint',
                    'finLength':            0.15,
                    'finThickness':         0.0015,
                    'finConductivity':      167.0})

print(radiator.calculateFinEfficiency()['efficiency'])
```

---

## References

- Gilmore, *Spacecraft Thermal Control Handbook*, volume I, chapter 6
- NASA-HDBK-2001, radiators and coatings
- Karam, *Satellite Thermal Control for Systems Engineers*
- Incropera and DeWitt, *Fundamentals of Heat and Mass Transfer*, fin analysis
