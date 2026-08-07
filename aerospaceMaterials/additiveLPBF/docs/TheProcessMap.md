[Home](../README.md) > The Process Map

# The Process Map

## Contents

- [Overview](#overview)
- [Volumetric energy density, and why it is not enough](#volumetric-energy-density-and-why-it-is-not-enough)
- [Normalised enthalpy](#normalised-enthalpy)
- [The window](#the-window)
- [Which side to err towards](#which-side-to-err-towards)
- [Developing a parameter set](#developing-a-parameter-set)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The process map is the region of parameter space where a part comes out dense. It is bounded below by lack of fusion and above by keyholing, and it is narrower than most published parameter sets admit.

Finding it is the first thing done with a new alloy and the thing most programmes underestimate.

---

## Volumetric energy density, and why it is not enough

```
E_v = P / (v * h * t)          [J/m^3]
```

Power divided by the product of scan speed, hatch spacing and layer thickness. It has units of energy per unit volume and it is the number everybody quotes.

**It is a poor discriminator and the reason is straightforward: the same E_v is reached by very different processes.**

| Set | Power | Speed | E_v | Melt pool |
|---|---|---|---|---|
| A | 200 W | 0.67 m/s | 67.5 J/mm^3 | Wide, shallow, slow |
| B | 400 W | 1.35 m/s | 67.5 J/mm^3 | Narrow, deep, fast |

Identical energy density, and B is far closer to keyholing than A because the intensity is doubled. Two parameter sets with the same E_v can sit on opposite sides of the window.

**Energy density is useful for talking about a process and useless for predicting one.** It is a bookkeeping quantity, not a physical one.

---

## Normalised enthalpy

The better discriminator compares the absorbed energy against the enthalpy needed to melt the material, scaled by how far heat diffuses in the interaction time:

```
dH / h_s = A P / ( rho h_s sqrt( pi alpha v sigma^3 ) )
```

| Symbol | Meaning |
|---|---|
| `A` | Absorptivity at the laser wavelength |
| `P` | Laser power |
| `rho h_s` | Enthalpy per unit volume at melting, including latent heat |
| `alpha` | Thermal diffusivity |
| `v` | Scan speed |
| `sigma` | Beam radius |

**Everything in it is physical.** The absorptivity is why copper is hard; the diffusivity is why aluminium needs high power and fast scanning; the beam radius enters to the three-halves power, which is why spot size is not a free parameter.

**It separates the two cases E_v cannot.** Set B above has twice the power at twice the speed, so its normalised enthalpy is higher by a factor of the square root of two, and the model puts it correctly closer to keyholing.

---

## The window

| Normalised enthalpy | Regime | Defect |
|---|---|---|
| **Below 6** | Lack of fusion | Flat, layer-aligned pores that behave like cracks |
| **6 to 30** | Stable | Porosity below 0.1 percent |
| **Above 30** | Keyhole | Round gas pores from vapour cavity collapse |

**The keyhole threshold near 30 is a guide, not a constant.** It shifts with material, layer thickness and beam diameter, and every alloy needs its own map established rather than assumed.

**A margin matters as much as being inside.** A process point four units from a boundary will cross it when the powder lot changes, the machine drifts, or a laser loses a few percent of its output. A parameter set that works on the development build and not on the fifth one is usually a parameter set with no margin.

---

## Which side to err towards

**The two defects are not equally bad, and given the choice, err towards keyhole.**

| | Lack of fusion | Keyhole |
|---|---|---|
| Shape | Flat, irregular | Round |
| Orientation | Aligned with the layers | Random |
| Stress concentration | Crack-like, effectively infinite | About 3 |
| **Fatigue impact** | **Severe** | Moderate |
| **Recoverable by HIP** | **Not fully** | Largely yes |

HIP closes porosity by creep. A round pore closes and the surfaces bond. A flat lack-of-fusion defect closes geometrically and the surfaces frequently do not bond, because they are oxidised, so the crack-like flaw remains even though the density measurement now reads 100 percent.

**A density measurement does not distinguish them.** Two parts at 99.8 percent density can have completely different fatigue lives depending on whether the missing 0.2 percent is round or flat. Metallography or CT is required to tell.

---

## Developing a parameter set

The sequence a programme actually follows.

**1. Single tracks.** Laser on a bare plate or a single powder layer, at a grid of power and speed. Section and measure the melt pool. This establishes the geometry without the complication of layer-to-layer interaction, and it is where the conduction and keyhole boundaries are first located.

**2. Single layers.** Hatched areas at a grid of hatch spacings. Confirms the track overlap.

**3. Bulk cubes.** 10 mm cubes across the surviving parameter grid, measured for density by Archimedes and by metallography. This is the map.

**4. Contour and skin parameters.** Separate development, because the surface needs different energy from the bulk.

**5. Properties.** Tensile, fatigue and metallography at the chosen point, in both orientations.

**6. Freeze.** The parameter set becomes a controlled document and any change to it is a change.

**Steps 1 to 3 are perhaps 60 builds** and they are the cost of a new alloy. This is why programmes stay on the alloys their machine vendor supports.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Volumetric energy density | 40 to 90 J/mm^3 for common alloys |
| Normalised enthalpy window | 6 to 30 |
| Margin to a boundary | 4 units minimum |
| Err towards | Keyhole, not lack of fusion |
| Density target | 99.9 % |
| A density number alone | Does not identify the defect type |
| Parameter development | ~60 builds for a new alloy |

---

## Failure modes

**Parameter set chosen on energy density alone.** Two sets with the same E_v on opposite sides of the window.

**No margin to the boundary.** Works on build one, fails on build five.

**Density measured, defect type not identified.** A crack-like flaw at 99.8 percent reads the same as a spherical one.

**HIP assumed to fix everything.** It does not close lack of fusion reliably.

**A vendor parameter set used on a different machine.** Beam profile, gas flow and calibration all differ.

**Contour parameters not developed.** The surface is the fatigue-critical region and it gets the bulk parameters.

---

## Worked numbers

From [`LpbfProcess`](../additiveLpbfLibrary/LpbfProcess.py):

| Alloy | Power | Speed | E_v [J/mm^3] | dH/h_s | Regime |
|---|---|---|---|---|---|
| Inconel 718 | 285 W | 0.96 m/s | 67.5 | 13.5 | stable |
| Ti-6Al-4V | 280 W | 1.20 m/s | 41.7 | 13.1 | stable |
| 316L | 195 W | 1.00 m/s | 54.2 | 8.3 | stable |
| AlSi10Mg | 370 W | 1.30 m/s | 37.4 | 10.7 | stable |
| **GRCop-42** | 300 W | 0.80 m/s | **85.2** | **2.2** | **lack of fusion** |
| **GRCop-42** | 500 W | 0.70 m/s | **162.3** | **4.0** | **lack of fusion** |

**GRCop-42 has the highest energy density in the table and it is deeply lack-of-fusion.** Its absorptivity is 0.15 against 0.42 for nickel, so most of the energy density is reflected rather than absorbed. That contradiction is the clearest demonstration available that energy density is not the discriminator.

---

## Standards

| Standard | Scope |
|---|---|
| **MSFC-SPEC-3717** | Control and qualification of LPBF processes |
| ISO/ASTM 52904 | Process characteristics and performance for metal PBF |
| ASTM F3303 | Process characteristics for metal PBF for critical applications |
| NASA-STD-6030 | Additive manufacturing requirements |
| ASTM B962 | Density by the Archimedes method |

---

## Tool interface

```python
from LpbfProcess import (LpbfProcess, NORMALISED_ENTHALPY_LOWER, NORMALISED_ENTHALPY_UPPER)

for power in (150.0, 285.0, 800.0):
    process = LpbfProcess()
    process.setInputs({'material': 'Inconel 718', 'laserPower': power, 'scanSpeed': 0.96})
    process.calculateEnergyDensity()
    result = process.classifyRegime()
    print(power, result['processRegime'], result['marginToNearestBound'])
```

---

## References

1. King, W. E. et al., "Observation of Keyhole-Mode Laser Melting in Laser Powder-Bed Fusion", *Journal of Materials Processing Technology*, Vol. 214, 2014.
2. Hann, D. B., Iammi, J. and Folkes, J., "A Simple Methodology for Predicting Laser-Weld Properties from Material and Laser Parameters", *Journal of Physics D*, Vol. 44, 2011.
3. Gordon, J. V. et al., "Defect Structure Process Maps for Laser Powder Bed Fusion", *Additive Manufacturing*, Vol. 36, 2020.
4. Tang, M., Pistorius, P. C. and Beuth, J. L., "Prediction of Lack-of-Fusion Porosity for Powder Bed Fusion", *Additive Manufacturing*, Vol. 14, 2017.
