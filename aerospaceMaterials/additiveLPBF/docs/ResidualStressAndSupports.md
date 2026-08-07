[Home](../README.md) > Residual Stress and Supports

# Residual Stress and Supports

## Contents

- [Overview](#overview)
- [Where the stress comes from](#where-the-stress-comes-from)
- [What it does](#what-it-does)
- [Reducing it during the build](#reducing-it-during-the-build)
- [Supports](#supports)
- [Support removal](#support-removal)
- [Stress relief](#stress-relief)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Every layer is deposited hot onto a cold substrate, contracts as it cools, and is restrained from contracting by everything beneath it. The result is tension in the new layer and compression below, accumulated over thousands of layers.

Residual stress in an as-built part routinely approaches the yield strength. It is not a second-order effect and it is the reason parts distort, crack, and fail during removal from the plate.

---

## Where the stress comes from

**The temperature gradient mechanism.** The laser heats a small region that wants to expand and cannot, because it is surrounded by cold material. It yields in compression. On cooling it contracts from a plastically compressed state and ends up in tension.

**The cool-down mechanism.** Each solidified layer contracts as it cools and is restrained by the layer below.

**Both act every layer**, and the accumulation is what produces part-scale distortion.

| Driver | Effect |
|---|---|
| **Long scan vectors** | Heat a long line that contracts along its length, pulling on everything either side |
| **High thermal gradient** | More plastic strain per layer |
| **Tall thin geometry** | Less lateral stiffness to resist it |
| **High modulus, high expansion** | More stress for the same strain |

---

## What it does

| Consequence | When it shows up |
|---|---|
| **Curling of overhangs** | During the build. The edge lifts and the recoater hits it |
| **Recoater crash** | The build stops, and the powder above the crash is contaminated |
| **Cracking** | During the build, in constrained geometry |
| **Distortion on cutting from the plate** | The moment the constraint is removed |
| **Distortion during machining** | The same mechanism as a quenched plate, and the same fix |

**Cutting from the plate is where it becomes visible.** The plate has been holding the part flat. Cut it free and the accumulated stress redistributes and the part moves, and it moves in one direction rather than randomly.

**A part that bananas on removal was not damaged by the removal.** It was already stressed and the removal simply revealed it. See [aerospaceMaterials HeatTreatment](../../docs/HeatTreatment.md) for the same mechanism in a quenched plate.

---

## Reducing it during the build

| Measure | Effect |
|---|---|
| **Island or chequerboard scanning** | Limits vector length, which is the primary driver |
| **Layer rotation** | Stops stress accumulating in one direction |
| **Build plate preheat** | Reduces the thermal gradient. 200 degC is typical, 500 for crack-prone alloys |
| **Orientation** | Minimise the cross-sectional area change between layers |
| **Reduced layer thickness** | Less energy per layer, less gradient |

**Preheat is the most effective single measure** and it is limited by what the machine offers. It is also what makes some crack-prone alloys printable at all.

**Orientation matters more than people expect.** A part whose cross section changes abruptly from layer to layer builds stress at the transition. Orienting to make the section change gradually is free.

---

## Supports

Supports do three jobs and the third is the one people forget.

| Job | Why |
|---|---|
| **Support overhangs** | Below 45 degrees the melt pool sits on loose powder and sinks |
| **Anchor to the plate** | Hold the part against the stress it is building |
| **Conduct heat away** | Powder is a poor conductor. An unsupported feature runs hot and its microstructure differs |

**The third job is why supports appear on features that would be geometrically self-supporting.** A thin unsupported spike does not sag; it overheats, because there is nowhere for the heat to go.

| Type | Use |
|---|---|
| Block or lattice | The default. Easy to remove, reasonable heat conduction |
| Tooth or perforated | Weakened at the interface for easier removal, at the cost of conduction |
| Solid | Where heat conduction matters most. Hard to remove |
| Contact point | Minimal witness marks, minimal conduction |

---

## Support removal

**This is the part that costs money**, and it is often the largest labour item in an additive part.

| Method | Notes |
|---|---|
| Hand tools | The default. Slow, and the finish is variable |
| Machining | Clean, and it needs access and a datum |
| Wire EDM | For the plate interface |
| Chemical | Where a sacrificial support material exists, which is rare in metal |

**Supports inside a closed passage cannot be removed.** Not slowly, not expensively: not at all. A design that requires them has an internal feature that will contain support structure for the life of the part.

**This is the single most important design rule in the sub-domain**, and it is why self-supporting internal geometry is worth a great deal of design effort. See [DesignForLpbf.md](DesignForLpbf.md).

---

## Stress relief

**On the plate, before cutting off. Always.**

The plate is the only thing holding the part in shape. Relieving the stress before removing that constraint is the whole point, and doing it afterwards relieves the stress in a part that has already distorted.

| Alloy | Typical cycle |
|---|---|
| 316L | 470 degC, 1 h |
| Inconel 718 | 1065 degC solution, then age |
| **Ti-6Al-4V** | **700 to 800 degC, 1 to 2 h, vacuum or argon** |
| AlSi10Mg | 300 degC, 2 h |

**Titanium stress relief is not optional.** As-built titanium carries very high residual stress and it will distort severely on removal without it.

**AlSi10Mg stress relief costs 20 percent of the yield strength**, because it coarsens the fine silicon network that produced the strength. That is an unusual trade: the treatment that makes the part stable makes it weaker.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Stress relieve on the plate | Before cutting off, always |
| Island scanning | Limits vector length |
| Layer rotation | 67 degrees |
| Preheat | 200 degC typical, 500 for crack-prone alloys |
| Self-supporting overhang | 45 degrees from horizontal |
| Supports inside a closed passage | Cannot be removed. Design them out |
| Supports conduct heat | Not only mechanical support |
| Titanium stress relief | Mandatory |

---

## Failure modes

**Part bananas on removal from the plate.** No stress relief, or done after removal.

**Recoater crash.** A curled overhang caught the blade.

**Cracking during the build.** Constrained geometry and high stress.

**Support structure permanently inside a passage.** Not removable at any cost.

**A feature that overheats despite being self-supporting.** Heat conduction was not considered.

**Distortion during machining.** The same mechanism as a quenched plate.

---

## Standards

| Standard | Scope |
|---|---|
| NASA-STD-6030 | Additive manufacturing requirements |
| MSFC-STD-3716 | LPBF spaceflight hardware |
| ASTM F3301 | Post-processing methods for metal additive parts |
| AMS 2801 | Heat treatment of titanium alloy parts |
| ASTM E837 | Residual stress by hole drilling |

---

## References

1. Mercelis, P. and Kruth, J.-P., "Residual Stresses in Selective Laser Sintering and Selective Laser Melting", *Rapid Prototyping Journal*, Vol. 12, 2006.
2. Kruth, J.-P. et al., "Assessing and Comparing Influencing Factors of Residual Stresses in SLM", *Proceedings of the IMechE Part B*, Vol. 226, 2012.
3. Denlinger, E. R. et al., "Effect of Inter-Layer Dwell Time on Distortion and Residual Stress", *Journal of Materials Processing Technology*, Vol. 215, 2015.
