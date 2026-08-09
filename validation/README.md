[Home](../README.md) > Validation

# Validation

## Contents

- [Why this exists](#why-this-exists)
- [The rule](#the-rule)
- [What a reference has to carry](#what-a-reference-has-to-carry)
- [Validated, bounded, unvalidated](#validated-bounded-unvalidated)
- [The comparison is the hard part](#the-comparison-is-the-hard-part)
- [Current state](#current-state)
- [What is not validated](#what-is-not-validated)
- [How to add a case](#how-to-add-a-case)
- [References](#references)

---

## Why this exists

Every class in this repository produces numbers that are internally consistent. The test suites are
thorough and they check that the code does what it was written to do. **None of that catches a
model that is wrong.**

The prompt for this directory was a specific failure. The propulsion hub carried a placeholder for
chamber wall heat load, two per cent of jet power, clearly labelled as a placeholder. A document was
written asserting the conclusion that placeholder produced. Three commits later the combustionDevices
sub-domain computed the same quantity properly from Bartz and got three times as much, which
inverted the conclusion.

Nothing in 666 passing tests caught it, because both numbers were internally consistent and neither
had ever been compared to anything outside the repository.

Worse, the correction had the same problem. Bartz gave 8.13 MW, the placeholder gave 2.72 MW, and
there was no external anchor for either. The commit message asserted that Bartz was the correction.
That was an assumption presented as a finding.

---

## The rule

**A tool that has only been checked against itself has not been checked.**

Two consequences follow, and the second is the one that takes discipline.

**Every domain needs at least one comparison against something published.** Not a textbook equation
re-derived, which is still internal: a number somebody measured or specified for real hardware.

**No reference may be adjusted to make a test pass.** If a tool disagrees with a reference, there
are exactly three honest outcomes: the tool is wrong, the comparison is wrong, or the disagreement
is real and understood. Editing the reference is not among them, and neither is tuning a coefficient
until the disagreement goes away.

---

## What a reference has to carry

Four fields, and an entry without all four is not usable.

| Field | Why |
|---|---|
| `value` | The published number |
| `source` | Specific enough to find again, with an access date |
| `kind` | Measured, specification, derived, or estimate |
| `note` | What the number includes, which is usually the difficult part |

**`kind` does most of the work.** A measured throat heat flux and a published engine specific
impulse are different sorts of number and can be compared against different things. An estimate is
a sanity bound and not a check, and calling one a validation is how a repository convinces itself of
something false.

A test asserts that every reference carries all four, because the discipline decays otherwise.

---

## Validated, bounded, unvalidated

Three states, and the third is not a failure.

**Validated.** Compared against published hardware data and agreeing within a band that was decided
before the comparison was run.

**Bounded.** No direct reference, but the calculation is bracketed by something. A correlation with
a published accuracy band bounds any result computed from it: Bartz is plus or minus twenty per
cent, so nothing downstream of Bartz may claim better.

**Unvalidated.** No external anchor. Recorded explicitly in `UNVALIDATED` with what depends on it
and what would fix it.

**The unvalidated register existing is more useful than it being short.** A reader who wants to know
whether to trust a number should be able to find out, and "we looked and could not find data" is a
real answer that beats silence.

---

## The comparison is the hard part

Getting a reference number is easy. Establishing that it is the same quantity your tool computes is
not, and it is where the value is.

The propulsion case is the worked illustration. The hub library models the thrust chamber and the
nozzle. A published engine specific impulse is a whole-engine figure.

| Engine | Cycle | Published vacuum Isp | Library ideal | Implied efficiency |
|---|---|---|---|---|
| RS-25 | Staged combustion, closed | 452.3 s | 459.8 s | 0.984 |
| F-1 | Gas generator, open | 304.0 s | 328.7 s | 0.925 |

A closed cycle engine puts all of its propellant through the main chamber, so its published impulse
is very nearly a thrust chamber figure and **RS-25 validates the library at 1.7 per cent**.

An open cycle engine dumps turbine exhaust overboard at a fraction of the main impulse. That is a
cycle loss the library does not model, so **F-1 disagrees by 8.1 per cent and is supposed to.**

The temptation is to average the two and call the result an efficiency. That would fit a cycle loss
into a nozzle coefficient and produce a model that agrees with both engines and is wrong about both.
F-1 is retained in the reference set specifically as the case that marks the boundary of what the
library covers, and a test asserts that it continues to disagree.

---

## Current state

| Domain | Level | Against what | Bibliography |
|---|---|---|---|
| [propulsion](../propulsion/README.md) | **Hardware** | RS-25 vacuum and sea level impulse, throat diameter | [refs](../propulsion/docs/ValidationReferences.md) |
| [environmentsAndLoads](../environmentsAndLoads/README.md) | **Hardware** | GEVS qualification spectrum against its published 14.1 Grms | [refs](../environmentsAndLoads/docs/ValidationReferences.md) |
| [thermalManagement](../thermalManagement/README.md) | **Hardware** | Stefan-Boltzmann exact, solar constant, white paint equilibrium | [refs](../thermalManagement/docs/ValidationReferences.md) |
| [fluidSystems](../fluidSystems/README.md) | **Hardware** | IAPWS-95 water density through the property backend | [refs](../fluidSystems/fluidSystemsLibrary/docs/ValidationReferences.md) |
| [aerospaceStructures](../aerospaceStructures/README.md) | Standard | SP-8007 knockdown at five R/t, classical buckling closed form | [refs](../aerospaceStructures/docs/ValidationReferences.md) |
| [propulsion/combustionDevices](../propulsion/combustionDevices/README.md) | Bounded | Bartz accuracy band only. Heat load unvalidated | [refs](../propulsion/combustionDevices/docs/ValidationReferences.md) |
| [aerospaceMaterials](../aerospaceMaterials/README.md) | Internal | Seed agreement against `common/materials.py`, itself MMPDS-derived | outstanding |
| [fluidSystems/fluidSystemsTesting](../fluidSystems/fluidSystemsTesting/README.md) | Internal | Process domain. Margin relationships only | outstanding |

**Four domains now reach hardware level and one reaches standard level.** The two remaining are the
two with least to get numerically wrong: materials is already seeded from an MMPDS-derived table and
tested against it, and testing is a process domain rather than a physics one.

**The distinction between hardware and standard is not cosmetic.** aerospaceStructures reproduces
the SP-8007 knockdown curve to 1e-4 at five radius-to-thickness ratios, which proves the
implementation and proves nothing about the curve. The curve is a lower bound fitted to 1960s test
scatter that the document does not reproduce in re-fittable form, and it remains the least validated
consequential number in the repository.

---

## What is not validated

The register lives in `referenceCases.py` under `UNVALIDATED`. Three entries at present, all in
combustionDevices, and the first is the one that matters.

**Chamber heat load.** The 8.13 MW computed for the reference engine is a Bartz result, not a
validated one. It replaced a hub placeholder lower by a factor of three. The direction of that
correction is supported by an independent argument, that the placeholder used jet power as its base
where thermal power is the physically meaningful one, but neither number has an external anchor.
Published engine data gives coolant flow and channel counts and rarely the heat load. The next step
is a textbook worked example that carries a full cooling calculation.

**Injector mixing quality.** A ranking, not a measurement. Used only to order element types and it
must not be used to predict c* efficiency.

**Coolant limits.** The RP-1 coking limit of 575 K drives the conclusion that the reference engine
cannot be regeneratively cooled. That is a widely quoted range rather than a sourced value, and the
real limit is a film temperature depending on residence time and surface chemistry.

---

## How to add a case

1. Find published data for real hardware. Record the source with an access date.
2. Decide what `kind` it is before deciding what to compare it against.
3. Write the `note` first. If you cannot state what the number includes, you cannot use it.
4. Decide the tolerance and its reason **before** running the comparison.
5. Run it. If it disagrees, investigate rather than adjusting.
6. If it cannot be validated, add it to `UNVALIDATED` with what depends on it.

Step four is the one that gets skipped and the one that matters. A tolerance chosen after seeing the
result is not a test, it is a description.

---

## References

- Bartz, *A simple equation for rapid estimation of rocket nozzle convective heat transfer
  coefficients*, 1957
- [NASA TN, comparison of experimental heat transfer coefficients against Bartz](https://ntrs.nasa.gov/api/citations/19710011726/downloads/19710011726.pdf)
- [RS-25 specifications](https://en.wikipedia.org/wiki/RS-25)
- [Rocketdyne F-1 specifications](https://en.wikipedia.org/wiki/Rocketdyne_F-1)
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*, which
  carries the A-1 stage worked example this directory should eventually be checked against
