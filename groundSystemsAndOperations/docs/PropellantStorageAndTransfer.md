[Home](../README.md) > Propellant Storage and Transfer

# Propellant Storage and Transfer

## Contents

- [Overview](#overview)
- [Four things spent before liftoff](#four-things-spent-before-liftoff)
- [The tanking sequence](#the-tanking-sequence)
- [What a scrub costs](#what-a-scrub-costs)
- [Sizing the storage](#sizing-the-storage)
- [Storable propellants are a different problem](#storable-propellants-are-a-different-problem)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The flight load is the number everybody quotes. It is not what the ground system has to supply, and on a cryogenic vehicle the gap is large enough to size the storage tank.

---

## Four things spent before liftoff

None of them reaches an engine.

**Chill-down** conditions the transfer line and the vehicle tank. Every kilogram of it boils and vents. The mass is an enthalpy balance and it is computed by [ChillDown](../../propulsion/ignitionAndStart/) in propulsion, not here: two implementations of one balance eventually disagree.

**Boil-off during the fill**, which runs as long as the tanking does.

**Replenish during the hold**, which runs as long as the hold does. **A hold is a propellant cost as well as a schedule cost**, and the slope is the boil-off rate, which makes it linear and easy to lose track of over a long hold.

**The detank on a scrub**, which returns some of the load to storage and vents the rest. Recovery is only possible where the ground tank can accept warm returning fluid, which is a design decision made long before the scrub happens.

---

## The tanking sequence

Not one flow rate. Four, and the fast fill everybody pictures is a minority of the elapsed time.

| Phase | Rate | Of the load | Purpose |
|---|---|---|---|
| Chill-down | 15% | none | condition the line and the tank |
| Slow fill | 30% | 5% | cover the tank bottom without shocking it or geysering the line |
| Fast fill | 100% | 93% | the bulk of the load |
| Topping | 10% | 2% | reach flight level against the ullage sensor |

**Chill-down dominates the clock**, at 64 per cent of a 102 minute sequence in the worked example, because it runs at a fraction of the transfer rate by necessity: the point of it is to boil.

**Slow fill exists because of two failures at once.** A cold liquid dropped onto a warm tank bottom is a thermal shock, and a partly filled vertical line is where a geyser forms: vapour collects, lifts a slug of liquid, and the slug arrives somewhere as a [water hammer](../../fluidSystems/fluidSystemsLibrary/docs/WaterHammer.md).

**Topping has a floor.** If the topping rate falls below the boil-off, the tank never reaches flight level, and the failure is quiet: the level simply stops rising. The class raises rather than reporting a long duration.

**After topping comes replenish**, which is not a phase with a duration of its own. It lasts as long as the hold.

---

## What a scrub costs

The result this subject exists to produce.

A scrub after tanking loses everything spent on the attempt plus whatever the detank cannot recover, and the next attempt pays the chill-down again from a warm tank. In the worked example that is **0.96 flight loads lost per scrub**, with 55 per cent of the vehicle load recovered.

**That is why storage is sized in loads rather than in kilograms**, and why the number of attempts a campaign can afford is a propellant question before it is a schedule one.

---

## Sizing the storage

Three quantities, and the third is the one that gets forgotten.

**One attempt** is chill-down plus flight load plus boil-off through the fill and the hold. In the worked example that is 1.51 times the flight load.

**The scrubs the campaign has to absorb**, which follows from the launch probability rather than from optimism. See [WeatherAndConstraints](WeatherAndConstraints.md).

**The resupply interval**, which on a hydrogen vehicle at a remote site is usually the turnaround driver and therefore sets the whole campaign. See [LaunchOperations](LaunchOperations.md).

**In the worked example the storage is the binding constraint on the campaign**: the countdown allows eight attempts in fourteen days and the tank supports seven. That is a resupply contract rather than an engineering change, which is a different conversation and a cheaper one.

---

## Storable propellants are a different problem

Everything above is cryogenic. Storables replace the thermal problem with a chemical and toxicological one.

**No chill-down, no boil-off, no replenish**, so a storable vehicle can sit loaded for weeks and the ground demand is close to the flight load.

**In exchange, every operation is a hazardous one.** Hydrazine and nitrogen tetroxide need self-contained breathing apparatus, a scrubber on every vent, a decontamination plan, and a exclusion zone that is toxicological rather than explosive. See [HazardousOperations](HazardousOperations.md) and the [hydrazine](../../fluidSystems/fluidSystemsLibrary/docs/Hydrazine.md) material in fluid systems.

**And a detank is far worse than a scrub.** A cryogenic detank vents to atmosphere. A hypergolic detank moves toxic propellant back through the same connections that just leaked, if any of them did.

---

## Worked numbers

A 5.4 t liquid hydrogen upper stage load, transfer at 3.2 kg/s, boil-off at 0.11 kg/s.

| Quantity | Value |
|---|---|
| Chill-down | 1,900 kg, 35% of the flight load |
| Boil-off through the fill | 676 kg |
| Replenish through a 30 minute hold | 198 kg |
| One attempt, total | 8,174 kg, 1.51 flight loads |
| Tanking duration | 102 min, 64% of it chill-down |
| Two hours of hold | 792 kg, 15% of the flight load |
| Lost on a scrub | 5,204 kg, 0.96 flight loads |
| Attempts supported by 42 t of storage | 7 |

---

## Design rules of thumb

- **Size the storage in loads, not kilograms.** A campaign is measured in attempts.
- **Take the chill-down mass from the enthalpy balance**, not from a fraction. For hydrogen the bounds differ by a factor of nine.
- **Cost a hold in propellant as well as in minutes.**
- **Check the topping rate against the boil-off.** Below it the tank never fills, quietly.
- **Decide whether the ground tank can take a warm detank return** before you need it to.
- **On a storable vehicle, count the hazardous operations rather than the kilograms.**

---

## Failure modes

**Ground demand estimated as the flight load.** Half again as much, and a scrub costs another whole one.

**Chill-down taken as a fraction.** The hydrogen bounds are a factor of nine apart.

**A hold costed only in schedule.** It is a mass, and it is linear in duration.

**Topping below the boil-off.** The level stops rising and nothing announces it.

**A detank plan written after the scrub.** The recovery fraction is a tank design decision, not an operational one.

---

## Tool interface

```python
from PropellantLoading import PropellantLoading

loading = PropellantLoading()
loading.setInputs({'flightLoad':      5400.0,
                   'transferRate':    3.2,
                   'chilldownMass':   1900.0,    # from propulsion/ignitionAndStart/ChillDown
                   'boilOffRate':     0.11,      # from fluidSystems/Insulation
                   'holdDuration':    1800.0,
                   'storageCapacity': 42000.0,
                   'detankRecovery':  0.55})

sequence    = loading.calculatePhases()
demand      = loading.calculateGroundDemand()
scrub       = loading.scrubCost()
sensitivity = loading.holdSensitivity()
```

---

## References

- [ChillDown](../../propulsion/ignitionAndStart/), which computes the conditioning mass and its bounds
- [Insulation](../../fluidSystems/fluidSystemsLibrary/docs/Insulation.md), which computes the boil-off rate
- [CryogenicSystems](../../fluidSystems/fluidSystemsLibrary/docs/CryogenicSystems.md), for the system view
- [WaterHammer](../../fluidSystems/fluidSystemsLibrary/docs/WaterHammer.md), for what a geyser produces
