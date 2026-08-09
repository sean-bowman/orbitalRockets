[Home](../README.md) > Mass Fractions and Estimating

# Mass Fractions and Estimating

## Contents

- [Overview](#overview)
- [Where a mass estimate comes from](#where-a-mass-estimate-comes-from)
- [Growth allowance is not margin](#growth-allowance-is-not-margin)
- [The three numbers a budget has](#the-three-numbers-a-budget-has)
- [Structural coefficient bands](#structural-coefficient-bands)
- [The non-tank fraction, which is doing too much work](#the-non-tank-fraction-which-is-doing-too-much-work)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Every subsystem mass estimate is wrong. The question is by how much, in which direction, and whether the budget says so.

---

## Where a mass estimate comes from

Four sources, in ascending order of confidence, and the ordering is what the growth allowance encodes.

**A scaling relationship.** Mass as a function of some driving parameter, fitted to historical hardware. Fast, and it is a statement about the historical fleet rather than about this design.

**An analysis of a defined configuration.** A tank wall from a pressure and a radius, which is what [SizingLoop](MassChain.md) does. Better, and it covers only what has been defined: no brackets, no fasteners, no insulation.

**A preliminary design with drawings.** Most of the parts exist on paper.

**A released drawing set.** Everything exists and the remaining growth is manufacturing.

And then **a weighed article**, which carries no allowance because it is not an estimate.

---

## Growth allowance is not margin

This is the distinction the domain makes most loudly, because confusing the two is how a programme discovers it has neither.

**Growth allowance covers what an estimate is expected to become.** It is a statistical statement about estimating at a given maturity: numbers from a scaling relationship have historically grown by about a quarter, numbers from a released drawing set by about a twentieth. It is not conservatism and it is not optional. **It is part of the estimate.**

**Margin covers what is not known at all.** The requirement that changes, the interface that turns out heavier, the qualification failure that needs a doubler. It is a management reserve and it is held at programme level rather than distributed into line items.

The two are added, not chosen between.

| Maturity | Growth allowance |
|---|---|
| Estimated | 25 % |
| Calculated | 15 % |
| Preliminary | 10 % |
| Detailed | 5 % |
| Actual | 0 % |

---

## The three numbers a budget has

```
estimate    what the hardware is currently believed to weigh
predicted   estimate plus growth allowance: what it is expected to weigh
required    predicted plus margin: what the allocation has to cover
```

A budget that closes on `estimate` and not on `predicted` **has not closed**, and comparing an estimate against an allocation is the commonest way a budget looks healthier than it is.

A budget that closes on `predicted` and not on `required` has closed with no reserve. That is a legitimate position late in a programme and it is not one at concept.

On the worked example's avionics assembly: 172 kg estimated against a 210 kg allocation looks like 38 kg of margin. **31 kg of it is growth allowance.** The real reserve is 7 kg, and spending the allowance as margin leaves the programme with neither.

---

## Structural coefficient bands

The stage-level version of the same estimating problem.

| Architecture | Coefficient |
|---|---|
| Kerolox booster | 0.045 to 0.070 |
| Kerolox upper stage | 0.030 to 0.055 |
| Hydrolox upper stage | 0.080 to 0.120 |
| Pressure fed | 0.080 to 0.150 |

Falcon 9's published stages come out at 0.0513 and 0.0359, both inside their bands, which is a weak but real check that the bands are the right shape.

**Hydrogen is bulky and the tank pays for it.** A hydrolox upper stage carries twice the structural coefficient of a kerolox one and still wins, because the specific impulse gain is larger than the structural loss. That trade is the clearest case in vehicle design of a worse mass fraction being the right answer.

---

## The non-tank fraction, which is doing too much work

[SizingLoop](MassChain.md) computes the tank from a real pressure vessel model and then adds everything else as a single fraction of propellant mass: engines, thrust structure, avionics, feed lines, separation hardware, skirts.

**That constant is doing as much work as the tank model, and unlike the tank model it is a constant rather than a calculation.**

It is registered as unvalidated, and it is the most tractable gap in the whole repository's register: every part of it is owned by a domain already built. Engine mass from [propulsion](../../propulsion/), thrust structure from [aerospaceStructures](../../aerospaceStructures/), feed lines from [fluidSystems](../../fluidSystems/). Assembling it rather than assuming it is a well-defined piece of work that has not been done.

---

## Worked numbers

The avionics assembly from the worked example.

| Item | Maturity | Estimate | Growth | Predicted |
|---|---|---|---|---|
| Flight computer | preliminary | 12.0 kg | 10 % | 13.2 kg |
| Harness | estimated | 38.0 kg | 25 % | 47.5 kg |
| Batteries | calculated | 46.0 kg | 15 % | 52.9 kg |
| Telemetry and comms | estimated | 22.0 kg | 25 % | 27.5 kg |
| Thrust vector actuators | calculated | 54.0 kg | 15 % | 62.1 kg |
| **Total** | | **172.0 kg** | **18.1 %** | **203.2 kg** |

Allocation 210 kg. Margin at 15 per cent adds 30 kg, so the requirement is 234 kg. **It does not close.**

---

## Design rules of thumb

- **Carry a maturity with every line item.** A mass without one cannot carry an allowance and is not a budget entry.
- **Compare the prediction against the allocation**, never the estimate.
- **Hold margin at programme level.** Distributed margin gets spent locally.
- **Do not spend the growth allowance.** It is the estimate, not a reserve.
- **Re-baseline the allowance as maturity rises**, and expect the predicted mass to fall as it does.

---

## Failure modes

**Estimate compared against allocation.** Looks like margin, is growth allowance.

**Margin distributed into line items.** It gets spent by whoever holds it.

**A budget with no maturities.** Cannot carry an allowance, so it is a list rather than a budget.

**Duplicate line items.** Counted twice or dropped, and neither shows as an error. [MassBudget](MassFractionsAndEstimating.md) refuses them.

**A single constant standing in for half a stage.** The non-tank fraction, named above.

---

## Tool interface

```python
from MassBudget import MassBudget

budget = MassBudget()
budget.setInputs({'items': [{'name': 'harness', 'mass': 38.0, 'maturity': 'estimated',
                             'station': 2.0}],
                  'allocatedMass':  210.0,
                  'programmePhase': 'preliminary'})

rollup = budget.rollUp()
margin = budget.checkMargin()

print(budget.generateReport())
```

---

## References

- AIAA S-120 and the ANSI/AIAA mass properties standards, for the growth allowance practice this follows in shape
- [MassChain](MassChain.md), for where the stage masses come from
- Humble, Henry and Larson, *Space Propulsion Analysis and Design*
