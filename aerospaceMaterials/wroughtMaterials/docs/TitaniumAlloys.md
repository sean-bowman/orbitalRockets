[Home](../README.md) > Titanium Alloys

# Titanium Alloys

## Contents

- [Overview](#overview)
- [The alloy classes](#the-alloy-classes)
- [The alloys](#the-alloys)
- [Ti-6Al-4V](#ti-6al-4v)
- [The oxygen prohibition](#the-oxygen-prohibition)
- [Alpha case](#alpha-case)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Titanium has the best specific strength of any common structural metal, and it is disqualified from a large fraction of launch vehicle applications by a single incompatibility. Understanding where it can and cannot be used is most of the engineering.

---

## The alloy classes

| Class | Structure | Weldable | Formable | Strength |
|---|---|---|---|---|
| **Alpha** | HCP | **Excellent** | Poor | Low |
| **Alpha-beta** | Both | Good | Moderate | **High** |
| Beta | BCC | Good | **Excellent** | Very high after ageing |

**Alpha-beta alloys are the structural class** and Ti-6Al-4V is 50 percent of all titanium used.

**Alpha alloys weld best** and they are used where weldability governs: CP titanium tubing and pressure vessel liners.

**Beta alloys form best** in the solution treated condition and then age to very high strength. Ti-15-3 and Beta-C are used for springs, fasteners and heavily formed parts.

---

## The alloys

| Alloy | Yield [MPa] | Class | Use |
|---|---|---|---|
| **Ti-6Al-4V** | 828 (annealed) | Alpha-beta | **The default. COPV bosses, structure, fittings** |
| **Ti-6Al-4V ELI** | 795 | Alpha-beta | **Cryogenic and fracture critical.** Low interstitial |
| **CP Ti grade 2** | 275 | Alpha | **Weldable.** Tube, liners, corrosion service |
| **Ti-3Al-2.5V** | 500 | Alpha-beta | **Hydraulic tube.** The tubing alloy |
| Ti-5Al-2.5Sn | 795 | Alpha | Cryogenic |

**ELI means extra low interstitial**, with oxygen held below 0.13 percent against 0.20 for standard grade. Oxygen strengthens titanium and it embrittles it, so the ELI grade trades 4 percent of the yield strength for a substantially better fracture toughness and much better cryogenic ductility.

**ELI is mandatory for fracture critical and cryogenic parts**, and specifying standard grade where ELI was intended is a real and recurring error.

**Ti-3Al-2.5V is the hydraulic tubing alloy** and it is nearly the only titanium alloy available as thin wall seamless tube, which is why it appears wherever a titanium line is needed.

---

## Ti-6Al-4V

| Condition | Yield [MPa] | Notes |
|---|---|---|
| **Annealed** | 828 | **The usual condition.** Best toughness and weldability |
| **STA** | 1035 | Solution treated and aged. Higher strength |
| Beta annealed | 795 | Best toughness and creep, coarser structure |
| LPBF HIP + anneal | ~850 | Comparable to wrought, with a build direction knockdown |

**Annealed is the usual specification** and STA is chosen only where the strength is genuinely needed, because STA loses fracture toughness. In the helium bottle worked example, the STA condition lost the leak-before-burst condition that the annealed condition satisfied.

**The beta transus is around 995 degC** and processing above it produces a coarse transformed structure with poor fatigue. All conventional processing is below it. See [formingProcesses Forging.md](../../formingProcesses/docs/Forging.md).

**Specific strength is its whole argument**: 187 kNm/kg against 148 for 7075-T73 and 51 for 316L. On a `sigma/rho` ranking it wins by 1.9x over aluminium and 3.3x over stainless.

---

## The oxygen prohibition

**Titanium is prohibited in liquid and gaseous oxygen, in nitrogen tetroxide and in red fuming nitric acid**, and the reason is that it burns.

| Environment | Status |
|---|---|
| **LOX, GOX** | **Prohibited** |
| **N2O4** | **Prohibited** |
| RFNA | Prohibited |
| Hydrazine, MMH | Acceptable |
| RP-1 | Acceptable |
| LH2, GH2 | With care. Hydride formation |
| Helium, nitrogen | Acceptable |

**The mechanism is that titanium's oxide film is protective until it is disrupted**, and once disrupted in an oxygen environment the fresh metal reacts exothermically enough to sustain combustion. A scratch, an impact or a particle strike is sufficient initiation.

**The prohibition is absolute in the applicable standards** and it is not a matter of margin. NASA-STD-6001 and the ASTM G-4 committee documents treat it as a categorical exclusion.

**This is the constraint that most often removes titanium from a launch vehicle application.** In the helium bottle worked example, titanium wins the Ashby ranking by 1.9x and is then rejected outright when the same bottle is specified for GOX service, with IN718 becoming the answer at a 30 percent mass penalty.

---

## Alpha case

**An oxygen enriched surface layer formed when titanium is heated in air above about 480 degC.**

| Property | Effect |
|---|---|
| **Hard and brittle** | It cracks under load |
| **Depth** | Tens to hundreds of micrometres, growing as `sqrt(time)` |
| **Fatigue** | Severely reduced. It is a crack initiation layer |
| Detection | Metallographic section, or microhardness traverse |

**Any titanium heat treatment in air produces it**, which is why titanium is heat treated in vacuum or in argon wherever practical.

**It must be removed** where it forms: by chemical milling in a nitric-hydrofluoric bath, or by machining. The depth has to be known so the removal can be specified with margin.

**It is the reason titanium castings need chemical milling** and the reason titanium is not centrifugally cast. See [spinCasting Alloys.md](../../spinCasting/docs/Alloys.md) and [postProcessing AlphaCaseRemoval.md](../../postProcessing/docs/AlphaCaseRemoval.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Best specific strength of the common metals | 187 kNm/kg |
| **Prohibited in LOX, GOX, N2O4** | Categorical |
| ELI for fracture critical and cryogenic | Oxygen below 0.13 % |
| Annealed unless the strength is needed | STA loses toughness |
| Beta transus ~995 degC | Process below it |
| Ti-3Al-2.5V for tube | Nearly the only option |
| Alpha case above 480 degC in air | Vacuum or argon, or remove it |
| Machinability index 22 | Low speed, high pressure coolant |

---

## Failure modes

**Titanium in an oxygen system.** Prohibited, and it burns.

**Standard grade used where ELI was intended.** Reduced toughness and cryogenic ductility.

**Heat treated in air.** Alpha case.

**Alpha case not removed.** Severe fatigue debit.

**Processed above the beta transus.** Coarse structure, poor fatigue.

**STA specified for a fracture critical part.** Leak-before-burst may be lost.

**Titanium galvanically coupled to aluminium.** 1.05 V against a 0.15 V limit.

---

## Standards

| Standard | Scope |
|---|---|
| **AMS 4911** | Ti-6Al-4V sheet, strip and plate, annealed |
| **AMS 4928** | Ti-6Al-4V bar, forgings and rings, annealed |
| AMS 4930 | Ti-6Al-4V ELI |
| AMS 4945 | Ti-3Al-2.5V seamless hydraulic tube |
| **AMS 2801** | Heat treatment of titanium alloy parts |
| **NASA-STD-6001** | Flammability, offgassing and compatibility |
| ASTM G124 | Combustion of metals in oxygen |
| ASTM B367 | Titanium castings |
| AMS 2488 | Anodic treatment of titanium |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterialsLibrary')

from MaterialSelector import MaterialSelector

selector = MaterialSelector()
selector.setInputs({'requirements': {'fluids': ['GOX'], 'serviceTemperature': 293.0},
                    'loadingMode': 'pressure vessel'})
screen = selector.screen()

for label in screen['rejected']:
    print(f'REJECTED {label}')
for entry in selector.rank()[:5]:
    print(f'{entry["label"]:24s} index {entry["index"]:12.4g}')
```

---

## References

1. Boyer, R., Welsch, G. and Collings, E. W., *Materials Properties Handbook: Titanium Alloys*, ASM International, 1994.
2. Leyens, C. and Peters, M., *Titanium and Titanium Alloys*, Wiley-VCH, 2003.
3. NASA-STD-6001B, *Flammability, Offgassing, and Compatibility Requirements and Test Procedures*.
