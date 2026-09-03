# Aegis Control Plane Productization v0.2 — CP-I09 P31 Plugin-Profile Qualification Package

Status: **P31 READY / MATERIALIZED — replacement CP-I09 package only**

Package ID: `CP-I09-P31-02`

Primary Owner: `aegis-implementation`

Execution surface: `CONTROL_REASONING -> CODE_EXECUTION`, with a required fresh installed-platform corroboration leg before final P34 return.

This package replaces `CP-I09-P31-01` only for active v0.2 `PLUGIN_PROFILE` applicability. The historical package and all historical R0/S0/W7D evidence remain preserved.

This package authorizes the minimum repository/evidence work required to close the accepted Plugin-profile Verification contract. It does not authorize a dedicated service product, R0/S0/W7D/monthly service claims, rollout expansion, P34 PASS, merge to main, or release publication.

---

## 1. Task identity

```yaml
package_id: CP-I09-P31-02
task_id: CP-I09
purpose: PLUGIN_PROFILE_QUALIFICATION_CLOSURE
primary_owner: aegis-implementation
preferred_code_executor: codex
review_return_surface: CONTROL_REVIEW
```

Historical package:

```yaml
package_id: CP-I09-P31-01
package_ref: 9f4b76d51ce2e8a2c0ac23d6fba323bc078a9385
disposition: HISTORICAL_ONLY
```

PR #44 remains paused and is not the execution branch for this package.

---

## 2. Exact Current Authority / accepted basis

### Product

- narrowed Product head: `e6f79e92d60b1fea126db4efec321fd5ddc1ada7`
- Product P21 review: `5097117641` — `PASS / ACCEPTED_FOR_DOWNSTREAM`

### Governance applicability

- P23 head: `b5677ad112a7a2067754b209ccde7fc97ef7469d`
- P23 review: `5097214759` — `PASS / AUTHORITY_SUPERSESSION_COMPLETE`

Controlling profile labels:

```text
PLUGIN_PROFILE  = required v0.2 delivery envelope
SERVICE_PROFILE = optional later service realization / claim
```

### Verification

- accepted Plugin-profile Verification head: `d6b795ce4a40a422d26f74d749cc823dd66a26df`
- P21 rereview: `5097554177` — `PASS / ACCEPTED_FOR_DOWNSTREAM`

Historical accepted P20 remains normative except where the Plugin-profile repair/amendment is more specific:

- historical P20 ref: `db83168e4086e47a7f431acf289006e4f25b8ffd`
- historical P20 review: `5062933855`

### P30 plan

- targeted P30 plan ref: `2196c2ee1038b7f48632ec9f11a9c5c4155b6108`
- active terminal slice: `CP-I09 / PLUGIN_PROFILE_QUALIFICATION_CLOSURE`

### Accepted implementation predecessor

- CP-I08 result: `ac2bcf19acf46a749761ed455ecf0a995069700d`
- CP-I08 P34 review: `5079977191` — `PASS / ACCEPTED_FOR_DOWNSTREAM`

### Published Plugin baseline to inherit

- current main: `38bf619ede0615431c7517bc0e07984136af28cf`
- published baseline: `v0.1.0-beta.3`

The beta.3 baseline contains the exact-nine Plugin materialization and accepted Codex execution-prefix/handoff behavior that the v0.2 qualification candidate must preserve.

---

## 3. Task anchor and execution-position contract

Repository-backed execution MUST use:

```yaml
task_anchor:
  revision: ac2bcf19acf46a749761ed455ecf0a995069700d
  relation: ancestor
resume_cursor: null
```

`Task Anchor != Execution Cursor`.

At initial P32 start there is no accepted continuation point for this replacement package, therefore `resume_cursor: null` is correct.

The executor must record the actual starting revision before edits.

The preferred execution branch is a new child branch from the task anchor, for example:

```text
chatgpt/control-plane-cp-i09-plugin-profile-implementation-v0.2
```

Do not reuse PR #44's implementation branch as the active P32 branch.

A valid descendant of the task anchor is acceptable if fresh P32 state inspection proves it contains only authorized/reconciled work. Historical HEAD equality is not the execution oracle.

---

## 4. Required exact baseline convergence

Before PP0 evidence can become final-candidate evidence, the execution candidate MUST contain both trusted histories as ancestors:

```text
ac2bcf19acf46a749761ed455ecf0a995069700d  # accepted CP-I08 implementation
38bf619ede0615431c7517bc0e07984136af28cf  # current published Plugin main
```

Preferred topology:

```text
start from CP-I08 accepted branch
        +
ancestry-preserving merge of main@38bf619
        =
one exact qualification candidate
```

The executor must verify both ancestor relationships after convergence.

### Merge conflict policy

Mechanical conflict resolution is authorized only when it preserves both:

1. accepted CP-I08 semantic/control implementation behavior;
2. accepted beta.3 Plugin/handoff/execution-prefix behavior.

If a conflict requires any of the following, stop and fail closed:

- redefining Product/Model/Architecture/Verification semantics;
- choosing a new lifecycle owner;
- changing P34 Gate ownership;
- weakening exact refs, CAS, idempotency, commit-before-dispatch, replay/currentness, or immutable history;
- editing Skill semantics beyond the already-published beta.3 delta;
- changing rollout policy;
- reactivating `SERVICE_PROFILE` claims.

Return `BLOCKED_AUTHORITY` or `BLOCKED_EXECUTION_DIVERGENCE` as applicable.

### Required convergence evidence

Record:

```text
actual_starting_revision
merge parents / ancestor proof
exact main ref incorporated
conflict file list
conflict-resolution classification
post-merge exact revision
```

No historical evidence may be rewritten during convergence.

---

## 5. Package objective

At one exact qualification candidate, produce reviewer-recomputable evidence that:

1. accepted CP-I01..CP-I08 semantic/control evidence remains applicable;
2. current regression still satisfies G01-G44 and M01-M20;
3. PP0 exact 40-WorkScope correctness-under-repetition passes with every zero-tolerance metric at zero;
4. the same exact candidate preserves the actual Plugin / nine-Skill product form;
5. sessionless resume, execution-surface handoff, exact Codex execution prefix, Gate ownership, and rollout denial remain intact;
6. the final evidence bundle is reviewer-accessible and digest-bound;
7. no service throughput/latency/economics/availability claim is inferred.

New production semantics are not expected.

---

## 6. Authorized scope

### 6.1 Expected new qualification/evidence surfaces

The executor MAY create/modify the following narrow surfaces:

```text
.github/workflows/control-plane-cp-i09-plugin-profile.yml

tests/control_plane/cp_i09_plugin_profile.py
tests/control_plane/generate_cp_i09_plugin_profile_evidence.py
tests/control_plane/test_cp_i09_plugin_profile*.py

tests/skillset/test_control_plane_plugin_profile*.py
skillset/dogfood/control-plane-v0.2-plugin-profile*.json
```

Equivalent narrowly named files under the same test/evidence ownership are allowed if the executor records the exact mapping in `engineering-handoff.json`.

### 6.2 Existing surfaces to reuse

Prefer reuse of accepted CP-I08/reference assets, including where applicable:

```text
tests/control_plane/cp_i08_d0.py
tests/control_plane/generate_cp_i08_evidence.py
tests/control_plane/catalogs.py
tests/control_plane/qualification.py
tests/control_plane/reference_model.py
tests/control_plane/completeness_oracle.py
tests/control_plane/store_oracle.py
tests/control_plane/verifier_helpers.py

tools/aegis_control/**

tests/skillset/test_openai_plugin_materialization.py
existing execution-surface / routing / installed-platform regression tooling
```

Do not duplicate G01-G44 or M01-M20 into a second competing corpus when the accepted one can be invoked directly.

### 6.3 Bounded production repair permission

Small changes under:

```text
tools/aegis_control/**
```

are authorized only when all are true:

1. PP0/current regression exposes a concrete implementation defect;
2. the defect is inside an already accepted semantic contract;
3. RED evidence exists before the fix;
4. the smallest repair is used;
5. the repair does not change upstream Authority or Product scope;
6. full affected regression is rerun after repair.

If the defect requires a new semantic decision, stop rather than patching it inside P32.

---

## 7. Explicit non-goals / prohibited scope

This package does NOT authorize new semantic edits to:

```text
skills/**
plugins/aegis/skills/**
.aegis/**
Product Authority documents
Modeling Authority documents
Architecture / P17 / P18 Authority documents
Verification Authority documents
```

The exact beta.3 merge may introduce its already-published changes to Skill/materialization files; that is baseline convergence, not new package-authored Skill semantics.

Also prohibited:

- new daemon or standalone Control Service;
- new public `/v1` service API solely for qualification;
- new worker/process topology;
- R0 service benchmark work;
- S0 real-wall-clock 4x service stress work;
- W7D service-cost qualification;
- completed-month availability work;
- reopening PR #44 P36;
- rewriting old R0/S0 FAIL evidence;
- version bump / GitHub Release publication;
- rollout expansion;
- merge to main;
- P34 Gate verdict generation inside CI/harness.

---

## 8. Evidence inheritance contract

CP-I01..CP-I08 are `RETAIN / DO NOT RERUN BY DEFAULT`, not `TRUST WITHOUT RESOLUTION`.

The executor must materialize an explicit inherited-evidence table inside `evidence-manifest.json`.

For each inherited evidence family record at least:

```yaml
claim_id: <CPV-Cxx>
evidence_ref: <immutable reviewer-resolvable ref>
source_result_revision: <exact revision>
source_gate_review: <review/ref where applicable>
applicability: APPLICABLE | REQUALIFIED | BLOCKED
lineage_basis: <ancestor/equivalence/current-regression explanation>
current_regression: PASS | FAIL | NOT_APPLICABLE
```

At minimum resolve:

- CP-I08 result `ac2bcf...`;
- CP-I08 P34 `5079977191`;
- G01-G44 corpus/evidence;
- M01-M20 qualification evidence;
- O-CRM independence;
- O-COMPLETE independence;
- P33 four-outcome evidence;
- G44 / retention-alert deterministic policy evidence;
- exact evidence/materialization provenance.

An unresolved required evidence ref is a hard `BLOCKED_EVIDENCE` result.

---

## 9. Required current regression before PP0 acceptance

At the converged exact candidate, run at minimum:

```text
G01-G44 mandatory scenarios: PASS
semantic mismatches vs independent oracle stack: 0
zero-tolerance invariant events: 0
M01-M20 mandatory mutant detection: 20/20
M01-M20 false acceptance: 0
Control Plane regression suite: PASS
Project State regression suite: PASS
Skillset / Plugin materialization regression: PASS
```

The executor must use the repository's actual accepted regression commands/workflows after inspecting current files; do not invent a weaker subset if existing workflows cover the required contract.

If a current regression contradicts an inherited result, that inherited claim is no longer silently accepted.

---

## 10. PP0 fixed workload contract

PP0 contains exactly 40 deterministic WorkScopes:

```text
Cohort A — clean lifecycle / routing / materialization                  8
Cohort B — duplicate delivery / callback loss / reconciliation          8
Cohort C — P33 resume and execution-position reconciliation              8
Cohort D — repair / rereview / escalation / REQUIRED-child boundaries    8
Cohort E — snapshot/currentness/capability/size/rate-limit policy         8
                                                                      ----
Total WorkScopes                                                         40
```

The workload manifest MUST bind:

- exact qualification candidate revision;
- package ID/ref;
- P20/P23 exact refs;
- exact 40 WorkScope IDs;
- cohort membership;
- deterministic seeds;
- fault schedule;
- expected final state;
- logical interleaving plan;
- relevant runtime/tool versions.

### Cohort A required behavior

Across eight scopes challenge:

- deterministic next-owner derivation;
- legal lifecycle progression;
- exact materialization refs;
- commit-before-dispatch observation;
- package/task binding where implementation work exists;
- no conversation-only durable truth;
- P34 externally owned outcome.

Rollout remains denied; the harness must not convert this into unauthorized zero-user-turn cross-Primary execution.

### Cohort B required behavior

Inject deterministic combinations of:

- duplicate delivery;
- callback loss;
- duplicate callback;
- callback reordering;
- delayed provider materialization;
- transport retry;
- provider query recovery.

Expected:

- one semantic occurrence per substantive attempt;
- callback never becomes canonical truth by itself;
- query/refetch recovers current provider truth where supported;
- transport uncertainty never invents replacement semantic attempts.

### Cohort C required behavior

Exactly cover each accepted P33 outcome twice:

```text
EXACT_CURSOR                         x2
DESCENDANT_CURSOR                    x2
ANCHOR_DESCENDANT_WITHOUT_CURSOR     x2
DIVERGED                             x2
```

Expected:

- valid descendant work preserved;
- completed work not replayed;
- accepted cursor established only under the contract;
- true divergence fails closed;
- task anchor never treated as cursor equality.

### Cohort D required behavior

Challenge a deterministic mix of:

- bounded P35/P36 repair lineage;
- reverify vs rereview occurrence identity;
- repair budget exhaustion;
- exact HumanDecision ref;
- REQUIRED-child acceptance barrier;
- exact historical child acceptance binding;
- terminalization/successor separation.

Expected:

- no semantic attempt collapse;
- no historical rewrite;
- no barrier crossing without exact accepted child facts;
- exhausted repair fails closed.

### Cohort E required behavior

Challenge a deterministic mix of:

- valid/tampered SourceSnapshotToken;
- wrong adapter/source binding;
- wrong provider resource/version binding;
- callback-only provider capability claim;
- provider currentness change before commit;
- canonical envelope around size/truncation boundaries;
- rate-limit policy transition;
- virtual-time retention/alert boundary behavior.

Expected:

- tampered/stale/cross-boundary truth fails closed;
- no silent canonical truncation;
- operational policy/timers do not create semantic truth;
- no service-throughput claim inferred from correctness.

---

## 11. PP0 concurrency/interleaving contract

Mandatory:

```text
maximum simultaneously active PP0 WorkScopes: 8
unrelated-lane interleavings: >= 8
deliberate same-lane CAS probes: >= 4
legal canonical winner for each same-lane race: exactly 1
```

Unrelated scopes must not acquire false shared semantic serialization.

Runtime duration is diagnostic only.

PP0 PASS MUST NOT depend on:

```text
requests per second
mutations per second
projection evaluations per second
provider events per second
latency p50/p95/p99
minimum wall-clock stress duration
service capacity
10,000 active WorkScopes
100 clients
4x R0
7-day cost ratio
completed-month availability
24x7 residency
```

---

## 12. PP0 oracle stack

Mandatory independent oracle/reference surfaces:

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
O-CONTRACT network checks
  only if the exact candidate exposes the corresponding physical Aegis-owned network boundary

O-PERF
  not required for PP0 PASS
```

Production implementation must not be its own only oracle.

---

## 13. Harness qualification / RED-first tests

Before accepting PP0 execution evidence, tests must prove the new harness fails closed for at least:

1. total WorkScope count != 40;
2. any cohort count != 8;
3. duplicate WorkScope identity;
4. missing/mutable seed or fault schedule;
5. incomplete four-state P33 coverage;
6. fewer than eight unrelated-lane interleavings;
7. fewer than four deliberate same-lane CAS probes;
8. same-lane race with zero or multiple legal winners;
9. unexpected OPEN occurrence at end;
10. unexpected ready outbox at end;
11. unexpected unresolved delivery at end;
12. nonzero semantic mismatch;
13. unauthorized canonical mutation;
14. duplicate semantic occurrence from transport;
15. dispatch-before-commit violation;
16. stale/ambiguous snapshot accepted;
17. invalid snapshot token accepted;
18. wrong P33 classification;
19. completed work replayed on resume;
20. REQUIRED-child barrier violation;
21. repair budget overrun;
22. unofficial Gate decision;
23. historical evidence rewrite;
24. silent canonical truncation;
25. unresolved required evidence ref;
26. G01-G44 incomplete/failing;
27. M01-M20 != 20/20 or false acceptance != 0;
28. platform evidence bound to another candidate;
29. Plugin catalog not exact-nine;
30. rollout not `DENIED`;
31. attempted PP0 PASS from RPS/latency/service metrics;
32. attempted old CP-I09 R0/S0 substitution.

Hosted RED is preferred before implementation of a new harness check when the repository workflow can expose it without excessive cost. Do not intentionally run historical long R0/S0 jobs to satisfy RED-first discipline.

---

## 14. PP0 PASS thresholds

Every following metric must equal zero:

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

Also mandatory:

```text
G01_G44 = PASS
M01_M20_detected = 20/20
M01_M20_false_acceptance = 0
current_cross_primary_rollout = DENIED
```

The final canonical record/revision/lineage set must equal the independent expected set exactly.

A fixture explicitly expected to end in a governed blocked/escalated/delivery-uncertain state is not counted as unexpected residue, but its expected state must be immutable in the workload manifest.

---

## 15. Fresh Plugin / nine-Skill product-form corroboration

The exact same qualification candidate used for PP0 must produce reviewer-resolvable corroboration for all of the following:

### PFC-01 exact Plugin materialization

- one native Aegis Plugin;
- exactly nine Skills;
- Plugin trees equal canonical Skill trees;
- no hidden tenth lifecycle owner.

### PFC-02 router ownership

A routing-only request is owned by central `aegis` and routes to the expected specialist family without performing that specialist's substantive stage.

### PFC-03 specialist ownership

At least one available specialist owns a substantive result in its declared stage family; central router/supporting Project State does not steal ownership.

### PFC-04 execution-surface handoff

At least one repository-backed implementation handoff preserves:

```text
package_ref
task_anchor
resume_cursor semantics
materialized_ref return obligation
stage_owner = aegis-implementation
```

### PFC-05 exact Codex execution prefix

Whenever `preferred_executor: codex` is rendered, the exact accepted instruction is immediately before the YAML envelope:

> 请按以下 Aegis handoff 直接执行：以 `package_ref` 为任务授权，按 `task_anchor/resume_cursor` 核对当前状态并从首个未完成步骤继续；若状态冲突则 fail closed。

### PFC-06 sessionless/resume durability

Produce a fresh observation that continuation/resume is derived from durable exact refs/state rather than solely from one conversation transcript.

### PFC-07 Gate ownership

No Plugin/Control Plane/CI/ProofEvaluation result emits or implies official P34 PASS. P34 remains externally owned by `aegis-gate-review`.

### PFC-08 rollout denial

Current cross-Primary rollout remains:

```text
DENIED
```

Capability to transport a handoff is not interpreted as permission for zero-user-turn cross-Primary substantive chaining.

### Evidence admissibility

Repository deterministic tests are necessary but not sufficient for fresh installed-platform corroboration.

`pp0-platform-corroboration.json` must contain reviewer-resolvable evidence refs or captures, candidate identity, observed specialist/router ownership, exact handoff metadata where applicable, and an explicit no-service-profile-claim statement.

Historical beta.3 install evidence may be supporting provenance but is not final-candidate corroboration by itself.

If the platform cannot bind the evidence to the exact qualification candidate, return `BLOCKED_EVIDENCE`.

---

## 16. Required EvidenceArtifacts

The final reviewer-accessible bundle must include at least:

```text
pp0-workload-manifest.json
pp0-trace-corpus.json
pp0-conformance.json
pp0-platform-corroboration.json
engineering-handoff.json
evidence-manifest.json
```

### `pp0-workload-manifest.json`

Must bind:

- exact result revision;
- exact package ref;
- exact P20 Plugin-profile ref;
- exact P23 ref;
- CP-I08 predecessor ref/P34;
- current main ref converged;
- 40 WorkScope identities;
- cohorts;
- seeds/fault schedule;
- interleaving plan;
- runtime/tool versions.

### `pp0-trace-corpus.json`

Must preserve enough immutable trace state to independently inspect/replay:

- occurrence lineage;
- lane/CAS results;
- idempotency results;
- outbox/dispatch/reconciliation relations;
- provider/snapshot observations;
- repair/escalation/child-barrier transitions;
- P33 outcomes;
- expected vs actual canonical record identity.

### `pp0-conformance.json`

Must contain:

- all PP0 zero-tolerance metrics;
- G01-G44 current status;
- M01-M20 current status;
- independent oracle results;
- exact convergence state;
- final PASS/BLOCKED evaluation for PP0 only.

It must not issue P34 PASS.

### `pp0-platform-corroboration.json`

Must contain PFC-01 through PFC-08, exact candidate identity, evidence refs/captures, reviewer-resolvability, and explicit profile-claim boundaries.

### `engineering-handoff.json`

Must identify:

- exact result revision;
- actual starting revision;
- package ID/ref;
- task anchor;
- merge/convergence facts;
- completed work;
- inherited evidence refs;
- new PP0 evidence refs;
- platform corroboration refs;
- tests/workflows executed;
- unresolved findings/blockers;
- `p34_gate_pass: false`.

### `evidence-manifest.json`

Every entry must classify as one of:

```text
INHERITED_EVIDENCE
NEW_PP0_EVIDENCE
NEW_PLATFORM_CORROBORATION
CHARACTERIZATION_ONLY
HISTORICAL_ONLY
```

Old CP-I09 R0/S0/W7D evidence may only be `HISTORICAL_ONLY`.

---

## 17. Performance / engineering constraints

No release-blocking service performance threshold exists in this package.

Allowed diagnostic-only measurements:

- total test/runtime duration;
- CPU/RSS;
- artifact size;
- local queue depth;
- conflict count;
- number of interleavings executed.

Do not optimize production code solely to improve diagnostic timing.

No benchmark may claim:

- service capacity;
- latency SLA/SLO;
- 4x stress resilience;
- W7D cost target;
- monthly availability;
- 24x7 agent residency.

---

## 18. Required hosted workflow topology

Prefer one focused workflow with bounded jobs such as:

```text
contract-regression
baseline-and-inheritance-check
pp0-deterministic-qualification
skillset-plugin-regression
combine-evidence
```

Fresh installed-platform corroboration may be a separate durable evidence step because it may require an actual product surface rather than repository CI.

The final combine/evidence materialization must not mark the package P34 PASS. It may only state whether the P32/P33 evidence package is internally complete for review.

Do not add R0/S0/W7D long-running jobs to the replacement workflow.

---

## 19. Exact exit criteria

Return `READY_FOR_P34_REVIEW` only when all are true at one exact candidate:

1. task anchor `ac2bcf...` is an ancestor;
2. main `38bf619...` is an ancestor;
3. convergence has no unresolved semantic conflict;
4. inherited evidence refs are exact/resolvable/applicable;
5. G01-G44 current regression PASS;
6. M01-M20 current qualification 20/20 and false acceptance 0;
7. PP0 exact 40 WorkScopes executed;
8. all five cohorts complete 8/8;
9. unrelated interleavings >=8;
10. same-lane CAS probes >=4 with one winner each;
11. every PP0 zero-tolerance metric = 0;
12. expected canonical record/revision set equals actual exactly;
13. PFC-01..PFC-08 complete against the same candidate;
14. exact-nine Plugin materialization passes;
15. exact Codex execution-prefix behavior is corroborated;
16. sessionless/resume corroboration is reviewer-resolvable;
17. P34 sole-Gate ownership preserved;
18. rollout remains `DENIED`;
19. old CP-I09 remains historical-only;
20. no R0/S0/W7D/monthly service claim is made;
21. final evidence bundle is digest-bound and reviewer-accessible;
22. return includes `materialized_ref`.

If fresh platform corroboration remains incomplete after repository PP0 passes, return:

```text
READY_FOR_PLATFORM_CORROBORATION
```

not P34-ready.

---

## 20. Blocked return behavior

### Authority / semantic conflict

```yaml
status: BLOCKED_AUTHORITY
```

Use when accepted sources conflict or implementation requires a new semantic decision.

### Execution divergence

```yaml
status: BLOCKED_EXECUTION_DIVERGENCE
```

Use when task-anchor ancestry cannot be established or trusted histories cannot be converged without incompatible rewrite.

### Evidence gap

```yaml
status: BLOCKED_EVIDENCE
```

Use for unresolved immutable refs, unbindable exact-candidate platform evidence, missing artifact materialization, or incomplete mandatory proof.

### Implementation defect

```yaml
status: BLOCKED_IMPLEMENTATION
```

Use when PP0/current regression exposes a defect outside the narrow authorized repair scope or after an authorized repair still fails.

### Environment blocker

```yaml
status: BLOCKED_ENVIRONMENT
```

Use when the required real platform or hosted evidence surface cannot execute and no equivalent Authority-approved proof exists.

Never weaken a threshold or reinterpret an old result to escape a blocker.

---

## 21. Final manifest minimum fields

```yaml
package_id: CP-I09-P31-02
package_ref: <exact package commit/ref>
result_revision: <exact qualification result>

task_anchor:
  revision: ac2bcf19acf46a749761ed455ecf0a995069700d
  relation: ancestor

published_plugin_baseline:
  revision: 38bf619ede0615431c7517bc0e07984136af28cf
  required_as_ancestor: true

source_cp_i08_p34_review: 5079977191
verification_ref: d6b795ce4a40a422d26f74d749cc823dd66a26df
verification_review: 5097554177
p30_ref: 2196c2ee1038b7f48632ec9f11a9c5c4155b6108

pp0:
  workscopes: 40
  cohort_a: 8
  cohort_b: 8
  cohort_c: 8
  cohort_d: 8
  cohort_e: 8
  unrelated_lane_interleavings_min: 8
  same_lane_cas_probes_min: 4
  zero_tolerance_metrics_all_zero: <bool>
  canonical_expected_equals_actual: <bool>

regression:
  g01_g44: <PASS|FAIL>
  m01_m20_detected: <0-20>/20
  m01_m20_false_acceptance: <int>
  control_plane: <PASS|FAIL>
  project_state: <PASS|FAIL>
  skillset_plugin: <PASS|FAIL>

platform_corroboration:
  pfc01_exact_plugin: <PASS|FAIL|BLOCKED>
  pfc02_router_ownership: <PASS|FAIL|BLOCKED>
  pfc03_specialist_ownership: <PASS|FAIL|BLOCKED>
  pfc04_surface_handoff: <PASS|FAIL|BLOCKED>
  pfc05_codex_prefix: <PASS|FAIL|BLOCKED>
  pfc06_sessionless_resume: <PASS|FAIL|BLOCKED>
  pfc07_gate_ownership: <PASS|FAIL|BLOCKED>
  pfc08_rollout_denied: <PASS|FAIL|BLOCKED>

claims:
  service_profile: NOT_CLAIMED
  r0_service_attainment: NOT_CLAIMED
  s0_service_attainment: NOT_CLAIMED
  w7d_service_economics: NOT_CLAIMED
  monthly_availability: NOT_CLAIMED
  current_cross_primary_rollout: DENIED
  p34_gate_pass: false

old_cp_i09:
  disposition: HISTORICAL_ONLY
  r0: FAIL
  s0: FAIL
  w7d: PASS
```

---

## 22. P31 approval boundary

This package authorizes P32 repository-heavy execution only after the exact package ref is materialized.

P32 must not edit this package to expand its own scope.

The executor must inspect repository state before modification and report:

1. actual starting revision;
2. task-anchor ancestry status;
3. whether an existing valid descendant contains authorized work;
4. whether main `38bf619...` is already an ancestor;
5. completed vs pending work if any;
6. first authorized incomplete action.

Before returning any P32/P33 completion to review, the exact result must be pushed/materialized at a reviewer-accessible durable ref and returned as `materialized_ref`.

Local-only commits/test transcripts are insufficient.

---

## 23. Surface handoff contract

请按以下 Aegis handoff 直接执行：以 `package_ref` 为任务授权，按 `task_anchor/resume_cursor` 核对当前状态并从首个未完成步骤继续；若状态冲突则 fail closed。

```yaml
type: surface_handoff
stage: P32
stage_owner: aegis-implementation
from_surface: CONTROL_REASONING
to_surface: CODE_EXECUTION
preferred_executor: codex
reason: repository_heavy_plugin_profile_qualification
package_ref: <exact CP-I09-P31-02 package ref>
task_anchor:
  revision: ac2bcf19acf46a749761ed455ecf0a995069700d
  relation: ancestor
resume_cursor: null
return_surface: CONTROL_REVIEW
```

This surface handoff does not transfer Primary ownership, change Authority, create Evidence, issue a Gate verdict, or mutate Project State merely by occurring.

---

## 24. P31 disposition

```yaml
P31_return:
  task_id: CP-I09
  package_id: CP-I09-P31-02
  purpose: PLUGIN_PROFILE_QUALIFICATION_CLOSURE

  authority:
    product: e6f79e92d60b1fea126db4efec321fd5ddc1ada7
    p23: b5677ad112a7a2067754b209ccde7fc97ef7469d
    verification: d6b795ce4a40a422d26f74d749cc823dd66a26df
    verification_review: 5097554177
    p30: 2196c2ee1038b7f48632ec9f11a9c5c4155b6108

  task_anchor:
    revision: ac2bcf19acf46a749761ed455ecf0a995069700d
    relation: ancestor
  resume_cursor: null

  required_convergence_ancestor:
    revision: 38bf619ede0615431c7517bc0e07984136af28cf

  phases:
    - baseline_convergence
    - inherited_evidence_resolution
    - PP0_40_workscope_qualification
    - fresh_plugin_product_form_corroboration
    - final_evidence_materialization

  old_cp_i09: HISTORICAL_ONLY
  pr44_resume: false
  service_profile: NOT_AUTHORIZED
  rollout: DENIED

  status: P31_READY_MATERIALIZED
  next_stage: P32_IMPLEMENTATION
  preferred_executor: codex
```

Stop after P31 materialization. Do not begin P32, merge, release, P34, resume PR #44, or expand rollout automatically.