# VP-I03-P31-02 — ECV0 v0.2 Targeted Repair Package

Status: **P31 / CONTROL_REASONING / MATERIALIZED — READY FOR EXPLICIT P32 START**

This is the replacement executable package for the targeted VP-I03 repair required by accepted ECV0 v0.2. It preserves the existing VP-I03 implementation result and authorizes only the minimum test/workflow repair needed to close the two earlier contract defects exposed by the blocked P32 occurrence.

It does **not** start P32, issue P34 PASS, merge PR #77/#78/#79, publish Current Authority, mutate release publication state, rewrite historical evidence, or create a release.

The shell commit `3f311d288d1a4b09f2d3be77907f16105736ed6a` is NON-EXECUTABLE materialization history and MUST NOT be used as `package_ref`.

---

## 1. Package identity

```yaml
package_id: VP-I03-P31-02
slice_id: VP-I03
name: ECV0_V0_2_TARGETED_REPAIR_AND_FRESH_REQUALIFICATION
stage_owner: aegis-implementation
stage: P31_TASK_PACKAGING
execution_surface_now: CONTROL_REASONING
future_execution_surface: CODE_EXECUTION

repository:
  provider: github
  full_name: Mostorm-Labs/aegis

source_commit: 2fec701cc38bb0d9bcb558d8802d0c7f012f408a
source_frontname: codex/verification-productization-vp-i03-implementation
source_retrieved_at: 2026-09-05T15:41:11Z

package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/79
package_document: docs/verification-productization-vp-i03-task-package-v0.2.md

p30_plan_ref: ca29996c44704f62446b9471bd2310cf37bc6c56
p30_plan_document: docs/verification-productization-vp-i03-v0.2-reconciliation-plan.md

task_anchor:
  revision: 2fec701cc38bb0d9bcb558d8802d0c7f012f408a
  relation: ancestor

resume_cursor: null
```

The exact executable `package_ref` is the final Git commit containing this document and is recorded externally by PR #79 after materialization. The package does not embed the future-self SHA of its own containing commit.

Future P32 MUST resolve, in order:

1. repository `github / Mostorm-Labs/aegis`;
2. same-repository package materialization PR #79;
3. the exact externally supplied final `package_ref` for this document;
4. `task_anchor` ancestry to the preserved implementation result;
5. actual starting revision and any delta from the exact package ref.

If the repository, package materialization, package ref, or anchor relation cannot be established exactly, return fail-closed before mutation.

---

## 2. Exact Authority / predecessor basis

```yaml
authority_refs:
  semantic_basis: 12c968c5c481ad671ce33bcfa088ba8a2fca0f43
  p14_architecture_basis: d9c8f6ac5db4359400fae06e76c51c65bd059bfc
  p15_module_basis: 665292dcfd7781935243369ee9f676c320f2878a
  p16_runtime_flow_basis: 708cf09c01effbcc63c65d45b9b4a67b7a8fc8db
  p17_platform_basis: c8f47d049be50d65f88b04ad141650ed6dfdb826

  prior_p20_basis: 674e01737621621b8131e35f83313fb0154a9f6d
  prior_p21_review: 5121075377

  replacement_p20_basis: 4d5ef43f0879a4ce45aeae0367d6f11187f29b61
  replacement_p21_review: 5121845074
  replacement_p21_verdict: PASS
  replacement_p21_disposition: ACCEPTED_FOR_DOWNSTREAM

  p30_targeted_reconciliation: ca29996c44704f62446b9471bd2310cf37bc6c56
```

The prior P20/P21 basis remains historical predecessor Authority. The replacement P20/P21 basis governs this package downstream; it is not silently published as Current `.aegis` Authority.

### Prior VP-I03 package and blocked result

```yaml
predecessor_package:
  package_id: VP-I03-P31-01
  package_ref: a3dd0f1aa08f2686b9169059799555cd597ca503
  materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/76

preserved_result:
  result_revision: 2fec701cc38bb0d9bcb558d8802d0c7f012f408a
  materialized_ref: https://github.com/Mostorm-Labs/aegis/pull/77
  p32_return_review: 5121781308
  central_routing_review: 5121799448
  status: BLOCKED_AUTHORITY
```

### Accepted VP-I01 predecessor

```yaml
vp_i01:
  result_revision: ef995501c3dcd1f7f608083028f43bb4bde66103
  p34_gate_review: 5121366259
  p34_verdict: PASS
  governing_package_id: VP-I01-P31-02
  governing_package_ref: b979f1fc59178c16285449a92f02dd5964e523d0
```

### Accepted VP-I02 predecessor

```yaml
vp_i02:
  result_revision: 8b98a58874268a8d6fae05d0406bd795a311f041
  p34_gate_review: 5121578992
  p34_verdict: PASS
  governing_package_id: VP-I02-P31-01
  governing_package_ref: 9a724830992d27681b223c8b424891e46623aeed
  p36_evidence_ref: 3f6e51fd9364793eb4694c0a9ba56c4366b14231
```

No VP-I01/VP-I02 semantics or implementation is reopened by this package.

---

## 3. Preserved implementation/evidence reality

The existing VP-I03 result already established reusable predecessor evidence:

```yaml
verification_productization_tests: 83/83_OK
EC_S01_to_EC_S17: 17/17_PASS
EC_M01_to_EC_M17: 17/17_DETECTED
mutant_false_acceptance: 0

github_actions:
  run: 33973747955
  job: 101326724541
  artifact: 9971689270
  artifact_digest: sha256:6e5784c103d7870adc19c35012bb96791a9e772d2da0ac3c7888762bd08aea59
```

P32 MUST preserve this implementation reality and modify only the exact repair scope below.

The old occurrence remains historically blocked. This package does not grant:

```yaml
revised_EC_PFC01: NOT_RETROACTIVELY_GRANTED
EC_PFC03: NOT_RETROACTIVELY_GRANTED
EC_PFC04: STILL_PENDING_FUTURE_CONTROL_REVIEW
prior_failed_workflow_run: HISTORICAL_FAILURE_PRESERVED
P34_PASS: false
```

A fresh exact result/requalification occurrence is mandatory.

---

## 4. Purpose and bounded repair contract

This package closes only the two accepted v0.2 deltas:

```text
Repair A
  executor-specific EC-PFC01/02 corroboration
  -> repository-backed CODE_EXECUTION exact preflight
     with actual executor provenance

Repair B
  historical release oracle applied to unrelated current candidate bytes
  -> source-bound historical publication verification
     + explicit active-candidate release applicability
```

It does not add a new verification product, daemon, service, proof object family, generic mutation framework, release mechanism, or Gate owner.

---

## 5. Exact authored write scope

```yaml
authorization_mode: EXACT_PATH_SET
expected_authored_changed_path_count: 6
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

Any required authored mutation outside these six paths is a package/scope blocker and MUST return to `aegis-implementation` rather than being added inside P32.

### Explicit negative write scope

P32 MUST NOT author changes under:

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

No generated `skills/**` output is expected from this repair because canonical Skill source is not in the authored scope. If any command changes generated Skill bytes, stop and return a scope blocker.

---

## 6. Repair A — fresh executor-agnostic platform corroboration

This is primarily a package/evidence obligation, not a new repository implementation change.

### EC-PFC01 — required P32 preflight

Before any mutation, future P32 MUST durably establish:

```yaml
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
package_id: VP-I03-P31-02
package_ref: <exact-final-P31-02-containing-commit>
package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/79
task_anchor:
  revision: 2fec701cc38bb0d9bcb558d8802d0c7f012f408a
  relation: ancestor
actual_starting_revision: <exact-observed-revision>
execution_surface: CODE_EXECUTION
executor_provenance: <actual executor/client/adapter identity>
capabilities_used:
  - exact repository resolution
  - same-repository package resolution
  - immutable revision and ancestry inspection
  - authorized file mutation
  - command/test execution
  - durable result materialization
```

An authorized Codex surface, ChatGPT repository connector, or another future repository-backed CODE_EXECUTION executor may satisfy the contract if it proves these exact semantics/capabilities.

The following never satisfy executor provenance or package preflight by themselves:

```text
branch name
assistant prose
handoff claim
ambient cwd/session repository
bare SHA
PR title
executor memory
```

If the observed starting revision differs from the exact package ref, P32 must compare the package ref to the observed revision before mutation. Any unexplained or unauthorized descendant delta is `BLOCKED_EXECUTION_DIVERGENCE`; `resume_cursor` is null and no interrupted repair work has been accepted yet.

### EC-PFC02 — durability boundary

Local-only report/test/worktree/stdout state remains staging. P32 MUST NOT claim review readiness until the exact repaired result and required evidence are materialized at reviewer-resolvable durable refs.

### EC-PFC03 / EC-PFC04

- `EC-PFC03`: must come from a fresh exact repaired-candidate hosted provider occurrence and terminal applicability/completion evidence. A failed or incomplete run is not PASS.
- `EC-PFC04`: remains exclusively future CONTROL_REVIEW/P34-owned. P32 MUST NOT emit or imply it.

---

## 7. Repair B — exact implementation requirements

### 7.1 Historical beta.1 source binding

The package freezes:

```yaml
historical_release:
  version: 0.2.0-beta.1
  tag: v0.2.0-beta.1
  exact_publication_source: 3253abced7a17d66d8754fa84d7953408aae49d4
```

For this non-release VP-I03 candidate, historical release verification must evaluate the historical source/materialization, not re-render expected release bytes from the current repair tree.

`skillset/releases/aegis-0.2.0-beta.1.json`, the tag, GitHub Release, and published Plugin payload are immutable inputs and outside write scope.

### 7.2 Legacy development/test snapshot applicability

`skillset/releases/aegis-0.1.0-task6.1.json` has no corresponding release tag and is not an active release claim for this VP-I03 repair. The generic Skillset qualification must not fail a non-release candidate merely because current Skill bytes do not reproduce that legacy development/test-distribution snapshot.

The file remains immutable during P32. This package does not authorize rewriting it to current bytes.

### 7.3 Active release safety

`.github/workflows/release.yml` remains outside scope and unchanged. Its exact-candidate manifest/archive/plugin coherence checks remain the production release boundary.

A real release mismatch must still fail closed; `EC-AP02` explicitly proves that negative side of the applicability rule.

---

## 8. Required file-level changes

### `.github/workflows/skillset.yml`

P32 must:

1. remove the legacy `0.1.0-task6.1` current-tree manifest equality from the generic non-release pass conditions;
2. replace current-tree `0.2.0-beta.1` manifest equality with exact historical-source validation;
3. fetch `refs/tags/v0.2.0-beta.1` and assert the commit is exactly `3253abced7a17d66d8754fa84d7953408aae49d4`;
4. materialize the historical source in an isolated directory and run release-manifest verification against that historical tree;
5. preserve the existing `v0.1.0-beta.3` historical binding check;
6. preserve native Plugin payload/history validation, current candidate Skill generation/distribution checks, routing/installed-platform checks, Project State, corpus, eval regressions, and candidate parity artifacts;
7. do not write release state.

### `tests/skillset/test_control_plane_v02_release_candidate.py`

Replace `test_public_release_identity_is_coherent` current-tree coupling with a source-bound historical release test.

The repaired test must fail if the exact historical source cannot be resolved, the historical manifest/materialization actually drifts, or the wrong publication source is used.

### `tests/verification_productization/ecv0_fixtures.py`

Add a separate applicability fixture family with exactly:

```text
EC-AP01
EC-AP02
```

Do not renumber or alter `EC-S01..17` or `EC-M01..17`.

### `tests/verification_productization/test_ecv0_applicability.py`

Create executable probes:

- `EC-AP01`: later non-release candidate Skill-byte change does not retarget the historical release oracle; intact historical source/materialization passes;
- `EC-AP02`: release-applicable exact candidate with manifest/artifact mismatch is rejected.

### `tests/verification_productization/run_ecv0.py`

Extend structured evidence with `applicability_records` and derived `applicability_required/pass/fail`. Missing, duplicate, unexpected, or failed applicability IDs must make the runner nonzero.

### `.github/workflows/verification-productization-ecv0.yml`

P32 must:

- make exact historical source resolution possible (`fetch-depth: 0` or equivalent exact fetch);
- run the repaired applicability tests as part of the suite;
- include the affected repair surfaces in workflow triggering where necessary;
- preserve full inherited regressions and exact candidate evidence upload;
- keep fail-closed full qualification enforcement.

---

## 9. Test-first execution contract

A future P32 MUST use TDD for the repair.

### RED checkpoint

Before making the inherited workflow/oracle green, materialize tests that demonstrate:

1. old historical beta.1 current-tree coupling falsely blocks a legitimate non-release candidate;
2. a real release-applicable mismatch still fails.

Run:

```bash
python3 -m unittest \
  tests.verification_productization.test_ecv0_applicability \
  tests.skillset.test_control_plane_v02_release_candidate -v
```

Record the RED transcript as local staging evidence, then proceed only within the six authorized paths.

### Focused GREEN checkpoint

Rerun the same command until:

```yaml
EC_AP01: PASS
EC_AP02: PASS
historical_beta1_source_binding: PASS
active_release_mismatch_false_acceptance: 0
```

### Structured evidence checkpoint

```bash
mkdir -p artifacts/ecv0
python3 tests/verification_productization/run_ecv0.py \
  --output artifacts/ecv0/ecv0.json
python3 -m json.tool artifacts/ecv0/ecv0.json >/dev/null
```

Required exact profile:

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

---

## 10. Full local qualification commands

At the exact repaired result, run:

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

python3 tests/verification_productization/run_ecv0.py \
  --output artifacts/ecv0/ecv0.json
python3 -m json.tool artifacts/ecv0/ecv0.json >/dev/null

python3 scripts/build_candidate_plugin_parity.py \
  --output artifacts/ecv0/candidate-plugin-parity.json
python3 -m json.tool artifacts/ecv0/candidate-plugin-parity.json >/dev/null
```

Do **not** use either of these as a current VP-I03 candidate pass condition:

```bash
python3 scripts/build_aegis_distributions.py --check
python3 scripts/build_aegis_distributions.py --version 0.2.0-beta.1 --check
```

when they are pointed at the current non-release candidate tree. Historical beta.1 verification must be executed against its exact historical source.

No command in this package may write a release manifest or published Plugin payload.

---

## 11. Exact authored-scope verification

Before result materialization, compare the final repaired result against the exact P31 package ref.

The changed authored path set MUST equal exactly:

```text
.github/workflows/skillset.yml
.github/workflows/verification-productization-ecv0.yml
tests/skillset/test_control_plane_v02_release_candidate.py
tests/verification_productization/ecv0_fixtures.py
tests/verification_productization/run_ecv0.py
tests/verification_productization/test_ecv0_applicability.py
```

Required negative count:

```yaml
unauthorized_changed_paths: 0
release_manifest_changed_paths: 0
published_plugin_changed_paths: 0
canonical_skill_changed_paths: 0
generated_skill_changed_paths: 0
release_workflow_changed_paths: 0
```

If the exact set differs, do not self-expand the package. Return `BLOCKED_SCOPE` / package reconciliation evidence.

---

## 12. Hosted exact-result requalification

After the six-path result is materialized on a new implementation branch/PR, obtain a fresh GitHub Actions occurrence for the exact result.

Required evidence navigation includes, at minimum:

```yaml
result_revision: <exact repaired commit>
materialized_ref: <reviewer-resolvable PR/ref>
provider:
  repository: Mostorm-Labs/aegis
  workflow: Aegis Verification Productization ECV0
  run_id: <exact>
  run_attempt: <exact>
  required_job_ids:
    - <exact>
  artifact_id: <exact>
  artifact_digest: <exact if exposed>
  source_revision: <exact repaired commit>
```

P32 may return these exact refs after the run is terminal. It MUST preserve a failed provider occurrence as failure rather than claiming `EC-PFC03` from green local tests.

`EC-PFC04` is not obtainable in P32 and remains pending for future P34 CONTROL_REVIEW.

---

## 13. Expected outputs

A successful future P32 produces:

```yaml
expected_outputs:
  - exact repaired result commit descended from this package ref
  - reviewer-resolvable implementation PR/ref
  - exactly six authored changed paths
  - TDD RED evidence for applicability defect
  - focused GREEN evidence
  - ECV0 structured artifact with 17/17 scenarios
  - ECV0 structured artifact with 17/17 mutants and false_acceptance 0
  - ECV0 structured artifact with 2/2 applicability probes
  - candidate Plugin parity evidence
  - full inherited regression results
  - fresh EC-PFC01 provenance/preflight evidence
  - fresh EC-PFC02 durability evidence
  - fresh exact hosted provider run refs for EC-PFC03 assessment
```

No expected output is a P34 verdict.

---

## 14. Artifact and evidence rules

```yaml
artifact_rules:
  local_worktree_paths: staging_only
  stdout_transcripts: staging_only
  exact_result_materialization_required: true
  reviewer_resolvable_refs_required: true
  exact_provider_identity_required: true
  signed_or_temporary_urls_as_identity: forbidden
  assistant_summary_as_evidence_source: forbidden
  copied_proof_totals_as_second_source: forbidden
  branch_name_as_executor_provenance: forbidden
  prior_result_retroactive_relabeling: forbidden
```

The fresh execution return should navigate to evidence objects rather than re-authoring their machine facts.

---

## 15. Negative prohibitions

```yaml
negative_prohibitions:
  modify_PR_77_history: false
  rewrite_predecessor_package: false
  mutate_release_manifest: false
  mutate_release_tag: false
  mutate_github_release: false
  mutate_published_plugin: false
  modify_release_workflow: false
  modify_proof_runtime: false
  modify_canonical_skills: false
  modify_generated_skills: false
  expand_beyond_6_authored_paths: false
  infer_executor_from_branch_name: false
  treat_executor_brand_as_generic_pass_condition: false
  use_current_candidate_bytes_as_historical_release_truth: false
  waive_active_release_mismatch: false
  claim_EC_PFC04_in_P32: false
  claim_P34_PASS_in_P32: false
  merge: false
  publish_current_authority: false
  release: false
  rollout_expansion: false
```

`false` above means the action is not authorized / must not occur.

---

## 16. Blocked return rules

P32 must stop and return exact blocker evidence when any of these occurs:

```yaml
BLOCKED_REPOSITORY_IDENTITY:
  - repository/package materialization cannot be exactly resolved

BLOCKED_EXECUTION_DIVERGENCE:
  - unexpected delta exists after package_ref before execution

BLOCKED_SCOPE:
  - accepted repair requires a seventh authored path
  - generated/canonical/release paths would need mutation

BLOCKED_AUTHORITY:
  - implementation would require weakening active release safety
  - implementation would need to reinterpret P17 or P20 v0.2

BLOCKED_EVIDENCE:
  - exact result cannot be durably materialized
  - required provider evidence is unavailable/incomplete
```

Do not patch Authority from P32.

---

## 17. P32 completion threshold

A result may return from P32 as ready for future independent review only when all are true:

```yaml
repository_preflight_exact: true
package_preflight_exact: true
actual_executor_provenance_recorded: true

changed_paths_exactly_6: true
unauthorized_changed_paths: 0

EC_S01_to_EC_S17: 17/17_PASS
EC_M01_to_EC_M17: 17/17_DETECTED
mutant_false_acceptance: 0
EC_AP01_to_EC_AP02: 2/2_PASS

full_verification_productization_suite: PASS
full_control_plane_regressions: PASS
full_project_state_regressions: PASS
full_skillset_regressions: PASS
skill_generation_distribution_checks: PASS
project_state_checks: PASS
corpus_eval_regressions: PASS
candidate_plugin_parity: PASS

historical_beta1_source_binding: PASS
historical_release_mutation: 0
active_release_safety_weakened: false

EC_PFC01: fresh_evidence_available
EC_PFC02: fresh_evidence_available
EC_PFC03: exact_terminal_provider_refs_available_for_independent_resolution
EC_PFC04: PENDING_CONTROL_REVIEW

result_materialized: true
P34_PASS: false
```

Provider success does not become P34 PASS. P34 remains a separate Primary owned by `aegis-gate-review`.

---

## 18. Future execution handoff requirements

This package is materialized for a future explicit P32 start. A future `surface_handoff` must carry:

```yaml
type: surface_handoff
stage: P32
stage_owner: aegis-implementation
from_surface: CONTROL_REASONING
to_surface: CODE_EXECUTION
reason: VP-I03_ECV0_V0_2_TARGETED_REPAIR
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
package_id: VP-I03-P31-02
package_ref: <exact final commit containing this document>
package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/79
task_anchor:
  revision: 2fec701cc38bb0d9bcb558d8802d0c7f012f408a
  relation: ancestor
resume_cursor: null
return_surface: CONTROL_REASONING
```

If a preferred executor is selected in that future handoff, its identity is profile/rendering metadata and must be separately recorded as actual executor provenance by the execution occurrence. It is not lifecycle Authority and not the generic EC-PFC01 pass condition.

---

## 19. P31 disposition

```yaml
P31_package:
  package_id: VP-I03-P31-02
  repository: Mostorm-Labs/aegis
  package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/79

  preserved_result_anchor: 2fec701cc38bb0d9bcb558d8802d0c7f012f408a
  replacement_p20_basis: 4d5ef43f0879a4ce45aeae0367d6f11187f29b61
  replacement_p21_review: 5121845074
  p30_plan_ref: ca29996c44704f62446b9471bd2310cf37bc6c56

  authored_write_scope_count: 6
  release_mutation_authorized: false
  p34_started: false
  p32_started: false

  status: READY_FOR_EXPLICIT_P32_START
  next_owner: aegis-implementation
  next_stage: P32_IMPLEMENTATION_REQUALIFICATION
```

Stop after P31 materialization. Do not automatically execute P32, P34, merge, Authority publication, or release.