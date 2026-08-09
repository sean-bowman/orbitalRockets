[Home](../README.md) > Area Ratio Selection

# Area Ratio Selection

## Contents

- [Overview](#overview)
- [The hub owns this](#the-hub-owns-this)
- [What this document adds](#what-this-document-adds)
- [The optimum is broad](#the-optimum-is-broad)
- [What actually sets a booster area ratio](#what-actually-sets-a-booster-area-ratio)
- [Upper stages](#upper-stages)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Area ratio selection is the decision the [propulsion hub worked example](../../codeInterface.py) is built around, and it is covered in full there. This document does not repeat it.

What it adds is the part visible only from inside the nozzle: how flat the optimum actually is, and what really sets a first stage area ratio once you accept that flatness.

---

## The hub owns this

The hub's result, in summary, because the rest of this document argues against parts of it.

Three defensible questions give three different answers:

| Question | Area ratio | Burn-averaged `Isp` |
|---|---|---|
| What maximises thrust at liftoff | 10.75 | 296.2 s |
| What maximises impulse over the burn | 25.75 | 302.3 s |
| What the flow will tolerate | 21.42 | 302.0 s |
| The design point, with margin | 20.35 | 301.8 s |

The hub concluded that the intuitive answer costs 61 m/s of stage delta-V, that the true optimum is unreachable because it separates, and that the separation limit lands close enough to the optimum to make the constraint nearly free.

**All of that is right and this document adds a caveat to the middle claim.**

---

## What this document adds

The hub used Summerfield's separation criterion, which permits an area ratio of 21.42. [Schmucker's criterion](FlowSeparation.md) permits **29.17**, and under it the hub's rejected optimum of 25.75 is perfectly reachable.

So the statement "the true optimum is unreachable" is a statement about which correlation was used, not about the engine.

**It changes almost nothing.** Moving the design point from 20.35 to 27.71 is worth **0.45 seconds**, 0.15 per cent. The reason is the subject of the next section.

---

## The optimum is broad

Burn-averaged specific impulse against area ratio, for the reference booster:

| Area ratio | Burn-averaged `Isp` |
|---|---|
| 20.35 | 301.82 s |
| 25.75 | 302.32 s |
| 27.71 | 302.28 s |

**Everything from 20 to 28 is within half a second.**

That flatness is why a 36 per cent change in the permitted area ratio is worth a seventh of a per cent in impulse, and it is why the argument over separation criteria is not worth having at length.

It also means the area ratio is available to be set by something other than performance, which is what usually happens.

---

## What actually sets a booster area ratio

Given the flatness, performance is rarely the binding consideration. In practice the area ratio of a first stage engine is set by:

**The start transient.** Every start is fully separated at the beginning and the separation line sweeps down the nozzle as chamber pressure rises. That is a side load event on every start, and it scales with nozzle size. See [FlowSeparation](FlowSeparation.md).

**The base diameter.** The exit diameter sets the vehicle base area and therefore the base drag and the engine spacing on a multi-engine cluster. On a clustered stage the nozzles have to fit beside each other before they have to be optimal.

**Gimbal envelope.** A larger nozzle needs more clearance to gimbal through its full range, and the clearance is at the base of the vehicle where structure is.

**Mass.** A larger nozzle is heavier and its mass is at the aft end.

**None of those are performance**, and all of them are more binding than half a second of specific impulse.

---

## Upper stages

The reasoning inverts almost completely.

There is no ambient pressure, so **there is no separation limit and no over-expansion**. The area ratio is bounded only by mass, by length, and by what the nozzle can be cooled to.

That is why upper stage area ratios are so much larger: RL10-B-2 reaches 285 with an extendible extension, which would be entirely unusable on the ground.

The remaining constraints are geometric rather than fluid dynamic, and the [extendible nozzle](AltitudeCompensation.md) exists to relax the length one.

---

## Design rules of thumb

- **Take the area ratio trade from the hub.** It owns it and its version is validated.
- **Do not over-refine it.** The optimum is flat to within half a second across a wide range.
- **Let something else set it.** Start transient, base diameter, gimbal envelope and mass are all more binding.
- **Report which separation criterion was used**, because it changes the permitted range by a third.
- **On an upper stage, push it until mass or length stops you.** Nothing fluid dynamic will.

---

## Failure modes

**The area ratio optimised to two decimal places.** The optimum is flat and the effort is wasted.

**A separation criterion adopted without saying so.** It changes the permitted range by 36 per cent.

**Performance treated as the binding constraint on a booster.** It usually is not.

**Base diameter discovered after the nozzle is sized.** On a clustered stage the nozzles have to fit.

**Sea level reasoning applied to an upper stage.** There is no separation limit in vacuum.

---

## Worked numbers

The reference booster, and the hub's own conclusions with this sub-domain's caveat.

| Quantity | Value |
|---|---|
| Hub design point | 20.35 |
| Hub burn-average optimum | 25.75, rejected under Summerfield |
| Summerfield permitted limit | 21.42 |
| Schmucker permitted limit | 29.17 |
| Optimum reachable under Schmucker | Yes |
| Worth of the change | 0.45 s, 0.15 % |
| Spread from area ratio 20 to 28 | under 0.5 s |

---

## Standards

| Standard | What it gives you |
|---|---|
| NASA SP-8120 | Liquid rocket engine nozzles |
| NASA SP-125 | Design of liquid propellant rocket engines |
| CPIA 246 | Performance prediction |

---

## Tool interface

The area ratio trade lives in the hub. This sub-domain contributes the separation criteria that bound it.

```python
import sys
sys.path.insert(0, '../propulsionLibrary')    # from the sub-domain directory

from EnginePerformance import EnginePerformance

performance = EnginePerformance()
performance.setInputs({'combination': 'LOX/RP-1', 'chamberPressure': 10.0e6,
                       'areaRatio': 20.35})

print(performance.compareExpansion()['usableAtSeaLevel'])
```

---

## References

- NASA SP-8120, *Liquid rocket engine nozzles*
- Sutton and Biblarz, *Rocket Propulsion Elements*, chapter 3
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
