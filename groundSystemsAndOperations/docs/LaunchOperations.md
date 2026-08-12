[Home](../README.md) > Launch Operations

# Launch Operations

## Contents

- [Overview](#overview)
- [The count is a graph](#the-count-is-a-graph)
- [Holds and recycles](#holds-and-recycles)
- [Scrub turnaround](#scrub-turnaround)
- [Launch commit criteria](#launch-commit-criteria)
- [The console](#the-console)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A countdown looks like a list and it is a dependency graph. Everything interesting about launch operations follows from that one fact.

---

## The count is a graph

Some tasks run in parallel and some cannot, so **the total is the longest chain rather than the sum**. In the worked example the count is 220 minutes against a serial sum of 380, a parallel gain of 1.73.

**The tasks not on the critical path are free until they are not.** A task with an hour of float costs nothing when it slips by ten minutes and becomes the schedule when it slips by seventy. That is why the near-critical list, the tasks with float below a few per cent of the count, is worth watching more closely than the critical path itself: the critical path is already known.

**Adding capability off the critical path buys nothing.** A faster kerosene transfer on a vehicle whose count is set by the oxygen load is money spent on the wrong pump.

---

## Holds and recycles

The distinction that costs programmes windows.

**A hold stops the clock.** Its cost is not its own length.

**A recycle backs the count up to an earlier point**, because some of what was done has to be redone: a tank topped and then held too long, an alignment that has aged out, a purge that has to be repeated. **The recycle is the hold plus the re-run**, and the re-run is usually the larger part.

In the worked example a ten minute hold at T-4 minutes that backs up to T-20 costs **26 minutes, a multiplier of 2.6**. Against a sixty minute window it fits with 34 minutes to spare, and a second hold would not.

**Whether the window survives the recycle is the launch commit decision**, and it has to be worked out before the count rather than during it.

---

## Scrub turnaround

How long before the next attempt, and it is set by one thing.

The candidates run in parallel with each other: propellant replenishment, flight battery recharge, ordnance safing and re-arm, crew duty and rest, range reset. **The turnaround is the largest of them and not the sum**, which is the most commonly ignored fact in launch operations planning.

In the worked example the drivers sum to 94 hours and the turnaround is 48, set entirely by hydrogen resupply from off site. **Fixing it buys 32 hours and no more**, because crew duty is waiting at 16.

**Turnaround is a design requirement rather than an operational detail.** It sets how many attempts a campaign gets, and attempts drive launch probability far harder than any single launch commit criterion does. See [WeatherAndConstraints](WeatherAndConstraints.md).

---

## Launch commit criteria

The list of conditions that all have to hold at T-0. Vehicle, ground, range and weather.

Three things about them are worth stating.

**They multiply.** Six criteria each satisfied nine times in ten give 53 per cent, not 90. See [WeatherAndConstraints](WeatherAndConstraints.md), where this is worked.

**A criterion is never free.** Adding one costs the campaign its own violation rate, regardless of how rarely it fires alone, and that cost is invisible from inside a review of that criterion.

**And a criterion nobody can measure is not a criterion.** If the console cannot see the parameter, the rule resolves to somebody's judgement under time pressure, which is a different and worse thing.

---

## The console

Not a calculation, and worth writing down because it is a decision.

**One person is responsible for the count.** Polls are taken, positions report go or no-go, and the authority to hold sits with named people rather than with whoever notices first.

**Anybody can call a hold and only one person can resume.** That asymmetry is deliberate: stopping is cheap and starting is not.

**The rules are agreed before the count.** A rule invented at T-4 minutes is a decision made by tired people in front of an audience, and that is the worst available condition for one.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Count, critical path | 220 min |
| Serial sum of all tasks | 380 min |
| Parallel gain | 1.73 |
| Critical chain | pad clear, RP-1 load, LO2 load stage 1, terminal count |
| Recycle from a 10 min hold at T-4 | 26 min, 2.6x |
| Window | 60 min, fits with 34 min spare |
| Turnaround | 48 h, hydrogen resupply |
| Sum of turnaround drivers | 94 h |
| Gain from fixing the governing driver | 32 h |
| Attempts in a 14 day campaign | 8 |

**The hydrogen load is not on the critical path** in this case, which is worth noticing: the kerosene chain is longer. The hydrogen still sets the turnaround, so it governs the campaign without governing the count.

---

## Design rules of thumb

- **Build the count as a graph and find the critical path.** The sum is not the answer.
- **Watch the near-critical tasks**, not the critical ones. The critical path is already known.
- **Cost a hold as hold plus re-run.** The re-run is the larger part.
- **Improve the governing turnaround driver or improve nothing.**
- **Treat turnaround as a launch probability requirement.**
- **Agree the launch commit criteria and the hold authority before the count.**

---

## Failure modes

**The count estimated as a sum.** It is a longest chain.

**Capability added off the critical path.** No schedule gain at all.

**A hold costed as its own length.** The recycle is several times it.

**Turnaround improved everywhere but the governing driver.** Nothing moves.

**A criterion with no measurement behind it.** It resolves to judgement under pressure.

**A rule invented during the count.** The worst conditions available for a decision.

---

## Tool interface

```python
from CountdownTimeline import CountdownTimeline

timeline = CountdownTimeline()
timeline.setInputs({'tasks': [{'name': 'pad clear', 'duration': 2700.0},
                              {'name': 'RP-1 load', 'duration': 4500.0,
                               'predecessors': ['pad clear']}],
                    'windowDuration':    3600.0,
                    'turnaroundDrivers': {'LH2 resupply': 172800.0,
                                          'crew duty':     57600.0}})

path       = timeline.calculateCriticalPath()
recycle    = timeline.calculateRecycle(holdAt = 240.0, backUpTo = 1200.0, holdDuration = 600.0)
turnaround = timeline.calculateTurnaround()
attempts   = timeline.attemptsPerCampaign(1209600.0)
```

---

## References

- [WeatherAndConstraints](WeatherAndConstraints.md), for what attempts are worth
- [PropellantStorageAndTransfer](PropellantStorageAndTransfer.md), for the other limit on attempts
- [HazardousOperations](HazardousOperations.md), for what the count has to sequence around
