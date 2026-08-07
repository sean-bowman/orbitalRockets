[Home](../README.md) > Dissimilar Metal Joints

# Dissimilar Metal Joints

## Contents

- [Overview](#overview)
- [The three problems](#the-three-problems)
- [Intermetallics](#intermetallics)
- [Thermal expansion mismatch](#thermal-expansion-mismatch)
- [Galvanic corrosion](#galvanic-corrosion)
- [The solutions](#the-solutions)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A joint between two different metals has three independent failure modes that a joint between like metals does not. Each one has a different solution, and a design that addresses one and not the others has not solved the problem.

---

## The three problems

| Problem | When it bites | Solution |
|---|---|---|
| **Intermetallics** | **During fusion welding** | Avoid melting, or use a transition |
| **Thermal expansion mismatch** | **In service, on temperature change** | Compliance, or matched materials |
| **Galvanic corrosion** | **In service, with an electrolyte** | Isolation, coatings, sealant |

---

## Intermetallics

**When two dissimilar metals are melted together, the mixture solidifies with intermetallic compounds that are hard and brittle.**

| Pair | Intermetallic | Consequence |
|---|---|---|
| **Aluminium to steel** | FeAl3, Fe2Al5 | **Extremely brittle.** Fusion welding is not viable |
| **Aluminium to titanium** | TiAl3 | Brittle |
| Copper to steel | Limited | Manageable |
| **Aluminium to copper** | CuAl2 and others | Brittle |
| Nickel to steel | None significant | **Weldable** |
| Stainless to nickel alloys | None significant | **Weldable, with 625 filler** |

**Intermetallic layer thickness grows with time at temperature**, so the amount formed depends on the heat input and the cooling rate. A very fast, very low heat input process forms a thin enough layer to be tolerable.

**A few micrometres of intermetallic is tolerable and tens are not.** That is the entire design window for processes that do form them.

**Stainless to nickel is the easy dissimilar case** because they are mutually soluble across the whole range. IN625 filler handles it, and the joint is essentially a conventional weld.

---

## Thermal expansion mismatch

| Material | alpha [1e-6 /K] |
|---|---|
| **Aluminium** | **23** |
| Copper | 17 |
| Austenitic stainless | 16 |
| Nickel alloys | 13 |
| Steel | 12 |
| **Titanium** | **8.6** |
| Invar | 1.2 |

**Aluminium to titanium is a factor of 2.7**, which is the worst common structural pair.

**The stress from a constrained joint is**

```
sigma = E * (alpha_1 - alpha_2) * dT
```

**A cryogenic system is the severe case** because `dT` is 270 K or more. An aluminium fitting in a titanium boss cooled to 77 K develops very large interference or clearance depending on which is outside.

**The consequences are joint gapping, seal leakage, bolt preload loss and bondline fatigue**, and they are all reversible each cycle, which makes it a fatigue problem rather than a strength one.

**Compliance is the design answer**: a flexible element, a bellows, a sliding joint, or an adhesive with enough elongation to absorb the differential.

---

## Galvanic corrosion

```
dE = |anodicIndex_1 - anodicIndex_2|
```

| Limit | Environment |
|---|---|
| **0.15 V** | Marine and coastal |
| **0.25 V** | General |
| 0.50 V | Controlled dry indoor |

| Couple | dE | Verdict |
|---|---|---|
| **Ti-6Al-4V to 6061** | **1.05 V** | Rejected, and it is the classic case |
| 316L to 6061 | 0.75 V | Rejected |
| **316L to IN625** | **0.20 V** | Passes general, **fails marine** |
| 2024 to 7075 | 0.05 V | Acceptable |

**Three conditions are needed for galvanic corrosion**: electrical contact, an electrolyte, and a potential difference. Breaking any one stops it, and breaking the electrolyte path is usually the easiest.

**The area ratio governs the rate.** A small anode against a large cathode corrodes fast, because all the galvanic current concentrates on a small area. **Never put a small anodic fastener into a large cathodic structure.**

**The 316L to IN625 couple at 0.20 V is a useful example** because it passes the general limit and fails the marine one, which means the same joint is acceptable at one launch site and not at another.

---

## The solutions

| Solution | Addresses | Detail |
|---|---|---|
| **Mechanical fastening with isolation** | All three | Sealant, isolating washers, coated fasteners |
| **Brazing** | Intermetallics | The parents do not melt |
| **Explosive welding** | Intermetallics | Solid state, and it makes transition joints |
| **Transition joints** | Intermetallics, expansion | A bimetallic block, welded conventionally each side |
| **Adhesive bonding** | Galvanic, expansion | The bondline isolates and it is compliant |
| Coatings and sealant | Galvanic | Break the electrolyte path |
| Sacrificial anode | Galvanic | Give the current something else |

**Explosive welded transition joints are the standard answer for aluminium to stainless** in cryogenic piping. A block with aluminium on one face and stainless on the other, bonded explosively in the solid state, is welded conventionally to aluminium on one side and stainless on the other. Neither weld is dissimilar.

**Sealant at the faying surface is the practical galvanic control** in fastened aerospace structure, and it works by excluding the electrolyte. Wet installation of fasteners does the same for the hole.

**Coat the cathode, not the anode**, if only one can be coated. A defect in a coating on the anode concentrates the whole galvanic current onto a tiny area of exposed anode, which is worse than no coating. A defect in the cathode coating merely exposes a small cathode.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Three independent problems | Each needs its own solution |
| Aluminium to steel is not fusion weldable | Intermetallics |
| Stainless to nickel is easy | Mutually soluble, 625 filler |
| Al to Ti expansion ratio 2.7 | The worst common pair |
| Galvanic limits 0.25 V, 0.15 V marine | |
| Area ratio governs the rate | Small anode is the bad case |
| **Coat the cathode, not the anode** | |
| Explosive transition joints for Al to stainless | The cryogenic standard |

---

## Failure modes

**Aluminium fusion welded to steel.** Brittle intermetallics.

**One problem solved, three present.** Galvanic addressed, expansion ignored.

**Small anodic fastener in a large cathodic structure.** Rapid attack.

**Anode coated instead of the cathode.** A coating defect concentrates the current.

**Cryogenic dissimilar joint designed at room temperature.** Gapping or overload at temperature.

**Marine service designed to the 0.25 V limit.** The limit is 0.15 V.

---

## Standards

| Standard | Scope |
|---|---|
| **MIL-STD-889** | Dissimilar metals |
| ASTM G82 | Development and use of a galvanic series |
| **ASTM G71** | Galvanic corrosion testing in electrolytes |
| SAE ARP1481 | Corrosion control and electrical conductivity in enclosures |
| ASTM B898 | Reactive and refractory metal clad plate |
| AWS D17.1 | Fusion welding for aerospace |
| ASTM E228 | Linear thermal expansion |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterialsLibrary')

from CorrosionAssessment import CorrosionAssessment

for anode, cathode in (('6061', 'TI-6AL-4V'), ('316L', 'INCONEL 625'), ('2024', '7075')):
    assessment = CorrosionAssessment()
    assessment.setInputs({'anodeMaterial': anode, 'cathodeMaterial': cathode,
                          'environment': 'launch site marine'})
    result = assessment.calculateGalvanicCouple()
    print(f'{anode:8s} to {cathode:12s} dE {result["potentialDifference"]:.2f} V  '
          f'{"OK" if result["acceptable"] else "REJECTED"}')
```

---

## References

1. MIL-STD-889C, *Dissimilar Metals*.
2. Jones, D. A., *Principles and Prevention of Corrosion*, 2nd ed., Prentice Hall, 1996.
3. Messler, R. W., *Joining of Materials and Structures*, Butterworth-Heinemann, 2004.
