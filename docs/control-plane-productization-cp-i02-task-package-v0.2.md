# Aegis Control Plane Productization v0.2 — CP-I02 P31 Task Package

Status: **P31 READY / MATERIALIZED — authorized package for later P32 execution**

Package ID: `CP-I02-P31-01`

Owner: `aegis-implementation`

Current stage: `P31 Task Packaging`

Target execution stage: `P32 Implementation`

Current execution surface: `CONTROL_REASONING`

Preferred later execution surface: `CODE_EXECUTION`

This artifact packages only **CP-I02 — Canonical mutation, lane CAS, idempotency, transactional outbox**. It does not begin P32, issue Evidence/ProofEvaluation, or produce a P34 Gate verdict.

---

# 1. Exact package trust anchor

Repository:

`Mostorm-Labs/aegis`

Accepted predecessor implementation:

- slice: `CP-I01 — Independent proof foundation + canonical semantic spine`
- exact accepted revision: `a996edb00fbbe1f292bba6e3634118e215fe4c14`
- P34 rereview comment: `5474322167`
- verdict: `PASS`
- downstream disposition: `ACCEPTED_FOR_DOWNSTREAM`

Required repository ancestry contract for later P32:

```yaml
task_anchor:
  revision: a996edb00fbbe1f292bba6e3634118e215fe4c14
  relation: ancestor
resume_cursor: null
```

`Task Anchor != Execution Cursor` remains controlling.

The P32 executor MUST establish that its accepted starting revision descends from this exact CP-I01 Gate-accepted anchor. It MUST NOT require HEAD equality with the historical anchor when ancestry is valid.

The exact P31 `package_ref` is the reviewer-accessible commit containing this file and must be carried by the later P32 surface handoff.

---

# 2. Exact trusted basis

P32 is authorized only against the accepted chain below. This package consumes it; it does not reopen or supersede it.

## Product

- head: `c628bdc15fdd3d32511a04b6f09055413f2786c3`
- Product Authority Review #2: `5061188138`
- disposition: `PASS / ACCEPTED_FOR_DOWNSTREAM`

## Modeling

- head: `f29c4da3698038e0174e4380707fa618b03c40b2`
- P21 Authority Review #3: `5062616510`
- disposition: `PASS / ACCEPTED_FOR_DOWNSTREAM`

Primary CP-I02 semantic source:

- `docs/control-plane-productization-operations-v0.2.md` — accepted P13 operation / mutation model.

## Architecture

- head: `e657f0e74771184b98f8c8e6f8a8581e4858c82d`
- P21 Authority Review: `5062769390`
- disposition: `PASS / ACCEPTED_FOR_DOWNSTREAM`

Primary CP-I02 architecture sources:

- `docs/control-plane-productization-modules-v0.2.md` — P15 `control-store` / `control-mutation` ownership;
- `docs/control-plane-productization-runtime-flow-v0.2.md` — P16 CAS / transaction / commit-before-dispatch choreography;
- `docs/control-plane-productization-platform-contract-v0.2.md` — P17 transactional durable-store capability contract.

## Verification

- accepted P20 head: `db83168e4086e47a7f431acf289006e4f25b8ffd`
- P21 review: `5062933855`
- disposition: `PASS / ACCEPTED_FOR_DOWNSTREAM`

Combined normative P20 package:

1. `docs/control-plane-productization-verification-v0.2.md`
2. `docs/control-plane-productization-verification-v0.2-p21-repair.md`

Repair blob:

`5bed0ce054ead0902bc8c72601814b2f63525067`

Applicable proof focus for this slice:

- `CPV-C01 Canonical Safety` / `CPV-R01..R05`;
- canonical/atomic/idempotency portions of `CPV-C02 Dispatch / Idempotency Safety` / `CPV-R06..R08,R10`;
- `O-AUTH`, accepted `O-CRM`, and a new independent `O-STORE` path;
- G01-G03 canonical subtraces plus the atomicity/history portions applicable before real dispatch exists.

## P30 implementation plan

- artifact: `docs/control-plane-productization-implementation-plan-v0.2.md`
- exact materialized head: `87cbb166411795261ec5f6e7034a89435e053451`
- selected slice: `CP-I02 — Canonical mutation, lane CAS, idempotency, transactional outbox`.

## Predecessor implementation reality

CP-I01 code at `a996edb...` is accepted implementation reality and the required predecessor for this task. It is not promoted into Product/Model/Architecture/Verification Authority.

The accepted CP-I01 canonical/reference foundation MUST be reused and preserved; P32 must not silently rewrite it merely to make CP-I02 easier.

---

# 3. Package objective

Implement the smallest durable mutation vertical slice that proves one Control Plane trajectory can be safely changed through the single canonical writer before projection/policy/scheduler/provider/real-dispatch complexity is introduced.

Required shape:

```text
accepted P13 operation request
  -> exact canonical/idempotency/current-state validation
  -> lane CAS / expected-record guards
  -> one atomic durable transaction
       canonical immutable revision(s)
       + lane-head advance where applicable
       + semantic idempotency result
       + permitted durable outbox where scheduling requires it
  -> committed canonical result
  -> independent durable-state audit
```

The slice must make partial/duplicate/stale writes observable as test failures rather than hide them behind process-local state.

---

# 4. Resolved implementation profile for CP-I02

P17 is capability-based and deliberately does not select a final database vendor. For this bounded implementation slice, P31 resolves the local durable adapter as:

```text
Python 3.12
+ Python stdlib sqlite3
+ file-backed SQLite database for durability/concurrency/crash-reopen evidence
```

This is an implementation mechanism for the P17 local-development profile, **not** a final managed-database Authority decision.

Rules:

1. No new third-party persistence dependency is required.
2. Durable/concurrency evidence MUST use a file-backed database; `:memory:` alone is insufficient evidence for this slice.
3. SQLite physical writer serialization MUST NOT become the semantic concurrency oracle. Lane CAS/expected-state guards remain the reason a same-lane loser is rejected.
4. No application-wide/global semantic lock may be introduced to manufacture correctness.
5. Operational SQLite busy handling may retry/serialize physical writes, but unrelated lanes must not be reported as semantic lane conflicts merely because the storage engine serialized writers.
6. Committed state must survive connection close/reopen in the evidence fixtures.
7. Remote/provider calls are forbidden inside a canonical transaction.

If the chosen SQLite profile cannot satisfy an accepted semantic atomicity requirement, P32 must stop and route the capability conflict upstream as required by P30; it may not weaken P13/P15/P16 semantics.

---

# 5. Authorized production responsibilities

## 5.1 `control-store`

Implement a small durable store adapter that provides persistence mechanics only.

Required capabilities:

- immutable canonical record revision append/read for the three accepted durable object families:
  - `STAGE_OCCURRENCE`;
  - `VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE`;
  - `ESCALATION`;
- exact canonical bytes/digest preservation using the accepted CP-I01 primitives;
- canonical identity uniqueness by stable object identity + `record_revision`;
- lane-head/version read and compare-and-advance;
- semantic idempotency record read/append;
- durable outbox record append/read;
- one atomic transaction spanning the records required by one accepted mutation;
- read-only audit/export support sufficient for independent `O-STORE` verification.

Store metadata such as lane heads, idempotency rows, and outbox rows are persistence/control metadata. They MUST NOT be presented as new P12 first-class canonical aggregates.

The store does not decide whether a P13 transition is semantically legal.

## 5.2 `control-mutation`

Implement the single canonical mutation boundary for the CP-I02 operation subset.

Required pipeline:

```text
validate request shape
-> read exact current canonical state
-> classify operation_request_id + fingerprint
-> validate operation-specific semantic preconditions
-> validate expected lane / target-record state
-> execute compare-and-append transaction
-> return exact committed/replayed result
```

Only this production module may invoke canonical append/lane-advance persistence mechanics.

No scheduler, dispatch worker, recovery helper, facade, test helper, or other production module may directly append canonical records.

---

# 6. P13 operation subset authorized in CP-I02

P32 must preserve the exact accepted P13 vocabulary, but this slice implements only the bounded operations needed for mutation/atomicity proof:

```text
MATERIALIZE_IMPLEMENTATION_PACKAGE
REVISE_IMPLEMENTATION_PACKAGE
SCHEDULE_STAGE_OCCURRENCE
TERMINATE_STAGE_OCCURRENCE
RAISE_ESCALATION
```

Required semantics:

## 6.1 `MATERIALIZE_IMPLEMENTATION_PACKAGE`

- create exactly revision `1`;
- reject/replay according to semantic idempotency rather than create a duplicate lineage;
- canonical record is complete and digest-bound before commit.

## 6.2 `REVISE_IMPLEMENTATION_PACKAGE`

- requires exact expected prior revision and digest;
- appends exactly `prior + 1`;
- prior revisions remain immutable/addressable;
- stale concurrent revise cannot silently rebase or last-write-win.

## 6.3 `SCHEDULE_STAGE_OCCURRENCE`

For the permitted schedule fixtures exercised in this slice, one transaction must atomically materialize:

```text
StageOccurrence revision 1 / OPEN
+ lane-head advance
+ semantic idempotency result
+ durable outbox record
```

A failed/CAS-losing transaction creates no occurrence and no outbox.

This slice does not implement the real projection/policy/scheduler that decides whether cross-Primary automation is currently allowed. Test fixtures therefore exercise only a schedule request already designated as permitted for the bounded mutation proof. CP-I02 MUST NOT claim rollout-policy correctness.

## 6.4 `TERMINATE_STAGE_OCCURRENCE`

- target must be the exact current OPEN occurrence revision;
- append exactly one terminal revision;
- frozen start facts remain unchanged;
- no successor occurrence/outbox is created implicitly;
- a second/conflicting terminalization fails closed.

## 6.5 `RAISE_ESCALATION`

When P13 requires escalation to accompany an escalated terminalization, one transaction must atomically:

```text
create Escalation revision 1
+ append the terminal StageOccurrence revision that references the new escalation ID
+ append semantic idempotency result
```

No orphan Escalation and no terminal revision pointing to a missing Escalation may survive rollback/crash injection.

Known P13 operations assigned to later slices — including execution-progress recording, escalation resolution, specialized repair/reverify/rereview scheduling, and projection recomputation — must fail closed without canonical mutation if invoked through the CP-I02 partial implementation. P32 must not implement them opportunistically.

---

# 7. Canonical concurrency and idempotency invariants

P32 must mechanically preserve all of the following.

## Lane CAS

1. Lane head/version is the semantic serialization boundary for one control trajectory.
2. Same-lane contenders that both start from `L@N` cannot both commit an `N -> N+1` transition.
3. The winner creates the one accepted canonical mutation.
4. The loser creates no canonical revision, no idempotency success record, and no outbox for the rejected candidate.
5. The loser must receive a deterministic conflict requiring re-read/reasoning rather than force-apply.
6. Independent lanes may both commit successfully without a semantic cross-lane conflict.
7. Locks/leases/storage-engine writer serialization cannot make stale expected state valid.

## Semantic idempotency

1. `operation_request_id + identical idempotency_fingerprint` returns the exact previously materialized semantic result.
2. Replay creates no additional canonical revision, lane advance, or outbox.
3. Same `operation_request_id + different fingerprint` fails closed and creates no mutation.
4. Idempotency result and accepted mutation commit atomically when replay safety requires them to agree.
5. Request arrival timestamps/UUID timestamp bits never decide winner or lifecycle order.

## Immutable history

1. Prior record revisions are never updated in place.
2. Stable `kind / id_scheme / id` identity is preserved across one lineage.
3. `record_revision` is contiguous.
4. One StageOccurrence has at most one terminal revision.
5. Terminal occurrence A never implicitly materializes successor B.

---

# 8. Transaction and outbox invariants

For a permitted schedule mutation, the all-or-none unit is:

```text
validate expected state
+ append OPEN StageOccurrence r1
+ advance lane head
+ append idempotency result
+ append durable outbox
COMMIT
```

Before commit, no separate reader may observe a semantically committed outbox/occurrence pair.

After commit:

- occurrence and outbox are both durable;
- process/connection close and reopen cannot lose one while retaining the other;
- no remote dispatch is executed by CP-I02;
- outbox is evidence of durable dispatch intent only;
- delivery acknowledgement/attempt state is outside this semantic transaction.

For terminalization:

```text
append one terminal revision
+ append idempotency result
COMMIT
```

No successor outbox belongs to this transaction.

For escalation atomicity, use the exact P13 companion semantics in §6.5.

---

# 9. Independent oracle requirements

## 9.1 Reuse accepted `O-CRM`

The Gate-accepted CP-I01 reference model remains the semantic transition oracle. CP-I02 production code must not be imported by `O-CRM` to compute expected truth.

P32 SHOULD consume the existing reference model rather than modify it. If CP-I02 cannot be correctly implemented without changing accepted CP-I01 oracle semantics, stop and return the exact blocker instead of silently changing predecessor truth.

## 9.2 Add independent `O-STORE`

Create a test-only durable-state oracle that inspects the SQLite evidence database independently from the production mutation flow.

`O-STORE` must verify at least:

- exact committed canonical record set;
- canonical bytes/digests and immutable lineage;
- lane versions/heads;
- idempotency rows;
- outbox rows and their occurrence binding;
- absence of duplicate terminal revisions;
- absence of half-committed schedule/escalation transactions;
- persistence after database close/reopen.

Strong independence requirement:

> `O-STORE` must not use `MutationService` or the production store write path as its only way to determine expected/observed durable truth.

Direct read-only SQL/database audit is permitted and preferred for this slice.

## 9.3 `O-AUTH` / structural ownership probe

Add a mechanical/static test proving the CP-I02 production tree has no second canonical writer path. At minimum, no production module outside the declared mutation/store boundary may invoke raw canonical append/lane-advance SQL or transaction methods.

CI green is not the oracle; this check is part of the evidence consumed by P34.

---

# 10. Required tests

P32 must use TDD for new behavior and add isolated CP-I02 tests covering at least the following.

## Package lineage

- materialize package r1;
- duplicate identity rejected/replayed according to idempotency;
- valid revise r1 -> r2;
- stale expected revision/digest revise rejected with no new revision;
- immutable prior bytes/digest remain unchanged.

## Schedule atomicity

- permitted schedule creates exactly OPEN r1 + one lane advance + one idempotency result + one outbox;
- second reader cannot treat pre-commit work as committed truth;
- injected failure after each pre-commit write boundary rolls back the complete semantic transaction;
- reopen after rollback shows the original lane state and no orphan occurrence/outbox/idempotency success;
- reopen after commit shows the full committed set.

## Same-lane race

- two independent connections/actors start from the same lane version;
- exactly one wins;
- exactly one OPEN occurrence and outbox exist;
- loser creates no semantic residue;
- canonical winner is determined by CAS, not an application-global lock or timestamp.

## Independent-lane concurrency

- unrelated lanes may both commit;
- storage-engine serialization/busy retry must not surface as a semantic same-lane conflict;
- no cross-lane head corruption.

## Idempotency

- identical request ID + fingerprint replays the exact result;
- replay adds zero revisions/outbox entries;
- same request ID + different fingerprint conflicts with zero mutation.

## Terminalization

- exact current OPEN occurrence can append one terminal revision;
- second/conflicting terminalization is rejected;
- no revision exists after terminal;
- terminalization creates no successor occurrence/outbox.

## Escalation companion atomicity

- Escalation r1 + terminal occurrence reference commit together;
- injected rollback leaves neither companion half-committed;
- Escalation never gains revision 2 in this slice.

## Unsupported later operations

- every P13-known-but-out-of-slice operation fails closed with no canonical/store mutation;
- no later-slice behavior is accidentally implemented.

## Predecessor regression

Existing CP-I01 canonical/reference/qualification tests must remain green and must not be weakened or deleted.

---

# 11. Required test commands

Focused CP-I02 command:

```text
python3 -m unittest discover -s tests/control_plane -p 'test_cp_i02_*.py' -v
```

Full Control Plane regression:

```text
python3 -m unittest discover -s tests/control_plane -v
```

Existing repository regressions:

```text
python3 -m unittest discover -s tests/project_state -v
python3 -m unittest discover -s tests/skillset -v
```

If another Current repository-mandatory integrity command is triggered by the authorized files, run it without widening semantic scope.

---

# 12. Required EvidenceArtifacts / durable output

P32 must produce a reviewer-resolvable exact artifact bundle for this slice.

Required evidence families:

1. `CPV-E-CANONICAL-CONFORMANCE`
   - single-writer, immutable history, same-lane CAS, independent-lane semantic behavior, multi-record atomicity;
2. `CPV-E-STORE-AUDIT`
   - independent direct durable-state audit of exact committed records/lane/idempotency/outbox state;
3. raw canonical trace corpus
   - deterministic schedule/race/idempotency/terminal/escalation/crash traces with exact expected/observed outcomes.

The artifact bundle should contain at least:

```text
artifacts/cp-i02/evidence-manifest.json
artifacts/cp-i02/store-audit.json
artifacts/cp-i02/trace-corpus.json
artifacts/cp-i02/crash-matrix.json
```

Exact file naming may vary only if the same evidence is durably and unambiguously materialized.

The manifest must record at least:

- `task_id = CP-I02-P31-01`;
- exact P31 package ref;
- exact result revision;
- exact CP-I01 accepted predecessor revision `a996edb...` and P34 comment `5474322167`;
- Product/Modeling/Architecture/P20 exact refs;
- Python version;
- SQLite runtime version;
- test commands;
- canonical/store schema or contract digest sufficient to bind the audited representation;
- scenario/trace identities;
- metrics and threshold results;
- hashes/digests of each emitted evidence file.

Mandatory CP-I02 zero-tolerance metrics:

```text
illegal accepted transitions = 0
duplicate canonical head = 0
half-committed semantic transactions = 0
same-lane double winners = 0
idempotency replay amplification = 0
conflicting-idempotency accepted mutations = 0
duplicate terminal revisions = 0
successor-before/sealed-into-terminal = 0
orphan schedule outbox/occurrence pairs = 0
orphan escalation companions = 0
```

The artifact may preserve G01-G03 identities for the canonical portions exercised here, but MUST NOT falsely claim the complete integrated D0 scenario result.

Explicit non-claims for CP-I02 evidence:

- no complete `CPV-E-D0-CONFORMANCE`;
- no complete `CPV-E-DISPATCH-FAULT-MATRIX` because real dispatch/reconciliation is not implemented;
- no Current rollout-policy proof;
- no provider-currentness proof;
- no R0/S0 performance proof;
- no seven-day cost or monthly availability proof;
- no P34 Gate PASS inside the evidence manifest.

---

# 13. Authorized repository paths

P32 may create/modify only the following paths:

```text
tools/aegis_control/store.py
tools/aegis_control/mutation.py
tools/aegis_control/__init__.py

tests/control_plane/store_oracle.py
tests/control_plane/cp_i02_fixtures.py
tests/control_plane/cp_i02_evidence.py
tests/control_plane/generate_cp_i02_evidence.py
tests/control_plane/test_cp_i02_*.py

.github/workflows/control-plane-cp-i02.yml
```

The existing CP-I01 semantic/reference files are predecessor truth for this package and are intentionally outside the normal edit scope, including:

```text
tools/aegis_control/canonical.py
tests/control_plane/reference_model.py
tests/control_plane/qualification.py
tests/control_plane/verifier_helpers.py
tests/control_plane/completeness_oracle.py
.github/workflows/control-plane-foundation.yml
```

They must still run as regression inputs.

If implementation genuinely requires changing one of these accepted predecessor files, stop and return the exact need to P31/P34 rather than silently widening scope.

Explicitly outside scope:

```text
.aegis/**
skills/**
skillset/**
plugins/**
docs/control-plane-productization-*.md
tools/aegis_state/**
tools/aegis_skillset/**
tests/project_state/**
tests/skillset/**
```

The CP-I02 package document itself remains unchanged during P32.

---

# 14. Explicit non-goals

P32 MUST NOT implement or modify:

- `control-projection`;
- `control-policy`;
- `control-scheduler`;
- actual `control-dispatch` / delivery worker behavior;
- provider/GitHub/Project State/Proof/Codex/ChatGPT adapters;
- SourceSnapshotToken currentness integration;
- REQUIRED-child acceptance binding logic beyond store mechanics not exercised by this slice;
- execution-progress/sessionless resume;
- escalation resolution;
- repair/reverify/rereview scheduling runtime;
- recovery coordinator;
- Control Service HTTPS API;
- Aegis Control App;
- Current cross-Primary automatic progression;
- P34 review/verdict logic;
- `.aegis` / Project State / Proof Plane / Skill / Execution Surface Authority;
- CP-I03 or later-slice behavior;
- R0/S0/7-day/monthly measurement claims;
- final database/cloud/broker selection.

No real remote provider call may occur while a canonical transaction is open.

---

# 15. Performance / engineering constraints

CP-I02 has **no R0/S0 throughput pass claim**.

Correctness constraints still apply:

- no application-global semantic lock;
- same-lane CAS is the semantic conflict oracle;
- unrelated lanes must not generate false semantic lane conflicts;
- deterministic/reproducible crash/race fixtures take precedence over micro-optimization;
- store audit must survive process/connection-independent reopen;
- no network/provider dependency in focused tests;
- any zero-tolerance semantic violation invalidates a positive CP-I02 result.

The P20 R0 unrelated-lane conflict-rate threshold is not claimed by this slice; performance measurement remains later work.

---

# 16. Required P32 executor workflow

When P32 is explicitly started, the code execution surface must:

1. inspect branch/HEAD/diff before edits;
2. resolve this exact P31 package ref;
3. verify `a996edb00fbbe1f292bba6e3634118e215fe4c14` is an ancestor of the accepted starting revision;
4. record the actual starting revision;
5. re-resolve the CP-I01 P34 PASS comment `5474322167` and fail closed if contradictory fresh evidence has appeared;
6. inspect the exact accepted P13/P15/P16/P17/P20 refs named above;
7. implement only the authorized CP-I02 files;
8. use TDD for new behavior;
9. run the focused CP-I02 suite;
10. run the full Control Plane regression suite;
11. run Project State and Skillset regressions;
12. generate the exact CP-I02 evidence bundle;
13. push/materialize the exact implementation to a reviewer-accessible remote branch/PR;
14. obtain exact-head CI/evidence artifact refs;
15. return the compact result contract below.

A code-surface handoff changes execution location only; `aegis-implementation` remains the P32 Primary Owner.

---

# 17. Required P32 return contract

```yaml
task_id: CP-I02-P31-01
package_ref: <exact commit containing this P31 package>
task_anchor:
  revision: a996edb00fbbe1f292bba6e3634118e215fe4c14
  relation: ancestor
starting_revision: <actual accepted P32 start revision>
result_revision: <exact result commit>
materialized_ref: <reviewer-accessible branch/PR/result ref>
changed:
  - <authorized paths only>
verification:
  focused_command: python3 -m unittest discover -s tests/control_plane -p 'test_cp_i02_*.py' -v
  focused_result: PASS | FAIL
  full_control_plane: PASS | FAIL
regression:
  project_state: PASS | FAIL | NOT_APPLICABLE_WITH_REASON
  skillset: PASS | FAIL | NOT_APPLICABLE_WITH_REASON
evidence:
  canonical_conformance: <exact CPV-E-CANONICAL-CONFORMANCE ref>
  store_audit: <exact CPV-E-STORE-AUDIT ref>
  trace_corpus: <exact durable ref>
  crash_matrix: <exact durable ref>
metrics:
  illegal_accepted_transitions: <N>
  duplicate_canonical_heads: <N>
  half_commits: <N>
  same_lane_double_winners: <N>
  idempotency_replay_amplification: <N>
  conflicting_idempotency_accepted_mutations: <N>
  duplicate_terminal_revisions: <N>
  orphan_schedule_pairs: <N>
  orphan_escalation_companions: <N>
authority_deviation: none | <exact blocker>
scope_deviation: none | <exact blocker>
blocker: none | <classified blocker>
```

A local-only commit/worktree/test transcript is not sufficient to return to `CONTROL_REVIEW`.

---

# 18. Exit criteria

CP-I02 may return from P32 as implementation-complete only if all are true:

1. Starting revision satisfies the task-anchor ancestry relation.
2. CP-I01 P34 PASS remains the accepted predecessor and no contradictory fresh Authority/evidence is found.
3. Changes remain entirely within §13.
4. File-backed durable Control Store exists and survives close/reopen.
5. `control-mutation` is the only production canonical writer.
6. Package materialize/revise preserve immutable exact revision lineage.
7. Same-lane race has exactly one canonical winner; loser leaves no semantic residue.
8. Independent lanes both complete without a semantic cross-lane conflict.
9. Idempotent replay creates no additional semantic writes/outbox; conflicting fingerprint creates no mutation.
10. Permitted scheduling commits OPEN + lane advance + idempotency + outbox all-or-none.
11. Every injected pre-commit crash point leaves zero half-committed semantic transaction after reopen.
12. Terminalization produces at most one terminal revision and no implicit successor.
13. Escalation companion semantics are all-or-none with no orphan.
14. Unsupported later P13 operations fail closed without write.
15. `O-CRM`, `O-STORE`, and ownership/Authority checks remain independent from the production mutation control flow as required.
16. Focused CP-I02 tests pass.
17. Full Control Plane regression passes, preserving CP-I01.
18. Project State and Skillset regressions remain green, or an unrelated pre-existing failure is reported exactly without out-of-scope repair.
19. All zero-tolerance CP-I02 metrics in §12 are zero.
20. Exact result and evidence bundle are durably materialized and independently reviewer-resolvable.
21. No CP-I03+ behavior or forbidden Authority mutation occurred.

These criteria make the implementation eligible to return to P34 `CONTROL_REVIEW`; they do not issue Gate PASS.

---

# 19. Blocked return behavior

## Earlier Authority / semantic conflict

If P13/P15/P16/P17/P20 cannot be implemented consistently without changing accepted semantics:

```text
BLOCKED_AUTHORITY
```

Return the exact earliest untrusted layer and conflicting refs. Do not redesign Authority inside P32.

## Persistence capability conflict

If the selected SQLite local profile cannot satisfy an accepted atomicity/CAS/durability semantic invariant, stop. Do not emulate correctness with process memory/global locks or weaken the invariant. Route the capability conflict to the owning architecture/platform layer as required by P30.

## Execution divergence

If task-anchor ancestry cannot be established or observed descendant work contradicts this package:

```text
BLOCKED_EXECUTION_DIVERGENCE
```

Preserve valid work; do not force-reset merely to recreate the historical anchor.

## Scope pressure

If correct implementation requires editing a path outside §13, stop and return the exact proposed path/need. Do not silently widen P32 scope.

## Evidence materialization failure

If code/tests exist but the exact result/evidence cannot be made reviewer-accessible:

```text
BLOCKED_EVIDENCE
```

Do not claim review readiness from local state.

## Environment blocker

If required tests cannot execute because of an external environment limitation unrelated to semantics:

```text
BLOCKED_ENVIRONMENT
```

Return the exact failed command/capability and preserve valid modifications.

---

# 20. Future surface handoff prepared by this package

After exact materialization of this P31 package and an explicit user request to begin P32, the intended handoff is:

```yaml
type: surface_handoff
stage: P32
stage_owner: aegis-implementation
from_surface: CONTROL_REASONING
to_surface: CODE_EXECUTION
preferred_executor: codex
reason: repository_heavy_execution
package_ref: <exact commit containing this P31 package>
task_anchor:
  revision: a996edb00fbbe1f292bba6e3634118e215fe4c14
  relation: ancestor
resume_cursor: null
return_surface: CONTROL_REVIEW
```

The user may explicitly choose another available code execution location; execution location does not change `aegis-implementation` stage ownership.

This document does not execute that handoff.

---

# 21. P31 disposition

This package authorizes exactly one bounded implementation slice:

```text
CP-I02 — Canonical mutation, lane CAS, idempotency, transactional outbox
```

No upstream Authority gap was found during packaging.

After exact repository materialization of this document:

```text
P31 Task Packaging — CP-I02 = READY / MATERIALIZED
next stage = P32 Implementation — CP-I02
next surface = CODE_EXECUTION
```

Stop after P31 materialization. Do not begin P32 in the same control occurrence.
