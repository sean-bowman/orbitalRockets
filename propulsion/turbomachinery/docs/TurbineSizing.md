[Home](../README.md) > Turbine Sizing

# Turbine Sizing

## Contents

- [Overview](#overview)
- [Spouting velocity and blade speed ratio](#spouting-velocity-and-blade-speed-ratio)
- [The classical impulse optimum](#the-classical-impulse-optimum)
- [Why a rocket turbine never reaches it](#why-a-rocket-turbine-never-reaches-it)
- [Partial admission](#partial-admission)
- [The driving flow, and what it costs](#the-driving-flow-and-what-it-costs)
- [Temperature and blade speed limits](#temperature-and-blade-speed-limits)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A rocket turbine is a turbine that does not get to choose its own shaft speed. The pump sets the speed, the turbine is bolted to the same shaft, and it makes do.

That single fact explains nearly everything that looks wrong about rocket turbines beside industrial practice: they run at blade speed ratios well below optimum, their efficiencies are in the forties and sixties rather than the nineties, and they are almost always partial admission impulse machines.

**None of that is poor design.** It is what a turbine looks like when the shaft speed is somebody else's decision, and the compromise is usually correct because the pump is the harder machine.

---

## Spouting velocity and blade speed ratio

The isentropic spouting velocity is the speed the gas would reach expanding through the full pressure ratio with no work extracted:

```
C0 = sqrt( 2 cp T_in (1 - PR^(-(gamma-1)/gamma)) )
```

It is set entirely by the gas and the pressure ratio, and it is the yardstick the blade speed is measured against.

```
U / C0        the blade speed ratio, and the parameter that decides efficiency
```

Everything about turbine performance is a function of that ratio.

---

## The classical impulse optimum

For a single stage impulse turbine with equiangular blading and a nozzle angle `alpha` measured from the plane of rotation, the utilisation is

```
eta_u = 4 (U/C0) (cos alpha - U/C0)
```

which peaks at

```
(U/C0)_opt = cos(alpha) / 2        with a peak of      cos^2(alpha)
```

At a 20 degree nozzle angle that is an **optimum ratio of 0.470 and a peak utilisation of 0.883.**

A shallow nozzle angle puts more of the gas velocity into the direction of blade motion, which is what the blade can extract, so shallow is efficient and hard to manufacture.

**Above `U/C0 = cos(alpha)` the turbine extracts no work at all**, because the blade is moving as fast as the useful component of the gas. That is a geometry error rather than an inefficiency, and the library raises rather than dividing by zero.

---

## Why a rocket turbine never reaches it

The blade speed is `omega D / 2`. The shaft speed belongs to the pump, and the mean diameter is bounded by the machine the turbine has to fit inside.

For the worked example turbopump:

| Quantity | Value |
|---|---|
| Spouting velocity | 1501 m/s |
| Blade speed | 236 m/s |
| Blade speed ratio | **0.157** |
| Optimum | 0.470 |
| Utilisation | 0.491 against a possible 0.883 |
| Efficiency after mechanical losses | **41.8 %** |

**A third of the optimum ratio, and roughly half the achievable efficiency.**

The single lever available is the mean diameter, and it improves things:

| Mean diameter [mm] | `U/C0` | Efficiency |
|---|---|---|
| 150 | 0.157 | 41.8 % |
| 250 | 0.262 | 60.3 % |
| 350 | 0.366 | 71.4 % |

A larger turbine is more efficient and it is heavier, it is harder to fit, and its blade tip speed rises toward the stress limit. That trade is the turbine designer's whole job once the shaft speed is fixed.

**Velocity compounding is the other answer.** A two row velocity compounded stage has an optimum blade speed ratio of 0.25 rather than 0.50, so it suits a slow shaft and a high pressure ratio, at the cost of a second row of blades and more loss.

---

## Partial admission

Rocket turbines frequently admit gas over only part of the annulus, because the flow is small relative to the blade height a full annulus would need.

The alternative is a very short blade, where tip clearance becomes a large fraction of the passage and the loss is worse than the scavenging loss partial admission carries.

**It is a choice between two losses**, and on a small turbopump partial admission usually wins. It brings its own problems: the blades are loaded and unloaded once per revolution, which is a fatigue driver, and the flow is unsteady in a way full admission is not.

---

## The driving flow, and what it costs

```
mdot = P / (eta cp T_in (1 - PR^(-(gamma-1)/gamma)))
```

For the worked example this is **1.33 kg/s, which is 3.6 per cent of the engine's total propellant flow.**

What that costs depends entirely on the cycle, and the difference is the whole distinction between a gas generator and a staged combustion engine.

**On an open cycle** the flow is dumped overboard through a low expansion nozzle at a fraction of main chamber impulse. It is a direct specific impulse loss, and it is the reason the F-1 disagreed with the propulsion hub library by eight per cent when that library was validated: the library models a thrust chamber and the published engine impulse includes the dump.

**On a closed cycle** it goes to the main chamber and costs nothing.

That difference propagates all the way back to the shaft speed. The [worked example](../codeInterface.py) finds an optimum shaft speed of 55 000 rpm on an open cycle and 27 000 rpm on a closed one, **a factor of 2.04, with nothing about the pumps changing.** On an open cycle turbine efficiency is worth real propellant, so it is worth spinning fast to get it; on a closed cycle it is free and the tank mass wins.

---

## Temperature and blade speed limits

| Blade material | Inlet limit [K] |
|---|---|
| Uncooled superalloy | 1150 |
| Cooled superalloy | 1500 |
| Expander cycle | 600 |

**A rocket turbine runs uncooled**, because the run time is short and the limit is a creep and rupture one over that run time rather than a melting point. Cooling costs flow and complexity and is rarely worth it for a few hundred seconds.

The expander cycle entry is not a material limit at all: it is the temperature the coolant reached in the chamber jacket, and it is what caps expander cycle chamber pressure.

The blade tip speed limit is **450 m/s**, tighter than the pump impeller limit despite the smaller loads, because the blade is a rotating mass on a hot disc.

**On the worked example that limit is the binding constraint.** At the open cycle optimum the blade reaches 432 m/s against the 450 limit, while both pump impellers sit under 170 m/s against limits of 450 and 550. On a moderate chamber pressure engine the pump is not the hard part of a turbopump; the turbine is.

---

## Design rules of thumb

- **Accept the shaft speed.** It is the pump's, and arguing loses.
- **Use the mean diameter as the lever**, and trade it against mass and blade stress.
- **Consider velocity compounding for a slow shaft** and a high pressure ratio.
- **Expect partial admission on a small turbopump**, and treat the blade fatigue that comes with it as real.
- **Run uncooled.** The run time is short and cooling costs more than it buys.
- **Check the blade tip speed before the pump impeller.** It is usually the binding one.
- **Ask what the cycle is before optimising anything.** It decides whether turbine efficiency is worth propellant.

---

## Failure modes

**Turbine efficiency optimised without asking the cycle.** On a closed cycle the effort buys nothing.

**Blade speed ratio above `cos(alpha)`.** No work is extracted and the flow calculation divides by zero.

**Full admission assumed on a small turbine.** Blade height becomes so small that tip clearance dominates.

**Partial admission fitted and the blade fatigue ignored.** Once per revolution loading is a real driver.

**Cooling proposed for a rocket turbine.** Costs flow and complexity for a run time that does not need it.

**The inlet temperature limit treated as a melting point.** It is a creep and rupture limit over the run time.

**Pump impeller stress checked and blade tip speed not.** The blade is tighter.

---

## Worked numbers

The worked example turbine: 0.624 MW, 1000 K inlet, pressure ratio 20, 30 000 rpm, 150 mm mean diameter.

| Quantity | Value |
|---|---|
| Spouting velocity | 1501 m/s |
| Blade speed | 236 m/s |
| Blade speed ratio | 0.157 against an optimum of 0.470 |
| Utilisation | 0.491 against a peak of 0.883 |
| Efficiency | 41.8 % |
| Driving flow | 1.33 kg/s, 3.6 % of total propellant |
| Temperature drop | 451 K, from 1000 K to 549 K |
| Blade speed at the open cycle optimum | 432 m/s against a 450 limit |

---

## Standards

| Standard | What it gives you |
|---|---|
| **NASA SP-8110** | **Liquid rocket engine turbines.** The design monograph |
| NASA SP-8107 | Turbopump systems |
| NASA SP-8081 | Liquid propellant gas generators, which feed the turbine |
| NASA-STD-5012 | Strength and life assessment, for the blade fatigue |

---

## Tool interface

```python
from Turbine import Turbine

turbine = Turbine()
turbine.setInputs({'requiredPower':    624000.0,
                   'inletTemperature': 1000.0,
                   'pressureRatio':    20.0,
                   'shaftSpeed':       30000.0,
                   'meanDiameter':     0.15,
                   'stageType':        'impulse'})

efficiency = turbine.calculateEfficiency()
print(efficiency['bladeSpeedRatio'], efficiency['optimumRatio'], efficiency['efficiency'])

print(turbine.sizeFlow()['drivingFlow'])
print(turbine.checkLimits()['tipSpeedOk'])
```

---

## References

- NASA SP-8110, *Liquid rocket engine turbines*
- NASA SP-8107, *Turbopump systems for liquid rocket engines*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- Dixon and Hall, *Fluid Mechanics and Thermodynamics of Turbomachinery*
- Sutton and Biblarz, *Rocket Propulsion Elements*, chapter 10
