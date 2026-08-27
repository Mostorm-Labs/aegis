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
