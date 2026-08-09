[Home](../README.md) > Propellant Selection

# Propellant Selection

## Contents

- [Overview](#overview)
- [What propulsion already owns](#what-propulsion-already-owns)
- [What this domain adds](#what-this-domain-adds)
- [Density impulse is a tank argument](#density-impulse-is-a-tank-argument)
- [Why hydrogen wins anyway, upstairs](#why-hydrogen-wins-anyway-upstairs)
- [Storability and the ground](#storability-and-the-ground)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

The propellant trade is owned by [propulsion](../../propulsion/docs/PropellantSelection.md), which has a `PropellantCombination` class computing bulk density, density impulse and the volume split across seven combinations.

**This document does not repeat it.** What is here is the part the propulsion-level trade cannot see, which is what a propellant choice does to the tank and therefore to the payload.

---

## What propulsion already owns

Specific impulse, bulk density, density impulse, the oxidiser-to-fuel volume split, chamber temperature, and the storable-against-cryogenic classification. All of it is in [propulsion/docs/PropellantSelection.md](../../propulsion/docs/PropellantSelection.md) with a class behind it.

Duplicating that here would be a second table to keep in agreement with the first, which is the failure this repository has avoided in four other places by pointing rather than copying.

---

## What this domain adds

One thing: **the density trade is a structural coefficient trade, and its magnitude comes from the tank.**

A denser propellant needs a smaller tank for the same mass. A smaller tank has less wall area, so less wall mass, so a better structural coefficient, so more payload. The chain is the same one in [MassChain](MassChain.md) and it runs the other way.

That is why density impulse exists as a figure of merit at all. **It is not a propulsion parameter. It is a vehicle parameter that propulsion computes**, and its whole justification is a tank mass that propulsion does not model.

---

## Density impulse is a tank argument

Specific impulse is what the engine produces. Density impulse, the product of specific impulse and bulk density, is what the vehicle cares about, and the reason is entirely structural.

The clean way to see it: the rocket equation cares about mass ratio, which is indifferent to density. Density only enters through the tank, and the tank only enters through the structural coefficient.

**So a density comparison quoted without a tank model is quoting a figure of merit whose justification has been left out.** The [SizingLoop](MassChain.md) closes that gap: change the propellant density and the tank size, the tank mass, the coefficient and the payload all move, and the sensitivity is computed rather than asserted.

---

## Why hydrogen wins anyway, upstairs

Hydrolox has the worst bulk density of any practical combination and a structural coefficient roughly twice a kerolox stage's, 0.080 to 0.120 against 0.030 to 0.055.

It still wins on upper stages, because the specific impulse gain is larger than the structural loss.

**The reason it wins upstairs and not downstairs is the elasticity ordering in [PerformanceAndPayload](PerformanceAndPayload.md).** Upper stage specific impulse carries an elasticity about two and a half times the first stage's, while the structural penalty applies to both. So the same trade that is favourable on the second stage is marginal on the first, which is exactly the pattern of flying hardware.

That is a satisfying result because it is not obvious and it falls straight out of the two numbers this domain computes.

---

## Storability and the ground

Cryogenic propellants impose a conditioning cost, a boil-off cost and a ground infrastructure cost, none of which appears in a mass fraction.

**The conditioning cost is computed** in [ignitionAndStart](../../propulsion/ignitionAndStart/docs/ChillInAndConditioning.md), where the chill-down band for LOX is 1.9 to one and for LH2 is 8.6 to one. That is propellant loaded, vented and not available for the mission.

**The ground cost is not modelled anywhere in this repository** and it is frequently the decisive one for a small programme. It belongs to [groundSystemsAndOperations](../../groundSystemsAndOperations/).

A kerosene first stage needs no fuel conditioning at all, and half the operational simplicity of a kerolox booster is in that sentence.

---

## Design rules of thumb

- **Take the propellant properties from propulsion.** One table.
- **Justify a density comparison with a tank model**, or do not make it.
- **Expect hydrogen to win upstairs and lose downstairs**, and check the elasticities rather than the folklore.
- **Count the conditioning propellant** in the mass budget. It is loaded and vented.
- **Ask what the ground segment costs** before choosing a cryogen for a small programme.

---

## Failure modes

**A second propellant table.** Two to keep in agreement, and nothing enforcing it.

**Density impulse quoted without a tank model.** The figure of merit's justification is the thing that was left out.

**A first stage propellant chosen on upper stage logic.** The elasticities differ by a factor of two and a half.

**Conditioning propellant omitted from the budget.** It is real mass, loaded and lost.

---

## References

- [propulsion PropellantSelection](../../propulsion/docs/PropellantSelection.md), which owns the trade
- [MassChain](MassChain.md), for the tank the density argument runs through
- [ignitionAndStart ChillInAndConditioning](../../propulsion/ignitionAndStart/docs/ChillInAndConditioning.md)
