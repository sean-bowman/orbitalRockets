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

## RS-25, the pressure ladder

- **URL:** <https://en.wikipedia.org/wiki/RS-25> and the NASA SSME orientation training material it cites
- **Accessed:** 09 August 2026
- **Validation level:** Hardware
- **Relevance:** RS-25 is staged combustion and publishes both its chamber pressure and its high pressure fuel turbopump discharge pressure, which is exactly the pair the pressure ladder predicts.
- **Key findings:**
  - Chamber pressure 20.64 MPa, high pressure fuel turbopump discharge roughly 41 MPa
  - The real discharge ratio is **1.99**
  - The library predicts 45.4 MPa, a ratio of 2.20, which is **11 per cent high and conservative**
  - Conservative is the right direction for a pressure ladder: it oversizes the pump rather than leaving it short
  - The structural claim that a closed cycle pump runs at roughly twice chamber pressure is therefore confirmed by hardware rather than only by the library's own constants

---

## RL10, the expander ceiling

- **Source:** RL10 published chamber pressure, 4.4 MPa
- **Accessed:** Standing reference, cross-checked against the turbomachinery search of 09 August 2026
- **Validation level:** Hardware, as a bracket rather than a point comparison
- **Relevance:** The expander heat balance produces a chamber pressure ceiling, and the question is whether that ceiling lands anywhere near where expander cycle engines actually operate.
- **Key findings:**
  - The library's sweep puts the ceiling between **4.0 and 4.5 MPa** for the reference engine
  - RL10 runs at **4.4 MPa**, inside that bracket
  - The agreement is closer than the model deserves and is a sanity bracket rather than a validation: the reference engine is LOX/RP-1 and RL10 runs on hydrogen, which has a far higher coolant specific heat and no coking limit
  - What it does establish is that the ceiling is real, that it is low, and that it sits where expander cycle engines sit. A model putting it at 1 MPa or 40 MPa would be telling us nothing useful
  - The computed scaling exponent is **1.3** against the **1.2** the dimensional argument predicts

---

## F-1, the open cycle penalty

- **URL:** <https://en.wikipedia.org/wiki/Rocketdyne_F-1>
- **Accessed:** 08 August 2026, carried forward from the propulsion hub validation
- **Validation level:** Hardware, partial
- **Relevance:** The propulsion hub library models a thrust chamber and overpredicts F-1's published vacuum impulse by 8.1 per cent while matching RS-25 to 1.7. F-1 is a gas generator engine, so part of that gap should be the cycle penalty this sub-domain computes.
- **Key findings:**
  - The cycle penalty at a 3 per cent driving flow is roughly 2 per cent
  - The hub disagreement is 8.1 per cent
  - **The penalty accounts for a meaningful part of the gap and not all of it**, and the test bounds it rather than asserting equality
  - The remainder is chamber efficiency, which is a different quantity, and conflating the two would let a cycle loss be absorbed into an injector efficiency

---

## What is not validated

**The turbine pressure ratios.** The values of 20 for an open cycle and 1.5 for a closed one are representative rather than sourced per engine. They set the expansion term, which is the factor of six between the cycle families, so the qualitative conclusion is robust and the exact flow fractions are not.

**The dumped exhaust impulse fraction.** Thirty per cent of main chamber impulse is a commonly quoted figure with no single source found. The gas generator penalty scales with it directly.

**The driving gas properties.** A single specific heat and gamma are used for all cycles, which understates a hydrogen rich preburner and overstates a hydrocarbon one. The staged combustion driving flow fraction is low for this reason and the document says so.

**The pressure ladder drop fractions.** Injector at 20 per cent, cooling at 15, lines at 5 and preburner injector at 20 are representative. The RS-25 comparison bounds their sum at 11 per cent conservative, which is the useful check on them.

**The tank mass model** used for the pressure fed comparison, shared with the turbomachinery worked example. The factor of forty eight against a pumped tank comes from the pressure ratio rather than from the model, so the elimination is robust to it.
