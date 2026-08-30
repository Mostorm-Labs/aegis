# Aegis PD-P34-01 Plugin Materialization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:test-driven-development for implementation. Execute only PD-P34-01; do not proceed into real platform install/upgrade cases in the same task.

**Goal:** Materialize one OpenAI-native GitHub Marketplace Aegis Plugin source containing the exact nine canonical Skills and prove deterministic source parity RED -> GREEN.

**Architecture:** `skills/<skill-id>/` remains canonical. A small deterministic materializer renders the native marketplace/plugin manifests and copies the exact nine canonical Skill trees into `plugins/aegis/skills/`. Check mode compares the committed Plugin materialization against canonical source and the committed Aegis release manifest so generated Plugin content cannot drift into a second Authority.

**Tech Stack:** Python 3.12, JSON, pathlib/shutil/hashlib, unittest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-08-29-aegis-plugin-distribution-p34-final-gate-v0.1.md`

## Global Constraints

- PD-P34-01 only; PD-P34-02 through PD-P34-05 remain out of scope.
- Canonical Plugin catalog is exactly the nine entries from `skillset/distribution.json`.
- Canonical Skill content is `skills/<skill-id>/`; `plugins/aegis/skills/<skill-id>/` is generated materialization only.
- Initial Plugin release identity is strict SemVer `0.1.0-beta.1`, bound to `skillset/releases/aegis-0.1.0-beta.1.json`.
- Plugin v0.1 has zero Apps and zero MCP servers.
- Marketplace path is `.agents/plugins/marketplace.json`; Plugin manifest path is `plugins/aegis/.codex-plugin/plugin.json`.
- Native manifest structure follows the OpenAI `openai/codex` plugin-creator contract snapshot at commit `6478a751fde8884b2fdc76486fe23175a8e795d4`.
- Existing Installation Kit generation remains required and unchanged; Plugin addition may not delete or replace it.
- Do not change Skill ownership, protected routing corpus, `terminal_trace_v0.2`, Project State history, or the nine canonical Skill instructions.
- No production implementation before a failing PD-P34-01 test is observed.

---

### Task 1: RED — Define the PD-P34-01 repository oracle

**Files:**
- Create: `tests/skillset/test_openai_plugin_materialization.py`

**Interfaces:**
- Consumes: `skillset/distribution.json`, `skillset/releases/aegis-0.1.0-beta.1.json`, canonical `skills/*`.
- Produces: executable expectations for marketplace/plugin existence, native manifest fields, exact-nine inventory, release identity, zero-App/MCP contract, and canonical tree equality.

- [ ] **Step 1: Write failing repository-shape tests**

Add tests that require:

```text
.agents/plugins/marketplace.json
plugins/aegis/.codex-plugin/plugin.json
plugins/aegis/skills/<exact-nine>/
```

The first RED must fail because these paths do not yet exist.

- [ ] **Step 2: Add manifest assertions without importing new production code**

The test reads JSON directly and asserts:

```python
marketplace["plugins"][0]["name"] == "aegis"
marketplace["plugins"][0]["source"] == {
    "source": "local",
    "path": "./plugins/aegis",
}
marketplace["plugins"][0]["policy"] == {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL",
}
plugin["name"] == "aegis"
plugin["version"] == "0.1.0-beta.1"
plugin["skills"] == "./skills/"
"apps" not in plugin
"mcpServers" not in plugin
```

Assert required native interface fields are non-empty and `capabilities` / `defaultPrompt` are non-empty arrays.

- [ ] **Step 3: Add exact-nine and tree-parity assertions**

Use existing `tree_sha256` from `tools.aegis_skillset.package` to require:

```python
set(plugin_skill_dirs) == set(distribution["plugin"]["skills"])
tree_sha256(plugin_skill_dir) == tree_sha256(canonical_skill_dir)
```

Also assert the Plugin version matches the committed release manifest's `release_version`.

- [ ] **Step 4: Run the focused test and record RED**

Run:

```bash
python3 -m unittest tests.skillset.test_openai_plugin_materialization -v
```

Expected: FAIL because marketplace/native Plugin materialization is absent.

- [ ] **Step 5: Commit the RED test alone**

Commit message:

```text
test: define PD-P34-01 plugin materialization oracle
```

Record the exact failing workflow run as PD-P34-01 RED evidence.

### Task 2: GREEN — Add deterministic OpenAI Plugin materializer

**Files:**
- Create: `tools/aegis_skillset/plugin_materialization.py`
- Create: `scripts/build_openai_plugin_materialization.py`
- Generate: `.agents/plugins/marketplace.json`
- Generate: `plugins/aegis/.codex-plugin/plugin.json`
- Generate: `plugins/aegis/skills/**`

**Interfaces:**
- Consumes: `skillset/distribution.json`, committed release manifest, canonical `skills/*`.
- Produces: `write_materialization(root, release_version)` and `check_materialization(root, release_version)` behavior exposed by the script CLI.

- [ ] **Step 1: Implement native manifest rendering**

Render marketplace JSON with:

```json
{
  "name": "mostorm-labs-aegis",
  "interface": {"displayName": "Mostorm Labs Aegis"},
  "plugins": [{
    "name": "aegis",
    "source": {"source": "local", "path": "./plugins/aegis"},
    "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
    "category": "Productivity"
  }]
}
```

Render `.codex-plugin/plugin.json` with strict SemVer, `skills = ./skills/`, zero App/MCP fields, and required native interface metadata.

- [ ] **Step 2: Implement canonical exact-nine materialization**

Read `skillset/distribution.json`, require exactly nine Plugin Skill IDs, remove any stale generated Plugin root, and copy each canonical `skills/<id>/` tree into `plugins/aegis/skills/<id>/`.

Do not copy Standalone or unrelated Skills.

- [ ] **Step 3: Bind materialization to the committed release manifest**

Before write/check, load `skillset/releases/aegis-<release>.json` and require:

```python
release["release_version"] == release_version
[entry["name"] for entry in release["plugin"]["skills"]] == expected_skill_ids
```

For each canonical Skill, require current `tree_sha256` to equal the tree digest pinned by that release manifest. If canonical source has advanced without a new release, materialization fails closed instead of silently relabeling changed Skills as the old release.

- [ ] **Step 4: Implement `--write` and `--check`**

CLI:

```bash
python3 scripts/build_openai_plugin_materialization.py --release-version 0.1.0-beta.1 --write
python3 scripts/build_openai_plugin_materialization.py --release-version 0.1.0-beta.1 --check
```

`--check` performs no writes and exits non-zero on manifest drift, missing/extra Skill, or tree mismatch.

- [ ] **Step 5: Generate the committed Plugin source**

Run `--write`, then inspect the generated tree and ensure there are exactly nine Plugin Skill directories.

- [ ] **Step 6: Run focused tests**

Run:

```bash
python3 -m unittest tests.skillset.test_openai_plugin_materialization -v
python3 scripts/build_openai_plugin_materialization.py --release-version 0.1.0-beta.1 --check
```

Expected: PASS.

### Task 3: GREEN — Put materialization drift under CI

**Files:**
- Modify: `.github/workflows/skillset.yml`

**Interfaces:**
- Consumes: materializer/check CLI from Task 2.
- Produces: hosted CI evidence that canonical Skill changes cannot leave Plugin materialization stale.

- [ ] **Step 1: Extend workflow path triggers**

Include:

```text
.agents/plugins/**
plugins/aegis/**
tools/aegis_skillset/plugin_materialization.py
scripts/build_openai_plugin_materialization.py
```

- [ ] **Step 2: Add deterministic check step**

Run before packaging publication:

```bash
python3 scripts/build_openai_plugin_materialization.py --release-version 0.1.0-beta.1 --check
```

- [ ] **Step 3: Run full Skillset regressions**

Hosted workflow must retain existing Installation Kit upload, routing, installed-platform, Project State, corpus, and eval steps.

Expected: all existing steps plus Plugin materialization check PASS.

### Task 4: Materialize reviewer-accessible PD-P34-01 evidence

**Files:**
- Modify: PR #13 durable conversation/body as evidence metadata; do not write a PASS decision into `.aegis/gates.json` before independent P34 review.

**Interfaces:**
- Consumes: exact GREEN commit and hosted workflow run.
- Produces: `result_revision`, `materialized_ref`, RED run, GREEN run, and PD-P34-01 review packet.

- [ ] **Step 1: Record RED evidence**

Record the exact RED commit/workflow and expected failure reason: native Plugin materialization absent.

- [ ] **Step 2: Record GREEN evidence**

Record exact GREEN commit and hosted CI run proving:

```text
native marketplace shape PASS
native plugin manifest PASS
exact-nine inventory PASS
canonical tree parity PASS
release binding PASS
zero Apps/MCP PASS
existing regressions PASS
Installation Kit path retained PASS
```

- [ ] **Step 3: Return to P34**

Return:

```yaml
stage: P32
package_ref: PD-P34-01
result_revision: <exact-green-sha>
materialized_ref: <PR13-or-exact-GitHub-ref>
return_surface: CONTROL_REVIEW
```

PD-P34-02 remains blocked on a fresh real ChatGPT Plugin install event.

## Self-Review

- Spec coverage: this plan implements only PD-P34-01 and preserves all Final Gate non-regression invariants.
- No placeholders are authorized in production manifests.
- Generated Plugin Skill trees remain derivative of canonical `skills/*` and are checked for exact parity.
- Installation Kit continues as a parallel release adapter and is not modified or removed by this plan.
