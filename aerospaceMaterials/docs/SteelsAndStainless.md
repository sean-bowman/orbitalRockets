[Home](../README.md) > Steels and Stainless

# Steels and Stainless

## Contents

- [Overview](#overview)
- [The lattice decides everything](#the-lattice-decides-everything)
- [Austenitic stainless](#austenitic-stainless)
- [Sensitization](#sensitization)
- [Pitting and the launch site](#pitting-and-the-launch-site)
- [Precipitation hardening stainless](#precipitation-hardening-stainless)
- [A286, the exception](#a286-the-exception)
- [Low alloy steels](#low-alloy-steels)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The word stainless covers three families that behave completely differently, and the differences are more important than anything they share. Austenitic grades are tough at any temperature and weak. Precipitation hardening grades are strong and go brittle cold. Low alloy steels are stronger still and are disqualified from most launch vehicle service by hydrogen and by temperature.

Reading the family correctly is most of the work, and the family is set by the crystal lattice.

---

## The lattice decides everything

| Structure | Alloys | DBTT | Hydrogen | Magnetic |
|---|---|---|---|---|
| **FCC austenitic** | 304L, 316L, 321, 347, A286 | **None** | Resistant | No |
| **BCC martensitic** | 17-4PH, 15-5PH, 4340, 300M | **Yes** | **Susceptible** | Yes |

Face-centred cubic lattices have enough independent slip systems to deform plastically at any temperature, so they have no ductile-to-brittle transition. Body-centred cubic lattices do not, and below the transition they fracture with no warning and no deformation.

**The same lattice property drives hydrogen embrittlement.** BCC has high hydrogen diffusivity and low solubility, which concentrates hydrogen at traps and crack tips. FCC is the opposite. This is not a coincidence; it is the same mechanism seen twice.

**Consequence: a martensitic stainless is not a cryogenic material regardless of the word stainless in its name.** 17-4PH retains 25 percent of its room temperature fracture toughness at 77 K.

---

## Austenitic stainless

The fluid system default, and it earns the position by being tough everywhere and compatible with almost everything.

| Alloy | Fty [MPa] | Ftu [MPa] | PREN | Stabilised | Where it belongs |
|---|---|---|---|---|---|
| 304L | 170 | 485 | 19.3 | Low carbon | General, non-chloride |
| **316L** | **170** | **485** | **26.1** | Low carbon | **The default. Molybdenum for pitting** |
| **321** | 205 | 515 | 18.0 | **Titanium** | Welded hot gas lines |
| 347 | 205 | 515 | 18.0 | **Niobium** | Welded liners seeing a second thermal cycle |

**The strength is embarrassing next to aluminium** at three times the density, and it is why stainless is used for fluid systems rather than for structure. What it buys is a material that works from 4 K to 900 K, welds without heat treatment, and is compatible with LOX, hydrazine, N2O4 and cryogens alike.

**Cryogenic strengthening is dramatic.** 316L roughly doubles its yield strength between room temperature and 77 K, driven by strain-induced martensite formation as much as by lattice friction. That is a genuine design margin for cryogenic hardware and it is why a stainless cryogenic line is not as heavy as the room temperature numbers suggest.

---

## Sensitization

Held between roughly 700 and 1200 K, chromium carbide precipitates at the grain boundaries and depletes the adjacent chromium below the 12 percent needed for passivity. The alloy then corrodes intergranularly, and the damage is not visible.

**This is a welding problem**, because a weld drags the heat affected zone through exactly that range.

The time to sensitize scales steeply with carbon content:

| Grade | Carbon | Time to sensitize at 675 degC |
|---|---|---|
| 316 (standard) | 0.08 % | ~20 minutes |
| **316L** | **0.025 %** | **~6 hours** |
| **321 (Ti stabilised)** | 0.05 % | **~100 hours** |
| 347 (Nb stabilised) | 0.05 % | ~150 hours |

**That factor of eighteen between 316 and 316L is the entire reason the L grades exist**, and it is why a welded fluid system is built from 316L rather than 316 without further discussion.

**Stabilisation goes further than low carbon.** Titanium or niobium ties the carbon up as a stable carbide that does not dissolve and re-precipitate, so a stabilised grade survives a second thermal cycle. **347 is preferred over 321 where the part is welded and then stress relieved**, because niobium carbide is the more stable of the two through a second exposure.

Once sensitized, a solution anneal is the only recovery.

---

## Pitting and the launch site

The pitting resistance equivalent number quantifies what chromium, molybdenum and nitrogen buy:

```
PREN = %Cr + 3.3 (%Mo + 0.5 %W) + 16 %N
CPT [degC] = 2.5 PREN - 71
```

| Alloy | PREN | Critical pitting temperature |
|---|---|---|
| 321 / 347 | 18.0 | -26 degC |
| 304L | 19.3 | -23 degC |
| **316L** | **26.1** | **-6 degC** |
| Inconel 625 | 51.2 | **+57 degC** |

**316L pits at ambient temperature in a chloride environment**, and a coastal launch site is a chloride environment. That single number says more about material selection at a launch site than any compatibility table.

**Passivation restores the film; it does not raise the threshold.** Only alloy content does. Where a component genuinely has to survive salt spray, 625 rather than 316L is the answer and its cost multiplier is the price of a positive critical pitting temperature.

---

## Precipitation hardening stainless

Strength comparable to a low alloy steel with some corrosion resistance retained, at the cost of the FCC toughness.

| Alloy and condition | Fty [MPa] | Ftu [MPa] | K_Ic [MPa-sqrt(m)] | H2 notched ratio |
|---|---|---|---|---|
| **17-4PH H900** | 1170 | 1310 | 50 | **0.35** |
| **17-4PH H1025** | 1070 | 1140 | 80 | 0.62 |
| 15-5PH H1025 | 1069 | 1138 | 92 | 0.64 |

**H900 is the condition to avoid.** It is the strongest and it is the most hydrogen and stress corrosion susceptible, with a notched hydrogen ratio of 0.35. **H1025 and above should be what is specified**, trading 9 percent of the yield for 60 percent more toughness and a far better hydrogen response.

**15-5PH is 17-4PH with the delta ferrite removed** by rebalancing the chemistry, which gives markedly better transverse and short transverse toughness. Where a forging will be loaded across the grain, it is the better choice and the database carries short transverse allowables for it that 17-4PH does not have.

**The 3.5 percent copper is worth knowing about.** It is bound as precipitates inside a passivated matrix and 17-4PH is used in hydrazine service, unlike the copper-base alloys. Some programmes restrict it anyway, and it is worth checking rather than assuming.

---

## A286, the exception

Austenitic and precipitation hardened at the same time, which is unusual and useful.

| Property | Value |
|---|---|
| Yield strength | 655 MPa |
| Ultimate strength | 1000 MPa |
| Structure | **FCC** |
| Yield at 20 K | 1.42x room temperature |
| Toughness at 20 K | 0.88x room temperature |

**It keeps FCC toughness down to cryogenic temperature while reaching 655 MPa yield.** That combination makes A286 the default aerospace fastener alloy anywhere a bolt sees both cryogenic temperature and real preload, and it is non-magnetic into the bargain.

The price is cost, a 12 week lead time on bar, and a machinability that makes it unpopular in the shop.

---

## Low alloy steels

Present for solid motor cases, landing gear and pyrotechnic hardware, and as the cautionary example everywhere else.

| Alloy | Fty [MPa] | Ftu [MPa] | K_Ic at 293 K | K_Ic at 77 K | H2 ratio |
|---|---|---|---|---|---|
| **4340 QT260** | 1520 | 1793 | 50 | **6** | **0.18** |
| **300M QT280** | 1690 | 1965 | 60 | 6 | **0.15** |

**Two properties disqualify them from most launch vehicle use.**

**They are BCC.** 4340 keeps 122 percent of its room temperature yield strength at 77 K and 8 percent of its fracture toughness. Keeping the strength while losing the toughness is exactly what makes it dangerous, because a strength table alone reports it as a better material cold.

**They are severely hydrogen embrittled above about 1000 MPa ultimate.** A notched ratio of 0.18 means a notched bar retains 18 percent of its air strength in hydrogen. Any plating or acid pickling operation demands a bake per ASTM F1940, and any hydrogen exposure at all is disqualifying. See [HydrogenEmbrittlement.md](HydrogenEmbrittlement.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Austenitic for anything cryogenic | No DBTT, and it gains strength cold |
| 316L not 316 for anything welded | 18x the sensitization tolerance |
| 321 or 347 for welded hot gas | Stabilised against a second thermal cycle |
| 347 over 321 where a stress relief follows | NbC is more stable than TiC |
| PREN 26 means 316L pits at ambient | Passivation does not change that |
| H1025 not H900 for 17-4PH | 60 % more toughness for 9 % of the yield |
| 15-5PH where the load is transverse | Delta ferrite removed |
| A286 for cryogenic fasteners | FCC and 655 MPa at once |
| Never a martensitic grade below 200 K | The word stainless does not mean tough |
| Bake any plated part above 1000 MPa | ASTM F1940, 23 h at 190 degC |

---

## Failure modes

**A martensitic stainless used cold.** Brittle fracture with no deformation and no warning.

**316 used where 316L was meant.** Intergranular corrosion at the weld, invisible until it leaks.

**316L specified for splash zone hardware.** It pits, because its critical pitting temperature is below ambient.

**17-4PH H900 plated without a bake.** Delayed hydrogen fracture, typically days after assembly.

**A stainless fastener galling in a stainless boss.** Austenitic grades gall badly against themselves; plate or use a dissimilar pair.

**A sensitized weld passing inspection.** There is nothing to see. The control is procedural, through the grade and the heat input.

**4340 selected on its strength to cost ratio.** It is excellent, and the alloy is wrong for almost every launch vehicle application.

---

## Standards

| Standard | Scope |
|---|---|
| **MMPDS Chapter 2** | Steel and stainless allowables |
| ASTM A240 | Stainless sheet and plate |
| ASTM A276 | Stainless bar |
| ASTM A269 / A213 | Stainless tubing |
| **ASTM A564** | Age hardening stainless bar and shapes |
| AMS 5643 / 5659 | 17-4PH and 15-5PH bar |
| AMS 5731 / 5737 | A286 bar |
| **AMS 2700** | Passivation of corrosion resistant steels |
| **ASTM A380** | Cleaning, descaling and passivation of stainless |
| ASTM A262 | Detecting susceptibility to intergranular attack |
| ASTM F1940 | Process control for hydrogen embrittlement in plating |

---

## Tool interface

```python
from HeatTreatment import HeatTreatment
from CorrosionAssessment import CorrosionAssessment

# The sensitization argument, as a number
treatment = HeatTreatment()
treatment.setInputs({'material': '316L', 'condition': 'annealed'})
result = treatment.calculateSensitization(exposureTemperature = 948.0)
print(result['timeToSensitizeMinutes'], result['carbonAdvantage'])   # 360 min, 18.3x

# The pitting argument, as a number
corrosion = CorrosionAssessment()
corrosion.setInputs({'anodeMaterial': '316L', 'anodeCondition': 'annealed'})
print(corrosion.calculatePittingResistance())    # PREN 26.1, CPT -6 degC
```

---

## References

1. MMPDS-18, Chapter 2, *Steel*.
2. Sedriks, A. J., *Corrosion of Stainless Steels*, 2nd ed., Wiley, 1996.
3. ASM Handbook Volume 1, *Properties and Selection: Irons, Steels, and High-Performance Alloys*.
4. Reed, R. P. and Clark, A. F. (eds.), *Materials at Low Temperatures*, ASM, 1983.
5. Lula, R. A., *Stainless Steel*, ASM, 1986.
