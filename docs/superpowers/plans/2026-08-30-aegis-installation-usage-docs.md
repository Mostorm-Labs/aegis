# Aegis Installation & Usage Documentation Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the accepted Aegis v0.1 Plugin distribution and v0.1.0-beta.2 nine-Skill Release installation paths obvious, accurate, and directly usable from the repository entrypoint.

**Architecture:** Documentation-only closure. Keep the existing native Plugin implementation, release assets, release tag, Project State manifests, and P34 evidence unchanged. Update the repository front door, add one canonical installation/usage guide, and align the stale Plugin Distribution Authority document header with the already-integrated Project State v0.5 truth.

**Tech Stack:** Markdown, GitHub Release assets, ChatGPT Plugin marketplace import, Aegis Project State v0.5, GitHub Actions.

**Spec:** `docs/plugin-distribution-contract-v0.1.md`

## Global Constraints

- Do not change Plugin implementation under `.agents/plugins/**` or `plugins/aegis/**`.
- Do not modify, recreate, or republish GitHub Release `v0.1.0-beta.2`.
- Do not change `.aegis/**`; Project State already records `aegis-plugin-distribution-v0.1` as `Current`, `gate-plugin-distribution-v01-pr13::decision::0001` as `PASS`, and `int-pr13` as current/conforming.
- Preserve the historical lifecycle wording in `docs/releases/v0.1.0-beta.2.md`; it records publication-time facts.
- Normal product guidance must prefer the native Plugin; the nine-Skill Installation Kit remains the portable/fallback path.
- A successful normal Plugin installation means one Aegis Plugin materializes the exact nine canonical Skills, not a partial catalog.
- Release version in this closure is exactly `0.1.0-beta.2`.
- Plugin marketplace repository URL is exactly `https://github.com/Mostorm-Labs/aegis`.

---

### Task 1: Replace the stale README installation story

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: current Plugin distribution contract and published `v0.1.0-beta.2` Release.
- Produces: repository front-door install instructions and link to the canonical usage guide.

- [ ] **Step 1: Replace the obsolete single-Skill packaging description**

Replace the existing `## What is included` section with a current product-level description that states:

```markdown
## What is included

Aegis v0.1 is distributed primarily as one native **Aegis Plugin** that materializes the exact nine canonical Skills:

1. `aegis`
2. `aegis-project-state`
3. `aegis-discovery`
4. `aegis-modeling`
5. `aegis-architecture`
6. `aegis-verification`
7. `aegis-governance`
8. `aegis-implementation`
9. `aegis-gate-review`

The GitHub Release also publishes a portable **9-Skill Installation Kit** containing nine directly uploadable Skill ZIPs for environments where Plugin marketplace distribution is unavailable.
```

- [ ] **Step 2: Replace the obsolete `Install / package` section**

Use exactly these two public entrypoints and prefer Plugin installation:

```markdown
## Install Aegis

### Recommended: GitHub Plugin

In ChatGPT Workspace settings, import the Plugin marketplace from:

```text
https://github.com/Mostorm-Labs/aegis
```

Use the repository root marketplace manifest (`.agents/plugins/marketplace.json`). Installing **Aegis** should materialize one Plugin with the exact nine canonical Skills.

### Alternative: 9-Skill Installation Kit

Download the `v0.1.0-beta.2` Release asset:

```text
https://github.com/Mostorm-Labs/aegis/releases/download/v0.1.0-beta.2/aegis-skill-installation-kit-v0.1.0-beta.2.zip
```

Extract the outer archive once, then upload the nine nested Skill ZIPs without unpacking them.

See [`docs/installation-and-usage-v0.1.md`](docs/installation-and-usage-v0.1.md) for exact installation, verification, usage, update, and troubleshooting instructions.
```

- [ ] **Step 3: Align README status and documentation links**

Replace the stale status sentence with:

```markdown
**v0.1 — Usable evidence-driven development control plane with accepted native Plugin distribution and a published nine-Skill Installation Kit.**
```

Add `docs/installation-and-usage-v0.1.md` and `docs/plugin-distribution-contract-v0.1.md` to the Documentation list.

- [ ] **Step 4: Check README for stale packaging claims**

Verify that the README no longer claims that normal Aegis v0.1 is packaged only as one standalone Skill, while preserving the explanation of the 25 core stages and Aegis + Superpowers composition.

---

### Task 2: Add the canonical installation and usage guide

**Files:**
- Create: `docs/installation-and-usage-v0.1.md`

**Interfaces:**
- Consumes: Plugin marketplace repository URL, exact-nine catalog contract, `v0.1.0-beta.2` Release assets, accepted Plugin Distribution P34 behavior.
- Produces: one user-facing document that can be handed directly to teammates or customers.

- [ ] **Step 1: Create the guide with a clear product choice**

Start with:

```markdown
# Aegis Installation & Usage Guide v0.1

Aegis is an evidence-driven software development control plane. The recommended installation is one native Aegis Plugin that materializes the exact nine canonical Skills. A portable nine-Skill Release kit is available as a fallback.

## Choose an installation path

| Situation | Recommended path |
| --- | --- |
| ChatGPT workspace with Plugin marketplace access | GitHub Plugin |
| Team/developer environment that should update as one product | GitHub Plugin |
| No Plugin marketplace access | 9-Skill Installation Kit |
| Offline archive or individual Skill testing | 9-Skill Installation Kit |
```

- [ ] **Step 2: Document GitHub Plugin installation**

Include the exact administrator flow:

```markdown
## Recommended: install the Aegis Plugin from GitHub

1. Open ChatGPT **Workspace settings**.
2. Open **Plugins**.
3. Choose **Add** / **Import marketplace**.
4. Set the repository source to:

   ```text
   https://github.com/Mostorm-Labs/aegis
   ```

5. Use the repository root marketplace manifest. Leave the path empty when the UI resolves `.agents/plugins/marketplace.json` from the repository root.
6. Select the imported **Aegis** Plugin and install it.
7. Open the installed Plugin details and verify the exact-nine catalog listed below.

The repository marketplace manifest points to `./plugins/aegis`, and that Plugin manifest points to `./skills/`. The Plugin is the distribution envelope; it is not a tenth lifecycle owner.
```

Also state that a branch/tag/commit pin may be used when the ChatGPT import UI exposes that field and reproducibility is required; otherwise normal product use should follow the maintained repository branch configured by the workspace administrator.

- [ ] **Step 3: Define exact-nine success criteria**

Include this exact catalog:

```text
aegis
aegis-project-state
aegis-discovery
aegis-modeling
aegis-architecture
aegis-verification
aegis-governance
aegis-implementation
aegis-gate-review
```

State explicitly:

```text
one Aegis Plugin + exact nine Skills = normal FULL_SPECIALIST installation
partial Aegis catalog              = incomplete / fail closed
```

- [ ] **Step 4: Document Release-kit installation**

Use these exact public artifacts:

```text
Release page:
https://github.com/Mostorm-Labs/aegis/releases/tag/v0.1.0-beta.2

Installation Kit:
https://github.com/Mostorm-Labs/aegis/releases/download/v0.1.0-beta.2/aegis-skill-installation-kit-v0.1.0-beta.2.zip

Installation Kit SHA-256:
1175ffcf0e66e52736dfb4e897e37bd39dbb51a2b41840de3f45c318f3cccd00
```

Explain: download the outer ZIP, optionally verify `SHA256SUMS`, extract the outer ZIP exactly once, and upload the nine nested ZIPs directly as Skills without unpacking those nested archives.

- [ ] **Step 5: Document normal usage and routing**

Include these example prompts:

```text
What should this project do next?
Design the semantic schema for this feature.
Audit this implementation against its Gate evidence.
```

Explain that users normally state the project task rather than manually selecting one of nine Skills. The central `aegis` entrypoint and owning specialists route work by lifecycle stage, Authority, earliest untrusted layer, evidence, and Gate state.

- [ ] **Step 6: Document update and failure behavior**

State that Plugin updates are whole-catalog transitions. If the ChatGPT workspace exposes marketplace synchronization, administrators may use its sync control to refresh the repository-backed Plugin. An invalid or partial Aegis catalog must not silently degrade into standalone compatibility; keep the last known coherent installation or repair the source before accepting the update.

- [ ] **Step 7: Add troubleshooting**

Cover these exact cases:

```markdown
- **Plugin imports but fewer than nine Aegis Skills are visible:** treat the installation as incomplete; do not continue as normal multi-Skill Aegis.
- **Nine-Skill kit was unpacked too far:** return to the outer kit and upload the nine nested ZIP files themselves.
- **Plugin marketplace import is unavailable:** use the Release-kit path.
- **A workspace has both Plugin and separately installed duplicate Aegis components:** remove the duplicate distribution before relying on the environment.
- **Need a reproducible historical installation:** pin the GitHub import to an immutable tag/commit when the platform exposes that control, or use the immutable Release kit.
```

---

### Task 3: Align the Plugin Distribution Authority document with integrated lifecycle truth

**Files:**
- Modify: `docs/plugin-distribution-contract-v0.1.md`

**Interfaces:**
- Consumes: `.aegis/authorities.json`, `.aegis/state.json`, immutable P34 Gate Decision, and `int-pr13` integration closure already on `main`.
- Produces: a non-stale human-readable Authority document without changing the normative distribution semantics.

- [ ] **Step 1: Replace only the stale lifecycle header**

Replace the current status line with:

```markdown
Status: **Current Authority v0.1 — P34 Gate accepted; published in Aegis `v0.1.0-beta.2`; PR #13 repository integration closed as current/conforming under Project State v0.5.**
```

- [ ] **Step 2: Replace the stale draft-repair paragraph**

Preserve the historical fact of the 2026-08-29 repair, but remove the false claim that the Authority is still Proposed. Use:

```markdown
The 2026-08-29 P34 installed-platform intake found and corrected one draft defect: the earlier draft coupled runtime **Catalog State** to **Distribution Provenance**. That coupling conflicted with Skill Decomposition v0.2, which allows specialist availability to be proven by installed-Skill inventory or an equivalent observable platform fact. The repair was accepted before the final Plugin Distribution P34 Gate; Git history and the P34 evidence preserve the prior wording and repair lineage.
```

- [ ] **Step 3: Update only the final product-acceptance sentence in Exit Criteria**

Replace the future-tense statement that a later Plugin Gate is still required with:

```markdown
For Plugin Distribution v0.1 product acceptance, the normal Plugin must additionally prove exact-nine materialization and packaging/upgrade safety. That separate product Gate has now passed; this does not change the distinction that PR #9 Task 6 itself only requires catalog and behavior evidence.
```

Do not change any matrix, catalog-state, provenance, upgrade, ownership, or historical-integration semantics.

---

### Task 4: Verify the documentation-only closure on the exact PR head

**Files:**
- Verify: `README.md`
- Verify: `docs/installation-and-usage-v0.1.md`
- Verify: `docs/plugin-distribution-contract-v0.1.md`
- Verify: `docs/releases/v0.1.0-beta.2.md` remains unchanged
- Verify: `.aegis/**`, `.agents/plugins/**`, and `plugins/aegis/**` remain unchanged

**Interfaces:**
- Consumes: completed documentation changes.
- Produces: merge-ready documentation PR with evidence that no implementation/release/state mutation occurred.

- [ ] **Step 1: Review the branch diff**

Expected changed files are exactly:

```text
README.md
docs/installation-and-usage-v0.1.md
docs/plugin-distribution-contract-v0.1.md
docs/superpowers/plans/2026-08-30-aegis-installation-usage-docs.md
```

- [ ] **Step 2: Verify public links and exact version strings**

Confirm all user-facing installation links point to `Mostorm-Labs/aegis`, all Release references use `v0.1.0-beta.2`, and the exact-nine catalog contains no missing or extra Aegis Skill IDs.

- [ ] **Step 3: Run repository verification**

On a normal checkout, run:

```bash
python3 -m tools.aegis_state.cli validate .
python3 -m tools.aegis_state.cli check .
python3 -m tools.aegis_skillset.cli validate .
python3 -m unittest discover -s tests/project_state -v
python3 -m unittest discover -s tests/skillset -v
python3 evals/scripts/validate_corpus.py
python3 -m unittest discover -s evals/tests -v
```

In an environment where the repository cannot be cloned, require the exact-head GitHub Actions `Aegis Project State Integrity` workflow to complete successfully; that workflow executes the same root-state, Skillset, corpus, and regression checks for this contract change.

- [ ] **Step 4: Merge only after exact-head verification**

Use fail-closed expected-head merge semantics. After merge, verify the `main` push workflow is successful and confirm `v0.1.0-beta.2` Release/tag/assets are unchanged.
