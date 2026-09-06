# Aegis

**Aegis** is an AI-native, evidence-gated software development control plane.

It helps humans and AI agents decide **where work should begin**, **which source is authoritative**, **what contract must hold**, **what evidence proves completion**, and **whether a gate may pass** before downstream work proceeds.

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

A result becomes a stable dependency only when its required evidence passes the relevant gate.

Aegis v0.2 also formalizes repository-backed execution safety: repository identity is resolved before package, task-anchor, or execution-cursor reasoning. A revision is not a repository locator, and unresolved or mismatched repository identity fails closed.

## Evaluation & dogfooding

Aegis is evaluated as a lifecycle decision system, not as a prose generator.

The Evaluation & Dogfooding Framework starts with a **protected 30-case seed corpus** covering routing, authority, defect, and gate behavior. The corpus is intentionally extensible: real failures are added permanently as `dogfood` or `incident` regressions rather than replacing seed cases.

The first dogfood regression (`defect-007`) was created by Aegis evaluating its own evaluation framework: the original validator incorrectly treated 30 as a corpus ceiling. CI now protects the 30 seed IDs while allowing regression growth.

Validate corpus integrity locally with:

```bash
python3 evals/scripts/validate_corpus.py
```

See [`docs/evaluation-and-dogfooding-v0.1.md`](docs/evaluation-and-dogfooding-v0.1.md) and [`evals/README.md`](evals/README.md).

## Aegis + Superpowers

Aegis is designed to compose with Superpowers rather than duplicate it.

- Aegis: project state, problem/product/semantic/architecture authority, verification design, drift, supersession, gate and release governance.
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

Current release-candidate identity:

```text
v0.2.0-beta.2
```

After publication, the intended Release asset is:

```text
https://github.com/Mostorm-Labs/aegis/releases/download/v0.2.0-beta.2/aegis-skill-installation-kit-v0.2.0-beta.2.zip
```

Extract the outer archive once, then upload the nine nested Skill ZIPs without unpacking them.

See [`docs/installation-and-usage-v0.2.md`](docs/installation-and-usage-v0.2.md) for installation, verification, usage, update, repository-backed execution, rollback, and troubleshooting guidance.

Until `v0.2.0-beta.2` is actually published, immutable `v0.2.0-beta.1` and `v0.1.0-beta.3` remain historical rollback/reproducibility boundaries.

## Status

**v0.2 — Control Plane candidate `v0.2.0-beta.2`, delivered as one Plugin + exact nine Skills, pending final P24 release-readiness review and publication.**

This candidate does not claim `SERVICE_PROFILE`, R0/S0/W7D service-scale qualification, rollout expansion, or zero-user-turn cross-Primary substantive chaining.

## Documentation

- [`docs/installation-and-usage-v0.2.md`](docs/installation-and-usage-v0.2.md)
- [`docs/releases/v0.2.0-beta.2.md`](docs/releases/v0.2.0-beta.2.md)
- [`docs/installation-and-usage-v0.1.md`](docs/installation-and-usage-v0.1.md)
- [`docs/plugin-distribution-contract-v0.1.md`](docs/plugin-distribution-contract-v0.1.md)
- [`docs/methodology.md`](docs/methodology.md)
- [`docs/architecture.md`](docs/architecture.md)
- [`docs/evaluation-and-dogfooding-v0.1.md`](docs/evaluation-and-dogfooding-v0.1.md)
- [`docs/roadmap.md`](docs/roadmap.md)

## License

No open-source license has been selected yet. Until one is added, normal copyright restrictions apply.
