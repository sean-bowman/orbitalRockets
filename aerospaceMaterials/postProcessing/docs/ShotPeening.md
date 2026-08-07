[Home](../README.md) > Shot Peening

# Shot Peening

## Contents

- [Overview](#overview)
- [The mechanism](#the-mechanism)
- [Almen intensity](#almen-intensity)
- [Coverage](#coverage)
- [Media selection](#media-selection)
- [What the benefit is worth](#what-the-benefit-is-worth)
- [How the benefit is lost](#how-the-benefit-is-lost)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Blast a surface with hard round media and each impact yields a small dimple. The material beneath the dimple has been stretched, and the surrounding material has not, so the surface layer ends up in compression.

A fatigue crack cannot open under compression. That is the whole mechanism and it is worth 10 to 20 percent on the fatigue limit for a process that costs almost nothing.

---

## The mechanism

Each impact plastically stretches a small volume at the surface. The elastic material beneath resists that stretch and squeezes the layer back, leaving it in residual compression.

| Quantity | Typical |
|---|---|
| Surface compressive stress | 0.4 to 0.6 of the yield strength |
| Layer depth | 0.05 to 0.5 mm |
| Peak stress location | Just below the surface, not at it |
| Balancing tension | In the core, and it is small because the core is large |

**The compression is limited by yield.** The surface cannot hold more compression than it can carry, so the stress saturates near half yield regardless of how hard it is peened. **More intensity buys depth, not magnitude.**

**Depth is what matters** for a crack that has to grow through the layer, which is why the intensity is specified rather than the stress.

---

## Almen intensity

Peening intensity is measured by what it does to a standard test strip rather than by the process parameters.

An Almen strip is clamped flat, peened on one side, released, and the arc height measured. The compressive layer on one side bows it.

| Strip | Thickness | Range | Use |
|---|---|---|---|
| **N** | 0.79 mm | 0.05 to 0.30 mm | Light. Thin sections and aluminium |
| **A** | 1.29 mm | 0.10 to 0.60 mm | The standard. Most aerospace |
| **C** | 2.39 mm | 0.15 to 0.60 mm | Heavy. Gears and landing gear |

**Intensity is quoted as an arc height and a strip**, for example 0.20A. The number alone is meaningless without the strip, because the same peening produces different arc heights on different strips.

**Saturation is what defines the intensity.** The intensity is the arc height at the point where doubling the exposure time increases the arc height by less than 10 percent. That is a specific measurement on a saturation curve, not simply the arc height after some exposure.

---

## Coverage

**Each impact lands randomly, so later impacts increasingly fall where earlier ones already have.**

```
C = 1 - exp(-A * t)
```

Coverage approaches 100 percent asymptotically and never reaches it. **Full coverage is therefore DEFINED as 98 percent**, and that is why a specification calling for 200 percent coverage is not a typo: it means twice the exposure time needed to reach 98 percent.

| Specification | Meaning |
|---|---|
| 100 % | Time to reach 98 percent coverage |
| 200 % | Twice that time |
| 400 % | Four times, for a demanding application |

**Partial coverage loses the benefit disproportionately.** The fatigue benefit depends on the whole surface being in compression, and an uncovered patch is where the crack starts. A part at 80 percent coverage does not have 80 percent of the benefit.

**Coverage is verified visually at 10x magnification**, or with a fluorescent tracer that is removed by the impacts.

---

## Media selection

| Media | Hardness | Roughening | Notes |
|---|---|---|---|
| **Cast steel shot** | 500 HV | 1.00 | The default. Cheap. **Leaves iron on the surface** |
| **Ceramic bead** | 700 HV | 0.60 | No iron. The choice for stainless and titanium |
| Glass bead | 500 HV | 0.50 | Light intensity, good finish |
| Cut wire | 550 HV | 0.90 | Consistent size, longer life |

**Media hardness must exceed the workpiece** or the shot deforms instead of the part and no compression is developed.

**Iron contamination is the reason ceramic exists.** Steel shot embeds iron particles in the surface, and on stainless or titanium those become corrosion initiation sites. A part that will be passivated afterwards must be peened with ceramic or glass.

**Broken media is a defect.** A fractured shot particle has sharp edges and it cuts rather than dimples, producing a stress concentration instead of removing one. Media is classified and the broken fraction removed continuously.

---

## What the benefit is worth

| Application | Typical fatigue gain |
|---|---|
| Machined surface | 10 to 20 % |
| **As-built additive surface** | Larger, because the starting point is worse |
| Welded joint | 20 to 40 %, and it also counters the weld tensile residual stress |
| Threaded fastener root | Substantial, and it is why rolled threads are peened |
| Shot peened before plating | Offsets the plating fatigue debit |

**Peening before hard chrome plating is standard practice** for exactly that last reason: chrome cracks and carries a severe fatigue debit, and a compressive layer underneath offsets it.

---

## How the benefit is lost

**The compressive layer is not permanent, and three things remove it.**

| Mechanism | Effect |
|---|---|
| **Any material removal** | Machining, etching or electropolishing takes the layer off |
| **Thermal exposure** | The compression relaxes. A stress relief undoes it |
| **High cyclic load** | Cyclic relaxation at stresses above about 0.6 yield |

**A peened part that sees a stress relief afterwards has lost the benefit and nobody notices**, because nothing visible changed and no inspection catches it.

**Peen last.** After machining, after etching, after every thermal cycle.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Surface compressive stress | ~0.5 of yield, saturating |
| Layer depth | 0.05 to 0.5 mm, set by intensity |
| Full coverage | 98 %, and 200 % means twice the time |
| Media harder than the workpiece | Or nothing happens |
| Ceramic on stainless and titanium | No iron contamination |
| Peen last | After every removal and thermal process |
| Fatigue gain | 10 to 20 % on a machined surface |
| Peen before hard chrome | Offsets the plating debit |

---

## Failure modes

**Electropolished after peening.** Layer removed.

**Stress relieved after peening.** Compression relaxed.

**Steel shot on stainless.** Iron contamination and corrosion sites.

**Broken media not removed.** It cuts rather than dimples.

**Partial coverage.** The benefit is lost disproportionately.

**Intensity quoted without the strip.** Meaningless.

**One side of a thin section peened.** The part bows.

---

## Worked numbers

From [`SurfaceTreatment`](../postProcessingLibrary/SurfaceTreatment.py), Ti-6Al-4V annealed at 0.20A with ceramic bead:

| Quantity | Value |
|---|---|
| Compressive layer depth | 0.170 mm |
| Surface compressive stress | -440 MPa (0.5 x yield) |
| Coverage at 2x saturation | 100 % |
| **Fatigue improvement factor** | **1.343** |

At 20 seconds against a 60 second saturation time, coverage falls to 28 percent and the fatigue factor collapses to near 1.0. **The last few percent of coverage take as long as the first eighty.**

---

## Standards

| Standard | Scope |
|---|---|
| **SAE AMS 2430** | Shot peening, automatic |
| SAE AMS 2432 | Computer monitored shot peening |
| **SAE J442** | Test strip, holder and gage for shot peening |
| SAE J443 | Procedures for using standard shot peening test strip |
| SAE J444 | Cast shot and grit size specifications |
| SAE J827 | High carbon cast steel shot |
| AMS 2431 | Peening media, general requirements |

---

## Tool interface

```python
from SurfaceTreatment import SurfaceTreatment, ALMEN_STRIPS, PEENING_MEDIA

for time in (20.0, 60.0, 120.0):
    treatment = SurfaceTreatment()
    treatment.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed',
                         'alloyFamily': 'titanium', 'wallThickness': 0.006,
                         'peeningTime': time, 'saturationTime': 60.0})
    result = treatment.calculatePeening()
    print(f'{time:5.0f} s: coverage {result["coverage"]*100:5.1f} %, '
          f'fatigue x{result["fatigueImprovementFactor"]:.3f}')
```

---

## References

1. SAE AMS 2430T, *Shot Peening, Automatic*.
2. Champaigne, J., "Shot Peening Overview", Electronics Inc., 2001.
3. Torres, M. A. S. and Voorwald, H. J. C., "An Evaluation of Shot Peening, Residual Stress and Stress Relaxation on the Fatigue Life of AISI 4340 Steel", *International Journal of Fatigue*, Vol. 24, 2002.
