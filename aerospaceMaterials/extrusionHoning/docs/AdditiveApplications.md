[Home](../README.md) > Additive Applications

# Additive Applications

## Contents

- [Overview](#overview)
- [What the as-built surface actually is](#what-the-as-built-surface-actually-is)
- [What honing fixes](#what-honing-fixes)
- [What it cannot fix](#what-it-cannot-fix)
- [Residual powder](#residual-powder)
- [The design requirement it imposes](#the-design-requirement-it-imposes)
- [The loop back to fluid systems](#the-loop-back-to-fluid-systems)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Abrasive flow machining and laser powder bed fusion are complementary in a specific way: additive makes internal passages that nothing else can make, and abrasive flow is the only process that can finish them.

Neither is much use to a flow-critical additive part without the other.

---

## What the as-built surface actually is

Not simply rough. Three distinct things at once:

| Feature | Scale | Consequence |
|---|---|---|
| **Adhering partially melted particles** | 20 to 50 um | The dominant roughness term. Notches everywhere |
| **A partially sintered layer** | 50 to 200 um | Bonded to the wall, so it is effectively part of it |
| **Stair stepping** | Layer thickness | Waviness on any sloped surface |

**The sintered layer is why an as-built passage is never at its drawing dimension.** The bonded powder narrows the bore, and it is not loose so no amount of blowing or vibrating removes it.

**It is also a contamination source.** Lightly bonded particles detach under flow and migrate downstream, which in a propulsion system means into an injector, a valve seat or a catalyst bed.

---

## What honing fixes

| Problem | Fixed |
|---|---|
| **Adhering particles** | Yes. This is the primary benefit |
| **The sintered layer** | Yes, and it is the only process that does |
| **Ra 20 um to 5 um** | Yes, in about 12 cycles |
| **Sharp intersections and burrs** | Yes, as a side effect |
| Loose residual powder | Yes, it is carried out with the media |

**The 4x roughness improvement is the headline number** and the sintered layer removal is arguably more important, because that layer is a contamination source with a service life.

---

## What it cannot fix

| Problem | Why not |
|---|---|
| **Below the grit floor** | The abrasive cannot cut finer than its own scratch |
| **Internal porosity** | It works on surfaces only |
| **Lack of fusion in the wall** | Same |
| **Geometry errors** | It follows the passage, it does not straighten it |
| **A dead-ended passage** | The media has nowhere to go |
| **Passage size** | It opens the bore rather than holding it |

**The finish floor for a medium media is 5 um.** An additive passage needing better than that needs a second, finer honing stage, and below about 1.5 um it needs a different process entirely.

**A passage with a geometric error stays wrong.** The process removes material in proportion to local shear, so a passage that is oval stays oval and simply becomes a larger oval.

---

## Residual powder

Honing removes residual powder as a side effect and it should not be relied on as the powder removal method.

| Reason | Detail |
|---|---|
| Loose powder can block the media | A plug of powder stops the flow |
| The media becomes contaminated | Powder loads it and shortens its life |
| Verification is separate | Honing does not prove the passage was clear |

**Depowder first, hone second.** See [additiveLPBF InternalPassages.md](../../additiveLPBF/docs/InternalPassages.md).

---

## The design requirement it imposes

**A passage that will be honed has to be designed for it, at concept.**

| Requirement | Reason |
|---|---|
| **Both ends accessible** | The media has to flow through |
| **No dead ends** | Nowhere for the media to go |
| **A through path** | Not a blind pocket |
| Reasonable aspect ratio | Wall shear falls with length |
| Branches of similar conductance | Or they hone unevenly |
| Somewhere to seal | The fixture has to grip and seal |

**This is the highest-value point of contact between the two sub-domains.** A designer who knows the passage will be honed leaves a through path; one who does not creates a blind passage that has an as-built surface for the life of the part.

**It costs nothing at concept and it cannot be added later.**

---

## The loop back to fluid systems

**An additively manufactured manifold sized on drawn-tube roughness under-predicts its own pressure drop by a large factor.**

That claim is made in the docstring of `roughnessTable()` in [common/materials.py](../../../common/materials.py), and honing is what closes the gap.

| Surface | Ra | Relative roughness in a 4.76 mm bore |
|---|---|---|
| Drawn tube | 1.5 um | 3.2e-4 |
| **LPBF as-built** | **20 um** | **4.2e-3** |
| After abrasive flow | 5 um | 1.1e-3 |

**A relative roughness of 4.2e-3 is squarely in the fully rough region of the Moody diagram**, where the friction factor no longer falls with Reynolds number. Drawn tube at 3.2e-4 is not.

The [aerospaceMaterials worked example](../../codeInterface.py) carries this through: the manifold pressure drop before and after honing, feeding the finished roughness back into the fluidSystems [`Line`](../../../fluidSystems/fluidSystemsLibrary/Line.py) and [`Orifice`](../../../fluidSystems/fluidSystemsLibrary/Orifice.py) classes.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Design the through path at concept | It cannot be added later |
| Depowder first, hone second | Honing is not a powder removal method |
| Ra 20 to 5 um | ~12 cycles, medium media |
| The sintered layer | Only honing removes it |
| Finish floor | 5 um for medium media |
| Passage grows 1 to 3 % | Put it in the tolerance stack |
| Geometry errors are not corrected | Only surfaces are |
| Feed the honed roughness back into the flow analysis | Not the drawn tube value |

---

## Failure modes

**A blind additive passage.** As-built surface for life.

**Manifold sized on drawn-tube roughness.** Pressure drop badly under-predicted.

**Sintered layer left in place.** Contamination source downstream.

**Honing relied on for powder removal.** A powder plug stops the media.

**Orifice sized before honing.** It grew.

**Better than 5 um expected from a coarse media.** The floor is the floor.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM F3335** | Assessing removal of additive manufacturing residues |
| NASA-STD-6030 | Additive manufacturing requirements |
| MSFC-STD-3716 | LPBF spaceflight hardware |
| ISO 4287 / 21920 | Surface texture |

---

## Tool interface

```python
from ExtrusionHoning import ExtrusionHoning
from materials import roughnessTable

honing = ExtrusionHoning()
honing.setInputs({'passageDiameter': 0.00476, 'passageLength': 0.180,
                  'material': 'Inconel 718', 'condition': 'lpbf hip + sta',
                  'cycleCount': 12})
honing.calculateWallShear()
finish = honing.calculateSurfaceFinish()

print(finish['initialRoughness'], roughnessTable('lpbf as-built'))       # they agree
print(finish['finalRoughness'],   roughnessTable('lpbf abrasive flow'))  # and so do these
print(finish['improvementRatio'])                                        # 4.0
```

---

## References

1. Gradl, P. R. et al., *Metal Additive Manufacturing for Propulsion Applications*, AIAA, 2022.
2. ASTM F3335-20, *Standard Guide for Assessing the Removal of Additive Manufacturing Residues*.
3. Peng, C. et al., "Abrasive Flow Machining of Additively Manufactured Internal Channels", *Journal of Manufacturing Processes*, Vol. 60, 2020.
