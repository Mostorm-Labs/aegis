#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def write(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"UPDATED {rel}")


def ensure_after_line(rel, needle, addition, marker):
    text = read(rel)
    if marker in text:
        print(f"PRESENT {rel}: {marker}")
        return
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if needle in line:
            lines.insert(index + 1, addition)
            write(rel, "\n".join(lines) + "\n")
            return
    raise SystemExit(f"missing line anchor in {rel}: {needle}")


def replace_stage_row(rel, stage, new_line):
    text = read(rel)
    lines = text.splitlines()
    prefix = f"| {stage} |"
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            if line == new_line:
                print(f"PRESENT {rel}: {stage}")
                return
            lines[index] = new_line
            write(rel, "\n".join(lines) + "\n")
            return
    raise SystemExit(f"missing stage row in {rel}: {stage}")


def append_section(rel, marker, section):
    text = read(rel)
    if marker in text:
        print(f"PRESENT {rel}: {marker}")
        return
    write(rel, text.rstrip() + "\n\n" + section.strip() + "\n")


ensure_after_line(
    "skillset/skills/aegis/SKILL.md",
    "At `P31`, freeze an `EXECUTION_CLOSURE_CONTRACT`",
    "   When repository execution would otherwise repeatedly reconstruct upstream context, materialize the frozen execution truth under `.aegis/packages/<task-id>/` and hand the code surface a thin package trigger; legacy remote packages remain valid.",
    "materialize the frozen execution truth under `.aegis/packages/<task-id>/`",
)

text = read("skillset/skills/aegis/SKILL.md")
lines = text.splitlines()
for index, line in enumerate(lines):
    if line.startswith("3. At `P32`, execute the complete frozen contract"):
        lines[index] = "3. At `P32`, execute the complete frozen contract until terminal success or an explicit terminal blocker. Use internal ImplementationDesignPreflight / RED-oracle checkpoints when frozen/applicable, but do not add a control round trip when they resolve cleanly. Do not redesign upstream authority and do not return merely because an intermediate checkpoint finished."
        write("skillset/skills/aegis/SKILL.md", "\n".join(lines) + "\n")
        break
else:
    raise SystemExit("missing P32 implementation behavior line")

ensure_after_line(
    "skillset/skills/aegis-verification/SKILL.md",
    "This stage is responsible for Verification closure before implementation.",
    "\nKeep `requirement`, `oracle`, and `evidence` distinct. For known-bad old behavior behind a critical invariant, freeze a RED-oracle precondition when practical; if the old implementation passes that oracle while the requirement is still known unsatisfied, route `VERIFICATION_DESIGN_DEFECT` instead of letting implementation adapt the test.",
    "Keep `requirement`, `oracle`, and `evidence` distinct.",
)

ensure_after_line(
    "skillset/skills/aegis-gate-review/SKILL.md",
    "At `P34`, audit the frozen completion target",
    "- **Implementation Producer != Final Gate Reviewer.** `READY_FOR_CONTROL_REVIEW` is an execution return state, never a self-issued P34/Capability/Release PASS; resolve package/result/evidence independently on the review surface.",
    "Implementation Producer != Final Gate Reviewer",
)

append_section(
    "skillset/skills/aegis-verification/references/verification.md",
    "## Requirement / oracle / evidence separation and RED Oracle Preflight",
    r'''## Requirement / oracle / evidence separation and RED Oracle Preflight

A frozen Verification obligation MUST keep three questions distinct:
- `requirement`: what system behavior must be true;
- `oracle`: what observation can falsify or accept that behavior;
- `evidence`: the durable artifact/identity produced by running the oracle.

A green test is evidence. It proves the requirement only to the extent that P20 has frozen that test/oracle as adequate coverage for the requirement and its material failure modes.

For atomic publication, consistency, recovery, ordering, concurrency, transaction semantics, or another critical behavioral invariant where a known old implementation violates the requirement, P20 SHOULD freeze a RED precondition when practical:

```yaml
oracle_precondition:
  red_required: true
  expected_failure: <behavior the old implementation must expose>
  observation_seam: <canonical observer boundary>
```

P32/P33 then run the frozen acceptance oracle against the old implementation before production mutation. If the old implementation is known to violate the requirement but the oracle passes, stop with `VERIFICATION_DESIGN_DEFECT`. Do not let implementation rewrite the test around its preferred architecture.''',
)

append_section(
    "skillset/skills/aegis-gate-review/references/gate-review.md",
    "## Independent producer / reviewer boundary",
    r'''## Independent producer / reviewer boundary

**Implementation Producer != Final Gate Reviewer.** P32/P33 may return `READY_FOR_CONTROL_REVIEW` and exact durable result/evidence identities, but the implementation producer cannot self-issue P34 PASS, Capability PASS, G2 PASS, or Release PASS.

P34 independently resolves the repo-local/legacy package, Authority and Verification bindings required for review, result identity, evidence graph, authorized scope, and hidden failure modes. For `repo_materialized`/`hybrid` packages, review the content-addressed locks first and reconcile upstream Notion only when freshness/supersession cannot be established locally or an explicit Authority reconciliation is required.

The thin `surface_handoff` and executor summary are navigation only. They cannot substitute for package contents, repository reality, or machine evidence.''',
)

append_section(
    "skillset/shared/handoff-contract.md",
    "## Repo-local minimal surface handoff",
    r'''## Repo-local minimal surface handoff

When P31 has materialized `execution_authority_mode: repo_materialized | hybrid`, the normal code-surface transfer is a thin execution trigger:

```yaml
type: surface_handoff
task_id: <task-id>
stage: P32
stage_owner: aegis-implementation
repository:
  provider: github
  full_name: <owner/repository>
package:
  path: .aegis/packages/<task-id>/package.json
  materialization_ref: <exact-same-repository-ref>
execution_ref: <branch-or-durable-ref>
resume_cursor: null
continue_until_terminal_state: true
return_surface: CONTROL_REVIEW
```

The handoff MUST NOT repeat full Authority prose, Verification prose, prior Gate history, or implementation interpretation already frozen inside the content-addressed package. The executor progressively loads `package.json`, `implementation-context.md`, and `execution-contract.json`; Authority/Verification locks are loaded only when the active step needs them.

For local packages, Notion/source reconciliation is exception-driven: missing/unverifiable local binding, hash/source mismatch, explicit supersession ambiguity, Authority conflict, or explicit control request. Do not add a connector round trip merely to restate an internally valid frozen lock.''',
)

append_section(
    "skillset/shared/core-invariants.md",
    "## Execution Authority Materialization Invariant",
    r'''## Execution Authority Materialization Invariant

P31 may materialize the smallest execution-required Authority/Verification/closure truth into a content-addressed repo-local package. Once that package is frozen, normal P32/P33 execution progressively loads it and does not repeatedly reconstruct the same truth from human-readable upstream sources.

A surface handoff is a thin trigger, not a second specification. P32/P33 internal ImplementationDesign/RED-oracle checkpoints continue in the same code execution context when resolved; only a real Authority, Verification, package, scope, or environment blocker creates an early control return.

`READY_FOR_CONTROL_REVIEW != P34 PASS`. The implementation producer returns durable identities; the Gate reviewer independently decides downstream trust.''',
)

append_section(
    "skillset/skills/aegis/references/implementation.md",
    "## Repo-local execution authority (v0.2 additive mode)",
    r'''## Repo-local execution authority (v0.2 additive mode)

P31 SHOULD use `execution_authority_mode: repo_materialized` or `hybrid` when execution truth can be frozen in the target repository. The package lives under `.aegis/packages/<task-id>/` and content-addresses its Authority lock, Verification lock, closure contract, evidence contract, and short implementation context. Missing mode remains legacy `remote`; no Project State schema migration is required.

P32/P33 progressively load the repo-local package rather than refetching upstream Notion by default. Architecture-sensitive tasks run `ImplementationDesignPreflight` internally; resolved designs continue without a human round trip. Critical behavioral obligations may require **RED Oracle Preflight** before mutation; a known-bad old implementation passing the frozen oracle is `VERIFICATION_DESIGN_DEFECT`.

The normal code-surface sequence is `inspect -> design -> RED oracle -> implement -> debug -> regression -> verification -> durable materialization`. Successful execution returns `READY_FOR_CONTROL_REVIEW`; independent P34 still owns PASS.''',
)

replace_stage_row(
    "skillset/skills/aegis/references/stage-contracts.md",
    "P31",
    "| P31 | Task Packaging | authority refs, scope/non-goals, required/forbidden changes, tests/oracles, blocking/corroborative evidence, terminal success/blockers in `EXECUTION_CLOSURE_CONTRACT`; optional repo-local execution-authority materialization | blocking completion target is frozen; coding agent need not redesign system, refetch frozen upstream truth, or infer finish criteria |",
)
replace_stage_row(
    "skillset/skills/aegis/references/stage-contracts.md",
    "P32",
    "| P32 | Implementation | code/change, P32/P33 internal PackageBinding/ImplementationDesign/RED-oracle checkpoints when applicable, frozen required tests/evidence, durable result identities, terminal blocker if any | complete frozen closure contract reaches terminal success/`READY_FOR_CONTROL_REVIEW` or explicit terminal blocker without ordinary checkpoint return |",
)
replace_stage_row(
    "skillset/skills/aegis/references/stage-contracts.md",
    "P33",
    "| P33 | Resume | current state/diff, `completed_through`, `next_action`, optional design/oracle cursor state, safe continuation plus root-cause check for newly introduced work | valid work is preserved; P32/P33 internal checkpoints resume without expanding package; P20/P31 omissions route earlier |",
)

for rel in [
    "tests/skillset/test_openai_plugin_materialization.py",
]:
    text = read(rel).replace("0.2.0-beta.4", "0.2.0-beta.5")
    write(rel, text)

rel = "tests/skillset/test_control_plane_v02_release_candidate.py"
text = read(rel).replace('VERSION = "0.2.0-beta.4"', 'VERSION = "0.2.0-beta.5"')
historical_old = '("0.1.0-beta.1", "0.1.0-beta.2", "0.1.0-beta.3", "0.2.0-beta.1", "0.2.0-beta.2", "0.2.0-beta.3")'
historical_new = '("0.1.0-beta.1", "0.1.0-beta.2", "0.1.0-beta.3", "0.2.0-beta.1", "0.2.0-beta.2", "0.2.0-beta.3", "0.2.0-beta.4")'
if historical_old in text:
    text = text.replace(historical_old, historical_new, 1)
write(rel, text)

rel = "README.md"
text = read(rel).replace("v0.2.0-beta.4", "v0.2.0-beta.5")
if "### Repo-local Execution Authority" not in text:
    anchor = "### Stable execution closure\n"
    section = "### Repo-local Execution Authority\n\nBeta.5 materializes frozen execution truth under `.aegis/packages/<task-id>/`, uses progressive loading and thin surface handoffs, runs ImplementationDesignPreflight/RED Oracle Preflight inside P32/P33 when applicable, and preserves independent P34 Gate review. Missing `execution_authority_mode` remains legacy `remote`; `repo_materialized` and `hybrid` are additive.\n\n"
    if anchor not in text:
        raise SystemExit("README stable execution closure anchor missing")
    text = text.replace(anchor, section + anchor, 1)
if "Historical rollback boundary: `v0.2.0-beta.4`." not in text:
    text = text.rstrip() + "\n\nHistorical rollback boundary: `v0.2.0-beta.4`.\n"
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

print("BETA5_FINALIZE_CONTENT_OK")
