[Home](../README.md) > Flow and Functional Testing

# Flow and Functional Testing

## Contents

- [Overview](#overview)
- [Flow calibration](#flow-calibration)
- [Determining Cd and Cv](#determining-cd-and-cv)
- [Functional testing](#functional-testing)
- [Response and timing](#response-and-timing)
- [Seat leakage](#seat-leakage)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Flow and functional testing establishes what the hardware actually does, as opposed to what the analysis predicted. For anything with a flow passage this is not optional: discharge coefficients cannot be predicted to better than about five percent, and for an additively manufactured passage not to better than twenty.

The output that matters is a **recorded number per article**, not a pass or fail. That number is the baseline against which erosion, plugging and edge rounding are detected over the article's life.

---

## Flow calibration

**Flow the article with a reference fluid at a defined differential and record the flow number:**

```
K_w = mdot / sqrt(dP)        [kg/s / sqrt(Pa)]
```

**Report a flow number, not a discharge coefficient.** The flow number is directly measured. A Cd requires assuming an area, and the area is exactly what is uncertain on a small or additively manufactured passage.

**Reference fluids:** water or IPA for liquid elements, GN2 for gas. Convert to the service fluid by density ratio, and note that the conversion is only valid if the Reynolds numbers are comparable. A trim orifice calibrated on water at Re = 10^5 and used on cold hydrazine at Re = 2000 has a different Cd, because Cd falls below Re = 10^4. See [fluidSystemsLibrary/docs/Orifices.md](../../fluidSystemsLibrary/docs/Orifices.md).

**Test at the service Reynolds number where it matters**, or at several points so the Reynolds dependence is characterized rather than assumed.

---

## Determining Cd and Cv

**Discharge coefficient**, from a measured flow and a measured area:

```
Cd = mdot / ( A * sqrt(2 * rho * dP) )
```

**Flow coefficient**, from the definition:

```
Cv = mdot / ( 2.40172e-5 * sqrt(rho * dP) )
```

Both require the differential to be measured across the article alone, which means tap placement matters and the approach and exit losses have to be either excluded or accounted for.

**Take multiple points across the operating range.** A single point gives a number with no indication of whether the relation is square-law, and a valve that is choked at the test condition and unchoked in service has been characterized at the wrong point entirely.

**For a valve, characterize against travel.** The inherent characteristic is what the control system needs, and it is measured by stepping travel and recording flow at constant differential.

---

## Functional testing

| Test | What it establishes | Notes |
|---|---|---|
| Stroke | Full travel in both directions | At the actual supply pressure, not shop air |
| **Function at differential** | It operates against its design load | A valve that strokes freely unloaded may not stroke at pressure |
| Setpoint | Regulator outlet, relief crack, check valve cracking | Across the inlet pressure range, not at one point |
| Position indication | The indicator agrees with the stem | Indicate on the stem, not the actuator |
| Response time | Opening and closing | See below |
| Seat leakage | Internal leakage when closed | See below |

**Test at differential.** This is the single most common functional test shortcut and it invalidates the result. A valve stroking with no pressure across it demonstrates the actuator and nothing about whether it can operate against its unbalance load.

**Test at the actual supply pressure.** A pneumatic actuator on 100 psi shop air behaves differently from the same actuator on its flight supply.

---

## Response and timing

**Effective closure time is not stroke time.** A valve with an equal-percentage or quick-opening characteristic does most of its flow reduction in the last part of its travel, so the time over which the velocity actually changes can be a small fraction of the total stroke. That effective time, not the stroke time, is what drives water hammer.

**Measure it properly:** record the command, the position and a downstream pressure or flow simultaneously, at a sample rate at least ten times the event bandwidth. For a 20 ms closure that is 5 kHz minimum, and 10 kHz is better.

**The pilot circuit usually sets the response**, not the main valve. A fast main valve fed through a long, small-bore pilot line is a slow valve.

---

## Seat leakage

Classified by ANSI/FCI 70-2:

| Class | Allowable |
|---|---|
| II | 0.5 % of rated capacity |
| III | 0.1 % |
| IV | 0.01 % (typical metal seat) |
| V | 5e-4 mL/min per mm of seat diameter per bar |
| **VI** | Bubble-tight, defined bubble count by seat size (soft seat) |

**For propulsion, the requirement is usually stated as an absolute helium leak rate instead**, because that is what can actually be measured on flight hardware and because it is comparable to the external leak requirement.

**Seat leakage after a single particle is permanent.** This is why filtration upstream of any valve that has to seal is not optional, and why seat leakage is re-checked after every environmental exposure.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Record a flow number per article | It is the baseline for life trending |
| Report flow number, not Cd | The number is measured; Cd requires assuming an area |
| Multiple points across the range | One point cannot show the relation |
| Test at differential | The most common invalidating shortcut |
| Test at actual supply pressure | Not shop air |
| Sample rate for timing | >= 10x the event bandwidth |
| Effective closure time | From the characteristic, not the stroke time |
| Reynolds match, or characterize the dependence | Cd falls below Re = 10^4 |
| Re-check seat leakage after every environment | A single particle is permanent |

---

## Failure modes

**A pass/fail record with no number.** The article passed and there is no baseline to trend against.

**Calibration at the wrong Reynolds number**, giving a Cd that does not apply in service.

**Functional test with no differential.** The actuator is characterized and the seat is not.

**Timing measured at too low a sample rate.** A 20 ms event on a 100 Hz system is three points.

**Stroke time reported as closure time.** The water hammer analysis then uses a number three times too long.

**Seat leakage checked once, at the start.** Environmental damage goes undetected.

**Differential measured across more than the article**, so approach and exit losses are included in the Cd.

---

## Worked example

Cv determination for the thruster valve, from [`codeInterface.py`](../codeInterface.py):

| Quantity | Value |
|---|---|
| Measured Cv | 0.348 |
| Expanded uncertainty (k = 2) | +/- 0.0084 |
| Relative | 2.41 % |
| Dominant contributor | Pressure transducer, 39 % of the variance |

The uncertainty budget behind that number is in [UncertaintyAndStatistics.md](UncertaintyAndStatistics.md). The useful output is the dominant contributor: the pressure transducer is 39 percent of the variance, so improving the flow meter or the temperature control will not move the result. Buying a better transducer will.

---

## Standards

| Standard | Scope |
|---|---|
| **IEC 60534-2-1** | Control valve flow capacity sizing equations |
| ISA-75.02.01 | Control valve capacity test procedures |
| **ANSI/FCI 70-2** | Control valve seat leakage classification |
| API 598 | Valve inspection and testing |
| MSS SP-61 | Pressure testing of valves |
| ISO 5167 | Flow measurement by pressure differential devices |
| ASME PTC 19.5 | Flow measurement |
| ASME MFC-3M | Flow measurement using orifice, nozzle and venturi |

---

## Tool interface

The design-side classes compute what the test should measure:

```python
from Valve import Valve            # fluidSystems design library
from Orifice import Orifice

valve = Valve()
valve.setInputs({'fluid': 'N2H4', 'upstreamPressure': 2.35e6, 'downstreamPressure': 2.30e6,
                 'upstreamTemperature': 293.15, 'massFlow': 0.045,
                 'valveType': 'ball full bore', 'nominalSize': 0.00635})
valve.sizeFlowCoefficient()        # the Cv the test should find
curves = valve.calculateCharacteristic(21)   # the characteristic the test should trace
```

and the uncertainty in the measurement comes from [`UncertaintyBudget`](../fluidSystemsTestingLibrary/UncertaintyBudget.py).

---

## References

1. IEC 60534-2-1:2011, *Industrial-process control valves: flow capacity sizing equations*.
2. ANSI/FCI 70-2, *Control Valve Seat Leakage*.
3. Emerson Process Management, *Control Valve Handbook*, 5th ed., 2019.
4. ISO 5167-2:2022, *Measurement of fluid flow by means of pressure differential devices: orifice plates*.
