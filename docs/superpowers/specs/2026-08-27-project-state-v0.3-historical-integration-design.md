# Project State v0.3 Historical Integration Durability Design

## Status

**Proposed design spec — requires human review before implementation planning.**

## Context

Aegis Project State v0.2 successfully separated Authority status, Gate verdict/validity, and repository Integration lifecycle, and it correctly propagates current `BLOCKED_*` Gates into derived routing.

The formal 08 self-host rerun then confirmed F08-03:

- PR #4 was truly integrated into `main` at revision `555bac21d485fc4530680c61719fc36831021b0d`;
- its supporting 07 v0.1 Authority was later correctly superseded by v0.2;
- the old Gate therefore became stale under current Authority semantics;
- v0.2 strict validation then rejected the still-true `integrated` record because `integrated` requires a current/current-valid Gate.

This makes two truthful facts impossible to represent simultaneously.

Defect classification:

- Primary: `SPEC_DEFECT`
- Secondary: `MISSING_CONTRACT`

The repair belongs in project-state Authority before implementation.

## Design objective

Preserve durable repository integration history while still detecting current project-control invalidity.

The design must allow:

```text
historical integration occurrence = true
current applicability = historical
```

without allowing stale current work to bypass Gate review.

## Non-goals

- no new Gate verdict vocabulary;
- no automated Git merge/rebase behavior;
- no event sourcing;
- no cross-repository distributed project state;
- no redesign of Authority dependency or supersession graphs;
- no manual `applicability` authoring;
- no weakening of current `awaiting_integration` safety checks;
- no special case for PR #4 or Aegis itself.

## Considered approaches

### A. Author applicability/actionability fields

Add authored `applicability` to Integration and authored `actionability` to Gate.

Advantages:

- simple validator logic;
- explicit manifest values.

Rejected because:

- creates new duplicated authored state;
- allows drift between Authority graph and manually maintained applicability;
- increases the number of facts users must keep synchronized.

### B. Durable occurrence + derived applicability/actionability — selected

Keep Integration occurrence and historical Gate verdict as authored facts. Compute current applicability/actionability from current Authority/Gate/Evidence state.

Advantages:

- preserves immutable historical truth;
- avoids redundant authored state;
- current routing stays deterministic;
- directly fixes F08-03 with the smallest conceptual extension.

Trade-off:

- compute/validator logic becomes more explicit about history versus current actionability.

### C. Append-only event ledger

Replace current lifecycle registries with an event-sourced model.

Rejected for v0.3 because it is much broader than F08-03 and would redesign persistence and replay semantics without current evidence that this complexity is needed.

## Core domain model

v0.3 defines three independent dimensions:

```text
Historical Occurrence
Current Applicability
Current Actionability
```

### Historical occurrence

A fact that happened and is supported by durable evidence.

Examples:

- PR merged into `main`;
- Gate returned PASS at that time;
- a specific revision was integrated.

Historical occurrence is not reversed because later Authority changes.

### Current applicability

Whether the historical occurrence still represents current project baseline semantics.

Derived values:

```text
current
needs_review
stale
historical
```

### Current actionability

Whether a Gate/Integration state requires current workflow action.

Examples:

- awaiting integration under a current PASS Gate -> actionable implementation handoff;
- current stale Gate -> actionable P34 review;
- stale Gate whose entire subject Authority is superseded history -> non-actionable historical record.

## Integration model

### Authored fields

Keep the existing Integration lifecycle statuses:

```text
awaiting_integration
integrated
closed_unmerged
```

These statuses describe lifecycle occurrence, not current applicability.

### `integrated` validation

An `integrated` record is valid when:

1. `gate_id` resolves;
2. historical Gate verdict is `PASS` or `PASS_WITH_FINDINGS`;
3. `integrated_revision` exists;
4. occurrence evidence exists;
5. occurrence evidence is available.

It does not require the Gate to remain effective-current after later Authority supersession.

This means a once-valid integration remains part of audit history even when its Authority is later superseded.

### `awaiting_integration` validation

An `awaiting_integration` record still represents a current proposed action, so it requires:

1. Gate verdict `PASS` or `PASS_WITH_FINDINGS`;
2. Gate is effective-current;
3. supporting evidence is available;
4. Gate is not stale/needs-review under current Authority.

This preserves v0.2's fail-closed merge handoff behavior.

### `closed_unmerged`

Remains historical evidence that the implementation candidate did not enter the baseline. It does not require current Gate validity and does not route as awaiting work.

## Derived Integration applicability

For each Integration, compute applicability from the current Authority/Gate/Evidence graph.

Required values:

```text
current
needs_review
stale
historical
```

Rules:

- current-effective Gate + current supporting Authority -> `current`;
- current Authority but needs-review Gate/evidence -> `needs_review`;
- current Authority but stale/invalid Gate/evidence -> `stale`;
- supporting Authority is Superseded/Historical and occurrence is durable history -> `historical`.

The projection is generated into `state.json`, not authored into `integrations.json`.

The final JSON shape must be deterministic and schema-defined. Preferred representation:

```json
{
  "integration_applicability": [
    {"integration_id":"int-pr4","applicability":"historical"},
    {"integration_id":"int-pr7","applicability":"current"}
  ]
}
```

Sort by `integration_id` for byte-stable generation.

## Gate model

### Historical Gate verdict

`verdict` remains the decision that occurred when the Gate was evaluated.

A later supersession does not rewrite historical PASS to another verdict.

### Gate current validity

`validity` and derived dependency validity continue to describe whether the Gate can support current work.

### Derived Gate actionability

v0.3 distinguishes:

```text
historical Gate
current actionable Gate
```

A stale Gate is classified as historical/non-actionable when the reason it is stale is that all relevant supporting Authority for its reviewed subject is now Superseded/Historical and the Gate is retained solely as provenance for completed history.

A Gate remains current-actionable when it relates to still-current Authority and its evidence/validity is stale or needs review.

Generated state should expose historical Gates explicitly, preferably:

```json
{
  "historical_gates": ["gate-project-state-pr4"]
}
```

`stale_gates[]` and `needs_review_gates[]` must contain current-actionable validity problems, not provenance-only historical Gates.

## Routing rules

### Historical Gate

```text
Gate stale only because subject Authority is superseded history
→ retain in historical_gates
→ no current blocker solely from this condition
→ no P34 route solely from this condition
```

### Current stale Gate

```text
subject Authority remains current
+ Gate/evidence is stale
→ actionable validity problem
→ current blocker
→ verification / P34
```

### Historical Integration

```text
integrated occurrence
+ supporting Authority superseded
→ occurrence stays integrated
→ applicability = historical
→ no integration handoff
```

### Awaiting current Integration

```text
awaiting_integration
+ current-valid PASS Gate
→ current applicability
→ implementation handoff
```

## Supersession behavior

Supersession may change applicability and actionability, but never occurrence.

Invariant:

```text
Authority supersession may invalidate current support.
Authority supersession cannot erase what happened.
```

This applies to both Gate provenance and repository Integration provenance.

## Versioning

This is a semantic breaking change to v0.2, so v0.3 receives new schema/generator versions.

Required version artifacts:

```text
schemas/project-state/v0.3/
SCHEMA_VERSION = "0.3"
GENERATOR_VERSION = "0.3"
```

Do not mutate existing v0.1/v0.2 schema meaning in place.

v0.2 remains Current until v0.3 passes P34 and is explicitly superseded/integrated.

## Verification design

The implementation plan must begin with RED tests. Required oracles:

### R03-01 — durable integration after supersession

```text
integrated occurrence
+ supporting Authority later superseded
→ manifest VALID
→ integration status remains integrated
→ applicability = historical
```

### R03-02 — historical PASS Gate supports occurrence provenance

A historical PASS/PASS_WITH_FINDINGS Gate may continue to support an already-integrated occurrence.

### R03-03 — historical BLOCKED Gate cannot prove integration

An integrated occurrence whose historical supporting Gate verdict is blocked must be rejected.

### R03-04 — awaiting work still requires current Gate

`awaiting_integration` with stale or non-current-effective Gate must remain invalid.

### R03-05 — historical stale Gate is non-actionable

A Gate stale solely because its Authority was superseded must appear in historical Gate projection and must not route to P34.

### R03-06 — stale current Gate remains actionable

A Gate tied to current Authority that is stale must remain in actionable stale Gate state and route to P34.

### R03-07 — occurrence evidence remains mandatory

Missing/invalid integration evidence invalidates an `integrated` occurrence even when historical.

### R03-08 — real Aegis self-host acceptance oracle

Input reality:

```text
PR #4 integrated at 555bac21d485fc4530680c61719fc36831021b0d
07 v0.1 = Superseded
PR #7 integrated at 8ca7b49d40a17e8cb7ffba86632da3aeae5e911c
07 v0.2 = Current
OpenAI real behavioral baseline = BLOCKED_ENVIRONMENT
```

Required result:

```text
int-pr4 occurrence = integrated
int-pr4 applicability = historical
int-pr7 occurrence = integrated
int-pr7 applicability = current
gate-project-state-pr4 = historical/non-actionable
blocking_gates = [gate-openai-real-baseline]
earliest_untrusted_layer = verification
recommended_next_stage = P34
strict root check = STATE_OK
```

R03-08 is mandatory acceptance evidence. Generic unit tests without real self-host closure are insufficient.

## Error handling / fail-closed rules

Do not repair failing history by:

- restoring Superseded Authority to Current;
- deleting historical Integration records;
- changing `integrated` to `closed_unmerged` after a real merge;
- fabricating a new current Gate for old history;
- hand-editing generated `state.json`;
- treating all stale Gates as historical;
- weakening `awaiting_integration` current-validity requirements.

If the algorithm cannot determine whether a Gate is historical-only versus current-actionable, classify conservatively as `needs_review` and route to Authority/Gate review rather than silently declaring it historical.

## Components expected to change after plan approval

Likely implementation scope:

```text
tools/aegis_state/model.py
tools/aegis_state/compute.py
tools/aegis_state/__init__.py
schemas/project-state/v0.3/*.json
tests/project_state/*
examples/project-state/minimal/.aegis/*
skills/aegis/references/project-state.md
skills/aegis/SKILL.md (thin version/reference update only if needed)
.github/workflows/project-state.yml
```

Exact file-level tasks belong in P30/P31, not this design spec.

## Migration / compatibility

- v0.1 and v0.2 remain readable historical schema trees;
- v0.3 tooling should fail clearly on unsupported older manifests unless an explicit migration path is invoked;
- migration from v0.2 to v0.3 should preserve Integration occurrence records and Gate verdict history;
- no migration is allowed to delete PR #4 historical integration truth merely to satisfy current validation.

## Acceptance and supersession

P34 may accept v0.3 only if:

1. all v0.3 focused regressions pass;
2. existing project-state behavior unrelated to F08-03 remains green;
3. schema parsing/validation passes;
4. Skill validation/package passes after reference update;
5. root Aegis self-host strict check returns `STATE_OK` with truthful repository history;
6. current OpenAI `BLOCKED_ENVIRONMENT` remains the primary `verification/P34` blocker;
7. PR #4 becomes historical/non-actionable rather than erased;
8. repository CI provides fresh evidence.

Only after P34 acceptance:

```text
v0.2 -> Superseded/Historical
v0.3 -> Current Replacement Authority
```

Then rerun 08 formally. 09 remains downstream and must not begin until the self-hosting contract is trustworthy.
