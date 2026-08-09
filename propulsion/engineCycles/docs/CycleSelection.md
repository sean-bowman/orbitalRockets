[Home](../README.md) > Cycle Selection

# Cycle Selection

## Contents

- [Overview](#overview)
- [One question decides everything](#one-question-decides-everything)
- [The cycles](#the-cycles)
- [Most candidates are eliminated, not chosen](#most-candidates-are-eliminated-not-chosen)
- [What the choice sets downstream](#what-the-choice-sets-downstream)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Cycle selection is the first decision in engine design and it constrains everything after it. It is usually presented as a menu of options with trade-offs, which makes it look like a preference.

It is not. **Most of the candidates are eliminated by arithmetic**, and the remaining choice is narrow.

---

## One question decides everything

**Where does the turbine exhaust go?**

| Answer | Consequence for impulse | Consequence for the pump |
|---|---|---|
| Overboard | Loses one to three per cent | Only has to reach the chamber |
| To the main injector | Loses nothing | Has to reach above the turbine inlet |

That is the whole trade, and every other difference between the cycles is downstream of it.

The mechanism is the turbine pressure ratio. An open cycle exhausts to ambient and takes a ratio of twenty. A closed cycle hands its exhaust to the main injector at above chamber pressure, so it gets a ratio near one and a half. **The same gas at the same temperature delivers about six times less work on a closed cycle**, which is why a staged combustion preburner passes most of one propellant while a gas generator passes three per cent of the total.

---

## The cycles

| Cycle | Closed | Turbine `PR` | Pump discharge | Character |
|---|---|---|---|---|
| Pressure fed | Yes | none | 1.40 x `Pc` at the tank | No pumps. The tank is the pump |
| Gas generator | No | 20 | 1.40 x `Pc` | The open cycle workhorse |
| Staged combustion | Yes | 1.5 | 2.20 x `Pc` | Everything through the chamber |
| Full flow staged combustion | Yes | 1.5 | 2.20 x `Pc` | Two preburners, no interpropellant seal |
| Expander | Yes | 1.6 | 2.12 x `Pc` | Turbine runs on jacket heat |
| Expander bleed | No | 15 | 1.30 x `Pc` | Jacket heat, and the flow is dumped |

The discharge ratios are for a 10 MPa chamber and they are the honest measure of how hard a cycle is on its turbomachinery.

**The ratio of about two for staged combustion is checked against hardware.** RS-25 runs a 20.64 MPa chamber with a fuel pump discharging at roughly 41 MPa, a real ratio of **1.99**. The pressure ladder in this library predicts 45.4 MPa, 11 per cent high and conservative.

---

## Most candidates are eliminated, not chosen

For the [worked example](../codeInterface.py) engine, 100 kN LOX/RP-1 at 10 MPa:

| Cycle | Verdict | Decided by |
|---|---|---|
| Pressure fed | **Eliminated** | Tank mass: 2219 kg of pressure vessel |
| Expander | **Eliminated** | Heat balance: ceiling near 4 MPa against a 10 MPa chamber |
| Staged combustion | Admitted | Costs pump discharge, 1.29 MW of pump power |
| Gas generator | Admitted | Costs impulse, 2.5 per cent |

**Two of the four were decided before any performance number was compared.**

The pressure fed elimination needs no subtlety: a pressure fed tank holds what the pump would have delivered, so it is a pressure vessel rather than a tank, and it comes out an order of magnitude heavier.

The expander elimination is the interesting one and it has its own document. Its turbine runs on heat the chamber wall gave up, that heat is nearly independent of chamber pressure while pump power rises with it, and there is a ceiling. See [ExpanderCycle](ExpanderCycle.md).

**Only the last two are a trade**, and the choice is between paying in pump discharge pressure and paying in impulse.

---

## What the choice sets downstream

The cycle is chosen first and it decides things that do not look like cycle decisions.

**The turbopump shaft speed, by a factor of two.** The [turbomachinery](../../turbomachinery/README.md) worked example finds an optimum of 55 000 rpm on an open cycle and 27 000 on a closed one, with nothing about the pumps changing. On an open cycle the turbine flow is thrown away so turbine efficiency is worth real propellant; on a closed cycle it is free and tank mass wins.

**The pump discharge pressure, and therefore the pump.** A factor of one and a half between the families, which is the difference between a single stage pump and a multi-stage one.

**Whether there is an interpropellant seal problem.** Full flow staged combustion has two preburners and each turbopump sees only one propellant, which removes the problem rather than managing it. See [SealsAndInterpropellantSeals](../../turbomachinery/docs/SealsAndInterpropellantSeals.md).

**The start sequence.** A closed cycle has no independent power source to bootstrap from, which makes starting it substantially harder. See [ignitionAndStart](../../ignitionAndStart/README.md).

---

## Design rules of thumb

- **Ask where the turbine exhaust goes first.** Everything else follows.
- **Eliminate before comparing.** Most candidates fail a constraint and never reach the trade.
- **Check the expander heat balance before considering it.** It is a hard ceiling and it is low.
- **Do not consider pressure fed above a few tonnes of propellant.**
- **Expect a closed cycle pump to run at twice chamber pressure**, and size the turbomachinery for it.
- **Choose the cycle before the shaft speed.** It moves the optimum by a factor of two.

---

## Failure modes

**Cycle treated as a preference.** Most of the candidates are eliminated by arithmetic and comparing them on impulse alone misses that.

**An expander considered without a heat balance.** It is the only cycle whose closure is a real question.

**Pump sized before the cycle.** The discharge pressure differs by a factor of one and a half.

**Shaft speed chosen before the cycle.** The optimum differs by a factor of two.

**A published open cycle impulse compared against a thrust chamber model.** The dump penalty is in the published figure and not in the model. See [GasGeneratorCycle](GasGeneratorCycle.md).

**Pressure fed proposed for a booster.** The tank is a pressure vessel and it is an order heavier.

---

## Worked numbers

The [worked example](../codeInterface.py) engine at 10 MPa.

| Cycle | Discharge [MPa] | Ratio | Delivered `Isp` [s] | Penalty | Drive flow |
|---|---|---|---|---|---|
| Pressure fed | 14.0 | 1.40 | 298.6 | 0 % | none |
| Gas generator | 14.0 | 1.40 | 291.1 | 2.52 % | 3.0 % |
| Staged combustion | 22.0 | 2.20 | 298.6 | 0 % | 15.8 % |
| Expander | 21.2 | 2.12 | 298.6 | 0 % | 27.5 % |

RS-25 hardware check:

| Quantity | Published | Library | Error |
|---|---|---|---|
| Pump discharge at 20.64 MPa chamber | 41 MPa | 45.4 MPa | +11 % |
| Discharge ratio | 1.99 | 2.20 | +0.21 |

---

## Standards

| Standard | What it gives you |
|---|---|
| **NASA SP-125** | **Design of Liquid Propellant Rocket Engines.** The cycle chapters |
| NASA SP-8081 | Liquid propellant gas generators |
| NASA SP-8107 | Turbopump systems, which the cycle sizes |
| ECSS-E-ST-35C | Propulsion general requirements |

---

## Tool interface

```python
from EngineCycle import EngineCycle

cycle = EngineCycle()
cycle.setInputs({'cycle':               'staged combustion',
                 'chamberPressure':     10.0e6,
                 'idealImpulse':        298.6,
                 'turbineFlowFraction': 0.035})

ladder = cycle.calculatePressureLadder()
print(ladder['dischargeRatio'], ladder['turbineInlet'])

print(cycle.calculateImpulseDelivered()['penalty'])

for name, entry in cycle.compareCycles()['cycles'].items():
    print(f'{name:30s} {entry["dischargeRatio"]:.2f}')
```

---

## References

- NASA SP-125, *Design of Liquid Propellant Rocket Engines*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- Sutton, *History of Liquid Propellant Rocket Engines*
- Sutton and Biblarz, *Rocket Propulsion Elements*, chapter 6
