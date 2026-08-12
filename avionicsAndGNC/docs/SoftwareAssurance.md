[Home](../README.md) > Software Assurance

# Software Assurance

## Contents

- [Overview](#overview)
- [Why software is different](#why-software-is-different)
- [The process](#the-process)
- [Coding standards](#coding-standards)
- [Autocoding](#autocoding)
- [Verification against validation](#verification-against-validation)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Flight software is the only subsystem on the vehicle with no random failures, and that changes everything about how it is assured.

---

## Why software is different

**Every software failure is a design failure.** A bolt fails randomly and a line of code does not: it does exactly what it says every time, and if what it says is wrong it is wrong every time.

Three consequences follow and all three are uncomfortable.

**Redundancy does not help.** Three copies of the same program hit the same fault simultaneously and vote unanimously for the wrong answer. See [FlightComputers](FlightComputers.md). Only dissimilar software addresses this, and it costs a second development by a separate team.

**Reliability numbers do not mean what they mean elsewhere.** A mean time between failures is a statement about a random process, and there is no random process here. Software reliability figures are statements about testing coverage dressed as statements about hardware.

**Testing shows the presence of faults, not their absence**, and the state space is far too large to cover. That is why the assurance is in the *process* rather than in the test count.

---

## The process

The shape is common across the standards even though the details differ.

**Requirements**, traceable to the system requirements, and each one testable. **A requirement that cannot fail a test is not a requirement**, which is the same principle [fluidSystemsTesting](../../fluidSystems/fluidSystemsTesting/) applies to hardware.

**Design**, reviewed against the requirements.

**Code**, reviewed against the design and against a coding standard.

**Unit test**, with a coverage criterion. Statement coverage is weak, branch coverage is better, and modified condition decision coverage is what the safety-critical standards ask for.

**Integration test** on the target hardware, because a compiler and a processor are part of the system.

**Traceability throughout**, so that every requirement maps to a test and every line of code maps to a requirement. **The orphaned code is what the trace is for**: code with no requirement behind it is either dead or undocumented, and both are findings.

---

## Coding standards

A coding standard for flight software exists to remove constructs whose behaviour is hard to reason about, not to enforce a house style.

The usual restrictions: no dynamic memory allocation after initialisation, because a failed allocation in flight has no good handling; bounded loops, so that execution time is provable; no recursion, so that stack use is provable; restricted pointer use; and every function's return value checked.

**The common thread is provability rather than elegance.** Each restriction turns a runtime question into a compile-time or review-time one, and on a vehicle there is no runtime to ask questions in.

---

## Autocoding

Generating flight code from a model, usually the control law model.

**What it buys** is that the thing tested in simulation and the thing that flies are the same artefact, which removes an entire class of transcription error, and that a model change propagates without a manual edit.

**What it costs** is that the generator becomes flight-critical. A qualified generator is expensive and an unqualified one means the generated code needs the same review as hand code, which removes most of the benefit.

**And the generated code is not the artefact anybody reads**, which makes a review of it much less effective than a review of the model. So the assurance moves to the model, and the model has to be assured to the standard the code would have been.

---

## Verification against validation

Worth separating because the words get swapped and the distinction matters.

**Verification** asks whether the software was built right: does it meet its requirements.

**Validation** asks whether the right software was built: are the requirements the right ones.

**Verification is tractable and validation is not.** A wrong requirement, correctly implemented and thoroughly verified, flies. That is the failure mode that survives a good process, and the defence is review by people who understand the vehicle rather than the software.

---

## Design rules of thumb

- **Make every requirement testable**, and check that each can fail.
- **Trace both ways.** Requirement to test, and code to requirement.
- **Do not count on redundancy for software.** It is a design failure, not a random one.
- **Restrict the language for provability**, not for style.
- **If you autocode, assure the model** to the standard the code would have needed.
- **Review requirements with vehicle engineers.** Validation is the failure that survives verification.

---

## Failure modes

**Redundant identical software.** Unanimous and wrong.

**A software reliability figure quoted as a hardware one.** Different kind of claim entirely.

**Statement coverage reported as coverage.** Weak, and it looks like a number.

**Orphaned code.** Dead or undocumented, and both are findings.

**A correct implementation of a wrong requirement.** Survives verification and flies.

---

## References

- NASA-STD-8739.8, *Software Assurance and Software Safety Standard*, not read here
- NASA-HDBK-2203, *NASA Software Engineering Handbook*, not read here
- DO-178C, *Software Considerations in Airborne Systems*, not read here
- [FlightComputers](FlightComputers.md), for the common mode argument
