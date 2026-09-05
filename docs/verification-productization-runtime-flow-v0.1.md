# Aegis Verification Productization v0.1 — P16 Runtime Data Flow

Status: **Draft / Proposed Authority — P16 Runtime Data Flow**

Scope: `aegis/verification-productization/runtime-flow`

Exact upstream basis:

- Verification Productization semantic head: `2eb7d507098d24328b883dfa1366521390026fce`
- semantic P21 review: `5061120240` — `PASS / ACCEPTED_FOR_DOWNSTREAM`
- Verification Productization P14 architecture head: `6faa0eff7a53ccd2828eae1b0ef1aeaef1de1a83`
- Verification Productization P15 module-design head: `e771cf450c9878105a28a83b6c05fb58d1d8384f`
- Evidence Contract Churn P21 reconciliation: `5119525139`
- Evidence Contract Churn P22 five-axis review: `5119537168`
- fresh external Current baseline: `main@342d6785d8f54dd9beb2c3bb82398f29b405df2f`

Retained external contracts:

- Control Plane `VerificationBoundImplementationPackage`, `CanonicalRef`, `TrustedBasis`, and StageOccurrence semantics;
- Current Execution Surface repository identity, `Task Anchor != Execution Cursor`, P32/P33 result materialization, and reviewer-accessible `materialized_ref` boundary;
- P34 as sole formal Gate owner, with P35 owning-layer classification and P36 repair/reverification;
- thin `.aegis` Authority/Evidence/Gate registries and immutable historical truth.

This P16 design traces temporal behavior across the P15 modules. It does not alter Verification semantics, module ownership, platform realization, verification policy, implementation authorization, or Gate authority.

---

# 1. P16 objective

Freeze the temporal ordering, interruption behavior, recovery rules, persistence boundaries, and fail-closed ownership needed to carry one exact Verification design from P31 package projection through P32 execution, Evidence compilation/materialization, ProofEvaluation, independent review preparation, and P34.

P16 must make the following temporal distinctions explicit:

```text
semantic design freeze
!= package freeze
!= execution
!= observation capture
!= evidence compilation
!= evidence materialization
!= implementation result materialization
!= proof evaluation
!= review preparation
!= Gate judgment
```

Core rule:

> **A later phase may consume exact immutable truth from an earlier phase, but it may not rewrite that earlier truth to make the later phase easier.**

---

# 2. Explicit non-goals

P16 does not:

- add lifecycle stages or new public statuses;
- create a workflow daemon or hidden cross-Primary owner;
- define GitHub/Codex/CI/filesystem concrete adapters; P17 owns that;
- define final CLI flags, queues, storage products, or retry intervals; P17/P18 own those;
- change P20 ProofContract semantics;
- change the P15 module set;
- authorize P31, P32, P34, P35, or P36 work;
- let a deterministic module issue a formal Gate verdict;
- permit executor or review prose to replace exact machine facts;
- require all evidence to live in one artifact or one repository commit;
- require EvidenceArtifact content to contain its own future materialization identity.

---

# 3. Runtime ownership rule

Module execution does not transfer lifecycle ownership.

The relevant control boundaries remain:

```text
P20 semantic verification design       -> aegis-verification
P31 package authorization               -> aegis-implementation
P32 implementation/execution            -> aegis-implementation
P33 interrupted execution reconciliation-> aegis-implementation
P34 independent Gate                    -> aegis-gate-review
P35 defect ownership classification     -> aegis-gate-review
P36 repair/reverification               -> aegis-gate-review
```

`proof-*` modules are deterministic/supporting components invoked under the active owning stage.

A completed Primary occurrence may prepare exact output for the next stage, but it does not itself author or execute the next Primary's substantive occurrence. Existing single-Primary composition rules remain intact.

---

# 4. Runtime phase model

P16 uses the following implementation-neutral phases. These are architecture phases, not new Aegis lifecycle statuses and not canonical objects.

```text
F0  EXACT_PROOF_BASIS
F1  PACKAGE_PREFLIGHT
F2  EXECUTION_AND_OBSERVATION
F3  EVIDENCE_COMPILE
F4  EXACT_MATERIALIZATION
F5  PROOF_EVALUATION
F6  REVIEW_PREPARATION
F7  P34_CONTROL_REVIEW
```

The minimal causal chain is:

```text
exact VerificationSpec / obligation set
  -> exact P31 projection + satisfiability preflight
  -> authorized P32 execution
  -> authoritative observations
  -> EvidenceArtifact candidate(s)
  -> exact EvidenceInputRef(s)
  -> exact implementation result materialization
  -> ProofEvaluation
  -> independent completeness / review navigation
  -> P34
```

`EvidenceInputRef` materialization and implementation-result materialization are separate truth families. Their relative ordering may vary by platform topology, subject to the partial-order rules in Section 8.

---

# 5. F0 — Exact proof basis

## 5.1 Inputs

F0 begins only from exact immutable Proof Plane inputs:

- exact VerificationSpec ref/digest;
- exact CoverageBasis identity;
- exact complete obligation-set ref/digest;
- exact applicable oracle/evidence-compilation contracts;
- exact upstream Authority/accepted facts needed by downstream package construction.

## 5.2 Owner and supporting modules

Lifecycle owner is the stage that established or accepted the verification basis. `proof-domain`, `proof-spec`, and `proof-obligations` provide deterministic support.

## 5.3 Exit invariant

No downstream task package may rely on floating phrases such as:

```text
accepted A4
latest Gate
current result
previous accepted baseline
```

Those labels must have been resolved into exact identities before F1.

A missing exact identity is not deferred to P32.

---

# 6. F1 — Package projection and preflight

## 6.1 Sequence

Under P31 ownership:

```text
1. P31TaskProjector consumes exact F0 inputs.
2. PackageBindingPreflight validates exact package bindings.
3. EvidencePlanBuilder derives required evidence fact families.
4. EvidenceContractPreflight builds the transient EvidenceDependencyGraph.
5. If all checks pass, the owning P31 flow may materialize/authorize the canonical VerificationBoundImplementationPackage.
```

The order matters: evidence satisfiability is checked before implementation begins.

## 6.2 Contract freeze boundary

Once the executable P31 package is materialized and authorized, the following are frozen for that package revision:

- exact TrustedBasis;
- exact implementation scope;
- exact VerificationSpec / obligation-set binding;
- exact acceptance-oracle refs;
- exact evidence-compilation contract;
- Gate/review policy binding;
- task anchor where applicable.

A later review may ask questions allowed by the frozen review contract, but it cannot silently add a new P32 deterministic evidence obligation to the old package.

A material change creates a new upstream spec/package revision as owned by the appropriate earlier layer.

## 6.3 Fail-closed exits

P32 is not authorized from this package when preflight detects:

- floating/unresolved trust dependency;
- exact-ref mismatch;
- missing required task anchor;
- evidence requirement that depends on future P34 judgment;
- future-self identity cycle;
- required immutable identity unavailable at the required phase;
- circular evidence production with no external immutable anchor.

The executor must not guess a repair.

---

# 7. F2 — Execution and authoritative observation

## 7.1 Entry

F2 starts only after the owning P32 flow has independently performed the existing Execution Surface preflight, including repository identity/package resolution and anchor/cursor checks where applicable.

## 7.2 Execution binding

The active execution supplies a platform-neutral binding containing enough exact context for collection, conceptually:

```text
package_ref
exact task/obligation bindings
execution/run identity
source/starting revision
result working identity when available
authoritative producer assignments
```

This is runtime metadata, not new canonical Authority.

## 7.3 Observation capture

`EvidenceCollector` invokes `ObservationSourcePort` as close as practical to the producing runner/provider.

For each machine-observable fact family, the EvidencePlan names one authoritative source contract.

Examples:

- raw test-case records;
- provider-native authoritative test summary;
- exit code;
- metric samples;
- fixture/corpus identity;
- CI run identity;
- command/probe identity;
- environment facts.

Executor narrative may coexist with `EXECUTOR` provenance, but it cannot override a conflicting deterministic source.

## 7.4 Completion barrier

Evidence compilation must not infer successful completion from partial arrival.

Before a required observation family is considered complete, the collector must have a provider-defined completion condition such as:

- run/job terminal state;
- complete structured result set;
- explicit end-of-stream/completeness marker;
- immutable provider artifact known to contain the complete result.

P17 defines the concrete provider mechanism.

Absent completion is missing evidence, not zero failures.

---

# 8. F3/F4 — Evidence compilation and materialization

## 8.1 Compilation sequence

```text
ObservationBatch(es)
  -> validate producer identity/completeness
  -> reconcile exact fact identity
  -> derive summaries/metrics once
  -> build EvidenceArtifactCandidate
  -> validate semantic envelope
```

For structured test results:

```text
raw authoritative records
  -> one compiler derivation
  -> pass/fail/skip totals
```

A second independently authored total is not accepted as competing truth.

If two authoritative sources conflict for the same exact fact identity, compilation fails closed.

## 8.2 Two valid materialization topologies

P16 intentionally defines a partial order rather than one universal sequence.

### Topology A — external evidence artifact

Use when EvidenceArtifact is persisted independently of the implementation result:

```text
execute
 -> observe
 -> compile EvidenceArtifact bytes
 -> ArtifactStorePort materializes exact evidence
 -> EvidenceInputRef exists
 -> implementation result materializes
 -> evaluation/review consume both exact identities
```

### Topology B — evidence artifact carried inside implementation result

Use when EvidenceArtifact is a file or artifact whose exact reviewer ref depends on the final implementation result identity:

```text
execute
 -> observe
 -> compile EvidenceArtifact bytes
 -> include bytes in result candidate
 -> implementation result materializes
 -> exact result identity becomes known
 -> EvidenceMaterializer/ExactRefResolver binds the committed artifact
 -> EvidenceInputRef exists
 -> evaluation/review consume both exact identities
```

This is allowed because the EvidenceArtifact content does not contain the future result identity that is needed to identify the artifact itself.

## 8.3 Universal partial-order invariants

Regardless of topology:

1. authoritative observation precedes compilation;
2. EvidenceArtifact bytes precede their own immutable identity;
3. no artifact content depends on the future identity generated from those same bytes;
4. implementation result content precedes implementation `materialized_ref`;
5. P34 receives exact evidence identity and exact implementation-result identity as distinct refs;
6. ProofEvaluation does not treat implementation `materialized_ref` as a substitute for EvidenceInputRef;
7. review navigation may connect the identities but does not collapse them.

---

# 9. F5 — Proof evaluation

## 9.1 Entry condition

Evaluation begins only when every EvidenceInputRef used for deterministic satisfaction is exact and resolvable.

## 9.2 Sequence

```text
resolve exact VerificationSpec
resolve exact obligation set
resolve each EvidenceInputRef
verify ref/digest/native immutable identity
check evaluation-set equality against bound obligation set
evaluate each obligation
aggregate Claim / CoverageBasis / overall counts
materialize immutable ProofEvaluation
project VerificationSummary
```

## 9.3 Fail-closed rules

- unresolved evidence -> affected obligation is not SATISFIED;
- digest/ref mismatch -> affected evidence is invalid;
- missing required obligation -> no clean summary;
- `REVIEW_REQUIRED` -> remains `EXCEPTION` until review-side resolution;
- summary totals are derived from per-obligation evaluation and cannot be supplied by a caller;
- evaluation never issues formal Gate PASS.

A changed evidence set always creates a new ProofEvaluation.

---

# 10. F6 — Independent review preparation

## 10.1 Sequence

Under preparation for P34:

```text
1. IndependentCompletenessChecker parses exact VerificationSpec directly.
2. It derives ExpectedObligationKeySet through review-owned traversal.
3. It compares expected set vs generated obligation set.
4. It compares complete obligation set vs ProofEvaluation evaluation set.
5. ReviewContractDiffer compares any review-requested requirement with frozen spec/package/review contract.
6. ReviewBundleAssembler builds derived navigation over exact refs.
```

The completeness checker may share canonical parsing and identity codecs with the generator but not its expected-set traversal.

## 10.2 Review bundle separation

ReviewBundleView must preserve:

```text
EvidenceInputRef(s)
ProofEvaluation identity
implementation result_revision
implementation materialized_ref
completeness-check evidence
mandatory EXCEPTIONs
contract-diff result
```

The bundle is not a new evidence source and does not copy machine facts merely for convenience.

---

# 11. F7 — P34 independent Gate

P34 remains outside the Proof Runtime.

At minimum the P34 owner independently resolves:

- intended Authority / verification basis;
- implementation package and exact result materialization;
- exact EvidenceInputRefs;
- ProofEvaluation identity and provenance;
- completeness-check result;
- mandatory exceptions;
- scope/Authority conformance;
- review-contract applicability.

Only P34 may issue the formal Gate verdict.

A CI green state, ProofEvaluation READY-like summary, or zero deterministic failures cannot substitute for P34.

---

# 12. Retry model

Retry means repeating a failed or incomplete runtime operation without silently changing its semantic inputs.

## 12.1 Deterministic retry

For the same exact inputs:

- spec validation is replayable;
- obligation generation is replayable;
- evidence compilation is replayable when authoritative observations are unchanged;
- evaluation is replayable when exact evidence inputs are unchanged.

A provider may return a different native storage locator on retry. The resulting exact ref must still identify immutable content, and review must bind the exact selected ref/content identity.

## 12.2 Retry must not overwrite history

If a retry produces a new durable artifact:

- the old immutable artifact remains historical;
- the new artifact receives its own exact identity;
- any new evaluation receives its own identity;
- no old Gate/evaluation/evidence record is rewritten.

## 12.3 Execution rerun is not evidence retry

If implementation/test execution itself reruns and produces a materially new result revision or materially new authoritative observation set, it is a new execution/evidence occurrence for applicability purposes.

Old evidence may be inherited only under an explicit applicability rule; timestamps or similarity do not make it current.

---

# 13. Interrupted-work recovery

P16 defines recovery from durable checkpoints without making checkpoint state canonical truth.

Conceptual recoverable checkpoints:

```text
C0 package exact / preflight complete
C1 implementation execution complete enough to identify result candidate
C2 authoritative observations complete
C3 EvidenceArtifact content compiled
C4 exact EvidenceInputRef(s) available
C5 exact implementation result materialized
C6 ProofEvaluation materialized
C7 independent review preparation complete
```

These labels are architecture shorthand only.

## 13.1 Recovery rule

After interruption, resume from the earliest missing/invalid checkpoint while preserving all previously validated immutable artifacts.

## 13.2 Interaction with P33

When interruption concerns P32 repository execution, P33 remains the lifecycle owner for repository-position reconciliation.

`resume_cursor` / execution navigation may identify where execution stopped, but it is not Proof evidence.

P33 must not rerun already verified implementation work merely because a later proof artifact was not materialized.

## 13.3 Recovery examples

### Result materialized, evaluation missing

Resolve the exact result/evidence refs and perform evaluation. Do not rerun implementation.

### Evidence candidate compiled, exact evidence ref missing

Retry only evidence materialization if the candidate is still bound to exact valid source/result facts.

### Observations incomplete

Resume/replay the required observation source or rerun the required probe according to the frozen package/evidence contract. Do not invent missing values.

### Only transient DTOs lost

Regenerate EvidencePlan, dependency graph, index view, or ReviewBundleView from exact durable inputs.

---

# 14. Evidence-only repair flow

Evidence-only repair is valid when the implementation result and governing semantic/package contract remain unchanged and the defect lies only in evidence compilation, transcription, binding, or materialization.

## 14.1 Preconditions

P35 or equivalent owning-layer classification has established that:

- the exact implementation result remains valid for the frozen package;
- no source implementation change is required;
- no VerificationSpec/ProofContract/package semantic change is required;
- the observed defect is in evidence production/materialization/evaluation inputs.

## 14.2 Temporal flow

```text
historical faulty EvidenceArtifact / EvidenceInputRef remains immutable
  -> recover authoritative original observations when exact/credible
     OR rerun only the required evidence-producing probe when permitted
  -> EvidenceCompiler regenerates truthful EvidenceArtifactCandidate
  -> EvidenceMaterializer creates NEW EvidenceInputRef
  -> ProofEvaluator creates NEW ProofEvaluation
  -> review bundle points to unchanged implementation result_revision/materialized_ref
     plus new evidence/evaluation identities
  -> P34 rereview occurs independently
```

## 14.3 Invariant

If the repair changes source implementation/result semantics, evidence-only repair terminates and the flow becomes a new implementation-result path.

Historical faulty evidence is never edited into truth.

---

# 15. Post-hoc review-contract delta flow

This flow handles a Gate-time request that appears to require evidence/fields not obviously present in the frozen package.

## 15.1 Sequence

```text
P34 review request
  -> ReviewContractDiffer.compare(...)
  -> one of:
       DECLARED
       EXISTING_REVIEW_ONLY
       UNDECLARED
       STRUCTURALLY_UNSATISFIABLE
```

## 15.2 DECLARED

The requirement was already frozen.

The review may resolve the existing exact evidence/ref or classify a genuine missing-evidence defect. No package mutation is needed.

## 15.3 EXISTING_REVIEW_ONLY

The frozen contract already assigns the question to CONTROL_REVIEW.

P34 may perform the review-side judgment/evidence allowed by that contract. It must not manufacture a P32 code-evidence requirement merely to mechanize the question.

## 15.4 UNDECLARED

The old package/evidence is not edited to pretend the requirement existed.

P35 classifies the root cause, for example:

- control-review defect;
- missing Verification contract;
- package-projection defect;
- upstream Authority gap.

If the requirement is genuinely necessary, the owning earlier layer produces a new immutable contract/spec/package revision and downstream applicability is reassessed.

## 15.5 STRUCTURALLY_UNSATISFIABLE

The requirement cannot be handed to the executor as evidence repair.

Examples include future-self commit identity or evidence that only P34 itself can create but was declared as deterministic P32 input.

The owning contract/review layer must be repaired.

---

# 16. Materialization failure flow

Materialization failures are separated by truth family.

## 16.1 Evidence materialization failure

Situation:

```text
valid EvidenceArtifactCandidate exists
but ArtifactStore/ExactRefResolver cannot produce reviewer-resolvable exact identity
```

Behavior:

- candidate bytes do not become SATISFIED proof merely because they exist locally;
- retry materialization may occur without rerunning implementation when inputs remain exact;
- if the environment cannot provide the required durable exact boundary, return the existing evidence/environment blocker through the owning lifecycle stage;
- P34 cannot rely on a local-only artifact.

## 16.2 Implementation result materialization failure

Situation:

```text
implementation work exists
but Execution Surface cannot return reviewer-accessible exact materialized_ref
```

Behavior:

- implementation cannot be treated as P34-reviewable completion;
- local HEAD/transcript is not a substitute;
- retry result materialization/repository publication as authorized;
- P34 does not begin from an unresolvable result.

## 16.3 Identity mismatch after materialization

If resolved bytes/result do not match the claimed digest/revision/native immutable identity:

- fail closed;
- preserve the contradictory artifacts for diagnosis;
- do not select the version that happens to make evaluation pass;
- classify root cause at P35 if already in Gate flow.

---

# 17. Cancellation semantics

Cancellation means the active owning stage stops further work; it does not manufacture a successful terminal proof state.

## 17.1 Before implementation mutation

Transient plan/preflight DTOs may be discarded. No Evidence or result truth is created.

## 17.2 After implementation mutation but before durable result materialization

Treat the work as interrupted execution. P33 may reconcile repository state later. Local edits are not proof and are not reviewable result materialization.

## 17.3 After evidence materialization but before implementation result materialization

The evidence artifact remains immutable historical data. It may be reused only if its exact subject/result applicability can later be established. Otherwise it remains unbound/supporting evidence.

## 17.4 After result materialization but before evaluation/review

The exact result persists. Later continuation should evaluate/review from exact refs rather than rerun implementation by default.

## 17.5 After ProofEvaluation but before P34

The evaluation remains immutable evidence computation. P34 may resume independently from exact refs. No Gate verdict is inferred from the interrupted state.

---

# 18. Backpressure and completeness

P16 freezes semantic behavior under slow consumers/storage without choosing concrete queue technology.

## 18.1 Observation backpressure

For required evidence:

- required records must not be silently dropped;
- required observations must not be sampled unless the frozen ProofContract explicitly defines sampling;
- producer/collector may pause, spool, or persist provider-native artifacts;
- loss of required data is missing evidence, not a successful empty result.

## 18.2 Compiler backpressure

The compiler may wait for complete observation families. It must not publish a clean partial summary merely because downstream review is waiting.

## 18.3 Materializer backpressure

Storage throttling/retry may delay reviewability but cannot relax exact-ref requirements.

## 18.4 Evaluation/review backpressure

Evaluation and review preparation operate from immutable inputs. They may be retried or resumed without mutating source proof facts.

P17 defines concrete buffering/spooling/provider timeout capabilities.

---

# 19. Persistence boundaries

P16 classifies runtime data by durability requirement.

## 19.1 Must be exact/durable when relied upon downstream

- VerificationSpec identity;
- obligation-set identity;
- canonical P31 package identity;
- exact implementation result revision/materialized_ref;
- EvidenceArtifact/EvidenceInputRef used for proof;
- ProofEvaluation;
- independent completeness-check evidence used by P34;
- formal Gate Decision and existing Project State lineage.

## 19.2 May be transient/regenerated

- EvidencePlan;
- ObservationBatch when authoritative source artifacts remain resolvable and replayable;
- EvidenceDependencyGraph;
- EvidenceArtifactCandidate before exact materialization;
- VerificationPackageProjection before canonical package materialization;
- ExpectedObligationKeySet;
- ReviewBundleView;
- derived Evidence index/navigation views.

If a transient item becomes the only surviving copy of a fact required for downstream proof, the system has failed its persistence boundary; serializing it locally does not automatically make it credible evidence.

---

# 20. R1–R5 temporal regression hooks

P20 later defines the actual verification corpus. P16 freezes the runtime behaviors that those tests must observe.

## R1 authoritative summary mismatch

```text
runner complete records
 -> compiler derives 445 PASS / 23 SKIP
 -> caller supplies 25 SKIP summary
 -> conflict rejected
 -> no EvidenceArtifact claiming 25 SKIP becomes valid proof
```

## R2 floating accepted dependency

```text
P31 input says "accepted A4"
 -> exact-ref resolution absent
 -> PackageBindingPreflight fails
 -> no P32 start
```

## R3 future-self materialization

```text
evidence contract requires artifact bytes contain commit SHA of commit containing those bytes
 -> EvidenceContractPreflight detects cycle in F1
 -> no P32 start under that contract
```

Valid replacement:

```text
artifact bytes
 -> result/evidence materializes
 -> exact ref returned externally
```

## R4 post-hoc Gate schema expansion

```text
P34 requests undeclared executor field
 -> ReviewContractDiffer = UNDECLARED
 -> old package/evidence remains immutable
 -> P35 owns classification
 -> no automatic P32 evidence repair
```

## R5 evidence-only repair

```text
same exact valid implementation result
 -> corrected evidence compilation/materialization
 -> new EvidenceInputRef
 -> new ProofEvaluation
 -> fresh P34 rereview
```

---

# 21. Runtime invariants

1. Exact trust dependencies are resolved before P32, never by the executor through floating labels.
2. P31 evidence satisfiability is checked before execution.
3. Machine-observable facts have a declared authoritative source and are compiled once.
4. Partial/missing observation is not equivalent to zero failures.
5. EvidenceArtifact content never requires its own future materialization identity.
6. EvidenceInputRef identity and implementation `materialized_ref` remain distinct.
7. The order of their materialization may vary only within the allowed partial-order topologies.
8. ProofEvaluation consumes exact evidence inputs and covers exactly the complete obligation set.
9. Review completeness traversal remains independent from generator traversal.
10. Review-time new requirements are classified as contract deltas; historical package/evidence is not mutated.
11. Retry/recovery creates new immutable artifacts when durable outputs change; history is preserved.
12. Evidence-only repair may keep an unchanged exact implementation result only when no implementation/semantic/package change is required.
13. Cancellation/interruption never implies success.
14. Backpressure may delay or pause required proof transport but may not silently drop required evidence.
15. Resume/navigation state is not Proof evidence.
16. P34 remains the sole formal Gate owner.
17. No runtime convenience crosses Primary ownership boundaries or silently authors the next substantive lifecycle occurrence.

---

# 22. P16 exit criteria

P16 is `READY` when downstream P17 can choose concrete platform adapters without inventing temporal semantics.

This design satisfies P16 when P17 can answer platform realization questions for all of the following frozen flows:

1. exact package preflight before P32;
2. authoritative observation capture and completion barriers;
3. external-evidence materialization topology;
4. evidence-inside-result materialization topology;
5. exact result materialization and reviewer resolution;
6. deterministic ProofEvaluation;
7. independent completeness/review-bundle preparation;
8. retry without history rewrite;
9. P33 recovery from missing later checkpoints;
10. evidence-only repair against unchanged result;
11. post-hoc review contract-delta handling;
12. evidence/result materialization failure;
13. cancellation at each durable boundary;
14. backpressure without silent evidence loss;
15. durable-vs-transient storage classification.

---

# 23. P16 disposition

```yaml
P16_runtime_data_flow:
  scope: aegis/verification-productization/runtime-flow

  semantic_basis: 2eb7d507098d24328b883dfa1366521390026fce
  architecture_basis: 6faa0eff7a53ccd2828eae1b0ef1aeaef1de1a83
  module_design_basis: e771cf450c9878105a28a83b6c05fb58d1d8384f
  external_current_baseline: 342d6785d8f54dd9beb2c3bb82398f29b405df2f

  p12_repair_required: false
  p14_redesign_required: false
  p15_redesign_required: false
  new_canonical_objects: NONE
  new_lifecycle_stages: NONE

  frozen_flows:
    normal_path: FROZEN
    dual_materialization_partial_order: FROZEN
    retry_recovery: FROZEN
    p33_resume_boundary: FROZEN
    evidence_only_repair: FROZEN
    post_hoc_contract_delta: FROZEN
    evidence_materialization_failure: FROZEN
    result_materialization_failure: FROZEN
    cancellation: FROZEN
    backpressure: FROZEN
    persistence_boundaries: FROZEN

  status: READY
  next_owner: aegis-architecture
  next_stage: P17_PLATFORM_CONTRACT
```

Stop after P16 materialization. Do not automatically execute P17.
