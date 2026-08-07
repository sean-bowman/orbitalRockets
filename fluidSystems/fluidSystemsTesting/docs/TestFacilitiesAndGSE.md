[Home](../README.md) > Test Facilities and GSE

# Test Facilities and Ground Support Equipment

## Contents

- [Overview](#overview)
- [The test stand as a fluid system](#the-test-stand-as-a-fluid-system)
- [Control systems and interlocks](#control-systems-and-interlocks)
- [Hazard zones and safety](#hazard-zones-and-safety)
- [Facility capability](#facility-capability)
- [Setup and configuration control](#setup-and-configuration-control)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A test stand is a fluid system with different constraints: heavier, cheaper, reconfigured constantly, and containing the hazard rather than flying it. Everything in the [fluidSystems](../../fluidSystemsLibrary/docs/FluidSystemsOverview.md) design library applies to it directly.

The difference is that the stand is designed to be changed, and that is both its purpose and its principal failure mode.

---

## The test stand as a fluid system

**The same analysis applies.** Line sizing, pressure budget, water hammer, relief protection, materials compatibility, cleanliness. A test stand that was not analyzed is a test stand that will produce a surge, a trapped volume, or a contamination event and blame the article.

**What differs:**

| Aspect | Flight | Test stand |
|---|---|---|
| Mass | Critical | Irrelevant |
| Pressurant | Helium | **Nitrogen**, because mass does not matter |
| Joints | Welded and VCR | **Quick disconnects and fittings**, because it is reconfigured constantly |
| Line sizing | Tight pressure budget | Generous, because the mass penalty is zero |
| Wall thickness | Minimum that qualifies | Generous, because it is cheap |
| Leak requirement | Hazard or mission derived | Usually looser, but the hazard case still applies |

**The joint count is the trade.** A stand built for reconfigurability has many demountable joints, and many joints means a worse aggregate leak rate. On a stand handling hydrazine, the hazard-derived allowable applies to the stand exactly as it applies to the vehicle, and it is usually the stand that struggles to meet it.

**Cleanliness must match or exceed the article's.** A clean flight article tested through a dirty stand is a dirty flight article, and the contamination arrived during the test that was supposed to qualify it.

---

## Control systems and interlocks

**Sequence enforcement:**

| Rule | Reason |
|---|---|
| Never close two series valves simultaneously on a liquid line | Trapped volume with no relief path |
| Open slowly into a dead-ended volume | Adiabatic compression, especially in oxygen |
| Vent before isolating | Not after |
| Verify each step before commanding the next | Where the out-of-sequence consequence is hazardous |

**Interlocks enforce sequence in hardware or software.** The design question is what happens when one is bypassed, because it will be bypassed during troubleshooting. **An interlock that can be bypassed silently is an interlock that will be**, and the bypass will not be restored.

**Abort and safe-state logic.** For every automated sequence, define what happens on loss of command, loss of power and loss of pneumatic supply. Each valve's fail state is a design decision that must be made explicitly and verified by test, not inferred from the spring.

**Data must be recording before the sequence starts.** The most common data loss in testing is a system armed after the event of interest.

---

## Hazard zones and safety

**Stored energy governs the standoff.** A pneumatic proof test at 30 MPa in a 10 litre volume stores 380 kJ, equivalent to 91 g of TNT, requiring roughly 10 m of unprotected standoff by conventional scaled-distance criteria. The calculation is in [ProofAndBurstTesting.md](ProofAndBurstTesting.md) and in [`PressureTest`](../fluidSystemsTestingLibrary/PressureTest.py).

**Barricade, clear and operate remotely** for any test above the facility's stored-energy threshold. The threshold is a facility safety analysis output, not a judgement call.

**Hazardous fluids** add a second set of controls: vapor monitoring, PPE, deluge, neutralization, and the procedural discipline covered in [fluidSystemsLibrary/docs/OperationsAndPurge.md](../../fluidSystemsLibrary/docs/OperationsAndPurge.md).

**Oxygen monitors** in any enclosed space where inert gas is used. Nitrogen asphyxiation gives no warning.

---

## Facility capability

Before committing to a facility, confirm it can actually do the test.

| Capability | What to confirm |
|---|---|
| **Shaker force rating** | Force = mass x acceleration, including the fixture and the head expander |
| Shaker frequency range | Both ends; low-frequency displacement limits bite before force limits |
| Thermal chamber ramp rate | The specified rate, at the article's thermal mass, not empty |
| Thermal chamber range | With the article's heat load, not the catalog number |
| Vacuum level and pump-down time | MLI and multilayer articles take days |
| Pressure capability | And the stored energy the cell is rated for |
| Cryogenic supply | Rate and total quantity, including chilldown losses |
| Data channels and rate | Simultaneous channels at the required sample rate |
| Article envelope and access | Including instrumentation leads and the fixture |

**Shaker force is the one most often discovered late.** The required force includes the fixture and the head expander, which frequently outweigh the article, and a 10 kN shaker driving a 40 kg fixture cannot deliver much acceleration to a 2 kg valve.

---

## Setup and configuration control

**The setup is part of the test and it has to be recorded as such.** A test result without a recorded configuration cannot be reproduced and cannot be defended.

| Record | Why |
|---|---|
| Photographs of the installed configuration | The single most useful record when something is questioned later |
| Instrumentation locations | A response measurement means nothing without a location |
| Fixture drawing and serial number | Fixtures change and their dynamics change with them |
| Torque values applied | For every joint made up for the test |
| Calibration records | Instrument, date, standard, traceability |
| The as-run procedure with redlines | What actually happened, not what was planned |

**Photograph before and after.** It costs minutes and it resolves arguments that would otherwise cost days.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Analyze the stand as a fluid system | It is one |
| Stand cleanliness >= article cleanliness | The article is only as clean as what fills it |
| Never close two series valves simultaneously | Trapped volume |
| Every isolatable volume gets a relief path | Absolute |
| Interlocks must fail visibly | A silent bypass will not be restored |
| Data recording before the sequence | The most common data loss |
| Confirm shaker force with the fixture | Fixture often outweighs the article |
| Confirm chamber ramp rate loaded | The catalog number is empty |
| Photograph the setup | Before and after |
| Verify QD separation force at pressure | A stuck disconnect stops the test |

---

## Failure modes

**The stand causes the anomaly.** A surge from a stand valve, a contamination event from stand plumbing, a pressure excursion from a stand regulator. Investigated as an article failure until somebody looks at the stand.

**Contamination introduced by the stand.** A clean article, a dirty stand, and a contaminated article afterwards.

**Trapped volume between two stand valves.** The line bursts, and it is the stand line rather than the article.

**Interlock bypassed and not restored.** The interlock existed for a reason and the reason is still there.

**Data system armed after the event.** The transient of interest is not recorded.

**Facility capability discovered mid-campaign.** The shaker cannot reach the level with the fixture installed.

**No configuration record.** The result cannot be reproduced or defended.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-8719.17** | Ground-based pressure vessels and pressurized systems |
| **AFSPCMAN 91-710** | Range safety user requirements |
| NASA-STD-8719.12 | Safety standard for explosives, propellants and pyrotechnics |
| KSC-STD-Z-0005 | Design and operation of hazardous propellant facilities |
| **ASME B31.3** | Process piping, which governs stand plumbing |
| MIL-STD-1522 | Safe design and operation of pressurized systems |
| OSHA 29 CFR 1910.147 | Control of hazardous energy (lockout/tagout) |
| NFPA 55 | Compressed gases and cryogenic fluids code |

---

## Tool interface

The design library applies directly to stand plumbing:

```python
from Line import Line                 # fluidSystems design library
from WaterHammer import WaterHammer
from PressureTest import PressureTest # testing library

# Stand line sizing: nitrogen, generous, mass irrelevant
standLine = Line()
standLine.setInputs({'fluid': 'Nitrogen', 'massFlow': 0.05, 'length': 15.0,
                     'inletPressure': 20e6, 'inletTemperature': 293.15,
                     'service': 'gaseous general', 'designPressure': 25e6})
standLine.sizeDiameter()
standLine.selectStandardTube()

# The stored energy that sets the cell standoff
test = PressureTest()
test.setInputs({'maximumExpectedOperatingPressure': 20e6,
                'hardwareClass': 'ground support equipment',
                'testMedium': 'gas', 'testFluid': 'Nitrogen', 'testVolume': 0.010})
test.calculateLevels()
print(test.calculateStoredEnergy()['safeStandoffDistance'])
```

---

## References

1. NASA-STD-8719.17B, *NASA Requirements for Ground-Based Pressure Vessels and Pressurized Systems*.
2. AFSPCMAN 91-710, *Range Safety User Requirements*.
3. ASME B31.3, *Process Piping*.
4. Huzel, D. K. and Huang, D. H., *Modern Engineering for Design of Liquid-Propellant Rocket Engines*, AIAA, 1992.
