[Home](../README.md) > Start Transient

# Start Transient

## Contents

- [Overview](#overview)
- [The one ratio](#the-one-ratio)
- [Why no engine lights at mainstage flow](#why-no-engine-lights-at-mainstage-flow)
- [Reading it the other way round](#reading-it-the-other-way-round)
- [Priming](#priming)
- [The published sequence](#the-published-sequence)
- [How much margin a sequence has](#how-much-margin-a-sequence-has)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The start transient is the few hundred milliseconds between a valve first moving and the engine running, and a disproportionate share of engine failures live there. An engine that runs happily at steady state can destroy itself during a start that admits propellant in the wrong order.

This document is about one quantity: how much propellant is sitting unburned in the chamber when combustion finally establishes. Everything else in a hard start is a consequence of it.

---

## The one ratio

If combustion is established a time `t` after propellant first reaches the chamber, and the chamber's mean residence time is `t_res`, then the unburned propellant in the chamber at that moment is

```
massRatio = startFlowFraction * t_delay / t_residence
```

times the mass that would be there at steady state. Burn all of it at constant volume and the pressure spike is that same ratio times the design chamber pressure.

**That is the whole model.** It has three inputs and two of them are properties of the chamber rather than of the igniter.

The bound is loose and it is worth being explicit about how loose. It assumes everything that entered is at the right mixture ratio, is fully vaporised, burns to completion, and burns faster than the nozzle can vent it. None of those is true. What survives all of that is the **ranking**, and the ranking is what decides a sequence.

---

## Why no engine lights at mainstage flow

The reference booster has a chamber volume of 7.09 L, holds 54.1 g of combustion gas at the design point, and passes it in **1.47 ms**. That is the same residence time [combustionDevices](../../combustionDevices/docs/ChamberSizing.md) computes from the same characteristic length, which is worth noting: a transient calculation and a combustion efficiency calculation turn out to need the same number.

Now suppose the engine tried to light at full mainstage flow.

| Ignition delay | Chamber-fulls | Spike bound |
|---|---|---|
| Hypergolic slug, 3 ms | 2.0 | 20 MPa |
| Spark, prompt, 20 ms | 13.6 | 136 MPa |
| Spark, cold and marginal, 50 ms | 34.0 | 340 MPa |

Every one of them, including a three millisecond hypergolic slug on a chamber designed for 10 MPa.

**That is not a verdict on igniters. It is the reason no engine lights at mainstage flow.** An engine cannot be made safe by finding a faster igniter, because there is no igniter fast enough relative to a millisecond residence time. It is made safe by not delivering the propellant.

---

## Reading it the other way round

Take the ignition delay as given, permit two chamber-fulls, and ask what flow the sequence may admit while it runs.

| Ignition delay | Flow permitted |
|---|---|
| Hypergolic slug, 3 ms | 98 % |
| Spark, prompt, 20 ms | 15 % |
| Spark, cold and marginal, 50 ms | 6 % |

**A hypergolic slug can be lit on virtually the whole flow.** That is what a triethylaluminium/triethylborane cartridge actually buys: not reliability, and not energy, but permission to skip the slow part of the sequence. A torch at 20 ms may be given a fifteenth of the flow, and the sequence then has to spend seconds getting from there to mainstage.

This is the cleanest available explanation of why kerosene boosters with hypergolic cartridges start in a fraction of a second and hydrogen engines with spark torches take several.

---

## Priming

Priming is filling the system with liquid such that the flow entering the injector equals the flow leaving it. Until that happens the injector is passing a two-phase mixture and the engine is not running on the propellants it was designed around.

On the reference booster, 8 litres downstream of the main valves takes **228 ms** to prime at full flow, which is **155 residence times**.

**An engine is not started when the igniter fires. It is started when the last of that volume has arrived as liquid.** The RS-25 sequence is built entirely around this: it primes three combustors about a tenth of a second apart and the whole valve schedule exists to hit those times.

---

## The published sequence

The RS-25 is the only large liquid engine whose start sequence is published to the hundredth of a second, which makes it the anchor for this whole sub-domain. From Biggs, *SSME: The First Ten Years*, part 3.

| Time [s] | Event |
|---|---|
| 0.100 | Fuel preburner oxidiser valve begins its ramp to 56 per cent |
| 0.120 | Oxidiser preburner oxidiser valve initial opening, seal retraction only |
| 0.200 | Main oxidiser valve delay ends, ramps to just under 60 per cent |
| 0.667 | Main fuel valve fully open |
| 0.720 | Fuel preburner valve notch, riding the second fuel system pressure dip |
| 0.840 | Oxidiser preburner major flow path starts to open |
| 1.250 | Speed check: the high pressure fuel turbopump must exceed 4600 rpm |
| 1.400 | Fuel preburner primes |
| 1.500 | Main combustion chamber primes |
| 1.600 | Oxidiser preburner primes |
| 1.700 | Ignition verified |
| 2.400 | Closed loop thrust control activated |
| 3.800 | Closed loop mixture ratio control activated |
| 5.000 | Rated power level, mixture ratio 6 |

Three things in that table are worth reading twice.

**The fuel valve opens first and completes in two thirds of a second.** The fuel lead is not a courtesy; it establishes a fuel-rich chamber so that when oxidiser arrives it arrives into an environment that will not run oxidiser-rich.

**The three primes are the events the sequence is built around**, and they are a tenth of a second apart.

**Five seconds to rated power.** Those seconds are not the igniter being slow. They are the sequence keeping the accumulation small while the turbomachinery comes up.

---

## How much margin a sequence has

The same source states that a timing error of a tenth of a second, or a valve position error of 2 per cent and 1 per cent for the oxidiser preburner valve, can lead to significant damage.

**The design spacing between primes and the damaging timing error are the same number.**

That is the honest measure of how much margin a start sequence has, and it is why sequences are developed on a test stand rather than on paper. The same source records what that development cost: 19 tests, 23 weeks and 8 turbopump replacements to reach 2 seconds into a 5 second sequence, then 18 more tests, 12 weeks and 5 more turbopump replacements to touch minimum power level.

The reason the margin is so thin is inertia. The RS-25 turbopumps have the highest power to weight ratio ever achieved, and the same source notes that with normal operating torque and no fluid load the high pressure oxidiser turbopump could reach a destructive overspeed in less than a tenth of a second, at about 400,000 rpm per second. There is no time to correct anything.

---

## Worked numbers

The 100 kN reference booster.

| Quantity | Value |
|---|---|
| Chamber volume | 7.09 L |
| Chamber gas mass at the design point | 54.1 g |
| Residence time | 1.47 ms |
| Window before two chamber-fulls, at mainstage flow | 2.9 ms |
| Flow permitted with a 3 ms hypergolic delay | 98 % |
| Flow permitted with a 20 ms spark delay | 15 % |
| Feed volume downstream of the main valves | 8 L |
| Priming time at full flow | 228 ms |
| Priming time in residence times | 155 |

---

## Design rules of thumb

- **Compute the residence time first.** Every transient number in this sub-domain is measured against it, and it is usually already available from the chamber sizing.
- **Never assume the igniter is the problem.** It is the flow schedule.
- **The fuel leads.** Establish a fuel-rich chamber before oxidiser arrives, at start and at shutdown both.
- **Prime, then ramp.** An engine that has not primed is not running on liquid and nothing about its steady-state design applies.
- **Develop the sequence on a stand.** The margin is a tenth of a second and no model in this repository resolves that.

---

## Failure modes

**Ignition at mainstage flow.** The accumulation bound says this cannot be made safe by any igniter. It is a sequencing error, not an ignition system error.

**An out-of-order sequence.** Not modelled anywhere in this repository. [StartTransient](StartTransient.md) refuses it, because a sequence out of order is not a slow start, it is a destroyed engine.

**Relying on ignition detection to prevent damage.** It cannot; see [IgnitionSystems](IgnitionSystems.md). Detection aborts, it does not protect.

**Treating priming as instantaneous.** It is 155 residence times on the reference engine.

**A sequence copied from a different engine.** The timing follows from the chamber volume and the feed volume, both of which change.

---

## Standards

There is no ignition sequencing standard in the sense that there is a standard for random vibration or shell buckling, and that absence is itself worth recording. Start sequences are developed per engine on a test stand, and what exists in the literature is engine-specific history rather than requirements.

The relevant general documents are the NASA SP-8 series on liquid rocket engine components, which discuss start and shutdown as design considerations without prescribing a method.

---

## Tool interface

```python
from StartTransient import StartTransient

start = StartTransient()
start.setInputs({'combination':       'LOX/RP-1',
                 'chamberPressure':   10.0e6,
                 'throatArea':        6.446e-3,
                 'massFlow':          36.81,
                 'ignitionDelay':     0.020,
                 'startFlowFraction': 0.15,
                 'feedVolume':        0.008})

accumulation = start.calculateAccumulation()
priming      = start.calculatePriming()
comparison   = start.compareIgnitionDelays()

print(start.generateReport())
```

`checkSequence()` takes an ordered dictionary of event times and raises rather than returning a verdict when the ordering is wrong.

---

## References

- Biggs, *Space Shuttle Main Engine: The First Ten Years*, part 3, Start and Shutdown, AAS History Series volume 13
- Sutton and Biblarz, *Rocket Propulsion Elements*, the ignition and starting sections
- NASA SP-8089, *Liquid rocket engine injectors*
- Huzel and Huang, *Modern Engineering for Design of Liquid-Propellant Rocket Engines*, the engine systems chapter
