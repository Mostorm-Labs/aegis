# Aegis Control Plane Productization v0.2 — P23 Authority Supersession

Status: **Draft / Proposed Governance Supersession — P23**

Scope: `aegis/control-plane-productization`

This document materializes the bounded P23 supersession authorized by the accepted Product boundary narrowing and the subsequent five-axis drift review. It does not redesign the Control Plane and it does not rewrite any historical Authority, Gate, package, workflow result, or evidence artifact.

---

# 1. Exact governance basis

## 1.1 Accepted Product boundary

Replacement Product candidate:

- exact head: `e6f79e92d60b1fea126db4efec321fd5ddc1ada7`
- amendment: `docs/control-plane-productization-v0.2-p02-p03-product-boundary-supersession.md`
- P21 review: `5097117641`
- verdict: `PASS / ACCEPTED_FOR_DOWNSTREAM`
- change class: `PRODUCT_CLAIM_APPLICABILITY_NARROWING`

The accepted Product boundary states that v0.2 is complete when the Control Plane contracts are semantically correct and usable through the Plugin / nine-Skill product form. A standalone daemon, hosted multi-tenant Control Service, 24x7 service residency, R0-scale sustained service throughput, S0-scale service stress, service-economics attainment, and completed-month service availability are not v0.2 Product claims unless separately governed.

## 1.2 Five-axis drift review

P22 review:

- review: `5097146033`
- reviewed head: `e6f79e92d60b1fea126db4efec321fd5ddc1ada7`
- verdict: `PASS_WITH_DOWNSTREAM_DRIFT / READY_FOR_P23_SUPERSESSION`

P22 found no Product or Semantic blocker and isolated four downstream findings:

```text
P22-A1  P17 DEPLOYMENT_PROFILE_DRIFT
P22-I1  old CP-I09 STALE_PACKAGE_APPLICABILITY
P22-V1  P18 ENGINEERING_CLAIM_APPLICABILITY_DRIFT
P22-V2  P20 VERIFICATION_APPLICABILITY_DRIFT
```

This P23 changes only those applicability contracts.

---

# 2. Supersession method

P23 uses additive supersession rather than in-place historical mutation.

The following accepted artifacts remain immutable historical records:

- P17 Platform Contract materialized at `e7acbe15ab34879e743ec88f7dfb38e5ce3a3931` and accepted as part of PR #27 architecture head `e657f0e74771184b98f8c8e6f8a8581e4858c82d` / review `5062769390`;
- P18 Engineering / Optimization at architecture head `e657f0e74771184b98f8c8e6f8a8581e4858c82d` / review `5062769390`;
- P20 Verification Design plus its P21 repair at `db83168e4086e47a7f431acf289006e4f25b8ffd` / review `5062933855`;
- CP-I09 package `CP-I09-P31-01` at `9f4b76d51ce2e8a2c0ac23d6fba323bc078a9385` and all of its execution/reverification evidence.

Where this P23 is more specific about **deployment-profile applicability, release applicability, and package actionability**, this P23 controls for the narrowed v0.2 Product claim. Unaffected semantic, architecture, engineering, and verification contracts remain inherited.

No prior FAIL becomes PASS. No prior PASS is broadened beyond what it proved.

---

# 3. Deployment profile vocabulary

P23 introduces no new semantic Product object. It defines governance applicability labels for existing platform/engineering/verification clauses.

## 3.1 `PLUGIN_PROFILE`

The v0.2 required Product delivery envelope:

```text
ChatGPT host
  -> Aegis Plugin
  -> nine Aegis Skills
  -> governed durable/execution surfaces
     such as GitHub / Notion / Codex / CI
```

The profile may use durable external state, provider APIs, hosted tools, or network services where naturally required by those providers. It does not require Aegis itself to expose a dedicated always-on Control Service or public Aegis API.

## 3.2 `SERVICE_PROFILE`

An optional deployment realization of the same Control Plane contracts that may include:

- dedicated Aegis Control Service;
- Aegis Control App transport bridge;
- versioned public/internal HTTPS APIs;
- separate `aegis-control-api` / `aegis-control-worker` processes;
- production service throughput/latency/backlog targets;
- long-window service economics and availability claims.

`SERVICE_PROFILE` is not required for v0.2 release validity. If a later Product Authority explicitly claims it, its conditional P17/P18/P20 obligations become mandatory for that claimed release/profile.

---

# 4. P17 targeted supersession — Platform applicability

Superseded applicability basis:

- document: `docs/control-plane-productization-platform-contract-v0.2.md`
- individual materialization head: `e7acbe15ab34879e743ec88f7dfb38e5ce3a3931`
- accepted architecture head: `e657f0e74771184b98f8c8e6f8a8581e4858c82d`
- review: `5062769390`

Change class:

`DEPLOYMENT_PROFILE_APPLICABILITY_SUPERSESSION`

## 4.1 Retained P17 contracts

The following remain required for v0.2 independent of deployment form:

1. durable control truth required for safe continuation is not dependent on one conversation, browser tab, Codex thread, worktree, or process memory;
2. canonical mutation has one logical write boundary and cannot be bypassed by projection, scheduling, dispatch, recovery, adapters, or clients;
3. canonical records/exact refs preserve accepted immutable/revisioned semantics;
4. credentials and transport capabilities remain outside canonical semantic truth;
5. callbacks/webhooks are wakeups/correlation hints, while durable query/refetch/reconciliation establishes provider current truth;
6. execution/provider observations do not directly become semantic truth;
7. capability/adaptor boundaries fail closed on unsupported, stale, ambiguous, or unverifiable external truth;
8. the Aegis Plugin remains a distribution/reasoning envelope and does not become a tenth lifecycle semantic owner;
9. P34 remains the sole official Gate owner;
10. Current rollout Authority still governs cross-Primary automatic continuation.

## 4.2 Reclassified P17 contracts

The following P17 choices remain valid **only when `SERVICE_PROFILE` is claimed or selected as the realization**:

- one dedicated logical `Aegis Control Service` as the required Aegis-hosted durable service boundary;
- `Aegis Control App -> HTTPS/JSON -> Aegis Control Service` as the required v0.2 topology;
- Process A `aegis-control-api` and Process B `aegis-control-worker` as the minimum production process boundary;
- a public Aegis `/v1` HTTPS API as a required v0.2 product surface;
- `/internal/v1` worker HTTP contracts as required when worker/service are not actually separated;
- unconditional HTTPS/JSON requirements where no Aegis-owned cross-process/network boundary exists.

For `PLUGIN_PROFILE`, these are optional realizations, not release criteria.

## 4.3 Cross-boundary protocol rule after supersession

When an Aegis-owned cross-process/network boundary actually exists, P17's versioned protocol, exact-ref, capability-isolation, and fail-closed requirements remain applicable to that boundary.

When modules are in-process, host-mediated, or represented through governed provider/plugin tool contracts, P17 does not require an artificial Aegis HTTP service solely to satisfy topology.

Disposition:

```yaml
P17:
  historical_artifact: RETAINED
  semantic_platform_invariants: RETAINED_REQUIRED
  service_topology: SERVICE_PROFILE_CONDITIONAL
  v0_2_plugin_profile_requires_control_service: false
  supersession: COMPLETE
```

---

# 5. P18 targeted supersession — Engineering applicability

Superseded applicability basis:

- document: `docs/control-plane-productization-engineering-v0.2.md`
- accepted head: `e657f0e74771184b98f8c8e6f8a8581e4858c82d`
- review: `5062769390`

Change class:

`ENGINEERING_PROFILE_APPLICABILITY_SUPERSESSION`

## 5.1 Retained P18 engineering authority

The following remain required engineering policy for v0.2:

- semantic correctness / fail-closed trust outranks performance;
- acknowledged canonical history must not be lost to satisfy an optimization target;
- deterministic recovery and idempotency remain mandatory;
- exact refs, currentness, CAS, commit-before-dispatch, immutable history, stage ownership, independent proof/review, and Gate ownership are not optimization knobs;
- no remote provider call may be used to weaken canonical transaction boundaries;
- backpressure, retry timers, pause/lease/cache state remain operational and cannot fabricate semantic truth;
- D0 deterministic/local conformance remains a valid required engineering profile for semantic and fault-contract qualification;
- measurement must bind exact workload, environment, raw evidence, metric definition, and threshold whenever an engineering claim is made;
- observability must not become semantic truth;
- provider latency and substantive execution latency must not be misrepresented as Control Plane-owned performance.

## 5.2 Conditional P18 service characterization

For `PLUGIN_PROFILE`, the following are **not release-blocking attainment requirements** merely because old P18 defined them:

- R0 as the launch benchmark for one production-shaped Aegis Control Service;
- 10,000 active WorkScopes / 100 interactive clients service envelope;
- R0 Control API request, mutation, projection, provider-event, and outbox throughput/latency targets;
- S0 `4 x R0 for 15 minutes` wall-clock service stress/backlog-recovery attainment;
- service backlog/worker/process-capacity targets whose purpose is proving the dedicated service profile;
- seven-day service economics attainment;
- completed-month Aegis service availability attainment.

These values remain preserved as engineering characterization targets for `SERVICE_PROFILE` and may be used for diagnostics, benchmarking, capacity planning, or a later explicitly governed service release.

## 5.3 Semantic invariants under any load

Any load/repetition profile that is executed — D0, bounded repeated-occurrence, R0, S0, or another later profile — still has zero permission to violate semantic invariants. A service benchmark being non-blocking for `PLUGIN_PROFILE` does not make semantic corruption acceptable.

Disposition:

```yaml
P18:
  historical_artifact: RETAINED
  correctness_and_safe_optimization: RETAINED_REQUIRED
  D0_semantic_engineering: RETAINED_REQUIRED
  R0_service_attainment: SERVICE_PROFILE_CONDITIONAL
  S0_service_attainment: SERVICE_PROFILE_CONDITIONAL
  W7D_service_economics: SERVICE_PROFILE_CONDITIONAL
  monthly_service_availability: SERVICE_PROFILE_CONDITIONAL
  supersession: COMPLETE
```

---

# 6. P20 targeted supersession — Verification applicability

Superseded applicability basis:

- documents:
  - `docs/control-plane-productization-verification-v0.2.md`
  - `docs/control-plane-productization-verification-v0.2-p21-repair.md`
- accepted exact head: `db83168e4086e47a7f431acf289006e4f25b8ffd`
- review: `5062933855`

Change class:

`VERIFICATION_PROFILE_APPLICABILITY_SUPERSESSION`

P23 does not replace `aegis-verification` as P20 owner and does not invent a new full VerificationSpec. It governs which existing proof obligations remain release-applicable after the Product claim narrowing and routes the exact targeted P20 repair required next.

## 6.1 Release-blocking verification retained

The following remain mandatory for v0.2 `PLUGIN_PROFILE`:

1. `CoverageBasis = REVIEW_DECLARED` and independent coverage-completeness review;
2. production SUT is not its own only correctness oracle;
3. independent `O-CRM`, `O-COMPLETE`, and the accepted oracle-independence boundaries;
4. deterministic semantic/fault conformance represented by the accepted G01-G44 corpus, except that a scenario's service-specific performance attainment must not be inferred where its retained purpose is semantic/policy correctness;
5. mandatory verifier qualification M01-M20 at `100% detection / 0 false acceptance`;
6. canonical safety, single-writer/CAS/idempotency/commit-before-dispatch correctness;
7. historical exact-ref, Required-child, external truth/currentness, snapshot-token, provider query/correlation, and no-silent-truncation correctness;
8. sessionless resume and all four P33 execution-position outcomes;
9. HumanDecision exact-ref integrity;
10. degraded recovery, timeout-not-semantic-retry, replay/audit, and duplicate-delivery safety;
11. exact evidence identity/materialization and reviewer-resolvable provenance;
12. P34 Gate independence: CI, provider success, ProofEvaluation, benchmark success, or dashboard state is never Gate PASS;
13. Current cross-Primary rollout denial until separately governed;
14. zero-tolerance semantic invariant violations remain release-blocking under every executed profile.

CP-I01 through CP-I08 remain accepted evidence for these retained contracts unless fresh evidence identifies a concrete contradiction.

## 6.2 Reclassified P20 proof obligations

For v0.2 `PLUGIN_PROFILE`, these obligations are not mandatory release blockers solely on the old service-profile basis:

- `CPV-C11 R0 Engineering Budget` insofar as it requires production Aegis service throughput/latency attainment;
- S0 real-wall-clock `4 x R0 for 15 minutes` as a mandatory service-scale stress/recovery release profile;
- `CPV-R39` / the cost portion of `CPV-C19 Long-window Cost / Availability` requiring seven-day service economics attainment;
- `CPV-R40` / the availability portion of `CPV-C19` requiring completed-month Aegis service availability attainment before v0.2 Plugin release;
- any raw service RPS/backlog/process-capacity threshold whose sole justification is the superseded mandatory Control Service launch profile.

These obligations remain mandatory whenever `SERVICE_PROFILE` or the matching economics/availability claim is explicitly adopted.

## 6.3 Targeted P20 repair still required

Before any new implementation package is created to replace old CP-I09, `aegis-verification` must materialize a targeted P20 replacement/amendment that:

- binds the accepted P02/P03 Product claim and this P23 applicability supersession;
- preserves the retained semantic/oracle/mutant/fault proof universe;
- defines an explicit release-blocking engineering/repetition profile proportional to `PLUGIN_PROFILE`;
- clearly distinguishes correctness/repetition evidence from throughput/availability claims;
- preserves historical R0/S0/W7D evidence without reinterpretation;
- states exactly which conditional service-profile claims would reactivate R0/S0/W7D/monthly requirements.

Until that targeted P20 repair is accepted, Governance must not create a replacement CP-I09 P31 package by guessing the new proof contract.

Disposition:

```yaml
P20:
  historical_artifact: RETAINED
  semantic_correctness_proof: RETAINED_RELEASE_BLOCKING
  G01_G44_semantic_fault_corpus: RETAINED
  M01_M20_verifier_qualification: RETAINED
  R0_service_attainment: SERVICE_PROFILE_CONDITIONAL
  S0_service_attainment: SERVICE_PROFILE_CONDITIONAL
  R39_W7D_service_economics: SERVICE_PROFILE_CONDITIONAL
  R40_monthly_service_availability: SERVICE_PROFILE_CONDITIONAL
  targeted_verification_repair_required: true
  supersession: APPLICABILITY_COMPLETE
```

---

# 7. CP-I01 through CP-I08 disposition

Accepted implementation predecessor:

- exact result: `ac2bcf19acf46a749761ed455ecf0a995069700d`
- CP-I08 P34 review: `5079977191`
- verdict: `PASS / ACCEPTED_FOR_DOWNSTREAM`

P23 disposition:

```yaml
CP_I01_I08:
  applicability: CURRENT_FOR_RETAINED_V0_2_SEMANTIC_CLAIM
  rerun_by_default: false
  accepted_evidence_rewritten: false
```

Reason: P22 found no Product/Semantic drift and no concrete implementation contradiction. Their accepted semantic/control evidence remains relevant to the narrowed Product claim.

A future fresh contradiction must fail closed at the earliest affected layer; this disposition is not permission to ignore such evidence.

---

# 8. Old CP-I09 disposition

Historical package:

```text
package_id  = CP-I09-P31-01
package_ref = 9f4b76d51ce2e8a2c0ac23d6fba323bc078a9385
```

Historical latest result discussed by the Product/P22 review:

```text
result_revision = 85956ea32f7df9f393526473ad5da3382d49ad11
workflow_run    = 33657495026
R0              = FAIL
S0              = FAIL
W7D             = PASS
combine         = SKIPPED
```

P23 classification:

`STALE_PACKAGE_APPLICABILITY -> HISTORICAL_ONLY`

Normative consequences:

1. all old package, commit, workflow, artifact, log, P34/P35/P36, R0/S0/W7D, diagnostic, and repair evidence remains immutable historical evidence;
2. R0 remains FAIL;
3. S0 remains FAIL;
4. W7D remains PASS for exactly what it measured;
5. no aggregate PASS is manufactured;
6. the package is no longer the active release-blocking P36 package for narrowed v0.2 `PLUGIN_PROFILE`;
7. PR #44 P36 remains paused rather than resumed to tune the stale service-scale package;
8. no replacement CP-I09 P31 package may be created until the targeted P20 verification repair is materialized and accepted;
9. a later `SERVICE_PROFILE` claim may reuse historical evidence as input, but must independently determine freshness/applicability and may require new evidence.

Disposition:

```yaml
old_CP_I09:
  package_id: CP-I09-P31-01
  package_ref: 9f4b76d51ce2e8a2c0ac23d6fba323bc078a9385
  status: HISTORICAL_ONLY
  active_release_blocker_for_PLUGIN_PROFILE: false
  historical_R0: FAIL
  historical_S0: FAIL
  historical_W7D: PASS
  evidence_deleted_or_rewritten: false
  P36_resume_authorized: false
```

---

# 9. Downstream dependency/version expectations

After this P23, downstream work must resolve the Control Plane authority stack as follows:

```text
P02/P03 Product
  base c628bdc... + accepted Product boundary amendment e6f79e9...

P10-P13 Modeling
  f29c4da... / review 5062616510
  RETAIN

P14 System Architecture
  54999ce...
  RETAIN

P15 Module Design
  12f75bc...
  RETAIN

P16 Runtime Data Flow
  56f7df8...
  RETAIN

P17 Platform Contract
  historical e7acbe1... + this P23 applicability supersession
  SERVICE_PROFILE topology conditional

P18 Engineering / Optimization
  historical e657f0e... + this P23 applicability supersession
  service attainment conditional

P20 Verification
  historical db83168... + this P23 applicability supersession
  semantic proof retained; service proof conditional
  targeted P20 replacement/amendment still required before new CP-I09 packaging

CP-I01..CP-I08
  RETAIN accepted results

old CP-I09-P31-01
  HISTORICAL_ONLY
```

This is a dependency/applicability correction. It does not convert the unmerged PR stack into root `.aegis` Current Authority or repository integration truth.

---

# 10. Explicit non-actions

P23 does **not**:

- redesign P10-P13;
- reopen P14-P16;
- edit historical P17/P18/P20 documents in place;
- weaken semantic zero-tolerance requirements;
- waive any failed evidence;
- rerun CP-I01 through CP-I08;
- resume PR #44 P36;
- create a replacement CP-I09 package;
- claim `SERVICE_PROFILE`;
- claim monthly availability;
- authorize Current cross-Primary rollout;
- mutate root `.aegis` Project State;
- mark PR #47 ready/merge it;
- merge, release, publish, or integrate anything;
- issue a P34 Gate verdict.

Current cross-Primary rollout remains:

`DENIED`

---

# 11. P23 acceptance / completion checks

P23 is complete only if all of the following remain true on its exact materialized head:

1. accepted Product narrowing and P22 basis are exact and unchanged;
2. no Product/Semantic redesign is introduced;
3. P14-P16 remain retained;
4. P17 service topology is conditional rather than mandatory for `PLUGIN_PROFILE`;
5. P18 service-scale engineering attainment is conditional while correctness policy is retained;
6. P20 semantic proof remains release-blocking while service-scale proof is conditional;
7. old CP-I09 becomes historical-only without rewriting R0/S0/W7D results;
8. CP-I01 through CP-I08 remain retained and are not rerun by default;
9. no replacement CP-I09 package is created before targeted P20 repair;
10. rollout remains `DENIED`;
11. repository/root Current Authority is not falsely claimed before integration;
12. no merge/release/P34 is implied.

---

# 12. P23 disposition

```yaml
P23_authority_supersession:
  scope: aegis/control-plane-productization

  product_basis:
    head: e6f79e92d60b1fea126db4efec321fd5ddc1ada7
    p21_review: 5097117641
    verdict: PASS_ACCEPTED_FOR_DOWNSTREAM

  p22_basis:
    review: 5097146033
    verdict: PASS_WITH_DOWNSTREAM_DRIFT

  retained:
    P10_P13: true
    P14: true
    P15: true
    P16: true
    CP_I01_I08: true

  superseded_applicability:
    P17:
      from: MANDATORY_FIRST_SERVICE_DEPLOYMENT
      to: SERVICE_PROFILE_CONDITIONAL
    P18:
      from: R0_S0_SERVICE_ATTAINMENT_AS_V0_2_LAUNCH_REQUIREMENT
      to: SERVICE_PROFILE_CONDITIONAL
    P20:
      from: SERVICE_SCALE_PROOF_AS_UNCONDITIONAL_V0_2_RELEASE_REQUIREMENT
      to: SEMANTIC_PROOF_BLOCKING_SERVICE_PROFILE_PROOF_CONDITIONAL

  old_CP_I09:
    package_id: CP-I09-P31-01
    package_ref: 9f4b76d51ce2e8a2c0ac23d6fba323bc078a9385
    disposition: HISTORICAL_ONLY
    P36_resume_authorized: false

  historical_evidence_preserved: true
  historical_failures_rewritten: false
  root_project_state_mutated: false
  rollout: DENIED

  next_owner: aegis-verification
  next_stage: TARGETED_P20_VERIFICATION_REPAIR
  replacement_CP_I09_package_authorized_now: false

  status: MATERIALIZED_PENDING_EXACT_HEAD_P23_GOVERNANCE_CHECK
```
