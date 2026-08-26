# Project State Manifest v0.3

Use this reference when a project contains `.aegis/` or when the user asks to persist, inspect, validate, supersede, resume, or integrate machine-readable project state.

## Canonical layout

```text
.aegis/
├── project.json
├── authorities.json
├── gates.json
├── evidence.json
├── integrations.json
└── state.json
```

The first five files are authored project-control manifests. `state.json` is generated and reproducible. Do not treat `.aegis/` as a replacement for PRDs, ADRs, architecture docs, schemas, tests, CI, release evidence, or repository truth.

## Startup sequence

```text
Read authored manifests
→ validate structure and cross-references
→ validate Authority/supersession DAGs
→ validate Gate/Evidence/Integration invariants
→ recompute derived state when tooling exists
→ compare committed state.json
→ identify earliest untrusted layer
→ route or hand off
```

If the repository provides `tools.aegis_state`, prefer its deterministic `validate`, `recompute`, and `check` commands over reimplementing the algorithm conversationally.

## Core v0.3 semantic split

Keep these dimensions independent:

```text
Historical Occurrence
!=
Current Applicability
!=
Current Actionability
```

A later Authority supersession may change whether an old result is still applicable or actionable. It must not erase a repository integration, Gate verdict, or other occurrence that actually happened and is supported by durable evidence.

## Authority registry

Each Authority has stable `id`, `scope`, `kind`, `version`, `status`, `ref`, and `depends_on[]`. Optional `supersedes` records replacement; optional `change_class` is:

`clarification | compatible | semantic | breaking | ownership`

Keep at most one `Current` Authority per `(scope, kind)`. Reject dangling dependencies, dependency cycles, and supersession cycles. Only validity-bearing relationships belong in `depends_on`; ordinary references do not.

When a dependency still points at a superseded Authority, determine impact from the replacement:

```text
semantic / breaking / ownership → stale
clarification / compatible       → needs_review
missing/unknown impact           → needs_review
```

An explicit impact review may mark one dependent `unaffected` only when it cites available evidence. Missing review evidence fails closed.

## Gate history, validity, and actionability

Keep historical Gate verdict separate from current validity:

```text
Gate verdict = what the Gate decided at the time
Gate validity = whether that decision still supports current work
```

Only a current-actionable Gate whose effective validity is `current` may contribute an active `BLOCKED_*` verdict. Use:

```text
BLOCKED_AUTHORITY      → authority / P21
BLOCKED_EVIDENCE       → verification / P34
BLOCKED_IMPLEMENTATION → implementation / P35
BLOCKED_ENVIRONMENT    → verification / P34
```

`PASS` and `PASS_WITH_FINDINGS` do not create a blocker from verdict alone.

### Historical Gate

A Gate becomes historical/non-actionable only when both are true:

1. all validity-bearing `authority_ids` are `Superseded/Historical`; and
2. the Gate is retained as provenance for a completed Integration (`integrated` or `closed_unmerged`).

Such a Gate is emitted in `historical_gates[]`. It does not enter current `stale_gates[]`, `needs_review_gates[]`, `blocking_gates[]`, or current routing solely because its old Authority was superseded.

A historical `BLOCKED_*` verdict remains audit history. It cannot support an `integrated` occurrence and must not reactivate a current blocker solely because the record still exists.

### Mixed Authority Gate

If a Gate's validity-bearing Authority set mixes `Current/Proposed` and `Superseded/Historical`, do not silently classify it as history.

```text
mixed Current + Historical
→ needs_review
→ current actionable Authority uncertainty
→ authority / P21
```

If the complete validity-bearing Authority set cannot be determined, fail closed the same way.

### Current stale Gate

If the Gate still belongs to current Authority and its Gate/evidence validity is stale or needs review, it remains actionable and routes under existing Gate validity semantics, normally `verification / P34`.

## Evidence registry

Evidence status is:

`available | missing | invalid | superseded`

A current PASS/PASS_WITH_FINDINGS must cite available evidence. Integration occurrence evidence for an `integrated` record must also be available; later Authority supersession does not waive proof that the integration actually happened.

## Repository Integration lifecycle

`integrations.json` records repository/change lifecycle facts. It does not perform Git operations.

Status remains:

```text
awaiting_integration
integrated
closed_unmerged
```

### `awaiting_integration`

This represents a current proposed action. It requires:

- Gate verdict `PASS` or `PASS_WITH_FINDINGS`;
- Gate declared and effective-current;
- Gate not historical/stale/needs-review;
- integration evidence exists and is available.

If no earlier blocker exists, route to:

```text
earliest_untrusted_layer = implementation
recommended_next_stage = null
recommended_handoff = superpowers:finishing-a-development-branch
```

### `integrated`

This is durable occurrence history. It requires:

- referenced Gate exists;
- historical Gate verdict is `PASS` or `PASS_WITH_FINDINGS`;
- non-empty `integrated_revision`;
- integration occurrence evidence exists and is available.

It does **not** require the Gate to remain current-valid forever after later Authority supersession.

Never rewrite a real historical merge as `closed_unmerged` merely because its Authority later becomes historical.

### `closed_unmerged`

This records that the candidate did not enter the target baseline. It is completed history and does not create an integration handoff.

## Derived Integration applicability

Applicability is generated into `state.json`, never authored into `integrations.json`.

Values:

```text
current
needs_review
stale
historical
```

Rules:

- all Gate Authorities current + effective-current Gate/evidence → `current`;
- mixed Current + Historical Authority or unresolved membership → `needs_review`;
- still-current Authority with stale/invalid Gate/evidence → `stale`;
- completed occurrence with all validity-bearing Gate Authorities Superseded/Historical → `historical`.

Generated projection is deterministic and ordered by Integration ID:

```json
{
  "integration_applicability": [
    {"integration_id":"int-old","applicability":"historical"},
    {"integration_id":"int-current","applicability":"current"}
  ]
}
```

## Generated state

`state.json` v0.3 includes deterministic project-control projections such as:

- manifest digest;
- active stage hint;
- earliest untrusted layer;
- blocking findings;
- stale / needs-review authorities;
- actionable `stale_gates[]` / `needs_review_gates[]`;
- `historical_gates[]`;
- `blocking_gates[]`;
- `awaiting_integrations[]`;
- `integration_applicability[]`;
- recommended next stage;
- `recommended_handoff`.

Do not add timestamps that prevent byte-stable recomputation. If committed `state.json` differs from fresh recomputation, treat it as state drift and do not trust the cache.

The manifest digest covers project, authorities, gates, evidence, and integrations.

## Routing precedence

Choose the earliest open/untrusted layer across Authority validity, Gate validity/actionability, active blocked verdicts, and Integration candidates using:

```text
problem → requirement → object → behavior → schema → operation
→ architecture → module → flow → platform → engineering
→ verification → authority → implementation → release
```

Examples:

- `BLOCKED_ENVIRONMENT` plus an awaiting PR → primary `verification / P34`; preserve integration as secondary.
- mixed Current/Historical Gate Authority → `authority / P21` rather than silently treating it as historical.
- historical Gate retained only for completed provenance → no route solely from that history.
- current stale Gate/evidence → `verification / P34`.
- no earlier blocker + current awaiting integration → finishing-development-branch handoff.
- manifest/source Authority conflict → `P21`/`P22`.

The manifest tells Aegis where to look and what project-control state is recorded; it never outranks contradictory Current Authority or repository evidence.
