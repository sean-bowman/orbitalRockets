[Home](../README.md) > Pyrotechnics

# Pyrotechnics

## Contents

- [Overview](#overview)
- [The two currents](#the-two-currents)
- [The firing circuit](#the-firing-circuit)
- [Devices in parallel](#devices-in-parallel)
- [Keeping stray energy out](#keeping-stray-energy-out)
- [Safe and arm](#safe-and-arm)
- [The shock, which is not computed](#the-shock-which-is-not-computed)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A bridgewire initiator is a resistor in contact with an explosive. Current heats the wire, the wire ignites the charge, and everything else in this document follows from wanting that to happen exactly once at exactly the right moment.

---

## The two currents

**No-fire** is the current the device must survive without firing. The NASA Standard Initiator convention is one amp and one watt applied for five minutes.

**All-fire** is the current at which it fires reliably, typically around five amps for an NSI.

**The gap is narrower than it looks.** A five to one ratio in current is twenty-five to one in power, and a fault putting a few volts across a one ohm bridgewire is already most of the way to no-fire.

One detail worth knowing: **the one amp and one watt are two independent limits, not one derived from the other.** At the nominal 1.05 ohm bridgewire, one amp dissipates 1.05 W, so the current limit is very slightly the binding one. A fault delivering a fixed voltage and one delivering a fixed current land on different limits, and both have to be checked.

---

## The firing circuit

Ohm's law, and the harness is usually the problem.

```
I = V / (R_harness + R_switch + R_bridgewire)
```

The voltage that matters is the one at the initiator bus **at the worst credible moment**: a cold battery at the end of a long countdown, not a nameplate value.

On the reference circuit, 28 V through 0.9 ohm of harness, 0.05 of switch and 1.05 of bridgewire delivers 18.98 A on the bus.

---

## Devices in parallel

Firing two initiators from one circuit is the usual redundancy, and it changes the arithmetic.

Parallel bridgewires present a lower resistance to the supply, so the bus current rises. But the **current per device falls**, because the same bus current is now shared:

| Devices | Bus current | Per device |
|---|---|---|
| 1 | 12.9 A | 12.9 A |
| 2 | 19.0 A | 9.5 A |

**A circuit sized for one device does not fire several**, and this is the arithmetic that catches it before the pad does. [PyrotechnicInitiator](Pyrotechnics.md) refuses a circuit that cannot deliver all-fire with margin.

Note the redundancy that matters here is **two ways to release rather than two of the same device in series**. Two initiators on one band are two chances to cut it; two in a series firing circuit are two chances for an open circuit.

---

## Keeping stray energy out

Everything a vehicle does about electromagnetic compatibility near ordnance exists to keep the stray current below no-fire.

**Bonding and grounding**, so there is no potential difference to drive a current.

**Shielding and twisted shielded pairs** on every initiator circuit, so a harness does not act as an antenna.

**Shorting plugs** across the bridgewire until late in the flow, so induced current has a path that is not through the device.

**Radio silence** near a loaded vehicle, which is an operational control standing in for a design one.

The margin convention applied here is a factor of two on current, which is a factor of four on power. That sounds generous and is not: it is a margin against radio frequency pickup, lightning-induced transients, static discharge and a test set connected wrongly, all at once.

**The initiator choice is an electromagnetic compatibility decision as much as an ordnance one.** A low energy device fires from a smaller circuit, which is real mass and battery saving, and it drops the no-fire threshold five times, which tightens every bonding and shielding requirement on the vehicle.

---

## Safe and arm

A safe and arm device is a mechanical interruption in the explosive train. In the safe position the initiator can fire and the energy goes nowhere, because the path to the main charge is physically broken.

That is a categorically stronger guarantee than an electrical inhibit, and it is why the device exists: **an electrical inhibit protects against a circuit fault and a mechanical interrupter protects against everything**, including the circuit fault nobody predicted.

The position is a critical state and NASA-STD-5017B requires a direct indication of it, which means sensing the barrier position rather than the actuator that moved it.

---

## The shock, which is not computed

A pyrotechnic release produces a shock that everything nearby pays for. It is a high frequency, high acceleration, short duration transient, and it is the reason [environmentsAndLoads](../../environmentsAndLoads/) treats separation as a major shock source.

**This library does not predict it.** Pyroshock prediction is a test-derived discipline: the response depends on the joint, the structure behind it, the path and the mounting of whatever is being protected, and no analytic model in the open literature predicts it to better than an order of magnitude.

What [ClampBand](SeparationSystems.md) computes instead is the **released strain energy**, 11.3 J on the reference band. That is the right quantity to compare designs against each other and against a device with a measured signature, and it is where the boundary honestly sits.

---

## Worked numbers

| Quantity | Value |
|---|---|
| NSI no-fire | 1 A and 1 W, five minutes |
| NSI all-fire | 5 A |
| NSI bridgewire | 1.05 ohm |
| Firing voltage | 28 V |
| Harness resistance | 0.9 ohm |
| Bus current, two devices | 18.98 A |
| Current per device | 9.49 A |
| Ratio to all-fire | 1.9 |
| Stray current assumed | 0.15 A |
| Margin on current | 6.7 |
| Margin on power | 42 |

---

## Design rules of thumb

- **Size the circuit at the worst credible bus voltage**, not the nameplate.
- **Divide by the device count.** A circuit for one does not fire two.
- **Check no-fire on current and on power separately.** They are independent limits.
- **Use a mechanical interrupter.** An electrical inhibit is not the same guarantee.
- **Treat initiator sensitivity as an EMC requirement**, because that is what it becomes.

---

## Failure modes

**A circuit sized on one device and flown with two.** Half the current per device.

**Bus voltage taken as nameplate.** A cold battery at the end of a countdown is the design case.

**Stray current assumed zero.** Makes the no-fire check pointless, so the tool requires it.

**A sensitive initiator chosen for circuit mass.** It buys the mass back in bonding and shielding.

**An electrical inhibit treated as a safe and arm.** Different guarantees entirely.

---

## Tool interface

```python
from PyrotechnicInitiator import PyrotechnicInitiator

initiator = PyrotechnicInitiator()
initiator.setInputs({'initiatorType':     'NSI',
                     'firingVoltage':     28.0,
                     'harnessResistance': 0.9,
                     'parallelCount':     2,
                     'strayCurrent':      0.15})

allFire = initiator.checkAllFire()
noFire  = initiator.checkNoFire()
```

Both raise rather than reporting a negative margin.

---

## References

- NASA-STD-5017B, *Design and Development Requirements for Mechanisms*
- MIL-STD-1576, *Electroexplosive Subsystem Safety Requirements and Test Methods for Space Systems*, not read here
- [environmentsAndLoads](../../environmentsAndLoads/docs/), for the shock environment this produces
- [rangeSafetyAndFTS](../../rangeSafetyAndFTS/), which shares this initiation hardware
