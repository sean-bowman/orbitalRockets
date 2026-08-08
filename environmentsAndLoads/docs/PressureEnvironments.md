[Home](../README.md) > Pressure Environments

# Pressure Environments

## Contents

- [Overview](#overview)
- [The ascent pressure profile](#the-ascent-pressure-profile)
- [Venting](#venting)
- [Compartment differential](#compartment-differential)
- [Ascent depressurisation of hardware](#ascent-depressurisation-of-hardware)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The ambient pressure falls from one atmosphere to vacuum in a few minutes, and everything sealed, trapped or partially vented on the vehicle has to survive the transition. It is a quiet environment that produces loud failures.

---

## The ascent pressure profile

| Altitude | Pressure | Fraction of sea level |
|---|---|---|
| 0 km | 101.3 kPa | 1.00 |
| 5 km | 54.0 kPa | 0.53 |
| 11 km | 22.6 kPa | 0.22 |
| 20 km | 5.5 kPa | 0.055 |
| 30 km | 1.2 kPa | 0.012 |
| 50 km | 0.08 kPa | 0.0008 |
| **100 km** | negligible | **~0** |

**The steepest rate of change is in the first minute**, at roughly 5 to 10 kPa per second for a typical trajectory. That rate, not the final vacuum, is what sizes a vent.

**The profile is a trajectory output**, so a trajectory change is a pressure environment change. A vehicle that flies a lofted trajectory depressurises more slowly than one that flies flat.

---

## Venting

**Every enclosed volume that is not deliberately sealed must be vented, and the vent must be sized for the depressurisation rate.**

```
required vent area ~ V / (t_characteristic c)
```

**Under-venting produces a burst.** The internal pressure lags the ambient, and the differential can reach several kPa, which on a large lightweight panel is a substantial load.

**Over-venting is not free either.** A large vent admits the acoustic field, contamination and moisture, and it is a path for the exhaust plume at liftoff.

**Vent location matters as much as area.** A vent in a region of local low pressure, such as a boattail or behind a step, can pull the compartment below ambient rather than equalising it.

**Filters clog.** A vent with a contamination filter has a design flow that assumes the filter is clean, and a filter that has been on the pad through a dusty summer may not be.

---

## Compartment differential

| Compartment | Concern |
|---|---|
| **Payload fairing** | Large volume, large area, low structural pressure capability |
| **Interstage** | Vented, and it is a plume path at separation |
| **Avionics bay** | Sealed or vented, and the choice drives the box design |
| Insulation blankets | Trapped gas between layers |

**A payload fairing is the classic case.** Its volume is large, its walls are lightweight sandwich, and a few kPa of internal overpressure is a design load. Fairing vent sizing is a real analysis and it is verified by test.

**Multi-layer insulation traps gas between its layers** and it has to be vented deliberately, usually by perforating the layers. Unperforated MLI balloons and can tear.

---

## Ascent depressurisation of hardware

**Sealed boxes have to be designed for it, and the two approaches are genuinely different.**

| Approach | Character |
|---|---|
| **Sealed** | Holds one atmosphere internally for the mission |
| **Vented** | Equalises with ambient, ends up in vacuum |

**A sealed box carries a pressure vessel requirement**, including proof and leak testing, and its walls are sized for one atmosphere differential.

**A vented box ends up in vacuum**, which changes everything about its internal thermal design: convection stops, so parts that were convectively cooled must be conductively cooled. That is a common source of surprise: a box that works fine on the bench overheats in vacuum.

**Corona and arcing are the other vented-box concern.** At a few hundred pascals the breakdown voltage of air reaches a minimum, which is Paschen's law, and a high voltage circuit passing through that pressure during ascent can arc where it would not at either sea level or vacuum.

**That transition is brief and it is passed through on every flight.** High voltage hardware either stays sealed at one atmosphere, is potted, or is inhibited until the vehicle is above the corona region.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Steepest depressurisation is the first minute | 5 to 10 kPa/s |
| Size the vent for the rate, not the final vacuum | |
| Vent location matters as much as area | Local low pressure regions pull down |
| Perforate MLI | Or it balloons and tears |
| A vented box operates in vacuum | Convection stops |
| Paschen minimum is a few hundred pascals | Passed through on every ascent |
| High voltage: seal, pot, or inhibit | Through the corona region |

---

## Failure modes

**Vent sized for the final vacuum rather than the rate.** The differential peaks during ascent.

**A vent placed in a local low pressure region.** It pulls the compartment down.

**MLI not perforated.** It balloons and tears.

**A convectively cooled box vented to vacuum.** It overheats.

**High voltage hardware unprotected through the Paschen minimum.** Arcing.

**A filter assumed clean.** It has been on the pad.

**Fairing vent verified by analysis only.** It is testable and should be tested.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-HDBK-1001** | Terrestrial environment criteria, including atmosphere |
| US Standard Atmosphere 1976 | The reference profile, implemented in `common/units.py` |
| MIL-STD-810 Method 500 | Low pressure altitude test methods |
| MIL-STD-1540 | Test requirements |
| ECSS-E-ST-10-04 | Space environment |
| **IEC 60664** | Insulation coordination, including Paschen |

---

## Tool interface

```python
import sys, os
root = os.path.abspath('..')
sys.path.insert(0, os.path.join(root, 'common'))

from units import convertAltitudeToPressure, convertPressureToAltitude

for altitude in (0.0, 5000.0, 11000.0, 20000.0, 30000.0, 50000.0):
    pressure = convertAltitudeToPressure(altitude)
    print(f'{altitude / 1000.0:5.0f} km  {pressure / 1000.0:9.4f} kPa  '
          f'{pressure / 101325.0:.5f} of sea level')

# the inverse round trips, which is what makes the profile usable in both directions
print(f'round trip: {convertPressureToAltitude(convertAltitudeToPressure(11000.0)):.1f} m')
```

---

## References

1. *US Standard Atmosphere, 1976*, NOAA/NASA/USAF.
2. NASA-HDBK-1001, *Terrestrial Environment (Climatic) Criteria Handbook*.
3. Paschen, F., "Ueber die zum Funkenubergang erforderliche Potentialdifferenz", *Annalen der Physik*, 1889.
