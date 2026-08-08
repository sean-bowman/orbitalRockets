[Home](../README.md) > Standards Index

# Standards Index

## Contents

- [Overview](#overview)
- [The handbooks](#the-handbooks)
- [Requirements and analysis](#requirements-and-analysis)
- [Testing](#testing)
- [Thermal protection and entry](#thermal-protection-and-entry)
- [Materials and property measurement](#materials-and-property-measurement)
- [Two phase and cryogenic](#two-phase-and-cryogenic)
- [How they fit together](#how-they-fit-together)
- [References](#references)

---

## Overview

An annotated index of the standards this domain works to, with what each one is actually for. Short on purpose: these are the documents a thermal engineer opens, not everything that exists.

The pattern in thermal control differs from the structural and dynamics domains. There is no equivalent of MMPDS: no single statistical allowables document that everyone works from. The authority is concentrated in two handbooks and one European standard, and the rest are test methods.

---

## The handbooks

| Document | What it gives you |
|---|---|
| **Gilmore, Spacecraft Thermal Control Handbook, volume I** | **The reference.** Fundamentals, hardware, coatings, radiators, heat pipes, testing. If one book, this one |
| Gilmore, volume II | Cryogenic systems, including coolers and cryogenic thermal control |
| **NASA-HDBK-2001** | **Spacecraft thermal control handbook.** Optical property tables, contact conductance data, degradation |
| Incropera and DeWitt | The undergraduate text, and still the right place for a correlation and its validity range |

**Gilmore volume I is the one document to read** to be able to design and defend a thermal control system rather than analyse one somebody else designed.

---

## Requirements and analysis

| Standard | What it gives you |
|---|---|
| **ECSS-E-ST-31C** | **Thermal control general requirements.** The European parent document, and the most complete requirements statement available |
| ECSS-E-ST-31-04C | Thermal analysis. Model fidelity expectations and the reduced model exchange format |
| ECSS-E-ST-31-02C | Two phase heat transport equipment. Heat pipes and loop heat pipes |
| NASA-STD-7009 | Models and simulations. The credibility assessment framework, which is what a correlation argument is graded against |
| NASA-STD-5001 | Structural design and test factors of safety, for the thermal stress cases that reach [aerospaceStructures](../../aerospaceStructures/README.md) |

**ECSS-E-ST-31C is the requirements document and NASA-HDBK-2001 is the data.** They are complements rather than alternatives, and a programme working to NASA requirements still uses the ECSS document to write them.

---

## Testing

| Standard | What it gives you |
|---|---|
| **MIL-STD-1540** | **Test requirements for launch, upper stage and space vehicles.** The parent test document |
| **GSFC-STD-7000** | **The GEVS.** General environmental verification standard, the practical test specification |
| ECSS-E-ST-10-03C | Testing. The European equivalent, including thermal vacuum and cycling |
| NASA-STD-7002 | Payload test requirements |
| ASTM E491 | Solar simulation for thermal balance testing |
| ASTM E2739 | Heat pipe performance testing |

**GEVS is what a test procedure is actually written from.** MIL-STD-1540 states the requirement; GEVS states the levels, durations and cycle counts.

---

## Thermal protection and entry

| Standard | What it gives you |
|---|---|
| **NASA SP-8014** | **Entry thermal protection.** The design monograph, and still the clearest statement of the sizing problem |
| NASA SP-8029 | Aerodynamic and rocket exhaust heating during launch and ascent |
| Sutton and Graves, NASA TR R-376 | The stagnation point heating correlation this domain uses |
| ASTM E285 | Oxyacetylene ablation testing. How an ablator's performance is measured |
| ASTM E457 | Thermal flux measurement by calorimeter |
| ASTM E511 | Heat flux measurement with a circular foil gauge |
| MIL-HDBK-17 | Composite materials handbook, for the phenolic ablators |

**The SP-8 monographs are from the 1960s and 1970s and have not been superseded**, which is a statement about how well they were written rather than about how much the field has moved.

---

## Materials and property measurement

| Standard | What it gives you |
|---|---|
| ASTM E1225 | Steady state thermal conductivity, guarded comparative method |
| ASTM C177 | Guarded hot plate conductivity, the reference method for insulation |
| ASTM C518 | Heat flow meter conductivity, the fast method |
| ASTM D5470 | Thermal interface material characterisation |
| ASTM E903 | Solar absorptance by spectrophotometry |
| ASTM E408 | Total normal emittance |
| ASTM E595 | Total mass loss and collected volatile condensable materials, the outgassing screen |
| NASA-STD-6016 | Materials and processes requirements, including the outgassing acceptance limits |
| ECSS-Q-ST-70-06 | Particle and molecular contamination control, which drives optical degradation |

**ASTM E903 and E408 are the pair that produce `alpha` and `eps`.** They are separate tests in separate spectral bands, which is the measurement level statement of why the two numbers are independent. See [RadiationHeatTransfer](RadiationHeatTransfer.md).

---

## Two phase and cryogenic

| Standard | What it gives you |
|---|---|
| ECSS-E-ST-31-02C | Two phase heat transport equipment |
| ASTM C740 | Evacuated reflective insulation in cryogenic service |
| ASTM C1774 | Thermal performance testing of cryogenic insulation systems |
| CGA H-3 | Cryogenic hydrogen storage |
| NASA-STD-6001 | Flammability, offgassing and compatibility, which constrains blanket materials |

The system level cryogenic documents live with [fluidSystems](../../fluidSystems/fluidSystemsLibrary/docs/CryogenicSystems.md), which owns tank and line design.

---

## How they fit together

A thermal control system is developed against four bodies of material and they enter at different points.

**Requirements come from ECSS-E-ST-31C or a programme equivalent.** That is where the temperature limits, the case definitions and the margin policy are written.

**Data comes from NASA-HDBK-2001 and Gilmore.** Optical properties, contact conductances, working fluid properties. This is the material a model is built from, and it is the material a correlation adjusts.

**Analysis credibility comes from NASA-STD-7009 and ECSS-E-ST-31-04C.** Not the physics, but the argument that the model is fit for the decision being made on it.

**Test levels come from GEVS and MIL-STD-1540.** The margins over predicted, the cycle counts, the dwells.

**The circular dependency worth naming:** the test margin exists because the prediction has uncertainty, and the prediction's uncertainty is established by correlating against the test. A 5 K acceptance margin and a 3 to 5 K correlation acceptance are the same number for that reason, and neither is derived independently of the other.

---

## References

- Gilmore, *Spacecraft Thermal Control Handbook*, volumes I and II
- NASA-HDBK-2001, *Spacecraft Thermal Control Handbook*
- ECSS-E-ST-31C, *Thermal control general requirements*
- MIL-STD-1540, *Test requirements for launch, upper stage and space vehicles*
- GSFC-STD-7000, *General environmental verification standard*
- NASA SP-8014, *Entry thermal protection*
