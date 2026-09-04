# Aegis Control Plane Productization v0.2 — P20 Plugin-Profile Verification Repair

Status: **Draft / Proposed Authority — targeted P20 Verification repair**

Scope: `aegis/control-plane-productization/verification`

This document is a **normative targeted amendment** to the accepted Control Plane P20 Verification package after the Product claim narrowing and P23 Authority supersession.

It does not redesign the Control Plane, does not weaken semantic proof, does not reinterpret historical benchmark evidence, and does not begin implementation or task packaging.

---

# 1. Exact trusted basis

## 1.1 Product / Governance basis

Accepted narrowed Product boundary:

- Product replacement head: `e6f79e92d60b1fea126db4efec321fd5ddc1ada7`
- Product P21 review: `5097117641`
- verdict: `PASS / ACCEPTED_FOR_DOWNSTREAM`
- change class: `PRODUCT_CLAIM_APPLICABILITY_NARROWING`

Accepted P23 applicability supersession:

- exact head: `b5677ad112a7a2067754b209ccde7fc97ef7469d`
- P22 drift review: `5097146033`
- P23 review: `5097214759`
- verdict: `PASS / AUTHORITY_SUPERSESSION_COMPLETE`

P23 freezes two deployment applicability labels:

```text
PLUGIN_PROFILE  = required v0.2 Product delivery envelope
SERVICE_PROFILE = optional later service realization / deployment claim
```

Current cross-Primary rollout remains:

```text
DENIED
```

This P20 repair does not alter that rollout policy.

## 1.2 Historical P20 basis

Accepted historical P20 package:

- `docs/control-plane-productization-verification-v0.2.md`
- `docs/control-plane-productization-verification-v0.2-p21-repair.md`
- accepted exact head: `db83168e4086e47a7f431acf289006e4f25b8ffd`
- P21 review: `5062933855`
- verdict: `PASS / ACCEPTED_FOR_DOWNSTREAM`

The historical P20 package remains normative except where this amendment is more specific about:

1. deployment-profile applicability;
2. release-blocking proof for `PLUGIN_PROFILE`;
3. transport/API proof that exists only when the corresponding physical boundary exists;
4. replacement engineering/repetition qualification after R0/S0 service-scale proof became conditional.

## 1.3 Accepted implementation evidence retained

Accepted semantic/control predecessor:

- CP-I08 result: `ac2bcf19acf46a749761ed455ecf0a995069700d`
- CP-I08 P34 review: `5079977191`
- verdict: `PASS / ACCEPTED_FOR_DOWNSTREAM`

P23 disposition:

```text
CP-I01 ... CP-I08 = RETAIN / DO NOT RERUN BY DEFAULT
```

Their accepted evidence remains usable for unchanged retained Claims, subject to exact-ref resolution and normal downstream applicability/ancestry checks.

## 1.4 Historical CP-I09 remains historical only

Old package:

- package: `CP-I09-P31-01`
- package ref: `9f4b76d51ce2e8a2c0ac23d6fba323bc078a9385`
- latest exact result: `85956ea32f7df9f393526473ad5da3382d49ad11`
- workflow: `33657495026`
- R0: `FAIL`
- S0: `FAIL`
- W7D: `PASS`
- combine: `SKIPPED`

P23 classification:

```text
STALE_PACKAGE_APPLICABILITY -> HISTORICAL_ONLY
```

This amendment does not turn any of those results into PASS and does not authorize resuming PR #44 P36.

---

# 2. Repair objective

The accepted historical P20 correctly proved deep semantic/control safety, but its final release profile inherited a stronger deployment claim than narrowed v0.2 now makes.

The repair objective is:

> **Preserve all evidence needed to prove the Control Plane semantics and Plugin / nine-Skill product form, while removing mandatory proof of an unclaimed dedicated service throughput/availability/economics profile.**

The controlling proof chain remains:

```text
Requirement
  -> Invariant
  -> Oracle / Reference
  -> Fixture / Corpus
  -> Test / Probe
  -> Metric
  -> Threshold
  -> Evidence Artifact
  -> P34 Gate
```

The implementation is still forbidden from being its own only oracle.

`Code Complete != Gate Complete` remains controlling.

---

# 3. Non-goals

This targeted repair does **not**:

- reopen P02/P03 Product semantics;
- reopen P10-P13 Modeling;
- redesign P14-P16 logical architecture;
- undo P23's P17/P18 applicability supersession;
- weaken `CoverageBasis = REVIEW_DECLARED`;
- weaken independent `O-CRM` / `O-COMPLETE` boundaries;
- remove G01-G44 semantic/fault coverage;
- remove M01-M20 verifier qualification;
- weaken exact refs, CAS, idempotency, commit-before-dispatch, currentness, immutable history, repair lineage, P33 resume, HumanDecision, or Gate ownership;
- authorize Current cross-Primary automatic continuation;
- claim R0/S0/W7D/monthly service attainment;
- delete old CP-I09 evidence;
- create a replacement CP-I09 package;
- begin P30/P31/P32/P34;
- merge, integrate, or release anything.

---

# 4. VerificationSpec identity after repair

The logical VerificationSpec remains the Control Plane v0.2 spec, now with profile-aware release applicability.

```yaml
verification_spec:
  id: aegis-control-plane-productization-v0.2
  scope: aegis/control-plane-productization
  version: p20-v0.2-plugin-profile-repair
  historical_p20_ref: db83168e4086e47a7f431acf289006e4f25b8ffd
  product_boundary_ref: e6f79e92d60b1fea126db4efec321fd5ddc1ada7
  p23_applicability_ref: b5677ad112a7a2067754b209ccde7fc97ef7469d
  required_release_profile: PLUGIN_PROFILE
  optional_profile: SERVICE_PROFILE
```

`CoverageBasis.mode` remains:

```text
REVIEW_DECLARED
```

P34 must still independently confirm coverage completeness against the exact accepted source set plus this amendment.

---

# 5. Requirement applicability repair

The historical Requirement universe `CPV-R01 ... CPV-R40` is preserved. No historical requirement is deleted.

This amendment changes release applicability and adds two new Plugin-profile requirements.

## 5.1 Required for v0.2 `PLUGIN_PROFILE`

The following remain release-blocking in their retained semantic/control meaning:

```text
CPV-R01 ... CPV-R24
CPV-R27 ... CPV-R38
```

with the profile clarifications below.

### R19 / API boundary clarification

`CPV-R19` remains mandatory for the logical mutation/capability boundary:

- no generic Gate/status/canonical mutation bypass;
- no worker/adapter direct canonical writes;
- application intents cannot invent new semantic mutation authority.

HTTP route names, public `/v1`, internal `/internal/v1`, and an Aegis-owned HTTPS process boundary are tested only when the candidate actually exposes those physical boundaries.

`PLUGIN_PROFILE` is not required to create a fake Aegis HTTP service merely to satisfy R19.

### R29 / observability clarification

`CPV-R29` remains mandatory for exact diagnostic/provenance observability required to audit semantic/control behavior.

It does not require proving a production service throughput dashboard, W7D cost attainment, or monthly availability dashboard for `PLUGIN_PROFILE`.

### R37 / R38 clarification

The semantic/policy conformance portions of retention and alerting remain testable through deterministic/virtual-time evidence, including G44.

Continuous production service retention/alert-attainment observation is conditional on a deployment actually claiming those operational defaults.

## 5.2 `SERVICE_PROFILE_CONDITIONAL`

The following historical requirements are not v0.2 `PLUGIN_PROFILE` release blockers:

```text
CPV-R25  R0 production-service engineering attainment
CPV-R26  S0 4x-R0 / 15-minute service-stress attainment
CPV-R39  7-day service economics attainment
CPV-R40  completed-month service availability attainment
```

They remain valid conditional obligations for `SERVICE_PROFILE` or a separately governed matching claim.

If such a claim is later adopted, these requirements reactivate without using this amendment to weaken their historical thresholds.

## 5.3 Added Requirement — CPV-R41

### `CPV-R41 Plugin-Profile Repeated Integration Stability`

Under the exact `PP0` qualification profile defined below, repeated and interleaved Control Plane execution MUST preserve the same semantic result as the independent oracle stack across independent WorkScopes, same-lane conflict probes, callback/reconciliation faults, interrupted resume, bounded repair, and external-truth faults.

Required end-state properties include:

- zero semantic mismatches against independent expected state;
- zero unauthorized canonical mutation;
- zero duplicate semantic occurrence caused by transport retry;
- zero dispatch-before-commit;
- zero stale/ambiguous external-truth success;
- zero wrong P33 execution-position classification;
- zero unofficial Gate decision;
- zero historical evidence rewrite;
- no residual operational work except fixtures explicitly ending in a governed blocked/escalated state;
- exact canonical record/lineage count equals the independent expected record set.

This is a **correctness-under-repetition** requirement, not a throughput claim.

No RPS, latency percentile, minimum wall-clock duration, or service-capacity threshold is implied.

## 5.4 Added Requirement — CPV-R42

### `CPV-R42 Plugin / Nine-Skill Product-Form Fidelity`

The v0.2 release candidate MUST demonstrate that the claimed `PLUGIN_PROFILE` preserves the accepted Control Plane boundaries through the actual product form:

- one Aegis Plugin exposes the exact reviewed nine-Skill catalog;
- central routing and specialist ownership remain consistent with Current Skill Decomposition Authority;
- execution-surface handoffs carry exact package/task-anchor/resume-cursor/materialized-ref semantics when applicable;
- conversation/session boundaries do not become sole durable lifecycle truth;
- exact durable refs used for continuation remain independently resolvable;
- P34 remains the only official Gate owner;
- Current rollout denial is preserved and no test falsely treats handoff capability as cross-Primary rollout authorization.

The platform corroboration may use the current ChatGPT/Codex/GitHub product surfaces. It is not evidence of 24x7 background service residency or high-RPS service capacity.

---

# 6. Claim applicability after repair

Historical Claims remain preserved. Applicability is repaired as follows.

## 6.1 Release-blocking for `PLUGIN_PROFILE`

Retained mandatory Claims:

```text
CPV-C01 Canonical Safety
CPV-C02 Dispatch / Idempotency Safety
CPV-C03 Historical Child / External Truth
CPV-C04 Ownership / Gate / Rollout Integrity
CPV-C05 Resume / Sessionless Control
CPV-C06 Human Decision Integrity
CPV-C07 API / Capability / Credential Boundary
CPV-C08 Derived / Operational State Separation
CPV-C09 Degraded Recovery / Durability
CPV-C10 D0 Semantic Conformance
CPV-C13 Retention / Replay / Audit
CPV-C14 Observability / Cost Attribution
CPV-C15 Snapshot / Async Provider Trust
CPV-C16 Delivery / Reconciliation Control
CPV-C17 Exact Envelope Representation
```

Applicability clarifications:

- C07 proves logical operation/capability boundaries unconditionally; network-specific HTTP conformance is conditional on an actual network boundary.
- C14 proves exact observability/correlation/cost-attribution correctness where cost data exists; it does not require W7D economics attainment.
- C16 retains deterministic timing-policy and no-semantic-retry proof; it does not require an S0 service-load run.
- C18 retains deterministic retention/alert policy conformance where implemented, while continuous production service-attainment observation is profile-conditional.

## 6.2 Conditional service Claims

```text
CPV-C11 R0 Engineering Budget            -> SERVICE_PROFILE_CONDITIONAL
CPV-C12 S0 Stress / Backpressure Safety   -> SERVICE_PROFILE_CONDITIONAL as a real-wall-clock service-load profile
CPV-C19 Long-window Cost / Availability   -> SERVICE_PROFILE_CONDITIONAL
```

The semantic backpressure/recovery properties historically exercised inside C12 remain covered by D0/G01-G44 and the new PP0 repetition profile. Only the mandatory 4x-R0 real-wall-clock service-load claim is conditionalized.

## 6.3 Added Claim — CPV-C20

### `CPV-C20 Plugin-Profile Repeated Integration Stability`

Requirements:

```text
CPV-R41
```

Criticality:

```text
CRITICAL
```

Minimum assurance:

```text
QUALIFIED
```

Base profile:

```text
REFERENCE + PROPERTY + INTEGRATION
```

Execution context:

```text
INTEGRATION
```

Statement:

> The Control Plane remains semantically correct under bounded repeated/interleaved product-representative execution without relying on service throughput as the product oracle.

## 6.4 Added Claim — CPV-C21

### `CPV-C21 Plugin Product-Form Corroboration`

Requirements:

```text
CPV-R42
```

Criticality:

```text
CRITICAL
```

Minimum assurance:

```text
CHALLENGED
```

Base profile:

```text
PLATFORM
```

Execution context:

```text
CROSS_IMPLEMENTATION / INSTALLED_PLATFORM
```

Statement:

> The actual Plugin / nine-Skill product form preserves the reviewed ownership, handoff, exact-ref, resume, materialization, and Gate boundaries needed by the narrowed v0.2 Product claim.

---

# 7. PP0 — Plugin Profile Release Qualification

P20 introduces one new release-blocking qualification profile:

```text
PP0 = Plugin Profile Release Qualification
```

PP0 is not R0-lite and is not a hidden throughput benchmark.

Its purpose is to expose race, state-drift, replay, reconciliation, resume, repair, and surface-integration defects at a representative bounded scale.

## 7.1 PP0 fixed workload shape

PP0 contains exactly five deterministic cohorts, each with eight independently addressed WorkScopes:

```text
Cohort A — clean lifecycle / routing / materialization                  8
Cohort B — duplicate delivery / callback loss / reconciliation          8
Cohort C — P33 resume and execution-position reconciliation              8
Cohort D — repair / rereview / escalation / REQUIRED-child boundaries    8
Cohort E — snapshot/currentness/capability/size/rate-limit policy         8
                                                                      ----
Total WorkScopes                                                         40
```

The workload identity, WorkScope IDs, seed set, expected final state, and injected fault schedule MUST be immutable evidence inputs.

## 7.2 Cohort A — clean lifecycle / routing / materialization

Each of eight scopes exercises a legal end-to-end control path through representative stage ownership and exact materialization boundaries.

Required probes include:

- deterministic next-owner derivation;
- exact task/package binding where implementation work exists;
- committed canonical transition before any dispatch observation;
- exact materialized result refs;
- no lifecycle truth derived solely from conversation history;
- P34 outcome remains externally owned.

Current rollout policy is respected: the harness MUST NOT turn this cohort into unauthorized automatic cross-Primary progression.

## 7.3 Cohort B — transport / callback / reconciliation

Across eight scopes, inject a deterministic mix of:

- duplicate delivery;
- callback loss;
- duplicate callback;
- callback reordering;
- delayed provider materialization;
- transport retry;
- provider query recovery.

Required outcome:

- one semantic occurrence per intended substantive attempt;
- query/refetch reconciliation recovers durable provider truth where supported;
- no callback becomes canonical truth by itself;
- no replacement occurrence is invented from transport uncertainty.

## 7.4 Cohort C — P33 resume

Eight scopes cover the exact four accepted execution-position outcomes twice each:

```text
EXACT_CURSOR                         x2
DESCENDANT_CURSOR                    x2
ANCHOR_DESCENDANT_WITHOUT_CURSOR     x2
DIVERGED                             x2
```

Required outcome:

- valid descendant work is preserved;
- completed work is not replayed;
- a missing accepted cursor is established only through the accepted contract;
- true divergence fails closed;
- task anchor is never treated as execution cursor equality.

## 7.5 Cohort D — repair / rereview / escalation / child barrier

Across eight scopes, exercise a deterministic mix of:

- bounded P35/P36 repair lineage;
- separate reverify and rereview occurrences;
- repair-attempt budget exhaustion;
- exact HumanDecision resolution ref;
- REQUIRED child acceptance barrier;
- parent successor pinned to exact historical child acceptance facts;
- terminalization/successor separation.

Required outcome:

- no semantic attempt identity collapse;
- no mutable historical acceptance rewrite;
- no parent barrier crossing without exact accepted child facts;
- exhausted repair policy fails closed rather than looping indefinitely.

## 7.6 Cohort E — external truth / boundary conformance

Across eight scopes, exercise a deterministic mix of:

- valid and tampered SourceSnapshotToken;
- wrong adapter/source binding;
- wrong provider resource/version binding;
- callback-only provider capability claim;
- provider currentness change before commit;
- canonical envelope around size/truncation boundaries;
- rate-limit policy transition;
- virtual-time retention/alert boundary behavior.

Required outcome:

- all tampered/stale/cross-boundary truth fails closed;
- no silent canonical truncation;
- operational timing/rate-limit state does not create semantic truth;
- service throughput is not inferred from policy correctness.

## 7.7 Concurrency/interleaving requirement

PP0 MUST include deterministic logical interleaving sufficient to challenge concurrency invariants without imposing a throughput target:

- maximum simultaneously active PP0 WorkScopes: `8`;
- at least `8` unrelated-lane interleavings;
- at least `4` deliberate same-lane conflict/CAS probes;
- exactly one legal canonical winner for each deliberate same-lane race;
- unrelated WorkScopes must not acquire false shared semantic serialization.

The runtime duration is diagnostic only.

PP0 does not PASS or FAIL based on requests per second, latency percentile, wall-clock duration, or infrastructure utilization.

## 7.8 PP0 completion / convergence

After the finite fixture schedule is exhausted:

- every non-blocked scope must converge to the exact oracle-expected stable state;
- every deliberately blocked/escalated scope must remain in the exact expected governed blocked/escalated state;
- no unexpected OPEN occurrence remains;
- no unexpected ready outbox work remains;
- no unresolved delivery work remains except where the fixture's expected result is explicitly delivery-uncertain;
- canonical record/revision lineage must match independent expected state exactly.

---

# 8. PP0 oracle stack

PP0 reuses the accepted independent oracle stack.

Mandatory:

```text
O-AUTH
O-CRM
O-STORE
O-PROVIDER
O-COMPLETE
O-SNAPSHOT
O-TIMEPOLICY
```

Conditional:

```text
O-CONTRACT network-specific checks
  only when the candidate exposes the corresponding Aegis-owned network boundary

O-PERF
  not required for PP0 PASS
  mandatory only for SERVICE_PROFILE performance claims
```

Platform corroboration:

```text
O-PLATFORM
```

is retained but repaired in scope as defined below.

---

# 9. O-PLATFORM applicability repair

Historical P20 required real-platform corroboration for the full production profile.

For v0.2 `PLUGIN_PROFILE`, O-PLATFORM means a **fresh installed-product corroboration**, not a production Aegis service deployment.

At minimum the exact release candidate must produce reviewer-resolvable evidence for:

1. one installed Aegis Plugin materializing the exact expected nine-Skill catalog;
2. central router ownership on a routing-only request;
3. at least one specialist-owned substantive result when that specialist is available;
4. an execution-surface handoff preserving exact task/package/anchor/cursor/materialized-ref semantics where applicable;
5. a sessionless/resume observation proving durable continuation does not rely solely on one conversation transcript;
6. no unofficial Gate PASS and no cross-Primary rollout expansion.

Fresh platform evidence may reuse already-qualified platform contracts and fixtures, but it MUST bind the exact candidate identity being reviewed.

A historical Plugin install against an older candidate is provenance, not sufficient final-candidate corroboration by itself.

---

# 10. Existing G01-G44 / M01-M20 status

The mandatory deterministic proof corpus remains:

```text
G01-G44 = required
M01-M20 = required
```

Threshold remains:

```text
G01-G44 mandatory scenarios: PASS
semantic mismatches vs independent oracle stack: 0
zero-tolerance invariant events: 0
M01-M20 mandatory mutant detection: 100%
false ACCEPT/PASS on mandatory mutant corpus: 0
```

This amendment does not transform G01-G44 into performance tests.

Where a G scenario validates retry cadence, rate-limit adaptation, retention, alerting, payload boundaries, or backpressure, its v0.2 `PLUGIN_PROFILE` purpose is policy/semantic correctness unless a matching service claim is separately active.

---

# 11. Evidence inheritance rules

Accepted CP-I01..CP-I08 evidence may be inherited rather than rerun when all of the following are true:

1. the evidence ref is immutable and independently resolvable;
2. the Claim it proves remains release-applicable under this amendment;
3. no accepted downstream semantic/architecture change invalidates the evidence basis;
4. exact lineage/applicability shows the candidate still contains the reviewed behavior or an independently reviewed equivalent;
5. current regression on the qualification candidate does not contradict the inherited result.

Evidence inheritance MUST be explicit in the final manifest. Silent assumption is not sufficient.

If any exact applicability/lineage question cannot be resolved, the affected Claim becomes `BLOCKED_EVIDENCE` until requalified.

This rule means:

```text
RETAIN / DO NOT RERUN BY DEFAULT
!=
TRUST WITHOUT RESOLUTION
```

---

# 12. Required PP0 evidence bundle

The replacement release qualification must materialize reviewer-accessible durable evidence containing at least:

```text
pp0-workload-manifest.json
pp0-trace-corpus.json
pp0-conformance.json
pp0-platform-corroboration.json
engineering-handoff.json
evidence-manifest.json
```

## 12.1 `pp0-workload-manifest.json`

Must bind:

- exact result revision;
- exact P20 repair ref;
- exact P23 ref;
- exact accepted CP-I08 predecessor/evidence refs used by inheritance;
- PP0 cohort identities;
- exact 40 WorkScope identities;
- deterministic seed/fault schedule;
- logical interleaving plan;
- runtime/tool versions relevant to reproduction.

## 12.2 `pp0-trace-corpus.json`

Must contain enough immutable trace state for independent replay/inspection of:

- canonical occurrence lineage;
- lane/CAS outcomes;
- idempotency results;
- outbox/dispatch/reconciliation relations;
- external snapshot/provider observations;
- repair/escalation/child-barrier transitions;
- P33 outcomes.

## 12.3 `pp0-conformance.json`

Must record independent oracle results and all zero-tolerance metrics.

## 12.4 `pp0-platform-corroboration.json`

Must bind reviewer-resolvable fresh installed-platform evidence to the exact candidate identity without claiming a service-scale deployment.

## 12.5 `engineering-handoff.json`

Must state the exact implementation/evidence result being returned to P34 and list inherited evidence refs separately from newly materialized PP0 evidence.

## 12.6 `evidence-manifest.json`

Must provide:

- exact artifact digests;
- exact result revision;
- exact Authority refs;
- exact package/task anchor when a later P31 exists;
- Claim/Requirement coverage;
- inherited vs newly executed evidence classification;
- no-service-profile-claim flags;
- current rollout status.

---

# 13. PP0 zero-tolerance metrics

PP0 PASS requires all of the following to equal zero:

```text
semantic_oracle_mismatches
unauthorized_canonical_mutations
duplicate_semantic_occurrences_from_transport
commit_before_dispatch_violations
stale_or_ambiguous_snapshot_successes
invalid_snapshot_tokens_accepted
wrong_p33_classifications
completed_work_replayed_on_resume
required_child_barrier_violations
repair_budget_overruns
unofficial_gate_decisions
historical_evidence_rewrites
silent_canonical_truncations
unexpected_open_occurrences_at_end
unexpected_ready_outbox_at_end
unexpected_unresolved_delivery_at_end
unresolvable_required_evidence_refs
```

Additional required exact state:

```text
G01_G44 = PASS
M01_M20_detected = 20/20
M01_M20_false_acceptance = 0
current_cross_primary_rollout = DENIED
```

Final canonical record/revision set must equal the independent expected set exactly.

---

# 14. Explicit PP0 non-metrics

The following MUST NOT be used as PP0 release thresholds:

```text
requests per second
mutations per second
projection evaluations per second
provider events per second
latency p50/p95/p99
minimum wall-clock stress duration
10,000 active WorkScopes
100 interactive clients
4x R0 load
7-day cost ratio
completed-month availability
multi-region capacity
24x7 background residency
```

Those are not current v0.2 `PLUGIN_PROFILE` Product claims.

A PP0 run may record runtime/resource diagnostics, but they are characterization only unless a separately governed requirement gives them release authority.

---

# 15. Service-profile reactivation rule

If a later accepted Product Authority explicitly claims any of the following:

- dedicated production Aegis Control Service readiness;
- R0 service capacity/latency;
- S0 service-load resilience;
- W7D service economics;
- completed-month Aegis service availability;

then the matching historical P18/P20 obligations reactivate:

```text
R25 / C11
R26 / C12
R39 / C19 cost portion
R40 / C19 availability portion
O-PERF and exact historical measurement contracts
```

Old failed CP-I09 R0/S0 evidence remains historical FAIL and cannot satisfy the reactivated Claims.

A new exact candidate must produce new valid evidence under the then-current Authority.

---

# 16. Replacement implementation/evidence package boundary

This P20 repair intentionally does **not** create a P31 package.

Only after this exact P20 candidate receives fresh P21 `PASS / ACCEPTED_FOR_DOWNSTREAM` may `aegis-implementation` decide the minimum downstream package needed to close the new release proof.

Expected implementation planning constraint:

> Prefer evidence reuse and the smallest new qualification surface. Do not create new service benchmark machinery merely because old CP-I09 had it.

A later P30/P31 may determine that the remaining work is primarily evidence aggregation/PP0 qualification rather than new production runtime behavior.

That decision belongs to implementation planning after P20 acceptance.

---

# 17. P34 review contract after repair

For `PLUGIN_PROFILE`, P34 must independently verify at least:

1. this P20 amendment is the accepted exact Verification Authority;
2. required Claim coverage is complete under `REVIEW_DECLARED`;
3. G01-G44 remains complete and PASS;
4. M01-M20 remains 100% detected / 0 false acceptance;
5. inherited CP-I01..CP-I08 evidence is exact, resolvable, and still applicable;
6. PP0 exact 40-scope workload identity and deterministic cohort coverage are complete;
7. PP0 zero-tolerance metrics are all zero;
8. independent expected canonical record/lineage set matches actual evidence;
9. fresh exact-candidate installed Plugin / nine-Skill platform corroboration is valid;
10. exact execution-surface/resume/materialization boundaries are preserved;
11. `current_cross_primary_rollout = DENIED`;
12. no R0/S0/W7D/monthly service claim is inferred from PP0;
13. old CP-I09 historical failures remain historical and unmodified;
14. P34 itself, not CI/PP0/ProofEvaluation, owns the final Gate verdict.

Missing a mandatory item is a real Gate blocker, not a cosmetic finding.

---

# 18. P20 targeted repair acceptance criteria

This P20 repair is acceptable only if fresh P21 review confirms:

1. it implements P23's applicability decision without reopening Product/Model/Architecture semantics;
2. semantic proof strength is not weakened;
3. `PLUGIN_PROFILE` has a concrete release-blocking proof profile rather than merely deleting R0/S0;
4. PP0 repetition/interleaving is clearly a correctness profile, not disguised service performance;
5. G01-G44 and M01-M20 remain mandatory;
6. API/network proof is conditional only where P17 made the physical boundary conditional, while logical mutation/capability safety remains mandatory;
7. fresh installed-product corroboration proves the actual Plugin/nine-Skill form;
8. accepted CP-I01..CP-I08 evidence may be inherited only through exact applicability/lineage resolution;
9. old CP-I09 remains historical-only and no FAIL is rewritten;
10. R0/S0/W7D/monthly obligations reactivate if their matching service claims are later adopted;
11. rollout remains `DENIED`;
12. no implementation package, merge, release, or P34 verdict is implied.

---

# 19. P20 disposition

```yaml
P20_targeted_repair:
  scope: aegis/control-plane-productization/verification

  historical_p20_ref: db83168e4086e47a7f431acf289006e4f25b8ffd
  historical_p20_review: 5062933855

  product_boundary_ref: e6f79e92d60b1fea126db4efec321fd5ddc1ada7
  product_review: 5097117641

  p23_ref: b5677ad112a7a2067754b209ccde7fc97ef7469d
  p23_review: 5097214759

  coverage_basis: REVIEW_DECLARED

  retained_release_proof:
    G01_G44: REQUIRED
    M01_M20: REQUIRED
    semantic_zero_tolerance: REQUIRED
    P34_independence: REQUIRED
    exact_evidence_provenance: REQUIRED

  new_requirements:
    - CPV-R41
    - CPV-R42

  new_claims:
    - CPV-C20
    - CPV-C21

  release_profile:
    name: PP0
    purpose: PLUGIN_PROFILE correctness-under-repetition + installed-product corroboration
    workscopes: 40
    service_throughput_claim: NOT_CLAIMED
    service_latency_claim: NOT_CLAIMED
    availability_claim: NOT_CLAIMED
    economics_claim: NOT_CLAIMED

  conditional_service_proof:
    R25_C11: SERVICE_PROFILE_CONDITIONAL
    R26_C12: SERVICE_PROFILE_CONDITIONAL
    R39_C19_cost: SERVICE_PROFILE_CONDITIONAL
    R40_C19_availability: SERVICE_PROFILE_CONDITIONAL

  CP_I01_I08: RETAIN_WITH_EXACT_EVIDENCE_RESOLUTION
  old_CP_I09: HISTORICAL_ONLY
  old_CP_I09_P36_resume: false

  current_cross_primary_rollout: DENIED

  replacement_CP_I09_package_authorized_now: false

  status: MATERIALIZED_DRAFT_PROPOSED
  next_owner: aegis-governance
  next_stage: P21_AUTHORITY_REVIEW
```

Stop at P20 materialization.

Do not begin P21 review, P30/P31 packaging, implementation, PR #44 P36, merge, release, rollout expansion, or P34 automatically.
