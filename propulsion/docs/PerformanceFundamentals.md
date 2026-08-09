[Home](../README.md) > Performance Fundamentals

# Performance Fundamentals

## Contents

- [Overview](#overview)
- [Characteristic velocity](#characteristic-velocity)
- [Thrust coefficient](#thrust-coefficient)
- [Specific impulse, and why its efficiency is uninformative](#specific-impulse-and-why-its-efficiency-is-uninformative)
- [Altitude behaviour](#altitude-behaviour)
- [Flow separation](#flow-separation)
- [The Vandenkerckhove function](#the-vandenkerckhove-function)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Engine performance is three numbers that multiply, and the value of the decomposition is that the three fail independently and are measured differently.

```
F   = Cf Pc At          thrust from the coefficient and the throat
c*  = Pc At / mdot      characteristic velocity, the combustion half
Isp = Cf c* / g0        specific impulse, the product
```

Everything in this document is an elaboration of which of those a given problem lives in.

---

## Characteristic velocity

```
c* = sqrt(R Tc) / Gamma
```

with `R` the specific gas constant of the combustion products and `Gamma` the [Vandenkerckhove function](#the-vandenkerckhove-function).

**`c*` is a property of the propellant and the chamber alone.** It contains the injector, the mixing, the residence time and the completeness of combustion. Nothing downstream of the throat appears in it.

**It is also directly measurable.** `Pc At / mdot` needs a chamber pressure tap, a throat diameter and a flow measurement, all of which a test stand has, and none of which is a thrust measurement. That is what makes it the first number to look at when an engine underperforms.

The scaling is `sqrt(Tc / M)`, and the molar mass term is the more interesting one. It is why peak specific impulse sits fuel rich of stoichiometric: past the stoichiometric point, adding fuel lowers the flame temperature, but it lowers the exhaust molar mass faster. LOX/LH2 is the extreme case, with a stoichiometric ratio of 7.94 and engines running near 5.5.

**Two characteristic velocities appear in this library and they disagree.** The tabulated one is a literature equilibrium value and is what the classes use. The ideal one computed from the tabulated chamber temperature, molar mass and gamma runs from 4.3 per cent below it to 1.6 per cent above across the propellant table. That is the frozen against equilibrium difference: the ideal relation assumes a composition frozen at the chamber value, and a real expansion recombines on the way down. Both are reported and the gap is stated, because a reader who does not know it is there will eventually wonder why two correct calculations disagree.

---

## Thrust coefficient

```
Cf = Gamma sqrt( 2 gamma / (gamma - 1) (1 - (Pe/Pc)^((gamma-1)/gamma)) ) + eps (Pe - Pa) / Pc
```

Two terms, and the split matters.

**The momentum term** is a function of gamma and area ratio alone. It does not move with ambient pressure, and if it ever appears to, the implementation has the split wrong.

**The pressure term** carries all of the altitude dependence. It is positive when the nozzle is under-expanded, zero at the matched condition, and negative when over-expanded.

That second term is why a single engine has two thrust numbers, why the vacuum figure is always the larger, and why every thrust specification has to state the ambient pressure it applies at.

---

## Specific impulse, and why its efficiency is uninformative

```
Isp = Cf c* / g0
```

Both factors carry an efficiency, and they multiply:

```
Isp_delivered = (eta_c* c*) (eta_Cf Cf) / g0
```

**A combined Isp efficiency cannot be inverted.** 94.1 per cent is 96 times 98 and it is equally 98 times 96. The first is an engine with a nozzle problem and the second is an engine with an injector problem, and they need different people working on different hardware.

Typical values for a well developed engine are 96 per cent on `c*` and 98 per cent on `Cf`. The asymmetry is real: nozzles are easier to get right than injectors, because a nozzle is a geometry problem and an injector is a mixing problem.

**The diagnostic procedure is fixed by this.** Measure chamber pressure, throat area and mass flow, form `c*`, and compare against the ideal. If `c*` is nominal the loss is in the nozzle. If it is not, the loss is in the chamber and the nozzle is irrelevant to it.

---

## Altitude behaviour

For the worked example engine, 100 kN class LOX/RP-1 at 10 MPa and an area ratio of 16:

| Altitude [km] | Ambient [kPa] | `Cf` | `Isp` [s] |
|---|---|---|---|
| 0 | 101.325 | 1.5740 | 280.9 |
| 5 | 54.020 | 1.6482 | 294.1 |
| 10 | 26.436 | 1.6914 | 301.8 |
| 20 | 5.475 | 1.7243 | 307.7 |
| 30 | 1.172 | 1.7310 | 308.9 |
| 50 | 0.076 | 1.7328 | 309.2 |

**The curve flattens hard.** Between 30 km and 50 km the specific impulse gains 0.3 seconds, because the pressure term has already gone to nearly zero. Above roughly 30 km an engine is at its vacuum performance and reporting further altitudes says nothing.

The vacuum to sea level ratio here is 1.101. It grows with area ratio, because a larger expansion has more exit area for the pressure term to act on.

**A fixed nozzle is optimum at exactly one altitude.** This one matches ambient at 4.2 km. Below that it is over-expanded and above it under-expanded, and both cost performance. Only the over-expanded side is dangerous.

---

## Flow separation

When the exit pressure falls far enough below ambient, the boundary layer cannot negotiate the adverse gradient and detaches from the wall. Summerfield's criterion puts it at

```
Pe < 0.4 Pa
```

**This is a cliff and not a penalty.** Past it the flow is unsteady, the separation point moves, and the nozzle sees a side load it was not designed for. Separation has destroyed hardware, and it is the reason a vacuum optimised nozzle cannot simply be lit on the pad.

The criterion is crude, and it is the one everybody uses, because the alternatives need the wall boundary layer and are not better in the regime where the answer is to not do that. **Design short of it.** The worked example holds five per cent back on area ratio, which costs 0.2 seconds of burn-averaged impulse.

For the example engine at 10 MPa, the separation limit at sea level is an area ratio of 21.42. Expansions past that separate:

| Area ratio | Sea level `Isp` [s] | Vacuum `Isp` [s] | Separated at sea level |
|---|---|---|---|
| 10 | 283.0 | 300.7 | No |
| 20 | 277.4 | 312.8 | No |
| 40 | 251.6 | 322.5 | Yes |
| 80 | 188.5 | 330.3 | Yes |
| 160 | 53.2 | 336.7 | Yes |

The sea level column past the separation limit is a fiction: those numbers are what the attached-flow relations predict, and the flow is not attached. **They are reported alongside the separation flag rather than suppressed**, because the flag is the finding and a blank cell is not.

---

## The Vandenkerckhove function

```
Gamma = sqrt(gamma) (2 / (gamma + 1)) ^ ((gamma + 1) / (2 (gamma - 1)))
```

It appears in the choked mass flow, in `c*` and in `Cf`, and it varies remarkably little:

| gamma | `Gamma` |
|---|---|
| 1.13 | 0.6346 |
| 1.15 | 0.6386 |
| 1.20 | 0.6485 |
| 1.24 | 0.6562 |
| 1.30 | 0.6673 |
| 1.40 | 0.6847 |

**Under eight per cent across the entire range a rocket ever sees.** That insensitivity is why order of magnitude engine numbers can be done in the head with `Gamma` about 0.65, and it is why an error in gamma is rarely the reason a performance prediction is wrong. The places gamma matters are the exponents in the area ratio and pressure ratio relations, not this group.

---

## Design rules of thumb

- **Form `c*` before anything else.** It is measurable without a load cell and it halves the problem.
- **Never quote a combined Isp efficiency alone.** It cannot be inverted into a diagnosis.
- **State the ambient pressure with every thrust and impulse figure.**
- **Stop reporting altitudes above about 30 km.** The engine is at vacuum performance and the rows say nothing.
- **Design short of the separation limit**, because the criterion has scatter and the failure is structural.
- **Take `Gamma` as 0.65** for a first pass. It is right to within four per cent for anything.

---

## Failure modes

**An Isp shortfall investigated without `c*`.** Half the engine gets worked on and it may be the wrong half.

**A thrust figure without its ambient pressure.** Ten per cent ambiguity on a first stage engine, more on an upper stage.

**The momentum term made altitude dependent.** A coding error that produces plausible numbers, which is why it is worth a test.

**Attached-flow relations applied past separation.** They return a number and the number is fiction.

**Sea level start of a vacuum expansion.** The nozzle separates, and the side load is the problem rather than the performance.

**Frozen ideal `c*` compared against an equilibrium measurement.** They differ by a few per cent for real physical reasons, and treating the gap as an efficiency loss charges the injector for thermodynamics.

---

## Worked numbers

LOX/RP-1 at 10 MPa chamber pressure, 96 per cent `c*` efficiency and 98 per cent `Cf` efficiency.

| Quantity | Value |
|---|---|
| Ideal characteristic velocity | 1823 m/s |
| Delivered characteristic velocity | 1750.1 m/s |
| Thrust coefficient at sea level, area ratio 16 | 1.5740 |
| Momentum term | 1.6727 |
| Pressure term | -0.0666 |
| Sea level specific impulse | 280.9 s |
| Vacuum specific impulse | 309.2 s |
| Combined efficiency | 94.1 % |
| Optimum expansion altitude | 4.2 km |
| Separation limit area ratio at sea level | 21.42 |

**Checked against hardware.** At an area ratio of 16 this gives 280.9 s sea level and 309.2 s vacuum, against 282 and 311 for Merlin 1D. The agreement is closer than the method deserves and should not be read as validation of anything but the arithmetic.

---

## Standards

| Standard | What it gives you |
|---|---|
| NASA SP-125 | Design of liquid propellant rocket engines. The performance chapters are still the clearest |
| CPIA 246 | Liquid rocket engine performance prediction and evaluation, the JANNAF methodology |
| JANNAF simplified and standardised performance | How a delivered Isp is reduced from test data defensibly |
| NASA RP-1311 | The CEA program and its theory, which is where the propellant properties come from |
| ISO 21349 | Space systems, inspection and test of propulsion subsystems |

**The JANNAF methodology is the reference for any Isp number that has to be defended contractually**, because it fixes what is included in a delivered performance figure and what is not.

---

## Tool interface

```python
from EnginePerformance import EnginePerformance

performance = EnginePerformance()
performance.setInputs({'combination':                 'LOX/RP-1',
                       'chamberPressure':             10.0e6,
                       'areaRatio':                   16.0,
                       'cstarEfficiency':             0.96,
                       'thrustCoefficientEfficiency': 0.98})

cstar = performance.calculateCharacteristicVelocity()
print(cstar['ideal'], cstar['delivered'])

thrustCoefficient = performance.calculateThrustCoefficient()
print(thrustCoefficient['momentumTerm'], thrustCoefficient['pressureTerm'])
print(thrustCoefficient['separated'])

impulse = performance.calculateSpecificImpulse()
print(impulse['delivered'], impulse['combinedEfficiency'])

altitude = performance.calculateAltitudePerformance()
print(altitude['optimumAltitude'], altitude['vacuumImpulse'])
```

---

## References

- Sutton and Biblarz, *Rocket Propulsion Elements*, chapters 3 and 5
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- Summerfield, Foster and Swan, *Flow separation in overexpanded supersonic exhaust nozzles*
- NASA SP-125, *Design of Liquid Propellant Rocket Engines*
- CPIA 246, *Liquid rocket engine performance prediction and evaluation*
