[Home](../README.md) > Media and Rheology

# Media and Rheology

## Contents

- [Overview](#overview)
- [What the media is](#what-the-media-is)
- [Shear thinning](#shear-thinning)
- [Media grades](#media-grades)
- [Abrasive selection](#abrasive-selection)
- [Media life](#media-life)
- [Temperature](#temperature)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The media is the tool, and unlike every other tool it changes shape to fit the work. Understanding its rheology is understanding why the process reaches where it does and why it removes what it does.

---

## What the media is

A viscoelastic polymer carrier, usually a silicone-based putty, loaded with abrasive grit to 30 to 60 percent by volume.

| Component | Role |
|---|---|
| **Carrier** | Holds the abrasive in suspension and transmits force to it |
| **Abrasive** | Does the cutting |
| Plasticiser | Adjusts the viscosity without changing the abrasive loading |

**The carrier has to do two contradictory things.** It must be stiff enough to hold the abrasive in suspension and to fill the fixture without slumping, and it must flow through a passage a fraction of a millimetre across at a practical pressure.

**Shear thinning is what resolves the contradiction.**

---

## Shear thinning

The media follows a power law:

```
tau = K * gammaDot^n
```

with `n` well below one, typically 0.22 to 0.32.

**What that means physically:** at rest the apparent viscosity is enormous and the media behaves almost as a solid. Under the high shear rate inside a passage the apparent viscosity collapses by orders of magnitude and it flows.

| Condition | Behaviour |
|---|---|
| At rest in the cylinder | Effectively solid. Holds its shape, holds the abrasive |
| Extruded into a passage | Shear rate rises, viscosity collapses, it flows |
| Leaving the passage | Recovers, and it does not run out of the fixture |

**A lower `n` means more strongly shear thinning**, and the harder grades have the lower values. That is why a hard media can be stiff enough to load a large bore heavily and still be extrudable at all.

---

## Media grades

| Grade | K [Pa s^n] | n | Grit [um] | Passage range | Removal |
|---|---|---|---|---|---|
| **Very soft** | 2.0e3 | 0.32 | 60 | 0.3 to 3 mm | 0.45x |
| **Soft** | 6.0e3 | 0.30 | 110 | 0.8 to 8 mm | 0.70x |
| **Medium** | 1.6e4 | 0.28 | 200 | 2 to 20 mm | 1.00x |
| **Hard** | 4.5e4 | 0.25 | 350 | 5 to 50 mm | 1.60x |
| **Very hard** | 1.2e5 | 0.22 | 550 | 12 to 100 mm | 2.40x |

**Grade selection is by passage size first.** A media too stiff for the passage will not flow through it at any practical pressure; one too soft passes through without loading the wall.

**Grit size sets the finish floor.** Roughly `gritSize / 40`, so medium media floors at 5 um and very soft at 1.5 um. **A finer finish requires a finer media in a second setup**, and that is a real cost that has to be planned.

---

## Abrasive selection

| Abrasive | Hardness [HV] | Efficiency | Use |
|---|---|---|---|
| **Silicon carbide** | 2600 | 1.00 | The default. Friable, so it self-sharpens |
| Aluminium oxide | 2100 | 0.75 | Tougher, less friable. Longer life, slower removal |
| **Boron carbide** | 3200 | 1.35 | Nickel alloys and anything that work hardens. Expensive |
| Diamond | 8000 | 1.80 | Ceramics and carbides. Rarely justified on metal |

**Friability matters as much as hardness.** A friable abrasive fractures under load and exposes fresh cutting edges, so it self-sharpens. A tough abrasive dulls and then rubs rather than cuts, which generates heat and stops removing material.

**Boron carbide on nickel alloys is worth the cost.** Inconel work hardens under a dulled abrasive, so the surface gets harder as the media gets duller, and a silicon carbide media can stall completely.

---

## Media life

Media degrades and it degrades in three ways at once.

| Mechanism | Effect |
|---|---|
| **Abrasive dulling and fracture** | Removal rate falls |
| **Loading with swarf** | The removed metal stays in the media |
| **Carrier degradation** | Shear and heat break the polymer down; viscosity falls |

**Swarf loading is the one that ends media life.** The removed metal accumulates and eventually the media is carrying more metal than abrasive, at which point it polishes rather than cuts.

**Media is a controlled consumable.** Its viscosity should be measured periodically, and its replacement should be on a schedule tied to throughput rather than on the operator's judgement. A programme running a qualified process has media life in the process specification.

---

## Temperature

Media heats as it is worked, and viscosity falls with temperature.

**A rising temperature during a cycle means a falling viscosity, a falling wall shear, and a falling removal rate.** A part honed at the start of a shift and one honed at the end are not the same part unless the temperature is controlled.

| Control | Effect |
|---|---|
| Cooled media reservoir | The usual answer |
| Cycle time limits | Let it cool between parts |
| Temperature monitoring | So the drift is visible |

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Flow index n | 0.22 to 0.32 |
| Abrasive loading | 30 to 60 % by volume |
| Grade selection | By passage size first |
| Finish floor | grit / 40 |
| Silicon carbide | The default, and it self-sharpens |
| Boron carbide | Nickel alloys, worth the cost |
| Media life | On a schedule, not a judgement |
| Temperature | Controlled, or the removal drifts |

---

## Failure modes

**Media too stiff for the passage.** It does not flow at any pressure.

**Media too soft.** It passes through without loading the wall.

**Dulled abrasive on a work hardening alloy.** The surface hardens and the process stalls.

**Swarf-loaded media.** It polishes rather than cuts.

**Uncontrolled temperature.** Removal drifts through the shift.

**A finer finish attempted with the same media.** The floor is the floor.

---

## Standards

| Standard | Scope |
|---|---|
| ASTM D2196 | Rheological properties of non-Newtonian materials |
| ISO 8130 | Powder coatings, particle size, cited for abrasive sizing practice |
| FEPA F and P grades | Abrasive grit size designation |
| ISO 4287 / 21920 | Surface texture |

---

## Tool interface

```python
from ExtrusionHoning import ExtrusionHoning, MEDIA_GRADES, ABRASIVE_TYPES

for grade, entry in MEDIA_GRADES.items():
    print(f'{grade:10s} K={entry["consistencyIndex"]:.0e}  n={entry["flowIndex"]:.2f}  '
          f'grit={entry["gritSize"]*1e6:.0f} um  '
          f'floor={entry["gritSize"]/40*1e6:.2f} um')

honing = ExtrusionHoning()
honing.setInputs({'passageDiameter': 0.0010})
print(honing.mediaGrade)        # selected automatically from the passage size
```

---

## References

1. Jain, V. K., *Advanced Machining Processes*, Allied Publishers, 2009.
2. Williams, R. E. and Rajurkar, K. P., "Stochastic Modeling and Analysis of Abrasive Flow Machining", *Journal of Engineering for Industry*, Vol. 114, 1992.
3. Kumar, S. et al., "A Review on Abrasive Flow Machining", *Materials Today Proceedings*, Vol. 5, 2018.
