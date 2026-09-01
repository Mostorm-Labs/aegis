# Aegis Control Plane Productization v0.2 — CP-I09 P31 Task Package

Status: **P31 READY / MATERIALIZED — CP-I09 only**

Package ID: `CP-I09-P31-01`

Primary Owner: `aegis-implementation`

Execution surface: `CONTROL_REASONING -> CODE_EXECUTION`

This package is the final frozen implementation slice. It authorizes R0 latency/throughput evidence, S0 stress/recovery evidence, and deterministic 168-hour seven-day cost evidence only. It does not authorize monthly availability attainment, Current cross-Primary rollout expansion, release, or repository integration.

---

# 1. Exact trusted basis

Accepted predecessor CP-I08 result:

`ac2bcf19acf46a749761ed455ecf0a995069700d`

Current CP-I08 P34 review:

`5079977191` — `PASS / ACCEPTED_FOR_DOWNSTREAM`

Task anchor:

```yaml
task_anchor:
  revision: ac2bcf19acf46a749761ed455ecf0a995069700d
  relation: ancestor
```

Current Authority:

- Product `c628bdc15fdd3d32511a04b6f09055413f2786c3` / review `5061188138`.
- Modeling `f29c4da3698038e0174e4380707fa618b03c40b2` / review `5062616510`.
- Architecture / Engineering `e657f0e74771184b98f8c8e6f8a8581e4858c82d` / review `5062769390`.
- Verification `db83168e4086e47a7f431acf289006e4f25b8ffd` / review `5062933855`.
- P30 implementation plan `87cbb166411795261ec5f6e7034a89435e053451`.

All CP-I01..CP-I08 accepted semantics and zero-tolerance invariants remain mandatory regression inputs.

---

# 2. Objective

At one exact implementation revision, produce reviewer-recomputable engineering evidence for:

1. **R0** reference production-shaped workload under real monotonic wall clock;
2. **S0** 4× stress workload under real monotonic wall clock plus backlog recovery;
3. **CPV-W7D-R0** exact 168-hour logical cost workload under deterministic accelerated replay only;
4. exact raw histograms/time-series/resource/cost-unit evidence sufficient for independent evaluation.

CP-I09 must never cite accelerated time as R0/S0 latency or monthly availability evidence.

---

# 3. R0 immutable benchmark contract

## 3.1 Required retained/runtime data shape

The benchmark fixture must materialize at least:

```yaml
active_work_scopes: 10000
retained_work_scopes: 100000
canonical_record_revisions_retained: 5000000
open_stage_occurrences: 2000
recent_completed_occurrence_revisions_per_work_scope_p95: 250
concurrent_active_provider_jobs: 500
concurrent_interactive_app_users: 100
```

Fixture materialization is setup work and is excluded from benchmark latency windows. It may use a benchmark-only bulk loader but must load the actual production `ControlStore` schema. The fixture loader must never be imported by production modules.

The benchmark artifact must report exact row/object counts after fixture load and fail closed below any declared floor.

## 3.2 Offered load

Steady-state R0:

```yaml
control_api_requests_per_second: 50
canonical_mutation_requests_per_second: 20
projection_evaluations_per_second: 200
provider_callback_or_query_events_per_second: 100
outbox_dispatch_attempts_per_second: 50
```

Mandatory bursts during the R0 measurement window:

```yaml
control_api_requests_per_second: 200
control_api_burst_wall_seconds: 60
canonical_mutation_requests_per_second: 100
canonical_mutation_burst_wall_seconds: 30
provider_callbacks_per_minute: 1000
```

The workload generator must materialize exact actual counts and scheduled/observed rates. It must not merely declare the rates in configuration.

## 3.3 Real wall-clock protocol

Required:

```yaml
clock_class: REAL_MONOTONIC_WALL_CLOCK
warmup_wall_seconds_min: 600
steady_state_wall_seconds_min: 1800
```

No virtual clock, accelerated time, duration multiplier, or post-hoc scaling may satisfy either duration.

The R0 evidence must contain raw monotonic start/end facts for warm-up and measurement and the evaluator must reject:

- warm-up `<600s`;
- measurement `<1800s`;
- any non-real measurement class;
- missing mandatory burst coverage.

## 3.4 R0 latency targets

Excluding provider execution time:

```yaml
cached_read_only_query_ms:
  p50_max: 50
  p95_max: 200
  p99_max: 500
simple_canonical_mutation_ms:
  p50_max: 100
  p95_max: 250
  p99_max: 750
cached_projection_up_to_2000_revisions_ms:
  p95_max: 250
cold_projection_up_to_2000_revisions_ms:
  p95_max: 2000
scheduler_decision_ms:
  p95_max: 250
outbox_claim_to_adapter_dispatch_ms:
  p95_max: 500
terminalization_commit_to_query_visibility_ms:
  p95_max: 1000
```

Every claimed latency family must include raw samples or reviewer-recomputable fixed histograms and p50/p95/p99 (plus max for completeness).

## 3.5 R0 pass conditions

- exact data-shape floors met;
- exact wall-clock minima met;
- required steady/burst load delivered;
- all required latency quantiles within threshold;
- zero invariant violations;
- zero accidental duplicate semantic executions;
- no provider call occurs inside an open canonical mutation transaction;
- provider read amplification median/p95 reported;
- raw CPU/RSS/disk/queue observations included.

---

# 4. S0 immutable stress contract

S0 uses the same topology and retained data shape as R0.

Required offered load is exactly `4×` every R0 steady-state rate:

```yaml
control_api_requests_per_second: 200
canonical_mutation_requests_per_second: 80
projection_evaluations_per_second: 800
provider_callback_or_query_events_per_second: 400
outbox_dispatch_attempts_per_second: 200
```

Required:

```yaml
clock_class: REAL_MONOTONIC_WALL_CLOCK
stress_wall_seconds_min: 900
```

S0 evidence must also include declared provider-degradation injection and a post-overload recovery phase.

Pass conditions:

- wall-clock stress `>=900s`;
- exact 4× offered-load identity;
- no silent dropped work;
- zero invariant violations;
- zero accidental semantic duplicates;
- p50/p95/p99/max reported for major latency families;
- throughput/saturation/resource utilization reported;
- backlog/pressure telemetry reported;
- after overload is removed, backlog/pressure returns below YELLOW before the recovery observation ends;
- rate-limit/degradation handling does not create semantic retry/replacement work.

---

# 5. Exact seven-day cost workload contract

Workload identity:

```yaml
id: CPV-W7D-R0
logical_window_hours: 168
hourly_slices: 168
measurement_class: ACCELERATED_REPLAY
generator_version: cp-i09-w7d-v1
seed: 20260901
profile_ref: P18-R0
```

Only this cost workload may use accelerated time.

Each logical hour must materialize raw provider-unit events derived from the exact declared transition/provider behavior manifest. The evaluator may not multiply one aggregate by 168.

## 5.1 Reference normalized cost model

CP-I09 freezes the following **reference normalized provider-action model** for the repository benchmark profile:

```yaml
cost_model_id: CP-I09-REFERENCE-NORMALIZED-V1
currency: NORMALIZED_COST_UNIT
weights:
  PIU: 1.0
  PRU: 1.0
  PAU: 1.0
rounding: none
minimum_billing: none
```

Rationale: this repository benchmark does not claim a production vendor price sheet. Equal unit weighting is intentionally transparent and conservative against orchestration overhead; it does not discount PRU/PAU to make the target easier.

The artifact must expose raw PIU/PRU/PAU rows and the independent evaluator must recompute both numerator and denominator from those rows.

If a later real deployment uses provider-specific prices/minimum billing, this normalized model does not replace that release evidence.

## 5.2 Cost classification

```text
orchestration_overhead_cost =
  Control-Plane-created provider reads + reconciliation reads +
  transport/artifact operations + orchestration-only invocations

substantive_provider_cost =
  required substantive implementation + proof/evidence execution +
  independently required review invocations
```

Required substantive work must never be reclassified as overhead to improve the ratio, and transport retries may not create extra substantive PIUs.

Pass rule:

```text
orchestration_overhead_cost / substantive_provider_cost <= 0.10
```

Artifact also reports raw PIU/PRU/PAU counts, provider-read amplification median/p95, retry/callback/rate-limit counts, model version, exact 168 slices, and independent recomputed ratio.

---

# 6. Monthly availability boundary

CP-I09 does **not** claim completed-month `>=99.9%` availability.

Required manifest state:

```yaml
monthly_availability_attainment: NOT_CLAIMED_PRELAUNCH
availability_evaluator_qualification: INHERITED_FROM_CP_I08
```

Accelerated cost replay, R0, or S0 evidence must never be converted into monthly availability evidence.

---

# 7. Production / benchmark implementation scope

No new semantic lifecycle capability is expected. Production optimization is allowed only when a real R0/S0 measurement identifies an engineering bottleneck and the change preserves accepted contracts.

Normally expected new surfaces are benchmark/evidence only:

```text
tests/control_plane/cp_i09_contract.py
tests/control_plane/cp_i09_fixture.py
tests/control_plane/cp_i09_benchmark.py
tests/control_plane/cp_i09_cost.py
tests/control_plane/generate_cp_i09_evidence.py
tests/control_plane/test_cp_i09_*.py
.github/workflows/control-plane-cp-i09.yml
```

If performance repair requires a production index/optimization, it must be the smallest change at the owning module (for example Store/index/projection query implementation), must receive RED performance/regression evidence first, and must not change canonical semantics.

No Product/Modeling/Architecture/Verification Authority document may be modified.

---

# 8. TDD contract before long benchmark execution

Short contract tests must first prove that the benchmark/evaluator fails closed for:

1. R0 warm-up `<600s`;
2. R0 measurement `<1800s`;
3. non-real clock attempting to claim R0 latency;
4. missing R0 burst coverage;
5. retained revision/work-scope/open-occurrence/provider/user shape below minimum;
6. S0 stress `<900s`;
7. S0 offered load not exactly 4× R0;
8. S0 recovery that remains YELLOW/ORANGE/RED;
9. seven-day cost with fewer/more than 168 exact hourly slices;
10. cost replay not marked `ACCELERATED_REPLAY`;
11. cost numerator/denominator inconsistent with raw PIU/PRU/PAU rows;
12. attempted monthly-availability claim from R0/S0/accelerated evidence.

These short tests validate the harness only. They cannot substitute for wall-clock R0/S0.

---

# 9. Workflow topology

The exact CP-I09 Actions workflow should use separate jobs where practical:

```text
contract-regression
fixture-shape / benchmark setup
r0-real-wall-clock
s0-real-wall-clock
cost-168h-accelerated
combine-and-verify
```

R0 and S0 may execute concurrently because S0 rates are frozen as exact 4× R0 configuration, not derived from empirical R0 throughput.

The final combine job may emit PASS evidence only after all required predecessor jobs succeed and exact result revision identity matches.

---

# 10. Required EvidenceArtifacts

The final reviewer-accessible exact-head bundle must include at least:

```text
r0-workload-manifest.json
r0-raw-timeseries.json
r0-latency-histograms.json
r0-performance.json                 # CPV-E-PERFORMANCE-R0
s0-workload-manifest.json
s0-raw-timeseries.json
s0-stress.json                      # CPV-E-STRESS-S0
w7d-workload-manifest.json
w7d-hourly-slices.json
w7d-raw-cost-events.json
w7d-cost-model.json
w7d-cost.json                       # CPV-E-7D-COST
engineering-handoff.json            # CPV-E-ENGINEERING-HANDOFF
evidence-manifest.json
```

A split per-job artifact is allowed during execution, but the final Gate artifact must materialize the combined exact set above at one reviewer-accessible result boundary.

---

# 11. Required final manifest fields

```yaml
package_id: CP-I09-P31-01
package_ref: <exact package ref>
result_revision: <exact result>
task_anchor:
  revision: ac2bcf19acf46a749761ed455ecf0a995069700d
  relation: ancestor
source_cp_i08_p34_review: 5079977191
r0:
  clock_class: REAL_MONOTONIC_WALL_CLOCK
  warmup_wall_seconds: <actual>
  measurement_wall_seconds: <actual>
  passed: <bool>
s0:
  clock_class: REAL_MONOTONIC_WALL_CLOCK
  stress_wall_seconds: <actual>
  offered_load_multiplier: 4
  recovery_below_yellow: <bool>
  passed: <bool>
w7d:
  measurement_class: ACCELERATED_REPLAY
  logical_hours: 168
  independent_ratio: <actual>
  passed: <bool>
claims:
  p34_gate_pass: false
  evidence_compiler_gate_authority: false
  current_cross_primary_rollout: DENIED
  monthly_availability_attainment: NOT_CLAIMED_PRELAUNCH
```

---

# 12. Zero-tolerance metrics

At minimum all equal zero:

```text
r0_invariant_failures
r0_accidental_semantic_duplicates
r0_wall_clock_shortfall
r0_required_load_or_burst_missing
r0_latency_target_miss
s0_invariant_failures
s0_accidental_semantic_duplicates
s0_wall_clock_shortfall
s0_offered_load_identity_mismatch
s0_unrecovered_backlog
provider_call_inside_open_mutation_transaction
cost_hourly_slice_identity_mismatch
cost_raw_recompute_mismatch
cost_ratio_target_miss
accelerated_time_used_for_latency_claim
monthly_availability_fabricated
current_cross_primary_rollout_expanded
```

Any nonzero metric blocks CP-I09.

---

# 13. P32 exit criteria

P32 may return `READY_FOR_P34_REVIEW` only when one exact result revision has:

- short CP-I09 contract tests PASS;
- full Control Plane regression PASS;
- Project State regression PASS;
- Skillset regression PASS;
- actual R0 real-wall-clock warm-up `>=600s` and measurement `>=1800s`;
- actual S0 real-wall-clock stress `>=900s` plus successful recovery below YELLOW;
- R0/S0 retained data shape at/above all required floors;
- all required R0 latency targets PASS;
- S0 invariant/duplicate/recovery targets PASS;
- exact 168-hour accelerated cost workload PASS with independently recomputed ratio `<=0.10`;
- all final zero metrics = 0;
- exact combined final artifact materialized and independently digest-verifiable;
- monthly availability explicitly not claimed;
- rollout remains `DENIED`;
- no Gate verdict from implementation/evidence compiler.

---

# 14. Post-Gate integration boundary

CP-I09 P34 acceptance ends the frozen implementation/evidence slices but **does not by itself complete the project** while stacked PRs remain unintegrated.

After CP-I09 Gate acceptance, route through central Aegis to the repository-integration/finishing owner. Integration must preserve exact accepted Gate history and merge stacked package/implementation refs in a fail-closed order or an equivalent reviewed integration strategy.
