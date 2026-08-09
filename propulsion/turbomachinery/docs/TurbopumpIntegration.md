[Home](../README.md) > Turbopump Integration

# Turbopump Integration

## Contents

- [Overview](#overview)
- [One shaft or two](#one-shaft-or-two)
- [The shaft speed is a vehicle decision](#the-shaft-speed-is-a-vehicle-decision)
- [The cycle decides it](#the-cycle-decides-it)
- [Boost pumps](#boost-pumps)
- [Gearing](#gearing)
- [The start problem](#the-start-problem)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A turbopump is three machines that have to agree about one number. This document is about the agreement rather than about any of the three.

---

## One shaft or two

**One shaft** is lighter, simpler, has one set of bearings and one turbine, and forces both pumps to run at the same speed whether that suits them or not. It also puts the fuel and the oxidiser on the same rotating assembly, which is what makes the [interpropellant seal](SealsAndInterpropellantSeals.md) a safety critical item.

**Two shafts** let each pump run where it wants, remove the interpropellant seal problem entirely, and cost a second turbine, a second set of bearings and a second seal package. RS-25 does this, with separate high pressure fuel and oxidiser turbopumps.

The interesting result from the [worked example](../codeInterface.py) is that the penalty for a common shaft is smaller than it looks. On 30 m of available NPSH the two pumps' maximum shaft speeds land **within four per cent of each other**, 51 260 rpm for the LOX side and 53 155 for the RP-1.

That is a coincidence of this engine rather than a rule: the oxidiser has more than twice the volumetric flow, which hurts its suction specific speed, and it is cryogenic, which helps by almost exactly as much. But it is worth checking before assuming a common shaft compromises anything, and the published RS-25 speeds make the same point from the other direction: on separate shafts, free to differ, the two run at 35 360 and 36 000 rpm, **within two per cent.**

---

## The shaft speed is a vehicle decision

Four constraints pull two ways.

| Constraint | Wants | Why |
|---|---|---|
| Pump specific speed | Faster | Efficiency rises toward a peak it never reaches |
| Turbine blade speed ratio | Faster | The optimum is 0.470 and a rocket sits far below it |
| Bearing DN | Slower | Bore times rpm, and it is a hard limit |
| Cavitation | Slower | NPSH goes as speed to the four thirds |

The cavitation constraint is the one that leaves the domain. NPSH is bought with tank pressure, tank pressure is bought with wall thickness, and **the shaft speed of a turbopump therefore sets a fraction of the vehicle's dry mass** through a chain with four links and no single owner.

That makes shaft speed a vehicle-level decision that looks like a component-level one.

---

## The cycle decides it

The strongest result in this sub-domain, and it comes from outside it.

Sweeping shaft speed and totalling turbopump mass, tank mass and dumped propellant for the worked example engine:

| Cycle | Optimum shaft speed | What dominates |
|---|---|---|
| Open, gas generator | **55 000 rpm** | Dumped turbine propellant |
| Closed, staged combustion | **27 000 rpm** | Tank pressure |

**A factor of 2.04, with nothing about the pumps changing between the two.**

On an open cycle the turbine flow is thrown overboard, so turbine efficiency is worth real propellant and it is worth spinning fast to get it. On a closed cycle that flow goes to the main chamber and costs nothing, so there is no reason to chase turbine efficiency and the tank mass wins.

**The cycle is chosen before any of this**, in [engineCycles](../../engineCycles/README.md), and it is not usually thought of as a turbopump decision.

Two further observations from the same sweep.

**The optimum is broad and the penalty is violently asymmetric.** Everything from 42 000 to 66 000 rpm is within five per cent of the open cycle minimum, and half the optimum speed costs 33 per cent. A broad optimum is not an invitation to sit in the middle of it: **err fast, up to the hard limits.**

**The hard limit that binds is the turbine blade, not the pump.** At the open cycle optimum the blade reaches 432 m/s against a 450 m/s stress limit, while both impellers sit under 170 m/s against limits of 450 and 550. On a moderate chamber pressure engine the pump is not the hard part of a turbopump.

---

## Boost pumps

A low pressure pump ahead of the main pump, raising the inlet pressure so the main pump can spin faster without cavitating.

It is a way of buying shaft speed without buying tank pressure, and it is what makes very high pressure engines possible. RS-25 runs a low pressure fuel turbopump at **5150 rpm** ahead of a high pressure one at **35 360 rpm**, a factor of seven.

**A boost pump is axial**, and for a reason worth stating because the classical charts get it wrong. At the LPFTP's dimensionless specific speed of about 0.285 the industrial chart says radial. The real machine is axial, because an axial inducer stage tolerates far more vapour than a radial impeller and the boost pump is chosen for cavitation performance rather than for specific speed. See [PumpSizing](PumpSizing.md).

The cost is a second machine, its own drive, and a start sequence that has to bring both up in the right order.

---

## Gearing

Almost never used on a rocket turbopump, and the reasons are worth knowing because the question comes up every time.

A gearbox would let the pump and the turbine each run where they want, which is exactly the compromise this whole sub-domain is about. It costs mass, it costs a lubrication system that has to work in the propellant environment, it is a reliability item in a machine with very few of them, and the power densities are extreme.

**The RL10 is the notable exception**, with a geared oxidiser pump. It is an expander cycle upper stage engine where the shaft speeds genuinely could not be reconciled and the power is modest.

The usual answer is to accept the compromise, and the [worked example](../codeInterface.py) shows why: the common shaft penalty is frequently small.

---

## The start problem

A turbopump has to accelerate from rest to full speed with nothing driving the turbine until propellant is flowing, and nothing flowing until the pump turns.

**The bootstrap has to come from somewhere.** A start cartridge, a spin-up gas bottle, tank head alone on a low pressure system, or a carefully sequenced tank-head start that gets enough flow to light a gas generator that then takes over.

Three things make it difficult beyond the bootstrap itself.

**The machine passes through a critical speed** if it operates supercritically, which most fast turbopumps do. See [ShaftDynamics](ShaftDynamics.md).

**The seals are neither sealing nor lifted** during part of the transient, if they are lift-off designs.

**The mixture ratio is uncontrolled** until both pumps are up, because the two circuits accelerate at different rates. An engine that reaches an oxidiser-rich excursion during start is an engine that damages its chamber before it reaches steady state, which is why start sequences are developed by test rather than designed by analysis.

That is [ignitionAndStart](../../ignitionAndStart/README.md), and it is the sub-domain that consumes what this one produces.

---

## Design rules of thumb

- **Check whether the two pumps actually want different speeds** before paying for two shafts. They frequently do not.
- **Ask what the cycle is before optimising shaft speed.** It moves the answer by a factor of two.
- **Err fast.** The optimum is broad and the penalty for slow is much larger than for fast.
- **Check the turbine blade stress before the pump impeller.** It is usually the binding limit.
- **Fit a boost pump instead of raising tank pressure** where the chamber pressure is high.
- **Do not gear it** unless the shaft speeds genuinely cannot be reconciled.
- **Develop the start sequence by test.** The mixture ratio transient is not designable by analysis.

---

## Failure modes

**Shaft speed chosen before the cycle.** The answer moves by a factor of two.

**Two shafts paid for without checking whether one would do.**

**The optimum treated as a target rather than a ceiling.** It is broad, and slow costs far more than fast.

**Pump impeller stress checked, turbine blade not.** The blade binds first.

**Tank pressure raised to fix cavitation when a boost pump would be lighter.**

**An oxidiser-rich mixture ratio excursion during start.** Damages the chamber before steady state.

**The interpropellant seal treated as a component rather than a system.** It is a sequence of seals, drains, purges and vents, and the vent is on the outside of the engine.

---

## Worked numbers

The worked example turbopump for the hub's 100 kN booster.

| Quantity | Value |
|---|---|
| Oxidiser pump maximum speed on 30 m NPSH | 51 260 rpm |
| Fuel pump maximum speed on 30 m NPSH | 53 155 rpm |
| Difference | 4 % |
| Open cycle optimum | 55 000 rpm |
| Closed cycle optimum | 27 000 rpm |
| Ratio | 2.04 |
| Within 5 % of the open optimum | 42 000 to 66 000 rpm |
| Cost of running at half the optimum | +33 % mass |
| Blade speed at the open optimum | 432 m/s against a 450 limit |
| Impeller tip speeds at the same point | under 170 m/s |

RS-25, for comparison, on separate shafts:

| Pump | Shaft speed [rpm] |
|---|---|
| High pressure fuel | 35 360 |
| High pressure oxidiser | 36 000 |
| Low pressure fuel | 5 150 |

---

## Standards

| Standard | What it gives you |
|---|---|
| **NASA SP-8107** | **Turbopump systems for liquid rocket engines.** The integration monograph |
| NASA SP-8048 | Turbopump bearings |
| NASA SP-8052 | Turbopump inducers |
| NASA SP-8110 | Turbines |
| NASA SP-8121 | Rotating shaft seals |
| NASA-STD-5012 | Strength and life assessment for rocket engines |

---

## Tool interface

The integration result is the worked example rather than a class, because it is a system trade across all three components.

```bash
python propulsion/turbomachinery/codeInterface.py
```

It sweeps shaft speed, totals the mass on both cycles, and reports which limit binds.

---

## References

- NASA SP-8107, *Turbopump systems for liquid rocket engines*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- Sutton, *History of Liquid Propellant Rocket Engines*
- Childs, *Turbomachinery Rotordynamics*
- Sutton and Biblarz, *Rocket Propulsion Elements*, chapter 10
