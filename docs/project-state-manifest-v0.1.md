# Aegis Project State Manifest + Authority Dependency Graph v0.1

**Status:** Superseded / Historical by `Aegis Project State Manifest + Authority Dependency Graph v0.2`.

This document preserves the original v0.1 machine-readable project-control contract and the history accepted through PR #4. PR #4 was integrated into `main` at `555bac21d485fc4530680c61719fc36831021b0d`.

## Supersession

Current replacement: `docs/project-state-manifest-v0.2.md`.

Reason: 08 Self-Hosting confirmed two authority defects that v0.1 could not represent safely:

- **F08-01 — SPEC_DEFECT + MISSING_CONTRACT:** current `BLOCKED_*` Gate verdicts did not propagate into derived project blockers/routing, allowing a false-clean state.
- **F08-02 — MISSING_CONTRACT:** repository integration lifecycle was absent, so P34 PASS could not be distinguished from implementation integrated into the current repository baseline.

v0.2 preserves the v0.1 schema files as history, adds blocked-Gate propagation and a separate integration lifecycle, and supersedes this document as Current Authority. Do not delete or rewrite this historical contract.

## Canonical layout

```text
.aegis/
├── project.json
├── authorities.json
├── gates.json
├── evidence.json
└── state.json
```

The first four files are authored project-control manifests. `state.json` is generated and reproducible; it is never independent authority.

## Required invariants

- one Current Authority per `(scope, kind)`;
- no dangling validity dependency;
- no dependency cycle;
- no supersession cycle;
- PASS/PASS_WITH_FINDINGS must cite evidence;
- a `current` PASS gate cannot depend on Superseded/Historical authority or unavailable evidence;
- generated state must be reproducible from the authored manifests.

## Invalidation

Supersession does not erase historical Gate verdicts. Instead, dependent authority and gate validity is computed as `current`, `needs_review`, or `stale`.

Default impact:

```text
semantic / breaking / ownership -> stale
clarification / compatible       -> needs_review
unknown                          -> needs_review
```

An explicit impact review can mark a dependency `unaffected` only when the referenced review evidence is available.

## Startup rule

When a project contains `.aegis/`, Aegis should:

```text
Read authored manifests
→ validate schema/IDs/graphs
→ recompute state
→ compare state.json
→ detect drift
→ select Earliest Untrusted Layer
→ route to minimum safe stage
```

If manifest metadata conflicts with actual Current Authority, route to P21/P22. Do not let `.aegis/` silently win the conflict.

## Historical implementation references

- Design spec: `docs/superpowers/specs/2026-08-26-project-state-manifest-design.md`
- Plan: `docs/superpowers/plans/2026-08-26-project-state-manifest.md`
- Schemas: `schemas/project-state/v0.1/`
- Runtime tooling lineage: `tools/aegis_state/`
- Tests lineage: `tests/project_state/`
