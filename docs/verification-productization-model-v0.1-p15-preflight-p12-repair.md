# Aegis Verification Productization Model v0.1 — P15 Preflight P12 Repair

Status: **Draft / Proposed Authority — P12 normative repair**

Scope: `aegis/verification-productization`

Base semantic package:

- `docs/verification-productization-model-v0.1.md`
- `docs/verification-productization-model-v0.1-p21-repair.md`

Previously accepted semantic head for downstream P14:

`1ca2f6e8845ee2d0021346bf05cfaffb6739e8e4`

Trigger:

- PR #24 P15 Module Design preflight
- durable blocker comment `5469349439`
- classification: `MISSING_CONTRACT`
- earliest untrusted layer: `P12 Semantic Schema`

This amendment repairs only the canonical subject and identity model for non-Claim-scoped `ProofObligation` instances, minimally covering the mandatory `REVIEW_DECLARED` CoverageBasis completeness obligation. It does not reopen the accepted Claim / ProofContract object model, assurance model, Profile model, P14 subsystem topology, Gate ownership, lifecycle stage vocabulary, or thin `.aegis` registry boundaries.

Where this amendment is more specific than the earlier P10-P13 documents, this amendment controls for the PR #23 semantic Authority candidate.

---

# 1. Problem statement

The existing semantic package contains two individually reasonable rules that are incompatible when combined:

1. `CoverageBasis.mode == REVIEW_DECLARED` requires obligation materialization to include a mandatory `REVIEW_REQUIRED` coverage-completeness obligation asking CONTROL_REVIEW to confirm that the declared Requirement set faithfully represents the pinned upstream Authority scope.
2. The base `ProofObligation` schema requires every obligation to carry a non-null `claim_id` and `proof_contract_id`.

CoverageBasis completeness is not a Claim-local proposition. It is a trust question over the exact Requirement universe of the containing `VerificationSpec`.

Therefore the schema cannot legitimately attach this obligation to:

- an arbitrary Claim;
- a synthetic Claim;
- a synthetic ProofContract; or
- a silently nullable `claim_id` with no explicit subject semantics.

P15 must not invent those semantics. P12 must define them explicitly.

---

# 2. P12 decision — ProofObligation has a discriminated subject

## 2.1 v0.1 subject kinds

A `ProofObligation` in v0.1 has exactly one canonical `subject` with one of two kinds:

```text
CLAIM
COVERAGE_BASIS
```

These meanings are normative:

- `CLAIM` — the obligation proves or challenges part of one Claim's resolved ProofContract.
- `COVERAGE_BASIS` — the obligation concerns the completeness/integrity of the exact Requirement universe represented by the containing VerificationSpec CoverageBasis.

There is **no generic `SPEC` subject kind in v0.1**.

Reason:

> Model the one required non-Claim subject explicitly instead of creating an unconstrained future extension point whose semantics are not yet needed.

If a future requirement introduces another genuinely spec-level obligation that is not a CoverageBasis question, that requires an explicit compatible schema revision rather than silently overloading `COVERAGE_BASIS`.

## 2.2 No synthetic Claim rule

A non-Claim obligation MUST NOT create or require a synthetic Claim or synthetic ProofContract merely to satisfy a transport shape.

Canonical proof semantics remain:

- product/proposition truth -> Claim / ProofContract;
- verification-scope completeness truth -> CoverageBasis obligation.

This keeps Claim identity reserved for falsifiable product/system propositions rather than workflow bookkeeping.

---

# 3. Consolidated ProofObligation schema

The base `ProofObligation` shape is amended to:

```yaml
id: <deterministic obligation id>
id_scheme: "proof-obligation-v0.1"
verification_spec:
  id: <VerificationSpec id>
  version: <VerificationSpec version>
  digest: <exact VerificationSpec digest>
subject:
  kind: CLAIM | COVERAGE_BASIS

  # required only when kind == CLAIM
  claim_id: <Claim id> | omitted
  proof_contract_id: <ProofContract id> | omitted

  # required only when kind == COVERAGE_BASIS
  coverage_basis_digest: <requirement_set_digest> | omitted

kind: INVARIANT | ORACLE | FIXTURE | PROBE | METRIC | THRESHOLD | EVIDENCE | CHALLENGE | QUALIFICATION | PROVENANCE | COVERAGE_COMPLETENESS
source_key: <stable canonical semantic source key>
evaluation_mode: DETERMINISTIC | REVIEW_REQUIRED
required_evidence_types:
  - <type>
pass_condition: <deterministic rule or review question>
```

The previous top-level mandatory `claim_id` and `proof_contract_id` fields are replaced by the discriminated `subject` as the normative identity contract.

An implementation may expose derived convenience fields such as top-level `claim_id` for Claim-scoped navigation, but those convenience fields are non-normative and MUST NOT be used to invent a Claim association for `COVERAGE_BASIS` obligations.

---

# 4. Subject validation rules

## 4.1 CLAIM subject

For:

```yaml
subject:
  kind: CLAIM
```

all of the following hold:

1. `claim_id` is required.
2. `proof_contract_id` is required.
3. `coverage_basis_digest` is forbidden.
4. `claim_id` MUST resolve to a Claim in the exact `VerificationSpec` revision.
5. `proof_contract_id` MUST resolve to that Claim's current ProofContract in the same exact revision.
6. The obligation's semantic source MUST be derivable from the resolved ProofContract or its QualificationSpec.
7. `COVERAGE_COMPLETENESS` is forbidden as a Claim-scoped obligation kind.

## 4.2 COVERAGE_BASIS subject

For:

```yaml
subject:
  kind: COVERAGE_BASIS
```

all of the following hold:

1. `coverage_basis_digest` is required.
2. `coverage_basis_digest` MUST equal the containing VerificationSpec's exact `coverage_basis.requirement_set_digest`.
3. `claim_id` is forbidden.
4. `proof_contract_id` is forbidden.
5. `kind` MUST be `COVERAGE_COMPLETENESS` in v0.1.
6. `evaluation_mode` MUST be `REVIEW_REQUIRED` in `REVIEW_DECLARED` mode.
7. `source_key` MUST be the canonical key `coverage-completeness` in v0.1.
8. The obligation is part of the complete obligation set and participates in overall readiness, but it does not participate in any Claim's local aggregate status.

## 4.3 EXACT_SET behavior

`CoverageBasis.mode == EXACT_SET` does not require a `COVERAGE_COMPLETENESS` review obligation merely for set equality, because the canonical Requirement set and Claim coverage can be deterministically validated by the Verification Spec Validator.

Architecture or downstream verification may still define separate provenance/integrity obligations if another accepted contract requires them, but v0.1 does not manufacture a `COVERAGE_COMPLETENESS` review obligation for `EXACT_SET` solely for symmetry.

## 4.4 REVIEW_DECLARED behavior

`CoverageBasis.mode == REVIEW_DECLARED` MUST materialize exactly one mandatory v0.1 CoverageBasis completeness obligation for the exact VerificationSpec revision:

```yaml
subject:
  kind: COVERAGE_BASIS
  coverage_basis_digest: <exact requirement_set_digest>
kind: COVERAGE_COMPLETENESS
source_key: coverage-completeness
evaluation_mode: REVIEW_REQUIRED
pass_condition: <review question confirming declared Requirement universe faithfully represents the pinned upstream Authority scope>
```

The obligation remains review-required by design. A deterministic evaluator cannot convert the underlying semantic completeness judgment into `SATISFIED` merely because the artifact is structurally present.

---

# 5. Stable semantic source key

Every obligation has a required `source_key` identifying the exact semantic source within its subject.

The key is not free-form workflow prose. It is a stable canonical locator used for obligation identity and independent completeness comparison.

## 5.1 Claim-scoped keys

For Claim-scoped obligations, `source_key` is derived from the resolved ProofContract semantic element that creates the obligation.

Examples of canonical key classes include:

```text
invariant:<local-invariant-id>
oracle:primary
fixture:<local-fixture-id>
probe:<local-probe-id>
metric:<local-metric-id>
pass-rule:<local-pass-rule-id>
evidence:<local-evidence-requirement-id>
challenge:<stable-challenge-key>
qualification:<stable-qualification-key>
provenance:<stable-provenance-key>
```

P15 may define concrete module representations, but it may not change the semantic rule that the key must be stable for the same exact resolved ProofContract semantics.

## 5.2 CoverageBasis key

The v0.1 CoverageBasis completeness obligation uses exactly:

```text
coverage-completeness
```

No Claim ID is prepended or implied.

---

# 6. ProofObligation identity and replay

## 6.1 Identity tuple

The deterministic obligation ID is derived from the canonical tuple:

```text
id_scheme
+ VerificationSpec.digest
+ subject.kind
+ subject-specific identity
+ obligation.kind
+ source_key
```

where subject-specific identity is:

```text
CLAIM:
  claim_id
  proof_contract_id

COVERAGE_BASIS:
  coverage_basis_digest
```

The exact byte-level canonicalization/hash algorithm is an implementation/module concern for P15/P17, but it MUST be versioned by `id_scheme` and produce the same semantic identity for the same canonical tuple.

## 6.2 Generator version is not an individual obligation subject

`generator.version` remains part of the **obligation-set provenance/identity envelope**, but it is not part of the v0.1 semantic obligation identity tuple above.

Reason:

- an implementation-only generator release should not arbitrarily rename an unchanged semantic obligation;
- an independently implemented completeness checker must be able to compare semantic obligation keys without calling the generator algorithm;
- if a generator version legitimately materializes a changed required obligation set, the set contents and `obligation_set_digest` change and the generator version records why.

This preserves the existing replay contract:

```text
exact VerificationSpec digest
+ exact CoverageBasis digest
+ complete obligation-set identity
+ generator version
```

while keeping each obligation's semantic identity independent from the generator implementation identity.

## 6.3 Identity changes

An obligation identity changes when any identity input changes, including:

- VerificationSpec digest;
- Claim identity;
- current ProofContract identity;
- CoverageBasis requirement-set digest;
- obligation kind;
- semantic source key;
- obligation ID scheme version.

A change to evidence alone does not change obligation identity. It creates a new ProofEvaluation/evidence history against the same obligation when the semantic contract is unchanged.

---

# 7. Obligation-set semantics

The complete obligation set includes obligations of both subject kinds.

The existing obligation-set envelope remains:

```yaml
obligation_set:
  verification_spec_digest: <exact VerificationSpec digest>
  coverage_basis_digest: <exact requirement_set_digest>
  generator:
    name: <generator>
    version: <version>
  obligation_ids:
    - <all Claim and CoverageBasis obligation ids>
  obligation_set_digest: <digest of canonical complete obligation set>
  obligation_count: <integer>
```

Normative rules:

1. `obligation_ids` includes all required `CLAIM` and `COVERAGE_BASIS` obligations.
2. `obligation_count` counts both kinds.
3. Omitting the mandatory `COVERAGE_COMPLETENESS` obligation in `REVIEW_DECLARED` mode makes the materialized set incomplete/invalid.
4. The independent completeness checker may derive the expected CoverageBasis key directly from `CoverageBasis.mode`, `requirement_set_digest`, and this P12 contract; it MUST NOT need a synthetic Claim.
5. Set equality is subject-agnostic: every canonical obligation ID expected for the exact spec must appear exactly once.

---

# 8. ProofEvaluation schema repair

## 8.1 Per-obligation evaluation records

The normative per-obligation evaluation shape becomes:

```yaml
obligations:
  - obligation_id: <id>
    subject:
      kind: CLAIM | COVERAGE_BASIS
      claim_id: <Claim id> | omitted
      proof_contract_id: <ProofContract id> | omitted
      coverage_basis_digest: <digest> | omitted
    status: SATISFIED | EXCEPTION | UNSATISFIED
    evidence_refs: []
    reason_code: <reason>
    detail: null | <compact detail>
```

The subject MUST match the exact materialized `ProofObligation` subject. ProofEvaluation cannot reinterpret an obligation's subject.

A top-level per-record `claim_id` may exist only as a derived convenience for `CLAIM` subjects; it is not required and MUST be absent rather than fabricated for `COVERAGE_BASIS` obligations.

## 8.2 Claim aggregates remain Claim-only

The existing:

```yaml
claims:
  - claim_id: <id>
    status: SATISFIED | EXCEPTION | UNSATISFIED
```

aggregates **only obligations whose `subject.kind == CLAIM` for that Claim**.

A CoverageBasis obligation:

- does not create a synthetic claim aggregate;
- does not worsen an arbitrary Claim's status;
- does not count toward `summary.claims.total` or `summary.critical_claims.total`.

## 8.3 CoverageBasis aggregate

ProofEvaluation adds one optional-but-required-when-present-subject aggregate:

```yaml
coverage_basis:
  status: SATISFIED | EXCEPTION | UNSATISFIED
  obligation_ids:
    - <CoverageBasis-scoped obligation ids>
```

Rules:

1. The field is required when the obligation set contains any `COVERAGE_BASIS` obligation.
2. It is omitted when the obligation set contains no CoverageBasis obligation.
3. Its status is the worst state among its CoverageBasis obligations using existing precedence:

```text
UNSATISFIED > EXCEPTION > SATISFIED
```

4. In the v0.1 `REVIEW_DECLARED` path, the semantic completeness obligation normally remains `EXCEPTION` until CONTROL_REVIEW resolves the trust question with reviewer evidence.
5. ProofEvaluator cannot convert that semantic review question to `SATISFIED` by structural self-assertion.

## 8.4 Overall obligation summary includes all subjects

The existing:

```yaml
summary:
  obligations:
    total: <n>
    satisfied: <n>
    exceptions: <n>
    unsatisfied: <n>
```

counts **all** obligations regardless of subject kind.

Therefore a CoverageBasis `EXCEPTION` or `UNSATISFIED` is visible in the overall proof state even though no Claim aggregate is falsely assigned.

---

# 9. EvidenceArtifact subject compatibility

The existing EvidenceArtifact envelope remains compatible:

```yaml
subjects:
  claim_ids: []
  obligation_ids: []
```

Clarification:

- `claim_ids` MAY be empty.
- `obligation_ids` is sufficient to bind evidence to a `COVERAGE_BASIS` obligation.
- reviewer evidence resolving the CoverageBasis completeness question MUST reference the exact CoverageBasis obligation ID and does not need a synthetic Claim ID.
- evidence subject resolution follows the obligation's canonical `subject` rather than inferring subject kind from whether `claim_ids` is populated.

No new EvidenceArtifact aggregate is introduced by this repair.

---

# 10. VerificationSummary readiness propagation

The existing fail-closed F1 mapping remains controlling.

This repair makes the non-Claim propagation explicit:

1. `VerificationSummary` readiness considers **all obligation statuses**, including `COVERAGE_BASIS` obligations.
2. Any `COVERAGE_BASIS` `UNSATISFIED` prevents `READY`.
3. Any unresolved mandatory `COVERAGE_BASIS` `EXCEPTION` prevents `READY`.
4. No Claim needs to be marked failed merely to propagate the blocker.
5. The primary `BLOCKED_*` status is selected by root cause under the existing F1 mapping, not by subject kind alone.

Typical `REVIEW_DECLARED` transitions are:

```text
mandatory completeness judgment not yet resolved
-> BLOCKED_UNRESOLVED_DECISION

review establishes declared Requirement universe conflicts with pinned Authority
-> BLOCKED_AUTHORITY

review cannot resolve required exact source/evidence identity
-> BLOCKED_EVIDENCE
```

These examples do not create new status values and do not override an earlier/more specific existing blocker.

A mandatory review obligation is never reclassified as advisory merely to obtain `READY`.

---

# 11. P34 behavior

P34 remains the only official Gate owner.

For a `COVERAGE_BASIS` completeness obligation, P34 / CONTROL_REVIEW must:

1. resolve the exact VerificationSpec and CoverageBasis source/digests;
2. inspect the pinned upstream Authority scope;
3. decide whether the declared Requirement universe faithfully represents that scope;
4. produce reviewer/Gate evidence referencing the exact CoverageBasis obligation ID;
5. classify any mismatch at the correct owning layer;
6. issue the existing Gate verdict only after all mandatory review questions are resolved.

Resolution does **not** mutate the historical ProofEvaluation from `EXCEPTION` to a fake deterministic `SATISFIED` result.

The existing rule remains:

> Reviewer resolution evidence and the official Gate decision are downstream evidence/decision artifacts; they are not retroactive mutations of the deterministic ProofEvaluation.

This preserves the independent-review boundary and avoids creating a second Gate inside the Proof Runtime.

---

# 12. P13 compatibility consequence — no new mutation vocabulary

This P12 repair does not require a new canonical mutation operation.

Existing derived operation:

```text
MATERIALIZE_PROOF_OBLIGATIONS
```

continues to materialize the complete obligation set, now using the repaired P12 subject model.

Existing:

```text
EVALUATE_PROOF
```

continues to evaluate exact obligations/evidence, now preserving each obligation's canonical subject.

No operation is added to:

- create a synthetic Claim;
- attach a CoverageBasis obligation to a Claim;
- mutate an obligation subject after materialization; or
- mark a review-required CoverageBasis obligation satisfied without reviewer evidence.

Replay continues to preserve the exact spec, exact obligation set, exact evidence inputs, and exact evaluator/generator versions as already required.

---

# 13. Compatibility with P14 architecture

This repair does not invalidate the P14 architecture topology.

It clarifies inputs for existing P14 subsystems:

- **Verification Spec Validator** validates the discriminated obligation-subject rules when checking derived materialization contracts.
- **Obligation Generator** derives both Claim-scoped obligations and the one required CoverageBasis-scoped completeness obligation in `REVIEW_DECLARED` mode.
- **Proof Evaluator** aggregates Claim subjects separately from CoverageBasis subjects.
- **Verification Summary Projector** propagates all mandatory subject scopes into readiness without inventing synthetic Claims.
- **Independent Obligation Completeness Checker** can derive the required CoverageBasis semantic key directly from CoverageBasis mode/digest and compare it independently with generator output.
- **Review Bundle Adapter** includes CoverageBasis aggregate/obligation navigation for P34.

However, because the semantic input head changes, the existing P14 artifact remains historically valid only against its previously accepted input until architecture ownership explicitly confirms/restacks the stack after fresh P21 acceptance.

P15 MUST remain closed until that governance/resume boundary is satisfied.

---

# 14. Explicitly rejected alternatives

The following are rejected for v0.1:

## 14.1 Arbitrary Claim attachment

Reject because CoverageBasis completeness is not owned by any arbitrary product Claim and would corrupt Claim aggregation semantics.

## 14.2 Synthetic Claim / synthetic ProofContract

Reject because it turns verification bookkeeping into product semantic truth and creates unnecessary identity/lifecycle rules.

## 14.3 Nullable legacy fields without a subject discriminator

Reject because `claim_id: null` does not explain what the obligation is about and would reproduce the original missing contract.

## 14.4 Generic `SPEC` subject in v0.1

Reject for now because no additional generic spec-level obligation semantics are accepted. `COVERAGE_BASIS` is the exact required subject. Future generic spec-level proof requires explicit schema evolution.

## 14.5 Generator-version-dependent obligation IDs

Reject because generator implementation identity belongs in obligation-set provenance and would make independent semantic-key comparison unnecessarily correlated with generator implementation changes.

---

# 15. P12 repaired invariants

1. Every ProofObligation has exactly one explicit canonical subject.
2. v0.1 subject kinds are exactly `CLAIM` and `COVERAGE_BASIS`.
3. A Claim-scoped obligation resolves to one real Claim and its real current ProofContract in the exact VerificationSpec revision.
4. A CoverageBasis-scoped obligation never requires or implies a synthetic Claim/ProofContract.
5. `REVIEW_DECLARED` materializes exactly one mandatory `COVERAGE_COMPLETENESS` review obligation for the exact CoverageBasis.
6. Obligation identity is derived from exact semantic subject + semantic source key under a versioned ID scheme.
7. Generator version is set-level provenance, not the semantic subject of an individual obligation.
8. Claim aggregation includes only Claim-scoped obligations.
9. CoverageBasis obligations have their own ProofEvaluation aggregate and still participate in the overall obligation summary/readiness state.
10. A mandatory spec/coverage-level exception blocks READY without falsely failing a Claim.
11. Reviewer evidence may resolve a review-required obligation for Gate purposes without rewriting historical ProofEvaluation state.
12. P34 Gate authority remains unchanged.

---

# 16. Repair acceptance criteria

Fresh P21 may accept this repair only if governance can answer YES to all of the following:

1. Can the mandatory `REVIEW_DECLARED` coverage-completeness obligation now be represented without inventing a Claim?
2. Is every obligation's canonical subject explicit and unambiguous?
3. Can Claim-scoped obligations still preserve the accepted Claim/ProofContract proof model unchanged?
4. Can obligation IDs remain stable/replayable from exact semantic inputs under a versioned identity scheme?
5. Can an independent checker derive the expected CoverageBasis obligation key without calling the Obligation Generator?
6. Can ProofEvaluation represent a CoverageBasis exception without assigning it to an arbitrary Claim?
7. Do overall obligation counts/readiness still fail closed on CoverageBasis exceptions/failures?
8. Can P34 resolve the CoverageBasis review question with reviewer evidence while preserving ProofEvaluation immutability?
9. Does the repair avoid a generic new workflow aggregate, synthetic Claim, new lifecycle stage, or second Gate?
10. Does the P14 topology remain semantically compatible, subject only to fresh exact-head governance/restack?

---

# 17. Stage disposition

This amendment is the minimal P12 repair requested by the P15 preflight blocker.

```text
P12 repair target:
  ProofObligation subject / identity semantics

New accepted-candidate subject kinds:
  CLAIM
  COVERAGE_BASIS

New required v0.1 obligation kind:
  COVERAGE_COMPLETENESS
```

No other P10-P13 decision is reopened.

After this amendment is materialized to PR #23, the next action is a **fresh P21 Authority Review against the new exact PR #23 head**.

P15 remains blocked until fresh P21 accepts this repaired semantic package and architecture ownership explicitly reconciles PR #24 against the new semantic head.
