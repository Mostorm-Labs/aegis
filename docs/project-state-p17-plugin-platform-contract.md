# Aegis Project State — P17 Plugin Platform Contract

Status: **P17 Platform Contract Candidate**

Scope: `aegis/project-state`

Triggering finding: `P22-F2 = MISSING_CONTRACT / SPEC_DEFECT`

Repository basis: `main@3a2607220cd875dc66857b334dcfbd2c763e7c7d`

P12 semantic basis candidate: `777e1e8a9652e2cbf220d234798641d65dc9b0c9`

P13 operation basis candidate: `b742ebb9f27520a595b2e73370f42157e28ea72e`

Repaired P14 architecture basis candidate: `cc768db72450b2c9d75a3d9650d447cdbd10048b`

Repaired P15 module-design basis candidate: `ffa79084c10211668ced1ae6801e238c789ffeb7`

P16 interaction/evidence-flow basis candidate: `40e094b62f9f3150516f4631ec9df98e6729d258`

Current Authority under repair: `aegis-project-state-v0.5`

This artifact defines the platform contracts between Aegis Skills, connected execution surfaces such as GitHub and Codex, repository durable state, and deterministic validator/CI support. It preserves the repaired Plugin-native product form. It does **not** introduce an Aegis runtime, daemon, agent loop, custom harness, background worker, repository state service, or transaction service.

It does not assign a replacement Project State version, does not modify `.aegis/*`, does not implement code, and does not authorize merge, release, rollout, or the real PR #82 historical reconciliation.

---

## 1. P17 objective

P17 separates common Aegis semantics from platform realization.

The core question is:

> What must remain true regardless of whether Aegis is reading or writing through GitHub, handing implementation to Codex, validating through repository tooling, or resuming in a later ChatGPT session?

The platform contract must prevent a platform shortcut from silently redefining Project State semantics.

The canonical separation is:

```text
COMMON SEMANTICS
  Authority / Gate / Integration meaning
  P12 Gate Decision Binding
  P13 legal transition vocabulary
  historical immutability
  fail-closed ambiguity

            ↓ realized through

PLATFORM SURFACES
  ChatGPT Aegis Skills
  GitHub connector / repository APIs
  Codex execution surface
  Git repository history
  deterministic validator / CI
```

Platform capability differences may change **how** evidence is fetched or a change is written.

They must never change **what the evidence means**.

---

## 2. Platform-independent semantic contract

The following rules are independent of tool, provider, client, connector, operating system, repository host, or execution environment.

### 2.1 Gate Decision Binding

For the future replacement schema:

```text
Integration Gate Decision Binding
  = Bound(exact immutable Gate Decision)
  | Absent(no_applicable_integration_gate_decision)
```

`Absent` is explicit historical truth.

The following are never equivalent to `Absent`:

```text
field missing
lookup returned no result
connector timed out
permission denied
result pagination incomplete
repository ref unavailable
Gate Decision ID unresolved
Current Authority unknown
```

### 2.2 Historical immutability

Once an Integration is finalized as `integrated`, the historical identity-bearing facts are immutable:

```text
id
kind
ref
target_ref
integrated_revision
gate_decision_binding
```

No platform may expose a convenience write that permits these facts to be silently rewritten.

### 2.3 Occurrence-time truth

The historical binding belongs to the actual repository occurrence.

A current/future PASS may affect current actionability but cannot be rebound to an older occurrence merely because it is easier for a platform implementation.

### 2.4 Authority separation

```text
repository occurrence
!= Gate acceptance
!= Authority acceptance
!= CI success
!= tool execution success
```

Every platform adapter must preserve these distinctions.

### 2.5 P13 operations are semantic verbs

```text
O1 Register Awaiting Integration
O2 Rebind Awaiting Integration
O3 Finalize Integration Occurrence
O4 Reconcile Historical Integration Occurrence
O5 Close Unmerged Candidate
O6 Append Corroborating Integration Evidence
```

These names classify legal state changes.

They do not require a shared runtime API, RPC protocol, worker, dispatcher, or Python executor.

---

## 3. Platform actor model

P17 recognizes six platform actors.

```text
A. ChatGPT / Aegis Skill control plane
B. GitHub read/write surface
C. Codex execution surface
D. Git repository durable state
E. deterministic repository validator / CLI
F. GitHub Actions / CI host
```

The same physical platform may realize more than one mechanical capability, but semantic ownership does not merge merely because one product exposes multiple APIs.

---

## 4. Contract A — ChatGPT / Aegis Skill control plane

### 4.1 Role

The Aegis Skill layer owns control-plane interpretation.

For Project State work it is responsible for:

- identifying the correct repository and scope;
- reading fresh durable evidence through available connected surfaces;
- interpreting Current Authority and historical Authority lineage;
- applying P12/P13 semantics;
- distinguishing occurrence, conformance, applicability, and actionability;
- deciding whether the intended change is semantically legal;
- classifying the change using P13 conceptual vocabulary;
- constructing an explicit mutation or handoff;
- failing closed when the basis is stale, ambiguous, contradictory, or unavailable.

### 4.2 Inputs

The Skill may consume:

```text
user intent
Current Authority artifacts
historical Authority / Gate decisions
authored .aegis manifests
repository refs / commits / PR state
durable review/comment IDs
validator / CI outputs
Codex result revisions / execution returns
```

Not all inputs have equal authority.

The Skill must preserve source role when interpreting them.

### 4.3 Outputs

A Project State control-plane output may be one of:

```text
read-only diagnosis
support_return
BLOCKED / unresolved result
explicit repository mutation specification
Codex execution handoff
post-execution reconciliation conclusion
next-stage routing recommendation
```

### 4.4 Forbidden promotion

The Skill must not convert these mechanical facts into semantic truth without the required Authority/evidence basis:

```text
GitHub write succeeded -> Authority accepted
Codex says tests pass -> P34 PASS
CI green -> Gate Decision PASS
tool search returned no decision -> Absent
repository merged -> merge was Gate-authorized
```

### 4.5 Session boundary

A ChatGPT conversation is not durable project state.

A later session must resume from durable refs and fresh repository state when correctness depends on them.

Conversation history may help locate those refs, but it cannot override contradictory durable repository evidence.

---

## 5. Contract B — GitHub read surface

### 5.1 Role

GitHub read capability supplies durable repository evidence.

Typical evidence includes:

```text
branch HEAD
commit SHA and parents
pull request metadata
merge status
review/comment IDs
file content at exact ref
workflow run/result metadata
repository diff
```

### 5.2 Exact-ref preference

When a semantic conclusion depends on historical identity, Aegis should prefer immutable or exact references where available:

```text
commit SHA
review/comment ID
PR number + exact head SHA
file content at exact commit
workflow run ID
```

A moving branch name is useful for fresh state but is not itself historical immutability.

### 5.3 Negative-read contract

A negative or failed GitHub read has only tool-level meaning unless the relevant Authority explicitly defines otherwise.

```text
404 / empty search / timeout / permission failure
-> NOT_FOUND_OR_UNRESOLVED_AT_TOOL_SURFACE
```

It must not be interpreted as:

```text
no Gate Decision existed
no Authority existed
no Integration occurred
Absent binding proven
```

### 5.4 Pagination / partial-result safety

If a platform read can return only a page, subset, filtered set, or otherwise incomplete result, Aegis must not derive global historical absence from that subset.

If completeness is required for the semantic claim and cannot be established:

```text
BLOCKED_ON_EVIDENCE_COMPLETENESS
```

### 5.5 Fresh-state contract

Before any write that depends on a prior basis, GitHub must be used to re-read the relevant moving ref or state whenever the platform supports it.

If the ref has changed:

```text
STALE_BASIS
-> prior mutation specification is invalidated
-> recompute from fresh evidence
```

---

## 6. Contract C — GitHub write surface

### 6.1 Role

GitHub write capability executes an already-authorized repository mutation.

It may:

- create/update files;
- create commits;
- advance a working branch;
- open/update PRs when authorized;
- return durable commit/PR refs.

It does not own the semantic decision that made the mutation legal.

### 6.2 Write precondition

A Project State write must have an explicit control-plane basis containing, at minimum where applicable:

```text
repository
working ref/branch
expected basis ref/head
semantic operation classification
exact intended authored-state change
required durable evidence refs
stop boundary / forbidden actions
```

For historical `Absent`, the write specification must not be created until the accepted proof contract establishes:

```text
Occurrence Basis
+
Absence Basis
```

### 6.3 Compare-and-fail-closed preference

When the GitHub platform supports an expected current blob SHA, expected branch head, or equivalent optimistic-concurrency guard, Project State writes should use it.

Conceptually:

```text
write only if current basis == expected basis
```

If the platform does not provide an atomic expected-head mutation for the exact action, Aegis compensates by:

1. fresh-reading immediately before write;
2. minimizing the time between read and write;
3. validating the returned commit parent/ref after write;
4. blocking if the result was based on unexpected concurrent state.

### 6.4 Write result contract

A successful write result proves only:

```text
the platform accepted a repository mutation
and returned a durable result ref
```

It does **not** prove:

```text
semantic correctness
Authority acceptance
verification sufficiency
Gate PASS
release readiness
```

### 6.5 Uncertain write outcome

If the write call times out or returns an ambiguous outcome:

```text
DO NOT BLINDLY RETRY
```

Required recovery:

```text
fresh-read target branch/files
-> determine whether intended change materialized
-> if exact intended state exists: capture durable ref and continue verification
-> if absent: retry only from fresh basis
-> if partial/conflicting: BLOCKED for repair/reconciliation
```

### 6.6 Multi-file writes

If a Project State change spans multiple authored files, the preferred realization is one coherent repository commit.

If the available GitHub surface can only issue sequential file writes/commits, intermediate commits are repository facts but are not automatically accepted Project State.

Acceptance occurs only after the complete intended state is materialized and verified.

No custom Aegis transaction server is introduced to hide this platform limitation.

---

## 7. Contract D — Codex execution surface

### 7.1 Role

Codex is an execution plane, not Aegis semantic Authority.

Codex is appropriate when an implementation package requires repository-side edits, tests, migration work, or other code-oriented execution that is better performed in a development workspace.

For the current Project State repair line, Codex is not required merely to reason about `Bound` versus `Absent`.

### 7.2 Handoff contract

A Codex handoff must be explicit enough that Codex does not need to invent Aegis lifecycle semantics.

Where applicable it should carry:

```text
repository
execution branch/worktree
stage/package identity
task anchor / expected starting revision
exact Authority/design basis refs
allowed files/scope
required implementation outcome
required verification commands/evidence
forbidden actions
stop boundary
expected return fields
```

### 7.3 Codex authority boundary

Codex may determine implementation-local facts such as:

```text
files changed
commands executed
tests passed/failed
result revision
observed repository conflicts
```

Codex must not self-promote those facts into lifecycle conclusions such as:

```text
P21 Authority accepted
P34 Gate PASS
release authorized
historical Absent proven
retroactive Gate authorization allowed
```

Those conclusions return to the owning Aegis stage.

### 7.4 Codex return contract

A useful execution return should include enough durable information for Aegis to reconcile fresh state, for example:

```text
actual starting revision
result revision
changed-file summary
verification commands + results
known deviations/blockers
whether requested scope was fully completed
```

A prose claim without a result revision or inspectable repository state is weaker evidence than a durable repository result and should not replace fresh-state verification.

### 7.5 Interrupted execution

If Codex is interrupted, a future Aegis/Codex continuation must inspect the actual workspace/repository state.

It must not assume that the last conversationally reported step is the durable stopping point.

### 7.6 No hidden cross-Primary chaining

Codex completion of implementation does not authorize Aegis to silently execute a different Primary's substantive stage.

The existing lifecycle ownership and user-turn boundaries remain unchanged.

---

## 8. Contract E — repository durable state

### 8.1 Canonical persistence

Canonical Project State is repository-authored state, including the applicable `.aegis/*.json` manifests and accepted Authority artifacts.

For Project State manifests:

```text
.aegis/project.json
.aegis/authorities.json
.aegis/gates.json
.aegis/evidence.json
.aegis/integrations.json
```

`state.json` remains generated/read-model state and cannot override authored manifests or Authority.

### 8.2 Commit identity

A repository commit SHA is the preferred durable identity of an exact materialized candidate.

A branch name identifies a moving line of work; it is not a substitute for the exact candidate SHA in Authority, verification, or handoff contracts.

### 8.3 History preservation

Repository history may record mistakes, superseded candidates, or blocked attempts.

P17 prefers supersession over history erasure:

```text
old candidate remains durable
new accepted/replacement candidate explicitly supersedes it
```

This is especially important for the repaired P14/P15 line, where prior runtime-oriented candidates remain historical artifacts but are no longer valid downstream design basis.

### 8.4 No private Plugin state database

Aegis Skills must not depend on an undisclosed parallel persistence store to establish Project State truth.

Conversation/session memory can assist continuity but cannot become authoritative project persistence.

---

## 9. Contract F — deterministic repository validator / CLI

### 9.1 Role

The existing Project State tooling may validate deterministic properties such as:

```text
schema shape
schema-version consistency
cross references
state recomputation
state drift
same-version historical immutability
migration equivalence
```

The current repository already exercises validation/recompute/check/transition behavior through its Project State CI workflow.

### 9.2 Input contract

The validator consumes repository/manifests as data.

It must not require access to private conversational state to reproduce a deterministic result.

### 9.3 Output contract

Validator output may establish:

```text
VALID / INVALID
mechanical invariant violation
computed state projection
transition mismatch
migration mismatch
```

Validator output must not establish by itself:

```text
historical governance absence
Authority acceptance
Gate Decision authority
release authorization
P34 PASS
```

### 9.4 `Absent` contract

A validator may check that an already-authored `Absent` record:

- has the legal variant shape;
- uses an allowed reason;
- appears only in a legal status;
- contains required durable references if the accepted schema requires them;
- preserves historical immutability across snapshots.

It must not derive `Absent` by searching external systems or noticing that no decision ID was found.

### 9.5 Determinism

Given the same exact repository inputs, deterministic validation should produce the same semantic validation result independent of ChatGPT session, user identity, or connector availability.

If a validation rule requires external non-durable lookup, it is not a deterministic repository invariant and must not be hidden inside the validator.

---

## 10. Contract G — GitHub Actions / CI host

### 10.1 Role

CI hosts deterministic checks against a repository candidate.

The current workflow validates schemas, examples, root manifests, generated state, transition history, Skill materialization, and regression suites.

CI is therefore a **verification host**, not an Aegis lifecycle owner.

### 10.2 CI PASS meaning

```text
CI PASS
= configured mechanical checks succeeded on the tested revision
```

It does not mean:

```text
Authority accepted
Gate PASS exists
integration is authorized
historical Absent is proven
release is approved
```

### 10.3 CI FAIL meaning

```text
CI FAIL
= at least one configured mechanical check failed or infrastructure prevented success
```

A failing CI job may be evidence of an implementation/manifest defect.

Infrastructure failure must not be silently reclassified as semantic invalidity without inspection.

### 10.4 Exact-source contract

When CI evidence is used downstream, Aegis should bind the evidence to the exact tested revision/run where available.

A green run for another commit is not evidence for the current candidate unless equivalence is independently established.

---

## 11. Skill materialization contract

The repository currently contains Project State Skill surfaces under both:

```text
skillset/skills/aegis-project-state/**
skills/aegis-project-state/**
```

P17 does not invent a new source-of-truth rule beyond existing repository materialization contracts.

It does require this invariant:

```text
materialized Plugin Skill semantics
must not contradict the accepted source Skill semantics
```

If the repository's distribution/materialization tooling designates one side as generated, implementation must follow that existing contract rather than editing both independently in a way that can drift.

The Project State CI already includes Skill validation/regression surfaces; future implementation should preserve that pattern.

---

## 12. Read capability degradation contract

Aegis must continue safely when a preferred read capability is unavailable.

### 12.1 Safe degradation

If an exact convenient API is unavailable but equivalent durable evidence can be obtained through another approved connected surface, Aegis may use the alternative.

Example:

```text
preferred PR metadata API unavailable
but exact merge commit + PR durable discussion are available
-> continue if the required semantic facts remain provable
```

### 12.2 Unsafe degradation

Aegis must block rather than weaken the semantic standard when the missing capability prevents proof.

Example:

```text
cannot establish complete occurrence-time Gate lineage
-> cannot prove Absent
-> BLOCKED
```

A platform limitation cannot redefine `unknown` as `Absent`.

---

## 13. Write capability degradation contract

### 13.1 Direct GitHub write unavailable

If ChatGPT cannot perform the exact required repository write through GitHub, it may produce an explicit Codex handoff or user-executable patch/command plan when that is the authorized execution path.

The semantic decision remains unchanged.

### 13.2 Expected-head guard unavailable

If the write API lacks an atomic expected-head guard:

```text
fresh read immediately before write
+
post-write parent/result verification
```

is required as compensation.

If concurrent drift cannot be excluded, the result is fail-closed rather than silently accepted.

### 13.3 Multi-file atomic update unavailable

The platform may realize a coherent logical mutation through multiple commits only if the lifecycle treats intermediate states as unaccepted and the final exact candidate is explicitly verified.

No platform limitation permits a partially valid authored Project State to be treated as accepted current truth.

---

## 14. Error taxonomy across platforms

P17 standardizes error meaning so platform-specific failures do not leak into semantic interpretation.

### `READ_UNRESOLVED`

Required evidence could not be read completely.

Effect:

```text
no semantic negative inference
```

### `STALE_BASIS`

Moving repository/Authority state changed after the mutation basis was formed.

Effect:

```text
invalidate prior mutation specification
fresh-reconcile
```

### `WRITE_UNCERTAIN`

Execution surface did not conclusively report whether mutation materialized.

Effect:

```text
fresh-read before any retry
```

### `WRITE_CONFLICT`

Expected file/ref no longer matches.

Effect:

```text
no last-write-wins
fresh-reconcile
```

### `MECHANICAL_INVALID`

Schema/validator/CI establishes an invalid materialized state.

Effect:

```text
candidate not accepted
```

### `SEMANTIC_AMBIGUITY`

Evidence is insufficient to establish the intended Authority/Binding meaning.

Effect:

```text
BLOCKED
no write
```

### `AUTHORITY_CONTRADICTION`

Fresh durable Authority contradicts the design/mutation basis.

Effect:

```text
return to the owning Authority/governance layer
```

---

## 15. Exact-source / provenance contract

Every downstream-critical fact should carry enough provenance to distinguish exact evidence from conversational restatement.

Examples:

```text
Authority artifact -> exact commit/ref
Gate Decision -> durable decision/review ID + exact candidate
repository occurrence -> PR/merge ref + integrated revision
Codex result -> result revision
CI -> workflow run + tested revision
Project State candidate -> exact commit SHA
```

A human-readable summary is useful, but the durable identifier is what allows a fresh session to re-establish the basis.

---

## 16. PR #82 platform contract

The real PR #82 reconciliation remains deferred until replacement Authority and downstream verification are accepted.

When it is eventually authorized, the platform boundary must be:

```text
Aegis control plane
  establishes O4 semantic legality
  establishes accepted Occurrence Basis + Absence Basis
        ↓
GitHub/Codex execution surface
  writes exact authored Project State change
        ↓
repository commit
  records durable candidate
        ↓
validator/CI
  verifies schema/invariants/projection
        ↓
Aegis/lifecycle owner
  reconciles exact result and determines acceptance
```

No platform may collapse this into:

```text
PR merged -> therefore Gate authorized
```

or:

```text
no Gate found by connector -> therefore Absent
```

or:

```text
CI green -> therefore historical absence proven
```

For PR #82 the target historical meaning remains:

```text
int-pr82
status = integrated
integrated_revision = 3a2607220cd875dc66857b334dcfbd2c763e7c7d
gate_decision_binding = Absent(no_applicable_integration_gate_decision)
historical_conformance = nonconforming
```

only after the required lifecycle preconditions are satisfied.

---

## 17. Platform non-goals

This P17 explicitly does not define or require:

```text
Aegis daemon
Aegis local agent runtime
repository event listener
background reconciliation worker
custom message queue
custom transaction server
custom state database
custom RPC protocol between ChatGPT and Codex
mandatory new Python adapter layer
```

It also does not require that GitHub and Codex expose identical APIs.

P17 requires **semantic equivalence of boundaries**, not API uniformity.

---

## 18. P17 platform invariants

```yaml
platform_invariants:
  product_form: chatgpt_plugin_skills

  semantic_authority:
    owner: aegis_control_plane_plus_accepted_authority_basis
    github_write_result: not_authority
    codex_result: not_authority
    ci_result: not_authority

  absent:
    infer_from_missing_data: forbidden
    infer_from_tool_failure: forbidden
    infer_from_empty_search: forbidden
    requires_occurrence_basis: true
    requires_accepted_absence_basis: true

  repository:
    exact_commit_preferred_for_candidate_identity: true
    moving_branch_is_historical_identity: false
    state_json_is_authority: false

  writes:
    fresh_state_preflight_required: true
    last_write_wins_for_history: forbidden
    blind_retry_after_uncertain_write: forbidden
    coherent_final_candidate_required: true

  codex:
    role: execution_plane
    may_self_declare_gate_pass: false
    may_self_declare_authority_acceptance: false
    durable_result_revision_preferred: true

  ci:
    role: deterministic_verification_host
    pass_equals_authority_pass: false
    exact_tested_revision_required_for_strong_evidence: true

  runtime:
    daemon_required: false
    harness_required: false
    background_agent_required: false
    custom_transaction_service_required: false
```

---

## 19. Downstream implementation implications

When implementation is eventually authorized, P17 expects changes to stay inside the minimal P15 surfaces.

Likely implementation work includes:

```text
Skill/reference contract updates
future replacement schema/examples
minimal existing validator/compute/transition changes where mechanically required
regression tests
CI wiring for replacement-version validation
```

P17 does not authorize or require a new platform abstraction layer solely to wrap GitHub/Codex.

If a future implementation proposes such a layer, it must demonstrate a concrete platform portability or correctness need rather than treating P17 itself as justification.

---

## 20. P17 acceptance criteria

P17 is complete when all of the following are frozen:

1. semantic truth remains platform-independent;
2. ChatGPT/Aegis Skills own semantic/lifecycle interpretation;
3. GitHub reads supply evidence but negative reads do not prove absence;
4. GitHub writes execute explicit authorized mutations and return durable refs only;
5. Codex is execution plane and cannot self-declare Authority/Gate acceptance;
6. repository commits remain canonical durable candidate identity;
7. `state.json` remains derived, not Authority;
8. validator/CLI remains deterministic mechanical verification support;
9. CI remains a verification host, not lifecycle Authority;
10. uncertain writes require fresh-read reconciliation before retry;
11. stale basis invalidates a prepared mutation;
12. platform capability degradation must fail closed rather than weaken semantics;
13. exact-source provenance is preserved for downstream-critical evidence;
14. PR #82 cannot be repaired from tool absence, merge fact, or CI success alone;
15. no runtime/harness/daemon/background worker is introduced.

---

## 21. P17 disposition

```yaml
p17_platform_contract:
  scope: aegis/project-state
  finding: P22-F2

  semantic_basis:
    p12: 777e1e8a9652e2cbf220d234798641d65dc9b0c9
    p13: b742ebb9f27520a595b2e73370f42157e28ea72e

  architecture_basis:
    p14_repaired: cc768db72450b2c9d75a3d9650d447cdbd10048b
    p15_repaired: ffa79084c10211668ced1ae6801e238c789ffeb7
    p16: 40e094b62f9f3150516f4631ec9df98e6729d258

  product_form:
    type: ChatGPT_Plugin_Skills

  platform_contracts:
    - aegis_skill_control_plane
    - github_read_surface
    - github_write_surface
    - codex_execution_surface
    - git_repository_durable_state
    - deterministic_validator_cli
    - github_actions_ci_host

  authority_promotion:
    github_write_success_to_authority: forbidden
    codex_success_to_gate_pass: forbidden
    ci_pass_to_authority: forbidden
    empty_read_to_absent: forbidden

  required_new_runtime_services: []

  replacement_version_assigned: false
  project_state_persistence_authorized: false
  implementation_authorized: false
  release_authorized: false

  verdict: READY
  disposition: READY_FOR_P18_ENGINEERING_OPTIMIZATION
```

P17 ends at the platform-contract boundary. It does not execute P18.