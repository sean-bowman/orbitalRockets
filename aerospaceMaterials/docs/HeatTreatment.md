[Home](../README.md) > Heat Treatment

# Heat Treatment

## Contents

- [Overview](#overview)
- [The three operations](#the-three-operations)
- [Quench factor analysis](#quench-factor-analysis)
- [Hardenability and section size](#hardenability-and-section-size)
- [Aging and time-temperature equivalence](#aging-and-time-temperature-equivalence)
- [Sensitization](#sensitization)
- [Residual stress and distortion](#residual-stress-and-distortion)
- [Hot isostatic pressing](#hot-isostatic-pressing)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Heat treatment is not a schedule to be looked up. It is a set of competing rate processes, and the useful questions are all quantitative: how much strength does a slow quench cost, are these two aging cycles equivalent, how long can a weld sit in the sensitization range, and how far will the part bow when half the plate is machined away.

Every one of those has an answer, and getting it from a model rather than from a trial part is the point of this document.

---

## The three operations

**Solution treatment.** Heat until the alloying elements dissolve into a single phase. The temperature is bounded above by incipient melting and below by incomplete solution, and the window is often only 20 K wide.

**Quench.** Cool fast enough that the dissolved elements stay in solution rather than precipitating coarsely on the way down. **This is where the strength is won or lost**, and it is the step the section thickness controls.

**Age.** Reheat to a lower temperature so the supersaturated solute precipitates in a fine, controlled dispersion. Under-age and the precipitate is too sparse; over-age and it coarsens and loses coherency.

**Peak strength sits at the top of the aging curve, and it is often not where you want to be.** T73 deliberately overages past peak to buy stress corrosion resistance, trading 13 percent of the yield for a factor of five in SCC threshold.

---

## Quench factor analysis

The Staley formulation predicts retained strength directly from the cooling curve.

```
C_T = -k1 k2 exp( k3 k4^2 / (R T (k4 - T)^2) ) exp( k5 / (R T) )
Q   = integral dt / C_T(T)
sigma / sigma_max = exp(k1 Q)
```

`C_T` is the time to reach a defined fraction of transformation at temperature, so it traces the C-curve of the alloy. The integral accumulates the fraction of available transformation consumed on the way down, and the retained strength follows from it.

**The five constants are alloy specific and published for the common alloys.** They cannot be assumed, and the [`HeatTreatment`](../aerospaceMaterialsLibrary/HeatTreatment.py) class raises rather than substituting a default.

**What it answers** is the question a designer actually has: given this section and this quenchant, what fraction of the achievable strength does the part get?

---

## Hardenability and section size

7075-T73 in agitated water, computed:

| Section | Biot number | Cooling rate | Retained strength |
|---|---|---|---|
| 10 mm | 0.30 | 253 K/s | **98.4 %** |
| 25 mm | 0.75 | 101 K/s | 96.0 % |
| 50 mm | 1.50 | 51 K/s | 92.1 % |
| **100 mm** | 3.00 | 25 K/s | **84.8 %** |
| 150 mm | 4.50 | 17 K/s | 78.1 % |

**7075 cannot be through-hardened above about 75 mm**, and that is why 7050 exists. Higher copper and zirconium give it hardenability that lets a 150 mm plate develop properties through the thickness.

**The Biot number decides whether the section quenches uniformly at all:**

```
Bi = h L / k
```

Below 0.1 the part cools essentially uniformly. Above it the surface leads the core, which is what generates the residual stress that later causes distortion. A 25 mm aluminium section in agitated water sits at 0.75, so the gradient is real.

**Quench severity is tabulated in inverse inches** in almost every reference, and converting to base SI is a factor of 39.37. Using the tabulated numbers directly in an SI calculation gives a Biot number two orders of magnitude too small, which reports every quench as perfect. There is a test in this domain that exists because that mistake was made.

| Quenchant | H [1/in] | H [1/m] |
|---|---|---|
| Still air | 0.02 | 0.8 |
| Still oil | 0.25 | 10 |
| Still water | 1.00 | 40 |
| **Agitated water** | **1.50** | **59** |
| Agitated brine | 2.00 | 80 |

**Faster is not always better.** A more severe quench gives more strength and more residual stress, more distortion and more risk of quench cracking. Polymer quenchants exist to sit between oil and water for exactly this trade.

---

## Aging and time-temperature equivalence

```
P = T (C + log10 t)          T in kelvin, t in hours, C about 20
```

Two cycles with the same Larson-Miller parameter produce the same degree of precipitation. That makes time and temperature interchangeable within limits, which is how a 24 hour age gets compressed into 6 hours and how over-aging is predicted rather than discovered on a hardness check.

**The limit is that the mechanism has to stay the same.** Pushing the temperature far enough to cross a solvus or nucleate a different precipitate does not accelerate the same process; it substitutes another one. The equivalence is a tool within a mechanism, not across mechanisms.

**Natural aging complicates it.** Some alloys age measurably at room temperature, so the time between quench and artificial age is a process variable. For 2xxx alloys the delay before aging changes the final properties, and it is controlled in the process specification for that reason.

---

## Sensitization

Austenitic stainless held between roughly 700 and 1200 K precipitates chromium carbide at the grain boundaries, depleting the adjacent chromium below the 12 percent needed for passivity.

The time to the nose scales steeply with carbon content:

| Grade | Carbon | Time at 675 degC |
|---|---|---|
| 316 standard | 0.08 % | ~20 minutes |
| **316L** | 0.025 % | **~6 hours** |
| 321 (Ti stabilised) | 0.05 % | ~100 hours |
| 347 (Nb stabilised) | 0.05 % | ~150 hours |

**That factor of eighteen between 316 and 316L is why the L grades exist.** It is a computable number rather than a preference, and it is what makes a welded fluid system a 316L system.

**Stabilised grades go further.** Titanium or niobium ties the carbon into a stable carbide that does not dissolve and re-precipitate, so the grade survives a second thermal cycle. 347 is preferred over 321 where a stress relief follows the weld.

Once sensitized, a solution anneal is the only recovery, and on a large welded assembly that is usually impractical.

---

## Residual stress and distortion

A quench generates residual stress because the surface cools and contracts before the core does.

```
sigma_residual ~ beta E alpha dT_gradient / (1 - nu)
```

**The stress distribution is self-equilibrating**: compression at both surfaces balanced by tension in the core, with zero net force and zero net moment. That is what allows a quenched plate to sit flat.

**Machine one side away and the balance is destroyed.** The remaining section carries an unbalanced moment and the part bows:

```
curvature = M_unbalanced / (E I_remaining)
bow = curvature L^2 / 8
```

**Integrating the profile matters.** Treating the removed layer as carrying a uniform stress and multiplying by an arm length overstates the released moment by roughly a factor of four, because it ignores that the removed layer contains both the compressive surface and part of the tensile core. A parabolic profile is the standard idealisation and it satisfies both equilibrium conditions exactly.

**Bow scales with the square of the part length**, which is why a long thin machined part distorts and a short stubby one does not.

**The fixes, in order:**

| Fix | Effect |
|---|---|
| **Stress relieved temper (T351, T7451)** | Stretching relieves most of the quench stress. The primary fix |
| Symmetric machining | Removes equally from both faces, preserving the balance |
| Rough, stress relieve, finish | Two setups, and it works |
| Alternating passes | Partial, and it is what most shops do |

---

## Hot isostatic pressing

HIP closes internal porosity by creep under pressure. It belongs with heat treatment rather than with surface processing because it is a thermal cycle at pressure and it interacts directly with the solution and aging steps.

| Alloy family | Temperature | Pressure | Time | What must follow |
|---|---|---|---|---|
| Nickel PH (718) | 1163 degC | 100 MPa | 4 h | **Solution treat and age.** The cycle is above the gamma prime solvus |
| Nickel solid solution | 1120 degC | 100 MPa | 4 h | Nothing |
| **Titanium alpha-beta** | 920 degC | 100 MPa | 2 h | Below the beta transus, or the alpha coarsens |
| Aluminium additive | 520 degC | 100 MPa | 2 h | Coarsens the silicon network; use only when porosity governs |
| Austenitic stainless | 1120 degC | 100 MPa | 4 h | Solution anneal, to redissolve carbides from the slow cool |

**A part HIPed and not re-treated is in an unknown condition**, and none of the allowables in any database apply to it. This is a recurring error on additive parts, where HIP is treated as a porosity fix rather than as a heat treatment.

**HIP is what makes additive fatigue properties acceptable.** As-built porosity dominates fatigue crack initiation, and closing it moves the additive knockdown from about 25 percent to about 5 percent.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| The quench is where the strength is won or lost | Not the age |
| 7075 cannot be through-hardened above 75 mm | 7050 exists for this |
| Biot number above 0.1 means a real gradient | And therefore residual stress |
| Quench severity is tabulated in inverse inches | Convert by 39.37 |
| Faster quench, more distortion and cracking risk | Polymer quenchants split the difference |
| Larson-Miller equivalence within a mechanism only | Not across a solvus |
| 316L tolerates 18x the sensitization exposure of 316 | The reason the L grades exist |
| Stress relieved tempers for thick machined parts | T351, T7451 |
| Bow scales with length squared | Long thin parts distort |
| HIP above a solvus needs a re-treat | Or the part is soft |

---

## Failure modes

**A thick section quenched and found soft in the core.** Hardenability exceeded. The alloy is wrong for the section.

**A machined plate part bowing millimetres.** Quench residual stress released asymmetrically.

**Quench cracking in a thick section.** Too severe a quench for the geometry.

**A sensitized weld.** Nothing to see, and it corrodes intergranularly in service.

**An additive part HIPed and not re-solutioned.** Soft and outside every allowable.

**Titanium HIPed above the beta transus.** Lamellar alpha and a large fatigue debit.

**A compressed aging cycle that crossed a solvus.** A different precipitate and different properties.

**Aging delayed after quench on a 2xxx alloy.** Natural aging changes the final result.

---

## Standards

| Standard | Scope |
|---|---|
| **AMS 2770** | Heat treatment of wrought aluminium alloy parts |
| AMS 2772 | Heat treatment of aluminium alloy raw materials |
| **AMS 2759** | Heat treatment of steel parts, general |
| AMS 2759/9 | Hydrogen embrittlement relief baking |
| **AMS 2801** | Heat treatment of titanium alloy parts |
| AMS 2774 | Heat treatment of wrought nickel and cobalt alloy parts |
| **AMS 2750** | Pyrometry. The furnace control specification everything else depends on |
| ASTM A262 | Detecting susceptibility to intergranular attack in austenitic stainless |
| ASTM E112 | Determining average grain size |
| **ASTM A1080** | Hot isostatic pressing of steel, stainless and related alloys |
| NASA-STD-6030 | Additive manufacturing requirements, including HIP |

---

## Tool interface

```python
from HeatTreatment import HeatTreatment

treatment = HeatTreatment()
treatment.setInputs({'material': '7075', 'condition': 't73',
                     'sectionThickness': 0.050, 'partLength': 0.500, 'partWidth': 0.200,
                     'quenchant': 'agitated water', 'machinedFraction': 0.50,
                     'agingTemperature': 393.0, 'agingTime': 86400.0})

treatment.modelCoolingCurve()          # and the Biot number check
treatment.calculateQuenchFactor()      # Staley integral, retained strength
treatment.calculateAgingResponse(comparisonTemperature = 413.0)   # equivalence
treatment.calculateDistortion()        # residual stress and the bow released
treatment.calculateHipCycle()          # and what must follow it
print(treatment.generateReport())
```

Lookup tables: `HeatTreatment.QUENCH_SEVERITY`, `HeatTreatment.HIP_CYCLES`.

---

## References

1. Staley, J. T., "Quench Factor Analysis of Aluminum Alloys", *Materials Science and Technology*, Vol. 3, 1987.
2. Totten, G. E. and MacKenzie, D. S. (eds.), *Handbook of Aluminum*, Marcel Dekker, 2003.
3. ASM Handbook Volume 4, *Heat Treating*.
4. Larson, F. R. and Miller, J., "A Time-Temperature Relationship for Rupture and Creep Stresses", *Transactions of the ASME*, Vol. 74, 1952.
5. Atkins, H. and Robinson, J. S., "Residual Stresses in Quenched Aluminium Alloy Plate", *Materials Science Forum*, 2011.
