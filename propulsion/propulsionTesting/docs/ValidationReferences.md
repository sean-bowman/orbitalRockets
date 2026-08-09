[Home](../README.md) > Validation References

# Validation References

The external sources this sub-domain's tools are checked against, and the several things they cannot check.

Kept separate from the reference lists at the foot of each document. Those are further reading; this is the material a test asserts against. The methodology is in [validation/README.md](../../../validation/README.md).

| Level | Means |
|---|---|
| **Hardware** | Compared against measured or specified performance of real hardware |
| **Standard** | Reproduces a published formula or measurement exactly. Catches an implementation error only |
| **Bounded** | No direct comparison, but the result is bracketed by something |
| **Unvalidated** | No external anchor. Recorded with what depends on it |

**This sub-domain's strongest results are algebra rather than measurements**, which is unusual here and worth saying at the top. The correlation trap in [DataReduction](DataReduction.md) is exact: it needs no reference because it is an identity, and no plausible set of instrument uncertainties changes it. What is weakly anchored is every absolute uncertainty figure, and those are registered below.

---

## The pulse gun development programme

- **Source:** Osborne, Hulka, McCay, Casiano and Dumbacher, *Development and Testing of Pulse Guns for Combustion Instability Testing*, AIAA Propulsion and Energy Forum and Exposition, 2021, NASA Marshall Space Flight Center
- **URL:** <https://ntrs.nasa.gov/api/citations/20210017842>
- **Accessed:** 09 August 2026
- **Validation level:** Hardware
- **Relevance:** The only sourced numbers in this sub-domain's stability rating model, and the source of the flux multiplier that explains why the test is run at all.
- **Key findings:**
  - 44 tests, firing into a chamber pressurised to **2300 psig** with gaseous nitrogen
  - Best configuration: a 0.40 inch inner diameter breech, 15 to 16 grains of gunpowder wrapped in cigarette paper, a 24,000 psid burst disk
  - **Zero-to-peak overpressures of 37 to 58 per cent of the mean chamber pressure**, stated to be adequate for typical combustion stability rating
  - For chambers **probably exceeding about 12 inches in diameter, a pulse gun may be unable to produce an adequate response**, necessitating a bomb
  - Under high frequency instability, **heat flux near the injector face can increase by a factor of 5 to 10 and can double at the throat**
  - Two device types are used for dynamic stability rating: nondirectional bombs and pulse guns. Bombs were used most on the Apollo era engines, Atlas, H-1 and F-1, and have since become expensive and demanding to procure, transport and handle
  - The CPIA combustion stability guidelines were first published in **1971**, and the current revision was, as of 2021, nearly 25 years old and being updated

**What it validates.** The perturbation floor of 37 per cent, the pulse gun diameter limit, and the flux multipliers. All three are used directly and all three carry the citation.

**What it does not validate.** The pass criterion. See the gap below.

**The cross-domain consequence is the important part.** [combustionDevices](../../combustionDevices/docs/RegenerativeCooling.md) computes a cooling circuit that does not close with comfortable margin at nominal flux. At five to ten times nominal near the injector face there is no circuit at all. **That is why stability is a hardware survival requirement rather than a performance one**, and it is a sourced statement rather than an assertion.

---

## The uncertainty propagation rule

- **Source:** ISO/IEC Guide 98-3, the *Guide to the expression of uncertainty in measurement*, for the propagation of uncertainty through a function of measured quantities
- **Validation level:** Standard
- **Relevance:** Every uncertainty this sub-domain reports.
- **Key findings:**
  - For a product of powers, the relative combined uncertainty is the root sum of squares of the relative input uncertainties weighted by the exponents
  - All the exponents in c*, Cf and Isp are plus or minus one, so the weights are one and the signs drop out in the squaring
  - **The rule applies to independent inputs.** c* and Cf are not independent, and that is the whole of the next section

---

## The correlation identity, which needs no reference

- **Validation level:** Exact. It is algebra
- **Key finding:** `c* * Cf = (Pc At / mdot) * (F / (Pc At)) = F / mdot`, identically

Chamber pressure and throat area cancel completely. Specific impulse computed as the product carries no chamber pressure or throat area uncertainty at all, and combining the two parameters' uncertainties as independent double-counts both shared terms.

On the reference booster that inflates the specific impulse uncertainty by **1.61 times**, and the inflation factor is `sqrt(1 + 2(u_Pc^2 + u_At^2)/(u_F^2 + u_mdot^2))`, which is above one for any non-zero pressure or area uncertainty.

**No instrument figures change the conclusion**, only its size. That makes it the strongest result in this sub-domain despite having no external source, which is the opposite of the usual situation in this repository and worth noticing.

---

## Cross-domain consistency

- **Validation level:** Internal, and it is a consistency check rather than a validation
- **Key findings:**
  - The reduced specific impulse, 277.02 s, reproduces the propulsion hub's 277.0 s design point, because the reduction is being handed the hub's own design channels
  - The reduced c* efficiency, 0.9607, reproduces the hub's assumed 0.96
  - The first tangential frequency uses the same eigenvalue, 1.8412, that [combustionDevices](../../combustionDevices/docs/CombustionStability.md) uses

**The first two of those are circular and are labelled as such.** The example is handed the hub's design point as if it were recorded data, because inventing plausible stand data would be worse. What the example demonstrates is the uncertainty attached to a reduction, not the reduction, and it says so.

---

## What is not validated

Three entries in [validation/referenceCases.py](../../../validation/referenceCases.py) under `UNVALIDATED`.

**The instrument uncertainties** (`instrumentUncertainty`). Representative of good practice rather than taken from any calibration certificate. Every uncertainty reported scales with them. The two conclusions drawn do not: the correlation identity is exact, and the finding that a one per cent effect is unresolvable while a four per cent effect is marginal holds for any plausible set of channel figures.

**The stability damp criterion** (`stabilityDampCriterion`). **Not carried, and not performed.** The CPIA guidelines specify how quickly a perturbation must decay for an engine to be rated stable. They are not openly available and the criterion has not been read, so `checkStabilityRating()` reports the perturbation adequacy and the device viability and deliberately does not report a pass or a fail. Stating a damp time from memory would put an unsourced number into the one part of this repository whose purpose is to prevent exactly that.

**The settling times** (`testSettlingTimes`). Representative time constants rather than measured ones. The usable thermal window scales with the wall constant. The conclusion drawn is that the two settling times differ by three orders of magnitude, which is robust to any plausible value, and the next step is tractable: compute the wall constant from the [thermalManagement](../../../thermalManagement/) lumped capacitance model for the actual chamber.

---

## The tacit half

Recorded because the objectives for this sub-domain named it explicitly and because leaving it out would misrepresent what has been built.

Test engineering has a large body of knowledge that is not written down here and is not derivable from anything that is: which channel on a given stand has a history, what a firing sounds like when it is about to go wrong, how long to wait before entering the cell, what post-test inspection finds that data reduction never will.

**What this sub-domain contains is the transferable arithmetic around that knowledge, not the knowledge.** The documents say so in their own failure mode sections rather than implying completeness.
