[Home](../README.md) > Mass Properties and Optimization

# Mass Properties and Optimization

## Contents

- [Overview](#overview)
- [Why structural mass matters so much](#why-structural-mass-matters-so-much)
- [Mass estimating relationships](#mass-estimating-relationships)
- [The sizing loop](#the-sizing-loop)
- [Structural efficiency](#structural-efficiency)
- [Where the mass actually is](#where-the-mass-actually-is)
- [Mass growth](#mass-growth)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Mass is the objective function. A structure that is adequate and heavy has failed at its job, and on a launch vehicle the exchange rate between structural mass and payload is close to one to one on the upper stage.

---

## Why structural mass matters so much

**The rocket equation is unforgiving of dry mass.**

```
dV = Isp g ln(m_initial / m_final)
```

**Structural mass sits in `m_final` on every stage**, so it is carried through the entire burn. An upper stage's dry mass trades against payload roughly one for one; a first stage's trades at perhaps one to ten.

**That asymmetry drives where effort goes.** A kilogram saved on the upper stage is worth ten saved on the booster, and the analysis effort should follow.

**It also explains the domain's design ethos.** Buckling knockdowns of 0.3 are not conservatism to be shrugged at; they triple the wall on the structure that carries them, and finding a way to avoid them is worth real effort.

---

## Mass estimating relationships

**Early sizing uses correlations against historical vehicles, because there is no design to weigh yet.**

| Structure | Typical relation |
|---|---|
| **Tank** | Mass per unit volume, or per unit wetted area |
| **Skirt and interstage** | Mass per unit surface area |
| **Thrust structure** | Fraction of engine thrust |
| Whole stage | Propellant mass fraction |

**Propellant mass fraction is the headline number.** A good aluminium stage reaches 0.90 to 0.94; a very good one exceeds 0.95. That single figure carries the whole structural design and it is what a conceptual design trades against.

**MERs are correlations, not physics.** They interpolate within the design space they were fitted to and mislead outside it. A composite stage, a pressure-stabilized stage or an unusually short and fat one are all outside the space most published MERs cover.

**They are useful precisely because they are early.** By the time a real mass estimate exists, the architecture is fixed and the leverage is gone.

---

## The sizing loop

**Structural sizing is not a single pass, because the loads depend on the mass and the mass depends on the loads.**

| Step | Detail |
|---|---|
| **1** | Assume a structural mass fraction |
| **2** | Compute the loads from the mass and the trajectory |
| **3** | Size the structure against those loads |
| **4** | Compute the resulting mass |
| **5** | Compare against the assumption and iterate |

**It converges, and the direction matters.** Underestimating the mass gives loads that are too low, which gives a structure that is too light, which reinforces the error. Starting from a conservative assumption converges from the safe side.

**A tank's wall does not participate.** Pressure sizing is independent of the vehicle mass, which is why the worked example's tanks are the same `R/t` at both scales. Only the dry structure participates in the loop.

---

## Structural efficiency

**Comparing structural concepts fairly requires an equal-mass comparison, not an equal-thickness one.**

| Concept | Typical gain over equal-mass monocoque |
|---|---|
| **Sandwich panel** | **100 to 400x in bending stiffness** |
| **Stiffened panel** | **2 to 4x in buckling allowable** |
| Pressure stabilized | Up to the classical allowable |
| Composite | Material property gain, less than the raw ratio |

**A stiffened panel that carries less than an equal-mass skin is a worse design that took more machining**, and that outcome is possible with badly proportioned stiffeners. Making the comparison is one line of code.

**Sandwich wins on bending stiffness by an enormous margin and loses on point loads.** Every attachment needs an insert, and that is where the mass the core saved comes back.

**The right comparison is at the panel level with all its details**, not at the idealised section. A sandwich panel with forty inserts is not 375x anything.

---

## Where the mass actually is

**Not usually in the membrane.**

| Element | Character |
|---|---|
| **Joints and fittings** | Discrete, heavy, and numerous |
| **Load introduction** | Rings, longerons, doublers, pads |
| **Weld lands** | Local thickening around every seam |
| **Y-rings** | Substantial forgings |
| Minimum gauge | Where the analysis says less than the shop can build |
| **Non-optimum factor** | 15 to 30 percent over the theoretical structure |

**The non-optimum factor is the honest admission** that a real structure weighs 15 to 30 percent more than the sum of its analysed members. It covers fasteners, sealant, tolerance, manufacturing minimums and the details that never appear in a sizing calculation.

**Minimum gauge governs more area than people expect.** Large lightly loaded areas are set by handling damage, manufacturability and minimum machinable wall, not by stress.

---

## Mass growth

**Structural mass grows through a programme, reliably and predictably.**

| Phase | Typical growth allowance |
|---|---|
| Conceptual | 20 to 30 percent |
| Preliminary design | 10 to 15 percent |
| Detailed design | 5 to 10 percent |
| Qualification | 2 to 5 percent |

**Carrying an explicit allowance is the discipline**, because the growth is real and pretending otherwise means it appears as a schedule problem instead of a mass one.

**Growth comes from detail, not from error.** Brackets nobody drew, fasteners nobody counted, and requirements that arrived late. The analysed members rarely grow much.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Upper stage dry mass trades ~1:1 with payload | First stage ~1:10 |
| Propellant mass fraction | 0.90 to 0.94 good, >0.95 very good |
| MERs interpolate, they do not extrapolate | |
| Start the sizing loop conservative | It converges from the safe side |
| Compare concepts at equal mass | Not equal thickness |
| Non-optimum factor | 15 to 30 percent |
| Carry an explicit growth allowance | The growth is real |
| Minimum gauge governs large areas | Not stress |

---

## Failure modes

**Concepts compared at equal thickness.** Meaningless.

**MER used outside its fitted design space.** Composite, pressure stabilized or unusual geometry.

**Sizing loop started optimistic.** Converges from the unsafe side.

**Non-optimum factor omitted.** The estimate is 20 percent light by construction.

**No growth allowance.** The growth arrives as a schedule problem.

**Sandwich stiffness quoted at the idealised section.** The inserts are not in it.

**Effort spent on booster mass instead of upper stage.** Ten times less leverage.

---

## Standards

| Standard | Scope |
|---|---|
| **AIAA S-120** | Mass properties control for space systems |
| MIL-STD-1811 | Mass properties control for space vehicles |
| NASA-STD-5001 | Structural design and test factors |
| SAWE RP A-3 | Mass properties control, recommended practice |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'aerospaceStructuresLibrary')

from PressureVessel import PressureVessel
from StiffenedPanel import StiffenedPanel

tank = PressureVessel()
tank.setInputs({'material': '2219-T87', 'condition': 't87', 'basis': 'A',
                'radius': 1.80, 'cylindricalLength': 6.0,
                'jointEfficiency': 0.70, 'operatingPressure': 2.4249e6})
tank.thickness = tank.sizeWallThickness()['requiredThickness']

geometry = tank.calculateVolumeAndMass()
print(f'shell mass {geometry["shellMass"]:.1f} kg for '
      f'{geometry["totalVolume"]:.2f} m^3')
print(f'mass per volume {geometry["massPerVolume"]:.2f} kg/m^3')
```

---

## References

1. AIAA S-120A, *Mass Properties Control for Space Systems*.
2. Humble, R. W., Henry, G. N. and Larson, W. J., *Space Propulsion Analysis and Design*, McGraw-Hill, 1995.
3. Society of Allied Weight Engineers, *Recommended Practice A-3*.
