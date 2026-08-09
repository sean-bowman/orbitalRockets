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

**Contour generation.** The NOVA suite generates method of characteristics contours and cooling channel geometry. This sub-domain supplies the requirements and consumes the geometry. See [NozzleContourInterface](NozzleContourInterface.md).

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
| Divergence | 0.9951 | 0.49 % |
| Boundary layer | 0.9920 | 0.80 % |
| Kinetic | 0.9950 | 0.50 % |
| **Overall** | **0.9822** | **1.78 %** |

**That reproduces the hub's single 0.98**, which is the check that the decomposition is describing the same quantity.

---

## Where the loss actually is

**The largest single loss is the boundary layer, not divergence.**

That is worth stating plainly because divergence is the term everyone reaches for, it is the one in every textbook, and it is the only one a contour shape changes. On a well shaped bell it has already been reduced to the smallest of the three.

The contour comparison makes the point:

| Contour | Exit angle | Length | Divergence | Boundary layer | Overall |
|---|---|---|---|---|---|
| Conical 15 degree | 15 | 1.00 | 0.9830 | 0.9900 | 0.9682 |
| Bell 60 per cent | 14 | 0.60 | 0.9851 | 0.9940 | 0.9743 |
| Bell 80 per cent | 8 | 0.80 | 0.9951 | 0.9920 | **0.9822** |
| Bell 100 per cent | 5 | 1.00 | 0.9981 | 0.9900 | 0.9831 |

**A shorter bell has more divergence loss and less boundary layer loss.** The two move in opposite directions, so the sum has a broad minimum rather than a sharp optimum, and the eighty per cent bell sits near it rather than at it.

The whole set spans **0.0149**, which is smaller than the difference between a good and a poor injector.

---

## The levers, ranked

From the [worked example](../codeInterface.py), all in seconds of burn-averaged specific impulse on the reference booster:

| Lever | Worth | Status |
|---|---|---|
| Altitude compensation, ideal | **14.51 s** | Unreachable |
| Altitude compensation, aerospike | **10.16 s** | Never flown operationally |
| Bell instead of a cone | 4.29 s | Done on every flying engine |
| A fuller bell | 0.29 s | Costs the length back |
| Schmucker instead of Summerfield | 0.45 s | A 36 per cent change in area ratio |

**The ordering is nearly the reverse of the attention each receives.**

The one large lever is altitude compensation, it has been understood since the 1950s, and no operational vehicle has captured it. Everything a contour designer controls is worth a few seconds at most. And the argument most likely to be had, over which separation correlation to believe, is worth less than half a second despite changing the permitted area ratio by more than a third.

---

## Design rules of thumb

- **Decompose before optimising.** A single efficiency does not say what to work on.
- **Use a bell rather than a cone.** Four seconds, and the decision is not controversial.
- **Do not chase the last of the divergence loss.** An eighty to a hundred per cent bell is a third of a second for a quarter of the length.
- **Check where the largest loss is** rather than assuming it is divergence.
- **Take the area ratio and the thrust coefficient from the hub**, which owns them.
- **Rank the levers before arguing about any of them.**

---

## Failure modes

**A single efficiency used to guide improvement.** It does not decompose and the effort lands arbitrarily.

**Divergence assumed to be the dominant loss.** On a well shaped bell it is the smallest of the three.

**Contour length increased to recover divergence.** It pays the recovery back in boundary layer, and the sum barely moves.

**Kinetic loss ignored at high area ratio.** It grows with expansion, which is exactly where the large area ratios are.

**A second thrust coefficient implementation written here.** The hub owns it and its version is validated.

---

## Worked numbers

The reference booster nozzle, eighty per cent bell, area ratio 20.35, chamber pressure 10 MPa.

| Quantity | Value |
|---|---|
| Divergence efficiency | 0.9951 |
| Boundary layer efficiency | 0.9920 |
| Kinetic efficiency | 0.9950 |
| Overall | 0.9822 |
| Hub's single figure | 0.98 |
| Largest single loss | Boundary layer, 0.80 % |
| Spread across all contours | 0.0149 |
| Cone to eighty per cent bell | 4.29 s |
| Eighty to a hundred per cent bell | 0.29 s |

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
