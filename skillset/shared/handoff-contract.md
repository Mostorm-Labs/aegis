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
return_surface: CONTROL_REVIEW
```

The `stage_owner` remains the Primary Owner across a surface handoff unless a separate valid `ownership_handoff` occurs. `package_ref` identifies the approved P31 task package or equivalent execution contract. The receiving execution surface must fail closed rather than invent missing semantic or Authority decisions.

Direct Primary-to-Primary substantive chaining is forbidden. A completed Primary may suggest the next Skill, but may not automatically continue substantive execution under a different Primary Owner.

Composite fallback requires explicit specialist-unavailability evidence; absence from a partial trace is not sufficient.

A bounded `Router -> Primary -> Router` blocker return is allowed only when the Primary emits no substantive result, discovers an earlier blocker not already conclusively established, and returns once to `aegis`. Other ownership cycles are invalid.

Superpowers owns coding-agent mechanics; Aegis owns authority, lifecycle routing, evidence obligations, task boundaries, Gate review, and release readiness.
