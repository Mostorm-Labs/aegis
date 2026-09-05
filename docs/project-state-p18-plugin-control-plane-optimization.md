# Aegis Project State — P18 Plugin Control-Plane Optimization

Status: **P18 Engineering / Optimization Candidate**

Scope: `aegis/project-state`

Triggering finding: `P22-F2 = MISSING_CONTRACT / SPEC_DEFECT`

Repository basis: `main@3a2607220cd875dc66857b334dcfbd2c763e7c7d`

P12 semantic basis candidate: `777e1e8a9652e2cbf220d234798641d65dc9b0c9`

P13 operation basis candidate: `b742ebb9f27520a595b2e73370f42157e28ea72e`

Repaired P14 architecture basis candidate: `cc768db72450b2c9d75a3d9650d447cdbd10048b`

Repaired P15 module-design basis candidate: `ffa79084c10211668ced1ae6801e238c789ffeb7`

P16 interaction/evidence-flow basis candidate: `40e094b62f9f3150516f4631ec9df98e6729d258`

P17 platform-contract basis candidate: `97efff0e414f17c5667c957f6d497472a6d2459a`

Current Authority under repair: `aegis-project-state-v0.5`

This artifact defines engineering and workflow optimization for the repaired Plugin-native Project State architecture. The optimization target is lower control-plane cost with unchanged evidence rigor.

It does **not** introduce an Aegis runtime, daemon, agent loop, background reconciler, cache service, repository-state service, transaction service, or custom harness. It does not assign a replacement Project State version, does not modify `.aegis/*`, does not implement code, and does not authorize merge, release, rollout, or the real PR #82 reconciliation.

---

## 1. Optimization objective

The repaired architecture already makes the correct semantic tradeoff:

```text
fresh durable evidence
+ exact refs
+ fail-closed ambiguity
+ explicit lifecycle ownership
```

The remaining engineering problem is unnecessary control-plane repetition.

Typical avoidable cost includes:

```text
re-reading immutable exact artifacts already established in the same task
re-scanning broad repository history when exact durable refs are already known
re-reading both source/materialized Skill copies when equivalence is not under review
fetching full CI logs before a failure requires them
reconstructing long handoffs from prose instead of a compact exact-ref resume capsule
re-reading moving refs multiple times when no write or freshness-sensitive conclusion occurs
```

P18 therefore optimizes the **number, breadth, and timing of evidence reads and handoff fields**, not the semantic rules themselves.

The optimization rule is:

> Reuse immutable facts; refresh mutable facts; never cache away a correctness boundary.

---

## 2. Non-negotiable correctness constraints

No optimization is valid if it weakens any of the following:

```text
exact candidate identity
fresh-state verification for moving refs
Authority / Gate / Integration separation
occurrence-time truth
Absent != missing / unresolved
integrated historical immutability
no retroactive authorization
no CI-to-Authority promotion
no execution-result-to-Gate promotion
no cross-Primary substantive chaining
```

If an optimized path and a conservative full-rehydration path disagree, the optimized result is discarded and the conservative path wins.

---

## 3. Workload classes

P18 optimizes four recurring workloads.

### W1 — Same-session stage continuation

Example:

```text
P16 complete at exact SHA
→ user explicitly asks for P17
```

Characteristics:

- exact prior-stage artifact is already known;
- same repository / branch / repair line;
- only moving repository state needs freshness confirmation;
- most semantic basis is immutable.

### W2 — New-session durable resume

Example:

```text
new ChatGPT session
→ resume from a durable handoff / exact refs
```

Characteristics:

- conversation memory is not sufficient as durable truth;
- exact refs should reconstruct the trusted basis;
- moving repository refs must be refreshed;
- broad rediscovery should be unnecessary when a good handoff exists.

### W3 — Mutation-capable Project State repair

Example:

```text
future O4 PR #82 historical reconciliation
```

Characteristics:

- correctness-sensitive write;
- requires fresh preflight;
- requires accepted semantic/proof basis;
- requires a final pre-write freshness guard;
- requires post-write exact candidate reconciliation.

### W4 — Codex execution handoff / return

Characteristics:

- ChatGPT/Aegis owns control-plane semantics;
- Codex owns execution-local work;
- exact starting/result revisions matter;
- handoff size should be small enough to be reliable but complete enough to avoid semantic invention.

---

## 4. Optimization metrics

P18 defines structural metrics that can be checked without introducing telemetry infrastructure.

### 4.1 Repository read count

Count repository/connector reads required to establish a stage result.

Distinguish:

```text
moving_ref_reads
immutable_exact_ref_reads
broad_search_reads
targeted_evidence_reads
ci_summary_reads
ci_log_reads
```

### 4.2 Redundant immutable reads

A redundant immutable read is a repeated fetch of the same exact commit/ref/artifact when:

- its content was already established in the current task/session;
- no contradiction exists;
- the current decision does not require previously unread portions.

Target:

```text
same-session redundant immutable reads = 0 by default
```

### 4.3 Freshness reads

Freshness reads target moving state only.

Examples:

```text
branch HEAD
current PR head/state
current Authority pointer if represented by moving state
current workflow status
```

These are not considered waste when they protect a semantic or write boundary.

### 4.4 Handoff payload density

A handoff is efficient when every included field supports resume correctness.

Measure:

```text
required exact refs present
stale narrative omitted
forbidden actions explicit
next permitted stage/action explicit
```

Long prose is not itself evidence quality.

### 4.5 Evidence fan-out

Evidence fan-out is the number of independent sources fetched before a conclusion.

Optimization target:

```text
fetch the minimal complete evidence closure for the claim
```

Not:

```text
fetch everything related to the repository
```

### 4.6 Recovery cost

Measure the number of reads needed after:

```text
session interruption
uncertain write
Codex interruption
stale basis detection
```

The target is bounded recovery from exact refs rather than global rediscovery.

---

## 5. Baseline

P18 does not claim a measured latency/token benchmark yet.

The structural baseline is the conservative workflow already demonstrated by this repair line:

```text
stage entry
→ load stage Skill contract
→ read architecture contract
→ fresh-check main
→ fresh-check working branch
→ re-open one or more prior exact design artifacts
→ perform stage reasoning
→ write stage artifact
→ fetch resulting commit
→ fetch branch again
```

This baseline is safe but can over-read immutable prior-stage artifacts.

P18 therefore optimizes structural call count first. Runtime latency/token measurements, if later useful, may be collected from representative eval traces without changing the architecture.

---

## 6. Resource budgets

The following are engineering targets, not semantic permissions.

### 6.1 Same-session, same-Primary stage continuation

When exact prior-stage refs are already established and no contradiction is visible:

```text
mandatory repository freshness reads:
  working branch HEAD: 1
  main/baseline HEAD: 0..1, only when baseline drift matters

immutable basis re-fetches:
  0 by default
  fetch only if current stage needs content not already established
```

The stage Skill/architecture contract remains mandatory according to the Aegis Skill system; P18 does not optimize away Skill invocation.

### 6.2 New-session resume with durable handoff

Target resume budget before substantive reasoning:

```text
1. working branch HEAD
2. main/baseline HEAD if relevant
3. current exact basis artifact or handoff anchor
4. only targeted evidence refs required by the resumed question
```

A broad repository search should be fallback behavior, not the default.

### 6.3 Read-only diagnosis

Target:

```text
one fresh moving-ref read
+ targeted manifest/evidence reads
+ no pre-write refresh
+ no post-write reconciliation
```

### 6.4 Mutation-capable flow

Freshness budget is intentionally higher:

```text
entry moving-ref read: 1
pre-write moving-ref read: 1
post-write exact result reconciliation: 1
```

These are correctness boundaries and must not be removed merely to reduce call count.

### 6.5 CI inspection

Default order:

```text
combined/status summary
→ failing job summary
→ failing step/log only if needed
```

Do not fetch full logs when status and step summaries already establish the required fact.

---

## 7. Optimization O1 — Immutable exact-ref reuse

Exact immutable refs may be reused after they have been established.

Examples:

```text
commit SHA
review/comment ID
exact artifact at commit
accepted package ref
result revision
```

### Same-session rule

If the exact artifact was already read and summarized sufficiently for the current task:

```text
reuse it
```

Do not fetch it again solely for ritual freshness.

### Cross-session rule

A new session may trust an exact ref as an identity pointer, but if substantive content is required and not present in a durable handoff, fetch the exact artifact again.

Conversation recollection alone must not substitute for missing exact content when that content is necessary for the decision.

### Invalidation

Reuse is invalidated when:

```text
another durable source contradicts the remembered basis
artifact identity is only a moving branch/tag
current task needs content not previously established
Authority supersession changed applicability
```

---

## 8. Optimization O2 — Mutable-state freshness envelope

Not every fact needs the same freshness policy.

Classify inputs as:

```text
IMMUTABLE
  exact commit
  exact review/comment
  exact historical Gate Decision

MOVING
  branch HEAD
  PR head/status
  current workflow status
  moving Authority pointer

DERIVED
  state.json
  CI summaries
  conversational summaries
```

Rules:

```text
IMMUTABLE -> reuse by exact identity
MOVING    -> refresh at semantic/write boundaries
DERIVED   -> never override authored/Authority truth
```

This prevents both over-fetching immutable data and under-fetching mutable state.

---

## 9. Optimization O3 — Minimal evidence closure

When exact durable refs are already known, prefer direct fetches over discovery searches.

Example:

```text
known P22 review id
+ known PR number
+ known merge revision
```

should lead to targeted reads of those exact sources, not a repository-wide search for all comments, gates, and commits.

Broad search remains appropriate when:

- a required ref is genuinely unknown;
- evidence completeness cannot otherwise be established;
- contradictory state suggests the handoff is stale.

The optimization must never use a narrow search result to prove global absence.

---

## 10. Optimization O4 — Compact durable resume capsule

P18 standardizes a compact **Resume Capsule** for session handoff.

It is not a new Project State schema object and is not Authority. It is a durable navigation aid that may live in a PR comment, issue comment, design artifact, or user-supplied handoff.

Recommended fields:

```yaml
repository: <owner/repo>
working_ref: <branch>
expected_head: <exact sha>
current_owner: <aegis specialist>
current_stage: <stage>
trusted_basis:
  - <role>: <exact durable ref>
blocker: <none or exact blocker>
forbidden_actions:
  - <important stop boundaries>
next_permitted_action: <single next action>
```

Optional only when needed:

```yaml
current_authority: <exact ref>
package_id: <id>
package_ref: <exact ref>
task_anchor: <exact ref>
result_revision: <exact ref>
proof_refs:
  - <exact refs>
```

The capsule should not duplicate whole documents.

### Resume algorithm

```text
read capsule
→ fresh-check expected moving refs
→ fetch exact basis only when needed
→ if consistent, resume
→ if inconsistent, invalidate capsule assumptions and fail closed
```

No background handoff service is required.

---

## 11. Optimization O5 — Handoff field discipline

A Codex or next-session handoff should contain facts the receiver cannot safely infer.

Required categories:

```text
identity
exact basis
allowed scope
forbidden scope
verification expectation
stop boundary
expected return
```

Avoid:

```text
large historical narrative already encoded by exact refs
repetition of accepted stages that are not under review
speculative next-stage instructions beyond the stop boundary
```

The goal is less prose and more exact identity.

---

## 12. Optimization O6 — Progressive CI evidence

CI inspection should be demand-driven.

### PASS path

If the exact candidate's relevant workflow summary is clearly successful and no deeper proof is required:

```text
summary is sufficient as mechanical CI evidence
```

### FAIL path

Escalate progressively:

```text
workflow run
→ job
→ failing step
→ targeted log region
```

Do not load unrelated logs.

### Authority boundary

Even a fully inspected CI PASS remains mechanical evidence only.

---

## 13. Optimization O7 — Source/materialization read deduplication

The repository may contain both source and materialized Plugin copies, for example under:

```text
skillset/skills/**
skills/**
```

P18 does not define which copy is authoritative where the repository contract has not already done so.

Optimization rule:

- do not read both copies on every architecture/reasoning turn merely to prove they are identical;
- when equivalence is under implementation or release verification, verify it using the repository's materialization/skillset checks;
- when a divergence is specifically suspected, inspect both exact copies.

Materialization equality is a verification concern, not a recurring conversational read tax.

---

## 14. Optimization O8 — Staged read depth

Use three read depths.

### Depth 1 — identity

Fetch only enough to establish:

```text
exact SHA
branch head
PR status
workflow status
```

### Depth 2 — targeted semantic content

Fetch the exact artifact/range needed for the decision.

### Depth 3 — full deep inspection

Use only when:

```text
contradiction exists
exact meaning is disputed
review/audit requires full context
failure diagnosis requires it
```

Defaulting every task to Depth 3 is safe but inefficient.

---

## 15. Optimization O9 — No speculative downstream work

Direct Primary-to-Primary substantive chaining is already forbidden.

P18 adds an efficiency reason to the same rule:

```text
Do not pre-read or precompute the next Primary's substantive evidence set
before the user/lifecycle boundary authorizes that stage.
```

This avoids wasted reads and prevents stale speculative reasoning.

Within the same Primary family, the next explicitly requested stage may inherit exact immutable basis from the just-completed stage.

---

## 16. Optimization O10 — Fail-fast contradiction detection

Before loading a large evidence set, check the smallest set of facts capable of invalidating the current basis.

Typical order:

```text
working branch HEAD
main/baseline HEAD if relevant
current Authority pointer/ref
exact target record identity
```

If one of these already contradicts the handoff:

```text
stop
→ do not continue fetching downstream evidence
→ recompute routing/basis
```

This reduces wasted tool usage while improving safety.

---

## 17. Write optimization without a transaction system

For repository writes, optimize around existing Git semantics.

Preferred path:

```text
prepare complete intended delta
→ final fresh-state check
→ coherent repository commit
→ exact result SHA
→ deterministic verification
```

Do not introduce a custom transaction layer to save connector calls.

If a platform requires multiple sequential file writes, efficiency is secondary to correctness. Intermediate materialization must not be falsely accepted as complete Project State.

---

## 18. Codex execution optimization

Use Codex only when repository-side execution materially benefits from a development workspace.

Do not hand off pure Aegis semantic reasoning such as:

```text
Is this historical binding Bound or Absent?
Which Authority owns the lifecycle decision?
Does a later PASS retroactively authorize an occurrence?
```

Those belong to the control plane.

A compact Codex package should maximize executable specificity and minimize rediscovery:

```yaml
repository: <repo>
branch: <branch>
expected_start: <sha>
package_or_stage: <id>
authority_basis:
  - <exact refs>
allowed_scope:
  - <paths/tasks>
required_verification:
  - <commands/evidence>
forbidden_actions:
  - <boundaries>
return:
  - actual_starting_revision
  - result_revision
  - changed_files
  - verification_results
  - deviations_or_blockers
```

This preserves the low-Codex-consumption product model: ChatGPT does control-plane reasoning; Codex performs bounded execution.

---

## 19. Recovery optimization

### 19.1 Session interruption

Preferred recovery:

```text
Resume Capsule
+ exact durable refs
+ fresh moving-state check
```

Not:

```text
reconstruct the entire project from conversation history
```

### 19.2 Uncertain write

Preferred recovery:

```text
fresh-read exact target
→ compare with intended result
→ classify materialized / absent / partial-conflict
```

No blind retry.

### 19.3 Codex interruption

Preferred recovery:

```text
inspect actual worktree/branch diff and revision
→ continue from durable workspace state
```

Do not replay already-completed steps solely because the conversation ended.

---

## 20. Observability / evidence plan

P18 intentionally avoids a telemetry daemon.

Optimization can be verified with representative recorded/eval traces.

Suggested benchmark scenarios:

```text
B1 same-session P16 -> P17-like continuation
B2 new-session resume from exact handoff capsule
B3 read-only Project State diagnosis
B4 O4 mutation preflight + write + verify
B5 Codex handoff + execution return reconciliation
B6 uncertain write recovery
B7 stale handoff contradiction
```

For each scenario record:

```text
repository reads by class
broad searches
immutable duplicate reads
moving freshness reads
write attempts
post-write reconciliation reads
handoff field count
correct final semantic verdict
```

Correctness gates:

```text
0 semantic promotions from tool success to Authority/Gate truth
0 missing/negative-read -> Absent inferences
0 stale-basis writes accepted
0 historical rewrites accepted
```

Only after correctness remains perfect should lower call count be accepted as an optimization win.

---

## 21. Performance targets

Because no measured production baseline is claimed here, P18 defines bounded structural targets rather than latency promises.

### Target T1 — same-session continuation

```text
redundant immutable repository reads: 0 by default
moving-state freshness reads: <= 2 before a non-mutating stage result
broad discovery searches: 0 when exact refs are already known
```

### Target T2 — durable session resume

```text
resume can normally begin substantive reasoning after:
  1 working-ref fresh read
  + 0..1 baseline fresh read
  + targeted exact basis/evidence reads
```

### Target T3 — mutation safety

```text
entry freshness + pre-write freshness + post-write reconciliation remain mandatory
```

No call-count target may remove those three boundaries.

### Target T4 — CI inspection

```text
full logs fetched only for failing/ambiguous evidence paths
```

### Target T5 — handoff compactness

A normal resume capsule should fit in a small structured block containing exact refs and stop boundaries, rather than duplicating full stage documents.

---

## 22. Resource budget hierarchy

When optimizing, spend resources in this priority order:

```text
1. correctness-critical fresh reads
2. exact durable evidence reads
3. targeted contradiction resolution
4. deterministic verification
5. convenience/context enrichment
```

If tool-call or context budget becomes constrained, drop convenience reads first, never the correctness-critical boundaries.

---

## 23. Reference / rollback path

Every optimization has a safe fallback: **Full Rehydration Mode**.

Full Rehydration Mode means:

```text
re-read current moving refs
re-read exact Authority/design artifacts needed for the decision
re-read exact occurrence/Gate/evidence refs
run deterministic validation where relevant
reconstruct the conclusion from durable sources
```

Enter Full Rehydration Mode when:

```text
handoff is incomplete
exact refs disagree
branch/head drift is unexpected
Authority supersession is unclear
negative evidence would otherwise be used to infer absence
session-local summary confidence is insufficient
write outcome is uncertain
```

The optimization layer must always be removable without changing semantic outcomes.

---

## 24. Explicitly forbidden optimization techniques

The following are rejected even if they reduce calls:

```text
persistent hidden semantic cache
background repository watcher
agent loop that auto-resumes stages
using conversation memory as canonical project state
skipping fresh pre-write checks
assuming branch name identifies exact candidate
using CI green as Gate PASS
using missing search results as Absent
prefetching future Primary work without authorization
creating a local repository mirror as independent Authority
creating a new Aegis daemon/service for handoff or caching
```

---

## 25. PR #82 optimization profile

The future real PR #82 O4 repair should use the optimized path only after its lifecycle prerequisites are satisfied.

Efficient evidence set should be exact and bounded:

```text
replacement Project State Authority exact ref
accepted absence-proof / verification exact refs
PR #82 occurrence evidence
integrated revision 3a2607220cd875dc66857b334dcfbd2c763e7c7d
P22-F2 durable governance basis
relevant P23 statement that it did not authorize merge
current .aegis target record/state
```

No repository-wide search should be needed if these refs remain durable and uncontradicted.

Immediately before mutation, moving repository state must still be refreshed.

After mutation, exact result revision plus deterministic validation remains required.

Optimization does not reduce the proof burden; it removes irrelevant reads around that burden.

---

## 26. Engineering decision summary

P18 chooses **protocol discipline** over infrastructure.

The primary optimizations are:

```text
exact-ref reuse
mutable-vs-immutable freshness classification
minimal evidence closure
compact durable Resume Capsule
progressive CI inspection
source/materialization deduplication
staged read depth
fail-fast contradiction checks
bounded Codex handoffs
full-rehydration fallback
```

The architecture still requires no new runtime subsystem.

---

## 27. P18 acceptance criteria

P18 is complete when downstream work can optimize Project State control-plane cost while preserving all of the following:

1. immutable exact refs are reused rather than ritualistically re-fetched;
2. moving state is still refreshed at semantic/write boundaries;
3. a compact durable handoff can resume work without global rediscovery;
4. broad search is fallback, not default, when exact refs are known;
5. CI/log reads are progressive and targeted;
6. Codex handoffs contain exact execution boundaries and do not delegate semantic Authority;
7. no new cache daemon, agent loop, harness, transaction service, or background reconciler is introduced;
8. Full Rehydration Mode remains the correctness reference path;
9. optimization success is measured only after semantic correctness remains unchanged;
10. the real PR #82 repair remains unauthorized until the replacement Authority and downstream verification lifecycle are complete.

---

## 28. P18 disposition

```yaml
p18_engineering_optimization:
  scope: aegis/project-state
  finding: P22-F2
  basis:
    p12: 777e1e8a9652e2cbf220d234798641d65dc9b0c9
    p13: b742ebb9f27520a595b2e73370f42157e28ea72e
    p14_repaired: cc768db72450b2c9d75a3d9650d447cdbd10048b
    p15_repaired: ffa79084c10211668ced1ae6801e238c789ffeb7
    p16: 40e094b62f9f3150516f4631ec9df98e6729d258
    p17: 97efff0e414f17c5667c957f6d497472a6d2459a

  optimization_strategy:
    primary: protocol_discipline
    infrastructure_expansion: false

  key_optimizations:
    - immutable_exact_ref_reuse
    - mutable_state_freshness_envelope
    - minimal_evidence_closure
    - compact_resume_capsule
    - progressive_ci_inspection
    - materialization_read_deduplication
    - staged_read_depth
    - fail_fast_contradiction_detection
    - bounded_codex_handoff

  correctness_reference_path: FULL_REHYDRATION_MODE

  forbidden:
    - persistent_hidden_semantic_cache
    - background_repository_watcher
    - autonomous_stage_resume
    - agent_loop
    - custom_harness
    - cache_service
    - transaction_service
    - conversation_memory_as_authority

  replacement_version_assigned: false
  aegis_persistence_performed: false
  implementation_authorized: false
  merge_authorized: false
  release_authorized: false

  verdict: READY
  disposition: ARCHITECTURE_STAGE_FAMILY_COMPLETE
```

P18 completes the P14–P18 architecture stage family for this Project State repair candidate. It does not itself authorize the next substantive Primary stage.