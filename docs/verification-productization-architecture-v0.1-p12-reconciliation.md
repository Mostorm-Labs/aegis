# Aegis Verification Productization Architecture v0.1 — P12 Reconciliation Amendment

Status: **Draft / Proposed Authority — P14 reconciliation**

Scope: `aegis/verification-productization/architecture`

Base architecture artifact:

- `docs/verification-productization-architecture-v0.1.md`
- original architecture head: `017d1583329bc579627d0650d55c0e47a9f3cefb`

Reconciled upstream semantic basis:

- PR #23 exact semantic head: `2eb7d507098d24328b883dfa1366521390026fce`
- P21 Authority Review #3: `PASS`
- durable P21 review: `5061120240`
- `docs/verification-productization-model-v0.1.md`
- `docs/verification-productization-model-v0.1-p21-repair.md`
- `docs/verification-productization-model-v0.1-p15-preflight-p12-repair.md`

Trigger:

- P15 preflight blocker on PR #24: `5469349439`
- classification: `MISSING_CONTRACT`
- repaired owner/layer: P12 Semantic Schema
- repair accepted by P21 #3

This amendment reconciles the existing P14 architecture with the accepted P12 `ProofObligation.subject` model. It is normative together with `docs/verification-productization-architecture-v0.1.md`. Where this amendment is more specific about the upstream semantic head or subject-aware interfaces, this amendment controls. All unaffected P14 topology, ownership, failure-domain, lifecycle, and trust-boundary decisions remain unchanged.

---

# 1. Reconciliation verdict

**P14 topology: UNCHANGED**

**P14 dependency/interface contract: AMENDED**

**P14 disposition after restack: READY**

The accepted P12 repair does not require a new subsystem, process, lifecycle stage, Gate, storage authority, or execution plane.

The existing architecture already separates:

1. Verification authoring / semantic control;
2. deterministic obligation generation and evaluation;
3. execution/evidence materialization;
4. independent completeness review and P34 Gate authority.

The new semantic distinction:

```text
ProofObligation.subject.kind
  CLAIM
  COVERAGE_BASIS
```

fits those existing responsibilities directly.

Architecture MUST NOT introduce synthetic Claims or synthetic ProofContracts to preserve old transport assumptions.

---

# 2. Updated architecture basis

The base architecture document was authored against semantic head:

`1ca2f6e8845ee2d0021346bf05cfaffb6739e8e4`

That exact dependency is superseded for the current stacked architecture candidate by:

`2eb7d507098d24328b883dfa1366521390026fce`

The current P14 architecture package therefore consists of:

```text
docs/verification-productization-architecture-v0.1.md
+ docs/verification-productization-architecture-v0.1-p12-reconciliation.md
```

against the three-file semantic package accepted by P21 #3.

The old P14 commit remains historical evidence of the original architecture reasoning; the restacked descendant architecture head is the only candidate that downstream P15 may consume.

---

# 3. Subject-aware architectural invariant

Every subsystem that transports, evaluates, summarizes, or reviews a ProofObligation MUST preserve the obligation's canonical subject discriminator.

It must never infer subject meaning solely from the presence or absence of a `claim_id` convenience field.

Normative transport rule:

```text
ProofObligation
  -> subject.kind
  -> subject-specific identity
  -> obligation.kind
  -> source_key
```

must remain recoverable across materialization, task projection where applicable, evidence binding, evaluation, summary projection, completeness checking, and review navigation.

---

# 4. Verification Spec Validator reconciliation

The existing Verification Spec Validator subsystem remains the owner of deterministic structural validation.

Additional subject-aware responsibilities:

- recognize v0.1 subject kinds exactly `CLAIM | COVERAGE_BASIS`;
- reject unknown required subject kinds fail-closed;
- reject `COVERAGE_COMPLETENESS` as a Claim-scoped obligation kind;
- require the exact `coverage_basis_digest` on CoverageBasis-scoped obligations;
- reject Claim / ProofContract association on a CoverageBasis-scoped obligation;
- preserve the existing rule that `REVIEW_DECLARED` requires exactly one mandatory coverage-completeness review obligation in the complete materialized set.

The validator does not decide whether the declared Requirement universe is semantically complete; CONTROL_REVIEW owns that judgment.

---

# 5. Obligation Generator reconciliation

The existing Obligation Generator subsystem remains unchanged in ownership and process placement.

It now materializes two semantic subject classes:

## 5.1 Claim-scoped obligations

Generated from the exact resolved Claim / ProofContract semantics.

Subject identity:

```text
CLAIM
+ claim_id
+ proof_contract_id
```

## 5.2 CoverageBasis-scoped obligation

For `CoverageBasis.mode == REVIEW_DECLARED`, materialize exactly one:

```text
subject.kind = COVERAGE_BASIS
subject.coverage_basis_digest = exact requirement_set_digest
kind = COVERAGE_COMPLETENESS
source_key = coverage-completeness
evaluation_mode = REVIEW_REQUIRED
```

It is part of the complete obligation set but is not an executable code-test task merely because it is an obligation.

## 5.3 Identity boundary

The Generator must use the accepted semantic identity tuple under `proof-obligation-v0.1`.

Generator implementation version remains obligation-set provenance and does not redefine unchanged individual semantic obligation IDs.

The Generator still cannot certify its own set completeness.

---

# 6. P31 Task Projection reconciliation

The existing P31 Task Projection Adapter remains a transport adapter, not a semantics owner.

It MUST distinguish obligations by `evaluation_mode` and execution applicability.

Architecture rule:

> A `REVIEW_REQUIRED` CoverageBasis completeness obligation is routed into review navigation / review-bundle inputs, not converted into an implementation task for P32.

Claim-scoped executable obligations may be projected into P31/P32 task packages as before.

The adapter may carry a CoverageBasis obligation reference for traceability, but it must not fabricate executable commands, Claim IDs, or ProofContract IDs for that obligation.

---

# 7. Evidence Collector / Materializer reconciliation

No new evidence subsystem is required.

Evidence binding remains obligation-ID based and may additionally include Claim IDs when the obligation is Claim-scoped.

For CoverageBasis reviewer evidence:

- `obligation_ids` binds the exact CoverageBasis obligation;
- `claim_ids` may be empty;
- materialization must still produce exact reviewer-resolvable immutable identity;
- absence of a Claim is not an evidence error when the canonical subject is CoverageBasis.

Executor-produced evidence cannot self-resolve the semantic completeness judgment merely because it references the obligation.

---

# 8. Proof Evaluator reconciliation

The existing Proof Evaluator remains deterministic and non-Gate.

It must preserve the exact canonical subject on every obligation evaluation record.

Aggregation becomes explicitly subject-aware:

```text
CLAIM obligations
  -> claims[] aggregates

COVERAGE_BASIS obligations
  -> coverage_basis aggregate

ALL obligations
  -> summary.obligations
```

For the `REVIEW_DECLARED` coverage-completeness obligation, the deterministic evaluator normally emits/retains `EXCEPTION` because the underlying trust question belongs to CONTROL_REVIEW.

It must not infer `SATISFIED` from:

- the obligation existing structurally;
- the declared Requirement list being non-empty;
- Generator self-assertion;
- executor prose.

Historical ProofEvaluation remains immutable after reviewer resolution.

---

# 9. Verification Summary Projector reconciliation

The Summary Projector remains a user-view projection only.

Readiness considers overall mandatory obligation state, not only Claim aggregates.

Therefore:

- CoverageBasis `UNSATISFIED` blocks `READY`;
- unresolved mandatory CoverageBasis `EXCEPTION` blocks `READY`;
- no arbitrary Claim must be marked failed to propagate the blocker;
- existing F1 root-cause `BLOCKED_*` mapping remains controlling.

The compact default UI remains compatible:

```text
Status
Critical Claims
Exceptions
```

A CoverageBasis exception appears as an exception/readiness blocker without being misrepresented as a product Claim failure.

---

# 10. Independent Obligation Completeness Checker reconciliation

The existing Independent Obligation Completeness Checker remains mandatory and independent from Generator output.

For CoverageBasis completeness, it derives the expected semantic obligation directly from accepted semantic truth:

```text
CoverageBasis.mode == REVIEW_DECLARED
+ exact requirement_set_digest
+ subject.kind = COVERAGE_BASIS
+ kind = COVERAGE_COMPLETENESS
+ source_key = coverage-completeness
+ id_scheme = proof-obligation-v0.1
```

It then compares the expected semantic obligation identity with the generated obligation set.

Allowed shared dependencies remain limited to semantic infrastructure such as:

- canonical schema/parser definitions;
- canonical enum definitions;
- canonical byte encoding / digest utility;
- accepted proof-obligation ID-scheme implementation.

Forbidden correlated dependency remains:

- calling ObligationGenerator's traversal/materialization algorithm to derive the expected set;
- consuming Generator output as the source of expected truth.

This amendment clarifies an important independence rule for P15:

> Shared canonical identity primitives are allowed; shared obligation-derivation logic is not sufficient for independent completeness proof.

---

# 11. Review Bundle Adapter reconciliation

The review bundle must make subject-aware navigation explicit.

For the CoverageBasis path it carries at minimum:

```text
VerificationSpec ref/digest
CoverageBasis exact source/digest/mode
CoverageBasis ProofObligation id/subject/kind/source_key
obligation-set ref/digest/generator version
ProofEvaluation ref/digest/evaluator version
coverage_basis aggregate
reviewer evidence refs
Completeness Checker result/version
mandatory exception state
```

It MUST NOT manufacture a Claim link for this path.

The bundle is still navigation, not Gate authority.

---

# 12. P34 reconciliation

P34 remains outside the Proof Runtime and remains the only official Gate owner.

For `REVIEW_DECLARED`, P34 must independently resolve:

1. exact VerificationSpec;
2. exact CoverageBasis source and digest;
3. declared Requirement universe against pinned Authority scope;
4. existence/completeness of the required CoverageBasis obligation;
5. review evidence bound to that exact obligation;
6. all other existing exact-result / scope / evidence / obligation-set conditions.

Reviewer resolution may support the Gate decision but does not rewrite the historical ProofEvaluation's deterministic `EXCEPTION` into a synthetic SATISFIED result.

---

# 13. Dependency topology check

No dependency arrow from the original P14 topology is removed or reversed.

The reconciled flow remains:

```text
Upstream Authority
      ↓
Verification Authoring Controller
      ↓
Profile Resolver / Spec Validator
      ↓
VerificationSpec Materializer
      ↓
Obligation Generator
      ↓
P31 Task Projection Adapter      [executable subset only]
      ↓
P32/P36 execution environments
      ↓
Evidence Collector / Materializer
      ↓
Proof Evaluator
      ↓
Verification Summary Projector
      ↓
Review Bundle Adapter
      ↓
Independent Completeness Checker + P34
```

And the mandatory independent review-side path remains:

```text
VerificationSpec / CoverageBasis --------------------┐
                                                     v
                                         Completeness Checker
Generated obligation set ---------------------------> compare
```

The CoverageBasis review obligation also routes directly into review-bundle/P34 handling rather than requiring P32 execution.

---

# 14. Failure-domain reconciliation

The P12 repair does not create a new failure domain.

Failures map to existing domains:

- invalid subject discriminator / illegal subject fields -> schema/spec validation failure;
- missing CoverageBasis completeness obligation -> obligation-set completeness failure;
- fabricated Claim association -> semantic/schema conformance failure;
- missing reviewer-resolvable evidence -> evidence failure;
- unresolved CoverageBasis completeness judgment -> existing unresolved-decision / review blocker;
- mismatch with pinned Authority scope -> Authority blocker;
- correlated checker using Generator derivation logic as oracle -> review completeness failure.

No new `BLOCKED_*` status is introduced.

---

# 15. Explicitly unchanged P14 decisions

The following remain unchanged:

1. four logical planes plus durable artifact boundary;
2. P20 semantic authoring ownership;
3. stateless/pure deterministic proof runtime preference;
4. P31/P32 implementation ownership boundaries;
5. exact reviewer-resolvable EvidenceArtifact / EvidenceInputRef requirement;
6. ProofEvaluation is not a Gate;
7. independent Completeness Checker is review-side;
8. P34 is the sole official Gate owner;
9. thin `.aegis` registries remain thin;
10. no new lifecycle stage;
11. `Task Anchor != Execution Cursor` remains unrelated navigation/execution state;
12. automation does not collapse stage ownership.

---

# 16. P15 constraints produced by reconciliation

P15 may now freeze concrete module interfaces without inventing missing semantic truth.

It MUST preserve these architectural constraints:

1. shared proof-model core may own parser/enums/canonicalization/digest/ID-scheme primitives;
2. Obligation Generator owns generation traversal/materialization rules;
3. Completeness Checker owns an independently implemented expected-obligation traversal;
4. Generator and Checker may share canonical identity primitives but not the same generation traversal as the completeness oracle;
5. subject-aware data structures preserve `CLAIM | COVERAGE_BASIS` explicitly;
6. P31 projection partitions executable versus review-required obligations without changing obligation semantics;
7. Proof Evaluator aggregates Claim and CoverageBasis subjects separately while overall readiness includes both;
8. Review Bundle exposes CoverageBasis review navigation without synthetic Claim mapping.

---

# 17. P14 reconciliation exit criteria

P14 reconciliation is complete when all answers are YES:

1. Is the architecture pinned to semantic head `2eb7d507098d24328b883dfa1366521390026fce`? **YES.**
2. Does the P12 repair require a new subsystem? **NO.**
3. Does it require a new execution plane or lifecycle stage? **NO.**
4. Can Obligation Generator represent both accepted subject kinds? **YES.**
5. Can P31 avoid converting review-only CoverageBasis obligations into code tasks? **YES.**
6. Can EvidenceArtifact bind CoverageBasis evidence without synthetic Claim IDs? **YES.**
7. Can ProofEvaluator preserve separate Claim/CoverageBasis aggregation? **YES.**
8. Can Summary fail closed on CoverageBasis exceptions/failures? **YES.**
9. Can the Completeness Checker derive expected CoverageBasis identity independently? **YES.**
10. Does P34 remain the only official Gate owner? **YES.**

---

# 18. Stage disposition

**P14 System Architecture: READY — RECONCILED**

The semantic dependency change is architecture-compatible and requires no topology redesign.

After this amendment is restacked onto semantic head `2eb7d507098d24328b883dfa1366521390026fce`, the next earliest untrusted layer becomes:

**P15 Module Design**

P15 should resume from this exact descendant architecture head and freeze concrete module boundaries/interfaces, especially the shared canonical identity core versus independently implemented Generator/Completeness traversal boundary.