[Home](../README.md) > Staged Combustion

# Staged Combustion

## Contents

- [Overview](#overview)
- [The pressure ladder](#the-pressure-ladder)
- [Everything through the turbine](#everything-through-the-turbine)
- [Fuel rich, oxidiser rich, full flow](#fuel-rich-oxidiser-rich-full-flow)
- [What it costs](#what-it-costs)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Staged combustion burns a propellant twice. Most of one propellant and a little of the other are burned in a preburner, expanded through the turbine, and then burned again in the main chamber with the rest.

Nothing is thrown away, so there is no cycle impulse penalty. The price is paid entirely by the turbomachinery, and it is a large price.

---

## The pressure ladder

The structural fact, and everything else follows from it.

**The turbine exhaust has to enter the main injector.** It therefore has to be above chamber pressure plus the injector drop. Working back up:

```
turbine exit    = Pc + injector drop
turbine inlet   = turbine exit x turbine pressure ratio
pump discharge  = turbine inlet + preburner injector + cooling + lines
```

For a 10 MPa chamber that gives a pump discharge of **22.0 MPa, a ratio of 2.20**, against 1.40 for a gas generator.

**A closed cycle pump works against its own turbine, not against the chamber.**

That ratio is checked against hardware. RS-25 runs a 20.64 MPa chamber with a high pressure fuel turbopump discharging at roughly 41 MPa, a real ratio of **1.99**. The library predicts 45.4 MPa, 11 per cent high and conservative, which is the right direction for a pressure ladder: it oversizes the pump rather than leaving it short.

---

## Everything through the turbine

The turbine pressure ratio is what changes, and it changes by a lot.

| | Gas generator | Staged combustion |
|---|---|---|
| Turbine pressure ratio | 20 | 1.5 |
| Expansion term | 0.451 | 0.078 |
| Specific work | 558 kJ/kg | 107 kJ/kg |
| Driving flow | 3.0 % | **15.8 %** |

**The same power needs five times the flow**, because the turbine has six times less to work with per kilogram.

At 15.8 per cent this is no longer a bleed. It is a preburner, and the library flags the distinction rather than reporting a large fraction without comment: above about ten per cent of total flow the cycle is staged combustion whether it is called that or not.

On a real staged combustion engine the fraction is higher still, because the preburner passes essentially all of one propellant. The library's figure is low because it uses a single set of driving gas properties rather than modelling the preburner mixture, which is a stated simplification.

---

## Fuel rich, oxidiser rich, full flow

Three arrangements, and the choice is a materials problem rather than a thermodynamic one.

**Fuel rich** is the hydrogen answer. The preburner runs fuel rich, the turbine gas is mostly hydrogen, and it is chemically benign. RS-25 does this. It does not transfer well to a hydrocarbon, because a fuel rich hydrocarbon preburner deposits carbon on the turbine.

**Oxidiser rich** is the kerosene answer and it is a materials achievement. The preburner runs oxidiser rich, so the turbine gas is hot oxygen, and every surface it touches has to survive that. The Soviet engines that pioneered it did so on the back of a coatings programme, and it is the single hardest thing about the cycle.

**Full flow** runs two preburners, one fuel rich and one oxidiser rich, each driving its own turbopump. Each turbopump sees only one propellant, which **removes the interpropellant seal problem rather than managing it**. See [SealsAndInterpropellantSeals](../../turbomachinery/docs/SealsAndInterpropellantSeals.md). It costs two preburners and two turbopumps.

---

## What it costs

**No impulse penalty.** That is the whole point.

**A pump at twice chamber pressure**, which on a large engine is a multi-stage machine rather than a single stage one. See [PumpSizing](../../turbomachinery/docs/PumpSizing.md), where the stage count goes as the square of the tip speed overrun.

**A preburner**, which is a full combustion device with its own development programme, its own stability problem, and in the oxidiser rich case its own materials programme.

**A start sequence with no independent power source.** The turbine gas comes from a preburner fed by pumps driven by that turbine. Bootstrapping it is substantially harder than lighting a gas generator, and it is developed by test.

**A slower turbopump.** The [turbomachinery](../../turbomachinery/README.md) worked example finds the optimum shaft speed at 27 000 rpm closed against 55 000 open, because turbine efficiency stops being worth propellant when the flow is not thrown away.

---

## Design rules of thumb

- **Expect the pump at twice chamber pressure** and size the turbomachinery before committing.
- **Choose fuel rich for hydrogen and oxidiser rich for hydrocarbons**, and treat the latter as a materials programme.
- **Consider full flow if the interpropellant seal is the dominant risk.** It removes the problem.
- **Budget the preburner as a combustion device**, not as a component.
- **Develop the start sequence by test.** There is no independent power source to bootstrap from.
- **Do not chase turbine efficiency.** On a closed cycle the flow is not lost, so it buys much less than it does on an open one.

---

## Failure modes

**The pump sized at open cycle discharge pressure.** A factor of one and a half, and it is the difference between one stage and three.

**A fuel rich hydrocarbon preburner.** Carbon on the turbine.

**An oxidiser rich preburner without the coatings programme.** Hot oxygen on an uncoated superalloy is a fire.

**The start sequence designed rather than developed.** There is no independent power source and the transient is not analytically tractable.

**Turbine efficiency optimised as though the flow were lost.** It is not, and the effort is better spent elsewhere.

**The interpropellant seal treated as a component.** On a single shaft closed cycle it is a sequence of seals, drains, purges and vents.

---

## Worked numbers

The [worked example](../codeInterface.py) engine at 10 MPa.

| Quantity | Value |
|---|---|
| Turbine exit | 12.0 MPa |
| Turbine inlet | 18.0 MPa |
| Pump discharge | 22.0 MPa, 2.20 x chamber |
| Turbine pressure ratio | 1.5 |
| Expansion term | 0.078 |
| Specific work | 107 kJ/kg |
| Driving flow | 5.83 kg/s, 15.8 % |
| Cycle impulse penalty | 0 % |

RS-25 hardware check:

| Quantity | Published | Library | Error |
|---|---|---|---|
| Pump discharge at a 20.64 MPa chamber | 41 MPa | 45.4 MPa | +11 % |
| Discharge ratio | 1.99 | 2.20 | +0.21 |

---

## Standards

| Standard | What it gives you |
|---|---|
| NASA SP-125 | Design of liquid propellant rocket engines |
| NASA SP-8081 | Liquid propellant gas generators, which covers preburners |
| NASA SP-8107 | Turbopump systems |
| NASA-STD-6001 | Materials compatibility, which the oxidiser rich case lives on |
| ASTM G93 | Cleaning for oxygen service |

---

## Tool interface

```python
from EngineCycle import EngineCycle

cycle = EngineCycle()
cycle.setInputs({'cycle':           'staged combustion',
                 'chamberPressure': 10.0e6,
                 'idealImpulse':    298.6})

ladder = cycle.calculatePressureLadder()
print(ladder['turbineExit'], ladder['turbineInlet'], ladder['dischargeRatio'])
```

---

## References

- NASA SP-125, *Design of Liquid Propellant Rocket Engines*
- Sutton, *History of Liquid Propellant Rocket Engines*, the Soviet oxidiser rich chapters
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- Sutton and Biblarz, *Rocket Propulsion Elements*, chapter 6
