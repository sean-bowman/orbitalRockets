[Home](../README.md) > Validation References

# Validation References

The external sources this domain's tools are checked against, and the several things they cannot check.

Kept separate from the reference lists at the foot of each document. Those are further reading; this is the material a test asserts against. The methodology is in [validation/README.md](../../validation/README.md).

| Level | Means |
|---|---|
| **Hardware** | Compared against measured or specified performance of real hardware |
| **Standard** | Reproduces a published standard exactly. Catches an implementation error only |
| **Bounded** | No direct comparison, but the result is bracketed by something |
| **Unvalidated** | No external anchor. Recorded with what depends on it |

**This domain has one strong source and no hardware comparison at all**, which is unusual here and is worth saying at the top. What it does have is a standard read in full rather than in summary, and that turned out to matter more than a hardware case would have.

---

## NASA-STD-5017B

- **Source:** NASA-STD-5017B, *Design and Development Requirements for Mechanisms*, approved 06 December 2022
- **URL:** <https://ntrs.nasa.gov/api/citations/20220014671>
- **Accessed:** 09 August 2026, read from the standard PDF
- **Validation level:** Standard
- **Relevance:** The margin equation, its safety factors, its threshold and most of its requirements are implemented directly from it.
- **Key findings:**
  - Equation 4-1: `margin = T_avail / (sum FSf Tf + sum FSv Tv + sum FSa Ta) - 1`
  - Table 1 factors, from 3.00/1.50/1.25 at analysis to 2.00/1.25/1.10 at flight-article test at extremes, and 1.00 across the board for a one-spring-out case
  - **A margin greater than or equal to zero indicates the requirements are met**, because the reserve is inside the factors
  - Setting the factors to unity represents the torque at which no reserve is available
  - Table 3 bearing Hertzian contact allowables, 440C at 2310 MPa quiet and 2760 non-quiet, through M62 at 3790 and 4070
  - Torque margin does **not** apply where a specific rather than minimum value is required, and the standard names an ejection mechanism requiring a specific separation velocity
  - Holding torque margin uses **intentional** holding torque only, excluding joint friction, harness bending and blanket rubbing

**What it validates.** Every factor, the equation, the threshold, the bearing allowables, and the scope boundary that keeps [SeparationSystem](SeparationSystems.md) out of the margin business.

**What it does not validate.** Any of the physics. It is a requirements document, so it says what a margin must be and not what a friction coefficient is.

---

## The correction

This entry exists because it is the most useful thing that happened while building this domain.

A web search summary of NASA-STD-5017B reported the required operating torque margin as **1.0 or greater**. The standard itself states that a margin **greater than or equal to zero** indicates the requirements are met.

**Building on the summary would have made every mechanism in this library look twice as marginal as it is**, and would have driven hardware changes to correct a problem that does not exist.

The general lesson is worth extracting. A summary of a standard is a secondary source about a document that **exists and is obtainable**, which is a far weaker position than a summary of an experiment that would take a laboratory to repeat. Where the primary source can be read, reading it is not diligence, it is the cheapest available correctness.

A test asserts the threshold is zero and that the correction note survives in the register.

---

## Closed forms

- **Validation level:** Standard, and exact
- **Key findings:**
  - Spring energy, `E = 0.5 k x^2`, reproduces its definition
  - Separation velocity conserves momentum: the mass-times-velocity products of the two bodies agree to machine precision
  - The velocity ratio equals the inverse mass ratio exactly
  - The wedge relation `P = 2 pi T / tan(alpha)` reproduces its own definition, and a shallower wedge amplifies more
  - The initiator circuit is Ohm's law
  - The deployment integration agrees with the undamped closed form to two per cent
  - Latch impact energy tracks the square of arrival rate to machine precision

**Two of those caught real defects.** The momentum and impulse checks exposed a per-spring impulse that had been computed as though each spring acted alone on the whole separating mass, overstating it by the square root of the spring count. And the invariance checks exposed a claim, since corrected, that a stronger spring leaves tipoff unchanged.

---

## What is not validated

Three entries in [validation/referenceCases.py](../../validation/referenceCases.py) under `UNVALIDATED`.

**The pyroshock magnitude** (`pyroshockMagnitude`). **Not computed at all.** Pyroshock prediction is test-derived and no analytic model in the open literature predicts it to better than an order of magnitude. [ClampBand](SeparationSystems.md) computes the released strain energy and stops, because a shock response spectrum from this library would carry more authority than it earns.

**The preload relaxation fractions** (`preloadRelaxation`). Representative rather than measured, and real relaxation depends on surface finish, coating, contact pressure and temperature history. Every retained preload scales with them. The conclusions do not: that the losses compound, that storage is the term nobody plans for, and that margin must be carried against the relaxed preload all hold for any non-zero values. **This is the most tractable gap in the domain**: preload retention testing on a representative joint is standard bolted-joint work.

**The spring rate tolerance** (`springRateTolerance`), and the independence assumption in the statistical tipoff model. Ten per cent is a common commercial tolerance and not a measurement of any supply. Both structural results, that the deterministic bound is flat in spring count and the statistical case falls as one over its root, are independent of the value. **The independence assumption is the weaker of the two** and the domain says so: springs from a single production lot are correlated, so a set bought together and installed unmeasured has bought the statistical case on paper and specified the worst one in reality.

---

## The shape of what is here

Worth naming because it differs from every other domain in this repository.

**There is no hardware case.** Not because none exists, but because mechanism performance data is programme-specific and rarely published: nobody publishes their clamp band preload retention or their measured tipoff rate.

So the validation strategy is different. **The requirements are anchored hard, in a standard read in full. The physics is anchored in closed forms and conservation laws. And the empirical inputs are all registered as unvalidated with what depends on them.**

That is a reasonable position for a domain where the hardware is simple and the confidence is expensive, and it is stated here rather than left to be inferred.
