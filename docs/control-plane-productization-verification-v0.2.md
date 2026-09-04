# Aegis Control Plane Productization v0.2 — P20 Verification Design

Status: **Draft / Proposed Authority — P20 Verification Design**

Scope: `aegis/control-plane-productization/verification`

Exact trusted architecture basis:

- PR #27 exact head: `e657f0e74771184b98f8c8e6f8a8581e4858c82d`
- P21 Architecture Authority Review: `5062769390`
- verdict: `PASS / ACCEPTED_FOR_DOWNSTREAM`

Upstream accepted basis retained:

- Product Authority PR #25: `c628bdc15fdd3d32511a04b6f09055413f2786c3`
- Product Authority Review #2: `5061188138` — `PASS / ACCEPTED_FOR_DOWNSTREAM`
- Modeling Authority PR #26: `f29c4da3698038e0174e4380707fa618b03c40b2`
- Modeling P21 Authority Review #3: `5062616510` — `PASS / ACCEPTED_FOR_DOWNSTREAM`

Verification Productization semantics reused by this P20 design:

- PR #23 semantic head: `2eb7d507098d24328b883dfa1366521390026fce`
- Verification Productization P21 #3: `5061120240` — accepted semantic basis
- compatible Proof Plane architecture head: `6faa0eff7a53ccd2828eae1b0ef1aeaef1de1a83`

Retained Current boundaries:

- Project State remains owner of Authority / Gate Decision / Integration truth;
- Proof Plane remains owner of VerificationSpec / ProofObligation / EvidenceArtifact / ProofEvaluation semantics;
- `aegis-verification` owns P20;
- `aegis-gate-review` owns P34 and remains the sole official Gate owner;
- Skill Decomposition v0.2 continues to govern Primary ownership;
- Execution Surface v0.2 continues to govern `Task Anchor != Execution Cursor` and P32/P33 execution-position semantics;
- target architecture capability does not itself authorize zero-user-turn cross-Primary rollout.

This document defines the proof required before a Control Plane implementation may be trusted. It does not implement the runtime, does not claim any P18 target has already been achieved, and does not issue a Gate verdict.

---

# 1. P20 objective

P20 answers:

> **What evidence would credibly prove that the Aegis Control Plane preserves its semantic trust boundaries under normal operation, concurrency, retries, crashes, stale external truth, provider failure, degraded modes, and the D0/R0/S0 engineering workloads?**

The controlling proof chain is:

```text
Requirement
  -> Invariant
  -> Oracle / Reference
  -> Fixture / Corpus
  -> Test / Probe
  -> Metric
  -> Threshold
  -> Evidence Artifact
  -> P34 Gate
```

Core verification rule:

> **The implementation must not be its own only oracle.**

Supporting rules:

> **Correctness invariants are zero-tolerance proof obligations, not performance error budgets.**
>
> **Provider success, CI green, ProofEvaluation, or a clean dashboard is not a P34 verdict.**
>
> **A faster result that weakens exact refs, currentness checks, CAS, commit-before-dispatch, independent review, or immutable history is verification failure.**

---

# 2. Non-goals

P20 does not:

- redefine P10-P18 semantics;
- repair or supersede Skill Decomposition, Execution Surface, Project State, Plugin Distribution, or Proof Plane Authority;
- authorize automatic cross-Primary continuation under Current rollout rules;
- choose a final database, broker, cache, cloud, language, framework, or CI vendor;
- turn a benchmark target into achieved Evidence before execution;
- convert ProofEvaluation into Gate PASS;
- create a second Gate, Finding store, Authority store, or proof database;
- begin P30, P31, P32, P33, P34, P35, or P36 implementation/review work.

---

# 3. VerificationSpec materialization model

This document is the human-reviewable P20 materialization of one VerificationSpec candidate for the Control Plane architecture.

Logical identity:

```yaml
verification_spec:
  id: aegis-control-plane-productization-v0.2
  scope: aegis/control-plane-productization
  version: p20-v0.2
  architecture_ref: e657f0e74771184b98f8c8e6f8a8581e4858c82d
  architecture_review: 5062769390
```

Until the deterministic Proof Plane materializer exists, the immutable Git blob/commit containing this document is the reviewer-resolvable exact materialization boundary for this proposed P20 Authority. A future Proof Plane implementation may additionally emit the canonical schema digest required by the accepted Verification Productization model; it may not reinterpret this P20 contract.

---

# 4. CoverageBasis

## 4.1 Coverage mode

The P14-P18 architecture package is exact and immutable at the reviewed commit, but its requirements are expressed through prose sections, numbered invariants, platform contracts, and P18 target tables rather than one machine-enumerable stable Requirement registry.

Therefore this P20 candidate uses:

```text
CoverageBasis.mode = REVIEW_DECLARED
```

The exact source snapshots are pinned. The declared Requirement universe below is canonical for this VerificationSpec candidate, but P34 must independently confirm that it faithfully covers the reviewed P14-P18 architecture and retained upstream semantic constraints.

That independent coverage-completeness judgment is mandatory. It cannot be self-certified by the same obligation generator used by execution.

## 4.2 Exact source set

```text
P14  docs/control-plane-productization-architecture-v0.2.md
     @ e657f0e74771184b98f8c8e6f8a8581e4858c82d

P15  docs/control-plane-productization-modules-v0.2.md
     @ e657f0e74771184b98f8c8e6f8a8581e4858c82d

P16  docs/control-plane-productization-runtime-flow-v0.2.md
     @ e657f0e74771184b98f8c8e6f8a8581e4858c82d

P17  docs/control-plane-productization-platform-contract-v0.2.md
     @ e657f0e74771184b98f8c8e6f8a8581e4858c82d

P18  docs/control-plane-productization-engineering-v0.2.md
     @ e657f0e74771184b98f8c8e6f8a8581e4858c82d
```

Normative retained external contracts are additionally resolved at review time from their Current exact refs, especially Skill Decomposition v0.2, Execution Surface v0.2, Project State v0.5, Plugin Distribution v0.1, and the accepted Verification Productization semantic package.

## 4.3 Declared Requirement universe

| Requirement ID | Required proposition |
|---|---|
| `CPV-R01` | Control Plane canonical truth is durable and independent from conversation/session/process memory. |
| `CPV-R02` | `control-mutation` is the only canonical Control Plane writer; store/policy/projection/scheduler/dispatch/recovery cannot bypass it. |
| `CPV-R03` | Canonical records are immutable/revisioned/exactly addressable; historical truth is never rewritten by current projection. |
| `CPV-R04` | Lane compare-and-append/CAS is the semantic concurrency oracle; unrelated lanes remain independently concurrent. |
| `CPV-R05` | Child spawn, REQUIRED-child barrier crossing, and other specified multi-record semantic mutations are atomic. |
| `CPV-R06` | Every substantive dispatch is commit-before-dispatch with OPEN occurrence + permitted outbox committed atomically. |
| `CPV-R07` | Transport is at-least-once; duplicate delivery/retry of one occurrence cannot create a new semantic attempt. |
| `CPV-R08` | Terminalization and successor scheduling are separate durable transitions; crash between them preserves terminal history. |
| `CPV-R09` | REQUIRED-child continuation is blocked until exact child acceptance facts exist and successor history pins immutable `RequiredChildAcceptanceBinding` facts. |
| `CPV-R10` | Repair/retry/reverify/rereview semantic attempts are new governed StageOccurrences; timeout/restart/transport retry is not semantic retry. |
| `CPV-R11` | Projection is deterministic/read-only/disposable and stale projection cannot authorize mutation. |
| `CPV-R12` | External Authority/Gate/Proof/Integration/execution/human-decision truth remains externally owned and is consumed through exact refs/snapshot validation. |
| `CPV-R13` | Webhooks/callbacks are wakeups only; query/refetch/reconciliation is the current-truth path. |
| `CPV-R14` | Trust-sensitive mutable currentness is freshly revalidated before commit; stale/ambiguous snapshots fail closed. |
| `CPV-R15` | P34 remains the sole official Gate owner; ProofEvaluation/CI/Control Plane cannot emit or imply Gate PASS. |
| `CPV-R16` | Current Skill Decomposition/Execution Surface Authority gates cross-Primary automation; architecture capability cannot self-authorize rollout. |
| `CPV-R17` | `Task Anchor != Execution Cursor`; all four P33 reconciliation states preserve accepted descendant work and fail closed on true divergence. |
| `CPV-R18` | Human decisions required by policy are durably materialized as exact external refs; raw chat/UI acknowledgement is not silently semantic approval. |
| `CPV-R19` | Public/internal platform APIs preserve P13 operation boundaries; generic status/Gate/canonical PATCH and worker direct canonical writes are forbidden. |
| `CPV-R20` | Credentials/capability tokens remain transport capabilities and do not enter canonical semantic payload/digests/logs improperly. |
| `CPV-R21` | Pause/admission/backpressure/leases/retry timers are operational only and cannot rewrite canonical history. |
| `CPV-R22` | Degraded modes fail closed; an already-controlled active WorkScope cannot silently fall back to duplicate manual substantive execution. |
| `CPV-R23` | Acknowledged canonical commits meet the supported durability/recovery contract; ordinary rollback preserves canonical data. |
| `CPV-R24` | D0 deterministic conformance can execute the full semantic/fault corpus without semantic invariant violation. |
| `CPV-R25` | R0 meets P18 Control API, canonical transaction, projection, outbox, reconciliation, freshness, concurrency, provider-amplification, and resource targets. |
| `CPV-R26` | S0 = 4x R0 for 15 minutes preserves all zero-tolerance semantic invariants and applies recoverable deterministic backpressure. |
| `CPV-R27` | Provider retry/liveness rules do not infer semantic failure from age alone and do not create replacement occurrences on timeout. |
| `CPV-R28` | Canonical history/idempotency retention, exact archival retrieval, and required indexes preserve replay/audit correctness. |
| `CPV-R29` | Required observability exposes latency, conflict, outbox, occurrence, snapshot, retry, failure, cost, and zero-tolerance invariant counters without becoming semantic truth. |
| `CPV-R30` | Full-profile sessionless resume and transport remove manual ref-copy dependence while preserving exact ownership/materialization boundaries. |

Coverage completeness over this declared set remains a mandatory P34 review obligation because `REVIEW_DECLARED` is used.

---

# 5. Claim set and assurance policy

P20 groups the Requirement universe into falsifiable Claims. Criticality is driven by the consequence of false acceptance.

| Claim | Requirements | Criticality | Minimum assurance | Base profile | Execution context |
|---|---|---|---|---|---|
| `CPV-C01 Canonical Safety` | R01-R05 | CRITICAL | QUALIFIED | PROPERTY | INTEGRATION |
| `CPV-C02 Dispatch / Idempotency Safety` | R06-R08, R10 | CRITICAL | QUALIFIED | PROPERTY | INTEGRATION |
| `CPV-C03 Historical Child / External Truth` | R09, R12-R14 | CRITICAL | QUALIFIED | REFERENCE | INTEGRATION |
| `CPV-C04 Ownership / Gate / Rollout Integrity` | R15-R16 | CRITICAL | QUALIFIED | REFERENCE | PLATFORM |
| `CPV-C05 Resume / Sessionless Control` | R17, R30 | CRITICAL | CHALLENGED | EXAMPLE | CROSS_IMPLEMENTATION |
| `CPV-C06 Human Decision Integrity` | R18 | CRITICAL | CHALLENGED | REFERENCE | PLATFORM |
| `CPV-C07 API / Capability / Credential Boundary` | R19-R20 | CRITICAL | QUALIFIED | PROPERTY | PLATFORM |
| `CPV-C08 Derived / Operational State Separation` | R11, R21 | CRITICAL | CHALLENGED | PROPERTY | INTEGRATION |
| `CPV-C09 Degraded Recovery / Durability` | R22-R23, R27 | CRITICAL | QUALIFIED | PROPERTY | INTEGRATION |
| `CPV-C10 D0 Semantic Conformance` | R24 | CRITICAL | QUALIFIED | REFERENCE | INTEGRATION |
| `CPV-C11 R0 Engineering Budget` | R25 | CRITICAL | CHALLENGED | MEASURE | PLATFORM |
| `CPV-C12 S0 Stress / Backpressure Safety` | R26 | CRITICAL | QUALIFIED | MEASURE | PLATFORM |
| `CPV-C13 Retention / Replay / Audit` | R28 | CRITICAL | CHALLENGED | REFERENCE | INTEGRATION |
| `CPV-C14 Observability / Cost Attribution` | R29 | ORDINARY | CHALLENGED | MEASURE | PLATFORM |

No Claim is allowed to reduce an upstream invariant merely to make proof easier.

---

# 6. Independent oracle stack

The verification design intentionally separates production implementation from the strongest correctness oracles.

## 6.1 `O-AUTH` — exact Authority/reference oracle

Reads the exact reviewed Product / Modeling / Architecture documents and Current external contracts.

Use:

- schema/contract conformance;
- owner/capability restrictions;
- exact status/reason requirements;
- target thresholds.

It is documentary reference, not runtime behavioral proof by itself.

## 6.2 `O-CRM` — Control Reference Model

A deliberately smaller deterministic reference interpreter for Control Plane state transitions.

It models only semantic truth necessary to decide:

- legal/illegal P13 transitions;
- expected lane head and occurrence revision lineage;
- Required-child barrier legality;
- idempotent replay result;
- repair/reverify/rereview occurrence identity;
- terminal/successor separation;
- current-policy admission decision;
- generated projection from canonical + supplied external snapshots.

`O-CRM` MUST NOT reuse the production scheduler/mutation implementation as its oracle.

Allowed shared dependencies are limited to canonical enum/schema definitions and canonical encoding/digest primitives. Production control-flow functions are forbidden as the reference computation.

## 6.3 `O-STORE` — transaction/history oracle

Validates durable state directly through test-only read APIs / database audit export:

- exactly committed record set;
- lane versions;
- immutable revision lineage;
- idempotency records;
- outbox atomicity;
- no illegal duplicate terminal revision;
- no history loss after supported crash/restart.

The oracle observes state; it does not mutate canonical data.

## 6.4 `O-PROVIDER` — deterministic provider simulator family

Fake Project State / Codex / GitHub / CI / Proof / Human Decision providers support controlled:

- callback loss;
- duplicate callback;
- callback reordering;
- delayed materialization;
- stale snapshot token;
- version change between read and commit;
- rate limit;
- timeout;
- provider job completion before callback;
- ambiguous/missing exact ref;
- capability disappearance;
- immutable result resolution.

Every simulation is seedable and replayable.

## 6.5 `O-CONTRACT` — API/capability conformance oracle

Validates:

- versioned HTTPS/JSON envelope behavior;
- P13 operation-only canonical mutation surface;
- `Idempotency-Key == operation_request_id`;
- absence/rejection of forbidden generic PATCH/status/Gate writes;
- worker inability to append canonical records directly;
- least-authority credential/capability matrix;
- unsupported version fail-closed behavior.

## 6.6 `O-COMPLETE` — independent obligation completeness oracle

P34-side checker derives expected semantic obligation keys from the exact VerificationSpec/ProofContract source keys and CoverageBasis rules without calling the execution-side obligation generator.

It must detect omitted, duplicate, or extra obligations and verify evaluation-set equality.

For this `REVIEW_DECLARED` CoverageBasis, it also requires exactly one mandatory `COVERAGE_COMPLETENESS` review obligation.

## 6.7 `O-PERF` — benchmark oracle

Consumes raw request/transaction/projection/outbox/reconciliation/resource/provider-call measurements and computes P18 metrics independently from production dashboards.

Raw samples are retained as immutable evidence inputs. Dashboard screenshots alone are insufficient.

## 6.8 `O-PLATFORM` — qualified real-platform corroboration

For the full production profile, at least one governed staging/real integration path must corroborate simulator results against the actual provider classes used by launch configuration, including GitHub plus the selected execution/reasoning/CI surfaces.

A platform observation does not replace deterministic semantic proof; it detects adapter/environment mismatches.

---

# 7. Verifier qualification

Critical Claims use `QUALIFIED` assurance where a flawed verifier could falsely accept a trust failure.

Qualification is one-hop only.

## 7.1 Control Reference Model qualification

Seed a fixed mutation corpus against an intentionally defective SUT/reference adapter. Required mutants include at least:

```text
M01 dispatch before OPEN/outbox commit
M02 retry creates a second StageOccurrence
M03 second canonical writer bypasses control-mutation
M04 stale snapshot accepted after provider version change
M05 REQUIRED child barrier crossed without acceptance binding
M06 historical acceptance inferred from current boolean projection
M07 terminalization and successor collapsed into one cross-owner transition
M08 worker restart creates semantic retry
M09 P34/Gate PASS inferred from CI/ProofEvaluation
M10 Execution Cursor treated as Authority/scope truth
M11 unauthorized cross-Primary auto-dispatch despite rollout denial
M12 projection cache authorizes mutation after canonical change
M13 outbox loss after acknowledged schedule commit
M14 unsafe manual fallback duplicates active controlled work
M15 late conflicting terminal result rewrites history
```

Qualification threshold:

```text
critical seeded mutants detected: 100%
false ACCEPT/PASS on mutant corpus: 0
```

A new Critical semantic invariant added later must add at least one corresponding negative/mutation case before the reference verifier remains qualified.

## 7.2 Completeness Checker qualification

Seed obligation-set defects:

- omit one Claim obligation;
- omit the mandatory CoverageBasis completeness obligation;
- duplicate one obligation ID;
- inject one extra unknown obligation;
- change one semantic source key;
- evaluate a strict subset/superset of the bound obligation set.

Threshold:

```text
all seeded completeness defects rejected: 100%
```

## 7.3 Benchmark harness qualification

The benchmark harness must self-test:

- monotonic-clock use for duration metrics;
- percentile computation against fixed synthetic samples;
- LOCAL vs EXTERNAL vs SUBSTANTIVE latency separation;
- injected callback-loss accounting;
- provider-call counters;
- raw-sample/artifact digest stability.

A benchmark whose measurement pipeline cannot pass these self-tests cannot satisfy a P18 MEASURE obligation.

---

# 8. Golden semantic / fault corpus

The following scenario corpus is mandatory for D0. Each scenario records initial canonical state, external snapshots, trigger sequence, fault injection, expected canonical history, expected projection, expected dispatch/provider observations, and expected fail-closed outcome.

| ID | Scenario | Required oracle outcome |
|---|---|---|
| `G01` | clean one-lane schedule -> execute -> terminalize -> separately continue | CRM/SUT exact semantic equivalence |
| `G02` | two schedulers race same lane | exactly one canonical winner; loser creates no occurrence/outbox |
| `G03` | unrelated lanes mutate concurrently | no semantic cross-lane serialization/conflict |
| `G04` | duplicate outbox delivery | same occurrence; no semantic retry |
| `G05` | crash after OPEN+outbox commit before first dispatch | restart dispatches same committed occurrence |
| `G06` | callback lost after provider completion | polling/query reconciles same occurrence |
| `G07` | callback duplicate/reordered | callback payload never directly mutates canonical truth |
| `G08` | late conflicting terminal result | terminal history immutable; conflict rejected |
| `G09` | REQUIRED child incomplete | parent successor blocked |
| `G10` | REQUIRED child accepted | successor includes exact RequiredChildAcceptanceBinding |
| `G11` | multiple REQUIRED children | all must bind before successor |
| `G12` | NON_BLOCKING child still open | parent may continue if all other rules permit |
| `G13` | stale SourceSnapshot/current Authority changes before commit | mutation fails/recomputes; no stale-success |
| `G14` | external truth changes after historical commit | historical basis unchanged; current actionability recomputed |
| `G15` | worker crash/timeout | same occurrence reconciled; no replacement occurrence by age alone |
| `G16` | provider outage/rate limit | only dependent work degrades; independent lanes may continue |
| `G17` | `EXACT_CURSOR` | resume from accepted cursor |
| `G18` | `DESCENDANT_CURSOR` | preserve valid descendant work; no replay |
| `G19` | `ANCHOR_DESCENDANT_WITHOUT_CURSOR` | reconcile and establish cursor; no reset |
| `G20` | `DIVERGED` | fail closed; no force-reset/discard |
| `G21` | platform technically callable, Current rollout denies cross-Primary automation | no autonomous new occurrence/outbox; NextLegalAction exposed |
| `G22` | explicit test-policy fixture authorizes separate-occurrence cross-owner continuation | capability works without ownership transfer; test fixture is not Current Authority |
| `G23` | human escalation resolved by durable external decision ref | resolving occurrence consumes exact decision ref |
| `G24` | raw chat acknowledgement with no governed decision materialization | semantic approval rejected |
| `G25` | pause then unpause | no history rewrite; new admission stops/resumes after fresh recompute |
| `G26` | cache loss/corruption | rebuild from canonical truth; same projection |
| `G27` | canonical store unavailable | no new mutation/dispatch admission; conversation memory not used as store |
| `G28` | active controlled WorkScope while service unavailable | no silent independent manual duplicate execution |
| `G29` | identical operation request replay | exact prior result returned; no duplicate mutation |
| `G30` | same operation_request_id with conflicting fingerprint/body | fail closed |
| `G31` | unsupported semantic/platform version | fail closed; no reinterpretation |
| `G32` | webhook signature invalid/unverifiable | rejected before semantic reconciliation |
| `G33` | immutable exact ref remains old while current Authority changes | immutability not confused with current actionability |
| `G34` | remote provider call attempted while canonical tx open | instrumentation/test fails immediately |
| `G35` | Escalation terminalization companion transaction | atomicity matches accepted model; no half state |

D0 threshold:

```text
all mandatory golden scenarios: PASS
semantic mismatches vs O-CRM: 0
zero-tolerance invariant events: 0
```

---

# 9. Proof Contracts

## 9.1 CPV-C01 — Canonical Safety

**Statement:** Every accepted canonical transition preserves single-writer ownership, immutable history, lane-CAS concurrency, and required multi-record atomicity.

**Invariant:** R01-R05 all hold for every accepted transition.

**Oracle:** `O-CRM + O-STORE + O-AUTH`.

**Fixtures:** G01-G03, G09-G12, G29-G30, plus randomized concurrent lane traces.

**Probes:** property-based state-machine execution, same-lane race injection, unrelated-lane concurrency, transaction crash points, direct-storage audit.

**Metrics:** illegal accepted transition count; duplicate canonical head count; half-committed semantic transaction count; unrelated-lane conflict rate.

**Threshold:** illegal accepted transitions = 0; duplicate head = 0; half commit = 0; R0 unrelated-lane conflicts `< 0.1%`.

**Evidence:** `CPV-E-CANONICAL-CONFORMANCE`, `CPV-E-STORE-AUDIT`, raw trace corpus.

**Gate:** mandatory P34 input; Critical/QUALIFIED.

## 9.2 CPV-C02 — Dispatch / Idempotency Safety

**Statement:** No executor receives substantive work before durable scheduling, and transport/restart never invents semantic attempts.

**Invariant:** R06-R08/R10.

**Oracle:** `O-CRM + O-STORE + O-PROVIDER`.

**Fixtures:** G04-G08, G15, G29-G30.

**Probes:** crash at every boundary from validation through provider acknowledgement; duplicate/reordered delivery; idempotent replay; terminal/successor crash gap.

**Metrics:** dispatch-before-commit count; semantic occurrence amplification per committed occurrence; duplicate terminal revisions; successor-before-terminal count.

**Threshold:** all = 0; every transport retry maps to same occurrence identity.

**Evidence:** `CPV-E-DISPATCH-FAULT-MATRIX`.

**Gate:** mandatory P34 input; Critical/QUALIFIED.

## 9.3 CPV-C03 — Historical Child / External Truth

**Statement:** Historical transitions are pinned to exact facts while current scheduling uses freshly validated external truth.

**Invariant:** R09/R12-R14.

**Oracle:** `O-CRM + O-PROVIDER + O-AUTH`.

**Fixtures:** G09-G14/G33.

**Probes:** mutate provider version between projection and commit; alter current child acceptance after historical successor; ambiguous acceptance facts; missing exact ref.

**Metrics:** stale-success commits; historical replay mismatch; unbound REQUIRED successor; current-state inference used in historical replay.

**Threshold:** all = 0. Trust-sensitive mutable snapshots must be resolved/verified within P18 `<=10s` before commit or protected by a stronger provider conditional-version primitive.

**Evidence:** `CPV-E-TRUST-CURRENTNESS`, `CPV-E-HISTORICAL-REPLAY`.

**Gate:** mandatory P34 input; Critical/QUALIFIED.

## 9.4 CPV-C04 — Ownership / Gate / Rollout Integrity

**Statement:** Control orchestration never steals specialist/Gate ownership and never self-authorizes cross-Primary rollout.

**Invariant:** R15-R16.

**Oracle:** `O-AUTH + O-CRM + O-CONTRACT`.

**Fixtures:** G21/G22 plus CI-success and ProofEvaluation-ready negative cases.

**Probes:** capability=true with rollout=false; synthetic future-authorized test fixture; attempts to set Gate via API/worker; attempts for Primary A to execute Primary B semantics inside one occurrence.

**Metrics:** unauthorized auto-schedules; unofficial Gate decisions accepted; cross-owner same-occurrence substantive execution.

**Threshold:** all = 0 under Current Authority. G22 proves architecture capability only under an explicit non-Current test-policy fixture and may not be cited as Current rollout authorization.

**Evidence:** `CPV-E-OWNERSHIP-ROLLOUT`.

**Gate:** mandatory P34 input; Critical/QUALIFIED.

## 9.5 CPV-C05 — Resume / Sessionless Control

**Statement:** Durable state supports sessionless resume without promoting conversation IDs or Execution Cursor to semantic Authority.

**Invariant:** R17/R30.

**Oracle:** `O-AUTH + O-CRM + repository ancestry fixture oracle`.

**Fixtures:** G17-G20 plus a new-conversation/no-session-memory resume fixture.

**Probes:** restart ChatGPT/client identity; drop conversational handoff; resolve current WorkScope/control state from durable service; four P33 repository positions.

**Metrics:** manual ref-copy required on normal durable resume; replayed completed work; false divergence; conversation/session ID required for canonical reconstruction.

**Threshold:** normal durable resume reconstructs control state with zero required conversation/session identifiers; all four P33 states match Execution Surface v0.2; no valid descendant work replayed.

**Evidence:** `CPV-E-RESUME-CORPUS`, platform corroboration where available.

**Gate:** mandatory for full persistent profile; Critical/CHALLENGED.

## 9.6 CPV-C06 — Human Decision Integrity

**Statement:** A required human decision becomes semantic input only through a governed durable exact decision ref.

**Invariant:** R18.

**Oracle:** `O-AUTH + O-PROVIDER`.

**Fixtures:** G23-G24.

**Probes:** materialize decision provider artifact; replay exact ref; send chat/UI acknowledgement without artifact; alter mutable decision draft after evaluation.

**Metric:** unmaterialized acknowledgements accepted as semantic decision.

**Threshold:** 0.

**Evidence:** `CPV-E-HUMAN-DECISION`.

**Gate:** mandatory when HUMAN_DECISION path is implemented; Critical/CHALLENGED.

## 9.7 CPV-C07 — API / Capability / Credential Boundary

**Statement:** Platform APIs and identities preserve least authority and cannot bypass canonical semantics.

**Invariant:** R19-R20.

**Oracle:** `O-CONTRACT + credential capability matrix`.

**Fixtures:** forbidden endpoint/capability corpus; worker/service identity fixtures; unsupported-version fixture G31; invalid signature G32.

**Probes:** negative API calls, authz denial, direct DB credential absence, secret scan over canonical records/digests/log samples, idempotency-header mismatch.

**Metrics:** forbidden mutation accepted; worker canonical append possible; secret/capability token found in semantic payload/digest or prohibited log field; unsupported version interpreted.

**Threshold:** all = 0.

**Evidence:** `CPV-E-API-CONTRACT`, `CPV-E-CAPABILITY-SECURITY`.

**Gate:** mandatory P34 input; Critical/QUALIFIED.

## 9.8 CPV-C08 — Derived / Operational State Separation

**Statement:** Projection/cache/pause/backpressure/lease/retry metadata affects derived view or timing only and cannot become semantic truth.

**Invariant:** R11/R21.

**Oracle:** `O-CRM + O-STORE`.

**Fixtures:** G25-G26 plus stale projection and lease-expiry cases.

**Probes:** delete cache, corrupt cache, pause/unpause, expire delivery lease, reorder retry timers, mutate canonical history and present stale projection.

**Metrics:** canonical history changes caused solely by cache/lease/pause; stale projection authorized mutation.

**Threshold:** 0.

**Evidence:** `CPV-E-DERIVED-STATE`.

**Gate:** mandatory P34 input; Critical/CHALLENGED.

## 9.9 CPV-C09 — Degraded Recovery / Durability

**Statement:** Supported failures preserve acknowledged canonical history and never replace controlled work with unsafe duplicate execution.

**Invariant:** R22-R23/R27.

**Oracle:** `O-STORE + O-CRM + O-PROVIDER`.

**Fixtures:** G05/G06/G15/G16/G27/G28 plus backup/restore and code rollback fixtures.

**Probes:** kill API/worker/process at every durable boundary; store unavailable; restore backup/WAL-equivalent; rollback application build; provider timeout beyond warning/critical liveness thresholds.

**Metrics:** acknowledged commit loss; fabricated history; semantic retry caused by restart/age; unsafe manual duplicate; restore digest mismatch; recovery timing.

**Threshold:** zero semantic failures; supported primary-fault-model acknowledged commit RPO = 0; process replacement recovery starts `<=30s`, durable outbox recovery `<=60s`, 95% recoverable pending items reconciled `<=5min`, application rollback/restart target `<=10min` where the test environment represents the supported deployment profile. Regional/disaster restoration target `<=60min` is release/deployment evidence, not a local unit-test claim.

**Evidence:** `CPV-E-RECOVERY-FAULT-MATRIX`, `CPV-E-BACKUP-RESTORE`.

**Gate:** mandatory for the claimed deployment profile; Critical/QUALIFIED.

## 9.10 CPV-C10 — D0 Semantic Conformance

**Statement:** The deterministic local profile proves all semantic invariants before provider-scale benchmarking.

**Invariant:** R24.

**Oracle:** all deterministic oracles except real-platform corroboration.

**Fixtures:** G01-G35 + seeded property traces + mutation corpus.

**Probe:** CI/local deterministic suite at the exact implementation revision.

**Metric:** mandatory scenario pass count; semantic differential mismatches; qualified-mutant detection.

**Threshold:** 100% mandatory scenarios pass; 0 semantic mismatches; 100% required critical mutants detected.

**Evidence:** `CPV-E-D0-CONFORMANCE` with exact source/result revision, commands, fixture digests, seed list, tool versions, environment fingerprint.

**Gate:** mandatory before any R0 result is considered credible; Critical/QUALIFIED.

## 9.11 CPV-C11 — R0 Engineering Budget

**Statement:** The first production-shaped deployment meets the P18 R0 budgets without weakening semantics.

**Invariant:** R25.

**Oracle:** `O-PERF + O-STORE + zero-tolerance semantic counters`.

**Fixture:** P18 R0 workload and data shape.

**Benchmark protocol:**

1. load the declared retained history/data shape;
2. 10-minute warm-up;
3. 30-minute R0 steady-state measurement;
4. execute the defined 60-second API burst and 30-second mutation burst;
5. run callback-loss and snapshot-freshness subtests;
6. retain raw samples, not only aggregates.

**Mandatory thresholds inherited from P18 include:**

- simple query p95 `<=150ms`, p99 `<=500ms`;
- cached projection p95 `<=200ms`, p99 `<=600ms`;
- uncached p95-scope projection p95 `<=500ms`, p99 `<=1.5s`;
- local mutation after snapshots p95 `<=250ms`, p99 `<=1.0s`;
- idempotent replay lookup p95 `<=150ms`, p99 `<=500ms`;
- canonical transaction p95 `<=50ms`, p99 `<=200ms`;
- full p95-scope projection rebuild p95 `<=500ms`, p99 `<=1.5s`;
- 2,000-revision stress projection rebuild `<=5s`;
- cache hit ratio after warm-up `>=80%` when cache is part of the claimed profile;
- commit -> first healthy-provider request p95 `<=3s`, p99 `<=15s`;
- unrelated-lane transaction conflicts `<0.1%`;
- all canonical CAS/conflict responses `<5%` sustained over five minutes outside deliberate race fixtures;
- healthy steady-state oldest ready outbox p95 `<10s`, pending ready outbox `<1,000`;
- callback received -> reconciliation p95 `<=5s`, p99 `<=30s`;
- missed callback recovery: 99% `<=5min`, 99.9% `<=15min`;
- trust-sensitive mutable snapshot `<=10s` before commit or equivalent stronger conditional-version check;
- provider-read amplification median `<=3`, p95 `<=8` per clean transition;
- orchestration-overhead cost target `<=10%` of substantive provider cost under the declared cost model;
- zero-tolerance semantic counters remain zero.

Provider wait time must be reported separately from Aegis-local latency.

**Evidence:** `CPV-E-R0-PERFORMANCE`, raw benchmark samples, resource profile, exact implementation/config refs.

**Gate:** required for full production-shaped profile; Critical/CHALLENGED.

## 9.12 CPV-C12 — S0 Stress / Backpressure Safety

**Statement:** 4x R0 offered load for 15 minutes causes deterministic backpressure rather than semantic corruption.

**Invariant:** R26.

**Oracle:** `O-PERF + O-CRM + O-STORE`.

**Fixture:** exact P18 S0 profile.

**Probe:** 4x R0 for 15 minutes followed by return to R0 and observation until backlog returns to healthy steady-state behavior.

**Metrics:** zero-tolerance semantic counters; acknowledged commit loss; duplicate occurrence creation; dispatch-before-commit; new-admission state; backlog age/count; cross-lane conflict; post-stress recovery.

**Threshold:** zero semantic invariant violations and zero acknowledged commit loss. Latency may degrade. Backpressure must defer new autonomous admission before sacrificing already committed work, and the backlog must demonstrably recover after offered load returns to R0. P20 introduces no extra numeric backlog-recovery SLA beyond P18.

**Evidence:** `CPV-E-S0-STRESS`.

**Gate:** required for full production-shaped profile; Critical/QUALIFIED.

## 9.13 CPV-C13 — Retention / Replay / Audit

**Statement:** Retention/archival policies never destroy canonical replay or semantic idempotency history.

**Invariant:** R28.

**Oracle:** `O-STORE + exact digest/revision-order checker`.

**Fixtures:** hot history, cold-tier archived history, retained idempotency records, compacted operational delivery metadata.

**Probes:** archive then replay historical WorkScopes; rebuild projections; resolve exact record bytes/digests; replay old operation_request_id; verify canonical data remains distinct from telemetry compaction.

**Metrics:** unrecoverable canonical record count; digest mismatch; revision-order mismatch; replay result drift.

**Threshold:** all = 0. No automatic deletion of canonical StageOccurrence/package/Escalation/semantic-idempotency history in v0.2.

**Evidence:** `CPV-E-RETENTION-REPLAY`.

**Gate:** mandatory for any deployment claiming archival/compaction; Critical/CHALLENGED.

## 9.14 CPV-C14 — Observability / Cost Attribution

**Statement:** Operators can diagnose performance/control failures and distinguish Aegis-local work from provider/substantive cost without using telemetry as semantic truth.

**Invariant:** R29.

**Oracle:** metric-schema checker + `O-PERF` raw-sample reconciliation.

**Fixtures:** normal R0, callback loss, store conflict, provider outage, stale snapshot, backpressure, recovery.

**Probes:** ensure required metric families exist and correlate by WorkScope/lane/occurrence/request/dispatch identifiers; independently recompute selected dashboard aggregates from raw samples.

**Metrics:** missing required metric family; uncorrelatable critical event; dashboard/raw mismatch; provider/local latency misclassification; cost-unit attribution mismatch.

**Threshold:** no missing metric required to evaluate a mandatory P18 SLO; selected aggregate recomputation matches raw evidence within measurement precision; zero-tolerance invariant alerts are present and trigger on seeded mutants.

**Evidence:** `CPV-E-OBSERVABILITY-COST`.

**Gate:** CHALLENGED; mandatory for full production-shaped profile, but telemetry itself never proves semantic correctness without the underlying exact evidence.

---

# 10. Backpressure verification matrix

P20 verifies the behavior of P18 admission states rather than only checking queue depth.

Reference expectations:

```text
GREEN
  -> normal admission

YELLOW
  -> reduce speculative/new autonomous admission before committed work

ORANGE
  -> materially restrict new autonomous scheduling; preserve terminalization/recovery/reconciliation

RED
  -> stop new autonomous admission except explicitly reserved safety/recovery classes
     while continuing already-committed work as safely possible
```

Exact implementation watermarks must match the accepted P18 target values/configuration. Tests inject backlog/provider/store pressure across each threshold and assert:

1. transition is driven by operational measurements, not canonical history rewrite;
2. priority remains terminalization/recovery/already-committed work over new autonomous admission;
3. no committed outbox entry is dropped merely to improve metrics;
4. returning below the threshold requires fresh control recomputation before normal admission resumes.

---

# 11. Provider retry / liveness verification

The retry harness verifies at minimum the P18 short-window policy for idempotent provider reads/internal HTTP operations:

```text
exponential backoff + full jitter
base = 250ms
cap = 30s
max short-window attempts = 8
short-window duration target <= 2min
```

For non-idempotent provider actions, the harness must prove that retry is impossible without a provider-supported idempotency/correlation contract.

Occurrence age tests use the P18 warning/critical formulas and assert:

- warning triggers reconciliation/metric only;
- critical age triggers diagnostics/continued reconciliation only;
- neither threshold alone terminalizes the occurrence or creates a replacement semantic attempt.

---

# 12. Evidence Compiler / materialization contract

The Control Plane verification path must minimize manual evidence transport.

For every deterministic run, the collector should materialize when available:

```text
verification_spec exact ref/digest
obligation_set exact ref/digest + generator version
source revision / task anchor
result revision
reviewer-accessible materialized_ref
actual commands/probes
exit codes
fixture/corpus IDs + digests
seed list
raw test results/counts
raw benchmark samples + aggregate metrics
CI/run/job identity
artifact refs + digests
tool versions
environment fingerprint
provider simulator versions / platform provider identities
SourceSnapshotToken or exact provider-version observations used by the test
cost-unit inputs
```

Executor prose may add context but cannot override deterministic collector facts.

A local-only result or mutable artifact with no exact identity cannot satisfy a deterministic proof obligation that requires reviewer replay/resolution.

---

# 13. Evidence artifact set

A complete implementation review bundle is expected to contain exact durable refs for the applicable artifacts below.

| Evidence ID | Purpose |
|---|---|
| `CPV-E-SPEC` | exact P20 VerificationSpec/materialization identity |
| `CPV-E-OBLIGATIONS` | complete ProofObligation set identity/generator version |
| `CPV-E-COMPLETENESS` | independent obligation/CoverageBasis completeness checker result |
| `CPV-E-D0-CONFORMANCE` | deterministic golden/property/differential suite |
| `CPV-E-VERIFIER-QUALIFICATION` | mutation/defect corpus proving critical verifiers detect seeded defects |
| `CPV-E-CANONICAL-CONFORMANCE` | single-writer/CAS/atomicity evidence |
| `CPV-E-DISPATCH-FAULT-MATRIX` | commit/outbox/retry/crash/idempotency evidence |
| `CPV-E-TRUST-CURRENTNESS` | SourceSnapshot/currentness/stale-fail-closed evidence |
| `CPV-E-HISTORICAL-REPLAY` | immutable transition/Required-child replay evidence |
| `CPV-E-OWNERSHIP-ROLLOUT` | Primary/Gate/Current rollout authorization evidence |
| `CPV-E-RESUME-CORPUS` | sessionless/P33 four-state resume evidence |
| `CPV-E-HUMAN-DECISION` | durable human-decision ref evidence |
| `CPV-E-API-CONTRACT` | public/internal API negative/positive conformance |
| `CPV-E-CAPABILITY-SECURITY` | least-authority + secret-exclusion checks |
| `CPV-E-DERIVED-STATE` | projection/cache/pause/backpressure nonsemantic evidence |
| `CPV-E-RECOVERY-FAULT-MATRIX` | process/provider/store recovery behavior |
| `CPV-E-BACKUP-RESTORE` | durability/restore/integrity evidence |
| `CPV-E-R0-PERFORMANCE` | R0 raw/aggregate engineering evidence |
| `CPV-E-S0-STRESS` | S0 stress/backpressure/recovery evidence |
| `CPV-E-RETENTION-REPLAY` | canonical retention/archive replay evidence |
| `CPV-E-OBSERVABILITY-COST` | metrics/alerts/cost attribution evidence |
| `CPV-E-PLATFORM-CORROBORATION` | real/staging provider corroboration for claimed production adapters |
| `CPV-E-PROOF-EVALUATION` | immutable ProofEvaluation over exact EvidenceInputRefs |
| `CPV-E-REVIEW-BUNDLE` | reviewer navigation bundle for P34 |

All EvidenceArtifacts used by ProofEvaluation must be represented by exact `EvidenceInputRef` identities under the accepted Proof Plane model.

---

# 14. Obligation generation rules

The execution-side obligation generator must emit at least one obligation for every mandatory invariant/probe/threshold/evidence requirement in the active Claim's resolved ProofContract.

Stable source-key classes should include, as applicable:

```text
invariant:<claim-local-key>
oracle:<oracle-key>
fixture:<fixture-key>
probe:<probe-key>
metric:<metric-key>
pass-rule:<threshold-key>
evidence:<artifact-key>
challenge:<challenge-key>
qualification:<qualification-key>
provenance:<provenance-key>
```

Because CoverageBasis is `REVIEW_DECLARED`, the complete set MUST also contain exactly one:

```text
subject.kind = COVERAGE_BASIS
kind = COVERAGE_COMPLETENESS
source_key = coverage-completeness
evaluation_mode = REVIEW_REQUIRED
```

The obligation generator cannot omit review-required obligations to obtain a clean ProofEvaluation.

---

# 15. ProofEvaluation rules

ProofEvaluator consumes only exact:

```text
VerificationSpec identity
CoverageBasis identity
complete obligation-set identity
EvidenceInputRefs
Evaluator version
```

Required behavior:

- deterministic pass rule met with credible exact evidence -> `SATISFIED`;
- deterministic evidence missing/failed/invalid/unresolvable -> `UNSATISFIED`;
- semantic/reviewer-owned question -> `EXCEPTION`;
- any mandatory CoverageBasis completeness question remains `EXCEPTION` until CONTROL_REVIEW resolves it;
- ProofEvaluation never emits Gate PASS.

Aggregation remains:

```text
UNSATISFIED > EXCEPTION > SATISFIED
```

VerificationSummary may become `READY` only when no mandatory UNSATISFIED/EXCEPTION or Authority/input/environment blocker remains. `READY` means ready for independent P34 review, not Gate PASS.

---

# 16. P34 independent review contract

P34 must independently establish at least:

1. exact intended Current/accepted Authority and reviewed implementation result;
2. exact P20 VerificationSpec identity;
3. CoverageBasis integrity against the pinned P14-P18 source set;
4. independent obligation-set completeness through `O-COMPLETE` or another credibly independent checker;
5. ProofEvaluation set equality against the complete obligation set;
6. exact EvidenceInputRef provenance/integrity;
7. exact implementation result/materialized-ref Authority and scope conformance;
8. `UNSATISFIED == 0` for all mandatory obligations;
9. all mandatory `EXCEPTION`s resolved by the owning reviewer/decision authority;
10. required profile evidence (D0 only vs full R0 production-shaped claim) is actually present;
11. no seeded/observed zero-tolerance semantic incident is hidden by performance averages;
12. Current rollout authorization was not inferred from architecture capability tests.

Only `aegis-gate-review` may issue the official P34 verdict.

---

# 17. Profile-specific Gate expectations

P20 supports phased implementation without allowing a small local test to masquerade as full-product proof.

## 17.1 `CONTROL_D0_CONFORMANCE`

May be used for an internal implementation slice.

Requires:

- complete D0 semantic/fault corpus;
- verifier qualification;
- API/schema behavior applicable to the slice;
- exact durable evidence/materialization;
- independent completeness review.

It does **not** claim R0 production performance, real-provider qualification, availability, disaster recovery, or product launch readiness.

## 17.2 `CONTROL_R0_PRODUCTION_SHAPED`

Required before claiming the full persistent Control Plane production-shaped profile.

Adds:

- full R0 benchmark;
- S0 stress/backpressure;
- supported recovery/durability/backup tests;
- production adapter/platform corroboration;
- observability/cost evidence;
- deployment capability/security conformance.

## 17.3 Current-rollout restriction

Neither profile changes Current orchestration Authority.

While Current Skill Decomposition/Execution Surface policy prohibits zero-user-turn cross-Primary continuation, the production conformance obligation is:

```text
technical capability may exist
AND
Current rollout authorization = false
=> no autonomous cross-Primary scheduling/outbox
```

A future Authority supersession may activate a separate positive production-auto-dispatch obligation without changing the canonical ownership proof in this document.

---

# 18. Availability and post-launch evidence

P18 includes monthly availability targets such as `>=99.9%` for the Control API/write path under the declared provider-exclusion model.

P20 does not fabricate one month of production evidence before launch.

Therefore:

- prelaunch P34/P24 evidence proves controlled fault recovery, R0/S0 capacity, durability, observability, and the ability to measure the SLO;
- actual monthly availability attainment is post-launch operational Evidence;
- a release/review may not state that the monthly SLO has been historically achieved until the observation window exists;
- P24 may separately decide whether the prelaunch surrogate evidence is sufficient for release under the accepted risk profile.

This preserves the distinction between a launch target and achieved operational Evidence.

---

# 19. Performance measurement rules

To prevent benchmark gaming:

1. raw samples are immutable evidence inputs;
2. failed requests are not silently removed from error/correctness accounting;
3. deliberate expected same-lane CAS losers are reported separately from unrelated-lane contention;
4. provider wait time is separated from Aegis-local latency;
5. warm-up duration and measurement window are recorded;
6. workload generator version/config/seed is exact;
7. implementation/config/database topology is exact;
8. benchmark runs with semantic zero-tolerance violations are invalid regardless of latency percentiles;
9. retries are counted in provider/read amplification and cost metrics where applicable;
10. cache-hit metrics are reported only when the claimed deployment actually enables the cache.

---

# 20. Optimization evidence rule

Before adding broker/distributed cache/sharding/event-stream complexity, downstream engineering evidence must show:

```text
workload
metric
observed baseline
failed P18 target / measured bottleneck
resource profile
simpler mitigations attempted
candidate optimization
expected gain
rollback/reference path
```

P20 requires that the pre-optimization and post-optimization runs reuse the same exact VerificationSpec/workload identities unless a governed design change explicitly replaces them.

If an optimization cannot preserve an existing Critical Claim, it is architecture drift and must route back to the owning design layer rather than weakening the proof contract.

---

# 21. Failure classification guidance

Expected primary classifications:

| Observation | Primary classification |
|---|---|
| implementation violates accepted semantic/runtime/platform contract | `IMPLEMENTATION_DEFECT` |
| P20 proof contract itself cannot credibly establish an accepted requirement | `SPEC_DEFECT` |
| upstream Current/accepted Authorities conflict | `AUTHORITY_CONFLICT` |
| required upstream contract is absent | `MISSING_CONTRACT` |
| test/harness asserts the wrong accepted behavior | `TEST_DEFECT` |
| required exact artifact/result/provenance is missing or insufficient | `EVIDENCE_GAP` |
| provider/test environment cannot execute credible proof | `ENVIRONMENT_DEFECT` |
| external dependency prevents required proof | `DEPENDENCY_BLOCKER` |
| product/risk/semantic decision remains unresolved | `UNRESOLVED_DECISION` |

An implementation failure is not repaired by weakening the threshold. A test defect is not repaired by changing product semantics.

---

# 22. P20 acceptance checklist

P20 itself is complete when downstream implementation planning can answer, without inventing proof later:

- which exact Requirement universe is in scope;
- which Claims are Critical;
- which oracle proves each Claim;
- how the oracle is independent from the SUT;
- how Critical verifiers are qualified;
- which deterministic/fault corpus is mandatory;
- which R0/S0 metrics and thresholds apply;
- which exact evidence artifacts P32/P36 must return;
- how EvidenceInputRef provenance is pinned;
- how obligation completeness is checked independently;
- how P34 distinguishes `READY` proof from official `PASS`;
- how Current rollout denial is verified independently from target capability;
- which evidence is prelaunch versus post-launch operational evidence.

---

# 23. P20 invariants

1. This VerificationSpec consumes exact P14-P18 head `e657f0e74771184b98f8c8e6f8a8581e4858c82d`.
2. P21 review `5062769390` is the accepted architecture basis for P20.
3. CoverageBasis is `REVIEW_DECLARED`; independent coverage completeness is mandatory.
4. Every declared Requirement maps to at least one Claim.
5. Every Claim has an explicit proof contract in this document.
6. Critical Claims never rely solely on SUT-produced success output.
7. `O-CRM` is independent from production control-flow implementation.
8. critical verifier qualification uses a seeded mutation/defect corpus and requires 100% detection of the mandatory mutants.
9. obligation completeness is not self-certified by the execution generator.
10. exact EvidenceInputRef identity is required for deterministic proof.
11. ProofEvaluation is not Gate PASS.
12. P34 remains independently owned by `aegis-gate-review`.
13. Current rollout denial remains a required behavior until governed Authority changes.
14. D0 evidence cannot be represented as R0 production-shaped proof.
15. R0/S0 performance evidence is invalid if any zero-tolerance semantic invariant fails.
16. monthly availability is not claimed as achieved before the observation window exists.
17. user/manual prose cannot replace machine-available exact deterministic evidence.
18. no benchmark optimization may weaken exact refs/currentness/CAS/commit-before-dispatch/history/independent review.
19. failure classification routes to the earliest owning layer.
20. P20 does not begin implementation.

---

# 24. P20 disposition and handoff boundary

```text
P20 Verification Design
  -> READY / MATERIALIZED — Draft/Proposed
```

P20 does not self-accept as Current Authority.

The required next owning stage is:

```text
P21 Authority Review
owner: aegis-governance
subject: exact Control Plane P20 Verification Design candidate
```

That review must consume the exact materialized P20 head and determine whether the proof design is sufficiently complete, independent, risk-proportional, and consistent with the accepted Product/Model/Architecture and Proof Plane semantics.

Do not begin P30/P31/P32 from an unreviewed P20 candidate.
