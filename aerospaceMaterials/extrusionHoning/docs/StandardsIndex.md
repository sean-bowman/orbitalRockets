[Home](../README.md) > Standards Index

# Standards Index

Abrasive flow machining has no dedicated international standard, which is itself worth knowing. What governs it is a combination of surface texture standards, additive manufacturing standards, and vendor practice.

## Contents

- [Surface texture](#surface-texture)
- [Additive manufacturing](#additive-manufacturing)
- [Inspection and metrology](#inspection-and-metrology)
- [Cleanliness](#cleanliness)
- [Quality and process control](#quality-and-process-control)
- [Vendor practice](#vendor-practice)
- [How to use them](#how-to-use-them)

---

## Surface texture

| Standard | Governs |
|---|---|
| **ISO 21920** | Surface texture, profile. The current series, superseding ISO 4287 |
| ISO 4287 | Surface texture, profile method. Still widely cited |
| ISO 4288 | Rules and procedures for assessing surface texture |
| **ASME B46.1** | Surface texture. The US equivalent, and it covers replication practice |
| ISO 25178 | Areal surface texture, for optical measurement |
| ISO 13565 | Surfaces with stratified functional properties, for bearing area curves |
| ISO 13715 | Edges of undefined shape, which is how an edge break is specified |

**ISO 13715 is the one to know for a deburring specification.** An edge break produced by abrasive flow has no defined radius, and this is the standard that says how to call it out.

---

## Additive manufacturing

| Standard | Governs |
|---|---|
| **ASTM F3335** | Assessing removal of additive manufacturing residues. The most directly relevant document |
| **NASA-STD-6030** | Additive manufacturing requirements for spaceflight systems |
| MSFC-STD-3716 | LPBF spaceflight hardware |
| MSFC-SPEC-3717 | Control and qualification of LPBF processes |
| ISO/ASTM 52900 | Terminology |
| ISO/ASTM 52902 | Test artefacts for geometric capability |
| ISO/ASTM 52905 | Non-destructive testing of additive parts |

---

## Inspection and metrology

| Standard | Governs |
|---|---|
| ASTM E1441 | Computed tomography imaging |
| ASTM E1351 | Production and evaluation of field metallographic replicas |
| ISO 25178-6 | Classification of methods for measuring surface texture |
| ASME PTC 19.5 | Flow measurement, for a flow test |
| ISO 5167 | Flow measurement by pressure differential devices |

---

## Cleanliness

| Standard | Governs |
|---|---|
| **IEST-STD-CC1246** | Product cleanliness levels |
| ASTM F331 | Nonvolatile residue of solvent extract |
| ASTM F312 | Microscopical sizing and counting particles on membrane filters |
| **ASTM G93** | Cleaning methods and cleanliness levels for oxygen service |
| ISO 14952 | Space systems, surface cleanliness of fluid systems |

**Media removal is a cleanliness problem** and it is governed by the same standards as any other contamination. The media is a silicone-loaded abrasive putty and residues of it are both particulate and non-volatile residue.

---

## Quality and process control

| Standard | Governs |
|---|---|
| **AS9100** | Quality management for aviation, space and defence |
| ISO 9001 | Quality management systems |
| MIL-STD-1520 | Corrective action and disposition of nonconforming material |
| AS9102 | First article inspection requirement |

---

## Vendor practice

**There is no ISO or ASTM standard for the abrasive flow process itself.** What exists is vendor practice, and it is genuinely useful because the equipment makers have the process data.

| Source | Content |
|---|---|
| Extrude Hone / Kennametal | Media grades, process guides, application notes |
| SAE ARP4438 | Abrasive flow machining, where a programme cites a practice document |
| Machining Data Handbook | General abrasive machining data |

**Treat vendor data as a starting point, not as an allowable.** The removal coefficient in particular is geometry specific, and a vendor figure derived on their coupon does not transfer to a specific part. See [ProcessQualification.md](ProcessQualification.md).

---

## How to use them

**There is no standard for the process, so the specification has to be written.** A drawing calling for abrasive flow machining without stating media grade, pressure, cycles and the acceptance method has specified nothing enforceable.

**What a specification needs to state:**

- Media grade and abrasive type
- Pressure and cycle count, or the acceptance criterion if the process is to be developed
- The surfaces to be honed, and the surfaces to be masked
- The acceptance method, and where it is measured
- The permitted dimensional growth
- Edge break, per ISO 13715
- Cleanliness after honing, per an IEST-STD-CC1246 level

**Specify the acceptance, not only the process.** A part honed to the correct parameters that does not meet the flow requirement is still a nonconforming part, and a specification that only calls out parameters has no way to say so.

**The cleanliness requirement is the one most often omitted** and media residue is a real contamination source in a fluid system.
