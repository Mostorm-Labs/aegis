# Aegis Control Plane Productization v0.2 — P30 Plugin-Profile Closure Plan

Status: **P30 COMPLETE / MATERIALIZED — targeted implementation-plan amendment**

Scope: `aegis/control-plane-productization/implementation-plan`

Owner: `aegis-implementation`

Execution surface: `CONTROL_REASONING`

This document is a targeted amendment to the historical P30 implementation plan. It preserves the accepted CP-I01 through CP-I08 slices and replaces only the old terminal CP-I09 service-scale evidence slice with the minimum implementation/evidence work required by the accepted `PLUGIN_PROFILE` Verification Authority.

It is not Product, Modeling, Architecture, or Verification Authority. It does not begin P32 implementation, issue P34 PASS, merge a branch, publish a release, resume PR #44, or authorize `SERVICE_PROFILE`.

---

## 1. Exact trusted basis

### 1.1 Product / Governance

Accepted narrowed Product boundary:

- Product replacement head: `e6f79e92d60b1fea126db4efec321fd5ddc1ada7`
- Product P21 review: `5097117641` — `PASS / ACCEPTED_FOR_DOWNSTREAM`

Accepted applicability supersession:

- P23 exact head: `b5677ad112a7a2067754b209ccde7fc97ef7469d`
- P23 review: `5097214759` — `PASS / AUTHORITY_SUPERSESSION_COMPLETE`

Controlling deployment labels:

```text
PLUGIN_PROFILE  = required v0.2 delivery envelope
SERVICE_PROFILE = optional later service realization / claim
```

Current cross-Primary rollout remains:

```text
DENIED
```

### 1.2 Accepted Verification Authority

Historical accepted P20:

- `db83168e4086e47a7f431acf289006e4f25b8ffd`
- review `5062933855` — `PASS / ACCEPTED_FOR_DOWNSTREAM`

Accepted Plugin-profile repair:

- exact head: `d6b795ce4a40a422d26f74d749cc823dd66a26df`
- P21 rereview: `5097554177` — `PASS / ACCEPTED_FOR_DOWNSTREAM`

Release-blocking `PLUGIN_PROFILE` proof includes:

- `CoverageBasis = REVIEW_DECLARED`;
- G01-G44 mandatory semantic/fault corpus;
- M01-M20 verifier qualification at `20/20 detected / 0 false acceptance`;
- PP0 exact 40-WorkScope correctness-under-repetition qualification;
- fresh installed Plugin / nine-Skill product-form corroboration;
- exact evidence provenance and explicit evidence inheritance;
- `CPV-R37 -> CPV-C18 -> P34` and `CPV-R38 -> CPV-C18 -> P34`;
- P34 as sole official Gate owner;
- rollout `DENIED`.

The following remain `SERVICE_PROFILE_CONDITIONAL` and are not release blockers for this plan:

- R25/C11 R0 throughput/latency/service budget;
- R26/C12 real-wall-clock S0 4x service load;
- R39/C19 seven-day service economics;
- R40/C19 completed-month service availability;
- continuous production-service retention/alert attainment.

### 1.3 Accepted implementation predecessor

Accepted semantic/control implementation predecessor:

- CP-I08 exact result: `ac2bcf19acf46a749761ed455ecf0a995069700d`
- CP-I08 P34 review: `5079977191` — `PASS / ACCEPTED_FOR_DOWNSTREAM`

P23/P20 disposition:

```text
CP-I01 ... CP-I08 = RETAIN / DO NOT RERUN BY DEFAULT
```

Evidence inheritance remains conditional on exact immutable refs, applicability, lineage/equivalence, and non-contradictory current regression.

### 1.4 Current published Plugin baseline

Current `main`:

`38bf619ede0615431c7517bc0e07984136af28cf`

Published maintenance baseline:

`v0.1.0-beta.3`

The main commit preserves the exact-nine native Plugin materialization and the Codex execution-prefix / execution-surface handoff behavior that v0.2 must inherit.

Repository ancestry observation:

- `main@38bf619...` and CP-I08 result `ac2bcf...` share base `a77fca147ead0d66484201cad30d8c6a80d11f8e`;
- CP-I08 is the 245-commit Control Plane implementation stack from that base;
- current main adds one maintenance-release commit from that same base.

Therefore v0.2 qualification must converge both histories into one exact candidate before final PP0/product-form evidence is accepted.

### 1.5 Historical CP-I09

Historical package:

- package ID: `CP-I09-P31-01`
- package ref: `9f4b76d51ce2e8a2c0ac23d6fba323bc078a9385`

Historical implementation/evidence PR:

- PR #44
- latest result revision: `85956ea32f7df9f393526473ad5da3382d49ad11`
- workflow `33657495026`
- R0 `FAIL`
- S0 `FAIL`
- W7D `PASS`
- combine `SKIPPED`

Disposition:

```text
HISTORICAL_ONLY
```

This plan does not resume that package or PR. The old R0/S0/W7D harness is not the default source for the new Plugin-profile qualification.

---

## 2. P30 decision

The historical P30 dependency chain remains valid through CP-I08.

The old terminal slice:

```text
CP-I09 = R0 + S0 + seven-day service evidence
```

is superseded for active v0.2 `PLUGIN_PROFILE` planning by:

```text
CP-I09 = Plugin-profile qualification closure
```

The active package revision will be:

```text
CP-I09-P31-02
```

`CP-I09-P31-01` remains preserved as historical-only rather than being rewritten.

No CP-I10 is introduced because there is no new product capability after CP-I08; the work remains the final qualification slice for the same Control Plane implementation sequence under a repaired Verification applicability contract.

---

## 3. Minimum active slice

### CP-I09 — Plugin-profile qualification closure

Purpose:

> Converge the accepted Control Plane implementation with the current exact-nine Plugin baseline into one exact qualification candidate, prove retained semantic evidence still applies, execute PP0 correctness-under-repetition, capture fresh Plugin/nine-Skill product-form corroboration, and materialize one reviewer-resolvable evidence bundle for P34.

This slice is evidence-heavy. New production semantics are not expected.

### Required phases

```text
A. exact baseline convergence
B. inherited-evidence resolution + current regression
C. PP0 deterministic qualification
D. fresh installed Plugin / nine-Skill corroboration
E. final evidence aggregation/materialization
```

These are phases inside one P31 package, not five independently authorized semantic packages.

---

## 4. Phase A — exact baseline convergence

### 4.1 Starting trust anchor

Repository-backed implementation must use:

```yaml
task_anchor:
  revision: ac2bcf19acf46a749761ed455ecf0a995069700d
  relation: ancestor
```

`Task Anchor != Execution Cursor` remains controlling.

### 4.2 Published baseline to converge

The exact current Plugin maintenance baseline to incorporate is:

```text
38bf619ede0615431c7517bc0e07984136af28cf
```

The qualification candidate must preserve ancestry from both:

```text
ac2bcf19acf46a749761ed455ecf0a995069700d
38bf619ede0615431c7517bc0e07984136af28cf
```

Preferred implementation is an ancestry-preserving merge into a dedicated child execution branch created from CP-I08.

A cherry-pick that obscures the exact published-main ancestry is not the preferred final evidence shape.

### 4.3 Merge-conflict policy

Mechanical conflict resolution is allowed only when it preserves both accepted contracts:

1. CP-I08 Control Plane behavior and accepted semantic evidence;
2. beta.3 Plugin/handoff/execution-prefix behavior.

If a conflict requires choosing one semantic contract over the other, inventing a new Skill behavior, changing ownership, changing Gate semantics, weakening evidence, or modifying Product/Model/Architecture/Verification Authority, P32 must fail closed rather than resolve it locally.

Return classification should be `BLOCKED_AUTHORITY`, `BLOCKED_EXECUTION_DIVERGENCE`, or the more specific existing blocker.

### 4.4 Convergence evidence

The final evidence bundle must record:

- exact merge/base parents;
- proof both trusted revisions are ancestors of the qualification candidate;
- exact conflict list and resolution classification;
- current `main` identity used for convergence;
- zero unresolved merge conflict;
- no historical evidence rewrite.

---

## 5. Phase B — inherited evidence resolution

CP-I01..CP-I08 are not rerun wholesale by default.

The executor must build an explicit inheritance manifest that binds each inherited Claim/evidence family to immutable refs and states why it remains applicable to the converged candidate.

At minimum resolve:

- CP-I08 result `ac2bcf...`;
- CP-I08 P34 `5079977191`;
- G01-G44 evidence identity;
- M01-M20 qualification evidence identity;
- independent O-CRM / O-COMPLETE boundary evidence;
- P33 four-outcome evidence;
- retention/alert deterministic policy evidence;
- exact evidence/materialization provenance.

The converged qualification candidate must run current regression sufficient to detect contradiction with inheritance.

Required current regression includes:

```text
G01-G44 = PASS
M01-M20 detected = 20/20
M01-M20 false acceptance = 0
Control Plane regression = PASS
Project State regression = PASS
Skillset / Plugin materialization regression = PASS
```

If current regression contradicts inherited evidence, the affected Claim is not inherited and the task fails closed for repair/requalification.

`RETAIN != TRUST WITHOUT RESOLUTION`.

---

## 6. Phase C — PP0 implementation/evidence

PP0 must implement the exact accepted Verification profile.

### 6.1 Fixed workload

Exactly 40 deterministic WorkScopes:

```text
A clean lifecycle / routing / materialization                  8
B duplicate delivery / callback loss / reconciliation          8
C P33 resume outcomes                                          8
D repair / rereview / escalation / REQUIRED-child              8
E snapshot/currentness/capability/size/rate-limit policy       8
                                                               --
Total                                                         40
```

Immutable PP0 inputs must include:

- WorkScope IDs;
- deterministic seeds;
- expected canonical state;
- injected fault schedule;
- logical interleaving plan;
- exact Authority refs;
- exact qualification candidate revision.

### 6.2 Interleaving contract

Required:

```text
max simultaneously active WorkScopes = 8
unrelated-lane interleavings >= 8
deliberate same-lane CAS conflict probes >= 4
legal canonical winners per same-lane race = exactly 1
```

Unrelated WorkScopes must not acquire false global semantic serialization.

No RPS, latency percentile, minimum wall-clock duration, service capacity, or infrastructure-utilization PASS threshold exists.

### 6.3 PP0 zero-tolerance metrics

All must equal zero:

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

Additional required state:

```text
G01_G44 = PASS
M01_M20_detected = 20/20
M01_M20_false_acceptance = 0
current_cross_primary_rollout = DENIED
```

Actual canonical revision/lineage set must equal independent expected state exactly.

### 6.4 Oracle requirements

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

Network-specific O-CONTRACT checks apply only if the converged candidate exposes the corresponding network boundary.

O-PERF is not a PP0 PASS oracle.

---

## 7. Phase D — fresh Plugin / nine-Skill product-form corroboration

The corroboration must bind the same exact qualification candidate used by PP0.

At minimum prove reviewer-resolvable facts for:

1. one installed Aegis Plugin exposes exactly the reviewed nine Skills;
2. Plugin skill trees match canonical Skill trees for that candidate;
3. central `aegis` owns a routing-only request;
4. at least one available specialist owns a substantive result in its stage family;
5. an execution-surface handoff preserves exact package/task-anchor/resume/materialized-ref semantics;
6. when `preferred_executor: codex`, the exact accepted execution prefix is rendered before the handoff envelope;
7. sessionless/resume behavior does not rely solely on one conversation transcript;
8. P34 remains the only official Gate owner;
9. current cross-Primary rollout remains `DENIED`;
10. no evidence claims 24x7 agent residency, service throughput, or autonomous background service behavior.

Repository-only exact-nine tests are necessary but not sufficient for this phase. Fresh installed-platform observations must be reviewer-resolvable and identify the exact candidate/materialization being exercised.

If the installed platform cannot bind the exact candidate or preserve the required evidence identity, return `BLOCKED_EVIDENCE`; do not substitute historical beta.3 install evidence as final-candidate corroboration.

---

## 8. Phase E — final evidence materialization

Required durable bundle:

```text
pp0-workload-manifest.json
pp0-trace-corpus.json
pp0-conformance.json
pp0-platform-corroboration.json
engineering-handoff.json
evidence-manifest.json
```

The evidence manifest must distinguish:

```text
INHERITED_EVIDENCE
NEW_PP0_EVIDENCE
NEW_PLATFORM_CORROBORATION
CHARACTERIZATION_ONLY
HISTORICAL_ONLY
```

Old CP-I09 R0/S0/W7D evidence must appear only as `HISTORICAL_ONLY` provenance if referenced.

No old R0/S0 FAIL may be reclassified as PASS.

The exact result must be materialized at a reviewer-accessible durable GitHub ref/PR plus hosted artifacts or equivalent resolvable evidence refs. Local-only logs are insufficient.

---

## 9. Authorized implementation surfaces

Expected new/modified implementation-test surfaces are intentionally narrow:

```text
.github/workflows/control-plane-cp-i09-plugin-profile.yml

tests/control_plane/cp_i09_plugin_profile.py
tests/control_plane/generate_cp_i09_plugin_profile_evidence.py
tests/control_plane/test_cp_i09_plugin_profile*.py

tests/skillset/test_control_plane_plugin_profile*.py        # only if needed for deterministic candidate checks
skillset/dogfood/control-plane-v0.2-plugin-profile*.json    # fresh platform evidence manifest/slots
```

Existing CP-I08 fixtures/oracles/tests should be reused where possible rather than copied.

Small production repairs under:

```text
tools/aegis_control/**
```

are allowed only if PP0 exposes a concrete implementation defect in an already-authorized semantic contract, RED evidence exists first, and the repair does not change Authority or expand Product scope.

Not authorized by default:

```text
skills/**
plugins/aegis/skills/**
.aegis/**
Product/Modeling/Architecture/Verification Authority documents
release version / GitHub release publication
new service daemon / API / worker topology
old R0/S0 benchmark machinery
```

The beta.3 merge may naturally introduce its already-published Skill/materialization changes. New semantic edits to those files are not authorized inside CP-I09-P31-02; any such need must fail closed and route to the owning earlier layer.

---

## 10. TDD / fail-closed harness contract

Before claiming PP0 evidence, short deterministic tests must prove the new qualification harness rejects at least:

1. PP0 WorkScope count != 40;
2. any cohort count != 8;
3. duplicate WorkScope ID;
4. mutable/missing seed or fault schedule identity;
5. missing one of the four accepted P33 outcomes;
6. fewer than four same-lane conflict probes;
7. same-lane race with zero or multiple canonical winners;
8. unexpected OPEN/outbox/delivery residue;
9. any nonzero PP0 zero-tolerance metric;
10. incomplete G01-G44 or M01-M20 inheritance/current-regression status;
11. unresolvable inherited evidence ref;
12. platform corroboration bound to a different candidate revision;
13. Plugin catalog != exact nine;
14. missing/incorrect Codex execution-prefix behavior;
15. unofficial Gate PASS or rollout != `DENIED`;
16. attempted PP0 PASS based on RPS/latency/wall-clock/service metrics;
17. attempted reuse of old CP-I09 R0/S0 as Plugin-profile PASS evidence.

These tests qualify the harness; they do not themselves constitute the required 40-scope PP0 execution or fresh platform corroboration.

---

## 11. Performance constraints

There is no release-blocking service performance target in this package.

Allowed diagnostics:

- total runtime;
- CPU/RSS;
- local queue depth;
- test duration;
- artifact size.

These are characterization only.

A performance optimization must not be introduced merely to improve such diagnostics.

---

## 12. Exit criteria for CP-I09 replacement slice

The slice is ready to return toward P34 only when one exact candidate satisfies all of the following:

1. both `ac2bcf...` and `38bf619...` are ancestors of the candidate;
2. no unresolved semantic merge conflict exists;
3. inherited CP-I01..CP-I08 evidence manifest is exact/resolvable/applicable;
4. G01-G44 current regression PASS;
5. M01-M20 current qualification `20/20`, false acceptance 0;
6. PP0 exact 40-WorkScope manifest complete;
7. every PP0 zero-tolerance metric = 0;
8. expected canonical lineage set = actual exactly;
9. fresh exact-candidate Plugin/nine-Skill corroboration complete;
10. exact-nine Plugin materialization verified;
11. sessionless/handoff/execution-prefix/Gate/rollout boundaries corroborated;
12. evidence bundle is reviewer-resolvable and digest-bound;
13. old CP-I09 remains historical-only;
14. no R0/S0/W7D/monthly attainment claim is made;
15. rollout remains `DENIED`;
16. final return contains a durable `materialized_ref`.

P32 completion is not P34 PASS.

---

## 13. Blocked return behavior

Return immediately without inventing a fix when any of the following occurs:

```text
Authority conflict                  -> BLOCKED_AUTHORITY
repository ancestry cannot converge -> BLOCKED_EXECUTION_DIVERGENCE
required inherited ref unresolved   -> BLOCKED_EVIDENCE
fresh platform candidate unbindable -> BLOCKED_EVIDENCE
PP0 exposes implementation defect   -> BLOCKED_IMPLEMENTATION until authorized repair/verification
environment prevents required proof -> BLOCKED_ENVIRONMENT
```

If a PP0 defect can be repaired inside the already-authorized `tools/aegis_control/**` scope without changing semantics, P32 may perform RED-first repair and reverify under the same package. Otherwise fail closed.

---

## 14. Historical P30 supersession boundary

Historical P30 exact ref:

`87cbb166411795261ec5f6e7034a89435e053451`

Disposition:

```text
CP-I01 ... CP-I08 planning = RETAIN
historical CP-I09 service-evidence planning = SUPERSEDED_FOR_PLUGIN_PROFILE
```

This amendment controls only the terminal CP-I09 planning applicability for narrowed v0.2.

If a future Product Authority opts into `SERVICE_PROFILE`, the historical R0/S0/W7D planning may be reactivated under fresh planning/verification review; this amendment does not erase it.

---

## 15. P30 disposition

```yaml
P30_return:
  scope: aegis/control-plane-productization/implementation-plan
  mode: targeted_terminal_slice_repair

  product_ref: e6f79e92d60b1fea126db4efec321fd5ddc1ada7
  p23_ref: b5677ad112a7a2067754b209ccde7fc97ef7469d
  verification_ref: d6b795ce4a40a422d26f74d749cc823dd66a26df
  verification_review: 5097554177

  historical_p30_ref: 87cbb166411795261ec5f6e7034a89435e053451
  cp_i01_i08: RETAIN

  accepted_implementation_predecessor: ac2bcf19acf46a749761ed455ecf0a995069700d
  accepted_cp_i08_p34: 5079977191
  current_plugin_main: 38bf619ede0615431c7517bc0e07984136af28cf

  old_cp_i09:
    package: CP-I09-P31-01
    ref: 9f4b76d51ce2e8a2c0ac23d6fba323bc078a9385
    disposition: HISTORICAL_ONLY

  active_terminal_slice:
    id: CP-I09
    purpose: PLUGIN_PROFILE_QUALIFICATION_CLOSURE
    planned_package: CP-I09-P31-02

  phases:
    - baseline_convergence
    - evidence_inheritance_resolution
    - PP0_qualification
    - fresh_plugin_product_form_corroboration
    - final_evidence_materialization

  service_profile_claim: NOT_AUTHORIZED
  rollout: DENIED

  status: P30_COMPLETE
  next_stage: P31_TASK_PACKAGING
```

P30 stops at planning. P31 may now freeze exactly one replacement package for the active terminal slice.