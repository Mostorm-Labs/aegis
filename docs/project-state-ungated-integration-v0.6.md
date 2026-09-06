# Aegis Project State Ungated Integration v0.6

Status: **Current Authority v0.6 — P23 Authority Supersession Complete**

Scope: `aegis/project-state`

Previous Authority: `aegis-project-state-v0.5` / `docs/project-state-gate-decision-lineage-v0.5.md` — **Superseded/Historical**

P21 accepted replacement basis: `82103e53354956133f5d1b5d2eb6c7a4f3ed580e` = `PASS / ACCEPTED_FOR_DOWNSTREAM`

Repository baseline at P23 start: `main@3a2607220cd875dc66857b334dcfbd2c763e7c7d`

Primary owner / stage: `aegis-governance -> P23 Authority Supersession`

Triggering finding: `P22-F2 = MISSING_CONTRACT / SPEC_DEFECT`

This document is the canonical Project State v0.6 Authority artifact. It performs the explicit Authority supersession accepted by P21. It preserves v0.5 as immutable historical Authority, assigns the replacement identity/version `aegis-project-state-v0.6`, binds that Authority to the accepted P12-P20 chain, and defines downstream version expectations.

This P23 does **not** implement the v0.6 schema/tooling, does not migrate root `.aegis/*`, does not create the real `int-pr82`, does not retroactively authorize PR #82, and does not merge, release, or expand rollout.

---

# 1. P23 decision

```yaml
p23_authority_supersession:
  scope: aegis/project-state
  finding: P22-F2

  predecessor:
    id: aegis-project-state-v0.5
    version: v0.5
    ref: docs/project-state-gate-decision-lineage-v0.5.md
    status: Superseded/Historical
    historical_provenance_preserved: true
    actionable_for_new_work: false

  replacement:
    id: aegis-project-state-v0.6
    version: v0.6
    ref: docs/project-state-ungated-integration-v0.6.md
    status: Current Authority
    change_class: semantic
    supersedes: aegis-project-state-v0.5

  p21_review:
    exact_ref: 82103e53354956133f5d1b5d2eb6c7a4f3ed580e
    verdict: PASS
    disposition: ACCEPTED_FOR_DOWNSTREAM

  one_current_authority_per_scope: PASS
  earlier_untrusted_layer: none
  blocker: none

  verdict: PASS
  disposition: AUTHORITY_SUPERSESSION_COMPLETE
```

After this P23 decision, the current Project State Authority is `aegis-project-state-v0.6`.

The v0.5 Authority remains available only for historical reconstruction, migration source semantics, and interpretation of occurrences governed while v0.5 was current.

---

# 2. Version designation

P21 intentionally left the replacement version unassigned and required P23 to designate the final Authority identity/version.

P23 assigns:

```yaml
authority_id: aegis-project-state-v0.6
schema_version_target: "0.6"
version: v0.6
change_class: semantic
```

Rationale:

- the current Project State Authority is v0.5;
- the repair changes the Integration binding schema and historical semantics in a backward-incompatible way for v0.5 authored manifests;
- v0.1 through v0.5 already form the existing Project State Authority sequence;
- no existing Project State v0.6 Authority is present in the repository;
- implementation and migration must therefore target the next explicit Project State schema version rather than silently extending v0.5 in place.

The version designation closes `P21-F1`.

No implementation may invent another replacement version label without a new Authority decision.

---

# 3. Accepted replacement Authority basis

The v0.6 Authority incorporates the exact P12-P20 chain accepted by P21:

```yaml
accepted_basis:
  P12_semantic_schema:
    ref: 777e1e8a9652e2cbf220d234798641d65dc9b0c9
    artifact: docs/project-state-p12-ungated-integration-semantic-schema.md

  P13_operation_mutation_model:
    ref: b742ebb9f27520a595b2e73370f42157e28ea72e
    artifact: docs/project-state-p13-ungated-integration-operation-model.md

  P14_plugin_native_architecture:
    ref: cc768db72450b2c9d75a3d9650d447cdbd10048b
    artifact: docs/project-state-p14-plugin-native-targeted-repair.md

  P15_plugin_native_module_design:
    ref: ffa79084c10211668ced1ae6801e238c789ffeb7
    artifact: docs/project-state-p15-plugin-native-minimal-module-design.md

  P16_interaction_evidence_flow:
    ref: 40e094b62f9f3150516f4631ec9df98e6729d258
    artifact: docs/project-state-p16-plugin-interaction-evidence-flow.md

  P17_platform_contract:
    ref: 97efff0e414f17c5667c957f6d497472a6d2459a
    artifact: docs/project-state-p17-plugin-platform-contract.md

  P18_control_plane_optimization:
    ref: 976de3f7729fc2c63a4726458afbe37292f35c17
    artifact: docs/project-state-p18-plugin-control-plane-optimization.md

  P20_verification_design:
    ref: 19b0433a9641847289262a3ad664122c78907569
    artifact: docs/project-state-p20-ungated-integration-verification-design.md

  P21_authority_review:
    ref: 82103e53354956133f5d1b5d2eb6c7a4f3ed580e
    artifact: docs/project-state-p21-ungated-integration-authority-review.md
    verdict: PASS
    disposition: ACCEPTED_FOR_DOWNSTREAM
```

These exact refs are not independent competing Current Authorities. They are the reviewed semantic, architecture, platform, optimization, and verification basis incorporated by this single v0.6 Current Authority.

---

# 4. Superseded candidate preservation

Two earlier architecture candidates remain preserved in repository history:

```yaml
prior_P14:
  ref: 21d6dd535dc7ab50898f7294e73c4bdd98757fc5
  artifact: docs/project-state-p14-ungated-integration-system-architecture.md
  classification: Superseded/Historical candidate
  downstream_authority: false

prior_P15:
  ref: a0eb5ea562af580f21e4d8c6e01d77266c738c0d
  artifact: docs/project-state-p15-ungated-integration-module-design.md
  classification: Superseded/Historical candidate
  downstream_authority: false
```

They are intentionally not deleted or rewritten.

The repaired P14/P15 exact refs are the only architecture/module-design basis incorporated into v0.6.

This closes `P21-F2` without erasing historical design attempts.

---

# 5. Core v0.6 semantic contract

Project State v0.6 replaces v0.5's total Integration-to-Gate-Decision relation with explicit historical Gate Decision Binding.

Canonical meaning:

```text
Integration
  -> Gate Decision Binding
       -> Bound(exact immutable Gate Decision)
       OR
       -> Absent(no_applicable_integration_gate_decision)
```

Canonical authored forms:

```yaml
gate_decision_binding:
  kind: bound
  gate_decision_id: <exact immutable Gate Decision id>
```

or:

```yaml
gate_decision_binding:
  kind: absent
  reason: no_applicable_integration_gate_decision
```

`Absent` is positive historical truth.

The following are never equivalent to `Absent`:

```text
missing field
missing Gate Decision record
failed lookup
empty search
404
permission denied
timeout
pagination incomplete
unresolved decision identity
unknown Authority
persistence lag
```

Ambiguity fails closed.

---

# 6. Preserved v0.5 historical truths

v0.6 preserves the semantic advances introduced by v0.5.

In particular:

```text
Gate Contract
!= Gate Review Decision
!= Current Gate Decision
!= Integration-bound historical Gate Decision
```

Also preserved:

- Gate Decisions are immutable historical decision occurrences;
- later Gate reviews append decisions rather than mutating old verdicts;
- a later PASS never retroactively authorizes an earlier Integration occurrence;
- Integration occurrence is distinct from Gate conformance, current applicability, and current actionability;
- a proven repository occurrence is never erased because governance was missing or violated;
- `state.json` remains generated state, not independent Authority;
- existing v0.5 Gate Decision lineage semantics remain authoritative unless specifically changed by v0.6;
- PR #9 remains historically bound to its original BLOCKED decision even though a later PASS cleared current actionability.

v0.6 is therefore an additive semantic correction to the Integration binding relation, not a rollback of v0.5 lineage semantics.

---

# 7. Status and historical-conformance contract

Status constraints:

```text
awaiting_integration -> Bound only
integrated           -> Bound | Absent
closed_unmerged      -> Bound only
```

Historical conformance for integrated occurrences:

```text
Bound(PASS / PASS_WITH_FINDINGS) -> conforming
Bound(BLOCKED_*)                  -> nonconforming
Absent                            -> nonconforming
```

`Bound(BLOCKED)` and `Absent` are both nonconforming but remain semantically distinct.

The former records an applicable Gate Decision whose verdict did not authorize integration.

The latter records that no applicable integration-relevant Gate Decision existed for the occurrence.

---

# 8. Operation / mutation contract

v0.6 adopts the P13 semantic operation vocabulary:

```text
O1 REGISTER_AWAITING_INTEGRATION
O2 REBIND_AWAITING_INTEGRATION
O3 FINALIZE_INTEGRATION_OCCURRENCE
O4 RECONCILE_HISTORICAL_INTEGRATION_OCCURRENCE
O5 CLOSE_UNMERGED_CANDIDATE
O6 APPEND_CORROBORATING_INTEGRATION_EVIDENCE
```

These names describe legal state changes.

They are **not** required Python APIs, RPC methods, services, dispatchers, or runtime operations.

After an Integration becomes `integrated`, the following historical identity-bearing fields are immutable under normal mutation:

```text
id
kind
ref
target_ref
integrated_revision
gate_decision_binding
```

Normal mutation must reject:

```text
Bound(D1) -> Bound(D2)
Bound(D) -> Absent
Absent -> Bound(D)
Absent -> another reason
integrated_revision rewrite
integrated -> awaiting_integration
integrated -> closed_unmerged
```

O6 may append corroborating evidence without changing historical identity or binding.

---

# 9. Plugin-native architecture remains Authority

Aegis remains a ChatGPT Plugin/Skills control plane.

Canonical ownership:

```text
Aegis Skills
  -> interpret Authority and durable evidence
  -> decide legal lifecycle / Project State semantics

GitHub / Codex / explicitly connected tools
  -> perform authorized repository execution

Git repository
  -> durable persistence

schema / validator / CI
  -> deterministic mechanical verification
```

v0.6 does not authorize or require:

```text
Aegis daemon
autonomous agent runtime
custom harness
background reconciler
repository-state service
transaction server
operation execution engine
internal execution loop
```

P13 operation names must not be used as justification for creating those surfaces.

---

# 10. Platform contract

Platform realization cannot redefine semantic truth.

The following promotions remain forbidden:

```text
GitHub write success -> Authority accepted
Codex reports tests pass -> P34 PASS
CI green -> Gate Decision PASS
repository merge -> merge was Gate-authorized
empty/failed tool search -> Absent
```

Exact durable refs are preferred for historical identity.

Moving refs must be refreshed at semantic and write boundaries.

Uncertain writes must be reconciled by fresh read before retry.

No platform capability gap may be compensated by weakening `Absent` proof requirements.

---

# 11. v0.5 -> v0.6 migration contract

v0.5 remains the canonical migration source for existing Project State repositories that adopt v0.6.

For every legacy v0.5 Integration binding:

```yaml
gate_decision_id: D
```

v0.6 migration must produce exactly:

```yaml
gate_decision_binding:
  kind: bound
  gate_decision_id: D
```

Migration must preserve:

```text
Integration id
kind
ref
status
target_ref
integrated_revision
occurrence evidence
historical decision identity
historical conformance
```

Migration must infer zero `Absent` records from legacy v0.5 state.

A historical `Absent` record may be added only through an explicit legal historical reconciliation such as P13 O4 with accepted occurrence and absence basis.

---

# 12. PR #82 canonical historical oracle

PR #82 is the exposing occurrence for this Authority repair.

Durable occurrence basis:

```yaml
repository: Mostorm-Labs/aegis
pr: 82
merged: true
integrated_revision: 3a2607220cd875dc66857b334dcfbd2c763e7c7d
```

Durable non-authorization evidence:

```yaml
p23_review: 5122113780
pr_82_merge_authorized_by_this_review: false
```

Durable absence-governance basis:

```yaml
p22_review: 5553423707
finding: P22-F2
```

That P22 review established that no separate P24/P34 integration-authorizing Gate Decision for PR #82 was durably created before the occurrence.

Therefore the future legal Project State representation, once v0.6 implementation and persistence are authorized and qualified, is:

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
```

with:

```text
historical_conformance = nonconforming
```

This P23 does not itself create that record.

This P23 also does not create a Gate Decision for PR #82 and does not reinterpret `5122113780` as merge authorization.

---

# 13. Verification Authority

The v0.6 implementation must satisfy P20 exact ref:

```text
19b0433a9641847289262a3ad664122c78907569
```

Mandatory evidence groups remain:

```text
V1  Gate Decision Binding representation
V2  status x binding constraints
V3  Absent non-inference
V4  historical conformance projection
V5  historical immutability
V6  occurrence-time binding / later PASS
V7  lossless v0.5 migration
V8  P13 state-transition legality
V9  Plugin-native / forbidden-runtime boundary
V10 platform-result authority separation
V11 PR #82 historical absence oracle
V12 deterministic replay / idempotency
V13 stale-basis / uncertain-write safety
V14 resume / exact-ref optimization safety
```

Missing core proof is Gate-blocking.

In particular:

```text
missing PR #82 historical absence proof
-> BLOCKED_EVIDENCE
```

not `PASS_WITH_FINDINGS`.

---

# 14. Current Authority versus implementation reality

P23 changes design/governance Authority now.

It does not claim implementation has already caught up.

At P23 completion:

```yaml
current_design_authority:
  id: aegis-project-state-v0.6
  status: Current

repository_implementation_reality:
  root_project_state_schema: "0.5"
  v0_6_schema_materialized: false
  v0_6_tooling_materialized: false
  v0_6_skill_contract_materialized: false
  int_pr82_persisted: false
```

This difference is expected downstream implementation/persistence drift, not permission to treat v0.5 as Current Authority for new work.

The root `.aegis/authorities.json` may still physically identify v0.5 as Current until the later authorized Project State persistence change is made. After this P23 decision, that manifest state is stale implementation/persistence reality for this scope and must not override the newer P23 Authority decision.

No downstream package may use that stale root entry to reactivate v0.5 as design Authority.

---

# 15. P22 finding disposition

## P22-F2 — Authority contract defect

```yaml
id: P22-F2
class: MISSING_CONTRACT
secondary: SPEC_DEFECT
prior_status: BLOCKED_AUTHORITY
post_P23_status: CLOSED_AT_AUTHORITY_LAYER
repair_authority: aegis-project-state-v0.6
```

The missing contract is now resolved at the Authority layer by v0.6.

## P22-F1 — Project State persistence drift

```yaml
id: P22-F1
class: STATE_PERSISTENCE_DRIFT
secondary: IMPLEMENTATION_DEFECT
prior_status: BLOCKED_BY_P22-F2
post_P23_status: UNBLOCKED_FOR_DOWNSTREAM_REPAIR
resolved: false
```

P22-F1 is not fixed merely because Authority is now correct.

It becomes eligible for downstream implementation/persistence work once v0.6 implementation is planned, packaged, executed, and independently Gate-qualified.

The real root migration/reconciliation must not run ahead of the v0.6 verification contract.

---

# 16. Downstream dependency and version expectations

All new work in `aegis/project-state` must resolve Project State Authority as:

```yaml
current_authority:
  id: aegis-project-state-v0.6
  version: v0.6
  ref: docs/project-state-ungated-integration-v0.6.md

superseded_authority:
  id: aegis-project-state-v0.5
  version: v0.5
  ref: docs/project-state-gate-decision-lineage-v0.5.md
```

For new implementation planning, packaging, execution, and Gate review:

```yaml
required_authority:
  project_state: aegis-project-state-v0.6
  semantic_basis: 777e1e8a9652e2cbf220d234798641d65dc9b0c9
  operation_basis: b742ebb9f27520a595b2e73370f42157e28ea72e
  architecture_basis: cc768db72450b2c9d75a3d9650d447cdbd10048b
  module_basis: ffa79084c10211668ced1ae6801e238c789ffeb7
  flow_basis: 40e094b62f9f3150516f4631ec9df98e6729d258
  platform_basis: 97efff0e414f17c5667c957f6d497472a6d2459a
  optimization_basis: 976de3f7729fc2c63a4726458afbe37292f35c17
  verification_basis: 19b0433a9641847289262a3ad664122c78907569
  p21_review: 82103e53354956133f5d1b5d2eb6c7a4f3ed580e
```

Fallback to v0.5 for new implementation semantics is forbidden.

v0.5 remains valid only as:

- superseded historical Authority;
- migration source contract;
- interpretation basis for historical occurrences governed while v0.5 was current.

---

# 17. Implementation boundary after P23

P23 makes v0.6 the Current Authority but authorizes no code by itself.

The next implementation lifecycle must begin from planning rather than ad hoc edits.

Expected implementation scope, subject to P30/P31 packaging, is bounded to the surfaces accepted by P15/P20:

```text
skillset/skills/aegis-project-state/SKILL.md
skillset/skills/aegis-project-state/references/project-state.md
skills/aegis-project-state/SKILL.md
skills/aegis-project-state/references/project-state.md
schemas/project-state/v0.6/**
examples/project-state/v0.6/**
existing deterministic validator / projection paths as mechanically necessary
existing migration utility/pattern for v0.5 -> v0.6
existing transition validation where required
.github/workflows/project-state.yml only as verification requires
tests/project_state/**
relevant Skill/eval fixtures
```

Implementation is expected **not** to add:

```text
tools/aegis_state/integration_ops.py
tools/aegis_state/transaction.py
new required transition dispatcher service
integration-history service
Aegis daemon
agent runtime
custom harness
background reconciler
```

A tiny pure helper may be introduced only if implementation evidence shows it materially simplifies deterministic validation and it has no orchestration or Authority role.

---

# 18. Root persistence / migration boundary

The root repository currently remains schema v0.5.

P23 does not migrate it.

The safe lifecycle is:

```text
P23 v0.6 Current Authority
  -> P30 implementation planning
  -> P31 bounded package(s)
  -> P32 implementation of v0.6 support
  -> P34 independent Gate against P20
  -> only after qualified support exists:
       root v0.5 -> v0.6 persistence/migration
       explicit PR #82 O4 historical reconciliation
       deterministic validation / CI
```

The exact packaging of root migration/reconciliation may be defined by P30/P31, but the real authored Project State must not be migrated to v0.6 before the code/schema/Skill support required to validate it has passed the v0.6 Gate.

This boundary prevents the control repository from making itself unreadable or unverifiable by adopting a schema before its supporting implementation is qualified.

---

# 19. Historical Authority preservation

The following remain immutable historical sources:

- `aegis-project-state-v0.1` through `v0.5` Authority artifacts;
- all historical Gate decisions and evidence associated with those versions;
- PR #9's original blocked Gate Decision and nonconforming Integration occurrence;
- PR #82's P23 review `5122113780` and repository merge occurrence;
- P22 review `5553423707` exposing the v0.5 contract defect;
- superseded runtime-oriented P14/P15 candidate artifacts.

No historical FAIL becomes PASS.

No historical non-authorization becomes authorization.

No old artifact is rewritten to make v0.6 easier to implement.

---

# 20. P23 acceptance criteria

P23 is complete only if all of the following are true:

1. P21 exact review `82103e53354956133f5d1b5d2eb6c7a4f3ed580e` remains PASS / ACCEPTED_FOR_DOWNSTREAM;
2. the reviewed P12-P20 exact chain is unchanged;
3. no earlier Product/Semantic/Architecture/Verification contradiction appears;
4. v0.5 is preserved as immutable historical Authority;
5. the replacement identity/version is explicitly assigned as `aegis-project-state-v0.6` / v0.6;
6. exactly one Current Authority exists conceptually for `aegis/project-state` after P23: v0.6;
7. old runtime-oriented P14/P15 candidates remain historical only;
8. PR #82's Absent meaning remains distinct from Authority promotion;
9. P22-F2 closes only at the Authority layer, while P22-F1 remains an unresolved downstream persistence defect;
10. no implementation or root `.aegis` migration is smuggled into P23;
11. downstream implementation is required to bind v0.6 and P20 exact evidence expectations;
12. merge/release/rollout remain outside this P23.

All criteria are satisfied by this materialization.

---

# 21. Formal disposition

```yaml
project_state_v0_6_p23:
  scope: aegis/project-state

  authority_transition:
    from:
      id: aegis-project-state-v0.5
      status: Superseded/Historical
    to:
      id: aegis-project-state-v0.6
      version: v0.6
      status: Current Authority
      ref: docs/project-state-ungated-integration-v0.6.md

  accepted_p21:
    ref: 82103e53354956133f5d1b5d2eb6c7a4f3ed580e
    verdict: PASS
    disposition: ACCEPTED_FOR_DOWNSTREAM

  p22_findings:
    P22-F2: CLOSED_AT_AUTHORITY_LAYER
    P22-F1: UNBLOCKED_FOR_DOWNSTREAM_REPAIR

  implementation_materialized: false
  root_schema_migrated: false
  project_state_persisted_to_v0_6: false
  pr82_reconciled: false
  merge_performed: false
  release_performed: false

  earlier_untrusted_layer: none
  blocker: none

  verdict: PASS
  disposition: AUTHORITY_SUPERSESSION_COMPLETE
```

---

# 22. Stop boundary / handoff

P23 stops at Authority supersession.

It does not execute implementation planning or any repository-state mutation beyond this governance artifact.

The next legal substantive stage is:

```text
aegis-implementation -> P30 Implementation Planning
```

P30 must plan the smallest v0.6 implementation that satisfies the P20 verification design and the Plugin-native P14/P15 boundary.

P23 does not authorize direct P32 execution, real `.aegis` v0.6 migration, PR #82 O4 reconciliation, merge, release, or rollout.
