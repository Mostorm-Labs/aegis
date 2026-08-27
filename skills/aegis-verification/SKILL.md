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
