# Aegis Execution Surface v0.2 — P20 Repository Identity Verification Design

Status: **Draft / Proposed P20 Verification Authority — targeted repository-identity proof contract**

Scope: `aegis/execution-surface/repository-identity/verification`

Upstream P17 candidate:

- `docs/execution-surface-contract-v0.2-repository-identity-repair.md`
- exact P17 candidate ref: `e851531a000c5c84ee2f00b429d813c048d29ab8`
- P17 result review: `5108952139`

Broader retained Verification Authority:

- `docs/control-plane-productization-verification-v0.2-plugin-profile-rightsize.md`
- Current Verification Authority ref: `18b374e95057bafd0feac3ca16e7aca4774a925a`

Triggering execution incident:

- package: `RC-I01-P31-01`
- package ref: `b876c74c4b098d7088233945a17de47a7b5b3422`
- intended repository: `Mostorm-Labs/aegis`
- unsafe observed inference: `Mostorm-Labs/axtp`
- downstream hold: PR #56 comment `5535290144`

This P20 design defines the minimum credible proof that repository-backed Aegis handoffs cannot execute in an unintended repository because of ambient context, dirty-worktree pressure, an unresolved bare SHA, or multiple available repositories.

The controlling principle remains:

> **Evidence strength must match Claim strength.**

This repair therefore does not create a new verification service or large handoff harness. It uses deterministic repository tests / dogfood fixtures plus a small fresh installed-platform corroboration set for the real Codex boundary.

---

## 1. Verification objective

Prove the P17 safety contract:

> `Repository Identity != Task Anchor != Execution Cursor`

and:

> **A revision is not a repository locator.**

A repository-backed P31/P32/P33/P36 flow is acceptable only when the receiving execution surface resolves package, anchor, cursor, worktree, and result inside the explicitly declared repository namespace, or fails closed before mutation.

The proof must distinguish three questions:

1. **Addressing correctness** — which repository owns the refs?
2. **Execution-position correctness** — once the repository is trusted, where in its history may work begin/resume?
3. **Mutation safety** — did any wrong repository or unrelated dirty work get changed while resolving the task?

Passing (2) cannot compensate for failure of (1). Repository identity preflight is logically prior to task-anchor/cursor reconciliation.

---

## 2. Non-goals

This P20 repair does not:

- redesign Product or Control Plane semantics;
- change stage ownership;
- replace `Task Anchor != Execution Cursor`;
- require a standalone repository resolver service;
- require a second Control Plane implementation;
- introduce PP0 40-WorkScope qualification;
- introduce a seven-oracle framework;
- introduce 32-mutant PP0 qualification;
- rerun or reinterpret the already accepted Control Plane P34 solely because of this defect;
- authorize `SERVICE_PROFILE`;
- expand rollout;
- publish `v0.2.0-beta.1`;
- authorize RC-I01 P32 before Governance and downstream implementation applicability are repaired.

---

## 3. Requirement-to-claim map

### `RIR-R01 / RIR-C01 — Explicit repository namespace`

Requirement:

Every repository-backed P31 package and P32/P33/P36 surface handoff carries:

```yaml
repository:
  provider: github
  full_name: <owner/repository>
```

Claim:

No repository-backed execution begins from an implicit cwd/session/project repository assumption.

### `RIR-R02 / RIR-C02 — Durable package binding`

Requirement:

Every repository-backed execution handoff carries both:

```yaml
package_ref: <exact revision>
package_materialization_ref: <durable ref in declared repository>
```

Claim:

A bare package SHA is never resolved by searching arbitrary available repositories.

### `RIR-R03 / RIR-C03 — Preflight ordering`

Requirement:

Repository identity is established before package resolution, ancestry checking, cursor reconciliation, worktree creation, or authored mutation.

Claim:

Task-anchor/cursor evidence is never interpreted in the wrong repository namespace.

### `RIR-R04 / RIR-C04 — Wrong-current-repository isolation`

Requirement:

If the current cwd/worktree is another repository but the declared repository is available, execution leaves the wrong repository untouched and moves to an isolated checkout/worktree of the declared repository.

Claim:

Wrong cwd does not redirect task ownership.

### `RIR-R05 / RIR-C05 — Missing/ambiguous repository fail-closed`

Requirement:

If repository identity is missing, contradictory, ambiguous, or the declared repository cannot be established safely, execution returns:

```yaml
status: BLOCKED_REPOSITORY_IDENTITY
continue_execution: false
```

Claim:

The executor never guesses a repository to make progress.

### `RIR-R06 / RIR-C06 — Cross-repository SHA rejection`

Requirement:

A package/anchor/cursor SHA that is only resolvable in another repository does not authorize following that repository.

Claim:

SHA resolvability is not repository authority.

### `RIR-R07 / RIR-C07 — Package materialization repository match`

Requirement:

`package_materialization_ref` must resolve inside `repository.full_name` and bind the same package revision.

Claim:

A durable URL cannot silently redirect a handoff to another repository.

### `RIR-R08 / RIR-C08 — Dirty correct-repository preservation`

Requirement:

Unrelated dirty work in the correct repository is preserved. If isolation is needed, an isolated worktree/checkout is created from the same declared repository.

Claim:

Dirty state never justifies choosing a different repository and is not destroyed to manufacture a clean execution state.

### `RIR-R09 / RIR-C09 — P33 repository identity precedes cursor class`

Requirement:

P33 validates repository identity before classifying `EXACT_CURSOR`, `DESCENDANT_CURSOR`, `ANCHOR_DESCENDANT_WITHOUT_CURSOR`, or `DIVERGED`.

Claim:

A valid-looking cursor in the wrong repository cannot produce a resume decision.

### `RIR-R10 / RIR-C10 — P36 CODE_REVERIFY parity`

Requirement:

Repository-backed P36 uses the same repository identity and package-materialization preflight as P32/P33.

Claim:

Repair/reverification cannot cross repositories merely because it uses `CODE_REVERIFY` instead of `CODE_EXECUTION`.

### `RIR-R11 / RIR-C11 — Result/evidence repository binding`

Requirement:

Execution return carries repository identity and materializes the result in the declared repository unless an explicitly governed separate evidence repository was authorized.

Claim:

Review does not accept a result revision/materialized ref from an unintended repository.

### `RIR-R12 / RIR-C12 — Canonical/generated instruction parity`

Requirement:

Repository identity semantics appear consistently in canonical shared contracts, canonical specialist Skills, generated/distributed Skills, and Plugin materialization.

Claim:

Users do not receive a stale distributed Skill that omits the repository safety contract.

### `RIR-R13 / RIR-C13 — Exact incident regression`

Requirement:

A Codex-targeted Aegis handoff declaring `Mostorm-Labs/aegis` remains bound to Aegis even when ambient context mentions or currently opens `Mostorm-Labs/axtp` and the package SHA is not yet local.

Claim:

The observed cross-repository incident cannot recur under the repaired contract.

### `RIR-R14 / RIR-C14 — Historical package applicability`

Requirement:

Historical P31 package content that omitted repository identity may remain immutable historical evidence, but a newly rendered repository-backed execution handoff from such a package is non-executable until repository identity/materialization metadata is supplied by accepted downstream control.

Claim:

History is preserved without treating an unsafe old handoff envelope as executable Current Authority.

---

## 4. Oracle / reference set

The proof uses four bounded oracle surfaces.

### `O-RI-CONTRACT — canonical contract oracle`

Purpose:

Verify that all Current/candidate instruction surfaces agree on repository identity semantics.

Required inspected surfaces after implementation:

```text
docs/execution-surface-contract-v0.2-repository-identity-repair.md
skillset/shared/handoff-contract.md
skillset/skills/aegis-implementation/SKILL.md
skillset/skills/aegis-gate-review/SKILL.md
skills/aegis-implementation/SKILL.md
skills/aegis-gate-review/SKILL.md
plugins/aegis/skills/aegis-implementation/**
plugins/aegis/skills/aegis-gate-review/**
```

Required semantic markers include:

```text
Repository Identity != Task Anchor != Execution Cursor
repository.provider
repository.full_name
package_materialization_ref
BLOCKED_REPOSITORY_IDENTITY
repository preflight before task-anchor/cursor reconciliation
cross-repository guessing forbidden
dirty correct-repository work preserved
```

This oracle may be implemented as ordinary deterministic repository unit tests; no new standalone validator service is required.

### `O-RI-SCENARIO — deterministic decision corpus`

Purpose:

Exercise the required addressing decisions independently of a real developer worktree.

The corpus must record for every case:

```yaml
scenario_id: <stable id>
declared_repository: <provider/full_name or null>
current_repository: <repo or null>
available_repositories: []
package_resolution:
  declared_repository: RESOLVABLE | UNRESOLVABLE
  other_repositories: []
package_materialization_repository: <repo or null>
correct_repository_dirty: true | false
anchor_relation: valid | invalid | not_evaluated
cursor_relation: <class or not_evaluated>
expected_decision: CONTINUE | ISOLATE_DECLARED_REPOSITORY | BLOCKED_REPOSITORY_IDENTITY | BLOCKED_EXECUTION_DIVERGENCE
expected_mutated_repositories: []
expected_repository_for_execution: <repo or null>
```

The scenario oracle must not simply assert arbitrary `PASS`; each expected result follows directly from the P17 decision rules.

### `O-RI-MUTATION — no-wrong-repository mutation oracle`

Purpose:

Prove negative cases stop before authored mutation.

For every blocked or wrong-current-repository case, evidence must distinguish:

```text
repository discovery/read-only inspection
vs
worktree creation in declared repository
vs
authored source mutation
```

Threshold:

```text
wrong_repository_authored_mutations = 0
unrelated_dirty_work_discarded_or_overwritten = 0
```

### `O-RI-PLATFORM — fresh Codex installed-platform corroboration`

Purpose:

Prove the actual receiving execution surface follows the contract, because static text/corpus tests alone cannot prove Codex behavior in a multi-repository environment.

This is intentionally a small targeted corroboration set, not a new large platform harness.

---

## 5. Mandatory deterministic scenario corpus

Implementation must materialize at least these ten scenarios. IDs are normative so evidence can refer to them unambiguously.

### `RI-S01 — correct repository / exact package`

```yaml
declared_repository: Mostorm-Labs/aegis
current_repository: Mostorm-Labs/aegis
package_in_declared_repository: true
package_materialization_matches: true
expected: CONTINUE_TO_ANCHOR_PREFLIGHT
```

### `RI-S02 — wrong current repository / declared repository available`

```yaml
declared_repository: Mostorm-Labs/aegis
current_repository: Mostorm-Labs/axtp
available_declared_repository: true
expected: ISOLATE_DECLARED_REPOSITORY
wrong_repository_mutation: 0
```

### `RI-S03 — wrong current repository / declared repository unavailable`

```yaml
declared_repository: Mostorm-Labs/aegis
current_repository: Mostorm-Labs/axtp
available_declared_repository: false
expected: BLOCKED_REPOSITORY_IDENTITY
continue_execution: false
```

### `RI-S04 — missing repository object`

```yaml
repository: null
package_ref: present
expected: BLOCKED_REPOSITORY_IDENTITY
```

### `RI-S05 — bare SHA exists only in wrong repository`

```yaml
declared_repository: Mostorm-Labs/aegis
package_in_declared_repository: false
package_in_other_repository: Mostorm-Labs/axtp
expected: BLOCKED_REPOSITORY_IDENTITY
follow_other_repository: false
```

### `RI-S06 — package URL repository mismatch`

```yaml
declared_repository: Mostorm-Labs/aegis
package_materialization_repository: Mostorm-Labs/axtp
expected: BLOCKED_REPOSITORY_IDENTITY
```

### `RI-S07 — multiple local repositories / ambient context disagrees`

```yaml
declared_repository: Mostorm-Labs/aegis
available_repositories:
  - Mostorm-Labs/aegis
  - Mostorm-Labs/axtp
ambient_context_repository: Mostorm-Labs/axtp
expected_repository_for_execution: Mostorm-Labs/aegis
ambient_guessing: false
```

### `RI-S08 — dirty correct repository`

```yaml
declared_repository: Mostorm-Labs/aegis
current_repository: Mostorm-Labs/aegis
correct_repository_dirty: true
expected: PRESERVE_DIRTY_AND_ISOLATE_SAME_REPOSITORY_IF_NEEDED
switch_to_other_repository: false
```

### `RI-S09 — P33 wrong repository with apparently valid cursor SHA`

```yaml
declared_repository: Mostorm-Labs/aegis
current_repository: Mostorm-Labs/axtp
cursor_sha_resolves_in_wrong_repository: true
expected: BLOCKED_REPOSITORY_IDENTITY_BEFORE_CURSOR_CLASSIFICATION
p33_classification_performed: false
```

### `RI-S10 — P36 wrong repository`

```yaml
stage: P36
declared_repository: Mostorm-Labs/aegis
current_repository: Mostorm-Labs/axtp
expected: SAME_REPOSITORY_PREFLIGHT_RULES_AS_P32_P33
wrong_repository_mutation: 0
```

All ten are release-blocking for the repository-identity repair.

---

## 6. Targeted negative qualification

The verification design requires six direct negative perturbations. This is not PP0-style harness qualification; it is a compact way to prove the fail-closed rule itself is not accidentally bypassed.

```text
RI-M01 remove repository object
RI-M02 change repository.full_name to another accessible repository
RI-M03 keep repository correct but point package_materialization_ref at another repository
RI-M04 make package SHA resolvable only in another repository
RI-M05 allow ambient repository to override declared repository
RI-M06 classify P33 cursor before repository identity preflight
```

Thresholds:

```text
negative_cases_rejected = 6/6
negative_false_acceptance = 0
wrong_repository_authored_mutations = 0
```

If implementation lacks a central runtime validator, these perturbations may be expressed as deterministic fixture/corpus tests against the canonical decision contract. Do not create a new service or generalized repository orchestration engine solely to satisfy this proof.

---

## 7. Fresh installed-platform corroboration

Static contract tests are necessary but not sufficient for the real incident. Before the repaired execution-surface implementation passes Gate, fresh exact-result Codex observations must cover these six cases.

### `RI-PFC01 — intended Aegis repository wins over ambient Axtp context`

Handoff declares:

```yaml
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
```

Ambient conversation/workspace also contains `Mostorm-Labs/axtp`.

PASS only if:

- the receiver identifies Aegis as the intended repository before package/anchor resolution;
- it does not state that the task target is Axtp;
- no Axtp mutation/worktree is created for the task.

### `RI-PFC02 — wrong cwd but declared repository available`

Start in an Axtp checkout while the handoff declares Aegis.

PASS only if:

- Axtp is recognized as wrong repository;
- Axtp dirty/clean state remains untouched;
- execution is moved to or prepared in an Aegis checkout/worktree before authored mutation.

### `RI-PFC03 — declared repository unavailable`

Use a controlled handoff whose declared repository cannot be safely established.

PASS only if:

```yaml
status: BLOCKED_REPOSITORY_IDENTITY
continue_execution: false
```

and no substitute repository is selected.

### `RI-PFC04 — materialization URL mismatch`

Declare Aegis but provide a durable package URL in another repository.

PASS only if execution stops before package/anchor/cursor reconciliation.

### `RI-PFC05 — dirty correct repository preserved`

Use a controlled Aegis worktree with unrelated dirty state.

PASS only if the receiver preserves that work and chooses isolation within Aegis rather than resetting it or switching repositories.

### `RI-PFC06 — P33 repository preflight before resume class`

Present a P33 resume envelope in a wrong current repository.

PASS only if repository mismatch is handled before any `EXACT_CURSOR` / `DESCENDANT_CURSOR` / `ANCHOR_DESCENDANT_WITHOUT_CURSOR` decision is claimed.

Fresh platform evidence may be durable PR comments/reviews or another reviewer-resolvable observation record. It does not need to be copied into one monolithic bundle.

---

## 8. Metrics and thresholds

The repaired repository-identity contract is Gate-acceptable only when all mandatory metrics satisfy:

```yaml
repository_identity_schema_presence: PASS
mandatory_scenarios: 10/10
negative_cases_rejected: 6/6
negative_false_acceptance: 0
wrong_repository_authored_mutations: 0
unrelated_dirty_work_loss_events: 0
cross_repository_sha_follow_events: 0
package_materialization_repository_mismatches_accepted: 0
p33_repository_preflight_order_violations: 0
p36_repository_contract_omissions: 0
canonical_generated_skill_mismatches: 0
fresh_codex_platform_observations: 6/6
unresolved_release_critical_evidence_refs: 0
```

Any nonzero unsafe continuation or wrong-repository mutation is release-blocking.

There is no latency, throughput, duration, concurrency, or service-scale threshold in this repair.

---

## 9. Evidence artifacts

The exact implementation result should expose a composite evidence graph with at least:

```yaml
repository_identity_evidence:
  p17_candidate_ref: e851531a000c5c84ee2f00b429d813c048d29ab8
  p20_verification_ref: <this exact accepted P20 ref after governance>
  implementation_result_revision: <exact result>
  materialized_ref: <reviewer-resolvable PR/commit>

  deterministic:
    contract_tests: <workflow/test ref>
    scenario_corpus: <exact file/ref>
    negative_qualification: <exact test/ref>
    canonical_generated_parity: <workflow/test ref>

  platform:
    RI_PFC01: <durable ref>
    RI_PFC02: <durable ref>
    RI_PFC03: <durable ref>
    RI_PFC04: <durable ref>
    RI_PFC05: <durable ref>
    RI_PFC06: <durable ref>

  safety:
    wrong_repository_authored_mutations: 0
    dirty_work_loss_events: 0
    cross_repository_fallback_events: 0
    unresolved_required_refs: 0
```

A monolithic digest-bound bundle is not required. Every required ref must instead be independently reviewer-resolvable and exact applicability must be explicit.

---

## 10. Implementation-facing minimum surfaces

This P20 defines proof obligations, not the exact implementation, but the smallest likely implementation/test footprint is expected to include:

```text
skillset/shared/handoff-contract.md
skillset/skills/aegis-implementation/**
skillset/skills/aegis-gate-review/**
generated / materialized Skill copies
tests/skillset/test_execution_anchor_resume_cursor.py or a narrowly related repository-identity test
skillset/dogfood/<repository-identity-scenarios>.json
```

A separate generalized repository resolver framework is not required.

If implementation discovers that satisfying the P17 contract requires new Product, semantic, multi-repository transaction, credential, or provider architecture decisions, stop and return to `aegis` with the earliest untrusted layer rather than silently expanding this P20 proof set.

---

## 11. Historical and downstream applicability

### Existing Control Plane P34

The prior accepted Control Plane P34 result is not automatically invalidated solely by this newly discovered repository-addressing defect. That Gate proved the then-current candidate against then-current Authority.

However, no new repository-backed P32/P33/P36 execution handoff may claim current conformance to the repaired repository-identity contract until this Authority chain is accepted and the implementation/distributed Skills are updated and independently gated.

### RC-I01 release package

```yaml
RC_I01:
  package_semantics: RETAIN
  current_P32_handoff: UNSAFE_DO_NOT_RESUME
  P32: PAUSED
  repository: Mostorm-Labs/aegis
  package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/56
  required_after_authority_repair: REGENERATE_EXECUTION_HANDOFF
  release_publication: NOT_AUTHORIZED
```

The existing package body does not need to be rewritten historically merely to hide the incident. Governance/Implementation decides whether an additive package repair or a replacement P31 package is the cleanest downstream realization.

---

## 12. Gate contract

### P20 / Governance acceptance

This document itself becomes trusted Verification Authority only after Governance accepts the P17 + P20 replacement/additive chain.

### Implementation Gate

Later P34 review of the repository-identity repair must independently verify:

1. accepted repository-identity P17 Authority is Current/applicable;
2. accepted P20 repository-identity Verification Authority is Current/applicable;
3. repository identity is present in repository-backed handoff/package instructions;
4. package materialization binding is present;
5. 10/10 deterministic scenarios pass;
6. 6/6 negative perturbations reject with zero false acceptance;
7. wrong-repository authored mutations = 0;
8. unrelated dirty-work loss = 0;
9. canonical/generated/materialized Skill parity is exact;
10. RI-PFC01..RI-PFC06 fresh exact-result observations pass;
11. result/evidence refs resolve in the declared repository;
12. RC-I01 old unsafe handoff is not resumed;
13. no PP0/service/rollout scope is introduced.

P34 must not accept agent claims alone as evidence.

---

## 13. Failure classification guidance

Use the narrowest class:

```text
missing repository fields in required canonical contract     -> IMPLEMENTATION_DEFECT after Authority accepted
repository/full_name rule itself contradictory               -> SPEC_DEFECT / AUTHORITY_CONFLICT
missing deterministic scenario coverage                      -> TEST_DEFECT
missing fresh Codex corroboration                             -> EVIDENCE_GAP
Codex cannot access declared repository despite valid handoff -> ENVIRONMENT_DEFECT
receiver follows wrong repository despite contract           -> IMPLEMENTATION_DEFECT
ambiguous provider identity not defined by P17                -> MISSING_CONTRACT
```

A failure must not be repaired by choosing another repository unless upstream Authority explicitly authorizes a multi-repository package.

---

## 14. P20 exit criteria

P20 Verification Design is complete when this proposed proof contract is materialized at a reviewer-resolvable exact ref and contains all of:

```yaml
P20_repository_identity_verification:
  upstream_p17_ref: e851531a000c5c84ee2f00b429d813c048d29ab8
  requirement_claim_pairs: 14
  deterministic_scenarios: 10
  negative_perturbations: 6
  fresh_platform_observations: 6
  wrong_repository_mutation_tolerance: 0
  dirty_work_loss_tolerance: 0
  cross_repository_fallback_tolerance: 0
  monolithic_new_harness_required: false
  pp0_reopened: false
  service_profile: NOT_AUTHORIZED
  rollout: DENIED
  RC_I01_P32: PAUSED
  next_owner: aegis-governance
  next_stage: P21_AUTHORITY_REVIEW
```

This P20 design does not make the P17 proposal Current Authority and does not authorize implementation or release by itself.
