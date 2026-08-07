[Home](../README.md) > Instrumentation and Data Acquisition

# Instrumentation and Data Acquisition

## Contents

- [Overview](#overview)
- [Sensor selection for test](#sensor-selection-for-test)
- [Sample rate](#sample-rate)
- [Calibration and traceability](#calibration-and-traceability)
- [Installation effects](#installation-effects)
- [Data management](#data-management)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The sensor hardware itself is covered in [fluidSystemsLibrary/docs/Instrumentation.md](../../fluidSystemsLibrary/docs/Instrumentation.md). This document is about instrumenting a test: what to measure, how fast, with what traceability, and how to avoid the data losses that make a test unrepeatable.

The governing principle is that **the measurement you did not take is the one the investigation needs.** Test instrumentation is cheap relative to a repeat test, and the marginal channel is almost always worth adding.

---

## Sensor selection for test

Test instrumentation differs from flight instrumentation in three ways: it can be denser, it can be more intrusive, and it must be more accurate, because the test is establishing the truth that flight instrumentation will later be compared against.

| Measurement | Test choice | Why it differs from flight |
|---|---|---|
| Pressure, steady | Precision strain gauge or sputtered thin film | Accuracy over ruggedness |
| Pressure, transient | **Piezoelectric, flush mounted** | Flight has no need for 100 kHz response |
| Temperature, accuracy | **Platinum RTD** | Flight uses thermocouples for ruggedness |
| Temperature, transient | Fine-gauge exposed thermocouple | Response time over durability |
| Flow | **Coriolis** | Direct mass flow, fluid-property independent |
| Displacement | LVDT or DIC | Flight has no equivalent |
| Strain | Foil rosettes | Test only |
| Acceleration | Triaxial, response locations | Denser than flight |

**Range matters more than accuracy class.** A 0.1 percent transducer on a 70 MPa range measuring 2 MPa is 3.5 percent of reading. Match the range to the measurement, and use a separate high-range channel for the transient if one is expected.

**Instrument the response, not just the input.** On a shaker test the control accelerometer says what the fixture saw; response accelerometers on the article say what the article saw, and those are different numbers.

---

## Sample rate

**Sample at least ten times the highest frequency of interest, and anti-alias filter below Nyquist.** Aliased data cannot be recovered and it is convincing: a 100 Hz oscillation sampled at 120 Hz appears as a real 20 Hz oscillation.

| Phenomenon | Content | Minimum rate |
|---|---|---|
| Steady-state trends | < 1 Hz | 10 Hz |
| Valve transients | 10 to 100 Hz | 1 kHz |
| **Water hammer** | 100 Hz to 1 kHz | **10 kHz** |
| **Chilldown slug impacts** | 100 Hz to 1 kHz | **10 kHz** |
| Combustion instability | 100 Hz to 20 kHz | 100 kHz |
| Pyroshock | 100 Hz to 10 kHz | 100 kHz |
| Cavitation acoustics | 1 to 100 kHz | 200 kHz |

**A 10 Hz system will not see a water hammer event at all.** It shows a slightly elevated steady pressure and nothing else, which is exactly how surge damage gets attributed to something else.

**Time synchronization across channels** matters as soon as you want to relate a valve command to a pressure response. Sub-millisecond synchronization is required for any transient work, and it has to be verified rather than assumed.

**Record continuously through the event, not on a trigger**, wherever storage permits. A trigger that fires late loses the onset, which is usually the interesting part.

---

## Calibration and traceability

**Every measurement in a qualification data package needs a traceable calibration chain** back to a national standard.

| Element | Record |
|---|---|
| Instrument | Serial number, calibration date, due date |
| Calibration standard | Its own traceability |
| Calibration method | And the uncertainty it introduces |
| As-found and as-left | As-found matters: it tells you whether the previous data was good |
| Environment during calibration | Temperature especially |

**The as-found reading is the one people skip and it is the important one.** If an instrument is found out of tolerance at its recalibration, every measurement made since the last calibration is suspect. That is a data review, and without as-found records it cannot be bounded.

**Calibrate the chain, not the sensor.** A transducer calibrated in isolation, then connected through a different amplifier and a different data system, has not been calibrated as used. End-to-end calibration through the actual signal path is the defensible practice.

**Bracket sensitive tests with a calibration**, particularly leak testing. Before and after; if they disagree, the data between them is not usable.

---

## Installation effects

**Pressure taps:** flush, no burr, perpendicular to the flow, adequate approach length. A burr at a tap is a several percent reading error and it is invisible once assembled.

**Sensing lines are a low-pass filter and a resonator.** A transducer on a 2 m, 3 mm sensing line has a Helmholtz resonance in the tens of hertz and will show a plausible pressure trace that is not the pressure at the tap. **For transient measurement, mount flush.**

**Thermocouple immersion:** at least ten probe diameters, or the reading is a conduction-weighted mixture of fluid and wall. A thermowell makes the response time the well's response time, which for a transient is the measurement.

**Strain gauge placement** has to be at the predicted critical location, which means the analysis has to come first. A gauge at a convenient location measures a strain nobody predicted and nobody can use.

**Support the cable, not just the sensor.** Cable failure at the connector is the most common instrumentation failure on a test stand.

---

## Data management

**Record more than you think you need.** Storage is cheaper than a repeat test by orders of magnitude.

| Practice | Why |
|---|---|
| Raw data preserved unmodified | Processing can be redone; raw data cannot be recovered |
| Processing scripts under version control | The result has to be reproducible |
| Channel list with locations and units | A channel named `P7` is useless in two years |
| Time-synchronized master clock | Cross-channel comparison depends on it |
| Recording started before the sequence | The most common data loss |
| Backup before leaving the cell | The second most common |

**Name channels meaningfully.** `PT_ValveInlet_Static` survives; `Channel_07` does not.

**Data without a configuration record is not data.** The channel list, the locations and the setup photographs are part of the dataset, not documentation about it.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Sample rate | >= 10x the highest frequency of interest |
| Water hammer, chilldown | >= 10 kHz |
| Anti-alias filter | Below Nyquist, always |
| Range matched to the measurement | Accuracy is % of full scale |
| Flush mount for transients | Sensing lines resonate |
| Thermocouple immersion | >= 10 probe diameters |
| Calibrate end to end | Not the sensor in isolation |
| Record as-found at recalibration | It bounds the suspect data |
| Bracket leak tests with a calibration | Before and after |
| Recording before the sequence | The most common data loss |
| Instrument response, not just input | They are different numbers |

---

## Failure modes

**Aliased transient data.** Convincing and wrong.

**Sensing line resonance reported as a real oscillation.** An artifact of the plumbing to the transducer.

**Transducer destroyed by a surge.** And it was the channel that would have shown the surge.

**Recording armed after the event.** The transient of interest is not in the file.

**Instrument found out of tolerance at recalibration, with no as-found record.** Every measurement since the last calibration is suspect and cannot be bounded.

**Calibration of the sensor but not the chain.** The amplifier gain was never verified.

**Channel names that mean nothing.** The data exists and cannot be interpreted.

**Cable failure at the connector.** The most common stand instrumentation failure.

**No configuration record.** The data cannot be reproduced or defended.

---

## Standards

| Standard | Scope |
|---|---|
| ASME PTC 19.2 | Pressure measurement |
| ASME PTC 19.3 | Temperature measurement |
| ASME PTC 19.5 | Flow measurement |
| **ISO/IEC 17025** | Competence of testing and calibration laboratories |
| **AIAA S-071** | Assessment of experimental uncertainty |
| ISO/IEC Guide 98 (GUM) | Uncertainty of measurement |
| IEST-RP-DTE011 | Mechanical shock and vibration data acquisition |
| NASA-STD-8739 series | Workmanship for instrumentation cabling |
| ANSI/NCSL Z540 | Calibration laboratories and measuring equipment |

---

## Tool interface

```python
from UncertaintyBudget import UncertaintyBudget
from LeakTest import LeakTest

# What the instrumentation choice costs in measurement uncertainty
budget = UncertaintyBudget()
budget.setInputs({'measurand': 'valve Cv', 'measurandValue': 0.348, 'measurandUnit': '-'})
budget.addContributor('flow meter calibration', 0.0035, 'normal k=2', note = 'Coriolis, 0.5 % rdg')
budget.addContributor('pressure transducer',    0.0052, 'normal k=2', note = '0.25 % FS, 5 MPa range')
budget.addContributor('repeatability',          0.0019, 'normal k=1', note = 'sd of 10 runs')
result = budget.calculate()
print(result['dominantContributor'])   # tells you which instrument to improve

# Whether the transducer resolution can support a pressure decay test
leak = LeakTest()
leak.setInputs({'allowableLeakRate': 1e-5, 'testPressure': 2.4e6, 'testVolume': 0.010,
                'transducerResolution': 100.0, 'testDuration': 3600.0})
leak.evaluatePressureDecay()
```

---

## References

1. ASME PTC 19.2, *Pressure Measurement*.
2. AIAA S-071A-1999, *Assessment of Experimental Uncertainty*.
3. ISO/IEC 17025:2017, *General requirements for the competence of testing and calibration laboratories*.
4. Figliola, R. S. and Beasley, D. E., *Theory and Design for Mechanical Measurements*, 6th ed., Wiley, 2015.
