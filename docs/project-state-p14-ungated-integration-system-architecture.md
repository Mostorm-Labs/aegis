# Aegis Project State — P14 Ungated Integration System Architecture

Status: **P14 System Architecture Candidate**

Scope: `aegis/project-state`

Triggering finding: `P22-F2 = MISSING_CONTRACT / SPEC_DEFECT`

Repository basis: `main@3a2607220cd875dc66857b334dcfbd2c763e7c7d`

P12 semantic basis candidate: `777e1e8a9652e2cbf220d234798641d65dc9b0c9`

P13 operation basis candidate: `b742ebb9f27520a595b2e73370f42157e28ea72e`

Current Authority under repair: `aegis-project-state-v0.5`

This artifact defines the bounded subsystem architecture required to realize the P12/P13 Project State repair. It does not assign a replacement schema version, does not modify `.aegis/*`, does not create a new Current Authority, and does not authorize implementation, repository integration, release, or rollout.

---

## 1. Architectural objective

The system must support one additional truthful historical Integration state:

```text
integrated occurrence
+
explicitly confirmed absence of an applicable Integration Gate Decision
```

while preserving these existing boundaries:

```text
Gate Contract
!= Gate Review Decision
!= Current Gate Decision
!= Integration-bound Gate Decision

Integration Occurrence
!= Gate Conformance
!= Current Applicability
!= Current Actionability
```

The architecture must also enforce P13's central historical rule:

```text
prospective Integration binding may change before occurrence
historical Integration binding becomes immutable after occurrence
```

No subsystem may infer `Absent` from lookup failure, missing persistence, missing `gate_decision_id`, or current Gate state.

---

## 2. Current repository architecture to preserve

Current Project State tooling already has a useful separation of concerns:

```text
schemas/project-state/*
        ↓
tools/aegis_state/model.py
        ↓
  single-snapshot validation

previous snapshot + current snapshot
        ↓
tools/aegis_state/transition_v05.py
        ↓
  cross-snapshot historical validation

valid authored manifests
        ↓
tools/aegis_state/compute.py
        ↓
  generated state projection

schema migration request
        ↓
tools/aegis_state/migrate_v05.py
        ↓
  deterministic version transform

user / CI
        ↓
tools/aegis_state/cli.py
        ↓
  orchestration surface

GitHub Actions
        ↓
.github/workflows/project-state.yml
        ↓
  independent enforcement
```

P14 preserves this architecture direction. The repair must extend the existing Project State engine rather than introduce a second parallel state engine.

---

## 3. Subsystem map

The repaired architecture consists of seven logical subsystems.

```text
                 External Governance / Repository Evidence
                              │
                              │ durable refs / qualified basis
                              ▼
                    ┌─────────────────────┐
                    │  Reconciliation /   │
                    │  Mutation Service   │
                    └─────────┬───────────┘
                              │ candidate authored manifests
                              ▼
┌───────────────────┐  ┌─────────────────────┐
│ Version Migration │  │ Manifest Domain /   │
│ Service           │→ │ Snapshot Validation │
└───────────────────┘  └─────────┬───────────┘
                                 │
                   previous ─────┼───── current
                                 ▼
                    ┌─────────────────────┐
                    │ Historical          │
                    │ Transition Guard    │
                    └─────────┬───────────┘
                              │ valid transition
                              ▼
                    ┌─────────────────────┐
                    │ State Projection    │
                    │ Engine              │
                    └─────────┬───────────┘
                              │ authored + generated candidate
                              ▼
                    ┌─────────────────────┐
                    │ Manifest Transaction│
                    │ Boundary            │
                    └─────────┬───────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
          CLI / Tool Adapter          CI Enforcement
```

The subsystem names are architectural roles, not required Python filenames. Exact module decomposition belongs to P15.

---

## 4. Subsystem A — Manifest Domain / Snapshot Validation

### Ownership

Owns the canonical authored-manifest model and all rules that can be validated from one Project State snapshot.

Current repository realization is primarily:

```text
schemas/project-state/<version>/*.schema.json
tools/aegis_state/model.py
```

### Must own

- schema-version consistency;
- Integration record structural shape;
- `Gate Decision Binding` variant validation;
- `Bound` decision reference existence;
- `Absent` reason vocabulary validation;
- status-specific binding constraints:
  - `awaiting_integration -> Bound only`;
  - `integrated -> Bound | Absent`;
  - `closed_unmerged -> Bound only`;
- evidence reference integrity;
- Gate / Authority / Decision cross-reference integrity;
- ordinary per-snapshot generated-state prerequisites.

### Must not own

- deciding whether a historical Gate Decision was actually applicable at occurrence time;
- proving that no applicable Gate Decision existed;
- inferring `Absent` from missing data;
- comparing historical identity across revisions;
- executing persistence mutations;
- deciding release readiness.

### Failure domain

A malformed or internally inconsistent candidate snapshot fails locally before projection or persistence.

```text
invalid snapshot
-> no authored-state mutation
```

---

## 5. Subsystem B — Historical Transition Guard

### Ownership

Owns cross-snapshot immutability and append-only historical constraints.

Current repository realization is `tools/aegis_state/transition_v05.py`, which already protects Gate Contract / Gate Decision history. The repair extends this architectural role to Integration historical identity.

### Must own

For every already-finalized `integrated` record, compare previous and current snapshots and reject mutation of:

```text
id
kind
ref
target_ref
integrated_revision
gate_decision_binding
```

It must therefore reject:

```text
Bound(D1) -> Bound(D2)
Bound(D)  -> Absent
Absent    -> Bound(D)
Absent(reason1) -> Absent(reason2)
integrated -> awaiting_integration
integrated -> closed_unmerged
```

It also owns P13 O6 append-only evidence protection: later corroborating evidence may be appended without changing immutable historical meaning; evidence replacement/removal must not silently rewrite the occurrence basis.

### Relationship to existing Gate Decision immutability

Gate Decision transition validation and Integration transition validation belong to the same architectural **Historical Transition Guard** because both answer the same question:

> did a later Project State snapshot rewrite an already-finalized governance/history fact?

They may be separate modules at P15, but they must share one transition-enforcement boundary.

### Must not own

- creation of `Absent`;
- reconciliation planning;
- migration;
- projection;
- external evidence retrieval;
- historical correction/supersession semantics not defined by P13.

### Failure domain

A historical mutation conflict blocks the transition as an Authority/history integrity failure. The guard never repairs the current snapshot in place.

---

## 6. Subsystem C — Reconciliation / Mutation Service

### Ownership

Owns application of P13's logical operations to an in-memory authored manifest set.

It is the sole domain subsystem allowed to *construct* a new Integration historical binding from an authorized operation request.

### Logical operations owned

```text
O1 Register Awaiting Integration
O2 Rebind Awaiting Integration
O3 Finalize Integration Occurrence
O4 Reconcile Historical Integration Occurrence
O5 Close Unmerged Candidate
O6 Append Corroborating Integration Evidence
```

### `Absent` creation boundary

For O3/O4 producing `Absent`, the service requires explicit inputs equivalent to:

```text
Occurrence Basis
+
Absence Basis
```

It must receive those as durable references / already-qualified governance inputs.

The service must **not** call GitHub, scan comments, search Gate registries, or use absence of a record to decide that `Absent` is true.

Conceptually:

```text
qualified request:
  integration identity
  exact occurrence revision
  occurrence basis refs
  binding = Absent
  absence basis refs

        ↓
Reconciliation Service
        ↓
validate request shape and references
        ↓
construct candidate manifest transaction
```

The truth judgment that the supplied basis is sufficient belongs to governance/verification Authority, not to this service.

### Idempotency ownership

The service owns P13's stable-ID replay behavior:

```text
same Integration.id + same immutable payload
-> deterministic no-op

same Integration.id + different immutable payload
-> HISTORICAL_INTEGRATION_ID_CONFLICT
```

### Must not own

- Authority review;
- evidence sufficiency policy;
- external repository truth discovery;
- direct file writes;
- state projection;
- schema-version migration.

### Failure domain

Insufficient, ambiguous, or contradictory operation inputs produce no candidate mutation.

---

## 7. Subsystem D — Version Migration Service

### Ownership

Owns deterministic schema-version transformation only.

Existing repository realization is `tools/aegis_state/migrate_v05.py` for the prior transition pattern.

### Required bounded behavior

When a replacement Project State version is eventually assigned, migration from v0.5 must losslessly map every existing legacy Integration:

```yaml
gate_decision_id: D
```

into semantic equivalent:

```yaml
gate_decision_binding:
  kind: bound
  gate_decision_id: D
```

### Critical non-ownership

Migration must **not** create PR #82 or any other missing historical occurrence.

```text
version migration
!= historical reconciliation
```

Migration transforms records that exist. O4 Reconciliation adds a proven repository occurrence that was absent from persistence.

Migration also must not infer `Absent` for any legacy record.

### Required sequencing

```text
validate source
-> transform deterministically
-> validate destination snapshot
-> validate migration equivalence/invariants
-> only then allow transaction output
```

### Failure domain

Non-equivalent or invalid source state produces no destination mutation.

---

## 8. Subsystem E — State Projection Engine

### Ownership

Owns all generated/read-model projections derived from valid authored manifests.

Current repository realization is `tools/aegis_state/compute.py`.

### New required projection behavior

For `integrated` records:

```text
Bound(PASS/PASS_WITH_FINDINGS)
-> conformance = conforming

Bound(BLOCKED_*)
-> conformance = nonconforming

Absent(no_applicable_integration_gate_decision)
-> conformance = nonconforming
```

For `Absent`, generated state must preserve enough derived information to distinguish the absence case from a bound BLOCKED case. Exact generated-state field shape belongs to P15/P20, but the architecture must not collapse the two histories into an indistinguishable internal path.

### Actionability rule

The Projection Engine must not synthesize a Gate Contract, Gate Decision, or current blocked Gate from an `Absent` binding.

`Absent` describes historical conformance, not a fictional current Gate verdict.

### Must not own

- authored-manifest mutation;
- historical binding resolution;
- external evidence retrieval;
- transition immutability;
- Authority decisions.

`state.json` remains a reproducible cache/read model.

### Failure domain

If projection cannot be produced deterministically from a valid authored snapshot, the candidate state is not persistable as complete Project State.

---

## 9. Subsystem F — Manifest Transaction Boundary

### Ownership

Owns the single commit boundary for authored Project State changes plus regenerated state.

This is an architectural boundary, not necessarily a standalone module.

### Why it is required

P13 requires O3/O4 to be atomic over:

- Integration record;
- exact integrated revision;
- occurrence evidence refs;
- governance/absence basis refs for `Absent`;
- referenced Gate Decision for `Bound`;
- regenerated state.

Therefore individual domain components must not independently write separate `.aegis/*.json` files and leave partially valid state behind.

### Transaction pipeline

```text
previous authored snapshot
+
operation/migration request
        ↓
build complete candidate authored snapshot
        ↓
Snapshot Validation
        ↓
Historical Transition Guard
        ↓
State Projection
        ↓
complete candidate Project State
        ↓
transaction commit boundary
```

If any step fails:

```text
commit nothing
```

### Important distinction

Authored manifests are canonical control state. `state.json` is generated output. The transaction boundary must never use a prewritten `state.json` to legitimize invalid authored manifests.

### Must not own

- domain semantics;
- evidence judgment;
- repair routing.

---

## 10. Subsystem G — CLI / Tool Adapter

### Ownership

Owns human/automation entrypoints and error rendering only.

Current repository realization is `tools/aegis_state/cli.py`.

The existing design already exposes:

```text
validate
recompute
check
transition-check
migrate-v05
```

The repaired architecture may add operation/reconciliation surfaces, but CLI commands must remain thin adapters over domain services.

### CLI must not

- implement a second copy of binding semantics;
- infer `Absent`;
- decide evidence sufficiency;
- bypass Historical Transition Guard;
- mutate files piecemeal;
- make current Gate decisions.

### Diagnostic ownership

CLI translates domain failures into fail-closed diagnostics. Lifecycle routing labels may be surfaced, but the CLI does not become governance Authority by printing them.

---

## 11. CI Enforcement Adapter

### Ownership

Owns independent repository enforcement by invoking the same deterministic Project State core used locally.

Current repository realization is `.github/workflows/project-state.yml`.

The current workflow already enforces:

- schema parsing;
- single-snapshot validate/check;
- unit regressions;
- cross-snapshot v0.5 transition checking on PRs and pushes;
- root self-host validation.

The repaired architecture extends this same enforcement plane rather than creating a separate CI-only rules engine.

### Required enforcement classes

Once implementation exists, CI must be able to independently exercise:

```text
1. candidate snapshot validity
2. generated-state reproducibility
3. Gate Decision historical immutability
4. Integration historical immutability
5. legal prospective rebind behavior
6. legal Bound -> finalized Bound occurrence
7. legal occurrence-time finalization to Absent when explicit basis is supplied
8. rejection of implicit/missing-data Absent
9. deterministic migration equivalence
10. PR #82 historical reconciliation fixture
11. PR #9 historical Bound(BLOCKED) preservation
```

Exact tests/oracles are P20 verification-design work; P14 only assigns enforcement responsibility.

### CI must not

- fabricate an absence basis from GitHub search results;
- auto-reconcile root `.aegis` merely because tests pass;
- publish Authority;
- perform release actions.

---

## 12. External evidence / governance boundary

Repository/GitHub reality and governance reviews remain external inputs to the Project State deterministic core.

Conceptually:

```text
GitHub merge evidence
Governance durable review
Gate reviews
Authority decisions
        │
        │ durable refs / authored Evidence records
        ▼
Project State operation request
```

The Project State core validates that required references are present and structurally consistent. It does not turn external lookup success/failure into governance truth.

For PR #82 specifically:

```text
Occurrence Basis:
  real merge at 3a260722...

Absence Basis:
  P22-F2 durable review 5553423707
```

A future P20 contract must define exactly what evidence/oracle proves those bases sufficiently. P14 does not preempt that verification design.

---

## 13. Dependency direction

Allowed dependency direction is:

```text
CLI / CI adapters
        ↓
Application operation surfaces
        ↓
Reconciliation Service / Migration Service
        ↓
Manifest Domain Validation
        ↓
Historical Transition Guard
        ↓
State Projection
        ↓
Transaction Boundary
```

More precisely, the transaction orchestrator may call validation, transition guard, and projection as sibling pure services. The important invariant is that lower-level domain services do not call outward into CLI, CI, GitHub, or governance systems.

Forbidden dependency directions include:

```text
model/validator -> GitHub
transition guard -> reconciliation service
compute/projection -> mutation service
migration -> external governance lookup
CI workflow -> bespoke semantic implementation
state.json -> authored manifest authority
```

---

## 14. Process / runtime boundary

No new daemon, database service, network service, or asynchronous control plane is required by P22-F2.

The repair remains compatible with the current deterministic local/CI execution model:

```text
Python process
reads Project State snapshot(s)
performs pure validation/transformation/projection
writes only through explicit transaction boundary
exits with deterministic result
```

GitHub Actions is an execution host, not a semantic owner.

This keeps Project State portable and testable and avoids coupling historical truth to one hosted provider.

---

## 15. Failure-domain matrix

| Failure | Owning subsystem | Required behavior |
| --- | --- | --- |
| malformed Binding shape | Manifest Domain Validation | reject snapshot |
| dangling Bound decision | Manifest Domain Validation | reject snapshot |
| `Absent` on awaiting candidate | Manifest Domain Validation | reject snapshot |
| absence basis missing/ambiguous during O3/O4 | Reconciliation Service | produce no mutation |
| integrated binding changed across snapshots | Historical Transition Guard | block transition |
| integrated revision changed | Historical Transition Guard | block transition |
| evidence removed/replaced from finalized occurrence | Historical Transition Guard | block transition unless future Authority defines correction lineage |
| same Integration ID, conflicting immutable payload | Reconciliation Service / Transition Guard | fail closed |
| migration cannot preserve v0.5 meaning | Migration Service | produce no destination |
| generated state differs from deterministic projection | State Projection / check surface | state drift failure |
| CI observes any above | CI Adapter | fail job; never auto-repair |

No failure path is allowed to synthesize a Gate Decision or silently convert an unknown state into `Absent`.

---

## 16. Existing-module alignment

P14 deliberately maximizes reuse of current repository architecture.

| Architectural responsibility | Existing basis | P14 direction |
| --- | --- | --- |
| Manifest Domain / snapshot validation | `schemas/project-state/**`, `model.py` | extend binding variants and invariants |
| Historical Transition Guard | `transition_v05.py` | extend/generalize to Integration immutable history |
| State Projection | `compute.py` | derive `Absent -> nonconforming` without synthetic Gate |
| Version Migration | `migrate_v05.py` pattern | add deterministic v0.5 -> replacement transform when version is assigned |
| CLI Adapter | `cli.py` | thin orchestration only |
| CI Adapter | `project-state.yml` | invoke same core for transition/reconciliation/migration evidence |
| Reconciliation / Mutation Service | no dedicated current subsystem | introduce bounded domain service |
| Manifest Transaction Boundary | currently implicit/command-specific | establish one explicit authored-state commit boundary |

This is an architectural extension, not a rewrite.

---

## 17. Explicit non-goals

P14 does not:

- name a replacement Project State version;
- choose final JSON property names beyond inherited P12 semantics;
- define exact Python classes/functions/files for each subsystem;
- define P20 proof thresholds or fixture corpus;
- implement tooling;
- mutate `.aegis/*`;
- reconcile PR #81 or PR #82 now;
- regenerate root `state.json`;
- create a synthetic Gate for PR #82;
- create a historical correction lineage;
- redesign all Project State persistence;
- change Product Authority;
- authorize release or rollout.

---

## 18. Architecture invariants

The repaired implementation must preserve all of the following:

```text
A1. One Project State semantic engine; no CLI/CI duplicate rules.
A2. Snapshot validation never infers historical absence.
A3. Reconciliation is the only operation path that can create missing historical occurrences.
A4. `Absent` requires explicit qualified absence basis input.
A5. Historical Transition Guard independently prevents retroactive rebinding.
A6. Migration never performs historical reconciliation.
A7. Projection never mutates authored state.
A8. `state.json` never outranks authored manifests or repository/governance truth.
A9. All authored changes cross one atomic transaction boundary.
A10. CI invokes the same deterministic core as local tooling.
A11. No hosted provider is required to interpret canonical Project State semantics.
A12. PR #9 Bound(BLOCKED) history and PR #82 Absent history remain semantically distinct.
```

---

## 19. P14 acceptance result

```yaml
p14_system_architecture:
  scope: aegis/project-state
  finding: P22-F2

  semantic_basis:
    p12: 777e1e8a9652e2cbf220d234798641d65dc9b0c9

  operation_basis:
    p13: b742ebb9f27520a595b2e73370f42157e28ea72e

  architecture_style:
    deterministic_single_process_control_state_engine

  subsystems:
    - manifest_domain_validation
    - historical_transition_guard
    - reconciliation_mutation_service
    - version_migration_service
    - state_projection_engine
    - manifest_transaction_boundary
    - cli_ci_adapters

  new_major_subsystem_required:
    reconciliation_mutation_service: true
    second_state_engine: false
    network_service: false
    database_service: false

  historical_binding_owner:
    creation: reconciliation_mutation_service
    single_snapshot_validation: manifest_domain_validation
    cross_snapshot_immutability: historical_transition_guard
    derived_conformance: state_projection_engine
    persistence_commit: manifest_transaction_boundary

  migration_may_create_absent: false
  projection_may_infer_absent: false
  cli_ci_may_infer_absent: false
  repository_lookup_failure_means_absent: false

  current_authority_changed: false
  replacement_version_assigned: false
  project_state_persistence_authorized: false
  implementation_authorized: false
  release_authorized: false

  verdict: READY
  disposition: READY_FOR_P15_MODULE_DESIGN
```

---

## 20. Downstream boundary

P14 establishes subsystem ownership and dependency direction. The next architecture stage, only after an explicit user turn, is:

```text
aegis-architecture -> P15 Module Design
```

P15 should freeze the concrete module/API boundaries for:

- Gate Decision Binding representation and validation;
- Integration transition comparison;
- reconciliation operation request/result types;
- transaction orchestration;
- migration adapter;
- projection output for Absent historical nonconformance;
- CLI command surfaces;
- CI invocation boundaries.

P14 does not execute P15 automatically.
