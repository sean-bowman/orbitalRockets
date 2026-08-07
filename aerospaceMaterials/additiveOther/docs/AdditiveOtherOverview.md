[Home](../README.md) > Additive Other Overview

# Non-LPBF Additive Processes

## Contents

- [Overview](#overview)
- [Why this sub-domain has no library](#why-this-sub-domain-has-no-library)
- [The processes](#the-processes)
- [The two axes that matter](#the-two-axes-that-matter)
- [Where each wins](#where-each-wins)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [Document index](#document-index)
- [References](#references)

---

## Overview

Laser powder bed fusion gets the attention and it is one of six or seven additive processes with aerospace relevance. The others cover the ranges LPBF cannot: parts larger than a build chamber, deposition rates an order of magnitude higher, and repair of existing hardware.

LPBF has its own sub-domain in [additiveLPBF](../../additiveLPBF/). This one covers everything else.

---

## Why this sub-domain has no library

**Each process reduces to one or two equations that belong in [`ProcessComparison`](../../aerospaceMaterialsLibrary/ProcessComparison.py)'s route table**, not in a class of its own.

**A class per process would be a lookup table with a `calculate` method**, duplicating the route data that already exists in one place. The route table is where the deposition rate, the achievable tolerance, the allowable knockdown and the lead time belong, because that is where they get compared against every other route.

**What this sub-domain contributes is the knowledge of which process suits what**, and the failure modes each one carries. That is documentation.

---

## The processes

| Process | Feedstock | Rate [cm^3/h] | Tolerance | Size | Properties |
|---|---|---|---|---|---|
| **LPBF** (reference) | Powder bed | 20 to 80 | **IT8** | 400 mm | Near wrought, HIP |
| **EB-PBF** | Powder bed | 55 to 110 | IT10 | 350 mm | **Low residual stress** |
| **DED, powder** | Blown powder | 50 to 500 | IT12 | **Metres** | Good, directional |
| **DED, wire (WAAM)** | Wire | **500 to 5000** | IT14 | **Metres** | Good, very coarse |
| **Binder jetting** | Powder plus binder | High | IT11 | 500 mm | **Sintered. Porosity** |
| **Cold spray** | Powder, supersonic | 500 to 3000 | IT13 | Unlimited | **No melting.** Cold worked |
| Sheet lamination | Foil | High | IT10 | Large | Bonded, anisotropic |

**The deposition rate spans two orders of magnitude** and it is inversely related to resolution, which is the fundamental trade in this table.

---

## The two axes that matter

**Resolution against rate, and melting against not melting.**

### Resolution against rate

| End | Process | Consequence |
|---|---|---|
| **Fine, slow** | LPBF, EB-PBF | Complex internal geometry, small parts |
| **Coarse, fast** | WAAM, cold spray | Large simple shapes, near net preforms |

**WAAM at 5000 cm^3/h against LPBF at 50 is a factor of a hundred.** That is not an incremental difference; it puts them in different applications entirely. WAAM makes a preform that is then machined; LPBF makes a finished part.

### Melting against not melting

| Category | Processes | Consequence |
|---|---|---|
| **Melting** | LPBF, EB-PBF, DED, WAAM | Residual stress, solidification structure, reactive material issues |
| **Not melting** | **Cold spray**, binder jet, sheet lamination | **No residual stress from solidification. No HAZ** |

**Cold spray's lack of melting is what makes it a repair process.** Material can be added to an existing part without a heat affected zone, without distortion and without changing the substrate's temper.

**Binder jetting does not melt during printing** and it sinters afterwards, which moves all the thermal problems into a furnace cycle where they are uniform and predictable rather than local and transient.

---

## Where each wins

| Need | Process |
|---|---|
| **Complex internal geometry** | LPBF |
| **Low residual stress, titanium** | **EB-PBF** |
| **Very large structure** | **WAAM or DED** |
| **Repair of existing hardware** | **DED or cold spray** |
| **Adding material with no HAZ** | **Cold spray** |
| **High volume, moderate properties** | **Binder jetting** |
| Functionally graded material | DED |
| A near net preform for machining | WAAM |

**Repair is the application that has no LPBF equivalent.** A worn or damaged part cannot be put in a powder bed; DED and cold spray add material to it in place, and that is a substantial part of why they exist.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Rate and resolution trade | Two orders of magnitude across the table |
| WAAM makes preforms, LPBF makes parts | |
| EB-PBF for low residual stress | Hot powder bed |
| Cold spray and binder jet do not melt | No HAZ, no solidification stress |
| DED and cold spray for repair | LPBF cannot |
| Size beyond a build chamber means DED or WAAM | |
| Every process needs its own qualification | They are not interchangeable |

---

## Failure modes

**LPBF assumed to represent additive generally.** The processes differ enormously.

**WAAM specified for a finished geometry.** It makes preforms.

**A process qualification transferred between processes.** Not valid.

**Cold spray assumed to bond like a weld.** It is mechanical interlock plus some metallurgical bonding.

**Binder jet part designed at wrought density.** It sinters to 95 to 99 %.

**Build direction anisotropy ignored.** It is present in every one of them.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-6030** | Additive manufacturing requirements for spaceflight |
| NASA-STD-6033 | Additive manufacturing quality |
| **ASTM F3049 / F2924 / F3001** | Powder and titanium additive specifications |
| ASTM F3187 | **Directed energy deposition** |
| ASTM F3049 | Characterising properties of metal powders |
| **ISO/ASTM 52900 series** | Additive manufacturing terminology and process categories |
| AWS D20.1 | Fabrication of metal components using additive manufacturing |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterialsLibrary')

from ProcessComparison import ProcessComparison

comparison = ProcessComparison()
comparison.setInputs({'material': 'TI-6AL-4V', 'condition': 'annealed', 'finishedMass': 40.0,
                      'minimumWallThickness': 0.008, 'characteristicSize': 1.500,
                      'requiredTolerance': 1.0e-3})
for entry in comparison.compareRoutes()[:4]:
    print(f'{entry["route"]:32s} btf {entry["buyToFly"]:4.1f}:1  '
          f'allow {entry["allowableFactor"]:.2f}')
```

---

## Document index

| Document | Covers |
|---|---|
| [DirectedEnergyDeposition.md](DirectedEnergyDeposition.md) | Blown powder DED, repair, graded material |
| [WireArcAdditive.md](WireArcAdditive.md) | WAAM, large structure, preforms |
| [ElectronBeamPowderBed.md](ElectronBeamPowderBed.md) | EB-PBF, low residual stress, titanium |
| [BinderJetting.md](BinderJetting.md) | Print and sinter, shrinkage, density |
| [ColdSpray.md](ColdSpray.md) | Supersonic solid state deposition, repair |
| [Repair.md](Repair.md) | Adding material to existing hardware |
| [ProcessSelection.md](ProcessSelection.md) | Choosing between them |
| [Qualification.md](Qualification.md) | What each process needs |
| [ProcessComparison.md](ProcessComparison.md) | Against LPBF, casting and machining |

---

## References

1. Gibson, I., Rosen, D. and Stucker, B., *Additive Manufacturing Technologies*, 3rd ed., Springer, 2021.
2. NASA-STD-6030, *Additive Manufacturing Requirements for Spaceflight Systems*.
3. DebRoy, T. et al., "Additive Manufacturing of Metallic Components: Process, Structure and Properties", *Progress in Materials Science*, Vol. 92, 2018.
