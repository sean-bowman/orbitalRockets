# groundSystemsAndOperations

**Launch Site, Ground Support Equipment and Operations**

> **Status: scaffolded.** The topic coverage below is defined and the documents are planned. Nothing in this domain is written yet. See [../fluidSystems/](../fluidSystems/) for a completed domain.

---

## What This Is

The vehicle spends hours on the pad and minutes in flight, and most of the risk to people is on the ground. This domain covers the launch site, the ground support equipment, propellant handling, and the operations and procedures that connect them.

Documentation first because the engineering here is heavily procedural and site-specific, and because the analytical parts are already covered by the fluid systems library.

Reference documentation first. A class library will follow once the documents establish what the tools actually need to compute.

## Design Ethos

- Ground systems are a fluid system with different constraints: heavier, cheaper, reconfigured constantly.
- The interface is where the problems are. Umbilicals and disconnects deserve disproportionate attention.
- A procedure that cannot be followed under pressure will not be followed under pressure.
- Everything that can be verified before the vehicle arrives should be.
- Scrub turnaround time is a design requirement, not an operational detail.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/GroundSystemsOverview.md` | Hub: the launch site, the operations flow, document index | planned |
| `docs/LaunchPadAndFacilities.md` | Pad layout, flame trench, deluge, lightning protection, blast | planned |
| `docs/PropellantStorageAndTransfer.md` | Storage tanks, transfer systems, conditioning, boil-off management | planned |
| `docs/UmbilicalsAndDisconnects.md` | Umbilical design, retract, separation force, contingency reconnect | planned |
| `docs/GSEDesign.md` | GSE fluid systems, pneumatics, control systems, mobility | planned |
| `docs/LaunchOperations.md` | Countdown, holds, recycles, scrub turnaround, launch commit criteria | planned |
| `docs/HazardousOperations.md` | Propellant loading, clearing, hazard zones, personnel protection | planned |
| `docs/ControlAndDataSystems.md` | Ground control architecture, interlocks, data recording, command paths | planned |
| `docs/IntegrationAndProcessing.md` | Vehicle integration flow, transport, erection, mate operations | planned |
| `docs/WeatherAndConstraints.md` | Weather rules, wind, lightning, upper level winds, launch windows | planned |
| `docs/StandardsIndex.md` | Annotated index of the governing ground and range standards | planned |

## Library

None planned yet. Reference documentation first. A class library will follow once the documents establish what the tools actually need to compute.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [fluidSystems](../fluidSystems/) | GSE is a fluid system; the analytical tools apply directly |
| [fluidSystemsTesting](../fluidSystems/fluidSystemsTesting/) | Test stands and launch pads share most of their design problems |
| [rangeSafetyAndFTS](../rangeSafetyAndFTS/) | Hazard zones, clearing and launch commit criteria |
| [recoveryAndReusability](../recoveryAndReusability/) | Recovery and refurbishment operations run on the same ground infrastructure |

---

Sean Bowman
