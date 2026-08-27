# Aegis Self-Hosting / Manual Dogfooding + Manifest Adoption v0.1

Status: **Current Dogfood Authority — formal v0.3 rerun semantic oracle PASS locally; repository P34 pending.**

## Objective

Make `Mostorm-Labs/aegis` the first real consumer of Aegis project-state governance and require root project state to represent actual Authority, Gate, Evidence, and repository integration facts without false readiness or historical rewriting.

Success does **not** mean the whole Aegis project is unblocked. Success means the generated state faithfully represents whatever blockers actually exist.

## Historical findings

### F08-01 — blocked Gate propagation

v0.1 could structurally validate while losing a real `BLOCKED_ENVIRONMENT` Gate. Classified `SPEC_DEFECT + MISSING_CONTRACT`; captured as `defect-008`.

07 v0.2 closed it by propagating current `BLOCKED_*` verdicts into `blocking_gates[]` and earliest-layer routing.

### F08-02 — repository integration lifecycle

v0.1 could not distinguish P34 PASS from code actually integrated into `main`. Classified `MISSING_CONTRACT`; captured as `defect-009`.

07 v0.2 closed the basic lifecycle through `integrations.json` with `awaiting_integration / integrated / closed_unmerged`.

### F08-03 — historical integration durability

The formal v0.2 rerun proved PR #4 was historically integrated while its 07 v0.1 Authority was correctly Superseded, but v0.2 required every `integrated` record to keep a current/current-valid PASS Gate forever. Classified `SPEC_DEFECT + MISSING_CONTRACT`; captured as `defect-010`.

07 v0.3 repairs this by separating:

```text
Historical Occurrence
!=
Current Applicability
!=
Current Actionability
```

## Formal v0.3 reality oracle

Current repository facts used by the rerun:

```text
07 v0.1 = Superseded / Historical
07 v0.2 = Superseded / Historical
07 v0.3 = Current

PR #3 = integrated @ d55686123bd22254c196f8232c8b115f469bde1e
PR #4 = integrated @ 555bac21d485fc4530680c61719fc36831021b0d
PR #6 = closed_unmerged history
PR #7 = integrated @ 8ca7b49d40a17e8cb7ffba86632da3aeae5e911c
PR #8 = integrated @ be385b3549900ba5bc34170dbfa8b4e583631a1d

OpenAI real behavioral baseline = BLOCKED_ENVIRONMENT
```

Root authored manifests use schema `0.3`; `state.json` is generated only.

## Formal v0.3 local rerun result

Fresh deterministic execution produced:

```text
STATE_WRITTEN
VALID
STATE_OK

historical_gates = [
  gate-project-state-pr4,
  gate-project-state-v02-pr7
]

blocking_gates = [gate-openai-real-baseline]
earliest_untrusted_layer = verification
recommended_next_stage = P34
recommended_handoff = null
awaiting_integrations = []

int-pr4 = historical
int-pr6 = historical
int-pr7 = historical
int-pr8 = current
```

This closes F08-03 in the real Aegis self-host scenario: historical integration facts survive later Authority supersession, while the current OpenAI environment blocker remains active and correctly routed.

## Current Gate interpretation

```text
F08-01 = CLOSED
F08-02 = CLOSED
F08-03 = CLOSED by v0.3 local self-host oracle
Root semantic fidelity = PASS locally
OpenAI behavioral baseline = still BLOCKED_ENVIRONMENT (expected independent project blocker)
Repository P34 = PENDING fresh PR CI
```

The presence of `BLOCKED_ENVIRONMENT` is evidence that self-hosting is working correctly, not evidence that 08 itself failed.

## Permanent regressions

`evals/cases/dogfood.json` preserves:

- `defect-007` — corpus seed is not a ceiling;
- `defect-008` — blocked Gate propagation;
- `defect-009` — P34 PASS vs repository integration;
- `defect-010` — historical integration durability after supersession.

Protected seed remains 30; expected corpus remains 34 until another real defect is discovered.

## Acceptance boundary

08 may move from `BLOCKED_AUTHORITY` to accepted self-host fidelity only after final-head repository CI proves:

```text
v0.3 schema/minimal tooling = PASS
project-state regression    = PASS
root validate/check         = VALID / STATE_OK
34-case corpus integrity    = PASS
```

No new Authority repair is currently indicated by the v0.3 self-host result.
