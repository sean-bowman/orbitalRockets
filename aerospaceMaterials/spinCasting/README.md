# spinCasting

**Centrifugal Casting for Aerospace Components**

> **Status: complete.** 14 documents, with the classes below built and tested. See [../../fluidSystems/](../../fluidSystems/) for the domain this one is modelled on.

---

## What This Is

Centrifugal casting produces cylindrical and axisymmetric components with a directionally solidified, porosity-free structure that static casting cannot match. This sub-domain covers the process, the alloys, the resulting structure, and where it competes with forging and with additive.

---

## Library

Built and tested. Run `python -m pytest tests/ -v` from this directory.

| Class | Computes |
|---|---|
| [`CentrifugalCasting`](spinCastingLibrary/CentrifugalCasting.py) | Speed selection, solidification, and the bore machining allowance |

**`CentrifugalCasting`** -- G-factor and the process window at both ends; Chvorinov solidification from the casting modulus; Stokes inclusion migration compared against the advancing solidification front, giving the capture number and the escape fraction; the segregated bore layer and the machining allowance it sets; pour mass and buy-to-fly.

The capture number is the figure of merit for the process. Well above one and essentially every inclusion reaches the bore ahead of the front, which is exactly why a centrifugal casting is cleaner than a static one of the same alloy. Near or below one and the front outruns them, they are frozen in place, and the process has bought nothing.

Shared helpers come from [`spinCastingUtils`](spinCastingLibrary/spinCastingUtils.py), which bootstraps both [`orbitalRockets/common`](../../common/) and the parent [`aerospaceMaterialsLibrary`](../aerospaceMaterialsLibrary/).

The module is named `spinCastingUtils.py` rather than `utils.py` deliberately, because every library in this repository ends up on a flat `sys.path` when pytest collects them in one process.

---

## Topic coverage

- [ ] Process fundamentals: true centrifugal, semi-centrifugal, centrifuge casting
- [ ] Rotational speed selection and the G-factor
- [ ] Mould design: permanent versus expendable, coatings, thermal management
- [ ] Solidification: directional structure, grain refinement, segregation
- [ ] Porosity and inclusion migration: why the process is inherently clean
- [ ] Alloys: steels, nickel alloys, copper alloys, aluminum, titanium limitations
- [ ] Achievable geometry: wall thickness, length to diameter, bore finish
- [ ] Machining allowance and the as-cast surface
- [ ] Defects: cold shuts, banding, segregation bands, hot tearing
- [ ] Post-processing: heat treatment, HIP, machining
- [ ] Inspection: RT, UT, dye penetrant, dimensional
- [ ] Comparison against forging, wrought and additive: cost, lead time, properties
- [ ] Qualification and lot acceptance

---

Sean Bowman
