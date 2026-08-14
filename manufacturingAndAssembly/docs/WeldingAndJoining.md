[Home](../README.md) > Welding and Joining

# Welding and Joining

## Contents

- [Overview](#overview)
- [Where the weld analysis lives](#where-the-weld-analysis-lives)
- [Process selection](#process-selection)
- [Friction stir](#friction-stir)
- [Distortion](#distortion)
- [Qualification](#qualification)
- [Joining that is not welding](#joining-that-is-not-welding)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Every weld is a fracture critical location, an inspection, a distortion source and a knockdown. **The design decision that matters most is how many there are.**

---

## Where the weld analysis lives

Stated first, because this domain deliberately duplicates none of it.

**[Weld](../../fluidSystems/fluidSystemsLibrary/docs/Welds.md) in fluidSystems** computes joint efficiency, heat affected zone knockdown and the WRC-1992 ferrite number. It was built there because a fluid system is mostly welded joints, and it applies unchanged to structure.

**[joiningProcesses](../../aerospaceMaterials/joiningProcesses/) in aerospaceMaterials is deliberately docs-only** for the same reason, and its overview says so.

**What stays here is selection, distortion and qualification**, which are manufacturing decisions rather than joint calculations.

---

## Process selection

| Process | Heat input | Distortion | Where it wins |
|---|---|---|---|
| GTAW | high | high | repair, short runs, anything a machine cannot reach |
| Plasma arc | moderate | moderate | thicker sections in one pass |
| Electron beam | very low | very low | deep narrow welds, and it needs a vacuum chamber |
| Laser beam | very low | very low | as EBW without the vacuum, at less penetration |
| Friction stir | none, no melting | low | long straight or circumferential aluminium welds |

**The ordering by heat input is the ordering by almost everything else**: distortion, heat affected zone width, knockdown and residual stress all follow it.

**And the constraint that decides is usually access rather than capability.** Electron beam needs the part in a vacuum chamber, friction stir needs a backing anvil and a rigid load path, and both are ruled out on a joint that has to be made after the structure closes out.

---

## Friction stir

Worth its own section because it changed what an aluminium tank is.

A rotating shouldered pin traverses the joint, plasticising rather than melting the material. **No melting means no solidification cracking, no porosity from a shielding gas failure and a far narrower heat affected zone**, which is why the knockdown is smaller than a fusion weld's.

**The costs are mechanical rather than metallurgical.** It needs a large reaction force, a rigid backing anvil, and a machine stiff enough to hold the tool position under that force. It leaves an exit hole at the end of the run unless a retractable pin is used. And it is a straight-line or circumferential process: it does not do complex three-dimensional joints.

**The result is that the tooling decision and the weld decision become the same decision**, which is unusual and is the practical reason friction stir arrives with a large capital number attached.

---

## Distortion

The manufacturing problem welding actually causes, as distinct from the strength problem.

**A weld shrinks as it cools and the shrinkage is restrained by the surrounding structure**, which leaves residual stress and moves the part. Three components: transverse shrinkage across the joint, longitudinal shrinkage along it, and angular distortion from the through-thickness temperature gradient.

**On a rolled barrel the transverse shrinkage pulls the cylinder out of round**, and in the worked [tolerance stack](AssemblyAndIntegration.md) it is the second largest contributor at 28 per cent of the statistical stack.

**The controls are all upstream of the weld.** Minimise heat input, which is process selection. Balance the welding sequence so that shrinkage on one side is offset by shrinkage on the other. Restrain the part in a fixture that reacts the shrinkage, which converts distortion into residual stress and is a trade rather than a fix. And pre-set the part to the opposite of the expected distortion, which is the same idea as springback overbend and is established on a first article.

**Distortion is not modelled in this repository**, and that is named rather than implied. It needs a thermal-mechanical analysis of the weld and its restraint, which is a real piece of work.

---

## Qualification

**A weld procedure is qualified, and so is the welder, and so is the equipment.** All three, separately, and a change to any of them is a requalification question.

The procedure specification fixes the joint geometry, the material, the filler, the heat input, the position, the preheat and the interpass temperature. **A qualified procedure is qualified over a range**, and a change outside that range is a new procedure.

**The thing that surprises people is how narrow some of the ranges are**: a thickness change, a position change or a filler lot change can each fall outside.

**And a coupon made the same way has to be destroyed**, which is the domain's design ethos in its most literal form. See [ProcessQualification](ProcessQualification.md).

---

## Joining that is not welding

Named because a design that reaches for a weld by default is a design with too many welds.

**Bolted joints** are inspectable, reversible and heavy, and they are the right answer at an interface that has to come apart. [aerospaceStructures](../../aerospaceStructures/) owns the analysis.

**Bonded joints** are light and continuous, and their strength depends on a surface preparation that cannot be inspected after the fact. That is the fundamental problem with adhesive bonding on a flight structure: **a bad bond and a good bond look identical.**

**Brazing** joins dissimilar materials and produces a joint weaker than either, which is fine where the joint is not the load path and is the usual answer in a heat exchanger.

---

## Design rules of thumb

- **Count the welds.** Each is an inspection, a knockdown and a distortion source.
- **Choose the process by access first and heat input second.**
- **Balance the welding sequence** before reaching for a fixture.
- **Expect the barrel weld to be a top-two tolerance contributor.**
- **Qualify the procedure, the welder and the equipment separately.**
- **Do not bond a flight-critical joint you cannot inspect.**

---

## Failure modes

**A weld chosen where a bolt would do.** An inspection forever.

**Process selected on capability without checking access.** EBW needs a chamber.

**Distortion managed by fixturing alone.** It becomes residual stress instead.

**A procedure change assumed to be inside its range.** Thickness and position are narrow.

**A bonded joint on a primary load path.** A bad bond looks like a good one.

---

## References

- [Welds](../../fluidSystems/fluidSystemsLibrary/docs/Welds.md), which owns joint efficiency and HAZ knockdown
- [joiningProcesses](../../aerospaceMaterials/joiningProcesses/), docs-only for the same reason
- [aerospaceStructures](../../aerospaceStructures/), for bolted and bonded joint analysis
- AWS D17.1, aerospace fusion welding, not read
