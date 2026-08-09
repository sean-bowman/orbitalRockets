[Home](../README.md) > Alternative Cooling

# Alternative Cooling

## Contents

- [Overview](#overview)
- [Film cooling](#film-cooling)
- [What film cooling costs](#what-film-cooling-costs)
- [The trade, worked](#the-trade-worked)
- [Ablative](#ablative)
- [Radiation cooled](#radiation-cooled)
- [Transpiration and dump cooling](#transpiration-and-dump-cooling)
- [Choosing](#choosing)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [What is not validated](#what-is-not-validated)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

[Regenerative cooling](RegenerativeCooling.md) is the default and it has a ceiling. Past that ceiling something else has to carry part of the load, and the alternatives are not interchangeable: each buys wall temperature with a different currency.

| Method | Pays with | Suits |
|---|---|---|
| Film | c* efficiency | Anything regenerative cooling nearly closes |
| Ablative | Mass and life | Short burns, single use, low cost |
| Radiation | Area and temperature limit | Vacuum, low flux, high area ratio |
| Transpiration | Complexity and manufacture | Extreme local flux |
| Dump | Propellant thrown away | Cycles with spare cold flow |

---

## Film cooling

A layer of cooler propellant injected along the wall, either from the outer injector row or from slots down the chamber. It does not remove heat from the wall so much as put something between the wall and the gas.

**It is the answer when regenerative cooling nearly works**, which is most of the time on hydrocarbon engines, and it is why nearly every engine has a different element pattern in its outer row.

The mechanism has a consequence that catches people. Film cooling is not a bulk effect; it is a local layer that gets entrained and consumed as it travels downstream. A film injected at the injector face has largely mixed out by the throat, which is where the flux is highest. **Multiple injection stations are normal**, and a single film at the face is a common way to protect the barrel and lose the throat.

---

## What film cooling costs

The diverted propellant burns at a mixture ratio chosen for the wall rather than for impulse, and some of it does not burn at all.

**The penalty is not the film fraction.** That is the single most common overstatement, and this library made it before it was corrected: an early version asserted the c* loss equalled the fraction diverted. Film propellant partly burns, so the loss is a fraction of the diverted flow, commonly quoted as **0.3 to 0.5 times the film fraction**.

At 8 per cent film that is a 2.4 to 4.0 per cent c* loss rather than 8 per cent, which is a factor of two to three difference in a number that decides the trade.

**That range is an estimate rather than a sourced value**, which is why the tool reports both ends instead of a single figure and why it is in the unvalidated register. A number quoted as a range is honest about what it is; the same number quoted as a value is not.

---

## The trade, worked

The [worked example](../codeInterface.py) chamber cannot be regeneratively cooled: 8.13 MW into 10.34 kg/s of RP-1 gives a 374 K rise to a 664 K outlet against a 575 K limit. The circuit can carry 6.19 MW within the limit, so **film cooling has to remove 24 per cent of the load.**

| Film fraction | Load removed | Circuit closes | c* loss |
|---|---|---|---|
| 2 % | 8 % | No | 0.6 to 1.0 % |
| 5 % | 20 % | No | 1.5 to 2.5 % |
| **8 %** | **32 %** | **Yes** | **2.4 to 4.0 %** |
| 10 % | 40 % | Yes | 3.0 to 5.0 % |
| 15 % | 60 % | Yes | 4.5 to 7.5 % |

**Eight per cent closes it, at a cost of 7 to 11 seconds of specific impulse on a 277 second engine.**

Two things about that result are worth stating plainly.

**It is not an optimisation.** The engine does not work without it. Film cooling on a small high pressure hydrocarbon engine is a requirement, and treating it as a refinement to be added late means designing an engine that cannot be built.

**The effectiveness is an assumption.** The four-to-one figure relating film fraction to load removed is stated in the example's configuration and is not sourced. The trade moves with it, and the example says so where it uses it.

---

## Ablative

The wall is consumed rather than cooled. Covered in depth by [thermalManagement](../../../thermalManagement/docs/AeroheatingAndTPS.md), which owns the ablation energy balance; what matters here is when it is the right answer for a chamber.

**Short burns, single use, low cost, and no coolant available.** Upper stage engines with modest chamber pressure, and almost every small pressure-fed engine. The mass is carried once and the thermal analysis is simple.

**The limit is throat erosion.** The throat area grows as the liner recedes, chamber pressure falls with it, and thrust and mixture ratio drift through the burn. A chamber that is thermally fine can still be performance-unacceptable, and the erosion rate rather than the wall temperature is what sizes it.

---

## Radiation cooled

The wall runs hot and radiates to space. No coolant, no consumable, no complexity, and a hard flux ceiling because `sigma T^4` is all the capacity there is.

At a wall temperature of 1600 K, achievable in a refractory alloy, radiation carries about 0.32 MW/m^2 at an emissivity of 0.85. **That is 0.6 per cent of the 52.1 MW/m^2 at the throat of the worked example chamber**, which is why radiation cooling appears on nozzle extensions and never on a chamber.

Where it does work it works very well: the area ratio is high, the flux is low, the surface is already there, and the alternative is carrying coolant into vacuum.

---

## Transpiration and dump cooling

**Transpiration** pushes coolant through a porous wall so the wall is cooled and the boundary layer is thickened at once. It is the most effective method known per unit coolant and it is a manufacturing problem: a porous wall that stays porous, does not clog, and has structural strength. Additive manufacture has made it more accessible than it was.

**Dump cooling** runs coolant through the jacket and throws it overboard rather than burning it. It costs the whole specific impulse of the dumped flow, so it only makes sense where there is cold flow with nothing better to do, which in practice means some expander and gas generator arrangements.

---

## Choosing

The decision is usually forced rather than chosen, and the order is:

1. **Can regenerative cooling close on its own?** Check capability first. If yes, stop.
2. **Does it nearly close?** Film cooling, and size the fraction from the shortfall.
3. **Is the burn short and single use?** Ablative, sized on throat erosion.
4. **Is it a nozzle extension in vacuum?** Radiation.
5. **Is the local flux extreme and the rest closed?** Transpiration at that station only.

**Step one is the one that gets skipped**, and skipping it is how a chamber gets a channel design before anyone has checked whether a channel can work.

---

## Design rules of thumb

- **Size film cooling from the regenerative shortfall**, not from a rule of thumb.
- **Inject film at more than one station.** A film at the face has mixed out by the throat.
- **Cost film cooling at 0.3 to 0.5 of the fraction diverted**, not at the fraction itself.
- **Size an ablative on erosion, not on wall temperature.** The performance drift is what ends the burn.
- **Do not expect radiation to carry a chamber.** It is two orders short at the throat.
- **Treat film cooling as a requirement on a small high pressure hydrocarbon engine**, not as a refinement.

---

## Failure modes

**Film cooling costed at the full film fraction.** Overstates the penalty by two to three times and can wrongly reject the only workable design.

**A single film station at the injector face.** Protects the barrel, loses the throat.

**Film cooling added late.** It changes the injector, the mixture ratio distribution and the performance, so it is not an adjustment.

**Ablative sized on temperature.** The throat erodes, chamber pressure falls, and the engine drifts off its design point while the wall is still intact.

**Radiation cooling proposed for a chamber.** Two orders of magnitude short.

**Transpiration assumed manufacturable.** A porous wall that clogs is worse than no wall, because it fails locally and without warning.

---

## Worked numbers

The [worked example](../codeInterface.py) chamber, 100 kN LOX/RP-1 at 10 MPa.

| Quantity | Value |
|---|---|
| Heat load | 8.13 MW |
| Regenerative circuit capacity within the coolant limit | 6.19 MW |
| Load that film cooling must remove | 24 % |
| Film fraction that closes it | 8 % |
| c* penalty at that fraction | 2.4 to 4.0 % |
| Impulse cost on a 277 s engine | 7 to 11 s |
| Radiation capacity at a 1600 K wall, emissivity 0.85 | 0.32 MW/m^2 |
| Peak throat flux for comparison | 52.1 MW/m^2 |

---

## What is not validated

**The film cooling effectiveness.** The four-to-one relationship between film fraction and load removed is an assumption stated in the example configuration. The trade moves with it.

**The c* penalty range.** The 0.3 to 0.5 multiplier is commonly quoted and no single source was found for it. It is reported as a range for that reason.

Both are registered in [validation/referenceCases.py](../../../validation/referenceCases.py). See [ValidationReferences](ValidationReferences.md).

---

## Standards

| Standard | What it gives you |
|---|---|
| NASA SP-8124 | Liquid rocket engine self-cooled combustion chambers, the ablative and radiation reference |
| NASA SP-8087 | Fluid-cooled combustion chambers, which covers film as an adjunct |
| ASTM E285 | Oxyacetylene ablation testing |
| NASA-STD-6016 | Materials and processes, for the refractory and ablative material selection |

---

## Tool interface

Film cooling is sized from the regenerative shortfall, so the two classes are used together.

```python
from RegenerativeCooling import RegenerativeCooling
from Injector import Injector

cooling = RegenerativeCooling()
cooling.setInputs({'combination': 'LOX/RP-1', 'chamberPressure': 10.0e6,
                   'throatDiameter': 0.0906, 'coolantFlow': 10.34})

capability = cooling.checkCoolantCapability()

if not capability['feasible']:

    injector = Injector()
    injector.setInputs({'combination': 'LOX/RP-1', 'chamberPressure': 10.0e6,
                        'oxidiserFlow': 26.47, 'fuelFlow': 10.34,
                        'filmFraction': 0.08})

    wall = injector.checkWallCompatibility()
    print(wall['efficiencyLossLower'], wall['efficiencyLossUpper'])
```

The [worked example](../codeInterface.py) runs the full sweep and reports which fraction closes.

---

## References

- NASA SP-8124, *Liquid rocket engine self-cooled combustion chambers*
- NASA SP-8087, *Liquid rocket engine fluid-cooled combustion chambers*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- Sutton and Biblarz, *Rocket Propulsion Elements*, chapter 8
- Yang, Habiballah, Hulka and Popp, *Liquid Rocket Thrust Chambers*
