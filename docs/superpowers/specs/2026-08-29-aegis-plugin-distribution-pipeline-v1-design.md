# Aegis Plugin Distribution Pipeline V1 — Design

Status: **Design approved in chat on 2026-08-29; written spec awaiting human review.**

Related Authority / design work:

- `docs/plugin-distribution-contract-v0.1.md`
- `docs/superpowers/specs/2026-08-29-aegis-plugin-distribution-v0.1-design.md`
- `docs/superpowers/specs/2026-08-29-aegis-catalog-provenance-repair.md`
- `docs/superpowers/plans/2026-08-29-aegis-catalog-provenance-repair.md`

Official platform references checked on 2026-08-29:

- https://help.openai.com/en/articles/20001256
- https://help.openai.com/en/articles/20001066-skills-in-chatgpt

## 1. Product Goal

Aegis V1 must eliminate per-Skill installation work for normal users.

The target experience is:

```text
Aegis source
    ↓
CI validates one coherent release
    ↓
one Aegis Plugin release
    ↓
workspace admin publishes / enables once
    ↓
installation policy = Installed
    ↓
eligible workspace users receive Aegis automatically
    ↓
exact 9 Aegis Skills are available
```

The normal user must **not**:

- download the repository;
- split the release into nine folders;
- create nine ZIP files;
- upload nine Skills;
- reason about which specialist Skills are required;
- repair partial or mixed installations manually.

### V1 success criterion

For each Aegis release, the administrator performs at most one Plugin publication/rollout action after CI produces an accepted release package. Eligible ordinary users perform **zero manual Aegis Skill installation actions** and receive the exact nine-Skill Aegis catalog through the Plugin.

The workspace installation policy should be set to `Installed` for the intended eligible role(s), so normal user installation is automatic where the platform supports that policy.

## 2. First-Class Design Principle: Minimize Human Work

Aegis exists to reduce coordination burden, not to turn verification into additional manual operations.

Normative principle:

```text
credible evidence at the lowest human cost
```

Equivalent rule:

```text
Evidence completeness
!=
test every supported mode on every change
```

A Gate should prove the risk boundary of the current change. Optional compatibility paths must not become permanent human blockers for the normal product path unless the change can affect those paths.

This principle applies to both distribution and verification.

## 3. Product / Distribution Topology

The normal product topology remains:

```text
Aegis Product
└── Aegis Plugin
    ├── aegis
    ├── aegis-project-state
    ├── aegis-discovery
    ├── aegis-modeling
    ├── aegis-architecture
    ├── aegis-verification
    ├── aegis-governance
    ├── aegis-implementation
    └── aegis-gate-review
```

The Plugin is the installation and release envelope.

The nine Skills remain the reasoning / ownership units.

The Plugin remains **not** a tenth Primary Owner.

Standalone central `aegis` remains a compatibility distribution, but it is not the normal product installation path.

## 4. V1 Release Pipeline

### 4.1 Stage A — Source validation

CI starts from an exact repository revision and verifies:

- exact nine Skill identities;
- ownership metadata;
- generated Skill consistency;
- routing corpus integrity;
- Project State integrity;
- deterministic tests;
- release manifest consistency.

A release candidate that fails any deterministic obligation cannot proceed to packaging.

### 4.2 Stage B — Deterministic release manifest

CI generates one release manifest containing at minimum:

```yaml
product_id: aegis
release_version: <release>
source_revision: <exact commit SHA>
plugin_id: aegis
skills:
  - skill_id: aegis
    tree_sha256: <digest>
  - skill_id: aegis-project-state
    tree_sha256: <digest>
  - ... exact nine total
```

The release manifest is the machine-readable identity of the coherent Aegis release.

No Skill exposes an independent public SemVer line. The Plugin/release owns the public release identity; each Skill is pinned by exact digest/revision.

### 4.3 Stage C — One Plugin release package

CI produces one normal distribution artifact:

```text
aegis-plugin-<release>
├── release manifest
└── exact nine Skills
```

The repository may also continue to produce a standalone compatibility artifact, but it must be clearly separated from the normal product artifact and must not be offered as the default user installation path.

The release package must be reproducible from the same source revision.

### 4.4 Stage D — Platform publication boundary

Current OpenAI product documentation establishes that a Plugin can contain multiple Skills and that workspace administrators can manage Plugin installation policies. It does **not** establish a stable public CI API or a guaranteed local ZIP schema for programmatically publishing a custom multi-Skill Plugin into every ChatGPT workspace.

Therefore V1 defines an explicit publication boundary:

```text
CI automation
    ↓
reviewer-accessible accepted release package
    ↓
ONE supported Plugin publication/import action by owner/admin
    ↓
workspace Plugin
```

Until OpenAI exposes a stable supported publication API, Aegis must not invent or depend on an undocumented endpoint.

If a supported publication/import API becomes available later, this boundary may be automated without changing Skill ownership or release semantics.

### 4.5 Stage E — Workspace rollout

After the Aegis Plugin is available to the workspace, the administrator configures its installation policy as:

```text
Installed
```

for the intended eligible role(s), where the workspace supports role-based installation controls.

Expected user experience:

```text
admin publishes/enables Aegis Plugin
        ↓
workspace policy installs it automatically
        ↓
user opens ChatGPT
        ↓
Aegis capabilities are available
        ↓
0 manual Skill uploads
```

Underlying App permissions, if Aegis later includes Apps, remain separate from Plugin installation and do not change Primary Owner semantics.

## 5. Upgrade Semantics

Aegis upgrades at the Plugin/release level:

```text
Aegis Plugin release N
        ↓
whole-catalog transition
        ↓
Aegis Plugin release N+1
```

Desired externally observable state is always a coherent release.

The normal user must never be asked to update individual specialist Skills.

If the platform exposes a transient partial/mixed state during upgrade, Aegis fails closed for specialist-owned execution until the coherent catalog is restored.

A partial Plugin installation must never be reinterpreted as Standalone compatibility mode.

## 6. Rollback Semantics

A release must retain enough identity to restore the last accepted coherent Plugin release.

Rollback target:

```text
release N+1 rejected / broken
        ↓
restore accepted Plugin release N
        ↓
exact nine Skill digests from N
```

Rollback is release-level, never a hand-edited combination of Skill versions.

## 7. Gate Decomposition

The previous Task 6 shape over-coupled the normal product path to Standalone compatibility evidence. V1 separates the Gates by risk boundary.

### 7.1 Core Skill Composition Gate — blocking

Purpose: prove the normal nine-Skill Aegis system routes and owns work correctly.

Required environment:

```text
catalog_state = FULL_SPECIALIST
installed Aegis catalog = exact nine Skills
coherent release/component set
```

Required protected probes:

1. `Audit this PR against its Gate evidence.`
2. `What should this project do next?`
3. `Design module architecture, but project authority is unresolved.`

Acceptance:

```text
3 / 3 PASS
```

This Gate blocks Skill Decomposition acceptance because it validates the normal product topology.

### 7.2 Standalone Compatibility Regression — non-blocking for normal product changes

Purpose: prove central `aegis` can perform the documented composite fallback when specialists are genuinely unavailable.

Protected probe:

`Only composite Aegis is installed; design a semantic schema.`

This remains a normative compatibility regression but does **not** block the normal nine-Skill Core Composition Gate on every change.

It becomes blocking only when the change touches the compatibility risk boundary, including for example:

- `aegis` compatibility instructions;
- specialist-unavailable evidence semantics;
- fallback routing;
- Standalone packaging/distribution;
- compatibility-mode oracle behavior.

Otherwise it can run in scheduled/release regression or when the affected boundary changes.

### 7.3 Plugin Distribution Gate — separate blocking Gate for product distribution

Purpose: prove the product can be delivered as one coherent Plugin release without per-Skill user work.

Minimum acceptance evidence:

- one Aegis Plugin release maps to exact nine Skill digests;
- the Plugin is available in the target workspace;
- workspace installation policy is `Installed` for the intended eligible population;
- a normal user receives Aegis without manually uploading any Skill;
- installed Aegis catalog is exact nine and release-consistent;
- partial/mixed Plugin state fails closed;
- Plugin packaging creates no new lifecycle owner.

This Gate is separate from the Skill Composition Gate.

## 8. Test Selection by Change Impact

Verification should be impact-driven.

Conceptual mapping:

```text
routing / owner semantics changed
    -> Core Composition Gate

central compatibility/fallback changed
    -> Core Composition Gate + Compatibility Regression

Plugin packaging/release changed
    -> Plugin Distribution Gate

release manifest/digest changed
    -> deterministic release checks + Plugin Distribution Gate

unrelated docs changed
    -> do not force external platform reruns
```

The exact machine-readable impact selector can be introduced in implementation planning. V1 does not require a general-purpose test scheduler before the release pipeline itself works.

## 9. Human Interaction Budget

V1 explicitly budgets human actions.

### Normal end user

```text
manual Aegis Skill installs per release = 0
manual Aegis Skill ZIP operations = 0
manual catalog assembly = 0
```

### Workspace administrator / Plugin owner

Until a supported publication API exists:

```text
Plugin publication/import actions per release <= 1
workspace installation-policy setup = one-time per deployment policy, unless policy changes
```

After a stable publication API exists, the target becomes zero release-publication actions as well.

### Aegis maintainer

Maintainer effort should be concentrated on Authority, review, exceptional failures, and release approval — not repetitive packaging or catalog assembly.

## 10. Evidence Model

Distribution evidence should be generated as close to the source as possible.

```text
Git revision
    ↓
release manifest
    ↓
Plugin release artifact
    ↓
platform Plugin identity / publication event
    ↓
workspace installation policy
    ↓
observed exact-nine catalog
```

Each later evidence item should carry enough reference to resolve the earlier identity chain.

Behavior evidence remains separate:

```text
Catalog Evidence != Behavior Evidence
```

A screenshot may support platform observability, but it does not replace release identity or terminal behavior evidence when those are required.

## 11. Failure Modes

### CI package generation fails

Return repository implementation/test failure. Do not publish.

### Release manifest and source tree disagree

Return `MIXED_REVISION` / deterministic release failure. Do not publish.

### Platform publication/import unavailable

Return `BLOCKED_ENVIRONMENT` for Plugin Distribution Gate only. Do not force users to install nine Skills as the product workaround.

Individually imported exact-nine Skills may still be used for the separate Skill Composition Gate because catalog state and distribution provenance are orthogonal.

### Plugin visible but partial catalog observed

Return `BLOCKED_ENVIRONMENT`; do not invoke compatibility fallback.

### Workspace policy cannot auto-install

Plugin Distribution V1 acceptance is not complete for the intended zero-touch deployment population. Do not redefine success as nine manual Skill installations.

## 12. Non-Goals

V1 does not require:

- inventing an undocumented OpenAI Plugin publication API;
- inventing a private Plugin ZIP schema and claiming platform compatibility;
- making Standalone Aegis the normal product path;
- automatically connecting future external Apps;
- removing the nine independent Skill identities;
- changing Aegis ownership semantics;
- changing `terminal_trace_v0.2` semantics;
- running every compatibility environment on every repository change.

## 13. V1 Acceptance Criteria

The design is implemented successfully when all of the following are true:

1. CI deterministically produces one coherent Aegis Plugin release artifact from an exact source revision.
2. The artifact pins the exact nine Skills and their digests.
3. The Plugin/release is the normal installation unit; nine individual Skill ZIPs are not part of the normal user workflow.
4. A supported Plugin publication/import action can materialize that release into the target workspace, or Plugin Distribution reports `BLOCKED_ENVIRONMENT` without semantic fallback.
5. Workspace admin can set the Plugin to `Installed` for the intended eligible population where that control is supported.
6. An eligible ordinary user performs zero manual Aegis Skill installation actions.
7. The resulting observed Aegis catalog is exact nine and release-consistent.
8. Core Skill Composition acceptance uses the normal `FULL_SPECIALIST` environment and requires the protected normal-path probes to pass 3/3.
9. Standalone composite fallback remains a compatibility regression and is not a permanent blocker for unrelated normal-path changes.
10. Plugin Distribution acceptance remains separate from Skill Composition acceptance.
11. No Plugin/distribution object becomes a lifecycle Primary Owner.
12. Existing historical integration truth, Gate history, and protected routing semantics are not rewritten.

## 14. Future Extension

When OpenAI exposes a stable supported publication/import API, the publication boundary can become:

```text
CI accepted release
    ↓
automated Plugin publish/update
    ↓
workspace Installed policy
    ↓
zero-touch rollout
```

That future automation must preserve the same release manifest, exact-nine catalog contract, fail-closed mixed-revision rules, and ownership boundaries defined here.
