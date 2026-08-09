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

## RS-25 engine specifications

- **URL:** <https://en.wikipedia.org/wiki/RS-25>
- **Accessed:** 08 August 2026
- **Validation level:** Hardware
- **Relevance:** The cleanest available validation case for the performance library. RS-25 is a staged combustion engine, so it is closed cycle, so its published specific impulse is very nearly a thrust chamber figure rather than a whole-engine one. That is what makes it comparable against a library that models the chamber and the nozzle and not the cycle.
- **Key findings:**
  - Vacuum thrust 2279 kN, sea level thrust 1860 kN
  - Vacuum specific impulse 452.3 s, sea level 366 s
  - Chamber pressure 20.64 MPa, expansion ratio 78:1, mixture ratio 6.03:1
  - Throat diameter 0.26 m
  - The library's ideal calculation gives 459.8 s vacuum, an overprediction of 1.7 per cent, which is the correct direction for a calculation carrying no losses
  - The implied combined efficiency of 0.984 is above the library's 0.941 default, so the defaults are conservative for a best-in-class engine

## Rocketdyne F-1 engine specifications

- **URL:** <https://en.wikipedia.org/wiki/Rocketdyne_F-1>
- **Accessed:** 08 August 2026
- **Validation level:** Hardware, retained as a boundary case
- **Relevance:** Kept in the reference set precisely because it does **not** validate the library. F-1 is a gas generator engine, so its published impulse includes turbine exhaust dumped overboard, which is a cycle loss the thrust chamber library does not model. It marks the edge of what the tools cover.
- **Key findings:**
  - Sea level thrust 6770 kN, chamber pressure 7.0 MPa, expansion ratio 16:1, mixture ratio 2.27:1
  - Vacuum specific impulse 304 s, sea level 263 s
  - The library overpredicts vacuum impulse by 8.1 per cent, against 1.7 per cent for the closed cycle case
  - The implied efficiency of 0.925 is a chamber efficiency multiplied by a cycle penalty and the two cannot be separated without the turbine flow fraction
  - A test asserts that this case continues to disagree. Tuning an efficiency until it agreed would fit a cycle loss into a nozzle coefficient

---

## What is not validated

Recorded in full in `validation/referenceCases.py` under `UNVALIDATED`.

**Chamber heat load** is the significant one. See [combustionDevices](../combustionDevices/docs/ValidationReferences.md).
