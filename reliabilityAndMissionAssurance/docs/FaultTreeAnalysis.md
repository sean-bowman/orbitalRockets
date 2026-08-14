[Home](../README.md) > Fault Tree Analysis

# Fault Tree Analysis

## Contents

- [Overview](#overview)
- [What it is for](#what-it-is-for)
- [Cut sets](#cut-sets)
- [The rare event approximation](#the-rare-event-approximation)
- [Importance](#importance)
- [What the tree cannot see](#what-the-tree-cannot-see)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A fault tree starts at an undesired top event and decomposes it downward through AND and OR gates to basic events. It is the complement of a [FMECA](FMECA.md): that works up from the parts, this works down from the failure.

---

## What it is for

**It is for the cut sets, not the number.**

A probability can be got from a spreadsheet. **A list of the smallest combinations of events that on their own cause the top event cannot**, and that list is what a fault tree produces that nothing else does.

**A cut set of order one is a single point failure.** Finding them is the whole justification for building the tree, and **a tree that produces a top event probability without producing that list has been run for the wrong reason.**

---

## Cut sets

A minimal cut set is a combination of basic events that causes the top event and that contains no smaller such combination.

They are built bottom up. **An OR gate's cut sets are the union of its inputs'** and **an AND gate's are every combination of one from each input**, with non-minimal sets removed at the end.

The order tells you almost everything.

**Order one is a single point failure.** It occurs at its own probability, which is orders of magnitude above any combination.

**Order two needs two independent failures**, which is a product of two small numbers and is usually negligible.

**Order three and above contributes nothing** to a top event probability and is not worth enumerating.

**So the ranking by contribution is nearly always the ranking by order**, and on the worked tree five single point failures carry essentially 100 per cent of the top event while two carefully redundant pairs carry a thousandth of it.

---

## The rare event approximation

Summing the cut set probabilities is the usual quantification and it is not exact.

**It double counts the overlaps**, so it overstates the top event probability. That is the safe direction, and the error is small when the events are rare: on the worked tree the sum is 3.501e-3 against an exact 3.497e-3, an overstatement of 0.11 per cent.

**It stops being small when the events are not rare.** A tree with basic events around ten per cent can be overstated by a noticeable fraction, and at that point the approximation should be replaced rather than trusted.

**Computing both makes the error visible rather than assumed**, which costs nothing on a tree small enough to evaluate exactly.

---

## Importance

How much each basic event matters, which is a different question from how likely it is.

The Birnbaum measure is the change in the top event probability when an event goes from certain to impossible. **An event in a single point cut set has an importance near one whatever its probability**, because the top event follows it directly. An event behind an AND gate has an importance of roughly its partner's probability, which is small.

On the worked tree the redundant avionics units sit **three orders of magnitude below a single valve on importance and one order above it on probability.**

**That is the whole reason to compute importance.** A ranking by probability points at the avionics; a ranking by importance points at the valve; and the valve is what loses the mission.

---

## What the tree cannot see

Three limitations, and the first is the one that matters most.

**Common cause.** A fault tree with independent basic events treats an AND gate over two identical units as a product of two independent probabilities, which is exactly the error [RedundancyAndFaultTolerance](RedundancyAndFaultTolerance.md) exists to correct. **An AND gate over units that share a design or an environment is not what it looks like**, and the honest treatment is to add an explicit common cause basic event as an OR input alongside the AND gate.

**Anything nobody put in it.** The tree contains the failures somebody thought of, which is why it does not replace a [FMECA](FMECA.md).

**And sequence.** A standard fault tree is combinatorial: it says which events together cause the top event and not in what order, so a failure that matters only if it happens before another one is not represented.

---

## Worked numbers

| Cut set | Order | Probability | Share |
|---|---|---|---|
| engineStartFail | 1 | 2.00e-3 | 57.1 % |
| regulatorFail | 1 | 5.00e-4 | 14.3 % |
| boltFail | 1 | 5.00e-4 | 14.3 % |
| fairingFail | 1 | 3.00e-4 | 8.6 % |
| mainValveFail | 1 | 2.00e-4 | 5.7 % |
| avionicsA + avionicsB | 2 | 1.00e-6 | 0.0 % |
| initiatorA + initiatorB | 2 | 1.00e-8 | 0.0 % |

| Quantity | Value |
|---|---|
| Top event, exact | 3.497e-3 |
| Rare event sum | 3.501e-3, an overstatement of 0.11 % |
| Single point failures | 5, carrying 100 % |
| Importance of a single valve | 0.997 |
| Importance of a redundant avionics unit | 9.97e-4 |

---

## Design rules of thumb

- **Run it for the cut sets.** The number is a by-product.
- **Read the order first.** Order one is categorically different from order two.
- **Compute the exact top event as well as the rare event sum.** It costs nothing on a small tree.
- **Rank by importance, not by probability.**
- **Add an explicit common cause event alongside every AND gate over similar units.**
- **Run a FMECA too.** The tree only contains what somebody put in it.

---

## Failure modes

**A tree run for its top event probability.** The cut sets are the product.

**An AND gate over identical units taken as independent.** Common cause is invisible to the tree.

**A rare event sum on a tree with common events.** The overstatement stops being small.

**Ranking basic events by probability.** The redundant ones look worse than the single ones.

**A tree used instead of a FMECA.** It only contains what was thought of.

---

## Tool interface

```python
from FaultTree import FaultTree
from reliabilityUtils import FaultTreeError

tree = FaultTree()
tree.setInputs({'topEvent': 'missionLoss',
                'gates': {'missionLoss': {'type': 'or',  'inputs': ['propulsion', 'control']},
                          'propulsion':  {'type': 'or',  'inputs': ['startFail', 'valveFail']},
                          'control':     {'type': 'and', 'inputs': ['avionicsA', 'avionicsB']}},
                'basicEvents': {'startFail': 2.0e-3, 'valveFail': 2.0e-4,
                                'avionicsA': 1.0e-3, 'avionicsB': 1.0e-3}})

probability = tree.calculateProbability()
cutSets     = tree.analyseCutSets()
importance  = tree.importance()

# Accepting every single point failure clears the check; leaving one off refuses.
check = tree.checkSinglePoints(accepted = cutSets['singlePoints'])

try:
    tree.checkSinglePoints(accepted = ['startFail'])
except FaultTreeError:
    pass
```

---

## References

- [FMECA](FMECA.md), which finds the modes this only contains if somebody added them
- [RedundancyAndFaultTolerance](RedundancyAndFaultTolerance.md), for the common cause the tree cannot see
- [SinglePointFailures](SinglePointFailures.md), which is what the cut sets of order one become
- NUREG-0492, the *Fault Tree Handbook*, not read
