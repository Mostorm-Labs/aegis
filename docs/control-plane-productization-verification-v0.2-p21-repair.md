# Aegis Control Plane Productization v0.2 — P20 Verification Design P21 Repair

Status: **Draft / Proposed Authority — P20 Verification Design repair**

Scope: `aegis/control-plane-productization/verification`

This document is a **normative amendment** to:

- `docs/control-plane-productization-verification-v0.2.md`
- exact original P20 head `c54ed3a9b2058fc1549d855465b42e24b566996c`

It repairs only the blockers from P21 Authority Review #1:

- review `5062825477`
- verdict `BLOCKED_AUTHORITY`
- earliest untrusted layer `P20 Verification Design`

Exact trusted upstream basis remains unchanged:

- P14-P18 architecture head `e657f0e74771184b98f8c8e6f8a8581e4858c82d`
- Architecture P21 review `5062769390` — `PASS / ACCEPTED_FOR_DOWNSTREAM`
- Product head `c628bdc15fdd3d32511a04b6f09055413f2786c3`, review `5061188138`
- Modeling head `f29c4da3698038e0174e4380707fa618b03c40b2`, review `5062616510`

The original P20 document and this amendment are normative together for the repaired candidate. Where this amendment is more specific for B1/B2/B3, this amendment controls. All original P20 decisions not explicitly changed here remain unchanged.

---

# 1. Repair boundary

P21 #1 accepted the core P20 strategy and identified three local verification-spec defects:

1. `B1 SPEC_DEFECT` — accepted P17/P18 launch/trust contracts were missing or under-bound in the declared `REVIEW_DECLARED` Requirement universe;
2. `B2 SPEC_DEFECT` — the 7-day orchestration-cost and post-launch monthly-availability targets lacked complete measurement/evidence contracts;
3. `B3 SPEC_DEFECT` — verifier qualification did not challenge the P17 `SourceSnapshotToken` integrity/binding boundary.

This repair does **not**:

- reopen P02/P03 or P10-P18;
- change the accepted P17/P18 requirements;
- weaken any existing P20 threshold;
- change `CoverageBasis.mode = REVIEW_DECLARED`;
- replace `O-CRM` or `O-COMPLETE` independence;
- reduce the original G01-G35 corpus;
- remove any original M01-M15 critical mutant;
- authorize Current cross-Primary automatic continuation;
- begin P30/P31/P32.

---

# 2. Accepted P20 decisions inherited unchanged

The repaired candidate preserves the following P21-accepted P20 decisions:

1. `CoverageBasis.mode = REVIEW_DECLARED`.
2. Production SUT is never its own only correctness oracle.
3. `O-CRM` MUST NOT reuse production control-flow as reference truth.
4. `O-COMPLETE` MUST NOT use the execution-side obligation generator as its expected-truth source.
5. Critical verifier qualification uses seeded negative defects and zero false acceptance.
6. D0, R0, and S0 remain distinct proof profiles.
7. Semantic zero-tolerance failures invalidate performance evidence regardless of latency percentiles.
8. Current rollout denial remains a mandatory proof until separate governance changes it.
9. `Task Anchor != Execution Cursor` and all four P33 reconciliation states remain controlling.
10. Human semantic decisions require durable exact external decision refs.
11. ProofEvaluation, CI success, provider success, and dashboards are not P34 Gate PASS.
12. Monthly availability MUST NOT be represented as historically achieved before a real observation window exists.

---

# 3. CoverageBasis repair

## 3.1 Combined Requirement universe

The original P20 Requirement universe `CPV-R01` through `CPV-R30` remains unchanged.

This amendment adds `CPV-R31` through `CPV-R40`.

The repaired declared Requirement universe is therefore:

```text
CPV-R01 ... CPV-R40
```

P34 independent coverage review MUST evaluate the exact combined R01-R40 universe against the pinned P14-P18 source set. The execution-side obligation generator cannot self-certify that this combined set is complete.

## 3.2 Added Requirements

| Requirement ID | Required proposition |
|---|---|
| `CPV-R31` | Every `SourceSnapshotToken` used at a trust-sensitive boundary is integrity-protected and validated for token integrity, issuing adapter/source-kind compatibility, provider resource binding, and version/currentness binding before it can support mutation. Tampered or cross-boundary tokens fail closed. |
| `CPV-R32` | Every async provider claimed capable of autonomous trust-sensitive work exposes a durable query/correlation path sufficient to recover state after callback loss; callback-only providers cannot claim full autonomous capability. |
| `CPV-R33` | Dispatch transport retry for one committed occurrence follows the accepted P18 retry policy and reaches `DELIVERY_UNCERTAIN` diagnostics at the accepted `12 attempts or 30 min` boundary without allocating a new StageOccurrence. |
| `CPV-R34` | OPEN-occurrence reconciliation follows the accepted P18 age bands/cadence, and time/age alone never terminalizes or creates a replacement semantic occurrence. |
| `CPV-R35` | Provider rate-limit adaptation follows the accepted P18 contract: sustained `>5%` rate-limit responses over `5 min` reduce new provider dispatch concurrency, honor provider retry-after semantics where safe, recover gradually, and reduce polling before weakening substantive proof/review behavior. |
| `CPV-R36` | Canonical/platform payloads satisfy the accepted P18 record/request-size engineering budgets for the claimed profile, and canonical bytes/digests are never computed from a silently truncated representation; oversized semantic content routes to exact external artifacts or fails closed. |
| `CPV-R37` | Operational retention for delivery metadata and observability satisfies the accepted P18 windows for any deployment claiming those defaults, while canonical StageOccurrence/package/Escalation/semantic-idempotency history remains governed by the stronger no-auto-deletion rule. |
| `CPV-R38` | Production-shaped alerting implements and fires the accepted P18 critical/urgent/warning thresholds from exact telemetry without treating alerts as semantic lifecycle truth. |
| `CPV-R39` | Over an exact representative **7-day R0 logical workload**, Control Plane orchestration-overhead cost, excluding required substantive implementation/proof/review, is `<=10%` of substantive provider execution cost under the exact cost model bound to the evidence run. |
| `CPV-R40` | Post-launch Control API/write/query availability is measured over an exact complete monthly observation window against the P18 `>=99.9%` targets with explicit numerator, denominator, provider-exclusion rules, raw evidence identity, and immutable evaluation provenance. Prelaunch evidence may qualify the measurement path but cannot claim historical attainment. |

## 3.3 Profile applicability

| Requirement | D0 conformance | Full R0 production-shaped | Post-launch operational |
|---|---|---|---|
| R31 snapshot token integrity | required via fake/qualified adapters | required | continuously enforced |
| R32 async provider query/correlation | capability-contract simulation | required for every provider claimed autonomous | continuously enforced |
| R33 dispatch retry/delivery uncertainty | virtual-clock conformance | required | operationally observed |
| R34 reconciliation cadence | virtual-clock conformance | required | operationally observed |
| R35 rate-limit adaptation | deterministic provider simulation | required | operationally observed |
| R36 payload/no truncation | boundary/property tests | required | monitored |
| R37 operational retention | policy/config + virtual-time proof | required when defaults are claimed | actual retention observed/audited |
| R38 alerting | alert-rule qualification | required | continuously observed |
| R39 7-day cost | harness qualification only | required before claiming full R0 economics target | may be remeasured |
| R40 monthly availability | evaluator qualification only | measurement capability required prelaunch | actual completed-month evidence required to claim attainment |

Profile-conditional does not mean optional: if the deployment claims the corresponding capability/profile, its requirement becomes mandatory.

---

# 4. Claim-set repair

Original Claims `CPV-C01` through `CPV-C14` remain valid and unchanged except for the scope clarifications in §4.6.

This amendment adds five Claims.

| Claim | Requirements | Criticality | Minimum assurance | Base profile | Execution context |
|---|---|---|---|---|---|
| `CPV-C15 Snapshot / Async Provider Trust` | R31-R32 | CRITICAL | QUALIFIED | REFERENCE | PLATFORM |
| `CPV-C16 Delivery / Reconciliation Control` | R33-R35 | CRITICAL | QUALIFIED | PROPERTY | INTEGRATION |
| `CPV-C17 Exact Envelope Representation` | R36 | CRITICAL | QUALIFIED | PROPERTY | PLATFORM |
| `CPV-C18 Operational Retention / Alerting` | R37-R38 | ORDINARY | CHALLENGED | PROPERTY | PLATFORM |
| `CPV-C19 Long-window Cost / Availability` | R39-R40 | ORDINARY | CHALLENGED | MEASURE | PLATFORM |

The repaired Claim universe is therefore:

```text
CPV-C01 ... CPV-C19
```

## 4.6 Scope clarifications for existing Claims

- `CPV-C03 Historical Child / External Truth` still proves stale/currentness and historical exact-ref behavior; **C15** now owns physical `SourceSnapshotToken` integrity and cross-adapter/source/resource binding proof.
- `CPV-C09 Degraded Recovery / Durability` still proves recovery and timeout-not-semantic-retry; **C16** now owns the exact accepted retry/reconciliation/rate-limit control policy.
- `CPV-C11 R0 Engineering Budget` still owns the 30-minute R0 performance window and P18 latency/throughput targets; **C19** exclusively owns the separate 7-day cost target so the 30-minute benchmark cannot be misrepresented as 7-day evidence.
- `CPV-C13 Retention / Replay / Audit` still owns canonical semantic history/replay; **C18** owns operational hot/telemetry retention windows.
- `CPV-C14 Observability / Cost Attribution` still owns metric availability/correlation and cost attribution correctness; **C18** owns alert-threshold conformance and **C19** owns the long-window cost pass rule.

---

# 5. Oracle extensions

The original `O-AUTH`, `O-CRM`, `O-STORE`, `O-PROVIDER`, `O-CONTRACT`, `O-COMPLETE`, `O-PERF`, and `O-PLATFORM` remain.

This amendment tightens their contracts and adds two specialized test oracles.

## 5.1 `O-SNAPSHOT` — independent snapshot-token boundary oracle

Purpose: verify P17 snapshot-token integrity/binding without using production scheduler/mutation success as the oracle.

Inputs:

```text
raw compact token bytes
expected adapter/source-kind
expected provider resource identity
expected provider version/currentness fixture
issuer test key/capability identity or independent verification interface
```

Checks:

1. payload modification invalidates token integrity;
2. integrity tag modification invalidates the token;
3. a token issued for adapter/source-kind A cannot satisfy adapter/source-kind B;
4. a valid token for resource X cannot satisfy resource Y;
5. a valid historical token cannot be treated as current after the bound provider version changes when currentness is required;
6. token failure produces fail-closed reconciliation/currentness behavior and no canonical success mutation.

`O-SNAPSHOT` may share canonical encoding primitives but MUST NOT call the production scheduler/mutation acceptance path to determine expected validity.

## 5.2 `O-TIMEPOLICY` — virtual-clock operational-policy oracle

Purpose: deterministically verify retry, reconciliation, rate-limit adaptation, retention expiry, and alert timing without multi-hour/day wall-clock tests.

It provides:

- monotonic virtual time;
- exact scheduled-action trace;
- provider callback/query/rate-limit event injection;
- expected policy transition trace derived from the accepted P18 timings;
- no semantic write capability.

Virtual time is valid for timing-policy conformance. It is **not** valid evidence for historical monthly service availability.

---

# 6. Verifier qualification repair

Original mandatory mutants `M01` through `M15` remain mandatory.

The repaired mandatory qualification corpus adds:

```text
M16 SourceSnapshotToken payload is modified but SUT/verifier accepts the original integrity tag
M17 SourceSnapshotToken from wrong adapter/source-kind is accepted at a different trust boundary
M18 SourceSnapshotToken with mismatched provider resource/version binding is accepted as valid current support
M19 callback-only async provider is incorrectly advertised/accepted as full autonomous trust-sensitive capability
M20 canonical representation is silently truncated before digest/acceptance and verifier fails to detect the mismatch
```

Repaired qualification threshold:

```text
mandatory critical mutants M01-M20 detected: 100%
false ACCEPT/PASS on mandatory mutant corpus: 0
```

For M16-M18, evidence MUST show the exact mutated token bytes/binding tuple and the expected fail-closed result. A generic `invalid token` unit test with no exact mutant provenance is insufficient qualification evidence.

For M20, the verifier MUST compare full canonical source bytes/digest against any size-limited transport representation and reject silent truncation.

---

# 7. Golden semantic / fault corpus extension

Original G01-G35 remain unchanged and mandatory.

The repaired D0 corpus adds G36-G44.

| ID | Scenario | Required oracle outcome |
|---|---|---|
| `G36` | modify one byte/field in a valid SourceSnapshotToken payload without issuing a new integrity tag | `O-SNAPSHOT` rejects; no trust-sensitive mutation |
| `G37` | present a valid token issued for another adapter/source kind | adapter/source compatibility rejects; no canonical success |
| `G38` | present a valid token for the wrong provider resource/version/currentness binding | exact binding/currentness rejects or re-resolves; no stale/cross-resource success |
| `G39` | provider offers callback delivery but no durable query/correlation path while claiming autonomous capability | full autonomous trust-sensitive capability rejected/degraded; no silent callback-only trust claim |
| `G40` | repeatedly fail delivery of one committed occurrence across virtual time | retry schedule follows P18; at `12 attempts or 30 min` delivery uncertainty becomes durable operational diagnostics; semantic occurrence count remains one |
| `G41` | lose callbacks for an OPEN occurrence across all P18 age bands | reconciliation queries follow accepted `30s / 2min / 5min / 15min` bands subject to safe rate-limit adaptation; age alone never terminalizes/retries semantically |
| `G42` | inject provider 429/rate-limit responses above and below the `>5% over 5 min` threshold | sustained breach reduces new dispatch concurrency, honors safe retry-after, avoids instant full recovery, and does not weaken substantive proof/review |
| `G43` | exercise canonical records/envelopes just below/at/above P18 size targets and attempt silent truncation before digest | representative profile meets targets; oversize content externalizes/fails closed; full canonical digest never uses truncated bytes |
| `G44` | virtual-time operational-retention and alert-threshold boundary sweep | configured retention/alert behavior matches P18; expiry affects only permitted operational/telemetry data; alerts fire at exact governed thresholds without semantic mutation |

Repaired D0 threshold:

```text
G01-G44 mandatory scenarios: PASS
semantic mismatches vs independent oracle stack: 0
zero-tolerance invariant events: 0
M01-M20 qualification detection: 100%
false ACCEPT/PASS on mandatory mutants: 0
```

G45/G46 are intentionally not added as fake D0 substitutes for long-window evidence; C19 defines those separately.

---

# 8. Added Proof Contracts

## 8.1 CPV-C15 — Snapshot / Async Provider Trust

**Statement:** Trust-sensitive external observations are accepted only through integrity-protected, correctly bound snapshot tokens/exact refs, and an async provider may claim autonomous trust-sensitive capability only when callback loss is recoverable through durable query/correlation.

**Invariant:** R31-R32.

**Oracle:** `O-SNAPSHOT + O-CONTRACT + O-PROVIDER + O-AUTH`.

**Fixtures:** G36-G39 plus valid-control tokens/providers.

**Probes:** token byte/payload mutation; wrong adapter/source/resource/version replay; callback drop with/without query capability; capability-descriptor conformance.

**Metrics:** tampered tokens accepted; cross-adapter/source tokens accepted; cross-resource/version tokens accepted; callback-only provider falsely classified autonomous; unrecoverable callback-loss states falsely treated as controllable.

**Threshold:** all = 0. Every provider claimed full autonomous for trust-sensitive work MUST expose durable query/correlation recovery.

**Evidence:** `CPV-E-SNAPSHOT-INTEGRITY`, `CPV-E-ASYNC-PROVIDER-CAPABILITY`.

**Gate:** mandatory P34 input for full persistent/autonomous-capable profile; Critical/QUALIFIED.

## 8.2 CPV-C16 — Delivery / Reconciliation Control

**Statement:** Transport uncertainty, occurrence liveness, and provider rate limits are handled by the exact accepted P18 operational policy without inventing semantic retries/failures.

**Invariant:** R33-R35.

**Oracle:** `O-TIMEPOLICY + O-CRM + O-PROVIDER + O-STORE`.

**Fixtures:** G40-G42 plus original G04-G07/G15-G16.

**Probes:** virtual-clock delivery failure; callback loss; provider completion before callback; sustained/borderline 429 windows; retry-after; provider recovery.

**Mandatory dispatch retry expectation:**

```text
1s, 2s, 4s, 8s, 16s, 30s, 60s, then cadence <= 5min
```

At:

```text
12 transport attempts OR 30min unresolved delivery uncertainty
```

expected behavior is persistent `DELIVERY_UNCERTAIN` diagnostics/reconciliation, not a new StageOccurrence.

**Mandatory reconciliation cadence:**

```text
0-5min:    every 30s
5-30min:   every 2min
30min-2h:  every 5min
>2h:       every 15min + operator alert
```

Safe callback progress/rate-limit signals may suppress or lengthen redundant polling as allowed by P18, but may never justify stale trust acceptance.

**Rate-limit threshold:** sustained provider rate-limit responses `>5% over 5min` MUST reduce new dispatch concurrency from the previous permitted level, including the P18 reference halving behavior, honor safe provider retry-after, and recover progressively rather than instantaneously to full capacity. Exact recovery-step configuration is implementation materialization evidence; it may not violate the P18 qualitative gradual-recovery rule.

**Metrics:** retry-schedule mismatch; replacement semantic occurrences; missing delivery-uncertain transition; reconciliation-cadence mismatch; age-only terminalization; sustained-rate-limit breach with no concurrency reduction; proof/review work weakened to save provider cost.

**Threshold:** all semantic violations = 0; timing-policy trace conforms to accepted P18 bands/configuration.

**Evidence:** `CPV-E-DELIVERY-POLICY`, `CPV-E-RECONCILIATION-POLICY`, `CPV-E-RATE-LIMIT-CONTROL`.

**Gate:** mandatory P34 input for worker/provider execution profile; Critical/QUALIFIED.

## 8.3 CPV-C17 — Exact Envelope Representation

**Statement:** P18 payload/record budgets are met for the claimed profile without truncating or altering canonical semantic identity.

**Invariant:** R36.

**Oracle:** `O-CONTRACT + canonical-byte/digest checker + O-STORE`.

**Fixtures:** G43 with generated boundary payloads and exact external-artifact alternatives.

**Probes:** generate StageOccurrence revisions around `128 KiB`, implementation packages around `256 KiB`, Escalations around `64 KiB`, cross-process requests around `512 KiB`, and supported reference request envelopes around `1 MiB`; attempt truncation before digest and attempt large evidence/log inline embedding.

**Metrics:** p99 representative size per record class; silently truncated accepted representations; digest mismatch between stored/full canonical bytes and transport bytes; large artifact inlining where exact external ref was required.

**Threshold:**

```text
StageOccurrence revision p99 target <= 128 KiB
Implementation Package p99 target  <= 256 KiB
Escalation p99 target               <= 64 KiB
cross-process JSON request target   <= 512 KiB
reference supported request envelope <= 1 MiB
silent truncation before canonical digest = 0
```

If valid semantics cannot fit the reference envelope, the implementation MUST externalize appropriate noncanonical large artifacts by exact ref or route the constraint back to P17/P12; it MUST NOT truncate canonical semantics.

**Evidence:** `CPV-E-ENVELOPE-SIZE-INTEGRITY`.

**Gate:** mandatory P34 input for full platform profile; Critical/QUALIFIED.

## 8.4 CPV-C18 — Operational Retention / Alerting

**Statement:** Operational evidence/metadata remains available for the accepted P18 windows and the accepted alert thresholds are machine-verifiable, while neither retention nor alerting becomes semantic truth.

**Invariant:** R37-R38.

**Oracle:** `O-TIMEPOLICY + metric/alert configuration checker + raw-event reconciliation`.

**Fixtures:** G44 plus exact configuration snapshots.

**Operational retention thresholds when the P18 defaults are claimed:**

```text
pending/unresolved outbox: retain until reconciled/resolved
completed delivery metadata hot: >=30 days
high-cardinality traces: 14 days
structured operational logs: 30 days
high-resolution metrics: 90 days
aggregated SLO/cost metrics: >=13 months
```

Canonical StageOccurrence/package/Escalation/semantic-idempotency history remains under the stronger no-automatic-deletion rule and is not governed by these telemetry windows.

**Alert conformance MUST include at least:**

Critical/immediate:

- canonical store integrity/digest failure;
- canonical write bypass;
- dispatch without committed occurrence;
- accepted duplicate terminal commit;
- possible acknowledged-commit loss;
- stale snapshot accepted;
- unauthorized cross-Primary dispatch;
- store unavailable `>2min` while production traffic exists.

Urgent/page:

- oldest ready outbox `>5min`;
- reconciliation lag `>15min` for queryable active provider work;
- RED backpressure sustained `>5min`;
- delivery uncertainty `>30min` or `>=12 attempts`;
- projection ambiguity `>0`;
- unrelated-lane conflict `>1% for 5min`.

Warning/engineering:

- p95 Control API target missed for `30min`;
- projection cache hit ratio `<80%` after warm-up when cache is claimed;
- provider query amplification p95 `>8 PRU`;
- orchestration overhead cost `>10%` on the exact 7-day evaluation;
- YELLOW/ORANGE backpressure sustained `>30min`.

**Metrics:** early/late/missing alert count; retained-artifact availability at boundary; semantic mutation caused solely by retention expiry/alert state.

**Threshold:** every mandatory seeded threshold triggers the expected alert class; no alert/retention event mutates canonical semantic history by itself.

**Evidence:** `CPV-E-OPERATIONAL-RETENTION`, `CPV-E-ALERTING-CONFORMANCE`.

**Gate:** CHALLENGED; mandatory for full production-shaped profile.

## 8.5 CPV-C19 — Long-window Cost / Availability

**Statement:** Long-window economics and service availability are proven with evidence windows that actually match the accepted P18 targets rather than being inferred from the 30-minute R0 latency benchmark.

**Invariant:** R39-R40.

**Oracle:** `O-PERF + independent cost evaluator + independent availability evaluator`.

**Fixtures:** exact 7-day logical R0 workload manifest for cost; qualified synthetic availability corpus prelaunch; actual completed-month raw availability evidence post-launch.

**Evidence:** `CPV-E-7D-COST`, `CPV-E-AVAILABILITY-EVALUATOR-QUALIFICATION`, `CPV-E-MONTHLY-AVAILABILITY`.

**Gate/evaluation:** 7-day cost evidence is required before claiming the full production-shaped cost target. Actual monthly availability attainment is post-launch operational Evidence and MUST NOT be fabricated as an initial P34 result. If a later release/readiness decision consumes it, P24 governance owns that release decision; monthly evidence failure may create a new operational/release finding but never rewrites a historical P34/P24 decision.

---

# 9. Seven-day R0 cost evidence contract

## 9.1 Why the 30-minute R0 benchmark is insufficient

The original P20 10-minute warm-up + 30-minute steady-state protocol remains the correct latency/throughput benchmark for C11. It is **not** evidence for the P18 seven-day cost target.

C19 therefore defines a separate cost workload/evidence run.

## 9.2 Exact workload identity

The run MUST materialize an immutable workload manifest:

```yaml
cost_workload:
  id: CPV-W7D-R0
  logical_window: 168h
  profile_ref: P18-R0
  generator_version: <exact>
  seed: <exact>
  hourly_slices: 168
  transition_mix_manifest_ref: <exact>
  provider_behavior_manifest_ref: <exact>
  cost_model_ref: <exact>
```

The workload MUST represent the accepted R0 control workload using exact counts/mixes for substantive StageOccurrence transitions, provider reads, retries/reconciliation, artifact operations, callback-loss/rate-limit cases included by the declared manifest, and the provider classes claimed by the deployment.

The manifest is reviewable evidence. A prose statement that the run was "representative" is insufficient.

## 9.3 Accelerated deterministic replay

Because the P18 cost target is based on provider/cost units rather than seven days of wall-clock latency, the 168-hour logical workload MAY be replayed with deterministic virtual/accelerated time **only for cost accounting** if all of the following hold:

1. every logical transition/provider interaction from the exact 168-hour manifest is accounted;
2. retry/reconciliation/rate-limit behaviors use the same accepted policies/configuration as the claimed deployment;
3. cost units are counted from actual simulated/recorded provider actions, not multiplied from a hand-entered aggregate;
4. the exact provider price/unit-weight model used to convert PIU/PRU/PAU into comparable cost is immutable and bound by `cost_model_ref`;
5. accelerated replay is not cited as monthly availability or real wall-clock latency evidence;
6. any production-provider-specific minimum billing/rounding behavior materially affecting the ratio is represented in the bound cost model.

A real seven-day staging observation MAY replace accelerated replay when it satisfies the same identity/provenance requirements.

## 9.4 Numerator / denominator

For the exact 168-hour manifest:

```text
orchestration_overhead_cost =
  cost of Control-Plane-created provider reads,
  reconciliation reads,
  transport/artifact operations,
  and any orchestration-only provider invocations

substantive_provider_cost =
  cost of required substantive implementation,
  proof/evidence execution,
  and independently required review invocations
```

Required substantive implementation/proof/review is never reclassified as overhead merely because it is expensive.

Transport retries MUST NOT create extra substantive PIUs; if they do, the semantic/idempotency Claim already fails independently.

Pass rule:

```text
orchestration_overhead_cost / substantive_provider_cost <= 0.10
```

The evidence MUST additionally report PIU/PRU/PAU counts, provider-read amplification median/p95, exact retry/callback/rate-limit counts, and cost-model version so a reviewer can recompute the ratio.

## 9.5 Evidence artifact

`CPV-E-7D-COST` contains exact refs/digests for:

- workload manifest;
- 168 logical hourly slices;
- generator/version/seed;
- provider behavior manifest;
- raw PIU/PRU/PAU events;
- exact cost-model snapshot;
- numerator/denominator classification table;
- independent evaluator version;
- recomputed ratio;
- implementation/config/provider-adapter refs.

Dashboard totals alone are insufficient.

---

# 10. Monthly availability evidence contract

## 10.1 Evidence timing

The P18 monthly availability targets are historical operational targets. They require one **complete actual observation month**.

For a deployment claiming these targets, the canonical evaluation window is one complete UTC calendar month unless a later governed deployment Authority explicitly replaces the reporting timezone/window contract.

Prelaunch P34/P24 evidence may prove:

- availability instrumentation exists;
- probe/evaluator classification is qualified;
- failure/exclusion accounting works on a seeded corpus;
- R0/S0 and recovery targets are met.

Prelaunch evidence MUST NOT set `monthly_availability_attained=true`.

## 10.2 SLI families

Three independent SLI families are required:

```text
CONTROL_API_AVAILABILITY
WRITE_PATH_AVAILABILITY
QUERY_PATH_WHEN_STORE_HEALTHY_AVAILABILITY
```

Each SLI records exact per-operation observations plus at least one authenticated synthetic probe per minute so idle periods do not disappear from the denominator.

Expected client-validation rejections such as semantically correct 4xx `INVALID_REQUEST` responses are service-available outcomes when the API successfully performs the contract. Infrastructure/service unavailability, server failures, and timeouts count unavailable unless an allowed exclusion applies.

## 10.3 Numerator / denominator

For each SLI:

```text
availability = good_eligible_observations / eligible_observations
```

`eligible_observations` MUST include raw real requests plus scheduled synthetic probes after deduplication rules defined by the exact evaluator version.

Provider-bound failures MAY be excluded only when:

1. the P18 target explicitly excludes the relevant external-provider outage;
2. an immutable provider-incident/evidence ref establishes the outage window;
3. Control Plane local API/store path health for the excluded observation can be independently established;
4. the exclusion is listed in an exact exclusion manifest and is reviewer-recomputable.

No generic maintenance/provider label may silently remove failed samples.

For `QUERY_PATH_WHEN_STORE_HEALTHY_AVAILABILITY`, observations during independently proven canonical-store-unhealthy intervals are outside that SLI denominator because the P18 target is explicitly conditioned on store health. Those intervals remain visible in the Control API/write-path evidence and cannot be hidden globally.

## 10.4 Monthly thresholds

For the completed observation month:

```text
CONTROL_API_AVAILABILITY >= 99.9%
WRITE_PATH_AVAILABILITY >= 99.9%
QUERY_PATH_WHEN_STORE_HEALTHY_AVAILABILITY >= 99.9%
```

A month with missing raw evidence, unresolvable exclusion refs, evaluator-version ambiguity, or incomplete probe coverage is `EVIDENCE_GAP/EXCEPTION`, not PASS by interpolation.

## 10.5 Evaluator qualification

Before launch, the availability evaluator MUST detect a seeded corpus containing at least:

- one local API outage;
- one canonical write-path outage;
- one query failure while store is independently healthy;
- one declared external-provider outage eligible for exclusion;
- one falsely labeled provider outage that must remain in denominator;
- one missing synthetic-probe interval;
- one duplicated raw observation;
- one expected semantic 4xx response that must not be counted as infrastructure downtime.

Qualification threshold:

```text
all seeded classifications correct: 100%
false exclusion of local failure: 0
```

Evidence: `CPV-E-AVAILABILITY-EVALUATOR-QUALIFICATION`.

## 10.6 Actual post-launch Evidence

`CPV-E-MONTHLY-AVAILABILITY` contains exact refs/digests for:

- UTC calendar-month boundaries;
- raw request/probe event store/export;
- build/config/deployment refs covering the month;
- store-health evidence;
- external-provider incident refs;
- exact exclusion manifest;
- evaluator version;
- per-SLI numerator/denominator;
- recomputed percentages;
- any evidence gaps/exceptions.

This artifact is generated only after the month closes. It may be consumed by operational/release governance. It does not retroactively rewrite earlier P34 or release history.

---

# 11. Operational retention proof protocol

P18 retention windows longer than a normal prelaunch run are configuration/expiry contracts, not claims that months of history already elapsed.

Prelaunch proof MAY use virtual time when it demonstrates the actual retention implementation/configuration boundary:

1. create exact synthetic operational records;
2. advance `O-TIMEPOLICY` across each retention threshold;
3. verify records are available before their minimum retention boundary;
4. verify only permitted operational/telemetry data expires/compacts after the boundary;
5. verify canonical semantic history remains exact/replayable;
6. capture exact deployed retention configuration/policy ref.

Post-launch audit MAY later corroborate actual age retention.

Virtual-time evidence cannot be used to claim actual monthly availability or actual 13-month historical SLO retention already occurred.

---

# 12. Alerting qualification protocol

Alert rules are verified with exact metric traces around each accepted P18 boundary.

For every mandatory threshold, the evidence set contains:

```text
metric/event input trace
threshold/config ref
virtual/real timestamps
expected alert class
actual alert class/time
correlation identifiers
alert evaluator version
```

Pass conditions:

- below-threshold control does not incorrectly page;
- threshold crossing triggers the correct class within the alerting system's declared evaluation interval;
- alert state does not create or rewrite canonical StageOccurrence/Authority/Gate history;
- zero-tolerance semantic alerts remain zero in clean conformance runs and fire on the corresponding seeded fault/mutant.

`CPV-E-ALERTING-CONFORMANCE` is independent from the dashboard rendering layer.

---

# 13. Evidence artifact additions

The original P20 evidence artifact set remains unchanged and is extended with:

| Evidence ID | Purpose |
|---|---|
| `CPV-E-SNAPSHOT-INTEGRITY` | exact SourceSnapshotToken tamper/binding/currentness negative and positive proof |
| `CPV-E-ASYNC-PROVIDER-CAPABILITY` | durable query/correlation capability proof for every provider claimed autonomous |
| `CPV-E-DELIVERY-POLICY` | dispatch retry cadence, delivery uncertainty, one-occurrence identity proof |
| `CPV-E-RECONCILIATION-POLICY` | OPEN reconciliation cadence and age-not-semantic-failure proof |
| `CPV-E-RATE-LIMIT-CONTROL` | 429 threshold/concurrency/backoff/recovery proof |
| `CPV-E-ENVELOPE-SIZE-INTEGRITY` | P18 record/request-size budgets and no-truncation-before-digest proof |
| `CPV-E-OPERATIONAL-RETENTION` | operational/telemetry retention configuration and expiry-boundary proof |
| `CPV-E-ALERTING-CONFORMANCE` | accepted P18 alert threshold qualification |
| `CPV-E-7D-COST` | exact 168-hour logical R0 cost evidence and independent ratio evaluation |
| `CPV-E-AVAILABILITY-EVALUATOR-QUALIFICATION` | prelaunch qualification of monthly availability classifier/exclusion logic |
| `CPV-E-MONTHLY-AVAILABILITY` | actual completed-month post-launch availability evidence |

Every deterministic artifact used by ProofEvaluation must retain exact `EvidenceInputRef` identity as defined by the accepted Proof Plane semantics.

---

# 14. Obligation-generation repair

The execution-side obligation generator MUST generate obligations for the combined R01-R40 / C01-C19 candidate.

For each applicable new Claim, obligations MUST include the same source-key classes already required by P20:

```text
invariant
oracle
fixture
probe
metric
pass-rule
evidence
challenge
qualification
provenance
```

Additional mandatory source keys include at least:

```text
qualification:snapshot-token-mutants-M16-M20
fixture:G36-G44
pass-rule:delivery-uncertain-12-or-30m
pass-rule:reconciliation-cadence-p18
pass-rule:rate-limit-5pct-5m
pass-rule:no-truncation-before-digest
pass-rule:7d-cost-le-10pct
pass-rule:monthly-api-availability-ge-99.9
pass-rule:monthly-write-availability-ge-99.9
pass-rule:monthly-query-healthy-store-availability-ge-99.9
evidence:CPV-E-7D-COST
evidence:CPV-E-MONTHLY-AVAILABILITY
```

Because CoverageBasis remains `REVIEW_DECLARED`, the complete set still MUST contain exactly one mandatory `COVERAGE_COMPLETENESS` review obligation. `O-COMPLETE` derives expected obligation keys independently from the combined original + repair source, not from the execution generator output.

---

# 15. P34 applicability repair

For a full production-shaped prelaunch P34 review, the reviewer MUST require all applicable original evidence plus the new evidence families, with these timing rules:

- `CPV-E-7D-COST` is required to claim the P18 seven-day economics target.
- `CPV-E-AVAILABILITY-EVALUATOR-QUALIFICATION` is required prelaunch so the later monthly SLI path is not invented after release.
- `CPV-E-MONTHLY-AVAILABILITY` is **not** an initial prelaunch P34 requirement because no actual completed month exists yet; absence before launch is not fabricated as SATISFIED.
- Any statement that monthly `>=99.9%` has been achieved requires actual `CPV-E-MONTHLY-AVAILABILITY` after a completed observation month.
- A later release/readiness evaluation consuming monthly evidence belongs to governance/P24 or the applicable post-release feedback/release decision path; it does not convert P20 into a release owner.

This timing distinction is part of the VerificationSpec and cannot be changed ad hoc by implementation or dashboards.

---

# 16. B1 closure mapping

P21 B1 required explicit binding of missing/under-bound P17/P18 contracts.

| P21 B1 item | Repair binding |
|---|---|
| SourceSnapshotToken integrity + adapter/source compatibility | R31 -> C15 -> O-SNAPSHOT -> G36-G38 -> M16-M18 -> `CPV-E-SNAPSHOT-INTEGRITY` |
| durable query/correlation for claimed autonomous provider | R32 -> C15 -> G39/M19 -> `CPV-E-ASYNC-PROVIDER-CAPABILITY` |
| dispatch retry cadence + delivery uncertainty | R33 -> C16 -> G40 -> `CPV-E-DELIVERY-POLICY` |
| OPEN reconciliation cadence | R34 -> C16 -> G41 -> `CPV-E-RECONCILIATION-POLICY` |
| provider rate-limit adaptation | R35 -> C16 -> G42 -> `CPV-E-RATE-LIMIT-CONTROL` |
| payload/record/request size + no truncation | R36 -> C17 -> G43/M20 -> `CPV-E-ENVELOPE-SIZE-INTEGRITY` |
| operational retention windows | R37 -> C18 -> G44 -> `CPV-E-OPERATIONAL-RETENTION` |
| alerting thresholds | R38 -> C18 -> G44 -> `CPV-E-ALERTING-CONFORMANCE` |
| monthly availability evidence chain | R40 -> C19 -> qualified evaluator + actual month -> `CPV-E-MONTHLY-AVAILABILITY` |

B1 is therefore repaired at the VerificationSpec level; downstream evidence still has to be produced later.

---

# 17. B2 closure mapping

P21 B2 required long-window proof contracts without weakening P18.

## Seven-day cost

Repaired as:

```text
R39
 -> C19
 -> exact CPV-W7D-R0 168h logical manifest
 -> accelerated deterministic replay or equivalent real 7-day observation
 -> exact PIU/PRU/PAU raw events + exact cost model
 -> independent numerator/denominator recomputation
 -> <=10% pass rule
 -> CPV-E-7D-COST
 -> prelaunch full-R0 P34 applicability
```

The original 30-minute R0 benchmark no longer carries the 7-day cost proof burden.

## Monthly availability

Repaired as:

```text
R40
 -> C19
 -> prelaunch evaluator/exclusion qualification
 -> actual complete UTC calendar month after launch
 -> raw request/probe/store-health/provider-incident evidence
 -> exact exclusion manifest
 -> independent per-SLI numerator/denominator recomputation
 -> >=99.9% pass rule for API/write/query-when-store-healthy
 -> CPV-E-MONTHLY-AVAILABILITY
 -> post-launch operational/release governance consumption
```

No prelaunch history is fabricated.

---

# 18. B3 closure mapping

P21 B3 required trust-boundary negative qualification for SourceSnapshotToken.

Repaired mandatory set:

```text
M16 tampered payload / invalid integrity binding
M17 wrong adapter/source-kind binding
M18 mismatched provider resource/version binding
```

Additional correlated boundary mutants:

```text
M19 callback-only provider falsely claims autonomy
M20 truncated canonical bytes accepted/digested
```

Threshold:

```text
M01-M20 detection = 100%
false acceptance = 0
```

Corresponding golden fixtures G36-G39/G43 and exact evidence artifacts are mandatory.

---

# 19. Repaired P20 invariants

The original P20 invariants remain and are extended by:

21. combined declared Requirement universe is R01-R40;
22. combined Claim universe is C01-C19;
23. P34 coverage completeness checks the original P20 + this repair amendment together;
24. SourceSnapshotToken integrity/binding is independently challenged, not inferred from scheduler success;
25. callback-only async providers cannot claim full autonomous trust-sensitive capability;
26. retry/reconciliation/rate-limit policy is verified under deterministic virtual time while preserving semantic identity;
27. payload-size optimization never permits canonical truncation before digest;
28. operational retention windows cannot weaken canonical no-auto-deletion history rules;
29. alerting is verified against accepted thresholds but never becomes semantic truth;
30. 30-minute R0 latency evidence is not seven-day cost evidence;
31. the seven-day cost target has its own exact 168-hour logical workload/evidence identity;
32. accelerated logical replay may prove cost accounting but never monthly availability attainment;
33. monthly availability requires an actual completed observation month;
34. monthly exclusions require immutable independently resolvable provider/store-health evidence;
35. missing monthly raw evidence is an evidence gap/exception, never interpolated PASS;
36. post-launch availability evidence does not retroactively rewrite historical P34/P24 decisions.

---

# 20. Repair disposition and handoff boundary

```text
P20 Verification Design repair
  -> READY / MATERIALIZED — Draft/Proposed
```

The repaired P20 candidate is the **combined two-document package**:

1. `docs/control-plane-productization-verification-v0.2.md`
2. `docs/control-plane-productization-verification-v0.2-p21-repair.md`

This repair does not self-accept the candidate.

Required next owning stage after materialization:

```text
P21 Authority Review
owner: aegis-governance
subject: repaired exact P20 Verification Design candidate
```

The fresh P21 review must verify B1/B2/B3 closure against the new exact head while inheriting the already accepted P20 decisions and the still-trusted architecture head `e657f0e74771184b98f8c8e6f8a8581e4858c82d`.

Do not begin P30/P31/P32 until the repaired exact P20 head receives `PASS / ACCEPTED_FOR_DOWNSTREAM`.