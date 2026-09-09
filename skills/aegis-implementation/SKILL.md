---
name: aegis-implementation
description: Control Aegis implementation planning, coding task packaging, authorized implementation scope, and interrupted-work resume. Use when current Authority is trusted and the user wants an implementation plan, Codex/agent work packages, controlled coding execution, or to resume partially completed implementation without losing valid work.
---

# Aegis Implementation

Own `P30` Implementation Planning, `P31` Task Packaging, `P32` Implementation control, and `P33` Resume Interrupted Work.

## Implementation control

Decompose Authority into evidence-gated vertical slices. P31 MUST freeze an `EXECUTION_CLOSURE_CONTRACT` containing required/forbidden changes, required tests/oracles, required vs optional hosted verification, blocking vs corroborative evidence, terminal success, explicit terminal blocker classes, and `continue_until_terminal_state: true`.

Once P31 authorizes implementation, the blocking completion target is stable. P32 executes the full frozen closure contract until success or an explicit terminal blocker; it does not return merely because an intermediate coding/test checkpoint finished. P33 resumes interrupted valid work and MUST NOT become a loop for incrementally adding package or Verification obligations omitted before execution.

Use Superpowers when available for coding mechanics such as brainstorming, writing plans, TDD, systematic debugging, worktree isolation, plan execution, and verification-before-completion. Do not duplicate those mechanics here.

**Earlier untrusted layer:** if implementation discovers missing or contradictory Authority, an ambiguous closure contract, a Verification Design omission, or a P31 package omission, classify the root cause and return to the earliest owning layer. Do not redesign upstream truth or continuously extend P33 inside a coding task.

Read [references/implementation-control.md](references/implementation-control.md) and shared handoff/Authority contracts.

## Execution-surface boundary

`Stage Ownership != Execution Surface`.

- `P30` Implementation Planning and `P31` Task Packaging default to `CONTROL_REASONING`.
- `P32` Implementation and `P33` Resume Interrupted Work default to `CODE_EXECUTION` when a suitable coding surface is available.
- Repository-backed execution MUST establish `repository.provider/full_name`, resolve the same-repository `package_materialization_ref`, and only then inspect `task_anchor` or `resume_cursor`. Missing, mismatched, ambiguous, or unavailable identity is terminal `BLOCKED_REPOSITORY_IDENTITY` with `continue_execution: false`; a bare SHA is not a repository locator.
- Before a `CONTROL_REASONING -> CODE_EXECUTION` transfer, produce an approved task package and carry it as `package_ref` in a `surface_handoff`.
- Whenever a rendered `surface_handoff` contains `preferred_executor: codex`, place the following exact execution instruction immediately before the YAML envelope. The prefix is execution-trigger/rendering metadata only; it does not expand Authority, package scope, evidence, Gate, or Project State:

  > 请按以下 Aegis handoff 直接执行：以 `package_ref` 为任务授权，按 `task_anchor/resume_cursor` 核对当前状态并从首个未完成步骤继续；若状态冲突则 fail closed。

- The package return policy is normative: continue through all remaining executable items in the frozen closure contract during the same execution unless an explicit terminal blocker is encountered.
- For repository-backed execution that depends on a repository baseline, the package MUST carry a non-null `task_anchor` describing the trusted ancestry relation. `Task Anchor != Execution Cursor`.
- `resume_cursor` is nullable at the schema level. When P33 has an accepted continuation point, the handoff MUST carry a non-null `resume_cursor` with the execution ref, accepted revision, verified `completed_through`, and `next_action`. If no accepted continuation point exists yet, `resume_cursor: null` is valid.
- A resumable task must not use historical HEAD equality as its only starting-state predicate. A valid descendant of the anchor/cursor is reconciled rather than rejected solely because HEAD advanced.
- The coding surface may resolve ordinary uncertainty from repository/Authority/package/tests, but must return a blocker rather than invent missing Authority or semantic decisions.
- Before returning P32/P33 results to `CONTROL_REVIEW`, satisfy the **reviewer-accessible** durable result/evidence boundary frozen by P31 and the selected profile. A local-only result is insufficient when independent reviewability was frozen as blocking.
- Return the exact `materialized_ref` whenever the frozen contract requires durable reviewer-accessible materialization. Under Standard, do not force an evidence-only descendant when an exact PR head/result revision and applicable hosted CI already satisfy the frozen identity/evidence contract. Under Full, stricter materialization/provenance may remain blocking when justified.

## Verification-bound repository execution

For a repository-backed P32/P33 task governed by a Verification-bound package, do not begin mutation until all package-frozen proof bindings are exact: VerificationSpec, obligation-set when required, TrustedBasis, scope contract, acceptance-oracle refs, evidence-compilation contract, and the Execution Closure Contract. Run `PackageBindingPreflight` and `EvidenceContractPreflight` before execution; a floating label, future-phase dependency, structurally unsatisfiable requirement, unresolved semantic choice, provider-impossible requirement, or ambiguous terminal criterion is a blocker rather than executor discretion.

Repository identity preflight still occurs first. Never pass floating labels such as `accepted A4`, `latest Gate`, `latest run`, or ambient branch truth to the executor as trust identities.

Execution returns carry exact identities required by the frozen contract, such as `result_revision`, reviewer-accessible `materialized_ref` when required, `evidence_input_refs`, and provider run/attempt/job/artifact refs. Do not manually type proof totals already owned by EvidenceArtifact / ProofEvaluation, and do not emit or imply official Gate PASS.

## P33 resume reconciliation

Before resuming interrupted repository work, classify the observed execution position:

- `EXACT_CURSOR`: observed HEAD equals `resume_cursor.revision`; resume from the cursor's `next_action`.
- `DESCENDANT_CURSOR`: cursor revision is an ancestor of observed HEAD; inspect only the descendant delta, preserve verified valid work, and do not replay completed work.
- `ANCHOR_DESCENDANT_WITHOUT_CURSOR`: no accepted cursor exists but the task anchor is an ancestor of observed HEAD; reconcile completed versus pending work, establish a cursor, then resume at the first incomplete verified step.
- `DIVERGED`: accepted cursor/anchor ancestry cannot be established, history is incompatibly rewritten, or observed state contradicts Authority/scope; fail closed with `BLOCKED_EXECUTION_DIVERGENCE` or a more specific existing blocker.

Apply `P33_REPETITION_GUARD`: new work caused by a P31 omission routes to P31 as `TASK_PACKAGE_DEFECT`; new work caused by a Verification Design omission routes to the Verification owner as `VERIFICATION_DESIGN_DEFECT`. Root cause, not retry count, decides. The cursor remains navigation metadata; it neither expands the authorized task package nor becomes Gate evidence.

A surface handoff changes where work executes; it does not transfer Primary Owner semantics. This Skill remains the P30-P33 owner while the authorized repository-heavy work executes on the code surface.

Default OpenAI profile: `CONTROL_REASONING -> ChatGPT`, `CODE_EXECUTION -> Codex`. Treat these product names as profile metadata, not lifecycle Authority.

## Composition boundary

Once substantive execution begins in this Skill's owned stage family, this Skill is the unique Primary Owner for that substantive result. It may consume Project State support from `aegis-project-state`; Project State support does not transfer ownership.

Direct Primary-to-Primary substantive chaining is forbidden. After completing its owned stage, this Skill may suggest an unambiguous next Skill, but it must not automatically execute substantive work owned by that next Primary.

If an earlier untrusted layer blocks safe execution, emit an `ownership_handoff` to `aegis` and stop substantive execution. Do not repair or silently redefine the earlier layer inside this specialist.
