[Home](../README.md) > Campaign Structure

# Campaign Structure

## Contents

- [Overview](#overview)
- [The five levels](#the-five-levels)
- [What each level is actually for](#what-each-level-is-actually-for)
- [Discrimination, and the test that cannot fail](#discrimination-and-the-test-that-cannot-fail)
- [Sequencing so a failure is informative](#sequencing-so-a-failure-is-informative)
- [Back to back beats better instruments](#back-to-back-beats-better-instruments)
- [Duration, and the two settling times](#duration-and-the-two-settling-times)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

An engine is developed by testing it. The campaign is the sequence of firings that gets from a drawing to a qualified engine, and its structure is a series of decisions about what each firing is allowed to be surprised by.

This sub-domain is the propulsion counterpart to [fluidSystemsTesting](../../../fluidSystems/fluidSystemsTesting/docs/TestCampaignPlanning.md), and it inherits that domain's principle: **a test that cannot fail its own acceptance criterion has not tested anything.** What is added here is the arithmetic for whether a hot fire can.

---

## The five levels

| Level | Hardware | Question |
|---|---|---|
| Component | Injector, igniter, valve, alone | Does the part work in isolation |
| Subscale | A smaller chamber, same element pattern | Does the combustion behave |
| Development | Full scale, iterating | Can it be made to work |
| Qualification | Flight-representative, to the environment | Does the design meet the requirement |
| Acceptance | Each flight article | Was this unit built like the qualified one |

The distinction that matters is the last one. **Qualification tests a design; acceptance tests a unit.** They can look identical on a stand and they answer different questions, and the acceptance criterion is tight where the qualification criterion is broad, precisely because the design question has already been settled.

---

## What each level is actually for

**Component testing exists to move the surprise earlier.** An injector that fails at the component level costs an injector. The same failure at development costs a chamber and a schedule.

**Subscale testing exists because combustion does not scale but element behaviour does.** A subscale chamber with the same element pattern, mixture ratio and chamber pressure tests the element, and it does not test the acoustics, which scale with chamber diameter and are the reason a subscale-stable engine can be full-scale unstable.

**Development testing is the expensive part and it is where the campaign structure earns or loses its money.** See the discrimination section below.

**Qualification exists to be evidence.** Its criterion is the requirement, not the best number achieved.

**Acceptance exists to catch a build error**, and its criterion should be tight enough to do that and no tighter.

---

## Discrimination, and the test that cannot fail

An acceptance band narrower than the measurement uncertainty is a band decided by noise.

```
discriminationRatio = acceptanceBand / measurementUncertainty
```

On the reference booster, with a c* measurement carrying 1.50 per cent:

| Criterion | Band | Ratio | Verdict |
|---|---|---|---|
| Validate the design | 4 % | 2.7 | Decides, and it will be argued about |
| Rank two injectors | 1 % | 0.7 | **Refused** |

**A four per cent effect is resolvable, if only just. A one per cent effect is not resolvable at all.**

[HotFireTest](CampaignStructure.md) raises rather than reporting a low ratio when the band is inside the uncertainty. A test that cannot distinguish a pass from a fail and is run anyway produces a verdict with a signature on it, and that is worse than not running it.

**Most development campaigns want to rank and are funded on the strength of validating.** The gap between those two sentences is where a lot of test money goes, and computing the ratio before the campaign rather than after is the cheapest thing in this document.

---

## Sequencing so a failure is informative

A campaign is sequenced so that when something fails, the failure names its own cause.

**Change one thing at a time**, which is obvious and is abandoned under schedule pressure faster than anything else on this list.

**Put the cheapest test that could fail first.** A campaign that runs its expensive tests first buys information in the wrong order.

**Run the same point twice, early.** Repeatability is the only measurement of scatter that exists, and a campaign with no repeat points has no way to distinguish a change from noise later.

**Instrument for the failure you have not had yet**, because adding a channel after a failure means the firing that produced the evidence did not record it.

---

## Back to back beats better instruments

The reference booster cannot rank two injectors a point apart, and improving both dominant channels only takes the ratio from 0.7 to 1.5, still below the working floor of three.

**Instrumentation alone will not buy that comparison.** The answer is a different comparison rather than a better measurement: fire both injectors on the same hardware, back to back, on the same day, and compare them to each other rather than each to an absolute.

The shared errors cancel. The throat is the same throat. The load path is the same load path. The flow meters have the same calibration and the same drift.

**That is the same cancellation the correlation trap in [DataReduction](DataReduction.md) is about, used deliberately this time.** A differential measurement is worth more than an absolute one whenever the question is differential, and the question in a development campaign almost always is.

---

## Duration, and the two settling times

Two things settle at rates three orders of magnitude apart.

| Quantity | Settles in |
|---|---|
| Chamber pressure | About 20 residence times, 29 ms on this engine |
| Wall temperature | Its own thermal time constant, of order 3 s |

A short burn gives a **valid performance number and an invalid wall temperature**, and the wall temperature is usually what the short test was run to get.

A 10 second burn on this engine leaves a 7 second window in which both are steady. That window, not the burn duration, is what a reduction should be taken from.

---

## Worked numbers

| Quantity | Value |
|---|---|
| c* measurement uncertainty | 1.50 % |
| Discrimination ratio at a 4 per cent band | 2.7 |
| Discrimination ratio at a 1 per cent band | 0.7, refused |
| Ratio at 1 per cent with both channels improved | 1.5 |
| Working floor | 3.0 |
| Chamber settling | 29 ms |
| Wall settling | 3 s |
| Usable window in a 10 s burn | 7 s |

---

## Design rules of thumb

- **Compute the discrimination ratio before the campaign.** It decides whether the campaign can answer its question.
- **Do not run a test that cannot fail.** The tool refuses it and so should the review.
- **Compare differentially when the question is differential.** Back to back beats better instruments.
- **Repeat a point early.** Scatter cannot be inferred from a single firing.
- **Size the burn for the slowest thing being measured**, which is the wall.
- **Change one thing at a time**, and notice when the schedule starts arguing otherwise.

---

## Failure modes

**An acceptance band tighter than the measurement.** Refused by the tool. Decided by noise in the review.

**A campaign funded to validate and expected to rank.** The commonest structural failure and it is visible before any hardware is built.

**No repeat points.** No measurement of scatter, so no way to attribute a later change.

**Subscale stability taken as full scale stability.** Element behaviour scales, acoustics do not.

**Qualification criteria applied at acceptance, or the reverse.** Different questions.

**A short burn used for a wall temperature.** Three orders of magnitude too short.

---

## Tool interface

```python
from HotFireTest import HotFireTest

test = HotFireTest()
test.setInputs({'objective':       'Rank injector A against injector B',
                'chamberPressure': 10.0e6,
                'chamberDiameter': 0.1433,
                'residenceTime':   0.00147,
                'duration':        10.0})

discrimination = test.checkDiscrimination(acceptanceBand = 0.04, uncertainty = 0.015)
duration       = test.checkDuration()
```

`objective` is required and is free text, because a test without a stated question is the failure this class exists to catch and it is the one thing here that cannot be checked automatically.

---

## References

- [fluidSystemsTesting TestCampaignPlanning](../../../fluidSystems/fluidSystemsTesting/docs/TestCampaignPlanning.md), for the campaign philosophy this inherits
- Sutton and Biblarz, *Rocket Propulsion Elements*, the engine development and testing chapter
- Biggs, *Space Shuttle Main Engine: The First Ten Years*, for what a real development campaign costs in tests and hardware
