[Home](../README.md) > Surface Integrity

# Surface Integrity

## Contents

- [Overview](#overview)
- [What the cut leaves behind](#what-the-cut-leaves-behind)
- [Residual stress](#residual-stress)
- [White layer](#white-layer)
- [Grinding burn](#grinding-burn)
- [The fatigue consequence](#the-fatigue-consequence)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Machining changes the material it leaves behind. The surface layer carries a residual stress, a modified microstructure and sometimes a transformed layer, and all three affect fatigue life far more than the roughness does.

Surface integrity is invisible on a drawing that specifies only Ra, and that is the problem.

---

## What the cut leaves behind

| Condition | Residual stress | Fatigue effect |
|---|---|---|
| **Sharp tool, flood coolant** | **-150 MPa compressive** | **Beneficial, ~1.2x** |
| Sharp tool, dry | -50 MPa | Slightly beneficial |
| **Worn tool, flood coolant** | +100 MPa tensile | **Detrimental** |
| **Worn tool, dry** | **+300 MPa tensile** | **Severely detrimental** |
| Abusive grinding | +400 MPa and worse | Severe, plus burn |

**A sharp tool leaves compression and a worn tool leaves tension**, and the swing between them is 450 MPa. That is a larger effect than most design decisions.

**The mechanism is the balance between mechanical and thermal effects.** A sharp tool cuts cleanly and the dominant effect is the plastic burnishing of the surface by the flank, which leaves compression. A worn tool has a large flank land that rubs and heats; the surface expands, is constrained, and ends up in tension when it cools.

**Coolant shifts the balance toward compression** by removing the heat that produces the tensile component.

**Tool wear limits therefore have a surface integrity basis as well as a dimensional one**, and on a fatigue critical surface the wear limit should be set by the surface it produces, not by the dimension it holds.

---

## Residual stress

| Property | Detail |
|---|---|
| **Depth** | 20 to 200 um, a thin layer |
| **Magnitude** | -300 to +400 MPa |
| **Measurement** | X-ray diffraction, or hole drilling |
| Stability | Relaxes at temperature, and under cyclic load |

**The layer is thin** and that is why it does not distort the part in the way quench stress does. It is also why it matters for fatigue: a crack initiates at the surface, and the surface layer is exactly where it initiates.

**Compressive residual stress delays crack initiation** by reducing the effective mean stress at the surface. That is the same mechanism shot peening uses deliberately. See [postProcessing ShotPeening.md](../../postProcessing/docs/ShotPeening.md).

**It relaxes.** At elevated temperature and under cyclic loading, machining residual stress fades, and the benefit cannot be relied on for a long-life high-temperature component the way a peened layer can.

**X-ray diffraction is the standard measurement** and it reads only the outermost few micrometres, so a depth profile needs successive electropolishing steps.

---

## White layer

**A hard, brittle, untempered martensite layer on machined steel**, visible as a white unetching band in a section.

| Cause | Detail |
|---|---|
| **Rapid heating above the austenitising temperature** | From a worn tool or an abusive cut |
| **Followed by quenching** | By the bulk material and the coolant |

| Property | Effect |
|---|---|
| Very hard | 800 to 1000 HV |
| **Brittle** | It cracks |
| **Tensile residual stress beneath it** | The layer is in compression, the material below in tension |
| **Fatigue initiation site** | Cracks form in it and propagate into the base material |

**It is a rejectable condition on any fatigue critical steel part**, and it is found by sectioning and etching or by nital etch inspection.

**The analogous condition in EDM is the recast layer**, which is resolidified melted material with a similar brittleness and a similar network of microcracks. It is removed by a subsequent abrasive or chemical operation on anything fatigue critical.

---

## Grinding burn

**Thermal damage from grinding**, and grinding is the most thermally aggressive machining process because almost all the energy goes into the workpiece rather than the chip.

| Severity | Appearance | Effect |
|---|---|---|
| Light | Temper colours | Softening, tensile stress |
| **Moderate** | **Rehardening burn** | White layer, cracking |
| Severe | Visible cracks | Rejectable |

**Nital etch inspection per AMS 2649 is the standard detection method** for steel, and it reveals both softened and rehardened regions as tonal differences.

**The controls are wheel selection, dressing frequency, coolant delivery and stock per pass**, and the commonest cause of burn is a glazed wheel that has not been dressed.

**Coolant delivery matters more in grinding than anywhere else** because the wheel carries an air boundary layer that deflects a poorly aimed coolant jet entirely. High pressure through-wheel or tangentially aimed nozzles are used.

---

## The fatigue consequence

**This is why surface integrity is worth the attention.**

| Surface condition | Fatigue factor |
|---|---|
| **Sharp tool, flood coolant** | **1.2x** |
| Sharp tool, dry | 1.05x |
| Worn tool, flood coolant | 0.85x |
| **Worn tool, dry** | **0.60x** |
| Abusive grinding with burn | Lower still |

**A factor of two between the best and worst machining condition**, on a surface that meets the same Ra specification in every case.

**A drawing that specifies Ra 1.6 and nothing else does not control any of this.** The part can be produced with a sharp tool and flood coolant, or with a worn tool running dry, and the surface finish measurement will not distinguish them.

**Fatigue critical surfaces need a process specification, not just a finish specification**: tool wear limits, coolant requirement, prohibited conditions, and an inspection for burn or white layer.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Sharp tool and coolant | -150 MPa, 1.2x fatigue |
| Worn tool dry | +300 MPa, 0.60x fatigue |
| The swing is 450 MPa | Larger than most design decisions |
| Affected depth | 20 to 200 um |
| Machining residual stress relaxes | Peening does not, as readily |
| White layer is rejectable | On fatigue critical steel |
| Ra does not control surface integrity | Specify the process |
| Nital etch per AMS 2649 | For grinding burn |

---

## Failure modes

**Ra specified and nothing else on a fatigue critical surface.** Nothing is controlled.

**Tool wear limit set on dimension alone.** The surface goes tensile first.

**Dry machining on a fatigue critical surface.** 0.60x fatigue.

**White layer left on a steel part.** A brittle cracked initiation site.

**EDM recast layer left in place.** The same problem.

**Glazed grinding wheel.** Burn.

**Machining compressive stress relied on at temperature.** It relaxes.

---

## Worked numbers

From [`MachiningProcess.assessSurfaceIntegrity`](../machiningProcessesLibrary/MachiningProcess.py):

| Condition | Residual stress | Fatigue factor |
|---|---|---|
| sharp tool, flood coolant | -150 MPa | 1.20 |
| sharp tool, dry | -50 MPa | 1.05 |
| worn tool, flood coolant | +100 MPa | 0.85 |
| **worn tool, dry** | **+300 MPa** | **0.60** |

---

## Standards

| Standard | Scope |
|---|---|
| **AMS 2649** | Etch inspection of high strength steel parts, for grinding burn |
| ASTM E837 | Residual stress by hole drilling |
| ASTM E915 | X-ray diffraction residual stress, alignment verification |
| **ANSI B211.1** | Surface integrity |
| ISO 4287 / 21920 | Surface texture parameters |
| AMS 2432 | Computer controlled shot peening |
| ASTM E1417 | Liquid penetrant testing |

---

## Tool interface

```python
from MachiningProcess import MachiningProcess, SURFACE_RESIDUAL_STRESS

machining = MachiningProcess()
machining.setInputs({'material': '17-4PH', 'condition': 'h1025',
                     'process': 'end mill', 'toolDiameter': 0.012,
                     'axialDepth': 0.005, 'radialDepth': 0.003, 'feedPerTooth': 0.0001})

for condition in SURFACE_RESIDUAL_STRESS:
    result = machining.assessSurfaceIntegrity(condition = condition)
    print(f'{condition:28s} {result["surfaceResidualStress"]/1e6:+7.0f} MPa  '
          f'fatigue x{result["fatigueFactor"]:.2f}')
```

---

## References

1. Field, M. and Kahles, J. F., "Review of Surface Integrity of Machined Components", *Annals of the CIRP*, Vol. 20, 1971.
2. Jawahir, I. S. et al., "Surface Integrity in Material Removal Processes", *CIRP Annals*, Vol. 60, 2011.
3. ASM Handbook Volume 16, *Machining*.
