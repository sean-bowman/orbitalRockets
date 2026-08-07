[Home](../README.md) > Process Parameters

# Process Parameters

## Contents

- [Overview](#overview)
- [Extrusion pressure](#extrusion-pressure)
- [Wall shear stress](#wall-shear-stress)
- [Cycle count](#cycle-count)
- [Flow rate and velocity](#flow-rate-and-velocity)
- [Temperature](#temperature)
- [What to change when](#what-to-change-when)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Four parameters: media grade, pressure, cycle count and temperature. Media grade is chosen from the passage size and then fixed, so the process is really controlled by the other three.

Everything they do runs through one intermediate quantity: the wall shear stress.

---

## Extrusion pressure

Typically 3 to 20 MPa, and it is the primary control.

**Pressure sets the wall shear directly** and therefore the removal rate. Higher pressure means faster removal and a shorter cycle time.

| Limit | Reason |
|---|---|
| **Fixture strength** | The fixture has to react the full pressure over the media area |
| **Part strength** | A thin walled part can be deformed by internal pressure |
| **Media temperature rise** | Higher pressure means more work and more heat |
| Machine capability | 20 MPa is a large machine |

**On a thin walled additive part the part itself is often the limit.** A 0.5 mm wall with 15 MPa inside it is at a real hoop stress, and honing a part into a bulge is a recoverable mistake only if it is noticed.

---

## Wall shear stress

```
tau_w = dP * D / (4 * L)
```

**This is a force balance on the media column and it does not depend on the rheology at all.** The pressure drop across the passage has to be reacted by shear on the wall, whatever the media is made of. That is a useful thing to know: the shear can be computed before anything is known about the media.

**The inverse length dependence is why long passages are hard.** At fixed pressure, doubling the length halves the wall shear and therefore roughly halves the removal rate.

**The direct diameter dependence is why small passages are hard.** Halving the diameter halves the shear too. A small, long passage is doubly penalised, and it is exactly the geometry an additive manifold produces.

| Passage | Pressure | Shear |
|---|---|---|
| 5 mm x 200 mm | 7 MPa | 43.8 kPa |
| 5 mm x 400 mm | 7 MPa | 21.9 kPa |
| 5 mm x 200 mm | 14 MPa | 87.5 kPa |
| 2.5 mm x 200 mm | 7 MPa | 21.9 kPa |

---

## Cycle count

One pass in each direction is one cycle. Typically 5 to 50.

**Removal rises sub-linearly with cycles:**

```
deltaR ~ N^0.85
```

The exponent is below one because the passage opens as it is honed, which drops the wall shear, which slows the removal. **The process self-limits**, and that is a helpful property: an extra cycle on a part that is nearly finished does less damage than it would if the relation were linear.

**Finish decays exponentially rather than as a power law:**

```
Ra_N = Ra_inf + (Ra_0 - Ra_inf) * exp(-k * N)
```

**The two behave differently and that is the key process insight.** The finish reaches its floor well before the removal stops. Cycles past the finish floor remove stock and open the passage without improving anything.

---

## Flow rate and velocity

Flow rate is a consequence rather than a control, but it is worth computing because it is what the operator sees.

For a power law fluid in a circular passage the mean velocity follows from the wall shear and the rheology. What matters practically:

| Observation | Meaning |
|---|---|
| Flow far slower than expected | The media is too stiff, or the passage is partly blocked |
| Flow far faster than expected | The media has degraded, or a seal is bypassing |
| Flow falling through a run | Media heating and thinning, or swarf loading |

**Flow rate is the best available process monitor** and it costs nothing to record.

---

## Temperature

Media heats as it is worked. Viscosity falls with temperature, so the apparent shear rate rises at the same wall shear, and the removal rate changes.

**A part honed cold and one honed hot are not the same part.** Temperature control is what makes the process repeatable, and an uncontrolled process drifts through a shift in a direction nobody records.

---

## What to change when

| Symptom | Change |
|---|---|
| Removal too slow | Raise the pressure, or a harder media |
| Removal too fast to control | Lower the pressure, more cycles |
| Finish not improving | Finer media. The floor has been reached |
| Passage grown too much | Fewer cycles, or a softer media |
| Uneven removal along the passage | Reverse the flow more often, or check the fixture |
| Uneven removal between branches | Restrictors. See [FixturingAndFlowControl.md](FixturingAndFlowControl.md) |
| Drift through a shift | Control the media temperature |

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Pressure | 3 to 20 MPa |
| Cycles | 5 to 50 |
| Wall shear | `dP D / (4 L)`, independent of the media |
| Removal against cycles | `N^0.85`, sub-linear |
| Finish decay | Exponential to a floor |
| Finish reaches its floor first | Later cycles only remove stock |
| Thin walled parts | The part may limit the pressure |
| Record the flow rate | The cheapest available monitor |

---

## Failure modes

**Cycling past the finish floor.** Stock removed, no improvement.

**Pressure above what a thin wall can take.** The part bulges.

**Uncontrolled media temperature.** The process drifts through the shift.

**A long passage honed at the pressure suited to a short one.** Under-processed.

**Flow rate not recorded.** The one cheap monitor discarded.

---

## Standards

| Standard | Scope |
|---|---|
| ISO 4287 / 21920 | Surface texture |
| ASME B46.1 | Surface texture |
| ASTM D2196 | Rheological properties |

---

## Tool interface

```python
from ExtrusionHoning import ExtrusionHoning

for length in (0.10, 0.20, 0.40):
    honing = ExtrusionHoning()
    honing.setInputs({'passageDiameter': 0.005, 'passageLength': length,
                      'extrusionPressure': 7.0e6, 'cycleCount': 20})
    shear = honing.calculateWallShear()
    print(f'{length*1000:.0f} mm: tau_w = {shear["wallShearStress"]/1000:.1f} kPa, '
          f'L/D = {shear["lengthToDiameter"]:.0f}')
```

---

## References

1. Jain, V. K. and Adsul, S. G., "Experimental Investigations into Abrasive Flow Machining", *International Journal of Machine Tools and Manufacture*, Vol. 40, 2000.
2. Kumar, S. et al., "A Review on Abrasive Flow Machining", *Materials Today Proceedings*, Vol. 5, 2018.
3. Rhoades, L. J., "Abrasive Flow Machining", *Manufacturing Engineering*, Vol. 101, 1988.
