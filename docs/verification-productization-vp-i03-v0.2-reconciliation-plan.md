# Aegis Verification Productization — VP-I03 ECV0 v0.2 Targeted Reconciliation Plan

> **For agentic workers:** use `superpowers:test-driven-development` for P32 implementation and `superpowers:verification-before-completion` before any completion claim. This document is P30 control materialization only; it does not start P32.

**Stage:** `P30 Implementation Planning — targeted reconciliation`

**Owner:** `aegis-implementation`

**Repository:** `Mostorm-Labs/aegis`

**Goal:** preserve the valid VP-I03 implementation already materialized at `2fec701cc38bb0d9bcb558d8802d0c7f012f408a`, reconcile only the two contract deltas accepted by ECV0 v0.2, and freeze the smallest repair scope that can support a fresh P32 requalification without rewriting historical evidence or release publication state.

---

## 1. Exact reconciliation basis

```yaml
repository:
  provider: github
  full_name: Mostorm-Labs/aegis

fresh_main_baseline: 342d6785d8f54dd9beb2c3bb82398f29b405df2f

prior_p20_basis: 674e01737621621b8131e35f83313fb0154a9f6d
prior_p21_review: 5121075377

replacement_p20_basis: 4d5ef43f0879a4ce45aeae0367d6f11187f29b61
replacement_p21_review: 5121845074
replacement_p21_verdict: PASS
replacement_p21_disposition: ACCEPTED_FOR_DOWNSTREAM

p17_platform_basis: c8f47d049be50d65f88b04ad141650ed6dfdb826

predecessor_package_id: VP-I03-P31-01
predecessor_package_ref: a3dd0f1aa08f2686b9169059799555cd597ca503
predecessor_package_pr: 76

preserved_implementation_result: 2fec701cc38bb0d9bcb558d8802d0c7f012f408a
preserved_implementation_pr: 77
blocked_p32_return: 5121781308
central_routing_review: 5121799448
```

The predecessor P20/P21 and predecessor P31 package remain immutable history. ECV0 v0.2 is a replacement downstream basis, not a retroactive rewrite of those occurrences.

The repair line starts from the exact preserved implementation result `2fec701c...`. The valid 31-path VP-I03 implementation is implementation reality and MUST NOT be replayed or rewritten merely because the Verification contract was repaired.

---

## 2. What is preserved without reimplementation

The following result evidence remains valid predecessor input:

```yaml
verification_productization_tests: 83/83_OK
deterministic_scenarios: 17/17_PASS
mandatory_mutants: 17/17_DETECTED
mutant_false_acceptance: 0
provider_run: 33973747955
provider_job: 101326724541
provider_artifact: 9971689270
provider_artifact_digest: sha256:6e5784c103d7870adc19c35012bb96791a9e772d2da0ac3c7888762bd08aea59
```

Those facts are predecessor evidence only. They do **not** retroactively grant the repaired obligations:

```yaml
revised_EC_PFC01: NOT_RETROACTIVELY_GRANTED
EC_PFC03: NOT_RETROACTIVELY_GRANTED
EC_PFC04: STILL_PENDING_FUTURE_CONTROL_REVIEW
prior_failed_workflow_run: HISTORICAL_FAILURE_PRESERVED
P34_PASS: false
```

The following implementation surfaces from the prior VP-I03 result are preserved as-is unless a fresh P32 proves that one of the six repair paths below cannot satisfy the accepted v0.2 contract:

- `tools/aegis_proof/adapters/**`
- `tools/aegis_proof/cli.py`
- `tools/aegis_proof/__main__.py`
- existing canonical Skill integration and generated `skills/**` changes from PR #77
- existing scenario corpus `EC-S01..EC-S17`
- existing mutant corpus `EC-M01..EC-M17`
- existing candidate Plugin parity behavior

No accepted Proof Runtime semantics are reopened by this P30 occurrence.

---

## 3. Contract delta A — executor-agnostic EC-PFC01 / EC-PFC02

### P30 decision

No new Proof Runtime module or canonical Skill rewrite is required for this delta.

The preserved implementation already separates lifecycle surface from product executor and already performs repository/package/anchor preflight. The defect was the old P20/P31 **corroboration requirement** that named Codex itself as the generic pass condition.

The replacement P31 package MUST therefore replace the old executor-specific corroboration rule with the accepted v0.2 contract.

### Fresh EC-PFC01 required observation

A future P32 occurrence must establish before mutation:

```yaml
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
package_id: <new exact package id>
package_ref: <new exact executable package ref>
package_materialization_ref: <same-repository durable locator>
task_anchor:
  revision: 2fec701cc38bb0d9bcb558d8802d0c7f012f408a
  relation: ancestor
actual_starting_revision: <exact observed revision>
execution_surface: CODE_EXECUTION
executor_provenance: <actual executor/client/adapter>
capabilities_used:
  - exact repository resolution
  - exact package materialization resolution
  - immutable revision/ancestry inspection
  - authorized file mutation
  - test execution
  - durable result materialization
```

The pass condition is exact repository/package/task binding plus reviewer-resolvable evidence and fail-closed behavior. Executor identity is mandatory provenance, but the generic requirement does not demand `executor == Codex`.

The following are never acceptable provenance substitutes:

- branch name, including `codex/...`;
- assistant prose;
- an execution handoff claim;
- ambient cwd/session repository;
- a bare SHA that also happens to resolve in another repository.

### Fresh EC-PFC02 required observation

A future P32 must demonstrate that local filesystem/worktree/stdout artifacts remain staging only. Review readiness is not claimed until the exact result/evidence is materialized at a reviewer-resolvable durable boundary.

`EC-PFC03` remains a fresh exact-provider applicability/completion requirement for the repaired result. `EC-PFC04` remains exclusively future `CONTROL_REVIEW` / P34-owned.

---

## 4. Contract delta B — inherited release-evidence applicability

### Repository reality

The preserved VP-I03 result exposed two different release-related states that must not be conflated:

1. `v0.2.0-beta.1` is now historical publication state with an immutable publication source; its tag resolves to exact commit `3253abced7a17d66d8754fa84d7953408aae49d4`.
2. the current VP-I03 candidate is explicitly non-release work and is not authorized to mutate release manifests, tags, GitHub Releases, or published Plugin payloads.

The generic Skillset workflow currently applies current-tree release-manifest rendering to a non-release candidate. That is the inherited applicability defect accepted by P20 v0.2.

The repository's actual release workflow already performs strict active-release candidate coherence against the exact release candidate. It is therefore preserved and excluded from this repair.

### P30 decision

For non-release VP-I03 qualification:

- historical `v0.2.0-beta.1` identity must be checked against its exact historical source/materialization;
- a later legitimate Skill change must not recompute historical expected bytes from the later candidate tree;
- the legacy `0.1.0-task6.1` development/test-distribution snapshot is not an active release claim for VP-I03 and MUST NOT be used as a current-candidate release-coherence Gate;
- actual active release candidates continue to fail closed through the existing exact release workflow and the new `EC-AP02` probe;
- no release manifest, tag, GitHub Release, or published Plugin payload may be edited to make VP-I03 green.

---

## 5. Exact P32 repair authored scope

Authorization mode for the replacement package:

```yaml
authorization_mode: EXACT_PATH_SET
expected_repair_changed_path_count: 6
```

### Modify exactly these five paths

```text
.github/workflows/skillset.yml
.github/workflows/verification-productization-ecv0.yml
tests/skillset/test_control_plane_v02_release_candidate.py
tests/verification_productization/ecv0_fixtures.py
tests/verification_productization/run_ecv0.py
```

### Create exactly this one path

```text
tests/verification_productization/test_ecv0_applicability.py
```

### Explicitly excluded from authored mutation

```text
tools/aegis_proof/**
tools/aegis_control/**
tools/aegis_state/**
tools/aegis_skillset/**
skillset/shared/**
skillset/skills/**
skills/**
plugins/aegis/**
.agents/plugins/**
.aegis/**
skillset/releases/**
docs/releases/**
.github/workflows/release.yml
all other .github/workflows/**
scripts/**
tests/control_plane/**
tests/project_state/**
all other tests/skillset/**
all other tests/verification_productization/**
```

If implementation evidence proves one of the six paths is insufficient to express the accepted v0.2 contract, P32 MUST stop with a scope/package blocker. It may not widen scope on its own.

---

## 6. File-by-file repair plan

### 6.1 `tests/verification_productization/test_ecv0_applicability.py` — create

Add the two mandatory inherited-evidence applicability probes as executable tests.

#### `EC-AP01 — Historical release remains source-bound on non-release candidate`

Fixture requirements:

- historical release version `0.2.0-beta.1`;
- exact historical publication source `3253abced7a17d66d8754fa84d7953408aae49d4`;
- a later non-release candidate whose canonical/generated Skill bytes differ legitimately;
- candidate scope with release/tag/manifest publication disabled.

Oracle requirements:

- resolve the historical release from the historical source/materialization;
- prove the candidate did not mutate that historical occurrence;
- do not regenerate the historical expected manifest from later candidate Skill bytes;
- required result is PASS when history is intact.

The test must fail against the old current-tree-coupled applicability model before the repair is accepted.

#### `EC-AP02 — Active release candidate mismatch still fails closed`

Fixture requirements:

- an explicitly release-applicable candidate;
- a manifest/artifact identity that does not match that candidate's exact release bytes.

Oracle requirements:

- apply candidate release coherence to the exact candidate source/materialization;
- required result is FAIL/BLOCKED;
- historical publication evidence may not excuse the active candidate mismatch.

This probe proves the applicability repair did not weaken real release safety.

### 6.2 `tests/verification_productization/ecv0_fixtures.py` — modify

Add exact applicability fixture identities and deterministic helpers required by `EC-AP01/02` without renumbering or changing `EC-S01..17` or `EC-M01..17`.

The applicability set is a separate two-record family:

```text
EC-AP01
EC-AP02
```

No generic mutation-testing framework is introduced.

### 6.3 `tests/verification_productization/run_ecv0.py` — modify

Extend structured ECV0 materialization with applicability records and a derived summary.

Required shape extension:

```json
{
  "profile": "ECV0",
  "source_revision": "<exact runtime-resolved revision>",
  "scenario_records": [],
  "mutant_records": [],
  "applicability_records": [
    {"id": "EC-AP01", "verdict": "PASS"},
    {"id": "EC-AP02", "verdict": "PASS"}
  ],
  "derived_summary": {
    "scenario_required": 17,
    "scenario_pass": 17,
    "mutant_required": 17,
    "mutant_detected": 17,
    "mutant_false_acceptance": 0,
    "applicability_required": 2,
    "applicability_pass": 2,
    "applicability_fail": 0
  }
}
```

The runner must derive counts from exact records and exit nonzero on missing/duplicate/unexpected IDs or failed thresholds.

### 6.4 `tests/skillset/test_control_plane_v02_release_candidate.py` — modify

Replace the inherited test behavior that compares historical `0.2.0-beta.1` expected bytes against the **current candidate tree**.

The repaired test must instead establish the historical source binding and verify the historical manifest/materialization against that exact source. It must preserve exact release version/tag/source identity and must not rewrite the historical manifest.

The test must remain fail-closed when the historical source, manifest, or protected materialization actually drifts.

### 6.5 `.github/workflows/skillset.yml` — modify

Repair inherited applicability while retaining existing Skillset integrity coverage.

Required changes:

1. stop treating the legacy `0.1.0-task6.1` development/test-distribution snapshot as an active release-coherence requirement for arbitrary non-release candidates;
2. replace current-candidate `0.2.0-beta.1` manifest rendering with an exact historical-source check:
   - fetch `refs/tags/v0.2.0-beta.1`;
   - require tag target `3253abced7a17d66d8754fa84d7953408aae49d4`;
   - materialize that historical source into an isolated directory;
   - run the manifest verification against the historical root, not the current VP-I03 tree;
3. retain the existing immutable beta.3 historical source check;
4. retain native Plugin payload/history validation;
5. retain current candidate Skill generation/distribution/routing/installed-platform/corpus/regression coverage;
6. retain candidate-only installation/parity artifacts as non-publication evidence;
7. never mutate a release manifest or publish a release.

The active release workflow is not modified by this package.

### 6.6 `.github/workflows/verification-productization-ecv0.yml` — modify

Required changes:

- checkout enough exact repository history for the source-bound applicability probe to resolve the historical tag/source (`fetch-depth: 0` or equivalent exact fetch);
- ensure the repaired applicability tests execute as part of the Verification Productization suite;
- ensure affected repair paths trigger the ECV0 workflow where needed;
- preserve full Control Plane, Project State, Skillset, Skill generation/distribution, candidate Plugin parity, structured evidence, and exact artifact upload behavior;
- preserve final fail-closed enforcement when any applicable inherited regression is red.

The workflow must not self-issue P34 PASS.

---

## 7. TDD execution sequence for future P32

### Task 1 — RED: reproduce applicability defect and release-safety counterexample

1. add `EC-AP01` and `EC-AP02` tests;
2. make the historical-source test explicitly distinguish current candidate bytes from historical release bytes;
3. run focused tests and capture expected RED against the unrepaired inherited logic.

Focused commands:

```bash
python3 -m unittest \
  tests.verification_productization.test_ecv0_applicability \
  tests.skillset.test_control_plane_v02_release_candidate -v
```

Expected RED basis:

- old historical beta.1 oracle is current-tree coupled;
- AP02 must demonstrate that a release-applicable mismatch is still rejected.

### Task 2 — GREEN: repair inherited release applicability

Modify only the authorized Skillset test/workflow and ECV0 fixture/test surfaces.

Run:

```bash
python3 -m unittest \
  tests.verification_productization.test_ecv0_applicability \
  tests.skillset.test_control_plane_v02_release_candidate -v
```

Required:

```yaml
EC_AP01: PASS
EC_AP02: PASS
historical_beta1_source_binding: PASS
release_manifest_mutation: false
```

### Task 3 — structured ECV0 materialization

Update the runner and rerun:

```bash
python3 tests/verification_productization/run_ecv0.py \
  --output artifacts/ecv0/ecv0.json
python3 -m json.tool artifacts/ecv0/ecv0.json >/dev/null
```

Required derived profile:

```yaml
deterministic_scenarios:
  required: 17
  pass: 17
  fail: 0
mutant_qualification:
  required: 17
  detected: 17
  false_acceptance: 0
inherited_evidence_applicability:
  required: 2
  pass: 2
  fail: 0
```

### Task 4 — full exact-result qualification

Run the full applicable local suites:

```bash
python3 -m unittest discover -s tests/verification_productization -v
python3 -m unittest discover -s tests/control_plane -v
python3 -m unittest discover -s tests/project_state -v
python3 -m unittest discover -s tests/skillset -v
python3 scripts/build_skillset.py --check
python3 scripts/validate_generated_skills.py
python3 -m tools.aegis_skillset.cli validate .
python3 -m tools.aegis_skillset.cli routing-check .
python3 -m tools.aegis_skillset.cli distribution-check .
python3 -m tools.aegis_state.cli validate .
python3 -m tools.aegis_state.cli check .
python3 evals/scripts/validate_corpus.py
python3 -m unittest discover -s evals/tests -v
python3 scripts/build_candidate_plugin_parity.py \
  --output artifacts/ecv0/candidate-plugin-parity.json
python3 -m json.tool artifacts/ecv0/candidate-plugin-parity.json >/dev/null
```

Do **not** use current-candidate `python3 scripts/build_aegis_distributions.py --version 0.2.0-beta.1 --check` as a non-release VP-I03 pass condition. Historical beta.1 verification must operate on the exact historical source.

Then obtain a fresh exact GitHub Actions ECV0 occurrence for the repaired exact result. P32 may return exact provider refs, but it cannot self-grant `EC-PFC03` before terminal applicability is established and cannot grant `EC-PFC04` at all.

---

## 8. Fresh platform corroboration after repair

A new P32/requalification occurrence must satisfy:

```text
EC-PFC01 Repository-backed execution-surface exact package preflight
EC-PFC02 Execution/local evidence durability boundary
EC-PFC03 GitHub Actions exact-result + terminal/completion applicability
EC-PFC04 CONTROL_REVIEW independent resolution
```

Disposition:

- `EC-PFC01`: fresh, executor-agnostic, exact repository/package/task preflight; actual executor provenance mandatory;
- `EC-PFC02`: fresh durability observation; local-only evidence accepted = 0;
- `EC-PFC03`: fresh hosted provider evidence for the exact repaired result; wrong-revision/incomplete/failed provider result is not PASS;
- `EC-PFC04`: remains pending until future P34 `CONTROL_REVIEW` independently resolves the exact graph.

The prior PR #77 occurrence is not relabeled to satisfy any of these repaired obligations.

---

## 9. Exact scope and historical immutability checks

Before P32 completion, compare the new result against the replacement package ref and prove exactly the six authorized authored paths changed.

Also prove no path under the following changed:

```text
skillset/releases/**
plugins/aegis/**
.agents/plugins/**
.aegis/**
.github/workflows/release.yml
tools/aegis_proof/**
skillset/skills/**
skills/**
```

The preserved PR #77 exact result remains the ancestry root for the repair. No force-push or history rewrite of PR #77 is authorized.

---

## 10. P30 exit criteria

P30 is READY for replacement P31 packaging when all are true:

1. ECV0 v0.2 exact basis `4d5ef43...` + P21 review `5121845074` is frozen;
2. valid PR #77 implementation/evidence is explicitly preserved;
3. Repair A is confined to replacement package execution/corroboration semantics rather than unnecessary runtime redesign;
4. Repair B has an exact six-path implementation scope;
5. `EC-AP01` and `EC-AP02` have executable locations and fail-closed oracles;
6. historical beta.1 is source-bound, while active release safety remains strict;
7. `0.1.0-task6.1` non-release snapshot is not misapplied as an active release Gate;
8. release manifests/tags/Releases/Plugin payloads and `.github/workflows/release.yml` remain excluded;
9. full local and hosted qualification commands are explicit;
10. P34 ownership remains independent and no prior evidence is retroactively upgraded.

---

## 11. P30 disposition

```yaml
P30_targeted_reconciliation:
  task: VP-I03_ECV0_V0_2_REPAIR
  repository: Mostorm-Labs/aegis
  preserved_result: 2fec701cc38bb0d9bcb558d8802d0c7f012f408a

  replacement_verification_basis: 4d5ef43f0879a4ce45aeae0367d6f11187f29b61
  replacement_p21_review: 5121845074

  repair_A:
    implementation_change_required: false
    package_contract_change_required: true
    fresh_requalification_required: true

  repair_B:
    authored_path_count: 6
    historical_release_source_bound: true
    active_release_safety_weakened: false

  release_state_mutation_authorized: false
  current_authority_publication_authorized: false
  p34_authorized_now: false

  status: READY_FOR_TARGETED_P31
  next_stage: P31_TASK_PACKAGING
  next_owner: aegis-implementation
```

P30 stops at planning. The subsequent P31 package must be a new immutable package descendant of the preserved result; it must not edit or reinterpret `VP-I03-P31-01` in place.