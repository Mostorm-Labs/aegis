# Aegis Execution Surface Verification v0.2 — Repository Identity Materialization Proof Repair

Status: **Draft / Proposed targeted P20 Verification Design amendment**

Scope: `aegis/execution-surface/repository-identity/verification/materialization`

Upstream Current / accepted basis:

- P17 repository-identity Platform Contract: `e851531a000c5c84ee2f00b429d813c048d29ab8`
- targeted repository-identity Verification Authority before this repair: `61aa42e98558a1621b0228223835473f248ee869`
- P23 supersession review: `5109528560`
- repository baseline: `main@212f1d7dcb2c31162f0f64946a4473912578c5d9`
- P30 short-circuit blocker: PR #58 comment `5536216853`

This amendment repairs only the proof-materialization boundary exposed during repository-identity P30 planning. It does not change the P17 repository-identity contract, the required scenarios, negative qualification, Codex platform observations, release version, Product form, or RC-I01 release-package scope.

---

## 1. Triggering verification conflict

The accepted repository-identity P20 requires repository safety semantics to be consistent across canonical shared contracts, canonical specialist Skills, generated/distributed Skills, and Plugin materialization.

The repository currently also preserves the published `0.1.0-beta.3` Plugin as an immutable release-bound materialization. Its release manifest freezes exact Skill tree digests, and the current Plugin materialization checker validates those frozen digests before accepting the committed Plugin tree.

Updating `aegis-implementation`, `aegis-gate-review`, or shared handoff semantics therefore necessarily changes current canonical Skill digests. Requiring the repaired candidate to overwrite or continue matching the committed `0.1.0-beta.3` Plugin would force one of two invalid outcomes:

1. mutate historical `0.1.0-beta.3` release identity/digests; or
2. prematurely materialize the separate `0.2.0-beta.1` RC-I01 release package.

Neither is authorized by the repository-identity repair.

Classification:

```yaml
class: AUTHORITY_CONFLICT
owning_stage: P20_VERIFICATION_DESIGN
conflict:
  repository_identity_plugin_parity_proof: REQUIRED
  immutable_beta3_release_binding: REQUIRED
  rc_i01_release_materialization_separation: REQUIRED
resolution_needed: proof_materialization_boundary
```

---

## 2. Corrected proof invariant

Repository-identity verification distinguishes two materially different artifacts:

### A. Published release materialization

A committed, version-bound Plugin tree governed by a release manifest and public release identity.

For `0.1.0-beta.3`:

```yaml
artifact_class: PUBLISHED_RELEASE_MATERIALIZATION
release_version: 0.1.0-beta.3
mutation_by_repository_identity_repair: FORBIDDEN
historical_digest_binding: PRESERVE
```

### B. Candidate Plugin parity artifact

A reviewer-resolvable, exact-revision, non-published Plugin-shaped evidence artifact generated only to prove that the repaired canonical/generated Skills can be materialized into the Plugin surface without losing repository-identity semantics.

```yaml
artifact_class: CANDIDATE_PLUGIN_PARITY_EVIDENCE
public_release: false
release_tag: null
release_manifest_authority: none
source_revision: <exact implementation result>
reviewer_resolvable: REQUIRED
publication_authority: false
```

The candidate artifact is evidence, not a release.

Therefore the corrected invariant is:

> Current candidate canonical Skills == generated/distributed Skills == candidate Plugin parity artifact, while already-published release materializations remain immutable historical release artifacts.

This replaces any interpretation that the repository-identity repair must rewrite the committed `0.1.0-beta.3` Plugin tree before RC-I01.

---

## 3. Repair to `RIR-R12 / RIR-C12`

The prior claim remains semantically correct but its materialization boundary is narrowed.

### Requirement

Repository-identity semantics must appear consistently in:

1. canonical shared contracts;
2. canonical `aegis-implementation` and `aegis-gate-review` Skills;
3. generated/distributed Skills produced from those canonical sources; and
4. a candidate Plugin parity artifact generated from the exact implementation result.

Published historical Plugin materializations are not rewritten to satisfy a later candidate contract.

### Claim

A future Plugin built from the repaired candidate does not omit repository-identity safety semantics, while historical release truth remains immutable.

---

## 4. Corrected `O-RI-CONTRACT` materialization surfaces

After implementation, the mandatory current-candidate parity oracle inspects:

```text
docs/execution-surface-contract-v0.2-repository-identity-repair.md
skillset/shared/handoff-contract.md
skillset/skills/aegis-implementation/**
skillset/skills/aegis-gate-review/**
skills/aegis-implementation/**
skills/aegis-gate-review/**
<candidate-plugin-artifact>/skills/aegis-implementation/**
<candidate-plugin-artifact>/skills/aegis-gate-review/**
```

The committed historical path:

```text
plugins/aegis/** @ release 0.1.0-beta.3
```

is evidence of the published beta.3 release and must remain validated against its historical release manifest. It is not required to equal the new candidate Skill digests before RC-I01 creates a new release candidate.

The repair must not disable or weaken beta.3 release-binding checks merely to make repository-identity implementation pass.

---

## 5. Candidate Plugin parity evidence contract

The implementation result must expose a durable candidate evidence artifact whose metadata contains at least:

```yaml
candidate_plugin_parity:
  artifact_class: CANDIDATE_PLUGIN_PARITY_EVIDENCE
  source_revision: <exact implementation result revision>
  repository:
    provider: github
    full_name: Mostorm-Labs/aegis
  public_release: false
  release_tag: null
  release_version_claim: none
  skill_inventory_count: 9
  exact_nine: true
  canonical_generated_parity: PASS
  candidate_plugin_parity: PASS
  repository_identity_markers_present: PASS
  artifact_ref: <reviewer-resolvable workflow artifact / durable ref>
```

The artifact may be produced in CI or another reviewer-resolvable evidence boundary. It must not require a GitHub Release, public tag, committed release manifest, or mutation of `plugins/aegis/**`.

The implementation may reuse existing deterministic Skill distribution/materialization primitives, but P20 does not require a new standalone Plugin build framework.

---

## 6. Required parity proof

For the exact repository-identity implementation result, Gate evidence must prove:

```yaml
candidate_parity:
  canonical_to_generated_aegis_implementation: PASS
  canonical_to_generated_aegis_gate_review: PASS
  generated_to_candidate_plugin_aegis_implementation: PASS
  generated_to_candidate_plugin_aegis_gate_review: PASS
  candidate_plugin_exact_nine_inventory: PASS
  repository_identity_required_markers: PASS

historical_release_integrity:
  beta3_release_manifest_mutated: false
  beta3_release_identity_rewritten: false
  beta3_historical_binding_check_weakened: false

rc_i01_separation:
  v0_2_0_beta_1_release_manifest_created_by_this_repair: false
  v0_2_0_beta_1_tag_created_by_this_repair: false
  github_release_created_by_this_repair: false
```

Any candidate parity mismatch is a repository-identity Gate blocker. Any mutation of historical beta.3 release identity or premature RC-I01 release materialization is also a blocker.

---

## 7. Relationship to existing P20 proof set

Everything else from `61aa42e98558a1621b0228223835473f248ee869` is retained:

- 14 repository-identity requirement/claim pairs, except the R12 materialization interpretation repaired here;
- `RI-S01..RI-S10` deterministic scenarios;
- `RI-M01..RI-M06` negative perturbations;
- `RI-PFC01..RI-PFC06` fresh Codex installed-platform observations;
- zero tolerance for wrong-repository authored mutations;
- zero dirty-work loss;
- zero cross-repository SHA fallback;
- zero negative false acceptance;
- repository preflight before P33 cursor classification;
- P36 repository identity parity;
- reviewer-resolvable composite evidence graph.

No PP0, service-scale proof, standalone repository resolver, monolithic evidence bundle, or new performance threshold is introduced.

---

## 8. Gate interpretation

For the targeted repository-identity repair, P34 may accept Plugin-surface parity when all of the following are true:

1. exact implementation revision is materialized and reviewer-resolvable;
2. canonical/generated Skill parity passes;
3. the candidate Plugin parity artifact is derived from that exact implementation revision;
4. candidate Plugin artifact contains exact nine Skills;
5. repository-identity semantics are present in the candidate Plugin copies of affected Skills;
6. historical beta.3 release materialization remains untouched and its existing binding rules are not weakened;
7. RC-I01 `0.2.0-beta.1` release package has not been prematurely materialized or published by this repair;
8. all other repository-identity P20 mandatory evidence remains satisfied.

The candidate artifact proves *future Plugin materializability of the repaired Skills*. It does not itself authorize a release.

---

## 9. Downstream implementation boundary

After Governance accepts this targeted P20 repair, repository-identity P30 may plan a separate repair slice that:

- updates canonical repository-identity handoff semantics;
- regenerates distributed Skills;
- adds deterministic repository-identity scenarios/negative tests;
- produces the candidate Plugin parity artifact as evidence;
- preserves published beta.3 release materialization;
- does not create the RC-I01 `0.2.0-beta.1` release manifest/tag/release;
- returns exact evidence for an independent repository-identity P34.

RC-I01 P32 remains paused until that repair is gated and integrated, then receives a current repository-bound P31/P32 handoff.

---

## 10. P20 exit criteria

```yaml
P20_materialization_repair:
  upstream_repository_identity_p20: 61aa42e98558a1621b0228223835473f248ee869
  proof_boundary_conflict: RESOLVED_BY_DESIGN
  beta3_history_preserved: true
  candidate_plugin_parity_artifact_allowed: true
  candidate_artifact_is_release: false
  rc_i01_release_materialization_consumed: false
  repository_identity_proof_strength_reduced: false
  pp0_reopened: false
  service_profile: NOT_AUTHORIZED
  rollout: DENIED
  release_authorized: false
  RC_I01_P32: PAUSED
  next_owner: aegis-governance
  next_stage: P21_AUTHORITY_REVIEW
```

This document remains Draft/Proposed until Governance explicitly reviews and supersedes the targeted repository-identity Verification Authority materialization interpretation.