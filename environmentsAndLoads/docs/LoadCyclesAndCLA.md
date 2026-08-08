[Home](../README.md) > Load Cycles and Coupled Loads Analysis

# Load Cycles and Coupled Loads Analysis

## Contents

- [Overview](#overview)
- [What a loads cycle is](#what-a-loads-cycle-is)
- [Coupled loads analysis](#coupled-loads-analysis)
- [Model validation](#model-validation)
- [Why the schedule matters](#why-the-schedule-matters)
- [What the CLA produces](#what-the-cla-produces)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A loads cycle is the process by which a vehicle and its payload agree on what loads the payload will see. It is as much a schedule and interface management problem as a technical one, and programmes are damaged more often by its timing than by its analysis.

---

## What a loads cycle is

**An iteration between two organisations that each hold half the model.**

| Step | Owner |
|---|---|
| **1. Payload delivers a model** | Payload |
| **2. Vehicle couples it to the vehicle model** | Launch provider |
| **3. Vehicle runs the transient events** | Launch provider |
| **4. Loads are extracted and delivered** | Launch provider |
| **5. Payload checks its structure** | Payload |
| **6. Redesign if required, and repeat** | Payload |

**Each cycle takes months.** A typical programme runs two or three: a preliminary cycle on coarse models, an intermediate one, and a verification cycle on test-correlated models that produces the loads of record.

**The payload model is delivered, not the payload.** It is a reduced mathematical model, typically a Craig-Bampton reduction with a defined interface, and its quality determines the answer.

---

## Coupled loads analysis

**The vehicle and payload finite element models are combined and run against forcing functions from the flight events.**

| Forcing function | Event |
|---|---|
| **Liftoff** | Hold-down release transient |
| **Engine ignition and shutdown** | Thrust transients |
| **Gust and buffet** | Aerodynamic, at max-Q |
| **Staging** | Separation and second stage start |
| Landing | Reusable stages |

**The output is time histories of accelerations, forces and displacements** at the interface and at defined internal locations, from which load factors and interface loads are extracted.

**It is a transient analysis, not a modal one.** The answer depends on how the forcing function's frequency content lines up with the coupled system's modes, which is why the payload's modes have to be clear of the vehicle's and why the frequency requirement exists at all.

---

## Model validation

**A model that has not been correlated to test is not accepted for the verification cycle.**

| Criterion | Typical requirement |
|---|---|
| **Frequency agreement** | Within 3 to 5 percent, for the significant modes |
| **Cross-orthogonality** | Above 0.9 for matched mode pairs |
| **Effective mass** | The model must capture a stated fraction, typically 80 to 90 percent |
| Damping | Measured, or a conservative assumption stated |

**A modal survey test is how the correlation is obtained**, and it is a substantial test in its own right: the article is suspended, excited by shakers, and its modes measured.

**Cross-orthogonality is the strict criterion.** Frequencies can agree while mode shapes do not, and a model that gets the frequencies right with the wrong shapes gives the wrong interface loads.

**Effective mass is the coverage check.** A model that captures only 60 percent of the effective mass in a direction is missing modes that carry load, and the CLA will not see them.

---

## Why the schedule matters

**The loads cycle is on the critical path and it does not compress.**

| Problem | Consequence |
|---|---|
| **Late model delivery** | The cycle slips, and so does everything after it |
| **A model that fails correlation** | A retest, then a re-run |
| **A design change after the verification cycle** | Potentially a new cycle |
| Loads that exceed the payload's capability | Redesign, then another cycle |

**A design change after the verification cycle is expensive**, because the loads of record no longer apply to the article that flies. Programmes accept small changes with an argument that they cannot increase the loads, and that argument has to be made carefully.

**Preliminary loads are used to design against and they are not the loads of record.** Designing to preliminary loads with no margin means the verification cycle is likely to force a change, and carrying margin against the preliminary cycle is a deliberate schedule investment.

---

## What the CLA produces

| Output | Used for |
|---|---|
| **Interface accelerations** | Payload design, and the quasi-static load factors |
| **Interface forces and moments** | Adapter and separation system design |
| **Internal responses** | Component-level environments at defined locations |
| **Load factors** | The quasi-static summary in [StaticAndQuasiStaticLoads.md](StaticAndQuasiStaticLoads.md) |
| Notching targets | The response predictions that justify a test notch |

**The quasi-static load factor is an output of the CLA, not an input to it.** That ordering is worth stating because the factor is often the only number a component supplier ever sees, and it arrives looking like a given.

**The notching targets matter as much as the load factors.** A CLA response prediction is what justifies reducing a sine or random input at a resonance, and without it the notch is unsupported. See [SineAndTransientVibration.md](SineAndTransientVibration.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Two or three cycles per programme | Each takes months |
| The payload delivers a reduced model | Craig-Bampton, defined interface |
| Frequency agreement 3 to 5 percent | For correlation |
| Cross-orthogonality above 0.9 | The stricter criterion |
| Effective mass 80 to 90 percent | The coverage check |
| Carry margin against preliminary loads | It is a schedule investment |
| A change after verification may force a new cycle | |
| The load factor is a CLA output | Not an input |

---

## Failure modes

**Designing to preliminary loads with no margin.** The verification cycle forces a change.

**A model correlated on frequency alone.** Right frequencies, wrong shapes, wrong interface loads.

**Insufficient effective mass captured.** Load-carrying modes are missing.

**A design change after the verification cycle.** The loads of record no longer apply.

**A notch applied with no CLA response prediction.** Unsupported.

**The load factor treated as an independent requirement.** It is a summary of the CLA.

**Model delivery slipped.** The whole cycle and everything after it slips.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-5002** | Load analyses of spacecraft and payloads |
| NASA-HDBK-7005 | Dynamic environmental criteria |
| **ECSS-E-ST-32-11** | Modal survey assessment |
| NASA-STD-5001 | Structural design and test factors |
| Launch vehicle user guides | The interface and model delivery requirements |

---

## Tool interface

```python
# A coupled loads analysis is a finite element transient run rather than a closed form.
# This domain supplies the quasi-static summary it produces and the environments that
# feed it.
import sys
sys.path.insert(0, 'environmentsAndLoadsLibrary')

from LoadFactorSet import LoadFactorSet

factors = LoadFactorSet()
factors.setInputs({'mass': 500.0, 'description': 'payload'})
factors.addStandardEvents(['liftoff', 'max-Q', 'staging'])

result = factors.identifyGoverning()
print(f'governing by combination: {result["governingByCombined"]}')
print(f'maximum combined factor:  {result["maximumCombined"]:.2f} g')
```

---

## References

1. NASA-STD-5002A, *Load Analyses of Spacecraft and Payloads*.
2. Craig, R. R. and Bampton, M. C. C., "Coupling of Substructures for Dynamic Analyses", *AIAA Journal*, Vol. 6, 1968.
3. ECSS-E-ST-32-11C, *Modal Survey Assessment*.
