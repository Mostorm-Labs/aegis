# Aegis

**Aegis** is an AI-native, evidence-gated software development control plane.

It helps humans and AI agents decide **where work should begin**, **which source is authoritative**, **what contract must hold**, **what evidence proves completion**, and **whether a gate may pass** before downstream work proceeds.

> Problem -> Authority -> Contract -> Evidence -> Plan -> Code -> Gate -> Release -> Feedback

## Why Aegis

AI makes implementation throughput cheap. The harder problems move upward and downward: choosing the right problem, keeping semantics and architecture coherent, preventing authority drift, and proving that implementation really satisfies the current contract.

Aegis turns those concerns into a reusable workflow rather than relying on individual engineering memory.

## What is included

Aegis v0.1 is packaged as one installable Skill with progressive references:

```text
skills/aegis/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/
    ├── bootstrap-routing.md
    ├── stage-contracts.md
    ├── discovery-design.md
    ├── verification-governance.md
    ├── implementation.md
    ├── output-contracts.md
    └── superpowers-integration.md
```

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

## Aegis + Superpowers

Aegis is designed to compose with Superpowers rather than duplicate it.

- Aegis: project state, problem/product/semantic/architecture authority, verification design, drift, supersession, gate and release governance.
- Superpowers: coding-agent execution mechanics such as brainstorming, plans, TDD, systematic debugging, code review, and verification-before-completion.

See [`skills/aegis/references/superpowers-integration.md`](skills/aegis/references/superpowers-integration.md).

## Install / package

The distributable Skill is built from `skills/aegis` with the standard Skill Creator packager:

```bash
python3 /path/to/skill-creator/scripts/package_skill.py skills/aegis dist
```

The resulting archive should be named `skill.zip`.

## Status

**v0.1 — Initial usable Skill.** The current goal is to validate routing and stage behavior on real projects before splitting Aegis into a multi-Skill suite.

## Documentation

- [`docs/methodology.md`](docs/methodology.md)
- [`docs/architecture.md`](docs/architecture.md)
- [`docs/roadmap.md`](docs/roadmap.md)

## License

No open-source license has been selected yet. Until one is added, normal copyright restrictions apply.
