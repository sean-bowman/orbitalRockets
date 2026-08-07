[Home](../README.md) > Die Casting

# Die Casting

## Contents

- [Overview](#overview)
- [Hot and cold chamber](#hot-and-cold-chamber)
- [What it achieves](#what-it-achieves)
- [Why it is hard to qualify](#why-it-is-hard-to-qualify)
- [The vacuum and squeeze variants](#the-vacuum-and-squeeze-variants)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Molten metal is injected into a steel die at high pressure and high speed. It gives the best dimensions and the best surface of any casting process, and it entraps gas doing it.

That entrapped gas is why die casting is rare in flight structure.

---

## Hot and cold chamber

| Variant | Injection | Alloys | Rate |
|---|---|---|---|
| **Hot chamber** | Pump submerged in the melt | Zinc, magnesium | Very fast |
| **Cold chamber** | Melt ladled into a shot sleeve | **Aluminium**, copper | Slower |

**Aluminium requires cold chamber** because molten aluminium attacks the steel of a submerged pump. That makes the cycle longer and it adds the ladling step, where air is entrained.

---

## What it achieves

| Property | Value |
|---|---|
| **Minimum wall** | 1.0 mm, the best of any casting route |
| **Tolerance** | DCTG 4, roughly IT8 |
| **Surface** | 1.6 um Ra |
| Maximum mass | 25 kg |
| Lead time | **26 weeks**, dominated by the die |
| Relative cost | 0.4 at volume |

**The dimensional capability is genuinely excellent** and many die cast features need no machining at all.

**The die is the cost and the lead time.** A hardened steel die that survives tens of thousands of shots of molten aluminium is a major tooling investment, and it only pays at volume.

---

## Why it is hard to qualify

**The fill is fast, and fast fill entrains air.**

Metal enters the die at 30 to 60 m/s. The air in the cavity has nowhere to go in the milliseconds available, so it is entrained in the metal as fine dispersed porosity.

| Consequence | Detail |
|---|---|
| **Porosity throughout** | Fine, dispersed, and it reduces properties |
| **Cannot be HIPed** | The gas is compressed, not removed, and it re-expands on heat treatment |
| **Cannot be heat treated** | Solution treatment blisters the casting as the gas expands |
| Properties are as-cast only | No T6 condition |

**The inability to heat treat is the killer for structure.** An aluminium casting that cannot be solution treated and aged is stuck at as-cast properties, which are a fraction of what the alloy can do.

**That is why die casting is a commercial process rather than an aerospace structural one**, and why it appears in this domain mostly as a comparison point.

---

## The vacuum and squeeze variants

**Both exist specifically to address the gas problem.**

| Variant | Method | Result |
|---|---|---|
| **Vacuum die casting** | The cavity is evacuated before the shot | Far less entrained gas. **Heat treatable** |
| **Squeeze casting** | Slow fill, then high pressure applied during solidification | Very low porosity, near-wrought properties |
| Semi-solid (thixocasting) | Injected as a semi-solid slurry | Laminar fill, low porosity |

**Vacuum die casting produces heat treatable aluminium castings** and it is used for structural automotive components. It is a real process with real properties, and it is the variant worth knowing about.

**Squeeze casting approaches wrought properties** because the applied pressure feeds the solidification shrinkage directly. It is slow and it is limited to simple shapes.

**These variants change the qualification story entirely**, and a die casting specification that does not say which variant is being used has not specified the important thing.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Minimum wall | 1.0 mm |
| Tolerance | DCTG 4, the best casting tolerance |
| Lead time | 26 weeks, die dominated |
| Conventional die casting | Cannot be heat treated |
| Cannot be HIPed | Gas re-expands |
| Vacuum die casting | Heat treatable, and a different proposition |
| Squeeze casting | Near-wrought properties, simple shapes |
| Specify the variant | It decides the qualification |

---

## Failure modes

**Conventional die casting solution treated.** It blisters.

**HIP expected to close the porosity.** The gas re-expands later.

**As-cast properties assumed to be T6.** They are far lower.

**Die casting specified without the variant.** The qualification story is undefined.

**Low volume die casting.** The die never amortises.

---

## Standards

| Standard | Scope |
|---|---|
| ASTM B85 | Aluminium alloy die castings |
| ASTM B94 | Magnesium alloy die castings |
| NADCA product specification standards | The industry reference |
| ISO 8062 | Casting tolerances |
| AMS 2175 | Castings, classification and inspection |

---

## References

1. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
2. ASM Handbook Volume 15, *Casting*.
3. Vinarcik, E. J., *High Integrity Die Casting Processes*, Wiley, 2002.
