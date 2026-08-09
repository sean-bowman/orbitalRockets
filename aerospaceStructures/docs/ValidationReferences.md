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

## NASA SP-8007, Buckling of Thin-Walled Circular Cylinders

- **Source:** NASA SP-8007, 1968 revision. Space Vehicle Design Criteria (Structures)
- **Accessed:** Standing reference, not retrieved during this work
- **Validation level:** Standard. Reproduces the published closed form and cannot validate the correlation itself
- **Relevance:** The shell buckling knockdown is the single most consequential empirical factor in this repository. It converts a classical buckling stress that overpredicts by a factor of four or five into a design value, and more than one domain depends on it.
- **Key findings:**
  - Correlation factor `gamma = 1 - 0.901 (1 - exp(-phi))` with `phi = (1/16) sqrt(R/t)`
  - Computed values: 0.5813 at R/t 100, 0.4042 at 300, 0.3217 at 500, 0.2238 at 1000, 0.1791 at 1500
  - At R/t 1000, an ordinary launch vehicle tank, the classical stress overpredicts by a factor of four and a half
  - The library reproduces all five points to within 1e-4
  - **The limit of this check:** it validates the implementation of a published curve. The test scatter the curve was fitted to is not in the document in a form that can be re-fitted, so the correlation itself remains unvalidated here

---

## What is not validated

**The knockdown correlation itself.** SP-8007 is a lower bound fitted to 1960s test data, it is known to be conservative for modern manufacturing, and there is a substantial literature on replacing it. Nothing in this repository checks it against test data, and a `standard` level check cannot.

**Next step:** the shell buckling test databases compiled since SP-8007, which would allow the correlation to be assessed rather than merely reproduced.
