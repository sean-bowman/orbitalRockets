[Home](../../README.md) > Qualification and Testing

# Qualification and Testing

## Contents

- [Overview](#overview)
- [The pressure vocabulary](#the-pressure-vocabulary)
- [Factors of safety](#factors-of-safety)
- [Proof and burst testing](#proof-and-burst-testing)
- [Leak testing](#leak-testing)
- [Environmental qualification](#environmental-qualification)
- [Life and cycle testing](#life-and-cycle-testing)
- [Qualification approaches](#qualification-approaches)
- [Acceptance testing](#acceptance-testing)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Qualification is the demonstration that a design meets its requirements with margin. Acceptance is the demonstration that a specific article was built to that design. They are different activities with different test levels and they are frequently conflated on programs, always to the program's cost.

The governing structure:

```
DESIGN  ->  ANALYSIS  ->  QUALIFICATION TEST (one or more articles, to margin, may be destructive)
                       ->  ACCEPTANCE TEST (every flight article, to operating levels, non-destructive)
```

---

## The pressure vocabulary

These terms are used loosely in conversation and precisely in specifications. Getting them wrong propagates into the design.

| Term | Definition |
|---|---|
| **MEOP** | Maximum Expected Operating Pressure. The highest pressure the component sees in service, including transients, thermal effects and relief valve accumulation. **Not the nominal operating pressure** |
| **MAWP** | Maximum Allowable Working Pressure. The highest pressure the component is rated for, from the code calculation |
| **Design pressure** | The pressure used in the design calculation. Should equal or exceed MEOP |
| **Proof pressure** | The test pressure applied to demonstrate strength without yielding. `proof factor x MEOP` |
| **Burst pressure** | The pressure at which the component fails. `burst factor x MEOP` |
| **Operating pressure** | What it actually runs at day to day |

**MEOP is where the errors start.** It must include:

- The nominal operating pressure
- The regulator outlet band maximum, not the setpoint. See [FlowControlDevices.md](FlowControlDevices.md)
- Relief valve set pressure plus accumulation, if the relief can lift
- Water hammer surge, if the transient reaches this component. See [WaterHammer.md](WaterHammer.md)
- Thermal pressure rise from a locked-up volume warming
- Blowdown initial pressure, for a blowdown system

A design where MEOP was taken as the nominal operating pressure has no margin at all against a transient, and it will be discovered at proof test or, worse, in service.

---

## Factors of safety

**AIAA S-080** (metallic pressure vessels) and **AIAA S-081** (COPVs) govern flight hardware. The factors depend on the component class and on the verification approach:

| Component class | Proof factor | Burst factor | Notes |
|---|---|---|---|
| **Metallic pressure vessel** | 1.5 | 2.0 | With fracture control; higher without |
| **COPV** | 1.5 | **2.0 to 2.5** | Higher for composite; stress rupture governs |
| **Lines and fittings, hazardous fluid** | 1.5 | **4.0** | The hazard drives the burst factor |
| Lines and fittings, non-hazardous | 1.5 | 2.5 to 4.0 | |
| Components (valves, regulators) | 1.5 | 2.5 | |
| Hoses and flexible lines | 1.5 | 4.0 | |
| Ground support equipment | Per ASME B31.3 | Per ASME B31.3 | Different regime entirely |

**The 4.0 burst factor on hazardous fluid lines** is worth noting: it is much higher than the 2.0 on a pressure vessel, because a line is thin, exposed, handled, and the consequence of a hydrazine or LOX line rupture is a personnel hazard rather than a mission loss.

**ASME B31.3** governs ground piping and works differently: it does not use a burst factor at all. It sets an allowable stress (the lesser of two thirds of yield and one third of ultimate) and requires a 1.5x hydrostatic proof test. The two systems are not interchangeable and a component qualified to one is not automatically acceptable under the other.

**Fracture control.** For a pressure vessel whose failure is catastrophic, a fracture control program (NASA-STD-5019) replaces or supplements the burst factor with a demonstrated flaw tolerance: assume the largest flaw the inspection can miss, show it will not grow to critical over the design life. That is a substantially more rigorous and more expensive path, and it is what allows a lower burst factor.

---

## Proof and burst testing

**Proof test** demonstrates that the article can take its design load without permanent deformation or leakage. It is applied to **every flight article** as an acceptance test.

- **Use a liquid where possible.** A liquid proof test stores almost no energy: if the article fails, it leaks. A pneumatic proof test at the same pressure stores enough energy to be genuinely dangerous, because the gas expands.
- **If a pneumatic proof is unavoidable**, barricade, clear the area to a calculated distance, and use remote pressurization and monitoring. The stored energy is `E = P * V / (gamma - 1) * [1 - (P_ambient/P)^((gamma-1)/gamma)]` and it should be calculated, not assumed to be small.
- **Measure permanent set.** The pass criterion is usually no detectable permanent deformation, which requires a dimensional measurement before and after, not just an absence of leaks.
- **Proof before leak test**, because proof can open a marginal joint and the leak test should find it.

**Burst test** demonstrates the ultimate capability. It is destructive, so it is a **qualification** test on dedicated articles, not an acceptance test.

- Minimum of three articles for a statistically meaningful result
- Record the failure location and mode; a burst that occurs somewhere other than the predicted location means the analysis was wrong even if the pressure was adequate
- Burst at temperature if the service temperature reduces the material strength

---

## Leak testing

Covered in detail in [Leaks.md](Leaks.md). The qualification-specific points:

**Test at the conditions that matter**, which means:

- At MEOP, not at a convenient pressure
- **At temperature.** A seal that passes at ambient can fail cold; leak testing at ambient does not qualify a cryogenic joint
- **After proof**, so that any joint opened by the proof test is caught
- **After the environmental exposures**, so that vibration and thermal cycling damage is caught
- **In the direction the seal will see**, since a pressure-energized seal may not seal in reverse

**Specify a rate that can be measured** with a factor of ten of margin above the method floor.

**Bracket every test with a calibrated leak standard.** Sensitivity before and after; if they disagree, the data between them is not usable.

---

## Environmental qualification

| Environment | Purpose | Typical qualification level |
|---|---|---|
| **Random vibration** | Launch environment | Acceptance + 3 dB, 2 min/axis (accept 1 min/axis) |
| Sine vibration | Low frequency launch transients | 1.25 to 1.5x flight, per axis |
| **Shock** | Stage and fairing separation, pyrotechnics | 1.4x flight SRS, 3 per axis |
| **Thermal vacuum** | On-orbit environment | Flight range +/- 10 K, 8 cycles (accept 4) |
| Thermal cycling | Thermal fatigue | Flight range plus margin, cycles per life plus factor |
| **Humidity** | Storage and transport | Per MIL-STD-810 |
| Salt fog | Coastal launch site | Per MIL-STD-810, if exposed |
| EMC | Electrical compatibility | For anything with electronics |

**Random vibration is where fluid system hardware fails**, and it fails at the fittings and at the supports rather than in the middle of a line. See the supports section of [PipeRoutingAndSizing.md](PipeRoutingAndSizing.md).

**Test in the flight configuration.** A component qualified alone and installed with a different mounting stiffness has not been qualified in the way it will be used. Where practical, qualify at the assembly level.

**Leak test after every environmental exposure**, not only at the end. Knowing which exposure caused a failure is worth the extra tests.

---

## Life and cycle testing

| Item | Life driver | Test |
|---|---|---|
| **Valve** | Actuation cycles, seat wear | Cycle to 4x expected life, leak test throughout |
| **Regulator** | Cycles and total flow | Cycle and flow to 4x, verify setpoint drift |
| **Check valve** | Cycles, chatter exposure | Cycle to 4x, verify reverse leakage |
| **Catalyst bed** | Pulses, cumulative burn time | Fire to 4x, track ignition delay. See [CatalystBeds.md](CatalystBeds.md) |
| **Seal** | Compression set, permeation | Long-duration compression at temperature |
| **Bellows** | Fatigue cycles | Cycle to 4x, then burst |
| **Pressure vessel** | Pressure cycles, stress rupture (COPV) | Cycle to 4x, then burst; COPVs also need sustained-load testing |
| **Line and fittings** | Vibration, thermal cycles | Part of the environmental qualification |

**A factor of 4 on life is the usual requirement** for flight hardware. Some programs use 2 with fracture control, or higher for a critical single-string item.

**Test the failure mode you care about.** Cycling a valve open and closed at ambient with no differential tests the actuator, not the seat. Cycle at the operating differential, at temperature, with the service fluid or a representative one, and leak test throughout rather than only at the end.

**Wear-out failures are the point.** A life test that produces no failures at 4x life has demonstrated the margin; a life test that produces a failure at 3.5x has demonstrated much more, because now you know the failure mode.

---

## Qualification approaches

| Approach | What it is | When it applies |
|---|---|---|
| **Dedicated qualification article** | Build extra units, test them to destruction | The default. Cleanest evidence, highest cost |
| **Protoqualification** | Test flight articles to levels between acceptance and qualification | Cost-constrained programs. Consumes some flight life |
| **Qualification by similarity** | Argue from a previously qualified item | Requires demonstrable similarity in design, materials, process AND environment. Frequently claimed and rarely valid |
| **Qualification by analysis** | Demonstrate by calculation | Only where the analysis method is validated and the failure mode is well understood |
| **Heritage** | Previously flown in the same application | Verify the application really is the same; a component flown in a different environment is not qualified |

**Qualification by similarity is the one that causes trouble.** The claim requires that the design, the materials, the manufacturing process **and the environment** are all similar enough that the previous evidence applies. A valve qualified for a 5 g random vibration environment is not qualified for a 12 g one, and a seal qualified in nitrogen is not qualified in hydrazine. Write the similarity argument down and have someone else review it.

---

## Acceptance testing

Every flight article gets:

| Test | Purpose |
|---|---|
| **Dimensional inspection** | It is what the drawing says |
| **Proof pressure** | Strength, no permanent set |
| **Leak test** | External and internal (seat) leakage |
| **Functional test** | It works: stroke, timing, setpoint, flow |
| **Flow calibration** | For orifices, injectors, venturis: the actual flow number |
| **Cleanliness verification** | To the specified level |
| **Workmanship inspection** | Welds, finishes, markings |
| Acceptance vibration | Workmanship screen, for programs that use it |

**Acceptance test levels are lower than qualification levels** and must be non-destructive. An acceptance test that consumes life is a design problem.

**The flow calibration deserves emphasis.** For any component whose flow rate matters (injectors, orifices, venturis, valves), the acceptance test should record the measured flow number, not just a pass/fail. That record is the baseline for detecting erosion, plugging or edge rounding across the component's life. See [Orifices.md](Orifices.md).

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| MEOP includes transients | Always | Not the nominal operating pressure |
| Proof factor | 1.5x MEOP | Universal for flight |
| Burst factor, hazardous fluid lines | 4.0x MEOP | Thin, exposed, personnel hazard |
| Burst factor, pressure vessels | 2.0x MEOP with fracture control | |
| Proof with liquid | Wherever possible | A pneumatic proof stores dangerous energy |
| Leak test after proof | Always | Proof can open a marginal joint |
| Leak test at temperature | For anything cryogenic | Ambient testing does not qualify a cold joint |
| Life factor | 4x expected | Standard for flight hardware |
| Qualify in the flight configuration | Wherever practical | Mounting stiffness changes the environment |
| Leak test after each environmental exposure | Always | Knowing which one caused it is worth the test |
| Record flow numbers at acceptance | For every flow-critical part | The baseline for life trending |
| Write the similarity argument down | Always | And have someone else review it |

---

## Failure modes

**MEOP underestimated.** A transient that was not in the MEOP definition exceeds the design pressure in service. Found at proof test if you are lucky and in service if you are not.

**Pneumatic proof test accident.** Stored energy released as a projectile. Entirely avoidable by using a liquid.

**Leak test at the wrong condition.** A joint passing at ambient and leaking cold, or passing in one direction and leaking in the other.

**Qualification by similarity that was not similar.** The component was qualified in a different environment, with a different fluid, or with a different mounting.

**Acceptance test that consumes life.** A cycle test as part of acceptance that uses up a meaningful fraction of the qualified life.

**Life test that did not test the failure mode.** Cycling with no differential, at ambient, with an inert fluid.

**Environmental test at the component level only.** Passed alone, failed in the assembly, because the mounting stiffness was different.

**No baseline data.** A component that fails in service with no acceptance record to compare against. The investigation has nowhere to start.

**Fracture control skipped.** A pressure vessel with a burst factor that assumed fracture control that was never actually performed.

---

## Standards

| Standard | Scope |
|---|---|
| **AIAA S-080** | Space systems metallic pressure vessels, pressurized structures and pressure components |
| **AIAA S-081** | Space systems composite overwrapped pressure vessels |
| **NASA-STD-5019** | Fracture control requirements for spaceflight hardware |
| NASA-STD-5001 | Structural design and test factors of safety for spaceflight hardware |
| **NASA-STD-7002** | Payload test requirements |
| NASA-STD-7001 | Payload vibroacoustic test criteria |
| **MIL-STD-1540** | Test requirements for launch, upper stage and space vehicles |
| **MIL-STD-810** | Environmental engineering considerations and laboratory tests |
| ECSS-E-ST-10-03 | Space engineering: testing |
| **ASME B31.3** | Process piping, including examination and testing (ground systems) |
| ASME BPVC Section VIII | Pressure vessels |
| NASA-STD-8719.17 | Ground-based pressure vessels and pressurized systems |
| ISO 14623 | Space systems, pressure vessels and pressurized structures, design and operation |
| ASTM E432 | Selection of a leak testing method |

---

## Tool interface

The library computes the design side of the qualification argument:

```python
from Line import Line
from Weld import Weld
from Regulator import Regulator
from WaterHammer import WaterHammer
from utils import b31_3WallThickness, materialProperties

# MEOP contributors: the surge that has to be included
surge = WaterHammer()
surge.setInputs({'fluid': 'N2H4', 'pressure': 2.3e6, 'temperature': 293.15,
                 'velocity': 2.34, 'innerDiameter': 0.004928, 'wallThickness': 0.000711,
                 'length': 2.5, 'closureTime': 0.020})
surge.calculateSurge()
meop = surge.peakPressure          # not the steady operating pressure

# And the regulator band, which is the other MEOP contributor
regulator = Regulator()
regulator.setInputs({'setPressure': 2.4e6, 'inletPressure': 30e6,
                     'finalInletPressure': 3.0e6, 'massFlow': 0.001})
band = regulator.sizeRegulator()['outletPressureBand']    # use the maximum

# Wall thickness and margin at that MEOP
line = Line()
line.setInputs({'fluid': 'N2H4', 'massFlow': 0.045, 'length': 2.5,
                'inletPressure': 2.4e6, 'inletTemperature': 293.15,
                'innerDiameter': 0.004928, 'designPressure': meop,
                'material': '316L'})
line.outerDiameter       = 0.00635
line.wallThicknessActual = 0.000711
line.calculateWallThickness()
print(line.wallThickness['margin'])       # margin against B31.3
print(line.wallThickness['hoopStress'])   # actual stress at MEOP

# Weld derating at the same MEOP
joint = Weld()
joint.setInputs({'jointType': 'tube to fitting', 'material': '316L',
                 'outerDiameter': 0.00635, 'wallThickness': 0.000711,
                 'designPressure': meop, 'fluidHazard': 'toxic'})
joint.calculateDerating()
joint.calculateAllowablePressure()
print(joint.pressureMargin)
joint.selectInspection()                  # the required NDE level
```

`Regulator.checkPressureStackup()` verifies the whole set point ladder from regulator band through relief and burst disc to proof pressure, which is the qualification-level consistency check for a pressure control chain.

---

## References

1. AIAA S-080A-2018, *Space Systems -- Metallic Pressure Vessels, Pressurized Structures, and Pressure Components*.
2. AIAA S-081B-2018, *Space Systems -- Composite Overwrapped Pressure Vessels*.
3. NASA-STD-5019A, *Fracture Control Requirements for Spaceflight Hardware*.
4. NASA-STD-7002B, *Payload Test Requirements*.
5. MIL-STD-1540E, *Test Requirements for Launch, Upper-Stage, and Space Vehicles*.
6. MIL-STD-810H, *Environmental Engineering Considerations and Laboratory Tests*.
7. ASME B31.3, *Process Piping*.
8. NASA-STD-8719.17B, *NASA Requirements for Ground-Based Pressure Vessels and Pressurized Systems*.
