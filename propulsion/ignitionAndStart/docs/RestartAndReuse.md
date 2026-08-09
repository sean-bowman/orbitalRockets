[Home](../README.md) > Restart and Reuse

# Restart and Reuse

## Contents

- [Overview](#overview)
- [What restart actually demands](#what-restart-actually-demands)
- [The igniter is the visible constraint and the smallest one](#the-igniter-is-the-visible-constraint-and-the-smallest-one)
- [Settling, which has no substitute](#settling-which-has-no-substitute)
- [Re-conditioning without a ground cart](#re-conditioning-without-a-ground-cart)
- [Reuse is a different requirement from restart](#reuse-is-a-different-requirement-from-restart)
- [What this sub-domain does not model](#what-this-sub-domain-does-not-model)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Restart is the requirement that changes an engine architecture more than any other single line in a specification, and it usually arrives late.

This document is deliberately shorter than its neighbours and it is mostly qualitative, because most of what restart demands is not computable from the quantities this repository carries. Saying that plainly is better than filling the space.

---

## What restart actually demands

Five things, in rough order of how much trouble each causes.

**An igniter that can fire again.** The visible one, and the easiest.

**Propellant settled over the outlets.** In free fall there is no such thing as the bottom of a tank.

**Hardware re-conditioned.** A cryogenic engine that has been coasting is not cold any more, and there is no ground cart.

**A purge between starts.** Residual propellant left in a hot chamber is a mixture waiting for an ignition source.

**A start sequence that works from an unknown thermal state.** The ground start begins from a state that was measured for four minutes. The second start begins from wherever the coast left things.

---

## The igniter is the visible constraint and the smallest one

Restart removes every consumable device from the selection. A pyrotechnic charge or a hypergolic cartridge is spent once, so `n` starts means `n` installations, and the mass and complexity of that grows linearly while the alternatives do not.

See [IgnitionSystems](IgnitionSystems.md) for the selection, where three starts cuts the viable list from four devices to two.

But an unlimited-restart igniter is a solved problem, and it has been since the RL10. The other four items on the list above are the ones that decide whether a stage can restart, and none of them is in the igniter.

---

## Settling, which has no substitute

Before a restart in free fall the propellant has to be over the tank outlets, and the only ways to do that are to accelerate the vehicle or to constrain the liquid.

**Ullage motors or settling thrusters** accelerate the whole stage briefly. Simple, and they consume propellant and hardware per restart.

**Propellant management devices** use surface tension to hold liquid at the outlet. No consumable, and they impose a limit on the accelerations the stage may see.

Either way it is a tank and structures problem rather than an engine problem, which is why it is named here and owned in [vehicleArchitecture](../../../vehicleArchitecture/) rather than modelled in this sub-domain.

**A restart requirement is a tank requirement first and an engine requirement second.** That is the single most useful thing on this page.

---

## Re-conditioning without a ground cart

An engine that starts on the ground has been conditioned by an hour of recirculation flow from a facility that can afford to vent. An engine restarting after a coast has neither the time nor the propellant to spare, and it has been sitting in sunlight.

The enthalpy balance in [ChillInAndConditioning](ChillInAndConditioning.md) still applies, but two things change. The metal mass to be cooled is smaller, because only what warmed back up needs re-cooling. And the method is forced toward the fast end of the band, because there is no time for a trickle chill, which pushes the propellant cost toward the upper bound.

**For a hydrogen stage that is the difference between the two ends of a factor of nine.** The chill-down band that looked like an optimisation on the ground becomes a hard cost in flight.

---

## Reuse is a different requirement from restart

Restart is within a mission. Reuse is between missions, and the two share almost nothing.

Restart is about state: settled propellant, cold hardware, a purged chamber. Reuse is about accumulated damage: thermal cycles on the chamber liner, low cycle fatigue on the turbine, coking in the cooling passages, and whether any of it can be inspected without disassembly.

**An engine that restarts five times in a mission is not thereby reusable, and a reusable engine need not restart at all.** Conflating them is common and it leads to the wrong hardware being qualified.

The damage accumulation half belongs to [aerospaceMaterials](../../../aerospaceMaterials/) and [reliabilityAndMissionAssurance](../../../reliabilityAndMissionAssurance/), and this sub-domain owns only the transient that each cycle consists of.

---

## What this sub-domain does not model

Recorded rather than implied, on the same principle as the rest of the repository.

**Settling and propellant management.** Named above, owned elsewhere, not computed.

**Thermal state after a coast.** It depends on the attitude, the duration and the surface properties, which is a thermal analysis rather than a propulsion one. See [thermalManagement](../../../thermalManagement/).

**Purge gas quantity per restart.** Computable in principle from the free volume and the required dilution, and not computed here because the required dilution has no source this repository has found.

**Cycle life.** Not a transient calculation.

---

## Design rules of thumb

- **Fix the restart count before selecting anything.** It removes device classes rather than penalising them.
- **Ask about the tank first.** Settling decides restart more often than the igniter does.
- **Budget re-conditioning at the fast end of the band.** There is no time for a trickle chill in flight.
- **Purge between starts.** A hot chamber with residual propellant is an ignition source looking for a mixture.
- **Do not confuse restart with reuse.** They qualify different hardware against different failure modes.

---

## Failure modes

**A restart requirement added after igniter selection.** It invalidates the selection outright.

**Restart assumed to be free because the igniter supports it.** The igniter is the smallest of the five requirements.

**Ground conditioning numbers applied to an in-flight restart.** The method is forced fast and the propellant cost moves toward the upper bound.

**No purge between starts.** Residual propellant in a hot chamber.

**Reuse claimed on the strength of restart capability.** Different failure modes, different qualification.

---

## References

- Sutton and Biblarz, *Rocket Propulsion Elements*, the upper stage and restart discussions
- Biggs, *Space Shuttle Main Engine: The First Ten Years*, part 3, for the ground conditioning baseline
- NASA SP-8080, *Liquid rocket pressure regulators, relief valves, check valves, burst disks and explosive valves*, for the purge and isolation hardware
