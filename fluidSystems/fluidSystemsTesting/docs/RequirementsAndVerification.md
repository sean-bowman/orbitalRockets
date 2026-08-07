[Home](../README.md) > Requirements and Verification

# Requirements and Verification

## Contents

- [Overview](#overview)
- [The five verification methods](#the-five-verification-methods)
- [Writing a verifiable requirement](#writing-a-verifiable-requirement)
- [The verification cross reference matrix](#the-verification-cross-reference-matrix)
- [Verification versus validation](#verification-versus-validation)
- [Qualification by similarity](#qualification-by-similarity)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A test campaign is the answer to a question, and the question is the requirement set. Planning the campaign before the requirements are verifiable produces a campaign that runs to completion and closes nothing.

The chain is: **requirement -> verification method -> evidence -> closure**. Every link has to hold. A requirement that cannot be verified is not a requirement; it is an aspiration that will be dispositioned by waiver at the flight readiness review, which is the most expensive possible time to discover it.

---

## The five verification methods

| Method | What it is | Cost | Confidence | When it is right |
|---|---|---|---|---|
| **Test** | Subject the article to the condition, measure the response | Highest | Highest | The requirement is measurable and the condition reproducible |
| **Demonstration** | Operate the article, observe the outcome | Medium | High | Functional and operational requirements with no measured quantity |
| **Analysis** | Calculate the response by a validated method | Low | Depends entirely on the method | The condition cannot be reproduced, or test is prohibitive |
| **Inspection** | Examine the article or its records | Lowest | High for what it covers | Dimensional, material, marking, workmanship |
| **Similarity** | Argue from previously qualified hardware | Lowest | **Highly variable** | Design, materials, process AND environment all demonstrably similar |

**Analysis is only as good as the method's validation.** An analysis-verified requirement carries an implicit second requirement: that the analysis method has itself been validated against test data for this class of problem. Programmes routinely verify by analysis using a method nobody has correlated, and the resulting confidence is imaginary.

**Combination is normal and it is usually right.** Most substantive requirements are verified by analysis supported by test at a few points, rather than by test everywhere. The test validates the model and the model covers the envelope.

---

## Writing a verifiable requirement

A requirement is verifiable when four things are unambiguous: the **quantity**, the **value**, the **condition**, and the **method**.

Not verifiable:

> The valve shall have low leakage.

Verifiable:

> The valve shall exhibit an external leak rate no greater than 1.0e-6 scc/s of helium when pressurized to MEOP with the downstream side at ambient, at any temperature between 253 K and 333 K, verified by helium mass spectrometer in the accumulation mode.

The second names the quantity (external leak rate), the value (1.0e-6 scc/s helium), the condition (MEOP, ambient downstream, over a stated temperature range), and the method (mass spec accumulation).

**The condition is the part most often left out**, and it is the part that decides whether the test means anything. A leak requirement without a temperature range gets verified at ambient, and a cryogenic seal passes an ambient leak test right up until it goes cold.

**Check measurability while the requirement is still being written.** The [`LeakTest`](../fluidSystemsTestingLibrary/LeakTest.py) class raises `TestInfeasibleError` when no detection method can see the specified rate with margin, and it is intended to be run at requirement-writing time rather than at test planning time.

---

## The verification cross reference matrix

The VCRM maps every requirement to its method, its evidence and its status. It is the single artifact that answers "are we done".

| Field | What it carries |
|---|---|
| Requirement ID | Traceable to the specification |
| Requirement text | Or a reference to it |
| Verification method | One of the five |
| Verification level | Component, subsystem, system |
| Verification article | Which unit provides the evidence |
| Evidence reference | Test report, analysis report, inspection record |
| Status | Open, in work, closed, waived |

**Every requirement appears exactly once, and every closure points at a document.** A VCRM line closed against "see test campaign" is not closed.

**The matrix is built during requirements definition, not after.** Building it afterwards reliably discovers requirements that nobody planned to verify, at which point the options are an unplanned test or a waiver.

---

## Verification versus validation

**Verification** asks: did we build it to the requirement? **Validation** asks: was the requirement right?

A system can be perfectly verified and completely wrong. The classic fluid system case is a leak requirement picked from a table rather than derived from the hazard: the hardware verifies against 1e-4 scc/s, and the actual exposure limit needed 1e-5. Every VCRM line closes and the system is unsafe.

The [design-side worked example](../../codeInterface.py) derives its leak allowable from the hydrazine exposure limit and the bay volume rather than from a table, which is validation done at the point where it is cheap.

---

## Qualification by similarity

The method that causes the most trouble, because it is nearly free and the argument is rarely written down.

**A similarity claim requires all four:**

1. **Design similarity.** Same configuration, same load paths, same sealing scheme. A dimensional scale is not automatically similar.
2. **Materials similarity.** Same alloys, same tempers, same soft goods. A seal material change invalidates the claim outright.
3. **Process similarity.** Same manufacturer, same processes, same qualified procedures. A supplier change is a process change.
4. **Environment similarity.** The previous qualification environment envelopes the new one, in every axis and every environment.

**Environment is the one that fails.** A component qualified for a 5 g random vibration environment is not qualified for 12 g, and no amount of design similarity fixes that.

**Write the argument down as a document, and have someone who did not write it review it.** A similarity claim made in a slide and never written up is how unqualified hardware flies.

---

## Design rules of thumb

| Rule | Why |
|---|---|
| Quantity, value, condition, method | A requirement missing any of the four is not verifiable |
| Check measurability at writing time | A requirement below every method's floor is a waiver waiting to happen |
| Build the VCRM during requirements definition | Building it after discovers unplanned verifications |
| Every closure points at a document | "See the test campaign" is not evidence |
| Analysis needs a validated method | Otherwise the confidence is imaginary |
| Write the similarity argument down | And have it reviewed by someone else |
| Derive requirements from hazards where one exists | Table-picked values verify and still fail validation |

---

## Failure modes

**An unverifiable requirement.** Discovered at test planning, or worse at the readiness review.

**A requirement with no condition stated.** Verified at whatever condition was convenient, which is usually ambient.

**A VCRM line closed against a document that does not contain the evidence.** Common, and it only surfaces during an audit.

**Verification by analysis with an uncorrelated model.** The number is real and the confidence is not.

**A similarity claim across an environment change.** The single most common invalid similarity argument.

**A requirement verified at the wrong level.** Component-level verification of a requirement that is only meaningful at assembly level, or the reverse.

**Validation skipped entirely.** Everything verifies and the requirement was wrong.

---

## Standards

| Standard | Scope |
|---|---|
| **MIL-STD-1540** | Test requirements for launch, upper stage and space vehicles |
| NASA-STD-7002 | Payload test requirements |
| NASA/SP-2016-6105 | NASA Systems Engineering Handbook: verification and validation process |
| ECSS-E-ST-10-02 | Space engineering: verification |
| ECSS-E-ST-10-03 | Space engineering: testing |
| ISO/IEC/IEEE 15288 | Systems and software engineering, life cycle processes |
| AIAA S-080 | Metallic pressure vessels: verification requirements |

---

## Tool interface

```python
from TestCampaign import TestCampaign
from LeakTest import LeakTest
from campaignUtils import VERIFICATION_METHODS, TestInfeasibleError

# Check measurability while the requirement is still being written
leak = LeakTest()
leak.setInputs({'allowableLeakRate': 1.0e-12, 'testPressure': 2.4e6})
try:
    leak.selectMethod()
except TestInfeasibleError as error:
    print(error)     # no method can see this, renegotiate now rather than later

# The campaign matrix, which is the test-method half of the VCRM
campaign = TestCampaign()
campaign.setInputs({'articleName': 'valve', 'articleType': 'valve', 'fluidHazard': 'toxic'})
matrix = campaign.buildMatrix()
```

---

## References

1. MIL-STD-1540E, *Test Requirements for Launch, Upper-Stage, and Space Vehicles*.
2. NASA/SP-2016-6105 Rev 2, *NASA Systems Engineering Handbook*.
3. NASA-STD-7002B, *Payload Test Requirements*.
4. ECSS-E-ST-10-02C, *Space Engineering: Verification*.
5. INCOSE, *Systems Engineering Handbook*, 5th ed., Wiley, 2023.
