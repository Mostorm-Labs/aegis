# Implementation Control

## P30 Implementation Planning
Build dependency-aware evidence-gated vertical slices, each independently reviewable. Default execution surface: `CONTROL_REASONING`.

## P31 Task Packaging
Include task ID/purpose, Current Authority refs, dependencies, scope/files, required changes, non-goals, tests/oracle, evidence artifacts, performance constraints, exit criteria, and blocked return behavior. Default execution surface: `CONTROL_REASONING`.

Before handing implementation to a code surface, compress resolved decisions into the approved task package. Do not spend execution-context tokens rediscovering decisions that the control plane can resolve once and encode into the package.

### EXECUTION_CLOSURE_CONTRACT

Every P31 implementation package MUST freeze an `EXECUTION_CLOSURE_CONTRACT` so the executor knows the complete blocking completion target before mutation begins:

```yaml
EXECUTION_CLOSURE_CONTRACT:
  implementation:
    required_changes: []
    forbidden_changes: []

  tests:
    required:
      - id: null
        command_or_oracle: null
        expected_result: null
        blocking_reason: null

  hosted_verification:
    required: []
    optional: []

  evidence:
    blocking: []
    corroborative: []

  terminal_success:
    all_of: []

  terminal_blockers:
    explicit_classes:
      - AUTHORITY_CONFLICT
      - MISSING_REQUIRED_INPUT
      - ENVIRONMENT_BLOCKER
      - FROZEN_VERIFICATION_FAILURE
      - NEW_HIGH_IMPACT_FAILURE_MODE

  return_policy:
    continue_until_terminal_state: true
```

P31 MUST separate blocking evidence from corroborative evidence and bind every blocking item to its frozen Verification obligation. If terminal success is ambiguous, a required oracle/input is missing, or the package depends on a Verification decision that has not been frozen, return to P20/P31 before CODE_EXECUTION. Do not let P32 infer a moving completion definition from later reviewer preferences.

For repository-backed execution that depends on a repository baseline, the package MUST carry a non-null `task_anchor` that identifies the trusted repository revision and required ancestry relation. `Task Anchor != Execution Cursor`: the task anchor is a trust baseline, not a requirement that current HEAD equal the historical package revision.

`resume_cursor` is nullable at the schema level. If interrupted work has already been reconciled and a control-plane-accepted continuation point exists, P31/P33 handoff metadata MUST carry a non-null `resume_cursor` with the execution ref, accepted revision, verified `completed_through`, and `next_action`. If no accepted continuation point exists yet, `resume_cursor: null` is valid. The cursor is navigation metadata only and cannot expand Authority or scope.

For tasks that return to a review surface, the package must define the evidence-materialization obligation required by its profile and Verification Contract. The exact result must become independently reviewer-resolvable at the frozen evidence boundary. Standard profile does not imply an evidence-only commit: an exact PR head/result revision plus applicable hosted CI may be the durable boundary when the contract says so.

For any rendered `surface_handoff` with `preferred_executor: codex`, place this exact execution instruction immediately before the YAML envelope:

> 请按以下 Aegis handoff 直接执行：以 `package_ref` 为任务授权，按 `task_anchor/resume_cursor` 核对当前状态并从首个未完成步骤继续；若状态冲突则 fail closed。

The package's return policy is normative: do not return merely because an intermediate checkpoint has been reached. Continue through all remaining executable items in the frozen Execution Closure Contract during the same execution unless an explicit terminal blocker is encountered.

The prefix is execution-trigger/rendering metadata only. It does not expand the approved package, change Current Authority, create Evidence, issue a Gate verdict, or mutate Project State.

## P32 Implementation
Default execution surface: `CODE_EXECUTION`. Inspect repository/task Authority before edits, change only assigned scope, and execute the complete frozen closure contract until `terminal_success` is satisfied or an explicit terminal blocker occurs. A `surface_handoff` must carry the approved P31 `package_ref`; baseline-dependent repository work MUST also carry the non-null stable `task_anchor`. It changes execution location, not P32 ownership.

Resolve ordinary uncertainty that is answerable by reading the repository, Current Authority, package, existing APIs, or runnable tests. Do not stop merely because code edits, local tests, or another intermediate checkpoint finished while required closure items remain executable.

Fail closed for real missing Authority, scope conflict, unresolved decisions, environment failures, frozen verification failures, or a newly observed high-impact failure mode that requires classification. Implementation MUST NOT redesign upstream Authority or add new blocking completion requirements on its own.

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
5. keep local filesystem/worktree artifacts staging-only until the package-required durable materialization exists;
6. treat structured EvidenceArtifact / provider observations / ProofEvaluation as the owners of their machine facts; do not copy their totals into the execution return as a second source of truth;
7. return exact `result_revision`, reviewer-resolvable `materialized_ref` when required by the frozen contract, exact `evidence_input_refs`, and exact provider run/attempt/job/artifact refs required by the package.

P32 may prepare all exact inputs needed by CONTROL_REVIEW, but it MUST NOT emit or imply official P34 PASS. If a required review-produced value is needed during P32, classify the phase dependency instead of waiting for or synthesizing the future review verdict.

Before returning to `CONTROL_REVIEW`, satisfy the package-defined durable result/evidence boundary. If the frozen contract requires a reviewer-accessible materialization and it is unavailable, return `BLOCKED_EVIDENCE` with the exact blocker. Do not invent an evidence-only descendant when Standard profile already has an independently resolvable PR head and exact hosted CI binding that the contract accepts.

## P33 Resume Interrupted Work
Default execution surface: `CODE_EXECUTION`. P33 means resume interrupted valid work after a session, environment, tool/API, or execution interruption. Inspect branch/diff/artifacts/tests/Authority, preserve valid modifications, and resume at the first incomplete verified step. P33 is not a continuous package-enhancement loop.

Classify the observed repository position before changing files:

P33 performs the same repository identity preflight before any anchor/cursor
classification. A repository-addressing failure is `BLOCKED_REPOSITORY_IDENTITY`,
not execution divergence.

- `EXACT_CURSOR`: observed HEAD equals `resume_cursor.revision`; resume from `next_action`.
- `DESCENDANT_CURSOR`: `resume_cursor.revision` is an ancestor of observed HEAD; inspect only the delta after the cursor, preserve verified valid work, and do not replay completed work.
- `ANCHOR_DESCENDANT_WITHOUT_CURSOR`: no accepted cursor exists but the task anchor is an ancestor of observed HEAD; reconcile completed versus pending work, establish a cursor, then resume at the first incomplete verified step.
- `DIVERGED`: neither accepted cursor nor required anchor ancestry can be established, history is incompatibly rewritten, or observed state contradicts Authority/scope; fail closed with `BLOCKED_EXECUTION_DIVERGENCE` or a more specific existing Authority/environment blocker.

### P33_REPETITION_GUARD

Whenever resume reconciliation introduces work that was not present in the frozen P31 closure contract, classify the root cause before continuing:

- package omitted an execution requirement -> `TASK_PACKAGE_DEFECT` -> return to P31;
- P20 omitted a required verification obligation/oracle -> `VERIFICATION_DESIGN_DEFECT` -> return to P20;
- implementation failed a frozen requirement -> implementation-owned defect, eligible for P36 after P35;
- new high-impact uncovered failure mode -> return to P35 for late-finding classification.

Do not keep generating P33 patch handoffs for repeated package/verification omissions. Mechanical retry count alone is not the decision rule; root cause is. Preserve accepted partial work when repairing the earlier layer, then issue one corrected current package rather than extending the old finish line incrementally.

Apply the same Verification-bound preflights and exact-return discipline when resuming P33. A resume cursor is navigation only; it cannot replace any required exact proof binding or expand the frozen closure contract.

## Default OpenAI profile

`CONTROL_REASONING -> ChatGPT`; `CODE_EXECUTION -> Codex`. Product names are executor-profile metadata, not lifecycle Authority.
