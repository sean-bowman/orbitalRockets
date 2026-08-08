[Home](../README.md) > Thermal Environments

# Thermal Environments

## Contents

- [Overview](#overview)
- [Ascent aeroheating](#ascent-aeroheating)
- [On-orbit radiation balance](#on-orbit-radiation-balance)
- [Alpha over epsilon](#alpha-over-epsilon)
- [Hot and cold cases](#hot-and-cold-cases)
- [Thermal cycling](#thermal-cycling)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Thermal is unlike the other environments in this domain. Vibration, shock and acoustics are transient and statistical; thermal is slow, deterministic and driven by geometry. It is also the environment most likely to be the design driver for something that looked benign.

---

## Ascent aeroheating

**The Sutton-Graves stagnation point correlation:**

```
q = k sqrt(rho / R_nose) V^3
```

**Velocity cubed is the whole story.** A 20 percent velocity increase is a 73 percent heat flux increase, and density enters only as a square root.

**That is why peak heating is not at peak dynamic pressure.** Dynamic pressure goes as `rho V^2` and heating as `sqrt(rho) V^3`, so heating peaks substantially higher and later in the trajectory, where the vehicle is faster and the air thinner.

**Nose radius matters inversely as a square root.** A blunt nose has a lower stagnation heat flux than a sharp one, which is the counterintuitive result behind every blunt reentry body: bluntness pushes the shock away from the surface and spreads the heating.

**This correlation sizes nothing.** It decides whether a surface needs protection. Anything past that decision needs a real aerothermal analysis.

---

## On-orbit radiation balance

**In vacuum, the only heat transfer is radiation, so the equilibrium temperature comes from a balance:**

```
absorbed = emitted
alpha S A_sun + alpha S a F A + eps E_ir F A + Q_internal = eps sigma A T^4
```

| Source | Magnitude |
|---|---|
| **Direct solar** | 1361 W/m^2 mean, 1412 at perihelion, 1322 at aphelion |
| **Albedo** | 0.25 to 0.35 of solar, reflected from Earth |
| **Earth infrared** | 220 to 260 W/m^2 |
| Internal dissipation | Whatever the hardware makes |

**The 6.9 percent annual solar variation from orbital eccentricity is not negligible.** The hot case uses perihelion and the cold case aphelion, which is nearly 90 W/m^2 of difference before anything else is considered.

**View factor to Earth falls with altitude**, so albedo and Earth infrared matter enormously in low orbit and very little in geostationary.

---

## Alpha over epsilon

**The ratio of solar absorptivity to infrared emissivity sets a sunlit equilibrium temperature almost by itself.**

| Finish | alpha | eps | alpha/eps (EOL) | Hot case |
|---|---|---|---|---|
| **Optical solar reflector** | 0.08 | 0.80 | **0.25** | **335 K** |
| White paint | 0.20 | 0.88 | 0.45 | 372 K |
| Aluminised kapton | 0.40 | 0.80 | 0.69 | 405 K |
| Black paint | 0.95 | 0.88 | 1.09 | 447 K |
| **Bare aluminium** | 0.15 | **0.05** | **5.00** | **647 K** |

**312 K between the hottest and coolest finish, on the same hardware.** That is a larger swing than most active thermal control can achieve, and it is bought with a coating.

**Bare aluminium is the trap.** Its absorptivity is low, which looks good, and its emissivity is very low, which is what dominates: it absorbs modestly and cannot radiate at all, so it runs extremely hot.

**Properties degrade in orbit.** Ultraviolet exposure and atomic oxygen raise absorptivity while emissivity stays roughly constant, so `alpha/eps` grows. White paint roughly doubles over a mission.

**Beginning-of-life and end-of-life are different thermal designs**, and a design closed at beginning-of-life properties will not close at end of life.

---

## Hot and cold cases

**They are constructed from different assumptions rather than being one calculation with different numbers.**

| Assumption | Hot case | Cold case |
|---|---|---|
| Solar constant | **Perihelion**, 1412 | **Aphelion**, 1322 |
| Albedo | Maximum, 0.35 | Minimum, 0.25 |
| Earth infrared | Maximum, 260 | Minimum, 220 |
| Internal dissipation | **Maximum** | **Zero** |
| Surface properties | **End of life** | **Beginning of life** |
| Attitude | Worst sun angle | Eclipse |

**Building each case from its own worst combination is the point.** A hot case that uses beginning-of-life absorptivity is not a hot case, and a cold case that includes internal dissipation is not a cold case.

---

## Thermal cycling

**A low Earth orbit is about 90 minutes, so cycles accumulate fast.**

| Mission | Cycles |
|---|---|
| 1 year | 5844 |
| 5 years | 29220 |
| 15 years | 87660 |

**That is a fatigue problem for anything with a coefficient of thermal expansion mismatch**, and solder joints are the classic casualty: a large ceramic component on a glass-epoxy board shears its joints over thousands of cycles.

**Above ten thousand cycles thermal fatigue is a primary design consideration** rather than a check, and qualification has to demonstrate it rather than argue it.

**Geostationary is gentler in cycle count and harsher in duration.** A GEO satellite sees two eclipse seasons a year, so roughly 90 cycles a year rather than 5800, but each eclipse is longer and the cold soak is deeper.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| `q = k sqrt(rho/R) V^3` | Velocity cubed dominates |
| Peak heating is above peak dynamic pressure | Different exponents |
| A blunt nose heats less | Not more |
| `alpha/eps` sets sunlit equilibrium | 312 K across the finish range |
| Bare aluminium runs very hot | Emissivity 0.05 |
| Properties degrade, `alpha/eps` grows | Design to end of life |
| Build hot and cold from different assumptions | Not one calculation |
| LEO gives ~5800 cycles per year | Thermal fatigue is a driver |

---

## Failure modes

**Thermal protection sized at max-Q.** Heating peaks higher and later.

**A sharp nose chosen for drag.** It heats far more.

**Beginning-of-life properties used for the hot case.** It is not a hot case.

**Internal dissipation included in the cold case.** It is not a cold case.

**Bare aluminium used as a radiating surface.** Emissivity 0.05.

**Thermal cycling ignored below ten thousand cycles.** It accumulates faster than expected.

**GEO and LEO cycling treated the same.** 90 cycles a year against 5800.

---

## Worked numbers

From [`ThermalEnvironment`](../environmentsAndLoadsLibrary/ThermalEnvironment.py), white paint at 500 km, 2 m^2 radiating, 50 W dissipation:

| Quantity | Value |
|---|---|
| Hot case | 372.1 K (+98.9 degC) |
| Cold case | 240.3 K (-32.8 degC) |
| **Swing** | **131.8 K per orbit** |
| alpha/eps beginning of life | 0.23 |
| alpha/eps end of life | 0.45 |
| Cycles in 5 years | 29220 |

**White paint degrades by 2.0x in alpha over epsilon**, so a design closed at beginning-of-life properties will not close at end of life.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-HDBK-1001** | Terrestrial environment criteria |
| ECSS-E-ST-31 | Thermal control general requirements |
| ECSS-E-ST-10-04 | Space environment |
| **ASTM E490** | Solar constant and air mass zero solar spectral irradiance |
| ASTM E903 | Solar absorptance by spectrophotometry |
| ASTM E408 | Total normal emittance |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'environmentsAndLoadsLibrary')

from ThermalEnvironment import ThermalEnvironment

thermal = ThermalEnvironment()
thermal.setInputs({'surfaceFinish': 'white paint', 'altitude': 500.0e3,
                   'radiatingArea': 2.0, 'internalDissipation': 50.0,
                   'missionYears': 5.0})

cases = thermal.calculateOnOrbitCases()
print(f'hot {cases["hotTemperature"] - 273.15:+.1f} degC, '
      f'cold {cases["coldTemperature"] - 273.15:+.1f} degC')

comparison = thermal.compareFinishes()
for name, entry in comparison['finishes'].items():
    print(f'{name:26s} a/e {entry["ratio"]:.2f}  hot {entry["hot"]:6.1f} K')
print(comparison['note'])
```

---

## References

1. Gilmore, D. G. (ed.), *Spacecraft Thermal Control Handbook*, 2nd ed., Aerospace Press, 2002.
2. Sutton, K. and Graves, R. A., *A General Stagnation-Point Convective Heating Equation*, NASA TR R-376, 1971.
3. ECSS-E-ST-31C, *Thermal Control General Requirements*.
