# Implementation Control

## P30 Implementation Planning
Build dependency-aware evidence-gated vertical slices, each independently reviewable. Default execution surface: `CONTROL_REASONING`.

## P31 Task Packaging
Include task ID/purpose, Current Authority refs, dependencies, scope/files, required changes, non-goals, tests/oracle, evidence artifacts, performance constraints, exit criteria, and blocked return behavior. Default execution surface: `CONTROL_REASONING`.

Before handing implementation to a code surface, compress resolved decisions into the approved task package. Do not spend execution-context tokens rediscovering decisions that the control plane can resolve once and encode into the package.

For tasks that return to a review surface, the package must define the evidence-materialization obligation: the exact result must become reviewer-accessible through a durable ref, and the executor return must carry that `materialized_ref`. A local-only result is not sufficient for P34 corroboration.

## P32 Implementation
Default execution surface: `CODE_EXECUTION`. Inspect repository/task Authority before edits, change only assigned scope, run specified evidence, and stop on Authority ambiguity. A `surface_handoff` must carry the approved P31 `package_ref`; it changes execution location, not P32 ownership.

Before returning to `CONTROL_REVIEW`, materialize the exact result at the package-defined reviewer-accessible evidence boundary and return its `materialized_ref`. If materialization is unavailable, return `BLOCKED_EVIDENCE` with the exact blocker.

## P33 Resume Interrupted Work
Default execution surface: `CODE_EXECUTION`. Inspect branch/diff/artifacts/tests/Authority, report completed vs pending work, preserve valid modifications, and resume at the first incomplete verified step. Apply the same evidence-materialization requirement before returning a completed result to review.

## Default OpenAI profile

`CONTROL_REASONING -> ChatGPT`; `CODE_EXECUTION -> Codex`. Product names are executor-profile metadata, not lifecycle Authority.
