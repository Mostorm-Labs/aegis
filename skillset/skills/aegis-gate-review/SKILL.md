---
name: aegis-gate-review
description: Audit a PR or implementation against Gate evidence and Gate exit criteria, determine PASS versus BLOCKED, classify defects, and route fix or reverification. Use for direct PR Gate audits, requests to review Gate evidence, verify Gate completion, classify whether a failure is implementation/spec/authority/test/evidence/environment related, or confirm regression closure.
---

# Aegis Gate Review

Own `P34` Gate Review, `P35` Defect Classification, and `P36` Fix / Reverification.

## Gate loop

- At `P34`, audit Authority conformance, semantics/contracts, scope, automated tests, oracle/golden/differential evidence, performance/platform evidence when required, and downstream safety. Agent claims are not evidence. Resolve the returned `materialized_ref` at a reviewer-accessible durable evidence boundary before relying on executor claims; a local-only result is `BLOCKED_EVIDENCE`.
- Before resolving any repository-backed P34/P36 evidence, establish the declared `repository.provider/full_name` and same-repository `package_materialization_ref`; only then resolve package, anchor, or repair state. Missing, mismatched, ambiguous, or unavailable identity is `BLOCKED_REPOSITORY_IDENTITY` with `continue_execution: false`.
- At `P35`, classify the owning defect layer before proposing a fix.
- At `P36`, repair at the owning layer and rerun the failed evidence plus relevant regression evidence.
- Before P36 returns to `CONTROL_REVIEW`, materialize the exact repair/reverification result and return its `materialized_ref`; if that cannot be independently resolved, classify the remaining gap as `EVIDENCE_GAP` instead of claiming closure.

For Verification-bound results, P34 must independently resolve the exact package, result, EvidenceInputRefs, ProofEvaluation, provider run applicability/completion, and independent obligation completeness. When a new Gate-critical requirement appears, apply `ReviewContractDiffer`; `UNDECLARED` or `STRUCTURALLY_UNSATISFIABLE` requirements route to their owning earlier layer instead of becoming retroactive implementation repair work. ProofEvaluation, green CI, workflow summaries, handoff prose, and executor claims cannot issue or imply official Gate PASS.

**Earlier untrusted layer:** if review discovers a spec or Authority defect upstream of implementation, stop downstream repair and hand back to `aegis`; do not silently rewrite Authority inside Gate review.

Read [references/gate-review.md](references/gate-review.md) and the shared status/Authority contracts.

## Execution-surface boundary

- `P34` Gate Review and `P35` Defect Classification default to `CONTROL_REVIEW`.
- `P36` repository repair and reverification may execute on `CODE_REVERIFY` only after P35 classification has identified an implementation-owned repair and the repair scope/evidence obligations are explicit.
- A `CONTROL_REVIEW -> CODE_REVERIFY` surface handoff changes execution location only; it does not transfer this Skill's P34-P36 Primary Owner semantics.
- If classification identifies an upstream Authority/spec defect, do not hand repair to the code surface; route the owning upstream layer instead.

Default OpenAI profile: `CONTROL_REVIEW -> ChatGPT`, `CODE_REVERIFY -> Codex`.

## Composition boundary

Once substantive execution begins in this Skill's owned stage family, this Skill is the unique Primary Owner for that substantive result. It may consume Project State support from `aegis-project-state`; Project State support does not transfer ownership.

Direct Primary-to-Primary substantive chaining is forbidden. After completing its owned stage, this Skill may suggest an unambiguous next Skill, but it must not automatically execute substantive work owned by that next Primary.

If an earlier untrusted layer blocks safe execution, emit an `ownership_handoff` to `aegis` and stop substantive execution. Do not repair or silently redefine the earlier layer inside this specialist.
