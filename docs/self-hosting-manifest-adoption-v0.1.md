# Aegis Self-Hosting / Manual Dogfooding + Manifest Adoption v0.1

Status: **Current Dogfood Authority — formal v0.3 rerun accepted; P34 `PASS_WITH_FINDINGS`; integrated in `main`.**

PR #5 was squash-merged at `335578a9646c414bba7ecc672d53b9f366bc0d0e` after fresh final-head merge-ref CI proved root self-host semantic fidelity.

## Objective

Make `Mostorm-Labs/aegis` the first real consumer of Aegis project-state governance and require root project state to represent actual Authority, Gate, Evidence, and repository integration facts without false readiness or historical rewriting.

Success does **not** mean the whole Aegis project is unblocked. Success means generated state faithfully represents whatever blockers actually exist.

## Historical findings

### F08-01 — blocked Gate propagation

v0.1 could structurally validate while losing a real `BLOCKED_ENVIRONMENT` Gate. Classified `SPEC_DEFECT + MISSING_CONTRACT`; captured as `defect-008`. 07 v0.2 closed it through active blocked-Gate propagation.

### F08-02 — repository integration lifecycle

v0.1 could not distinguish P34 PASS from code integrated into `main`. Classified `MISSING_CONTRACT`; captured as `defect-009`. 07 v0.2 closed the basic lifecycle through `awaiting_integration / integrated / closed_unmerged`.

### F08-03 — historical integration durability

The formal v0.2 rerun proved PR #4 was historically integrated while its v0.1 Authority was correctly Superseded, but v0.2 required `integrated` to keep a current/current-valid Gate forever. Classified `SPEC_DEFECT + MISSING_CONTRACT`; captured as `defect-010`.

07 v0.3 repairs this through:

```text
Historical Occurrence
!=
Current Applicability
!=
Current Actionability
```

## Formal v0.3 reality oracle

Truthful repository facts:

```text
07 v0.1 = Superseded / Historical
07 v0.2 = Superseded / Historical
07 v0.3 = Current / integrated

PR #3 = integrated @ d55686123bd22254c196f8232c8b115f469bde1e
PR #4 = integrated @ 555bac21d485fc4530680c61719fc36831021b0d
PR #6 = closed_unmerged history
PR #7 = integrated @ 8ca7b49d40a17e8cb7ffba86632da3aeae5e911c
PR #8 = integrated @ be385b3549900ba5bc34170dbfa8b4e583631a1d

OpenAI real behavioral baseline = BLOCKED_ENVIRONMENT
```

Root authored manifests use schema `0.3`; `state.json` is generated only.

## Accepted generated state

```text
historical_gates = [
  gate-project-state-pr4,
  gate-project-state-v02-pr7
]

blocking_gates = [gate-openai-real-baseline]
earliest_untrusted_layer = verification
recommended_next_stage = P34
recommended_handoff = null
awaiting_integrations = []

int-pr1 = current
int-pr2 = current
int-pr3 = current
int-pr4 = historical
int-pr6 = historical
int-pr7 = historical
int-pr8 = current
```

This projection is now present on `main` in `.aegis/state.json`.

## Fresh repository evidence

PR #5 final head:

```text
3d0549bdfe5f2f057dda171d0c6a36a837840d44
```

Actual PR merge-ref:

```text
114d5acc228403224e3162b58ef05c4e34fd38e7
```

Project State run `33026385793`:

- `validate-tooling` job `98368600472`: six v0.3 schemas PASS, minimal `VALID / STATE_OK`, 43/43 project-state tests PASS.
- `self-host` job `98368600417`: root manifests `VALID`, root generated state `STATE_OK`, corpus validator PASS with 34 cases.

Eval Integrity run `33026385830`, job `98368600085`:

```text
PASS: 34 cases validated
Ran 34 tests
OK
```

## Final finding status

```text
F08-01 = CLOSED
F08-02 = CLOSED
F08-03 = CLOSED
Self-host semantic fidelity = PASS
Overall 08 = PASS_WITH_FINDINGS
```

The sole finding is the independent 06-02 provider baseline environment blocker:

```text
OpenAI behavioral baseline = BLOCKED_ENVIRONMENT
reason = no authorized OPENAI_API_KEY
route = verification / P34
```

This blocker does not invalidate 08. Its continued presence is positive evidence that v0.3 does not become false-clean while closing historical project-state defects.

## Permanent regressions

The extensible corpus preserves:

- `defect-007` — protected seed is not a corpus ceiling;
- `defect-008` — blocked Gate propagation;
- `defect-009` — P34 PASS versus repository integration;
- `defect-010` — historical integration durability after supersession.

Protected seed = 30; current corpus = 34.

## Repository integration

PR #5 was squash-merged into `main` at:

```text
335578a9646c414bba7ecc672d53b9f366bc0d0e
```

The root `.aegis/` project-control state is therefore no longer a dogfood-only branch artifact; it is now part of the Aegis repository baseline.

## Handoff

08 no longer blocks downstream work on project-state Authority. The 06-02 OpenAI behavioral baseline remains separately `BLOCKED_ENVIRONMENT` and may stay parked until an authorized API credential exists.

The next planned lifecycle stage may now enter **09 Aegis Skill Decomposition & Multi-Skill Architecture**, subject to its own design Gate.
