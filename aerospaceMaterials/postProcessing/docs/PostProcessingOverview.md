[Home](../README.md) > Post-Processing Overview

# Post-Processing Overview

## Contents

- [Overview](#overview)
- [What these processes have in common](#what-these-processes-have-in-common)
- [The catalogue](#the-catalogue)
- [Order matters](#order-matters)
- [Where HIP went](#where-hip-went)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [Document index](#document-index)
- [References](#references)

---

## Overview

Everything done to a part after it exists that changes its properties or its surface. Peening, chemical milling, electropolishing, anodising, plating, thermal spray and vibratory finishing.

They are grouped together because they share a failure mode: each one is easy to specify, and each one interacts with the others in ways that a drawing note does not capture.

---

## What these processes have in common

**Fatigue cracks start at surfaces.** Almost every process here exists to change that, either by putting the surface into compression so a crack cannot open, or by removing the layer that would have started one.

| Approach | Processes |
|---|---|
| **Put the surface in compression** | Shot peening, laser shock peening |
| **Remove the damaged layer** | Chemical milling, electropolishing, machining |
| **Cover it** | Plating, anodising, thermal spray |
| **Smooth it** | Vibratory finishing, electropolishing, laser polishing |

**The second and third categories fight each other.** A plating operation charges hydrogen into the substrate; an etch removes stock from both sides; and an electropolish removes the compressive layer a peening operation just created.

---

## The catalogue

| Process | Does | Costs |
|---|---|---|
| **Shot peening** | Compressive layer, 15 % fatigue gain | Surface roughening |
| **Laser shock peening** | 4 to 5x the layer depth, no roughening | Cost |
| **Chemical milling** | Uniform stock removal, no residual stress | Removes from both sides. No finish improvement |
| **Electropolishing** | Removes peaks, improves Ra to 0.4 um | Removes any compressive layer |
| **Anodising** | Corrosion protection, hardness | A real fatigue debit |
| **Plating** | Corrosion, wear, conductivity | Hydrogen charging above 1000 MPa |
| **Thermal spray** | Wear surfaces, dimensional restoration | Residual stress from CTE mismatch |
| **Vibratory finishing** | Edge break and Ra on external surfaces | Rounds edges that were meant to be sharp |

---

## Order matters

**Several of these processes undo each other, and the order is the control.**

| Rule | Reason |
|---|---|
| **Peen last** | Electropolish or chem mill afterwards removes the layer |
| **Bake immediately after plating** | Within four hours, or the crack has already started |
| **Remove alpha case before anything else** | It is a fatigue initiation site under any coating |
| **Machine before peening** | Machining removes the layer |
| Stress relieve before peening | A relief afterwards relaxes the compression |
| Chem mill before final dimensioning | It changes the wall |

**The single most common sequencing error is electropolishing after peening.** Both are common, both are beneficial, and in that order the second undoes the first completely.

---

## Where HIP went

**Hot isostatic pressing is deliberately not in this sub-domain.**

It is a thermal cycle at pressure and it interacts directly with solution treatment and aging: the HIP cycle for a precipitation hardened nickel alloy runs above the gamma prime solvus, so it dissolves the strengthening precipitate and a full solution treat and age has to follow.

That interaction belongs with the other thermal cycles, so HIP lives in [aerospaceMaterials HeatTreatment](../../docs/HeatTreatment.md) and in the [`HeatTreatment`](../../aerospaceMaterialsLibrary/HeatTreatment.py) class.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Peen last | After every removal process |
| Bake within 4 h of plating | The window matters as much as the bake |
| Bake trigger | 1000 MPa ultimate |
| Chem mill removes from both sides | A 0.15 mm etch takes 0.3 mm off a wall |
| Chem mill does not improve Ra | Electropolish does |
| Alpha case removal | A required specification for hot formed titanium |
| Anodising carries a fatigue debit | Type III more than Type II |
| Thermal spray | Check the CTE mismatch sign |

---

## Failure modes

**Electropolish after peening.** The compressive layer is gone.

**Plating bake started late.** The crack initiated during the delay.

**Chem mill sized for one surface.** The wall is half what was intended.

**Alpha case left under a coating.** A fatigue initiation site nobody can see.

**Anodising specified on a fatigue critical part.** A debit nobody accounted for.

**Vibratory finishing on a part with a sharp orifice.** The entry is rounded.

---

## Worked numbers

From [`SurfaceTreatment`](../postProcessingLibrary/SurfaceTreatment.py), Ti-6Al-4V annealed:

| Quantity | Value |
|---|---|
| Ceramic bead peening, 0.20 mm A intensity | 0.170 mm compressive layer |
| Surface compressive stress | -440 MPa |
| Coverage at 2x saturation time | 100 % |
| **Fatigue improvement factor** | **1.343** |
| Laser shock peening, same intensity | **0.765 mm layer, 4.5x deeper** |
| Laser shock fatigue factor | 1.541 |

| Chemical mill, 10 minutes at 25 um/min | Value |
|---|---|
| Removal per surface | 0.250 mm |
| **Removal from the wall** | **0.500 mm** |
| A 3.00 mm wall becomes | 2.50 mm |

---

## Standards

| Standard | Scope |
|---|---|
| **SAE AMS 2430** | Shot peening, automatic |
| SAE AMS 2432 | Computer monitored shot peening |
| **ASTM F1940** | Process control to prevent hydrogen embrittlement in plating |
| ASTM F519 | Mechanical hydrogen embrittlement evaluation |
| AMS 2759/9 | Hydrogen embrittlement relief baking |
| AMS 2488 | Anodic treatment of titanium |
| MIL-A-8625 | Anodic coatings for aluminium |
| AMS 2700 | Passivation of corrosion resistant steels |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'postProcessingLibrary')

from SurfaceTreatment import SurfaceTreatment

treatment = SurfaceTreatment()
treatment.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed',
                     'alloyFamily': 'titanium', 'wallThickness': 0.003,
                     'almenIntensity': 0.20e-3, 'peeningMedia': 'ceramic bead'})

treatment.calculatePeening()
treatment.calculateAlphaCase(1123.15, 3600.0)
treatment.checkPlatingBake('cadmium')
print(treatment.generateReport())
```

---

## Document index

| Document | Covers |
|---|---|
| [ShotPeening.md](ShotPeening.md) | Almen intensity, coverage, the compressive layer |
| [LaserShockPeening.md](LaserShockPeening.md) | Deeper layer, no roughening, and the cost |
| [ChemicalMilling.md](ChemicalMilling.md) | Uniform removal, both surfaces, masking |
| [AlphaCaseRemoval.md](AlphaCaseRemoval.md) | Titanium oxygen dissolution and its removal |
| [Electropolishing.md](Electropolishing.md) | Peak removal, the Ra floor, and what it undoes |
| [AnodisingAndConversion.md](AnodisingAndConversion.md) | Aluminium coatings and the fatigue debit |
| [Plating.md](Plating.md) | Nickel, cadmium, silver, and the hydrogen problem |
| [HydrogenBakeout.md](HydrogenBakeout.md) | ASTM F1940, the trigger and the window |
| [ThermalSpray.md](ThermalSpray.md) | HVOF, plasma, cold spray, and CTE mismatch |
| [VibratoryFinishing.md](VibratoryFinishing.md) | Edge break, Ra, and what it rounds |
| [LaserPolishing.md](LaserPolishing.md) | Remelting the surface |
| [Passivation.md](Passivation.md) | Where it overlaps the fluidSystems treatment |
| [VerificationOfSurfaceTreatments.md](VerificationOfSurfaceTreatments.md) | How each is inspected |

---

## References

1. SAE AMS 2430, *Shot Peening, Automatic*.
2. ASTM F1940-07a, *Process Control Verification to Prevent Hydrogen Embrittlement*.
3. Davis, J. R. (ed.), *Surface Engineering for Corrosion and Wear Resistance*, ASM, 2001.
4. Champaigne, J., "Shot Peening Overview", Electronics Inc., 2001.
