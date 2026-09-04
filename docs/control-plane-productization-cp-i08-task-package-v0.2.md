# Aegis Control Plane Productization v0.2 — CP-I08 P31 Task Package

Status: **P31 READY / MATERIALIZED — CP-I08 only**

Package ID: `CP-I08-P31-01`

Primary Owner: `aegis-implementation`

Execution surface: `CONTROL_REASONING -> CODE_EXECUTION`

This package authorizes the integrated deterministic D0 / verifier-qualification / observability-closure slice only. It does not authorize CP-I09 performance claims, release, integration, or Current cross-Primary rollout expansion.

---

# 1. Exact trusted basis

Accepted predecessor CP-I07 result:

`c7cb7d3d60c5b4505b965bd9f1ea5389c9135e07`

CP-I07 P34 review:

`5079615570` — `PASS_WITH_FINDINGS / ACCEPTED_FOR_DOWNSTREAM`

Task anchor:

```yaml
task_anchor:
  revision: c7cb7d3d60c5b4505b965bd9f1ea5389c9135e07
  relation: ancestor
```

Current Authority remains:

- Product `c628bdc15fdd3d32511a04b6f09055413f2786c3` / review `5061188138`.
- Modeling `f29c4da3698038e0174e4380707fa618b03c40b2` / review `5062616510`.
- Architecture/P14-P18 `e657f0e74771184b98f8c8e6f8a8581e4858c82d` / review `5062769390`.
- Verification `db83168e4086e47a7f431acf289006e4f25b8ffd` / review `5062933855`.
- P30 plan `87cbb166411795261ec5f6e7034a89435e053451`.

All CP-I01 through CP-I07 Gate-accepted behavior remains inherited and must regress cleanly at the exact CP-I08 result.

---

# 2. Objective

At one exact integrated implementation revision, prove that the complete deterministic Control Plane through CP-I07 preserves semantic invariants and that the verifier/evidence machinery is qualified before any R0/S0/long-window engineering result can be trusted.

The exact closure target is:

```text
G01-G44 = 44/44 PASS
semantic differential mismatches = 0
zero-tolerance invariant events = 0
M01-M20 detected = 20/20
false mutant acceptance = 0
canonical replay drift = 0
required metric families missing = 0
availability evaluator false local-failure exclusion = 0
```

---

# 3. Authorized implementation scope

## 3.1 Production-shaped composition boundary

Add the smallest deterministic composition root needed to prove CP-I07 F1/F2:

- public `ControlApi` is bound to the already-accepted `MutationService` instance, never to a second semantic writer;
- worker-facing capability receives only operational ports/callables and never the `ControlStore` private mutation transaction or canonical append authority;
- provider-event ingress preserves explicit post-auth provenance (`signature_verified` and verifier/source metadata) before reconciliation/query;
- composition metadata is observable but never semantic truth.

## 3.2 Observability / raw evidence export

Add a deterministic observability layer that:

- records append-only raw operational metric/trace events;
- carries correlation IDs and exact occurrence/request/provider identifiers when present;
- exposes independent aggregation input without becoming semantic state;
- supports the required P18 metric-family presence checks;
- does not infer Gate/Authority/lifecycle truth from telemetry.

## 3.3 Operational retention

Add deterministic retention policy evaluation for permitted operational/telemetry data only.

Must prove:

- expiry decisions are based on explicit class/window/current-time inputs;
- canonical StageOccurrence/package/Escalation/semantic-idempotency history is `NO_AUTO_DELETE`;
- retention evaluation has no canonical write capability;
- exact boundary behavior can be swept under virtual time.

## 3.4 Alert qualification

Add deterministic alert-rule evaluation over explicit telemetry facts.

Must prove:

- exact threshold/boundary classification;
- alert state is operational only;
- alert evaluation cannot terminalize occurrences, schedule successors, emit Gate truth, or mutate canonical history;
- seeded warning/urgent/critical cases are reproducible.

## 3.5 Availability evaluator qualification

Add an independent evaluator/classifier for the *measurement path only*.

It must use explicit:

- numerator;
- denominator;
- provider-exclusion classification;
- local/store-health classification;
- observation-window identity.

Prelaunch CP-I08 may qualify the evaluator with seeded cases. It MUST NOT claim any historical monthly `>=99.9%` attainment.

## 3.6 Integrated D0 harness

Materialize one exact-revision D0 harness that covers all `G01..G44` and `M01..M20`.

Allowed evidence source kinds per G-case:

```text
DIRECT_INTEGRATED_PROBE
EXACT_HEAD_REGRESSION_TEST
INHERITED_ACCEPTED_PREDECESSOR_EVIDENCE
```

Rules:

1. Every G01-G44 key appears exactly once.
2. Any inherited entry pins exact predecessor revision, Gate review, artifact ID/file/case ID, and is mechanically checked to exist.
3. Any regression-test entry pins an exact test ID and the exact CP-I08 workflow/job that executed it.
4. G36-G44 must have direct integrated/exact-head evidence at CP-I08; they may not be satisfied by prose.
5. `M01..M20` must execute `qualification.run_qualification()` at the exact CP-I08 revision and materialize exact mutant provenance/results.
6. A green generic test suite is not itself a 44/44 coverage proof.

---

# 4. CP-I07 findings carried as mandatory CP-I08 obligations

## F1 — composition wiring

Directly prove that production-shaped composition binds `ControlApi` to accepted `MutationService` and that the worker side cannot access a second canonical writer.

Required negative probe: a worker/composition object must not expose `append_canonical`, `_mutation_transaction`, lane-CAS, terminalization, Gate write, or equivalent semantic write capability.

## F2 — provider-auth provenance

Directly prove that normalized provider-event reconciliation preserves the post-auth `signature_verified` provenance and an explicit verifier/source identity before query/corroboration. A false/unverified event must not invoke provider query or semantic mutation.

This package does not implement a real webhook server/signature algorithm; it proves the accepted logical post-auth boundary and provenance transport at the integrated composition layer.

---

# 5. Explicit non-goals

Not authorized:

- CP-I09 R0 30-minute pass claim;
- CP-I09 S0 4x/15-minute pass claim;
- seven-day cost pass claim;
- fabricated/accelerated monthly availability attainment;
- real production launch/cloud deployment;
- Current cross-Primary rollout expansion;
- rewriting P20/P17/P18 Authority;
- new canonical semantic writer;
- deleting canonical history under retention policy;
- alert/evaluator/telemetry becoming semantic truth;
- P34 verdict from implementation/evidence compiler;
- merge/ready-for-review/repository integration.

---

# 6. Expected implementation surfaces

Production surfaces should remain bounded principally to:

```text
tools/aegis_control/composition.py
tools/aegis_control/observability.py
tools/aegis_control/retention.py
tools/aegis_control/availability.py
```

A narrow extension to `provider_events.py` is permitted only to carry already-accepted post-auth provenance without changing provider trust semantics.

Test/evidence/workflow surfaces:

```text
tests/control_plane/test_cp_i08_*.py
tests/control_plane/cp_i08_d0.py
tests/control_plane/generate_cp_i08_evidence.py
.github/workflows/control-plane-cp-i08.yml
```

No Product/Modeling/Architecture/Verification Authority document may be modified.

---

# 7. TDD order

P32 must observe RED before production changes for each new capability group:

1. composition/F1 second-writer denial;
2. provider-auth provenance/F2;
3. observability raw-event + aggregate recomputation;
4. retention `NO_AUTO_DELETE` boundary;
5. alert boundary and no semantic mutation;
6. availability evaluator classification;
7. integrated D0 completeness/evidence materialization.

Do not weaken existing CP-I01..I07 tests to obtain GREEN.

---

# 8. Required EvidenceArtifacts

Exact reviewer-accessible bundle must contain at least:

```text
d0-conformance.json                       # CPV-E-D0-CONFORMANCE
verifier-qualification.json               # CPV-E-VERIFIER-QUALIFICATION
retention-replay.json                     # CPV-E-RETENTION-REPLAY
observability-cost.json                   # CPV-E-OBSERVABILITY-COST (qualification/attribution path, not 7-day pass)
operational-retention.json                # CPV-E-OPERATIONAL-RETENTION
alerting-conformance.json                 # CPV-E-ALERTING-CONFORMANCE
availability-evaluator-qualification.json # CPV-E-AVAILABILITY-EVALUATOR-QUALIFICATION
evidence-manifest.json
```

The manifest must carry exact refs to applicable accepted CP-I01..I07 evidence inputs or exact-head regression/test identities. It must not paraphrase predecessor claims without resolvable refs.

---

# 9. Mandatory D0 / qualification contract

## G corpus

- exactly `G01..G44`;
- exactly 44 evaluated entries;
- 44/44 PASS;
- `semantic_differential_mismatches = 0`;
- `zero_tolerance_invariant_events = 0`.

Direct CP-I08 boundary requirements include:

- G32 invalid/unverifiable webhook/event auth rejection;
- G36-G38 snapshot integrity/binding qualification at exact integrated revision;
- G39 callback-only provider capability rejection;
- G40 delivery retry identity preservation;
- G41 callback-loss/age-band reconciliation without semantic retry;
- G42 rate-limit policy conformance;
- G43 full representation/no silent truncation;
- G44 retention/alert boundary sweep.

## Mutant corpus

- exactly `M01..M20`;
- detected 20/20;
- false acceptance 0;
- exact M16-M18 token/binding provenance retained;
- exact M20 full/truncated representation provenance retained.

---

# 10. Observability qualification

Required raw event families at minimum:

```text
control_api_latency
canonical_transaction_latency
projection_latency
outbox_depth
outbox_oldest_age
open_occurrence_age
reconciliation_latency
provider_call_count
provider_rate_limit
conflict_count
zero_tolerance_invariant
orchestration_cost_component
```

Every raw event must include:

- metric/event family;
- timestamp/monotonic sequence;
- correlation ID;
- value/unit;
- exact dimensions needed for independent aggregation.

The evidence compiler must independently recompute aggregates from raw rows and prove exact equality with exported aggregate values.

No dashboard screenshot or precomputed-only aggregate is sufficient.

---

# 11. Retention / replay qualification

Mandatory direct cases:

- permitted delivery metadata expires exactly at policy boundary;
- permitted telemetry expires exactly at policy boundary;
- data one tick before boundary remains;
- canonical StageOccurrence history is never auto-delete eligible;
- canonical Implementation Package history is never auto-delete eligible;
- canonical Escalation history is never auto-delete eligible;
- semantic idempotency history is never auto-delete eligible;
- retention evaluator has no canonical mutation capability;
- canonical replay digest before/after operational retention sweep is identical.

`canonical_replay_drift` must be 0.

---

# 12. Alert qualification

Direct seeded cases must prove exact no-alert/warning/urgent/critical boundaries for the P18 thresholds selected by the implementation plan/Authority and prove:

- an alert result is an operational record/DTO only;
- no alert case invokes MutationService;
- no alert case emits Gate PASS/BLOCKED as lifecycle truth;
- alert result can be recomputed from raw telemetry.

---

# 13. Availability evaluator qualification

Seeded corpus must include at least:

- local API success counts in denominator/numerator correctly;
- local API failure remains a local failure and is never provider-excluded;
- canonical-store/local dependency failure cannot be provider-excluded;
- explicitly external provider outage may be classified according to the accepted exclusion rule only when evidence marks it external;
- ambiguous failure fails closed as non-excluded;
- empty/invalid denominator fails closed;
- incomplete observation window is marked `INCOMPLETE` and cannot claim monthly attainment;
- complete seeded window computes exact ratio deterministically.

Threshold for evaluator qualification:

```text
seeded classifications correct = 100%
false exclusion of local failure = 0
historical monthly attainment claimed = 0
```

---

# 14. Zero-tolerance manifest metrics

At minimum all must equal zero:

```text
semantic_differential_mismatches
zero_tolerance_invariant_events
false_mutant_acceptance
canonical_replay_drift
missing_required_metric_families
raw_aggregate_recompute_mismatch
operational_retention_mutated_canonical_history
alert_caused_semantic_mutation
alert_emitted_gate_truth
availability_false_local_failure_exclusion
availability_incomplete_window_claimed_attainment
composition_second_writer_exposed
provider_auth_provenance_lost
current_cross_primary_rollout_expanded
```

Any nonzero value blocks CP-I08.

---

# 15. Exact workflow exit criteria

P32 may return to CONTROL_REVIEW only when the exact result has:

- CP-I08 focused tests PASS;
- full Control Plane regression PASS;
- Project State regression PASS;
- Skillset regression PASS;
- G01-G44 exactly 44/44 PASS;
- M01-M20 exactly 20/20 detected, false acceptance 0;
- availability evaluator seeded qualification 100%;
- retention/alert/observability qualification PASS;
- all manifest zero metrics = 0;
- exact 8-file evidence artifact uploaded and independently resolvable;
- artifact ZIP/file digests independently checkable;
- CP-I09 not started;
- rollout remains `DENIED`;
- no Gate claim from the evidence compiler.

P32 cannot issue P34 PASS.

---

# 16. Handoff

Successful P31 return:

```yaml
stage: P31 Task Packaging — CP-I08
package_id: CP-I08-P31-01
status: READY / MATERIALIZED
package_ref: <exact package revision>
task_anchor:
  revision: c7cb7d3d60c5b4505b965bd9f1ea5389c9135e07
  relation: ancestor
source_cp_i07_p34_review: 5079615570
next_stage: P32 Implementation — CP-I08
execution_surface: CODE_EXECUTION
```
