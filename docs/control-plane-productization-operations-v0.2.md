# Aegis Control Plane Productization v0.2 — P13 Operation / Mutation Model

Status: **Draft / Proposed Authority — P13 Operation / Mutation Model**

Scope: `aegis/control-plane-productization`

Upstream Product Authority:

- `docs/control-plane-productization-v0.2.md`
- `docs/control-plane-productization-v0.2-p02-p03-repair.md`
- accepted Product Authority head: `c628bdc15fdd3d32511a04b6f09055413f2786c3`

Upstream modeling package:

- `docs/control-plane-productization-model-v0.2.md`
- `docs/control-plane-productization-schema-v0.2.md`
- exact P12 head before P13: `b6135c1fa00f5b6c4071b69345e402f7aa894398`

Retained external semantic boundaries:

- Verification Productization / Proof Plane candidate on PR #23, accepted semantic head `2eb7d507098d24328b883dfa1366521390026fce`;
- Project State v0.5 Gate Decision lineage remains the repository source of Gate Decision semantics;
- Execution Surface v0.2 remains the source of `Task Anchor != Execution Cursor`, P32/P33 resume classification, and reviewer-accessible result materialization semantics;
- existing stage ownership remains controlling until separately governed Control Plane orchestration reconciliation.

This document defines **P13 operations over the P12 canonical objects**. It does not redesign P12, choose databases/queues/services, define P14 subsystem topology, or implement an orchestrator.

---

# 1. Mutation philosophy

The Control Plane uses a small explicit command vocabulary rather than a generic `update object` operation.

Core rule:

> **Every accepted mutation appends durable truth; no operation rewrites historical trust facts.**

Therefore:

```text
create / append / terminate / supersede-by-new-revision
```

are allowed semantic patterns, while:

```text
overwrite history / mutate accepted evidence / rewrite Gate verdict / retarget an executing package
```

are forbidden.

The domain is intentionally not a general event-sourcing framework. Immutable record revisions are the canonical history already defined by P12; P13 only defines legal transitions between those revisions.

---

# 2. Operation request envelope

Operation requests use an execution/transport envelope that is **not itself a new product aggregate**:

```yaml
operation:
  operation_name: <canonical operation name>
  operation_request_id: req_<UUIDv7>
  actor:
    class: CONTROL_PLANE | PRIMARY_OWNER | EXECUTION_SURFACE | REVIEW_SURFACE | HUMAN | EXTERNAL_SYSTEM
    id: <actor identity>
  control_lane_id: lane_<UUIDv7>
  expected_state:
    active_occurrence_ref: null | <exact StageOccurrence revision ref>
    predecessor_occurrence_ref: null | <exact terminal StageOccurrence revision ref>
    target_record_revision: null | <positive integer>
    target_record_digest: null | <sha256 digest>
    trusted_basis_digest: null | <sha256 digest>
    package_ref: null | <exact package revision ref>
  idempotency_fingerprint: <sha256 digest of canonical semantic request payload>
  payload: <operation-specific payload>
```

Rules:

1. `operation_request_id` is a transport/deduplication identity, not Authority, Evidence, Gate, Project State, or a Control Plane aggregate.
2. The same `operation_request_id` plus the same `idempotency_fingerprint` MUST return the already-materialized semantic result rather than execute the mutation again.
3. The same `operation_request_id` with a different fingerprint is `OPERATION_IDEMPOTENCY_CONFLICT` and fails closed.
4. `expected_state` is an optimistic concurrency guard. It does not become Authority.
5. A mutation MUST validate exact referenced state before committing.
6. Missing required guards at a trust-sensitive mutation boundary fail closed rather than degrading to last-write-wins.
7. UUIDv7 timestamps do not establish domain order. Canonical order is established by revision lineage, exact predecessor bindings, and operation preconditions.

---

# 3. Canonical operation vocabulary

P13 v0.2 defines exactly these domain operations:

```text
MATERIALIZE_IMPLEMENTATION_PACKAGE
REVISE_IMPLEMENTATION_PACKAGE

SCHEDULE_STAGE_OCCURRENCE
RECORD_EXECUTION_PROGRESS
TERMINATE_STAGE_OCCURRENCE

RAISE_ESCALATION
RECORD_ESCALATION_RESOLUTION

SCHEDULE_REPAIR_OCCURRENCE
SCHEDULE_REVERIFICATION_OCCURRENCE
SCHEDULE_REREVIEW_OCCURRENCE

RECOMPUTE_CONTROL_PROJECTION
```

The final four scheduling operations are specialized semantic forms of occurrence scheduling. They exist to make repair/reverification/re-review invariants explicit; they do not create separate workflow aggregates.

No generic `PATCH_STAGE_OCCURRENCE`, `UPDATE_ESCALATION`, `SET_CONTROL_CURSOR`, `SET_CURRENT_MACRO_PHASE`, `SET_GATE_VERDICT`, or `MOVE_EXECUTION_CURSOR` operation exists.

---

# 4. MATERIALIZE_IMPLEMENTATION_PACKAGE

Purpose:

Create the first canonical revision of a complete `VerificationBoundImplementationPackage`.

Input requirements:

- exact TrustedBasis;
- scope identity and exact scope contract;
- exact VerificationSpec reference;
- required Proof Obligation Set reference when the governing proof contract requires materialization before BUILD;
- exact acceptance oracle references;
- exact Evidence Compilation contract;
- PolicyBinding;
- task anchor when repository execution depends on a repository baseline.

Preconditions:

1. Required P12 package fields are complete and valid.
2. All exact refs required at this trust boundary resolve and match their identities.
3. Required verification/acceptance semantics already exist; the operation may not invent them.
4. `control_autonomy != HUMAN_DECISION` is not by itself proof that the package is executable; proof/Gate requirements remain independently validated.
5. No package with the allocated `package_id` revision `1` already exists.

Commit:

```text
create package record_revision = 1
calculate package_digest
materialize exact package revision
```

Atomicity:

The canonical package revision either materializes completely or not at all. A partially written package is not canonical.

Failure examples:

```text
PACKAGE_MISSING_VERIFICATION_BINDING
PACKAGE_SCOPE_CONFLICT
PACKAGE_STALE_TRUSTED_BASIS
PACKAGE_UNRESOLVABLE_REF
PACKAGE_IDENTITY_CONFLICT
```

No canonical mutation occurs on failure.

---

# 5. REVISE_IMPLEMENTATION_PACKAGE

Purpose:

Append a new immutable revision to an existing package lineage when authorization semantics materially change.

Preconditions:

1. `expected_state.target_record_revision` equals the current package revision.
2. `expected_state.target_record_digest` equals that exact revision digest.
3. The proposed complete replacement package passes all `MATERIALIZE_IMPLEMENTATION_PACKAGE` invariants.
4. `record_revision = prior + 1`.

Semantic rules:

1. Revision is whole-record replacement semantics, not partial patch semantics.
2. Prior revisions remain immutable and addressable.
3. Any material change to TrustedBasis, scope, verification binding, PolicyBinding, or required task anchor creates a new package revision and digest.
4. An already-open StageOccurrence bound to an older exact package revision is **not retargeted** to the new package revision.
5. If the old package is no longer safe for an active occurrence, that occurrence must terminate/block according to the earliest untrusted layer; a new occurrence may later bind the new package.
6. Package revision does not move an Execution Cursor.

Concurrency:

Two revisions racing from the same expected prior revision cannot both commit. One may append `N+1`; the other receives `STALE_PACKAGE_REVISION` and must re-read/reason rather than silently rebasing.

---

# 6. SCHEDULE_STAGE_OCCURRENCE

Purpose:

Create a new separately owned `StageOccurrence` revision `1 / OPEN` after the Control Plane derives a legal next action.

Payload includes:

```yaml
occurrence_id: so_<UUIDv7>
stage_span: <P12 StageSpan>
primary_owner: <owner>
trusted_basis: <TrustedBasis>
policy_binding: <PolicyBinding>
schedule_basis: <ScheduleBasis>
input_refs: []
repair_context: null
execution_navigation: null | <accepted initial snapshot>
```

Preconditions:

1. Stage span is valid and maps entirely to `primary_owner`.
2. TrustedBasis is effective enough for this new occurrence.
3. Any required package ref is exact and still valid for scheduling.
4. The predecessor/active-occurrence guards match current canonical lane state.
5. No other scheduler-active OPEN occurrence exists for the same `control_lane_id` scheduling slot.
6. The requested transition is legal under lifecycle routing plus the pinned PolicyBinding.
7. `HUMAN_DECISION` forbids autonomous scheduling unless the required human/external decision is already present as exact accepted fact.
8. A required independent review boundary cannot be skipped merely because scheduling is autonomous.
9. The scheduler may derive a new Primary owner but may not execute that owner's substantive stage while performing this operation.

Atomic commit:

```text
validate schedule guard
+ allocate/materialize StageOccurrence revision 1 OPEN
+ make that exact occurrence eligible for dispatch
```

The operation does not create downstream substantive output.

## 6.1 Lane serialization boundary

`control_lane_id` is the concurrency serialization boundary for one control trajectory, not necessarily the whole project.

P13 requires at most one scheduler-active OPEN occurrence per lane slot. Independent work may use distinct control lanes. P14 decides physical storage/indexing and any child-lane topology; P13 does not invent a project-wide global lock.

## 6.2 Commit-before-dispatch invariant

A substantive executor MUST NOT begin work from a merely transient scheduling decision.

Canonical sequence:

```text
validate transition
  -> durably commit OPEN StageOccurrence
  -> dispatch exact occurrence ID + exact refs
  -> executor acts
```

Never:

```text
dispatch / start work
  -> later try to create occurrence history
```

This makes occurrence history the durable authorization boundary for autonomous execution.

## 6.3 Delivery retries

Transport may be at-least-once.

Repeated delivery of the same exact scheduled occurrence:

```text
same occurrence_id
+ same exact revision/input bindings
```

is a dispatch retry, **not a new StageOccurrence**.

A receiver MUST deduplicate by exact occurrence identity and execution contract. If it cannot determine whether an execution already started/completed, it must reconcile the existing occurrence rather than allocate a duplicate semantic attempt.

---

# 7. RECORD_EXECUTION_PROGRESS

Purpose:

Persist a Control-Plane-accepted execution/navigation checkpoint for sessionless resume without making the cursor proof or scope authorization.

This operation appends a new immutable OPEN revision of the same StageOccurrence.

Allowed delta:

```text
execution_navigation only
```

All frozen start facts remain byte-semantically identical:

```text
control_lane_id
stage_span
primary_owner
TrustedBasis
PolicyBinding
ScheduleBasis
input_refs
RepairContext
```

Preconditions:

1. Target occurrence is OPEN and current revision matches `expected_state`.
2. The incoming snapshot has already been reconciled under the owning Execution Surface/P33 contract when repository position semantics apply.
3. Task anchor matches the exact authorized package/task anchor semantics.
4. The operation does not infer correctness from cursor position.
5. It cannot widen scope, change owner, change Authority, alter package revision, or satisfy a proof obligation.

Ordering:

A new accepted checkpoint appends `record_revision = prior + 1`.

A cursor is not required to be lexically/temporally monotonic by SHA or timestamp. Progress validity comes from the external execution-position contract. A cursor that cannot be reconciled under that contract is rejected as `EXECUTION_NAVIGATION_DIVERGENCE`.

Idempotency:

The same checkpoint request against the same prior revision is idempotent. Competing different checkpoints from the same prior occurrence revision cause a concurrency conflict; the Control Plane must reconcile rather than pick one by arrival time.

---

# 8. TERMINATE_STAGE_OCCURRENCE

Purpose:

Append the one terminal revision of an OPEN StageOccurrence.

Preconditions:

1. Target occurrence is OPEN.
2. Expected current revision/digest matches exactly.
3. Frozen start facts are unchanged.
4. Terminal status/outcome combination is valid under P12.
5. Every `produced_ref` required for downstream trust is durable and exact.
6. P34 `READY` is not substituted for a missing official external Gate Decision.
7. Required result materialization exists before a completion outcome that claims review readiness.
8. Raised/resolved escalation bindings satisfy §§9-10.
9. Required repair/reverification/re-review policy has not been silently bypassed.

Commit:

```text
append record_revision = prior + 1
state = TERMINAL
terminal = <TerminalFacts>
```

Once terminal, no later StageOccurrence revision is valid.

## 8.1 Terminal outcome matrix

Canonical relationship:

```text
COMPLETED
  -> READY | READY_WITH_FINDINGS

BLOCKED
  -> BLOCKED_*

ESCALATED
  -> normally BLOCKED_UNRESOLVED_DECISION or owning BLOCKED_* status
  -> at least one raised_escalation_id

FAILED_WITH_FINDING
  -> owning BLOCKED_* or READY_WITH_FINDINGS only when downstream policy explicitly permits the finding
```

A non-P34 StageOccurrence `COMPLETED / READY` never means Gate PASS.

## 8.2 Exact-result materialization

For execution/review boundaries that require reviewer-accessible materialization, an executor message, local worktree, local commit, or test transcript is not enough.

If exact result materialization cannot be produced, the occurrence terminates with the smallest valid blocking status, normally `BLOCKED_EVIDENCE`, rather than pretending to be complete.

---

# 9. RAISE_ESCALATION

Purpose:

Materialize an immutable Escalation when automatic continuation must stop for a human/product/Authority/risk decision.

Preconditions:

1. `raised_from_occurrence_ref` resolves to the occurrence being terminated or already terminal at the exact expected revision.
2. Escalation category and owning layer are valid.
3. The unresolved condition cannot be safely closed by the currently authorized automatic policy.
4. The Escalation does not itself answer the decision.

Atomic relationship with occurrence termination:

When an occurrence terminates as `ESCALATED`, creating the new Escalation record(s) and appending the terminal occurrence revision that references those IDs is one semantic atomic unit:

```text
create Escalation revision 1
+ terminate StageOccurrence with raised_escalation_ids
```

Either all referenced Escalations and the terminal occurrence commit, or none do.

This prevents terminal history from pointing to a non-existent escalation or an orphan Escalation from claiming a raise that never became terminal truth.

Escalation has no UPDATE operation.

---

# 10. RECORD_ESCALATION_RESOLUTION

Purpose:

Record later durable truth that resolves an Escalation **without mutating the Escalation record**.

Canonical resolution occurs through a separately owned StageOccurrence that:

- consumes the exact escalation ID and required human/external decision as input/TrustedBasis fact;
- performs the owning lifecycle responsibility;
- terminates with that escalation ID in `resolved_escalation_ids`.

The resolution operation therefore appends the resolving StageOccurrence's terminal revision; it does not append an Escalation revision.

Preconditions:

1. Escalation exists and is currently unresolved.
2. Resolving occurrence is owned by the correct stage/layer.
3. Required decision/evidence is exact and durable.
4. Resolution does not silently weaken Authority/proof/Gate semantics.
5. One Escalation may have at most one effective resolution binding.

Idempotency:

Re-recording the exact same effective resolution is a no-op/result replay. A conflicting second resolution is `ESCALATION_RESOLUTION_CONFLICT` and fails closed. A materially new decision creates a new Escalation/occurrence history instead of rewriting the original question.

---

# 11. SCHEDULE_REPAIR_OCCURRENCE

Purpose:

Schedule one bounded authorized repair attempt as a new StageOccurrence rather than a hidden retry.

This is a specialized `SCHEDULE_STAGE_OCCURRENCE` with:

```yaml
schedule_basis.reason_code: REPAIR
repair_context:
  finding_ref: <exact finding>
  root_occurrence_ref: <exact root occurrence>
  previous_attempt_occurrence_ref: null | <exact previous repair occurrence>
  attempt_ordinal: <contiguous ordinal>
  repair_policy_digest: <exact current applicable policy digest>
```

Preconditions:

1. Finding classification is exact enough to identify an allowed repair class.
2. Repair class is permitted by the pinned RepairPolicy.
3. Attempt ordinal is exactly previous + 1, starting at `1`.
4. Attempt ordinal does not exceed `max_attempts`.
5. Root finding identity is unchanged across the lineage.
6. Required scope remains inside the existing authorized repair boundary.
7. Authority/product/semantic changes, uncertain material classification, destructive action, or exhausted budget prohibit automatic repair and require escalation/earlier-layer routing.
8. The repair occurrence has its own correct Primary owner; P35 classification does not become P36 implementation ownership.

There is no operation that increments a mutable repair counter. `attempts_used` and remaining budget are derived from committed repair occurrences.

---

# 12. SCHEDULE_REVERIFICATION_OCCURRENCE

Purpose:

Schedule fresh proof execution/evidence work after an authorized repair when required by policy/proof contract.

Specialized schedule semantics:

```text
reason_code = REVERIFY
new StageOccurrence ID
separately owned verification/execution stage
exact repaired result/package/evidence refs as inputs
```

Rules:

1. Reverification is never represented by mutating prior EvidenceArtifact or ProofEvaluation history.
2. New evidence/proof results are externally materialized under Proof Plane semantics and referenced exactly by the occurrence.
3. A required reverification cannot be skipped because repair tests happened to pass locally.
4. Automatic scheduling is allowed only when Control Autonomy permits it.

---

# 13. SCHEDULE_REREVIEW_OCCURRENCE

Purpose:

Schedule a fresh independently owned review/Gate occurrence after a repair or new evidence when Gate policy requires it.

Rules:

1. Re-review is a new StageOccurrence.
2. A prior Gate Decision is never changed in place.
3. P34 remains the sole official Gate owner.
4. The new review consumes the exact new result/evidence plus exact historical basis needed for independent judgment.
5. `REVIEW_GUARDED` may permit the Control Plane to schedule this review without a user round trip; it never permits the Control Plane to issue the review verdict itself.
6. Downstream trust cannot advance until the required fresh official Gate Decision exists.

---

# 14. RECOMPUTE_CONTROL_PROJECTION

Purpose:

Deterministically derive/calculate ControlCursor, macro phase, open Escalations, repair lineages, next legal action, and LifecycleSummary from canonical history plus exact external truth.

This is **not a canonical domain mutation**.

Inputs:

```text
all relevant exact canonical record revisions
+ exact/current external Authority/Gate/Proof/Integration truth
+ projection algorithm version
```

Rules:

1. Projection may be recomputed at any time.
2. Cache replacement is safe because projection fields are generated only.
3. A cached projection never overrides canonical records.
4. If two different projection values are derivable from the same exact inputs/version, the projection is invalid and control fails closed.
5. Unknown/unresolvable required external truth blocks next-action derivation rather than being guessed.
6. `current_macro_phase` is projected from internal lifecycle responsibility, not authored transitions.
7. `next_legal_action` is recomputed after every accepted canonical mutation and before autonomous scheduling.

Idempotency:

Same exact canonical/external input identities plus the same projection version must produce semantically identical output.

---

# 15. Automatic continuation transaction boundary

Automatic continuation across Primary owners is explicitly **not one cross-stage atomic transaction**.

Canonical sequence:

```text
Occurrence A owned by Primary A
  -> TERMINATE_STAGE_OCCURRENCE
  -> durable terminal boundary

RECOMPUTE_CONTROL_PROJECTION
  -> derive next legal action
  -> validate policy / exact current truth

SCHEDULE_STAGE_OCCURRENCE
  -> Occurrence B OPEN
  -> owned by Primary B
```

Properties:

1. A must be durably terminal before B may be scheduled.
2. Primary A does not create B as part of its substantive operation.
3. If projection/scheduling fails after A commits, A remains truthful terminal history and the system resumes from that boundary later.
4. There is no distributed transaction that rolls A back because B could not start.
5. This preserves separately owned Stage Occurrences while enabling zero-user-turn continuation when policy allows.

---

# 16. Repair loop transaction boundary

Canonical automated repair loop:

```text
review occurrence terminal finding
  -> classification/finding exact ref
  -> recompute next action
  -> SCHEDULE_REPAIR_OCCURRENCE
  -> repair terminal exact result
  -> SCHEDULE_REVERIFICATION_OCCURRENCE if required
  -> fresh evidence/proof result
  -> SCHEDULE_REREVIEW_OCCURRENCE if required
  -> new official Gate Decision
  -> recompute next action
```

Each arrow crosses a durable boundary. The entire loop is **not** one rollbackable transaction.

If any step fails:

- committed prior occurrences remain history;
- no future step is assumed complete;
- resume starts from the latest trustworthy boundary;
- budget/lineage are derived from committed attempts only.

---

# 17. Ordering model

P13 uses four distinct ordering concepts.

## 17.1 Record revision order

Within one canonical object lineage:

```text
record_revision N -> N+1
```

is total and contiguous.

## 17.2 Occurrence predecessor order

Across StageOccurrences in one lane, `ScheduleBasis.predecessor_occurrence_ref` records the immediately relevant durable predecessor for that scheduled transition.

It does not mean all project work is globally serial.

## 17.3 Repair order

`RepairContext.previous_attempt_occurrence_ref + attempt_ordinal` creates a linear repair lineage.

## 17.4 External causal order

Git commits, Gate Decisions, Evidence artifacts, and other external objects retain their own governed ordering/lineage contracts. The Control Plane references them exactly; it does not infer their order from `recorded_at`.

No semantic decision uses wall-clock timestamp as its only ordering oracle.

---

# 18. Concurrency / conflict handling

The default concurrency model is optimistic and fail-closed.

## 18.1 Compare-and-append

A canonical append operation must specify the exact record revision/digest it believes is current. Commit succeeds only if that expectation still holds.

Conflict result:

```text
STALE_RECORD_REVISION
```

The caller must re-read current truth and re-derive the operation.

## 18.2 Schedule race

If two schedulers derive the next occurrence from the same lane boundary, only one may commit the next OPEN occurrence for that scheduling slot.

The loser receives:

```text
CONTROL_LANE_SCHEDULE_CONFLICT
```

It must recompute rather than dispatch its stale choice.

## 18.3 Terminal race

Only one terminal revision may append to an occurrence. A second different terminal request is:

```text
OCCURRENCE_ALREADY_TERMINAL
```

An exact duplicate terminal request is idempotently resolved to the existing terminal revision.

## 18.4 No last-write-wins at trust boundaries

Last-write-wins is forbidden for:

- package revisions;
- occurrence revisions;
- terminal outcome;
- repair ordinal;
- escalation resolution;
- TrustedBasis/PolicyBinding change.

---

# 19. Idempotency and deduplication

P13 distinguishes transport duplicate from semantic retry.

```text
Transport duplicate
  same operation_request_id + fingerprint
  -> return same semantic result

Dispatch duplicate
  same occurrence ID / exact work contract
  -> resume/reconcile same occurrence

Semantic retry / repair
  new StageOccurrence ID
  -> new durable history
```

Rules:

1. A network timeout after commit must not cause a second package revision or second occurrence when the caller retries.
2. Dedup state may be physically implemented in any P14-approved mechanism; P13 requires behavior, not a specific table/service.
3. Idempotency cannot convert conflicting semantic payloads into success.
4. A new `operation_request_id` does not authorize replaying an already-completed semantic action when canonical preconditions forbid it.

---

# 20. Replay model

P13 distinguishes **historical replay** from **current projection replay**.

## 20.1 Historical replay

Historical replay reconstructs canonical Control Plane history from immutable object revisions and exact operation results.

Rules:

1. Previously committed StageOccurrence/package/Escalation records are reproduced as written.
2. Old scheduling decisions are not re-derived using today's Authority or policy.
3. Historical TrustedBasis remains the basis that constrained that occurrence at the time.
4. Replay never changes an old outcome because a later Gate Decision or Authority now exists.

## 20.2 Current projection replay

Current projection replay takes immutable history plus currently effective exact external truth and recomputes:

- current control cursor;
- current macro phase;
- next legal action;
- open Escalations;
- current repair budget;
- lifecycle summary.

A later Authority/Gate change may alter **current actionability/projection** without altering historical records.

If required current external truth is missing or contradictory, current projection fails closed.

---

# 21. Undo / rollback / compensation

There is no destructive domain undo.

Forbidden:

```text
delete occurrence history
rewrite a prior terminal status
remove a failed repair attempt
mutate prior package authorization
change old Escalation evidence/question
rewrite historical Gate/Evidence
```

Correction uses new durable truth:

- new package revision;
- new StageOccurrence;
- new repair attempt;
- new Proof/Evidence artifact under its owning contract;
- new Gate Decision under Project State/P34 semantics;
- new Escalation where the decision question materially changes.

Physical transaction rollback is allowed only for an operation that **never became a successful canonical commit**.

---

# 22. Cancellation / stop semantics

P13 distinguishes transient operation cancellation from durable lifecycle history.

## 22.1 Before canonical commit

A pending mutation request may be cancelled before commit. It produces no canonical record and may be retried from current truth later.

## 22.2 After StageOccurrence scheduling

Once an OPEN StageOccurrence is durably committed, cancellation cannot erase that occurrence.

An execution surface may stop work only through its governed execution contract. The occurrence must eventually be reconciled and terminated truthfully with the smallest applicable existing status; cancellation is not permission to fabricate `COMPLETED` or delete partial history.

## 22.3 Stop automatic continuation

A user/platform directive that disables future automatic scheduling is an **operational control/permission input**, not a substitute for Authority/Gate truth. P13 requires the scheduler to honor such a directive before `SCHEDULE_STAGE_OCCURRENCE` commits.

The physical persistence/configuration boundary for operator pause/resume is a P14 control-service concern because P12 intentionally does not introduce a mutable ControlLane aggregate. P13 therefore does not invent a canonical `CANCELLED` status or mutable lane record.

Existing terminal occurrences remain historical; future scheduling stays stopped while the valid external control directive is in force.

---

# 23. Fail-closed error taxonomy

P13 operations return one of:

```text
COMMITTED
IDEMPOTENT_REPLAY
REJECTED_PRECONDITION
CONFLICT_RETRY_REQUIRED
BLOCKED_TRUST
BLOCKED_ENVIRONMENT
```

Representative reason codes:

```text
OPERATION_IDEMPOTENCY_CONFLICT
STALE_RECORD_REVISION
CONTROL_LANE_SCHEDULE_CONFLICT
OCCURRENCE_ALREADY_TERMINAL
STALE_TRUSTED_BASIS
UNRESOLVABLE_EXACT_REF
ILLEGAL_STAGE_OWNER
ILLEGAL_STAGE_TRANSITION
CONTROL_POLICY_PROHIBITS_AUTONOMY
REQUIRED_REVIEW_NOT_SATISFIED
PACKAGE_MISSING_VERIFICATION_BINDING
PACKAGE_SCOPE_CONFLICT
EXECUTION_NAVIGATION_DIVERGENCE
REPAIR_CLASS_NOT_AUTHORIZED
REPAIR_BUDGET_EXHAUSTED
REPAIR_LINEAGE_CONFLICT
ESCALATION_RESOLUTION_CONFLICT
MISSING_MATERIALIZED_RESULT
UNSUPPORTED_SCHEMA_VERSION
AMBIGUOUS_CONTROL_PROJECTION
```

Rules:

1. A failed mutation does not partially commit canonical state.
2. Unknown semantic/Authority conditions map to a blocking result, never a guessed transition.
3. Conflict retry means **re-read/re-derive**, not blind command replay with relaxed guards.
4. Environment failure cannot be silently reclassified as implementation correctness failure.
5. A blocker at an earlier untrusted layer routes ownership according to existing Aegis semantics; P13 does not repair that layer itself.

---

# 24. Invariants across operations

A conforming P13 implementation preserves all of the following:

1. Canonical history is append-only by immutable record revisions.
2. No operation changes an existing record revision.
3. Package authoring is atomic and complete; partial canonical packages do not exist.
4. Existing OPEN occurrences are never silently retargeted to a new package revision.
5. StageOccurrence is committed OPEN before substantive dispatch.
6. Dispatch retries reuse the same occurrence identity.
7. A semantic retry/repair is a new occurrence, never a duplicate dispatch.
8. One substantive StageOccurrence has exactly one Primary owner.
9. Cross-owner continuation crosses a durable terminal/schedule boundary.
10. A Primary terminal operation never substantively executes the next Primary's stage.
11. Progress checkpoints mutate only execution-navigation state through appended occurrence revisions.
12. Execution cursor is navigation, never proof/scope authorization.
13. Every terminal occurrence has one terminal revision only.
14. Required exact results/evidence are materialized before claiming the corresponding readiness boundary.
15. Escalations are immutable and raised atomically with the occurrence terminal binding when created together.
16. Escalation resolution creates later durable truth; the original Escalation never changes.
17. Repair attempts are new StageOccurrences with contiguous bounded lineage.
18. Repair counters/budgets are derived, never incremented mutable truth.
19. Required reverification/re-review are separate occurrences and cannot be skipped by orchestration convenience.
20. Prior Gate Decisions/Evidence/ProofEvaluations are never rewritten by Control Plane operations.
21. Control projections are recomputed, never directly authored.
22. Cached projection divergence cannot override canonical truth.
23. Optimistic concurrency conflicts fail closed; last-write-wins is forbidden at trust boundaries.
24. Same request + same fingerprint is idempotent; same request + different semantics conflicts.
25. Historical replay preserves old truth; current projection replay may change actionability without history rewrite.
26. Automatic scheduling cannot weaken Proof Assurance, Gate policy, Authority, scope, or repair bounds.
27. Operator pause/cancel never erases committed history.
28. P13 does not create a new lifecycle P-stage, Gate, Proof object, Repair workflow aggregate, or mutable ControlLane truth.

---

# 25. User-facing product boundary

These operations are internal Control Plane machinery.

Normal UX does not expose a command console containing:

```text
SCHEDULE_STAGE_OCCURRENCE
RECORD_EXECUTION_PROGRESS
record_revision
basis_digest
repair ordinal
exact Gate Decision ID
execution cursor
```

The normal user sees the already accepted product projection:

```text
DEFINE / BUILD / PROVE / SHIP
status
trusted result
what changed
exception / required human decision
```

Internal exactness remains expandable for audit/debugging only.

---

# 26. P13 disposition

P13 Operation / Mutation Model is complete as a Draft/Proposed continuation of the P10-P12 Control Plane model.

It freezes:

- explicit mutation vocabulary rather than generic patch operations;
- complete/atomic package materialization and compare-and-append package revision;
- OPEN-occurrence commit before dispatch;
- occurrence progress checkpoints as immutable revisions;
- one terminal occurrence revision;
- immutable escalation raise and later resolution binding;
- repair/reverification/re-review as separate StageOccurrences;
- cross-owner automatic continuation across durable boundaries;
- optimistic concurrency and lane scheduling guards;
- transport idempotency versus semantic retry distinction;
- historical replay versus current projection replay;
- append-only correction/compensation instead of destructive undo;
- fail-closed conflict/error behavior;
- non-productization of internal orchestration mechanics.

The complete modeling family is now:

```text
P10 Product Object Model       COMPLETE — Draft/Proposed
P11 Interaction Behavior       COMPLETE — Draft/Proposed
P12 Semantic Schema            COMPLETE — Draft/Proposed
P13 Operation / Mutation Model COMPLETE — Draft/Proposed
```

No Current Authority, Skill, Project State, Proof Plane, Execution Surface implementation, or orchestrator is modified by this document.

Next stage is outside `aegis-modeling` ownership:

```text
P14 System Architecture — Aegis Control Plane
```

Per Aegis composition rules, P13 stops at this durable modeling boundary and does not automatically execute P14.