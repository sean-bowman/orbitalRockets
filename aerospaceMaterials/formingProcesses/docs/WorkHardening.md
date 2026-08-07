[Home](../README.md) > Work Hardening

# Work Hardening

## Contents

- [Overview](#overview)
- [The power law](#the-power-law)
- [Uniform elongation equals n](#uniform-elongation-equals-n)
- [The values](#the-values)
- [Anneal scheduling](#anneal-scheduling)
- [Forming loads](#forming-loads)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Work hardening is what makes forming possible. Without it, any local thinning would run away immediately and no sheet could be stretched at all. The exponent that describes it also predicts exactly how far the sheet can go.

---

## The power law

```
sigma = K * eps^n
```

| Symbol | Meaning |
|---|---|
| `sigma` | True stress |
| `eps` | True plastic strain |
| `K` | Strength coefficient, the true stress at unit strain |
| `n` | **Work hardening exponent** |

**`n` describes how fast the material strengthens as it deforms.** A high `n` means the material fights back hard against further deformation, which is what stabilises a forming operation.

**`K` sets the load** and it has little to do with formability. A high `K` material needs a big press; a high `n` material forms well.

---

## Uniform elongation equals n

**The most useful result in sheet forming, and it falls out in two lines.**

Necking begins at the maximum of the load, where `dP = 0`. With `P = sigma A` and volume conservation `dA/A = -deps`:

```
d(sigma)/sigma = deps
```

Substituting the power law, `d(sigma)/deps = n K eps^(n-1)`, gives

```
n K eps^(n-1) / (K eps^n) = 1     ->     eps = n
```

**The uniform true strain at the onset of necking is numerically equal to `n`.**

**That makes `n` directly readable as a formability number.** A material with n = 0.25 can be stretched 25 percent uniformly, and beyond that the deformation localises into a neck and the part splits.

**It is also the basis of the FLD correlation**, which is why FLD0 is a function of `n`. See [FormingLimitDiagram.md](FormingLimitDiagram.md).

---

## The values

| Material | Condition | n | K [MPa] | Uniform elongation |
|---|---|---|---|---|
| **316L** | annealed | **0.45** | 1400 | **45 %** |
| 304L | annealed | 0.45 | 1400 | 45 % |
| 6061 | O | 0.22 | 400 | 22 % |
| 2219 | O | 0.20 | 480 | 20 % |
| **6061** | **T6** | **0.05** | 450 | **5 %** |
| 7075 | T73 | 0.06 | 700 | 6 % |
| Ti-6Al-4V | annealed | 0.08 | 1100 | 8 % |
| IN718 | annealed | 0.30 | 1600 | 30 % |

**Austenitic stainless is the best formable structural metal**, and n = 0.45 is why. It also transforms partially to martensite as it deforms, which raises the effective hardening further and is the reason 304 deep draws so well.

**Temper dominates alloy.** 6061 goes from n = 0.22 annealed to n = 0.05 in T6, a factor of four. **That single row is the quantitative case for forming in the annealed condition and heat treating afterwards.**

**Precipitation hardened tempers work harden very little** because the precipitates already provide the obstacle density that dislocation accumulation would otherwise supply.

---

## Anneal scheduling

**Cold working consumes the material's remaining ductility**, and a multi-stage forming operation has to restore it.

| Accumulated strain | Action |
|---|---|
| Below 0.5 | Continue forming |
| **Above 0.5** | **Intermediate anneal required** |

**The 0.5 threshold is a working rule** rather than a physical constant, and it varies with the material. Below it a typical alloy retains enough ductility to continue; above it the next operation is likely to crack.

**Each anneal resets the accumulated strain to zero** and returns the material to its annealed flow curve.

**Anneals are expensive** in cycle time, in oxidation and in distortion, so a forming sequence is designed to minimise their number. That is one of the reasons a part is formed in a few large steps rather than many small ones.

**Austenitic stainless can absorb a great deal before needing one**, and 6061-T6 cannot be cold formed meaningfully at all, which puts it in a different class entirely.

---

## Forming loads

**The load follows `K`, not `n`.**

```
sigma = K * eps^n
```

At a strain of 0.2, 316L at K = 1400 flows at about 1010 MPa and 6061-O at K = 400 flows at about 289 MPa. The stainless part needs three and a half times the press force.

**High `K` and high `n` together is the difficult combination**: excellent formability requiring a very large press. Austenitic stainless and Inconel are both in that category, and Inconel 718 at K = 1600 is the reason nickel alloy forming is done hot wherever possible.

**Press capacity is often the real constraint on material choice for a formed part**, and it is a shop capability question rather than a design one.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Uniform elongation | Equals `n` |
| `n` is formability, `K` is load | Two independent properties |
| Form annealed, heat treat after | The 0.22 to 0.05 factor |
| Intermediate anneal | Above 0.5 accumulated strain |
| Austenitic stainless n = 0.45 | The best formable structural metal |
| Precipitation tempers barely harden | n ~0.05 |
| High K and high n | Excellent forming, very large press |

---

## Failure modes

**T6 temper formed to an annealed strain.** Four times the available uniform elongation.

**Anneal skipped in a multi-stage sequence.** Cracking on the later operation.

**Press sized from `n` rather than `K`.** Undersized.

**`n` measured on a different temper.** It is a condition property, not an alloy property.

**Uniform elongation confused with total elongation.** Total includes the post-necking strain, which is not usable in forming.

---

## Worked numbers

From [`FormingProcess.calculateWorkHardening`](../formingProcessesLibrary/FormingProcess.py) at an effective strain of 0.20:

| Material | n | Flow stress | Remaining uniform elongation |
|---|---|---|---|
| **316L annealed** | **0.45** | 618 MPa | **25.0 %** |
| 2219-T87 | 0.18 | 464 MPa | **0.0 %** |
| **6061-T6** | 0.20 | 290 MPa | **0.0 %** |

**316L still has 25 percent uniform elongation left after a 0.20 strain.** The precipitation hardened tempers have none: they were already past their uniform elongation before the strain was applied.

**The class carries one hardening exponent per alloy**, so the per-temper values in the table above are literature figures rather than class outputs. The physical point is unchanged and the class is the conservative reading of it.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM E646** | Tensile strain hardening exponents of sheet materials |
| ASTM E8 / E8M | Tension testing of metallic materials |
| ASTM E2218 | Determining forming limit curves |
| AMS 2770 | Heat treatment of wrought aluminium alloys |
| AMS 2759 | Heat treatment of steel parts |

---

## Tool interface

```python
from FormingProcess import FormingProcess, WORK_HARDENING, ANNEAL_STRAIN_THRESHOLD

for material, condition in (('316L', 'annealed'), ('2219', 't87'), ('6061', 't6')):
    forming = FormingProcess()
    forming.setInputs({'material': material, 'condition': condition,
                       'process': 'stretch form', 'thickness': 0.002})
    result = forming.calculateWorkHardening(effectiveStrain = 0.20)
    print(f'{material:8s} {condition:8s} n={result["hardeningExponent"]:.2f}  '
          f'flow {result["flowStress"]/1e6:6.0f} MPa  '
          f'remaining uniform {result["remainingUniformElongation"]*100:5.1f} %  '
          f'anneal {result["annealRequired"]}')
```

---

## References

1. Hollomon, J. H., "Tensile Deformation", *Transactions AIME*, Vol. 162, 1945.
2. Hosford, W. F. and Caddell, R. M., *Metal Forming: Mechanics and Metallurgy*, 4th ed., Cambridge, 2011.
3. ASTM E646, *Standard Test Method for Tensile Strain-Hardening Exponents of Metallic Sheet Materials*.
