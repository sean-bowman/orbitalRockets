[Home](../README.md) > Aerodynamic Loads

# Aerodynamic Loads

## Contents

- [Overview](#overview)
- [Dynamic pressure and max-Q](#dynamic-pressure-and-max-q)
- [Why q alpha is the real parameter](#why-q-alpha-is-the-real-parameter)
- [Buffet](#buffet)
- [Wind and gust](#wind-and-gust)
- [Load relief](#load-relief)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Aerodynamic loads are the only environment a vehicle can actively steer around, which makes this the one place where the guidance system and the structure are designed against each other.

---

## Dynamic pressure and max-Q

```
q = 0.5 rho V^2
```

**Density falls exponentially and velocity rises, so their product peaks.** Max-Q typically occurs at 10 to 15 km altitude and Mach 1 to 1.5, and it is the moment of highest aerodynamic loading.

**It is not the moment of highest heating.** Stagnation heating goes as `sqrt(rho) V^3`, which peaks substantially higher and later. Sizing thermal protection at max-Q is the wrong condition. See [ThermalEnvironments.md](ThermalEnvironments.md).

**Max-Q is a trajectory design output**, and it can be reduced by throttling. Most vehicles throttle through the transonic region for exactly this reason, trading performance for structural load.

---

## Why q alpha is the real parameter

**Dynamic pressure alone produces axial drag, which structure handles easily. The bending moment comes from angle of attack.**

```
bending moment ~ q alpha
```

**`q alpha` is the parameter the guidance system is limited against**, not `q`. A vehicle at max-Q flying perfectly aligned has a modest structural load; the same vehicle at 3 degrees of angle of attack has a large one.

| Contribution | Effect |
|---|---|
| **q alone** | Axial drag. Small structural consequence |
| **q alpha** | **Bending moment. The design driver** |
| q beta | Yaw equivalent, same physics |

**Angle of attack comes from wind.** The vehicle flies a planned trajectory through an atmosphere that is moving, and the difference between the planned velocity vector and the relative wind is the angle of attack.

**That is why day-of-launch wind measurement matters.** A balloon sounding taken hours before launch feeds a trajectory update that reduces `q alpha` for the winds actually present, and it is the difference between launching and scrubbing on a windy day.

---

## Buffet

**Unsteady aerodynamic loading from separated or shock-oscillating flow, concentrated in the transonic region.**

| Source | Character |
|---|---|
| **Shock oscillation** | On a boattail or a payload fairing shoulder |
| **Separated flow** | Behind a step, a flare or a protuberance |
| **Base flow** | Unsteady recirculation at the base |

**It is a random pressure field, not a steady load**, so it produces both a structural vibration environment and a fluctuating bending moment.

**Geometry drives it.** A hammerhead fairing, one wider than the stage below it, produces strong shock oscillation at its shoulder and is a classic buffet generator. That geometry is chosen for payload volume and it costs a buffet environment.

**It is measured in a wind tunnel** with dynamic pressure transducers, and the transonic buffet test is one of the few environments that cannot be reasonably predicted analytically.

---

## Wind and gust

| Model | Use |
|---|---|
| **Steady wind profile** | Trajectory design, mean loads |
| **Wind shear** | Change of wind with altitude. Produces angle of attack rapidly |
| **Gust** | A discrete change superimposed on the profile |
| Turbulence | Continuous random component |

**Wind shear is the driver rather than wind speed.** A steady 50 m/s wind at altitude is trimmed out by the guidance; a 20 m/s change over a kilometre of altitude is not, because the vehicle passes through it faster than it can respond.

**Design wind profiles are statistical**, typically 95th or 99th percentile for the launch site and month, and they are one of the few environments with a strong seasonal dependence.

---

## Load relief

**The guidance system can deliberately fly at an angle of attack to reduce structural load, at a cost in trajectory performance.**

| Mode | Character |
|---|---|
| **No load relief** | Fly the planned attitude. Maximum `q alpha` in wind |
| **Load relief** | Steer into the relative wind, reducing `q alpha` |
| Adaptive | Use measured accelerations to reduce load in real time |

**Load relief trades performance for structure.** Flying into the wind reduces the bending moment and moves the trajectory off the optimum, costing payload.

**This is the one environment that is actively controlled**, and it means the structural design and the guidance design are coupled: a stronger structure permits a more aggressive trajectory, and a better load relief law permits a lighter structure.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| `q = 0.5 rho V^2` | Peaks at 10 to 15 km, Mach 1 to 1.5 |
| Max-Q is not max heating | Heating peaks higher and later |
| **`q alpha` is the design parameter** | Not `q` |
| Angle of attack comes from wind | Day-of-launch measurement matters |
| Wind shear drives it, not wind speed | The vehicle cannot respond fast enough |
| Hammerhead fairings generate buffet | Geometry chosen for volume |
| Buffet is measured, not predicted | Transonic wind tunnel |
| Load relief trades payload for structure | The one controllable environment |

---

## Failure modes

**Structure sized against `q` rather than `q alpha`.** The bending moment is missed.

**Thermal protection sized at max-Q.** Heating peaks higher and later.

**A steady wind profile used without shear.** Shear is what produces angle of attack.

**Buffet predicted analytically.** It is measured in a tunnel.

**A hammerhead fairing added late.** It brings a buffet environment with it.

**Load relief assumed available without checking the trajectory cost.** It costs payload.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-HDBK-1001** | Terrestrial environment criteria for launch vehicle development |
| NASA-STD-5002 | Load analyses |
| **NASA SP-8085** | Ascent vehicle wind loads |
| NASA SP-8001 | Buffeting during atmospheric ascent |
| MIL-HDBK-310 | Global climatic data |
| Range user guides | Site-specific wind statistics |

---

## Tool interface

```python
# Aerodynamic loads come from a trajectory and a wind model rather than a closed form,
# so this domain documents them and supplies the quasi-static summary they produce.
import sys
sys.path.insert(0, 'environmentsAndLoadsLibrary')

from LoadFactorSet import LoadFactorSet, FLIGHT_EVENTS

print('max-Q is the highest lateral event:')
for name, entry in FLIGHT_EVENTS.items():
    print(f'  {name:18s} lateral {entry["lateral"]:.2f} g')
```

---

## References

1. NASA SP-8085, *Ascent Vehicle Wind Loads*, 1972.
2. NASA SP-8001, *Buffeting During Atmospheric Ascent*, revised 1970.
3. NASA-HDBK-1001, *Terrestrial Environment (Climatic) Criteria Handbook*.
