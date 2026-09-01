# Aegis Control Plane Productization v0.2 — CP-I06 P31 Task Package

Status: **P31 READY / MATERIALIZED — authorized package for later P32 execution**

Package ID: `CP-I06-P31-01`

Owner: `aegis-implementation`

Stage: `P31 Task Packaging`

Target execution stage: `P32 Implementation`

Execution surface: `CONTROL_REASONING`

Preferred later execution surface: `CODE_EXECUTION`

This package defines only:

`CP-I06 — Repair, Reverification, Rereview, Escalation, Human Decision, Degraded Recovery`

It does not start implementation, issue Evidence, produce a Gate verdict, merge CP-I05, expand Current rollout authorization, or start CP-I07+.

---

## 1. Repository execution anchor

Repository:

`Mostorm-Labs/aegis`

Accepted predecessor:

```yaml
task_anchor:
  revision: 7b3244417c5beba4c75d5eafd471083007fa1843
  relation: ancestor
resume_cursor: null
```

`Task Anchor != Execution Cursor`.

The anchor is the exact CP-I05 revision accepted by the fresh P34 Gate re-review. It is an ancestry trust baseline, not a requirement that a later P32 HEAD remain equal to this historical revision.

P32 must record its actual starting revision before edits. The start is legal only when:

1. `7b3244417c5beba4c75d5eafd471083007fa1843` is an ancestor of the starting revision; and
2. the exact package ref materializing this P31 document is also present in that ancestry.

If either relationship cannot be established, return `BLOCKED_EXECUTION_DIVERGENCE` rather than rebasing, force-moving, or inventing a new baseline.

---

## 2. Accepted predecessor boundary

CP-I05:

```yaml
revision: 7b3244417c5beba4c75d5eafd471083007fa1843
status: PASS / MATERIALIZED / ACCEPTED_FOR_DOWNSTREAM
p34_comment: 5490992992
p36_return_comment: 5490883002
evidence_artifact_id: 9790980577
current_cross_primary_rollout: DENIED
repository_integration: NOT_PERFORMED
```

CP-I06 consumes and must preserve every accepted CP-I01 through CP-I05 invariant, including:

- the independent oracle / evidence boundary established by CP-I01;
- one canonical writer through `control-mutation`;
- immutable record revisions, exact refs, lane CAS, semantic idempotency, and transactional outbox;
- deterministic/read-only projection and transient scheduler candidates;
- external Authority/Gate/Proof/Integration/execution truth remaining externally owned;
- `SourceSnapshotToken` integrity/currentness and historical exact-ref behavior;
- REQUIRED-child acceptance/barrier semantics;
- dispatch only after committed OPEN occurrence + outbox;
- at-least-once transport without semantic occurrence amplification;
- exact Current dispatch authorization resolved from trust facts rather than caller assertion;
- exact reviewer-resolvable RESULT materialization before review-ready completion;
- provider acknowledgement not being semantic completion;
- callback-loss/query reconciliation and durable provider correlation;
- P33 `EXACT_CURSOR`, `DESCENDANT_CURSOR`, `ANCHOR_DESCENDANT_WITHOUT_CURSOR`, and `DIVERGED` semantics;
- `Task Anchor != Execution Cursor`;
- age/transport uncertainty not being semantic failure;
- Current cross-Primary automatic rollout remaining `DENIED` until separately governed.

CP-I06 may extend the accepted runtime only with the bounded repair/escalation/degraded-recovery semantics already frozen by Current Authority. It must not reinterpret predecessor truth.

---

## 3. Current Authority refs

### 3.1 Product

```text
c628bdc15fdd3d32511a04b6f09055413f2786c3
review: 5061188138
PASS / ACCEPTED_FOR_DOWNSTREAM
```

### 3.2 Modeling

```text
f29c4da3698038e0174e4380707fa618b03c40b2
review: 5062616510
PASS / ACCEPTED_FOR_DOWNSTREAM
```

Normative modeling package includes:

```text
docs/control-plane-productization-model-v0.2.md
docs/control-plane-productization-schema-v0.2.md
docs/control-plane-productization-operations-v0.2.md
docs/control-plane-productization-model-v0.2-p21-repair.md
docs/control-plane-productization-model-v0.2-p21-b3-repair.md
```

### 3.3 Architecture / engineering

```text
e657f0e74771184b98f8c8e6f8a8581e4858c82d
review: 5062769390
PASS / ACCEPTED_FOR_DOWNSTREAM
```

Relevant contracts:

```text
docs/control-plane-productization-modules-v0.2.md
docs/control-plane-productization-runtime-flow-v0.2.md
docs/control-plane-productization-platform-contract-v0.2.md
docs/control-plane-productization-engineering-v0.2.md
```

### 3.4 Verification

```text
db83168e4086e47a7f431acf289006e4f25b8ffd
review: 5062933855
PASS / ACCEPTED_FOR_DOWNSTREAM
```

Normative verification package:

```text
docs/control-plane-productization-verification-v0.2.md
docs/control-plane-productization-verification-v0.2-p21-repair.md
```

### 3.5 Implementation plan

```text
87cbb166411795261ec5f6e7034a89435e053451
```

P30 defines CP-I06 as:

```text
Repair + escalation + degraded recovery
```

Applicable proof claims / requirements for this slice include at minimum:

```text
CPV-C06 — Human Decision Integrity
CPV-C08 — Derived / Operational State Separation, for pause/backpressure behavior
CPV-C09 — Degraded Recovery / Durability
CPV-C16 — operational provider-rate-limit portion

CPV-R10
CPV-R18
CPV-R21
CPV-R22
CPV-R23
CPV-R27
CPV-R35
```

CP-I06 does not claim the later CP-I07 API/capability profile, CP-I08 integrated D0 closure, CP-I09 R0/S0/7-day performance profile, or post-launch monthly availability.

---

## 4. Objective

Make failure handling evidence-driven and bounded without turning operational uncertainty into semantic retry or allowing manual escape hatches to duplicate already-controlled work.

The intended semantic loop is:

```text
exact finding / blocker / degraded observation
  |
  v
re-read canonical + exact external truth
  |
  v
projection + repair / recovery policy
  |
  +---------------------------+
  |                           |
  | repairable                | decision required / unsafe / exhausted
  v                           v
new REPAIR occurrence       immutable Escalation
  |                           |
  v                           v
exact repaired result       exact durable HumanDecision / owned resolution
  |                           |
  +-------------+-------------+
                |
       reverify if required
                |
       fresh exact Evidence/Proof
                |
       rereview if required
                |
       fresh independent P34 decision
                |
              recompute
```

Operational recovery remains a separate concern:

```text
process restart / timeout / store restart / provider throttling / pause / backlog
  -> reconcile existing durable truth
  -> alter timing/admission only where appropriate
  -> submit a normal P13 operation only when a governed semantic transition is actually required
```

Core rule:

> **Infrastructure recovery != semantic retry.**

---

## 5. Authorized implementation scope

### 5.1 Promote the CP-I06 P13 mutation subset

The existing single `MutationService` remains the only canonical writer.

CP-I06 may promote the following already-accepted P13 operations from the current later-operation set into the implemented subset:

```text
RECORD_ESCALATION_RESOLUTION
SCHEDULE_REPAIR_OCCURRENCE
SCHEDULE_REVERIFICATION_OCCURRENCE
SCHEDULE_REREVIEW_OCCURRENCE
```

`RAISE_ESCALATION` already exists in the predecessor runtime and may be extended or hardened only as required to satisfy the accepted CP-I06 contracts.

`RECOMPUTE_CONTROL_PROJECTION` remains noncanonical derivation. CP-I06 may invoke or expose the accepted projection/recompute capability through existing internal boundaries, but it must not turn projection into a second durable semantic write.

All CP-I06 operations must preserve:

- exact operation request shape;
- semantic idempotency;
- exact expected-state guards;
- lane/work-scope ownership;
- existing package/scope boundaries;
- all-or-none canonical transaction semantics;
- zero canonical residue on rejection.

No generic mutation API may be introduced.

### 5.2 Bounded repair lineage and attempt budget

Implement the exact P12/P13 `RepairContext` contract:

```yaml
repair_context:
  finding_ref: <exact FINDING ref>
  root_occurrence_ref: <exact STAGE_OCCURRENCE ref>
  previous_attempt_occurrence_ref: null | <exact immediately previous repair occurrence>
  attempt_ordinal: <integer >= 1>
  repair_policy_digest: <exact PolicyBinding.policy_digest>
```

Required behavior:

- first repair attempt is ordinal `1` with no previous attempt;
- every later repair points to exactly one immediately previous repair occurrence;
- ordinals are contiguous;
- one lineage keeps the same exact root finding identity;
- `attempt_ordinal <= repair_policy.max_attempts`;
- remaining budget is derived from canonical repair occurrences, never stored as a mutable semantic counter;
- the exact repair class must be present in `repair_policy.allowed_classes`;
- the repair policy digest must match the policy governing the occurrence;
- repair scope must remain within the already-authorized semantic scope;
- repair scheduling still obeys normal lane/CAS and Current autonomy/rollout rules;
- a repair is a new StageOccurrence with its own correct Primary owner.

The following must prohibit automatic repair and fail closed or route to escalation / the earliest valid upstream layer:

- Authority/product/semantic redesign;
- scope expansion;
- wrong or ambiguous finding classification;
- destructive/irreversible action not already authorized;
- exhausted attempt budget;
- missing/ambiguous policy truth;
- a materially different root finding masquerading as the same lineage.

P35 classification does not itself grant P36 implementation authority. CP-I06 only materializes the orchestration semantics needed to represent governed repair attempts.

### 5.3 Reverification as a separate occurrence

Implement `SCHEDULE_REVERIFICATION_OCCURRENCE` as a specialized new-occurrence schedule with:

```text
reason_code = REVERIFY
new StageOccurrence ID
separately owned stage
exact repaired result/package/evidence refs as inputs
```

Required behavior:

- prior EvidenceArtifact / ProofEvaluation history is immutable;
- fresh reverification creates fresh externally owned proof/evidence truth;
- a policy-required reverification cannot be skipped because local repair tests pass;
- schedule only when exact repaired result/input refs exist;
- current autonomy/rollout restrictions remain binding;
- cross-Primary automatic scheduling capability may be implemented/tested under an explicit non-Current fixture, but Current behavior must remain denied where Current Authority denies it.

### 5.4 Rereview as a separate occurrence

Implement `SCHEDULE_REREVIEW_OCCURRENCE` as a fresh independently owned review occurrence.

Required behavior:

- prior Gate Decisions are immutable and never edited in place;
- P34 remains the sole official Gate owner;
- the new review consumes exact repaired result/evidence plus exact historical basis;
- `REVIEW_GUARDED` may authorize scheduling capability only when Current rollout/policy also permits it;
- Control Plane never emits, manufactures, or implies the review verdict;
- downstream trust cannot advance until the required fresh official Gate Decision exists.

No CI result, Evidence Compiler result, ProofEvaluation, or provider success may be used as a local substitute for P34.

### 5.5 Escalation raise and immutable lifecycle

Preserve the exact P12 Escalation object as an immutable revision-1 record.

Supported categories remain the accepted set:

```text
AUTHORITY_CONFLICT
MISSING_CONTRACT
PRODUCT_DECISION
SEMANTIC_SCOPE_EXPANSION
RISK_OR_ASSURANCE_CHANGE
IRREVERSIBLE_ACTION
ORACLE_CREDIBILITY
REPAIR_BUDGET_EXHAUSTED
ENVIRONMENT_INTERVENTION
UNRESOLVED_MATERIAL_CLASSIFICATION
```

When an OPEN occurrence raises an escalation, the semantic unit remains:

```text
create Escalation revision 1
+ append terminal StageOccurrence revision outcome=ESCALATED
+ bind raised_escalation_ids
+ semantic idempotency result
```

all-or-none.

Required behavior:

- exact raised-from occurrence binding;
- exact trusted-basis digest;
- exact evidence snapshot refs where required;
- owning layer and required decision remain the original immutable question;
- no mutable Escalation status/update field;
- projection derives open/resolved state;
- no successor is scheduled in the same transaction that raises the escalation.

### 5.6 Escalation resolution and durable HumanDecision

Implement `RECORD_ESCALATION_RESOLUTION` without mutating the original Escalation.

The resolution path must require:

- an existing unresolved Escalation;
- a separately owned resolving StageOccurrence;
- correct owning layer/stage;
- exact durable external decision/evidence when required;
- the escalation ID in the resolving occurrence terminal `resolved_escalation_ids`;
- normal current policy/rollout rules for the resolving occurrence;
- one effective resolution binding at most.

Exact replay of the same effective resolution is idempotent. A conflicting second resolution must fail closed with `ESCALATION_RESOLUTION_CONFLICT` or the exact accepted equivalent, leaving history unchanged.

For HumanDecision behavior, implement the deterministic/internal adapter capability required to prove the existing `HumanDecisionPort` contract:

```text
publish escalation view -> delivery observation only
resolve exact external_decision_ref -> DecisionSnapshot / exact trust support
```

Rules:

- publishing a prompt, UI notification, chat message, or acknowledgement is not semantic resolution;
- raw text such as `approved=true` is never a generic bypass;
- a required decision must be represented by a governed reviewer-resolvable durable exact `EXTERNAL_DECISION` ref;
- mutable/unpinned/ambiguous/stale/wrong-resource decision support fails closed;
- the decision remains externally owned;
- CP-I06 does not implement the CP-I07 public HTTP/API surface or real production human-decision vendor integration.

### 5.7 Recovery sweeps over existing durable work

Extend the existing `RecoveryCoordinator` toward the P15/P16 internal recovery contract using normal module interfaces only.

The bounded CP-I06 recovery surface may cover:

```text
reconcile_open_occurrence
reconcile_outbox
reconcile_external_truth_change
reconcile_execution_position
startup recovery sweep / deterministic equivalent
```

Recovery may:

- re-read canonical records and lane heads;
- re-resolve exact external truth;
- query/re-dispatch the same already-committed occurrence;
- request P33-compatible execution-position reconciliation;
- rebuild disposable projection;
- submit normal accepted P13 operations when a genuinely governed semantic repair/reverify/rereview/resolution is required.

Recovery may not:

- silently create a new occurrence because a process restarted;
- treat elapsed time as a finding by itself;
- force-move a repository to match stale metadata;
- mutate an old terminal record;
- rewrite a RequiredChildAcceptanceBinding;
- bypass repair budget/policy;
- create a privileged direct canonical-write path;
- create a second writer in store/recovery code.

The deterministic recovery matrix must preserve at least the P16 durable boundaries:

```text
before schedule commit
OPEN + outbox committed, before dispatch
after dispatch, before acknowledgement persistence
worker advanced, before accepted execution checkpoint
result materialized, before Control Plane accepts callback
terminal commit, before projection refresh
projection refresh, before next scheduling
successor OPEN committed, before successor dispatch
```

At every boundary, restart must recover from durable truth rather than process memory.

### 5.8 OPEN occurrence age and timeout behavior

Occurrence age remains diagnostic.

When a provider expected-runtime profile exists:

```text
warning = max(3 x provider expected p95 runtime, 15 min)
critical = max(10 x provider expected p95 runtime, 2 h)
```

Without a provider runtime profile:

```text
warning: 15 min without accepted progress/result observation
critical: 2 h without accepted progress/result observation
```

At warning:

- trigger/reinforce reconciliation;
- record operational liveness diagnostics;
- do not terminalize;
- do not allocate replacement semantic work.

At critical:

- emit operator/control diagnostics/alert state;
- continue fail-closed reconciliation;
- do not terminalize or replace merely because time elapsed.

Only the owning execution/provider contract may establish an unrecoverable substantive failure or divergence.

### 5.9 Pause / resume and admission/backpressure as operational state

Implement only the internal/deterministic operational capability required by P16/P18. Do not create a new canonical lane-status aggregate or `CANCELLED` semantic outcome.

Pause rules:

- pause affects future automatic scheduling attempts;
- existing canonical history is unchanged;
- already OPEN occurrences remain OPEN until truthfully progressed/terminated;
- already committed outbox entries remain durable and are not erased;
- resume requires fresh canonical/external re-read and recomputation;
- a stale pre-pause candidate is never replayed as authorization.

Reference capacity states:

```text
GREEN   < 70%
YELLOW  70-85%
ORANGE  85-95%
RED     >= 95%
```

Required behavior:

- GREEN: normal admission;
- YELLOW: reduce speculative/optional work before required semantic work;
- ORANGE: defer new autonomous scheduling for the saturated resource; prioritize terminalization, reconciliation, and committed outbox draining; preserve only explicitly safe reserve capacity;
- RED: stop new autonomous occurrence admission for the saturated path; continue safe reads/recovery/terminalization where possible; if necessary defer user-requested new occurrence creation rather than overcommit.

Drain priority remains:

```text
1. accepted terminalization / exact human-decision resolution
2. reconciliation of already OPEN work
3. dispatch of already committed outbox work
4. explicit user-requested new scheduling
5. new autonomous scheduling
6. optional refresh / prefetch
```

Backpressure controls **when**, never **what canonical history is true**.

### 5.10 Provider rate-limit adaptation

Complete the CP-I06 portion of the repaired CPV-C16/P18 provider policy.

For each deterministic provider/controller scope:

```text
sustained provider rate-limit responses > 5% over 5 min
```

must reduce new provider dispatch concurrency from the previously permitted level.

Reference behavior:

- halve new dispatch concurrency on each sustained threshold breach until stable/safe configured floor;
- honor explicit provider retry-after semantics where safe;
- reduce/cap redundant polling before weakening substantive implementation/proof/review behavior;
- recover concurrency gradually rather than instantly returning to full capacity;
- provider rate-limit/unavailability remains an operational/environment fact, not an implementation or Gate failure;
- existing committed semantic work is preserved;
- rate limiting never creates a replacement StageOccurrence;
- rate-limit state never becomes Authority, Proof, Gate, or canonical StageOccurrence truth.

CP-I06 may add deterministic operational state/configuration needed for this behavior. It must not implement CP-I07 real-provider credentials/network API.

### 5.11 Supported process/store restart and backup/restore proof path

Implement the smallest reference/deterministic recovery capability needed to prove the accepted CP-I06 durability contract for the currently supported store/runtime profile.

The supported primary-fault-model requirement is:

```text
RPO for acknowledged canonical commits = 0
```

The implementation/test path must prove, for the profile actually claimed:

- acknowledged canonical records survive supported process/store restart;
- immutable record bytes/digests/revision lineage remain exact;
- lane heads remain consistent with the recovered canonical history;
- semantic idempotency history required for replay is preserved;
- committed outbox intent is preserved/recoverable;
- backup/snapshot/restore does not fabricate or rewrite Gate/Evidence/Authority truth;
- post-restore external refs/currentness are re-resolved before autonomous continuation where current actionability depends on them;
- possible acknowledged-commit loss or an unreconciled history gap blocks autonomous continuation instead of being papered over.

A deterministic/local backup/restore test may prove only the supported reference-store fault model. It must not claim regional disaster recovery, production infrastructure RTO, or launch readiness that requires CP-I07/CP-I09/release evidence.

### 5.12 Unsafe manual fallback denial

Implement/verify the accepted degraded-mode rule:

> an already-controlled active WorkScope must not silently fall back to duplicate manual substantive execution.

If canonical truth shows an active OPEN occurrence or already committed dispatch intent for the same controlled semantic work, degraded handling must prefer:

```text
query / reconcile / resume / wait / explicit blocker / governed repair
```

rather than:

```text
launch duplicate uncontrolled substantive work
```

A manual/operator action may provide a governed exact decision or operational pause/resume input where the existing contracts permit it; it may not erase or bypass the active controlled history.

---

## 6. Allowed repository surfaces

P32 may add or modify only surfaces necessary to realize this bounded CP-I06 contract.

Primary production surfaces already present in the accepted predecessor:

```text
tools/aegis_control/mutation.py
tools/aegis_control/recovery.py
tools/aegis_control/policy.py
tools/aegis_control/scheduler.py
tools/aegis_control/store.py
tools/aegis_control/trust.py
tools/aegis_control/external_ports.py
tools/aegis_control/projection.py
tools/aegis_control/dispatch.py
tools/aegis_control/execution_surface.py
tools/aegis_control/__init__.py
```

The expected change concentration is:

- `mutation.py`: later P13 repair/reverify/rereview/escalation-resolution operations and exact validation;
- `policy.py`: repair/autonomy/admission decisions without semantic writes;
- `scheduler.py`: transient specialized schedule candidates only;
- `recovery.py`: recovery sweeps, liveness handling, normal-interface orchestration;
- `store.py`: narrowly scoped noncanonical operational state plus supported backup/restore test mechanics if required;
- `trust.py` / `external_ports.py`: exact HumanDecision resolution/currentness support only;
- `projection.py`: generated RepairLineage/OpenEscalations/operationally informed view only where already required by accepted P12/P15 semantics;
- `dispatch.py`: provider concurrency/rate-limit operational gate only where needed, preserving CP-I05 dispatch semantics;
- `execution_surface.py`: only deterministic provider behavior needed by CP-I06 tests; no semantic ownership expansion.

A new narrowly scoped internal module may be introduced only if the existing module boundaries would otherwise be blurred, for example for deterministic operational admission/rate-limit state. Any such module must:

- remain noncanonical;
- preserve P15 dependency direction;
- expose no second canonical-write capability;
- be covered by ownership tests.

Conditionally allowed shared surfaces:

```text
tools/aegis_control/canonical.py
tools/aegis_control/snapshot.py
```

only when needed to enforce an already-accepted exact-ref/schema/currentness rule. They may not be used to redesign P12/P13 semantics.

Test/evidence surfaces:

```text
tests/control_plane/test_cp_i06_*.py
tests/control_plane/cp_i06_*.py
tests/control_plane/generate_cp_i06_evidence.py
.github/workflows/control-plane-cp-i06.yml
```

Existing CP-I01..CP-I05 tests may be adjusted only for a necessary compatibility assertion caused by an authorized CP-I06 interface extension. Do not weaken, delete, skip, or rewrite predecessor acceptance semantics to make CP-I06 green.

Generated runtime evidence belongs in CI artifact output such as:

```text
artifacts/cp-i06/
```

and is not committed as fabricated precomputed proof.

---

## 7. Explicit non-goals

CP-I06 P32 is **not authorized** to implement:

- CP-I07 versioned public/internal HTTP API, OpenAPI, process topology, credential/capability isolation, or production provider adapters;
- real vendor credentials or production network calls;
- CP-I08 integrated D0 `G01-G44` / full verifier-qualification closure as one all-product claim;
- CP-I09 R0/S0/seven-day cost benchmarking;
- post-launch monthly availability attainment;
- regional/multi-region disaster-recovery claims;
- Current cross-Primary rollout expansion;
- a second Project State, Proof Plane, Gate, Finding, or HumanDecision authority store;
- a mutable RepairAttempt aggregate;
- a mutable Escalation status/update API;
- a generic `approved=true` override;
- a generic `set_status`, `set_gate`, `PATCH_STAGE_OCCURRENCE`, or canonical PATCH path;
- a canonical pause/backpressure/rate-limit aggregate;
- a `CANCELLED` semantic status not present in P12;
- replacement StageOccurrences created merely because of timeout, process restart, transport uncertainty, or provider throttling;
- unsafe manual duplicate execution of active controlled work;
- any P34 verdict from implementation or evidence generation;
- modification of accepted Product/Modeling/Architecture/Verification Authority to fit implementation convenience.

If implementing the bounded slice appears to require any of the above, return the appropriate blocker rather than expanding scope.

---

## 8. Hard runtime / semantic invariants

The P32 implementation must make the following mechanically testable.

1. Repair attempts are new StageOccurrences.
2. Reverify attempts are new StageOccurrences.
3. Rereview attempts are new StageOccurrences.
4. The prior occurrence/evidence/Gate Decision remains immutable.
5. Repair ordinals are contiguous and finite.
6. Repair lineage retains one root finding identity.
7. Repair policy cannot expand Authority or semantic scope.
8. Exhausted repair budget cannot silently reset.
9. Wrong/ambiguous repair class cannot auto-repair.
10. `RAISE_ESCALATION` remains atomic with the raising occurrence terminalization.
11. Escalation record is immutable revision 1.
12. Open/resolved escalation state is derived.
13. Resolution uses a separate resolving occurrence and exact durable support.
14. Raw chat/UI acknowledgement is not HumanDecision truth.
15. A conflicting second effective escalation resolution fails closed.
16. Recovery writes canonical truth only through `MutationService`.
17. Process restart alone does not create semantic retry.
18. Occurrence age alone does not create semantic retry or terminal failure.
19. Provider rate-limit state is operational only.
20. Pause/backpressure state is operational only.
21. Pause does not delete OPEN work or committed outbox intent.
22. Backpressure prioritizes already-controlled work over new autonomous admission.
23. Current cross-Primary automatic rollout remains denied.
24. Rate-limit adaptation reduces provider pressure before proof/review behavior is weakened.
25. Supported acknowledged canonical commits are not lost by supported primary fault recovery.
26. Restore never fabricates missing canonical history.
27. Unreconciled recovery gaps block autonomous continuation.
28. An active controlled WorkScope cannot silently spawn duplicate manual substantive execution.
29. P34 remains the sole official Gate owner.
30. Evidence Compiler / CI / provider success never self-asserts P34 PASS.

---

## 9. TDD and mandatory test matrix

P32 must begin with failing tests for the authorized CP-I06 behaviors before production changes that satisfy them.

A dedicated focused suite should be discoverable as:

```text
python3 -m unittest discover -s tests/control_plane -p 'test_cp_i06_*.py' -v
```

### 9.1 Repair lineage / budget cases

At minimum cover:

```text
repair_first_attempt_ordinal_1
repair_second_attempt_contiguous_and_exact_previous
repair_gap_ordinal_rejected_zero_residue
repair_duplicate_ordinal_or_lineage_conflict_rejected
repair_budget_exhausted_rejected_or_escalated_without_repair_occurrence
repair_wrong_class_rejected_zero_residue
repair_ambiguous_classification_rejected
repair_root_finding_change_rejected
repair_policy_digest_mismatch_rejected
repair_scope_expansion_rejected
repair_authority_or_semantic_defect_not_laundered_as_implementation_repair
competing_repair_candidates_exactly_one_cas_winner
```

Every rejected canonical mutation must demonstrate zero unintended canonical/outbox/idempotency residue according to the accepted atomicity contract.

### 9.2 Reverify / rereview cases

At minimum cover:

```text
required_reverification_creates_distinct_occurrence
required_reverification_exact_repaired_result_binding
required_reverification_cannot_be_skipped_by_local_test_success
rereview_creates_distinct_review_occurrence
rereview_consumes_exact_new_evidence_basis
rereview_does_not_mutate_prior_gate_decision
control_plane_cannot_issue_p34_verdict
current_cross_primary_rollout_denies_unpermitted_auto_handoff
```

A synthetic future-authorized fixture may prove architecture capability, but its evidence must be explicitly non-Current and must not be cited as Current rollout authorization.

### 9.3 Escalation / HumanDecision cases

At minimum cover:

```text
raise_escalation_atomic_with_terminal_occurrence
raise_escalation_precommit_faults_leave_zero_residue
escalation_immutable_revision_one
escalation_required_decision_does_not_self_resolve
chat_or_ui_acknowledgement_not_semantic_resolution
human_decision_missing_exact_ref_rejected
human_decision_mutable_or_unpinned_ref_rejected
human_decision_wrong_resource_or_stale_snapshot_rejected
human_decision_exact_durable_ref_accepted
escalation_resolution_uses_separate_occurrence
exact_resolution_replay_idempotent
conflicting_second_resolution_rejected
```

The HumanDecision evidence must record the exact externally modeled decision ref/currentness identity, not only a Boolean test result.

### 9.4 Recovery / fault cases

At minimum cover the accepted P16 boundaries:

```text
crash_before_schedule_commit_no_dispatch
restart_after_open_outbox_commit_dispatches_same_occurrence
restart_after_dispatch_before_ack_reuses_same_occurrence_and_correlation
restart_after_execution_progress_resolves_p33_position
callback_loss_after_materialization_resolves_same_exact_result
restart_after_terminal_before_projection_rebuilds_without_rollback
restart_after_projection_before_next_schedule_recomputes_candidate
restart_after_successor_open_before_dispatch_preserves_separate_successor
store_unavailable_creates_no_fabricated_history
warning_age_reconciles_without_terminalization
critical_age_alerts_reconciles_without_terminalization_or_replacement
```

### 9.5 Backup / restore cases

For the supported reference store profile, cover:

```text
backup_restore_preserves_exact_canonical_bytes_and_digests
backup_restore_preserves_revision_lineage
backup_restore_preserves_lane_heads
backup_restore_preserves_semantic_idempotency_replay
backup_restore_preserves_committed_outbox_intent
post_restore_current_external_truth_is_reconciled_before_auto_continuation
possible_acknowledged_commit_gap_blocks_continuation
restore_never_fabricates_missing_history
```

If the current test environment cannot credibly model a required supported fault mode, return `BLOCKED_ENVIRONMENT` for that proof obligation instead of replacing it with a weaker assertion.

### 9.6 Pause / backpressure cases

Using deterministic operational inputs, cover:

```text
pause_causes_zero_canonical_delta
pause_does_not_drop_open_occurrence
pause_does_not_drop_committed_outbox
resume_recomputes_fresh_truth_not_stale_candidate
watermark_green_normal_admission
watermark_yellow_reduces_optional_before_required_work
watermark_orange_defers_new_autonomous_admission
watermark_red_stops_saturated_new_autonomous_admission
terminalization_priority_survives_backpressure
reconciliation_priority_survives_backpressure
committed_outbox_drain_survives_backpressure
backpressure_state_never_becomes_semantic_blocker_record
```

### 9.7 Provider rate-limit cases

Use a deterministic virtual clock / provider simulator and cover at minimum repaired G42 semantics:

```text
rate_limit_at_or_below_5_percent_over_5_min_no_false_sustained_breach
rate_limit_above_5_percent_over_5_min_reduces_new_dispatch_concurrency
sustained_repeated_breach_applies_reference_halving_behavior
safe_retry_after_is_honored
polling_is_reduced_before_substantive_proof_or_review_is_weakened
provider_recovery_increases_concurrency_gradually
provider_recovery_does_not_jump_immediately_to_full_capacity
rate_limit_state_creates_no_semantic_occurrence
provider_unavailability_not_misclassified_as_implementation_or_gate_failure
```

### 9.8 Unsafe manual fallback cases

Cover at minimum:

```text
active_controlled_occurrence_denies_duplicate_manual_execution
committed_outbox_denies_duplicate_manual_execution
recovery_prefers_reconcile_resume_wait_or_governed_repair
operator_pause_or_exact_decision_does_not_erase_controlled_history
```

### 9.9 Predecessor regression suites

The same exact candidate must also pass:

```text
full CP-I05 focused suite
full tests/control_plane suite
full tests/project_state suite
full tests/skillset suite
```

No predecessor suite may be excluded merely because a CP-I06-specific suite is green.

---

## 10. Independent oracle / evidence obligations

CP-I06 proof must continue using the accepted independent oracle stack rather than production self-certification.

Applicable oracles include:

```text
O-AUTH
O-CRM
O-STORE
O-PROVIDER
O-TIMEPOLICY
```

Use the production SUT to produce behavior, but determine expected semantic legality from the independent oracle/reference contract wherever the P20 design requires it.

The P32 evidence generator must not become Gate authority.

### 10.1 Required evidence families

The reviewer-accessible CP-I06 bundle must materialize exact durable files or equivalent exact artifacts for:

```text
CPV-E-HUMAN-DECISION
CPV-E-RECOVERY-FAULT-MATRIX
CPV-E-BACKUP-RESTORE
CPV-E-RATE-LIMIT-CONTROL
CPV-E-DERIVED-STATE        # CP-I06 pause/backpressure nonsemantic update
```

CP-I05 exact evidence remains a predecessor dependency and should be linked/referenced, not rewritten as if CP-I06 originated it.

### 10.2 Suggested deterministic artifact layout

A conforming implementation may use:

```text
artifacts/cp-i06/
  human-decision.json
  recovery-fault-matrix.json
  backup-restore.json
  rate-limit-control.json
  derived-operational-state.json
  evidence-manifest.json
```

Equivalent names are acceptable only if the manifest makes the evidence-family mapping unambiguous.

### 10.3 Evidence manifest minimum contract

The manifest must include at least:

```yaml
schema_version: "0.2"
kind: CP-I06_EVIDENCE_MANIFEST
package_id: CP-I06-P31-01
package_ref: <exact P31 package ref>
result_revision: <exact P32 result revision>
task_anchor:
  revision: 7b3244417c5beba4c75d5eafd471083007fa1843
  relation: ancestor
predecessor:
  cp_i05_revision: 7b3244417c5beba4c75d5eafd471083007fa1843
  cp_i05_p34_comment: "5490992992"
  cp_i05_evidence_artifact_id: "9790980577"
evidence_files:
  - file: <file>
    evidence_family: <family>
    digest: sha256:<digest>
    passed: true | false
metrics: {...}
claims:
  p34_gate_pass: false
  evidence_compiler_gate_authority: false
  cp_i07_plus: false
  current_cross_primary_rollout: DENIED
passed: true | false
```

Each evidence file must contain case-level outcomes and enough exact inputs/observations for an independent reviewer to corroborate the claimed pass result. A prose-only `metric: 0` is not sufficient where the metric is expected to be derived from deterministic executed cases.

The manifest must never self-assert `p34_gate_pass: true`.

### 10.4 Zero-tolerance metric set

At minimum derive and require `0` for:

```text
unmaterialized_human_acknowledgement_accepted
semantic_retry_from_restart_or_age
unsafe_manual_duplicate_execution
acknowledged_commit_loss_in_supported_primary_fault_model
repair_scope_expansion_accepted
repair_budget_violation_accepted
repair_lineage_gap_accepted
escalation_history_mutated
conflicting_escalation_resolution_accepted
required_reverification_skipped
control_plane_self_issued_gate_verdict
pause_or_backpressure_semantic_mutation
committed_outbox_dropped_by_backpressure
sustained_rate_limit_breach_without_concurrency_reduction
instant_full_rate_limit_recovery
restore_digest_or_revision_mismatch
```

If a metric cannot be credibly derived from the implemented/probed supported profile, the evidence bundle must remain incomplete/blocked rather than hard-coding a passing value.

---

## 11. Engineering / timing constraints

### 11.1 Recovery targets

For the supported deployment/test profile actually represented by CP-I06 evidence, P20/P18 targets include:

```text
process replacement recovery starts <= 30 s
durable outbox recovery starts <= 60 s
95% recoverable pending items reconciled <= 5 min
application rollback/restart target <= 10 min
```

The last target applies only where the test environment genuinely represents the supported application deployment profile.

Regional/disaster restoration target `<=60 min` is deployment/release evidence and is not a CP-I06 local/unit-test claim.

### 11.2 Durability

For the supported primary fault domain:

```text
acknowledged canonical commit RPO = 0
```

A test cannot pass this requirement by ignoring a fault mode the claimed profile says it supports.

### 11.3 Rate-limit policy

```text
sustained >5% provider rate-limit responses over 5 min
  -> reduce new dispatch concurrency
  -> reference halving behavior
  -> honor safe retry-after
  -> recover gradually
```

### 11.4 Backpressure policy

```text
GREEN   <70%
YELLOW  70-85%
ORANGE  85-95%
RED     >=95%
```

The implementation may choose internal representation/configuration consistent with the accepted contracts, but it may not change these governed thresholds to make tests easier.

### 11.5 No performance overclaim

CP-I06 does not prove:

- full R0 API/throughput profile;
- S0 4x R0 stress profile;
- 7-day orchestration-cost target;
- monthly availability;
- regional disaster recovery.

Those remain later slice/profile evidence.

---

## 12. Hosted CI / evidence materialization

P32 must add a dedicated hosted workflow, normally:

```text
.github/workflows/control-plane-cp-i06.yml
```

The workflow must trigger on the exact CP-I06 production/test/evidence surfaces and run, at minimum:

```text
1. CP-I06 focused tests
2. full Control Plane regression suite
3. Project State regression suite
4. Skillset regression suite
5. CP-I06 evidence materialization
6. JSON/evidence structural validation
7. reviewer-accessible artifact upload
```

The uploaded artifact name must carry the exact reviewed result revision, for example:

```text
cp-i06-evidence-<exact-head-sha>
```

The workflow/evidence generator must pin:

- exact P31 `package_ref`;
- exact CP-I06 `result_revision`;
- task anchor `7b3244417c5beba4c75d5eafd471083007fa1843`;
- CP-I05 P34 `5490992992`;
- CP-I05 predecessor evidence artifact `9790980577`.

Before returning P32 to `CONTROL_REVIEW`, the executor must provide a reviewer-accessible durable `materialized_ref` for the exact result/evidence artifact. A local-only commit, worktree, or test transcript is insufficient.

---

## 13. P32 implementation sequence

The later P32 execution should use TDD and keep commits reviewable.

Recommended dependency order:

```text
A. RED tests / fixtures for P13 repair + escalation-resolution semantics
B. MutationService specialized operations and immutable lineage validation
C. Projection/policy/scheduler repair + escalation derived-state behavior
D. deterministic HumanDecision exact-ref path
E. recovery sweep / liveness behavior
F. pause/backpressure operational controls
G. provider rate-limit adaptation
H. supported backup/restore/restart path
I. evidence compiler + completeness tests
J. hosted exact-head workflow + reviewer-accessible artifact
```

This order is an implementation-control recommendation, not new semantic Authority. If a smaller order is mechanically better while preserving the same package boundaries and evidence, P32 may use it.

P32 must not skip RED evidence by first implementing production behavior and then writing only confirming tests.

---

## 14. Exit criteria

CP-I06 P32 is complete only when all of the following are true at one exact materialized result revision:

1. every authorized CP-I06 P13 operation is implemented through the single `MutationService` writer;
2. repair lineage/budget/scope rules pass deterministic positive and negative cases;
3. reverify/rereview are separate immutable occurrences;
4. P34 remains external/independent and no prior Gate Decision is rewritten;
5. escalation raise remains atomic and immutable;
6. exact HumanDecision behavior passes missing/chat-only/mutable/stale/wrong/exact cases;
7. escalation resolution is separately owned, idempotent for exact replay, and conflicting second resolution fails closed;
8. restart/age/recovery never creates semantic retry by itself;
9. pause/backpressure causes no canonical semantic mutation by itself;
10. already committed OPEN/outbox work is not dropped to improve operational health;
11. sustained >5%/5min provider rate limiting reduces new dispatch concurrency and recovery is gradual;
12. supported reference backup/restore preserves exact acknowledged canonical history and required replay state;
13. unsafe manual duplicate execution is denied for active controlled work;
14. every required zero-tolerance metric is `0` from executed case-level evidence;
15. CP-I06 focused tests pass;
16. full Control Plane regression passes;
17. Project State regression passes;
18. Skillset regression passes;
19. evidence bundle is complete, exact-head-bound, digest-addressed, and reviewer-accessible;
20. Evidence Compiler declares no Gate authority;
21. Current cross-Primary rollout remains `DENIED`;
22. CP-I07+ remains unstarted;
23. exact result/evidence is materialized before return to `CONTROL_REVIEW`.

P32 success is:

```text
implementation_result = READY_FOR_CONTROL_REVIEW
```

not:

```text
P34 = PASS
```

---

## 15. Blocked return behavior

P32 must fail closed and return the earliest valid blocker when the bounded package cannot be safely completed.

### 15.1 Authority / semantic ambiguity

If implementation discovers that accepted P12/P13/P16/P18/P20 semantics are contradictory or insufficient to decide a trust-sensitive transition:

```text
status: BLOCKED_AUTHORITY
route: aegis -> earliest untrusted Authority owner
```

Do not repair Product/Modeling/Architecture/Verification truth inside CP-I06 implementation.

### 15.2 Repository divergence

If the CP-I05 task anchor/package ancestry cannot be established:

```text
status: BLOCKED_EXECUTION_DIVERGENCE
```

Do not force reset/rewrite history.

### 15.3 Evidence materialization failure

If implementation/tests succeed locally but exact result/evidence cannot be made reviewer-accessible:

```text
status: BLOCKED_EVIDENCE
```

Do not claim review readiness from executor prose.

### 15.4 Environment/provider limitation

If the claimed supported recovery/restore/provider capability cannot be exercised or corroborated in the available environment:

```text
status: BLOCKED_ENVIRONMENT
```

Keep the capability gap explicit. Do not fake the evidence or weaken the contract.

### 15.5 Implementation defect

If the package is semantically clear but the implementation cannot satisfy it:

```text
status: BLOCKED_IMPLEMENTATION
```

Return exact failing tests/evidence and preserve valid completed work for later P35/P36 classification/repair.

### 15.6 Current rollout prohibition

Current cross-Primary automatic rollout remains:

```text
DENIED
```

This is not a CP-I06 implementation failure. It is a Current governed rollout boundary that tests must preserve. Capability fixtures may demonstrate future semantics only when clearly marked non-Current.

---

## 16. Required P32 surface handoff

When P32 is explicitly started, use a surface handoff equivalent to:

```yaml
surface_handoff:
  from: CONTROL_REASONING
  to: CODE_EXECUTION
  primary_owner: aegis-implementation
  stage: P32 Implementation — CP-I06
  package_id: CP-I06-P31-01
  package_ref: <exact commit materializing this P31 package>
  task_anchor:
    revision: 7b3244417c5beba4c75d5eafd471083007fa1843
    relation: ancestor
  resume_cursor: null
  return_surface: CONTROL_REVIEW
  materialization_required: true
```

The P32 executor must first verify fresh repository state and record its actual starting revision. It may not rediscover or expand package semantics merely because execution occurs on another surface.

---

## 17. P31 disposition

This document completes only:

```text
CP-I06 / P31 Task Packaging
```

Disposition:

```yaml
package_id: CP-I06-P31-01
status: READY / MATERIALIZED
owner: aegis-implementation
execution_surface: CONTROL_REASONING
task_anchor:
  revision: 7b3244417c5beba4c75d5eafd471083007fa1843
  relation: ancestor
resume_cursor: null
current_cross_primary_rollout: DENIED
cp_i07_plus: NOT_STARTED
p32_execution: NOT_STARTED
next_legal_stage: P32 Implementation — CP-I06
next_surface: CODE_EXECUTION
```

P31 stops here. P32 must be a separate explicitly started occurrence.