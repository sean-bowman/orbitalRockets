[Home](../README.md) > Cleanliness Verification

# Cleanliness Verification

## Contents

- [Overview](#overview)
- [What is being verified](#what-is-being-verified)
- [Sampling](#sampling)
- [Particulate verification](#particulate-verification)
- [NVR verification](#nvr-verification)
- [Moisture verification](#moisture-verification)
- [Oxygen service](#oxygen-service)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Cleanliness is specified at the system level, achieved at the part level, and verified by sampling. The verification is the weakest link of the three, because a sample is a statement about the area that was sampled and about nothing else.

The requirements and the cleaning processes are in [fluidSystemsLibrary/docs/CleanlinessAndContamination.md](../../fluidSystemsLibrary/docs/CleanlinessAndContamination.md). This document is about proving it.

---

## What is being verified

Three independent things, requiring three independent verifications.

| Property | Failure it prevents | Method |
|---|---|---|
| **Particulate** | Plugged orifices, damaged valve seats, abraded catalyst | Rinse, filter, count |
| **NVR** | Ignition in oxygen, catalyst poisoning, seal degradation | Rinse, evaporate, weigh |
| **Moisture** | Ice, corrosion, acid formation, catalyst poisoning | Dew point |

**Specify and verify all three.** A particulate-only specification says nothing about the hydrocarbon film that will ignite in an oxygen system, and it is the omission that matters most.

A combined specification reads `Level 100A`: particulate to Level 100 and NVR to Level A.

---

## Sampling

**A cleanliness verification is a statement about the sampled area.** This is the fundamental limitation and it drives everything about how sampling is done.

| Decision | Why it matters |
|---|---|
| **Sampled area** | A count without a defined area has no units |
| Rinse volume | Determines the concentration and therefore the detection limit |
| Sample location | The dirtiest location is the one that matters, and it is not random |
| Number of samples | One sample is an anecdote |
| Blank sample | Establishes the contribution of the solvent, the container and the technique |

**Always run a blank.** Rinse a known-clean surface, or the empty container, with the same solvent and the same technique. The blank is subtracted, and if the blank is comparable to the sample the measurement is meaningless.

**Sample where contamination collects**, not where it is convenient: low points, dead legs, upstream of the first restriction, and the inside of anything that was machined.

**Internal surfaces are the problem.** A long, small-bore tube cannot be rinsed representatively by pouring solvent through it, and an additively manufactured passage cannot be sampled at all without cutting it open. For those, the honest verification is a flow test looking for shed particulate, plus destructive examination of a coupon made the same way.

---

## Particulate verification

**Method:** rinse a defined area with filtered solvent, pass the rinse through a membrane filter, count and size the particles under a microscope or with an automatic counter.

**Report the distribution, not just the largest particle.** A Level 100 specification defines a whole log-normal distribution, and a single 90 micron particle with nothing else is a different condition from a distribution that is at the limit everywhere.

**Fibres are counted separately** because they behave differently: a fibre passes a size rating test presented end-on and then lodges across a passage. Most specifications count fibres above a length threshold as a separate category.

**Practical limits:** the method resolves down to roughly 5 micron reliably. Below that, counting is slow and operator-dependent, and an automatic counter is required.

---

## NVR verification

**Method:** rinse a defined area with a solvent of known purity, evaporate the rinse to dryness in a tared vessel, weigh the residue.

**The gravimetric method is straightforward and the failure modes are all procedural:**

- The solvent itself contributes residue, which the blank corrects for
- The evaporation must be complete, and complete is defined by weight stability rather than by time
- Handling the vessel adds fingerprints, which are NVR
- The balance resolution has to be well below the limit, which for a 1 mg limit means a 0.1 mg balance minimum

**Black light inspection** is a fast qualitative screen that catches gross hydrocarbon contamination, because many hydrocarbons fluoresce under UV. It does not replace the gravimetric measurement, because not all hydrocarbons fluoresce and the ones that do not are just as flammable.

**The water break test** is the cheapest useful check: a clean metal surface holds a continuous water film, and a contaminated one breaks it into droplets. It is qualitative, immediate, and it catches the gross case that would otherwise waste a gravimetric measurement.

---

## Moisture verification

**Method:** measure the dew point of the purge gas leaving the article, after purging.

| Requirement | Typical dew point |
|---|---|
| General | -40 degC |
| Cryogenic service | -60 to -70 degC |
| Ultra-high purity | Below -80 degC |

**Sample from the far end of the purge path**, not near the inlet. A sample taken at the inlet reads the purge gas.

**Verify by measurement, not by purge time.** The time to dry depends on geometry, flow rate and dead legs, none of which are reliably known. A flow-through purge of a system with dead legs reads dry at the vent while the dead legs are still wet.

---

## Oxygen service

Oxygen systems get a separate and much more stringent verification, because contamination is an ignition source rather than a nuisance.

**Per ASTM G93 and SAE ARP1176:**

- **NVR is the governing requirement**, not particulate
- **No hydrocarbon solvents at any stage**, because the residue is the hazard
- **Cleaning and sampling materials must themselves be oxygen compatible**: no hydrocarbon wipes, no ordinary gloves, no shop air
- **Verification is mandatory and documented**, gravimetric NVR plus black light
- **Packaging immediately** in a verified-clean bag, double bagged, caps installed
- **The bag is opened only in a controlled environment**, at installation

**The failure mode is direct.** A hydrocarbon film in a GOX line has an autoignition temperature around 500 K in oxygen, and adiabatic compression on valve opening exceeds that easily. That is a fire in the line, and in an oxygen-enriched environment the line then burns.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Specify particulate AND NVR | Level 100A, not Level 100 |
| Always run a blank | If the blank is comparable, the sample is meaningless |
| Define the sampled area | A count without an area has no units |
| Sample where contamination collects | Not where it is convenient |
| Report the distribution | Not just the largest particle |
| Balance resolution | At least 10x below the NVR limit |
| Verify moisture by dew point, not time | Dead legs defeat time-based purging |
| Sample from the far end | The inlet reads the purge gas |
| Oxygen service | ASTM G93, NVR governing, no hydrocarbons at any stage |
| Internal passages | Flow test plus destructive coupon; a rinse is not representative |

---

## Failure modes

**No blank.** The solvent contribution is unknown and may be the whole measurement.

**Undefined sample area.** The count cannot be compared to a specification or to another sample.

**Sampling the convenient location.** The clean part is verified and the dirty part is not.

**Particulate verified, NVR not.** The hydrocarbon film that will ignite is invisible to the verification.

**Incomplete evaporation.** Residual solvent weighs as residue and the article fails a test it should pass.

**Fingerprints from handling the vessel.** A fingerprint is NVR, and it is on the measurement rather than on the article.

**Time-based purge verification.** Dead legs read dry at the vent.

**Verification passed, then the article is opened.** Cleanliness is a state, not a property, and it ends the moment a cap comes off.

---

## Standards

| Standard | Scope |
|---|---|
| **IEST-STD-CC1246** | Product cleanliness levels and contamination control |
| **ASTM G93** | Cleaning methods and cleanliness levels for oxygen service |
| **SAE ARP1176** | Oxygen system and component cleaning and packaging |
| ASTM F331 | Nonvolatile residue of solvent extract from aerospace components |
| ASTM F312 | Microscopical sizing and counting particles on membrane filters |
| ASTM F303 | Sampling for particles in aerospace fluids and components |
| ASTM A380 | Cleaning, descaling and passivation of stainless steel |
| MIL-STD-1330 | Cleaning and testing of shipboard oxygen systems |
| ISO 14952 | Space systems, surface cleanliness of fluid systems |

---

## Tool interface

Cleanliness enters the library through the filtration rating, which is what the specification has to be consistent with:

```python
from Filter import Filter    # fluidSystems design library

element = Filter()
element.setInputs({'fluid': 'N2H4', 'filterType': 'pleated mesh', 'massFlow': 0.045,
                   'upstreamPressure': 2.3e6, 'protectedPassage': 0.0017,
                   'allowableCleanPressureDrop': 2.0e4, 'contaminationLoading': 1e-3})
element.selectRating()
print(element.absoluteRating, element.protectionRatio)
```

The cleanliness level and the filter rating have to be consistent with each other and with the passage being protected. A Level 100 specification permits a 100 micron particle, which plugs a 300 micron orifice regardless of what the filter is rated at.

---

## References

1. IEST-STD-CC1246E, *Product Cleanliness Levels*.
2. ASTM G93-19, *Standard Guide for Cleaning Methods and Cleanliness Levels for Material and Equipment Used in Oxygen-Enriched Environments*.
3. SAE ARP1176, *Oxygen System and Component Cleaning and Packaging*.
4. NASA KSC-C-123J, *Surface Cleanliness of Fluid Systems*.
