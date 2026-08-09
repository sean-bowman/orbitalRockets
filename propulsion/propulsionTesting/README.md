# propulsionTesting

**Hot Fire Campaigns and Test Data**

> **Status: complete, at light depth.** Two classes, six documents and 50 tests, with a worked example that asks what a firing can establish and finds that three of its five answers were decided before anyone lit anything.

---

## What This Is

How an engine is actually developed, which is by testing it. This sub-domain covers the campaign structure, what each test is meant to answer, the instrumentation and data reduction that turn a firing into a number, and the uncertainty that decides whether the number means anything.

It is the propulsion counterpart to [fluidSystemsTesting](../../fluidSystems/fluidSystemsTesting/), and it follows the same principle: **a test that cannot fail its own acceptance criterion has not tested anything.** What is added here is the arithmetic for whether a hot fire can.

---

## The result worth taking away

The reduction is three lines of algebra and it contains one genuinely easy mistake.

```
c*  = Pc At / mdot          Cf  = F / (Pc At)          Isp = F / (mdot g)
```

**Chamber pressure and throat area appear in both c\* and Cf, inverted, so they cancel in the product.** `c* * Cf` is exactly `F / mdot`. Combining the two parameters' uncertainties as independent double-counts both shared terms.

| Route to specific impulse | Value | Uncertainty |
|---|---|---|
| `F / (mdot g)`, direct | 277.02 s | **1.25 %** |
| `c* Cf / g`, uncertainties combined | 277.02 s | **2.02 %** |

Same number to the last digit, **1.61 times the uncertainty**. And this repository owns a generic uncertainty budget, in fluidSystemsTesting, that would get it wrong: not because the class is poor but because its interface takes independent contributors and these are not independent.

**That result is an identity rather than a measurement**, which makes it the strongest thing in this sub-domain despite having no external source. No plausible set of instrument figures changes it.

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [DataReduction.md](docs/DataReduction.md) | The three parameters, the correlation trap, and which channel dominates | **written** |
| [CampaignStructure.md](docs/CampaignStructure.md) | The five levels, discrimination, and why back to back beats better instruments | **written** |
| [Instrumentation.md](docs/Instrumentation.md) | The four channels, what makes each hard, and the three sample rate thresholds | **written** |
| [TestStands.md](docs/TestStands.md) | The load path, bias against scatter, and stand dynamics | **written** |
| [StabilityRating.md](docs/StabilityRating.md) | Bombs and pulse guns, how hard the perturbation has to be, and the criterion not carried | **written** |
| [AnomalyInvestigation.md](docs/AnomalyInvestigation.md) | Signatures, the ones that look alike, and the derived channels | **written** |
| [ValidationReferences.md](docs/ValidationReferences.md) | One hardware source, one identity, and three gaps | **written** |

## Library

| Class | Computes | Status |
|---|---|---|
| `PerformanceReduction` | c*, Cf and Isp with a correctly correlated uncertainty budget | **written** |
| `HotFireTest` | Discrimination, sample rate adequacy, duration and stability rating viability | **written** |

Both planned classes were built. `HotFireTest` **refuses** an acceptance band inside the measurement uncertainty rather than reporting a low ratio, because a test that cannot distinguish a pass from a fail and is run anyway produces a verdict decided by noise and signed by a person.

`UncertaintyBudget` in fluidSystemsTesting was deliberately not reused for the reduction, and the reason is in [DataReduction](docs/DataReduction.md) rather than assumed.

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../../common/](../../common/) through this sub-domain's `propulsionTestUtils.py`.

---

## Worked example

`codeInterface.py` asks what a firing on the 100 kN booster can establish.

| Question | Answer |
|---|---|
| Does the injector perform roughly as designed | Yes, and only just, at a discrimination ratio of 2.7 |
| Is this injector a point better than that one | **No, and no instrument fixes it** |
| What is the specific impulse | 277.0 s, plus or minus 1.2 % |
| Is the engine dynamically stable | Not from this data system |
| What is the steady wall temperature | Yes, after 3 s of the burn |

**Three of those five are limited by decisions made before the firing**: the throat measurement, the sample rate, and the burn duration. None is limited by the engine.

Improving both dominant channels takes the discrimination ratio at a one per cent band from 0.7 to 1.5, still below the working floor of three. **The answer is a different comparison rather than a better measurement**: fire both injectors on the same hardware, back to back, and compare them to each other. The shared errors cancel, which is the same cancellation as the trap above, used deliberately.

```bash
python propulsion/propulsionTesting/codeInterface.py
```

---

## What is not here

The objectives for this sub-domain said the knowledge is largely tacit, and it is worth being explicit about which half was captured.

**Captured:** the arithmetic. Uncertainty propagation, discrimination, sample rate adequacy, settling times, perturbation magnitude.

**Not captured:** which channel on a given stand has a history, what a firing sounds like when it is about to go wrong, what post-test inspection finds that data reduction never will, and how long to wait before entering the cell.

The documents say so in their own failure mode sections rather than implying completeness. One criterion is also deliberately absent: **the stability damp time**, because the CPIA guideline that specifies it has not been read, and stating it from memory would put an unsourced number into the one part of this repository whose purpose is to prevent exactly that.

---

## Where this sub-domain connects

| Domain | Interaction |
|---|---|
| [../combustionDevices/](../combustionDevices/) | It owns the stability model; this owns whether a test could demonstrate it, and the 5 to 10 times flux multiplier under instability is why it matters |
| [../ignitionAndStart/](../ignitionAndStart/) | The transients a stand rings on, and the flow measurement that is unavailable through a chill-in |
| [../nozzles/](../nozzles/) | The separation limit that bounds what a sea level firing can test |
| [../../fluidSystems/fluidSystemsTesting/](../../fluidSystems/fluidSystemsTesting/) | The same campaign philosophy, and the uncertainty budget this one deliberately does not reuse |
| [../../reliabilityAndMissionAssurance/](../../reliabilityAndMissionAssurance/) | Test evidence is what a reliability claim rests on |

---

Sean Bowman
