[Home](../../README.md) > Validation References

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

## IAPWS-95, through REFPROP and CoolProp

- **Source:** IAPWS-95 formulation for the thermodynamic properties of water, implemented independently in NIST REFPROP and in CoolProp
- **Accessed:** Standing reference, called at runtime
- **Validation level:** Hardware. The backend is an independent implementation of measured equations of state
- **Relevance:** This domain started ahead of every other in the repository, because it has been calling an external property library since the beginning. The check is that the repository calls it correctly, not that the equation of state is right.
- **Key findings:**
  - Water at 293.15 K and 101 325 Pa has a density of 998.2 kg/m^3
  - The repository dispatches to REFPROP where installed and falls back to CoolProp, and the two agree closely for pure fluids
  - **This is the only domain whose properties were externally anchored before the validation directory existed**, which is why it is last in the retrofit order rather than first

## Joukowsky, water hammer

- **Source:** Joukowsky 1898, and every water hammer text since
- **Accessed:** Standing reference
- **Validation level:** Standard. An exact closed form
- **Relevance:** Bounds every surge calculation in the domain. A tool that exceeds it has an error rather than a conservative answer.
- **Key findings:**
  - `dP = rho a dV` for instantaneous valve closure
  - Exact for instantaneous closure and an upper bound for any real closure time
  - For water at 998.2 kg/m^3, a wave speed of 1200 m/s and a 3 m/s velocity change, the surge is 3.59 MPa
