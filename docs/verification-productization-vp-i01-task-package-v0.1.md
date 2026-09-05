# VP-I01-P31-01 — Exact Contract & Package Preflight Task Package

Status: **P31 / CONTROL_REASONING / MATERIALIZED — READY FOR EXPLICIT P32 START**

This is the executable P31 package for the first Verification Productization implementation slice. It authorizes only `VP-I01 — EXACT_CONTRACT_AND_PACKAGE_PREFLIGHT` and does not itself start P32.

## 1. Task identity

```yaml
package_id: VP-I01-P31-01
slice_id: VP-I01
name: EXACT_CONTRACT_AND_PACKAGE_PREFLIGHT
stage_owner: aegis-implementation
execution_surface_now: CONTROL_REASONING
preferred_p32_surface: CODE_EXECUTION
preferred_executor: codex
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/70
task_anchor:
  revision: 674e01737621621b8131e35f83313fb0154a9f6d
  relation: ancestor
resume_cursor: null
```

The exact `package_ref` is the final P31 head revision and is recorded externally by the P31 stage result / PR metadata after this document is materialized. This document MUST NOT attempt to embed the future commit SHA that contains itself.

A future P32 handoff is executable only when it carries all of:

```yaml
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
package_ref: <exact final VP-I01-P31-01 head>
package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/70
task_anchor:
  revision: 674e01737621621b8131e35f83313fb0154a9f6d
  relation: ancestor
resume_cursor: null
```

Repository identity is resolved before package, anchor, cursor, or mutation handling.

---

## 2. Exact trusted basis

### Verification Productization accepted basis

- semantic Proof Plane: `12c968c5c481ad671ce33bcfa088ba8a2fca0f43`
- semantic re-certification P21: `5121012716` — `PASS / ACCEPTED_FOR_DOWNSTREAM`
- P14 architecture: `d9c8f6ac5db4359400fae06e76c51c65bd059bfc`
- P15 module design: `665292dcfd7781935243369ee9f676c320f2878a`
- P16 runtime flow: `708cf09c01effbcc63c65d45b9b4a67b7a8fc8db`
- P17 platform contract: `c8f47d049be50d65f88b04ad141650ed6dfdb826`
- P20 ECV0 verification design: `674e01737621621b8131e35f83313fb0154a9f6d`
- P20 P21 review: `5121075377` — `PASS / ACCEPTED_FOR_DOWNSTREAM`
- P30 implementation plan: `69a390439f650e1f418f9b589828b6e67bc18c6f`

### Current external contract baseline

Current external contracts are resolved from repository baseline:

`main@342d6785d8f54dd9beb2c3bb82398f29b405df2f`

This includes Current Project State v0.5, Execution Surface v0.2, Control Plane Product/Verification, repository-identity platform/verification/materialization, and the accepted package/CanonicalRef/TrustedBasis rules recorded in `.aegis/authorities.json`.

Normative invariants retained:

> `Repository Identity != Task Anchor != Execution Cursor`

> `semantic proof truth != execution observation != evidence identity != result identity != ProofEvaluation != Gate Decision`

> `generated obligation set != independent completeness oracle`

> `P34 remains the sole formal Gate owner`

---

## 3. Exact Verification binding

For this bootstrap slice, the accepted P20 ECV0 materialization is the exact VerificationSpec input. No new competing VerificationSpec is invented in P31.

```yaml
verification_binding:
  verification_spec_ref:
    object_type: VERIFICATION_SPEC
    id: aegis-verification-productization-ecv0-v0.1
    ref: https://github.com/Mostorm-Labs/aegis/blob/674e01737621621b8131e35f83313fb0154a9f6d/docs/verification-productization-verification-v0.1.md
    identity:
      scheme: git-sha
      value: 674e01737621621b8131e35f83313fb0154a9f6d

  obligation_set_ref: null

  acceptance_oracle_refs:
    - object_type: CONTRACT
      id: O-EC-CONTRACT
      ref: https://github.com/Mostorm-Labs/aegis/blob/674e01737621621b8131e35f83313fb0154a9f6d/docs/verification-productization-verification-v0.1.md
      identity:
        scheme: git-sha
        value: 674e01737621621b8131e35f83313fb0154a9f6d

    - object_type: CONTRACT
      id: O-EC-PREFLIGHT
      ref: https://github.com/Mostorm-Labs/aegis/blob/674e01737621621b8131e35f83313fb0154a9f6d/docs/verification-productization-verification-v0.1.md
      identity:
        scheme: git-sha
        value: 674e01737621621b8131e35f83313fb0154a9f6d

    - object_type: CONTRACT
      id: control-plane-verification-bound-package-v0.2
      ref: https://github.com/Mostorm-Labs/aegis/blob/342d6785d8f54dd9beb2c3bb82398f29b405df2f/docs/control-plane-productization-schema-v0.2.md
      identity:
        scheme: git-sha
        value: 342d6785d8f54dd9beb2c3bb82398f29b405df2f

  evidence_compilation_contract_ref:
    object_type: CONTRACT
    id: ecv0-vp-i01-evidence-contract-v0.1
    ref: https://github.com/Mostorm-Labs/aegis/blob/674e01737621621b8131e35f83313fb0154a9f6d/docs/verification-productization-verification-v0.1.md
    identity:
      scheme: git-sha
      value: 674e01737621621b8131e35f83313fb0154a9f6d
```

### Why `obligation_set_ref: null` is valid here

The governing semantic/architecture contract defines ProofObligations as deterministic derived state from an exact VerificationSpec / ProofContract. VP-I01 is the bootstrap implementation of that deterministic generation path.

Therefore this package explicitly permits later obligation materialization **without semantic change** for VP-I01 only:

1. exact P20 ECV0 VerificationSpec identity is already frozen;
2. the required VP-I01 claim/scenario/mutant semantics are already fixed by P20;
3. `ObligationGenerator` may derive the set but may not invent or weaken obligations;
4. a changed P20 semantic identity requires a replacement P31 package;
5. if implementation discovers that deterministic generation cannot preserve the accepted semantics, return `BLOCKED_AUTHORITY` rather than inventing a local set.

No downstream VP-I02/VP-I03 package may infer that `obligation_set_ref` is generally optional; each later package must bind the exact predecessor/generator result required by its governing contract.

---

## 4. Exact scope contract

The authoritative implementation scope is P30 `VP-I01` at exact revision:

```yaml
scope:
  scope_id: VP-I01_EXACT_CONTRACT_AND_PACKAGE_PREFLIGHT
  scope_contract_ref:
    object_type: CONTRACT
    id: vp-i01-scope-v0.1
    ref: https://github.com/Mostorm-Labs/aegis/blob/69a390439f650e1f418f9b589828b6e67bc18c6f/docs/verification-productization-implementation-plan-v0.1.md
    identity:
      scheme: git-sha
      value: 69a390439f650e1f418f9b589828b6e67bc18c6f
```

Scope authorization is **exact path-set based**. There is no numeric changed-file-count requirement.

```yaml
authorization_mode: EXACT_PATH_SET
numeric_changed_file_count_constraint: NONE
```

### Authorized authored paths

Exactly these source/test paths may be authored in VP-I01:

```text
tools/aegis_proof/__init__.py
tools/aegis_proof/domain.py
tools/aegis_proof/spec.py
tools/aegis_proof/obligations.py
tools/aegis_proof/package.py
tools/aegis_control/canonical.py
tests/verification_productization/__init__.py
tests/verification_productization/test_domain_spec.py
tests/verification_productization/test_package_preflight.py
```

No other authored path is authorized.

Temporary local test files outside the repository may be used as ephemeral execution state, but they do not become evidence or authorized repository mutation.

### Explicitly forbidden mutation families

```text
plugins/aegis/**
skillset/**
skills/**
.aegis/**
.github/workflows/**
tools/aegis_state/**
tools/aegis_skillset/**
docs/** except implementation-result navigation generated outside this package scope
release manifests / tags / releases
```

The P31 package document itself is already materialized on PR #70 and is not P32 mutation scope.

Any requested authored change outside the exact nine paths above requires a replacement P31 package or an earlier-layer route; do not widen scope in Codex.

---

## 5. Required implementation

### 5.1 `tools/aegis_proof/domain.py`

Implement the P30-frozen deterministic proof identity primitives:

```python
class ProofValidationError(ValueError):
    pass

class ProofCodec:
    @staticmethod
    def canonicalize(value): ...

    @staticmethod
    def digest(value): ...

class ObligationIdentityCodec:
    @staticmethod
    def semantic_key(
        *, verification_spec_digest, subject_kind, subject_id,
        obligation_kind, source_key
    ): ...

    @staticmethod
    def id_from_key(key): ...

class EvidenceInputIdentity:
    @staticmethod
    def from_materialized_artifact(
        *, evidence_id, ref, digest, producer_class
    ): ...
```

Rules:

- reuse `tools.aegis_control.canonical` JCS/digest primitives;
- do not implement a second canonicalizer;
- preserve exact source identity;
- no network, filesystem, lifecycle mutation, Gate, profile-selection, or obligation traversal logic.

### 5.2 `tools/aegis_proof/spec.py`

Implement:

```python
ValidationFinding
ValidationResult
VerificationSpecValidator.validate(spec)
```

Required behavior:

- enforce accepted CoverageBasis shape;
- preserve `CLAIM | COVERAGE_BASIS` subject semantics;
- enforce resolved ProofContract structure and exact profile/version identity when present;
- unknown required schema/enum values fail closed;
- no risk/assurance downgrade or semantic authoring decisions inside the validator.

### 5.3 `tools/aegis_proof/obligations.py`

Implement deterministic `ObligationGenerator` and `ObligationSet`.

Required invariants:

- exact validated spec only;
- preserve `CLAIM | COVERAGE_BASIS` subject;
- `REVIEW_DECLARED` creates exactly one required CoverageBasis completeness obligation;
- review-required obligations remain in the complete set;
- no obligation is marked SATISFIED by generation;
- generator output is not its own completeness proof.

### 5.4 `tools/aegis_proof/package.py`

Implement:

```text
P31TaskProjector
PackageBindingPreflight
EvidenceContractPreflight
PreflightCode
PreflightFinding
PreflightResult
```

Mandatory preflight behavior:

1. exact VerificationSpec ref required;
2. exact obligation-set ref required when the governing contract requires one;
3. TrustedBasis / scope / acceptance-oracle / evidence-compilation refs must be exact;
4. floating values such as `accepted A4`, `latest Gate`, `current result`, and `previous accepted baseline` are rejected before P32;
5. repository-backed task anchor shape is validated;
6. future-self materialization requirements are rejected as structurally unsatisfiable;
7. P34-produced judgment cannot be required as deterministic P32 evidence;
8. mutable-only provider identity is rejected when an exact trust-boundary identity is required;
9. unresolved semantic choice fails closed instead of being guessed.

The transient evidence dependency phases are exactly:

```text
P31_FREEZE
P32_EXECUTION
EVIDENCE_COMPILE
ARTIFACT_MATERIALIZE
RESULT_MATERIALIZE
P34_REVIEW
```

These are implementation states, not new Aegis lifecycle stages.

### 5.5 `tools/aegis_control/canonical.py`

Add package-specific nested validation without moving Control Plane ownership into `aegis_proof`:

```python
validate_trusted_basis(...)
validate_verification_binding(...)
validate_verification_bound_package(...)
```

and invoke the package-specific validator from `validate_record()` for `VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE`.

Required checks include:

- exact nested field sets;
- CanonicalRef object-type restrictions;
- required non-empty arrays where P12 mandates them;
- deterministic TrustedBasis `basis_digest` validation;
- `scope_contract_ref`, `verification_spec_ref`, acceptance-oracle and evidence-compilation ref types;
- task-anchor shape when non-null;
- `package_digest == canonical_digest(record, self_digest_field="package_digest")`.

This slice must not add Control Plane mutation/dispatch behavior to `aegis_proof`.

---

## 6. Mandatory TDD / Verification subset

VP-I01 binds the exact P20 ECV0 subset:

```text
EC-S02
EC-S03
EC-M02
EC-M03
```

### `EC-S02`

A package using floating accepted labels such as `accepted A4` / `latest Gate` without exact identity is rejected before P32.

### `EC-S03`

An evidence requirement that demands an artifact contain the future SHA/ref of the immutable object whose identity depends on those same artifact bytes returns `STRUCTURALLY_UNSATISFIABLE` before P32.

### `EC-M02`

A mutant that admits a floating dependency across the executable trust boundary must be detected.

### `EC-M03`

A mutant that accepts a future-self materialization cycle must be detected.

Required RED -> GREEN sequence:

1. add failing package/canonical regression tests demonstrating the current nested-validation/preflight gap;
2. run the focused RED tests and preserve the actual failure output;
3. implement the minimum VP-I01 code;
4. run focused tests to GREEN;
5. run inherited regression suites.

Required focused command:

```bash
python3 -m unittest \
  tests.verification_productization.test_domain_spec \
  tests.verification_productization.test_package_preflight -v
```

Required inherited regressions:

```bash
python3 -m unittest discover -s tests/control_plane -v
python3 -m unittest discover -s tests/project_state -v
python3 -m unittest discover -s tests/skillset -v
```

No P18 performance/resource threshold applies to VP-I01.

---

## 7. Evidence and result-materialization contract

P32 may use local execution for TDD, but local-only state is never sufficient for CONTROL_REVIEW readiness.

Before a completed P32 return, the executor MUST:

1. push the exact implementation result to a branch in `Mostorm-Labs/aegis`;
2. expose that exact result through a reviewer-resolvable Draft implementation PR;
3. return the exact `result_revision` and `materialized_ref`;
4. return the exact implementation PR/branch and actual starting revision;
5. materialize the focused RED/GREEN command outputs on the implementation PR as durable, reviewer-resolvable execution evidence without manually retyping derived test totals;
6. return exact durable refs for those focused execution records;
7. resolve and return every hosted GitHub Actions check/run that applies to the exact result revision, including the existing Control Plane foundation workflow triggered by `tools/aegis_control/canonical.py` changes;
8. preserve provider-native run/job identity rather than returning only `latest`, branch name, or workflow name;
9. return `unresolved_required_refs: 0` before claiming review readiness.

The focused execution record must preserve the machine-generated command output or per-test records. A prose statement such as `tests passed` or manually typed pass/skip totals is navigation only and cannot substitute for the underlying record.

If the executor cannot produce reviewer-resolvable durable evidence for a required proof input, return `BLOCKED_EVIDENCE` instead of `READY_FOR_CONTROL_REVIEW`.

The existing CP-I01 evidence manifest, if produced by an inherited workflow, must not be misrepresented as the VP-I01 package's own ProofEvaluation or Gate evidence merely because the workflow ran. P34 decides applicability independently.

P32 does not issue a Gate verdict.

---

## 8. Exit criteria

VP-I01 is ready to return from P32 only when all are true:

```yaml
repository_identity_preflight: PASS
package_ref_resolved_in_declared_repository: true
task_anchor_relation: ancestor
scope_deviation: none
authority_deviation: none

verification_spec_exact: true
obligation_generation_deterministic: true
nested_package_validation_enabled: true
floating_dependency_admitted_to_p32: 0
future_self_contract_admitted_to_p32: 0

EC-S02: PASS
EC-S03: PASS
EC-M02_detected: true
EC-M03_detected: true
mutant_false_acceptance: 0

focused_tests_exit_code: 0
control_plane_regression_failures: 0
project_state_regression_failures: 0
skillset_regression_failures: 0

result_revision: REQUIRED
materialized_ref: REQUIRED
durable_focused_execution_refs: REQUIRED
unresolved_required_refs: 0
P34_claimed_by_P32: false
```

Acceptance target values are contract thresholds, not a claim that they already pass at P31.

---

## 9. Fail-closed returns

Use the most specific existing blocker:

- declared repository/package materialization mismatch or unavailable repository -> `BLOCKED_REPOSITORY_IDENTITY`, `continue_execution: false`;
- required exact Authority/Verification meaning is absent or contradictory -> `BLOCKED_AUTHORITY`;
- a required exact input/ref is missing -> `BLOCKED_MISSING_INPUT`;
- a semantic choice is unresolved -> `BLOCKED_UNRESOLVED_DECISION`;
- implementation cannot satisfy the frozen contract without changing semantics -> `BLOCKED_AUTHORITY`;
- implementation/test code is defective within authorized scope -> `BLOCKED_IMPLEMENTATION`;
- required durable proof cannot be materialized/resolved -> `BLOCKED_EVIDENCE`;
- provider/tool/runtime availability prevents execution -> `BLOCKED_ENVIRONMENT`;
- anchor/cursor ancestry is genuinely incompatible after repository identity succeeds -> `BLOCKED_EXECUTION_DIVERGENCE`.

Do not treat a historical expected-HEAD mismatch as divergence when the actual start is a valid descendant of the task anchor.

Any requested source mutation outside the exact authorized path set is out of package scope and must not be performed; return a blocker and request a replacement P31 package rather than widening scope locally.

---

## 10. Explicit non-goals

VP-I01 MUST NOT:

- implement VP-I02 evidence compiler/evaluator/review runtime;
- implement VP-I03 provider adapters, CLI, Skill integration, generated Skills, or ECV0 full qualification;
- modify `skillset/**`, `skills/**`, `plugins/aegis/**`, `.aegis/**`, or workflow files;
- create a standalone verifier service/daemon/database/queue;
- modify Project State or formal Gate ownership;
- publish Draft Verification Productization Authority as Current;
- merge PR #23/#24/#68/#69/#70;
- create tags, releases, manifests, Installation Kits, or rollout changes;
- enter P18;
- claim P34 PASS;
- start VP-I02 before VP-I01 has the accepted downstream result required by its future package.

---

## 11. P32 handoff rule

This P31 stage stops after materialization. Do not execute P32 in the same turn.

When a later user explicitly starts P32 with Codex, the rendered surface handoff must place the exact required Codex execution prefix immediately before the YAML and carry:

```text
repository identity
final package_ref
package_materialization_ref = PR #70
task_anchor = 674e017... / ancestor
resume_cursor = null
```

The executor must first resolve the declared repository and final package ref, then establish anchor ancestry, record the actual starting revision, and only then mutate the authorized paths.

---

## 12. P31 disposition

```yaml
P31_package:
  package_id: VP-I01-P31-01
  slice_id: VP-I01
  repository: Mostorm-Labs/aegis
  package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/70
  task_anchor:
    revision: 674e01737621621b8131e35f83313fb0154a9f6d
    relation: ancestor
  resume_cursor: null

  verification_basis: 674e01737621621b8131e35f83313fb0154a9f6d
  verification_p21: 5121075377
  p30_basis: 69a390439f650e1f418f9b589828b6e67bc18c6f

  authorized_slice: VP-I01_EXACT_CONTRACT_AND_PACKAGE_PREFLIGHT
  authorized_authored_paths: 9
  numeric_changed_file_count_constraint: NONE

  mandatory_scenarios:
    - EC-S02
    - EC-S03
  mandatory_mutants:
    - EC-M02
    - EC-M03

  p32_started: false
  p34_pass_issued: false
  merge_authorized: false
  release_authorized: false

  status: MATERIALIZED_READY_FOR_EXPLICIT_P32_START
  next_owner: aegis-implementation
  next_stage: P32_IMPLEMENTATION
```

The final exact `package_ref` is external repository identity produced by the commit containing this document and must not be self-embedded here.
