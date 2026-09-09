# Verification and Governance

## P20 Verification Design

For each important requirement define:

`Requirement -> Invariant -> Failure Mode -> Existing Independent Coverage -> Residual Proof Gap -> Oracle/Reference -> Fixture/Corpus -> Exact Execution Method -> Evidence Artifact -> Blocking/Corroborative -> Gate Criterion`

Choose evidence strength appropriate to risk:

`Narrative < Manual observation < Automated test < Deterministic oracle/golden < Differential/cross-implementation proof < Production/platform-qualified evidence`

Do not mechanically choose the strongest form. Choose the lowest-cost form that credibly closes a material residual proof gap. For every blocking artifact state the high-impact failure mode, impact, existing independent coverage, unique detection value, and blocking justification. Evidence that only increases confidence in an independently covered behavior remains corroborative.

P20 should close important Verification obligations before P31. Missing required oracle, ambiguous terminal criterion, or unresolved blocking/corroborative classification is a P20/P31 blocker rather than something P34 should retroactively invent.

Apply the Anti-Proof-Recursion Rule: proof of an evidence mechanism becomes blocking only when that mechanism is a material undetected-failure source, lacks independent validation, and could materially alter the Gate decision.

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

Evaluate only evidence relevant to the selected risk profile and frozen release contract. Typical areas: required Gate results, migration/upgrade/downgrade, crash/recovery, data compatibility, rollback, observability, platform/device matrix, performance SLO, security/compliance handoff, known limitations, and support/runbook readiness.

Do not import Full-assurance evidence rituals into a Standard release merely because tooling can generate them. Full remains available when justified by protocol/schema, security, data-integrity, conformance, irreversible migration, or regulated/high-assurance risk.

## Defect taxonomy

Global defect vocabulary remains backward-compatible:

- `IMPLEMENTATION_DEFECT`: code violates current contract.
- `SPEC_DEFECT`: current specification is internally wrong/incomplete for intended behavior.
- `AUTHORITY_CONFLICT`: multiple effective sources disagree.
- `MISSING_CONTRACT`: downstream work lacks a necessary defined boundary or semantic rule.
- `TEST_DEFECT`: test/oracle does not correctly represent the current contract.
- `EVIDENCE_GAP`: a residual proof-capability gap remains for a material failure mode.
- `ENVIRONMENT_DEFECT`: toolchain, platform, service, permission, or infrastructure prevents valid execution.
- `DEPENDENCY_BLOCKER`: required upstream artifact/version/task is unavailable.
- `UNRESOLVED_DECISION`: design choice is intentionally still open and blocks downstream commitment.

For P35 late-finding routing, additionally express root-cause labels `VERIFICATION_DESIGN_DEFECT`, `TASK_PACKAGE_DEFECT`, and `NON_BLOCKING_HARDENING` without requiring a breaking global enum change. Do not disguise P20/P31 omissions as implementation incomplete.

## Gate verdicts

Use:

- `PASS`
- `PASS_WITH_FINDINGS`
- `BLOCKED_IMPLEMENTATION`
- `BLOCKED_AUTHORITY`
- `BLOCKED_EVIDENCE`
- `BLOCKED_ENVIRONMENT`

`PASS_WITH_FINDINGS` is only for findings that do not invalidate the frozen current exit criteria. A real newly discovered high-impact uncovered failure mode may still block; redundant evidence or hardening does not.
