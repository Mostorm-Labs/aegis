# Project State v0.3 Historical Integration Durability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Project State v0.3 so durable repository integration history survives later Authority supersession while current Gate/actionability routing remains fail-closed.

**Architecture:** Keep integration occurrence and historical Gate verdict as authored facts. Derive current integration applicability and Gate actionability from the current Authority/Gate/Evidence graph; completed all-historical provenance becomes non-actionable history, mixed Current/Historical dependencies fail closed to Authority review, and awaiting integration retains v0.2 current-validity requirements.

**Tech Stack:** Python 3 stdlib, `unittest`, JSON / JSON Schema documents, GitHub Actions, Aegis Skill markdown.

**Spec:** `docs/superpowers/specs/2026-08-27-project-state-v0.3-historical-integration-design.md`

## Global Constraints

- `SCHEMA_VERSION = "0.3"` and `GENERATOR_VERSION = "0.3"` in the accepted implementation.
- Do not mutate `schemas/project-state/v0.1/` or `schemas/project-state/v0.2/`.
- `integrated` is durable occurrence; later supersession must not erase it.
- `awaiting_integration` still requires a current-effective `PASS`/`PASS_WITH_FINDINGS` Gate and available evidence.
- Applicability/actionability are generated, never authored.
- A Gate is automatically historical only when all validity-bearing `authority_ids` are `Superseded/Historical` and it is retained for completed-history provenance.
- Mixed Current + Historical Gate Authority sets fail closed to `needs_review` and contribute Authority/P21 routing.
- Historical-only `BLOCKED_*` verdicts remain audit history but do not reactivate current blockers.
- Missing or unavailable occurrence evidence rejects `integrated` provenance.
- Production code must not special-case PR #4, merge revision `555bac21d485fc4530680c61719fc36831021b0d`, or Aegis repository IDs.
- R03-09 real Aegis self-host oracle is mandatory acceptance evidence before P34.

---

### Task 1: Add semantic RED regressions against the current v0.2 implementation

**Files:**
- Create: `tests/project_state/test_history_v03.py`
- Read only: `tools/aegis_state/model.py`, `tools/aegis_state/compute.py`

**Interfaces:**
- Consumes current v0.2 `load_manifests()`, `validate_manifests()`, and `compute_state()`.
- Produces semantic RED evidence without changing manifest version first.

- [ ] **Step 1: Create a local scenario writer inside `test_history_v03.py` that emits schema 0.2 manifests**

Use ordinary authored manifests so the current loader accepts them. The helper must support:

```python
def write_scenario(root: Path, *, authorities: list[dict], gate: dict, integration: dict, evidence_status: str = "available") -> None:
    docs = {
        "project.json": {"schema_version":"0.2","project":{"id":"demo","name":"Demo","profile":"standard","lifecycle_hint":"implementation"}},
        "authorities.json": {"schema_version":"0.2","authorities":authorities,"impact_reviews":[]},
        "gates.json": {"schema_version":"0.2","gates":[gate]},
        "evidence.json": {"schema_version":"0.2","evidence":[{"id":"ev","type":"ci","ref":"ci://history","status":evidence_status}]},
        "integrations.json": {"schema_version":"0.2","integrations":[integration]},
    }
    aegis = root / ".aegis"
    aegis.mkdir(parents=True)
    for name, data in docs.items():
        (aegis / name).write_text(json.dumps(data), encoding="utf-8")
```

- [ ] **Step 2: Add R03-01/R03-02 test for durable integrated history**

Build one Superseded Authority, a historical PASS Gate, and an `integrated` record with `integrated_revision="abc123"`. Assert:

```python
errors = validate_manifests(load_manifests(root))
self.assertEqual(errors, [])
state = compute_state(load_manifests(root))
self.assertIn({"integration_id":"int-old","applicability":"historical"}, state["integration_applicability"])
self.assertIn("G-old", state["historical_gates"])
self.assertNotIn("G-old", state["stale_gates"])
```

- [ ] **Step 3: Add R03-03/R03-04 tests**

Historical `BLOCKED_IMPLEMENTATION` must not support an `integrated` record. An `awaiting_integration` record whose Gate is no longer current-valid must still be rejected.

- [ ] **Step 4: Add R03-05/R03-06/R03-07/R03-08 tests**

Assert all of the following:

```text
all-historical Gate -> historical_gates, no P34 route solely from history
Current Authority + stale evidence -> stale_gates + verification/P34
mixed Current + Historical Authority -> needs_review_gates + authority/P21
integrated occurrence + missing evidence -> validation error
```

- [ ] **Step 5: Run focused tests and verify semantic RED**

Run:

```bash
python3 -m unittest tests.project_state.test_history_v03 -v
```

Valid RED requires current v0.2 behavior to fail assertions because it rejects historical integration, lacks `historical_gates` / `integration_applicability`, or routes mixed/history incorrectly. Version mismatch, import error, syntax error, or missing fixture file does not count.

- [ ] **Step 6: Commit only the RED test file**

```bash
git add tests/project_state/test_history_v03.py
git commit -m "test: define project state v0.3 history semantics"
```

---

### Task 2: Implement Gate historical/actionable classification

**Files:**
- Modify: `tools/aegis_state/compute.py`
- Test: `tests/project_state/test_history_v03.py`

**Interfaces:**
- Produces internal `_gate_authority_membership(gate, auth_by_id)` returning `current | mixed | historical | unknown`.
- Produces generated `historical_gates: list[str]`.
- Preserves current-actionable `stale_gates`, `needs_review_gates`, and `blocking_gates`.

- [ ] **Step 1: Add membership classifier**

Implement:

```python
def _gate_authority_membership(gate: dict, auth_by_id: dict[str, dict]) -> str:
    statuses: list[str] = []
    for aid in gate.get("authority_ids", []):
        authority = auth_by_id.get(aid)
        if not authority:
            return "unknown"
        status = authority.get("status")
        if not isinstance(status, str):
            return "unknown"
        statuses.append(status)
    if not statuses:
        return "unknown"
    has_current = any(status in {"Current", "Proposed"} for status in statuses)
    has_history = any(status in {"Superseded", "Historical"} for status in statuses)
    if has_current and has_history:
        return "mixed"
    if has_history and not has_current:
        return "historical"
    if has_current and not has_history:
        return "current"
    return "unknown"
```

- [ ] **Step 2: Split Gate computation by membership**

Use this exact policy:

```text
historical -> append gid to historical_gates; do not append to stale/needs_review/blocking; do not add route solely from historical verdict
mixed/unknown -> append gid to needs_review_gates; add Authority/P21 route
current -> keep existing evidence/effective validity and BLOCKED_* routing logic
```

For mixed/unknown, add finding text that explicitly says Authority review is required.

- [ ] **Step 3: Return `historical_gates` in deterministic state**

Add:

```python
"historical_gates": sorted(historical_gates),
```

Historical-only `BLOCKED_*` verdicts must not enter `blocking_gates`.

- [ ] **Step 4: Run focused Gate tests**

Run:

```bash
python3 -m unittest \
  tests.project_state.test_history_v03.HistoryV03Tests.test_historical_gate_is_non_actionable \
  tests.project_state.test_history_v03.HistoryV03Tests.test_current_stale_gate_remains_actionable \
  tests.project_state.test_history_v03.HistoryV03Tests.test_mixed_authority_gate_routes_p21 -v
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

**Interfaces:**
- Produces generated `integration_applicability` ordered by `integration_id`.
- Keeps authored statuses `awaiting_integration | integrated | closed_unmerged` unchanged.

- [ ] **Step 1: Change strict validator semantics for `integrated`**

For `integrated`, require all of:

```python
if not gate or gate.get("verdict") not in PASS_VERDICTS:
    errors.append(f"integration {iid}: requires historical PASS/PASS_WITH_FINDINGS gate {gate_id}")
if not isinstance(revision, str) or not revision:
    errors.append(f"integration {iid}: integrated_revision is required when status=integrated")
for eid in evidence_ids:
    ev = evidence_by_id.get(eid)
    if ev and ev.get("status") != "available":
        errors.append(f"integration {iid}: uses unavailable evidence {eid}")
```

Do not require `gate.validity == current` or effective-current Gate for completed `integrated` occurrence.

- [ ] **Step 2: Preserve current fail-closed validation for `awaiting_integration`**

For `awaiting_integration`, retain PASS verdict, declared `current`, effective-current Gate, and available evidence requirements. Restrict the post-compute `noncurrent_gate_ids` rejection loop to `status == "awaiting_integration"`.

- [ ] **Step 3: Generate Integration applicability**

For each integration, use its Gate membership and effective validity:

```python
if status in {"integrated", "closed_unmerged"} and membership == "historical":
    applicability = "historical"
elif membership in {"mixed", "unknown"}:
    applicability = "needs_review"
elif gate_effective.get(gate_id) == "stale":
    applicability = "stale"
elif gate_effective.get(gate_id) == "needs_review":
    applicability = "needs_review"
else:
    applicability = "current"
```

Append `{"integration_id": iid, "applicability": applicability}` and sort the final list by `integration_id`.

- [ ] **Step 4: Preserve integration handoff semantics**

Only `awaiting_integration` under a current-effective PASS/PASS_WITH_FINDINGS Gate may enter `awaiting_integrations[]` and create `superpowers:finishing-a-development-branch` handoff. `integrated` and `closed_unmerged` never create that handoff.

- [ ] **Step 5: Run all focused history tests**

```bash
python3 -m unittest tests.project_state.test_history_v03 -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tools/aegis_state/model.py tools/aegis_state/compute.py tests/project_state/test_history_v03.py
git commit -m "feat: preserve historical integration occurrence"
```

---

### Task 4: Advance the executable contract to schema/generator 0.3

**Files:**
- Modify: `tools/aegis_state/__init__.py`
- Modify: `tools/aegis_state/model.py`
- Modify: `tools/aegis_state/compute.py`
- Modify: `tests/project_state/helpers.py`
- Modify: `tests/project_state/test_gate_blockers_v02.py`
- Modify: `tests/project_state/test_integrations_v02.py`
- Modify: `tests/project_state/test_v02_model.py`

**Interfaces:**
- `GENERATOR_VERSION == "0.3"`.
- `SCHEMA_VERSION == "0.3"`.
- `compute_state()` returns `schema_version == "0.3"`.

- [ ] **Step 1: Advance runtime constants**

Set:

```python
# tools/aegis_state/__init__.py
GENERATOR_VERSION = "0.3"

# tools/aegis_state/model.py
SCHEMA_VERSION = "0.3"
```

Set generated `state["schema_version"]` to `"0.3"`.

- [ ] **Step 2: Migrate existing project-state test fixtures from schema 0.2 to 0.3**

Change fixture version strings and names needed for the new executable contract. Keep all prior behavioral assertions unchanged. Existing tests continue to prove duplicate IDs, dangling refs, Gate blocker routing, digest behavior, current-awaiting integration, and evidence requirements.

- [ ] **Step 3: Run the complete project-state suite**

```bash
python3 -m unittest discover -s tests/project_state -v
```

Expected: all existing and new tests PASS.

- [ ] **Step 4: Commit**

```bash
git add tools/aegis_state tests/project_state
git commit -m "refactor: advance project state runtime to v0.3"
```

---

### Task 5: Publish v0.3 schemas and migrate the minimal executable example

**Files:**
- Create: `schemas/project-state/v0.3/project.schema.json`
- Create: `schemas/project-state/v0.3/authorities.schema.json`
- Create: `schemas/project-state/v0.3/gates.schema.json`
- Create: `schemas/project-state/v0.3/evidence.schema.json`
- Create: `schemas/project-state/v0.3/integrations.schema.json`
- Create: `schemas/project-state/v0.3/state.schema.json`
- Modify: `examples/project-state/minimal/.aegis/project.json`
- Modify: `examples/project-state/minimal/.aegis/authorities.json`
- Modify: `examples/project-state/minimal/.aegis/gates.json`
- Modify: `examples/project-state/minimal/.aegis/evidence.json`
- Modify: `examples/project-state/minimal/.aegis/integrations.json`
- Regenerate: `examples/project-state/minimal/.aegis/state.json`

**Interfaces:**
- v0.1/v0.2 schema directories remain untouched.
- v0.3 state schema includes `historical_gates[]` and `integration_applicability[]`.

- [ ] **Step 1: Create v0.3 schema tree by copying the six v0.2 schemas**

Update each `$id`, title, and `schema_version` constant to 0.3. Do not add authored applicability/actionability fields to `integrations.schema.json`.

- [ ] **Step 2: Extend only the v0.3 state schema**

Add:

```json
"historical_gates": {"type":"array","items":{"type":"string"},"uniqueItems":true},
"integration_applicability": {
  "type":"array",
  "items": {
    "type":"object",
    "additionalProperties":false,
    "required":["integration_id","applicability"],
    "properties": {
      "integration_id":{"type":"string","minLength":1},
      "applicability":{"enum":["current","needs_review","stale","historical"]}
    }
  }
}
```

Require both fields in the state schema.

- [ ] **Step 3: Migrate minimal authored manifests to schema 0.3**

Change authored manifest version strings to 0.3. Keep occurrence/actionability fields authored exactly as defined by the v0.3 schemas.

- [ ] **Step 4: Regenerate and verify minimal state**

```bash
python3 -m tools.aegis_state.cli recompute examples/project-state/minimal --write
python3 -m tools.aegis_state.cli validate examples/project-state/minimal
python3 -m tools.aegis_state.cli check examples/project-state/minimal
```

Expected output includes `STATE_WRITTEN`, `VALID`, and `STATE_OK`.

- [ ] **Step 5: Parse all v0.3 schemas using stdlib JSON**

```bash
python3 -c 'import glob,json; [json.load(open(p)) for p in glob.glob("schemas/project-state/v0.3/*.json")]; print("SCHEMA_PARSE_OK")'
```

Expected: `SCHEMA_PARSE_OK`.

- [ ] **Step 6: Commit**

```bash
git add schemas/project-state/v0.3 examples/project-state/minimal
git commit -m "feat: publish project state schema v0.3"
```

---

### Task 6: Update Aegis Skill and repository CI

**Files:**
- Modify: `skills/aegis/references/project-state.md`
- Modify: `skills/aegis/SKILL.md`
- Modify: `.github/workflows/project-state.yml`

**Interfaces:**
- Skill keeps `SKILL.md` as thin control plane and detailed project-state rules in `references/project-state.md`.
- CI validates v0.3 schemas, minimal example, and full project-state tests.

- [ ] **Step 1: Update `references/project-state.md` to v0.3 semantics**

Document exactly:

```text
Historical Occurrence != Current Applicability != Current Actionability
all historical Authority -> historical/non-actionable
mixed Current + Historical Authority -> needs_review + Authority/P21
current stale Gate -> actionable verification/P34
historical BLOCKED verdict -> audit history only, never integration proof or current blocker
```

Preserve v0.2 blocked-Gate propagation rules for current Gates.

- [ ] **Step 2: Update only the thin bootstrap wording in `SKILL.md`**

Change the version reference from v0.2 to v0.3 and mention historical/applicability bootstrap behavior. Do not duplicate the full algorithm.

- [ ] **Step 3: Update `.github/workflows/project-state.yml`**

The workflow must parse `schemas/project-state/v0.3/*.json`, validate/check the minimal v0.3 example, and run:

```bash
python3 -m unittest discover -s tests/project_state -v
```

Keep existing trigger paths for project-state Authority/spec changes.

- [ ] **Step 4: Run full local regression**

```bash
python3 -m unittest discover -s tests/project_state -v
python3 -m tools.aegis_state.cli validate examples/project-state/minimal
python3 -m tools.aegis_state.cli check examples/project-state/minimal
```

Expected: unit suite PASS, `VALID`, `STATE_OK`.

- [ ] **Step 5: Validate and package the complete Aegis Skill**

Run the installed Skill Creator validator/package workflow against `skills/aegis`. Expected validator output contains `Skill is valid!`; archive integrity check must report no ZIP errors.

- [ ] **Step 6: Commit**

```bash
git add skills/aegis .github/workflows/project-state.yml
git commit -m "docs: teach Aegis project state v0.3 history semantics"
```

---

### Task 7: Execute R03-09 real Aegis self-host oracle

**Evidence source:** current PR #5 root `.aegis/` manifests plus current GitHub repository facts.

**Interfaces:**
- Consumes v0.3 tooling.
- Produces mandatory acceptance evidence before P34.

- [ ] **Step 1: Build truthful v0.3 self-host input**

Preserve all of these facts:

```text
PR #4 integrated @ 555bac21d485fc4530680c61719fc36831021b0d
07 v0.1 = Superseded
PR #7 integrated @ 8ca7b49d40a17e8cb7ffba86632da3aeae5e911c
07 v0.2 = Current until v0.3 supersession
OpenAI real baseline = BLOCKED_ENVIRONMENT
```

- [ ] **Step 2: Recompute and strictly validate/check**

Required generated assertions:

```text
int-pr4 applicability = historical
int-pr7 applicability = current
gate-project-state-pr4 in historical_gates
gate-project-state-pr4 not in stale_gates
blocking_gates = [gate-openai-real-baseline]
earliest_untrusted_layer = verification
recommended_next_stage = P34
strict check = STATE_OK
```

- [ ] **Step 3: Prove production code has no repository-specific repair**

Search changed production files for `pr4`, `555bac21d485fc4530680c61719fc36831021b0d`, and `Mostorm-Labs/aegis`. Expected: zero matches outside docs/tests/evidence fixtures.

- [ ] **Step 4: Record exact self-host output in the feature PR and Notion v0.3 evidence section**

Label it as R03-09 acceptance evidence, distinct from generic unit regression.

---

### Task 8: P34, P23 supersession, repository integration, and formal 08 rerun

**Files:**
- Review all v0.3 changed files.
- Update Authority status only after P34 evidence passes.

**Interfaces:**
- P34 consumes focused regressions, full regression, schemas, minimal E2E, Skill package, R03-09, and fresh repository CI.

- [ ] **Step 1: Open PR from `aegis/project-state-manifest-v0.3` to current `main`**

PR body must identify F08-03 and list R03-01 through R03-09 evidence requirements. v0.2 remains Current while the PR is under review.

- [ ] **Step 2: Require fresh CI on the final PR head**

Inspect workflow job steps/logs. Do not use an old-head green run as final evidence.

- [ ] **Step 3: Execute P34**

Accept only when:

```text
focused v0.3 regressions          PASS
full project-state regression     PASS
v0.3 schema/minimal contract      PASS
Aegis Skill validation/package    PASS
R03-09 real self-host             STATE_OK
historical PR #4 truth            preserved
OpenAI blocker route              verification/P34
fresh repository CI               PASS
```

- [ ] **Step 4: Execute P23 only after P34 acceptance**

Set:

```text
07 v0.2 -> Superseded/Historical
07 v0.3 -> Current Replacement Authority
```

Update Notion and repository companion docs with explicit supersession reason and accepted evidence.

- [ ] **Step 5: Merge the accepted v0.3 PR, record the actual merge revision, then formally rerun 08**

Formal 08 rerun must use current repository facts. F08-03 closes only if truthful root project state remains `STATE_OK` after v0.3 integration; otherwise classify the new earliest defect instead of forcing 08 PASS.
