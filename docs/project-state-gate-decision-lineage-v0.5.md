# Aegis Project State Gate Decision Lineage v0.5

Status: **Proposed Replacement Authority v0.5 — P21/P22 complete; P20 verification design and P34 acceptance pending.**

Previous Authority: [Project State v0.4](project-state-manifest-v0.4.md), which remains Current until this replacement passes its Gate and is superseded through P23.

## Problem statement

F09-07 exposed a missing Project State contract: a Gate currently stores both the durable identity of the Gate and the latest review verdict in one mutable record. That is insufficient when the same Gate is reviewed more than once.

The concrete failure mode is PR #9:

```text
P34 review #1
→ BLOCKED_EVIDENCE
→ repository integration still occurred
→ int-pr9 correctly records a nonconforming occurrence

later
→ missing platform evidence is supplied
→ P34 re-review now passes
```

Under v0.4, changing the existing Gate verdict from `BLOCKED_EVIDENCE` to `PASS` would also change the historical conformance of `int-pr9` from `nonconforming` to `conforming`, because Integration conformance is derived from the currently stored verdict on the referenced Gate. That would rewrite repository/governance history.

## F09-07 classification

```text
Finding                  = F09-07
Name                     = Gate Decision Historical Identity Gap
Primary                  = MISSING_CONTRACT
Secondary                = SPEC_DEFECT
Earliest Untrusted Layer = Authority
Owning Authority         = Project State
Start Stage              = P21
Review Stage             = P22
Repair                   = Project State replacement Authority v0.5
```

## P22 Five-Axis Drift Review

1. **Product Drift:** none. Aegis still requires evidence-gated progression and truthful history.
2. **Semantic Drift:** present. v0.4 conflates a Gate contract with a particular Gate review decision.
3. **Architecture Drift:** present. Project State lacks a durable Gate Decision identity and lineage boundary.
4. **Implementation Drift:** present. Integration conformance reads a mutable Gate verdict rather than an immutable decision occurrence.
5. **Verification Drift:** present. Existing tests do not prove that a later PASS can coexist with an earlier BLOCKED decision while preserving historical nonconformance.

## Core semantic split

v0.5 introduces this invariant:

```text
Gate Contract
!=
Gate Review Decision
!=
Current Gate Decision
!=
Integration-bound Gate Decision
```

Definitions:

- **Gate Contract**: the stable Gate identity: what stage is reviewed and which Authority scopes govern it.
- **Gate Review Decision**: one immutable P34 decision occurrence with its own verdict and evidence set.
- **Current Gate Decision**: the unique unsuperseded lineage head for a Gate Contract.
- **Integration-bound Gate Decision**: the exact historical decision that authorized or failed to authorize a repository integration occurrence.

A later review creates a new decision. It never mutates a previous decision's verdict.

## v0.5 manifest model

`gates.json` remains the single Gate manifest. v0.5 separates stable Gate contracts from immutable decisions:

```json
{
  "schema_version": "0.5",
  "gates": [
    {
      "id": "gate-skill-decomposition-v02-pr9",
      "stage": "P34",
      "authority_ids": ["aegis-skill-decomposition-v0.2"]
    }
  ],
  "decisions": [
    {
      "id": "gate-decision-pr9-p34-01",
      "gate_id": "gate-skill-decomposition-v02-pr9",
      "verdict": "BLOCKED_EVIDENCE",
      "evidence_ids": ["ev-pr9-task6-preflight"]
    },
    {
      "id": "gate-decision-pr9-p34-02",
      "gate_id": "gate-skill-decomposition-v02-pr9",
      "verdict": "PASS",
      "evidence_ids": ["ev-pr9-task6-current"],
      "supersedes": "gate-decision-pr9-p34-01"
    }
  ]
}
```

### Gate Contract rules

A Gate Contract has:

- stable `id`;
- `stage`;
- `authority_ids[]`.

The contract does not carry a mutable review verdict. Its effective validity is derived from its Authority set.

### Gate Decision rules

A Gate Decision has:

- stable `id`;
- `gate_id`;
- immutable `verdict`;
- immutable `evidence_ids[]` as the evidence set used for that decision occurrence;
- optional `supersedes`, which points to the immediately previous decision for the same Gate.

Decision records are append-only governance facts. A later review must create a new decision ID.

## Decision lineage

For every Gate:

1. `supersedes` must reference another decision for the same Gate.
2. A decision may supersede at most one previous decision.
3. A decision may be superseded by at most one later decision.
4. Cycles are invalid.
5. Exactly one unsuperseded decision must exist when a Gate has decisions.
6. More than one unsuperseded head is an unresolved decision fork and fails closed to `P21`.
7. The unique unsuperseded head is the **Current Gate Decision**.

Historical decisions remain queryable and retain their original verdicts and evidence.

## Current actionability

Current blockers are derived only from the Current Gate Decision for an effective-current Gate Contract.

```text
current decision = BLOCKED_AUTHORITY
→ authority / P21

current decision = BLOCKED_EVIDENCE
→ verification / P34

current decision = BLOCKED_IMPLEMENTATION
→ implementation / P35

current decision = BLOCKED_ENVIRONMENT
→ verification / P34

current decision = PASS or PASS_WITH_FINDINGS
→ no active Gate blocker
```

A superseded BLOCKED decision remains historical evidence but is not an active blocker.

## Integration semantics

v0.5 Integrations bind to a specific Gate Decision, not merely to a mutable Gate Contract.

Canonical v0.5 shape:

```json
{
  "id": "int-pr9",
  "kind": "pull_request",
  "ref": "https://github.com/Mostorm-Labs/aegis/pull/9",
  "gate_decision_id": "gate-decision-pr9-p34-01",
  "status": "integrated",
  "target_ref": "main",
  "evidence_ids": ["ev-pr9-merged"],
  "integrated_revision": "a0c6b0103b119f517c7adf9ec4a90b5963e5e1e3"
}
```

For v0.5, every Integration lifecycle record must bind the exact decision relevant to that occurrence/action:

- `integrated`: the decision in force for the actual integration occurrence;
- `awaiting_integration`: the PASS/PASS_WITH_FINDINGS decision authorizing the proposed integration;
- `closed_unmerged`: the final decision associated with that completed candidate.

The Gate Contract is reached through `gate_decision_id -> decision.gate_id`; duplicating a second authored `gate_id` on the Integration is intentionally avoided to prevent drift.

## Historical conformance

For an `integrated` occurrence:

```text
referenced decision verdict PASS / PASS_WITH_FINDINGS
→ conforming

referenced decision verdict BLOCKED_*
→ nonconforming
```

This conformance is permanently tied to the referenced immutable Gate Decision.

Therefore the PR #9 sequence becomes:

```text
D1 = BLOCKED_EVIDENCE
int-pr9 → D1
int-pr9 conformance = nonconforming

D2 = PASS
D2 supersedes D1
Current Gate Decision = D2
Current blocker = cleared

int-pr9 still → D1
int-pr9 conformance remains nonconforming
```

No later Gate review can retroactively authorize an earlier repository occurrence.

## Generated state v0.5

The generated state preserves existing useful projections and adds decision identity explicitly.

Required projections include:

```json
{
  "current_gate_decisions": [
    {
      "gate_id": "gate-skill-decomposition-v02-pr9",
      "decision_id": "gate-decision-pr9-p34-02",
      "verdict": "PASS"
    }
  ],
  "blocking_gate_decisions": [],
  "integration_conformance": [
    {
      "integration_id": "int-pr9",
      "gate_decision_id": "gate-decision-pr9-p34-01",
      "conformance": "nonconforming"
    }
  ],
  "nonconforming_integrations": ["int-pr9"]
}
```

`blocking_gates[]` may remain as a compatibility projection of Gate IDs, but it must be derived from the current decision head rather than from historical decisions.

## Evidence semantics

Evidence remains separate from decisions.

A Gate Decision records which evidence IDs supported that decision occurrence. Evidence status can later become unavailable/superseded without mutating the decision's historical verdict. That may affect whether the decision can support current actionability, but it must not rewrite the historical decision itself.

For a Current Gate Decision:

- unavailable required evidence makes the current decision ineffective for downstream action and routes to verification review;
- the historical verdict remains immutable.

## Migration from v0.4

v0.5 is opt-in. v0.4 manifests retain exact v0.4 behavior.

A deterministic migration from v0.4 to v0.5 must:

1. preserve every existing Gate ID as a Gate Contract ID;
2. create exactly one legacy decision for each v0.4 Gate using the existing verdict and evidence IDs;
3. preserve the original Gate stage and Authority set on the Gate Contract;
4. replace each Integration's `gate_id` with the corresponding generated legacy `gate_decision_id`;
5. preserve every Integration occurrence status, target, revision, and occurrence evidence;
6. reproduce the same pre-migration current blockers and Integration conformance before any new decision is appended;
7. introduce no nondeterministic timestamps or generated IDs.

Legacy decision IDs must be deterministic from the Gate identity. The exact naming rule is part of implementation authority and must be frozen before coding; recommended form:

```text
<gate-id>::decision::0001
```

A later re-review appends `::0002`, `::0003`, and so on within that Gate lineage.

## Backward compatibility

- v0.3 continues to use v0.3 semantics.
- v0.4 continues to use v0.4 semantics.
- only v0.5 enables Gate Decision lineage.
- mixed schema versions within one Project State manifest set remain invalid.

No v0.5 behavior may reinterpret historical v0.3/v0.4 projects unless those manifests are explicitly migrated to v0.5.

## PR #9 reconciliation target

Once v0.5 itself passes P34 and is promoted through P23:

1. migrate the root Project State to v0.5;
2. preserve the original PR #9 decision as `BLOCKED_EVIDENCE`;
3. bind `int-pr9` permanently to that original decision;
4. append a new PR #9 P34 decision carrying the accepted 4/4 installed-platform evidence and verdict `PASS`;
5. make the new PASS decision the unique current lineage head;
6. confirm `int-pr9` remains `nonconforming` historical truth;
7. then execute Skill Decomposition v0.2 P23 supersession.

## Non-goals

v0.5 does not:

- reinterpret PR #9's historical merge as conforming;
- alter the Gate verdict vocabulary;
- make repository integration evidence count as Gate acceptance evidence;
- change Authority supersession semantics;
- change Skill routing/ownership semantics;
- introduce a general event-sourcing system;
- require a new manifest file solely for Gate decisions;
- automatically retry or rerun Gates.

## P20 verification design / acceptance contract

The replacement Authority is not accepted until executable evidence proves all of the following:

1. **Immutable blocked history:** a BLOCKED decision cannot be mutated into PASS in-place under the v0.5 model.
2. **Re-review PASS:** the same Gate Contract can append a later PASS decision that supersedes the blocked decision.
3. **Unique current head:** current Gate verdict/actionability is derived from the unique unsuperseded decision head.
4. **Historical integration preservation:** an Integration bound to the old BLOCKED decision remains `nonconforming` after the new PASS decision becomes current.
5. **Blocker clearance:** the superseded historical BLOCKED decision does not remain in current blockers.
6. **Fork fail-closed:** two unsuperseded decision heads for one Gate are rejected or route deterministically to `P21` as unresolved Authority/Gate state.
7. **Lineage integrity:** cross-Gate supersession, dangling decision refs, decision cycles, duplicate decision IDs, and Integration refs to missing decisions are rejected.
8. **Awaiting integration safety:** `awaiting_integration` requires a current-effective PASS/PASS_WITH_FINDINGS decision and cannot use a historical/superseded/blocked decision.
9. **Migration equivalence:** deterministic v0.4 → v0.5 migration reproduces the pre-migration v0.4 current blockers, applicability, and conformance before any new decision is appended.
10. **Version isolation:** v0.3 and v0.4 regression behavior remains unchanged.
11. **Root PR #9 proof:** after migrating the root fixtures/state and appending the new PR #9 PASS decision, `int-pr9` remains `nonconforming` while `gate-skill-decomposition-v02-pr9` has no active blocker.
12. **Self-host integrity:** v0.5 schemas parse, root manifests validate, generated `state.json` is reproducible, and the existing Aegis Skillset/Project State/evaluation regressions remain green.

## Required lifecycle

```text
F09-07
  ↓
P21 Authority Review        COMPLETE
  ↓
P22 Five-Axis Drift Review  COMPLETE
  ↓
Project State v0.5 Proposed Replacement Authority
  ↓
P20 Verification Design
  ↓
P30 Implementation Plan
  ↓
P31 Task Packages
  ↓
P32 RED-first implementation
  ↓
P34 independent Gate Review
  ↓ PASS
P23 Project State v0.4 → v0.5 supersession
  ↓
root manifest migration
  ↓
PR #9 new PASS decision
  ↓
Skill Decomposition v0.2 P23 supersession
```

Until Project State v0.5 passes its own P34 Gate, v0.4 remains Current and no historical Gate verdict may be rewritten.