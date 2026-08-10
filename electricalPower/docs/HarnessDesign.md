[Home](../README.md) > Harness Design

# Harness Design

## Contents

- [Overview](#overview)
- [The AWG definition](#the-awg-definition)
- [Two constraints, and which one binds](#two-constraints-and-which-one-binds)
- [Derating](#derating)
- [Bus voltage against copper](#bus-voltage-against-copper)
- [Mass, counted rather than fractioned](#mass-counted-rather-than-fractioned)
- [Connectors](#connectors)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Harnessing is reliably underestimated in mass and in schedule, and the gauge is reliably chosen on the wrong constraint. Both are avoidable and neither is difficult.

---

## The AWG definition

Wire gauge is defined rather than tabulated:

```
d(n) = 0.127 mm * 92 ** ((36 - n) / 39)
```

36 AWG is exactly 0.005 inches and each step multiplies the diameter by the 39th root of 92. With the standard copper resistivity of 1.724e-8 ohm m, every wire resistance in this library is computed rather than looked up, and it **reproduces published resistance tables to four significant figures**.

That is the tightest agreement anywhere in this repository, and it matters because the domain's central result rests on a resistance calculation. See [ValidationReferences](ValidationReferences.md).

Three useful consequences of the definition: three gauge steps double the area, six steps quadruple it, and ten steps are a factor of ten in resistance.

---

## Two constraints, and which one binds

**Ampacity** is a thermal limit: current heats the conductor and the insulation has a temperature limit. It does not depend on length.

**Voltage drop** is what arrives at the load:

```
dV = 2 * R * I
```

The factor of two is the part that gets forgotten. Current goes out along one wire and returns along another, so the loop resistance is twice the one-way resistance unless the return is through structure.

On the reference run, 3 A over 12 m on a 28 V bus:

| Constraint | Gauge |
|---|---|
| Ampacity, after derating | 20 AWG |
| Voltage drop, 3 per cent limit | **14 AWG** |

**Six gauge steps and four times the copper.** A harness sized on ampacity would deliver 25.1 V to a 28 V load, and would not function.

The reason is geometry rather than electricity. **A launch vehicle harness is long relative to its currents**, so voltage drop scales with length and ampacity does not. A short high-current run inverts it, and the tool reports both so the binding constraint is visible rather than inferred.

---

## Derating

The free-air ampacity is not the installed ampacity, and two factors come off it.

**Bundle derating** is the larger and the one most often forgotten. A wire in the middle of a harness cannot shed heat to anywhere except its neighbours, which are also warm. A wire in a bundle of thirty carries under half its free-air rating.

**Altitude derating** follows from air density: convective cooling falls, and above the atmosphere the only paths are conduction along the wire and radiation.

Both are given as curves in SAE AS50881, which is not openly available, so the values in this library are representative and registered as unvalidated. **The conclusion above does not rest on them**: the derating would have to be wrong by several gauge steps to change which constraint binds.

---

## Bus voltage against copper

Power is fixed, so raising the bus voltage does two things at once: the current falls, and the allowed drop in volts rises. Both reduce the copper required.

| Bus | Current | Governing gauge | Copper area |
|---|---|---|---|
| 12 V | 7.0 A | **does not close** | |
| 28 V | 3.00 A | 14 AWG | 2.08 mm^2 |
| 50 V | 1.68 A | 18 AWG | 0.82 mm^2 |
| 100 V | 0.84 A | 24 AWG | 0.20 mm^2 |

**Copper falls roughly with the square of bus voltage**, and on this run a 12 V bus cannot close at all. That is the cleanest single argument for a higher bus, and it is why anything with a long harness runs above 28 V.

What it trades against is insulation, creepage and clearance, arc risk in a partial vacuum, and the availability of components. Those are real and they are not modelled here.

---

## Mass, counted rather than fractioned

**Harness mass is always more than estimated**, and the reason is the estimating method rather than the harness.

A harness estimated as a percentage of dry mass grows every time the vehicle does and never converges, because the thing it is a fraction of is not what drives it. What drives it is run length, conductor count, gauge and connector count, and all four are countable early.

The count needs three things a straight-line estimate leaves out:

**A routing allowance**, because a wire never goes where the straight line goes. Twenty per cent is representative, and leaving it out entirely is a large part of the underestimate.

**Insulation mass**, which is a larger fraction on small gauges: a 24 AWG wire is more than twice its bare copper mass once insulated, and a 10 AWG wire is about a third more.

**Connectors**, which are 22 per cent of the reference harness.

---

## Connectors

**Connector count is the best available reliability proxy for a harness.** Every one is a set of contacts that can be mis-mated, back-driven, contaminated or fretted, and the failure rate scales with the count far more directly than with wire length.

So the number is worth tracking for a reason other than mass, and a design decision that removes a connector is worth more than its mass suggests.

The counter-pressure is testability and assembly: a harness with no connectors cannot be built in sections, tested in sections, or replaced in sections. **The right count is not the minimum**, and there is no formula for it in this library.

---

## Worked numbers

The reference run and harness.

| Quantity | Value |
|---|---|
| Current | 3.0 A |
| Length | 12 m |
| Bundle | 15 wires |
| Altitude | 30 km |
| Ampacity gauge | 20 AWG |
| Voltage drop gauge | 14 AWG |
| Drop at 14 AWG | 0.71 V, 2.5 % |
| Wire mass | 6.34 kg |
| Connector mass | 1.78 kg, 25 connectors |
| Total | 8.12 kg |

---

## Design rules of thumb

- **Size on voltage drop first**, then check ampacity.
- **Count both conductors.** The factor of two is the commonest arithmetic slip here.
- **Derate for the bundle before the altitude.** Bundle is the larger effect.
- **Count the harness from runs and connectors**, with a routing allowance.
- **Raise the bus if the runs are long.** Copper falls with the square of voltage.

---

## Failure modes

**Gauge sized on ampacity.** The load sits several per cent low and nobody knows why.

**One-way resistance used for the drop.** Half the real number.

**Free-air ampacity used in a bundle.** More than double the real rating.

**Harness mass as a fraction of dry mass.** Never converges, and always low.

**Routing allowance omitted.** The single largest contributor to the underestimate.

**Connector count minimised.** Trades reliability against testability, and the minimum is not the answer.

---

## Tool interface

```python
from HarnessSizing import HarnessSizing

harness = HarnessSizing()
harness.setInputs({'busVoltage': 28.0,
                   'current':    3.0,
                   'length':     12.0,
                   'bundleSize': 15,
                   'altitude':   30000.0})

sized  = harness.sizeGauge()
mass   = harness.calculateMass([{'gauge': 14, 'length': 12.0, 'count': 2}],
                               {'circular, 8 way': 12})
buses  = harness.compareBusVoltage()
```

`sizeGauge()` raises when no candidate satisfies either constraint, and the message names which one and what to do about it.

---

## References

- [ValidationReferences](ValidationReferences.md), for the AWG anchor
- SAE AS50881, *Wiring Aerospace Vehicle*, for the derating curves, not read here
- [vehicleArchitecture MassChain](../../vehicleArchitecture/docs/MassChain.md), for what harness mass costs at liftoff
