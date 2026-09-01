# Aegis Control Plane Productization v0.2 — CP-I05 P31 Task Package

Status: **P31 READY / MATERIALIZED — authorized package for later P32 execution**

Package ID: `CP-I05-P31-01`

Owner: `aegis-implementation`

Stage: `P31 Task Packaging`

Target execution stage: `P32 Implementation`

Execution surface: `CONTROL_REASONING`

Preferred later execution surface: `CODE_EXECUTION`

This package defines only:

`CP-I05 — Dispatch, Reconciliation, Exact Result Materialization, Sessionless Resume`

It does not start implementation, issue Evidence, produce a Gate verdict, merge CP-I04, or start CP-I06+.

---

## 1. Repository execution anchor

Repository:

`Mostorm-Labs/aegis`

Accepted predecessor:

```yaml
task_anchor:
  revision: a3fd350c350bec9220a1c6e283de88c14dfbcd2a
  relation: ancestor
resume_cursor: null
```

`Task Anchor != Execution Cursor`.

The anchor is the exact CP-I04 revision accepted by P34. It is an ancestry trust baseline, not a requirement that a later P32 HEAD remain equal to this historical revision.

P32 must record its actual starting revision before edits. The start is legal only when the task anchor is an ancestor of the starting revision and the exact package ref materializing this P31 document is present in that ancestry.

---

## 2. Accepted predecessor boundary

CP-I04:

```yaml
revision: a3fd350c350bec9220a1c6e283de88c14dfbcd2a
status: PASS / ACCEPTED_FOR_DOWNSTREAM
p34_comment: 5486917398
p36_return_comment: 5483906756
evidence_artifact_id: 9773820653
```

CP-I05 consumes and must preserve all accepted CP-I01 through CP-I04 semantics, including:

- independent oracle / evidence boundary;
- single canonical writer through `control-mutation`;
- immutable revisions, lane CAS, semantic idempotency, and transactional outbox;
- deterministic/read-only projection and transient scheduler candidates;
- Current cross-Primary automatic progression remaining denied;
- externally owned trust facts remaining externally owned;
- exact `SourceSnapshotToken` / exact-ref currentness behavior;
- historical trust using pinned immutable facts;
- REQUIRED-child acceptance/binding semantics;
- exact reviewer-accessible materialization as a trust boundary rather than executor prose.

CP-I05 may extend the accepted runtime with dispatch/reconciliation/navigation support. It must not reinterpret predecessor semantic truth.

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

Architecture / engineering:

```text
e657f0e74771184b98f8c8e6f8a8581e4858c82d
review: 5062769390
PASS / ACCEPTED_FOR_DOWNSTREAM
```

Relevant contracts:

```text
docs/control-plane-productization-modules-v0.2.md
docs/control-plane-productization-runtime-flow-v0.2.md
docs/control-plane-productization-platform-contract-v0.2.md
docs/control-plane-productization-engineering-v0.2.md
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

Applicable proof claims / requirements for this slice include:

```text
CPV-C02
CPV-C05 — persistent/sessionless-resume portion
CPV-C16 — delivery/reconciliation worker/provider portion
CPV-R33
CPV-R34
```

`CPV-R35` full sustained rate-limit adaptation remains a later operational-control concern unless only the minimum safe retry-after handling is required to keep CP-I05 transport fail-closed. CP-I05 must not pre-implement the broader CP-I06 degraded-recovery/rate-limit controller.

---

## 4. Objective

Connect an already committed `OPEN` StageOccurrence/outbox entry to an execution surface, recover from at-least-once transport and callback loss, reconcile exact execution position/result, and persist only the accepted execution-navigation facts needed for sessionless resume.

Required semantic shape:

```text
control-mutation commits OPEN occurrence + outbox
                 |
                 v
       committed outbox becomes visible
                 |
                 v
          control-dispatch
                 |
        exact occurrence identity
        exact execution contract
        durable provider correlation
                 |
                 v
        execution-surface adapter
          /               \
     callback hint      exact query
          \               /
           v             v
            reconciliation
                 |
      +----------+-----------+
      |                      |
      v                      v
accepted navigation       exact durable result
checkpoint                materialized_ref
      |                      |
      v                      v
RECORD_EXECUTION_PROGRESS   terminal precondition
      \                      /
       +---------> control-mutation
```

No dispatch or reconciliation component becomes lifecycle truth. Canonical truth still changes only through accepted P13 operations submitted to `control-mutation`.

---

## 5. Authorized implementation scope

### 5.1 `control-dispatch` over committed outbox only

Implement a dispatch service that can consume only durable outbox rows already visible after the scheduling transaction commits.

Required behavior:

- read/claim committed ready outbox entries through an internal operational API;
- re-resolve the exact occurrence referenced by the outbox before provider work;
- preserve exact `occurrence_id`, occurrence revision/input bindings, WorkScope/lane identity, and execution contract correlation;
- send no provider request from a transient scheduler candidate or uncommitted transaction;
- use at-least-once transport semantics;
- treat repeated delivery of the same exact occurrence as transport retry, never a semantic retry;
- refuse dispatch when Current rollout/policy does not authorize that dispatch path;
- never create or mutate canonical records directly.

A dispatch acknowledgement means only that transport/provider acceptance was observed. It is not semantic completion.

### 5.2 Operational delivery metadata — non-canonical only

Extend the store/runtime with an operational delivery state separate from canonical record tables.

The operational state may represent, as needed:

```text
outbox readiness / claim hint
provider correlation id
delivery attempt count
last attempt timestamp
next attempt eligibility
callback/query observation metadata
DELIVERY_UNCERTAIN diagnostic state
lease/claim expiry hints
```

Rules:

- these are operational coordination facts, not P12 canonical records;
- workers may update them only through a narrowly scoped internal operational contract;
- operational metadata writes must have no path to append `canonical_records`, advance lane heads, append semantic idempotency, or issue Gate/Authority truth;
- deleting/rebuilding operational state must not rewrite canonical semantic history;
- leases remain coordination only; canonical concurrency truth remains lane CAS / immutable revision guards.

Already committed outbox work may not be dropped merely to improve backlog metrics.

### 5.3 Execution-surface adapter contract

Add a deterministic, implementation-neutral execution-surface adapter boundary for CP-I05 tests and bounded runtime behavior.

The adapter must support durable correlation sufficient to answer:

```text
dispatch(exact occurrence / execution envelope)
query(correlation / occurrence identity)
resolve current execution position
resolve exact durable result/materialized_ref
```

The adapter may additionally expose callback/event hints, but callback delivery alone is never enough for autonomous recovery.

For deterministic conformance, provide a fake execution provider capable of modeling:

- accepted dispatch;
- duplicate dispatch;
- request accepted but local acknowledgement lost;
- callback loss;
- provider job still running;
- exact result materialized;
- result missing;
- result identity mismatch;
- local-only/unreviewable result;
- exact repository execution cursor / descendant / divergence observations;
- process crash/restart while the provider job continues.

No real vendor credentials or production provider rollout are authorized in CP-I05.

### 5.4 `RECORD_EXECUTION_PROGRESS`

Promote the already accepted P13 operation from the current "known later" set into the supported CP-I05 mutation subset.

It appends a new immutable `OPEN` revision of the same `StageOccurrence` with exactly one allowed semantic delta:

```text
execution_navigation only
```

All frozen start facts must remain byte-semantically unchanged:

```text
control_lane_id
work_scope_ref
stage_span
primary_owner
trusted_basis
policy_binding
schedule_basis
input_refs
repair_context
```

Required preconditions:

- target occurrence is `OPEN`;
- exact current record revision/digest matches `expected_state`;
- the navigation snapshot was first reconciled under the accepted Execution Surface / P33 position contract;
- task anchor remains the authorized package/task anchor;
- the checkpoint cannot widen scope, change owner, replace Authority/package identity, satisfy Proof/Gate semantics, or infer correctness from repository position.

Different competing checkpoints from the same prior revision must conflict/fail closed; arrival time is not a semantic ordering oracle.

### 5.5 Four-state sessionless resume classifier

Implement exactly the accepted P33 repository-position classification:

```text
EXACT_CURSOR
DESCENDANT_CURSOR
ANCHOR_DESCENDANT_WITHOUT_CURSOR
DIVERGED
```

Required behavior:

- `EXACT_CURSOR`: observed execution revision equals the accepted cursor revision; resume from the accepted `next_action`;
- `DESCENDANT_CURSOR`: accepted cursor revision is an ancestor of observed HEAD; inspect only the delta after the cursor, preserve verified valid work, and never replay `completed_through` work;
- `ANCHOR_DESCENDANT_WITHOUT_CURSOR`: no accepted cursor exists, but the task anchor is an ancestor of observed HEAD; reconcile completed versus pending work, establish an accepted cursor, and resume at the first incomplete verified step;
- `DIVERGED`: neither cursor nor anchor ancestry can establish a compatible continuation, history was incompatibly rewritten, or observed state contradicts Authority/scope; fail closed with `BLOCKED_EXECUTION_DIVERGENCE` or a more specific existing blocker.

The classifier is execution/navigation logic. Its raw result is not Gate evidence and cannot expand package Authority.

### 5.6 Exact result materialization and terminal precondition

Before an execution occurrence may terminate with a completion outcome that claims downstream/review readiness, the execution-surface path must independently resolve an exact reviewer-accessible durable result.

Accepted materialization must provide enough exact identity to establish:

```text
same execution occurrence / package/task
same expected result lineage
reviewer-accessible durable ref
immutable or contractually exact identity
not merely a local worktree / local-only commit / transcript / executor prose
```

The exact result ref is consumed through normal existing `produced_refs` / TrustedBasis/input-ref semantics where the accepted P12/P13 contract requires it. CP-I05 must not invent a new canonical Result aggregate.

If required result materialization is missing, ambiguous, mismatched, inaccessible to the reviewer, or only local, completion claiming review readiness must fail closed. The smallest valid terminal disposition is normally:

```text
BLOCKED_EVIDENCE
```

Remote acknowledgement alone is never sufficient.

### 5.7 Reconciliation after callback loss / dispatch uncertainty

Implement `control-recovery` reconciliation entrypoints for already scheduled/open work without implementing CP-I06 repair semantics.

Canonical reconciliation pattern:

```text
callback/event hint or periodic wakeup
  -> correlate exact occurrence/provider job
  -> query provider current state
  -> verify exact current execution position/result
  -> derive one of:
       no semantic change
       accepted progress checkpoint request
       exact terminal request
       delivery/reconciliation diagnostic
       fail-closed divergence/blocker
  -> submit any canonical change through control-mutation
```

Age alone may not terminalize an occurrence or allocate a replacement occurrence.

### 5.8 Delivery uncertainty policy

Implement the accepted P18 dispatch retry policy for the same committed occurrence:

```text
1 s
2 s
4 s
8 s
16 s
30 s
60 s
then <= 5 min cadence
```

Operational boundary:

```text
12 transport attempts OR 30 min unresolved delivery uncertainty
```

At the boundary:

```text
operational state -> DELIVERY_UNCERTAIN
trigger persistent diagnostics / reconciliation
semantic StageOccurrence count remains one
```

It MUST NOT allocate a replacement occurrence merely to erase uncertainty.

### 5.9 Reconciliation cadence

Under deterministic virtual clock, implement the accepted callback-loss/provider-query cadence for an `OPEN` occurrence requiring active reconciliation:

```text
0-5 min:      every 30 s
5-30 min:     every 2 min
30 min-2 h:   every 5 min
>2 h:         every 15 min + operator diagnostic/alert signal
```

Recent verified callback/provider progress may suppress redundant polling.

Provider signals may safely delay polling where the accepted contract permits, but CP-I05 must never use a slower cadence as justification for stale trust acceptance or semantic retry.

Full sustained rate-limit adaptation (`>5%` over `5 min`, gradual recovery, broader concurrency controller) is not part of this package unless an earlier accepted interface requires a minimal no-blind-retry safeguard.

---

## 6. Allowed repository surfaces

P32 may add or modify only surfaces necessary to realize the bounded CP-I05 contract.

Primary production surfaces:

```text
tools/aegis_control/dispatch.py                 # new
tools/aegis_control/recovery.py                 # new
tools/aegis_control/execution_surface.py        # new deterministic/provider contract preferred
tools/aegis_control/store.py                    # operational outbox/delivery metadata APIs only
tools/aegis_control/mutation.py                 # RECORD_EXECUTION_PROGRESS + exact terminal guard
tools/aegis_control/trust.py                    # exact result/currentness resolution only if needed
tools/aegis_control/__init__.py                 # exports only
```

Conditionally allowed:

```text
tools/aegis_control/canonical.py
```

only to expose/enforce already accepted P12 `execution_navigation` validation or exact-ref shape. It may not redefine schema semantics.

Existing production surfaces expected to remain semantically unchanged:

```text
tools/aegis_control/policy.py
tools/aegis_control/projection.py
tools/aegis_control/scheduler.py
tools/aegis_control/snapshot.py
tools/aegis_control/external_ports.py
```

A narrow compatibility change is allowed only if required to connect an already accepted interface without changing CP-I01..I04 semantics. If substantive changes to their meaning are required, P32 must stop and return a blocker rather than silently expanding scope.

Verification/test surfaces may include:

```text
tests/control_plane/test_cp_i05_*.py
tests/control_plane/cp_i05_fixtures.py
tests/control_plane/cp_i05_evidence.py
tests/control_plane/generate_cp_i05_evidence.py
tests/control_plane/reference_model.py            # independent oracle extension only
tests/control_plane/verifier_helpers.py           # independent verifier helpers only
.github/workflows/control-plane-cp-i05.yml
```

Existing CP-I01..I04 tests/evidence fixtures may be reused or minimally extended, but prior assertions and accepted expected semantics must not be weakened.

Equivalent narrowly scoped names are allowed only when ownership boundaries and this package's file-class restrictions remain mechanically reviewable.

---

## 7. Explicit non-goals

P32 MUST NOT implement or claim:

- CP-I06 semantic repair/reverification/rereview scheduling or escalation/recovery policy;
- full P18 sustained rate-limit adaptation controller;
- CP-I07 real production provider credential rollout / platform API productization;
- a new canonical delivery/job/cursor/result aggregate;
- executor/provider direct canonical writes;
- distributed exactly-once execution;
- a second canonical writer;
- duplicate semantic occurrence as a transport retry;
- timeout/age as semantic failure by itself;
- callback/webhook payload as semantic truth;
- remote acknowledgement as semantic completion;
- local-only result as reviewer-ready materialization;
- `Task Anchor == Execution Cursor` semantics;
- repository SHA/time ordering as correctness proof;
- Current cross-Primary zero-user-turn rollout beyond existing authorization;
- policy-generated Gate/Authority/Proof truth;
- CP-I08 integrated D0 closure;
- CP-I09 R0/S0/seven-day performance/cost evidence;
- monthly availability attainment;
- P34 PASS from tests/evidence compiler.

---

## 8. Frozen invariants

1. Canonical OPEN occurrence and its outbox commit before any substantive provider request.
2. `control-mutation` remains the only canonical writer.
3. Worker/dispatch/recovery components have no direct canonical append/lane-advance capability.
4. Transport is at-least-once; semantic occurrence identity remains exactly once per scheduled occurrence.
5. Duplicate delivery of one exact occurrence is transport retry, not semantic retry.
6. Provider acknowledgement is not semantic completion.
7. Callback/webhook is a hint; durable query/correlation is the recovery/trust path.
8. Exact reviewer-accessible result materialization is required before review-ready completion.
9. Local worktree, local-only commit, transcript, or executor prose cannot substitute for materialization.
10. `Task Anchor != Execution Cursor`.
11. Cursor/progress is navigation metadata, not scope/Authority/Proof/Gate authorization.
12. `RECORD_EXECUTION_PROGRESS` changes only `execution_navigation`; frozen start facts remain unchanged.
13. Valid repository descendants are reconciled, not rejected merely for differing from a historical HEAD.
14. Already verified completed work is not replayed on resume.
15. True divergence fails closed.
16. Delivery uncertainty never creates a replacement semantic occurrence.
17. Age/liveness is diagnostic; age alone never terminalizes.
18. Terminal occurrence revision remains unique.
19. Terminalization of A and scheduling successor B remain separate durable transitions.
20. Operational delivery metadata is non-canonical and cannot become lifecycle truth.
21. Leases/claims are operational hints; lane CAS remains semantic concurrency truth.
22. Current cross-Primary rollout remains denied exactly where existing policy/Authority denies it.
23. P34 remains the sole official Gate owner.

---

## 9. Required tests / independent oracle obligations

P32 must materialize deterministic tests against the accepted independent oracle stack. Production success alone is not sufficient expected truth.

Required oracle composition:

```text
O-CRM
O-STORE
O-PROVIDER
O-AUTH
O-TIMEPOLICY
+ independent execution-position/materialization checker
```

### 9.1 Commit-before-dispatch / outbox

Cover at minimum:

- uncommitted/transient schedule cannot be observed/claimed by dispatcher;
- committed OPEN + outbox becomes dispatchable only after transaction commit;
- crash at schedule precommit checkpoints yields zero provider dispatch;
- worker restart after outbox commit preserves one semantic occurrence;
- unrelated operational delivery metadata never changes canonical counts/history.

Zero tolerance:

```text
dispatch_before_commit = 0
worker_direct_canonical_writes = 0
```

### 9.2 Duplicate / crash / callback-loss fault matrix

Cover G04-G06 style cases plus repaired G40-G41:

- duplicate delivery of one committed occurrence;
- provider accepts dispatch then worker crashes before local acknowledgement;
- duplicate callback/event;
- callback never arrives;
- worker/process restart while provider execution continues;
- provider query returns running -> materialized -> exact result transition;
- uncertainty reaches 12 attempts/30 min without new occurrence.

Zero tolerance:

```text
semantic_occurrence_amplification = 0
duplicate_terminal_revision = 0
age_only_terminalization = 0
```

### 9.3 Exact result materialization matrix

Cover:

```text
exact reviewer-accessible result -> eligible for valid completion path
missing result -> fail closed / BLOCKED_EVIDENCE when completion requires it
mismatched result identity -> fail closed
ambiguous result -> fail closed
local-only result -> not review-ready
provider acknowledgement only -> not completion
```

Evidence must show exact result ref identity and the reviewer resolution outcome, not only a boolean test pass.

### 9.4 `RECORD_EXECUTION_PROGRESS`

Cover:

- accepted navigation checkpoint appends exactly one OPEN revision;
- only `execution_navigation` changes;
- every frozen start fact stays byte-semantically identical;
- stale revision/digest guard rejects with zero residue;
- conflicting checkpoints from one prior revision cannot both commit;
- cursor cannot change package/Authority/scope/owner or satisfy Gate/Proof truth;
- repeated exact idempotent request returns same result.

### 9.5 P33 four-state resume corpus

Materialize exact cases for:

```text
EXACT_CURSOR
DESCENDANT_CURSOR
ANCHOR_DESCENDANT_WITHOUT_CURSOR
DIVERGED
```

Required assertions:

- exact and legal descendant cases resume without replaying `completed_through` work;
- anchor-descendant/no-cursor reconciles current work and establishes a new accepted cursor;
- divergence returns `BLOCKED_EXECUTION_DIVERGENCE` (or narrower accepted blocker) and records no misleading progress;
- no classification expands package scope or Authority.

### 9.6 Delivery / reconciliation time policy

Using `O-TIMEPOLICY` with virtual time, prove exact boundaries:

Dispatch retry:

```text
1s, 2s, 4s, 8s, 16s, 30s, 60s, then <=5m cadence
12 attempts OR 30m -> DELIVERY_UNCERTAIN diagnostic
```

Reconciliation:

```text
0-5m: 30s
5-30m: 2m
30m-2h: 5m
>2h: 15m + diagnostic/alert signal
```

Virtual time proves policy conformance only. It cannot be cited as historical availability evidence.

### 9.7 Current rollout preservation

Prove that the existence of dispatch code does not silently authorize current cross-Primary zero-turn execution.

Required controls:

- dispatch allowed only on a path already authorized by current policy/rollout facts;
- a currently denied cross-Primary case issues no provider request;
- non-Current/future capability fixtures cannot be cited as Current authorization.

---

## 10. Required EvidenceArtifacts

P32 must produce a new exact-head reviewer-resolvable CP-I05 bundle containing, at minimum:

```text
CPV-E-DISPATCH-FAULT-MATRIX
CPV-E-RESUME-CORPUS
CPV-E-DELIVERY-POLICY
CPV-E-RECONCILIATION-POLICY
```

Preferred deterministic files:

```text
dispatch-fault-matrix.json
resume-corpus.json
delivery-policy.json
reconciliation-policy.json
evidence-manifest.json
```

The bundle may include additional exact-result/progress subfamilies when that improves reviewer auditability, but aggregate metrics alone are insufficient.

Each mandatory case family must expose exact case identity, relevant before/after canonical and operational state, provider observation/correlation, mutation result when applicable, and zero-residue/no-amplification facts.

The manifest must bind:

- `CP-I05-P31-01`;
- exact P31 package ref;
- task anchor `a3fd350c...` with `relation: ancestor`;
- actual P32 result revision;
- predecessor CP-I04 P34 comment `5486917398`;
- exact Authority refs;
- test/oracle identities and commands;
- evidence file digests;
- deterministic adapter/config/time-policy identity;
- all zero-tolerance metrics;
- `p34_gate_pass: false`;
- Current cross-Primary rollout status.

Evidence compiler has no authority to issue Gate PASS or `ACCEPTED_FOR_DOWNSTREAM`.

---

## 11. Engineering / performance constraints for this slice

CP-I05 must preserve accepted P18 budgets without claiming R0/S0 attainment from D0 tests.

Reference dispatch targets when provider/policy capacity permits:

```text
outbox visible -> worker claim:        p95 <= 1 s, p99 <= 5 s
worker claim -> first provider request: p95 <= 2 s, p99 <= 10 s
commit -> first provider request:       p95 <= 3 s, p99 <= 15 s
```

Reference callback/reconciliation targets:

```text
callback received -> reconciliation starts: p95 <= 5 s, p99 <= 30 s
missed callback -> query recovery: 99% <= 5 min, 99.9% <= 15 min
```

These are engineering contracts, not permission to use stale data and not automatic P34 evidence unless the applicable P20 profile requires and measures them.

No remote provider call may occur while a canonical store transaction is open.

No new project-wide/global lock may be introduced.

---

## 12. Expected P32 implementation sequence

P32 should follow TDD and keep the implementation reviewable in this order:

1. add RED tests for committed-outbox visibility, worker canonical-write prohibition, and duplicate dispatch identity;
2. add operational delivery metadata/claim APIs with no canonical write authority;
3. add deterministic execution-surface adapter + exact correlation/query/result model;
4. implement `control-dispatch` over committed outbox and duplicate/crash reconciliation;
5. add RED tests for `RECORD_EXECUTION_PROGRESS` frozen-start-fact semantics, then implement the operation;
6. add P33 four-state resume classifier and corpus;
7. add callback-loss/query reconciliation and exact result materialization terminal guard;
8. add virtual-clock delivery/reconciliation policy tests and implementation;
9. run CP-I01..I04 regression suites and verify no accepted invariant drift;
10. materialize exact-head CP-I05 evidence and reviewer-accessible P32 return.

If a RED test proves that accepted Authority cannot be represented without semantic redesign, stop and return the earlier-layer blocker instead of changing the contract inside P32.

---

## 13. Exit criteria

P32 may return `COMPLETE / MATERIALIZED / READY_FOR_P34_REVIEW` only when all are true:

```text
dispatch_before_commit = 0
worker_direct_canonical_writes = 0
semantic_occurrence_amplification_from_duplicate_transport = 0
duplicate_terminal_revision = 0
age_only_terminalization = 0
unreviewable_result_accepted_as_complete = 0
valid_descendant_resume_replayed_completed_work = 0
diverged_resume_accepted = 0
unauthorized_cross_primary_provider_request = 0
```

And:

- CP-I05 focused tests pass;
- full Control Plane regression passes;
- Project State regression passes;
- Skillset/composition regression passes;
- prior CP-I01..I04 exact semantics remain green;
- four P33 states classify exactly;
- G40 delivery uncertainty and G41 callback-loss cadence materialize case-level evidence;
- required exact-result cases materialize reviewer-auditable evidence;
- the final artifact is bound to the exact result revision and all file digests independently verify;
- P32 return carries a reviewer-accessible `materialized_ref`;
- evidence compiler still cannot issue P34 PASS.

CP-I05 is not `ACCEPTED_FOR_DOWNSTREAM` until P34 independently resolves the return/evidence and issues its own Gate verdict.

---

## 14. Blocked return behavior

P32 must stop and return the narrowest owning blocker when any of these occurs:

### Earlier Authority / contract ambiguity

Examples:

- accepted P12/P13 navigation shape cannot represent `RECORD_EXECUTION_PROGRESS` without redefining schema;
- Execution Surface position semantics conflict with P12/P13;
- current rollout policy would need weakening to dispatch.

Return the earlier owning layer; do not patch Authority inside implementation.

### `BLOCKED_EVIDENCE`

Use when the runtime/test result exists but an exact reviewer-accessible durable result/evidence artifact cannot be materialized or independently resolved.

Do not substitute local state, transcript, or executor prose.

### `BLOCKED_IMPLEMENTATION`

Use for implementation-owned failures inside the authorized package surface after Authority is confirmed.

### `BLOCKED_ENVIRONMENT`

Use when required deterministic/runtime tooling is unavailable and the failure is truly environmental rather than a provider/contract ambiguity.

### Execution divergence

If P32/P33 observes incompatible history such that neither the required task anchor ancestry nor an accepted resume cursor can establish a trusted continuation:

```text
BLOCKED_EXECUTION_DIVERGENCE
```

or the more specific accepted Authority/environment blocker.

Do not reset/rewrite history to make the task appear resumable.

---

## 15. P31 disposition

```yaml
stage: P31 Task Packaging — CP-I05
package_id: CP-I05-P31-01
status: READY / MATERIALIZED
task_anchor:
  revision: a3fd350c350bec9220a1c6e283de88c14dfbcd2a
  relation: ancestor
resume_cursor: null
source_cp_i04_p34_comment: 5486917398
execution_surface: CONTROL_REASONING
next_execution_surface: CODE_EXECUTION
```

P31 stops here.

The next legal lifecycle action is `P32 Implementation — CP-I05` using the exact package ref that materializes this document. P31 does not execute P32.