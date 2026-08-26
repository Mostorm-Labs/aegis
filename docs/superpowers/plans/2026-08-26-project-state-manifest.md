# Aegis Project State Manifest + Authority Dependency Graph v0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build deterministic `.aegis/` project-state manifests, validation, supersession invalidation, generated state recomputation, CI evidence, and Aegis Skill bootstrap integration.

**Architecture:** Four authored JSON manifests (`project`, `authorities`, `gates`, `evidence`) feed a stdlib Python validator and state calculator. A fifth `state.json` is generated, reproducible, and checked for drift. Authority and Gate historical truth remain separate from computed validity.

**Tech Stack:** Python stdlib, JSON, JSON Schema documents, unittest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-08-26-project-state-manifest-design.md`

## Global Constraints

- Do not add a YAML dependency.
- Do not change P00-P36 IDs or existing Gate verdict vocabulary.
- Do not make `.aegis/state.json` authoritative.
- Do not mutate authored manifests during recomputation.
- Fail closed on dangling references, graph cycles, or invalid current PASS gates.
- Keep output deterministic for identical authored manifests.

## Task 1 — Manifest schemas and structural loader

Create five schemas under `schemas/project-state/v0.1/`, plus `tools/aegis_state/model.py`. Test missing/duplicate IDs, duplicate Current `(scope, kind)`, dangling refs and basic manifest structure before implementation.

## Task 2 — Graph and Gate invariants

Extend validation with dependency-cycle and supersession-cycle detection; require evidence for PASS/PASS_WITH_FINDINGS and reject declared-current PASS gates that rely on non-current authority or unavailable evidence.

## Task 3 — Supersession impact and derived state

Create `tools/aegis_state/compute.py`. Implement default `change_class` mapping, recursive dependency validity, transitive propagation, stale dominance, earliest-untrusted mapping and deterministic manifest digest.

## Task 4 — Explicit impact review

Support evidence-gated `impact_reviews[]`. An `unaffected` outcome suppresses invalidation only when every cited evidence item is `available`; otherwise fall back to the default supersession impact.

## Task 5 — CLI and state drift

Create `tools/aegis_state/cli.py` with `validate`, `recompute [--write]`, and `check`. `state.json` must be byte-stable for identical authored manifests. `check` exits non-zero when committed state differs from fresh recomputation.

## Task 6 — Minimal example and CI

Add `examples/project-state/minimal/.aegis/` and `.github/workflows/project-state.yml`. CI must run strict validate, state check, and the complete project-state unittest suite.

## Task 7 — Aegis Skill integration

Modify `skills/aegis/SKILL.md` with a thin `.aegis/` bootstrap rule and add `skills/aegis/references/project-state.md`. Update repository architecture/roadmap. Repackage the complete Skill via Skill Creator and validate `skill.zip`.

## Task 8 — P34 repository Gate

Push only tested files to `aegis/project-state-manifest-v0.1`, open a PR against `main`, inspect fresh workflow logs, and make a P34 verdict against the approved 07 authority. Keep the PR unmerged pending the integration decision.

## Required verification commands

```bash
python3 -m tools.aegis_state.cli recompute examples/project-state/minimal --write
python3 -m tools.aegis_state.cli validate examples/project-state/minimal
python3 -m tools.aegis_state.cli check examples/project-state/minimal
python3 -m unittest discover -s tests/project_state -v
```

The implementation is not complete until all commands pass on the exact tree proposed for integration and the updated Aegis Skill passes Skill Creator validation/package verification.
