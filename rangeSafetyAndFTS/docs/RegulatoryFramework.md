[Home](../README.md) > Regulatory Framework

# Regulatory Framework

## Contents

- [Overview](#overview)
- [Who regulates what](#who-regulates-what)
- [What Part 450 requires](#what-part-450-requires)
- [The safety criteria](#the-safety-criteria)
- [Hazard control strategies](#hazard-control-strategies)
- [What an applicant submits](#what-an-applicant-submits)
- [Designing to it rather than discovering it](#designing-to-it-rather-than-discovering-it)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Range safety is the one part of launch vehicle engineering where the governing document is the substance rather than a reference. This is what it says.

---

## Who regulates what

Two authorities, and the split confuses people.

**The FAA licenses the launch**, under 14 CFR Part 450, for any commercial launch or reentry from a US site or by a US entity. That licence is what makes the launch legal.

**The range operator controls the range**, whether that is a federal range under its own manual or a private site. The range's requirements sit alongside the licence and can be stricter.

**A commercial launch from a federal range answers to both**, which is the common case and means two sets of documentation with overlapping content and different formats.

---

## What Part 450 requires

The structure is worth knowing because it is the shape of the safety case.

**A hazard control strategy** for each phase of flight, chosen from a defined set.

**A flight safety analysis** that quantifies the risk, including debris, blast overpressure and toxic release.

**Safety criteria met**, which are the numbers in the next section.

**And the evidence for all of it**, submitted as part of the application.

**The regulation is performance-based rather than prescriptive** in most places: it says what has to be shown rather than how to build. That is more work for an applicant and it is what permits an autonomous system, a novel vehicle or an unusual trajectory to be licensed at all.

---

## The safety criteria

14 CFR 450.101, read from the regulation.

| Criterion | Limit |
|---|---|
| Collective risk, public | 1e-4 expected casualties |
| Collective risk, neighbouring operations personnel | 2e-4 expected casualties |
| Individual risk, public | 1e-6 probability of casualty per launch |
| Individual risk, neighbouring operations personnel | 1e-5 probability of casualty per launch |
| Aircraft | 1e-6 probability of impact with debris capable of causing a casualty |

**Both collective and individual criteria apply**, and they catch different failures. See [PublicRiskAnalysis](PublicRiskAnalysis.md).

**And 450.145 sets the flight safety system at a design reliability of 0.999 at 95 per cent confidence**, for the onboard and off-vehicle portions both. See [FlightTerminationSystems](FlightTerminationSystems.md) for why that number cannot be demonstrated by test.

---

## Hazard control strategies

The choice that shapes everything else, and it is made per phase of flight.

**A flight safety system**, which is the traditional answer: carry a termination system and enforce trajectory limits with it.

**Physical containment**, where the vehicle cannot reach anything that matters, which suits a small vehicle on a large range.

**Wind weighting**, for unguided vehicles, where the launcher is aimed to account for the measured wind on the day.

**And flight hazard area review**, where the areas can be cleared and kept clear for the duration.

**The strategy determines whether an FTS is required at all**, which is why it is chosen first and why a small vehicle on a remote site can sometimes fly without one. **That is a licensing decision rather than an engineering preference**, and it is settled early or not at all.

---

## What an applicant submits

Worth listing, because the volume surprises people and because it is the real schedule item.

**The trajectory and its dispersions**, in a form the analysis can be run against.

**The debris analysis**: catalogue, ballistic coefficients, break-up assumptions and the resulting footprints.

**The risk analysis** against every criterion, with the population data used.

**The flight safety system description**, its reliability analysis, its test plan and its verification evidence.

**And the operational documents**: the hazard areas, the clearing plan, the launch commit criteria and the procedures.

**None of that can be produced late.** The debris analysis needs a vehicle design, the risk analysis needs the debris analysis, and the licence needs all of it, which puts the whole chain on the programme's critical path.

---

## Designing to it rather than discovering it

The domain's ethos, and the specific things it means.

**The launch azimuth is a risk decision before it is a performance one.** Choose it against overflown population and then see what performance it leaves, rather than the other way round.

**The trajectory shape is constrained.** A lofted trajectory keeps the impact point closer for longer, which buys destruct line margin at a performance cost.

**The FTS is a vehicle-level requirement with mass, power and volume**, and it is the highest reliability item on board. Fitting it late is expensive.

**And the reliability estimate feeds the risk analysis directly**, so a vehicle with a weak reliability argument has a weak risk case regardless of its hardware.

**All four are known at concept.** Discovering them at licensing is the expensive path, and it is the common one.

---

## Design rules of thumb

- **Choose the hazard control strategy first.** It decides whether an FTS is needed.
- **Pick the azimuth on population, then check performance.**
- **Put the licence chain on the programme schedule.** It is serial and long.
- **Expect two sets of requirements** at a federal range.
- **Treat the reliability estimate as a licensing input**, not just an engineering one.
- **Read the regulation.** It is performance-based and it says what has to be shown.

---

## Failure modes

**A hazard control strategy assumed rather than chosen.** It decides the FTS requirement.

**An azimuth picked for performance.** Risk follows population.

**A licence application started after the design freezes.** The chain is serial.

**Range requirements discovered after the FAA ones.** Both apply and the range can be stricter.

**A reliability number quoted without a basis.** It multiplies the whole risk analysis.

---

## References

- 14 CFR Part 450, *Launch and Reentry License Requirements*
- AFSPCMAN 91-710, *Range Safety User Requirements*, not read
- RCC 319 and RCC 321, the Range Commanders Council standards, not read
- [StandardsIndex](StandardsIndex.md)
