[Home](../README.md) > Anomaly and Failure Investigation

# Anomaly and Failure Investigation

## Contents

- [Overview](#overview)
- [The first hour](#the-first-hour)
- [Classification](#classification)
- [Root cause analysis](#root-cause-analysis)
- [Corrective action](#corrective-action)
- [Closure and the fleet question](#closure-and-the-fleet-question)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes of the investigation itself](#failure-modes-of-the-investigation-itself)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Every campaign has an anomaly. The programmes that handle them well are the ones that decided how before they needed to.

An anomaly is not a failure until it is classified as one. It is an observation that does not match expectation, and roughly half of them turn out to be instrumentation, test setup, or a procedure that was ambiguous.

**The variance in a test programme's cost and schedule is almost entirely anomaly investigation.** A campaign with none runs to plan; one with a single hard failure can double.

---

## The first hour

What happens immediately determines whether the investigation is possible at all.

| Action | Why |
|---|---|
| **Stop. Do not reconfigure anything** | The configuration is evidence and it is destroyed by tidying up |
| **Photograph everything, before touching it** | The single most valuable record and it takes minutes |
| Secure the data | Copy it off the acquisition system immediately |
| Record the as-run state | Valve positions, setpoints, what the operator saw and when |
| Preserve the article | Do not disassemble, do not clean, do not "just have a look" |
| Note the environment | Ambient conditions, who was present, what else was running |
| Write down what happened while it is fresh | Memories reconstruct themselves within hours |

**The most common irrecoverable mistake is disassembly.** Somebody takes the article apart to see what happened, and the evidence of what happened is destroyed in the process. Disassembly is a planned step in an investigation, performed with a written procedure and photography at each stage, not an instinct.

**Do not exercise the hardware to "see if it does it again".** If it does, you have two anomalies and no more information. If it does not, you have destroyed the only occurrence.

---

## Classification

| Class | Meaning | Response |
|---|---|---|
| **Test artifact** | The test setup, instrumentation or procedure caused it | Fix the test, document, repeat |
| **Nonconformance** | The article departs from a requirement | Disposition through the MRB |
| **Design deficiency** | The design does not meet the requirement | Design change, requalify |
| **Requirement error** | The requirement was wrong | Requirement change, revalidate |
| **Operator error** | A procedure was not followed, or could not be | Procedure and training; usually a procedure problem |

**Roughly half of anomalies are test artifacts**, and confirming that is a real investigation rather than an assumption. The instrumentation is guilty until proven innocent: check the calibration, check the channel, check the sensing line, check the ground, before concluding the hardware did something.

**"Operator error" is almost always a procedure problem.** A procedure that can be performed wrongly under time pressure will be. The corrective action is to make the wrong action impossible or obvious, not to retrain somebody.

---

## Root cause analysis

**The fault tree is the tool.** Start from the observed effect and enumerate everything that could produce it, then eliminate branches with evidence rather than with judgement.

**Discipline that makes it work:**

- **Enumerate before eliminating.** The branch nobody wrote down is the one it turns out to be.
- **Eliminate with evidence.** "That could not have happened" is not evidence; a measurement is.
- **Keep multiple hypotheses alive** until one is proven, rather than pursuing the first plausible one.
- **Distinguish the proximate cause from the root cause.** The seal failed (proximate) because it was the wrong material (root) because the drawing called out a dimension and not a part number (systemic).
- **Ask what else the root cause touches.** A drawing practice that produced one wrong seal produced others.

**Five whys is a prompt, not a method.** It works when the chain is linear and it fails when the cause is a combination, which in fluid systems it usually is.

**Reproduce it if you can.** A root cause that cannot be reproduced on demand is a hypothesis. Reproduction on a separate article, deliberately, is the strongest possible evidence, and it is worth an article to get.

---

## Corrective action

| Element | Requirement |
|---|---|
| **Containment** | What stops the problem reaching anything else, right now |
| **Correction** | What fixes this article |
| **Corrective action** | What stops it recurring |
| **Effectiveness verification** | Evidence that the corrective action worked |
| **Extent of condition** | Everything else the root cause could have affected |

**Extent of condition is the step most often skipped and the one that matters most.** If a seal was the wrong material because of a drawing practice, every drawing using that practice is suspect. If a weld was made by an operator whose qualification had lapsed, every weld made in that period is suspect.

**Effectiveness verification is not the same as implementation.** Changing a drawing is implementation; confirming that hardware built to the new drawing is correct is verification, and it takes time that has to be planned.

---

## Closure and the fleet question

**An investigation closes when four things are true:**

1. The root cause is understood and evidenced
2. The extent of condition is bounded
3. The corrective action is implemented and verified effective
4. The disposition of affected hardware is decided and documented

**The fleet question:** does this affect hardware already delivered, already installed, or already flown? It is asked at closure and it is the question that turns a test anomaly into a programme event. Answering it needs traceability that has to exist before the anomaly, which is why configuration management earns its cost.

**Trend the anomalies.** Individually they are events; collectively they are a signal about the design, the process or the organization. Three seal anomalies with three different proximate causes may share a systemic root that no individual investigation would find.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Stop and photograph before touching | The most valuable minutes in the investigation |
| Do not disassemble instinctively | It is a planned step with a procedure |
| Do not re-run to see if it repeats | Two anomalies, no more information |
| Instrumentation is guilty until proven innocent | Half of anomalies are test artifacts |
| Enumerate the fault tree before eliminating | The unwritten branch is the answer |
| Eliminate with evidence, not judgement | "That could not have happened" is not evidence |
| Proximate cause is not root cause | Keep asking what allowed it |
| Extent of condition, always | The most skipped and most important step |
| Effectiveness verification is separate from implementation | And it takes time |
| Trend anomalies across the programme | The systemic cause is invisible individually |

---

## Failure modes of the investigation itself

**Disassembly before documentation.** The evidence is gone and the investigation is now speculation.

**The first plausible hypothesis accepted.** Confirmation bias closes the investigation early and the real cause recurs.

**Proximate cause recorded as root cause.** The seal is replaced with the same wrong material.

**Extent of condition skipped.** The corrective action fixes one article and the fleet still has the problem.

**Corrective action implemented but not verified.** Everyone believes it is fixed.

**"Operator error" as a root cause.** It is a symptom of a procedure problem, and recording it as the cause guarantees recurrence.

**The anomaly closed under schedule pressure.** Investigations closed to meet a date reopen in flight.

**No trending.** Each anomaly is investigated individually and the systemic cause is never seen.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-8739.8** | Software assurance and safety (referenced for problem reporting practice) |
| NASA-HDBK-8739.18 | Root cause analysis |
| NPR 8621.1 | NASA procedural requirements for mishap and close call reporting and investigation |
| **MIL-STD-1520** | Corrective action and disposition system for nonconforming material |
| AS9100 | Quality management for aviation, space and defence, clause 10.2 |
| ISO 9001 | Quality management, nonconformity and corrective action |
| IEC 62740 | Root cause analysis |

---

## Tool interface

The library does not model investigation directly, but two things support it.

**Baseline data is what an investigation compares against.** The flow number, the leak rate and the response time recorded at acceptance are the reference that makes a later measurement interpretable. See [FlowAndFunctionalTesting.md](FlowAndFunctionalTesting.md).

**The design library reproduces the conditions** so a hypothesis can be tested numerically before it is tested on hardware:

```python
from WaterHammer import WaterHammer   # fluidSystems design library

# Hypothesis: the transducer failed because of a surge nobody expected
surge = WaterHammer()
surge.setInputs({'fluid': 'N2H4', 'pressure': 2.3e6, 'temperature': 293.15,
                 'velocity': 2.34, 'innerDiameter': 0.004928, 'wallThickness': 0.000711,
                 'length': 2.5, 'closureTime': 0.005})   # the ACTUAL closure time, measured
surge.calculateSurge()
print(surge.peakPressure)     # compare against the transducer range
```

Re-running the design analysis with the as-measured conditions rather than the as-designed ones is frequently how a test anomaly resolves.

---

## References

1. NASA-HDBK-8739.18, *Root Cause Analysis*.
2. NPR 8621.1D, *NASA Procedural Requirements for Mishap and Close Call Reporting, Investigation, and Recordkeeping*.
3. Dekker, S., *The Field Guide to Understanding Human Error*, 3rd ed., CRC Press, 2014.
4. Vaughan, D., *The Challenger Launch Decision*, University of Chicago Press, 1996.
5. IEC 62740:2015, *Root Cause Analysis*.
