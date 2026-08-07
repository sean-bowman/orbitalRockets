[Home](../README.md) > Alpha Case Removal

# Alpha Case Removal

## Contents

- [Overview](#overview)
- [What alpha case is](#what-alpha-case-is)
- [Where it comes from](#where-it-comes-from)
- [How deep](#how-deep)
- [Removing it](#removing-it)
- [Detecting it](#detecting-it)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Titanium heated in air above about 530 degC dissolves oxygen from the atmosphere, forming a hard, brittle, oxygen-enriched surface layer called alpha case.

It is a fatigue crack initiation site, its removal is a required specification rather than an optional refinement, and the removal depth has to be added to the stock dimension because it comes off the wall.

---

## What alpha case is

**Not an oxide scale.** An oxide flakes off and can be pickled away. Alpha case is oxygen in solid solution in the metal itself, stabilising the alpha phase, and the only way to remove it is to remove the metal.

| Property | Effect |
|---|---|
| Hardness | Substantially higher than the parent |
| Ductility | Effectively zero |
| Fracture | Brittle, and it cracks under any strain |
| Appearance | Often invisible. Sometimes a colour change |

**The layer cracks under load and those cracks propagate into the parent.** That is why a hot formed titanium part with the case left on has a fatigue strength a fraction of the parent material.

---

## Where it comes from

| Source | Typical exposure |
|---|---|
| **Hot forming** | 700 to 950 degC for minutes to hours |
| **Heat treatment in air** | Any cycle without vacuum or inert cover |
| **Welding without back purge** | Local, at the weld and the HAZ |
| Casting | The whole surface |
| Grinding without coolant | Local, and it can be severe |

**The fix upstream is inert cover.** Vacuum or argon during any thermal cycle prevents the case forming at all, and it is far cheaper than removing it afterwards.

**Welding is the case people forget.** Full inert shielding of the weld, the heat affected zone and the back side is required, and discolouration other than light straw is a rejection criterion because the colour is an oxide thickness gauge that correlates with the pickup.

---

## How deep

Oxygen diffusion follows a parabolic law with an Arrhenius diffusivity:

```
depth = sqrt(D * t)         D = D0 * exp(-Q / (R * T))
```

**Depth goes as the square root of time**, so doubling the exposure increases the case by only 41 percent. **It goes exponentially with temperature**, so 50 degrees hotter matters far more than twice as long.

| Exposure | Approximate case depth |
|---|---|
| 700 degC, 1 h | Negligible |
| 850 degC, 1 h | Tens of micrometres |
| 950 degC, 1 h | Approaching 0.1 mm |
| 950 degC, 4 h | Twice that |

**Below about 530 degC the rate is negligible** and no case forms in any practical time.

---

## Removing it

| Method | Notes |
|---|---|
| **Chemical milling** | The standard. Nitric and hydrofluoric acid. Removes uniformly from every surface |
| **Machining** | Where the surface is being machined anyway |
| Grit blasting | Removes scale, not case. It does not go deep enough |
| Pickling | Same. It removes the oxide and leaves the case |

**A safety factor over the computed depth is standard**, typically 1.5, because the diffusion depth is a nominal and the case boundary is diffuse rather than sharp.

**The removal comes off both surfaces** because the part is immersed, so a wall loses twice the removal depth. See [ChemicalMilling.md](ChemicalMilling.md).

**That has to be in the stock dimension.** A 0.05 mm case removed with a 1.5 factor takes 0.15 mm off a wall, and on a 1 mm section that is 15 percent.

---

## Detecting it

| Method | Notes |
|---|---|
| **Metallographic section** | The definitive method. The case etches differently |
| **Microhardness traverse** | Quantitative, and it gives the depth profile |
| Bend test | A witness coupon bent until it cracks. Crude and effective |
| Visual | Unreliable. Case can be invisible |

**Visual inspection does not find alpha case** and relying on it is the commonest way a cased part reaches service. The colour that is sometimes visible is the oxide above the case, not the case itself, and a part can be pickled clean and still be fully cased.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Forms above | ~530 degC |
| Depth | Parabolic in time, exponential in temperature |
| Removal safety factor | 1.5x the computed depth |
| Both surfaces removed | Wall loses 2x |
| Add it to the stock dimension | It cannot be added later |
| Prevent with inert cover | Cheaper than removing |
| Weld discolouration | Straw acceptable, blue marginal, grey reject |
| Visual inspection does not find it | Section or hardness traverse |

---

## Failure modes

**Case left on a hot formed part.** Fatigue strength a fraction of the parent.

**Removal not in the stock dimension.** The wall ends undersize.

**Grit blasting used to remove it.** It removes scale only.

**Pickled and assumed clean.** The oxide went, the case stayed.

**Welded without back purge.** A cased HAZ on the inside of a tube.

**Visual inspection accepted as verification.** It is invisible.

---

## Worked numbers

From [`SurfaceTreatment.calculateAlphaCase`](../postProcessingLibrary/SurfaceTreatment.py), Ti-6Al-4V on a 6 mm wall:

| Exposure | Case depth | Removal per surface | Off the wall |
|---|---|---|---|
| 700 K (427 degC), 1 h | 0.000 mm | 0 | 0 |
| 1123 K (850 degC), 1 h | ~0.002 mm | 0.002 mm | 0.005 mm |
| 1200 K (927 degC), 1 h | larger | larger | larger |

The class returns zero below 800 K and raises a `ProcessInfeasibleError` if the removal would consume the whole wall, because forming under inert cover or starting from thicker stock are the answers rather than accepting it.

---

## Standards

| Standard | Scope |
|---|---|
| **SAE AMS 2681** | Chemical milling of titanium alloys |
| AMS 2801 | Heat treatment of titanium alloy parts |
| AMS 4911 / 4928 | Ti-6Al-4V sheet and bar, which limit interstitials |
| ASTM E1409 | Oxygen and nitrogen by inert gas fusion |
| ASTM E384 | Microindentation hardness |
| AWS D17.1 | Fusion welding for aerospace, including discolouration criteria |

---

## Tool interface

```python
from SurfaceTreatment import SurfaceTreatment, ALPHA_CASE_SAFETY

treatment = SurfaceTreatment()
treatment.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed',
                     'alloyFamily': 'titanium', 'wallThickness': 0.006})

result = treatment.calculateAlphaCase(exposureTemperature = 1200.0, exposureTime = 3600.0)
print(result['caseDepth'], result['removalDepth'], result['removalBothSurfaces'])
```

---

## References

1. SAE AMS 2681, *Chemical Milling of Titanium Alloys*.
2. Gaddam, R. et al., "Study of Alpha-Case Depth in Ti-6Al-2Sn-4Zr-2Mo and Ti-6Al-4V", *IOP Conference Series*, Vol. 48, 2013.
3. Boyer, R., Welsch, G. and Collings, E. W. (eds.), *Materials Properties Handbook: Titanium Alloys*, ASM, 1994.
