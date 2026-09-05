# Aegis Project State — P20 Ungated Integration Verification Design

Status: **P20 Verification Design Candidate**

Scope: `aegis/project-state`

Triggering finding: `P22-F2 = MISSING_CONTRACT / SPEC_DEFECT`

Repository basis: `main@3a2607220cd875dc66857b334dcfbd2c763e7c7d`

Trusted replacement design chain:

```yaml
P12_semantic_schema: 777e1e8a9652e2cbf220d234798641d65dc9b0c9
P13_operation_model: b742ebb9f27520a595b2e73370f42157e28ea72e
P14_plugin_native_architecture: cc768db72450b2c9d75a3d9650d447cdbd10048b
P15_minimal_module_design: ffa79084c10211668ced1ae6801e238c789ffeb7
P16_plugin_interaction_flow: 40e094b62f9f3150516f4631ec9df98e6729d258
P17_plugin_platform_contract: 97efff0e414f17c5667c957f6d497472a6d2459a
P18_control_plane_optimization: 976de3f7729fc2c63a4726458afbe37292f35c17
```

Current Authority under repair: `aegis-project-state-v0.5`

This artifact defines the proof contract required before the Project State repair may be treated as implementation-ready or Gate-complete. It does not assign a replacement Project State version, does not modify `.aegis/*`, does not implement code, does not supersede v0.5, does not reconcile PR #82, and does not authorize merge, release, or rollout.

---

## 1. Verification objective

The repair is acceptable only if evidence proves all of the following without fabricating historical authorization:

1. the replacement representation can faithfully express an integrated occurrence with either an exact historical Gate Decision or explicit confirmed absence of one;
2. `Absent` cannot arise from missing data, failed lookup, unresolved identity, or incomplete evidence;
3. occurrence-time binding becomes immutable historical truth after integration;
4. later PASS decisions never retroactively rewrite an earlier occurrence;
5. legacy v0.5 bound history migrates losslessly and never infers `Absent`;
6. deterministic Project State projection preserves the distinction between `Absent` and `Bound(BLOCKED)`;
7. the product remains a ChatGPT Plugin/Skills control plane rather than acquiring an Aegis runtime/harness/service layer;
8. GitHub/Codex/CI mechanical success cannot silently become Authority, Gate, or historical truth;
9. PR #82 can be represented truthfully as a real integrated occurrence with explicit `Absent`, but only after the replacement Authority is accepted/applicable and the required historical proof remains uncontradicted.

The verification principle is:

```text
mechanical representability
+
historical semantic correctness
+
platform-boundary correctness
+
no forbidden runtime expansion
```

All four are required.

---

## 2. Evidence-strength policy

Use the cheapest evidence that credibly proves each requirement.

```text
Schema / local invariant behavior
-> deterministic automated tests + fixed fixtures

Cross-snapshot historical immutability
-> deterministic transition corpus

Migration equivalence
-> deterministic golden migration corpus

Skill / platform semantic behavior
-> contract fixtures + repository diff review + existing Skill regressions

Historical Absent truth
-> durable occurrence evidence + accepted governance absence determination

PR #82 concrete case
-> exact durable repository/governance refs + deterministic replacement-state fixture
```

A raw tool search returning no result is never an acceptable absence oracle.

A green CI run is never an Authority or Gate verdict by itself.

---

## 3. Verification map overview

The mandatory requirement groups are:

```text
V1  Gate Decision Binding representation
V2  Status × binding constraints
V3  Absent non-inference
V4  Historical conformance projection
V5  Historical immutability
V6  Occurrence-time binding / later-PASS behavior
V7  Legacy v0.5 migration
V8  P13 operation legality
V9  Plugin-native architecture / forbidden-runtime boundary
V10 Platform-result authority separation
V11 PR #82 historical absence oracle
V12 Deterministic replay / idempotency
V13 Failure / stale-basis / uncertain-write safety
V14 Resume / exact-ref optimization safety
```

Every mandatory group must have an executable or durable reviewable evidence artifact before P34 may PASS the later implementation.

---

# 4. V1 — Gate Decision Binding representation

## Requirement

The replacement schema must represent exactly one historical binding form:

```text
Bound(exact Gate Decision)
OR
Absent(no_applicable_integration_gate_decision)
```

## Invariant

For every replacement-schema Integration record:

```text
exactly one binding variant is present
```

For Bound:

```yaml
gate_decision_binding:
  kind: bound
  gate_decision_id: <exact decision id>
```

For Absent:

```yaml
gate_decision_binding:
  kind: absent
  reason: no_applicable_integration_gate_decision
```

## Oracle / reference

P12 semantic schema `777e1e8a9652e2cbf220d234798641d65dc9b0c9`.

## Fixture corpus

Mandatory positive fixtures:

```text
integrated + Bound(PASS)
integrated + Bound(BLOCKED)
integrated + Absent(valid reason)
```

Mandatory negative fixtures:

```text
both Bound and Absent fields present
binding kind unknown
Bound missing gate_decision_id
Absent missing reason
Absent with unknown reason
binding omitted in replacement schema
legacy gate_decision_id used where replacement schema forbids it
```

## Test / probe

JSON Schema validation plus deterministic Project State validation.

## Metric / threshold

```text
all positive fixtures accepted = 100%
all negative fixtures rejected = 100%
```

Any false accept/reject in the mandatory corpus is Gate-blocking.

## Evidence artifact

Deterministic test output bound to exact candidate revision.

---

# 5. V2 — Status × binding constraints

## Requirement

P12 status constraints remain exact:

```text
awaiting_integration -> Bound only
integrated           -> Bound | Absent
closed_unmerged      -> Bound only
```

## Invariant

`Absent` is legal only for finalized integrated history in this repair.

## Fixture corpus

```text
awaiting + Bound -> valid
awaiting + Absent -> invalid
integrated + Bound -> valid
integrated + Absent -> valid
closed_unmerged + Bound -> valid
closed_unmerged + Absent -> invalid
```

## Test / probe

Schema and/or deterministic validator according to the final implementation boundary.

## Threshold

100% agreement with the corpus.

---

# 6. V3 — Absent non-inference

## Requirement

`Absent` is positive historical truth and must never be inferred from incomplete mechanical state.

## Invariant

The following must never produce `Absent`:

```text
missing binding field
missing gate decision record
dangling decision reference
GitHub 404
empty search
permission denied
timeout
pagination incomplete
Authority unknown
failed repository read
```

## Oracle / reference

P12, P13, P16, and P17 exact bases.

## Fixture / probe

At minimum test mechanical cases for:

```text
missing binding
dangling Bound decision
unknown decision id
```

For platform-read failure semantics, use contract/eval fixtures showing that the Skill returns a blocked/unresolved result rather than authoring `Absent`.

## Metric / threshold

```text
false_Absent_count = 0
```

Any inferred Absent from unresolved data is a hard Gate failure.

---

# 7. V4 — Historical conformance projection

## Requirement

Occurrence and Gate conformance remain separate facts.

## Invariant

```text
Bound(PASS or PASS_WITH_FINDINGS) -> conforming
Bound(BLOCKED_*)                  -> nonconforming
Absent(valid historical absence) -> nonconforming
```

`Bound(BLOCKED)` and `Absent` must remain distinguishable in authored and derived state.

## Fixture corpus

At minimum:

```text
historical PASS binding
historical BLOCKED binding
historical Absent binding
```

## Test / probe

Deterministic state recomputation / projection comparison.

## Threshold

Exact expected projection for every fixture.

---

# 8. V5 — Historical immutability

## Requirement

Once an Integration is `integrated`, its historical identity-bearing fields cannot be rewritten by normal Project State mutation.

## Invariant

Immutable after integration:

```text
id
kind
ref
target_ref
integrated_revision
gate_decision_binding
```

## Negative transition corpus

The transition validator must reject at least:

```text
Bound(D1) -> Bound(D2)
Bound(D) -> Absent
Absent -> Bound(D)
Absent(reason) -> Absent(other reason)
integrated_revision change
ref change
target_ref change
kind change
removal of integrated occurrence
integrated -> awaiting_integration
integrated -> closed_unmerged
```

## Positive transition corpus

```text
O6 append corroborating evidence without identity change
unrelated Project State changes that preserve integrated identity
```

## Metric / threshold

All forbidden transitions rejected; all legal preservation cases accepted.

---

# 9. V6 — Occurrence-time binding and later PASS

## Requirement

Historical binding is resolved from the actual occurrence-time governance state.

## Invariant

```text
current/future PASS
!= authorization for an earlier occurrence
```

## Oracle / reference

P13 occurrence-time binding rule and P17 platform-independent contract.

## Golden scenarios

Scenario A:

```text
awaiting Bound(D1)
occurrence governed by D1
-> integrated Bound(D1)
```

Scenario B:

```text
awaiting Bound(D1)
occurrence governed by D2
-> integrated Bound(D2)
```

Scenario C:

```text
occurrence had confirmed no applicable integration Gate
-> integrated Absent
later D3 = PASS
-> historical binding remains Absent
```

Scenario D:

```text
historical Bound(BLOCKED D1)
later D2 = PASS
-> historical binding remains Bound(D1)
```

## Threshold

No golden scenario may permit retroactive binding.

---

# 10. V7 — Legacy v0.5 migration

## Requirement

Existing v0.5 history must migrate without changing historical meaning.

## Invariant

Legacy:

```yaml
gate_decision_id: D
```

must become exactly:

```yaml
gate_decision_binding:
  kind: bound
  gate_decision_id: D
```

No legacy record is inferred as Absent.

## Corpus

Include representative v0.5 records covering:

```text
integrated PASS
integrated BLOCKED
awaiting_integration
closed_unmerged
```

Include current root examples such as existing integrated records and specifically preserve PR #9's original historical BLOCKED binding semantics.

## Probe

One-shot deterministic migration followed by replacement-schema validation and state recomputation.

## Metric / threshold

```text
identity_preservation = 100%
binding_semantic_preservation = 100%
inferred_Absent_from_legacy = 0
```

---

# 11. V8 — P13 operation legality

## Requirement

P13 O1-O6 remain semantic transition vocabulary, with legal pre/postconditions, without becoming a runtime API requirement.

## Invariants

```text
O1 none -> awaiting Bound
O2 awaiting Bound -> awaiting Bound, pre-occurrence only
O3 awaiting -> integrated, one-time occurrence finalization
O4 none -> integrated, historical reconciliation only
O5 awaiting Bound -> closed_unmerged Bound
O6 integrated -> same historical identity + appended corroborating evidence only
```

## Verification method

Use state-transition fixtures, not an operation executor API.

The implementation may prove these contracts through schema + existing transition validation + tests.

## Hard negative

Verification must not require or reward creation of:

```text
integration_ops.py
operation dispatcher
mutation service
transaction service
```

merely to satisfy P13 naming.

---

# 12. V9 — Plugin-native architecture / forbidden-runtime boundary

## Requirement

The repair must remain a ChatGPT Plugin/Skills control-plane feature.

## Invariant

The implementation must not introduce an Aegis-owned:

```text
daemon
autonomous agent runtime
background reconciler
custom harness
repository-state service
transaction server
internal execution loop
```

## Oracle / reference

P14 `cc768db72450b2c9d75a3d9650d447cdbd10048b` and P15 `ffa79084c10211668ced1ae6801e238c789ffeb7`.

## Evidence

Changed-file review plus repository architecture review against the exact implementation candidate.

Expected implementation bias:

```text
Skill/reference contract changes
replacement schema/examples
minimal existing validator changes only where mechanically necessary
regression tests
```

Expected not to add:

```text
tools/aegis_state/integration_ops.py
tools/aegis_state/transaction.py
required transition.py dispatcher
integration history service
new agent/daemon/service entrypoint
```

## Threshold

No forbidden runtime surface may be introduced.

A tiny pure helper inside existing deterministic tooling is not automatically a failure if it has no orchestration/authority role and is justified by implementation simplicity.

---

# 13. V10 — Platform-result authority separation

## Requirement

Mechanical platform results must retain their correct evidence role.

## Invariants

The following promotions are forbidden:

```text
GitHub write success -> Authority accepted
Codex tests pass -> P34 PASS
CI green -> Gate Decision PASS
tool search empty -> Absent
repository merge -> merge was Gate-authorized
```

## Oracle / reference

P17 `97efff0e414f17c5667c957f6d497472a6d2459a`.

## Evidence

Skill/eval cases or structured review fixtures that exercise these statements and require fail-closed outcomes.

## Threshold

Zero authority-promotion violations in the mandatory corpus.

---

# 14. V11 — Historical Absent proof oracle

This is the critical proof contract introduced by P20.

## 14.1 Generic Absent claim

A Project State historical `Absent` claim is acceptable only when all of the following are available:

```text
A. Occurrence Basis
B. Accepted Absence Basis
C. Exact occurrence identity / revision
D. No contradictory positive applicable-Gate evidence
```

### A. Occurrence Basis

Must durably prove:

```text
the repository occurrence happened
exact Integration identity/ref
exact target
exact integrated revision
```

A branch name or conversational claim alone is insufficient.

### B. Accepted Absence Basis

Must be an explicit durable governance/verification determination whose semantic conclusion is equivalent to:

```text
no applicable integration-authorizing Gate Decision existed for this occurrence
```

The determination must not merely say:

```text
no record was found
```

or rely on a single incomplete search.

### C. Exact occurrence identity

The absence determination and occurrence evidence must refer to the same historical occurrence.

### D. Contradiction rule

If any durable evidence establishes a positive applicable Gate Decision for the occurrence, the Absent claim fails.

If applicability is ambiguous, the result is:

```text
BLOCKED_EVIDENCE
```

not Absent.

---

## 14.2 PR #82 canonical oracle

PR #82 is the mandatory golden historical-absence case for this repair.

### Occurrence Basis

Repository evidence must establish:

```yaml
repository: Mostorm-Labs/aegis
pr: 82
state: merged
target: main
merge_commit: 3a2607220cd875dc66857b334dcfbd2c763e7c7d
```

### Non-authorization basis

P23 review:

```text
5122113780
```

explicitly records:

```text
pr_82_merge_authorized_by_this_review: false
```

Therefore P23 itself is not a valid historical integration-authorizing Gate Decision for PR #82.

### Accepted absence/governance basis

P22 Five-Axis Drift Review:

```text
5553423707
```

explicitly establishes that:

```text
- no separate P24/P34 integration-authorizing Gate Decision for PR #82 was durably created before merge;
- PR #82 nevertheless became a real repository occurrence at 3a260722...;
- binding the occurrence to P23 5122113780 would misstate history;
- creating a later PASS and binding it backward would be retroactive authorization;
- current v0.5 cannot represent the occurrence without losing truth or fabricating authorization.
```

P20 treats that exact P22 determination as the current durable Absence Basis candidate for the PR #82 golden case.

### Required PR #82 expected result after replacement Authority is applicable

```yaml
id: int-pr82
kind: pull_request
ref: https://github.com/Mostorm-Labs/aegis/pull/82
status: integrated
target_ref: main
integrated_revision: 3a2607220cd875dc66857b334dcfbd2c763e7c7d

gate_decision_binding:
  kind: absent
  reason: no_applicable_integration_gate_decision

historical_conformance: nonconforming
```

### Mandatory negative PR #82 variants

Verification must reject or mark invalid any fixture that attempts to:

```text
bind PR #82 to P23 review 5122113780 as integration authorization
bind PR #82 to a later PASS decision
omit the binding entirely
invent a synthetic PASS decision
erase the repository occurrence
classify tool lookup failure as the absence basis
```

### Threshold

The canonical PR #82 fixture must produce the expected Absent/nonconforming result, and every forbidden variant must fail.

---

# 15. V12 — Deterministic replay and idempotency

## Requirement

Repeated evaluation of identical durable input must produce identical Project State output.

## Invariants

```text
same exact authored state + same exact evidence refs
-> same validation/projection result
```

For an already materialized historical reconciliation payload:

```text
same Integration.id + same immutable payload
-> deterministic no-op / identical state
```

Conflicting payload for the same historical Integration identity must fail closed.

## Metric / threshold

Zero nondeterministic result differences across repeated fixture runs.

---

# 16. V13 — Failure / stale-basis / uncertain-write safety

## Requirement

Execution failure must never be promoted into semantic truth or duplicated history.

## Scenarios

```text
stale branch head before write
write timeout with unknown outcome
partial multi-file materialization
tool read failure
concurrent branch movement
```

## Expected behavior

```text
stale basis -> discard prior mutation specification and recompute
uncertain write -> fresh-read before any retry
partial/conflicting materialization -> BLOCKED
read failure -> unresolved, never Absent
```

## Evidence

Contract/eval cases and, where implementation touches write helpers, targeted tests.

No custom transaction service is required.

---

# 17. V14 — Resume / exact-ref optimization safety

## Requirement

P18 optimizations may reduce redundant reads but must not weaken correctness.

## Invariants

```text
immutable exact refs may be reused
moving refs refresh at semantic/write boundaries
derived state never overrides authored/Authority truth
optimized path disagreement with full rehydration -> optimized result discarded
```

## Verification method

Use paired reasoning/eval scenarios:

```text
stable exact basis -> optimized and full path agree
moving branch changed -> optimized path detects stale basis
contradictory Authority ref -> full rehydration fallback
```

## Threshold

No optimized scenario may produce a different accepted semantic result from the conservative reference path.

---

# 18. Replacement-version verification boundary

P20 intentionally does not choose the replacement schema version number.

When governance later assigns the replacement version, all version-specific fixtures and expected paths must bind to that accepted exact version.

Until then, verification artifacts should use semantic labels such as:

```text
replacement-schema
replacement-binding-format
```

rather than guessing a version identifier.

Version assignment belongs to the later accepted Authority/supersession lifecycle, not P20.

---

# 19. Evidence artifact contract

The later implementation must make evidence reviewer-resolvable from the exact candidate revision.

Mandatory evidence classes:

```yaml
schema_and_validation:
  - replacement binding positive/negative corpus
  - status-binding corpus

historical_transition:
  - immutable integrated-history corpus
  - O6 legal append case

projection:
  - PASS / BLOCKED / Absent conformance golden cases

migration:
  - v0.5 Bound -> replacement Bound equivalence corpus

historical_absence:
  - PR #82 canonical occurrence + absence fixture
  - forbidden retroactive/synthetic variants

platform_contract:
  - no false authority promotion cases
  - read-failure != Absent cases

architecture_boundary:
  - exact changed-file review proving no forbidden runtime/harness expansion
```

Exact file paths may be selected during implementation planning/package design, but every evidence class above is mandatory.

---

# 20. P34 Gate contract for the future implementation

A later P34 review may PASS only if all of the following hold on the exact implementation candidate:

1. replacement-schema fixtures pass;
2. all invalid binding/status cases fail as expected;
3. `Absent` is never inferred from missing/unresolved data;
4. conformance projection distinguishes Bound(PASS), Bound(BLOCKED), and Absent;
5. all forbidden historical rewrites are rejected;
6. later PASS does not rewrite earlier Bound(BLOCKED) or Absent history;
7. v0.5 migration is lossless for existing bound records and creates zero inferred Absent records;
8. PR #82 canonical fixture produces integrated + Absent + nonconforming;
9. all PR #82 retroactive/synthetic/fabricated variants fail;
10. no forbidden Aegis runtime/harness/service architecture was introduced;
11. GitHub/Codex/CI mechanical results remain mechanically scoped and are not promoted into Authority/Gate truth;
12. deterministic replay is stable;
13. current Skill/reference/source/materialization surfaces required by the accepted package are semantically aligned;
14. exact candidate CI/evidence is durable and reviewer-resolvable.

Possible P34 verdicts remain:

```text
PASS
PASS_WITH_FINDINGS
BLOCKED_IMPLEMENTATION
BLOCKED_AUTHORITY
BLOCKED_EVIDENCE
BLOCKED_ENVIRONMENT
```

Missing PR #82 historical absence proof is `BLOCKED_EVIDENCE`, never `PASS_WITH_FINDINGS`.

---

# 21. Pre-implementation Authority-review checks

Before implementation planning, the later P21 Authority Review should verify that this P20 design is compatible with the replacement P12-P18 chain and that no earlier contradiction has appeared.

P21 should specifically confirm:

```text
P12 explicit Bound|Absent semantics remain accepted candidate truth
P13 immutable occurrence-time binding remains accepted
P14-P18 remain Plugin-native and no-harness
P20 does not smuggle implementation choices into verification truth
PR #82 P22/P23 durable refs still mean what this oracle assumes
Current v0.5 remains Current until explicit supersession
```

If any of these fail, P21 must block or route to the earliest affected layer rather than relaxing P20.

---

# 22. Non-goals

P20 does not:

- assign the replacement Project State schema version;
- modify `.aegis/*`;
- create `int-pr82` in real Project State;
- create a Gate Decision for PR #82;
- reinterpret P23 `5122113780` as merge authorization;
- create a later PASS for retroactive use;
- implement schema/validator/test changes;
- define a Python operation engine;
- create a daemon, agent, harness, service, or background worker;
- start P21, P23, P30, P31, P32, or P34;
- merge or release anything.

---

# 23. P20 acceptance criteria

P20 is complete when the verification design provides a credible proof path for every materially changed contract and does not rely on implementation claims to establish semantic truth.

Acceptance checklist:

1. Bound/Absent representation is covered by deterministic positive/negative fixtures;
2. status/binding constraints are covered;
3. Absent non-inference is explicitly tested;
4. historical conformance projection is covered;
5. historical immutability is covered by cross-snapshot negative corpus;
6. later-PASS / occurrence-time semantics are covered;
7. v0.5 migration equivalence is covered;
8. P13 operations are verified as state semantics, not runtime APIs;
9. Plugin-native/no-runtime architecture is a Gate condition;
10. platform-result authority separation is a Gate condition;
11. a generic historical Absent proof oracle is defined;
12. PR #82 exact golden oracle is defined using durable occurrence + governance refs;
13. deterministic replay/idempotency is covered;
14. stale-basis / uncertain-write safety is covered;
15. P18 optimization never outranks full rehydration correctness;
16. missing core evidence yields `BLOCKED_EVIDENCE`;
17. no replacement version is invented prematurely.

---

# 24. P20 disposition

```yaml
p20_verification_design:
  scope: aegis/project-state
  finding: P22-F2

  upstream_basis:
    P12: 777e1e8a9652e2cbf220d234798641d65dc9b0c9
    P13: b742ebb9f27520a595b2e73370f42157e28ea72e
    P14: cc768db72450b2c9d75a3d9650d447cdbd10048b
    P15: ffa79084c10211668ced1ae6801e238c789ffeb7
    P16: 40e094b62f9f3150516f4631ec9df98e6729d258
    P17: 97efff0e414f17c5667c957f6d497472a6d2459a
    P18: 976de3f7729fc2c63a4726458afbe37292f35c17

  historical_absence_oracle:
    occurrence_basis_required: true
    accepted_absence_basis_required: true
    ambiguity_result: BLOCKED_EVIDENCE
    tool_negative_result_is_absence: false

  pr82_golden:
    occurrence_revision: 3a2607220cd875dc66857b334dcfbd2c763e7c7d
    non_authorization_ref: 5122113780
    absence_governance_ref: 5553423707
    expected_binding: absent/no_applicable_integration_gate_decision
    expected_conformance: nonconforming

  implementation_required_now: false
  replacement_version_assigned: false
  project_state_mutated: false

  verdict: READY
  disposition: READY_FOR_P21_AUTHORITY_REVIEW
```

---

# 25. Stop boundary

This P20 candidate stops at Verification Design.

The next legal substantive stage is:

```text
aegis-governance -> P21 Authority Review
```

P21 must independently review the exact P12-P20 replacement chain and fresh repository/governance state before any P23 supersession or implementation planning.

P20 completion does not itself authorize P21, P23, implementation, `.aegis` persistence, PR #82 reconciliation, merge, release, or rollout.
