[Home](../README.md) > Cryogenic Materials

# Cryogenic Materials

## Contents

- [Overview](#overview)
- [The lattice rule](#the-lattice-rule)
- [Strength against temperature](#strength-against-temperature)
- [Toughness against temperature](#toughness-against-temperature)
- [Thermal contraction](#thermal-contraction)
- [Thermal conductivity](#thermal-conductivity)
- [Specific heat and the chilldown consequence](#specific-heat-and-the-chilldown-consequence)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

This document carries the numbers: property against temperature for the alloys that matter, from 20 K to ambient.

The system-level cryogenic story, chilldown, two-phase flow, geysering, insulation and the operational hazards, is in [fluidSystems CryogenicSystems.md](../../fluidSystems/fluidSystemsLibrary/docs/CryogenicSystems.md), which also carries the qualitative material behaviour table. What is here is the quantitative side and the curves the [`MaterialDatabase`](../aerospaceMaterialsLibrary/MaterialDatabase.py) interpolates.

---

## The lattice rule

**Face-centred cubic alloys have no ductile-to-brittle transition. Body-centred cubic alloys do.** That single distinction decides whether a material can be used cold at all, and it is not negotiable by heat treatment or by alloying within a family.

| Structure | Alloys | Cold behaviour |
|---|---|---|
| **FCC** | Austenitic stainless, all aluminium, nickel alloys, copper | **Ductile to 4 K**, and stronger |
| **HCP** | Titanium alloys | Usable, with reduced ductility |
| **BCC** | Ferritic and martensitic steel, PH stainless | **Brittle below the transition** |

**The one BCC exception worth knowing is 9 percent nickel steel**, which is used for LNG tankage to 77 K. Nickel suppresses the transition far enough to be usable, and it is the reason that particular alloy exists.

---

## Strength against temperature

Ratios to the room temperature value. These are the curves stored in the database.

| Alloy | 20 K | 77 K | 200 K | 293 K |
|---|---|---|---|---|
| **304L yield** | **2.60** | 2.50 | 1.55 | 1.00 |
| **316L yield** | **2.50** | 2.40 | 1.52 | 1.00 |
| 321 yield | 2.40 | 2.30 | 1.50 | 1.00 |
| A286 yield | 1.42 | 1.38 | 1.14 | 1.00 |
| Monel 400 yield | 1.55 | 1.50 | 1.16 | 1.00 |
| **Ti-6Al-4V yield** | 1.55 | 1.48 | 1.18 | 1.00 |
| Inconel 718 yield | 1.18 | 1.15 | 1.06 | 1.00 |
| **2219-T87 yield** | 1.34 | 1.28 | 1.09 | 1.00 |
| 6061-T6 yield | 1.25 | 1.21 | 1.06 | 1.00 |
| 7075-T73 yield | 1.22 | 1.18 | 1.06 | 1.00 |

**The austenitic stainless gain is dramatic and real.** 316L roughly doubles its yield strength by 77 K, driven by strain-induced martensite formation as much as by lattice friction. A stainless cryogenic line is not as heavy as its room temperature properties suggest.

**Aluminium gains 22 to 34 percent**, which is useful and rarely designed for because ambient handling loads often govern.

**Do not design to the cryogenic strength without checking the ambient case.** A tank is proof tested warm, handled warm and often pressurised warm, and the ambient condition frequently governs even though the service is cold.

---

## Toughness against temperature

This is where the lattice rule shows itself, and the contrast is stark.

| Alloy | Structure | K_Ic ratio at 20 K | at 77 K |
|---|---|---|---|
| 316L | FCC | 0.86 | 0.89 |
| **2219-T87** | FCC | **1.15** | 1.12 |
| Ti-6Al-4V | HCP+BCC | 0.72 | 0.75 |
| **Ti-6Al-4V ELI** | HCP+BCC | **0.84** | 0.86 |
| Inconel 718 | FCC | 0.82 | 0.86 |
| **17-4PH H1025** | **BCC** | -- | **0.25** |
| **4340 QT260** | **BCC** | **0.08** | **0.12** |

**4340 retains 8 percent of its room temperature fracture toughness at 20 K while keeping 122 percent of its yield strength.** Keeping the strength and losing the toughness is exactly what makes a BCC alloy dangerous cold: a strength table reports it as a better material, and the fracture behaviour is catastrophic.

**Aluminium toughness actually rises**, which is unusual and helpful.

**ELI titanium retains far more toughness than grade 5**, which is the entire reason the grade exists and why it is specified for cryogenic pressure vessels.

---

## Thermal contraction

Integrated contraction from 293 K, as a percentage of length. These are what set joint gaps, seal squeeze and support strut lengths.

| Material | to 77 K | to 20 K |
|---|---|---|
| **PTFE** | **1.94 %** | 2.14 % |
| Silicone | 1.60 % | 1.75 % |
| Aluminium 6061 | 0.39 % | 0.41 % |
| Copper | 0.30 % | 0.32 % |
| **316L** | **0.29 %** | 0.30 % |
| Inconel 718 | 0.24 % | 0.25 % |
| Titanium | 0.15 % | 0.17 % |
| **G-10, warp direction** | 0.21 % | 0.24 % |
| Invar | 0.04 % | 0.04 % |

**PTFE contracts six and a half times as much as the stainless around it.** On a 20 mm gland that differential is roughly 0.33 mm, which is several times the squeeze on a small cross section. **A PTFE seal that had adequate compression at ambient has none at 77 K**, and this is the dominant cryogenic seal failure mechanism.

**Invar exists for this reason** and it is what optical benches and precision structures are made from when contraction has to be near zero.

---

## Thermal conductivity

Ratios to the room temperature value, which is where the insulation and heat leak calculations start.

| Alloy | 20 K | 77 K | 293 K |
|---|---|---|---|
| **316L** | **0.12** | 0.49 | 1.00 |
| 6061-T6 | 0.55 | 0.72 | 1.00 |
| Inconel 718 | 0.13 | 0.45 | 1.00 |
| Ti-6Al-4V | 0.28 | 0.37 | 1.00 |
| G-10 | ~0.30 | ~0.55 | 1.00 |

**Stainless conductivity collapses to 12 percent at 20 K.** That is helpful for a support strut and unhelpful for anything that has to conduct, and it is why a cryogenic system's heat leak analysis cannot use room temperature conductivity.

**Aluminium falls much less**, which makes an aluminium bracket a far better heat leak path than a stainless one, in both directions.

---

## Specific heat and the chilldown consequence

**Specific heat falls dramatically at low temperature**, approaching zero as the Debye model predicts. At 20 K a metal has a few percent of its room temperature heat capacity.

The practical consequence appears during chilldown: **the last part of the cooldown is fast because there is almost no thermal mass left**, while the first part is slow. A chilldown estimate made with room temperature properties over-predicts the propellant consumed at the cold end and under-predicts it at the warm end.

It also means a cold component warms up very quickly once flow stops, which is why a chilled line that sits idle for a minute has to be re-chilled.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| FCC for anything below 200 K | No transition, and it gains strength |
| Never BCC below its transition | 4340 keeps 8 % of its toughness at 20 K |
| Austenitic stainless doubles its yield by 77 K | Real, and rarely designed for |
| Check the ambient case as well | Proof, handling and ground pressurisation are warm |
| PTFE contracts 6.5x more than stainless | The dominant cryogenic seal failure |
| ELI titanium for cryogenic pressure vessels | Far better retained toughness |
| Stainless conductivity is 12 % at 20 K | Heat leak analysis cannot use ambient values |
| Specific heat approaches zero | The cold end of chilldown is fast |
| 9 % nickel steel is the BCC exception | To 77 K, and it is why it exists |

---

## Failure modes

**A BCC alloy used below its transition.** Brittle fracture, no deformation, no warning.

**A PTFE or elastomer seal that passed an ambient leak check.** Contraction opens the gland cold.

**A heat leak analysis done with room temperature conductivity.** Wrong by a factor of eight for stainless.

**Designing to cryogenic strength and failing the ambient proof test.** The warm case governs more often than expected.

**A cryogenic joint qualified only at ambient.** The failure mechanism is differential contraction and it does not exist warm.

**Grade 5 titanium where ELI was needed.** Lower toughness in the condition where toughness governs.

---

## Standards

| Standard | Scope |
|---|---|
| **NIST Cryogenic Material Properties Database** | The primary low temperature property source |
| ASTM E1450 | Tension testing of structural alloys in liquid helium |
| ASTM E1820 | Fracture toughness measurement |
| **CGA P-12** | Safe handling of cryogenic liquids |
| ISO 21010 | Cryogenic vessels, gas and materials compatibility |
| ASTM C1774 | Thermal performance testing of cryogenic insulation |
| **NASA-STD-8719.17** | Ground-based pressure vessels and pressurized systems |
| ASME BPVC Section VIII Division 1 UHA-51 | Impact testing requirements for low temperature service |

---

## Tool interface

```python
import numpy as np
from MaterialDatabase import MaterialDatabase

database = MaterialDatabase()
database.setInputs({'material': '316L', 'condition': 'annealed'})

temperatures = np.array([20.0, 77.0, 200.0, 293.15])
print(database.getTemperatureCurve('yieldStrength',       temperatures) / 1.0e6)
print(database.getTemperatureCurve('thermalConductivity', temperatures))

# Toughness is corrected by the same mechanism, and the BCC collapse is visible in the data
for material, condition in (('316L', 'annealed'), ('4340', 'qt-260')):
    for temperature in (293.15, 77.0):
        query = MaterialDatabase()
        query.setInputs({'material': material, 'condition': condition,
                         'temperature': temperature})
        print(material, temperature,
              query.getFractureData()['planeStrainToughness'])
```

---

## References

1. NIST, *Cryogenic Material Properties Database*, https://trc.nist.gov/cryogenics/.
2. Reed, R. P. and Clark, A. F. (eds.), *Materials at Low Temperatures*, ASM, 1983.
3. Barron, R. F., *Cryogenic Systems*, 2nd ed., Oxford University Press, 1985.
4. Ekin, J. W., *Experimental Techniques for Low-Temperature Measurements*, Oxford, 2006.
5. Flynn, T. M., *Cryogenic Engineering*, 2nd ed., Marcel Dekker, 2004.
