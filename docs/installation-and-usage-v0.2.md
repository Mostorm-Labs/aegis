# Aegis Installation & Usage Guide v0.2

Aegis v0.2 is an evidence-driven software development Control Plane delivered primarily as one native **Aegis Plugin** exposing the exact nine canonical Skills. A portable **9-Skill Installation Kit** remains the fallback path.

Current published prerelease identity: `v0.2.0-beta.3`.

This guide describes the beta.3 distribution and use model.

## Choose an installation path

| Situation | Recommended path |
| --- | --- |
| ChatGPT workspace with Plugin marketplace access | GitHub Plugin |
| Team/developer environment that should update as one product | GitHub Plugin |
| No Plugin marketplace access | 9-Skill Installation Kit |
| Reproducible/offline archive | immutable published Release kit |

For normal product use, prefer the Plugin. The Plugin owns distribution/install coherence; it is not an additional lifecycle owner.

## Recommended: GitHub Plugin

Import the marketplace from the repository root:

```text
https://github.com/Mostorm-Labs/aegis
```

Use the repository-root `.agents/plugins/marketplace.json`. Do not append `/tree/...`, a branch name, or a manifest filename to the source URL.

For a reproducible beta.3 installation, pin the immutable published tag:

```text
v0.2.0-beta.3
```

## Verify the exact-nine catalog

A normal installation must expose exactly:

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

Acceptance rule:

```text
one Aegis Plugin + exact nine Skills = normal FULL_SPECIALIST installation
partial or mixed Aegis catalog       = incomplete / fail closed
```

UI ordering is not significant; catalog identity is set-based and coherent as one product.

## Alternative: 9-Skill Installation Kit

The published prerelease asset is:

```text
aegis-skill-installation-kit-v0.2.0-beta.3.zip
```

Verify the outer archive against the Release-provided `SHA256SUMS` or `aegis-release-v0.2.0-beta.3.json`, extract the outer archive once, and upload the nine nested Skill ZIPs without unpacking them.

Expected nested archives:

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

## What v0.2 adds

The distribution model remains Plugin + exact nine Skills, while the product semantics include the formal Control Plane behavior accepted for v0.2:

- Current Authority and durable Project State as explicit control inputs;
- evidence-bound implementation packages;
- failure-mode-first blocking evidence qualification;
- `Missing Evidence != Automatically Gate Blocked` while preserving `Code Complete != Gate Complete`;
- `Task Anchor != Execution Cursor` and controlled interrupted-work resume;
- independent Gate ownership;
- durable result materialization before review;
- explicit provider-qualified repository identity for repository-backed execution;
- repository preflight before package, task-anchor, or cursor reasoning;
- fail-closed handling for unavailable, ambiguous, or mismatched repository identity.

A bare revision is not a repository locator.

### Blocking evidence in beta.3

Aegis starts from the high-impact failure mode, checks existing credible independent detection coverage, and asks what residual proof gap remains. An Evidence Artifact is allowed to become a blocking Gate requirement only when its absence leaves such a failure mode without credible independent detection coverage.

Independence is assessed at the detection-mechanism and oracle level. Re-running the same test locally and in CI does not create independent coverage, and multiple tests sharing the same faulty oracle do not protect against that oracle failure. Redundant confidence, diagnostic, audit, and observability evidence remains useful but non-blocking.

## How to use Aegis

Users normally start with the task itself or a routing question such as:

```text
What should this project do next?
```

Aegis determines the earliest untrusted layer, Current Authority, evidence obligations, and owning stage. The central `aegis` Skill owns genuine routing ambiguity; specialist Skills retain substantive stage ownership.

Simplified flow:

```text
User task
   ↓
Aegis routing / project-state preflight
   ↓
Current Authority + earliest untrusted layer
   ↓
Owning specialist / stage
   ↓
Evidence-producing work
   ↓
Gate review
   ↓
continue | block | repair | integrate | release
```

Under current Authority, substantive work owned by different Primary Skills does **not** silently chain across Primary boundaries in one user turn. A completed stage may identify the next owner, but that does not itself authorize the next Primary's substantive stage.

## Repository-backed execution

Repository-backed P31/P32/P33/P36 handoffs carry an explicit repository identity, a same-repository package materialization ref, and a task anchor when a trusted repository ancestry baseline is required.

The execution order is fail-closed:

```text
repository identity
→ declared-repository checkout/worktree
→ package resolution in that repository
→ package materialization repository match
→ task-anchor ancestry
→ resume-cursor classification when applicable
→ authored mutation
```

If the declared repository cannot be established, Aegis must not substitute an ambient checkout or use a bare SHA to infer another repository.

## Updating

Aegis Plugin updates are whole-catalog transitions. After a GitHub-backed marketplace update or **Sync now**, verify the exact-nine catalog before relying on the new state.

Do not accept a partial or mixed Aegis catalog. For reproducibility, pin an immutable published tag or use its Release kit.

## Rollback boundary

The current prerelease is:

```text
v0.2.0-beta.3
```

Earlier immutable published boundaries remain available for rollback and historical reproduction:

```text
v0.2.0-beta.2
v0.2.0-beta.1
v0.1.0-beta.3
```

Their published manifests, notes, tags, Releases, and assets remain historical and unchanged.

## Deliberate product boundaries

Aegis v0.2 does not claim:

- a required standalone daemon or hosted Control Service;
- R0/S0/W7D service-scale qualification;
- `SERVICE_PROFILE` authorization;
- rollout expansion beyond the accepted Plugin profile;
- zero-user-turn cross-Primary substantive chaining.

## Troubleshooting

- **Fewer than nine Aegis Skills are visible:** treat the installation as incomplete.
- **Mixed old/new Aegis Skills are present:** restore one coherent catalog before use.
- **Installation Kit was unpacked too far:** upload the nine nested ZIP files, not their unpacked directories.
- **Repository-backed handoff resolves the wrong repository:** stop; repository identity must be resolved before package/anchor/cursor reasoning.
- **Declared repository is unavailable:** return `BLOCKED_REPOSITORY_IDENTITY`; do not substitute another checkout.
- **Need a reproducible historical environment:** use an immutable published tag and its Release assets, including `v0.2.0-beta.2`, `v0.2.0-beta.1`, or `v0.1.0-beta.3` when reproducing earlier behavior.

## References

- distribution semantics: [`plugin-distribution-contract-v0.1.md`](plugin-distribution-contract-v0.1.md)
- prior v0.1 guide: [`installation-and-usage-v0.1.md`](installation-and-usage-v0.1.md)
- beta.3 release notes: [`releases/v0.2.0-beta.3.md`](releases/v0.2.0-beta.3.md)
- previous beta.2 release notes: [`releases/v0.2.0-beta.2.md`](releases/v0.2.0-beta.2.md)
