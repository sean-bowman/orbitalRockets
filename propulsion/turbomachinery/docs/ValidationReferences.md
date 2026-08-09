[Home](../README.md) > Validation References

# Validation References

The external sources this sub-domain's tools are checked against, with what each one was used for and what was taken from it.

Kept separate from the reference lists at the foot of each document. Those are further reading; this is the material a test asserts against, and a source here cannot be changed without a test changing with it. The methodology is in [validation/README.md](../../../validation/README.md).

| Level | Means |
|---|---|
| **Hardware** | Compared against measured or specified performance of real hardware. Can catch a wrong model |
| **Standard** | Reproduces a published formula or tabulated level exactly. Catches an implementation error only |
| **Unvalidated** | No external anchor. Recorded with what depends on it |

---

## RS-25 turbopump specifications

- **URL:** <https://en.wikipedia.org/wiki/RS-25> and the NASA SSME orientation training material it cites
- **Accessed:** 09 August 2026
- **Validation level:** Hardware
- **Relevance:** The best documented turbopumps in the open literature, and unusually they publish shaft speed **and** shaft power together. Those two between them close the loop on a pump model in a way a geometry alone cannot.
- **Key findings:**
  - High pressure fuel turbopump: 35 360 rpm, 69 000 hp (51.45 MW), three stages, discharge around 41 MPa
  - High pressure oxidiser turbopump: 36 000 rpm, 25 000 hp (18.64 MW)
  - Low pressure fuel turbopump: 5150 rpm, boosting LH2 from 0.2 to 1.9 MPa, and it is an **axial** machine
  - The two high pressure pumps are on separate shafts and still run within two per cent of each other
  - **At the published three stages this library predicts 56.0 MW against 51.45, an error of +9 per cent.** Good agreement for a first order model, and conservative
  - **At one stage it predicts 77.3 MW, an error of +50 per cent.** The model is not wrong; it is sensitive to an input that is easy to omit
  - The implied real HPFTP efficiency is 82 per cent against the library's 75 at three stages, so the correlation is seven points conservative on a best-in-class machine

---

## The stage count is the finding

Worth separating out, because it is the practical result rather than the headline number.

Each stage of a multi-stage pump runs at a much higher specific speed than the machine as a whole: specific speed goes as `H^-0.75`, so splitting the head across `n` stages multiplies the per-stage value by `n^0.75`. Efficiency follows the per-stage value.

**A pump model handed an overall specific speed and no stage count reports a plausible and badly pessimistic efficiency, and nothing in the answer looks wrong.** That is the failure mode a user will actually hit, and a test exists for it specifically.

| Stages assumed | Predicted [MW] | Error against 51.45 MW |
|---|---|---|
| 1 | 77.3 | +50 % |
| 2 | 61.6 | +20 % |
| **3, as published** | **56.0** | **+9 %** |
| 4 | 53.2 | +3 % |

---

## Where the model does not apply

- **Source:** RS-25 low pressure fuel turbopump, as above
- **Validation level:** Hardware, retained as a boundary case
- **Relevance:** Kept in the reference set precisely because the library **disagrees** with it, for a reason that is about rocket practice rather than the model being broken.
- **Key findings:**
  - The LPFTP runs at a dimensionless specific speed of about 0.285
  - The classical industrial geometry chart says radial at that value
  - The real machine is **axial**
  - A rocket boost pump is axial because it is chosen for cavitation performance, and an axial inducer stage tolerates far more vapour than a radial impeller
  - A test asserts the disagreement, so that nobody later adjusts the geometry bands to match a machine they were never meant to describe

---

## What is not validated

Three model parameters are estimates rather than data, and all three are labelled where they are used.

**The pump efficiency correlation.** A fit to the specific speed range rocket pumps operate in, roughly 0.2 to 0.4 dimensionless, rather than a fit to data. The RS-25 comparison shows it is seven points conservative on a best-in-class machine, which is a useful bound and not a validation. It ranks; it does not predict.

**The turbine mechanical loss factor.** 0.85, covering tip leakage, disc friction, partial admission scavenging and exit kinetic energy. No source was found for it.

**The thermodynamic suppression factors.** An approximation of a genuinely complicated effect, expressed as a multiplier on tolerable suction specific speed.

Three further assumptions live in the worked example's asset rather than in the library, because the conclusion moves with them: the tank pressure vessel scaling, the turbopump mass correlation, and the fraction of dumped propellant charged as lost. **The factor of two between the open and closed cycle optima is robust to all three, because it comes from one term being present or absent rather than from its size.** The absolute masses are not, and no test asserts them.
