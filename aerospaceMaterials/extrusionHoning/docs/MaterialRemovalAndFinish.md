[Home](../README.md) > Material Removal and Finish

# Material Removal and Finish

## Contents

- [Overview](#overview)
- [The removal model](#the-removal-model)
- [Dimensional growth](#dimensional-growth)
- [The finish model](#the-finish-model)
- [The grit-limited floor](#the-grit-limited-floor)
- [Edge radius](#edge-radius)
- [Workpiece hardness](#workpiece-hardness)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Two outputs matter and they behave differently. Removal keeps accumulating; finish reaches a floor and stops. Knowing where the floor is decides when to stop the process.

---

## The removal model

```
deltaR = C * tau_w^1.15 * N^0.85
```

**The shear exponent is above one.** Higher shear presses the abrasive harder into the wall and also increases the number of particles passing per unit time, so the two effects compound slightly.

**The cycle exponent is below one.** The passage opens as it is honed, which drops the wall shear, which slows the removal. The process self-limits.

Both are empirical and both are calibrated per material and media. The coefficient `C` should be established from coupons rather than taken from a table, and that is what [ProcessQualification.md](ProcessQualification.md) is for.

---

## Dimensional growth

**Removing material from the wall of a passage opens it.** Diametral growth is twice the radial removal.

**The consequence people forget: an orifice sized before honing is no longer the size it was.**

On a flow-critical passage there are two options and both are decisions rather than defaults:

| Option | Practice |
|---|---|
| **Put the honing in the tolerance stack** | Size the passage undersize by the predicted growth |
| **Size the orifice after honing** | Hone first, then drill or EDM the metering feature |

**The second is safer and it is not always possible**, because the metering feature may be inside the honed passage.

**Growth of 1 to 3 percent on diameter is typical** for a useful amount of finish improvement, which is far more than a flow tolerance usually allows.

---

## The finish model

```
Ra_N = Ra_inf + (Ra_0 - Ra_inf) * exp(-k * N)
```

Roughness falls exponentially because each cycle removes the remaining peaks and the peaks get progressively harder to reach.

| Cycles | Ra from 20 um |
|---|---|
| 1 | 16.4 um |
| 5 | 8.7 um |
| 10 | 6.1 um |
| **12** | **5.6 um, within 10 % of the floor** |
| 20 | 5.06 um |
| 40 | 5.00 um |

**The last thirty percent of the improvement takes as long as the first seventy**, which is characteristic of exponential decay and it is why an operator's instinct to run a few more cycles is usually wasted.

---

## The grit-limited floor

```
Ra_inf ~ gritSize / 40
```

**The abrasive cannot produce a surface finer than the scratch it leaves.** That floor is the most important limit in the process.

| Media | Grit | Floor |
|---|---|---|
| Very soft | 60 um | 1.50 um |
| Soft | 110 um | 2.75 um |
| **Medium** | 200 um | **5.00 um** |
| Hard | 350 um | 8.75 um |
| Very hard | 550 um | 13.75 um |

**Running more cycles past the floor accomplishes nothing except removing stock and opening the passage.** A finer finish needs a finer media, which needs a second setup with a second media, a second fixture cleanout and a second process qualification.

**Two-stage honing is normal for a demanding finish**: a coarse media to remove the bulk and a fine one to finish. It doubles the setup cost and it is the only route below the coarse floor.

---

## Edge radius

**Abrasive flow rounds sharp edges as a side effect**, because the flow accelerates around a corner and the local shear rises.

Typically the edge radius is about half the radial removal, so a 50 um removal produces a 25 um edge break.

**That is usually wanted.** Deburring cross-drilled intersections is a primary application, and the edge break improves fatigue by removing the stress concentration.

**Occasionally it is not.** A sharp-edged orifice was sized sharp, and rounding its entry changes the discharge coefficient measurably. See [fluidSystems Orifices.md](../../../fluidSystems/fluidSystemsLibrary/docs/Orifices.md), where the entry geometry is one of the primary Cd drivers.

---

## Workpiece hardness

Removal scales roughly with the inverse square root of hardness.

| Material | Hardness [HV] | Relative removal |
|---|---|---|
| 6061-T6 | 95 | 1.62 |
| 316L | 150 | 1.29 |
| Ti-6Al-4V | 334 | 0.87 |
| Inconel 718 STA | 400 | 0.79 |

**Nickel alloys are the hard case and the mechanism is worse than the hardness suggests**, because they work harden under a dulling abrasive. A silicon carbide media that starts cutting can stall as it dulls, and boron carbide is the answer.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Removal | `tau^1.15 N^0.85` |
| Diametral growth | 2x radial removal, 1 to 3 % typical |
| Finish decay | Exponential |
| Finish floor | grit / 40 |
| Cycles to the floor | ~12 for a 4x improvement |
| Edge radius | ~0.5x radial removal |
| Hardness effect | ~1/sqrt(HV) |
| Two-stage honing | For a finish below the coarse floor |

---

## Failure modes

**Passage growth not in the tolerance stack.** The orifice is no longer the size it was.

**Cycling past the floor.** Stock removed, no improvement.

**A sharp orifice entry rounded.** The discharge coefficient changed.

**Nickel alloy honed with a dulling abrasive.** The process stalls.

**Removal coefficient taken from a table.** It is material and media specific.

---

## Worked numbers

From [`ExtrusionHoning`](../extrusionHoningLibrary/ExtrusionHoning.py), 4.76 mm x 180 mm Inconel 718, 7 MPa, medium media:

| Cycles | Radial removal | Diametral growth | Ra |
|---|---|---|---|
| 10 | 28.7 um | 0.57 mm... 57 um | 6.1 um |
| **20** | **51.8 um** | **104 um (2.18 %)** | **5.06 um** |
| 40 | 93.3 um | 187 um (3.92 %) | 5.00 um |

**Doubling from 20 to 40 cycles doubles the growth and improves the finish by 1 percent.** That is the whole argument for stopping at the floor.

---

## Standards

| Standard | Scope |
|---|---|
| **ISO 4287 / 21920** | Surface texture, profile method |
| ASME B46.1 | Surface texture |
| ISO 25178 | Areal surface texture |
| ISO 13715 | Edges of undefined shape, indication and dimensioning |

---

## Tool interface

```python
from ExtrusionHoning import ExtrusionHoning

for cycles in (5, 10, 12, 20, 40):
    honing = ExtrusionHoning()
    honing.setInputs({'passageDiameter': 0.00476, 'passageLength': 0.180,
                      'material': 'Inconel 718', 'condition': 'lpbf hip + sta',
                      'cycleCount': cycles})
    honing.calculateWallShear()
    removal = honing.calculateRemoval()
    finish  = honing.calculateSurfaceFinish()
    print(f'{cycles:2d}: {removal["radialRemoval"]*1e6:5.1f} um removed, '
          f'{removal["diametralGrowthPercent"]:.2f} % growth, '
          f'Ra {finish["finalRoughness"]*1e6:.2f} um')
```

---

## References

1. Williams, R. E. and Rajurkar, K. P., "Stochastic Modeling and Analysis of Abrasive Flow Machining", *Journal of Engineering for Industry*, Vol. 114, 1992.
2. Jain, R. K. and Jain, V. K., "Specific Energy and Temperature Determination in Abrasive Flow Machining", *International Journal of Machine Tools and Manufacture*, Vol. 41, 2001.
3. Kumar, S. et al., "A Review on Abrasive Flow Machining", *Materials Today Proceedings*, Vol. 5, 2018.
