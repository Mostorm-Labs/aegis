# Aegis Verification Productization v0.2 — P20 Targeted Verification Contract Repair

Status: **Draft / Proposed Replacement Verification Authority — P20 targeted repair**

Scope: `aegis/verification-productization/verification`

This document is a targeted replacement candidate for the exact P20 v0.1 verification basis:

```yaml
prior_p20_ref: 674e01737621621b8131e35f83313fb0154a9f6d
prior_p20_artifact: docs/verification-productization-verification-v0.1.md
prior_p21_review: 5121075377
prior_p21_disposition: PASS / ACCEPTED_FOR_DOWNSTREAM
```

It does not silently rewrite v0.1. Until a fresh P21 accepts this exact v0.2 candidate, v0.1 remains the previously accepted downstream basis and this document remains Draft / Proposed only. If accepted, v0.2 replaces v0.1 for future Verification Productization planning, packaging, execution, and Gate applicability while preserving v0.1 and its implementation history as immutable provenance.

The repair is intentionally narrow. It addresses two verification-contract defects discovered by the VP-I03 P32 occurrence and leaves all other ECV0 claims, deterministic scenarios, mutants, exact-identity rules, evidence-durability rules, independent completeness semantics, and P34 ownership unchanged unless explicitly amended below.

---

# 1. Role, Authority, objective, and non-goals

## Role

`aegis-verification` owns this P20 repair. Its job is to correct the proof contract, not to make the existing implementation or CI look green.

## Exact upstream Authority retained

```yaml
repository: Mostorm-Labs/aegis
external_current_baseline_at_v0_1_design: 342d6785d8f54dd9beb2c3bb82398f29b405df2f

semantic_basis: 12c968c5c481ad671ce33bcfa088ba8a2fca0f43
semantic_recertification_review: 5121012716

p14_architecture_basis: d9c8f6ac5db4359400fae06e76c51c65bd059bfc
p15_module_design_basis: 665292dcfd7781935243369ee9f676c320f2878a
p16_runtime_flow_basis: 708cf09c01effbcc63c65d45b9b4a67b7a8fc8db
p17_platform_contract_basis: c8f47d049be50d65f88b04ad141650ed6dfdb826

prior_p20_basis: 674e01737621621b8131e35f83313fb0154a9f6d
prior_p20_p21_acceptance: 5121075377
```

The P17 contract remains trusted and unchanged. In particular, it freezes lifecycle surfaces such as `CODE_EXECUTION` and platform capabilities without making Codex, ChatGPT, GitHub Actions, or another provider the lifecycle owner. A provider/executor may change transport or invocation mechanics but may not weaken identity, provenance, completeness, or lifecycle ownership.

## Incident / implementation evidence that triggered this repair

The VP-I03 P32 occurrence is implementation reality and evidence, not Authority:

```yaml
vp_i03_package_id: VP-I03-P31-01
vp_i03_package_ref: a3dd0f1aa08f2686b9169059799555cd597ca503
vp_i03_result_revision: 2fec701cc38bb0d9bcb558d8802d0c7f012f408a
vp_i03_materialization: https://github.com/Mostorm-Labs/aegis/pull/77
p32_blocked_return_review: 5121781308
central_routing_review: 5121799448

observed_deterministic_evidence:
  verification_productization_tests: 83/83_OK
  ecv0_scenarios: 17/17_PASS
  ecv0_mutants: 17/17_DETECTED
  mutant_false_acceptance: 0

exact_hosted_evidence:
  workflow_run: 33973747955
  job: 101326724541
  artifact_id: 9971689270
  artifact_digest: sha256:6e5784c103d7870adc19c35012bb96791a9e772d2da0ac3c7888762bd08aea59
```

That occurrence stopped fail-closed for two earlier-layer defects:

1. `EC-PFC01` was over-constrained to an actual Codex occurrence even though P17's governing semantic requirement is repository/exact-package/capability integrity across the `CODE_EXECUTION` surface.
2. An inherited public-release coherence oracle recomputed a historical `v0.2.0-beta.1` manifest from the current development candidate's generated Skill bytes, making a legitimate non-release Skill change fail while the package simultaneously forbade release-manifest mutation.

## Objective

Repair the minimum verification semantics needed so that future planning can distinguish:

- **what must be true** at a repository-backed execution boundary from **which product happens to execute it**; and
- **historical release identity** from **current candidate release coherence**, using explicit applicability rather than comparing an unrelated development working tree to a published historical manifest.

## Non-goals

This P20 repair does **not**:

- change P02/P03 or P10-P17 Authority;
- redesign Proof Runtime semantics;
- require P18;
- modify any production code, tests, workflow, Skill, generated distribution, release manifest, tag, GitHub Release, Plugin, `.aegis` state, or PR #77 implementation bytes;
- retroactively turn workflow run `33973747955` from failure into success;
- retroactively claim `EC-PFC01`, `EC-PFC03`, or P34 PASS for result `2fec701c...`;
- authorize P30/P31/P32 execution;
- publish this Draft as Current Authority;
- merge or release anything.

---

# 2. Inherited ECV0 contract

Except for the explicit amendments in this document, the exact P20 v0.1 contract at `674e01737621621b8131e35f83313fb0154a9f6d` is inherited unchanged, including:

- `ECV-R01..ECV-R17`;
- `EC-S01..EC-S17`;
- `EC-M01..EC-M17`;
- mutant false acceptance threshold `0`;
- exact result / evidence / Gate identity separation;
- local-only evidence rejection;
- exact-result provider applicability and completion;
- mutable/latest lookup rejection;
- reviewer-resolvable evidence requirement;
- adapter semantic parity;
- independent completeness oracle;
- P34 as the sole formal Gate verdict owner;
- composite evidence graphs being allowed without requiring a monolithic bundle.

The repaired profile is still named `ECV0`. This is a verification-authority revision, not a new verification product.

---

# 3. Repair A — executor-agnostic installed-platform corroboration

## 3.1 Defect classification

```yaml
finding: P20-B2
class: SPEC_DEFECT
prior_contract: EC-PFC01 requires an actual Codex repository / exact package preflight
root_cause: executor brand was made a pass condition even though the upstream P17 Claim is execution-surface capability + exact repository/package identity
owning_layer: P20 Verification Design
```

Codex may remain a valid executor, but Codex identity is not itself the thing being proven by `ECV-R11`, package preflight, or repository-identity integrity.

## 3.2 Revised `O-EC-PLATFORM`

Replace the v0.1 wording that conceptually checks the real `ChatGPT/Codex/GitHub` boundary with the following normative rule:

> `O-EC-PLATFORM` checks fresh installed **execution, control, and provider surfaces** where deterministic fixtures alone cannot prove installed-platform capability or exact identity behavior. Executor/provider identity is recorded as provenance. It becomes a pass condition only when the Requirement explicitly claims behavior unique to that executor/provider.

The platform oracle must distinguish:

```text
lifecycle surface
!= executor product
!= provider
!= repository identity
!= package identity
!= result identity
!= evidence identity
```

## 3.3 Revised `EC-PFC01`

### `EC-PFC01 — Repository-backed execution-surface exact package preflight`

**Requirement.** A fresh repository-backed `CODE_EXECUTION` occurrence must establish the declared repository and exact executable package before mutation or trust-critical execution.

**Required observation.** The occurrence must durably identify, where applicable:

```yaml
repository:
  provider: <exact provider>
  full_name: <exact owner/name>
package_id: <exact package id>
package_ref: <immutable exact ref>
package_materialization_ref: <reviewer-resolvable locator>
task_anchor:
  revision: <exact revision>
  relation: <declared relation>
actual_starting_revision: <exact revision observed at execution start>
execution_surface: CODE_EXECUTION
executor_provenance: <actual executor / client / adapter identity>
capabilities_used:
  - <required repository/materialization capabilities>
```

**Invariant.** Ambient cwd/session repository, a bare SHA, branch name, PR title, executor memory, or another repository that happens to resolve the SHA may not override the declared repository/package binding.

**Pass condition.** The execution remains within the declared repository/package/task binding or fails closed before unauthorized mutation. The evidence is reviewer-resolvable and exact.

**Executor rule.** An authorized ChatGPT repository connector, Codex, or another future repository-backed `CODE_EXECUTION` executor may satisfy this corroboration when it demonstrates the same frozen semantics and capabilities. Merely naming an executor does not satisfy the corroboration.

**Negative rule.** A branch named `codex/...`, an assistant statement saying Codex ran, or an executor-authored handoff cannot substitute for actual execution provenance.

This preserves P17's `Stage Ownership != Execution Surface` and `Provider execution != lifecycle ownership` boundaries.

## 3.4 Revised `EC-PFC02`

Rename the v0.1 `Codex/local evidence durability boundary` to:

### `EC-PFC02 — Execution/local evidence durability boundary`

Produce a local-only test/report artifact from the actual execution surface, then demonstrate that execution does not claim review readiness until an exact reviewer-resolvable evidence/materialization path exists.

The pass condition is executor-agnostic. Local filesystem/worktree/stdout evidence remains staging only regardless of whether the executor is Codex, ChatGPT, or another authorized code surface.

## 3.5 `EC-PFC03` and `EC-PFC04`

These remain semantically unchanged:

- `EC-PFC03` proves GitHub Actions exact-result + terminal/completion applicability for the reviewed candidate.
- `EC-PFC04` is a fresh independent `CONTROL_REVIEW` resolution occurrence and remains exclusively Gate/review-owned. P32 cannot self-issue it.

No historical failed provider occurrence is upgraded by this repair. A new/requalified exact candidate must supply applicable evidence under the accepted repaired contract.

---

# 4. Repair B — historical release identity vs candidate release coherence

## 4.1 Defect classification

```yaml
finding: P20-B1
class: TEST_DEFECT
owning_layer: P20 Verification Design / inherited-evidence applicability
secondary_manifestation: P30/P31 package contradiction
observed_failure: test_public_release_identity_is_coherent
```

The defect is not that the published release identity may be rewritten. The defect is that the inherited oracle used the **current development candidate Skill bytes** as the expected bytes for a **historical published release** even when the candidate explicitly did not claim a release publication.

## 4.2 Publication identity model

Verification must distinguish two different Claims.

### Claim A — Historical published-release identity

A published release is historical immutable evidence bound to its publication occurrence:

```text
release/version identity
+ published/tagged target revision
+ release manifest identity/content
+ published artifact/materialization identity
```

The historical release must be checked against the exact source/materialization it was published from, not against an unrelated future development candidate.

For the motivating occurrence, `v0.2.0-beta.1` publication history is bound to its own published source/integration lineage. A later VP-I03 candidate changing canonical/generated Skill bytes does not rewrite that historical source.

### Claim B — Active candidate release coherence

A current candidate must match a release manifest only when the candidate actually claims to create, replace, republish, or otherwise qualify a release publication whose contract binds that manifest to the candidate bytes.

These Claims are not interchangeable:

```text
historical release remains immutable
!=
current development tree must equal historical release bytes
```

## 4.3 Normative applicability predicate

Before a release-coherence oracle is applied to a candidate, determine its applicability from exact package/Authority scope.

```yaml
candidate_release_coherence_applicable: true
```

only when at least one accepted condition requires the candidate to own release publication semantics, for example:

- the executable package authorizes a release/tag/manifest/publication mutation;
- the candidate explicitly claims to materialize a named release version;
- the Gate Claim being reviewed is release-package parity for that candidate;
- accepted Authority explicitly requires current candidate bytes to equal the active release artifact.

For a candidate whose accepted scope says:

```yaml
release_authorized: false
public_release: false
release_manifest_mutation_authorized: false
```

historical release identity remains relevant only as immutable history / non-regression provenance. Re-rendering the historical manifest from the current candidate tree is **not an applicable candidate-coherence oracle**.

## 4.4 Historical-release oracle

For a non-release development candidate, the inherited release check must establish only the historical properties actually claimed, such as:

1. the checked-in historical release manifest has not been silently rewritten by the candidate;
2. the historical manifest/version remains bound to its exact historical publication source/materialization;
3. any protected published artifact/hash being relied on is resolved from that historical source rather than regenerated from current candidate bytes;
4. the current candidate does not falsely claim `public_release: true` or mutate release publication state outside package authority.

A changed current Skill tree is not, by itself, evidence that a historical release was corrupted.

## 4.5 Active-release oracle

When release coherence **is** applicable, the check remains strict:

- the candidate release manifest must be derived from the candidate's exact release source/materialization;
- manifest/tree/archive/plugin identities must match the exact candidate bytes required by the release contract;
- a mismatch fails closed;
- historical release identity cannot be substituted for a new candidate release;
- no `latest` or branch-relative release identity is sufficient.

This repair therefore does not weaken release verification. It narrows each oracle to the Claim it actually proves.

---

# 5. Mandatory applicability probes added by v0.2

The original `17 scenarios + 17 mutants` remain unchanged. v0.2 adds two **inherited-evidence applicability probes** because the discovered defect is in test applicability rather than Proof Runtime semantics.

These probes are mandatory for any future VP-I03 requalification under v0.2, but they do not renumber `EC-S01..17` or `EC-M01..17`.

## `EC-AP01 — Historical release remains source-bound on non-release candidate`

**Fixture / occurrence.** Start from a repository with an already-published release manifest bound to an exact historical release source. Create a later candidate that legitimately changes canonical/generated Skill bytes while its exact package forbids release/tag/manifest publication.

**Oracle.** Historical release verification resolves the published release's bound source/materialization and confirms the candidate did not mutate that history. It does not regenerate the historical release expectation from the candidate tree.

**Required result.** `PASS` for historical identity if history is intact; no false candidate blocker solely because the current Skill bytes differ.

## `EC-AP02 — Active release candidate mismatch still fails closed`

**Fixture / occurrence.** A candidate explicitly claims release publication/coherence for a version whose manifest is required to describe that candidate's exact release bytes, but the manifest or artifact identity does not match.

**Oracle.** Apply candidate release-coherence verification against the exact candidate source/materialization.

**Required result.** `FAIL / BLOCKED` for the release Claim. Historical publication evidence cannot excuse the mismatch.

## Threshold

```yaml
inherited_evidence_applicability:
  required: 2
  pass: 2
  fail: 0
```

This pair proves both sides of the repair: non-release work is not falsely blocked by a historical manifest oracle, while an actual release candidate does not gain a weaker path.

---

# 6. Revised proof mapping for the repaired areas

| Repaired Claim | Invariant | Oracle / reference | Probe | Threshold | Evidence / Gate use |
|---|---|---|---|---|---|
| repository-backed execution preflight | exact repository/package/task binding precedes mutation; executor brand is provenance unless explicitly claimed | `O-EC-PREFLIGHT` + revised `O-EC-PLATFORM` + P17 capability contract | revised `EC-PFC01` | one fresh applicable occurrence; wrong-repository fallback = 0 | `ECV-E05`, independently resolved by P34 |
| local evidence durability | local-only bytes never become review-ready merely because an executor produced them | ArtifactStore/ResultMaterialization contract + revised `O-EC-PLATFORM` | revised `EC-PFC02` | local-only evidence accepted = 0 | `ECV-E04/E05` |
| historical release identity | historical release is checked against its bound publication source, not arbitrary current candidate bytes | exact release publication source + inherited evidence applicability | `EC-AP01` | false historical-candidate coupling = 0 | inherited/non-regression evidence only unless Gate Claim requires more |
| active release coherence | a real release candidate must match its own exact release manifest/artifact contract | candidate exact source/materialization + release manifest oracle | `EC-AP02` | release mismatch accepted = 0 | release Gate only when applicable |

---

# 7. Revised ECV0 v0.2 acceptance profile

The profile remains bounded and claim-proportional.

```yaml
profile: ECV0
revision: v0.2

deterministic_scenarios:
  required: 17
  pass: 17
  fail: 0

mutant_qualification:
  required: 17
  detected: 17
  undetected: 0
  false_acceptance: 0

inherited_evidence_applicability:
  required: 2
  pass: 2
  fail: 0

fresh_platform_corroboration:
  required: 4
  pass: 4
  fail: 0

zero_tolerance_events:
  authoritative_fact_override: 0
  floating_dependency_executed: 0
  unsatisfiable_contract_admitted_to_p32: 0
  post_hoc_requirement_misrouted_to_p32: 0
  same_result_false_claim_after_result_mutation: 0
  local_only_evidence_accepted: 0
  wrong_revision_ci_accepted: 0
  incomplete_provider_false_clean: 0
  mutable_latest_ref_accepted: 0
  signed_url_used_as_durable_identity: 0
  wrong_repository_fallback: 0
  inaccessible_required_evidence_accepted: 0
  proof_summary_overrode_exact_source: 0
  incomplete_obligation_set_false_complete: 0
  non_p34_gate_pass_emission: 0
  executor_brand_substituted_for_exact_preflight: 0
  historical_release_recomputed_from_unrelated_candidate_as_required_truth: 0
  active_release_mismatch_accepted: 0
```

The additional applicability probes do not create a new verification service, daemon, generic mutation framework, or monolithic evidence bundle.

---

# 8. Revised inherited-evidence applicability rule

Replace / refine P20 v0.1 section `Inherited evidence and applicability` with the following:

1. inherited evidence is accepted only for the exact Claim and source/materialization it actually proves;
2. candidate implementation changes invalidate inherited evidence only for Claims whose behavior/applicability changed, not unrelated historical occurrences;
3. historical release evidence is source-bound to its publication occurrence and is not re-targeted to the current candidate by recency, branch position, or shared file names;
4. candidate release-coherence evidence is required only when exact package/Authority scope makes the release Claim applicable;
5. exact candidate regressions override stale inherited PASS when they address the same applicable Claim;
6. timestamps, `latest`, branch names, or workflow names never establish inheritance or release applicability;
7. a non-release candidate changing canonical/generated Skill bytes must still prove Skill/generated-distribution parity and all other applicable regressions, but it is not required to make those bytes equal a historical published release tree;
8. P20 does not authorize mutation of historical release manifests to make a development candidate green;
9. when an inherited test encodes a broader applicability predicate than the accepted Claim, the test is a `TEST_DEFECT` and must be repaired/repackaged rather than treated as implementation failure.

---

# 9. Existing VP-I03 evidence under the repaired design

The exact result `2fec701cc38bb0d9bcb558d8802d0c7f012f408a` and its evidence remain immutable implementation history.

They may be reused as predecessor evidence only after a fresh P21 accepts v0.2 and downstream P30/P31 explicitly reconcile applicability and scope. This P20 repair does not declare the old result Gate-ready.

In particular:

```yaml
result_2fec701c:
  deterministic_core_evidence: PRESERVED_INPUT
  ecv0_17_scenarios: PRESERVED_INPUT
  ecv0_17_mutants: PRESERVED_INPUT
  old_EC_PFC01: NOT_SATISFIED_UNDER_V0_1
  revised_EC_PFC01: NOT_RETROACTIVELY_GRANTED
  EC_PFC03: NOT_RETROACTIVELY_GRANTED
  EC_PFC04: STILL_PENDING_FUTURE_CONTROL_REVIEW
  prior_failed_workflow_run: HISTORICAL_FAILURE_PRESERVED
  p34_pass: false
```

A later implementation/requalification occurrence must bind its evidence to the exact result that is actually reviewed after package/test/workflow reconciliation.

---

# 10. P34 interpretation after acceptance

If Governance accepts this repair, P34 may issue PASS for ECV0 v0.2 only when it independently establishes all applicable evidence for the exact reviewed candidate, including:

- `17/17` deterministic scenarios;
- `17/17` mandatory mutants detected with false acceptance `0`;
- `2/2` inherited-evidence applicability probes;
- `4/4` fresh platform corroborations using revised `EC-PFC01/02` semantics;
- exact result materialization and reviewer-resolvable EvidenceInputRefs/provider objects;
- exact provider run applicability/completion;
- independent obligation completeness;
- no unresolved review-contract delta;
- no zero-tolerance event.

P34 must not:

- infer `EC-PFC01` from an executor/assistant claim;
- treat branch naming as executor provenance;
- ignore a real provider failure merely because the underlying deterministic tests are green;
- require a non-release candidate to regenerate a historical release manifest from current bytes;
- waive active release coherence when release publication is actually in scope;
- convert ProofEvaluation or CI into its own Gate verdict.

---

# 11. Downstream planning / packaging implications

After fresh P21 acceptance, P30/P31 must perform a **targeted reconciliation**, not a full Verification Productization re-plan.

At minimum downstream work must:

1. replace the Codex-specific `EC-PFC01/02` wording with the accepted execution-surface-neutral contract;
2. preserve actual executor identity as provenance, without making brand identity a generic preflight pass condition;
3. define the two `EC-AP01/02` applicability probes in executable form;
4. repair/reclassify inherited release-coherence testing so historical release identity is source-bound and candidate release coherence is gated by exact applicability;
5. keep historical `v0.2.0-beta.1` manifest/tag/release immutable unless a separately authorized release task explicitly changes publication state;
6. reissue VP-I03 package scope only for the minimum new/changed test/workflow/contract paths required by the accepted repair;
7. preserve valid implementation work from PR #77 rather than reimplementing VP-I03 from zero;
8. require a fresh exact requalification occurrence after the repaired package is materialized;
9. keep `EC-PFC04` exclusively P34/CONTROL_REVIEW-owned.

P20 does not choose the exact repair file list; that remains P30/P31 implementation-control responsibility after Governance acceptance.

---

# 12. Quality / evidence gate for this P20 repair

This P20 repair is ready for Governance review only if the following are explicit without downstream invention:

1. why P17 permits executor-agnostic `CODE_EXECUTION` corroboration;
2. what exact fields and capabilities revised `EC-PFC01` must prove;
3. why executor provenance remains recorded but is not normally a pass condition;
4. why local-only durability semantics remain unchanged;
5. how historical release identity is bound to its publication source;
6. when candidate release-coherence becomes applicable;
7. how the repaired oracle still fails closed for a real release mismatch;
8. what two new applicability probes must prove;
9. what old VP-I03 evidence may be preserved and what cannot be retroactively accepted;
10. why P34 remains independent and cannot be started until downstream reconciliation/requalification closes the repaired contract.

---

# 13. P20 disposition

```yaml
P20_targeted_verification_contract_repair:
  repository: Mostorm-Labs/aegis
  scope: aegis/verification-productization/verification
  profile: ECV0_v0.2

  prior_p20_ref: 674e01737621621b8131e35f83313fb0154a9f6d
  prior_p21_review: 5121075377

  trigger_result: 2fec701cc38bb0d9bcb558d8802d0c7f012f408a
  trigger_p32_review: 5121781308
  routing_review: 5121799448

  repaired_findings:
    P20_B2_executor_specific_platform_corroboration:
      class: SPEC_DEFECT
      repair: executor_agnostic_exact_repository_package_preflight
    P20_B1_historical_release_oracle_applicability:
      class: TEST_DEFECT
      repair: source_bound_historical_release_plus_explicit_candidate_release_applicability

  retained:
    deterministic_scenarios: 17
    mandatory_mutants: 17
    mutant_false_acceptance_threshold: 0
    fresh_platform_corroborations: 4
    p34_sole_gate_owner: true

  added:
    inherited_evidence_applicability_probes: 2

  p17_repair_required: false
  p18_required_now: false
  implementation_authorized: false
  p34_gate_pass_issued: false
  authority_published_current: false

  status: READY_FOR_P21_AUTHORITY_REVIEW
  next_owner: aegis-governance
  next_stage: P21_AUTHORITY_REVIEW
```

Stop after exact P20 v0.2 materialization. Do not automatically execute P21, P30/P31 repair, P32 resume/requalification, P34, merge, Authority publication, or release.
