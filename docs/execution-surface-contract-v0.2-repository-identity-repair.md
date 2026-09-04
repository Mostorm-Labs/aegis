# Aegis Execution Surface Contract v0.2 — Repository Identity Repair

Status: **Draft / Proposed P17 Platform Contract amendment**

Scope: `aegis/execution-surface`

Current Authority being amended:

- `docs/execution-surface-contract-v0.2.md`
- current repository baseline: `212f1d7dcb2c31162f0f64946a4473912578c5d9`

Triggering dogfood incident:

- release package: `RC-I01-P31-01`
- package ref: `b876c74c4b098d7088233945a17de47a7b5b3422`
- intended repository: `Mostorm-Labs/aegis`
- observed execution-surface misresolution: Codex inferred `Mostorm-Labs/axtp` from ambient repository context after the bare package ref was not immediately resolvable locally.

This amendment is intentionally narrow. It does not redesign the Control Plane, lifecycle, stage ownership, task-anchor semantics, resume-cursor semantics, Gate ownership, release packaging, or Project State. It repairs one missing platform contract: **repository namespace identity for repository-backed execution handoffs**.

---

## 1. Defect classification

The observed failure is classified as:

```yaml
class: MISSING_CONTRACT
owning_stage: P17_PLATFORM_CONTRACT
affected_surface: CONTROL_REASONING -> CODE_EXECUTION / CODE_REVERIFY
failure_mode: repository-backed refs interpreted without an explicit repository namespace
safety_effect: execution may resolve package/anchor/cursor against an unintended repository
```

The prior v0.2 execution-surface repair correctly established:

> `Task Anchor != Execution Cursor`

but implicitly assumed that all repository-local refs were already being interpreted inside the correct repository.

That assumption is unsafe in multi-repository environments, especially when:

- the current checkout contains unrelated dirty work;
- the package ref has not yet been fetched into the local object database;
- multiple local repositories or remotes are available;
- ambient project/session context references another repository;
- an executor creates an isolated worktree and must choose which repository owns it.

---

## 2. New core invariant

The execution-position invariant is extended to:

> `Repository Identity != Task Anchor != Execution Cursor`.

And:

> **A revision is not a repository locator.**

`package_ref`, `task_anchor.revision`, `resume_cursor.revision`, execution refs, and result revisions are repository-scoped identifiers. A repository-backed handoff MUST define the repository namespace in which those refs are valid before the receiving surface resolves, fetches, checks out, or mutates anything.

Ambient cwd, nearby worktrees, prior-session repository context, guessed project names, or other locally available repositories MUST NOT substitute for the declared repository identity.

---

## 3. Repository identity object

Every repository-backed P31 package and every repository-backed `surface_handoff` MUST carry a non-null repository identity object.

For the current GitHub-backed profile:

```yaml
repository:
  provider: github
  full_name: <owner/repository>
```

Example:

```yaml
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
```

`full_name` is the canonical repository namespace for all bare Git revisions carried by that package/handoff.

This amendment does not require a local filesystem path. Local checkout/worktree paths are executor-specific and must not become portable lifecycle Authority.

A future non-GitHub repository provider may define an equivalent provider-qualified canonical repository ID, but the current v0.2 Plugin profile only needs the GitHub form above.

---

## 4. Package materialization binding

A repository-backed execution handoff MUST carry both:

```yaml
package_ref: <exact package revision>
package_materialization_ref: <reviewer/executor-resolvable durable URL or repository ref>
```

For GitHub, `package_materialization_ref` SHOULD resolve to a commit or pull request in the declared `repository.full_name`.

Example:

```yaml
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
package_ref: b876c74c4b098d7088233945a17de47a7b5b3422
package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/56
```

The materialization ref does not expand package Authority. It gives the receiving surface a deterministic route to resolve the exact package without guessing another repository.

If `package_materialization_ref` resolves to a different repository than `repository.full_name`, execution MUST fail closed.

---

## 5. Repository-scoped ref semantics

Within one repository-backed package/handoff, the following are interpreted only inside the declared repository namespace unless an individual field explicitly declares a different governed repository:

```text
package_ref
task_anchor.revision
resume_cursor.revision
resume_cursor.execution_ref
actual_starting_revision
result_revision
materialized repository branch / PR refs
```

The default is single-repository execution.

Cross-repository execution is not inferred. If a future task genuinely spans repositories, each repository must be explicitly named and the package must define which refs/files/actions belong to each one. A single-repository package may never silently switch repositories to make a ref resolvable.

---

## 6. Mandatory receiving-surface preflight

Before resolving package contents, checking ancestry, creating a worktree, or changing files, the receiving CODE_EXECUTION / CODE_REVERIFY surface MUST perform repository identity preflight in this order:

1. read the declared `repository.provider` and `repository.full_name`;
2. determine whether the current checkout/worktree belongs to that repository;
3. if the current checkout belongs to the declared repository, continue repository-local inspection;
4. if it belongs to a different repository, do not reuse it for execution;
5. locate or create an isolated checkout/worktree for the declared repository without mutating unrelated dirty work;
6. resolve/fetch `package_ref` only from the declared repository/remotes;
7. verify `package_materialization_ref` belongs to the declared repository;
8. only then verify `task_anchor` ancestry and establish actual starting revision.

Repository identity preflight occurs before task-anchor reconciliation because ancestry is meaningless if evaluated in the wrong repository namespace.

---

## 7. Fail-closed repository mismatch behavior

The following conditions MUST stop execution:

```text
- repository is missing from a repository-backed handoff;
- current/selected checkout belongs to another repository and no declared-repository checkout can be established safely;
- package_ref can only be found in a different repository;
- package_materialization_ref belongs to another repository;
- task_anchor cannot be resolved in the declared repository;
- executor has multiple plausible repositories and the handoff does not disambiguate them;
- local remote identity conflicts with the declared repository identity;
- repository identity changes during resume without an explicit package supersession.
```

Return:

```yaml
status: BLOCKED_REPOSITORY_IDENTITY
continue_execution: false
```

`BLOCKED_REPOSITORY_IDENTITY` is an execution/environment safety blocker. It does not authorize selecting a different repository, rewriting the package, or guessing from ambient context.

If repository identity evidence also contradicts Current Authority or package scope, the executor may return the more specific existing `BLOCKED_AUTHORITY` / `BLOCKED_EXECUTION_DIVERGENCE` as appropriate.

---

## 8. Dirty worktree behavior

A dirty worktree in the correct repository is not repository divergence by itself.

When unrelated dirty work exists:

- preserve it;
- do not reset, stash, discard, or overwrite it without explicit user authorization;
- prefer an isolated worktree/checkout for the declared repository;
- do not switch to another repository merely because that repository is clean.

This formalizes the safe behavior observed in the triggering incident before the repository misresolution occurred.

---

## 9. Revised surface handoff schema

A repository-backed P32/P33 handoff becomes:

```yaml
type: surface_handoff
stage: P32 | P33
stage_owner: aegis-implementation
from_surface: CONTROL_REASONING
to_surface: CODE_EXECUTION
preferred_executor: codex
reason: repository_heavy_execution

repository:
  provider: github
  full_name: <owner/repository>

package_ref: <approved-task-package-revision>
package_materialization_ref: <durable package URL/ref in declared repository>

task_anchor:
  revision: <trusted-revision>
  relation: ancestor

resume_cursor: null | <accepted-cursor>
return_surface: CONTROL_REVIEW
```

A repository-backed P36 CODE_REVERIFY handoff uses the same repository object and package-materialization rule.

The existing Codex execution prefix may remain unchanged. The envelope itself now carries the missing repository identity, and the receiving-surface contract requires repository preflight before package/cursor reconciliation.

---

## 10. P31 package requirements

For repository-backed implementation, P31 MUST freeze:

```yaml
repository:
  provider: github
  full_name: <owner/repository>
package_ref: <exact package revision after materialization>
package_materialization_ref: <durable ref in same repository>
task_anchor:
  revision: <trusted revision in same repository>
  relation: ancestor
```

The package body SHOULD also name the intended repository in human-readable task identity so reviewers can detect a mismatch without interpreting raw refs.

A P31 package that omits repository identity is not executable on CODE_EXECUTION even if its task content is otherwise valid.

---

## 11. P32 / P33 / P36 execution requirements

Repository-backed execution MUST:

- validate repository identity before package resolution;
- reject cross-repository fallback;
- preserve unrelated dirty work;
- fetch only from the declared repository namespace;
- perform task-anchor/cursor reconciliation only after repository identity is established;
- include repository identity in the return envelope;
- materialize result evidence in the same declared repository unless the package explicitly authorized a separate evidence repository.

P33 additionally MUST treat a repository-identity mismatch as fail-closed before classifying EXACT_CURSOR / DESCENDANT_CURSOR / ANCHOR_DESCENDANT_WITHOUT_CURSOR / DIVERGED.

---

## 12. Verification implications for P20

Downstream Verification Design must add deterministic and dogfood coverage for at least:

1. correct repository + resolvable package -> continue;
2. wrong current repository + correct repository available -> isolate/switch to declared repository without mutating wrong repo;
3. wrong current repository + declared repository unavailable -> `BLOCKED_REPOSITORY_IDENTITY`;
4. bare package SHA exists only in another repository -> must not follow it;
5. package materialization URL repository mismatch -> fail closed;
6. multiple local repositories + ambiguous ambient context -> declared repository wins, no guessing;
7. dirty correct repository -> preserve dirty work and use isolated worktree when needed;
8. correct repository + valid descendant anchor/cursor -> existing reconciliation semantics remain unchanged;
9. generated canonical/distributed `aegis-implementation` and `aegis-gate-review` instructions preserve the repository-identity contract;
10. Codex-targeted dogfood demonstrates that a task for `Mostorm-Labs/aegis` never executes in `Mostorm-Labs/axtp` solely because ambient context references `axtp`.

These are verification obligations, not implementation details owned by this P17 amendment.

---

## 13. Impact on the paused RC-I01 release package

`RC-I01-P31-01` remains the intended release-package task definition, but its current P32 handoff is not safe to execute because the handoff schema omitted repository identity.

Required downstream disposition after this amendment is accepted:

```yaml
RC-I01:
  P32: PAUSED
  package_semantics: RETAIN
  execution_handoff: REGENERATE_AFTER_AUTHORITY_REPAIR
  intended_repository:
    provider: github
    full_name: Mostorm-Labs/aegis
  package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/56
  pp0_harness_work: NOT_REOPENED
  p34_rerun_for_prior_control_plane_candidate: NOT_REQUIRED_BY_THIS_DEFECT
  release_publication: NOT_AUTHORIZED
```

Whether the existing P31 package file itself needs a small additive repair or a replacement P31 package is a downstream implementation-control decision after Verification/Governance accept the repaired contract.

---

## 14. Non-goals

This repair does not:

- change Product requirements or the Plugin + exact-nine product form;
- change Control Plane objects or lifecycle semantics;
- change stage ownership;
- change `Task Anchor != Execution Cursor` semantics;
- permit cross-Primary zero-user-turn substantive chaining;
- reopen PP0 40-WorkScope harness obligations;
- authorize SERVICE_PROFILE;
- expand rollout;
- rerun or reinterpret the already accepted Control Plane P34 verdict solely because of this repository-addressing defect;
- publish `v0.2.0-beta.1`;
- discard or rewrite the dirty historical CP-I09 worktree that exposed the issue.

---

## 15. P17 exit criteria

This proposed Platform Contract repair is complete for architecture review when:

```yaml
repository_identity_contract:
  explicit_namespace: REQUIRED
  package_materialization_binding: REQUIRED
  repository_preflight_before_ancestry: REQUIRED
  cross_repository_guessing: FORBIDDEN
  dirty_worktree_preservation: REQUIRED
  mismatch_result: BLOCKED_REPOSITORY_IDENTITY
  P32_P33_P36_covered: true
  downstream_verification_update_required: true
  downstream_p31_handoff_regeneration_required: true
```

Next owner after P17: `aegis-verification`.

Next stage: targeted `P20 Verification Design` repair for repository-identity and wrong-repository fail-closed evidence.

This document remains `Draft / Proposed` until the required downstream Verification and Governance stages accept/supersede the Current Authority chain.