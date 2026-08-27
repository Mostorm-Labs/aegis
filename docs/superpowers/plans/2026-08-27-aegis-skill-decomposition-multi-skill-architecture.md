# Aegis Skill Decomposition & Multi-Skill Architecture v0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the approved nine-entrypoint Hub-and-Spoke Aegis Skill System with one canonical `skillset/` source, deterministic committed standalone `skills/*` distributions, composite `aegis` compatibility, protected routing/handoff tests, and split deterministic/behavioral Gates.

**Architecture:** `skillset/manifest.json` owns Skill/build identity, `skillset/ownership.json` alone owns P-stage and cross-cutting ownership, `skillset/shared/` owns global contracts, and `skillset/skills/` owns canonical per-Skill source. `tools/aegis_skillset` + `scripts/build_skillset.py` render/check generated self-contained `skills/*`. Routing corpus is only an intended-routing oracle; real platform auto-selection remains a separate behavioral evidence Gate.

**Tech Stack:** Python 3 stdlib, JSON/Markdown, existing Skill Creator validation/package tooling, existing Aegis project-state/evaluation tooling, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-08-27-aegis-skill-decomposition-multi-skill-architecture-design.md`

## Global Constraints
- Nine entrypoints exactly: `aegis`, `aegis-project-state`, `aegis-discovery`, `aegis-modeling`, `aegis-architecture`, `aegis-verification`, `aegis-governance`, `aegis-implementation`, `aegis-gate-review`.
- `aegis` is the only ambiguity/cross-domain router and remains the complete single-Skill compatibility facade.
- `aegis-project-state` owns no P-stage; it is cross-cutting.
- Preserve P00-P36 semantics, statuses, defect taxonomy, Gate verdicts, Project State v0.3, and Superpowers boundary.
- `manifest.json` must not duplicate stage ownership from `ownership.json`.
- Generated `skills/*` is committed, standalone, deterministic, and runtime-independent of siblings.
- Specialists fail closed when `.aegis/` exists but deterministic project-state verification is unavailable, unless independent Current Authority proves execution safety.
- Routing corpus/package validation never counts as platform auto-trigger evidence.
- Existing OpenAI hosted baseline remains independently `BLOCKED_ENVIRONMENT`; no API key is required for deterministic 09 work.
- Existing 34-case lifecycle/evaluation corpus must not regress.

---

### Task 1: Machine-readable Skill identity and ownership
**Create:** `skillset/manifest.json`, `skillset/ownership.json`, `tools/aegis_skillset/{__init__,model,cli}.py`, `tests/skillset/{helpers,test_metadata}.py`.

- [ ] RED: assert every P-stage has exactly one owner; duplicate/missing ownership, unknown Skill, stage fields duplicated in manifest, or ambiguity router != `aegis` fail.
- [ ] GREEN: implement `SkillSpec`, `SkillSetConfig`, `load_skillset(root)`, `validate_skillset(config)`, CLI `validate` -> `SKILLSET_VALID`.
- [ ] Freeze ownership: P00-P03 discovery; P10-P13 modeling; P14-P18 architecture; P20 verification; P21-P24 governance; P30-P33 implementation; P34-P36 gate-review. Cross-cutting: project_state -> project-state; ambiguity_router -> aegis.
- [ ] Run `python3 -m unittest tests.skillset.test_metadata -v` and CLI validate.

### Task 2: Shared contracts + deterministic builder
**Create:** `skillset/shared/{core-invariants,stage-vocabulary,authority-contract,status-contract,handoff-contract}.md`, `tools/aegis_skillset/build.py`, `scripts/build_skillset.py`, `tests/skillset/test_build.py`.

- [ ] RED: two renders byte-identical; canonical shared bytes equal rendered shared refs; drift detection; no timestamps; no path escape.
- [ ] GREEN: deterministic `render_distribution`, `build_all`, `--write`, `--check`.
- [ ] Extract only existing global semantics; do not redesign lifecycle.

### Task 3: Composite `aegis` migration
**Create canonical:** `skillset/skills/aegis/**`; **regenerate:** `skills/aegis/**`; **test:** `tests/skillset/test_composite.py`.

- [ ] Capture current accepted composite semantics before migration.
- [ ] RED: generated source compatibility not yet true.
- [ ] Move source ownership to `skillset/skills/aegis`; generate composite from same shared/specialist source.
- [ ] GREEN: stage/core/status/Gate/defect/Project-State semantics preserved; 34-case corpus PASS; provider bundle still top-level `aegis/`.

### Task 4: Protected routing/handoff corpus
**Create:** `skillset/routing/{direct-trigger,ambiguous-routing,cross-skill-handoff,upstream-blocker,compatibility}.json`, `tools/aegis_skillset/routing.py`, `tests/skillset/test_routing.py`.

- [ ] RED: direct modeling/governance/verification/gate-review cases, ambiguous router case, earlier-blocker/unverifiable-project-state stop cases, happy handoff, forbidden cycle.
- [ ] GREEN: deterministic schema/ownership/handoff evaluator only; no LLM classifier. CLI `routing-check` -> `ROUTING_OK`.

### Task 5: Eight specialist distributions
Implement in order: `aegis-project-state`, `aegis-governance`, `aegis-gate-review`, `aegis-verification`, `aegis-architecture`, `aegis-modeling`, `aegis-discovery`, `aegis-implementation`.

For each:
- [ ] Add RED standalone/existence/ownership/preflight tests.
- [ ] Add canonical `SKILL.md`, `agents/openai.yaml`, stage-family refs as required.
- [ ] Regenerate distribution and run focused build/routing tests.
- [ ] Validate standalone Skill package before proceeding.

`aegis-implementation` must reference Superpowers mechanics rather than copy them.

### Task 6: Repository deterministic Gate
**Create:** `.github/workflows/skillset.yml`, `docs/skill-decomposition-v0.1.md`.

Required commands:
```bash
python3 -m tools.aegis_skillset.cli validate .
python3 scripts/build_skillset.py --check
python3 -m tools.aegis_skillset.cli routing-check .
python3 -m unittest discover -s tests/skillset -v
python3 -m unittest discover -s tests/project_state -v
python3 -m evals.cli corpus evals/corpus
```
Also validate/package all nine distributions without live provider calls. Record actual final counts, not guessed counts.

### Task 7: Manual dogfood + P34 split verdict
**Create:** `docs/skill-decomposition-dogfood-v0.1.md`; update Notion 09 after evidence.

Exercise direct specialist, ambiguous router, upstream-blocker specialist reroute, and composite fallback where platform installed-Skill behavior is observable. Every real failure becomes a permanent regression before instruction changes.

P34 reports separately:
```text
Deterministic Skill-System Tooling = PASS | BLOCKED_*
Multi-Skill Behavioral Trigger     = PASS | BLOCKED_EVIDENCE | BLOCKED_*
Existing Hosted Provider Baseline  = BLOCKED_ENVIRONMENT unless new real evidence exists
```
Package/routing-corpus success cannot be promoted into platform behavioral evidence.

## Plan Self-Review
- Spec coverage: complete across Tasks 1-7.
- Placeholder scan: none.
- Naming consistency: canonical namespaces remain `skillset/`, `skills/`, `tools/aegis_skillset/`, `tests/skillset/`; only `aegis` is ambiguity router.
