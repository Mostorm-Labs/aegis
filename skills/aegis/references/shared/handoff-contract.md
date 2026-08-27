# Handoff Contract

A handoff is execution/navigation metadata, never Authority, Evidence, Gate, or Project State.

Logical fields: `owner_skill`, `completed_stage`, `status`, `authority_refs`, `evidence_required`, `next_stage`, `suggested_skill`, `blockers`.

Only the central `aegis` Skill owns ambiguous/cross-domain rerouting. Specialists may suggest an unambiguous next Skill. Earlier blockers return to `aegis`. Handoff cycles are invalid.

Superpowers owns coding-agent mechanics; Aegis owns authority, lifecycle routing, evidence obligations, task boundaries, Gate review, and release readiness.
