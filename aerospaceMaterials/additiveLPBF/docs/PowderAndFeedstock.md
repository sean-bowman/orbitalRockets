[Home](../README.md) > Powder and Feedstock

# Powder and Feedstock

## Contents

- [Overview](#overview)
- [How powder is made](#how-powder-is-made)
- [Particle size distribution](#particle-size-distribution)
- [Morphology and flow](#morphology-and-flow)
- [Chemistry and oxygen pickup](#chemistry-and-oxygen-pickup)
- [Reuse and blend-back](#reuse-and-blend-back)
- [Handling and safety](#handling-and-safety)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Powder is a controlled material, not a consumable. Its condition changes every time it goes through the machine, and the two things that change are the two that matter most: how it flows, and what is dissolved in it.

A programme that does not have a written reuse policy with a retirement criterion is guessing about a material property that decides fracture toughness.

---

## How powder is made

| Route | Result |
|---|---|
| **Gas atomisation** | Molten stream broken up by inert gas jets. Spherical, some satellites, entrapped gas porosity. The default |
| **Plasma atomisation** | Wire fed into a plasma. Very spherical, very clean, expensive. Titanium mostly |
| **Plasma rotating electrode** | A spinning electrode melted at its face. The cleanest available, no entrapped gas, expensive and coarse |
| Water atomisation | Irregular and oxidised. Not usable for powder bed |

**Entrapped gas porosity in the powder itself** is a real defect source in gas atomised material. A hollow particle carries argon that ends up in the part, and HIP does not remove it because the gas is still in there under pressure. It re-expands on any subsequent heat treatment, which is why HIPed additive parts can develop porosity on a later solution treatment.

---

## Particle size distribution

The standard cut is 15 to 45 um, and both bounds exist for a reason.

| Bound | Why |
|---|---|
| **Fines below 15 um** | Cohesive, so they degrade flow. Also the inhalation and explosion hazard |
| **Coarse above 45 um** | Cannot be spread in a 40 um layer. Dragged by the recoater, scoring the layer |

**The d90 against layer thickness check is what catches reused powder**, because the distribution coarsens with every cycle: fines are consumed preferentially, both by being melted and by being carried away in the gas flow.

**Distribution span** `(d90 - d10) / d50` matters as much as the bounds. A wide distribution segregates during handling, so the powder that reaches the bed is not the powder that was tested.

---

## Morphology and flow

The recoater spreads loose powder in a fraction of a second and does not tap it. A powder that only packs well when tapped spreads badly.

**Hausner ratio** is tapped density over apparent density:

| Ratio | Classification | Meaning for the recoater |
|---|---|---|
| 1.00 to 1.11 | Excellent | Spreads uniformly at any speed |
| 1.11 to 1.18 | Good | The normal condition for virgin gas atomised powder |
| 1.18 to 1.25 | Fair | Reduce the recoat speed |
| **Above 1.25** | Passable to very poor | Layer defects, and porosity no parameter change fixes |

**Satellites are the usual cause of degradation.** Small particles welded to larger ones by the spatter of previous builds. They interlock and stop the powder flowing.

---

## Chemistry and oxygen pickup

**Oxygen is the property that retires a lot**, and for titanium it is the only one that matters.

| Alloy | Virgin | Limit | Window |
|---|---|---|---|
| Ti-6Al-4V | 0.13 % | 0.20 % | 0.07 % |
| **Ti-6Al-4V ELI** | **0.10 %** | **0.13 %** | **0.03 %** |
| Inconel 718 | 0.020 % | 0.050 % | 0.030 % |
| 316L | 0.025 % | 0.060 % | 0.035 % |

**The ELI window is 0.03 percent wide.** Drift past it and the powder is grade 5, a third of the fracture toughness has gone, and nothing visible has changed. Only a measurement catches it.

**Oxygen is measured by inert gas fusion.** It is neither expensive nor slow, and a titanium programme that does not measure it on a schedule is guessing.

---

## Reuse and blend-back

Reuse is economically necessary. A build consumes a few percent of the powder in the chamber and the rest is recovered, so virgin-only operation is unaffordable on any alloy worth printing.

**What makes it safe:**

| Element | Purpose |
|---|---|
| Sieving after every build | Removes spatter, agglomerates and the coarse fraction |
| A blend-back ratio | Dilutes the accumulated oxygen |
| Oxygen testing on a schedule | Catches the drift the projection misses |
| A retirement criterion | Written down, not judged |
| Lot records | The blend has to be traceable |

**The steady state is the useful concept.** There is a virgin fraction at which the oxygen added per build exactly equals the oxygen removed by dilution, and running at that ratio means the lot never retires on chemistry.

---

## Handling and safety

**Titanium and aluminium powders are genuinely dangerous**, and the fines fraction is the hazard.

| Hazard | Control |
|---|---|
| **Dust explosion** | Inert handling, grounded equipment, no ignition sources, explosion relief |
| **Pyrophoricity** | Fine titanium ignites in air. Handle under argon |
| **Inhalation** | Respiratory protection. Some alloys carry nickel and cobalt sensitisation risk |
| **Wet reaction** | Aluminium and water produce hydrogen. Never wet-clean aluminium powder equipment |

**Powder handling is a process safety problem and it should be treated as one**, with a hazard analysis rather than a set of habits.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Standard cut | 15 to 45 um |
| d90 against layer thickness | Below 80 % |
| Hausner ratio | Below 1.18 for production |
| Sieve after every build | 63 um standard mesh |
| Measure oxygen on a schedule | Not on suspicion |
| ELI titanium window | 0.03 percent |
| Blend-back | Run at the steady state fraction |
| Powder handling | A process safety problem |

---

## Failure modes

**Powder reused past the oxygen limit.** ELI becomes grade 5 silently.

**Poor flow from satellites.** Non-uniform layers and porosity that looks like a parameter problem.

**Coarse particles in a fine layer.** Recoater drag and a build crash.

**Aluminium powder exposed to humid air.** Hydrogen porosity throughout.

**Blend not recorded.** Traceability broken back to the certificate.

**Wet cleaning of aluminium powder equipment.** Hydrogen generation.

---

## Worked numbers

From [`PowderLot`](../additiveLpbfLibrary/PowderLot.py), Ti-6Al-4V ELI at the default pickup rate:

| Cycle | Oxygen | Cycles remaining |
|---|---|---|
| 0 | 0.1000 % | 7 |
| 5 | 0.1200 % | 2 |
| **8** | **at the limit** | **retired** |

| Blend-back at cycle 6 | Value |
|---|---|
| Virgin fraction to reach 0.115 % | **37 %** |
| **Steady state virgin fraction** | **27 %** |

Running at 27 percent virgin on every build holds the lot indefinitely, so it never retires on chemistry.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM F3049** | Characterizing properties of metal powders for additive manufacturing |
| ISO/ASTM 52907 | Feedstock materials, methods to characterise metal powders |
| ASTM B212 / B417 | Apparent density |
| ASTM B527 | Tap density |
| ASTM B822 | Particle size by light scattering |
| ASTM E1409 | Oxygen and nitrogen by inert gas fusion |
| **NFPA 484** | Combustible metals |

---

## Tool interface

```python
from PowderLot import PowderLot

lot = PowderLot()
lot.setInputs({'material': 'Ti-6Al-4V ELI', 'lotIdentifier': 'LOT-A',
               'apparentDensity': 2500.0, 'tappedDensity': 2820.0,
               'particleD10': 18.0e-6, 'particleD50': 32.0e-6, 'particleD90': 48.0e-6,
               'reuseCycles': 6})

lot.calculateFlowability()
lot.checkParticleSize(layerThickness = 40.0e-6)
lot.projectOxygenPickup()        # raises when the limit is reached
lot.calculateBlendBack()
print(lot.assessLot()['disposition'])
```

---

## References

1. ASTM F3049-14, *Standard Guide for Characterizing Properties of Metal Powders Used for Additive Manufacturing Processes*.
2. Sutton, A. T. et al., "Powder Characterisation Techniques and Effects of Powder Characteristics on Part Properties", *Virtual and Physical Prototyping*, Vol. 12, 2017.
3. Cordova, L., Campos, M. and Tinga, T., "Revealing the Effects of Powder Reuse for Selective Laser Melting", *JOM*, Vol. 71, 2019.
4. NFPA 484, *Standard for Combustible Metals*.
