# Execution Anchor + Resume Cursor Design

Status: Approved design for implementation
Date: 2026-08-29

## Problem

Aegis currently transfers an approved P31 task package to the code execution surface, but the shared `surface_handoff` contract does not carry a normative execution position. The package tells Codex what work is authorized, while the executor's local branch/worktree may already have advanced beyond the historical package baseline. A later resume can therefore compare the current HEAD against a stale historical expected HEAD and incorrectly return `BLOCKED_STARTING_STATE_MISMATCH` even when the current HEAD is a valid descendant containing already-completed authorized work.

The defect is not that Codex inspects repository state or fails closed. The missing layer is a shared execution-position contract between the control plane and the execution plane.

## Core invariants

1. `Task Anchor != Execution Cursor`.
2. A task package tells the executor what is authorized; an execution cursor tells the executor where authorized execution currently is.
3. A resumable task must not use historical HEAD equality as its only starting-state predicate.
4. P33 preserves verified descendant work and resumes at the first incomplete verified step; it must not replay completed work solely because HEAD advanced.
5. True ancestry divergence, missing trusted ancestry, or contradictory Authority still fails closed.
6. Execution-position metadata remains handoff/navigation metadata. It does not become Authority, Evidence, Gate, Integration, or Project State merely by existing.

## Task Anchor

`task_anchor` is the stable trust baseline for one execution package.

```yaml
task_anchor:
  revision: <40-char-revision>
  relation: ancestor
```

For repository execution, `relation: ancestor` means the anchor revision must be an ancestor of the executor's accepted starting or resume revision. The anchor is not required to equal HEAD.

The task anchor answers: "what trusted repository history must this work descend from?"

## Resume Cursor

`resume_cursor` is optional, mutable handoff metadata created only after a P33 reconciliation or an executor return has established a verified continuation point.

```yaml
resume_cursor:
  execution_ref: <branch-or-durable-ref>
  revision: <40-char-revision>
  completed_through:
    - <verified completed step>
  next_action: <first incomplete verified step>
```

The resume cursor answers: "where is the accepted continuation point now?"

The cursor does not authorize new scope. All work after the cursor remains constrained by the original package Authority, scope, non-goals, tests, evidence obligations, and exit criteria.

## P31 handoff semantics

A repository-heavy P32/P33 handoff should carry:

```yaml
type: surface_handoff
stage: P32 | P33
stage_owner: aegis-implementation
from_surface: CONTROL_REASONING
to_surface: CODE_EXECUTION
preferred_executor: codex
package_ref: <approved-task-package>
task_anchor:
  revision: <trusted-revision>
  relation: ancestor
resume_cursor: null | <cursor>
return_surface: CONTROL_REVIEW
```

`task_anchor` is required when the package depends on a repository baseline. `resume_cursor` is optional for a fresh P32 start and expected for a control-plane-approved P33 continuation when a continuation point is known.

## P32 starting-state rules

For fresh implementation:

- inspect actual repository state;
- verify the task anchor according to its declared relation;
- record actual starting revision;
- do not require `actual HEAD == task_anchor.revision` when the contract says `ancestor`;
- if actual HEAD is a valid descendant and does not contain contradictory/out-of-scope state, continue from actual HEAD;
- if the anchor is absent from ancestry or repository state is otherwise incompatible, fail closed with exact evidence.

## P33 reconciliation rules

P33 classifies the observed repository position before resuming:

1. **EXACT_CURSOR** — actual HEAD equals `resume_cursor.revision`: resume from `next_action`.
2. **DESCENDANT_CURSOR** — cursor revision is an ancestor of actual HEAD: inspect only the delta after the cursor, preserve verified valid work, advance the cursor if appropriate, and resume at the first incomplete verified step. Do not replay already-completed work.
3. **ANCHOR_DESCENDANT_WITHOUT_CURSOR** — task anchor is an ancestor of actual HEAD but no accepted cursor exists: reconcile completed vs pending work from the anchor/package boundary, establish a cursor, then resume.
4. **DIVERGED** — neither the accepted cursor nor required anchor relation can be established, history was rewritten incompatibly, or repository state contradicts Authority/scope: fail closed with `BLOCKED_EXECUTION_DIVERGENCE` or the more specific existing Authority/environment blocker.

A historical expected HEAD mismatch by itself is not a blocker when the observed HEAD is a valid descendant under the task anchor/cursor relation.

## Evidence return

Existing materialization rules remain unchanged. Before returning a completed P32/P33 result to `CONTROL_REVIEW`, the exact result must be materialized at a reviewer-accessible durable ref and returned as `materialized_ref` plus `result_revision`.

The execution cursor is navigation metadata, not P34 proof. P34 still independently resolves the materialized result.

## Compatibility and scope

This change is additive to the existing execution-surface model. It does not:

- change P-stage ownership;
- create a new lifecycle stage or semantic execution surface;
- turn Codex into the loop controller;
- move Gate judgment away from ChatGPT/`CONTROL_REVIEW`;
- alter Project State Authority/Gate/Evidence semantics;
- permit scope expansion or upstream semantic invention.

## Acceptance cases

The implementation must prove at least:

- `anchor=old revision`, `actual=descendant`, no cursor -> P33 reconciliation/resume, not starting-state mismatch;
- `cursor=accepted revision`, `actual=cursor` -> exact resume;
- `cursor=accepted revision`, `actual=descendant` -> reconcile only descendant delta and preserve valid work;
- unrelated/diverged actual revision -> fail closed;
- shared and generated Skill instructions contain the same invariants;
- existing execution-surface and composition tests remain green.
