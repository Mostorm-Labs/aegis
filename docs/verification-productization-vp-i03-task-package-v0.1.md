# VP-I03-P31-01 — Platform / Skill Integration & ECV0 Qualification Task Package

Status: **P31 / CONTROL_REASONING / MATERIALIZED — READY FOR EXPLICIT P32 START**

This is the executable P31 package for `VP-I03 — Platform / Skill Integration & ECV0 Qualification`. It consumes the accepted VP-I01 and VP-I02 results and authorizes only the platform adapters, structured CLI, canonical Skill integration/regeneration, exact ECV0 qualification corpus, and one dedicated ECV0 workflow frozen by P30/P20.

It does **not** start P32, issue P34 PASS, merge any PR, publish Authority, rewrite the published Plugin beta.3 tree, create a release, or expand rollout.

The pre-final materialization commits `d044603322018614c24b351c0bd9e9f41a48f525`, `b99329f259c5a6f5a493319ed2647ad979d21b55`, and `ee57198b81badb9fcbd1ca51820216bbd969ae55` are **NON-EXECUTABLE materialization history** and MUST NOT be used as `package_ref`.

---

## 1. Task identity

```yaml
package_id: VP-I03-P31-01
slice_id: VP-I03
name: PLATFORM_SKILL_INTEGRATION_AND_ECV0_QUALIFICATION
stage_owner: aegis-implementation
execution_surface_now: CONTROL_REASONING
preferred_p32_surface: CODE_EXECUTION
preferred_executor: codex
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/76

task_anchor:
  revision: 674e01737621621b8131e35f83313fb0154a9f6d
  relation: ancestor

resume_cursor: null
```

The exact executable `package_ref` is the final commit containing this document and is recorded externally by the P31 result / PR metadata after materialization. This document does not embed the future commit SHA that contains itself.

A future P32 MUST resolve repository identity first, then this same-repository PR #76 and exact final `package_ref`, then verify the task-anchor ancestry and the accepted predecessor chain below before mutation.

---

## 2. Exact trusted basis

```yaml
main_baseline_at_p30: 342d6785d8f54dd9beb2c3bb82398f29b405df2f
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

These are `ACCEPTED_FOR_DOWNSTREAM` design/verification inputs; they are not silently published as Current `.aegis` Authority by this package.

### Accepted VP-I01 predecessor

```yaml
vp_i01:
  result_revision: ef995501c3dcd1f7f608083028f43bb4bde66103
  materialized_ref: https://github.com/Mostorm-Labs/aegis/pull/71
  p34_gate_review: 5121366259
  p34_verdict: PASS
  p24_readiness_review: 5121383523
  p24_disposition: READY_FOR_STACK_LOCAL_INTEGRATION
  governing_package_id: VP-I01-P31-02
  governing_package_ref: b979f1fc59178c16285449a92f02dd5964e523d0
```

### Immediate accepted VP-I02 predecessor

```yaml
vp_i02:
  result_revision: 8b98a58874268a8d6fae05d0406bd795a311f041
  materialized_ref: https://github.com/Mostorm-Labs/aegis/pull/74
  p34_gate_review: 5121578992
  p34_verdict: PASS
  p24_readiness_review: 5121589661
  p24_disposition: READY_FOR_STACK_LOCAL_INTEGRATION
  governing_package_id: VP-I02-P31-01
  governing_package_ref: 9a724830992d27681b223c8b424891e46623aeed
  p36_evidence_ref: 3f6e51fd9364793eb4694c0a9ba56c4366b14231
```

The expected clean P32 starting revision is the final VP-I03 package head, which is a descendant of exact accepted VP-I02 result `8b98a588...`. Historical equality to the P20 task anchor is not required; ancestry is required.

If the observed starting revision is not a descendant of `8b98a588...`, or if descendant changes alter accepted VP-I01/VP-I02 Proof Runtime semantics before P32 starts, stop fail-closed rather than silently reconciling a semantic fork.

---

## 3. Purpose and final-slice boundary

P30 defines exactly three Verification Productization implementation slices:

```text
VP-I01  Exact Contract & Package Preflight
  -> VP-I02  Evidence Compilation & Independent Review Runtime
    -> VP-I03  Platform / Skill Integration & ECV0 Qualification
```

VP-I03 is the final implementation slice in that P30 plan. Its job is to connect the already-accepted deterministic Proof Runtime to real Aegis execution surfaces and prove the complete ECV0 profile without duplicating proof semantics in workflow YAML, prompts, shell wrappers, hand-written summaries, or provider-specific code.

This slice primarily closes or fully qualifies P20 requirements R6-R16 at the installed/platform boundary while rerunning the complete R1-R17 deterministic corpus as one qualification set.

Normative identity separation remains:

```text
machine observation
!= EvidenceArtifact / EvidenceInputRef
!= implementation result
!= ProofEvaluation
!= P34 Gate Decision
```

No new service, daemon, external database, third-party Python dependency, canonical ProofFact family, second Gate, or second source of proof truth is authorized.

---

## 4. Exact P32 authored scope

Authorization mode:

```yaml
authorization_mode: EXACT_PATH_SET
expected_p32_changed_path_count: 31
```

The expected count is the exact implementation/result diff from the final VP-I03 P31 package ref. Runtime-generated evidence files under temporary/local `artifacts/` directories are not authored result paths and MUST NOT be committed merely to satisfy this count.

### 4.1 Create exactly these 13 paths

```text
tools/aegis_proof/adapters/__init__.py
tools/aegis_proof/adapters/local_runner.py
tools/aegis_proof/adapters/github_actions.py
tools/aegis_proof/adapters/repository.py
tools/aegis_proof/cli.py
tools/aegis_proof/__main__.py
tests/verification_productization/ecv0_fixtures.py
tests/verification_productization/test_provider_adapters.py
tests/verification_productization/test_cli_parity.py
tests/verification_productization/test_ecv0_scenarios.py
tests/verification_productization/test_ecv0_mutants.py
tests/verification_productization/run_ecv0.py
.github/workflows/verification-productization-ecv0.yml
```

### 4.2 Modify exactly these 5 canonical Skill source paths

```text
skillset/shared/handoff-contract.md
skillset/skills/aegis-implementation/SKILL.md
skillset/skills/aegis-implementation/references/implementation-control.md
skillset/skills/aegis-gate-review/SKILL.md
skillset/skills/aegis-gate-review/references/gate-review.md
```

### 4.3 Mechanically regenerate exactly these 13 distribution outputs

The current `skillset/manifest.json` assigns shared `handoff-contract` to all nine canonical Skills, and `build_skillset.py` copies canonical Skill files plus shared refs into their `skills/**` distribution paths. Therefore the canonical edits above are expected to change exactly these generated outputs:

```text
skills/aegis/references/shared/handoff-contract.md
skills/aegis-project-state/references/shared/handoff-contract.md
skills/aegis-discovery/references/shared/handoff-contract.md
skills/aegis-modeling/references/shared/handoff-contract.md
skills/aegis-architecture/references/shared/handoff-contract.md
skills/aegis-verification/references/shared/handoff-contract.md
skills/aegis-governance/references/shared/handoff-contract.md
skills/aegis-implementation/references/shared/handoff-contract.md
skills/aegis-gate-review/references/shared/handoff-contract.md
skills/aegis-implementation/SKILL.md
skills/aegis-implementation/references/implementation-control.md
skills/aegis-gate-review/SKILL.md
skills/aegis-gate-review/references/gate-review.md
```

These generated paths MUST be produced by:

```bash
python3 scripts/build_skillset.py --write
```

They MUST NOT be hand-edited independently of canonical `skillset/**` sources.

If `build_skillset.py --write` changes any additional `skills/**` path, stop and return a scope/package blocker. Do not widen the package inside P32.

### 4.4 Explicitly forbidden authored mutation

```text
tools/aegis_proof/__init__.py
tools/aegis_proof/domain.py
tools/aegis_proof/spec.py
tools/aegis_proof/obligations.py
tools/aegis_proof/package.py
tools/aegis_proof/ports.py
tools/aegis_proof/evidence.py
tools/aegis_proof/evaluation.py
tools/aegis_proof/review.py
tools/aegis_control/**
tools/aegis_state/**
tools/aegis_skillset/**
other skillset/** paths not listed above
other skills/** paths not listed above
plugins/aegis/**
.aegis/**
other .github/workflows/** files
scripts/**
tests/control_plane/**
tests/project_state/**
tests/skillset/**
release manifests / tags / GitHub releases
VP-I01 / VP-I02 package or historical evidence rewrites
```

The existing P20/P30 design explicitly keeps published `plugins/aegis/**` beta.3 materialization immutable. Candidate Plugin parity is evidence only and MUST be generated through the existing script without rewriting the published Plugin tree.

---

## 5. Adapter contracts

### 5.1 Local runner adapter

`tools/aegis_proof/adapters/local_runner.py` converts one completed local process/report into `ObservationBatch` only after process termination, structured report finalization, and complete expected record/end-condition verification.

Required fail-closed behavior:

- truncated process/report -> `complete=False`;
- missing required record set -> incomplete evidence;
- never infer zero failures from missing output;
- local paths are staging/navigation only and never reviewer-resolvable durable identity by themselves.

### 5.2 GitHub Actions adapter

`tools/aegis_proof/adapters/github_actions.py` consumes provider-qualified run/job metadata using exact:

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

It MUST reject wrong revision, `latest` without exact run identity, missing required job/matrix child, incomplete run/job state, and artifact-name-only identity.

The workflow artifact MUST NOT be required to contain the future terminal conclusion of the same run that uploads it. P34 resolves terminal/completeness state externally from exact provider identity.

### 5.3 Repository adapter

`tools/aegis_proof/adapters/repository.py` represents exact repository artifact/result bindings. Repository identity includes repository namespace plus exact commit/native object plus path/native ID plus digest when required by the frozen contract.

Branch name, PR title/number, cwd, and bare SHA remain navigation unless paired with the exact selected repository-qualified identity.

Cross-repository fallback is forbidden unless explicitly authorized by a future package; this package authorizes only `Mostorm-Labs/aegis`.

---

## 6. Structured CLI contract

`python3 -m tools.aegis_proof` MUST expose deterministic JSON-in/JSON-out subcommands exactly:

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

1. UTF-8 JSON input;
2. stdout emits one structured JSON result only;
3. human diagnostics go to stderr;
4. nonzero exit means validation/contract/runtime failure and does not rewrite semantic truth;
5. CLI delegates to the same accepted library functions used by unit tests;
6. no duplicated proof/evaluation rules in CLI argument parsing or presentation logic.

`EC-S17` / adapter parity MUST compare canonical semantic outputs from direct library invocation and CLI/provider-adapter invocation for the same exact fixtures.

---

## 7. Canonical Skill integration contract

### 7.1 `aegis-implementation`

The canonical Skill/reference must explicitly require before repository-backed P32/P33 execution:

1. exact VerificationSpec / obligation-set / TrustedBasis / scope / acceptance-oracle / evidence-compilation bindings;
2. `PackageBindingPreflight` success;
3. `EvidenceContractPreflight` success;
4. repository identity preflight before package/anchor/cursor resolution;
5. no floating accepted labels passed to Codex/executor;
6. no manually typed proof totals when EvidenceArtifact/ProofEvaluation owns those facts;
7. exact return navigation: `result_revision`, `materialized_ref`, `evidence_input_refs`, and exact provider run refs required by package.

### 7.2 `aegis-gate-review`

The canonical Skill/reference must explicitly require P34 to:

1. independently resolve exact package/result/evidence/provider identities;
2. establish provider run applicability and completion;
3. establish independent obligation completeness;
4. apply `ReviewContractDiffer` when a new Gate requirement appears;
5. route `UNDECLARED` / `STRUCTURALLY_UNSATISFIABLE` requirements to the owning earlier layer instead of retroactive P32 repair;
6. never treat ProofEvaluation, green CI, or summary prose as official Gate PASS.

### 7.3 Shared handoff return contract

The canonical execution-return example may carry:

```yaml
result_revision: <exact result>
materialized_ref: <reviewer-resolvable exact result ref>
evidence_input_refs:
  - <exact EvidenceInputRef>
provider_run_refs:
  - <exact provider run identity>
```

It MUST NOT introduce independently authored duplicate proof totals such as `tests_passed`, `tests_skipped`, copied obligation totals, or copied ProofEvaluation metrics.

---

## 8. Complete ECV0 deterministic scenario corpus

`tests/verification_productization/test_ecv0_scenarios.py` and the shared fixture corpus MUST materialize all exact P20 scenario identities `EC-S01..EC-S17`.

Required semantics are frozen as follows:

```text
EC-S01 authoritative machine facts beat conflicting manual totals
EC-S02 floating accepted/latest dependency is blocked before P32
EC-S03 future-self artifact/commit identity is structurally unsatisfiable
EC-S04 undeclared Gate-critical field routes to owning earlier layer
EC-S05 external evidence rematerialization may preserve unchanged result identity
EC-S06 result-byte mutation changes result identity
EC-S07 local-only evidence is not review-ready
EC-S08 CI for the wrong result revision is rejected
EC-S09 missing/incomplete required matrix child is incomplete evidence
EC-S10 mutable/latest/artifact-name-only lookup is rejected at trust boundary
EC-S11 durable artifact identity survives signed-URL rotation/expiry
EC-S12 reviewer-inaccessible required artifact blocks review
EC-S13 cross-repository fallback for package/ref SHA is rejected
EC-S14 copied handoff/manifest totals cannot override exact evidence/evaluation
EC-S15 independent completeness detects omitted obligation
EC-S16 green CI + clean evaluation cannot compensate for unresolvable result
EC-S17 library / CLI / provider adapter semantic outputs are canonically equivalent
```

Every scenario record must be machine-identifiable by exact ID. No scenario may be marked PASS by manually authored aggregate input.

---

## 9. Complete ECV0 mutant qualification

`tests/verification_productization/test_ecv0_mutants.py` MUST materialize and machine-kill all exact P20 mutants `EC-M01..EC-M17`:

```text
EC-M01 manual total overrides authoritative total
EC-M02 floating accepted dependency reaches P32
EC-M03 future-self identity admitted
EC-M04 undeclared P34 field becomes old P32 repair
EC-M05 changed result bytes retain old result SHA
EC-M06 local path/transcript treated as reviewer-resolvable evidence
EC-M07 latest green CI selected regardless of result revision
EC-M08 missing matrix child ignored
EC-M09 artifact/branch name trusted without exact identity
EC-M10 temporary signed URL persisted as immutable identity
EC-M11 resolvable SHA followed into wrong repository
EC-M12 reviewer-inaccessible required evidence accepted
EC-M13 green CI / ProofEvaluation treated as Gate PASS
EC-M14 handoff summary overrides exact source totals
EC-M15 generator output used as sole completeness expected-set oracle
EC-M16 adapter/workflow/prompt reimplements and weakens deterministic semantics
EC-M17 missing/incomplete provider data becomes zero failures
```

Acceptance requires every mutant detected with `mutant_false_acceptance: 0`. Purpose-built negative fixtures are sufficient; no generic mutation-testing framework is authorized.

The already-accepted VP-I01/VP-I02 implementation is the production baseline for mutants that target predecessor behavior. P32 may add qualification wrappers/fixtures in the authorized VP-I03 test paths, but it may not reopen predecessor production files merely to simplify mutation tests.

---

## 10. ECV0 structured runner contract

`tests/verification_productization/run_ecv0.py` must derive its output from per-case records and emit structured output containing:

```json
{
  "profile": "ECV0",
  "source_revision": "<runtime-resolved exact git HEAD>",
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

The numbers are acceptance targets, not command-line inputs. Aggregate values MUST be derived from exact records and the runner MUST exit nonzero when targets are not met.

---

## 11. Dedicated GitHub Actions workflow contract

Create `.github/workflows/verification-productization-ecv0.yml` with these exact responsibilities:

1. checkout the exact candidate;
2. use Python 3.12;
3. run full `tests/verification_productization`;
4. run inherited Control Plane regressions;
5. run Project State regressions;
6. run Skillset regressions;
7. run `python3 scripts/build_skillset.py --check`;
8. run `python3 -m tools.aegis_skillset.cli distribution-check .`;
9. run `python3 tests/verification_productization/run_ecv0.py --output artifacts/ecv0/ecv0.json`;
10. run `python3 scripts/build_candidate_plugin_parity.py --output artifacts/ecv0/candidate-plugin-parity.json`;
11. validate both JSON files with `python3 -m json.tool`;
12. upload evidence with an exact-candidate-qualified artifact name and finite retention;
13. never modify `plugins/aegis/**` or publish a release.

The workflow does not self-certify P34 applicability. CONTROL_REVIEW must independently resolve exact run ID/attempt, terminal conclusion, required jobs/matrix children, artifact identity, and exact result revision.

---

## 12. Fresh platform corroborations and phase ownership

The final ECV0 Gate target requires four real platform observations:

```text
EC-PFC01 Codex repository / exact package preflight
EC-PFC02 Codex/local evidence durability boundary
EC-PFC03 GitHub Actions exact-result + completion applicability
EC-PFC04 CONTROL_REVIEW independent resolution
```

### `EC-PFC01` — P32/P33 execution-phase evidence

Actual repository-backed Codex execution must demonstrate declared `Mostorm-Labs/aegis` identity is established before package/ref/anchor/cursor use and that ambient wrong-repository/bare-SHA context cannot redirect mutation.

### `EC-PFC02` — P32/P33 execution-phase evidence

Actual execution must demonstrate local-only test/report artifacts are not called review-ready before exact durable materialization exists.

### `EC-PFC03` — post-result provider evidence before P34

An exact candidate GitHub Actions run must be terminal, account for required jobs/matrix children, bind artifacts to exact candidate identity, and be independently addressable by exact run/attempt/artifact identities.

### `EC-PFC04` — **P34_REVIEW phase only**

`EC-PFC04` is produced by fresh CONTROL_REVIEW / `aegis-gate-review`, not by P32. P32 MUST NOT claim `EC-PFC04: PASS`, synthesize a Gate decision, or make its own return depend on a future P34 verdict.

The package therefore freezes this satisfiable phase boundary:

```yaml
p32_required_platform_observations:
  EC-PFC01: required
  EC-PFC02: required
  EC-PFC03: required
  EC-PFC04: pending_p34_control_review

final_ecv0_gate_target:
  EC-PFC01: PASS
  EC-PFC02: PASS
  EC-PFC03: PASS
  EC-PFC04: PASS
```

P32 may return `READY_FOR_CONTROL_REVIEW` only when all inputs needed for independent `EC-PFC04` are durably reviewer-resolvable. P34 alone decides whether that observation passes.

---

## 13. Evidence families and materialization obligation

The complete ECV0 evidence graph uses the P20 families:

```text
ECV-E01 requirement/claim/obligation trace
ECV-E02 deterministic scenario records
ECV-E03 mutant qualification records
ECV-E04 exact provider applicability/completion objects
ECV-E05 fresh installed-platform corroboration refs
ECV-E06 exact candidate result materialization
ECV-E07 ProofEvaluation + independent completeness refs
ECV-E08 derived P34 ReviewBundle navigation
```

Rules:

1. counts/totals are derived from structured records only;
2. every required cross-boundary artifact is exact and reviewer-resolvable;
3. signed URLs/credentials are access mechanisms, not durable identities;
4. ECV-E08 is navigation only and does not duplicate machine facts;
5. result identity remains distinct from evidence identity;
6. failed/historical evidence remains immutable when repaired evidence is materialized;
7. platform refs bind exact result/provider occurrences;
8. P32 must materialize the exact implementation result at a reviewer-accessible durable ref and return that `materialized_ref`;
9. local-only transcripts are insufficient for P34;
10. external evidence-only materialization must not mutate the exact implementation result bytes.

---

## 14. TDD and test ownership

P32 implementation MUST use RED -> minimal GREEN. Do not first implement adapters/CLI/Skill changes and add tests afterward.

### Initial RED set

Before production implementation, add failing tests covering at least:

```text
EC-S07 / EC-M06 local-only durability
EC-S08 / EC-M07 exact-result applicability
EC-S09 / EC-M08 / EC-M17 provider completion
EC-S10 / EC-M09 mutable/latest identity rejection
EC-S11 / EC-M10 signed URL non-identity
EC-S12 / EC-M12 reviewer access
EC-S13 / EC-M11 repository namespace integrity
EC-S17 / EC-M16 adapter semantic parity
```

The full scenario/mutant files still enumerate all 17/17 and exercise predecessor behavior without reopening predecessor production code.

Recommended ownership:

```text
test_provider_adapters.py
  provider/repository/local adapter negatives and applicability/completion

test_cli_parity.py
  structured CLI library parity, especially EC-S17 / EC-M16

test_ecv0_scenarios.py
  exact EC-S01..EC-S17 corpus

test_ecv0_mutants.py
  exact EC-M01..EC-M17 qualification
```

---

## 15. Skill generation and parity commands

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

The parity artifact describes the candidate only and does not authorize Plugin publication.

---

## 16. Full qualification commands

Fresh completion evidence at the exact P32 result must include the full applicable command set:

```bash
python3 -m unittest discover -s tests/verification_productization -v
python3 -m unittest discover -s tests/control_plane -v
python3 -m unittest discover -s tests/project_state -v
python3 -m unittest discover -s tests/skillset -v
python3 scripts/build_skillset.py --check
python3 scripts/validate_generated_skills.py
python3 -m tools.aegis_skillset.cli validate .
python3 -m tools.aegis_skillset.cli routing-check .
python3 -m tools.aegis_skillset.cli distribution-check .
python3 tests/verification_productization/run_ecv0.py \
  --output artifacts/ecv0/ecv0.json
python3 -m json.tool artifacts/ecv0/ecv0.json >/dev/null
python3 scripts/build_candidate_plugin_parity.py \
  --output artifacts/ecv0/candidate-plugin-parity.json
python3 -m json.tool artifacts/ecv0/candidate-plugin-parity.json >/dev/null
```

The dedicated GitHub Actions workflow must independently run the P30-required hosted subset at the exact candidate.

No completion/readiness claim is valid from partial or stale command output.

---

## 17. P32 execution exit criteria

P32 may return `READY_FOR_CONTROL_REVIEW` only when all of the following are established for one exact candidate result:

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

p32_platform_corroboration:
  EC-PFC01: evidence_materialized
  EC-PFC02: evidence_materialized
  EC-PFC03: exact_terminal_provider_refs_materialized
  EC-PFC04: pending_p34_control_review

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

full_local_qualification: PASS
skill_generation_parity: PASS
candidate_plugin_parity: PASS
result_materialized: true
required_evidence_reviewer_resolvable: true
p34_claimed_by_p32: false
```

The executor return carries exact refs/navigation only. It does not manually copy scenario totals as an alternate evidence source.

---

## 18. Final P34 ECV0 acceptance target

The later independent P34 Gate may issue PASS only if it independently resolves the exact package/result/evidence/provider graph and establishes:

```yaml
deterministic_scenarios: 17/17 PASS
mutants_detected: 17/17
mutant_false_acceptance: 0
fresh_platform_corroborations: 4/4 PASS
zero_tolerance_events: all_zero
independent_obligation_completeness: PASS
provider_applicability_and_completion: PASS
result_and_required_evidence_reviewer_resolvable: true
formal_gate_owner: aegis-gate-review
```

P32/CI/ProofEvaluation/runner summaries cannot issue this verdict.

---

## 19. Performance / security / environment constraints

- Python 3.12 standard library only; no third-party Python dependency is authorized.
- No new throughput/latency/resource target is introduced; P18 remains unnecessary for this correctness/integration slice unless implementation discovers a real new performance contract.
- Credentials and temporary signed URLs must never be serialized as durable evidence identity.
- No service, daemon, queue, external DB, or new network control plane is authorized.
- Provider access is used only through existing repository/GitHub/Actions surfaces needed for exact evidence resolution.
- Existing Control Plane, Project State, Skillset, and distribution validation remain mandatory regressions.

---

## 20. Blocked-return behavior

P32 must stop rather than widen or reinterpret this package in these cases:

### Repository / ancestry

```yaml
status: BLOCKED_REPOSITORY_IDENTITY
continue_execution: false
```

for wrong/missing/ambiguous repository identity or unresolvable same-repository package materialization.

Use `BLOCKED_EXECUTION_DIVERGENCE` when the accepted VP-I02 predecessor/task-anchor ancestry cannot be established or incompatible descendant work rewrites the trusted baseline.

### Earlier semantic/design gap

```yaml
status: BLOCKED_AUTHORITY
earliest_untrusted_layer: <exact owning earlier layer>
continue_execution: false
```

when implementation would require inventing or weakening P12/P15/P17/P20 semantics.

### Scope/package gap

If implementation requires any authored path outside the exact 31-path set, or skill regeneration changes an unexpected distribution path, stop and request P31 reclassification/repackage. Do not silently add files.

### Evidence/platform gap

Return `BLOCKED_EVIDENCE` or `BLOCKED_ENVIRONMENT` when a required exact/reviewer-resolvable provider/platform identity cannot be produced or resolved. Do not replace it with copied prose or a local path.

### Implementation/test defect

Return `BLOCKED_IMPLEMENTATION` for in-scope implementation/test defects that prevent the required qualification target; a later P35/P36 may repair only after independent Gate classification if P34 is reached.

### P34 phase boundary

P32 must never block waiting for its own future P34 verdict. It prepares exact inputs for `EC-PFC04`; CONTROL_REVIEW creates that observation independently.

---

## 21. P31 exit

```yaml
stage: P31_TASK_PACKAGING
owner: aegis-implementation
package_id: VP-I03-P31-01
repository: Mostorm-Labs/aegis
package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/76
accepted_predecessor: 8b98a58874268a8d6fae05d0406bd795a311f041
task_anchor: 674e01737621621b8131e35f83313fb0154a9f6d
resume_cursor: null
status: MATERIALIZED_READY_FOR_EXPLICIT_P32_START
implementation_execution_authorized: false
p32_started: false
p34_pass_issued: false
main_merge_authorized: false
release_authorized: false
authority_publication_complete: false
```

A new explicit user turn is required before P32 implementation begins. The future CODE_EXECUTION handoff must carry the exact final `package_ref`, this PR #76, the stable task anchor, and `resume_cursor: null` unless an accepted continuation cursor is later established.
