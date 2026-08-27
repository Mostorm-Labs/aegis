---
name: aegis-verification
description: Design Aegis verification evidence before implementation. Use when the user asks how to prove a requirement or architecture is correct, define invariants, oracles, golden corpora, fixtures, metrics, thresholds, evidence artifacts, cross-language conformance, performance evidence, or map requirements to verification Gates.
---

# Aegis Verification

Own `P20` Verification Design. Define credible proof before implementation.

## Verification design

Map each important requirement through: `Requirement -> Invariant -> Oracle/Reference -> Fixture/Corpus -> Test/Probe -> Metric -> Threshold -> Evidence Artifact -> Gate`. Choose the cheapest evidence strength that credibly proves the contract.

**Earlier untrusted layer:** if the requirement, semantic contract, or architecture to verify is missing or contradictory, stop and hand back to `aegis`; verification must not freeze an undefined upstream truth.

Read [references/verification.md](references/verification.md) and shared core/status contracts.

## Composition boundary

Once substantive execution begins in this Skill's owned stage family, this Skill is the unique Primary Owner for that substantive result. It may consume Project State support from `aegis-project-state`; Project State support does not transfer ownership.

Direct Primary-to-Primary substantive chaining is forbidden. After completing its owned stage, this Skill may suggest an unambiguous next Skill, but it must not automatically execute substantive work owned by that next Primary.

If an earlier untrusted layer blocks safe execution, emit an `ownership_handoff` to `aegis` and stop substantive execution. Do not repair or silently redefine the earlier layer inside this specialist.
