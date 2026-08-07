[Home](../README.md) > Nickel Alloys

# Nickel Alloys

## Contents

- [Overview](#overview)
- [The alloys](#the-alloys)
- [Inconel 718](#inconel-718)
- [Inconel 625](#inconel-625)
- [Monel](#monel)
- [Hydrogen resistance](#hydrogen-resistance)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Nickel alloys are what gets used where aluminium and stainless run out: high temperature, high pressure, aggressive oxidisers, and hydrogen. They are expensive, slow to machine and heavy, and there is frequently no alternative.

---

## The alloys

| Alloy | Yield [MPa] | Max temperature | Distinguishing feature |
|---|---|---|---|
| **IN718** | 1035 (STA) | 650 degC | **The workhorse.** Strong, weldable, LPBF friendly |
| **IN625** | 415 | 815 degC | **Corrosion resistance.** PREN 51 |
| **Monel 400** | 240 | 480 degC | **Oxygen compatible.** Ni-Cu |
| Monel K-500 | 690 | 480 degC | Age hardened Monel |
| Haynes 230 | 380 | **1150 degC** | Very high temperature, oxidation resistant |
| Hastelloy X | 355 | 1200 degC | Combustor and hot gas |
| Waspaloy | 795 | 760 degC | Turbine discs |

---

## Inconel 718

**The most used nickel alloy in aerospace, and for four independent reasons.**

| Reason | Detail |
|---|---|
| **Strength** | 1035 MPa yield in STA, comparable to a high strength steel |
| **Weldable** | Unusual among precipitation hardened superalloys |
| **Available** | In every product form, from many suppliers |
| **LPBF friendly** | One of the best characterised additive alloys |

**Its weldability is the property that distinguishes it.** Most gamma-prime strengthened superalloys crack during post-weld heat treatment because the precipitation reaction is fast enough to occur while the weld is still cooling and stressed. IN718 is strengthened by gamma-double-prime, which precipitates sluggishly, so the weld can be made and heat treated without strain age cracking.

**The 650 degC limit is the gamma-double-prime instability.** Above it the metastable gamma-double-prime transforms to the equilibrium delta phase and the strength falls away. That is a hard ceiling and it is why higher temperature applications go to other alloys.

**The standard heat treatment** is solution at 950 to 1065 degC, then a two-step age at 720 and 620 degC. Solution temperature choice is a real decision: a lower solution temperature retains delta phase at the grain boundaries and controls grain growth, giving better fatigue; a higher one dissolves it and gives better creep.

**It is the hardest common alloy to machine**, with a machinability index of 12 against 6061's 190. See [machiningProcesses Machinability.md](../../machiningProcesses/docs/Machinability.md).

---

## Inconel 625

**Solid solution strengthened, so it is not as strong and it does not care about temperature.**

| Property | Detail |
|---|---|
| **PREN 51** | Essentially immune to chloride pitting |
| **815 degC** | Long term service |
| **No ageing** | It is used annealed. Nothing to overage |
| Excellent weldability | And 625 filler is used on many dissimilar joints |

**Its corrosion resistance is the reason to choose it.** A CPT of +57 degC means it does not pit in chloride at any temperature it will meet in service, and it resists a wide range of acids and oxidisers.

**It does not lose strength by overageing** because there is nothing to overage. That makes it forgiving in welded and thermally cycled service where a precipitation hardened alloy would degrade.

**IN625 filler is the standard for dissimilar metal welds** between stainless and nickel, and between very different grades generally, because its wide solubility accommodates the dilution.

---

## Monel

**Nickel-copper, and its distinguishing property is oxygen compatibility.**

| Property | Detail |
|---|---|
| **Oxygen compatible** | **Including GOX and LOX at high pressure** |
| Seawater resistant | The original application |
| **Hydrofluoric acid resistant** | Almost uniquely |
| Non-sparking | |

**Monel is the material for high pressure gaseous oxygen service** and there is very little else. Its combination of a high ignition threshold and a low heat of combustion means it resists the ignition and burn propagation that destroys other metals in oxygen.

**That places it in oxygen valve seats, high pressure GOX lines and LOX system internals**, where the alternative is often a design that avoids the problem rather than a different material.

**K-500 is the age hardened version** at 690 MPa yield, used where the strength is needed. It is more susceptible to hydrogen embrittlement in the aged condition, which is the usual trade.

---

## Hydrogen resistance

**Nickel alloys are generally the answer for hydrogen service, and the picture is not simple.**

| Alloy | Hydrogen environment embrittlement |
|---|---|
| **IN718 STA** | **Susceptible.** High strength, and it is affected |
| IN718 annealed | Much better |
| **IN625** | Good |
| Monel 400 | Good |
| **A286** | Good |
| 316L | **Very good** |

**High strength is the risk factor**, as it is in every family. IN718 in the fully aged condition is one of the more hydrogen susceptible superalloys, and that is a surprise to people who choose it for a hydrogen system on the strength of the family reputation.

**316L is the best of the common structural alloys in hydrogen** and it is often the right answer for a gaseous hydrogen line despite being weaker, because the knockdown that applies to a susceptible alloy exceeds the strength difference.

See [aerospaceMaterials HydrogenEmbrittlement.md](../../docs/HydrogenEmbrittlement.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| IN718 for strength, weldability and availability | Below 650 degC |
| The 650 degC limit is gamma-double-prime | A hard ceiling |
| IN625 for corrosion and for temperature | PREN 51, 815 degC |
| IN625 filler for dissimilar joints | Wide solubility |
| Monel for high pressure oxygen | Very few alternatives |
| IN718 STA is hydrogen susceptible | Despite the family reputation |
| 316L is better in hydrogen than IN718 STA | Often the right answer |
| Machinability index 12 | Plan for it |

---

## Failure modes

**IN718 used above 650 degC.** Gamma-double-prime transforms and the strength goes.

**IN718 STA in gaseous hydrogen.** Susceptible.

**A gamma-prime superalloy welded and aged.** Strain age cracking.

**Aluminium or stainless in high pressure GOX.** Ignition.

**IN718 machined at stainless parameters.** Rapid tool failure.

**Solution temperature not specified.** Fatigue and creep differ substantially.

---

## Standards

| Standard | Scope |
|---|---|
| **AMS 5662 / 5663** | IN718 bar, forgings and rings, and the heat treatment |
| AMS 5596 | IN718 sheet, strip and plate |
| AMS 5599 | IN625 sheet, strip and plate |
| AMS 4675 | Monel 400 |
| **ASTM G93 / ASTM G124** | Oxygen system cleanliness and flammability |
| **NASA-STD-6001** | Flammability, offgassing and compatibility |
| **ASTM F1459 / G142** | Hydrogen environment embrittlement testing |
| AWS D17.1 | Fusion welding for aerospace |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterialsLibrary')

from MaterialDatabase import queryMaterial

for temperature in (293.0, 650.0, 815.0):
    for material, condition in (('INCONEL 718', 'sta'), ('INCONEL 625', 'annealed')):
        record = queryMaterial(material, condition, temperature = temperature)
        print(f'{material:14s} {temperature:5.0f} K  '
              f'yield {record["yieldStrength"]/1e6:6.0f} MPa')
```

---

## References

1. Reed, R. C., *The Superalloys: Fundamentals and Applications*, Cambridge University Press, 2006.
2. Special Metals Corporation, *Inconel Alloy 718* and *Inconel Alloy 625* datasheets.
3. MMPDS-2023, *Metallic Materials Properties Development and Standardization*.
