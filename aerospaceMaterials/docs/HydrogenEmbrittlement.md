[Home](../README.md) > Hydrogen Embrittlement

# Hydrogen Embrittlement

## Contents

- [Overview](#overview)
- [The three mechanisms](#the-three-mechanisms)
- [What makes a material susceptible](#what-makes-a-material-susceptible)
- [The susceptibility ranking](#the-susceptibility-ranking)
- [The temperature surprise](#the-temperature-surprise)
- [Where the hydrogen comes from](#where-the-hydrogen-comes-from)
- [Bake-out](#bake-out)
- [Design practice](#design-practice)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Hydrogen embrittlement is the reduction of ductility and fracture resistance caused by atomic hydrogen dissolved in a metal. It produces **delayed brittle fracture at stresses far below yield**, typically hours to days after loading, in a material that tested perfectly.

It matters on a launch vehicle for two separate reasons: hydrogen is a propellant, and electroplating puts hydrogen into steel parts that never go near the propellant.

---

## The three mechanisms

They are not alternatives; all three operate and the dominant one depends on the material and the stress state.

**Hydrogen enhanced decohesion (HEDE).** Dissolved hydrogen reduces the cohesive strength of the lattice and of grain boundaries directly. The fracture is intergranular and it is the dominant mechanism in high strength steels.

**Hydrogen enhanced localised plasticity (HELP).** Hydrogen increases dislocation mobility locally, concentrating plastic flow into narrow bands. The macroscopic result is brittle, the microscopic mechanism is enhanced plasticity, and the fracture surface shows fine dimples on what looks like a cleavage plane.

**Hydride formation.** In titanium, zirconium and vanadium, hydrogen forms a genuine brittle hydride phase. This is a distinct mechanism with a distinct remedy, and it is why titanium is not a high pressure gaseous hydrogen material despite being otherwise excellent.

---

## What makes a material susceptible

Three factors, and they compound.

**Crystal structure.** BCC lattices have high hydrogen diffusivity and low solubility, which delivers hydrogen quickly to traps and crack tips without providing anywhere benign to store it. FCC is the reverse: high solubility, low diffusivity, so hydrogen dissolves harmlessly and moves slowly.

| Structure | Relative risk |
|---|---|
| **BCC, martensitic** | 1.00 |
| HCP + BCC (titanium) | 0.60 |
| HCP | 0.50 |
| **FCC austenitic** | 0.15 |

**This is the same lattice property that governs the ductile to brittle transition**, seen from a different direction. It is not a coincidence.

**Strength level.** Susceptibility rises steeply above about 1000 MPa ultimate tensile strength, which is where the ASTM F1940 bake trigger sits. Below roughly 1000 MPa most steels are usable; above 1400 MPa almost none are.

**Stress state.** Triaxial tension at a notch or a crack tip draws hydrogen in by dilatation. A smooth bar tolerates hydrogen far better than a notched one, which is why the notched tensile ratio is the standard measure rather than the smooth one.

---

## The susceptibility ranking

The notched tensile ratio is the strength in hydrogen divided by the strength in helium, measured on a notched bar. It is the direct experimental measure.

| Material | Notched ratio | Assessment |
|---|---|---|
| **300M, 1965 MPa** | **0.15** | Severe. Disqualified from hydrogen service |
| **4340, 1793 MPa** | **0.18** | Severe |
| **17-4PH H900** | **0.35** | Severe |
| **Inconel 718 STA** | **0.55** | Moderate. Usable with care |
| 17-4PH H1025 | 0.62 | Moderate |
| Monel K-500 | 0.72 | Moderate |
| **Ti-6Al-4V** | 0.75 | Moderate, and hydride formation is a separate concern |
| Inconel 625 | 0.80 | Low |
| A286 | 0.85 | Low |
| **316L, 304L** | **0.90 to 0.92** | **Low. The default hydrogen material** |
| 6061, 2219 | 0.97 to 0.98 | Negligible. Aluminium is essentially immune |

**Austenitic stainless and aluminium are the hydrogen materials**, and the reason is the FCC lattice in both cases.

**Inconel 718 at 0.55 is better than steel and is not immune**, and the ratio falls as the aging treatment is pushed for strength. Hydrogen service argues for a lower strength age, which is a trade a strength-driven design will not make on its own.

---

## The temperature surprise

**Embrittlement is worst near 200 to 250 K, not at either extreme.**

| Temperature | Effect |
|---|---|
| Cryogenic | Diffusion too slow to feed the crack tip. **Reduced susceptibility** |
| **200 to 250 K** | **Peak susceptibility** |
| Ambient | High |
| Above ~400 K | Hydrogen escapes faster than it accumulates. Reduced |

This is counterintuitive and it has a practical consequence: **a hydrogen test at room temperature or at liquid hydrogen temperature both understate the effect.** A component that sees 220 K in service has to be tested there.

It also explains why liquid hydrogen tankage is less of an embrittlement problem than gaseous hydrogen plumbing at ambient. The cold slows the mechanism down.

---

## Where the hydrogen comes from

The propellant is the obvious source and it is not the most common one.

| Source | Notes |
|---|---|
| **Electroplating** | **The commonest source.** Cadmium, zinc and chromium plating all charge hydrogen into the substrate |
| Acid pickling and etching | Same mechanism, before plating |
| Alkaline cleaning | Cathodic cleaning charges hydrogen |
| Welding | Moisture in the flux, the shielding gas or on the surface |
| Corrosion | The cathodic half reaction produces atomic hydrogen at the surface |
| Cathodic protection | Overprotection charges hydrogen into the protected structure |
| Gaseous hydrogen service | Direct, and rate depends on pressure and temperature |

**A part that never sees hydrogen propellant can still fail by embrittlement**, and plating is how. This is why the bake requirement is triggered by tensile strength rather than by service.

---

## Bake-out

Per ASTM F1940 and AMS 2759/9, a part above the strength threshold that has been plated or acid processed requires a bake to drive the hydrogen out.

| Parameter | Requirement |
|---|---|
| **Trigger** | Ultimate tensile strength >= 1000 MPa |
| **Temperature** | 190 degC (463 K), typically 175 to 205 degC |
| **Time** | >= 23 hours, longer for higher strength |
| **Start within** | 4 hours of plating |

**The four hour window matters.** Hydrogen diffuses to traps and cracks initiate during that time, and a bake started late removes the hydrogen from a part that is already cracked.

**The bake temperature is bounded by the tempering temperature.** Baking above the temper softens the part, so a low tempered high strength steel has a narrow window and the process has to be controlled rather than assumed.

**Some plating processes are inherently low hydrogen** and are preferred for high strength parts: ion vapour deposited aluminium, mechanical plating, and aluminium coatings generally. IVD aluminium is the standard replacement for cadmium on high strength steel.

---

## Design practice

**Avoid the problem rather than manage it:**

| Practice | Reason |
|---|---|
| **Keep ultimate strength below 1000 MPa** | Below the trigger, most of the problem disappears |
| Use austenitic stainless or aluminium in hydrogen | FCC lattice, ratio above 0.9 |
| Specify IVD aluminium rather than cadmium plating | No hydrogen charging |
| Age nickel alloys to a lower strength for hydrogen service | The ratio falls with strength |
| **Never use a BCC alloy above 1400 MPa in hydrogen** | There is no bake that fixes it |
| Design out notches and stress concentrations | Triaxiality draws hydrogen in |
| Control weld moisture | Low hydrogen electrodes, dry gas, clean surfaces |
| Test at 220 K, not ambient | Peak susceptibility |

**ASTM F519 is the standard qualification test**, using a notched bar sustained load specimen held at 75 percent of notched fracture strength for 200 hours. It qualifies the process, not the part.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Bake trigger | 1000 MPa ultimate |
| Bake cycle | 23 h at 190 degC, started within 4 h |
| Peak susceptibility | 200 to 250 K |
| FCC alloys for hydrogen | Notched ratio above 0.9 |
| 718 is resistant, not immune | 0.55, and worse at higher strength |
| Titanium forms hydrides | Not a gaseous hydrogen material |
| Plating is the commonest source | Not the propellant |
| The failure is delayed | Hours to days after loading |
| Test at 220 K | Ambient and cryogenic both understate it |

---

## Failure modes

**Delayed fracture days after assembly.** A plated high strength fastener, no bake or a late bake.

**A part that passed every test failing in service.** The mechanism is time dependent; a fast tensile test does not see it.

**A cathodically overprotected structure embrittling.** Too much protection charges hydrogen in.

**Titanium hydriding in gaseous hydrogen.** A distinct mechanism, and the reason titanium is excluded.

**A bake performed above the tempering temperature.** The part is soft and the hydrogen is gone.

**A hydrogen test performed at room temperature.** Understates the effect by a wide margin.

**718 aged for maximum strength in hydrogen service.** The strongest condition is the most susceptible.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM F1940** | Process control verification to prevent hydrogen embrittlement in plating |
| **ASTM F519** | Mechanical hydrogen embrittlement evaluation of plating processes |
| **AMS 2759/9** | Hydrogen embrittlement relief baking of steel parts |
| ASTM F1624 | Measurement of the threshold for hydrogen stress cracking |
| ASTM G142 | Hydrogen embrittlement susceptibility in high pressure hydrogen |
| **ASME B31.12** | Hydrogen piping and pipelines |
| **ANSI/AIAA G-095** | Guide to safety of hydrogen and hydrogen systems |
| NASA/TM-2016-219078 | Safety standard for hydrogen and hydrogen systems |
| SAE AMS-QQ-P-416 | Cadmium plating, including the bake requirement |
| MIL-DTL-83488 | Aluminium coating, IVD |

---

## Tool interface

```python
from CorrosionAssessment import CorrosionAssessment

for material, condition in (('4340', 'qt-260'), ('Inconel 718', 'sta'), ('316L', 'annealed')):
    assessment = CorrosionAssessment()
    assessment.setInputs({'anodeMaterial': material, 'anodeCondition': condition,
                          'temperature': 220.0})           # peak susceptibility
    result = assessment.assessHydrogenEmbrittlement()
    print(material, result['susceptibilityIndex'], result['bakeRequired'],
          result['temperatureFactor'])
```

---

## References

1. ASTM F1940-07a, *Standard Test Method for Process Control Verification to Prevent Hydrogen Embrittlement in Plated or Coated Fasteners*.
2. Gangloff, R. P. and Somerday, B. P. (eds.), *Gaseous Hydrogen Embrittlement of Materials in Energy Technologies*, Woodhead, 2012.
3. San Marchi, C. and Somerday, B. P., *Technical Reference for Hydrogen Compatibility of Materials*, SAND2012-7321.
4. ANSI/AIAA G-095A-2017, *Guide to Safety of Hydrogen and Hydrogen Systems*.
5. Robertson, I. M. et al., "Hydrogen Embrittlement Understood", *Metallurgical and Materials Transactions A*, Vol. 46, 2015.
