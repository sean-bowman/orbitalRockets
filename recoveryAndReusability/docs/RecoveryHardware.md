[Home](../README.md) > Recovery Hardware

# Recovery Hardware

## Contents

- [Overview](#overview)
- [Two things are given up](#two-things-are-given-up)
- [The hardware](#the-hardware)
- [The reserve](#the-reserve)
- [What each costs in payload](#what-each-costs-in-payload)
- [Why the transfer orbit penalty is larger](#why-the-transfer-orbit-penalty-is-larger)
- [Using a published penalty honestly](#using-a-published-penalty-honestly)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Recovery hardware is a payload penalty paid on every flight, including the ones that do not come back. This document is about what makes it up and which half of it is the expensive one.

---

## Two things are given up

**Propellant that could have accelerated the payload**, spent on boost-back, entry and landing burns.

**Dry mass carried the whole way up**: legs, fins, avionics and the structure to react landing loads.

They do not cost the same per kilogram. **Dry mass is carried through the entire first stage burn and the reserve is burned at the end of it**, so a kilogram of leg costs more payload than a kilogram of reserve. A budget that adds the two without weighting is missing that.

**But the reserve is the larger cost anyway**, because there is so much more of it. On the worked case the reserve is twelve times the hardware by mass and costs nearly five times the payload.

---

## The hardware

Counted rather than fractioned, for the same reason a [harness](../../electricalPower/docs/HarnessDesign.md) is: **a counted estimate converges as the design matures and a fractional one does not.**

| Item | Share of recovery mass | Note |
|---|---|---|
| Landing legs | ~68 % | the dominant term, and it scales with footprint |
| Grid fins | ~15 % | titanium if they are to be reused without refurbishment |
| Entry and landing avionics | ~5 % | a second flight computer set and its power |
| Thrust structure reinforcement | ~13 % | the landing load has to go somewhere |

**The legs dominate**, and they dominate because [tipover](DescentAndLanding.md) demands a wide footprint and a wide footprint demands long legs. Reducing leg mass is a tipover conversation, not a materials one.

**The reinforcement is the term most often forgotten**, because it does not look like recovery hardware. It exists only because the stage lands.

---

## The reserve

| Mode | Reserve | Hardware | Note |
|---|---|---|---|
| Expended | 0 % | 0 % | the baseline everything is measured against |
| Parachute and splashdown | 0 % | ~6 % | salt water instead of propellant |
| Downrange landing | ~9 % | ~9 % | entry burn and landing burn |
| Return to launch site | ~17 % | ~9 % | boost-back as well, and it is the largest single term |

**The ordering is structural rather than numerical.** A return to the launch site has to cancel the downrange velocity and then reverse it, so it costs roughly twice the reserve of a downrange landing. That holds for any values, which is why it is worth stating separately from the numbers.

**Boost-back is the term that makes return to launch site expensive**, and it is bought for operational convenience: no ship, no transport back, no sea state. Whether that is worth roughly double the reserve is a fleet decision rather than a vehicle one.

---

## What each costs in payload

The conversion is an exchange ratio: payload lost per kilogram of stage dry mass, and per kilogram of reserve.

**Those are properties of the vehicle rather than of the recovery system**, and the domain that owns them is [vehicleArchitecture](../../vehicleArchitecture/), whose `StagedVehicle.exchangeRatios` computes both from the rocket equation on a specific stack. They remain inputs here so a budget can be written for any stage, and the worked case takes them from that method rather than from a constant.

**The reserve is the more expensive of the two per kilogram**, and the reason is not the intuitive one. Both are aboard for the whole ascent burn: a recovery reserve is spent after separation, not during the climb. What separates them is that added dry mass raises the first stage initial mass and its burnout mass together, while reserved propellant is already aboard and raises the burnout mass alone. Differentiating the stage contribution `c ln(I/F)`:

```
d(dV)/d(dry)      = c (1/I - 1/F)
d(dV)/d(reserve)  = -c / F

dry / reserve     = 1 - F/I = 1 - 1/R
```

**That is exact, and it is below one for any stage that burns any propellant at all.** So reserve propellant costs more payload per kilogram than dry mass on every vehicle, and relatively more the smaller the mass ratio of the stage carrying it. On the worked case `R` is 3.63, the closed form is 0.724, and the numerically measured ratio is 0.724.

**This domain had that ordering backwards** until the two libraries were wired together, with a plausible reason written down beside it: that a reserve is carried for less of the burn than a landing leg. It is not, and the class guard that enforced the old ordering would have rejected the correct pair. A pair the other way round is now refused for the opposite reason.

---

## Why the transfer orbit penalty is larger

Same recovery hardware, same reserve, and nearly twice the payload penalty.

**The recovery cost is a nearly fixed number of kilograms.** The payload it eats into is not: a transfer orbit mission takes more delta-V and leaves less margin. Expressed as a fraction, the same fixed cost grows.

That is why **boosters are expended on the most demanding missions of an otherwise reusable fleet**, and it is a performance decision rather than an operational one. It is also the same shape as the payload elasticity result in [PerformanceAndPayload](../../vehicleArchitecture/docs/PerformanceAndPayload.md): a vehicle with less margin loses more of it to any fixed cost.

---

## Using a published penalty honestly

The Falcon 9 penalties are published, 18.9 per cent to low orbit and 33.7 per cent to transfer orbit, both from the same source table so the ratio is sourced even though the model behind it is not.

**Tuning the exchange ratios until a bottom-up budget reproduced those figures, and then reporting the agreement, would be calibration rather than validation.** The class does the opposite, and it can now do it better than it could: with both exchange ratios computed from the vehicle, the budget has exactly one free quantity left and it is the one this domain owns.

**Inverting the low orbit penalty says the stage holds back 6.2 per cent of its propellant load, not the 9 per cent assumed.** The counted hardware is only 8 per cent of the bill, which is the more useful half of that result: a recovery budget is mostly a statement about propellant, and the propellant is the part nobody weighs.

**An inverted number is only worth having if it survives being turned back into what it describes.** Through the rocket equation on a landed mass of 25,300 kg, a 6.2 per cent reserve buys 1,937 m/s, which is an entry burn and a landing burn without boost-back. The 9 per cent assumption needs 2,491 m/s, which is more descent than that profile flies. **That check is what separates a descent profile from an artefact of the arithmetic.**

**And the over-prediction grows at transfer orbit.** The exchange ratios are no longer the suspect for that: they are computed from the stack, and the transfer orbit stack is a different one, flown to a different staging velocity with a different reserve.

---

## Worked numbers

A Falcon 9 class first stage, downrange landing.

| Quantity | Value |
|---|---|
| Recovery hardware, counted | 3,100 kg, 14 % of stage dry mass |
| Reserve propellant, assumed | 36,981 kg, 9 % of the load |
| Exchange ratio, dry mass | 0.1115 kg payload per kg |
| Exchange ratio, reserve | 0.1540 kg payload per kg |
| First stage mass ratio | 3.63 |
| Ratio of the two, measured against `1 - 1/R` | 0.7242 against 0.7242 |
| Payload cost, hardware | 346 kg |
| Payload cost, reserve | 5,696 kg |
| Reserve against hardware, in payload | **16.5x** |
| Penalty, modelled | 26.5 % |
| Penalty, published | 18.9 % |
| Reserve implied by the published penalty | 6.2 % of the load, 1,937 m/s |
| Return to launch site against downrange | 1.8x |

---

## Design rules of thumb

- **Count the hardware, do not fraction it.**
- **Do not forget the thrust structure reinforcement.** It does not look like recovery hardware and it is.
- **Argue about the reserve, not the legs.** It is five times the payload cost.
- **Take the exchange ratios from the mass chain**, per mission, not from a constant. They are a one-line calculation on a stack that already exists.
- **Expect to expend on the hardest missions.** The fixed cost eats a shrinking margin.
- **Invert a published penalty rather than tuning to it.**

---

## Failure modes

**Recovery mass fractioned from dry mass.** It does not converge.

**Reserve propellant left out of the payload penalty.** The larger half is missing.

**One pair of exchange ratios across missions.** They belong to a stack flown to a staging velocity, and a transfer orbit mission is a different one.

**Reserve propellant assumed cheaper than dry mass because it gets burned.** It does not get burned during the ascent: it is spent after separation. Dry mass is the cheaper of the two, and for a different reason.

**Boost-back costed as operational convenience only.** It is roughly double the reserve.

**A budget tuned to a published penalty.** That is calibration and it should be labelled as such.

---

## Tool interface

```python
from RecoveryBudget import RecoveryBudget

budget = RecoveryBudget()
budget.setInputs({'stageDryMass':    22200.0,
                  'stagePropellant': 410900.0,
                  'baselinePayload': 22800.0,
                  'mode':            'downrangeLanding',
                  'hardwareItems':   {'landing legs': 2100.0, 'grid fins': 450.0}})

penalty     = budget.calculatePenalty()
modes       = budget.compareModes()
sensitivity = budget.missionSensitivity([22800.0, 8300.0])
implied     = budget.impliedExchangeRatios(4300.0)
```

---

## References

- [ReusabilityImpacts](../../vehicleArchitecture/docs/ReusabilityImpacts.md), which owns the published penalty
- [PerformanceAndPayload](../../vehicleArchitecture/docs/PerformanceAndPayload.md), for the elasticity argument
- [HarnessDesign](../../electricalPower/docs/HarnessDesign.md), for the counting rather than fractioning argument
- [ValidationReferences](ValidationReferences.md)
