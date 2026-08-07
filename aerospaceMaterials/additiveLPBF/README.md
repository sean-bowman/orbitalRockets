# additiveLPBF

**Laser Powder Bed Fusion for Aerospace Hardware**

> **Status: complete.** 15 documents, with the classes below built and tested. See [../../fluidSystems/](../../fluidSystems/) for the domain this one is modelled on.

---

## What This Is

LPBF is the process that made integrated, conformally cooled and topologically optimized propulsion hardware practical. This sub-domain covers the process itself, the alloys that work in it, the defect population it produces, and the qualification burden that comes with it.

It is the process sub-domain closest to my existing experience, and the one with the most direct impact on fluid system hardware.

---

## Library

Built and tested. Run `python -m pytest tests/ -v` from this directory.

| Class | Computes |
|---|---|
| [`LpbfProcess`](additiveLpbfLibrary/LpbfProcess.py) | Process window, melt pool, design for additive checks and build time |
| [`PowderLot`](additiveLpbfLibrary/PowderLot.py) | Flowability, oxygen pickup across reuse, and the blend-back mass balance |
| [`LpbfQualification`](additiveLpbfLibrary/LpbfQualification.py) | Part classification and the evidence it demands |

**`LpbfProcess`** -- volumetric energy density and normalised enthalpy; Eagar-Tsai melt pool depth against the layer overlap criterion; lack of fusion, stable and keyhole classification; minimum wall, overhang angle and self-supporting channel checks; powder evacuation feasibility, which raises rather than warns; as-built roughness by build angle; scan and recoat build time.

**`PowderLot`** -- Hausner ratio and Carr index against the flowability scale; particle size distribution against the layer thickness; oxygen accumulation and the cycles remaining before the limit; the virgin fraction needed to hold a target, and the steady state at which a lot never retires on chemistry.

**`LpbfQualification`** -- NASA-STD-6030 consequence class against process maturity; witness coupon count, placement and test matrix; NDE method selection including the computed tomography trigger; the five qualification pillars; the allowables basis and the orientation knockdown.

Shared helpers come from [`lpbfUtils`](additiveLpbfLibrary/lpbfUtils.py), which bootstraps both [`orbitalRockets/common`](../../common/) and the parent [`aerospaceMaterialsLibrary`](../aerospaceMaterialsLibrary/), so a class here can query an alloy and apply a knockdown without repeating the import.

The module is named `lpbfUtils.py` rather than `utils.py` deliberately. Every library in this repository ends up on a flat `sys.path` when pytest collects them in one process, so a second `utils.py` would shadow the first and whichever was imported earliest would win.

---

## Topic coverage

- [ ] Process fundamentals: melt pool, scan strategy, layer thickness, energy density
- [ ] Machine and parameter selection: OEMs, build volume, laser count, parameter development
- [ ] Alloys: GRCop-42, Inconel 625 and 718, AlSi10Mg, Ti-6Al-4V, 316L, and what each needs
- [ ] Powder: PSD, morphology, chemistry, reuse and degradation, handling and safety
- [ ] Defects: porosity, lack of fusion, keyholing, cracking, and how each is detected
- [ ] Residual stress, distortion, and support strategy
- [ ] Anisotropy: build direction effects on strength, fatigue and thermal conductivity
- [ ] Post-processing: stress relief, HIP, solution and age, machining datums
- [ ] Surface condition: as-built roughness, downskin, and the link to extrusion honing
- [ ] Design for LPBF: minimum feature, overhang angle, self-supporting channels, powder removal
- [ ] Internal passages: powder evacuation, inspection, the limits of what can be verified
- [ ] Inspection: CT, in-situ monitoring, witness coupons
- [ ] Qualification: NASA-STD-6030, MSFC-STD-3716, part classification, equivalency
- [ ] Service bureaus versus in-house, and what each requires

---

Sean Bowman
