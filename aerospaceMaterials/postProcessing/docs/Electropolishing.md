[Home](../README.md) > Electropolishing

# Electropolishing

## Contents

- [Overview](#overview)
- [The mechanism](#the-mechanism)
- [What it achieves](#what-it-achieves)
- [What it removes that you wanted](#what-it-removes-that-you-wanted)
- [Process control](#process-control)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Electropolishing is anodic dissolution under conditions that remove peaks preferentially. It is the only chemical process in this sub-domain that improves surface finish, and it is the one most likely to undo something else that was done deliberately.

---

## The mechanism

The part is the anode in an electrolyte. Metal dissolves, and a viscous boundary layer forms at the surface.

**That boundary layer is thinner over a peak than in a valley**, because a peak projects into the flowing electrolyte. Thinner layer means lower resistance means higher local current density means faster dissolution.

**Peaks dissolve faster than valleys**, so the profile smooths.

| Feature | Result |
|---|---|
| Micro-roughness | Removed preferentially. This is the benefit |
| Macro-waviness | Not removed. The scale is too large for the boundary layer effect |
| Sharp edges | Rounded, and rapidly, because they are extreme peaks |
| Deep scratches | Not removed. They deepen with the surrounding surface |

**The scale limit is the point people miss.** Electropolishing improves Ra and it does not improve waviness, flatness or form. A wavy surface comes out shiny and wavy.

---

## What it achieves

| Property | Effect |
|---|---|
| **Ra** | Improves by roughly 3x, to a floor near 0.4 um |
| **Cleanability** | Substantially better. No crevices to hold contamination |
| **Passivity** | On stainless, it enriches chromium at the surface |
| Deburring | Effective on small burrs |
| Appearance | Bright, and it is often the actual reason |

**The passivity benefit is real and it is separate from the finish.** Anodic dissolution removes iron preferentially from a stainless surface, leaving it chromium enriched. An electropolished stainless surface is more corrosion resistant than a mechanically polished one at the same Ra.

**Cleanability is why it is specified for fluid systems and vacuum hardware.** A surface with no crevices has nowhere for contamination to hide and nothing to outgas from.

---

## What it removes that you wanted

**This is the section that matters.**

| Removed | Consequence |
|---|---|
| **A peening compressive layer** | The fatigue benefit is gone. Peen last |
| **Sharp edges** | An orifice entry that was sized sharp is now rounded |
| **Stock, from both surfaces** | A wall loses twice the removal depth |
| Dimensional accuracy | Anything held to a tight tolerance moves |
| A thin coating | It is anodic dissolution; it removes whatever is on the surface |

**Electropolishing after shot peening is the commonest sequencing error in this sub-domain.** Both operations are beneficial, both are routinely specified, and in that order the second removes the layer the first created. **Peen last.**

---

## Process control

| Parameter | Effect |
|---|---|
| **Current density** | Sets the rate. Too low etches rather than polishes |
| Electrolyte composition | Alloy specific. Phosphoric and sulphuric for stainless |
| Temperature | Rate and boundary layer viscosity |
| Time | Total removal |
| Agitation | Changes the boundary layer, and too much destroys the effect |

**There is a polishing window in current density**, and it matters:

| Current density | Result |
|---|---|
| Too low | Etching. The surface roughens rather than smooths |
| **The plateau** | **Polishing** |
| Too high | Gas evolution, pitting and streaking |

**Below the plateau the process actively makes the surface worse**, which surprises people who assume less current means a gentler process. Grain boundaries and inclusions etch preferentially and the Ra rises.

**Cathode geometry matters** because it shapes the current distribution. A complex part needs a shaped or segmented cathode, and an internal passage needs an electrode inside it.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Ra improvement | ~3x, floor near 0.4 um |
| Improves roughness, not waviness | The boundary layer scale sets it |
| Removes from both surfaces | Wall loses 2x |
| **Peen after, never before** | It removes the compressive layer |
| Current density plateau | Below it, the surface etches |
| Enriches chromium on stainless | A real passivity benefit |
| Rounds sharp edges rapidly | Check any metering feature |
| Internal passages need an internal electrode | Line of sight in current, not light |

---

## Failure modes

**Electropolished after peening.** The layer is gone and nothing shows it.

**Current density below the plateau.** The surface etches and roughens.

**A sharp orifice entry rounded.** The discharge coefficient changed.

**Expected to fix waviness.** It does not.

**Wall thinned by twice the intended amount.** Both surfaces.

**No internal electrode on a passage.** Only the outside polished.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM B912** | Passivation of stainless by electropolishing |
| ASTM E1558 | Electrolytic polishing of metallographic specimens |
| AMS 2700 | Passivation of corrosion resistant steels |
| SEMI F19 | Electropolished stainless for semiconductor fluid systems |
| ISO 4287 / 21920 | Surface texture |

---

## Tool interface

```python
from SurfaceTreatment import SurfaceTreatment

treatment = SurfaceTreatment()
treatment.setInputs({'material': '316L', 'condition': 'annealed',
                     'alloyFamily': 'stainless', 'wallThickness': 0.004,
                     'initialRoughness': 3.2e-6})

polish = treatment.calculateStockRemoval('electropolish', processTime = 300.0)
print(polish['initialRoughness'], polish['finalRoughness'])   # improves
mill = treatment.calculateStockRemoval('chemical mill', 60.0, 25.0e-6)
print(mill['initialRoughness'], mill['finalRoughness'])       # unchanged
```

---

## References

1. ASTM B912-02, *Standard Specification for Passivation of Stainless Steels Using Electropolishing*.
2. Landolt, D., "Fundamental Aspects of Electropolishing", *Electrochimica Acta*, Vol. 32, 1987.
3. Davis, J. R. (ed.), *Surface Engineering for Corrosion and Wear Resistance*, ASM, 2001.
