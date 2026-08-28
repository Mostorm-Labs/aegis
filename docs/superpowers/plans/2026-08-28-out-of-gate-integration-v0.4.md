# Out-of-Gate Integration v0.4 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow Project State v0.4 to truthfully record a repository integration that occurred under a blocked Gate while preserving the Gate blocker and deriving the integration as nonconforming.

**Architecture:** Keep repository occurrence, Gate conformance, applicability, and actionability orthogonal. v0.4 adds a schema/generator version and derived conformance projections; v0.3 remains supported under its original stricter semantics.

**Tech Stack:** Python 3.12, JSON Schema draft 2020-12, unittest, GitHub Actions.

**Spec:** `docs/project-state-manifest-v0.4.md`

## Global Constraints

- Never change a BLOCKED Gate to PASS merely because repository integration occurred.
- `awaiting_integration` continues to require a current-effective PASS/PASS_WITH_FINDINGS Gate.
- v0.3 projects retain v0.3 validation semantics.
- Only proven `integrated` occurrences receive Gate-conformance projections.
- Root PR #9 merge evidence is occurrence evidence, not Gate acceptance evidence.

---

### Task 1: RED-first v0.4 semantic oracle

**Files:**
- Create: `tests/project_state/test_out_of_gate_v04.py`

**Interfaces:**
- Consumes: `load_manifests`, `validate_manifests`, `compute_state`.
- Produces: executable acceptance oracle for v0.4 and backward-compatibility oracle for v0.3.

- [ ] Write a v0.4 fixture with a Current/Proposed Authority, `BLOCKED_EVIDENCE` Gate, available occurrence evidence, and `integrated` revision.
- [ ] Assert strict validation accepts it.
- [ ] Assert generated `integration_conformance` marks it `nonconforming` and `nonconforming_integrations` contains the ID.
- [ ] Assert the Gate remains in `blocking_gates` and route remains `verification / P34`.
- [ ] Add PASS-backed conforming case.
- [ ] Add v0.3 regression proving blocked-backed integration is still rejected.
- [ ] Run the focused test and observe RED for missing v0.4 support/conformance fields.

### Task 2: Version-aware Project State model

**Files:**
- Modify: `tools/aegis_state/model.py`
- Modify: `tools/aegis_state/__init__.py`

**Interfaces:**
- Produces: support for schema versions `0.3` and `0.4`, with version-specific integrated-Gate validation.

- [ ] Accept consistent manifest sets using supported versions `0.3` or `0.4`; reject mixed/unknown versions.
- [ ] Preserve v0.3 `integrated -> PASS/PASS_WITH_FINDINGS` requirement.
- [ ] For v0.4, allow `integrated` under any valid Gate verdict while still requiring `integrated_revision` and available occurrence evidence.
- [ ] Keep `awaiting_integration` PASS/current rules unchanged for both versions.
- [ ] Run focused tests to GREEN.

### Task 3: Derived conformance and v0.4 state schema

**Files:**
- Modify: `tools/aegis_state/compute.py`
- Create: `schemas/project-state/v0.4/project.schema.json`
- Create: `schemas/project-state/v0.4/authorities.schema.json`
- Create: `schemas/project-state/v0.4/gates.schema.json`
- Create: `schemas/project-state/v0.4/evidence.schema.json`
- Create: `schemas/project-state/v0.4/integrations.schema.json`
- Create: `schemas/project-state/v0.4/state.schema.json`

**Interfaces:**
- Produces: v0.4 generated fields `integration_conformance[]` and `nonconforming_integrations[]`.

- [ ] Copy v0.3 structural schemas to v0.4 and update IDs/titles/version constants.
- [ ] Extend v0.4 state schema with the two conformance projections.
- [ ] For `integrated`, derive `conforming` from PASS/PASS_WITH_FINDINGS and `nonconforming` from BLOCKED_*.
- [ ] Add an explicit finding for nonconforming current integration without adding a competing route.
- [ ] Emit v0.4 fields only for v0.4 manifests; preserve v0.3 generated shape.
- [ ] Run focused and full Project State tests.

### Task 4: Migrate minimal/self-host state and reconcile PR #9

**Files:**
- Modify: `examples/project-state/minimal/.aegis/*.json`
- Modify: `.aegis/project.json`
- Modify: `.aegis/authorities.json`
- Modify: `.aegis/gates.json`
- Modify: `.aegis/evidence.json`
- Modify: `.aegis/integrations.json`
- Regenerate: `.aegis/state.json`
- Modify: `.github/workflows/project-state.yml`

**Interfaces:**
- Produces: real self-hosted v0.4 Project State with PR #9 occurrence recorded truthfully.

- [ ] Register `aegis-project-state-v0.4` as Proposed replacement Authority without superseding v0.3 yet.
- [ ] Register a v0.4 P34 Gate as pending/blocked until fresh evidence exists.
- [ ] Add `ev-pr9-merged` repository-integration evidence for merge commit `a0c6b0103b119f517c7adf9ec4a90b5963e5e1e3`.
- [ ] Add `int-pr9` as `integrated` referencing the unchanged `BLOCKED_EVIDENCE` Gate.
- [ ] Do not add merge evidence to the Gate acceptance evidence set.
- [ ] Migrate root/minimal manifests to schema 0.4 and regenerate state.
- [ ] Update workflow labels/schema parsing to v0.4.
- [ ] Verify root state shows `int-pr9/current/nonconforming` and still routes P34.

### Task 5: P34 evidence and supersession preparation

**Files:**
- Modify: `docs/project-state-manifest-v0.4.md`
- Modify: root `.aegis/evidence.json`, `.aegis/gates.json`, `.aegis/state.json` only after fresh CI evidence.

**Interfaces:**
- Consumes: hosted merge-ref CI.
- Produces: evidence package suitable for P34; P23 remains separate.

- [ ] Run Project State Integrity and Skillset Integrity on the final PR head/merge ref.
- [ ] Record exact runs/jobs and acceptance results.
- [ ] If all v0.4 acceptance criteria pass, update the v0.4 Gate to PASS with durable evidence.
- [ ] Do not mark v0.3 Superseded until P23 is explicitly authorized.
