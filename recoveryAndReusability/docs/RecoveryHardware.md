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

**Those are properties of the vehicle rather than of the recovery system**, and the domain that owns them is [vehicleArchitecture](../../vehicleArchitecture/), whose `StagedVehicle.payloadSensitivity` computes the payload elasticity of a specific vehicle directly. They are inputs here with representative defaults, in the same way that chill-down mass is an input to [groundSystemsAndOperations](../../groundSystemsAndOperations/) rather than a calculation in it.

**What is structural is that dry mass costs more per kilogram than reserve propellant.** A pair of ratios the other way round is a sign convention error rather than an unusual vehicle, and the class refuses it.

---

## Why the transfer orbit penalty is larger

Same recovery hardware, same reserve, and nearly twice the payload penalty.

**The recovery cost is a nearly fixed number of kilograms.** The payload it eats into is not: a transfer orbit mission takes more delta-V and leaves less margin. Expressed as a fraction, the same fixed cost grows.

That is why **boosters are expended on the most demanding missions of an otherwise reusable fleet**, and it is a performance decision rather than an operational one. It is also the same shape as the payload elasticity result in [PerformanceAndPayload](../../vehicleArchitecture/docs/PerformanceAndPayload.md): a vehicle with less margin loses more of it to any fixed cost.

---

## Using a published penalty honestly

The Falcon 9 penalties are published, 18.9 per cent to low orbit and 33.7 per cent to transfer orbit, both from the same source table so the ratio is sourced even though the model behind it is not.

**Tuning the exchange ratios until a bottom-up budget reproduced those figures, and then reporting the agreement, would be calibration rather than validation.** The class does the opposite: it inverts the published penalty and reports the exchange ratios the vehicle must actually have.

On the worked case the budget over-predicts by 25 per cent at low orbit, and the inversion says the vehicle implies 0.240 kg of payload per kilogram of dry mass against the 0.300 assumed. **That is an honest 80 per cent agreement rather than a manufactured exact one.**

**And the over-prediction grows at transfer orbit**, which is itself informative: one pair of exchange ratios cannot cover both missions, because they are properties of the mission as well as of the vehicle.

---

## Worked numbers

A Falcon 9 class first stage, downrange landing.

| Quantity | Value |
|---|---|
| Recovery hardware, counted | 3,100 kg, 14 % of stage dry mass |
| Reserve propellant | 36,981 kg, 9 % of the load |
| Payload cost, hardware | 930 kg |
| Payload cost, reserve | 4,438 kg |
| Reserve against hardware, in payload | **4.8x** |
| Penalty, modelled | 23.5 % |
| Penalty, published | 18.9 % |
| Return to launch site against downrange | 1.7x |

---

## Design rules of thumb

- **Count the hardware, do not fraction it.**
- **Do not forget the thrust structure reinforcement.** It does not look like recovery hardware and it is.
- **Argue about the reserve, not the legs.** It is five times the payload cost.
- **Take the exchange ratios from the mass chain**, per mission, not from a constant.
- **Expect to expend on the hardest missions.** The fixed cost eats a shrinking margin.
- **Invert a published penalty rather than tuning to it.**

---

## Failure modes

**Recovery mass fractioned from dry mass.** It does not converge.

**Reserve propellant left out of the payload penalty.** The larger half is missing.

**One pair of exchange ratios across missions.** They are mission properties too.

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
