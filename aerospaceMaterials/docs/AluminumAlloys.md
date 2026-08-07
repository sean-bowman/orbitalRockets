[Home](../README.md) > Aluminium Alloys

# Aluminium Alloys

## Contents

- [Overview](#overview)
- [The families](#the-families)
- [Tempers](#tempers)
- [Weldability, and what it costs](#weldability-and-what-it-costs)
- [Stress corrosion and the short transverse direction](#stress-corrosion-and-the-short-transverse-direction)
- [Cryogenic behaviour](#cryogenic-behaviour)
- [Aluminium-lithium](#aluminium-lithium)
- [Additive aluminium](#additive-aluminium)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Aluminium is the launch vehicle structural default and every alloy in the family has a catch. 2219 is weldable and LOX compatible but not strong. 7075 is strong but neither weldable nor stress corrosion resistant. 2195 is both strong and weldable and costs several times as much with a supply chain measured in months.

Choosing between them is almost always a trade between strength, weldability and stress corrosion resistance, and it is rarely possible to have all three.

---

## The families

| Alloy | Fty typ [MPa] | Ftu typ [MPa] | rho [kg/m3] | Weldable | Where it belongs |
|---|---|---|---|---|---|
| **2219-T87** | 393 | 476 | 2840 | **Yes** | Cryogenic tanks, LOX compatible |
| **2195-T8 (Al-Li)** | 545 | 580 | 2710 | Yes | Lightweight cryogenic tanks |
| 2024-T3 | 345 | 483 | 2780 | No | Airframe. Poor launch vehicle choice |
| **6061-T6** | 276 | 310 | 2700 | Yes | General structure, brackets, lines |
| **7075-T73** | 435 | 505 | 2810 | **No** | Machined fittings, manifold bodies |
| 7075-T6 | 503 | 572 | 2810 | No | Higher strength, poor SCC resistance |
| 7050-T7451 | 455 | 524 | 2830 | No | Thick machined bulkheads and fittings |
| AlSi10Mg (LPBF) | 250 | 420 | 2670 | n/a | Additive brackets and manifolds |

**2219 is the cryogenic tank alloy** because it is the only one that combines weldability, toughness at LH2 temperature and LOX compatibility. The Shuttle external tank was 2219 before it was 2195. Its modest strength is what it pays for that combination.

**7050 exists because 7075 cannot be through-hardened in thick sections.** Higher copper and zirconium give it far better hardenability, so a 150 mm plate develops properties through the thickness that 7075 cannot. See [HeatTreatment.md](HeatTreatment.md).

---

## Tempers

The temper designation carries more information than the alloy number, and reading it correctly is most of the skill.

| Temper | Meaning |
|---|---|
| **O** | Annealed, softest |
| **T3** | Solution treated, cold worked, naturally aged |
| **T6** | Solution treated, artificially aged to **peak strength** |
| **T73** | Solution treated, **overaged** for stress corrosion resistance |
| **T7451** | Overaged, stress relieved by controlled stretching |
| **T87** | Solution treated, cold worked 7 %, artificially aged |
| **T351** | Solution treated, stress relieved by stretching, naturally aged |

**T6 versus T73 is the trade that matters.** T73 deliberately overages past peak strength, losing about 13 percent of the yield, and buys a factor of five in stress corrosion threshold. On any part carrying a sustained short transverse tensile stress, that is not a close call.

**The 51 suffix means stress relieved by stretching**, and it is what stops a thick machined plate part from bowing when material is removed asymmetrically. It is not a nicety; the bow is millimetres.

---

## Weldability, and what it costs

**6061-T6 loses roughly half its yield strength in the weld heat affected zone**, and it does not recover without a full solution treat and age that will distort the part.

| Alloy | As-welded yield ratio | Recoverable |
|---|---|---|
| **6061-T6** | **0.50** | Only by full solution treat and age |
| 2219-T87 | 0.42 | Yes, and it is routinely done on tanks |
| **7075-T73** | **not weldable** | Severe hot cracking, no recovery |

**Never size an aluminium weldment on parent metal properties.** This is the single most common aluminium design error and the numbers above are why.

**Friction stir welding changes the calculation.** No melting means no solidification cracking, so it can join alloys that fusion welding cannot, and the knockdown is around 0.80 rather than 0.50 because the nugget is recrystallised rather than resolutionised. It is the standard process for aluminium tank barrels for exactly these reasons.

The weld side of this is covered in [fluidSystems Welds.md](../../fluidSystems/fluidSystemsLibrary/docs/Welds.md).

---

## Stress corrosion and the short transverse direction

**7xxx alloys crack under sustained tension in the short transverse direction, in ordinary humid air.**

| Alloy and temper | SCC threshold, salt fog [MPa] | ST rating |
|---|---|---|
| **7075-T6** | **50** | very low |
| 7075-T73 | 240 | moderate |
| 7050-T7451 | 240 | moderate |
| 2219-T87 | 275 | high |
| 6061-T6 | 200 | high |

**Fifty MPa is a stress nobody thinks twice about.** It is well below yield, well below any design allowable, and it is reached by an interference fit, a mis-shimmed joint, or a bolt torqued to specification through a thick plate. The [`CorrosionAssessment`](../aerospaceMaterialsLibrary/CorrosionAssessment.py) class raises rather than warns on this combination.

**Short transverse is the through-thickness direction of a rolled or forged product.** Grain flow runs longitudinally, so the grain boundaries present themselves broadside to a short transverse stress, and that is the crack path.

**The fix is the temper, not the design.** T73 or T7451 rather than T6, and the mass penalty is around 13 percent of the yield strength.

---

## Cryogenic behaviour

Aluminium is face-centred cubic, so it has **no ductile-to-brittle transition** and stays tough to liquid hydrogen temperature. That is why aluminium and austenitic stainless dominate cryogenic tankage and why steel does not.

| Property at 20 K, as a ratio to 293 K | 2219-T87 | 6061-T6 | 7075-T73 |
|---|---|---|---|
| Yield strength | 1.34 | 1.25 | 1.22 |
| Ultimate strength | 1.48 | 1.42 | 1.30 |
| Elastic modulus | 1.12 | 1.12 | 1.11 |
| **Fracture toughness** | **1.15** | 1.12 | 1.10 |

**Toughness rises rather than falls**, which is the opposite of what happens to any BCC alloy and is the whole reason the family is used cold. Compare 4340, which retains 8 percent of its room temperature toughness at 20 K.

Thermal contraction from 293 K to 20 K is roughly 0.4 percent, which matters for joint design and is covered in [fluidSystems CryogenicSystems.md](../../fluidSystems/fluidSystemsLibrary/docs/CryogenicSystems.md).

---

## Aluminium-lithium

Lithium is the only alloying element that **lowers density and raises modulus at the same time**. Every other addition trades one against the other.

| Property | 2219-T87 | 2195-T8 | Change |
|---|---|---|---|
| Density [kg/m3] | 2840 | 2710 | **-4.6 %** |
| Elastic modulus [GPa] | 73.1 | 76.5 | **+4.7 %** |
| Yield strength [MPa] | 393 | 545 | +39 % |

The Shuttle super lightweight tank saved 3400 kg by changing from 2219 to 2195, and that saving went directly to payload.

**The catches are real.** Few mills produce it, lead times run to 32 weeks against 18 for 2219, cost is roughly three times, and the anisotropy is pronounced: the short transverse allowable sits 13 percent below the longitudinal against 4 percent for 2219. A designer who ignores grain direction will find the difference in service.

---

## Additive aluminium

**AlSi10Mg is the default LPBF aluminium**, and it is a casting alloy rather than a wrought one. The rapid solidification produces a fine cellular silicon network that gives as-built properties above cast and approaching 6061-T6.

| Condition | Fty [MPa] | Ftu [MPa] | Elongation |
|---|---|---|---|
| LPBF as-built | 250 | 420 | 6 % |
| LPBF stress relieved | 200 | 320 | 10 % |

**Stress relief costs 20 percent of the yield** because it coarsens the silicon network that produced the strength. That is an unusual and important trade: the thermal treatment that makes the part dimensionally stable is the one that makes it weaker.

**Anisotropy is real**: Z direction properties run 5 to 15 percent below XY, and elongation is worse than strength. The database carries the ratios, and none of the LPBF aluminium data in it is traceable to a statistical basis. It is marked `estimate` for that reason.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Never size an aluminium weldment on parent properties | 6061-T6 loses half its yield in the HAZ |
| T73 rather than T6 for any sustained ST stress | 50 MPa cracks 7075-T6 in humid air |
| 51 suffix tempers for thick machined parts | Stress relieved by stretching; stops the bow |
| 2219 for weldable cryogenic and LOX service | The only alloy with all three |
| 7050 rather than 7075 above 75 mm | 7075 cannot be through-hardened |
| Al-Li for mass-critical tanks, if the schedule allows | 32 week lead time |
| Aluminium gains toughness cold | Unlike every BCC alloy |
| Check the short transverse allowable | It is the lowest and the least often quoted |

---

## Failure modes

**Weldment sized on parent metal.** Undersized by half.

**7075-T6 in sustained short transverse tension.** Cracks in ordinary humid air.

**A thick machined plate part bowing after machining.** Quench residual stress released asymmetrically. The fix is a stress relieved temper.

**7075 specified for a welded assembly.** It is not weldable; hot cracking with no strength recovery.

**2024 chosen for its fatigue reputation.** It is not weldable, corrodes readily unless clad, and its LOX compatibility is not established.

**Al-Li specified without checking lead time.** The design freezes and the material arrives eight months later.

**LPBF aluminium allowables taken from a vendor datasheet.** They are typical values from one machine and one parameter set.

---

## Standards

| Standard | Scope |
|---|---|
| **MMPDS Chapter 3** | Aluminium alloy allowables |
| AMS 4027 / 4031 / 4037 | Sheet and plate specifications by alloy |
| AMS-QQ-A-250 | Aluminium plate and sheet, general |
| **ASTM B209** | Aluminium sheet and plate |
| ASTM B221 | Aluminium extruded bar, rod and shapes |
| AMS 2770 | Heat treatment of wrought aluminium alloy parts |
| **AMS 2772** | Heat treatment of aluminium alloy raw materials |
| ASTM G47 | Determining susceptibility to SCC of 2xxx and 7xxx alloys |
| ASTM F3318 | LPBF AlSi10Mg |

---

## Tool interface

```python
from MaterialDatabase import queryMaterial
from HeatTreatment import HeatTreatment

# The weld knockdown, as a separate condition rather than a factor applied by hand
parent   = queryMaterial('6061', 't6',        293.15)
asWelded = queryMaterial('6061', 'as-welded', 293.15)
print(asWelded['yieldStrength'] / parent['yieldStrength'])     # 0.50

# Whether a section can be through-hardened
treatment = HeatTreatment()
treatment.setInputs({'material': '7075', 'condition': 't73',
                     'sectionThickness': 0.100, 'quenchant': 'agitated water'})
treatment.modelCoolingCurve()
print(treatment.calculateQuenchFactor()['retainedStrengthFraction'])    # 0.848
```

---

## References

1. MMPDS-18, Chapter 3, *Aluminum*.
2. Polmear, I. et al., *Light Alloys*, 5th ed., Butterworth-Heinemann, 2017.
3. Starke, E. A. and Staley, J. T., "Application of Modern Aluminum Alloys to Aircraft", *Progress in Aerospace Sciences*, Vol. 32, 1996.
4. Rioja, R. J. and Liu, J., "The Evolution of Al-Li Base Products for Aerospace and Space Applications", *Metallurgical and Materials Transactions A*, Vol. 43, 2012.
5. ASM Handbook Volume 2, *Properties and Selection: Nonferrous Alloys*.
