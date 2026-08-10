[Home](../README.md) > Valve and Actuator Drive

# Valve and Actuator Drive

## Contents

- [Overview](#overview)
- [Peak and hold](#peak-and-hold)
- [The hot coil is the design case](#the-hot-coil-is-the-design-case)
- [Inrush](#inrush)
- [Flyback, and the timing decision hidden in it](#flyback-and-the-timing-decision-hidden-in-it)
- [Motor drives](#motor-drives)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A solenoid valve is a coil, a spring and a moving iron core. Three things about driving one are worth knowing and all three are routinely left on the table.

---

## Peak and hold

Magnetic force goes roughly as the inverse square of the air gap, so a solenoid needs a large force to pull in and a much smaller one to stay closed once the gap has shut.

Drive it at pull-in current for the whole time it is open and three quarters of the energy becomes heat in the coil.

| Strategy | Current | Power |
|---|---|---|
| Continuous | 0.473 A | 13.25 W |
| Peak and hold at 50 per cent | 0.237 A | 3.31 W |

**A 75 per cent saving, because power goes as the square of current.**

Across four valves on the reference stage that is 40 W off the peak, and the same saving in coil heating, for the cost of a resistor and a transistor per valve. On a vehicle with valves open for minutes rather than milliseconds it is the difference between a heater-sized load and a negligible one.

---

## The hot coil is the design case

Copper gains about 0.393 per cent per kelvin. A coil at 100 C has **31 per cent more resistance** than at 20, pulls **24 per cent less current**, and makes about **42 per cent less force**, because force goes as the square of current.

**A valve that works cold and marginally hot is the classic version of this failure**, and it is found on a hot day rather than in qualification.

Two consequences.

**Size the pull-in at the hot resistance**, not the datasheet value at 20 C.

**Peak and hold reduces the heating that causes it**, which makes it a reliability measure and not only a power one: a coil that runs at a quarter of the power runs far cooler and keeps more of its force.

---

## Inrush

The coil is an inductor, so the current does not appear instantly:

```
tau = L / R
```

It matters for two reasons. It sets how quickly the valve actually opens, which is a sequencing question on a system with a timed sequence. And it stores energy that has to go somewhere when the drive is removed, which is the next section.

A current-limited supply drives this longer than the time constant suggests, which is worth checking on a bus with several valves actuating together.

---

## Flyback, and the timing decision hidden in it

When the drive opens, the coil's stored energy has to be dissipated.

**A plain freewheeling diode** clamps the voltage at about a volt. Kind to the switch, and slow: the current decays with the same time constant it built up with, and the valve stays open while it does.

**A diode plus zener** clamps higher, dissipates the energy faster, and closes the valve sooner.

On the reference valve, 3.4 mJ stored at hold current: a diode alone takes 6.1 ms to decay and a 50 V clamp takes 0.57 ms, **a factor of eleven**.

**The clamp voltage sets the valve closing time.** A designer choosing a suppression network on component stress alone has chosen a valve response time by accident, and on a sequenced system that is a sequencing decision made in the wrong meeting.

---

## Motor drives

Named rather than modelled, because the torque side belongs to [mechanismsAndSeparation](../../mechanismsAndSeparation/docs/ActuatorsAndDrives.md) and the electrical side needs a controller model this domain does not carry.

**Stall current** is the design case for the drive electronics and the protection, and it is several times the running current. NASA-STD-5017B requires the mechanism to remain functional after a stall at any point in travel, which makes the stall a specified condition rather than a fault.

**Back EMF** limits the speed and is what makes a motor drive current-controlled rather than voltage-controlled in most applications.

**Regeneration** on a decelerating load pushes current back into the bus, and a bus with no path for it sees a voltage rise.

---

## Worked numbers

The reference valve on a 28 V bus.

| Quantity | Value |
|---|---|
| Coil resistance at 20 C | 45.0 ohm |
| Coil resistance at 100 C | 59.1 ohm |
| Resistance rise | 31 % |
| Pull-in current, cold | 0.622 A |
| Pull-in current, hot | 0.473 A |
| Force ratio, hot to cold | 0.58 |
| Continuous power | 13.25 W |
| Hold power at 50 per cent | 3.31 W |
| Saving | 75 % |
| Stored coil energy | 3.4 mJ |
| Decay, diode only | 6.1 ms |
| Decay, 50 V clamp | 0.57 ms |

---

## Design rules of thumb

- **Use peak and hold** on anything open for more than a moment. It is nearly free.
- **Size pull-in at the hot resistance.** The datasheet value is at 20 C.
- **Choose the clamp on closing time**, then check the switch can take it.
- **Check inrush against the sequence** if several valves actuate together.
- **Treat motor stall as a design condition**, not a fault.

---

## Failure modes

**Continuous drive on a long-open valve.** Four times the power and four times the heating.

**Pull-in sized cold.** Works in qualification and marginally on a hot day.

**Suppression chosen on component stress.** Sets a valve closing time by accident.

**Inrush ignored on a shared bus.** Several valves at once is a different load from one.

**Motor drive sized on running current.** The stall is several times it.

---

## Tool interface

```python
from SolenoidDrive import SolenoidDrive

valve = SolenoidDrive()
valve.setInputs({'busVoltage':      28.0,
                 'coilResistance':  45.0,
                 'coilInductance':  0.12,
                 'coilTemperature': 100.0,
                 'holdFraction':    0.50,
                 'openDuration':    60.0})

drive      = valve.calculateDrive()
strategies = valve.compareDriveStrategies()
flyback    = valve.calculateFlyback()
```

A clamp voltage at or below the bus raises, because it would conduct continuously while the valve is driven.

---

## References

- [fluidSystems](../../fluidSystems/), for the valves this drives
- [mechanismsAndSeparation ActuatorsAndDrives](../../mechanismsAndSeparation/docs/ActuatorsAndDrives.md), for the torque margin side
- [PowerQuality](PowerQuality.md), for what inrush and flyback do to the bus
