[Home](../README.md) > Inspection and NDE

# Inspection and NDE

## Contents

- [Overview](#overview)
- [An inspection is a probability](#an-inspection-is-a-probability)
- [a50, a90 and a90/95](#a50-a90-and-a9095)
- [The demonstration behind a number](#the-demonstration-behind-a-number)
- [The result that decides the design](#the-result-that-decides-the-design)
- [What each method misses](#what-each-method-misses)
- [Dimensional inspection](#dimensional-inspection)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

**Inspection finds what it is looking for.** Deciding what you are looking for, and whether the method can see it, is the whole subject.

---

## An inspection is a probability

An inspection does not find flaws. It finds flaws with a probability that depends on their size, and MIL-HDBK-1823A models that with a log-odds curve:

```
log( POD / (1 - POD) ) = ( log(a) - mu ) / sigma
```

which rearranges to

```
POD(a) = 1 / ( 1 + (a50 / a) ** (1 / sigma) )
```

The handbook offers four link functions, logit, probit, complementary log-log and log-log, of which the logit is the one used here. **The curve reaches zero and one only in the limit**, which is the model saying what everybody knows and few procedures admit: there is no flaw size an inspection is guaranteed to find, and no size it cannot occasionally find.

---

## a50, a90 and a90/95

Three numbers, and the difference between the last two is the one that gets lost.

**a50** is the size found half the time. It is the middle of the curve and it is where a demonstration estimates most precisely.

**a90** is the size found nine times in ten. Because the logit of 0.9 is log 9,

```
a90 / a50 = 9 ** sigma
```

**so the shape of a detection curve is one number.** A steep inspection has a small sigma and a narrow band between finding half and finding nine tenths; a shallow one has a wide band and its a90 is far out.

**a90/95 is a different kind of number.** It is the 95 per cent confidence bound on the **estimate** of a90, so it depends on how many specimens the demonstration used as well as on the inspection itself.

**The handbook notes that a90/95 has become a de facto design criterion**, and it also notes that 120 binary inspection opportunities give a significantly more precise a50 and therefore a smaller a90/95 than the 60 target minimum, for the same technique.

**Which means the flaw size a programme designs to is partly a statement about how many specimens somebody paid for.** That is not how a design criterion is usually understood and it is worth understanding.

---

## The demonstration behind a number

MIL-HDBK-1823A section 4.5.2.2, and these are minimums rather than targets.

| Response | Minimum targets | Unflawed sites |
|---|---|---|
| Binary hit or miss | 60 | at least 3 per flawed site |
| Quantitative signal | 40 | same |

**The unflawed sites are there for the false positive rate**, which is the half of inspection capability nobody quotes. An inspection that finds everything is useless, because it also finds everything that is not there, and the cost of that is a rejected part or a disassembly.

**The handbook also records a change of practice worth knowing.** Target sizes were once spaced uniformly on a log scale; the current recommendation is uniform Cartesian spacing, because a90/95 is the criterion and the ninetieth percentile is therefore the part of the curve worth estimating precisely. It warns separately that demonstrations tend to contain too many large targets, because small ones are hard to make and the ones intended to be small often come out larger.

---

## The result that decides the design

**If the reliably detectable flaw size is larger than the critical flaw size, the inspection establishes nothing.**

It cannot rule out a flaw big enough to fail the part. The part is not inspectable in any useful sense, and the alternatives are a proof test, a life limit, or a material with a larger critical flaw. See [FractureAndDamageTolerance](../../aerospaceMaterials/docs/FractureAndDamageTolerance.md) for where the critical size comes from and [InspectionAndAcceptance](../../recoveryAndReusability/docs/InspectionAndAcceptance.md) for what a proof test bounds instead.

**A factor between the two is usual**, because the flaw grows between inspections. A margin of one means the inspection just barely rules out failure today and says nothing about the interval before the next one.

**This is the conclusion that gets discovered late**, because the inspection procedure is written after the wall thickness is fixed. On the worked tank the same weld and the same inspection clear comfortably at full wall and fail at a thinner one, and nothing about the inspection changed.

---

## What each method misses

The column that decides the answer, and it is not the one people read.

| Method | a90 | Cost | Misses |
|---|---|---|---|
| Computed tomography | 0.65 mm | 40 | little, and it is limited by part size and cost |
| Eddy current | 0.86 mm | 6 | flaws deeper than a few skin depths |
| Magnetic particle | 1.20 mm | 3 | **everything in an austenitic or aluminium part** |
| Penetrant | 1.45 mm | 3 | subsurface flaws, and anything a smeared surface closed |
| Ultrasonic | 2.15 mm | 8 | flaws parallel to the beam, and the near field |
| Radiography | 4.50 mm | 12 | tight planar cracks not aligned with the beam |
| Visual | 6.70 mm | 1 | anything subsurface, and anything under a coating |

**On the worked tank the cheapest method that clears the size requirement is magnetic particle, and it does nothing at all on aluminium.** The applicable answer is penetrant, at the same cost and a slightly larger a90.

**A ranking by a90 is not a ranking by usefulness.** Three things break it.

**Material.** Magnetic particle needs a ferromagnetic part.

**Access.** Ultrasonic needs a couplant and a surface to put the probe on; radiography needs both sides.

**Orientation.** Ultrasonic misses a flaw parallel to the beam and radiography misses a tight crack not aligned with it. **A flaw the method cannot see is not reported as a miss; it is not reported at all.**

---

## Dimensional inspection

Different problem, same shape of answer.

**A coordinate measuring machine** is accurate, slow, and limited to what fits on it. It measures points and infers features, which means the feature it reports depends on where the points were taken.

**A laser tracker** covers a launch vehicle sized article at lower accuracy, and it is what large assemblies are actually measured with. Its accuracy degrades with distance and with the number of instrument moves, and **every move is a new coordinate frame that has to be tied to the last one.**

**Photogrammetry** covers a surface rather than points and is the right answer for a shape rather than a dimension.

**All three measure the part in the shop rather than in flight**, at a shop temperature and in a shop gravity orientation, and a large thin structure is a different shape in both.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Penetrant a50 | 0.600 mm |
| Penetrant a90 | 1.445 mm |
| Ratio, which is 9 to the sigma | 2.41 |
| Critical flaw, full wall | 4.000 mm |
| Required with a factor of two | 2.890 mm, margin 1.38 |
| Critical flaw, thin wall | 1.300 mm, **refused** |
| Flaws missed at the thin wall critical size | 13 % |
| Demonstration used | 80 targets against a 60 minimum |
| Methods clearing the full wall case | 5 of 7 |

---

## Design rules of thumb

- **Get the critical flaw size before choosing the method**, not after.
- **Leave a factor between a90 and the critical size.** The flaw grows between inspections.
- **Read the "what it misses" column first.** It disqualifies more methods than a90 does.
- **Ask what the demonstration was.** a90/95 depends on it.
- **Count the unflawed sites.** The false positive rate is half the capability.
- **Remember that a large structure is a different shape in the shop.**

---

## Failure modes

**An inspection specified after the wall thickness.** It may not see the critical flaw.

**A method chosen by sensitivity.** The one that clears may not work on the material.

**a90 and a90/95 used interchangeably.** One is a property of the inspection, the other of the demonstration.

**A capability claim with no demonstration size.** The number means nothing without it.

**A false positive rate never estimated.** Rejected good parts and unnecessary disassemblies.

**An orientation-sensitive method on an unknown flaw orientation.** Silence rather than a miss.

---

## Tool interface

```python
from InspectionCapability import InspectionCapability

inspection = InspectionCapability()
inspection.setInputs({'method':               'penetrant',
                      'responseType':         'hitMiss',
                      'demonstrationTargets': 80,
                      'criticalFlawSize':     0.0040,
                      'detectionMargin':      2.0})

curve         = inspection.detectionCurve()
demonstration = inspection.demonstrationSize()   # raises below the standard minimum
check         = inspection.checkAgainstCriticalFlaw()   # raises where it establishes nothing
methods       = inspection.compareMethods()
```

---

## References

- MIL-HDBK-1823A, *Nondestructive Evaluation System Reliability Assessment*, 7 April 2009, section 4.5.2.2 and appendix G
- [FractureAndDamageTolerance](../../aerospaceMaterials/docs/FractureAndDamageTolerance.md), for the critical flaw size
- [InspectionAndAcceptance](../../recoveryAndReusability/docs/InspectionAndAcceptance.md), for the reuse case
- [ProcessQualification](ProcessQualification.md)
