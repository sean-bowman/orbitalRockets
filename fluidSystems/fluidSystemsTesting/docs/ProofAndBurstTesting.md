[Home](../README.md) > Proof and Burst Testing

# Proof and Burst Testing

## Contents

- [Overview](#overview)
- [Test levels](#test-levels)
- [Proof testing](#proof-testing)
- [Stored energy and the pneumatic hazard](#stored-energy-and-the-pneumatic-hazard)
- [Burst testing](#burst-testing)
- [Instrumentation](#instrumentation)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Two tests with different purposes and very different consequences.

**Proof** demonstrates that an article takes its design load without permanent deformation or leakage. It is applied to **every flight article** as an acceptance test, so it must be non-destructive by construction.

**Burst** demonstrates ultimate capability. It destroys the article, so it is a qualification test on dedicated units and it is never an acceptance test.

The part of this that matters most operationally is not the pressure levels, which are a lookup. It is the stored energy, which decides whether the test is a routine operation or a hazardous one.

---

## Test levels

From AIAA S-080 and S-081, applied to MEOP:

| Hardware class | Proof | Burst |
|---|---|---|
| Metallic pressure vessel | 1.5 | 2.0 |
| COPV | 1.5 | 2.5 |
| **Line, hazardous fluid** | **1.5** | **4.0** |
| Line, non-hazardous | 1.5 | 2.5 |
| Component | 1.5 | 2.5 |
| Flexible hose | 1.5 | 4.0 |
| Ground support equipment | Per ASME B31.3 | Per ASME B31.3 |

**MEOP is the input that has to be right.** It includes the nominal operating pressure, the regulator outlet band maximum rather than its setpoint, relief accumulation if the relief can lift, water hammer surge if the transient reaches this article, and thermal rise in a locked-up volume.

**ASME B31.3 works differently and is not interchangeable.** It sets an allowable stress (the lesser of two thirds of yield and one third of ultimate) and requires a 1.5x hydrostatic proof, with no burst factor at all. An article qualified to one system is not automatically acceptable under the other.

---

## Proof testing

**Procedure, generically:**

1. Install the article with calibrated instrumentation and take baseline dimensional measurements
2. Fill and vent to remove all gas if hydrostatic
3. Pressurize slowly to MEOP, hold, check for gross leakage
4. Pressurize to proof pressure at a controlled rate
5. **Hold for the specified time**, typically 300 s, long enough for equilibrium and for a leak to manifest
6. Depressurize slowly
7. Repeat the dimensional measurements and compare

**The pass criteria are two:** no leakage during the hold, and no detectable permanent set. Permanent set requires a measurement before and after, not merely the absence of a leak. A criterion of 0.2 percent of the elastic deflection is typical.

**Depressurize slowly.** A rapid depressurization risks explosive decompression of elastomer seals and is itself a transient that can generate a surge.

**Proof before leak test.** Proof can open a marginal joint and the leak test immediately afterwards is what catches it.

---

## Stored energy and the pneumatic hazard

This is the calculation that decides whether the test is dangerous, and it is why the rule is to proof with a liquid wherever possible.

**Gas, expanding isentropically to ambient:**

```
E = (P * V) / (gamma - 1) * [ 1 - (P_ambient / P)^((gamma-1)/gamma) ]
```

**Liquid, compression energy only:**

```
E = (dP)^2 * V / (2 * K)
```

with K the bulk modulus.

The difference is enormous. Ten litres at 30 MPa:

| Medium | Stored energy | TNT equivalent | Unprotected standoff |
|---|---|---|---|
| Water | 1.9 kJ | 0.45 g | 1.7 m |
| **Nitrogen** | **380 kJ** | **91 g** | **9.9 m** |

A factor of 200 at this pressure, and far more at lower pressures where the liquid's own compression energy is negligible.

**Use the real gas gamma.** Nitrogen at 30 MPa has gamma = 1.72, not 1.4. Using the ideal value gives 605 kJ instead of 380 kJ, a 60 percent overestimate. The [`PressureTest`](../fluidSystemsTestingLibrary/PressureTest.py) class pulls gamma from the property backend for exactly this reason.

**Standoff by Hopkinson-Cranz scaling:**

```
R = Z * W^(1/3)
```

with Z the scaled distance criterion and W the TNT-equivalent mass. Blast overpressure at a given scaled distance is approximately independent of charge size, which is what makes the criterion transferable.

| Criterion | Z [m/kg^(1/3)] |
|---|---|
| Personnel, unprotected | 22 |
| Personnel, behind a substantial barrier | 8 |
| Equipment damage threshold | 4 |
| Structural damage | 2 |

**These numbers make the magnitude visible; they do not replace a facility safety analysis.** A real standoff comes from the applicable range or site standard. What the calculation is for is ensuring that a pneumatic proof test is a considered decision rather than a default.

**If a pneumatic proof is unavoidable:** barricade, clear to the calculated distance, pressurize remotely, monitor remotely, and have nobody in the cell.

---

## Burst testing

**Purpose:** demonstrate ultimate capability and, equally important, confirm the failure location and mode.

**A burst that occurs somewhere other than the predicted location means the analysis was wrong even if the pressure was adequate.** That is a finding, and it should be treated as one rather than as a pass.

**Practice:**

- **Minimum three articles** for a statistically meaningful ultimate. One article gives a number with no distribution.
- **Hydrostatic wherever possible.** A burst test is a deliberate failure and the stored energy is released by design.
- **Burst at temperature** if the service temperature reduces the material strength.
- **Instrument to capture the failure**, with high-rate pressure and strain, and high-speed video where the geometry permits.
- **Record the failure location and mode** photographically before anything is disturbed.

---

## Instrumentation

| Measurement | Purpose | Notes |
|---|---|---|
| Pressure | The independent variable | Two independent transducers, one as a check |
| Strain | Detects yield onset before it becomes permanent set | Rosettes at the predicted critical location |
| Displacement | Bulk deformation and permanent set | LVDT or DIC |
| Dimensional, before and after | The permanent set criterion | CMM or micrometer, same operator and method |
| Temperature | Property correction, and detects adiabatic heating on a gas test | |
| Acoustic emission | Optional; detects crack initiation before failure | Useful on composites |

**Two independent pressure measurements.** A single transducer that drifts turns a proof test into an unknown, and the article has already been subjected to whatever the real pressure was.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Proof factor | 1.5x MEOP, universally |
| Burst factor, hazardous fluid line | 4.0x MEOP |
| Burst factor, pressure vessel | 2.0x MEOP with fracture control |
| Proof hold time | ~300 s |
| Proof with liquid | Wherever possible |
| Use real-gas gamma for stored energy | Ideal overestimates by 60 % at 30 MPa |
| Permanent set criterion | ~0.2 % of elastic deflection, measured |
| Burst articles | 3 minimum for a distribution |
| Two independent pressure transducers | A drifting single transducer invalidates the test |
| Depressurize slowly | Explosive decompression and surge |

---

## Failure modes

**Pneumatic proof accident.** Stored energy released as a projectile. Entirely avoidable.

**MEOP underestimated**, so proof is below the real operating transient.

**Permanent set not measured**, only leakage checked. Yielding goes undetected.

**Proof yields the article**, because the design has inadequate margin. Every flight article is damaged. This is a design finding and the [`PressureTest`](../fluidSystemsTestingLibrary/PressureTest.py) class raises rather than reporting a margin below one.

**Burst below the required level.** A design finding.

**Burst at an unpredicted location.** An analysis finding, even at an adequate pressure.

**Gas trapped in a hydrostatic test.** A pocket of air converts a benign test into an energetic one locally. Vent thoroughly and verify.

---

## Worked example

The thruster valve from [`codeInterface.py`](../codeInterface.py), MEOP 2.4249 MPa (the surge peak), component class, 316L, 20 cc internal volume:

| Quantity | Value |
|---|---|
| Proof pressure | 3.6374 MPa, 300 s hold, hydrostatic |
| Burst pressure | 6.0622 MPa |
| Hydrostatic stored energy | 0.06 J |
| Hoop stress at proof | 6.87 MPa |
| **Yield margin at proof** | **24.8** |
| Same test, pneumatic | 0.11 kJ, a factor of 1830 more |
| Pneumatic unprotected standoff | 0.65 m |

The yield margin of 24.8 is typical for small-bore hardware, where the wall is set by handling rather than by pressure. The 1830x energy ratio at a 20 cc volume is the argument for hydrostatic testing even on small articles; scale the volume to a tank and it becomes a serious hazard.

---

## Standards

| Standard | Scope |
|---|---|
| **AIAA S-080** | Metallic pressure vessels, pressurized structures and pressure components |
| **AIAA S-081** | Composite overwrapped pressure vessels |
| ASME BPVC Section VIII | Pressure vessels |
| **ASME B31.3** | Process piping, including hydrostatic and pneumatic leak testing |
| NASA-STD-8719.17 | Ground-based pressure vessels and pressurized systems |
| NASA-STD-5019 | Fracture control for spaceflight hardware |
| CGA P-1 | Safe handling of compressed gases |

---

## Tool interface

```python
from PressureTest import PressureTest

test = PressureTest()
test.setInputs({'maximumExpectedOperatingPressure': 2.4249e6,
                'hardwareClass': 'line hazardous fluid',
                'testMedium': 'gas', 'testFluid': 'Nitrogen', 'testVolume': 0.010,
                'material': '316L', 'outerDiameter': 0.00953, 'wallThickness': 0.00165})

test.calculateLevels()           # proof, burst, hold time
test.calculateStoredEnergy()     # energy, TNT equivalent, standoff by criterion
test.checkArticleCapability()    # hoop stress and margins; raises if proof would yield
print(test.generateReport())
```

---

## References

1. AIAA S-080A-2018, *Space Systems -- Metallic Pressure Vessels, Pressurized Structures, and Pressure Components*.
2. ASME B31.3, *Process Piping*, Chapter VI: Inspection, Examination and Testing.
3. NASA-STD-8719.17B, *NASA Requirements for Ground-Based Pressure Vessels and Pressurized Systems*.
4. Baker, W. E. et al., *Explosion Hazards and Evaluation*, Elsevier, 1983.
5. Kinney, G. F. and Graham, K. J., *Explosive Shocks in Air*, 2nd ed., Springer, 1985.
