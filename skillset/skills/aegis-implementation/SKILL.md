---
name: aegis-implementation
description: Control Aegis implementation planning, coding task packaging, authorized implementation scope, and interrupted-work resume. Use when current Authority is trusted and the user wants an implementation plan, Codex/agent work packages, controlled coding execution, or to resume partially completed implementation without losing valid work.
---

# Aegis Implementation

Own `P30` Implementation Planning, `P31` Task Packaging, `P32` Implementation control, and `P33` Resume Interrupted Work.

## Implementation control

Decompose Authority into evidence-gated vertical slices, package each task with Authority/scope/non-goals/tests/evidence/dependencies/exit criteria, authorize only assigned implementation scope, and resume interrupted work by inspecting current diff/state before changing it.

Use Superpowers when available for coding mechanics such as brainstorming, writing plans, TDD, systematic debugging, worktree isolation, plan execution, and verification-before-completion. Do not duplicate those mechanics here.

**Earlier untrusted layer:** if implementation discovers missing or contradictory Authority, stop and hand back to `aegis`; classify before fixing and do not redesign upstream truth inside a coding task.

Read [references/implementation-control.md](references/implementation-control.md) and shared handoff/Authority contracts.

## Execution-surface boundary

`Stage Ownership != Execution Surface`.

- `P30` Implementation Planning and `P31` Task Packaging default to `CONTROL_REASONING`.
- `P32` Implementation and `P33` Resume Interrupted Work default to `CODE_EXECUTION` when a suitable coding surface is available.
- Before a `CONTROL_REASONING -> CODE_EXECUTION` transfer, produce an approved task package and carry it as `package_ref` in a `surface_handoff`.
- Whenever a rendered `surface_handoff` contains `preferred_executor: codex`, place the following exact execution instruction immediately before the YAML envelope. The prefix is execution-trigger/rendering metadata only; it does not expand Authority, package scope, evidence, Gate, or Project State:

  > 请按以下 Aegis handoff 直接执行：以 `package_ref` 为任务授权，按 `task_anchor/resume_cursor` 核对当前状态并从首个未完成步骤继续；若状态冲突则 fail closed。

- For repository-backed execution that depends on a repository baseline, the package MUST carry a non-null `task_anchor` describing the trusted ancestry relation. `Task Anchor != Execution Cursor`.
- `resume_cursor` is nullable at the schema level. When P33 has an accepted continuation point, the handoff MUST carry a non-null `resume_cursor` with the execution ref, accepted revision, verified `completed_through`, and `next_action`. If no accepted continuation point exists yet, `resume_cursor: null` is valid.
- A resumable task must not use historical HEAD equality as its only starting-state predicate. A valid descendant of the anchor/cursor is reconciled rather than rejected solely because HEAD advanced.
- The coding surface still inspects current repository state and must return a blocker rather than invent missing Authority or semantic decisions.
- Before returning P32/P33 results to `CONTROL_REVIEW`, materialize the exact result into a reviewer-accessible durable evidence boundary and return its `materialized_ref`. A local-only commit/worktree/test transcript is not sufficient `CONTROL_REVIEW` evidence.
- If the result cannot be materialized for independent review, return `BLOCKED_EVIDENCE` with the exact blocker instead of claiming review readiness.

## P33 resume reconciliation

Before resuming interrupted repository work, classify the observed execution position:

- `EXACT_CURSOR`: observed HEAD equals `resume_cursor.revision`; resume from the cursor's `next_action`.
- `DESCENDANT_CURSOR`: cursor revision is an ancestor of observed HEAD; inspect only the descendant delta, preserve verified valid work, and do not replay completed work.
- `ANCHOR_DESCENDANT_WITHOUT_CURSOR`: no accepted cursor exists but the task anchor is an ancestor of observed HEAD; reconcile completed versus pending work, establish a cursor, then resume at the first incomplete verified step.
- `DIVERGED`: accepted cursor/anchor ancestry cannot be established, history is incompatibly rewritten, or observed state contradicts Authority/scope; fail closed with `BLOCKED_EXECUTION_DIVERGENCE` or a more specific existing blocker.

The cursor remains navigation metadata. It neither expands the authorized task package nor becomes Gate evidence.

A surface handoff changes where work executes; it does not transfer Primary Owner semantics. This Skill remains the P30-P33 owner while the authorized repository-heavy work executes on the code surface.

Default OpenAI profile: `CONTROL_REASONING -> ChatGPT`, `CODE_EXECUTION -> Codex`. Treat these product names as profile metadata, not lifecycle Authority.

## Composition boundary

Once substantive execution begins in this Skill's owned stage family, this Skill is the unique Primary Owner for that substantive result. It may consume Project State support from `aegis-project-state`; Project State support does not transfer ownership.

Direct Primary-to-Primary substantive chaining is forbidden. After completing its owned stage, this Skill may suggest an unambiguous next Skill, but it must not automatically execute substantive work owned by that next Primary.

If an earlier untrusted layer blocks safe execution, emit an `ownership_handoff` to `aegis` and stop substantive execution. Do not repair or silently redefine the earlier layer inside this specialist.
