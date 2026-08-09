[Home](../README.md) > Standards Index

# Standards Index

## Contents

- [Overview](#overview)
- [The design monographs](#the-design-monographs)
- [Performance methodology](#performance-methodology)
- [Combustion stability](#combustion-stability)
- [Propellant specifications](#propellant-specifications)
- [Requirements and testing](#requirements-and-testing)
- [The textbooks](#the-textbooks)
- [How they fit together](#how-they-fit-together)
- [References](#references)

---

## Overview

An annotated index of the standards this domain works to, with what each one is actually for. Short on purpose: these are the documents a propulsion engineer opens, not everything that exists.

Liquid propulsion has an unusual literature. **The authoritative design references are a set of NASA monographs written between 1965 and 1976 and never superseded**, and the working reference is a textbook. There is no MMPDS equivalent and no single requirements document that everything traces to.

---

## The design monographs

The NASA SP-8000 series. Each one is a short monograph on a single component, written by the people who had just built them, and most have not been improved on.

| Document | What it gives you |
|---|---|
| **NASA SP-125** | **Design of Liquid Propellant Rocket Engines.** The one book. Sizing, performance, injectors, cooling, turbomachinery |
| NASA SP-8087 | Liquid rocket engine fluid-cooled combustion chambers |
| NASA SP-8089 | Liquid rocket engine injectors |
| NASA SP-8120 | Liquid rocket engine nozzles, including the side load discussion |
| NASA SP-8107 | Turbopump systems for liquid rocket engines |
| NASA SP-8052 | Liquid rocket engine turbopump inducers |
| NASA SP-8048 | Liquid rocket engine turbopump bearings |
| NASA SP-8113 | Liquid rocket engine combustion stabilization devices |
| NASA SP-8081 | Liquid propellant gas generators |
| NASA SP-8124 | Liquid rocket engine self-cooled combustion chambers |

**SP-125 is the one to read.** It is a 1971 document and the physics has not moved; what has moved is manufacturing, and the sizing arguments are unaffected by that.

---

## Performance methodology

This is where the domain does have a rigorous standard, and it matters because performance figures are contractual.

| Document | What it gives you |
|---|---|
| **CPIA 246** | **Liquid rocket engine performance prediction and evaluation.** The JANNAF methodology |
| NASA RP-1311 | CEA theory and usage, the equilibrium chemistry everything starts from |
| CPIA 178 | JANNAF rocket engine performance test data acquisition and interpretation |
| JANNAF SPP | Standardised performance program, the reference implementation |

**The JANNAF methodology fixes what is included in a delivered specific impulse and what is not**, which is the whole difficulty in quoting one. Without it, two honest engineers produce different numbers for the same engine and neither is wrong.

---

## Combustion stability

Separated out because it is the failure mode that destroys hardware and because the literature is distinct.

| Document | What it gives you |
|---|---|
| **NASA SP-194** | **Liquid Propellant Rocket Combustion Instability.** Harrje and Reardon. The standing reference |
| CPIA 655 | Combustion stability testing and rating, including the bomb test |
| NASA SP-8113 | Combustion stabilization devices, baffles and acoustic cavities |

**SP-194 is fifty years old and still the reference.** Combustion instability is a threshold rather than a margin: a stable engine and an unstable one differ by a design detail rather than by a factor, and that is why the rating tests are perturbation tests rather than steady measurements.

---

## Propellant specifications

| Standard | Covers |
|---|---|
| MIL-PRF-25576 | RP-1 |
| MIL-PRF-27401 | Nitrogen tetroxide |
| MIL-PRF-27404 | Monomethylhydrazine |
| MIL-PRF-27407 | High-test hydrogen peroxide |
| MIL-PRF-25508 | Liquid oxygen |
| CGA G-4 | Oxygen handling |
| NASA-STD-6001 | Materials flammability, offgassing and compatibility |

---

## Requirements and testing

| Standard | What it gives you |
|---|---|
| ECSS-E-ST-35C | Propulsion general requirements. The European parent document, and the closest thing to a single requirements standard |
| ECSS-E-ST-35-02C | Solid propulsion, for completeness |
| MIL-STD-1540 | Test requirements for launch vehicles |
| NASA-STD-5012 | Strength and life assessment for rocket engines |
| AIAA S-080 | Metallic pressure vessels, which the chamber is |
| ISO 21349 | Inspection and test of propulsion subsystems |

**NASA-STD-5012 is the one that is easy to miss** and it is the structural counterpart to everything in this domain: it covers how an engine's strength and life are demonstrated, which is a different problem from a vehicle structure because the loads are thermal and cyclic.

---

## The textbooks

| Book | What it is for |
|---|---|
| **Sutton and Biblarz, Rocket Propulsion Elements** | The working reference. Broad, current, and the one on the desk |
| **Huzel and Huang, Modern Engineering for Design of Liquid Propellant Rocket Engines** | The design handbook. Denser than Sutton and more directly usable for sizing |
| Yang, Habiballah, Hulka and Popp, *Liquid Rocket Thrust Chambers* | Modern treatment of the combustion device |
| Clark, *Ignition!* | The propellant history, and the best explanation of why the storables are what they are |
| Sutton, *History of Liquid Propellant Rocket Engines* | Which configurations were tried and what happened |

---

## How they fit together

**Requirements come from ECSS-E-ST-35C** or a programme equivalent, and there is no American single document that plays the same role.

**Design comes from the SP-8000 monographs and Huzel.** They are old and they are correct.

**Performance numbers come from CEA through the JANNAF methodology.** CEA gives the ideal, JANNAF says how to reduce a test to a defensible delivered figure.

**Stability comes from SP-194 and is demonstrated by CPIA 655 rating tests**, which are deliberate perturbations rather than measurements, because the quantity of interest is a threshold.

**Structural life comes from NASA-STD-5012**, separately from the vehicle structure standards, because engine loads are thermal and cyclic.

**The gap worth naming:** there is no propulsion equivalent of MMPDS. Propellant performance is a CEA run rather than a table, and the tabulated values in this library exist so a first pass runs without CEA installed, not so that CEA can be skipped. See [PropellantSelection](PropellantSelection.md).

---

## References

- NASA SP-125, *Design of Liquid Propellant Rocket Engines*
- Harrje and Reardon, NASA SP-194, *Liquid Propellant Rocket Combustion Instability*
- CPIA 246, *Liquid rocket engine performance prediction and evaluation*
- Gordon and McBride, NASA RP-1311, *Computer Program for Calculation of Complex Chemical Equilibrium Compositions*
- ECSS-E-ST-35C, *Propulsion general requirements*
- Sutton and Biblarz, *Rocket Propulsion Elements*
