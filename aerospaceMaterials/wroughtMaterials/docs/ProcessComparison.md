[Home](../README.md) > Process Comparison

# Process Comparison

## Contents

- [Overview](#overview)
- [The allowable ladder](#the-allowable-ladder)
- [Why wrought is the baseline](#why-wrought-is-the-baseline)
- [The comparison](#the-comparison)
- [When wrought loses](#when-wrought-loses)
- [Design rules of thumb](#design-rules-of-thumb)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Every process route in this domain is measured against wrought material, and the measurement is a multiplier on the allowable. Collecting those multipliers in one place is the most useful thing this document does.

---

## The allowable ladder

| Route | Allowable multiplier | Basis |
|---|---|---|
| **Wrought, L orientation** | **1.00** | The baseline |
| Wrought, LT | 0.95 to 1.00 | |
| **Wrought, ST** | **0.90 strength, 0.10 to 0.30 SCC** | See [GrainDirection.md](GrainDirection.md) |
| **Forged** | **1.00**, with better grain flow | Not a knockdown, an improvement in direction |
| Flow formed | 1.00 or better | Cold work, once qualified |
| **As-welded, aluminium** | **0.50** | HAZ overageing |
| As-welded, austenitic stainless | 0.90 to 1.00 | No precipitates to lose |
| **Cast, qualified** | **1.00** | Factor 1.0 |
| Cast, documented process | 0.752 | Factor 1.33 |
| **Cast, default** | **0.50** | **Factor 2.0** |
| **LPBF, HIP, XY** | 0.95 to 1.00 | With a qualified process |
| **LPBF, HIP, Z** | 0.85 to 0.95 | Build direction |
| LPBF, as-built | 0.70 or lower | Plus surface roughness debit |

**Two routes sit at 0.50 and they are the two that most often surprise people**: an unqualified casting and an as-welded heat treatable aluminium joint.

**The as-welded aluminium number is the one that catches designers**, because the weld is a small part of the structure and the knockdown applies at exactly the location the structure is most likely to be critical.

---

## Why wrought is the baseline

| Reason | Detail |
|---|---|
| **The grain structure is worked** | Elongated grains, closed porosity, broken up inclusions |
| **The processing is uniform** | The whole plate saw the same rolling and the same quench |
| **The statistics are enormous** | Decades of production, tens of thousands of lots |
| **MMPDS is built on it** | The allowables are statistical, from real production data |

**The statistical basis is the underrated reason.** An A-basis allowable requires a sample of at least 100 from at least 10 lots to be credible, and wrought material has that from routine production. A new casting process or a new additive process does not, which is why their knockdowns are as much about uncertainty as about the material.

**That also explains why the knockdowns shrink over time.** LPBF IN718 allowables today are far better than they were a decade ago, and the alloy has not changed.

---

## The comparison

For an 8 kg moderately complex part:

| Route | Buy-to-fly | Allowable | Lead | Cost | Tolerance |
|---|---|---|---|---|---|
| **Machined from plate** | 8.0 : 1 | **1.00** | **12 wk** | 1.0 | **IT7** |
| Forged and machined | 4.0 : 1 | **1.00** | 24 wk | 1.8 | IT7 |
| Ring rolled and machined | 3.0 : 1 | 1.00 | 18 wk | 1.4 | IT9 |
| Formed sheet, welded | 1.3 : 1 | **0.50 at the weld** | 10 wk | 0.8 | IT11 |
| Investment cast | 1.6 : 1 | 0.50 to 1.00 | 20 wk | 1.2 | IT11 |
| **LPBF** | **1.4 : 1** | 0.85 to 1.00 | 10 wk | 3.2 | IT8 |

**Wrought routes hold the allowable and lose the buy-to-fly.** Near net shape routes do the opposite. That is the trade in one sentence.

---

## When wrought loses

| Condition | Better route |
|---|---|
| **Complex internal geometry** | Additive or casting |
| **Very high buy-to-fly on an expensive alloy** | Near net shape |
| **Quantity with a stable design** | Forging or casting |
| Very large thin structure | Formed and welded |
| Integral cooling channels | Additive |
| A bimetallic cylinder | Centrifugal casting |

**The buy-to-fly argument is alloy dependent** and it is the one most often made carelessly. An 8 : 1 in 6061 and an 8 : 1 in IN718 are different decisions, because the material cost and the machining cost both differ by an order of magnitude. See [machiningProcesses ProcessComparison.md](../../machiningProcesses/docs/ProcessComparison.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Wrought is 1.00 by definition | Everything else is measured against it |
| As-welded aluminium is 0.50 | At the weld |
| Unqualified casting is 0.50 | Compare against qualifying |
| LPBF Z direction is 0.85 to 0.95 | With HIP and a qualified process |
| Knockdowns shrink with statistical maturity | Not with material change |
| Wrought holds the allowable, near net shape holds the buy-to-fly | The trade in one sentence |

---

## Standards

| Standard | Scope |
|---|---|
| **MMPDS** | Wrought allowables, the baseline |
| **NASA-STD-5001** | Structural design and test factors, including casting factors |
| NASA-STD-6016 | Materials and processes requirements |
| NASA-STD-6030 | Additive manufacturing requirements |
| AWS D17.1 | Fusion welding for aerospace |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterialsLibrary')

from ProcessComparison import ProcessComparison

comparison = ProcessComparison()
comparison.setInputs({'material': '316L', 'condition': 'annealed', 'finishedMass': 8.0,
                      'minimumWallThickness': 0.005, 'characteristicSize': 0.200,
                      'requiredTolerance': 1.0e-4})
for entry in comparison.compareRoutes():
    print(f'{entry["route"]:32s} btf {entry["buyToFly"]:4.1f}:1  '
          f'allow {entry["allowableFactor"]:.2f}  lead {entry["leadTimeWeeks"]:3.0f} wk')
```

---

## References

1. MMPDS-2023, *Metallic Materials Properties Development and Standardization*.
2. NASA-STD-5001B, *Structural Design and Test Factors of Safety for Spaceflight Hardware*.
3. Campbell, F. C., *Manufacturing Technology for Aerospace Structural Materials*, Elsevier, 2006.
