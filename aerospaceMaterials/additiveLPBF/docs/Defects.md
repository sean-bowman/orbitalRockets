[Home](../README.md) > Defects

# Defects

## Contents

- [Overview](#overview)
- [The defect catalogue](#the-defect-catalogue)
- [Lack of fusion](#lack-of-fusion)
- [Keyhole porosity](#keyhole-porosity)
- [Entrapped gas porosity](#entrapped-gas-porosity)
- [Cracking](#cracking)
- [Why density is not enough](#why-density-is-not-enough)
- [Detection](#detection)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Every defect this process produces has a cause in the process map, the powder, or the geometry. Knowing which tells you what to change, and the change is different for each.

The important distinction is not how much porosity there is. It is what shape it is.

---

## The defect catalogue

| Defect | Appearance | Cause | Fixed by |
|---|---|---|---|
| **Lack of fusion** | Flat, irregular, layer aligned | Insufficient energy or overlap | More power, slower scan, tighter hatch |
| **Keyhole porosity** | Round, often large, at track ends | Excess intensity | Less power, faster scan |
| **Entrapped gas** | Small, spherical, uniformly distributed | Gas inside the powder particles | Better powder route |
| **Solidification cracking** | Interdendritic, in the last liquid | Wide freezing range, high stress | Alloy change or preheat |
| **Strain age cracking** | In the HAZ of a PH nickel alloy | Gamma prime forming under stress | Preheat, or a different alloy |
| **Balling** | Discontinuous, beaded tracks | Insufficient wetting | More energy, or fix the oxide |
| **Spatter inclusion** | Oxidised particle melted into the part | Poor gas flow | Fix the gas flow |
| **Delamination** | A separated layer, visible | Severe lack of fusion or stress | Both causes need addressing |

---

## Lack of fusion

**The worst defect this process produces.**

The melt pool did not penetrate into the previous layer, or adjacent tracks did not overlap. The result is a void with unmelted powder in it, flat, and aligned with the build layers.

**It behaves like a pre-existing crack**, because it is flat and it has a sharp edge. Its stress concentration is effectively that of a crack rather than the roughly 3 of a round pore, and its fatigue impact is correspondingly severe.

**It is aligned with the layers**, which means it is perpendicular to a Z-direction tensile stress. That is the worst possible orientation and it is a large part of why Z properties are lower than XY.

**HIP does not fully recover it.** Pressure closes the void geometrically, and the two surfaces are oxidised and frequently do not bond. The density measurement then reads 100 percent and the crack-like flaw is still there.

---

## Keyhole porosity

The vapour cavity in keyhole mode is unstable. It oscillates, and periodically the walls collapse and pinch off a bubble of metal vapour that freezes in as a pore.

**Round, often large, and concentrated at the ends of scan tracks** where the laser decelerates and the intensity per unit length rises.

**Less harmful than lack of fusion.** Round means a stress concentration of about 3, and round means HIP closes it properly with clean surfaces that bond.

**Given the choice, err towards keyhole.** See [TheProcessMap.md](TheProcessMap.md).

---

## Entrapped gas porosity

Gas atomised powder contains hollow particles with argon inside them. That argon ends up in the part.

**HIP does not remove it.** The pore closes under pressure and the gas inside is compressed, not eliminated. On any subsequent heat treatment at temperature and ambient pressure it re-expands, and porosity reappears in a part that was measured dense after HIP.

**The fix is upstream.** Plasma rotating electrode powder has essentially no entrapped gas because the process never involves a gas jet. It is coarser and far more expensive, and for a fatigue critical titanium part it is sometimes the right answer.

---

## Cracking

**Solidification cracking.** The last liquid to freeze sits in thin films between dendrites. The surrounding solid contracts, pulls those films apart, and there is not enough liquid left to feed the gap. A wide freezing range makes it worse, which is why 7075 and 2024 aluminium cannot be printed.

**Strain age cracking.** In precipitation hardened nickel alloys, gamma prime precipitates during cooling in a heat affected zone that is simultaneously under high residual stress. The alloy hardens and is strained at the same time. This is why high gamma prime superalloys are difficult and 718 is not: 718 strengthens with gamma double prime, which forms slowly enough to avoid the coincidence.

**Both are alloy problems more than parameter problems.** Preheat helps by reducing the thermal gradient, and it does not make an uncrackable alloy out of a crackable one.

---

## Why density is not enough

**Two parts at 99.8 percent density can have completely different fatigue lives**, depending on whether the missing 0.2 percent is round or flat.

| Method | What it tells you |
|---|---|
| **Archimedes density** | A single number. Nothing about shape, size or location |
| **Metallography** | Shape and size, on one plane, destructively |
| **Computed tomography** | Shape, size and location, in three dimensions, non-destructively |

**Archimedes is the fast screen and it cannot be the acceptance criterion for a fatigue critical part.** It cannot distinguish the defect that matters from the one that does not.

---

## Detection

| Defect | Best method |
|---|---|
| Lack of fusion | CT, or metallography |
| Keyhole porosity | CT, Archimedes as a screen |
| Entrapped gas | CT, and it is small so resolution matters |
| Cracking | CT, penetrant if surface breaking |
| Balling | Visual, and it is usually obvious |
| Spatter inclusion | CT, metallography |

**Radiography is not a substitute for CT here.** It integrates through the thickness, so a flat lack of fusion defect lying in the build plane is presented edge-on and is close to invisible. That is exactly the orientation this process produces.

See [Inspection.md](Inspection.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Density target | 99.9 % |
| Density alone | Not an acceptance criterion for fatigue critical parts |
| Lack of fusion | Crack-like, and HIP does not fully fix it |
| Keyhole porosity | Round, and HIP does fix it |
| Entrapped gas | HIP does not fix it, and heat treat re-opens it |
| Radiography | Blind to the defect this process produces |
| Cracking | An alloy problem, not a parameter problem |

---

## Failure modes

**Density measured, defect shape not identified.** The number that matters was not measured.

**HIP assumed to close everything.** Lack of fusion and entrapped gas both survive it.

**Porosity reappearing after heat treatment.** Entrapped argon re-expanding.

**A crack-prone alloy attempted without preheat.** Solidification or strain age cracking.

**Radiography accepted as volumetric NDE.** Blind to the flat defect.

**Balling dismissed as cosmetic.** It is severe lack of wetting and the layer beneath it is not sound.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM E1441** | Computed tomography imaging |
| ASTM E2767 | Digital imaging and communication in NDE for CT |
| ASTM B962 | Density by Archimedes |
| ASTM E3 | Metallographic specimen preparation |
| ASTM E1417 | Liquid penetrant testing |
| NASA-STD-6030 | Additive manufacturing requirements |
| **NASA-STD-5009** | NDE requirements for fracture critical components |

---

## References

1. Gordon, J. V. et al., "Defect Structure Process Maps for Laser Powder Bed Fusion", *Additive Manufacturing*, Vol. 36, 2020.
2. Tang, M., Pistorius, P. C. and Beuth, J. L., "Prediction of Lack-of-Fusion Porosity", *Additive Manufacturing*, Vol. 14, 2017.
3. Snow, Z., Nassar, A. R. and Reutzel, E. W., "Invited Review Article: Review of the Formation and Impact of Flaws in Powder Bed Fusion", *Additive Manufacturing*, Vol. 36, 2020.
4. du Plessis, A. et al., "Effects of Defects on Mechanical Properties in Metal Additive Manufacturing", *Materials and Design*, Vol. 187, 2020.
