[Home](../README.md) > Validation References

# Validation References

The external material this domain's tools are checked against, and what they cannot check.

Kept separate from the reference lists at the foot of each document. Those are further reading; this is the material a test asserts against. The methodology is in [validation/README.md](../../validation/README.md).

| Level | Means |
|---|---|
| **Hardware** | Compared against measured or specified performance of real hardware |
| **Standard** | Reproduces a published standard or definition exactly. Catches an implementation error only |
| **Bounded** | No direct comparison, but the result is bracketed by something |
| **Unvalidated** | No external anchor. Recorded with what depends on it |

**This domain's anchor is the strongest kind available to it and the weakest kind available to a physics domain.** The criteria are not a model of anything: they are the numbers a launch is licensed against, so reproducing them is exact by construction and establishes nothing about whether the analysis feeding them is right.

---

## 14 CFR Part 450

- **Source:** 14 CFR Part 450, sections 450.101 and 450.145, read from the regulation
- **Validation level:** Standard, and exact
- **Relevance:** Every verdict this domain reaches
- **Key findings:**
  - Collective risk, public 1e-4 and neighbouring operations personnel 2e-4 expected casualties
  - Individual risk, public 1e-6 and neighbouring 1e-5 probability of casualty per launch
  - Aircraft, 1e-6 probability of impact with debris capable of causing a casualty
  - Flight safety system design reliability of 0.999 at 95 per cent confidence, onboard and off-vehicle

**All of them are duplicated into [validation/referenceCases.py](../../validation/referenceCases.py) and asserted against the library by a test.** They are separate files on purpose: a library edited without the register is a library that has quietly stopped citing anything.

---

## What reading it settled

**Collective and individual risk are separate tests and both apply.** A launch can meet the collective criterion by spreading a small risk thinly over a large population and still fail the individual one for the person nearest the trajectory. **The individual limit exists to stop exactly that trade**, and in the worked case it is the tighter of the two by a factor of two.

**The neighbouring operations personnel limits are looser by exactly a factor of two on the collective side and ten on the individual side.** That is a policy statement rather than an engineering one, distinguishing people who chose to be there from people who did not, and it is asserted by a test because a table edited later could quietly lose it.

**And the reliability requirement covers the off-vehicle portion.** The ground transmitter chain carries the same number as the hardware on the rocket.

---

## The demonstration arithmetic

- **Validation level:** Standard, and exact
- **Key finding:** `n = ln(1 - C) / ln(R)`, so 0.999 at 95 per cent confidence needs **2,994 successful tests with zero failures**

This is not a reference so much as a consequence, and it is the most useful thing in the domain.

**It cannot be met.** The articles are consumed by the test, a lot of that size would not be the lot that flies, and no programme has ever attempted it. **So the claim is argued from redundancy, parts history, environmental margin and an end-to-end test of the flight article**, and the regulation's own language, commensurate design, analysis and testing, acknowledges as much.

**Each additional nine costs ten times the tests**, asserted by a test, so the arithmetic gets worse rather than better as requirements tighten.

---

## Closed forms

- **Validation level:** Standard, and exact
- **Key findings:**
  - The free-flight solution conserves specific angular momentum and energy, asserted against the state
  - Downrange distance grows faster than linearly with speed, which is why the impact point accelerates
  - The Earth rotation offset equals the rotation rate times the flight time times the radius
  - A circular orbit and an orbit whose perigee clears the surface both have no impact point, and both raise
  - Casualty expectation is exactly linear in the failure probability
  - The dual parallel path reliability is exactly `1 - (1 - r) ** 2`
  - A two-out-of-two configuration is below its own element reliability
  - `n = ln(1 - C) / ln(R)`, checked at a case where it returns exactly one

**The refusal at orbital insertion earns its place.** The absence of an impact point there is a physical fact rather than a numerical failure, and returning a large number instead would misrepresent the end of the range safety flight phase as a very long fall.

---

## What is not validated

Two entries in [validation/referenceCases.py](../../validation/referenceCases.py) under `UNVALIDATED`, and each names what survives it.

**Casualty areas and population densities** (`casualtyAreas`). A real casualty area comes from a fragment mass, velocity and impact angle through a lethality model, and a real population comes from a gridded census rather than a land use class. Every casualty expectation scales linearly with both. **The structural results do not**: that risk follows population rather than impact probability follows from the product form, and that a casualty area exceeds a fragment footprint is a definition. **A gridded population product is public and would close half of this.**

**Impact probabilities and the failure probability** (`impactProbabilities`). A real impact probability comes from propagating a debris catalogue through an atmosphere with a wind field, from every failure time along the trajectory, which is a Monte Carlo rather than a closed form. The failure probability comes from a reliability argument the vehicle does not have yet.

**The failure probability multiplies everything**, which is why the class sweeps it and reports the value at which the criterion stops being met rather than quoting a single number. **The risk analysis inherits the reliability estimate whole**, and that is the weakest number in it.

---

## What is not modelled at all

**Debris catalogues and fragment dispersion.** The largest single piece of unbuilt work implied by this repository. [EntryTrajectory](../../recoveryAndReusability/docs/EntryAerodynamics.md) computes the descent of one body; the missing parts are the catalogue, the imparted velocity, the wind field and the Monte Carlo over failure times.

**Blast overpressure.** Computed in [groundSystemsAndOperations](../../groundSystemsAndOperations/docs/HazardZonesAndSiting.md) from DESR 6055.09 and not duplicated here.

**Toxic dispersion.** Named as not modelled in both domains, for the same reason: it scales with release rate, wind and atmospheric stability rather than with quantity.

**Ordnance initiation margins.** [PyrotechnicInitiator](../../mechanismsAndSeparation/docs/Pyrotechnics.md).

**Autonomous FTS rule sets and their verification.** Mission specific, and the verification is a [software assurance](../../avionicsAndGNC/docs/SoftwareAssurance.md) problem.

**Common cause failure in the FTS redundancy.** The configuration arithmetic here assumes independent paths, which is optimistic. [reliabilityAndMissionAssurance](../../reliabilityAndMissionAssurance/) computes the beta-factor case, and applying it to an FTS would reduce every redundancy gain in this domain.

---

## The shape of what is here

**What this domain concludes about the regulation is exact**, because the regulation is a set of numbers rather than a model.

**What it concludes about trajectories rests on a closed-form Keplerian solution**, and the two structural results, that the impact point accelerates and that it ceases to exist at insertion, follow from the mathematics rather than from any value.

**What it concludes about reliability rests on one line of binomial arithmetic**, and the conclusion, that the requirement cannot be demonstrated by test, is arithmetic rather than opinion.

**And what it reports about risk rests on representative debris and population data**, so the arithmetic is exact and the answer is illustrative. That is stated here rather than implied, and it is the honest position for a domain whose hardest input is a Monte Carlo nobody has run.
