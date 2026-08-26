# Aegis Project State Manifest + Authority Dependency Graph v0.1 Design

## Status

Current Design Authority v0.1. User-approved on 2026-08-26.

## Goal

Persist project-control metadata in `.aegis/` so Aegis can validate current authority dependencies, recompute derived state deterministically, detect stale gates after supersession, and route work from the earliest untrusted layer without reconstructing the whole project state from scratch.

## Architecture

Use four authored JSON manifests plus one generated JSON state file:

```text
.aegis/
├── project.json
├── authorities.json
├── gates.json
├── evidence.json
└── state.json       # generated
```

JSON is chosen for deterministic parsing, JSON Schema support, stdlib tooling, and CI portability. `state.json` is never an independent authority; it is reproducible from the four authored manifests.

## Core boundaries

1. `.aegis/` is project-control metadata, not a replacement for PRDs, ADRs, schemas, architecture docs, tests, or CI artifacts.
2. A manifest may point at authority, but it cannot silently override authority. Material conflicts route to P21/P22.
3. Gate `verdict` preserves historical review truth. Gate `validity` answers whether that verdict remains usable after upstream change.
4. State computation never rewrites authored manifests in v0.1.
5. Ordinary cross-references are not dependency edges. Only validity-bearing dependencies belong in `depends_on`.

## Manifest model

### project.json

Required: `schema_version: "0.1"`, `project.id`, `project.name`, and `project.profile` (`lite | standard | full`). Optional fields include `project.required_layers[]` and `project.lifecycle_hint`.

### authorities.json

Each authority contains `id`, `scope`, `kind`, `version`, `status`, `ref`, `depends_on[]`, optional `supersedes`, and optional `change_class` (`clarification | compatible | semantic | breaking | ownership`).

Top-level `impact_reviews[]` may record an explicit review with `id`, `source_authority`, `dependent_authority`, `outcome` (`unaffected | needs_review | stale`), and `evidence_ids[]`. An `unaffected` review only suppresses invalidation if all referenced evidence is available.

### gates.json

Each gate contains `id`, `stage`, the existing Aegis `verdict`, independent `validity` (`current | needs_review | stale`), `authority_ids[]`, and `evidence_ids[]`. Historical verdicts are preserved even when validity changes.

### evidence.json

Each evidence item contains `id`, `type`, `ref`, `status` (`available | missing | invalid | superseded`), and optional `subject_ids[]`.

### state.json

Generated fields include `schema_version`, `generator_version`, `manifest_digest`, `active_stage`, `earliest_untrusted_layer`, `blocking_findings[]`, stale/needs-review authority and gate lists, and `recommended_next_stage`. No timestamp is included so recomputation is deterministic.

## Validation invariants

Reject duplicate IDs, multiple Current authorities for one `(scope, kind)`, dangling dependencies, dependency cycles, supersession cycles, dangling supersedes targets, dangling Gate/impact-review references, PASS/PASS_WITH_FINDINGS without evidence, current PASS depending on Superseded/Historical authority, and current PASS using unavailable evidence.

## Invalidation semantics

When a dependency points to a superseded authority, find the replacement whose `supersedes` points to it.

```text
semantic / breaking / ownership -> stale
clarification / compatible       -> needs_review
missing replacement/change class -> needs_review
```

An evidence-backed impact review may override the direct impact. `unaffected` is valid only when all review evidence is available. Invalidation propagates transitively through validity-bearing dependencies and `stale` dominates `needs_review`.

Gate effective validity is computed from authority effective validity and evidence availability while preserving its historical verdict.

## Routing semantics

Map the earliest affected authority kind to the corresponding Aegis lifecycle layer. Unknown kinds fall back to `authority`. Authority invalidation routes to `P21`; Gate/Evidence-only invalidation routes to `P34`; no invalidity preserves the project's lifecycle hint.

## CLI

```text
python3 -m tools.aegis_state.cli validate <project-root>
python3 -m tools.aegis_state.cli recompute <project-root>
python3 -m tools.aegis_state.cli recompute <project-root> --write
python3 -m tools.aegis_state.cli check <project-root>
```

`validate` is strict. `recompute` can calculate derived state from structurally valid manifests even when a declared Gate validity has drifted, so supersession does not prevent the tool from diagnosing the stale state. `check` compares committed `state.json` with fresh recomputation.

## Non-goals

No event sourcing, cross-repository distributed state, automatic Notion edits, authored-manifest mutation during recompute, new Gate verdict vocabulary, generated-state authority, or blanket invalidation of the whole project.

## Evidence plan

TDD covers duplicate Current authority, dangling dependency, dependency cycle, supersession cycle, PASS without evidence, invalid current PASS dependency, breaking/compatible supersession, transitive propagation, evidence-gated unaffected review, deterministic recomputation, and committed state drift. CI validates a minimal example end to end.
