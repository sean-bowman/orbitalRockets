[Home](../README.md) > Validation References

# Validation References

The external sources this domain's tools are checked against, with what each one was used for and
what was taken from it.

Kept separate from the reference lists at the foot of each document. Those are further reading; this
is the material that a test asserts against, and a source here cannot be changed without a test
changing with it. The methodology is in [validation/README.md](../../validation/README.md).

**Validation level** is recorded against each entry, because not every check is the same strength.

| Level | Means |
|---|---|
| **Hardware** | Compared against measured or specified performance of real hardware. Can catch a wrong model |
| **Standard** | Reproduces a published formula or tabulated level exactly. Catches an implementation error only |
| **Unvalidated** | No external anchor. Recorded with what depends on it |

---

## CODATA 2018 and the 2019 SI redefinition, Stefan-Boltzmann constant

- **Source:** CODATA 2018 recommended values, exact by the 2019 SI revision
- **Accessed:** Standing reference
- **Validation level:** Hardware. Exact by definition
- **Relevance:** Every radiation calculation in the domain rests on it, and since 2019 it is exact rather than measured, so an implementation that disagrees is wrong rather than approximate.
- **Key findings:**
  - `sigma` = 5.670374419e-08 W/m^2 K^4, exact
  - The library matches to within 1e-12 relative
  - There is no tolerance to argue about, which makes this the one check in the repository with no judgement in it

## ASTM E490, solar spectral irradiance and the solar constant

- **Source:** ASTM E490 standard solar constant and zero air mass solar spectral irradiance
- **Accessed:** Standing reference
- **Validation level:** Hardware. A measured quantity
- **Relevance:** Sets the absolute scale of every on-orbit thermal case. The equilibrium temperature of a coated surface follows from it and the optical properties together.
- **Key findings:**
  - Total solar irradiance at 1 AU is 1361 W/m^2
  - It varies by about 0.1 per cent over a solar cycle, far below anything this repository resolves
  - A flat plate normal to the sun with no other load equilibrates at `(alpha/eps x G / sigma)^0.25`

## NASA-HDBK-2001, Spacecraft Thermal Control Handbook, optical properties

- **Source:** NASA-HDBK-2001, optical property tables
- **Accessed:** Standing reference
- **Validation level:** Standard. Tabulated properties rather than measurements taken here
- **Relevance:** The `SURFACE_PROPERTIES` table drives every equilibrium temperature and every radiator sizing in the domain. Checking one entry against the handbook and closing the fourth-power balance validates the table and the radiation implementation together.
- **Key findings:**
  - White paint: absorptivity 0.20, emissivity 0.88, giving an equilibrium of 271.8 K normal to the sun
  - Bare aluminium: absorptivity 0.15, emissivity 0.05
  - **Bare aluminium absorbs less sunlight than white paint and runs 246 K hotter**, because it cannot emit what it takes in. This is the most misread result in spacecraft thermal control and it follows directly from the tabulated pair
  - The library reproduces the white paint equilibrium to within 1 K
