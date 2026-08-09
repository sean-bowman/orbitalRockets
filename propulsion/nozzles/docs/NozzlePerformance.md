[Home](../README.md) > Nozzle Performance

# Nozzle Performance

## Contents

- [Overview](#overview)
- [What this document does not cover](#what-this-document-does-not-cover)
- [The three loss mechanisms](#the-three-loss-mechanisms)
- [The decomposition](#the-decomposition)
- [Where the loss actually is](#where-the-loss-actually-is)
- [The levers, ranked](#the-levers-ranked)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The [propulsion hub](../../docs/PerformanceFundamentals.md) carries a thrust coefficient efficiency of 0.98 and calls it what a well developed nozzle achieves. That number is adequate for sizing an engine and useless for improving one, because it does not say which of three unrelated mechanisms is responsible.

This document takes it apart.

---

## What this document does not cover

**The thrust coefficient itself.** The hub owns `Cf`, its altitude behaviour and the area ratio trade, and its implementation is validated against RS-25. A second implementation here would be a second thing to keep in agreement.

**Contour generation for manufacture.** The NOVA suite generates method of characteristics contours and cooling channel geometry. This sub-domain supplies the requirements and consumes the geometry. The conceptual wall angles and wetted area that the loss budget below is built on are computed here, by Rao's approximation, in [NozzleContour](NozzleContour.md). See [NozzleContourInterface](NozzleContourInterface.md) for where the fidelity boundary sits.

Two of the four classes originally planned for this sub-domain were not built for the first reason. That decision is recorded in the sub-domain README rather than left as an absence.

---

## The three loss mechanisms

They are unrelated to each other and they multiply.

**Divergence.** The exit flow is not axial, so its transverse component produces no thrust.

```
eta_div = (1 + cos alpha) / 2
```

with `alpha` the wall angle at the exit. **This is the only one a contour designer controls directly.**

**Boundary layer.** Friction on the wall, which scales with wetted area and therefore with contour length. A longer nozzle recovers divergence loss and pays it back here.

**Kinetic.** The chemistry does not keep up with the expansion. Recombination reactions that would release energy do not complete, because the gas thins and cools faster than they can proceed. It worsens with area ratio, since residence time falls.

---

## The decomposition

For the reference booster nozzle, an eighty per cent bell at an area ratio of 20.35:

| Mechanism | Efficiency | Loss |
|---|---|---|
| Divergence | 0.9899 | **1.01 %** |
| Boundary layer | 0.9920 | 0.80 % |
| Kinetic | 0.9950 | 0.50 % |
| **Overall** | **0.9771** | **2.29 %** |

**That sits 0.3 points below the hub's single 0.98**, which is close enough to be describing the same quantity and far enough to be worth noting. The hub's figure is an assumed default; this is computed.

The exit angle is computed by [NozzleContour](NozzleContour.md) from Rao's approximation rather than looked up. An earlier version of this document carried a table giving an 80 per cent bell an exit angle of 8 degrees regardless of area ratio, reported an overall efficiency of 0.9822, and drew the opposite conclusion from the one below. Rao gives 11.5 degrees at this area ratio, and the correction doubled the divergence loss.

---

## Where the loss actually is

**Divergence is the largest loss on every contour except a hundred per cent bell.**

An earlier version of this document said the opposite, on the strength of a tabulated exit angle that was too optimistic by three and a half degrees. Computing the angle inverted the conclusion, which is recorded here rather than quietly corrected.

| Contour | Exit angle | Length | Divergence | Boundary layer | Overall | Largest loss |
|---|---|---|---|---|---|---|
| Conical 15 degree | 15.0 | 1.00 | 0.9830 | 0.9900 | 0.9682 | Divergence |
| Bell 60 per cent | **15.4** | 0.60 | 0.9821 | 0.9940 | 0.9713 | Divergence |
| Bell 80 per cent | 11.5 | 0.80 | 0.9899 | 0.9920 | **0.9771** | Divergence |
| Bell 100 per cent | 9.2 | 1.00 | 0.9935 | 0.9900 | 0.9787 | Boundary layer |

**Look at the 60 per cent bell.** Its exit angle of 15.4 degrees is *steeper* than the 15 degree cone it competes with, because a short bell has to turn the flow hard at the throat and has no length left to turn it back. Its divergence loss is therefore worse than the cone's, and the only reason it wins overall is its shorter wall and lower friction.

**A short bell is not a cheap way to buy divergence recovery. It is a way to buy wall area back.** The lookup table, which gave the 60 per cent bell 14 degrees, hid that entirely.

The two mechanisms still move in opposite directions with length, so the sum still has a broad minimum. The whole set spans **0.0105**, which remains smaller than the difference between a good and a poor injector.

---

## The levers, ranked

From the [worked example](../codeInterface.py), all in seconds of burn-averaged specific impulse on the reference booster:

| Lever | Worth | Status |
|---|---|---|
| Altitude compensation, ideal | **14.51 s** | Unreachable |
| Altitude compensation, aerospike | **10.16 s** | Never flown operationally |
| Bell instead of a cone | 2.72 s | Done on every flying engine |
| A fuller bell | 0.49 s | Costs the length back |
| Schmucker instead of Summerfield | 0.45 s | A 36 per cent change in area ratio |

**The ordering is nearly the reverse of the attention each receives.**

The one large lever is altitude compensation, it has been understood since the 1950s, and no operational vehicle has captured it. Everything a contour designer controls is worth a few seconds at most. And the argument most likely to be had, over which separation correlation to believe, is worth less than half a second despite changing the permitted area ratio by more than a third.

---

## Design rules of thumb

- **Decompose before optimising.** A single efficiency does not say what to work on.
- **Use a bell rather than a cone.** Four seconds, and the decision is not controversial.
- **Compute the exit angle, do not look it up.** It depends on area ratio and a table will be wrong.
- **Check where the largest loss is** rather than assuming. On these contours it is usually divergence, and this document said the opposite until the angle was computed.
- **Take the area ratio and the thrust coefficient from the hub**, which owns them.
- **Rank the levers before arguing about any of them.**

---

## Failure modes

**A single efficiency used to guide improvement.** It does not decompose and the effort lands arbitrarily.

**A tabulated exit angle used instead of a computed one.** This sub-domain did exactly that and drew the wrong conclusion from it. An 80 per cent bell does not have a fixed exit angle; it depends on area ratio.

**Contour length increased to recover divergence.** It pays the recovery back in boundary layer, and the sum barely moves.

**Kinetic loss ignored at high area ratio.** It grows with expansion, which is exactly where the large area ratios are.

**A second thrust coefficient implementation written here.** The hub owns it and its version is validated.

---

## Worked numbers

The reference booster nozzle, eighty per cent bell, area ratio 20.35, chamber pressure 10 MPa.

| Quantity | Value |
|---|---|
| Exit angle, computed by Rao | 11.5 degrees |
| Divergence efficiency | 0.9899 |
| Boundary layer efficiency | 0.9920 |
| Kinetic efficiency | 0.9950 |
| Overall | 0.9771 |
| Hub's single figure | 0.98, an assumed default |
| Largest single loss | Divergence, 1.01 % |
| Spread across all contours | 0.0105 |
| Cone to eighty per cent bell | 2.72 s |
| Eighty to a hundred per cent bell | 0.49 s |

---

## Standards

| Standard | What it gives you |
|---|---|
| **NASA SP-8120** | **Liquid rocket engine nozzles.** The design monograph |
| CPIA 246 | Performance prediction, which fixes what a delivered efficiency includes |
| NASA SP-125 | Design of liquid propellant rocket engines |
| JANNAF SPP | The standardised performance program, which does this properly |

---

## Tool interface

```python
from NozzleLosses import NozzleLosses

losses = NozzleLosses()
losses.setInputs({'combination':     'LOX/RP-1',
                  'areaRatio':       20.35,
                  'chamberPressure': 10.0e6,
                  'contour':         'bell 80 per cent'})

decomposition = losses.decomposeEfficiency()
print(decomposition['overall'], decomposition['largestLoss'])

for name, entry in losses.compareContours()['contours'].items():
    print(f'{name:22s} {entry["overall"]:.4f}')
```

---

## References

- NASA SP-8120, *Liquid rocket engine nozzles*
- Sutton and Biblarz, *Rocket Propulsion Elements*, chapter 3
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- Rao, *Exhaust nozzle contour for optimum thrust*
- CPIA 246, *Liquid rocket engine performance prediction and evaluation*
