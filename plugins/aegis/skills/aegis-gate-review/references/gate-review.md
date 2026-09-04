# Gate Review Workflow

## P34
Review Authority/contract conformance, scope drift, required tests, required oracles, performance/resource evidence, platform evidence, and downstream safety. Return PASS, PASS_WITH_FINDINGS, or a precise blocker.

For any result returned from a code surface, resolve the supplied `materialized_ref` through a reviewer-accessible durable evidence boundary before relying on executor claims. A missing, local-only, or unresolvable result is `BLOCKED_EVIDENCE` and should be classified as an `EVIDENCE_GAP` at P35 unless an earlier layer owns the failure.

Repository-backed review and repair must first resolve the declared repository
identity and verify that package materialization belongs to that repository.
Do not use a bare SHA, ambient checkout, or another repository as a substitute;
identity failures are `BLOCKED_REPOSITORY_IDENTITY` before anchor/cursor or
repair decisions.

## P35
Use the shared defect taxonomy. Identify owning layer, affected Authority/task/Gate, and downstream invalidation.

## P36
Fix the owning layer; rerun original failing evidence and relevant regressions. If upstream Authority changed, update supersession and downstream execution packages before reuse.

Before returning a P36 repository repair/reverification result to `CONTROL_REVIEW`, materialize the exact result and return its reviewer-accessible `materialized_ref`. Do not claim closure from a local-only commit or transcript.
