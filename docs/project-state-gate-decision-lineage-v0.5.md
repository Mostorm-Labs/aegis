# Aegis Project State Gate Decision Lineage v0.5

Status: **Proposed Replacement Authority v0.5 — P21/P22 complete; P20 verification design complete; P32 implementation complete; P34 acceptance pending.**

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
      "id": "gate-skill-decomposition-v02-pr9::decision::0001",
      "gate_id": "gate-skill-decomposition-v02-pr9",
      "verdict": "BLOCKED_EVIDENCE",
      "evidence_ids": ["ev-pr9-task6-preflight"]
    },
    {
      "id": "gate-skill-decomposition-v02-pr9::decision::0002",
      "gate_id": "gate-skill-decomposition-v02-pr9",
      "verdict": "PASS",
      "evidence_ids": ["ev-pr9-task6-current"],
      "supersedes": "gate-skill-decomposition-v02-pr9::decision::0001"
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

Every v0.5 Gate Contract must have at least one Gate Decision.

### Gate Decision rules

A Gate Decision has:

- stable `id`;
- `gate_id`;
- immutable `verdict`;
- immutable `evidence_ids[]` as the evidence set used for that decision occurrence;
- optional `supersedes`, which points to the immediately previous decision for the same Gate.

Decision records are append-only governance facts. A later review must create a new decision ID.

Decision IDs are deterministic and sequential within one Gate lineage:

```text
<gate-id>::decision::0001
<gate-id>::decision::0002
<gate-id>::decision::0003
...
```

The decimal suffix is four-digit zero-padded and monotonically increases by one. Migration creates `0001`; each later P34 re-review appends the next sequence number.

## Decision lineage

For every Gate:

1. `supersedes` must reference another decision for the same Gate.
2. A decision may supersede at most one previous decision.
3. A decision may be superseded by at most one later decision.
4. Cycles are invalid.
5. Exactly one unsuperseded decision must exist.
6. All decisions for the Gate must belong to one connected linear lineage rooted at `::decision::0001`.
7. More than one unsuperseded head, a disconnected decision, or a sequence gap is invalid manifest state and fails closed before downstream routing; the diagnostic route is `P21`.
8. The unique unsuperseded head is the **Current Gate Decision**.

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

The existing `blocking_gates[]` projection remains in v0.5 for compatibility and contains Gate Contract IDs whose **current decision head** is an active BLOCKED verdict. v0.5 additionally exposes `blocking_gate_decisions[]` with the exact decision IDs.

## Integration semantics

v0.5 Integrations bind to a specific Gate Decision, not merely to a mutable Gate Contract.

Canonical v0.5 shape:

```json
{
  "id": "int-pr9",
  "kind": "pull_request",
  "ref": "https://github.com/Mostorm-Labs/aegis/pull/9",
  "gate_decision_id": "gate-skill-decomposition-v02-pr9::decision::0001",
  "status": "integrated",
  "target_ref": "main",
  "evidence_ids": ["ev-pr9-merged"],
  "integrated_revision": "a0c6b0103b119f517c7adf9ec4a90b5963e5e1e3"
}
```

For v0.5, every Integration lifecycle record must bind the exact decision relevant to that occurrence/action:

- `integrated`: the decision in force for the actual integration occurrence;
- `awaiting_integration`: the current PASS/PASS_WITH_FINDINGS decision authorizing the proposed integration;
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
      "decision_id": "gate-skill-decomposition-v02-pr9::decision::0002",
      "verdict": "PASS"
    }
  ],
  "blocking_gates": [],
  "blocking_gate_decisions": [],
  "integration_conformance": [
    {
      "integration_id": "int-pr9",
      "gate_decision_id": "gate-skill-decomposition-v02-pr9::decision::0001",
      "conformance": "nonconforming"
    }
  ],
  "nonconforming_integrations": ["int-pr9"]
}
```

## Evidence semantics

Evidence remains separate from decisions.

A Gate Decision records which evidence IDs supported that decision occurrence. The decision's `evidence_ids[]` membership is immutable after that decision is authored. Evidence registry status may later become unavailable or superseded without mutating the decision's historical verdict.

For a Current Gate Decision:

- unavailable required evidence makes the current decision ineffective for downstream action and routes to verification review;
- the historical verdict remains immutable.

For a superseded historical decision, later evidence availability changes do not reactivate it as a current blocker and do not change historical Integration conformance.

## Migration from v0.4

v0.5 is opt-in. v0.4 manifests retain exact v0.4 behavior.

A deterministic migration from v0.4 to v0.5 must:

1. preserve every existing Gate ID as a Gate Contract ID;
2. create exactly one `::<decision>::0001`-style legacy decision for each v0.4 Gate using the existing verdict and evidence IDs, specifically `<gate-id>::decision::0001`;
3. preserve the original Gate stage and Authority set on the Gate Contract;
4. replace each Integration's `gate_id` with the corresponding generated `gate_decision_id`;
5. preserve every Integration occurrence status, target, revision, and occurrence evidence;
6. reproduce the same pre-migration current blockers and Integration conformance before any new decision is appended;
7. introduce no nondeterministic timestamps or generated IDs.

After migration, a later re-review appends `::decision::0002`, then `0003`, and so on.

## Backward compatibility

- v0.3 continues to use v0.3 semantics.
- v0.4 continues to use v0.4 semantics.
- only v0.5 enables Gate Decision lineage.
- mixed schema versions within one Project State manifest set remain invalid.

No v0.5 behavior may reinterpret historical v0.3/v0.4 projects unless those manifests are explicitly migrated to v0.5.

## PR #9 reconciliation target

Once v0.5 itself passes P34 and is promoted through P23:

1. migrate the root Project State to v0.5;
2. preserve the original PR #9 decision as `BLOCKED_EVIDENCE` in `gate-skill-decomposition-v02-pr9::decision::0001`;
3. bind `int-pr9` permanently to that original decision;
4. append `gate-skill-decomposition-v02-pr9::decision::0002` carrying the accepted 4/4 installed-platform evidence and verdict `PASS`;
5. make `0002` the unique current lineage head;
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
6. **Fork fail-closed:** two unsuperseded decision heads, disconnected lineages, or sequence gaps are rejected and diagnosed as requiring `P21`.
7. **Lineage integrity:** cross-Gate supersession, dangling decision refs, decision cycles, duplicate decision IDs, and Integration refs to missing decisions are rejected.
8. **Awaiting integration safety:** `awaiting_integration` requires the current-effective PASS/PASS_WITH_FINDINGS decision and cannot use a historical/superseded/blocked decision.
9. **Migration equivalence:** deterministic v0.4 → v0.5 migration reproduces the pre-migration v0.4 current blockers, applicability, and conformance before any new decision is appended.
10. **Version isolation:** v0.3 and v0.4 regression behavior remains unchanged.
11. **Root PR #9 proof:** after migrating the root fixtures/state and appending the new PR #9 PASS decision, `int-pr9` remains `nonconforming` while `gate-skill-decomposition-v02-pr9` has no active blocker.
12. **Self-host integrity:** v0.5 schemas parse, root manifests validate, generated `state.json` is reproducible, and the existing Aegis Skillset/Project State/evaluation regressions remain green.

## P32 implementation evidence

Implementation is isolated on PR #14. Root `.aegis/*` remains v0.4; no root migration or Authority promotion is included in the P32 slice.

RED evidence:

- Initial v0.5 lineage/migration oracle: Project State run `33234280222` failed before v0.5 schemas/tooling existed while legacy tests remained green.
- Cross-snapshot immutability oracle: Project State run `33234756600` failed because `tools.aegis_state.transition_v05` did not yet exist; the remaining Project State suite was green.

Fresh exact-head GREEN evidence for commit `43513094bdb36c638d59c8552a4fbf2d51f10538`:

- Aegis Project State Integrity run `33234803966`: PASS.
- v0.3/v0.4/v0.5 schema JSON parsing: PASS.
- v0.4 minimal manifest validation/check: PASS / `STATE_OK`.
- v0.5 minimal manifest validation/check: PASS / `STATE_OK`.
- Project State tests: `74/74 PASS`, including immutable-transition, lineage integrity, migration equivalence, and root PR #9 reconciliation.
- Root v0.4 manifest validation/check: PASS / `STATE_OK`.
- Aegis Skillset validation: PASS; Skillset regressions: `71/71 PASS` on this branch baseline.
- Evaluation corpus validation: `34` cases PASS; evaluation regressions: `34/34 PASS`.

The exact-head workflow intentionally runs Project State, Skillset, and evaluation regressions together so P34 does not have to infer cross-system safety from an older commit.

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
P20 Verification Design     COMPLETE
  ↓
P30 Implementation Plan     COMPLETE
  ↓
P31 Task Packages           COMPLETE
  ↓
P32 RED-first implementation COMPLETE
  ↓
P34 independent Gate Review ← NEXT
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
