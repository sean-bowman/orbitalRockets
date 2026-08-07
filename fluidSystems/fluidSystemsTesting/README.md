# fluidSystemsTesting

**Fluid System Test Campaigns -- Concept Through Qualification to Flight Acceptance**

The counterpart to the [fluidSystems](../) design library. That one says what to build; this says how to prove it works.

---

## What This Is

A test engineering reference and toolset covering the full campaign: what gets tested, at what level, in what order, with what instrumentation, to what statistical confidence, and what to do when it fails.

**A naming note.** [`fluidSystems/tests/`](../tests/) holds pytest unit tests for the design library code. This directory documents physical hardware testing. Different things, adjacent names, and worth being explicit about.

## Design Ethos

- Qualification and acceptance are different activities with different levels and different consequences. Conflating them is the most expensive test planning error there is.
- Test sequence is not arbitrary. Proof before leak, leak after every environment, burst last.
- A requirement you cannot measure is not a requirement. Check measurability while the requirement is still negotiable.
- Every dB of margin should be traceable to a source. Test levels are derived, not chosen.
- Tailoring is legitimate. Tailoring by omission, where a test quietly does not happen because nobody noticed it was required, is not.
- The test that produces a failure at 3.5x life has demonstrated more than the one that produces nothing at 4x.

---

## Worked example

`codeInterface.py` builds the complete qualification and acceptance campaign for the thruster valve from the design-side example, inheriting its two governing numbers:

| Inherited from the design analysis | Value | What it drives |
|---|---|---|
| Peak pressure including water hammer surge | 2.4249 MPa | MEOP, and therefore proof and burst |
| Hazard-derived system leak allowable | 1.042e-05 scc/s He | Leak method, and the joint architecture |

```bash
python codeInterface.py
```

### What it produces

| Quantity | Value |
|---|---|
| Qualification sequence | 14 tests, 1 destructive |
| Acceptance sequence | 10 tests, every flight article |
| Proof pressure | 3.6374 MPa, 300 s hold, hydrostatic |
| Burst pressure | 6.0622 MPa, destructive |
| Leak method | Sniffer probe, 10.4x margin over its floor |
| Per-joint leak allowable | 8.68e-07 scc/s across 12 joints |
| Random vibration, qualification | 11.48 Grms, 120 s per axis |
| Shock, qualification | 2100 g peak SRS, 3 per axis |
| Thermal, qualification | 243.2 to 343.1 K, 8 cycles |
| Life, qualification | 20 000 cycles, 0.12 days at 2 Hz |
| Cv measurement uncertainty | +/- 0.0084 (2.41 %, k = 2) |
| Demonstrated reliability | R = 0.4642 at 90 % confidence, from 3 articles |

### The findings, which are the point

1. **The per-joint leak allowable admits only welded or VCR joints.** The design example used AN flare unions at 1e-4 scc/s each. Both directories reach the same conclusion from opposite ends, which is the cross-check working.
2. **Pressure decay cannot verify this leak requirement.** It is temperature-limited at 2.27e-02 scc/s, three orders of magnitude above the target.
3. **A pneumatic proof would store 1830 times the energy of the hydrostatic one** and need a 0.65 m unprotected standoff even at this small volume. Scale that to a tank and it becomes a serious hazard.
4. **Three qualification articles demonstrate R = 0.46, not the R = 0.99 in the requirement.** Closing that gap needs analysis, heritage and process control; the demonstration alone would need 230 units.
5. **The dominant Cv uncertainty is the pressure transducer at 39 % of the variance.** Improving anything else on the stand will not move the result.

---

## Library

| Class | Computes |
|---|---|
| [`TestCampaign`](fluidSystemsTestingLibrary/TestCampaign.py) | The qualification and acceptance matrix: which tests, what order, what rationale, what was tailored out and why |
| [`PressureTest`](fluidSystemsTestingLibrary/PressureTest.py) | Proof and burst levels, hold times, **stored energy and blast standoff**, hoop stress margins |
| [`LeakTest`](fluidSystemsTestingLibrary/LeakTest.py) | Method selection with margin, per-joint allocation, pressure decay feasibility, service fluid scaling |
| [`EnvironmentalTest`](fluidSystemsTestingLibrary/EnvironmentalTest.py) | Grms from a PSD, qualification levels, **Miner duration scaling**, shock and thermal levels |
| [`LifeTest`](fluidSystemsTestingLibrary/LifeTest.py) | Required life by article type, Arrhenius and Coffin-Manson acceleration, duration and feasibility |
| [`UncertaintyBudget`](fluidSystemsTestingLibrary/UncertaintyBudget.py) | GUM budget, RSS combination, expanded uncertainty, **dominant contributor** |
| [`SampleSize`](fluidSystemsTestingLibrary/SampleSize.py) | Success-run and binomial sample sizes, the reverse calculation, Weibull duration trade |

Shared helpers are in [`campaignUtils.py`](fluidSystemsTestingLibrary/campaignUtils.py), which bootstraps both [`orbitalRockets/common`](../../common/) and the sibling [`fluidSystemsLibrary`](../fluidSystemsLibrary/). `LeakTest` delegates to the design library's `LeakPath` rather than reimplementing leak physics, so a design-side statement about achievable leak class and a test-side statement about measurability cannot drift apart.

```python
import sys
sys.path.insert(0, 'fluidSystemsTestingLibrary')

from PressureTest import PressureTest

test = PressureTest()
test.setInputs({'maximumExpectedOperatingPressure': 2.4249e6,
                'hardwareClass': 'line hazardous fluid',
                'testMedium': 'gas', 'testFluid': 'Nitrogen',
                'testVolume': 0.010})
test.calculateLevels()
test.calculateStoredEnergy()
print(test.generateReport())
```

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [FluidSystemsTestingOverview.md](docs/FluidSystemsTestingOverview.md) | Hub: the campaign, terminology, the verification chain, document index | complete |
| [RequirementsAndVerification.md](docs/RequirementsAndVerification.md) | Verification methods, traceability, the VCRM, what "verified" means | complete |
| [TestCampaignPlanning.md](docs/TestCampaignPlanning.md) | Development through qualification to acceptance, matrices, tailoring, article count | complete |
| [ProofAndBurstTesting.md](docs/ProofAndBurstTesting.md) | Levels, hold times, stored energy, pneumatic hazard, permanent set | complete |
| [LeakTesting.md](docs/LeakTesting.md) | Method selection, sensitivity, calibration, where it repeats and why | complete |
| [FlowAndFunctionalTesting.md](docs/FlowAndFunctionalTesting.md) | Flow calibration, Cd and Cv determination, cycle and response testing | complete |
| [EnvironmentalTesting.md](docs/EnvironmentalTesting.md) | Vibration, shock, thermal, thermal vacuum, level derivation, Miner scaling | complete |
| [LifeAndEnduranceTesting.md](docs/LifeAndEnduranceTesting.md) | Life definitions, acceleration models, wear-out, what to instrument | complete |
| [CryogenicAndColdShockTesting.md](docs/CryogenicAndColdShockTesting.md) | Cold functional, cold leak, chilldown, thermal shock | complete |
| [CleanlinessVerification.md](docs/CleanlinessVerification.md) | Particulate and NVR verification, sampling, oxygen service | complete |
| [TestFacilitiesAndGSE.md](docs/TestFacilitiesAndGSE.md) | Test stands, control systems, safety, hazard zones | complete |
| [InstrumentationAndDataAcquisition.md](docs/InstrumentationAndDataAcquisition.md) | Sensor selection for test, sample rates, calibration chains, recording | complete |
| [UncertaintyAndStatistics.md](docs/UncertaintyAndStatistics.md) | GUM, uncertainty budgets, sample size, reliability demonstration | complete |
| [AnomalyAndFailureInvestigation.md](docs/AnomalyAndFailureInvestigation.md) | What to do when a test fails: containment, root cause, corrective action | complete |
| [TestDocumentation.md](docs/TestDocumentation.md) | Plans, procedures, as-run redlines, reports, data packages | complete |
| [AcceptanceAndFlightScreening.md](docs/AcceptanceAndFlightScreening.md) | ATP content, workmanship screens, what acceptance must not do | complete |
| [StandardsIndex.md](docs/StandardsIndex.md) | Annotated index of the governing test standards | complete |

---

## Testing

```bash
python -m pytest tests/ -v
```

Three tiers, matching the repository convention. Tier 2 validates against MIL-STD-1540 qualification levels, the GUM worked example, the success-run reliability formula, Miner's rule fatigue equivalence, and closed-form Grms integration.

---

Sean Bowman
