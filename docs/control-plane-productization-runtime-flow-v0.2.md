# Aegis Control Plane Productization v0.2 — P16 Runtime Data Flow

Status: **Draft / Proposed Authority — P16 Runtime Data Flow**

Scope: `aegis/control-plane-productization/runtime-flow`

Exact upstream basis:

- accepted P10-P13 modeling head: `f29c4da3698038e0174e4380707fa618b03c40b2`
- P21 Authority Review #3: `5062616510`
- modeling verdict: `PASS / ACCEPTED_FOR_DOWNSTREAM`
- P14 System Architecture materialized head: `54999ce91ff4f35455916c33b4f7891e2b6b8d4d`
- P15 Module Design materialized head: `12f75bc1938406d8d0cadca4d343fcdb95fdbfb9`
- Current Execution Surface Authority: `docs/execution-surface-contract-v0.2.md`

P16 consumes those exact boundaries. It does not reopen P10-P15, change Current Skill Decomposition / Execution Surface Authority, or begin implementation.

---

# 1. P16 objective

Freeze the **time-ordered runtime choreography** of the accepted Control Plane architecture.

P14 established subsystem ownership. P15 established module ownership. P16 now answers:

> **When a control fact changes, in what exact order are canonical state, external truth, projection, policy, scheduling, mutation, outbox, dispatch, execution return, terminalization, recovery, and continuation handled?**

The target runtime loop is:

```text
observe trigger
  -> re-read canonical control truth
  -> resolve exact current external truth
  -> recompute projection
  -> evaluate policy / rollout authorization
  -> derive transient schedule candidate
  -> revalidate through the single mutation boundary
  -> CAS + atomic canonical commit
  -> durable outbox when dispatch is permitted
  -> dispatch after commit
  -> specialist execution
  -> exact result materialization
  -> result reconciliation
  -> terminal canonical commit
  -> recompute
  -> continue / wait / repair / escalate / complete
```

Every arrow crosses an explicit ownership or trust boundary.

Core runtime rule:

> **Triggers are hints; canonical records and exact external truth are the source of runtime decisions.**

A callback, queue message, UI event, scheduler wakeup, wall-clock timeout, or process memory state never authorizes a canonical transition by itself.

---

# 2. Non-goals

P16 does not:

- redefine `WorkScopeRef`, `StageOccurrence`, `VerificationBoundImplementationPackage`, `Escalation`, `ScheduleBasis`, `RequiredChildAcceptanceBinding`, or any accepted P13 operation;
- change the P14 topology or P15 module boundaries;
- create a second canonical writer;
- turn projection, scheduler, dispatch, recovery, queue state, logs, or UI state into semantic truth;
- create a mutable `ControlLane`, `ChildWork`, `barrier_consumed`, `child_accepted`, `RepairAttempt`, or `ChatSession` aggregate;
- introduce a `CANCELLED` lifecycle status;
- create a second Gate or allow ProofEvaluation to become Gate truth;
- make a transport acknowledgement equivalent to substantive completion;
- claim distributed exactly-once execution;
- infer semantic retry from timeout, crash, duplicate delivery, or restart;
- choose database, queue, broker, RPC, callback, polling, subscription, SDK, process, ABI, deployment, or credential technology; P17 owns platform realization;
- choose load thresholds, SLOs, queue depth limits, timeout budgets, or retention values; P18 owns measurable engineering budgets;
- supersede Current Skill Decomposition / Execution Surface Authority;
- begin P17, P20, P30, P31, P32, or implementation work.

---

# 3. Frozen runtime invariants

A conforming P16 runtime preserves all of the following.

1. `control-mutation` is the only Control Plane module that authors canonical P13 writes.
2. `control-store` provides transaction/CAS/idempotency/outbox mechanics only.
3. `control-projection` is deterministic, read-only, rebuildable, and disposable.
4. `control-policy` evaluates authorization/policy but authors no canonical truth.
5. `control-scheduler` produces transient candidates only.
6. `control-dispatch` consumes committed outbox work only.
7. `control-recovery` uses normal module interfaces and has no privileged write bypass.
8. StageOccurrence is committed `OPEN` before substantive dispatch.
9. A permitted semantic scheduling commit and its outbox creation are atomic.
10. Delivery acknowledgement is outside the semantic transaction.
11. Transport is at-least-once.
12. Duplicate delivery of one committed occurrence is not semantic retry.
13. A new semantic retry/repair/reverify/rereview is a new governed StageOccurrence.
14. Lane head/version CAS is the concurrency truth boundary.
15. Locks/leases are optional coordination only.
16. External Authority/Proof/Gate/Integration/Execution truth remains externally owned.
17. External snapshot tokens/exact refs are validated and pinned; there is no cross-system distributed transaction claim.
18. Historical transitions replay their pinned basis; current projection uses current exact truth.
19. REQUIRED-child barrier crossing is atomic with successor creation and exact acceptance binding materialization.
20. `Task Anchor != Execution Cursor` remains controlling.
21. Current rollout authorization may prohibit automatic cross-Primary progression even when `NextLegalAction` is derivable.
22. Operator pause/backpressure may defer future action but never rewrite semantic history.
23. Terminalization and successor scheduling are separate durable boundaries.
24. A Primary never substantively executes the next Primary's stage while terminating its own occurrence.

---

# 4. Runtime truth surfaces

P16 distinguishes four runtime surfaces.

## 4.1 Canonical Control Plane truth

Owned through `control-mutation` + `control-store`:

- WorkScope/lane binding;
- StageOccurrence immutable revisions;
- P31 package immutable revisions;
- Escalation immutable record;
- ScheduleBasis / RequiredChildAcceptanceBinding;
- semantic operation idempotency records;
- canonical lane head/version;
- durable outbox record tied to an accepted scheduling mutation.

## 4.2 External semantic truth

Resolved through `control-trust-resolver` + stable ports/adapters:

- Project State Authority / GateDecision / Integration;
- Proof Plane VerificationSpec / ProofObligation / Evidence / ProofEvaluation;
- externally owned Finding/classification truth;
- Execution Surface materialized result and accepted repository position;
- externally governed human/product decision refs.

## 4.3 Derived control state

Owned by `control-projection` as disposable calculation:

- ControlCursor;
- macro phase;
- child completion / acceptance;
- repair lineage;
- open escalation state;
- NextLegalAction;
- lifecycle summary.

## 4.4 Operational state

Examples:

- scheduler wakeups;
- dispatch leases;
- delivery attempts/receipts;
- adapter rate-limit state;
- process health;
- retry timers;
- active operator pause/resume directive;
- metrics/traces/logs;
- projection cache entries.

Operational state may control **when** the runtime tries again. It never changes **what semantic history is true**.

---

# 5. Trigger model

Runtime work may be triggered by:

```text
user/product request
canonical mutation commit
outbox availability
worker callback or poll/subscription observation
external Authority/Gate/Proof/Integration change
human decision arrival
operator pause/resume
recovery sweep
process startup
periodic reconciliation
```

A trigger only asks the runtime to inspect current truth.

Canonical handling is always:

```text
trigger
  -> read/reconcile
  -> derive
  -> validate
  -> maybe mutate
```

Never:

```text
trigger payload
  -> trust payload blindly
  -> mutate canonical state
```

If the trigger cannot be correlated to an exact WorkScope/lane/occurrence/external ref, processing fails closed or remains operationally pending until correlation is available.

---

# 6. Standard transition ledger

Every semantic transition in P16 can be audited using the following ledger.

| Field | Required runtime answer |
|---|---|
| Trigger | What caused reevaluation? |
| Module owner | Which P15 module owns this step? |
| Canonical read | Which exact Control Store records/versions are read? |
| External read | Which externally owned exact refs/snapshot tokens are resolved? |
| Validation boundary | What must be true before mutation? |
| Canonical mutation | Which accepted P13 operation, if any, is invoked? |
| Transaction boundary | Which records must commit all-or-none? |
| Outbox behavior | Is an outbox entry created, retained, retried, or absent? |
| Dispatch behavior | What exact committed occurrence may be delivered? |
| Result return | How is an exact durable result reconciled? |
| Retry/recovery | What repeats without changing semantic identity? |
| Fail-closed disposition | What happens when exactness/trust/concurrency cannot be established? |

No flow may leave these ownership questions implicit at a trust-sensitive boundary.

---

# 7. Normal happy path

This flow applies when the next action is semantically legal **and current policy/rollout Authority permits the requested scheduling/dispatch mode**.

```text
observe
  -> project
  -> policy
  -> schedule candidate
  -> mutation validation
  -> OPEN + outbox commit
  -> dispatch
  -> execute
  -> materialize result
  -> terminalize
  -> recompute
  -> continue / complete
```

## 7.1 Temporal trace

| Step | Owner | Reads / validation | Canonical write / transaction | Outbox / dispatch | Failure behavior |
|---|---|---|---|---|---|
| H1 Observe | `control-facade` or `control-recovery` | correlate WorkScope/lane/occurrence; trigger is non-authoritative | none | none | uncorrelated trigger does not mutate |
| H2 Read canonical | `control-store` via reader | lane head, latest occurrence/package/escalation/idempotency facts | none | none | missing/inconsistent canonical refs fail closed |
| H3 Resolve trust | `control-trust-resolver` | exact Project State / Proof / Gate / execution facts + snapshot tokens | none | none | stale/ambiguous external truth is explicit |
| H4 Project | `control-projection` | exact canonical history + exact current trust snapshots | projection/cache only | none | contradictory derivation -> fail-closed projection |
| H5 Policy | `control-policy` | projection + exact policy/current rollout Authority | none | none | missing policy -> no autonomous progression |
| H6 Candidate | `control-scheduler` | projection + PolicyDecision | none; transient `ScheduleCandidate` only | none | no legal/authorized candidate -> `NoAction` |
| H7 Revalidate | `control-mutation` | re-read expected lane/record heads; re-resolve required external truth; verify snapshot freshness; idempotency | no write until all guards pass | none | stale candidate/CAS/trust -> reject/recompute |
| H8 Schedule commit | `control-mutation` + `control-store` | exact expected-state guards | `SCHEDULE_STAGE_OCCURRENCE`: OPEN r1 + idempotency result + lane-head advance + permitted outbox, all-or-none | outbox durable in same transaction | transaction failure -> no occurrence and no outbox |
| H9 Deliver | `control-dispatch` | committed outbox + exact occurrence envelope only | delivery metadata only; no semantic record | at-least-once dispatch after commit | retry same occurrence; never invent another |
| H10 Execute | specialist execution surface | exact package/input/TrustedBasis contract from committed occurrence | Control Store none | execution outside semantic DB tx | specialist owns substantive work/result |
| H11 Materialize result | execution/evidence owner | produce reviewer-resolvable durable exact result/evidence refs | external owner persists its own truth | return/callback is only a signal | executor prose/local state is insufficient when materialization required |
| H12 Reconcile return | execution adapter + trust resolver | resolve exact occurrence + materialized result + current accepted execution position | none | no new dispatch required | unresolved/mismatched result fails closed |
| H13 Terminalize | `control-mutation` + `control-store` | exact latest OPEN revision + exact result refs + current operation guards | `TERMINATE_STAGE_OCCURRENCE`: one terminal revision + idempotency; escalation companion if applicable | **no successor outbox here** | CAS conflict -> re-read; invalid result -> reject |
| H14 Recompute | `control-projection` | now-terminal canonical history + current external truth | projection only | none | ambiguity stops progression |
| H15 Continue | policy + scheduler + mutation | fresh state, not stale H6 candidate | separate later schedule transaction if permitted | new outbox belongs to new occurrence only | blocked/complete/escalate according to current truth |

## 7.2 Terminal boundary rule

Even on the clean path:

```text
Occurrence A terminal commit
!=
Occurrence B schedule commit
```

The correct boundary is:

```text
A TERMINAL durable
  -> recompute from durable truth
  -> policy
  -> derive B candidate
  -> independently validate B
  -> B OPEN durable
```

If the runtime crashes after A terminalizes and before B schedules, A remains valid history. Recovery resumes from A; A is never rolled back merely because B did not start.

---

# 8. Schedule transaction and outbox boundary

A scheduling transition that is permitted to dispatch uses one Control Store transaction:

```text
validate operation request + request idempotency
validate expected lane head / predecessor
validate exact WorkScope/package relationships
validate TrustedBasis + current external snapshots
validate PolicyBinding / rollout authorization
validate REQUIRED-child barriers when applicable
construct immutable ScheduleBasis
append StageOccurrence revision 1 / OPEN
advance lane head
append semantic idempotency result
append outbox record
COMMIT
```

Only after commit:

```text
outbox worker may claim
  -> dispatch exact immutable semantic envelope
```

The remote dispatch call is never inside the semantic transaction.

Consequences:

- store rollback before commit means neither occurrence nor outbox exists;
- process death after commit cannot lose dispatch intent because outbox is durable;
- remote acknowledgement cannot make an uncommitted occurrence valid;
- a dispatch worker cannot change owner, scope, package, basis, inputs, or stage span;
- delivery metadata may change independently without changing StageOccurrence meaning.

---

# 9. Scheduler race

Two scheduler instances may legitimately observe the same parent boundary.

Example:

```text
Scheduler A -> candidate S1
Scheduler B -> candidate S1 or conflicting S2
```

Both candidates are transient.

## 9.1 Temporal trace

1. Both read the same lane head `L@N`.
2. Both independently resolve current external truth and derive candidates.
3. Both submit a normal P13 scheduling request through `control-mutation`.
4. Mutation revalidates `L@N` and all expected-state guards.
5. The first transaction to compare-and-append succeeds and advances the lane head to `L@N+1` with one OPEN occurrence and its outbox when permitted.
6. The second transaction sees that `L@N` is no longer current.
7. The loser returns `CONTROL_LANE_SCHEDULE_CONFLICT` / `CONFLICT_RETRY_REQUIRED`.
8. The loser creates **no occurrence and no outbox entry**.
9. The loser discards the stale candidate, re-reads canonical truth, recomputes, and normally observes the winner's occurrence.

Correctness invariant:

> **The CAS winner determines canonical scheduling; scheduler arrival order, lock ownership, and candidate timestamp do not.**

If the two candidates differ semantically, the loser never force-applies its choice after conflict. It must re-derive from the winner's new durable boundary.

---

# 10. Duplicate delivery

At-least-once transport means the same committed occurrence may be delivered more than once.

```text
same occurrence_ref
same WorkScope
same stage span
same owner
same package/input refs
same TrustedBasis/policy digests
```

is one semantic attempt.

## 10.1 Temporal trace

1. `control-dispatch` reads a committed outbox entry.
2. Delivery attempt D1 is sent.
3. Ack is lost, dispatcher crashes, lease expires, or delivery state remains uncertain.
4. Recovery/dispatcher reads the same outbox entry again.
5. Delivery attempt D2 sends the **same semantic envelope** with a new transport attempt identity if the transport needs one.
6. `adapter-execution-surface` / receiver deduplicates or reconciles by exact occurrence identity and execution contract.
7. If work already started, the receiver resumes/returns current state for that occurrence.
8. If work already completed and exact result was materialized, the receiver returns/re-resolves that same result.
9. No new StageOccurrence is allocated merely because D2 exists.

If the execution surface cannot determine whether the exact occurrence already started/completed, the runtime enters execution reconciliation / delivery-uncertain handling. It does **not** create a second semantic attempt to make uncertainty disappear.

---

# 11. Worker crash / timeout / disappearing executor

An OPEN StageOccurrence is durable authorization history even if its executor disappears.

A timeout is an operational observation, not automatically a substantive failure.

## 11.1 Reconciliation sequence

```text
OPEN occurrence
  -> worker heartbeat/callback missing
  -> control-recovery wakes
  -> read exact OPEN occurrence/latest revision
  -> query delivery state
  -> resolve execution position
  -> resolve materialized result if one exists
  -> classify recoverable infrastructure state
```

Allowed recovery branches:

### A. Confirmed not started / safe redelivery

- re-deliver the **same occurrence**;
- retain identical semantic envelope;
- update only delivery metadata;
- no new occurrence.

### B. Started or progress exists

- reconcile accepted execution position;
- apply P33 semantics when repository-backed execution requires them;
- optionally append an accepted execution-navigation checkpoint through `RECORD_EXECUTION_PROGRESS`;
- resume same occurrence.

### C. Exact materialized result already exists

- resolve that exact result through the execution adapter;
- validate it against the same occurrence/package/input contract;
- terminalize the existing occurrence if still OPEN and valid.

### D. Delivery/execution state genuinely uncertain

- keep the semantic occurrence unchanged;
- report/observe `DELIVERY_UNCERTAIN` operationally;
- retry reconciliation according to P18 budgets;
- do not convert uncertainty into a new semantic attempt.

### E. Owning execution contract proves unrecoverable environment failure

Only then may the normal mutation boundary truthfully terminalize with the smallest applicable existing blocking status, typically `BLOCKED_ENVIRONMENT` and an exact reason such as execution divergence/environment failure.

`control-recovery` itself cannot decide implementation correctness, Gate truth, or invent a terminal result from timeout alone.

---

# 12. Late, duplicate, and conflicting result returns

Worker return messages are signals. Canonical terminal history is decided only by the mutation boundary after exact result reconciliation.

## 12.1 Identical duplicate result

If the occurrence is already terminal and the new return is semantically identical to the existing terminal payload/exact produced refs:

```text
existing terminal revision
+ equivalent duplicate request
  -> idempotent replay of existing result
```

No new revision is written.

If the same `operation_request_id` and fingerprint are replayed, the idempotency record returns the prior semantic result directly.

## 12.2 Result after timeout or re-dispatch

If the same occurrence was re-delivered but remains OPEN:

1. resolve the returned materialized result;
2. re-read latest OPEN occurrence revision;
3. if execution navigation advanced, use the latest accepted revision as the terminalization guard;
4. validate exact package/input/result identity;
5. append the one terminal revision.

The fact that a timeout happened earlier does not make the result late in the semantic sense.

## 12.3 Result after terminalization

If the occurrence is already terminal:

- exact duplicate -> idempotent existing result;
- different terminal payload/result -> `OCCURRENCE_ALREADY_TERMINAL` / conflict;
- the later message cannot rewrite the terminal revision;
- arrival time never selects the winner.

If the conflict indicates a meaningful external execution integrity problem, that problem is surfaced as a new current blocker/finding/escalation under its owning contract. The old terminal record remains immutable.

## 12.4 Conflicting concurrent terminal requests

Two different terminal requests racing from the same OPEN revision cannot both commit.

CAS admits one terminal revision. The other re-reads and either resolves as an exact duplicate or fails closed as conflict.

---

# 13. Restart / crash recovery matrix

P16 requires restart recovery from durable truth rather than process memory.

| Crash point | Durable truth after crash | Recovery action | Forbidden behavior |
|---|---|---|---|
| Before schedule transaction commits | no new occurrence/outbox | discard transient candidate; recompute | dispatch transient work |
| After OPEN + outbox commit, before dispatch | OPEN occurrence + pending outbox | dispatcher claims durable outbox and sends same occurrence | allocate replacement occurrence |
| After dispatch, before ack persistence | OPEN occurrence + outbox with uncertain delivery metadata | query/retry same occurrence | treat missing ack as semantic failure |
| After worker started, before accepted progress checkpoint | OPEN occurrence; external execution may have advanced | resolve execution position; use P33 reconciliation; append progress only if accepted | infer progress from logs alone |
| After worker materialized result, before Control Plane accepts return | OPEN occurrence + external exact result | resolve exact result and terminalize same occurrence if valid | require worker to re-execute simply because callback was lost |
| After terminal commit, before projection refresh | terminal canonical history; stale/missing projection cache | rebuild projection from canonical + current external truth | roll back terminal commit |
| After projection refresh, before next scheduling | terminal history + derived NextLegalAction | re-run policy/scheduler/mutation from fresh truth | trust cached candidate without revalidation |
| After successor OPEN commit, before successor dispatch | successor OPEN + outbox | dispatch successor from durable outbox | merge predecessor/successor into one retry |

Startup order is conceptually:

```text
start process
  -> establish store connectivity
  -> reconcile pending outbox
  -> reconcile aged/open occurrences
  -> rebuild/invalidate projections as needed
  -> resume scheduler from canonical heads
```

Exact process topology is deferred to P17.

---

# 14. P33 repository resume flow

Repository-backed execution must preserve the Current Execution Surface invariant:

```text
Task Anchor != Execution Cursor
```

The stable package `task_anchor` authorizes the required ancestor relation. The moving accepted `execution_cursor` records navigation only.

## 14.1 Resume trigger

`control-recovery` or `control-facade` requests reconciliation of an OPEN repository-backed occurrence.

Reads:

- exact occurrence and package revision;
- package `task_anchor`;
- latest accepted `execution_navigation`, if any;
- observed execution branch/ref/HEAD through `ExecutionSurfacePort.resolve_execution_position`.

The adapter/owning P33 execution contract classifies one of four states.

## 14.2 `EXACT_CURSOR`

```text
observed HEAD == accepted execution_cursor.revision
```

Flow:

- preserve package/task anchor;
- resume from cursor `next_action`;
- no semantic mutation is required merely to recognize equality;
- later accepted progress may append an OPEN revision via `RECORD_EXECUTION_PROGRESS`.

## 14.3 `DESCENDANT_CURSOR`

```text
execution_cursor.revision is ancestor of observed HEAD
```

Flow:

1. inspect only the descendant delta under the owning P33 contract;
2. preserve verified valid work;
3. reconcile completed/pending obligations;
4. establish the first incomplete verified step;
5. if the new position is accepted, submit `RECORD_EXECUTION_PROGRESS`;
6. mutation verifies that only `execution_navigation` changes and all frozen start facts remain identical;
7. CAS appends the next OPEN revision.

Already-completed work is not replayed solely because HEAD advanced.

## 14.4 `ANCHOR_DESCENDANT_WITHOUT_CURSOR`

No accepted cursor exists, but:

```text
task_anchor.revision is ancestor of observed HEAD
```

Flow:

- reconcile package obligations against the descendant state;
- do not assume descendant commits are automatically authorized just because ancestry holds;
- once the owning P33 contract establishes the accepted position, append the first execution-navigation checkpoint through `RECORD_EXECUTION_PROGRESS`;
- continue from the first incomplete verified step.

## 14.5 `DIVERGED`

If neither accepted cursor nor required task-anchor ancestry can be established, history is incompatibly rewritten, or observed repository state contradicts Authority/scope:

```text
DIVERGED
```

Flow:

- no progress checkpoint is committed;
- no force reset/force push/discard is performed by recovery;
- return reason `BLOCKED_EXECUTION_DIVERGENCE` or the more specific valid Authority/environment blocker;
- map any terminalization, if the owning contract requires one, onto the smallest existing P12 terminal status (`BLOCKED_AUTHORITY` or `BLOCKED_ENVIRONMENT` as appropriate);
- never invent a new baseline.

Historical expected-HEAD mismatch alone is not divergence when the accepted ancestor relation holds.

---

# 15. REQUIRED child fan-out / join

REQUIRED child work uses independent WorkScopes and lanes while imposing one deterministic parent continuation barrier.

```text
parent occurrence P
  -> spawn REQUIRED child C1
  -> spawn REQUIRED child C2
  -> P may terminalize

C1 lane -> progresses independently
C2 lane -> progresses independently

parent lane
  X no substantive successor after P
    while any uncrossed REQUIRED child is unaccepted

all REQUIRED children completed + accepted
  -> materialize exact acceptance bindings
  -> atomically schedule parent successor S
```

## 15.1 Child spawn transaction

For each new child schedule accepted by current policy/rollout Authority, `control-mutation` validates:

- new child WorkScope identity;
- new child lane identity;
- exact parent WorkScope;
- exact `spawned_by_occurrence_ref` belonging to the parent;
- acyclic parent relationship;
- exact acceptance-contract refs;
- child stage/Primary ownership;
- semantic scope authorization;
- expected parent occurrence revision when required to prevent stale spawn.

One atomic transaction establishes:

```text
new WorkScopeRef
+ immutable ChildWorkBinding
+ one-to-one child lane mapping
+ child StageOccurrence revision 1 / OPEN
+ semantic idempotency result
+ outbox if dispatch is currently permitted
```

A partial child relationship cannot exist.

Different child lanes may then progress concurrently.

## 15.2 Parent behavior while children run

The spawning parent occurrence may finish truthfully.

For REQUIRED children, the barrier applies to the **next substantive parent-lane occurrence after the spawning occurrence**.

Projection derives child state from canonical history + current external truth:

```text
completed
accepted_for_parent
```

No mutation writes those booleans.

## 15.3 Join / barrier crossing

When the parent scheduler proposes successor `S`:

1. `control-projection` identifies all uncrossed REQUIRED child barriers.
2. `control-trust-resolver` resolves exact child completion occurrence, acceptance contracts, result/evidence/proof/Gate/decision facts, and snapshot freshness for every child.
3. `control-scheduler` may derive `S` only as a transient candidate.
4. `control-mutation` revalidates **every** uncrossed REQUIRED child.
5. For each accepted child, mutation constructs one exact `RequiredChildAcceptanceBinding`.
6. Each binding's facts are also pinned into successor TrustedBasis/input refs according to the accepted modeling contract.
7. Mutation validates successor basis/package/owner/current policy.
8. One atomic transaction commits:

```text
all required acceptance bindings inside S.ScheduleBasis
+ S StageOccurrence revision 1 / OPEN
+ lane-head advance
+ idempotency result
+ permitted outbox
```

If any child is incomplete, unaccepted, stale, ambiguous, or conflicting:

```text
REQUIRED_CHILD_WORK_NOT_ACCEPTED
CHILD_ACCEPTANCE_BASIS_AMBIGUOUS
CHILD_ACCEPTANCE_BASIS_CONFLICT
```

as applicable, and **no successor mutation occurs**.

There is no separate barrier-consumed write. Historical crossing is derived only from `S.ScheduleBasis.required_child_acceptance_bindings`.

## 15.4 Multiple REQUIRED children

The successor binds all uncrossed REQUIRED children in the same accepted scheduling boundary. Partial join cannot advance the parent lane.

---

# 16. NON_BLOCKING child flow

`parent_gate = NON_BLOCKING` means the child relationship remains independently visible/auditable but does not itself prohibit parent continuation.

Flow:

1. child spawn uses the same atomic child materialization rules;
2. child lane progresses independently;
3. parent projection includes the child state for visibility;
4. parent scheduler does **not** treat that child as a REQUIRED barrier;
5. parent successor `ScheduleBasis.required_child_acceptance_bindings` does not include the NON_BLOCKING child merely because it exists;
6. parent continuation still must satisfy all other Authority/Proof/Gate/policy constraints;
7. later child completion/acceptance may change current summary/projection but does not retroactively alter the already authorized parent transition.

NON_BLOCKING is not permission for the parent to steal child ownership or weaken the child's own lifecycle requirements.

---

# 17. Repair -> reverify -> rereview loop

A finding-driven loop remains a sequence of separately owned durable occurrences.

```text
finding
  -> exact classification / owning-layer determination
  -> repair policy + budget check
  -> repair occurrence
  -> exact repaired result
  -> reverification occurrence when required
  -> fresh evidence/proof result
  -> independent rereview occurrence when required
  -> new official Gate Decision
  -> recompute
```

## 17.1 Finding/classification boundary

Finding and classification truth remain externally owned by the relevant Gate/review/classification contracts.

The Control Plane consumes exact refs/support. It does not infer that every failure is an implementation defect.

If the earliest untrusted layer is Authority/product/semantic design rather than implementation, routing goes to that owner instead of creating an implementation repair attempt.

## 17.2 Repair scheduling

`control-policy` validates:

- repair class allowed;
- finite attempt budget remaining;
- scope remains authorized;
- no Authority/product/semantic change is being hidden as repair;
- whether reverification and fresh independent rereview are required;
- current Control Autonomy/rollout authorization.

`control-scheduler` proposes the repair only transiently.

`control-mutation` applies `SCHEDULE_REPAIR_OCCURRENCE` and validates:

- exact finding ref;
- root occurrence;
- previous attempt ref;
- contiguous `attempt_ordinal`;
- repair policy digest;
- package/scope/current basis;
- lane/CAS guards.

The new repair occurrence and its permitted outbox commit atomically.

No prior occurrence is transformed into a repair attempt.

## 17.3 Reverification

After the repair materializes an exact result and terminalizes:

```text
recompute
  -> policy says reverify required
  -> SCHEDULE_REVERIFICATION_OCCURRENCE
```

Reverification is a fresh occurrence owned by the appropriate specialist/proof execution boundary.

It produces fresh exact Evidence/Proof truth under the Proof Plane contract. Old evidence is not rewritten.

## 17.4 Independent rereview

If Gate/review policy requires a fresh independent review:

```text
fresh repaired result/evidence
  -> SCHEDULE_REREVIEW_OCCURRENCE
  -> P34-owned review occurrence
  -> new external immutable Gate Decision
```

P34 remains sole official Gate owner.

A previous Gate Decision is never mutated in place.

## 17.5 Loop termination

At every boundary the system recomputes from committed history.

Loop stops when:

- PASS/acceptable fresh Gate truth permits continuation;
- a non-repairable earlier layer is identified;
- repair budget is exhausted;
- required evidence cannot be produced;
- human decision is required;
- current rollout policy blocks automatic cross-Primary continuation.

Committed prior repair/reverify/rereview history remains even when the loop stops.

---

# 18. Human escalation flow

Escalation is a durable interruption, not a mutable ticket and not a generic approval override.

## 18.1 Raise

When an occurrence reaches an unresolved decision that cannot be closed automatically:

1. owner produces the exact blocker/question/category/owning layer required by existing contracts;
2. `control-mutation` validates that escalation is appropriate;
3. in one semantic transaction:

```text
create immutable Escalation revision 1
+ append occurrence terminal revision outcome=ESCALATED
+ bind raised_escalation_ids
+ idempotency result
```

4. no successor is scheduled as part of that transaction;
5. projection now derives the escalation as open;
6. scheduler stops automatic continuation while the unresolved escalation blocks the lane.

## 18.2 Surface to user

`adapter-human-decision` may publish a user-facing view containing only the actual decision needed plus expandable evidence/context.

Publishing/acknowledging the UI notification is not semantic resolution.

No input such as:

```text
approved = true
```

may bypass Authority/Proof/Gate requirements unless an existing governed contract explicitly defines such a decision and the exact durable external decision ref is available.

## 18.3 Resolve

When the human/product/governance system materializes an exact decision:

1. `HumanDecisionPort.resolve_decision` returns an exact externally governed decision ref + snapshot token;
2. projection/trust resolver recompute current actionability;
3. a separately owned resolving occurrence is scheduled under normal routing/current rollout rules;
4. that occurrence consumes the escalation ID + exact decision ref in its inputs/TrustedBasis where applicable;
5. the owning specialist performs the required substantive responsibility;
6. `RECORD_ESCALATION_RESOLUTION` records the resolving occurrence's terminal revision with `resolved_escalation_ids`;
7. the original Escalation record remains immutable;
8. projection derives it as resolved and may derive later continuation.

A materially different later decision does not rewrite the first resolution. It creates new governed history as required by the accepted model.

---

# 19. Pause / cancel flow

P13 intentionally does not create a canonical mutable lane status or `CANCELLED` outcome.

P16 therefore distinguishes three cases.

## 19.1 Cancel before semantic commit

A pending transient schedule/mutation request may be abandoned before commit.

Result:

```text
no canonical occurrence
no outbox
no history to erase
```

A later attempt must re-read current truth and derive a new valid request.

## 19.2 Pause future automatic continuation

An active operator/user directive that disables future automatic scheduling is an **operational permission input**, not Authority/Gate truth.

Runtime effect:

1. `control-facade` receives the pause/resume intent;
2. current effective directive is made available to scheduling/policy through the control-service operational boundary;
3. projection may still derive semantic `NextLegalAction`;
4. scheduler does not submit a new autonomous scheduling mutation while pause is effective;
5. no new outbox is created for deferred future work;
6. existing canonical history is unchanged;
7. already committed OPEN occurrences and already durable outbox entries are not erased by the pause;
8. after resume, scheduler re-reads canonical/external truth and recomputes rather than replaying a stale candidate.

P17 will define the physical representation/persistence/API of this operational directive. P16 does not promote it into a new P12 aggregate.

## 19.3 Stop already running external work

Once an occurrence is OPEN, Control Plane cancellation cannot delete it.

If the governed execution-surface contract supports stop/suspend:

- request stop through the execution adapter;
- keep the occurrence canonical history intact;
- reconcile what actually happened;
- materialize any required partial/result evidence;
- terminalize truthfully using the smallest applicable existing status only when the owning contract supports that conclusion.

If the external worker cannot be stopped immediately, its already-running work may continue. Future scheduling remains independently pausable.

The Control Plane never fabricates `COMPLETED` merely because the user requested cancellation.

---

# 20. Backpressure and temporary unavailability

Backpressure changes **when** work is attempted, not the semantic truth of the work.

P18 will define concrete budgets/thresholds. P16 freezes behavior classes.

## 20.1 Too many OPEN occurrences / admission pressure

Before submitting a new candidate, `control-scheduler` may defer operational submission when the runtime is above its configured admission budget.

- semantic `NextLegalAction` may remain derivable;
- candidate may remain transient;
- no canonical occurrence is created merely to sit behind an unbounded admission queue;
- existing OPEN occurrences remain unchanged;
- when pressure clears, scheduler recomputes from fresh truth.

This is operational admission control, not a new Gate/policy verdict.

## 20.2 Transport unavailable after OPEN commit

If schedule commit already created OPEN + outbox but the transport is unavailable:

```text
OPEN occurrence remains true
outbox remains pending
no semantic retry
```

Dispatcher retries later with the same occurrence.

## 20.3 External system rate-limited

- adapter/dispatcher honors the operational retry window;
- exact semantic envelope is retained;
- no new occurrence is created;
- no Authority/Evidence result is inferred from rate-limit metadata.

## 20.4 Adapter truth stale

Trust-sensitive adapter staleness is not treated as ordinary queue delay.

`control-trust-resolver` returns `EXTERNAL_SNAPSHOT_STALE` / ambiguity.

Before a new canonical mutation:

- mutation fails closed;
- no schedule/outbox commit occurs.

For an already OPEN occurrence, new downstream transitions remain blocked until exact current truth can be re-established. The old occurrence history remains intact.

## 20.5 Outbox growth

Outbox backlog is operational state.

- pending entries cannot be dropped merely to reduce backlog;
- scheduler may defer new admission before commit;
- if store cannot atomically persist both the new semantic occurrence and required outbox, the scheduling transaction aborts completely;
- existing outbox entries continue recovery/retry according to operational budgets;
- backlog does not change stage owner, TrustedBasis, package, outcome, or Gate truth.

---

# 21. External truth change

External truth may change after a historical transition.

Example:

```text
D1 Gate Decision / Authority basis valid
  -> occurrence S scheduled with D1/exact basis pinned

later
D2 supersedes D1 or current Authority changes
```

P16 preserves two separate computations.

## 21.1 Historical transition audit

`control-query` / `control-projection.replay_historical_transition` uses:

- immutable occurrence revisions;
- immutable ScheduleBasis;
- immutable RequiredChildAcceptanceBinding where present;
- pinned exact TrustedBasis/input refs;
- historical exact acceptance/Gate/Proof/result facts.

It does **not** ask whether those facts are current today in order to rewrite past authorization.

## 21.2 Current actionability

A trigger from Project State/Proof/Gate/current-truth observation causes:

```text
resolve current external snapshot
  -> recompute current projection
  -> compare with existing open/next work requirements
```

Possible effects:

- `NextLegalAction` changes;
- current scope becomes blocked at an earlier untrusted layer;
- a not-yet-scheduled candidate disappears;
- future scheduling fails current basis validation;
- an OPEN occurrence whose basis is no longer safe may need governed stop/reconciliation and truthful blocked terminalization under its owning contract.

What never changes:

- old occurrence TrustedBasis;
- old ScheduleBasis;
- old RequiredChildAcceptanceBinding;
- old Gate Decision/Evidence/ProofEvaluation identities;
- old terminal outcome.

There is no retroactive historical rewrite.

---

# 22. Current Authority rollout gate

The target architecture can support:

```text
terminal A
  -> recompute
  -> schedule separately owned B
  -> dispatch B without copy/paste
```

But **capability is not authorization**.

Current Skill Decomposition / Execution Surface Authority still gates automatic cross-Primary continuation.

## 22.1 Derivable `NextLegalAction`

After A terminalizes:

1. projection may correctly derive B as the next legal stage/Primary owner;
2. policy evaluates current orchestration/dispatch Authority;
3. the result may be `PROHIBITED` / compatibility-gated for automatic cross-Primary dispatch;
4. scheduler may retain a transient candidate for display/audit purposes;
5. the candidate is **not submitted automatically** to mutation;
6. therefore no B occurrence and no B outbox entry exist from autonomous chaining;
7. `control-query`/facade may surface B as the next action to the user.

## 22.2 User-mediated continuation under current rules

If the user explicitly starts/continues the next separately owned stage:

- treat that as a fresh trigger;
- re-read canonical/external truth;
- invoke the owning Primary normally;
- schedule under the currently valid user-request/current-composition rules if permitted;
- never reuse the old transient candidate without revalidation.

This preserves current no-direct-Primary-chaining semantics without requiring the user to carry hidden technical state.

## 22.3 Future governed rollout

If later governance explicitly authorizes zero-user-turn cross-Primary orchestration:

- `control-policy` may return an automatic dispatch authorization for the same architecture;
- scheduler may submit the candidate;
- mutation still independently revalidates and commits OPEN + outbox;
- stage ownership and specialist truth ownership remain unchanged.

P16 does not perform that governance change.

---

# 23. Completion / no-action state

A WorkScope is not completed merely because one occurrence terminalized.

Projection derives completion only from the accepted modeling semantics, including:

- no active StageOccurrence;
- no unresolved blocking Escalation;
- no remaining required lifecycle responsibility;
- durable exact required results;
- required child/verification/review obligations satisfied.

When `NextLegalAction.control_action = COMPLETE`:

- scheduler returns `NoAction`;
- no synthetic completion occurrence is created solely to mark a flag;
- query/facade exposes the derived lifecycle summary;
- later current external truth may make the work actionable/blocked again without rewriting history.

---

# 24. Failure and blocker mapping

P16 uses existing domain/module failure classes; it does not invent a new Gate verdict space.

Representative runtime mapping:

| Condition | Runtime result | Semantic effect |
|---|---|---|
| malformed operation | `INVALID_REQUEST` / `REJECTED_PRECONDITION` | no mutation |
| stale lane/record guard | `CONFLICT_RETRY_REQUIRED` | re-read/recompute |
| scheduler race | `CONTROL_LANE_SCHEDULE_CONFLICT` | loser creates no occurrence |
| same request/same fingerprint | `IDEMPOTENT_REPLAY` | return prior result |
| same request/different fingerprint | `OPERATION_IDEMPOTENCY_CONFLICT` | fail closed |
| stale/ambiguous external truth | `EXTERNAL_SNAPSHOT_STALE` / `AMBIGUOUS_EXTERNAL_TRUTH` | no trust-sensitive mutation |
| REQUIRED child unaccepted | `REQUIRED_CHILD_WORK_NOT_ACCEPTED` | no parent successor |
| child acceptance facts ambiguous/conflicting | `CHILD_ACCEPTANCE_BASIS_AMBIGUOUS` / `...CONFLICT` | no barrier crossing |
| delivery uncertain | `DELIVERY_UNCERTAIN` | reconcile same occurrence |
| repository execution divergence | `BLOCKED_EXECUTION_DIVERGENCE` reason | no force reset; map to existing blocker/status |
| repair budget exhausted | `REPAIR_BUDGET_EXHAUSTED` | stop repair; route/escalate |
| exact required result missing | `MISSING_MATERIALIZED_RESULT` / `BLOCKED_EVIDENCE` | cannot claim completion |
| current rollout forbids auto-dispatch | `CONTROL_POLICY_PROHIBITS_AUTONOMY` | derive/display next action only |

Module exceptions must preserve the owning layer so the earliest untrusted layer remains diagnosable.

---

# 25. Projection refresh and cache behavior

Projection is intentionally disposable.

After every accepted canonical mutation and after relevant external-truth change, the runtime must ensure that subsequent scheduling uses a projection derived from current exact inputs.

Permitted implementation strategies include eager refresh, invalidation + lazy rebuild, or equivalent P17 realization, provided:

1. a stale cache entry cannot authorize mutation;
2. mutation independently revalidates canonical/external guards;
3. projection algorithm version is observable/replayable;
4. deleting the cache cannot delete canonical history;
5. terminal commit remains valid even if projection refresh crashes;
6. recovery can rebuild from canonical + exact external truth.

---

# 26. Observability ordering

`control-observability` should correlate runtime events by:

- WorkScopeRef;
- control lane;
- occurrence ID/revision;
- operation request ID;
- dispatch attempt ID;
- package ref;
- external snapshot token identities where safe to expose;
- recovery correlation ID.

Recommended trace sequence mirrors semantic boundaries:

```text
projection
policy
candidate
mutation.validation
mutation.commit
outbox.ready
dispatch.attempt
execution.observed
result.resolved
terminal.commit
projection.refresh
```

But trace order is never the canonical lifecycle oracle.

A missing log line cannot erase a commit; an out-of-order log line cannot reorder immutable occurrence revisions.

---

# 27. Runtime transition matrix

| Transition | Canonical writer | Required durable boundary | External action after/before | Semantic retry rule |
|---|---|---|---|---|
| fresh stage schedule | `control-mutation` | OPEN + lane CAS + idempotency + permitted outbox atomic | dispatch after commit | new occurrence only via new schedule operation |
| execution progress | `control-mutation` | next OPEN occurrence revision | reconciliation occurs before accepted checkpoint | same occurrence |
| terminalize | `control-mutation` | one terminal revision | exact result must already be resolvable when required | no second terminal |
| raise escalation | `control-mutation` | Escalation + terminal occurrence binding atomic | UI publication after durable raise | new escalation only for materially new question |
| escalation resolution | `control-mutation` | resolving occurrence terminal binding | exact external decision exists before resolution | original escalation immutable |
| child spawn | `control-mutation` | child WorkScope + binding + lane + OPEN + permitted outbox atomic | child dispatch after commit | retry same schedule idempotently |
| REQUIRED parent join | `control-mutation` | all required acceptance bindings + parent successor OPEN + permitted outbox atomic | successor dispatch after commit | no barrier-consumed flag |
| repair schedule | `control-mutation` | new repair occurrence + lineage context + outbox | repair after commit | new occurrence per semantic attempt |
| reverify schedule | `control-mutation` | new reverification occurrence + outbox | proof execution after commit | new occurrence |
| rereview schedule | `control-mutation` | new review occurrence + outbox | P34 review after commit | new occurrence / new Gate Decision externally |
| projection recompute | none canonical | no semantic commit | external truth may be read | deterministic replay |
| dispatch retry | none semantic | existing outbox/occurrence retained | same occurrence delivered again | **not** semantic retry |
| process restart | none semantic by itself | recover existing canonical state | reconcile | **not** semantic retry |
| pause | none canonical by itself | operational permission only | prevents future auto-schedule | stale candidate discarded |

---

# 28. End-to-end runtime examples

## 28.1 Clean same-owner or currently authorized continuation

```text
terminal A
  -> canonical commit
  -> projection
  -> policy permits
  -> candidate B
  -> mutation revalidates
  -> B OPEN + outbox atomic
  -> dispatch B
```

## 28.2 Current cross-Primary compatibility gate

```text
terminal A
  -> projection says B / owner=OtherPrimary
  -> policy says cross-Primary auto-dispatch not currently authorized
  -> expose NextLegalAction B
  -> STOP autonomous chain
  -> no B occurrence
  -> no B outbox
```

## 28.3 Crash after B schedule

```text
B OPEN + outbox committed
  -> process crashes
  -> restart
  -> read pending outbox
  -> dispatch same B occurrence
```

## 28.4 Lost worker callback

```text
worker finished
  -> exact result materialized externally
  -> callback lost
  -> recovery resolves result by occurrence/ref
  -> terminalizes same occurrence
```

## 28.5 REQUIRED children

```text
P spawns C1 REQUIRED
P spawns C2 REQUIRED
P terminalizes
C1 accepted
C2 not accepted
  -> parent successor rejected
C2 accepted
  -> mutation resolves exact C1/C2 acceptance basis
  -> successor S OPEN with two immutable bindings
```

## 28.6 Repair loop

```text
P34 finding
  -> exact classification says implementation-repairable
  -> budget permits attempt 1
  -> repair occurrence
  -> exact result
  -> reverify occurrence
  -> fresh proof/evidence
  -> rereview occurrence
  -> new Gate Decision
  -> projection
```

Every arrow is separately durable when it crosses an occurrence boundary.

---

# 29. Decisions deliberately deferred to P17/P18

## P17 Platform Contract must define physical realization for

- process/service placement;
- local vs hosted components;
- RPC/IPC/HTTP/SDK/CLI contracts;
- concrete source snapshot-token representation;
- callback vs poll vs subscription mechanisms;
- outbox claim/lease wire protocol;
- execution-surface delivery and correlation protocol;
- human-decision delivery/return protocol;
- operator pause/resume control representation;
- authn/authz/credential propagation;
- GitHub/ChatGPT/Codex/CI integration capabilities;
- language/ABI boundaries;
- platform lifecycle/startup/shutdown hooks.

P17 may choose representation but cannot redefine any P16 temporal ownership or semantic boundary.

## P18 Engineering / Optimization must define measurable budgets for

- maximum/expected active WorkScopes and OPEN occurrences;
- scheduler admission thresholds;
- mutation throughput;
- projection rebuild cost;
- outbox backlog thresholds;
- dispatch retry/backoff/age budgets;
- adapter freshness budgets;
- worker reconciliation/timeout budgets;
- recovery scan cadence;
- storage/index/retention/compaction;
- observability SLOs;
- load shedding/reference path.

P18 may optimize timing and capacity but cannot weaken correctness to meet throughput targets.

---

# 30. P16 invariants

A conforming runtime data flow satisfies all of the following.

1. every substantive dispatch has a previously committed OPEN occurrence;
2. every permitted dispatching schedule commit atomically persists its outbox intent;
3. terminalization never silently schedules the next Primary in the same semantic transaction;
4. scheduler candidates are disposable and always revalidated before commit;
5. CAS loser recomputes; it never force-applies stale intent;
6. duplicate transport reuses one occurrence identity;
7. crash/restart alone never creates a new semantic occurrence;
8. missing ack alone never creates a new semantic occurrence;
9. timeout alone never proves substantive failure;
10. exact worker result must be resolved/materialized before terminal readiness when required;
11. identical duplicate return is idempotent;
12. conflicting late return cannot rewrite terminal history;
13. recovery may re-dispatch/reconcile but has no privileged canonical write path;
14. P33 preserves valid descendants and fails closed on true divergence;
15. `Task Anchor != Execution Cursor` remains unchanged;
16. REQUIRED child work blocks the next parent substantive occurrence after the spawning occurrence until all uncrossed required children are accepted;
17. parent join pins exact historical child acceptance facts in immutable successor ScheduleBasis;
18. NON_BLOCKING child work does not create a required acceptance binding merely by existing;
19. repair/reverify/rereview are separately owned new occurrences;
20. P34 remains sole official Gate owner;
21. Escalation raise is durable/immutable and resolution is later durable truth;
22. no generic human `approved=true` bypass exists;
23. pause/cancel never erases committed history;
24. already-running external work is reconciled rather than wished away by cancellation;
25. backpressure changes retry/admission timing, not semantic truth;
26. stale trust-sensitive external snapshots block mutation;
27. outbox backlog never changes StageOccurrence meaning;
28. historical transition replay uses pinned basis, not today's acceptance/currentness;
29. later Authority/Gate/Proof changes alter current actionability only;
30. projection cache is disposable and never authorizes mutation by itself;
31. current cross-Primary rollout policy may stop automation even when the next legal owner is known;
32. future governance can enable zero-user-turn dispatch without collapsing ownership boundaries;
33. external truth owners remain external throughout all flows;
34. no P16 flow requires a new P10-P15 semantic or module bypass.

---

# 31. P16 handoff boundary

P16 is complete when downstream platform design can answer **how to physically realize each already-frozen temporal boundary** without guessing semantic order.

The next architecture-family stage is:

```text
P17 Platform Contract
```

P17 must consume the exact materialized P16 head and preserve:

- canonical commit-before-dispatch;
- single canonical writer;
- lane CAS correctness;
- no distributed exactly-once claim;
- outbox durability independent from delivery ack;
- transient scheduler candidate boundary;
- deterministic/read-only projection;
- external exact-truth ownership;
- infrastructure retry != semantic retry;
- P33 Task Anchor / Execution Cursor reconciliation;
- REQUIRED-child exact acceptance-basis join;
- separately owned repair/reverify/rereview occurrences;
- immutable escalation + later resolution;
- noncanonical pause/backpressure semantics;
- historical replay vs current actionability separation;
- Current Authority cross-Primary rollout gate.

If P17 would require violating any of these temporal boundaries, the defect belongs back in P16/P15/P14 rather than being hidden inside a platform shortcut.

Do not begin P20/P30/P32 from P16.

---

# 32. P16 disposition

```text
P16 Runtime Data Flow
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
  @ 12f75bc1938406d8d0cadca4d343fcdb95fdbfb9

P16 Runtime Data Flow
  -> this artifact
```

The next architecture-family stage is P17 Platform Contract, but P16 stops at this durable boundary and does not execute P17 automatically.
