# Aegis Control Plane v0.2 — P31 Release-Candidate Task Package Repair

Status: **P31 / CONTROL_REASONING / MATERIALIZED SCOPE REPAIR**

Package ID: `RC-I01-P31-03`

Task ID: `RC-I01`

Primary Owner: `aegis-implementation`

Next execution stage: `P33 Resume Interrupted Work`

Preferred execution surface: `CODE_EXECUTION / Codex`

Review return: `CONTROL_REVIEW -> aegis-governance / P24_RELEASE_READINESS_REREVIEW`

This package is a narrow additive repair of `RC-I01-P31-02`. It does not re-plan RC-I01, change release identity, discard the existing beta.1 candidate, reopen upstream Authority, or restart P32 from the beginning. It authorizes the single missing test-oracle path and tightens already-authorized CI evidence to the exact execution head.

## 1. Task identity

```yaml
package_id: RC-I01-P31-03
task_id: RC-I01
purpose: CONTROL_PLANE_V02_RELEASE_CANDIDATE_MATERIALIZATION
primary_owner: aegis-implementation
next_stage: P33
preferred_code_executor: codex
review_return_surface: CONTROL_REVIEW
final_review_owner: aegis-governance
final_review_stage: P24_RELEASE_READINESS_REREVIEW
release_version: 0.2.0-beta.1
release_tag: v0.2.0-beta.1
product_form: PLUGIN_PLUS_EXACT_NINE_SKILLS
implementation_scope: RELEASE_PACKAGE_ONLY
supersedes_package_id: RC-I01-P31-02
supersedes_package_ref: 670a3f460df935df838d596934b361e7cdf89b56
supersession_reason: P31_SCOPE_GAP_REPAIR
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/64
task_anchor:
  revision: 63d65472278448f8d2b5fa2bc2991189dcd0825a
  relation: ancestor
resume_cursor:
  execution_ref: https://github.com/Mostorm-Labs/aegis/pull/66
  branch: aegis/control-plane-v02-release-candidate-p32
  revision: ffc80d125ed8bf107800a5bb982cc88149adc8f9
  relation: descendant_of_task_anchor
  completed_through:
    - repository identity and beta.1 release-identity collision preflight
    - required RED release-identity oracle
    - beta.1 deterministic release manifest materialization
    - beta.1 native Plugin exact-nine materialization
    - beta.1 release notes, installation guidance, and README current pointers
    - beta.3 isolated historical source validation
    - candidate Installation Kit build/upload on workflow run 33861131795
    - routing, installed-platform, and generated-Skill checks on workflow run 33861131795
    - candidate CI reached full skillset suite and exposed the P31 scope gap
  next_action: reconcile PR #66 at the cursor, repair the stale current-vs-historical Plugin test oracle, bind PR candidate parity to the exact branch head, then rerun the complete evidence set
```

`Task Anchor != Execution Cursor`. P33 must classify the observed PR #66 execution position against this cursor. If PR #66 remains exactly at `ffc80d...`, classify `EXACT_CURSOR`. If it is a valid descendant, inspect only the descendant delta and classify `DESCENDANT_CURSOR`. Divergence fails closed.

## 2. Trusted basis retained unchanged

Retain without re-review or re-plan:

- P30 plan ref: `3bd76507522f69714bbd584e287347cdac38f361`;
- Control Plane accepted candidate: `18559f32ede7ebd845064fe8de7967ca358b785f`;
- Control Plane P34: `5108520468 = PASS / ACCEPTED_FOR_DOWNSTREAM`;
- repository-identity P17: `e851531a000c5c84ee2f00b429d813c048d29ab8`;
- repository-identity core P20: `61aa42e98558a1621b0228223835473f248ee869`;
- repository-identity materialization-proof Authority: `8fc76fc6c10951c4748c04be60bbc1c953e6de7e`;
- repository-identity P34: `5110723189 = PASS`;
- PR #62 integration: `7e9771b5914b40654b9e0015001d1dd21cdabb53`;
- PR #63 Project State closure / task anchor: `63d65472278448f8d2b5fa2bc2991189dcd0825a`;
- published beta.3 historical source: `v0.1.0-beta.3 @ 38bf619ede0615431c7517bc0e07984136af28cf`;
- published beta.3 Installation Kit SHA-256: `19db0cb4c5823a65a610a0edb0354267517417c7941456adc76f1e59487354b1`.

Fresh P31 repair preflight:

- current `main = 63d65472278448f8d2b5fa2bc2991189dcd0825a`;
- PR #66 is open / draft / unmerged at `ffc80d125ed8bf107800a5bb982cc88149adc8f9`;
- task anchor is the merge base / ancestor of the accepted cursor;
- `v0.2.0-beta.1` tag is absent;
- `v0.2.0-beta.1` GitHub Release is absent.

If any of these facts conflict at P33 start, fail closed instead of widening or replaying work.

## 3. Scope repair

Authorization mode remains path/pattern based; there is no numeric changed-file-count invariant.

All `RC-I01-P31-02` authorized paths and generated-output rules remain authorized exactly as before.

Add exactly this authored path:

```text
tests/skillset/test_openai_plugin_materialization.py
```

Retain the existing authored authorization for:

```text
.github/workflows/skillset.yml
```

All prior forbidden paths and non-goals remain forbidden, including canonical `skills/**`, packaging/materialization script semantics, Project State, `.github/workflows/release.yml`, tag creation, GitHub Release publication, merge, SERVICE_PROFILE, rollout expansion, and upstream Authority changes.

## 4. Required repair A — current-vs-historical Plugin oracle

Root cause established by workflow run `33861131795`:

`tests/skillset/test_openai_plugin_materialization.py` hard-codes the historical beta.3 release manifest/version for repository-level assertions, causing the current committed beta.1 Plugin to be compared against historical beta.3 version/tree digests.

Repair semantics:

- repository-level assertions for the **current committed Plugin** MUST bind to `skillset/releases/aegis-0.2.0-beta.1.json` and release version `0.2.0-beta.1`;
- exact-nine current Plugin trees MUST match the current beta.1 release manifest / current canonical Skills;
- materializer reproducibility/check tests may exercise the current beta.1 release state;
- immutable beta.3 proof MUST remain separate and MUST NOT be redefined as a requirement that the current Plugin equal beta.3;
- historical beta.3 manifests, notes, tag, GitHub Release, and published assets MUST remain untouched;
- the isolated historical validation already implemented in `.github/workflows/skillset.yml` remains required and unweakened.

This is an oracle-boundary repair only. It does not authorize changes to `scripts/build_openai_plugin_materialization.py`, `scripts/build_aegis_distributions.py`, `tools/aegis_skillset/**`, canonical `skills/**`, or historical release data.

## 5. Required repair B — exact-head candidate evidence

Root cause established by workflow run `33861131795`:

PR-triggered Actions checked out the synthetic PR merge ref, while `scripts/build_candidate_plugin_parity.py` derives `source_revision` from `git rev-parse HEAD`. The first parity artifact therefore bound its `source_revision` to the PR merge ref instead of the actual P32 branch head.

Repair only `.github/workflows/skillset.yml` so that PR evidence executes against the exact PR head:

- `actions/checkout@v4` MUST checkout `${{ github.event.pull_request.head.sha || github.sha }}` (or an equivalent exact-head expression);
- candidate parity generation MUST therefore observe the actual checked-out branch head via `git rev-parse HEAD`;
- candidate parity artifact naming MUST use the same exact evidence revision rather than the synthetic PR merge SHA;
- push behavior MUST remain bound to the push commit;
- do not modify `scripts/build_candidate_plugin_parity.py`.

Final evidence is invalid unless:

```yaml
candidate_parity:
  source_revision: <exact final PR #66 head>
  artifact_name_revision: <same exact final PR #66 head>
  exact_nine: true
  public_release: false
```

The earlier artifact `9932157642` is historical intermediate evidence only and is not sufficient as the final exact-result parity artifact.

## 6. P33 resume behavior

P33 must preserve valid existing PR #66 work and resume from the first incomplete verified step. Do not regenerate already-correct release surfaces merely because execution is resuming.

At resume:

1. validate repository identity before package/anchor/cursor reasoning;
2. resolve this exact successor `package_ref` and same-repository materialization ref;
3. inspect PR #66 head and classify against `resume_cursor`;
4. preserve all valid authorized candidate work already materialized on PR #66;
5. apply only repair A and repair B plus any deterministic generated output already authorized by P31-02;
6. rerun the complete evidence set at the new exact result revision;
7. repeat beta.1 tag/Release collision preflight before final return;
8. materialize the exact final result on PR #66 before returning to CONTROL_REVIEW.

## 7. Required final evidence

All applicable checks from P31-02 remain required, including full Skillset, Project State, Control Plane and eval regressions plus deterministic distribution/materialization checks.

Additionally require:

- `tests/skillset/test_openai_plugin_materialization.py` current Plugin assertions PASS against beta.1;
- isolated beta.3 historical source validation remains PASS;
- final PR CI checks out exact PR #66 head;
- candidate Installation Kit is regenerated/uploaded for the exact final result revision;
- candidate Plugin parity artifact is regenerated and has `source_revision == exact_result_revision`;
- candidate parity artifact name is bound to the same exact result revision;
- no unresolved required refs;
- PR #66 remains draft/unmerged during P33;
- beta.1 tag and GitHub Release remain absent;
- no Project State mutation, P24 verdict, SERVICE_PROFILE, rollout expansion, or public release occurs.

## 8. Exit and blocked return

P33 may return `READY_FOR_CONTROL_REVIEW` only when the exact result is reviewer-resolvable through PR #66, all required CI/evidence is green on that exact result, final artifacts are resolvable, and release-identity collision checks remain clean.

If exact-result evidence cannot be materialized, return `BLOCKED_EVIDENCE`. If cursor ancestry diverges, return `BLOCKED_EXECUTION_DIVERGENCE`. If another authored path is required outside this repaired package, return `BLOCKED_SCOPE` rather than widening again.

P31 repair ends at package materialization. It does not execute P33, issue P24 readiness, merge PR #66, create `v0.2.0-beta.1`, publish a GitHub Release, authorize SERVICE_PROFILE, or expand rollout.
