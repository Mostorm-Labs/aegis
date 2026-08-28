# Execution Surface Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add machine-readable execution-surface routing and surface-handoff semantics so Aegis defaults high-level reasoning to ChatGPT and repository-heavy implementation/reverification to Codex without changing lifecycle-stage ownership.

**Architecture:** Keep lifecycle ownership and execution location as orthogonal dimensions. Extend `skillset/ownership.json` with semantic surfaces, an OpenAI executor profile, and P30-P36 surface mappings; parse/validate them in `tools/aegis_skillset/model.py`; define `surface_handoff` once in the shared handoff contract; then update implementation/gate-review/router instructions and regenerate distributed Skills.

**Tech Stack:** JSON metadata, Python dataclasses/validation, unittest/pytest-compatible tests, Markdown Skill contracts, existing Aegis skillset generator and CI.

**Spec:** `docs/execution-surface-contract-v0.1.md`

## Global Constraints

- `Stage Ownership != Execution Surface`.
- `Surface Handoff != Ownership Handoff`.
- P30/P31 -> `CONTROL_REASONING`.
- P32/P33 -> `CODE_EXECUTION`.
- P34/P35 -> `CONTROL_REVIEW`.
- P36 -> `CODE_REVERIFY`.
- Default OpenAI profile maps control surfaces to ChatGPT and code surfaces to Codex.
- Provider/product names remain profile metadata, not semantic Authority.
- Existing v0.2 single-owner composition semantics must remain unchanged.

---

### Task 1: Machine-readable surface metadata

**Files:**
- Modify: `skillset/ownership.json`
- Modify: `tools/aegis_skillset/model.py`
- Test: `tests/skillset/test_metadata.py`

**Interfaces:**
- Consumes: existing `primary_owner_by_stage`, `cross_cutting`, and `composition` metadata.
- Produces: `semantic_surfaces: tuple[str, ...]`, `executor_profiles: dict[str, dict[str, str]]`, `default_executor_profile: str`, and `execution_surface_by_stage: dict[str, str]` on `SkillSetConfig`.

- [ ] **Step 1: Write failing metadata tests**

Add tests asserting exact surface vocabulary, OpenAI profile mapping, exact P30-P36 mappings, and negative validation for unknown/missing execution surfaces.

- [ ] **Step 2: Run the focused RED test**

Run: `python -m unittest tests.skillset.test_metadata -v`

Expected: FAIL because surface fields are absent from `SkillSetConfig` / `ownership.json`.

- [ ] **Step 3: Add minimal metadata and parser/validator**

Add this contract to `skillset/ownership.json`:

```json
"execution_surfaces": {
  "semantic_surfaces": ["CONTROL_REASONING", "CODE_EXECUTION", "CONTROL_REVIEW", "CODE_REVERIFY"],
  "default_executor_profile": "openai",
  "executor_profiles": {
    "openai": {
      "CONTROL_REASONING": "chatgpt",
      "CODE_EXECUTION": "codex",
      "CONTROL_REVIEW": "chatgpt",
      "CODE_REVERIFY": "codex"
    }
  },
  "surface_handoff_transfers_ownership": false,
  "execution_surface_by_stage": {
    "P30": "CONTROL_REASONING",
    "P31": "CONTROL_REASONING",
    "P32": "CODE_EXECUTION",
    "P33": "CODE_EXECUTION",
    "P34": "CONTROL_REVIEW",
    "P35": "CONTROL_REVIEW",
    "P36": "CODE_REVERIFY"
  }
}
```

Parse those fields into `SkillSetConfig`. Validate: exact stage key set P30-P36; every mapped surface is declared; default profile exists; every semantic surface appears in the default profile; `surface_handoff_transfers_ownership` is false.

- [ ] **Step 4: Run focused GREEN test**

Run: `python -m unittest tests.skillset.test_metadata -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skillset/ownership.json tools/aegis_skillset/model.py tests/skillset/test_metadata.py
git commit -m "feat: add execution surface metadata"
```

### Task 2: Shared surface-handoff contract

**Files:**
- Modify: `skillset/shared/handoff-contract.md`
- Modify: `tests/skillset/test_instruction_contracts.py` if present; otherwise add the assertions to the existing shared-contract test file that validates handoff text.

**Interfaces:**
- Consumes: existing `support_return` and `ownership_handoff` semantics.
- Produces: canonical `surface_handoff` vocabulary and non-ownership-transfer invariant.

- [ ] **Step 1: Write failing text-contract tests**

Assert the shared contract contains `surface_handoff`, `Surface Handoff != Ownership Handoff`, `stage_owner`, `from_surface`, `to_surface`, `package_ref`, and an explicit statement that surface transfer does not transfer ownership.

- [ ] **Step 2: Run the focused RED test**

Run the repository's focused skill instruction-contract test command.

Expected: FAIL because the shared contract lacks surface-handoff semantics.

- [ ] **Step 3: Add the shared contract**

Add a third edge type after support/ownership handoffs with this canonical shape:

```yaml
type: surface_handoff
stage: P32
stage_owner: aegis-implementation
from_surface: CONTROL_REASONING
to_surface: CODE_EXECUTION
preferred_executor: codex
reason: repository_heavy_execution
package_ref: <task-package-ref>
return_surface: CONTROL_REVIEW
```

State explicitly that surface handoff is ephemeral execution metadata and never transfers Primary Owner, Authority, Evidence, Gate, Integration, or Project State semantics.

- [ ] **Step 4: Run focused GREEN test**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skillset/shared/handoff-contract.md tests/skillset
git commit -m "feat: define surface handoff contract"
```

### Task 3: Implementation-family instruction boundaries

**Files:**
- Modify: `skillset/skills/aegis-implementation/SKILL.md`
- Modify: `skillset/skills/aegis-implementation/references/implementation-control.md`
- Modify: `skillset/skills/aegis-gate-review/SKILL.md`
- Modify: relevant gate-review reference if one exists
- Modify: central `skillset/skills/aegis/SKILL.md` only where needed to expose surface routing
- Test: existing Skill instruction contract tests

**Interfaces:**
- Consumes: machine-readable surface mapping and shared `surface_handoff` contract.
- Produces: executable Skill instructions that preserve stage ownership while routing repository-heavy P32/P33/P36 work to the code surfaces.

- [ ] **Step 1: Write failing instruction tests**

Assert `aegis-implementation` says P30/P31 default to `CONTROL_REASONING`, P32/P33 default to `CODE_EXECUTION`, requires an approved package reference, and forbids treating a surface handoff as ownership transfer. Assert gate-review keeps P34/P35 on `CONTROL_REVIEW` and permits P36 execution on `CODE_REVERIFY` only after classification/repair scope is explicit.

- [ ] **Step 2: Run RED tests**

Expected: FAIL on missing instruction text.

- [ ] **Step 3: Update canonical Skill sources**

Add concise execution-surface sections. Preserve all existing single-owner, earlier-untrusted-layer, and Project State support rules unchanged.

- [ ] **Step 4: Run GREEN tests**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skillset/skills tests/skillset
git commit -m "feat: route implementation across execution surfaces"
```

### Task 4: Generate distributions and regression gate

**Files:**
- Regenerate: `skills/*` through the repository's existing generator
- Modify only generated files produced by canonical source changes

**Interfaces:**
- Consumes: canonical `skillset/` metadata and Skill sources.
- Produces: distribution Skills containing identical execution-surface boundaries.

- [ ] **Step 1: Run generator check before generation**

Run the repository's existing `generate -- --check` equivalent.

Expected: FAIL because canonical and distributed Skills differ after Task 3.

- [ ] **Step 2: Regenerate Skills**

Run the existing skillset generator without `--check`.

- [ ] **Step 3: Run deterministic regression suite**

Run metadata tests, shared instruction-contract tests, package/generator checks, and the full skillset deterministic test suite used by `.github/workflows/skillset.yml`.

Expected: all PASS, including existing v0.2 ownership/composition tests.

- [ ] **Step 4: Commit**

```bash
git add skills
git commit -m "build: regenerate execution surface skill contracts"
```

### Task 5: P34 acceptance evidence

**Files:**
- Add or update the repository's appropriate evidence record for this architectural change.

**Interfaces:**
- Consumes: deterministic test and CI results from Tasks 1-4.
- Produces: a Gate-reviewable evidence bundle; no supersession of unrelated PR #9 authority is implied.

- [ ] **Step 1: Run final deterministic verification on the branch head**

Run the complete skillset integrity workflow inputs locally where available and hosted CI after push.

- [ ] **Step 2: Record exact evidence**

Record branch/head SHA, commands, test results, CI run/job IDs, and any environment limitations.

- [ ] **Step 3: Perform P34 review**

Verify Authority conformance, scope drift, required tests, generated distribution parity, and regression behavior. Do not claim Gate PASS from implementation-agent statements alone.

- [ ] **Step 4: Commit evidence if the repository's governance policy requires committed evidence**

```bash
git add <evidence-path>
git commit -m "docs: record execution surface gate evidence"
```
