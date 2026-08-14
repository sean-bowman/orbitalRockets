[Home](../README.md) > FMECA

# FMECA

## Contents

- [Overview](#overview)
- [What it is and what it is for](#what-it-is-and-what-it-is-for)
- [The risk priority number is not a number](#the-risk-priority-number-is-not-a-number)
- [Criticality finds what RPN buries](#criticality-finds-what-rpn-buries)
- [The filter that cannot be gamed](#the-filter-that-cannot-be-gamed)
- [Running one that produces findings](#running-one-that-produces-findings)
- [The action is the product](#the-action-is-the-product)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A failure modes, effects and criticality analysis lists every way a component can fail and what each failure does. That much is bookkeeping. **What makes it useful or useless is what happens to the list afterwards.**

---

## What it is and what it is for

**It works up from the parts**, one component at a time, and it is exhaustive rather than clever.

**What it finds that nothing else does is the failure mode nobody thought about.** A [fault tree](FaultTreeAnalysis.md) only contains the failures somebody put in it; a FMECA finds them by going through the parts list. That is the entire justification for the effort and it is a good one.

**What it cannot do is see a combination.** It is one component at a time by construction, so two failures that together lose the mission are invisible to it. That is what the fault tree is for, and **a programme that runs one and not the other is missing what the other finds.**

---

## The risk priority number is not a number

The ranking almost everybody uses, and it should be read carefully.

```
RPN = severity rank x occurrence rank x detection rank
```

**All three are ordinal scales.** Severity 4 is worse than severity 3 and it is not four thirds of it. Multiplying ordinals produces something that **sorts and does not measure**: an RPN of 80 is not twice an RPN of 40, and two modes with the same RPN can be completely different problems.

**The bands are conventions too.** The occurrence rank comes from banding a probability, and a different banding reorders the table without anything about the design changing.

**None of that makes it useless.** It makes it a sort, and the failure is treating a sort as a measurement: setting an RPN threshold, tracking an average RPN, or reporting a reduction in total RPN as a reliability improvement.

---

## Criticality finds what RPN buries

The consequence that matters on a launch vehicle.

```
criticality = severity rank x occurrence rank
```

**Detection is left out, and that is the point.** Multiplying detection in pushes a rare and detectable catastrophe below a common and hidden nuisance, which is exactly backwards where the catastrophic modes are the whole subject.

On the worked table:

| Mode | Severity | Detection | Criticality | RPN | Rank by crit | Rank by RPN |
|---|---|---|---|---|---|---|
| hard start | catastrophic | possible | 20 | 60 | 1 | 4 |
| fails closed on command | catastrophic | certain | 16 | 16 | 2 | 6 |
| fails open | catastrophic | unlikely | 16 | 64 | 3 | 3 |
| fails to release | catastrophic | undetectable | 16 | 80 | 4 | 1 |

**Two catastrophic modes drop three and four places when detection is multiplied in**, purely because somebody can see them coming.

**Detectability is a mitigation, not a reduction in consequence.** A mode you can see coming still loses the vehicle if nothing is done about it, and folding detection into the ranking treats "we would notice" as though it were "it would not matter".

---

## The filter that cannot be gamed

The third view, and it uses no arithmetic at all.

**Every mode at or above a severity threshold is reviewed, regardless of how either product ranks it.** On the worked case that is seven of eight modes, because on a launch vehicle almost everything is severe.

**That is a feature rather than an embarrassment.** A ranking is for allocating attention among things that all matter; the severity filter is for ensuring nothing that matters is dropped. **The two questions are different and a single ranked list answers only one of them.**

---

## Running one that produces findings

Six things that separate a useful FMECA from a document.

**Start from a real parts list**, not from a block diagram. The modes live in the parts.

**One row per mode, not per component.** A valve that can fail open and fail closed is two rows with different effects, different severities and often different actions.

**State the effect at system level**, not at component level. "Valve fails closed" is a mode; "no engine start, mission lost on the pad" is the effect, and only the second is rankable.

**Give every mode a unique name.** A mode listed twice under different names is a mode that will be actioned once and closed twice, and the class refuses it.

**Rank on both scales and look at the disagreement**, which is where the buried modes are.

**And attach an owner to every action.** A finding with no owner is a finding with no action.

---

## The action is the product

**The FMECA is only useful if somebody acts on it. An unactioned finding is worse than none**, because it converts a real hazard into a document that says the hazard was considered.

That is the domain ethos and it is enforced in code: the class raises where a mandatory review mode has no action against it, rather than reporting a count.

**Four kinds of action, in descending order of how much they are worth.**

**Eliminate the mode**, by removing the component or changing the design so the failure cannot occur.

**Reduce the consequence**, which usually means adding [redundancy](RedundancyAndFaultTolerance.md) or a fail safe state.

**Reduce the occurrence**, by [derating](DeratingAndMargins.md), by qualification, or by process control.

**Improve the detection**, which is the weakest of the four because it does not change what happens, only when you learn about it. **It is also the one most often chosen**, because it is the cheapest.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Modes in the table | 8 |
| At or above critical severity | 7, which is 88 % |
| Top by criticality | hard start |
| Top by risk priority | fails to release |
| Rankings agree | **no** |
| Catastrophic modes buried by detection | 2 |
| Worst rank movement | 4 places |
| Unactioned mandatory review modes | 2, and the check **refuses** |

---

## Design rules of thumb

- **Rank on criticality and on RPN, and read the disagreement.**
- **Apply a severity filter that uses no arithmetic.**
- **One row per mode, not per component.**
- **State the effect at system level.** Only that is rankable.
- **Attach an owner to every action.**
- **Treat improved detection as the weakest of the four actions**, not the default.
- **Never set a threshold on an ordinal product.**

---

## Failure modes

**An RPN threshold.** A sort treated as a measurement.

**Ranking only by RPN.** The detectable catastrophes sort to the bottom.

**One row per component.** Two modes with different consequences collapsed into one.

**An effect stated at component level.** Not rankable and not actionable.

**Detection improved instead of the design changed.** Cheapest and weakest.

**A finding with no owner.** A document saying the hazard was considered.

---

## Tool interface

```python
from FMECA import FMECA

analysis = FMECA()
analysis.setInputs({'modes': [{'item': 'valve', 'mode': 'fails closed',
                               'effect': 'no start', 'severity': 'catastrophic',
                               'probability': 2.0e-4, 'detection': 'certain'}],
                    'actioned': ['fails closed']})

table        = analysis.calculateTable()
disagreement = analysis.rankingDisagreement()
review       = analysis.mandatoryReview()
actions      = analysis.checkActions()   # raises on an unactioned mandatory review mode
```

---

## References

- [FaultTreeAnalysis](FaultTreeAnalysis.md), which finds the combinations this cannot
- [SinglePointFailures](SinglePointFailures.md), which is where the catastrophic modes end up
- MIL-STD-1629A, *Procedures for Performing a Failure Mode, Effects and Criticality Analysis*, not read
