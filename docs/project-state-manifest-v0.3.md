# Aegis Project State Historical Integration Durability + Gate History Semantics v0.3

Status: **Proposed Replacement Authority v0.3**

This document is the repository companion to the Notion authority `07 v0.3 Project State Historical Integration Durability + Gate History Semantics`.

It is driven by the formal 08 self-host rerun finding **F08-03** and does not supersede v0.2 until P34 acceptance and repository integration complete.

## Authority basis

Current v0.2 correctly closes:

- F08-01: active `BLOCKED_*` Gate verdicts propagate into derived project state and routing;
- F08-02: Authority status, Gate verdict/validity, and repository Integration status are distinct dimensions.

The formal Aegis self-host rerun then exposed F08-03:

```text
PR #4 was historically integrated
        +
its supporting 07 v0.1 Authority was later superseded
        ↓
v0.2 marks the old Gate stale
        ↓
v0.2 rejects the still-true integration occurrence
```

Classification:

- Primary: `SPEC_DEFECT`
- Secondary: `MISSING_CONTRACT`
- Repair owner: 07 Project State Authority

The defect is not that the validator failed to match v0.2. The validator correctly enforced an incomplete v0.2 contract.

## Scope

v0.3 only defines:

1. durable historical Integration occurrence;
2. derived current Integration applicability;
3. historical Gate record versus current actionable Gate;
4. supersession semantics connecting those dimensions.

## Non-goals

v0.3 does not:

- add new Gate verdicts;
- make Aegis perform Git merge/rebase actions;
- introduce event sourcing;
- introduce cross-repository distributed state;
- redesign the Authority DAG;
- redesign Evidence registry semantics beyond what F08-03 requires;
- turn `state.json` into authored authority;
- change F08-01 blocked-Gate routing semantics.

## Core semantic split

v0.3 establishes:

```text
Historical Occurrence
        !=
Current Applicability
        !=
Current Actionability
```

Historical facts are not rewritten merely because their supporting Authority later loses current applicability.

## Integration occurrence semantics

The existing integration lifecycle remains:

```text
awaiting_integration
integrated
closed_unmerged
```

The meaning is clarified:

```text
status = repository integration occurrence / lifecycle fact
```

An `integrated` record is durable history once repository evidence proves the integration occurred.

For `integrated`, strict validation requires:

- referenced Gate exists;
- historical Gate verdict is `PASS` or `PASS_WITH_FINDINGS`;
- `integrated_revision` is non-empty;
- integration occurrence evidence exists and is available.

`integrated` does **not** require the Gate to remain current-valid forever.

Later Authority supersession must not change:

```text
integrated -> not integrated
```

For `awaiting_integration`, current actionability still matters. It continues to require a current-effective `PASS` or `PASS_WITH_FINDINGS` Gate and available evidence because it represents an action that is still proposed now.

`closed_unmerged` remains non-integrated history and is non-actionable unless a new integration candidate is explicitly authored.

## Derived Integration applicability

Current applicability is generated, not authored.

Use these derived applicability classes:

```text
current
needs_review
stale
historical
```

Rules:

- `current`: all Gate `authority_ids` are `Current`, the Gate is effective-current, and required evidence is current-usable;
- `needs_review`: at least one referenced Authority remains `Current` but the Gate/evidence needs review, **or** the Gate references a mixed set of `Current` and `Superseded/Historical` Authorities;
- `stale`: at least one referenced Authority remains `Current` and current Gate/evidence validity is stale/invalid;
- `historical`: the occurrence is already completed (`integrated` or `closed_unmerged`) and **all** validity-bearing Gate Authorities are `Superseded/Historical`.

A mixed Current + Historical Authority set must never be silently classified as historical. If the algorithm cannot determine the set safely, fail closed to `needs_review`.

For `closed_unmerged`, applicability is historical once no current integration action remains.

Generated state must expose deterministic Integration applicability. The exact JSON representation may be an ordered list or map, but it must be byte-stable and schema-defined.

## Gate history and current actionability

Keep historical Gate verdict separate from current validity:

```text
Gate verdict = what the Gate decided at the time
Gate validity = whether that decision still supports current work
```

v0.3 adds a derived distinction between:

```text
Historical Gate Record
        !=
Current Actionable Gate
```

A Gate becomes historical/non-actionable only when **all** validity-bearing `authority_ids` are `Superseded/Historical` and the Gate is retained solely as provenance for completed history.

Such a Gate:

- remains in Gate history;
- may support a historically true `integrated` occurrence only when its historical verdict was `PASS`/`PASS_WITH_FINDINGS`;
- if its historical verdict was `BLOCKED_*`, that verdict remains audit history but cannot support an `integrated` occurrence;
- does not reactivate an active `BLOCKED_*` current-project blocker merely because the verdict is retained;
- must not route the current project to P34 solely for being historical.

A Gate tied to any still-Current Authority whose evidence/validity is stale or needs review remains actionable and continues to route under existing validity semantics. Mixed Current + Historical Authority membership fails closed to current `needs_review`, not historical; that mixed-authority condition itself contributes an Authority-layer `P21` review requirement.

Generated state therefore needs a deterministic historical/actionable projection, including a representation such as `historical_gates[]` while preserving current `stale_gates[]` / `needs_review_gates[]` for actionable current problems.

## Supersession semantics

The key invariant is:

```text
Authority supersession may change applicability.
Authority supersession does not erase historical occurrence.
```

Decision table:

| Situation | Integration occurrence | Derived applicability | Gate treatment | Current route |
| --- | --- | --- | --- | --- |
| Gate PASS, not merged | awaiting_integration | current | current/actionable | implementation handoff |
| Gate PASS, merged | integrated | current | current/actionable | none |
| All supporting Authority later superseded | integrated | historical | historical/non-actionable | none solely from history |
| Mixed Current + Historical Authority | integrated | needs_review | actionable Authority uncertainty | P21 |
| Current Authority Gate needs review | integrated | needs_review | actionable needs-review Gate | P34 |
| Current Authority Gate stale | integrated | stale | actionable stale Gate | P34 |
| Gate historically BLOCKED and all Authority historical | must not support integrated occurrence | n/a | historical/non-actionable blocked record | none solely from history |

Other independent earlier blockers may still take precedence under the existing earliest-untrusted-layer ordering.

## Versioning

This change is semantically incompatible with v0.2 even where field names are reused.

Therefore:

```text
schemas/project-state/v0.3/
SCHEMA_VERSION = "0.3"
GENERATOR_VERSION = "0.3"
```

Do not overwrite `schemas/project-state/v0.1/` or `schemas/project-state/v0.2/`.

v0.2 remains Current until v0.3 completes P34, supersession, repository integration, and formal 08 rerun acceptance.

## Verification design

Implementation must first add RED regressions for at least:

1. `integrated` + later all supporting Authority superseded -> VALID; occurrence remains integrated; applicability = historical;
2. `integrated` + historical PASS Gate -> allowed;
3. `integrated` + historical BLOCKED Gate -> rejected and old blocked verdict does not become a current blocker solely from history;
4. `awaiting_integration` + stale/non-current-effective Gate -> rejected;
5. historical stale Gate -> historical projection and no P34 routing;
6. current Authority + stale Gate -> remains actionable and routes P34;
7. mixed Current + Historical Gate Authorities -> `needs_review` + Authority/P21, not historical;
8. missing/invalid integration occurrence evidence -> integrated provenance cannot be accepted;
9. real Aegis self-host oracle:

```text
PR #4 integrated + 07 v0.1 superseded
PR #7 integrated + 07 v0.2 current
OpenAI baseline = BLOCKED_ENVIRONMENT

=> int-pr4 occurrence = integrated
=> int-pr4 applicability = historical
=> int-pr7 occurrence = integrated
=> int-pr7 applicability = current
=> gate-project-state-pr4 = historical / non-actionable
=> blocking_gates = [gate-openai-real-baseline]
=> earliest_untrusted_layer = verification
=> recommended_next_stage = P34
=> strict root check = STATE_OK
```

The real self-host oracle is mandatory acceptance evidence. Unit tests alone are insufficient.

## Required lifecycle route

```text
P35 Defect Classification
→ P21 Authority Review
→ P20 Verification Design
→ written v0.3 spec approval
→ P30 / P31 implementation package
→ P32 TDD implementation
→ P36 full regression
→ P34
→ P23 v0.2 supersession if accepted
→ repository integration
→ formal 08 rerun
```

## Acceptance boundary

v0.3 may supersede v0.2 only when all are true:

- schema/validator/compute regressions pass;
- historical Integration truth survives Authority supersession;
- stale Gate tied to current Authority still blocks correctly;
- mixed Current/Historical dependencies fail closed to Authority review;
- historical `BLOCKED_*` verdicts do not reactivate current blockers solely from provenance;
- stale Gate retained only as superseded-history provenance does not block current routing;
- Aegis root self-host strict check returns `STATE_OK` under truthful PR #4 / PR #7 / OpenAI-baseline facts;
- repository CI evidence passes the defined P34 gate;
- Aegis Skill project-state reference is updated and validates/packages successfully.

Until then, v0.2 remains Current Authority and 08 remains `BLOCKED_AUTHORITY`.
