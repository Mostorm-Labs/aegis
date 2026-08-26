# Project State v0.3 Historical Integration Durability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Project State v0.3 so durable repository integration history survives later Authority supersession while current Gate/actionability routing remains fail-closed.

**Architecture:** Keep integration occurrence and historical Gate verdict as authored facts. Derive current integration applicability and Gate actionability from the current Authority/Gate/Evidence graph; completed all-historical provenance becomes non-actionable history, mixed Current/Historical dependencies fail closed to Authority review, and awaiting integration retains v0.2 current-validity requirements.

**Tech Stack:** Python 3 stdlib, `unittest`, JSON / JSON Schema documents, GitHub Actions, Aegis Skill markdown.

**Spec:** `docs/superpowers/specs/2026-08-27-project-state-v0.3-historical-integration-design.md`

## Global Constraints

- `SCHEMA_VERSION = "0.3"` and `GENERATOR_VERSION = "0.3"`.
- Do not mutate `schemas/project-state/v0.1/` or `schemas/project-state/v0.2/`.
- `integrated` is durable occurrence; later supersession must not erase it.
- `awaiting_integration` still requires a current-effective `PASS`/`PASS_WITH_FINDINGS` Gate and available evidence.
- Applicability/actionability are generated, never authored.
- A Gate is automatically historical only when all validity-bearing `authority_ids` are `Superseded/Historical` and it is retained for completed-history provenance.
- Mixed Current + Historical Gate Authority sets fail closed to `needs_review` and contribute Authority/P21 routing.
- Historical-only `BLOCKED_*` verdicts remain audit history but do not reactivate current blockers.
- Missing/invalid occurrence evidence still rejects `integrated` provenance.
- No PR #4 or Aegis-specific production special cases.
- R03-09 real Aegis self-host oracle is mandatory acceptance evidence before P34.

---

### Task 1: Freeze v0.3 version boundary and RED fixtures

**Files:**
- Modify: `tests/project_state/helpers.py`
- Modify: `tests/project_state/test_integrations_v02.py`
- Modify: `tests/project_state/test_v02_model.py`
- Create: `tests/project_state/test_history_v03.py`
- Modify later in GREEN: `tools/aegis_state/__init__.py`, `tools/aegis_state/model.py`

**Interfaces:**
- Consumes: existing `load_manifests()`, `validate_manifests()`, `compute_state()`.
- Produces: v0.3 fixtures and focused RED oracles R03-01 through R03-08.

- [ ] **Step 1: Migrate shared fixtures to schema 0.3 without changing existing behavioral assertions**

Change all project-state test fixture manifests from `"schema_version":"0.2"` to `"schema_version":"0.3"`. Do not weaken existing assertions for Gate blockers, integration handoff, digest behavior, duplicate IDs, dangling refs, or unavailable evidence.

- [ ] **Step 2: Add focused failing history tests**

Create `tests/project_state/test_history_v03.py` with explicit cases equivalent to:

```python
class HistoryV03Tests(unittest.TestCase):
    def test_integrated_survives_all_authority_supersession(self):
        state, errors = scenario_integrated_then_superseded()
        self.assertEqual(errors, [])
        self.assertIn(
            {"integration_id": "int-old", "applicability": "historical"},
            state["integration_applicability"],
        )
        self.assertIn("G-old", state["historical_gates"])
        self.assertNotIn("G-old", state["stale_gates"])

    def test_historical_blocked_gate_cannot_support_integrated(self):
        errors = scenario_integrated_with_historical_blocked_gate()
        self.assertTrue(any("requires historical PASS/PASS_WITH_FINDINGS" in e for e in errors))

    def test_awaiting_still_rejects_noncurrent_gate(self):
        errors = scenario_awaiting_with_superseded_authority()
        self.assertTrue(any("requires current-valid gate" in e for e in errors))

    def test_current_stale_gate_remains_actionable(self):
        state = scenario_current_authority_stale_gate()
        self.assertIn("G-current", state["stale_gates"])
        self.assertEqual(state["earliest_untrusted_layer"], "verification")
        self.assertEqual(state["recommended_next_stage"], "P34")

    def test_mixed_authority_gate_fails_closed_to_p21(self):
        state = scenario_mixed_current_historical_gate()
        self.assertIn("G-mixed", state["needs_review_gates"])
        self.assertEqual(state["earliest_untrusted_layer"], "authority")
        self.assertEqual(state["recommended_next_stage"], "P21")

    def test_integrated_requires_available_occurrence_evidence(self):
        errors = scenario_integrated_with_missing_occurrence_evidence()
        self.assertTrue(any("uses unavailable evidence" in e for e in errors))
```

The helper scenarios must build ordinary manifests; do not call any special history API unavailable to users.

- [ ] **Step 3: Run focused tests and verify RED**

Run:

```bash
python3 -m unittest tests.project_state.test_history_v03 -v
```

Expected: failures caused by v0.2 semantics, including absent `integration_applicability` / `historical_gates`, integrated history rejected for non-current Gate, or mixed Gate routed as stale/P34 rather than Authority/P21. Import/syntax failures do not count as valid RED.

- [ ] **Step 4: Commit the RED tests only**

```bash
git add tests/project_state
git commit -m "test: define project state v0.3 history semantics"
```

---

### Task 2: Implement Gate history/actionability classification

**Files:**
- Modify: `tools/aegis_state/compute.py`
- Test: `tests/project_state/test_history_v03.py`

**Interfaces:**
- Produces helper classification internal to `compute.py`:
  - Authority membership state for a Gate: `current | mixed | historical | unknown`.
  - Generated `historical_gates: list[str]`.
- Preserves: existing `stale_gates`, `needs_review_gates`, `blocking_gates` for current-actionable Gate problems.

- [ ] **Step 1: Add the smallest classification helper needed by the tests**

Implement internal logic equivalent to:

```python
def _gate_authority_membership(gate: dict, auth_by_id: dict[str, dict]) -> str:
    statuses = []
    for aid in gate.get("authority_ids", []):
        authority = auth_by_id.get(aid)
        if not authority:
            return "unknown"
        statuses.append(authority.get("status"))
    if not statuses:
        return "unknown"
    has_current = any(s in {"Current", "Proposed"} for s in statuses)
    has_history = any(s in {"Superseded", "Historical"} for s in statuses)
    if has_current and has_history:
        return "mixed"
    if has_history and not has_current:
        return "historical"
    if has_current and not has_history:
        return "current"
    return "unknown"
```

`Proposed` remains validity-bearing like current planning state, matching existing authority validity semantics.

- [ ] **Step 2: Separate historical Gate records from current actionable Gate validity**

During Gate computation:

```python
membership = _gate_authority_membership(gate, auth_by_id)
if membership == "historical":
    historical_gates.append(gid)
    # retain declared/effective provenance drift information if useful,
    # but do not append this Gate to stale_gates/needs_review_gates or routing.
elif membership in {"mixed", "unknown"}:
    needs_review_gates.append(gid)
    findings.append(f"gate {gid} needs Authority review because its validity-bearing Authority set is mixed or unresolved")
    route_candidates.append(("authority", "P21", None))
else:
    # current Authority path: keep v0.2 evidence/validity computation.
```

Historical-only `BLOCKED_*` verdicts must never enter `blocking_gates`.

- [ ] **Step 3: Keep current stale Gate behavior unchanged**

For current Gate Authority membership, retain evidence checks and effective validity. A current stale Gate still goes to `stale_gates` and contributes `verification/P34`.

- [ ] **Step 4: Run Gate-focused tests**

Run:

```bash
python3 -m unittest \
  tests.project_state.test_history_v03.HistoryV03Tests.test_current_stale_gate_remains_actionable \
  tests.project_state.test_history_v03.HistoryV03Tests.test_mixed_authority_gate_fails_closed_to_p21 -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/aegis_state/compute.py tests/project_state/test_history_v03.py
git commit -m "feat: separate historical and actionable gates"
```

---

### Task 3: Implement durable Integration occurrence and derived applicability

**Files:**
- Modify: `tools/aegis_state/model.py`
- Modify: `tools/aegis_state/compute.py`
- Test: `tests/project_state/test_history_v03.py`
- Test: `tests/project_state/test_v02_model.py`
- Test: `tests/project_state/test_integrations_v02.py`

**Interfaces:**
- Produces generated field:

```python
"integration_applicability": [
    {"integration_id": str, "applicability": "current|needs_review|stale|historical"}
]
```

sorted by `integration_id`.

- [ ] **Step 1: Change validator semantics only for completed occurrence**

For `integrated`:

```python
if gate.get("verdict") not in PASS_VERDICTS:
    errors.append(f"integration {iid}: requires historical PASS/PASS_WITH_FINDINGS gate {gate_id}")
if not integrated_revision:
    errors.append(...)
for eid in evidence_ids:
    if evidence exists and evidence.status != "available":
        errors.append(f"integration {iid}: uses unavailable evidence {eid}")
```

Do **not** require `gate.validity == current` or computed current-valid Gate for `integrated`.

For `awaiting_integration`, preserve the existing current verdict/declared/current-effective validation and available evidence requirement.

For `closed_unmerged`, retain history without current Gate routing.

- [ ] **Step 2: Restrict post-compute current-validity check to awaiting integrations**

Change the existing validator loop that checks `noncurrent_gate_ids` so only `status == "awaiting_integration"` is rejected for stale/needs-review Gate validity. Completed `integrated` history must not be rejected solely because its Gate is now historical.

- [ ] **Step 3: Generate Integration applicability**

Use Gate membership plus effective current validity:

```python
if status in {"integrated", "closed_unmerged"} and membership == "historical":
    applicability = "historical"
elif membership in {"mixed", "unknown"}:
    applicability = "needs_review"
elif gate_effective[gid] == "stale":
    applicability = "stale"
elif gate_effective[gid] == "needs_review":
    applicability = "needs_review"
else:
    applicability = "current"
```

For `awaiting_integration`, any non-current applicability should already fail strict validation; compute still remains deterministic.

- [ ] **Step 4: Ensure only current awaiting integrations create handoff**

Keep `awaiting_integrations[]` and finishing-development-branch handoff only when the Gate is PASS/PASS_WITH_FINDINGS and current-effective. Historical completed records never create implementation handoff.

- [ ] **Step 5: Run focused history and existing integration suites**

Run:

```bash
python3 -m unittest \
  tests.project_state.test_history_v03 \
  tests.project_state.test_integrations_v02 \
  tests.project_state.test_v02_model -v
```

Expected: PASS after fixture version migration; prior duplicate/dangling/evidence/current-awaiting behavior stays green.

- [ ] **Step 6: Commit**

```bash
git add tools/aegis_state/model.py tools/aegis_state/compute.py tests/project_state
git commit -m "feat: preserve historical integration occurrence"
```

---

### Task 4: Advance schema/generator to v0.3 and expose generated projections

**Files:**
- Modify: `tools/aegis_state/__init__.py`
- Modify: `tools/aegis_state/model.py`
- Modify: `tools/aegis_state/compute.py`
- Create: `schemas/project-state/v0.3/project.schema.json`
- Create: `schemas/project-state/v0.3/authorities.schema.json`
- Create: `schemas/project-state/v0.3/gates.schema.json`
- Create: `schemas/project-state/v0.3/evidence.schema.json`
- Create: `schemas/project-state/v0.3/integrations.schema.json`
- Create: `schemas/project-state/v0.3/state.schema.json`
- Modify: `examples/project-state/minimal/.aegis/*.json`

**Interfaces:**
- `tools.aegis_state.GENERATOR_VERSION == "0.3"`
- `tools.aegis_state.model.SCHEMA_VERSION == "0.3"`
- generated state includes `historical_gates[]` and `integration_applicability[]`.

- [ ] **Step 1: Copy v0.2 schemas into a new v0.3 tree**

Do not edit v0.2 files. Change `$id`, titles, and `schema_version` constants to 0.3.

- [ ] **Step 2: Update v0.3 state schema**

Require deterministic fields already produced by state plus:

```json
"historical_gates": {
  "type": "array",
  "items": {"type": "string"},
  "uniqueItems": true
},
"integration_applicability": {
  "type": "array",
  "items": {
    "type": "object",
    "additionalProperties": false,
    "required": ["integration_id", "applicability"],
    "properties": {
      "integration_id": {"type": "string", "minLength": 1},
      "applicability": {"enum": ["current", "needs_review", "stale", "historical"]}
    }
  }
}
```

- [ ] **Step 3: Keep authored integration schema occurrence-focused**

The v0.3 `integrations.schema.json` keeps existing authored fields/statuses; do not add authored applicability/actionability fields.

- [ ] **Step 4: Advance constants and generated state version**

Set generator/model schema to `0.3`; `compute_state()` returns `schema_version: "0.3"`.

- [ ] **Step 5: Migrate minimal example to 0.3 and regenerate `state.json` using tooling**

Run:

```bash
python3 -m tools.aegis_state.cli recompute examples/project-state/minimal --write
python3 -m tools.aegis_state.cli validate examples/project-state/minimal
python3 -m tools.aegis_state.cli check examples/project-state/minimal
```

Expected:

```text
STATE_WRITTEN
VALID
STATE_OK
```

Do not hand-edit generated `state.json` after recompute.

- [ ] **Step 6: Parse all six v0.3 schemas**

Run a stdlib JSON parse loop over `schemas/project-state/v0.3/*.json`; expected no parse failures.

- [ ] **Step 7: Commit**

```bash
git add tools/aegis_state schemas/project-state/v0.3 examples/project-state/minimal tests/project_state
git commit -m "feat: publish project state schema v0.3"
```

---

### Task 5: Update Aegis Skill project-state contract and CI

**Files:**
- Modify: `skills/aegis/references/project-state.md`
- Modify: `skills/aegis/SKILL.md` only for thin version/reference wording if necessary
- Modify: `.github/workflows/project-state.yml`

**Interfaces:**
- Skill continues to treat `state.json` as generated cache.
- Skill understands historical occurrence/current applicability/current actionability split.
- CI parses v0.3 schemas and runs full project-state tests.

- [ ] **Step 1: Update `references/project-state.md` to v0.3**

Document:

```text
Historical Occurrence != Current Applicability != Current Actionability
```

and the exact all-historical / mixed / current rules from the approved spec. Preserve blocked-Gate propagation from v0.2.

- [ ] **Step 2: Keep `SKILL.md` thin**

Only change bootstrap wording necessary to identify v0.3 manifests/reference; do not duplicate the full rules into the control-plane entrypoint.

- [ ] **Step 3: Update workflow schema path/checks**

CI must parse `schemas/project-state/v0.3/*.json`, validate/check the minimal 0.3 example, and run:

```bash
python3 -m unittest discover -s tests/project_state -v
```

- [ ] **Step 4: Validate/package the Skill**

Use Skill Creator's repository validator/package scripts as required by the installed skill. Expected: `Skill is valid!` and a valid `skill.zip` archive.

- [ ] **Step 5: Run full local regression**

```bash
python3 -m unittest discover -s tests/project_state -v
python3 -m tools.aegis_state.cli validate examples/project-state/minimal
python3 -m tools.aegis_state.cli check examples/project-state/minimal
```

Expected: all tests pass; `VALID`; `STATE_OK`.

- [ ] **Step 6: Commit**

```bash
git add skills/aegis .github/workflows/project-state.yml
git commit -m "docs: teach Aegis project state v0.3 history semantics"
```

---

### Task 6: Execute R03-09 real Aegis self-host acceptance oracle

**Files:**
- Evidence source: current PR #5 root `.aegis/` manifests and GitHub repository facts
- No production special-case file.
- If durable fixture is needed for CI, create only a generic `tests/project_state/fixtures/aegis_self_host_v03/` copy whose data is traceable to the same repository facts.

**Interfaces:**
- Consumes v0.3 tooling from Tasks 2-5.
- Produces acceptance evidence before P34.

- [ ] **Step 1: Build the truthful v0.3 self-host input from repository facts**

Must preserve:

```text
PR #4 integrated @ 555bac21d485fc4530680c61719fc36831021b0d
07 v0.1 Superseded
PR #7 integrated @ 8ca7b49d40a17e8cb7ffba86632da3aeae5e911c
07 v0.2 Current (until v0.3 P34/supersession)
OpenAI real baseline = BLOCKED_ENVIRONMENT
```

Do not delete or relabel historical PR #4 integration.

- [ ] **Step 2: Run strict v0.3 recompute/validate/check**

Required assertions:

```text
int-pr4 applicability = historical
int-pr7 applicability = current
gate-project-state-pr4 in historical_gates
blocking_gates = [gate-openai-real-baseline]
earliest_untrusted_layer = verification
recommended_next_stage = P34
strict check = STATE_OK
```

- [ ] **Step 3: Verify no PR #4/current-history repair hack exists**

Search changed production files for `pr4`, merge SHA `555bac21`, or Aegis-specific IDs. Expected: no production logic special cases.

- [ ] **Step 4: Record exact oracle output in the feature PR / Notion evidence section**

Label it as real self-host acceptance evidence, distinct from generic unit tests.

---

### Task 7: Repository P34 and supersession handoff

**Files:**
- Review all v0.3 changed files.
- Update docs/status only after evidence.

**Interfaces:**
- P34 consumes: focused tests, full regression, schemas, minimal E2E, Skill validation, R03-09, GitHub CI.

- [ ] **Step 1: Open PR from `aegis/project-state-manifest-v0.3` to current `main`**

PR body must state v0.2 remains Current until acceptance and list F08-03 / R03-01..09 evidence.

- [ ] **Step 2: Require fresh GitHub CI on final head**

Do not accept old-head green runs. Inspect actual job steps/logs, not only status icons.

- [ ] **Step 3: Perform P34**

Accept only if:

```text
focused v0.3 regressions               PASS
existing project-state regression      PASS
v0.3 schema/minimal contract           PASS
Skill validation/package               PASS
R03-09 self-host oracle                STATE_OK
historical PR #4 truth                 preserved
current OpenAI blocker                 verification/P34
fresh repository CI                    PASS
```

- [ ] **Step 4: If P34 passes, execute P23 supersession**

Only then:

```text
07 v0.2 -> Superseded/Historical
07 v0.3 -> Current Replacement Authority
```

Update Notion and GitHub companion docs with explicit supersession reason and evidence.

- [ ] **Step 5: Integrate repository PR, then formally rerun 08**

The formal 08 rerun occurs after v0.3 repository integration. It must use current repository facts and may close F08-03 only if strict root self-host state remains truthful and `STATE_OK`.
