# Implementation Control

## P30 Implementation Planning
Build dependency-aware evidence-gated vertical slices, each independently reviewable. Default execution surface: `CONTROL_REASONING`.

## P31 Task Packaging
Include task ID/purpose, Current Authority refs, dependencies, scope/files, required changes, non-goals, tests/oracle, evidence artifacts, performance constraints, exit criteria, and blocked return behavior. Default execution surface: `CONTROL_REASONING`.

Before handing implementation to a code surface, compress resolved decisions into the approved task package. Do not spend execution-context tokens rediscovering decisions that the control plane can resolve once and encode into the package.

For repository-backed execution that depends on a repository baseline, the package MUST carry a non-null `task_anchor` that identifies the trusted repository revision and required ancestry relation. `Task Anchor != Execution Cursor`: the task anchor is a trust baseline, not a requirement that current HEAD equal the historical package revision.

`resume_cursor` is nullable at the schema level. If interrupted work has already been reconciled and a control-plane-accepted continuation point exists, P31/P33 handoff metadata MUST carry a non-null `resume_cursor` with the execution ref, accepted revision, verified `completed_through`, and `next_action`. If no accepted continuation point exists yet, `resume_cursor: null` is valid. The cursor is navigation metadata only and cannot expand Authority or scope.

For tasks that return to a review surface, the package must define the evidence-materialization obligation: the exact result must become reviewer-accessible through a durable ref, and the executor return must carry that `materialized_ref`. A local-only result is not sufficient for P34 corroboration.

For any rendered `surface_handoff` with `preferred_executor: codex`, place this exact execution instruction immediately before the YAML envelope:

> 请按以下 Aegis handoff 直接执行：以 `package_ref` 为任务授权，按 `task_anchor/resume_cursor` 核对当前状态并从首个未完成步骤继续；若状态冲突则 fail closed。

The prefix is execution-trigger/rendering metadata only. It does not expand the approved package, change Current Authority, create Evidence, issue a Gate verdict, or mutate Project State.

## P32 Implementation
Default execution surface: `CODE_EXECUTION`. Inspect repository/task Authority before edits, change only assigned scope, run specified evidence, and stop on Authority ambiguity. A `surface_handoff` must carry the approved P31 `package_ref`; baseline-dependent repository work MUST also carry the non-null stable `task_anchor`. It changes execution location, not P32 ownership.

For `task_anchor.relation: ancestor`, verify that the anchor is an ancestor of the accepted starting revision. Do not require historical HEAD equality when the declared contract is ancestry. Record the actual starting revision before edits.

Repository identity is the first P32 preflight. Resolve the declared
`repository.provider/full_name`, then the same-repository
`package_materialization_ref`, before resolving the package or checking
anchor/cursor ancestry. Missing, mismatched, ambiguous, or unavailable
identity returns `BLOCKED_REPOSITORY_IDENTITY` with `continue_execution:
false`; a bare revision is never a repository locator.

For Verification-bound repository execution, after repository identity succeeds and before mutation:

1. resolve exact VerificationSpec, obligation-set when required, TrustedBasis, scope, acceptance-oracle, and evidence-compilation bindings from the approved package;
2. require `PackageBindingPreflight` success;
3. require `EvidenceContractPreflight` success;
4. reject floating labels or mutable-only trust identities rather than passing them into CODE_EXECUTION;
5. keep local filesystem/worktree artifacts staging-only until exact durable materialization exists;
6. treat structured EvidenceArtifact / provider observations / ProofEvaluation as the owners of their machine facts; do not copy their totals into the execution return as a second source of truth;
7. return exact `result_revision`, reviewer-resolvable `materialized_ref`, exact `evidence_input_refs`, and exact provider run/attempt/job/artifact refs required by the package.

P32 may prepare all exact inputs needed by CONTROL_REVIEW, but it MUST NOT emit or imply official P34 PASS. If a required review-produced value is needed during P32, classify the phase dependency instead of waiting for or synthesizing the future review verdict.

Before returning to `CONTROL_REVIEW`, materialize the exact result at the package-defined reviewer-accessible evidence boundary and return its `materialized_ref`. If materialization is unavailable, return `BLOCKED_EVIDENCE` with the exact blocker.

## P33 Resume Interrupted Work
Default execution surface: `CODE_EXECUTION`. Inspect branch/diff/artifacts/tests/Authority, report completed vs pending work, preserve valid modifications, and resume at the first incomplete verified step. A resumable task must not use historical HEAD equality as its only starting-state predicate. If a control-plane-accepted continuation point is known, the handoff MUST carry its non-null `resume_cursor` before execution resumes.

Classify the observed repository position before changing files:

P33 performs the same repository identity preflight before any anchor/cursor
classification. A repository-addressing failure is `BLOCKED_REPOSITORY_IDENTITY`,
not execution divergence.

- `EXACT_CURSOR`: observed HEAD equals `resume_cursor.revision`; resume from `next_action`.
- `DESCENDANT_CURSOR`: `resume_cursor.revision` is an ancestor of observed HEAD; inspect only the delta after the cursor, preserve verified valid work, and do not replay completed work.
- `ANCHOR_DESCENDANT_WITHOUT_CURSOR`: no accepted cursor exists but the task anchor is an ancestor of observed HEAD; reconcile completed versus pending work, establish a cursor, then resume at the first incomplete verified step.
- `DIVERGED`: neither accepted cursor nor required anchor ancestry can be established, history is incompatibly rewritten, or observed state contradicts Authority/scope; fail closed with `BLOCKED_EXECUTION_DIVERGENCE` or a more specific existing Authority/environment blocker.

Apply the same Verification-bound preflights and exact-return discipline when resuming P33. A resume cursor is navigation only; it cannot replace any required exact proof binding.

Apply the same evidence-materialization requirement before returning a completed result to review. An execution cursor is not P34 evidence; P34 still resolves the returned `materialized_ref` independently.

## Default OpenAI profile

`CONTROL_REASONING -> ChatGPT`; `CODE_EXECUTION -> Codex`. Product names are executor-profile metadata, not lifecycle Authority.
