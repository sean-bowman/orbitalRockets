[Home](../README.md) > Process Route Selection

# Process Route Selection

## Contents

- [Overview](#overview)
- [The four axes](#the-four-axes)
- [Buy-to-fly](#buy-to-fly)
- [The allowable knockdown](#the-allowable-knockdown)
- [The routes](#the-routes)
- [Geometric feasibility](#geometric-feasibility)
- [The ten sub-domains](#the-ten-sub-domains)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The alloy decision and the process decision are usually made separately, and they should not be. **The same alloy through two routes is two materials**, because the route sets the allowable knockdown, and the knockdown frequently matters more than the difference between two candidate alloys.

A cast part with no qualified process carries a casting factor of 2.0, which halves the allowable and doubles the material needed to carry the same load. No alloy substitution recovers that, and qualifying the casting process is usually cheaper than switching to titanium.

That trade is invisible unless the routes are compared side by side with the knockdowns attached.

---

## The four axes

| Axis | What it drives | Where the number comes from |
|---|---|---|
| **Buy-to-fly** | Raw material cost, machining time, scrap value | Route geometry |
| **Allowable knockdown** | The wall thickness, and therefore the mass | Process qualification state |
| **Lead time** | The programme schedule | Stock availability plus process time |
| **Dimensional capability** | Whether the route can make the part at all | Tolerance grade and minimum wall |

**Dimensional capability screens first**, because a route that cannot hold the wall thickness is not a cheap option, it is not an option.

**Cost is expressed as a ratio, never as currency.** Absolute prices are wrong within a quarter, and a number with a currency symbol invites a decision it cannot support. Every cost figure carries the basis date it came from.

---

## Buy-to-fly

The mass of stock consumed per unit mass of finished part. It drives raw material cost, machining time and scrap value simultaneously, and **on an expensive alloy it dominates everything else.**

| Route | Buy-to-fly |
|---|---|
| **LPBF as-built** | **1.2 : 1** |
| Investment cast | 1.6 : 1 |
| Sand cast | 1.8 : 1 |
| Spun and welded | 2.0 : 1 |
| Wire arc additive | 2.0 : 1 |
| Centrifugal cast | 2.2 : 1 |
| Flow formed | 2.5 : 1 |
| Ring rolled | 3.0 : 1 |
| Closed die forged | 4.0 : 1 |
| **Machined from plate** | **8.0 : 1** |

**Machining from plate throws away seven eighths of the stock.** On 6061 at 0.6 times the 316L index that is irrelevant; on Ti-6Al-4V at 8.5 or GRCop-42 at 22 it is the whole cost of the part.

**This is the defining economic property of additive manufacturing** and the reason it wins on expensive alloys despite a high process cost per kilogram. It is also why the buy-to-fly comparison, not the per-kilogram price, is the right way to compare routes.

---

## The allowable knockdown

| Route | Knockdown | Factor |
|---|---|---|
| Machined from wrought | none | 1.00 |
| Forged | none | 1.00 |
| Flow formed | none | 1.00 |
| **Electron beam welded** | Weld | 0.95 |
| Additive, HIP and machined | Build direction | 0.90 |
| Friction stir welded | Weld | 0.80 |
| **Cast, qualified process** | Casting factor 1.0 | **1.00** |
| **Cast, partial qualification** | Casting factor 1.33 | **0.75** |
| **Cast, no qualification** | Casting factor 2.0 | **0.50** |
| Additive, as-built surface | Surface | 0.75 |

**The casting factor ladder is the strongest argument in the table.** Per NASA-STD-5001 and 6016 the factor falls to 1.0 with a qualified process, 100 percent volumetric NDE and three sample lots. Getting there is a real programme investment, and it recovers the entire allowable.

**Knockdowns compound.** An as-built additive part carries both the build direction and the surface knockdown, giving 0.675 together. HIP and machining remove the surface term and most of the build direction term, which is why a flight additive part is HIPed and machined rather than as-built.

**A knockdown is a mass penalty.** For a membrane, the material needed scales as the inverse of the allowable factor, so a 0.5 factor is exactly twice the material.

---

## The routes

| Route | Min wall | Max size | Tolerance | Ra | Lead adder |
|---|---|---|---|---|---|
| Machined from plate | 0.8 mm | 2.0 m | IT7 | 1.6 um | 4 wk |
| Closed die forged | 2.5 mm | 1.5 m | IT7 | 1.6 um | 24 wk |
| Ring rolled | 5.0 mm | 6.0 m | IT9 | 3.2 um | 18 wk |
| **Flow formed** | **0.6 mm** | 3.0 m | IT9 | 1.6 um | 14 wk |
| Spun and welded | 0.8 mm | 4.0 m | IT11 | 3.2 um | 12 wk |
| Investment cast | 1.5 mm | 1.0 m | IT11 | 3.2 um | 20 wk |
| Sand cast | 5.0 mm | 5.0 m | IT14 | 25 um | 12 wk |
| Centrifugal cast | 4.0 mm | 4.0 m | IT12 | 12.5 um | 14 wk |
| **LPBF as-built** | **0.4 mm** | **0.4 m** | IT12 | 20 um | **6 wk** |
| LPBF HIP and machined | 0.6 mm | 0.4 m | IT8 | 1.6 um | 10 wk |
| **Wire arc additive** | 6.0 mm | **6.0 m** | IT11 | 25 um | 8 wk |

**LPBF has the finest minimum wall and the smallest maximum size**, which is the fundamental constraint of the process: build volume. Wire arc additive inverts both, trading a coarse minimum wall for essentially unlimited size.

**Flow forming is underrated for thin walled cylinders and domes.** Cold work raises the strength of the formed section, wall thickness control is excellent, and the buy-to-fly beats every wrought route. It needs a mandrel per geometry, which is why it suits production rather than one-offs.

---

## Geometric feasibility

Three screens, applied before any cost comparison.

**Minimum wall.** Can the route produce the section the design requires? Sand casting cannot hold 0.5 mm and no amount of process development changes that.

**Maximum size.** Does the part fit? An LPBF machine with a 400 mm build volume cannot make a 600 mm part, and splitting it introduces a joint with its own knockdown.

**Tolerance.** Can the route hold the dimension? An IT14 sand casting holds 870 um on a 100 mm dimension, so a 500 um requirement screens it out **on dimensions before the allowable ever enters the argument.**

**The usual resolution of a tolerance failure is not to change route.** It is to add a finish machining operation to a near-net route, which keeps the buy-to-fly advantage and pays for a second setup. The comparison table treats those as separate routes for exactly that reason.

---

## The ten sub-domains

Each route in this document belongs to a sub-domain, and each sub-domain supplies the numbers for its own row.

| Sub-domain | Library | What it computes |
|---|---|---|
| [additiveLPBF](../additiveLPBF/) | Yes | Energy density, process map, build time, DFAM checks, qualification |
| [additiveOther](../additiveOther/) | Docs only | DED, WAAM, EB-PBF, binder jet, cold spray |
| [spinCasting](../spinCasting/) | Yes | G-factor, solidification, inclusion migration depth |
| [castingProcesses](../castingProcesses/) | Yes | Chvorinov, riser sizing, casting factor selection |
| [wroughtMaterials](../wroughtMaterials/) | Docs only | Product form, grain flow, temper, the ST story |
| [formingProcesses](../formingProcesses/) | Yes | Bend radius, springback, forming limit, work hardening |
| [machiningProcesses](../machiningProcesses/) | Yes | Taylor tool life, chatter lobes, thin wall deflection, distortion |
| [joiningProcesses](../joiningProcesses/) | Docs only | Brazing, adhesive, mechanical. Welding is in fluidSystems |
| [postProcessing](../postProcessing/) | Yes | Peening, chem mill, electropolish, coatings, alpha case |
| [extrusionHoning](../extrusionHoning/) | Yes | Media rheology, flow split, Ra decay, edge radius |

**Three are deliberately docs-only.** `wroughtMaterials` because product form, temper and grain direction are database axes rather than computations. `joiningProcesses` because [fluidSystems Weld.py](../../fluidSystems/fluidSystemsLibrary/Weld.py) already does joint efficiency and HAZ knockdown, and duplicating it would create the drift this repository works to avoid. `additiveOther` because each process is one or two equations that belong in the route table rather than in a class.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Choose the alloy and the route together | The same alloy through two routes is two materials |
| Screen geometry before cost | An infeasible route is not a cheap route |
| Buy-to-fly dominates on expensive alloys | 8:1 on titanium is the whole cost |
| A knockdown is a mass penalty | Factor 0.5 means twice the material |
| Qualify the casting process | It recovers the entire allowable |
| Additive flight parts are HIPed and machined | As-built carries two knockdowns |
| A tolerance failure means add a finish operation | Not change route |
| Cost as a ratio with a basis date | Never currency |
| Two routes within 10 percent are a tie | Decide on supplier capability instead |

---

## Failure modes

**Alloy chosen, then route chosen.** The knockdown was never in the trade.

**An unqualified casting used at the qualified allowable.** Half the strength assumed.

**An additive part designed as-built and flown.** Two compounding knockdowns and an uninspectable internal passage.

**A route selected on per-kilogram price.** Buy-to-fly inverts the answer.

**A part that does not fit the build volume, discovered late.** The split introduces a joint nobody planned.

**A near-net route abandoned over tolerance.** A finish operation would have kept the buy-to-fly advantage.

**Lead time discovered after the design freeze.** A 24 week forging on the critical path.

---

## Worked example

From [`codeInterface.py`](../codeInterface.py), routes for the 1.23 kg Ti-6Al-4V helium bottle, 2.62 mm wall, 183 mm diameter, 300 um tolerance:

| Route | Buy-to-fly | Allowable | Effective mass | Rel cost | Lead |
|---|---|---|---|---|---|
| **Investment cast** | 1.6:1 | 0.75 | 1.64 kg | 21.5 | 28 wk |
| **Spun and welded** | 2.0:1 | 0.95 | 1.29 kg | 24.7 | 20 wk |
| **LPBF HIP and machined** | 1.4:1 | 0.90 | 1.36 kg | 26.9 | 18 wk |
| Flow formed | 2.5:1 | 1.00 | 1.23 kg | 30.4 | 22 wk |
| Machined from plate | 8.0:1 | 1.00 | 1.23 kg | 89.0 | 12 wk |

**Machining from plate is nearly three times the cost of the cheapest route** and it is the fastest, because there is no tooling and no process qualification. On a single article that speed often wins anyway, which is why prototypes are machined and production parts are not.

**The investment cast route is cheapest and heaviest.** The 0.75 casting factor costs 33 percent more material, and qualifying the process to a factor of 1.0 would make it cheapest and lightest at once.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-5001** | Structural design and test factors of safety, including casting factors |
| **NASA-STD-6016** | Materials and processes requirements for spacecraft |
| NASA-STD-6030 | Additive manufacturing requirements for spaceflight |
| MSFC-STD-3716 | Standard for additively manufactured spaceflight hardware |
| **ISO 286** | Geometrical product specifications, tolerance grades |
| ISO 8062 | Casting dimensional tolerances and machining allowances |
| ASTM E1417 / E1444 | Penetrant and magnetic particle examination |
| **ASTM E1742** | Radiographic examination |
| AMS 2175 | Castings, classification and inspection |

---

## Tool interface

```python
from ProcessComparison import ProcessComparison

comparison = ProcessComparison()
comparison.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed',
                      'finishedMass': 1.228,
                      'minimumWallThickness': 0.00262,
                      'characteristicSize': 0.1834,
                      'requiredTolerance': 0.30e-3,
                      'quantity': 1})

comparison.screenRoutes()      # geometric feasibility, with reasons for every rejection
comparison.compareRoutes()     # the full trade
comparison.selectRoute('minimum cost')
comparison.selectRoute('minimum mass')
print(comparison.generateReport())
```

Lookup table: `ProcessComparison.PROCESS_ROUTES`.

---

## References

1. NASA-STD-5001B, *Structural Design and Test Factors of Safety for Spaceflight Hardware*.
2. Campbell, F. C., *Manufacturing Technology for Aerospace Structural Materials*, Elsevier, 2006.
3. Boothroyd, G., Dewhurst, P. and Knight, W., *Product Design for Manufacture and Assembly*, 3rd ed., CRC Press, 2010.
4. Gradl, P. R. et al., "Metal Additive Manufacturing in Aerospace: A Review", *Materials and Design*, Vol. 209, 2021.
5. Kalpakjian, S. and Schmid, S., *Manufacturing Engineering and Technology*, 7th ed., Pearson, 2013.
