# Handoff Contract

Handoff metadata is ephemeral execution/navigation metadata, never Authority, Evidence, Gate, Integration, or Project State.

## Roles and edges

A **Primary Owner** owns the substantive result for one lifecycle stage family. A **Supporting Skill** may provide bounded facts or validation without becoming the substantive owner. The central `aegis` Router owns genuine ambiguity, routing-only results, accepted earlier-blocker terminal results, and compatibility fallback only under its evidence precondition.

`aegis-project-state` is the only generally allowlisted Supporting Skill in v0.2.

`Support Edge != Ownership Handoff Edge`.

A support edge returns bounded facts to the existing or future Primary Owner without transferring ownership:

```yaml
type: support_return
supporting_skill: aegis-project-state
facts: {}
```

An ownership handoff is a terminal return from a Primary Owner that discovered an earlier untrusted layer and cannot safely continue:

```yaml
type: ownership_handoff
from_owner: <primary>
to: aegis
reason: earlier_untrusted_layer
requested_stage: <stage>
earliest_untrusted_layer: <stage-or-layer>
status: <BLOCKED_*>
suggested_next_stage: <stage>
```

The recipient named in an `ownership_handoff` becomes the final-answer owner only for that routing or blocked result. A `support_return` never makes the Supporting Skill the final-answer owner for another stage family.

## Execution-surface handoff

`Surface Handoff != Ownership Handoff`.

A surface handoff changes where authorized work executes. It does not transfer ownership, change Current Authority, create Evidence, issue a Gate verdict, or mutate Project State merely by occurring.

```yaml
type: surface_handoff
stage: P32
stage_owner: aegis-implementation
from_surface: CONTROL_REASONING
to_surface: CODE_EXECUTION
preferred_executor: codex
reason: repository_heavy_execution
package_ref: <task-package-ref>
task_anchor:
  revision: <trusted-revision>
  relation: ancestor
resume_cursor: null
return_surface: CONTROL_REVIEW
```

The `stage_owner` remains the Primary Owner across a surface handoff unless a separate valid `ownership_handoff` occurs. `package_ref` identifies the approved P31 task package or equivalent execution contract. The receiving execution surface must fail closed rather than invent missing semantic or Authority decisions.

## Execution position

`Task Anchor != Execution Cursor`.

A task package tells the executor what is authorized. A `task_anchor` tells repository execution what trusted history the task must descend from. A `resume_cursor` tells the executor where previously reconciled authorized execution currently is.

Repository-backed packages should encode a stable anchor such as:

```yaml
task_anchor:
  revision: <40-char-revision>
  relation: ancestor
```

`relation: ancestor` means the anchor revision must be an ancestor of the accepted starting or resume revision. It does not mean the anchor must equal HEAD. A resumable task must not use historical HEAD equality as its only starting-state predicate.

An accepted P33 continuation may additionally carry:

```yaml
resume_cursor:
  execution_ref: <branch-or-durable-ref>
  revision: <40-char-revision>
  completed_through:
    - <verified-completed-step>
  next_action: <first-incomplete-verified-step>
```

The cursor is navigation metadata only. It does not expand scope, replace Authority, or become Gate evidence.

P33 classifies the observed repository position before resuming:

- `EXACT_CURSOR`: observed HEAD equals `resume_cursor.revision`; resume from `next_action`.
- `DESCENDANT_CURSOR`: the cursor revision is an ancestor of observed HEAD; inspect only the delta after the cursor, preserve verified valid work, and do not replay completed work.
- `ANCHOR_DESCENDANT_WITHOUT_CURSOR`: no accepted cursor exists but `task_anchor.revision` is an ancestor of observed HEAD; reconcile completed versus pending work, establish a cursor, then resume at the first incomplete verified step.
- `DIVERGED`: neither the accepted cursor nor required anchor relation can be established, or repository history/state contradicts Authority or authorized scope; fail closed with `BLOCKED_EXECUTION_DIVERGENCE` or a more specific existing Authority/environment blocker.

A historical expected-HEAD mismatch by itself is not divergence when the observed revision is a valid descendant under the declared anchor/cursor relation.

Direct Primary-to-Primary substantive chaining is forbidden. A completed Primary may suggest the next Skill, but may not automatically continue substantive execution under a different Primary Owner.

Composite fallback requires explicit specialist-unavailability evidence; absence from a partial trace is not sufficient.

A bounded `Router -> Primary -> Router` blocker return is allowed only when the Primary emits no substantive result, discovers an earlier blocker not already conclusively established, and returns once to `aegis`. Other ownership cycles are invalid.

Superpowers owns coding-agent mechanics; Aegis owns authority, lifecycle routing, evidence obligations, task boundaries, Gate review, and release readiness.

## Evidence materialization before review return

Before an execution surface returns result evidence to a review surface, the exact result must be materialized into a reviewer-accessible durable evidence boundary. Repository execution normally materializes the exact result commit/ref on a remote branch or pull request that the reviewer can independently resolve; non-repository environments may use an equivalent durable artifact or immutable ref.

The evidence return must carry `materialized_ref` identifying that reviewer-accessible result. A local-only commit SHA, worktree path/state, test transcript, or executor message is context only and is insufficient for P34 corroboration.

If the executor cannot produce a reviewer-accessible `materialized_ref`, return `BLOCKED_EVIDENCE` with the exact materialization blocker instead of claiming review readiness. The review surface resolves `materialized_ref` independently before relying on executor claims.
