# Aegis Project State Historical Integration Durability + Gate History Semantics v0.3

Status: **Superseded by [Project State v0.4](project-state-manifest-v0.4.md). Historical P34 PASS; integrated in `main`.**

Supersession reason: F09-06 proved that v0.3 cannot truthfully represent a repository Integration that physically occurred while its Gate remained `BLOCKED_*`. v0.4 preserves v0.3 history/applicability semantics while separating Integration occurrence from Gate conformance. v0.3 remains an immutable supported historical schema; v0.4 does not reinterpret v0.3 manifests.

This document is the repository companion to the Notion authority `07 v0.3 Aegis Project State Historical Integration Durability + Gate History Semantics` and supersedes `docs/project-state-manifest-v0.2.md`.

P34 accepted v0.3 on PR #8 after fresh merge-ref CI. PR #8 was then squash-merged into `main` at revision `be385b3549900ba5bc34170dbfa8b4e583631a1d`.

## Authority basis

v0.2 correctly closed F08-01 (active `BLOCKED_*` Gate propagation) and F08-02 (separate repository Integration lifecycle), but the formal Aegis self-host rerun exposed F08-03:

```text
PR #4 historically integrated
+
its supporting 07 v0.1 Authority later superseded
↓
v0.2 makes the old Gate stale
↓
v0.2 rejects the still-true integrated occurrence
```

Classification: `SPEC_DEFECT + MISSING_CONTRACT`; repair owner: 07 Project State Authority.

## Scope

v0.3 defines only:

1. durable historical Integration occurrence;
2. derived current Integration applicability;
3. historical Gate record versus current actionable Gate;
4. supersession semantics connecting those dimensions.

It does not add Gate verdicts, automate Git, introduce event sourcing, redesign the Authority DAG, or make `state.json` authored authority.

## Core semantic split

```text
Historical Occurrence
!=
Current Applicability
!=
Current Actionability
```

Authority supersession may change applicability and actionability. It cannot erase what actually happened.

## Integration occurrence semantics

Statuses remain:

```text
awaiting_integration
integrated
closed_unmerged
```

`integrated` is durable occurrence history once repository evidence proves the integration happened. Strict validation requires a referenced historical `PASS`/`PASS_WITH_FINDINGS` Gate, non-empty `integrated_revision`, and available occurrence evidence. It does not require that Gate to remain current-valid forever.

`awaiting_integration` is a current proposed action and therefore still requires a current-effective PASS Gate and available evidence.

`closed_unmerged` is completed non-integrated history: its Integration applicability is `historical`, it never enters `awaiting_integrations[]`, and it never creates a finishing-development-branch handoff. This does not automatically make its supporting Gate historical.

## Derived Integration applicability

Generated values:

```text
current
needs_review
stale
historical
```

Rules:

- `closed_unmerged` -> `historical`;
- `integrated` + all Gate Authorities Current + effective-current Gate/evidence -> `current`;
- `integrated` + mixed Current and Superseded/Historical Authority -> `needs_review`;
- `integrated` + still-current Authority but stale/invalid Gate/evidence -> `stale`;
- `integrated` + all validity-bearing Gate Authorities Superseded/Historical -> `historical`.

A mixed Current + Historical set never silently becomes historical; unresolved membership fails closed to Authority review.

## Gate history and current actionability

```text
Gate verdict = what the Gate decided at the time
Gate validity = whether that decision still supports current work
Historical Gate Record != Current Actionable Gate
```

A Gate becomes historical/non-actionable only when all validity-bearing Authority is Superseded/Historical **and** the Gate is retained as provenance for a completed Integration. Such a Gate appears in `historical_gates[]` and does not create a current P34 blocker solely because its historical record remains.

Historical `BLOCKED_*` verdicts remain audit history, cannot prove an integrated occurrence, and do not reactivate current blockers solely from provenance.

A Gate tied to still-current Authority whose evidence/validity is stale remains current-actionable and routes to `verification / P34`. Mixed Current + Historical Authority contributes Authority/P21 review.

## Supersession decision table

| Situation | Integration occurrence | Applicability | Gate treatment | Current route |
| --- | --- | --- | --- | --- |
| PASS, not merged | awaiting | current | current/actionable | integration handoff |
| PASS, merged | integrated | current | current/actionable | none |
| All supporting Authority later superseded | integrated | historical | historical/non-actionable | none solely from history |
| Mixed Current + Historical Authority | integrated | needs_review | Authority uncertainty | P21 |
| Current Gate needs review | integrated | needs_review | actionable | P34 |
| Current Gate stale | integrated | stale | actionable | P34 |
| Historical BLOCKED Gate | cannot support integrated occurrence | n/a | historical/non-actionable | none solely from history |
| Candidate closed without merge | closed_unmerged | historical | Gate independently classified | none from Integration |

## Versioning

```text
schemas/project-state/v0.3/
SCHEMA_VERSION = "0.3"
GENERATOR_VERSION = "0.3"
```

v0.1, v0.2, and v0.3 schema trees are immutable historical contracts. v0.3 is Superseded as Current Authority but remains supported for projects whose authored manifests declare schema `0.3`.

## Accepted verification evidence

Development was RED-first. PR #8 final head was `9198ed45818f564456a3a807fb30db8dd2f8bf2d`.

GitHub Actions run `33025424144`, job `98365477644`, checked out the actual merge ref `b152ed01160d1930c6dab9c6193b665b28b69a1e` and produced:

```text
six v0.3 schemas parse = PASS
minimal validate       = VALID
minimal state check    = STATE_OK
Ran 43 tests in 0.230s
OK
```

Fresh local verification also produced 43/43 PASS, Skill Creator validation/package PASS, clean ZIP integrity, and R03-09 `STATE_OK`.

R03-09 accepted pre-supersession projection:

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

No PR #4, its merge SHA, or Aegis repository-specific special case exists in `tools/aegis_state` production logic.

## P34 / P23 / repository integration

Historical P34 verdict: **PASS**.

P23 originally superseded v0.2 with v0.3. Repository integration was a separate action: PR #8 was squash-merged at:

```text
be385b3549900ba5bc34170dbfa8b4e583631a1d
```

F09-06 later triggered a second P23 transition from v0.3 to v0.4. The original v0.3 evidence remains historical and is not rewritten.

The real OpenAI behavioral baseline remains separately `BLOCKED_ENVIRONMENT -> verification/P34`; Project State supersession does not alter that independent Gate.