# Project State v0.6 Root Persistence — P31 Package

Package ID: `PS-V06-P31-02`

Stage: `P31 Task Packaging`

Owner: `aegis-implementation`

Repository: `Mostorm-Labs/aegis`

Task anchor: `cfb69ee10dee03e34b363820cd66136a127658cc` (`ancestor`)

## Purpose

Close the implementation/persistence portion of `P22-F1` by migrating the root `.aegis` project from schema v0.5 to v0.6 and reconciling the already-established Verification Productization Authority / Gate / PR #81 integration history. This package deliberately stops before the real PR #82 O4 historical reconciliation.

## Trusted basis

- Project State v0.6 Current Authority: `docs/project-state-ungated-integration-v0.6.md`; P23 materialization `096b57f34dc9a29be6e844475f3725e0615f9968`.
- Project State v0.6 implementation accepted by P34: exact candidate `8ffb087e2557fa76cf6c7f7ffdb9effbe63ef333`; P34 review `5556311585`; repository integration merge `c0ec6cccc6675eca98aa3a453a5ad1c6b672d7dc`.
- P22 persistence finding / absence boundary: PR #82 comment `5553423707`.
- Verification Productization replacement Authority: `docs/verification-productization-verification-v0.2.md`, exact Authority basis `4d5ef43f0879a4ce45aeae0367d6f11187f29b61`, P21 `5121845074`, P23 `5122113780`.
- VP-I03 repaired Gate-PASS result: `41cc2035ef18b2fbb05d2e3c59792563fd47e4a6`, P34 review `5122032071` on PR #80.
- PR #81 final pre-occurrence integration authorization: P24 review `5122078313`; merge closure `5553309663`; merge commit `dfd22aea08a6523a35051c066a722c3286c23d75`.

## Authorized files

Only root Project State persistence files may be changed:

```text
.aegis/project.json
.aegis/authorities.json
.aegis/gates.json
.aegis/evidence.json
.aegis/integrations.json
.aegis/state.json
```

No production code, schema, Skill, workflow, release, or documentation changes are authorized by this package.

## Required changes

### 1. Mechanical root migration v0.5 -> v0.6

Use the existing deterministic `migrate-v06` tooling. The migrated authored state must:

- set all root Project State manifest `schema_version` values to `0.6`;
- convert every legacy v0.5 Integration `gate_decision_id: D` to `gate_decision_binding: {"kind":"bound","gate_decision_id":"D"}`;
- preserve every existing Integration identity, target, occurrence revision, evidence list, Gate Decision identity, and historical meaning;
- infer **zero** Absent records from legacy state.

Do not hand-edit a migrated legacy binding into Absent.

### 2. Persist Project State Authority supersession

In `.aegis/authorities.json`:

- `aegis-project-state-v0.5` becomes `Superseded`;
- add `aegis-project-state-v0.6` as the unique `Current` Authority for scope `aegis/project-state`;
- v0.6 ref is `docs/project-state-ungated-integration-v0.6.md`;
- v0.6 `supersedes` v0.5 and `change_class` is `semantic`;
- preserve v0.5 as immutable historical Authority.

### 3. Persist Verification Productization Authority transition

Add the Verification Productization verification Authority lineage for scope `aegis/verification-productization/verification`:

- predecessor ID: `aegis-verification-productization-verification-v0.1`, version `v0.1`, ref `docs/verification-productization-verification-v0.1.md`, status `Superseded`;
- replacement ID: `aegis-verification-productization-verification-v0.2`, version `v0.2`, ref `docs/verification-productization-verification-v0.2.md`, status `Current`, supersedes the v0.1 ID, change class `semantic`.

Use the minimum dependency list supported by durable Authority; do not invent new semantic dependencies merely to satisfy formatting.

### 4. Persist VP-I03 / PR #80 Gate lineage

Add Gate Contract:

`gate-verification-productization-v02-pr80`

- stage: `P34`;
- authority: `aegis-verification-productization-verification-v0.2`.

Add immutable decision:

`gate-verification-productization-v02-pr80::decision::0001`

- verdict: `PASS`;
- evidence includes the exact PR #80 P34 review `https://github.com/Mostorm-Labs/aegis/pull/80#pullrequestreview-5122032071`.

### 5. Persist PR #81 integration authorization and occurrence

Add Gate Contract:

`gate-verification-productization-v02-pr81`

- stage: `P24`;
- authority: `aegis-verification-productization-verification-v0.2`.

Add immutable decision:

`gate-verification-productization-v02-pr81::decision::0001`

- verdict: `PASS`;
- evidence includes the exact pre-occurrence P24 authorization `https://github.com/Mostorm-Labs/aegis/pull/81#pullrequestreview-5122078313`.

Add Integration:

```yaml
id: int-pr81
kind: pull_request
ref: https://github.com/Mostorm-Labs/aegis/pull/81
status: integrated
target_ref: main
integrated_revision: dfd22aea08a6523a35051c066a722c3286c23d75
gate_decision_binding:
  kind: bound
  gate_decision_id: gate-verification-productization-v02-pr81::decision::0001
```

Occurrence evidence must include the merge commit / integration closure and must not rewrite the Gate decision after the fact.

### 6. Evidence records

Add the minimum reviewer-resolvable evidence records needed by the new Authority/Gate/Integration entries. At minimum preserve exact durable refs for:

- Verification Productization P23 Authority supersession: PR #82 review `5122113780`;
- VP-I03 P34 PASS: PR #80 review `5122032071`;
- PR #81 P24 merge authorization: PR #81 review `5122078313`;
- PR #81 repository occurrence: merge commit `dfd22aea08a6523a35051c066a722c3286c23d75` and/or closure `5553309663`.

Evidence IDs may follow existing repository naming style but must be stable and unambiguous.

### 7. Generated state

After authored manifests are final, generate `.aegis/state.json` only through the existing deterministic tooling. Do not hand-author digest or derived state.

## Explicit non-goals / hard stop

This package MUST NOT:

- create `int-pr82`;
- create any synthetic Gate Decision for PR #82;
- bind PR #82 to P23 review `5122113780` as merge authorization;
- retroactively bind a later PASS to PR #82;
- modify any Integration's historical identity while migrating;
- modify code/schema/Skill/workflow/release files;
- merge the resulting PR;
- publish a release or expand rollout.

PR #82 O4 reconciliation is the separately gated successor `PS-V06-I06` and remains unauthorized until this root v0.6 persistence result is independently accepted.

## Required procedure / verification

1. Capture the exact pre-change root `.aegis` snapshot from task anchor ancestry.
2. Run the existing v0.5 -> v0.6 migration into a temporary destination; use that output as the mechanical baseline rather than manually converting every legacy record.
3. Apply only the targeted P22-F1 reconciliation records above.
4. Recompute root `state.json`.
5. Run `transition-check` from the exact pre-change v0.5 snapshot to the candidate v0.6 root.
6. Run:

```bash
python3 -m tools.aegis_state.cli validate .
python3 -m tools.aegis_state.cli check .
python3 -m unittest discover -s tests/project_state -v
python3 -m tools.aegis_skillset.cli validate .
python3 scripts/build_skillset.py --check
python3 -m unittest discover -s tests/skillset -v
python3 evals/scripts/validate_corpus.py
python3 -m unittest discover -s evals/tests -v
```

7. Materialize the exact result on branch `chatgpt/project-state-v06-root-persistence` in a reviewer-accessible PR and wait for exact-SHA hosted Project State / Skillset / Verification Productization CI.

## Exit criteria

- root schema is exactly `0.6`;
- exactly one Current `aegis/project-state` Authority exists and it is v0.6;
- Verification Productization v0.2 is the unique Current Authority for its scope;
- all pre-existing v0.5 Integration bindings migrated to Bound with zero inferred Absent;
- PR #80 Gate lineage exists and remains PASS;
- `int-pr81` exists and is Bound to its pre-occurrence P24 PASS decision;
- `int-pr82` is absent from root persistence in this package;
- `transition-check`, root validate/check, Project State tests, Skillset checks, evals, and exact-SHA hosted CI all PASS;
- no files outside the six authorized `.aegis` paths changed.

## Required return

```yaml
P32_return:
  package_id: PS-V06-P31-02
  repository: Mostorm-Labs/aegis
  actual_starting_revision: <sha>
  task_anchor:
    revision: cfb69ee10dee03e34b363820cd66136a127658cc
    relation: ancestor
  result_revision: <exact-sha>
  exact_tree: <tree-sha>
  materialized_ref: <PR/ref>
  changed_files: <list>
  migration:
    legacy_integrations_migrated_to_bound: <count>
    inferred_absent: 0
  project_state:
    schema_version: "0.6"
    current_project_state_authority: aegis-project-state-v0.6
    current_verification_productization_authority: aegis-verification-productization-verification-v0.2
    int_pr81: bound
    int_pr82_present: false
  verification:
    transition_v05_to_v06: <PASS|FAIL>
    root_validate_check: <PASS|FAIL>
    project_state_tests: <PASS|FAIL>
    skillset: <PASS|FAIL>
    distribution_check: <PASS|FAIL>
    evals: <PASS|FAIL>
    hosted_ci:
      project_state: <run/result>
      skillset: <run/result>
      verification_productization: <run/result>
  merged: false
  blockers: []
  status: READY_FOR_P34 | BLOCKED_*
  return_surface: CONTROL_REVIEW
```

`READY_FOR_P34` is only an execution return and never constitutes a Gate PASS.