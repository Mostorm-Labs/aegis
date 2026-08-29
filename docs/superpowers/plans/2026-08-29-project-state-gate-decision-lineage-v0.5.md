# Project State Gate Decision Lineage v0.5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Project State v0.5 so repeated Gate reviews create immutable decision occurrences, current actionability is derived from the unique decision-lineage head, and historical Integrations remain bound to the exact Gate decision that existed when the occurrence happened.

**Architecture:** Keep `gates.json` as the single Gate manifest but split stable Gate Contracts from immutable `decisions[]`. Teach Project State validation and state derivation to branch by schema version: v0.3/v0.4 behavior is untouched, while v0.5 resolves one linear decision lineage per Gate and uses its head for current routing. Add a pure deterministic v0.4→v0.5 migration function; do not migrate the repository root until v0.5 itself passes P34/P23.

**Tech Stack:** Python 3.12 standard library, JSON Schema draft 2020-12 documents, `unittest`, GitHub Actions.

**Spec:** `docs/project-state-gate-decision-lineage-v0.5.md`

## Execution Status

Executed inline in the ChatGPT control thread on branch `aegis/project-state-gate-decision-lineage-v0.5`.

- P20 verification design: COMPLETE
- P30 implementation plan: COMPLETE
- P31 task packaging: COMPLETE
- P32 RED-first implementation: COMPLETE
- P34 independent review: PENDING

RED runs:
- `33234280222` — v0.5 lineage/migration oracle failed before v0.5 tooling existed.
- `33234756600` — immutable transition oracle failed before transition validation existed.

Fresh exact-head GREEN evidence is maintained in PR #14 rather than hard-coded here, so evidence-only commits do not make this plan self-stale. Root `.aegis/*` remains v0.4 until P34/P23.

## Global Constraints

- `aegis-project-state-v0.4` remains Current until v0.5 passes its own P34 and P23 supersession.
- v0.3 and v0.4 semantics must remain byte-for-byte behaviorally compatible for existing manifests.
- v0.5 Gate Decision IDs are deterministic: `<gate-id>::decision::0001`, `0002`, ... with four-digit zero padding and contiguous sequence numbers.
- A Gate Decision is append-only governance history: later reviews create a new decision and must not mutate an older verdict/evidence set.
- `blocking_gates[]` remains as a compatibility projection of Gate IDs; v0.5 adds `current_gate_decisions[]` and `blocking_gate_decisions[]`.
- v0.5 Integrations use `gate_decision_id`, not authored `gate_id`.
- An integrated occurrence derives conformance from its bound immutable decision, never from the current decision head.
- A superseded BLOCKED decision must never remain an active blocker.
- Root `.aegis/*` remains v0.4 during this implementation PR; root migration is a post-P34/P23 lifecycle action.
- RED-first: acceptance tests are committed and observed failing before production semantics are added.

---

### Task 1: RED-first Gate Decision Lineage Oracle — COMPLETE

**Files:**
- `tests/project_state/test_gate_decision_lineage_v05.py`
- `tests/project_state/test_migration_v05.py`
- `tests/project_state/test_gate_decision_transition_v05.py`

Implemented executable coverage for re-review PASS, historical integration preservation, lineage integrity, migration equivalence, root PR #9 reconciliation, and cross-snapshot append-only immutability.

RED evidence:

```text
33234280222  v0.5 schema/migration absent
33234756600  transition_v05 absent
```

---

### Task 2: v0.5 Schemas and Structural Validation — COMPLETE

**Files:**
- `schemas/project-state/v0.5/*.schema.json`
- `tools/aegis_state/model.py`
- `tools/aegis_state/__init__.py`

Implemented:

```text
SUPPORTED_SCHEMA_VERSIONS = 0.3 / 0.4 / 0.5
Gate Contract + decisions[] split
<gate-id>::decision::<NNNN> identity
linear contiguous lineage validation
cross-Gate / dangling / fork / cycle rejection
v0.5 Integration gate_decision_id validation
current PASS decision safety for awaiting integration
```

---

### Task 3: v0.5 State Derivation and Routing — COMPLETE

**Files:**
- `tools/aegis_state/compute.py`

Implemented:

```text
current_gate_decisions[]
blocking_gate_decisions[]
blocking_gates[] compatibility projection
current decision evidence drives current Gate validity
historical Integration conformance derives from bound Gate Decision
superseded BLOCKED decisions do not remain active blockers
v0.3 / v0.4 output semantics preserved
```

---

### Task 4: Deterministic v0.4 → v0.5 Migration — COMPLETE

**Files:**
- `tools/aegis_state/migrate_v05.py`
- `tools/aegis_state/cli.py`

Interfaces:

```text
legacy_decision_id(gate_id)
migrate_v04_to_v05(manifests)
python3 -m tools.aegis_state.cli migrate-v05 SOURCE_ROOT DEST_ROOT
```

Migration deep-copies source manifests, creates deterministic `::decision::0001` decisions, rewrites Integration references to `gate_decision_id`, refuses an existing destination `.aegis`, and introduces no timestamps.

---

### Task 5: v0.5 Example and CI — COMPLETE

**Files:**
- `examples/project-state/v0.5-minimal/.aegis/*`
- `.github/workflows/project-state.yml`
- `tests/project_state/test_state.py`

The workflow now checks:

```text
v0.3/v0.4/v0.5 schema JSON
v0.4 minimal validate/check
v0.5 minimal validate/check
Project State regressions
root v0.4 self-host validate/check
Aegis Skillset validation/regressions
Aegis evaluation corpus/regressions
```

---

### Task 6: P32 Completion Evidence and P34 Handoff — COMPLETE / P34 NEXT

Required exact-head evidence is maintained on PR #14 and in its durable review comments.

The P32 slice intentionally does **not**:

```text
promote v0.5 to Current
supersede v0.4
migrate root .aegis manifests
rewrite PR #9 historical Gate verdict
append PR #9 PASS decision to root
```

P34 must independently audit all twelve acceptance requirements. Only after P34 PASS may P23 and root migration begin.

If P34 PASS, the separate lifecycle sequence is:

```text
P23 Project State v0.4 -> v0.5
→ root deterministic migration
→ append PR #9 decision::0002 PASS using accepted Task 6 evidence
→ recompute root state and verify int-pr9 remains nonconforming
→ Skill Decomposition v0.2 P23 supersession
```
