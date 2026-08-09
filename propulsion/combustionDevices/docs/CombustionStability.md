[Home](../README.md) > Combustion Stability

# Combustion Stability

## Contents

- [Overview](#overview)
- [A threshold, not a margin](#a-threshold-not-a-margin)
- [Three regimes](#three-regimes)
- [Chug](#chug)
- [Acoustic modes](#acoustic-modes)
- [Baffles](#baffles)
- [Acoustic cavities](#acoustic-cavities)
- [Rating](#rating)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Combustion instability is a coupling between the combustion process and an acoustic or hydraulic mode of the system containing it. When the coupling feeds energy into the mode faster than the mode loses it, the oscillation grows.

A high frequency instability can destroy an engine in **milliseconds**. It is the one failure mode in this domain where the hardware does not survive long enough to be shut down, and it is the reason engine development programmes spend what they do on it.

---

## A threshold, not a margin

The single most important thing to understand, and the reason this sub-domain's stability class deliberately returns no margin.

**A stable engine and an unstable one differ by a design detail rather than by a factor.** There is no continuous quantity that says how stable an engine is. An engine either damps a disturbance or amplifies it, and the difference between the two can be a baffle blade, an element spacing, or a chamber a few millimetres longer.

This has two consequences that shape everything else.

**The meaningful question is about disturbances, not steady operation.** An engine can run smoothly for a full duration and go unstable on the next start, because the question is whether a perturbation grows and no perturbation was applied.

**So the test is a deliberate perturbation.** You set off a bomb in the chamber and time how long the oscillation takes to die. That is the only stability statement that means anything, and it is a test result rather than a calculation.

**A class that returned a stability margin would be inventing one.** `CombustionStability` computes the frequencies a chamber will support, the one necessary condition that is easy to check, and what the suppression devices are tuned to. It reports its chug check as a necessary condition explicitly, and a test asserts that it says so.

---

## Three regimes

| Regime | Frequency | Couples with | Severity |
|---|---|---|---|
| Chug | Tens to low hundreds of Hz | Feed system and chamber volume | Rough running |
| Buzz | Hundreds of Hz | Longitudinal chamber acoustics | Damaging over time |
| Screech | Thousands of Hz | Transverse chamber acoustics | Destroys engines in milliseconds |

The severity ordering is not a coincidence. Higher frequency means shorter wavelength, which means the pressure oscillation is concentrated rather than spread, and it means the heat transfer to the wall is enhanced by the scrubbing action of a wave sweeping around the chamber.

---

## Chug

Low frequency, and the one instability with a criterion simple enough to check by hand.

The feed system and the chamber form an oscillator: chamber pressure rises, which reduces the pressure differential across the injector, which reduces the flow, which drops the chamber pressure, which increases the flow again. **Injector stiffness is what breaks the loop**, by making the chamber pressure oscillation small compared to the injector drop.

Below roughly **5 per cent** stiffness the coupling is strong enough to sustain it. The recommended design band is 15 to 25 per cent.

**This is a necessary condition and not a sufficient one.** Chug involves the feed line inertance and the chamber volume as well as the injector, so clearing the criterion does not prove stability. Failing it does prove a problem, which is what makes it worth checking.

The throttling coupling matters here: stiffness falls linearly with throttle setting, so an engine designed at 20 per cent reaches the floor at 25 per cent throttle. See [InjectorDesign](InjectorDesign.md).

---

## Acoustic modes

A cylindrical chamber supports transverse modes at frequencies set by the roots of the derivative of the Bessel function:

```
f = alpha a / (pi D)          a = sqrt(gamma R Tc)
```

and longitudinal modes at `f = n a / (2 L)`.

For the [worked example](../codeInterface.py) chamber, 143.2 mm diameter, LOX/RP-1 at 3670 K giving a speed of sound of 1274 m/s:

| Mode | `alpha` | Frequency [Hz] | Character |
|---|---|---|---|
| **1T** | 1.8412 | **5214** | First tangential. The one that destroys engines |
| 2T | 3.0542 | 8648 | Second tangential |
| 1R | 3.8317 | 10 850 | First radial |
| 3T | 4.2012 | 11 896 | Third tangential |
| 1T1R | 5.3314 | 15 096 | Combined |
| 1L | | 1401 | First longitudinal |

**The first tangential mode is the one that matters.** It is the lowest transverse mode, it couples readily with the injection and atomisation process, and its pressure wave sweeps around the chamber circumference scrubbing the wall as it goes. Engines lost to instability are usually lost to 1T.

**It scales as one over diameter**, so a large chamber has a low and dangerous 1T and a small chamber has a high one. That is one of the few respects in which a small engine is easier.

---

## Baffles

Radial blades projecting from the injector face. A baffle with `N` blades prevents a coherent wave travelling around the circumference for tangential orders up to `N/2`.

**Baffles do nothing whatever to radial modes.** A radial wave does not travel around the circumference, so there is nothing for a radial blade to interrupt. Six blades on the worked example chamber cover 1T, 2T and 3T and leave 1R and 1T1R untouched.

**A baffled engine that goes unstable in 1R is a well documented outcome**, and it is why baffles and acoustic cavities are fitted together rather than chosen between.

Blade depth is typically a quarter of the chamber radius: deep enough to interrupt the wave near the injector face where the energy is added, and no deeper, because the blades are **uncooled obstructions in the hottest part of the chamber** and they are a classic failure item. A baffle that burns off during a burn removes the suppression it was fitted for at the moment the engine is hottest.

---

## Acoustic cavities

Helmholtz or quarter-wave resonators in the injector face or the chamber wall near it, absorbing energy at the frequency they are tuned to.

A quarter wave cavity tuned to the 5214 Hz first tangential of the worked example chamber is **61.1 mm deep**.

Two advantages over baffles and one difficulty.

**They work on radial modes**, which baffles do not, which is why the two are complements.

**They are not obstructions in the gas path**, so they do not burn off.

**The tuning is temperature sensitive.** The speed of sound in the cavity depends on what is in it and how hot that is, so a cavity tuned at the design chamber temperature is mistuned at start-up and during a throttle excursion. Real installations use a **range of depths** rather than all identical, which covers a band at the cost of peak absorption at any one frequency.

---

## Rating

The only meaningful stability statement is a test result.

The engine is perturbed deliberately and the oscillation is timed. **Anything that does not decay within about 40 ms is not dynamically stable**, whatever it did in undisturbed operation.

| Method | Character |
|---|---|
| **Bomb** | Explosive charge in the chamber. The most severe and the standard |
| Pulse gun | External gas pulse through a port. Repeatable, less severe |
| Directed flow | A jet across the injector face. Least severe, easiest to instrument |

**Undisturbed stable operation demonstrates nothing**, which is the hardest thing to accept about this subject. A full duration run at nominal conditions is not evidence of stability, because no disturbance was applied and the question is entirely about what happens when one is.

---

## Design rules of thumb

- **Do not ask for a stability margin.** There is no such quantity.
- **Keep injector stiffness above 5 per cent at the deepest throttle setting**, and treat that as necessary rather than sufficient.
- **Compute 1T early.** It is the mode that destroys engines and it follows from the chamber diameter alone.
- **Fit baffles and cavities together.** Baffles miss radial modes entirely.
- **Keep baffle blades shallow.** They are uncooled and they are in the hottest part of the chamber.
- **Vary cavity depths.** A single tuning is mistuned everywhere except one condition.
- **Rate by bomb test.** Nothing else is evidence.

---

## Failure modes

**A stability margin quoted.** It does not exist, and quoting one implies a continuity that is not there.

**Undisturbed operation taken as evidence.** The engine has not been asked the question.

**Baffles fitted and radial modes ignored.** A documented way to lose an engine that had been made stable in every tangential mode.

**Baffle blades too deep.** They burn, and they burn at the moment they are most needed.

**A cavity tuned at one temperature.** Mistuned at start-up, which is when many instabilities appear.

**Chug criterion treated as sufficient.** It omits the feed line inertance and the chamber volume.

**Stiffness checked at full thrust only.** It falls linearly with throttle.

---

## Worked numbers

The [worked example](../codeInterface.py) chamber: 143.2 mm diameter, 454.7 mm long, LOX/RP-1, six baffle blades.

| Quantity | Value |
|---|---|
| Speed of sound | 1274 m/s |
| 1T | 5214 Hz |
| 2T | 8648 Hz |
| 1R | 10 850 Hz |
| 1L | 1401 Hz |
| Baffle suppression, 6 blades | Tangential to order 3 |
| Modes left unsuppressed | 1R, 1T1R |
| Quarter wave cavity for 1T | 61.1 mm |
| Chug floor | 5 % stiffness |
| Damp time requirement | 40 ms |

---

## Standards

| Standard | What it gives you |
|---|---|
| **NASA SP-194** | **Liquid Propellant Rocket Combustion Instability.** Harrje and Reardon. Still the reference |
| CPIA 655 | Combustion stability testing and rating, including the bomb test |
| NASA SP-8113 | Combustion stabilization devices, baffles and cavities |
| NASA SP-8089 | Injectors, which are the usual cause |

---

## Tool interface

```python
from CombustionStability import CombustionStability

stability = CombustionStability()
stability.setInputs({'combination':       'LOX/RP-1',
                     'chamberDiameter':   0.1432,
                     'chamberLength':     0.4547,
                     'injectorStiffness': 0.20,
                     'baffleBlades':      6})

modes = stability.calculateAcousticModes()
print(modes['firstTangential'])

baffles = stability.sizeBaffles()
print(baffles['suppressed'], baffles['unsuppressed'])

print(stability.sizeAcousticCavity('1T')['quarterWaveDepth'])
print(stability.checkChugCriterion()['necessaryOnly'])
```

There is deliberately no method that returns a stability verdict.

---

## References

- Harrje and Reardon, NASA SP-194, *Liquid Propellant Rocket Combustion Instability*
- NASA SP-8113, *Liquid rocket engine combustion stabilization devices*
- Yang and Anderson, *Liquid Rocket Engine Combustion Instability*
- Oefelein and Yang, *Comprehensive review of liquid-propellant combustion instabilities in F-1 engines*
- CPIA 655, *Combustion stability testing and rating*
