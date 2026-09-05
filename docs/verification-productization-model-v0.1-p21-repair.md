# Aegis Verification Productization Model v0.1 — P21 Repair Amendment

Status: **Draft / Proposed Authority — P10-P13 normative repair**

Scope: `aegis/verification-productization`

Base model: `docs/verification-productization-model-v0.1.md`

Reviewed base head: `19c62cbb8a7349aa9818729f4c1b03cb233c0553`

Purpose: repair only the four semantic gaps identified by the P21 Authority Review on PR #23. This amendment does not reopen accepted P02/P03 product decisions, does not redesign the P10-P13 object model, does not modify the current `aegis-verification` Skill, does not create a new lifecycle stage, and does not change P34 Gate ownership.

For the PR #23 authority candidate, this amendment is normative together with the base model. Where one of the four repaired contracts below is more specific than the base model, this amendment controls. All unaffected base-model semantics remain unchanged.

---

# 1. Repair B1 — Exact Requirement coverage basis

## 1.1 Problem repaired

The base model correctly requires every in-scope Requirement to be covered by at least one Claim, but generic `authority_refs` plus per-Claim `requirement_refs` do not identify the complete set of Requirements that belongs to the verification scope. Without an exact coverage basis, a verifier cannot distinguish complete coverage from an omitted Requirement.

P14 must not invent the verification scope. Therefore completeness becomes explicit P10/P12 truth.

## 1.2 `CoverageBasis` is a value object, not a new aggregate

`CoverageBasis` is embedded in `VerificationSpec`.

It identifies the exact upstream Requirement universe against which Claim coverage is judged.

It is not independently mutable and has no lifecycle separate from the containing VerificationSpec revision.

Semantic shape:

```yaml
coverage_basis:
  authority_ref: <exact upstream authority identifier/ref>
  authority_version: null | <semantic version/revision>
  authority_digest: <digest of the exact upstream authority snapshot>
  source_ref: <reviewer-resolvable immutable or version-pinned source ref>
  mode: EXACT_SET | REVIEW_DECLARED
  requirements:
    - id: <stable requirement identity>
      ref: null | <addressable requirement ref>
  requirement_set_digest: <digest of canonical ordered requirement identities>
```

Required semantics:

1. `authority_ref`, `authority_digest`, `source_ref`, `mode`, `requirements`, and `requirement_set_digest` are required.
2. Requirement IDs are unique and stable within the pinned upstream Authority snapshot.
3. `requirements` is the complete in-scope Requirement set for this VerificationSpec revision, not merely the Requirements that happened to receive Claims.
4. `requirement_set_digest` is derived from the canonical complete set and therefore changes when the in-scope Requirement universe changes.
5. Every Claim `requirement_ref` MUST resolve to one or more Requirement IDs in `coverage_basis.requirements`.
6. Every Requirement ID in `coverage_basis.requirements` MUST be covered by at least one committed Claim.
7. Extra Claim references to Requirements outside the exact basis fail validation rather than silently widening scope.
8. A change to the upstream Requirement universe requires a new VerificationSpec revision; it cannot silently reuse the old coverage result.

## 1.3 Coverage modes

### `EXACT_SET`

Use when the upstream Authority exposes machine-addressable stable Requirement identities.

Commit requires deterministic set coverage:

```text
set(coverage_basis.requirement_ids)
==
union(all Claim.requirement_refs)
```

The equality is about required coverage, not one-to-one mapping: one Requirement may map to multiple Claims and one Claim may cover multiple Requirements when semantically justified.

### `REVIEW_DECLARED`

Use only when the upstream Authority cannot expose a mechanically enumerable Requirement set without inventing false structure.

The exact Authority snapshot is still pinned by `authority_digest` and `source_ref`, and the declared Requirement identities still form the canonical coverage basis. In this mode obligation materialization MUST include a mandatory `REVIEW_REQUIRED` coverage-completeness obligation asking CONTROL_REVIEW to confirm that the declared Requirement set faithfully represents the pinned Authority scope.

`REVIEW_DECLARED` is not permission to omit the Requirement universe. It moves only the completeness judgment from deterministic evaluation to explicit review.

## 1.4 P10 invariant repair

Replace the informal coverage invariant with:

> Every committed VerificationSpec contains one exact CoverageBasis for its scope. Every Requirement identity in that basis is covered by at least one Claim, every Claim Requirement reference resolves inside that basis, and coverage completeness is either deterministically established (`EXACT_SET`) or represented by a mandatory review obligation (`REVIEW_DECLARED`).

## 1.5 P11 authoring/commit repair

Authoring start MUST pin the exact CoverageBasis before Claim coverage can be accepted.

A VerificationSpec revision cannot commit when:

- the complete Requirement universe is unknown;
- the upstream Authority snapshot cannot be pinned;
- any Claim references an out-of-basis Requirement;
- any in-basis Requirement is uncovered; or
- `REVIEW_DECLARED` mode is used but the mandatory coverage-completeness review obligation cannot be generated.

A material upstream Requirement change invalidates the transient authoring computation and requires rebase/restart against the new CoverageBasis.

---

# 2. Repair B2 — Independent P34 completeness and conformance invariant

## 2.1 Problem repaired

Exception-based review may compress repeated inspection of machine-satisfied proof facts, but it must not let a flawed or under-complete obligation generator define its own completeness.

A ProofEvaluation with zero `UNSATISFIED` and zero `EXCEPTION` is insufficient by itself: a missing Claim or missing obligation could otherwise disappear from the evaluation and produce a falsely clean summary.

## 2.2 Exact obligation-set identity

The derived obligation set MUST have exact identity.

ProofEvaluation therefore binds an `obligation_set` envelope:

```yaml
obligation_set:
  verification_spec_digest: <exact VerificationSpec digest>
  coverage_basis_digest: <exact requirement_set_digest>
  generator:
    name: <generator>
    version: <version>
  obligation_ids:
    - <canonical obligation id>
  obligation_set_digest: <digest of canonical complete obligation set>
  obligation_count: <integer>
```

Rules:

1. `obligation_ids` represents the complete obligation set for the exact VerificationSpec, not only executed or successful obligations.
2. The generator version is part of identity.
3. `obligation_set_digest` changes if any required obligation is added, removed, or semantically changed.
4. ProofEvaluation MUST evaluate the exact bound set; an obligation absent from the set cannot be silently treated as SATISFIED.
5. Evaluation output MUST preserve set identity even if per-obligation detail is compacted.

## 2.3 P34 independent completeness invariant

P34 remains the formal independent Gate owner.

P34 MAY avoid re-deriving every deterministic fact already credibly established by ProofEvaluation only after independently establishing all of the following:

1. **Spec identity** — the VerificationSpec ID/version/digest is the intended Current verification design basis for the reviewed result.
2. **Coverage-basis integrity** — the exact Requirement universe used by the spec matches the pinned upstream Authority scope, including mandatory review of `REVIEW_DECLARED` completeness when applicable.
3. **Obligation-set completeness** — the evaluated obligation-set identity is complete for the exact VerificationSpec and generator contract; the reviewer must not rely solely on the evaluator's own assertion that its set is complete.
4. **Evaluation-set equality** — the ProofEvaluation covers exactly the complete bound obligation set; missing or extra evaluated obligation identities fail closed.
5. **Exact-result Authority/scope conformance** — the independently resolved implementation `materialized_ref` is the exact result authorized by the reviewed Authority/task scope and does not contain unexplained scope drift.
6. **Evidence provenance/integrity** — evidence inputs are exact, reviewer-resolvable, and immutably pinned as defined in Repair B3.
7. **Outcome condition** — there are no `UNSATISFIED` obligations and no unresolved mandatory `EXCEPTION` obligations.

The independent completeness check may be implemented by deterministic tooling, regeneration, a qualified generator, or another credible independent mechanism. Architecture may choose the mechanism, but it MUST preserve this semantic invariant.

A single component MUST NOT be allowed to both omit an obligation and self-certify that the resulting obligation set is complete without an independently credible completeness check.

## 2.4 P34 normal-path repair

The compact normal path is therefore:

```text
resolve exact materialized_ref independently
-> confirm exact Current Authority / VerificationSpec identity
-> establish CoverageBasis integrity
-> establish complete obligation-set identity independently
-> validate ProofEvaluation input identity/provenance
-> confirm exact-result Authority/scope conformance
-> require UNSATISFIED = 0
-> resolve all mandatory EXCEPTIONs
-> issue existing official P34 Gate verdict
```

This preserves exception-centric review without weakening current P34 responsibilities for Authority conformance, semantic/scope conformance, and downstream safety.

---

# 3. Repair B3 — Immutable identity for every ProofEvaluation evidence input

## 3.1 Problem repaired

The base model says ProofEvaluation is computed from an exact evidence set, but a human-readable or mutable `evidence_ref` alone does not prove exact input identity. The referenced content could change after evaluation and break replay or independent review.

## 3.2 `EvidenceInputRef`

Every EvidenceArtifact consumed by ProofEvaluation MUST be represented by an exact input binding:

```yaml
evidence_inputs:
  - evidence_id: <EvidenceArtifact id>
    ref: <reviewer-resolvable durable ref>
    digest: <content digest of the exact EvidenceArtifact envelope or exact immutable artifact>
    producer_class: DETERMINISTIC_COLLECTOR | EXECUTOR | REVIEWER | EXTERNAL
```

Required semantics:

1. `evidence_id`, `ref`, `digest`, and `producer_class` are required for every evaluation input.
2. `ref` MUST be reviewer-resolvable at the review boundary.
3. `digest` MUST pin the exact content used by the evaluator. A mutable ref without a matching immutable digest is not an exact evaluation input.
4. If the evidence provider has a natively immutable content-addressed/versioned ref, its immutable identity may be used as the digest-equivalent only when the identity semantics are explicit and replay-safe; the materialized ProofEvaluation still records the resolved immutable identity.
5. If exact identity cannot be established, an obligation that depends on that evidence cannot become `SATISFIED`; use `UNSATISFIED` for required missing/invalid provenance or `EXCEPTION` only when the contract explicitly requires review rather than deterministic identity.
6. Re-evaluating against changed evidence creates a new ProofEvaluation with new evidence input identities. Historical evaluations remain pinned to their old inputs.

## 3.3 ProofEvaluation schema repair

Replace ambiguous bare `evidence_refs` as the normative evaluation-input contract with `evidence_inputs`.

A compatibility-oriented implementation may additionally expose convenience `evidence_refs`, but they are derived navigation fields and MUST NOT be the sole identity used for evaluation or replay.

ProofEvaluation exact identity now consists at minimum of:

```text
VerificationSpec digest
+ CoverageBasis requirement_set_digest
+ obligation_set_digest + generator version
+ ordered/canonical EvidenceInputRef identities
+ evaluator version
```

## 3.4 Evidence registry compatibility

This repair does not expand `.aegis/evidence.json` into a proof database.

The existing thin evidence registry may continue to store `id/type/ref/status/subject_ids`. The exact EvidenceInputRef/digest belongs in the detailed EvidenceArtifact / ProofEvaluation artifact referenced by that registry.

---

# 4. Repair F1 — Fail-closed user-facing VerificationSummary status mapping

## 4.1 Problem repaired

`Verification: READY` is a compact readiness view, not a Gate verdict. It must never hide an unresolved mandatory exception or a failed/missing proof obligation.

The summary reuses existing Aegis workflow statuses. It does not create a second public status taxonomy.

## 4.2 Status derivation

A `VerificationSummary` MUST NOT render `READY` unless all readiness preconditions below hold:

1. CoverageBasis is valid for the exact upstream Authority snapshot.
2. The complete obligation set is materialized and its identity is available.
3. Every required evidence input used for deterministic satisfaction has exact immutable identity.
4. `UNSATISFIED == 0`.
5. unresolved mandatory `EXCEPTION == 0`.
6. no unresolved Authority/scope/criticality/assurance decision blocks verification readiness.

When all conditions hold:

```text
status: READY
```

When only non-mandatory/advisory findings remain and downstream policy explicitly permits them:

```text
status: READY_WITH_FINDINGS
```

A mandatory exception is never downgraded to an advisory finding merely to produce READY.

## 4.3 Fail-closed blocker mapping

Use the smallest applicable existing Aegis status based on the owning reason:

| Condition | Summary status |
|---|---|
| upstream Authority / Requirement scope mismatch, stale CoverageBasis, semantic authority conflict | `BLOCKED_AUTHORITY` |
| required evidence missing, invalid, inaccessible, mutable/unpinned, incomplete obligation/evaluation evidence | `BLOCKED_EVIDENCE` |
| deterministic proof establishes that the authorized implementation behavior fails | `BLOCKED_IMPLEMENTATION` |
| required execution/probe environment cannot provide credible evidence | `BLOCKED_ENVIRONMENT` |
| required input to author/evaluate the spec is absent | `BLOCKED_MISSING_INPUT` |
| criticality, risk acceptance, assurance downgrade, or another mandatory semantic decision is unresolved | `BLOCKED_UNRESOLVED_DECISION` |

If more than one blocker exists, expose the earliest/owning blocker as primary and preserve the remaining blocker reasons as findings. Do not collapse a semantic Authority defect into `BLOCKED_IMPLEMENTATION` merely because code also fails.

## 4.4 Relationship to P34 Gate status

`VerificationSummary.status` is workflow/readiness state only.

It MUST NOT emit or imply an official Gate `PASS`, `PASS_WITH_FINDINGS`, or Gate `BLOCKED_*` decision. P34 remains the sole formal Gate review surface for the implementation occurrence.

A summary may say `READY` before P34 only to mean that verification evidence is ready for formal independent Gate review.

---

# 5. P12 consolidated schema deltas

The base `VerificationSpec` shape is amended to:

```yaml
schema_version: "0.1"
id: <stable verification-scope id>
scope: <semantic scope>
version: <immutable revision/version>
authority_refs:
  - <upstream authority ref>
coverage_basis:
  authority_ref: <exact upstream authority identifier/ref>
  authority_version: null | <version/revision>
  authority_digest: <digest>
  source_ref: <reviewer-resolvable immutable/version-pinned ref>
  mode: EXACT_SET | REVIEW_DECLARED
  requirements:
    - id: <stable requirement id>
      ref: null | <addressable requirement ref>
  requirement_set_digest: <digest>
claims:
  - <Claim>
proof_contracts:
  - <ProofContract>
extensions: {}
```

Additional validation:

- the CoverageBasis complete set is required;
- Claim requirement references must be a subset of the basis;
- all basis Requirement identities require Claim coverage;
- exact-set equality is deterministically checked in `EXACT_SET` mode;
- `REVIEW_DECLARED` produces a mandatory review obligation;
- coverage basis changes require a new VerificationSpec revision.

The base `ProofEvaluation` shape is amended to include:

```yaml
verification_spec:
  id: <spec id>
  version: <spec version>
  digest: <exact digest>
coverage_basis_digest: <exact requirement_set_digest>
obligation_set:
  verification_spec_digest: <exact spec digest>
  coverage_basis_digest: <exact requirement_set_digest>
  generator:
    name: <generator>
    version: <version>
  obligation_ids: []
  obligation_set_digest: <digest>
  obligation_count: <integer>
evaluator:
  name: <evaluator>
  version: <version>
evidence_inputs:
  - evidence_id: <id>
    ref: <durable reviewer-resolvable ref>
    digest: <exact content digest or explicit immutable identity>
    producer_class: DETERMINISTIC_COLLECTOR | EXECUTOR | REVIEWER | EXTERNAL
obligations:
  - <existing obligation evaluation record>
claims:
  - <existing claim evaluation record>
summary:
  - <existing aggregate counts>
created_at: <timestamp>
```

The normative prohibition remains unchanged: ProofEvaluation cannot contain or imply the official P34 Gate verdict.

---

# 6. P13 operation/replay deltas

## 6.1 `CREATE_VERIFICATION_SPEC` / `REVISE_VERIFICATION_SPEC`

Both operations MUST validate exact CoverageBasis semantics before canonical commit.

A changed upstream Requirement set or digest requires a new spec revision and re-evaluation of downstream coverage/proof. It cannot silently inherit prior completeness.

## 6.2 `MATERIALIZE_PROOF_OBLIGATIONS`

Output identity now includes the complete canonical obligation set plus `obligation_set_digest` and `coverage_basis_digest`.

Same exact:

```text
VerificationSpec digest
+ CoverageBasis digest
+ generator version
```

must produce a semantically identical complete obligation set.

Missing coverage-completeness review obligation in `REVIEW_DECLARED` mode is an invalid materialization.

## 6.3 `REGISTER_EVIDENCE_ARTIFACT`

Registration remains append-only.

An artifact may be indexed before an exact evaluation digest exists, but it cannot satisfy an exact ProofEvaluation input until a reviewer-resolvable immutable identity/digest is available.

## 6.4 `EVALUATE_PROOF`

Inputs are now:

```text
exact VerificationSpec digest
+ exact CoverageBasis digest
+ exact complete obligation-set identity/generator version
+ exact EvidenceInputRef set
+ exact evaluator version
```

Output remains an immutable ProofEvaluation.

If complete obligation-set identity or exact evidence-input identity is unavailable, evaluation fails closed rather than emitting a falsely clean SATISFIED result.

## 6.5 Replay

Replayability additionally requires preserving:

- CoverageBasis `requirement_set_digest`;
- complete `obligation_set_digest` + generator version;
- each ProofEvaluation `EvidenceInputRef.digest` or explicit immutable identity.

This closes the gap between human-readable references and exact historical proof inputs.

---

# 7. Repair acceptance criteria

The P21 repair is complete only when governance can answer YES to all of the following:

1. Can the complete in-scope Requirement universe be identified exactly for every committed VerificationSpec?
2. Can universal Claim coverage be deterministically checked when possible and explicitly reviewed when exact machine enumeration is not possible?
3. Can P34 detect an omitted Claim/obligation rather than trusting a ProofEvaluator's self-reported clean set?
4. Does P34 retain independent Authority/scope conformance responsibility while still avoiding redundant re-derivation of credible deterministic facts?
5. Is every evidence item consumed by ProofEvaluation pinned to immutable/replay-safe identity?
6. Can a changed evidence artifact never silently rewrite the historical meaning of an existing ProofEvaluation?
7. Can a mandatory EXCEPTION or any UNSATISFIED obligation never render `Verification: READY`?
8. Does the user-facing readiness status reuse existing Aegis `READY / READY_WITH_FINDINGS / BLOCKED_*` vocabulary without becoming a second Gate?
9. Are the original productization principles still preserved: rigorous inside, simple outside, risk-proportional assurance, one-hop qualification, deterministic collection, exception-centric review, and no new lifecycle stage?

---

# 8. Stage repair disposition

With this amendment, the intended P10-P13 model remains the base PR #23 model with only these four normative repairs:

```text
B1  exact CoverageBasis
B2  independent P34 obligation-completeness + scope-conformance invariant
B3  immutable ProofEvaluation evidence-input identity
F1  fail-closed VerificationSummary status mapping
```

No other P10-P13 decision is reopened by this repair.

After this exact-head repair is materialized, the next action is a fresh P21 Authority Review against the new PR #23 head. P14 must remain closed until that governance review accepts the repaired authority candidate.