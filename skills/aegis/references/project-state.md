# Project State Manifest v0.2

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
→ validate authority/supersession DAGs
→ validate Gate/Evidence/Integration invariants
→ recompute derived state when tooling exists
→ compare committed state.json
→ identify earliest untrusted layer
→ route or hand off
```

If the repository provides `tools.aegis_state`, prefer its deterministic `validate`, `recompute`, and `check` commands over reimplementing the algorithm conversationally.

## Authority registry

Each Authority has stable `id`, `scope`, `kind`, `version`, `status`, `ref`, and `depends_on[]`. Optional `supersedes` records replacement; optional `change_class` is:

`clarification | compatible | semantic | breaking | ownership`

Keep at most one `Current` Authority per `(scope, kind)`. Reject dangling dependencies, dependency cycles, and supersession cycles. Only validity-bearing relationships belong in `depends_on`; ordinary references do not.

## Gate history, validity, and active blockers

Keep historical Gate verdict separate from current validity. A historical PASS can become `stale` without rewriting the verdict.

Only a Gate whose **effective validity is current** may contribute an active `BLOCKED_*` verdict to derived state. Use this fixed map:

```text
BLOCKED_AUTHORITY      → authority / P21
BLOCKED_EVIDENCE       → verification / P34
BLOCKED_IMPLEMENTATION → implementation / P35
BLOCKED_ENVIRONMENT    → verification / P34
```

`PASS` and `PASS_WITH_FINDINGS` do not create a blocker from verdict alone. A stale or needs-review Gate is handled by validity semantics, not resurrected as a current blocker from its historical verdict.

Generated state records current blocked Gate IDs in `blocking_gates[]`.

## Supersession invalidation

When a dependency still points at a superseded Authority, determine impact from the replacement:

```text
semantic / breaking / ownership → stale
clarification / compatible       → needs_review
missing/unknown impact           → needs_review
```

Propagate invalidation through validity-bearing dependencies. `stale` dominates `needs_review`.

An explicit impact review may mark one dependent `unaffected` only when the review cites evidence and all cited evidence is available. Missing review evidence fails closed. Do not invalidate the entire project merely because one document version changed.

## Evidence registry

Evidence status is:

`available | missing | invalid | superseded`

A current PASS/PASS_WITH_FINDINGS must cite available evidence and cannot depend on Superseded/Historical Authority.

## Repository integration lifecycle

`integrations.json` records whether Gate-approved implementation has entered its target repository baseline. It does not perform Git operations.

Each integration record has stable `id`, `kind`, `ref`, `gate_id`, `status`, `target_ref`, and `evidence_ids[]`. Status is one of:

```text
awaiting_integration
integrated
closed_unmerged
```

`integrated` additionally requires non-empty `integrated_revision`.

For `awaiting_integration` or `integrated`:

- `gate_id` must resolve to `PASS` or `PASS_WITH_FINDINGS`;
- the Gate must be effective-current, not merely declared current;
- integration evidence must exist and be available;
- a blocked/stale Gate cannot support integration.

Keep these facts independent:

```text
Authority status ≠ Gate verdict/validity ≠ Integration status
```

Aegis records and routes integration state. A human or implementation workflow such as `superpowers:finishing-a-development-branch` performs merge/rebase/integration.

## Generated state

`state.json` v0.2 may include:

- manifest digest;
- active stage hint;
- earliest untrusted layer;
- blocking findings;
- stale / needs-review authorities and gates;
- `blocking_gates[]`;
- `awaiting_integrations[]`;
- recommended next stage;
- `recommended_handoff`.

Keep output deterministic; do not add timestamps that prevent byte-stable recomputation. If committed `state.json` differs from fresh recomputation, treat that as state drift and do not trust the cache.

The manifest digest must cover integration state as well as project, authorities, gates, and evidence.

## Routing precedence

Choose the earliest open/untrusted layer across all Authority validity, Gate validity, active Gate verdict, and integration candidates using the lifecycle order:

```text
problem → requirement → object → behavior → schema → operation
→ architecture → module → flow → platform → engineering
→ verification → authority → implementation → release
```

Examples:

- `BLOCKED_ENVIRONMENT` plus an awaiting PR → primary `verification / P34`; preserve the integration finding as secondary.
- no earlier blocker and one awaiting integration → `earliest_untrusted_layer=implementation`, `recommended_next_stage=null`, `recommended_handoff=superpowers:finishing-a-development-branch`.
- stale/needs-review Authority dependency → `P21` (then `P22`/`P23` if required).
- Gate/Evidence-only invalidity → `P34`.
- manifest/source Authority conflict → `P21`/`P22`.

The manifest tells Aegis where to look and what project-control state is recorded; it never outranks contradictory Current Authority or repository evidence.
