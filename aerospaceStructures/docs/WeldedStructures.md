[Home](../README.md) > Welded Structures

# Welded Structures

## Contents

- [Overview](#overview)
- [Joint efficiency](#joint-efficiency)
- [The HAZ is the weak point](#the-haz-is-the-weak-point)
- [Friction stir welding](#friction-stir-welding)
- [Weld lands](#weld-lands)
- [Residual stress and distortion](#residual-stress-and-distortion)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A welded tank is a structure with a designed-in strength discontinuity running around and along it. The metallurgy is covered in [aerospaceMaterials joiningProcesses](../../aerospaceMaterials/joiningProcesses/); this document is about what the weld does to the structure.

---

## Joint efficiency

**A multiplier on the parent allowable, applied at the joint.**

| Joint | Efficiency |
|---|---|
| **Parent material** | 1.00 |
| Full penetration butt, austenitic stainless | 0.90 to 1.00 |
| **Full penetration butt, 2219** | **0.70** |
| **Fusion weld, 6061-T6** | **0.50** |
| **Friction stir weld, 2219** | **0.80 to 0.90** |
| Fillet weld | 0.55 to 0.70 |
| Partial penetration | Proportional, and worse |

**The efficiency divides the wall thickness.** A 2219 tank at 0.70 needs its membrane wall increased by 43 percent, which is a large and often overlooked mass.

**Austenitic stainless barely loses anything** because it has no precipitates to overage. Heat treatable aluminium loses half. That asymmetry drives a great deal of design: a stainless weldment can be designed near parent strength and an aluminium one cannot.

---

## The HAZ is the weak point

**Not the weld metal.** The fusion zone is usually overmatched by filler selection. The heat affected zone beside it is parent material that was heated enough to overage and not enough to melt, and nothing in the welding process prevents it.

**6061-T6 as-welded yields around 138 MPa against 276 in the parent**, a 50 percent knockdown, and that number is shared with [`Weld.HAZ_KNOCKDOWN`](../../fluidSystems/fluidSystemsLibrary/Weld.py) in fluidSystems. A cross-domain test asserts the two agree, so the same physical number cannot drift between the domains that use it.

**The HAZ width scales with heat input**, which is the argument for electron beam and laser welding: a narrower HAZ means a smaller fraction of the structure is knocked down.

**Post-weld solution treatment and ageing would recover it** and is impractical on most large structures. That is why the knockdown is treated as permanent.

---

## Friction stir welding

**Solid state, so there is no solidification and none of its problems.**

| Fusion problem | FSW |
|---|---|
| Hot cracking | **None.** Nothing solidifies |
| Porosity from dissolved gas | None |
| Cast fusion zone structure | Replaced by fine recrystallised grain |
| Filler and dilution | No filler |

**It welds 7075 and 2024, which fusion cannot.** That single capability opened high strength aluminium to welded construction and is why FSW became the launch vehicle tank process.

**The HAZ is still the weak point.** FSW removes the fusion zone problems and does not remove the overageing beside the weld. It is narrower, because the heat input is lower, which is where most of the efficiency gain comes from.

**Repeatability is a machine property rather than an operator one.** A qualified FSW schedule produces the same weld every time, which a manual GTAW weld does not.

---

## Weld lands

**A local thickening at the weld, so the joint efficiency applies to a thicker section.**

| Reason | Detail |
|---|---|
| **Restore the knocked-down strength** | Thicker section at the reduced allowable |
| **Provide material for the tool** | FSW needs a shoulder bearing surface |
| **Accommodate mismatch** | Fit-up tolerance |
| Allow for weld repair | A second pass removes material |

**A land is not free.** It adds mass exactly where the structure is already heaviest, and it creates a stiffness discontinuity that concentrates stress at its runout. The runout radius is a real design detail.

**Machining a land into a barrel means machining the whole barrel down to the membrane thickness around it**, which is why integrally machined and land-inclusive barrels are the norm on modern vehicles: the land is what is left, not what is added.

---

## Residual stress and distortion

| Effect | Consequence |
|---|---|
| **Longitudinal shrinkage** | Along the weld |
| **Transverse shrinkage** | Across it, pulls the joint closed |
| **Angular distortion** | More shrinkage at the top of a groove than the root |
| **Buckling distortion** | Thin sheet, from compressive residual stress |
| **Residual tension at the weld** | Adds to the applied stress, and drives SCC |

**Restraint trades distortion for residual stress.** A heavily fixtured weld comes out straight and highly stressed, and that stress reappears later as distortion when material is machined off, or as a stress corrosion driver in service.

**A circumferential weld in a cylinder pulls the diameter in locally**, producing an inward imperfection ring. That is a geometric imperfection in exactly the structure whose buckling is imperfection sensitive, which is one of the reasons real shells fall short of theory.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Efficiency divides the wall | 0.70 is a 43 % increase |
| 6061-T6 as-welded | 138 MPa, half the parent |
| Austenitic stainless welds near parent | No precipitates to lose |
| FSW for high strength aluminium | 0.80 to 0.90 |
| The HAZ is the weak point, not the weld metal | |
| Narrower HAZ means less knockdown | EBW, LBW, FSW |
| A weld shrinks the local diameter | An imperfection where it matters |
| Full penetration for pressure boundaries | Inspectability |

---

## Failure modes

**As-welded aluminium designed at parent strength.** Half the actual capability.

**Joint efficiency omitted from the wall sizing.** 30 to 40 percent thin.

**Partial penetration in a pressure boundary.** Cannot be volumetrically inspected.

**7075 fusion welded.** Hot cracking. FSW is the route.

**Weld land runout with a sharp step.** Stress concentration at the discontinuity.

**Weld shrinkage imperfection ignored in the buckling analysis.** It is exactly the imperfection that matters.

**Residual stress released by later machining.** Distortion after final inspection.

---

## Worked numbers

From the worked example, 2219-T87 at 0.70 joint efficiency:

| Quantity | Value |
|---|---|
| A-basis Fty | 345.0 MPa |
| Effective allowable at the joint | 241.5 MPa |
| **Wall increase over seamless** | **43 %** |
| Stage tank wall at 0.70 | 22.59 mm |
| Stage tank wall at 1.00 | 15.81 mm |

**Nearly 7 mm of wall on a 1.8 m radius tank is bought by the weld**, which on a 6 m barrel is a substantial mass.

---

## Standards

| Standard | Scope |
|---|---|
| **AWS D17.1** | Fusion welding for aerospace applications |
| **AWS D17.3** | Friction stir welding for aerospace |
| NASA-STD-5006 | General welding requirements |
| AMS 2680 / 2681 | Electron beam welding |
| ASME BPVC Section IX | Welding qualification |
| ASTM E1417 / E2700 | Penetrant and phased array ultrasonic |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../fluidSystems/fluidSystemsLibrary')

from Weld import Weld

# Weld reads the nine-alloy seed table in common, not the aerospaceMaterials database,
# so these are the alloys it knows.
for material in ('6061-T6', '316L', 'INCONEL 718'):
    weld = Weld()
    weld.setInputs({'material': material, 'jointType': 'butt full penetration',
                    'outerDiameter': 0.050, 'wallThickness': 0.003})
    result = weld.calculateDerating()
    print(f'{material:10s} efficiency {result["jointEfficiency"]:.2f}  '
          f'HAZ yield factor {result["hazYieldFactor"]:.2f}')
```

---

## References

1. AWS D17.1, *Specification for Fusion Welding for Aerospace Applications*.
2. Mishra, R. S. and Ma, Z. Y., "Friction Stir Welding and Processing", *Materials Science and Engineering R*, Vol. 50, 2005.
3. Kou, S., *Welding Metallurgy*, 2nd ed., Wiley, 2003.
