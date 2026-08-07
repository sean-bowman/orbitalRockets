[Home](../README.md) > Post-Processing

# Post-Processing

## Contents

- [Overview](#overview)
- [The sequence](#the-sequence)
- [Heat treatment](#heat-treatment)
- [HIP](#hip)
- [Machining](#machining)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

A centrifugal casting comes out sound at the outer wall and contaminated at the bore, with a directional columnar structure and casting residual stress. What follows fixes the last two.

---

## The sequence

| Step | Purpose |
|---|---|
| **1. Extract and cut off** | Remove risers if any, and the pour end |
| **2. Heat treat** | Homogenise, and develop the required condition |
| **3. HIP, if specified** | Close residual porosity, for a casting factor of 1.0 |
| **4. Rough machine the bore** | Remove the segregated layer |
| **5. Inspect** | Now the surfaces are clean enough to inspect properly |
| **6. Finish machine** | Datums, then features |

**Machining the bore before inspection is deliberate.** The as-cast bore is rough and oxidised, and penetrant on it indicates everywhere. Removing the segregated layer first gives a surface that can actually be inspected.

---

## Heat treatment

**Every centrifugal casting is heat treated**, and the reason is the directional structure rather than strength.

| Treatment | Purpose |
|---|---|
| **Homogenisation** | Reduce the microsegregation the directional freezing produced |
| **Solution anneal** | Austenitic stainless: dissolve carbides formed during the slow cool |
| Normalise | Steel: refine the coarse columnar structure |
| Solution and age | Where the alloy is precipitation hardened |
| Stress relief | Casting residual stress from the constrained contraction |

**The columnar structure is not always wanted.** It gives good hoop properties and poor radial ones, and a normalising treatment breaks it into equiaxed grains where isotropy matters more than hoop strength.

**Austenitic stainless castings need a solution anneal**, because the slow cool through the sensitization range precipitates chromium carbide at the grain boundaries. An as-cast austenitic stainless is sensitized. See [aerospaceMaterials HeatTreatment](../../docs/HeatTreatment.md).

---

## HIP

**Required to reach a casting factor of 1.0** in most qualification schemes, alongside the process qualification and the volumetric NDE. See [castingProcesses](../../castingProcesses/).

| Effect | Detail |
|---|---|
| **Closes internal porosity** | Gas and shrinkage both |
| **Does not close surface connected porosity** | No pressure differential across the pore wall |
| Homogenises | The temperature is high and the time is long |
| May coarsen | Check against the alloy's solvus |

**A centrifugal casting is a good HIP candidate** because its porosity is mostly interior and mostly at the bore end, which is machined away in any case. The HIP is often about the qualification requirement rather than about a defect anyone has found.

---

## Machining

| Surface | Allowance | Notes |
|---|---|---|
| **Bore** | 1.5 to 3 mm | Removes the segregated layer. See [MachiningAllowance.md](MachiningAllowance.md) |
| **Outer** | 1 to 2 mm | Dimensional only. This is the best material |
| Ends | As required | The pour end is the worst |

**Rough the bore before finish machining anything**, because removing the segregated layer redistributes the casting residual stress and the part moves.

**The pour end is the worst material** in the casting: last to freeze, most contaminated, and often where a shrinkage cavity sits. It is cut off and the length allowance accounts for it.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Machine the bore before inspecting | The as-cast surface cannot be inspected |
| Solution anneal austenitic stainless | As-cast, it is sensitized |
| Normalise where isotropy matters | It breaks the columnar structure |
| HIP for a casting factor of 1.0 | With process qualification and NDE |
| HIP does not close surface porosity | No differential |
| Rough the bore first | The part moves |
| Cut off the pour end | It is the worst material |

---

## Failure modes

**Penetrant on an as-cast bore.** It indicates everywhere.

**Austenitic stainless used as cast.** Sensitized, and it corrodes intergranularly.

**Finish machined before roughing the bore.** The part moved.

**Pour end retained.** Shrinkage and contamination in the part.

**HIP expected to close surface connected porosity.** It does not.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM A451 / A426** | Centrifugally cast pipe, including heat treatment |
| ASTM A1080 | Hot isostatic pressing of steel and stainless |
| ASTM A262 | Detecting susceptibility to intergranular attack |
| AMS 2750 | Pyrometry |
| ISO 8062 | Machining allowances |

---

## References

1. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
2. ASM Handbook Volume 4, *Heat Treating*.
3. ASM Handbook Volume 15, *Casting*.
