[Home](../../README.md) > Leaks

# Leaks

## Contents

- [Overview](#overview)
- [Units](#units)
- [Flow regimes](#flow-regimes)
- [Conductance and the equivalent hole](#conductance-and-the-equivalent-hole)
- [Scaling between gases](#scaling-between-gases)
- [Detection methods](#detection-methods)
- [Pressure decay testing](#pressure-decay-testing)
- [Setting an allowable leak rate](#setting-an-allowable-leak-rate)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Operations](#operations)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Leaks are the most misunderstood topic in fluid systems, for three reasons.

**The units.** Three unrelated families are in common use -- throughput (Pa-m^3/s, mbar-L/s), standard volumetric (scc/s, sccm) and mass (lbm/yr, g/yr) -- and converting between the first two and the third requires knowing the gas. A specification written in one family and verified in another is a common and expensive mistake.

**The gas.** Leak checks are run on helium and hardware is used on something else. The scaling between them is not a single factor: in molecular flow the rate scales as `1/sqrt(M)`, in viscous flow it scales as `1/mu`, and for helium versus nitrogen those two point in **opposite directions**.

**The physics.** A leak rate is a flow through a passage, and how that passage behaves depends on how its size compares to the mean free path of the gas. The same physical crack is viscous at 10 MPa upstream and molecular at 1 kPa, and the rate does not scale linearly between them. A leak measured at test pressure cannot simply be ratioed to operating pressure.

---

## Units

| Unit | Family | Definition | Conversion to Pa-m^3/s |
|---|---|---|---|
| Pa-m^3/s | Throughput | SI. The internal working unit here | 1 |
| mbar-L/s | Throughput | European vacuum industry standard | 0.1 |
| torr-L/s | Throughput | | 0.13332 |
| atm-cm^3/s | Throughput | Numerically equal to scc/s at 0 degC | 0.101325 |
| **scc/s** | Standard volumetric | Standard cm^3 per second, 0 degC and 1 atm | 0.101325 |
| sccm | Standard volumetric | Standard cm^3 per minute | 0.0016888 |
| slpm | Standard volumetric | Standard litres per minute | 1.68875 |
| kg/s, g/yr, lbm/yr | Mass | **Requires the molar mass** | gas dependent |

**Useful equalities to memorize:**

```
1 scc/s     = 1.01325 mbar-L/s = 0.101325 Pa-m^3/s
1 mbar-L/s  = 0.98692 scc/s
1e-4 scc/s of helium = 1.24e-3 lbm/yr
```

**A trap.** The "standard" in scc/s is 0 degC and 1 atm by the vacuum industry convention used here and by most leak-test standards. Some specifications define it at 20 degC or 70 degF instead, a 7 percent difference. If a legacy specification does not say, ask; the [`leakRateConvert`](../utils.py) function takes an explicit reference temperature so a spec written against a different basis can be reproduced exactly.

**A second trap.** SCFM (standard cubic feet per minute) uses 60 degF as its standard, not 0 degC. Mixing the SCFM standard state with the scc/s standard state is a 5 percent error that hides very well inside a regulator sizing calculation.

**Scale intuition.** A useful anchor: **1e-4 scc/s of helium is roughly one bubble every ten seconds** in a water immersion test, and it is about 1.2e-3 lbm per year. A 1e-11 scc/s leak, the mass spectrometer floor, would take about 3000 years to fill a one-litre bottle to 1 atm.

---

## Flow regimes

The controlling parameter is the Knudsen number, the ratio of the mean free path to the passage diameter:

```
Kn = lambda / d,        lambda = k_B * T / ( sqrt(2) * pi * d_molecule^2 * P )
```

| Kn | Regime | Physics | Rate scaling |
|---|---|---|---|
| < 0.01 | Viscous (continuum) | Molecule-molecule collisions dominate. Poiseuille flow | `d^4`, `1/mu`, `(P1^2 - P2^2)` |
| 0.01 to 1 | Transitional | Both mechanisms contribute | Between the two |
| > 1 | Molecular (Knudsen) | Molecule-wall collisions dominate. No viscosity | `d^3`, `1/sqrt(M)`, `(P1 - P2)` |
| any, with a high pressure ratio and a large hole | Choked | Sonic velocity at the exit | `d^2`, `P1/sqrt(T1)` |

**Evaluate the mean free path at the MEAN pressure through the passage**, not the upstream pressure. A leak from 1 MPa into vacuum has most of its length at low pressure, and using the upstream value puts it in the viscous regime when it is largely molecular.

For helium at 293 K, the mean free path is roughly:

| Pressure | Mean free path |
|---|---|
| 1 atm | 0.19 micron |
| 1 kPa | 19 micron |
| 1 Pa | 19 mm |
| 1e-3 Pa | 19 m |

which is why a leak into hard vacuum is essentially always molecular, and a leak between two pressurized volumes essentially always viscous.

---

## Conductance and the equivalent hole

**Viscous (Poiseuille) throughput** through a long capillary:

```
Q = pi * d^4 * (P1^2 - P2^2) / ( 256 * mu * L )
```

**Molecular (Knudsen) conductance** of a long tube:

```
C = (pi/12) * v_mean * d^3 / L,       v_mean = sqrt( 8*R*T / (pi*M) )
Q = C * (P1 - P2)
```

**Transitional flow** is handled by adding the two contributions. That is the standard engineering approximation and it is accurate to about 20 percent across the transition, which is far better than the uncertainty in the geometry of a real leak.

**The equivalent hole diameter** is what you get by inverting the above for a measured rate. It is a standardized comparison quantity, **not a physical measurement**. A real leak is a crack in a weld, a scratch across a sealing face, or an interconnected porosity network, and none of those are round capillaries.

What the equivalent diameter buys you is intuition and comparability:

| Helium leak rate (1 atm dP, 1 mm path) | Equivalent diameter | Comparable to |
|---|---|---|
| 1e-2 scc/s | ~7 micron | A human hair is 70 micron |
| 1e-4 scc/s | ~2 micron | A red blood cell |
| 1e-6 scc/s | ~0.7 micron | A bacterium |
| 1e-8 scc/s | ~0.15 micron | Visible light wavelength |
| 1e-11 scc/s | ~10 nm | A few hundred atoms across |

At the bottom of that table the leak is not a hole in any meaningful sense. It is transport through an imperfectly closed interface, and it is why the achievable leak rate of a joint is a property of the sealing mechanism rather than of the workmanship.

---

## Scaling between gases

The conversion that turns a helium acceptance test into a statement about the service fluid.

| Regime | Scaling | He to N2 ratio |
|---|---|---|
| Molecular | `sqrt(M_source / M_target)` | `sqrt(4/28) = 0.38` (nitrogen leaks 2.6x less) |
| Viscous | `mu_source / mu_target` | `1.96/1.79 = 1.10` (nitrogen leaks 10 % MORE) |
| Choked | `sqrt(gamma_t/M_t) / sqrt(gamma_s/M_s)` x the choked function | close to the molecular result |

**The two limits point in opposite directions.** Helium is more viscous than nitrogen at room temperature -- which surprises everyone -- so in viscous flow nitrogen is the faster leaker despite being seven times heavier.

**Practical consequences:**

- A helium test into vacuum (molecular) is **conservative** relative to nitrogen service: the real nitrogen leak will be 2.6 times smaller.
- A helium test at pressure into atmosphere (viscous) is **slightly optimistic** relative to nitrogen service.
- Neither result transfers to a liquid without a completely separate calculation. A liquid leak through the same path is governed by the liquid viscosity and by surface tension, and a passage small enough to be a nuisance for helium may not pass liquid at all.

**Hazardous fluid vapor.** For hydrazine, MMH or N2O4, the leak that matters is usually the vapor leak, driven by the vapor pressure rather than by the system pressure. A hydrazine system at 2.5 MPa has a vapor pressure of only 1.4 kPa, so the driving differential for the vapor is three orders of magnitude lower than the system pressure. This is why a hydrazine system can have a hydrazine leak that is undetectable by pressure decay and perfectly detectable by a sensitive vapor monitor.

---

## Detection methods

| Method | Floor [scc/s He] | What it is good for | What it cannot do |
|---|---|---|---|
| Mass spec, hard vacuum | 1e-11 | The reference method for flight hardware | Requires the part to hold vacuum and fit the pump |
| Mass spec, inside out | 1e-10 | Total leakage of a sealed unit | Gives a total, not a location |
| Accumulation / bagging | 1e-8 | Quantitative on an installed assembly | Slow; enclosure volume and dwell must be controlled |
| Sniffer probe | 1e-6 | **Locating** leaks on an assembled system | Highly operator dependent. Poor for quantifying |
| Pressure decay | 1e-4 | Total system integrity with no tracer gas | Temperature limited (see below) |
| Bubble immersion (ASTM E515) | 1e-4 | Cheap, visual, quantitative by bubble count | Wets the part; unusable if it must stay clean |
| Bubble solution | 1e-3 | Fast field check | Contamination source |
| Ultrasonic | 1e-2 | First pass on a large system before spending helium | Gross leaks only |

**Nine orders of magnitude** separate the ends of that table. The choice of method is therefore a hard constraint on what leak rate you are allowed to specify: **a requirement you cannot measure is not a requirement.**

**Specify with margin.** A leak requirement set at the exact sensitivity floor of a method makes every measurement a coin flip and turns every disposition into an argument about instrumentation rather than about hardware. Specify at least a factor of ten above the method floor.

**Helium mass spectrometry practicalities:**

- **Background helium** in the test cell rises through the day as helium is sprayed. It sets the practical floor far more often than the instrument does. Ventilate, and take a background reading before every measurement.
- **Response time and clean-up time.** A large leak saturates the spectrometer and takes minutes to clear. Work from the least likely leak location toward the most likely, not the reverse.
- **Spray probe control.** Helium is lighter than air and rises. Spray from the bottom up, at a controlled rate, and give the system time to respond between locations.
- **Calibrated leak standard.** Every test starts and ends with a calibrated leak to establish sensitivity. Without it the number is meaningless.

---

## Pressure decay testing

A pressure decay test isolates a known volume, pressurizes it and measures the pressure fall:

```
Q = V * dP / dt
```

so the minimum detectable leak is

```
Q_min = V * dP_resolution / t_test
```

That part is straightforward. **The part that kills pressure decay tests is temperature.** For a fixed volume of ideal gas,

```
dP / P = dT / T
```

A temperature drift of only 0.1 K at 293 K produces an apparent pressure change of `3.4e-4` of the absolute pressure. At 10 MPa that is 3.4 kPa, which is very often orders of magnitude larger than the leak signal being sought.

**Pressure decay tests are almost always temperature limited, not transducer limited.**

**Worked illustration.** A 10 litre volume at 2.5 MPa, a 100 Pa resolution transducer, a one hour test, and 0.1 K of temperature stability:

| Floor | Value |
|---|---|
| Transducer limited | 2.7e-3 scc/s |
| **Temperature limited** | **2.3e-2 scc/s** |
| Binding | Temperature drift, by a factor of 8.5 |

To detect 1e-5 scc/s under these conditions the test would have to run for about 2.7 years. It is not a marginal shortfall; pressure decay simply cannot reach that level without active temperature control.

**Making a pressure decay test work:**

1. **Thermal soak** before starting. Hours, not minutes, and measure the gas temperature rather than the ambient.
2. **Measure and compensate.** Record gas temperature and correct the pressure to a reference temperature. This can buy one to two orders of magnitude.
3. **Reference volume.** A sealed, identical, known-tight volume alongside the test volume, differentially measured. Common-mode temperature effects cancel. This is the standard method for sensitive decay testing.
4. **Minimize the volume.** The floor scales with volume, so isolate the smallest volume that contains the joint under test.
5. **Use a differential transducer** against a reference rather than an absolute transducer at full scale. Resolution improves by the turndown ratio.

**When pressure decay is the right method anyway:** system-level integrity checks where the requirement is coarse (1e-3 to 1e-2 scc/s), where no tracer gas is available, or where the system is too large to bag or evacuate. It is a system integrity test, not a joint qualification test.

---

## Setting an allowable leak rate

Picking a number from a table is the common approach and it is the wrong one. Derive it.

**From a hazard criterion.** For a toxic or flammable fluid leaking into an enclosed volume, with no ventilation, the concentration after a time `t` is

```
C = Q_leak * t / V_enclosure
```

so the allowable leak is

```
Q_allowable = C_limit * V_enclosure / t_exposure
```

With ventilation at volumetric rate `V_dot`, the steady-state concentration is `Q_leak / V_dot`. **Both cases must be evaluated**, because a design that relies on ventilation must also survive the ventilation failing.

Relevant concentration limits:

| Fluid | Limit | Basis |
|---|---|---|
| Hydrazine | 0.01 ppm (1e-8) | OSHA 8-hour TWA. Also a suspected carcinogen |
| MMH | 0.01 ppm (1e-8) | 8-hour TWA |
| N2O4 / NO2 | 3 ppm (3e-6) | 8-hour TWA |
| Ammonia | 25 ppm (2.5e-5) | 8-hour TWA |
| Hydrogen | 4 % (0.04) | Lower flammability limit; design to 25 % of LFL |
| Methane | 5 % (0.05) | Lower flammability limit |
| Oxygen enrichment | 23.5 % (0.235) | Above this, ordinary materials become fire hazards |
| Oxygen depletion | 19.5 % (0.195) | Below this, asphyxiation risk from inert gas displacement |

**From a mission criterion.** For a pressurant or propellant that must last a mission:

```
Q_allowable = (acceptable mass loss) / (mission duration)
```

A spacecraft that must retain its GHe pressurant for ten years with less than 2 percent loss, from a 30 litre bottle at 20 MPa, is allowed to lose about 0.1 kg over 3.16e8 seconds, which is 3.2e-10 kg/s, or about 1.8e-3 scc/s of helium. That is a much looser requirement than the 1e-6 scc/s that gets specified reflexively, and it is worth checking which criterion actually governs before imposing a leak requirement that drives the joint architecture.

**From a functional criterion.** A valve seat leak that is acceptable for isolation may be unacceptable for a thruster that must not dribble. Work back from the consequence.

**Typical specified values, for calibration:**

| Application | Allowable [scc/s He] |
|---|---|
| Ultra high vacuum | 1e-10 |
| Spacecraft propulsion, per joint | 1e-7 |
| Spacecraft propulsion, long duration total | 1e-6 |
| Hazardous fluid, external | 1e-6 |
| Launch vehicle feed system | 1e-4 |
| Valve seat, ANSI Class VI equivalent | 1e-4 |
| Ground support equipment | 1e-3 |

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Leak rates add | Total = sum over joints | Twenty 1e-6 joints is a 2e-5 system |
| Specify above the method floor | 10x minimum | Otherwise every measurement is a coin flip |
| Helium test into vacuum vs N2 service | Conservative by 2.6x | Molecular scaling |
| Pressure decay temperature sensitivity | `dP/P = dT/T` | 0.1 K at 10 MPa is 3.4 kPa |
| Mean free path evaluation | At the mean pressure | Not the upstream pressure |
| Equivalent hole at 1e-6 scc/s | About 0.7 micron | Intuition anchor |
| Bubble test floor | 1e-4 scc/s | Set by surface tension |
| Vapor leak from a hazardous liquid | Driven by vapor pressure, not system pressure | Hydrazine at 2.5 MPa has 1.4 kPa vapor pressure |
| Design to 25 % of LFL for flammables | 1 % H2 in air | Not to the LFL itself |

---

## Failure modes

**Specification and verification in different units.** A requirement in mbar-L/s verified in scc/s without conversion is a 1.3 percent error, which is harmless. A requirement in scc/s verified in lbm/yr on the wrong gas is an order of magnitude, which is not.

**Leak rate scaled linearly with pressure.** A joint that leaks 1e-6 scc/s at 1 MPa does not leak 1e-5 scc/s at 10 MPa. In viscous flow the throughput scales with `(P1^2 - P2^2)`, not `P1`, and the regime may change as well.

**Background helium.** A test cell that has been used all day is saturated with helium, and the instrument reads background rather than leak. Every failed leak check should start with a background measurement before anyone touches the hardware.

**Permeation mistaken for a leak.** An elastomer-sealed joint has an irreducible permeation rate that no amount of assembly work reduces. If the measured rate matches the calculated permeation, the joint is not leaking. See [Seals.md](Seals.md).

**Virtual leaks.** A trapped volume inside the system (a blind tapped hole, an unvented annulus, a crevice at a socket weld) slowly outgasses into the evacuated system and looks exactly like a real leak. It cannot be found by external helium spray because there is nothing outside to find. Design them out: vent every blind hole, avoid crevices.

**Leak found, leak fixed, leak reappears.** Almost always a second leak that was masked by the first, or a joint that was disturbed while fixing the first. Re-check the whole system after any repair.

**Cold leak.** A joint that is tight at ambient and leaks cold, because the seal passed its glass transition or because differential contraction opened the joint. Leak testing at ambient does not qualify a cryogenic joint.

---

## Operations

**Leak check after every make-up.** A joint that was tight last time is not evidence about this time.

**Test in the direction the system will see.** A seal that is pressure energized in one direction may not seal at all in the other.

**Test at the temperature that matters.** For cryogenic hardware, that means a cold leak check, which is expensive and inconvenient and is the only way to know.

**Bracket every test with a calibrated leak.** Sensitivity before and after. If they disagree, the data between them is suspect.

**Record everything:** method, instrument, calibration date, background level, spray or sniff technique, dwell times, temperature. Leak data without those is not repeatable and therefore not usable.

**Isolate to locate.** On a system that fails a total leak check, subdivide with isolation valves and re-test each section rather than sniffing every joint. It is faster and much more reliable.

---

## Worked example

A joint on a hydrazine feed system, helium tested at 2.5 MPa upstream into atmosphere, measured leak 1e-5 scc/s, assumed 1 mm sealing land length.

**Regime and geometry:**

| Quantity | Value |
|---|---|
| Mean free path at the mean pressure | 0.0104 micron |
| Equivalent hole diameter | 0.669 micron |
| Knudsen number | 0.0155 |
| Regime | Transitional |
| Conductance | 4.22e-13 m^3/s |

**The same leak in every unit:**

| Unit | Value |
|---|---|
| scc/s | 1.000e-5 |
| sccm | 6.000e-4 |
| Pa-m^3/s | 1.013e-6 |
| mbar-L/s | 1.013e-5 |
| torr-L/s | 7.600e-6 |
| kg/s | 1.786e-12 |
| g/yr | 5.635e-2 |
| lbm/yr | 1.242e-4 |

**Detection:** the least sensitive adequate method with 10x margin is the sniffer probe (floor 1e-6 scc/s). Adequate for locating, but the operator dependence means the quantitative number should come from an accumulation or mass spectrometer test.

**Pressure decay feasibility** for a 10 litre volume, 100 Pa transducer, one hour, 0.1 K stability: the temperature-limited floor is 2.3e-2 scc/s, more than three orders of magnitude above the target. **Pressure decay cannot verify this joint.** The expected pressure drop from the actual leak over the hour is 0.36 Pa, well below the noise from any realistic temperature drift.

**Hazard-derived allowable:** hydrazine at a 0.01 ppm limit, in a 30 m^3 unventilated bay over an 8 hour shift, gives an allowable of 1.04e-5 scc/s. The measured 1e-5 scc/s is right at that limit, which means this joint is not acceptable without either ventilation credit or a tighter joint.

Reproduce with:

```python
from LeakPath import LeakPath

joint = LeakPath()
joint.setInputs({'species': 'He', 'upstreamPressure': 2.5e6,
                 'downstreamPressure': 101325.0, 'temperature': 293.15,
                 'leakRate': 1e-5, 'leakRateUnit': 'sccs', 'length': 1e-3})

joint.calculateEquivalentDiameter()
print(joint.generateReport())
print(joint.scaleToSpecies('Nitrogen'))
print(joint.calculatePressureDecayTest(testVolume = 0.01,
                                       transducerResolution = 100.0,
                                       testDuration = 3600.0))
print(joint.calculateAllowableFromHazard(enclosureVolume = 30.0,
                                         concentrationLimit = 1e-8,
                                         exposureTime = 28800.0))
```

---

## Standards

| Standard | Scope |
|---|---|
| ASTM E432 | Selection of a leak testing method |
| ASTM E479 | Preparation of a leak testing specification |
| ASTM E493 | Leaks using the mass spectrometer leak detector in the inside-out testing mode |
| ASTM E498 | Leaks using the mass spectrometer leak detector in the tracer probe mode |
| ASTM E499 | Leaks using the mass spectrometer leak detector in the detector probe mode |
| ASTM E515 | Leaks using bubble emission techniques |
| ASTM E1003 | Hydrostatic leak testing |
| ASME BPVC Section V Article 10 | Leak testing |
| MIL-STD-1330 | Cleaning and testing of shipboard oxygen systems (widely referenced for leak practice) |
| ANSI/FCI 70-2 | Control valve seat leakage classification |
| ISO 20485 | Non-destructive testing, leak testing, tracer gas method |
| NASA-STD-8719.17 | Requirements for ground-based pressure vessels and pressurized systems |

---

## Tool interface

The [`LeakPath`](../LeakPath.py) class handles units, regimes, equivalent geometry, gas scaling, method selection and test design.

```python
from LeakPath import LeakPath

leak = LeakPath()
leak.setInputs({'species': 'He', 'upstreamPressure': 2.5e6,
                'downstreamPressure': 101325.0, 'temperature': 293.15,
                'leakRate': 1e-5, 'leakRateUnit': 'sccs', 'length': 1e-3})

leak.calculateEquivalentDiameter()   # inverse: rate to geometry
leak.convertUnits()                  # the rate in every unit
leak.scaleToSpecies('Nitrogen')      # helium test to service fluid
leak.selectDetectionMethod()         # least sensitive adequate method
leak.calculatePressureDecayTest(0.01, 100.0, 3600.0)
leak.calculateAllowableFromHazard(30.0, 1e-8, exposureTime = 28800.0)

# Forward: geometry to rate
leak.diameter = 1e-6
leak.calculateLeakRate()
```

Also useful directly: [`utils.leakRateConvert`](../utils.py), which does the unit matrix without constructing a `LeakPath`. Lookup tables: `LeakPath.DETECTION_METHODS`, `LeakPath.TYPICAL_ALLOWABLE_LEAK_RATES`, `LeakPath.MOLECULAR_DIAMETERS`.

---

## References

1. Jousten, K. (ed.), *Handbook of Vacuum Technology*, 2nd ed., Wiley-VCH, 2016.
2. O'Hanlon, J. F., *A User's Guide to Vacuum Technology*, 3rd ed., Wiley, 2003.
3. ASTM E432-91, *Standard Guide for Selection of a Leak Testing Method*.
4. ASME BPVC Section V, Article 10, *Leak Testing*.
5. Marr, J. W., *Leakage Testing Handbook*, NASA CR-952, 1968.
6. Nondestructive Testing Handbook, Volume 1: *Leak Testing*, 4th ed., ASNT, 2017.
7. NASA-STD-8719.17B, *NASA Requirements for Ground-Based Pressure Vessels and Pressurized Systems*.
8. Roth, A., *Vacuum Sealing Techniques*, AIP Press, 1994.
