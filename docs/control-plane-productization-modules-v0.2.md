# Aegis Control Plane Productization v0.2 — P15 Module Design

Status: **Draft / Proposed Authority — P15 Module Design**

Scope: `aegis/control-plane-productization/modules`

Upstream architecture basis:

- PR #27 P14 exact head: `54999ce91ff4f35455916c33b4f7891e2b6b8d4d`
- `docs/control-plane-productization-architecture-v0.2.md`
- upstream modeling head: `f29c4da3698038e0174e4380707fa618b03c40b2`
- P21 Authority Review #3: `5062616510`
- modeling verdict: `PASS / ACCEPTED_FOR_DOWNSTREAM`

This P15 design refines P14 into independently understandable modules with stable interfaces and invariants. It does not change P10-P14 semantics.

---

# 1. P15 objective

Freeze the module boundaries needed to implement the P14 Control Plane architecture without allowing implementation convenience to blur ownership.

P15 must make these facts mechanically obvious in code structure:

```text
canonical write
!= projection
!= policy/routing
!= dispatch transport
!= external truth ownership
```

and:

```text
one module may coordinate another
without inheriting that module's semantic authority
```

The module design should be small enough for an initial single-process implementation while preserving boundaries that remain valid if workers/processes are separated later.

---

# 2. Non-goals

P15 does not:

- redefine WorkScopeRef, StageOccurrence, package, Escalation, ScheduleBasis, RequiredChildAcceptanceBinding, or P13 operations;
- add new durable semantic aggregates;
- choose a database vendor;
- choose a queue/broker vendor;
- choose RPC/HTTP/CLI syntax;
- define exact JSON Schema files or language-specific class names;
- define exact temporal happy/retry/recovery sequences; P16 owns runtime data flow;
- define OS/process/ABI/platform realization; P17 owns platform contract;
- define throughput/SLO/backpressure budgets; P18 owns engineering/optimization;
- enable cross-Primary automatic dispatch before Current Authority permits it;
- begin implementation.

---

# 3. Module map

P15 freezes the following logical modules.

```text
                         +------------------+
                         |  control-facade  |
                         +---------+--------+
                                   |
                    queries        | commands/intents
                                   v
+---------------------------------------------------------------------+
|                        CONTROL CORE                                 |
|                                                                     |
|  +----------------+      +------------------+                        |
|  | control-query  |<-----| control-projection|                       |
|  +----------------+      +---------+--------+                        |
|                                  ^                                  |
|                                  |                                  |
|  +----------------+      +-------+----------+       +-------------+ |
|  | control-policy |<-----| control-trust    |------>| external     | |
|  +-------+--------+      | resolver         |       | ports        | |
|          |               +------------------+       +-------------+ |
|          v                                                          |
|  +----------------+        +------------------+                      |
|  | control-       |------->| control-mutation |------------------+  |
|  | scheduler      |        +--------+---------+                  |  |
|  +----------------+                 |                            |  |
|                                     v                            |  |
|                           +------------------+                    |  |
|                           | control-store    |<-------------------+  |
|                           +--------+---------+                       |
|                                    |                                |
|                              durable outbox                          |
|                                    v                                |
|                           +------------------+                       |
|                           | control-dispatch |                       |
|                           +--------+---------+                       |
|                                    |                                |
|                           +--------v---------+                       |
|                           | external adapters|                       |
|                           +------------------+                       |
|                                                                     |
|  +--------------------+        +------------------+                  |
|  | control-recovery   |------->| core modules     |                  |
|  +--------------------+        +------------------+                  |
+---------------------------------------------------------------------+

Cross-cutting, non-semantic:
  control-observability

Pure shared definitions:
  control-domain
```

The diagram is dependency/ownership guidance, not a mandatory deployment topology.

---

# 4. Dependency rules

The stable dependency direction is:

```text
control-domain
      ^
      |
control-store / control-external-ports
      ^                ^
      |                |
control-trust-resolver |
      ^                |
      |                |
control-mutation       |
control-projection     |
control-policy         |
      ^                |
      |                |
control-scheduler      |
control-dispatch ------+
control-recovery
control-query
control-facade
```

Rules:

1. `control-domain` depends on no infrastructure module.
2. external adapters implement `control-external-ports`; core modules do not import vendor/client implementations directly.
3. `control-store` owns persistence mechanics but does not call scheduler/policy/projection.
4. `control-mutation` is the only canonical writer.
5. `control-projection` is read/derive only.
6. `control-policy` is decision/derivation only; it cannot write canonical records.
7. `control-scheduler` may request a mutation but cannot bypass `control-mutation`.
8. `control-dispatch` consumes durable outbox entries; it cannot schedule a new StageOccurrence.
9. `control-recovery` coordinates existing interfaces; it gets no privileged backdoor write path.
10. `control-facade` does not become a second domain layer.
11. cyclic core dependencies are forbidden.

---

# 5. Module: `control-domain`

## 5.1 Purpose

`control-domain` is the pure semantic representation layer for already accepted P10-P13 contracts.

It contains implementation-neutral definitions for:

- canonical Control Plane records;
- canonical embedded values;
- operation request/result contracts;
- canonical enums/status/reason codes;
- exact `CanonicalRef` representation;
- canonicalization and digest primitives required by accepted schema rules;
- pure structural validation helpers that do not require external I/O.

It does **not** own new semantic meaning. It implements the accepted model.

## 5.2 Public interfaces

Conceptual interfaces:

```text
CanonicalCodec
  canonicalize(record) -> bytes
  digest(record) -> sha256
  verify_digest(record, expected) -> bool

StructuralValidator<T>
  validate(value) -> ValidationResult

CanonicalRefComparator
  compare(a, b) -> ordering
```

Concrete language API names are deferred.

## 5.3 Invariants

- canonicalization must be deterministic;
- digest calculation must match P12 rules;
- UUID timestamp bits never determine lifecycle order;
- this module performs no network/database/repository access;
- structural validation may reject malformed semantics but may not decide current Authority, current Gate status, or current proof truth;
- no mutable singleton/global state is required.

## 5.4 Explicit non-ownership

`control-domain` does not:

- determine NextLegalAction;
- decide Control Autonomy;
- resolve external refs;
- commit any record;
- issue P34 verdicts.

---

# 6. Module: `control-external-ports`

## 6.1 Purpose

This module defines stable read/interaction ports for systems whose truth remains externally owned.

Core code depends on these interfaces, not on GitHub, filesystem, Project State implementation, Proof Runtime implementation, Codex, or ChatGPT-specific clients.

## 6.2 Common snapshot contract

Every external read that may affect trust-sensitive routing returns:

```yaml
source_snapshot:
  source_kind: <PROJECT_STATE | PROOF_PLANE | EXECUTION_SURFACE | HUMAN_DECISION | OTHER_GOVERNED_SOURCE>
  snapshot_token: <opaque replay/freshness token>
  observed_at: <operational metadata only>
  resolved_refs:
    - <exact CanonicalRef>
```

`snapshot_token` is opaque to the Control Plane domain. P17 chooses physical representation.

The token is not Authority, Evidence, Gate, Integration, or a new semantic aggregate.

## 6.3 ProjectStatePort

Conceptual read interface:

```text
ProjectStatePort
  resolve_authorities(refs_or_scopes) -> ProjectStateSnapshot
  resolve_gate_decisions(gate_refs) -> ProjectStateSnapshot
  resolve_current_gate(gate_contract_ref) -> ProjectStateSnapshot
  resolve_integration(integration_ref) -> ProjectStateSnapshot
  resolve_blockers(scope) -> ProjectStateSnapshot
  verify_snapshot(token) -> SnapshotValidity
```

Writes are intentionally absent from the generic Control Plane port.

Project State mutation occurs only through its existing owning governance/Gate workflows.

## 6.4 ProofPlanePort

Conceptual interface:

```text
ProofPlanePort
  resolve_verification_spec(ref) -> ProofSnapshot
  resolve_obligations(ref) -> ProofSnapshot
  resolve_evidence(refs) -> ProofSnapshot
  resolve_proof_evaluation(ref) -> ProofSnapshot
  resolve_review_bundle(ref) -> ProofSnapshot
  verify_snapshot(token) -> SnapshotValidity
```

The port may expose governed proof-runtime commands later, but those commands remain owned by the Proof Plane and do not turn Control Plane into proof authority.

## 6.5 ExecutionSurfacePort

Conceptual interface:

```text
ExecutionSurfacePort
  dispatch(envelope) -> DeliveryReceipt
  query_delivery(dispatch_attempt_id) -> DeliveryState
  resolve_execution_position(occurrence_ref) -> ExecutionSnapshot
  resolve_materialized_result(ref) -> ResultSnapshot
```

The interface preserves:

```text
Task Anchor != Execution Cursor
```

and exact reviewer-accessible materialization.

## 6.6 HumanDecisionPort

Conceptual interface:

```text
HumanDecisionPort
  publish_escalation(view) -> DeliveryReceipt
  resolve_decision(external_decision_ref) -> DecisionSnapshot
```

The interface cannot synthesize a generic `approved=true` override.

## 6.7 Adapter invariant

All adapters may translate transport representation; none may translate semantic ownership.

---

# 7. Module: `control-store`

## 7.1 Purpose

`control-store` realizes the P14 Canonical Control Store boundary.

It owns persistence primitives for Control Plane canonical records and the atomic transaction boundary required by P13/P14.

It does not own business decisions about whether a mutation is semantically legal; `control-mutation` owns that decision.

## 7.2 Store interfaces

Conceptual read interface:

```text
ControlReader
  get_work_scope(ref)
  get_lane_head(lane_id)
  get_occurrence(ref)
  list_occurrence_revisions(occurrence_id)
  get_package(ref)
  get_escalation(ref)
  list_children(parent_work_scope_ref)
  list_open_occurrences(selector)
  read_idempotency(request_id)
  read_outbox(selector)
```

Conceptual transaction interface:

```text
ControlStore
  begin(expected_lane_heads, expected_record_revisions) -> ControlTransaction

ControlTransaction
  append_occurrence_revision(record)
  append_package_revision(record)
  append_escalation_revision(record)
  establish_work_scope_lane_binding(binding)
  append_idempotency_record(record)
  append_outbox(record)
  update_outbox_delivery_metadata(record)
  compare_lane_head(lane_id, expected)
  advance_lane_head(lane_id, next)
  commit() -> CommitResult
  abort()
```

Exact method names are not normative; the capability boundary is.

## 7.3 Projection cache interface

Projection cache is explicitly separate from canonical records:

```text
ProjectionCache
  get(key, algorithm_version) -> optional<Projection>
  put(key, algorithm_version, projection)
  invalidate(selector)
  clear()
```

Deleting this cache must never delete canonical truth.

## 7.4 Transaction invariants

`control-store` must support one atomic transaction for at least:

- child WorkScope + ChildWorkBinding + lane binding + first OPEN occurrence + permitted outbox;
- REQUIRED-child acceptance bindings + parent successor OPEN occurrence + permitted outbox;
- StageOccurrence terminal revision plus P13-required canonical companions;
- Escalation creation plus occurrence terminal binding where P13 requires semantic atomicity;
- canonical schedule mutation plus outbox entry;
- request idempotency result plus accepted mutation where replay safety requires them to agree.

## 7.5 CAS invariants

- lane head/version is the serialization oracle;
- compare-and-append determines the winner;
- lock/lease state cannot make a stale transaction valid;
- no last-write-wins on canonical truth;
- independent lanes may commit concurrently.

## 7.6 Outbox storage invariant

Outbox records live inside the same transactional persistence boundary as the semantic schedule commit that creates them.

Delivery acknowledgement is not part of that semantic transaction.

## 7.7 Explicit non-ownership

The store cannot decide:

- whether child acceptance is semantically satisfied;
- whether a stage may be scheduled;
- whether an external Gate is current;
- whether a proof is credible;
- whether a human decision is sufficient.

---

# 8. Module: `control-trust-resolver`

## 8.1 Purpose

`control-trust-resolver` is a read-only aggregation layer over external truth ports.

It gives projection/mutation/policy code one typed way to obtain exact externally owned facts without teaching those modules Project State/Proof/Execution vendor details.

It is not a second Project State or proof cache of authority.

## 8.2 Interface

Conceptual interface:

```text
TrustResolver
  resolve_for_projection(work_scope_ref) -> TrustSnapshotBundle
  resolve_for_mutation(operation_request) -> TrustSnapshotBundle
  resolve_child_acceptance(child_work_scope_ref) -> ChildAcceptanceSupport
  resolve_current_authority(trusted_basis) -> AuthoritySupport
  resolve_gate_support(refs) -> GateSupport
  resolve_proof_support(refs) -> ProofSupport
  verify_freshness(snapshot_bundle) -> FreshnessResult
```

## 8.3 TrustSnapshotBundle

A bundle contains:

- exact resolved refs;
- source-specific opaque snapshot tokens;
- typed validity/currentness facts returned by the owning adapter;
- unresolved/ambiguous conditions;
- no authored Control Plane verdict beyond derived validity classification.

The bundle is transient validation input unless exact refs/tokens are explicitly pinned into a canonical record under accepted schema rules.

## 8.4 ChildAcceptanceSupport

For REQUIRED-child continuation, the resolver must make available enough exact support for `control-mutation` to construct the accepted `RequiredChildAcceptanceBinding`:

- child WorkScope ref;
- exact completion occurrence ref;
- exact acceptance contract refs;
- exact result/evidence/proof/Gate/decision refs required by those contracts;
- source snapshot tokens/freshness result;
- ambiguity/conflict indication.

It does not return a free-floating new durable `ChildAccepted` record.

## 8.5 Invariants

- external truth remains externally owned;
- transient aggregation cannot overwrite canonical history;
- stale/ambiguous required truth is explicit, never silently coerced to false/true;
- resolver caches, if any, are operational caches and cannot authorize mutation without freshness validation.

---

# 9. Module: `control-mutation`

## 9.1 Purpose

`control-mutation` is the **single canonical write authority inside the Control Plane implementation**.

All P13 canonical mutations pass through this module.

No other module may append StageOccurrence/package/Escalation canonical revisions or advance a lane head directly.

## 9.2 Interface

Primary conceptual interface:

```text
MutationService
  apply(operation_request) -> OperationResult
```

Supported operation names remain exactly the accepted P13 vocabulary:

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

`RECOMPUTE_CONTROL_PROJECTION` delegates derivation to `control-projection`; it does not promote the projection to canonical business truth.

## 9.3 Internal collaborator ports

The module may depend on:

- `control-domain` validators/canonicalization;
- `ControlReader` / `ControlStore`;
- `TrustResolver`;
- `ProjectionEngine` where a validated current projection is an input to mutation checks;
- `PolicyEvaluator` only for policy facts explicitly required by the operation contract;
- `control-observability` for telemetry.

It must not depend on dispatch worker implementations.

## 9.4 Mutation pipeline contract

P15 freezes capability stages, not P16 timing:

```text
schema validation
canonical current-state resolution
external exact-truth resolution
operation-specific invariant validation
idempotency classification
compare-and-append transaction
canonical result
```

No later module may add a second hidden write step that changes the semantic meaning of the committed operation.

## 9.5 REQUIRED-child invariant

When scheduling a parent successor across REQUIRED barriers, `control-mutation` alone owns validation and construction of `RequiredChildAcceptanceBinding`.

Neither projection, scheduler, nor dispatch may synthesize or alter that binding.

## 9.6 Outbox invariant

When the accepted mutation is permitted to dispatch immediately, `control-mutation` writes the outbox entry in the same store transaction.

When Current Authority/policy does not permit automatic dispatch, no implementation may create an outbox entry simply because a candidate next action exists.

## 9.7 Idempotency invariant

- same request ID + same fingerprint -> replay accepted prior result;
- same request ID + different fingerprint -> conflict;
- transport delivery IDs never substitute for operation request IDs;
- semantic retry uses a new accepted scheduling operation/occurrence, not a hidden mutation retry.

## 9.8 Explicit non-ownership

`control-mutation` validates policy/Authority inputs but does not author them.

It cannot:

- choose product intent;
- decide P34;
- mutate external Gate/Authority/Proof truth;
- widen package scope;
- create a specialist result.

---

# 10. Module: `control-projection`

## 10.1 Purpose

`control-projection` deterministically derives current control state from canonical records plus exact current external truth.

It owns no canonical durable decision.

## 10.2 Interface

```text
ProjectionEngine
  project_work_scope(work_scope_ref, trust_snapshot_bundle) -> ControlProjection
  project_lane(control_lane_id, trust_snapshot_bundle) -> ControlProjection
  project_children(parent_work_scope_ref, trust_snapshot_bundle) -> ChildWorkProjection[]
  replay_historical_transition(occurrence_ref) -> HistoricalTransitionView
```

## 10.3 Outputs

Outputs include:

- ControlCursor;
- CurrentMacroPhase;
- RepairLineage;
- OpenEscalations;
- NextLegalAction;
- LifecycleSummary;
- child completion;
- child accepted_for_parent;
- current blockers/reasons.

## 10.4 Invariants

- same canonical/external input snapshot + same algorithm version -> same projection;
- projection may be cached but is disposable;
- projection cannot mutate canonical records;
- stale projection cannot authorize mutation;
- historical transition replay uses immutable ScheduleBasis/RequiredChildAcceptanceBinding rather than today's child projection;
- conflicting input truth returns fail-closed projected state;
- projection algorithm version is observable and replayable.

## 10.5 Explicit non-ownership

A projection value such as `READY`, `accepted_for_parent`, or `NextLegalAction` is derived routing state, not a new Gate/Authority verdict.

---

# 11. Module: `control-policy`

## 11.1 Purpose

`control-policy` answers whether an otherwise legal candidate action may proceed automatically under currently effective Control Autonomy / Gate / repair / orchestration rollout policy.

It remains separate from Proof Assurance.

## 11.2 Interface

```text
PolicyEvaluator
  evaluate_next_action(projection, trusted_policy_refs) -> PolicyDecision
  evaluate_repair(repair_context, trusted_policy_refs) -> PolicyDecision
  evaluate_dispatch(source_occurrence, target_owner, current_authority_support) -> DispatchAuthorization
```

## 11.3 PolicyDecision

Transient output may contain:

```yaml
mode: AUTONOMOUS | REVIEW_GUARDED | HUMAN_DECISION | PROHIBITED
reason_codes: [...]
policy_refs: [exact refs]
requires_escalation: true | false
```

This output is not a new durable Authority. Exact policy refs used for a canonical transition are pinned through existing accepted record fields where required.

## 11.4 Current composition gate

Until governance accepts the required orchestration reconciliation:

```text
cross-Primary automatic dispatch
-> PROHIBITED / compatibility-gated
```

The policy module may still allow projection of NextLegalAction.

It must not infer future authorization from target architecture intent.

## 11.5 Invariants

- Proof Assurance and Control Autonomy are separate inputs/axes;
- HUMAN_DECISION cannot be downgraded to AUTONOMOUS by implementation default;
- missing/ambiguous policy truth fails closed;
- destructive/irreversible actions remain governed by their accepted human-decision rules;
- policy evaluator is deterministic for the same exact input refs and policy version.

---

# 12. Module: `control-scheduler`

## 12.1 Purpose

`control-scheduler` converts a current projection plus policy decision into a **candidate P13 scheduling request**.

It is a planner/coordinator, not a canonical writer and not a specialist owner.

## 12.2 Interface

```text
Scheduler
  derive_candidate(work_scope_ref) -> ScheduleCandidate | NoAction
  submit_candidate(candidate) -> OperationResult
```

`submit_candidate` calls `MutationService`; it has no direct store write path.

## 12.3 ScheduleCandidate

A candidate is transient and contains enough information to construct the applicable accepted P13 scheduling operation:

- work scope/lane;
- predecessor occurrence;
- target stage span;
- target Primary owner;
- schedule reason;
- required package ref if applicable;
- expected-state guards;
- relevant policy refs/digests;
- dispatch authorization state.

It is not durable semantic truth until `control-mutation` accepts it.

## 12.4 Invariants

- one candidate never spans different Primary owners;
- scheduler never calls a specialist directly;
- scheduler never appends an occurrence directly;
- if Current Authority disallows cross-Primary auto-progression, scheduler returns/persists only allowed derived action state and does not manufacture an auto-dispatch mutation;
- scheduler losing a race is normal; it recomputes after canonical conflict rather than forcing its stale candidate;
- scheduler may be replicated because store CAS is the correctness boundary.

---

# 13. Module: `control-dispatch`

## 13.1 Purpose

`control-dispatch` transports already committed work to execution surfaces.

It owns delivery mechanics only.

## 13.2 Interfaces

```text
OutboxReader
  claim_ready_batch(worker_identity, lease_hint) -> OutboxEntry[]

DispatchService
  deliver(outbox_entry) -> DeliveryReceipt
  record_delivery_attempt(entry, receipt) -> DeliveryMetadataResult
```

Claim/lease semantics are coordination only; losing a lease does not invalidate canonical occurrence truth.

## 13.3 DispatchEnvelope

The stable semantic payload includes:

```yaml
occurrence_ref: <exact STAGE_OCCURRENCE ref>
work_scope_ref: <WorkScopeRef>
control_lane_id: <lane>
stage_span: <stage(s)>
primary_owner: <specialist>
execution_surface: <surface>
trusted_basis_digest: <digest>
policy_digest: <digest>
package_ref: null | <exact P31 package ref>
input_refs: [...]
```

Transport-specific attempt IDs/headers are outside the semantic payload.

## 13.4 Invariants

- outbox entry must already be durable before delivery;
- delivery is at-least-once;
- duplicate delivery reuses the same occurrence ID;
- dispatch cannot alter stage owner, package ref, TrustedBasis, WorkScope, or input refs;
- transport retry does not create a new StageOccurrence;
- successful network acknowledgement is not proof of substantive completion;
- worker return must re-enter through accepted mutation/adapter boundaries.

## 13.5 Explicit non-ownership

`control-dispatch` cannot:

- schedule next work;
- decide retry semantics;
- terminalize an occurrence by itself;
- decide a Gate;
- mutate package scope.

---

# 14. Module: external adapters

P15 defines adapter modules separately from stable ports so platform integrations can change without contaminating core semantics.

Initial adapters:

```text
adapter-project-state
adapter-proof-plane
adapter-execution-surface
adapter-human-decision
```

Additional adapters require the same rule: implement an existing port; do not create new semantic ownership.

## 14.1 `adapter-project-state`

Responsibilities:

- translate Current Project State representation into exact refs/current lineage/snapshot tokens;
- preserve Gate Contract != Gate Decision != Integration-bound Gate Decision;
- fail closed on invalid lineage;
- never expose a convenience `set_gate_pass()` API to Control Plane core.

## 14.2 `adapter-proof-plane`

Responsibilities:

- resolve exact VerificationSpec/obligation/evidence/evaluation/review-bundle refs;
- invoke only proof-runtime capabilities permitted by the owning Proof Plane contract;
- preserve ProofEvaluation != Gate;
- preserve independent completeness-review boundary.

## 14.3 `adapter-execution-surface`

Responsibilities:

- map DispatchEnvelope to CONTROL_REASONING / CODE_EXECUTION / CONTROL_REVIEW / CODE_REVERIFY realization;
- preserve package identity;
- preserve Task Anchor != Execution Cursor;
- preserve exact result/materialized-ref return;
- map execution reconciliation states without manufacturing Authority.

## 14.4 `adapter-human-decision`

Responsibilities:

- surface escalation payloads;
- resolve exact externally governed decision refs;
- never treat UI acknowledgement as semantic resolution.

---

# 15. Module: `control-recovery`

## 15.1 Purpose

`control-recovery` coordinates infrastructure recovery using normal core interfaces.

It gets no hidden mutation privilege.

## 15.2 Interface

```text
RecoveryCoordinator
  reconcile_open_occurrence(occurrence_ref) -> RecoveryResult
  reconcile_outbox(entry_ref) -> RecoveryResult
  reconcile_external_truth_change(work_scope_ref) -> RecoveryResult
  reconcile_execution_position(occurrence_ref) -> RecoveryResult
```

## 15.3 Allowed actions

Recovery may:

- re-read canonical state;
- re-resolve external exact truth;
- re-dispatch an existing committed occurrence;
- request P33-compatible execution reconciliation through the Execution Surface adapter;
- request projection rebuild;
- submit a normal P13 operation where a governed semantic repair/retry/reverify/rereview is truly required.

## 15.4 Forbidden actions

Recovery may not:

- silently create a new occurrence because a process restarted;
- force-move a repository to match stale metadata;
- mutate an old terminal result;
- rewrite RequiredChildAcceptanceBinding;
- bypass repair budget/policy;
- convert delivery timeout into substantive failure without the owning contract.

## 15.5 Invariant

```text
infrastructure recovery
!= semantic retry
```

---

# 16. Module: `control-query`

## 16.1 Purpose

`control-query` provides read models for product UX, audit, debugging, and sessionless resume.

It consumes projections and exact canonical refs but does not mutate control truth.

## 16.2 Interfaces

```text
ControlQuery
  get_summary(work_scope_ref) -> LifecycleSummaryView
  get_current(work_scope_ref) -> CurrentControlView
  get_exceptions(work_scope_ref) -> ExceptionView[]
  get_audit_transition(occurrence_ref) -> TransitionAuditView
  get_internal_trace(work_scope_ref) -> InternalLifecycleView
```

## 16.3 Product view

Default public view remains conceptually:

```text
DEFINE / BUILD / PROVE / SHIP
status
what changed
trusted result
open exceptions
next human decision, if any
```

Exact P-stage/ref/digest/routing details are progressively disclosed.

## 16.4 Audit view

`get_audit_transition` must be reconstructable from canonical records/exact refs even if operational logs are absent.

For REQUIRED-child historical continuation it exposes the pinned RequiredChildAcceptanceBinding, not today's acceptance boolean.

## 16.5 Invariants

- query DTOs are not semantic authority;
- cache/UI formatting cannot change routing truth;
- user-facing simplicity never deletes canonical detail.

---

# 17. Module: `control-facade`

## 17.1 Purpose

`control-facade` is the stable application boundary presented to UI/CLI/API callers.

It keeps callers from depending directly on store, scheduler, or adapter internals.

## 17.2 Interface families

Conceptually:

```text
ControlFacade
  query(...)
  request_next_action(...)
  submit_human_decision_ref(...)
  resume(...)
  request_cancel_or_pause(...)
```

Actual mutation semantics behind these calls must map to accepted P13 operations or externally governed control inputs; the facade does not invent generic PATCH semantics.

## 17.3 Invariants

- no `set_status`, `set_cursor`, `mark_pass`, or arbitrary canonical PATCH API;
- every canonical write path terminates at MutationService;
- every read path is projection/query based;
- external caller identity maps into P13 actor/audit identity where relevant;
- facade may be transport-neutral at P15.

---

# 18. Module: `control-observability`

## 18.1 Purpose

Cross-cutting traces, metrics, structured logs, and diagnostics.

## 18.2 Interface

Conceptually:

```text
ControlTelemetry
  record_mutation(...)
  record_projection(...)
  record_policy_decision(...)
  record_dispatch_attempt(...)
  record_recovery(...)
  record_adapter_freshness(...)
```

## 18.3 Correlation keys

Operational telemetry should correlate at least:

- WorkScopeRef;
- control_lane_id;
- StageOccurrence ID;
- operation_request_id;
- dispatch attempt ID;
- package ref.

## 18.4 Invariants

- telemetry loss cannot erase semantic history;
- trace order does not override canonical lifecycle order;
- operational logs cannot be used as a substitute for exact required EvidenceArtifact/Gate truth;
- observability module cannot write canonical business records.

---

# 19. Canonical write matrix

Only one module owns canonical writes.

| Record / state | Writer | Other modules |
|---|---|---|
| WorkScope/lane binding | `control-mutation` via `control-store` | read only |
| StageOccurrence revisions | `control-mutation` via `control-store` | read only |
| P31 package revisions | `control-mutation` via `control-store` | read only |
| Escalation revisions | `control-mutation` via `control-store` | read only |
| ScheduleBasis / RequiredChildAcceptanceBinding | `control-mutation` via `control-store` | read only |
| idempotency semantic record | `control-mutation` via `control-store` | read only |
| outbox creation tied to semantic mutation | `control-mutation` via `control-store` | dispatch reads/updates delivery metadata only |
| projection cache | `control-projection`/cache adapter | disposable derived state |
| Authority / GateDecision / Integration | external owning workflow | Control Plane read/reference only |
| Verification/Proof/Evidence | Proof Plane owner | Control Plane read/invoke/reference only |
| Execution Cursor | Execution Surface owner / accepted navigation contract | Control Plane carries snapshot only |

No implementation may add a second canonical writer for convenience.

---

# 20. Interface-level failure contract

All core interfaces use typed failure classes rather than ambiguous null/exception-only semantics at trust boundaries.

Representative classes:

```text
INVALID_REQUEST
BLOCKED_TRUST
BLOCKED_AUTHORITY
BLOCKED_EVIDENCE
BLOCKED_IMPLEMENTATION
BLOCKED_ENVIRONMENT
CONFLICT_RETRY_REQUIRED
IDEMPOTENT_REPLAY
AMBIGUOUS_EXTERNAL_TRUTH
EXTERNAL_SNAPSHOT_STALE
DELIVERY_UNCERTAIN
```

These are transport/module result classes; they must map to accepted domain/P13 statuses without inventing new Gate verdicts.

Rules:

- trust ambiguity fails closed;
- CAS conflict is retry/recompute, not semantic failure;
- delivery uncertainty is infrastructure state, not proof failure;
- adapter unavailability cannot be converted into stale trust acceptance;
- module exception types must preserve the owning layer in diagnostics.

---

# 21. Module-level test seams

P15 freezes testable seams without defining P20 Verification Design.

## 21.1 `control-domain`

Can be tested as pure deterministic functions.

## 21.2 `control-store`

Can be tested against transaction/CAS/idempotency/outbox invariants using an in-memory conformance implementation plus real-store adapter tests later.

## 21.3 `control-trust-resolver`

Can be tested with fake external ports returning exact snapshots, stale tokens, forks, missing refs, and conflicting truth.

## 21.4 `control-mutation`

Can be tested against operation fixtures with fake store/trust ports while asserting exact canonical append sets and no forbidden external writes.

## 21.5 `control-projection`

Can be golden-tested for deterministic derived state from canonical history + exact external snapshots.

## 21.6 `control-policy`

Can be table-tested for autonomy/gate/repair/orchestration combinations, including Current Authority compatibility gating.

## 21.7 `control-scheduler`

Can be tested for candidate derivation and race handling without executing specialists.

## 21.8 `control-dispatch`

Can be tested for at-least-once duplicate delivery, immutable semantic envelope, and no occurrence creation.

## 21.9 adapters

Each adapter gets contract tests proving exact-ref preservation and non-ownership.

## 21.10 `control-recovery`

Can be tested with crash/restart/delivery-uncertain/open-occurrence fixtures while proving no implicit semantic retry.

These seams are inputs to later P20 verification design; P15 does not itself declare proof sufficient.

---

# 22. Packaging boundary for initial implementation

P15 allows the following initial source/package grouping:

```text
control/domain
control/ports
control/store
control/trust
control/mutation
control/projection
control/policy
control/scheduler
control/dispatch
control/recovery
control/query
control/facade
control/observability
adapters/project_state
adapters/proof_plane
adapters/execution_surface
adapters/human_decision
```

Names are descriptive and may be adapted to repository language conventions, but one implementation package must not collapse semantic boundaries merely to reduce files.

A single deployable process may contain most core modules initially.

Module boundary != mandatory microservice boundary.

---

# 23. Process placement constraints carried from P14

P15 does not fix exact processes but freezes compatibility rules.

Allowed initial placement:

```text
Process A:
  facade
  query
  projection
  policy
  scheduler
  mutation
  store client
  trust resolver
  recovery coordinator

Worker B:
  outbox/dispatch

External domains:
  Project State
  Proof Plane
  specialist execution/review surfaces
```

Also allowed: Worker B colocated in Process A if it remains restartable and cannot move delivery acknowledgement into the canonical semantic commit.

Forbidden coupling:

- database transaction waits for remote specialist acknowledgement;
- dispatch worker owns canonical scheduling decision;
- specialist worker has direct canonical DB write access;
- Project State adapter shares writable internal DB tables with Control Store merely to avoid explicit boundaries;
- projection cache becomes the write source of truth.

---

# 24. Security/capability assignment by module

Least-authority capability guidance:

| Module | Required capability | Must not require by default |
|---|---|---|
| `control-query` | read projections/canonical refs | repo write, Gate write |
| `control-projection` | read canonical + external snapshots | canonical write |
| `control-policy` | read policy/trust refs | repo write, proof write |
| `control-scheduler` | submit scheduling requests | direct DB write, specialist credentials |
| `control-mutation` | canonical transaction write | arbitrary repo credentials |
| `control-dispatch` | read outbox + call target adapter | Authority/Gate mutation |
| `adapter-execution-surface` | occurrence-scoped execution credentials | Control Store direct write |
| `adapter-project-state` | read trust state; governed write only in owning workflows | generic Gate mutation |
| `adapter-proof-plane` | proof-runtime scoped capabilities | P34 verdict capability |
| `control-recovery` | normal module APIs | force-reset/force-push backdoor |

Actor identity/audit fields pass through module boundaries unchanged where the accepted operation contract requires them.

---

# 25. Current-Authority rollout gate at module level

P15 makes the orchestration compatibility gate explicit in module interfaces.

Before governance reconciliation:

```text
ProjectionEngine
  may derive NextLegalAction across owner boundary

Scheduler
  may derive a candidate

PolicyEvaluator.evaluate_dispatch(...)
  returns non-autonomous / prohibited for disallowed cross-Primary auto-dispatch

MutationService
  must not create a dispatching schedule mutation whose policy precondition is not satisfied

DispatchService
  never sees an outbox entry for an unauthorized transition
```

After future governance acceptance, enabling zero-user-turn continuation should primarily change governed policy/configuration and adapter rollout, not require deleting stage ownership boundaries.

P15 therefore avoids hard-coding today's prohibition into the data model while refusing to bypass it in runtime behavior.

---

# 26. REQUIRED-child module responsibility split

For REQUIRED child work:

```text
control-projection
  derives current child completion / accepted_for_parent

control-trust-resolver
  resolves exact current support and source snapshots

control-policy
  may evaluate whether continuation is otherwise permitted

control-scheduler
  derives parent successor candidate

control-mutation
  validates every uncrossed barrier
  constructs RequiredChildAcceptanceBinding
  commits successor atomically

control-store
  provides transaction/CAS

control-dispatch
  transports the already committed successor
```

No other module may mark a child accepted or barrier consumed.

Historical barrier crossing remains derived from immutable successor ScheduleBasis.

---

# 27. Repair / reverify / rereview module responsibility split

The existing durable occurrence model remains controlling.

```text
control-projection
  exposes active finding/blocker/repair lineage

control-policy
  checks repair budget, defect class, autonomy limits

control-scheduler
  selects the accepted P13 repair/reverify/rereview operation family

control-mutation
  validates and appends the new occurrence

control-dispatch
  delivers the new occurrence

specialist owner
  owns substantive repair/reverify/review result
```

No module mutates a prior occurrence into a repair attempt.

---

# 28. Sessionless resume module responsibility split

Sessionless resume is implemented as composition of existing truth, not a special mutable session object.

```text
control-query / facade
  receives WorkScope or project-resume intent

control-store
  provides canonical current lane/history

control-trust-resolver
  refreshes current external truth

control-projection
  rebuilds ControlCursor + NextLegalAction

control-recovery
  reconciles OPEN occurrence/outbox/execution position when required
```

Conversation history may improve UX but is never the only state source.

No `ChatSession` becomes a canonical control aggregate in v0.2.

---

# 29. Compatibility with retained Proof Plane modules

P15 does not duplicate the Verification Productization subsystem decomposition.

Control Plane integration is through `ProofPlanePort` / `adapter-proof-plane`.

The retained Proof Plane still owns its internal modules such as:

- Verification Authoring Controller;
- Spec Validator;
- VerificationSpec Materializer;
- Obligation Generator;
- Evidence Collector/Materializer;
- Proof Evaluator;
- Verification Summary Projector;
- Independent Obligation Completeness Checker;
- Review Bundle Adapter;
- existing P34 review boundary.

Control Plane modules may coordinate those capabilities through exact refs but may not collapse them into `control-projection` or `control-policy`.

---

# 30. P15 invariants

A conforming module implementation must preserve all of the following:

1. `control-domain` is infrastructure-free and implements accepted semantics only.
2. external truth access occurs through stable ports/adapters.
3. external adapters translate representation, not semantic ownership.
4. `control-store` owns persistence mechanics, not semantic permission.
5. `control-mutation` is the only canonical Control Plane writer.
6. no scheduler/dispatch/recovery direct canonical DB write path exists.
7. `control-projection` is deterministic/read-only/disposable.
8. stale projection never authorizes mutation.
9. `control-policy` is distinct from Proof Assurance and cannot author Authority.
10. `control-scheduler` produces transient candidates only.
11. one scheduled substantive occurrence has one Primary owner.
12. `control-dispatch` sees only already committed work.
13. transport retry never creates semantic retry.
14. semantic mutation + permitted outbox entry is atomic.
15. delivery acknowledgement is outside semantic commit.
16. store CAS/lane head is the concurrency truth boundary.
17. locks/leases are optional coordination only.
18. independent lanes may proceed concurrently.
19. `control-trust-resolver` cannot turn cached/stale external facts into trusted current truth.
20. Project State remains owner of Authority/Gate/Integration.
21. Proof Plane remains owner of Verification/Proof/Evidence.
22. P34 remains sole Gate owner.
23. Execution Cursor remains navigation metadata.
24. VerificationBoundImplementationPackage remains the strengthened existing P31 package truth.
25. RequiredChildAcceptanceBinding is created only by accepted parent-successor mutation.
26. no mutable child-accepted/barrier-consumed registry is introduced.
27. infrastructure recovery is not semantic retry.
28. facade/query DTOs are not semantic authority.
29. observability is not semantic history.
30. no arbitrary PATCH/status setter bypasses explicit P13 operations.
31. current orchestration Authority gates cross-Primary automatic dispatch.
32. specialist execution surfaces never get direct Control Store write authority.
33. user-facing simplicity is derived from full canonical state, not destructive compression.
34. modules may be colocated in one process but trust boundaries remain explicit in code/interfaces.

---

# 31. Decisions deliberately deferred to P16-P18

## P16 Runtime Data Flow

Must freeze temporal sequences for:

- fresh schedule/dispatch/return/terminalize;
- duplicate scheduler race;
- duplicate delivery;
- process restart/outbox recovery;
- worker timeout/late return;
- P33 execution reconciliation;
- external truth change;
- REQUIRED-child fan-out/join;
- repair/reverify/rereview loop;
- escalation/human resolution;
- cancellation/pause/backpressure.

## P17 Platform Contract

Must choose/define:

- local/hosted process boundaries;
- RPC/IPC/HTTP/CLI/SDK representation;
- snapshot token physical representation;
- auth/credential propagation;
- GitHub/ChatGPT/Codex/CI integration capability contracts;
- worker callback/poll/subscription mechanisms;
- ABI/language boundaries if more than one runtime language is used.

## P18 Engineering / Optimization

Must define measurable:

- expected active WorkScopes/lanes;
- mutation throughput;
- projection rebuild cost;
- outbox latency/retry budgets;
- OPEN occurrence timeout/age policies;
- adapter freshness budgets;
- backpressure/load-shedding behavior;
- storage retention/indexing/compaction constraints;
- observability SLOs;
- performance baselines/targets.

---

# 32. P16 handoff boundary

P15 is complete when downstream work can answer **which module owns every state transition and interface**, without yet needing exact time-ordered runtime choreography.

The next architecture-family stage is:

```text
P16 Runtime Data Flow
```

P16 must consume the exact materialized P15 head and preserve:

- single canonical writer;
- store CAS correctness;
- projection read-only boundary;
- scheduler candidate-only boundary;
- commit-before-dispatch/outbox boundary;
- external truth adapters;
- no semantic retry from infrastructure retry;
- current orchestration authorization gate;
- RequiredChildAcceptanceBinding ownership.

If P16 discovers that a runtime flow requires violating one of those module boundaries, it must route the defect back to P15/P14 rather than silently adding a bypass.

Do not begin P20/P30/P32 implementation from P15.

---

# 33. P15 disposition

```text
P15 Module Design
  -> READY / MATERIALIZED — Draft/Proposed
```

Authority chain:

```text
P10-P13 modeling
  @ f29c4da3698038e0174e4380707fa618b03c40b2
  -> P21 #3 PASS / ACCEPTED_FOR_DOWNSTREAM

P14 System Architecture
  @ 54999ce91ff4f35455916c33b4f7891e2b6b8d4d

P15 Module Design
  -> this artifact
```

The next architecture-family stage is P16 Runtime Data Flow.