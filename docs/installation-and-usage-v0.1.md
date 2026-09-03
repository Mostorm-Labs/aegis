# Aegis Installation & Usage Guide v0.1

Aegis is an evidence-driven software development control plane. The recommended installation is one native **Aegis Plugin** that materializes the exact nine canonical Skills. A portable **9-Skill Installation Kit** is available as a fallback.

This guide describes the accepted Aegis `v0.1.0-beta.3` distribution paths.

## Choose an installation path

| Situation | Recommended path |
| --- | --- |
| ChatGPT workspace with Plugin marketplace access | GitHub Plugin |
| Team/developer environment that should update as one product | GitHub Plugin |
| No Plugin marketplace access | 9-Skill Installation Kit |
| Offline archive or individual Skill testing | 9-Skill Installation Kit |

For normal product use, prefer the Plugin. The Plugin owns distribution/install coherence; it is not a tenth Aegis lifecycle owner.

## Recommended: install the Aegis Plugin from GitHub

### 1. Import the marketplace

In ChatGPT:

1. Open **Workspace settings**.
2. Open **Plugins**.
3. Choose **Add** / **Import marketplace**.
4. In **Source**, enter the repository URL only:

   ```text
   https://github.com/Mostorm-Labs/aegis
   ```

   Do not append `/tree/...`, a branch name, or a folder path to the Source URL.
5. Leave **Path** empty so ChatGPT resolves the repository-root `.agents/plugins/marketplace.json`. Do not enter the manifest filename itself.
6. Optionally set **Branch, tag, or commit**:
   - **Maintained repository state:** leave it empty to use the repository default branch, or select the workspace-approved maintained branch.
   - **Immutable `v0.1.0-beta.3` installation:** pin the tag `v0.1.0-beta.3`.
7. Select **Import marketplace** and complete GitHub authorization if prompted.
8. Review the import result.

The repository marketplace manifest declares one `aegis` Plugin and points it to `./plugins/aegis`. The Plugin manifest then points its Skills directory to `./skills/`.

### 2. Install Aegis

After the marketplace is imported:

1. Find **Aegis** in the imported marketplace.
2. Install the Plugin, or have the workspace administrator configure its installation policy for the intended roles.
3. Open the installed Aegis Plugin details.
4. Verify that the full nine-Skill catalog is present.

## Verify the exact-nine catalog

A normal Plugin installation must expose exactly these nine canonical Skill IDs:

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

The acceptance rule is:

```text
one Aegis Plugin + exact nine Skills = normal FULL_SPECIALIST installation
partial Aegis catalog              = incomplete / fail closed
```

UI ordering is not significant. The catalog is set-based: all nine entries must be present, with no partial Aegis Plugin state accepted as normal operation.

## Alternative: install the 9-Skill Release kit

Use this path when Plugin marketplace distribution is unavailable or when you need a portable archive.

### Release artifacts

```text
Release page:
https://github.com/Mostorm-Labs/aegis/releases/tag/v0.1.0-beta.3

Installation Kit:
https://github.com/Mostorm-Labs/aegis/releases/download/v0.1.0-beta.3/aegis-skill-installation-kit-v0.1.0-beta.3.zip

Verification:
Use the Release-provided SHA256SUMS or aegis-release-v0.1.0-beta.3.json.
```

The Release publishes `SHA256SUMS` and `aegis-release-v0.1.0-beta.3.json` for checksum and release-manifest verification.

### Installation steps

1. Download `aegis-skill-installation-kit-v0.1.0-beta.3.zip`.
2. Verify the archive against the Release-provided `SHA256SUMS` or `aegis-release-v0.1.0-beta.3.json`.
3. Extract the **outer** Installation Kit exactly once.
4. Keep the nine nested Skill ZIPs intact; do **not** unpack the nested ZIPs.
5. In ChatGPT, open **Plugins** -> **Skills** -> **Create** -> **Upload from your computer**.
6. Upload the nine nested Skill ZIPs themselves.
7. Verify that the installed Aegis-family catalog contains the same exact-nine IDs listed above.

The outer kit contains these directly uploadable archives:

```text
aegis.zip
aegis-project-state.zip
aegis-discovery.zip
aegis-modeling.zip
aegis-architecture.zip
aegis-verification.zip
aegis-governance.zip
aegis-implementation.zip
aegis-gate-review.zip
```

## How to use Aegis

Users normally describe the project task. They do not need to manually choose one of the nine Skills for every step.

Good starting prompts include:

```text
What should this project do next?
```

```text
Design the semantic schema for this feature.
```

```text
Audit this implementation against its Gate evidence.
```

Aegis routes work according to project lifecycle state, Current Authority, the earliest untrusted layer, required evidence, and Gate state. The central `aegis` entrypoint handles product-level routing; specialist Skills own their corresponding stages and contracts.

A simplified flow is:

```text
User task
   ↓
Aegis routing
   ↓
Current Authority + project state preflight
   ↓
Owning Skill / stage
   ↓
Evidence-producing work
   ↓
Gate review
   ↓
continue | block | repair | integrate | release
```

## Updating a GitHub-backed Plugin

Aegis Plugin updates are whole-catalog transitions. Do not accept an update that leaves the environment with a partial or mixed Aegis catalog.

A newly imported GitHub marketplace has automatic daily sync enabled. To request an update immediately:

1. Open **Workspace settings** -> **Plugins**.
2. Open **Marketplaces**.
3. Select the Aegis marketplace.
4. Select **Sync now**.
5. Review the sync result and verify the exact-nine catalog again before relying on the environment.

The repository marketplace source/path remains stable across this maintenance update; the Aegis Plugin manifest version advances to `0.1.0-beta.3` together with the coherent exact-nine Skill tree. This makes `v0.1.0-beta.2` -> `v0.1.0-beta.3` a useful real-world whole-catalog sync test.

For reproducible environments, pin an immutable tag or commit. For `v0.1.0-beta.3`, the immutable release tag is:

```text
v0.1.0-beta.3
```

If an update to the existing Plugin is invalid, ChatGPT retains the last working version while valid updates can continue. Fix the source problem and use **Sync now** to retry. A partial Aegis catalog must never be treated as standalone compatibility.

## Troubleshooting

- **Plugin imports but fewer than nine Aegis Skills are visible:** treat the installation as incomplete; do not continue as normal multi-Skill Aegis.
- **Nine-Skill kit was unpacked too far:** return to the outer kit and upload the nine nested ZIP files themselves.
- **Plugin marketplace import is unavailable:** use the Release-kit path.
- **A workspace has both Plugin and separately installed duplicate Aegis components:** remove the duplicate distribution before relying on the environment.
- **Need a reproducible historical installation:** pin the GitHub import to an immutable tag/commit, or use the immutable Release kit.
- **Aegis appears installed but behavior is unexpected:** first confirm the exact-nine catalog and coherent distribution state before debugging routing or Gate behavior.
- **A GitHub sync reports an invalid Aegis update:** keep the retained last working version, repair the repository source, then run **Sync now** again.

## Distribution model

The normal product model is:

```text
Aegis Product
│
├── Aegis Plugin                 ← recommended normal distribution
│   └── exact nine Skills
│
└── Standalone / Release paths   ← compatibility, fallback, archive
```

The authoritative distribution semantics are defined in [`plugin-distribution-contract-v0.1.md`](plugin-distribution-contract-v0.1.md). The published `v0.1.0-beta.3` release notes are in [`releases/v0.1.0-beta.3.md`](releases/v0.1.0-beta.3.md).

## Platform references

Current ChatGPT platform behavior is documented by OpenAI here:

- GitHub marketplace import and sync: `https://help.openai.com/en/articles/20001504`
- Skills installation and upload: `https://help.openai.com/en/articles/20001066`
