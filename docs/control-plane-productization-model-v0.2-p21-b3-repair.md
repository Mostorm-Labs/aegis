# Aegis Control Plane Productization v0.2 — P21 B3 Modeling Repair

Status: **Draft / Proposed Authority — P12/P13 normative repair**

Scope: `aegis/control-plane-productization`

Reviewed modeling head:

- PR #26 head: `cea1a5796ee34ffcc9835af8240bfca30c576053`
- P21 Authority Review #2: `5062599653`
- verdict: `BLOCKED_AUTHORITY`

Upstream accepted Product Authority remains unchanged:

- PR #25 head `c628bdc15fdd3d32511a04b6f09055413f2786c3`
- Product Authority Review #2 `5061188138`
- verdict `PASS / ACCEPTED_FOR_DOWNSTREAM`

This amendment repairs only **B3 — REQUIRED-child parent-transition barrier and exact acceptance-basis binding**.

All P10-P13 base semantics plus the prior P21 modeling repair remain normative unless this amendment is more specific.

---

# 1. Repair objective

The previous repair correctly established:

```text
WorkScopeRef
Control Lane
ChildWorkBinding
child completed
child accepted_for_parent
```

but left one historical-audit gap:

```text
child accepted_for_parent = true
  -> parent successor scheduled
```

without a normative canonical binding that permanently records **which exact child acceptance facts authorized that parent transition**.

This repair freezes that transition boundary so historical replay never has to infer past authorization from today's generated projection.

---

# 2. REQUIRED child barrier semantics

For v0.2, `ChildWorkBinding.parent_gate = REQUIRED` has one exact meaning:

> **After the REQUIRED child is durably spawned from `spawned_by_occurrence_ref`, no new substantive StageOccurrence may be scheduled on the parent WorkScope's Control Lane after that spawning occurrence until the child is `accepted_for_parent`.**

The spawning parent occurrence itself may finish truthfully. The barrier applies to the next substantive parent-lane occurrence that would continue work after the spawning occurrence.

Therefore:

```text
Parent occurrence P
  -> spawns REQUIRED child C
  -> P may terminate

Child C
  -> executes independently on its own lane

Parent lane
  X no successor after P while C is unaccepted

C accepted_for_parent = true
  -> parent successor S may be scheduled
```

This rule intentionally favors deterministic semantics over a more flexible transition-specific dependency graph in v0.2.

If parent work should remain freely continuable while the child runs, the child binding must use:

```text
parent_gate = NON_BLOCKING
```

A later schema version may introduce a finer-grained barrier contract, but P14 may not reinterpret REQUIRED as a narrower or broader dependency on its own.

---

# 3. Barrier identity and consumption

The REQUIRED barrier is identified by the immutable pair:

```text
child WorkScopeRef
+ ChildWorkBinding.spawned_by_occurrence_ref
```

No mutable barrier object is introduced.

A REQUIRED barrier is considered historically crossed only when a later parent StageOccurrence is durably scheduled with a valid `RequiredChildAcceptanceBinding` for that child.

There is no authored `barrier_consumed` flag.

Historical crossing is derived from the successor's immutable ScheduleBasis.

If several REQUIRED children were spawned from the same parent occurrence, the next parent successor must bind all REQUIRED child barriers that are still uncrossed.

---

# 4. P12 repair — RequiredChildAcceptanceBinding

P12 adds one embedded transition/audit value:

```text
RequiredChildAcceptanceBinding
```

It is not:

- a new aggregate;
- a new acceptance verdict;
- a Gate;
- a mutable approval record;
- a replacement for child `accepted_for_parent` projection.

It records the exact historical basis used when a parent successor crosses one REQUIRED-child continuation barrier.

Canonical shape:

```yaml
required_child_acceptance_binding:
  child_work_scope_ref: <WorkScopeRef>
  barrier_after_occurrence_ref: <CanonicalRef object_type=STAGE_OCCURRENCE>
  child_completion_occurrence_ref: <CanonicalRef object_type=STAGE_OCCURRENCE>
  acceptance_contract_refs:
    - <CanonicalRef object_type=CONTRACT>
  acceptance_fact_refs:
    - <CanonicalRef>
  acceptance_basis_digest: <sha256 digest>
```

Field meaning:

- `child_work_scope_ref` identifies the child whose REQUIRED barrier is being crossed;
- `barrier_after_occurrence_ref` must equal that child's immutable `ChildWorkBinding.spawned_by_occurrence_ref`;
- `child_completion_occurrence_ref` pins the exact terminal child occurrence that participated in deriving child completion at authorization time;
- `acceptance_contract_refs` are the exact acceptance contracts from the child's immutable ChildWorkBinding;
- `acceptance_fact_refs` are the exact durable facts that satisfied those contracts and made `accepted_for_parent = true` at authorization time;
- `acceptance_basis_digest` is derived from the complete canonical binding.

---

# 5. Acceptance fact requirements

`acceptance_fact_refs` MUST contain the minimum exact fact set sufficient to reproduce the parent-acceptance decision under the child's acceptance contracts.

Depending on the contract this may include exact refs to:

```text
RESULT
EVIDENCE
PROOF_EVALUATION
GATE_DECISION
INTEGRATION
EXTERNAL_DECISION
```

Rules:

1. mutable navigation refs without immutable identity are invalid;
2. if a Gate Decision is required, the exact Gate Decision occurrence used for authorization must be present;
3. if a ProofEvaluation or EvidenceArtifact is required by the acceptance contract, its exact immutable identity must be present;
4. if a terminal child result is required, the exact result ref must be present;
5. `acceptance_fact_refs` may reference externally owned truth but never transfer ownership of that truth into Control Plane semantics;
6. duplicate refs are invalid;
7. arrays are canonically sorted using the existing CanonicalRef ordering rule before digesting;
8. the binding may not claim facts that were not valid under the referenced acceptance contracts when the parent successor was scheduled.

The Control Plane does not synthesize a second PASS value. It records exact existing facts that caused the derived acceptance condition to be true.

---

# 6. P12 repair — ScheduleBasis extension

`ScheduleBasis` is amended to include:

```yaml
schedule_basis:
  predecessor_occurrence_ref: null | <CanonicalRef object_type=STAGE_OCCURRENCE>
  reason_code: USER_REQUEST | NEXT_LEGAL_STAGE | RESUME |
               REPAIR | REVERIFY | REREVIEW | EARLIER_LAYER_ROUTE
  derived_from_basis_digest: <TrustedBasis.basis_digest>
  required_child_acceptance_bindings:
    - <RequiredChildAcceptanceBinding>
```

Rules:

1. the field is required and may be an empty array;
2. it is empty when no REQUIRED-child barrier is crossed by this scheduling transition;
3. each binding corresponds to one distinct child WorkScope;
4. bindings are canonically sorted by child WorkScope ID;
5. the complete ScheduleBasis is frozen at StageOccurrence creation and immutable across revisions;
6. `required_child_acceptance_bindings` explains a transition authorization dependency; it does not become Authority or Gate truth.

This makes child-gated continuation part of the successor's canonical transition basis rather than transient projection state.

---

# 7. Relationship to TrustedBasis and input_refs

The parent successor must remain independently auditable through its normal StageOccurrence references.

For every `RequiredChildAcceptanceBinding`:

1. `child_completion_occurrence_ref` MUST also appear in the successor StageOccurrence `input_refs`;
2. each `acceptance_fact_ref` MUST also appear either:
   - in `trusted_basis.accepted_fact_refs` when its object type is allowed by that field's existing contract; or
   - in `input_refs` for exact externally owned proof/evidence facts not classified as TrustedBasis accepted facts;
3. every acceptance contract ref MUST already be reachable from the child binding and/or the successor's applicable TrustedBasis/contract refs;
4. the ScheduleBasis binding provides the **association** between child, barrier, contracts, and exact facts; TrustedBasis/input_refs remain the normal exact-reference surfaces consumed by the occurrence.

This is reference reuse, not duplicated semantic ownership.

---

# 8. P13 repair — parent successor scheduling

`SCHEDULE_STAGE_OCCURRENCE` for an existing parent lane adds these preconditions.

Before commit, derive all uncrossed REQUIRED-child barriers for the parent WorkScope.

For each such child:

1. current child `completed` must be true;
2. current child `accepted_for_parent` must be true;
3. exact child completion occurrence must resolve;
4. every acceptance contract must resolve exactly;
5. the exact durable facts that made acceptance true must resolve and satisfy the contract;
6. build one `RequiredChildAcceptanceBinding`;
7. pin the same exact refs into the successor's TrustedBasis/input_refs as required by section 7.

If any uncrossed REQUIRED child cannot satisfy these conditions:

```text
REQUIRED_CHILD_WORK_NOT_ACCEPTED
```

and no parent successor canonical mutation occurs.

If the projected acceptance is true but the exact supporting fact set cannot be uniquely materialized:

```text
CHILD_ACCEPTANCE_BASIS_AMBIGUOUS
```

and scheduling fails closed.

If the projected acceptance and exact acceptance facts disagree:

```text
CHILD_ACCEPTANCE_BASIS_CONFLICT
```

and scheduling fails closed.

---

# 9. Atomic scheduling boundary

Crossing a REQUIRED child barrier and scheduling the parent successor are one semantic commit boundary:

```text
validate child acceptance
+ construct exact RequiredChildAcceptanceBinding(s)
+ validate parent successor TrustedBasis/input refs
+ create parent StageOccurrence revision 1 / OPEN
```

Either the successor containing all required immutable bindings becomes durable, or no barrier is considered crossed.

No separate mutable operation marks a barrier consumed.

A transport retry of the same scheduling request returns/reconciles the same parent successor occurrence and the same acceptance bindings.

---

# 10. Historical replay

Historical replay of a parent transition MUST use the immutable acceptance binding stored in that successor's ScheduleBasis.

It MUST NOT ask:

```text
is child accepted_for_parent today?
```

to determine whether the historical transition was authorized.

Instead it resolves the pinned historical tuple:

```text
child WorkScope
barrier/spawn occurrence
child completion occurrence
acceptance contracts
exact result/evidence/proof/Gate/decision facts
acceptance_basis_digest
```

and answers:

> these were the exact facts and contracts that allowed this parent successor to be scheduled at that historical boundary.

A later Gate Decision, Authority change, ProofEvaluation, Evidence replacement, or current projection change never rewrites this historical binding.

---

# 11. Current projection after later truth changes

Historical authorization and current actionability remain distinct.

Example:

```text
D1 = child Gate Decision PASS
  -> parent successor S scheduled with D1 pinned

later
D2 supersedes D1 or another current trust condition changes
```

Rules:

1. S retains D1 in its immutable transition basis;
2. S's historical authorization is not retroactively rewritten;
3. current Control projection may become blocked or route to an earlier untrusted layer if current truth no longer supports continued downstream trust;
4. any later newly scheduled parent occurrence must satisfy current TrustedBasis/policy/contract validity independently;
5. no later projection may claim that S was originally authorized by D2.

This mirrors the existing Aegis distinction between immutable historical Gate Decisions and current Gate actionability.

---

# 12. Multiple REQUIRED children

If a parent occurrence spawns multiple REQUIRED children, the next parent successor may be scheduled only when **all** uncrossed REQUIRED children are accepted.

Its ScheduleBasis contains one binding per required child:

```yaml
required_child_acceptance_bindings:
  - child_work_scope_ref: ws_child_a
    ...
  - child_work_scope_ref: ws_child_b
    ...
```

Partial acceptance cannot cross the parent barrier.

NON_BLOCKING children never appear in this array merely because they exist.

---

# 13. Repair / reverify / rereview interaction

If a REQUIRED child reaches completion only after repair/reverification/re-review:

- the child history remains a sequence of separately owned StageOccurrences;
- `child_completion_occurrence_ref` pins the exact terminal occurrence establishing the final completed trajectory boundary used at authorization time;
- `acceptance_fact_refs` pin the exact fresh result/evidence/ProofEvaluation/Gate Decision required by the acceptance contract;
- prior blocked or superseded facts remain historical but do not authorize the parent successor unless the acceptance contract explicitly says they do.

No repair counter, Gate verdict, or ProofEvaluation is copied into the parent as new semantic truth.

---

# 14. Validation invariants added by B3

A conforming v0.2 candidate additionally satisfies:

1. REQUIRED has one deterministic continuation-barrier meaning;
2. the barrier starts from the immutable spawning parent occurrence;
3. no parent successor may cross an uncrossed REQUIRED barrier while the child is unaccepted;
4. crossing the barrier requires a canonical RequiredChildAcceptanceBinding;
5. the binding pins one exact child WorkScope, barrier occurrence, completion occurrence, acceptance contract set, and acceptance fact set;
6. the binding digest is reproducible;
7. the successor reuses the exact facts through TrustedBasis/input_refs;
8. multiple REQUIRED children all bind before the parent continues;
9. NON_BLOCKING children do not create a barrier;
10. no mutable barrier-consumed state exists;
11. historical replay uses pinned acceptance bindings, not current child projection;
12. later current-truth changes may alter actionability but never rewrite prior transition authorization;
13. ambiguous or conflicting acceptance fact materialization fails closed;
14. P14 may choose storage/index/transaction mechanisms but may not redefine REQUIRED barrier or historical acceptance binding semantics.

---

# 15. Explicitly unchanged modeling authority

This repair does not reopen or modify:

- WorkScopeRef identity;
- one primary Control Lane per WorkScope in v0.2;
- immutable ChildWorkBinding parent relationship;
- child and parent using separate lanes;
- `completed != accepted_for_parent`;
- acceptance being derived from existing exact contract/Gate/Proof truth;
- VerificationBoundImplementationPackage as the strengthened existing P31 package;
- Finding ownership remaining external;
- exactly one Primary owner per StageOccurrence;
- `terminal A -> recompute -> schedule B` cross-owner continuation;
- Proof Assurance != Gate Policy != Control Autonomy;
- Task Anchor != Execution Cursor;
- append-only history;
- commit OPEN before dispatch;
- bounded repair/reverify/rereview;
- optimistic concurrency/idempotency/replay semantics;
- generated Control projections;
- P34 as sole official Gate owner.

---

# 16. Architecture boundary

After this repair, P14 still owns physical realization only, including:

- where WorkScope/Lane/StageOccurrence records are stored;
- how REQUIRED-child barriers are indexed for lookup;
- how acceptance refs are resolved efficiently;
- transaction technology for atomic successor commit;
- scheduler/queue/process topology;
- projection-cache realization;
- reconciliation adapters to Project State / Proof Plane / Execution Surface.

P14 may not invent a different REQUIRED-child meaning or infer historical acceptance from mutable/current projection state.

---

# 17. B3 disposition

```text
B3 REQUIRED-child parent-transition barrier
   + exact acceptance-basis binding
  -> REPAIRED IN CANDIDATE
```

The complete proposed modeling Authority package is now:

```text
docs/control-plane-productization-model-v0.2.md
+ docs/control-plane-productization-schema-v0.2.md
+ docs/control-plane-productization-operations-v0.2.md
+ docs/control-plane-productization-model-v0.2-p21-repair.md
+ docs/control-plane-productization-model-v0.2-p21-b3-repair.md
```

This amendment is still Draft/Proposed and does not self-accept the new head.

Required next action after materialization:

```text
fresh P21 Authority Review against the new exact PR #26 head
```

Do not enter P14 until that exact repaired head receives `PASS / ACCEPTED_FOR_DOWNSTREAM`.
