[Home](../README.md) > The Mass Chain

# The Mass Chain

## Contents

- [Overview](#overview)
- [The chain](#the-chain)
- [One bar, traced](#one-bar-traced)
- [The amplification](#the-amplification)
- [Where the chain becomes brutal](#where-the-chain-becomes-brutal)
- [Why this crosses domains](#why-this-crosses-domains)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

This is the document this domain exists for.

Every other class here takes the structural coefficient as an input. It is the number the whole architecture turns on and it is the one nobody can supply, because it is an output of the tank, which is an output of the tank pressure, which is an output of the feed system.

So the question "what is a feed system pressure drop worth" has an answer, and it is not a pressure. It is a payload.

---

## The chain

```
feed system pressure drop
    -> tank operating pressure
    -> tank wall thickness           (aerospaceStructures)
    -> tank mass
    -> stage dry mass
    -> structural coefficient
    -> rocket equation
    -> payload
```

Four of those steps belong to three different domains and no one of them can see the whole thing. The feed system engineer choosing a line size is setting a tank pressure. The structures engineer sizing a wall is setting a payload. Neither is usually told so.

The chain is also **circular**, which is why it has to be iterated rather than evaluated. The propellant load sets the tank size, the tank mass sets the dry mass, the dry mass sets the propellant load. [SizingLoop](MassChain.md) closes that loop and **raises when it diverges rather than returning the last iterate**, because the last iterate of a diverging loop looks exactly like a converged answer.

---

## One bar, traced

On the reference vehicle, 1.5 t to low Earth orbit, two stages, kerolox, 0.9 m tank radius at 0.35 MPa.

| Step | Change |
|---|---|
| Tank pressure | +0.10 MPa |
| First stage wall thickness | +0.286 mm |
| First stage tank mass | +64 kg |
| Structural coefficient | 0.0402 to 0.0420 |
| **Liftoff mass, payload held** | **+730 kg** |

**One bar of extra feed system pressure drop costs 730 kg on a 40 tonne vehicle.**

That is a smaller line, a tighter filter, or one more valve in the run. It is the kind of decision made in an afternoon by somebody who is not thinking about payload, and the pressure drop budget in [fluidSystems](../../fluidSystems/) is where it is made.

---

## The amplification

The number worth carrying around is the ratio.

**Every kilogram added to the first stage tank costs about eleven kilograms at liftoff.**

That is not a coincidence of this vehicle. A kilogram of dry mass low in the stack has to be lifted by all the propellant below it, and the propellant to lift it has to be carried in a bigger tank, which is heavier. The amplification is the derivative of the sizing loop and it is always well above one.

Three consequences follow.

**A kilogram is not a kilogram.** Where it sits decides what it costs, and the same kilogram on the upper stage costs more still because it is carried further.

**Trades made in mass at the component level are wrong by an order of magnitude** unless they are amplified. A component engineer choosing between two designs 5 kg apart is choosing between vehicles 55 kg apart.

**The amplification is the argument for a vehicle model early.** Not to optimise the vehicle, which is flat in most of its variables, but to price the decisions being made in the subsystems, which are not.

---

## Where the chain becomes brutal

The same vehicle, swept across tank pressure.

| Tank pressure | Wall | Tank mass | Coefficient | Liftoff |
|---|---|---|---|---|
| 0.35 MPa | 1.00 mm | 210 kg | 0.0402 | 40.2 t |
| 0.70 MPa | 2.00 mm | 445 kg | 0.0464 | 42.8 t |
| 1.50 MPa | 4.29 mm | 1096 kg | 0.0601 | 49.7 t |
| 2.50 MPa | 7.16 mm | 2197 kg | 0.0763 | 60.5 t |
| 3.50 MPa | 10.02 mm | 3753 kg | 0.0918 | 74.5 t |

**Going from pump fed to pressure fed takes the same payload from 40.2 t to 74.5 t of vehicle, a factor of 1.85.** The structural coefficient leaves the kerolox booster band entirely and lands in the pressure fed one.

That is not a penalty applied from a table. It is the tank wall getting thicker, computed by the [aerospaceStructures](../../aerospaceStructures/docs/) pressure vessel model, and it is the whole reason turbopumps exist.

**One limitation, stated rather than buried.** The pressure vessel model has no minimum manufacturing gauge, so the thin-wall end of that table is optimistic: a real 2219 tank has a gauge floor of a millimetre or two regardless of pressure. That makes the low pressure rows better than they should be. It does not change the direction and it does compress the range.

---

## Why this crosses domains

[SizingLoop](MassChain.md) imports `PressureVessel` from [aerospaceStructures](../../aerospaceStructures/) rather than carrying its own tank model. That is the only three-domain coupling in this repository and it is deliberate.

**The alternative is two tank models that drift.** A vehicle-level tank estimate and a structures-level tank design will disagree eventually, both will produce plausible masses, and the disagreement will surface as an argument rather than as an error. Importing the real one means a change in the structures allowables reaches the payload with nobody reconciling anything.

A test asserts the import actually resolves into `aerospaceStructures`, because the failure mode if it ever stopped is silent.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Reference vehicle | 1.5 t to LEO, two stage kerolox |
| Closed liftoff mass | 40.2 t |
| Payload fraction | 3.73 % |
| Iterations to close | 5 |
| One bar of tank pressure | +730 kg liftoff |
| Amplification, tank kg to liftoff kg | **11.3** |
| Pump fed to pressure fed | 40.2 t to 74.5 t |

---

## Design rules of thumb

- **Price subsystem decisions through the chain, not in isolation.** A component trade in kilograms is wrong by an order of magnitude.
- **Get a vehicle model early**, to price decisions rather than to optimise the vehicle.
- **Tell the feed system engineer what a bar costs.** It is usually the first time anyone has.
- **Iterate the closure and refuse the divergence.** A diverging loop's last iterate reads as an answer.
- **Import the tank, do not estimate it.** One model, or two that drift.

---

## Failure modes

**A diverging sizing loop reported as a result.** The last iterate looks converged. [SizingLoop](MassChain.md) raises instead.

**Two tank models.** One at vehicle level and one in structures, drifting silently, both plausible.

**A component trade done in component kilograms.** Off by the amplification factor, which is about eleven at the bottom of this vehicle.

**A minimum gauge omitted.** Makes low-pressure tanks lighter than anything manufacturable.

**A structural coefficient asserted rather than computed.** It is the answer, not an input. [SizingLoop](MassChain.md) refuses one.

---

## Tool interface

```python
from SizingLoop import SizingLoop

loop = SizingLoop()
loop.setInputs({'payloadMass':  1500.0,
                'targetDeltaV': 9300.0,
                'stages': [{'specificImpulse': 297.0, 'deltaVFraction': 0.45},
                           {'specificImpulse': 340.0, 'deltaVFraction': 0.55}],
                'tankRadius':   0.9,
                'tankPressure': 0.35e6,
                'tankMaterial': '2219-T87'})

closed = loop.close()
trace  = loop.traceMassChain(pressureIncrement = 0.1e6)

print(loop.generateReport())
```

The structural coefficient is deliberately not an input. Passing one raises, because computing it is what the class is for.

---

## References

- [aerospaceStructures PressureVessel](../../aerospaceStructures/docs/), for the tank model this imports
- [fluidSystems](../../fluidSystems/), for where the pressure drop is decided
- Sutton and Biblarz, *Rocket Propulsion Elements*, the vehicle sizing chapter
- Humble, Henry and Larson, *Space Propulsion Analysis and Design*, for the sizing loop structure
