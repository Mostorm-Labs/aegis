# Aegis Control Plane Productization v0.2 — P12 Semantic Schema

Status: **Draft / Proposed Authority — P12 Semantic Schema**

Scope: `aegis/control-plane-productization`

Upstream accepted Product Authority:

- `docs/control-plane-productization-v0.2.md`
- `docs/control-plane-productization-v0.2-p02-p03-repair.md`
- accepted candidate head: `c628bdc15fdd3d32511a04b6f09055413f2786c3`

Upstream P10/P11 model:

- `docs/control-plane-productization-model-v0.2.md`
- exact model head before this P12 materialization: `b84201d692e167d5022635f30875aa6655000056`

Retained external semantic dependencies, referenced rather than duplicated:

- Verification Productization / Proof Plane candidate on PR #23, accepted semantic head `2eb7d507098d24328b883dfa1366521390026fce`;
- Project State v0.5 Gate Decision lineage as Current repository Authority;
- Execution Surface v0.2 `Task Anchor != Execution Cursor` semantics as Current repository Authority.

This P12 document defines canonical identity, field meaning, serialization, validation, versioning, compatibility, and generated-projection rules for the Control Plane model. It does **not** define P13 mutations, P14 storage topology, or implementation classes.

---

# 1. Schema principles

## 1.1 Canonical truth is small

The canonical Control Plane schema has exactly these first-class durable object families in v0.2:

```text
StageOccurrence
VerificationBoundImplementationPackage
Escalation
```

The following are embedded values/references, not independent aggregates:

```text
CanonicalRef
TrustedBasis
PolicyBinding
RepairPolicy
ScheduleBasis
RepairContext
ExecutionNavigationSnapshot
```

The following are generated projections, never authored canonical truth:

```text
ControlCursor
CurrentMacroPhase
RepairLineage
OpenEscalations
NextLegalAction
LifecycleSummary
```

No `WorkItem`, `Workflow`, `Handoff`, `RepairAttempt`, `ExecutionCursor`, `Finding`, `GateDecision`, `VerificationSpec`, or `EvidenceArtifact` aggregate is recreated inside the Control Plane schema merely for convenience.

## 1.2 Durable does not mean Authority

A durable Control Plane record may preserve audit/navigation facts without becoming semantic Authority, Evidence, Gate, Integration, or Project State.

In particular:

```text
StageOccurrence history
!= Authority

ExecutionNavigationSnapshot
!= Evidence

ControlCursor
!= ExecutionCursor

orchestration metadata
!= semantic contract
```

## 1.3 Internal exactness, external simplicity

Exact refs, digests, stage IDs, routing reasons, cursor snapshots, and repair lineage are internal/audit-facing semantics.

The normal user projection remains limited to:

```text
macro phase
status
trusted result
open exception / human decision
```

P12 MUST NOT require normal users to author or transport internal refs.

---

# 2. Canonical serialization envelope

Every canonical Control Plane record uses UTF-8 JSON semantics, regardless of whether a future implementation stores or displays it as JSON, YAML, database rows, or another equivalent representation.

Canonical records contain:

```yaml
schema_version: "0.2"
kind: <record kind>
id_scheme: <kind-specific identity scheme>
id: <stable object identity>
record_revision: <positive integer>
recorded_at: <RFC3339 UTC timestamp>
...
extensions: {}
```

Rules:

1. `schema_version` is required and exactly `"0.2"` for this contract.
2. `kind` is required and discriminates the record schema.
3. `id_scheme` is required and versioned independently of storage implementation.
4. `id` is stable across immutable revisions of the same semantic object lineage.
5. `record_revision` starts at `1` and increases monotonically by one for later immutable revisions of the same object.
6. A serialized record revision is immutable after materialization.
7. `recorded_at` is audit metadata; it does not establish Authority, precedence, causal order, or trust by itself.
8. `extensions` is required and defaults to `{}`.
9. Unknown authored top-level fields are invalid in v0.2. Forward-compatible additions must use namespaced `extensions` or a new schema version.

Canonical digest calculation uses:

```text
RFC 8785 JSON Canonicalization Scheme
+ SHA-256
```

Digest text form:

```text
sha256:<64 lowercase hexadecimal characters>
```

A record digest is calculated over the full canonical record excluding any containing field whose sole purpose is to store that same record digest.

---

# 3. Common reference schema

## 3.1 CanonicalRef

`CanonicalRef` is the only generic exact-reference value in this schema.

```yaml
object_type: AUTHORITY | CONTRACT | VERIFICATION_SPEC | PROOF_OBLIGATION_SET |
             IMPLEMENTATION_PACKAGE | RESULT | EVIDENCE | PROOF_EVALUATION |
             GATE_DECISION | INTEGRATION | FINDING | EXECUTION_CURSOR |
             EXTERNAL_DECISION
id: <stable referenced identity>
ref: <system/reviewer-resolvable durable reference>
identity:
  scheme: <git-sha | sha256 | semantic-version | native-immutable-id | other governed scheme>
  value: <exact identity value>
```

Rules:

1. `id`, `ref`, `identity.scheme`, and `identity.value` are required.
2. `ref` must resolve to the referenced object or to a registry that resolves the object without ambiguity.
3. `identity` pins the exact referenced revision/content/immutable occurrence.
4. A mutable location with no exact identity is not a valid `CanonicalRef` at a trust boundary.
5. `native-immutable-id` is allowed only when the referenced source contract guarantees immutability of that ID.
6. `object_type` does not transfer ownership of the referenced object's semantics into the Control Plane.

Examples:

```yaml
object_type: GATE_DECISION
id: gate-x::decision::0002
ref: .aegis/gates.json#gate-x::decision::0002
identity:
  scheme: native-immutable-id
  value: gate-x::decision::0002
```

```yaml
object_type: RESULT
id: implementation-result
ref: https://github.com/example/repo/commit/abc...
identity:
  scheme: git-sha
  value: abc...
```

---

# 4. TrustedBasis schema

`TrustedBasis` is an immutable embedded value. It has no independent lifecycle or object ID.

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

1. `authority_refs` is required and non-empty for substantive occurrences unless the owning stage explicitly establishes Authority itself.
2. Arrays are canonically sorted by `(object_type, id, identity.scheme, identity.value)` before `basis_digest` calculation.
3. `basis_digest` is derived from the four canonical ref sets; it is not manually authored semantic truth.
4. A new occurrence cannot silently inherit a basis whose referenced Current Authority has become invalid/superseded for that scope.
5. Historical occurrences retain their original basis even when later Authority changes.
6. `accepted_fact_refs` may constrain continuation but do not become Authority merely because they are included in the basis.
7. Conversation history, executor prose, or handoff text is not a valid TrustedBasis substitute.

---

# 5. Policy schema

## 5.1 Separation invariant

The three accepted policy dimensions remain semantically independent:

```text
Proof Assurance
!= Gate / Review Policy
!= Control Autonomy
```

Proof-strength semantics remain owned by the Verification / Proof Plane and are referenced through exact VerificationSpec/ProofContract truth. The Control Plane does not retype ProofContract semantics.

## 5.2 PolicyBinding

```yaml
policy_binding:
  gate_policy_ref: <CanonicalRef object_type=CONTRACT>
  control_autonomy: AUTONOMOUS | REVIEW_GUARDED | HUMAN_DECISION
  repair_policy:
    allowed_classes:
      - <governed defect/change classification>
    max_attempts: <integer >= 0>
    require_reverification: true | false
    require_fresh_independent_review: true | false
    escalation_conditions:
      - <governed reason code>
  policy_digest: <sha256 digest>
```

Rules:

1. `gate_policy_ref` is required for work whose downstream trust depends on a Gate/review contract.
2. `control_autonomy` is required.
3. `repair_policy.max_attempts` is required and finite.
4. A repair policy cannot authorize Authority/semantic invention, proof weakening, Gate weakening, destructive external action, or scope expansion merely by listing a class.
5. `policy_digest` is derived from the canonical policy binding.
6. Proof Assurance is not duplicated as an authored enum here; required proof strength is resolved from the pinned Verification/Proof truth.

---

# 6. StageOccurrence schema

## 6.1 Identity

```text
id_scheme = stage-occurrence-v0.2
id        = so_<UUIDv7>
```

UUIDv7 follows RFC 9562.

The Control Plane allocates the occurrence ID before scheduling substantive execution. The ID is opaque and carries no semantic Authority.

A retry/repair/new review is a new StageOccurrence ID. Two executions must never collapse to one identity merely because their semantic inputs are identical.

## 6.2 Stage span

One occurrence may cover one or more contiguous stages only when all stages are owned by the same Primary owner under the governing stage-ownership contract.

```yaml
stage_span:
  stages:
    - P10
    - P11
primary_owner: aegis-modeling
```

Rules:

1. `stages` is non-empty, ordered, unique, and uses canonical P-stage identifiers.
2. Every stage in one `stage_span` must map to the same `primary_owner`.
3. Cross-Primary spans are invalid.
4. `stage_family` is derived from stage ownership and is not authored canonical truth.

This permits one bounded P10/P11 modeling occurrence while still forbidding a single occurrence such as `P14 -> P20` across distinct Primary owners.

## 6.3 Occurrence revisions

A StageOccurrence uses immutable revisions rather than in-place mutation.

Minimum lifecycle:

```text
record_revision 1: OPEN
record_revision N: TERMINAL
```

A future P13 contract may define additional strictly monotonic intermediate revisions, but no revision may rewrite prior facts.

Canonical shape:

```yaml
schema_version: "0.2"
kind: STAGE_OCCURRENCE
id_scheme: stage-occurrence-v0.2
id: so_<uuidv7>
record_revision: 1
recorded_at: <timestamp>
control_lane_id: lane_<uuidv7>
stage_span:
  stages: [P12]
primary_owner: aegis-modeling
state: OPEN | TERMINAL
trusted_basis: <TrustedBasis>
policy_binding: <PolicyBinding>
schedule_basis:
  predecessor_occurrence_ref: null | <CanonicalRef to prior StageOccurrence materialization>
  reason_code: USER_REQUEST | NEXT_LEGAL_STAGE | RESUME | REPAIR | REVERIFY | REREVIEW | EARLIER_LAYER_ROUTE
  derived_from_basis_digest: <TrustedBasis.basis_digest>
input_refs:
  - <CanonicalRef>
repair_context: null | <RepairContext>
execution_navigation: null | <ExecutionNavigationSnapshot>
terminal: null | <TerminalFacts>
extensions: {}
```

### OPEN rules

For `state: OPEN`:

- `terminal` MUST be `null`;
- stage span, owner, TrustedBasis, policy, schedule basis, inputs, and repair context are frozen for the occurrence;
- a later terminal revision may add terminal/navigation facts but may not rewrite the frozen start facts.

### TERMINAL rules

For `state: TERMINAL`, `terminal` is required:

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
  earliest_untrusted_layer: null | <canonical layer/stage identifier>
  navigation_result: null | <ExecutionNavigationSnapshot>
```

Rules:

1. `outcome_category` is a coarse P11 interaction category; `status` uses existing Aegis workflow status vocabulary.
2. `READY` / `COMPLETED` on a non-P34 occurrence never means official Gate `PASS`.
3. A P34 occurrence may reference an official immutable `GATE_DECISION`; the StageOccurrence does not duplicate or replace that decision's verdict semantics.
4. A blocked terminal state must preserve the earliest trusted owning layer when known.
5. `produced_refs` stores exact durable results, not prose claims.
6. A terminal occurrence MUST NOT author `next_stage`, `next_owner`, or `current_macro_phase`; those are projections derived by the Control Plane.

---

# 7. ScheduleBasis schema

`ScheduleBasis` is immutable audit metadata explaining why an occurrence was allowed to start.

```yaml
schedule_basis:
  predecessor_occurrence_ref: null | <CanonicalRef>
  reason_code: USER_REQUEST | NEXT_LEGAL_STAGE | RESUME | REPAIR | REVERIFY | REREVIEW | EARLIER_LAYER_ROUTE
  derived_from_basis_digest: <digest>
```

The authorization for automatic continuation is the exact pinned `PolicyBinding`, not the `reason_code` alone.

`ScheduleBasis` records orchestration reasoning without making orchestration metadata Authority.

---

# 8. RepairContext schema

A repair attempt is represented by a StageOccurrence plus embedded `RepairContext`; there is no separate `RepairAttempt` aggregate.

```yaml
repair_context:
  finding_ref: <CanonicalRef object_type=FINDING>
  root_occurrence_ref: <CanonicalRef to occurrence whose result ultimately led to repair>
  previous_attempt_occurrence_ref: null | <CanonicalRef to previous repair StageOccurrence>
  attempt_ordinal: <integer >= 1>
  repair_policy_digest: <PolicyBinding.policy_digest>
```

Rules:

1. `attempt_ordinal` starts at `1` for the first authorized repair in a lineage.
2. `previous_attempt_occurrence_ref` is null only for the first attempt.
3. Every later attempt points to exactly one immediately previous repair occurrence.
4. All attempts in one lineage must reference the same root finding identity unless a new finding creates a new lineage.
5. `attempt_ordinal` must not exceed `repair_policy.max_attempts`.
6. Remaining budget is derived; it is not authored.
7. A repair requiring new Authority or semantic scope creates/escalates earlier-layer work; it must not be smuggled into the same repair lineage as if it were ordinary implementation repair.

`RepairLineage` is the generated traversal of these immutable occurrence links.

---

# 9. ExecutionNavigationSnapshot schema

The Control Plane may durably preserve the minimum accepted execution-position snapshot needed for sessionless resume, but this remains navigation metadata.

```yaml
execution_navigation:
  execution_surface: CONTROL_REASONING | CODE_EXECUTION | CONTROL_REVIEW | CODE_REVERIFY
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

1. `task_anchor` preserves Current Execution Surface v0.2 semantics.
2. `execution_cursor` preserves the last Control-Plane-accepted execution position; it does not authorize new scope.
3. Historical expected-HEAD equality is not introduced as a Control Plane invariant.
4. `ExecutionNavigationSnapshot` is not Authority, Evidence, Gate, Integration, or Proof.
5. A P34 reviewer must still resolve reviewer-accessible result/evidence independently; a cursor snapshot never proves correctness.
6. The package contains the stable task anchor where required; moving execution cursor state does not revise the implementation package.
7. Physical persistence/reconciliation with the currently separate Execution Surface contract is a downstream P14/P21 concern; P12 defines only the semantic snapshot needed by the accepted product requirement.

---

# 10. VerificationBoundImplementationPackage schema

## 10.1 Identity

```text
id_scheme = verification-bound-package-v0.2
id        = pkg_<UUIDv7>
```

A package has a stable lineage ID and immutable package revisions.

Any material change to authorized scope, TrustedBasis, verification bindings, Gate policy, Control Autonomy, repair policy, or task anchor requires a new immutable `record_revision` and a new package digest.

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
  scope_id: <stable semantic scope identity>
  authorized_refs:
    - <CanonicalRef>
  excluded_refs:
    - <CanonicalRef>
verification_binding:
  verification_spec_ref: <CanonicalRef object_type=VERIFICATION_SPEC>
  obligation_set_ref: null | <CanonicalRef object_type=PROOF_OBLIGATION_SET>
  acceptance_oracle_refs:
    - <CanonicalRef object_type=CONTRACT>
  evidence_compilation_contract_ref: <CanonicalRef object_type=CONTRACT>
gate_policy_ref: <CanonicalRef object_type=CONTRACT>
control_autonomy: AUTONOMOUS | REVIEW_GUARDED | HUMAN_DECISION
repair_policy: <RepairPolicy>
task_anchor: null | { revision: <exact revision>, relation: ancestor }
package_digest: <sha256 digest>
extensions: {}
```

Rules:

1. `verification_spec_ref` is required before an implementation package may become autonomously executable.
2. The package references Proof Plane truth; it MUST NOT copy Claim statements, ProofContract pass semantics, or invent local proof obligations.
3. `obligation_set_ref` may be null only when the governing Verification contract explicitly allows obligation materialization later without changing proof semantics.
4. `acceptance_oracle_refs` must point to canonical oracle/pass contracts, not executor-authored summaries.
5. `gate_policy_ref` is independent of `control_autonomy`.
6. `task_anchor` is required when repository execution depends on a repository baseline, preserving Execution Surface v0.2.
7. `resume_cursor` is forbidden as a package field because it is moving navigation state, not stable package authorization.
8. A package revision cannot broaden its own scope during execution.
9. A changed VerificationSpec/ProofContract identity requires a new package revision; existing execution cannot silently retarget the new proof truth.
10. `package_digest` is derived from the complete canonical package payload excluding `package_digest` itself.

---

# 11. Escalation schema

## 11.1 Identity

```text
id_scheme = escalation-v0.2
id        = esc_<UUIDv7>
```

An escalation is an immutable raised trust-interruption occurrence. It is not updated into a resolved object.

Canonical shape:

```yaml
schema_version: "0.2"
kind: ESCALATION
id_scheme: escalation-v0.2
id: esc_<uuidv7>
record_revision: 1
recorded_at: <timestamp>
control_lane_id: lane_<uuidv7>
raised_from_occurrence_ref: <CanonicalRef>
trusted_basis_digest: <digest>
category: AUTHORITY_CONFLICT | MISSING_CONTRACT | PRODUCT_DECISION |
          SEMANTIC_SCOPE_EXPANSION | RISK_OR_ASSURANCE_CHANGE |
          IRREVERSIBLE_ACTION | ORACLE_CREDIBILITY |
          REPAIR_BUDGET_EXHAUSTED | ENVIRONMENT_INTERVENTION |
          UNRESOLVED_MATERIAL_CLASSIFICATION
owning_layer: <canonical stage/layer identity>
required_decision:
  decision_kind: <governed decision class>
  summary: <compact human-readable question>
evidence_snapshot_refs:
  - <CanonicalRef object_type=EVIDENCE | RESULT | FINDING | GATE_DECISION>
extensions: {}
```

Rules:

1. Escalation records why autonomy stopped; it does not itself answer the decision.
2. Escalation resolution is represented by a later separately owned StageOccurrence or external governed decision that lists this escalation ID in `resolved_escalation_ids`.
3. `open/resolved` is a generated projection, not a mutable Escalation field.
4. A later resolution does not rewrite the original escalation category, evidence snapshot, or question.
5. Multiple materially different decisions require separate Escalation IDs rather than mutating one record into a different question.

---

# 12. Generated Control State schema

Generated state is a projection from canonical records plus referenced external truth. It may be cached, but it is never the source of truth.

Recommended projection shape:

```yaml
projection_version: "0.2"
control_lane_id: lane_<uuidv7>
generated_from:
  canonical_record_digests:
    - <sha256 digest>
  external_ref_identities:
    - <CanonicalRef identity>
control_cursor:
  trusted_basis_digest: <current applicable digest>
  active_occurrence_ref: null | <CanonicalRef>
  last_terminal_occurrence_ref: null | <CanonicalRef>
  current_package_ref: null | <CanonicalRef object_type=IMPLEMENTATION_PACKAGE>
  current_stage_span: null | [Pxx, ...]
  current_owner: null | <primary owner>
  execution_cursor: null | <ExecutionNavigationSnapshot.execution_cursor>
current_macro_phase: DEFINE | BUILD | PROVE | SHIP
next_legal_action:
  stage_span: null | [Pxx, ...]
  primary_owner: null | <owner>
  control_action: CONTINUE | WAIT_FOR_REVIEW | REPAIR | REVERIFY | REREVIEW | ESCALATE | COMPLETE | NONE
  reason_code: <derived reason>
open_escalation_ids:
  - esc_<uuidv7>
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

Rules:

1. Every projection field is derived; direct authored edits are invalid.
2. If a cached projection conflicts with canonical records or referenced external truth, canonical/external truth wins and the projection is regenerated.
3. If regeneration cannot establish a unique current state, the system fails closed rather than selecting a convenient cursor.
4. `current_macro_phase` is derived from the earliest active/incomplete required responsibility; it never overrides P-stage truth.
5. `next_legal_action` is derived from lifecycle + TrustedBasis + policies + blockers; a Primary owner's terminal output does not author its successor.
6. `open_escalation_ids` contains escalations with no valid later resolution binding.
7. `repair_lineages` are derived from `RepairContext` links and PolicyBinding; there is no repair-lineage aggregate.
8. The projection may expose an execution cursor for resume but cannot use it as evidence of correctness.

---

# 13. Project State v0.5 compatibility boundary

P12 deliberately does not redefine Current Project State semantics.

The Control Plane MUST reuse by exact reference:

- Authority identities/status from the Authority registry;
- Gate Contract / immutable Gate Decision identity from Project State v0.5;
- Integration occurrence/conformance identity from Project State v0.5;
- existing blocker/Gate semantics where they remain authoritative.

Rules:

1. A StageOccurrence referencing a Gate Decision stores a `CanonicalRef`; it does not copy a second mutable Gate verdict.
2. A Control projection may display current Gate state, but Project State remains the source for Gate Decision lineage until separately governed change occurs.
3. An Integration remains a Project State lifecycle record; Control Plane history does not create a parallel Integration aggregate.
4. This P12 candidate does not modify `.aegis/authorities.json`, `.aegis/gates.json`, or root Project State manifests.
5. Whether future Persistent Control State physically extends Project State manifests or remains a separate durable store is a P14 architecture decision and requires downstream governance before changing Current Authority.

---

# 14. Proof Plane compatibility boundary

The retained Verification Productization model remains the source of truth for:

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

1. Implementation packages pin exact Verification/Proof refs.
2. StageOccurrence may reference ProofEvaluation/Evidence outputs but does not reinterpret them.
3. Evidence Compiler output remains Evidence/Proof truth, not Control Plane truth.
4. Control Autonomy can decide whether another occurrence may be scheduled; it cannot turn insufficient proof into sufficient proof.
5. P34 remains the sole official Gate owner.

---

# 15. Execution Surface v0.2 compatibility boundary

Current Execution Surface semantics remain controlling until separately reconciled.

P12 preserves:

```text
Task Anchor != Execution Cursor
Stage Ownership != Execution Surface
resume cursor != Authority/Evidence/Gate
reviewer-accessible materialization required before P34
```

Control Plane extension intent:

- package revision pins the stable task anchor when required;
- accepted moving execution position may be preserved as internal `ExecutionNavigationSnapshot` for sessionless resume;
- the snapshot does not become scope authorization or proof;
- exact execution reconciliation behavior remains owned by the Execution Surface / implementation lifecycle contract.

This is an impacted downstream boundary, not silent supersession.

---

# 16. Validation invariants

A conforming v0.2 Control Plane semantic state must satisfy all of the following.

## 16.1 Identity / immutability

1. Record IDs conform to their declared `id_scheme`.
2. Record revisions are append-only and monotonically contiguous per object lineage.
3. A historical record revision never changes content.
4. UUID occurrence/package/escalation identities are never reused for semantically distinct objects.
5. Canonical digests reproduce under RFC 8785 + SHA-256.

## 16.2 Ownership

6. Every substantive StageOccurrence has exactly one Primary owner.
7. Every stage in one occurrence maps to that same owner.
8. No occurrence crosses a Primary ownership boundary.
9. Orchestrator/scheduler metadata never becomes the Primary substantive owner.

## 16.3 Trust / policy

10. TrustedBasis refs are exact and resolvable at required trust boundaries.
11. Control Autonomy cannot override Proof Assurance or Gate policy.
12. A package without required verification/acceptance bindings is not autonomously executable.
13. A stale/diverged required exact ref fails closed.

## 16.4 Repair

14. Repair attempt lineage is linear within one root finding lineage.
15. Attempt ordinals are contiguous and do not exceed bounded policy.
16. Reverification/re-review required by policy cannot be skipped by a repair occurrence.
17. Authority/semantic scope repair cannot masquerade as an authorized implementation-only repair.

## 16.5 Escalation

18. Escalation is immutable after raise.
19. Resolution is represented by later durable truth; original escalation is not edited away.
20. Open/resolved state is derived.

## 16.6 Projection

21. ControlCursor, macro phase, repair lineage, open escalations, and next legal action are generated only.
22. Cached projection disagreement never overrides canonical records.
23. Non-unique or contradictory derivation fails closed.

## 16.7 External boundaries

24. Gate Decision semantics are not duplicated from Project State.
25. Verification/Proof semantics are not duplicated into implementation packages.
26. Execution cursor metadata never counts as correctness evidence.
27. Existing Current composition/execution contracts are not silently superseded by this Draft P12 candidate.

---

# 17. Versioning and compatibility

## 17.1 Compatible within v0.2

The following may be added without changing canonical semantic meaning:

- namespaced entries under `extensions`;
- new generated projection fields whose values are fully derivable from existing canonical truth;
- new human-readable display labels that do not participate in identity, routing, validation, or trust.

## 17.2 Requires a new schema version

A new semantic schema version is required for:

- changing any record identity scheme;
- changing the meaning of existing required fields;
- making an optional trust field required or vice versa;
- changing stage ownership validation semantics;
- changing TrustedBasis exactness rules;
- changing Control Autonomy/Gate/Proof separation;
- introducing a new first-class durable aggregate;
- changing immutable revision/lineage semantics;
- changing repair-bound semantics;
- changing what counts as canonical vs generated state.

## 17.3 Reader behavior

A v0.2 reader:

1. MUST reject unsupported semantic schema versions at a trust boundary;
2. MUST fail closed on unknown canonical `kind` values;
3. MUST preserve or safely ignore namespaced `extensions` without interpreting them as Authority;
4. MUST NOT reinterpret older records under newer semantics without explicit migration;
5. MUST NOT use projection version compatibility as evidence that canonical schema versions are compatible.

---

# 18. User-facing projection constraint

The canonical schema is intentionally richer than the normal product UX.

Normal users should not need to see or enter:

```text
UUID occurrence IDs
basis digests
package digests
P-stage refs
Gate Decision IDs
Git SHAs
handoff/surface fields
repair ordinals
execution cursor internals
policy digests
```

Default UX remains:

```text
DEFINE / BUILD / PROVE / SHIP
current status
trusted result
what changed
open exception / human decision
```

Progressive disclosure may expose the canonical/audit detail without changing its semantic role.

---

# 19. P12 disposition

P12 Semantic Schema is complete as a Draft/Proposed downstream model over the accepted P02/P03 Product Authority and P10/P11 model.

It freezes:

- first-class durable object families;
- exact reference semantics;
- record identity and immutable revisioning;
- StageOccurrence ownership/stage-span shape;
- TrustedBasis and policy binding semantics;
- Verification-bound package schema;
- Escalation schema;
- repair-attempt representation through StageOccurrence + RepairContext;
- execution-navigation snapshot boundary;
- generated ControlCursor/macro/repair/escalation projections;
- Project State / Proof Plane / Execution Surface non-duplication boundaries;
- compatibility and versioning rules.

Next earliest untrusted layer after acceptance of this P12 candidate:

```text
P13 Operation / Mutation Model — Aegis Control Plane
```

P13 must define explicit append/materialize/terminate/schedule/repair/escalation-resolution operations, atomicity, ordering, idempotency/deduplication, replay, and fail-closed error behavior. P13 must not silently redesign the P12 object model.
