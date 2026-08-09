[Home](../README.md) > Validation References

# Validation References

The external sources this domain's tools are checked against, with what each one was used for and
what was taken from it.

Kept separate from the reference lists at the foot of each document. Those are further reading; this
is the material that a test asserts against, and a source here cannot be changed without a test
changing with it. The methodology is in [validation/README.md](../../../validation/README.md).

**Validation level** is recorded against each entry, because not every check is the same strength.

| Level | Means |
|---|---|
| **Hardware** | Compared against measured or specified performance of real hardware. Can catch a wrong model |
| **Standard** | Reproduces a published formula or tabulated level exactly. Catches an implementation error only |
| **Unvalidated** | No external anchor. Recorded with what depends on it |

---

## Bartz correlation, and the literature comparing it against test data

- **URL:** <https://ntrs.nasa.gov/api/citations/19710011726/downloads/19710011726.pdf>
- **Accessed:** 08 August 2026
- **Validation level:** Bounding only. The correlation's accuracy band is used as a ceiling on any claim made downstream of it
- **Relevance:** The gas-side heat transfer coefficient in this sub-domain is Bartz, and every cooling conclusion rests on it. What was sought was the accuracy band, so that no result downstream could claim to be better than the correlation underneath it.
- **Key findings:**
  - Bartz is quoted at plus or minus twenty per cent at best, and worse in the convergent section
  - The literature consistently reports that the one-dimensional Bartz calculation **overestimates** inner wall temperature, because it does not account for boundary layer thickness variation along the wall
  - Modified forms with a correction factor agree better near the injector face
  - Predictions are more reliable in oxidiser-rich conditions
  - Consequence for this repository: a cooling design that closes on a ten per cent margin against Bartz has not closed, and the classes say so in their findings

## RS-25 regenerative cooling configuration

- **URL:** <https://en.wikipedia.org/wiki/RS-25>
- **Accessed:** 08 August 2026
- **Validation level:** Unvalidated. Searched and did not yield the quantity needed
- **Relevance:** Sought to close the energy balance on a real regeneratively cooled chamber, which would have validated the Bartz heat load integration. It does not carry the numbers required.
- **Key findings:**
  - Around 390 channels are machined into the liner wall to carry liquid hydrogen
  - Chamber temperature approaching 3600 K at pressures up to 23 MPa
  - The coolant path is described but neither the heat load nor the coolant temperature rise is given
  - **The search did not produce a validation case.** Published engine data commonly gives coolant flow and channel counts and rarely the heat load

## Measured throat heat flux, open literature survey

- **URL:** <https://www.sciencedirect.com/science/article/pii/S0094576521001417> and the accompanying dataset at <https://www.sciencedirect.com/science/article/pii/S2352340921004571>
- **Accessed:** 08 August 2026
- **Validation level:** Hardware, but bounding only. A range rather than a case to reproduce
- **Relevance:** The nearest anchor found for the heat transfer side. It cannot validate the integrated heat load, which is what actually matters here, but it can bound the peak throat flux the integration is built on.
- **Key findings:**
  - Pizzarelli et al. survey roughly 500 experimental points on throat heat transfer from hot-fire tests
  - Individual reported values surfaced alongside it: 54 MW/m^2 at the throat at 41.4 bar and a mixture ratio of 6.0, and 18 MW/m^2 as a maximum in another campaign
  - The library computes 52.1 MW/m^2 for the reference engine, which sits **inside** that band and at 95 per cent of the way up it
  - Sitting near the top is consistent with the documented tendency of Bartz to overpredict
  - **The limit of this check:** the band spans a factor of three across different propellants, scales and pressures. It would catch an order-of-magnitude error and would not catch the factor of three that made this directory necessary
  - The full dataset was not retrievable, so this is a range rather than a distribution

---

## What is not validated

Three entries, and the first drives a conclusion.

**Chamber heat load.** The 8.13 MW computed for the reference engine is a Bartz result, not a validated one. It replaced a propulsion hub placeholder that was lower by a factor of three. One independent argument supports the direction of the correction: the placeholder used jet power, 135.8 MW, as its base where thermal power, 228.8 MW, is the physically meaningful one. Even corrected, two per cent of thermal power gives 4.58 MW against Bartz's 8.13, so the fraction was optimistic as well as measured against the wrong quantity. Neither number has an external anchor.

**Next step:** the Huzel and Huang A-1 stage worked example, which carries a full cooling calculation for a 750 000 lbf LOX/RP-1 engine and would close the loop.

**Injector mixing quality.** A ranking rather than a measurement. Used only to order element types and it must not be used to predict c* efficiency.

**Coolant limits.** The RP-1 coking limit of 575 K drives the conclusion that the reference engine cannot be regeneratively cooled. That is a widely quoted range rather than a sourced value, and the real limit is a film temperature depending on residence time and surface chemistry. The conclusion is sensitive to it.
