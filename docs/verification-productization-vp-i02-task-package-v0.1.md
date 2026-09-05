# VP-I02-P31-01 — Evidence Compilation & Independent Review Runtime Task Package

Status: **P31 / CONTROL_REASONING / MATERIALIZED — READY FOR EXPLICIT P32 START**

This is the executable P31 package for `VP-I02 — Evidence Compilation & Independent Review Runtime`. It consumes the accepted VP-I01 Gate result and authorizes only the deterministic evidence/evaluation/review runtime defined by the accepted P30/P20 basis. It does not start P32, issue P34 PASS, merge any PR, publish Authority, or begin VP-I03.

The earlier commit `fc653f6f97a8807b9e7efe618d6383479d970a75` is a **NON-EXECUTABLE materialization shell** only and MUST NOT be used as `package_ref`.

---

## 1. Task identity

```yaml
package_id: VP-I02-P31-01
slice_id: VP-I02
name: EVIDENCE_COMPILATION_AND_INDEPENDENT_REVIEW_RUNTIME
stage_owner: aegis-implementation
execution_surface_now: CONTROL_REASONING
preferred_p32_surface: CODE_EXECUTION
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/73

# P30 preserves this stable trusted ancestry root.
task_anchor:
  revision: 674e01737621621b8131e35f83313fb0154a9f6d
  relation: ancestor

resume_cursor: null
```

The exact executable `package_ref` is the final commit containing this document and is recorded externally by the P31 result / PR metadata after materialization. This document does not attempt to embed the future commit SHA that contains itself.

A future P32 MUST resolve repository identity first, then resolve this same-repository PR #73 and exact final `package_ref`, then verify ancestry and the exact accepted predecessor below before any mutation.

---

## 2. Exact trusted basis and accepted predecessor

### Upstream accepted Authority / design basis

```yaml
semantic_basis: 12c968c5c481ad671ce33bcfa088ba8a2fca0f43
semantic_p21_recertification: 5121012716
p14_basis: d9c8f6ac5db4359400fae06e76c51c65bd059bfc
p15_basis: 665292dcfd7781935243369ee9f676c320f2878a
p16_basis: 708cf09c01effbcc63c65d45b9b4a67b7a8fc8db
p17_basis: c8f47d049be50d65f88b04ad141650ed6dfdb826
p20_verification_basis: 674e01737621621b8131e35f83313fb0154a9f6d
p20_p21_review: 5121075377
p30_implementation_plan: 69a390439f650e1f418f9b589828b6e67bc18c6f
```

### Accepted VP-I01 predecessor

```yaml
accepted_predecessor:
  slice: VP-I01
  result_revision: ef995501c3dcd1f7f608083028f43bb4bde66103
  materialized_ref: https://github.com/Mostorm-Labs/aegis/pull/71
  p34_gate_review: 5121366259
  p34_verdict: PASS
  p24_readiness_review: 5121383523
  p24_disposition: READY_FOR_STACK_LOCAL_INTEGRATION
  governing_package_id: VP-I01-P31-02
  governing_package_ref: b979f1fc59178c16285449a92f02dd5964e523d0
  governing_package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/72
```

P32 may start only from a repository revision that preserves exact VP-I01 predecessor semantics. The expected clean execution base is the final VP-I02 P31 package head, which is itself a descendant of `ef995501...`; historical HEAD equality to the stable P20 task anchor is not required.

If the observed starting revision is not a descendant of `ef995501...`, or if descendant changes conflict with VP-I01 APIs used by this package, stop with `BLOCKED_EXECUTION_DIVERGENCE` rather than silently rebasing semantic assumptions.

---

## 3. Purpose and incident closure

VP-I02 implements the deterministic evidence/evaluation/review core after VP-I01 established exact package/preflight truth.

This slice closes the P30-assigned incident/proof families:

- **R1 authoritative fact mismatch** — authoritative structured producer truth cannot be overridden by copied/manual totals;
- **R4 post-hoc Gate schema expansion** — undeclared Gate-critical fields are classified/routed to their owning earlier layer instead of becoming retroactive P32 transcription work;
- **R5 evidence-only repair** — external evidence rematerialization may preserve result identity only when result bytes do not change;
- **independent obligation completeness** — review expected-set traversal is independent from generator traversal;
- **Gate ownership separation** — ProofEvaluation/green CI/summary data cannot emit official P34 PASS.

Normative identity separation remains:

```text
machine observation
!= EvidenceArtifact / EvidenceInputRef
!= implementation result
!= ProofEvaluation
!= P34 Gate Decision
```

No second canonical `ProofFact`, `EvidenceManifest`, or `MaterializationEnvelope` object family is authorized.

---

## 4. Exact authored scope

Authorization mode:

```yaml
authorization_mode: EXACT_PATH_SET
numeric_changed_file_count_constraint: NONE
```

### Create exactly these seven paths

```text
tools/aegis_proof/ports.py
tools/aegis_proof/evidence.py
tools/aegis_proof/evaluation.py
tools/aegis_proof/review.py
tests/verification_productization/test_evidence_compiler.py
tests/verification_productization/test_evidence_repair.py
tests/verification_productization/test_evaluation_review.py
```

### Modify exactly this existing path, and only for public exports

```text
tools/aegis_proof/__init__.py
```

The `__init__.py` change is authorized only to re-export the P30-frozen VP-I02 public interfaces introduced by the four new runtime modules. It MUST NOT change VP-I01 behavior, package/preflight semantics, canonicalization, or introduce convenience logic.

The intended export surface is limited to the exact P30 interfaces introduced by VP-I02:

```text
ObservationRecord
ObservationBatch
ImmutableArtifactLocator
ArtifactStorePort
ExactRefResolverPort
ResultMaterializationPort
EvidenceRequirement
EvidencePlan
EvidencePlanBuilder
EvidenceCompiler
EvidenceMaterializer
EvaluationResult
ProofEvaluator
ReviewDelta
CompletenessResult
IndependentCompletenessChecker
ReviewContractDiffer
ReviewBundleAdapter
```

### Explicitly forbidden authored mutation

```text
tools/aegis_proof/domain.py
tools/aegis_proof/spec.py
tools/aegis_proof/obligations.py
tools/aegis_proof/package.py
tools/aegis_control/**
tests/control_plane/**
plugins/aegis/**
skillset/**
skills/**
.aegis/**
.github/workflows/**
tools/aegis_state/**
tools/aegis_skillset/**
release manifests / tags / releases
VP-I03 adapter / CLI / Skill-integration paths
```

If the accepted VP-I01 implementation must change to make VP-I02 work, stop and classify the exact reason. This package does not authorize repairing predecessor semantics in place.

---

## 5. Required runtime contracts

### 5.1 `tools/aegis_proof/ports.py`

Implement the P30-frozen provider-neutral DTO/port boundary:

```python
@dataclass(frozen=True)
class ObservationRecord:
    fact_key: str
    producer_class: str
    producer_id: str
    subject_ref: str
    value: Any
    provider_run_ref: str | None = None

@dataclass(frozen=True)
class ObservationBatch:
    producer_id: str
    complete: bool
    observations: tuple[ObservationRecord, ...]

@dataclass(frozen=True)
class ImmutableArtifactLocator:
    provider: str
    native_id: str
    ref: str
    digest: str
    reviewer_resolvable: bool

class ArtifactStorePort(Protocol):
    def materialize(
        self, data: bytes, *, media_type: str, metadata: Mapping[str, Any]
    ) -> ImmutableArtifactLocator: ...

    def resolve(self, locator: ImmutableArtifactLocator) -> bytes: ...

class ExactRefResolverPort(Protocol):
    def resolve(self, ref: Mapping[str, Any]) -> Mapping[str, Any]: ...

class ResultMaterializationPort(Protocol):
    def resolve_result(self, result_ref: Mapping[str, Any]) -> Mapping[str, Any]: ...
```

`ObservationBatch` is transient and MUST NOT serialize as canonical Evidence by itself. No GitHub/network adapter is implemented here.

### 5.2 `tools/aegis_proof/evidence.py`

Implement:

```python
@dataclass(frozen=True)
class EvidenceRequirement:
    fact_key: str
    authoritative_producer: str
    required: bool

@dataclass(frozen=True)
class EvidencePlan:
    requirements: tuple[EvidenceRequirement, ...]

class EvidencePlanBuilder:
    def build(
        self,
        *,
        verification_spec: Mapping[str, Any],
        obligation_set: Mapping[str, Any],
        evidence_compilation_contract: Mapping[str, Any],
    ) -> EvidencePlan: ...

class EvidenceCompiler:
    def compile(
        self,
        *,
        plan: EvidencePlan,
        batches: Sequence[ObservationBatch],
    ) -> Mapping[str, Any]: ...

class EvidenceMaterializer:
    def materialize(
        self,
        evidence_artifact: Mapping[str, Any],
        *,
        store: ArtifactStorePort,
    ) -> Mapping[str, Any]: ...
```

Required behavior:

1. producer assignment is frozen by `EvidencePlan`;
2. conflicting non-authoritative/manual values cannot override authoritative structured values;
3. incomplete required producer batches mean missing evidence, never zero failures;
4. deterministic summaries/totals are derived from authoritative per-case/native summary records exactly once;
5. `EvidenceMaterializer` creates a new exact `EvidenceInputRef` from the external locator and does not mutate the EvidenceArtifact to insert its own future locator;
6. historical faulty EvidenceArtifact/EvidenceInputRef remains immutable;
7. a handoff/manifest summary remains derived navigation only and cannot become a second fact producer.

### 5.3 `tools/aegis_proof/evaluation.py`

Implement:

```python
@dataclass(frozen=True)
class EvaluationResult:
    proof_evaluation: Mapping[str, Any]
    verification_summary: Mapping[str, Any]

class ProofEvaluator:
    def evaluate(
        self,
        *,
        verification_spec: Mapping[str, Any],
        obligation_set: Mapping[str, Any],
        evidence_input_refs: Sequence[Mapping[str, Any]],
        evaluator_version: str,
    ) -> EvaluationResult: ...
```

Evaluation may produce only accepted proof states such as `SATISFIED / EXCEPTION / UNSATISFIED` according to the exact ProofContract semantics. It MUST NOT emit, imply, synthesize, or serialize official P34 Gate PASS.

### 5.4 `tools/aegis_proof/review.py`

Implement:

```python
class ReviewDelta(str, Enum):
    DECLARED = "DECLARED"
    EXISTING_REVIEW_ONLY = "EXISTING_REVIEW_ONLY"
    UNDECLARED = "UNDECLARED"
    STRUCTURALLY_UNSATISFIABLE = "STRUCTURALLY_UNSATISFIABLE"

@dataclass(frozen=True)
class CompletenessResult:
    complete: bool
    expected_ids: tuple[str, ...]
    actual_ids: tuple[str, ...]
    missing_ids: tuple[str, ...]
    unexpected_ids: tuple[str, ...]

class IndependentCompletenessChecker:
    def check(
        self,
        *,
        verification_spec: Mapping[str, Any],
        actual_obligation_set: Mapping[str, Any],
    ) -> CompletenessResult: ...

class ReviewContractDiffer:
    def classify(
        self,
        *,
        requested_requirement: Mapping[str, Any],
        verification_spec: Mapping[str, Any],
        package: Mapping[str, Any],
    ) -> ReviewDelta: ...

class ReviewBundleAdapter:
    def build(
        self,
        *,
        package_ref: Mapping[str, Any],
        result_ref: Mapping[str, Any],
        evidence_input_refs: Sequence[Mapping[str, Any]],
        proof_evaluation_ref: Mapping[str, Any],
        completeness: CompletenessResult,
    ) -> Mapping[str, Any]: ...
```

The completeness checker may reuse canonical subject/identity helpers from `domain.py`, but MUST NOT call `ObligationGenerator.generate()` or share its traversal implementation as the expected-set oracle.

`ReviewContractDiffer` classifies a newly requested Gate requirement against the frozen spec/package. `UNDECLARED` and `STRUCTURALLY_UNSATISFIABLE` are not converted into historical P32 repair obligations.

`ReviewBundleAdapter` is navigation/projection only. It cannot issue Gate PASS and cannot make an unresolved result/evidence identity review-ready.

---

## 6. Exact deterministic verification subset for VP-I02

The P20 ECV0 meanings are frozen. P32 must implement and execute these scenarios:

```yaml
EC-S01:
  input: authoritative structured test source says 445 PASS / 23 SKIP while manual evidence says 25 SKIP
  required: conflicting manual value cannot override authoritative structured truth

EC-S04:
  input: P34 requests a new Gate-critical field absent from frozen spec/package
  required: classify UNDECLARED and route to owning earlier layer, not old P32 repair

EC-S05:
  input: implementation result unchanged while faulty evidence is externally rematerialized
  required: new EvidenceInputRef + new ProofEvaluation may retain the same result identity

EC-S06:
  input: evidence repair requires modifying a byte/file inside the result commit
  required: result SHA changes; same-result claim is rejected

EC-S14:
  input: handoff/manifest copied proof totals conflict with exact EvidenceArtifact/ProofEvaluation
  required: copied totals remain non-authoritative

EC-S15:
  input: ProofEvaluation appears clean but generated obligation set omitted an expected obligation
  required: independent completeness detects the omission and review cannot PASS

EC-S16:
  input: CI is green and ProofEvaluation has zero UNSATISFIED, but exact result materialization cannot be independently resolved
  required: not review-ready / blocked evidence
```

Mandatory purpose-built mutants:

```yaml
EC-M01: accept manual 25 SKIP over authoritative 23 SKIP
EC-M04: convert undeclared P34 field into old P32 repair obligation
EC-M05: change result commit during evidence-only repair while reporting old result SHA
EC-M13: treat green CI / ProofEvaluation as official Gate PASS
EC-M14: let handoff summary override exact EvidenceArtifact/ProofEvaluation totals
EC-M15: use generator output as sole completeness expected-set oracle
EC-M17: treat missing/incomplete producer/provider data as zero failures
```

Every mutant above MUST be instantiated and machine-detected. Purpose-built negative fixtures are sufficient; no general mutation framework is authorized.

For `EC-M15`, the focused test MUST monkeypatch/replace `ObligationGenerator.generate()` with a raising stub while executing `IndependentCompletenessChecker.check()`. A passing completeness check that never invokes the generator demonstrates traversal independence; merely comparing two outputs produced by the same generator is insufficient.

---

## 7. Test ownership / TDD plan

P32 uses test-first RED -> minimal GREEN. Before production implementation, add failing tests that demonstrate the missing VP-I02 behavior against the exact accepted predecessor.

Recommended ownership is frozen as follows so P32 does not redistribute semantics arbitrarily:

### `test_evidence_compiler.py`

Own at least:

```text
EC-S01
EC-S14
EC-M01
EC-M14
EC-M17
```

It must also cover incomplete required producer batches as missing evidence rather than clean/zero-failure evidence.

### `test_evidence_repair.py`

Own at least:

```text
EC-S05
EC-S06
EC-M05
```

It must prove evidence identity and result identity remain distinct.

### `test_evaluation_review.py`

Own at least:

```text
EC-S04
EC-S15
EC-S16
EC-M04
EC-M13
EC-M15
```

It must prove ProofEvaluation is not a Gate and the completeness expected-set traversal is independent.

If a different distribution among these three authorized test files is mechanically simpler, it is allowed only when all exact scenario/mutant identities remain explicit in test names/fixtures and no semantic requirement is weakened or omitted.

### Focused command

```bash
python3 -m unittest \
  tests.verification_productization.test_evidence_compiler \
  tests.verification_productization.test_evidence_repair \
  tests.verification_productization.test_evaluation_review -v
```

### Accumulated Verification Productization regression

```bash
python3 -m unittest discover -s tests/verification_productization -v
```

### Inherited regressions

```bash
python3 -m unittest discover -s tests/control_plane -v
python3 -m unittest discover -s tests/project_state -v
python3 -m unittest discover -s tests/skillset -v
```

No P18 performance profile is required for this correctness slice.

---

## 8. P32 evidence/materialization contract

P32 may return to CONTROL_REVIEW only after all required execution evidence is durable and independently resolvable.

### Exact result materialization

1. push the exact VP-I02 implementation result to a branch in `Mostorm-Labs/aegis`;
2. expose the exact result through a reviewer-resolvable Draft implementation PR based on the final P31 package branch;
3. return exact `result_revision`, PR/materialized ref, actual starting revision, and authored changed paths;
4. preserve PR #73 and its final P31 head as immutable package authorization input.

### Focused RED/GREEN + mutant evidence

Because this P31 does **not** authorize workflow changes, P32 MUST NOT pretend that the existing Control Plane workflows execute the new VP-I02 focused suite when they do not.

The focused RED/GREEN and mandatory mutant execution must be materialized through one of these exact durable topologies:

- an applicable provider-native immutable artifact bound to the exact result; or
- a dedicated external evidence commit/branch whose parent/basis is the exact result and whose only added bytes are machine execution records under `artifacts/verification-productization/vp-i02/**`.

External evidence materialization is not implementation authored scope and MUST NOT change the implementation result revision.

The durable focused record must preserve, without manually retyping derived totals:

```yaml
subject_result_revision: REQUIRED
source_blob_identities: REQUIRED
command: REQUIRED
interpreter_environment: REQUIRED
exit_code: REQUIRED
raw_machine_output_or_per_test_records: REQUIRED
scenario_ids: [EC-S01, EC-S04, EC-S05, EC-S06, EC-S14, EC-S15, EC-S16]
mutant_ids: [EC-M01, EC-M04, EC-M05, EC-M13, EC-M14, EC-M15, EC-M17]
```

It must explicitly remain distinct from ProofEvaluation and P34 Gate Decision.

### Hosted regression evidence

Resolve every GitHub Actions workflow run applicable to the exact implementation result. Preserve provider-native run/job/artifact identities and exact result applicability. Any required existing hosted regression failure is a blocker.

A PR merge-ref run may be accepted for content applicability only if reviewer-verifiable Git tree/content identity proves it corresponds to the exact candidate bytes.

### No manual proof totals

P32/P33/P36 returns may summarize status but MUST NOT invent or independently author proof totals already owned by EvidenceArtifact/ProofEvaluation/raw execution records.

---

## 9. Exact P32 exit criteria

VP-I02 is review-ready only when all of the following are established:

```yaml
repository_identity_preflight: PASS
package_ref_resolved_in_declared_repository: true
task_anchor_relation: ancestor
accepted_vp_i01_predecessor_relation: ancestor
scope_deviation: none
authority_deviation: none

EC-S01: PASS
EC-S04: PASS
EC-S05: PASS
EC-S06: PASS
EC-S14: PASS
EC-S15: PASS
EC-S16: PASS

EC-M01_detected: true
EC-M04_detected: true
EC-M05_detected: true
EC-M13_detected: true
EC-M14_detected: true
EC-M15_detected: true
EC-M17_detected: true
mutant_false_acceptance: 0

authoritative_fact_override: 0
post_hoc_requirement_misrouted_to_p32: 0
same_result_false_claim_after_result_mutation: 0
incomplete_obligation_set_false_complete: 0
non_p34_gate_pass_emission: 0
incomplete_required_data_false_clean: 0

focused_vp_i02_exit_code: 0
verification_productization_regression_failures: 0
control_plane_regression_failures: 0
project_state_regression_failures: 0
skillset_regression_failures: 0
hosted_required_failures: 0

result_revision: REQUIRED
materialized_ref: REQUIRED
durable_focused_execution_refs: REQUIRED
unresolved_required_refs: 0
P34_claimed_by_P32: false
```

A clean ProofEvaluation, green CI, or executor prose is insufficient to satisfy P34. P34 remains the sole formal Gate owner.

---

## 10. Fail-closed blocked returns

Use the most specific existing blocker and stop rather than widening this package:

```text
repository/package identity mismatch
  -> BLOCKED_REPOSITORY_IDENTITY

stable task-anchor or accepted predecessor ancestry conflict
  -> BLOCKED_EXECUTION_DIVERGENCE

accepted P12/P15/P17/P20/VP-I01 meaning missing or contradictory
  -> BLOCKED_AUTHORITY

required exact input/ref missing
  -> BLOCKED_MISSING_INPUT

unresolved semantic choice
  -> BLOCKED_UNRESOLVED_DECISION

defect inside one of the eight authorized implementation paths
  -> BLOCKED_IMPLEMENTATION

required source mutation outside the eight-path set
  -> BLOCKED_IMPLEMENTATION / P31_PACKAGE_SCOPE_DEFECT
     and request a replacement P31 package

required durable proof cannot be materialized/resolved
  -> BLOCKED_EVIDENCE

provider/runtime prevents required execution
  -> BLOCKED_ENVIRONMENT
```

If a failing scenario indicates P20/P15/P17 semantics themselves are wrong or insufficient, do not locally reinterpret them. Return to the earlier owning Authority layer.

---

## 11. Explicit non-goals

VP-I02 does not authorize:

- GitHub Actions, local-runner, repository, or network provider adapters;
- structured CLI / `__main__.py`;
- canonical Skill source changes or generated Skill distribution;
- published Plugin mutation;
- `.aegis` Authority/Gate/Integration publication;
- release/tag/manifest mutation;
- new service/daemon/database/queue/third-party dependency;
- P18 performance work;
- VP-I03;
- merging PR #70/#71/#72/#73 or any upstream Draft Authority stack;
- P34 PASS by implementation.

---

## 12. P31 disposition

```yaml
P31_package:
  package_id: VP-I02-P31-01
  slice_id: VP-I02
  repository: Mostorm-Labs/aegis
  package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/73

  task_anchor:
    revision: 674e01737621621b8131e35f83313fb0154a9f6d
    relation: ancestor

  resume_cursor: null

  accepted_predecessor:
    result_revision: ef995501c3dcd1f7f608083028f43bb4bde66103
    p34_review: 5121366259
    p24_review: 5121383523

  authorization_mode: EXACT_PATH_SET
  authored_path_count: 8

  status: MATERIALIZED_READY_FOR_EXPLICIT_P32_START
  p32_started: false
  p34_pass_issued: false
  merge_authorized: false
  release_authorized: false
  vp_i03_started: false

  next_owner: aegis-implementation
  next_stage: P32_IMPLEMENTATION
```

Only the **final PR #73 head after this document is materialized** is the executable `package_ref`. The historical shell commit is permanently non-executable.
