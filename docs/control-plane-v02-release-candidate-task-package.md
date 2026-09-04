# Aegis Control Plane v0.2 — P31 Release-Candidate Task Package

Status: **P31 READY / MATERIALIZED — release-package-only execution contract**

Package ID: `RC-I01-P31-01`

Task ID: `RC-I01`

Primary Owner: `aegis-implementation`

Preferred execution surface: `CODE_EXECUTION / Codex`

Review return: `CONTROL_REVIEW -> aegis-governance / P24_RELEASE_READINESS_REREVIEW`

This package authorizes only the materialization of the already Gate-accepted Aegis Control Plane v0.2 as a coherent prerelease Plugin + exact-nine Skills release candidate. It does not authorize any new Control Plane semantics, a P34 rerun, publication, rollout expansion, or SERVICE_PROFILE work.

---

## 1. Task identity

```yaml
package_id: RC-I01-P31-01
task_id: RC-I01
purpose: CONTROL_PLANE_V02_RELEASE_CANDIDATE_MATERIALIZATION
primary_owner: aegis-implementation
preferred_code_executor: codex
review_return_surface: CONTROL_REVIEW
final_review_owner: aegis-governance
final_review_stage: P24_RELEASE_READINESS_REREVIEW
release_version: 0.2.0-beta.1
release_tag: v0.2.0-beta.1
product_form: PLUGIN_PLUS_EXACT_NINE_SKILLS
implementation_scope: RELEASE_PACKAGE_ONLY
```

---

## 2. Exact trusted basis

### Repository / lifecycle baseline

- current trusted `main`: `212f1d7dcb2c31162f0f64946a4473912578c5d9`
- repository integration closure: PR #54
- post-merge Project State Integrity: `33831680034 = SUCCESS`

### Accepted Control Plane product result

- accepted exact implementation candidate: `18559f32ede7ebd845064fe8de7967ca358b785f`
- P34 review: `5108520468`
- P34 verdict: `PASS / ACCEPTED_FOR_DOWNSTREAM`

### Current Authority

- Current Product Authority is the v0.2 Plugin / exact-nine product boundary recorded in root Project State.
- Current Verification Authority ref: `18b374e95057bafd0feac3ca16e7aca4774a925a`
- `SERVICE_PROFILE = NOT_AUTHORIZED`
- rollout remains `DENIED`
- zero-user-turn cross-Primary substantive chaining is not authorized by current composition Authority.

### P24 blocker that this package closes

- durable P24 record: PR #54 comment `5535084263`
- disposition: product / Gate / integration accepted; release blocked only because the v0.2 release package has not yet been materialized.

### P30 implementation plan

- P30 ref: `3bd76507522f69714bbd584e287347cdac38f361`
- plan: `docs/superpowers/plans/2026-09-04-control-plane-v02-release-candidate.md`
- slice: `RC-I01 — CONTROL_PLANE_V02_RELEASE_CANDIDATE_MATERIALIZATION`

If any of these trusted facts is contradicted at execution time, stop instead of expanding this package.

---

## 3. Task anchor and execution position

Repository-backed execution MUST use:

```yaml
task_anchor:
  revision: 212f1d7dcb2c31162f0f64946a4473912578c5d9
  relation: ancestor
resume_cursor: null
```

`Task Anchor != Execution Cursor`.

At initial P32 entry there is no previously accepted execution continuation point for `RC-I01-P31-01`, therefore `resume_cursor: null` is correct.

The executor MUST:

1. record the actual starting revision before edits;
2. prove `212f1d7...` is an ancestor of that starting revision;
3. inspect the starting diff/state before modifying files;
4. preserve valid P30/P31 documentation already present on the execution branch;
5. fail closed on incompatible history or out-of-package changes.

A valid descendant of the task anchor is acceptable. Historical HEAD equality is not the execution oracle.

---

## 4. Execution branch / materialization contract

Preferred execution topology:

```text
main@212f1d7...
   -> P30 plan ref 3bd765...
   -> P31 package ref
   -> P32 release-candidate implementation branch / PR
```

The P32 result MUST be pushed to a reviewer-accessible GitHub branch / pull request before returning to review.

Required return fields:

```yaml
result_revision: <exact pushed 40-char commit>
materialized_ref: <reviewer-resolvable GitHub commit or PR ref>
actual_starting_revision: <exact revision inspected before edits>
task_anchor:
  revision: 212f1d7dcb2c31162f0f64946a4473912578c5d9
  relation: ancestor
```

A local-only result is `BLOCKED_EVIDENCE` and cannot be returned as P24-ready evidence.

---

## 5. Authorized public release identity

The package freezes exactly one public identity:

```yaml
release_version: 0.2.0-beta.1
release_tag: v0.2.0-beta.1
release_channel: prerelease
```

Rationale already frozen by P30:

- the product minor line advances from `0.1` to `0.2`;
- this is the first Control Plane v0.2 prerelease;
- no stable `0.2.0` claim is inferred.

Before implementation and again before final materialization, the executor MUST verify that neither the tag nor a GitHub Release named `v0.2.0-beta.1` already exists.

Collision result:

```yaml
status: BLOCKED_RELEASE_IDENTITY_COLLISION
continue_execution: false
```

Do not silently choose `beta.2`, rename the release, move an existing tag, or overwrite an existing Release.

---

## 6. Authorized file scope

### 6.1 Create

```text
tests/skillset/test_control_plane_v02_release_candidate.py
skillset/releases/aegis-0.2.0-beta.1.json
docs/releases/v0.2.0-beta.1.md
docs/installation-and-usage-v0.2.md
```

### 6.2 Modify / regenerate

```text
plugins/aegis/.codex-plugin/plugin.json
plugins/aegis/skills/**
.agents/plugins/marketplace.json
.github/workflows/skillset.yml
README.md
```

`plugins/aegis/skills/**` and `.agents/plugins/marketplace.json` may change only as deterministic output of the existing native Plugin materialization path. Semantic Skill changes are not authorized.

### 6.3 Read/reuse without semantic modification

```text
scripts/build_aegis_distributions.py
scripts/build_openai_plugin_materialization.py
tools/aegis_skillset/package.py
tools/aegis_skillset/plugin_materialization.py
skillset/distribution.json
.github/workflows/release.yml
docs/plugin-distribution-contract-v0.1.md
docs/installation-and-usage-v0.1.md
```

### 6.4 Explicitly out of authored scope

```text
tools/aegis_control/**
tests/control_plane/**
.aegis/**
Control Plane Product / Modeling / Architecture / Verification Authority docs
.github/workflows/release.yml
historical release manifests / historical release notes
```

If implementation needs to edit an out-of-scope semantic surface, stop and return to `aegis` with the earliest untrusted layer rather than extending this package.

---

## 7. Required changes

### RC-I01-A — RED release-identity oracle

Create `tests/skillset/test_control_plane_v02_release_candidate.py` as frozen by the P30 plan.

The test MUST prove at least:

- committed `skillset/releases/aegis-0.2.0-beta.1.json` exists;
- Plugin manifest version equals `0.2.0-beta.1`;
- committed manifest equals `render_release_manifest(ROOT, "0.2.0-beta.1")`;
- Plugin release manifest has exactly nine unique Skill entries;
- release notes, README, and v0.2 installation guide point to `v0.2.0-beta.1`;
- historical beta.3 manifest / notes remain present.

Before creating the release surfaces, run the targeted test and preserve RED evidence.

### RC-I01-B — deterministic release manifest

Generate, do not hand-author:

```bash
python3 scripts/build_aegis_distributions.py \
  --version 0.2.0-beta.1 \
  --write-manifest
```

The generated manifest MUST bind the current canonical exact-nine Skill trees and ZIP digests.

### RC-I01-C — native Plugin materialization

Generate from the committed release identity:

```bash
python3 scripts/build_openai_plugin_materialization.py \
  --release-version 0.2.0-beta.1 \
  --write
```

Required state:

- `plugins/aegis/.codex-plugin/plugin.json.version = 0.2.0-beta.1`;
- exact nine Plugin Skill directories;
- each materialized Skill tree remains byte-equivalent to its canonical `skills/<name>` tree;
- marketplace remains one Aegis Plugin pointing to `./plugins/aegis`;
- no app, owner, routing, or lifecycle semantics are introduced.

### RC-I01-D — v0.2 release notes / installation guidance

Create:

```text
docs/releases/v0.2.0-beta.1.md
docs/installation-and-usage-v0.2.md
```

Update `README.md` current product/release pointers.

Release copy MUST state the accepted claim envelope:

- Control Plane v0.2 is delivered as one Plugin + exact nine Skills;
- durable Authority / state / Gate / resume semantics are part of the product;
- P34 accepted candidate is `18559f32...` / review `5108520468`;
- no standalone daemon / hosted Control Service is required;
- no R0/S0/W7D service-scale claim;
- `SERVICE_PROFILE` remains not authorized;
- rollout remains denied;
- zero-user-turn cross-Primary substantive chaining is not claimed;
- historical PP0 40-WorkScope harness obligations are not v0.2 release requirements under Current Verification Authority;
- `v0.1.0-beta.3` remains the previous immutable rollback / reproducibility boundary.

Do not say the release is already published.

### RC-I01-E — candidate CI binding

Modify only the beta.3 candidate-specific release bindings in `.github/workflows/skillset.yml` to `0.2.0-beta.1`.

Required v0.2 candidate commands / artifact identity:

```yaml
manifest_check: python3 scripts/build_aegis_distributions.py --version 0.2.0-beta.1 --check
plugin_check: python3 scripts/build_openai_plugin_materialization.py --release-version 0.2.0-beta.1 --check
candidate_kit: aegis-skill-installation-kit-0.2.0-beta.1-candidate
candidate_archive: aegis-skill-installation-kit-0.2.0-beta.1.zip
```

Preserve the existing `0.1.0-task6.1` mutable development-oracle path unchanged.

Do not change `.github/workflows/release.yml` publication semantics.

---

## 8. Explicit non-goals / prohibited work

This package does NOT authorize:

- any new Control Plane semantic behavior;
- edits to Product, Modeling, Architecture, Verification, Distribution, or Gate Authority;
- PP0 40-WorkScope harness work;
- seven-oracle PP0 aggregation;
- 32-mutant PP0 self-qualification;
- monolithic PP0 evidence bundle reconstruction;
- a P34 rerun or reinterpretation;
- a new daemon / agent / service / worker topology;
- R0, S0, W7D, completed-month availability, or service-cost qualification;
- SERVICE_PROFILE claims;
- rollout expansion;
- zero-user-turn cross-Primary substantive chaining claims;
- changing stage ownership;
- rewriting `.aegis` Gate / integration history;
- changing historical `v0.1.0-beta.1`, beta.2, or beta.3 release files/tags/assets;
- creating `v0.2.0-beta.1` tag during P32;
- dispatching the release workflow during P32;
- manually creating a GitHub Release;
- merging the P32 release candidate;
- declaring P24 ready/authorized from CI or implementation.

---

## 9. Required test / oracle sequence

### 9.1 RED first

Before the release surfaces exist:

```bash
python3 -m unittest tests.skillset.test_control_plane_v02_release_candidate -v
```

Expected: current-identity assertions fail for the missing v0.2 manifest/docs and/or old Plugin version; historical beta.3 preservation remains true.

If the test unexpectedly passes on the starting state, inspect for untrusted pre-existing release work before continuing.

### 9.2 Generated release identity checks

After manifest / Plugin generation:

```bash
python3 scripts/build_aegis_distributions.py --version 0.2.0-beta.1 --check
python3 scripts/build_openai_plugin_materialization.py --release-version 0.2.0-beta.1 --check
python3 -m tools.aegis_skillset.cli distribution-check .
```

All MUST exit `0`.

### 9.3 Candidate workflow-equivalent checks

```bash
python3 -m tools.aegis_skillset.cli validate .
python3 scripts/build_skillset.py --check
python3 -m tools.aegis_skillset.cli distribution-check .
python3 scripts/build_aegis_distributions.py --check
python3 scripts/build_aegis_distributions.py --version 0.2.0-beta.1 --check
python3 scripts/build_openai_plugin_materialization.py --release-version 0.2.0-beta.1 --check
python3 -m tools.aegis_skillset.cli routing-check .
python3 -m tools.aegis_skillset.cli installed-platform-check .
python3 scripts/validate_generated_skills.py
```

All MUST exit `0`.

### 9.4 Full packaging-regression suite

Before materialization:

```bash
python3 -m unittest discover -s tests/skillset -v
python3 -m unittest discover -s tests/project_state -v
python3 -m unittest discover -s tests/control_plane -v
python3 evals/scripts/validate_corpus.py
python3 -m unittest discover -s evals/tests -v
python3 -m tools.aegis_state.cli validate .
python3 -m tools.aegis_state.cli check .
```

All MUST PASS.

These are regression checks only. They do not create or replace a P34 verdict.

### 9.5 Deterministic Installation Kit

Build:

```bash
rm -rf /tmp/aegis-v02-release-candidate
mkdir -p /tmp/aegis-v02-release-candidate
python3 scripts/build_aegis_distributions.py \
  --version 0.2.0-beta.1 \
  --installation-kit-archive-dir /tmp/aegis-v02-release-candidate
```

Verify:

- embedded release version is `0.2.0-beta.1`;
- exactly nine unique Plugin Skill entries;
- exactly nine nested Skill ZIPs;
- each nested ZIP SHA-256 matches the committed release manifest;
- no extra Aegis Skill ZIP.

---

## 10. Hosted evidence requirements

After pushing the exact result revision, require at minimum:

```yaml
Aegis_Skillset_Integrity:
  exact_head: true
  conclusion: SUCCESS

Aegis_Project_State_Integrity:
  if_triggered: SUCCESS
  if_not_triggered:
    required_record: explicit_path_filter_non_trigger
    exact_head_local_project_state_commands: PASS

required_checks:
  any_failure: forbidden
```

The successful Skillset workflow MUST publish the candidate artifact:

```text
aegis-skill-installation-kit-0.2.0-beta.1-candidate
```

Record its GitHub artifact ID and digest.

Independently inspect the uploaded artifact and verify:

- archive filename `aegis-skill-installation-kit-0.2.0-beta.1.zip`;
- embedded release version `0.2.0-beta.1`;
- exact nine unique Skill entries / ZIPs;
- each nested Skill ZIP digest matches `skillset/releases/aegis-0.2.0-beta.1.json`;
- exact result Plugin manifest version is `0.2.0-beta.1`;
- marketplace still points to `./plugins/aegis`.

---

## 11. Historical immutability checks

At the final result, verify the following remain present and unmodified relative to the trusted anchor unless Git history already proves an accepted prior difference:

```text
skillset/releases/aegis-0.1.0-beta.1.json
skillset/releases/aegis-0.1.0-beta.2.json
skillset/releases/aegis-0.1.0-beta.3.json
docs/releases/v0.1.0-beta.1.md
docs/releases/v0.1.0-beta.2.md
docs/releases/v0.1.0-beta.3.md
docs/installation-and-usage-v0.1.md
.github/workflows/release.yml
```

Do not modify existing Git tags or published Release assets.

---

## 12. Evidence materialization envelope

P32 completion is not accepted until the exact result is reviewer-resolvable.

Required return:

```yaml
release_candidate_return:
  package_id: RC-I01-P31-01
  stage: P32_IMPLEMENTATION_COMPLETE
  release_version: 0.2.0-beta.1
  release_tag: v0.2.0-beta.1

  task_anchor:
    revision: 212f1d7dcb2c31162f0f64946a4473912578c5d9
    relation: ancestor
  actual_starting_revision: <exact revision>
  result_revision: <exact result revision>
  materialized_ref: <reviewer-resolvable GitHub ref>

  red_oracle_observed: PASS
  plugin_exact_nine: PASS
  committed_release_manifest: PASS
  plugin_materialization: PASS
  current_release_docs: PASS
  packaging_regressions: PASS
  candidate_skillset_ci: PASS
  project_state_integrity: PASS

  candidate_artifact_id: <artifact id>
  candidate_artifact_digest: <digest>
  candidate_archive: aegis-skill-installation-kit-0.2.0-beta.1.zip
  artifact_nested_skill_digests: PASS

  release_identity_collision: false
  historical_beta3_preserved: PASS
  service_profile: NOT_AUTHORIZED
  rollout: DENIED
  p34_rerun_performed: false
  publication_performed: false
  merge_performed: false

  next_owner: aegis-governance
  next_stage: P24_RELEASE_READINESS_REREVIEW
```

Do not claim `P24 PASS` in this envelope.

---

## 13. Exit criteria

`RC-I01-P31-01` is complete only when all are true:

1. the actual start is a valid descendant of `task_anchor`;
2. target release identity is unused;
3. RED release-identity oracle is observed before implementation;
4. deterministic `0.2.0-beta.1` release manifest is committed;
5. native Plugin is coherently regenerated at `0.2.0-beta.1`;
6. Plugin inventory is exact nine and canonical/materialized Skill parity holds;
7. v0.2 release notes, v0.2 install guide, and README current pointers are coherent;
8. candidate Skillset CI is bound to `0.2.0-beta.1` without changing release publication semantics;
9. all required local regressions pass;
10. exact result is pushed/materialized at a reviewer-accessible GitHub ref;
11. exact-head hosted Skillset CI succeeds;
12. candidate Installation Kit artifact is reviewer-resolvable and independently digest-verified;
13. historical beta.1/beta.2/beta.3 release identity remains immutable;
14. no P34 rerun, tag, publication, merge, rollout expansion, or SERVICE_PROFILE work occurred;
15. the return envelope is complete enough for independent P24 rereview.

---

## 14. Blocked returns

Return without inventing a repair when any of the following occurs:

### `BLOCKED_RELEASE_IDENTITY_COLLISION`

Target tag / Release already exists.

### `BLOCKED_EXECUTION_DIVERGENCE`

Task anchor ancestry cannot be established, history was incompatibly rewritten, or observed state contains contradictory unauthorized work.

### `BLOCKED_AUTHORITY`

Release materialization requires a new Product / Semantic / Architecture / Verification / Distribution / Gate decision not already authorized.

### `BLOCKED_IMPLEMENTATION_SCOPE`

Required work would change semantic Skill content, Control Plane implementation, `.aegis`, release publication semantics, or another prohibited surface.

### `BLOCKED_EVIDENCE`

Exact result cannot be pushed/materialized, hosted evidence cannot be resolved, candidate artifact is unavailable, or a required digest/provenance fact cannot be independently verified.

### `BLOCKED_IMPLEMENTATION`

A required release/package regression fails due to an implementation/package defect inside authorized scope.

In all blocked cases preserve already-valid work and return the exact observed revision, failing command/check, and first untrusted boundary.

---

## 15. P32 surface handoff contract

P31 authorizes the following execution-surface transfer only after the exact package ref is known:

```yaml
type: surface_handoff
stage: P32
stage_owner: aegis-implementation
from_surface: CONTROL_REASONING
to_surface: CODE_EXECUTION
preferred_executor: codex
reason: repository_heavy_release_candidate_materialization
package_ref: <exact RC-I01-P31-01 package commit/ref>
task_anchor:
  revision: 212f1d7dcb2c31162f0f64946a4473912578c5d9
  relation: ancestor
resume_cursor: null
return_surface: CONTROL_REVIEW
```

The exact required Codex execution prefix must be rendered immediately before this YAML whenever the handoff is issued:

> 请按以下 Aegis handoff 直接执行：以 `package_ref` 为任务授权，按 `task_anchor/resume_cursor` 核对当前状态并从首个未完成步骤继续；若状态冲突则 fail closed。

This handoff changes execution location only. `aegis-implementation` remains the P32 Primary Owner; `aegis-governance` owns the later P24 rereview.

---

## 16. P31 disposition

```yaml
P31_release_candidate_package:
  package_id: RC-I01-P31-01
  task_id: RC-I01
  purpose: CONTROL_PLANE_V02_RELEASE_CANDIDATE_MATERIALIZATION
  public_version: 0.2.0-beta.1
  public_tag: v0.2.0-beta.1
  product_form: PLUGIN_PLUS_EXACT_NINE_SKILLS
  task_anchor:
    revision: 212f1d7dcb2c31162f0f64946a4473912578c5d9
    relation: ancestor
  resume_cursor: null
  preferred_executor: codex
  p34_rerun_required: false
  pp0_harness_work: forbidden
  service_profile: NOT_AUTHORIZED
  rollout: DENIED
  publication_during_P32: forbidden
  merge_during_P32: forbidden
  final_review_owner: aegis-governance
  final_review_stage: P24_RELEASE_READINESS_REREVIEW
  status: READY_FOR_P32_IMPLEMENTATION
```
