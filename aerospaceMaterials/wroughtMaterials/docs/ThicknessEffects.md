[Home](../README.md) > Thickness Effects

# Thickness Effects

## Contents

- [Overview](#overview)
- [The quench rate mechanism](#the-quench-rate-mechanism)
- [The property fall-off](#the-property-fall-off)
- [Quench factor analysis](#quench-factor-analysis)
- [Alloy sensitivity](#alloy-sensitivity)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A thick section has lower properties than a thin one in the same alloy and temper, and the reason is that its core cooled more slowly during the quench. MMPDS tables are stratified by thickness for exactly this reason, and using the wrong stratum is a common and optimistic error.

---

## The quench rate mechanism

**Precipitation hardening requires the solute to be retained in solution through the quench.**

| Step | Detail |
|---|---|
| **Solution treat** | The alloying elements dissolve into the aluminium |
| **Quench** | Cool fast enough that they stay dissolved |
| **Age** | Precipitate them in a controlled fine distribution |

**If the quench is too slow, precipitation happens during the quench**, at the grain boundaries and on dispersoids, in a coarse distribution that contributes little strength and consumes the solute that the ageing treatment needed.

**A thick section cannot be quenched fast in its core.** Heat has to conduct from the centre to the surface, and the conduction time goes as the square of the section thickness. A 100 mm plate core cools an order of magnitude more slowly than a 12 mm plate core.

**The surface of a thick plate is fine and its core is not**, so the property gradient is through the thickness. A part machined from the core of a thick plate has lower properties than one machined from near the surface, and the allowables tables give the minimum across the section.

---

## The property fall-off

| Thickness | Typical 7075-T73 yield, relative |
|---|---|
| 6 mm | 1.00 |
| 25 mm | 0.97 |
| 50 mm | 0.93 |
| **100 mm** | **0.88** |
| 150 mm | 0.85 |

**A 12 to 15 percent reduction from thin plate to very thick plate** is typical of the quench sensitive 7000 series, and it is larger for toughness than for strength.

**Toughness falls faster than strength**, because the coarse grain boundary precipitation that slow quenching produces is a fracture path as well as a strength loss.

**The MMPDS stratification is the authority** and it is not interpolated casually. The tables give a value per thickness band and a part at the top of a band gets the band's value.

---

## Quench factor analysis

**The quantitative treatment, and it is what [`HeatTreatment`](../../aerospaceMaterialsLibrary/HeatTreatment.py) computes.**

The Staley quench factor integrates the time spent at each temperature against the C-curve for precipitation:

```
Q = integral dt / C_T(T)
sigma / sigma_max = exp(k1 * Q)
```

| Symbol | Meaning |
|---|---|
| `C_T(T)` | The time at temperature `T` to produce a defined fraction of precipitation |
| `Q` | The accumulated fraction of the available precipitation that occurred during the quench |
| `k1` | A material constant, negative |

**Q = 0 is a perfect quench** and the material reaches its full aged strength. **Q around 1 loses a substantial fraction.**

**It converts a cooling curve into a strength prediction**, which is what makes it useful: a measured or computed quench curve for a specific part geometry gives a specific expected property, rather than a table lookup by nominal thickness.

**Grossmann quench severity numbers are tabulated in inverse inches**, which is a unit trap. Using them as inverse metres understates the Biot number by a factor of 39 and makes every quench look perfect.

---

## Alloy sensitivity

**Not all alloys are quench sensitive to the same degree.**

| Alloy | Quench sensitivity | Notes |
|---|---|---|
| **7075** | **High** | The classic quench sensitive alloy |
| 7050 | **Lower** | Developed specifically for thick sections |
| 7175 | Lower | Same intent |
| 2024 | Moderate | |
| **2219** | Low | One reason it suits thick tank structure |
| 6061 | **Low** | Very forgiving |

**7050 exists because 7075 is quench sensitive.** The copper and zirconium adjustments reduce the tendency to precipitate during the quench, so 7050-T7451 holds its properties in 100 mm plate where 7075 does not. **That is the alloy to specify for thick machined structure.**

**6061's low quench sensitivity is part of why it is so widely used.** It tolerates a slow quench, which means less distortion and fewer residual stress problems, at the cost of a lower peak strength.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Properties fall with section thickness | Quench rate |
| Conduction time goes as thickness squared | |
| 7075 thick plate | ~12 % below thin |
| Toughness falls faster than strength | |
| Use the correct MMPDS thickness stratum | Do not interpolate casually |
| **7050 for thick sections** | Developed for it |
| 6061 and 2219 are quench tolerant | |
| Grossmann numbers are inverse inches | A unit trap |

---

## Failure modes

**Thin plate allowables used for a thick part.** Optimistic by 10 to 15 %.

**7075 specified for 100 mm plate.** 7050 is the alloy for that section.

**Quench sensitivity ignored in an alloy substitution.** The substitute may be far more sensitive.

**Grossmann severity used as inverse metres.** Every quench looks perfect.

**Toughness assumed to scale with strength.** It falls faster.

---

## Worked numbers

From [`HeatTreatment.calculateQuenchFactor`](../../aerospaceMaterialsLibrary/HeatTreatment.py), 7075 in water:

| Section | Quench factor Q | Strength retained |
|---|---|---|
| Thin | Low | Near full |
| **Thick** | **Higher** | **Reduced** |

**The Biot number decides whether the quench is surface limited or conduction limited**, and the Grossmann severity in inverse inches, converted by 39.37, is what makes that calculation come out right.

---

## Standards

| Standard | Scope |
|---|---|
| **MMPDS** | Allowables stratified by thickness |
| **AMS 2770** | Heat treatment of wrought aluminium alloy parts |
| ASTM B918 | Heat treatment of wrought aluminium alloys |
| AMS 2750 | Pyrometry |
| ASTM B209 | Aluminium sheet and plate |
| ASTM A255 | Determining hardenability of steel, the Jominy method |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterialsLibrary')

from HeatTreatment import HeatTreatment

for thickness in (0.012, 0.050, 0.100):
    treatment = HeatTreatment()
    treatment.setInputs({'material': '7075', 'condition': 't73',
                         'sectionThickness': thickness, 'quenchant': 'agitated water'})
    result = treatment.calculateQuenchFactor()
    print(f'{thickness*1000:5.0f} mm: Q {result["quenchFactor"]:6.2f}, '
          f'strength retained {result["retainedStrengthFraction"]*100:.1f} %')
```

---

## References

1. Staley, J. T., "Quench Factor Analysis of Aluminium Alloys", *Materials Science and Technology*, Vol. 3, 1987.
2. MMPDS-2023, *Metallic Materials Properties Development and Standardization*.
3. ASM Handbook Volume 4, *Heat Treating*.
