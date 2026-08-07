[Home](../README.md) > Laser Shock Peening

# Laser Shock Peening

## Contents

- [Overview](#overview)
- [The mechanism](#the-mechanism)
- [What it buys](#what-it-buys)
- [What it costs](#what-it-costs)
- [Where it is worth it](#where-it-is-worth-it)
- [Process parameters](#process-parameters)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Laser shock peening produces the same compressive layer as shot peening, four to five times deeper, with almost no surface roughening. It costs a great deal more and it is worth it in a small number of specific places.

---

## The mechanism

A short, intense laser pulse vaporises a sacrificial ablative layer on the surface. The vapour is confined by a water layer above it, so instead of expanding freely it generates a pressure pulse of several gigapascals lasting tens of nanoseconds.

**That pressure pulse is a shock wave** and it propagates into the material, plastically deforming it far below the surface.

| Element | Role |
|---|---|
| **Ablative layer** | Black tape or paint. Absorbs the pulse and protects the surface |
| **Confining medium** | A flowing water curtain. Confines the plasma and multiplies the pressure |
| **Laser pulse** | 10 to 30 ns, a few joules, focused to a few millimetres |

**No media touches the part.** The surface is not impacted mechanically, so the roughening that shot peening causes does not occur.

---

## What it buys

| Property | Shot peening | Laser shock |
|---|---|---|
| **Layer depth** | 0.05 to 0.5 mm | **0.5 to 2.0 mm** |
| Surface stress | ~0.5 yield | ~0.5 yield |
| **Surface roughening** | Real | **Almost none** |
| Coverage control | Statistical | Deterministic, spot by spot |
| Thin section distortion | Significant | Lower, because less energy per unit area |

**Depth is the point.** A crack that has to grow through 1.5 mm of compression rather than 0.15 mm has a very different life, and for a deep surface flaw the shot peened layer is simply not deep enough to help.

**The absence of roughening matters on a fatigue critical surface**, where shot peening's own dimples become initiation sites and partly cancel the benefit.

---

## What it costs

| Cost | Detail |
|---|---|
| **Equipment** | A high energy pulsed laser system |
| **Cycle time** | Spot by spot, with overlap. Slow on a large area |
| **Consumables** | Ablative layer applied and removed for every pass |
| **Setup** | Water curtain, fixturing, and line of sight to every treated area |
| Line of sight | Required. It cannot treat an internal surface |

**It is a specialist service**, not a shop process. That constrains the supply chain and it puts the operation somewhere in a schedule rather than in a shop travelling with the part.

---

## Where it is worth it

| Application | Why |
|---|---|
| **Turbine blade leading edges** | Foreign object damage tolerance. The original driver |
| **Fastener holes in thick section** | The compressive layer reaches past the fatigue critical depth |
| Weld toes | Deep enough to counter the weld residual tension through the section |
| Fracture critical features | Where the crack growth life needs a real extension |
| Repair | Extending the life of an existing part without removing material |

**It is a targeted process.** Treating a whole part is rarely economic; treating the one feature that governs the fatigue life usually is.

---

## Process parameters

| Parameter | Typical |
|---|---|
| Pulse energy | 3 to 30 J |
| Pulse duration | 10 to 30 ns |
| Spot size | 2 to 6 mm |
| Power density | 5 to 10 GW/cm^2 |
| Overlap | 50 to 70 percent |
| Passes | 1 to 3 |

**Power density is the control** and there is a threshold. Below about 1 GW/cm^2 the plasma does not generate enough pressure to yield the material. Above about 10 the plasma becomes opaque and absorbs the rest of the pulse, so more energy does nothing.

**Multiple passes deepen the layer**, and the second pass adds less than the first because the material has already work hardened.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Layer depth | 0.5 to 2.0 mm, 4 to 5x shot peening |
| Surface roughening | Almost none |
| Power density | 5 to 10 GW/cm^2 |
| Overlap | 50 to 70 % |
| Line of sight required | No internal surfaces |
| A targeted process | Treat the governing feature, not the part |
| Ablative layer | Applied and removed every pass |

---

## Failure modes

**Applied without an ablative layer.** The surface is ablated and damaged.

**Power density below threshold.** No plasma pressure, no compression.

**Power density too high.** The plasma goes opaque and absorbs the pulse.

**Water curtain interrupted.** No confinement, and the pressure falls by an order of magnitude.

**Applied to a thin section.** It can bow, though less than shot peening.

**Expected to treat an internal surface.** It needs line of sight.

---

## Standards

| Standard | Scope |
|---|---|
| **SAE AMS 2546** | Laser peening |
| SAE AMS 2580 | Laser peening of metallic parts, process |
| ASTM E837 | Residual stress by hole drilling, for verification |
| ASTM E2860 | Residual stress by X-ray diffraction |

---

## Tool interface

```python
from SurfaceTreatment import SurfaceTreatment, PEENING_MEDIA

for media in ('ceramic bead', 'laser shock'):
    treatment = SurfaceTreatment()
    treatment.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed',
                         'alloyFamily': 'titanium', 'peeningMedia': media,
                         'wallThickness': 0.010})
    result = treatment.calculatePeening()
    print(f'{media:14s} layer {result["compressiveLayerDepth"]*1000:.3f} mm, '
          f'roughening factor {result["roughnessFactor"]:.2f}, '
          f'fatigue x{result["fatigueImprovementFactor"]:.3f}')
```

---

## References

1. SAE AMS 2546, *Laser Peening*.
2. Montross, C. S. et al., "Laser Shock Processing and its Effects on Microstructure and Properties of Metal Alloys: A Review", *International Journal of Fatigue*, Vol. 24, 2002.
3. Ding, K. and Ye, L., *Laser Shock Peening: Performance and Process Simulation*, Woodhead, 2006.
