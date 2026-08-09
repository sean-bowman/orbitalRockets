[Home](../README.md) > Standards Index

# Standards Index

## Contents

- [Overview](#overview)
- [Mass properties](#mass-properties)
- [Reference vehicles](#reference-vehicles)
- [Textbooks that function as standards](#textbooks-that-function-as-standards)
- [What was not read](#what-was-not-read)
- [References](#references)

---

## Overview

Vehicle architecture has fewer governing standards than the domains below it, and that is not an accident. A tank has a pressure vessel code; a vehicle has a customer.

What exists is mass properties practice, interface documents, and a body of textbook method that functions as a standard because everyone uses the same equations.

---

## Mass properties

**AIAA S-120, Mass Properties Control for Space Systems.** The governing practice for mass growth allowance, margin policy and mass properties reporting through a programme. It is the source of the *shape* of the growth allowance table in this library: an allowance applied by design maturity, because estimates at that maturity have historically grown by about that much.

**ANSI/AIAA mass properties standards** more broadly, covering reporting formats and the definitions of estimate, prediction and allocation that [MassFractionsAndEstimating](MassFractionsAndEstimating.md) uses.

**The specific percentages in this library were not taken from the standard**, which was not read. That is registered in [ValidationReferences](ValidationReferences.md) as `massGrowthAllowance`, and it is the single most closable gap in this domain: the standard exists, it is obtainable, and carrying its table with a citation is a bounded piece of work.

---

## Reference vehicles

Not standards, but they function as the check that the method is right.

**Falcon 9 Block 5 published stage masses**, used in [ValidationReferences](ValidationReferences.md) as the only external anchor this domain has. Published stage masses through the rocket equation have to land near a real mission delta-V or the bookkeeping is wrong.

The general principle is worth stating: **in a domain whose physics is exact and whose inputs are estimates, a reference vehicle validates the accounting rather than the models.**

---

## Textbooks that function as standards

**Humble, Henry and Larson, Space Propulsion Analysis and Design.** The standard reference for conceptual vehicle sizing, mass estimating relationships and the sizing loop structure. Where this domain has a method rather than an equation, it is usually this method.

**Curtis, Orbital Mechanics for Engineering Students.** The Lagrange multiplier staging condition in [RocketEquationAndStaging](RocketEquationAndStaging.md) follows Curtis.

**Sutton and Biblarz, Rocket Propulsion Elements.** The flight performance chapter for the loss budget shape.

These are cited as sources rather than as validation. A textbook agreeing with an implementation confirms the implementation reproduces the textbook, which catches an arithmetic error and nothing else.

---

## What was not read

Recorded explicitly, on the same principle as the rest of the repository.

**AIAA S-120 itself.** The growth allowance shape follows it; the numbers do not come from it.

**Any launch vehicle user guide.** The payload envelope, environment and interface definitions in a real user guide would sharpen [ConfigurationTrades](ConfigurationTrades.md) considerably, and none was consulted.

**Any range safety or launch licensing requirement.** These constrain azimuth and therefore the rotation assist in [TrajectoryBasics](TrajectoryBasics.md), and they belong to [rangeSafetyAndFTS](../../rangeSafetyAndFTS/).

---

## References

- AIAA S-120, *Mass Properties Control for Space Systems*
- Humble, Henry and Larson, *Space Propulsion Analysis and Design*
- Curtis, *Orbital Mechanics for Engineering Students*
- Sutton and Biblarz, *Rocket Propulsion Elements*
- [ValidationReferences](ValidationReferences.md)
