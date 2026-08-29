# Aegis Plugin Distribution P34 Final Gate Design v0.1

Status: **Approved Final Gate Design v0.1 — human-approved 2026-08-29; P35 repair amendment F13-PD01-01 incorporated; Gate not yet accepted.**

Gate ID: `gate-plugin-distribution-v01-pr13`

Owning Proposed Authority:

- `docs/plugin-distribution-contract-v0.1.md`
- `docs/superpowers/specs/2026-08-29-aegis-plugin-distribution-v0.1-design.md`
- upstream Skill topology: `docs/skill-decomposition-v0.2.md`
- portable distribution adapter: `docs/superpowers/specs/2026-08-29-aegis-plugin-distribution-pipeline-v1-design.md`

Current platform oracle snapshot used by this design:

- OpenAI Help Center, `Importing and syncing plugin marketplaces from GitHub`, consulted 2026-08-29: GitHub workspace import recognizes `.agents/plugins/marketplace.json`, supports public/private GitHub sources, and sync retains the last working plugin version when an update to an existing plugin is invalid.
- OpenAI `openai/codex` plugin-creator reference at commit `6478a751fde8884b2fdc76486fe23175a8e795d4`: native Plugin root uses `.codex-plugin/plugin.json`; repo/team marketplace uses `.agents/plugins/marketplace.json`; a Plugin may expose `skills` without `apps` or `mcpServers`; the reference validator requires strict SemVer and the required interface metadata.

This document freezes the final P34 product Gate. It does not itself constitute Gate evidence.

## 1. Gate Objective

Prove that Aegis can be distributed as one real GitHub-backed Plugin whose normal installation materializes the exact nine-Skill Aegis catalog, preserves existing routing/ownership semantics, upgrades as one coherent catalog, and fails closed under invalid/broken upgrades.

The Gate is intentionally hybrid:

```text
Deterministic repository oracle
        +
real ChatGPT Plugin platform evidence
        +
protected behavioral evidence
        +
upgrade transition evidence
        ->
Plugin Distribution P34 verdict
```

Synthetic repository evidence alone cannot prove a real ChatGPT Plugin installation. UI observation alone is too weak to prove deterministic source/release identity. Both are required.

## 2. Non-Regression Invariants

The following invariants are normative for all PD-P34 cases:

1. The Aegis semantic catalog remains exactly the nine Skills defined by Skill Decomposition v0.2.
2. The Plugin is a distribution envelope, never a tenth lifecycle Primary Owner.
3. `Catalog State != Distribution Provenance` remains unchanged.
4. `terminal_trace_v0.2`, protected routing cases, Router/support/compatibility semantics, and Project State history remain unchanged.
5. A broken or partial Plugin never degrades into Standalone/Composite compatibility.
6. Plugin v0.1 requires zero Apps and zero MCP servers.
7. **Adding Plugin distribution MUST NOT remove, weaken, or replace the exact-nine Skill Installation Kit distribution.**
8. Plugin and Installation Kit are parallel adapters around one coherent Aegis release/component set.
9. Every future Aegis release that publishes a Plugin must remain capable of publishing the portable exact-nine Installation Kit from the same canonical Skill sources.
10. Canonical Skill source remains `skills/<skill-id>/`; Plugin Skill trees are deterministic materializations and must not become a second hand-maintained Authority.
11. **A published Aegis release identity is historical and must not be retrospectively reused by a Plugin source created after that release's pinned source revision.**

Target product model:

```text
                    Aegis Release
                         |
          +--------------+--------------+
          |                             |
          v                             v
     Aegis Plugin              9-Skill Installation Kit
   preferred install            portable/manual install
          |                             |
          +--------------+--------------+
                         |
                 same exact nine
                 same release identity
                 same Skill contents
```

Standalone central `aegis` remains a separate compatibility distribution.

## 3. P34 Preflight State

At freeze time the overall Plugin Distribution Gate is `BLOCKED_IMPLEMENTATION` because a supported GitHub Marketplace / native Plugin source has not yet been materialized in the repository.

State transitions:

- before PD-P34-01 implementation: `BLOCKED_IMPLEMENTATION`;
- after deterministic Plugin source exists but real platform install/upgrade events are still absent: `BLOCKED_EVIDENCE` for the missing platform evidence, unless another implementation defect is active;
- if the required ChatGPT workspace import/install/sync capability is unavailable to the tester: `BLOCKED_ENVIRONMENT`;
- only PD-P34-01 through PD-P34-05 all PASS can yield Gate PASS.

## 4. PD-P34-01 — GitHub Marketplace / Plugin Materialization

### Requirement

A reviewer-accessible GitHub revision contains one OpenAI-supported marketplace source and one native Aegis Plugin source that materializes the exact nine canonical Skills.

### Required repository shape

```text
.agents/
└── plugins/
    └── marketplace.json

plugins/
└── aegis/
    ├── .codex-plugin/
    │   └── plugin.json
    └── skills/
        ├── aegis/
        ├── aegis-project-state/
        ├── aegis-discovery/
        ├── aegis-modeling/
        ├── aegis-architecture/
        ├── aegis-verification/
        ├── aegis-governance/
        ├── aegis-implementation/
        └── aegis-gate-review/
```

### Marketplace contract

`.agents/plugins/marketplace.json` must:

- be valid JSON;
- contain one Aegis Plugin entry for this repository scope;
- use `name = aegis` for the Plugin entry;
- resolve to `./plugins/aegis` using the native local-source form;
- carry `policy.installation = AVAILABLE` and `policy.authentication = ON_INSTALL` for native marketplace compatibility;
- carry a display category;
- not use marketplace policy as evidence of ChatGPT workspace installation policy, because workspace import/configuration owns that policy independently.

### Plugin manifest contract

`plugins/aegis/.codex-plugin/plugin.json` must:

- use `name = aegis`;
- use strict SemVer matching the Aegis candidate/release identity under test;
- include non-empty `description` and `author.name`;
- set `skills` to `./skills/`;
- include the native required interface metadata;
- omit `apps` because Plugin v0.1 requires zero Apps;
- omit `mcpServers` because Plugin v0.1 requires zero MCP servers;
- omit unsupported manifest fields;
- contain no placeholders.

### Exact-nine materialization contract

The Plugin Skill inventory must equal the canonical Plugin Skill list in `skillset/distribution.json` exactly once and in full.

For every Skill `S`:

```text
tree_sha256(plugins/aegis/skills/S)
==
tree_sha256(skills/S)
```

The Plugin materialization must be generated/checkable from canonical sources. Direct hand-editing of the Plugin copies is non-authoritative and CI must detect drift.

### Release binding

The Plugin manifest version and materialized Skill contents must resolve to one coherent committed Aegis candidate/release manifest.

The already-published `v0.1.0-beta.1` release is historical and remains pinned to source revision `6a20969d66d1d594e7c37f970f43142e5a061e2e`; it MUST NOT be reused for the later native Plugin source.

PD-P34-01 therefore binds to the next unpublished candidate identity:

```text
candidate_release_version = 0.1.0-beta.2
candidate_release_manifest = skillset/releases/aegis-0.1.0-beta.2.json
Plugin manifest version = 0.1.0-beta.2
```

The candidate manifest is evidence/configuration for the Plugin Gate and is not itself a published GitHub Release. Publication remains downstream of the applicable P34/P24 decision.

Because Plugin and Installation Kit are parallel adapters, the same `0.1.0-beta.2` candidate must also remain buildable as an exact-nine Installation Kit from the same canonical Skill sources.

This release-binding repair is recorded as `F13-PD01-01` in `docs/superpowers/findings/2026-08-29-pd-p34-01-release-identity-finding.md`.

### PD-P34-01 PASS threshold

PASS requires all of the following:

1. native marketplace manifest exists at the supported path;
2. native Plugin manifest exists at the supported path;
3. both manifests satisfy the frozen OpenAI-compatible structural contract;
4. Plugin declares zero Apps and zero MCP servers;
5. Plugin inventory is exact nine;
6. all nine Plugin Skill trees are byte/content-identical to canonical Skill trees under the deterministic tree oracle;
7. materialization is reproducible/checkable by repository tooling;
8. CI fails when the materialization is absent or drifts and passes after materialization is corrected;
9. Plugin and a buildable exact-nine Installation Kit are bound to the same unpublished candidate release identity;
10. the exact result is committed to a reviewer-accessible GitHub revision.

PD-P34-01 proves **source materialization only**. It does not prove that a human installed the Plugin in ChatGPT; that is PD-P34-02.

## 5. PD-P34-02 — One Plugin Install -> Exact Nine

On a clean ChatGPT workspace state with no installed Aegis Plugin distribution:

```text
one Aegis Plugin installation
        ->
observed Aegis-family catalog == exact nine
        ->
provenance = PLUGIN
        ->
catalog_state = FULL_SPECIALIST
        ->
one coherent release/component set
```

Required evidence includes one real platform event, complete catalog capture, Plugin identity/provenance, release binding, and reviewer-accessible materialization evidence.

No duplicate Aegis distribution may be present.

## 6. PD-P34-03 — Plugin Behavioral Parity

Under fresh real `PLUGIN + FULL_SPECIALIST` provenance, rerun the four protected Skill Composition cases unchanged:

- `09-01-direct-specialist`
- `09-01-ambiguous-router`
- `09-01-upstream-blocker-reroute`
- `09-01-composite-fallback` only in its intended composite environment; it must not be manufactured by breaking the Plugin.

For Plugin multi-Skill behavior, the protected FULL_SPECIALIST cases must preserve `terminal_trace_v0.2`, Primary Owner, Router/support boundaries, and blocked terminality.

Plugin packaging is forbidden from changing routing semantics.

## 7. PD-P34-04 — Whole-Catalog Valid Upgrade

Using the same Plugin identity:

```text
COHERENT_RELEASE_A
        -> Sync/Refresh
COHERENT_RELEASE_B
        -> PASS
```

Required:

- same Plugin ID before/after;
- exact-nine coherent catalog before and after;
- no duplicate distribution;
- no accepted mixed-revision runtime state;
- post-sync component set matches Release B manifest;
- workspace installation/access policy remains preserved where observable.

Unchanged Skill digests between releases are permitted. Coherence is evaluated at the release/component-set boundary.

## 8. PD-P34-05 — Invalid Upgrade Fail-Closed

Create an intentionally invalid update fixture, for example a missing Skill or mismatched component revision.

Preferred supported-platform behavior:

```text
COHERENT_A
  -> invalid Sync
SYNC_ERROR
  -> last working COHERENT_A retained
  -> runtime safety preserved
```

If the platform ever exposes a transient broken catalog instead:

```text
COHERENT_A
  -> PARTIAL_CATALOG or MIXED_REVISION
  -> BLOCKED_ENVIRONMENT
  -> no runtime acceptance
  -> no compatibility fallback
```

Forbidden transition:

```text
PLUGIN
  -> broken/partial update
  -> aegis-only or partial catalog
  -> COMPOSITE_ONLY compatibility
  -> PASS
```

Any such fallback is a serious `BLOCKED_IMPLEMENTATION` defect.

## 9. Evidence Schema Extension

Plugin P34 platform evidence must be capable of recording:

```yaml
plugin_id: <platform-plugin-id>
plugin_name: aegis
distribution_provenance: PLUGIN
marketplace_source: <github-marketplace-source>
source_ref: <branch-tag-or-commit>
source_commit: <exact-source-commit>
release_version: <aegis-release>
release_manifest_ref: <durable-manifest-ref>
before_snapshot: <catalog-snapshot-or-null>
after_snapshot: <catalog-snapshot>
sync_result: <not-run|success|error>
same_plugin_id: <true|false|not-applicable>
catalog_state: <FULL_SPECIALIST|COMPOSITE_ONLY|PARTIAL_CATALOG|MIXED_REVISION>
installed_skill_ids: [<ids>]
accepted_runtime: <true|false>
materialization_ref: <reviewer-accessible-evidence>
```

Screenshots may support the record but do not replace machine-readable evidence tied to immutable source/release identity.

## 10. Final Gate Threshold

No shortcut is permitted.

```text
PD-P34-01 PASS
AND PD-P34-02 PASS
AND PD-P34-03 PASS
AND PD-P34-04 PASS
AND PD-P34-05 PASS
        ->
gate-plugin-distribution-v01-pr13 PASS
```

Missing one core case is a blocker, not `PASS_WITH_FINDINGS`.

## 11. Failure Classification

- unsupported/unavailable marketplace import or workspace permission -> `BLOCKED_ENVIRONMENT`;
- missing real install/upgrade/materialization evidence -> `BLOCKED_EVIDENCE` / `EVIDENCE_GAP`;
- invalid native manifest, wrong catalog, drifted generated Plugin tree, or valid upgrade producing incoherence -> `BLOCKED_IMPLEMENTATION` / `IMPLEMENTATION_DEFECT`;
- release-binding rule that reuses an already-published historical identity -> `SPEC_DEFECT` at P20/P34 Verification Design;
- broken Plugin becoming compatibility -> `BLOCKED_IMPLEMENTATION` / serious safety defect;
- packaging changing protected ownership/routing -> `BLOCKED_IMPLEMENTATION`;
- Project State historical integration facts -> out of scope and must not be rewritten.

## 12. Current Execution Boundary

The authorized implementation slice remains:

```text
PD-P34-01 RED
-> native marketplace / Plugin materialization
-> deterministic materialization oracle
-> release-identity repair / reverification when required
-> GREEN
-> exact GitHub materialized_ref
```

PD-P34-02 through PD-P34-05 remain unexecuted until PD-P34-01 is independently reviewable.
