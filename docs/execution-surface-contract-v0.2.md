# Aegis Execution Surface Contract v0.2

Status: **Current Additive Authority v0.2 — execution-position repair**

Supersedes: `docs/execution-surface-contract-v0.1.md`

v0.2 preserves the v0.1 execution-surface vocabulary, P30-P36 ownership mapping, task-package compression rule, reviewer-accessible evidence-materialization boundary, and independent P34 review. It adds one missing contract: how a repository-backed task identifies its stable trusted baseline and its moving accepted resume point across `CONTROL_REASONING -> CODE_EXECUTION` handoffs. It also standardizes the execution-trigger rendering for Codex-targeted handoffs without changing lifecycle or Authority semantics.

## 1. Preserved v0.1 semantics

The following remain unchanged:

- `Stage Ownership != Execution Surface`.
- `CONTROL_REASONING`, `CODE_EXECUTION`, `CONTROL_REVIEW`, and `CODE_REVERIFY` retain their v0.1 meanings.
- P30/P31 execute on `CONTROL_REASONING`; P32/P33 on `CODE_EXECUTION`; P34/P35 on `CONTROL_REVIEW`; P36 on `CODE_REVERIFY`.
- `aegis-implementation` remains Primary Owner for P30-P33; `aegis-gate-review` remains Primary Owner for P34-P36.
- `surface_handoff` changes execution location only.
- Exact results must still be materialized at a reviewer-accessible durable ref and returned as `result_revision` + `materialized_ref` before P34 can corroborate them.
- Agent/executor claims remain context, not Gate evidence.

## 2. Missing contract repaired by v0.2

A P31 task package can remain valid while the executor's branch advances through authorized implementation commits. Therefore the task's historical package revision cannot also serve as the only valid resume HEAD.

Core invariant:

> `Task Anchor != Execution Cursor`.

A task package tells the executor **what is authorized**. A task anchor tells repository execution **what trusted history the work must descend from**. A resume cursor tells the executor **where accepted authorized execution currently is**.

A resumable task **must not** use historical HEAD equality as its only starting-state predicate.

## 3. Task anchor

Any repository-backed P31 package whose execution depends on a repository baseline MUST include a non-null `task_anchor`:

```yaml
task_anchor:
  revision: <40-char-revision>
  relation: ancestor
```

For `relation: ancestor`, the executor must establish that `task_anchor.revision` is an ancestor of the accepted starting/resume revision. The relation does not require `HEAD == task_anchor.revision`.

The task anchor is stable for the package unless upstream Authority legitimately supersedes the package itself.

## 4. Resume cursor

`resume_cursor` is nullable at the schema level. When P33 has a control-plane-accepted continuation point, the handoff MUST include a non-null `resume_cursor`:

```yaml
resume_cursor:
  execution_ref: <branch-or-durable-ref>
  revision: <40-char-revision>
  completed_through:
    - <verified-completed-step>
  next_action: <first-incomplete-verified-step>
```

If no accepted continuation point exists yet, `resume_cursor: null` is valid. The resume cursor is execution/navigation metadata. It does not become Authority, Evidence, Gate, Integration, or Project State; it does not authorize new files, new semantics, or scope expansion.

## 5. Surface handoff v0.2

A repository-backed P32/P33 handoff is represented as below. When the rendered handoff uses `preferred_executor: codex`, the presentation MUST prepend this exact execution instruction immediately before the YAML envelope:

> 请按以下 Aegis handoff 直接执行：以 `package_ref` 为任务授权，按 `task_anchor/resume_cursor` 核对当前状态并从首个未完成步骤继续；若状态冲突则 fail closed。

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
resume_cursor: null | <accepted-cursor>
return_surface: CONTROL_REVIEW
```

The standard prefix is execution-trigger/rendering metadata only. It does not alter stage ownership, Current Authority, package scope, evidence obligations, Gate semantics, or Project State. It is conditional on `preferred_executor: codex`; other executor profiles are not required to render it.

`package_ref` continues to carry the authorized work contract. `task_anchor` and `resume_cursor` carry execution-position semantics only. The nullability shown above does not weaken the conditional requirements in §§3-4: baseline-dependent repository execution requires a non-null anchor, and a known accepted P33 continuation requires a non-null cursor.

## 6. P32 starting-state semantics

For fresh repository implementation:

1. inspect actual repository/branch/worktree state;
2. verify Current Authority and package scope;
3. verify the declared task-anchor relation;
4. capture actual starting revision before edits;
5. if actual HEAD is a compatible descendant under `relation: ancestor`, continue from actual HEAD rather than failing solely because it is newer than the package revision;
6. fail closed when required ancestry cannot be established or observed state contradicts Authority/scope.

Historical HEAD equality is not the default oracle for an ancestry-based package.

## 7. P33 reconciliation

P33 must classify the observed position before resuming:

### `EXACT_CURSOR`

Observed HEAD equals `resume_cursor.revision`.

Action: resume from the cursor's `next_action`.

### `DESCENDANT_CURSOR`

`resume_cursor.revision` is an ancestor of observed HEAD.

Action: inspect only the descendant delta, preserve verified valid work, update completed/pending facts if necessary, and resume at the first incomplete verified step. **Do not replay** already-completed work merely because HEAD advanced.

### `ANCHOR_DESCENDANT_WITHOUT_CURSOR`

No accepted cursor exists, but `task_anchor.revision` is an ancestor of observed HEAD.

Action: reconcile package obligations against the descendant state, establish a resume cursor, and continue from the first incomplete verified step.

### `DIVERGED`

Neither accepted cursor nor required task-anchor ancestry can be established, history is incompatibly rewritten, or observed repository state contradicts Current Authority or authorized scope.

Action: fail closed with `BLOCKED_EXECUTION_DIVERGENCE` or a more specific existing Authority/environment blocker. Do not silently reset, force-push, discard valid work, or invent a new baseline.

A historical expected-HEAD mismatch by itself is not `DIVERGED` when the observed revision is a valid descendant under the declared relation.

## 8. Evidence return remains independent

Resume reconciliation does not weaken the v0.1 evidence boundary. Before P32/P33 returns completion to `CONTROL_REVIEW`, the exact result still must be materialized to a reviewer-accessible durable ref and returned as:

```yaml
result_revision: <exact-result-revision>
materialized_ref: <reviewer-accessible-durable-ref>
return_surface: CONTROL_REVIEW
```

P34 resolves `materialized_ref` independently. A `resume_cursor` is not evidence of correctness.

## 9. Skill instruction requirements

`aegis-implementation` must:

- require the exact standard execution prefix immediately before every rendered `surface_handoff` whose `preferred_executor` is `codex`;
- require a non-null repository task anchor whenever P31 execution depends on a repository baseline;
- require a non-null accepted resume cursor whenever P33 has a known control-plane-accepted continuation point;
- allow `resume_cursor: null` only when no accepted continuation point exists yet;
- inspect actual repository state instead of assuming the package commit is the current HEAD;
- distinguish `EXACT_CURSOR`, `DESCENDANT_CURSOR`, `ANCHOR_DESCENDANT_WITHOUT_CURSOR`, and `DIVERGED`;
- preserve valid descendant work and resume from the first incomplete verified step;
- reject historical HEAD equality as the only resume predicate;
- fail closed on real ancestry/Authority divergence;
- preserve v0.1 materialization and ownership boundaries.

Generated/distributed Skills must preserve these instructions from the canonical skillset sources.

## 10. Acceptance

v0.2 is accepted when deterministic and hosted verification prove:

1. shared handoff instructions define `Task Anchor != Execution Cursor`;
2. baseline-dependent repository execution conditionally requires a non-null `task_anchor` with explicit repository relation semantics;
3. `resume_cursor` is nullable only when no accepted continuation point exists, and a known accepted P33 continuation conditionally requires a non-null cursor with execution ref/revision and continuation facts;
4. P33 defines all four reconciliation outcomes;
5. behavioral dogfood exercises `EXACT_CURSOR`, `DESCENDANT_CURSOR`, `ANCHOR_DESCENDANT_WITHOUT_CURSOR`, and `DIVERGED`, including no-replay descendant resume and fail-closed divergence;
6. genuine divergence fails closed with `BLOCKED_EXECUTION_DIVERGENCE` or a more specific valid blocker;
7. historical HEAD equality is not the sole resumable-task predicate;
8. every rendered `surface_handoff` with `preferred_executor: codex` carries the exact standard execution prefix immediately before its YAML envelope;
9. canonical and generated Skill instructions agree;
10. existing execution-surface, composition, routing, Project State, and evaluation regressions remain green;
11. final result is reviewer-accessible and P34 can independently resolve it.

## 11. Non-goals

v0.2 does not:

- change lifecycle ownership;
- create a new P-stage or execution surface;
- make Codex the Aegis loop controller;
- change Project State Authority/Gate/Evidence semantics;
- permit autonomous scope expansion;
- permit rewriting or discarding executor history to manufacture a matching HEAD;
- replace the reviewer-accessible materialization boundary.

## 12. Origin of the repair

The execution-position repair was triggered by a real handoff failure mode in which a control-plane prompt retained an earlier P32 expected HEAD while the code-execution branch already contained later authorized implementation, test-strengthening, and evidence commits. The executor correctly observed the mismatch but lacked a shared contract for distinguishing valid descendant progress from true divergence. v0.2 promotes the previously local ancestry-based preflight pattern into shared normative execution-position semantics. The Codex prefix addition closes a separate presentation ambiguity: a valid handoff envelope must also make it explicit that the receiving Codex surface should begin authorized execution rather than merely inspect the protocol payload.
