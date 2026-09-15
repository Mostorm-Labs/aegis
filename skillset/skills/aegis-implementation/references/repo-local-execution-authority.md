# Repo-local Execution Authority

P31 MAY materialize execution truth into the target repository so the code surface does not repeatedly refetch or reinterpret upstream Authority. This is additive to existing remote packages and does not create a new lifecycle stage.

## Directory contract

For `execution_authority_mode: repo_materialized | hybrid`:

```text
.aegis/packages/<task-id>/
  package.json
  authority.lock.json
  verification.lock.json
  execution-contract.json
  implementation-context.md
  evidence-contract.json
```

`.aegis/results/<task-id>/` MAY contain execution-produced durable records when the frozen Evidence Contract requires them.

JSON is the canonical dependency-free representation for v0.1 of this package contract. Existing `package_ref`, `package_materialization_ref`, Notion-first packages, `task_anchor`, `resume_cursor`, and Project State v0.3-v0.6 remain valid.

## execution_authority_mode

- `remote`: legacy behavior; upstream Authority may need connector resolution. If the field is absent, treat the package as `remote`.
- `repo_materialized`: all implementation-required frozen Authority/Verification/closure context is content-addressed locally.
- `hybrid`: local package is primary for execution; explicit remote refs remain only for reconciliation/freshness exceptions.

## package.json is the executor entrypoint

The executor MUST read `package.json` first. It identifies task/repository/execution state and local content-addressed refs. For local modes it binds `authority_lock_ref`, `verification_lock_ref`, `execution_contract_ref`, `implementation_context_ref`, and `evidence_contract_ref`, each with a same-directory path and SHA-256.

The package also preserves repository identity, `execution_ref`, `task_anchor`, nullable `resume_cursor`, `continue_until_terminal_state: true`, and `return_surface: CONTROL_REVIEW`.

## Progressive loading

Normal load order is deliberately progressive:

1. `package.json`;
2. `implementation-context.md`;
3. `execution-contract.json`;
4. `authority.lock.json` only when an exact Authority statement is needed;
5. `verification.lock.json` only when an obligation/oracle needs inspection;
6. `evidence-contract.json` when materializing or returning evidence.

Do not fetch all Authority, Verification history, prior Gate reviews, or Notion pages at code-surface entry. A code surface SHOULD use the repo-local package as execution truth until a freshness/reconciliation condition fails.

## Lock responsibilities

`authority.lock.json` is a frozen execution binding, not a mirror of the human-readable source. It contains source provider/id/revision/content hash, current/supersession state, trusted sections, and only implementation-relevant frozen statements.

`verification.lock.json` MUST keep `requirement`, `oracle`, `acceptance`, and `evidence_required` distinct for every obligation. `test PASS` does not imply requirement satisfaction unless that frozen acceptance mapping says the test is a complete oracle.

`execution-contract.json` is the machine-readable `EXECUTION_CLOSURE_CONTRACT`: required/forbidden changes, authorized mutation scope, preserved work, required verification, blocking/corroborative evidence, terminal success/blockers, continuous execution, optional ImplementationDesignPreflight policy, optional RED-oracle precondition, and return contract.

`implementation-context.md` is short and code-oriented: current flow, known incomplete boundary, relevant owners/files, preserved completed work, and first incomplete action. It MUST NOT become a second architecture authority.

## PackageBindingPreflight and freshness

For local modes, after repository identity and exact package materialization are resolved, validate:

- every package-local ref exists, stays inside the package directory, and matches its SHA-256;
- Authority lock is Current and not explicitly superseded;
- source identity/revision/content hash are present;
- Verification obligations separate requirement/oracle/evidence and are structurally executable;
- execution terminal criteria and scope are unambiguous;
- task-anchor/cursor rules remain valid.

Do not refetch Notion merely to prove freshness when the frozen local binding is internally valid and no supersession signal exists. Reconcile upstream only for missing/unverifiable bindings, source/hash mismatch, explicit supersession ambiguity, Authority conflict, or explicit control-plane reconciliation.

## ImplementationDesignPreflight

This is a P32/P33 internal checkpoint, not a new P-stage and not an automatic human approval Gate. Require it when work changes transaction boundaries, ownership, publication, a subsystem boundary, cross-module coordination, concurrency/lifecycle, or a non-trivial data model.

Record exact current flow, target owner/prepare/commit/publication/abort flow, affected types/files, obligation-to-implementation/verification mapping, test plan, and unresolved semantic decisions.

If `unresolved_semantic_decisions: []`, `authority_conflict: false`, `verification_conflict: false`, and `package_scope_conflict: false`, execution continues in the same CODE_EXECUTION context. Do not bounce to Control merely to approve an implementation plan. If any item is unresolved, fail closed to the earliest owning layer.

## RED Oracle Preflight

For critical behavioral invariants, P31 MAY freeze:

```yaml
oracle_precondition:
  red_required: true
  expected_failure: <what old behavior must violate>
  observation_seam: <where canonical behavior is observed>
```

P32/P33 MUST run that acceptance oracle against the old implementation before mutating production code and observe the expected RED. If old code passes the oracle while the known requirement is still unsatisfied, return `VERIFICATION_DESIGN_DEFECT`; do not rewrite the oracle around the intended implementation.

## Continuous execution and return

Normal P32/P33 code-surface sequence is:

`inspect -> ImplementationDesignPreflight -> RED Oracle Preflight -> implement -> debug -> regression -> verification -> durable materialization`

An intermediate test pass, commit, or checkpoint is not a return condition. Continue until the frozen terminal success is satisfied or an explicit terminal blocker occurs. Successful execution returns `READY_FOR_CONTROL_REVIEW` plus exact result/materialization/evidence identities; it never declares P34 PASS.

## Independent Gate boundary

**Implementation Producer != Final Gate Reviewer.** The implementation producer may return `READY_FOR_CONTROL_REVIEW`; it cannot issue P34 PASS, Capability PASS, G2 PASS, or Release PASS. P34 independently resolves the package, Authority/Verification bindings required for review, result identity, evidence graph, authorized scope, and hidden failure modes.

## Deterministic tooling

When `scripts/aegis_execution_package.py` is available, prefer it to conversational reconstruction:

```text
materialize <descriptor> --root <repo>
validate <package.json>
render-handoff <package.json> --materialization-ref <exact-ref>
check-cursor <package.json> <observed-revision> --root <repo>
```

The rendered handoff is a thin trigger. Full Authority/Verification prose remains in the package and is progressively loaded, not recopied into the handoff.
