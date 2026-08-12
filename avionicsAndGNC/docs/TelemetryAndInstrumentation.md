[Home](../README.md) > Telemetry and Instrumentation

# Telemetry and Instrumentation

## Contents

- [Overview](#overview)
- [A few channels spend most of the bandwidth](#a-few-channels-spend-most-of-the-bandwidth)
- [Channel count against sample rate](#channel-count-against-sample-rate)
- [Aliasing is worse than not measuring](#aliasing-is-worse-than-not-measuring)
- [Recorder against downlink](#recorder-against-downlink)
- [What to measure](#what-to-measure)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A telemetry budget is a bandwidth allocation problem with an unusual cost function: **the cost of getting it wrong is paid during the investigation afterwards, not during the flight.**

A channel that was not recorded is not a degraded measurement. It is an absence, and the absence is discovered at the worst possible moment by somebody who cannot go back.

---

## A few channels spend most of the bandwidth

The reference measurement list, 93 channels:

| Group | Channels | Rate | Share of bandwidth |
|---|---|---|---|
| Structural accelerometers | 12 | 2 kHz | **75 %** |
| Pressure transducers | 24 | 200 Hz | 13 % |
| Navigation state | 1 | 100 Hz | 10 % |
| Valve positions | 16 | 50 Hz | 1 % |
| Temperatures | 40 | 5 Hz | 0 % |

**Twelve channels out of ninety-three are three quarters of the budget**, and forty temperature channels are a rounding error.

That has a direct consequence for how a list gets cut. Deleting temperature channels achieves nothing. **The only cut that matters is in the group an investigation most needs**, which is why the cut has to be a deliberate decision rather than a negotiation between people defending their own measurements.

---

## Channel count against sample rate

They compete for the same bits, exactly.

| Sample rate factor | Channels affordable |
|---|---|
| 0.5x | 2x baseline |
| 1.0x | baseline |
| 2.0x | 0.5x baseline |
| 4.0x | 0.25x baseline |

The instinct is to sample everything fast, and the result is a list that does not fit. Showing the trade explicitly turns the cut from an argument into a decision, which is most of what this calculation is for.

---

## Aliasing is worse than not measuring

A channel sampled below Nyquist for the frequency it is meant to represent does not miss its signal. **It aliases it into a lower frequency that is not there**, and an investigation reading that data will chase something that never happened.

Two thresholds, as elsewhere in this repository:

**Nyquist, twice the signal frequency**, says whether the frequency is representable at all.

**Ten times**, says whether the amplitude and shape can be recovered, and a transient is a shape.

A channel between the two **detects without resolving**: it can say that something happened and not how large it was, which is enough for a health check and not enough for an investigation.

The fix for a channel that must be sampled slowly is an anti-alias filter ahead of the sampler, and that is a hardware decision made at build time. See [electricalPower EMIAndEMC](../../electricalPower/docs/EMIAndEMC.md), which makes the same point about a different signal.

---

## Recorder against downlink

They fail in opposite ways, and that is the argument for having both.

**A recorder is not bandwidth-limited and it has to survive.** It can hold everything at full rate, and if the vehicle is lost the data is lost with it unless the recorder is recoverable.

**A downlink is bandwidth-limited and it arrives regardless.** Whatever fits is on the ground before anything happens to the vehicle.

So the usual arrangement is **record everything, downlink a subset**, and the subset is chosen for real-time decisions rather than for investigation.

The reference recorder holds 108 minutes at full rate against a 9 minute flight, which is comfortable. **A recorder that runs out before the end is the worst case**, because the end is the part an investigation wants most, and the library refuses that configuration.

---

## What to measure

Qualitative, and it is the part that transfers least well as a rule.

**Measure the thing, not its consequence**, where you can. A valve position is better than an inferred flow.

**Measure across every interface**, because interfaces are where the argument happens afterwards.

**Measure what you would need to exonerate a subsystem**, not just what you need to run it. Those are different lists and the second is longer.

**Keep the health-check subset small and fast**, and the investigation set large and recorded.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Channels | 93 |
| Payload rate | 511.2 kbit/s |
| With 20 % framing | 613.4 kbit/s |
| With 25 % margin | 766.8 kbit/s |
| Link capacity | 1000 kbit/s |
| Utilisation | 77 % |
| Recorder duration | 108.7 min |
| Flight duration | 9.0 min |

---

## Design rules of thumb

- **Cut from the high-rate group or do not cut.** Everything else is a rounding error.
- **State a signal frequency with every channel.** Without it the rate cannot be checked.
- **Anti-alias in hardware** on anything sampled below ten times its content.
- **Record everything, downlink a subset.**
- **Size the recorder for longer than the flight.** The end is the part that matters.

---

## Failure modes

**A list cut by deleting temperature channels.** Achieves nothing.

**A channel below Nyquist.** Aliases, and an investigation chases a signal that never existed.

**A recorder that runs out before the end.** Loses the part that matters.

**A downlink-only architecture.** Whatever did not fit is gone.

**A measurement list built for operations.** Exoneration needs a longer list.

---

## Tool interface

```python
from TelemetryBudget import TelemetryBudget

telemetry = TelemetryBudget()
telemetry.setInputs({'measurements': [{'name': 'accelerometers', 'count': 12,
                                       'sampleRate': 2000.0, 'wordLength': 16,
                                       'signalFrequency': 150.0}],
                     'linkCapacity':     1.0e6,
                     'recorderCapacity': 4.0e9,
                     'flightTime':       540.0})

link        = telemetry.checkLink()
rates       = telemetry.checkSampleRates()
recorder    = telemetry.checkRecorder()
allocations = telemetry.compareAllocations()
```

`checkSampleRates()` raises on an aliasing channel, because aliased data is worse than absent data.

---

## References

- IRIG 106, *Telemetry Standards*, not read here
- [electricalPower EMIAndEMC](../../electricalPower/docs/EMIAndEMC.md), for anti-alias filtering
- [propulsionTesting Instrumentation](../../propulsion/propulsionTesting/docs/Instrumentation.md), which makes the same sample rate argument for a stand
