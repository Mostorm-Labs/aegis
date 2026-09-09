---
name: aegis-gate-review
description: Audit a PR or implementation against Gate evidence and Gate exit criteria, determine PASS versus BLOCKED, classify defects, and route fix or reverification. Use for direct PR Gate audits, requests to review Gate evidence, verify Gate completion, classify whether a failure is implementation/spec/authority/test/evidence/environment related, or confirm regression closure.
---

# Aegis Gate Review

Own `P34` Gate Review, `P35` Defect Classification, and `P36` Fix / Reverification.

## Gate loop

- At `P34`, audit the frozen completion target through `Frozen Requirement Audit`, `Frozen Evidence Audit`, and `Repository Reality Audit`. P34 verifies frozen obligations; it does not normally redesign Verification after implementation starts. Agent claims are not evidence.
- Classify a blocker as `FROZEN_REQUIREMENT_FAILURE` or `NEWLY_DISCOVERED_FINDING`. A late finding may newly block only when it exposes a high-impact correctness, safety, security, compatibility, data-integrity, or release-critical failure mode not reasonably covered by frozen evidence.
- Every new blocking finding must state its failure mode, impact, existing independent coverage, unique detection value, why frozen evidence missed it, and why severity is sufficient to override closure stability. Otherwise classify it `NON_BLOCKING_FINDING` and optionally create successor work.
- A missing named artifact is not automatically an `EVIDENCE_GAP`. Before blocking, identify the high-impact failure mode it was meant to detect, check alternate credible coverage and mechanism/oracle independence, and state the residual proof gap. Redundant supporting, confidence, diagnostic, audit, observability, or hardening evidence is non-blocking.
- Apply the Anti-Proof-Recursion Rule. Do not create a blocking proof-of-proof chain unless the evidence mechanism itself is a material undetected-failure source, lacks independent validation, and can materially change the Gate decision.
- Before resolving repository-backed P34/P36 evidence, establish the declared repository identity, resolve the returned reviewer-accessible `materialized_ref`, and verify the exact result/evidence boundary required by the frozen package/profile before relying on executor claims. Missing, local-only, mismatched, ambiguous, or unavailable review identity is `BLOCKED_EVIDENCE` or `BLOCKED_REPOSITORY_IDENTITY` as applicable.
- At `P35`, classify the owning defect layer before proposing a fix. Late findings must distinguish implementation defects from `VERIFICATION_DESIGN_DEFECT`, `TASK_PACKAGE_DEFECT`, and `NON_BLOCKING_HARDENING`; do not disguise an earlier-layer omission as implementation incomplete.
- At `P36`, repair only implementation-owned work here and rerun the frozen failed evidence plus relevant regressions. Earlier-layer defects route back before a new/current execution package is issued.

For Verification-bound results, P34 independently resolves the exact package, result, frozen blocking EvidenceInputRefs, ProofEvaluation/provider identities when required, and independent obligation completeness. `UNDECLARED` or `STRUCTURALLY_UNSATISFIABLE` late requirements route to the owning earlier layer instead of becoming retroactive implementation repair work. ProofEvaluation, green CI, workflow summaries, handoff prose, and executor claims cannot issue or imply official Gate PASS.

**Earlier untrusted layer:** if review discovers a spec, Authority, Verification Design, or Task Package defect upstream of implementation, stop downstream repair and hand back to `aegis`; do not silently rewrite Authority or expand the old closure contract inside Gate review.

Read [references/gate-review.md](references/gate-review.md) and the shared status/Authority contracts.

## Execution-surface boundary

- `P34` Gate Review and `P35` Defect Classification default to `CONTROL_REVIEW`.
- `P36` repository repair and reverification may execute on `CODE_REVERIFY` only after P35 classification has identified an implementation-owned repair and the repair scope/evidence obligations are explicit.
- A `CONTROL_REVIEW -> CODE_REVERIFY` surface handoff changes execution location only; it does not transfer this Skill's P34-P36 Primary Owner semantics.
- If classification identifies an upstream Authority/spec/Verification/package defect, do not hand repair to the code surface; route the owning upstream layer instead.

Default OpenAI profile: `CONTROL_REVIEW -> ChatGPT`, `CODE_REVERIFY -> Codex`.

## Composition boundary

Once substantive execution begins in this Skill's owned stage family, this Skill is the unique Primary Owner for that substantive result. It may consume Project State support from `aegis-project-state`; Project State support does not transfer ownership.

Direct Primary-to-Primary substantive chaining is forbidden. After completing its owned stage, this Skill may suggest an unambiguous next Skill, but it must not automatically execute substantive work owned by that next Primary.

If an earlier untrusted layer blocks safe execution, emit an `ownership_handoff` to `aegis` and stop substantive execution. Do not repair or silently redefine the earlier layer inside this specialist.
