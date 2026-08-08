[Home](../README.md) > Thermal Testing

# Thermal Testing

## Contents

- [Overview](#overview)
- [What each test proves](#what-each-test-proves)
- [Thermal balance](#thermal-balance)
- [Thermal vacuum and thermal cycling](#thermal-vacuum-and-thermal-cycling)
- [Qualification and acceptance](#qualification-and-acceptance)
- [Instrumentation](#instrumentation)
- [The tests that catch soakback](#the-tests-that-catch-soakback)
- [Ground test artefacts](#ground-test-artefacts)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Thermal testing serves two distinct purposes that get conflated, and the conflation is the source of most arguments about what a test was for.

**One purpose is to correlate the model.** That is thermal balance, it is run at steady conditions, and its output is a set of parameters rather than a pass or fail.

**The other purpose is to demonstrate the hardware survives and works.** That is thermal vacuum and thermal cycling, it is run at the extremes, and its output is a verdict.

A programme that runs only the second has hardware that passed and a model nobody trusts. A programme that runs only the first has a trusted model and no evidence the hardware works.

---

## What each test proves

| Test | Environment | Proves |
|---|---|---|
| Thermal balance | Vacuum, steady, several cases | The model. Correlates contact conductances and insulation performance |
| Thermal vacuum | Vacuum, hot and cold extremes | The hardware works at its limits, and outgassing is acceptable |
| Thermal cycling | Ambient pressure usually, many cycles | Workmanship. Finds solder joints, wire bonds and CTE mismatch failures |
| Thermal shock | Rapid transition | Survival of a rate rather than a level |
| Burn in | Elevated, continuous | Infant mortality screening |

**Thermal cycling finds workmanship defects and thermal vacuum finds design defects**, and they are not substitutes for each other. Cycling at ambient pressure is cheap and can be run for many cycles; vacuum is expensive and is run for few.

---

## Thermal balance

The test that makes the model real.

The article is put in a vacuum chamber with a cold shroud, brought to steady state under a known set of boundary conditions, and every sensor is recorded. Several cases are run: hot, cold, and usually one intermediate, so the correlation has more than one point to fit.

**Steady state is the point.** A transient correlation has too many free parameters and too little information; a steady state one isolates the resistances. The uncertain parameters are the contact conductances and the effective insulation conductivity, and those are what the correlation adjusts.

**The usual acceptance is 3 to 5 K agreement at every sensor.** The usual reason for missing it is a contact interface that is not what the drawing said: a joint assembled without the specified interface filler, a blanket compressed under a strap, a strut that was supposed to be G10 and is not.

Once correlated, the model is used to predict the flight cases, including the ones the chamber cannot produce. **That prediction is the deliverable. The test itself proves nothing about flight.**

---

## Thermal vacuum and thermal cycling

Thermal vacuum runs the article between its hot and cold limits in vacuum, with functional testing at each extreme and usually during the transitions.

Vacuum matters for three reasons and only one of them is thermal. It removes convection, so the article is thermally in the right environment. It allows outgassing, which is a contamination problem. And it removes the possibility of corona and arcing in high voltage hardware, which is not thermal at all but is tested here because this is where the vacuum is.

**Functional testing during the transition is where intermittent failures appear.** A connector that opens at a particular temperature will not be caught by testing at two static extremes.

Thermal cycling is run for cycle count rather than for level. The failure mechanisms it targets are fatigue driven: solder joint cracking, wire bond lift, delamination, and anything driven by a coefficient of thermal expansion mismatch. **The damage accumulates per cycle**, so eight cycles and eighty cycles are different tests.

---

## Qualification and acceptance

The standard relationship, consistent with the rest of the repository:

| | Temperature range | Cycles | Dwell |
|---|---|---|---|
| Acceptance | Predicted extremes plus 5 K | 4 to 8 | 4 hours at each extreme |
| Qualification | Acceptance plus 10 K | 8 to 25 | 4 hours at each extreme |
| Protoflight | Qualification levels, acceptance duration | 4 to 8 | 4 hours at each extreme |

**The margins are on temperature, and they exist because the prediction has uncertainty.** A 5 K acceptance margin is roughly the correlation accuracy of a good model, which is not a coincidence.

**The dwell is for the article to reach steady state, not for the chamber.** A heavy article with good insulation can take far longer than four hours, and a dwell timed from when the shroud reached temperature rather than when the article did is not a dwell.

---

## Instrumentation

Thermocouples are cheap, robust and imprecise. Platinum resistance thermometers are precise and fragile. Thermistors sit between them. The choice follows the requirement rather than the habit.

| Sensor | Typical accuracy | Note |
|---|---|---|
| Type T thermocouple | 0.5 to 1.0 K | Good to 20 K, the cryogenic default |
| Type K thermocouple | 1.1 to 2.2 K | Wide range, less accurate |
| PRT, 4 wire | 0.03 to 0.1 K | The reference choice, fragile leads |
| Thermistor | 0.1 to 0.2 K | Narrow range, high sensitivity |

**A sensor measures its own temperature, not the temperature of what it is attached to.** A thermocouple bonded to a surface in vacuum with a lead running to a warm feedthrough conducts along that lead, and the error is in the direction of the lead. On a cryogenic surface it can be several kelvin.

**Sensor placement is a modelling decision.** A sensor placed where the model has a node produces a correlation. A sensor placed for convenience produces a number that has to be interpolated, and the interpolation carries its own error into the correlation.

---

## The tests that catch soakback

A soakback failure is invisible to a test that stops when the heating stops, in exactly the way it is invisible to an analysis that does the same.

Three requirements follow.

**The test has to run past the event.** For the worked example, the heating lasts 140 seconds and the avionics peak at 950 seconds. A test terminated at 300 seconds records a passing temperature on hardware that fails.

**The sensors have to be on the deep nodes.** The TPS backface peaks at the end of the pulse and tells you nothing about soakback. The avionics peak seven times later and are the only place the failure appears.

**The transition to vacuum has to be represented.** Convective cooling on the pad that disappears at liftoff is a soakback initiator, and a test conducted entirely in air or entirely in vacuum misses it.

**The general rule: run the test until every sensor has turned over**, which is the same rule the analysis follows and for the same reason.

---

## Ground test artefacts

Some things behave differently on the bench and the difference is not the hardware.

**Contact conductance is roughly four times higher in air** than in vacuum on a bare bolted joint, because trapped air conducts across the gap. A thermal test in air measures a joint that does not exist in flight.

**Heat pipes are gravity sensitive to a degree that catches people.** A one metre grooved ammonia pipe transports 115 W level, 253 W at two degrees favourable, and nothing at two degrees adverse. **A pipe tested favourably was never tested**, and a pipe tested adversely by an unmeasured amount can fail for a reason that does not exist in orbit. See [HeatPipesAndTwoPhase](HeatPipesAndTwoPhase.md).

**Natural convection exists on the bench and does not exist in orbit.** Any test not in vacuum has a heat transfer path that will not be present, and it is usually in the helpful direction.

**Chamber shroud temperature is not sink temperature.** The shroud has a finite emissivity and the article sees the shroud plus whatever else is in the chamber, including the fixture.

**The fixture is a thermal path.** A test article bolted to a support that leads out of the chamber is conducting through it, and the flight article is not.

---

## Design rules of thumb

- **Run thermal balance before thermal vacuum.** Correlate the model, then use it.
- **Correlate against steady state, not transient.** Fewer free parameters, more information.
- **Adjust the uncertain parameters only.** Contact conductance and insulation performance, not conductivity.
- **Run the test past the event**, until every sensor has turned over.
- **Instrument the deep nodes**, where soakback appears, not just the surface.
- **Put sensors where the model has nodes.**
- **Control heat pipe tilt to a fraction of the dead angle**, and state the dead angle in the procedure.
- **Time the dwell from when the article reaches temperature**, not the shroud.
- **Account for the fixture**, which is a conduction path the flight article does not have.

---

## Failure modes

**Test terminated when the heating stops.** Misses the soakback peak entirely, in the same way and for the same reason the analysis does.

**Sensors only on the surface.** The surface peaks first and is not where the failure is.

**Test conducted in air.** Contact conductance four times too high, and a convective path that does not exist in flight.

**Heat pipe tested favourably.** Demonstrates a capability the pipe will not have.

**Dwell timed from the shroud.** The article never reached the temperature it was supposed to dwell at.

**Sensor lead conduction ignored.** The measurement is biased toward the lead's environment.

**Cycling count reduced to save schedule.** The mechanism it targets is fatigue, and fatigue is counted in cycles.

**Model correlated by adjusting whatever fits.** Produces a model that matches one test and predicts nothing.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Thermal balance correlation acceptance | 3 to 5 K at every sensor |
| Acceptance temperature margin | Predicted extremes plus 5 K |
| Qualification margin over acceptance | 10 K |
| Typical acceptance cycles | 4 to 8 |
| Typical qualification cycles | 8 to 25 |
| Dwell at each extreme | 4 hours, from when the article stabilises |
| Contact conductance, bare bolted, in air | 2000 W/m^2 K |
| Contact conductance, bare bolted, in vacuum | 500 W/m^2 K |
| Heat pipe, level | 115.0 W |
| Heat pipe, 2 degrees favourable | 253.5 W |
| Heat pipe, 2 degrees adverse | 0 W |
| Worked example event duration | 140 s |
| Worked example deepest peak | 950 s |

**A test run to 300 seconds on the worked example hardware records 307 K and passes. The hardware reaches 375 K against a 323 K limit.**

---

## Standards

| Standard | What it gives you |
|---|---|
| MIL-STD-1540 | Test requirements for launch and space vehicles. The parent document |
| ECSS-E-ST-10-03C | Testing, including thermal vacuum and thermal cycling |
| NASA-STD-7002 | Payload test requirements |
| GSFC-STD-7000 | The GEVS, general environmental verification standard |
| ASTM E491 | Solar simulation for thermal balance testing |
| NASA-STD-6016 | Materials and processes, which covers outgassing acceptance |
| ASTM E595 | Total mass loss and collected volatile condensable materials |

---

## Tool interface

The model side of a correlation is the [ThermalNetwork](ThermalModelling.md) class. The test itself is not modelled, but the two comparisons a correlation needs are:

```python
from ThermalNetwork import ThermalNetwork

network = ThermalNetwork()
network.setInputs({'timeStep': 10.0, 'endTime': 20000.0})
network.addNodeFromMass('article', mass = 30.0, specificHeat = 900.0,
                        temperature = 293.15, heatLoad = 40.0)
network.addNode('shroud', temperature = 173.15, boundary = True)
network.addRadiation('article', 'shroud', emissivity = 0.85, area = 1.2)

steady = network.solveSteadyState()
print(steady['temperatures']['article'])

print(network.resistanceSensitivity()['findings'])
```

The sensitivity report tells the correlation which parameters are worth adjusting, which is the same question in both directions.

---

## References

- Gilmore, *Spacecraft Thermal Control Handbook*, volume I, chapter 18
- MIL-STD-1540, *Test requirements for launch, upper stage and space vehicles*
- GSFC-STD-7000, *General environmental verification standard*
- ECSS-E-ST-10-03C, *Testing*
- Welch, *Thermal balance testing and model correlation*
