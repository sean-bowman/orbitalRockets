[Home](../README.md) > Fairing Separation

# Fairing Separation

## Contents

- [Overview](#overview)
- [The two arrangements](#the-two-arrangements)
- [Clearance](#clearance)
- [When to jettison](#when-to-jettison)
- [Contamination](#contamination)
- [The shock, again](#the-shock-again)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

A fairing is the largest single-shot mechanism on a launch vehicle, it operates closest to the payload, and its failure mode is the most expensive available.

---

## The two arrangements

**Clamshell.** Two halves hinged at the base, rotating outward and away. The hinge controls the trajectory, which is the main advantage: the halves cannot go anywhere unexpected. It costs a hinge that has to carry flight loads and then let go, and the halves sweep a large volume as they rotate.

**Fully separating.** The halves are pushed clear without a hinge. Less hardware, less mass, and the trajectory is controlled only by the initial push, so the clearance analysis carries all the risk.

The same [tipoff and recontact](SeparationSystems.md) arithmetic applies to both, with one difference that matters: **a fairing half is not a compact body.** Its centre of gravity is a long way from the push points and its inertia is large and asymmetric, so a small force imbalance produces a large rotation.

---

## Clearance

The clearance problem is harder than a stage separation for three reasons.

**The payload is inside.** A fairing half that rotates inward at any point in its travel contacts what it was protecting.

**The half is flexible.** A large composite shell deflects under the separation loads, and the deflected shape is what has to clear, not the drawing.

**The relative motion is large.** A half sweeps several metres, so a small angular error at the start is a large position error at the end.

None of that is modelled here. [SeparationSystem](SeparationSystems.md) computes a rigid-body clearance for a compact body, and applying it to a fairing half would be using it outside its scope. **The right tool is a multi-body dynamics analysis with a flexible shell**, and that is named here rather than approximated.

---

## When to jettison

The jettison time is a trade between two costs.

**Jettison early** and the vehicle stops carrying the fairing mass, which is worth payload through the [mass chain](../../vehicleArchitecture/docs/MassChain.md). Fairing mass is dropped before the second stage burn, so its amplification is lower than a first stage tank kilogram but far from negligible.

**Jettison late** and the payload is protected for longer from aerodynamic heating and from free molecular flow.

The constraint is a **free molecular heating limit** on the payload, usually stated as a flux the payload can tolerate, and it falls rapidly with altitude. The jettison happens as soon as that limit is met, which is typically a few minutes into flight and well into the second stage burn.

That is a trajectory and thermal calculation rather than a mechanism one, and it belongs to [vehicleArchitecture](../../vehicleArchitecture/) and [thermalManagement](../../thermalManagement/).

---

## Contamination

A fairing separation happens a few metres from a payload that may have optical surfaces, and anything released goes with it.

**Pyrotechnic products** unless the device is contained. This is the strongest single argument for [non-explosive actuators](NonExplosiveActuators.md) on a fairing.

**Particulate** shaken loose from the fairing interior by the shock and the acoustic environment. Cleanliness of the fairing interior is a payload requirement rather than a fairing one, and it is verified before encapsulation.

**Debris from the separation joint itself.** Frangible joints fracture, and containment is what makes them acceptable near a payload.

---

## The shock, again

The fairing separation shock reaches the payload more directly than any other event, because the payload adapter is close to the separation plane and the path is short.

As everywhere in this domain, **the magnitude is not predicted here**. What can be said is structural: a longer path with more joints attenuates shock, and the payload adapter is the one place a designer can add both.

---

## Design rules of thumb

- **Use a multi-body flexible analysis for fairing clearance.** A rigid-body check is out of scope.
- **Set the jettison time from the free molecular heating limit**, then check the mass benefit.
- **Prefer contained or non-explosive release near a payload.**
- **Put attenuation in the adapter.** It is the shortest path to the payload.
- **Verify fairing interior cleanliness before encapsulation.** Afterwards is too late.

---

## Failure modes

**Rigid-body clearance applied to a flexible shell.** The deflected shape is what clears.

**A half rotating inward.** The payload is inside the swept volume.

**Jettison set on mass alone.** The heating limit is the binding constraint.

**Uncontained pyrotechnic products near an optic.** The contamination is the mission.

**Adapter designed without attenuation.** The shortest shock path to the most sensitive item.

---

## References

- [SeparationSystems](SeparationSystems.md), for the arithmetic this extends beyond
- [vehicleArchitecture ConfigurationTrades](../../vehicleArchitecture/docs/ConfigurationTrades.md), for fairing sizing
- [thermalManagement](../../thermalManagement/), for the free molecular heating limit
- Conley, *Space Vehicle Mechanisms: Elements of Successful Design*
