# Aegis Project State — P14 Plugin-Native Targeted Repair

Status: **P14 System Architecture Replacement Candidate**

Scope: `aegis/project-state`

Triggering finding: `P22-F2 = MISSING_CONTRACT / SPEC_DEFECT`

Repository basis: `main@3a2607220cd875dc66857b334dcfbd2c763e7c7d`

P12 semantic basis candidate: `777e1e8a9652e2cbf220d234798641d65dc9b0c9`

P13 operation basis candidate: `b742ebb9f27520a595b2e73370f42157e28ea72e`

Prior P14 candidate being replaced as downstream design basis: `21d6dd535dc7ab50898f7294e73c4bdd98757fc5`

Prior P15 candidate invalidated by that architectural assumption: `a0eb5ea562af580f21e4d8c6e01d77266c738c0d`

Current Authority under repair: `aegis-project-state-v0.5`

This artifact performs a targeted P14 repair only. It preserves P12/P13 semantics, removes the runtime/harness interpretation introduced by the prior P14/P15 candidates, and reasserts Aegis as a ChatGPT Plugin/Skills control plane. It does not assign a replacement Project State version, does not modify `.aegis/*`, does not create a new Current Authority, and does not authorize implementation, merge, release, or rollout.

---

## 1. Repair reason

The prior P14/P15 candidates correctly preserved several semantic boundaries, but they over-materialized those rules into an internal execution architecture:

```text
Reconciliation / Mutation Service
Manifest Transaction Boundary
operation execution modules
transition dispatch modules
runtime-oriented state machinery
```

That is the wrong product-form assumption for Aegis.

Aegis is not intended to become:

```text
an agent runtime
a daemon
a repository-side orchestration harness
a background reconciliation service
a custom state service
a local execution loop
```

The product form is instead:

```text
ChatGPT Aegis Plugin / Skills
        ↓
reason over Authority + durable evidence
        ↓
produce explicit control decisions / mutations / handoffs
        ↓
use existing connected execution surfaces
        ↓
repository durable state
```

The targeted repair therefore separates **control-plane reasoning** from **optional deterministic repository validation**.

---

## 2. Product-form invariant

The following is a P14 architectural invariant for this repair line:

```yaml
product_form:
  type: ChatGPT Plugin / Skills

control_plane:
  owner: Aegis Skills

execution_plane:
  external_surfaces:
    - GitHub connector
    - Codex
    - other explicitly connected tools

forbidden_internal_product_forms:
  - aegis_daemon
  - autonomous_agent_runtime
  - custom_harness
  - background_reconciler
  - internal_execution_loop
  - repository_state_service
  - transaction_server
```

Aegis may invoke connected tools when authorized by the lifecycle and user intent. That does not turn Aegis itself into an execution runtime.

---

## 3. Corrected system architecture

The repaired P14 architecture contains four layers only:

```text
┌──────────────────────────────────────────────┐
│ A. Aegis Plugin / Skill Control Plane        │
│                                              │
│ - interpret Current Authority                │
│ - apply P12/P13 semantics                    │
│ - distinguish occurrence / conformance       │
│ - determine legal Project State mutation     │
│ - fail closed on ambiguity                   │
│ - produce explicit handoff / repository edit │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ B. Existing Connected Execution Surfaces     │
│                                              │
│ GitHub / Codex / approved tool surface       │
│                                              │
│ - read durable evidence                      │
│ - write explicit repository change           │
│ - commit/push only when lifecycle authorizes │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ C. Durable Repository Control State          │
│                                              │
│ .aegis/*.json                                │
│ docs / Authority artifacts / durable refs    │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ D. Optional Deterministic Validation         │
│                                              │
│ JSON Schema / existing Python validator / CI │
│                                              │
│ - validate shape / invariants                │
│ - recompute generated state                  │
│ - detect drift / immutable-history violation │
└──────────────────────────────────────────────┘
```

There is no fifth runtime layer.

---

## 4. Layer A — Aegis Plugin / Skill Control Plane

### Ownership

The `aegis-project-state` Skill owns Project State interpretation, inspection, diagnosis, explicit repair/persistence requests, and deterministic support facts when another Primary owns the lifecycle stage.

The repository already describes this Skill as owning Project State inspection, validation, recomputation, state-drift diagnosis, and direct Project State tasks while not taking lifecycle-stage ownership.

For this repair, the Skill must additionally understand the P12/P13 concepts:

```text
Gate Decision Binding
  = Bound(exact decision)
  | Absent(no_applicable_integration_gate_decision)
```

and the historical rule:

```text
integrated binding is immutable history
```

### The Skill may

- read repository/GitHub durable evidence;
- read Project State manifests;
- compare Current Authority and historical occurrence facts;
- determine which P13 conceptual operation describes the requested repair;
- require durable occurrence and absence basis before authoring `Absent`;
- produce the exact manifest change that should be written;
- ask or use an authorized connected tool to write that change;
- report fail-closed blockers when truth is ambiguous.

### The Skill must not

- create a hidden autonomous loop;
- continuously monitor or reconcile repositories unless the user explicitly creates an allowed scheduled automation elsewhere;
- invent a synthetic Gate Decision;
- infer `Absent` from missing records or tool lookup failure;
- silently rewrite immutable history;
- treat a later PASS as retroactive authorization;
- own a private state database separate from repository durable state.

---

## 5. Layer B — Existing connected execution surfaces

GitHub, Codex, or another explicitly connected tool is the execution surface.

The architecture does not introduce an Aegis-specific execution service between the Skill and those tools.

Conceptually:

```text
Skill decision
   ↓
explicit repository mutation / handoff
   ↓
GitHub or Codex
   ↓
repository commit
```

The connected tool does not decide Aegis semantic truth. It executes the already-authorized mutation or supplies evidence.

For example, Codex may edit `.aegis/integrations.json`, but Codex does not decide that PR #82 has an `Absent` binding. That semantic decision must already be supported by Authority and durable evidence.

---

## 6. Layer C — durable Project State

The canonical persistent control state remains repository-authored manifests:

```text
.aegis/project.json
.aegis/authorities.json
.aegis/gates.json
.aegis/evidence.json
.aegis/integrations.json
```

`state.json` remains generated/read-model state, not Authority.

The repair may eventually require a replacement schema version to represent explicit `gate_decision_binding`, but P14 does not assign that version.

The durable repository is the source of persistent Project State truth; there is no parallel Aegis runtime database.

---

## 7. Layer D — optional deterministic repository validation

Existing repository tooling may remain as a validator/lint/CI utility.

Allowed roles include:

```text
schema validation
reference validation
cross-snapshot invariant checks
deterministic state recomputation
state drift detection
one-shot schema migration
CI regression checks
```

These tools are support mechanisms, not the product runtime.

### Explicit non-ownership

Repository validators must not:

- decide whether external governance evidence proves `Absent`;
- search GitHub and make Authority judgments;
- autonomously reconcile missing history;
- invoke lifecycle stages;
- schedule or execute Aegis work;
- become an agent loop;
- become a mutation service;
- become a transaction service.

The presence of Python tooling does not imply that new Python services or modules are required by this repair.

---

## 8. P13 operations are domain language, not runtime APIs

P13's six operations remain valid:

```text
O1 REGISTER_AWAITING_INTEGRATION
O2 REBIND_AWAITING_INTEGRATION
O3 FINALIZE_INTEGRATION_OCCURRENCE
O4 RECONCILE_HISTORICAL_INTEGRATION_OCCURRENCE
O5 CLOSE_UNMERGED_CANDIDATE
O6 APPEND_CORROBORATING_INTEGRATION_EVIDENCE
```

P14 interprets them as **control-plane verbs** used by Skills to reason about legal state changes.

They do not imply:

```text
Python classes
service endpoints
operation dispatchers
background workers
transaction engines
```

A Skill may say:

```text
This repair is O4 historical reconciliation.
```

and then produce the exact repository mutation through an existing tool surface.

That is sufficient.

---

## 9. Atomicity without a transaction subsystem

P13 requires logical atomicity: an invalid partial Project State must not be accepted as the successful result of a mutation.

That does **not** require a custom `Manifest Transaction Boundary` runtime subsystem.

In the Plugin-native architecture, atomicity means:

1. the Skill prepares the complete intended authored-state delta;
2. all required durable references are identified before the write;
3. the repository edit is made as one coherent change/commit where practical;
4. deterministic validation/CI must reject an incomplete or inconsistent result;
5. if validation fails, the lifecycle remains blocked rather than treating partial state as accepted.

This is repository workflow atomicity, not a bespoke transaction server.

---

## 10. Historical immutability without a history service

The invariant remains:

```text
once status = integrated:
  id
  kind
  ref
  target_ref
  integrated_revision
  gate_decision_binding
are historical identity-bearing facts
```

Protection is layered:

```text
Aegis Skill rule
+
Project State schema/invariant definition
+
optional deterministic transition validation / CI
```

No dedicated `IntegrationHistoryService` is required.

If a validator can enforce the invariant with a small change to existing repository tooling, that is allowed. The architecture does not require a new module simply to give the invariant a class or service name.

---

## 11. Migration without a migration service

When a replacement Project State schema version is eventually accepted, a one-shot deterministic migration utility may transform existing v0.5 records:

```yaml
gate_decision_id: D
```

into the replacement schema's explicit Bound form.

This utility may be implemented by extending the existing migration pattern or by a narrowly scoped one-shot script.

It is not a long-lived service and must not perform historical reconciliation.

```text
schema migration != O4 historical reconciliation
```

PR #82 must therefore still be reconciled explicitly after the replacement Authority is legally applicable.

---

## 12. PR #82 Plugin-native flow

After replacement Authority becomes accepted/applicable, the intended flow is:

```text
Aegis Project State Skill
  ↓
read durable repository occurrence evidence
  ↓
read accepted governance/absence basis
  ↓
classify requested repair as P13 O4
  ↓
construct exact Project State edit:
    int-pr82
    status = integrated
    integrated_revision = 3a260722...
    binding = Absent(no_applicable_integration_gate_decision)
    durable evidence refs
  ↓
GitHub / Codex writes repository files
  ↓
existing/minimally-extended validator + CI checks result
  ↓
Project State repair is accepted only if checks and lifecycle Authority allow it
```

No Aegis reconciliation daemon or mutation service participates.

---

## 13. Failure boundaries

### Ambiguous historical truth

If durable evidence cannot establish whether an applicable Gate Decision existed:

```text
BLOCKED
```

The Skill must not default to Absent.

### Invalid repository state

If schema or deterministic invariant checks fail:

```text
BLOCKED / state not accepted
```

The validator reports the defect; it does not autonomously repair it.

### Tool failure

A GitHub/Codex fetch or write failure is an execution/tool failure, not semantic evidence of `Absent` and not permission to infer historical truth.

### Contradictory later evidence

If later durable evidence contradicts an immutable binding, normal Project State mutation remains forbidden and the issue returns to Authority/governance review, as P13 already requires.

---

## 14. Explicitly removed architecture from prior P14/P15

The following are removed from the required architecture:

```text
Reconciliation / Mutation Service
Manifest Transaction Boundary as a runtime subsystem
Integration operation executor
Integration history service
Transition dispatcher as a required new runtime module
custom state orchestration layer
background reconciliation worker
```

The following proposed P15 modules are therefore not valid downstream requirements:

```text
integration_ops.py
transaction.py
transition.py
integration_history.py
integration_binding.py as a required standalone module
```

A future implementation may factor a tiny pure helper if code duplication genuinely warrants it, but P14 does not require such a module and it must not become a runtime/service boundary.

---

## 15. What remains valid from prior P14

The targeted repair preserves these architectural truths:

- `Absent` is explicit history, never missing data;
- Integrated historical identity is immutable;
- later PASS cannot retroactively authorize an earlier occurrence;
- migration must not create missing historical occurrences;
- `state.json` is derived, not Authority;
- deterministic validation should fail closed;
- current actionability is distinct from historical conformance.

Only the runtime/service realization is withdrawn.

---

## 16. P14 acceptance criteria

P14 targeted repair is complete when the downstream architecture satisfies all of the following:

1. Aegis remains a ChatGPT Plugin/Skills control plane.
2. No custom harness, daemon, autonomous agent runtime, or background service is required.
3. P12/P13 semantics remain intact.
4. P13 operation names are control-plane domain language, not mandatory runtime APIs.
5. Repository durable manifests remain the persistent state authority surface.
6. GitHub/Codex remain existing execution surfaces rather than being wrapped by an Aegis runtime.
7. Existing Python tooling is classified as optional deterministic validation/migration support only.
8. No new Python service/module is required merely to embody an architectural responsibility.
9. Atomicity is achieved through complete repository edits plus fail-closed validation, not a transaction subsystem.
10. PR #82 historical reconciliation remains explicit and evidence-driven.

---

## 17. P14 disposition

```yaml
p14_targeted_repair:
  scope: aegis/project-state
  finding: P22-F2
  p12_basis: 777e1e8a9652e2cbf220d234798641d65dc9b0c9
  p13_basis: b742ebb9f27520a595b2e73370f42157e28ea72e

  replaces_downstream_design_basis:
    p14: 21d6dd535dc7ab50898f7294e73c4bdd98757fc5
    dependent_p15: a0eb5ea562af580f21e4d8c6e01d77266c738c0d

  product_form: chatgpt_plugin_skills
  aegis_runtime: forbidden
  custom_harness: forbidden
  autonomous_agent: forbidden
  background_service: forbidden

  repository_python_tooling:
    allowed_role: deterministic_validation_and_one_shot_migration_only
    required_new_runtime_modules: false

  p12_p13_semantics_preserved: true
  replacement_version_assigned: false
  state_mutation_performed: false
  implementation_authorized: false

  status: READY_FOR_REPAIRED_P15
```
