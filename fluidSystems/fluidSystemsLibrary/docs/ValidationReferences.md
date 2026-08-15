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
  - **This is the only domain whose properties were externally anchored before the validation directory existed**, which is why it was last in the retrofit order rather than first


## Princeton Superpipe, smooth pipe friction

- **Source:** McKeon, Zagarola and Smits, *A new friction factor relationship for fully developed pipe flow*, Journal of Fluid Mechanics 538, 429-443, 2005
- **Accessed:** 13 August 2026, through the reproduction of the relation and its error bounds in Yang and Joseph
- **Validation level:** Hardware. A fit to measurement over 31,000 to 35,500,000 in Reynolds number, not a fit to another correlation
- **Relevance:** The friction factor is the only term in a line pressure drop that is a model rather than a definition, so it is the one worth anchoring. This is what the Moody chart and the Crane friction chart are both approximations to.
- **Key findings:**
  - `1/sqrt(lambda) = 1.930 log10( Re sqrt(lambda) ) - 0.537`, fitting the Princeton data to 1.25 % across its range and 0.5 % over 300,000 to 13,600,000
  - **Every method in this library under-predicts it, and none crosses over anywhere in the range.** Colebrook is 2.9 % low at the top, Churchill 2.1 % and Haaland 2.3 %
  - The shortfall is under one per cent below Re = 100,000 and grows monotonically above it
  - **A low friction factor is a low pressure drop**, so a line sized on one has less margin than its number says
  - At zero roughness the Colebrook equation reduces to the Prandtl smooth pipe law, and the Superpipe work is what moved its constants from 2.0 and 0.8 to 1.930 and 0.537. **The intercept it actually gives is `2 log10(2.51) = 0.799347`**, not the 0.8 that gets quoted: the rounding is in the textbook rather than in the equation

**This is not the anchor the retrofit list called for.** It asked for Crane TP-410 worked examples. TP-410 is not openly available and the search for a reproducible example from it failed, so the anchor became the measurement its friction chart approximates. **That is the better reference of the two:** a TP-410 example would establish that this library implements Colebrook the way Crane does, and the Superpipe fit establishes how far Colebrook is from the pipe.

**What it does not cover:** the roughness branch, which the fit says nothing about, and the fitting loss coefficients, which are a table rather than a model and remain the largest unanchored part of a line pressure drop.

## Hagen-Poiseuille, laminar pipe flow

- **Source:** Closed form for fully developed laminar flow in a circular pipe
- **Accessed:** Standing reference
- **Validation level:** Standard. An exact closed form
- **Relevance:** The only place in this domain where a pressure drop has an exact answer, which makes it the check on the **whole chain** rather than on one term of it.
- **Key findings:**
  - `dP = 128 mu Q L / (pi D^4)`
  - Velocity from mass flow, the Reynolds number, the 64/Re friction factor and the Darcy-Weisbach assembly all have to be right together to reproduce it
  - **A factor of four anywhere, a radius used where a diameter belongs, or a Fanning factor read as a Darcy one all fail this by a wide margin**, which is why it needs no tolerance
  - The library matches to one part in a million, and the residual is the density being re-evaluated along the marched line rather than an error
  - The exponents are asserted as well as the value: fourth power in diameter, first power in length and in flow. A chain that got one case right by luck does not also get the exponents right

## Blasius, the low Reynolds bracket

- **Source:** Blasius 1913, `lambda = 0.3164 Re^-0.25`
- **Accessed:** Standing reference
- **Validation level:** Standard, and a bracket rather than a validation. Blasius is itself a correlation
- **Relevance:** The Superpipe fit starts at Re = 31,000 and a small feed line can sit below it, so the low end needs its own check.
- **Key findings:**
  - The library sits 2.8 % below Blasius at worst over 10,000 to 90,000, and below it almost everywhere
  - **That is the same direction as the Superpipe comparison at the other end of the range**, which is the part worth noticing: the under-prediction is not an artefact of one reference

## Joukowsky, water hammer

- **Source:** Joukowsky 1898, and every water hammer text since
- **Accessed:** Standing reference
- **Validation level:** Standard. An exact closed form
- **Relevance:** Bounds every surge calculation in the domain. A tool that exceeds it has an error rather than a conservative answer.
- **Key findings:**
  - `dP = rho a dV` for instantaneous valve closure
  - Exact for instantaneous closure and an upper bound for any real closure time
  - For water at 998.2 kg/m^3, a wave speed of 1200 m/s and a 3 m/s velocity change, the surge is 3.59 MPa
