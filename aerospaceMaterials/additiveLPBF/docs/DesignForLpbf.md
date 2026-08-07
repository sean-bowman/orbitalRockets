[Home](../README.md) > Design for LPBF

# Design for LPBF

## Contents

- [Overview](#overview)
- [The geometric limits](#the-geometric-limits)
- [The overhang angle](#the-overhang-angle)
- [Self-supporting channels](#self-supporting-channels)
- [Orientation](#orientation)
- [Consolidation, and its limit](#consolidation-and-its-limit)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Additive manufacturing is often sold as design freedom. It is not free: it is a different set of constraints from machining, and a designer who treats it as unconstrained produces parts that cannot be built, cleared of powder, or inspected.

The constraints are few and they are hard.

---

## The geometric limits

| Limit | Value | What happens past it |
|---|---|---|
| **Minimum wall** | 0.4 mm | Not fully dense; properties are not in any database |
| **Minimum feature** | 0.3 mm | Not resolved |
| **Self-supporting overhang** | 45 deg from horizontal | Needs support |
| **Unsupported horizontal span** | 2 mm | Sags or curls |
| **Self-supporting round channel** | 8 mm | Roof sags. Use a teardrop |
| **Minimum channel** | 0.5 mm | Powder cannot be evacuated at all |
| **Channel aspect ratio** | 20 : 1 | Powder cannot be reliably evacuated |
| **Minimum printed hole** | 0.8 mm | Print undersize and drill |

**These are the capability of a well developed parameter set on a modern machine.** A specific machine and alloy may do better or worse, and the numbers should be confirmed rather than assumed.

---

## The overhang angle

**45 degrees from horizontal is the classic rule** and the mechanism is worth understanding.

A layer overhanging the one below sits partly on loose powder. Powder is a poor conductor and offers no mechanical support, so the melt pool sinks into it. At a shallow angle each layer overhangs the last by more than the melt pool can bridge, and the surface sinks progressively.

| Angle from horizontal | Result |
|---|---|
| Above 45 deg | Self-supporting. Surface degrades gradually below 60 |
| 30 to 45 deg | Poor surface, dross, usually needs support |
| Below 30 deg | Sags. Needs support |
| 0 deg (horizontal) | Needs support beyond a 2 mm span |

**The angle can often be designed away.** Replacing a flat horizontal roof with a shallow gable, a chamfer or a teardrop makes it self-supporting at no cost in function. **That is the single highest-value design move in this process.**

---

## Self-supporting channels

A horizontal round channel has a flat roof at its crown, which is a horizontal overhang. Above about 8 mm diameter it sags.

| Section | Self-supporting at any size | Why |
|---|---|---|
| Round | No, above ~8 mm | The crown is horizontal |
| **Teardrop** | **Yes** | The crown is a point above the self-supporting angle |
| **Diamond** | **Yes** | Same, with a sharper apex |
| Elliptical, tall | Yes, if the aspect is enough | The crown curvature stays above the angle |

**The teardrop is the standard answer** and it costs almost nothing: the flow area is essentially the same and the pressure drop is barely affected. A designer who knows the trick uses it everywhere; one who does not fills the part with supports that cannot be removed.

---

## Orientation

Orientation is chosen once and it decides several things at once, and they conflict.

| Objective | Wants |
|---|---|
| Minimum supports | Overhangs above 45 degrees |
| Best surface on a critical face | That face up-skin or vertical |
| Best properties in the loaded direction | Load in XY, not Z |
| Minimum build height | Lowest, since height drives recoat time |
| Minimum residual stress | Gradual cross-section change between layers |
| Powder evacuation | Passages draining downward |

**They conflict, and the resolution is a decision rather than an optimisation.** A part oriented for minimum supports may put the loaded direction in Z; one oriented for best properties may need supports inside a passage.

**Whatever is chosen has to go on the drawing.** See [Anisotropy.md](Anisotropy.md).

---

## Consolidation, and its limit

The strongest argument for additive is part consolidation: six machined pieces and five joints become one piece and no joints.

**Every joint removed is a leak path removed, a fastener removed, an inspection removed and an assembly step removed.** On a fluid system manifold that is a large saving and it is real.

**The limit is inspectability.** A consolidated part has internal geometry, and internal geometry can only be inspected by computed tomography. Consolidating to the point where the part cannot be verified has traded a set of inspectable joints for an uninspectable monolith.

**The question to ask at concept:** if this part has a defect in the internal passage, how would anyone know? If the answer is CT, that is a cost and a schedule item. If the answer is that nobody would know, the consolidation has gone too far.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Minimum wall | 0.4 mm |
| Self-supporting overhang | 45 degrees |
| Round channel self-supporting limit | 8 mm |
| **Use teardrop or diamond channels** | Self-supporting at any size |
| Channel aspect ratio for powder removal | 20 : 1 |
| Print holes undersize and drill | Below 0.8 mm |
| Design supports out rather than in | They cannot be removed from a closed passage |
| Orientation goes on the drawing | It is a design decision |
| Consolidate until inspectability limits it | Not further |

---

## Failure modes

**A closed passage requiring internal supports.** They are permanent.

**A horizontal round channel above 8 mm.** The roof sags.

**A part consolidated beyond what can be inspected.** No way to verify it.

**Orientation left to the build preparation technician.** The loaded direction ends up in Z.

**A wall below 0.4 mm.** Not fully dense, and no allowable applies.

**A dead-ended passage.** Powder cannot drain and it cannot be honed.

---

## Standards

| Standard | Scope |
|---|---|
| ISO/ASTM 52910 | Design for additive manufacturing, guidelines |
| ISO/ASTM 52902 | Test artefacts for geometric capability |
| NASA-STD-6030 | Additive manufacturing requirements |
| MSFC-STD-3716 | LPBF spaceflight hardware |

---

## Tool interface

```python
from LpbfProcess import LpbfProcess, DFAM_LIMITS

process = LpbfProcess()
process.setInputs({'material': 'Inconel 718'})

result = process.checkGeometry({'minimumWallThickness': 0.0003,
                                'overhangAngle': 30.0,
                                'channelDiameter': 0.012,
                                'unsupportedSpan': 0.005})

for violation in result['violations']:
    print('VIOLATION:', violation)
for warning in result['warnings']:
    print('WARNING:  ', warning)
```

---

## References

1. ISO/ASTM 52910, *Additive Manufacturing -- Design -- Requirements, Guidelines and Recommendations*.
2. Thompson, M. K. et al., "Design for Additive Manufacturing: Trends, Opportunities, Considerations and Constraints", *CIRP Annals*, Vol. 65, 2016.
3. Gradl, P. R. et al., *Metal Additive Manufacturing for Propulsion Applications*, AIAA, 2022.
