[Home](../README.md) > Material Substitution

# Material Substitution

## Contents

- [Overview](#overview)
- [What has to be checked](#what-has-to-be-checked)
- [The properties nobody checks](#the-properties-nobody-checks)
- [Common substitutions and their traps](#common-substitutions-and-their-traps)
- [Cross reference is not equivalence](#cross-reference-is-not-equivalence)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Substitution requests arrive because of lead time, cost or availability, and they are usually justified on one property. The failures come from the properties nobody compared.

---

## What has to be checked

| Property | Why |
|---|---|
| **Strength, at temperature** | The obvious one, and the one always checked |
| **Fracture toughness** | Changes the critical flaw size and the leak-before-burst condition |
| **Fatigue** | Often the governing requirement, and rarely compared |
| **Corrosion and SCC** | Especially the ST threshold |
| **Propellant compatibility** | Categorical prohibitions, not gradual |
| **Galvanic compatibility** | With whatever it is bolted to |
| **Weldability** | A different filler, or none |
| **Thermal expansion** | In a joint or an assembly |
| **Density** | The mass, and the mass properties |
| Availability and form | The reason for the substitution in the first place |

**Ten properties, and a typical substitution request compares one.**

---

## The properties nobody checks

**Three in particular, and each has a service history behind it.**

**Fracture toughness.** A stronger substitute usually has a lower toughness, which reduces the critical flaw size, which may take a part from leak-before-burst to burst-before-leak. In the helium bottle worked example, substituting Ti-6Al-4V STA for the annealed condition gained 25 percent strength and lost the leak-before-burst condition entirely.

**Galvanic couple.** A substitute changes the anodic index and therefore the couple with everything it touches. Titanium at 0.15 against 6061 at 0.90 is 0.75 V, and that same part in stainless would have been 0.35. The marine limit is 0.15 V and the general limit 0.25.

**Thermal expansion in an assembly.** A substitution that changes `alpha` changes every interference fit, every bolted joint preload over temperature and every seal compression in a cryogenic system. A titanium fitting in an aluminium manifold behaves differently at 77 K than the aluminium fitting it replaced.

---

## Common substitutions and their traps

| Substitution | Gained | Trap |
|---|---|---|
| **304L for 316L** | Cost, availability | **PREN 19 against 26.** Chloride pitting |
| **316 for 316L** | Strength, availability | **Sensitization** on welding |
| **7075-T6 for T73** | 15 % strength | **ST SCC.** The reason T73 exists |
| **6061 for 2219** in a tank | Cost, availability | Lower strength, and different cryogenic behaviour |
| **IN718 for IN625** | Strength | **650 degC limit**, and hydrogen susceptibility |
| **Ti-6Al-4V for stainless** | 1.9x specific strength | **Oxidiser prohibition**, galvanic couple |
| Standard grade for ELI | Availability | Toughness, cryogenic ductility |
| **17-4PH H900 for H1025** | 17 % strength | SCC and hydrogen susceptibility |

**304L for 316L is the commonest and it is usually fine and sometimes not.** The molybdenum is the entire difference, and it matters only in chloride. A dry gas system does not care; a coastal launch site or a seawater-adjacent installation does.

**316 for 316L is the one that looks harmless.** The carbon difference is invisible on a certificate to anyone not looking for it, and the consequence appears months later as intergranular corrosion in the weld HAZ.

---

## Cross reference is not equivalence

**Cross reference tables list alloys with similar chemistry. They do not certify interchangeability.**

| Pair | Relationship |
|---|---|
| **UNS S31603 and 316L** | The same alloy, different designation systems |
| **1.4404 and 316L** | European equivalent. **Similar, not identical** |
| **SUS316L and 316L** | Japanese. Similar |
| **AMS 5507 and ASTM A240 316L** | The same alloy to different specifications, with different requirements |

**The specification matters as much as the alloy.** An AMS specification for a given alloy typically carries tighter chemistry, additional testing and quality requirements over the equivalent ASTM. Substituting the ASTM version of the "same alloy" drops those requirements.

**European and Japanese equivalents have different chemistry ranges** and different mechanical minima. They are close and they are not the same, and for a flight critical part the difference has to be evaluated rather than assumed away.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Ten properties, not one | The checklist above |
| Fracture toughness usually falls when strength rises | Check leak-before-burst |
| A substitution changes every galvanic couple it makes | |
| Thermal expansion propagates through the assembly | |
| Propellant prohibitions are categorical | Not a margin question |
| Cross reference is similarity, not equivalence | |
| The specification matters as much as the alloy | AMS is not ASTM |

---

## Failure modes

**Substitution justified on strength alone.** Nine properties unchecked.

**316 substituted for 316L.** Sensitized HAZ, months later.

**7075-T6 substituted for T73.** ST stress corrosion.

**Titanium substituted into an oxidiser system.** Prohibited.

**European equivalent treated as identical.** Different chemistry range and minima.

**ASTM substituted for AMS.** Testing and quality requirements dropped.

**Stronger substitute in a fracture critical part.** Leak-before-burst lost.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-6016** | Materials and processes requirements, including substitution |
| **MMPDS** | Allowables, the basis for comparison |
| AS9100 | Quality management, change control |
| SAE J1086 | Numbering metals and alloys, UNS |
| NASA-STD-6001 | Flammability, offgassing and compatibility |
| ASTM G82 | Development and use of a galvanic series |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterialsLibrary')

from MaterialSelector import MaterialSelector

selector = MaterialSelector()
selector.setInputs({'requirements': {'fluids': ['LOX'], 'serviceTemperature': 90.0},
                    'loadingMode': 'pressure vessel'})
screen = selector.screen()

for label in screen['rejected']:
    print(f'REJECTED {label}')
for entry in selector.rank()[:5]:
    print(f'{entry["label"]:24s} index {entry["index"]:12.4g}')
```

---

## References

1. NASA-STD-6016B, *Standard Materials and Processes Requirements for Spacecraft*.
2. MMPDS-2023, *Metallic Materials Properties Development and Standardization*.
3. Campbell, F. C., *Manufacturing Technology for Aerospace Structural Materials*, Elsevier, 2006.
