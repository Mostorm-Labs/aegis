# Aegis Control Plane Productization v0.2 — P21 Modeling Repair

Status: **Draft / Proposed Authority — P10/P12/P13 normative repair**

Scope: `aegis/control-plane-productization`

Reviewed modeling head:

- PR #26 head: `0b2b36f93ed72919277fb8203b5503b19d1796db`
- P21 Authority Review #1: `5062539826`
- verdict: `BLOCKED_AUTHORITY`

Upstream accepted Product Authority remains unchanged:

- PR #25 head `c628bdc15fdd3d32511a04b6f09055413f2786c3`
- Product Authority Review #2 `5061188138`
- verdict `PASS / ACCEPTED_FOR_DOWNSTREAM`

This amendment repairs only:

- **B1** — missing canonical semantic work-scope identity;
- **B2** — missing child-work relationship / completion / acceptance semantics;
- **F1** — implementation package identity wording;
- **F2** — Finding ownership wording.

All other semantics in the existing P10-P13 package remain normative unless this amendment is more specific.

---

# 1. Repair principle

Persistent Control State must distinguish four concepts that were previously partially conflated:

```text
Work Scope
  what lifecycle unit of work is being controlled

Control Lane
  the serialized control trajectory for that work scope

Implementation Package Scope
  the exact implementation/code authorization boundary for BUILD execution

Child Work
  a separately controlled sub-scope whose completion/acceptance may affect the parent
```

Therefore:

```text
Work Scope
!= Control Lane
!= Implementation Package Scope
!= StageOccurrence
```

This repair does **not** introduce a giant mutable `WorkItem` aggregate.

---

# 2. P10 repair — WorkScopeRef

## 2.1 Classification

`WorkScopeRef` is an immutable embedded semantic identity value/reference.

It is not:

- a mutable project/task record;
- Authority;
- an implementation package;
- a ControlCursor;
- an ExecutionCursor;
- a workflow engine.

Its purpose is to answer:

> **Which stable unit of product/development work do these StageOccurrences, package revisions, escalations, and generated control facts belong to?**

## 2.2 Stable identity

A Control Plane work scope has one stable opaque identity:

```text
id_scheme = control-work-scope-v0.2
id        = ws_<UUIDv7>
```

The identity is allocated when the first durable Control Plane occurrence for that work scope is scheduled.

The UUID is only identity. Encoded time does not establish priority, Authority, trust, or lifecycle order.

## 2.3 Scope meaning versus scope authorization

`WorkScopeRef` provides lifecycle correlation identity; it does **not** itself authorize files, schemas, product semantics, or proof weakening.

The exact semantic/authorization boundaries remain owned by their existing contracts:

- Authority / Contract refs in `TrustedBasis`;
- implementation/code boundary in the P31 package scope contract;
- VerificationSpec / Proof truth in the Proof Plane;
- Gate policy / Gate Decision in its existing owner.

Therefore a work scope may exist before an implementation package exists, including DEFINE/design/governance work.

---

# 3. P10 repair — Work Scope and Control Lane relationship

For v0.2:

> **One `control_lane_id` controls exactly one `WorkScopeRef`, and one WorkScopeRef has exactly one primary control lane.**

This is a semantic relationship, not a storage-table decision.

Consequences:

1. every substantive `StageOccurrence` carries the WorkScopeRef for its lane;
2. successor occurrences on the same lane retain the same WorkScopeRef;
3. a lane may not be rebound to another work scope;
4. a work scope may not silently move to another lane;
5. parallel/decomposed work is represented as child work scopes with their own lanes rather than by creating competing active trajectories for the same work-scope identity;
6. P14 may choose how lane/work mappings are indexed or persisted but may not redefine this semantic relationship.

This gives sessionless resume a stable answer to both:

```text
what work am I resuming?
where in the control trajectory is that work now?
```

---

# 4. P10 repair — ChildWorkBinding

Child work is represented by a stable relationship between existing work scopes, not by a new mutable `ChildWork` aggregate.

A non-root work scope carries one immutable `ChildWorkBinding`:

```yaml
child_work_binding:
  parent_work_scope_ref: <WorkScopeRef>
  spawned_by_occurrence_ref: <exact CanonicalRef object_type=STAGE_OCCURRENCE>
  parent_gate: REQUIRED | NON_BLOCKING
  acceptance_contract_refs:
    - <CanonicalRef object_type=CONTRACT>
```

A root work scope has:

```yaml
child_work_binding: null
```

Meaning:

- `parent_work_scope_ref` identifies the direct parent scope;
- `spawned_by_occurrence_ref` pins the durable parent occurrence from which decomposition/delegation was authorized;
- `parent_gate` states whether the parent may cross the dependent continuation boundary before the child is accepted;
- `acceptance_contract_refs` state what existing canonical contract(s), if any, determine acceptance of this child for the parent.

The binding does not make the parent owner of the child specialist stage. The child still executes through separately owned StageOccurrences.

## 4.1 Child identity rules

1. one child work scope has at most one direct parent;
2. parent binding is frozen when the child scope is first materialized;
3. a child cannot be re-parented;
4. parent/child cycles are invalid;
5. the parent and child must have different WorkScope IDs and different Control Lane IDs;
6. a materially different decomposition relationship creates a new child work scope rather than rewriting the old binding;
7. child work may itself have children, producing a tree/DAG-free direct-parent hierarchy in v0.2;
8. physical tree indexes or adjacency storage are P14 concerns; the semantic direct-parent relationship is frozen here.

---

# 5. P10/P11 repair — Child completion and acceptance

Child work has no authored mutable `status` object.

Its current state is derived from canonical history and external truth.

Two concepts are distinct:

```text
Child Completed
!=
Child Accepted For Parent
```

## 5.1 Completed

A child work scope is **completed** only when its generated control state proves all of the following:

1. no active StageOccurrence remains for the child scope;
2. no unresolved Escalation blocks the child scope;
3. its derived `next_legal_action` is `COMPLETE` / no further required lifecycle responsibility;
4. all required terminal results for that child trajectory are durable exact refs.

A terminal implementation occurrence alone does not make the child work complete when verification/review is still required.

## 5.2 Accepted for parent

A child work scope is **accepted for the parent** only when:

1. the child is completed; and
2. every `acceptance_contract_ref` in its ChildWorkBinding is satisfied by exact durable facts under that contract's owning semantics; and
3. any required independent Gate Decision exists and is acceptable under the parent/child acceptance contract; and
4. no stale/diverged exact ref invalidates the accepted result for current parent continuation.

The Control Plane does not invent a second acceptance verdict.

For example:

```text
child P34 Gate required
  -> official Gate Decision remains owned by P34 / Project State
  -> child acceptance projection references that exact decision
```

`completed` may therefore be true while `accepted_for_parent` remains false.

## 5.3 Parent continuation

If:

```text
parent_gate = REQUIRED
```

then a parent transition that depends on the child MUST NOT be scheduled until `accepted_for_parent` is true.

If:

```text
parent_gate = NON_BLOCKING
```

then the relationship is tracked for visibility/audit but does not by itself prohibit unrelated parent continuation.

No child relationship permits a parent to weaken Authority, Proof Assurance, Gate policy, or the child's own stage ownership.

---

# 6. P12 repair — canonical WorkScopeRef shape

The P12 embedded-value set is amended to include:

```text
WorkScopeRef
ChildWorkBinding
```

Canonical value:

```yaml
work_scope_ref:
  id_scheme: control-work-scope-v0.2
  id: ws_<uuidv7>
  child_work_binding: null | {
    parent_work_scope_ref: {
      id_scheme: control-work-scope-v0.2
      id: ws_<uuidv7>
    }
    spawned_by_occurrence_ref: <CanonicalRef object_type=STAGE_OCCURRENCE>
    parent_gate: REQUIRED | NON_BLOCKING
    acceptance_contract_refs:
      - <CanonicalRef object_type=CONTRACT>
  }
```

Rules:

1. `id_scheme` and `id` are required.
2. root scopes have `child_work_binding: null`.
3. non-root scopes have exactly one immutable binding.
4. all `acceptance_contract_refs` are exact references.
5. duplicate acceptance refs are invalid.
6. parent binding is part of the WorkScopeRef's frozen semantic identity facts for the lifetime of that scope.
7. WorkScopeRef is not independently mutated or versioned as a new aggregate in v0.2.

---

# 7. P12 repair — StageOccurrence

Every `StageOccurrence` canonical record now requires:

```yaml
work_scope_ref: <WorkScopeRef>
```

Conceptual shape becomes:

```yaml
kind: STAGE_OCCURRENCE
id: so_<uuidv7>
control_lane_id: lane_<uuidv7>
work_scope_ref: <WorkScopeRef>
stage_span: ...
primary_owner: ...
trusted_basis: ...
policy_binding: ...
...
```

Additional validation:

1. every revision of one occurrence preserves byte-semantic equality of `work_scope_ref`;
2. every successor occurrence scheduled on the same lane uses the same WorkScopeRef;
3. the same lane ID may not appear with a different WorkScopeRef;
4. the same WorkScopeRef may not appear as the primary work scope of a different lane;
5. a child scope's first occurrence must pin a valid parent occurrence belonging to the declared parent WorkScopeRef;
6. a child scope does not inherit the parent's Primary owner; each child occurrence resolves its own stage owner normally.

`work_scope_ref` joins the existing frozen start facts for OPEN occurrence revisions.

---

# 8. P12 repair — VerificationBoundImplementationPackage

The package shape is amended with:

```yaml
work_scope_ref: <WorkScopeRef>
```

The existing package `scope` field remains the exact implementation/code scope contract:

```yaml
scope:
  scope_id: <stable semantic implementation-scope identity>
  scope_contract_ref: <CanonicalRef object_type=CONTRACT>
```

Relationship:

```text
WorkScopeRef
  lifecycle work identity

Package.scope
  executable implementation authorization boundary
```

They are intentionally not the same concept.

Rules:

1. a package belongs to exactly one WorkScopeRef;
2. repository execution occurrence(s) consuming the package must use that same WorkScopeRef;
3. package scope cannot widen the TrustedBasis/Authority of that work scope;
4. a parent feature scope with multiple independent implementation units should model those units as child WorkScopes, each with its own P31 package as appropriate;
5. changing package code scope creates a package revision under existing P12 rules but does not rename/reparent the WorkScopeRef unless the semantic unit of work itself is newly decomposed.

## 8.1 F1 clarification — no second P31 package truth

`VerificationBoundImplementationPackage` is the strengthened canonical semantic contract for the **existing P31 implementation/task package** required by Control Plane Productization.

It is not a second parallel package store or a wrapper package with independent authorization truth.

Current Execution Surface semantics remain controlling:

```text
P31 package = what work is authorized
Task Anchor  = trusted repository baseline relation
Execution Cursor = accepted moving repository position
```

A future architecture may use adapters/serializers around the P31 package, but those adapters do not create another authoritative package aggregate.

---

# 9. P12 repair — Escalation and generated Control State

Every Escalation is correlated to the work it interrupts through the same WorkScopeRef:

```yaml
work_scope_ref: <WorkScopeRef>
control_lane_id: lane_<uuidv7>
```

The generated Control projection is amended to expose:

```yaml
control_cursor:
  work_scope_ref: <WorkScopeRef>
  control_lane_id: lane_<uuidv7>
  ...

child_work:
  - work_scope_ref: <WorkScopeRef>
    control_lane_id: lane_<uuidv7>
    completed: true | false
    accepted_for_parent: true | false
    accepted_fact_refs:
      - <CanonicalRef>
    blocking_reason: null | <derived reason>
```

Projection rules:

1. `child_work[]` is generated, not authored.
2. child discovery comes from immutable ChildWorkBindings.
3. `completed` derives only from the child scope's canonical lifecycle state.
4. `accepted_for_parent` derives from completion plus exact acceptance-contract satisfaction.
5. `accepted_fact_refs` lists exact external/canonical facts that caused the acceptance derivation; it does not create new acceptance truth.
6. stale or contradictory acceptance evidence fails closed and projects `accepted_for_parent: false` with a derived blocker.
7. the parent's `next_legal_action` incorporates REQUIRED child acceptance constraints.

This satisfies CP-FR01's requirement to make completed/accepted child work available without a mutable child-status registry.

---

# 10. P13 repair — operation request guards

The P13 operation envelope is amended so trust-sensitive scheduling/package mutations may guard:

```yaml
expected_state:
  work_scope_ref: null | <WorkScopeRef>
  control_lane_id: lane_<uuidv7>
  ...existing guards...
```

Where a target canonical object already exists, its exact WorkScopeRef must match the guarded work scope.

A lane/work mismatch is not eligible for last-write-wins reconciliation.

Representative reason code:

```text
WORK_SCOPE_LANE_CONFLICT
```

---

# 11. P13 repair — package operations

`MATERIALIZE_IMPLEMENTATION_PACKAGE` now requires:

```text
WorkScopeRef
+ existing complete package inputs
```

Preconditions add:

1. the package WorkScopeRef resolves to the intended control lane/work trajectory;
2. the package's implementation scope remains within that work scope's TrustedBasis/Authority constraints;
3. if the package is for child work, its WorkScopeRef retains the exact ChildWorkBinding created for that child scope;
4. no second parallel package truth is created for the same P31 authorization.

`REVISE_IMPLEMENTATION_PACKAGE` must preserve the WorkScopeRef across revisions.

If implementation scope change means the work has actually been decomposed into a distinct semantic child unit rather than merely revising the existing authorized package, create a new child WorkScope/package instead of silently repurposing the existing WorkScope identity.

---

# 12. P13 repair — scheduling same-scope continuation

`SCHEDULE_STAGE_OCCURRENCE` adds required payload:

```yaml
work_scope_ref: <WorkScopeRef>
```

For continuation on an existing lane:

1. `work_scope_ref` must equal the lane's existing WorkScopeRef;
2. `schedule_basis.predecessor_occurrence_ref`, when present, must belong to the same WorkScopeRef unless this operation is the first occurrence of a newly created child scope;
3. successor scheduling may change stage/owner according to governed routing, but it cannot change the WorkScopeRef;
4. any required package ref must belong to the same WorkScopeRef;
5. REQUIRED child-work acceptance constraints must be satisfied before a parent-dependent continuation transition commits.

Representative failure codes:

```text
WORK_SCOPE_MISMATCH
PACKAGE_WORK_SCOPE_MISMATCH
REQUIRED_CHILD_WORK_NOT_ACCEPTED
```

---

# 13. P13 repair — scheduling new child work

No new `CREATE_WORK_ITEM` or mutable child-work operation is introduced.

The first `SCHEDULE_STAGE_OCCURRENCE` for a new child work scope atomically establishes:

```text
new WorkScopeRef
+ immutable ChildWorkBinding
+ new control_lane_id
+ StageOccurrence revision 1 / OPEN
```

Preconditions:

1. child WorkScope ID is new;
2. child Control Lane ID is new;
3. parent WorkScope exists;
4. `spawned_by_occurrence_ref` is exact, durable, and belongs to that parent WorkScope;
5. parent/child relationship is acyclic;
6. every acceptance contract ref resolves exactly;
7. the scheduling decision is authorized by the parent occurrence's TrustedBasis/policy and cannot widen semantic scope without the owning Authority decision;
8. child Primary owner is derived from the child stage, not inherited from the parent;
9. the parent does not become the substantive owner of the child occurrence.

Atomicity:

Either the child binding, lane association, and first OPEN occurrence become durable together, or none do.

A transport retry reuses the same exact child WorkScope/lane/occurrence identity.

A materially different child decomposition is a new child WorkScope, not an in-place rewrite.

---

# 14. P13 repair — child completion/acceptance projection

No `MARK_CHILD_COMPLETE` or `ACCEPT_CHILD_WORK` mutation exists.

After any child canonical mutation or relevant external Gate/Proof/Authority change:

```text
RECOMPUTE_CONTROL_PROJECTION
```

must derive:

- child completion;
- child acceptance for parent;
- exact accepted fact refs;
- whether a REQUIRED child blocks the parent's next legal action.

This preserves the existing rule:

```text
Control projection = derived state
```

and avoids a second mutable approval universe.

If the same exact canonical/external inputs produce contradictory child acceptance results, the projection is invalid and control fails closed.

---

# 15. P13 repair — replay and history

Historical replay preserves the WorkScopeRef and ChildWorkBinding exactly as originally materialized.

Later changes do not:

- re-parent historical child work;
- collapse child scopes into a parent;
- rename an old WorkScope to match a new decomposition;
- retroactively mark a child accepted under a later Gate Decision as if the earlier parent transition had been authorized by it.

Current projection replay may change current child `accepted_for_parent` when current exact acceptance truth changes, but historical parent/child transitions remain bound to the exact facts that existed for those occurrences.

---

# 16. F2 repair — Finding ownership wording

The P10 shorthand:

```text
immutable occurrences / packages / findings
```

must be read and henceforth stated as:

```text
immutable Control Plane occurrences / P31 package revisions
+ exact references to externally owned Finding / Evidence / Gate / Proof truth
```

Control Plane does **not** create a new Finding aggregate or Finding store.

Findings remain owned by their existing review/classification/evidence contracts and enter Control Plane history only through exact `CanonicalRef` values.

---

# 17. Repaired invariant set

The complete P10-P13 candidate now additionally requires:

1. every substantive StageOccurrence belongs to one stable WorkScopeRef;
2. one WorkScopeRef has one primary Control Lane in v0.2;
3. Control Lane identity never substitutes for semantic work identity;
4. package code scope never substitutes for lifecycle WorkScope identity;
5. successor occurrences on one lane preserve WorkScopeRef;
6. package revisions preserve WorkScopeRef;
7. Escalations retain WorkScope correlation;
8. child work is a relationship between WorkScopes, not a new mutable aggregate;
9. child WorkScope has exactly one immutable direct parent binding;
10. child and parent use separate Control Lanes;
11. child Primary ownership is derived independently from its stage;
12. child `completed` and `accepted_for_parent` are distinct generated facts;
13. REQUIRED child work blocks dependent parent continuation until accepted;
14. acceptance uses existing exact contract/Gate/Proof truth and never creates a second verdict;
15. no operation directly authors child completion/acceptance projection state;
16. parent/child relationships are never rewritten by replay;
17. VerificationBoundImplementationPackage is the strengthened existing P31 package truth, not a parallel package aggregate;
18. Control Plane references Finding truth and does not own a second Finding aggregate.

All previously accepted P10-P13 invariants remain in force.

---

# 18. Architecture boundary after repair

The following remain **P14 architecture decisions** and are intentionally not solved here:

- physical store/file/table representation of WorkScope/lane mappings;
- adjacency indexes for parent/child traversal;
- transaction technology used to atomically materialize a child binding + lane + first occurrence;
- scheduler process topology;
- queue/broker realization;
- projection-cache technology;
- distributed lock/lease implementation;
- APIs/ABI between Control Plane services;
- reconciliation adapters to Project State / Proof Plane / Execution Surface storage.

P14 may choose those mechanisms only while preserving the repaired semantics above.

---

# 19. Repair disposition

P21 #1 findings are repaired in this candidate as follows:

```text
B1 Canonical work-scope identity
  -> REPAIRED

B2 Child-work semantics
  -> REPAIRED

F1 P31 package identity wording
  -> CLARIFIED

F2 Finding ownership wording
  -> CLARIFIED
```

The complete proposed modeling Authority package is now:

```text
docs/control-plane-productization-model-v0.2.md
+ docs/control-plane-productization-schema-v0.2.md
+ docs/control-plane-productization-operations-v0.2.md
+ docs/control-plane-productization-model-v0.2-p21-repair.md
```

This amendment remains Draft/Proposed and does not self-accept the repaired modeling head.

Required next action after materialization:

```text
fresh P21 Authority Review against the new exact PR #26 head
```

Do not enter P14 until that exact repaired head receives `PASS / ACCEPTED_FOR_DOWNSTREAM`.
