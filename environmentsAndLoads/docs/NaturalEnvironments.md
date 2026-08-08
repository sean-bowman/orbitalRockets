[Home](../README.md) > Natural Environments

# Natural Environments

## Contents

- [Overview](#overview)
- [Ground and pad environments](#ground-and-pad-environments)
- [Salt fog and humidity](#salt-fog-and-humidity)
- [Sand, dust and rain](#sand-dust-and-rain)
- [Lightning](#lightning)
- [The space environment](#the-space-environment)
- [Radiation](#radiation)
- [Atomic oxygen](#atomic-oxygen)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The natural environments are the ones that act slowly, are easy to defer, and produce failures that appear long after the decision that caused them. They are also where the launch site rather than the vehicle determines the requirement.

---

## Ground and pad environments

**Hardware spends far longer on the ground than in flight, and the ground is corrosive.**

| Environment | Duration | Consequence |
|---|---|---|
| **Storage and transport** | Months to years | Corrosion, vibration, handling damage |
| **Pad exposure** | Days to weeks | Salt fog, humidity, temperature cycling |
| **Cryogenic loading** | Hours | Local chilling, condensation, liquid air |
| Countdown holds | Hours to days | Repeated thermal and pressure cycling |

**Transport vibration is frequently the most severe vibration hardware sees**, and it lasts orders of magnitude longer than flight. It is also the environment least likely to have been derived.

**A scrubbed launch is a full environmental cycle.** Load, chill, hold, drain, warm, dry. Hardware qualified for one mission may see a dozen of those, and the cycle count belongs in the fatigue analysis.

---

## Salt fog and humidity

**A coastal launch site is a marine environment and it does not stop being one because the hardware is aerospace.**

| Site | Character |
|---|---|
| **Coastal (Cape Canaveral, Kourou, Wallops)** | Salt fog, high humidity, year round |
| Inland (Baikonur, Jiuquan) | Dry, wide temperature range |
| High latitude (Kodiak, Andoya) | Cold, wet, icing |

**Salt fog drives the galvanic limit from 0.25 V to 0.15 V**, which changes which material pairs are acceptable. See [aerospaceMaterials DissimilarMetalJoints](../../aerospaceMaterials/joiningProcesses/docs/DissimilarMetalJoints.md).

**Condensation is a real load path.** Cryogenic hardware chills the air around it below the dew point, water condenses, runs down, and pools somewhere unintended. On a very cold surface it condenses liquid air, which is oxygen-enriched and is an ignition hazard.

**Humidity plus a cyclic temperature is worse than either.** The daily cycle drives moisture into and out of enclosures by breathing, which is why sealed boxes accumulate water over months on the pad.

---

## Sand, dust and rain

| Environment | Concern |
|---|---|
| **Blowing dust** | Abrasion of optical and sealing surfaces, filter clogging |
| **Rain erosion** | On a fairing or a nose cone at high speed |
| **Hail** | Impact damage on the pad, and it is a real fairing concern |
| Ice | Accretion on cryogenic surfaces, then shed at liftoff |

**Ice shed at liftoff is a debris hazard.** Ice forms on chilled tank surfaces, releases when the vehicle moves, and impacts anything downstream. It was a contributing factor in a well known launch vehicle loss and it drives insulation and purge design.

**Hail on the pad has scrubbed launches and damaged vehicles.** A fairing with honeycomb core is vulnerable to it, and hail covers are real hardware.

---

## Lightning

**A launch vehicle on the pad is a tall grounded conductor in a thunderstorm-prone location, and in flight it can trigger a strike that would not otherwise have occurred.**

| Mechanism | Detail |
|---|---|
| **Direct strike on the pad** | Managed by lightning masts and catenary systems |
| **Triggered lightning in flight** | The vehicle and its exhaust plume form a conductive path |
| Induced transients | Coupled into harnesses even without a direct attachment |

**Triggered lightning is the one that catches programmes.** A vehicle flying through an electrified but non-stormy cloud can initiate a strike that would not have happened without it, which is why launch commit criteria include field mill readings and standoff distances from clouds that look harmless.

**Apollo 12 was struck twice in the first minute**, which is the canonical case and the reason the launch commit criteria are as conservative as they are.

**The exhaust plume is conductive**, so the effective height of the vehicle for lightning purposes is much greater than its physical height.

---

## The space environment

| Environment | Effect |
|---|---|
| **Vacuum** | Outgassing, cold welding, no convection |
| **Radiation** | Total dose, single event effects, displacement damage |
| **Atomic oxygen** | Erosion of polymers and some metals, in low orbit |
| **Micrometeoroid and debris** | Impact, and it is a growing concern |
| **Plasma and charging** | Differential charging, then discharge |
| Thermal cycling | Covered in [ThermalEnvironments.md](ThermalEnvironments.md) |

**Outgassing is a contamination problem for someone else's hardware.** A material that outgasses deposits on cold optical surfaces, and the requirement is stated as total mass loss below 1.0 percent and collected volatile condensable material below 0.1 percent per ASTM E595.

**Cold welding is real and rare.** Clean metal surfaces in vacuum with no oxide between them can bond, which matters for mechanisms that must move after a long dormant period.

---

## Radiation

| Type | Effect | Mitigated by |
|---|---|---|
| **Total ionising dose** | Cumulative degradation of semiconductors | Shielding, rad-hard parts |
| **Single event upset** | A bit flips | Error detection and correction |
| **Single event latchup** | A parasitic structure conducts. **Can be destructive** | Current limiting, part selection |
| Displacement damage | Lattice damage in solar cells and detectors | Coverglass, margin |

**The environment depends enormously on the orbit.** Low equatorial orbit is benign; the inner Van Allen belt is not; a polar orbit passes through the South Atlantic Anomaly repeatedly.

**Latchup is the destructive one.** An upset is recoverable and a latchup can draw enough current to destroy the device, which is why current limiting on a susceptible part is a design requirement rather than a nicety.

**A launch vehicle sees very little of this** because it is in the environment for minutes. It matters for the payload and for anything left in orbit.

---

## Atomic oxygen

**In low Earth orbit the residual atmosphere is atomic oxygen, and the vehicle runs into it at 8 km/s.**

**That gives each atom about 5 eV of collision energy**, which is enough to break chemical bonds. It is a chemically erosive environment rather than an inert one.

| Material | Behaviour |
|---|---|
| **Kapton, Mylar, polymers** | **Eroded steadily.** Measured in cm^3 per incident atom |
| Silver | Oxidised, and the oxide flakes |
| **Silicones** | Form a protective silica layer, then stable |
| Aluminium, gold, ceramics | Essentially unaffected |

**Fluence depends on altitude and solar activity**, and it drops off rapidly with altitude. At 400 km during solar maximum it is severe; at 800 km it is not.

**It is why exposed Kapton MLI is coated** and why silver interconnects on solar arrays are protected. An uncoated polymer surface facing the ram direction can lose measurable thickness over a few years.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Hardware spends far longer on the ground than in flight | And the ground corrodes |
| Transport vibration can exceed flight | And lasts far longer |
| A scrub is a full environmental cycle | Count them |
| Coastal site means a 0.15 V galvanic limit | Not 0.25 |
| Ice shed at liftoff is a debris hazard | Drives insulation and purge |
| Triggered lightning needs no thunderstorm | Field mill criteria exist for this |
| Outgassing: TML < 1.0 %, CVCM < 0.1 % | ASTM E595 |
| Atomic oxygen erodes polymers at 5 eV | Coat exposed Kapton |

---

## Failure modes

**Transport environment never derived.** Often the worst the hardware sees.

**Scrub cycles omitted from the fatigue count.** A dozen full cycles per mission.

**General galvanic limit used at a coastal site.** It is 0.15 V, not 0.25.

**Condensation path not considered on cryogenic hardware.** Water, or liquid air.

**MLI ballooning from unperforated layers.** Covered in [PressureEnvironments.md](PressureEnvironments.md).

**Exposed polymer in the ram direction.** Atomic oxygen erosion.

**Latchup-susceptible part with no current limiting.** Destructive rather than recoverable.

---

## Standards

| Standard | Scope |
|---|---|
| **MIL-STD-810** | Environmental engineering considerations and laboratory tests |
| **NASA-HDBK-1001** | Terrestrial environment criteria |
| **ASTM E595** | Total mass loss and collected volatile condensable materials |
| ASTM B117 | Salt spray testing |
| **NASA-HDBK-4002** | Mitigating in-space charging effects |
| ECSS-E-ST-10-04 | Space environment |
| MIL-HDBK-310 | Global climatic data |
| SAE ARP5412 | Aircraft lightning environment |

---

## Tool interface

```python
# Natural environments are covered here as requirements rather than as calculations. The
# corrosion and compatibility consequences live in aerospaceMaterials.
import sys
sys.path.insert(0, '../aerospaceMaterials/aerospaceMaterialsLibrary')

from CorrosionAssessment import CorrosionAssessment, GALVANIC_POTENTIAL_LIMIT

for environment in GALVANIC_POTENTIAL_LIMIT:
    print(f'{environment:24s} limit {GALVANIC_POTENTIAL_LIMIT[environment]:.2f} V')
```

---

## References

1. MIL-STD-810H, *Environmental Engineering Considerations and Laboratory Tests*.
2. NASA-HDBK-1001, *Terrestrial Environment (Climatic) Criteria Handbook*.
3. Banks, B. A. et al., *Atomic Oxygen Effects on Spacecraft Materials*, NASA TM-2003-212484.
