# Gate Review Workflow

## P34
P34 audits a frozen closure contract; it does not normally redesign Verification after P31. Perform three explicit review passes:

1. `Frozen Requirement Audit`
2. `Frozen Evidence Audit`
3. `Repository Reality Audit`

Return PASS, PASS_WITH_FINDINGS, or a precise blocker.

### Gate Closure Stability

Classify every blocking candidate as either `FROZEN_REQUIREMENT_FAILURE` or `NEWLY_DISCOVERED_FINDING`.

`FROZEN_REQUIREMENT_FAILURE` means an explicitly frozen requirement or frozen Verification obligation failed. It may block under the governing Gate.

`NEWLY_DISCOVERED_FINDING` was not part of the frozen P31 completion target. Split it into:

- `blocking_high_impact`: a newly discovered high-impact correctness, safety, security, compatibility, data-integrity, or release-critical failure mode that was not reasonably covered by the frozen contract;
- `NON_BLOCKING_FINDING`: confidence improvement, redundant evidence, diagnostics, auditability, observability, or hardening that does not expose such an uncovered failure mode.

A new blocking finding MUST record:

- `failure_mode`
- `impact`
- `existing_independent_coverage`
- `new_evidence_unique_detection_value`
- `blocking_justification`
- `why_existing_frozen_evidence_did_not_cover_it`
- `why_it_is_severe_enough_to_override_closure_stability`

Without that justification, classify the late item as `NON_BLOCKING_FINDING`; it may become successor work but MUST NOT move the current blocking finish line.

### Blocking evidence decision discipline

At P34, an `EVIDENCE_GAP` is a proof-capability gap: missing evidence blocks only when its absence leaves at least one high-impact failure mode without credible independent detection coverage.

The absence of a named artifact does not by itself establish `EVIDENCE_GAP`. Before blocking for missing evidence, independently determine:

1. which high-impact failure mode the evidence is intended to detect;
2. whether alternate credible evidence already detects that failure mode;
3. whether that alternate coverage is genuinely independent at the mechanism and oracle level;
4. what residual proof gap remains without the named artifact; and
5. whether the proposed new evidence has unique detection value rather than merely increasing confidence.

If alternate credible evidence independently closes the same proof gap, treat the new or missing artifact as non-blocking unless the frozen governing Authority already required it for a distinct failure mode or prerequisite identity/provenance contract.

Do not require evidence solely to prove another evidence mechanism trustworthy unless that mechanism itself is a material source of undetected Gate error, lacks independent validation, and can materially change the Gate decision. This is the Anti-Proof-Recursion Rule applied at review time.

### Gate review output

```yaml
gate_review:
  frozen_requirements:
    passed: []
    failed: []

  frozen_evidence:
    passed: []
    failed: []

  new_findings:
    blocking_high_impact: []
    non_blocking: []

  verdict: null
```

For any result returned from a code surface, resolve the result identity through the frozen reviewer-accessible durable boundary before relying on executor claims. A local-only result is insufficient when the closure contract requires independent reviewability. Do not invent a stricter materialization ritual after P31 merely because Full-style evidence could improve confidence.

Repository-backed review and repair must first resolve the declared repository
identity and verify that package materialization belongs to that repository.
Do not use a bare SHA, ambient checkout, or another repository as a substitute;
identity failures are `BLOCKED_REPOSITORY_IDENTITY` before anchor/cursor or
repair decisions.

For a Verification-bound implementation result, P34 independently resolves and checks:

1. exact governing package and exact result identities;
2. all frozen blocking EvidenceInputRefs and their reviewer-resolvable access, plus non-blocking evidence only as findings/corroboration;
3. ProofEvaluation identity and its exact subject/result binding when required by the frozen contract;
4. exact provider run/attempt/job/matrix/artifact identities, terminal state, and result applicability when required;
5. independent obligation completeness using review-owned traversal rather than a generator as sole oracle;
6. any late Gate-critical finding through `ReviewContractDiffer`, applying closure-stability and failure-mode-first qualification before assigning repair;
7. identity separation between result, evidence, ProofEvaluation, provider observations, and formal Gate decision.

`UNDECLARED` and `STRUCTURALLY_UNSATISFIABLE` requirements do not become retroactive old-P32 obligations. Classify their root cause and route to the owning earlier layer. ProofEvaluation, green CI, workflow summaries, handoff prose, and executor claims cannot issue or imply official P34 PASS.

## P35
Use the shared defect taxonomy for global Gate status, and classify late-finding root cause before repair. In addition to existing defect types, the late-finding analysis MUST be able to express:

- `IMPLEMENTATION_DEFECT`
- `SPEC_DEFECT`
- `VERIFICATION_DESIGN_DEFECT`
- `TASK_PACKAGE_DEFECT`
- `NON_BLOCKING_HARDENING`

These late-finding labels refine routing and do not require a breaking change to the global defect enum. Do not disguise a Verification Design or Task Package defect as implementation incomplete.

- `VERIFICATION_DESIGN_DEFECT` -> earliest untrusted layer P20.
- `TASK_PACKAGE_DEFECT` -> P31, preserving valid implementation work where possible.
- `IMPLEMENTATION_DEFECT` under a trusted frozen contract -> P36.
- `NON_BLOCKING_HARDENING` -> successor task; current Gate remains judged against frozen obligations.
- real newly discovered high-impact uncovered defect -> block and route through P35 to the actual owning layer.

Use `EVIDENCE_GAP` only for a residual proof-capability gap, not checklist or artifact completeness alone.

## P36
Fix the owning layer; rerun original failing frozen evidence and relevant regressions. If upstream Authority, Verification Design, or the task package changed, refresh downstream execution authority before reuse.

Before returning a P36 repository repair/reverification result to `CONTROL_REVIEW`, satisfy the repaired package's reviewer-accessible evidence boundary. Do not claim closure from a local-only commit or transcript when the contract requires durable independent resolution.

P36 must preserve the same exact evidence/provider identity discipline required by the active profile and frozen contract. Repaired evidence that changes only an external EvidenceInputRef may preserve an unchanged result identity; any repair that changes repository result bytes creates a new result revision and must not be reported as the old result.
