---
name: aegis-verification
description: Design Aegis verification evidence before implementation. Use when the user asks how to prove a requirement or architecture is correct, define invariants, oracles, golden corpora, fixtures, metrics, thresholds, evidence artifacts, cross-language conformance, performance evidence, or map requirements to verification Gates.
---

# Aegis Verification

Own `P20` Verification Design. Define credible proof before implementation so P31 can freeze a stable completion target.

## Verification design

Start from failure modes, not artifact lists. An Evidence Artifact may become a blocking Gate requirement only when its absence leaves at least one high-impact failure mode without credible independent detection coverage. If alternate independent coverage already closes that proof gap, classify additional evidence as corroborative/non-blocking. Judge independence at the detection-mechanism and oracle level, not by artifact name or duplicate execution location.

Map each important requirement through:

`Requirement -> Invariant -> Failure Mode -> Existing Independent Coverage -> Residual Proof Gap -> Oracle/Reference -> Fixture/Corpus -> Exact Execution Method -> Evidence Artifact -> Blocking/Corroborative -> Gate Criterion`

For each proposed blocking artifact record `failure_mode`, `impact`, `existing_independent_coverage`, `new_evidence_unique_detection_value`, and `blocking_justification`. Choose the lowest-cost evidence strength that credibly closes the residual proof gap.

P20 is responsible for Verification closure before implementation. Do not leave a list of "tests we would like to have" for P34 to turn into new blocking requirements later. If a useful evidence idea does not uniquely detect a material uncovered failure mode, keep it corroborative or successor hardening.

Apply the Anti-Proof-Recursion Rule: evidence about another evidence mechanism becomes blocking only when that mechanism is itself a material undetected-failure source, lacks independent validation, and could materially change the Gate decision.

**Earlier untrusted layer:** if the requirement, semantic contract, or architecture to verify is missing or contradictory, stop and hand back to `aegis`; verification must not freeze an undefined upstream truth.

Read [references/verification.md](references/verification.md) and shared core/status contracts.

## Composition boundary

Once substantive execution begins in this Skill's owned stage family, this Skill is the unique Primary Owner for that substantive result. It may consume Project State support from `aegis-project-state`; Project State support does not transfer ownership.

Direct Primary-to-Primary substantive chaining is forbidden. After completing its owned stage, this Skill may suggest an unambiguous next Skill, but it must not automatically execute substantive work owned by that next Primary.

If an earlier untrusted layer blocks safe execution, emit an `ownership_handoff` to `aegis` and stop substantive execution. Do not repair or silently redefine the earlier layer inside this specialist.
