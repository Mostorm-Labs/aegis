# Aegis Project State — P12 Ungated Integration Semantic Schema Repair

Status: **P12 Semantic Schema Repair Candidate**

Scope: `aegis/project-state`

Triggering finding: `P22-F2 = MISSING_CONTRACT / SPEC_DEFECT`

Repository basis: `main@3a2607220cd875dc66857b334dcfbd2c763e7c7d`

Current Authority under repair: `aegis-project-state-v0.5`

This artifact defines a bounded semantic repair candidate. It is not Current Authority, does not assign a replacement Project State version, does not modify `.aegis/*`, and does not authorize repository integration, release, or rollout.

---

## 1. Problem boundary

Project State v0.5 currently requires every Integration lifecycle record to bind an exact `gate_decision_id`.

That model covers two historical cases:

1. an applicable Gate Decision existed and was `PASS` / `PASS_WITH_FINDINGS`;
2. an applicable Gate Decision existed and was `BLOCKED_*`.

It does not cover a third real repository state:

> an Integration occurrence happened, but no applicable integration-relevant Gate Decision was in force for that occurrence.

PR #82 is the concrete exposing occurrence. It is a real repository integration at `3a2607220cd875dc66857b334dcfbd2c763e7c7d`, while P23 review `5122113780` explicitly did not authorize the merge and no separate applicable P24/P34 integration-authorizing decision existed before the occurrence.

The repair must make that historical state representable without fabricating, erasing, or retroactively broadening governance history.

---

## 2. Preserved semantic truths

The following v0.5 semantics remain inherited unless a later stage explicitly proves they must change:

```text
Gate Contract
!=
Gate Review Decision
!=
Current Gate Decision
!=
Integration-bound Gate Decision
```

Also preserved:

- Gate Decisions are immutable historical decision occurrences.
- A later Gate Decision never rewrites an earlier Gate Decision.
- A later Gate Decision never retroactively authorizes an earlier Integration occurrence.
- Integration occurrence is distinct from Gate conformance, current applicability, and current actionability.
- A repository occurrence proven to have happened is never erased because governance was missing or violated.
- `state.json` remains generated state, not independent Authority.
- Existing v0.5 Gate Decision lineage semantics are not reopened by this repair.

---

## 3. Core semantic repair

The v0.5 assumption that every Integration lifecycle record has exactly one applicable Gate Decision is too strong.

Replace that total relation with an explicit **Gate Decision Binding** value object.

Canonical meaning:

```text
Integration
  -> Gate Decision Binding
       -> Bound(exact Gate Decision)
       OR
       -> Absent(explicitly no applicable Gate Decision for the occurrence)
```

This is not a nullable foreign key.

`Absent` is a positive historical assertion. It means the absence of an applicable Gate Decision has itself been established as repository/governance truth. Missing data, persistence lag, unresolved evidence, or an unknown decision identity must never be interpreted as `Absent`.

---

## 4. Canonical schema

### 4.1 Integration identity

Existing Integration identity remains stable:

```text
Integration.id
```

The repair does not create a second Integration identity and does not create a synthetic Gate Decision.

### 4.2 Gate Decision Binding

Each Integration lifecycle record carries exactly one explicit binding state:

```yaml
gate_decision_binding:
  kind: bound | absent
```

#### Bound form

```yaml
gate_decision_binding:
  kind: bound
  gate_decision_id: <exact immutable Gate Decision id>
```

Meaning:

> an applicable Gate Decision existed for this Integration lifecycle occurrence/action, and this is its exact identity.

The referenced decision may be PASS or BLOCKED. Binding does not imply authorization.

#### Absent form

```yaml
gate_decision_binding:
  kind: absent
  reason: no_applicable_integration_gate_decision
```

Meaning:

> for this already-realized Integration occurrence, no applicable Gate Decision existed in force that governed or authorized the occurrence.

The initial reason vocabulary is intentionally closed to exactly:

```text
no_applicable_integration_gate_decision
```

Additional absence reasons require a later Authority change; they must not be invented as implementation conveniences.

---

## 5. Status-specific optionality

The repair is deliberately narrow.

### `awaiting_integration`

Must remain `bound`.

```text
awaiting_integration
-> exact current PASS / PASS_WITH_FINDINGS Gate Decision
```

An awaiting future action without an applicable authorizing decision is not an actionable Integration candidate.

`absent` is invalid for `awaiting_integration`.

### `integrated`

May be either:

```text
bound
or
absent
```

This is the only lifecycle state for which the new `absent` variant is introduced by this repair.

### `closed_unmerged`

Remains `bound` under the bounded repair.

No broader redesign of abandoned/unreviewed candidate semantics is authorized by P22-F2.

---

## 6. Validation invariants

The replacement semantic contract must reject all ambiguous combinations.

### Bound invariants

```text
kind = bound
=> gate_decision_id is required and non-empty
=> referenced Gate Decision must exist
=> absence reason must not be present
```

### Absent invariants

```text
kind = absent
=> status must equal integrated
=> gate_decision_id must not be present
=> reason must equal no_applicable_integration_gate_decision
```

### No implicit default

The following is invalid under the replacement semantic contract:

```yaml
gate_decision_id: null
```

or simply omitting all binding information.

Neither means `absent`.

The binding state must be explicit so that "historically absent" cannot be confused with "not yet persisted", "unknown", or "broken reference".

---

## 7. Historical conformance

Gate Decision Binding and Integration conformance remain distinct dimensions.

For an `integrated` occurrence:

```text
Bound(PASS / PASS_WITH_FINDINGS)
-> conformance = conforming

Bound(BLOCKED_*)
-> conformance = nonconforming

Absent(no_applicable_integration_gate_decision)
-> conformance = nonconforming
```

The third case must remain distinguishable from the second through its binding state/reason.

Therefore Project State must be able to state both:

```text
int-pr9
-> Bound(BLOCKED_EVIDENCE decision)
-> nonconforming
```

and:

```text
int-pr82
-> Absent(no_applicable_integration_gate_decision)
-> nonconforming
```

without pretending those histories are equivalent.

A later PASS decision may clear a current Gate blocker if legitimately created for current/future work, but it must never replace an `Absent` historical binding on an already-integrated occurrence.

---

## 8. Applicability and actionability

The existing semantic split remains:

```text
Integration Occurrence
!=
Gate Conformance
!=
Current Applicability
!=
Current Actionability
```

An `Absent` historical binding:

- proves neither current authorization nor current blocking Gate state;
- must not synthesize a fake Gate Contract or fake Gate Decision;
- must remain visible as historical nonconformance;
- must not, by itself, create a fictional current `BLOCKED_*` Gate verdict.

Any current remediation requirement must come from actual Current Authority / Gate / governance findings, not from inventing a Gate Decision for the old occurrence.

---

## 9. PR #82 canonical representation target

The semantic target is equivalent to:

```yaml
id: int-pr82
kind: pull_request
ref: https://github.com/Mostorm-Labs/aegis/pull/82
status: integrated
target_ref: main
integrated_revision: 3a2607220cd875dc66857b334dcfbd2c763e7c7d

gate_decision_binding:
  kind: absent
  reason: no_applicable_integration_gate_decision

evidence_ids:
  - <durable occurrence evidence to be registered downstream>
```

The placeholder evidence identity is intentionally not assigned by P12. Evidence registration and proof sufficiency remain downstream responsibilities.

This representation does **not** say:

- P23 `5122113780` authorized the merge;
- a Gate Decision existed but was lost;
- PR #82 is conforming;
- a later PASS may be attached retroactively.

---

## 10. Illegal repairs

The following remain forbidden:

```text
PR #82 -> P23 5122113780 as merge authorization
```

because that review explicitly did not authorize repository integration.

Also forbidden:

```text
later PASS -> old PR #82 occurrence
```

as retroactive authorization.

Also forbidden:

```text
missing gate_decision_id == absent
```

because absence must be explicit historical truth, not inferred from incomplete state.

Also forbidden:

```text
create synthetic BLOCKED or PASS decision solely to satisfy schema shape
```

because that fabricates a governance occurrence that did not happen.

---

## 11. Versioning and compatibility

This P12 stage does not assign a replacement schema version.

Compatibility requirements for whichever replacement Authority is later accepted:

1. existing v0.5 records with `gate_decision_id` must map losslessly to `gate_decision_binding.kind = bound`;
2. existing Gate Contract IDs and Gate Decision IDs remain unchanged;
3. existing historical conformance derived from bound decisions remains unchanged;
4. PR #9 must remain bound to its original BLOCKED decision and remain historically nonconforming;
5. v0.5 projects remain interpreted using v0.5 semantics until an explicit migration/supersession occurs;
6. no old v0.5 manifest is silently reinterpreted as containing `Absent` bindings.

---

## 12. Extensibility boundary

This repair intentionally does not generalize into a universal "missing governance" taxonomy.

The semantic extension is exactly one new state:

```text
integrated occurrence
+
explicit absence of an applicable Integration Gate Decision
```

Future requirements such as:

- unknown historical Gate identity;
- corrupted governance provenance;
- imported repositories with unverifiable history;
- intentionally policy-exempt integrations;

are not represented by this repair and require their own Authority analysis if they arise.

---

## 13. P12 acceptance criteria

P12 is semantically complete when all of the following hold:

1. PR #82 can be represented without inventing a Gate Decision.
2. Historical repository occurrence remains durable truth.
3. Absence is explicit and cannot be confused with missing persistence.
4. Existing bound PASS/BLOCKED histories preserve their exact meaning.
5. `awaiting_integration` still requires an exact current PASS/PASS_WITH_FINDINGS decision.
6. No later decision can semantically retro-authorize the old occurrence.
7. Gate Decision lineage itself is unchanged.
8. The repair introduces no product requirement change.
9. No replacement Project State version is assumed by P12.
10. Unaffected Project State semantics are inherited.

P12 disposition for this candidate:

```yaml
p12_semantic_schema:
  scope: aegis/project-state
  finding: P22-F2
  semantic_gap: TOTAL_GATE_DECISION_BINDING_CANNOT_REPRESENT_CONFIRMED_ABSENCE
  repair: EXPLICIT_GATE_DECISION_BINDING_SUM_TYPE
  new_integrated_state: ABSENT_NO_APPLICABLE_INTEGRATION_GATE_DECISION
  product_change: none
  gate_lineage_change: none
  historical_truth_preserved: true
  retroactive_authorization: forbidden
  replacement_version_assigned: false
  status: READY_FOR_DOWNSTREAM_MODELING
```

---

## 14. Downstream handoff boundary

This P12 candidate does not define mutation/transition mechanics for how a binding becomes durable or how an already-integrated binding is protected across later manifest revisions. Those rules belong to P13 Operation / Mutation Model.

It also does not define implementation architecture, verification oracles, implementation packages, persistence changes, Gate review, supersession, release readiness, or release publication.

Recommended next stage, only after an explicit user turn:

```text
aegis-modeling -> P13 Operation / Mutation Model
```

P13 should define the append/transition rules necessary to preserve an `Absent` historical binding and prevent later mutation into a retroactive `Bound` decision.
