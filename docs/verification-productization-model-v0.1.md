# Aegis Verification Productization Model v0.1

Status: **Draft / Proposed Authority — P10-P13**

Scope: `aegis/verification-productization`

Upstream basis: accepted `Aegis Verification Productization Convergence v0.1` product requirements and capability traceability from the 2026-08-30 control-plane convergence session.

This document intentionally does **not** modify the current `aegis-verification` Skill, the Aegis lifecycle stage vocabulary, Gate authority, or `.aegis` Project State semantics. It defines the smallest semantic model needed to make Verification rigorous internally while substantially compressing the user-facing workflow.

Core product rule:

> **Users manage exceptions; Aegis manages proof machinery.**

Supporting rules:

> **Preserve proof depth, compress workflow surface.**
>
> **Rigorous inside. Simple outside.**
>
> **Increase trust depth without increasing workflow depth.**

---

## 1. Upstream product constraints treated as accepted input

The following are not reopened by this modeling pass:

1. The existing P20 proof chain remains semantically valid:
   `Requirement -> Invariant -> Oracle/Reference -> Fixture/Corpus -> Test/Probe -> Metric -> Threshold -> Evidence Artifact -> Gate`.
2. Every in-scope Requirement requires verification coverage.
3. Only Critical Claims require an explicit Proof Contract by default; ordinary claims may use a generated contract.
4. Verification strength is risk-proportional and internally represented as `STANDARD`, `CHALLENGED`, or `QUALIFIED` assurance.
5. Base Proof Profiles are `EXAMPLE`, `PROPERTY`, `REFERENCE`, `MEASURE`, `OBSERVATION`, plus the `CUSTOM` escape hatch.
6. Challenge modifiers are orthogonal to base profile selection.
7. Verifier qualification is one-hop only.
8. Evidence metadata that can be generated deterministically should not be manually transported by an executor or reviewer.
9. Machine computation produces Proof Evaluation, not an independent formal Gate.
10. P34 remains the formal independent Gate review surface.
11. No new lifecycle P-stage is introduced.
12. The first productized version should prefer compatibility with the existing thin `.aegis/evidence.json` and `.aegis/gates.json` registries rather than expanding Project State prematurely.

---

# 2. P10 — Product Object Model

## 2.1 Modeling rule

Do not make every useful noun a first-class entity.

A productization model that turns `Claim`, `Critical Claim`, `Assurance`, `Profile`, `Challenge`, `Qualification`, `Obligation`, `Evidence`, `Evaluation`, and `Exception` into separately mutable entities would recreate the workflow complexity this project is trying to remove.

The canonical model therefore uses **three durable semantic objects**, a small set of value objects, and derived/external artifacts.

---

## 2.2 Durable semantic objects

### 2.2.1 `VerificationSpec` — aggregate root

A versioned verification specification for one verification scope.

It is the durable P20 authority candidate that binds:

- upstream Authority / Requirement references;
- Claims;
- current Proof Contracts for those Claims;
- the minimum assurance required for each Claim.

A `VerificationSpec` is authored or revised atomically. It is not partially valid: a committed revision must satisfy the coverage and contract invariants in this document.

Identity semantics:

- `id` identifies the semantic verification scope/lineage;
- `version` identifies one immutable specification revision;
- `digest` identifies the exact materialized content when used downstream;
- Authority/Governance determines which revision is Current; timestamps do not.

Lifecycle:

`Draft authoring -> Proposed materialization -> Authority/Governance -> Current or Superseded/Historical`

This modeling document does not itself promote a VerificationSpec to Current Authority.

---

### 2.2.2 `Claim`

A stable, falsifiable proposition that Aegis intends to verify.

A Claim is the bridge between user/product Requirements and proof machinery.

A Claim contains:

- stable `id`;
- falsifiable `statement`;
- one or more `requirement_refs`;
- risk factors and criticality classification;
- minimum required assurance;
- reference to its current Proof Contract in this VerificationSpec revision.

A Claim may cover multiple Requirements only when one proposition and one proof contract credibly prove them together. One Requirement may map to multiple Claims.

Identity rule:

- if only proof mechanics change while the proposition remains semantically the same, preserve `claim_id` and revise/supersede its Proof Contract;
- if the proposition itself materially changes, create a new Claim identity and optionally record `supersedes_claim_id`.

### Critical Claim

`Critical Claim` is **not** a separate entity type.

It is a Claim whose `criticality.class == CRITICAL`.

This prevents duplicate lifecycle and identity semantics.

A Claim is Critical when a false acceptance can create material trust failure and ordinary local verification is not sufficient to credibly detect it. Typical triggers include:

- durable data/state corruption or loss;
- core semantic invariant failure;
- protocol / serialization / cross-implementation incompatibility;
- security, safety, or irreversible external effect;
- release-critical performance or reliability contract;
- replay of a high-severity historical defect;
- high downstream dependency fan-out where one false Claim invalidates many downstream conclusions.

The trigger set is extensible, but lowering an already-established criticality classification requires explicit Authority/risk acceptance rather than silent model inference.

---

### 2.2.3 `ProofContract`

The canonical proof semantics for one Claim in one VerificationSpec revision.

A Proof Contract answers:

> What evidence would credibly establish or reject this Claim?

A Proof Contract may be authored as:

- `GENERATED` — expanded from a pinned Proof Profile plus minimal parameters;
- `EXPLICIT` — manually/semantically specified because the Claim warrants direct proof design;
- `CUSTOM` — full escape hatch when standard Profiles are not expressive enough.

Every committed Claim has exactly one current Proof Contract reference in the same VerificationSpec revision.

### Resolved-contract rule

A generated contract MUST retain both:

1. the pinned profile reference and input parameters; and
2. the resolved proof semantics produced from that profile.

Profile evolution must never silently change the meaning of an already-materialized Proof Contract.

Therefore:

`ProfileRef + Parameters -> Resolved Proof Contract Snapshot`

The snapshot, not a future version of the profile template, is the semantic truth used by downstream execution and review.

---

## 2.3 Value objects

The following are values inside durable objects, not independently mutable entities.

### `Criticality`

```text
ORDINARY
CRITICAL
```

Carries explicit reason codes/basis.

### `AssuranceClass`

```text
STANDARD
CHALLENGED
QUALIFIED
```

This is an internal policy result, not a lifecycle stage and not a mandatory user-facing mode.

### `ProofProfileRef`

Base profile taxonomy:

```text
EXAMPLE
PROPERTY
REFERENCE
MEASURE
OBSERVATION
CUSTOM
```

Non-CUSTOM profiles MUST be version-pinned.

### `ChallengeSpec`

Orthogonal challenge modifiers:

```text
BOUNDARY
NEGATIVE
HISTORICAL_REPLAY
FAULT_INJECTION
MUTATION
ADVERSARIAL
```

These answer how the primary verifier is challenged; they are not top-level proof profiles.

### `ExecutionContext`

```text
COMPONENT
INTEGRATION
PLATFORM
CROSS_IMPLEMENTATION
```

Context describes where proof executes, not what proof strategy it is.

### `QualificationSpec`

Nested inside a Proof Contract when verifier qualification is required.

It defines:

- the defect model or verifier weakness being challenged;
- one or more allowed qualification methods;
- the qualification pass rule;
- required qualification evidence.

Qualification is strictly one-hop. A QualificationSpec cannot contain another QualificationSpec.

---

## 2.4 Derived / addressable objects

### `ProofObligation`

A Proof Obligation is generated from an exact VerificationSpec / Proof Contract revision.

It is addressable because P31/P32/P34 need stable references, but it is **derived state**, not independently authored canonical truth.

A Proof Obligation contains at minimum:

- deterministic/stable obligation ID within the exact contract revision;
- Claim and Proof Contract refs;
- obligation kind;
- required evidence kind(s);
- evaluation mode (`DETERMINISTIC` or `REVIEW_REQUIRED`);
- pass/fail condition or review question.

Changing a Proof Contract regenerates its obligation set.

Do not allow direct mutation of an obligation to bypass the Proof Contract.

---

### `ProofEvaluation`

An immutable derived artifact computed from:

- exact VerificationSpec identity/digest;
- exact obligation set;
- exact evidence set;
- exact evaluator version.

It is **not Authority and not a Gate decision**.

Its obligation states are:

```text
SATISFIED
EXCEPTION
UNSATISFIED
```

Meaning:

- `SATISFIED`: evaluator can deterministically establish the obligation from credible evidence;
- `EXCEPTION`: credible resolution requires CONTROL_REVIEW judgment, independent-oracle judgment, semantic interpretation, manual observation review, or another non-deterministic decision;
- `UNSATISFIED`: deterministic evidence is missing, invalid, inaccessible, or failed its pass rule.

Aggregation precedence:

`UNSATISFIED > EXCEPTION > SATISFIED`

ProofEvaluation MUST NOT emit a formal Gate `PASS` or `BLOCKED_*` verdict.

---

### `VerificationSummary`

A derived user-facing view, never canonical truth.

Normal compact shape:

```text
Verification: READY
Critical Claims: <n>
Satisfied: <n>
Exceptions: <n>
```

`Verification: READY` is a workflow/readiness status and must never be confused with an official P34 Gate `PASS`.

---

## 2.5 External / evidence objects

### `EvidenceArtifact`

A durable factual artifact produced by execution, CI, a collector, an external system, or a reviewer.

It is not part of VerificationSpec authority.

Detailed proof evidence may live in a referenced artifact while the existing `.aegis/evidence.json` remains a thin registry of `id/type/ref/status/subject_ids`.

Evidence provenance must distinguish at least:

```text
DETERMINISTIC_COLLECTOR
EXECUTOR
REVIEWER
EXTERNAL
```

Only fields with credible provenance may satisfy obligations that depend on them.

### `Exception`

An Exception is a finding inside ProofEvaluation, not a standalone mutable entity.

It identifies:

- Claim;
- obligation;
- reason code;
- review question / required resolution;
- evidence already available.

P34 resolves the trust question; it does not mutate the original Exception into a fake deterministic SATISFIED result.

---

## 2.6 Core relationships

```text
Requirement 1..* <-> 1..* Claim

VerificationSpec
  1 -> * Claim
  1 -> * ProofContract

Claim
  1 -> 1 current ProofContract (per VerificationSpec revision)

ProofContract
  1 -> * derived ProofObligation

ProofObligation
  * <-> * EvidenceArtifact

VerificationSpec + Obligations + Evidence + EvaluatorVersion
  -> ProofEvaluation

ProofEvaluation
  -> 0..* Exception

ProofEvaluation + independent CONTROL_REVIEW
  -> existing P34 Gate decision
```

---

## 2.7 P10 invariants

1. Every in-scope Requirement is covered by at least one Claim.
2. Every committed Claim has exactly one current Proof Contract in the VerificationSpec revision.
3. Every Critical Claim uses an explicit/resolved Proof Contract; it may have originated from a profile, but its resolved semantics are frozen and inspectable.
4. `Critical Claim` is classification, not a parallel object type.
5. `AssuranceClass` is policy state, not a lifecycle stage.
6. `ProofObligation` is derived from ProofContract and cannot be independently edited.
7. `ProofEvaluation` is derived evidence computation and cannot issue a Gate verdict.
8. `Exception` is a review finding, not a second workflow aggregate.
9. Profile changes cannot retroactively alter an existing resolved Proof Contract.
10. Qualification is one-hop only.

---

# 3. P11 — Interaction / Behavior Model

## 3.1 Authoring session

Verification modeling uses transient authoring state before canonical commit.

### Start

Inputs:

- trusted upstream Authority / Requirements;
- current product/system semantic authority;
- applicable risk metadata/history;
- available Proof Profile catalog.

The authoring session pins the upstream Authority snapshot it is reasoning from.

### Transient work

Aegis may:

1. extract candidate Claims;
2. validate universal Requirement coverage;
3. derive risk factors and Criticality;
4. derive minimum AssuranceClass;
5. select a base Proof Profile;
6. apply context and challenge modifiers;
7. expand the profile into a resolved Proof Contract;
8. identify qualification requirements;
9. generate a compact user summary and exceptions.

These intermediate choices are transient until the VerificationSpec revision commits.

### Commit

A VerificationSpec revision commits atomically only when:

- all in-scope Requirements have coverage;
- every Claim is falsifiable enough to verify;
- every Claim has resolved Criticality;
- every Claim has minimum required AssuranceClass;
- every Claim resolves to one Proof Contract;
- every required profile definition/version is available;
- Critical Claims have inspectable explicit/resolved proof semantics;
- QUALIFIED assurance has a one-hop QualificationSpec;
- no assurance downgrade exists without an explicit risk-acceptance/Authority reference;
- the spec references the exact upstream Authority snapshot.

### Cancel

Canceling an authoring session produces no canonical mutation.

### Retry

Retry against the same pinned upstream Authority may recompute transient choices.

If upstream Authority materially changes during authoring, the session cannot silently commit against the new truth. Rebase/restart the authoring computation against the new trusted Authority.

---

## 3.2 Criticality behavior

Aegis should derive Criticality from explicit risk/Authority signals where possible.

Rules:

1. deterministic structural triggers may automatically elevate a Claim to Critical;
2. semantic reasoning may also propose/elevate Criticality;
3. automatic elevation is allowed when credible;
4. silent downgrade of an established Critical Claim is forbidden;
5. materially ambiguous Criticality creates a blocking review exception rather than defaulting to ordinary;
6. explicit risk acceptance may authorize lower assurance, but must remain traceable.

---

## 3.3 Assurance behavior

Minimum AssuranceClass is derived from Claim risk, historical defects, proof independence needs, and profile/context characteristics.

### STANDARD

Requires a credible primary proof, explicit pass rule, and durable evidence.

### CHALLENGED

Requires STANDARD plus at least one challenge appropriate to the actual defect model, such as boundary, negative, or historical replay.

### QUALIFIED

Requires CHALLENGED plus evidence that the verifier itself is credible for the relevant defect model.

Aegis may automatically strengthen assurance. Weakening below the derived minimum requires explicit Authority/risk acceptance and becomes review-visible.

---

## 3.4 Profile behavior

Profile selection is an authoring convenience, not the final semantic truth.

```text
Claim
+ AssuranceClass
+ ExecutionContext
+ ProofProfileRef(version)
+ minimal parameters
+ ChallengeSpec(s)
-> resolved ProofContract snapshot
```

If a standard Profile cannot express credible proof, use `CUSTOM` rather than expanding the mandatory taxonomy.

No v0.1 profile inheritance hierarchy is defined.

---

## 3.5 Qualification behavior

Qualification asks:

> Would this verifier reject the defect class we are actually worried about?

Representative methods include:

- independent differential oracle;
- mutation sensitivity;
- fault injection;
- historical defect replay;
- independent property oracle;
- adversarial review.

Choose the cheapest method that credibly challenges the verifier.

Qualification terminates after this one verifier challenge. If the qualification result itself cannot be interpreted credibly, route the ambiguity to CONTROL_REVIEW/Authority rather than generating qualification-of-qualification.

---

## 3.6 Execution behavior

Once a VerificationSpec is trusted downstream:

1. materialize Proof Obligations from the exact spec/contract revision;
2. P31 references obligation IDs rather than copying full verification prose;
3. P32 executes the authorized obligations;
4. runner/CI/collector captures deterministic evidence metadata;
5. detailed EvidenceArtifacts are durably materialized;
6. `.aegis/evidence.json` may index those artifacts without becoming the detailed proof database;
7. Proof Evaluator consumes exact obligations + evidence;
8. CONTROL_REVIEW consumes ProofEvaluation and the exact materialized implementation result.

---

## 3.7 Evidence behavior

The following should be collected deterministically when available:

- source revision;
- result revision;
- materialized result ref;
- actual command/probe identity;
- exit code;
- test counts/results;
- fixture/corpus identity and digest;
- artifact URI and digest;
- CI run identity;
- tool/version information;
- available environment fingerprint;
- measured metrics;
- threshold evaluation inputs/results;
- Claim / obligation binding.

Executor-supplied prose does not override deterministic facts.

Executor responsibility remains limited to actual execution, runtime-only observations, setup/actions the collector cannot infer, exact blockers, and scope deviation reporting.

Reviewer responsibility remains semantic credibility, oracle independence, unresolved criticality, manual observation credibility, unexpected scope, Authority conflict, and explicit risk acceptance.

---

## 3.8 Evaluation behavior

For each obligation:

### SATISFIED

Emit only when the evaluator can deterministically prove the pass condition from credible bound evidence.

### UNSATISFIED

Use when a deterministic requirement fails, including missing required evidence, failed threshold, invalid artifact, missing qualification evidence, or inaccessible exact result where accessibility is itself required.

### EXCEPTION

Use when the evidence exists but the trust question requires independent review, including semantic interpretation, oracle independence, manual observation, ambiguous criticality, or a proposed assurance downgrade.

Claim status is the worst state among its obligations.

A ProofEvaluation is immutable. New evidence produces a new evaluation artifact; old evaluations remain historical evidence.

---

## 3.9 P34 behavior boundary

P34 remains independent and formal.

Normal path:

1. independently resolve the exact `materialized_ref`;
2. validate ProofEvaluation provenance/version/input digests;
3. confirm no `UNSATISFIED` obligations;
4. inspect mandatory `EXCEPTION` obligations;
5. issue the existing official P34 Gate verdict.

P34 is not required to re-derive every machine-satisfied deterministic fact unless provenance/integrity is suspect.

Fail closed:

> Any unresolved mandatory EXCEPTION or any UNSATISFIED obligation prevents P34 PASS.

---

# 4. P12 — Semantic Schema

This section defines canonical semantic fields. Concrete JSON Schema files may be produced downstream, but implementations must preserve these meanings.

## 4.1 `VerificationSpec`

```yaml
schema_version: "0.1"
id: <stable verification-scope id>
scope: <semantic scope>
version: <immutable revision/version>
authority_refs:
  - <upstream authority/requirement ref>
claims:
  - <Claim>
proof_contracts:
  - <ProofContract>
extensions: {}
```

Validation:

- `schema_version`, `id`, `scope`, `version`, `authority_refs`, `claims`, and `proof_contracts` are required;
- `authority_refs` is non-empty;
- Claim IDs are unique;
- ProofContract IDs are unique;
- all local references resolve;
- universal Requirement coverage must be validated before readiness;
- exactly one current ProofContract is referenced by each Claim in the revision.

`extensions` may contain explicitly non-semantic metadata. Unknown top-level semantic fields fail closed unless introduced by a compatible schema version.

---

## 4.2 `Claim`

```yaml
id: <stable claim id>
statement: <falsifiable proposition>
requirement_refs:
  - <requirement ref>
criticality:
  class: ORDINARY | CRITICAL
  reasons:
    - <reason code or explicit reason>
  basis: DERIVED | EXPLICIT
risk_factors:
  - <risk factor>
required_assurance: STANDARD | CHALLENGED | QUALIFIED
assurance_basis:
  - <reason>
risk_acceptance_ref: null | <explicit authority/risk acceptance ref>
proof_contract_ref: <ProofContract id>
supersedes_claim_id: null | <Claim id>
```

Required:

- `id`;
- `statement`;
- at least one `requirement_ref`;
- resolved `criticality`;
- `required_assurance`;
- `proof_contract_ref`.

A Claim with materially unresolved criticality is not represented as `ORDINARY`; the VerificationSpec remains blocked from readiness until resolved.

---

## 4.3 `ProofContract`

```yaml
id: <stable contract id>
claim_id: <Claim id>
origin: GENERATED | EXPLICIT | CUSTOM
profile:
  kind: EXAMPLE | PROPERTY | REFERENCE | MEASURE | OBSERVATION | CUSTOM
  version: null | <pinned profile version>
parameters: {}
contexts:
  - COMPONENT | INTEGRATION | PLATFORM | CROSS_IMPLEMENTATION
challenges:
  - kind: BOUNDARY | NEGATIVE | HISTORICAL_REPLAY | FAULT_INJECTION | MUTATION | ADVERSARIAL
    parameters: {}
resolved:
  invariants:
    - id: <local invariant id>
      statement: <what must remain true>
  oracle:
    kind: <oracle/reference kind>
    ref: null | <reference>
    independence_requirement: NONE | REVIEW | INDEPENDENT
  fixtures:
    - id: <local fixture id>
      kind: <fixture/corpus kind>
      ref: null | <reference>
      digest_required: true | false
  probes:
    - id: <local probe id>
      kind: <test/probe kind>
      ref: null | <runner/test/probe ref>
  metrics:
    - id: <local metric id>
      name: <metric>
      unit: null | <unit>
  pass_rules:
    - id: <local pass-rule id>
      expression: <deterministic rule or review question>
  evidence_requirements:
    - id: <local evidence requirement id>
      evidence_type: <type>
      producer_requirement: ANY | DETERMINISTIC | INDEPENDENT | REVIEWER
      required: true | false
  gate_requirement:
    stage: P34
    independent_review: true
qualification: null | <QualificationSpec>
supersedes_contract_id: null | <ProofContract id>
resolved_digest: <digest of resolved semantics>
```

Rules:

1. non-CUSTOM generated Profiles require a pinned profile version;
2. generated contracts retain `parameters` plus the fully `resolved` semantic snapshot;
3. `QUALIFIED` Claim assurance requires non-null QualificationSpec;
4. QualificationSpec cannot recursively contain qualification;
5. `OBSERVATION` alone cannot satisfy a QUALIFIED Claim unless another independent/qualified mechanism provides the missing credibility;
6. `gate_requirement.stage` remains P34 in v0.1.

---

## 4.4 `QualificationSpec`

```yaml
defect_model:
  - <representative verifier failure / implementation defect>
methods:
  - kind: DIFFERENTIAL | MUTATION | FAULT_INJECTION | HISTORICAL_REPLAY | PROPERTY | ADVERSARIAL_REVIEW
    ref: null | <reference>
pass_rule: <what proves verifier sensitivity/independence>
evidence_requirement: <qualification evidence requirement>
```

No nested qualification field exists by design.

---

## 4.5 Derived `ProofObligation`

```yaml
id: <deterministic obligation id>
verification_spec:
  id: <spec id>
  version: <spec version>
  digest: <exact digest>
claim_id: <Claim id>
proof_contract_id: <ProofContract id>
kind: INVARIANT | ORACLE | FIXTURE | PROBE | METRIC | THRESHOLD | EVIDENCE | CHALLENGE | QUALIFICATION | PROVENANCE
evaluation_mode: DETERMINISTIC | REVIEW_REQUIRED
required_evidence_types:
  - <type>
pass_condition: <deterministic rule or review question>
```

Obligation identity MUST be reproducible for the same exact VerificationSpec and obligation generator version, or the artifact must carry a stable explicit mapping that provides equivalent replayability.

---

## 4.6 `EvidenceArtifact`

Detailed EvidenceArtifact shape may vary by runner/provider, but the semantic envelope is:

```yaml
schema_version: "0.1"
id: <evidence artifact id>
producer_class: DETERMINISTIC_COLLECTOR | EXECUTOR | REVIEWER | EXTERNAL
producer:
  name: <producer/tool>
  version: null | <version>
subjects:
  claim_ids: []
  obligation_ids: []
source_ref: null | <source revision/ref>
result_revision: null | <exact result revision>
materialized_ref: null | <reviewer-accessible durable ref>
command: null | <actual command/probe>
exit_code: null | <exit code>
corpus:
  ref: null | <fixture/corpus ref>
  digest: null | <digest>
environment: {}
metrics: []
artifacts:
  - ref: <durable ref>
    digest: null | <digest>
observations: []
created_at: <timestamp>
```

Provider-specific fields belong in extensions/artifacts, not in core semantic requirements.

The existing `.aegis/evidence.json` can index an EvidenceArtifact through its current `id/type/ref/status/subject_ids` model.

---

## 4.7 `ProofEvaluation`

```yaml
schema_version: "0.1"
id: <evaluation id>
verification_spec:
  id: <spec id>
  version: <spec version>
  digest: <exact digest>
obligation_generator:
  name: <generator>
  version: <version>
evaluator:
  name: <evaluator>
  version: <version>
evidence_refs:
  - <EvidenceArtifact ref>
obligations:
  - obligation_id: <id>
    claim_id: <id>
    status: SATISFIED | EXCEPTION | UNSATISFIED
    evidence_refs: []
    reason_code: <reason>
    detail: null | <compact detail>
claims:
  - claim_id: <id>
    status: SATISFIED | EXCEPTION | UNSATISFIED
summary:
  obligations:
    total: <n>
    satisfied: <n>
    exceptions: <n>
    unsatisfied: <n>
  claims:
    total: <n>
    satisfied: <n>
    exceptions: <n>
    unsatisfied: <n>
  critical_claims:
    total: <n>
    satisfied: <n>
    exceptions: <n>
    unsatisfied: <n>
created_at: <timestamp>
```

Normative prohibition:

`ProofEvaluation` MUST NOT contain or imply an official Gate verdict such as `PASS`, `PASS_WITH_FINDINGS`, or `BLOCKED_*`.

Those remain existing P34 Gate decision semantics.

---

## 4.8 Compatibility and extensibility

1. `schema_version` is explicit on materialized semantic artifacts.
2. Unknown required semantic enum values fail closed.
3. Non-semantic extensions may be ignored only when explicitly namespaced/declared optional.
4. Profile versions are pinned and resolved snapshots are retained.
5. VerificationSpec/ProofContract revisions use explicit supersession rather than timestamp winner selection.
6. Derived evaluation can always identify the exact VerificationSpec digest and evaluator/generator version used.
7. Existing `.aegis` Authority/Evidence/Gate registries remain authoritative for their current responsibilities; these new artifacts do not silently supersede them.

---

# 5. P13 — Operation / Mutation Model

## 5.1 Design principle

Prefer immutable revision materialization over fine-grained mutable object operations.

The product does **not** need a public mutation language such as `SET_CRITICALITY`, `ADD_CHALLENGE`, `EDIT_THRESHOLD`, and `MARK_OBLIGATION_SATISFIED` as independent canonical mutations. That would increase workflow and replay complexity with little trust benefit.

The canonical mutation vocabulary is deliberately small.

---

## 5.2 `CREATE_VERIFICATION_SPEC`

Creates the first immutable VerificationSpec revision for a scope.

Preconditions:

- upstream Authority/Requirements are trusted enough for P20;
- no unresolved missing semantic truth is silently invented;
- P10/P12 validation invariants pass.

Atomicity:

- the complete spec revision commits or nothing commits;
- no partially covered Claim set becomes canonical.

Failure:

- unresolved upstream truth -> `BLOCKED_AUTHORITY` / owning earlier-layer blocker;
- missing required modeling input -> `BLOCKED_MISSING_INPUT`;
- unresolved criticality or risk decision -> `BLOCKED_UNRESOLVED_DECISION`.

---

## 5.3 `REVISE_VERIFICATION_SPEC`

Creates a new immutable revision derived from an existing spec.

Payload semantically includes:

- prior spec identity/digest;
- new exact spec body;
- change rationale;
- explicit semantic supersession relation.

Rules:

- preserve Claim identity when the proposition is unchanged;
- create new Claim identity for materially changed propositions;
- proof-only changes may supersede ProofContract while preserving Claim identity;
- lowering criticality/assurance requires explicit risk acceptance/Authority evidence;
- previous spec/evidence/evaluations remain historical and immutable.

A revision does not automatically become Current Authority; Governance controls that promotion.

---

## 5.4 `SUPERSEDE_VERIFICATION_SPEC`

Marks semantic succession through the existing Authority/Governance model.

This operation belongs to Authority lifecycle semantics, not to a local timestamp-based resolver.

The modeling requirement is simply that every new revision can explicitly identify what it supersedes and that downstream artifacts remain pinned to the old exact revision until re-evaluated.

---

## 5.5 `MATERIALIZE_PROOF_OBLIGATIONS`

Pure/derived operation.

Input:

- exact VerificationSpec digest;
- obligation generator version.

Output:

- deterministic/addressable obligation set.

Canonical mutation: none.

Idempotency:

- same exact inputs must produce semantically identical obligations;
- if identifiers are content-derived, IDs must also be identical;
- if an implementation uses explicit generated IDs, it must provide stable replay mapping.

Failure:

- unknown profile/contract semantics or invalid spec -> fail closed; do not guess obligations.

---

## 5.6 `REGISTER_EVIDENCE_ARTIFACT`

Append-only registration of durable factual evidence.

Rules:

- never overwrite old evidence to make a new run appear historically true;
- a retry creates new evidence identity or a new immutable exact artifact;
- deterministic metadata takes precedence over contradictory executor prose;
- local-only/unresolvable evidence cannot satisfy reviewer-accessibility obligations.

Deduplication:

- duplicate registration of the same immutable artifact may be idempotently recognized by identity/digest;
- semantically different runs must not collapse solely because they share a human label.

---

## 5.7 `EVALUATE_PROOF`

Pure/derived operation.

Input:

- exact VerificationSpec digest;
- exact obligation set/generator version;
- exact EvidenceArtifact set;
- evaluator version.

Output:

- immutable ProofEvaluation artifact.

No Authority or Gate mutation occurs.

Determinism:

- deterministic obligations must yield the same semantic result for the same exact inputs/evaluator version;
- review-required obligations remain `EXCEPTION` rather than being guessed into SATISFIED.

Retry:

- additional/new evidence -> new ProofEvaluation;
- old evaluation remains historical.

---

## 5.8 P34 exception resolution

P34 review does not mutate the VerificationSpec or forge deterministic evaluation results.

It may produce reviewer evidence / Gate-review evidence that explains how an EXCEPTION was resolved, then issue the existing Gate decision.

If an exception reveals an upstream ProofContract or Authority defect, route to the owning earlier layer instead of locally weakening the obligation.

---

## 5.9 Ordering

Canonical ordering is semantic, not wall-clock:

```text
Authority/Requirement revision
-> VerificationSpec revision
-> ProofObligation materialization
-> EvidenceArtifact(s)
-> ProofEvaluation
-> P34 Gate decision
```

A downstream artifact pinned to an older exact input remains historically valid evidence for that old input, but it cannot be silently reused as proof for a semantically changed spec.

---

## 5.10 Replay

Replayability requires preserving:

- exact VerificationSpec identity/digest;
- resolved Proof Contract semantics;
- profile version + parameters when profile-generated;
- obligation generator version;
- evidence refs/digests;
- evaluator version.

This is sufficient to explain/recompute proof computation without preserving an entire ChatGPT/Codex conversation transcript.

---

# 6. Machine vs executor vs reviewer responsibility

| Responsibility | Machine / deterministic | Executor | CONTROL_REVIEW |
|---|---|---|---|
| Claim extraction | partial | no | only ambiguity/escalation |
| risk trigger evaluation | yes where structural | no | ambiguous/material judgment |
| profile expansion | yes | no | review only when exception |
| obligation generation | yes | no | no normal-path duplication |
| command/run | orchestrates/captures | performs | no |
| source/result refs | captures | produces result | independently resolves |
| corpus/artifact digest | captures | produces artifact | inspect if disputed |
| metrics/threshold math | yes | no | review exceptions only |
| scope deviation | may detect | must report | judges impact |
| oracle independence | partial | cannot self-certify | owns judgment when required |
| semantic/manual credibility | no | provides observation | owns judgment |
| official Gate verdict | no | no | yes, existing P34 |

---

# 7. Compatibility with current Aegis

## P20

P20 continues to own Verification Design.

Target internal flow:

```text
Requirements
-> Claims
-> Criticality / Assurance
-> Proof Profile authoring abstraction
-> resolved Proof Contracts
-> derived Proof Obligations
```

The existing nine-step proof semantics remain represented inside each resolved Proof Contract.

## P30/P31

Task packages should eventually reference:

- Authority ref;
- VerificationSpec ref/digest;
- Claim refs;
- Proof Obligation refs;
- execution scope/non-goals.

Do not duplicate the full Proof Contract prose into each package.

## P32

Execute obligations and materialize durable evidence. Deterministic collectors should produce transport metadata automatically.

## P34-P36

P34 consumes ProofEvaluation as precomputed review evidence but remains the independent official Gate.

P35 still classifies the owning defect layer.

P36 re-executes affected obligations and relevant regressions after a valid repair.

## `.aegis`

v0.1 preference:

- do not expand `state.json` for Claim/obligation counters;
- keep `.aegis/evidence.json` as a thin evidence index;
- let detailed EvidenceArtifact/ProofEvaluation files be referenced artifacts;
- keep `.aegis/gates.json` as the official Gate decision registry;
- add Project State schema only later if real product evidence shows that persisted proof summaries are necessary.

---

# 8. Explicit rejected complexity

This model intentionally does not introduce:

1. a separate CriticalClaim entity;
2. a separately mutable Assurance entity;
3. a separately mutable Challenge entity;
4. a separately mutable Qualification workflow aggregate;
5. Profile inheritance;
6. numeric risk scoring;
7. a second Machine Gate;
8. direct manual mutation of ProofObligation status;
9. mandatory mutation/fault/differential testing for ordinary claims;
10. qualification-of-qualification;
11. new lifecycle P-stages;
12. mandatory `.aegis/state.json` schema expansion.

---

# 9. P10-P13 acceptance / stage exit

## P10 — Product Object Model: READY

The minimum durable object set is:

```text
VerificationSpec
Claim
ProofContract
```

Everything else is a value object, derived artifact, external evidence, or view unless future evidence justifies promotion.

## P11 — Interaction / Behavior: READY

Authoring, commit/cancel/retry, criticality, assurance, profile expansion, qualification, execution, evidence collection, proof evaluation, and P34 exception review behavior are explicit.

## P12 — Semantic Schema: READY

Canonical field meanings, identity, defaults/optionality, version pinning, compatibility, derived-state boundary, and fail-closed semantics are defined at the contract level.

## P13 — Operation / Mutation Model: READY

The mutation vocabulary is intentionally small:

```text
CREATE_VERIFICATION_SPEC
REVISE_VERIFICATION_SPEC
SUPERSEDE_VERIFICATION_SPEC
MATERIALIZE_PROOF_OBLIGATIONS   # derived
REGISTER_EVIDENCE_ARTIFACT      # append-only evidence
EVALUATE_PROOF                  # derived
```

Atomicity, ordering, idempotency, retry, replay, supersession, and error boundaries are defined.

---

# 10. Next earliest untrusted layer

After this P10-P13 model is accepted, the next earliest untrusted layer for this scope is:

**P14 System Architecture**

The next specialist should determine how the model maps onto:

- P20 authoring/control-plane modules;
- Profile catalog / expansion engine;
- obligation generator;
- evidence collector interfaces;
- evaluator;
- artifact storage / `.aegis` references;
- P31/P32 handoff integration;
- P34 exception-review integration;
- deterministic versus reasoning execution boundaries.

Do not modify `aegis-verification` or begin implementation until architecture and downstream Verification Design have been accepted.
