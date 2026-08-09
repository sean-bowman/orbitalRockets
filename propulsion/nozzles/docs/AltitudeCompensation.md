[Home](../README.md) > Altitude Compensation

# Altitude Compensation

## Contents

- [Overview](#overview)
- [The size of the prize](#the-size-of-the-prize)
- [Where the prize actually is](#where-the-prize-actually-is)
- [The arrangements](#the-arrangements)
- [Why the aerospike has not flown](#why-the-aerospike-has-not-flown)
- [Why the extendible nozzle has](#why-the-extendible-nozzle-has)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [What is not validated](#what-is-not-validated)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A fixed nozzle is optimally expanded at exactly one altitude and losing performance everywhere else. A first stage climbs through two orders of magnitude of ambient pressure during its burn, so the loss is real.

Altitude compensation is the oldest unclaimed prize in propulsion. It has been understood since the 1950s, several schemes exist, and **no operational vehicle has captured more than a fraction of it.**

---

## The size of the prize

The upper bound is what a nozzle expanding exactly to ambient at every altitude would deliver. No real device reaches it, and knowing it is what makes the subject tractable: an arrangement costing more than this in mass cannot pay for itself however well it compensates.

For the reference booster:

| | Burn-averaged `Isp` |
|---|---|
| Fixed bell at an area ratio of 20.35 | 308.0 s |
| Perfectly compensating | 322.5 s |
| **The prize** | **14.5 s, 4.7 %** |

Large enough to be worth chasing. Small enough that every scheme for capturing it has so far lost more in mass, cooling or complexity than it gained.

---

## Where the prize actually is

The result worth carrying away, and it is the opposite of the intuition.

| Altitude [km] | Fixed [s] | Ideal [s] | Gap [s] |
|---|---|---|---|
| 0 | 282.7 | 288.9 | 6.2 |
| 3 | 294.0 | 295.7 | 1.7 |
| 8 | 306.6 | 306.8 | 0.2 |
| 15 | 315.1 | 321.1 | 6.0 |
| 25 | 318.6 | 336.5 | 17.9 |
| 38 | 319.4 | 349.4 | 30.0 |
| 55 | 319.5 | 359.1 | **39.6** |

**The gap is 6.2 s at sea level and 39.6 s at the top, a factor of six.**

A fixed nozzle's *visible* problem at sea level is over-expansion. That is what causes separation, what produces side loads, and what gets the attention. Its *performance* loss is dominated by under-expansion high up, where nothing dramatic happens and the nozzle is simply too small.

The zero crossing at 8 km is the design point: that is the one altitude where the fixed nozzle is right.

This reframes what compensation is for. **A device that only fixed the sea level over-expansion would capture almost none of the prize.** The value is in being larger at altitude, not smaller at sea level.

---

## The arrangements

| Arrangement | Recovers | Gain | Mass penalty | Flown operationally |
|---|---|---|---|---|
| Fixed bell | 0 % | 0 s | 0 % | Yes |
| Extendible | 55 % | 8.0 s | 25 % | **Yes** |
| Dual bell | 45 % | 6.5 s | 15 % | No |
| Aerospike | 70 % | 10.2 s | 80 % | No |

The recovery fractions and mass penalties are representative rather than sourced and are registered as unvalidated. **What they encode is an ordering.**

**The best performing arrangement has never flown operationally.** That is the honest shape of the subject and it has been true for seventy years.

---

## Why the aerospike has not flown

It compensates continuously and it is the highest performing arrangement on paper. The reasons it has not flown are not aerodynamic.

**Cooling.** A bell nozzle has a wall with hot gas on one side and coolant on the other. An aerospike has a centrebody with hot gas on the *outside* over its whole length, and the surface area is large, and it is in the worst possible place thermally. This is the dominant reason.

**Mass.** The centrebody is structure that a bell does not have, and it is hot structure.

**Truncation.** A full spike is impractically long, so real designs truncate it and accept a base flow region. That base does not compensate and it is a real loss, which is part of why the recovery is around seventy per cent rather than higher.

**Test difficulty.** A bell can be tested at sea level with a known separation behaviour. An aerospike's whole claim is that it behaves differently at different altitudes, and demonstrating that needs altitude facilities.

---

## Why the extendible nozzle has

It is the one compensating arrangement in operational service, and it works because **it solves an easier problem.**

It is not continuous compensation. It is two area ratios with a single transition, and the transition happens **once, in vacuum, on an upper stage.** There is no unsteady transition through the atmosphere, no separation to manage during the change, and no requirement to work at intermediate conditions.

The mechanism is a deployable extension that translates aft after staging. RL10-B-2 does this with a carbon-carbon extension and reaches an area ratio of 285, which would be unusable on the ground.

**The lesson generalises.** The compensating arrangements that work are the ones that avoid the hard part of the problem rather than solving it.

---

## Design rules of thumb

- **Compute the bound before evaluating any device.** It caps what any of them can be worth.
- **Look at where the gap is**, not at the total. It is at altitude, not at sea level.
- **Do not size a compensating device to fix sea level over-expansion.** That is not where the prize is.
- **Consider an extendible nozzle on an upper stage.** It is the arrangement that works.
- **Cost an aerospike's cooling before its aerodynamics.** That is what has stopped it.
- **Treat the recovery fractions as an ordering**, not as predictions.

---

## Failure modes

**The prize assumed to be at sea level.** It is at altitude by a factor of six.

**An aerospike evaluated on aerodynamics alone.** Cooling is what has kept it grounded.

**A truncated spike credited with full compensation.** The base flow does not compensate.

**A dual bell's transition assumed clean.** It is unsteady and it is why the arrangement has not flown.

**A compensating device costing more mass than the bound is worth.** It cannot pay for itself however well it works.

---

## Worked numbers

The reference booster, LOX/RP-1 at 10 MPa, fixed area ratio 20.35, over a representative first stage ascent.

| Quantity | Value |
|---|---|
| Fixed bell burn average | 308.0 s |
| Perfectly compensating | 322.5 s |
| The prize | 14.5 s, 4.7 % |
| Gap at sea level | 6.2 s |
| Gap at 55 km | 39.6 s |
| Ratio | 6.4 |
| Zero crossing, the design altitude | about 8 km |
| Aerospike gain at 70 per cent recovery | 10.2 s |
| Extendible gain at 55 per cent recovery | 8.0 s |

---

## What is not validated

**The recovery fractions.** Representative figures encoding an ordering, not predictions for a specific device.

**The mass penalties.** The same.

Both are registered in [validation/referenceCases.py](../../../validation/referenceCases.py). The **bound** is computed rather than assumed, and it is the part of this document that does not depend on either.

---

## Standards

| Standard | What it gives you |
|---|---|
| NASA SP-8120 | Liquid rocket engine nozzles |
| Sutton and Biblarz | The altitude compensation survey |
| Hagemann et al. | Advanced rocket nozzles, the modern review |

---

## Tool interface

```python
from AltitudeCompensation import AltitudeCompensation

compensation = AltitudeCompensation()
compensation.setInputs({'combination':     'LOX/RP-1',
                        'chamberPressure': 10.0e6,
                        'areaRatio':       20.35})

bound = compensation.calculateIdealBenefit()
print(bound['benefit'], bound['benefitFraction'])

for name, entry in compensation.compareArrangements()['arrangements'].items():
    print(f'{name:16s} {entry["impulseGain"]:.1f} s, flown {entry["flown"]}')
```

---

## References

- Hagemann, Immich, Nguyen and Dumnov, *Advanced rocket nozzles*, Journal of Propulsion and Power
- NASA SP-8120, *Liquid rocket engine nozzles*
- Sutton and Biblarz, *Rocket Propulsion Elements*, chapter 3
- Rommel et al., *Plug nozzle flowfield calculations for SSTO applications*
