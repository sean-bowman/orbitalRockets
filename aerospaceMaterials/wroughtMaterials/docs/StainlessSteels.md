[Home](../README.md) > Stainless Steels

# Stainless Steels

## Contents

- [Overview](#overview)
- [The families](#the-families)
- [Austenitic](#austenitic)
- [Precipitation hardening](#precipitation-hardening)
- [Sensitization](#sensitization)
- [Pitting resistance](#pitting-resistance)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Stainless steel is the fluid system material: lines, fittings, valve bodies, manifolds and cryogenic hardware. Austenitic grades dominate because they are weldable, formable, tough at cryogenic temperature and compatible with almost every propellant.

---

## The families

| Family | Structure | Magnetic | Weldable | Hardenable | Use |
|---|---|---|---|---|---|
| **Austenitic (300)** | **FCC** | No | **Excellent** | Work only | **Fluid systems, cryogenic** |
| Ferritic (400) | BCC | Yes | Moderate | No | **Has a DBTT.** Not for cryogenic |
| Martensitic (410, 440) | BCT | Yes | Poor | **Heat** | Cutting tools, shafts |
| **Precipitation hardening** | Varies | Yes | Moderate | **Heat** | **High strength fittings, bosses** |
| Duplex | Both | Yes | Good | No | Chloride service, high strength |

**Austenitic is the aerospace default and the FCC structure is why.** No ductile-to-brittle transition, so it is safe to 4 K; excellent weldability; and good compatibility with cryogenic oxygen, which is not true of most structural metals.

**Ferritic and martensitic grades have a DBTT** and they are prohibited in cryogenic structural service for that reason.

---

## Austenitic

| Grade | Yield [MPa] | Distinguishing feature |
|---|---|---|
| **304L** | 170 | Cheap, general purpose, low carbon |
| **316L** | 205 | **Molybdenum.** Better pitting resistance |
| **321** | 205 | **Titanium stabilised.** No sensitization |
| 347 | 205 | Niobium stabilised. Same intent |
| A286 | 590 | **Precipitation hardened austenitic.** Fasteners |

**316L is the fluid system default** and the molybdenum is what earns it: PREN 26.1 against 304L's 19, and a correspondingly better resistance to chloride pitting.

**321 and 347 are stabilised grades** with titanium or niobium added to tie up the carbon as a stable carbide, so that chromium carbide cannot form at the grain boundaries. They are the answer where a part will see the sensitization range in service and cannot be solution annealed afterwards.

**The L suffix means low carbon**, below 0.03 percent, which slows sensitization enough that a normal weld does not cause it. It costs a little strength.

**A286 is the aerospace fastener alloy** in this family: an austenitic matrix that is precipitation hardened to 590 MPa yield, non-magnetic, and usable to 700 degC.

---

## Precipitation hardening

| Grade | Condition | Yield [MPa] | Notes |
|---|---|---|---|
| **17-4PH** | **H900** | 1170 | Strongest, least tough, most SCC susceptible |
| 17-4PH | **H1025** | 1000 | **The usual choice** |
| 17-4PH | H1150 | 795 | Toughest, most SCC resistant |
| 15-5PH | H1025 | 1000 | Lower delta ferrite, better transverse properties |

**The H-number is the ageing temperature in degrees Fahrenheit**, and the same overageing trade as aluminium applies: higher number means lower strength and better toughness and SCC resistance.

**H900 is rarely the right choice.** It is the strongest and it is notably susceptible to hydrogen embrittlement and stress corrosion, and the strength difference to H1025 is 15 percent.

**17-4PH contains 3 to 5 percent copper**, which is the precipitating element. **That does not make it a copper-base alloy** and it does not fall under the hydrazine copper prohibition, which applies to copper matrix alloys. That distinction cost a wrong test assertion in this build and it is worth stating.

---

## Sensitization

**Chromium carbide precipitation at the grain boundaries, leaving a chromium depleted zone that corrodes intergranularly.**

| Element | Detail |
|---|---|
| **Temperature range** | 425 to 815 degC |
| **Cause** | Carbon and chromium combining at the boundaries |
| **Result** | The boundary is locally below 12 % chromium and no longer stainless |
| Detection | ASTM A262 practices |

**Welding is the usual cause** because the HAZ passes through the range. A thick section weld holds material in the range long enough to sensitize it.

**Three controls, and they are alternatives rather than a sequence:**

| Control | Detail |
|---|---|
| **Low carbon (L grades)** | Below 0.03 % C. Slows it enough for normal welding |
| **Stabilised grades (321, 347)** | Ti or Nb ties the carbon up permanently |
| **Post-weld solution anneal** | Redissolves the carbides. Often impractical on a large weldment |

**The time-temperature-sensitization C-curve is what [`HeatTreatment`](../../aerospaceMaterialsLibrary/HeatTreatment.py) computes**, and it turns the 316 against 316L argument into a computed time at temperature rather than a rule of thumb.

**An as-cast austenitic stainless is sensitized** because it cooled slowly through the range, which is why castings in these grades are always solution annealed. See [castingProcesses](../../castingProcesses/).

---

## Pitting resistance

```
PREN = %Cr + 3.3 (%Mo + 0.5 %W) + 16 %N
CPT = 2.5 * PREN - 71        [degC]
```

| Grade | PREN | CPT |
|---|---|---|
| 304L | 19.0 | -24 degC |
| **316L** | **26.1** | **-6 degC** |
| 317L | 30 | +4 degC |
| Duplex 2205 | 35 | +17 degC |
| **IN625** | **51** | **+57 degC** |

**The critical pitting temperature is the useful output.** Above it, pitting initiates in chloride solution; below it, it does not.

**316L's CPT of -6 degC means it pits at room temperature in chloride**, which is why marine and coastal launch site exposure is a real concern for stainless hardware and why 316L is not the answer for permanent seawater service.

**PREN values in a database must reconcile with the chemistry stored alongside them**, and in this build six of eleven did not until they were corrected. The worst was Haynes 230, which stored 28.6 against a computed 51.7.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Austenitic for cryogenic and fluid systems | FCC, no DBTT |
| Ferritic and martensitic have a DBTT | Not for cryogenic |
| 316L as the fluid system default | PREN 26.1 |
| L grades for weldments | Below 0.03 % C |
| 321 or 347 for service in the sensitization range | |
| Sensitization range | 425 to 815 degC |
| 17-4PH H1025 as the usual PH choice | H900 is rarely right |
| CPT = 2.5 PREN - 71 | The useful output |

---

## Failure modes

**Ferritic grade used at cryogenic temperature.** DBTT.

**316 rather than 316L welded in a thick section.** Sensitized HAZ.

**As-cast austenitic used without solution anneal.** Sensitized.

**17-4PH H900 in a hydrogen or SCC environment.** The most susceptible condition.

**316L assumed immune to chloride pitting.** Its CPT is below room temperature.

**PREN quoted without reconciling against the chemistry.** Six of eleven were wrong here.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM A240 / A276** | Stainless plate and bar |
| ASTM A269 / A213 | Stainless tube |
| **ASTM A262** | Detecting susceptibility to intergranular attack |
| ASTM G48 | Pitting and crevice corrosion, ferric chloride |
| ASTM G150 | Critical pitting temperature |
| **AMS 5643** | 17-4PH bar, forgings and rings |
| AMS 5731 / 5737 | A286 |
| AWS D17.1 | Fusion welding for aerospace |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterialsLibrary')

from CorrosionAssessment import CorrosionAssessment

for material in ('304L', '316L', 'INCONEL 625'):
    assessment = CorrosionAssessment()
    assessment.setInputs({'anodeMaterial': material, 'anodeCondition': 'annealed'})
    result = assessment.calculatePittingResistance()
    print(f'{material:14s} PREN {result["pren"]:5.1f}  '
          f'CPT {result["criticalPittingCelsius"]:+6.1f} degC')
```

---

## References

1. Sedriks, A. J., *Corrosion of Stainless Steels*, 2nd ed., Wiley, 1996.
2. ASM Handbook Volume 1, *Properties and Selection: Irons, Steels, and High-Performance Alloys*.
3. MMPDS-2023, *Metallic Materials Properties Development and Standardization*.
