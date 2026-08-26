# Project State v0.2 Authority Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close F08-01 and F08-02 by making blocked Gate verdicts affect derived project state and by adding a separate repository integration lifecycle.

**Architecture:** Preserve the v0.1 authority/evidence/gate model, add a v0.2 `integrations.json` authored manifest, and extend deterministic state computation with active Gate blockers and integration handoff. Keep v0.1 schemas immutable and put the new contract under `schemas/project-state/v0.2/`.

**Tech Stack:** Python 3.12 stdlib, JSON/JSON Schema documents, unittest, GitHub Actions, Aegis Skill references.

**Spec:** `docs/superpowers/specs/2026-08-26-project-state-v0.2-authority-repair-design.md`

## Global Constraints

- Do not add new Gate verdicts or P-stages.
- Keep Authority status, Gate verdict, Gate validity, and Integration status separate.
- `state.json` remains generated and deterministic.
- Aegis records/routes integration; it does not perform merge/rebase operations.
- Preserve `schemas/project-state/v0.1/` unchanged.
- Current blocked Gate routing is fixed by the v0.2 authority table.
- Do not repair 08 by special-casing OpenAI or PR numbers.

---

### Task 1: Freeze v0.2 schemas and loader contract

**Files:**
- Create: `schemas/project-state/v0.2/project.schema.json`
- Create: `schemas/project-state/v0.2/authorities.schema.json`
- Create: `schemas/project-state/v0.2/gates.schema.json`
- Create: `schemas/project-state/v0.2/evidence.schema.json`
- Create: `schemas/project-state/v0.2/integrations.schema.json`
- Create: `schemas/project-state/v0.2/state.schema.json`
- Modify: `tools/aegis_state/model.py`
- Test: `tests/project_state/test_v02_model.py`

**Interfaces:**
- Consumes: existing `ManifestSet`, Gate/Evidence registries.
- Produces: `ManifestSet.integrations`, `integration_items`, 0.2 schema/version validation.

- [ ] Write failing tests that a 0.2 project requires `integrations.json`, integration IDs are unique, dangling Gate/Evidence refs fail, and `integrated` requires `integrated_revision`.
- [ ] Run `python3 -m unittest tests.project_state.test_v02_model -v` and confirm RED because v0.2/integrations are unsupported.
- [ ] Add v0.2 schemas without editing any v0.1 schema file.
- [ ] Extend `ManifestSet` and loader/validator for `integrations.json` and the three allowed statuses.
- [ ] Add current-pass/current-valid/available-evidence invariants for awaiting/integrated integration records.
- [ ] Run the focused tests and confirm GREEN.

### Task 2: Implement blocked Gate verdict propagation

**Files:**
- Modify: `tools/aegis_state/compute.py`
- Test: `tests/project_state/test_gate_blockers_v02.py`

**Interfaces:**
- Consumes: effective Gate validity and canonical Gate verdict.
- Produces: `blocking_gates[]`, blocker findings, earliest layer, recommended stage.

- [ ] Write failing tests for all four `BLOCKED_*` mappings, `PASS_WITH_FINDINGS`, and stale blocked Gate behavior.
- [ ] Run the focused suite and confirm RED with the F08-01 false-clean behavior.
- [ ] Implement a constant Gate-verdict route map and only activate it for effective-current Gates.
- [ ] Merge Gate blocker candidates with existing authority/Gate-validity candidates using lifecycle precedence.
- [ ] Emit deterministic `blocking_gates` and stable findings.
- [ ] Run focused tests and confirm GREEN.

### Task 3: Implement integration-derived state and handoff

**Files:**
- Modify: `tools/aegis_state/compute.py`
- Test: `tests/project_state/test_integrations_v02.py`

**Interfaces:**
- Consumes: validated `integration_items`.
- Produces: `awaiting_integrations[]`, `recommended_handoff`, integration findings.

- [ ] Write failing tests that awaiting integration becomes an implementation-level open item, integrated disappears from awaiting, and a verification blocker outranks awaiting integration.
- [ ] Confirm RED.
- [ ] Add integration records to `manifest_digest`.
- [ ] Compute awaiting integration state deterministically.
- [ ] When integration is the primary open item, set `earliest_untrusted_layer="implementation"`, `recommended_next_stage=null`, and `recommended_handoff="superpowers:finishing-a-development-branch"`.
- [ ] Preserve integration findings as secondary findings when another earlier blocker wins.
- [ ] Confirm focused GREEN.

### Task 4: Migrate executable example, CI, and Skill reference

**Files:**
- Modify: `examples/project-state/minimal/.aegis/project.json`
- Modify: `examples/project-state/minimal/.aegis/authorities.json`
- Modify: `examples/project-state/minimal/.aegis/gates.json`
- Modify: `examples/project-state/minimal/.aegis/evidence.json`
- Create: `examples/project-state/minimal/.aegis/integrations.json`
- Regenerate: `examples/project-state/minimal/.aegis/state.json`
- Modify: `.github/workflows/project-state.yml`
- Modify: `skills/aegis/references/project-state.md`
- Test: existing and new `tests/project_state/*`

**Interfaces:**
- Consumes: v0.2 model/compute.
- Produces: end-to-end v0.2 fixture and updated Skill instructions.

- [ ] Migrate fixture schema_version to 0.2 and add a pass-gated awaiting integration record.
- [ ] Run `python3 -m tools.aegis_state.cli recompute examples/project-state/minimal --write`.
- [ ] Run `validate` and `check`; expect `VALID` and `STATE_OK`.
- [ ] Update CI paths/commands if necessary so the v0.2 example is exercised.
- [ ] Update `references/project-state.md` with Gate blocker mapping and integration lifecycle; keep `SKILL.md` thin.
- [ ] Run `python3 -m unittest discover -s tests/project_state -v` and require zero failures.

### Task 5: P34, supersession, and 08 rerun

**Files:**
- Update after evidence: `docs/project-state-manifest-v0.2.md`
- Update after evidence: Notion 07 v0.2 page
- Update after acceptance: Notion/GitHub v0.1 supersession markers
- Rerun target: PR #5 / `aegis/self-hosting-manifest-v0.1`

**Interfaces:**
- Consumes: final PR-context CI evidence.
- Produces: P34 verdict and accepted/superseded authority state.

- [ ] Open a stacked v0.2 PR against `aegis/project-state-manifest-v0.1`.
- [ ] Require PR-context CI to pass full project-state regressions and example validation/check.
- [ ] Run Skill Creator validation/package on the updated complete Aegis Skill.
- [ ] P34-review v0.2 against this authority; do not promote on unit-test claims alone.
- [ ] If P34 passes, mark v0.2 Current Replacement Authority and v0.1 Superseded with reason/link.
- [ ] Replay/retarget 08 self-hosting onto v0.2 and regenerate root state.
- [ ] Require the real baseline Gate to appear as `BLOCKED_ENVIRONMENT`, with `verification/P34`, and PR integration records to remain awaiting until repository reality says integrated.
- [ ] Only then reconsider PR #5 Overall 08 Gate.

## Self-review

- Spec coverage: Gate propagation, integration lifecycle, precedence, schema versioning, Skill integration, P34, and 08 rerun are all mapped to tasks.
- Placeholder scan: no TBD/TODO or undefined implementation steps.
- Type consistency: `blocking_gates`, `awaiting_integrations`, `recommended_handoff`, `integrations.json`, and `integrated_revision` use identical names across tasks/spec.
