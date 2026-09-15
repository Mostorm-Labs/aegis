# Aegis Execution Authority Materialization v0.3

## Decision

Aegis keeps the existing P30-P36 lifecycle. The optimization is an execution-architecture change, not a new lifecycle stage.

```text
Human-readable Authority
  -> P20 Verification closure
  -> P31 freeze + repo-local materialization
  -> P32/P33 CODE_EXECUTION
       PackageBindingPreflight
       -> ImplementationDesignPreflight (when architecture-sensitive)
       -> RED Oracle Preflight (when frozen)
       -> implement/debug/regression/verification/materialize
  -> READY_FOR_CONTROL_REVIEW
  -> independent P34 Gate Review
```

## Authority placement

- Notion: human-readable upstream Authority and design governance.
- Repository `.aegis`: frozen execution-time Authority/Verification/closure bindings.
- GitHub: source, durable implementation identity, reviewable evidence.
- Codex/code surface: implementation executor.

P31 may materialize `.aegis/packages/<task-id>/package.json`, `authority.lock.json`, `verification.lock.json`, `execution-contract.json`, `implementation-context.md`, and `evidence-contract.json`.

The package is content-addressed by SHA-256 and progressively loaded. Upstream Notion is not fetched again on the normal P32/P33 path unless a local binding is missing/unverifiable, a source/hash mismatch exists, supersession is ambiguous, or explicit reconciliation is required.

## Why JSON

The user-facing prompt used YAML as an illustrative shape. v0.1 uses JSON for deterministic stdlib tooling and compatibility with existing `.aegis` JSON conventions. JSON is a YAML-compatible subset, so no semantic capability is lost and no YAML runtime dependency is introduced.

## Implementation Design Binding

Architecture-sensitive implementation runs `ImplementationDesignPreflight` inside P32/P33. It records exact current flow, target ownership/prepare/commit/publication/abort flow, affected types/files, obligation mapping, tests, and unresolved semantic decisions.

Clean preflight resolution continues directly in the same code execution context. It is not a human approval Gate. Only Authority ambiguity, Verification omission, package omission, scope divergence, or environment blockers return early.

## RED Oracle First

Critical behavioral invariants can freeze a RED precondition. The old implementation must fail the acceptance oracle before production mutation. If known-bad behavior passes, classify `VERIFICATION_DESIGN_DEFECT`; do not create an implementation-shaped test and call it proof.

## Continuous execution

P32/P33 default sequence:

```text
inspect -> design -> RED oracle -> implement -> debug -> regression -> verification -> durable materialization
```

Intermediate commits/tests/checkpoints do not return to Control. The executor returns only terminal success (`READY_FOR_CONTROL_REVIEW`) or an explicit terminal blocker.

## Resume

P33 keeps `EXACT_CURSOR`, `DESCENDANT_CURSOR`, `ANCHOR_DESCENDANT_WITHOUT_CURSOR`, and `DIVERGED`. Cursors add `completed_through`, `next_action`, and optionally `design_binding_ref`/`oracle_state` so continuation does not restate the whole task.

## Gate independence

Implementation Producer != Final Gate Reviewer. P32/P33 cannot self-issue P34 PASS, Capability PASS, G2 PASS, or Release PASS. P34 independently resolves package/result/evidence identities, Authority satisfaction, Verification completeness, scope conformance, and hidden failure modes.

## Compatibility and migration

`execution_authority_mode` is additive:

- `remote`: legacy Notion-first behavior; missing field means `remote`.
- `repo_materialized`: repo-local package is execution truth.
- `hybrid`: local-first execution plus explicit remote reconciliation refs.

No Project State v0.6 schema break is required. Existing `.aegis` manifests, `package_ref`, `package_materialization_ref`, `task_anchor`, `resume_cursor`, and v0.3-v0.6 projects remain valid.

## Token/connector objective

The old authority-heavy loop could refetch roughly 5-10 upstream pages per continuation/review round, then pay again for ChatGPT summarization and code-surface reinterpretation. Two to four rounds could therefore mean roughly 10-40 repeated connector reads plus repeated prompt context.

The target steady state is one P31 synthesis/materialization, zero normal Notion reads during CODE_EXECUTION, and one independent review. For large multi-round Authority sets, reducing repeated control/executor context overhead by roughly 50-80% is a reasonable engineering target, not a billing guarantee.
