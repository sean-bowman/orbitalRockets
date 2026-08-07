[Home](../README.md) > Temper Designations

# Temper Designations

## Contents

- [Overview](#overview)
- [The aluminium system](#the-aluminium-system)
- [The T tempers](#the-t-tempers)
- [The H tempers](#the-h-tempers)
- [Why overaged tempers exist](#why-overaged-tempers-exist)
- [Other families](#other-families)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

The temper designation carries more engineering information than the alloy number does. Two parts in the same alloy with different tempers can differ by 15 percent in strength, by a factor in stress corrosion resistance, and by a factor of four in formability.

---

## The aluminium system

Per ANSI H35.1:

| Designation | Meaning |
|---|---|
| **F** | As fabricated. No property guarantee |
| **O** | **Annealed.** The softest and most formable condition |
| **H** | **Strain hardened.** Non heat treatable alloys |
| W | Solution treated, unstable. A transient condition |
| **T** | **Thermally treated to a stable condition** |

**The W condition is a real designation and it is a transient one.** A solution treated alloy is soft and formable for a limited time before natural ageing hardens it, and forming in the W condition, then ageing, is a genuine production route. Refrigeration extends the window.

---

## The T tempers

| Temper | Meaning |
|---|---|
| **T3** | Solution treated, **cold worked**, naturally aged |
| **T4** | Solution treated, naturally aged |
| **T6** | Solution treated, **artificially aged to peak strength** |
| **T7** | Solution treated, **overaged** past peak |
| **T73** | Overaged for **stress corrosion resistance** |
| **T76** | Overaged for **exfoliation resistance**, between T6 and T73 |
| **T8** | Solution treated, cold worked, artificially aged |
| T87 | T8 with a specific 7 % cold work |

**Additional digits carry the stress relief:**

| Suffix | Meaning |
|---|---|
| **51** | **Stress relieved by stretching** |
| 52 | Stress relieved by compressing |
| 54 | Stress relieved by combined stretch and compress |

**7050-T7451 is therefore: solution treated, overaged for SCC resistance, and stress relieved by stretching.** That last part is what makes it the right choice for a large machined part, because the quench stress that would otherwise distort the part on machining has been removed. See [machiningProcesses DistortionControl.md](../../machiningProcesses/docs/DistortionControl.md).

**T87 is why 2219 is a tank alloy.** The 7 percent cold work before ageing gives a fine uniform precipitate distribution, and the result is good strength, good toughness, good weldability and good cryogenic behaviour.

---

## The H tempers

**For work hardened, non heat treatable alloys: the 1000, 3000 and 5000 series.**

| First digit | Meaning |
|---|---|
| **H1** | Strain hardened only |
| **H2** | Strain hardened and partially annealed |
| **H3** | Strain hardened and stabilised |

**The second digit is the degree of hardening**, in eighths of the way from annealed to full hard:

| Digit | Condition |
|---|---|
| 2 | Quarter hard |
| **4** | **Half hard** |
| 6 | Three quarter hard |
| 8 | **Full hard** |

**H32, H34, H36 and H38 in 5083 and 5052** are the common structural ones, and each step trades formability for strength.

**H3 stabilisation matters for magnesium bearing alloys.** 5000 series alloys with more than about 3 percent magnesium age soften and become sensitized to intergranular corrosion at slightly elevated temperature; the stabilisation treatment prevents it.

---

## Why overaged tempers exist

**They give away strength and buy stress corrosion resistance, and the trade is nearly always correct.**

| Temper | Relative strength | ST SCC resistance |
|---|---|---|
| **T6** | 1.00 | **Poor** |
| T76 | 0.93 | Moderate |
| **T73** | **0.85** | **Good** |

**Ageing past peak coarsens the grain boundary precipitates** and changes the boundary chemistry, which interrupts the anodic dissolution path that stress corrosion follows.

**A 15 percent strength reduction for a large multiple of the SCC threshold** is a trade almost any structural application should take, and 7075-T6 survives mainly in applications with no sustained tension in the short transverse direction.

**T76 is the compromise** and it targets exfoliation corrosion specifically, which is the surface-layered attack that thin 7000 series sections suffer.

---

## Other families

| Family | System |
|---|---|
| **Stainless** | Condition A (annealed), and H-numbers for PH grades: H900, H1025, H1150 |
| **Nickel** | Annealed, solution treated, STA (solution treated and aged) |
| **Titanium** | Annealed, STA, beta annealed, mill annealed |
| Steel | Normalised, quenched and tempered, with a hardness or strength callout |

**PH stainless H-numbers are the ageing temperature in Fahrenheit.** H900 is aged at 900 degF and is strongest; H1150 is aged at 1150 degF and is toughest and most SCC resistant. The same overageing trade as aluminium, expressed differently.

**Titanium mill annealed and beta annealed differ substantially** in toughness and in fatigue, and the specification has to say which.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| The temper carries more information than the alloy | |
| O for forming, T for service | Form annealed, heat treat after |
| T73 for SCC resistance | At ~15 % strength |
| The 51 suffix is stress relief by stretching | Specify it for large machined parts |
| T87 for 2219 tanks | Cold work before ageing |
| H second digit is eighths | H38 is full hard |
| PH H-numbers are degF | H900 strongest, H1150 toughest |

---

## Failure modes

**Temper omitted from the callout.** The property is undefined.

**T6 substituted for T73 to gain strength.** SCC resistance lost.

**Non-stress-relieved plate for a large machined part.** Distortion.

**Formed in T6.** A quarter of the formability.

**H-temper alloy specified with a T temper.** It is not heat treatable.

**Titanium annealed condition unspecified.** Mill and beta annealed differ substantially.

---

## Standards

| Standard | Scope |
|---|---|
| **ANSI H35.1** | Alloy and temper designation systems for aluminium |
| ASTM B918 | Heat treatment of wrought aluminium alloys |
| **AMS 2770** | Heat treatment of wrought aluminium alloy parts |
| AMS 2759 | Heat treatment of steel parts |
| AMS 2801 | Heat treatment of titanium alloy parts |
| AMS 5643 etc. | 17-4PH by condition |

---

## References

1. ANSI H35.1, *Alloy and Temper Designation Systems for Aluminum*.
2. MMPDS-2023, *Metallic Materials Properties Development and Standardization*.
3. ASM Handbook Volume 4, *Heat Treating*.
