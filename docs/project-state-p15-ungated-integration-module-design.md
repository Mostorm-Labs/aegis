# Aegis Project State — P15 Ungated Integration Module Design

Status: **P15 Module Design Candidate**

Scope: `aegis/project-state`

Triggering finding: `P22-F2 = MISSING_CONTRACT / SPEC_DEFECT`

Repository basis: `main@3a2607220cd875dc66857b334dcfbd2c763e7c7d`

P12 semantic basis candidate: `777e1e8a9652e2cbf220d234798641d65dc9b0c9`

P13 operation basis candidate: `b742ebb9f27520a595b2e73370f42157e28ea72e`

P14 architecture basis candidate: `21d6dd535dc7ab50898f7294e73c4bdd98757fc5`

Current Authority under repair: `aegis-project-state-v0.5`

This artifact refines P14 into concrete module boundaries and interfaces. It does not assign a replacement Project State version, does not modify `.aegis/*`, does not create a new Current Authority, and does not authorize implementation, repository integration, release, or rollout.

---

## 1. Design objective

P15 must realize the P12/P13 semantics with the smallest coherent extension of the current Project State tooling.

The current package is already usefully decomposed:

```text
tools/aegis_state/
  model.py
  compute.py
  transition_v05.py
  migrate_v05.py
  cli.py
```

The repair must not create a parallel Project State engine.

The module design therefore follows three principles:

1. preserve existing modules where their responsibility is already correct;
2. add only the missing domain modules required by P12/P13;
3. centralize Gate Decision Binding semantics so `model.py`, `compute.py`, transition validation, migration, and mutation do not each implement their own interpretation.

---

## 2. Target package map

The bounded target module map is:

```text
tools/aegis_state/
  __init__.py                     existing
  model.py                        existing / extend
  integration_binding.py          NEW
  integration_ops.py              NEW
  integration_history.py          NEW
  transition.py                   NEW dispatcher/composition boundary
  transition_v05.py               existing / preserve
  compute.py                      existing / extend
  transaction.py                  NEW
  migrate_v05.py                  existing / preserve
  <future target migration>.py    deferred until replacement version exists
  cli.py                          existing / extend thinly
```

Schema and enforcement surfaces remain outside the Python package:

```text
schemas/project-state/<version>/**
.github/workflows/project-state.yml
tests/project_state/**
examples/project-state/**
```

No replacement-version directory or filename is assigned by P15.

---

## 3. Module: `integration_binding.py`

### Purpose

Own the pure domain representation and interpretation of Gate Decision Binding.

This module exists specifically to prevent duplicated Bound/Absent logic across validators, projections, transitions, operations, and migration.

### Public domain types

Conceptual interface:

```python
@dataclass(frozen=True)
class BoundBinding:
    gate_decision_id: str

@dataclass(frozen=True)
class AbsentBinding:
    reason: str

GateDecisionBinding = BoundBinding | AbsentBinding
```

The implementation may use equivalent immutable representations, but callers must not inspect raw manifest fields independently when binding semantics are required.

### Required public helpers

Conceptually:

```python
def read_binding(integration: dict, schema_version: str) -> GateDecisionBinding | None:
    ...


def validate_binding_shape(integration: dict, schema_version: str) -> list[str]:
    ...


def binding_identity(binding: GateDecisionBinding) -> tuple:
    ...
```

`read_binding` behavior:

- v0.5 `gate_decision_id: D` is interpreted losslessly in memory as `BoundBinding(D)`;
- a replacement schema may expose explicit `gate_decision_binding` Bound or Absent variants;
- older schemas without binding semantics may return `None` where appropriate;
- no schema version may infer `Absent` from a missing field or failed lookup.

### Invariants

```text
missing binding data != Absent
unknown decision != Absent
dangling decision != Absent
```

For explicit Absent:

```text
reason == no_applicable_integration_gate_decision
```

until a later Authority explicitly expands the reason vocabulary.

### Non-ownership

This module must not:

- inspect GitHub;
- resolve occurrence-time governance applicability;
- decide whether absence evidence is sufficient;
- mutate manifests;
- compare revisions;
- calculate current actionability.

### Dependency rule

`integration_binding.py` must remain lower-level than `model.py`.

It must not import `model.py` or `ManifestSet`, preventing a dependency cycle.

---

## 4. Module: `model.py`

### Preserve current responsibility

`model.py` remains the owner of:

- `ManifestSet`;
- manifest loading;
- registry accessors;
- single-snapshot validation;
- cross-reference validation;
- schema-version consistency.

### Required extension

Integration validation delegates binding-specific rules to `integration_binding.py`.

The effective validation path becomes:

```text
Integration record
  -> structural required fields
  -> read/validate binding
  -> status × binding rule
  -> referenced decision/evidence validation
```

For the replacement schema:

```text
awaiting_integration -> Bound only
integrated           -> Bound | Absent
closed_unmerged      -> Bound only
```

### Important non-ownership

`model.py` must not determine that `Absent` is historically true.

It validates only that an already-authored Absent state is structurally and referentially valid.

It also must not own cross-snapshot immutability.

---

## 5. Module: `integration_ops.py`

### Purpose

Own P13 O1–O6 as pure in-memory domain operations.

This is the only domain module that may construct a new Integration binding from an already-qualified operation request.

### Operation request types

Conceptually:

```python
IntegrationOperation = (
    RegisterAwaiting
    | RebindAwaiting
    | FinalizeOccurrence
    | ReconcileHistoricalOccurrence
    | CloseUnmergedCandidate
    | AppendCorroboratingEvidence
)
```

The exact Python type mechanism is implementation detail, but operation kind must be explicit and closed.

### Stable entrypoint

Conceptually:

```python
def apply_integration_operation(
    manifests: ManifestSet,
    operation: IntegrationOperation,
) -> ManifestSet:
    ...
```

The function:

- receives a complete source `ManifestSet`;
- deep-copies or otherwise preserves input immutability;
- applies exactly one logical P13 operation;
- returns a candidate authored `ManifestSet`;
- performs no file writes;
- performs no state projection.

### O4 request boundary

A historical Absent reconciliation request must carry role-separated qualified inputs equivalent to:

```text
occurrence basis IDs
absence basis IDs
```

The operation module may require both sets to be non-empty and require every referenced evidence ID to exist in the candidate evidence registry.

However, it must not itself decide that those evidence records prove the claim.

That proof policy belongs to P20 Verification Authority.

### Canonical persistence caution

P12/P13 currently require durable occurrence and absence bases, but do not define separate canonical manifest fields for the two roles.

Therefore P15 does **not** invent `occurrence_evidence_ids` or `absence_evidence_ids` as new authored schema fields.

The operation request may keep the roles distinct while requiring the referenced IDs to be durably present in the existing evidence relationship permitted by the accepted schema.

If P20 later proves that durable role discrimination must itself be canonical state, that is a semantic-schema requirement and must route back to P12 rather than being smuggled into implementation.

### Idempotency

`integration_ops.py` owns P13 replay identity behavior:

```text
same Integration.id + same immutable historical payload
-> deterministic no-op

same Integration.id + different immutable historical payload
-> HISTORICAL_INTEGRATION_ID_CONFLICT
```

### Non-ownership

The module must not:

- fetch repository evidence;
- infer an applicable Gate Decision;
- infer Absent;
- persist files;
- regenerate `state.json`;
- bypass snapshot or transition validation.

---

## 6. Module: `integration_history.py`

### Purpose

Own reusable cross-snapshot Integration history comparison.

This module is separate from `transition_v05.py` because the existing v0.5 transition module protects v0.5 Gate Contract / Gate Decision lineage and must remain valid for historical v0.5 projects.

### Stable entrypoint

Conceptually:

```python
def validate_integration_history(
    previous: ManifestSet,
    current: ManifestSet,
) -> list[str]:
    ...
```

### Historical identity payload

For every previously finalized Integration:

```text
id
kind
ref
target_ref
integrated_revision
gate_decision_binding
```

must compare equal after normalization through `integration_binding.py`.

The module must reject:

```text
removal of an integrated occurrence
Bound(D1) -> Bound(D2)
Bound(D) -> Absent
Absent -> Bound(D)
Absent(reason1) -> Absent(reason2)
integrated_revision change
integrated -> awaiting_integration
integrated -> closed_unmerged
```

### Evidence append rule

For an already integrated record:

```text
previous evidence_ids ⊆ current evidence_ids
```

is allowed for O6 corroboration.

Removal/replacement of prior evidence IDs is rejected by this bounded repair.

### Non-ownership

This module does not:

- create Integration records;
- decide evidence truth;
- mutate the current snapshot;
- perform migration;
- emit current lifecycle routing decisions.

---

## 7. Module: `transition.py`

### Purpose

Provide one transition-validation composition boundary for CLI, transaction code, and CI.

Current `cli.py` imports `validate_v05_transition` directly. P14 requires a single Historical Transition Guard boundary, so P15 introduces a version-dispatched composition module rather than making every caller know version-specific transition files.

### Stable entrypoint

Conceptually:

```python
def validate_transition(
    previous: ManifestSet,
    current: ManifestSet,
) -> list[str]:
    ...
```

### Composition rules

For current v0.5 -> v0.5:

```text
transition.py
  -> transition_v05.validate_v05_transition
```

with existing v0.5 behavior preserved.

For a future accepted replacement version -> same replacement version:

```text
transition.py
  -> target-version Gate/Authority transition validator
  -> integration_history.validate_integration_history
```

Cross-version migration is not silently treated as an ordinary same-version transition. It must use the migration transaction path.

### Why this module is needed

Without this boundary, `cli.py`, CI helpers, and transaction logic would each need to know which version-specific transition validators to invoke, creating multiple enforcement paths.

### Non-ownership

`transition.py` dispatches/composes validators only. It contains no schema semantics and no mutation logic.

---

## 8. Module: `transition_v05.py`

### Preservation rule

Existing v0.5 transition behavior remains historical compatibility code.

It continues to own v0.5:

- immutable Gate Contracts;
- immutable Gate Decisions.

P15 does not retrofit Absent semantics into v0.5.

A v0.5 manifest remains a v0.5 manifest and cannot contain an Absent Integration binding.

### Allowed future refactor

Common helper extraction is allowed only if behavior remains byte-for-byte equivalent from the perspective of v0.5 validation outcomes.

---

## 9. Module: `compute.py`

### Preserve current responsibility

`compute.py` remains the State Projection Engine.

It should consume binding semantics through `integration_binding.py` instead of reading `gate_decision_id` directly whenever conformance semantics are involved.

### Required projection logic

Conceptually:

```text
Bound(PASS/PASS_WITH_FINDINGS)
-> conforming

Bound(BLOCKED_*)
-> nonconforming

Absent(no_applicable_integration_gate_decision)
-> nonconforming
```

### Required historical distinction

The generated read model must retain enough information for consumers/tests to distinguish:

```text
nonconforming because Bound(BLOCKED)
```

from:

```text
nonconforming because Absent
```

P15 does not assign replacement-version serialized field names where P12 has not already done so.

The internal projection path must nonetheless preserve the variant explicitly rather than collapsing both cases before serialization.

### Actionability invariant

`compute.py` must not create a synthetic Gate, Gate Decision, or current Gate blocker for Absent.

### Non-ownership

No authored manifest mutation occurs in `compute.py`.

---

## 10. Module: `transaction.py`

### Purpose

Own the only Project State write/commit boundary for mutation and migration workflows introduced by this repair.

### Candidate type

Conceptually:

```python
@dataclass(frozen=True)
class ProjectStateCandidate:
    manifests: ManifestSet
    state: dict
```

Additional rendering metadata may be included, but the candidate must represent a complete authored + generated state set.

### Operation transaction entrypoint

Conceptually:

```python
def prepare_operation_transaction(
    previous: ManifestSet,
    operation: IntegrationOperation,
) -> ProjectStateCandidate:
    ...
```

Required pipeline:

```text
previous
-> integration_ops.apply_integration_operation
-> validate_manifests(current)
-> validate_transition(previous, current)
-> compute_state(current)
-> ProjectStateCandidate
```

Any error produces no candidate.

### Migration transaction entrypoint

Conceptually:

```python
def prepare_migration_transaction(
    source: ManifestSet,
    migration_transform,
) -> ProjectStateCandidate:
    ...
```

Required pipeline:

```text
validate source
-> deterministic transform
-> validate destination
-> migration equivalence checks
-> compute destination state
-> ProjectStateCandidate
```

The exact migration equivalence oracle is downstream Verification territory where not already fixed by Authority.

### Persistence entrypoint

There must be exactly one module-level persistence boundary for a prepared candidate.

Conceptually:

```python
def commit_candidate(root: Path, candidate: ProjectStateCandidate) -> None:
    ...
```

The temporal staging/swap algorithm belongs to P16 Runtime Data Flow, but callers must not write individual `.aegis/*.json` files directly around this boundary.

### Non-ownership

`transaction.py` does not decide:

- whether Absent is true;
- whether evidence is sufficient;
- what the current lifecycle stage is.

It enforces composition and all-or-nothing commit behavior only.

---

## 11. Module: `migrate_v05.py`

### Preservation rule

Existing v0.4 -> v0.5 migration remains unchanged in semantics.

It is not repurposed for the new repair.

### Future replacement migration module

After a replacement Project State version is formally assigned, a target-version-specific migration module may be added using the existing naming pattern.

P15 intentionally does not name that file because no replacement version is Current or accepted yet.

Its required transform for v0.5 Integration records is already fixed by P12/P13:

```yaml
gate_decision_id: D
```

losslessly becomes semantically equivalent to:

```yaml
gate_decision_binding:
  kind: bound
  gate_decision_id: D
```

It must not add PR #82 or infer any Absent record.

### Module dependency

Future migration code may use `integration_binding.py` helpers for canonical comparison but must not call `integration_ops.py` to perform historical reconciliation.

```text
migration != reconciliation
```

remains a hard module boundary.

---

## 12. Module: `cli.py`

### Preserve current commands

Existing read/check surfaces remain:

```text
validate
recompute
check
transition-check
migrate-v05
```

### Required internal change

`transition-check` should depend on `transition.validate_transition` rather than importing one version-specific validator directly.

### Future operation surface

If a reconciliation/mutation CLI command is introduced, it must be a thin adapter that:

1. parses an explicit operation payload;
2. loads manifests;
3. calls `transaction.prepare_operation_transaction`;
4. optionally calls `transaction.commit_candidate`;
5. renders deterministic diagnostics.

The CLI must never:

- inspect GitHub to discover absence;
- guess a Gate Decision;
- construct Absent from a missing field;
- write `integrations.json` independently;
- bypass transition checks.

Exact end-user command naming belongs to P17 Platform Contract unless needed sooner by an accepted implementation package.

---

## 13. Schema modules

### Current v0.5 schemas

The following remain historical v0.5 contracts and are not modified by this design stage:

```text
schemas/project-state/v0.5/*.schema.json
```

In particular, v0.5 `integrations.schema.json` continues to require `gate_decision_id`.

### Future replacement schema

Only after a replacement version is assigned may a new schema directory materialize.

The target `integrations.schema.json` must encode the P12 variant contract:

```text
Bound
or
Absent(no_applicable_integration_gate_decision)
```

with status-dependent validity.

The target generated-state schema must preserve the distinction between Bound(BLOCKED) and Absent historical nonconformance.

P15 does not mutate or reinterpret v0.5 schema files in place.

---

## 14. Dependency DAG

The intended dependency direction is:

```text
integration_binding
       ↑
       ├──────────── model
       │              ↑
       │              ├──────── integration_ops
       │              ├──────── integration_history
       │              ├──────── compute
       │              └──────── migration modules
       │
transition_v05 ──────┐
integration_history ─┼─> transition
                     │
integration_ops ─────┐
model ───────────────┼─> transaction
transition ──────────┤
compute ─────────────┘

model / compute / transition / transaction / migrations
                     ↓
                    cli
```

Forbidden dependency directions:

```text
integration_binding -> model
model -> transaction
compute -> transaction
transition -> transaction
integration_ops -> cli
core modules -> GitHub/network clients
```

This keeps the domain core deterministic and testable.

---

## 15. Failure ownership

Each diagnostic class has one primary module owner.

```text
DANGLING_BOUND_DECISION
AWAITING_INTEGRATION_CANNOT_BE_ABSENT
invalid Absent reason
-> model / integration_binding

MISSING_OCCURRENCE_EVIDENCE
ABSENCE_NOT_PROVEN input missing
AMBIGUOUS_GATE_DECISION_BINDING request
HISTORICAL_INTEGRATION_ID_CONFLICT
-> integration_ops

IMMUTABLE_INTEGRATION_BINDING_CHANGED
INTEGRATED_REVISION_CHANGED
integrated occurrence removed
historical evidence removed
-> integration_history / transition

NONDETERMINISTIC_REPLAY
transaction composition mismatch
partial candidate impossible
-> transaction + downstream verification oracle
```

`ABSENCE_NOT_PROVEN` here means the operation request does not contain the required qualified absence basis. Whether supplied evidence is substantively sufficient is a P20 question.

---

## 16. Testing module map

P15 requires focused unit ownership rather than one large end-to-end test file.

### Existing tests to preserve

All existing Project State tests remain regression coverage, especially:

```text
test_gate_decision_lineage_v05.py
test_gate_decision_transition_v05.py
test_gate_decision_transition_cli_v05.py
test_migration_v05.py
```

The repair must not change v0.5 expected behavior.

### New version-neutral domain tests

Recommended exact files:

```text
tests/project_state/test_integration_binding.py
tests/project_state/test_integration_ops.py
tests/project_state/test_integration_history.py
tests/project_state/test_integration_projection.py
tests/project_state/test_transaction.py
```

Responsibilities:

#### `test_integration_binding.py`

- legacy v0.5 `gate_decision_id` normalizes to Bound;
- explicit Bound validates;
- explicit Absent validates only for integrated;
- missing data never becomes Absent;
- unknown Absent reason rejects.

#### `test_integration_ops.py`

- O1–O6 legal transitions;
- O4 Absent requires occurrence + absence bases;
- idempotent replay;
- conflicting same-ID replay rejects;
- no operation mutates input snapshot.

#### `test_integration_history.py`

- integrated record removal rejects;
- Bound -> Bound different rejects;
- Bound <-> Absent rejects;
- integrated revision change rejects;
- evidence append allowed;
- evidence removal rejects.

#### `test_integration_projection.py`

- Bound PASS -> conforming;
- Bound BLOCKED -> nonconforming;
- Absent -> nonconforming;
- Absent does not synthesize a current Gate blocker;
- Bound(BLOCKED) and Absent remain distinguishable.

#### `test_transaction.py`

- invalid operation creates no candidate;
- snapshot validation failure aborts;
- transition failure aborts;
- projection failure aborts;
- valid operation yields complete authored + generated candidate;
- commit boundary is the only write path tested for state-changing operations.

### Future version-specific tests

After replacement-version assignment:

```text
migration test for v0.5 -> replacement
schema parsing/validation for replacement
example project validation/check
root self-host reconciliation coverage
```

Exact version suffixes are deferred until the version exists.

---

## 17. Test helper boundary

`tests/project_state/helpers.py` may gain reusable builders for:

```text
Bound integration
Absent integrated occurrence
qualified evidence records
previous/current snapshot pairs
```

But test helpers must not hide the critical distinction between occurrence basis and absence basis.

Tests must make those inputs visible at call sites for O4 so accidental inference is obvious.

---

## 18. CI module boundary

`.github/workflows/project-state.yml` remains an adapter, not a semantic implementation.

It should continue to invoke the Python core for:

```text
snapshot validation
state check
transition validation
unit regressions
```

When the replacement version and implementation exist, CI may add target-version schema parsing and new tests, but must not encode Bound/Absent rules in shell expressions.

```text
CI YAML -> invoke core
CI YAML != second validator
```

---

## 19. Example/fixture boundary

A future accepted replacement version should include at least two fixture classes:

```text
minimal conforming Bound example
historical Absent integration example
```

The Absent fixture must demonstrate:

```text
real integrated_revision
explicit Absent reason
nonconforming historical projection
no synthetic current Gate blocker
```

PR #82 may be used as root self-host evidence, but generic fixtures should not require access to live GitHub.

---

## 20. No-network core invariant

All modules under `tools/aegis_state` defined by this repair remain deterministic local logic.

They receive durable IDs/refs as data.

They do not fetch:

- GitHub PRs;
- comments;
- workflow runs;
- remote Authority documents.

External evidence collection belongs outside the Project State core.

This ensures:

```text
same authored inputs + same operation request
-> same candidate result
```

and makes CI/local behavior equivalent.

---

## 21. Versioning boundary

P15 does not create or imply `v0.6` or any other replacement version.

Version-dependent names are deferred where naming would assert Authority that does not yet exist.

What is fixed now is the module contract, not the replacement-version identifier.

Existing v0.5 modules and schemas remain valid historical artifacts.

---

## 22. Minimal implementation surface implied by P15

Subject to downstream Authority/Verification, the likely bounded implementation surface is:

### New Python modules

```text
tools/aegis_state/integration_binding.py
tools/aegis_state/integration_ops.py
tools/aegis_state/integration_history.py
tools/aegis_state/transition.py
tools/aegis_state/transaction.py
```

### Existing Python modules to extend

```text
tools/aegis_state/model.py
tools/aegis_state/compute.py
tools/aegis_state/cli.py
```

### Existing modules preserved semantically

```text
tools/aegis_state/transition_v05.py
tools/aegis_state/migrate_v05.py
```

### New tests

```text
tests/project_state/test_integration_binding.py
tests/project_state/test_integration_ops.py
tests/project_state/test_integration_history.py
tests/project_state/test_integration_projection.py
tests/project_state/test_transaction.py
```

### Deferred until replacement-version Authority exists

```text
new schemas/project-state/<replacement-version>/
new target migration module
replacement-version examples
version-specific migration/schema tests
root .aegis persistence changes
```

---

## 23. P15 acceptance criteria

P15 is complete when:

1. Binding semantics have one reusable domain owner.
2. Single-snapshot validation remains in `model.py`.
3. P13 O1–O6 have one pure in-memory operation owner.
4. Historical Integration immutability has one reusable cross-snapshot owner.
5. Existing v0.5 transition code remains valid and un-reinterpreted.
6. Transition callers use one composition boundary.
7. Projection remains in `compute.py` and cannot synthesize Gate truth from Absent.
8. Migration remains separate from reconciliation.
9. State-changing workflows use one transaction boundary.
10. CLI and CI remain adapters over the same core.
11. No new module performs network evidence discovery.
12. Test ownership maps directly to module ownership.
13. No replacement Project State version is invented.
14. No `.aegis/*` persistence is performed during design.

P15 disposition for this candidate:

```yaml
p15_module_design:
  scope: aegis/project-state
  finding: P22-F2
  basis:
    p12: 777e1e8a9652e2cbf220d234798641d65dc9b0c9
    p13: b742ebb9f27520a595b2e73370f42157e28ea72e
    p14: 21d6dd535dc7ab50898f7294e73c4bdd98757fc5

  new_modules:
    - integration_binding.py
    - integration_ops.py
    - integration_history.py
    - transition.py
    - transaction.py

  extend_modules:
    - model.py
    - compute.py
    - cli.py

  preserve_modules:
    - transition_v05.py
    - migrate_v05.py

  migration_reconciliation_separated: true
  no_network_core: true
  v05_reinterpreted: false
  replacement_version_assigned: false
  aegis_persistence_performed: false
  status: READY_FOR_P16_RUNTIME_DATA_FLOW
```

---

## 24. Downstream handoff boundary

P15 defines module responsibilities and stable composition interfaces, but not the temporal execution protocol.

The next architecture stage is:

```text
aegis-architecture -> P16 Runtime Data Flow
```

P16 should trace, in order:

- normal future `awaiting -> integrated Bound` flow;
- occurrence-time `awaiting -> integrated Absent` flow;
- PR #82 O4 historical reconciliation flow;
- failed/ambiguous absence flow;
- transaction staging/validation/projection/commit flow;
- retry/idempotent replay flow;
- migration flow kept separate from reconciliation;
- CI transition-check flow.

P16 must name the owning module at every state transition and preserve the no-network Project State core boundary.
