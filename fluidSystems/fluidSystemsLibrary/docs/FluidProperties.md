[Home](../../README.md) > Fluid Properties

# Fluid Properties

## Contents

- [Overview](#overview)
- [The backend ladder](#the-backend-ladder)
- [Input and output type codes](#input-and-output-type-codes)
- [The sentinel trap](#the-sentinel-trap)
- [The four query modes](#the-four-query-modes)
- [Phase coding](#phase-coding)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Every component class in this library is a thin layer of geometry and correlation wrapped around a property lookup. Get the properties wrong and nothing downstream is worth anything, which makes the property layer the most load-bearing code in the repository and the least visible.

[`fluidProps`](../../../common/fluidProperties.py) is the single accessor every class calls. [`FluidView`](../FluidView.py) is the tool for looking at what it returns before committing to a design.

---

## The backend ladder

`fluidProps` dispatches in a fixed order, and which rung answers changes the fidelity of the number.

| Order | Backend | Covers | Fidelity |
|---|---|---|---|
| **1** | **Correlation table** | Species with no equation of state anywhere. Currently hydrazine | **Engineering estimate** |
| **2** | **REFPROP** | Anything with a `.FLD` file. **Mixtures** | **Reference quality** |
| **3** | **CoolProp** | Single component fluids | Very good |

**The dispatch is automatic and it is silent**, which is the point: the same call site runs on a machine with a REFPROP licence and on one without. It is also the hazard, because two engineers can get different numbers from the same code and not know why.

**`FluidView` reports which backend answered** in every result, as a finding. That is the mechanism for catching it.

**REFPROP is the only backend that does mixtures** through this interface. A `'N2;He'` species string on a CoolProp-only machine will not do what you expect.

**Hydrazine is the one species served by a correlation table**, because neither REFPROP nor CoolProp carries an equation of state for it. Its values are good enough to size a feed system and they are not reference data. See [Hydrazine.md](Hydrazine.md).

---

## Input and output type codes

**The input type is a two character code naming the two independent properties being fixed.**

| Code | Fixes | Typical use |
|---|---|---|
| **`TP`** | Temperature and pressure | **The default. Most states are specified this way** |
| `TD` | Temperature and density | Fixed volume systems |
| `PD` | Pressure and density | |
| **`PH`** | Pressure and enthalpy | **Downstream of a throttle, which is isenthalpic** |
| `PS` | Pressure and entropy | Downstream of an ideal expansion, which is isentropic |
| **`TQ`, `PQ`** | Temperature or pressure, and quality | **On the saturation line, where `TP` is degenerate** |

**`TP` does not work on the saturation line** and that is the single most common input-code mistake. At the saturation pressure a fluid can be liquid, vapour or anything between, so temperature and pressure together do not specify the state. Use `TQ` or `PQ` there.

**Output types are a space delimited string of labels.** `PROPERTY_LABELS` in [`FluidView`](../FluidView.py) maps readable names onto them, so `'density'` and `'D'` both work.

| Readable | Label | Unit |
|---|---|---|
| density | `D` | kg/m^3 |
| viscosity | `VIS` | Pa*s |
| thermal conductivity | `TCX` | W/m/K |
| speed of sound | `W` | m/s |
| specific heat cp | `CP` | J/kg/K |
| gamma | `CP/CV` | - |
| enthalpy | `H` | J/kg |
| entropy | `S` | J/kg/K |
| phase | `PHASE` | a string, not a number |

**Viscosity is dynamic, not kinematic.** That is worth stating because the Reynolds number relation in [`utils`](../utils.py) takes dynamic viscosity, and a kinematic value silently gives a Reynolds number wrong by the density.

**Enthalpy and entropy reference states are backend dependent.** Absolute values are not comparable across backends; differences are.

---

## The sentinel trap

**REFPROP does not raise on a failed lookup. It returns a large negative number.**

```
REFPROP_ERROR_SENTINEL = -9.0e6
```

A request for a species that is not installed, or a state point outside the equation of state's range, comes back as roughly `-9999990.0` and is a perfectly ordinary float as far as Python is concerned.

**The consequences are quiet and bad.** A carpet plot with one bad corner has a spike to minus ten million in it. A wall thickness calculation fed a negative density produces a negative wall and a `sqrt` of a negative number several functions later, and the traceback points nowhere near the property call.

**Every `FluidView` query is checked against the sentinel** and converts it into a `CompatibilityError` naming the species and the state point that failed. That check is the single most useful thing the class does, and any code calling `fluidProps` directly should do the same.

---

## The four query modes

| Mode | Sweeps | Returns | Cost |
|---|---|---|---|
| **Single point** | Nothing | One value per property | 1 call |
| **Range sweep** | First input | One array per property | `n` calls |
| **Carpet plot** | Both inputs | One 2D grid per property | `n x m` calls |
| **Phase diagram** | Both, as `TP` | An integer coded phase field | `n x m` calls |

**Cost is the thing to watch.** Backend calls do not vectorise through REFPROP, so a carpet plot is a genuine double loop and a 500 by 500 grid is a quarter of a million calls.

**`MAXIMUM_GRID_POINTS` guards against that** at 250,000, raising rather than running for an hour. Coarsen the ranges, or raise the constant deliberately.

**The grid is indexed `[firstRange, secondRange]`**, so `grid[i, j]` is the property at `firstRange[i]` and `secondRange[j]`. That ordering matters when handing the array to a contour plot, which conventionally wants the transpose.

---

## Phase coding

A phase query returns a string, and a contour plot needs a number, so the strings are mapped onto integers.

| Phase | Code |
|---|---|
| Unrecognised | **0** |
| Subcooled liquid | 1 |
| Superheated gas | 2 |
| Supercritical | 3 |
| Two-phase | 4 |

**The ordering is not physically meaningful.** It exists so adjacent fields get adjacent contour levels, nothing more. Do not do arithmetic on it.

**Code 0 means the backend reported a phase name not in the table**, which is reported as a finding rather than being silently swallowed.

**A phase diagram whose grid is entirely one phase is reported as a finding too**, because the usual cause is bounds that do not straddle a phase boundary, and a chart of one uniform colour looks like a working chart.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| `fluidProps` dispatches correlation, then REFPROP, then CoolProp | Silently |
| Check which backend answered | It changes the fidelity |
| Mixtures need REFPROP | CoolProp cannot do them here |
| `TP` fails on the saturation line | Use `TQ` or `PQ` |
| Viscosity is dynamic | Not kinematic |
| Enthalpy and entropy references are backend dependent | Differences only |
| **Check every result against the sentinel** | REFPROP does not raise |
| Carpet plots are `n x m` calls | They do not vectorise |
| Phase codes are labels, not quantities | No arithmetic |

---

## Failure modes

**Sentinel plotted as data.** A spike to minus ten million, or a negative density propagating into a wall thickness.

**`TP` used on the saturation line.** The state is not specified and the answer is whichever side the solver landed on.

**Mixture requested without REFPROP.** Not what you asked for.

**Hydrazine values quoted as reference data.** They are a correlation table.

**Kinematic viscosity supplied where dynamic was wanted.** Reynolds number wrong by the density.

**Enthalpies compared across backends.** Different reference states.

**Carpet plot sized without thinking about the call count.** A quarter of a million lookups.

**Grid handed to a contour plot without transposing.** The axes are swapped and the chart looks plausible.

---

## Standards

| Standard | Scope |
|---|---|
| **NIST REFPROP** | Reference fluid thermodynamic and transport properties |
| CoolProp | Open source equation of state library |
| IAPWS-IF97 | Water and steam properties |
| ISO 6976 | Calculation of calorific values and density from composition |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'fluidSystems/fluidSystemsLibrary')

import numpy as np
from FluidView import FluidView, listAvailableFluids

print(listAvailableFluids()['refpropInstalled'])

# a single state point
view = FluidView()
view.setInputs({'species': 'N2', 'inputTypes': 'TP',
                'outputTypes': ['density', 'viscosity', 'speed of sound'],
                'firstValue': 300.0, 'secondValue': 5.0e6})
result = view.calculateSinglePoint()
for label, value in result['properties'].items():
    print(f'  {label:6s} {value:12.6g} {result["units"][label]}')

# the phase field, integer coded for contouring
phase = FluidView()
phase.setInputs({'species': 'N2', 'inputTypes': 'TP', 'outputTypes': ['phase'],
                 'firstRange': np.linspace(70.0, 200.0, 6),
                 'secondRange': np.linspace(1.0e5, 5.0e6, 6)})
field = phase.calculatePhaseDiagram()
print(field['phasesPresent'])
print(field['phaseCodes'])
```

---

## References

1. Lemmon, E. W., Bell, I. H., Huber, M. L. and McLinden, M. O., *NIST Reference Fluid Thermodynamic and Transport Properties Database (REFPROP), Version 10.0*, NIST, 2018.
2. Bell, I. H. et al., "Pure and Pseudo-pure Fluid Thermophysical Property Evaluation and the Open-Source Thermophysical Property Library CoolProp", *Industrial and Engineering Chemistry Research*, Vol. 53, 2014.
3. Poling, B. E., Prausnitz, J. M. and O'Connell, J. P., *The Properties of Gases and Liquids*, 5th ed., McGraw-Hill, 2001.
