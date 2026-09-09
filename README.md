# Aegis

**Aegis** is an AI-native, evidence-gated software development control plane.

It helps humans and AI agents decide **where work should begin**, **which source is authoritative**, **what contract must hold**, **what evidence proves completion**, and **whether a Gate may pass** before downstream work proceeds.

> Problem -> Authority -> Contract -> Evidence -> Plan -> Code -> Gate -> Release -> Feedback

## Why Aegis

AI makes implementation throughput cheap. The harder problems move upward and downward: choosing the right problem, keeping semantics and architecture coherent, preventing authority drift, and proving that implementation really satisfies the current contract.

Aegis turns those concerns into a reusable workflow rather than relying on individual engineering memory.

## What is included

Aegis v0.2 is delivered as one native **Aegis Plugin** that materializes the exact nine canonical Skills:

1. `aegis`
2. `aegis-project-state`
3. `aegis-discovery`
4. `aegis-modeling`
5. `aegis-architecture`
6. `aegis-verification`
7. `aegis-governance`
8. `aegis-implementation`
9. `aegis-gate-review`

The Release path also provides a portable **9-Skill Installation Kit** containing nine directly uploadable Skill ZIPs for environments where Plugin marketplace distribution is unavailable.

The control plane routes into 25 core stages:

- Discovery: P00-P03
- Design: P10-P18
- Verification & Governance: P20-P24
- Implementation: P30-P36

`P-BOOT` is represented by Aegis bootstrap routing rather than counted as a core stage.

## Core behavior

Aegis finds the **Earliest Untrusted Layer** instead of blindly starting from code. It distinguishes Current Authority from drafts, historical material, implementation reality, and evidence. It blocks downstream implementation when upstream authority is contradictory or incomplete.

`Code Complete != Gate Complete`

`Missing Evidence != Automatically Gate Blocked`

A blocking Evidence Artifact must close a material high-impact failure mode that is not already credibly covered by another independent mechanism. Redundant evidence remains useful for confidence, diagnostics, auditability, or observability, but does not block lifecycle progression solely for duplicate proof.

### Gate Closure Stability in beta.4

Once P31 authorizes implementation, the **blocking completion target is frozen**. P31 now carries an explicit `EXECUTION_CLOSURE_CONTRACT`; P32 executes that frozen contract through terminal success or a real terminal blocker rather than returning at ordinary intermediate checkpoints.

P34 audits frozen requirements and frozen evidence. It may still block a genuinely newly discovered high-impact correctness, safety, security, compatibility, data-integrity, or release-critical failure mode that the frozen contract did not reasonably cover, but it must not continuously redesign the Gate merely to gain more confidence.

P33 remains **Resume Interrupted Work**. Package omissions route to P31 and Verification Design omissions route to P20 instead of becoming an indefinite P33 patch loop.

Aegis also applies an **Anti-Proof-Recursion Rule**: evidence about an evidence mechanism becomes blocking only when that mechanism is itself a material undetected-failure source, lacks independent validation, and could materially change the Gate decision.

### Risk-proportionate profiles

- **Lite**: small/local, low-blast-radius, reversible work with strong existing tests.
- **Standard**: the default for most ordinary feature, bugfix, and module work. Exact PR/result identity, required tests, hosted CI, and reviewer-accessible evidence are normally sufficient when they close the frozen failure modes.
- **Full**: requires explicit risk justification, such as protocol/schema, security, data-integrity, cross-language conformance, formal SDK, irreversible migration, or regulated/high-assurance work. It may retain clean-checkout, materialized-evidence, provenance, and stronger independent-oracle requirements.

Aegis v0.2 also formalizes repository-backed execution safety: repository identity is resolved before package, task-anchor, or execution-cursor reasoning. A revision is not a repository locator, and unresolved or mismatched repository identity fails closed.

## Evaluation & dogfooding

Aegis is evaluated as a lifecycle decision system, not as a prose generator. The protected seed corpus is extended with permanent dogfood/incident regressions as real failures are discovered. Beta.4 adds seven Gate-closure-stability scenarios covering stable closure, redundant evidence, real late defects, incomplete P31 packages, repeated P33 package patching, Standard evidence proportionality, and Full-profile strictness.

Validate corpus integrity locally with:

```bash
python3 evals/scripts/validate_corpus.py
```

See [`docs/evaluation-and-dogfooding-v0.1.md`](docs/evaluation-and-dogfooding-v0.1.md) and [`evals/README.md`](evals/README.md).

## Aegis + Superpowers

Aegis is designed to compose with Superpowers rather than duplicate it.

- Aegis: project state, problem/product/semantic/architecture authority, verification design, drift, supersession, Gate and release governance.
- Superpowers: coding-agent execution mechanics such as brainstorming, plans, TDD, systematic debugging, code review, and verification-before-completion.

See [`skills/aegis/references/superpowers-integration.md`](skills/aegis/references/superpowers-integration.md).

## Install Aegis

### Recommended: GitHub Plugin

In ChatGPT Workspace settings, import the Plugin marketplace from:

```text
https://github.com/Mostorm-Labs/aegis
```

Use the repository root marketplace manifest (`.agents/plugins/marketplace.json`). Installing **Aegis** should materialize one Plugin with the exact nine canonical Skills.

### Alternative: 9-Skill Installation Kit

Current published prerelease:

```text
v0.2.0-beta.4
```

The published Release asset is:

```text
https://github.com/Mostorm-Labs/aegis/releases/download/v0.2.0-beta.4/aegis-skill-installation-kit-v0.2.0-beta.4.zip
```

Extract the outer archive once, then upload the nine nested Skill ZIPs without unpacking them.

See [`docs/installation-and-usage-v0.2.md`](docs/installation-and-usage-v0.2.md) for installation, verification, usage, update, repository-backed execution, rollback, and troubleshooting guidance.

Immutable `v0.2.0-beta.3`, `v0.2.0-beta.2`, `v0.2.0-beta.1`, and `v0.1.0-beta.3` remain historical rollback/reproducibility boundaries.

## Status

**v0.2 — Control Plane prerelease `v0.2.0-beta.4`, delivered as one Plugin + exact nine Skills with stable post-P31 closure, risk-proportionate evidence, and late-finding Gate discipline.**

This prerelease does not claim `SERVICE_PROFILE`, R0/S0/W7D service-scale qualification, rollout expansion, or zero-user-turn cross-Primary substantive chaining.

## Documentation

- [`docs/installation-and-usage-v0.2.md`](docs/installation-and-usage-v0.2.md)
- [`docs/releases/v0.2.0-beta.4.md`](docs/releases/v0.2.0-beta.4.md)
- [`docs/releases/v0.2.0-beta.3.md`](docs/releases/v0.2.0-beta.3.md)
- [`docs/releases/v0.2.0-beta.2.md`](docs/releases/v0.2.0-beta.2.md)
- [`docs/installation-and-usage-v0.1.md`](docs/installation-and-usage-v0.1.md)
- [`docs/plugin-distribution-contract-v0.1.md`](docs/plugin-distribution-contract-v0.1.md)
- [`docs/methodology.md`](docs/methodology.md)
- [`docs/architecture.md`](docs/architecture.md)
- [`docs/evaluation-and-dogfooding-v0.1.md`](docs/evaluation-and-dogfooding-v0.1.md)
- [`docs/roadmap.md`](docs/roadmap.md)

## License

No open-source license has been selected yet. Until one is added, normal copyright restrictions apply.
