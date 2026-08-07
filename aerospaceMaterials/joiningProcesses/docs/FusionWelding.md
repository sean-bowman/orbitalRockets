[Home](../README.md) > Fusion Welding

# Fusion Welding

## Contents

- [Overview](#overview)
- [The processes](#the-processes)
- [The heat affected zone](#the-heat-affected-zone)
- [Filler selection](#filler-selection)
- [Ferrite number](#ferrite-number)
- [Distortion](#distortion)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Fusion welding melts the parent material and solidifies it. That produces a cast structure in the fusion zone, an overaged or transformed structure beside it, and a residual stress field around both. The design problem is that all three sit at a geometric discontinuity.

---

## The processes

| Process | Heat input | Penetration | Distortion | Use |
|---|---|---|---|---|
| **GTAW (TIG)** | Moderate | Moderate | Moderate | **The aerospace general answer.** Clean, controllable |
| GMAW (MIG) | High | Good | High | Thicker sections, higher rate |
| **EBW** | **Very low** | **Very deep** | **Very low** | **Thick single pass, vacuum** |
| **LBW** | Low | Deep | Low | Fast, no vacuum, precise |
| Plasma arc | Moderate | Good, keyhole | Moderate | Between GTAW and EBW |
| Resistance spot | Local | Local | Low | Sheet, at rate |

**GTAW is the aerospace default** because it is the cleanest and the most controllable, and because it can be done manually where access is difficult and automatically where it is not.

**Electron beam welding gives the deepest penetration with the least heat**, so a 25 mm section welds in one pass with a narrow HAZ and very little distortion. The vacuum chamber is the constraint, and it sets the part size.

**Laser beam welding gets most of the EBW benefit without the vacuum**, which is why it has displaced EBW in many applications. It is more sensitive to joint fit-up because the beam is small.

---

## The heat affected zone

**The parent material that was heated enough to change but not enough to melt**, and it is usually the weakest part of the joint.

| Material | HAZ effect | Knockdown |
|---|---|---|
| **6061-T6** | **Overageing** | **0.50** |
| 2219-T87 | Overageing | 0.70 |
| 7075 | Hot cracking. Not weldable | -- |
| **316L** | Little, if L grade | 0.90 to 1.00 |
| 316 | **Sensitization** | Corrosion, not strength |
| **IN718** | Some, and manageable | 0.85 to 0.95 |
| Ti-6Al-4V | Coarsening, alpha case if unshielded | 0.90 |

**Overageing is the aluminium mechanism.** The weld heat takes the HAZ through the ageing range and past it, coarsening the precipitates that provide the strength. Nothing in the welding process prevents it, and the only recovery is a post-weld solution treatment and age.

**Sensitization is the stainless mechanism** and it is a corrosion problem rather than a strength one. L grades and stabilised grades avoid it. See [wroughtMaterials StainlessSteels.md](../../wroughtMaterials/docs/StainlessSteels.md).

**The HAZ width scales with the heat input**, which is the argument for EBW and LBW: a narrower HAZ means a smaller fraction of the structure is knocked down.

---

## Filler selection

| Parent | Filler | Notes |
|---|---|---|
| 6061 | **4043** | Si bearing. Lower cracking, lower strength |
| 6061 | **5356** | Mg bearing. Higher strength, less fluid |
| 2219 | **2319** | Matching. The tank filler |
| 316L | **316L** | Matching |
| 304L | 308L | Slightly higher alloy, for dilution |
| IN718 | **IN718** or 625 | 625 for dissimilar and for ductility |
| Ti-6Al-4V | **Matching, or CP Ti** | CP for ductility |

**Filler is not always matching.** 308L on 304L is deliberately higher in chromium and nickel to compensate for dilution with the parent, so the weld metal composition ends up where it should be.

**4043 against 5356 on 6061 is a real choice.** 4043 is more crack resistant and gives a lower strength weld; 5356 gives higher strength and is more prone to cracking and to sensitization if the service temperature is elevated. Neither recovers the HAZ knockdown, which is a parent material effect.

**IN625 filler on IN718** gives a more ductile and crack resistant weld at lower strength, and it is used where the weld is not the critical section.

---

## Ferrite number

**Austenitic stainless weld metal needs a controlled amount of delta ferrite.**

| Ferrite number | Consequence |
|---|---|
| **0** | **Hot cracking.** Fully austenitic solidification |
| **3 to 10** | **The target.** Crack resistant |
| Above 15 | Embrittlement on thermal exposure, reduced corrosion resistance |
| Cryogenic service | **Lower is preferred.** Ferrite is BCC and it has a DBTT |

**Delta ferrite prevents solidification cracking** by changing the solidification mode. A fully austenitic weld concentrates sulphur and phosphorus in low melting films at the grain boundaries; a ferritic-austenitic solidification dissolves them.

**The WRC-1992 diagram predicts the ferrite number** from the chromium and nickel equivalents, and it is what [`Weld`](../../../fluidSystems/fluidSystemsLibrary/Weld.py) implements.

**Cryogenic service wants low ferrite** because delta ferrite is BCC and undergoes a ductile-to-brittle transition, so a weld with 10 FN has BCC islands in an FCC matrix at 20 K. The tension between cracking resistance and cryogenic toughness is real and it is resolved by aiming at the low end of the range.

---

## Distortion

| Type | Cause |
|---|---|
| **Transverse shrinkage** | Across the weld |
| **Longitudinal shrinkage** | Along it |
| **Angular** | More shrinkage at the top of a V groove than the root |
| Buckling | Thin sheet, compressive residual stress |

| Control | Detail |
|---|---|
| **Balanced welding** | Alternate sides of a double V |
| **Back-step and skip sequences** | Distribute the heat |
| **Fixturing** | Restrain during welding, and it raises the residual stress |
| **Pre-setting** | Set the parts to spring into position |
| Lower heat input | EBW, LBW |
| Post-weld stress relief | Where the material allows |

**Restraint trades distortion for residual stress.** A heavily fixtured weld comes out straight and highly stressed, and the stress reappears as distortion when material is machined off later or as a cracking risk during welding.

**Pre-setting is the elegant answer** where the distortion is repeatable: the parts are assembled deliberately out of position by the predicted distortion, and the weld pulls them into place.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| GTAW as the aerospace default | Clean and controllable |
| EBW and LBW for narrow HAZ | Less knockdown, less distortion |
| 6061-T6 as-welded | 138 MPa, 0.50 |
| Ferrite number 3 to 10 | Low end for cryogenic |
| Filler is not always matching | Dilution |
| Restraint trades distortion for residual stress | |
| Full penetration for pressure boundaries | Inspectability |

---

## Failure modes

**As-welded aluminium designed at parent strength.** Half the capability.

**Fully austenitic weld metal, FN 0.** Hot cracking.

**High ferrite weld in cryogenic service.** BCC islands with a DBTT.

**316 rather than 316L welded thick.** Sensitized HAZ.

**7075 fusion welded.** Hot cracking.

**Titanium welded without adequate shielding.** Oxygen pickup and embrittlement.

**Heavily restrained weld then machined.** The residual stress reappears as distortion.

---

## Standards

| Standard | Scope |
|---|---|
| **AWS D17.1** | Fusion welding for aerospace applications |
| **NASA-STD-5006** | General welding requirements |
| AMS 2680 / 2681 | Electron beam welding |
| AMS 2694 | In-process welding of castings |
| **ASME BPVC Section IX** | Welding and brazing procedure and performance qualification |
| AWS A5 series | Filler metal specifications |
| **ANSI/AWS A4.2** | Ferrite number measurement, WRC-1992 |
| ASTM E1417 / E1742 | Penetrant and radiographic examination |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../../fluidSystems/fluidSystemsLibrary')

from Weld import Weld

for material in ('6061-T6', '316L', 'INCONEL 718'):
    weld = Weld()
    weld.setInputs({'material': material, 'jointType': 'butt full penetration',
                    'outerDiameter': 0.050, 'wallThickness': 0.003})
    result = weld.calculateDerating()
    print(f'{material:14s} joint efficiency {result["jointEfficiency"]:.2f}, '
          f'HAZ yield factor {result["hazYieldFactor"]:.2f}')
```

---

## References

1. Kou, S., *Welding Metallurgy*, 2nd ed., Wiley, 2003.
2. AWS D17.1, *Specification for Fusion Welding for Aerospace Applications*.
3. Kotecki, D. J. and Siewert, T. A., "WRC-1992 Constitution Diagram for Stainless Steel Weld Metals", *Welding Journal*, Vol. 71, 1992.
