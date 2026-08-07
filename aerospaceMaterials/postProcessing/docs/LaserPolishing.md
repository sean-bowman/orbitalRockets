[Home](../README.md) > Laser Polishing

# Laser Polishing

## Contents

- [Overview](#overview)
- [The mechanism](#the-mechanism)
- [What it achieves](#what-it-achieves)
- [What it costs](#what-it-costs)
- [Where it fits](#where-it-fits)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Laser polishing melts a very thin surface layer and lets surface tension smooth it before it refreezes. No material is removed and no abrasive is involved, which makes it a genuinely different proposition from every other finishing process here.

It is a developing technology rather than a mature one, and it is included because it is well suited to additive surfaces.

---

## The mechanism

A defocused or scanned laser melts a layer typically 20 to 100 um deep. **Surface tension pulls the liquid from peaks into valleys**, and the surface refreezes smoother than it was.

| Regime | Depth | Effect |
|---|---|---|
| **Surface shallow melting** | 20 to 50 um | Removes micro-roughness. The usual mode |
| **Surface over melting** | 50 to 200 um | Removes larger features, at the cost of a thicker resolidified layer |

**No material is removed.** The volume is conserved, so peaks fill valleys and the mean surface stays where it was. That means the dimension does not change, which is a real advantage over every abrasive or chemical route.

**The wavelength limit follows from the mechanism.** Surface tension flattens features whose wavelength is short relative to the melt pool. Long wavelength waviness is not affected, because the whole waviness is inside a single melt pool and it moves with it.

---

## What it achieves

| Property | Effect |
|---|---|
| **Ra** | 10 um to 1 um typically, and better on a good starting surface |
| **Dimensional change** | Essentially none |
| Waviness | Not improved |
| **Resolidified layer** | 20 to 100 um of remelted material |
| Residual stress | Tensile, from the melt contraction |

**The resolidified layer is the catch.** It has a different microstructure from the bulk, it has solidification texture, and it carries tensile residual stress. On a fatigue critical surface that is a real debit and it can outweigh the roughness improvement.

**The tensile residual stress is the reason peening sometimes follows** laser polishing on a fatigue critical part.

---

## What it costs

| Cost | Detail |
|---|---|
| **Line of sight** | Required. No internal passages |
| **Cycle time** | Scanned, so it scales with area |
| Equipment | A laser system with scanning optics |
| Process development | Parameters are material and starting-surface specific |
| Atmosphere | Inert cover needed on reactive alloys |

**Line of sight is the limit that matters** and it is the same limit as machining. An internal passage cannot be laser polished, so it does not compete with abrasive flow machining; it competes with vibratory finishing and machining on external surfaces.

---

## Where it fits

| Application | Why |
|---|---|
| **Additive external surfaces** | The starting roughness is high and there is a lot to gain |
| **Complex external geometry** | It follows a scanned path, so shape does not matter as it does for machining |
| Where no dimensional change is allowed | It removes nothing |
| Tooling and dies | Established use |
| Medical implants | Established use |

**It is genuinely useful where the geometry defeats machining** and dimensional change is unacceptable. That is a narrow niche and additive parts fall in it more often than conventionally made ones.

**It is not yet a routine aerospace process.** The resolidified layer has to be qualified like any other surface condition, and the process specification is not standardised.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Melt depth | 20 to 100 um |
| Ra | 10 um to 1 um typical |
| Dimensional change | None. Volume is conserved |
| Waviness | Not improved |
| Resolidified layer | Different microstructure, tensile stress |
| Line of sight required | No internal passages |
| Consider peening afterwards | To counter the tensile stress |
| Inert cover on reactive alloys | Titanium in particular |

---

## Failure modes

**Resolidified layer not accounted for.** A different microstructure at the fatigue critical surface.

**Tensile residual stress ignored.** A fatigue debit that offsets the roughness gain.

**Expected to fix waviness.** It does not.

**Applied to a reactive alloy in air.** Oxygen pickup and a cased surface.

**Expected to reach an internal passage.** It needs line of sight.

**Over-melting on a thin section.** Distortion.

---

## Standards

| Standard | Scope |
|---|---|
| ISO 4287 / 21920 | Surface texture |
| ASME B46.1 | Surface texture |
| ASTM F3301 | Post-processing methods for metal additive parts |
| ISO/ASTM 52900 | Additive manufacturing terminology |

**There is no dedicated laser polishing standard**, which is a fair summary of the technology's maturity. A specification has to state the parameters and the acceptance directly.

---

## References

1. Temmler, A., Willenborg, E. and Wissenbach, K., "Laser Polishing", *Proceedings of SPIE*, Vol. 8243, 2012.
2. Bhaduri, D. et al., "Laser Polishing of 3D Printed Mesoscale Components", *Applied Surface Science*, Vol. 405, 2017.
3. Gora, W. S. et al., "Enhancing Surface Finish of Additively Manufactured Titanium and Cobalt Chrome Elements Using Laser Based Finishing", *Physics Procedia*, Vol. 83, 2016.
