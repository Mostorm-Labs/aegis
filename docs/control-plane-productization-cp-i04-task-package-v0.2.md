# Aegis Control Plane Productization v0.2 — CP-I04 P31 Task Package

Status: **P31 READY / MATERIALIZED — authorized package for later P32 execution**

Package ID: `CP-I04-P31-01`

Owner: `aegis-implementation`

Stage: `P31 Task Packaging`

Target execution stage: `P32 Implementation`

Execution surface: `CONTROL_REASONING`

Preferred later execution surface: `CODE_EXECUTION`

This package defines only:

`CP-I04 — Historical Trust, REQUIRED-child Barrier, Snapshot / Provider Trust`

It does not start implementation, issue Evidence, or produce a Gate verdict.

---

## 1. Repository execution anchor

Repository:

`Mostorm-Labs/aegis`

Accepted predecessor:

```yaml
task_anchor:
  revision: f6820374d29772dfe1069f3502b6e4f80795fd80
  relation: ancestor
resume_cursor: null
```

`Task Anchor != Execution Cursor`.

The anchor is the exact CP-I03 revision accepted by P34. It is an ancestry trust baseline, not a requirement that a later execution HEAD remain equal to this historical revision.

---

## 2. Accepted predecessor boundary

CP-I03:

```yaml
revision: f6820374d29772dfe1069f3502b6e4f80795fd80
status: PASS / ACCEPTED_FOR_DOWNSTREAM
p34_comment: 5480775507
evidence_artifact_id: 9764168734
```

CP-I04 consumes and must preserve the accepted CP-I01 / CP-I02 / CP-I03 implementation semantics, including:

- independent reference/oracle boundary;
- single canonical writer through `control-mutation`;
- immutable revisions;
- lane CAS and semantic idempotency;
- transactional outbox;
- deterministic/read-only/disposable projection;
- transient scheduler candidate semantics;
- fresh commit-bound policy revalidation;
- Current cross-Primary automatic progression remaining denied.

CP-I04 may extend canonical/store/mutation/projection support where required by already accepted WorkScope / child-work / trust Authority. It must not reinterpret accepted predecessor semantics.

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

Normative modeling package includes:

```text
docs/control-plane-productization-model-v0.2.md
docs/control-plane-productization-schema-v0.2.md
docs/control-plane-productization-operations-v0.2.md
docs/control-plane-productization-model-v0.2-p21-repair.md
docs/control-plane-productization-model-v0.2-p21-b3-repair.md
```

Architecture:

```text
e657f0e74771184b98f8c8e6f8a8581e4858c82d
review: 5062769390
PASS / ACCEPTED_FOR_DOWNSTREAM
```

Relevant architecture contracts:

```text
docs/control-plane-productization-modules-v0.2.md
docs/control-plane-productization-platform-contract-v0.2.md
```

Verification:

```text
db83168e4086e47a7f431acf289006e4f25b8ffd
review: 5062933855
PASS / ACCEPTED_FOR_DOWNSTREAM
```

Normative verification package:

```text
docs/control-plane-productization-verification-v0.2.md
docs/control-plane-productization-verification-v0.2-p21-repair.md
```

Implementation plan:

```text
87cbb166411795261ec5f6e7034a89435e053451
```

---

## 4. Objective

Implement the bounded trust slice that lets the Control Plane consume exact externally owned trust facts without importing their ownership, while making parent/child continuation and historical replay independently auditable.

Required semantic shape:

```text
current canonical history
+ exact external refs
+ verified SourceSnapshotToken(s)
        |
        v
control-trust-resolver
        |
        +--> current child completion / acceptance support
        +--> current Authority / Gate / Proof / decision support
        +--> explicit stale / ambiguous / conflicting state
        |
        v
projection / policy / scheduling intent
        |
        v
fresh trust + snapshot revalidation at mutation boundary
        |
        v
control-mutation
        |
        +--> preserve WorkScope / lane identity
        +--> atomically create child scope/lane/OPEN occurrence when applicable
        +--> atomically bind ALL uncrossed REQUIRED-child acceptance facts
        +--> canonical commit through CP-I02 CAS / idempotency only
```

Historical replay uses the immutable acceptance bindings stored with the historical successor. It does not ask today's child projection to reconstruct yesterday's authorization.

---

## 5. Authorized implementation scope

### 5.1 WorkScope / ChildWork implementation completion

Implement the already accepted WorkScope semantics needed by CP-I04:

- `WorkScopeRef` validation and stable identity handling;
- one primary Control Lane per WorkScope;
- immutable `ChildWorkBinding` for non-root work scopes;
- parent and child use distinct WorkScope IDs and distinct lane IDs;
- parent/child cycle rejection;
- child Primary owner derives from child stage ownership and is not inherited from the parent;
- package/occurrence/escalation WorkScope correlation where required by accepted P12 repair semantics;
- same-lane continuation preserves WorkScope identity.

The first `SCHEDULE_STAGE_OCCURRENCE` for a new child scope may atomically establish:

```text
new WorkScopeRef
+ immutable ChildWorkBinding
+ new control_lane_id binding
+ StageOccurrence revision 1 / OPEN
+ permitted outbox entry, if and only if current policy permits it
```

No new `CREATE_WORK_ITEM`, `MARK_CHILD_COMPLETE`, or `ACCEPT_CHILD_WORK` mutation may be invented.

### 5.2 `control-external-ports`

Add typed, implementation-neutral read contracts for deterministic fake adapters representing externally owned truth classes required by this slice:

- Project State;
- Proof Plane;
- Execution Surface;
- Human Decision;
- generic governed source only where a test fixture requires it.

Trust-sensitive reads return exact refs plus an opaque `SourceSnapshotToken` and typed currentness/ambiguity information.

Adapters may translate transport representation. They may not translate semantic ownership.

No real vendor credentials or production provider rollout are part of this package.

### 5.3 `SourceSnapshotToken` issue / verify boundary

Implement the P17 physical token contract for deterministic local/fake adapters:

```text
sst1.<base64url(payload)>.<integrity-tag>
```

Logical payload binds at least:

```yaml
v: 1
source_kind: <governed source kind>
adapter_id: <stable adapter id>
resource_key: <provider-scoped resource identity>
version_scheme: <provider version scheme>
version_value: <exact provider version or normalized digest>
observed_at: <operational timestamp>
expires_at: null | <freshness deadline>
```

Verification must check, as applicable:

- token integrity;
- issuing adapter / source-kind compatibility;
- provider resource binding;
- provider version/currentness binding;
- configured freshness deadline.

The core domain treats the token as opaque. The issuing adapter owns verification.

A token is a validation guard, not Authority, Evidence, Gate, Integration, or a replacement for exact `CanonicalRef` values.

### 5.4 `control-trust-resolver`

Implement a read-only resolver over the external ports with typed support equivalent to:

```text
resolve_for_projection(work_scope_ref)
resolve_for_mutation(operation_request)
resolve_child_acceptance(child_work_scope_ref)
resolve_current_authority(trusted_basis)
resolve_gate_support(refs)
resolve_proof_support(refs)
verify_freshness(snapshot_bundle)
```

The resolver must expose:

- exact resolved refs;
- source-specific snapshot tokens;
- typed validity/currentness facts from the owning adapter;
- unresolved / missing / ambiguous / conflicting conditions explicitly;
- no new durable Control Plane verdict.

Resolver caches, if any, are disposable operational caches. A cached support bundle cannot authorize mutation without fresh validation.

### 5.5 Child completion / acceptance projection

Extend generated projection with the accepted distinction:

```text
child completed
!=
child accepted_for_parent
```

`completed` derives from the child canonical trajectory.

`accepted_for_parent` derives only when:

- the child is completed;
- every acceptance contract is satisfied by exact durable facts;
- any required Gate / Proof / Result / Integration / External Decision fact resolves exactly;
- current refs required for a new parent continuation are not stale/diverged;
- support is neither ambiguous nor conflicting.

Projection may expose exact accepted fact refs, but it cannot create a durable `ChildAccepted` record.

### 5.6 REQUIRED-child barrier and immutable acceptance binding

Implement the exact v0.2 REQUIRED barrier:

> Once a REQUIRED child is durably spawned from a parent occurrence, no new substantive parent-lane StageOccurrence may be scheduled after that spawning occurrence until every uncrossed REQUIRED child is accepted for the parent.

For each barrier crossed, construct an immutable `RequiredChildAcceptanceBinding` equivalent to:

```yaml
required_child_acceptance_binding:
  child_work_scope_ref: <WorkScopeRef>
  barrier_after_occurrence_ref: <exact parent spawning occurrence ref>
  child_completion_occurrence_ref: <exact terminal child occurrence ref>
  acceptance_contract_refs:
    - <exact CONTRACT refs>
  acceptance_fact_refs:
    - <exact RESULT / EVIDENCE / PROOF_EVALUATION / GATE_DECISION /
       INTEGRATION / EXTERNAL_DECISION refs as required>
  acceptance_basis_digest: <derived sha256 digest>
```

The binding must also reuse the exact supporting refs through normal successor `trusted_basis.accepted_fact_refs` and/or `input_refs` according to the accepted schema contract.

All uncrossed REQUIRED children must bind before the parent continues. NON_BLOCKING children do not create this barrier.

Required failure modes include, or must be semantically equivalent to:

```text
REQUIRED_CHILD_WORK_NOT_ACCEPTED
CHILD_ACCEPTANCE_BASIS_AMBIGUOUS
CHILD_ACCEPTANCE_BASIS_CONFLICT
WORK_SCOPE_LANE_CONFLICT
WORK_SCOPE_MISMATCH
PACKAGE_WORK_SCOPE_MISMATCH
```

All failures are fail-closed and leave zero canonical/outbox residue for the rejected transition.

### 5.7 Atomic mutation boundary

`control-mutation` remains the only canonical writer.

Two CP-I04 multi-record boundaries must be atomic:

1. child spawn:

```text
child WorkScope / ChildWorkBinding
+ child lane binding
+ first child OPEN occurrence
+ permitted outbox
```

2. parent barrier crossing:

```text
fresh child acceptance validation
+ RequiredChildAcceptanceBinding(s)
+ successor TrustedBasis/input ref checks
+ parent successor OPEN occurrence
+ permitted outbox
```

Either the complete semantic set commits through the existing CP-I02 transaction/CAS/idempotency boundary, or none of it commits.

There is no mutable `barrier_consumed` flag.

### 5.8 Historical replay

Implement deterministic historical replay from the immutable successor transition basis:

```text
child WorkScope
+ barrier/spawn occurrence
+ child completion occurrence
+ acceptance contracts
+ exact acceptance facts
+ acceptance_basis_digest
```

Historical authorization must not be recomputed from today's child `accepted_for_parent` projection.

Later Gate Decisions, ProofEvaluations, Authority changes, Evidence replacements, or current projection changes may alter current actionability but never rewrite which exact facts authorized a historical successor.

### 5.9 Async provider capability declaration

Implement a non-semantic capability check for trust-sensitive async providers.

A provider may be classified as fully autonomous-capable for trust-sensitive use only if callback loss is recoverable through a durable query/correlation path.

```text
callback-only provider
-> not full autonomous trust-sensitive capability
```

Capability state is environment/operational evidence. It does not authorize Current cross-Primary rollout.

---

## 6. Allowed repository surfaces

P32 may add or modify only surfaces necessary to realize the bounded CP-I04 contract, expected to include:

```text
tools/aegis_control/canonical.py
tools/aegis_control/store.py
tools/aegis_control/mutation.py
tools/aegis_control/projection.py
tools/aegis_control/__init__.py

tools/aegis_control/external_ports.py          # new if used
tools/aegis_control/trust.py                   # new if used
tools/aegis_control/snapshot.py                # new if used
```

Equivalent narrowly scoped names are allowed if the module ownership remains P15-conformant.

Verification/test surfaces may include:

```text
tests/control_plane/reference_model.py
tests/control_plane/verifier_helpers.py
tests/control_plane/cp_i02_fixtures.py
tests/control_plane/test_cp_i04_*.py
tests/control_plane/cp_i04_evidence.py
tests/control_plane/generate_cp_i04_evidence.py
.github/workflows/control-plane-cp-i04.yml
```

Existing CP-I01/02/03 fixtures may be upgraded to carry the already accepted WorkScope fields required by final P12/P13 Authority, but such fixture changes must not weaken their prior assertions or rewrite prior semantic expectations.

Production `policy.py` / `scheduler.py` changes are allowed only if strictly necessary to pass already accepted WorkScope/trust inputs through the existing CP-I03 boundary without changing autonomy meaning. Any semantic redesign of CP-I03 policy/scheduler behavior is outside this package and must block.

---

## 7. Explicit non-goals

P32 MUST NOT implement or claim:

- real vendor credential rollout;
- real production dispatch worker;
- CP-I05 dispatch/reconciliation/sessionless-resume behavior;
- callback-only provider as fully autonomous;
- a new ChildAccepted, Finding, Gate, WorkItem, mutable barrier, or Proof aggregate;
- direct external-truth writes from Control Plane;
- Current cross-Primary automatic dispatch/progression;
- policy-generated Gate or Authority truth;
- provider success as semantic completion;
- P34 Gate PASS from an evidence compiler;
- CP-I06 repair/recovery loop;
- CP-I07 real platform adapter boundary;
- integrated D0 closure;
- R0/S0/7-day/monthly performance or availability claims.

This package may use deterministic fake adapters and platform-contract simulators only for the trust boundary required by CP-I04.

---

## 8. Frozen invariants

1. External Authority / Gate / Proof / Integration / Execution / Human Decision truth remains externally owned.
2. Exact external refs never become mutable local copies of the external verdict.
3. `SourceSnapshotToken` is an opaque validation guard, not semantic truth.
4. Webhook/callback payloads are hints; query/refetch/currentness verification is the trust path.
5. Stale, expired, wrong-adapter, wrong-source, wrong-resource, wrong-version, ambiguous, or conflicting trust support fails closed.
6. Trust-sensitive mutable currentness is revalidated before commit.
7. One WorkScope has one primary Control Lane in v0.2.
8. One child WorkScope has at most one immutable direct parent binding.
9. Parent and child use distinct WorkScope IDs and lane IDs.
10. Child Primary ownership is derived from its stage and is never inherited from the parent.
11. Child `completed` and `accepted_for_parent` are distinct generated facts.
12. No operation directly authors child completion or acceptance state.
13. REQUIRED blocks the next substantive parent continuation after the spawning occurrence until all uncrossed REQUIRED children are accepted.
14. Barrier crossing requires exact immutable `RequiredChildAcceptanceBinding` facts.
15. Multiple REQUIRED children must all bind before parent continuation.
16. NON_BLOCKING children do not appear in REQUIRED barrier bindings merely because they exist.
17. There is no mutable barrier-consumed state.
18. Historical replay uses pinned transition facts, not today's child projection.
19. Current truth changes may change current actionability but never rewrite historical authorization.
20. Child spawn and parent barrier crossing are atomic semantic mutation boundaries.
21. `control-mutation` remains the only canonical writer.
22. Lane CAS / semantic idempotency / immutable revision rules remain CP-I02-canonical.
23. Projection/trust resolver/cache remain read-only/transient.
24. Current cross-Primary rollout remains denied exactly as governed.
25. Provider capability does not imply rollout authorization.
26. P34 remains the sole official Gate owner.

---

## 9. Required tests / oracle obligations

P32 must materialize deterministic tests against the independent oracle stack. Production control-flow success is not sufficient as its own oracle.

### 9.1 WorkScope / child atomicity

Cover:

- root WorkScope + lane identity preservation;
- first child scheduling atomically creates child scope/binding/lane/OPEN occurrence;
- child spawn crash/failure at every precommit point leaves zero partial child scope/lane/occurrence/outbox residue;
- same request ID replay returns the same child identities;
- different fingerprint with same request ID conflicts;
- parent/child cycle rejection;
- same lane with different WorkScope rejection;
- package/occurrence WorkScope mismatch rejection.

Oracle:

`O-CRM + O-STORE + O-AUTH`.

### 9.2 REQUIRED-child barrier matrix

Cover:

- REQUIRED child incomplete -> parent successor rejected;
- child completed but acceptance contract not satisfied -> rejected;
- acceptance facts missing -> rejected;
- acceptance facts ambiguous -> rejected;
- acceptance facts conflicting with projected acceptance -> rejected;
- one of multiple REQUIRED children unaccepted -> rejected;
- all REQUIRED children accepted -> exactly one parent successor can commit;
- NON_BLOCKING child does not block unrelated parent continuation;
- accepted successor contains one canonical binding per crossed REQUIRED child;
- all required acceptance refs are reused through successor TrustedBasis/input refs;
- no mutable barrier-consumed state exists.

Rejected cases must prove unchanged canonical/outbox state.

### 9.3 Historical replay

Cover:

```text
D1 authorizes child acceptance
-> parent successor S commits with D1 pinned
-> current truth later changes to D2 / child becomes non-current
-> historical replay(S)
```

Required result:

- replay resolves D1 and the original acceptance tuple;
- no historical mismatch;
- no current projection inference substitutes D2;
- a newly scheduled future occurrence must satisfy current truth independently.

Oracle:

`O-CRM + O-AUTH + exact ref/digest checker`.

### 9.4 Snapshot/currentness matrix

Use independent `O-SNAPSHOT` plus production fake adapter implementation.

Mandatory cases include P20 G36-G38 and M16-M18 equivalents:

- mutate token payload without new integrity tag -> reject;
- mutate integrity tag -> reject;
- wrong adapter/source-kind token -> reject;
- wrong provider resource token -> reject;
- wrong provider version token -> reject or force re-resolution;
- provider version changes between read/projection and commit -> stale success rejected;
- expired/stale token when current truth required -> re-resolve or reject;
- valid correctly bound token -> accepted as support only, subject to normal policy/mutation checks.

Every negative commit-bound case must prove zero canonical/outbox success residue.

### 9.5 Trust ambiguity / exact-ref matrix

Cover:

- missing exact acceptance fact ref;
- mutable/unpinned ref at a trust boundary;
- duplicate acceptance fact refs;
- exact Gate / Proof / Result facts supplied under the wrong acceptance contract;
- same facts yielding contradictory resolver support;
- resolver cache stale while provider version changes.

All ambiguous/conflicting trust must fail closed.

### 9.6 Async provider capability

Mandatory P20 G39 / M19 equivalent:

```text
callback available = true
query/correlation = false
```

must not be classified as fully autonomous trust-sensitive capability.

A deterministic provider with callback + durable query/correlation may satisfy the capability contract, but this still does not authorize Current cross-Primary rollout.

Oracle:

`O-CONTRACT + O-PROVIDER + O-AUTH`.

### 9.7 Accepted predecessor regression

At final exact P32 head rerun at least:

- focused CP-I04 suite;
- full Control Plane suite;
- Project State suite;
- Skillset suite;
- CP-I01 foundation / verifier qualification regression;
- accepted CP-I02 mutation/atomicity/idempotency/CAS regressions;
- accepted CP-I03 projection/policy/scheduler/currentness regressions.

If upgrading prior fixtures for WorkScope fields changes an earlier accepted behavior rather than only completing the accepted canonical shape, stop and return a blocker.

---

## 10. Evidence obligations

Primary required CP-I04 EvidenceArtifacts:

```text
CPV-E-TRUST-CURRENTNESS
CPV-E-HISTORICAL-REPLAY
CPV-E-SNAPSHOT-INTEGRITY
CPV-E-ASYNC-PROVIDER-CAPABILITY
```

Because CP-I04 implements the child multi-record atomicity portion of `CPV-C01`, also materialize an exact CP-I04 extension to:

```text
CPV-E-CANONICAL-CONFORMANCE
```

covering child spawn and REQUIRED-barrier crossing atomicity / zero residue while retaining accepted single-writer and lane-CAS evidence.

The evidence bundle must bind:

- exact `CP-I04-P31-01` package ref;
- exact P32 result revision;
- accepted CP-I03 predecessor revision `f6820374d29772dfe1069f3502b6e4f80795fd80`;
- CP-I03 P34 PASS comment `5480775507`;
- exact Product / Modeling / Architecture / Verification refs;
- exact test commands and test identities;
- O-CRM / O-STORE / O-PROVIDER / O-SNAPSHOT / O-AUTH / O-CONTRACT oracle identities as applicable;
- G36-G39 fixture identities and M16-M19 qualification identities;
- runtime/tool versions;
- deterministic fake-adapter identities/configuration;
- exact evidence file digests;
- reviewer-accessible artifact/materialized ref.

The evidence compiler may report evidence facts only. It must not emit P34 PASS.

---

## 11. Exit criteria

Zero tolerance:

```text
stale_success_commits = 0
historical_replay_mismatch = 0
unbound_required_successor = 0
required_child_barrier_bypass = 0
child_spawn_half_commit = 0
barrier_cross_half_commit = 0
tampered_snapshot_accepted = 0
cross_adapter_or_source_snapshot_accepted = 0
cross_resource_or_version_snapshot_accepted = 0
ambiguous_trust_success = 0
callback_only_provider_fully_autonomous = 0
second_canonical_writer = 0
```

Required final conditions:

```text
all REQUIRED children accepted before barrier crossing
historical successor replay uses pinned immutable acceptance basis
trust-sensitive currentness revalidated before commit
provider full-autonomy capability requires durable query/correlation
Current cross-Primary rollout remains DENIED exactly as governed
```

For mutable trust-sensitive snapshots, the P20/P18 `<=10s before commit` bound or an equivalent stronger provider conditional-version check applies to any claimed current-success path. Deterministic tests should use an injected clock/version oracle rather than wall-clock sleeping.

---

## 12. Blocked return behavior

Return the smallest applicable blocker and stop if implementation discovers any of the following:

### Authority / semantic blocker

If correct implementation would require:

- changing REQUIRED barrier meaning;
- weakening exact acceptance-fact binding;
- allowing historical replay from current projection;
- introducing mutable child acceptance/barrier state;
- importing external Gate/Proof/Authority ownership into Control Plane;
- weakening SourceSnapshot/currentness requirements;
- reinterpreting Current cross-Primary rollout;

return `BLOCKED_AUTHORITY` / the applicable upstream owning-layer blocker. Do not repair Authority inside P32.

### Implementation blocker

If the accepted local persistence/runtime cannot atomically realize child spawn or barrier crossing while preserving CP-I02 semantics, return `BLOCKED_IMPLEMENTATION` with exact failing invariant/evidence.

### Evidence blocker

If the exact result cannot be materialized at a reviewer-accessible durable boundary, return `BLOCKED_EVIDENCE`; local commits, logs, or executor prose are insufficient.

### Provider capability gap

If a simulated/selected provider lacks durable query/correlation, expose the capability as degraded/not-full-autonomous. Do not invent capability or weaken trust rules to obtain a clean test.

---

## 13. Required P32 materialization boundary

Before returning from P32 to `CONTROL_REVIEW`, the executor must materialize the exact result and evidence at a reviewer-accessible durable ref.

The P32 return must include at minimum:

```yaml
package_id: CP-I04-P31-01
package_ref: <this P31 materialized commit>
task_anchor:
  revision: f6820374d29772dfe1069f3502b6e4f80795fd80
  relation: ancestor
starting_revision: <actual execution start revision>
result_revision: <exact final revision>
materialized_ref: <reviewer-accessible durable result/evidence ref>
evidence_artifact_id: <if artifact-backed>
return_surface: CONTROL_REVIEW
status: COMPLETE / MATERIALIZED / READY_FOR_P34
```

A P32 result does not self-accept downstream trust.

---

## 14. Surface handoff contract

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
  revision: f6820374d29772dfe1069f3502b6e4f80795fd80
  relation: ancestor
resume_cursor: null
return_surface: CONTROL_REVIEW
```

P31 completion stops here.

Next legal action:

`P32 CODE_EXECUTION — CP-I04 only`

Do not start CP-I05.
