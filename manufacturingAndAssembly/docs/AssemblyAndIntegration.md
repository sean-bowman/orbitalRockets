[Home](../README.md) > Assembly and Integration

# Assembly and Integration

## Contents

- [Overview](#overview)
- [Two stacks](#two-stacks)
- [The crossover nobody checks](#the-crossover-nobody-checks)
- [One dimension holds the stack](#one-dimension-holds-the-stack)
- [What the statistical method assumes](#what-the-statistical-method-assumes)
- [Shimming](#shimming)
- [Sequence and access](#sequence-and-access)
- [Torque control](#torque-control)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Whether the parts go together, and the arithmetic that decides how expensive the answer is.

---

## Two stacks

A chain of dimensions has two answers.

**The worst case stack** adds the tolerances arithmetically. It assumes every contributor sits at its limit at the same time and in the same direction, it guarantees assembly, and it is expensive: it demands tolerances tight enough that a coincidence which will never happen would still fit.

**The statistical stack** adds them in quadrature. It assumes the contributors are independent and roughly centred, it is smaller, and it accepts that some assemblies will not fit.

```
worst case  = sum of tolerances
statistical = sqrt( sum of squares )
```

For n equal contributors the ratio is exactly the square root of n, so twelve equal contributors differ by 3.5 between the two methods. **That is the difference between a machined tolerance and a ground one on every part in the stack**, and it is a decision about how many assemblies you are willing to rework rather than a calculation.

---

## The crossover nobody checks

The statistical stack is quoted at a sigma level, and that is where the arithmetic turns around.

**The worst case is a hard bound**: no combination of tolerances can exceed the arithmetic sum. So a k sigma statistical stack exceeds it whenever

```
k > sum(t) / sqrt( sum(t**2) )
```

which for equal contributors is exactly the square root of the count.

| Equal contributors | Crossover sigma | Does 3 sigma help |
|---|---|---|
| 2 | 1.41 | no |
| 4 | 2.00 | no |
| 6 | 2.45 | no |
| 9 | 3.00 | no |
| 10 | 3.16 | yes |
| 16 | 4.00 | yes |
| 25 | 5.00 | yes |

**A three sigma statistical stack needs more than nine contributors before it saves anything.** Below that it produces a spread larger than the arithmetic sum, which cannot physically occur.

**And unequal contributors move the crossover further out**, because one loose dimension dominates the quadrature sum and it stops behaving like root n. The worked stack has six contributors and a crossover of 2.09 against the 2.45 six equal ones would give.

**The check is one line and it is almost never made**, which is how a statistical stack ends up being used on a four contributor joint where it is strictly worse.

---

## One dimension holds the stack

A contributor enters the worst case linearly and the statistical stack as its **square**, so the two rankings differ and the statistical one is far more concentrated.

| Contributor | Tolerance | Worst case share | Statistical share |
|---|---|---|---|
| Barrel roundness after roll | 0.800 mm | 34 % | **50 %** |
| Weld shrinkage across the seam | 0.600 mm | 26 % | 28 % |
| Dome trim to length | 0.400 mm | 17 % | 13 % |
| Fixture location | 0.250 mm | 11 % | 5 % |
| Thermal growth in the shop | 0.180 mm | 8 % | 3 % |
| Y-ring machining | 0.120 mm | 5 % | 1 % |

**Tightening the dominant dimension moves the assembly and tightening any of the others moves almost nothing.** Tightening the Y-ring machining from 0.12 mm to 0.06 removes one per cent of the statistical stack, for a real cost.

**And fixing the dominant one moves the problem rather than removing it.** Tighten the barrel roundness and weld shrinkage becomes the dominant contributor at fifty per cent. That is the same shape as a [bottleneck](RateAndLearning.md) and a [life limit](../../recoveryAndReusability/docs/LifeTrackingAndLimits.md), and it means the gain from any one fix is the gap to the next contributor.

---

## What the statistical method assumes

Two assumptions, and both fail in the place that matters.

**Independence.** Parts from one batch, one machine, one operator or one thermal environment share a bias, and **a shared bias adds arithmetically like the worst case rather than in quadrature.** The contributors most likely to be correlated are the ones from the same process, which is exactly the set a statistical stack is usually applied to.

**Centring.** The quadrature sum describes a spread around the nominal and says nothing about where the nominal sits. **A process running at the top of its band puts the whole stack off centre**, and the statistical stack will happily report a symmetric spread around a mean that is not where the drawing says.

Both are why a statistical stack needs process capability data behind it and not just a tolerance block.

---

## Shimming

The answer to a stack that opens too far, and it is a cost rather than a failure.

**A gap that closes is an interference** and the parts do not go together. That is refused rather than reported, because a negative gap is not a small negative margin.

**A gap that opens is a shim**, which is measurable, fillable and a labour item. The design decision is whether shims are custom-machined per assembly, which is accurate and slow, or selected from a set, which is fast and coarse.

**Liquid shim exists for the cases neither covers** and it brings a cure time into the assembly sequence, which is a schedule item on the critical path.

---

## Sequence and access

**The assembly sequence is a design output and it is usually discovered rather than designed.**

Three things it has to satisfy.

**Every fastener has to be reachable with a tool and a hand attached to it.** A component reachable in CAD is not reachable with a torque wrench and a forearm.

**Every joint that needs inspecting has to be inspectable before it is covered.** Once a closeout panel is on, the [inspection](InspectionAndNDE.md) behind it is a disassembly.

**And the sequence has to be reversible where a scrub or a finding demands it.** A joint that can only be made once is a joint whose failure scraps the assembly.

---

## Torque control

Small, and it is where a surprising number of findings come from.

**Torque is a proxy for preload and it is a poor one.** Most of the torque goes into friction, and the fraction that becomes preload depends on the thread condition, the lubricant and the surface under the nut. A torque specification without a lubrication specification is a preload with a scatter of tens of per cent.

**Which is why the preload-critical joints are not torque controlled.** Turn of the nut, bolt stretch measurement and instrumented bolts all measure something closer to the preload itself. See [mechanismsAndSeparation](../../mechanismsAndSeparation/) for what preload does downstream.

---

## Worked numbers

The tank barrel stack, six contributors, quoted at three sigma.

| Quantity | Value |
|---|---|
| Worst case | 2.350 mm |
| Statistical, one sigma | 1.127 mm |
| Statistical at three sigma | 3.380 mm, **capped at the worst case** |
| Crossover sigma | 2.09 |
| Equal contributor crossover | 2.45 |
| Dominant contributor | barrel roundness, 50 % |
| After tightening it | weld shrinkage, 50 % |
| Rejects at three sigma | 1 in 370 |
| Process tolerance spread | 600x |

---

## Design rules of thumb

- **Check the crossover before choosing a statistical stack.** One line.
- **Tighten the dominant contributor and nothing else.** The rest hold almost nothing.
- **Expect the problem to move**, and know what it moves to.
- **Get process capability data before assuming independence and centring.**
- **Design the sequence, do not discover it.**
- **Do not torque a preload-critical joint.** Measure something closer to the preload.

---

## Failure modes

**A three sigma stack on few contributors.** Worse than the arithmetic sum.

**Correlated contributors added in quadrature.** A shared bias adds arithmetically.

**An off-centre process in a centred model.** The spread is right and the mean is not.

**Every dimension tightened equally.** Cost everywhere, benefit in one place.

**A joint inspected after closeout.** It is a disassembly.

**Preload specified as torque.** Tens of per cent of scatter.

---

## Tool interface

```python
from ToleranceStack import ToleranceStack

stack = ToleranceStack()
stack.setInputs({'nominalGap': 0.0040,
                 'minimumGap': 0.0002,
                 'maximumGap': 0.0055,
                 'sigmaLevel': 3.0,
                 'contributors': [{'name': 'roundness', 'tolerance': 0.00080},
                                  {'name': 'weld',      'tolerance': 0.00060}]})

result    = stack.calculateStack()
check     = stack.checkGap('worstCase')      # raises where the gap closes
rejects   = stack.rejectFraction()
processes = stack.compareProcesses(dimension = 3.7)
```

---

## References

- [ToolingAndFixturing](ToolingAndFixturing.md), which owns two of the contributors
- [InspectionAndNDE](InspectionAndNDE.md), for what has to be reachable before closeout
- [mechanismsAndSeparation](../../mechanismsAndSeparation/), for what preload does downstream
- ASME Y14.5, geometric dimensioning and tolerancing, not read
