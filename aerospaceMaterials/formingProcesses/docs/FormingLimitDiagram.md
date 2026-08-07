[Home](../README.md) > Forming Limit Diagram

# Forming Limit Diagram

## Contents

- [Overview](#overview)
- [The strain space](#the-strain-space)
- [Why plane strain is the worst case](#why-plane-strain-is-the-worst-case)
- [FLD0](#fld0)
- [Using the diagram](#using-the-diagram)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The forming limit diagram answers whether a given point on a formed part will split. It is plotted in principal strain space and its central and counter-intuitive feature is that the limit is lowest in the middle.

---

## The strain space

Every point on a formed sheet experiences two in-plane principal strains: major `eps_1` and minor `eps_2`, with `eps_1 >= eps_2`.

| Strain path | eps_2 / eps_1 | Where it occurs |
|---|---|---|
| **Uniaxial tension** | -0.5 | A narrow strip being stretched |
| **Plane strain** | **0** | **A long bend, a wall between two features** |
| **Biaxial stretch** | +1 | A dome apex, a hemispherical punch |
| Drawing | < -0.5 | Material being drawn in, thickening |

**The forming limit curve is a V** in this space, with its minimum at plane strain and both arms rising away from it.

---

## Why plane strain is the worst case

**Because the minor strain provides no thinning relief.**

Volume is conserved in plastic deformation, so the thickness strain is

```
eps_3 = -(eps_1 + eps_2)
```

| Path | eps_2 | eps_3 for eps_1 = 0.2 |
|---|---|---|
| Uniaxial | -0.10 | -0.10 |
| **Plane strain** | **0** | **-0.20** |
| Biaxial | +0.20 | -0.40 |

**Under uniaxial tension the material narrows as well as thins**, so a given major strain costs less thickness. Under plane strain it cannot narrow, so all the deformation goes into thinning.

**Under biaxial stretch it thins even faster, yet the limit is higher.** That is the part that surprises people, and the reason is that biaxial stretching stabilises against necking: a neck forming in one direction is resisted by the tension in the other, so the material can carry more strain before instability.

**Plane strain gets the worst of both.** No narrowing relief and no biaxial stabilisation.

**The design consequence is direct: plane strain regions are where parts split**, and they are the regions least likely to look dangerous. A long straight bend and a flat wall between two features are both plane strain, and both look benign next to a deep drawn corner.

---

## FLD0

**The height of the curve at plane strain**, and the single number that characterises a material's stretch formability.

The Keeler-Brazier correlation gives it from the work hardening exponent and the thickness:

```
FLD0 = (23.3 + 14.13 * t_mm) * n / 21.0        for n <= 0.21
FLD0 = (23.3 + 14.13 * t_mm) * 0.21 / 21.0     for n > 0.21
```

| Material | n | Thickness | FLD0 |
|---|---|---|---|
| **316L annealed** | 0.45 | 2 mm | ~0.52 |
| 6061-O | 0.22 | 2 mm | ~0.52 |
| **6061-T6** | 0.05 | 2 mm | **~0.12** |
| Ti-6Al-4V | 0.08 | 2 mm | ~0.19 |

**Two features of the correlation matter.**

**It saturates at n = 0.21.** Above that, more work hardening does not raise the forming limit further, which is why 316L at n = 0.45 and 6061-O at n = 0.22 have the same FLD0.

**Thicker sheet forms better.** The `14.13 * t_mm` term says a 3 mm sheet has a higher limit than a 1 mm one of the same material, because a thicker sheet resists through-thickness necking.

**6061-T6 at FLD0 = 0.12 is barely formable**, and that number is the quantitative statement of the rule to form in the annealed condition.

---

## Using the diagram

| Step | Detail |
|---|---|
| **1. Get the strain field** | From forming simulation, or circle grid analysis on a trial part |
| **2. Plot each point** | In `eps_1`, `eps_2` space |
| **3. Compare against the curve** | For that material and thickness |
| **4. Apply a safety margin** | 10 % below the curve is conventional |
| **5. Fix the worst points** | Blank shape, lubrication, draw bead, radius |

**Circle grid analysis is the physical measurement.** A grid of small circles is etched on the blank before forming; after forming they are ellipses, and the major and minor axes give the two principal strains directly at every point.

**The 10 percent margin is not optional.** The FLD is a necking limit determined on ideal specimens, and real parts have thickness variation, lubrication variation and strain rate effects.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| The limit is lowest at plane strain | And that is where parts split |
| `eps_3 = -(eps_1 + eps_2)` | Volume conservation |
| FLD0 saturates at n = 0.21 | More hardening does not help further |
| Thicker sheet forms better | The `14.13 t` term |
| Safety margin | 10 % below the curve |
| Circle grid analysis | The physical measurement |
| 6061-T6 FLD0 ~0.12 | Barely formable. Form annealed |

---

## Failure modes

**Only the deep drawn corners checked.** The split happens in a plane strain wall.

**Biaxial regions assumed worst because they thin fastest.** The limit is higher there.

**FLD applied without a margin.** It is a necking limit on ideal specimens.

**T6 temper formed to an annealed strain field.** FLD0 four times lower.

**Strain path change ignored.** A non-proportional path invalidates the standard FLD.

---

## Worked numbers

From [`FormingProcess.checkFormingLimit`](../formingProcessesLibrary/FormingProcess.py), 2 mm sheet, at plane strain:

| Material | n | FLD0 | Limit at plane strain |
|---|---|---|---|
| **316L annealed** | **0.45** | **0.636** | 0.636 |
| 6061-T6 | 0.20 | 0.283 | 0.283 |
| 2219-T87 | 0.18 | 0.255 | 0.255 |

**The thickness factor is 1.414 at 2 mm**, which is the `sqrt(t/t_ref)` scaling in the class against a 1 mm reference. Thicker sheet forms further, as the correlation says it should.

**316L reaches 2.25 times the limit strain of 6061-T6**, which is the practical statement of why austenitic stainless is the best formable structural metal.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM E2218** | Determining forming limit curves |
| ISO 12004 | Metallic materials, determination of forming limit curves |
| ASTM E646 | Tensile strain hardening exponents of sheet |
| ASTM E517 | Plastic strain ratio r for sheet |

---

## Tool interface

```python
from FormingProcess import FormingProcess

forming = FormingProcess()
forming.setInputs({'material': '6061', 'condition': 't6', 'process': 'stretch form',
                   'thickness': 0.002})

for path, minor in (('uniaxial', -0.05), ('plane strain', 0.0), ('biaxial', 0.10)):
    result = forming.checkFormingLimit(majorStrain = 0.10, minorStrain = minor)
    print(f'{path:14s} ' + '  '.join(f'{k}={result[k]}' for k in sorted(result)
                                     if not isinstance(result[k], (dict, list))))
```

---

## References

1. Keeler, S. P. and Brazier, W. G., "Relationship Between Laboratory Material Characterization and Press-Shop Formability", *Microalloying 75*, 1977.
2. Marciniak, Z., Duncan, J. L. and Hu, S. J., *Mechanics of Sheet Metal Forming*, 2nd ed., Butterworth-Heinemann, 2002.
3. ASTM E2218, *Standard Test Method for Determining Forming Limit Curves*.
