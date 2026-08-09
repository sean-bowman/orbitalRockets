[Home](../README.md) > Cavitation and NPSH

# Cavitation and NPSH

## Contents

- [Overview](#overview)
- [The chain that leaves the domain](#the-chain-that-leaves-the-domain)
- [Suction specific speed](#suction-specific-speed)
- [The four thirds power](#the-four-thirds-power)
- [What an inducer buys](#what-an-inducer-buys)
- [Thermodynamic suppression](#thermodynamic-suppression)
- [Most of a cryogenic tank pressure is not cavitation margin](#most-of-a-cryogenic-tank-pressure-is-not-cavitation-margin)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Cavitation is vapour forming at the pump inlet because the local pressure has fallen to the vapour pressure. It is not a graceful degradation: the pump loses head, the flow becomes unsteady, and collapsing bubbles erode the blade.

The reason it gets its own document is not the physics, which is simple. It is that **avoiding it is the most consequential decision this sub-domain makes**, and the consequence lands in a different domain entirely.

---

## The chain that leaves the domain

Four links, and no single owner:

```
shaft speed  ->  NPSH required  ->  tank pressure  ->  tank mass
```

A faster shaft needs more suction head. Suction head comes from tank pressure. Tank pressure needs a thicker wall and a bigger pressurisation system.

**So the shaft speed of a turbopump sets a fraction of the vehicle's dry mass.** It is not usually thought of that way, and the [worked example](../codeInterface.py) exists partly to make it visible: it computes the chain in both directions and a test asserts the two agree.

The number that leaves the domain is a tank pressure. It lands in [aerospaceStructures](../../../aerospaceStructures/README.md) as a wall thickness and in [fluidSystems](../../../fluidSystems/README.md) as a pressurisation requirement.

---

## Suction specific speed

The same dimensionless group as specific speed, with the available suction head in place of the developed head:

```
Nss = omega sqrt(Q) / (g NPSH)^0.75
```

It measures how hard the inlet is working rather than how hard the pump is.

| Configuration | Tolerable `Nss` |
|---|---|
| Bare centrifugal impeller | 3.0 |
| With an inducer | 12.0 |
| High performance inducer | 20.0 |

The high performance case accepts partial cavitation by design: the inducer runs with vapour present and the main impeller sees liquid, which is a very different thing from a pump cavitating.

---

## The four thirds power

Rearranging for the head a given speed demands:

```
NPSH_r = (omega sqrt(Q) / Nss)^(4/3) / g
```

**The four thirds exponent is what makes shaft speed expensive.** A ten per cent faster shaft needs fourteen per cent more suction head. Doubling the speed needs 2.52 times the head.

That exponent is the reason the shaft speed trade is not symmetric, and it is why the cavitation constraint tends to win arguments against the pump and turbine efficiency arguments, which are both roughly linear.

---

## What an inducer buys

An inducer is an axial stage ahead of the main impeller with a low blade angle and a large blade passage. It raises the inlet pressure enough that the main impeller does not cavitate, and it tolerates vapour in a way a radial impeller cannot.

**It buys a factor of four in shaft speed at the same suction condition.** On 30 m of available NPSH for the worked example LOX pump:

| Configuration | Maximum shaft speed [rpm] |
|---|---|
| No inducer | 12 815 |
| Inducer | 51 260 |
| High performance inducer | 85 433 |

That factor is the entire reason it is fitted. Without it the turbopump would be four times slower, four times larger, and heavier by more than the inducer weighs by a wide margin.

**This is also why rocket boost pumps are axial.** The RS-25 low pressure fuel turbopump runs at a dimensionless specific speed where the classical chart says radial, and it is axial, because it is chosen for cavitation performance rather than for specific speed. Reading the industrial geometry chart across to a boost pump gets it wrong. See [PumpSizing](PumpSizing.md).

---

## Thermodynamic suppression

Cryogens get help that storables do not, and it is a real effect rather than a margin.

Vaporising a little cryogen at the blade absorbs latent heat from the surrounding liquid. That cools it. Cooler liquid has a lower vapour pressure, which suppresses further vaporisation. **The cavitation partly puts itself out.**

| Propellant | Suppression factor |
|---|---|
| LH2 | 2.00 |
| LCH4 | 1.40 |
| LOX | 1.30 |
| RP-1, N2O4, MMH | 1.00 |

Hydrogen benefits most because its latent heat is large relative to its liquid heat capacity and its vapour pressure curve is steep.

**A storable propellant gets none of it**, which is an advantage for cryogens that is easy to forget when the disadvantages are so visible.

The factors here are an approximation of a genuinely complicated effect and they are registered as unvalidated.

---

## Most of a cryogenic tank pressure is not cavitation margin

The finding worth carrying away from this document.

For the worked example at 30 000 rpm:

| | Tank pressure [kPa] | Vapour pressure [kPa] | Vapour share |
|---|---|---|---|
| LOX | 288 | 101 | **35 %** |
| RP-1 | 129 | 2 | 2 % |

**On a cryogenic stage a large part of the tank pressure is not buying cavitation margin at all. It is holding the propellant liquid.**

The oxidiser tank costs roughly four times the fuel tank at every shaft speed, and the pump is barely responsible for the difference. LOX boils at 101 kPa and RP-1 at 2 kPa, so the LOX tank starts a hundred kilopascals in debt before any pump requirement is added.

That reframes the trade. Reducing shaft speed to save tank pressure works on the fuel side and works much less well on a cryogenic oxidiser side, because a large fixed component is not responding.

---

## Design rules of thumb

- **Hold at least 1.5 on NPSH.** Cavitation is a cliff, not a slope.
- **Work the chain in both directions.** Tank pressure from shaft speed, and shaft speed from an already-fixed tank pressure.
- **Fit an inducer.** It buys a factor of four and it is not close.
- **Expect cavitation to win against efficiency arguments.** It is a four thirds power and they are linear.
- **Credit thermodynamic suppression for cryogens** and never for storables.
- **Separate the vapour pressure from the cavitation margin** when reporting a tank pressure. They are different requirements with different owners.
- **Do not classify a boost pump from the industrial specific speed chart.**

---

## Failure modes

**NPSH available computed without the line loss.** The pump sees the inlet, not the tank.

**Suppression credited to a storable.** It is a cryogenic effect and the factor is 1.00.

**A tank pressure quoted without saying how much of it is vapour pressure.** Invites an attempt to reduce it that cannot work.

**Shaft speed raised late in design.** The four thirds power means a small speed increase is a large tank pressure increase, and the tank is somebody else's.

**Cavitation treated as a performance loss.** The head falls, the flow goes unsteady, and the blade erodes. It is a damage mechanism.

**A bare impeller assumed adequate.** Without an inducer the tolerable suction specific speed is a quarter of what it needs to be.

---

## Worked numbers

The worked example LOX pump: 26.47 kg/s, 1141 kg/m^3, 30 000 rpm, 3 m static head, 5 m line loss.

| Quantity | Value |
|---|---|
| Volumetric flow | 23.2 l/s |
| Suppression factor | 1.30 |
| Tolerable `Nss` | 15.6 |
| NPSH required | 9.8 m |
| With 1.5 margin | 14.7 m |
| Tank pressure required | 288 kPa |
| Vapour pressure share of it | 35 % |

Maximum shaft speed on 30 m available NPSH:

| Configuration | LOX [rpm] | RP-1 [rpm] |
|---|---|---|
| No inducer | 12 815 | 13 289 |
| Inducer | 51 260 | 53 155 |
| High performance | 85 433 | 88 592 |

The two propellants land within four per cent of each other, which is a coincidence of this engine: the oxidiser has more than twice the volumetric flow, which hurts, and it is cryogenic, which helps by almost exactly as much.

---

## Standards

| Standard | What it gives you |
|---|---|
| **NASA SP-8052** | **Liquid rocket engine turbopump inducers.** The design monograph |
| NASA SP-8107 | Turbopump systems |
| Brennen, *Hydrodynamics of Pumps* | The cavitation machinery |
| ANSI/HI 9.6.1 | NPSH margin practice, industrial but the reasoning transfers |

---

## Tool interface

```python
from Inducer import Inducer

inducer = Inducer()
inducer.setInputs({'propellant':     'LOX',
                   'density':        1141.0,
                   'massFlow':       26.47,
                   'shaftSpeed':     30000.0,
                   'vapourPressure': 101325.0,
                   'staticHead':     3.0,
                   'lineLoss':       5.0})

print(inducer.calculateRequiredNpsh()['withMargin'])
print(inducer.requiredTankPressure()['tankPressure'])

ceiling = inducer.maximumShaftSpeed(availableNpsh = 30.0)
print(ceiling['maximumRpm'], ceiling['comparison'])
```

Supplying `tankPressure` lets `checkMargin` work the chain the other way.

---

## References

- NASA SP-8052, *Liquid rocket engine turbopump inducers*
- Brennen, *Hydrodynamics of Pumps*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- Stepanoff, *Centrifugal and Axial Flow Pumps*
- NASA SP-8107, *Turbopump systems for liquid rocket engines*
