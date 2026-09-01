# Aegis Control Plane Productization v0.2 — CP-I07 P31 Task Package

Status: **P31 READY / MATERIALIZED — CP-I07 only**

Package ID: `CP-I07-P31-01`

Owner: `aegis-implementation`

Execution surface: `CONTROL_REASONING -> CODE_EXECUTION`

This package authorizes one bounded implementation slice only. It is not Product / Modeling / Architecture / Verification Authority, not a P34 Gate verdict, and not permission to begin CP-I08 or CP-I09.

---

# 1. Exact trusted basis

## Accepted predecessor

CP-I06 repaired exact result:

`38b1eb01becb4f1d564dda6dbb635c0a98e0e5d9`

Current CP-I06 P34 review:

`5079267574` — `PASS / ACCEPTED_FOR_DOWNSTREAM`

Historical blocked CP-I06 review `5076730656` remains immutable history and is superseded in current effect only.

Task anchor:

```yaml
task_anchor:
  revision: 38b1eb01becb4f1d564dda6dbb635c0a98e0e5d9
  relation: ancestor
```

## Current Authority chain

- Product: `c628bdc15fdd3d32511a04b6f09055413f2786c3`, review `5061188138`.
- Modeling: `f29c4da3698038e0174e4380707fa618b03c40b2`, review `5062616510`.
- Architecture / P14-P18: `e657f0e74771184b98f8c8e6f8a8581e4858c82d`, review `5062769390`.
- Verification: `db83168e4086e47a7f431acf289006e4f25b8ffd`, review `5062933855`.
- P30 implementation plan: `87cbb166411795261ec5f6e7034a89435e053451`.

Normative implementation sources for this package:

- `docs/control-plane-productization-platform-contract-v0.2.md`
- `docs/control-plane-productization-modules-v0.2.md`
- `docs/control-plane-productization-runtime-flow-v0.2.md`
- `docs/control-plane-productization-engineering-v0.2.md`
- `docs/control-plane-productization-verification-v0.2.md`
- `docs/control-plane-productization-verification-v0.2-p21-repair.md`
- `docs/control-plane-productization-implementation-plan-v0.2.md`

---

# 2. Objective

Implement the first production-shaped **logical platform boundary** for the Control Plane while proving that HTTPS/API/worker/provider convenience cannot create a second semantic writer or new lifecycle owner.

The package must make these boundaries executable and independently testable:

```text
client / app intent
  -> versioned public facade
  -> accepted P13 operation envelope
  -> existing MutationService

worker
  -> internal operational capability
  -> outbox / delivery metadata / reconcile request
  -> NO direct canonical write

provider event
  -> authenticate/correlate hint
  -> exact provider query
  -> corroborated observation
  -> maybe normal mutation/reconciliation
```

---

# 3. Authorized production scope

The implementation may add the smallest modules needed for the following.

## 3.1 Public Control API logical contract

Support a framework-neutral request/response boundary representing:

- protocol version `v1`;
- UTF-8 JSON request bodies;
- `POST /v1/operations`;
- `Idempotency-Key == operation_request_id` when both are present;
- read-only query DTO routes needed for bounded tests;
- application intents that remain noncanonical and may only delegate to existing operations/operational directives.

Forbidden generic mutation routes must be rejected, including semantic equivalents of:

```text
PATCH /status
PATCH /cursor
PATCH /gate
PATCH /stage-occurrence
```

## 3.2 Internal worker capability boundary

Expose a framework-neutral internal capability surface sufficient for:

- claiming committed outbox work;
- recording delivery-attempt metadata;
- requesting occurrence reconciliation;
- submitting provider observations;
- querying provider/platform capability descriptors.

The worker surface MUST NOT expose or possess canonical append / lane advance / terminalization / Gate write methods.

## 3.3 Capability and credential isolation

Represent explicit process/capability descriptors for at least:

- `aegis-control-api`;
- `aegis-control-worker`;
- provider adapters.

The production contract must mechanically distinguish transport credentials from semantic data. Secret/token-shaped fields are forbidden in canonical request payloads and prohibited audit/log summaries produced by this platform layer.

## 3.4 Provider event + query corroboration

Provider callbacks/events are authenticated wakeup hints only.

For any provider class claimed `AUTONOMOUS_TRUST_SENSITIVE`, the adapter descriptor must declare durable query/correlation capability. Callback-only adapters must be classified as non-autonomous/degraded and rejected from full trust-sensitive capability claims.

This package claims real/staging corroboration only for the repository/CI class reachable through the GitHub Actions evidence path. ChatGPT/Codex/Human/Proof real adapters are **NOT_CLAIMED** by CP-I07 and may be represented only as deterministic contract fixtures.

## 3.5 Envelope and size integrity

Enforce the accepted representation rule:

- canonical source bytes are never silently truncated before digest/acceptance;
- request/envelope limits fail closed when exceeded;
- oversized noncanonical artifacts may be represented by exact external ref where the caller already supplies one;
- the platform layer never invents an externalization ref.

## 3.6 Machine-readable API description

Materialize OpenAPI 3.1 or an equivalent exact machine-readable contract covering the public `/v1` and internal `/internal/v1` capability families included by this package.

---

# 4. Explicit non-goals

This package does NOT authorize:

- CP-I08 integrated D0 closure;
- CP-I09 R0/S0/7-day performance claims;
- a real cloud deployment or vendor selection;
- generic canonical PATCH/status/Gate endpoints;
- worker direct canonical database access;
- App / worker / provider adapter becoming a Primary owner;
- webhook payload becoming semantic truth;
- real ChatGPT/Codex/Human/Proof autonomous adapter capability claims;
- any Current cross-Primary rollout expansion;
- repository merge / ready-for-review transition;
- P34 Gate verdict logic inside production or evidence code.

---

# 5. Governing invariants

1. `control-mutation` remains the single canonical Control Plane writer.
2. Public `POST /v1/operations` delegates to the existing accepted MutationService; facade does not duplicate P13 semantics.
3. `Idempotency-Key` mismatch fails closed before mutation.
4. Unsupported protocol version fails closed.
5. Invalid/non-UTF-8/non-JSON transport fails closed before semantic handling.
6. Forbidden generic PATCH/direct-write capabilities are absent or explicitly rejected.
7. Worker capability does not include canonical append, lane CAS, terminalization, or Gate/Authority mutation.
8. Process colocation never weakens logical capability separation.
9. Credentials/tokens are transport capability only and never enter canonical semantic payload/digest or prohibited logs.
10. Provider event payload is a hint only; trust-sensitive state requires query/correlation corroboration.
11. Callback-only provider cannot claim full autonomous trust-sensitive capability.
12. Canonical bytes/digests are computed from the complete representation, never a truncated representation.
13. Current cross-Primary automatic rollout remains `DENIED`.
14. CI/evidence compiler/provider success remains non-authoritative for P34.

---

# 6. Expected implementation surfaces

Production changes are expected to stay within:

```text
tools/aegis_control/api.py
tools/aegis_control/capabilities.py
tools/aegis_control/provider_events.py
tools/aegis_control/openapi.py
tools/aegis_control/__init__.py        # exports only if needed
```

A narrow update to existing internal operational/query helpers is allowed only when required to expose an already-accepted CP-I05/CP-I06 capability without widening canonical ownership.

Test/evidence/workflow surfaces may include:

```text
tests/control_plane/test_cp_i07_*.py
tests/control_plane/generate_cp_i07_evidence.py
.github/workflows/control-plane-cp-i07.yml
```

Any production change outside these boundaries must be explained as required by an accepted contract and must not modify Product/Modeling/Architecture/Verification Authority.

---

# 7. TDD order

P32 MUST execute RED -> GREEN -> regression for each behavioral group.

Minimum initial RED groups:

1. public operation envelope + version/idempotency/forbidden PATCH boundary;
2. worker capability negative probes;
3. callback-only provider autonomy rejection + query-correlated provider acceptance;
4. secret exclusion;
5. exact envelope size / no-silent-truncation;
6. OpenAPI exact capability surface.

Production code must not be written for a behavior before its corresponding failing test is observed.

---

# 8. Verification contract

This package consumes the following combined P20 obligations:

- `CPV-C07 API / Capability / Credential Boundary` / `CPV-R19-R20`;
- `CPV-C15 Snapshot / Async Provider Trust` / provider-capability portion of `CPV-R31-R32`;
- `CPV-C17 Exact Envelope Representation` / `CPV-R36`;
- retained ownership/rollout invariants from `CPV-C04`.

Independent oracle basis:

```text
O-CONTRACT + O-SNAPSHOT + O-PLATFORM + O-AUTH
```

`O-CONTRACT` expected truth must be derived from the accepted P17/P20 contract, not from the production API implementation.

## 8.1 Mandatory direct cases

At minimum evidence must execute and materialize:

### API

- v1 operation envelope delegates exactly once to MutationService;
- `Idempotency-Key` exact match accepted;
- idempotency mismatch rejected with zero canonical residue;
- unsupported protocol version rejected;
- non-JSON / malformed envelope rejected before mutation;
- forbidden PATCH/status/Gate/canonical routes rejected;
- public query route returns DTO/exact refs only and cannot mutate.

### Capability isolation

- worker descriptor has no canonical-write capability;
- worker API exposes no canonical append/lane/terminal/Gate operation;
- colocation fixture preserves the same denial;
- App/facade/provider descriptor has no Primary-owner authority.

### Credential/secret exclusion

- token/secret-shaped fields in semantic operation payload rejected at the facade boundary;
- audit/log serialization redacts or refuses prohibited secret material;
- capability descriptors contain references/scopes, never credential values.

### Provider corroboration

- signed/authenticated event with query-capable adapter wakes reconciliation then uses query result;
- event payload value conflicting with queried value never wins;
- callback-only adapter cannot claim `AUTONOMOUS_TRUST_SENSITIVE`;
- query/correlation-capable GitHub/CI profile may be claimed only with exact corroboration metadata;
- missed callback remains recoverable through query.

### Envelope integrity

- below/at size boundary accepted;
- above boundary fails closed or requires already-supplied exact external ref;
- silent truncation mutant detected;
- digest of accepted canonical payload equals digest of complete source bytes.

### OpenAPI

- OpenAPI version is `3.1.x`;
- `/v1/operations` exists;
- included internal worker paths exist;
- forbidden generic PATCH paths absent;
- schema has explicit protocol/idempotency contract markers.

---

# 9. Required EvidenceArtifacts

P32 must materialize one reviewer-accessible exact-head artifact set containing at least:

```text
api-contract.json                 # CPV-E-API-CONTRACT
capability-security.json          # CPV-E-CAPABILITY-SECURITY
platform-corroboration.json       # CPV-E-PLATFORM-CORROBORATION
envelope-size-integrity.json      # CPV-E-ENVELOPE-SIZE-INTEGRITY
async-provider-capability.json    # refreshed CPV-E-ASYNC-PROVIDER-CAPABILITY
evidence-manifest.json
```

If snapshot-token evidence is inherited unchanged from accepted CP-I04, the manifest must pin the exact predecessor artifact/case identity instead of paraphrasing it. CP-I07 may add adapter-capability evidence without re-owning snapshot token semantics.

Every evidence family must carry exact case-level pass/fail facts and zero-residue / no-semantic-mutation facts where relevant.

The manifest must include:

```yaml
package_id: CP-I07-P31-01
package_ref: <exact P31 package revision>
result_revision: <exact P32 result>
task_anchor:
  revision: 38b1eb01becb4f1d564dda6dbb635c0a98e0e5d9
  relation: ancestor
predecessor_cp_i06_review: 5079267574
claims:
  p34_gate_pass: false
  evidence_compiler_gate_authority: false
  current_cross_primary_rollout: DENIED
  cp_i08_plus: false
```

---

# 10. Zero-tolerance metrics

The evidence manifest must expose at least these metrics, all equal to zero:

```text
forbidden_public_mutation_accepted
worker_canonical_write_capability_exposed
idempotency_identity_mismatch_accepted
unsupported_protocol_version_interpreted
secret_material_entered_semantic_payload
secret_material_emitted_in_prohibited_log
callback_payload_trusted_without_query
callback_only_provider_claimed_autonomous
silent_truncation_before_digest
canonical_digest_mismatch_after_roundtrip
unofficial_gate_or_primary_authority_created
current_cross_primary_rollout_expanded
```

Any nonzero value blocks the package regardless of other test results.

---

# 11. Real-platform corroboration boundary

P20 requires real/staging corroboration for claimed provider classes. CP-I07 therefore uses a narrow claim:

```yaml
claimed_real_provider_classes:
  - GITHUB_REPOSITORY_CI
not_claimed:
  - CHATGPT_REASONING
  - CODEX_EXECUTION
  - HUMAN_DECISION
  - PROOF_PLANE
```

Reviewer-visible GitHub Actions workflow/run/artifact metadata at the exact P32 result is permitted corroboration evidence for the GitHub/CI class, together with the deterministic adapter contract tests.

This does not mean CI success is Gate truth; it only corroborates that the claimed repository/CI provider class has durable queryable run/correlation/materialization surfaces.

---

# 12. Exit criteria

P32 may return `READY_FOR_P34_REVIEW` only when all are true:

1. exact result descends from this package task anchor;
2. all focused CP-I07 tests pass;
3. full Control Plane regression passes;
4. Project State regression passes;
5. Skillset regression passes;
6. evidence generation and JSON validation pass;
7. exact-head artifact upload succeeds and is reviewer accessible;
8. artifact digest can be independently rechecked;
9. all mandatory direct cases pass;
10. all zero-tolerance metrics are zero;
11. no Authority or scope deviation exists;
12. Current cross-Primary rollout remains `DENIED`;
13. CP-I08+ remains not started.

P32 cannot issue P34 PASS.

---

# 13. Handoff

If this package materializes successfully, P31 returns:

```yaml
stage: P31 Task Packaging — CP-I07
package_id: CP-I07-P31-01
status: READY / MATERIALIZED
package_ref: <exact package revision>
task_anchor:
  revision: 38b1eb01becb4f1d564dda6dbb635c0a98e0e5d9
  relation: ancestor
execution_surface: CODE_EXECUTION
next_stage: P32 Implementation — CP-I07
```

P31 itself writes no production implementation and no Gate verdict.
