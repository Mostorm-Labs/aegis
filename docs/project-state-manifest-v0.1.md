# Aegis Project State Manifest + Authority Dependency Graph v0.1

**Status:** Current Design Authority v0.1 — implementation in progress.

This document defines the machine-readable project-control state used by Aegis. It is the repository companion to the approved 07 design authority.

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

## Implementation references

- Design spec: `docs/superpowers/specs/2026-08-26-project-state-manifest-design.md`
- Plan: `docs/superpowers/plans/2026-08-26-project-state-manifest.md`
- Schemas: `schemas/project-state/v0.1/`
- Runtime tooling: `tools/aegis_state/`
- Tests: `tests/project_state/`
