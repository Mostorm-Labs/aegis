# Execution Surface Behavioral Dogfood v0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:test-driven-development for the RED -> GREEN cycle and superpowers:verification-before-completion before returning evidence. Execute this package on a repository coding surface; do not redesign the Authority.

**Goal:** Exercise one real `CONTROL_REASONING -> CODE_EXECUTION -> CONTROL_REVIEW` handoff by having Codex add a bounded behavioral trace artifact and deterministic test without changing Aegis normative semantics.

**Architecture:** ChatGPT owns P30/P31 reasoning and packages the task from the existing Execution Surface Contract. Codex owns no lifecycle Authority; it executes the P32 repository work on `CODE_EXECUTION`, records a bounded executor return, and hands evidence back to ChatGPT for independent P34 review. The task adds only non-normative dogfood evidence plus a test that cross-checks that evidence against the existing machine-readable surface contract.

**Tech Stack:** JSON dogfood artifact, Python 3.12 `unittest`, existing `tools.aegis_skillset.model.load_skillset`, Git/GitHub CI.

**Spec:** `docs/execution-surface-contract-v0.1.md`

## Authority and baseline

Current Authority for this task:

- `docs/execution-surface-contract-v0.1.md`, especially sections 2-8, 10-12.
- `skillset/ownership.json` machine-readable execution-surface metadata.
- `skillset/shared/handoff-contract.md` canonical `surface_handoff` semantics.
- `skills/aegis-implementation/SKILL.md` P30-P33 execution-surface boundary.

Required repository ancestry before P32 starts:

- PR #11 integration commit `5fde161ccf71f283e727a238c914506edf79e258` must be an ancestor of the working HEAD.
- Project State v0.4 closure commit `4de19f76037ebc4a61d3b7be29c136d8a52ac515` must be an ancestor of the working HEAD.

The executor must record its actual starting HEAD before edits. Do not assume the package commit itself is the starting revision.

## Global constraints

- `Stage Ownership != Execution Surface`.
- `Surface Handoff != Ownership Handoff`.
- P31 executes on `CONTROL_REASONING`; P32 executes on `CODE_EXECUTION`; P34 returns to `CONTROL_REVIEW`.
- P32 Primary Owner remains `aegis-implementation` even while Codex executes the repository work.
- Do not modify `skillset/ownership.json`, any `SKILL.md`, any shared contract, `.aegis/**`, Project State tooling, Gate records, or Authority documents.
- Do not add a new lifecycle stage, status, or execution surface.
- Do not expand the two-file implementation scope below without returning a blocker.
- Agent claims are context, not P34 evidence. ChatGPT will corroborate the returned claim against the diff, tests, and hosted CI.

---

### Task 1: Behavioral trace artifact + deterministic contract test

**Files:**
- Create: `skillset/dogfood/execution-surface-behavioral-v0.1.json`
- Create: `tests/skillset/test_execution_surface_behavioral_dogfood.py`

**Interfaces:**
- Consumes: `load_skillset(ROOT)` from `tools.aegis_skillset.model` and the existing machine-readable mappings in `skillset/ownership.json`.
- Produces: one durable dogfood trace plus one discovered `unittest` module. No production API or normative contract changes.

#### Trace shape

Create `skillset/dogfood/execution-surface-behavioral-v0.1.json` with this exact top-level structure. Replace only `<ACTUAL_STARTING_HEAD>` after running `git rev-parse HEAD` before edits.

```json
{
  "schema_version": "0.1",
  "scenario_id": "ES-BD-001",
  "purpose": "real_control_to_code_surface_handoff",
  "authority_refs": [
    "docs/execution-surface-contract-v0.1.md",
    "skillset/ownership.json",
    "skillset/shared/handoff-contract.md",
    "skills/aegis-implementation/SKILL.md"
  ],
  "surface_handoff": {
    "type": "surface_handoff",
    "stage": "P32",
    "stage_owner": "aegis-implementation",
    "from_surface": "CONTROL_REASONING",
    "to_surface": "CODE_EXECUTION",
    "preferred_executor": "codex",
    "reason": "behavioral_dogfood_repository_execution",
    "package_ref": "docs/superpowers/plans/2026-08-28-execution-surface-behavioral-dogfood-v0.1.md",
    "return_surface": "CONTROL_REVIEW"
  },
  "executor_observation": {
    "executor": "codex",
    "surface": "CODE_EXECUTION",
    "starting_revision": "<ACTUAL_STARTING_HEAD>",
    "status": "READY_FOR_REVIEW",
    "changed_files": [
      "skillset/dogfood/execution-surface-behavioral-v0.1.json",
      "tests/skillset/test_execution_surface_behavioral_dogfood.py"
    ],
    "verification_commands": [
      "python3 -m unittest tests.skillset.test_execution_surface_behavioral_dogfood -v",
      "python3 -m unittest tests.skillset.test_execution_surface_contract tests.skillset.test_metadata -v"
    ]
  }
}
```

`executor_observation` is an execution claim only. It must not be treated as Gate evidence without independent corroboration.

- [ ] **Step 1: Preflight the exact P32 baseline**

Run:

```bash
git status --short
git rev-parse HEAD
git merge-base --is-ancestor 5fde161ccf71f283e727a238c914506edf79e258 HEAD
git merge-base --is-ancestor 4de19f76037ebc4a61d3b7be29c136d8a52ac515 HEAD
```

Expected:

- working tree has no unrelated uncommitted changes;
- both ancestry checks exit 0;
- capture `git rev-parse HEAD` as `<ACTUAL_STARTING_HEAD>`.

If either required ancestor is absent, return `BLOCKED_IMPLEMENTATION` with the observed HEAD and stop without editing.

- [ ] **Step 2: Write the RED test first**

Create `tests/skillset/test_execution_surface_behavioral_dogfood.py` with:

```python
import json
import re
import unittest
from pathlib import Path

from tools.aegis_skillset.model import load_skillset

ROOT = Path(__file__).resolve().parents[2]
TRACE_PATH = ROOT / "skillset/dogfood/execution-surface-behavioral-v0.1.json"
EXPECTED_CHANGED_FILES = [
    "skillset/dogfood/execution-surface-behavioral-v0.1.json",
    "tests/skillset/test_execution_surface_behavioral_dogfood.py",
]


class ExecutionSurfaceBehavioralDogfoodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_skillset(ROOT)
        cls.trace = json.loads(TRACE_PATH.read_text(encoding="utf-8"))

    def test_surface_handoff_matches_machine_contract(self):
        handoff = self.trace["surface_handoff"]
        config = self.config

        self.assertEqual(self.trace["scenario_id"], "ES-BD-001")
        self.assertEqual(handoff["type"], "surface_handoff")
        self.assertEqual(handoff["stage"], "P32")
        self.assertEqual(handoff["stage_owner"], config.primary_owner_by_stage["P32"])
        self.assertEqual(handoff["from_surface"], config.execution_surface_by_stage["P31"])
        self.assertEqual(handoff["to_surface"], config.execution_surface_by_stage["P32"])
        self.assertEqual(
            handoff["preferred_executor"],
            config.executor_profiles[config.default_executor_profile][handoff["to_surface"]],
        )
        self.assertEqual(handoff["return_surface"], config.execution_surface_by_stage["P34"])
        self.assertFalse(config.surface_handoff_transfers_ownership)

    def test_executor_observation_is_bounded_and_auditable(self):
        observation = self.trace["executor_observation"]
        self.assertEqual(observation["executor"], "codex")
        self.assertEqual(observation["surface"], "CODE_EXECUTION")
        self.assertEqual(observation["status"], "READY_FOR_REVIEW")
        self.assertRegex(observation["starting_revision"], re.compile(r"^[0-9a-f]{40}$"))
        self.assertEqual(observation["changed_files"], EXPECTED_CHANGED_FILES)
        self.assertEqual(
            observation["verification_commands"],
            [
                "python3 -m unittest tests.skillset.test_execution_surface_behavioral_dogfood -v",
                "python3 -m unittest tests.skillset.test_execution_surface_contract tests.skillset.test_metadata -v",
            ],
        )


if __name__ == "__main__":
    unittest.main()
```

Do **not** create the JSON trace yet.

- [ ] **Step 3: Run the focused RED test**

Run:

```bash
python3 -m unittest tests.skillset.test_execution_surface_behavioral_dogfood -v
```

Expected: FAIL/ERROR because `skillset/dogfood/execution-surface-behavioral-v0.1.json` does not exist.

Record the exact RED result in the return evidence.

- [ ] **Step 4: Create the minimal trace artifact**

Create `skillset/dogfood/execution-surface-behavioral-v0.1.json` using the exact trace shape above, substituting only the captured 40-character starting revision.

Do not add fields, rename surfaces, or alter expected semantics.

- [ ] **Step 5: Run focused GREEN verification**

Run exactly:

```bash
python3 -m unittest tests.skillset.test_execution_surface_behavioral_dogfood -v
python3 -m unittest tests.skillset.test_execution_surface_contract tests.skillset.test_metadata -v
```

Expected: all PASS.

- [ ] **Step 6: Check scope before commit**

Run:

```bash
git status --short
git diff --check
git diff --name-only
```

Expected changed paths are exactly:

```text
skillset/dogfood/execution-surface-behavioral-v0.1.json
tests/skillset/test_execution_surface_behavioral_dogfood.py
```

Any additional path is a scope violation. Revert only the executor's own out-of-scope edits; never discard unrelated pre-existing work.

- [ ] **Step 7: Commit the P32 result**

```bash
git add skillset/dogfood/execution-surface-behavioral-v0.1.json tests/skillset/test_execution_surface_behavioral_dogfood.py
git commit -m "test: add execution surface behavioral dogfood"
```

Then run:

```bash
git rev-parse HEAD
git status --short
```

Return the resulting commit SHA and clean/dirty status to ChatGPT. Do not edit this plan to insert the result SHA.

## P32 evidence-return contract

Return one compact evidence block containing:

```text
scenario_id: ES-BD-001
executor: codex
surface: CODE_EXECUTION
starting_revision: <40-char SHA>
result_revision: <40-char SHA>
red_command: python3 -m unittest tests.skillset.test_execution_surface_behavioral_dogfood -v
red_result: <exact failing summary>
green_commands:
  - python3 -m unittest tests.skillset.test_execution_surface_behavioral_dogfood -v
  - python3 -m unittest tests.skillset.test_execution_surface_contract tests.skillset.test_metadata -v
green_result: <exact passing summaries>
changed_files:
  - skillset/dogfood/execution-surface-behavioral-v0.1.json
  - tests/skillset/test_execution_surface_behavioral_dogfood.py
worktree_status: <git status --short after commit>
blocker: null | <exact blocker>
```

Do not claim P34 PASS. The return surface is ChatGPT `CONTROL_REVIEW`, which will independently inspect repository diff, tests, hosted CI, Authority conformance, and scope.

## Blocked-return behavior

Stop without inventing a repair when:

- Current Authority or the package contradicts repository reality -> `BLOCKED_AUTHORITY` and return the contradiction.
- Required ancestor/worktree/tooling cannot be established -> `BLOCKED_ENVIRONMENT` or `BLOCKED_IMPLEMENTATION` with exact evidence.
- The requested two-file change would require changing normative Aegis semantics -> `BLOCKED_AUTHORITY`.
- A pre-existing unrelated test failure prevents credible verification -> return the failure; do not fix outside scope.

## P34 acceptance after return

ChatGPT may accept ES-BD-001 only if independent review proves all of the following:

1. the actual P32 starting revision contains this P31 package and both required ancestors;
2. the diff contains exactly the two authorized files;
3. the trace matches machine-readable owner/surface/executor mappings;
4. RED occurred before the trace existed;
5. focused GREEN verification passed;
6. hosted Skillset Integrity passes on the returned result revision or a descendant containing only review/evidence updates;
7. no Authority, ownership, Project State, Gate, or Skill semantics changed during P32;
8. Codex did not claim P34 ownership and returned to `CONTROL_REVIEW`.

A PASS here is behavioral evidence for Execution Surface Contract v0.1 only. It does not clear the independent PR #9 `BLOCKED_EVIDENCE` Gate or OpenAI baseline `BLOCKED_ENVIRONMENT`.

## Surface handoff emitted by P31

```yaml
type: surface_handoff
stage: P32
stage_owner: aegis-implementation
from_surface: CONTROL_REASONING
to_surface: CODE_EXECUTION
preferred_executor: codex
reason: behavioral_dogfood_repository_execution
package_ref: docs/superpowers/plans/2026-08-28-execution-surface-behavioral-dogfood-v0.1.md
return_surface: CONTROL_REVIEW
```

This is an execution-location transfer only. Primary Owner remains `aegis-implementation` for P32.