[Home](../README.md) > Batteries and Storage

# Batteries and Storage

## Contents

- [Overview](#overview)
- [The two derations](#the-two-derations)
- [What is left of the nameplate](#what-is-left-of-the-nameplate)
- [Rate against energy](#rate-against-energy)
- [Chemistries](#chemistries)
- [Pack against cell](#pack-against-cell)
- [Safety](#safety)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A battery is sized by three numbers and the nameplate capacity is the least interesting of them. This document is mostly about the other two.

---

## The two derations

**Depth of discharge** is a life and reliability limit rather than a physical one. A pack cycled many times is held to about half its capacity; a primary battery used once can go to ninety per cent. That is a factor of nearly two between two batteries with the same label.

**Temperature** is the one that bites on a launch vehicle. A cell cold-soaked at minus twenty delivers about three quarters of its rated capacity, and a vehicle that sized its battery at twenty degrees has lost a quarter of its energy before the count starts.

**Neither is a margin.** They are the difference between what the label says and what the battery does, and a margin sits on top of them. Treating either as conservatism is how a pack ends up a third too small.

---

## What is left of the nameplate

The chain, on the reference stage:

| Step | Energy |
|---|---|
| Delivered to the loads | 270.9 W h |
| Plus 25 per cent margin | 338.6 W h |
| Divided by usable fraction, 68 per cent | **501.6 W h** |

**The nameplate is 1.85 times the energy actually delivered.**

Of that factor, 1.25 is the margin and 1.48 is the deration. The deration is the larger of the two and it is the one that is usually left out of a first estimate.

---

## Rate against energy

Energy and discharge rate are separate budgets and either can govern.

A long low load sizes on energy. A short high load sizes on rate, and a pack sized on energy alone can be physically unable to supply the current.

On the reference stage the peak is 452 W from a 501.6 W h pack, which is 0.90 C against a 3 C limit for lithium ion. **Energy governs, with 3.3 times the rate capability in hand.**

[Battery](BatteriesAndStorage.md) **refuses** a pack that cannot deliver the current rather than reporting a negative margin, because a battery that cannot supply the load is not a battery that is slightly small.

---

## Chemistries

| Chemistry | Specific energy | Rate limit | Cold limit |
|---|---|---|---|
| Lithium ion | 200 W h/kg | 3 C | -20 C |
| Lithium polymer | 180 W h/kg | 10 C | -10 C |
| Silver zinc | 120 W h/kg | 20 C | -20 C |
| Lithium thionyl chloride | 500 W h/kg | 0.1 C | -55 C |

The reference stage across all four:

| Chemistry | Pack mass | Viable |
|---|---|---|
| Lithium thionyl chloride | 1.48 kg | **no** |
| Lithium ion | 3.69 kg | yes |
| Lithium polymer | 4.10 kg | yes |
| Silver zinc | 6.15 kg | yes |

**The lightest option is the one that cannot do the job.** Lithium thionyl chloride has two and a half times the specific energy and a rate limit thirty times too low.

That is the useful result: **the discharge rate decides the chemistry, and it is the only place in the whole calculation where the chemistry choice changes the answer at all.** Everything else, the derations and the margin, applies equally to all of them.

**Silver zinc is worth understanding for a reason that is not on the table.** Its wet life is measured in months, which disqualifies it from almost every application except the one that matters here: a battery that only has to work once, shortly after activation, at a very high rate. That is a launch vehicle, and it is why silver zinc has the heritage it does.

---

## Pack against cell

Specific energy is quoted at cell level. A pack is roughly 68 per cent of it once the case, the interconnects, the management electronics and the thermal hardware are counted.

That fraction is representative and it moves with the design: a pack that needs heaters, cell balancing and a structural case in a vibration environment gives up more than one that does not.

---

## Safety

Stated qualitatively because it is a safety analysis rather than an energy one, and it is not modelled here.

**Thermal runaway** is the lithium failure mode and it is self-sustaining: a cell that goes into runaway heats its neighbours, and the design question is propagation rather than initiation. Cell spacing, thermal barriers and venting paths are the mitigations, and all three cost mass that the specific energy comparison above does not show.

**Over-discharge and over-charge** both damage lithium cells permanently and both are management-system responsibilities.

**Handling and transport** of a charged lithium pack is restricted, and on a small programme that is a schedule constraint rather than a technical one.

The comparison table above is an energy comparison. **A safety comparison would rank them differently**, and silver zinc's persistence on launch vehicles is partly that.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Delivered energy | 270.9 W h |
| Energy margin | 25 % |
| Depth of discharge, single use | 90 % |
| Temperature factor at -20 C | 75 % |
| Usable fraction | 68 % |
| Nameplate required | 501.6 W h |
| Oversize factor | 1.85x |
| Pack mass, lithium ion | 3.69 kg |
| Peak demand | 0.90 C against a 3 C limit |

---

## Design rules of thumb

- **Derate before you margin.** They are different things and the deration is larger.
- **Size at the cold case**, which is the pad rather than the flight.
- **Check the rate separately from the energy.** Either can govern.
- **Let the rate choose the chemistry.** Nothing else in the calculation does.
- **Count the pack fraction.** Cell specific energy is not pack specific energy.

---

## Failure modes

**Depth of discharge treated as margin.** Spends the same allowance twice.

**Sized at room temperature.** A quarter of the capacity missing on a cold pad.

**Sized on energy alone.** The pack cannot supply the current, and the tool refuses it.

**Cell specific energy used for a pack.** A third light.

**Chemistry chosen on specific energy.** The lightest option here cannot do the job.

---

## Tool interface

```python
from Battery import Battery

battery = Battery()
battery.setInputs({'chemistry':     'lithium ion',
                   'busVoltage':    28.0,
                   'missionEnergy': 975.0e3,
                   'peakPower':     452.0,
                   'temperature':   -20.0,
                   'cycleClass':    'single use'})

sized      = battery.sizePack()
rate       = battery.checkDischargeRate()
comparison = battery.compareChemistries()
```

A temperature below the chemistry's low limit raises rather than extrapolating, because the capacity model does not apply there.

---

## References

- [PowerOverview](PowerOverview.md)
- [thermalManagement](../../thermalManagement/), for the battery thermal control this assumes exists
- Cell manufacturer datasheets, which would replace every representative value here
