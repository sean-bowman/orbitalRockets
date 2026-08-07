[Home](../README.md) > Solidification

# Solidification

## Contents

- [Overview](#overview)
- [Chvorinov](#chvorinov)
- [The modulus](#the-modulus)
- [Directional solidification](#directional-solidification)
- [Shrinkage](#shrinkage)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Everything about a casting's soundness follows from where it freezes last. Solidification analysis is the discipline of arranging for that place to be in the riser rather than in the part.

---

## Chvorinov

```
t = B * (V / A)^n          n = 2
```

**The volume to cooling area ratio is the modulus**, and two castings with the same modulus freeze in the same time whatever their shape. That single fact is what makes riser design tractable.

**The exponent of 2 makes the dependence strong.** Doubling the modulus quadruples the time, so a small increase in section thickness has a large effect on freezing.

**B is the mould constant**, carrying the mould material, coating and preheat:

| Mould | Relative B |
|---|---|
| Die (steel, cooled) | 0.6 |
| Permanent mould | 1.0 |
| Investment shell | 1.4 |
| **Sand** | **2.2** |

---

## The modulus

**Computing the modulus correctly is most of the skill.**

| Feature | Modulus |
|---|---|
| Plate, thickness t, cooled both sides | t / 2 |
| Bar, square side a | a / 4 |
| Cylinder, diameter d | d / 4 |
| Sphere, diameter d | d / 6 |

**A sphere has the largest modulus for a given volume**, which is why a spherical riser freezes last and why risers are made as compact as possible.

**Junctions have a higher modulus than either member**, because material meets from several directions and the cooling area does not increase in proportion. **That is why hot spots form at junctions** and why they are the classic shrinkage location.

**A designer can move a hot spot by changing a fillet radius**, and that is a genuine and underused design lever.

---

## Directional solidification

**The goal is for the casting to freeze progressively towards the riser**, so that liquid feed is always available behind the front.

| Technique | Effect |
|---|---|
| **Tapered sections** | Thin at the far end, thick towards the riser |
| **Chills** | Metal inserts in the mould, locally accelerating freezing |
| Riser placement | On the heaviest section |
| Insulating sleeves | Slow the riser so it freezes last |
| Exothermic sleeves | Actively heat the riser |

**Chills are the most useful tool** for a casting whose geometry cannot be tapered. A chill at an isolated heavy section makes it freeze early, converting a hot spot into a cold one.

**The rule is that no isolated heavy section can be fed**, and if the geometry produces one the answer is a chill, a change of geometry, or accepting the shrinkage.

---

## Shrinkage

**Three separate contractions, and they are often confused.**

| Contraction | Magnitude | Compensated by |
|---|---|---|
| **Liquid contraction** | Small | The pour |
| **Solidification shrinkage** | **3 to 6.5 %** | **The riser** |
| **Solid contraction** | 1 to 2 % linear | **The pattern being oversize** |

| Alloy family | Solidification shrinkage |
|---|---|
| Steel | 3.0 % |
| Titanium | 3.0 % |
| Stainless | 4.0 % |
| Nickel | 4.5 % |
| Copper | 4.5 % |
| **Aluminium** | **6.5 %** |

**Aluminium's 6.5 percent is why aluminium castings have poor yield.** It needs roughly twice the riser volume of steel for the same casting, so a much larger fraction of the poured metal ends up in the risers.

**Pattern shrinkage compensates for solid contraction only** and it is a completely separate allowance from the machining stock. Getting it wrong makes every casting from that tool the wrong size, and it is not recoverable by machining if the error went the wrong way.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Chvorinov exponent | 2 |
| Sphere has the largest modulus | Which is why risers are compact |
| Junctions have a raised modulus | The classic hot spot |
| No isolated heavy section can be fed | Chill it or redesign |
| Taper towards the riser | Directional solidification |
| Solidification shrinkage | 3 % steel to 6.5 % aluminium |
| Pattern shrinkage is separate | And it is not machined off |

---

## Failure modes

**Isolated heavy section.** Cannot be fed; centreline shrinkage.

**Hot spot at a junction.** Shrinkage porosity in the part.

**Riser modulus below the casting's.** It freezes first and stops feeding.

**Aluminium risered like steel.** Half the volume needed.

**Pattern shrinkage confused with machining stock.** Every casting the wrong size.

---

## Standards

| Standard | Scope |
|---|---|
| ISO 8062 | Casting tolerances and machining allowances |
| AMS 2175 | Castings, classification and inspection |
| ASTM E446 / E186 / E280 | Reference radiographs |

---

## Tool interface

```python
from CastingProcess import CastingProcess, SOLIDIFICATION_SHRINKAGE

for process in ('investment', 'sand', 'die'):
    casting = CastingProcess()
    casting.setInputs({'process': process, 'castingVolume': 1.0e-4,
                       'castingSurfaceArea': 0.05})
    result = casting.calculateSolidification()
    print(f'{process:16s} B={result["chvorinovConstant"]:.1e}  '
          f't_sol={result["solidificationTime"]:.1f} s')
```

---

## References

1. Chvorinov, N., "Theory of the Solidification of Castings", *Giesserei*, Vol. 27, 1940.
2. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
3. Stefanescu, D. M., *Science and Engineering of Casting Solidification*, 3rd ed., Springer, 2015.
