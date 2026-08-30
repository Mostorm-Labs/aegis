# Aegis Verification Productization Architecture v0.1

Status: **Draft / Proposed Authority — P14 System Architecture**

Scope: `aegis/verification-productization/architecture`

Upstream semantic basis (P21 `PASS`, accepted for downstream):

- PR #23 exact head: `1ca2f6e8845ee2d0021346bf05cfaffb6739e8e4`
- P21 durable review: `5061034069`
- `docs/verification-productization-model-v0.1.md`
- `docs/verification-productization-model-v0.1-p21-repair.md`

Current compatible Aegis contracts used as constraints:

- Aegis Methodology / lifecycle authority
- current P20 ownership by `aegis-verification`
- current P30-P36 Execution Surface semantics
- current P34 ownership by `aegis-gate-review`
- current thin `.aegis` Authority / Evidence / Gate registry responsibilities
- current single-Primary composition boundary

This architecture does **not** modify those authorities. It maps the accepted Verification Productization semantic model onto system responsibilities and failure boundaries.

Core architecture rule:

> **Automate proof machinery, not authority.**

Supporting rules:

> **Reasoning chooses what must be believed; deterministic runtime carries, checks, and evaluates the proof.**
>
> **P34 remains independently responsible for accepting the proof.**
>
> **Users manage exceptions; Aegis manages proof transport.**

---

# 1. P14 objective

Define the smallest system architecture that can implement the accepted Verification Productization model while preserving:

1. full proof depth;
2. exact Authority / Requirement coverage identity;
3. risk-proportional proof authoring;
4. deterministic profile expansion, obligation generation, evidence capture, and proof evaluation where credible;
5. one-hop verifier qualification;
6. reviewer-accessible immutable proof inputs;
7. independent P34 completeness / conformance review;
8. existing Aegis stage ownership and execution surfaces;
9. existing thin `.aegis` Project State registries;
10. a compact user surface of status, critical claims, and exceptions.

The system should reduce the current human message-queue pattern without moving semantic judgment into unreviewed automation.

---

# 2. Non-goals

P14 does not:

- redefine `VerificationSpec`, `Claim`, `ProofContract`, `CoverageBasis`, `ProofObligation`, `EvidenceArtifact`, or `ProofEvaluation` semantics;
- introduce another lifecycle P-stage;
- create a second official Gate;
- make Codex or a runner the lifecycle controller;
- let the Proof Evaluator decide P34;
- let the Obligation Generator self-certify obligation completeness;
- turn `.aegis/state.json` into a proof database;
- define final JSON Schema files, CLI flags, class names, file paths, or network APIs; those belong downstream;
- modify `aegis-verification`, `aegis-gate-review`, `aegis-implementation`, or current Project State in this architecture pass;
- begin implementation.

---

# 3. System shape

The architecture uses four logical planes plus durable artifact boundaries:

```text
                   ┌──────────────────────────────┐
                   │  REASONING CONTROL PLANE     │
                   │  P20 / CONTROL_REASONING     │
                   │                              │
Authority -------->│ Verification Authoring       │
Requirements       │ Controller                   │
                   └──────────────┬───────────────┘
                                  │ VerificationSpec candidate
                                  v
                   ┌──────────────────────────────┐
                   │ DETERMINISTIC PROOF RUNTIME  │
                   │                              │
                   │ Spec Validator               │
                   │ Profile Resolver             │
                   │ Obligation Generator         │
                   │ Proof Evaluator              │
                   │ Summary Projector            │
                   └───────┬───────────┬──────────┘
                           │           ^
               obligations │           │ exact EvidenceInputRefs
                           v           │
                   ┌──────────────────────────────┐
                   │ EXECUTION / EVIDENCE PLANE   │
                   │ P31/P32 integration          │
                   │                              │
                   │ Task Projection Adapter      │
                   │ Evidence Collector Gateway   │
                   │ Evidence Materializer        │
                   └──────────────┬───────────────┘
                                  │ immutable artifacts
                                  v
                   ┌──────────────────────────────┐
                   │ DURABLE ARTIFACT BOUNDARY    │
                   │                              │
                   │ VerificationSpec refs        │
                   │ Obligation-set refs/digests  │
                   │ EvidenceArtifact refs/digests│
                   │ ProofEvaluation refs/digests │
                   └──────────────┬───────────────┘
                                  │
                                  v
                   ┌──────────────────────────────┐
                   │ INDEPENDENT REVIEW PLANE     │
                   │ P34 / CONTROL_REVIEW         │
                   │                              │
                   │ Completeness Checker         │
                   │ Review Bundle Adapter        │
                   │ existing aegis-gate-review   │
                   └──────────────────────────────┘
```

The planes are logical responsibility boundaries, not mandatory microservices.

For v0.1, the preferred deployment shape is a **versioned deterministic proof runtime with independently invokable commands/modules**, not a fleet of always-on services. Platform realization is deferred to P17.

---

# 4. Subsystem ownership

## 4.1 Verification Authoring Controller

**Plane:** Reasoning Control Plane  
**Stage integration:** P20  
**Primary lifecycle owner:** `aegis-verification`  
**Default execution surface:** CONTROL_REASONING

Responsibilities:

- consume trusted upstream Authority / Requirements;
- pin the exact `CoverageBasis` before accepting Claim coverage;
- extract or refine Claims;
- classify risk / Criticality;
- derive minimum AssuranceClass;
- select profile + context + challenge modifiers;
- request deterministic profile expansion;
- construct the complete `VerificationSpec` candidate;
- surface semantic ambiguity as existing `BLOCKED_*` statuses;
- present compact status / critical-claim / exception views to the user.

Explicit non-ownership:

- does not execute code tests;
- does not fabricate evidence;
- does not decide P34;
- does not mark a VerificationSpec Current merely by materializing it;
- does not silently weaken a Critical Claim or assurance level.

Architecture invariant:

> The Authoring Controller may use deterministic services, but semantic decisions that require product/risk judgment remain P20 control-plane decisions.

---

## 4.2 Proof Profile Catalog

**Plane:** Deterministic Proof Runtime / versioned authority asset

Responsibilities:

- expose version-pinned base profiles: `EXAMPLE`, `PROPERTY`, `REFERENCE`, `MEASURE`, `OBSERVATION`, plus `CUSTOM` escape semantics;
- expose challenge definitions and allowed parameter contracts;
- preserve profile versions used by generated Proof Contracts;
- make profile definitions reviewer-inspectable.

Explicit non-ownership:

- does not decide which Claim is Critical;
- does not choose assurance policy by itself;
- does not mutate an already-resolved ProofContract snapshot;
- does not define Gate verdicts.

A profile definition may evolve, but existing resolved ProofContracts remain frozen to their stored snapshot.

---

## 4.3 Profile Resolver

**Plane:** Deterministic Proof Runtime

Input conceptually:

```text
Claim
+ AssuranceClass
+ ExecutionContext
+ ProofProfileRef(version)
+ Parameters
+ ChallengeSpec(s)
```

Output:

```text
Resolved ProofContract snapshot
+ resolver version/provenance
```

Responsibilities:

- expand standard profiles deterministically where the profile contract permits;
- emit the full resolved proof semantics required by the accepted model;
- fail closed on unknown profile version / unsupported required semantic field;
- never read a future profile version to reinterpret an old contract.

`CUSTOM` may bypass standard expansion but remains subject to Spec validation.

---

## 4.4 Verification Spec Validator

**Plane:** Deterministic Proof Runtime

Responsibilities:

- validate canonical VerificationSpec structure;
- validate exact CoverageBasis identity and digest presence;
- enforce Claim-to-CoverageBasis referential integrity;
- establish complete Claim coverage for `EXACT_SET` mode;
- require the mandatory coverage-completeness review obligation for `REVIEW_DECLARED` mode;
- enforce one current ProofContract per Claim in a spec revision;
- enforce Critical Claim / assurance / QualificationSpec structural requirements;
- reject silent assurance downgrade without required risk-acceptance reference;
- enforce version / compatibility rules.

Explicit non-ownership:

- structural validation does not make semantic ambiguity true;
- it cannot turn unresolved Criticality into `ORDINARY`;
- it cannot promote the spec to Current Authority.

---

## 4.5 VerificationSpec Materializer

**Plane:** Durable Artifact Boundary

Responsibilities:

- materialize an immutable VerificationSpec revision at a reviewer-resolvable durable ref;
- compute/preserve exact content identity/digest;
- return the ref/digest used by downstream obligation generation and task packaging;
- preserve historical revisions.

Explicit non-ownership:

- materialization is not Authority promotion;
- it does not update `.aegis/authorities.json` unless a later authorized governance operation explicitly does so.

---

## 4.6 Obligation Generator

**Plane:** Deterministic Proof Runtime

Input:

```text
exact VerificationSpec digest
+ exact CoverageBasis digest
+ generator version
```

Output:

```text
complete ProofObligation set
+ obligation_ids
+ obligation_count
+ obligation_set_digest
+ generator identity/version
```

Responsibilities:

- derive the complete executable/reviewable obligation set from the exact resolved ProofContracts;
- create the mandatory `REVIEW_REQUIRED` coverage obligation for `REVIEW_DECLARED` mode;
- produce stable/replayable obligation identity;
- include deterministic and review-required obligations without filtering out failures or unevaluated items;
- fail closed on unknown semantic input.

Explicit non-ownership:

- cannot mark obligations SATISFIED;
- cannot determine P34 completeness by self-assertion;
- cannot omit review-required obligations to produce a clean result.

---

## 4.7 P31 Task Projection Adapter

**Plane:** Execution / Evidence Plane  
**Lifecycle ownership remains:** `aegis-implementation` for P31

Responsibilities:

- project an accepted verification design into compact P31 references;
- carry exact Authority / VerificationSpec / Claim / obligation references and digests;
- preserve execution scope and non-goals;
- avoid copying the full ProofContract prose into every package;
- preserve existing `task_anchor` / `resume_cursor` execution-position semantics where repository execution is involved.

Architecture invariant:

> Projection compresses transport; it never creates new verification semantics.

The adapter is not a new lifecycle owner and does not authorize P32 by itself.

---

## 4.8 Evidence Collector Gateway

**Plane:** Execution / Evidence Plane  
**Primary operational stage:** P32 / P36 as applicable

Responsibilities:

Capture machine-verifiable facts from the actual runner / CI / code-execution environment where available:

- source revision;
- result revision;
- reviewer-accessible `materialized_ref`;
- actual command/probe identity;
- exit code;
- test counts/results;
- corpus / fixture identity and digest;
- artifact URI / digest;
- CI run identity;
- tool/version;
- environment fingerprint;
- metric values;
- threshold inputs/results;
- Claim / obligation binding.

It may also accept explicitly labeled executor observations when facts cannot be captured automatically, but deterministic facts take precedence over conflicting executor prose.

Explicit non-ownership:

- does not decide semantic credibility of an oracle;
- does not decide risk acceptance;
- does not issue a Gate verdict.

---

## 4.9 Evidence Materializer

**Plane:** Durable Artifact Boundary

Responsibilities:

- create immutable/replay-safe EvidenceArtifact materialization;
- compute/preserve exact digest or explicit immutable identity;
- ensure the ref is reviewer-resolvable at the required review boundary;
- return an exact `EvidenceInputRef` for evaluation;
- preserve append-only historical evidence behavior;
- optionally register the artifact in existing thin `.aegis/evidence.json` without moving detailed proof data into Project State.

Failure invariant:

> A local-only or mutable/unpinned artifact cannot become a deterministic SATISFIED proof input.

---

## 4.10 Proof Evaluator

**Plane:** Deterministic Proof Runtime

Exact inputs:

```text
VerificationSpec digest
+ CoverageBasis digest
+ complete obligation-set identity / generator version
+ canonical EvidenceInputRef set
+ evaluator version
```

Output:

```text
immutable ProofEvaluation
```

Responsibilities:

- evaluate deterministic obligations against exact evidence;
- retain review-required obligations as `EXCEPTION`;
- classify missing/invalid required deterministic evidence as `UNSATISFIED`;
- aggregate Claim and overall counts using the accepted precedence;
- preserve exact input identities and version provenance;
- never emit an official Gate verdict.

Explicit non-ownership:

- cannot reinterpret Authority;
- cannot self-resolve semantic/manual/oracle-independence exceptions;
- cannot mark P34 PASS.

---

## 4.11 Verification Summary Projector

**Plane:** Deterministic Proof Runtime / user-view projection

Responsibilities:

- derive the compact user-facing verification readiness view;
- reuse existing Aegis workflow status vocabulary;
- expose `Status + Critical Claims + Exceptions` by default;
- expand to Claim -> Proof -> Pass Rule when requested;
- fail closed according to the accepted F1 mapping.

It MUST NOT render `READY` when:

- `UNSATISFIED > 0`;
- unresolved mandatory `EXCEPTION > 0`;
- coverage / obligation-set / evidence identity is incomplete;
- an Authority / criticality / assurance decision is unresolved.

`READY` means ready for the next authorized lifecycle action, not P34 PASS.

---

## 4.12 Independent Obligation Completeness Checker

**Plane:** Independent Review Plane  
**Invoked for:** P34 CONTROL_REVIEW

This subsystem exists specifically to close the correlated-failure problem identified by P21.

Responsibilities:

- consume the exact VerificationSpec independently from the Obligation Generator output;
- derive the expected obligation-key/completeness structure from canonical resolved ProofContract semantics;
- confirm CoverageBasis integrity;
- compare expected obligation identity against the generated obligation set;
- verify evaluation-set equality against the complete set;
- produce review evidence for P34.

Independence rule:

> The Completeness Checker MUST NOT use the Obligation Generator's produced obligation list as its source of expected truth.

Allowed shared dependencies:

- canonical schema parser;
- canonical digest/canonicalization utility;
- stable semantic enum definitions.

Forbidden shared dependency for completeness proof:

- calling `ObligationGenerator.generate()` or equivalent generation algorithm and comparing its output to itself.

Preferred v0.1 strategy:

- implement a deliberately smaller review-side traversal that derives required obligation keys directly from the resolved ProofContract sections and CoverageBasis rules;
- version the checker independently;
- record its version and result in reviewer evidence.

For `REVIEW_DECLARED` CoverageBasis, the checker also confirms that the required coverage-completeness review obligation exists; the human/control reviewer still owns the actual completeness judgment against the pinned upstream Authority.

---

## 4.13 Review Bundle Adapter

**Plane:** Independent Review Plane

Responsibilities:

Assemble reviewer navigation over exact durable artifacts:

```text
Current/intended Authority refs
VerificationSpec ref/digest
CoverageBasis identity
obligation_set ref/digest/generator version
ProofEvaluation ref/digest/evaluator version
EvidenceInputRefs
implementation result_revision
implementation materialized_ref
Completeness Checker result/version
mandatory EXCEPTION list
scope/conformance metadata
```

The adapter may reduce navigation cost but cannot resolve exceptions or issue a Gate verdict.

---

## 4.14 Existing P34 Gate Review

**Plane:** Independent Review Plane  
**Primary owner:** `aegis-gate-review`  
**Execution surface:** CONTROL_REVIEW

P34 remains outside the Proof Runtime.

It must independently:

1. resolve the exact implementation `materialized_ref`;
2. confirm intended Authority / VerificationSpec identity;
3. establish CoverageBasis integrity;
4. establish obligation-set completeness through independently credible checking;
5. establish ProofEvaluation set equality and provenance;
6. establish exact-result Authority/scope conformance;
7. inspect mandatory EXCEPTIONs;
8. confirm no UNSATISFIED obligations;
9. issue the existing official Gate verdict.

ProofEvaluation and Completeness Checker results are evidence inputs to P34, not replacements for P34.

---

# 5. Dependency direction

Allowed dependency direction:

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
P31 Task Projection Adapter
      ↓
P32/P36 execution environments
      ↓
Evidence Collector Gateway
      ↓
Evidence Materializer
      ↓
Proof Evaluator
      ↓
Verification Summary Projector
      ↓
Review Bundle Adapter
      ↓
Independent Completeness Checker + P34 Gate Review
```

Review-side dependency intentionally also reaches back to the exact VerificationSpec directly:

```text
VerificationSpec ------------------------------┐
                                               v
                                  Completeness Checker
Obligation Generator output ------------------> compare
```

This second path is mandatory. It prevents generator output from being its own completeness oracle.

Forbidden dependency directions:

- Proof Evaluator -> mutate VerificationSpec;
- Evidence Collector -> lower assurance;
- Summary Projector -> issue Gate verdict;
- Obligation Generator -> certify P34 completeness;
- P31/P32 -> redefine Claim/ProofContract semantics;
- `.aegis/evidence.json` -> become detailed proof truth;
- `resume_cursor` -> become proof evidence.

---

# 6. Canonical truth vs derived/runtime state

## Canonical semantic truth

- accepted upstream Authority / Requirement snapshot;
- VerificationSpec revision;
- CoverageBasis;
- Claim;
- resolved ProofContract.

## Derived deterministic artifacts

- ProofObligation set;
- obligation-set digest;
- ProofEvaluation;
- VerificationSummary.

## Evidence truth

- immutable EvidenceArtifact;
- exact EvidenceInputRef;
- independent completeness-check evidence;
- P34 reviewer evidence.

## Navigation / execution state only

- task package transport metadata;
- task anchor;
- resume cursor;
- transient authoring session;
- UI expanded/collapsed state.

Architecture invariant:

> Navigation state never upgrades into Authority or Evidence merely because automation uses it.

---

# 7. Process and execution boundaries

## 7.1 Reasoning process

Semantic authoring runs in the control reasoning environment.

It may invoke deterministic validation/resolution helpers, but the reasoning agent remains responsible for semantic ambiguity and risk judgment within P20 authority.

## 7.2 Deterministic proof runtime

The Profile Resolver, Spec Validator, Obligation Generator, Proof Evaluator, and Summary Projector should be stateless/pure where practical.

They must be reproducible from exact versioned inputs.

They may execute as library calls, CLI commands, CI jobs, or equivalent platform invocations; P17 decides concrete realization.

## 7.3 Execution process

Evidence collection occurs where the actual command / test / probe executes so it can capture machine facts without manual retranscription.

The executor cannot self-certify semantic credibility merely because it produced the artifact.

## 7.4 Review process

The Completeness Checker and P34 review execute on the review side, logically separated from executor assertions.

The checker must maintain the independence constraint from the Obligation Generator.

P34 must independently resolve durable refs rather than relying on local executor state.

---

# 8. Failure domains and fail-closed behavior

## 8.1 Authoring / Authority failure

Examples:

- stale/unresolvable upstream Authority;
- unknown complete Requirement universe;
- unresolved Criticality;
- unapproved assurance downgrade.

Owning status:

- `BLOCKED_AUTHORITY`, `BLOCKED_MISSING_INPUT`, or `BLOCKED_UNRESOLVED_DECISION` according to cause.

No downstream obligation generation should proceed from an invalid canonical spec.

## 8.2 Profile / schema failure

Examples:

- unknown profile version;
- unsupported required semantic field;
- invalid local references;
- missing required QualificationSpec.

Behavior:

- fail closed before durable readiness;
- do not guess defaults that alter proof meaning.

## 8.3 Obligation generation failure

Examples:

- invalid VerificationSpec digest;
- generator cannot interpret required semantics;
- missing required REVIEW_DECLARED coverage obligation;
- incomplete generated set.

Behavior:

- do not emit a clean obligation manifest;
- surface the owning blocker;
- completeness checker later independently detects omitted obligations if generation nevertheless materializes an incomplete set.

## 8.4 Evidence collection/materialization failure

Examples:

- command result unavailable;
- artifact local-only;
- mutable ref without digest;
- missing result revision/materialized_ref.

Owning status:

- normally `BLOCKED_EVIDENCE`, or `BLOCKED_ENVIRONMENT` when the required environment cannot produce credible evidence.

## 8.5 Evaluation failure

Examples:

- evidence input identity mismatch;
- missing required evidence;
- threshold failure;
- evaluator version unavailable.

Behavior:

- missing/invalid required evidence -> `UNSATISFIED` where the semantic contract permits evaluation;
- evaluator/runtime unavailable -> existing environment/evidence blocker;
- never infer SATISFIED from absence of failure data.

## 8.6 Review completeness failure

Examples:

- completeness checker cannot establish expected set;
- generated set differs from expected set;
- evaluation set differs from complete obligation set;
- checker independence cannot be established.

Behavior:

- P34 cannot PASS;
- classify as evidence/spec/authority defect according to root cause;
- never waive completeness merely because ProofEvaluation reports zero exceptions.

---

# 9. Artifact and storage boundaries

v0.1 deliberately separates detailed verification artifacts from Project State registries.

```text
Detailed immutable artifact
        ↓ referenced by
thin .aegis registry entry
```

Existing responsibilities remain:

- `.aegis/authorities.json` -> Authority registry;
- `.aegis/evidence.json` -> thin evidence index;
- `.aegis/gates.json` -> official Gate decisions;
- `.aegis/state.json` -> generated cache, not proof database.

Detailed VerificationSpec / obligation-set / EvidenceArtifact / ProofEvaluation artifacts may be stored in repository paths, CI artifacts, content-addressed storage, or equivalent reviewer-resolvable durable systems.

P17 will define required portability / URI / platform capability behavior.

Architecture requirement:

> Any artifact required for independent review must have an exact identity and reviewer-resolvable durable reference at the relevant review boundary.

---

# 10. Stage / plane integration

## P20 — Verification Design

Owns semantic authoring through the Verification Authoring Controller.

Target result:

```text
trusted exact VerificationSpec
+ resolved ProofContracts
+ materialized complete obligation-set identity
```

P20 continues to preserve the original proof chain inside resolved contracts.

## P30/P31 — Planning / Task Packaging

Consume exact verification refs through the P31 Task Projection Adapter.

Task packages transport Claim/obligation identity; they do not restate proof semantics.

## P32 — Implementation / execution

Executes authorized obligations and produces machine facts/artifacts.

The Evidence Collector Gateway should remove manual evidence transcription wherever facts are machine-observable.

## P33 — Resume

Existing Task Anchor / Execution Cursor semantics remain unchanged.

Resume metadata is not proof evidence.

## P34 — Gate Review

Consumes the exact review bundle plus independent completeness evidence.

P34 remains the only official implementation Gate verdict owner.

## P35/P36 — Defect / reverification

P35 routes failures to the owning layer.

P36 re-executes affected obligations and regressions and emits new immutable evidence/evaluation artifacts rather than rewriting historical proof.

---

# 11. Product interaction consequence

The architecture supports the intended user experience:

Normal path:

```text
Verification: READY
Critical Claims: 3
Satisfied: 3
Exceptions: 0
```

The user does not manually shuttle:

- commit SHAs already machine-known;
- exit codes;
- test counts;
- corpus digests;
- artifact digests;
- obligation IDs;
- ProofEvaluation summaries.

Those flow through deterministic artifacts.

The user/control reviewer is pulled in for:

- unresolved semantic decisions;
- risk acceptance;
- oracle independence judgment;
- manual observation credibility;
- REVIEW_DECLARED completeness;
- mandatory EXCEPTION resolution;
- unexpected scope/Authority drift.

This implements the product rule:

> **Human attention is spent on exceptions, not proof plumbing.**

---

# 12. Automation boundary

Aegis may automate deterministic transitions and artifact transport, but this P14 architecture does not authorize a hidden monolithic workflow owner.

Allowed automation examples:

- profile expansion;
- spec validation;
- obligation generation;
- evidence capture;
- digest/materialization;
- evaluation;
- summary projection;
- handoff field population;
- review bundle assembly.

Not automatically collapsed:

- P20 semantic judgment;
- P21 Authority acceptance;
- P30/P31 authorization;
- P34 Gate judgment;
- P35 defect ownership classification.

Existing single-Primary composition semantics remain intact.

A future user experience may make `继续 Aegis` sufficient to route to the next owner, but routing convenience does not erase lifecycle ownership.

---

# 13. Security / trust boundaries

The system has three important trust boundaries.

## 13.1 Semantic authority boundary

Reasoning/runtime cannot silently modify accepted upstream semantic truth.

Any changed Requirement universe or materially changed Claim/ProofContract semantics creates a new revision and appropriate governance/review path.

## 13.2 Executor evidence boundary

Executor-produced claims are not automatically trusted evidence.

Machine-captured facts and reviewer-resolvable immutable artifacts are preferred.

## 13.3 Reviewer independence boundary

The same correlated component cannot both:

1. define/omit the generated obligation set; and
2. serve as the only proof that the set is complete.

Likewise, ProofEvaluator output is not a Gate verdict.

---

# 14. P14 architectural invariants

1. **Stage Ownership != Proof Runtime execution.**
2. **Proof Runtime != Gate authority.**
3. **Generated obligation set != completeness oracle.**
4. **Executor prose != deterministic evidence when machine facts exist.**
5. **Mutable/local artifact != exact review input.**
6. **VerificationSummary READY != P34 PASS.**
7. **Navigation state != Authority/Evidence.**
8. **Profile version change != retroactive ProofContract change.**
9. **Changed evidence != mutation of historical ProofEvaluation.**
10. **Changed Requirement universe != reuse of old coverage result.**
11. **Project State thin registries remain thin in v0.1.**
12. **Single-Primary lifecycle ownership remains unchanged.**

---

# 15. Architecture decisions intentionally deferred

P14 freezes system responsibility, not all implementation detail.

Defer to P15 Module Design:

- exact module/package boundaries;
- internal interfaces;
- canonicalization utility ownership;
- independent checker rule representation;
- review-bundle internal structure.

Defer to P16 Runtime Data Flow:

- exact temporal happy/error/retry/recovery flows;
- evidence arrival ordering;
- reevaluation triggers;
- cancellation/backpressure behavior.

Defer to P17 Platform Contract:

- CLI vs library invocation per environment;
- ChatGPT/Codex/CI/GitHub adapter contracts;
- durable URI schemes;
- filesystem/repository/CI artifact capability differences;
- authentication / reviewer-access behavior.

Defer to P18 Engineering / Optimization:

- runtime latency targets;
- artifact size budgets;
- caching;
- incremental reevaluation;
- large-corpus performance;
- observability/rollback metrics.

Defer to P20 Verification Design:

- the proof contracts that verify this architecture itself.

---

# 16. P14 exit criteria

P14 is `READY` when downstream design can answer all of the following without inventing semantic truth:

1. Which subsystem owns semantic authoring? **Verification Authoring Controller under P20.**
2. Which subsystem expands profiles? **Profile Resolver.**
3. Which subsystem validates exact Requirement coverage? **Verification Spec Validator using CoverageBasis.**
4. Which subsystem creates the executable/reviewable obligation set? **Obligation Generator.**
5. Which subsystem captures execution facts? **Evidence Collector Gateway.**
6. Which subsystem guarantees reviewer-resolvable immutable evidence inputs? **Evidence Materializer.**
7. Which subsystem computes SATISFIED/EXCEPTION/UNSATISFIED? **Proof Evaluator.**
8. Which subsystem produces compact readiness UX? **Verification Summary Projector.**
9. Which subsystem independently checks obligation completeness? **Independent Obligation Completeness Checker.**
10. Who issues the formal Gate verdict? **Existing P34 / aegis-gate-review only.**
11. Where do detailed proof artifacts live? **Outside thin Project State registries, behind durable exact refs.**
12. Does any automation change stage ownership? **No.**

---

# 17. P14 disposition

**P14 System Architecture: READY — Draft / Proposed Architecture Authority**

The architecture is sufficiently explicit to proceed to P15 Module Design without modifying implementation or Current Aegis runtime behavior.

Next earliest untrusted layer for this scope:

**P15 Module Design**

P15 should refine these logical subsystems into concrete independently understandable modules and stable interfaces, with special focus on:

- canonical shared model/parser vs independent completeness logic;
- versioned Profile Catalog representation;
- deterministic Obligation Generator contract;
- Evidence Collector / Materializer provider boundary;
- Proof Evaluator inputs/outputs;
- review bundle and Completeness Checker interfaces;
- strict prohibition on shared generator logic becoming the completeness oracle.
