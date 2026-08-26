# Project State Manifest v0.1

Use this reference when a project contains `.aegis/` or when the user asks to persist, inspect, validate, supersede, or resume machine-readable project authority/gate state.

## Canonical layout

```text
.aegis/
├── project.json
├── authorities.json
├── gates.json
├── evidence.json
└── state.json
```

The first four files are authored project-control manifests. `state.json` is generated and reproducible. Do not treat `.aegis/` as a replacement for PRDs, ADRs, architecture docs, schemas, tests, CI, or release evidence.

## Startup sequence

```text
Read authored manifests
→ validate structure/cross-references
→ validate dependency and supersession DAGs
→ recompute derived state when tooling exists
→ compare committed state.json
→ identify stale/needs-review authority or gates
→ select Earliest Untrusted Layer
→ route
```

If the repository provides `tools.aegis_state`, prefer its deterministic validator/recompute/check commands.

## Authority registry

Each Authority should have stable `id`, `scope`, `kind`, `version`, `status`, `ref`, and `depends_on[]`. Optional `supersedes` records version replacement; optional `change_class` is `clarification | compatible | semantic | breaking | ownership`.

Keep at most one `Current` Authority per `(scope, kind)`. Reject dangling dependencies, dependency cycles, and supersession cycles. Only validity-bearing relationships belong in `depends_on`.

## Gate history versus current validity

Do not rewrite a historical Gate verdict because upstream authority later changes. Keep verdict and validity separate:

```json
{
  "id": "G5",
  "verdict": "PASS",
  "validity": "stale"
}
```

Use existing Aegis Gate verdicts only. Validity is `current | needs_review | stale`. A current PASS/PASS_WITH_FINDINGS must cite available evidence and must not depend on Superseded/Historical authority.

## Supersession invalidation

When a dependency still points at a superseded authority, determine impact from the replacement:

```text
semantic / breaking / ownership -> stale
clarification / compatible       -> needs_review
missing/unknown impact           -> needs_review
```

Propagate invalidation through validity-bearing dependencies. `stale` dominates `needs_review`.

An explicit impact review may mark one dependent authority `unaffected` only when the review cites evidence and all of that evidence is available. Missing review evidence fails closed.

Do not invalidate the whole project merely because one document version changed.

## Evidence registry

Evidence status is `available | missing | invalid | superseded`. A Gate that requires missing/invalid/superseded evidence cannot remain current-valid PASS.

## Generated state

`state.json` may include manifest digest, active stage hint, earliest untrusted layer, blocking findings, stale/needs-review authorities and gates, and recommended next stage. Keep v0.1 output deterministic; do not add timestamps that prevent byte-stable recomputation.

If committed `state.json` differs from fresh recomputation, treat it as state drift and do not silently trust the cache.

## Routing

- stale/needs-review Authority dependency → `P21` (then `P22`/`P23` when needed);
- Gate/Evidence-only invalidity → `P34`;
- manifest/source authority conflict → `P21`/`P22`;
- no invalidity → continue normal Aegis routing.

The manifest tells Aegis where to look and what is believed current; it never outranks contradictory Current Authority evidence.
