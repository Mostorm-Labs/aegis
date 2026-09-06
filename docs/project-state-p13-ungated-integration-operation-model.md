# Aegis Project State — P13 Ungated Integration Operation / Mutation Model

Status: **P13 Operation / Mutation Model Candidate**

Scope: `aegis/project-state`

Triggering finding: `P22-F2 = MISSING_CONTRACT / SPEC_DEFECT`

Repository basis: `main@3a2607220cd875dc66857b334dcfbd2c763e7c7d`

P12 semantic basis candidate: `777e1e8a9652e2cbf220d234798641d65dc9b0c9`

Current Authority under repair: `aegis-project-state-v0.5`

This artifact defines the bounded mutation semantics required by the P12 Gate Decision Binding model. It does not assign a replacement schema version, does not mutate `.aegis/*`, does not create a new Current Authority, and does not authorize repository integration, release, or rollout.

---

## 1. Inherited P12 semantic contract

P12 introduced an explicit Gate Decision Binding value object:

```text
Integration
  -> Gate Decision Binding
       -> Bound(exact Gate Decision)
       OR
       -> Absent(no applicable Integration Gate Decision existed)
```

Inherited status constraints:

```text
awaiting_integration -> Bound only
integrated           -> Bound | Absent
closed_unmerged      -> Bound only
```

`Absent` is positive historical truth. It is never inferred from missing state, a dangling reference, an incomplete manifest, or a failed lookup.

P13 defines how those states may be created, finalized, replayed, and protected from later rewrite.

---

## 2. Mutation vocabulary

P13 defines six logical domain operations. These are semantic operations, not required API names.

### O1 — Register Awaiting Integration

Purpose:

> register a proposed repository integration that is currently authorized for execution.

Input contract:

```yaml
integration_id: <stable id>
kind: <integration kind>
ref: <candidate ref>
target_ref: <target>
gate_decision_binding:
  kind: bound
  gate_decision_id: <exact current PASS/PASS_WITH_FINDINGS decision>
evidence_refs:
  - <candidate/integration-readiness evidence>
```

Preconditions:

- no repository occurrence has yet been finalized for this `integration_id`;
- the bound decision exists;
- it is the applicable current decision for this proposed action;
- its verdict is `PASS` or `PASS_WITH_FINDINGS`;
- required evidence is available.

Result:

```text
none -> awaiting_integration + Bound(D)
```

`Absent` is forbidden for O1.

---

### O2 — Rebind Awaiting Integration

Purpose:

> update a still-unrealized candidate to the exact current decision that now governs the proposed action.

Allowed only before a repository occurrence exists.

Transition:

```text
awaiting_integration + Bound(D1)
-> awaiting_integration + Bound(D2)
```

Preconditions:

- the candidate is still unmerged/unrealized;
- `D2` exists and is the exact current applicable `PASS` / `PASS_WITH_FINDINGS` decision;
- the prior binding is prospective only and has not become a historical occurrence binding.

This operation exists because an awaiting candidate is current action state, not yet historical occurrence truth.

`Bound -> Absent` is forbidden while status remains `awaiting_integration`.

---

### O3 — Finalize Integration Occurrence

Purpose:

> convert a proposed Integration into the exact historical truth of what actually occurred in the repository.

The operation is atomic over:

```text
status = integrated
integrated_revision
occurrence evidence
historical Gate Decision Binding
```

The historical binding is resolved at the actual occurrence, not copied blindly from the prior awaiting candidate.

Possible results:

```text
awaiting Bound(D1)
-> integrated Bound(D1)
```

when `D1` was the applicable decision for the actual occurrence;

or:

```text
awaiting Bound(D1)
-> integrated Bound(D2)
```

when another exact decision `D2` was the applicable decision for the actual occurrence;

or:

```text
awaiting Bound(D1)
-> integrated Absent(no_applicable_integration_gate_decision)
```

when durable evidence establishes that no applicable Integration Gate Decision existed for the actual occurrence.

The last two forms are not arbitrary historical rewrites. They are part of the one-time transition from prospective action state to historical occurrence state.

Once O3 succeeds, the historical binding is frozen.

---

### O4 — Reconcile Historical Integration Occurrence

Purpose:

> append an Integration occurrence that repository reality proves happened but Project State has not yet recorded.

This is the operation required for PR #82 after a replacement Authority is accepted.

Possible results:

```text
none -> integrated Bound(D)
```

or:

```text
none -> integrated Absent(no_applicable_integration_gate_decision)
```

Preconditions for `Bound(D)`:

- durable repository evidence proves the occurrence and exact integrated revision;
- `D` exists and is proven to have been the applicable decision for that occurrence.

Preconditions for `Absent(...)`:

- durable repository evidence proves the occurrence and exact integrated revision;
- a durable governance basis explicitly establishes that no applicable Integration Gate Decision existed for that occurrence;
- the condition is not merely unknown, missing, unresolved, or unpersisted;
- no synthetic Gate Decision is created to satisfy schema shape.

O4 is append-only historical reconciliation. It is not permission to repair an already-recorded historical binding in place.

---

### O5 — Close Unmerged Candidate

Purpose:

> close a proposed Integration that never became a repository occurrence.

Transition:

```text
awaiting_integration + Bound(D)
-> closed_unmerged + Bound(D)
```

The final associated decision remains historical candidate provenance.

`Absent` is not introduced for `closed_unmerged` by this repair.

---

### O6 — Append Corroborating Integration Evidence

Purpose:

> add later corroborating evidence without rewriting historical occurrence meaning.

For an already `integrated` record, O6 may append evidence references only.

It must not change:

- Integration identity;
- repository `ref`;
- target ref;
- integrated revision;
- status;
- Gate Decision Binding kind;
- bound Gate Decision ID;
- Absent reason.

Evidence removal or replacement is not permitted by O6.

---

## 3. Who may establish `Absent`

P13 does not assign semantic authority based on executor identity.

A human, ChatGPT, Project State tooling, or another executor cannot make `Absent` true merely by writing the field.

The authority to materialize `Absent` comes from a **durable governance determination** that the historical occurrence had no applicable Integration Gate Decision.

Therefore an `Absent`-producing O3/O4 operation requires two distinct bases:

```text
Occurrence Basis
+
Absence Basis
```

Occurrence Basis proves:

- the repository occurrence happened;
- the exact target baseline/revision;
- the Integration identity/ref.

Absence Basis proves:

- no applicable Integration Gate Decision governed/authorized the actual occurrence;
- candidate decisions that might superficially appear relevant are not silently reinterpreted as applicable;
- absence is confirmed history, not missing Project State persistence.

For PR #82, P22 finding `P22-F2` / durable review `5553423707` is the current governance basis establishing this distinction. P13 does not itself declare that review sufficient as final verification evidence; P20 must later define the proof oracle and evidence contract.

---

## 4. Occurrence-time binding rule

Historical binding is determined from the governance state applicable to the actual repository occurrence.

Conceptually:

```text
resolve_binding(actual_occurrence, governance_history)

-> Bound(D)   if exactly one applicable Gate Decision D is established
-> Absent     if confirmed that no applicable Gate Decision existed
-> BLOCKED    if applicability is ambiguous or evidence is insufficient
```

Ambiguity must never collapse into `Absent`.

Examples of blocked states:

- a likely Gate Decision exists but its applicability to the occurrence is unresolved;
- decision timing/order cannot be established;
- repository occurrence evidence is incomplete;
- multiple candidate decisions conflict;
- the only apparent decision explicitly says it did not authorize the occurrence, but absence of all other applicable decisions has not yet been established.

These cases fail closed for governance/verification rather than fabricating a binding.

---

## 5. Historical immutability boundary

Once an Integration is `integrated`, the following become historical identity-bearing facts:

```text
id
kind
ref
target_ref
integrated_revision
gate_decision_binding
```

They are immutable across later Project State revisions.

Specifically, after integration:

```text
Bound(D1) -> Bound(D2)   FORBIDDEN
Bound(D)  -> Absent      FORBIDDEN
Absent    -> Bound(D)    FORBIDDEN
Absent    -> another reason FORBIDDEN
integrated -> awaiting_integration FORBIDDEN
integrated -> closed_unmerged FORBIDDEN
```

This is the key protection against retroactive authorization.

A later `PASS` Gate Decision may legitimately become the current decision for current/future work, but it cannot be attached to an earlier `Absent` or earlier `Bound(BLOCKED)` Integration occurrence.

---

## 6. Later PASS behavior

Suppose historical state is:

```text
int-pr82
-> integrated
-> Absent(no_applicable_integration_gate_decision)
-> nonconforming
```

A later Gate review may create:

```text
D_later = PASS
```

if current/future work legitimately requires such a decision.

Legal effect:

```text
D_later may affect current/future actionability
```

Illegal effect:

```text
int-pr82.binding = Bound(D_later)
```

The Integration remains `Absent` historically.

The same rule preserves PR #9:

```text
int-pr9 -> Bound(original BLOCKED decision)
```

A later PASS decision may clear the current blocker but cannot change `int-pr9` to the later PASS decision.

---

## 7. Atomicity

Each logical operation must either commit a valid Project State transition or commit nothing.

For O3/O4, atomic semantic state includes all references required for the new record to be valid:

- Integration record;
- exact integrated revision;
- required occurrence evidence references;
- required governance/absence evidence references for `Absent`;
- any referenced Gate Decision for `Bound`.

Referenced authored records may already exist or may be introduced in the same Project State transaction, but the post-transition manifest set must be self-consistent.

`state.json` remains derived state. It must be recomputed from the authored transition and must not be used to make a partial authored mutation appear valid.

A transition that would leave dangling references or an unrecomputable generated state fails atomically.

---

## 8. Ordering

Manifest insertion order does not determine historical truth.

Ordering comes from durable repository/governance provenance sufficient to establish:

```text
which Gate Decision, if any, was applicable to the actual occurrence
```

A Gate Decision created after a repository occurrence cannot become that occurrence's binding merely because it is the current lineage head when Project State is later reconciled.

The historical occurrence relation must therefore use occurrence-time provenance, not reconciliation-time state.

---

## 9. Idempotency and deduplication

O3/O4 are keyed by stable `Integration.id` plus canonical historical payload.

If replay sees an existing integrated record with exactly the same immutable payload, the operation is an idempotent no-op except for legal evidence append behavior under O6.

If the same `Integration.id` exists with a different immutable payload, replay fails closed with a historical Integration conflict.

There is no last-write-wins behavior for historical bindings.

`Absent` must never be deduced during replay from the absence of a referenced decision.

---

## 10. Replay semantics

A deterministic Project State replay must reproduce the same result from the same durable inputs.

For a historical `Absent` reconciliation, replay must preserve:

```text
same Integration.id
same integrated_revision
same gate_decision_binding.kind = absent
same reason = no_applicable_integration_gate_decision
same conformance = nonconforming
```

Discovery of a later PASS decision during replay must not change that result.

For legacy bound records, replay preserves the exact bound decision identity and derived historical conformance.

---

## 11. Contradictory later evidence

This bounded P13 repair does not define an Integration-history correction lineage.

If later durable evidence contradicts an already-finalized historical binding—for example, an `Absent` occurrence is later proven to have had an applicable decision—normal Project State mutation must not rewrite the record in place.

The contradiction fails closed to Authority/governance review because correcting immutable historical facts requires an explicit correction/supersession contract that is outside P22-F2.

Likewise, a previously bound decision later shown not to have been applicable cannot silently become `Absent`.

---

## 12. Compatibility / migration operation

Whichever replacement Project State Authority is later accepted must provide a deterministic compatibility transform for existing v0.5 Integration records.

For every legacy v0.5 record:

```yaml
gate_decision_id: D
```

transform losslessly to the semantic equivalent:

```yaml
gate_decision_binding:
  kind: bound
  gate_decision_id: D
```

Requirements:

- no existing Gate Decision ID changes;
- no existing historical conformance changes;
- no legacy record is inferred to be `Absent`;
- PR #9 remains bound to its original BLOCKED decision;
- migration must validate the source before transformation;
- migration/replay must be deterministic.

PR #82 is not created by this compatibility transform because it is missing historical persistence, not a legacy bound Integration record. It requires O4 historical reconciliation after the replacement Authority is legally active.

---

## 13. PR #82 reconciliation operation target

After a replacement Authority has been reviewed, verified, accepted, and made applicable, the logical reconciliation target is:

```yaml
operation: RECONCILE_HISTORICAL_INTEGRATION_OCCURRENCE

integration:
  id: int-pr82
  kind: pull_request
  ref: https://github.com/Mostorm-Labs/aegis/pull/82
  target_ref: main
  integrated_revision: 3a2607220cd875dc66857b334dcfbd2c763e7c7d

binding:
  kind: absent
  reason: no_applicable_integration_gate_decision

occurrence_basis:
  - repository merge evidence for PR #82 / 3a260722...

absence_basis:
  - P22-F2 durable review 5553423707
```

This operation must not:

- create a synthetic Gate Contract;
- create a synthetic PASS/BLOCKED Gate Decision;
- bind PR #82 to P23 `5122113780`;
- treat a later decision as historical authorization;
- modify the P23 Authority supersession outcome itself.

P13 defines this as the target mutation semantics only. It does not authorize executing the mutation now.

---

## 14. Error / fail-closed behavior

The operation model requires fail-closed diagnostics for at least these semantic failures:

```text
MISSING_OCCURRENCE_EVIDENCE
ABSENCE_NOT_PROVEN
AMBIGUOUS_GATE_DECISION_BINDING
DANGLING_BOUND_DECISION
AWAITING_INTEGRATION_CANNOT_BE_ABSENT
IMMUTABLE_INTEGRATION_BINDING_CHANGED
INTEGRATED_REVISION_CHANGED
HISTORICAL_INTEGRATION_ID_CONFLICT
NONDETERMINISTIC_REPLAY
```

These are semantic diagnostic classes, not new Aegis lifecycle verdicts.

No failure may be repaired by fabricating a Gate Decision or silently defaulting to `Absent`.

---

## 15. P13 acceptance criteria

P13 is complete when all of the following are explicit:

1. `Absent` can only be established through occurrence reconciliation/finalization with a durable absence basis.
2. Executor identity does not substitute for governance authority.
3. Awaiting Integration remains Bound-only.
4. The actual occurrence binding is resolved at occurrence time, not copied blindly from candidate state.
5. Integrated bindings are immutable across later revisions.
6. A later PASS cannot retroactively replace `Absent` or `Bound(BLOCKED)`.
7. Historical reconciliation is atomic and fail-closed.
8. Replay is deterministic and idempotent.
9. Exact duplicate replay is a no-op; conflicting replay is rejected.
10. Legacy v0.5 bound records migrate losslessly to `Bound`.
11. No legacy record is inferred to be `Absent`.
12. Contradictory later evidence routes to Authority/governance rather than in-place rewrite.
13. PR #82 has a legal target reconciliation operation without being reinterpreted as authorized.
14. P22-F1 persistence remains blocked until the replacement Authority lifecycle is completed.

P13 disposition for this candidate:

```yaml
p13_operation_model:
  scope: aegis/project-state
  finding: P22-F2
  p12_basis: 777e1e8a9652e2cbf220d234798641d65dc9b0c9

  core_operations:
    - REGISTER_AWAITING_INTEGRATION
    - REBIND_AWAITING_INTEGRATION
    - FINALIZE_INTEGRATION_OCCURRENCE
    - RECONCILE_HISTORICAL_INTEGRATION_OCCURRENCE
    - CLOSE_UNMERGED_CANDIDATE
    - APPEND_CORROBORATING_INTEGRATION_EVIDENCE

  absent_creation:
    requires_occurrence_basis: true
    requires_durable_governance_absence_basis: true
    inference_from_missing_data: forbidden

  integrated_binding_mutability: immutable
  later_pass_retroactive_binding: forbidden
  historical_replay: deterministic
  legacy_v0_5_binding_migration: lossless_bound
  replacement_version_assigned: false

  status: READY_FOR_DOWNSTREAM_DESIGN
```

---

## 16. Downstream boundary

P13 does not decide:

- which module/tool owns transition enforcement;
- whether authored manifest shape nests the binding object exactly as illustrated or uses an equivalent serialization;
- how cross-file transition validation is wired into CLI/CI;
- how repository/governance provenance is fetched;
- the verification oracle for proving no applicable decision existed;
- implementation tasks;
- Project State persistence;
- Authority supersession;
- release readiness or publication.

P22 already found architecture drift in the current Project State contract. With P12 and P13 now defined, the next earliest untrusted layer is the architecture boundary for owning and enforcing these transition semantics.

Recommended next Primary, only on a new explicit user turn:

```text
aegis-architecture -> P14 System Architecture
```
