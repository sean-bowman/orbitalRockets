[Home](../README.md) > Defects

# Defects

## Contents

- [Overview](#overview)
- [The catalogue](#the-catalogue)
- [Banding](#banding)
- [Raining](#raining)
- [Cold shut](#cold-shut)
- [Hot tearing](#hot-tearing)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Most centrifugal casting defects trace to the rotational speed being wrong, the pour being wrong, or the mould thermal condition being wrong. Knowing which tells you what to change.

---

## The catalogue

| Defect | Appearance | Cause | Fix |
|---|---|---|---|
| **Banding** | Circumferential segregation bands | Unsteady front motion, high G | Lower the speed, more superheat |
| **Raining** | Thick bottom, thin top, entrapped oxide | G-factor too low | Raise the speed |
| **Cold shut** | A seam where two fronts met | Insufficient superheat or slow pour | More superheat, faster pour |
| **Hot tearing** | Longitudinal cracks | Restrained contraction, high G | Lower G, mould taper |
| **Gas porosity** | Rounded pores near the bore | Dissolved gas rejected on freezing | Degas the melt |
| **Shrinkage** | Near the bore | Inadequate feeding | Higher G, more superheat |
| Inclusions in the wall | Trapped oxide | Low capture number | Raise G, cleaner melt |
| Mould coating inclusions | Refractory in the casting | Coating thrown at high G | Lower G, better coating adhesion |

---

## Banding

**The characteristic centrifugal casting defect** and the one that bounds the speed at the top end.

Circumferential bands of segregated composition, visible on a machined bore or in a section, spaced along the length or through the wall.

**The mechanism is unsteady solidification front motion.** The front does not advance smoothly; it stalls and surges, and at each stall the enriched liquid ahead of it accumulates and then gets trapped when the front moves again.

| Contributor | Effect |
|---|---|
| **High G-factor** | Pins the melt, so it cannot move to even out composition |
| **Wide freezing range** | A longer mushy zone, more opportunity |
| **Low superheat** | A less stable front |
| Mould thermal variation | Drives the stall-surge cycle |

**The model in this sub-domain does not predict banding**, and that is worth being explicit about. Chvorinov gives a mean solidification time and says nothing about whether the front moved smoothly. Predicting bands needs a transient thermal model.

---

## Raining

**The classic under-speed failure**, and it is unmistakable.

At the top of the arc the melt is held against the mould by the centrifugal field acting against gravity. Below about G = 40 the field is not strong enough with margin, so the melt detaches and falls through the bore.

| Symptom | Cause |
|---|---|
| Thick at the bottom, thin at the top | The fallen metal accumulated |
| Entrapped oxide throughout | The falling metal broke its oxide skin repeatedly |
| Rough, irregular bore | The free surface was never stable |

**Check the G-factor at the bore, not the outer wall**, because the free surface is at the bore and that is where the raining criterion applies. See [RotationalSpeed.md](RotationalSpeed.md).

---

## Cold shut

Two advancing fronts of melt meet and do not fuse, leaving a seam.

| Cause | Fix |
|---|---|
| Insufficient superheat | More |
| Slow pour | Faster |
| Mould too cold | More preheat |
| Long mould, single pour point | Traversing spout |

**On a long horizontal casting it usually appears part way along**, where the melt poured at one end met melt that had run further and started to freeze.

---

## Hot tearing

Longitudinal cracks, formed while the casting is still partly liquid.

**The mechanism is restrained contraction.** The casting contracts onto the mould as it solidifies, and the mould does not contract with it. The semi-solid material has almost no strength and it tears.

| Contributor | Effect |
|---|---|
| **High G-factor** | The melt cannot move to feed the tear |
| **A cylindrical mould with no taper** | The casting grips it |
| Wide freezing range | Longer time in the vulnerable state |
| Sharp section changes | Stress concentration |

**A slight mould taper is the standard fix** and it also helps extraction.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Banding bounds the speed at the top | ~150 G |
| Raining bounds it at the bottom | ~40 G, checked at the bore |
| Cold shut | Superheat and pour rate |
| Hot tearing | Mould taper, and lower G |
| Gas porosity collects at the bore | Where it is machined away |
| Coating inclusions | Above ~150 G |
| The model does not predict banding | Be explicit about it |

---

## Failure modes

**Speed set at the top of the window on a wide freezing range alloy.** Banding.

**Speed set from the outer wall on a thick casting.** The bore rains.

**Single pour point on a long mould.** Cold shut part way along.

**No mould taper.** Hot tearing and difficult extraction.

**Melt not degassed.** Porosity, and it is concentrated where it is at least machined away.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM E446 / E186 / E280** | Reference radiographs for steel castings, by thickness |
| ASTM A802 | Steel castings, surface acceptance standards |
| ASTM E45 | Inclusion content of steel |
| ASTM E1417 | Liquid penetrant testing |
| ASTM E114 | Ultrasonic pulse-echo straight beam examination |

---

## References

1. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
2. ASM Handbook Volume 15, *Casting*.
3. Janco, N., *Centrifugal Casting*, American Foundrymen's Society, 1988.
