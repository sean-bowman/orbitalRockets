[Home](../README.md) > Bonded and Composite Joints

# Bonded and Composite Joints

## Contents

- [Overview](#overview)
- [Why adhesive joints do not load uniformly](#why-adhesive-joints-do-not-load-uniformly)
- [Joint configurations](#joint-configurations)
- [Laminate failure criteria](#laminate-failure-criteria)
- [Damage tolerance in composites](#damage-tolerance-in-composites)
- [Surface preparation](#surface-preparation)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Bonded joints distribute load over an area rather than concentrating it at a hole, which is why they can outperform fastening in fatigue. They are also the joining method most sensitive to process control and the hardest to inspect.

The adhesive mechanics are covered in [aerospaceMaterials AdhesiveBonding](../../aerospaceMaterials/joiningProcesses/docs/AdhesiveBonding.md). This document is about the structural consequences.

---

## Why adhesive joints do not load uniformly

**The shear stress in the bondline peaks at the ends of the overlap and drops to nearly nothing in the middle.**

The Volkersen shear lag model gives it:

```
tau(x) = tau_avg (wL/2) cosh(w x) / sinh(w L/2)
w      = sqrt(G_a / (t_a E t))
```

**Beyond roughly 30 times the adhesive thickness, additional overlap contributes essentially nothing**, because the middle of a long joint carries no load. Doubling the overlap does not double the strength.

**That is the single most counterintuitive fact about bonded joints** and it is the reason a long lap joint is not a strong one.

**A more compliant adhesive spreads the load better**, which is why a toughened adhesive with a lower modulus can carry more than a stiff brittle one of higher nominal strength.

---

## Joint configurations

| Joint | Peel | Efficiency |
|---|---|---|
| **Single lap** | **High.** Eccentric load path | Poor |
| **Double lap** | Low. Balanced | Good |
| **Scarf** | **Very low.** Aligned load path | **Best** |
| Stepped lap | Low | Very good, and machinable |
| Butt | -- | Useless |

**The single lap joint is the worst configuration and the most common one.** The load path is eccentric, so the joint bends under load and peels the ends apart. Goland and Reissner extended the shear lag model to include that bending moment, and it is the peel stress rather than the shear that usually initiates failure.

**Scarf joints are the best and the hardest to make.** A shallow taper aligns the load path through the bond, eliminating both the eccentricity and the stress concentration. Composite repair uses scarf and stepped lap joints for exactly that reason.

**Never load a bonded joint in peel or cleavage.** Where geometry cannot avoid it, a fastener at the end of the overlap arrests the peel. That hybrid is common and it is not a failure of design.

---

## Laminate failure criteria

| Criterion | Character |
|---|---|
| **Maximum stress** | Simple, non-interactive, ply by ply |
| **Maximum strain** | Same, in strain space. Common in aerospace |
| **Tsai-Wu** | Interactive quadratic. Smooth, and it can be non-conservative |
| **Hashin** | Distinguishes fibre and matrix failure modes |
| **Puck** | Physically based, matrix failure planes |

**Maximum strain is the common aerospace choice** because it is conservative, simple to apply, and the allowables are directly measurable.

**First ply failure is not laminate failure.** A laminate can lose its transverse plies to matrix cracking and continue carrying load in the fibres. Whether that counts as failure is a requirements decision, and for a pressure boundary it usually does because matrix cracks leak.

**Composite allowables are statistical in a way metals are not.** The scatter is larger, so the B-basis and A-basis knockdowns are correspondingly larger, and the environmental knockdowns for hot-wet conditions are substantial.

---

## Damage tolerance in composites

**The governing consideration for composite primary structure, and it is different from metals.**

| Metal | Composite |
|---|---|
| Cracks grow predictably | **Damage is discrete and does not grow predictably** |
| Detectable by inspection | **Barely visible impact damage** |
| Fracture mechanics applies | **Damage tolerance by allowables knockdown** |

**Barely visible impact damage (BVID) is the design case.** A tool drop or a bird strike produces internal delamination and matrix cracking with almost no external mark, and the compression-after-impact strength is substantially below the pristine value.

**The design approach is to size for the presence of undetectable damage** rather than to predict growth. Compression after impact allowables are measured on deliberately damaged coupons, and the structure is sized against those.

**That makes composite structure conservative by construction**, and it is why the mass saving over aluminium is smaller in practice than the raw specific properties suggest.

---

## Surface preparation

**The dominant variable in bond durability, and it is a process rather than a material.**

| Adherend | Preparation |
|---|---|
| **Aluminium** | Degrease, etch, **phosphoric acid anodise**, prime |
| Titanium | Degrease, etch, sol-gel or plasma |
| **Composite** | **Peel ply removal**, or abrade and solvent wipe |

**The difference between preparations shows up in durability, not in initial strength.** A poorly prepared bond can test perfectly on delivery and fail after two years of humidity exposure, because the failure is progressive hydration of the oxide at the interface.

**That is why bonded primary structure is qualified by wedge test** rather than by lap shear alone: the wedge test measures durability, and lap shear does not.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| The ends of the overlap carry the load | The middle does not |
| Overlap beyond ~30x the bondline adds little | |
| Double lap or scarf, never single lap if avoidable | Eccentricity |
| Never load in peel or cleavage | Fastener-arrest if unavoidable |
| Maximum strain criterion | The conservative aerospace default |
| First ply failure is not laminate failure | Unless it leaks |
| Size for BVID | Damage tolerance, not growth prediction |
| Phosphoric acid anodise for aluminium | Durability, not initial strength |

---

## Failure modes

**Single lap designed at double lap allowables.** Peel at the ends.

**Overlap lengthened to gain strength.** The middle carries nothing.

**Bonded joint loaded in peel.** Very low capability.

**Simple etch instead of anodise.** Passes on delivery, fails in service.

**Pristine allowables used for composite structure.** BVID is the design case.

**First ply failure treated as ultimate.** Or ignored on a leak path.

**Room temperature dry allowables used.** Hot-wet is the design condition.

---

## Standards

| Standard | Scope |
|---|---|
| **CMH-17** | Composite materials handbook, all volumes |
| ASTM D1002 | Lap shear strength, metal to metal |
| **ASTM D3762** | Adhesive bonded surface durability, wedge test |
| ASTM D7137 | Compressive residual strength after impact |
| ASTM D5528 | Mode I interlaminar fracture toughness |
| ASTM D2651 | Preparation of metal surfaces for adhesive bonding |
| NASA-STD-5019 | Fracture control |

---

## Tool interface

```python
# Adhesive and laminate analysis is not implemented in this domain. The shear lag and
# bearing relations live with the joint classes, and the composite allowables live in
# aerospaceMaterials.
import sys
sys.path.insert(0, '../aerospaceMaterials/aerospaceMaterialsLibrary')

from MaterialDatabase import queryMaterial

record = queryMaterial('IM7/8552', 'autoclave cured')
print(record['elasticModulus'], record['density'])
```

---

## References

1. Hart-Smith, L. J., *Adhesive-Bonded Single-Lap Joints*, NASA CR-112236, 1973.
2. CMH-17, *Composite Materials Handbook*, Volumes 1 to 3.
3. Volkersen, O., "Die Nietkraftverteilung in zugbeanspruchten Nietverbindungen", *Luftfahrtforschung*, Vol. 15, 1938.
