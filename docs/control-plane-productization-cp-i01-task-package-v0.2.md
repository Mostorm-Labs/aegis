# Aegis Control Plane Productization v0.2 — CP-I01 P31 Task Package

Status: **P31 READY / MATERIALIZED — authorized package for later P32 execution**

Package ID: `CP-I01-P31-01`

Owner: `aegis-implementation`

Current stage: `P31 Task Packaging`

Target execution stage: `P32 Implementation`

Current execution surface: `CONTROL_REASONING`

Preferred later execution surface: `CODE_EXECUTION`

Preferred later executor profile: `codex`

This artifact is a bounded implementation package. It does not itself begin P32, execute code, issue Evidence/ProofEvaluation, or produce a P34 Gate verdict.

---

# 1. Exact package trust anchor

Repository:

`Mostorm-Labs/aegis`

P30 materialized head:

`87cbb166411795261ec5f6e7034a89435e053451`

Required repository ancestry contract for later P32:

```yaml
task_anchor:
  revision: 87cbb166411795261ec5f6e7034a89435e053451
  relation: ancestor
resume_cursor: null
```

`Task Anchor != Execution Cursor` remains controlling.

The P32 executor MUST establish that the accepted starting revision descends from this anchor. It MUST NOT require HEAD to equal this historical revision when ancestry is valid.

A later accepted P33 continuation point may introduce a `resume_cursor`; this initial package does not have one.

---

# 2. Exact Authority basis

P32 is authorized only against the exact accepted chain below.

## Product

- head: `c628bdc15fdd3d32511a04b6f09055413f2786c3`
- review: `5061188138`
- disposition: `PASS / ACCEPTED_FOR_DOWNSTREAM`

## Modeling

- head: `f29c4da3698038e0174e4380707fa618b03c40b2`
- review: `5062616510`
- disposition: `PASS / ACCEPTED_FOR_DOWNSTREAM`

Required semantic sources include the combined accepted P10-P13 package, especially:

- `docs/control-plane-productization-schema-v0.2.md`
- `docs/control-plane-productization-operations-v0.2.md`
- the accepted P21 modeling repair amendments

## Architecture

- head: `e657f0e74771184b98f8c8e6f8a8581e4858c82d`
- review: `5062769390`
- disposition: `PASS / ACCEPTED_FOR_DOWNSTREAM`

## Verification

- accepted P20 head: `db83168e4086e47a7f431acf289006e4f25b8ffd`
- review: `5062933855`
- disposition: `PASS / ACCEPTED_FOR_DOWNSTREAM`

Combined normative P20 package:

1. `docs/control-plane-productization-verification-v0.2.md`
2. `docs/control-plane-productization-verification-v0.2-p21-repair.md`

Repair blob:

`5bed0ce054ead0902bc8c72601814b2f63525067`

## Implementation Plan

- P30 artifact: `docs/control-plane-productization-implementation-plan-v0.2.md`
- exact P30 materialized head: `87cbb166411795261ec5f6e7034a89435e053451`
- selected slice: `CP-I01 — Independent proof foundation + canonical semantic spine`

## Retained Current external contracts

The package must preserve the Current repository contracts already present at the task anchor, including:

- `docs/skill-decomposition-v0.2.md`
- `docs/execution-surface-contract-v0.2.md`
- Project State v0.5 registry semantics in `.aegis/**`

These are consumed as constraints. This package does not supersede them.

---

# 3. Package purpose

Implement the first vertical slice required by P30:

> Create the smallest executable canonical semantic/reference foundation that later Control Plane runtime code can be independently checked against, without using production control flow as its own correctness oracle.

The package must establish a trustworthy **proof spine before runtime orchestration complexity**.

The required shape is:

```text
accepted P12/P13 semantics
  -> canonical representation / validation primitives
  -> independent semantic reference oracles
  -> independent completeness oracle
  -> independent verifier qualification corpus
  -> exact reproducible evidence output
```

This slice does not attempt to implement the Control Service.

---

# 4. Authorized implementation scope

P32 may implement only the following bounded capabilities.

## 4.1 Production/shared semantic primitives

Create an isolated Control Plane namespace for pure semantic primitives, for example under:

```text
tools/aegis_control/
```

Authorized responsibilities:

- P12 canonical value/type representation needed by this slice;
- accepted canonical enums/status/reason identities needed by reference tests;
- exact `CanonicalRef` structural representation/validation;
- RFC 8785 canonical JSON semantics required by P12;
- SHA-256 canonical digest calculation/verification;
- deterministic sorting/normalization required by accepted digest rules;
- pure structural validation that requires no database/network/provider access;
- explicit failure on malformed/unknown trust-sensitive canonical input.

This shared semantic layer may expose canonical primitives to independent test oracles, but it MUST NOT contain production scheduler/mutation/policy/store control flow.

## 4.2 Independent `O-CRM` reference model

Create a deliberately small deterministic reference interpreter under a test/reference-only namespace, for example:

```text
tests/control_plane/reference_model.py
```

It must model only enough semantic truth to determine expected outcomes for accepted Control Plane invariants, including:

- legal/illegal P13 transition shape;
- immutable StageOccurrence/package/escalation revision lineage;
- lane head and predecessor expectations;
- semantic idempotency replay/conflict expectation;
- commit-before-dispatch expectation as semantic trace ordering;
- one-occurrence transport retry vs new semantic attempt;
- one terminal revision;
- terminal/successor separation;
- REQUIRED-child barrier legality and expected exact acceptance-binding shape;
- repair/reverify/rereview as separate governed occurrence identity;
- Current rollout denial expectation;
- `Task Anchor != Execution Cursor` / P33 classification expectations where represented by fixtures;
- projection expected-state derivation required for semantic fixture comparison.

`O-CRM` MUST NOT import or call future/current production scheduler, mutation, projection, policy, dispatch, recovery, or service control-flow functions to compute expected truth.

Allowed shared imports are limited to canonical enum/schema definitions and canonical encoding/digest primitives whose behavior is independently covered by golden vectors.

## 4.3 Independent `O-COMPLETE`

Create an independent CoverageBasis/obligation completeness checker under a test/reference-only namespace.

It must independently derive/validate the expected semantic obligation identity set for the accepted combined P20 source and detect at least:

- one omitted Claim obligation;
- omitted mandatory `COVERAGE_COMPLETENESS` obligation;
- duplicate obligation ID;
- extra unknown obligation;
- changed semantic source key;
- evaluated strict subset/superset of the bound obligation set.

For `CoverageBasis.mode = REVIEW_DECLARED`, the expected set must include exactly one mandatory `COVERAGE_COMPLETENESS` review obligation.

`O-COMPLETE` MUST NOT call the execution-side obligation generator to derive expected truth.

## 4.4 Independent verifier qualification helpers

Provide test-only independent verifier helpers needed to seed and detect the mandatory `M01-M20` corpus.

The package may implement test/reference-only helpers for:

- semantic trace mutation detection for M01-M15;
- `O-SNAPSHOT` token-integrity/binding verification fixtures for M16-M18;
- async-provider capability classification fixture for M19;
- full-canonical-bytes vs truncated-transport comparison for M20.

These helpers are verifier/reference tooling only. They do not implement the real external provider adapter or production dispatch/runtime path owned by later slices.

## 4.5 Fixture / mutant catalog

Create a deterministic catalog representing the identities and required expected outcomes for:

```text
G01-G44
M01-M20
```

For CP-I01, the G01-G44 catalog must be structurally representable and addressable by stable IDs. It is **not** required to claim that the full production SUT passes all G01-G44; integrated D0 execution belongs to CP-I08 after later runtime slices exist.

M01-M20 verifier qualification **is required in this slice**: the independent verifier stack must detect all mandatory seeded mutants without false acceptance.

## 4.6 Exact evidence manifest plumbing

Provide a deterministic test/evidence manifest writer for CP-I01 qualification outputs. It must record at least:

- exact implementation/result revision when run in CI;
- exact P20 source identities;
- exact task package identity/ref supplied by the workflow;
- test command(s);
- Python/runtime version;
- fixture catalog digest;
- mutant catalog digest;
- deterministic seed list, if randomized/property traces are used;
- qualification totals;
- false-acceptance totals;
- canonical golden-vector digest;
- individual M16-M18 mutated token bytes/binding tuple identity sufficient for reviewer reproduction;
- M20 full canonical input digest and attempted truncated representation digest/identity.

The manifest is evidence material, not Authority, ProofEvaluation, or Gate truth.

## 4.7 Dedicated CI path

P32 may add one narrowly scoped GitHub Actions workflow, for example:

```text
.github/workflows/control-plane-foundation.yml
```

The workflow must:

- trigger only for the CP-I01 implementation/test paths and itself;
- use the repository's established Python 3.12 / `unittest` style unless a justified repository-local alternative is needed;
- run the CP-I01 foundation tests;
- materialize the exact qualification/evidence manifest as a durable Actions artifact or equivalent reviewer-resolvable artifact;
- fail if M01-M20 detection is not 20/20 or any false acceptance is nonzero.

CI success is an observation/evidence producer only. It is not P34 Gate PASS.

---

# 5. Authorized repository paths

P32 may create/modify only the following path families unless a narrower implementation chooses fewer files:

```text
tools/aegis_control/**
tests/control_plane/**
.github/workflows/control-plane-foundation.yml
```

If a tiny repository-level test discovery/configuration adjustment is strictly necessary to make the isolated CP-I01 suite executable, the executor must stop and report the exact proposed path/change before widening scope unless the change is purely additive and does not alter existing test semantics.

The following are explicitly outside authorized scope:

```text
.aegis/**
skills/**
skillset/**
plugins/**
tools/aegis_state/**
tools/aegis_skillset/**
tests/project_state/**
tests/skillset/**
docs/control-plane-productization-*.md
```

The P31 package document itself may remain unchanged during P32.

---

# 6. Explicit non-goals

P32 MUST NOT implement or modify any of the following in CP-I01:

- `control-store` production persistence;
- `control-mutation` production writer;
- production projection/policy/scheduler;
- transactional outbox runtime;
- dispatch/reconciliation worker;
- production external-provider adapters;
- Control Service public/internal HTTP API;
- Aegis Control App;
- real HUMAN_DECISION provider integration;
- repair/recovery runtime;
- R0/S0 benchmark runtime;
- seven-day cost execution;
- monthly availability evidence;
- P34 review/verdict logic;
- Current Skill Decomposition changes;
- Current Execution Surface changes;
- `.aegis` Authority/Gate/Evidence/Integration mutation;
- Proof Plane canonical store or a second Evidence/ProofEvaluation database.

Do not implement CP-I02 or later slices opportunistically.

---

# 7. Required semantic invariants

The CP-I01 implementation must mechanically preserve these invariants.

## Canonical representation

1. Canonical semantic records use UTF-8 JSON semantics.
2. Canonical digest = RFC 8785 JCS + SHA-256.
3. Digest text uses `sha256:<64 lowercase hex>`.
4. The field storing a record's own digest is excluded only from that same digest where accepted P12 semantics require it.
5. Unknown authored top-level canonical fields are rejected unless represented through the accepted namespaced `extensions` mechanism.
6. Stable IDs remain stable across immutable revisions; `record_revision` is monotonic by exactly one in represented lineages.
7. UUID timestamp bits never become lifecycle order/trust truth.

## Ownership/trust

8. Canonical/reference helpers do not synthesize Authority/Gate/Proof/Integration truth.
9. P34 remains the sole official Gate owner.
10. ProofEvaluation/CI/provider success is never interpreted as Gate PASS.
11. Current cross-Primary rollout denial remains part of the expected semantic oracle.
12. A Primary never gains authority to execute another Primary's substantive stage.

## Execution/navigation

13. `Task Anchor != Execution Cursor`.
14. Valid descendant execution positions are not rejected merely because they differ from a historical anchor SHA.
15. `EXACT_CURSOR`, `DESCENDANT_CURSOR`, `ANCHOR_DESCENDANT_WITHOUT_CURSOR`, and `DIVERGED` remain distinct expected classifications.

## Independent proof

16. Production/shared canonical primitives may be shared only where P20 explicitly permits shared canonical identity/encoding definitions.
17. `O-CRM` cannot reuse production control-flow functions as expected truth.
18. `O-COMPLETE` cannot reuse execution-side obligation generation to derive expected truth.
19. `O-SNAPSHOT` cannot use production scheduler/mutation acceptance success as its validity oracle.
20. Silent canonical truncation before digest/acceptance is always rejected.

---

# 8. Required verifier qualification corpus

The package binds exactly the accepted mandatory mutants.

## M01-M15

```text
M01 dispatch before OPEN/outbox commit
M02 retry creates a second StageOccurrence
M03 second canonical writer bypasses control-mutation
M04 stale snapshot accepted after provider version change
M05 REQUIRED child barrier crossed without acceptance binding
M06 historical acceptance inferred from current boolean projection
M07 terminalization and successor collapsed into one cross-owner transition
M08 worker restart creates semantic retry
M09 P34/Gate PASS inferred from CI/ProofEvaluation
M10 Execution Cursor treated as Authority/scope truth
M11 unauthorized cross-Primary auto-dispatch despite rollout denial
M12 projection cache authorizes mutation after canonical change
M13 outbox loss after acknowledged schedule commit
M14 unsafe manual fallback duplicates active controlled work
M15 late conflicting terminal result rewrites history
```

## M16-M20

```text
M16 SourceSnapshotToken payload is modified but verifier accepts original integrity tag
M17 SourceSnapshotToken from wrong adapter/source-kind is accepted at another trust boundary
M18 SourceSnapshotToken with mismatched provider resource/version binding is accepted as valid current support
M19 callback-only async provider is classified as full autonomous trust-sensitive capability
M20 canonical representation is silently truncated before digest/acceptance and verifier fails to detect it
```

Mandatory qualification threshold:

```text
M01-M20 detected = 20/20
false ACCEPT/PASS on mandatory mutant corpus = 0
```

For M16-M18, evidence must retain exact mutated token bytes/binding tuple. A generic invalid-token test is insufficient.

For M20, evidence must compare the full canonical source bytes/digest against the size-limited/truncated representation.

---

# 9. G01-G44 fixture catalog obligation

CP-I01 must provide stable catalog identities and expected-outcome metadata for all accepted D0 scenarios:

```text
G01-G44
```

The catalog must preserve the exact accepted scenario meanings from the combined P20 package.

CP-I01 is responsible for:

- stable IDs;
- deterministic fixture schema/representation;
- exact expected-oracle metadata;
- fixture/corpus digest;
- enough seed/mutation representation to qualify independent verifiers.

CP-I01 is **not** authorized to claim the integrated runtime passes G01-G44. The full:

```text
G01-G44 = 44/44 PASS
```

requirement belongs to CP-I08 after CP-I02..CP-I07 are implemented.

---

# 10. Required tests

At minimum, add isolated `unittest`-compatible coverage for the following groups.

## Canonical semantics

- deterministic canonical JSON golden vectors;
- map/object key ordering;
- UTF-8 / string escaping cases required by RFC 8785;
- accepted numeric canonicalization cases used by Control Plane schemas;
- digest determinism;
- self-digest-field exclusion behavior where applicable;
- unknown top-level field rejection;
- exact CanonicalRef validation;
- immutable revision lineage structural checks;
- no silent truncation before digest.

## O-CRM independence and behavior

- representative legal/illegal transition traces;
- semantic retry vs delivery retry identity;
- one terminal revision;
- terminal/successor separation;
- REQUIRED-child barrier cases;
- stale/current historical-basis expectations;
- Current rollout denial;
- P33 four-state expected classification fixtures.

Include an architectural dependency test/static import check that fails if the reference model imports production control-flow modules outside the explicitly allowed canonical primitive set.

## O-COMPLETE

- exact accepted obligation set;
- omitted Claim obligation;
- omitted CoverageBasis obligation;
- duplicate obligation;
- extra unknown obligation;
- changed semantic source key;
- strict subset/superset evaluation set.

Include a dependency/static import check that fails if the completeness oracle imports the execution-side obligation generator for expected-set derivation.

## Snapshot/capability/truncation verifier helpers

- valid control token/binding case;
- M16 exact payload mutation;
- M17 wrong adapter/source kind;
- M18 wrong resource/version/currentness;
- M19 callback-only capability classification;
- M20 full-vs-truncated canonical bytes/digest.

## Qualification runner

- every M01-M20 is present exactly once as a mandatory mutant identity;
- all 20 seeded mutants are detected;
- false acceptance count = 0;
- evidence manifest contains exact required provenance fields;
- deterministic repeat run yields same corpus/catalog digests for the same source/seed inputs.

---

# 11. Required test commands

The implementation should preserve the repository's existing Python 3.12 / stdlib-unittest convention.

Required focused command:

```text
python3 -m unittest discover -s tests/control_plane -v
```

Required existing-regression commands before return:

```text
python3 -m unittest discover -s tests/project_state -v
python3 -m unittest discover -s tests/skillset -v
```

If the executor discovers another repository-mandatory integrity command from current CI, it should run it when the CP-I01 changes can affect that contract, but it must not widen implementation scope merely to make unrelated historical tests pass.

---

# 12. Required EvidenceArtifacts / durable evidence outputs

P32 must produce reviewer-resolvable durable support for the following CP-I01 evidence families:

1. `CPV-E-SPEC`
   - exact P20 source/materialization identity used by the package.
2. `CPV-E-COMPLETENESS`
   - independent completeness-checker qualification/result for the bound obligation set.
3. `CPV-E-VERIFIER-QUALIFICATION`
   - M01-M20 detection = 20/20; false acceptance = 0; exact mutant provenance.
4. `CPV-E-OBLIGATIONS`
   - only if this slice materializes a complete deterministic obligation identity set without inventing a second Proof Plane store.

`CPV-E-D0-CONFORMANCE` is **not** complete in CP-I01 and must not be falsely emitted as integrated D0 PASS.

Evidence artifacts must be exact and independently resolvable. Dashboard/console prose alone is insufficient.

Every artifact later consumed by ProofEvaluation must be capable of being bound through exact `EvidenceInputRef` identity under the accepted Proof Plane semantics.

---

# 13. Performance / engineering constraints

CP-I01 has no R0/S0 throughput pass claim.

The following constraints still apply:

- deterministic/reproducible verifier execution is more important than micro-optimization;
- avoid dependencies on network/provider availability in focused qualification tests;
- no benchmark number produced here may be represented as R0/S0 or seven-day evidence;
- no monthly availability claim is permitted;
- implementation complexity must not blur independent-oracle boundaries.

---

# 14. Required P32 executor workflow

When P32 is later authorized, the code execution surface must:

1. inspect current repository HEAD/branch/diff before edits;
2. verify the task anchor `87cbb166...` is an ancestor of the accepted starting revision;
3. record the actual starting revision;
4. inspect this exact P31 package and exact Authority refs;
5. fail closed on Authority ambiguity or scope conflict;
6. implement only authorized CP-I01 paths;
7. run focused tests;
8. run required existing regression tests;
9. push/materialize the exact result to a reviewer-accessible remote branch/PR;
10. obtain durable CI/evidence refs where required;
11. return the compact evidence contract in §15.

P32 may use normal coding mechanics/TDD/debugging, but those mechanics do not expand Aegis Authority or package scope.

---

# 15. Required P32 return contract

The executor must return a compact machine-readable-equivalent result containing at least:

```yaml
task_id: CP-I01-P31-01
package_ref: <exact P31 materialized ref>
task_anchor:
  revision: 87cbb166411795261ec5f6e7034a89435e053451
  relation: ancestor
starting_revision: <actual accepted P32 start revision>
result_revision: <exact result commit>
materialized_ref: <reviewer-accessible branch/PR/result ref>
changed:
  - <paths>
verification:
  focused_command: python3 -m unittest discover -s tests/control_plane -v
  focused_result: PASS | FAIL
  mutant_detection: <N>/20
  false_acceptance: <N>
regression:
  project_state: PASS | FAIL | NOT_APPLICABLE_WITH_REASON
  skillset: PASS | FAIL | NOT_APPLICABLE_WITH_REASON
evidence:
  - <exact durable CPV-E-* refs / CI artifacts>
authority_deviation: none | <exact blocker>
scope_deviation: none | <exact blocker>
blocker: none | <classified blocker>
```

The result is not review-ready without a reviewer-accessible `materialized_ref`.

A local-only commit/worktree/test transcript is insufficient.

---

# 16. Exit criteria

CP-I01 may return from P32 as implementation-complete only if all of the following are true:

1. Actual starting revision satisfies the `task_anchor` ancestry relation.
2. Changes remain inside the authorized path/scope boundary.
3. Canonical serialization/digest primitives pass deterministic golden tests.
4. `O-CRM` independent reference implementation exists and passes its focused suite.
5. `O-COMPLETE` independent checker exists and rejects every seeded completeness defect.
6. G01-G44 fixture catalog identities/expected metadata are complete and deterministic.
7. M01-M20 mandatory mutants are all represented and detected:

```text
20/20 detected
0 false acceptance
```

8. M16-M18 evidence includes exact mutated token/binding provenance.
9. M20 proves full canonical bytes/digest cannot be silently replaced by a truncated representation.
10. Focused `tests/control_plane` suite passes.
11. Existing Project State and Skillset regression suites remain green, or an unrelated pre-existing failure is reported exactly without being silently fixed outside scope.
12. Exact result is pushed/materialized at a reviewer-accessible durable ref.
13. Required exact evidence/CI refs are returned.
14. No `.aegis`, Skill Decomposition, Execution Surface, Project State, existing Skill implementation, or upstream Authority mutation occurred.
15. No CP-I02+ runtime functionality was implemented.

These criteria make the result eligible to return to `CONTROL_REVIEW`; they do not issue P34 PASS.

---

# 17. Blocked return behavior

P32 must stop without inventing a design if any of the following occurs.

## Earlier Authority defect

Examples:

- accepted P12 semantics cannot be represented deterministically without contradictory interpretations;
- exact P20 obligation identity/completeness semantics are insufficient to derive an independent expected set;
- M01-M20 required verifier expectation conflicts with accepted Product/Model/Architecture semantics.

Return:

```text
BLOCKED_AUTHORITY
```

with exact earliest untrusted layer and contradictory refs.

Do not repair Product/Model/Architecture/P20 inside CP-I01.

## Execution divergence

If task-anchor ancestry cannot be established or observed history contradicts package scope/Authority:

```text
BLOCKED_EXECUTION_DIVERGENCE
```

Do not force-reset or discard valid work.

## Evidence materialization failure

If code/tests exist but exact result/evidence cannot be made reviewer-accessible:

```text
BLOCKED_EVIDENCE
```

Do not claim review readiness from a local commit or transcript.

## Environment blocker

If the authorized tests cannot execute because of an external environment/tooling limitation unrelated to semantic design:

```text
BLOCKED_ENVIRONMENT
```

with exact failed command/capability and preserved valid modifications.

## Scope pressure

If implementation appears to require edits outside the authorized path families or CP-I02+ runtime behavior, stop and return the exact scope need. Do not silently expand the package.

---

# 18. Future surface handoff prepared by this package

After P31 is accepted and the user starts P32, the intended handoff is:

```yaml
type: surface_handoff
stage: P32
stage_owner: aegis-implementation
from_surface: CONTROL_REASONING
to_surface: CODE_EXECUTION
preferred_executor: codex
reason: repository_heavy_execution
package_ref: <exact commit/ref containing this P31 package>
task_anchor:
  revision: 87cbb166411795261ec5f6e7034a89435e053451
  relation: ancestor
resume_cursor: null
return_surface: CONTROL_REVIEW
```

The surface handoff changes execution location only. `aegis-implementation` remains the P32 stage owner.

This document does **not** execute that handoff.

---

# 19. P31 disposition

This package authorizes exactly one implementation slice:

```text
CP-I01 — Independent proof foundation + canonical semantic spine
```

No upstream Authority gap was found during packaging.

Therefore after exact repository materialization of this document:

```text
P31 Task Packaging = READY / MATERIALIZED
next stage = P32 Implementation
next surface = CODE_EXECUTION
preferred executor = Codex
```

Stop after P31 materialization. Do not begin P32 in the same control occurrence.
