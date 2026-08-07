[Home](../README.md) > Fixturing and Flow Control

# Fixturing and Flow Control

## Contents

- [Overview](#overview)
- [What the fixture does](#what-the-fixture-does)
- [The flow split problem](#the-flow-split-problem)
- [Why it amplifies](#why-it-amplifies)
- [Restrictors](#restrictors)
- [Directing the media](#directing-the-media)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The fixture is where the engineering is. The media and the parameters are largely selected from tables; getting the media to go where it is wanted, in the proportion it is wanted, is a design problem specific to the part.

On a single passage the fixture is trivial. On a manifold it is the whole job.

---

## What the fixture does

| Function | Why |
|---|---|
| **Seal** | Media at 15 MPa finds every gap |
| **Locate** | The part has to be in the same place every time |
| **Direct** | Media should go through the passage, not around it |
| **Restrict** | Balance parallel paths |
| **Protect** | Mask surfaces that must not be honed |
| **Extend** | Carry the media in and out without honing the entry |

**Masking is underrated.** A sealing face, a bearing bore or a datum surface that must not grow has to be masked, and a mask is a fixture feature rather than an afterthought.

**Entry and exit effects are real.** The first and last few diameters of a passage see a different flow field from the middle, so they hone differently. Sacrificial extension pieces move that non-uniformity outside the part, and they are cheap.

---

## The flow split problem

**A manifold with parallel branches does not hone evenly**, and left alone the differences get worse rather than better.

For a power law fluid the conductance of a circular passage scales as

```
Q ~ D^(3 + 1/n) / L^(1/n)
```

**With `n` near 0.28 the diameter exponent is 6.6.**

| Diameter difference | Flow difference |
|---|---|
| 5 % | 39 % |
| **10 %** | **87 %** |
| 20 % | 3.4x |

**A ten percent diameter difference nearly doubles the flow.** Additive passages routinely vary by that much between branches, so a manifold that looks symmetrical on the drawing is not symmetrical to the media.

---

## Why it amplifies

**Within a single passage the process is self-correcting.** A restriction sees higher local velocity, higher shear, more removal, and it opens faster than the surrounding bore.

**Across parallel branches it is the opposite.** The branch with the most flow gets the most shear and the most removal, so it opens further and takes an even larger share on the next cycle.

```
more flow -> more shear -> more removal -> larger bore -> more flow
```

**That is a positive feedback loop** and it runs for every cycle of the process. A small initial difference becomes a large final one.

**The practical consequence:** an unbalanced manifold ends with one branch over-honed and grown out of tolerance, and the others barely touched. Both failures in one part.

---

## Restrictors

**The fix is to deliberately throttle the favoured branches until the flows match.**

| Approach | Notes |
|---|---|
| **Fixture restrictors** | Orifice plates in the fixture at each branch entry. The usual answer |
| Sacrificial inserts | Consumable restrictors that are honed away, which self-compensates |
| Sequential honing | Plug all but one branch and hone them in turn. Slow and exact |
| Media routing | Direct the media so branches see it in series rather than parallel |

**Sizing follows from the conductance ratio.** The required restrictor area on each branch is the ratio of the worst branch's conductance to that branch's, so every path is throttled down to the least favoured one.

**Sequential honing is the exact answer and it costs cycle time.** For a small number of branches on a high value part it is often the right choice, because it removes the balancing problem entirely.

---

## Directing the media

| Technique | Use |
|---|---|
| **Blanking plugs** | Close paths that must not be honed |
| **Sacrificial extensions** | Move entry and exit effects outside the part |
| **Flow reversal** | Alternate direction so both ends see the same treatment |
| Series routing | Force the media through branches in sequence |
| Volume fillers | Reduce dead volume so more of the media does work |

**Flow reversal is standard and it matters more than it looks.** A passage honed in one direction only develops a taper, because the entry sees fresh media at full pressure and the exit sees media that has already done work.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Diameter exponent | 3 + 1/n, about 6.6 |
| 10 % diameter difference | 87 % flow difference |
| Balance tolerance | 10 % on flow fraction |
| Restrictor area ratio | Worst conductance over this branch's |
| Sacrificial extensions | Move entry effects outside the part |
| Reverse the flow | Or the passage tapers |
| Mask what must not grow | It is a fixture feature |
| Sequential honing | Exact, and it costs cycle time |

---

## Failure modes

**Unbalanced branches.** One over-honed, the rest untouched.

**No restrictors on a manifold.** The imbalance amplifies every cycle.

**Sealing face not masked.** It grows and it is no longer flat.

**One-directional flow.** The passage tapers.

**Entry effects inside the part.** The first few diameters are over-honed.

**Fixture leaks at pressure.** Media everywhere and no flow through the part.

---

## Worked numbers

From [`ExtrusionHoning.calculateFlowSplit`](../extrusionHoningLibrary/ExtrusionHoning.py), three branches:

| Branch | Diameter | Length | Flow | Relative removal | Restrictor |
|---|---|---|---|---|---|
| 0 | 5.0 mm | 150 mm | **53.8 %** | **2.79x** | 0.36 |
| 1 | 4.5 mm | 150 mm | 26.9 % | 1.40x | 0.72 |
| 2 | 5.0 mm | 200 mm | 19.3 % | 1.00x | 1.00 |

**Imbalance 61 percent, and branch 0 is honed 2.79 times as much as branch 2.** A 10 percent diameter difference and a 33 percent length difference produce a nearly threefold removal difference, and the class recommends restrictors at 0.36 and 0.72 area ratio to bring them level.

---

## Standards

| Standard | Scope |
|---|---|
| ISO 4287 / 21920 | Surface texture |
| ASME B46.1 | Surface texture |
| ASTM F3335 | Assessing removal of additive manufacturing residues |

---

## Tool interface

```python
from ExtrusionHoning import ExtrusionHoning

honing = ExtrusionHoning()
honing.setInputs({'passageDiameter': 0.005})

result = honing.calculateFlowSplit([{'diameter': 0.0050, 'length': 0.15},
                                    {'diameter': 0.0045, 'length': 0.15},
                                    {'diameter': 0.0050, 'length': 0.20}])

print(result['diameterExponent'], result['imbalance'], result['balanced'])
for branch in result['branches']:
    print(branch['index'], branch['flowFraction'], branch['restrictorAreaRatio'])
```

---

## References

1. Jain, V. K. and Adsul, S. G., "Experimental Investigations into Abrasive Flow Machining", *International Journal of Machine Tools and Manufacture*, Vol. 40, 2000.
2. Rhoades, L. J., "Abrasive Flow Machining", *Manufacturing Engineering*, Vol. 101, 1988.
3. Gradl, P. R. et al., *Metal Additive Manufacturing for Propulsion Applications*, AIAA, 2022.
