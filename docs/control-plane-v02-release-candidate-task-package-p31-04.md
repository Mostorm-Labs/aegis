# Aegis Control Plane v0.2 — P31 Release-Candidate Task Package Repair 2

Status: **P31 / CONTROL_REASONING / MATERIALIZED SCOPE REPAIR**

Package ID: `RC-I01-P31-04`

Task ID: `RC-I01`

Primary Owner: `aegis-implementation`

Next execution stage: `P33 Resume Interrupted Work`

Preferred execution surface: `CODE_EXECUTION / Codex`

This package is a second narrow additive repair of `RC-I01-P31-03`. It does not re-plan RC-I01, reopen Authority, change release identity, discard or replay the existing beta.1 candidate, or broaden the release-package-only purpose. It authorizes the single additional workflow-regression oracle path required to implement the already-authorized exact-head evidence semantics without masking the old synthetic-merge-SHA expectation.

## 1. Task identity

```yaml
package_id: RC-I01-P31-04
task_id: RC-I01
purpose: CONTROL_PLANE_V02_RELEASE_CANDIDATE_MATERIALIZATION
primary_owner: aegis-implementation
next_stage: P33
release_version: 0.2.0-beta.1
release_tag: v0.2.0-beta.1
product_form: PLUGIN_PLUS_EXACT_NINE_SKILLS
implementation_scope: RELEASE_PACKAGE_ONLY
supersedes_package_id: RC-I01-P31-03
supersedes_package_ref: 5f3e2ec1feaecbb27f289d1a563ab0aeed30e159
supersession_reason: P31_WORKFLOW_ORACLE_SCOPE_GAP_REPAIR
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
    - first P33 reconciliation classified EXACT_CURSOR and found workflow-oracle scope gap before mutation
  next_action: update the three authorized test/workflow files, rerun complete exact-head evidence, and materialize the final result on PR #66
```

`Task Anchor != Execution Cursor`. P33 must reconcile against the same accepted cursor. If PR #66 is still exactly at `ffc80d...`, classify `EXACT_CURSOR`; a valid descendant requires delta inspection; incompatible history fails closed.

## 2. Trusted basis retained unchanged

Retain P30 and all accepted Control Plane / repository-identity Authority, Gate, integration and Project State bases from P31-03. In particular:

- P30 re-plan is **not** required;
- Authority reopen is **not** required;
- current main/task anchor remains `63d65472278448f8d2b5fa2bc2991189dcd0825a` unless fresh state contradicts it;
- published beta.3 remains immutable at `v0.1.0-beta.3 / 38bf619ede0615431c7517bc0e07984136af28cf`;
- beta.1 tag and GitHub Release must remain absent throughout P33;
- current candidate PR #66 must be preserved rather than restarted.

## 3. Scope repair

Authorization remains path/pattern based. All P31-03 authorizations and forbidden paths remain unchanged.

Add exactly this authored path:

```text
tests/skillset/test_workflow_paths.py
```

Retain the previously repaired authored paths:

```text
tests/skillset/test_openai_plugin_materialization.py
.github/workflows/skillset.yml
```

No other authored path is added by this package.

## 4. Required repair set

### A. Current-vs-historical Plugin oracle

Update `tests/skillset/test_openai_plugin_materialization.py` so repository-level/current materialization assertions bind to `skillset/releases/aegis-0.2.0-beta.1.json` and release version `0.2.0-beta.1`. Exact-nine Plugin trees must match the current beta.1 release manifest/current canonical Skills. Immutable beta.3 proof remains separate through the isolated historical source validation already present in the workflow.

### B. Exact-head candidate evidence

Update `.github/workflows/skillset.yml` so PR-triggered evidence checks out the exact PR head SHA, while push behavior remains bound to the push SHA. Candidate parity generation must therefore observe the actual execution head via `git rev-parse HEAD`, and the parity artifact name must use the same exact evidence revision rather than the synthetic PR merge SHA.

Acceptable invariant:

```yaml
exact_evidence_revision: ${{ github.event.pull_request.head.sha || github.sha }}
checkout_ref: <exact_evidence_revision>
candidate_parity.source_revision: <exact_evidence_revision>
candidate_parity.artifact_name_revision: <exact_evidence_revision>
```

Do not modify `scripts/build_candidate_plugin_parity.py`.

### C. Workflow regression oracle

Update `tests/skillset/test_workflow_paths.py` to require the exact-head checkout and exact-head parity artifact-name expression above, and to reject the stale PR artifact naming assumption `aegis-candidate-plugin-parity-${{ github.sha }}` as the sole PR evidence identity.

This test change is only an oracle update for already-authorized exact-head semantics; it does not authorize new workflow functionality beyond repair B.

## 5. Required P33 verification

After applying only repairs A/B/C, rerun the complete evidence set required by P31-03/P31-02. Final hosted evidence must prove:

- Skillset tests PASS, including both updated oracle files;
- Project State regressions PASS;
- applicable Control Plane/eval checks PASS;
- deterministic distribution and beta.1 Plugin materialization checks PASS;
- isolated beta.3 historical source validation remains PASS and unchanged in meaning;
- PR workflow checkout revision equals exact final PR #66 head;
- candidate Installation Kit is regenerated/uploaded from the exact final result;
- candidate Plugin parity artifact has `source_revision == exact_result_revision`;
- candidate parity artifact name carries the same exact result revision;
- no unresolved required refs;
- PR #66 stays draft and unmerged during P33;
- beta.1 tag/Release remain absent;
- no Project State mutation, P24 verdict, SERVICE_PROFILE, rollout expansion, merge or public release occurs.

## 6. Exit / blocked return

Return `READY_FOR_CONTROL_REVIEW` only when PR #66 resolves the exact final revision and all required hosted evidence/artifacts are green and exact-head bound. If another authored path is required, return `BLOCKED_SCOPE`; if evidence cannot be durably materialized, return `BLOCKED_EVIDENCE`; if cursor ancestry diverges, return `BLOCKED_EXECUTION_DIVERGENCE`.

This P31 repair itself does not execute P24, merge PR #66, create the beta.1 tag, publish a GitHub Release, mutate Project State, authorize SERVICE_PROFILE, or expand rollout.
