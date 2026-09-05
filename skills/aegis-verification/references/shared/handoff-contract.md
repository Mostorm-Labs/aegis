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

Repository identity is resolved before any `task_anchor` or `resume_cursor`
handling. A bare revision is not a repository locator.

A Codex execution prefix is rendering/trigger metadata only. It does not transfer ownership, expand Authority or package scope, create Evidence, issue a Gate verdict, or mutate Project State. Whenever a rendered `surface_handoff` contains `preferred_executor: codex`, it MUST place this exact execution instruction immediately before the YAML envelope:

> 请按以下 Aegis handoff 直接执行：以 `package_ref` 为任务授权，按 `task_anchor/resume_cursor` 核对当前状态并从首个未完成步骤继续；若状态冲突则 fail closed。

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

### Repository identity preflight

Every repository-backed handoff MUST establish the declared repository before
resolving a package, checking an anchor, classifying a cursor, or mutating a
worktree:

```yaml
repository:
  provider: github
  full_name: <owner/repository>
package_ref: <exact-package-revision>
package_materialization_ref: <durable-same-repository-ref>
```

The executor resolves the declared repository and package materialization ref
in that order. A missing, mismatched, ambiguous, or unavailable repository
identity is terminal:

```yaml
status: BLOCKED_REPOSITORY_IDENTITY
continue_execution: false
```

`repository identity != task anchor != execution cursor`; a bare SHA is never
a repository locator. This preflight also applies to P33 resume and P36
reverification, before any anchor/cursor classification or repair mutation.

The `stage_owner` remains the Primary Owner across a surface handoff unless a separate valid `ownership_handoff` occurs. `package_ref` identifies the approved P31 task package or equivalent execution contract. The receiving execution surface must fail closed rather than invent missing semantic or Authority decisions.

## Execution position

`Task Anchor != Execution Cursor`.

A task package tells the executor what is authorized. A `task_anchor` tells repository execution what trusted history the task must descend from. A `resume_cursor` tells the executor where previously reconciled authorized execution currently is.

Any repository-backed package whose execution depends on a repository baseline MUST include a non-null `task_anchor`:

```yaml
task_anchor:
  revision: <40-char-revision>
  relation: ancestor
```

`relation: ancestor` means the anchor revision must be an ancestor of the accepted starting or resume revision. It does not mean the anchor must equal HEAD. A resumable task must not use historical HEAD equality as its only starting-state predicate.

`resume_cursor` is nullable at the schema level. When a control-plane-accepted P33 continuation point is known, the handoff MUST include a non-null `resume_cursor`:

```yaml
resume_cursor:
  execution_ref: <branch-or-durable-ref>
  revision: <40-char-revision>
  completed_through:
    - <verified-completed-step>
  next_action: <first-incomplete-verified-step>
```

If no accepted continuation point exists yet, `resume_cursor: null` is valid. The cursor is navigation metadata only. It does not expand scope, replace Authority, or become Gate evidence.

P33 classifies the observed repository position before resuming:

- `EXACT_CURSOR`: observed HEAD equals `resume_cursor.revision`; resume from `next_action`.
- `DESCENDANT_CURSOR`: the cursor revision is an ancestor of observed HEAD; inspect only the delta after the cursor, preserve verified valid work, and do not replay completed work.
- `ANCHOR_DESCENDANT_WITHOUT_CURSOR`: no accepted cursor exists but the task anchor is an ancestor of observed HEAD; reconcile completed versus pending work, establish a cursor, then resume at the first incomplete verified step.
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

## Verification-bound execution return

When a P31 package carries a frozen VerificationSpec / obligation-set / TrustedBasis / scope / acceptance-oracle / evidence-compilation binding, execution returns carry exact identities and navigation only. They may include:

```yaml
result_revision: <exact-result-revision>
materialized_ref: <reviewer-resolvable-exact-result-ref>
evidence_input_refs:
  - <exact-EvidenceInputRef>
provider_run_refs:
  - <exact-provider-run-attempt-job-artifact-identity>
```

They MUST NOT introduce independently authored duplicate proof facts such as `tests_passed`, `tests_skipped`, copied obligation totals, copied ProofEvaluation state totals, or a Gate verdict. Machine facts remain owned by the exact EvidenceArtifact / provider observation / ProofEvaluation that produced them. A return may navigate to those objects but cannot become a competing evidence producer.

A P32/P33 execution return MUST NOT claim official P34 PASS. Any platform corroboration owned by CONTROL_REVIEW remains pending until `aegis-gate-review` independently resolves the exact result/evidence/provider graph.
