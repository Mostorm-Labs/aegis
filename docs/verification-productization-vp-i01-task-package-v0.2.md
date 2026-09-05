# VP-I01-P31-02 — Control Plane Canonical Package Compatibility Migration

Status: **P31 / CONTROL_REASONING / REPLACEMENT PACKAGE — READY FOR EXPLICIT P32 RESUME**

This immutable replacement package supersedes `VP-I01-P31-01` only for the blocked completion of `VP-I01 — EXACT_CONTRACT_AND_PACKAGE_PREFLIGHT`.

It preserves the valid partial VP-I01 implementation already materialized at `c6cc55f7d0067fd77d1e21f21ee1f7dcf06fb03f` and authorizes only the smallest compatibility migration required by the inherited Control Plane regression failure.

It does not start P32, does not authorize P34, and does not reopen Verification Productization semantics or architecture.

---

## 1. Task identity

```yaml
package_id: VP-I01-P31-02
slice_id: VP-I01
name: CONTROL_PLANE_CANONICAL_PACKAGE_COMPATIBILITY_MIGRATION
stage_owner: aegis-implementation
execution_surface_now: CONTROL_REASONING
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
predecessor_package_id: VP-I01-P31-01
predecessor_package_ref: d311cadaee2cdc0e1ce2823e03864e170a880300
predecessor_package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/70
blocked_partial_result:
  result_revision: c6cc55f7d0067fd77d1e21f21ee1f7dcf06fb03f
  materialized_ref: https://github.com/Mostorm-Labs/aegis/pull/71
  blocker_comment: https://github.com/Mostorm-Labs/aegis/pull/71#issuecomment-5551746696
task_anchor:
  revision: c6cc55f7d0067fd77d1e21f21ee1f7dcf06fb03f
  relation: ancestor
resume_cursor: c6cc55f7d0067fd77d1e21f21ee1f7dcf06fb03f
```

The exact `package_ref` is the final commit containing this document and is recorded externally after materialization. This document does not self-embed that future commit SHA.

Repository identity MUST be resolved before package, anchor, cursor, or mutation handling.

---

## 2. Why a replacement package is required

`VP-I01-P31-01` authorized exactly nine authored paths. P32 correctly implemented nested validation for the already-accepted P12 `VerificationBoundImplementationPackage` contract and preserved exact scope compliance.

Focused VP-I01 verification is GREEN, but inherited hosted Control Plane regressions fail because historical Control Plane fixtures still construct an abbreviated package shape, for example:

```python
'trusted_basis': {'authority': [...]},
'scope': {'name': ...},
'verification_binding': {'spec': ...},
'policy_binding': {'control_autonomy': 'REVIEW_GUARDED'},
```

The exact hosted failure is:

```text
CanonicalValidationError: TrustedBasis has invalid fields
```

The failure path is:

```text
legacy package fixture
-> MutationService._complete_package(...)
-> validate_record(...)
-> validate_verification_bound_package(...)
-> validate_trusted_basis(...)
```

The P31-01 contract explicitly requires a replacement package rather than local scope expansion whenever a required source mutation falls outside its nine-path allowlist.

This is therefore a package-scope completion defect, not permission to weaken nested validation.

---

## 3. Exact retained Authority and verification basis

No semantic Authority changed during the blocked P32 execution. P31-02 inherits the exact accepted basis from P31-01:

- semantic Proof Plane: `12c968c5c481ad671ce33bcfa088ba8a2fca0f43`
- semantic re-certification P21: `5121012716` — `PASS / ACCEPTED_FOR_DOWNSTREAM`
- P14 architecture: `d9c8f6ac5db4359400fae06e76c51c65bd059bfc`
- P15 module design: `665292dcfd7781935243369ee9f676c320f2878a`
- P16 runtime flow: `708cf09c01effbcc63c65d45b9b4a67b7a8fc8db`
- P17 platform contract: `c8f47d049be50d65f88b04ad141650ed6dfdb826`
- P20 ECV0 verification design: `674e01737621621b8131e35f83313fb0154a9f6d`
- P20 P21 review: `5121075377` — `PASS / ACCEPTED_FOR_DOWNSTREAM`
- P30 implementation plan: `69a390439f650e1f418f9b589828b6e67bc18c6f`
- predecessor P31 package: `d311cadaee2cdc0e1ce2823e03864e170a880300`
- valid partial implementation result: `c6cc55f7d0067fd77d1e21f21ee1f7dcf06fb03f`
- P32 blocked-return record: comment `5551746696`

The accepted P12 package semantics remain unchanged. P31-02 adds no new semantic object, lifecycle stage, status, or Gate authority.

---

## 4. Minimal migration-surface determination

Fresh inspection of exact result `c6cc55f7...` establishes:

1. `tests/control_plane/cp_i02_fixtures.py` is the shared constructor that directly emits the historical abbreviated `VerificationBoundImplementationPackage` test fixture through `package_record()`.
2. `tests/control_plane/cp_i02_evidence.py` imports and consumes that shared `package_record()`; it does not own a separate package schema.
3. `tests/control_plane/generate_cp_i04_evidence.py` imports and consumes the same shared `package_record()`; it does not own a separate package schema.
4. `tests/control_plane/test_cp_i04_barrier_matrix.py` imports and consumes the same helper.
5. `tests/control_plane/cp_i08_d0.py` binds existing Control Plane tests such as G29/G30; it does not construct a second package representation.
6. `tests/control_plane/generate_cp_i08_evidence.py` consumes integrated D0 results and does not define a separate `VerificationBoundImplementationPackage` constructor.

Therefore the smallest known authored compatibility migration is one path.

---

## 5. Exact authored scope for resumed P32

Authorization mode:

```yaml
authorization_mode: EXACT_PATH_SET
numeric_changed_file_count_constraint: NONE
```

### Newly authorized authored path

Exactly this path may be authored after resume:

```text
tests/control_plane/cp_i02_fixtures.py
```

### Frozen predecessor result paths

The nine VP-I01 paths already materialized at `c6cc55f7...` are retained as frozen predecessor work and MUST NOT be modified under P31-02 unless a later replacement package explicitly authorizes such a change:

```text
tests/verification_productization/__init__.py
tests/verification_productization/test_domain_spec.py
tests/verification_productization/test_package_preflight.py
tools/aegis_control/canonical.py
tools/aegis_proof/__init__.py
tools/aegis_proof/domain.py
tools/aegis_proof/obligations.py
tools/aegis_proof/package.py
tools/aegis_proof/spec.py
```

No other authored path is authorized.

A test/evidence caller that becomes GREEN solely because the shared fixture is repaired is not an authored migration surface and MUST NOT be modified merely because it previously failed.

---

## 6. Required compatibility migration

The resumed P32 must update `package_record()` in `tests/control_plane/cp_i02_fixtures.py` so historical Control Plane tests construct the already-accepted full P12 package contract instead of the old abbreviated nested shape.

The migrated fixture MUST:

1. preserve the existing caller-facing `package_record(package_id, lane_id, revision, scope_name)` behavior unless a compatibility-safe internal helper is required;
2. emit a complete valid `TrustedBasis` with exact canonical refs, canonical ordering, and a correct `basis_digest`;
3. emit `scope.scope_id` plus an exact `scope_contract_ref`;
4. emit an exact `verification_binding` with `verification_spec_ref`, nullable `obligation_set_ref` where allowed by the governing bootstrap contract, non-empty exact `acceptance_oracle_refs`, and an exact `evidence_compilation_contract_ref`;
5. emit a complete `policy_binding`, including an exact Gate-policy contract ref, complete repair policy, and a correct `policy_digest`;
6. preserve the exact repository task-anchor shape already used by the fixture;
7. emit a valid package digest before the package first crosses the canonical validation boundary;
8. keep all synthetic test identities deterministic and immutable in test semantics;
9. preserve existing lane, revision, scope-change, idempotency, and work-scope test intent;
10. not add a compatibility branch to production canonical validation for the abbreviated historical representation.

The compatibility repair is in the producer fixture, not in the canonical validator.

---

## 7. Explicit prohibitions

P31-02 MUST NOT authorize the resumed P32 to:

- weaken or bypass `validate_verification_bound_package`, `validate_trusted_basis`, scope validation, verification-binding validation, policy validation, or package-digest validation;
- modify any of the frozen nine predecessor VP-I01 paths;
- modify `tests/control_plane/cp_i02_evidence.py`, `generate_cp_i04_evidence.py`, CP-I08 files, or other callers unless a new observed failure proves an independent authored defect and a later replacement package authorizes it;
- modify `.github/workflows/**`;
- modify `plugins/aegis/**`, `skillset/**`, `skills/**`, `.aegis/**`, Project State, release artifacts, tags, or manifests;
- start VP-I02 or VP-I03;
- claim P34 PASS or merge any PR.

If the one-path migration cannot satisfy the inherited regression contract without another source mutation, stop fail-closed and return the exact newly discovered path/reason for another replacement P31 package.

---

## 8. Verification contract for resumed P32

The existing hosted regression failure is the RED evidence for this compatibility repair. The resumed implementation must first reproduce or bind that exact failure basis and then verify the repaired exact result.

Required local/focused commands:

```bash
python3 -m unittest \
  tests.verification_productization.test_domain_spec \
  tests.verification_productization.test_package_preflight -v

python3 -m unittest \
  tests.control_plane.test_cp_i02_mutation \
  tests.control_plane.test_cp_i02_guards \
  tests.control_plane.test_cp_i04_barrier_matrix -v
```

Required inherited regressions:

```bash
python3 -m unittest discover -s tests/control_plane -v
python3 -m unittest discover -s tests/project_state -v
python3 -m unittest discover -s tests/skillset -v
```

Required hosted verification:

- resolve every GitHub Actions workflow run applicable to the exact final result;
- preserve provider-native workflow run and job identities;
- inherited Control Plane workflows that apply to the exact result must have no unresolved required failure;
- do not replace machine output with manually retyped pass/skip totals.

P32 may return `READY_FOR_CONTROL_REVIEW` only if:

```yaml
repository_identity_preflight: PASS
package_ref_resolved_in_declared_repository: true
task_anchor_relation: ancestor
resume_cursor_relation: exact_or_ancestor
scope_deviation: none
authority_deviation: none

focused_vp_i01_exit_code: 0
compatibility_focus_exit_code: 0
control_plane_regression_failures: 0
project_state_regression_failures: 0
skillset_regression_failures: 0
hosted_required_failures: 0
unresolved_required_refs: 0

result_revision: REQUIRED
materialized_ref: REQUIRED
P34_claimed_by_P32: false
```

---

## 9. Fail-closed return rules

Use the most specific existing blocker:

- repository/package identity mismatch -> `BLOCKED_REPOSITORY_IDENTITY`;
- required exact Authority meaning absent/contradictory -> `BLOCKED_AUTHORITY`;
- missing exact input/ref -> `BLOCKED_MISSING_INPUT`;
- unresolved semantic choice -> `BLOCKED_UNRESOLVED_DECISION`;
- defect within the one authorized migration path -> `BLOCKED_IMPLEMENTATION`;
- required additional authored source path outside the one-path set -> `BLOCKED_IMPLEMENTATION / P31_PACKAGE_SCOPE_DEFECT` and request another replacement P31;
- required durable proof unavailable -> `BLOCKED_EVIDENCE`;
- provider/runtime prevents execution -> `BLOCKED_ENVIRONMENT`;
- anchor/cursor ancestry incompatible after repository identity succeeds -> `BLOCKED_EXECUTION_DIVERGENCE`.

No blocker discovered here authorizes a semantic downgrade or a compatibility exception in the canonical contract.

---

## 10. P31 disposition

```yaml
P31_package:
  package_id: VP-I01-P31-02
  slice_id: VP-I01
  repository: Mostorm-Labs/aegis

  predecessor_package_ref: d311cadaee2cdc0e1ce2823e03864e170a880300
  preserved_partial_result: c6cc55f7d0067fd77d1e21f21ee1f7dcf06fb03f
  blocked_return_comment: 5551746696

  task_anchor:
    revision: c6cc55f7d0067fd77d1e21f21ee1f7dcf06fb03f
    relation: ancestor
  resume_cursor: c6cc55f7d0067fd77d1e21f21ee1f7dcf06fb03f

  newly_authorized_authored_paths:
    - tests/control_plane/cp_i02_fixtures.py
  frozen_predecessor_authored_paths: 9
  numeric_changed_file_count_constraint: NONE

  p32_started_for_this_package: false
  p34_pass_issued: false
  merge_authorized: false
  release_authorized: false

  status: MATERIALIZED_READY_FOR_EXPLICIT_P32_RESUME
  next_owner: aegis-implementation
  next_stage: P32_IMPLEMENTATION_RESUME
```

The exact `package_ref` and package materialization PR are external repository identities produced after this document is committed and reviewed. P32 MUST resolve them before mutation.
