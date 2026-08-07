[Home](../README.md) > Process Qualification

# Process Qualification

## Contents

- [Overview](#overview)
- [What gets qualified](#what-gets-qualified)
- [Establishing the removal coefficient](#establishing-the-removal-coefficient)
- [First article](#first-article)
- [Production control](#production-control)
- [What counts as a change](#what-counts-as-a-change)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Abrasive flow machining is a process with no direct measurement of its output on the finished part, which puts the entire weight of assurance on process control. That is the same position additive manufacturing is in, and for the same reason.

---

## What gets qualified

| Element | Content |
|---|---|
| **Media** | Grade, abrasive type, batch, viscosity, replacement interval |
| **Parameters** | Pressure, cycle count, temperature, flow direction sequence |
| **Fixture** | Drawing, serial number, restrictor sizes, seal condition |
| **Sequence** | Depowder, hone, clean, inspect, in that order |
| **Cleaning** | Media removal is a process step with its own verification |
| **Operators** | Trained and current |

**The fixture is part of the qualified process**, and a fixture change is a process change. A worn seal or an eroded restrictor changes the flow split and therefore the result.

---

## Establishing the removal coefficient

The removal model is empirical:

```
deltaR = C * tau_w^1.15 * N^0.85
```

**`C` is material, media and geometry specific and it has to be measured.** Taking it from a table produces a number with no relationship to the part.

**The procedure:**

1. Coupons of the part material, with passages representative of the part geometry
2. Honed at a matrix of pressure and cycle count
3. Sectioned, and both removal and roughness measured directly
4. `C` fitted, and the finish decay constant with it
5. Confirmed on a first article

**Representative geometry is the requirement people compromise.** A straight 10 mm bore is easy to make and to section, and it does not represent a 4 mm passage with two bends. The coefficient fitted on the easy coupon over-predicts the removal in the real part, because the real part has lower wall shear at the same pressure.

---

## First article

| Step | Purpose |
|---|---|
| Build or make the part to the drawing | The real geometry |
| Measure before honing | Bore size, flow, and roughness where accessible |
| Hone to the qualified parameters | |
| Measure after | The change is what is being qualified |
| **Section it** | The only way to see the middle of the passage |
| Compare against the coupon prediction | Confirms the coefficient transfers |

**Sectioning the first article is the point of having one.** A first article that is delivered rather than cut up has confirmed dimensions and nothing about the internal surface.

---

## Production control

| Control | Frequency |
|---|---|
| Media viscosity | Per batch, and periodically in use |
| Media replacement | On a schedule tied to throughput |
| Temperature | Every run, recorded |
| Flow rate | Every run, recorded and trended |
| Pressure and cycles | Every run, from the machine record |
| Fixture condition | Periodically, and after any leak |
| Flow test of the part | Every part, against the qualified reference |
| Witness passage | Per lot, sectioned |

**Flow rate trending is the cheapest and most informative control.** A gradual fall means the media is loading or the temperature is drifting; a step change means something broke.

---

## What counts as a change

| Change | Requalify |
|---|---|
| Media grade or abrasive | Yes |
| **Media batch from a different supplier** | Yes |
| Pressure or cycle count | Yes |
| Fixture, including a repaired seal | Yes |
| Part material or condition | Yes |
| **Part geometry, including an upstream additive parameter change** | Yes |
| Machine | Yes |
| Operator | No, if trained and current |

**The upstream one is the one that surprises people.** An additive parameter change that alters the as-built roughness changes the honing starting point, so the same honing cycle produces a different result. **A change in one sub-domain propagates into the other**, and a change control system that treats them separately misses it.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Removal coefficient | Measured, not tabulated |
| Coupons must be representative | Same size, same bends |
| Section the first article | Or it proved nothing |
| Trend the flow rate | Cheapest available control |
| Media replacement on a schedule | Not on judgement |
| The fixture is part of the process | A seal repair is a change |
| An upstream additive change is a change here | Change control has to span both |

---

## Failure modes

**Removal coefficient from a table.** No relationship to the part.

**Coupons of convenient geometry.** Over-predicts the removal.

**First article delivered rather than sectioned.** Nothing learned about the surface.

**Media replaced on judgement.** Drift nobody records.

**Fixture seal repaired without requalification.** The flow split changed.

**Additive parameters changed upstream.** The honing starting point moved.

---

## Standards

| Standard | Scope |
|---|---|
| **AS9100** | Quality management for aviation, space and defence |
| NASA-STD-6030 | Additive manufacturing requirements |
| MSFC-SPEC-3717 | Control and qualification of LPBF processes |
| ISO 4287 / 21920 | Surface texture |
| ASTM F3335 | Assessing removal of additive residues |
| MIL-STD-1520 | Corrective action and disposition of nonconforming material |

---

## Tool interface

```python
from ExtrusionHoning import ExtrusionHoning, REMOVAL_COEFFICIENT

# The coefficient is a module constant precisely so it can be replaced by a fitted value
print(REMOVAL_COEFFICIENT)

# The prediction a first article is compared against
honing = ExtrusionHoning()
honing.setInputs({'passageDiameter': 0.00476, 'passageLength': 0.180,
                  'material': 'Inconel 718', 'condition': 'lpbf hip + sta',
                  'extrusionPressure': 7.0e6, 'cycleCount': 12})
honing.calculateWallShear()
print(honing.calculateRemoval()['radialRemoval'])
```

---

## References

1. AS9100D, *Quality Management Systems for Aviation, Space and Defense Organizations*.
2. NASA-STD-6030, *Additive Manufacturing Requirements for Spaceflight Systems*.
3. Jain, V. K. and Adsul, S. G., "Experimental Investigations into Abrasive Flow Machining", *International Journal of Machine Tools and Manufacture*, Vol. 40, 2000.
