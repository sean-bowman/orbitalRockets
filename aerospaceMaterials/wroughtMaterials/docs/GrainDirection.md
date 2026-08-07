[Home](../README.md) > Grain Direction

# Grain Direction

## Contents

- [Overview](#overview)
- [The three directions](#the-three-directions)
- [Why short transverse is worst](#why-short-transverse-is-worst)
- [The stress corrosion consequence](#the-stress-corrosion-consequence)
- [How parts end up loaded in ST](#how-parts-end-up-loaded-in-st)
- [Controls](#controls)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Wrought material is anisotropic and the anisotropy is severe in exactly the property that causes structural failures. The short transverse direction has a fraction of the longitudinal stress corrosion threshold, and the direction is not marked on the part.

This is the single most important thing in this sub-domain.

---

## The three directions

| Direction | Symbol | Definition |
|---|---|---|
| **Longitudinal** | **L** | Along the principal working direction, the rolling or extrusion axis |
| **Long transverse** | **LT** | Across the working direction, in the plane of the plate |
| **Short transverse** | **ST** | **Through the thickness** |

**Working elongates the grains along L and flattens them in ST**, and it aligns the inclusion stringers, the second phase particles and the grain boundaries in the same way.

**A plate has a pancake grain structure**: grains long in L, moderate in LT and thin in ST. Loading in ST loads across the flattened grain boundaries and across the aligned inclusions.

---

## Why short transverse is worst

**Because ST loads the material across every planar feature that working aligned.**

| Feature | Orientation after working | ST loading |
|---|---|---|
| **Grain boundaries** | Flattened into the plate plane | Loaded normal to them |
| **Inclusion stringers** | Aligned in L | Loaded across them |
| Second phase particles | Strung out in the plate plane | Loaded across |
| Porosity from the ingot | Flattened | Loaded to open it |

**Each of those features is a crack path**, and ST is the direction in which they are all normal to the load.

| Property | ST relative to L |
|---|---|
| Yield strength | 0.90 to 0.95 |
| Ultimate strength | 0.95 |
| **Elongation** | **0.4 to 0.6** |
| **Fracture toughness** | **0.6 to 0.8** |
| **SCC threshold** | **0.1 to 0.3** |

**The strength penalty is small and the toughness and SCC penalties are large**, which is precisely the trap. A designer checking strength sees a 5 to 10 percent difference and concludes the anisotropy is minor.

---

## The stress corrosion consequence

**Stress corrosion cracking in high strength aluminium is overwhelmingly a short transverse phenomenon**, and the tempers that exist to resist it exist for that reason alone.

| Alloy and temper | ST SCC threshold | Notes |
|---|---|---|
| **7075-T6** | **Very low** | Sustained ST tension is prohibited |
| **7075-T73** | High | Overaged. **This is why T73 exists** |
| 7050-T7451 | High | Overaged and stress relieved |
| 2024-T3 | Low in ST | |
| 2219-T87 | Good | One of its main attractions |

**The T73 temper costs about 15 percent of the T6 strength and buys a large multiple of the ST SCC threshold.** That trade is nearly always correct for a part with any sustained ST tension, and 7075-T6 in a sustained-load ST application is a known failure mode with a long service history behind it.

**The mechanism is anodic dissolution along the aligned grain boundaries**, which is why the effect is so directional: in ST the boundary path runs straight across the section.

---

## How parts end up loaded in ST

**Usually by accident, and that is what makes it dangerous.**

| Route | How |
|---|---|
| **Machined from thick plate** | The part's load axis happens to be the plate thickness direction |
| **Machined from a forging** | Same, and the flow direction is not on the drawing |
| **A lug or clevis** | The pin load can be through-thickness |
| Fastener clamp-up | A bolt clamps in ST through the plate |
| **Fitting machined from bar** | The radial direction of bar is ST |

**A bolt clamping a thick plate loads it in ST** through the joint, in sustained tension, which is exactly the SCC loading condition. That is a very common configuration and it is why fastener preload in thick 7075 is a known concern.

**The drawing usually does not show the orientation** because the drawing shows the part, not the stock it came from. The information exists in the process planning and it does not reach the stress analysis.

---

## Controls

| Control | Detail |
|---|---|
| **Specify the orientation on the drawing** | Relative to the part axes. The primary fix |
| **Use ST allowables where the load is ST** | And know that they exist |
| **Specify an SCC resistant temper** | T73, T7451, T851 |
| Orient the part in the stock deliberately | It is a planning decision with structural consequences |
| Forge to shape | Grain flow follows the contour instead |
| Avoid sustained ST tension | The design rule |

**Specifying the orientation on the drawing is the fix** and it costs nothing. A note giving the required grain direction relative to the part, plus a stock orientation callout, moves the information from the shop to the drawing where the stress analyst can see it.

**Overaged tempers are the material answer** and they are cheap: a temper designation change on the purchase order.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| ST strength penalty | 5 to 10 %, and it is not the problem |
| **ST SCC threshold** | **10 to 30 % of L. This is the problem** |
| ST toughness | 60 to 80 % of L |
| ST elongation | 40 to 60 % of L |
| 7075-T73 exists for ST SCC | At a 15 % strength cost |
| Specify orientation on the drawing | The primary control |
| No sustained ST tension in T6 tempers | |

---

## Failure modes

**Orientation not specified.** The part is oriented for stock yield instead.

**Strength checked, toughness and SCC not.** The small penalty seen, the large one missed.

**7075-T6 under sustained ST tension.** A known failure mode.

**Bolt preload in thick plate treated as benign.** It is sustained ST tension.

**L allowables used for an ST-loaded lug.** Off by a factor in SCC and by 20 to 40 % in toughness.

**Forging grain flow assumed favourable.** It follows the die, not the part's load path, unless specified.

---

## Standards

| Standard | Scope |
|---|---|
| **MMPDS** | Allowables by orientation |
| **ASTM G47** | SCC of 2XXX and 7XXX aluminium products, ST direction |
| ASTM G44 | Alternate immersion SCC testing |
| ASTM G64 | Classification of the SCC resistance of aluminium alloys |
| ASTM E399 / E1820 | Fracture toughness, with orientation designation |
| ASTM E1823 | Fatigue and fracture terminology, including L-T and S-L notation |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterialsLibrary')

from MaterialDatabase import queryMaterial

for orientation in ('L', 'LT', 'ST'):
    record = queryMaterial('7075-T73', 't73', orientation = orientation, basis = 'A')
    print(f'{orientation:3s} yield {record["yieldStrength"]/1e6:6.0f} MPa  '
          f'elongation {record["elongation"]*100:4.1f} %')
```

---

## References

1. MMPDS-2023, *Metallic Materials Properties Development and Standardization*.
2. Speidel, M. O., "Stress Corrosion Cracking of Aluminum Alloys", *Metallurgical Transactions A*, Vol. 6, 1975.
3. ASTM G64, *Classification of the Resistance to Stress-Corrosion Cracking of Heat-Treatable Aluminum Alloys*.
