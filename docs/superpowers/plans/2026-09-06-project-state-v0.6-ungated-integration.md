# Aegis Project State v0.6 Ungated Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Aegis stage:** `P30 Implementation Planning`

**Plan ID:** `PS-V06-P30-01`

**Goal:** Implement Project State v0.6 as the smallest deterministic Plugin-native extension that can represent `Integration -> Bound(exact Gate Decision) | Absent(no_applicable_integration_gate_decision)`, preserve immutable history, migrate v0.5 losslessly, and satisfy the accepted P20 verification contract without introducing an Aegis runtime/harness.

**Architecture:** Extend the repository's existing version-aware Project State schema/model/projection/migration/transition-validation paths. Keep semantic and Authority reasoning in Aegis Skills, repository execution in GitHub/Codex, durable truth in Git history, and Python/CI tooling mechanical only. Qualification implementation stops before root `.aegis` migration and before real PR #82 reconciliation; those require an exact P34 PASS result first.

**Tech Stack:** Python 3.12 stdlib, `unittest`, JSON / JSON Schema documents, Markdown Skill contracts, GitHub Actions.

**Spec:** `docs/project-state-ungated-integration-v0.6.md`

**Verification:** `docs/project-state-p20-ungated-integration-verification-design.md`

**Accepted Authority anchor:** `096b57f34dc9a29be6e844475f3725e0615f9968`

## Global Constraints

- Current Authority is `aegis-project-state-v0.6`; fallback to v0.5 for new implementation semantics is forbidden.
- Preserve v0.5 Gate Decision lineage semantics; v0.6 changes only the Integration binding relation plus the minimum supporting projection/migration/transition behavior.
- Canonical v0.6 binding is exactly `Bound(exact immutable Gate Decision)` or `Absent(no_applicable_integration_gate_decision)`.
- `Absent` is positive historical truth. Missing data, dangling refs, failed reads, empty search, 404, timeout, permissions failure, incomplete pagination, persistence lag, or unresolved decision identity must never imply `Absent`.
- `awaiting_integration -> Bound only`; `integrated -> Bound | Absent`; `closed_unmerged -> Bound only`.
- `Bound(PASS/PASS_WITH_FINDINGS) -> conforming`; `Bound(BLOCKED_*) -> nonconforming`; `Absent -> nonconforming`.
- `Bound(BLOCKED)` and `Absent` must remain distinguishable in authored and generated state.
- Once `integrated`, `id`, `kind`, `ref`, `target_ref`, `integrated_revision`, and `gate_decision_binding` are immutable. O6 may append corroborating evidence only.
- A later PASS must never rewrite an earlier Bound(BLOCKED) or Absent occurrence.
- v0.5 -> v0.6 migration converts every legacy `gate_decision_id: D` to `gate_decision_binding: {kind: bound, gate_decision_id: D}` and infers zero Absent records.
- PR #82 is a verification fixture before P34, not a real root `.aegis` mutation during the qualification implementation.
- Do not modify root `.aegis/**` in PS-V06-I01 through PS-V06-I04.
- Do not create or require `integration_ops.py`, `transaction.py`, a transition dispatcher service, an integration-history service, a daemon, agent runtime, custom harness, background reconciler, repository-state service, transaction server, or internal execution loop.
- A tiny pure helper is allowed only inside existing deterministic tooling when it removes repeated mechanical parsing/validation and owns no lifecycle/Authority decision.
- `CI PASS != Authority PASS`; `Codex complete != P34 PASS`; repository write success does not establish historical Absent.
- Every P31 package derived from this plan must use repository `Mostorm-Labs/aegis` and a non-null `task_anchor` whose revision is `096b57f34dc9a29be6e844475f3725e0615f9968` with relation `ancestor`, unless a later accepted control-plane reconciliation explicitly supersedes that anchor.
- Every P32 result must be materialized at a reviewer-accessible durable Git ref before it can return to control review.

---

## Repository implementation map

### Existing deterministic surfaces to extend

```text
tools/aegis_state/model.py
  version support, authored manifest validation, Gate Decision lineage, Integration binding validation

tools/aegis_state/compute.py
  deterministic state projection, conformance/applicability, routing projections

tools/aegis_state/cli.py
  validate / recompute / check / transition-check / migration entrypoints

tools/aegis_state/transition_v05.py
  existing immutable Gate Contract / Gate Decision cross-snapshot enforcement

tools/aegis_state/migrate_v05.py
  existing versioned deterministic migration pattern
```

### New versioned deterministic surfaces allowed by this plan

```text
schemas/project-state/v0.6/**
examples/project-state/v0.6-minimal/**
tools/aegis_state/migrate_v06.py
tools/aegis_state/transition_v06.py
tests/project_state/test_integration_binding_v06.py
tests/project_state/test_migration_v06.py
tests/project_state/test_integration_transition_v06.py
```

`migrate_v06.py` and `transition_v06.py` are deterministic repository-support utilities analogous to the existing v0.5 files. They are not runtime services or operation executors.

### Skill/control-plane surfaces

```text
skillset/skills/aegis-project-state/SKILL.md
skillset/skills/aegis-project-state/references/project-state.md
skills/aegis-project-state/SKILL.md
skills/aegis-project-state/references/project-state.md
```

### Verification surfaces

```text
evals/cases/dogfood.json
.github/workflows/project-state.yml
existing tests/project_state/** regressions
existing tests/skillset/** regressions
existing evals/tests/** regressions
```

### Explicitly excluded from the pre-P34 implementation candidate

```text
.aegis/project.json
.aegis/authorities.json
.aegis/gates.json
.aegis/evidence.json
.aegis/integrations.json
.aegis/state.json
```

---

# Dependency graph

```text
PS-V06-I01  v0.6 binding model + projection + schema/example
        |
        v
PS-V06-I02  v0.5->v0.6 migration + v0.6 transition immutability
        |
        v
PS-V06-I03  Project State Skill/reference + behavioral regression corpus
        |
        v
PS-V06-I04  CI/self-host qualification + exact candidate materialization
        |
        v
P34 independent Gate against P20
        |
        +-- PASS --> successor persistence package may be created
        |
        +-- BLOCKED_* --> P35/P36, no root migration
```

Tasks I01-I04 are the only tasks eligible for immediate P31 packaging from this P30. Real root migration and PR #82 reconciliation are deliberately not released until P34 provides an exact accepted result.

---

### Task PS-V06-I01: Implement v0.6 Gate Decision Binding representation and deterministic projection

**Purpose:** Make v0.6 manifests mechanically representable and prove Bound/Absent status, conformance, and non-inference semantics before any root migration.

**Dependencies:** P23 Current Authority `096b57f34dc9a29be6e844475f3725e0615f9968`.

**Files:**
- Create: `tests/project_state/test_integration_binding_v06.py`
- Create: `schemas/project-state/v0.6/project.schema.json`
- Create: `schemas/project-state/v0.6/authorities.schema.json`
- Create: `schemas/project-state/v0.6/gates.schema.json`
- Create: `schemas/project-state/v0.6/evidence.schema.json`
- Create: `schemas/project-state/v0.6/integrations.schema.json`
- Create: `schemas/project-state/v0.6/state.schema.json`
- Create: `examples/project-state/v0.6-minimal/.aegis/project.json`
- Create: `examples/project-state/v0.6-minimal/.aegis/authorities.json`
- Create: `examples/project-state/v0.6-minimal/.aegis/gates.json`
- Create: `examples/project-state/v0.6-minimal/.aegis/evidence.json`
- Create: `examples/project-state/v0.6-minimal/.aegis/integrations.json`
- Create: `examples/project-state/v0.6-minimal/.aegis/state.json`
- Modify: `tools/aegis_state/model.py`
- Modify: `tools/aegis_state/compute.py`

**Interfaces:**
- Consumes existing v0.5 Gate Contract / Gate Decision lineage without semantic change.
- Produces v0.6 authored `gate_decision_binding` validation.
- Produces v0.6 `integration_conformance[]` entries whose `gate_decision_binding` preserves whether the historical occurrence is Bound or Absent.
- Produces `generator_version = "0.6"` for v0.6 manifests while leaving v0.3/v0.4/v0.5 output unchanged.

- [ ] **Step 1: Write RED v0.6 binding tests before production changes**

Create the test helper with v0.6 authored manifests:

```python
D1 = "G1::decision::0001"


def bound(decision_id=D1):
    return {"kind": "bound", "gate_decision_id": decision_id}


def absent():
    return {"kind": "absent", "reason": "no_applicable_integration_gate_decision"}
```

The helper must write `schema_version: "0.6"` to all five authored manifests and use v0.5-style Gate Contract + Decision lineage unchanged.

Add tests with these exact expectations:

```python
# integrated + Bound(PASS)
self.assertEqual([], validate_manifests(manifests))
self.assertIn(
    {
        "integration_id": "int1",
        "gate_decision_binding": bound(D1),
        "conformance": "conforming",
    },
    compute_state(manifests)["integration_conformance"],
)

# integrated + Absent
self.assertEqual([], validate_manifests(manifests))
state = compute_state(manifests)
self.assertIn(
    {
        "integration_id": "int-absent",
        "gate_decision_binding": absent(),
        "conformance": "nonconforming",
    },
    state["integration_conformance"],
)
self.assertIn("int-absent", state["nonconforming_integrations"])
self.assertNotIn("int-absent", state["awaiting_integrations"])
```

Also add negative tests for:

```text
missing gate_decision_binding
unknown binding kind
Bound missing gate_decision_id
Bound dangling gate_decision_id
Absent missing reason
Absent wrong reason
awaiting_integration + Absent
closed_unmerged + Absent
```

- [ ] **Step 2: Run RED and confirm the failure is semantic/version support**

Run:

```bash
python3 -m unittest tests.project_state.test_integration_binding_v06 -v
```

Expected RED: v0.6 is unsupported and/or binding semantics are not implemented. Import errors, syntax errors, or malformed fixtures do not count as valid RED evidence.

- [ ] **Step 3: Add v0.6 schemas by preserving v0.5 unchanged except where v0.6 requires a new version/binding shape**

All six v0.6 schema documents use:

```json
"schema_version": {"const": "0.6"}
```

The Integration binding definition is exactly:

```json
"gate_decision_binding": {
  "oneOf": [
    {
      "type": "object",
      "additionalProperties": false,
      "required": ["kind", "gate_decision_id"],
      "properties": {
        "kind": {"const": "bound"},
        "gate_decision_id": {"type": "string", "minLength": 1}
      }
    },
    {
      "type": "object",
      "additionalProperties": false,
      "required": ["kind", "reason"],
      "properties": {
        "kind": {"const": "absent"},
        "reason": {"const": "no_applicable_integration_gate_decision"}
      }
    }
  ]
}
```

The v0.6 `integrations.schema.json` requires `gate_decision_binding` instead of `gate_decision_id`.

Use JSON Schema conditionals to forbid `Absent` when status is `awaiting_integration` or `closed_unmerged`; `integrated_revision` remains required only for `integrated`.

The v0.6 `state.schema.json` keeps all existing v0.5 projections but changes v0.6 `integration_conformance[]` item shape to:

```json
{
  "integration_id": "int1",
  "gate_decision_binding": {
    "kind": "bound",
    "gate_decision_id": "G1::decision::0001"
  },
  "conformance": "conforming"
}
```

or the exact Absent binding object. This is required so generated state does not collapse `Bound(BLOCKED)` and `Absent` into the same opaque `nonconforming` record.

- [ ] **Step 4: Extend `model.py` version support without changing old-version semantics**

Set:

```python
SCHEMA_VERSION = "0.6"
SUPPORTED_SCHEMA_VERSIONS = {"0.3", "0.4", "0.5", "0.6"}
DECISION_SCHEMA_VERSIONS = {"0.5", "0.6"}
```

Update `ManifestSet.decision_items` and Gate Decision lineage branches to use `DECISION_SCHEMA_VERSIONS`.

Add a small pure binding parser in `model.py`:

```python
def integration_binding(item: dict, schema_version: str | None) -> tuple[str | None, str | None]:
    if schema_version == "0.6":
        binding = item.get("gate_decision_binding")
        if not isinstance(binding, dict):
            return None, None
        kind = binding.get("kind")
        if kind == "bound":
            decision_id = binding.get("gate_decision_id")
            return "bound", decision_id if isinstance(decision_id, str) else None
        if kind == "absent":
            reason = binding.get("reason")
            return "absent", reason if isinstance(reason, str) else None
        return None, None
    if schema_version == "0.5":
        decision_id = item.get("gate_decision_id")
        return "bound", decision_id if isinstance(decision_id, str) else None
    return None, None
```

This helper is mechanical parsing only. It must not infer Absent.

For v0.6 Integration validation:

```text
kind=bound:
  require a non-empty gate_decision_id
  require the exact decision to exist

kind=absent:
  require reason == no_applicable_integration_gate_decision
  require status == integrated
  do not synthesize or resolve a Gate
```

For v0.6 `awaiting_integration`, require `kind=bound`, the bound decision to be the unique current Gate Decision, verdict PASS/PASS_WITH_FINDINGS, effective current Authority/evidence, and available integration evidence.

- [ ] **Step 5: Extend `compute.py` for v0.6 while preserving v0.5 generated shape**

Treat v0.6 as a Gate Decision lineage version wherever v0.5 currently uses current-decision heads.

For v0.6 integrated Bound:

```python
binding = dict(integration["gate_decision_binding"])
decision_id = binding["gate_decision_id"]
bound_decision = decision_by_id.get(decision_id)
verdict = bound_decision.get("verdict") if bound_decision else None
conformance = "conforming" if verdict in PASS_VERDICTS else "nonconforming"
```

For v0.6 integrated Absent:

```python
binding = dict(integration["gate_decision_binding"])
conformance = "nonconforming"
applicability = "historical"
```

Do not create a Gate blocker, fake Gate ID, P34 route, or current actionability from Absent alone.

Emit v0.6 conformance as:

```python
{
    "integration_id": iid,
    "gate_decision_binding": binding,
    "conformance": conformance,
}
```

Retain the existing v0.5 `gate_decision_id` generated shape unchanged for backward compatibility.

For v0.6:

```python
generator_version = "0.6"
```

and include the same Gate Decision projections as v0.5.

- [ ] **Step 6: Materialize `examples/project-state/v0.6-minimal`**

Use one current Authority, one Gate Contract, one PASS decision, and one `awaiting_integration` Bound record. Generate `state.json` only from `compute_state()` after the implementation passes focused tests; do not hand-author a digest.

Commands:

```bash
python3 -m tools.aegis_state.cli validate examples/project-state/v0.6-minimal
python3 -m tools.aegis_state.cli recompute examples/project-state/v0.6-minimal --write
python3 -m tools.aegis_state.cli check examples/project-state/v0.6-minimal
```

Expected: `VALID`, `STATE_WRITTEN`, `STATE_OK`.

- [ ] **Step 7: Run focused and backward-compatibility tests**

```bash
python3 -m unittest tests.project_state.test_integration_binding_v06 -v
python3 -m unittest tests.project_state.test_gate_decision_lineage_v05 -v
python3 -m unittest tests.project_state.test_state -v
```

Expected: PASS.

- [ ] **Step 8: Commit I01 as an independently reviewable slice**

```bash
git add \
  schemas/project-state/v0.6 \
  examples/project-state/v0.6-minimal \
  tools/aegis_state/model.py \
  tools/aegis_state/compute.py \
  tests/project_state/test_integration_binding_v06.py
git commit -m "feat: add Project State v0.6 integration bindings"
```

**I01 exit criteria:** P20 V1-V4 core fixtures pass; v0.5 regressions remain green; no root `.aegis` mutation; no runtime/harness files added.

---

### Task PS-V06-I02: Implement lossless v0.5 -> v0.6 migration and immutable v0.6 transition checks

**Purpose:** Prove that existing v0.5 history becomes Bound without inferred Absent and that integrated v0.6 history cannot later be rewritten.

**Dependencies:** PS-V06-I01 accepted implementation slice.

**Files:**
- Create: `tools/aegis_state/migrate_v06.py`
- Create: `tools/aegis_state/transition_v06.py`
- Create: `tests/project_state/test_migration_v06.py`
- Create: `tests/project_state/test_integration_transition_v06.py`
- Modify: `tools/aegis_state/transition_v05.py`
- Modify: `tools/aegis_state/cli.py`

**Interfaces:**
- Produces `migrate_v05_to_v06(manifests: ManifestSet) -> ManifestSet`.
- Preserves `validate_v05_transition(previous, current)` behavior.
- Produces `validate_v06_transition(previous, current) -> list[str]`.
- Produces `validate_v05_to_v06_transition(previous, current) -> list[str]` for the later root migration boundary.
- Extends existing CLI `transition-check` to dispatch on `(previous_version, current_version)`.
- Adds CLI `migrate-v06 SOURCE_ROOT DESTINATION_ROOT`.

- [ ] **Step 1: Write migration RED tests**

Test that a valid v0.5 record:

```json
{
  "id": "int1",
  "gate_decision_id": "G1::decision::0001",
  "status": "integrated"
}
```

becomes v0.6:

```json
{
  "id": "int1",
  "gate_decision_binding": {
    "kind": "bound",
    "gate_decision_id": "G1::decision::0001"
  },
  "status": "integrated"
}
```

Assert:

```python
self.assertEqual("0.6", migrated.schema_version)
self.assertNotIn("gate_decision_id", migrated.integration_items[0])
self.assertEqual(bound(D1), migrated.integration_items[0]["gate_decision_binding"])
self.assertFalse(any(i["gate_decision_binding"]["kind"] == "absent" for i in migrated.integration_items))
```

Cover integrated PASS, integrated BLOCKED, awaiting, and closed_unmerged source records.

- [ ] **Step 2: Write v0.6 transition RED tests**

For an already integrated v0.6 record, reject all of:

```text
removal of the record
kind change
ref change
target_ref change
integrated_revision change
Bound(D1) -> Bound(D2)
Bound(D) -> Absent
Absent -> Bound(D)
Absent reason rewrite
integrated -> awaiting_integration
integrated -> closed_unmerged
removal of previously recorded evidence_ids
```

Accept exactly:

```text
same immutable payload
same immutable payload + additional evidence_ids (O6)
new unrelated records
append-only later Gate Decision lineage that leaves the historical binding unchanged
```

- [ ] **Step 3: Refactor only the reusable Gate/Decision immutability kernel from `transition_v05.py`**

Keep the public v0.5 function stable:

```python
def validate_v05_transition(previous: ManifestSet, current: ManifestSet) -> list[str]:
    if previous.schema_version != "0.5" or current.schema_version != "0.5":
        return ["gate decision transition validation requires schema_version 0.5 on both snapshots"]
    return validate_gate_decision_immutability(previous, current)
```

Add the pure helper in the same module:

```python
def validate_gate_decision_immutability(previous: ManifestSet, current: ManifestSet) -> list[str]:
    # existing Gate Contract and Gate Decision comparison body
```

No dispatcher service or new runtime abstraction is introduced.

- [ ] **Step 4: Implement `migrate_v06.py` as a pure one-shot transformer**

Start from a strict-valid v0.5 source:

```python
def migrate_v05_to_v06(manifests: ManifestSet) -> ManifestSet:
    if manifests.schema_version != "0.5":
        raise ValueError("v0.6 migration requires schema_version 0.5")
    source_errors = validate_manifests(manifests, strict_gate_validity=True)
    if source_errors:
        raise ValueError("invalid v0.5 source: " + "; ".join(source_errors))
```

Deep-copy project/authorities/gates/evidence/integrations, convert each Integration exactly once, set all authored `schema_version` fields to `"0.6"`, and return a `ManifestSet`.

Do not add PR #82 during migration. Migration infers zero Absent records.

- [ ] **Step 5: Implement `transition_v06.py`**

For v0.6 -> v0.6, first call `validate_gate_decision_immutability()`, then protect integrated history with this normalization:

```python
def _integrated_identity(item: dict) -> dict:
    return {
        "id": item.get("id"),
        "kind": item.get("kind"),
        "ref": item.get("ref"),
        "target_ref": item.get("target_ref"),
        "integrated_revision": item.get("integrated_revision"),
        "gate_decision_binding": item.get("gate_decision_binding"),
    }
```

For every previously integrated record:

```text
current record must still exist
status must still be integrated
_integrated_identity must be exactly equal
old evidence_ids must be a subset of current evidence_ids
```

For v0.5 -> v0.6 transition validation, require every previous v0.5 Gate Contract/Decision to remain unchanged and every previous Integration to retain identity/status/revision/evidence while changing only its binding representation to exact `Bound(previous gate_decision_id)`. Additive v0.6 records are allowed; rewriting legacy history is not.

- [ ] **Step 6: Extend CLI without changing the meaning of existing commands**

Add:

```python
from .migrate_v06 import migrate_v05_to_v06
from .transition_v06 import validate_v05_to_v06_transition, validate_v06_transition
```

Dispatch `transition-check` by exact version pair:

```python
pair = (previous.schema_version, current.schema_version)
if pair == ("0.5", "0.5"):
    transition_errors = validate_v05_transition(previous, current)
elif pair == ("0.6", "0.6"):
    transition_errors = validate_v06_transition(previous, current)
elif pair == ("0.5", "0.6"):
    transition_errors = validate_v05_to_v06_transition(previous, current)
else:
    transition_errors = [f"unsupported transition-check schema pair {pair[0]} -> {pair[1]}"]
```

Add `migrate-v06` mirroring the existing `migrate-v05` destination-writing contract, printing:

```text
MIGRATED_V06: <destination>/.aegis
```

- [ ] **Step 7: Run focused migration/transition suites plus v0.5 regression**

```bash
python3 -m unittest tests.project_state.test_migration_v06 -v
python3 -m unittest tests.project_state.test_integration_transition_v06 -v
python3 -m unittest tests.project_state.test_gate_decision_transition_v05 -v
python3 -m unittest tests.project_state.test_gate_decision_transition_cli_v05 -v
python3 -m unittest tests.project_state.test_migration_v05 -v
```

Expected: PASS.

- [ ] **Step 8: Commit I02**

```bash
git add \
  tools/aegis_state/migrate_v06.py \
  tools/aegis_state/transition_v06.py \
  tools/aegis_state/transition_v05.py \
  tools/aegis_state/cli.py \
  tests/project_state/test_migration_v06.py \
  tests/project_state/test_integration_transition_v06.py
git commit -m "feat: enforce Project State v0.6 history transitions"
```

**I02 exit criteria:** P20 V5-V8/V12 migration and immutability evidence passes; v0.5 transition and migration behavior remains unchanged; no inferred Absent; no root migration.

---

### Task PS-V06-I03: Update the Project State Skill contract and durable behavioral regression corpus

**Purpose:** Make the ChatGPT Plugin/Skills control plane understand v0.6 semantics while preserving the platform/Authority boundary.

**Dependencies:** PS-V06-I01 and I02 accepted implementation slices.

**Files:**
- Modify: `skillset/skills/aegis-project-state/SKILL.md`
- Modify: `skillset/skills/aegis-project-state/references/project-state.md`
- Modify: `skills/aegis-project-state/SKILL.md`
- Modify: `skills/aegis-project-state/references/project-state.md`
- Modify: `evals/cases/dogfood.json`

**Interfaces:**
- Source Skill and materialized Skill remain semantically identical under existing Skillset validation.
- The reference becomes explicitly version-aware through v0.6.
- Dogfood cases make false-Absent, retroactive-PASS, and ungated-occurrence failure modes durable regression inputs.

- [ ] **Step 1: Update `SKILL.md` product contract, not implementation mechanics**

The short Skill must explicitly state:

```text
v0.6 Gate Decision Binding = Bound(exact decision) | Absent(no_applicable_integration_gate_decision)
missing/failed/unresolved evidence != Absent
awaiting integration remains Bound-only
integrated binding is immutable historical truth
a later PASS cannot retroactively bind an older occurrence
historical Absent requires durable Occurrence Basis + accepted Absence Basis
P13 O1-O6 are reasoning vocabulary, not runtime API calls
state.json is generated cache, never Authority
repository/tooling reality cannot silently override newer durable Authority
```

Update the description/version language so the Skill no longer claims v0.4 is the latest supported semantics.

Do not add agent-loop, reconciliation-worker, transaction, or background-service instructions.

- [ ] **Step 2: Rewrite the Project State reference as a version-aware v0.6-first contract**

Top-level order:

```text
canonical layout/startup
v0.6 Bound|Absent semantics
v0.6 status constraints
historical conformance
historical immutability/O1-O6
absence proof boundary
v0.5 Gate Decision lineage compatibility
v0.5 -> v0.6 migration
v0.4/v0.3 backward compatibility
platform/tool failure semantics
routing/safety boundary
```

The reference must include the exact canonical forms:

```yaml
gate_decision_binding:
  kind: bound
  gate_decision_id: <exact immutable Gate Decision id>
```

and:

```yaml
gate_decision_binding:
  kind: absent
  reason: no_applicable_integration_gate_decision
```

It must say that only an accepted governance/verification basis can establish historical absence; deterministic tooling validates representation but cannot discover governance truth by itself.

- [ ] **Step 3: Keep source/materialized copies aligned**

Apply the exact accepted source bytes to:

```text
skillset/skills/aegis-project-state/SKILL.md
skills/aegis-project-state/SKILL.md
```

and the exact accepted reference bytes to both reference paths. Do not allow the two copies to drift.

- [ ] **Step 4: Add three durable dogfood regression cases**

Append IDs in sequence after the current corpus maximum.

Case A title:

```text
Merged occurrence with no applicable Integration Gate must not fabricate authorization
```

Required findings include:

```text
A real repository occurrence remains durable even when no applicable integration-authorizing Gate Decision existed.
Project State v0.6 represents the proven historical absence explicitly rather than binding an unrelated P23/P34/P24 decision or deleting the occurrence.
```

Forbidden findings include:

```text
Treat the merge itself as PASS evidence.
Bind a later PASS retroactively.
Use P23 5122113780 as PR #82 merge authorization.
```

Case B title:

```text
Tool lookup failure must not become historical Absent
```

Required finding:

```text
404, timeout, permission failure, empty search, or incomplete lookup is unresolved evidence and must fail closed; it is not proof that no applicable Gate Decision existed.
```

Case C title:

```text
Later PASS must not rewrite an older Bound(BLOCKED) or Absent occurrence
```

Required finding:

```text
Current/future actionability may change after a later PASS, but the historical Integration binding and conformance remain tied to the occurrence-time truth.
```

- [ ] **Step 5: Run Skillset and corpus validation**

```bash
python3 -m tools.aegis_skillset.cli validate .
python3 -m unittest discover -s tests/skillset -v
python3 evals/scripts/validate_corpus.py
python3 -m unittest discover -s evals/tests -v
```

Expected: PASS.

- [ ] **Step 6: Commit I03**

```bash
git add \
  skillset/skills/aegis-project-state/SKILL.md \
  skillset/skills/aegis-project-state/references/project-state.md \
  skills/aegis-project-state/SKILL.md \
  skills/aegis-project-state/references/project-state.md \
  evals/cases/dogfood.json
git commit -m "docs: teach Project State skill v0.6 semantics"
```

**I03 exit criteria:** P20 V3/V9/V10 behavioral contract is durably represented; Skillset/eval regressions pass; source/materialized copies align; no new Skill/agent/runtime is added.

---

### Task PS-V06-I04: Wire v0.6 qualification into Project State CI and materialize the exact review candidate

**Purpose:** Produce the exact, independently reviewable implementation candidate and full mechanical evidence required to hand off to P34.

**Dependencies:** PS-V06-I01, I02, I03 complete on one descendant chain of the P23 anchor.

**Files:**
- Modify: `.github/workflows/project-state.yml`
- Modify only if a failing acceptance test proves necessary: existing `tests/project_state/**`, `tests/skillset/**`, `evals/tests/**`
- Do not modify: root `.aegis/**`

**Interfaces:**
- CI parses v0.3/v0.4/v0.5/v0.6 schemas.
- CI validates/checks both the existing v0.5 minimal project and new v0.6 minimal project.
- CI uses the existing `transition-check` command as the single deterministic cross-snapshot entrypoint; the CLI dispatches by version pair.
- Full Project State + Skillset + evaluation regression evidence is bound to one exact candidate revision.

- [ ] **Step 1: Extend schema parse and minimal-example CI**

Change schema parse loop to:

```bash
for version in v0.3 v0.4 v0.5 v0.6; do
  for schema in schemas/project-state/$version/*.json; do
    python3 -m json.tool "$schema" >/dev/null
  done
done
```

Add:

```bash
python3 -m tools.aegis_state.cli validate examples/project-state/v0.6-minimal
python3 -m tools.aegis_state.cli check examples/project-state/v0.6-minimal
```

Keep existing v0.4/v0.5 example checks.

- [ ] **Step 2: Generalize self-host transition enforcement without weakening v0.5**

For PR and push paths, archive the previous `.aegis` snapshot exactly as today. Use a shell `case` on `previous:current`:

```bash
case "$PREVIOUS_VERSION:$CURRENT_VERSION" in
  0.5:0.5|0.5:0.6|0.6:0.6)
    python3 -m tools.aegis_state.cli transition-check /tmp/aegis-previous .
    ;;
  *)
    echo "TRANSITION_CHECK_SKIPPED: previous=$PREVIOUS_VERSION current=$CURRENT_VERSION"
    ;;
esac
```

This preserves v0.5 enforcement, qualifies future v0.6 same-version immutability, and gives the later root 0.5->0.6 migration a fail-closed transition boundary.

- [ ] **Step 3: Run the full local acceptance matrix before pushing**

```bash
python3 -m unittest discover -s tests/project_state -v
python3 -m tools.aegis_state.cli validate examples/project-state/v0.5-minimal
python3 -m tools.aegis_state.cli check examples/project-state/v0.5-minimal
python3 -m tools.aegis_state.cli validate examples/project-state/v0.6-minimal
python3 -m tools.aegis_state.cli check examples/project-state/v0.6-minimal
python3 -m tools.aegis_state.cli validate .
python3 -m tools.aegis_state.cli check .
python3 -m tools.aegis_skillset.cli validate .
python3 -m unittest discover -s tests/skillset -v
python3 evals/scripts/validate_corpus.py
python3 -m unittest discover -s evals/tests -v
```

Root validation/check is expected to stay v0.5 and pass because this task still does not migrate root `.aegis`.

- [ ] **Step 4: Run explicit P20 golden checks before final materialization**

The test suite must prove all of these on the exact candidate:

```text
V1  Bound/Absent representation positive/negative corpus
V2  status x binding restrictions
V3  zero false-Absent from missing/unresolved authored data
V4  PASS/BLOCKED/Absent conformance projection stays distinguishable
V5  integrated historical identity/binding immutable
V6  later PASS cannot rewrite Bound(BLOCKED) or Absent
V7  v0.5 migration lossless, inferred Absent count = 0
V8  O1-O6 semantics realizable through state/transition validation without operation executor
V9  no forbidden runtime/harness/service files introduced
V10 platform result roles remain mechanical only in Skill/reference/eval contract
V11 PR #82 fixture => integrated + Absent + nonconforming; synthetic/retroactive variants rejected
V12 deterministic replay/idempotency stable
V13 stale/uncertain write semantics preserved in control-plane contract; no transaction service added
V14 v0.6 changes do not weaken exact-ref/fresh-state optimization safety
```

If any core item is missing, return `BLOCKED_EVIDENCE` rather than claiming P34 readiness.

- [ ] **Step 5: Push/materialize the exact implementation candidate and capture durable evidence**

The executor must return:

```yaml
actual_starting_revision: <observed descendant of task_anchor>
result_revision: <exact pushed commit SHA>
materialized_ref: <reviewer-accessible Git branch/commit>
changed_files: <exact list>
verification:
  project_state_tests: PASS
  v0_5_example: PASS
  v0_6_example: PASS
  root_v0_5_self_host: PASS
  skillset: PASS
  evals: PASS
ci:
  project_state_workflow: <run id/status if hosted run exists>
root_aegis_mutated: false
```

P31 will replace angle-bracket execution-return fields with actual results; they are return-schema fields, not implementation assumptions.

- [ ] **Step 6: Commit I04 before P34 handoff**

```bash
git add .github/workflows/project-state.yml
git commit -m "ci: qualify Project State v0.6 support"
```

If test files require legitimate acceptance repairs, include them in the same bounded commit or a preceding focused commit and record the reason in the P32 return.

**I04 exit criteria:** exact candidate is durable and reviewer-accessible; full Project State/Skillset/eval evidence is green or exact blocker is reported; root `.aegis` remains v0.5; result is ready for independent P34, not self-declared PASS.

---

# Post-P34 successor boundary — not released for P31 yet

The following work is known but **must not** be packaged for execution until P34 produces an exact accepted v0.6 implementation result. This is a dependency boundary, not a placeholder implementation task.

## Successor PS-V06-I05 — root v0.5 -> v0.6 Project State persistence

Release condition:

```text
P34 = PASS or otherwise explicitly authorizes the exact v0.6 implementation candidate for downstream persistence
```

When released, a fresh P31 package must bind the exact P34 decision/evidence and must:

```text
run/verify deterministic v0.5 -> v0.6 migration on root
persist aegis-project-state-v0.5 as Superseded/Historical
persist aegis-project-state-v0.6 as Current with ref docs/project-state-ungated-integration-v0.6.md
preserve all existing Gate Decisions and Integration history as Bound
recompute state.json
enforce 0.5 -> 0.6 transition-check
run full Project State + Skillset + eval CI
```

It must not create `int-pr82` in the same logical step unless the separately packaged O4 preconditions are also independently satisfied and the package explicitly authorizes that change.

## Successor PS-V06-I06 — PR #82 O4 historical reconciliation

Release conditions:

```text
root v0.6 persistence accepted
+
PR #82 occurrence evidence still exact/uncontradicted
+
P23 review 5122113780 still explicitly non-authorizing
+
P22 absence basis 5553423707 still uncontradicted
```

Expected authored record remains:

```yaml
id: int-pr82
kind: pull_request
ref: https://github.com/Mostorm-Labs/aegis/pull/82
status: integrated
target_ref: main
integrated_revision: 3a2607220cd875dc66857b334dcfbd2c763e7c7d
gate_decision_binding:
  kind: absent
  reason: no_applicable_integration_gate_decision
```

The package must attach reviewer-resolvable occurrence/absence evidence IDs according to the then-current accepted root evidence registry. It must not invent a Gate Decision, use P23 `5122113780` as merge authorization, or bind a later PASS retroactively.

---

# P30 evidence-to-task coverage

```text
P20 V1-V4   -> PS-V06-I01
P20 V5-V8   -> PS-V06-I02
P20 V9-V10  -> PS-V06-I03 + changed-file review in I04
P20 V11     -> I01 fixture + I03 dogfood + I04 exact Gate evidence
P20 V12     -> I02 deterministic migration/transition + I04 replay
P20 V13     -> I03 platform contract preservation + I04 changed-file review
P20 V14     -> I03 Skill/reference preservation + I04 full regression
```

No P20 mandatory evidence class is intentionally deferred past the qualification candidate.

Real root persistence and PR #82 reconciliation are post-P34 applications of already-qualified behavior, not substitutes for the pre-P34 P20 proof corpus.

---

# P30 package-release policy

P31 should package **one task at a time** in dependency order:

```text
first release: PS-V06-I01
then:          PS-V06-I02 after I01 control reconciliation
then:          PS-V06-I03 after I02 control reconciliation
then:          PS-V06-I04 after I03 control reconciliation
```

A P31 package may combine adjacent steps only if fresh repository reality proves they are already inseparable on one exact descendant and the combined package remains independently reviewable. Do not collapse all tasks into one unbounded Codex handoff by default.

Every package must include:

```yaml
repository:
  provider: github
  full_name: Mostorm-Labs/aegis

task_anchor:
  revision: 096b57f34dc9a29be6e844475f3725e0615f9968
  relation: ancestor

current_authority:
  id: aegis-project-state-v0.6
  ref: docs/project-state-ungated-integration-v0.6.md
  authority_materialization: 096b57f34dc9a29be6e844475f3725e0615f9968

verification_authority:
  ref: 19b0433a9641847289262a3ad664122c78907569

forbidden:
  - root .aegis mutation before P34 PASS
  - real int-pr82 reconciliation before root v0.6 persistence
  - runtime/harness/agent/service expansion
  - retroactive Gate authorization
  - synthetic Gate Decision for PR #82
  - merge/release/rollout unless separately authorized
```

P31 must define a reviewer-accessible `materialized_ref` obligation before any P32 handoff.

---

# P30 self-review

## Spec coverage

- v0.6 Bound|Absent authored representation -> I01.
- status/binding constraints -> I01.
- Absent non-inference -> I01 + I03.
- conformance distinction -> I01.
- immutable integrated history/O6 -> I02.
- later PASS preservation -> I02.
- v0.5 migration with zero inferred Absent -> I02.
- Plugin-native/no-runtime boundary -> I03 + I04 changed-file review.
- platform result/Authority separation -> I03.
- PR #82 golden oracle -> I01 fixture + I03 corpus + I04 Gate evidence.
- deterministic replay and transition safety -> I02 + I04.
- CI/version support -> I04.
- root persistence ordering -> post-P34 I05 boundary.
- real PR #82 O4 ordering -> post-P34 I06 boundary.

No accepted v0.6/P20 requirement is left without an implementation or evidence owner.

## Placeholder scan

No production implementation step relies on `TBD`, `TODO`, or an unspecified algorithm. Fields that are intentionally unknown until execution (`result_revision`, CI run ID, exact P34 decision/evidence) appear only in executor-return or post-Gate dependency contracts and cannot be correctly invented during P30.

## Type/interface consistency

- `gate_decision_binding.kind` is consistently `bound | absent`.
- Bound consistently carries `gate_decision_id`.
- Absent consistently carries reason `no_applicable_integration_gate_decision`.
- `migrate_v05_to_v06()` produces only Bound legacy integrations.
- `validate_v06_transition()` protects v0.6 integrated history.
- `validate_v05_to_v06_transition()` protects the later root migration boundary.
- CLI remains the existing deterministic entrypoint; no new runtime execution surface is created.

---

# Formal P30 disposition

```yaml
p30_implementation_plan:
  id: PS-V06-P30-01
  scope: aegis/project-state

  authority:
    id: aegis-project-state-v0.6
    exact_ref: 096b57f34dc9a29be6e844475f3725e0615f9968

  verification:
    exact_ref: 19b0433a9641847289262a3ad664122c78907569

  implementation_slices:
    - PS-V06-I01
    - PS-V06-I02
    - PS-V06-I03
    - PS-V06-I04

  post_gate_successors:
    - PS-V06-I05
    - PS-V06-I06

  first_package_to_release: PS-V06-I01
  task_anchor:
    revision: 096b57f34dc9a29be6e844475f3725e0615f9968
    relation: ancestor

  root_aegis_mutation_authorized: false
  pr82_real_reconciliation_authorized: false
  p32_started: false
  p34_performed: false
  merge_authorized: false
  release_authorized: false

  earlier_untrusted_layer: none
  blocker: none

  verdict: READY
  disposition: READY_FOR_P31_TASK_PACKAGING
```

---

# Stop boundary

P30 stops after implementation planning.

The next legal substantive stage is:

```text
aegis-implementation -> P31 Task Packaging
```

The first P31 package should be only `PS-V06-I01` unless fresh repository state justifies a different independently reviewable boundary.

P30 does not start Codex, does not create a CODE_EXECUTION handoff, does not modify implementation files, does not migrate root `.aegis`, does not reconcile PR #82, and does not perform P34, merge, release, or rollout.
