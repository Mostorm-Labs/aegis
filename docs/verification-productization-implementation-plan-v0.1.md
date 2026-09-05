# Aegis Verification Productization v0.1 — P30 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:test-driven-development` for implementation and `superpowers:verification-before-completion` before any completion claim. Use `superpowers:using-git-worktrees` before repository-heavy P32 execution when isolation is needed.

**Stage:** `P30 Implementation Planning`

**Owner:** `aegis-implementation`

**Goal:** Implement the smallest reusable Proof Runtime and integration surface that closes the Evidence Contract Churn incident family and can satisfy the accepted `ECV0` Verification profile without creating a new verification service, hidden daemon, second source of proof truth, or PP0-style framework.

**Architecture:** Add one new Python package, `tools/aegis_proof`, for the deterministic Proof Plane runtime defined by P15-P17. Keep Control Plane canonical package truth in `tools/aegis_control`, keep provider/platform behavior behind explicit adapters, and keep lifecycle/Gate ownership in existing Aegis Skills. Implement in three evidence-gated vertical slices so each slice can be independently reviewed and, if necessary, repaired without reopening accepted upstream design.

**Tech Stack:** Python 3.12 standard library, `unittest`, existing `tools/aegis_control`, existing `tools/aegis_skillset`, GitHub Actions, repository/Skill distribution scripts already present in `scripts/`.

**Spec:**

- `docs/verification-productization-model-v0.1.md`
- `docs/verification-productization-model-v0.1-p21-repair.md`
- `docs/verification-productization-model-v0.1-p15-preflight-p12-repair.md`
- `docs/verification-productization-architecture-v0.1.md`
- `docs/verification-productization-architecture-v0.1-p12-reconciliation.md`
- `docs/verification-productization-modules-v0.1.md`
- `docs/verification-productization-runtime-flow-v0.1.md`
- `docs/verification-productization-platform-contract-v0.1.md`
- `docs/verification-productization-verification-v0.1.md`

## Global exact basis

```yaml
repository:
  provider: github
  full_name: Mostorm-Labs/aegis

main_baseline: 342d6785d8f54dd9beb2c3bb82398f29b405df2f
semantic_basis: 12c968c5c481ad671ce33bcfa088ba8a2fca0f43
semantic_p21_recertification: 5121012716
p14_basis: d9c8f6ac5db4359400fae06e76c51c65bd059bfc
p15_basis: 665292dcfd7781935243369ee9f676c320f2878a
p16_basis: 708cf09c01effbcc63c65d45b9b4a67b7a8fc8db
p17_basis: c8f47d049be50d65f88b04ad141650ed6dfdb826
p20_basis: 674e01737621621b8131e35f83313fb0154a9f6d
p20_p21_review: 5121075377

future_p31_task_anchor:
  revision: 674e01737621621b8131e35f83313fb0154a9f6d
  relation: ancestor
```

The P30/P31 materialization commits are expected descendants of the task anchor. Future P32 MUST validate ancestry, not historical HEAD equality.

## Global constraints

1. `machine observation != EvidenceArtifact/EvidenceInputRef != implementation result != ProofEvaluation != P34 Gate Decision`.
2. `Repository Identity != Task Anchor != Execution Cursor`.
3. No canonical `ProofFact`, `EvidenceManifest`, or `MaterializationEnvelope` aggregate is added.
4. Machine-observable facts have one authoritative producer; copied totals never become a second source of truth.
5. Gate-critical accepted dependencies are exact before P32. Floating labels such as `accepted A4`, `latest Gate`, `current result`, or `previous accepted baseline` are rejected before execution.
6. Evidence contracts are satisfiable before P32. Future-self commit/ref cycles are rejected rather than pushed to the executor.
7. Result identity and evidence identity remain separate. Evidence-only repair may preserve a result revision only when evidence rematerializes externally without mutating result bytes.
8. P34 remains the sole formal Gate owner. ProofEvaluation, green CI, execution return prose, and summary manifests cannot issue PASS.
9. Review completeness traversal must not call the Obligation Generator traversal as its expected-set oracle.
10. Local filesystem/worktree paths are staging only. Required review evidence must become reviewer-resolvable at an exact durable ref.
11. Credentials and temporary signed URLs never become durable proof identity.
12. `plugins/aegis/**` published `0.1.0-beta.3` materialization is immutable and MUST NOT be rewritten by this implementation. Candidate Plugin parity uses `scripts/build_candidate_plugin_parity.py`.
13. No new service, daemon, external database, third-party Python dependency, performance profile, release, merge, Authority publication, or rollout expansion is authorized.
14. Existing Control Plane, Project State, and Skillset regression suites remain required throughout implementation.

---

# 1. Repository implementation reality and placement decision

Current implementation reality contains:

```text
tools/aegis_control
tools/aegis_skillset
tools/aegis_state
```

There is no Proof Runtime package today. `tools/aegis_control/canonical.py` already recognizes `VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE` at the top-level record shape, but the accepted downstream contract requires deeper validation of exact TrustedBasis / verification bindings / package digest plus proof-specific projection and satisfiability checks.

P30 therefore freezes this placement:

```text
tools/aegis_control
  owns Control Plane canonical package shape and existing lifecycle/runtime truth

             exact CanonicalRef / package bridge
                         |
                         v

tools/aegis_proof
  owns deterministic Proof Plane parsing, obligation generation,
  package/evidence preflight, evidence compilation, evaluation,
  completeness/review support, and provider-neutral DTOs

             structured adapters / exact refs
                         |
                         v

Codex / local runner / GitHub Actions / GitHub / CONTROL_REVIEW
```

`tools/aegis_proof` may reuse the canonical JSON/digest primitives in `tools/aegis_control.canonical`; it must not import Control Plane mutation/dispatch logic.

---

# 2. P31 packaging decision

P30 chooses **three** sequential P31 candidates. This is the minimum split that keeps each review meaningful without creating a high-overhead package per module.

```text
VP-I01  Exact Contract & Package Preflight
   |
   v
VP-I02  Evidence Compilation & Independent Review Runtime
   |
   v
VP-I03  Platform / Skill Integration & ECV0 Qualification
```

Rules:

- each candidate gets a separate P31 package and exact package revision;
- each package uses `674e017...` as the stable task-anchor ancestry root unless a later accepted upstream Authority supersedes the basis;
- downstream slice execution does not begin until the preceding slice has a valid accepted result/Gate basis required by its package;
- P31 freezes the exact generated-file scope after canonical Skill edits are known; P30 does not authorize wildcard mutation of published Plugin materialization;
- P32 is not authorized by this P30 document.

---

# 3. Slice VP-I01 — Exact Contract & Package Preflight

## Purpose

Build the deterministic trust-boundary kernel required before any proof/evidence execution. This slice closes the two highest-leverage pre-execution incident classes: **R2 floating accepted dependency** and **R3 self-referential/unsatisfiable evidence contract**.

## Files

**Create:**

- `tools/aegis_proof/__init__.py`
- `tools/aegis_proof/domain.py`
- `tools/aegis_proof/spec.py`
- `tools/aegis_proof/obligations.py`
- `tools/aegis_proof/package.py`
- `tests/verification_productization/__init__.py`
- `tests/verification_productization/test_domain_spec.py`
- `tests/verification_productization/test_package_preflight.py`

**Modify:**

- `tools/aegis_control/canonical.py`

No Skill source, workflow, Plugin tree, `.aegis` registry, or provider adapter changes belong in this slice.

## Interfaces frozen by P30

### `tools/aegis_proof/domain.py`

```python
class ProofValidationError(ValueError):
    pass

class ProofCodec:
    @staticmethod
    def canonicalize(value: Mapping[str, Any]) -> bytes: ...

    @staticmethod
    def digest(value: Mapping[str, Any]) -> str: ...

class ObligationIdentityCodec:
    @staticmethod
    def semantic_key(
        *,
        verification_spec_digest: str,
        subject_kind: str,
        subject_id: str,
        obligation_kind: str,
        source_key: str,
    ) -> str: ...

    @staticmethod
    def id_from_key(key: str) -> str: ...

class EvidenceInputIdentity:
    @staticmethod
    def from_materialized_artifact(
        *, evidence_id: str, ref: str, digest: str, producer_class: str
    ) -> Mapping[str, Any]: ...
```

`ProofCodec` reuses accepted canonical JSON/JCS helpers from `tools.aegis_control.canonical`; it does not implement a second canonicalizer.

### `tools/aegis_proof/spec.py`

```python
@dataclass(frozen=True)
class ValidationFinding:
    code: str
    path: str
    detail: str

@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    findings: tuple[ValidationFinding, ...]

class VerificationSpecValidator:
    def validate(self, spec: Mapping[str, Any]) -> ValidationResult: ...
```

The validator enforces accepted `CoverageBasis`, `CLAIM | COVERAGE_BASIS` subject shape, resolved ProofContract structure, exact profile/version identity where present, and unknown-required-value fail-closed behavior. It does not make semantic risk decisions.

### `tools/aegis_proof/obligations.py`

```python
@dataclass(frozen=True)
class ObligationSet:
    verification_spec_digest: str
    coverage_basis_digest: str
    generator_version: str
    obligations: tuple[Mapping[str, Any], ...]
    obligation_set_digest: str

class ObligationGenerator:
    def generate(
        self,
        *,
        verification_spec: Mapping[str, Any],
        generator_version: str,
    ) -> ObligationSet: ...
```

Required behavior:

- exact validated spec only;
- preserve `CLAIM | COVERAGE_BASIS` subject;
- `REVIEW_DECLARED` generates exactly one required CoverageBasis completeness obligation;
- review-required obligations stay in the complete set;
- no obligation may be marked SATISFIED here.

### `tools/aegis_proof/package.py`

```python
class PreflightCode(str, Enum):
    OK = "OK"
    FLOATING_DEPENDENCY = "FLOATING_DEPENDENCY"
    UNRESOLVABLE_EXACT_REF = "UNRESOLVABLE_EXACT_REF"
    CONTRACT_IDENTITY_MISMATCH = "CONTRACT_IDENTITY_MISMATCH"
    STRUCTURALLY_UNSATISFIABLE = "STRUCTURALLY_UNSATISFIABLE"
    PROVIDER_PHASE_UNAVAILABLE = "PROVIDER_PHASE_UNAVAILABLE"
    REVIEW_DEPENDENCY_IN_EXECUTION = "REVIEW_DEPENDENCY_IN_EXECUTION"

@dataclass(frozen=True)
class PreflightFinding:
    code: PreflightCode
    path: str
    detail: str

@dataclass(frozen=True)
class PreflightResult:
    ready: bool
    findings: tuple[PreflightFinding, ...]

class P31TaskProjector:
    def project(
        self,
        *,
        verification_spec_ref: Mapping[str, Any],
        obligation_set_ref: Mapping[str, Any] | None,
        scope_contract_ref: Mapping[str, Any],
        acceptance_oracle_refs: Sequence[Mapping[str, Any]],
        evidence_compilation_contract_ref: Mapping[str, Any],
        trusted_basis: Mapping[str, Any],
        policy_binding: Mapping[str, Any],
        task_anchor: Mapping[str, Any],
    ) -> Mapping[str, Any]: ...

class PackageBindingPreflight:
    def check(
        self,
        package: Mapping[str, Any],
        *,
        exact_ref_resolver: Callable[[Mapping[str, Any]], bool],
    ) -> PreflightResult: ...

class EvidenceContractPreflight:
    def check(
        self,
        requirements: Sequence[Mapping[str, Any]],
        *,
        provider_capabilities: Mapping[str, bool],
    ) -> PreflightResult: ...
```

The evidence preflight uses a transient phase graph with exactly these ordered phase names:

```text
P31_FREEZE
P32_EXECUTION
EVIDENCE_COMPILE
ARTIFACT_MATERIALIZE
RESULT_MATERIALIZE
P34_REVIEW
```

It rejects future-self identity cycles, review-produced values required during P32, mutable-only trust identities, and provider-impossible required fields.

### `tools/aegis_control/canonical.py`

Add and call package-specific nested validators from `validate_record()`:

```python
def validate_trusted_basis(value: Mapping[str, Any]) -> None: ...
def validate_verification_binding(value: Mapping[str, Any]) -> None: ...
def validate_verification_bound_package(record: Mapping[str, Any]) -> None: ...
```

They must enforce:

- exact expected field sets;
- CanonicalRef object-type restrictions;
- non-empty required arrays where mandated by accepted P12;
- deterministic `basis_digest` validation;
- exact `scope_contract_ref` / `verification_spec_ref` / acceptance-oracle / evidence-compilation-contract types;
- task anchor shape when non-null;
- `package_digest == canonical_digest(record, self_digest_field="package_digest")`.

## TDD / proof steps

- [ ] Add failing canonical package tests showing a top-level-shape-valid package with an invalid/floating nested verification ref is currently accepted.
- [ ] Run `python3 -m unittest tests.verification_productization.test_package_preflight -v` and record the expected failure.
- [ ] Implement nested Control Plane package validation and the `tools.aegis_proof` domain/spec/obligation/package kernel.
- [ ] Add exact regression fixtures for `EC-S02`, `EC-S03`, `EC-M02`, and `EC-M03`.
- [ ] Verify floating `accepted A4` / `latest Gate` is rejected before P32.
- [ ] Verify an artifact contract requiring its own future containing commit SHA returns `STRUCTURALLY_UNSATISFIABLE`.
- [ ] Run focused tests:

```bash
python3 -m unittest \
  tests.verification_productization.test_domain_spec \
  tests.verification_productization.test_package_preflight -v
```

- [ ] Run inherited Control Plane regressions:

```bash
python3 -m unittest discover -s tests/control_plane -v
```

- [ ] Confirm no file under `plugins/aegis/**`, `skillset/**`, `skills/**`, or `.aegis/**` changed in this slice.

## Slice exit / Gate claim

VP-I01 is review-ready only when:

```yaml
EC-S02: PASS
EC-S03: PASS
EC-M02_detected: true
EC-M03_detected: true
floating_dependency_admitted_to_p32: 0
future_self_contract_admitted_to_p32: 0
control_plane_regression_failures: 0
```

A failure that requires changing P12/P15/P17/P20 semantics is `BLOCKED_AUTHORITY`, not a local implementation repair.

---

# 4. Slice VP-I02 — Evidence Compilation & Independent Review Runtime

## Purpose

Implement the deterministic evidence/evaluation/review core after exact package truth is trusted. This slice closes **R1 authoritative fact mismatch**, **R4 post-hoc schema expansion**, **R5 evidence-only repair**, and the independent completeness boundary.

## Dependency

Requires an accepted VP-I01 result and exact package/preflight API compatibility.

## Files

**Create:**

- `tools/aegis_proof/ports.py`
- `tools/aegis_proof/evidence.py`
- `tools/aegis_proof/evaluation.py`
- `tools/aegis_proof/review.py`
- `tests/verification_productization/test_evidence_compiler.py`
- `tests/verification_productization/test_evidence_repair.py`
- `tests/verification_productization/test_evaluation_review.py`

**Modify only if required by the already-frozen public exports:**

- `tools/aegis_proof/__init__.py`

No GitHub/network adapter, workflow, Skill distribution, published Plugin tree, or `.aegis` mutation belongs in this slice.

## Interfaces frozen by P30

### `tools/aegis_proof/ports.py`

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

`ObservationBatch` is transient and never serializes as canonical Evidence by itself.

### `tools/aegis_proof/evidence.py`

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

Rules:

- producer assignment is frozen by `EvidencePlan`;
- conflicting non-authoritative/manual values cannot override authoritative machine values;
- incomplete required producer batches are missing evidence, never zero failures;
- deterministic summary counts are derived from authoritative per-case/native summary records exactly once;
- `EvidenceMaterializer` produces a new exact `EvidenceInputRef`; it does not mutate the EvidenceArtifact to insert a future locator;
- historical faulty EvidenceArtifact / EvidenceInputRef remains immutable.

### `tools/aegis_proof/evaluation.py`

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

Evaluation may produce `SATISFIED / EXCEPTION / UNSATISFIED` according to accepted ProofContract semantics. It cannot emit Gate PASS.

### `tools/aegis_proof/review.py`

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

The independent completeness traversal may reuse only canonical subject/identity helpers from `domain.py`; it MUST NOT call `ObligationGenerator.generate()` or share its traversal implementation.

## TDD / proof steps

- [ ] Write failing `EC-S01` test: authoritative structured source says `445 PASS / 23 SKIP`; manual summary says `25 SKIP`; compiler must reject/ignore the manual conflict and preserve authoritative truth.
- [ ] Write failing `EC-S04` test for an undeclared P34 field.
- [ ] Write `EC-S05` and `EC-S06` as paired evidence-only repair tests: external rematerialization preserves result identity; repository-result byte mutation does not.
- [ ] Write independent completeness test `EC-S15` and mutant `EC-M15`; monkeypatch/replace `ObligationGenerator.generate()` with a raising stub during the completeness check to prove the review traversal does not depend on it.
- [ ] Write `EC-S16` showing clean ProofEvaluation cannot make an unresolvable result review-ready.
- [ ] Add mutants `EC-M01`, `EC-M04`, `EC-M05`, `EC-M13`, `EC-M14`, `EC-M15`, and `EC-M17`.
- [ ] Implement minimal evidence/evaluation/review code to make focused tests pass.
- [ ] Run:

```bash
python3 -m unittest \
  tests.verification_productization.test_evidence_compiler \
  tests.verification_productization.test_evidence_repair \
  tests.verification_productization.test_evaluation_review -v
```

- [ ] Run all Verification Productization tests accumulated so far:

```bash
python3 -m unittest discover -s tests/verification_productization -v
```

- [ ] Run inherited regressions:

```bash
python3 -m unittest discover -s tests/control_plane -v
python3 -m unittest discover -s tests/project_state -v
python3 -m unittest discover -s tests/skillset -v
```

## Slice exit / Gate claim

VP-I02 is review-ready only when at least these accepted incident/proof conditions are demonstrably closed:

```yaml
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
authoritative_fact_override: 0
post_hoc_requirement_misrouted_to_p32: 0
same_result_false_claim_after_result_mutation: 0
incomplete_obligation_set_false_complete: 0
non_p34_gate_pass_emission: 0
```

---

# 5. Slice VP-I03 — Platform / Skill Integration & ECV0 Qualification

## Purpose

Connect the deterministic Proof Runtime to the actual Aegis execution surfaces and prove the complete ECV0 profile without duplicating semantics in workflow YAML, prompts, or hand-written summary JSON.

## Dependency

Requires accepted VP-I01 and VP-I02 results.

## Files

**Create:**

- `tools/aegis_proof/adapters/__init__.py`
- `tools/aegis_proof/adapters/local_runner.py`
- `tools/aegis_proof/adapters/github_actions.py`
- `tools/aegis_proof/adapters/repository.py`
- `tools/aegis_proof/cli.py`
- `tools/aegis_proof/__main__.py`
- `tests/verification_productization/ecv0_fixtures.py`
- `tests/verification_productization/test_provider_adapters.py`
- `tests/verification_productization/test_cli_parity.py`
- `tests/verification_productization/test_ecv0_scenarios.py`
- `tests/verification_productization/test_ecv0_mutants.py`
- `tests/verification_productization/run_ecv0.py`
- `.github/workflows/verification-productization-ecv0.yml`

**Modify canonical Skill sources:**

- `skillset/shared/handoff-contract.md`
- `skillset/skills/aegis-implementation/SKILL.md`
- `skillset/skills/aegis-implementation/references/implementation-control.md`
- `skillset/skills/aegis-gate-review/SKILL.md`
- `skillset/skills/aegis-gate-review/references/gate-review.md`

**Generated outputs:**

- mechanically regenerated `skills/**` files selected by `skillset/distribution.json` from the canonical source changes above, using `python3 scripts/build_skillset.py --write`;
- exact generated paths must be captured in the P31 package/result diff rather than hand-maintained in this plan.

**Explicitly excluded:**

- `plugins/aegis/**` published beta.3 materialization;
- release manifests/tags/releases;
- `.aegis/authorities.json`, `.aegis/gates.json`, `.aegis/integrations.json` publication changes.

## Adapter contracts

### `local_runner.py`

Converts one completed local process/report into `ObservationBatch` only after:

- process termination;
- required structured report finalization;
- complete expected record set/end condition.

A truncated process/report returns `complete=False`; it never synthesizes zero failures.

### `github_actions.py`

Consumes provider-qualified GitHub Actions run/job metadata and produces structured observation/applicability facts using:

```text
repository.full_name
workflow identity
run_id
run_attempt
exact result/source revision
required job identities
required matrix child identities
terminal job/run conclusions when externally observable
```

It rejects:

- wrong revision;
- `latest` without exact run identity;
- missing required job/matrix child;
- incomplete run/job state;
- artifact-name-only identity.

The same CI artifact MUST NOT be required to embed the future terminal conclusion of the run that uploads it. P34 resolves run terminal/completeness state externally by exact run/job identity.

### `repository.py`

Represents exact repository artifact/result bindings. Repository locator identity includes repository namespace + exact commit/native object + path/native ID + digest where the governing contract requires it. Branch/PR names remain navigation unless paired with exact selected identity.

## Structured CLI

`python3 -m tools.aegis_proof` must expose deterministic JSON-in/JSON-out subcommands:

```text
validate-spec
build-obligations
project-package
preflight-package
preflight-evidence
compile-evidence
evaluate
review-check
```

Rules:

- input files are UTF-8 JSON;
- stdout emits only one structured JSON result for machine consumption;
- human diagnostics go to stderr;
- nonzero exit means contract/validation/runtime failure and does not rewrite semantic truth;
- CLI calls the same library functions as unit tests; it does not reimplement proof rules.

`test_cli_parity.py` compares canonical semantic outputs from direct library invocation versus CLI invocation for the same exact fixtures (`EC-S17`).

## Skill integration changes

### `aegis-implementation`

The canonical Skill/ref must explicitly require before repository-backed P32:

1. exact VerificationSpec / obligation-set / TrustedBasis / scope / acceptance-oracle / evidence-compilation bindings;
2. `PackageBindingPreflight` success;
3. `EvidenceContractPreflight` success;
4. repository identity preflight before package/anchor/cursor resolution;
5. no floating accepted labels passed to Codex;
6. no manually typed proof totals in the execution return when EvidenceArtifact/ProofEvaluation owns those facts;
7. return exact `result_revision`, `materialized_ref`, `evidence_input_refs`, and exact provider run refs required by the package.

### `aegis-gate-review`

The canonical Skill/ref must explicitly require P34 to:

1. independently resolve exact package/result/evidence/provider identities;
2. establish provider run applicability and completion;
3. establish independent obligation completeness;
4. apply `ReviewContractDiffer` when a new Gate requirement appears;
5. classify `UNDECLARED` / `STRUCTURALLY_UNSATISFIABLE` requirements to the owning earlier layer rather than bouncing them to P32;
6. never treat ProofEvaluation/green CI/summary prose as Gate PASS.

### Shared handoff contract

The execution-return example must carry exact refs/navigation only. It may contain:

```yaml
result_revision: <exact result>
materialized_ref: <reviewer-resolvable exact result ref>
evidence_input_refs:
  - <exact EvidenceInputRef>
provider_run_refs:
  - <exact provider run identity>
```

It must not introduce manually typed duplicated fields such as `tests_passed`, `tests_skipped`, or copied ProofEvaluation totals.

## ECV0 deterministic corpus

`tests/verification_productization/test_ecv0_scenarios.py` must materialize all exact scenarios `EC-S01..EC-S17` from P20.

`tests/verification_productization/test_ecv0_mutants.py` must materialize all exact mutants `EC-M01..EC-M17` from P20.

`run_ecv0.py` must produce a structured artifact from per-case records. Aggregate values are computed by the runner and never passed as free-authored command-line totals.

Required output shape:

```json
{
  "profile": "ECV0",
  "source_revision": "<runtime-resolved git HEAD>",
  "scenario_records": [{"id": "EC-S01", "verdict": "PASS"}],
  "mutant_records": [{"id": "EC-M01", "detected": true}],
  "derived_summary": {
    "scenario_required": 17,
    "scenario_pass": 17,
    "mutant_required": 17,
    "mutant_detected": 17,
    "mutant_false_acceptance": 0
  }
}
```

The example numbers above are acceptance targets; the runner must derive them from exact records and fail nonzero when targets are not met.

## GitHub Actions workflow

`.github/workflows/verification-productization-ecv0.yml` must:

1. checkout the exact candidate;
2. use Python `3.12`;
3. run `python3 -m unittest discover -s tests/verification_productization -v`;
4. run inherited Control Plane / Project State / Skillset regressions;
5. run `python3 scripts/build_skillset.py --check`;
6. run `python3 -m tools.aegis_skillset.cli distribution-check .`;
7. run `python3 tests/verification_productization/run_ecv0.py --output artifacts/ecv0/ecv0.json`;
8. run `python3 scripts/build_candidate_plugin_parity.py --output artifacts/ecv0/candidate-plugin-parity.json`;
9. validate both JSON outputs with `python3 -m json.tool`;
10. upload the artifacts with an exact-candidate-qualified artifact name and finite retention;
11. never modify `plugins/aegis/**` or create a release.

The workflow does not self-certify its final P34 applicability. CONTROL_REVIEW resolves the exact run ID/attempt, terminal conclusion, required jobs, artifact identity, and exact result revision externally.

## Fresh platform corroboration plan

The final VP-I03 package must require four exact candidate observations from P20:

```text
EC-PFC01 Codex repository / exact package preflight
EC-PFC02 Codex/local evidence durability boundary
EC-PFC03 GitHub Actions exact-result + completion applicability
EC-PFC04 CONTROL_REVIEW independent resolution
```

Disposition by production surface:

- `EC-PFC01`: actual Codex P32/P33 observation; not simulated by repository unit tests.
- `EC-PFC02`: actual Codex execution return proving local-only artifact is not called review-ready before materialization.
- `EC-PFC03`: exact hosted workflow run + independently resolved run/jobs/artifact/result identity.
- `EC-PFC04`: fresh CONTROL_REVIEW resolution using exact provider/repository refs; not executor prose.

These observations become durable evidence refs. Their pass/fail totals are not manually copied into a competing evidence JSON.

## Skill generation / parity commands

After canonical Skill source edits:

```bash
python3 scripts/build_skillset.py --write
python3 scripts/build_skillset.py --check
python3 scripts/validate_generated_skills.py
python3 -m tools.aegis_skillset.cli validate .
python3 -m tools.aegis_skillset.cli routing-check .
python3 -m tools.aegis_skillset.cli distribution-check .
```

Candidate Plugin parity:

```bash
python3 scripts/build_candidate_plugin_parity.py \
  --output artifacts/ecv0/candidate-plugin-parity.json
```

The command output is evidence about the current candidate only; it does not authorize publication.

## Full qualification commands

```bash
python3 -m unittest discover -s tests/verification_productization -v
python3 -m unittest discover -s tests/control_plane -v
python3 -m unittest discover -s tests/project_state -v
python3 -m unittest discover -s tests/skillset -v
python3 scripts/build_skillset.py --check
python3 -m tools.aegis_skillset.cli distribution-check .
python3 tests/verification_productization/run_ecv0.py \
  --output artifacts/ecv0/ecv0.json
python3 -m json.tool artifacts/ecv0/ecv0.json >/dev/null
python3 scripts/build_candidate_plugin_parity.py \
  --output artifacts/ecv0/candidate-plugin-parity.json
python3 -m json.tool artifacts/ecv0/candidate-plugin-parity.json >/dev/null
```

No completion claim may be made without fresh outputs from the full applicable command set at the exact result revision.

## Final ECV0 acceptance target

```yaml
deterministic_scenarios:
  required: 17
  pass: 17
  fail: 0

mutant_qualification:
  required: 17
  detected: 17
  undetected: 0
  false_acceptance: 0

fresh_platform_corroboration:
  required: 4
  pass: 4
  fail: 0

zero_tolerance_events:
  authoritative_fact_override: 0
  floating_dependency_executed: 0
  unsatisfiable_contract_admitted_to_p32: 0
  post_hoc_requirement_misrouted_to_p32: 0
  same_result_false_claim_after_result_mutation: 0
  local_only_evidence_accepted: 0
  wrong_revision_ci_accepted: 0
  incomplete_provider_false_clean: 0
  mutable_latest_ref_accepted: 0
  signed_url_used_as_durable_identity: 0
  wrong_repository_fallback: 0
  inaccessible_required_evidence_accepted: 0
  proof_summary_overrode_exact_source: 0
  incomplete_obligation_set_false_complete: 0
  non_p34_gate_pass_emission: 0
```

These are future Gate thresholds. P30 does not claim they currently pass.

---

# 6. ECV0 coverage allocation

| ECV0 obligation | Primary implementation slice |
|---|---|
| R1 authoritative fact single source | VP-I02 |
| R2 exact accepted dependency | VP-I01 |
| R3 contract satisfiability / self-reference | VP-I01 |
| R4 frozen review contract / post-hoc delta | VP-I02 |
| R5 evidence-only repair identity | VP-I02 |
| R6 local-only evidence rejection | VP-I02 core + VP-I03 platform |
| R7 exact-result provider applicability | VP-I03 |
| R8 provider/matrix completion | VP-I03 |
| R9 mutable/latest lookup rejection | VP-I03 |
| R10 durable identity vs signed URL | VP-I02 identity + VP-I03 provider |
| R11 repository namespace integrity | retained Current repository-identity implementation + VP-I03 regression |
| R12 reviewer read capability | VP-I03 |
| R13 result/evidence identity separation | VP-I02 |
| R14 derived summaries only | VP-I02 + VP-I03 return contract |
| R15 P34 independent resolution | VP-I02 review + VP-I03 Skill integration |
| R16 adapter semantic parity | VP-I03 |
| R17 independent completeness oracle | VP-I02 |

All `EC-S01..EC-S17` and `EC-M01..EC-M17` are rerun together in VP-I03 even when the owning implementation landed earlier.

---

# 7. Review and repair policy during implementation

## If a deterministic test exposes an implementation defect

Route through normal P35/P36 implementation repair. Do not change upstream semantics.

## If implementation cannot construct an accepted semantic object without inventing a field/value

Return:

```yaml
status: BLOCKED_AUTHORITY
earliest_untrusted_layer: <exact owning earlier layer>
continue_execution: false
```

Do not patch the model locally.

## If an ECV0 requirement is impossible on the selected provider surface

First distinguish:

- implementation adapter missing capability -> implementation/environment repair;
- provider cannot expose required exact/reviewer-resolvable identity -> `BLOCKED_EVIDENCE` / platform capability blocker;
- requirement is structurally self-dependent -> contract preflight blocker;
- requirement was never in the frozen P20/P31 contract -> `ReviewContractDiffer` + owning-layer routing.

Never downgrade the ProofContract just to make execution pass.

## If evidence-only repair is needed

Preserve unchanged `result_revision/materialized_ref` only when the repaired evidence uses an external materialization path. If a repository-contained evidence edit changes result bytes, treat it as a new result revision.

---

# 8. P31 requirements derived from this plan

Each future P31 package MUST include:

```yaml
repository:
  provider: github
  full_name: Mostorm-Labs/aegis

package_materialization_ref: <same-repository durable PR/ref>

task_anchor:
  revision: 674e01737621621b8131e35f83313fb0154a9f6d
  relation: ancestor

trusted_basis:
  semantic: 12c968c5c481ad671ce33bcfa088ba8a2fca0f43
  p17_platform: c8f47d049be50d65f88b04ad141650ed6dfdb826
  p20_verification: 674e01737621621b8131e35f83313fb0154a9f6d
  p20_p21_review: 5121075377

verification:
  profile: ECV0
  exact_spec_ref: <exact package-specific VerificationSpec/contract ref>
  exact_obligation_set_ref: <exact materialized set when required>
  exact_acceptance_oracle_refs: <exact refs>
  exact_evidence_compilation_contract_ref: <exact ref>
```

P31 must also freeze:

- exact slice file scope;
- exact predecessor accepted result/Gate refs for VP-I02/VP-I03;
- exact required focused tests and inherited regressions;
- exact evidence artifact families;
- exact platform corroborations applicable to that slice;
- blocked-return behavior;
- result materialization obligation.

The package must not contain floating phrases as executable dependencies.

---

# 9. Non-goals / explicitly excluded work

This P30 plan does not authorize:

- changing Product P02/P03;
- changing Proof Plane P10-P17 semantics;
- entering P18;
- publishing PR #23/#24/#68 as Current Authority;
- merging the stacked Draft PRs;
- changing P34 ownership;
- autonomous cross-Primary substantive chaining;
- implementing a generic mutation-testing framework;
- implementing a standalone verifier service/daemon;
- introducing a database or queue;
- rewriting the published beta.3 Plugin tree;
- creating `v0.2.0-beta.1` tag/manifest/release;
- release or rollout changes;
- P32 execution before P31 package approval.

---

# 10. P30 exit criteria

P30 is READY for P31 when all of the following are true:

1. implementation placement is fixed to `tools/aegis_proof` plus narrow bridges into existing Control Plane/Skill surfaces;
2. the implementation is split into three dependency-ordered, independently reviewable slices;
3. every ECV0 R1-R17 requirement has an owning slice;
4. R1-R5 incident regressions have explicit implementation and test locations;
5. all 17 deterministic scenarios, 17 mutants, and four platform corroborations have a defined production/evidence surface;
6. published Plugin materialization remains explicitly excluded from mutation;
7. Skill canonical source changes and generated distribution handling are explicit;
8. exact full qualification commands are known;
9. future P31 task-anchor and exact upstream verification basis are fixed;
10. no unresolved semantic/platform design decision is left for Codex to guess.

---

# 11. P30 disposition

```yaml
P30_implementation_plan:
  task: AEGIS_EVIDENCE_CONTRACT_CHURN
  repository: Mostorm-Labs/aegis

  exact_verification_basis: 674e01737621621b8131e35f83313fb0154a9f6d
  verification_p21_review: 5121075377
  task_anchor:
    revision: 674e01737621621b8131e35f83313fb0154a9f6d
    relation: ancestor

  implementation_package_root: tools/aegis_proof

  planned_slices:
    - VP-I01_EXACT_CONTRACT_AND_PACKAGE_PREFLIGHT
    - VP-I02_EVIDENCE_AND_INDEPENDENT_REVIEW_RUNTIME
    - VP-I03_PLATFORM_SKILL_INTEGRATION_AND_ECV0_QUALIFICATION

  p18_required: false
  implementation_execution_authorized: false
  p31_materialized: false
  p32_started: false
  p34_pass_issued: false
  merge_authorized: false
  release_authorized: false

  status: READY_FOR_P31_TASK_PACKAGING
  next_owner: aegis-implementation
  next_stage: P31_TASK_PACKAGING
  recommended_first_slice: VP-I01_EXACT_CONTRACT_AND_PACKAGE_PREFLIGHT
```

The P30 result revision/materialized Git identity is recorded externally by the repository commit/PR and must not be embedded as a future-self value inside this document.