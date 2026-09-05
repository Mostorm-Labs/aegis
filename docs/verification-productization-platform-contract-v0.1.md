# Aegis Verification Productization v0.1 — P17 Platform Contract

Status: **Draft / Proposed Authority — P17 Platform Contract**

Scope: `aegis/verification-productization/platform-contract`

Exact upstream basis:

- Verification Productization semantic head after repository restack: `12c968c5c481ad671ce33bcfa088ba8a2fca0f43`
- semantic rebase-only P21 recertification: review `5121012716` — `PASS / ACCEPTED_FOR_DOWNSTREAM`
- P14 architecture reconciliation after restack: `d9c8f6ac5db4359400fae06e76c51c65bd059bfc`
- P15 module-design result after restack: `665292dcfd7781935243369ee9f676c320f2878a`
- P16 runtime-flow result / exact P17 resume basis: `708cf09c01effbcc63c65d45b9b4a67b7a8fc8db`
- Evidence Contract Churn P21 reconciliation: review `5119525139`
- Evidence Contract Churn P22 five-axis review: review `5119537168`
- fresh external Current baseline: `main@342d6785d8f54dd9beb2c3bb82398f29b405df2f`

The P21 recertification established that the semantic artifacts and P14/P15/P16 architecture artifacts are byte-identical to their pre-restack versions. Old SHA references embedded in those historical documents remain historical metadata; this P17 contract uses the exact restacked basis above.

Retained Current external contracts:

- Control Plane `CanonicalRef`, `TrustedBasis`, `VerificationBoundImplementationPackage`, `StageOccurrence`, and existing status semantics;
- Execution Surface v0.2 `Stage Ownership != Execution Surface`, `Task Anchor != Execution Cursor`, exact result materialization, and independent P34 review;
- repository-identity platform contract: `Repository Identity != Task Anchor != Execution Cursor`, explicit GitHub repository namespace, same-repository package materialization, and fail-closed wrong-repository behavior;
- Project State v0.5 immutable Authority / Evidence / Gate / Integration lineage;
- P34 as sole formal Gate owner, with P35 owning-layer classification and P36 repair/reverification.

This P17 design maps the P15/P16 Proof Runtime ports and temporal rules onto concrete execution/provider surfaces. It does **not** change Proof Plane semantics, lifecycle ownership, Gate authority, package semantics, or Current repository behavior by itself.

---

# 1. P17 objective

Freeze the platform contract that allows one exact Proof Plane design to move safely across:

```text
CONTROL_REASONING
CODE_EXECUTION
CI / provider execution
GitHub repository/materialization
local filesystem/worktree staging
CONTROL_REVIEW
CODE_REVERIFY
```

without turning platform convenience into new semantic truth.

P17 must answer five questions precisely:

1. Which environment invokes deterministic proof modules as a library, CLI, or remote/provider adapter?
2. Which provider is authoritative for each machine-observable fact and how is completion established?
3. Which storage/materialization forms are exact and reviewer-resolvable, and which are only transient staging?
4. How are repository identity, result identity, evidence identity, authentication, and reviewer access kept separate?
5. What must fail closed when a platform cannot satisfy the frozen P15/P16 contract?

Core rule:

> **A platform adapter may translate representation and transport, but it may not translate away identity, provenance, completeness, or lifecycle ownership.**

---

# 2. Explicit non-goals

P17 does not:

- add a new lifecycle stage, execution surface, Gate, or Primary owner;
- create a hidden workflow daemon or make Codex / GitHub Actions / ChatGPT the Aegis lifecycle controller;
- create new canonical Proof Plane or Control Plane aggregates;
- change `VerificationSpec`, `ProofObligation`, `EvidenceArtifact`, `EvidenceInputRef`, `ProofEvaluation`, `CanonicalRef`, or `VerificationBoundImplementationPackage` semantics;
- change repository-identity Authority or allow repository inference from ambient cwd/session context;
- let a PR URL, branch name, local path, CI green badge, log transcript, or assistant/executor message substitute for exact identity;
- require all evidence to be stored in Git or all evidence to be stored in CI;
- require public artifact access; reviewer-resolvable private access is sufficient;
- define performance/latency/size budgets, cache policy, parallelism, or retention-cost optimization; P18 would own those if later required;
- define the P20 proof contracts that test this platform contract;
- authorize P30/P31/P32 implementation.

---

# 3. Existing Aegis surfaces vs platform providers

P17 preserves the existing execution-surface vocabulary.

```text
CONTROL_REASONING  -> reasoning / authority / package-control surface
CODE_EXECUTION     -> repository-heavy implementation execution surface
CONTROL_REVIEW     -> independent P34/P35 control review surface
CODE_REVERIFY      -> repair/reverification execution surface
```

GitHub, GitHub Actions, local git, local filesystem, command runners, and future artifact stores are **providers/adapters**, not new Aegis execution surfaces.

A provider may be used by more than one surface. That does not transfer stage ownership.

Examples:

- ChatGPT on `CONTROL_REASONING` may resolve GitHub refs and materialize architecture/package documents through a GitHub connector;
- Codex on `CODE_EXECUTION` may use local git/filesystem/process execution plus GitHub remote materialization;
- GitHub Actions may produce authoritative CI observations and external artifacts while P32 remains owned by `aegis-implementation`;
- ChatGPT on `CONTROL_REVIEW` may independently read GitHub commits, workflow runs, evidence artifacts, and reviews while P34 remains owned by `aegis-gate-review`.

`Provider execution != lifecycle ownership`.

---

# 4. Invocation contract: library core, CLI edge, connector control

## 4.1 Canonical deterministic module boundary

The P15 modules remain the canonical deterministic implementation boundary:

```text
proof-domain
proof-spec
proof-obligations
proof-package
proof-ports
proof-evidence
proof-evaluation
proof-review
```

Their library/API contracts own parsing, canonicalization, validation, generation, compilation, evaluation, and review-support semantics.

A CLI or remote adapter must call those contracts rather than reimplementing proof rules in shell snippets, prompts, workflow YAML, or provider-specific JSON transformations.

## 4.2 CODE_EXECUTION / CODE_REVERIFY invocation

Repository-heavy local execution uses a **structured CLI adapter over the deterministic library**.

The exact executable/subcommand names are implementation details for P30/P32, but the platform contract is normative:

- input is exact refs plus structured DTOs/files, not copied semantic prose;
- output is structured UTF-8 JSON/JSONL or equivalent machine-readable data;
- trust-critical identity fields are explicit;
- deterministic command exit/nonzero state is captured as an observation, not interpreted by shell prose;
- stdout/stderr may be retained for diagnostics but is not the sole durable proof object;
- human-readable summaries are derived views only.

A direct in-process library call is allowed for unit/integration tests and tightly coupled runtime components, provided it produces the same semantic output as the CLI adapter for the same exact inputs.

## 4.3 CI invocation

CI uses the same deterministic contracts through either:

- the same structured CLI adapter; or
- a provider-native runner wrapper that is mechanically equivalent and emits the same Observation / Evidence DTO semantics.

Workflow YAML may select commands, inputs, and artifact transport, but it must not independently encode Claim pass rules, duplicate test totals, or redefine obligation semantics.

## 4.4 CONTROL_REASONING / CONTROL_REVIEW invocation

Control surfaces do not assume direct access to the local proof-runtime process.

They interact through:

- exact repository/provider refs;
- durable materialized artifacts;
- provider APIs/connectors;
- structured P31/P32/P34 handoff fields.

A control-surface assistant message is never the authoritative machine observation merely because it paraphrases a provider result.

---

# 5. Port-to-platform binding

P17 binds the P15 ports as follows.

| P15 port | v0.1 platform adapters | Required property |
|---|---|---|
| `ObservationSourcePort` | local command/test runner; GitHub Actions job/report adapter; explicit external provider adapter; reviewer observation adapter for review-only evidence | producer identity + completion barrier + structured facts |
| `ArtifactStorePort` | exact GitHub repository blob at exact revision; GitHub Actions artifact when retention/access contract is sufficient; explicit external immutable/content-addressed store | immutable identity + reviewer-resolvable locator + content identity |
| `ExactRefResolverPort` | GitHub repository/commit/blob/PR resolver; GitHub Actions run/artifact resolver; explicit external provider resolver | no mutable alias accepted without exact identity |
| `ResultMaterializationPort` | GitHub remote commit/branch/PR result adapter for repository-backed work | exact `result_revision` + reviewer-resolvable `materialized_ref` |

Local filesystem and worktree paths are staging mechanisms only. They do not implement a reviewer-resolvable `ArtifactStorePort` by themselves.

---

# 6. Platform capability preflight

Before a phase relies on a provider, the active surface must establish that the provider exposes the capabilities required by the frozen package/evidence contract.

Capability discovery is runtime/preflight state only; it is not a canonical object.

Relevant capabilities include:

```text
repository_read
repository_write
git_fetch
git_push
local_process_execute
local_filesystem_read
local_filesystem_write
ci_run_read
ci_job_read
ci_artifact_read
ci_artifact_write_or_upload
review_comment_or_review_read
reviewer_identity_read
external_artifact_read
external_artifact_write
```

Rules:

1. missing capability never weakens the ProofContract or package;
2. lack of a write/materialization capability blocks the dependent phase rather than falling back to local-only evidence;
3. lack of reviewer read access means the artifact is not reviewer-resolvable at that review boundary;
4. credentials/tokens are runtime configuration and MUST NOT be serialized into Proof, package, evidence, review, or Project State artifacts;
5. capability checks occur before irreversible/mutating provider operations.

No new public blocker vocabulary is introduced. The owning phase maps capability failure to existing statuses such as `BLOCKED_ENVIRONMENT`, `BLOCKED_EVIDENCE`, `BLOCKED_MISSING_INPUT`, `BLOCKED_AUTHORITY`, or existing repository-identity blockers according to root cause.

---

# 7. ObservationSourcePort platform contracts

## 7.1 Local CODE_EXECUTION runner

A local runner may be authoritative for facts produced by the command/process it directly executes.

Minimum observation provenance:

```text
repository identity when repository-backed
package/task binding
actual starting/result working revision when relevant
command/probe identity
runner/tool identity + version when available
process exit/result code
structured result/report location
fixture/corpus identity where required
environment fingerprint fields required by ProofContract
producer completion state
```

### Completion barrier

A local process is complete only after:

1. the process has terminated;
2. required structured result/report files have been closed/finalized;
3. the runner can establish that the result set is complete for the command invocation.

A truncated process, interrupted pipe, partially written report, or missing end condition is incomplete evidence, not a successful zero-failure run.

## 7.2 GitHub Actions CI adapter

GitHub Actions may be the authoritative producer for CI-native facts.

Minimum provider binding when applicable:

```text
repository.full_name
workflow identity
run_id
run_attempt
job_id
trigger/source revision
terminal run/job state
job conclusion
structured report/artifact identity
```

### Completion barrier

Required CI observations are complete only after the applicable run/job is in a terminal provider state and all evidence artifacts required by the EvidencePlan are available.

`queued`, `in_progress`, cancelled/incomplete upload, unavailable structured report, or a job whose expected matrix children have not all reached terminal state cannot be compiled as a clean completed result.

A green workflow badge alone is navigation. Evidence compilation consumes the exact run/job/report facts declared by the EvidencePlan.

## 7.3 Structured report preference

For tests/metrics:

1. prefer raw machine-readable case/metric records;
2. otherwise use a provider-native authoritative machine summary;
3. use human/log parsing only when the ProofContract explicitly permits it and the parser/version/provenance are recorded;
4. never retype totals manually into a second evidence JSON.

## 7.4 External provider adapter

A non-GitHub provider is allowed only when the frozen evidence contract names or permits it and the adapter can provide:

- provider-qualified identity;
- terminal/completeness semantics;
- immutable or digest-pinned result identity;
- reviewer-resolvable access.

Ambient URLs or copied text are not sufficient.

## 7.5 Reviewer observations

A reviewer/manual observation can satisfy only a `REVIEW_REQUIRED` or otherwise explicitly review-owned obligation.

A mutable GitHub comment/review URL alone is not an immutable EvidenceInputRef. If reviewer text itself must become durable proof input, materialize a snapshot with exact content digest and bind the provider review/comment identity as provenance.

---

# 8. ArtifactStorePort platform contracts

P17 supports three durability profiles without requiring one universal store.

## 8.1 Profile A — repository artifact at exact revision

Use when evidence bytes naturally belong in a repository result/history.

Reviewer locator conceptually contains:

```yaml
provider: github
repository:
  full_name: <owner/repo>
revision: <exact 40-char commit>
path: <repository-relative path>
content_digest: sha256:<digest>
review_ref: https://github.com/<owner>/<repo>/blob/<revision>/<path>
```

Rules:

- repository-relative path is portable; local absolute path is not;
- exact revision is required;
- branch name alone is not evidence identity;
- file content digest is verified before deterministic use;
- the evidence bytes MUST NOT contain the future commit identity needed to identify themselves.

This is P16's evidence-inside-result topology when the exact file ref becomes known only after result commit materialization.

## 8.2 Profile B — GitHub Actions artifact

Use for generated/large/external evidence when provider retention and reviewer access are sufficient for the governing proof/review horizon.

Locator conceptually contains:

```yaml
provider: github_actions
repository:
  full_name: <owner/repo>
run_id: <native id>
run_attempt: <integer>
artifact_id: <native artifact id>
artifact_name: <name>
member_path: <path inside artifact when applicable>
content_digest: sha256:<digest of exact EvidenceArtifact bytes>
review_ref: <stable run/artifact locator capable of resolving current download access>
```

Rules:

1. a temporary signed download URL is not the durable `review_ref` because it expires;
2. store provider-native run/artifact identity from which authorized access can be regenerated;
3. content digest pins the exact EvidenceArtifact bytes even when the provider packages them in a ZIP/archive;
4. retention/expiry must be compatible with the required review/replay window;
5. if the provider artifact expires before the required trust horizon, it cannot remain the sole durable EvidenceInputRef and must be promoted/materialized to another acceptable store before downstream trust relies on it.

P17 defines the correctness boundary, not the retention duration or cost policy.

## 8.3 Profile C — external immutable/content-addressed store

A future or project-specific external store may satisfy `ArtifactStorePort` when it provides:

- stable provider-qualified locator;
- immutable/version-pinned content;
- exact digest/native immutable identity;
- intended reviewer read access;
- retention compatible with governing proof/replay requirements.

No external store is required for the first implementation.

## 8.4 Local filesystem staging

Local files may stage:

- ObservationBatch;
- EvidencePlan;
- EvidenceArtifactCandidate;
- compiled EvidenceArtifact bytes awaiting materialization;
- temporary resolver/download content.

But:

```text
/Users/.../evidence.json
/tmp/.../report.xml
worktree-relative uncommitted file
```

is never by itself an exact reviewer-resolvable evidence identity.

If local bytes are the only surviving copy of a required fact, the persistence boundary has failed.

---

# 9. ExactRefResolverPort and GitHub identity

## 9.1 Repository identity first

For repository-backed work, resolution order remains:

```text
repository.provider/full_name
  -> package materialization
  -> package_ref
  -> task_anchor / resume_cursor
  -> result/evidence refs
```

No bare SHA is resolved before the repository namespace is established.

Cross-repository fallback is forbidden.

## 9.2 Mutable navigation vs exact identity

The following may be useful navigation but are not exact by themselves:

```text
branch name
PR URL
workflow name
latest run
artifact name
local path
```

They become safe trust-boundary navigation only when paired with the exact identity required by the owning contract.

Examples:

```text
PR URL + exact result_revision
workflow + exact run_id/run_attempt/job_id
artifact name + exact artifact_id + content digest
repository path + exact commit + content digest
```

## 9.3 Branch/PR movement

After package/evidence/result freeze, later branch or PR movement does not retarget the historical exact ref.

A reviewer resolving a PR must verify the stored exact result revision rather than assuming the PR's current head is still the reviewed result.

## 9.4 Signed/ephemeral URLs

Ephemeral signed URLs are access tokens, not durable identity.

Persist provider-native stable IDs plus exact digest/native immutable identity; generate signed access only at read time.

---

# 10. ResultMaterializationPort — GitHub repository profile

Repository-backed P32/P33/P36 materialization uses the declared GitHub repository.

Required return remains:

```yaml
repository:
  provider: github
  full_name: <owner/repo>
package_ref: <exact package>
result_revision: <exact commit revision>
materialized_ref: <reviewer-accessible remote ref>
return_surface: CONTROL_REVIEW
```

Rules:

1. result commit must be resolvable in the declared repository;
2. `materialized_ref` may be an exact commit URL or a remote branch/PR locator, but P34 must independently resolve it and confirm the returned `result_revision` is present/applicable;
3. prefer an exact commit URL as the immutable review target when the provider supports it; branch/PR remains navigation/context;
4. local-only commit SHA is insufficient;
5. push/fetch failure or unavailable reviewer access blocks review readiness;
6. materializing a result does not materialize every EvidenceArtifact automatically;
7. EvidenceInputRef and result materialization remain separate identities.

---

# 11. P16 materialization topologies on concrete platforms

P17 realizes P16's partial-order rules without collapsing identities.

## 11.1 Repository-contained evidence

```text
CODE_EXECUTION
 -> run/probe
 -> local ObservationBatch
 -> compile EvidenceArtifact bytes
 -> include bytes in result candidate
 -> git commit/push result
 -> exact result_revision/materialized_ref
 -> resolve exact repository blob at result_revision
 -> EvidenceInputRef
 -> ProofEvaluation
 -> P34
```

The evidence file never contains the future commit SHA needed to identify itself.

## 11.2 External evidence available before result materialization

```text
CODE_EXECUTION/provider
 -> authoritative observations
 -> compile EvidenceArtifact
 -> external ArtifactStorePort
 -> EvidenceInputRef
 -> result materialization
 -> evaluation/review consume both exact identities
```

## 11.3 Provider-triggered CI external evidence

Some CI providers require an already-materialized repository revision before they can execute. This is a concrete realization of P16's **partial order**, not a collapse of evidence/result identity:

```text
result content
 -> exact remote result_revision
 -> CI run bound to that exact revision
 -> authoritative CI observations
 -> compile/materialize external EvidenceArtifact
 -> EvidenceInputRef
 -> ProofEvaluation
 -> P34
```

This profile is valid only because:

- result materialization does not depend on the future EvidenceInputRef;
- EvidenceArtifact content does not contain its own future materialization identity;
- CI observations are explicitly bound to the exact result revision;
- P34 receives result and evidence identities separately.

A CI run against a different revision is not applicable merely because it is newer or green.

## 11.4 Evidence-only repair

To preserve an unchanged exact implementation result, an evidence-only repair must use an evidence materialization boundary that does not require rewriting the implementation result commit.

Valid pattern:

```text
same exact result_revision/materialized_ref
 -> rerun/recover authoritative evidence producer as allowed
 -> new external EvidenceArtifact
 -> new EvidenceInputRef
 -> new ProofEvaluation
 -> fresh P34 rereview
```

If the selected repository-contained evidence topology requires changing bytes inside the result commit, then the repository result identity necessarily changes. It must not be reported as the same exact result. Use an external evidence store/profile when the owning repair classification requires the implementation result to remain unchanged.

---

# 12. P31 platform satisfiability checks

Before P32 authorization, `EvidenceContractPreflight` plus platform capability preflight must establish that every required fact has a realizable provider/store path.

For each required evidence family, P31 must be able to answer conceptually:

```text
Who produces it?
What exact execution/result does it bind to?
What marks the producer complete?
How is the EvidenceArtifact materialized?
What exact identity pins its bytes?
How does the intended reviewer resolve it?
Can the identity exist at the phase where the contract requires it?
```

Reject before P32 when:

- only a local path is available for a required durable artifact;
- the selected CI/provider cannot expose terminal/completeness state;
- a required artifact can only be addressed by a future self-dependent ref;
- provider retention cannot satisfy an explicit required review horizon and no promotion store exists;
- intended reviewers lack required read capability and no permitted alternative exists;
- repository/provider namespace is ambiguous;
- evidence requires a P34 judgment before it can be produced;
- a mutable alias is the only available trust-boundary identity.

The executor does not choose a weaker provider after P31 freeze.

---

# 13. P32 / P33 / P36 surface contract

## 13.1 Entry

Repository-backed CODE_EXECUTION / CODE_REVERIFY first performs Current repository-identity preflight, then task-anchor/cursor reconciliation, then proof-provider capability checks.

## 13.2 Execution binding

The platform adapter supplies the P16 execution binding from exact package/repository facts. It may include runtime/provider IDs, but those do not become Authority.

## 13.3 Structured return

Execution returns navigation plus exact materialization refs, not copied proof summaries.

Conceptually:

```yaml
repository: <declared repository identity>
package_ref: <exact package>
actual_starting_revision: <exact revision>
result_revision: <exact implementation result>
materialized_ref: <reviewer-accessible result ref>
evidence_input_refs:
  - <exact EvidenceInputRef or exact durable locator to be compiled/resolved by owning flow>
provider_run_refs:
  - <exact CI/provider run identity where applicable>
return_surface: CONTROL_REVIEW
```

Do not add independent handoff fields such as manually typed `tests_passed`, `tests_skipped`, or derived proof totals when those values belong in EvidenceArtifact / ProofEvaluation.

## 13.4 P33 resume

P33 may reuse already-valid durable evidence/materialization checkpoints when applicability still holds.

A resume cursor/local transcript does not replace exact provider evidence.

If only a later provider/materialization checkpoint is missing, resume from that missing checkpoint instead of rerunning implementation solely for convenience.

---

# 14. CONTROL_REVIEW / P34 resolution contract

Before relying on a review bundle, CONTROL_REVIEW independently resolves:

1. accepted Authority/Verification basis;
2. package identity;
3. declared repository identity;
4. exact result revision and result materialization;
5. every deterministic EvidenceInputRef used by ProofEvaluation;
6. provider run identities needed to establish observation applicability/completion;
7. ProofEvaluation exact identity;
8. independent completeness-check evidence;
9. mandatory review exceptions;
10. review-contract diff result.

A review bundle may contain clickable URLs and provider navigation, but exact identity/digest fields control trust.

If a provider object is no longer readable at review time, P34 cannot infer its prior content from copied narrative. The owning blocker is `BLOCKED_EVIDENCE` unless another earlier layer is the actual cause.

---

# 15. Authentication and reviewer-access contract

## 15.1 Reviewer-resolvable does not mean public

An exact ref is reviewer-resolvable when the intended independent review surface can retrieve and verify the exact object using authorized platform access at the review boundary.

Private GitHub repositories and private CI artifacts are valid when the reviewer has the required read capability.

## 15.2 Credential separation

Credentials, API tokens, SSH keys, cookies, and signed download URLs are runtime secrets/configuration.

They MUST NOT be stored in:

- VerificationSpec;
- P31 package;
- EvidenceArtifact content unless the evidence subject is explicitly a credential-security test with redaction rules;
- EvidenceInputRef;
- ProofEvaluation;
- review bundle;
- `.aegis` registries;
- durable handoff comments.

## 15.3 Access loss

If a previously valid provider ref becomes inaccessible before the required Gate/replay boundary:

- do not treat copied metadata as equivalent evidence;
- attempt only contract-permitted re-resolution/promotion/re-materialization;
- otherwise fail closed.

Authorization failure is not permission to switch to another repository, another artifact with the same name, or a local cached copy whose identity cannot be independently established.

---

# 16. Provider/applicability binding

Provider results must be bound to the exact subject they prove.

Examples:

- GitHub Actions run -> exact repository + triggering/source/result revision + run attempt;
- local test report -> exact execution binding + command/probe + result working/revision identity when required;
- repository blob -> exact repository + commit + path + content digest;
- external artifact -> provider namespace + immutable/version ID + digest + subject binding.

Timestamps, recency, branch position, or artifact names do not establish applicability.

A newer CI run for another revision cannot supersede the exact run selected by the evidence contract without a new evidence/evaluation occurrence.

---

# 17. Failure and fail-closed mapping

P17 introduces no new public lifecycle status. Representative platform failures map as follows:

| Failure | Owning behavior |
|---|---|
| wrong/ambiguous repository namespace | existing repository-identity fail-closed behavior, normally `BLOCKED_REPOSITORY_IDENTITY` |
| required local/CI execution capability unavailable | `BLOCKED_ENVIRONMENT` |
| authoritative provider incomplete/terminal state unavailable | missing/incomplete evidence; normally `BLOCKED_EVIDENCE` |
| required structured report missing | `BLOCKED_EVIDENCE` unless environment cannot produce it, then `BLOCKED_ENVIRONMENT` |
| local-only required artifact | `BLOCKED_EVIDENCE` |
| artifact ref mutable/unpinned | `BLOCKED_EVIDENCE` |
| artifact expired/inaccessible before required review | `BLOCKED_EVIDENCE` |
| exact Authority/package ref cannot be resolved | owning Authority/input blocker, not executor guess |
| result push/materialization unavailable | `BLOCKED_EVIDENCE`; P34 not ready |
| CI evidence bound to wrong result revision | `BLOCKED_EVIDENCE` / applicability failure |
| future-self evidence ref cycle | pre-P32 contract blocker; do not execute |
| P34 asks undeclared new executor field | `ReviewContractDiffer`; P35 classifies owning earlier layer |

A platform adapter must preserve the earliest owning cause rather than collapsing every provider failure into implementation failure.

---

# 18. Portability and serialization

## 18.1 Portable paths

Repository artifacts use repository-relative paths. Local absolute paths are diagnostic/navigation only.

## 18.2 Provider-qualified native IDs

Native provider IDs are always interpreted inside their provider/repository namespace. `artifact_id=123` or `run_id=456` without provider/repository context is not portable identity.

## 18.3 Canonical vs transient encoding

Canonical Proof/Control objects retain their governing canonicalization/digest rules.

Transient platform DTOs may use ordinary structured JSON/JSONL, but any field promoted into exact EvidenceArtifact/CanonicalRef identity must be normalized under the owning semantic contract before digesting.

## 18.4 Versioning

Adapters record provider/tool/parser versions when required for replay or qualification.

A provider API version change does not silently change Proof semantics. If adapter behavior changes materially, verifier qualification/P20 determines whether a new adapter/evaluator version is required.

---

# 19. Process / thread / lifecycle boundary

The v0.1 platform contract requires no persistent central service.

Allowed deployment:

```text
CONTROL_REASONING
  -> durable package/ref handoff
CODE_EXECUTION / CI
  -> deterministic proof-runtime CLI/library invocations
GitHub / artifact provider
  -> immutable refs
CONTROL_REVIEW
  -> independent resolution
```

Deterministic modules may run in one process or multiple processes. Shared memory is never required across lifecycle surfaces.

Cross-process recovery uses exact durable refs/checkpoints, not in-memory coordinator state.

This preserves the current human/Control Plane architecture while enabling later automation without requiring a new orchestration service merely to close Evidence Contract Churn.

---

# 20. Concrete adapter responsibilities

## 20.1 ChatGPT / CONTROL_REASONING adapter

May:

- read Current Authority and exact repository refs;
- create/review P20/P31/control artifacts through connected providers;
- resolve exact GitHub objects;
- assemble deterministic navigation from existing exact refs;
- route lifecycle work.

Must not:

- claim local command execution it did not perform;
- manually retype machine totals as authoritative evidence;
- treat conversation text as TrustedBasis/Evidence;
- infer repository/package identity from ambient project context when exact refs disagree.

## 20.2 Codex / CODE_EXECUTION adapter

May:

- execute authorized repository commands;
- invoke proof-runtime CLI/library adapters;
- capture local structured observations;
- stage/compile evidence;
- commit/push authorized result/evidence according to the package;
- return exact result/provider refs.

Must:

- perform repository identity preflight first;
- preserve unrelated dirty work;
- fail closed on package/anchor/cursor/provider mismatch;
- not redesign missing ProofContract/package semantics;
- not promote local paths/transcripts into Gate evidence.

## 20.3 GitHub Actions adapter

May:

- run exact-revision CI/probes;
- produce structured reports;
- expose run/job terminal state;
- upload provider artifacts;
- provide immutable/native IDs used by evidence materialization.

Must not:

- define lifecycle Authority;
- convert green CI into P34 PASS;
- silently select `latest` run for a frozen evidence binding;
- omit failed/missing matrix children from a supposedly complete summary.

## 20.4 GitHub repository adapter

Owns platform realization for:

- repository namespace;
- exact commits/blobs;
- package/result materialization;
- branch/PR navigation;
- reviewer-resolvable repository artifacts.

A PR/branch is navigation unless paired with exact selected identity.

---

# 21. P20 verification handoff requirements

P17 does not execute P20, but the targeted P20 repair must verify the platform contracts needed to close the Evidence Contract Churn incident family.

At minimum preserve/cover:

### R1 — authoritative fact mismatch

- local/CI structured producer reports the authoritative exact facts;
- a conflicting manually supplied total cannot become valid EvidenceArtifact truth.

### R2 — floating accepted dependency

- package/control input such as `accepted A4` without exact CanonicalRef fails before CODE_EXECUTION.

### R3 — self-referential materialization

- repository artifact requiring its own future containing commit SHA is rejected before P32;
- exact repository blob identity is resolved after commit/materialization instead.

### R4 — post-hoc schema expansion

- CONTROL_REVIEW cannot convert an undeclared Gate request into a historical P32 requirement;
- platform adapter does not synthesize missing fields to satisfy the reviewer.

### R5 — evidence-only repair

- unchanged exact implementation result can receive a new external EvidenceInputRef / ProofEvaluation without source implementation mutation when the owning classification permits it.

Additional platform regressions required by P17:

1. local-only evidence cannot satisfy reviewer-resolvable evidence requirements;
2. PR/branch movement cannot retarget an exact reviewed result;
3. CI run must be terminal/complete and bound to the exact result revision;
4. `latest run` / artifact-name-only lookup cannot cross the trust boundary;
5. expired/inaccessible required CI artifact fails closed unless contract-permitted durable promotion exists;
6. temporary signed URL is not stored as durable artifact identity;
7. wrong-repository SHA/artifact fallback is rejected;
8. missing reviewer read capability blocks evidence readiness;
9. incomplete/missing matrix job cannot be summarized as zero failures;
10. control/executor prose cannot override deterministic provider facts.

Verifier qualification should include negative/mutant cases for these provider failures.

---

# 22. P18 determination

P17 discovered no new engineering/performance requirement that must be frozen before verification.

The current incident is about trust correctness, identity, provenance, completeness, materialization, and access semantics.

Therefore:

```yaml
P18_required_now: false
reason: no new measurable latency/throughput/size/resource target is needed to define correctness
```

Future evidence-volume, artifact-retention-cost, caching, incremental reevaluation, or large-corpus performance work may enter P18 when an actual workload/metric/target exists.

This is a routing disposition, not execution of P18.

---

# 23. P17 exit criteria

P17 is `READY` when downstream P20 can write executable proof contracts without inventing platform semantics.

Required frozen outcomes:

1. existing Aegis execution surfaces preserved; providers are not new owners/surfaces;
2. deterministic library core + structured CLI/provider adapter split defined;
3. local/Codex and GitHub Actions ObservationSource completion rules defined;
4. exact repository/blob, CI artifact, and optional external-store materialization profiles defined;
5. local filesystem explicitly classified as transient staging, not review evidence;
6. GitHub repository identity and cross-repository fail-closed rules retained;
7. mutable navigation refs separated from exact identity;
8. result materialization and EvidenceInputRef remain distinct;
9. temporary signed URLs and credentials excluded from durable identity;
10. reviewer-resolvable private access semantics defined;
11. provider-triggered CI exact-result applicability defined;
12. evidence-only repair platform path defined without falsely preserving a changed result commit;
13. platform capability preflight fails closed before execution/materialization;
14. P34 independent resolution remains mandatory;
15. no new canonical object, lifecycle stage, Gate, or hidden workflow owner introduced.

---

# 24. P17 disposition

```yaml
P17_platform_contract:
  scope: aegis/verification-productization/platform-contract

  semantic_basis: 12c968c5c481ad671ce33bcfa088ba8a2fca0f43
  semantic_p21_recertification: 5121012716
  architecture_basis: d9c8f6ac5db4359400fae06e76c51c65bd059bfc
  module_design_basis: 665292dcfd7781935243369ee9f676c320f2878a
  runtime_flow_basis: 708cf09c01effbcc63c65d45b9b4a67b7a8fc8db
  external_current_baseline: 342d6785d8f54dd9beb2c3bb82398f29b405df2f

  new_canonical_objects: NONE
  new_lifecycle_stages: NONE
  new_execution_surfaces: NONE
  new_gate_owner: NONE
  hidden_daemon_required: false

  platform_contracts:
    deterministic_library_core: FROZEN
    structured_cli_edge: FROZEN
    control_connector_boundary: FROZEN
    local_runner_observation: FROZEN
    github_actions_observation: FROZEN
    provider_completion_barriers: FROZEN
    repository_artifact_profile: FROZEN
    github_actions_artifact_profile: FROZEN
    local_filesystem_transient_only: FROZEN
    exact_ref_resolution: FROZEN
    repository_identity_preflight: RETAINED
    result_materialization: FROZEN
    reviewer_access: FROZEN
    authentication_separation: FROZEN
    signed_url_non_identity: FROZEN
    provider_result_applicability: FROZEN
    evidence_only_repair_surface: FROZEN
    p34_independent_resolution: RETAINED

  p12_repair_required: false
  p14_redesign_required: false
  p15_redesign_required: false
  p16_redesign_required: false
  p18_required_now: false

  status: READY
  next_owner: aegis-verification
  next_stage: P20_TARGETED_EVIDENCE_CONTRACT_REGRESSION_DESIGN
```

Stop after P17 materialization. Do not automatically execute P20, P30, P31, P32, or P34.
