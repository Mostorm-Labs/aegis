# Aegis Project State Historical Integration Durability + Gate History Semantics v0.3

Status: **Current Replacement Authority v0.3 — P34 PASS; integrated in `main`.**

This document is the repository companion to the Notion authority `07 v0.3 Aegis Project State Historical Integration Durability + Gate History Semantics` and supersedes `docs/project-state-manifest-v0.2.md`.

P34 accepted v0.3 on PR #8 after fresh merge-ref CI. PR #8 was then squash-merged into `main` at revision `be385b3549900ba5bc34170dbfa8b4e583631a1d`.

## Authority basis

v0.2 correctly closed:

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
v0.2 rejects the still-true integrated occurrence
```

Classification:

- Primary: `SPEC_DEFECT`
- Secondary: `MISSING_CONTRACT`
- Repair owner: 07 Project State Authority

The defect was not that the validator failed to match v0.2. The validator correctly enforced an incomplete v0.2 contract.

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

`closed_unmerged` is completed non-integrated history: it is non-actionable, has Integration applicability `historical`, never enters `awaiting_integrations[]`, and never creates a finishing-development-branch handoff. This does not automatically make its supporting Gate historical; Gate actionability remains independently derived.

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

- `closed_unmerged` -> `historical`;
- `integrated` + all Gate `authority_ids` Current + effective-current Gate/evidence -> `current`;
- `integrated` + mixed Current and Superseded/Historical Authority -> `needs_review`;
- `integrated` + still-current Authority but stale/invalid Gate/evidence -> `stale`;
- `integrated` + all validity-bearing Gate Authorities Superseded/Historical -> `historical`.

A mixed Current + Historical Authority set must never be silently classified as historical. If the algorithm cannot determine the set safely, fail closed to `needs_review`.

Generated state exposes deterministic Integration applicability through `integration_applicability[]`, ordered by Integration ID.

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

A Gate becomes historical/non-actionable only when both are true:

1. all validity-bearing `authority_ids` are `Superseded/Historical`; and
2. the Gate is retained as provenance for a completed Integration (`integrated` or `closed_unmerged`).

Such a Gate:

- remains in Gate history;
- may support a historically true `integrated` occurrence only when its historical verdict was `PASS`/`PASS_WITH_FINDINGS`;
- if its historical verdict was `BLOCKED_*`, that verdict remains audit history but cannot support an `integrated` occurrence;
- does not reactivate an active `BLOCKED_*` current-project blocker merely because the verdict is retained;
- must not route the current project to P34 solely for being historical.

A Gate tied to any still-Current Authority whose evidence/validity is stale or needs review remains actionable and continues to route under existing validity semantics. Mixed Current + Historical Authority membership fails closed to current `needs_review`, not historical; that mixed-authority condition itself contributes an Authority-layer `P21` review requirement.

Generated state exposes provenance-only Gates in `historical_gates[]`, while `stale_gates[]` / `needs_review_gates[]` remain current actionable problems.

## Supersession semantics

The key invariant is:

```text
Authority supersession may change applicability.
Authority supersession does not erase historical occurrence.
```

| Situation | Integration occurrence | Derived applicability | Gate treatment | Current route |
| --- | --- | --- | --- | --- |
| Gate PASS, not merged | awaiting_integration | current | current/actionable | implementation handoff |
| Gate PASS, merged | integrated | current | current/actionable | none |
| All supporting Authority later superseded | integrated | historical | historical/non-actionable | none solely from history |
| Mixed Current + Historical Authority | integrated | needs_review | actionable Authority uncertainty | P21 |
| Current Authority Gate needs review | integrated | needs_review | actionable needs-review Gate | P34 |
| Current Authority Gate stale | integrated | stale | actionable stale Gate | P34 |
| Gate historically BLOCKED and all Authority historical | must not support integrated occurrence | n/a | historical/non-actionable blocked record | none solely from history |
| Candidate closed without merge | closed_unmerged | historical | Gate remains independently classified | none from Integration |

Other independent earlier blockers may still take precedence under the existing earliest-untrusted-layer ordering.

## Versioning

This change is semantically incompatible with v0.2 even where field names are reused.

```text
schemas/project-state/v0.3/
SCHEMA_VERSION = "0.3"
GENERATOR_VERSION = "0.3"
```

`schemas/project-state/v0.1/` and `schemas/project-state/v0.2/` remain preserved as historical contracts. v0.2 is now Superseded/Historical; v0.3 is Current.

## Accepted verification evidence

The implementation was developed RED-first and accepted only after focused history regressions, the existing project-state suite, declarative schema checks, Skill validation/package, and the real Aegis self-host oracle all passed.

PR #8 final head:

```text
9198ed45818f564456a3a807fb30db8dd2f8bf2d
```

GitHub Actions run `33025424144`, job `98365477644`, checked out the real PR merge ref `b152ed01160d1930c6dab9c6193b665b28b69a1e` and produced:

```text
six v0.3 schemas parse = PASS
minimal validate       = VALID
minimal state check    = STATE_OK
Ran 43 tests in 0.230s
OK
```

Fresh local verification also produced 43/43 PASS, Skill Creator validation/package PASS, clean ZIP integrity, and R03-09 `STATE_OK`.

R03-09 accepted state before v0.3 supersession/integration:

```text
int-pr4 = integrated / historical
int-pr6 = closed_unmerged / historical
int-pr7 = integrated / current
gate-project-state-pr4 = historical / non-actionable
blocking_gates = [gate-openai-real-baseline]
earliest_untrusted_layer = verification
recommended_next_stage = P34
strict root check = STATE_OK
```

Production special-case scan found no PR #4, PR #4 merge SHA, or `Mostorm-Labs/aegis` special case under `tools/aegis_state`.

## P34 / P23 / repository integration

P34 verdict: **PASS**.

P23 then superseded v0.2 with v0.3 in the Authority system. Repository integration was performed separately through PR #8, squash-merged at:

```text
be385b3549900ba5bc34170dbfa8b4e583631a1d
```

The next mandatory downstream evidence is the formal 08 Self-Hosting rerun on the integrated v0.3 baseline. That rerun must preserve the real OpenAI behavioral baseline as `BLOCKED_ENVIRONMENT -> verification/P34`; success means self-host semantic fidelity is correct, not that the entire Aegis project is globally unblocked.
