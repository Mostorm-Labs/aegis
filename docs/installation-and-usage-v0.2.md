# Aegis Installation & Usage Guide v0.2

Current prerelease: `v0.2.0-beta.5`.

Aegis v0.2 is delivered primarily as one native Aegis Plugin exposing the exact nine canonical Skills. A portable 9-Skill Installation Kit remains the fallback path.

## Install

Marketplace source: `https://github.com/Mostorm-Labs/aegis`. For reproducible beta.5 installation, pin immutable tag `v0.2.0-beta.5`.

Exact-nine catalog: `aegis`, `aegis-project-state`, `aegis-discovery`, `aegis-modeling`, `aegis-architecture`, `aegis-verification`, `aegis-governance`, `aegis-implementation`, `aegis-gate-review`.

## Beta.5 execution model

P31 may use `execution_authority_mode: remote | repo_materialized | hybrid`; missing mode remains legacy `remote`. Local modes materialize `.aegis/packages/<task-id>/` with `package.json`, Authority/Verification locks, execution/evidence contracts, and implementation context.

Normal CODE_EXECUTION progressively reads `package.json -> implementation-context.md -> execution-contract.json`, loading Authority/Verification locks only when needed. Notion reconciliation is exception-driven.

Architecture-sensitive work runs `ImplementationDesignPreflight` internally. Critical behavioral invariants may freeze RED Oracle Preflight; a known-bad old implementation passing the acceptance oracle returns `VERIFICATION_DESIGN_DEFECT`.

Continuous execution is `inspect -> design -> RED oracle -> implement -> debug -> regression -> verification -> durable materialization`. Success returns `READY_FOR_CONTROL_REVIEW`; only independent P34 can issue Gate PASS.

## Deterministic package commands

```bash
python3 scripts/aegis_execution_package.py materialize descriptor.json --root .
python3 scripts/aegis_execution_package.py validate .aegis/packages/<task-id>/package.json
python3 scripts/aegis_execution_package.py render-handoff .aegis/packages/<task-id>/package.json --materialization-ref <exact-ref>
python3 scripts/aegis_execution_package.py check-cursor .aegis/packages/<task-id>/package.json <revision> --root .
```

## Compatibility / rollback

No new top-level P-stage and no Project State v0.6 schema break are introduced. Existing Notion-first projects and P31/task-anchor/resume-cursor refs remain valid. Rollback boundaries include immutable `v0.2.0-beta.4` and earlier releases.
