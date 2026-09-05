# Aegis Project State — P15 Plugin-Native Minimal Module Design

Status: **P15 Module Design Replacement Candidate**

Scope: `aegis/project-state`

Triggering finding: `P22-F2 = MISSING_CONTRACT / SPEC_DEFECT`

Repository basis: `main@3a2607220cd875dc66857b334dcfbd2c763e7c7d`

P12 semantic basis candidate: `777e1e8a9652e2cbf220d234798641d65dc9b0c9`

P13 operation basis candidate: `b742ebb9f27520a595b2e73370f42157e28ea72e`

Repaired P14 basis candidate: `cc768db72450b2c9d75a3d9650d447cdbd10048b`

Prior P15 candidate replaced as downstream design basis: `a0eb5ea562af580f21e4d8c6e01d77266c738c0d`

Current Authority under repair: `aegis-project-state-v0.5`

This artifact replaces the runtime-oriented P15 candidate with the smallest Plugin-native design that can carry the P12/P13 semantics. It does not assign a replacement Project State version, does not modify `.aegis/*`, does not implement code, and does not authorize merge, release, or rollout.

---

## 1. P15 design objective

The repaired P14 establishes that Aegis is a ChatGPT Plugin/Skills control plane, not a custom harness or runtime.

Therefore P15 must answer only:

> Which existing Plugin/Skill, repository schema, validation, and test surfaces need to carry the new Project State semantics?

It must **not** translate conceptual responsibilities into mandatory Python services or runtime modules.

The design principle is:

```text
prefer instruction/schema/test changes
before code changes;
prefer minimal existing-validator changes
before new modules;
never create an Aegis runtime layer.
```

---

## 2. Minimal target surface

The repair is bounded to five repository surfaces:

```text
A. aegis-project-state Skill instructions
B. aegis-project-state reference contract
C. Project State schema / examples for the future replacement version
D. existing deterministic validator / CI only where mechanically necessary
E. regression tests / evidence fixtures
```

No new execution subsystem is part of P15.

---

## 3. Surface A — `aegis-project-state` Skill instructions

Current repository materializes the Project State Skill in both:

```text
skillset/skills/aegis-project-state/SKILL.md
skills/aegis-project-state/SKILL.md
```

The two surfaces must remain semantically aligned under the repository's existing skill materialization rules.

### Required semantic additions

The Skill instructions must eventually make these rules explicit:

```text
1. Integration occurrence != Gate conformance.
2. For the replacement schema, Gate Decision Binding is explicit:
     Bound(exact decision)
     or
     Absent(no_applicable_integration_gate_decision).
3. Missing data / failed lookup / unresolved decision identity != Absent.
4. Awaiting Integration remains Bound-only.
5. Integrated history may be Bound or Absent.
6. An integrated binding is immutable historical truth.
7. A later PASS cannot retroactively bind an earlier occurrence.
8. Historical Absent requires durable occurrence basis + durable absence/governance basis.
9. P13 O1-O6 are conceptual state-transition verbs used for reasoning, not runtime API calls.
10. If evidence is ambiguous, fail closed and route to the owning Authority/governance stage.
```

### Skill non-ownership

The Skill must not claim that deterministic tooling can establish governance truth by itself.

It may use tooling to validate manifests, but evidence sufficiency and lifecycle Authority remain Aegis reasoning/governance concerns.

### No new Skill/agent requirement

This repair does **not** require:

```text
another agent skill
background skill
reconciliation skill
mutation skill
transaction skill
```

The existing `aegis-project-state` Skill is the correct product surface.

---

## 4. Surface B — Project State reference contract

Current repository already has:

```text
skillset/skills/aegis-project-state/references/project-state.md
```

with the corresponding materialized Plugin reference under `skills/aegis-project-state/references/`.

The Project State reference should carry the detailed version-aware semantics that are too large for `SKILL.md`.

### Required reference content

The future repaired reference should define:

#### Gate Decision Binding

```text
Bound(D)
Absent(no_applicable_integration_gate_decision)
```

#### Status constraints

```text
awaiting_integration -> Bound only
integrated           -> Bound | Absent
closed_unmerged      -> Bound only
```

#### Historical conformance

```text
Bound(PASS/PASS_WITH_FINDINGS) -> conforming
Bound(BLOCKED_*)                -> nonconforming
Absent                          -> nonconforming
```

#### Historical immutability

Once integrated, the following remain immutable:

```text
id
kind
ref
target_ref
integrated_revision
gate_decision_binding
```

#### P13 conceptual operations

The reference should describe O1-O6 as legal state-transition vocabulary so the Skill can reason consistently across sessions.

It must explicitly state that these operations do not imply Python functions, services, or an executor.

#### Historical reconciliation

For O4 with Absent:

```text
Occurrence Basis
+
Absence Basis
```

must be explicit and durable.

Ambiguity fails closed.

---

## 5. Surface C — future replacement schema

P12 requires a replacement representation capable of expressing explicit Gate Decision Binding.

P15 does not assign the replacement schema version.

When lifecycle Authority eventually assigns one, its Integration schema must represent the P12 sum type directly.

Conceptually:

```yaml
gate_decision_binding:
  kind: bound
  gate_decision_id: <decision-id>
```

or:

```yaml
gate_decision_binding:
  kind: absent
  reason: no_applicable_integration_gate_decision
```

### Schema responsibilities only

The schema should mechanically enforce what JSON Schema can safely enforce, such as:

- exactly one binding variant;
- required fields per variant;
- closed Absent reason vocabulary;
- status/binding compatibility where practical;
- no legacy `gate_decision_id` field in replacement-version records if the replacement contract says binding is canonical.

### Schema non-ownership

JSON Schema cannot decide:

```text
whether a Gate Decision was actually applicable at occurrence time
whether durable evidence proves no applicable decision existed
whether a later decision is retroactive
```

Those remain control-plane semantics.

---

## 6. Surface D — existing deterministic validator / CI

The repository already contains deterministic Project State tooling and a Project State CI workflow.

P15 classifies those as optional support tooling only.

### Preferred implementation rule

When implementation is eventually authorized:

```text
first attempt:
  minimally extend existing validation paths

only if genuinely necessary:
  add a small version-specific helper
```

There is **no** architectural requirement to create new modules named:

```text
integration_binding.py
integration_ops.py
integration_history.py
transition.py
transaction.py
```

Those names from the prior P15 candidate are withdrawn.

### What existing tooling may need to do

Mechanically, a future implementation may need existing validator/compute/transition paths to understand the replacement schema well enough to:

- reject malformed Bound/Absent records;
- reject dangling Bound decision references;
- reject forbidden status/binding combinations;
- project Absent historical conformance as nonconforming;
- preserve the distinction between Absent and Bound(BLOCKED);
- reject mutation of already-integrated historical identity;
- recompute `state.json` deterministically;
- validate lossless migration of old bound records.

These are validation duties, not orchestration duties.

### CI

The existing Project State workflow should continue to invoke deterministic checks.

P15 does not introduce:

```text
an Aegis CI agent
a reconciliation job
a mutation workflow
a background repair workflow
```

CI remains a verifier.

---

## 7. Surface E — tests and evidence fixtures

The repair should be proven primarily through regression cases, not through runtime machinery.

The future implementation should cover at least these cases:

### Binding shape

```text
integrated + Bound(valid decision) -> valid
integrated + Absent(valid reason) -> valid
awaiting + Absent -> invalid
closed_unmerged + Absent -> invalid
missing binding -> invalid in replacement schema
unknown/dangling Bound decision -> invalid
```

### Historical conformance

```text
Bound(PASS) -> conforming
Bound(BLOCKED) -> nonconforming
Absent -> nonconforming
```

and Bound(BLOCKED) must remain distinguishable from Absent.

### Historical immutability

Reject:

```text
Bound(D1) -> Bound(D2)
Bound -> Absent
Absent -> Bound
integrated_revision change
removal of integrated occurrence
```

### Later PASS

Prove that a later PASS may affect current/future actionability but does not rewrite an earlier Absent or Bound(BLOCKED) occurrence.

### Legacy migration

Prove that existing v0.5:

```yaml
gate_decision_id: D
```

maps losslessly to replacement Bound(D), with no legacy record inferred as Absent.

### PR #82 fixture

After replacement Authority is active, a dedicated fixture should prove the intended O4 historical reconciliation shape for:

```text
int-pr82
integrated_revision = 3a260722...
binding = Absent(no_applicable_integration_gate_decision)
```

using durable occurrence and absence basis.

P15 does not authorize applying that fixture to the real `.aegis` state yet.

---

## 8. No runtime API surface

The repaired P15 intentionally defines **no** public runtime API such as:

```python
apply_integration_operation(...)
prepare_operation_transaction(...)
validate_transition_dispatch(...)
reconcile_history(...)
```

The Plugin itself reasons about the conceptual operation and produces a repository mutation or handoff.

If implementation later uses a private helper function inside an existing validator for readability, that helper is an implementation detail and not part of Aegis product architecture.

---

## 9. No transaction module

The prior P15 proposed a `transaction.py` module. That requirement is removed.

For this Plugin-native product, a legal Project State change means:

```text
Aegis determines the complete intended patch
→ connected tool writes a coherent repository change
→ validator/CI verifies resulting manifests
→ lifecycle accepts or blocks the result
```

Repository commits already provide the durable change boundary.

A custom transaction subsystem would duplicate repository semantics and incorrectly move Aegis toward a harness.

---

## 10. No operation executor

The prior `integration_ops.py` requirement is removed.

P13 operations remain documentation/Skill concepts:

```text
O1-O6 tell Aegis what kind of state transition is being considered.
```

They are useful because they make reasoning and verification precise.

They are not useful as a reason to create an internal executor.

---

## 11. No history service or dispatcher

The prior `integration_history.py` and `transition.py` requirements are removed as mandatory architecture.

Historical immutability can be enforced through:

```text
Skill contract
+
reference contract
+
replacement schema where expressible
+
minimal existing validator/CI logic where cross-snapshot comparison is required
```

If the existing transition validator later needs a few additional checks, implementation may extend it or add a narrowly scoped version-specific validator according to the repository's existing pattern.

P15 does not prescribe a dispatcher/service layer.

---

## 12. Minimal dependency structure

The repaired design dependency is:

```text
P12/P13 semantic Authority candidates
        ↓
P14 Plugin-native architecture
        ↓
aegis-project-state SKILL.md
        ↓
project-state reference
        ↓
future replacement schema
        ↓
optional minimal validator / CI support
        ↓
regression evidence
```

Not:

```text
Skill
→ custom state runtime
→ operation service
→ transaction service
→ persistence engine
```

---

## 13. Concrete future implementation surface

When implementation is eventually authorized, the expected change set should be biased toward:

```text
MODIFY / MATERIALIZE AS NEEDED
  skillset/skills/aegis-project-state/SKILL.md
  skillset/skills/aegis-project-state/references/project-state.md
  skills/aegis-project-state/SKILL.md
  skills/aegis-project-state/references/project-state.md

ADD ONLY AFTER REPLACEMENT VERSION IS AUTHORIZED
  schemas/project-state/<replacement-version>/**
  examples/project-state/<replacement-version>/**

MINIMAL EXTENSION ONLY IF VERIFICATION REQUIRES IT
  tools/aegis_state/model.py
  tools/aegis_state/compute.py
  existing/version-specific transition validation
  existing migration utility/pattern
  .github/workflows/project-state.yml
  tests/project_state/**
```

Expected **not** to add:

```text
tools/aegis_state/integration_ops.py
tools/aegis_state/transaction.py
tools/aegis_state/transition.py as a new dispatcher
tools/aegis_state/integration_history.py
an Aegis service/daemon/harness
```

`integration_binding.py` is also not a required module. If a tiny pure helper later proves the simplest implementation after tests expose duplicated logic, it may be considered as a local refactor, but it is not an architectural requirement and must not become runtime infrastructure.

---

## 14. P15 acceptance criteria

P15 replacement is complete when:

1. the Project State repair is carried primarily by the existing Plugin/Skill contract and reference;
2. P12/P13 semantics are represented without inventing runtime services;
3. future schema work is version-gated and not prematurely named;
4. existing Python tooling remains optional deterministic validation support;
5. `integration_ops.py`, `transaction.py`, required `transition.py`, and service-style modules are removed from downstream requirements;
6. no autonomous agent/harness/background loop is introduced;
7. regression tests are the primary proof surface for deterministic tooling behavior;
8. PR #82 remains a later explicit Skill-driven O4 repository repair, not an automatically reconciled record;
9. no `.aegis` mutation occurs during design;
10. implementation remains unauthorized until downstream verification/governance stages allow it.

---

## 15. P15 disposition

```yaml
p15_plugin_native_minimal_design:
  scope: aegis/project-state
  finding: P22-F2

  p12_basis: 777e1e8a9652e2cbf220d234798641d65dc9b0c9
  p13_basis: b742ebb9f27520a595b2e73370f42157e28ea72e
  p14_basis: cc768db72450b2c9d75a3d9650d447cdbd10048b

  replaces_downstream_design_basis:
    p15: a0eb5ea562af580f21e4d8c6e01d77266c738c0d

  product_surface:
    primary:
      - aegis-project-state_skill
      - project-state_reference
      - future_replacement_schema
    support_only:
      - existing_validator
      - existing_ci
      - regression_tests

  required_new_python_runtime_modules: []
  operation_executor: forbidden
  transaction_subsystem: forbidden
  reconciliation_service: forbidden
  autonomous_agent_or_harness: forbidden

  replacement_version_assigned: false
  state_mutation_performed: false
  implementation_authorized: false

  status: READY_FOR_DOWNSTREAM_ARCHITECTURE_CONTINUATION
```
