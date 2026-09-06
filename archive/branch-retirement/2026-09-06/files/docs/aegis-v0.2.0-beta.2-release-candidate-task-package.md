# Aegis v0.2.0-beta.2 — P31 Release Candidate Task Package

Status: **P31 / CONTROL_REASONING / MATERIALIZED**

Package ID: `RC-I02-P31-01`

Task ID: `RC-I02`

Primary owner: `aegis-implementation`

Preferred execution surface: `CODE_EXECUTION / Codex`

Review return: `CONTROL_REVIEW -> aegis-gate-review / P34`

## 1. Task identity

```yaml
package_id: RC-I02-P31-01
task_id: RC-I02
purpose: AEGIS_V020_BETA2_RELEASE_CANDIDATE_MATERIALIZATION
primary_owner: aegis-implementation
preferred_code_executor: codex
review_return_surface: CONTROL_REVIEW
release_version: 0.2.0-beta.2
release_tag: v0.2.0-beta.2
release_channel: prerelease
product_form: PLUGIN_PLUS_EXACT_NINE_SKILLS
implementation_scope: RELEASE_PACKAGE_ONLY
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/84
task_anchor:
  revision: c0ec6cccc6675eca98aa3a453a5ad1c6b672d7dc
  relation: ancestor
resume_cursor: null
p30_plan_ref: 9d0e7d0f308f9cfeb176d83d11203e478bf38140
p30_plan_path: docs/superpowers/plans/2026-09-06-aegis-v0.2.0-beta.2-release-candidate.md
```

This is the only substantive package for beta.2 release-candidate materialization.

The exact `package_ref` is the commit that materializes this document on PR #84. P32 is not authorized unless its handoff carries that exact `package_ref`, the same-repository materialization ref, and the task anchor above.

## 2. Frozen release basis

Release content baseline is frozen at:

`main@c0ec6cccc6675eca98aa3a453a5ad1c6b672d7dc`

with tree:

`702a8a9629ca51579b4a7ebec413f22d9992c930`

P32 SHOULD create its implementation branch directly from this exact revision. A later moving `main` must not be silently absorbed into beta.2.

If `main` advances before P32 and the executor is tempted to include newer changes, stop with:

`BLOCKED_RELEASE_BASE_DRIFT`

unless control reasoning explicitly re-baselines this package.

Task-anchor ancestry remains required, but ancestry alone does not authorize widening the frozen release content.

## 3. Published predecessor / identity safety

Published predecessor:

```yaml
version: 0.2.0-beta.1
tag: v0.2.0-beta.1
source_revision: 3253abced7a17d66d8754fa84d7953408aae49d4
```

At P30/P31 preflight:

```yaml
v0_2_0_beta_2_tag_exists: false
v0_2_0_beta_2_github_release_exists: false
release_v0_2_0_beta_2_branch_exists: false
```

P32 MUST repeat collision checks before authored changes and again before final return.

Any collision is:

`BLOCKED_RELEASE_IDENTITY_COLLISION`

Do not overwrite, move, replace, or silently rename release identity.

## 4. Accepted release claim envelope

beta.2 packages current accepted repository capability; it does not create new semantic Authority.

The release may claim:

- one native Aegis Plugin exposing exactly nine canonical Skills;
- current repository-identity fail-closed handoff semantics;
- current Verification Productization evidence-contract semantics;
- Project State v0.6 capability, including `Bound` / affirmative historical `Absent` Gate Decision Binding semantics;
- deterministic v0.5 -> v0.6 migration support with zero inferred `Absent`;
- immutable integrated occurrence identity/history and append-only corroborating evidence;
- independent P34 Gate ownership and reviewer-resolvable exact-result evidence boundaries.

The release MUST NOT claim:

- that root `.aegis/**` has already migrated to v0.6;
- that real `int-pr82` has been persisted;
- that a synthetic or retroactive PR #82 Gate Decision exists;
- SERVICE_PROFILE authorization;
- rollout expansion;
- zero-user-turn cross-Primary substantive chaining;
- a required daemon/hosted control service;
- beta.2 publication before the release workflow actually succeeds.

## 5. Authorized file scope

P32 may author only the following release-package paths/patterns unless a blocked return is issued first.

### Required / normally changed

```text
tests/skillset/test_control_plane_v02_release_candidate.py
skillset/releases/aegis-0.2.0-beta.2.json
docs/releases/v0.2.0-beta.2.md
docs/installation-and-usage-v0.2.md
README.md
plugins/aegis/.codex-plugin/plugin.json
plugins/aegis/skills/**
.github/workflows/skillset.yml
```

### Conditionally allowed only for beta.2 version/oracle alignment

```text
tests/skillset/test_openai_plugin_materialization.py
tests/skillset/test_workflow_paths.py
.agents/plugins/marketplace.json
```

`plugins/aegis/skills/**` and `.agents/plugins/marketplace.json` are generator-owned outputs. Do not hand-edit semantic Skill content there.

### Read/reuse only; no semantic modification

```text
skills/**
skillset/skills/**
skillset/distribution.json
scripts/build_aegis_distributions.py
scripts/build_openai_plugin_materialization.py
scripts/build_candidate_plugin_parity.py
scripts/build_skillset.py
scripts/validate_generated_skills.py
tools/aegis_skillset/**
tools/aegis_state/**
.github/workflows/release.yml
.aegis/**
```

### Explicitly forbidden

```text
root .aegis/** authored mutation
Control Plane Product/Modeling/Architecture/Verification semantic change
Verification Productization semantic Authority change
Project State v0.6 semantic Authority change
canonical Skill semantic change merely to make packaging pass
release workflow semantic change
historical release manifest/note/tag/asset rewrite
release tag creation
GitHub Release creation
merge to main
SERVICE_PROFILE / rollout expansion
new runtime/daemon/service/agent
```

If a required fix falls outside the allowed release-package surface, stop rather than widening the package.

## 6. Required implementation sequence

### RC-I02-1 — Repository / release identity preflight

Mandatory receiving order:

```text
repository identity
-> package materialization ref
-> package_ref
-> exact frozen release baseline
-> task-anchor ancestry
-> release identity collision check
-> worktree/dirty-work inspection
-> authored mutation
```

Record the actual starting revision.

Create a fresh implementation branch/PR from exact release baseline `c0ec6cccc6675eca98aa3a453a5ad1c6b672d7dc` rather than modifying PR #84.

Recommended branch:

`aegis/release-v0.2.0-beta.2-rc`

Recommended implementation PR title:

`release: materialize Aegis v0.2.0-beta.2 candidate`

Keep the implementation PR Draft through P32.

### RC-I02-2 — RED release candidate oracle

Update `tests/skillset/test_control_plane_v02_release_candidate.py` so the **current candidate** identity is beta.2 and historical release identity remains explicitly protected.

The oracle must verify at minimum:

- beta.2 release manifest path is expected;
- beta.2 release notes exist after materialization;
- current Plugin version is beta.2 after materialization;
- README and v0.2 installation guide point to beta.2;
- published beta.1 manifest/notes remain present and unchanged;
- historical v0.1 beta.1/beta.2/beta.3 files remain present;
- public/historical source verification does not reinterpret a moving current candidate as an old published release.

Before beta.2 release surfaces are created, run the targeted test and preserve RED evidence.

If it unexpectedly passes before beta.2 materialization, inspect for pre-existing/untrusted beta.2 work and fail closed if release identity is no longer clean.

### RC-I02-3 — Generate beta.2 release manifest

Run:

```bash
python3 scripts/build_aegis_distributions.py \
  --version 0.2.0-beta.2 \
  --write-manifest
```

Then verify:

```bash
python3 scripts/build_aegis_distributions.py \
  --version 0.2.0-beta.2 \
  --check
```

Required committed artifact:

`skillset/releases/aegis-0.2.0-beta.2.json`

Do not hand-author digest fields.

### RC-I02-4 — Materialize exact-nine Plugin beta.2

Run:

```bash
python3 scripts/build_openai_plugin_materialization.py \
  --release-version 0.2.0-beta.2 \
  --write
```

Then verify:

```bash
python3 scripts/build_openai_plugin_materialization.py \
  --release-version 0.2.0-beta.2 \
  --check
```

Required current state:

```yaml
plugin_version: 0.2.0-beta.2
plugin_skill_count: 9
partial_or_mixed_catalog: forbidden
```

Current Plugin Skill trees must be generated from current canonical Skills and include the accepted beta.2 capability delta already present at the frozen source revision.

### RC-I02-5 — Release notes / guide / README

Create:

`docs/releases/v0.2.0-beta.2.md`

Update the existing v0.2 installation guide and README current-release pointers.

Release notes must be factual and bounded.

Recommended sections:

1. `What beta.2 is`
2. `Changes since beta.1`
3. `Verification Productization evidence-contract hardening`
4. `Project State v0.6 capability`
5. `Distribution / exact-nine Plugin`
6. `Known boundary: repository root Project State remains v0.5`
7. `Upgrade / rollback to v0.2.0-beta.1`
8. `Verification / publication boundary`

Do not describe root v0.6 persistence or `int-pr82` as completed.

### RC-I02-6 — Candidate workflow binding

Update `.github/workflows/skillset.yml` minimally.

Preserve published beta.1 source verification exactly against:

`v0.2.0-beta.1 -> 3253abced7a17d66d8754fa84d7953408aae49d4`

Preserve beta.3 historical compatibility verification where currently present.

Change current candidate checks from beta.1 to beta.2:

```yaml
current_plugin_materialization:
  version: 0.2.0-beta.2

candidate_installation_kit:
  version: 0.2.0-beta.2
  artifact_name: aegis-skill-installation-kit-0.2.0-beta.2-candidate
  archive_name: aegis-skill-installation-kit-0.2.0-beta.2.zip
```

Add/retain exact candidate release-manifest check for beta.2.

Do not delete published beta.1 validation just because current candidate advances to beta.2.

If practical within the existing workflow, ensure full Control Plane regressions are included in exact-head candidate qualification; otherwise run them separately and return exact evidence. Do not create a new release verification framework.

### RC-I02-7 — Deterministic candidate Kit / parity evidence

Build candidate Kit:

```bash
rm -rf /tmp/aegis-v02-beta2-release-candidate
mkdir -p /tmp/aegis-v02-beta2-release-candidate
python3 scripts/build_aegis_distributions.py \
  --version 0.2.0-beta.2 \
  --installation-kit-archive-dir /tmp/aegis-v02-beta2-release-candidate
```

Generate exact-head candidate Plugin parity evidence:

```bash
python3 scripts/build_candidate_plugin_parity.py \
  --output /tmp/aegis-beta2-candidate-plugin-parity.json
```

Independently inspect the Installation Kit:

- expected outer ZIP exists;
- embedded `release.json` equals committed beta.2 release manifest;
- exact nine nested Skill ZIPs exist exactly once;
- every nested ZIP digest equals the beta.2 manifest;
- Plugin inventory is exact-nine;
- candidate Plugin parity is bound to exact result revision.

## 7. Required regression / oracle set

At minimum run:

```bash
python3 -m unittest tests.skillset.test_control_plane_v02_release_candidate -v

python3 -m tools.aegis_skillset.cli validate .
python3 scripts/build_skillset.py --check
python3 -m tools.aegis_skillset.cli distribution-check .
python3 scripts/build_aegis_distributions.py --check
python3 scripts/build_aegis_distributions.py --version 0.2.0-beta.2 --check
python3 scripts/build_openai_plugin_materialization.py --release-version 0.2.0-beta.2 --check
python3 -m tools.aegis_skillset.cli routing-check .
python3 -m tools.aegis_skillset.cli installed-platform-check .
python3 scripts/validate_generated_skills.py

python3 -m unittest discover -s tests/skillset -v
python3 -m unittest discover -s tests/project_state -v
python3 -m unittest discover -s tests/control_plane -v
python3 evals/scripts/validate_corpus.py
python3 -m unittest discover -s evals/tests -v

python3 -m tools.aegis_state.cli validate .
python3 -m tools.aegis_state.cli check .
```

All applicable tests must pass on the exact result candidate.

Historical beta.1 publication/source proof must remain valid and must resolve the immutable historical tag/source rather than the beta.2 candidate tree.

## 8. Hosted evidence

Before return to CONTROL_REVIEW, push the exact result to the Draft implementation PR.

Required reviewer-resolvable evidence includes:

- exact `result_revision` and tree;
- exact implementation PR URL;
- exact changed-file list;
- Skillset workflow result on exact candidate;
- Project State workflow result on exact candidate;
- Verification Productization workflow result on exact candidate when triggered/applicable;
- any other changed-path workflow results;
- candidate Installation Kit artifact ID/name/digest when available;
- exact candidate Plugin parity artifact/ref;
- local/full regression summary;
- proof that `v0.2.0-beta.2` tag/Release still do not exist at P32 return;
- proof root `.aegis/**` was not modified;
- proof historical release assets/manifests/notes were not rewritten.

A local-only result is not review evidence.

If materialization or hosted evidence is unavailable, return `BLOCKED_EVIDENCE` rather than claiming P34 readiness.

## 9. P32 hard stops

P32 MUST NOT:

```text
create v0.2.0-beta.2 tag
create/publish GitHub Release
create release/v0.2.0-beta.2 publication branch
merge implementation PR
mark P34 PASS
mark P24 READY
migrate root .aegis to v0.6
persist real int-pr82
rewrite beta.1 or beta.3 history
expand rollout
claim SERVICE_PROFILE
```

## 10. Exit criteria

P32 is complete only when all are true:

```yaml
release_identity_clean: true
beta2_manifest_deterministic: true
plugin_version_beta2: true
plugin_exact_nine: true
canonical_plugin_parity: true
release_notes_beta2: true
install_and_readme_pointers_beta2: true
published_beta1_history_preserved: true
root_aegis_unchanged: true
real_int_pr82_not_persisted: true
full_regressions_pass: true
exact_result_remote_materialized: true
hosted_exact_candidate_evidence_available: true
release_tag_created: false
github_release_created: false
```

Successful return status:

`READY_FOR_P34`

## 11. Required P32 return

```yaml
P32_return:
  repository: Mostorm-Labs/aegis
  package_id: RC-I02-P31-01
  package_ref: <exact current package ref>
  package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/84

  task_anchor:
    revision: c0ec6cccc6675eca98aa3a453a5ad1c6b672d7dc
    relation: ancestor

  actual_starting_revision: <sha>
  result_revision: <exact sha>
  exact_tree: <tree sha>
  materialized_ref: <implementation PR URL>

  release:
    version: 0.2.0-beta.2
    tag: v0.2.0-beta.2
    tag_exists: false
    github_release_exists: false

  verification:
    targeted_release_candidate: PASS
    skillset: PASS
    project_state: PASS
    control_plane: PASS
    evals: PASS
    root_validate_check: PASS
    hosted_ci:
      skillset: <run>/PASS
      project_state: <run>/PASS
      verification_productization: <run>/PASS | NOT_APPLICABLE

  artifacts:
    candidate_installation_kit: <artifact/ref>
    candidate_plugin_parity: <artifact/ref>

  boundaries:
    root_aegis_modified: false
    real_int_pr82_persisted: false
    historical_release_rewritten: false
    release_published: false
    merged: false

  blockers: []
  status: READY_FOR_P34
  return_surface: CONTROL_REVIEW
```

## 12. P31 disposition

```yaml
P31:
  package_id: RC-I02-P31-01
  task_id: RC-I02
  package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/84
  task_anchor: c0ec6cccc6675eca98aa3a453a5ad1c6b672d7dc
  resume_cursor: null
  substantive_package_count: 1
  primary_gate_budget: 1
  status: READY_FOR_P32
```

Do not execute P34 or publication from this package. P32 returns the exact release candidate for independent review.
