# RI-I01-P31-01 — Repository Identity Execution Handoff Repair Task Package

Status: **P31 / CONTROL_REASONING**

## Task identity

```yaml
package_id: RI-I01-P31-01
slice_id: RI-I01
name: REPOSITORY_IDENTITY_EXECUTION_HANDOFF_REPAIR
stage_owner: aegis-implementation
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
task_anchor:
  revision: 8fc76fc6c10951c4748c04be60bbc1c953e6de7e
  relation: ancestor
resume_cursor: null
```

The exact `package_ref` is the final P31 materialized revision and is recorded by the P31 stage result. A P32 handoff is non-executable unless it carries that exact revision together with this package's same-repository durable materialization ref.

## Current Authority

- P17 repository identity Platform Authority: `e851531a000c5c84ee2f00b429d813c048d29ab8`
- repository-identity core P20 Authority: `61aa42e98558a1621b0228223835473f248ee869`
- repository-identity materialization-proof Authority: `8fc76fc6c10951c4748c04be60bbc1c953e6de7e`
- P23 targeted supersession review: `5109657871`
- P30 implementation plan: `6d3604c13e5f3c8389a7e3598bf01bd218ca0bc2`
- P30 review: `5109766128`

Normative invariants:

> `Repository Identity != Task Anchor != Execution Cursor`

> `A revision is not a repository locator.`

## Purpose

Implement the narrow repository-addressing repair so Aegis repository-backed P31/P32/P33/P36 work cannot select, mutate, resume, repair, or materialize evidence in an unintended repository because of ambient context, cwd, another checkout, a dirty worktree, or a bare SHA.

This is instruction-first. Do not introduce a repository resolver service, daemon, generalized cross-repository orchestrator, new Product object, or SERVICE_PROFILE behavior.

## Authorized changes

### A. Repository-bound canonical handoff semantics

Modify:

- `skillset/shared/handoff-contract.md`
- `skillset/skills/aegis-implementation/SKILL.md`
- `skillset/skills/aegis-implementation/references/implementation-control.md`
- `skillset/skills/aegis-gate-review/SKILL.md`
- `skillset/skills/aegis-gate-review/references/gate-review.md`

Repository-backed P31/P32/P33/P36 must require:

```yaml
repository:
  provider: github
  full_name: <owner/repository>
package_ref: <exact package revision>
package_materialization_ref: <durable same-repository ref>
task_anchor:
  revision: <trusted revision>
  relation: ancestor
```

Receiving order is normative:

```text
repository identity
-> declared-repository checkout/worktree
-> package resolution in declared repository
-> package_materialization_ref repository match
-> task_anchor ancestry
-> resume_cursor classification if applicable
-> authored mutation
```

Missing/mismatched/ambiguous/unavailable declared repository must return:

```yaml
status: BLOCKED_REPOSITORY_IDENTITY
continue_execution: false
```

P33 must establish repository identity before claiming `EXACT_CURSOR`, `DESCENDANT_CURSOR`, `ANCHOR_DESCENDANT_WITHOUT_CURSOR`, or `DIVERGED`. P36 CODE_REVERIFY uses the same repository preflight before repair mutation.

### B. Deterministic repository-identity proof

Create/update only the narrow proof surfaces needed by P20/P30:

- `skillset/dogfood/repository-identity-v0.2.json`
- `skillset/dogfood/repository-identity-negative-v0.2.json`
- `tests/skillset/test_repository_identity_handoff.py`
- `tests/skillset/test_execution_anchor_resume_cursor.py`

Mandatory: `RI-S01..RI-S10 = 10/10`, `RI-M01..RI-M06 = 6/6`, `negative_false_acceptance = 0`.

Safety thresholds:

```yaml
wrong_repository_authored_mutations: 0
unrelated_dirty_work_loss_events: 0
cross_repository_sha_follow_events: 0
package_materialization_repository_mismatches_accepted: 0
p33_repository_preflight_order_violations: 0
p36_repository_contract_omissions: 0
```

### C. Separate immutable beta.3 history from current candidate Plugin parity

Authorized implementation surfaces:

- `tools/aegis_skillset/package.py`
- `scripts/build_aegis_distributions.py`
- `tools/aegis_skillset/plugin_materialization.py`
- `scripts/build_openai_plugin_materialization.py`
- new `scripts/build_candidate_plugin_parity.py`
- `tests/skillset/test_openai_plugin_materialization.py`
- new `tests/skillset/test_candidate_plugin_parity.py`

Implement two distinct evidence classes:

1. `PUBLISHED_RELEASE_MATERIALIZATION` validates committed `0.1.0-beta.3` history against its committed Plugin payload without redefining it from current generated Skills.
2. `CANDIDATE_PLUGIN_PARITY_EVIDENCE` is exact-revision, exact-nine, repository-bound to `Mostorm-Labs/aegis`, reviewer-resolvable, non-published, and carries no SemVer/tag/release claim.

Candidate evidence must not write `plugins/aegis/**`.

### D. Regenerate current distributed Skills only

Use existing deterministic generators. Generated `skills/**` must carry the repository identity contract. `skillset/releases/aegis-0.1.0-task6.1.json` may change only if the current development-oracle manifest requires updated digests.

Must remain unchanged from the task anchor:

```text
skillset/releases/aegis-0.1.0-beta.3.json
plugins/aegis/**
```

### E. Exact-head CI evidence

Modify `.github/workflows/skillset.yml` and `tests/skillset/test_workflow_paths.py` only as required to:

- validate beta.3 using explicit published-history modes;
- stop building a current-head candidate labeled `0.1.0-beta.3`;
- retain ordinary non-release development-oracle regressions;
- build/check/upload exact-head `CANDIDATE_PLUGIN_PARITY_EVIDENCE`;
- bind artifact `source_revision` to the exact implementation head SHA.

## Required tests / evidence

Before P32 completion, run the complete P30 regression set, including Skillset validation, generated Skill checks, published beta.3 checks, routing/installed-platform checks, Skillset and Project State unit tests, protected corpus validation, and eval regressions.

Required fresh installed-Codex corroboration at the exact result revision:

```text
RI-PFC01 Aegis declared + ambient Axtp -> Aegis wins; zero Axtp mutation/worktree
RI-PFC02 cwd Axtp + Aegis available -> isolate inside Aegis
RI-PFC03 declared repository unavailable -> BLOCKED_REPOSITORY_IDENTITY; no substitute
RI-PFC04 Aegis declared + package URL in Axtp -> block before package/anchor/cursor
RI-PFC05 dirty correct Aegis repo -> preserve dirty work; isolate inside Aegis
RI-PFC06 P33 wrong repo -> block before cursor classification
```

Every platform observation must identify the exact result revision and be reviewer-resolvable.

## Result materialization obligation

Before returning P32 to CONTROL_REVIEW:

- push the exact result revision;
- expose it through a reviewer-resolvable implementation PR;
- resolve the exact-head candidate parity workflow run/artifact;
- return all `RI-PFC01..RI-PFC06` durable refs;
- return `unresolved_required_refs: 0`.

A local-only commit/worktree/test transcript is insufficient. If exact evidence cannot be materialized, return `BLOCKED_EVIDENCE`.

P32 does not issue a Gate verdict. Next owner after a complete P32 return is `aegis-gate-review -> P34_GATE_REVIEW`.

## Explicit non-goals / forbidden changes

The executor MUST NOT:

- resume or mutate RC-I01 release P32;
- create `0.2.0-beta.1` release manifest, tag, GitHub Release, published Plugin, or Installation Kit;
- modify `skillset/releases/aegis-0.1.0-beta.3.json`;
- modify committed `plugins/aegis/**`;
- weaken historical beta.3 binding;
- reopen PP0 / 40-WorkScope / seven-oracle / 32-mutant work;
- introduce SERVICE_PROFILE, daemon/service runtime, generalized repository resolver/orchestration, or rollout expansion;
- rerun/reinterpret prior Control Plane P34 solely because of this repair;
- rewrite `.aegis` Project State;
- merge the implementation PR;
- publish any release.

## Dependencies and fail-closed behavior

- P30 plan `6d3604c13e5f3c8389a7e3598bf01bd218ca0bc2` must be an ancestor of the implementation start.
- `task_anchor.revision = 8fc76fc6c10951c4748c04be60bbc1c953e6de7e` must be an ancestor of the implementation start.
- Repository identity/package resolution occurs before anchor/cursor reconciliation.
- If `Mostorm-Labs/aegis` cannot be safely established, do not continue in another repository.

Return `BLOCKED_REPOSITORY_IDENTITY` for repository-addressing failure, `BLOCKED_AUTHORITY` for unresolved upstream decisions, `BLOCKED_EVIDENCE` for missing durable evidence, and `BLOCKED_EXECUTION_DIVERGENCE` only after repository identity succeeds and ancestry is genuinely incompatible.

## Exit criteria

```yaml
repository_contract_implemented: true
repository_preflight_before_anchor_cursor: true
mandatory_scenarios: 10/10
negative_cases_rejected: 6/6
negative_false_acceptance: 0
wrong_repository_authored_mutations: 0
dirty_work_loss_events: 0
cross_repository_sha_follow_events: 0
p33_preflight_order_violations: 0
p36_repository_contract_omissions: 0
canonical_generated_skill_mismatches: 0
candidate_plugin_parity:
  artifact_class: CANDIDATE_PLUGIN_PARITY_EVIDENCE
  exact_nine: true
  public_release: false
published_beta3:
  manifest_mutated: false
  plugin_payload_mutated: false
  binding_weakened: false
RC_I01_P32: PAUSED
fresh_platform_observations: 6/6
materialized_ref: REQUIRED
P34_claimed_by_P32: false
```

## P32 handoff rendering rule

Do not render or execute P32 until this P31 package is durably materialized and the handoff carries the exact final `package_ref`, the same-repository `package_materialization_ref`, the repository object, and the task anchor.

Whenever the future handoff uses `preferred_executor: codex`, place this exact prefix immediately before the YAML:

> 请按以下 Aegis handoff 直接执行：以 `package_ref` 为任务授权，按 `task_anchor/resume_cursor` 核对当前状态并从首个未完成步骤继续；若状态冲突则 fail closed。

This P31 package alone does not execute P32.
