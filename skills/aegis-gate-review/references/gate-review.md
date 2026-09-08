# Gate Review Workflow

## P34
Review Authority/contract conformance, scope drift, required tests, required oracles, performance/resource evidence, platform evidence, and downstream safety. Return PASS, PASS_WITH_FINDINGS, or a precise blocker.

### Blocking decision discipline

At P34, an `EVIDENCE_GAP` is a proof-capability gap: missing evidence blocks only when its absence leaves at least one high-impact failure mode without credible independent detection coverage.

The absence of a named artifact does not by itself establish `EVIDENCE_GAP`. Before blocking for missing evidence, independently determine:

1. which high-impact failure mode the evidence is intended to detect;
2. whether alternate credible evidence already detects that failure mode;
3. whether that alternate coverage is genuinely independent at the mechanism and oracle level; and
4. what residual proof gap remains without the named artifact.

If alternate credible evidence independently closes the same proof gap, treat the missing artifact as a non-blocking finding unless the governing Authority requires it to detect a distinct high-impact failure mode or to establish a prerequisite identity/provenance contract that no alternate evidence satisfies.

For any result returned from a code surface, resolve the supplied `materialized_ref` through a reviewer-accessible durable evidence boundary before relying on executor claims. A missing, local-only, or unresolvable result remains `BLOCKED_EVIDENCE` because result identity, provenance, and reviewer accessibility are themselves an uncovered proof-capability gap; classify it as an `EVIDENCE_GAP` at P35 unless an earlier layer owns the failure.

Repository-backed review and repair must first resolve the declared repository
identity and verify that package materialization belongs to that repository.
Do not use a bare SHA, ambient checkout, or another repository as a substitute;
identity failures are `BLOCKED_REPOSITORY_IDENTITY` before anchor/cursor or
repair decisions.

For a Verification-bound implementation result, P34 independently resolves and checks:

1. exact governing package and exact result identities;
2. all blocking EvidenceInputRefs and their reviewer-resolvable access, plus any non-blocking evidence needed for findings;
3. ProofEvaluation identity and its exact subject/result binding;
4. exact provider run/attempt/job/matrix/artifact identities, terminal state, and result applicability;
5. independent obligation completeness using the review-owned traversal rather than the generator as sole oracle;
6. any new Gate requirement through `ReviewContractDiffer`, including its high-impact failure mode, existing independent coverage, and residual proof gap, before assigning repair;
7. identity separation between result, evidence, ProofEvaluation, provider observations, and formal Gate decision.

`UNDECLARED` and `STRUCTURALLY_UNSATISFIABLE` review requirements route to the owning earlier layer; they are not converted into old P32 obligations. ProofEvaluation, green CI, workflow summaries, manually copied totals, and executor/assistant prose remain evidence/navigation inputs only and cannot issue or imply official P34 PASS.

## P35
Use the shared defect taxonomy. Identify owning layer, affected Authority/task/Gate, and downstream invalidation. Use `EVIDENCE_GAP` for a residual proof-capability gap, not for checklist or artifact completeness alone.

## P36
Fix the owning layer; rerun original failing evidence and relevant regressions. If upstream Authority changed, update supersession and downstream execution packages before reuse.

Before returning a P36 repository repair/reverification result to `CONTROL_REVIEW`, materialize the exact result and return its reviewer-accessible `materialized_ref`. Do not claim closure from a local-only commit or transcript.

P36 must preserve the same exact evidence/provider identity discipline as P34. Repaired evidence that changes only an external EvidenceInputRef may preserve an unchanged result identity; any repair that changes repository result bytes creates a new result revision and must not be reported as the old result.
