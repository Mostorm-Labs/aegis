# Aegis Control Plane Productization v0.2 — CP-I03 P31 Task Package

Status: **P31 READY / MATERIALIZED — authorized package for later P32 execution**

Package ID: `CP-I03-P31-01`

Owner: `aegis-implementation`

Stage: `P31 Task Packaging`

Target execution stage: `P32 Implementation`

Execution surface: `CONTROL_REASONING`

Preferred later execution surface: `CODE_EXECUTION`

This package defines only:

`CP-I03 — Projection, Policy, Scheduler, and Current Rollout Denial`

It does not start implementation, issue Evidence, or produce a Gate verdict.

---

## 1. Repository execution anchor

Repository:

`Mostorm-Labs/aegis`

Accepted predecessor:

```yaml
task_anchor:
  revision: f820132ab6fb9b2af7754773477fe69af513e83c
  relation: ancestor
resume_cursor: null
```

`Task Anchor != Execution Cursor`.

The anchor is a trusted ancestry baseline, not a requirement that future HEAD remain equal to this revision.

---

## 2. Accepted predecessor boundary

CP-I02:

```yaml
revision: f820132ab6fb9b2af7754773477fe69af513e83c
package_ref: 68a6eebec569b31a468743fd8cd4c1a21ac75952
status: PASS / ACCEPTED_FOR_DOWNSTREAM
p34_comment: 5475361166
```

CP-I03 consumes CP-I02 canonical mutation, CAS, idempotency, and transactional outbox semantics. It does not redesign them.

---

## 3. Current Authority refs

Product:

```text
c628bdc15fdd3d32511a04b6f09055413f2786c3
review: 5061188138
PASS / ACCEPTED_FOR_DOWNSTREAM
```

Modeling:

```text
f29c4da3698038e0174e4380707fa618b03c40b2
review: 5062616510
PASS / ACCEPTED_FOR_DOWNSTREAM
```

Architecture:

```text
e657f0e74771184b98f8c8e6f8a8581e4858c82d
review: 5062769390
PASS / ACCEPTED_FOR_DOWNSTREAM
```

Verification:

```text
db83168e4086e47a7f431acf289006e4f25b8ffd
review: 5062933855
PASS / ACCEPTED_FOR_DOWNSTREAM
```

---

## 4. Objective

Implement the bounded control-loop slice that derives current control state and next legal actions without allowing derived state to become canonical truth.

Required runtime shape:

```text
canonical history
+ supplied external snapshots
        ↓
control-projection
        ↓
derived current state
        ↓
control-policy
        ↓
transient candidate
        ↓
fresh revalidation
        ↓
control-mutation
        ↓
canonical commit
```

---

## 5. Authorized scope

### control-projection

Implement deterministic read-only projection covering:

- ControlCursor
- CurrentMacroPhase
- RepairLineage
- OpenEscalations
- NextLegalAction
- LifecycleSummary

Projection must be:

- deterministic;
- rebuildable;
- disposable;
- cache-safe.

### control-policy

Implement policy evaluation for:

- legal candidate evaluation;
- Control Autonomy checks;
- Current rollout authorization;
- fail-closed missing/ambiguous policy handling.

### control-scheduler

Implement transient candidate generation only.

Scheduler may:

- derive candidate;
- submit candidate to mutation.

Scheduler may not:

- write canonical state;
- append StageOccurrence;
- bypass CAS.

### control-mutation integration

All accepted candidates must return through the existing mutation boundary for:

- fresh state validation;
- lane CAS;
- idempotency;
- canonical commit.

---

## 6. Explicit non-goals

P32 MUST NOT implement:

- dispatch worker;
- external provider dispatch;
- Current cross-Primary autonomous continuation;
- canonical projection/status/cursor writes;
- policy-generated Gate truth;
- policy-generated Authority truth;
- CP-I04 historical trust;
- CP-I05 dispatch/reconciliation/resume;
- CP-I06 repair recovery loop;
- CP-I07 platform adapter implementation;
- R0/S0/performance claims.

---

## 7. Frozen invariants

1. Projection is derived state, never canonical truth.
2. Projection cannot mutate lifecycle history.
3. Stale projection cannot authorize mutation.
4. Scheduler candidate is transient.
5. Candidate commit requires fresh mutation revalidation.
6. `control-mutation` remains the only canonical writer.
7. Architecture capability does not imply Current rollout authorization.
8. Current cross-Primary rollout remains DENIED unless separately authorized by Current Authority.
9. One StageOccurrence has one Primary owner.
10. Primary A never performs Primary B substantive work in the same occurrence.
11. Cache, pause, lease, or coordination state cannot create canonical history.
12. Same-state scheduler races converge through CP-I02 CAS.
13. Terminalization and successor scheduling remain separate durable transitions.

---

## 8. Required tests / oracle obligations

Required P32 evidence must cover:

### Projection differential

Production projection compared against independent semantic oracle paths.

### Stale state rejection

```text
candidate derived from state N
canonical state advances
candidate submitted
=> fail closed or re-evaluate
```

### Rollout policy matrix

Cover:

- permitted same-owner progression;
- cross-Primary semantic next action;
- architecture-capable but Current-denied rollout;
- missing policy basis;
- stale projection/policy basis.

### Scheduler race

Two candidates from the same state must produce:

- at most one canonical winner;
- zero stale residue;
- CP-I02 CAS decides the winner.

### Derived-state isolation

Verify:

- cache rebuild/drop;
- stale cache;
- pause state;
- lease-like operational state

cannot alter canonical history alone.

---

## 9. Evidence obligations

Required EvidenceArtifacts:

```text
CPV-E-OWNERSHIP-ROLLOUT
CPV-E-DERIVED-STATE
CPV-E-CANONICAL-CONFORMANCE (scheduler/CAS extension)
```

Evidence must bind:

- exact CP-I03 package_ref;
- exact result revision;
- CP-I02 accepted predecessor;
- Authority refs;
- runtime/tool versions;
- test identities;
- evidence digests.

Evidence compiler output is not a Gate verdict.

---

## 10. Exit criteria

Zero tolerance:

```text
unauthorized_auto_schedules = 0
unofficial_gate_decisions_accepted = 0
stale_projection_authorization = 0
cache_pause_lease_only_canonical_mutations = 0
```

Required final condition:

```text
Current cross-Primary rollout = DENIED exactly as governed
```

---

## 11. Blocked return behavior

If implementation requires:

- changing accepted CP-I02 semantics;
- weakening rollout restrictions;
- redefining projection ownership;
- changing Authority meaning;

return `BLOCKED_AUTHORITY` or the applicable existing blocker.

Do not repair upstream semantics inside P32.

---

## 12. Surface handoff contract

Later transition:

```yaml
type: surface_handoff
stage: P32
stage_owner: aegis-implementation
from_surface: CONTROL_REASONING
to_surface: CODE_EXECUTION
preferred_executor: codex
package_ref: <this package ref>
task_anchor:
  revision: f820132ab6fb9b2af7754773477fe69af513e83c
  relation: ancestor
resume_cursor: null
return_surface: CONTROL_REVIEW
```

P31 completion stops here.

Next legal action:

`P32 CODE_EXECUTION`
