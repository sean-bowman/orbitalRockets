[Home](../README.md) > Test Campaign Planning

# Test Campaign Planning

## Contents

- [Overview](#overview)
- [The four levels](#the-four-levels)
- [Building the matrix](#building-the-matrix)
- [Sequence rules](#sequence-rules)
- [Article count](#article-count)
- [Tailoring](#tailoring)
- [Schedule and cost drivers](#schedule-and-cost-drivers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Campaign planning decides what gets tested, at what level, in what order, on how many articles. It is done once, early, and it is expensive to change afterwards because the article count drives the build plan and the build plan drives the schedule.

The output is a matrix, and the matrix has to survive contact with three things that always happen: a requirement changes, an article fails, and the schedule compresses.

---

## The four levels

| Level | Purpose | Articles | Levels | Destructive |
|---|---|---|---|---|
| **Development** | Does the concept work? Find the failure modes | Breadboards, prototypes | Whatever is informative | Yes, deliberately |
| **Qualification** | Does the design meet requirements with margin? | Dedicated units | Flight plus margin | Yes |
| **Acceptance** | Was this article built right? | Every flight unit | Flight levels | **Never** |
| **Pre-flight** | Is the installed system ready? | The flight vehicle | Operating levels | Never |

**Development testing is undervalued.** It is the cheapest place to find a failure mode, and a programme that goes straight from analysis to qualification discovers its design problems on dedicated articles at the most expensive possible moment. The purpose of development testing is to fail things.

**Protoqualification** is the middle path for cost-constrained programmes: test flight articles at levels between acceptance and qualification. It saves the dedicated articles and it consumes some flight life, which has to be tracked and accounted for.

---

## Building the matrix

The matrix is assembled from three inputs:

1. **What the article is.** A valve needs functional and life testing; a length of tube does not. A pressurized article needs proof and leak; a bracket does not.
2. **What it contains.** A hazardous fluid drives volumetric weld inspection, hazard-derived leak requirements and procedural controls. A cryogen drives cold functional and cold leak testing.
3. **Where it flies.** Spaceflight adds thermal vacuum. A first stage sees a different vibration environment from an upper stage.

The [`TestCampaign`](../fluidSystemsTestingLibrary/TestCampaign.py) class encodes this as a catalogue with applicability tags, so the matrix falls out of the article description rather than being assembled by hand and subsequently forgotten about.

---

## Sequence rules

Five rules, each of which exists because something went wrong once.

| Rule | Reason |
|---|---|
| **Proof before leak** | Proof can open a marginal joint; the leak test after is what catches it |
| **Baseline functional early** | The post-environmental comparison needs a pre-environmental baseline on the same article |
| **Leak after every environment** | Knowing which exposure caused a failure is worth the extra tests |
| **Life before final functional** | Wear-out shows as leakage and drift before it shows as function |
| **Burst last** | It destroys the article |

**The leak-after-every-environment rule is the one most often compromised for schedule**, and it is a false economy. Running one leak test at the end tells you the article leaks; running four tells you the thermal cycling did it, which is the difference between a corrective action and an investigation.

---

## Article count

The article count is set by the destructive tests and by the statistical demonstration, and it is almost always higher than the first estimate.

| Driver | Articles |
|---|---|
| Burst test | 1, consumed. Three for a statistically meaningful ultimate |
| Life test | 1 minimum, more if the reliability demonstration needs them |
| Parallel environmental testing (schedule) | 1 per parallel path |
| Reliability demonstration | See [UncertaintyAndStatistics](UncertaintyAndStatistics.md); often the dominant driver |
| Spares for anomaly investigation | At least 1, and it will be used |

**The reliability demonstration is where the count explodes.** Demonstrating R = 0.99 at 90 percent confidence by test alone needs 230 units with zero failures. Nobody builds 230 flight valves, which is why reliability is argued from test plus analysis plus heritage plus process control rather than demonstrated. Plan the argument, not just the test.

**Budget an article for the anomaly.** Every campaign has one. A programme with no spare article stops when it happens.

---

## Tailoring

Programmes tailor standards. That is legitimate and it is expected.

**What is not legitimate is tailoring by omission**, where a test quietly does not happen because nobody noticed it was required. The difference is a written reason.

The [`TestCampaign`](../fluidSystemsTestingLibrary/TestCampaign.py) class requires a reason string for every tailored test and reproduces it in the report, so the decision is visible in the same document as the sequence rather than living in a meeting minute nobody can find.

**Legitimate tailoring reasons:**

- The environment does not apply to this configuration (no pyrotechnic events, so no shock)
- The test is covered at a higher assembly level (thermal vacuum at the module rather than the component)
- The requirement is verified by another method (analysis validated by a different test)
- Heritage or similarity covers it, with a written argument

**Not legitimate:** schedule, cost, or "we have never had a problem with that".

---

## Schedule and cost drivers

| Activity | Cost share | Schedule share |
|---|---|---|
| Environmental test facility time | 30 to 40 % | 20 % |
| **Life and endurance testing** | 15 to 25 % | **40 to 50 %** |
| Article fabrication | 15 to 25 % | 20 % |
| Instrumentation and fixturing | 10 to 15 % | 15 % |
| Documentation | 5 to 10 % | 10 % |
| **Anomaly investigation** | **variable** | **variable** |

**Life testing dominates the schedule** and it cannot be compressed by spending money, only by acceleration (needing a defensible model) or parallelism (needing more articles). It should be started as early as the design maturity permits, because it is on the critical path from the moment it starts.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Development testing exists to fail things | Cheapest place to find a failure mode |
| Acceptance must be non-destructive | And must not consume meaningful life |
| Leak test after every environmental exposure | Identifies which exposure caused a failure |
| Burst last, always | It destroys the article |
| Budget a spare article for the anomaly | There is always one |
| Start life testing as early as design maturity allows | It is on the critical path |
| Every tailored test carries a written reason | Tailoring by omission is the failure mode |
| Reliability comes from an argument, not a demonstration | 230 units for R = 0.99 at 90 % |

---

## Failure modes

**No development testing.** Design problems surface on qualification articles.

**Acceptance at qualification levels.** Flight hardware life consumed before it flies.

**Article count set by the destructive tests alone.** No spare for the anomaly, and the campaign stops.

**Life testing started late.** It is on the critical path and the programme discovers that too late to parallelize.

**Tailoring by omission.** A required test that nobody noticed was required.

**Sequence compromised for schedule.** Usually the intermediate leak tests, which is the compromise that costs the most information.

**The reliability requirement not planned for.** Discovered when someone asks how R = 0.99 will be shown.

---

## Worked example

From [`codeInterface.py`](../codeInterface.py), the thruster isolation valve for the 100 N hydrazine system:

| Quantity | Value |
|---|---|
| Article | Thruster isolation valve, toxic fluid, spaceflight |
| Qualification sequence | 14 tests, 1 destructive |
| Acceptance sequence | 10 tests, every flight article |
| Tailored out | 1 (thermal vacuum, covered at module level, reason recorded) |
| Qualification articles | 3 (1 consumed by burst) |
| Demonstrated reliability from those 3 | R = 0.4642 at 90 % confidence |

The last two lines are the finding: three articles is what the destructive tests and the schedule allow, and three articles demonstrate R = 0.46 against a requirement of R = 0.99. That gap is closed by argument, not by testing, and identifying it during planning is the entire point of doing this calculation early.

---

## Standards

| Standard | Scope |
|---|---|
| **MIL-STD-1540** | Test requirements for launch, upper stage and space vehicles |
| NASA-STD-7002 | Payload test requirements |
| MIL-STD-810 | Environmental engineering considerations and laboratory tests |
| ECSS-E-ST-10-03 | Space engineering: testing |
| AIAA S-080 / S-081 | Pressure vessel and COPV verification requirements |

---

## Tool interface

```python
from TestCampaign import TestCampaign

campaign = TestCampaign()
campaign.setInputs({'articleName': 'Thruster isolation valve',
                    'articleType': 'valve', 'hardwareClass': 'component',
                    'fluidHazard': 'toxic', 'isCryogenic': False, 'isSpaceflight': True,
                    'tailoring': {'thermal vacuum': 'Covered at module assembly level'}})
matrix = campaign.buildMatrix()
print(campaign.generateReport())
```

Lookup tables: `TestCampaign.TEST_CATALOGUE`, `TestCampaign.ARTICLE_ATTRIBUTES`.

---

## References

1. MIL-STD-1540E, *Test Requirements for Launch, Upper-Stage, and Space Vehicles*.
2. NASA-STD-7002B, *Payload Test Requirements*.
3. ECSS-E-ST-10-03C, *Space Engineering: Testing*.
4. NASA/SP-2016-6105 Rev 2, *NASA Systems Engineering Handbook*.
