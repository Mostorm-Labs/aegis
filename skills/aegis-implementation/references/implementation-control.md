# Implementation Control

## P30 Implementation Planning
Build dependency-aware evidence-gated vertical slices, each independently reviewable.

## P31 Task Packaging
Include task ID/purpose, Current Authority refs, dependencies, scope/files, required changes, non-goals, tests/oracle, evidence artifacts, performance constraints, exit criteria, and blocked return behavior.

## P32 Implementation
Inspect repository/task Authority before edits, change only assigned scope, run specified evidence, and stop on Authority ambiguity.

## P33 Resume Interrupted Work
Inspect branch/diff/artifacts/tests/Authority, report completed vs pending work, preserve valid modifications, and resume at the first incomplete verified step.
