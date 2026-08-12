[Home](../README.md) > Validation References

# Validation References

The external sources this domain's tools are checked against, and what they cannot check.

Kept separate from the reference lists at the foot of each document. Those are further reading; this is the material a test asserts against. The methodology is in [validation/README.md](../../validation/README.md).

| Level | Means |
|---|---|
| **Hardware** | Compared against measured or specified performance of real hardware |
| **Standard** | Reproduces a published standard or definition exactly. Catches an implementation error only |
| **Bounded** | No direct comparison, but the result is bracketed by something |
| **Unvalidated** | No external anchor. Recorded with what depends on it |

**This domain splits cleanly in two, and the split is worth stating first.** Its explosives siting is anchored to a standard read in full, and reading it corrected two things a summary would have got wrong. Everything operational is representative.

---

## The explosives siting standard

- **Source:** DESR 6055.09, Edition 1 Change 1, 23 February 2024, Volume 5 Enclosure 4 Table V5.E4.T5 and footnote f. Reproduced identically as NASA-STD-8719.12A Table 5-29, with the K factors as Table E-1
- **Validation level:** Standard, read in full
- **Relevance:** Every separation distance the domain computes
- **Key findings:**
  - The equivalence percentages for six liquid combinations, in both the range launch and static test columns
  - The hydrogen rule as `max(8 W**(2/3), 0.14 W)` in pounds, with the crossover at 186,589 lb or 84,635 kg
  - The RP-1 two tier rule, 20 per cent up to 226,795 kg and 10 per cent above
  - Twelve K factors with their overpressures, from 1.79 at 386.9 psi to 50 at 0.9

**Both tables are duplicated into [validation/referenceCases.py](../../validation/referenceCases.py) and a test asserts the library against the register.** They are separate files on purpose: a library edited without the register is a library that has quietly stopped citing anything.

---

## What reading it corrected

Two things, and the first would have been a substantial error.

**The sixty per cent figure is not the siting rule.** The widely quoted 60 per cent TNT equivalence for LO2/LH2 comes from the Project PYRO test series and from an evaluation of shuttle on-pad operations. It is a yield figure. The standard sites launch vehicles on the larger of the sublinear term and fourteen per cent.

**Building on sixty per cent would have overstated a small stage by about a factor of three** and, worse, would have missed the shape of the rule entirely: that the effective fraction rises as the load falls is the domain's headline result and a flat percentage has no such behaviour.

**The standard's bracketed metric coefficient is not the conversion of its English one.** `8 W**(2/3)` in pounds converts exactly to `6.147 Q**(2/3)` in kilograms. The standard prints `4.13`. The two differ by a factor of 1.488 with the published metric form the smaller, and the discrepancy is present in both DESR 6055.09 Edition 1 Change 1 and NASA-STD-8719.12A.

**An analyst working natively in SI from the bracketed coefficient gets a shorter siting distance** than the form the table is built on. This library computes in the English form and converts, which is the conservative reading, and a test asserts the discrepancy rather than correcting it silently. **No reference was adjusted to make anything pass.**

**This is the second time reading a standard rather than a summary changed a result in this repository.** The first was NASA-STD-5017B in [mechanismsAndSeparation](../../mechanismsAndSeparation/docs/ValidationReferences.md), where a summary reported the required torque margin as 1.0 and the standard says 0. The pattern is consistent enough to be a rule.

---

## Closed forms

- **Validation level:** Standard, and exact
- **Key findings:**
  - Cube root scaling: eight times the mass is exactly twice the distance
  - Distance is exactly linear in the K factor
  - `d = 40 W**(1/3)` gives exactly 400 ft for 1,000 lb, through the library's kilogram interface
  - The hydrogen effective fraction never falls below fourteen per cent, because the rule is a maximum
  - The tanking phases deliver exactly the flight load
  - The ground demand shares sum to one
  - Hold demand is exactly linear in hold duration
  - The critical path is never longer than the serial sum
  - Constraint probabilities multiply, and cumulative probability is one minus the failure product
  - The correlated chain reproduces the unconditional rate exactly, and its lag one correlation is exactly the input

**The last of those earns its place.** A correlated model that does not reproduce its own unconditional rate is a fudge with a plausible shape, and the test is the difference between the two.

---

## Bounded

**The weather share of scrubs.** Roughly half of launch scrubs at the Eastern Range across three decades were weather, which is a published record. The library's 48 per cent sits inside that, and the test asserts a band rather than a value.

**It bounds the share and says nothing about the rates that produce it**, which is why the individual criterion violation probabilities are unvalidated below.

---

## What is not validated

Three entries in [validation/referenceCases.py](../../validation/referenceCases.py) under `UNVALIDATED`, and each names what survives it.

**Loading phase fractions** (`loadingPhaseFractions`). The rate and load fractions, and the detank recovery, are representative of cryogenic practice rather than taken from a procedure. The tanking duration scales with them. **The structural result does not**: chill-down runs at a fraction of the transfer rate because the point of it is to boil, so it takes a share of the clock out of all proportion to the mass it moves. That holds for any rate fraction below one. **Half of this could be closed internally**, because the transfer line geyser and water hammer limits are already computable in [fluidSystems](../../fluidSystems/).

**Scrub causes and criterion violation rates** (`scrubCauseSplit`). The weather share is bounded as above; everything else is representative. The per-attempt go probability and the whole campaign figure scale with them. **Neither result does**: that independent criteria multiply is arithmetic, and that attempts beat criteria follows from the cumulative probability being one minus a product.

**Weather correlation** (`weatherCorrelation`). The chain is internally exact and its value is representative, and a two-state chain is a coarse model of a weather system in any case. The gap between the independent and correlated figures scales with it, and that gap is offered as the uncertainty in the answer rather than as a result. **The direction does not scale**: correlation always costs campaign probability.

---

## What is not modelled at all

Distinct from unvalidated, and listed because a reader should not have to infer it.

**GSE fluid analysis.** Deliberately not built. [fluidSystems](../../fluidSystems/) computes every component in a ground half system and a second implementation would drift. See [GSEDesign](GSEDesign.md).

**Chill-down mass and boil-off rate.** Both consumed as inputs from the domains that own them.

**Toxic dispersion.** [HazardousOperations](HazardousOperations.md) states that the toxic exclusion zone scales with dispersion rather than with quantity, and computes only the explosive one.

**Fragmentation and thermal hazard distance.** The K factors model overpressure only, which the standard says explicitly and which a distance calculation cannot tell you.

**Acoustic suppression water flow.** The environment belongs to [environmentsAndLoads](../../environmentsAndLoads/) and the water is a facility design.

**Methane.** Not in the equivalence table, and the library refuses rather than borrowing the kerosene number.

---

## The shape of what is here

**What it concludes about siting** rests on a standard read in full, and the arithmetic on top of it is exact. That half of the domain is as well anchored as anything in this repository.

**What it concludes about operations** rests on arithmetic that survives its inputs: products, sums, longest chains and maxima. The numbers are representative and the conclusions are not at risk from them.

**What it reports** rests on representative tables a real programme would replace from its own procedures, and none of them is a research problem.

**And what it documents** rests on AFSPCMAN 91-710, which was not read. That is the largest documentation gap here, and it is the document that would turn most of the hazardous operations material from practice into requirement.
