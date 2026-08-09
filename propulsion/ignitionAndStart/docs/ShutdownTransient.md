[Home](../README.md) > Shutdown Transient

# Shutdown Transient

## Contents

- [Overview](#overview)
- [Why shutdown is the harder problem](#why-shutdown-is-the-harder-problem)
- [The decay rate belongs to the vehicle](#the-decay-rate-belongs-to-the-vehicle)
- [The residual impulse, and the part that matters](#the-residual-impulse-and-the-part-that-matters)
- [Fuel-rich on purpose](#fuel-rich-on-purpose)
- [What the pumps are doing](#what-the-pumps-are-doing)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Shutdown gets a fraction of the attention start does and it is the harder of the two.

At start the engine is cold and empty and every event is commanded. At shutdown it is hot, full and spinning, and the propellant already downstream of the valves is going to arrive whatever the controller does. **The valves close; the engine does not stop.**

---

## Why shutdown is the harder problem

Three things are true at shutdown that are not true at start.

**The hardware is hot.** Everything is at operating temperature, so any excursion in mixture ratio happens with no thermal margin left.

**The system is full.** The dribble volume between the valves and the injector is liquid propellant with nowhere to go but the chamber.

**The turbomachinery has stored energy.** The pumps are spinning and they continue to pump. The RS-25 source notes that if the flow through the high pressure fuel turbopump falls below a critical value while it coasts, the excess power is dissipated by vaporising the hydrogen, which loses axial thrust control and causes significant internal rubbing. The shutdown schedule is written to avoid that until the pump is below 7000 rpm, which takes about five seconds.

The one thing that helps is that shutdown is **open loop**. There is nothing to control and no closed loop to destabilise, which is why the RS-25's shutdown development, in the same source, produced fewer problems than its start.

---

## The decay rate belongs to the vehicle

The RS-25 limits its oxidiser preburner valve to 45 per cent per second and its main oxidiser valve to 40. The stated reason for the first is an interface control document limit of **700,000 pounds of thrust per second, which is an orbiter structural limit**.

The engine could shut down faster. The airframe could not survive it.

That converts to 3.11 MN/s, and on a 100 kN engine it permits no faster than **32 ms** to zero thrust. On a larger engine the constraint bites harder in absolute time.

**A shutdown specification that does not name the vehicle it was written against is not a specification.** The number is not a property of the engine.

The main oxidiser valve rate has a second and different reason: it must close slowly enough to keep chamber pressure high relative to the turbine inlet pressures, because a further reduction in turbine back pressure would raise the pressure ratio and risk an overspeed. Two limits, two owners, and neither is about the valve.

---

## The residual impulse, and the part that matters

Two contributions after the shutdown command. The thrust decaying through its ramp, which is roughly half the steady thrust over the decay time. And the dribble volume, the liquid already downstream of the valves, which burns badly and produces a fraction of its design impulse.

On the reference booster, with 8 litres downstream of the valves:

| Contribution | Impulse | Share |
|---|---|---|
| Thrust ramp | 1.61 kN s | 12 % |
| Dribble volume | 11.39 kN s | **88 %** |
| Total | 12.99 kN s | |

**The residual impulse is the plumbing, not the ramp.** 8.4 kg of propellant is downstream of the valves when they close.

And then the result that matters:

**The magnitude is not the problem. Its scatter is.** A cutoff impulse that is large but repeatable is trimmed out in the guidance, because guidance can predict it. One that varies from engine to engine and start to start cannot be trimmed, and it lands directly in the injection accuracy. At an assumed 15 per cent scatter that is about 1.95 kN s on this engine.

**A shutdown that is repeatable beats a shutdown that is fast**, and the design lever is the dribble volume: valves close-coupled to the injector are worth more than a faster valve.

---

## Fuel-rich on purpose

The oxidiser is shut down faster than the fuel, so the mixture ratio falls through the transient.

An oxidiser-rich excursion at combustion temperature attacks everything it touches: the injector face, the throat, and on a staged combustion engine the turbine. Running fuel-rich costs a little unburned fuel and protects the hardware.

The RS-25 holds its main fuel valve open for more than a second past the shutdown command for exactly this, and its first shutdown action is to remove power from the oxidiser turbopump turbine so that oxidiser flow falls faster than fuel flow.

[ShutdownTransient](ShutdownTransient.md) refuses a sequence where the fuel valve closes at or before the oxidiser valve, on the same grounds the start sequence ordering check refuses an out-of-order start. An engine that shuts down oxidiser-rich is not a slightly worse engine.

---

## What the pumps are doing

Worth stating because it is the constraint nobody expects.

The RS-25 partially closes its chamber coolant valve during shutdown to force more coolant into the chamber and nozzle, because the heat load rises as the engine throttles down. It holds the fuel valve open both to keep the shutdown fuel-rich and to keep flow through the coasting fuel turbopump, and it schedules that flow so the pump never falls below the rate at which its own residual power would start boiling the hydrogen.

None of that is about thrust. It is about not destroying the machinery on the way down.

---

## Worked numbers

The 100 kN reference booster.

| Quantity | Value |
|---|---|
| Reference structural decay limit | 700,000 lbf/s, 3.11 MN/s |
| Minimum decay time at 100 kN | 32 ms |
| Feed volume downstream of the valves | 8 L |
| Dribble mass | 8.4 kg |
| Ramp impulse | 1.61 kN s |
| Dribble impulse | 11.39 kN s |
| Total residual | 12.99 kN s |
| Scatter, at 15 per cent | 1.95 kN s |
| Fuel valve lead over oxidiser | 1.20 s |
| RS-25 fuel valve hold | more than 1 s |

---

## Design rules of thumb

- **Close the oxidiser first, always.** There is no case for anything else.
- **Minimise the dribble volume before minimising the valve closing time.** It is 88 per cent of the residual on this engine.
- **Specify repeatability, not magnitude.** Guidance trims what it can predict.
- **Get the decay rate limit from the vehicle**, not from the engine supplier.
- **Keep flow through a coasting pump.** The residual power has to go somewhere.

---

## Failure modes

**An oxidiser-rich shutdown.** Refused by the tool. It is how injector faces and turbines are destroyed.

**A dribble volume nobody counted.** It dominates the residual impulse and it is set by the plumbing layout, which is usually fixed by the time anyone computes a cutoff impulse.

**A decay rate specified without a vehicle.** The 700,000 lbf/s figure is an orbiter limit and it does not transfer.

**A pump allowed to run dry while coasting.** Boilout, loss of axial thrust control, internal rubbing.

**Chasing cutoff impulse magnitude.** The scatter is what reaches the trajectory.

---

## Tool interface

```python
from ShutdownTransient import ShutdownTransient

shutdown = ShutdownTransient()
shutdown.setInputs({'combination': 'LOX/RP-1',
                    'thrust':      100.0e3,
                    'massFlow':    36.81,
                    'feedVolume':  0.008})

decay    = shutdown.calculateDecayLimit()
residual = shutdown.calculateResidualImpulse()
order    = shutdown.checkShutdownOrder(oxidiserCloseTime = 0.0, fuelCloseTime = 1.2)

print(shutdown.generateReport())
```

`checkShutdownOrder()` raises rather than returning a verdict when the shutdown would run oxidiser-rich.

---

## References

- Biggs, *Space Shuttle Main Engine: The First Ten Years*, part 3, Start and Shutdown, AAS History Series volume 13
- Sutton and Biblarz, *Rocket Propulsion Elements*, the engine systems and controls chapters
- Huzel and Huang, *Modern Engineering for Design of Liquid-Propellant Rocket Engines*
