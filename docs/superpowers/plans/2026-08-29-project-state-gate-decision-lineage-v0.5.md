# Project State Gate Decision Lineage v0.5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Project State v0.5 so repeated Gate reviews create immutable decision occurrences, current actionability is derived from the unique decision-lineage head, and historical Integrations remain bound to the exact Gate decision that existed when the occurrence happened.

**Architecture:** Keep `gates.json` as the single Gate manifest but split stable Gate Contracts from immutable `decisions[]`. Teach Project State validation and state derivation to branch by schema version: v0.3/v0.4 behavior is untouched, while v0.5 resolves one linear decision lineage per Gate and uses its head for current routing. Add a pure deterministic v0.4→v0.5 migration function; do not migrate the repository root until v0.5 itself passes P34/P23.

**Tech Stack:** Python 3.12 standard library, JSON Schema draft 2020-12 documents, `unittest`, GitHub Actions.

**Spec:** `docs/project-state-gate-decision-lineage-v0.5.md`

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

### Task 1: RED-first Gate Decision Lineage Oracle

**Files:**
- Create: `tests/project_state/test_gate_decision_lineage_v05.py`
- Create: `tests/project_state/test_migration_v05.py`

**Interfaces:**
- Consumes: current `load_manifests()`, `validate_manifests()`, `compute_state()`.
- Produces: executable P20 oracle for the twelve v0.5 acceptance requirements; tests intentionally fail against v0.4-only tooling.

- [ ] **Step 1: Add a v0.5 scenario writer and core re-review test**

Create helpers in `test_gate_decision_lineage_v05.py` that write all five manifests with schema version `0.5`, one Gate Contract `G1`, decision `G1::decision::0001 = BLOCKED_EVIDENCE`, optional `G1::decision::0002 = PASS supersedes 0001`, and an integrated `int1` bound to `0001`.

The first test must assert after `0002` is appended:

```python
state = compute_state(load_manifests(root))
self.assertIn(
    {"gate_id": "G1", "decision_id": "G1::decision::0002", "verdict": "PASS"},
    state["current_gate_decisions"],
)
self.assertNotIn("G1", state["blocking_gates"])
self.assertIn(
    {
        "integration_id": "int1",
        "gate_decision_id": "G1::decision::0001",
        "conformance": "nonconforming",
    },
    state["integration_conformance"],
)
```

- [ ] **Step 2: Add lineage integrity negative tests**

Cover each required failure independently:

```text
duplicate decision ID
bad decision ID sequence
missing ::decision::0001 root
sequence gap 0001 -> 0003
cross-Gate supersedes
dangling supersedes
decision cycle
two children superseding one predecessor / fork
two unsuperseded heads
disconnected lineage
Integration -> missing gate_decision_id
awaiting_integration -> superseded decision
awaiting_integration -> current BLOCKED decision
```

Every assertion must match a stable diagnostic substring such as `decision lineage`, `cross-gate`, `sequence`, `dangling gate decision`, or `requires current PASS/PASS_WITH_FINDINGS gate decision`.

- [ ] **Step 3: Add migration-equivalence RED tests**

`test_migration_v05.py` must import the not-yet-existing interface:

```python
from tools.aegis_state.migrate_v05 import legacy_decision_id, migrate_v04_to_v05
```

Required assertions:

```python
self.assertEqual(legacy_decision_id("G1"), "G1::decision::0001")
migrated = migrate_v04_to_v05(v04_manifests)
self.assertEqual("0.5", migrated.schema_version)
self.assertEqual(v04_state["blocking_gates"], v05_state["blocking_gates"])
self.assertEqual(v04_state["integration_applicability"], v05_state["integration_applicability"])
```

For each v0.4 integrated occurrence, compare conformance after dropping only the new `gate_decision_id` key from the v0.5 projection.

- [ ] **Step 4: Add a root PR #9 reconciliation fixture test**

Build a temporary fixture from the root v0.4 manifest JSON, migrate it with `migrate_v04_to_v05()`, append a new `gate-skill-decomposition-v02-pr9::decision::0002` PASS decision using a synthetic available `ev-pr9-task6-accepted` evidence record, and assert:

```python
self.assertNotIn("gate-skill-decomposition-v02-pr9", state["blocking_gates"])
self.assertIn("int-pr9", state["nonconforming_integrations"])
self.assertEqual(
    "gate-skill-decomposition-v02-pr9::decision::0001",
    next(x for x in state["integration_conformance"] if x["integration_id"] == "int-pr9")["gate_decision_id"],
)
```

This is a fixture proof only; it must not rewrite root `.aegis/*`.

- [ ] **Step 5: Run RED**

Run:

```bash
python3 -m unittest tests.project_state.test_gate_decision_lineage_v05 tests.project_state.test_migration_v05 -v
```

Expected: FAIL because schema version `0.5`, `decision_items`, state projections, and `tools.aegis_state.migrate_v05` do not exist yet.

- [ ] **Step 6: Commit RED evidence**

```bash
git add tests/project_state/test_gate_decision_lineage_v05.py tests/project_state/test_migration_v05.py
git commit -m "test: define Project State v0.5 gate lineage oracle"
```

---

### Task 2: v0.5 Schemas and Structural Validation

**Files:**
- Create: `schemas/project-state/v0.5/project.schema.json`
- Create: `schemas/project-state/v0.5/authorities.schema.json`
- Create: `schemas/project-state/v0.5/evidence.schema.json`
- Create: `schemas/project-state/v0.5/gates.schema.json`
- Create: `schemas/project-state/v0.5/integrations.schema.json`
- Create: `schemas/project-state/v0.5/state.schema.json`
- Modify: `tools/aegis_state/model.py`
- Modify: `tools/aegis_state/__init__.py`

**Interfaces:**
- Consumes: v0.5 Authority data model from the spec.
- Produces: `ManifestSet.decision_items`, structural/strict validation for v0.5, `SUPPORTED_SCHEMA_VERSIONS={"0.3","0.4","0.5"}`.

- [ ] **Step 1: Add schemas**

Copy unchanged project/authority/evidence shapes from v0.4 but change schema IDs/constants to `0.5`.

`gates.schema.json` must require:

```json
{
  "schema_version": "0.5",
  "gates": [{"id":"...","stage":"P34","authority_ids":["..."]}],
  "decisions": [{
    "id":"...::decision::0001",
    "gate_id":"...",
    "verdict":"PASS|PASS_WITH_FINDINGS|BLOCKED_*",
    "evidence_ids":["..."],
    "supersedes":"optional previous decision id"
  }]
}
```

Gate Contracts must not accept `verdict`, `validity`, or `evidence_ids`; decisions must not accept `authority_ids` or `stage`.

`integrations.schema.json` replaces required `gate_id` with required `gate_decision_id`.

`state.schema.json` retains v0.4 fields and additionally requires `current_gate_decisions` and `blocking_gate_decisions`; v0.5 `integration_conformance` items also require `gate_decision_id`.

- [ ] **Step 2: Add version and decision accessors**

In `tools/aegis_state/model.py`:

```python
SCHEMA_VERSION = "0.5"
SUPPORTED_SCHEMA_VERSIONS = {"0.3", "0.4", "0.5"}

@property
def decision_items(self) -> list[dict]:
    if self.schema_version != "0.5":
        return []
    return list(self.gates.get("decisions", []))
```

Update `tools/aegis_state/__init__.py` to `GENERATOR_VERSION = "0.5"`; `compute_state()` must still emit legacy generator versions for v0.3/v0.4 explicitly.

- [ ] **Step 3: Add v0.5 Gate/Decision validation branch**

Preserve the existing v0.3/v0.4 Gate validation untouched under `schema_version != "0.5"`.

For v0.5 validate:

```text
Gate: id, stage, authority_ids; no decision fields required by Python model
Decision: id, gate_id, verdict, evidence_ids, optional supersedes
Decision ID exactly matches <gate-id>::decision::<4 digits>
At least one decision per Gate
All decision evidence refs exist
PASS/PASS_WITH_FINDINGS decision has at least one evidence ID
Every supersedes target exists, belongs to same Gate, and is exactly the preceding sequence number
Exactly one child per decision
Exactly one head per Gate
All sequence numbers are contiguous from 0001
```

Use one helper that returns `current_decision_by_gate` only after lineage validation succeeds; validation errors must not guess a head.

- [ ] **Step 4: Add v0.5 Integration validation**

For schema 0.5, require `gate_decision_id`; resolve the Gate through the decision. `awaiting_integration` must point to the unique current decision, that decision must be PASS/PASS_WITH_FINDINGS, its Gate Contract must be current-effective, and occurrence evidence must be available. `integrated` may point to historical BLOCKED decisions but still requires available occurrence evidence and `integrated_revision`.

- [ ] **Step 5: Run structural tests**

```bash
python3 -m unittest tests.project_state.test_gate_decision_lineage_v05 -v
python3 -m unittest tests.project_state.test_out_of_gate_v04 tests.project_state.test_v02_model tests.project_state.test_validation -v
```

Expected: lineage structural negative cases PASS; state-derivation assertions may remain failing until Task 3. All v0.3/v0.4 tests remain PASS.

- [ ] **Step 6: Commit schemas/model**

```bash
git add schemas/project-state/v0.5 tools/aegis_state/model.py tools/aegis_state/__init__.py
git commit -m "feat: add Project State v0.5 gate decision model"
```

---

### Task 3: v0.5 State Derivation and Routing

**Files:**
- Modify: `tools/aegis_state/compute.py`
- Test: `tests/project_state/test_gate_decision_lineage_v05.py`

**Interfaces:**
- Consumes: validated `ManifestSet.gate_items`, `ManifestSet.decision_items`, v0.5 Integrations.
- Produces: `current_gate_decisions[]`, `blocking_gate_decisions[]`, v0.5 historical conformance tied to `gate_decision_id` while preserving existing compatibility projections.

- [ ] **Step 1: Isolate Gate view resolution by schema version**

Add helpers so legacy flow continues to consume Gate records with embedded `verdict/validity/evidence_ids`, while v0.5 creates an internal current Gate view from Gate Contract + current decision head.

The v0.5 view must carry:

```python
{
    "gate_id": gate_id,
    "decision_id": decision_id,
    "verdict": decision["verdict"],
    "authority_ids": gate["authority_ids"],
    "evidence_ids": decision["evidence_ids"],
}
```

- [ ] **Step 2: Derive v0.5 Gate effective validity**

Authority validity is still derived from Gate Contract `authority_ids`. Evidence validity comes only from the **current decision's** evidence IDs. A superseded decision's unavailable evidence must not make the Gate stale or blocked.

- [ ] **Step 3: Derive current blockers**

For v0.5:

```python
blocking_gates.append(gate_id)
blocking_gate_decisions.append(decision_id)
```

only when the current decision is current-effective and has a BLOCKED verdict. A current PASS/PASS_WITH_FINDINGS decision clears the old blocker.

- [ ] **Step 4: Derive Integration applicability and conformance**

Resolve `integration["gate_decision_id"] -> decision -> gate`.

For `integrated` v0.5 records append:

```python
{
    "integration_id": iid,
    "gate_decision_id": decision_id,
    "conformance": "conforming" if decision["verdict"] in PASS_VERDICTS else "nonconforming",
}
```

Do not consult the Gate's current decision to derive historical conformance.

- [ ] **Step 5: Emit v0.5 state contract**

For v0.5 set `generator_version="0.5"` and include sorted `current_gate_decisions` and `blocking_gate_decisions`. For v0.4 continue emitting exactly the existing v0.4 shape; for v0.3 continue emitting the existing v0.3 shape.

- [ ] **Step 6: Run GREEN lineage tests plus legacy regression subset**

```bash
python3 -m unittest tests.project_state.test_gate_decision_lineage_v05 -v
python3 -m unittest tests.project_state.test_out_of_gate_v04 tests.project_state.test_history_v03 tests.project_state.test_gate_blockers_v02 -v
```

Expected: PASS.

- [ ] **Step 7: Commit state derivation**

```bash
git add tools/aegis_state/compute.py tests/project_state/test_gate_decision_lineage_v05.py
git commit -m "feat: derive current Gate decisions in Project State v0.5"
```

---

### Task 4: Deterministic v0.4 → v0.5 Migration

**Files:**
- Create: `tools/aegis_state/migrate_v05.py`
- Modify: `tools/aegis_state/cli.py`
- Test: `tests/project_state/test_migration_v05.py`

**Interfaces:**
- Produces:
  - `legacy_decision_id(gate_id: str) -> str`
  - `migrate_v04_to_v05(manifests: ManifestSet) -> ManifestSet`
  - CLI: `python3 -m tools.aegis_state.cli migrate-v05 SOURCE_ROOT DEST_ROOT`

- [ ] **Step 1: Implement pure deterministic migration**

Use `copy.deepcopy`. Reject any input whose `schema_version != "0.4"`.

For each v0.4 Gate:

```python
contract = {
    "id": gate["id"],
    "stage": gate["stage"],
    "authority_ids": list(gate["authority_ids"]),
}
decision = {
    "id": legacy_decision_id(gate["id"]),
    "gate_id": gate["id"],
    "verdict": gate["verdict"],
    "evidence_ids": list(gate["evidence_ids"]),
}
```

For each Integration, replace `gate_id` with `gate_decision_id=legacy_decision_id(old_gate_id)` and preserve every other field.

Change all five manifest schema versions to `0.5`; do not introduce timestamps.

- [ ] **Step 2: Implement safe CLI materialization**

`migrate-v05 SOURCE_ROOT DEST_ROOT` must refuse to write if `DEST_ROOT/.aegis` already exists. It writes the five migrated manifests and a freshly computed `state.json`; it never mutates SOURCE_ROOT.

Success output:

```text
MIGRATED_V05: <destination>/.aegis
```

- [ ] **Step 3: Prove migration equivalence**

Run:

```bash
python3 -m unittest tests.project_state.test_migration_v05 -v
```

Expected: PASS for deterministic ID generation, v0.4 state equivalence, PR #9 historical nonconformance preservation, and repeatability.

- [ ] **Step 4: Commit migration tooling**

```bash
git add tools/aegis_state/migrate_v05.py tools/aegis_state/cli.py tests/project_state/test_migration_v05.py
git commit -m "feat: add deterministic Project State v0.5 migration"
```

---

### Task 5: v0.5 Example, JSON-Schema CI, and Candidate-Gate Evidence

**Files:**
- Create: `examples/project-state/v0.5-minimal/.aegis/project.json`
- Create: `examples/project-state/v0.5-minimal/.aegis/authorities.json`
- Create: `examples/project-state/v0.5-minimal/.aegis/gates.json`
- Create: `examples/project-state/v0.5-minimal/.aegis/evidence.json`
- Create: `examples/project-state/v0.5-minimal/.aegis/integrations.json`
- Create: `examples/project-state/v0.5-minimal/.aegis/state.json`
- Modify: `.github/workflows/project-state.yml`
- Test: `tests/project_state/test_state.py`

**Interfaces:**
- Consumes: final v0.5 tooling.
- Produces: reproducible checked-in v0.5 example and hosted CI evidence while root `.aegis` stays v0.4.

- [ ] **Step 1: Generate the v0.5 minimal example by migration**

Run migration from `examples/project-state/minimal` to `examples/project-state/v0.5-minimal`, then verify:

```bash
python3 -m tools.aegis_state.cli validate examples/project-state/v0.5-minimal
python3 -m tools.aegis_state.cli check examples/project-state/v0.5-minimal
```

The migrated example must preserve the existing awaiting-integration route while binding it to `G1::decision::0001`.

- [ ] **Step 2: Extend workflow schema parsing**

Rename the step to `Parse project-state v0.3, v0.4, and v0.5 schemas` and iterate `v0.3 v0.4 v0.5`.

Add:

```yaml
- name: Validate minimal v0.5 project manifests
  run: python3 -m tools.aegis_state.cli validate examples/project-state/v0.5-minimal
- name: Check generated minimal v0.5 project state
  run: python3 -m tools.aegis_state.cli check examples/project-state/v0.5-minimal
```

Keep the existing v0.4 minimal and root v0.4 checks unchanged.

- [ ] **Step 3: Add CLI v0.5 roundtrip test**

In `test_state.py`, create a v0.5 fixture or migrate a v0.4 fixture, run `recompute --write`, then `check`, and require `STATE_OK`.

- [ ] **Step 4: Run complete Project State suite**

```bash
python3 -m unittest discover -s tests/project_state -v
```

Expected: all tests PASS, including unchanged v0.3/v0.4 suites.

- [ ] **Step 5: Commit example/CI**

```bash
git add examples/project-state/v0.5-minimal .github/workflows/project-state.yml tests/project_state/test_state.py
git commit -m "ci: verify Project State v0.5 lineage semantics"
```

---

### Task 6: P32 Completion Evidence and P34 Handoff

**Files:**
- Modify only if needed for evidence bookkeeping: PR #14 body/comments; do not promote v0.5 Authority or migrate root manifests in this task.

**Interfaces:**
- Produces: reviewer-accessible exact-head evidence for independent P34.

- [ ] **Step 1: Run full local verification**

```bash
python3 -m unittest discover -s tests/project_state -v
python3 -m unittest discover -s tests/skillset -v
python3 evals/scripts/validate_corpus.py
python3 -m unittest discover -s evals/tests -v
python3 -m tools.aegis_state.cli validate .
python3 -m tools.aegis_state.cli check .
python3 -m tools.aegis_state.cli validate examples/project-state/v0.5-minimal
python3 -m tools.aegis_state.cli check examples/project-state/v0.5-minimal
```

Expected: all PASS. Root remains schema 0.4; v0.5 example is schema 0.5.

- [ ] **Step 2: Confirm historical root files were not migrated**

```bash
git diff main...HEAD -- .aegis/project.json .aegis/gates.json .aegis/integrations.json .aegis/state.json
```

Expected: no v0.5 root migration. Any changes to these files are a scope violation before P34/P23.

- [ ] **Step 3: Confirm protected PR #9 truth in executable fixture**

Run the exact `test_root_pr9_reconciliation_preserves_nonconforming_occurrence` test and capture its PASS as P20/P34 evidence.

- [ ] **Step 4: Wait for hosted CI on exact head and materialize evidence**

Required hosted evidence:

```text
Aegis Project State Integrity = PASS
Aegis Skillset Integrity      = PASS if triggered by touched shared files; otherwise existing full regressions must be run/materialized before P34
```

Record exact commit SHA and run IDs in PR #14.

- [ ] **Step 5: Handoff to independent P34**

P34 must audit all twelve acceptance requirements from the spec. It must not mutate root manifests, mark v0.5 Current, or execute P23 as part of the same evidence claim.

If P34 PASS, the next separate lifecycle sequence is:

```text
P23 Project State v0.4 -> v0.5
→ root deterministic migration
→ append PR #9 decision::0002 PASS using accepted Task 6 evidence
→ recompute root state and verify int-pr9 remains nonconforming
→ Skill Decomposition v0.2 P23 supersession
```
