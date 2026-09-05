# Aegis Verification Productization v0.1 — P20 Targeted Evidence Contract Regression Design

Status: **Draft / Proposed Verification Authority — P20 targeted Evidence Contract regression design**

Scope: `aegis/verification-productization/verification`

This document defines the minimum credible proof needed to verify the Verification Productization Evidence Contract Completion produced by P15-P17. It is intentionally targeted: it closes the real Evidence Contract Churn incident family without creating a new verification service, monolithic proof bundle, or large synthetic qualification framework.

---

# 1. Exact trusted basis

This P20 design consumes the following exact upstream basis:

```yaml
repository: Mostorm-Labs/aegis
external_current_baseline: 342d6785d8f54dd9beb2c3bb82398f29b405df2f

semantic_basis: 12c968c5c481ad671ce33bcfa088ba8a2fca0f43
semantic_recertification_review: 5121012716

p14_architecture_basis: d9c8f6ac5db4359400fae06e76c51c65bd059bfc
p15_module_design_basis: 665292dcfd7781935243369ee9f676c320f2878a
p16_runtime_flow_basis: 708cf09c01effbcc63c65d45b9b4a67b7a8fc8db
p17_platform_contract_basis: c8f47d049be50d65f88b04ad141650ed6dfdb826

evidence_contract_churn_p21: 5119525139
evidence_contract_churn_p22: 5119537168
```

Retained Current external contracts include:

- Control Plane exact `CanonicalRef`, `TrustedBasis`, and `VerificationBoundImplementationPackage` semantics;
- Current Execution Surface v0.2 exact result materialization and `Task Anchor != Execution Cursor` semantics;
- Current repository-identity rule `Repository Identity != Task Anchor != Execution Cursor`;
- Project State immutable Authority / Evidence / Gate / Integration lineage;
- P34 as the sole formal Gate verdict owner;
- P35 owning-layer classification and P36 repair/reverification;
- existing Control Plane verification right-sizing: evidence strength must match Claim strength, composite reviewer-resolvable evidence is allowed, and a dedicated new verification product is not required.

This P20 design does not reinterpret the Draft/Proposed Proof Plane package as Current `.aegis` Authority. It is an exact downstream verification candidate that must still pass fresh Governance review.

---

# 2. Verification objective

Prove that the reusable Proof Runtime cannot silently convert ambiguous, incomplete, mutable, inaccessible, mis-scoped, or manually retyped data into trusted evidence or a false clean review state.

The controlling chain is:

```text
Requirement
  -> Invariant
  -> Oracle / Reference
  -> Fixture / Corpus
  -> Test / Probe
  -> Metric / Verdict
  -> Evidence Artifact
  -> P34 Gate
```

The central verification principle is:

> **Exact trust boundaries must fail closed before or at the first layer that can establish the contradiction. Later convenience must never repair trust by guessing.**

For machine-observable facts:

> **Producer-owned structured observations are authoritative; copied prose, hand-entered summaries, or navigation labels are not competing truth.**

For review:

> **ProofEvaluation and green CI are review inputs, not Gate verdicts. P34 independently resolves exact applicability and completeness.**

---

# 3. Verification profile and non-goals

The mandatory targeted profile is named:

```text
ECV0 = Evidence Contract Verification Profile v0.1
```

`ECV0` is a bounded regression profile, not a new product or service.

It must be implementable using the deterministic Proof Runtime modules, repository tests/fixtures, provider adapters, and a small fresh installed-platform corroboration set.

This P20 design does **not**:

- reopen P02/P03, P10-P13, or redesign P14-P17;
- require P18 performance work;
- introduce a standalone verifier daemon or always-on service;
- require a fixed 40-WorkScope PP0-style corpus;
- require one monolithic evidence bundle;
- require every proof artifact to live in Git;
- require public artifact access when the intended reviewer has valid private access;
- authorize P30/P31/P32 implementation;
- issue a P34 verdict;
- merge PRs, publish Authority, or release a product.

---

# 4. Requirement-to-Claim map

## `ECV-R01 / ECV-C01 — Authoritative fact single source` — R1

**Requirement.** For each machine-observable fact family, the frozen EvidencePlan identifies the authoritative producer. Derived counts/metrics are computed once from that producer's structured data or preserved from its authoritative native summary.

**Claim.** A conflicting hand-entered or executor-authored summary cannot override the authoritative machine fact.

**Invariant.** If the authoritative source says `445 PASS / 23 SKIP`, an independently entered `25 SKIP` cannot be accepted as equivalent evidence.

---

## `ECV-R02 / ECV-C02 — Exact accepted dependency binding` — R2

**Requirement.** Every Gate-critical accepted dependency is resolved into an exact immutable `CanonicalRef` / `TrustedBasis` / package binding before P32.

**Claim.** Labels such as `accepted A4`, `latest Gate`, `current result`, or `previous accepted baseline` never cross the executable trust boundary unresolved.

**Invariant.** The executor never chooses which accepted result the package meant.

---

## `ECV-R03 / ECV-C03 — Evidence-contract satisfiability` — R3

**Requirement.** `EvidenceContractPreflight` rejects future-self identity cycles and any requirement whose value can exist only after materializing the same bytes whose content requires that value.

**Claim.** An EvidenceArtifact is never required to embed the SHA/ref of the commit or immutable object whose identity depends on that same artifact content.

**Invariant.** Artifact content precedes its own immutable locator; final materialization identity is carried externally by `EvidenceInputRef` or result occurrence metadata.

---

## `ECV-R04 / ECV-C04 — Frozen review contract / post-hoc delta ownership` — R4

**Requirement.** A Gate-requested requirement absent from the frozen VerificationSpec / ProofContract / P31 package is classified by `ReviewContractDiffer` as undeclared or structurally unsatisfiable and routed to the owning earlier layer.

**Claim.** P34 cannot silently transform a new Gate-critical field into a historical P32 executor obligation.

**Invariant.** Historical package/spec/evidence remains immutable; a genuinely needed missing requirement creates an upstream repair/new revision.

---

## `ECV-R05 / ECV-C05 — Evidence-only repair preserves exact result only when truly external` — R5

**Requirement.** When implementation semantics/result remain valid and only evidence compilation, binding, or materialization is defective, repair may create a new immutable EvidenceArtifact / EvidenceInputRef / ProofEvaluation without source implementation mutation.

**Claim.** Evidence-only repair can preserve the same exact `result_revision/materialized_ref` only if the repaired evidence materializes independently of the result commit.

**Invariant.** If repairing evidence changes bytes inside the implementation result commit, the implementation result identity changes and must not be reported as unchanged.

---

## `ECV-R06 / ECV-C06 — Local-only evidence cannot satisfy reviewer-resolvable proof`

**Requirement.** A required deterministic proof input must be materialized at an exact reviewer-resolvable durable boundary.

**Claim.** Local filesystem paths, worktree state, stdout/stderr, and local-only commit objects cannot independently satisfy a P34 evidence requirement.

**Invariant.** No reviewer-resolvable durable ref -> no deterministic evidence readiness.

---

## `ECV-R07 / ECV-C07 — Exact-result provider applicability`

**Requirement.** CI/provider evidence is bound to the exact repository and result revision it actually proves, including provider-native run/attempt identity where relevant.

**Claim.** A newer or green provider run for another revision cannot substitute for the run bound to the reviewed exact result.

**Invariant.** Recency, branch position, and green status do not establish applicability.

---

## `ECV-R08 / ECV-C08 — Provider completion and matrix completeness`

**Requirement.** An authoritative provider observation is usable only after its contract-defined terminal/completion barrier is established. Multi-job/matrix evidence is complete only when all required children are accounted for.

**Claim.** Partial arrival, missing matrix jobs, interrupted reports, or absent end-of-stream state cannot be summarized as zero failures.

**Invariant.** Missing completion is missing evidence, not success.

---

## `ECV-R09 / ECV-C09 — Mutable/latest lookup rejection`

**Requirement.** Mutable PR/branch names, `latest run`, artifact names, workflow names, or equivalent navigation aliases are not trust-boundary identities by themselves.

**Claim.** Evidence resolution cannot drift when a branch moves or a later run/artifact receives the same human-readable name.

**Invariant.** Exact selected commit/run/artifact/content identity controls trust.

---

## `ECV-R10 / ECV-C10 — Durable artifact identity != temporary access URL`

**Requirement.** Durable evidence identity is represented by provider-qualified immutable/native identity and/or digest. Credentials and temporary signed URLs remain runtime access mechanisms.

**Claim.** Expiring download URLs or credentials are never serialized as the durable evidence identity.

**Invariant.** Loss of a temporary access token does not rename evidence; loss of all reviewer-resolvable access before the required boundary blocks review.

---

## `ECV-R11 / ECV-C11 — Repository namespace integrity`

**Requirement.** Repository identity is established before package/ref/anchor/cursor/provider resolution. Cross-repository fallback is forbidden unless the package explicitly governs multiple repositories.

**Claim.** A bare SHA or ambient cwd/session context cannot redirect execution or evidence lookup into another repository.

**Invariant.** Wrong-repository resolvability never becomes proof of intended repository ownership.

---

## `ECV-R12 / ECV-C12 — Reviewer read capability is part of evidence readiness`

**Requirement.** At the relevant P34 boundary, the intended independent reviewer must be able to retrieve and verify every required exact evidence object under authorized platform access.

**Claim.** A private artifact is acceptable when reviewer access exists; an inaccessible artifact is not accepted merely because an executor says it once existed.

**Invariant.** Copied metadata/narrative cannot replace inaccessible required evidence.

---

## `ECV-R13 / ECV-C13 — Result identity and evidence identity remain distinct`

**Requirement.** Implementation `result_revision/materialized_ref`, EvidenceInputRefs, ProofEvaluation identity, provider run identities, and P34 Gate Decision remain separate exact identities.

**Claim.** A result commit is not automatically an EvidenceInputRef, an EvidenceInputRef is not a Gate verdict, and a green CI run is not result materialization.

**Invariant.** Review navigation may connect these identities but cannot collapse them.

---

## `ECV-R14 / ECV-C14 — Handoff / manifest summaries are derived only`

**Requirement.** P32/P33/P36 returns and thin manifests carry exact refs/navigation, not independently authored proof totals already owned by EvidenceArtifact/ProofEvaluation.

**Claim.** Fields such as manually typed `tests_passed`, `tests_skipped`, derived obligation totals, or copied metric values cannot become a second source of truth.

**Invariant.** Summary views are mechanically derived from exact underlying records.

---

## `ECV-R15 / ECV-C15 — P34 independent resolution remains mandatory`

**Requirement.** CONTROL_REVIEW independently resolves the accepted basis, package, repository, exact result, required EvidenceInputRefs, provider applicability/completion, ProofEvaluation, completeness evidence, exceptions, and contract-diff state.

**Claim.** `VerificationSummary.READY`, zero deterministic failures, green CI, or executor/assistant prose cannot issue or imply official P34 PASS.

**Invariant.** Formal Gate verdict ownership remains exclusively P34 / `aegis-gate-review`.

---

## `ECV-R16 / ECV-C16 — Adapter semantic parity`

**Requirement.** Library, structured CLI, CI wrapper, and provider adapters invoke the same accepted deterministic semantics rather than reimplementing Proof rules in prompts, shell text, or workflow YAML.

**Claim.** The same exact inputs yield semantically equivalent validation/generation/compilation/evaluation outcomes independent of adapter surface.

**Invariant.** Platform translation may change transport representation, not trust semantics.

---

## `ECV-R17 / ECV-C17 — Independent completeness oracle`

**Requirement.** The review-side completeness checker derives the expected obligation set from exact VerificationSpec semantics through an independently owned traversal. It may share canonical identity codecs, but not the generator traversal as its sole expected-set oracle.

**Claim.** A generator omission cannot self-certify the resulting incomplete obligation set as complete.

**Invariant.** `generated obligation set != completeness oracle`.

---

# 5. Oracle / reference set

`ECV0` uses a bounded six-oracle model.

## `O-EC-CONTRACT — Exact contract oracle`

Inspects the exact P12/P15/P16/P17 schemas and package/evidence/review contracts. It establishes what fields/identities are required, when they may exist, and which owner may create them.

## `O-EC-PREFLIGHT — Package + evidence satisfiability oracle`

Exercises `PackageBindingPreflight`, `EvidenceContractPreflight`, repository identity preflight, and platform capability preflight against exact fixtures.

Expected behavior is fail-closed before P32 for unresolved dependency, future-self identity, impossible provider phase, ambiguous repository, and reviewer-inaccessible required path detected pre-execution.

## `O-EC-PRODUCER — Structured observation / Evidence Compiler oracle`

Uses authoritative structured runner/provider records as source truth and verifies deterministic compilation, single derivation of totals, producer precedence, and conflict rejection.

## `O-EC-PROVIDER — Provider applicability/completion oracle`

Uses deterministic GitHub/GitHub-Actions-shaped fixtures or provider adapter tests to verify exact-result binding, run-attempt identity, terminal state, matrix completeness, immutable artifact identity, retention/access behavior, and mutable/latest lookup rejection.

## `O-EC-REVIEW — Independent review oracle`

Exercises `IndependentCompletenessChecker`, `ReviewContractDiffer`, review-bundle identity separation, and P34-side exact ref resolution without allowing ProofEvaluation or generator output to become Gate truth.

## `O-EC-PLATFORM — Fresh installed-surface corroboration`

A small fresh corroboration set checks the real ChatGPT/Codex/GitHub boundary where deterministic unit fixtures alone cannot establish installed-platform behavior. It is not a second full verification framework.

---

# 6. Mandatory deterministic scenario corpus

The implementation plan may choose fixture file names, but the semantic scenarios below are fixed for `ECV0`.

| ID | Scenario | Required result |
|---|---|---|
| `EC-S01` | authoritative test source = `445 PASS / 23 SKIP`; conflicting manual evidence says `25 SKIP` | conflict rejected; authoritative structured result controls |
| `EC-S02` | package dependency uses `accepted A4` / `latest Gate` without exact identity | P31/preflight blocked before P32 |
| `EC-S03` | evidence schema requires artifact to contain SHA of commit containing itself | `STRUCTURALLY_UNSATISFIABLE` / pre-P32 rejection |
| `EC-S04` | P34 requests a new Gate-critical field absent from frozen spec/package | `UNDECLARED`; route to owning earlier layer, not P32 transcription repair |
| `EC-S05` | unchanged exact implementation result; faulty evidence is externally rematerialized | new EvidenceInputRef + new ProofEvaluation; same result identity allowed |
| `EC-S06` | repaired evidence requires modifying a file inside result commit | result SHA changes; cannot claim same exact implementation result |
| `EC-S07` | only `/tmp/...` or worktree path exists for required evidence | `BLOCKED_EVIDENCE` / not review-ready |
| `EC-S08` | green CI belongs to another commit than reviewed result | applicability rejected |
| `EC-S09` | matrix has one required missing/incomplete child | evidence incomplete; no false clean summary |
| `EC-S10` | resolver is given `latest run` / artifact name / moving branch only | rejected at trust boundary until exact identity selected |
| `EC-S11` | artifact durable native ID + digest exists but signed URL rotates/expires | identity remains stable; access is re-resolved; signed URL not persisted as identity |
| `EC-S12` | required artifact is inaccessible to independent reviewer at Gate | P34 blocked unless contract-permitted exact promotion/rematerialization exists |
| `EC-S13` | package/ref SHA exists only in another repository than declared repository | cross-repository fallback rejected |
| `EC-S14` | handoff/manifest contains manually copied proof totals inconsistent with exact EvidenceArtifact/ProofEvaluation | copied totals non-authoritative; mismatch cannot override exact source |
| `EC-S15` | ProofEvaluation is clean but generated obligation set omitted one expected obligation | independent completeness checker detects mismatch; P34 cannot PASS |
| `EC-S16` | CI run is green and ProofEvaluation has zero UNSATISFIED, but result materialized_ref cannot be independently resolved | P34 not review-ready / blocked evidence |
| `EC-S17` | same exact inputs executed through library and structured CLI/provider adapter | semantic outputs equivalent under canonical comparison |

All seventeen scenarios are mandatory for the targeted implementation that claims `ECV0` conformance.

---

# 7. Mandatory verifier-qualification mutant set

A verifier that only passes happy-path fixtures is insufficient for this incident family. `ECV0` therefore requires a bounded negative/mutant qualification set.

Each mutant intentionally removes or corrupts one safety condition and must be detected by the intended oracle chain.

| ID | Mutant | Must be detected |
|---|---|---|
| `EC-M01` | accept manual `25 SKIP` over authoritative `23 SKIP` | yes |
| `EC-M02` | allow floating `accepted A4` to reach P32 | yes |
| `EC-M03` | allow future-self commit SHA requirement | yes |
| `EC-M04` | convert undeclared P34 field into old P32 repair obligation | yes |
| `EC-M05` | change result commit during evidence-only repair while reporting old result SHA | yes |
| `EC-M06` | treat local path/transcript as reviewer-resolvable evidence | yes |
| `EC-M07` | select latest green CI regardless of result revision | yes |
| `EC-M08` | ignore a missing matrix child and report complete success | yes |
| `EC-M09` | trust artifact name / branch name without exact identity | yes |
| `EC-M10` | persist temporary signed URL as immutable evidence identity | yes |
| `EC-M11` | follow a resolvable SHA into another repository | yes |
| `EC-M12` | accept required evidence that reviewer cannot retrieve | yes |
| `EC-M13` | treat green CI / ProofEvaluation as official Gate PASS | yes |
| `EC-M14` | let handoff summary override exact EvidenceArtifact/ProofEvaluation totals | yes |
| `EC-M15` | use generator output as sole completeness expected-set oracle | yes |
| `EC-M16` | let workflow/prompt adapter reimplement and weaken deterministic proof semantics | yes |
| `EC-M17` | treat missing/incomplete provider data as zero failures | yes |

Mutant qualification is itself deterministic evidence. The implementation need not invent a general mutation-testing framework; purpose-built negative fixtures are sufficient when they prove the false-acceptance path is closed.

---

# 8. Fresh installed-platform corroboration

Deterministic fixtures cover most of the contract. Four fresh platform observations are additionally required for the exact implementation candidate because the real provider boundary itself is part of the Claim.

## `EC-PFC01 — Codex repository / exact package preflight`

A Codex-targeted repository-backed handoff declares `Mostorm-Labs/aegis` while ambient context exposes another repository or an unresolved bare SHA. The observed execution must remain in the declared repository or fail closed before mutation.

## `EC-PFC02 — Codex/local evidence durability boundary`

Produce a local-only test/report artifact, then demonstrate that the execution return does not claim review readiness until an exact reviewer-resolvable evidence/materialization path exists.

## `EC-PFC03 — GitHub Actions exact-result + completion applicability`

For an exact candidate revision, corroborate that the selected run/attempt is terminal, all required jobs/matrix children are accounted for, and evidence is bound to that exact revision rather than `latest`.

## `EC-PFC04 — CONTROL_REVIEW independent resolution`

From a fresh control-review surface, independently resolve the exact result materialization, required EvidenceInputRefs/provider refs, and one reviewer-access path. The observation must demonstrate that copied executor prose is unnecessary for trust.

These observations may use existing installed ChatGPT/Codex/GitHub capabilities. No standalone hosted harness is required.

---

# 9. Metrics and thresholds

The mandatory `ECV0` acceptance thresholds are exact and zero-tolerance where false acceptance is safety-critical.

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

Any nonzero zero-tolerance event blocks the affected Gate claim.

---

# 10. Evidence artifact contract

`ECV0` intentionally uses a composite evidence graph. It does not require one self-contained monolithic JSON file.

Minimum reviewer-resolvable evidence families:

```text
ECV-E01  requirement/claim/obligation trace artifact
ECV-E02  deterministic scenario result artifact
ECV-E03  mutant qualification result artifact
ECV-E04  exact provider applicability/completion artifact(s)
ECV-E05  fresh installed-platform corroboration refs
ECV-E06  exact candidate result materialization ref
ECV-E07  ProofEvaluation + independent completeness-check refs
ECV-E08  derived P34 ReviewBundle navigation
```

Rules:

1. machine counts and scenario totals are derived from structured per-case records; they are not independently re-entered in handoff prose;
2. every durable artifact crossing the trust boundary carries exact immutable/native identity and/or digest plus reviewer-resolvable ref;
3. temporary signed URLs are not the durable identity;
4. `ECV-E08` is navigation only and does not copy machine facts as a second authoritative source;
5. exact implementation result identity remains distinct from evidence identity;
6. historical failed/faulty evidence remains immutable when repaired evidence is created;
7. platform corroboration observations identify the exact candidate/result/provider occurrence they apply to.

---

# 11. Requirement -> proof mapping

The following mapping is normative at the level of proof strength; exact test file names are P30/P31 implementation detail.

| Requirement | Primary oracle | Corpus/probe | Threshold | Gate evidence |
|---|---|---|---|---|
| `R01` fact single source | `O-EC-PRODUCER` | `EC-S01`, `EC-M01`, `EC-M14`, `EC-M17` | no authoritative override | `E02/E03/E07` |
| `R02` exact dependencies | `O-EC-PREFLIGHT` | `EC-S02`, `EC-M02` | unresolved dependency admitted = 0 | `E02/E03` |
| `R03` satisfiability | `O-EC-PREFLIGHT` | `EC-S03`, `EC-M03` | self-reference admitted = 0 | `E02/E03` |
| `R04` review freeze | `O-EC-REVIEW` | `EC-S04`, `EC-M04` | misrouted post-hoc executor obligation = 0 | `E02/E03/E08` |
| `R05` evidence-only repair | contract + provider + review | `EC-S05/S06`, `EC-M05` | false same-result claim = 0 | `E02/E07/E08` |
| `R06` durability | provider/ref oracle | `EC-S07`, `EC-M06`, `EC-PFC02` | local-only accepted = 0 | `E04/E05` |
| `R07` exact-result applicability | `O-EC-PROVIDER` | `EC-S08`, `EC-M07`, `EC-PFC03` | wrong-revision acceptance = 0 | `E04/E05` |
| `R08` completion | `O-EC-PROVIDER` | `EC-S09`, `EC-M08/M17`, `EC-PFC03` | incomplete false-clean = 0 | `E02/E03/E04` |
| `R09` mutable lookup | ref resolver | `EC-S10`, `EC-M09` | mutable-only trust acceptance = 0 | `E02/E03` |
| `R10` durable identity/access | provider/ref oracle | `EC-S11/S12`, `EC-M10/M12` | signed-url identity / inaccessible acceptance = 0 | `E04/E05` |
| `R11` repository integrity | repository-identity oracle | `EC-S13`, `EC-M11`, `EC-PFC01` | wrong-repository fallback = 0 | `E02/E03/E05` |
| `R12` reviewer access | `O-EC-PLATFORM/REVIEW` | `EC-S12`, `EC-M12`, `EC-PFC04` | inaccessible required evidence accepted = 0 | `E05/E08` |
| `R13` identity separation | contract/review oracle | `EC-S16`, `EC-M13` | identity collapse causing false review readiness = 0 | `E07/E08` |
| `R14` derived summaries | producer/evaluation oracle | `EC-S14`, `EC-M14` | copied summary override = 0 | `E02/E03/E07` |
| `R15` P34 independence | `O-EC-REVIEW` | `EC-S16`, `EC-M13`, `EC-PFC04` | non-P34 PASS emission = 0 | `E08 + Gate Decision` |
| `R16` adapter parity | contract + deterministic differential | `EC-S17`, `EC-M16` | semantic differential = 0 | `E02/E03` |
| `R17` completeness independence | `O-EC-REVIEW` | `EC-S15`, `EC-M15` | omitted obligation false-complete = 0 | `E03/E07/E08` |

---

# 12. Inherited evidence and applicability

Existing repository-identity and Control Plane verification artifacts may be inherited only when their exact applicability remains valid for the candidate and the current implementation did not change the behavior they prove.

Rules:

1. exact candidate regressions take precedence over stale inherited PASS when contradictory;
2. a changed implementation surface invalidates inherited evidence for the affected Claim unless equivalence/applicability is independently established;
3. timestamps and `latest` labels never establish inheritance;
4. existing repository-identity negative scenarios may satisfy overlapping `ECV-R11` evidence when exact candidate applicability is established;
5. P20 does not require re-running unrelated Product or Control Plane proofs solely because `ECV0` is added.

---

# 13. Evidence-only repair verification rule

Because evidence-only repair caused repeated churn in the motivating incident, its proof contract is explicit.

A test claiming evidence-only repair must establish all of:

```yaml
same_frozen_package: true
same_verification_contract: true
same_implementation_result_revision: true
same_implementation_materialized_ref: true
source_implementation_change: false
new_evidence_input_ref: true
new_proof_evaluation: true
historical_faulty_evidence_preserved: true
fresh_p34_rereview_required: true
```

If repaired evidence is repository-contained and changing it changes the implementation result commit, then:

```yaml
same_implementation_result_revision: false
```

and the occurrence is not allowed to assert an evidence-only repair preserving the same exact result identity.

---

# 14. Review-contract delta verification rule

For `ECV-R04`, tests must distinguish at least:

```text
DECLARED
EXISTING_REVIEW_ONLY
UNDECLARED
STRUCTURALLY_UNSATISFIABLE
```

Required routing expectations:

- `DECLARED` -> review may evaluate the frozen requirement;
- `EXISTING_REVIEW_ONLY` -> P34 may perform the already-authorized review judgment without mutating P32 package obligations;
- `UNDECLARED` -> P35/governance routes to the owning earlier contract layer if required;
- `STRUCTURALLY_UNSATISFIABLE` -> fail closed before pretending the executor can repair it.

The verifier must never use the newly requested field itself as proof that the old package required it.

---

# 15. Provider failure semantics under test

The test oracle must preserve owning-layer cause rather than classifying every provider problem as implementation defect.

Representative expected outcomes:

```text
wrong/ambiguous repository               -> repository-identity blocker
required process/provider unavailable     -> BLOCKED_ENVIRONMENT
required provider output incomplete       -> BLOCKED_EVIDENCE
required structured report missing        -> BLOCKED_EVIDENCE or environment root cause
local-only required artifact              -> BLOCKED_EVIDENCE
mutable/unpinned artifact                 -> BLOCKED_EVIDENCE
artifact inaccessible at required review  -> BLOCKED_EVIDENCE
exact Authority/package ref unresolved    -> owning Authority/input blocker
result cannot be materialized remotely    -> BLOCKED_EVIDENCE
wrong-result CI applicability             -> BLOCKED_EVIDENCE
future-self identity cycle                -> pre-P32 contract blocker
undeclared P34 executor field              -> review delta + owning-layer classification
```

The exact public status vocabulary remains governed by existing Aegis contracts; this P20 design does not add a new status taxonomy.

---

# 16. P34 Gate interpretation

P34 may issue PASS for an implementation claiming `ECV0` conformance only when the independent review can establish all mandatory evidence for the exact reviewed candidate.

P34 must block when any of the following is true:

- any mandatory deterministic scenario fails or is missing;
- any mandatory mutant is undetected;
- mutant false acceptance is nonzero;
- any required fresh platform corroboration fails or is missing;
- exact result materialization cannot be resolved;
- a required EvidenceInputRef/provider object cannot be independently resolved;
- provider run applicability/completion is ambiguous;
- independent obligation completeness cannot be established;
- review-contract delta shows an undeclared/unsatisfiable Gate requirement that has not been repaired at its owning layer;
- result/evidence identity is collapsed or contradicted;
- a zero-tolerance event is observed.

P34 may accept a composite evidence graph. It must not require a monolithic bundle merely for convenience.

P34 remains free to identify a new valid contradiction, but a newly discovered Gate-critical requirement absent from the frozen contract must be classified/routed rather than retroactively attributed to the executor.

---

# 17. Implementation planning implications

After Governance accepts this P20 design, P30/P31 may plan the smallest implementation that can satisfy it.

Expected implementation classes include, without pre-authorizing exact files:

- deterministic canonical/ref validation for nested verification-bound packages;
- exact P31 projection and preflight enforcement;
- producer-bound ObservationSource/EvidenceCompiler path;
- EvidenceArtifact/EvidenceInputRef materialization adapters;
- review-side contract differ and independent completeness checks;
- targeted deterministic scenario fixtures and mutants;
- small installed-platform corroboration scripts/probes;
- generated/distributed Skill contract updates where existing implementation drift requires them.

P30/P31 must not replace these verification requirements with hand-authored task summaries.

---

# 18. P20 exit criteria

P20 is `READY` for Governance review when the downstream implementation team can determine, without inventing new proof semantics:

1. what exact incident/platform Claims must be proven;
2. which oracle owns each truth family;
3. which deterministic scenarios reproduce R1-R5 and P17 platform failures;
4. which mutants prove false-acceptance paths are closed;
5. what minimum fresh installed-platform corroboration is required;
6. what metrics and zero-tolerance thresholds block acceptance;
7. which evidence identities must be durable/reviewer-resolvable;
8. how evidence-only repair is distinguished from a changed implementation result;
9. how post-hoc review requirements route to the owning earlier layer;
10. why P34 remains independent and why no monolithic proof framework is required.

---

# 19. P20 disposition

```yaml
P20_targeted_evidence_contract_regression_design:
  scope: aegis/verification-productization/verification
  profile: ECV0

  semantic_basis: 12c968c5c481ad671ce33bcfa088ba8a2fca0f43
  semantic_p21_recertification: 5121012716
  p14_basis: d9c8f6ac5db4359400fae06e76c51c65bd059bfc
  p15_basis: 665292dcfd7781935243369ee9f676c320f2878a
  p16_basis: 708cf09c01effbcc63c65d45b9b4a67b7a8fc8db
  p17_basis: c8f47d049be50d65f88b04ad141650ed6dfdb826
  external_current_baseline: 342d6785d8f54dd9beb2c3bb82398f29b405df2f

  core_incident_regressions:
    R1_authoritative_fact_mismatch: REQUIRED
    R2_floating_dependency: REQUIRED
    R3_self_referential_materialization: REQUIRED
    R4_post_hoc_schema_expansion: REQUIRED
    R5_evidence_only_repair: REQUIRED

  deterministic_scenarios: 17
  mandatory_mutants: 17
  fresh_platform_corroborations: 4
  mutant_false_acceptance_threshold: 0
  zero_tolerance_safety_events: 0

  monolithic_evidence_bundle_required: false
  new_verification_service_required: false
  p18_required_now: false
  implementation_authorized: false
  gate_pass_issued: false

  status: READY_FOR_P21_AUTHORITY_REVIEW
  next_owner: aegis-governance
  next_stage: P21_AUTHORITY_REVIEW
```

Stop after P20 materialization. Do not automatically execute P21, P30, P31, P32, P34, merge, Authority publication, or release.