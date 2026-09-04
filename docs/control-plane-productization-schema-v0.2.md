# Aegis Control Plane Productization v0.2 — P12 Semantic Schema

Status: **Draft / Proposed Authority — P12 Semantic Schema**

Scope: `aegis/control-plane-productization`

Upstream accepted Product Authority:

- `docs/control-plane-productization-v0.2.md`
- `docs/control-plane-productization-v0.2-p02-p03-repair.md`
- accepted candidate head: `c628bdc15fdd3d32511a04b6f09055413f2786c3`

Upstream P10/P11 model:

- `docs/control-plane-productization-model-v0.2.md`
- exact model head before P12: `b84201d692e167d5022635f30875aa6655000056`

Retained external semantic dependencies, referenced rather than duplicated:

- Verification Productization / Proof Plane candidate on PR #23, accepted semantic head `2eb7d507098d24328b883dfa1366521390026fce`;
- Project State v0.5 Gate Decision lineage as Current repository Authority;
- Execution Surface v0.2 `Task Anchor != Execution Cursor` semantics as Current repository Authority.

This document freezes P12 identity, field meaning, serialization, validation, versioning, compatibility, and generated-projection rules. It does **not** define P13 mutations, P14 storage topology, or implementation classes.

---

# 1. Canonical-state boundary

The Control Plane has exactly three first-class durable object families in v0.2:

```text
StageOccurrence
VerificationBoundImplementationPackage
Escalation
```

Embedded value/reference types:

```text
CanonicalRef
TrustedBasis
PolicyBinding
RepairPolicy
ScheduleBasis
RepairContext
ExecutionNavigationSnapshot
```

Generated-only projections:

```text
ControlCursor
CurrentMacroPhase
RepairLineage
OpenEscalations
NextLegalAction
LifecycleSummary
```

There is no new first-class `WorkItem`, `Workflow`, `Handoff`, `RepairAttempt`, `ExecutionCursor`, `Finding`, `GateDecision`, `VerificationSpec`, or `EvidenceArtifact` aggregate merely for orchestration convenience.

Durable orchestration metadata still does not become Authority, Evidence, Gate, Integration, Project State, or Proof.

Normal users are not required to author or transport exact refs, digests, P-stage IDs, execution cursors, or repair lineage. Those remain internal/audit-facing semantics.

---

# 2. Canonical serialization

All canonical Control Plane records have UTF-8 JSON semantics even if a later architecture persists them as YAML, rows, objects, or another equivalent representation.

Common envelope:

```yaml
schema_version: "0.2"
kind: <record kind>
id_scheme: <kind-specific scheme>
id: <stable object identity>
record_revision: <positive integer>
recorded_at: <RFC3339 UTC timestamp>
...
extensions: {}
```

Rules:

1. `schema_version` is exactly `"0.2"`.
2. `kind`, `id_scheme`, `id`, `record_revision`, `recorded_at`, and `extensions` are required.
3. `id` is stable across immutable revisions of the same object lineage.
4. `record_revision` starts at `1` and increments monotonically by one.
5. Every materialized record revision is immutable.
6. `recorded_at` is audit metadata only; it does not establish Authority, precedence, causal order, or trust.
7. Unknown authored top-level fields are invalid. Compatible extensions use namespaced `extensions`.

Canonical digests use:

```text
RFC 8785 JSON Canonicalization Scheme
+ SHA-256
```

Text form:

```text
sha256:<64 lowercase hex characters>
```

A digest excludes only the field that stores that same digest.

---

# 3. Identity schemes

Runtime occurrence identities must not collapse repeated attempts with identical semantic inputs.

```text
StageOccurrence
  id_scheme = stage-occurrence-v0.2
  id        = so_<UUIDv7>

VerificationBoundImplementationPackage
  id_scheme = verification-bound-package-v0.2
  id        = pkg_<UUIDv7>

Escalation
  id_scheme = escalation-v0.2
  id        = esc_<UUIDv7>

Control lane key
  lane_<UUIDv7>
```

UUIDv7 follows RFC 9562. IDs are opaque; encoded time/order does not itself establish lifecycle truth.

Package ID identifies one package lineage. A materially changed authorized package becomes a new immutable `record_revision` with a changed digest. A retry, repair, reverify, or re-review is always a new `StageOccurrence` ID.

---

# 4. CanonicalRef

`CanonicalRef` is the common exact-reference value:

```yaml
object_type: AUTHORITY | CONTRACT | STAGE_OCCURRENCE |
             VERIFICATION_SPEC | PROOF_OBLIGATION_SET |
             IMPLEMENTATION_PACKAGE | RESULT | EVIDENCE |
             PROOF_EVALUATION | GATE_DECISION | INTEGRATION |
             FINDING | EXECUTION_CURSOR | EXTERNAL_DECISION
id: <stable referenced identity>
ref: <system/reviewer-resolvable durable reference>
identity:
  scheme: <git-sha | sha256 | semantic-version | native-immutable-id | governed scheme>
  value: <exact identity value>
```

Rules:

1. `id`, `ref`, `identity.scheme`, and `identity.value` are required.
2. `ref` must resolve without ambiguity.
3. `identity` pins the exact referenced revision/content/immutable occurrence.
4. A mutable location with no exact identity is invalid at a trust boundary.
5. `native-immutable-id` is allowed only when the referenced contract guarantees immutability.
6. Referencing an external object never transfers semantic ownership of that object into the Control Plane.

---

# 5. TrustedBasis

`TrustedBasis` is an immutable embedded value, not an aggregate:

```yaml
trusted_basis:
  authority_refs:
    - <CanonicalRef object_type=AUTHORITY>
  contract_refs:
    - <CanonicalRef object_type=CONTRACT>
  verification_refs:
    - <CanonicalRef object_type=VERIFICATION_SPEC or PROOF_OBLIGATION_SET>
  accepted_fact_refs:
    - <CanonicalRef object_type=GATE_DECISION | RESULT | INTEGRATION | EXTERNAL_DECISION>
  basis_digest: <sha256 digest>
```

Rules:

1. `authority_refs` is non-empty for substantive downstream occurrences unless the owning stage is itself establishing Authority.
2. Ref arrays are canonically sorted by `(object_type, id, identity.scheme, identity.value)` before digesting.
3. `basis_digest` is derived, never free-authored.
4. Historical occurrences retain their pinned basis after later Authority supersession.
5. A new occurrence cannot silently reuse a basis that is no longer effective for the new work.
6. Accepted facts may constrain continuation without becoming Authority.
7. Conversation history, handoff prose, or executor claims cannot substitute for TrustedBasis.

---

# 6. PolicyBinding and RepairPolicy

The accepted dimensions remain distinct:

```text
Proof Assurance
!= Gate / Review Policy
!= Control Autonomy
```

Proof Assurance stays owned by pinned Verification/Proof truth; the Control Plane does not duplicate it as a local enum.

`RepairPolicy`:

```yaml
allowed_classes:
  - <governed defect/change classification>
max_attempts: <integer >= 0>
require_reverification: true | false
require_fresh_independent_review: true | false
escalation_conditions:
  - <governed reason code>
```

`PolicyBinding`:

```yaml
policy_binding:
  gate_policy_ref: <CanonicalRef object_type=CONTRACT>
  control_autonomy: AUTONOMOUS | REVIEW_GUARDED | HUMAN_DECISION
  repair_policy: <RepairPolicy>
  policy_digest: <sha256 digest>
```

Rules:

1. `gate_policy_ref` is required whenever downstream trust depends on a Gate/review contract.
2. `control_autonomy` is required.
3. `max_attempts` is finite.
4. Repair policy cannot authorize Authority invention, semantic scope expansion, proof/Gate weakening, or destructive/irreversible action merely by naming a class.
5. `policy_digest` is derived from the complete canonical binding.

A valid target therefore remains possible without conflation:

```text
Proof Assurance = QUALIFIED     # resolved from Proof Plane
Gate Policy     = independent P34 required
Control Autonomy= REVIEW_GUARDED
clean-path user round trips = 0
```

---

# 7. StageOccurrence

## 7.1 Stage span and ownership

```yaml
stage_span:
  stages: [P10, P11]
primary_owner: aegis-modeling
```

Rules:

1. `stages` is non-empty, ordered, unique, and uses canonical P-stage IDs.
2. One occurrence may cover multiple contiguous stages only when all map to the same Primary owner.
3. Cross-Primary spans are invalid.
4. `stage_family` is derived, not authored.

This permits one bounded P10/P11 modeling occurrence while still forbidding a single `P14 -> P20` occurrence across different owners.

## 7.2 Immutable occurrence revisions

A StageOccurrence is durable before completion and never rewritten in place.

Minimum lineage:

```text
record_revision 1: OPEN
record_revision N: TERMINAL
```

P13 may define additional monotonic intermediate revisions but may not change prior revision content.

Canonical shape:

```yaml
schema_version: "0.2"
kind: STAGE_OCCURRENCE
id_scheme: stage-occurrence-v0.2
id: so_<uuidv7>
record_revision: <positive integer>
recorded_at: <timestamp>
control_lane_id: lane_<uuidv7>
stage_span:
  stages: [P12]
primary_owner: aegis-modeling
state: OPEN | TERMINAL
trusted_basis: <TrustedBasis>
policy_binding: <PolicyBinding>
schedule_basis: <ScheduleBasis>
input_refs:
  - <CanonicalRef>
repair_context: null | <RepairContext>
execution_navigation: null | <ExecutionNavigationSnapshot>
terminal: null | <TerminalFacts>
extensions: {}
```

For `OPEN`:

- `terminal` is null;
- stage span, owner, TrustedBasis, policy, schedule basis, inputs, and repair context are frozen for the occurrence.

For `TERMINAL`:

```yaml
terminal:
  outcome_category: COMPLETED | BLOCKED | ESCALATED | FAILED_WITH_FINDING
  status: READY | READY_WITH_FINDINGS |
          BLOCKED_AUTHORITY | BLOCKED_MISSING_INPUT |
          BLOCKED_UNRESOLVED_DECISION | BLOCKED_EVIDENCE |
          BLOCKED_IMPLEMENTATION | BLOCKED_ENVIRONMENT
  produced_refs:
    - <CanonicalRef>
  finding_refs:
    - <CanonicalRef object_type=FINDING>
  raised_escalation_ids:
    - esc_<uuidv7>
  resolved_escalation_ids:
    - esc_<uuidv7>
  earliest_untrusted_layer: null | <canonical stage/layer>
  navigation_result: null | <ExecutionNavigationSnapshot>
```

Terminal rules:

1. `outcome_category` is the P11 interaction category; `status` uses existing Aegis workflow status vocabulary.
2. `READY`/`COMPLETED` on a non-P34 occurrence never means official Gate `PASS`.
3. A P34 occurrence references the immutable external `GATE_DECISION`; it does not duplicate that verdict as new Gate truth.
4. Blocked outcomes preserve the earliest trusted owning layer when known.
5. Produced results are exact refs, not agent prose.
6. `next_stage`, `next_owner`, and `current_macro_phase` are forbidden authored terminal fields.

---

# 8. ScheduleBasis

`ScheduleBasis` explains why an occurrence was allowed to start without becoming Authority:

```yaml
schedule_basis:
  predecessor_occurrence_ref: null | <CanonicalRef object_type=STAGE_OCCURRENCE>
  reason_code: USER_REQUEST | NEXT_LEGAL_STAGE | RESUME |
               REPAIR | REVERIFY | REREVIEW | EARLIER_LAYER_ROUTE
  derived_from_basis_digest: <TrustedBasis.basis_digest>
```

Automatic authorization comes from the pinned `PolicyBinding`, not from `reason_code` alone.

A Primary terminal result does not author its successor. The successor's schedule basis records the Control Plane's separately derived transition.

---

# 9. RepairContext / RepairLineage

There is no `RepairAttempt` aggregate. Each attempt is a separately owned StageOccurrence with:

```yaml
repair_context:
  finding_ref: <CanonicalRef object_type=FINDING>
  root_occurrence_ref: <CanonicalRef object_type=STAGE_OCCURRENCE>
  previous_attempt_occurrence_ref: null | <CanonicalRef object_type=STAGE_OCCURRENCE>
  attempt_ordinal: <integer >= 1>
  repair_policy_digest: <PolicyBinding.policy_digest>
```

Rules:

1. First attempt has ordinal `1` and no previous attempt.
2. Later attempts point to exactly one immediately previous repair occurrence.
3. One lineage retains the same root finding identity.
4. Ordinals are contiguous and cannot exceed policy `max_attempts`.
5. Remaining budget is derived.
6. Authority/semantic-scope repair routes to the earlier owning layer rather than masquerading as implementation repair.

`RepairLineage` is a generated traversal over these immutable occurrence links.

---

# 10. ExecutionNavigationSnapshot

The accepted product requires sessionless resume, but current Execution Surface semantics must remain intact.

Internal snapshot:

```yaml
execution_navigation:
  execution_surface: CONTROL_REASONING | CODE_EXECUTION |
                     CONTROL_REVIEW | CODE_REVERIFY
  task_anchor:
    revision: <exact revision>
    relation: ancestor
  execution_cursor:
    execution_ref: <branch or durable execution ref>
    revision: <exact accepted revision>
    completed_through:
      - <verified completed step identity>
    next_action: <first incomplete verified step identity>
```

Rules:

1. `Task Anchor != Execution Cursor` remains controlling.
2. The cursor preserves the last Control-Plane-accepted execution position only.
3. It cannot authorize new files, semantics, scope, or Authority.
4. It is not Evidence, Gate, Proof, or Integration truth.
5. Historical expected-HEAD equality is not reintroduced as a resume oracle.
6. P34 must still independently resolve reviewer-accessible materialized result/evidence.
7. Moving cursor state does not revise the implementation package.
8. Physical reconciliation with the Current Execution Surface contract is deferred to P14/P21; this P12 only freezes the semantic snapshot required by the accepted product requirement.

---

# 11. VerificationBoundImplementationPackage

Canonical shape:

```yaml
schema_version: "0.2"
kind: VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE
id_scheme: verification-bound-package-v0.2
id: pkg_<uuidv7>
record_revision: <positive integer>
recorded_at: <timestamp>
control_lane_id: lane_<uuidv7>
trusted_basis: <TrustedBasis>
scope:
  scope_id: <stable semantic work-scope identity>
  scope_contract_ref: <CanonicalRef object_type=CONTRACT>
verification_binding:
  verification_spec_ref: <CanonicalRef object_type=VERIFICATION_SPEC>
  obligation_set_ref: null | <CanonicalRef object_type=PROOF_OBLIGATION_SET>
  acceptance_oracle_refs:
    - <CanonicalRef object_type=CONTRACT>
  evidence_compilation_contract_ref: <CanonicalRef object_type=CONTRACT>
policy_binding: <PolicyBinding>
task_anchor: null | { revision: <exact revision>, relation: ancestor }
package_digest: <sha256 digest>
extensions: {}
```

Rules:

1. `verification_spec_ref` is required before autonomous implementation execution.
2. The package references Proof Plane truth and does not copy Claim statements, ProofContract semantics, or locally redefine obligations.
3. `obligation_set_ref` may be null only when the governing verification contract explicitly permits later obligation materialization without changing semantics.
4. Acceptance oracle refs point to canonical contracts, never executor summaries.
5. `scope_contract_ref` is the authoritative package scope boundary; execution cannot widen it.
6. `policy_binding` preserves Gate/Autonomy/Repair separation without retyping Proof Assurance.
7. `task_anchor` is required when repository execution depends on a repository baseline.
8. `resume_cursor` is forbidden as a package field because it is moving navigation state.
9. Any material change to TrustedBasis, scope, verification bindings, policy binding, or required task anchor creates a new immutable package revision and digest.
10. A changed VerificationSpec/ProofContract identity cannot silently retarget an existing execution.

---

# 12. Escalation

An Escalation is an immutable raised trust interruption, not a mutable ticket.

```yaml
schema_version: "0.2"
kind: ESCALATION
id_scheme: escalation-v0.2
id: esc_<uuidv7>
record_revision: 1
recorded_at: <timestamp>
control_lane_id: lane_<uuidv7>
raised_from_occurrence_ref: <CanonicalRef object_type=STAGE_OCCURRENCE>
trusted_basis_digest: <digest>
category: AUTHORITY_CONFLICT | MISSING_CONTRACT | PRODUCT_DECISION |
          SEMANTIC_SCOPE_EXPANSION | RISK_OR_ASSURANCE_CHANGE |
          IRREVERSIBLE_ACTION | ORACLE_CREDIBILITY |
          REPAIR_BUDGET_EXHAUSTED | ENVIRONMENT_INTERVENTION |
          UNRESOLVED_MATERIAL_CLASSIFICATION
owning_layer: <canonical stage/layer>
required_decision:
  decision_kind: <governed decision class>
  summary: <compact human-readable question>
evidence_snapshot_refs:
  - <CanonicalRef object_type=EVIDENCE | RESULT | FINDING | GATE_DECISION>
extensions: {}
```

Rules:

1. Escalation records why autonomy stopped; it does not answer the decision.
2. Resolution is later durable truth from a separately owned StageOccurrence or governed external decision that lists the escalation ID in `resolved_escalation_ids`.
3. `open/resolved` is generated state; Escalation has no mutable status field.
4. Later resolution never rewrites the original category, evidence snapshot, or question.
5. A materially different decision creates another Escalation instead of mutating the existing one.

---

# 13. Generated Control State

Generated state may be cached, but canonical objects and referenced external truth remain authoritative.

Recommended projection:

```yaml
projection_version: "0.2"
control_lane_id: lane_<uuidv7>
generated_from:
  canonical_record_digests: []
  external_ref_identities: []
control_cursor:
  trusted_basis_digest: <current digest>
  active_occurrence_ref: null | <CanonicalRef object_type=STAGE_OCCURRENCE>
  last_terminal_occurrence_ref: null | <CanonicalRef object_type=STAGE_OCCURRENCE>
  current_package_ref: null | <CanonicalRef object_type=IMPLEMENTATION_PACKAGE>
  current_stage_span: null | [Pxx, ...]
  current_owner: null | <Primary owner>
  execution_cursor: null | <ExecutionNavigationSnapshot.execution_cursor>
current_macro_phase: DEFINE | BUILD | PROVE | SHIP
next_legal_action:
  stage_span: null | [Pxx, ...]
  primary_owner: null | <owner>
  control_action: CONTINUE | WAIT_FOR_REVIEW | REPAIR |
                  REVERIFY | REREVIEW | ESCALATE | COMPLETE | NONE
  reason_code: <derived reason>
open_escalation_ids: []
repair_lineages:
  - root_finding_ref: <CanonicalRef>
    attempt_occurrence_refs: []
    attempts_used: <integer>
    attempts_remaining: <integer>
lifecycle_summary:
  status: <existing workflow status>
  trusted_result_ref: null | <CanonicalRef>
  exception_count: <integer>
```

Projection rules:

1. Every field is derived; authored edits are invalid.
2. Cached projection conflict is resolved by regenerating from canonical/external truth.
3. Non-unique or contradictory derivation fails closed.
4. `current_macro_phase` derives from the earliest active/incomplete required responsibility and never overrides P-stage truth.
5. `next_legal_action` derives from lifecycle, TrustedBasis, policy, blockers, and required independent review. A Primary does not author its own successor.
6. Open Escalations are those with no valid later resolution binding.
7. Repair lineage is derived from `RepairContext` links.
8. Execution cursor may aid resume but never proves correctness.

---

# 14. Project State v0.5 boundary

P12 does not redefine Current Project State semantics.

The Control Plane reuses by exact reference:

- Authority registry identities/status;
- Gate Contract and immutable Gate Decision identities;
- Integration occurrence/conformance identities;
- existing blocker/Gate semantics where Current Authority owns them.

Therefore:

1. A StageOccurrence references `GATE_DECISION`; it never keeps a second mutable Gate verdict.
2. A generated Control view may display current Gate state, but Project State remains the source of Gate Decision lineage until separately governed change.
3. Integration remains a Project State lifecycle record, not a Control Plane aggregate.
4. This Draft does not modify root `.aegis` manifests or `.aegis/authorities.json`.
5. Whether Persistent Control State later extends Project State storage or remains separate is a P14 architecture question plus later governance, not a P12 assumption.

---

# 15. Proof Plane boundary

The retained Verification Productization model remains semantic owner of:

```text
VerificationSpec
Claim
ProofContract
CoverageBasis
ProofObligation
EvidenceArtifact / EvidenceInputRef
ProofEvaluation
Proof Assurance
```

Control Plane rules:

1. Package refs pin exact proof truth without copying it.
2. StageOccurrence may reference ProofEvaluation/Evidence outputs but cannot reinterpret them.
3. Evidence Compiler output remains Proof/Evidence truth.
4. Control Autonomy decides scheduling permission, never proof sufficiency.
5. P34 remains the sole official Gate owner.

---

# 16. Execution Surface v0.2 boundary

Current semantics remain controlling until explicitly reconciled:

```text
Task Anchor != Execution Cursor
Stage Ownership != Execution Surface
resume cursor != Authority/Evidence/Gate
reviewer-accessible materialization required before P34
```

The v0.2 Control Plane candidate adds only this proposed downstream requirement:

- stable task anchor remains package authorization/navigation context;
- moving accepted execution position may be durably snapshotted internally for sessionless resume;
- that snapshot does not become scope authorization or proof;
- repository resume classification remains owned by the execution lifecycle contract.

This is an impacted boundary, not silent supersession.

---

# 17. Validation invariants

A conforming v0.2 state satisfies all of the following.

## Identity / history

1. IDs match their `id_scheme`.
2. Record revisions are append-only and contiguous per lineage.
3. Historical revisions never change.
4. Canonical digests reproduce under RFC 8785 + SHA-256.

## Ownership

5. Every substantive StageOccurrence has exactly one Primary owner.
6. Every stage in one span belongs to that owner.
7. No StageOccurrence crosses a Primary boundary.
8. Scheduler/orchestrator metadata never becomes substantive owner.

## Trust / policy

9. TrustedBasis refs are exact and resolvable at required trust boundaries.
10. Control Autonomy cannot override Proof Assurance or Gate policy.
11. Verification-bound packages lacking required acceptance bindings are not autonomously executable.
12. Stale/diverged required exact refs fail closed.

## Repair

13. Repair lineage is linear and attempt ordinals are contiguous.
14. Attempts cannot exceed bounded policy.
15. Required reverification/re-review cannot be skipped.
16. Authority/semantic repair cannot masquerade as implementation-only repair.

## Escalation

17. Escalation is immutable after raise.
18. Resolution is later durable truth; original escalation remains history.
19. Open/resolved state is derived.

## Projection

20. ControlCursor, macro phase, repair lineage, open escalation, and next legal action are generated only.
21. Cached projection never overrides canonical truth.
22. Ambiguous projection derivation fails closed.

## External ownership

23. Gate Decision semantics are not duplicated from Project State.
24. Verification/Proof semantics are not duplicated into packages.
25. Execution cursor metadata is never correctness evidence.
26. Current composition/execution Authorities are not silently superseded by this Draft.

---

# 18. Versioning / compatibility

Compatible inside schema v0.2:

- namespaced `extensions`;
- additional generated projection fields fully derivable from canonical truth;
- display-only labels that do not affect identity, routing, validation, or trust.

A new semantic schema version is required for:

- changed identity schemes;
- changed required-field meaning/optionality;
- changed stage-ownership validation;
- changed TrustedBasis exactness;
- changed Proof/Gate/Autonomy separation;
- new first-class durable aggregates;
- changed immutable-revision semantics;
- changed repair bounds/lineage meaning;
- changed canonical-vs-generated boundaries.

A v0.2 reader MUST:

1. reject unsupported semantic schema versions at a trust boundary;
2. fail closed on unknown canonical `kind` values;
3. preserve or safely ignore namespaced extensions without interpreting them as Authority;
4. never reinterpret older records under new semantics without explicit migration;
5. never infer canonical compatibility from projection-version compatibility.

---

# 19. User-facing projection constraint

The internal schema may expose exact audit detail through progressive disclosure, but the normal product UX remains:

```text
DEFINE / BUILD / PROVE / SHIP
current status
trusted result
what changed
open exception / required human decision
```

Normal users should not need to see or enter:

```text
UUID occurrence IDs
basis/package/policy digests
P-stage refs
Gate Decision IDs
Git SHAs
handoff/surface fields
repair ordinals
execution cursor internals
```

This is a hard product boundary, not merely a UI preference.

---

# 20. P12 disposition

P12 Semantic Schema is complete as a Draft/Proposed downstream model over the accepted P02/P03 Product Authority and P10/P11 model.

It freezes:

- the three first-class durable object families;
- exact-reference and TrustedBasis semantics;
- record identity and immutable revisioning;
- StageOccurrence stage-span/ownership shape;
- independent Gate/Autonomy/Proof policy boundaries;
- Verification-bound package schema;
- repair attempts as StageOccurrence + RepairContext;
- immutable Escalation semantics;
- execution-navigation snapshot boundary;
- generated ControlCursor/macro/repair/escalation projections;
- Project State / Proof Plane / Execution Surface non-duplication boundaries;
- versioning and compatibility rules.

Next earliest untrusted layer after this P12 candidate:

```text
P13 Operation / Mutation Model — Aegis Control Plane
```

P13 must define append/materialize/terminate/schedule/repair/escalation-resolution operations, atomicity, ordering, idempotency/deduplication, replay, and fail-closed error behavior without redesigning the P12 object model.
