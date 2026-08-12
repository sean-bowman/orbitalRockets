[Home](../README.md) > Standards Index

# Standards Index

## Contents

- [Overview](#overview)
- [DESR 6055.09](#desr-605509)
- [NASA-STD-8719.12A](#nasa-std-871912a)
- [Two things reading them corrected](#two-things-reading-them-corrected)
- [AFSPCMAN 91-710](#afspcman-91-710)
- [What was not read](#what-was-not-read)
- [References](#references)

---

## Overview

This domain rests on one standard read in full and several not read, which is a better position than the domain before it and worse than fluid systems.

The one that was read is the explosives siting standard, and it is the one this domain's hardest number comes from.

---

## DESR 6055.09

*Defense Explosives Safety Regulation*, Edition 1 Change 1, 23 February 2024. Volume 5 Enclosure 4 covers energetic liquids.

**Read in full for the parts this domain uses**: Table V5.E4.T5, the energetic liquid equivalent explosive weights, and its footnote f, which carries the hydrogen rule.

It supplies:

- The TNT equivalence percentages for every liquid combination the standard covers, in both the range launch and static test stand columns
- The rule that a combination not in the table goes to individual assessment rather than to a default
- The hydrogen rule, `max(8 W**(2/3), 0.14 W)` in pounds
- The RP-1 two-tier rule, 20 per cent up to 226,795 kg and 10 per cent on the excess
- The substitution rules: MMH for hydrazine or UDMH, alcohols and hydrocarbons for RP-1, hydrogen peroxide for LO2 in a hydrocarbon combination

**And the caveat that governs the whole table**: the percentages apply to propellant aboveground and unconfined except by its own tankage. Confinement is a different problem and the standard sends it elsewhere.

---

## NASA-STD-8719.12A

*Safety Standard for Explosives, Propellants and Pyrotechnics*, 23 May 2018.

**Read in full for Tables 5-29 and E-1.** Table 5-29 reproduces the DESR table identically and cites it. Table E-1 is the K factor table, and it is the more useful of the two here because it carries the overpressure and the consequence alongside each K value.

**Both are in this library** and both are asserted against the register by a test.

The consequence descriptions are worth reading rather than summarising. At K = 18, intraline distance without barricades and 3.5 psi, the standard says damage to unstrengthened buildings is around half their replacement cost and there is a one per cent chance of eardrum damage. That is what an operations building is being designed to, and it is not a benign number.

---

## Two things reading them corrected

Both are recorded in [ValidationReferences](ValidationReferences.md) and both are the kind of thing a summary loses.

**The sixty per cent hydrogen figure is not the siting rule.** It is a yield figure from the Project PYRO test series and from an evaluation of shuttle on-pad operations. The siting rule is the max of the sublinear term and fourteen per cent. **Building on sixty per cent would have overstated a small stage by about a factor of three** and missed the shape of the rule entirely.

**The standard's own bracketed metric coefficient does not convert.** The rule is printed as `8 W**(2/3)` in pounds and `4.13 Q**(2/3)` in kilograms, and those are not the same rule: the exact conversion is 6.147, a factor of 1.488 larger. The discrepancy is present in both documents. **An SI-native reading of the bracketed coefficient gives a shorter siting distance than the form the table is built on**, which is non-conservative.

This library computes in the English form and converts, and a test asserts the discrepancy rather than silently correcting it.

---

## AFSPCMAN 91-710

*Range Safety User Requirements*. The Eastern and Western Range requirements for anything flown from a US federal range: system safety, ground and launch personnel safety, flight safety, and the flight termination system requirements.

**Not read.** It is the document that would turn most of [HazardousOperations](HazardousOperations.md) from practice into requirement, and it is the largest single gap in this domain's documentation.

Volume 3 is where the flight termination requirements live, which is [rangeSafetyAndFTS](../../rangeSafetyAndFTS/) rather than here, and it is unread in both places.

---

## What was not read

| Standard | Would fix |
|---|---|
| AFSPCMAN 91-710 | Range user requirements, safety and personnel |
| NFPA 30 and 29 CFR 1910.106 | Flammable liquid storage siting, cited by the explosives standard |
| MIL-STD-1576 | Electroexplosive subsystem safety, shared with [mechanisms](../../mechanismsAndSeparation/docs/StandardsIndex.md) |
| NASA-STD-8719.9 | Lifting standard, which governs erection and mate |
| The interim LO2/LNG TNT curves | Methane, which has no entry in the equivalence table |

**Methane is worth calling out.** It is a current propellant on multiple vehicles and the equivalence table does not cover it. The interim curves developed for LO2/LNG are exactly that, interim, and the library refuses a combination it has no rule for rather than borrowing the kerosene number.

**And one that is not a standard at all**: a tanking procedure with its phase rates and transitions. Every programme writes one and none publishes one, and it would close half of the [loading phase gap](ValidationReferences.md).

---

## References

- DESR 6055.09, Edition 1 Change 1, Volume 5 Enclosure 4
- NASA-STD-8719.12A, Tables 5-29 and E-1
- AFSPCMAN 91-710, *Range Safety User Requirements*, not read
- AFRPL-TR-67-124, cited by the standard for the hybrid propellant evaluation
- [ValidationReferences](ValidationReferences.md)
