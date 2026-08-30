# Verification and Governance

## P20 Verification Design

For each important requirement define:

`Requirement -> Invariant -> Oracle/Reference -> Fixture/Corpus -> Test/Probe -> Metric -> Threshold -> Evidence Artifact -> Gate`

Choose evidence strength appropriate to risk:

`Narrative < Manual observation < Automated test < Deterministic oracle/golden < Differential/cross-implementation proof < Production/platform-qualified evidence`

Do not mechanically choose the strongest form; choose the cheapest form that credibly proves the contract.

## P21 Authority Review

Build a source-of-truth map. Classify sources as Current, Draft/Proposed, Superseded/Historical, Implementation Reality, or Evidence. Detect conflicting current documents, missing contracts, unresolved decisions, and stale downstream plans. Repository code cannot win an authority conflict merely because it exists.

Result: `READY`, `READY_WITH_FINDINGS`, or a precise `BLOCKED_*` status.

## P22 Five-Axis Drift Review

Check all five axes:

1. Product Drift: value/requirement changed or implementation no longer serves it.
2. Semantic Drift: object/operation/state meaning changed.
3. Architecture Drift: ownership/dependency/contract changed.
4. Implementation Drift: repository differs from current execution authority.
5. Verification Drift: tests prove stale/incorrect behavior rather than current requirements.

Classify each finding and identify the correct repair layer.

## P23 Authority Supersession

When accepted design changes replace current authority:

Old version:
- preserve it;
- mark `Superseded`;
- link the new version at the top;
- explain the supersession reason.

New version:
- mark `Current Authority`;
- link the previous version;
- include Review Findings / Change Summary;
- name the authority/evidence that drove the change.

Master/index:
- point only to current execution/design authority;
- update downstream dependency/version expectations.

Never label an implementation-plan correction as an architecture redesign unless architecture conclusions actually changed.

## P24 Release Readiness

Evaluate only evidence relevant to the product's risk profile. Typical areas: required gate results, migration/upgrade/downgrade, crash/recovery, data compatibility, rollback, observability, platform/device matrix, performance SLO, security/compliance handoff, known limitations, and support/runbook readiness.

## Defect taxonomy

- `IMPLEMENTATION_DEFECT`: code violates current contract.
- `SPEC_DEFECT`: current specification is internally wrong/incomplete for intended behavior.
- `AUTHORITY_CONFLICT`: multiple effective sources disagree.
- `MISSING_CONTRACT`: downstream work lacks a necessary defined boundary or semantic rule.
- `TEST_DEFECT`: test/oracle does not correctly represent the current contract.
- `EVIDENCE_GAP`: evidence required by the gate is absent or insufficient.
- `ENVIRONMENT_DEFECT`: toolchain, platform, service, permission, or infrastructure prevents valid execution.
- `DEPENDENCY_BLOCKER`: required upstream artifact/version/task is unavailable.
- `UNRESOLVED_DECISION`: design choice is intentionally still open and blocks downstream commitment.

## Gate verdicts

Use:

- `PASS`
- `PASS_WITH_FINDINGS`
- `BLOCKED_IMPLEMENTATION`
- `BLOCKED_AUTHORITY`
- `BLOCKED_EVIDENCE`
- `BLOCKED_ENVIRONMENT`

`PASS_WITH_FINDINGS` is only for findings that do not invalidate current exit criteria. Missing core evidence is never a cosmetic finding.
