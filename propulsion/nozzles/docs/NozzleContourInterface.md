[Home](../README.md) > Nozzle Contour Interface

# Nozzle Contour Interface

## Contents

- [Overview](#overview)
- [The boundary](#the-boundary)
- [Related](#related)
- [Why the boundary is where it is](#why-the-boundary-is-where-it-is)
- [What this domain supplies](#what-this-domain-supplies)
- [What NOVA returns](#what-nova-returns)
- [How the two are kept consistent](#how-the-two-are-kept-consistent)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Nozzle work splits into two halves and this repository owns one of them. **The boundary is one of fidelity, not of subject.**

**The decisions and the conceptual geometry** are here: what area ratio, what contour family, what the loss budget is, where the flow separates, what altitude compensation would be worth, and approximately what shape and how much wetted area the bell has.

**The geometry for manufacture** is not: the method of characteristics contour and the cooling channel layout that follows it.

This document originally drew the line at geometry altogether and said this sub-domain supplied requirements and nothing else. That was too broad, and it left the loss budget depending on a tabulated exit angle that was wrong by three and a half degrees. See [NozzleContour](NozzleContour.md).

---

## The boundary

| Question | Owner |
|---|---|
| What area ratio | [propulsion hub](../../docs/PerformanceFundamentals.md) |
| What contour family, and what it costs | This sub-domain |
| Where does it separate | This sub-domain |
| What would compensation be worth | This sub-domain |
| **Approximately what shape, and how much area** | **This sub-domain, by Rao's approximation** |
| **What are the coordinates** | **NOVA** |
| **What are the channel geometries** | **NOVA** |
| **CAD-ready output** | **NOVA** |

---

## Related

[NozzleContour](NozzleContour.md) is the conceptual half of that table: Rao's approximation, the wall angles it gives, the wetted area it integrates, and the lookup table it replaced.

---

## Why the boundary is where it is

**A second method of characteristics implementation would be a second thing to keep in agreement, and nothing would enforce the agreement.**

That is the same argument that keeps `joiningProcesses` in [aerospaceMaterials](../../../aerospaceMaterials/README.md) documentation-only against the existing `Weld` class, and the same one that stopped this sub-domain building a thrust coefficient the [propulsion hub](../../docs/PerformanceFundamentals.md) already owns and has validated against RS-25.

It is worth being explicit about the failure mode being avoided. Two implementations of the same method drift. They drift slowly, they drift silently, and the drift is discovered when two people produce different answers for the same nozzle and neither can say which is right. A repository with one implementation and a stated boundary is in a better position than one with two and a convention about which to use.

**Rao's approximation is not a second implementation of that method.** It is a closed-form fit to published design charts, it is the standard conceptual-design tool, and it produces a wall angle and an area rather than a wall. Nothing it computes is something NOVA would also compute and have to agree with, except the exit angle, which is the one number the two halves have always shared and which this document has always said to check on return.

**The argument against duplication is not an argument against every calculation in a neighbouring subject.** Conflating the two is how a sub-domain ends up with a lookup table where it needed an equation, which is exactly what happened here.

---

## What this domain supplies

The requirements a contour generator needs, and nothing it does not.

| Quantity | Source |
|---|---|
| Throat diameter | [EngineSizing](../../docs/EngineSizing.md) |
| Area ratio | [EnginePerformance](../../docs/PerformanceFundamentals.md), bounded by [FlowSeparation](FlowSeparation.md) |
| Contour family and length fraction | [NozzlePerformance](NozzlePerformance.md) |
| Chamber pressure and propellant | The hub |
| Wall heat flux | [combustionDevices](../../combustionDevices/docs/RegenerativeCooling.md) |
| Coolant flow and inlet conditions | [combustionDevices](../../combustionDevices/docs/RegenerativeCooling.md) |

---

## What NOVA returns

Geometry, and this domain consumes it rather than checking it.

- The wall contour, as coordinates
- Cooling channel geometry along it
- CAD-ready output

**The one number worth checking on return** is the exit wall angle, because that is what the divergence efficiency in [NozzlePerformance](NozzlePerformance.md) is computed from. A contour whose exit angle differs from the one assumed changes the loss budget, and it is the only place the two halves can disagree numerically.

---

## How the two are kept consistent

There is no automated check, and that is a deliberate limitation rather than an oversight.

NOVA is a separate suite outside this repository. A cross-repository test would need one to import the other, which would couple their release cycles and defeat the point of the separation. The repository-wide link checker also refuses links that point outside the repository, so this document names NOVA rather than linking to it.

**What holds instead is a stated interface**: the quantities above, in those units, and the exit angle checked on return. That is weaker than a test and it is honest about being weaker.

If the two ever need to be checked automatically, the right shape is a fixture file: NOVA writes a contour summary, this repository reads it and asserts the exit angle and area ratio match what it asked for. That is recorded here as the next step rather than implied to exist.

---

## Design rules of thumb

- **Supply the requirements, and a conceptual contour to size against. Do not supply a wall to cut metal from.**
- **Check the exit angle on return.** It is the one number the two halves share.
- **Do not reimplement the method of characteristics** to avoid a dependency. The dependency is the cheaper problem.
- **Do not let that argument stop you computing the things a closed form can do.** A conceptual wall angle is not a rival contour generator, and refusing to compute it is how the loss budget ended up on a wrong lookup table.
- **State the interface in units.** Most cross-tool errors are unit errors.

---

## Failure modes

**A second contour generator written for convenience.** Two implementations drift silently.

**The exit angle assumed rather than read back.** It sets the divergence loss and it is the only shared number.

**The exit angle tabulated rather than computed.** The failure that actually happened here, and it inverted a published finding. A fixed number per contour family cannot represent something that varies by a factor of two across the area ratios a launch vehicle uses.

**The boundary blurred over time.** A little contour work here and a little performance work there, and neither tool is authoritative.

**The boundary drawn too wide.** The opposite error, and the one this document made. "NOVA owns contours" was read as "compute no geometry at all", which left a lookup table doing a job an equation should have been doing.

**NOVA linked rather than named.** The link checker refuses out-of-repository links, and it is right to.

---

## References

- Rao, *Exhaust nozzle contour for optimum thrust*
- NASA SP-8120, *Liquid rocket engine nozzles*
- Anderson, *Modern Compressible Flow*, the method of characteristics chapters
