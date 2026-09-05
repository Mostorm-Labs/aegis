# Aegis Verification Productization v0.1 — P15 Module Design

Status: **Draft / Proposed Authority — P15 Module Design**

Scope: `aegis/verification-productization/modules`

Exact upstream basis:

- Verification Productization semantic head: `2eb7d507098d24328b883dfa1366521390026fce`
- semantic P21 review: `5061120240` — `PASS / ACCEPTED_FOR_DOWNSTREAM`
- Evidence Contract Churn P21 reconciliation: `5119525139` — `PASS / AUTHORITY_SUFFICIENT_WITH_DRIFT_FINDINGS`
- Verification Productization P14 architecture head: `6faa0eff7a53ccd2828eae1b0ef1aeaef1de1a83`
- Evidence Contract Churn P22 five-axis review: `5119537168` — `READY_WITH_FINDINGS`
- fresh repository baseline used for external Current contracts: `main@342d6785d8f54dd9beb2c3bb82398f29b405df2f`

Retained Current external contracts:

- Control Plane Product v0.2, including `CP-FR06 Evidence Compiler` and `CP-FR08 Verification-Bound Implementation Package`;
- Control Plane `CanonicalRef`, `TrustedBasis`, and `VerificationBoundImplementationPackage` semantics;
- Execution Surface v0.2 task-anchor / execution-cursor / result-materialization boundary;
- Project State v0.5 immutable Authority / Gate Decision / Integration lineage;
- P34 sole official Gate ownership and P35 owning-layer classification.

This P15 design completes module/interface detail intentionally deferred by P14. It does **not** create new Verification semantics, does not reopen P02/P03 or P10-P14, and does not begin implementation.

---

# 1. P15 objective

Refine the accepted P14 Proof Plane architecture into independently understandable modules with stable interfaces and invariants so that downstream P16/P17/P20/P30 can implement evidence transport without recreating semantic truth in task-specific JSON or reviewer prose.

The Evidence Contract Churn incidents are treated as architecture-completion evidence, not as permission to invent a parallel proof model.

P15 must make these boundaries mechanically obvious:

```text
semantic proof truth
!= execution observation
!= evidence materialization identity
!= implementation result materialization identity
!= review judgment
```

and:

```text
exact accepted dependency
!= floating human label
```

and:

```text
review navigation
!= new evidence truth
```

Core module-design rule:

> **One semantic source, one authoritative machine producer per fact, one immutable evidence identity, and one independent review boundary.**

---

# 2. Explicit non-goals

P15 does not:

- add a canonical `ProofFact`, `EvidenceManifest`, or `MaterializationEnvelope` aggregate;
- change `VerificationSpec`, `Claim`, `ProofContract`, `CoverageBasis`, `ProofObligation`, `EvidenceArtifact`, `EvidenceInputRef`, or `ProofEvaluation` semantics;
- change the accepted `CLAIM | COVERAGE_BASIS` obligation-subject model;
- make the P31 projection adapter a lifecycle owner;
- make the Evidence Compiler an Authority or Gate owner;
- let the Completeness Checker reuse Obligation Generator traversal as its only expected-set oracle;
- require one monolithic evidence bundle;
- require an EvidenceArtifact to embed the future commit/ref that materializes that same artifact;
- change `.aegis` registries or Project State schema;
- change Execution Surface `Task Anchor != Execution Cursor` semantics;
- create new public `BLOCKED_*` statuses;
- begin P16 runtime-flow design, P17 platform realization, P20 verification design, P30 planning, or P32 implementation.

---

# 3. Module map

P15 freezes eight logical modules. A later implementation may place several in one package/process, but their dependency and write/ownership boundaries remain.

```text
                          +-------------------+
                          |   proof-domain    |
                          +---------+---------+
                                    ^
             +----------------------+----------------------+
             |                      |                      |
             |                      |                      |
      +------+-------+      +-------+--------+      +------+-------+
      |  proof-spec  |      | proof-obligations|     |  proof-ports |
      +------+-------+      +-------+--------+      +------+-------+
             |                      |                      ^
             |                      |                      |
             +-----------+----------+----------------------+
                         |
                  +------v-------+
                  | proof-package|
                  +------+-------+
                         |
                  +------v--------+
                  | proof-evidence|
                  +------+--------+
                         |
                  +------v----------+
                  | proof-evaluation|
                  +------+----------+
                         |
                  +------v------+
                  | proof-review|
                  +-------------+
```

Important independence edge:

```text
VerificationSpec -------------------------------> proof-review completeness traversal
      |
      +-----------------> proof-obligations generation traversal

proof-review MUST NOT call proof-obligations generation traversal to establish expected-set completeness.
```

Allowed shared dependency between generation and review is limited to `proof-domain` canonical parsing, semantic enum definitions, and obligation-identity primitives.

---

# 4. Module: `proof-domain`

## 4.1 Purpose

Pure representation and canonical identity support for already accepted Proof Plane semantics.

Contains implementation-neutral representations/helpers for:

- VerificationSpec / CoverageBasis / Claim / resolved ProofContract;
- ProofObligation and obligation-set identity;
- EvidenceArtifact and EvidenceInputRef;
- ProofEvaluation;
- canonical subject discriminator `CLAIM | COVERAGE_BASIS`;
- canonical ordering, encoding, digest, and semantic-key helpers required by accepted schemas;
- exact-ref bridge helpers needed to expose Proof Plane objects through Control Plane `CanonicalRef` without changing Proof Plane ownership.

## 4.2 Public interfaces

Conceptually:

```text
ProofCodec
  parse(kind, bytes) -> typed value
  canonicalize(value) -> bytes
  digest(value) -> exact digest

ObligationIdentityCodec
  semantic_key(spec, subject, obligation_kind, source_key) -> key
  id_from_key(key) -> obligation_id

EvidenceInputIdentity
  from_materialized_artifact(evidence_id, ref, digest, producer_class)
    -> EvidenceInputRef

CanonicalRefBridge
  verification_spec_ref(spec_identity) -> CanonicalRef<VERIFICATION_SPEC>
  obligation_set_ref(set_identity) -> CanonicalRef<PROOF_OBLIGATION_SET>
  evidence_ref(EvidenceInputRef) -> CanonicalRef<EVIDENCE>
  proof_evaluation_ref(eval_identity) -> CanonicalRef<PROOF_EVALUATION>
```

Exact API names are not normative.

## 4.3 Invariants

- no network, repository, CI, filesystem, or lifecycle mutation;
- no profile selection, obligation traversal, evaluation, or Gate logic;
- canonical encoding/digest is deterministic;
- unknown required schema/enum values fail closed;
- canonical subject meaning is preserved through parse/serialize cycles;
- a Control Plane `CanonicalRef` bridge preserves the exact source identity; it does not create a second semantic identity.

## 4.4 Independence rule

`ObligationIdentityCodec` may be shared by generator and completeness checker because identity encoding is semantic infrastructure.

The algorithm that **discovers which obligations must exist** is not shared. That traversal belongs separately to `proof-obligations` and `proof-review`.

---

# 5. Module: `proof-spec`

## 5.1 Purpose

Implement the deterministic support surface used by the P20 Verification Authoring Controller without taking over P20 semantic judgment.

It contains four internal capabilities:

```text
ProfileCatalog
ProfileResolver
VerificationSpecValidator
VerificationSpecMaterializer
```

## 5.2 Interfaces

```text
ProfileCatalog
  get(profile_ref@version) -> profile definition

ProfileResolver
  resolve(claim, assurance, context, profile_ref, parameters, challenges)
    -> resolved ProofContract snapshot

VerificationSpecValidator
  validate(spec_candidate) -> ValidationResult

VerificationSpecMaterializer
  materialize(valid_spec) -> ExactVerificationSpecRef
```

## 5.3 Invariants

- profile versions are exact and immutable for a resolved contract;
- unknown profile/version fails closed;
- validator enforces accepted CoverageBasis, Claim, assurance, qualification, subject, and version rules only;
- validator does not decide semantic ambiguity or lower risk/assurance;
- materialization does not promote Authority;
- materializer returns exact reviewer-resolvable identity but does not update `.aegis/authorities.json` by itself.

## 5.4 Evidence-contract responsibility

`proof-spec` must make the evidence requirements in each resolved ProofContract machine-readable enough for downstream modules to derive an execution/evidence plan without retyping proof semantics.

If a required evidence condition exists only in prose that cannot be unambiguously resolved by the accepted schema/profile snapshot, validation returns an unresolved semantic condition to P20 rather than letting P31/P32 invent a local interpretation.

---

# 6. Module: `proof-obligations`

## 6.1 Purpose

Own deterministic obligation generation from one exact accepted VerificationSpec.

## 6.2 Interface

```text
ObligationGenerator
  generate(exact_spec_ref, generator_version)
    -> ObligationSet
```

`ObligationSet` contains the accepted exact identity envelope:

```text
VerificationSpec digest
CoverageBasis digest
Generator identity/version
Complete obligation IDs
Obligation count
Obligation-set digest
```

## 6.3 Invariants

- input spec must be exact and validated;
- generation preserves `CLAIM | COVERAGE_BASIS` subject;
- `REVIEW_DECLARED` materializes exactly one required CoverageBasis completeness obligation;
- review-required obligations remain in the complete set;
- generator cannot mark an obligation SATISFIED;
- generator cannot omit an obligation because no executor command is available;
- generator output is never its own completeness proof.

## 6.4 No evidence ownership

`proof-obligations` may describe `required_evidence_types` and pass/review conditions derived from ProofContract semantics. It does not capture runner facts, choose evidence storage, or fabricate task commands.

---

# 7. Module: `proof-package`

## 7.1 Purpose

Bridge exact Proof Plane truth into P31 without becoming a competing package authority.

The canonical P31 package remains the Control Plane `VerificationBoundImplementationPackage`. `proof-package` provides deterministic projection and preflight services consumed by `aegis-implementation` / the Control Plane package materializer.

Internal capabilities:

```text
P31TaskProjector
PackageBindingPreflight
EvidenceContractPreflight
```

## 7.2 `P31TaskProjector`

Interface:

```text
project(
  exact_verification_spec_ref,
  exact_obligation_set_ref,
  exact_scope_contract_ref,
  exact_acceptance_oracle_refs,
  exact_evidence_compilation_contract_ref,
  exact_trusted_basis,
  task_anchor
) -> VerificationPackageProjection
```

Projection result contains only fields already owned by the accepted P31 / Control Plane package contract.

Rules:

1. every Gate-critical Authority / verification / accepted-fact dependency crosses the trust boundary as exact identity;
2. labels such as `accepted A4`, `latest Gate`, `current result`, or `previous accepted baseline` are not package values;
3. resolution of such labels, if used in user/reasoning input, must complete before package projection;
4. projection never copies full ProofContract prose merely for transport;
5. review-only CoverageBasis obligations remain review navigation and are not converted into P32 executable work.

## 7.3 `PackageBindingPreflight`

Before an executable P31 package can be READY, preflight verifies:

- VerificationSpec ref is exact and resolvable;
- obligation-set ref is exact when required by the governing contract;
- TrustedBasis contains exact relevant Authority/Contract/accepted-fact refs;
- scope contract is exact;
- acceptance oracle refs are exact contracts, not executor summaries;
- evidence compilation contract is exact;
- repository-backed execution has a valid task anchor under Current Execution Surface rules;
- no projected exact ref conflicts with the semantic identity embedded in Proof Plane artifacts.

A floating dependency fails before P32. The executor is never responsible for selecting which accepted result a package meant.

## 7.4 `EvidenceContractPreflight`

P15 defines a bounded, deterministic satisfiability preflight over evidence-production dependencies.

It builds a transient dependency graph over required values and production phases:

```text
P31_FREEZE
  -> P32_EXECUTION
  -> EVIDENCE_COMPILE
  -> ARTIFACT_MATERIALIZE
  -> RESULT_MATERIALIZE
  -> P34_REVIEW
```

This graph is implementation/preflight state only; it is not a new canonical object.

The preflight rejects at least:

1. a required EvidenceArtifact field whose value can exist only after the same artifact has been materialized and whose materialization identity itself depends on that field;
2. a requirement that a repository artifact embed the future commit SHA of the commit containing that artifact;
3. a required exact ref whose provider contract offers only mutable/unpinned identity at the required phase;
4. a deterministic P32 evidence requirement that can only be supplied by a later P34 judgment;
5. circular evidence dependencies that have no externally fixed immutable anchor.

Allowed pattern:

```text
EvidenceArtifact content
  -> materialize
  -> EvidenceInputRef returned externally
  -> ReviewBundle references EvidenceInputRef
```

Allowed implementation-result pattern:

```text
P32 result/evidence content
  -> exact result materialization
  -> result_revision + materialized_ref returned by execution surface
  -> P34 independently resolves materialized_ref
```

Forbidden pattern:

```text
artifact bytes must contain the future commit/ref whose identity depends on those artifact bytes
```

`EvidenceArtifact.materialized_ref` is already nullable in the accepted semantic envelope. When its own durable ref is self-dependent, the field remains null/absent as permitted in the content and the exact materialized identity is carried by the returned `EvidenceInputRef` / review navigation boundary instead.

## 7.5 Non-ownership

`proof-package` does not:

- authorize P32;
- create Current Authority;
- decide a P34 verdict;
- choose a missing semantic dependency;
- silently weaken a contract to make it satisfiable.

If satisfiability requires changing semantic truth, it routes the unresolved contract back to the owning earlier layer.

---

# 8. Module: `proof-ports`

## 8.1 Purpose

Define platform-neutral interfaces for systems that own execution facts or artifact persistence. P17 chooses concrete adapters/protocols.

Logical ports:

```text
ObservationSourcePort
ArtifactStorePort
ExactRefResolverPort
ResultMaterializationPort
```

## 8.2 `ObservationSourcePort`

```text
capture(execution_binding) -> ObservationBatch
```

`ObservationBatch` is a transient DTO, not Evidence and not Authority.

Each observation record carries enough producer identity to establish where the fact came from, for example:

```text
producer class / producer id
provider run/job identity
subject/result identity when known
command/probe identity
raw test case/result records or authoritative machine summary
metric samples
artifact locations
exit/result codes
environment facts
```

P17 defines GitHub/CI/runner-specific representation.

## 8.3 `ArtifactStorePort`

```text
materialize(bytes, media_type, metadata) -> ImmutableArtifactLocator
resolve(locator) -> bytes + immutable identity
```

The port must be capable of producing reviewer-resolvable exact identity for required proof inputs.

## 8.4 `ExactRefResolverPort`

```text
resolve(exact_ref) -> immutable/currentness result
```

Used for package preflight/review navigation. It must not convert a mutable alias into an accepted exact ref without an owning control/governance resolution step.

## 8.5 `ResultMaterializationPort`

Represents the Current Execution Surface result-materialization boundary.

```text
resolve_result(result_ref) -> exact result materialization
```

This is separate from EvidenceArtifact materialization because implementation result identity and proof-input identity are related but not the same truth family.

---

# 9. Module: `proof-evidence`

## 9.1 Purpose

Implement the Product Authority's Evidence Compiler direction using P14's Evidence Collector Gateway + Evidence Materializer responsibilities.

Internal capabilities:

```text
EvidencePlanBuilder
EvidenceCollector
EvidenceCompiler
EvidenceMaterializer
EvidenceIndexProjector
```

Only `EvidenceArtifact` / `EvidenceInputRef` are accepted durable proof objects. `ObservationBatch`, `EvidencePlan`, and `EvidenceIndexView` are transient/derived implementation DTOs.

## 9.2 `EvidencePlanBuilder`

```text
build(exact_spec, exact_obligation_set, evidence_compilation_contract)
  -> EvidencePlan
```

Rules:

- derives required observation/fact keys from exact obligations and evidence compilation contract;
- does not restate semantic pass conditions independently;
- records which producer class/source is authoritative for each machine-observable fact family;
- marks review-required evidence separately from deterministic execution facts;
- fails closed when the same required fact has conflicting authoritative producer assignments.

## 9.3 `EvidenceCollector`

```text
collect(plan, execution_binding) -> ObservationBatch
```

Collection happens as close as practical to the actual runner/CI/provider so facts do not require human retranscription.

Executor narrative may be captured as explicitly `EXECUTOR` provenance when needed, but it cannot override a conflicting deterministic collector fact.

## 9.4 `EvidenceCompiler`

```text
compile(plan, observation_batches) -> EvidenceArtifactCandidate[]
```

Core single-source rules:

1. a machine-observable fact is taken from its declared authoritative producer, not from hand-authored summary prose;
2. if raw structured test records are available, counts/summaries are derived from those records by one compiler path rather than re-entered separately;
3. if only a provider's authoritative machine summary exists, that summary is preserved as the source fact and is not retyped by an executor;
4. conflicting authoritative observations for the same exact fact identity fail closed rather than selecting whichever value makes the Gate pass;
5. derived totals/metrics carry derivation provenance internally and are serialized once into EvidenceArtifact content;
6. executor/reviewer comments may add observations but cannot replace deterministic facts;
7. compilation never writes an official Gate verdict into evidence.

This directly prevents a pattern where a runner reports one skip count while a separately hand-maintained evidence JSON records another.

## 9.5 EvidenceArtifact content boundary

Compiler emits the accepted EvidenceArtifact semantic envelope.

Interpretation of key identities:

- `source_ref` / `result_revision` describe the subject execution/result when known independently;
- `materialized_ref` inside EvidenceArtifact is optional and may name an already-existing external immutable resource;
- the immutable identity of the EvidenceArtifact **itself** is established by the materializer and returned as `EvidenceInputRef`;
- no field is populated with a guessed future commit/ref merely to make the artifact appear complete.

## 9.6 `EvidenceMaterializer`

```text
materialize(candidate) -> EvidenceInputRef
```

Steps conceptually:

```text
validate candidate
canonicalize / serialize
materialize through ArtifactStorePort
resolve immutable identity
construct EvidenceInputRef(evidence_id, ref, digest, producer_class)
return exact input binding
```

Failure to produce exact reviewer-resolvable identity prevents deterministic satisfaction of obligations that depend on the artifact.

## 9.7 `EvidenceIndexProjector`

May derive a thin navigation/index view for `.aegis/evidence.json` or a review manifest.

Invariant:

> The index/manifest references evidence; it does not become a second copy of fact truth.

A manifest may include identifiers, refs, digests, subject bindings, applicability, and navigation status. It must not require independent re-entry of test counts or metric values already owned by EvidenceArtifact/ProofEvaluation.

---

# 10. Module: `proof-evaluation`

## 10.1 Purpose

Compute immutable ProofEvaluation and compact VerificationSummary from exact proof inputs.

Internal capabilities:

```text
EvidenceResolver
ProofEvaluator
VerificationSummaryProjector
```

## 10.2 Interface

```text
ProofEvaluator.evaluate(
  exact_spec_ref,
  exact_obligation_set_ref,
  EvidenceInputRef[],
  evaluator_version
) -> ProofEvaluation
```

## 10.3 Invariants

- every EvidenceInputRef is resolved and exact before deterministic use;
- digest/ref mismatch fails the affected obligation closed;
- evaluation covers exactly the bound obligation set;
- no missing obligation silently disappears from summary totals;
- `REVIEW_REQUIRED` stays `EXCEPTION` until review-side resolution under the accepted model;
- Claim and CoverageBasis aggregates remain separate while overall counts include both;
- changed evidence creates a new ProofEvaluation; historical evaluation is never rewritten;
- evaluator emits only `SATISFIED | EXCEPTION | UNSATISFIED`, never Gate PASS.

## 10.4 Summary rule

All summary counts are derived from the exact per-obligation evaluation records. No caller supplies total/satisfied/exception/unsatisfied counts as independent authoritative values.

---

# 11. Module: `proof-review`

## 11.1 Purpose

Provide independent review-side derivation and navigation for P34 without becoming P34 itself.

Internal capabilities:

```text
IndependentCompletenessChecker
ReviewContractDiffer
ReviewBundleAssembler
```

## 11.2 `IndependentCompletenessChecker`

```text
expected_keys(exact_spec_ref, checker_version) -> ExpectedObligationKeySet
check(expected_keys, exact_obligation_set_ref, proof_evaluation_ref)
  -> CompletenessCheckResult
```

Rules:

- parses exact VerificationSpec through `proof-domain`;
- derives expected semantic obligation keys through a review-owned traversal;
- may reuse canonical identity codec and enum definitions;
- MUST NOT call the generator traversal or use generator output as the source of expected truth;
- checks obligation-set equality and evaluation-set equality;
- preserves the mandatory REVIEW_DECLARED CoverageBasis completeness obligation;
- returns review evidence, not Gate verdict.

## 11.3 `ReviewContractDiffer`

Purpose: expose whether a Gate-requested check was already part of the frozen accepted contract without deciding P35 defect ownership.

```text
compare(review_requirement, frozen_spec/package/review_contract)
  -> DECLARED
   | EXISTING_REVIEW_ONLY
   | UNDECLARED
   | STRUCTURALLY_UNSATISFIABLE
```

These are internal comparison results, not public Aegis status values.

Rules:

- `UNDECLARED` cannot be silently injected into an already-executed P31 package;
- `STRUCTURALLY_UNSATISFIABLE` cannot be converted into an executor evidence repair;
- P34/P35 remains responsible for deciding whether the root cause is review defect, missing verification contract, package projection defect, Authority gap, or another existing class;
- the original package/spec/evidence remains immutable while a corrected earlier-layer artifact is created if required.

This prevents post-hoc Gate schema expansion from being misrepresented as a P32 transcription defect.

## 11.4 `ReviewBundleAssembler`

```text
assemble(
  authority_refs,
  package_ref,
  verification_spec_ref,
  obligation_set_ref,
  evidence_input_refs,
  proof_evaluation_ref,
  implementation_result_revision,
  implementation_materialized_ref,
  completeness_check_ref,
  mandatory_exceptions,
  contract_diff_summary
) -> ReviewBundleView
```

`ReviewBundleView` is derived navigation only.

It MUST keep these identities visibly separate:

```text
Proof evidence identity     = EvidenceInputRef(s)
Proof evaluation identity   = ProofEvaluation ref/digest
Implementation result       = result_revision
Result durable boundary     = materialized_ref
Formal acceptance           = later P34 Gate Decision
```

The bundle may be composite. It does not require all source evidence to be copied into one file.

## 11.5 Non-ownership

`proof-review` cannot:

- resolve semantic exceptions as deterministic SATISFIED;
- mutate the package because review wants another field;
- repair executor evidence;
- issue `PASS`, `PASS_WITH_FINDINGS`, or official `BLOCKED_*` Gate decisions;
- update Project State Gate Decision lineage.

---

# 12. Stable cross-module DTOs

P15 deliberately keeps the following as non-canonical implementation DTOs:

```text
ObservationBatch
EvidencePlan
EvidenceArtifactCandidate
VerificationPackageProjection
ExpectedObligationKeySet
CompletenessCheckResult
ReviewBundleView
ContractDiffResult
EvidenceDependencyGraph
```

Rules:

1. DTOs may be regenerated from exact canonical/external inputs;
2. no DTO becomes Authority merely because it is serialized for debugging;
3. if a DTO is persisted for audit/navigation, its persistence does not create a new semantic source of truth;
4. downstream code must resolve back to the canonical Proof/Control/Execution identities carried by the DTO.

This is how the useful three-layer mental model is retained without a parallel object model:

```text
"Proof facts"
  -> machine observations compiled into EvidenceArtifact content

"Evidence manifest"
  -> derived EvidenceIndexView / ReviewBundleView over exact refs

"Materialization envelope"
  -> EvidenceInputRef plus Execution Surface result_revision/materialized_ref and StageOccurrence lineage
```

---

# 13. Dependency rules

Allowed stable dependency direction:

```text
proof-domain
   ^
   +-- proof-spec
   +-- proof-obligations
   +-- proof-package
   +-- proof-evidence
   +-- proof-evaluation
   +-- proof-review
   +-- proof-ports (typed contracts may depend on domain identities)
```

Additional rules:

1. `proof-spec` does not import P31/P34 implementations.
2. `proof-obligations` does not import `proof-review`.
3. `proof-review` does not import generator traversal from `proof-obligations`.
4. `proof-package` may consume Proof Plane exact identities and expose Control Plane package fields, but cannot persist/authorize P31 by itself.
5. `proof-evidence` may call ports but cannot call Gate-review mutation APIs.
6. `proof-evaluation` has no write access to EvidenceArtifact storage except through explicit read/resolve ports.
7. `proof-review` reads exact artifacts and emits review inputs only.
8. cyclic semantic dependencies are forbidden.

---

# 14. Failure ownership / fail-closed boundaries

P15 does not create new public statuses. Modules emit typed diagnostics to the lifecycle owner, which maps them into the existing Aegis status/defect taxonomy.

Representative boundaries:

| Failure | Detecting module | Earliest likely owning layer |
|---|---|---|
| VerificationSpec semantic ambiguity | `proof-spec` | P20 / earlier Authority as appropriate |
| Obligation-generation unsupported semantic | `proof-obligations` | P20/P12 only if accepted semantics truly missing |
| floating accepted dependency | `proof-package` | P31 package projection / earlier unresolved Authority input |
| impossible self-referential evidence requirement | `proof-package` EvidenceContractPreflight | contract/spec/review layer that authored it |
| runner facts unavailable | `proof-evidence` | P32/P36 environment/evidence |
| machine fact conflicts with separately supplied executor summary | `proof-evidence` | evidence compilation / producer integrity |
| evidence materialization cannot produce exact ref | `proof-evidence` | evidence/environment boundary |
| EvidenceInputRef digest mismatch | `proof-evaluation` / `proof-review` | evidence integrity |
| generated obligation set incomplete | `proof-review` | generator/spec depending root cause |
| Gate requests undeclared field after execution | `proof-review` differ | P35 classifies review/spec/package owner |
| P34 judgment unresolved | existing P34 | CONTROL_REVIEW |

No downstream implementation module is allowed to repair an earlier semantic/Authority defect by inventing a field or choosing an ambiguous accepted baseline.

---

# 15. Evidence Contract Churn regression design hooks

P20 later owns the actual VerificationSpec/tests, but P15 freezes the interfaces required to make the incident classes mechanically testable.

## R1 — authoritative test-summary mismatch

Required module behavior:

- structured test records or authoritative runner summary enter through `ObservationSourcePort`;
- `EvidenceCompiler` derives summary once;
- caller cannot override generated pass/skip/fail counts with hand-entered values;
- conflicting machine facts fail closed.

## R2 — floating accepted dependency

Required module behavior:

- `PackageBindingPreflight` rejects unresolved/floating dependency labels;
- P32 receives exact CanonicalRef/TrustedBasis/package bindings only.

## R3 — self-referential materialization

Required module behavior:

- `EvidenceContractPreflight` identifies the future-self-identity dependency cycle before P32;
- EvidenceArtifact may omit/null its own not-yet-existing `materialized_ref` as accepted by v0.1;
- EvidenceMaterializer returns exact EvidenceInputRef externally;
- implementation `materialized_ref` remains Execution Surface return metadata resolved by P34.

## R4 — post-hoc Gate schema expansion

Required module behavior:

- `ReviewContractDiffer` identifies an undeclared requirement;
- existing package/evidence is not edited to pretend the requirement was always present;
- P35 classifies the owning earlier layer.

## R5 — evidence-only repair

Required module behavior:

- when implementation semantics/result remain unchanged and only evidence compilation/materialization is defective, a new immutable EvidenceArtifact / EvidenceInputRef / ProofEvaluation may bind the same unchanged result revision;
- historical faulty evidence remains preserved;
- no source implementation change is required solely to regenerate truthful evidence.

---

# 16. Compatibility and migration

## 16.1 Existing Proof Plane drafts

PR #23 semantic package remains the semantic basis. P15 does not require a new P12 revision.

PR #24 P14 package remains the architecture basis. P15 adds module detail; it does not replace P14 topology.

## 16.2 Current Control Plane

Control Plane `CanonicalRef`, `TrustedBasis`, `VerificationBoundImplementationPackage`, StageOccurrence, and Execution Surface result materialization remain externally owned contracts.

P15 adapters must conform to them rather than forking them.

## 16.3 Existing evidence artifacts

Historical evidence remains immutable and interpretable under the contract that produced it.

New compiler/runtime code may ingest legacy artifacts through compatibility readers, but must not rewrite old evidence to satisfy new module invariants.

A legacy artifact that lacks the exact identity required for a new ProofEvaluation cannot be silently upgraded; applicability/requalification must be explicit.

## 16.4 `.aegis` registries

No Project State schema change is required by P15.

Thin evidence/Authority/Gate registries remain thin. Detailed Proof Plane artifacts stay behind exact refs.

---

# 17. P15 exit criteria

P15 is `READY` when downstream P16 can trace runtime behavior without inventing module ownership or semantic truth.

This design satisfies that condition when all of the following are accepted:

1. `proof-domain` is the only shared semantic/identity primitive layer.
2. generator and completeness checker share identity primitives but not expected-set traversal.
3. P31 projection consumes exact Verification/TrustedBasis refs and rejects floating trust labels before P32.
4. evidence-contract satisfiability is checked before execution; future-self materialization cycles fail closed.
5. machine-observable facts enter through structured observation ports and are compiled once.
6. evidence summaries are derived from authoritative machine facts rather than independently retyped.
7. EvidenceArtifact self-materialization identity is returned externally as EvidenceInputRef; implementation result materialization remains a separate Execution Surface boundary.
8. ProofEvaluation consumes only exact EvidenceInputRefs and derives its own totals.
9. review navigation preserves the distinction between evidence, evaluation, implementation result, result materialization, and Gate decision.
10. post-hoc review requirements are surfaced as contract deltas rather than silently injected into prior P31/P32 work.
11. evidence-only repair can regenerate immutable evidence/evaluation against an unchanged valid result without rewriting history.
12. no module introduced a second Gate, Authority store, Project State, or parallel proof-fact model.

---

# 18. P15 disposition

```yaml
P15_module_design:
  scope: aegis/verification-productization/modules
  semantic_basis: 2eb7d507098d24328b883dfa1366521390026fce
  architecture_basis: 6faa0eff7a53ccd2828eae1b0ef1aeaef1de1a83
  p21_evidence_churn_review: 5119525139
  p22_drift_review: 5119537168

  new_canonical_objects: NONE
  p12_repair_required: false
  p14_topology_change_required: false

  modules:
    - proof-domain
    - proof-spec
    - proof-obligations
    - proof-package
    - proof-ports
    - proof-evidence
    - proof-evaluation
    - proof-review

  key_repairs_by_design:
    authoritative_fact_single_source: FROZEN
    exact_p31_dependency_projection: FROZEN
    evidence_contract_satisfiability_preflight: FROZEN
    self_referential_materialization_prohibition: FROZEN
    post_hoc_review_delta_detection: FROZEN
    evidence_only_repair_path: PRESERVED

  status: READY
  next_owner: aegis-architecture
  next_stage: P16_RUNTIME_DATA_FLOW
```

Stop after P15 materialization. Do not automatically execute P16.