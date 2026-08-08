[Home](../README.md) > Thermal Control Systems

# Thermal Control Systems

## Contents

- [Overview](#overview)
- [Passive first](#passive-first)
- [The hot case and the cold case are one problem](#the-hot-case-and-the-cold-case-are-one-problem)
- [Temperature limits, operational and survival](#temperature-limits-operational-and-survival)
- [Heater sizing](#heater-sizing)
- [Duty cycle, energy and thermostat life](#duty-cycle-energy-and-thermostat-life)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Thermal control is the business of keeping every component inside its limits in every case the mission contains, and it is almost entirely a problem of the two extremes rather than the average.

The structure of the problem is fixed. There is a hot case, where everything is dissipating, the sun is on the wrong surfaces, and the coatings have degraded. There is a cold case, where nothing is dissipating, the vehicle is in eclipse, and the coatings are new. **The design has to close at both, and the levers that help one hurt the other.**

---

## Passive first

The ordering is not a preference, it is a cost.

| Approach | What it costs |
|---|---|
| Coating selection | Nothing. It is the surface you were going to have anyway |
| Radiator sizing and placement | Mass and area |
| Conduction path design, isolators, straps | Mass, and some design freedom |
| Heaters | Power, continuously, for the whole mission |
| Louvres, variable conductance | Mass, complexity, a mechanism |
| Pumped loops | All of the above, plus a single point failure |

**Every passive lever exhausted is heater power not spent.** A heater is the only item on that list whose cost recurs every orbit for the life of the mission, and it is the item most often added late because it is the easiest to add.

---

## The hot case and the cold case are one problem

This is the point that makes thermal control different from most sizing problems.

A radiator sized for the hot case is oversized for the cold case, by definition. In the cold case it is still there, still radiating, and the heat it rejects has to be replaced by a heater. **The radiator that solved the hot case created the cold case load.**

So the two cases are not independent analyses with independent margins. They are a single optimisation, and the correct objective is usually to minimise heater energy subject to closing the hot case, rather than to maximise hot case margin.

**A hot case margin of 20 K is not free.** It was bought with radiator area, and the same area is paid for in the cold case at every eclipse for the mission duration.

The [worked example](../codeInterface.py) shows the shape of it: 35 W of avionics dissipation needs 0.148 m^2 of radiator at 305 K, and the same avionics in the cold case need 27 W of sized heater at a 67 per cent duty cycle, which is 78.8 kWh over a one year mission.

---

## Temperature limits, operational and survival

Every component has two bands and they are not interchangeable.

| Component | Operational [K] | Survival [K] |
|---|---|---|
| Electronics | 263 to 323 | 243 to 343 |
| Battery | 273 to 303 | 263 to 318 |
| Propellant, N2H4 | 288 to 313 | 280 to 323 |
| Optics | 288 to 298 | 263 to 323 |
| Mechanism | 253 to 333 | 233 to 353 |

**Operational means it works. Survival means it is not damaged and will work again once it is back in band.**

The distinction is worth real power. Electronics have a 60 K operational band and a 100 K survival band. **Sizing a heater to the survival band rather than the operational band is a large saving, and whether it is allowed is a requirements question rather than a thermal one.** If the hardware genuinely does not have to operate while cold, sizing to survival is correct and the analysis should say so out loud rather than defaulting to the tighter band.

Batteries are the exception that drives most spacecraft cold cases. A 30 K operational band, with the lower limit at the freezing point of the electrolyte, and a capacity that falls sharply below it. **The battery is usually why there is a survival heater at all.**

Hydrazine is the other one. It freezes at 275 K, and a frozen line is a mission ending event because thawing it can burst the line. The propellant limits above have almost no margin below and they are not negotiable.

---

## Heater sizing

The calculation itself is not difficult.

```
required = coldCaseLoss - internalDissipation
sized    = required x margin
```

The margin is typically 1.5 and it covers the things the cold case analysis did not know: degraded insulation, a colder than predicted sink, a component that turned out not to dissipate what its datasheet claimed.

**Internal dissipation is a real credit and it is frequently forgotten.** A box that dissipates 2 W in a 12 W cold case needs 10 W of heater, not 12. That is a 17 per cent saving available for free, and it is missed whenever the heater is sized against the loss rather than against the net.

The subtlety is that the dissipation credit is only available when the box is on. **A survival heater has to close with zero internal dissipation**, because the case it exists for is the one where everything is off.

---

## Duty cycle, energy and thermostat life

A thermostatically controlled heater cycles between a lower and an upper setpoint separated by the deadband.

```
dutyCycle = required / sized
```

The sized power is on for the fraction of the time needed to supply the required power. **A generously sized heater does not use more energy; it uses the same energy at a lower duty cycle.** What it changes is the cycle period and therefore the thermostat cycle count.

```
period = thermalMass x deadband / required
cycles = missionDuration / period
```

**Thermostat cycle life is a real design constraint.** Mechanical thermostats are rated in the tens of thousands of cycles. A small thermal mass with a tight deadband on a long mission can exhaust that.

The levers are the deadband, which is usually set by the temperature limits, and the thermal mass, which is usually set by the hardware. Where neither can move, the answer is a solid state controller rather than a bimetallic thermostat.

**The energy number is the one that belongs in a different budget.** 78.8 kWh over a mission is a power system input, and it was created by a thermal decision. Thermal and power are usually budgeted separately, and the radiator that caused the heater load rarely appears in the power budget's justification.

---

## Design rules of thumb

- **Exhaust the passive levers before adding a heater.** Coatings are free, heaters are not.
- **Size the hot case at end of life and the cold case at beginning of life.** Optical degradation moves them in opposite directions.
- **Credit internal dissipation in the operational cold case and not in the survival case.**
- **Ask whether the survival band is acceptable before sizing to operational.** The saving is large and the question is a requirements one.
- **Check the thermostat cycle count**, not just the duty cycle.
- **Cost heater energy against the radiator that caused it**, in the same trade.
- **Put the battery first.** It usually sets the cold case and it has the narrowest band.

---

## Failure modes

**Heater sized against the loss rather than the net.** Oversized by the internal dissipation, every time.

**Survival heater sized with a dissipation credit.** The case it exists for is the one where nothing is dissipating.

**Hot and cold cases traded separately.** Produces a design with excellent hot case margin and an unaffordable heater budget.

**Thermostat cycle life not checked.** A tight deadband on a small mass can exceed the rating well inside the mission.

**Beginning of life properties in the hot case.** White paint moves 41 K over a mission, which is larger than most margins.

**Operational band used where survival would do.** Buys power that was never required.

---

## Worked numbers

A battery, 12 W cold case loss, 2 W internal dissipation, 5000 J/K thermal mass, 5 K deadband, one year mission.

| Quantity | Value |
|---|---|
| Governing band | Operational, 273.15 to 303.15 K |
| Required power | 10.0 W |
| Sized power at 1.5 margin | 15.0 W |
| Lower setpoint | 273.15 K |
| Upper setpoint | 278.15 K |
| Duty cycle | 66.7 % |
| Cycle period | 7500 s |
| Thermostat cycles over the mission | 2100 |
| Heater energy over the mission | 43.8 kWh |
| Hot case at 300 K against a 303.15 K limit | +3.1 K margin |

**The operational band is 30 K and the survival band is 55 K.** If the battery only had to survive rather than operate while cold, the required power would fall substantially. It does not, because a battery that is cold is a battery that cannot deliver current, which is exactly what the vehicle needs it for.

The avionics case from the worked example, 18 W cold case loss, no dissipation credit, 5200 J/K:

| Quantity | Value |
|---|---|
| Required power | 18.0 W |
| Sized power | 27.0 W |
| Duty cycle | 66.7 % |
| Thermostat cycles | 3635 |
| Heater energy over the mission | 78.8 kWh |
| Hot case margin | +18.1 K |

---

## Standards

| Standard | What it gives you |
|---|---|
| ECSS-E-ST-31C | Thermal control general requirements |
| ECSS-E-ST-10-03C | Testing, including thermal vacuum and cycling |
| NASA-STD-7001 | Payload vibroacoustic test criteria, for the survival case definitions |
| MIL-STD-1540 | Test requirements for launch and space vehicles |
| NASA-HDBK-2001 | Spacecraft thermal control handbook |

---

## Tool interface

```python
from ThermalControl import ThermalControl

control = ThermalControl()
control.setInputs({'component':           'battery',
                   'coldCaseLoss':        12.0,
                   'hotCaseTemperature':  300.0,
                   'internalDissipation': 2.0,
                   'thermalMass':         5000.0,
                   'missionDuration':     3.15e7,
                   'deadband':            5.0})

heater = control.sizeHeater()
print(heater['requiredPower'], heater['sizedPower'], heater['governingBand'])

duty = control.calculateDutyCycle()
print(duty['dutyCycle'], duty['cycles'], duty['energy'] / 3.6e6)

print(control.checkHotCase()['margin'])
```

`TEMPERATURE_LIMITS` carries both bands for each component class, and `governingLimits` reports which one was used.

---

## References

- Gilmore, *Spacecraft Thermal Control Handbook*, volume I
- NASA-HDBK-2001, *Spacecraft Thermal Control Handbook*
- ECSS-E-ST-31C, *Thermal control general requirements*
- Karam, *Satellite Thermal Control for Systems Engineers*
