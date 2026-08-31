# Aegis Control Plane Productization v0.2 — P18 Engineering / Optimization

Status: **Draft / Proposed Authority — P18 Engineering / Optimization**

Scope: `aegis/control-plane-productization/engineering`

Exact upstream basis:

- accepted P10-P13 modeling head: `f29c4da3698038e0174e4380707fa618b03c40b2`
- P21 Authority Review #3: `5062616510`
- modeling verdict: `PASS / ACCEPTED_FOR_DOWNSTREAM`
- P14 System Architecture materialized head: `54999ce91ff4f35455916c33b4f7891e2b6b8d4d`
- P15 Module Design materialized head: `12f75bc1938406d8d0cadca4d343fcdb95fdbfb9`
- P16 Runtime Data Flow materialized head: `56f7df8aab30a2720b9b180eea0237eae689f291`
- P17 Platform Contract materialized head: `e7acbe15ab34879e743ec88f7dfb38e5ce3a3931`

Retained Current boundaries:

- Project State / Gate Decision lineage remains externally owned;
- Aegis Skill Decomposition remains owner of Primary-owner composition rules;
- Execution Surface remains owner of `Task Anchor != Execution Cursor` and P32/P33 execution-position semantics;
- Proof Plane remains owner of verification/proof/evidence semantics;
- P34 remains the sole official Gate owner;
- Aegis Plugin / Control App / Control Service do not become lifecycle semantic owners merely because they coordinate transport.

P18 consumes the exact P14-P17 architecture and freezes engineering budgets, measurable acceptance targets, reference load, observability, degraded-mode behavior, and optimization triggers. It does not reopen product/model/platform semantics.

---

# 1. P18 objective

P18 answers:

> **How much load must the first production-shaped Control Plane support, what latency/freshness/recovery/cost budgets must it meet, how do we observe those budgets, and which implementation optimizations are justified before or after evidence says the simple reference path is insufficient?**

P18 intentionally separates:

```text
semantic correctness invariants
!=
engineering SLOs
!=
provider latency
!=
optimization choices
```

The optimization rule is:

> **Correctness boundaries are not performance knobs. Optimize by reducing redundant work, batching/coalescing, indexing, caching derived state, and controlling provider amplification — never by weakening exact refs, CAS, commit-before-dispatch, independent review, or immutable history.**

---

# 2. Evidence status and baseline discipline

P18 does not claim measured production performance because no P32 Control Plane implementation exists yet.

## 2.1 Observed product baseline

The accepted P02/P03 evidence established a qualitative baseline:

```text
current manual workflow
  -> user transports handoffs between ChatGPT / Codex / GitHub / review
  -> conversation history carries too much operational state
  -> callback/result/review continuation requires human turns
```

This is sufficient to justify the Control Plane product direction, but it is **not** a numeric service-performance benchmark.

## 2.2 Measured implementation baseline

At P18 materialization time:

```text
MEASURED_CONTROL_SERVICE_BASELINE = NOT_YET_AVAILABLE
```

Therefore every numeric value below is one of:

- **Reference workload** — the minimum workload a first production-shaped implementation must benchmark;
- **Launch target** — a proposed acceptance budget to be verified later;
- **Safety limit** — a fail-safe engineering boundary protecting semantic correctness;
- **Optimization trigger** — evidence threshold that justifies adding complexity.

None of these values may later be represented as achieved evidence until measured under P20-designed verification and P32/P34 execution/review.

## 2.3 Evidence before optimization

Before replacing the simple reference path with a more complex store/cache/broker/sharding design, engineering must record:

```text
workload
metric
observed baseline
failed target
resource bottleneck
candidate optimization
expected gain
rollback/reference path
```

A faster design that weakens P14-P17 invariants is not an optimization; it is architecture drift.

---

# 3. Optimization priority order

P18 freezes this engineering priority order:

```text
1. semantic correctness / fail-closed trust
2. no loss of acknowledged canonical history
3. deterministic recovery / idempotency
4. provider-call and human-turn minimization
5. control-loop latency
6. throughput / concurrency
7. infrastructure efficiency
8. implementation convenience
```

If a lower priority conflicts with a higher priority, the higher priority wins.

Examples:

- do not skip a fresh trust check to save provider latency;
- do not dispatch before commit to reduce perceived latency;
- do not add a second writer to raise throughput;
- do not delete canonical history to reduce storage cost;
- do not turn a duplicate dispatch into a new occurrence to avoid reconciliation complexity.

---

# 4. Reference workload profiles

P18 defines three workload profiles.

## 4.1 D0 — local development / deterministic conformance

Purpose: developer tests, local fake adapters, deterministic P20/P32 conformance work.

Reference envelope:

```text
active WorkScopes:                 100
simultaneous OPEN occurrences:      25
external jobs in flight:            10
Control API sustained RPS:          10
canonical mutations / second:        5
projection evaluations / second:    25
provider events / second:           25
```

D0 is not a production scalability claim.

## 4.2 R0 — first production-shaped reference deployment

R0 is the **launch benchmark profile** for one logical Control Service deployment before any global/multi-region scale claim.

Reference envelope:

```text
active WorkScopes:                    10,000
total retained WorkScopes:           100,000
simultaneous OPEN occurrences:         2,000
simultaneous external provider jobs:     500
interactive clients:                    100

Control API sustained RPS:               50
Control API 60-second burst RPS:         200
canonical mutation sustained / sec:       20
canonical mutation 30-second burst/sec:  100
projection evaluations sustained/sec:    200
projection evaluations burst/sec:        800
provider events sustained/sec:           100
provider events burst/sec:               500
outbox dispatch sustained/sec:             50
outbox dispatch burst/sec:                200
```

Expected data shape:

```text
p95 StageOccurrence revisions per WorkScope: 250
stress revisions per WorkScope:             2,000
p95 direct child WorkScopes per parent:         10
stress REQUIRED children on one parent:        100
canonical record revisions retained:       5,000,000+
```

R0 is intentionally much smaller than hyperscale workflow infrastructure and much larger than the current human-driven dogfood workflow. The product is provider-latency-dominated, not event-stream-throughput-dominated.

## 4.3 S0 — stress / backpressure profile

S0 is:

```text
4 x R0 offered load
for 15 minutes
```

S0 does **not** require launch-target latency to remain unchanged.

It requires:

- no semantic invariant violation;
- no acknowledged canonical commit loss;
- no dispatch-before-commit;
- no duplicate semantic occurrence from transport retry;
- deterministic admission/backpressure before store/provider collapse;
- recoverable backlog after offered load returns to R0;
- no cross-lane serialization caused solely by unrelated WorkScopes.

---

# 5. Latency accounting model

P18 separates three latency classes.

## 5.1 `LOCAL_CONTROL_LATENCY`

Time owned by Aegis after required external snapshots/results are already available:

```text
API parsing
canonical read
projection compute/cache
policy
scheduler derivation
mutation validation
store transaction
outbox claim bookkeeping
```

## 5.2 `EXTERNAL_RESOLUTION_LATENCY`

Time spent waiting on:

- Project State/GitHub reads;
- Proof Plane reads;
- Codex/execution reads;
- CI reads;
- human decision provider reads;
- other governed providers.

This latency is measured by Aegis but cannot be represented as solely Aegis-owned availability.

## 5.3 `SUBSTANTIVE_EXECUTION_LATENCY`

Time spent in the owning substantive stage, including reasoning, code execution, CI, proof, or review.

P18 does not impose one global duration target on substantive work.

Core measurement rule:

> End-to-end control-loop latency must report all three classes separately so provider slowness does not hide Control Plane regressions and Control Plane slowness does not get excused as provider latency.

---

# 6. Control API latency targets

Under R0, with Canonical Control Store healthy and excluding external-provider wait time:

| Operation class | p50 | p95 | p99 |
|---|---:|---:|---:|
| simple canonical/query read | <= 50 ms | <= 150 ms | <= 500 ms |
| cached control projection query | <= 75 ms | <= 200 ms | <= 600 ms |
| uncached projection at p95 scope size | <= 150 ms | <= 500 ms | <= 1.5 s |
| local mutation after trust snapshots available | <= 100 ms | <= 250 ms | <= 1.0 s |
| idempotent replay lookup | <= 50 ms | <= 150 ms | <= 500 ms |

For a trust-sensitive operation requiring multiple independent external reads:

- independent provider reads should execute concurrently when ownership/contracts permit;
- Aegis-added orchestration overhead after the slowest required provider response should target `<= 500 ms p95`;
- no fixed end-to-end PASS target is claimed for a provider-bound operation whose external provider itself violates its own latency budget.

A latency target never authorizes using stale data.

---

# 7. Canonical store transaction targets

Under R0:

```text
canonical transaction p95: <= 50 ms
canonical transaction p99: <= 200 ms
```

Measured from transaction begin to durable commit acknowledgement, excluding external reads performed before the transaction.

Required transaction classes include:

- OPEN occurrence + lane head + idempotency + outbox;
- child WorkScope/lane/binding + first OPEN occurrence + outbox;
- REQUIRED-child acceptance bindings + parent successor + outbox;
- terminal occurrence revision;
- Escalation + terminal binding atomic unit.

## 7.1 Contention targets

At R0:

```text
unrelated-lane transaction conflicts: < 0.1%
all canonical CAS/conflict responses:  < 5% sustained over 5 minutes
```

Higher conflict on deliberate same-lane race tests is expected and is not a store defect if exactly one legal winner commits.

If unrelated-lane contention exceeds the target, optimize indexing/transaction scope before considering distributed locks or semantic partitioning.

## 7.2 Transaction time rule

No remote provider call may occur while a canonical store transaction is open.

This is both a correctness and performance invariant.

---

# 8. Projection engineering targets

Projection remains deterministic/read-only/disposable.

## 8.1 Rebuild target

For a WorkScope at the R0 p95 history shape:

```text
full projection rebuild p95 <= 500 ms
full projection rebuild p99 <= 1.5 s
```

For the stress history shape of 2,000 occurrence revisions:

```text
full projection rebuild target <= 5 s
```

without changing semantic output.

## 8.2 Complexity target

Common current-state projection should avoid scanning unrelated project history.

Expected cost should be bounded primarily by:

```text
current WorkScope history
+ direct/required child relationships needed by that projection
+ exact current external supports
```

not total global repository history.

## 8.3 Cache target

A production implementation may use a disposable projection cache.

Reference target:

```text
cache hit ratio on repeated interactive reads: >= 80%
```

after warm-up under R0.

Cache misses are correctness-safe and must rebuild from canonical truth.

Cache failure must degrade to recomputation, not blocked semantic history.

---

# 9. Outbox / dispatch targets

When a provider is healthy and capacity is available:

```text
canonical schedule commit -> outbox visible: atomic / same transaction
outbox visible -> worker claim:             p95 <= 1 s, p99 <= 5 s
worker claim -> first provider request:      p95 <= 2 s, p99 <= 10 s
commit -> first provider request:            p95 <= 3 s, p99 <= 15 s
```

These targets apply only after current policy/rollout Authority permits the dispatch.

## 9.1 Backlog targets

Healthy R0 steady state:

```text
oldest ready outbox age p95 < 10 s
pending ready outbox count < 1,000
```

Warning thresholds:

```text
oldest ready outbox > 30 s
or pending ready outbox > 1,000
```

Critical/backpressure thresholds:

```text
oldest ready outbox > 5 min
or pending ready outbox > 5,000
```

At critical threshold, new autonomous scheduling must be admission-deferred before canonical OPEN creation unless a reserved high-priority capacity class applies.

Already committed outbox work is never dropped to restore metrics.

---

# 10. Webhook / reconciliation SLO

Callbacks/webhooks are acceleration only.

For active OPEN occurrences under a queryable healthy provider:

```text
provider callback received -> reconciliation starts:
  p95 <= 5 s
  p99 <= 30 s

missed callback -> provider-query recovery:
  99% detected/reconciled within 5 min
  99.9% within 15 min
```

This is an Aegis reconciliation target, not a claim that the provider itself always exposes a result within those times.

A callback-loss test must be part of the reference benchmark.

---

# 11. SourceSnapshot freshness budgets

Freshness is defined by provider version/currentness contracts, not wall-clock age alone.

Time budgets below control cache/reverification behavior.

## 11.1 Mutable currentness sources

For trust-sensitive mutation using mutable currentness such as:

- Current Authority/Gate head;
- current repository/execution position;
- current provider capability/availability;
- current human-decision resolution state;

reference rule:

```text
snapshot successfully resolved/verified <= 10 s before commit
```

or the mutation must reverify the token/current version before commit.

If the provider supplies a stronger conditional-version primitive, that primitive may replace simple time freshness while preserving exact currentness.

## 11.2 Immutable exact refs

An exact immutable artifact/decision/result ref has no arbitrary TTL merely because time passed.

It may be cached as long as:

- immutability is guaranteed by the owning contract;
- identity still resolves;
- current actionability is not incorrectly inferred from historical immutability.

## 11.3 Capability discovery

Provider/platform capability state may be cached for:

```text
<= 60 s
```

for scheduling convenience.

Before a critical dispatch that depends on an optional capability, the adapter must still handle a stale capability observation safely.

## 11.4 Freshness failure

Freshness failure causes:

```text
EXTERNAL_SNAPSHOT_STALE
AMBIGUOUS_EXTERNAL_TRUTH
or owning fail-closed equivalent
```

not a stale-success mutation.

---

# 12. OPEN occurrence age / liveness policy

Occurrence age is diagnostic. It is never by itself proof of failure.

Each provider adapter should expose an operational expected-runtime class when available.

Reference stale thresholds:

```text
warning threshold
  = max(3 x provider expected p95 runtime, 15 min)

critical reconciliation threshold
  = max(10 x provider expected p95 runtime, 2 h)
```

If no provider runtime profile exists:

```text
warning: 15 min without accepted progress/result observation
critical: 2 h without accepted progress/result observation
```

At warning:

- trigger explicit reconciliation;
- record liveness metric;
- do not terminalize automatically.

At critical:

- alert operator/control diagnostics;
- continue fail-closed reconciliation;
- do not create a replacement semantic occurrence merely because time elapsed.

Only the owning execution/provider contract may establish that the work is unrecoverably failed or diverged.

---

# 13. Retry / backoff budgets

P18 distinguishes transport retry from semantic retry.

## 13.1 Short transient retry

For idempotent provider reads/internal HTTP operations:

```text
exponential backoff + full jitter
base: 250 ms
cap: 30 s
max short-window attempts: 8
short-window duration target: <= 2 min
```

Non-idempotent provider actions must not be blindly retried without provider idempotency/correlation semantics.

## 13.2 Dispatch retry

For the same committed occurrence:

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

Reference operational limit before mandatory alert/escalated diagnostics:

```text
12 transport attempts or 30 min unresolved delivery uncertainty
```

Reaching this limit does **not** allocate a new StageOccurrence.

It transitions the operational state into persistent `DELIVERY_UNCERTAIN` diagnostics/reconciliation.

## 13.3 Reconciliation cadence

For an OPEN occurrence requiring active reconciliation when callbacks are absent/uncertain:

```text
0-5 min:      every 30 s
5-30 min:     every 2 min
30 min-2 h:   every 5 min
>2 h:         every 15 min + operator alert
```

Recent verified callback/provider progress may suppress redundant polling.

Provider rate-limit signals may further increase cadence; they may never justify stale trust acceptance.

---

# 14. Worker concurrency budgets

R0 reference:

```text
maximum simultaneously in-flight external jobs: 500
```

The global number is additionally constrained by each adapter/provider capability.

Effective provider concurrency is:

```text
min(global operational budget,
    provider advertised/configured budget,
    current rate-limit-derived budget)
```

Worker threads/process count is implementation-specific; the semantic unit remains occurrence-scoped dispatch/reconciliation.

Increasing worker count must not increase canonical writers or bypass store CAS.

---

# 15. Admission and backpressure

Backpressure protects already-committed work and provider/store health before admitting new autonomous work.

## 15.1 Capacity watermarks

For each bounded resource (`OPEN`, provider in-flight, outbox backlog, DB pool, adapter rate limit):

```text
GREEN   < 70%
YELLOW  70-85%
ORANGE  85-95%
RED     >= 95%
```

## 15.2 Behavior by level

### GREEN

Normal operation.

### YELLOW

- coalesce duplicate projection refreshes;
- stop optional prefetch;
- slow low-priority background reconciliation where safe;
- preserve all semantic operations.

### ORANGE

- defer **new autonomous scheduling** targeting the saturated resource;
- prioritize terminalization/reconciliation of already OPEN work;
- prioritize draining already committed outbox;
- preserve a small configured reserve for human-decision resolution / critical recovery where safe;
- recompute before admission later; do not retain stale candidates as authorization.

### RED

- stop new autonomous occurrence admission for the saturated path;
- if no safe reserved capacity remains, also defer new user-requested occurrence creation rather than overcommit;
- continue read/query where possible;
- continue recovery/terminalization paths that do not require new saturated-provider work;
- page/alert operations.

Backpressure state is operational only. It does not write a fake semantic blocker into StageOccurrence history.

## 15.3 Drain priority

Operational queue priority is:

```text
1. accepted terminalization / exact human-decision resolution
2. reconciliation of already OPEN work
3. dispatch of already committed outbox work
4. explicit user-requested new scheduling
5. new autonomous scheduling
6. optional refresh/prefetch
```

This changes service work ordering only. It cannot reorder canonical predecessor/occurrence history.

---

# 16. Provider rate-limit adaptation

For any adapter:

```text
provider 429/rate-limit responses > 5% over 5 min
```

triggers provider-specific concurrency reduction.

Reference behavior:

- halve new dispatch concurrency on each sustained threshold breach until stable;
- honor explicit provider retry-after semantics where safe;
- recover concurrency gradually, not instantly;
- cap polling before reducing substantive execution quality;
- never convert provider unavailability into implementation or Gate failure.

Repeated provider rate limiting contributes to operational `BLOCKED_ENVIRONMENT`/degraded diagnostics when user intervention or capacity change becomes necessary, using existing status semantics only.

---

# 17. Provider-cost model

Vendor pricing and model token pricing may change. P18 therefore freezes **cost units and amplification targets**, not fixed currency prices.

## 17.1 Cost units

```text
PIU = Provider Invocation Unit
      one substantive reasoning/execution/review invocation

PRU = Provider Read Unit
      one provider state/query/reconciliation read

PAU = Provider Artifact Unit
      one artifact upload/download/materialization operation
```

Required verification/review work is semantic product work, not orchestration overhead merely because it consumes PIUs.

## 17.2 Clean-path amplification targets

For one substantive StageOccurrence:

```text
orchestration-created extra substantive PIUs due solely to transport retry: 0 target
provider state reads per transition:
  median <= 3 PRU
  p95    <= 8 PRU
```

The Control Plane must not use an LLM/provider invocation merely to:

- poll an outbox;
- resolve a CAS conflict;
- compute deterministic projection;
- validate webhook signature;
- refresh a deterministic cache;
- sleep/retry.

## 17.3 Cost-overhead target

Over a representative 7-day R0 workload:

```text
Control Plane orchestration overhead cost
(excluding required substantive implementation/proof/review)
<= 10% of substantive provider execution cost
```

This is a launch target to measure, not a current evidence claim.

If exceeded, optimize query coalescing, reconciliation cadence, payload materialization, and duplicate provider work before weakening proof/review behavior.

---

# 18. Payload / record size budgets

Control Plane canonical records carry refs/metadata, not large evidence blobs.

Reference engineering targets:

```text
StageOccurrence revision p99 JSON size: <= 128 KiB
Implementation Package p99 JSON size:   <= 256 KiB
Escalation p99 JSON size:                <= 64 KiB
cross-process JSON request target:       <= 512 KiB
reference supported request envelope:    <= 1 MiB
```

Large logs, CI archives, diffs, proof artifacts, screenshots, binaries, and repository payloads should remain externally materialized and referenced by exact `CanonicalRef`.

If valid semantics cannot fit the reference envelope, route the engineering constraint back to P17/P12 rather than silently truncating canonical data.

No canonical digest may be computed over a truncated representation.

---

# 19. Canonical storage / indexing requirements

The reference store must efficiently support at least these access paths:

```text
WorkScope -> lane
lane -> current head
occurrence ID -> revision lineage
WorkScope -> occurrences in lifecycle order
parent WorkScope -> direct children
child -> immutable parent binding
package ID -> revision lineage
WorkScope -> current package refs
Escalation ID -> immutable record / resolution lookup
operation_request_id -> idempotency result
outbox status + next_attempt_at -> ready dispatch batch
provider/occurrence correlation -> recovery lookup
```

Recommended physical indexes must preserve exact semantic keys; no mutable denormalized status becomes authoritative.

## 19.1 Canonical history retention

For v0.2:

> **No automatic deletion of canonical StageOccurrence/package/Escalation history or semantic idempotency history is permitted.**

Canonical history is retained for the controlled project/workspace lifetime.

Physical cold-tier archival is allowed only when exact bytes/digests/revision order remain retrievable and audit semantics remain unchanged.

## 19.2 Projection/cache retention

Projection cache is disposable.

Reference cache TTL:

```text
<= 5 min
```

plus explicit invalidation on relevant canonical mutation/external-truth change where feasible.

A longer cached object may remain stored physically, but mutation authorization must never rely on it without current validation.

## 19.3 Outbox/delivery metadata retention

- pending/unresolved outbox records: retain until reconciled/resolved;
- completed delivery metadata: keep at least 30 days hot;
- after 30 days it may be compacted into operational audit storage if occurrence identity, dispatch attempts, final delivery state, and timestamps remain reconstructable for diagnostics.

Compaction cannot delete the canonical occurrence or semantic scheduling history.

## 19.4 Observability retention

Reference defaults:

```text
high-cardinality traces:   14 days
structured operational logs: 30 days
high-resolution metrics:   90 days
aggregated SLO/cost metrics: >= 13 months
```

Security/compliance deployments may require longer retention, but longer telemetry retention does not make telemetry semantic history.

---

# 20. Reference implementation path

P18 chooses a **simple reference path first**.

Logical implementation profile:

```text
stateless `aegis-control-api` replicas
+ stateless `aegis-control-worker` replicas
+ one ACID relational-class Canonical Control Store
+ store-native transactional outbox
+ B-tree/equivalent indexes for canonical access paths
+ optional disposable in-process or external projection cache
+ no mandatory external message broker
+ provider adapters over P17 HTTPS/provider APIs
```

The specific database vendor remains an implementation selection, but it must provide P17's ACID/CAS/unique-constraint/outbox capability.

## 20.1 Why no mandatory broker in the reference path

P16/P17 already require a durable transactional outbox.

At R0, an extra broker adds:

- another replicated state system;
- another retry/deduplication surface;
- more operational failure modes;
- no semantic correctness benefit.

Therefore a broker is an optimization candidate, not a launch prerequisite.

## 20.2 Why no mandatory distributed cache

Projection is derived and the R0 rebuild target is modest.

Start with direct computation + simple disposable cache.

Add distributed caching only from measured load evidence.

## 20.3 Why no early store sharding

WorkScope/lane concurrency is already semantically partitionable, but sharding before evidence adds migration/routing complexity.

Start with one logical transactional store deployment capable of R0.

Scale replicas/compute before semantic partitioning.

---

# 21. Optimization triggers

Additional platform complexity requires a measured trigger.

## 21.1 External message broker trigger

Consider a broker only if, while the store itself remains healthy:

```text
oldest outbox age violates p99 target at R0/S0
or store-native claim work consumes > 20% of store capacity
or worker fan-out cannot meet dispatch throughput target
```

and simpler indexing/batching/worker scaling has already been measured insufficient.

The broker remains downstream of the canonical outbox; it never becomes the semantic commit boundary.

## 21.2 Distributed projection cache trigger

Consider distributed caching if:

```text
projection computation consumes > 20% of Control API CPU
or uncached p95 projection exceeds 500 ms at R0
or repeated cross-replica rebuilds cause measurable provider-read amplification
```

Cache still cannot authorize mutation.

## 21.3 Canonical-store partition/shard trigger

Consider partitioning/sharding only if at R0/S0 after indexing/query optimization:

```text
canonical tx p99 > 200 ms
or unrelated-lane contention > 0.1%
or storage/IO exceeds sustainable single-deployment capacity
```

Partition key should preserve WorkScope/lane locality where possible.

Cross-shard design may not weaken atomic REQUIRED-child or scheduling transactions; if it cannot preserve them, route back to architecture rather than ship an approximation.

## 21.4 Event-stream/materialized-view trigger

Consider additional derived event streams/materialized views only if audit/query workloads measurably interfere with canonical mutation SLOs.

Derived streams are never a replacement canonical history.

---

# 22. Failure isolation targets

The reference deployment must preserve these failure domains.

## Control API loss

- external provider work may continue;
- no new canonical mutation while API/store boundary unavailable;
- recovery re-reads durable truth;
- no provider callback is trusted as substitute history.

## Worker loss

- Control API/query remains available;
- outbox accumulates durably;
- replacing worker resumes same occurrences.

## Projection cache loss

- query latency may rise;
- semantics remain available from canonical rebuild.

## One provider outage

- only work requiring that provider is operationally degraded;
- independent lanes/providers may continue if their own trust/policy permits;
- outage never becomes implementation or Gate failure.

## Canonical store loss/unavailability

- enter fail-closed no-new-mutation mode;
- suspend new dispatch claims that cannot be durably reconciled;
- already-running external work may continue externally but its return waits for reconciliation;
- never fall back to conversation memory as the store.

---

# 23. Availability / recovery objectives

These are platform-owned launch targets under the R0 reference environment, excluding declared external-provider outages.

```text
Control API monthly availability:        >= 99.9%
canonical store/service write path:       >= 99.9%
query/read path when store healthy:       >= 99.9%
```

Correctness invariants remain 100% requirements rather than error-budget SLOs.

Examples of zero-tolerance correctness events:

- dispatch before committed OPEN occurrence;
- two canonical writers;
- lost acknowledged canonical commit under supported local fault model;
- duplicate terminal revision;
- unauthorized generic PATCH write;
- current-truth decision from unverified stale snapshot;
- transport retry creating a new semantic occurrence.

## 23.1 Recovery targets

Single process/worker loss:

```text
replacement process starts recovery: <= 30 s target
durable outbox recovery resumes:      <= 60 s target
95% recoverable pending items reconciled: <= 5 min
```

Control Service deployment rollback/restart:

```text
RTO target <= 10 min
```

Regional/disaster recovery:

```text
service restoration target <= 60 min
```

If disaster recovery cannot prove that every previously acknowledged canonical commit survived, autonomous continuation remains blocked until the possible gap is explicitly reconciled. Recovery must never fabricate missing history.

---

# 24. Durability / backup target

Within the supported primary deployment fault domain:

```text
RPO for acknowledged canonical commits = 0
```

The store must not acknowledge semantic commit before the configured durable write guarantee is met.

Production deployment should provide:

- continuous transaction/WAL-equivalent recovery capability;
- periodic immutable backup/snapshot;
- tested restore procedure;
- integrity/digest verification after restore;
- external-ref reconciliation before autonomous continuation after catastrophic recovery.

Backup restoration never rewrites an old Gate/Evidence truth. It only restores the Control Plane records that referenced those external truths.

---

# 25. Degraded modes

P18 freezes explicit degraded modes so failure does not silently change semantics.

## 25.1 `CACHE_BYPASS`

Condition: projection cache unavailable/corrupt.

Behavior:

- discard/bypass cache;
- rebuild from canonical/external truth;
- continue if latency/capacity permits.

## 25.2 `WORKER_DEGRADED`

Condition: dispatch/reconciliation worker unavailable.

Behavior:

- API/query may continue;
- committed outbox remains durable;
- avoid unlimited new autonomous admission as backlog grows;
- resume same entries after worker recovery.

## 25.3 `PROVIDER_DEGRADED`

Condition: one external execution/truth provider unavailable/rate-limited.

Behavior:

- stop/defer new work requiring that provider when capacity/trust cannot be established;
- continue independent work only when semantics permit;
- reconcile OPEN work later;
- do not generate semantic retry.

## 25.4 `NO_AUTONOMY`

Condition: programmatic surface capability or current orchestration Authority unavailable/ambiguous.

Behavior:

- projection may derive NextLegalAction;
- no unauthorized autonomous occurrence/outbox is created;
- expose next legal user action through Plugin/App/manual workflow.

This mode is compatible with Current Skill Decomposition rollout restrictions.

## 25.5 `READ_ONLY_CONTROL`

Condition: canonical write path unavailable but safe reads remain possible.

Behavior:

- audit/query may continue with clear degraded indication;
- no new canonical mutation;
- no new scheduling commit;
- do not use UI/conversation memory to emulate writes.

## 25.6 `CONTROL_STORE_UNAVAILABLE`

Condition: canonical store/currentness cannot be trusted.

Behavior:

- fail closed;
- stop new control actions requiring mutation/current state;
- already-running providers may finish externally, but returned results remain pending reconciliation;
- service resumes only after canonical store integrity is restored.

---

# 26. Manual compatibility fallback rule

P17 permits an interactive compatibility profile, but P18 forbids unsafe failover of an already-controlled WorkScope.

A full-profile WorkScope with canonical OPEN/outbox/history must **not** silently switch to an independent conversational/manual execution path that creates duplicate substantive work.

Safe fallback is:

```text
control service unavailable
  -> show degraded status / exact known next action
  -> wait for canonical reconciliation
```

or a separately governed migration procedure that proves no active occurrence/outbox conflict.

Manual workflow may remain available for unrelated/new scopes that were never admitted into the persistent Control Plane, under existing Current Skill contracts.

---

# 27. Deployment / rollback strategy

Application rollback must preserve canonical data.

## 27.1 Code rollback

Target:

```text
rollback to prior known-good Control API/worker build <= 10 min
```

Rollback changes code, not previously committed canonical history.

## 27.2 Store migration rule

Use expand/migrate/contract style changes.

A release that changes physical storage should:

1. add backward-compatible structures;
2. deploy code that can operate during transition;
3. backfill/verify derived physical data;
4. cut over;
5. retain rollback compatibility for the declared rollback window;
6. remove old physical structures only in a later controlled change.

No destructive migration may be justified merely by deployment convenience.

A semantic schema change is not an ordinary physical migration and must route back through governed Authority.

## 27.3 Version skew

During rolling deployment, current and immediately previous implementation builds should be able to coexist for the same P17 platform contract where practical.

Workers with unsupported platform versions fail closed rather than reinterpret payloads.

---

# 28. Observability contract

Observability must make trust/control failures diagnosable without becoming semantic truth.

## 28.1 Required metrics

At minimum:

```text
control_api_requests_total
control_api_latency_seconds
control_mutations_total
control_mutation_latency_seconds
control_mutation_conflicts_total
idempotent_replays_total

projection_rebuild_total
projection_rebuild_latency_seconds
projection_cache_hit_ratio
projection_ambiguity_total

outbox_ready_count
outbox_oldest_ready_age_seconds
outbox_claim_latency_seconds
dispatch_attempts_total
delivery_uncertain_count

open_occurrence_count
open_occurrence_age_seconds
reconciliation_lag_seconds
reconciliation_attempts_total

provider_requests_total
provider_request_latency_seconds
provider_rate_limit_total
provider_errors_total
provider_inflight

snapshot_age_at_validation_seconds
snapshot_stale_rejections_total

required_child_barrier_rejections_total
repair_attempts_total
repair_budget_exhausted_total
open_escalations

unauthorized_auto_dispatch_prevented_total
backpressure_level
provider_cost_units_total
```

## 28.2 Required correlation keys

Traces/logs should correlate:

- WorkScopeRef;
- control lane;
- occurrence ID/revision;
- package ref;
- operation request ID;
- dispatch attempt ID;
- provider job/correlation ID where non-secret;
- recovery/reconciliation correlation ID.

## 28.3 Zero-tolerance invariant counters

The following must remain zero in a conforming run:

```text
dispatch_without_open_occurrence_total
canonical_write_bypass_total
duplicate_terminal_commit_total
semantic_retry_from_transport_total
stale_snapshot_accepted_total
unauthorized_gate_write_total
unauthorized_cross_primary_dispatch_total
```

Any nonzero value is a correctness incident, not merely an SLO miss.

---

# 29. Alerting targets

## Immediate page / critical

- canonical store integrity/digest failure;
- canonical write bypass detected;
- dispatch without committed occurrence;
- duplicate terminal commit attempt that appears accepted;
- possible acknowledged-commit loss;
- stale snapshot accepted rather than rejected;
- unauthorized cross-Primary dispatch;
- store unavailable for > 2 min while production traffic exists.

## Page / urgent

- oldest ready outbox > 5 min;
- reconciliation lag > 15 min for queryable active provider work;
- RED backpressure sustained > 5 min;
- provider delivery uncertainty exceeds 30 min/12 attempts;
- projection ambiguity count > 0;
- unrelated-lane conflict > 1% for 5 min.

## Warning / engineering action

- p95 Control API latency target missed for 30 min;
- projection cache hit ratio < 80% after warm-up;
- provider query amplification p95 > 8 PRU;
- orchestration overhead cost > 10% target over rolling 7 days;
- YELLOW/ORANGE backpressure sustained > 30 min.

---

# 30. Reference benchmark suite

P18 defines the benchmark/load scenarios P20 should turn into verification evidence.

## B18-01 — R0 mixed control traffic

Generate the R0 workload mix with:

- query;
- projection;
- schedule/terminal mutations;
- provider events;
- outbox dispatch;
- reconciliation.

Prove latency/throughput targets and zero correctness violations.

## B18-02 — same-lane scheduler race

Launch `100` competing schedule requests from one exact lane boundary.

Expected:

```text
exactly 1 canonical winner
99 conflict/idempotent losers as applicable
1 OPEN semantic occurrence
<= 1 semantic outbox entry
0 stale forced commits
```

## B18-03 — independent-lane concurrency

Drive mutations across many WorkScopes at R0/S0.

Expected unrelated-lane conflict remains under target.

## B18-04 — crash after schedule commit / before dispatch

Crash API/worker after OPEN+outbox commit but before provider request.

Expected:

- one occurrence;
- durable outbox;
- recovery dispatches same occurrence;
- no semantic retry.

## B18-05 — duplicate delivery storm

Deliver the same occurrence envelope at least `100` times through the adapter test harness.

Expected:

- one semantic occurrence;
- provider dedupe/query reconciliation prevents duplicate semantic attempts;
- no new StageOccurrence allocation.

Where a provider cannot guarantee one physical execution, the system must still preserve one semantic attempt and surface ambiguity rather than minting new history.

## B18-06 — callback loss

Drop at least `10%` of synthetic provider callbacks for active occurrences.

Expected provider-query reconciliation meets recovery SLO and no work is lost.

## B18-07 — provider outage / rate limiting

Simulate `30 min` provider outage plus rate limits.

Expected:

- no semantic failure fabrication;
- adaptive backoff/concurrency;
- bounded PRU amplification;
- backlog preserved;
- recovery after provider returns.

## B18-08 — P33 descendant resume

Exercise:

```text
EXACT_CURSOR
DESCENDANT_CURSOR
ANCHOR_DESCENDANT_WITHOUT_CURSOR
DIVERGED
```

under concurrent reconciliation.

Expected Current Execution Surface semantics remain unchanged.

## B18-09 — REQUIRED-child fan-out/join

Stress one parent with `100` REQUIRED child WorkScopes plus many ordinary parents.

Expected:

- parent does not cross before all required acceptance is valid;
- exact bindings are materialized atomically;
- no mutable barrier-consumed state;
- projection/join meets stress latency target.

## B18-10 — repair / reverify / rereview load

Run bounded multi-attempt repair lineages across concurrent scopes.

Expected:

- repair ordinals contiguous;
- budget enforced;
- fresh reverify/rereview occurrences;
- no old Gate/Evidence rewrite.

## B18-11 — store/cache/worker degraded modes

Independently fail:

- projection cache;
- worker;
- Control API replica;
- canonical write path;

Expected documented degraded mode with no semantic shortcut.

## B18-12 — software rollback

Deploy a candidate build, create canonical traffic, then rollback application build.

Expected:

- committed history preserved;
- previous compatible build can read/operate under declared platform version;
- no canonical DB restore needed for ordinary code rollback.

## B18-13 — S0 backpressure

Offer 4x R0 for 15 minutes.

Expected:

- watermarks engage;
- new autonomous admission defers before collapse;
- existing OPEN/outbox work is prioritized;
- backlog drains after return to R0;
- zero correctness incidents.

---

# 31. Engineering acceptance matrix

P18 launch acceptance should eventually require evidence for all rows.

| Area | Target |
|---|---|
| semantic correctness | all P14-P17 invariants preserved; zero-tolerance counters stay 0 |
| R0 throughput | all sustained/burst workload classes supported |
| API local latency | p95/p99 targets in §6 |
| canonical transaction | p95 <= 50 ms; p99 <= 200 ms |
| projection | p95 <= 500 ms at p95 history shape |
| outbox | commit->first request p95 <= 3 s, p99 <= 15 s healthy provider |
| callback recovery | 99% <= 5 min; 99.9% <= 15 min |
| snapshot freshness | trust-sensitive currentness verified <= 10 s before commit or equivalent stronger check |
| retry | bounded transport attempts; never semantic retry |
| provider amplification | median <= 3 PRU, p95 <= 8 PRU per transition |
| cost | orchestration overhead <= 10% substantive provider cost target |
| backpressure | S0 survives with deterministic admission/degradation |
| recovery | process/outbox recovery targets met |
| durability | acknowledged canonical commit RPO 0 in supported primary fault model |
| rollback | application rollback <= 10 min without canonical history rollback |
| observability | required metrics/correlation/alerts present |

P20 Verification Design must define the exact fixtures/oracles/evidence needed to prove these targets before implementation is accepted.

---

# 32. Allowed optimization techniques

P18 explicitly permits, when measured/needed:

- batching canonical reads that do not cross semantic transaction boundaries;
- parallel external reads from independent providers;
- coalescing duplicate projection refreshes;
- deterministic projection caching;
- store indexes/materialized **derived** lookup structures;
- outbox batch claiming;
- provider-specific concurrency control;
- callback-driven fast path plus polling recovery;
- jittered exponential backoff;
- cold archival of canonical bytes with exact retrieval preserved;
- horizontal stateless API/worker replicas;
- physical partitioning after trigger evidence;
- broker/cache introduction after trigger evidence.

---

# 33. Forbidden performance shortcuts

The following are forbidden even if they improve benchmarks:

- write canonical state from worker/adapter directly;
- dispatch before OPEN+outbox commit;
- make queue/broker acknowledgement the semantic commit;
- use last-write-wins instead of lane/record CAS;
- skip fresh validation because projection cache is warm;
- treat webhook payload as current semantic truth;
- treat CI green as Gate PASS;
- treat execution cursor as proof;
- reuse stale child acceptance projection without exact binding materialization;
- merge repair/reverify/rereview into one hidden retry;
- delete failed/blocked history for storage efficiency;
- truncate canonical JSON before digesting;
- inline massive evidence blobs to avoid exact-ref resolution;
- use conversation/session memory as a cache that can authorize mutation;
- auto-dispatch cross-Primary work merely because the provider/API is fast/available;
- reduce independent review/proof to meet cost targets.

---

# 34. Current rollout / cost behavior

Current Skill Decomposition / Execution Surface Authority may still prohibit cross-Primary automatic dispatch.

P18 performance/cost benchmarks must therefore distinguish:

```text
platform-capable synthetic dispatch benchmark
!=
currently authorized production autonomous routing
```

It is valid to benchmark the transport/control implementation with fake/sandbox providers while production rollout keeps cross-Primary auto-dispatch disabled.

No performance benchmark grants governance permission.

---

# 35. P18 invariants

A conforming engineering implementation preserves all of the following.

1. numeric targets are measured against a declared workload profile;
2. provider wait time and Aegis-local latency are reported separately;
3. correctness invariants are not traded for latency/throughput;
4. R0 is a reference deployment profile, not a global scale claim;
5. S0 may degrade latency but never semantic correctness;
6. canonical store transactions contain no remote provider calls;
7. unrelated lanes remain independently concurrent;
8. projection optimization never becomes semantic authority;
9. cache loss is recoverable from canonical truth;
10. outbox backlog never deletes committed work;
11. transport retry remains the same semantic occurrence;
12. provider cost controls do not weaken proof/review requirements;
13. LLM/provider calls are not used for deterministic housekeeping;
14. mutable currentness is freshly verified before trust-sensitive commit;
15. immutable exact refs are not reclassified as current merely because they remain resolvable;
16. occurrence age is diagnostic and never sole failure proof;
17. rate limits/outages map to operational/environment behavior, not implementation correctness;
18. backpressure defers new work before sacrificing already committed work;
19. backpressure state remains noncanonical;
20. canonical history/idempotency history is not automatically deleted in v0.2;
21. physical cold storage preserves exact canonical retrieval;
22. large evidence stays referenced rather than copied into Control Plane records;
23. simple transactional store + native outbox is the reference path;
24. broker/cache/sharding complexity requires measured trigger evidence;
25. canonical outbox remains semantic dispatch intent even if a broker is later introduced;
26. disaster recovery never fabricates missing history;
27. ordinary application rollback never rolls canonical data backward;
28. active full-profile WorkScopes do not silently fall back to duplicate manual execution;
29. observability can diagnose but cannot rewrite lifecycle truth;
30. zero-tolerance semantic incident counters remain zero;
31. P20 must verify the P18 budgets before downstream implementation acceptance;
32. Current orchestration Authority remains independent from platform capacity/performance;
33. no P18 decision requires redesigning P10-P17 semantics.

---

# 36. Architecture-family completion boundary

With P18 materialized, the Control Plane architecture family is complete as one Draft/Proposed candidate:

```text
P14 System Architecture
P15 Module Design
P16 Runtime Data Flow
P17 Platform Contract
P18 Engineering / Optimization
```

P18 does not self-accept this architecture as Current Authority.

Because P14-P18 collectively define a new production platform/control boundary, the architecture package requires governance review before downstream implementation relies on it as trusted Authority.

Expected next owning stage:

```text
P21 Authority Review
owner: aegis-governance
subject: exact P14-P18 architecture candidate
```

The review should consume the exact P18 materialized head and determine whether the complete architecture is `PASS / ACCEPTED_FOR_DOWNSTREAM` or route any defect to its earliest untrusted layer.

Only after trusted architecture acceptance should downstream verification/implementation planning treat these platform/engineering contracts as Current downstream basis.

Per composition rules, `aegis-architecture` stops here and does not directly invoke `aegis-governance`, `aegis-verification`, or implementation work.

---

# 37. P18 disposition

```text
P18 Engineering / Optimization
  -> READY / MATERIALIZED — Draft/Proposed
```

Authority chain:

```text
P10-P13 modeling
  @ f29c4da3698038e0174e4380707fa618b03c40b2
  -> P21 #3 PASS / ACCEPTED_FOR_DOWNSTREAM

P14 System Architecture
  @ 54999ce91ff4f35455916c33b4f7891e2b6b8d4d

P15 Module Design
  @ 12f75bc1938406d8d0cadca4d343fcdb95fdbfb9

P16 Runtime Data Flow
  @ 56f7df8aab30a2720b9b180eea0237eae689f291

P17 Platform Contract
  @ e7acbe15ab34879e743ec88f7dfb38e5ce3a3931

P18 Engineering / Optimization
  -> this artifact
```

Required next action after materialization:

```text
fresh P21 Authority Review against the exact PR #27 P18 head
```

Do not begin P20/P30/P31/P32 from an unreviewed P14-P18 Draft/Proposed architecture package.
