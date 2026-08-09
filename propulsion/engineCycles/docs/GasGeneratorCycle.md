[Home](../README.md) > Gas Generator Cycle

# Gas Generator Cycle

## Contents

- [Overview](#overview)
- [The arrangement](#the-arrangement)
- [What the dump costs](#what-the-dump-costs)
- [The penalty is invisible to a chamber model](#the-penalty-is-invisible-to-a-chamber-model)
- [Why it persists](#why-it-persists)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A small fraction of the propellant is burned in a separate gas generator at a mixture ratio chosen for turbine inlet temperature rather than for performance, expanded through the turbine, and thrown overboard.

It is the simplest cycle with turbomachinery, it has flown more than any other, and it throws away one to three per cent of the engine's impulse to do it.

---

## The arrangement

```
tank -> pump -> most of the flow -> chamber
              -> a few per cent  -> gas generator -> turbine -> overboard
```

The gas generator runs **fuel rich**, typically at a mixture ratio a quarter of the main chamber's, so the exhaust is around 900 K rather than 3600. That is what lets the turbine blades run uncooled.

The turbine exhausts to ambient, which is the structural advantage: **it can take a pressure ratio of twenty**, so a kilogram of driving gas delivers 558 kJ against 107 for a staged combustion turbine. Three per cent of the flow is enough.

The pump only has to reach the chamber, so its discharge is about **1.40 times chamber pressure** against 2.20 for staged combustion. That is a single stage pump instead of a multi-stage one.

---

## What the dump costs

The turbine exhaust is cool, fuel rich and expanded through a short nozzle that exists to avoid a side force rather than to produce thrust. It delivers roughly **thirty per cent** of main chamber specific impulse.

```
Isp_engine = Isp_chamber (1 - f) + Isp_dumped f
```

For the [worked example](../codeInterface.py) engine at a 3.5 per cent driving flow, an ideal 298.6 s becomes **291.1 s, a 2.5 per cent loss.**

That is the entire cost of the cycle, and it is worth comparing against what it buys: a pump at 1.40 rather than 2.20 times chamber pressure, no preburner, and a start sequence with an independent power source.

---

## The penalty is invisible to a chamber model

The consequence that matters when reading published data.

**A thrust chamber and nozzle model does not contain the dump.** It computes what the chamber and nozzle deliver. A published open cycle engine impulse is a whole-engine figure that includes the overboard flow.

This is not hypothetical: it showed up when the [propulsion hub](../../docs/PerformanceFundamentals.md) library was validated. Against RS-25, which is closed cycle, the library overpredicts vacuum impulse by **1.7 per cent**. Against F-1, which is a gas generator, it overpredicts by **8.1 per cent**.

The cycle penalty computed here accounts for a meaningful part of that gap and not all of it. **The rest is chamber efficiency, which is a different thing**, and a test in this sub-domain asserts the penalty stays below the total disagreement rather than explaining it away entirely.

The practical rule: **an open cycle engine's published impulse cannot be compared directly against a chamber model** without adding the cycle back in.

---

## Why it persists

Despite being the only cycle with an intrinsic performance loss, it has flown more than any other, and the reasons are all about difficulty rather than performance.

**The pump is easy.** 1.40 rather than 2.20 times chamber pressure is frequently a single stage instead of three.

**There is no preburner.** A staged combustion preburner is a full combustion device with its own development programme, and an oxidiser rich one is a materials problem on top.

**Starting is straightforward.** The gas generator is an independent power source that can be lit before the main chamber, which makes bootstrapping tractable. A closed cycle has no such thing. See [ignitionAndStart](../../ignitionAndStart/README.md).

**There is no interpropellant seal problem** on a single shaft, because the turbine gas is already mixed.

Two to three per cent of impulse buys all of that, and on a first stage, where impulse matters least, it is frequently the right trade.

---

## Design rules of thumb

- **Budget one to three per cent of impulse** and check it against what the pump saves.
- **Run the gas generator fuel rich** at whatever mixture ratio gives an uncooled turbine inlet temperature.
- **Never compare a published open cycle impulse against a chamber model** without adding the cycle penalty.
- **Expect the driving flow to be a few per cent.** Above six, something upstream is wrong.
- **Use it on a first stage** where impulse is worth least and simplicity is worth most.
- **Expand the turbine exhaust just enough to avoid a side force**, and do not try to recover thrust from it.

---

## Failure modes

**The dump penalty omitted from a performance prediction.** Two to three per cent, and it looks like a chamber efficiency problem.

**A published open cycle impulse compared against a chamber model.** Eight per cent on the F-1, and the conclusion is that the model is broken.

**The gas generator run too hot.** The turbine is uncooled and the limit is creep and rupture over the run time.

**The driving flow allowed to grow.** Above six per cent an open cycle is throwing away more than the cycle is worth.

**The turbine exhaust nozzle sized for thrust.** It is there to avoid a side force and the impulse is not recoverable.

---

## Worked numbers

The [worked example](../codeInterface.py) engine at 10 MPa.

| Quantity | Value |
|---|---|
| Pump discharge | 14.0 MPa, 1.40 x chamber |
| Turbine pressure ratio | 20 |
| Expansion term | 0.451 |
| Specific work | 558 kJ/kg |
| Driving flow | 1.12 kg/s, 3.0 % of the engine |
| Ideal impulse | 298.6 s |
| Delivered impulse | 291.1 s |
| Cycle penalty | 2.52 % |
| Turbine inlet | 900 K |

For comparison, the hub library validation:

| Engine | Cycle | Library error against published |
|---|---|---|
| RS-25 | Staged combustion | +1.7 % |
| F-1 | Gas generator | +8.1 % |

---

## Standards

| Standard | What it gives you |
|---|---|
| **NASA SP-8081** | **Liquid propellant gas generators.** The design monograph |
| NASA SP-125 | Design of liquid propellant rocket engines |
| NASA SP-8110 | Liquid rocket engine turbines |
| CPIA 246 | Performance prediction, which is where the cycle penalty has to be declared |

---

## Tool interface

```python
from EngineCycle import EngineCycle

cycle = EngineCycle()
cycle.setInputs({'cycle':               'gas generator',
                 'chamberPressure':     10.0e6,
                 'idealImpulse':        298.6,
                 'turbineFlowFraction': 0.035})

impulse = cycle.calculateImpulseDelivered()
print(impulse['deliveredImpulse'], impulse['penalty'])
```

---

## References

- NASA SP-8081, *Liquid propellant gas generators*
- NASA SP-125, *Design of Liquid Propellant Rocket Engines*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- Sutton, *History of Liquid Propellant Rocket Engines*
