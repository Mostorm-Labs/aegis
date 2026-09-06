# Aegis Project State v0.6 — P31 Single Implementation Package

Status: **P31 Task Package — APPROVED_FOR_P32**

Package ID: `PS-V06-P31-01`

Primary owner: `aegis-implementation`

Execution surface: `CODE_EXECUTION`

Preferred executor: `codex`

Repository: `Mostorm-Labs/aegis`

## 1. Purpose

Implement the complete pre-P34 Project State v0.6 support in one repository package. This package intentionally collapses P30 tasks `PS-V06-I01` through `PS-V06-I04` into one execution unit. The P30 task boundaries remain useful implementation order only; they are not separate P31 packages and must not require separate control-plane returns.

The executor should proceed end-to-end until the complete v0.6 support candidate is implemented, fully verified, and materialized at one reviewer-accessible exact Git revision.

## 2. Current Authority and trusted basis

```yaml
current_authority:
  id: aegis-project-state-v0.6
  ref: 096b57f34dc9a29be6e844475f3725e0615f9968
  artifact: docs/project-state-ungated-integration-v0.6.md

verification_basis:
  ref: 19b0433a9641847289262a3ad664122c78907569
  artifact: docs/project-state-p20-ungated-integration-verification-design.md

p21_review:
  ref: 82103e53354956133f5d1b5d2eb6c7a4f3ed580e
  verdict: PASS
  disposition: ACCEPTED_FOR_DOWNSTREAM

p30_plan:
  ref: e621e466328471bb4bc4a4e9f6f6438235263669
  plan_id: PS-V06-P30-01
```

Additional accepted design refs:

```yaml
P12: 777e1e8a9652e2cbf220d234798641d65dc9b0c9
P13: b742ebb9f27520a595b2e73370f42157e28ea72e
P14: cc768db72450b2c9d75a3d9650d447cdbd10048b
P15: ffa79084c10211668ced1ae6801e238c789ffeb7
P16: 40e094b62f9f3150516f4631ec9df98e6729d258
P17: 97efff0e414f17c5667c957f6d497472a6d2459a
P18: 976de3f7729fc2c63a4726458afbe37292f35c17
```

## 3. Repository anchor

```yaml
task_anchor:
  revision: 096b57f34dc9a29be6e844475f3725e0615f9968
  relation: ancestor

resume_cursor: null
```

The executor must record the actual starting revision. A descendant of the anchor is valid if ancestry is preserved; historical HEAD equality is not required.

## 4. Authorized scope

The package authorizes all implementation required to make v0.6 support complete before P34, including these surfaces:

```text
schemas/project-state/v0.6/**
examples/project-state/v0.6-minimal/**

tools/aegis_state/model.py
tools/aegis_state/compute.py
tools/aegis_state/cli.py
tools/aegis_state/migrate_v06.py
tools/aegis_state/transition_v06.py
tools/aegis_state/transition_v05.py   # only if compatibility dispatch requires it

tests/project_state/**               # v0.6 tests plus necessary regressions

skillset/skills/aegis-project-state/SKILL.md
skillset/skills/aegis-project-state/references/project-state.md
skills/aegis-project-state/SKILL.md
skills/aegis-project-state/references/project-state.md

evals/cases/dogfood.json
evals/tests/**                        # only where needed for v0.6 behavioral regression

.github/workflows/project-state.yml
```

Small adjustments to adjacent deterministic Project State helpers/tests are allowed when mechanically required by this package. Do not perform unrelated cleanup or refactoring.

## 5. Required implementation outcome

The complete candidate must implement all of the following in one execution run:

1. Add Project State schema version `0.6` while preserving v0.3/v0.4/v0.5 behavior.
2. Preserve v0.5 Gate Contract / Gate Decision lineage semantics in v0.6.
3. Replace v0.5 Integration `gate_decision_id` with canonical v0.6 `gate_decision_binding`:

```yaml
gate_decision_binding:
  kind: bound
  gate_decision_id: <exact immutable decision id>
```

or:

```yaml
gate_decision_binding:
  kind: absent
  reason: no_applicable_integration_gate_decision
```

4. Enforce status rules:

```text
awaiting_integration -> Bound only
integrated           -> Bound | Absent
closed_unmerged      -> Bound only
```

5. Derive historical conformance without collapsing semantics:

```text
Bound(PASS/PASS_WITH_FINDINGS) -> conforming
Bound(BLOCKED_*)                -> nonconforming
Absent                          -> nonconforming
```

Generated state must preserve whether a nonconforming occurrence was Bound(BLOCKED) or Absent.

6. Never infer Absent from missing fields, dangling references, failed lookups, empty results, unavailable evidence, timeout, permission failure, unresolved decision identity, or other unknown state.
7. Extend deterministic projection and generator version behavior for v0.6 without changing older-version output contracts.
8. Implement deterministic v0.5 -> v0.6 migration:

```text
gate_decision_id: D
->
gate_decision_binding:
  kind: bound
  gate_decision_id: D
```

Migration must infer zero Absent records and preserve historical conformance and occurrence identity.
9. Implement v0.6 transition validation that preserves existing immutable Gate Contract / Gate Decision history and additionally rejects in-place mutation of integrated occurrence identity/binding. After an Integration is `integrated`, these are immutable:

```text
id
kind
ref
target_ref
integrated_revision
gate_decision_binding
```

Evidence may only grow through legal corroborating-evidence append semantics; no binding rewrite is allowed.
10. Extend CLI/version dispatch so validate/recompute/check/migration/transition checking handle v0.6 deterministically.
11. Update Project State Skill and reference material in both materialized Skill trees so control-plane semantics match v0.6. Explicitly state `missing/failed/unresolved != Absent`, occurrence-time binding immutability, later PASS non-retroactivity, and O1-O6 as semantic vocabulary rather than runtime APIs.
12. Add durable dogfood/regression coverage for the real class of failure exposed by PR #82, including tool-read failure not implying Absent and later PASS not rewriting historical binding.
13. Extend Project State CI to parse and validate v0.6, check the v0.6 minimal fixture, enforce appropriate v0.5/v0.6 transition history, and keep Project State + Skillset + evaluation regressions in the exact candidate qualification path.
14. Materialize one complete exact candidate for independent P34 review.

## 6. Mandatory verification / P20 evidence mapping

The result must satisfy the full P20 evidence contract, including:

```text
V1  Gate Decision Binding representation
V2  status x binding constraints
V3  Absent non-inference
V4  historical conformance projection
V5  historical immutability
V6  occurrence-time binding / later PASS
V7  lossless v0.5 migration
V8  legal transition semantics
V9  Plugin-native / forbidden-runtime boundary
V10 platform-result authority separation
V11 PR #82 historical absence oracle
V12 deterministic replay / idempotency
V13 stale-basis / uncertain-write safety
V14 resume / exact-ref optimization safety
```

PR #82 must appear as a fixture/oracle only before P34. The implementation/tests must prove that this shape is representable and nonconforming:

```yaml
id: int-pr82
status: integrated
integrated_revision: 3a2607220cd875dc66857b334dcfbd2c763e7c7d
gate_decision_binding:
  kind: absent
  reason: no_applicable_integration_gate_decision
```

The fixture must not mutate root `.aegis`.

## 7. Verification commands

At minimum, run and record results for:

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

Also run focused RED->GREEN tests for v0.6 binding, migration, transition immutability, later-PASS history, and PR #82 oracle. A RED caused only by missing v0.6 support is valid; syntax/import/fixture-construction mistakes are not acceptable RED evidence.

If repository workflow/CI is available for the materialized result, report the exact workflow run ID and result. Local test success alone is not sufficient to claim P34 readiness if the required reviewer-accessible evidence boundary has not been created.

## 8. Explicit non-goals / forbidden actions

This package does NOT authorize:

```text
root .aegis/project.json migration to 0.6
root .aegis/authorities.json migration to 0.6
root .aegis/gates.json migration to 0.6
root .aegis/evidence.json migration to 0.6
root .aegis/integrations.json migration to 0.6
root .aegis/state.json replacement for 0.6
real int-pr82 persistence
retroactive Gate Decision creation for PR #82
reinterpretation of P23 review 5122113780 as PR #82 merge authorization
merge to main
release / rollout
P34 self-declaration
```

Do not create or require:

```text
tools/aegis_state/integration_ops.py
tools/aegis_state/transaction.py
integration-history service
transition dispatcher service
Aegis daemon
agent runtime
custom harness
background reconciler
repository-state service
transaction server
internal execution loop
```

The Python code in this package is deterministic repository support only; it owns no Authority, Gate verdict, evidence sufficiency decision, or lifecycle orchestration.

## 9. Stop / blocker behavior

Stop and return `BLOCKED_AUTHORITY` if implementation discovers a contradiction in the accepted v0.6/P20 Authority rather than repairing semantics inside code.

Return `BLOCKED_REPOSITORY_IDENTITY` if repository/package/anchor identity cannot be resolved safely.

Return `BLOCKED_EXECUTION_DIVERGENCE` if the execution history is incompatible with the package anchor and cannot be reconciled as a descendant.

Return `BLOCKED_EVIDENCE` if the implementation result cannot be materialized at a reviewer-accessible durable ref or if required verification evidence cannot be produced.

Do not weaken Absent proof requirements merely to make tests pass.

## 10. Exit criteria

This single package is complete only when all of the following are true:

- v0.6 schema/example/tooling/Skill/CI support is implemented;
- all mandatory P20 verification groups have executable evidence;
- v0.3/v0.4/v0.5 regressions remain green;
- v0.5 -> v0.6 migration is deterministic and lossless for legacy Bound history;
- integrated binding/identity immutability is enforced;
- PR #82 golden fixture passes without root persistence;
- no forbidden runtime/harness surface was added;
- root `.aegis` remains physically v0.5;
- exact result is pushed/materialized at a reviewer-accessible Git ref;
- the executor returns the exact materialized revision and verification evidence for P34.

## 11. Required P32 return

Return one consolidated result:

```yaml
P32_return:
  package_id: PS-V06-P31-01
  repository: Mostorm-Labs/aegis
  actual_starting_revision: <sha>
  task_anchor:
    revision: 096b57f34dc9a29be6e844475f3725e0615f9968
    relation: ancestor
  result_revision: <exact final sha>
  materialized_ref: <reviewer-accessible branch/PR/ref resolving result_revision>
  changed_files: [<paths>]
  completed_scope:
    - v0.6 schema/model/projection
    - v0.5->v0.6 migration
    - v0.6 transition immutability
    - Skill/reference materialization
    - regression/eval corpus
    - CI qualification
  verification:
    project_state_tests: <result>
    v0_5_regression: <result>
    v0_6_validate_check: <result>
    root_v0_5_self_host: <result>
    skillset: <result>
    evals: <result>
    hosted_ci: <run-id/result-or-blocker>
  root_aegis_modified: false
  pr82_persisted: false
  blockers: []
  status: READY_FOR_P34 | BLOCKED_*
```

`READY_FOR_P34` is an implementation return state only. It is not a P34 verdict.

## 12. P31 disposition

```yaml
p31_task_package:
  package_id: PS-V06-P31-01
  packaging_strategy: single_package
  subsumes_p30_tasks:
    - PS-V06-I01
    - PS-V06-I02
    - PS-V06-I03
    - PS-V06-I04
  task_anchor:
    revision: 096b57f34dc9a29be6e844475f3725e0615f9968
    relation: ancestor
  resume_cursor: null
  preferred_executor: codex
  root_persistence_authorized: false
  pr82_real_reconciliation_authorized: false
  verdict: READY
  disposition: APPROVED_FOR_P32
```
