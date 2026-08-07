[Home](../README.md) > Process Comparison

# Process Comparison

## Contents

- [Overview](#overview)
- [Against LPBF](#against-lpbf)
- [Against casting](#against-casting)
- [Against machining and forging](#against-machining-and-forging)
- [The honest comparison](#the-honest-comparison)
- [Design rules of thumb](#design-rules-of-thumb)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Non-LPBF additive processes compete with different things depending on which one is being considered. WAAM competes with forging, cold spray competes with weld repair, and binder jetting competes with investment casting. Grouping them as "additive" obscures that.

---

## Against LPBF

| Axis | LPBF | The others |
|---|---|---|
| **Resolution** | **Best** | Worse, by 2 to 6 IT grades |
| **Rate** | Slow | **Up to 100x faster** |
| **Size** | 400 mm | **Metres** |
| **Repair** | **Cannot** | DED and cold spray can |
| **Internal geometry** | **Excellent** | Poor |
| Material range | Wide | Process dependent |
| Maturity and data | **Best** | Less |

**They barely compete.** The overlap is a moderate size part with moderate resolution requirements, and there LPBF usually wins on data maturity alone.

**EB-PBF is the only real LPBF competitor** in this group, and it wins specifically on residual stress and on crack prone alloys.

---

## Against casting

| Axis | Investment casting | Binder jetting | WAAM |
|---|---|---|---|
| **Tooling** | **Required. 20 wk** | **None** | **None** |
| Tolerance | DCTG 6 | IT11 | IT14 |
| **Allowable** | Casting factor | Sintered, HIP | Good, HIP |
| **Volume economics** | **Best at high volume** | Good at moderate | Low volume |
| Lead time | 20 wk | 4 wk | 4 wk |

**The tooling is the whole comparison at low volume.** An investment casting needs a wax die that costs weeks and money; binder jetting and WAAM need neither.

**At high volume the casting wins** because the tooling amortises and the per-part cost is lower.

**The crossover is typically tens to low hundreds of parts**, and it moves with the part size and the alloy.

**Binder jet sand moulds change this comparison** by removing the pattern cost from sand casting entirely, which puts conventional casting back into the low volume comparison. See [BinderJetting.md](BinderJetting.md).

---

## Against machining and forging

**This is where WAAM and DED actually compete, and it is the comparison that matters.**

For a 40 kg titanium structural part:

| Route | Buy-to-fly | Lead time | Tooling | Allowable |
|---|---|---|---|---|
| **Machined from plate** | **10 : 1** | 16 wk | None | **1.00** |
| **Forged and machined** | 4 : 1 | **30 wk** | **Required** | **1.00** |
| **WAAM and machined** | **1.5 : 1** | **6 wk** | **None** | 0.9 to 1.0 |
| DED and machined | 2 : 1 | 8 wk | None | 0.9 to 1.0 |

**WAAM wins on all three of buy-to-fly, lead time and tooling**, and it loses on allowable maturity and on the qualification burden.

**In titanium the buy-to-fly difference is decisive.** Going from 10 : 1 to 1.5 : 1 on a 40 kg part saves 340 kg of titanium and the machining time to remove it, and at titanium's cost index of 8.5 that is a very large number.

**In aluminium it is not.** The same ratio on cheap, easily machined material does not pay for the qualification, and that is why WAAM adoption is concentrated in titanium and nickel.

---

## The honest comparison

**Three things are routinely left out of additive comparisons and all three favour the conventional route.**

**Machining allowance.** A WAAM part is not finished when the deposition stops. Three to six millimetres per surface has to come off, and that machining is at the same rate and cost as machining anything else. A buy-to-fly of 1.5 : 1 quoted without the allowance is not the real number.

**Qualification cost.** A conventional route uses an existing qualification. An additive route needs its own, and for flight hardware under NASA-STD-6030 that is a substantial programme. It is a one-off cost and it is real.

**Allowable knockdown.** Additive allowables carry a build direction knockdown and a maturity margin. A route that saves 30 percent of the mass in material and gives back 10 percent in allowable has saved less than it appears.

**With all three included the comparison is still often favourable**, and that is the point: it should be made honestly rather than avoided.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| These processes compete with different things | Not with each other |
| WAAM competes with forging and plate | Not with LPBF |
| Cold spray competes with weld repair | |
| Binder jet competes with investment casting | |
| Tooling is the comparison at low volume | |
| **Include the machining allowance** | Or the buy-to-fly is fiction |
| **Include the qualification cost** | It is real and one-off |
| **Include the allowable knockdown** | Mass saved is given partly back |

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-6030** | Additive manufacturing requirements for spaceflight |
| NASA-STD-5001 | Structural design and test factors, including casting factors |
| NASA-STD-6016 | Materials and processes requirements |
| ISO/ASTM 52900 | Additive manufacturing terminology |
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
for entry in comparison.compareRoutes():
    print(f'{entry["route"]:32s} btf {entry["buyToFly"]:4.1f}:1  '
          f'allow {entry["allowableFactor"]:.2f}  lead {entry["leadTimeWeeks"]:3.0f} wk  '
          f'cost {entry["relativeCost"]:.1f}')
```

---

## References

1. Gradl, P. R. et al., "Metal Additive Manufacturing in Aerospace: A Review", *Materials and Design*, Vol. 209, 2021.
2. Williams, S. W. et al., "Wire + Arc Additive Manufacturing", *Materials Science and Technology*, Vol. 32, 2016.
3. NASA-STD-6030, *Additive Manufacturing Requirements for Spaceflight Systems*.
