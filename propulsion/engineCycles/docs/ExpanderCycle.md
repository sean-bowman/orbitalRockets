[Home](../README.md) > Expander Cycle

# Expander Cycle

## Contents

- [Overview](#overview)
- [How it works](#how-it-works)
- [The ceiling](#the-ceiling)
- [Why the jacket heat barely moves](#why-the-jacket-heat-barely-moves)
- [The scaling argument](#the-scaling-argument)
- [Expander bleed](#expander-bleed)
- [Why it is a hydrogen cycle](#why-it-is-a-hydrogen-cycle)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The expander is the only closed cycle with no combustion outside the main chamber. The fuel goes through the cooling jacket, picks up heat, drives the turbine on that heat alone, and is then burned in the chamber. Nothing is thrown away and nothing is burned twice.

It is the most elegant cycle available and it has a hard ceiling that rules it out of most applications.

---

## How it works

```
tank -> pump -> cooling jacket -> turbine -> injector -> chamber
```

The turbine's energy source is the enthalpy the coolant gained in the jacket. There is no preburner, no gas generator, and no separate combustion of any kind.

That gives it three real advantages. **No preburner** means no second combustion device to develop and no oxidiser rich turbine gas. **A cool turbine**, around 500 K rather than 1000, means the blades are not a life-limited item. And **closed** means no impulse loss.

It also means the cycle has **no throttle on its own power source.** Every other cycle closes by burning more propellant. An expander closes if the chamber wall gave up enough heat and does not close if it did not, and nothing inside the cycle changes that.

---

## The ceiling

For the [worked example](../codeInterface.py) engine held at 100 kN and swept in chamber pressure:

| `Pc` [MPa] | Throat [mm] | Jacket heat [MW] | Pump power [MW] | Available [MW] | Margin | Closes |
|---|---|---|---|---|---|---|
| 2.0 | 202.6 | 9.55 | 0.182 | 0.471 | 2.58 | Yes |
| 3.0 | 165.4 | 9.17 | 0.282 | 0.452 | 1.60 | Yes |
| 4.0 | 143.3 | 8.91 | 0.392 | 0.439 | 1.12 | Yes |
| **4.5** | 135.1 | 8.80 | 0.450 | 0.434 | 0.96 | **No** |
| 5.0 | 128.1 | 8.71 | 0.511 | 0.430 | 0.84 | No |
| 10.0 | 90.6 | 8.13 | 1.225 | 0.401 | 0.33 | No |

**The ceiling is between 4.0 and 4.5 MPa.**

**RL10, the best known expander cycle engine, runs at 4.4 MPa.** That agreement is closer than the model deserves and it should be read as a sanity bracket rather than a validation: the propellant here is LOX/RP-1 and RL10 runs on hydrogen. What it does establish is that the ceiling is real and that it sits where expander cycle engines actually sit.

It is also why expander cycles are upper stage engines. An upper stage tolerates a modest chamber pressure because it operates in vacuum where the area ratio does the work.

---

## Why the jacket heat barely moves

The counterintuitive half of the ceiling, and the reason it is worth computing rather than assuming.

Across a five-fold increase in chamber pressure the jacket heat falls only from **9.55 to 8.13 MW**, a change of 15 per cent.

Two effects nearly cancel. Raising the chamber pressure at constant thrust **shrinks the engine**: the throat area goes as the inverse of chamber pressure, so every length scales as the inverse square root and the wall area falls. But the heat flux **rises** with chamber pressure, roughly as `Pc^0.8` through Bartz.

Area down, flux up, and the product is nearly flat.

**So the expander's power source is close to constant while its power demand is not.** Pump power rises almost linearly with chamber pressure, from 0.182 to 1.225 MW over the same sweep. The margin collapses from one side only.

---

## The scaling argument

The table can be predicted without running it.

```
heat available   ~  A_wall  x  q      ~  Pc^-1  x  Pc^0.8   =  Pc^-0.2
pump power       ~  Q_vol   x  dP     ~  Pc
margin           ~  Pc^-0.2 / Pc      =  Pc^-1.2
```

The computed sweep gives an exponent of **1.3**, against the 1.2 the argument predicts.

**That exponent is the whole story of the expander cycle.** A cycle whose margin falls faster than the first power of chamber pressure cannot be pushed to high chamber pressure by any amount of development, and the only levers are outside the cycle.

The levers that do exist are worth naming because they are all geometric. **A longer chamber** adds wall area at the cost of mass and residence time. **Channel roughening or turbulators** raise the heat pickup at the cost of pressure drop. **A larger area ratio nozzle with a regenerative extension** adds area. All of them buy a little and none of them change the exponent.

---

## Expander bleed

The escape, and it works by abandoning what made the cycle attractive.

An expander bleed dumps the turbine flow overboard rather than returning it to the chamber. That raises the turbine pressure ratio from 1.6 to about 15, which raises the specific work by a factor of five, so far less flow is needed and the heat balance closes at much higher chamber pressure.

**It costs the impulse penalty an open cycle carries**, and it is no longer a closed cycle. It is a gas generator whose gas generator happens to be the cooling jacket.

That is a real and used solution. It is worth being clear that it solves the problem by removing the property that made an expander worth wanting.

---

## Why it is a hydrogen cycle

Two reasons, and the first is the one usually given.

**Hydrogen has an enormous specific heat**, 14 300 J/kg K against 2100 for RP-1, so the same jacket heat produces far more turbine-usable enthalpy per kilogram of coolant.

**Hydrogen tolerates a high jacket outlet temperature.** It does not coke and it does not decompose, so the coolant can leave hot, and turbine work goes with inlet temperature.

A hydrocarbon expander is possible and it is harder on both counts. The coking limit caps the jacket outlet temperature, which caps the turbine inlet temperature, which caps the specific work. See [RegenerativeCooling](../../combustionDevices/docs/RegenerativeCooling.md), where the same coking limit decides whether a chamber can be cooled at all.

---

## Design rules of thumb

- **Run the heat balance before considering an expander.** It is the only cycle whose closure is a real question.
- **Expect a ceiling near 4 to 5 MPa** for a hydrocarbon and higher for hydrogen.
- **Do not expect development to raise it.** The margin falls as `Pc^-1.2` and that is structural.
- **Use it on an upper stage**, where a modest chamber pressure costs little.
- **Consider expander bleed if the pressure has to be higher**, and accept that it is an open cycle.
- **Prefer hydrogen.** Specific heat and the absence of a coking limit both point the same way.
- **Add wall area if you are close**, and expect it to buy a little.

---

## Failure modes

**An expander proposed at a booster chamber pressure.** The heat balance does not close and no development changes it.

**The heat balance assumed to improve with engine size.** Area and flow both scale together; it is nearly neutral.

**The jacket heat assumed to rise with chamber pressure.** Flux rises and area falls, and the product is flat.

**A hydrocarbon expander sized without the coking limit.** The jacket outlet temperature is capped and so is the turbine work.

**Expander bleed described as a closed cycle.** It dumps its turbine flow and carries the impulse penalty.

**Closure margin treated as a performance reserve.** An expander has no throttle on its power source, so the margin is the entire design reserve.

---

## Worked numbers

The [worked example](../codeInterface.py) engine, 100 kN LOX/RP-1, swept in chamber pressure at constant thrust.

| Quantity | Value |
|---|---|
| Ceiling | Between 4.0 and 4.5 MPa |
| RL10 chamber pressure, for comparison | 4.4 MPa |
| Jacket heat at 2 MPa | 9.55 MW |
| Jacket heat at 10 MPa | 8.13 MW |
| Pump power at 2 MPa | 0.182 MW |
| Pump power at 10 MPa | 1.225 MW |
| Margin at 2 MPa | 2.58 |
| Margin at 10 MPa | 0.33 |
| Scaling exponent, computed | 1.3 |
| Scaling exponent, predicted | 1.2 |
| Driving flow fraction at 10 MPa | 27.5 % |

---

## Standards

| Standard | What it gives you |
|---|---|
| NASA SP-125 | Design of liquid propellant rocket engines |
| NASA SP-8087 | Fluid-cooled combustion chambers, which is the power source |
| NASA SP-8110 | Liquid rocket engine turbines |
| NASA SP-8107 | Turbopump systems |

---

## Tool interface

The closure check needs the jacket heat, which comes from [combustionDevices](../../combustionDevices/README.md) rather than being computed here. That keeps one implementation of Bartz in the repository.

```python
from PowerBalance import PowerBalance

balance = PowerBalance()
balance.setInputs({'cycle':           'expander',
                   'chamberPressure': 4.0e6,
                   'totalFlow':       36.81,
                   'pumpPower':       0.392e6,
                   'availableHeat':   8.91e6})

closure = balance.checkClosure()
print(closure['closes'], closure['margin'])
```

The [worked example](../codeInterface.py) runs the full sweep and reports the ceiling.

---

## References

- NASA SP-125, *Design of Liquid Propellant Rocket Engines*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- Sutton, *History of Liquid Propellant Rocket Engines*, the RL10 chapters
- Sutton and Biblarz, *Rocket Propulsion Elements*, chapter 6
- NASA SP-8087, *Liquid rocket engine fluid-cooled combustion chambers*
