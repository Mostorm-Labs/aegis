# Aegis Control Plane Productization v0.2 — P20 Plugin-Profile Verification Right-Sizing

Status: **Draft / Proposed Verification Authority — targeted P20 supersession for v0.2 PLUGIN_PROFILE**

Scope: `aegis/control-plane-productization/verification`

This document is a narrow normative amendment to the accepted Plugin-profile Verification Authority at:

- `d6b795ce4a40a422d26f74d749cc823dd66a26df`
- P21 review `5097554177` — `PASS / ACCEPTED_FOR_DOWNSTREAM`

It exists because downstream Gate execution exposed a verification-scope drift: the release proof for a Plugin + nine-Skill product evolved into a new standalone PP0 qualification framework whose implementation burden is disproportionate to the accepted v0.2 Product claim.

This amendment does **not** weaken the Control Plane semantic contract. It removes the requirement to build a new verification product in order to release the Plugin product.

---

# 1. Exact trusted basis

## 1.1 Product boundary

Accepted Product claim boundary:

- Product supersession head: `e6f79e92d60b1fea126db4efec321fd5ddc1ada7`
- Product P21 review: `5097117641` — `PASS / ACCEPTED_FOR_DOWNSTREAM`
- P23 applicability supersession: `b5677ad112a7a2067754b209ccde7fc97ef7469d`
- P23 review: `5097214759` — `PASS / AUTHORITY_SUPERSESSION_COMPLETE`

The required v0.2 delivery form remains:

```text
ChatGPT host
  -> Aegis Plugin
  -> exact nine Aegis Skills
  -> governed external surfaces such as GitHub / Notion / Codex / CI
```

The v0.2 release claim remains:

> The Aegis Control Plane contracts are semantically correct, durable, resumable, auditable, fail-closed, ownership-preserving, and usable through the Plugin / nine-Skill product form.

A standalone agent, daemon, dedicated Control Service, verification service, or always-on verification harness is not a required product component.

## 1.2 Verification basis being superseded

Accepted Plugin-profile P20 basis:

- `docs/control-plane-productization-verification-v0.2-plugin-profile-repair.md`
- `docs/control-plane-productization-verification-v0.2-plugin-profile-p21-b1-repair.md`
- exact accepted head: `d6b795ce4a40a422d26f74d749cc823dd66a26df`
- review: `5097554177`

That basis correctly removed service-scale R0/S0/W7D/monthly obligations from the mandatory `PLUGIN_PROFILE`, but it introduced a new release-blocking `PP0` profile with:

- exact 40 WorkScopes;
- five fixed cohorts;
- seven mandatory oracle surfaces;
- dedicated trace corpus and workload manifest requirements;
- a new qualification-harness negative set;
- a monolithic final-bundle materialization contract.

The downstream Gate loop then required implementing and qualifying that proof machinery itself before the Plugin could pass.

## 1.3 Gate evidence motivating this repair

Current qualified Plugin candidate:

`18559f32ede7ebd845064fe8de7967ca358b785f`

Accepted current evidence already demonstrates:

- repository Control Plane regressions PASS;
- G01-G44 PASS;
- M01-M20 = `20/20`, false acceptance `0`;
- exact-nine Plugin materialization PASS;
- fresh exact-candidate installed-platform PFC-01..PFC-08 observations PASS;
- router/specialist ownership boundaries preserved;
- Codex execution-prefix and handoff contract preserved;
- sessionless durable-ref resume preserved;
- P34 sole-Gate ownership preserved;
- cross-Primary rollout remains `DENIED`;
- `SERVICE_PROFILE` remains not authorized.

P34 rereview findings `CP-I09-P34-B2/B3` do not demonstrate a product semantic failure. They demonstrate that the dedicated PP0 proof system itself was synthetic/incomplete under the accepted PP0-specific contract.

This is the verification-scope drift corrected by this amendment.

---

# 2. Repair objective

For v0.2 `PLUGIN_PROFILE`, release-blocking evidence must prove the product claim directly and proportionately.

The controlling principle is:

> **Evidence strength must match Claim strength. A Plugin release must not require building a separate verification framework whose complexity materially exceeds the Plugin product being released.**

The verification chain remains:

```text
Requirement
  -> Invariant
  -> Oracle / Reference
  -> Existing Fixture / Corpus
  -> Test / Probe
  -> Metric / Verdict
  -> Reviewer-resolvable Evidence
  -> P34 Gate
```

The change is in proof packaging and profile size, not in semantic truth.

---

# 3. Explicit non-goals

This repair does **not**:

- reopen P02/P03 Product Authority;
- reopen P10-P13 Modeling;
- reopen P14-P18 semantic architecture;
- weaken exact refs, ownership, CAS/idempotency, commit-before-dispatch, currentness, immutable history, repair lineage, P33 resume, HumanDecision, provider reconciliation, or Gate ownership;
- remove G01-G44;
- remove M01-M20;
- authorize zero-user-turn cross-Primary substantive chaining;
- authorize `SERVICE_PROFILE`;
- reinterpret old R0/S0/W7D failures as PASS;
- resume PR #44;
- require a new dedicated PP0 harness;
- require a standalone verification agent/service;
- merge, release, or issue P34 PASS.

---

# 4. Normative verification-profile repair

## 4.1 `PP0` fixed 40-WorkScope profile is no longer a v0.2 release blocker

For v0.2 `PLUGIN_PROFILE`, the exact fixed profile previously named:

```text
PP0 = Plugin Profile Release Qualification
```

with exact 40 WorkScopes, five fixed 8-scope cohorts, dedicated concurrency/CAS counts, dedicated PP0 trace corpus, and dedicated PP0 harness qualification is reclassified as:

```text
OPTIONAL_CHARACTERIZATION / FUTURE_VERIFICATION_FRAMEWORK
```

It is **not required** for v0.2 Plugin release.

No P34 decision may require implementation of a new PP0 harness solely because the superseded P20 text specified that machinery.

Existing PP0 artifacts may remain as historical/supporting evidence but are not release-authoritative by themselves.

## 4.2 `CPV-R41 / CPV-C20` intent is retained but right-sized

`CPV-R41 Plugin-Profile Repeated Integration Stability` and `CPV-C20 Plugin-Profile Repeated Integration Stability` remain valid in their semantic intent:

> bounded repeated/replayed/interleaved execution must not contradict accepted Control Plane semantics.

Their v0.2 proof vehicle is superseded as follows:

```text
Release applicability: REQUIRED
Dedicated 40-WorkScope PP0 profile: NOT_REQUIRED
Dedicated new oracle stack implementation: NOT_REQUIRED
Dedicated PP0 trace framework: NOT_REQUIRED
Proof vehicle: existing accepted semantic/fault/regression corpus + current-candidate regression + targeted existing integration/replay/resume/provider/repair tests
```

P34 must verify that current regressions do not contradict the retained semantic Claims. It must not require a second Control Plane model or a new verification runtime.

## 4.3 `CPV-R42 / CPV-C21` remains release-blocking

`CPV-R42 Plugin / Nine-Skill Product-Form Fidelity` and `CPV-C21 Plugin Product-Form Corroboration` remain release-blocking because they directly prove the actual v0.2 delivery form.

Required evidence remains fresh and exact-candidate-bound:

- one Aegis Plugin;
- exactly nine Skills;
- central router ownership on routing-only work;
- specialist ownership on specialist work;
- correct execution-surface handoff metadata;
- exact Codex execution prefix when applicable;
- sessionless durable-ref continuation;
- P34 sole-Gate ownership;
- rollout remains `DENIED`.

---

# 5. Required v0.2 `PLUGIN_PROFILE` proof set

The release-blocking proof set is now the minimum direct evidence that credibly proves the Plugin claim.

## 5.1 Semantic/control regression

Mandatory:

```text
G01-G44 = PASS
semantic oracle mismatches = 0
zero-tolerance semantic/control invariant events = 0
```

The accepted G corpus and the repository's current Control Plane regression suites are the primary semantic proof vehicles.

P34 may inspect the existing independent reference/oracle surfaces used by those tests. This repair does not require creating a new all-in-one oracle harness.

## 5.2 Verifier qualification

Mandatory:

```text
M01-M20 detected = 20/20
M01-M20 false acceptance = 0
```

No additional 32-mutant PP0-harness qualification layer is required for v0.2 release.

## 5.3 Current candidate regression

The exact candidate must have current hosted evidence showing relevant repository regressions PASS, including as applicable:

- Control Plane regression;
- Project State regression;
- Skillset / Plugin materialization regression;
- inherited-evidence applicability checks.

A current regression contradiction invalidates the affected inherited evidence.

## 5.4 Fresh installed Plugin / nine-Skill corroboration

Fresh exact-candidate platform corroboration remains mandatory for `CPV-C21`.

The accepted PFC-01..PFC-08 model is retained.

## 5.5 Exact evidence provenance

All release-critical evidence must be:

- reviewer-resolvable;
- exact-candidate-bound where candidate identity matters;
- explicit about inherited vs current execution evidence;
- explicit that rollout remains `DENIED`;
- explicit that `SERVICE_PROFILE` is not claimed;
- explicit that P34 is the sole official Gate verdict owner.

---

# 6. Evidence packaging right-sizing

A single monolithic digest-bound bundle containing every historical, repository, and installed-platform observation is **not required** for v0.2 `PLUGIN_PROFILE`.

P34 may accept a composite evidence graph when every required ref is independently reviewer-resolvable and exact applicability is explicit.

Minimum final evidence record may be a reviewer-accessible manifest or durable review record that binds:

```yaml
verification_authority_ref: <accepted right-sized P20 ref>
qualified_candidate_revision: <exact candidate>
repository_workflow_refs: [...]
repository_artifact_refs: [...]
inherited_evidence_refs: [...]
platform_corroboration_refs: [...]
g01_g44: PASS
m01_m20_detected: 20/20
m01_m20_false_acceptance: 0
exact_nine: PASS
pfc01_pfc08: PASS
unresolved_required_evidence_refs: 0
current_cross_primary_rollout: DENIED
service_profile: NOT_CLAIMED
p34_gate_pass: false
```

Individual source artifacts may retain their own immutable digests. Platform observations may remain durable PR review/comment refs; they do not need to be copied into a newly generated synthetic bundle merely to become admissible.

Evidence provenance remains strict; evidence co-location is not a product requirement.

---

# 7. Evidence inheritance

Accepted CP-I01..CP-I08 evidence remains reusable when:

1. its exact ref is independently resolvable;
2. the Claim remains release-applicable;
3. no accepted semantic/architecture change invalidates its basis;
4. the current Plugin candidate still contains the relevant reviewed behavior or an accepted equivalent;
5. current regression does not contradict it.

`RETAIN / DO NOT RERUN BY DEFAULT` remains controlling.

No new verification framework is required to re-prove already accepted semantics absent a concrete contradictory result.

---

# 8. Service-profile proof remains conditional

The following remain non-blocking for v0.2 `PLUGIN_PROFILE` unless a future Product Authority explicitly claims them:

```text
R25 / C11 R0 service throughput/latency
R26 / C12 real-wall-clock S0 service stress
R39 / C19 W7D service economics
R40 / C19 completed-month service availability
24x7 residency
multi-tenant / multi-region service capacity
```

Old CP-I09 service evidence remains `HISTORICAL_ONLY`:

```text
R0 = FAIL
S0 = FAIL
W7D = PASS
```

No historical result is rewritten.

---

# 9. Downstream disposition of current CP-I09 / Gate work

If this P20 amendment is accepted by Governance:

## 9.1 Keep/reuse

The following current evidence remains eligible for exact-ref applicability review:

- qualified candidate `18559f32ede7ebd845064fe8de7967ca358b785f`;
- hosted repository qualification evidence already produced for that candidate;
- G01-G44 PASS;
- M01-M20 `20/20`, false acceptance `0`;
- exact-nine Plugin materialization;
- fresh exact-candidate PFC-01..PFC-08 observations;
- durable sessionless/resume and handoff observations;
- P34 ownership and rollout-denial observations.

## 9.2 Stop/supersede

The following obligations from `CP-I09-P31-02` become stale to the extent that they exist solely to satisfy the superseded fixed PP0 profile:

- building a real 40-WorkScope PP0 harness;
- implementing a new seven-oracle aggregation runtime;
- qualifying a separate 32-mutant PP0 harness;
- generating a mandatory full semantic PP0 trace corpus;
- requiring `pp0-workload-manifest.json` / `pp0-trace-corpus.json` / `pp0-conformance.json` as release-blocking artifacts;
- requiring all evidence to be recopied into one final monolithic digest bundle.

`CP-I09-P34-B2` and `CP-I09-P34-B3` therefore become **applicability-stale findings**, not product defects, once this Verification Authority is accepted and downstream package applicability is superseded.

Until Governance completes that supersession, no P34 PASS is implied.

## 9.3 P36 harness repair must stop

The P36 CODE_REVERIFY handoff that attempts to implement the PP0 harness is no longer the intended repair direction under this proposed Verification Authority.

Do not continue that harness implementation while this Authority repair is under review.

---

# 10. P34 review contract after acceptance

For v0.2 `PLUGIN_PROFILE`, P34 must independently verify at least:

1. this right-sized P20 amendment is accepted Current Verification Authority;
2. required Claim coverage remains complete under `REVIEW_DECLARED`;
3. G01-G44 current status is PASS;
4. semantic/control zero-tolerance violations are zero in the accepted/current corpus;
5. M01-M20 = `20/20`, false acceptance `0`;
6. inherited CP-I01..CP-I08 evidence is exact, resolvable, applicable, and not contradicted by current regression;
7. exact candidate repository regressions are PASS;
8. exact-nine Plugin materialization is valid;
9. fresh exact-candidate PFC-01..PFC-08 product-form corroboration is valid;
10. durable continuation does not depend solely on one conversation transcript;
11. P34 remains sole official Gate owner;
12. current cross-Primary rollout is `DENIED`;
13. no `SERVICE_PROFILE`, R0/S0/W7D/monthly service claim is inferred;
14. old CP-I09 historical evidence remains historical and unmodified;
15. no unresolved release-critical evidence ref remains.

P34 MUST NOT require the superseded fixed 40-WorkScope PP0 harness, its dedicated trace corpus, or its 32-mutant self-qualification as a v0.2 release criterion.

---

# 11. Acceptance criteria for this P20 repair

This amendment is acceptable only if fresh Governance review confirms:

1. Product/Modeling/Architecture semantics are not reopened;
2. the v0.2 product remains Plugin + exact nine Skills;
3. semantic/control proof remains strong through existing accepted corpus, current regression, verifier qualification, and installed-product corroboration;
4. the fixed PP0 harness requirement is proof-system overreach rather than a Product requirement;
5. `CPV-R41/C20` semantic stability intent remains release-applicable without requiring a new verification runtime;
6. `CPV-R42/C21` installed-product fidelity remains release-blocking;
7. exact evidence provenance remains mandatory even though monolithic co-location is not;
8. old service-scale evidence remains historical-only;
9. rollout remains `DENIED`;
10. no P34 PASS, merge, release, or rollout expansion is implied.

---

# 12. P20 disposition

```yaml
P20_plugin_profile_rightsize:
  scope: aegis/control-plane-productization/verification

  superseded_verification_ref: d6b795ce4a40a422d26f74d749cc823dd66a26df
  superseded_verification_review: 5097554177

  product_boundary_ref: e6f79e92d60b1fea126db4efec321fd5ddc1ada7
  product_review: 5097117641
  p23_ref: b5677ad112a7a2067754b209ccde7fc97ef7469d
  p23_review: 5097214759

  required_release_form: PLUGIN_PLUS_EXACT_NINE_SKILLS
  coverage_basis: REVIEW_DECLARED

  retained_release_proof:
    G01_G44: REQUIRED
    M01_M20: REQUIRED
    current_candidate_regression: REQUIRED
    exact_evidence_provenance: REQUIRED
    fresh_installed_product_corroboration: REQUIRED
    p34_independence: REQUIRED

  CPV_R41_C20:
    semantic_intent: RETAINED
    fixed_PP0_40_workscope_profile: NOT_REQUIRED
    dedicated_PP0_harness: NOT_REQUIRED
    dedicated_PP0_trace_framework: NOT_REQUIRED

  CPV_R42_C21:
    installed_product_fidelity: REQUIRED

  evidence_packaging:
    monolithic_final_bundle: NOT_REQUIRED
    composite_reviewer_resolvable_evidence_graph: ALLOWED

  conditional_service_proof:
    R25_C11: SERVICE_PROFILE_CONDITIONAL
    R26_C12: SERVICE_PROFILE_CONDITIONAL
    R39_C19_cost: SERVICE_PROFILE_CONDITIONAL
    R40_C19_availability: SERVICE_PROFILE_CONDITIONAL

  current_candidate_for_downstream_reassessment: 18559f32ede7ebd845064fe8de7967ca358b785f
  P36_PP0_harness_repair_direction: STOP
  old_CP_I09: HISTORICAL_ONLY
  current_cross_primary_rollout: DENIED

  status: READY_FOR_P21_AUTHORITY_REVIEW
  next_owner: aegis-governance
  next_stage: P21_AUTHORITY_REVIEW
```

Stop after P20 materialization.

Do not continue the PP0 harness repair, do not execute P21 automatically, do not issue P34 PASS, and do not merge/release/expand rollout from this document alone.
