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

## GSFC-STD-7000A, General Environmental Verification Standard (GEVS)

- **URL:** <https://experiorlabs.com/wp-content/uploads/2019/10/GSFC-STD-7000A-General-Environmental-Verification-Standard-GEVS-for-GSFC-Flight-Programs-and-Projects-4-22-2013.pdf>
- **Accessed:** 08 August 2026
- **Validation level:** Hardware. A real qualification level that flight hardware has been tested to
- **Relevance:** GEVS is unusually good validation material because it publishes both a spectrum and the Grms that spectrum integrates to. The Grms is an independent check on the spectrum, so a tool that computes one from the other sits inside a closed loop.
- **Key findings:**
  - Generalised random vibration, qualification, components of 22.7 kg or less: 0.026 g^2/Hz at 20 Hz, rising at +6 dB/octave to a 0.16 g^2/Hz plateau from 50 to 800 Hz, falling at -6 dB/octave to 0.026 g^2/Hz at 2000 Hz
  - Published overall level 14.1 Grms
  - The library integrates the published breakpoints to **14.14 Grms**, agreeing to 0.3 per cent
  - The table is self-consistent: a +6 dB/octave slope from 0.026 at 20 Hz reaches 0.026 x (50/20)^2 = 0.1625 at 50 Hz, matching the tabulated plateau
  - Acceptance is qualification less 3 dB, which is a factor of sqrt(2) in Grms. The library gives 10.00 Grms against a published 10.0

## Secondary sources on GEVS levels, and a contradiction they created

- **URL:** <https://vibrationresearch.com/blog/wmu-cubesat-qualification-testing/> and related search results
- **Accessed:** 08 August 2026
- **Validation level:** Not used as a reference. Recorded because resolving it was itself a validation
- **Relevance:** Two secondary sources gave apparently contradictory levels. Resolving the contradiction with the repository's own tool turned out to be a better check than either source alone.
- **Key findings:**
  - One source quoted a 0.16 g^2/Hz plateau at 14.1 Grms; another quoted 0.016 g^2/Hz at 10.0 Grms
  - Integrating the first gives 14.14 Grms, which matches its stated overall
  - Integrating the second gives 6.18 Grms, which does not match its stated 10.0
  - The 10.0 figure is the **acceptance** level of the first spectrum, qualification less 3 dB, which is 14.14 / sqrt(2) = 10.00
  - Both sources were right about different things and neither said which. **A secondary source quoting a Grms without its spectrum, or a spectrum without its Grms, cannot be checked**
