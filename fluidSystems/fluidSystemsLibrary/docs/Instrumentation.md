[Home](../../README.md) > Instrumentation

# Instrumentation

## Contents

- [Overview](#overview)
- [Pressure measurement](#pressure-measurement)
- [Temperature measurement](#temperature-measurement)
- [Flow measurement](#flow-measurement)
- [Level and quantity gauging](#level-and-quantity-gauging)
- [Position and valve state](#position-and-valve-state)
- [Installation effects](#installation-effects)
- [Sample rate and dynamics](#sample-rate-and-dynamics)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Instrumentation is the only thing standing between a fluid system and an unexplained anomaly. Two principles govern the design:

**Instrument for the questions you will have to answer, not for the ones you expect.** Every propulsion test program generates questions that were not anticipated, and the ones that can be answered are the ones where a sensor happened to be. Retrofitting a port into an assembled system is far more expensive than installing one.

**Every port is a leak path and a stress concentration.** The tension is real and it is resolved by being deliberate rather than by defaulting to either extreme.

---

## Pressure measurement

| Type | Range | Accuracy | Response | Notes |
|---|---|---|---|---|
| **Strain gauge (bonded foil)** | 0 to 100+ MPa | 0.1 to 0.5 % FS | kHz | The workhorse. Robust, wide range |
| **Silicon piezoresistive** | 0 to 70 MPa | 0.05 to 0.25 % FS | 10s of kHz | Better accuracy, more temperature sensitive |
| **Sputtered thin film** | 0 to 200 MPa | 0.1 % FS | kHz | Excellent stability and long term drift |
| **Piezoelectric** | dynamic only | -- | 100s of kHz | **AC coupled: cannot measure steady pressure.** For transients and combustion instability |
| Capacitive | low ranges | 0.05 % FS | 100s of Hz | Good at low pressure and vacuum |
| Bourdon gauge | any | 1 to 2 % FS | slow | Local indication. Never a data source |

**Range selection.** Accuracy is quoted as a percentage of **full scale**, so a 0.25 percent transducer on a 70 MPa range is +/- 175 kPa regardless of the reading. Measuring a 2 MPa pressure with it gives 9 percent error. **Match the range to the measurement**, and use a separate high-range transducer for the pressures that need it.

**Overrange protection.** A transducer sized for the operating pressure will be destroyed by a water hammer surge. See [WaterHammer.md](WaterHammer.md). Either size for the surge, or protect with a snubber (which destroys the frequency response), or accept that transducers are consumables.

**Absolute versus gauge versus differential.** State which. A gauge transducer reads zero at ambient and its reading changes with altitude and weather. An absolute transducer is unambiguous and is the right default for anything that flies.

**Temperature sensitivity** is often the dominant error in a cryogenic installation. A transducer qualified at ambient and used at 90 K has a zero shift and a span shift that must be characterized, not assumed.

---

## Temperature measurement

| Type | Range | Accuracy | Response | Notes |
|---|---|---|---|---|
| **Type K thermocouple** | 73 to 1500 K | +/- 2.2 K or 0.75 % | fast | General purpose. Poor below 100 K |
| **Type T thermocouple** | 20 to 620 K | +/- 1.0 K or 0.75 % | fast | The cryogenic thermocouple |
| **Type E thermocouple** | 20 to 1150 K | +/- 1.7 K | fast | Highest output; good for small dT |
| **Platinum RTD (PT100)** | 20 to 850 K | **+/- 0.1 K** | slow | Much more accurate and much slower. The reference |
| Silicon diode | 1.4 to 500 K | +/- 0.1 K | medium | The cryogenic standard below 20 K |
| Thermistor | 200 to 400 K | +/- 0.1 K | medium | Narrow range, very sensitive |
| Infrared | surface only | +/- 2 % | fast | Non-contact; emissivity dependent |

**Thermocouples measure the difference between the junction and the reference**, so the cold junction compensation is part of the measurement. A thermocouple with a poorly characterized reference is a poorly characterized measurement.

**Fluid temperature versus wall temperature** is a decision, not a detail. A probe in the flow reads the fluid (with a recovery factor correction at high velocity); a surface-mounted sensor reads the wall. During chilldown the wall is what you are waiting for; during operation the fluid is usually what you want. Instrument both where it matters.

**Immersion depth.** A probe that does not reach the flow reads a mixture of fluid and wall temperature weighted by the conduction along the probe. A rule of thumb is ten probe diameters of immersion, and a thermowell makes it worse by adding another conduction path.

**Response time.** A bare thermocouple responds in milliseconds; the same thermocouple in a thermowell responds in seconds. For a transient measurement, the well is the measurement.

---

## Flow measurement

| Type | Accuracy | dP cost | Notes |
|---|---|---|---|
| **Coriolis** | **0.1 to 0.5 % of reading** | low | Direct mass flow, fluid property independent. Expensive, heavy, sensitive to vibration |
| **Turbine** | 0.5 to 1 % of reading | low | Volumetric. Needs a density measurement for mass flow. Bearings wear and are the life limit |
| **Venturi** | 0.5 to 1 % | 5 to 20 % of dP | Low permanent loss, no moving parts. Large and heavy |
| **Orifice plate** | 0.5 to 1 % (ISO 5167) | 40 to 75 % of dP | Cheap, well characterized, high permanent loss. See [Orifices.md](Orifices.md) |
| Ultrasonic | 0.5 to 2 % | none | Non-intrusive, clamp-on options. Sensitive to profile and to two-phase |
| Vortex shedding | 1 % | moderate | No moving parts, wide range. Poor at low flow |
| Positive displacement | 0.1 to 0.5 % | high | Very accurate, mechanical, limited to clean fluids |

**Accuracy quoted "of reading" versus "of full scale" is the important distinction.** A Coriolis meter at 0.2 percent of reading holds that accuracy across its turndown; an orifice plate at 0.5 percent of full scale is 5 percent at 10 percent flow.

**Straight run requirements** are real and they are the most common cause of a flow meter reading wrong. ISO 5167 specifies 10 to 44 diameters upstream depending on the disturbance and the beta ratio. Violating them is not recoverable by calibration, because the error depends on the specific upstream geometry.

**Two-phase flow defeats most meters.** A turbine spins up on the vapor, a Coriolis meter reads a mixture density, and an orifice plate sees a two-phase multiplier it was not calibrated for. Cryogenic flow measurement during chilldown is essentially not possible with a conventional meter.

**The alternative for propulsion:** many test programs do not measure flow directly at all. They measure tank level change (for the integral), and chamber pressure with a known throat area and c* (for the instantaneous rate). Both are indirect and both are often more reliable than a meter in a transient.

---

## Level and quantity gauging

| Method | Environment | Notes |
|---|---|---|
| **Capacitance probe** | Ground and flight | Continuous level from the dielectric difference between liquid and vapor. Standard for cryogens |
| **Differential pressure** | Ground, 1-g | Head between top and bottom. Simple, needs a known density |
| **Point sensors (thermistor, optical)** | Both | Discrete wet/dry indication. Used in arrays for coarse level |
| **PVT gauging** | Flight, gas-pressurized | Infer propellant from pressure, volume and temperature of the ullage. Accuracy degrades as the tank empties |
| **Thermal gauging** | Flight | Heat the tank and measure the temperature response; the thermal mass indicates the propellant |
| **Bookkeeping** | Flight | Integrate the commanded flow. Accumulates error, but it is free |

**Zero-g gauging is genuinely hard.** The liquid is not at the bottom, so level means nothing. PVT is the usual method and its accuracy falls off exactly when it matters most, at end of mission when the remaining propellant is small and the ullage is large.

---

## Position and valve state

**Indicate on the stem, not on the actuator**, wherever valve position matters for safety. A limit switch on the actuator will happily report "closed" for a valve whose stem has sheared.

| Type | Notes |
|---|---|
| Limit switch | Discrete, robust, two positions only |
| LVDT | Continuous position, high accuracy, needs conditioning electronics |
| Hall effect / magnetic | Non-contact, no penetration of the pressure boundary. Preferred where a seal would otherwise be needed |
| Potentiometer | Cheap continuous position; wear limited |

**Valve open/closed indication is not the same as valve function.** A valve can indicate open and be blocked, or indicate closed and be leaking. Where it matters, verify function by a downstream pressure or flow measurement rather than by position alone.

---

## Installation effects

**Pressure taps:**

- Flush with the wall, no burr, no protrusion. A burr at a tap produces a local stagnation or separation and a reading error of several percent
- Perpendicular to the flow
- Tap diameter 2 to 10 percent of the pipe diameter; too small and the response is slow, too large and it disturbs the flow
- Adequate straight run upstream, particularly for a differential measurement
- A sensing line to a remote transducer adds a time constant and a resonance. For dynamic measurement, mount the transducer flush at the wall

**Sensing line dynamics** deserve a specific warning. A transducer connected by a 2 m, 3 mm sensing line has a Helmholtz resonance in the tens of hertz and a low-pass response above it. It will show a plausible-looking pressure trace that is not the pressure at the tap. For anything transient, mount flush or use a very short, stiff sensing line.

**Thermal isolation.** A transducer on a cryogenic line will be at cryogenic temperature unless it is isolated. Either qualify it cold or provide a standoff, and note that a standoff full of liquid still conducts.

**Vibration.** Cantilevered sensors and their cabling fail in vibration at the mount. Support the cable, not just the sensor.

---

## Sample rate and dynamics

**Sample at least ten times the highest frequency of interest**, and anti-alias filter below the Nyquist frequency. Data that has aliased cannot be recovered.

| Phenomenon | Frequency content | Minimum sample rate |
|---|---|---|
| Steady-state trends | < 1 Hz | 10 Hz |
| Valve transients | 10 to 100 Hz | 1 kHz |
| **Water hammer** | **100 Hz to 1 kHz** | **10 kHz** |
| Combustion instability | 100 Hz to 20 kHz | 100 kHz |
| Cavitation, acoustic | 1 to 100 kHz | 200 kHz |

**A 10 Hz data system will not see a water hammer event at all.** It will show a slightly elevated steady pressure and nothing else, which is exactly how surge damage gets attributed to something else. See [WaterHammer.md](WaterHammer.md).

**Time synchronization** across channels matters as soon as you want to relate a valve command to a pressure response. Sub-millisecond synchronization is required for any transient work.

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Match transducer range to the measurement | Within 2x | Accuracy is % of full scale |
| Protect transducers from surge | Size for it, or accept consumables | Water hammer exceeds operating pressure |
| Absolute, not gauge, for flight | Always | Gauge readings change with ambient |
| Immersion depth | >= 10 probe diameters | Conduction error |
| Flow meter straight run | Per ISO 5167, 10 to 44 D | Not recoverable by calibration |
| Sample rate | >= 10x the highest frequency of interest | Aliasing is unrecoverable |
| Water hammer sampling | >= 10 kHz | A 10 Hz system sees nothing |
| Sensing lines for dynamic measurement | Flush mount, or very short and stiff | Helmholtz resonance |
| Valve position indication | On the stem | The actuator can lie |
| Every port is a leak path | Be deliberate, not reflexive | And a stress concentration |
| Instrument for the unexpected question | Add the port now | Retrofit is far more expensive |

---

## Failure modes

**Transducer destroyed by surge.** Very common, and the transducer that would have shown the surge is the one that fails.

**Sensing line resonance mistaken for a real pressure oscillation.** A plausible trace that is an artifact of the plumbing to the transducer.

**Thermocouple reading the wall instead of the fluid.** Inadequate immersion or a thermowell.

**Flow meter reading wrong from inadequate straight run.** No amount of recalibration fixes it.

**Aliased transient data.** A 100 Hz oscillation sampled at 120 Hz appears as a 20 Hz oscillation. Convincing and wrong.

**Cryogenic zero shift.** A transducer characterized at ambient and used cold reads a bias that looks like a real pressure.

**Cable failure at the connector in vibration.** The most common instrumentation failure on a test stand.

**Port leak.** Every penetration is a leak path and instrumentation ports are frequently the leakiest joints on a system, because they are small, numerous and installed last.

**Position indication disagreeing with valve state.** Actuator-mounted switches.

---

## Standards

| Standard | Scope |
|---|---|
| ASME PTC 19.2 | Pressure measurement |
| ASME PTC 19.3 | Temperature measurement |
| ASME PTC 19.5 | Flow measurement |
| ISO 5167 | Flow measurement by pressure differential devices |
| ASTM E230 | Temperature-electromotive force tables for standardized thermocouples |
| IEC 60751 | Industrial platinum resistance thermometers |
| ISA-20 | Specification forms for process measurement and control instruments |
| SAE AS8006 | Minimum performance standard for pressure instruments |
| NASA-STD-8739 series | Workmanship standards for instrumentation cabling and connectors |
| AIAA S-071 | Assessment of experimental uncertainty |
| ISO/IEC Guide 98 (GUM) | Uncertainty of measurement |

---

## Tool interface

The library does not model instrumentation directly, but three calculations bear on it:

```python
from LeakPath import LeakPath
from WaterHammer import WaterHammer
from Orifice import Orifice

# Pressure decay test feasibility: what a transducer resolution can actually detect
leak = LeakPath()
leak.setInputs({'species': 'He', 'upstreamPressure': 2.5e6, 'temperature': 293.15,
                'leakRate': 1e-5, 'leakRateUnit': 'sccs'})
leak.calculatePressureDecayTest(testVolume = 0.01,
                                transducerResolution = 100.0,   # transducer resolution [Pa]
                                testDuration = 3600.0,
                                temperatureStability = 0.1)
# reports whether the test is transducer-limited or temperature-limited

# Surge magnitude, which sets the transducer range and the sample rate requirement
surge = WaterHammer()
surge.setInputs({'fluid': 'Water', 'pressure': 1.0e6, 'temperature': 293.15,
                 'velocity': 3.0, 'innerDiameter': 0.05, 'wallThickness': 0.003,
                 'length': 20.0, 'closureTime': 0.020})
surge.calculateSurge()
print(surge.peakPressure)     # transducer range
print(surge.pipePeriod)       # the event timescale sets the sample rate

# ISO 5167 metering orifice, including the permanent pressure loss the measurement costs
meter = Orifice()
meter.setInputs({'fluid': 'Water', 'upstreamPressure': 1.0e6, 'downstreamPressure': 0.98e6,
                 'upstreamTemperature': 293.15, 'diameter': 0.05, 'pipeDiameter': 0.10,
                 'model': 'plate', 'tappings': 'flange'})
meter.calculateMassFlow()
print(meter.dischargeCoefficient, meter.permanentPressureLoss)
```

---

## References

1. ASME PTC 19.2, *Pressure Measurement*.
2. ASME PTC 19.3, *Temperature Measurement*.
3. ISO 5167-1 to -4, *Measurement of fluid flow by means of pressure differential devices*.
4. Beckwith, T. G., Marangoni, R. D. and Lienhard, J. H., *Mechanical Measurements*, 6th ed., Pearson, 2007.
5. Figliola, R. S. and Beasley, D. E., *Theory and Design for Mechanical Measurements*, 6th ed., Wiley, 2015.
6. NIST Special Publication 250-35, *Cryogenic Thermometry*.
7. AIAA S-071A-1999, *Assessment of Experimental Uncertainty with Application to Wind Tunnel Testing*.
8. Sutton, G. P. and Biblarz, O., *Rocket Propulsion Elements*, 9th ed., Wiley, 2016 (test instrumentation chapter).
