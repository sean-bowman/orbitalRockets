[Home](../README.md) > Ignition Systems

# Ignition Systems

## Contents

- [Overview](#overview)
- [The five types](#the-five-types)
- [What actually decides the selection](#what-actually-decides-the-selection)
- [The detection window](#the-detection-window)
- [Hypergolic propellants, which have no igniter](#hypergolic-propellants-which-have-no-igniter)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

An igniter has to deliver enough energy, in the right place, at the right moment, as many times as the mission requires. Of those four, the first is almost never the constraint.

Every device below delivers orders of magnitude more than the minimum ignition energy of a gaseous propellant mixture. **An ignition problem is almost never solved by a bigger igniter.** It is solved by the sequence, and this document is largely about why.

---

## The five types

| Type | Restarts | Needs power | Consumable | Flight example |
|---|---|---|---|---|
| Augmented spark | Unlimited | Yes | No | RS-25, one per combustor |
| Torch | Unlimited | Yes | No | RL10 |
| Pyrotechnic | One per installation | Yes | Yes | Solid charge, various |
| Hypergolic slug | One per cartridge | **No** | Yes | F-1 and Merlin, TEA-TEB |
| Catalytic | Unlimited | No | No | Hydrazine monopropellant, Shell 405 |

An **augmented spark igniter** is a small chamber burning the main propellants, lit by a spark plug, exhausting into the main chamber. Unlimited restarts and no consumable, at the cost of a propellant tap and its own small feed system.

A **torch** is the same idea. Where the two are distinguished, a torch has its own gas supply rather than tapping the main propellants.

A **pyrotechnic** igniter is a solid charge: the most energy for the least hardware, works with any propellant, spent once.

A **hypergolic slug** is a cartridge of something that ignites on contact with the oxidiser, burst into the fuel line. It needs no electrical power at the engine at all, which is its real advantage.

A **catalytic** bed is not an igniter in the usual sense. It decomposes a monopropellant, and its limits are bed life and cold-start performance rather than ignition energy.

---

## What actually decides the selection

Two constraints, and each removes a different half of the list.

**Restart removes the consumables.** A cartridge is spent once, so three starts means three installations, and above one or two the answer becomes a device with a propellant tap.

**No electrical power at the engine removes everything else.** A hypergolic cartridge is the only device on the list that needs none, which is why the F-1 used one.

On the reference booster:

| Case | Survivors |
|---|---|
| One start, power available | Augmented spark, torch, pyrotechnic, hypergolic slug |
| Three starts, power available | Augmented spark, torch |
| One start, no power at the engine | Hypergolic slug |
| Three starts, no power at the engine | **None** |

The last row is not a hard igniter problem. It is an architecture that has not been closed, and the right response is to move the power or the start count. [IgnitionSystem](IgnitionSystems.md) raises there rather than returning an empty answer.

Where more than one survives, the choice is made on grounds the class does not model: what the programme has flown before, and what the test stand already supports. The class reports the survivors and picks the one with no consumable, which is a **stated convention rather than a derived result**.

---

## The detection window

This is the part worth taking away, and the conclusion is not the one the words "ignition detection" suggest.

The window is not set by how fast a pressure transducer responds. It is set by how much propellant may accumulate before combustion, which is a mass budget:

```
t_window = N_permitted * t_residence / startFlowFraction
```

On the reference booster, at full mainstage flow, two chamber-fulls accumulate in **2.9 ms**. A detection system needs on the order of **10 ms** to sense a chamber pressure rise, decide, and command a valve.

**No practical detection system is fast enough to prevent that hard start. It can only record it.**

| Start flow | Window | Detection can act |
|---|---|---|
| 100 % | 2.9 ms | No |
| 50 % | 5.9 ms | No |
| 30 % | 9.8 ms | No |
| 10 % | 29 ms | Yes |
| 5 % | 59 ms | Yes |

The only lever with authority is the flow. Admitting **29 per cent** of mainstage flow opens the window to the detection latency, and that is what a staged valve sequence is: a way of buying time by not delivering propellant.

**Detection exists to abort, not to protect. The protection is in the sequence.** The RS-25 verifies ignition at 1.7 seconds and again at 2.3, well after its combustors have primed, and by then the flow schedule has already bounded what a failed ignition could do.

---

## Hypergolic propellants, which have no igniter

A hypergolic combination has no igniter to select. The delay is a property of the propellants and the injector, and for MMH with nitrogen tetroxide it is 1 to 5 ms at ambient conditions.

That range is wide because the measurement method matters. Liquid-phase induction times are measured in tens of microseconds; everything above that is physical transport and heat transfer, which is why the observed delay depends on the injector rather than only on the chemistry.

**The real reason storable propellants dominate spacecraft propulsion is not the storability**, which is in the name. It is that a system with no igniter has one fewer thing to fail after ten years in orbit.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Residence time, reference booster | 1.47 ms |
| Detection window at mainstage flow | 2.9 ms |
| Assumed detection latency | 10 ms |
| Start flow that makes detection viable | 29 % |
| MMH/NTO ignition delay, measured range | 1 to 5 ms |
| RS-25 ignition verification times | 1.7 s and 2.3 s |

---

## Design rules of thumb

- **Select on restart count and power availability.** Energy is fourth and it is rarely binding.
- **Do not size a detection system to prevent a hard start.** Size the flow schedule.
- **A cartridge buys sequence speed, not reliability.** Its value is permission to admit flow while it works.
- **Count the installations.** An igniter that supports one start on a stage that needs four is four igniters, and that is usually what kills it.
- **Hypergolic means no igniter, not no ignition problem.** The delay is still real and it still sets the permitted flow.

---

## Failure modes

**Selecting on energy.** Every device has enough. Selecting on energy means the real constraint was never identified.

**Assuming detection protects the engine.** It cannot act inside the window on a large chamber.

**A restart requirement discovered late.** It invalidates the whole selection, because it removes an entire class of device rather than penalising it.

**An igniter qualified in air and flown in vacuum.** Not modelled here and it is a real effect: ignition delay and spark behaviour both change.

**No power at the engine, discovered after the igniter was chosen.** This combination is refused by the tool rather than approximated, because there is no partial answer to it.

---

## Tool interface

```python
from IgnitionSystem import IgnitionSystem

system = IgnitionSystem()
system.setInputs({'combination':       'LOX/RP-1',
                  'startsRequired':    3,
                  'powerAvailable':    True,
                  'residenceTime':     0.00147,
                  'startFlowFraction': 0.15})

selection = system.selectIgniter()
window    = system.calculateDetectionWindow()

print(system.generateReport())
```

Take `residenceTime` from `StartTransient.residenceTime()` for the same engine, so the two classes are describing one chamber.

---

## References

- Biggs, *Space Shuttle Main Engine: The First Ten Years*, part 3, Start and Shutdown, AAS History Series volume 13
- Sutton and Biblarz, *Rocket Propulsion Elements*, the ignition sections
- Comparative reviews of hypergolic ignition delay at ambient conditions, drop test and impinging jet methods
- NASA SP-8081, *Liquid propellant gas generators*
