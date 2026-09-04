# Aegis Control Plane v0.2 — P31 Release-Candidate Task Package Re-issue

Status: **P31 / CONTROL_REASONING / MATERIALIZED REPLACEMENT**

Package ID: `RC-I01-P31-02`

Task ID: `RC-I01`

Primary Owner: `aegis-implementation`

Preferred execution surface: `CODE_EXECUTION / Codex`

Review return: `CONTROL_REVIEW -> aegis-governance / P24_RELEASE_READINESS_REREVIEW`

This package re-issues the already-approved RC-I01 release-candidate task after the repository-identity repair was independently gated, integrated, and persisted into Project State. It preserves the accepted release purpose, public version, product form, release-package-only scope, prior Control Plane P34, and P30 plan. It replaces only the unsafe repository-less execution envelope from `RC-I01-P31-01` and reconciles the release-candidate CI instructions with the current repository-identity materialization boundary.

## 1. Task identity

```yaml
package_id: RC-I01-P31-02
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
supersedes_package_id: RC-I01-P31-01
supersedes_package_ref: b876c74c4b098d7088233945a17de47a7b5b3422
supersession_reason: REPOSITORY_IDENTITY_EXECUTION_ENVELOPE_REISSUE
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/64
task_anchor:
  revision: 63d65472278448f8d2b5fa2bc2991189dcd0825a
  relation: ancestor
resume_cursor: null
```

The exact replacement `package_ref` is the final P31 head revision and is recorded by the P31 stage result and PR metadata. P32 is non-executable unless its handoff carries that exact revision together with the same-repository `package_materialization_ref`, repository object, task anchor, and `resume_cursor: null`.

`RC-I01-P31-01` remains historical task evidence. Its release purpose/version/product form remain retained, but its repository-less executable envelope is `SUPERSEDED_UNSAFE_DO_NOT_RESUME`.

## 2. Current trusted basis

Repository / integration baseline:

- current trusted `main`: `63d65472278448f8d2b5fa2bc2991189dcd0825a`
- repository-identity implementation PR: `#62`
- repository-identity P34 review: `5110723189 = PASS / ACCEPTED_FOR_DOWNSTREAM`
- PR #62 integration revision: `7e9771b5914b40654b9e0015001d1dd21cdabb53`
- repository-identity Project State closure PR: `#63`
- PR #63 merge revision / task anchor: `63d65472278448f8d2b5fa2bc2991189dcd0825a`
- post-merge Project State Integrity: `33854466232 = SUCCESS`
- Project State records `gate-repository-identity-pr62::decision::0001 = PASS` and `int-pr62 = current / conforming`.

Accepted Control Plane product result:

- exact accepted Control Plane candidate: `18559f32ede7ebd845064fe8de7967ca358b785f`
- P34 review: `5108520468 = PASS / ACCEPTED_FOR_DOWNSTREAM`

Current Authority / contracts:

- Control Plane v0.2 Product Authority: Plugin + exact-nine product boundary recorded in root Project State;
- Control Plane Verification Authority: `18b374e95057bafd0feac3ca16e7aca4774a925a`;
- repository-identity Platform Authority: `e851531a000c5c84ee2f00b429d813c048d29ab8`;
- repository-identity core Verification Authority: `61aa42e98558a1621b0228223835473f248ee869`;
- repository-identity materialization-proof Authority: `8fc76fc6c10951c4748c04be60bbc1c953e6de7e`;
- repository-backed handoff contract requires explicit `repository`, same-repository `package_materialization_ref`, repository preflight before package/anchor/cursor reasoning, and fail-closed `BLOCKED_REPOSITORY_IDENTITY`;
- Plugin distribution contract remains unchanged;
- `SERVICE_PROFILE = NOT_AUTHORIZED`;
- rollout remains `DENIED`;
- zero-user-turn cross-Primary substantive chaining remains unauthorized.

Retained P30:

- P30 plan ref: `3bd76507522f69714bbd584e287347cdac38f361`;
- plan path: `docs/superpowers/plans/2026-09-04-control-plane-v02-release-candidate.md`;
- disposition: `RETAIN_NO_REPLAN`;
- slice: `RC-I01 — CONTROL_PLANE_V02_RELEASE_CANDIDATE_MATERIALIZATION`.

The re-issue may refine execution instructions to remain compatible with Current Authority and current implementation reality, but it may not widen the retained release-package-only scope or change release identity.

If any trusted fact above is contradicted at execution time, fail closed instead of expanding this package.

## 3. Repository identity and execution position

Repository-backed execution MUST begin with:

```yaml
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/64
task_anchor:
  revision: 63d65472278448f8d2b5fa2bc2991189dcd0825a
  relation: ancestor
resume_cursor: null
```

Normative invariants:

> `Repository Identity != Task Anchor != Execution Cursor`

> `A revision is not a repository locator.`

Receiving order is mandatory:

```text
repository identity
-> declared-repository checkout/worktree
-> package resolution in declared repository
-> package_materialization_ref repository match
-> task_anchor ancestry
-> resume_cursor classification if applicable
-> authored mutation
```

There is no accepted RC-I01 execution continuation point. The earlier unsafe handoff did not establish an accepted P32 result/cursor and must not be resumed.

The executor MUST establish `Mostorm-Labs/aegis` first, record the actual starting revision, prove task-anchor ancestry, inspect worktree state, preserve unrelated dirty work, isolate inside the declared Aegis repository when needed, and never substitute another ambient repository. Repository-addressing failure returns `BLOCKED_REPOSITORY_IDENTITY` before any anchor/cursor classification or authored mutation.

## 4. Frozen public release identity

```yaml
release_version: 0.2.0-beta.1
release_tag: v0.2.0-beta.1
release_channel: prerelease
product_form: one native Aegis Plugin + exactly nine canonical Skills
```

Fresh P31 preflight established:

- `v0.1.0-beta.3` tag exists at `38bf619ede0615431c7517bc0e07984136af28cf`;
- published beta.3 GitHub prerelease exists;
- published beta.3 Installation Kit SHA-256 remains `19db0cb4c5823a65a610a0edb0354267517417c7941456adc76f1e59487354b1`;
- `v0.2.0-beta.1` tag does not exist;
- no GitHub Release exists for `v0.2.0-beta.1`.

P32 MUST repeat the beta.1 tag/Release collision preflight before authored changes and again before final evidence return. Collision returns `BLOCKED_RELEASE_IDENTITY_COLLISION`; do not silently choose another version or overwrite/move an existing identity.

## 5. Authorized file scope

Authorization is path/pattern based; there is no numeric changed-file-count invariant.

Create:

```text
tests/skillset/test_control_plane_v02_release_candidate.py
skillset/releases/aegis-0.2.0-beta.1.json
docs/releases/v0.2.0-beta.1.md
docs/installation-and-usage-v0.2.md
```

Modify / regenerate:

```text
plugins/aegis/.codex-plugin/plugin.json
plugins/aegis/skills/**
.agents/plugins/marketplace.json
.github/workflows/skillset.yml
README.md
```

`plugins/aegis/skills/**` and `.agents/plugins/marketplace.json` may change only as deterministic output of the existing native Plugin materialization path. Their Skill semantics must come from already-current canonical `skills/**`; no canonical Skill semantic changes are authorized.

Read/reuse without authored semantic modification:

```text
scripts/build_aegis_distributions.py
scripts/build_openai_plugin_materialization.py
scripts/build_candidate_plugin_parity.py
tools/aegis_skillset/package.py
tools/aegis_skillset/plugin_materialization.py
skillset/distribution.json
.github/workflows/release.yml
docs/plugin-distribution-contract-v0.1.md
docs/installation-and-usage-v0.1.md
skillset/shared/handoff-contract.md
skills/aegis-implementation/**
skills/aegis-gate-review/**
.aegis/**
```

Explicitly forbidden authored scope:

```text
tools/aegis_control/**
tests/control_plane/**
skillset/shared/handoff-contract.md
skillset/skills/aegis-implementation/**
skillset/skills/aegis-gate-review/**
skills/**
scripts/build_aegis_distributions.py
scripts/build_openai_plugin_materialization.py
scripts/build_candidate_plugin_parity.py
tools/aegis_skillset/package.py
tools/aegis_skillset/plugin_materialization.py
.aegis/**
Control Plane Product / Modeling / Architecture / Verification Authority docs
repository-identity Authority docs
.github/workflows/release.yml
historical release manifests / historical release notes
```

Generated `plugins/aegis/skills/**` is authorized; canonical `skills/**` is not. If execution appears to require an authored change outside this boundary, stop rather than widening the package.

## 6. Required changes

### RC-I01-A — RED release-identity oracle

Create `tests/skillset/test_control_plane_v02_release_candidate.py` from the retained P30/P31-01 contract. It MUST prove the beta.1 release manifest exists and is deterministic, the current Plugin version is beta.1, exact-nine inventory holds, current docs point to beta.1, and historical beta.1/beta.2/beta.3 manifests/notes remain present.

Before release surfaces exist, run the targeted test and preserve RED evidence. If it unexpectedly passes, inspect for untrusted pre-existing beta.1 release work and fail closed if the identity is no longer clean.

### RC-I01-B — deterministic beta.1 release manifest

Generate, do not hand-author digests:

```bash
python3 scripts/build_aegis_distributions.py \
  --version 0.2.0-beta.1 \
  --write-manifest
```

The manifest MUST bind the current canonical exact-nine Skill trees, including the integrated repository-identity semantics.

### RC-I01-C — native Plugin materialization for beta.1

```bash
python3 scripts/build_openai_plugin_materialization.py \
  --release-version 0.2.0-beta.1 \
  --write
```

Required state:

- `plugins/aegis/.codex-plugin/plugin.json.version = 0.2.0-beta.1`;
- exact nine Plugin Skill directories;
- every Plugin Skill tree matches current canonical `skills/<name>` and therefore carries repository-identity semantics;
- marketplace remains one Aegis Plugin at `./plugins/aegis`;
- no App, owner, routing, lifecycle, SERVICE_PROFILE, or rollout semantics are introduced.

Advancing current committed `plugins/aegis/**` from beta.3 to beta.1 is authorized by RC-I01. Rewriting historical beta.3 manifests, notes, tag, Release, or published assets is not.

### RC-I01-D — v0.2 release notes / installation guidance

Create `docs/releases/v0.2.0-beta.1.md` and `docs/installation-and-usage-v0.2.md`; update `README.md` current pointers.

Release copy MUST state the accepted claim envelope: one Plugin + exact nine Skills; durable Authority/Project State/Gate/resume semantics; Control Plane P34 candidate `18559f32...` / review `5108520468`; repository-backed execution includes the separately Gate-accepted/integrated repository-identity preflight; no standalone hosted service requirement; no R0/S0/W7D claim; `SERVICE_PROFILE` not authorized; rollout denied; no zero-user-turn cross-Primary substantive chaining claim; PP0 40-WorkScope harness not a v0.2 release requirement under Current Verification Authority; beta.3 remains the previous immutable published rollback/reproducibility boundary.

Do not state beta.1 is already published.

### RC-I01-E — candidate CI binding without weakening beta.3 history

Modify only `.github/workflows/skillset.yml` for release-candidate binding.

Preserve current repository-identity/current-head checks, exact-head `CANDIDATE_PLUGIN_PARITY_EVIDENCE`, routing/installed-platform/generated-Skill checks, repository-identity regressions, and task6.1 development-oracle checks/artifacts.

Add/bind the beta.1 candidate path:

```yaml
release_manifest_check: python3 scripts/build_aegis_distributions.py --version 0.2.0-beta.1 --check
plugin_check: python3 scripts/build_openai_plugin_materialization.py --release-version 0.2.0-beta.1 --check
candidate_kit_artifact: aegis-skill-installation-kit-0.2.0-beta.1-candidate
candidate_archive: aegis-skill-installation-kit-0.2.0-beta.1.zip
```

Historical beta.3 compatibility rule:

The candidate head MUST NOT apply the beta.3 Plugin materialization checker to the new beta.1 `plugins/aegis/**` payload. Without modifying packaging/materialization scripts, continue beta.3 historical binding by validating the immutable historical source itself:

```yaml
historical_release:
  tag: v0.1.0-beta.3
  source_revision: 38bf619ede0615431c7517bc0e07984136af28cf
  validation_location: isolated_historical_checkout_or_archive
  current_candidate_plugin_used_as_beta3_payload: false
  historical_manifest_rewritten: false
  historical_tag_or_release_mutated: false
```

A valid implementation may fetch/archive exact historical source `38bf619...` into a temporary isolated directory and run that historical checkout's release-manifest and Plugin-materialization checks there. The current candidate checkout is responsible for beta.1 checks and repository-identity exact-head parity evidence.

Do not delete or weaken beta.3 history proof; do not modify current packaging/materialization tooling merely to make the candidate pass.

## 7. Required test / oracle sequence

Before edits: repository preflight, task-anchor ancestry, beta.1 tag/Release absence, worktree inspection and dirty-work preservation.

RED first:

```bash
python3 -m unittest tests.skillset.test_control_plane_v02_release_candidate -v
```

Current beta.1 generated checks after materialization:

```bash
python3 scripts/build_aegis_distributions.py --version 0.2.0-beta.1 --check
python3 scripts/build_openai_plugin_materialization.py --release-version 0.2.0-beta.1 --check
python3 -m tools.aegis_skillset.cli distribution-check .
python3 scripts/build_candidate_plugin_parity.py --output /tmp/aegis-candidate-plugin-parity.json
```

Historical beta.3 proof MUST inspect `v0.1.0-beta.3 / 38bf619...` historical source/payload, not reinterpret the current beta.1 Plugin as beta.3. It must also prove P32 did not mutate the published tag/Release identity.

Current workflow-equivalent regression set:

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

Full regression suite:

```bash
python3 -m unittest discover -s tests/skillset -v
python3 -m unittest discover -s tests/project_state -v
python3 -m unittest discover -s tests/control_plane -v
python3 evals/scripts/validate_corpus.py
python3 -m unittest discover -s evals/tests -v
python3 -m tools.aegis_state.cli validate .
python3 -m tools.aegis_state.cli check .
```

All applicable checks MUST PASS. These checks are P32/release-candidate evidence only; they do not create a P24 verdict or rewrite any P34 verdict.

## 8. Deterministic Installation Kit and hosted evidence

Build the beta.1 candidate Installation Kit through existing deterministic packaging. The candidate artifact must be reviewer-resolvable and must not be a GitHub Release.

Required hosted state:

```yaml
Aegis_Skillset_Integrity:
  exact_head: true
  conclusion: SUCCESS
  candidate_artifact: aegis-skill-installation-kit-0.2.0-beta.1-candidate
Aegis_Project_State_Integrity:
  if_triggered: SUCCESS
  if_not_triggered:
    required_record: explicit_path_filter_non_trigger
    exact_head_local_project_state_commands: PASS
required_checks:
  any_failure: forbidden
```

Record candidate artifact ID and digest. Independently verify archive filename `aegis-skill-installation-kit-0.2.0-beta.1.zip`, embedded beta.1 identity, exactly nine unique Skill entries/nested ZIPs, nested ZIP digests against the committed beta.1 manifest, current Plugin version beta.1, repository-identity semantics in Plugin copies, stable marketplace path, and no publication claim.

## 9. Historical immutability / release separation

P32 must leave historical beta.1/beta.2/beta.3 release manifests, release notes, tags, GitHub Releases and published assets unmodified. `plugins/aegis/**` is the current materialized Plugin surface and is authorized to advance to beta.1; historical beta.3 Plugin truth is preserved by its historical source/tag/Release evidence, not by forcing current HEAD to remain beta.3 forever.

P32 MUST NOT create `v0.2.0-beta.1` tag, publish a GitHub Release, dispatch or alter release publication semantics, merge the implementation PR, rewrite `.aegis` history, or claim publication complete.

## 10. Explicit non-goals

No new Control Plane semantics; no canonical repository-identity semantics; no Product/Modeling/Architecture/Verification/Distribution/Gate Authority edits; no P17/P20 edits; no PP0/40-WorkScope/seven-oracle/32-mutant work; no Control Plane P34 rerun; no daemon/service topology; no R0/S0/W7D/service-cost claim; no SERVICE_PROFILE; no rollout expansion; no zero-user-turn cross-Primary claim; no stage-ownership change; no Project State rewrite; no release-workflow semantic change; no packaging/materialization script semantic change; no tag/Release/publication or merge during P32; no P24 verdict from implementation/CI.

## 11. Required P32 result materialization

Before returning to CONTROL_REVIEW, P32 MUST push the exact result to a reviewer-resolvable GitHub branch/PR and return:

```yaml
P32_return:
  package_id: RC-I01-P31-02
  package_ref: <exact P31 package revision>
  repository:
    provider: github
    full_name: Mostorm-Labs/aegis
  package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/64
  task_anchor:
    revision: 63d65472278448f8d2b5fa2bc2991189dcd0825a
    relation: ancestor
  resume_cursor: null
  actual_starting_revision: <exact inspected revision>
  result_revision: <exact pushed revision>
  materialized_ref: <reviewer-resolvable implementation PR/ref>
  release_identity:
    version: 0.2.0-beta.1
    tag_collision: false
    release_collision: false
    tag_created: false
    github_release_created: false
  scope:
    unauthorized_authored_paths: 0
    canonical_skill_semantics_changed: false
    project_state_changed: false
    release_workflow_semantics_changed: false
  verification:
    targeted_red_observed: true
    beta1_release_manifest_check: PASS
    beta1_plugin_materialization_check: PASS
    exact_nine: true
    repository_identity_regressions: PASS
    historical_beta3_source_binding: PASS
    full_skillset_regressions: PASS
    project_state_regressions: PASS
    control_plane_regressions: PASS
    eval_regressions: PASS
  hosted_ci:
    exact_head_skillset: SUCCESS
    project_state: SUCCESS_OR_EXPLICIT_NON_TRIGGER
    candidate_installation_kit_artifact_id: <id>
    candidate_installation_kit_digest: <digest>
  unresolved_required_refs: 0
  p24_started: false
  merged: false
  release_published: false
  return_surface: CONTROL_REVIEW
```

A local-only result is `BLOCKED_EVIDENCE`. P32 does not issue P24 readiness and does not publish. After a complete P32 evidence return, the next Primary owner is `aegis-governance` for `P24_RELEASE_READINESS_REREVIEW`.

## 12. Fail-closed returns

Use the narrowest applicable blocker:

- `BLOCKED_REPOSITORY_IDENTITY` — repository declaration/resolution/materialization binding missing/mismatched/ambiguous/unavailable;
- `BLOCKED_RELEASE_IDENTITY_COLLISION` — beta.1 tag or Release already exists;
- `BLOCKED_SCOPE` — required authored change outside this package;
- `BLOCKED_AUTHORITY` — Current Authority/Gate/integration basis contradicted;
- `BLOCKED_EXECUTION_DIVERGENCE` — repository identity succeeds but anchor/history incompatible;
- `BLOCKED_EVIDENCE` — exact result or required hosted/artifact evidence cannot be made reviewer-resolvable.

Do not repair an earlier Authority layer, widen scope, invent a version, or publish to escape a blocker.

## 13. Exit criteria

```yaml
package_id: RC-I01-P31-02
repository_bound: true
same_repository_materialization_ref: REQUIRED
task_anchor: 63d65472278448f8d2b5fa2bc2991189dcd0825a
resume_cursor: null
p30_replanned: false
release_version_changed: false
product_form_changed: false
implementation_scope: RELEASE_PACKAGE_ONLY
historical_p31_01: RETAIN_HISTORICAL
old_p32_handoff: SUPERSEDED_UNSAFE_DO_NOT_RESUME
beta3_history_proof_weakened: false
repository_identity_repair_modified: false
p32_executed_by_p31: false
p24_started_by_p31: false
release_published: false
rollout: DENIED
service_profile: NOT_AUTHORIZED
```

This P31 package alone does not execute P32.

## P32 handoff rendering rule

Do not render or execute P32 until this package is durably materialized and its exact final `package_ref` is known.

Whenever the future handoff uses `preferred_executor: codex`, place this exact prefix immediately before the YAML:

> 请按以下 Aegis handoff 直接执行：以 `package_ref` 为任务授权，按 `task_anchor/resume_cursor` 核对当前状态并从首个未完成步骤继续；若状态冲突则 fail closed。
