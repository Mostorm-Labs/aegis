# Project State Manifest v0.4

Use this reference when a project contains `.aegis/` or when the user asks to persist, inspect, validate, supersede, resume, or integrate machine-readable project state. Project State tooling is version-aware: apply v0.4 semantics only to v0.4 manifests and preserve v0.3 semantics for v0.3 projects.

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

The first five files are authored project-control manifests. `state.json` is generated and reproducible. Repository truth, Current Authority, Gate decisions, Evidence, and Integration occurrence remain distinct sources of truth.

## Startup sequence

```text
Read authored manifests
→ determine one consistent supported schema version
→ validate structure and cross-references
→ validate Authority/supersession DAGs
→ validate Gate/Evidence/Integration invariants for that version
→ recompute derived state when tooling exists
→ compare committed state.json
→ compare manifests with repository reality
→ identify earliest untrusted layer
→ route or hand off
```

If `tools.aegis_state` exists, prefer its deterministic `validate`, `recompute`, and `check` commands over conversational reimplementation.

## Core v0.4 semantic split

Keep these dimensions independent:

```text
Integration Occurrence
!=
Gate Conformance
!=
Current Applicability
!=
Current Actionability
```

- **Occurrence** asks what actually happened in the repository.
- **Gate Conformance** asks whether that occurrence was authorized by its Gate verdict.
- **Applicability** asks whether the occurrence still applies to the current Authority/baseline.
- **Actionability** asks what Aegis should route or block now.

A real repository occurrence must never be erased, renamed, or converted into PASS merely because it violated governance.

## Authority registry

Each Authority has stable `id`, `scope`, `kind`, `version`, `status`, `ref`, and `depends_on[]`. Optional `supersedes` records an accepted replacement; optional `change_class` is:

`clarification | compatible | semantic | breaking | ownership`

Keep at most one `Current` Authority per `(scope, kind)`. A Proposed replacement does not supersede Current Authority merely because it exists. P23 must explicitly perform promotion/supersession.

When a dependency still points at a Superseded/Historical Authority, derive impact from the accepted replacement. Missing impact information fails closed to review.

## Gate history, validity, and actionability

Gate verdict and Gate validity remain separate:

```text
Gate verdict = what the Gate decided
Gate validity = whether that decision currently supports work
```

Only a current-actionable, effective-current blocked Gate contributes an active blocker:

```text
BLOCKED_AUTHORITY      → authority / P21
BLOCKED_EVIDENCE       → verification / P34
BLOCKED_IMPLEMENTATION → implementation / P35
BLOCKED_ENVIRONMENT    → verification / P34
```

A repository merge never changes a blocked verdict into PASS. Missing Gate acceptance evidence stays missing after integration.

Historical/non-actionable Gate provenance remains durable after Authority supersession and completed Integration. Mixed current/historical validity-bearing Authority fails closed to P21.

## Evidence registry

Evidence status is:

`available | missing | invalid | superseded`

Current PASS/PASS_WITH_FINDINGS must cite available Gate evidence. Every `integrated` occurrence must independently cite available occurrence evidence and a non-empty `integrated_revision`.

Do not reuse repository integration evidence as Gate acceptance evidence unless the Gate contract explicitly defines it as such.

## Repository Integration lifecycle

Authored statuses remain:

```text
awaiting_integration
integrated
closed_unmerged
```

### `awaiting_integration`

This is a future/current action candidate. It still requires:

- Gate verdict `PASS` or `PASS_WITH_FINDINGS`;
- declared and effective-current Gate;
- available integration evidence;
- no historical/stale/needs-review Gate condition.

A blocked Gate must never produce an integration recommendation.

### `integrated` in v0.4

This records an occurrence that repository evidence proves actually entered the target baseline. It requires:

- referenced Gate exists;
- non-empty `integrated_revision`;
- available occurrence evidence.

Unlike v0.3, the referenced Gate does **not** have to be PASS/PASS_WITH_FINDINGS. If the Gate was blocked, the occurrence is still recorded and its Gate conformance is derived as `nonconforming`.

Example:

```text
Integration.status      = integrated
Gate.verdict            = BLOCKED_EVIDENCE
Gate conformance        = nonconforming
Integration occurrence  = preserved
Gate blocker            = preserved
```

### `closed_unmerged`

This records a completed candidate that did not enter the target baseline. It is historical for Integration applicability and has no integration-occurrence conformance classification.

## Derived Gate conformance

For v0.4 `integrated` occurrences:

```text
PASS / PASS_WITH_FINDINGS → conforming
BLOCKED_*                  → nonconforming
```

Generated state exposes:

```json
{
  "integration_conformance": [
    {"integration_id":"int-pr9","conformance":"nonconforming"}
  ],
  "nonconforming_integrations": ["int-pr9"]
}
```

Conformance is derived historical truth; it is never authored into `integrations.json` and never silently rewrites the Gate verdict.

## Derived Integration applicability

Applicability remains independent of conformance:

`current | needs_review | stale | historical`

A nonconforming integration can be `current` when the merged revision is in the active baseline and its validity-bearing Authority/Gate are still current. The active blocked Gate continues to determine routing.

Rules for mixed/historical/stale Authority and Gate validity remain the same as v0.3.

## Generated state v0.4

`state.json` adds:

- `integration_conformance[]`;
- `nonconforming_integrations[]`.

It continues to include manifest digest, active stage, earliest untrusted layer, findings, Authority/Gate validity projections, blocking Gates, awaiting Integrations, Integration applicability, recommended stage, and handoff.

Do not add nondeterministic timestamps. `state.json` is cache, not Authority. Any mismatch with fresh recomputation is state drift.

## Routing precedence

Choose the earliest open/untrusted layer across Authority validity, Gate validity/actionability, active blocked verdicts, and Integration candidates:

```text
problem → requirement → object → behavior → schema → operation
→ architecture → module → flow → platform → engineering
→ verification → authority → implementation → release
```

A nonconforming integration does not create a competing route when its still-current blocked Gate already supplies the correct route. Surface the nonconformance as a finding and route from the Gate.

## v0.3 backward compatibility

When all authored manifests declare `schema_version = "0.3"`, preserve v0.3 semantics and generated shape. In particular:

- `integrated` still requires a historical PASS/PASS_WITH_FINDINGS Gate;
- no v0.4 conformance fields are generated;
- v0.4 permissiveness must not reinterpret historical v0.3 projects.

Reject mixed schema versions within one Project State manifest set.

## Safety boundary

The manifest tells Aegis where to look and what project-control state is recorded; it never outranks contradictory Current Authority or repository evidence. If GitHub/repository evidence proves an occurrence that the authored state cannot represent, route to Authority review rather than falsifying repository truth.