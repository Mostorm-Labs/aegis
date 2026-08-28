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
- The coding surface still inspects current repository state and must return a blocker rather than invent missing Authority or semantic decisions.

A surface handoff changes where work executes; it does not transfer Primary Owner semantics. This Skill remains the P30-P33 owner while the authorized repository-heavy work executes on the code surface.

Default OpenAI profile: `CONTROL_REASONING -> ChatGPT`, `CODE_EXECUTION -> Codex`. Treat these product names as profile metadata, not lifecycle Authority.

## Composition boundary

Once substantive execution begins in this Skill's owned stage family, this Skill is the unique Primary Owner for that substantive result. It may consume Project State support from `aegis-project-state`; Project State support does not transfer ownership.

Direct Primary-to-Primary substantive chaining is forbidden. After completing its owned stage, this Skill may suggest an unambiguous next Skill, but it must not automatically execute substantive work owned by that next Primary.

If an earlier untrusted layer blocks safe execution, emit an `ownership_handoff` to `aegis` and stop substantive execution. Do not repair or silently redefine the earlier layer inside this specialist.
