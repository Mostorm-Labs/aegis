#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = "README stable execution closure anchor missing"

try:
    runpy.run_path(str(ROOT / "scripts/beta5_finalize_once.py"), run_name="__main__")
except SystemExit as exc:
    if str(exc) != EXPECTED:
        raise


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def write(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"UPDATED {rel}")


rel = "README.md"
text = read(rel)
text = text.replace("### Gate Closure Stability in beta.4", "### Gate Closure Stability in beta.5", 1)
text = text.replace(
    "Current published prerelease:\n\n```text\nv0.2.0-beta.4\n```",
    "Current published prerelease:\n\n```text\nv0.2.0-beta.5\n```",
    1,
)
text = text.replace(
    "https://github.com/Mostorm-Labs/aegis/releases/download/v0.2.0-beta.4/aegis-skill-installation-kit-v0.2.0-beta.4.zip",
    "https://github.com/Mostorm-Labs/aegis/releases/download/v0.2.0-beta.5/aegis-skill-installation-kit-v0.2.0-beta.5.zip",
    1,
)
text = text.replace(
    "Immutable `v0.2.0-beta.3`, `v0.2.0-beta.2`, `v0.2.0-beta.1`, and `v0.1.0-beta.3` remain historical rollback/reproducibility boundaries.",
    "Immutable `v0.2.0-beta.4`, `v0.2.0-beta.3`, `v0.2.0-beta.2`, `v0.2.0-beta.1`, and `v0.1.0-beta.3` remain historical rollback/reproducibility boundaries.",
    1,
)
text = text.replace(
    "**v0.2 — Control Plane prerelease `v0.2.0-beta.4`, delivered as one Plugin + exact nine Skills with stable post-P31 closure, risk-proportionate evidence, and late-finding Gate discipline.**",
    "**v0.2 — Control Plane prerelease `v0.2.0-beta.5`, delivered as one Plugin + exact nine Skills with repo-local execution authority, stable post-P31 closure, risk-proportionate evidence, and independent Gate discipline.**",
    1,
)
if "[`docs/releases/v0.2.0-beta.5.md`](docs/releases/v0.2.0-beta.5.md)" not in text:
    marker = "- [`docs/releases/v0.2.0-beta.4.md`](docs/releases/v0.2.0-beta.4.md)"
    text = text.replace(marker, "- [`docs/releases/v0.2.0-beta.5.md`](docs/releases/v0.2.0-beta.5.md)\n" + marker, 1)
if "### Repo-local Execution Authority" not in text:
    marker = "### Gate Closure Stability in beta.5\n"
    section = (
        "### Repo-local Execution Authority\n\n"
        "Beta.5 materializes frozen execution truth under `.aegis/packages/<task-id>/`, uses progressive loading and thin surface handoffs, runs ImplementationDesignPreflight/RED Oracle Preflight inside P32/P33 when applicable, and preserves independent P34 Gate review. Missing `execution_authority_mode` remains legacy `remote`; `repo_materialized` and `hybrid` are additive.\n\n"
    )
    if marker not in text:
        raise SystemExit("README beta.5 gate-closure anchor missing")
    text = text.replace(marker, section + marker, 1)
write(rel, text)

write("docs/releases/v0.2.0-beta.5.md", '''# Aegis v0.2.0-beta.5

Status: **Prerelease candidate**

## What beta.5 changes

Beta.5 makes the frozen P31 completion model executable without repeatedly reconstructing Authority across ChatGPT, Codex, and Notion. It preserves P30-P36 ownership and Project State v0.6 while adding repo-local execution authority, progressive loading, internal implementation-design/RED-oracle preflights, deterministic package tooling, and a thinner surface transfer.

No new top-level P-stage is introduced.

## Repo-local package

`execution_authority_mode: repo_materialized | hybrid` materializes `.aegis/packages/<task-id>/package.json`, `authority.lock.json`, `verification.lock.json`, `execution-contract.json`, `implementation-context.md`, and `evidence-contract.json` with local SHA-256 bindings. Missing `execution_authority_mode` remains compatible with legacy `remote` packages.

## Behavioral changes

- P32/P33 progressively load the local package and do not refetch upstream Notion by default.
- `ImplementationDesignPreflight` is internal to the code surface; clean resolution continues without a ChatGPT approval round trip.
- Critical invariants may require RED Oracle Preflight; known-bad behavior passing the frozen oracle routes `VERIFICATION_DESIGN_DEFECT`.
- Continuous execution is `inspect -> design -> RED -> implement -> debug -> regression -> verification -> materialize` until terminal state.
- Success returns `READY_FOR_CONTROL_REVIEW`; implementation producers cannot self-issue P34/Capability/Release PASS.
- P33 retains existing cursor classifications and adds `completed_through` / `next_action`, with optional design/oracle navigation state.
- Notion remains human-readable upstream Authority; repo-local locks become execution-time truth, with upstream fetch used for fallback/reconciliation.

## Deterministic tooling

Adds `scripts/aegis_execution_package.py` with `materialize`, `validate`, `render-handoff`, and `check-cursor`, plus `schemas/execution-package-v0.1.schema.json`.

## Compatibility

P30-P36 ownership and Project State v0.6 are unchanged. Existing `.aegis` manifests, `package_ref`, `package_materialization_ref`, `task_anchor`, and `resume_cursor` remain valid. `remote`, `repo_materialized`, and `hybrid` may coexist during migration. Immutable beta.4 and earlier releases remain rollback boundaries.

## Token-efficiency target

The old authority-heavy loop could perform roughly 5-10 upstream Authority fetches per continuation/review round; two to four rounds could produce 10-40 repeated connector reads plus repeated summarization/reinterpretation. Beta.5's normal path is one P31 synthesis/materialization, zero normal Notion fetches in CODE_EXECUTION, and one independent review. For large Authority sets, a 50-80% reduction in repeated control/executor context overhead is an engineering target, not a billing guarantee.
''')

write("docs/installation-and-usage-v0.2.md", '''# Aegis Installation & Usage Guide v0.2

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
''')

print("BETA5_FINALIZE_WRAPPER_OK")
