[Home](../README.md) > Cryogenic and Cold Shock Testing

# Cryogenic and Cold Shock Testing

## Contents

- [Overview](#overview)
- [Why ambient testing does not qualify a cryogenic joint](#why-ambient-testing-does-not-qualify-a-cryogenic-joint)
- [Cold functional testing](#cold-functional-testing)
- [Cold leak testing](#cold-leak-testing)
- [Thermal shock](#thermal-shock)
- [Chilldown characterization](#chilldown-characterization)
- [Test media and safety](#test-media-and-safety)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Cryogenic testing exists because the failure mechanisms that matter at cryogenic temperature do not exist at ambient, and no amount of ambient testing exercises them.

The physics is in [fluidSystemsLibrary/docs/CryogenicSystems.md](../../fluidSystemsLibrary/docs/CryogenicSystems.md). This document is about running the tests.

---

## Why ambient testing does not qualify a cryogenic joint

Three mechanisms, none of which are present at room temperature.

**Differential contraction.** Materials shrink by different amounts. PTFE contracts 1.9 percent to 77 K against 0.30 percent for the stainless around it. On a 20 mm gland that is a 0.32 mm differential, several times the squeeze on a small cross section. The seal that had adequate compression at ambient has none cold.

**Glass transition.** An elastomer below its Tg is not a soft seal; it is a hard plastic ring with no compliance. Viton has a Tg at 255 K, so a Viton-sealed joint that passes every ambient leak check leaks on a cold morning, let alone at 90 K.

**Material transition.** Ferritic and martensitic steels have a ductile-to-brittle transition. A component that is ductile at ambient can be brittle at 77 K, and the failure is sudden and without deformation.

**A cold leak test is therefore not an optional refinement.** It is the only test that exercises the mechanism.

---

## Cold functional testing

**What changes cold:**

| Effect | Consequence |
|---|---|
| Differential contraction | Clearances change; seat interference changes |
| Increased seat interference | **Breakaway torque rises by 2 to 3x** after a cold soak |
| Lubricant viscosity | Actuation force rises, response time grows |
| Material strength | Austenitic stainless gains strength; some materials embrittle |
| Fluid properties | Density, viscosity and vapor pressure all change substantially |

**Test the actuator at its cold breakaway, not its ambient one.** A cryogenic ball valve seat shrinks onto the ball during a cold soak, and an actuator sized on catalog running torque will fail to open it. This is a recurring and entirely predictable failure.

**Soak before testing.** The article has to reach thermal equilibrium, verified by instrumentation on the article rather than on the chamber. A cold shell over a warm core has not been cold-soaked.

---

## Cold leak testing

**The hard part is instrumenting a leak measurement at temperature**, because the detection equipment does not go cold with the article.

| Approach | How it works | Notes |
|---|---|---|
| **Cold article, warm detector** | Article in a cryostat or LN2 bath, sample line to the detector at ambient | Standard. The sample line adds a time constant |
| Bagging at temperature | Enclose the cold article, accumulate, sample | Condensation inside the bag is the complication |
| Immersion bubble | Immerse in LN2, watch for bubbles | Crude, but unambiguous, and boiling makes it hard to read |
| Mass spectrometer with cold probe | Probe at the joint, article cold | Best sensitivity; probe icing is the problem |

**Ice and condensation are the practical obstacles.** A cold surface in air accumulates ice which blocks the leak path, invalidating the measurement in the reassuring direction. Test in a dry purged enclosure or under vacuum.

**Test cold AND after return to ambient.** A joint that leaks cold and seals warm has a contraction problem; one that leaks after the cycle has been damaged. They are different findings with different fixes.

---

## Thermal shock

**Thermal shock is the rate, not the range.** A component cooled slowly to 77 K sees a different stress state from one plunged into LN2, because the gradient through the wall is what generates the stress.

**When to test it:** whenever the service includes a rapid transition. A propellant valve that opens onto a warm downstream line sees the cryogen arrive in milliseconds, and that is a shock the slow cooldown of a thermal cycle test never applies.

**Method:** plunge or rapid flow initiation, with the article instrumented for wall temperature so the actual gradient is known rather than assumed. Follow with a leak and functional test.

---

## Chilldown characterization

Chilldown is a test in its own right on any system with a cryogenic transfer line, and the reasons are in [fluidSystemsLibrary/docs/CryogenicSystems.md](../../fluidSystemsLibrary/docs/CryogenicSystems.md): the two-phase slugs, the repeated water hammer events, and the fact that no steady-state model predicts any of it.

**What to measure:**

| Measurement | Why |
|---|---|
| **Wall temperature along the line** | Chilldown is complete when the wall is cold, which is later than the outlet suggests |
| High-rate pressure | Each slug arrival is a water hammer event, at 10 kHz or better |
| Flow rate | Highly unsteady; a conventional meter will not track it |
| Chilldown mass consumed | It is a real propellant line item |
| Time to steady state | The operational number |

**Instrument for the transient.** A 10 Hz data system sees a smooth cooldown curve and none of the slug impacts that are actually damaging the hardware.

---

## Test media and safety

| Medium | Temperature | Notes |
|---|---|---|
| **LN2** | 77 K | The workhorse. Cheap, inert, available |
| LAr | 87 K | Where nitrogen is chemically unsuitable |
| LOX | 90 K | **Only when oxygen compatibility is being tested.** Everything becomes a fire hazard |
| LH2 | 20 K | Extremely hazardous; specialized facilities only |
| GHe, cold | Any | Cold gas for a controlled ramp rate |

**Test with LN2 wherever the point is temperature rather than fluid compatibility.** Using LOX because the service fluid is LOX turns a routine test into a hazardous operation, and it is only justified when oxygen compatibility is what is being demonstrated.

**Safety, briefly:** oxygen monitors in any enclosed space, because nitrogen asphyxiation gives no warning. Liquid air condensation on any surface below 90 K, which is oxygen-enriched and drips. Relief paths on every isolatable volume, because trapped cryogen expands several hundred to one.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Cold leak test is mandatory for cryogenic hardware | Ambient does not exercise the mechanism |
| Soak to equilibrium, verified on the article | Not on the chamber |
| Cold breakaway torque | 2 to 3x ambient |
| Test cold AND after return to ambient | Different findings |
| Dry purged enclosure or vacuum | Ice blocks the leak path |
| Thermal shock is the rate | Instrument wall gradient |
| Chilldown sampling | >= 10 kHz for the slug impacts |
| Use LN2 unless compatibility is the point | LOX turns it into a hazardous operation |
| Relief path on every isolatable volume | Trapped cryogen expands hundreds to one |

---

## Failure modes

**Ambient-only qualification of a cryogenic joint.** It passes and it is not qualified.

**Ice blocking the leak path.** The measurement reads clean because the leak is frozen shut.

**Actuator sized on ambient breakaway.** The valve will not open after a cold soak.

**Insufficient soak.** A cold shell over a warm core; the test temperature was never reached.

**Chilldown instrumented at 10 Hz.** The slug impacts are invisible and the damage is unexplained.

**LOX used where LN2 would do.** A routine test conducted as a hazardous operation for no benefit.

**Trapped cryogen in an isolated volume.** The line bursts.

---

## Standards

| Standard | Scope |
|---|---|
| **CGA P-12** | Safe handling of cryogenic liquids |
| ISO 21010 | Cryogenic vessels, gas/materials compatibility |
| ISO 21014 | Cryogenic vessels, insulation performance |
| ASTM C1774 | Thermal performance testing of cryogenic insulation systems |
| NASA-STD-8719.17 | Ground-based pressure vessels and pressurized systems |
| **NASA-STD-6001** | Flammability, offgassing and compatibility, including LOX impact |
| ASTM G86 | Ignition sensitivity to mechanical impact in oxygen |
| NFPA 55 | Compressed gases and cryogenic fluids code |

---

## Tool interface

```python
from TestCampaign import TestCampaign
from LeakTest import LeakTest

# A cryogenic article picks up the cold functional and cold leak tests automatically
campaign = TestCampaign()
campaign.setInputs({'articleName': 'LOX isolation valve', 'articleType': 'valve',
                    'fluidHazard': 'oxidizer', 'isCryogenic': True})
matrix = campaign.buildMatrix()
# 'cryogenic functional' and 'leak test, at temperature' now appear in the sequence

# The cold leak test itself
leak = LeakTest()
leak.setInputs({'allowableLeakRate': 1.0e-5, 'testPressure': 4.0e5,
                'temperature': 90.0, 'species': 'He'})
leak.selectMethod()
```

Design-side support: [`Seal.checkCompatibility`](../../fluidSystemsLibrary/Seal.py) raises on a glass transition violation, and [`Insulation`](../../fluidSystemsLibrary/Insulation.py) flags liquid air condensation below 90 K.

---

## References

1. Barron, R. F., *Cryogenic Systems*, 2nd ed., Oxford University Press, 1985.
2. CGA P-12, *Safe Handling of Cryogenic Liquids*.
3. Flynn, T. M., *Cryogenic Engineering*, 2nd ed., Marcel Dekker, 2004.
4. NASA-STD-6001B, *Flammability, Offgassing, and Compatibility Requirements and Test Procedures*.
