# Aegis Control Plane Productization v0.2 — P10/P11 Object + Interaction Model

Status: **Draft / Proposed Authority — P10 Product Object Model + P11 Interaction Behavior**

Scope: `aegis/control-plane-productization`

Upstream Product Authority:
- `docs/control-plane-productization-v0.2.md`
- `docs/control-plane-productization-v0.2-p02-p03-repair.md`
- accepted candidate head: `c628bdc15fdd3d32511a04b6f09055413f2786c3`

## Modeling principle

Do not turn every orchestration fact into a product object.

The Control Plane must preserve durable trust history while hiding internal lifecycle transport complexity from users.

Model:

```text
Durable truth
  -> immutable occurrences / packages / findings

Generated control view
  -> cursor / phase / next action / summaries

Internal transport
  -> refs, handoff fields, execution navigation metadata
```

`Code Complete != Gate Complete` and routing metadata never becomes Authority, Evidence, Gate, Integration, or Project State.

---

# P10 Product Object Model

## 1. Durable Objects

## 1.1 StageOccurrence

`StageOccurrence` is the primary durable execution boundary.

Purpose:

Represent one bounded substantive execution of an internal lifecycle stage/family under exactly one Primary owner.

Identity:

- stable occurrence id;
- stage/family;
- work scope identity;
- owner identity;
- lifecycle lineage.

Contains:

- trusted input basis references;
- control policy reference;
- execution surface references when applicable;
- terminal result or blocker;
- durable transition facts.

Rules:

1. One StageOccurrence has exactly one Primary owner once substantive execution begins.
2. A Primary owner cannot execute another Primary's stage inside the same occurrence.
3. Completion creates a durable boundary from which the Control Plane may schedule a new occurrence.
4. Historical occurrences are immutable; later work creates new occurrences.

StageOccurrence is the durable answer to:

"What happened, who owned it, and what trusted result was produced?"

---

## 1.2 VerificationBoundImplementationPackage

A durable authorized work package.

Purpose:

Bind executable implementation work to its acceptance context before execution begins.

Contains references to:

- Authority / Contract basis;
- implementation scope;
- VerificationSpec / proof obligations;
- acceptance oracle;
- evidence compilation contract;
- Gate policy;
- Control Autonomy policy;
- authorized repair policy.

It references proof truth. It does not redefine ProofContract semantics.

Identity:

- package id;
- immutable package revision;
- exact referenced contracts.

---

## 1.3 Escalation

Escalation is a durable trust interruption occurrence.

It records:

- why autonomous continuation stopped;
- owning layer;
- unresolved decision category;
- evidence available at escalation time;
- required human decision.

Escalation is not a replacement workflow.

A resolved escalation does not mutate history; resolution creates new durable facts and may permit a new occurrence.

---

# 2. Value Objects / References

## 2.1 TrustedBasis

TrustedBasis is a pinned reference object, not an independent workflow aggregate.

Meaning:

"What Authority, contracts, packages, and accepted refs constrain this work?"

Contains references to:

- Current Authority basis;
- accepted contract revisions;
- relevant Proof/Gate references;
- exact result ancestry where required.

TrustedBasis is immutable for an occurrence.

A changed basis creates a new occurrence or package revision.

---

## 2.2 ControlPolicy

ControlPolicy is a value/reference describing whether autonomous continuation is allowed.

It does not replace proof or gate policy.

Separate dimensions:

```text
Proof Assurance
  proof strength

Gate / Review Policy
  independent trust decision

Control Autonomy
  allowed automatic continuation
```

Possible autonomy values:

```text
AUTONOMOUS
REVIEW_GUARDED
HUMAN_DECISION
```

---

## 2.3 RepairPolicy

Defines bounded repair behavior:

- allowed repair classes;
- maximum attempts;
- required re-verification/re-review;
- escalation conditions.

It is not a workflow engine.

---

# 3. Generated Projections

## 3.1 ControlCursor

ControlCursor is generated navigation state, not canonical truth.

It answers:

"Where is the control plane currently positioned?"

Derived from:

- active StageOccurrence;
- terminal history;
- current policy;
- unresolved escalations.

It is not:

- Authority;
- Execution Cursor;
- Evidence;
- Gate Decision.

Relationship:

```text
TrustedBasis
    !=
ControlCursor
    !=
ExecutionCursor
```

ExecutionCursor remains repository execution-position metadata.

---

## 3.2 Current Macro Phase

Generated from internal lifecycle truth.

```text
DEFINE
BUILD
PROVE
SHIP
```

It is a user-facing projection only.

Internal P-stage facts win over stale macro labels.

---

## 3.3 RepairLineage Projection

Repair history is derived from immutable repair occurrences.

It shows:

- attempts;
- classifications;
- outcomes;
- remaining budget.

It does not create a second workflow universe.

---

# P11 Interaction Behavior

## 1. Start

Control Plane observes durable state:

1. resolve TrustedBasis;
2. validate no Authority conflict;
3. derive legal next action;
4. create a new StageOccurrence when execution is allowed.

The Control Plane schedules. It does not become stage owner.

---

## 2. Execute

A StageOccurrence executes under one Primary owner.

Possible outcomes:

```text
COMPLETED
BLOCKED
ESCALATED
FAILED_WITH_FINDING
```

Terminal facts are persisted before any next transition.

---

## 3. Continue

Automatic continuation:

```text
StageOccurrence A
        |
        v
terminal durable boundary
        |
Control Plane evaluates policy
        |
StageOccurrence B
```

Not:

```text
aegis-architecture -> aegis-verification
```

inside one ownership chain.

---

## 4. Repair

Repair behavior:

```text
finding
 -> classify
 -> check RepairPolicy
 -> create repair occurrence
 -> materialize result
 -> reverify
 -> independent review
 -> persist lineage
```

Stop and escalate when:

- Authority change is required;
- semantic scope expands;
- repair class is uncertain;
- bounds are exceeded;
- human/environment action is required.

---

## 5. Cancellation

Cancellation stops future scheduling.

Existing occurrences and evidence remain historical.

No rollback of trust history occurs.

---

# P10/P11 Invariants

1. StageOccurrence is the durable unit of substantive lifecycle execution.
2. Exactly one Primary owner exists per substantive StageOccurrence.
3. Control Plane schedules; it does not own specialist semantics.
4. TrustedBasis constrains work but does not become mutable project state.
5. ControlCursor is generated navigation state, not Authority.
6. ExecutionCursor remains separate from ControlCursor.
7. Verification-bound packages reference proof truth without duplicating it.
8. Escalation preserves unresolved trust decisions as durable history.
9. Repair loops create bounded occurrences, not hidden retries.
10. User-facing UX exposes status and exceptions, not internal transport complexity.

---

## Exit

P10/P11 modeling complete.

Next earliest untrusted layer:

P12 Semantic Schema.

P12 must consume this model and define canonical field identity, serialization, validation, versioning, and compatibility rules.
