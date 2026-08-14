# reliabilityAndMissionAssurance

**Reliability, Fault Tolerance and Mission Assurance**

> **Status: complete.** Four classes, twelve documents and 66 tests. No external anchor, and the conclusions least sensitive to that of any domain here.

---

## What This Is

Reliability engineering is what turns a collection of good hardware into a vehicle that works. This domain covers the analytical methods (FMECA, fault trees, reliability allocation), the design responses (redundancy, fault tolerance, derating), and the programmatic systems (quality, configuration control, problem reporting) that make them stick.

**It is deliberately unglamorous and it is where most launch failures are actually decided.**

---

## The four results

**The two FMECA rankings disagree, and the disagreement is the finding.** A risk priority number is severity times occurrence times detection, and all three are ordinal ranks: **multiplying ordinals produces something that sorts and does not measure.** Folding detection in pushes a rare and detectable catastrophe below a common and hidden nuisance, and on the worked table two catastrophic modes drop three and four places for no reason except that somebody can see them coming. **Criticality, which leaves detection out, is the ranking that finds them.**

**The single point failures carry the whole fault tree.** Five of them account for essentially 100 per cent of the top event probability, and the two carefully redundant pairs contribute a thousandth of it. **A fault tree is run for its cut sets, not its number.** And the importance ranking is not the probability ranking: the redundant avionics units sit three orders of magnitude below a single valve on importance and an order of magnitude above it on probability.

**A third of the reliability budget has nothing behind it.** The rollup closes at 0.972 against a 0.970 target, and 35 per cent of the allowed unreliability is supported by an allocation and a number somebody wrote down. **A reliability number without a stated basis is a wish**, and the basis audit is what says which ones are. Demonstrating the target by flight alone would take 98 flights with no failures, which is why a vehicle reliability is argued from its parts rather than demonstrated as a whole.

**And separating two units beats adding a third by a factor of six.** With `Q = ((1 - beta) q)^n + beta q`, the first term falls as the nth power and the second does not fall at all: **common cause is 93 per cent of a dual redundant set's failure probability at a ten per cent beta.** On the worked case the ideal arithmetic clears the requirement and the real one does not, the third unit buys seven per cent, and moving one rung down the sharing ladder buys forty-five with **no hardware added anywhere.**

---

## Design Ethos

- A reliability number without a stated basis is a wish. Say where it came from.
- Redundancy that shares a failure cause is not redundancy.
- Most failures are not random. They are design escapes, process escapes, or human error.
- The FMECA is only useful if somebody acts on it. An unactioned finding is worse than none.
- Single-point failures should be listed, argued and accepted deliberately, never discovered.
- Read an ordinal product as a sort, not a measurement.

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [ReliabilityOverview.md](docs/ReliabilityOverview.md) | Hub: what the domain found, the two directions of analysis, document index | **written** |
| [FMECA.md](docs/FMECA.md) | The table, both rankings, and why the disagreement is the finding | **written** |
| [FaultTreeAnalysis.md](docs/FaultTreeAnalysis.md) | Cut sets, the rare event approximation, importance, what the tree cannot see | **written** |
| [ReliabilityAllocation.md](docs/ReliabilityAllocation.md) | Series rollup, item count, allocation, the basis audit, why prediction fails | **written** |
| [RedundancyAndFaultTolerance.md](docs/RedundancyAndFaultTolerance.md) | Beta factors, coverage, voting, fail-operational, redundancy that is not | **written** |
| [SinglePointFailures.md](docs/SinglePointFailures.md) | Finding them, why a launch vehicle has so many, accepting one, tracking | **written** |
| [DeratingAndMargins.md](docs/DeratingAndMargins.md) | What derating does, where margin protects and where it does not, stacking | **written** |
| [QualityAndProcessControl.md](docs/QualityAndProcessControl.md) | The three escape types, SPC, why inspection is not quality | **written** |
| [ConfigurationManagement.md](docs/ConfigurationManagement.md) | Three configurations, baselines, change control, as-built drift | **written** |
| [ProblemReporting.md](docs/ProblemReporting.md) | Nonconformance, disposition, root cause, corrective action, trending | **written** |
| [HumanFactors.md](docs/HumanFactors.md) | The failure mode that is a person, error-proofing, procedure design | **written** |
| [StandardsIndex.md](docs/StandardsIndex.md) | Why the list is thin, and what was deliberately not implemented | **written** |
| [ValidationReferences.md](docs/ValidationReferences.md) | No external anchor, and what survives the tables being wrong | **written** |

## Library

| Class | Computes | Status |
|---|---|---|
| `FMECA` | The mode table, both rankings, the disagreement, the mandatory review, the action check | **written** |
| `FaultTree` | Top event probability, minimal cut sets, importance, the single point failure check | **written** |
| `ReliabilityBudget` | Series rollup, allocation, the basis audit, item count, demonstration cost | **written** |
| `RedundancyAnalysis` | Beta factor configuration, the unit sweep, the beta sweep, the lever comparison | **written** |

**Six things were deliberately not built**, and two of them are declines rather than omissions.

**Component failure rate prediction.** A parts count handbook prediction has a long documented history of being optimistic, it describes random failures where most failures are escapes, and **it carries an authority its basis does not support.** The rates here are representative and registered as unvalidated, and the domain says the only honest source is operating experience.

**Quantified human reliability analysis.** The methods exist, their uncertainty is frequently an order of magnitude, and **putting a human error probability into a fault tree alongside a component failure rate makes them look like the same kind of quantity.** [HumanFactors](docs/HumanFactors.md) documents the design responses instead.

Also not built: **quality, configuration management and problem reporting**, which are process and documented as such; **the FTS reliability case**, which [rangeSafetyAndFTS](../rangeSafetyAndFTS/) owns; **derating curves**, which live with the components; and **Bayesian updating**, which needs a prior this repository has no basis for.

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `reliabilityUtils.py`.

---

## Worked example

`codeInterface.py` takes one two stage vehicle through a FMECA, a fault tree, a budget and a redundancy trade.

| Question | Answer |
|---|---|
| FMECA rankings agree | **no** |
| Catastrophic modes buried by the detection column | 2 |
| Single point failures in the tree | 5 |
| Share of the top event they carry | 100 % |
| Rare event overstatement | 0.11 % |
| Dominant subsystem, and its share | propulsion, 53 % |
| Failure budget with evidence behind it | 63 % |
| Flights to demonstrate the target | 98 |
| Common cause share of a dual redundant set | 93 % |
| A third unit against separating the two | 7 % against 45 % |

```bash
python reliabilityAndMissionAssurance/codeInterface.py
```

---

## No anchor, and why that is survivable

**Nothing in this domain was read**, and there is no standard whose reproduction would validate any of it. That is stated at the top of [ValidationReferences](docs/ValidationReferences.md) rather than at the bottom.

**Every result the domain reports follows from the form of an expression rather than the value in it.** That series reliability multiplies is arithmetic. That common cause dominates a redundant set follows from one term falling as the nth power and the other not falling at all. That single point failures dominate a fault tree follows from a cut set of order one occurring at its own probability. That multiplying ordinal ranks produces a sort rather than a measurement follows from what an ordinal scale is.

**A domain whose conclusions are about form does not need a reference to be right, and it cannot use one to become more right.** What it cannot do is tell you the number: every probability in it is representative, and the honest use of the library is to run it on a programme's own rates.

**Three UNVALIDATED entries**, and the third is unusual: the ordinal scales cannot be validated because an ordinal rank is a definition. **That is the point the domain makes rather than a weakness it has**, and it is recorded so the absence is deliberate rather than overlooked.

**IEC 61508 is the largest gap**, because the beta factor is the central quantity and that document carries the method for estimating it rather than a table of values.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [rangeSafetyAndFTS](../rangeSafetyAndFTS/) | Owns the FTS reliability case; this domain supplies the common cause model its redundancy arithmetic leaves out |
| [fluidSystems](../fluidSystems/) | Leak paths, single valves and trapped volumes are the recurring findings the worked case is built from |
| [fluidSystemsTesting](../fluidSystems/fluidSystemsTesting/) | Test evidence is what a reliability claim is built on |
| [mechanismsAndSeparation](../mechanismsAndSeparation/) | Single-shot non-redundant devices dominate the fault tree |
| [manufacturingAndAssembly](../manufacturingAndAssembly/) | Process escapes, lot traceability and first article are the quality half of this |
| [avionicsAndGNC](../avionicsAndGNC/) | Makes the same common mode argument about identical software |

---

Sean Bowman
