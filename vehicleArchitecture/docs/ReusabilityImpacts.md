[Home](../README.md) > Reusability Impacts

# Reusability Impacts

## Contents

- [Overview](#overview)
- [The penalty, measured](#the-penalty-measured)
- [Why the GTO penalty is larger](#why-the-gto-penalty-is-larger)
- [Where the penalty comes from](#where-the-penalty-comes-from)
- [What the trade actually is](#what-the-trade-actually-is)
- [What this domain does not model](#what-this-domain-does-not-model)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Recovery hardware is a payload penalty paid on every flight, and the interesting thing about it is that the penalty is published, so it does not have to be modelled.

---

## The penalty, measured

Falcon 9 Block 5, both figures from the same source table.

| Orbit | Expended | Reusable | Penalty |
|---|---|---|---|
| LEO, 28.5 degrees | 22,800 kg | 18,500 kg | **18.9 %** |
| GTO, 27 degrees | 8,300 kg | 5,500 kg | **33.7 %** |

**Neither number is something this repository can reproduce**, because recovery propellant, entry burn, landing burn and the aerodynamic hardware are all outside it. But both come from one table, so **the ratio is a sourced quantity even though the model behind it is not.**

That makes this one of the cleaner validation situations in the repository: a measured outcome with no model to disagree with.

---

## Why the GTO penalty is larger

Same recovery hardware, same recovery propellant, and nearly twice the payload penalty.

The recovery reserve is a roughly fixed quantity of first stage propellant and mass. **On a GTO mission that fixed quantity is a larger share of a smaller performance margin**, because the mission takes more delta-V and leaves less to give.

The general form: **the recovery penalty as a fraction of payload rises as the mission gets harder**, which is the same shape as the payload elasticity result in [PerformanceAndPayload](PerformanceAndPayload.md). A vehicle with less margin loses more of it to any fixed cost.

That is why boosters are expended on the most demanding missions of an otherwise reusable fleet, and it is a performance decision rather than an operational one.

---

## Where the penalty comes from

Four contributions, none of them modelled here, in rough order of size for a propulsive return.

**Recovery propellant.** Boost-back, entry burn and landing burn. The largest term, and it is first stage propellant that does not accelerate the payload.

**Landing hardware.** Legs and grid fins, which are dry mass on the stage that stays with it through the whole first stage burn.

**Thermal protection.** Whatever the entry environment requires.

**Structural margin for reuse.** A stage flown once is designed to a life of one. A stage flown ten times is designed to a fatigue life, and that is mass.

The last one is the one most often forgotten in a conceptual trade, and it belongs to [aerospaceMaterials](../../aerospaceMaterials/) and [reliabilityAndMissionAssurance](../../reliabilityAndMissionAssurance/) rather than here.

---

## What the trade actually is

**Not payload against payload.** Cost per kilogram against cost per kilogram, over a fleet life.

A 19 per cent payload penalty is worth paying if the stage flies enough times, and the break-even depends on refurbishment cost and flight rate, neither of which is a mass. **A reusability trade decided on mass alone will always say no**, because the mass penalty is real and immediate and the saving is neither.

This domain can price the mass side exactly and cannot price the other side at all, and stating that is more useful than producing a break-even number from assumed costs.

---

## What this domain does not model

Everything except the mass penalty, and the mass penalty is taken from a published outcome rather than computed.

**No recovery trajectory.** Boost-back and entry are trajectory problems and this domain does not integrate trajectories. See [TrajectoryBasics](TrajectoryBasics.md).

**No refurbishment cost or flight rate.** The other half of the trade.

**No fatigue life.** The structural margin for reuse.

**No recovery mode comparison.** Propulsive against winged against parachute is a whole design space and it belongs to [recoveryAndReusability](../../recoveryAndReusability/).

---

## Worked numbers

| Quantity | Value |
|---|---|
| LEO payload penalty | 18.9 % |
| GTO payload penalty | 33.7 % |
| Ratio between them | 1.78 |
| Source | One published table, both figures |

---

## Design rules of thumb

- **Use the measured penalty** where one exists. It beats a model of four unmodelled contributions.
- **Expect the penalty to rise with mission difficulty.** Fixed cost, shrinking margin.
- **Do not decide reuse on mass.** The mass side always says no.
- **Count the fatigue margin.** Designing for ten flights is not free and it is usually forgotten.
- **Expend the booster on the hardest missions** if the fleet allows it.

---

## Failure modes

**A reusability trade closed on mass.** It cannot be, and the answer it gives is always the same one.

**A LEO penalty applied to a GTO mission.** It is nearly twice as large.

**Recovery propellant counted and reuse structural margin forgotten.** The second is invisible until a fatigue analysis exists.

**A break-even computed from assumed refurbishment costs.** The assumption is the whole answer.

---

## References

- [ValidationReferences](ValidationReferences.md), for the published penalty
- [recoveryAndReusability](../../recoveryAndReusability/), which owns the recovery design
- [PerformanceAndPayload](PerformanceAndPayload.md), for why a fixed cost hurts a marginal vehicle more
