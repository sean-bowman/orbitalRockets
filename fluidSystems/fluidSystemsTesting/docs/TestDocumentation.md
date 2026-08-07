[Home](../README.md) > Test Documentation

# Test Documentation

## Contents

- [Overview](#overview)
- [The document set](#the-document-set)
- [The test plan](#the-test-plan)
- [The test procedure](#the-test-procedure)
- [As-run and redlines](#as-run-and-redlines)
- [The test report](#the-test-report)
- [The data package](#the-data-package)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Documentation is what turns a test into evidence. A test that was run and not documented did not close a requirement, and a test documented badly closes it only until somebody audits it.

The volume is real: documentation is 5 to 10 percent of campaign cost and around 10 percent of schedule. Underestimating it is routine, and the shortfall always lands at the end when the readiness review is already scheduled.

---

## The document set

| Document | Answers | Written |
|---|---|---|
| **Test plan** | What will be tested and why | Before the procedure |
| **Test procedure** | Exactly how, step by step | Before the test |
| **As-run procedure** | What actually happened | During the test |
| **Test report** | What the results mean | After the test |
| **Data package** | The evidence itself | Assembled throughout |

**Each has a different audience.** The plan is read by the programme and the customer; the procedure by the technician executing it; the report by the engineer closing the requirement; the data package by whoever audits it in three years.

---

## The test plan

**Content:**

- Objectives, and the requirements each objective verifies
- Article description and configuration
- Test levels and their derivation, traceable to the environment
- Sequence, and the rationale for the order
- Facility and equipment
- Instrumentation list with locations, ranges and accuracies
- Pass/fail criteria, **quantitative**
- Anomaly and stop-work criteria
- Safety analysis and hazard controls
- Data to be recorded and how it will be reduced
- Schedule and article allocation

**Pass/fail criteria must be quantitative and written before the test.** A criterion of "no significant leakage" is decided after the fact by whoever wants a particular outcome. A criterion of "external leakage no greater than 1.0e-6 scc/s helium at MEOP, measured by mass spectrometer in accumulation mode" is decided by the measurement.

**Stop-work criteria are as important as pass/fail** and they are more often omitted. What observation stops the test? Who has the authority? What is preserved before anything is touched?

---

## The test procedure

**The procedure is written for the person executing it**, not for the engineer who designed the test. That means numbered steps, one action per step, unambiguous language, and a place to record the actual value at every step that produces one.

| Element | Why |
|---|---|
| Numbered, sequential steps | Position in the sequence must be unambiguous |
| One action per step | Two actions in one step get half done |
| Explicit values, not "as required" | "Pressurize as required" is not a step |
| A blank for every measured value | Recorded at the time, not from memory |
| Sign-off at critical steps | And for hazardous operations, a second signature |
| Prerequisites checklist | Configuration, calibration, safety, personnel |
| Hold points | Where the test stops for a decision |
| Restoration steps | Returning the article and stand to a safe state |

**A procedure that cannot be followed under pressure will not be followed under pressure.** If a step is ambiguous, the operator will interpret it, and the interpretation will not be recorded. Walk the procedure with the technician before the test.

**Hold points are where the engineering decision happens.** Building them in deliberately is what stops a technician making an engineering judgement at two in the morning.

---

## As-run and redlines

**The as-run procedure is the primary record of the test.** It is the procedure with the actual values written in, every deviation redlined, and every signature present.

| Rule | Why |
|---|---|
| Record values at the time, in ink | Reconstruction from memory is not data |
| **Redline every deviation, as it happens** | An undocumented deviation invalidates the run |
| Never erase; strike through, initial and date | The original entry is part of the record |
| Note anything unexpected, even if it seems irrelevant | Relevance is established later |
| Time-stamp significant events | Correlating with the data depends on it |

**An undocumented deviation is the most common reason a test has to be repeated.** The data may be perfectly good and there is no way to demonstrate what produced it.

**"It seemed irrelevant at the time" is the phrase that appears in every failure investigation.** Record it anyway.

---

## The test report

**Content:**

- What was tested, in what configuration, when, by whom
- What the procedure was, and every deviation from it
- The results, against the quantitative pass/fail criteria
- **Measurement uncertainty** on every reported value
- Anomalies and their disposition
- **The requirements this test closes**, by identifier
- Conclusions, and what they do not cover

**Report the uncertainty.** A result without one is a number, not a measurement, and a pass margin smaller than the uncertainty is not a pass.

**Name the requirements closed.** The report is the evidence a VCRM line points at, and a report that does not identify what it closes forces somebody to reconstruct the mapping later.

**State what the test does not cover.** A qualification report that implies broader coverage than the test provided is how unqualified hardware flies.

---

## The data package

The archive that has to survive the programme.

| Content | Notes |
|---|---|
| **Raw data, unmodified** | Processing can be redone; raw data cannot be recovered |
| Processing scripts | Under version control, so the reduction is reproducible |
| Channel list | Locations, units, ranges, serial numbers |
| Calibration records | Instrument, standard, dates, as-found and as-left |
| As-run procedures | Signed, with redlines |
| Photographs | Setup, article before and after, any anomaly |
| Configuration record | Drawing revisions, serial numbers, as-built deviations |
| Test report | And any anomaly reports |

**Raw data preserved unmodified is the non-negotiable one.** Every reduction, filter and correction can be redone if the raw data survives. None of them can be undone if it does not.

**Assume nobody will remember anything.** In three years the people are gone and the package is all that exists.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Quantitative pass/fail, written before the test | Otherwise it is decided afterwards |
| Stop-work criteria in the plan | As important as pass/fail |
| One action per step | Two get half done |
| A blank for every measured value | Recorded at the time |
| Redline every deviation as it happens | The most common reason for a repeat |
| Never erase; strike, initial, date | The original entry is the record |
| Report uncertainty on every value | A margin smaller than the uncertainty is not a pass |
| Name the requirements closed | The report is what the VCRM points at |
| Raw data preserved unmodified | Non-negotiable |
| Walk the procedure with the technician | Ambiguity surfaces immediately |
| Budget 10 % of schedule for documentation | It is always underestimated |

---

## Failure modes

**Qualitative pass/fail criteria.** Decided after the fact by whoever prefers a particular outcome.

**An undocumented deviation.** Good data that cannot be defended, and a repeat test.

**Values recorded from memory after the run.** Not data.

**No uncertainty reported.** A marginal pass that may be a fail.

**The report does not identify the requirements closed.** The mapping is reconstructed later, badly.

**Raw data overwritten by processed data.** Irrecoverable.

**A procedure written for the engineer, executed by a technician.** Interpreted, and the interpretation is unrecorded.

**Documentation left to the end.** The readiness review is scheduled and the package is not started.

**Configuration not recorded.** The result cannot be tied to a specific hardware build.

---

## Standards

| Standard | Scope |
|---|---|
| **MIL-STD-1540** | Test requirements, including documentation content |
| NASA-STD-7002 | Payload test requirements |
| **AS9100** | Quality management for aviation, space and defence |
| ISO/IEC 17025 | Testing and calibration laboratory competence, including reporting |
| ASME PTC 1 | General instructions for performance test codes |
| ECSS-E-ST-10-03 | Space engineering: testing |
| NASA-STD-8739 series | Workmanship, including record requirements |

---

## References

1. MIL-STD-1540E, *Test Requirements for Launch, Upper-Stage, and Space Vehicles*.
2. ISO/IEC 17025:2017, *General requirements for the competence of testing and calibration laboratories*.
3. AS9100D, *Quality Management Systems -- Requirements for Aviation, Space and Defense Organizations*.
4. NASA/SP-2016-6105 Rev 2, *NASA Systems Engineering Handbook*.
