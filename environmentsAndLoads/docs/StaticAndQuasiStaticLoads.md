[Home](../README.md) > Static and Quasi-Static Loads

# Static and Quasi-Static Loads

## Contents

- [Overview](#overview)
- [What a load factor actually is](#what-a-load-factor-actually-is)
- [The flight events](#the-flight-events)
- [Combination](#combination)
- [What a load factor does not describe](#what-a-load-factor-does-not-describe)
- [Ground handling](#ground-handling)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A quasi-static load factor collapses a whole dynamic environment into a single acceleration that structure can be sized against without a transient analysis. It is a convenience, it is an approximation, and knowing which parts are which is the entire subject.

---

## What a load factor actually is

**Not the trajectory acceleration.**

```
quasi-static factor = steady acceleration + dynamic amplification of the transient
```

**A 3 g liftoff event can present as 5 g to a structure**, because the hold-down release transient rings the vehicle and the structure responds at its own frequency. Taking the trajectory acceleration as the load factor understates the load, and the error is invisible because both numbers are plausible.

**Keeping the split visible is worth doing.** A factor that is mostly steady is well represented as quasi-static; a factor that is mostly dynamic is not, and it is a signal that a transient analysis is required instead.

| Event | Axial | Steady | Dynamic share |
|---|---|---|---|
| Max acceleration | 6.0 g | 5.7 g | **5 %** |
| Liftoff | 3.0 g | 1.2 g | 60 % |
| **Staging** | 1.7 g | 0.2 g | **88 %** |

**Staging at 88 percent dynamic is barely a quasi-static event at all.** Representing it as one is a modelling choice that should be made deliberately.

---

## The flight events

| Event | Axial | Lateral | Character |
|---|---|---|---|
| **Ground handling** | 1.2 g | 0.5 g | **Unpressurized.** Crane, transport, erection |
| **Liftoff** | 3.0 g | 1.0 g | Hold-down release transient |
| **Max-Q** | 2.5 g | **2.2 g** | Gust and buffet. Highest lateral |
| **Max acceleration** | **6.0 g** | 0.3 g | End of burn, lowest mass |
| Staging | 1.7 g | 0.6 g | Near freefall plus separation transient |
| **Landing** | 4.0 g | 1.5 g | Reusable stages. Touchdown |

**Max acceleration is highest in axial because the stage is nearly empty.** The same thrust acting on a much smaller mass gives the peak acceleration of the flight, at the moment the structure is least loaded by propellant.

**Max-Q is highest in lateral** and only moderate in axial. Neither event bounds the other, which is why both are run.

**Ground handling is the only unpressurized case** and it is the one most often skipped. For a pressure-stabilized structure it governs stability outright. See [aerospaceStructures ShellBuckling](../../aerospaceStructures/docs/ShellBuckling.md).

---

## Combination

| Method | Form | When |
|---|---|---|
| **Vector** | `sqrt(axial^2 + lateral^2)` | Both peak together. The physical answer |
| **Elliptical** | `(a/A)^2 + (l/L)^2 <= 1` | The peaks are not simultaneous |
| Algebraic | `axial + lateral` | Very conservative, rarely justified |

**Axial and lateral do not occur independently**, so taking the worst of each and applying them together is an envelope of a condition that never occurs.

**The governing combination is frequently not the largest single component.** Whether it is depends on the numbers, and reporting both is the honest output: a set where they agree is as informative as one where they do not.

---

## What a load factor does not describe

**This is the most consequential limitation and it is routinely lost.**

**A load factor applies at the centre of mass of an item.** It describes the inertial load on that item as a rigid body.

**It says nothing about what a component mounted on a flexible panel sees.** The panel amplifies, and the amplification at the component's own resonance can be a factor of ten or more.

| Question | Answered by |
|---|---|
| What inertial load does this 200 kg box impose on its mounts? | **Load factor** |
| What does a connector on the box's circuit card see? | **Random vibration** |
| What does the box see when the separation nut fires? | **Shock** |

**Conflating the first and second is a real source of under-test.** A component qualified to a 6 g quasi-static load and mounted on a panel with a 200 Hz resonance in a 0.08 g^2/Hz field sees far more than 6 g, and the load factor never said otherwise.

---

## Ground handling

**The unglamorous case that catches programmes.**

| Source | Character |
|---|---|
| **Crane lift** | Sling angles produce compression in unexpected members |
| **Transport** | Road and rail shock, often the worst vibration the hardware sees |
| **Erection** | The vehicle rotated from horizontal to vertical |
| Wind on the pad | Sustained lateral load, unpressurized |

**Transport vibration is frequently more severe than flight** for hardware shipped by road, and it lasts orders of magnitude longer. It is also the environment least likely to have been derived, because it is somebody else's problem until it is not.

**Erection loads a vehicle in a direction it never sees in flight.** A structure optimised for axial compression is being asked to act as a beam in bending across its whole length.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Load factor = steady + dynamic amplification | Not trajectory acceleration |
| Keep the split visible | A mostly dynamic factor needs a transient analysis |
| Max acceleration is highest axial | Lowest mass, not highest thrust |
| Max-Q is highest lateral | Neither bounds the other |
| Vector combination when peaks coincide | Elliptical when they do not |
| A load factor applies at the centre of mass | Not at a component on a panel |
| Ground handling is the unpressurized case | And often skipped |
| Transport can exceed flight | And lasts far longer |

---

## Failure modes

**Trajectory acceleration used as the load factor.** Understates by the dynamic amplification.

**A load factor applied to a component on a flexible panel.** The panel amplifies and the factor never said otherwise.

**Worst axial and worst lateral applied together.** An envelope of a condition that never occurs.

**Ground handling skipped.** The only unpressurized case.

**Transport treated as somebody else's problem.** Often the worst environment the hardware sees.

**An 88 percent dynamic event represented quasi-statically.** It is a transient.

---

## Worked numbers

From [`LoadFactorSet`](../environmentsAndLoadsLibrary/LoadFactorSet.py), vector combination:

| Event | Axial | Lateral | Combined | Dynamic |
|---|---|---|---|---|
| ground handling | 1.20 | 0.50 | 1.30 | 17 % |
| liftoff | 3.00 | 1.00 | 3.16 | 60 % |
| max-Q | 2.50 | 2.20 | 3.33 | 48 % |
| **max acceleration** | **6.00** | 0.30 | **6.01** | 5 % |
| staging | 1.70 | 0.60 | 1.80 | **88 %** |
| landing | 4.00 | 1.50 | 4.27 | 62 % |

**Max acceleration governs both by axial factor and by combination for this set**, which is worth stating because it is not always the case and the class reports both.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-5001** | Structural design and test factors of safety |
| **NASA-STD-5002** | Load analyses of spacecraft and payloads |
| MIL-STD-1540 | Test requirements |
| ECSS-E-ST-32-10 | Structural factors of safety |
| Launch vehicle user guides | The authoritative source for a given vehicle |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'environmentsAndLoadsLibrary')

from LoadFactorSet import LoadFactorSet

factors = LoadFactorSet()
factors.setInputs({'mass': 500.0, 'combinationMethod': 'vector'})
factors.addStandardEvents()

result = factors.identifyGoverning()
for name, entry in result['combined'].items():
    print(f'{name:18s} combined {entry["combined"]:5.2f} g  '
          f'dynamic {entry["dynamicShare"] * 100.0:5.1f} %')

for finding in result['findings']:
    print(finding)
```

---

## References

1. NASA-STD-5002A, *Load Analyses of Spacecraft and Payloads*.
2. Wijker, J. J., *Spacecraft Structures*, Springer, 2008.
3. Sarafin, T. P., *Spacecraft Structures and Mechanisms*, Microcosm, 1995.
