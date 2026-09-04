# Aegis Control Plane Productization v0.2 — P14 System Architecture

Status: **Draft / Proposed Authority — P14 System Architecture**

Scope: `aegis/control-plane-productization/architecture`

Upstream semantic basis:

- PR #26 exact head: `f29c4da3698038e0174e4380707fa618b03c40b2`
- P21 Authority Review #3: `5062616510`
- verdict: `PASS / ACCEPTED_FOR_DOWNSTREAM`

Normative upstream modeling package:

- `docs/control-plane-productization-model-v0.2.md`
- `docs/control-plane-productization-schema-v0.2.md`
- `docs/control-plane-productization-operations-v0.2.md`
- `docs/control-plane-productization-model-v0.2-p21-repair.md`
- `docs/control-plane-productization-model-v0.2-p21-b3-repair.md`

Retained compatible Proof Plane foundation:

- PR #23 semantic head `2eb7d507098d24328b883dfa1366521390026fce`
- PR #24 architecture head `6faa0eff7a53ccd2828eae1b0ef1aeaef1de1a83`
- `VerificationSpec -> ProofObligation -> EvidenceArtifact -> ProofEvaluation -> P34`
- P34 remains the sole official Gate owner.

Current repository control boundaries used as constraints:

- Project State registry baseline `a77fca147ead0d66484201cad30d8c6a80d11f8e`
- `aegis/project-state` current registry entry v0.5 semantics
- `aegis/skill/decomposition` current v0.2 composition semantics
- `aegis/execution-surface` current v0.2 Task Anchor / Execution Cursor semantics

This architecture does not silently supersede any of those Current Authorities.

---

# 1. Architecture objective

Define the smallest system architecture that can turn the accepted Control Plane model into a durable autonomous loop while preserving Aegis trust boundaries.

The architecture must make this possible:

```text
observe durable truth
  -> derive current control projection
  -> determine the next legal stage / owner
  -> durably schedule a separately owned StageOccurrence
  -> dispatch exact work to the correct execution surface
  -> receive/materialize exact result/evidence
  -> terminalize the occurrence
  -> recompute control state
  -> auto-advance, bounded-repair, or escalate
```

without making the user a message bus and without turning the orchestrator, Codex, Project State, Proof Runtime, or P34 into a universal owner.

Core architecture rule:

> **The Control Plane owns control progression; specialist stages own substantive truth.**

Supporting rules:

> **Canonical control history is durable; current control state is derived.**
>
> **Commit before dispatch; transport may retry but may not invent semantic attempts.**
>
> **External Authority / Proof / Gate / Integration truth is referenced, not copied.**
>
> **Correctness comes from canonical compare-and-append state, not from queue delivery guarantees or in-memory locks.**

---

# 2. Non-goals

P14 does not:

- redefine any P10-P13 object, field, identity, mutation, barrier, or replay rule;
- introduce a giant mutable `PersistentControlState` aggregate;
- introduce another official Gate or acceptance verdict;
- move ProofEvaluation, EvidenceArtifact, GateDecision, Integration, Finding, or Authority ownership into the Control Plane;
- turn `.aegis/state.json` or `gates.json` into a high-frequency workflow database;
- make Codex or any specialist Skill the loop controller;
- allow one Primary owner to execute another Primary's stage;
- claim distributed exactly-once execution;
- make an Execution Cursor into Authority, Evidence, Gate, Integration, or Project State;
- enable autonomous cross-Primary continuation under today's Current Skill Composition Authority before the required governance reconciliation is complete;
- define final database vendor, file paths, class names, RPC protocol, CLI syntax, deployment platform, or ABI; those belong to P15-P17;
- begin implementation.

---

# 3. System shape

The target architecture has one logical Control Plane Runtime surrounded by independently owned truth/execution domains.

```text
                         USER / PRODUCT UX
                               |
                               v
                  +-----------------------------+
                  | Control Facade / Query API  |
                  +--------------+--------------+
                                 |
                                 v
+------------------------------------------------------------------+
|                    AEGIS CONTROL PLANE RUNTIME                    |
|                                                                  |
|  Command / Mutation Boundary                                     |
|          |                                                       |
|          v                                                       |
|  Canonical Control Store <------> Projection Engine              |
|          |                         |                              |
|          |                         v                              |
|          |                  Scheduler / Policy Engine             |
|          |                         |                              |
|          +---- transactional ----> Outbox                        |
|                                    |                              |
|                                    v                              |
|                           Dispatch / Transport Gateway            |
|                                                                  |
|  Recovery / Reconciliation Controller                            |
|  Escalation / Human-Decision Gateway                             |
+-------------------+----------------+----------------+-------------+
                    |                |                |
                    v                v                v
             Project State      Proof Plane      Execution Surfaces
             Adapter            Adapter          Adapter
                    |                |                |
              Authority /        Spec / Proof /   Reasoning / Codex /
              GateDecision /     Evidence refs     Review / Reverify
              Integration
```

The diagram shows logical responsibility boundaries, not mandatory microservices.

Preferred initial realization:

> **one logically centralized Control Plane service/process backed by a transactional durable store, with stateless/restartable scheduler and dispatch workers around the same canonical store.**

Horizontal replication is allowed later, but no correctness property may depend on there being only one process.

---

# 4. Authoritative data ownership

The architecture freezes one system-of-record owner per truth family.

| Truth / object | System of record | Control Plane role |
|---|---|---|
| `WorkScopeRef` / `ChildWorkBinding` correlation | Canonical Control Store | owns canonical control correlation |
| `StageOccurrence` revisions | Canonical Control Store | owns |
| `VerificationBoundImplementationPackage` | canonical P31 package record in Control Store | owns the strengthened existing P31 package truth; no wrapper truth |
| `Escalation` revisions | Canonical Control Store | owns |
| `ScheduleBasis` / `RequiredChildAcceptanceBinding` | Canonical Control Store | owns immutable transition basis |
| `ControlCursor` / macro / repair lineage / child acceptance projection | Projection Engine derived from canonical + external exact truth | derives only |
| Authority registry / supersession | Project State / governance owner | resolves/references only |
| Gate Contract / immutable Gate Decision / Integration | Project State / P34/governance owner | resolves/references only |
| VerificationSpec / ProofObligation / EvidenceArtifact / ProofEvaluation | Proof Plane | resolves/invokes/references only |
| Finding truth | existing Gate/review/evidence owner | exact refs only |
| Task Anchor | P31 package / Execution Surface contract | carries exact ref; does not reinterpret |
| Execution Cursor | Execution Surface accepted navigation state | stores accepted navigation snapshot only as permitted by governed boundary; never trust truth |
| implementation result/materialized artifact | execution/evidence durable artifact owner | exact ref only |

Architecture invariant:

> **A Control Plane projection may aggregate these truths for routing, but aggregation never transfers semantic ownership.**

---

# 5. Canonical Control Store

## 5.1 Responsibility

The Canonical Control Store is the durable source of Control Plane-owned canonical records:

- WorkScope / lane identity mapping;
- StageOccurrence immutable revisions;
- P31 package immutable revisions;
- Escalation immutable revisions;
- ScheduleBasis and RequiredChildAcceptanceBinding;
- accepted execution-navigation snapshots carried by StageOccurrence revisions where allowed;
- operation idempotency records needed to enforce P13 replay semantics;
- per-lane canonical head/version used for optimistic concurrency;
- transactional outbox entries associated with committed occurrences.

## 5.2 Separate from Project State

Persistent Control State is **not** implemented by growing Project State into one high-frequency mutable workflow document.

Project State remains the durable owner of repository/governance truth such as Authority, Gate Decision lineage, Integration, and their generated projections.

The Control Store is a separate persistence boundary because:

1. StageOccurrence/package/escalation revisions evolve at workflow frequency rather than governance-manifest frequency;
2. P13 requires compare-and-append, idempotency, atomic child spawn, and commit-before-dispatch semantics;
3. Project State explicitly preserves immutable decision lineage rather than becoming a general event-sourcing/control-loop system;
4. Control state must be resumable without duplicating Gate/Authority semantics.

P14 does not require a specific physical database vendor or repository path.

## 5.3 Not generic event sourcing

The Control Store may physically append immutable record revisions, but it is not a generic event-sourcing architecture.

Canonical P12/P13 records remain the business truth. Infrastructure events, queue acknowledgements, traces, and logs do not become semantic truth merely because they are append-only.

---

# 6. Command / Mutation Boundary

The Command / Mutation Boundary is the only component allowed to commit P13 canonical mutations.

It implements the accepted operation vocabulary exactly:

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

Responsibilities:

- validate operation schema and actor class;
- validate exact `expected_state` guards;
- resolve relevant immutable external refs through adapters;
- enforce lane/work/package ownership invariants;
- enforce WorkScope / Control Lane 1:1 mapping;
- enforce REQUIRED-child barrier semantics;
- construct RequiredChildAcceptanceBinding where a barrier is crossed;
- enforce repair budget / policy constraints;
- enforce request-id / fingerprint idempotency;
- execute compare-and-append transaction;
- atomically persist canonical mutation plus any required outbox entry;
- return P13 result classes.

Explicit non-ownership:

- does not choose product intent;
- does not author Authority;
- does not issue P34 verdicts;
- does not weaken proof or policy;
- does not fabricate execution results.

---

# 7. Concurrency and transaction model

## 7.1 Lane serialization

`control_lane_id` is the scheduling/concurrency serialization key for one WorkScope trajectory.

The store maintains a canonical lane head/version. Scheduling or terminalization uses compare-and-append against that version.

Correctness rule:

> **A lane lock or lease may reduce contention, but only canonical compare-and-append determines the winner.**

Therefore stale workers cannot commit through last-write-wins.

## 7.2 No project-wide global lock

Independent WorkScopes / child lanes may progress concurrently.

A project-wide global lock is not required and would unnecessarily serialize unrelated work.

## 7.3 Multi-record atomic mutations

The store must support one transaction across all Control Plane-owned records affected by a semantic mutation.

Required examples:

### Child spawn

```text
new WorkScopeRef
+ immutable ChildWorkBinding
+ new lane mapping
+ child StageOccurrence revision 1 / OPEN
+ outbox dispatch record when dispatch is permitted
```

become durable together or not at all.

### REQUIRED-child barrier crossing

```text
validate all uncrossed REQUIRED children
+ materialize exact RequiredChildAcceptanceBinding(s)
+ validate successor TrustedBasis/input refs
+ create parent successor StageOccurrence revision 1 / OPEN
+ outbox dispatch record when dispatch is permitted
```

become durable together or not at all.

## 7.4 External-store atomicity

Project State, Proof Plane, Git, CI, and execution systems are separate systems of record. The Control Store therefore does not pretend to offer one transaction spanning every external system.

Instead:

- adapters return immutable exact refs plus an authoritative source snapshot/revision token where the source has mutable current-head semantics;
- the Control mutation pins those exact refs/snapshot identities;
- later external truth changes are later facts and may alter current actionability;
- they never rewrite the already committed historical transition basis;
- if a required source cannot provide sufficiently fresh/replayable identity, mutation fails closed rather than claiming cross-system atomicity.

---

# 8. Projection Engine

The Projection Engine is deterministic and rebuildable.

Inputs:

- canonical Control Store records;
- exact current Project State snapshot;
- exact current Proof/Gate/Integration refs needed by policy;
- accepted execution-navigation facts where applicable.

Outputs include the accepted generated families:

```text
ControlCursor
CurrentMacroPhase
RepairLineage
OpenEscalations
NextLegalAction
LifecycleSummary
child_work[] completion / accepted_for_parent
```

Rules:

1. projection data is cacheable but disposable;
2. deleting projection cache must not delete canonical history;
3. a stale projection may never authorize a canonical mutation by itself;
4. scheduling revalidates the relevant canonical/external basis through the Command Boundary;
5. ambiguity or contradictory external truth yields a fail-closed projection/status rather than guessing;
6. historical replay uses immutable occurrence/ScheduleBasis facts, not today's current projection.

---

# 9. Scheduler / Policy Engine

The Scheduler determines **what may happen next**, not **what another specialist's answer is**.

Responsibilities:

- consume a fresh generated control projection;
- resolve the next legal internal stage and Primary owner;
- apply Control Autonomy / Gate / Repair policy independently from Proof Assurance;
- determine whether the next occurrence may be automatically scheduled, must be review-guarded, or requires human decision;
- ask the Command Boundary to schedule the new occurrence;
- never directly execute the specialist-owned substantive work;
- stop when an earlier untrusted layer, unresolved escalation, REQUIRED child barrier, stale exact ref, or policy prohibition exists.

Explicit non-ownership:

- no Authority repair;
- no P20 verification judgment;
- no P34 verdict;
- no implementation mutation;
- no semantic cross-owner chaining inside one occurrence.

---

# 10. Orchestration authorization boundary

Current `aegis/skill/decomposition` semantics still prohibit automatic multi-stage substantive Primary-to-Primary continuation without a separately authorized workflow.

Therefore target architecture and current rollout state are deliberately separated.

## 10.1 Architecture capability

The Scheduler and Dispatch Gateway are capable of:

```text
terminal Occurrence A
  -> recompute
  -> create separately owned Occurrence B
  -> dispatch B without a user copy/paste hop
```

## 10.2 Current-authority gate

Until Skill Decomposition / Execution Surface governance explicitly authorizes this workflow, the runtime must operate the cross-Primary step in a compatibility-gated mode:

- it may compute and persist `NextLegalAction`;
- it may prepare an exact next-occurrence candidate only if allowed by current policy;
- it must not auto-dispatch a newly owned Primary occurrence merely because the target architecture supports it.

Once a governed orchestration workflow contract is accepted/supersedes the affected Current boundaries, the same architecture may enable zero-user-turn dispatch without changing stage ownership.

Architecture invariant:

> **Feature enablement is governed by Current Authority; architecture capability is not self-authorization.**

---

# 11. Durable Outbox and Dispatch / Transport Gateway

## 11.1 Commit-before-dispatch

Every substantive dispatch follows:

```text
validate
-> commit StageOccurrence OPEN + exact refs
-> commit outbox entry in the same Control Store transaction
-> dispatch after commit
```

An executor must never start from a transient scheduler decision that was not durably committed.

## 11.2 At-least-once transport

Transport is explicitly at-least-once.

Dispatch retry sends the same occurrence identity and does not create a new semantic attempt.

Representative dispatch envelope:

```yaml
occurrence_ref: <exact STAGE_OCCURRENCE ref>
work_scope_ref: <WorkScopeRef>
control_lane_id: <lane>
stage_span: <accepted stage(s)>
primary_owner: <specialist>
execution_surface: <surface>
trusted_basis_digest: <digest>
policy_digest: <digest>
package_ref: null | <exact P31 package ref>
input_refs: [...]
idempotency_key: <occurrence identity / dispatch attempt metadata>
```

The transport layer may add delivery metadata but may not mutate the semantic payload.

## 11.3 No distributed exactly-once claim

The architecture does not promise exactly-once worker execution.

It guarantees instead:

- exactly one canonical semantic occurrence identity per accepted schedule mutation;
- idempotent duplicate dispatch of that identity;
- compare-and-append protection on accepted progress/terminal mutations;
- semantic retry creates a new StageOccurrence only through an explicit new scheduling operation.

---

# 12. Specialist Execution Surface Adapter

The Execution Surface Adapter converts one durable occurrence into the existing execution-surface contract without stealing stage ownership.

Surface mapping remains compatible with Current Execution Surface semantics:

```text
CONTROL_REASONING
CODE_EXECUTION
CONTROL_REVIEW
CODE_REVERIFY
```

Responsibilities:

- route occurrence to the correct surface/Primary;
- serialize the existing P31 package rather than create a wrapper package truth;
- preserve Task Anchor semantics;
- carry accepted Execution Cursor/navigation state without treating it as Authority;
- carry exact result/materialized refs back to Control Plane;
- enforce that a P34 review surface remains independently owned;
- map surface failures into exact P13 blocker/result inputs without inventing a stage verdict.

## 12.1 Task Anchor / Execution Cursor

Current invariant remains:

```text
Task Anchor != Execution Cursor
```

Target architecture may persist accepted execution-navigation snapshots inside canonical occurrence revisions for sessionless resume, but that storage does not promote the cursor into Authority, Evidence, Gate, Integration, or Project State.

Because this changes how the existing handoff/cursor mechanics are system-managed, implementation enablement requires explicit Execution Surface reconciliation before rollout.

## 12.2 Result return

Before an implementation/reverify occurrence can be terminalized as successfully materialized, the adapter must return exact reviewer-resolvable result identity required by the stage contract, including where applicable:

```text
result_revision
materialized_ref
EvidenceArtifact / ProofEvaluation refs
execution navigation result
```

Agent prose alone is never sufficient evidence.

---

# 13. Project State Adapter

The Project State Adapter is the trust boundary between Control Plane routing and Current project/governance truth.

Read responsibilities:

- resolve Current Authority IDs/status;
- resolve exact Gate Contract / Gate Decision lineage;
- resolve current Gate Decision and blockers;
- resolve Integration-bound historical Gate Decision;
- resolve exact Integration facts;
- expose a reproducible source snapshot/revision token;
- fail closed on invalid/multiple current lineage heads or dangling refs.

Write/non-write boundary:

- the Control Plane does not directly manufacture Gate Decisions or Authority supersession;
- writes to Project State occur only through the existing owning governance/Gate workflows;
- after those owners materialize a new exact Project State fact, the adapter observes it and projection recomputes.

This prevents a second Gate/Authority universe inside the Control Store.

---

# 14. Proof Plane Adapter

The Control Plane reuses the existing Verification Productization architecture rather than embedding another proof engine.

The adapter may invoke/resolve:

- VerificationSpec materialization;
- obligation set identity;
- Evidence Compiler / Evidence materialization;
- ProofEvaluation;
- VerificationSummary;
- Independent Completeness Checker output;
- Review Bundle refs.

Ownership remains:

```text
P20 semantic verification design -> aegis-verification
proof runtime machinery          -> deterministic Proof Plane
P34 Gate acceptance              -> aegis-gate-review
```

The Control Plane uses exact proof refs for routing and package readiness but cannot turn ProofEvaluation into a Gate verdict.

---

# 15. Escalation / Human-Decision Gateway

The Escalation Gateway exposes only decisions that policy says cannot safely remain autonomous.

Responsibilities:

- surface unresolved Escalation records in compact user UX;
- show required decision, owning layer, relevant exact evidence/context refs, and affected WorkScope;
- capture an externally governed decision/ref when the relevant owner resolves the issue;
- schedule a new correctly owned occurrence only after the resolution becomes durable and policy permits continuation.

Explicit non-ownership:

- acknowledging an escalation does not resolve it;
- UI interaction does not mutate the original Escalation;
- the gateway cannot weaken Authority/proof/Gate requirements;
- it does not invent a generic “user approved” override for trust boundaries.

---

# 16. Recovery / Reconciliation Controller

The Recovery Controller restores forward progress after process, transport, or surface interruption without rewriting semantic history.

Responsibilities:

- scan durable OPEN occurrences/outbox state after restart;
- re-dispatch an undelivered or uncertain dispatch using the same occurrence ID;
- reconcile duplicate worker returns idempotently;
- detect stale execution navigation and invoke the existing P33-style reconciliation semantics where the occurrence belongs to repository execution;
- recompute projections after external Project State / Proof / Gate changes;
- detect irreconcilable divergence and fail closed;
- never create a new semantic retry merely because a transport/process retry happened.

Recovery invariant:

> **Process restart is infrastructure recovery, not a new StageOccurrence.**

A genuinely new semantic attempt is created only by the governed scheduling operation that defines retry/repair/reverify/rereview lineage.

---

# 17. High-level runtime lifecycle

Detailed temporal flow belongs to P16, but P14 freezes the ownership boundaries.

## 17.1 Observe / resume

```text
Control Store canonical records
+ Project State exact snapshot
+ Proof / execution exact refs
        ↓
Projection Engine
        ↓
ControlCursor + NextLegalAction + exceptions
```

A conversation/handoff is never the sole source of current state.

## 17.2 Schedule

```text
Scheduler derives candidate
        ↓
Command Boundary validates Current Authority / policy / barriers
        ↓
transaction:
  StageOccurrence OPEN
  + exact ScheduleBasis
  + outbox entry
        ↓
commit
```

## 17.3 Dispatch / execute

```text
Outbox
  -> Transport Gateway
  -> correct specialist surface
  -> specialist owns substantive result
```

## 17.4 Return / terminalize

```text
exact result/materialized refs
  -> Command Boundary
  -> append terminal StageOccurrence revision
  -> recompute projection
```

## 17.5 Continue / repair / escalate

Projection determines one of:

```text
COMPLETE
NEXT_LEGAL_STAGE
REPAIR
REVERIFY
REREVIEW
EARLIER_LAYER_ROUTE
HUMAN_DECISION / ESCALATION
BLOCKED_ENVIRONMENT
```

A different Primary always receives a new StageOccurrence.

---

# 18. REQUIRED child-work architecture

P14 implements, but does not reinterpret, the accepted child semantics.

## 18.1 Parent/child indexing

The Control Store keeps an index from parent WorkScope to immutable ChildWorkBindings for efficient projection/recovery.

The index is derived from canonical bindings; it is not a mutable child-status registry.

## 18.2 REQUIRED barrier

For `parent_gate = REQUIRED`:

- the spawning occurrence may terminalize;
- no later substantive parent occurrence may be scheduled until all uncrossed REQUIRED children are accepted;
- the Command Boundary resolves current exact acceptance support;
- the parent successor stores one immutable RequiredChildAcceptanceBinding per crossed child barrier;
- barrier crossing and successor creation share one Control Store transaction.

## 18.3 Current vs historical truth

Later Gate/Proof truth may cause the current projection to route backward or block future progression.

It never rewrites the RequiredChildAcceptanceBinding that explains why an earlier successor was legal at its historical boundary.

---

# 19. Failure domains and fail-closed behavior

## 19.1 Canonical Control Store unavailable

Effect:

- no new semantic mutation;
- no dispatch from transient scheduler state;
- existing workers may finish externally but return cannot be trusted/accepted until store recovery.

Disposition: `BLOCKED_ENVIRONMENT` or equivalent stage-valid blocker.

## 19.2 Projection cache unavailable/corrupt

Effect:

- discard cache;
- rebuild from canonical records + exact external truth;
- canonical history remains unaffected.

Cache loss is not a trust failure if rebuild succeeds.

## 19.3 Scheduler duplicate/race

Effect:

- only one candidate can win compare-and-append for the lane head;
- losers receive `CONFLICT_RETRY_REQUIRED` / equivalent and recompute;
- no last-write-wins.

## 19.4 Outbox/transport failure

Effect:

- retry the same outbox/occurrence identity;
- do not create another occurrence;
- delivery uncertainty is infrastructure state, not a semantic retry.

## 19.5 Worker crash / timeout

Effect:

- occurrence remains OPEN unless a governed terminal/blocker mutation is committed;
- recovery may redeliver the same occurrence;
- if environment requires human intervention, raise/route an Escalation rather than fabricating success.

## 19.6 Duplicate worker result

Effect:

- same accepted result fingerprint is idempotent replay;
- different result for the same terminalized occurrence is conflict/fail-closed;
- no silent overwrite.

## 19.7 External Project State / Proof source unavailable

Effect:

- if required exact/current truth cannot be resolved with a trustworthy source snapshot, scheduling stops;
- stale local projection never substitutes for unavailable trust truth.

## 19.8 External truth changes after historical commit

Effect:

- recompute current projection/actionability;
- do not rewrite historical StageOccurrence / ScheduleBasis / GateDecision bindings;
- a new downstream action must satisfy current basis independently.

## 19.9 Execution divergence

Effect:

- Execution Surface adapter applies existing Task Anchor / Execution Cursor reconciliation;
- compatible descendant progress may be preserved;
- real divergence fails closed;
- Control Plane must not reset/force-push/discard work to manufacture a matching cursor.

## 19.10 Required child acceptance ambiguity

Effect:

- no parent successor commit;
- return `CHILD_ACCEPTANCE_BASIS_AMBIGUOUS` or `CHILD_ACCEPTANCE_BASIS_CONFLICT`;
- never infer a historical acceptance basis from a current boolean projection.

---

# 20. Process / thread boundaries

P14 freezes logical trust/process boundaries even though P17 will choose platform realization.

## 20.1 Control Plane process domain

May host together initially:

- Command Boundary;
- Canonical Control Store client;
- Projection Engine;
- Scheduler / Policy Engine;
- Recovery Controller;
- API facade.

They may share a process, but correctness must survive process restart.

## 20.2 Dispatch worker domain

Outbox dispatch should run in a restartable worker/thread separate from the canonical commit path.

The semantic transaction ends when outbox state is durable, not when remote execution acknowledges delivery.

## 20.3 Specialist worker domains

Reasoning, code execution, CI/evidence, review, and reverify surfaces are independent failure domains.

No specialist worker is trusted merely because it shares a process or account with the orchestrator.

## 20.4 External truth domains

Project State and Proof Plane remain separately versioned/trusted domains accessed through explicit adapters.

Cross-domain communication always carries exact refs/snapshot identity required by the owning contract.

---

# 21. Security / capability boundaries

The target architecture follows least-authority execution.

- Scheduler may schedule but should not receive arbitrary repository mutation credentials.
- Code execution adapter receives only the package/work scope authorized for that occurrence.
- Review adapter may read exact result/evidence refs but cannot silently mutate implementation or issue another owner's Authority decision.
- Project State adapter may read current trust state; writes require the existing owning governance/Gate operation.
- Proof adapter may materialize proof artifacts but cannot issue P34 PASS.
- destructive or irreversible external actions remain HUMAN_DECISION unless separately governed.
- actor identity from P13 operation envelopes must remain auditable across API/worker boundaries.

---

# 22. Observability and auditability

Operational observability is required but is not a second semantic history.

Every trace/log/metric should be correlatable by:

```text
WorkScopeRef
control_lane_id
StageOccurrence ID
operation_request_id
dispatch attempt ID
package ref
```

Minimum operational signals:

- mutation commit/reject/conflict counts;
- projection rebuild/failure counts;
- scheduler decisions and blocked reasons;
- outbox age / retry count;
- worker delivery/return latency;
- OPEN occurrence age;
- unresolved Escalation age;
- adapter freshness / source snapshot age;
- repair/reverify/rereview counts;
- fail-closed reason-code distribution.

Audit explanations must be reconstructable from canonical exact refs even if operational logs are lost.

---

# 23. User-facing product boundary

Normal user UX consumes generated projection only.

Default surface remains:

```text
DEFINE / BUILD / PROVE / SHIP
status
what changed
trusted result
open exceptions
next human decision, if any
```

Internal details such as P-stage, WorkScope IDs, occurrence refs, SHAs, evidence digests, repair lineage, and routing history remain progressively discloseable for audit/debugging.

The architecture does not require the user to copy package/source/result/materialized refs between surfaces.

---

# 24. Authority-impact and rollout reconciliation

P14 separates **target architecture** from **permission to enable it under Current Authority**.

## 24.1 Skill Decomposition impact

Target architecture supports zero-user-turn scheduling across separately owned StageOccurrences.

Current Skill Decomposition still prohibits automatic multi-stage substantive continuation without a separately authorized workflow.

Required before rollout:

- explicit governance reconciliation of the orchestration workflow;
- preservation of exactly one Primary per StageOccurrence;
- preservation of blocked short-circuit semantics;
- no `Primary A -> Primary B` ownership transfer inside one occurrence.

P14 does not perform that supersession.

## 24.2 Execution Surface impact

Target architecture makes handoff transport system-managed and persists accepted navigation snapshots for sessionless resume.

Required before rollout:

- explicit reconciliation confirming this remains navigation/control metadata;
- Task Anchor != Execution Cursor preserved;
- Codex remains an execution surface, not the Control Plane loop controller;
- exact reviewer-accessible result materialization remains mandatory.

P14 does not supersede Current Execution Surface Authority.

## 24.3 Project State impact

Core P14 does **not** require Project State to become the Control Store.

Therefore no semantic Project State replacement is required merely to store StageOccurrences.

Possible future additions such as publishing a pointer/summary of active Control Work into Project State would be a separate governed change and are not required for this architecture.

## 24.4 Proof Plane impact

No Proof Plane topology redesign is required.

Control Plane integrates through adapters/exact refs and preserves:

- independent Completeness Checker;
- Evidence Compiler / materialization;
- ProofEvaluation != Gate;
- P34 independent ownership.

---

# 25. Architecture invariants

A conforming P14 implementation must preserve all of the following:

1. Canonical Control Store owns only Control Plane canonical truth.
2. Project State remains owner of Authority/Gate/Integration truth.
3. Proof Plane remains owner of Verification/Proof/Evidence truth.
4. P34 remains the sole official Gate owner.
5. VerificationBoundImplementationPackage is the existing strengthened P31 package truth, not a wrapper authority.
6. one WorkScope has one primary Control Lane in v0.2.
7. one substantive StageOccurrence has exactly one Primary owner.
8. scheduler/orchestrator never issues specialist substantive verdicts.
9. cross-owner continuation creates a new occurrence after a durable terminal boundary.
10. current Skill Composition Authority gates whether cross-owner auto-dispatch may be enabled.
11. all substantive dispatch is commit-before-dispatch.
12. canonical mutation + outbox commit is atomic inside the Control Store.
13. transport is at-least-once; duplicate transport does not create semantic retry.
14. correctness uses compare-and-append; no last-write-wins at trust boundaries.
15. lane locks/leases are optional coordination aids, never the truth oracle.
16. independent lanes may progress concurrently; no project-wide global lock is required.
17. child spawn is one atomic Control Store mutation.
18. REQUIRED-child barrier crossing and parent successor creation are one atomic Control Store mutation.
19. historical child acceptance uses immutable RequiredChildAcceptanceBinding, not current projection.
20. generated projections are disposable/rebuildable and cannot override canonical truth.
21. stale/unresolvable external truth blocks scheduling.
22. external-source snapshots/refs are pinned sufficiently for replay; cross-system exactly-once is not claimed.
23. Execution Cursor remains navigation metadata only.
24. process restart / dispatch retry does not create a new StageOccurrence.
25. semantic repair/retry/reverify/rereview creates new occurrences only through governed P13 operations.
26. no Control Plane Finding/Gate/Proof/Authority duplicate store is introduced.
27. unresolved semantic/product/risk/irreversible decisions escalate rather than being guessed.
28. user-facing simplicity is a projection over full durable mechanics, not deletion of those mechanics.

---

# 26. P15 handoff boundary

P14 intentionally leaves these decisions to P15 Module Design / P16-P17:

- concrete module/package names;
- Control Store persistence implementation and schema/index realization;
- exact lane-head/CAS API;
- outbox/inbox table or log realization;
- scheduler worker partitioning;
- adapter interface method signatures;
- exact source-snapshot token representation per external system;
- dispatch protocol and worker-return schema realization;
- projection cache structure;
- reconciliation polling/subscription strategy;
- authentication/credential plumbing;
- API/CLI/UI transport;
- local vs hosted deployment packaging;
- performance targets/backpressure limits.

P15 must preserve this ownership/topology and may not collapse the Control Store into Project State, turn a queue into semantic truth, or move Gate/Proof/Authority ownership into the orchestrator.

---

# 27. P14 disposition

```text
P14 System Architecture
  -> READY / MATERIALIZED — Draft/Proposed
```

Architecture basis is pinned to:

```text
PR #26 modeling head
f29c4da3698038e0174e4380707fa618b03c40b2

P21 Authority Review #3
5062616510
PASS / ACCEPTED_FOR_DOWNSTREAM
```

The next architecture-family stage after this artifact is:

```text
P15 Module Design
```

P15 must consume the exact materialized P14 head and fail closed if either the accepted modeling basis or this P14 artifact changes unexpectedly.

Do not begin P20/P30/P32 implementation from P14.
