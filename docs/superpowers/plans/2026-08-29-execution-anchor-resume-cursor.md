# Execution Anchor + Resume Cursor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a shared execution-position contract so resumable Aegis tasks distinguish a stable trusted task anchor from a moving accepted resume cursor and do not misclassify valid descendant repository state as a starting-state mismatch.

**Architecture:** Keep lifecycle ownership and execution-surface routing unchanged. Extend the shared handoff contract and P31-P33 implementation instructions with `task_anchor` and optional `resume_cursor`, define explicit P33 reconciliation outcomes, and preserve the existing reviewer-accessible evidence-materialization boundary. Prove the behavior with a RED-first deterministic contract test plus a dogfood trace, then regenerate distributed Skills.

**Tech Stack:** Markdown contracts and Skills, JSON dogfood artifact, Python 3.12 `unittest`, existing Aegis skillset distribution tooling, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-08-29-execution-anchor-resume-cursor-design.md`

## Global Constraints

- `Task Anchor != Execution Cursor`.
- A resumable task must not use historical HEAD equality as its only starting-state predicate.
- P33 preserves verified descendant work and resumes at the first incomplete verified step.
- True ancestry divergence or Authority contradiction must fail closed.
- Execution-position metadata remains handoff/navigation metadata, not Authority/Evidence/Gate/Integration/Project State.
- Existing `materialized_ref` requirements remain unchanged.
- Do not modify Project State/Gate semantics or lifecycle ownership.

---

### Task 1: RED contract test for descendant resume semantics

**Files:**
- Create: `tests/skillset/test_execution_anchor_resume_cursor.py`

**Interfaces:**
- Consumes: canonical shared handoff contract, implementation Skill/control reference, v0.2 execution-surface Authority, and dogfood trace paths.
- Produces: deterministic text/fixture acceptance tests that fail until the new contract exists.

- [ ] **Step 1: Write the failing test**

Create assertions requiring all of:

```text
Task Anchor != Execution Cursor
task_anchor
resume_cursor
historical HEAD equality
DESCENDANT_CURSOR
ANCHOR_DESCENDANT_WITHOUT_CURSOR
BLOCKED_EXECUTION_DIVERGENCE
```

The test must also require a dogfood fixture whose scenario proves `anchor=old revision`, `actual=descendant revision`, `decision=P33_RESUME`, and `replay_completed_work=false`.

- [ ] **Step 2: Materialize RED before implementation**

Commit only the plan/spec and RED test. Open a draft PR so hosted Skillset Integrity executes against the RED-only revision. Record the exact failing run/job and confirm the failure is caused by missing new contract/fixture content, not syntax or unrelated failures.

### Task 2: Shared handoff and P31-P33 contract GREEN

**Files:**
- Modify: `skillset/shared/handoff-contract.md`
- Modify: `skillset/skills/aegis-implementation/SKILL.md`
- Modify: `skillset/skills/aegis-implementation/references/implementation-control.md`

**Interfaces:**
- Consumes: existing `surface_handoff`, `package_ref`, `materialized_ref` semantics.
- Produces: additive `task_anchor` and optional `resume_cursor` handoff metadata plus explicit P33 reconciliation semantics.

- [ ] **Step 1: Extend shared handoff contract minimally**

Add the approved shapes and state that repository task anchors use ancestry relations rather than default exact-HEAD equality.

- [ ] **Step 2: Update P31 packaging**

Require repository-backed resumable packages to encode a stable task anchor and carry an accepted resume cursor when P33 has one.

- [ ] **Step 3: Update P32/P33 behavior**

Define `EXACT_CURSOR`, `DESCENDANT_CURSOR`, `ANCHOR_DESCENDANT_WITHOUT_CURSOR`, and `DIVERGED`; require descendant reconciliation without replay and fail closed only on genuine divergence/contradiction.

### Task 3: Additive Authority v0.2 and dogfood evidence

**Files:**
- Create: `docs/execution-surface-contract-v0.2.md`
- Modify: `docs/execution-surface-contract-v0.1.md` only to mark supersession and link v0.2; do not rewrite historical content.
- Create: `skillset/dogfood/execution-anchor-resume-cursor-v0.1.json`

**Interfaces:**
- Consumes: v0.1 execution-surface contract and the approved design.
- Produces: current additive Authority plus a bounded non-normative behavioral trace.

- [ ] **Step 1: Publish v0.2 additive Authority**

Copy forward unchanged v0.1 surface ownership/materialization semantics and add only execution-anchor/resume-cursor rules.

- [ ] **Step 2: Mark v0.1 superseded**

Add a top-of-document status/link only.

- [ ] **Step 3: Add dogfood case**

Use concrete 40-character synthetic revisions with explicit ancestry relation metadata:

```json
{
  "scenario_id": "ES-RC-001",
  "stage": "P33",
  "task_anchor": {"revision": "1111111111111111111111111111111111111111", "relation": "ancestor"},
  "resume_cursor": {"revision": "2222222222222222222222222222222222222222"},
  "observed": {"revision": "3333333333333333333333333333333333333333", "relation_to_cursor": "descendant"},
  "decision": "P33_RESUME",
  "replay_completed_work": false
}
```

The fixture is semantic dogfood, not a claim that these synthetic SHAs exist in Git.

### Task 4: Regenerate distributions and verify GREEN

**Files:**
- Regenerate: `skills/*` from canonical `skillset/*` using existing build tooling.

**Interfaces:**
- Consumes: canonical skillset changes.
- Produces: generated/distributed Skills with no drift.

- [ ] **Step 1: Regenerate**

Run the repository's existing skillset build/write command or equivalent project script.

- [ ] **Step 2: Focused GREEN**

Run:

```bash
python3 -m unittest tests.skillset.test_execution_anchor_resume_cursor -v
python3 -m unittest tests.skillset.test_execution_surface_contract tests.skillset.test_execution_surface_behavioral_dogfood -v
python3 -m unittest tests.skillset.test_metadata tests.skillset.test_distribution_validation -v
```

Expected: PASS.

- [ ] **Step 3: Relevant full verification**

Run all `tests/skillset` and relevant `tests/project_state` suites plus generated-skill validation and diff/whitespace checks. No unrelated semantic changes are allowed.

### Task 5: Materialize reviewable result and PR

**Files:** none beyond prior tasks.

- [ ] **Step 1: Confirm exact changed-file scope and final branch HEAD**
- [ ] **Step 2: Push/materialize the final branch revision**
- [ ] **Step 3: Update the draft PR body with RED evidence, GREEN evidence, scope, and exact result revision**
- [ ] **Step 4: Confirm hosted CI on final revision is green**
- [ ] **Step 5: Return `result_revision` and reviewer-accessible `materialized_ref`; do not claim an independent P34 verdict beyond corroborated CI/evidence.**
