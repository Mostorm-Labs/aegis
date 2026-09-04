# Aegis Control Plane Productization v0.2 — P02/P03 Review Repair

Status: **Draft / Proposed Product Authority — P02/P03 normative repair**

Scope: `aegis/control-plane-productization`

Base candidate:

- `docs/control-plane-productization-v0.2.md`
- reviewed head: `14b0f459dfd9f826753cb29055da11deede26082`
- Product Authority Review: `5061176924`
- review verdict: `BLOCKED_AUTHORITY`

This amendment repairs only the two blocking product/capability contracts identified by that review:

- B1 — macro lifecycle ordering versus verification-bound implementation;
- B2 — autonomous cross-owner orchestration versus the current Multi-Skill composition contract.

All product directions explicitly accepted by the review remain unchanged unless this amendment is more specific.

---

# 1. B1 repair — macro lifecycle is ordered, and acceptance design belongs before BUILD execution

The default macro lifecycle is an **ordered user-facing progression**:

```text
DEFINE -> BUILD -> PROVE -> SHIP
```

It is a projection over internal P-stages, not a replacement lifecycle.

The normative macro meanings are amended to:

```text
DEFINE
  Problem
  Product / semantic Authority
  Contract
  Acceptance / Verification Design

BUILD
  Implementation Plan
  Implementation Package
  Implementation / Repair execution

PROVE
  Evidence compilation / materialization
  Reverification
  Independent review / Gate

SHIP
  Integration
  Release
  Feedback
```

## 1.1 DEFINE exit condition

A work item may leave DEFINE for executable BUILD only when all required execution prerequisites are trustworthy enough for the selected control policy.

For implementation work this includes, at minimum where applicable:

- trusted Authority / Contract basis;
- accepted scope boundary;
- required VerificationSpec / acceptance contract;
- required oracle / pass semantics;
- required Evidence compilation contract;
- Gate / review policy;
- Control Autonomy / repair policy.

Therefore:

> An implementation package MUST NOT become autonomously executable merely because code scope is defined. Required acceptance / verification semantics must already exist.

This preserves the internal dependency:

```text
Authority / Contract
  -> Verification Design
  -> Implementation Planning / Package
  -> Implementation
  -> Evidence
  -> Gate
```

## 1.2 PROVE does not mean “design verification after implementation”

Within the macro UX, PROVE means **execute and accept the already-defined proof contract**, not invent the proof contract after BUILD.

PROVE primarily contains:

- evidence compilation from structured observations;
- required test/probe execution results where execution is part of proof;
- reverification after authorized repair;
- independent completeness/conformance review;
- Gate decisions.

Verification Design belongs to DEFINE even if proof execution happens later in PROVE.

## 1.3 Re-entry semantics

The macro progression is ordered but not irreversible.

If BUILD or PROVE discovers a genuine earlier-layer defect, the Control Plane must route to the earliest untrusted layer and the macro projection moves backward accordingly.

Examples:

```text
PROVE finds MISSING_CONTRACT
-> earliest untrusted layer = semantic Authority / Contract
-> macro projection = DEFINE

BUILD finds implementation-only defect
-> remains BUILD

PROVE finds evidence-only defect within authorized repair scope
-> automatic repair may re-enter BUILD for the repair occurrence
-> then returns to PROVE
```

A backward macro projection is not history rewrite. Prior occurrences remain durable history.

## 1.4 Current macro phase derivation

`current_macro_phase` is a generated projection of the earliest active/incomplete required macro responsibility for the current work occurrence.

It is not an authored Authority field that may override internal stage truth.

If internal lifecycle facts disagree with a cached macro label, internal authoritative lifecycle facts win and the projection is regenerated.

---

# 2. B2 repair — automatic continuation schedules separate Stage Occurrences

The product goal remains zero-user-turn continuation across unambiguous stages.

This does **not** authorize direct substantive Primary-to-Primary chaining.

The normative control rule is:

> **Automatic continuation is Control Plane scheduling across separately owned Stage Occurrences, not ownership transfer from Primary A to Primary B.**

## 2.1 Stage Occurrence

A Stage Occurrence is one bounded substantive execution of an internal lifecycle stage/family under exactly one Primary owner.

Conceptually:

```text
StageOccurrence
  stage
  scope / work occurrence
  trusted input refs
  primary_owner
  control policy
  terminal result / blocker
  durable transition facts
```

The exact object/schema belongs to P10-P13. This P02/P03 repair freezes only the ownership semantics.

For every substantive Stage Occurrence:

1. exactly one Primary owner exists once substantive execution begins;
2. that Primary may not execute another Primary's stage under its own ownership;
3. terminal output is materialized/recorded sufficiently for the Control Plane to determine the next legal transition;
4. the next stage, if any, is a new separately owned occurrence.

## 2.2 Orchestrator role

The Control Plane orchestrator is a scheduler/coordinator, not a universal substantive owner.

It may:

- observe trusted durable state;
- determine the next legal stage/owner according to governed routing policy;
- create/schedule a new Stage Occurrence;
- transport exact refs internally between surfaces;
- persist routing/repair/audit metadata;
- stop/escalate when policy requires.

It may not, merely by being the orchestrator:

- become the semantic owner of specialist stages;
- issue another owner's substantive verdict;
- repair Authority without the owning stage;
- weaken proof/Gate requirements;
- treat orchestration metadata as new Authority.

## 2.3 Automatic continuation example

Desired zero-user-turn behavior:

```text
Occurrence A
stage = P14
owner = aegis-architecture
-> terminal READY result
-> durable result boundary

Control Plane
-> evaluates next legal action
-> schedules new occurrence

Occurrence B
stage = P20
owner = aegis-verification
-> terminal READY result
-> durable result boundary

Control Plane
-> schedules new occurrence

Occurrence C
stage = P30/P31
owner = aegis-implementation
```

This is allowed product behavior **only when an explicit Control Plane orchestration contract has been governed and accepted**.

It must not be represented as:

```text
aegis-architecture -> aegis-verification -> aegis-implementation
```

inside one continuously owned substantive execution.

## 2.4 Relationship to current Multi-Skill composition Authority

The current composition contract remains controlling until explicitly reconciled/superseded.

Current constraints that remain valid include:

- one Primary substantive owner at a time;
- no Primary may steal another stage's ownership;
- router/support metadata does not become substantive Authority;
- earlier blockers fail closed.

However, the current default prohibition on automatic multi-stage substantive continuation is now classified as an **impacted Authority contract** for vNext productization.

Specifically, the future Control Plane design/implementation must explicitly reconcile at least:

- `aegis/skill/decomposition` composition semantics;
- `aegis/execution-surface` transport/return semantics where orchestration crosses execution surfaces.

This P02/P03 candidate does not silently supersede those Current Authorities.

Before autonomous cross-owner continuation can become Current implementation behavior, downstream governance must establish an explicit orchestration workflow contract that extends/reconciles them.

## 2.5 Separate workflow authorization

The required future orchestration contract must authorize the workflow itself, not grant one Primary broader ownership.

At minimum it must specify:

- what event closes one Stage Occurrence;
- what durable facts permit scheduling the next occurrence;
- how the next owner is derived;
- which transitions may be automatic;
- which transitions require HUMAN_DECISION;
- how exact refs are carried without user copy/paste;
- how independent-review boundaries remain independent;
- how loops/retries are bounded;
- how each autonomous transition is audited;
- how divergence/stale state terminates the loop.

Until that contract exists, the product requirement is accepted direction only, not permission for existing Skills to violate Current composition semantics.

---

# 3. Control Autonomy clarification

The existing orthogonal Control Autonomy axis is retained:

```text
AUTONOMOUS
REVIEW_GUARDED
HUMAN_DECISION
```

This amendment freezes the following separation:

```text
Proof Assurance
  -> how strong proof must be

Gate / Review Policy
  -> what independently owned review/decision is required before trust

Control Autonomy
  -> whether the Control Plane may schedule the next allowed occurrence without asking the user
```

`REVIEW_GUARDED` means:

- implementation/mechanical routing may proceed automatically within authorized scope;
- a separately owned required review occurrence must complete with an acceptable decision before downstream trust is granted;
- the user need not be interrupted merely because that review exists;
- unresolved review exceptions still escalate according to policy.

Therefore this combination is explicitly valid:

```text
Proof Assurance = QUALIFIED
Gate Policy = independent P34 required
Control Autonomy = REVIEW_GUARDED
User round trips on clean path = 0
```

Low interaction never implies low assurance.

---

# 4. P03 capability traceability repair

The capability model is amended with explicit Authority impact:

| Requirement | Capability | Current reusable contract | vNext impact |
|---|---|---|---|
| CP-FR02 Automatic Routing | Stage Scheduler / Router | stage ownership + central routing rules | extend with governed cross-occurrence automatic scheduling |
| CP-FR03 Cross-Surface Orchestration | Orchestrator / internal transport | Execution Surface v0.2 | reconcile transport so handoff payload is system-managed |
| CP-FR04 Auto Repair | Repair Loop Controller | P34/P35/P36 ownership semantics | schedule separate repair/review occurrences; do not merge owners |
| CP-FR08 Verification-Bound Package | Package readiness policy | P20 + P31 contracts | verification/acceptance design is DEFINE prerequisite to executable BUILD |
| CP-FR09 Macro UX | Macro Projection | existing lifecycle stage truth | DEFINE includes Verification Design; PROVE executes/accepts proof |
| CP-FR10 Sessionless Resume | Control Cursor projection | Project State + Execution Cursor | orchestrator resumes from durable state and schedules next occurrence |

Impacted Authority set for downstream reconciliation includes at least:

```text
aegis/skill/decomposition
aegis/execution-surface
```

Potential Project State impact remains expected but is not declared as semantic supersession at P02/P03; P10-P14 must determine whether Persistent Control State extends Project State or introduces a separate governed control-state boundary.

---

# 5. Product acceptance criteria added by this repair

The Control Plane product requirement is not satisfied unless all of the following are true:

1. The default macro progression is unambiguously `DEFINE -> BUILD -> PROVE -> SHIP`.
2. Required Verification/Acceptance Design is completed in DEFINE before autonomous implementation execution can enter BUILD.
3. PROVE means proof execution/evidence/review/Gate, not late invention of acceptance semantics.
4. Earlier-layer discoveries may move the macro projection backward without rewriting historical occurrences.
5. Automatic cross-owner continuation creates a new separately owned Stage Occurrence.
6. Exactly one Primary owner exists per substantive Stage Occurrence.
7. One Primary never gains authority to execute another Primary's stage merely because continuation is automatic.
8. The orchestrator coordinates/schedules but is not the substantive owner of every stage.
9. Current no-direct-Primary-chain semantics are treated as an impacted Authority requiring explicit downstream reconciliation, not silently ignored.
10. An accepted future orchestration workflow contract is required before Current Skills may perform zero-user-turn multi-stage continuation.
11. Proof Assurance, Gate Policy, and Control Autonomy remain distinct.
12. A QUALIFIED + independent-review workflow can still target zero user round trips on the clean path.

---

# 6. Explicitly unchanged accepted direction

This amendment does not reopen:

- Persistent Control State as a product requirement;
- immutable occurrences + generated current projections;
- Trusted Basis != Control Cursor != Execution Cursor;
- bounded automatic repair loops;
- escalation-only UX;
- Evidence Compiler from ProofContract/oracle semantics + structured observations;
- Verification Productization PR #23/#24 as retained Proof Plane foundation;
- sessionless resume;
- autonomous transition auditability;
- fail-closed loop termination;
- no new P-stage merely for orchestration;
- independent review preservation.

---

# 7. Repair disposition

B1 — Macro lifecycle ordering: **REPAIRED IN CANDIDATE**

B2 — Composition/orchestration Authority impact: **REPAIRED IN CANDIDATE**

The combined proposed Product Authority package for PR #25 is now:

```text
docs/control-plane-productization-v0.2.md
+ docs/control-plane-productization-v0.2-p02-p03-repair.md
```

The prior Product Authority Review `5061176924` remains historical and applies to the earlier exact head only.

This repair is still Draft/Proposed and requires a fresh Product Authority Review before P10/P11 may consume it as accepted downstream product truth.

Next earliest untrusted layer after successful review:

**P10 Product Object Model / P11 Interaction Behavior for the Control Plane.**
