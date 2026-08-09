[Home](../README.md) > Power Balance

# Power Balance

## Contents

- [Overview](#overview)
- [The equation](#the-equation)
- [The expansion term is where cycles diverge](#the-expansion-term-is-where-cycles-diverge)
- [When a bleed stops being a bleed](#when-a-bleed-stops-being-a-bleed)
- [Closure is only a question for one cycle](#closure-is-only-a-question-for-one-cycle)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The power balance is one equation and it is trivial to write. What makes it worth a document is that each side is constrained by something different, and the constraints belong to different sub-domains.

---

## The equation

```
P_turbine = P_pumps
```

The pump side comes from the pressure ladder, which is a cycle decision, and from the flow, which is an engine decision. The turbine side comes from three things:

```
w = eta cp T_in (1 - PR^(-(gamma-1)/gamma))        specific work, per kilogram of driving gas
mdot = P_pumps / w                                  the flow that balance demands
```

The inlet temperature is a materials limit. The efficiency belongs to [turbomachinery](../../turbomachinery/docs/TurbineSizing.md). **The pressure ratio belongs to the cycle, and it is the term that matters.**

---

## The expansion term is where cycles diverge

```
1 - PR^(-(gamma-1)/gamma)
```

At a driving gas gamma of 1.25:

| Cycle | `PR` | Expansion term | Specific work [kJ/kg] |
|---|---|---|---|
| Gas generator | 20.0 | **0.451** | 558 |
| Staged combustion | 1.5 | **0.078** | 107 |
| Expander | 1.6 | 0.090 | 62 |

**A factor of six in the expansion term between the open and closed families**, from nothing but where the exhaust goes.

The expander is lower still on specific work despite a slightly better expansion term, because its inlet temperature is 500 K rather than 1000: the turbine runs on what the coolant picked up, not on what a blade tolerates.

The consequence is the driving flow:

| Cycle | Driving flow | Fraction of engine |
|---|---|---|
| Gas generator | 1.12 kg/s | **3.0 %** |
| Staged combustion | 5.83 kg/s | **15.8 %** |
| Expander | 10.12 kg/s | **27.5 %** |

**That is why a gas generator taps three per cent and a staged combustion preburner passes most of one propellant.** It is the same power through a turbine with six times less to work with.

The expander needing 27.5 per cent is worth noticing against a fuel fraction of 28.1 per cent for LOX/RP-1 at this mixture ratio. **An expander needs essentially all of its fuel through the turbine, which is exactly what an expander does.**

---

## When a bleed stops being a bleed

Above roughly **ten per cent** of total flow, a turbine drive is not a bleed. It is a preburner, the cycle is staged combustion whether it is called that or not, and treating the flow as a small correction stops being defensible.

The class says so rather than reporting a large fraction without comment, because the distinction changes what the engine is:

- A **bleed** is a tap. The main flow is unaffected and the tapped flow is a loss or a return.
- A **preburner** is a stage. Most of a propellant is burned at a mixture ratio chosen for turbine inlet temperature, then burned again in the main chamber.

An open cycle at more than about six per cent is also flagged, because it is throwing away far too much impulse and something upstream needs revisiting.

---

## Closure is only a question for one cycle

**A gas generator or staged combustion cycle closes by burning more propellant.** The driving flow is an output rather than a constraint. The cycle closes until a temperature limit or a pressure limit stops it, and the power balance is an accounting exercise.

**An expander has no such lever.** Its turbine runs on heat the chamber wall gave up, and that heat is fixed by the wall area and the flux. If it is not enough, the cycle does not close and **no adjustment inside the cycle fixes it.**

That is the whole distinction, and it is why `checkClosure` returns trivially for three cycles and is the entire question for the fourth. See [ExpanderCycle](ExpanderCycle.md).

---

## Design rules of thumb

- **Compute the expansion term first.** It is the factor of six between the families.
- **Check the driving flow fraction against ten per cent.** Above it, the cycle is not what it is being called.
- **Expect a closed cycle to need an order more driving flow** for the same power.
- **Do not run a closure check on a non-expander and think it means anything.**
- **Get the turbine efficiency from the turbomachinery sub-domain**, where it is computed from the blade speed ratio rather than assumed.

---

## Failure modes

**The expansion term taken as similar across cycles.** It differs by six.

**A large driving flow reported without comment.** Fifteen per cent is a preburner and the engine is a different one.

**An expander closure assumed rather than checked.** It is the only cycle where it can fail.

**Turbine efficiency assumed at industrial values.** A rocket turbine runs far below its optimum blade speed ratio.

**A closure check that passes and a temperature limit that does not.** Closing the power balance is necessary and not sufficient.

---

## Worked numbers

The [worked example](../codeInterface.py) engine, 0.624 MW of pump power at 36.81 kg/s total flow.

| Cycle | `PR` | Term | Work [kJ/kg] | Flow [kg/s] | Fraction | Is a bleed |
|---|---|---|---|---|---|---|
| Gas generator | 20.0 | 0.451 | 558 | 1.12 | 3.0 % | Yes |
| Staged combustion | 1.5 | 0.078 | 107 | 5.83 | 15.8 % | No |
| Expander | 1.6 | 0.090 | 62 | 10.12 | 27.5 % | No |

---

## Standards

| Standard | What it gives you |
|---|---|
| NASA SP-125 | Design of liquid propellant rocket engines |
| NASA SP-8081 | Liquid propellant gas generators |
| NASA SP-8110 | Liquid rocket engine turbines |
| NASA SP-8107 | Turbopump systems |

---

## Tool interface

```python
from PowerBalance import PowerBalance

balance = PowerBalance()
balance.setInputs({'cycle':           'staged combustion',
                   'chamberPressure': 10.0e6,
                   'totalFlow':       36.81,
                   'pumpPower':       0.624e6})

work = balance.specificWork()
print(work['expansionTerm'], work['specificWork'])

driving = balance.calculateDrivingFlow()
print(driving['flowFraction'], driving['isBleed'])

print(balance.checkClosure()['closes'])
```

An expander closure check additionally needs `availableHeat`, which comes from [combustionDevices](../../combustionDevices/README.md).

---

## References

- NASA SP-125, *Design of Liquid Propellant Rocket Engines*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- Sutton and Biblarz, *Rocket Propulsion Elements*, chapter 6
- NASA SP-8081, *Liquid propellant gas generators*
