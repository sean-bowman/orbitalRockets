[Home](../README.md) > Process Fundamentals

# Process Fundamentals

## Contents

- [Overview](#overview)
- [The melt pool](#the-melt-pool)
- [Conduction mode and keyhole mode](#conduction-mode-and-keyhole-mode)
- [The layer overlap criterion](#the-layer-overlap-criterion)
- [Solidification rate](#solidification-rate)
- [Scan strategy](#scan-strategy)
- [The four parameters](#the-four-parameters)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Everything the process does happens in a melt pool a few hundred micrometres across that exists for a few hundred microseconds. Understanding that pool is understanding the process, because every defect, every property and every limitation traces back to its size, its shape and how fast it froze.

---

## The melt pool

A laser moving over a powder bed leaves a moving pool of molten metal behind it. The powder melts, the material beneath re-melts, the pool solidifies as the laser moves away, and the next track overlaps it.

**The pool has to do two things at once and they are different requirements:**

**Melt the powder in this layer.** Obvious, and it is the easy one.

**Re-melt the material below.** This is what actually joins the layers, and it is the requirement people miss. A pool that melts the powder and stops at the previous layer's surface produces a part that is fully dense by area and has no metallurgical bond between layers.

**Pool dimensions, for a production Inconel 718 parameter set:**

| Quantity | Value |
|---|---|
| Depth | 91 um |
| Width | 158 um |
| Layer thickness | 40 um |
| Beam diameter | 80 um |
| **Depth in layers** | **2.28** |

**The pool is wider than the beam** because heat conducts laterally while the pool is liquid. That is why a 110 um hatch spacing on an 80 um beam still overlaps: the pools overlap even though the beam paths do not.

---

## Conduction mode and keyhole mode

Two distinct regimes with different pool shapes and different defects.

**Conduction mode.** The laser heats the surface and heat conducts inward. The pool is shallow and wide, roughly semicircular in section, with a depth to width ratio below about 0.5. Absorption is a surface phenomenon at the material's flat-surface absorptivity.

**Keyhole mode.** The intensity is high enough to vaporise metal, and the vapour pressure pushes a narrow depression into the pool. The laser then enters that depression and reflects off its walls multiple times, so the effective absorptivity rises sharply. The pool becomes deep and narrow.

| | Conduction | Keyhole |
|---|---|---|
| Depth to width | < 0.5 | > 1.0 |
| Absorption | Surface, at the flat value | Multiple reflection, much higher |
| Stability | Stable | The cavity oscillates and collapses |
| Defect | None, if deep enough | Round gas pores from collapse |

**Keyholing is not simply a failure mode.** Deliberate shallow keyholing is how deep penetration is achieved at reasonable speed, and many production parameter sets sit just inside it. What is not acceptable is unstable keyholing, where the cavity collapses periodically and traps vapour.

---

## The layer overlap criterion

**The single most important process check there is:**

```
meltPoolDepth > layerThickness
```

If the pool does not penetrate into already-solidified material, the layers are not metallurgically joined and the result is lack of fusion porosity: flat, aligned with the build layers, and behaving like a pre-existing crack.

**A depth of 1.5 to 2.5 layers is the usual target.** Less than 1.5 leaves no margin for layer thickness variation, powder packing variation and the reduced absorption on a re-melted surface. More than about 3 wastes energy and increases the residual stress.

**Hatch overlap is the same criterion applied sideways.** Adjacent tracks have to overlap or the gaps between them do not re-melt:

```
overlap = (meltPoolWidth - hatchSpacing) / meltPoolWidth
```

**Twenty percent is the practical minimum.** Below it the valleys between tracks retain unmelted powder and the porosity appears between scan vectors rather than between layers.

---

## Solidification rate

**1e5 to 1e7 K/s.** For comparison a sand casting cools at perhaps 1 K/s and a die casting at 1e3.

That rate produces a microstructure no conventional process makes:

| Feature | Consequence |
|---|---|
| **Cellular or fine dendritic** | Sub-micron spacing rather than tens of microns |
| **Extended solid solubility** | Elements stay in solution that would precipitate on slow cooling |
| **Fine, textured grains** | Grains grow along the thermal gradient, so they are columnar and aligned with the build |
| **No macrosegregation** | The pool is too small and freezes too fast for it to develop |

**This is why as-built additive material is often stronger than the wrought equivalent** and why it is usually less ductile: the fine structure that strengthens it also gives it less room to deform.

**It is also why AlSi10Mg loses 20 percent of its yield strength on stress relief.** The strength comes from a fine cellular silicon network produced by the rapid solidification, and any thermal treatment coarsens it.

---

## Scan strategy

How the laser covers each layer, and it matters more than it looks.

| Strategy | Purpose |
|---|---|
| **Stripe** | Layer divided into narrow strips, each scanned in turn. Limits the length of any single vector and therefore the thermal gradient along it |
| **Chequerboard / island** | Layer divided into small squares scanned in random order. Distributes heat and reduces residual stress |
| **Rotation between layers** | Typically 67 degrees. Prevents defects and texture stacking up in the same place layer after layer |
| **Contour** | A separate perimeter pass with different parameters, because the surface needs a different energy input from the bulk |
| **Up-skin and down-skin** | Separate parameter sets for the top and bottom surfaces |

**The 67 degree rotation is worth understanding.** Rotating by 90 degrees would return to the same orientation every second layer, letting scan-vector-aligned defects stack. An irrational-ish angle like 67 degrees never repeats within any reasonable build height.

**Vector length drives residual stress.** A long vector heats a long line, which contracts along its length and pulls on everything either side. Breaking the layer into islands limits that length, which is the whole reason island strategies exist.

---

## The four parameters

| Parameter | Typical | What it does |
|---|---|---|
| **Laser power** | 200 to 400 W | Energy in |
| **Scan speed** | 0.5 to 2.0 m/s | Time to deposit it |
| **Hatch spacing** | 80 to 200 um | Track overlap |
| **Layer thickness** | 20 to 60 um | Layers per unit height |

They combine into the volumetric energy density, but that number is a poor discriminator on its own. See [TheProcessMap.md](TheProcessMap.md).

**Layer thickness has leverage on cost that the others do not.** It sets both the layer count, and therefore the recoat time, and the volume deposited per pass, and therefore the scan time. Halving it roughly doubles the build time.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Melt pool penetration | 1.5 to 2.5 layers |
| Hatch overlap | 20 % minimum |
| Pool depth to width, conduction | < 0.5 |
| Pool depth to width, keyhole | > 1.0 |
| Solidification rate | 1e5 to 1e7 K/s |
| Layer rotation | 67 degrees |
| Vector length | Limited by stripe or island width |

---

## Failure modes

**Pool does not reach the previous layer.** Lack of fusion, layer aligned, crack-like.

**Hatch overlap below 20 percent.** Porosity between scan vectors.

**Unstable keyholing.** Round gas pores from cavity collapse.

**Long scan vectors.** High residual stress along the vector direction.

**No layer rotation.** Defects and texture stack in the same place.

**Contour parameters used for the bulk.** The surface needs different energy from the interior.

---

## Standards

| Standard | Scope |
|---|---|
| ISO/ASTM 52900 | Terminology |
| ISO/ASTM 52904 | Process characteristics and performance for metal PBF |
| **MSFC-SPEC-3717** | Control and qualification of LPBF processes |
| NASA-STD-6030 | Additive manufacturing requirements |
| ISO/ASTM 52907 | Feedstock characterisation |

---

## Tool interface

```python
from LpbfProcess import LpbfProcess

process = LpbfProcess()
process.setInputs({'material': 'Inconel 718', 'laserPower': 285.0, 'scanSpeed': 0.960,
                   'hatchSpacing': 110.0e-6, 'layerThickness': 40.0e-6,
                   'beamDiameter': 80.0e-6})

pool = process.calculateMeltPool()
print(pool['depthToLayerRatio'])      # 2.28, inside the 1.5 to 2.5 target
print(pool['hatchOverlapFraction'])   # 0.30, above the 0.20 minimum
print(pool['aspectRatio'])            # depth over width, the keyhole indicator
```

---

## References

1. DebRoy, T. et al., "Additive Manufacturing of Metallic Components", *Progress in Materials Science*, Vol. 92, 2018.
2. King, W. E. et al., "Observation of Keyhole-Mode Laser Melting in Laser Powder-Bed Fusion", *Journal of Materials Processing Technology*, Vol. 214, 2014.
3. Eagar, T. W. and Tsai, N. S., "Temperature Fields Produced by Traveling Distributed Heat Sources", *Welding Journal*, Vol. 62, 1983.
4. Thijs, L. et al., "A Study of the Microstructural Evolution during Selective Laser Melting of Ti-6Al-4V", *Acta Materialia*, Vol. 58, 2010.
