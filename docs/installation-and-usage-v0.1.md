# Aegis Installation & Usage Guide v0.1

Aegis is an evidence-driven software development control plane. The recommended installation is one native **Aegis Plugin** that materializes the exact nine canonical Skills. A portable **9-Skill Installation Kit** is available as a fallback.

This guide describes the accepted Aegis `v0.1.0-beta.2` distribution paths.

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
4. Set the repository source to:

   ```text
   https://github.com/Mostorm-Labs/aegis
   ```

5. Use the repository root marketplace manifest. Leave the path empty when the UI resolves `.agents/plugins/marketplace.json` from the repository root.
6. If the import UI asks for a branch, tag, or commit, choose one of these policies:
   - **Maintained repository state:** use the workspace-approved maintained branch, normally `main`.
   - **Immutable `v0.1.0-beta.2` installation:** pin the tag `v0.1.0-beta.2`.
7. Import the marketplace.

The repository marketplace manifest declares one `aegis` Plugin and points it to `./plugins/aegis`. The Plugin manifest then points its Skills directory to `./skills/`.

### 2. Install Aegis

After the marketplace is imported:

1. Find **Aegis** in the imported marketplace.
2. Install the Plugin.
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
https://github.com/Mostorm-Labs/aegis/releases/tag/v0.1.0-beta.2

Installation Kit:
https://github.com/Mostorm-Labs/aegis/releases/download/v0.1.0-beta.2/aegis-skill-installation-kit-v0.1.0-beta.2.zip

Installation Kit SHA-256:
1175ffcf0e66e52736dfb4e897e37bd39dbb51a2b41840de3f45c318f3cccd00
```

The Release also publishes `SHA256SUMS` and `aegis-release-v0.1.0-beta.2.json` for checksum and release-manifest verification.

### Installation steps

1. Download `aegis-skill-installation-kit-v0.1.0-beta.2.zip`.
2. Optionally verify the archive against `SHA256SUMS` or the SHA-256 value above.
3. Extract the **outer** Installation Kit exactly once.
4. Keep the nine nested Skill ZIPs intact; do **not** unpack the nested ZIPs.
5. Upload the nine nested ZIPs to ChatGPT Skills.
6. Verify that the installed Aegis-family catalog contains the same exact-nine IDs listed above.

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

When the ChatGPT workspace exposes marketplace synchronization, an administrator may use the marketplace sync control to refresh the repository-backed Plugin. After synchronization, verify the exact-nine catalog again before relying on the environment.

For reproducible environments, pin an immutable tag or commit when the import UI exposes that control. For `v0.1.0-beta.2`, the immutable release tag is:

```text
v0.1.0-beta.2
```

An invalid or partial Plugin update must not silently degrade into standalone compatibility. Keep or restore the last coherent installation, or repair the source before accepting the update.

## Troubleshooting

- **Plugin imports but fewer than nine Aegis Skills are visible:** treat the installation as incomplete; do not continue as normal multi-Skill Aegis.
- **Nine-Skill kit was unpacked too far:** return to the outer kit and upload the nine nested ZIP files themselves.
- **Plugin marketplace import is unavailable:** use the Release-kit path.
- **A workspace has both Plugin and separately installed duplicate Aegis components:** remove the duplicate distribution before relying on the environment.
- **Need a reproducible historical installation:** pin the GitHub import to an immutable tag/commit when the platform exposes that control, or use the immutable Release kit.
- **Aegis appears installed but behavior is unexpected:** first confirm the exact-nine catalog and coherent distribution state before debugging routing or Gate behavior.

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

The authoritative distribution semantics are defined in [`plugin-distribution-contract-v0.1.md`](plugin-distribution-contract-v0.1.md). The published `v0.1.0-beta.2` release notes are in [`releases/v0.1.0-beta.2.md`](releases/v0.1.0-beta.2.md).
