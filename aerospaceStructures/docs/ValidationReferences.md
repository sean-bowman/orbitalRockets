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

- **Source:** NASA/SP-8007-2020/REV 2, December 2020. The current revision, read in place of the 1968 original
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

**The magnitude of the correlation's conservatism.** Reading the 2020 revision changed what can be said here, and it is worth separating the two halves.

**The direction is now sourced.** Rev 2 states that the knockdown equation is likely to bound what is expected in the design of aerospace-quality cylinders with well-controlled manufacturing, and that testing has shown buckling loads higher than the lower bound design curve. That is a published statement about how hardware behaves relative to the curve, and it is what makes the factor safe to use without being accurate.

**The magnitude is not.** Knowing the curve is a lower bound is not knowing how far below the data it sits, and Rev 2 does not reproduce the test scatter in a form that can be re-fitted. That remains the difference between this entry and a hardware-level one.

**And the formula is unchanged after fifty two years**, which is a stronger statement than the 1968 document could make on its own: a curve that survives a full revision by the organisation that owns it has been re-examined rather than merely inherited.

**Next step:** the shell buckling test databases compiled since 1968, which would let the conservatism be measured rather than known only by direction.

## What reading the current revision corrected

Four things, and three of them were in the unconservative direction.

**The R/t bound was wrong by a factor of two.** Rev 2 writes the knockdown parameter for `r/t < 1500` and the library allowed 3000, with an error message asserting that 3000 was the fitted range.

**The L/r caution was absent.** Rev 2 states the correlation is unverified by experiment above `L/r = 5`, and separately that the classical prediction becomes unconservative at large `L/r` because it cannot see shell-column interaction. Neither appeared anywhere in the domain.

**The torsion correlation was 0.80 against the document's 0.67**, applied to the same classical expression, which is 19 per cent unconservative on every torsional check.

**The external pressure correlation was a single 0.90 against the document's two.** Rev 2 gives 0.90 for the long two-lobe oval mode and 0.5625 for shorter shells that buckle into more circumferential waves. Every short shell was sized 1.6 times unconservative.

**None of the four was caught by 111 passing tests**, because none of the four constants was asserted against anything. They are now.
