# Aegis Installation & Usage Guide v0.2

Aegis v0.2 is an evidence-driven software development Control Plane delivered primarily as one native **Aegis Plugin** exposing the exact nine canonical Skills. A portable **9-Skill Installation Kit** remains the fallback path.

Current candidate identity: `v0.2.0-beta.2`.

This guide describes the candidate distribution and use model. Publication is not complete until final P24 release readiness and the release workflow succeed.

## Choose an installation path

| Situation | Recommended path |
| --- | --- |
| ChatGPT workspace with Plugin marketplace access | GitHub Plugin |
| Team/developer environment that should update as one product | GitHub Plugin |
| No Plugin marketplace access | 9-Skill Installation Kit |
| Reproducible/offline archive | immutable Release kit after publication |

For normal product use, prefer the Plugin. The Plugin owns distribution/install coherence; it is not an additional lifecycle owner.

## Recommended: GitHub Plugin

Import the marketplace from the repository root:

```text
https://github.com/Mostorm-Labs/aegis
```

Use the repository-root `.agents/plugins/marketplace.json`. Do not append `/tree/...`, a branch name, or a manifest filename to the source URL.

After `v0.2.0-beta.2` is published, reproducible installations may pin the immutable tag:

```text
v0.2.0-beta.2
```

Until publication, do not treat that tag as existing.

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

The intended prerelease asset is:

```text
aegis-skill-installation-kit-v0.2.0-beta.2.zip
```

After publication, verify the outer archive against the Release-provided `SHA256SUMS` or `aegis-release-v0.2.0-beta.2.json`, extract the outer archive once, and upload the nine nested Skill ZIPs without unpacking them.

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

The distribution model remains Plugin + exact nine Skills, while the product semantics now include the formal Control Plane behavior accepted for v0.2:

- Current Authority and durable Project State as explicit control inputs;
- evidence-bound implementation packages;
- `Task Anchor != Execution Cursor` and controlled interrupted-work resume;
- independent Gate ownership;
- durable result materialization before review;
- explicit provider-qualified repository identity for repository-backed execution;
- repository preflight before package, task-anchor, or cursor reasoning;
- fail-closed handling for unavailable, ambiguous, or mismatched repository identity.

A bare revision is not a repository locator.

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

The previous immutable published release remains:

```text
v0.1.0-beta.3
```

Its published Installation Kit SHA-256 is part of historical release evidence. The v0.2 candidate does not rewrite beta.3 manifests, notes, tag, Release, or published assets.

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
- **Need a reproducible historical environment:** use immutable `v0.1.0-beta.3` or the published beta.1 history until beta.2 is actually published.

## References

- distribution semantics: [`plugin-distribution-contract-v0.1.md`](plugin-distribution-contract-v0.1.md)
- prior v0.1 guide: [`installation-and-usage-v0.1.md`](installation-and-usage-v0.1.md)
- candidate release notes: [`releases/v0.2.0-beta.2.md`](releases/v0.2.0-beta.2.md)
