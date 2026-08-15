[Home](../README.md) > Standards Index

# Standards Index

## Contents

- [Overview](#overview)
- [Software assurance](#software-assurance)
- [Data buses](#data-buses)
- [Telemetry](#telemetry)
- [Radiation](#radiation)
- [Electromagnetic](#electromagnetic)
- [What was not read](#what-was-not-read)
- [References](#references)

---

## Overview

**Every standard in this index was not read**, which is a shorter and more honest statement than any of the other domains can make.

That is a consequence of what this domain is. Its three classes compute integration orders, moment balances and bit rates, and none of those is defined by a standard. The standards here govern *process* and *interface*, and the documents describe both without carrying their numbers.

Where a number is carried it is representative and registered as such in [ValidationReferences](ValidationReferences.md).

---

## Software assurance

**NASA-STD-8739.8**, *Software Assurance and Software Safety Standard*, and **NASA-HDBK-2203**, the *NASA Software Engineering Handbook*. Between them they define the classification of flight software, the assurance activities required at each class, and the evidence expected.

**DO-178C**, *Software Considerations in Airborne Systems and Equipment Certification*, is the civil aviation equivalent and is the more widely known of the two lineages. Its design assurance levels A through E and its coverage criteria, including modified condition decision coverage, are what [SoftwareAssurance](SoftwareAssurance.md) describes.

**None read.** The process shape in that document comes from general practice, and the coverage criteria are named rather than defined.

**This is the largest gap in the domain by consequence**, because software assurance is the one part of avionics where the standard *is* the method. There is no calculation underneath it to fall back on.

---

## Data buses

**MIL-STD-1553**, the command-response multiplexed data bus. Dual redundant, transformer coupled, one bus controller polling up to 31 remote terminals, 1 Mbit/s.

**Not read**, and [DataBusesAndNetworks](DataBusesAndNetworks.md) carries only its architectural properties: that determinism comes from the controller owning every transaction, and that the bandwidth is low by any modern measure and sufficient for command and control.

**ARINC 429** and the time-triggered Ethernet variants are named in the same document and equally unread.

The consequence is bounded, because the domain's timing argument is about latency accumulating into phase margin rather than about any particular bus. **83 ms of loop delay costs 30 degrees of phase at 1 Hz** regardless of what carries the bits.

---

## Telemetry

**IRIG 106**, the *Telemetry Standards* of the Range Commanders Council, and the **CCSDS** recommendations for space data link protocols. They define frame structures, synchronisation patterns, error correction coding and the resulting overhead.

**Neither read.** `FRAMING_OVERHEAD` in this library is a representative fraction, and [TelemetryAndInstrumentation](TelemetryAndInstrumentation.md) says so.

**What the overhead cannot change** is the domain's telemetry result: that twelve channels out of ninety three carry three quarters of the bandwidth. That is a property of the measurement list, and a framing fraction multiplies both sides of it.

---

## Radiation

**No standard is carried here at all**, and it is worth saying why rather than listing one.

Single event effects and total ionising dose are environment-specific. A launch vehicle spends minutes below the belts and a satellite spends years inside them, and the parts selection that follows differs by orders of magnitude in cost. [FlightComputers](FlightComputers.md) makes exactly that argument and stops there.

**NASA-HDBK-1002** is named in that document as the reference for the environment. Not read.

---

## Electromagnetic

**MIL-STD-461** and **MIL-STD-464** govern emissions, susceptibility and the system-level electromagnetic environment.

They are indexed in [electricalPower](../../electricalPower/docs/StandardsIndex.md) rather than here, because that is where the harness and the grounding topology live. **Neither is read there either.**

Avionics is the victim rather than the owner of most EMC problems, which is why the standard sits in the other domain and the consequence lands in this one.

---

## What was not read

The whole list, since it is the whole index.

| Standard | Would fix |
|---|---|
| NASA-STD-8739.8 | Assurance activities by software class |
| NASA-HDBK-2203 | The engineering process, in detail |
| DO-178C | Design assurance levels and coverage criteria |
| MIL-STD-1553 | Bus electrical and protocol detail |
| IRIG 106 / CCSDS | Framing overhead, currently representative |
| NASA-HDBK-1002 | The radiation environment |
| MIL-STD-461 / 464 | Emissions and susceptibility, indexed in electricalPower |

**And one that is not a standard**: an IMU datasheet. Every manufacturer publishes bias, random walk and scale factor for every grade, and that single document would move [SensorsAndNavigation](SensorsAndNavigation.md) from representative to anchored.

**It was called the most tractable gap here until somebody tried to close it.** The Analog Devices ADIS16507 datasheet was attempted through the manufacturer, two distributors and two mirrors, and every route returned a block page or timed out. Secondary summaries quoting a bias stability and a random walk were found and are deliberately not recorded: this repository has been wrong three times by trusting a summary of a document it had not read. **The same shape of gap in [electricalPower](../../electricalPower/docs/ValidationReferences.md) closed on the first attempt**, which is the difference between a manufacturer that serves a PDF and one that does not.

---

## References

- NASA-STD-8739.8, NASA-HDBK-2203, DO-178C
- MIL-STD-1553, ARINC 429
- IRIG 106, *Telemetry Standards*, Range Commanders Council
- CCSDS space data link recommendations
- NASA-HDBK-1002, for the space radiation environment
- [ValidationReferences](ValidationReferences.md)
