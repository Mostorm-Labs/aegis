# Aegis Self-Hosting v0.1 Dogfood Report

Status: **Formal v0.3 rerun semantic oracle PASS locally; repository P34 pending.**

## Purpose

Preserve the complete self-hosting learning chain. The success condition is faithful project-control state, not an artificially all-green project.

## Pass I — strict v0.1 adoption

The first Aegis self-host run found:

- **F08-01:** current `BLOCKED_*` Gate verdicts disappeared from derived project state;
- **F08-02:** P34 PASS could not be distinguished from repository integration.

Both were classified upstream and captured as `defect-008` / `defect-009`. Structural validation was green while semantic fidelity was `BLOCKED_AUTHORITY`.

## Pass II — formal v0.2 rerun

07 v0.2 correctly closed F08-01 and basic F08-02:

```text
BLOCKED_ENVIRONMENT/current
→ blocking_gates[]
→ verification / P34
```

and repository state became explicit through:

```text
awaiting_integration
integrated
closed_unmerged
```

The same real Aegis facts then exposed **F08-03**: PR #4 was genuinely integrated under v0.1, but after v0.1 was superseded the old Gate was stale; v0.2 rejected the still-true integration because `integrated` required a current/current-valid Gate forever.

Classification:

```text
F08-03
Primary   = SPEC_DEFECT
Secondary = MISSING_CONTRACT
```

This became permanent `defect-010` and routed to 07 v0.3.

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

### Reality input

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

### Deterministic result

Using current v0.3 production tooling on truthful root manifests:

```text
STATE_WRITTEN
VALID
STATE_OK
```

Generated state:

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

### Finding status

```text
F08-01 = CLOSED
F08-02 = CLOSED
F08-03 = CLOSED by real v0.3 self-host oracle
```

No repository-specific special case is required. Historical Gates no longer become current blockers solely from supersession, historical integrations remain durable, and current stale/blocked conditions remain actionable.

## Independent current blocker

The live OpenAI behavioral baseline remains:

```text
BLOCKED_ENVIRONMENT
reason = no authorized OPENAI_API_KEY
route = verification / P34
```

This does not invalidate self-hosting fidelity. In fact, preserving this blocker while closing F08-03 is the required evidence that the system is not becoming false-clean.

## Corpus

Permanent regression history remains:

```text
defect-007 corpus growth
defect-008 blocked Gate propagation
defect-009 Gate PASS vs repository integration
defect-010 historical integration durability
```

Protected seed = 30. Expected total = 34.

## Current Gate split

```text
Project State v0.3 generic tooling   = PASS locally
Root v0.3 state recomputation        = PASS
Root strict validate/check           = VALID / STATE_OK
Self-host semantic fidelity          = PASS locally
OpenAI behavioral baseline           = BLOCKED_ENVIRONMENT (independent)
Repository final-head CI             = PENDING
Overall 08 P34                       = PENDING repository evidence
```

Do not promote 08 to final PASS based only on this local result; require fresh GitHub CI on the final PR head.
