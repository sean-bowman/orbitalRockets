[Home](../README.md) > Architecture Overview

# Architecture Overview

## Contents

- [Overview](#overview)
- [The sizing loop](#the-sizing-loop)
- [What this domain found](#what-this-domain-found)
- [Document index](#document-index)
- [What this domain does not do](#what-this-domain-does-not-do)
- [Design rules of thumb](#design-rules-of-thumb)
- [References](#references)

---

## Overview

This domain sits above the others and is where the mass chain running through all of them either closes or does not.

It answers one question, which is whether a vehicle exists that meets a payload requirement, and it answers a second that turns out to matter more: what the decisions being made in the subsystems are worth in payload.

---

## The sizing loop

The structural coefficient is the number a vehicle architecture lives or dies by, and it is an output rather than an input.

```
guess a dry mass
    -> stage propellant from the rocket equation
    -> tank volume from the propellant
    -> tank wall from the pressure and the volume
    -> tank mass, plus the fixed masses
    -> a new dry mass
```

That loop either converges or it diverges, and a vehicle that diverges does not close. See [MassChain](MassChain.md).

**A design that does not close cannot be optimised.** Optimising an open design is the most common wasted effort in conceptual work, and it happens because a diverging loop stopped at an iteration limit looks like a converged one.

---

## What this domain found

Four results, in descending order of how much they change what somebody should do.

**A kilogram in the first stage tank costs eleven kilograms at liftoff.** One bar of feed system pressure drop is worth 730 kg on a 40 tonne vehicle. See [MassChain](MassChain.md).

**Payload elasticity is inversely proportional to payload fraction.** This domain's own stated ethos said small upstream errors are large payload errors, and that is a claim about marginal vehicles rather than about rockets. On a healthy design a one per cent dry mass error costs a third of a per cent of payload; on a marginal one it costs one and a half. See [PerformanceAndPayload](PerformanceAndPayload.md).

**The staging optimum is flat and the real vehicle is not at it.** Ten per cent either way costs 0.20 per cent of liftoff mass, and Falcon 9 sits four per cent off its own optimum for reasons the optimisation cannot see. See [RocketEquationAndStaging](RocketEquationAndStaging.md).

**The loss budget does not choose the liftoff thrust to weight.** It wants 2.58 and everything flies near 1.35. It sets a floor, not a target. See [ThrustToWeightAndSizing](ThrustToWeightAndSizing.md).

Three of those four say that a thing widely treated as a design decision is not one, and that the real leverage is somewhere less glamorous. That is the shape of the domain.

---

## Document index

| Document | Covers |
|---|---|
| [MassChain](MassChain.md) | Feed pressure to payload, the amplification, and why it crosses domains |
| [RocketEquationAndStaging](RocketEquationAndStaging.md) | Tsiolkovsky, the bookkeeping, optimal staging and why it is flat |
| [MassFractionsAndEstimating](MassFractionsAndEstimating.md) | Where mass estimates come from, growth allowance against margin |
| [ThrustToWeightAndSizing](ThrustToWeightAndSizing.md) | Liftoff thrust to weight, engine count, engine-out |
| [TrajectoryBasics](TrajectoryBasics.md) | The delta-V budget, the losses, and what is not modelled |
| [PerformanceAndPayload](PerformanceAndPayload.md) | Payload sensitivity, and the ethos this domain corrected |
| [ConfigurationTrades](ConfigurationTrades.md) | Diameter, length, tank arrangement, fairing |
| [MassProperties](MassProperties.md) | Centre of gravity, inertia, and growth that is not evenly distributed |
| [ReusabilityImpacts](ReusabilityImpacts.md) | The recovery penalty, measured rather than modelled |
| [PropellantSelection](PropellantSelection.md) | What this domain adds to the propulsion trade, which is tank mass |
| [CostAndProducibility](CostAndProducibility.md) | The axis mass-based design cannot see |
| [StandardsIndex](StandardsIndex.md) | The standards, and the ones not read |
| [ValidationReferences](ValidationReferences.md) | One hardware source, exact closed forms, three gaps |

---

## What this domain does not do

**It chooses between architectures on mass alone.** Cost, schedule, manufacturability and the recovery mode that pays for itself over a hundred flights are all outside it, and a vehicle chosen on mass is chosen on one axis of several. See [CostAndProducibility](CostAndProducibility.md).

**It does not integrate a trajectory.** The ascent budget is a loss model, not an optimisation with a steering law. See [TrajectoryBasics](TrajectoryBasics.md).

**It does not model parallel staging or crossfeed.** Both are named in [RocketEquationAndStaging](RocketEquationAndStaging.md) with what they buy, and neither is computed.

**It does not estimate subsystem masses from first principles.** The non-tank fraction is a constant, and building it from the domains that own the parts is the most tractable gap in the register.

---

## Design rules of thumb

- **Close the design before optimising it.** An open design has no payload to optimise.
- **Price subsystem decisions through the chain.** A component trade in kilograms is wrong by the amplification factor.
- **Spend effort where the elasticity is**, which is the structural coefficient rather than the staging split.
- **Keep growth allowance and margin apart.** Confusing them leaves a programme with neither.
- **State what the vehicle was not chosen on.** Mass is one axis.

---

## References

- Humble, Henry and Larson, *Space Propulsion Analysis and Design*
- Sutton and Biblarz, *Rocket Propulsion Elements*, the vehicle chapters
- Curtis, *Orbital Mechanics for Engineering Students*
- [ValidationReferences](ValidationReferences.md)
