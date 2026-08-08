[Home](../README.md) > Sine and Transient Vibration

# Sine and Transient Vibration

## Contents

- [Overview](#overview)
- [The low frequency transients](#the-low-frequency-transients)
- [Sine equivalent testing](#sine-equivalent-testing)
- [Why sine testing is dangerous](#why-sine-testing-is-dangerous)
- [Notching](#notching)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Below about 100 Hz the environment is transient rather than random: discrete events that ring the vehicle at its own modes. This is the band where the coupled loads analysis lives and where the structure rather than the components is at risk.

---

## The low frequency transients

| Event | Duration | Character |
|---|---|---|
| **Liftoff release** | 1 to 3 s | Hold-downs release, the vehicle springs |
| **Engine ignition** | 0.5 to 2 s | Thrust builds in tens of milliseconds |
| **Engine shutdown** | 0.5 to 1 s | Thrust decay, and the vehicle unloads |
| **Staging** | 0.1 to 1 s | Separation and second stage ignition |
| **Gust and buffet** | seconds | Aerodynamic, at max-Q |
| POGO | sustained if it occurs | Closed-loop instability |

**These excite the vehicle's global modes**, which sit at a few hertz to a few tens of hertz, and the payload rides on the end of that. The resulting loads are what the coupled loads analysis produces.

**They are transient, not steady.** The peak response depends on how the forcing function's frequency content lines up with the structure's modes, which is why a coupled analysis is required and a load factor is a summary of its output rather than an input to it.

---

## Sine equivalent testing

**A swept sine test that produces the same peak response as the transient, one frequency at a time.**

| Property | Detail |
|---|---|
| **Sweep rate** | 2 to 4 octaves per minute, typically |
| **Level** | Derived to envelope the transient response |
| **Range** | 5 to 100 Hz, the low frequency band |
| Purpose | Verify the structure and its modes |

**It exists because a transient is hard to reproduce on a shaker** and a swept sine is easy. The equivalence is in the peak response, not in the waveform.

---

## Why sine testing is dangerous

**A swept sine puts far more energy into a resonance than a transient does, and it does it at every resonance in turn.**

| | Flight transient | Swept sine |
|---|---|---|
| **Cycles at resonance** | A handful | **Hundreds** |
| **Energy delivered** | Bounded by the event | Bounded by the sweep rate |
| **Simultaneous modes** | All excited together | One at a time |

**The cycle count is the problem.** A transient rings a mode a few times and decays. A sine sweep passing through that mode at 2 octaves per minute delivers hundreds of cycles at full amplitude, which is a fatigue exposure the flight event never produces.

**That is why sine testing without notching routinely overtests**, and why notching a sine test is not a concession but a necessary correction.

**It also excites one mode at a time**, where flight excites them together. A structure whose failure depends on two modes interacting will not show it in a sine test.

---

## Notching

**Reducing the input at frequencies where the test would exceed the flight response.**

| Basis | Character |
|---|---|
| **Response limiting** | Limit a measured response to the coupled loads prediction |
| **Force limiting** | Limit the interface force to the flight prediction |
| Manual notch | Named frequencies, requires justification |

**Notching a sine test is normal and expected.** The unnotched level is derived to envelope the transient at every frequency simultaneously, which no single flight condition produces, so running it unnotched tests a condition that cannot occur.

**The justification has to be quantitative.** A notch supported by a coupled loads analysis response prediction is defensible; a notch applied because the article was responding hard is not.

**Force limiting is the more robust basis** because it is measured at the interface rather than inferred from a model. See [RandomVibration.md](RandomVibration.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Below ~100 Hz the environment is transient | Not random |
| Sine equivalence is in peak response | Not in waveform |
| Sweep rate 2 to 4 oct/min | Faster is less damaging, and less controlled |
| A sine sweep delivers hundreds of cycles | A transient delivers a handful |
| Notching a sine test is necessary | Not a concession |
| Notches need a quantitative basis | Response or force limiting |
| Sine excites one mode at a time | Flight excites them together |

---

## Failure modes

**An unnotched sine test.** Tests a condition that cannot occur, at a cycle count flight never produces.

**A notch applied because the article responded hard.** No quantitative basis.

**Sine equivalence assumed to reproduce the transient.** It matches peak response only.

**Two-mode interaction expected to show in a sine test.** It excites them one at a time.

**Sweep rate not stated.** The fatigue exposure depends on it.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-5002** | Load analyses of spacecraft and payloads |
| **NASA-HDBK-7004** | Force limited vibration testing |
| MIL-STD-1540 | Test requirements |
| MIL-STD-810 Method 514 | Vibration, including sine |
| ECSS-E-ST-10-03 | Testing |

---

## Tool interface

```python
# Sine and transient environments come out of a coupled loads analysis rather than a
# closed form, so this domain covers them in documentation and supplies the quasi-static
# summary the CLA produces.
import sys
sys.path.insert(0, 'environmentsAndLoadsLibrary')

from LoadFactorSet import LoadFactorSet

factors = LoadFactorSet()
factors.setInputs({'mass': 500.0})
factors.addStandardEvents(['liftoff', 'staging'])

for name in factors.events:
    combined = factors.combineEvent(name)
    print(f'{name:10s} dynamic share {combined["dynamicShare"] * 100.0:5.1f} %')
```

---

## References

1. NASA-STD-5002A, *Load Analyses of Spacecraft and Payloads*.
2. Scharton, T. D., *Force Limited Vibration Testing Monograph*, NASA RP-1403, 1997.
3. Wijker, J. J., *Spacecraft Structures*, Springer, 2008.
