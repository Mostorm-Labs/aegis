# Aegis Self-Hosting v0.1 Dogfood Report

Status: **Formal v0.3 rerun accepted — P34 `PASS_WITH_FINDINGS`; integrated in `main`.**

## Purpose

Preserve the complete self-hosting learning chain. The success condition is faithful project-control state, not an artificially all-green project.

## Pass I — strict v0.1 adoption

The first self-host run found:

- **F08-01:** current `BLOCKED_*` Gate verdicts disappeared from derived state;
- **F08-02:** P34 PASS could not be distinguished from repository integration.

Both were classified upstream and captured as `defect-008` / `defect-009`. Structural validation was green while semantic fidelity remained `BLOCKED_AUTHORITY`.

## Pass II — formal v0.2 rerun

07 v0.2 closed F08-01 and basic F08-02, but the same truthful project facts exposed **F08-03**: PR #4 had genuinely integrated under v0.1, yet v0.2 rejected that historical Integration after v0.1 was superseded because `integrated` required a current/current-valid Gate forever.

Classification:

```text
F08-03
Primary   = SPEC_DEFECT
Secondary = MISSING_CONTRACT
```

The finding became permanent `defect-010` and routed to 07 v0.3.

## Pass III — formal v0.3 rerun

07 v0.3 is Current and integrated through PR #8 at:

```text
be385b3549900ba5bc34170dbfa8b4e583631a1d
```

v0.3 establishes:

```text
Historical Occurrence
!=
Current Applicability
!=
Current Actionability
```

### Truthful input

```text
07 v0.1 = Superseded
07 v0.2 = Superseded
07 v0.3 = Current
PR #4 = integrated historical fact
PR #6 = closed_unmerged history
PR #7 = integrated v0.2 history
PR #8 = integrated current v0.3
OpenAI real baseline = BLOCKED_ENVIRONMENT/current
```

### Accepted result

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

The exact projection is now committed on `main` as `.aegis/state.json`.

### Fresh PR evidence

PR #5 final head:

```text
3d0549bdfe5f2f057dda171d0c6a36a837840d44
```

Actual merge-ref:

```text
114d5acc228403224e3162b58ef05c4e34fd38e7
```

Project State run `33026385793`:

```text
validate-tooling / job 98368600472
  schemas                 PASS
  minimal validate        VALID
  minimal state           STATE_OK
  project-state tests     43/43 PASS

self-host / job 98368600417
  root validate           VALID
  root state              STATE_OK
  corpus                   34 cases PASS
```

Eval Integrity run `33026385830`, job `98368600085`:

```text
PASS: 34 cases validated
Ran 34 tests
OK
```

### Finding closure

```text
F08-01 = CLOSED
F08-02 = CLOSED
F08-03 = CLOSED
```

No repository-specific special case is required. Historical Gate records no longer become current blockers solely because their Authority was superseded; historical integration facts remain durable; current Gate/evidence problems remain actionable.

## Independent current blocker

The live OpenAI behavioral baseline remains:

```text
BLOCKED_ENVIRONMENT
reason = no authorized OPENAI_API_KEY
route = verification / P34
```

This is not a self-hosting failure. Keeping it visible while closing F08-03 proves the root state is not false-clean.

## Corpus

Permanent regression history:

```text
defect-007 corpus growth
defect-008 blocked Gate propagation
defect-009 Gate PASS vs repository integration
defect-010 historical integration durability
```

Protected seed = 30; current corpus = 34.

## Final Gate split

```text
Project State v0.3 generic tooling = PASS
Root v0.3 state recomputation      = PASS
Root strict validate/check         = VALID / STATE_OK
Self-host semantic fidelity        = PASS
OpenAI behavioral baseline         = BLOCKED_ENVIRONMENT (independent)
Overall 08 P34                     = PASS_WITH_FINDINGS
```

## Repository integration

PR #5 was squash-merged into `main` at:

```text
335578a9646c414bba7ecc672d53b9f366bc0d0e
```

08 therefore exits its Authority block. Project State is now self-hosted in the Aegis repository baseline. The next planned stage may enter 09 after its own design approval.
