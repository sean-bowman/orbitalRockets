[Home](../README.md) > Fluid Systems Testing Overview

# Fluid Systems Testing Overview

The hub document. It maps the subject, defines the vocabulary precisely, walks the campaign end to end, and indexes everything else.

## Contents

- [What testing is for](#what-testing-is-for)
- [The vocabulary](#the-vocabulary)
- [The verification chain](#the-verification-chain)
- [The campaign, end to end](#the-campaign-end-to-end)
- [Test levels](#test-levels)
- [Sequence and why it matters](#sequence-and-why-it-matters)
- [Where the money and schedule go](#where-the-money-and-schedule-go)
- [The ten things that go wrong](#the-ten-things-that-go-wrong)
- [Document index](#document-index)
- [Class index](#class-index)

---

## What testing is for

Testing exists to answer three different questions, and confusing them is the root of most bad test programmes.

| Question | Activity | Applied to | May be destructive |
|---|---|---|---|
| Does the concept work? | **Development** | Breadboards, prototypes | Yes, that is the point |
| Does the design meet its requirements with margin? | **Qualification** | Dedicated articles | Yes |
| Was this specific article built to that design? | **Acceptance** | Every flight article | **Never** |

A development test that fails is information. A qualification test that fails is a design finding. An acceptance test that fails is a manufacturing finding. The same physical test, run at the same levels, means three different things depending on which question it was asked to answer, and the disposition path is different for each.

**The most expensive planning error is conflating qualification and acceptance.** An acceptance test at qualification levels consumes flight hardware life. A qualification test at acceptance levels demonstrates nothing about margin. Both happen, routinely, on programmes that did not write the distinction down.

---

## The vocabulary

These terms are used loosely in conversation and precisely in specifications. Getting them wrong propagates into the design and then into the hardware.

| Term | Definition |
|---|---|
| **MEOP** | Maximum Expected Operating Pressure. The highest pressure the article sees in service, **including transients, relief accumulation and thermal rise**. Not the nominal operating pressure |
| **Proof pressure** | Test pressure demonstrating strength without yielding. `proof factor x MEOP`, universally 1.5 |
| **Burst pressure** | Pressure at which the article fails. `burst factor x MEOP`, 2.0 to 4.0 depending on class |
| **Qualification** | Demonstration that the design meets requirements with margin |
| **Acceptance** | Demonstration that a specific article conforms to the qualified design |
| **Protoqualification** | Flight articles tested between acceptance and qualification levels. Consumes some flight life |
| **Verification** | Confirming a requirement is met, by any of the five methods |
| **Validation** | Confirming the requirement was the right one |
| **VCRM** | Verification Cross Reference Matrix: every requirement mapped to its method and its evidence |
| **ATP** | Acceptance Test Procedure |
| **As-run** | The procedure with the redlines and actual values recorded during execution |
| **Nonconformance** | A departure from a requirement, requiring disposition |
| **MRB** | Material Review Board, which dispositions nonconformances |

**MEOP is where the errors start.** It must include the nominal operating pressure, the regulator outlet band maximum rather than its setpoint, relief valve set pressure plus accumulation if the relief can lift, water hammer surge if the transient reaches this article, and thermal pressure rise in a locked-up volume. A design that took MEOP as the nominal operating pressure has no margin against a transient at all, and it discovers that at proof test if it is lucky.

In the [worked example](../codeInterface.py), MEOP is 2.4249 MPa, which is the water hammer peak, not the 2.236 MPa steady tank pressure. That 8 percent difference propagates into every test level downstream.

---

## The verification chain

Every requirement is verified by one of five methods, and the choice determines the cost and the confidence.

| Method | What it is | When it is appropriate |
|---|---|---|
| **Test** | Subject the article to the condition and measure the response | The requirement is measurable and the condition is reproducible |
| **Demonstration** | Operate the article and observe the outcome | Functional and operational requirements without a measured quantity |
| **Analysis** | Calculate the response using a validated method | The condition cannot be reproduced, or test is prohibitive |
| **Inspection** | Examine the article or its documentation | Dimensional, material, marking and workmanship requirements |
| **Similarity** | Argue from previously qualified hardware | Design, materials, process **and environment** are all demonstrably similar |

**Similarity is the one that causes trouble.** It is the cheapest and the most frequently claimed without a defensible argument. The claim requires that the design, the materials, the manufacturing process and the environment are all similar enough that the previous evidence applies. A valve qualified for a 5 g random vibration environment is not qualified for a 12 g one, and a seal qualified in nitrogen is not qualified in hydrazine. Write the similarity argument down and have someone who did not write it review it.

Detail is in [RequirementsAndVerification.md](RequirementsAndVerification.md).

---

## The campaign, end to end

```
REQUIREMENTS
     |
     v
VERIFICATION PLANNING  ------> VCRM: every requirement to a method
     |
     v
DEVELOPMENT TESTING            breadboards, parameter studies, failure hunting
     |                         may be destructive, informal, iterated
     v
QUALIFICATION                  dedicated articles, levels with margin
     |                         dimensional -> cleanliness -> proof -> leak ->
     |                         functional -> flow cal -> vibration -> leak ->
     |                         shock -> thermal -> life -> leak -> functional -> BURST
     v
ACCEPTANCE                     every flight article, operating levels, non-destructive
     |                         dimensional -> cleanliness -> proof -> leak ->
     |                         functional -> flow cal -> vibration -> leak ->
     |                         thermal -> functional
     v
PRE-FLIGHT                     installed configuration, integrated checks
     |
     v
FLIGHT
```

Each stage produces evidence that closes VCRM lines. A requirement with no closed verification is an open item at the flight readiness review, and there is never a good time to discover one.

---

## Test levels

**Pressure**, from AIAA S-080 and S-081:

| Hardware class | Proof | Burst |
|---|---|---|
| Metallic pressure vessel | 1.5 | 2.0 |
| COPV | 1.5 | 2.5 |
| **Line, hazardous fluid** | **1.5** | **4.0** |
| Line, non-hazardous | 1.5 | 2.5 |
| Component | 1.5 | 2.5 |
| Flexible hose | 1.5 | 4.0 |

The 4.0 on a hazardous fluid line against 2.0 on a pressure vessel is not an inconsistency. A line is thin, exposed, routinely handled, and the consequence of a hydrazine or LOX line rupture is a personnel hazard rather than a mission loss.

**Environmental**, from MIL-STD-1540 and NASA-STD-7002:

| Environment | Acceptance | Qualification |
|---|---|---|
| Random vibration | Flight level, 60 s per axis | **+3 dB, 120 s per axis** |
| Acoustic | Flight level | +3 dB |
| Shock | Not applied | **1.4x flight SRS, 3 per axis** |
| Thermal | Flight range, 4 cycles | **Flight range +/- 10 K, 8 cycles** |
| Thermal vacuum | Not applied | Flight range +/- 10 K |

**The +3 dB and 2x duration are not independent margins.** Under Miner's rule with the standard fatigue exponent of 4, a factor of two in PSD raises stress amplitude by sqrt(2), and sqrt(2)^4 = 4. So 3 dB alone buys a factor of four in equivalent fatigue time; the 2x duration is additional margin on top of that, not the same margin counted twice. Detail in [EnvironmentalTesting.md](EnvironmentalTesting.md).

**Life:** 4x the expected life, at the operating condition, for flight hardware.

---

## Sequence and why it matters

The order is not arbitrary. Five rules, each of which exists because something went wrong once.

**Proof before leak.** Proof can open a marginal joint, and the leak test immediately after is what catches it. A leak test run only before proof proves nothing about the article that will fly.

**Baseline functional early.** The post-environmental functional test only means something compared against a pre-environmental baseline taken on the same article with the same setup.

**Leak after every environmental exposure, not only at the end.** Vibration loosens joints, thermal cycling breaks seals through differential contraction. Testing after each exposure costs a few extra tests and tells you which exposure caused the failure, which is worth far more than the tests cost.

**Life before the final functional.** Wear-out shows as leakage growth and performance drift before it shows as a functional failure, so the instrumentation has to be running throughout the life test rather than bracketing it.

**Burst last.** It destroys the article. Everything you wanted from that unit has to be collected first.

---

## Where the money and schedule go

Roughly, for a component qualification campaign:

| Activity | Share of cost | Share of schedule |
|---|---|---|
| Environmental testing (facility time) | 30 to 40 % | 20 % |
| Life and endurance testing | 15 to 25 % | **40 to 50 %** |
| Test article fabrication | 15 to 25 % | 20 % |
| Instrumentation, setup, fixturing | 10 to 15 % | 15 % |
| Documentation and data packages | 5 to 10 % | 10 % |
| Anomaly investigation | **highly variable** | **highly variable** |

**Life testing dominates the schedule** because it is the one activity that cannot be compressed by spending money, only by acceleration (which requires a defensible model) or by parallelism (which requires more articles).

**Anomaly investigation is the variance.** A campaign with no anomalies runs to plan; one with a single hard failure can double. That is why the anomaly process is worth having defined before it is needed, and it is covered in [AnomalyAndFailureInvestigation.md](AnomalyAndFailureInvestigation.md).

---

## The ten things that go wrong

In rough order of how often they actually happen:

1. **MEOP underestimated**, because a transient was not in its definition. Found at proof if you are lucky.
2. **A leak requirement that cannot be measured**, specified without checking any method's floor.
3. **Qualification and acceptance conflated**, so acceptance consumes flight life.
4. **Pressure decay proposed for a tight leak requirement**, which is temperature-limited and cannot work.
5. **Leak testing only at ambient** on cryogenic hardware, where differential contraction is the failure mechanism.
6. **A pneumatic proof test** where a hydrostatic one would do, storing hundreds of kilojoules unnecessarily.
7. **Life testing at the wrong condition**, demonstrating the actuator rather than the seat.
8. **Qualification by similarity that was not similar**, usually a different environment.
9. **Tailoring by omission**, where a test quietly does not happen because nobody noticed it was required.
10. **No baseline data**, so when something fails in service the investigation has nowhere to start.

Every one is a planning failure rather than a test failure, and every one is catchable before hardware exists.

---

## Document index

| Document | Covers |
|---|---|
| [RequirementsAndVerification](RequirementsAndVerification.md) | The five methods, traceability, the VCRM, what "verified" means |
| [TestCampaignPlanning](TestCampaignPlanning.md) | Levels, matrices, sequencing, tailoring, article count |
| [ProofAndBurstTesting](ProofAndBurstTesting.md) | Levels, hold times, stored energy, the pneumatic hazard |
| [LeakTesting](LeakTesting.md) | Method selection, sensitivity, calibration, where it repeats |
| [FlowAndFunctionalTesting](FlowAndFunctionalTesting.md) | Flow calibration, Cv and Cd determination, cycle and response |
| [EnvironmentalTesting](EnvironmentalTesting.md) | Vibration, shock, thermal, level derivation, Miner scaling |
| [LifeAndEnduranceTesting](LifeAndEnduranceTesting.md) | Life definitions, acceleration, wear-out, what to instrument |
| [CryogenicAndColdShockTesting](CryogenicAndColdShockTesting.md) | Cold functional, cold leak, chilldown, thermal shock |
| [CleanlinessVerification](CleanlinessVerification.md) | Particulate and NVR verification, sampling, oxygen service |
| [TestFacilitiesAndGSE](TestFacilitiesAndGSE.md) | Stands, control systems, safety, hazard zones |
| [InstrumentationAndDataAcquisition](InstrumentationAndDataAcquisition.md) | Sensors, sample rates, calibration chains, recording |
| [UncertaintyAndStatistics](UncertaintyAndStatistics.md) | GUM budgets, sample size, reliability demonstration |
| [AnomalyAndFailureInvestigation](AnomalyAndFailureInvestigation.md) | Containment, root cause, corrective action, closure |
| [TestDocumentation](TestDocumentation.md) | Plans, procedures, as-run redlines, reports, data packages |
| [AcceptanceAndFlightScreening](AcceptanceAndFlightScreening.md) | ATP content, workmanship screens, what acceptance must not do |
| [StandardsIndex](StandardsIndex.md) | Annotated index of the governing standards |

**The design-side counterpart** is [fluidSystemsLibrary/docs/](../../fluidSystemsLibrary/docs/FluidSystemsOverview.md), and in particular [QualificationAndTesting.md](../../fluidSystemsLibrary/docs/QualificationAndTesting.md), which covers the same ground from the design engineer's side. This directory is the test engineer's side of the same conversation.

---

## Class index

| Class | Primary use |
|---|---|
| [`TestCampaign`](../fluidSystemsTestingLibrary/TestCampaign.py) | Build the matrix: which tests, what order, what was tailored and why |
| [`PressureTest`](../fluidSystemsTestingLibrary/PressureTest.py) | Levels, hold times, stored energy, blast standoff, hoop margins |
| [`LeakTest`](../fluidSystemsTestingLibrary/LeakTest.py) | Method selection, per-joint allocation, pressure decay feasibility |
| [`EnvironmentalTest`](../fluidSystemsTestingLibrary/EnvironmentalTest.py) | Grms, qualification levels, Miner duration scaling |
| [`LifeTest`](../fluidSystemsTestingLibrary/LifeTest.py) | Required life, acceleration models, duration and feasibility |
| [`UncertaintyBudget`](../fluidSystemsTestingLibrary/UncertaintyBudget.py) | GUM budget, expanded uncertainty, dominant contributor |
| [`SampleSize`](../fluidSystemsTestingLibrary/SampleSize.py) | Success-run and binomial sample sizes, reliability demonstration |

Every class follows the repository interface: `setInputs()`, `calculate*()`, `generateReport()`, with typed errors carrying context. `TestInfeasibleError` is specific to this library and it means the inputs are valid but the test simply cannot do what is being asked, which is a different problem from a bad input and has a different fix.
