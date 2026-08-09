[Home](../README.md) > Engine Sizing

# Engine Sizing

## Contents

- [Overview](#overview)
- [The chain](#the-chain)
- [Chamber pressure is the master variable](#chamber-pressure-is-the-master-variable)
- [What sizes the chamber](#what-sizes-the-chamber)
- [Residence time is not what you expect](#residence-time-is-not-what-you-expect)
- [Nozzle length and the divergence loss](#nozzle-length-and-the-divergence-loss)
- [Mass](#mass)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Sizing an engine is a short chain of forced steps followed by two decisions that are not forced at all. The chain is easy and the decisions are where the engineering is.

---

## The chain

```
mdot = F / (Isp g0)             the propellant the thrust requires
At   = mdot c* / Pc             the throat that chokes that flow at that pressure
Ae   = eps At                   the exit the expansion requires
Vc   = L* At                    the chamber volume combustion requires
Ac   = contraction ratio x At   the chamber cross-section
```

Each line follows from the one above it. **The throat is where the engine is defined**, and every other area in the geometry is a ratio to it.

The closing check is that `F = Cf Pc At` returns the thrust the geometry was derived from. It is worth running: it catches a mismatched ambient pressure between the performance calculation and the sizing, which is otherwise invisible.

**State the ambient pressure the thrust is quoted at.** A 100 kN sea level engine and a 100 kN vacuum engine differ by roughly ten per cent of throat area, and nothing in the arithmetic will tell you which one was meant.

---

## Chamber pressure is the master variable

Everything gets better and everything gets harder together. For a 100 kN LOX/RP-1 engine at an area ratio of 20, thrust quoted at sea level:

| `Pc` [MPa] | `Isp` [s] | Throat diameter [mm] | Chamber volume [cm^3] | Cooling margin |
|---|---|---|---|---|
| 2 | 135.6 | 289.4 | 72 366 | 26.07 |
| 5 | 242.0 | 137.0 | 16 226 | 3.78 |
| 10 | 277.4 | 90.5 | 7 077 | 1.62 |
| 20 | 295.1 | 62.0 | 3 326 | 0.83 |
| 30 | 301.0 | 50.2 | 2 174 | 0.58 |

Three things to read off it.

**Performance saturates.** From 2 to 10 MPa buys 142 seconds. From 20 to 30 MPa buys 6. The returns fall away sharply and the difficulty does not.

**The engine shrinks fast.** A factor of 15 in chamber pressure is a factor of 33 in chamber volume. High chamber pressure engines are small, dense and awkward, and that compactness is most of why they are hard rather than an incidental consequence.

**The 2 MPa row is a warning rather than a data point.** 135.6 seconds is not a real engine, it is an area ratio of 20 at a chamber pressure that cannot support it: the nozzle is grossly over-expanded at sea level and the flow has separated. **Area ratio and chamber pressure are not independent choices**, and pairing a large expansion with a low chamber pressure produces arithmetic rather than an engine.

---

## What sizes the chamber

Two competing requirements, and which governs flips with chamber pressure.

**Characteristic length** gives a volume, `Vc = L* At`, from the residence time combustion needs. Typical values are 1.10 m for LOX/RP-1, 0.90 m for LOX/LH2 and 0.80 m for the hypergolics, which need less because ignition delay is not part of the budget.

**Cooling** gives a wall area, from the heat load divided by the flux the wall can carry.

Volume and area are different functions of the geometry, so neither is derivable from the other and both have to be checked. For the same 100 kN engine at an area ratio of 20:

| `Pc` [MPa] | Cooling margin | Governed by |
|---|---|---|
| 10 | 1.62 | Characteristic length |
| 12 | 1.34 | Characteristic length |
| 14 | 1.15 | Characteristic length |
| 16 | 1.01 | Characteristic length, barely |
| 18 | 0.91 | Cooling |
| 30 | 0.58 | Cooling |

**The crossover is near 16 MPa.** Below it combustion sizes the chamber; above it cooling does, and the chamber is longer than its residence time requires because the extra length is wall area.

**The cross-check has to count the whole gas-side wall.** On the worked example the divergent section is 66 per cent of the wetted area. A cooling check run on the barrel alone concludes the chamber is short by a factor of two when the real margin is 1.64, and that error is in the direction that makes you lengthen a chamber that did not need it.

The flux used here is representative rather than computed, and it is a stand-in for a cooling analysis rather than a substitute for one. What the calculation establishes is that the two requirements are different numbers, not what either of them is on a specific engine.

---

## Residence time is not what you expect

Substituting the chain into `t = Vc rho_c / mdot`, with `rho_c = Pc / (R Tc)`:

```
t = L* c* / (R Tc)
```

**Both chamber pressure and mass flow cancel.** Residence time is a property of the propellant and the characteristic length, and of nothing else.

A 10 kN engine and a 1000 kN engine on LOX/RP-1 at `L*` = 1.10 m both hold their propellant for 1.47 milliseconds. So do the same engines at 5 MPa and at 30 MPa.

This is worth knowing before scaling an engine and expecting the combustion to behave differently, and before adjusting chamber pressure to fix a combustion problem. **The lever on residence time is `L*` and the propellant, and there is no third option.**

A liquid engine chamber holds its propellant for single-digit milliseconds. Anything outside that band by orders of magnitude is a units error rather than an unusual engine, which is exactly how the error that produced 1100 milliseconds in an early version of this library survived a glance.

---

## Nozzle length and the divergence loss

A conical nozzle throws away the transverse component of its exit momentum:

```
eta_div = (1 + cos alpha) / 2
```

At the classical 15 degree half angle that is 0.9830, a 1.7 per cent loss. **That loss is the entire reason bell nozzles exist.**

A bell is quoted as a percentage of the length of a 15 degree cone of the same area ratio. Eighty per cent is the common design point: it recovers most of the divergence loss for four fifths of the length, and the last twenty per cent buys very little.

For the worked example at an area ratio of 20.35, the cone is 593 mm and the 80 per cent bell is 475 mm.

**The contour that achieves it is a method of characteristics problem and belongs in the NOVA suite.** This is the envelope and the loss, which is what a sizing pass needs. See [nozzles](../nozzles/README.md).

---

## Mass

```
mass = F / (T/W g0)
```

A scaling estimate, and labelled as one. Real engines span roughly 60 for a small pressure-fed thruster to over 150 for a large staged combustion engine, and the cycle decides which end. The library uses 100.

| Thrust [kN] | Mass [kg] | Mass flow [kg/s] | Throat diameter [mm] |
|---|---|---|---|
| 10 | 10.2 | 3.68 | 28.6 |
| 100 | 102.0 | 36.76 | 90.5 |
| 1000 | 1019.7 | 367.60 | 286.2 |

**At 36.76 kg/s the 100 kN engine consumes its own mass in propellant every 2.8 seconds.** That ratio is why engine mass matters far less than propellant mass on anything but an upper stage, and why a mass estimate this crude is adequate for a first pass. It stops being adequate the moment the engine is on a stage whose burn time is measured in tens of seconds.

Engine mass is really set by the cycle, the chamber pressure and the materials, none of which a single ratio captures. The estimate exists because a vehicle sizing loop needs a number before any of those exist, and a number with its basis stated is better than a number without one.

---

## Design rules of thumb

- **Define the engine at the throat.** Everything else is a ratio to it.
- **Close the loop with `F = Cf Pc At`.** It catches a mismatched ambient pressure.
- **Do not choose area ratio and chamber pressure independently.** A large expansion at low chamber pressure separates.
- **Expect the chamber to be cooling limited above roughly 16 MPa.**
- **Count the nozzle in the wall area.** It is two thirds of it.
- **Do not try to change residence time with chamber pressure.** It cancels.
- **Take the mass estimate as a placeholder** and replace it once the cycle exists.

---

## Failure modes

**Thrust quoted without its ambient pressure.** Ten per cent on the throat area, silently.

**A large area ratio at low chamber pressure.** Produces impressive vacuum numbers and a separated nozzle at sea level.

**Cooling checked on the barrel alone.** Understates available wall area by a factor of three.

**A contraction ratio too large for the characteristic length.** The convergent section consumes the whole chamber volume and there is no barrel left to put an injector on. The class raises rather than returning a negative barrel length.

**Residence time treated as adjustable through chamber pressure.** It is not, and the attempt wastes a design cycle.

**A residence time outside single-digit milliseconds accepted.** It is a units error.

**The engine mass estimate carried into a mass budget as though it were a mass properties calculation.**

---

## Worked numbers

100 kN at sea level, LOX/RP-1, 10 MPa chamber pressure, area ratio 20.35, contraction ratio 2.5.

| Quantity | Value |
|---|---|
| Specific impulse | 277.0 s |
| Mass flow | 36.81 kg/s |
| Oxidiser flow | 26.47 kg/s |
| Fuel flow | 10.34 kg/s |
| Throat diameter | 90.6 mm |
| Exit diameter | 408.5 mm |
| Chamber diameter | 143.2 mm |
| Barrel length | 409.1 mm |
| Convergent length | 45.6 mm |
| Bell length | 475 mm |
| Chamber volume | 7 086 cm^3 |
| Residence time | 1.47 ms |
| Cooling margin | 1.64 |
| Governed by | Characteristic length |
| Wall heat load | 2.72 MW |
| Nozzle share of wall area | 66 % |
| Engine mass | 102.0 kg |

---

## Standards

| Standard | What it gives you |
|---|---|
| NASA SP-125 | Design of liquid propellant rocket engines. The sizing chapters |
| NASA SP-8087 | Liquid rocket engine fluid-cooled combustion chambers |
| NASA SP-8120 | Liquid rocket engine nozzles |
| NASA SP-8089 | Liquid rocket engine injectors |
| AIAA S-080 | Metallic pressure vessels, which the chamber is |
| CPIA 246 | Performance prediction, for the impulse the sizing starts from |

---

## Tool interface

```python
from EngineSizing import EngineSizing

sizing = EngineSizing()
sizing.setInputs({'combination':      'LOX/RP-1',
                  'thrust':           100000.0,
                  'chamberPressure':  10.0e6,
                  'areaRatio':        20.35,
                  'ambientPressure':  101325.0,
                  'contractionRatio': 2.5})

throat = sizing.sizeThroat()
print(throat['throatDiameter'], throat['massFlow'])

chamber = sizing.sizeChamber()
print(chamber['residenceTime'], chamber['coolingMargin'], chamber['governing'])

nozzle = sizing.sizeNozzle()
print(nozzle['bellLength'], nozzle['divergenceEfficiency'])

print(sizing.estimateMass()['mass'])
```

`characteristicLength` defaults per propellant and can be overridden. `sizeChamber` raises if the contraction ratio and the characteristic length are incompatible.

---

## References

- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- NASA SP-125, *Design of Liquid Propellant Rocket Engines*
- Sutton and Biblarz, *Rocket Propulsion Elements*, chapter 8
- NASA SP-8087, *Liquid rocket engine fluid-cooled combustion chambers*
- NASA SP-8120, *Liquid rocket engine nozzles*
